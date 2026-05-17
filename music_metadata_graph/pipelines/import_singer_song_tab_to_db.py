from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from music_metadata_graph.run_log import run_with_log
from music_metadata_graph.pipelines.defaults import DEFAULT_DB_PATH, DEFAULT_MVP_DB_PATH
from typing import Any

from music_metadata_graph.pipelines.collect_singer_song_tab_raw import CollectConfig as SongTabCollectConfig
from music_metadata_graph.pipelines.collect_singer_song_tab_raw import DEFAULT_PAGE_SIZE as SONG_TAB_PAGE_SIZE
from music_metadata_graph.pipelines.collect_singer_song_tab_raw import DEFAULT_RAW_DIR as DEFAULT_QQMUSIC_RAW_DIR
from music_metadata_graph.pipelines.collect_singer_song_tab_raw import DEFAULT_SINGER_LIST_RAW_DIR
from music_metadata_graph.pipelines.collect_singer_song_tab_raw import resolve_targets as resolve_song_tab_targets
from music_metadata_graph.pipelines.quick_search_artist_mid import split_artist_names
from music_metadata_graph.pipelines.song_csv import BASE_SONG_CSV_FIELDS, sort_song_csv_rows, write_song_csv


DEFAULT_RAW_DIR = Path("data/raw/qqmusic/singer_homepage_song_tab")
DEFAULT_REJECTION_CSV = Path("data/processed/validation/song_import_rejections/csv_views/song_import_rejections.csv")
SONG_CSV_FIELDS = BASE_SONG_CSV_FIELDS


@dataclass(frozen=True)
class ImportConfig:
    raw_dir: Path
    db_path: Path
    rejection_csv: Path
    singer_list_raw_dir: Path
    qqmusic_raw_dir: Path
    all_available_song_tabs: bool
    mvp: bool
    mids: tuple[str, ...]
    names: tuple[str, ...]


@dataclass(frozen=True)
class SingerTarget:
    mid: str
    name: str


def ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_csv_values(values: list[str] | None) -> tuple[str, ...]:
    if not values:
        return ()
    parsed: list[str] = []
    for value in values:
        parsed.extend(part.strip() for part in value.split(",") if part.strip())
    return tuple(parsed)


def parse_page(path: Path) -> int:
    parts = path.stem.split("_")
    if len(parts) >= 2 and parts[1].isdigit():
        return int(parts[1])
    return 0


def is_missing(value: Any) -> bool:
    return value is None or value == ""


def compact_singers(singers: list[Any]) -> str:
    parts: list[str] = []
    for order, singer in enumerate(singers, 1):
        if not isinstance(singer, dict):
            parts.append(f"{order}:::")
            continue
        parts.append(
            f"{order}:{singer.get('mid') or ''}:{singer.get('id') or ''}:{singer.get('name') or ''}"
        )
    return "; ".join(parts)


def singers_json(singers: list[Any]) -> str:
    rows: list[dict[str, str]] = []
    for singer in singers:
        if not isinstance(singer, dict):
            rows.append({"mid": "", "name": ""})
            continue
        rows.append(
            {
                "mid": str(singer.get("mid") or ""),
                "name": str(singer.get("name") or ""),
            }
        )
    return json.dumps(rows, ensure_ascii=False, separators=(",", ":"))


def load_song_rows(raw_dir: Path, target_mids: tuple[str, ...]) -> list[dict[str, Any]]:
    if target_mids:
        files: list[Path] = []
        missing_dirs: list[str] = []
        for mid in target_mids:
            singer_dir = raw_dir / mid
            singer_files = sorted(singer_dir.glob("*.json"))
            if not singer_files:
                missing_dirs.append(mid)
            files.extend(singer_files)
        if missing_dirs:
            raise FileNotFoundError(
                "Singer homepage song-tab raw JSON is missing for targets: " + ", ".join(missing_dirs)
            )
    else:
        files = sorted(raw_dir.glob("*/*.json"))
    if not files:
        raise FileNotFoundError(f"No singer homepage song-tab JSON files found: {raw_dir}")
    rows: list[dict[str, Any]] = []
    for path in files:
        payload = load_json(path)
        page = parse_page(path)
        for index, song in enumerate(((payload.get("SongTab") or {}).get("List") or []), 1):
            rows.append(
                {
                    "song": song,
                    "raw_json_path": path.as_posix(),
                    "raw_page": page,
                    "raw_row_index": index,
                }
            )
    return rows


def connect(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise FileNotFoundError(f"Database does not exist: {db_path}")
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS songs (
            mid TEXT NOT NULL PRIMARY KEY,
            id INTEGER NOT NULL UNIQUE,
            name TEXT NOT NULL,
            title TEXT NOT NULL,
            language INTEGER NOT NULL,
            album_mid TEXT NOT NULL,
            raw_json_path TEXT NOT NULL DEFAULT '',
            raw_page INTEGER NOT NULL DEFAULT 0,
            raw_row_index INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(album_mid) REFERENCES albums(mid)
        )
        """
    )
    rebuild_legacy_song_singers = False
    existing_song_singers = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'song_singers'"
    ).fetchone()
    if existing_song_singers:
        foreign_keys = connection.execute("PRAGMA foreign_key_list(song_singers)").fetchall()
        rebuild_legacy_song_singers = any(str(row["table"]) == "singers" for row in foreign_keys)
    if rebuild_legacy_song_singers:
        connection.execute("DROP TABLE song_singers")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS song_singers (
            song_mid TEXT NOT NULL,
            singer_order INTEGER NOT NULL,
            singer_mid TEXT NOT NULL,
            raw_json_path TEXT NOT NULL DEFAULT '',
            raw_page INTEGER NOT NULL DEFAULT 0,
            raw_row_index INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY(song_mid, singer_order),
            FOREIGN KEY(song_mid) REFERENCES songs(mid) ON DELETE CASCADE,
            FOREIGN KEY(singer_mid) REFERENCES artists(mid)
        )
        """
    )
    legacy_singers = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'singers'"
    ).fetchone()
    artists = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'artists'"
    ).fetchone()
    if legacy_singers and artists:
        connection.execute("DROP TABLE singers")


def load_reference_sets(connection: sqlite3.Connection) -> tuple[set[str], set[str]]:
    singer_mids = {str(row["mid"]) for row in connection.execute("SELECT mid FROM artists").fetchall()}
    album_mids = {str(row["mid"]) for row in connection.execute("SELECT mid FROM albums").fetchall()}
    if not singer_mids:
        raise ValueError("No artists found in database.")
    if not album_mids:
        raise ValueError("No albums found in database.")
    return singer_mids, album_mids


def load_unique_artist_name_mid_map(connection: sqlite3.Connection) -> tuple[dict[str, str], int]:
    rows = connection.execute("SELECT name, mid FROM artists WHERE name <> '' ORDER BY rowid").fetchall()
    mids_by_name: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        name = str(row["name"] or "").strip()
        mid = str(row["mid"] or "").strip()
        if name and mid:
            mids_by_name[name].add(mid)
    unique_map = {name: next(iter(mids)) for name, mids in mids_by_name.items() if len(mids) == 1}
    ambiguous_names = sum(1 for mids in mids_by_name.values() if len(mids) > 1)
    return unique_map, ambiguous_names


def resolve_missing_artist_name_mids(name: str, artist_name_mid_map: dict[str, str]) -> list[str]:
    source_name = name.strip()
    if not source_name:
        return []
    search_names = split_artist_names(source_name) if "/" in source_name else (source_name,)
    resolved: list[str] = []
    seen: set[str] = set()
    for search_name in search_names:
        mid = artist_name_mid_map.get(search_name, "")
        if mid and mid not in seen:
            seen.add(mid)
            resolved.append(mid)
    return resolved


def resolve_singer_mids(singer: Any, artist_name_mid_map: dict[str, str]) -> list[str]:
    if not isinstance(singer, dict):
        return []
    singer_mid = str(singer.get("mid") or "").strip()
    if singer_mid:
        return [singer_mid]
    singer_name = str(singer.get("name") or "").strip()
    return resolve_missing_artist_name_mids(singer_name, artist_name_mid_map)


def unique_targets(rows: list[sqlite3.Row]) -> tuple[SingerTarget, ...]:
    targets: list[SingerTarget] = []
    seen: set[str] = set()
    for row in rows:
        mid = str(row["mid"])
        if mid in seen:
            continue
        seen.add(mid)
        targets.append(SingerTarget(mid=mid, name=str(row["name"])))
    return tuple(targets)


def load_existing_song_tab_mids(connection: sqlite3.Connection, config: ImportConfig) -> tuple[str, ...]:
    song_tab_config = SongTabCollectConfig(
        raw_dir=config.qqmusic_raw_dir,
        db_path=config.db_path,
        page_size=SONG_TAB_PAGE_SIZE,
        singer_list_raw_dir=config.singer_list_raw_dir,
        max_pages_per_singer=None,
        force=False,
        all_singers=True,
        mvp=config.mvp,
        mids=(),
        names=(),
    )
    target_mids = tuple(target.mid for target in resolve_song_tab_targets(song_tab_config))
    existing_target_mids = tuple(
        mid
        for mid in target_mids
        if any((config.raw_dir / mid).glob("page_*_size_*.json"))
    )
    if not existing_target_mids:
        raise FileNotFoundError("No step-4 target singer homepage song-tab raw JSON exists yet.")
    return existing_target_mids


def resolve_target_mids(connection: sqlite3.Connection, config: ImportConfig) -> tuple[str, ...]:
    if config.all_available_song_tabs:
        if config.mids or config.names:
            raise ValueError("--all cannot be combined with --mid or --name.")
        return load_existing_song_tab_mids(connection, config)
    requested_count = len(config.mids) + len(config.names)
    if requested_count == 0:
        raise ValueError("Provide --all, or at least one --mid or --name.")

    rows: list[sqlite3.Row] = []
    missing: list[str] = []
    for mid in config.mids:
        row = connection.execute("SELECT mid, name FROM artists WHERE mid = ?", (mid,)).fetchone()
        if row is None:
            missing.append(f"mid:{mid}")
        else:
            rows.append(row)
    for name in config.names:
        matched = connection.execute("SELECT mid, name FROM artists WHERE name = ? ORDER BY rowid", (name,)).fetchall()
        if not matched:
            missing.append(f"name:{name}")
        elif len(matched) > 1:
            choices = ", ".join(f"{row['name']}({row['mid']})" for row in matched[:10])
            raise ValueError(f"Name is ambiguous, use --mid instead: {name}; matches: {choices}")
        else:
            rows.append(matched[0])
    if missing:
        raise ValueError("Singer targets not found in database: " + ", ".join(missing))
    return tuple(target.mid for target in unique_targets(rows))


def group_unique_songs(raw_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, bool], int]:
    by_mid: dict[str, list[dict[str, Any]]] = defaultdict(list)
    missing_mid_rows = 0
    for row in raw_rows:
        song_mid = str(row["song"].get("mid") or "").strip()
        if not song_mid:
            missing_mid_rows += 1
            continue
        by_mid[song_mid].append(row)

    conflict_by_mid: dict[str, bool] = {}
    unique_rows: list[dict[str, Any]] = []
    for song_mid, rows in sorted(by_mid.items()):
        serialized = {
            json.dumps(row["song"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            for row in rows
        }
        conflict_by_mid[song_mid] = len(serialized) > 1
        unique_rows.append(rows[0])
    return unique_rows, conflict_by_mid, missing_mid_rows


def evaluate_rows(
    unique_rows: list[dict[str, Any]],
    conflict_by_mid: dict[str, bool],
    singer_mids: set[str],
    album_mids: set[str],
    artist_name_mid_map: dict[str, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    duplicate_ids = find_duplicate_song_ids(unique_rows)
    accepted_songs: list[dict[str, Any]] = []
    accepted_singers: list[dict[str, Any]] = []
    rejections: list[dict[str, Any]] = []

    for row in unique_rows:
        song = row["song"]
        song_mid = str(song.get("mid") or "").strip()
        song_id = song.get("id")
        name = str(song.get("name") or "").strip()
        title = str(song.get("title") or "").strip()
        language = song.get("language")
        album = song.get("album") if isinstance(song.get("album"), dict) else {}
        album_mid = str(album.get("mid") or "").strip()
        singers = song.get("singer") if isinstance(song.get("singer"), list) else []
        reasons: list[str] = []
        problem_singers: list[str] = []

        if conflict_by_mid.get(song_mid):
            reasons.append("duplicate_song_mid_conflict")
        if not song_mid:
            reasons.append("missing_song_mid")
        if is_missing(song_id):
            reasons.append("missing_song_id")
        elif song_id in duplicate_ids:
            reasons.append("duplicate_song_id")
        if not name:
            reasons.append("missing_name")
        if not title:
            reasons.append("missing_title")
        if is_missing(language):
            reasons.append("missing_language")
        if not album_mid:
            reasons.append("missing_album_mid")
        elif album_mid not in album_mids:
            reasons.append("album_mid_not_in_albums")
        if not singers:
            reasons.append("empty_singer_list")
        for order, singer in enumerate(singers, 1):
            singer_name = (singer or {}).get("name") if isinstance(singer, dict) else ""
            singer_id = (singer or {}).get("id") if isinstance(singer, dict) else ""
            resolved_mids = resolve_singer_mids(singer, artist_name_mid_map)
            if not resolved_mids:
                reasons.append("missing_singer_mid")
                problem_singers.append(f"{order}::{singer_id}:{singer_name}")
            elif any(singer_mid not in singer_mids for singer_mid in resolved_mids):
                reasons.append("singer_mid_not_in_singers")
                problem_singers.append(f"{order}:{'/'.join(resolved_mids)}:{singer_id}:{singer_name}")

        reasons = sorted(set(reasons))
        if reasons:
            rejections.append(build_rejection_row(row, reasons, problem_singers))
            continue

        accepted_songs.append(
            {
                "mid": song_mid,
                "id": int(song_id),
                "name": name,
                "title": title,
                "language": int(language),
                "album_mid": album_mid,
                "raw_json_path": row["raw_json_path"],
                "raw_page": int(row["raw_page"]),
                "raw_row_index": int(row["raw_row_index"]),
            }
        )
        accepted_singer_order = 0
        for singer in singers:
            for singer_mid in resolve_singer_mids(singer, artist_name_mid_map):
                accepted_singer_order += 1
                accepted_singers.append(
                    {
                        "song_mid": song_mid,
                        "singer_order": accepted_singer_order,
                        "singer_mid": singer_mid,
                        "raw_json_path": row["raw_json_path"],
                        "raw_page": int(row["raw_page"]),
                        "raw_row_index": int(row["raw_row_index"]),
                    }
                )
    return accepted_songs, accepted_singers, rejections


def find_duplicate_song_ids(unique_rows: list[dict[str, Any]]) -> set[Any]:
    counts: Counter[Any] = Counter()
    for row in unique_rows:
        song_id = row["song"].get("id")
        if not is_missing(song_id):
            counts[song_id] += 1
    return {song_id for song_id, count in counts.items() if count > 1}


def build_rejection_row(row: dict[str, Any], reasons: list[str], problem_singers: list[str]) -> dict[str, Any]:
    song = row["song"]
    album = song.get("album") if isinstance(song.get("album"), dict) else {}
    singers = song.get("singer") if isinstance(song.get("singer"), list) else []
    return {
        "song_mid": song.get("mid") or "",
        "song_id": song.get("id") if song.get("id") is not None else "",
        "song_name": song.get("name") or "",
        "song_title": song.get("title") or "",
        "song_language": song.get("language") if song.get("language") is not None else "",
        "album_mid": album.get("mid") or "",
        "album_id": album.get("id") if album.get("id") is not None else "",
        "album_name": album.get("name") or "",
        "album_type": album.get("albumType") or "",
        "album_publish_date": album.get("publishDate") or album.get("time_public") or "",
        "singer_count": len(singers),
        "singers": compact_singers(singers),
        "singers_json": singers_json(singers),
        "problem_singers": "; ".join(problem_singers),
        "reason_flags": ";".join(reasons),
        "raw_json_path": row["raw_json_path"],
        "raw_page": row["raw_page"],
        "raw_row_index": row["raw_row_index"],
    }


def write_rejection_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    write_song_csv(path, sort_song_csv_rows(rows), include_credits=False)


def replace_songs(
    connection: sqlite3.Connection,
    songs: list[dict[str, Any]],
    song_singers: list[dict[str, Any]],
) -> None:
    with connection:
        connection.execute("DELETE FROM song_singers")
        connection.execute("DELETE FROM songs")
        connection.executemany(
            """
            INSERT INTO songs (
                mid, id, name, title, language, album_mid,
                raw_json_path, raw_page, raw_row_index
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row["mid"],
                    row["id"],
                    row["name"],
                    row["title"],
                    row["language"],
                    row["album_mid"],
                    row["raw_json_path"],
                    row["raw_page"],
                    row["raw_row_index"],
                )
                for row in songs
            ],
        )
        connection.executemany(
            """
            INSERT INTO song_singers (
                song_mid, singer_order, singer_mid,
                raw_json_path, raw_page, raw_row_index
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row["song_mid"],
                    row["singer_order"],
                    row["singer_mid"],
                    row["raw_json_path"],
                    row["raw_page"],
                    row["raw_row_index"],
                )
                for row in song_singers
            ],
        )


def run(config: ImportConfig) -> dict[str, Any]:
    with connect(config.db_path) as connection:
        target_mids = resolve_target_mids(connection, config)
        raw_rows = load_song_rows(config.raw_dir, target_mids)
        unique_rows, conflict_by_mid, missing_mid_rows = group_unique_songs(raw_rows)
        create_schema(connection)
        singer_mids, album_mids = load_reference_sets(connection)
        artist_name_mid_map, ambiguous_artist_names = load_unique_artist_name_mid_map(connection)
        songs, song_singers, rejections = evaluate_rows(unique_rows, conflict_by_mid, singer_mids, album_mids, artist_name_mid_map)
        replace_songs(connection, songs, song_singers)
        db_song_rows = connection.execute("SELECT COUNT(*) FROM songs").fetchone()[0]
        db_song_singer_rows = connection.execute("SELECT COUNT(*) FROM song_singers").fetchone()[0]

    write_rejection_csv(config.rejection_csv, rejections)
    reason_counts: Counter[str] = Counter()
    for row in rejections:
        for reason in str(row["reason_flags"]).split(";"):
            if reason:
                reason_counts[reason] += 1
    return {
        "raw_rows": len(raw_rows),
        "target_singers": len(target_mids),
        "missing_song_mid_raw_rows": missing_mid_rows,
        "unique_song_mid_rows": len(unique_rows),
        "imported_songs": len(songs),
        "imported_song_singers": len(song_singers),
        "rejected_songs": len(rejections),
        "db_song_rows": db_song_rows,
        "db_song_singer_rows": db_song_singer_rows,
        "rejection_csv": config.rejection_csv.as_posix(),
        "rejection_reason_counts": dict(sorted(reason_counts.items())),
        "artist_name_mid_matches": len(artist_name_mid_map),
        "ambiguous_artist_names": ambiguous_artist_names,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import complete QQ Music song rows into SQLite and write rejected rows to CSV.")
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--rejection-csv", type=Path, default=DEFAULT_REJECTION_CSV)
    parser.add_argument("--singer-list-raw-dir", type=Path, default=DEFAULT_SINGER_LIST_RAW_DIR, help="Singer list raw directory used by step 3 and step 4 to define --all targets.")
    parser.add_argument("--qqmusic-raw-dir", type=Path, default=DEFAULT_QQMUSIC_RAW_DIR, help="QQ Music raw root used for step-4 target resolution.")
    parser.add_argument("--all", action="store_true", dest="all_available_song_tabs", help="Import only song-tab raw for singers selected by the current step-3 singer-list import rules.")
    parser.add_argument("--mvp", action="store_true", help="MVP mode: --all uses the first 10 area 0/1 singers and the MVP database by default.")
    parser.add_argument("--mid", action="append", help="Singer mid whose song-tab raw JSON should be imported. Can be repeated or comma-separated.")
    parser.add_argument("--name", action="append", help="Singer exact name whose song-tab raw JSON should be imported. Can be repeated or comma-separated.")
    return parser.parse_args()


def _main() -> None:
    ensure_utf8_stdout()
    args = parse_args()
    db_path = args.db if args.db is not None else (DEFAULT_MVP_DB_PATH if args.mvp else DEFAULT_DB_PATH)
    result = run(
        ImportConfig(
            raw_dir=args.raw_dir,
            db_path=db_path,
            rejection_csv=args.rejection_csv,
            singer_list_raw_dir=args.singer_list_raw_dir,
            qqmusic_raw_dir=args.qqmusic_raw_dir,
            all_available_song_tabs=args.all_available_song_tabs,
            mvp=args.mvp,
            mids=parse_csv_values(args.mid),
            names=parse_csv_values(args.name),
        )
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()

