from __future__ import annotations

import argparse
import asyncio
import csv
import json
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass
from dataclasses import replace as dataclass_replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pypinyin import Style, lazy_pinyin
from qqmusic_api import Client


DEFAULT_RAW_DIR = Path("data/raw/qqmusic")
DEFAULT_OUTPUT_DIR = Path("data/processed/high_confidence_singer_songs")
DEFAULT_CSV_OUTPUT_DIR = Path("data/processed/validation/csv_views/high_confidence_singer_songs")
DEFAULT_REGISTRY_PATH = Path("data/processed/singer_registry/qqmusic_hot/singer_registry.json")
DEFAULT_PAGE_SIZE = 30
REQUEST_RATE = 0.5
REQUEST_CAPACITY = 1
ALLOWED_ALBUM_TYPES = ("Single", "EP", "录音室专辑")
DEDUPED_NAME_ALBUM_TYPE_PRIORITY = {
    "录音室专辑": 0,
    "EP": 1,
    "Single": 2,
}
TEST_SINGERS = (
    ("zhoujielun", "周杰伦", "0025NhlN2yWrP4"),
    ("xuezhiqian", "薛之谦", "002J4UUk29y8BY"),
    ("linjunjie", "林俊杰", "001BLpXF2DyJe2"),
    ("wangsulong", "汪苏泷", "001z2JmX09LLgL"),
)


@dataclass(frozen=True)
class SingerTarget:
    slug: str
    name: str
    mid: str


@dataclass(frozen=True)
class CollectConfig:
    raw_dir: Path
    output_dir: Path
    csv_output_dir: Path
    page_size: int
    singers: tuple[SingerTarget, ...]
    singer_source: str
    write_csv: bool


def ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def is_relative_to_path(path: Path, base: Path) -> bool:
    try:
        path.resolve().relative_to(base.resolve())
    except ValueError:
        return False
    return True


def validate_config(config: CollectConfig) -> None:
    if config.write_csv and is_relative_to_path(config.csv_output_dir, config.output_dir):
        raise ValueError(
            "--csv-output-dir must not be inside --output-dir; "
            "CSV files are validation views and must stay outside the formal JSON output directory."
        )


def normalize_text(value: str) -> str:
    return unicodedata.normalize("NFKC", value or "").casefold().strip()


def sort_key(value: str) -> str:
    return " ".join(lazy_pinyin(normalize_text(value), style=Style.NORMAL, errors="default"))


def parse_singer(value: str) -> SingerTarget:
    parts = value.split("=", 2)
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("Singer must use slug=name=mid format.")
    slug, name, mid = (part.strip() for part in parts)
    if not slug or not name or not mid:
        raise argparse.ArgumentTypeError("Singer slug, name, and mid cannot be empty.")
    return SingerTarget(slug=slug, name=name, mid=mid)


def safe_slug(name: str, mid: str) -> str:
    pinyin = "-".join(lazy_pinyin(normalize_text(name), style=Style.NORMAL, errors="ignore"))
    slug = re.sub(r"[^a-z0-9]+", "-", pinyin.casefold()).strip("-")
    slug = slug or re.sub(r"[^a-z0-9]+", "-", mid.casefold()).strip("-")
    suffix = mid[:8].casefold() if mid else "unknown"
    return f"{slug}-{suffix}" if suffix and suffix not in slug else slug


def singer_from_registry_row(row: dict[str, Any]) -> SingerTarget | None:
    mid = str(row.get("mid") or "").strip()
    name = str(row.get("name") or row.get("title") or "").strip()
    if not mid or not name:
        return None
    return SingerTarget(slug=safe_slug(name, mid), name=name, mid=mid)


def load_registry_singers(path: Path, max_singers: int | None = None) -> tuple[SingerTarget, ...]:
    payload = load_json(path)
    rows = payload.get("singers") if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError(f"Registry does not contain a singer list: {path}")
    singers: list[SingerTarget] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        target = singer_from_registry_row(row)
        if target is None or target.mid in seen:
            continue
        seen.add(target.mid)
        singers.append(target)
        if max_singers is not None and len(singers) >= max_singers:
            break
    if not singers:
        raise ValueError(f"Registry contains no usable singers: {path}")
    return tuple(singers)


async def execute_or_load(client: Client, cache_path: Path, request: Any) -> Any:
    if cache_path.exists():
        return load_json(cache_path)
    result = await client.execute(request)
    payload = result.model_dump(mode="json") if hasattr(result, "model_dump") else result
    dump_json(cache_path, payload)
    return payload


def raw_album_id(album: dict[str, Any]) -> int | str | None:
    return album.get("albumID") or album.get("albumId") or album.get("id")


def raw_album_mid(album: dict[str, Any]) -> str:
    return str(album.get("albumMid") or album.get("mid") or "")


def compact_album(album: dict[str, Any], target: SingerTarget, page: int, row: int) -> dict[str, Any]:
    row_data = dict(album)
    name = str(row_data.get("albumName") or row_data.get("name") or row_data.get("title") or "")
    album_type = str(row_data.get("albumType") or row_data.get("album_type") or "")
    row_data.update(
        {
            "aux_target_singer": target.name,
            "aux_target_singer_mid": target.mid,
            "aux_page": page,
            "aux_row": row,
            "aux_sort_key": sort_key(name),
            "aux_include_album": album_type in ALLOWED_ALBUM_TYPES,
            "aux_album_filter_reason": "" if album_type in ALLOWED_ALBUM_TYPES else f"excluded_album_type:{album_type or 'missing'}",
            "aux_source": "qqmusic.singer.get_album_list",
        }
    )
    return row_data


async def collect_singer_albums(client: Client, target: SingerTarget, config: CollectConfig) -> tuple[list[dict[str, Any]], int | None]:
    albums: list[dict[str, Any]] = []
    total: int | None = None
    page = 1
    cache_dir = config.raw_dir / "high_confidence_singer_songs" / target.slug / "singer_album_list"
    while True:
        cache_path = cache_dir / f"page_{page:04d}_size_{config.page_size}.json"
        request = dataclass_replace(
            client.singer.get_album_list(target.mid, num=config.page_size, page=page),
            response_model=None,
        )
        payload = await execute_or_load(client, cache_path, request)
        page_albums = payload.get("albumList") or []
        if total is None and payload.get("total") is not None:
            total = int(payload["total"])
        for index, album in enumerate(page_albums, 1):
            albums.append(compact_album(album, target, page, index))
        print(f"{target.name} albums page={page} count={len(page_albums)} total={total}")
        if not page_albums:
            break
        if total is not None and len(albums) >= total:
            break
        if len(page_albums) < config.page_size:
            break
        page += 1
    return albums, total


def song_singers(song: dict[str, Any]) -> list[dict[str, Any]]:
    return list(song.get("singer") or [])


def target_in_song(song: dict[str, Any], target: SingerTarget) -> bool:
    for singer in song_singers(song):
        if str(singer.get("mid") or "") == target.mid:
            return True
    return False


def song_key(song: dict[str, Any]) -> str:
    mid = song.get("mid")
    if mid:
        return f"mid:{mid}"
    song_id = song.get("id")
    if song_id is not None:
        return f"id:{song_id}"
    return ""


def song_name_key(song: dict[str, Any]) -> str:
    return normalize_text(str(song.get("name") or ""))


def compact_song(song: dict[str, Any], album: dict[str, Any], target: SingerTarget) -> dict[str, Any]:
    row_data = dict(song)
    name = str(song.get("name") or song.get("title") or "")
    row_data.update(
        {
            "aux_target_singer": target.name,
            "aux_target_singer_mid": target.mid,
            "aux_sort_key": sort_key(name),
            "aux_source_albumMid": raw_album_mid(album),
            "aux_source_albumName": album.get("albumName") or album.get("name") or album.get("title") or "",
            "aux_source_albumType": album.get("albumType") or album.get("album_type") or "",
            "aux_source_album_publishDate": album.get("publishDate") or album.get("time_public") or "",
            "aux_source_album_singerName": album.get("singerName") or album.get("singer_name") or "",
            "aux_target_singer_match": target_in_song(song, target),
            "aux_source": "qqmusic.album.get_song",
        }
    )
    return row_data


async def collect_album_songs(
    client: Client,
    target: SingerTarget,
    album: dict[str, Any],
    config: CollectConfig,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], int | None]:
    album_mid = raw_album_mid(album)
    if not album_mid:
        return [], [], [], None
    all_rows: list[dict[str, Any]] = []
    kept: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    total: int | None = None
    page = 1
    cache_dir = config.raw_dir / "high_confidence_singer_songs" / target.slug / "album_songs" / album_mid
    while True:
        cache_path = cache_dir / f"page_{page:04d}_size_{config.page_size}.json"
        request = dataclass_replace(
            client.album.get_song(album_mid, num=config.page_size, page=page),
            response_model=None,
        )
        payload = await execute_or_load(client, cache_path, request)
        page_songs = [
            (item or {}).get("songInfo") or item
            for item in (payload.get("songList") or [])
        ]
        if total is None and payload.get("totalNum") is not None:
            total = int(payload["totalNum"])
        for song in page_songs:
            compacted = compact_song(song, album, target)
            compacted["aux_filter_step"] = "high_confidence_album_song_filter_1_target_singer_match"
            all_rows.append(dict(compacted))
            if compacted["aux_target_singer_match"]:
                compacted["aux_filter_result"] = "kept"
                compacted["aux_filter_reason"] = ""
                kept.append(compacted)
            else:
                compacted["aux_filter_result"] = "removed"
                compacted["aux_filter_reason"] = "target_singer_not_in_song_singers"
                rejected.append(compacted)
        print(f"{target.name} album={album.get('albumName')} page={page} songs={len(page_songs)} total={total}")
        if not page_songs:
            break
        if total is not None and len(kept) + len(rejected) >= total:
            break
        if len(page_songs) < config.page_size:
            break
        page += 1
    return all_rows, kept, rejected, total


def album_type_priority(row: dict[str, Any]) -> int:
    return DEDUPED_NAME_ALBUM_TYPE_PRIORITY.get(str(row.get("aux_source_albumType") or ""), 3)


def numeric_song_id(row: dict[str, Any]) -> int:
    try:
        return int(row.get("id") or 0)
    except (TypeError, ValueError):
        return 0


def dedupe_by_song_key(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    deduped: dict[str, dict[str, Any]] = {}
    duplicate_rows: list[dict[str, Any]] = []
    for row in rows:
        key = song_key(row)
        if not key:
            duplicate = dict(row)
            duplicate["aux_filter_step"] = "high_confidence_album_song_filter_2_dedupe"
            duplicate["aux_filter_result"] = "removed"
            duplicate["aux_filter_reason"] = "missing_song_mid_and_id"
            duplicate_rows.append(duplicate)
            continue
        existing = deduped.get(key)
        if existing is None:
            row["aux_source_albums"] = [
                {
                    "albumMid": row.get("aux_source_albumMid"),
                    "albumName": row.get("aux_source_albumName"),
                    "albumType": row.get("aux_source_albumType"),
                }
            ]
            deduped[key] = row
            continue
        source_album = {
            "albumMid": row.get("aux_source_albumMid"),
            "albumName": row.get("aux_source_albumName"),
            "albumType": row.get("aux_source_albumType"),
        }
        existing.setdefault("aux_source_albums", []).append(source_album)
        duplicate = dict(row)
        duplicate["aux_filter_step"] = "high_confidence_album_song_filter_2_dedupe"
        duplicate["aux_filter_result"] = "removed"
        duplicate["aux_filter_reason"] = "duplicate_song_key_in_songs_after_filter1_target_singer_match"
        duplicate["aux_source_albums"] = existing.get("aux_source_albums", [])
        duplicate_rows.append(duplicate)
    return list(deduped.values()), duplicate_rows


def dedupe_by_song_name(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    groups: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    for index, row in enumerate(rows):
        key = song_name_key(row)
        row["aux_filter2_name_key"] = key
        groups.setdefault(key, []).append((index, row))

    kept: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    for key, indexed_group in groups.items():
        if len(indexed_group) == 1:
            kept.append(indexed_group[0][1])
            continue
        _, selected = min(indexed_group, key=lambda item: (album_type_priority(item[1]), numeric_song_id(item[1]), item[0]))
        selected_key = song_key(selected)
        selected["aux_filter2_name_group_size"] = len(indexed_group)
        selected["aux_filter2_name_preferred_albumType"] = selected.get("aux_source_albumType") or ""
        selected["aux_filter2_name_preferred_song_id"] = numeric_song_id(selected)
        kept.append(selected)
        for _, row in indexed_group:
            if row is selected:
                continue
            duplicate = dict(row)
            duplicate["aux_filter_step"] = "high_confidence_album_song_filter_2_dedupe"
            duplicate["aux_filter_result"] = "removed"
            duplicate["aux_filter_reason"] = "duplicate_song_name_prefer_recording_album_then_ep_then_single_then_lowest_id"
            duplicate["aux_filter2_name_key"] = key
            duplicate["aux_filter2_name_group_size"] = len(indexed_group)
            duplicate["aux_filter2_selected_song_key"] = selected_key
            duplicate["aux_filter2_selected_albumType"] = selected.get("aux_source_albumType") or ""
            duplicate["aux_filter2_selected_song_id"] = numeric_song_id(selected)
            removed.append(duplicate)
    return kept, removed


def dedupe_songs(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    key_deduped, key_duplicates = dedupe_by_song_key(rows)
    name_deduped, name_duplicates = dedupe_by_song_name(key_deduped)
    return name_deduped, key_duplicates + name_duplicates


def cleanup_song_output_files(output_dir: Path) -> None:
    keep = {
        "albums_all.json",
        "albums_all.csv",
        "songs_after_filter1_target_singer_match.json",
        "songs_after_filter1_target_singer_match.csv",
        "songs_removed_by_filter1_target_singer_match.json",
        "songs_removed_by_filter1_target_singer_match.csv",
        "songs_after_filter2_dedupe.json",
        "songs_after_filter2_dedupe.csv",
        "songs_removed_by_filter2_dedupe.json",
        "songs_removed_by_filter2_dedupe.csv",
        "songs_all.json",
        "songs_all.csv",
        "albums_included.json",
        "albums_included.csv",
        "albums_excluded.json",
        "albums_excluded.csv",
        "summary.json",
    }
    if not output_dir.exists():
        return
    for file in output_dir.iterdir():
        if file.is_file() and file.name not in keep:
            file.unlink(missing_ok=True)


def sorted_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            str(row.get("aux_target_singer") or ""),
            str(row.get("aux_sort_key") or ""),
            str(row.get("time_public") or row.get("aux_source_album_publishDate") or ""),
            str(row.get("mid") or row.get("id") or ""),
        ),
    )


def csv_cell(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return value


def row_fieldnames(rows: list[dict[str, Any]], preferred: list[str]) -> list[str]:
    seen: set[str] = set()
    fields: list[str] = []
    for field in preferred:
        if field in seen:
            continue
        if any(field in row for row in rows):
            seen.add(field)
            fields.append(field)
    for row in rows:
        for field in row:
            if field not in seen:
                seen.add(field)
                fields.append(field)
    return fields


def write_csv(path: Path, rows: list[dict[str, Any]], preferred_fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = row_fieldnames(rows, preferred_fields) if rows else list(dict.fromkeys(preferred_fields))
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows([{key: csv_cell(row.get(key)) for key in fieldnames} for row in rows])


SONG_RAW_FIELDS = [
    "id",
    "type",
    "mid",
    "name",
    "title",
    "subtitle",
    "singer",
    "album",
    "mv",
    "interval",
    "isonly",
    "language",
    "genre",
    "index_cd",
    "index_album",
    "time_public",
    "status",
    "fnote",
    "file",
    "pay",
    "action",
    "ksong",
    "volume",
    "label",
    "url",
    "bpm",
    "version",
    "trace",
    "data_type",
    "modify_stamp",
    "pingpong",
    "aid",
    "ppurl",
    "tid",
    "ov",
    "sa",
    "es",
    "vs",
    "vi",
    "ktag",
    "vf",
    "va",
]
SONG_AUX_FIELDS = [
    "aux_target_singer",
    "aux_target_singer_mid",
    "aux_sort_key",
    "aux_source_albumMid",
    "aux_source_albumName",
    "aux_source_albumType",
    "aux_source_album_publishDate",
    "aux_source_album_singerName",
    "aux_target_singer_match",
    "aux_filter_step",
    "aux_filter_result",
    "aux_filter_reason",
    "aux_filter2_name_key",
    "aux_filter2_name_group_size",
    "aux_filter2_name_preferred_albumType",
    "aux_filter2_name_preferred_song_id",
    "aux_filter2_selected_song_key",
    "aux_filter2_selected_albumType",
    "aux_filter2_selected_song_id",
    "aux_source_albums",
    "aux_source",
]
SONG_FIELDS = SONG_RAW_FIELDS + SONG_AUX_FIELDS
ALBUM_RAW_FIELDS = [
    "albumMid",
    "albumName",
    "albumTranName",
    "publishDate",
    "totalNum",
    "albumType",
    "pmid",
    "albumID",
    "singerName",
    "tags",
]
ALBUM_AUX_FIELDS = [
    "aux_target_singer",
    "aux_target_singer_mid",
    "aux_page",
    "aux_row",
    "aux_sort_key",
    "aux_include_album",
    "aux_album_filter_reason",
    "aux_source",
]
ALBUM_FIELDS = ALBUM_RAW_FIELDS + ALBUM_AUX_FIELDS


async def collect_target(client: Client, target: SingerTarget, config: CollectConfig) -> dict[str, Any]:
    albums, api_total = await collect_singer_albums(client, target, config)
    albums_sorted = sorted_rows(albums)
    included_albums = [album for album in albums if album["aux_include_album"]]
    excluded_albums = [album for album in albums if not album["aux_include_album"]]
    songs_all: list[dict[str, Any]] = []
    songs_after_filter1_target_singer_match: list[dict[str, Any]] = []
    songs_removed_by_filter1_target_singer_match: list[dict[str, Any]] = []
    album_song_counts: dict[str, int | None] = {}
    for index, album in enumerate(included_albums, 1):
        print(f"[{index}/{len(included_albums)}] {target.name} album songs: {album.get('albumName')}")
        all_rows, kept, rejected, total = await collect_album_songs(client, target, album, config)
        songs_all.extend(all_rows)
        songs_after_filter1_target_singer_match.extend(kept)
        songs_removed_by_filter1_target_singer_match.extend(rejected)
        album_song_counts[str(raw_album_mid(album) or raw_album_id(album) or index)] = total

    deduped_rows, duplicate_rows = dedupe_songs(songs_after_filter1_target_singer_match)
    songs_after_filter2_dedupe = sorted_rows(deduped_rows)
    duplicate_sorted = sorted_rows(duplicate_rows)
    all_songs_sorted = sorted_rows(songs_all)
    rejected_sorted = sorted_rows(songs_removed_by_filter1_target_singer_match)
    included_sorted = sorted_rows(included_albums)
    excluded_sorted = sorted_rows(excluded_albums)
    output_dir = config.output_dir / target.slug
    output_dir.mkdir(parents=True, exist_ok=True)
    cleanup_song_output_files(output_dir)
    dump_json(output_dir / "albums_all.json", albums_sorted)
    dump_json(output_dir / "songs_all.json", all_songs_sorted)
    dump_json(output_dir / "songs_after_filter1_target_singer_match.json", sorted_rows(songs_after_filter1_target_singer_match))
    dump_json(output_dir / "songs_removed_by_filter1_target_singer_match.json", rejected_sorted)
    dump_json(output_dir / "songs_after_filter2_dedupe.json", songs_after_filter2_dedupe)
    dump_json(output_dir / "songs_removed_by_filter2_dedupe.json", duplicate_sorted)
    dump_json(output_dir / "albums_included.json", included_sorted)
    dump_json(output_dir / "albums_excluded.json", excluded_sorted)
    if config.write_csv:
        csv_output_dir = config.csv_output_dir / target.slug
        cleanup_song_output_files(csv_output_dir)
        write_csv(csv_output_dir / "albums_all.csv", albums_sorted, ALBUM_FIELDS)
        write_csv(csv_output_dir / "songs_all.csv", all_songs_sorted, SONG_FIELDS)
        write_csv(csv_output_dir / "songs_after_filter1_target_singer_match.csv", sorted_rows(songs_after_filter1_target_singer_match), SONG_FIELDS)
        write_csv(csv_output_dir / "songs_removed_by_filter1_target_singer_match.csv", rejected_sorted, SONG_FIELDS)
        write_csv(csv_output_dir / "songs_after_filter2_dedupe.csv", songs_after_filter2_dedupe, SONG_FIELDS)
        write_csv(csv_output_dir / "songs_removed_by_filter2_dedupe.csv", duplicate_sorted, SONG_FIELDS)
        write_csv(csv_output_dir / "albums_included.csv", included_sorted, ALBUM_FIELDS)
        write_csv(csv_output_dir / "albums_excluded.csv", excluded_sorted, ALBUM_FIELDS)

    summary = {
        "generated_at": now_iso(),
        "target": {"slug": target.slug, "name": target.name, "mid": target.mid},
        "source": {
            "albums": "qqmusic.singer.get_album_list",
            "album_songs": "qqmusic.album.get_song",
        },
        "rules": {
            "allowed_album_types": list(ALLOWED_ALBUM_TYPES),
            "song_keep_rule": "song.singer[].mid contains target singer mid",
        },
        "counts": {
            "album_api_total": api_total,
            "albums_total": len(albums),
            "albums_all": len(albums_sorted),
            "albums_included": len(included_albums),
            "albums_excluded": len(excluded_albums),
            "songs_all": len(all_songs_sorted),
            "songs_after_filter1_target_singer_match": len(songs_after_filter1_target_singer_match),
            "songs_removed_by_filter1_target_singer_match": len(songs_removed_by_filter1_target_singer_match),
            "songs_after_filter2_dedupe": len(songs_after_filter2_dedupe),
            "songs_removed_by_filter2_dedupe": len(duplicate_rows),
        },
        "album_type_counts": dict(Counter(str(album.get("albumType") or "") for album in albums).most_common()),
        "album_song_counts": album_song_counts,
        "outputs": {
            "albums_all_json": str((output_dir / "albums_all.json").as_posix()),
            "songs_all_json": str((output_dir / "songs_all.json").as_posix()),
            "songs_after_filter1_target_singer_match_json": str((output_dir / "songs_after_filter1_target_singer_match.json").as_posix()),
            "songs_removed_by_filter1_target_singer_match_json": str((output_dir / "songs_removed_by_filter1_target_singer_match.json").as_posix()),
            "songs_after_filter2_dedupe_json": str((output_dir / "songs_after_filter2_dedupe.json").as_posix()),
            "songs_removed_by_filter2_dedupe_json": str((output_dir / "songs_removed_by_filter2_dedupe.json").as_posix()),
            "albums_included_json": str((output_dir / "albums_included.json").as_posix()),
            "albums_excluded_json": str((output_dir / "albums_excluded.json").as_posix()),
        },
    }
    if config.write_csv:
        summary["outputs"].update(
            {
                "albums_all_csv_view": str((config.csv_output_dir / target.slug / "albums_all.csv").as_posix()),
                "songs_all_csv_view": str((config.csv_output_dir / target.slug / "songs_all.csv").as_posix()),
                "songs_after_filter1_target_singer_match_csv_view": str((config.csv_output_dir / target.slug / "songs_after_filter1_target_singer_match.csv").as_posix()),
                "songs_removed_by_filter1_target_singer_match_csv_view": str((config.csv_output_dir / target.slug / "songs_removed_by_filter1_target_singer_match.csv").as_posix()),
                "songs_after_filter2_dedupe_csv_view": str((config.csv_output_dir / target.slug / "songs_after_filter2_dedupe.csv").as_posix()),
                "songs_removed_by_filter2_dedupe_csv_view": str((config.csv_output_dir / target.slug / "songs_removed_by_filter2_dedupe.csv").as_posix()),
                "albums_included_csv_view": str((config.csv_output_dir / target.slug / "albums_included.csv").as_posix()),
                "albums_excluded_csv_view": str((config.csv_output_dir / target.slug / "albums_excluded.csv").as_posix()),
            }
        )
    dump_json(output_dir / "summary.json", summary)
    return {
        "summary": summary,
        "songs": songs_after_filter2_dedupe,
    }


async def run(config: CollectConfig) -> None:
    client = Client(rate=REQUEST_RATE, capacity=REQUEST_CAPACITY)
    summaries: list[dict[str, Any]] = []
    try:
        for target in config.singers:
            result = await collect_target(client, target, config)
            summaries.append(result["summary"])
    finally:
        await client.close()

    config.output_dir.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "generated_at": now_iso(),
        "source": "album_subset_candidate",
        "singer_source": config.singer_source,
        "rules": {
            "allowed_album_types": list(ALLOWED_ALBUM_TYPES),
            "song_keep_rule": "song.singer[].mid contains target singer mid",
            "validation_outputs": "each filter step writes kept rows and removed rows with aux_filter_reason when rows are removed",
            "csv_outputs": "optional validation/view output enabled by --write-csv; CSV files are kept outside the formal output directory",
        },
        "summaries": summaries,
        "counts": {
            "singers": len(config.singers),
            "albums_all": sum(item["counts"].get("albums_all", 0) for item in summaries),
            "songs_all": sum(item["counts"].get("songs_all", 0) for item in summaries),
            "songs_after_filter1_target_singer_match": sum(
                item["counts"].get("songs_after_filter1_target_singer_match", 0) for item in summaries
            ),
            "songs_removed_by_filter1_target_singer_match": sum(
                item["counts"].get("songs_removed_by_filter1_target_singer_match", 0) for item in summaries
            ),
            "songs_after_filter2_dedupe": sum(
                item["counts"].get("songs_after_filter2_dedupe", 0) for item in summaries
            ),
            "songs_removed_by_filter2_dedupe": sum(
                item["counts"].get("songs_removed_by_filter2_dedupe", 0) for item in summaries
            ),
        },
        "outputs": {},
    }
    dump_json(config.output_dir / "summary.json", snapshot)
    print(json.dumps(snapshot["counts"], ensure_ascii=False, indent=2))
    print(f"saved: {config.output_dir / 'summary.json'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build high-confidence singer songs from QQ Music album subsets.")
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--csv-output-dir", type=Path, default=DEFAULT_CSV_OUTPUT_DIR, help="CSV validation/view output directory used only with --write-csv.")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH, help="Singer registry JSON used when --singer is not provided.")
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)
    parser.add_argument("--max-singers", type=int, default=None, help="Limit registry singers for smoke tests.")
    parser.add_argument("--write-csv", action="store_true", help="Also write CSV view files for manual inspection. JSON is the formal output.")
    parser.add_argument(
        "--singer",
        action="append",
        type=parse_singer,
        help="Singer target as slug=name=mid. Can be repeated for tests. Defaults to all singers in --registry.",
    )
    parser.add_argument(
        "--test-four-singers",
        action="store_true",
        help="Use the four current test singers: Jay Chou, Joker Xue, JJ Lin, and Silence Wang.",
    )
    return parser.parse_args()


def main() -> None:
    ensure_utf8_stdout()
    args = parse_args()
    test_singers = tuple(SingerTarget(slug=slug, name=name, mid=mid) for slug, name, mid in TEST_SINGERS)
    if args.singer:
        singers = tuple(args.singer)
        singer_source = "explicit_singers"
    elif args.test_four_singers:
        singers = test_singers
        singer_source = "test_four_singers"
        if args.csv_output_dir == DEFAULT_CSV_OUTPUT_DIR:
            args.csv_output_dir = Path("data/processed/validation/four_singers/csv_views/high_confidence_singer_songs")
    else:
        singers = load_registry_singers(args.registry, args.max_singers)
        singer_source = "registry"
    config = CollectConfig(
        raw_dir=args.raw_dir,
        output_dir=args.output_dir,
        csv_output_dir=args.csv_output_dir,
        page_size=args.page_size,
        singers=singers,
        singer_source=singer_source,
        write_csv=args.write_csv,
    )
    validate_config(config)
    asyncio.run(run(config))


if __name__ == "__main__":
    main()
