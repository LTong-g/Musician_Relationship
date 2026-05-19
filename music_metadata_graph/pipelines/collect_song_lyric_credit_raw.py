from __future__ import annotations
import argparse
import asyncio
import csv
import json
import re
import sqlite3
import sys
from dataclasses import dataclass
from dataclasses import replace as dataclass_replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from qqmusic_api import Client
from qqmusic_api.algorithms import qrc_decrypt
from music_metadata_graph.run_log import run_with_log
from music_metadata_graph.pipelines.collect_song_producer_raw import CREDIT_TITLES, producer_groups
from music_metadata_graph.pipelines.defaults import DEFAULT_DB_PATH
from music_metadata_graph.pipelines.song_csv import escape_excel_formula_row

DEFAULT_QQMUSIC_ROOT = Path("data/raw/qqmusic")
DEFAULT_RAW_DIR = Path("data/raw/qqmusic/song_lyric_credit")
DEFAULT_PRODUCER_RAW_DIR = Path("data/raw/qqmusic/song_producer")
DEFAULT_CSV = Path("data/processed/validation/song_lyric_credit/csv_views/song_lyric_credit.csv")
REQUEST_RATE = 0.5
REQUEST_CAPACITY = 1
REQUEST_BATCH_SIZE = 20
PROGRESS_EVERY = 1000
CACHE_KIND = "qqmusic_lyric_credit_evidence"
SCHEMA_VERSION = 1
HEADER_EFFECTIVE_LINE_LIMIT = 5
HEADER_RAW_LINE_LIMIT = 10
ROLE_LABEL_SEPARATOR_RE = re.compile(r"[:：]")
LRC_META_RE = re.compile(r"^\s*\[(?:ti|ar|al|by|offset):", re.IGNORECASE)
LRC_TIMESTAMP_RE = re.compile(r"^\s*\[[0-9]{1,2}:[0-9]{2}(?:\.[0-9]{1,3})?\]")
LYRICIST_EXPLICIT_LABELS = ("作词", "作詞", "lyrics", "lyric", "lyricist")
COMPOSER_EXPLICIT_LABELS = ("作曲", "composed", "composer", "music")
LYRICIST_SINGLE_LABELS = {"词", "詞"}
COMPOSER_SINGLE_LABELS = {"曲"}


@dataclass(frozen=True)
class LyricCreditConfig:
    raw_dir: Path
    producer_raw_dir: Path
    db_path: Path
    csv_path: Path
    force: bool
    max_songs: int | None
    artist_mid: str | None
    artist_name: str | None
    batch_size: int


@dataclass(frozen=True)
class FetchFailure:
    song_mid: str
    path: Path
    reason: str


@dataclass(frozen=True)
class CacheLoadResult:
    payload: dict[str, Any]
    status: str


def ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    temp_path = path.with_name(f"{path.name}.tmp")
    temp_path.write_text(text, encoding="utf-8")
    temp_path.replace(path)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def try_load_cached_json(path: Path) -> Any | None:
    try:
        return load_json(path)
    except (OSError, json.JSONDecodeError):
        return None


def connect(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise FileNotFoundError(f"Database does not exist: {db_path}")
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def lyric_path(raw_dir: Path, song_mid: str) -> Path:
    return raw_dir / f"{song_mid}.json"


def producer_roles(payload: Any) -> set[str]:
    roles: set[str] = set()
    for group in producer_groups(payload):
        role = str(group.get("title") or group.get("Title") or "")
        if role not in CREDIT_TITLES:
            continue
        producer_list = (
            group.get("producers")
            if isinstance(group.get("producers"), list)
            else group.get("Producers")
        )
        producers = producer_list if isinstance(producer_list, list) else []
        if producers:
            roles.add(role)
    return roles


def missing_credit_roles_from_producer(payload: Any) -> set[str]:
    return set(CREDIT_TITLES) - producer_roles(payload)


def strip_lrc_timestamp(line: str) -> str:
    return LRC_TIMESTAMP_RE.sub("", line).strip()


def effective_lyric_lines(lyric: str) -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    for raw_index, line in enumerate((lyric or "").replace("\r", "").split("\n"), 1):
        stripped = line.strip()
        if not stripped or LRC_META_RE.match(stripped):
            continue
        rows.append((raw_index, stripped))
    return rows


def lyric_text_from_payload(payload: Any) -> str:
    if not isinstance(payload, dict):
        return ""
    lyric = str(payload.get("lyric") or "")
    if int(payload.get("crypt") or 0) == 1 and lyric:
        return qrc_decrypt(lyric)
    return lyric


def is_lyric_credit_evidence(payload: Any) -> bool:
    return (
        isinstance(payload, dict)
        and payload.get("cache_kind") == CACHE_KIND
        and int(payload.get("schema_version") or 0) >= 1
    )


def raw_lyric_lines(lyric: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw_index, line in enumerate((lyric or "").replace("\r", "").split("\n"), 1):
        if raw_index > HEADER_RAW_LINE_LIMIT:
            break
        rows.append({"raw_row_index": raw_index, "text": line})
    return rows


def effective_header_line_rows(lyric: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for effective_index, (raw_index, line) in enumerate(
        effective_lyric_lines(lyric)[:HEADER_EFFECTIVE_LINE_LIMIT], 1
    ):
        if raw_index > HEADER_RAW_LINE_LIMIT:
            continue
        rows.append(
            {
                "raw_row_index": raw_index,
                "effective_row_index": effective_index,
                "text": strip_lrc_timestamp(line),
            }
        )
    return rows


def roles_from_label(label: str) -> set[str]:
    normalized = label.strip().casefold()
    roles: set[str] = set()
    if normalized in LYRICIST_SINGLE_LABELS:
        roles.add("作词")
    if normalized in COMPOSER_SINGLE_LABELS:
        roles.add("作曲")
    if any(token in normalized for token in LYRICIST_EXPLICIT_LABELS):
        roles.add("作词")
    if any(token in normalized for token in COMPOSER_EXPLICIT_LABELS):
        roles.add("作曲")
    return roles


def parse_lyric_credit_rows_from_lines(
    header_lines: list[dict[str, Any]], *, raw_path: Path | str = ""
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for line_row in header_lines:
        raw_index = int(line_row.get("raw_row_index") or 0)
        effective_index = int(line_row.get("effective_row_index") or 0)
        clean = str(line_row.get("text") or "").strip()
        parts = ROLE_LABEL_SEPARATOR_RE.split(clean, maxsplit=1)
        if len(parts) != 2:
            continue
        label, value = parts[0].strip(), parts[1].strip()
        if not value:
            continue
        for role in roles_from_label(label):
            key = (role, value)
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "role": role,
                    "name": value,
                    "raw_json_path": Path(raw_path).as_posix() if raw_path else "",
                    "raw_page": 0,
                    "raw_row_index": raw_index,
                    "effective_row_index": effective_index,
                    "matched_line": clean,
                }
            )
    return rows


def parse_lyric_credit_rows_from_text(
    lyric: str, *, raw_path: Path | str = ""
) -> list[dict[str, Any]]:
    return parse_lyric_credit_rows_from_lines(effective_header_line_rows(lyric), raw_path=raw_path)


def parse_lyric_credit_rows(payload: Any, *, raw_path: Path | str = "") -> list[dict[str, Any]]:
    if is_lyric_credit_evidence(payload):
        rows: list[dict[str, Any]] = []
        for row in payload.get("parsed_credit_rows") or []:
            if not isinstance(row, dict):
                continue
            item = dict(row)
            item["raw_json_path"] = (
                Path(raw_path).as_posix() if raw_path else str(item.get("raw_json_path") or "")
            )
            item.setdefault("raw_page", 0)
            item.setdefault("raw_row_index", 0)
            rows.append(item)
        return rows
    return parse_lyric_credit_rows_from_text(lyric_text_from_payload(payload), raw_path=raw_path)


def evidence_parse_status(lyric: str, parsed_rows: list[dict[str, Any]]) -> str:
    if not lyric.strip():
        return "empty_lyric"
    roles = {str(row.get("role") or "") for row in parsed_rows}
    if {"作词", "作曲"}.issubset(roles):
        return "parsed_both"
    if roles:
        return "parsed_any"
    return "no_credit_lines"


def build_lyric_credit_evidence(
    payload: Any,
    *,
    target: dict[str, Any] | None = None,
    raw_path: Path | str = "",
) -> dict[str, Any]:
    if is_lyric_credit_evidence(payload):
        return dict(payload)
    target = target or {}
    payload_dict = payload if isinstance(payload, dict) else {}
    lyric = lyric_text_from_payload(payload)
    header_lines = effective_header_line_rows(lyric)
    parsed_rows = parse_lyric_credit_rows_from_lines(header_lines, raw_path=raw_path)
    song_mid = str(target.get("song_mid") or "")
    if not song_mid and raw_path:
        song_mid = Path(raw_path).stem
    lyric_line_count = len([line for line in lyric.replace("\r", "").split("\n") if line.strip()])
    return {
        "cache_kind": CACHE_KIND,
        "schema_version": SCHEMA_VERSION,
        "source_api": "qqmusic.lyric.get_lyric",
        "song_mid": song_mid,
        "song_id": str(target.get("song_id") or payload_dict.get("songID") or ""),
        "song_name": str(target.get("song_name") or ""),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "producer_missing_roles": list(target.get("missing_roles") or []),
        "source_crypt": int(payload_dict.get("crypt") or 0),
        "lyric_empty": not bool(lyric.strip()),
        "lyric_line_count": lyric_line_count,
        "raw_header_lines": raw_lyric_lines(lyric),
        "effective_header_lines": header_lines,
        "parsed_credit_rows": parsed_rows,
        "parse_status": evidence_parse_status(lyric, parsed_rows),
    }


def load_or_migrate_lyric_credit_evidence(
    path: Path,
    *,
    target: dict[str, Any] | None = None,
) -> CacheLoadResult:
    payload = load_json(path)
    if is_lyric_credit_evidence(payload):
        return CacheLoadResult(payload=dict(payload), status="evidence_cache_hit")
    evidence = build_lyric_credit_evidence(payload, target=target, raw_path=path)
    dump_json(path, evidence)
    return CacheLoadResult(payload=evidence, status="migrated_legacy_raw")


def try_load_lyric_credit_evidence(
    path: Path, *, target: dict[str, Any] | None = None
) -> CacheLoadResult | None:
    try:
        return load_or_migrate_lyric_credit_evidence(path, target=target)
    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        return None


def target_song_rows(
    connection: sqlite3.Connection, config: LyricCreditConfig
) -> list[dict[str, Any]]:
    params: list[Any] = []
    where_sql = ""
    if config.artist_mid:
        where_sql = "WHERE EXISTS (SELECT 1 FROM song_singers WHERE song_singers.song_mid = songs.mid AND song_singers.singer_mid = ?)"
        params.append(config.artist_mid)
    elif config.artist_name:
        where_sql = (
            "WHERE EXISTS ("
            "SELECT 1 FROM song_singers "
            "JOIN artists ON artists.mid = song_singers.singer_mid "
            "WHERE song_singers.song_mid = songs.mid AND artists.name = ?"
            ")"
        )
        params.append(config.artist_name)
    rows = connection.execute(
        f"""
        SELECT mid, id, name
        FROM songs
        {where_sql}
        ORDER BY name, id, mid
        """,
        params,
    ).fetchall()
    return [dict(row) for row in rows]


def lyric_target_rows(
    connection: sqlite3.Connection, config: LyricCreditConfig
) -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    for row in target_song_rows(connection, config):
        song_mid = str(row["mid"])
        producer_path = config.producer_raw_dir / f"{song_mid}.json"
        payload = try_load_cached_json(producer_path)
        if payload is None:
            continue
        missing_roles = missing_credit_roles_from_producer(payload)
        if not missing_roles:
            continue
        targets.append(
            {
                "song_mid": song_mid,
                "song_id": str(row["id"]),
                "song_name": str(row["name"]),
                "missing_roles": sorted(missing_roles),
                "producer_raw_json_path": producer_path.as_posix(),
            }
        )
    if config.max_songs is not None:
        targets = targets[: config.max_songs]
    return targets


async def execute_request_batch(
    client: Client,
    config: LyricCreditConfig,
    batch: list[tuple[int, dict[str, Any], Path, Any]],
) -> tuple[list[tuple[int, dict[str, Any], dict[str, Any], str, Path]], list[FetchFailure]]:
    loaded: list[tuple[int, dict[str, Any], dict[str, Any], str, Path]] = []
    failures: list[FetchFailure] = []

    def save_payload(index: int, target: dict[str, Any], path: Path, result: Any) -> None:
        payload = result.model_dump(mode="json") if hasattr(result, "model_dump") else result
        evidence = build_lyric_credit_evidence(payload, target=target, raw_path=path)
        dump_json(path, evidence)
        loaded.append((index, target, evidence, "fetched", path))

    if not batch:
        return loaded, failures

    requests = [request for _, _, _, request in batch]
    try:
        results = await client.gather(requests, batch_size=len(requests), return_exceptions=True)
    except Exception:
        for index, target, path, request in batch:
            try:
                result = await client.execute(request)
            except Exception as item_exc:
                failures.append(
                    FetchFailure(
                        song_mid=str(target["song_mid"]),
                        path=path,
                        reason=f"{type(item_exc).__name__}: {item_exc}",
                    )
                )
                continue
            save_payload(index, target, path, result)
        return sorted(loaded, key=lambda item: item[0]), failures

    for (index, target, path, _request), result in zip(batch, results, strict=True):
        if isinstance(result, Exception):
            failures.append(
                FetchFailure(
                    song_mid=str(target["song_mid"]),
                    path=path,
                    reason=f"{type(result).__name__}: {result}",
                )
            )
            continue
        save_payload(index, target, path, result)
    return sorted(loaded, key=lambda item: item[0]), failures


def write_credit_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "song_mid",
        "song_id",
        "song_name",
        "missing_roles",
        "status",
        "parsed_lyricists",
        "parsed_composers",
        "raw_json_path",
        "producer_raw_json_path",
        "lyric_line_count",
        "matched_lines_json",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\r\n"
        )
        writer.writeheader()
        writer.writerows(escape_excel_formula_row(row) for row in rows)


def build_csv_row(target: dict[str, Any], payload: Any, status: str, path: Path) -> dict[str, Any]:
    parsed_rows = parse_lyric_credit_rows(payload, raw_path=path)
    lyricists = [row["name"] for row in parsed_rows if row["role"] == "作词"]
    composers = [row["name"] for row in parsed_rows if row["role"] == "作曲"]
    lyric_line_count = int(payload.get("lyric_line_count") or 0) if isinstance(payload, dict) else 0
    return {
        "song_mid": target["song_mid"],
        "song_id": target["song_id"],
        "song_name": target["song_name"],
        "missing_roles": "/".join(target["missing_roles"]),
        "status": status,
        "parsed_lyricists": " / ".join(lyricists),
        "parsed_composers": " / ".join(composers),
        "raw_json_path": path.as_posix(),
        "producer_raw_json_path": target["producer_raw_json_path"],
        "lyric_line_count": lyric_line_count,
        "matched_lines_json": json.dumps(
            [row["matched_line"] for row in parsed_rows], ensure_ascii=False, separators=(",", ":")
        ),
    }


async def collect(config: LyricCreditConfig) -> dict[str, Any]:
    if config.batch_size <= 0:
        raise ValueError("--batch-size must be greater than 0.")
    connection = connect(config.db_path)
    try:
        targets = lyric_target_rows(connection, config)
    finally:
        connection.close()

    client = Client(rate=REQUEST_RATE, capacity=REQUEST_CAPACITY)
    fetched = 0
    evidence_cache_hits = 0
    migrated_legacy_raw = 0
    failed_migrations = 0
    fetch_failures: list[FetchFailure] = []
    csv_rows: list[dict[str, Any]] = []
    pending: list[tuple[int, dict[str, Any], Path, Any]] = []

    async def handle_loaded(
        loaded_rows: list[tuple[int, dict[str, Any], dict[str, Any], str, Path]],
    ) -> None:
        nonlocal fetched, evidence_cache_hits, migrated_legacy_raw
        for loaded_index, target, payload, status, path in loaded_rows:
            display_index = loaded_index + 1
            fetched += int(status == "fetched")
            evidence_cache_hits += int(status == "evidence_cache_hit")
            migrated_legacy_raw += int(status == "migrated_legacy_raw")
            csv_rows.append(build_csv_row(target, payload, status, path))
            if (
                status == "fetched"
                or display_index == len(targets)
                or display_index % PROGRESS_EVERY == 0
            ):
                print(
                    f"[{display_index}/{len(targets)}] song_mid={target['song_mid']} status={status} saved={path.as_posix()}",
                    flush=True,
                )

    async def flush_pending() -> None:
        if not pending:
            return
        batch = list(pending)
        pending.clear()
        loaded, failures = await execute_request_batch(client, config, batch)
        fetch_failures.extend(failures)
        await handle_loaded(loaded)
        for failure in failures:
            print(
                f"song_mid={failure.song_mid} status=failed reason={failure.reason} saved={failure.path.as_posix()}",
                flush=True,
            )

    try:
        for index, target in enumerate(targets):
            song_mid = str(target["song_mid"])
            path = lyric_path(config.raw_dir, song_mid)
            if path.exists() and not config.force:
                cache_result = try_load_lyric_credit_evidence(path, target=target)
                if cache_result is not None:
                    await handle_loaded(
                        [(index, target, cache_result.payload, cache_result.status, path)]
                    )
                    continue
                failed_migrations += 1
            request = dataclass_replace(client.lyric.get_lyric(song_mid), response_model=None)
            pending.append((index, target, path, request))
            if len(pending) >= config.batch_size:
                await flush_pending()
        await flush_pending()
    finally:
        await client.close()

    write_credit_csv(config.csv_path, csv_rows)
    parsed_both = sum(1 for row in csv_rows if row["parsed_lyricists"] and row["parsed_composers"])
    parsed_any = sum(1 for row in csv_rows if row["parsed_lyricists"] or row["parsed_composers"])
    result = {
        "songs_with_incomplete_producer_credits": len(targets),
        "artist_mid": config.artist_mid or "",
        "artist_name": config.artist_name or "",
        "batch_size": config.batch_size,
        "fetched": fetched,
        "cache_hits": evidence_cache_hits,
        "evidence_cache_hits": evidence_cache_hits,
        "migrated_legacy_raw": migrated_legacy_raw,
        "failed_migrations": failed_migrations,
        "failed_fetches": len(fetch_failures),
        "failed_song_mids": [failure.song_mid for failure in fetch_failures][:50],
        "parsed_any_credit": parsed_any,
        "parsed_both_credits": parsed_both,
        "csv": config.csv_path.as_posix(),
        "raw_dir": config.raw_dir.as_posix(),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if fetch_failures:
        failed_mids = ", ".join(failure.song_mid for failure in fetch_failures)
        raise RuntimeError(
            f"Failed to fetch {len(fetch_failures)} song lyric request(s). Rerun the command to continue from cached successes. Failed song mids: {failed_mids}"
        )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect QQ Music lyric raw JSON for songs whose structured producer credits are incomplete."
    )
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--producer-raw-dir", type=Path, default=DEFAULT_PRODUCER_RAW_DIR)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument(
        "--force", action="store_true", help="Refetch and overwrite cached lyric raw JSON."
    )
    parser.add_argument("--max-songs", type=int, default=None, help="Limit songs for smoke tests.")
    parser.add_argument(
        "--artist-mid",
        default=None,
        help="Only collect songs whose singer list contains this artist mid.",
    )
    parser.add_argument(
        "--artist-name",
        default=None,
        help="Only collect songs whose singer list contains this exact artist name.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=REQUEST_BATCH_SIZE,
        help="Maximum request descriptors per QQ Music CGI batch.",
    )
    return parser.parse_args()


def _main() -> None:
    ensure_utf8_stdout()
    args = parse_args()
    asyncio.run(
        collect(
            LyricCreditConfig(
                raw_dir=args.raw_dir,
                producer_raw_dir=args.producer_raw_dir,
                db_path=args.db,
                csv_path=args.csv,
                force=args.force,
                max_songs=args.max_songs,
                artist_mid=args.artist_mid,
                artist_name=args.artist_name,
                batch_size=args.batch_size,
            )
        )
    )


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()
