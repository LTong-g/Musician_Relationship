from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from qqmusic_api import Client

from music_metadata_graph.pipelines.import_singer_list_to_db import import_artists
from music_metadata_graph.pipelines.song_csv import escape_excel_formula_row


QUICK_SEARCH_RATE = 0.5
QUICK_SEARCH_CAPACITY = 1
MID_FILL_CSV_FIELDS = [
    "source_step",
    "source_role",
    "source_name",
    "search_name",
    "match_mode",
    "status",
    "matched_mid",
    "matched_name",
    "matched_pic",
    "exact_match_count",
    "candidate_count",
    "raw_json_path",
    "source_song_mid",
    "source_song_id",
    "source_song_name",
    "source_raw_json_path",
    "source_raw_page",
    "source_raw_row_index",
]


@dataclass(frozen=True)
class MissingArtistName:
    source_step: str
    source_role: str
    source_name: str
    source_song_mid: str
    source_song_id: str
    source_song_name: str
    source_raw_json_path: str
    source_raw_page: int
    source_raw_row_index: int


def quick_search_path(raw_dir: Path, artist_name: str) -> Path:
    invalid_chars = '<>:"/\\|?*'
    safe_name = "".join("_" if char in invalid_chars or ord(char) < 32 else char for char in artist_name)
    safe_name = safe_name.strip().rstrip(". ")
    if not safe_name:
        safe_name = "_"
    return raw_dir / f"{safe_name}.json"


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


async def execute_or_load_quick_search(
    client: Client,
    raw_dir: Path,
    artist_name: str,
    *,
    force: bool,
) -> tuple[dict[str, Any], str, Path]:
    path = quick_search_path(raw_dir, artist_name)
    if path.exists() and not force:
        return load_json(path), "cache_hit", path
    payload = await client.search.quick_search(artist_name)
    dump_json(path, payload)
    return payload, "fetched", path


def singer_candidates(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    singer_group = payload.get("singer")
    if not isinstance(singer_group, dict):
        return []
    itemlist = singer_group.get("itemlist")
    if not isinstance(itemlist, list):
        return []
    return [item for item in itemlist if isinstance(item, dict)]


def resolve_exact_artist(artist_name: str, payload: Any) -> tuple[dict[str, Any] | None, int, int]:
    candidates = singer_candidates(payload)
    exact = [
        item
        for item in candidates
        if str(item.get("name") or "").strip() == artist_name
        and str(item.get("mid") or "").strip()
    ]
    if len(exact) != 1:
        return None, len(exact), len(candidates)
    return exact[0], len(exact), len(candidates)


def search_status(match: dict[str, Any] | None, exact_match_count: int, candidate_count: int) -> str:
    if match is not None:
        return "matched"
    if exact_match_count > 1:
        return "ambiguous_exact_match"
    if candidate_count == 0:
        return "no_singer_candidates"
    return "not_matched"


def split_artist_names(artist_name: str) -> tuple[str, ...]:
    if "/" not in artist_name:
        return ()
    names: list[str] = []
    seen: set[str] = set()
    for part in artist_name.split("/"):
        name = part.strip()
        if not name or name in seen:
            continue
        seen.add(name)
        names.append(name)
    return tuple(names)


def build_artist_row(match: dict[str, Any], raw_path: Path) -> dict[str, Any]:
    return {
        "mid": str(match.get("mid") or "").strip(),
        "name": str(match.get("name") or "").strip(),
        "area_id": None,
        "other_name": "",
        "icon": str(match.get("pic") or "").strip(),
        "spell": "",
        "raw_json_path": raw_path.as_posix(),
        "raw_page": 0,
        "raw_row_index": 1,
    }


def load_artist_rows_by_name(connection: Any) -> dict[str, list[dict[str, Any]]]:
    rows = connection.execute(
        """
        SELECT mid, name, icon, raw_json_path, raw_page, raw_row_index
        FROM artists
        WHERE name <> ''
        ORDER BY rowid
        """
    ).fetchall()
    rows_by_name: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        item = dict(row)
        name = str(item.get("name") or "").strip()
        mid = str(item.get("mid") or "").strip()
        if name and mid:
            rows_by_name.setdefault(name, []).append(item)
    return rows_by_name


def resolve_db_artist(artist_name: str, rows_by_name: dict[str, list[dict[str, Any]]]) -> tuple[dict[str, Any] | None, int]:
    rows = rows_by_name.get(artist_name, [])
    mids = {str(row.get("mid") or "").strip() for row in rows if str(row.get("mid") or "").strip()}
    if len(mids) != 1:
        return None, len(mids)
    row = rows[0]
    return {
        "mid": str(row.get("mid") or "").strip(),
        "name": str(row.get("name") or "").strip(),
        "pic": str(row.get("icon") or "").strip(),
        "raw_json_path": str(row.get("raw_json_path") or "").strip(),
    }, len(mids)


def remember_artist_match(rows_by_name: dict[str, list[dict[str, Any]]], match: dict[str, Any], raw_path: Path) -> None:
    name = str(match.get("name") or "").strip()
    mid = str(match.get("mid") or "").strip()
    if not name or not mid:
        return
    rows_by_name.setdefault(name, []).append(
        {
            "mid": mid,
            "name": name,
            "icon": str(match.get("pic") or "").strip(),
            "raw_json_path": raw_path.as_posix(),
            "raw_page": 0,
            "raw_row_index": 1,
        }
    )


def match_raw_path(match: dict[str, Any] | None, fallback: Path) -> str:
    raw_json_path = str((match or {}).get("raw_json_path") or "").strip()
    return raw_json_path or fallback.as_posix()


def build_csv_row(
    source: MissingArtistName,
    *,
    search_name: str | None = None,
    match_mode: str = "direct",
    status: str,
    raw_path: Path | str,
    match: dict[str, Any] | None,
    exact_match_count: int,
    candidate_count: int,
) -> dict[str, Any]:
    return {
        "source_step": source.source_step,
        "source_role": source.source_role,
        "source_name": source.source_name,
        "search_name": search_name or source.source_name,
        "match_mode": match_mode,
        "status": status,
        "matched_mid": str((match or {}).get("mid") or ""),
        "matched_name": str((match or {}).get("name") or ""),
        "matched_pic": str((match or {}).get("pic") or ""),
        "exact_match_count": exact_match_count,
        "candidate_count": candidate_count,
        "raw_json_path": raw_path.as_posix() if isinstance(raw_path, Path) else raw_path,
        "source_song_mid": source.source_song_mid,
        "source_song_id": source.source_song_id,
        "source_song_name": source.source_song_name,
        "source_raw_json_path": source.source_raw_json_path,
        "source_raw_page": source.source_raw_page,
        "source_raw_row_index": source.source_raw_row_index,
    }


def write_mid_fill_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=MID_FILL_CSV_FIELDS, extrasaction="ignore", lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(escape_excel_formula_row(row) for row in rows)


async def fill_missing_artist_mids(
    connection: Any,
    sources: list[MissingArtistName],
    *,
    raw_dir: Path,
    csv_path: Path,
    force: bool,
) -> dict[str, Any]:
    unique_sources: dict[str, MissingArtistName] = {}
    for source in sources:
        name = source.source_name.strip()
        if name and name not in unique_sources:
            unique_sources[name] = source

    client = Client(rate=QUICK_SEARCH_RATE, capacity=QUICK_SEARCH_CAPACITY)
    csv_rows: list[dict[str, Any]] = []
    fetched = 0
    cache_hits = 0
    failed = 0
    imported = 0
    db_matches = 0

    db_artist_rows_by_name = load_artist_rows_by_name(connection)
    try:
        async def process_search_name(source: MissingArtistName, index: int, search_name: str, match_mode: str) -> None:
            nonlocal fetched, cache_hits, failed, imported, db_matches

            db_match, db_match_count = resolve_db_artist(search_name, db_artist_rows_by_name)
            if db_match is not None:
                db_matches += 1
                csv_rows.append(
                    build_csv_row(
                        source,
                        search_name=search_name,
                        match_mode=match_mode,
                        status="db_matched",
                        raw_path=match_raw_path(db_match, quick_search_path(raw_dir, search_name)),
                        match=db_match,
                        exact_match_count=1,
                        candidate_count=1,
                    )
                )
                write_mid_fill_csv(csv_path, csv_rows)
                suffix = "" if match_mode == "direct" else f" split={search_name}"
                print(f"[{index}/{len(unique_sources)}] name={source.source_name}{suffix} status=db_matched")
                return

            if db_match_count > 1:
                csv_rows.append(
                    build_csv_row(
                        source,
                        search_name=search_name,
                        match_mode=match_mode,
                        status="db_ambiguous_name",
                        raw_path=quick_search_path(raw_dir, search_name),
                        match=None,
                        exact_match_count=db_match_count,
                        candidate_count=db_match_count,
                    )
                )
                write_mid_fill_csv(csv_path, csv_rows)
                suffix = "" if match_mode == "direct" else f" split={search_name}"
                print(f"[{index}/{len(unique_sources)}] name={source.source_name}{suffix} status=db_ambiguous_name")
                return

            try:
                payload, cache_status, raw_path = await execute_or_load_quick_search(
                    client,
                    raw_dir,
                    search_name,
                    force=force,
                )
            except Exception as exc:
                failed += 1
                raw_path = quick_search_path(raw_dir, search_name)
                csv_rows.append(
                    build_csv_row(
                        source,
                        search_name=search_name,
                        match_mode=match_mode,
                        status=f"failed:{type(exc).__name__}",
                        raw_path=raw_path,
                        match=None,
                        exact_match_count=0,
                        candidate_count=0,
                    )
                )
                write_mid_fill_csv(csv_path, csv_rows)
                suffix = "" if match_mode == "direct" else f" split={search_name}"
                print(f"[{index}/{len(unique_sources)}] name={source.source_name}{suffix} status=failed reason={type(exc).__name__}: {exc}")
                return

            fetched += int(cache_status == "fetched")
            cache_hits += int(cache_status == "cache_hit")
            match, exact_match_count, candidate_count = resolve_exact_artist(search_name, payload)
            status = search_status(match, exact_match_count, candidate_count)
            csv_rows.append(
                build_csv_row(
                    source,
                    search_name=search_name,
                    match_mode=match_mode,
                    status=status,
                    raw_path=raw_path,
                    match=match,
                    exact_match_count=exact_match_count,
                    candidate_count=candidate_count,
                )
            )
            if match is not None:
                imported += import_artists(connection, [build_artist_row(match, raw_path)])
                remember_artist_match(db_artist_rows_by_name, match, raw_path)
            write_mid_fill_csv(csv_path, csv_rows)
            suffix = "" if match_mode == "direct" else f" split={search_name}"
            print(f"[{index}/{len(unique_sources)}] name={source.source_name}{suffix} status={status} raw={raw_path.as_posix()}")

        for index, source in enumerate(unique_sources.values(), 1):
            split_names = split_artist_names(source.source_name)
            if "/" in source.source_name:
                if not split_names:
                    csv_rows.append(
                        build_csv_row(
                            source,
                            search_name="",
                            match_mode="split",
                            status="empty_split_names",
                            raw_path=quick_search_path(raw_dir, source.source_name),
                            match=None,
                            exact_match_count=0,
                            candidate_count=0,
                        )
                    )
                    write_mid_fill_csv(csv_path, csv_rows)
                    print(f"[{index}/{len(unique_sources)}] name={source.source_name} status=empty_split_names")
                    continue
                for split_name in split_names:
                    await process_search_name(source, index, split_name, "split")
                continue

            await process_search_name(source, index, source.source_name, "direct")
    finally:
        await client.close()

    write_mid_fill_csv(csv_path, csv_rows)
    return {
        "source_rows": len(sources),
        "unique_names": len(unique_sources),
        "matched_names": sum(1 for row in csv_rows if str(row.get("status") or "") in {"matched", "db_matched"}),
        "imported_artists": imported,
        "db_matches": db_matches,
        "fetched": fetched,
        "cache_hits": cache_hits,
        "failed_searches": failed,
        "csv": csv_path.as_posix(),
        "raw_dir": raw_dir.as_posix(),
    }
