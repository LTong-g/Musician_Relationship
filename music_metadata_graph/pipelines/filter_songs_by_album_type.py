from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

from music_metadata_graph.run_log import run_with_log
from music_metadata_graph.pipelines.defaults import DEFAULT_DB_PATH
from typing import Any

from music_metadata_graph.pipelines.song_csv import BASE_SONG_CSV_FIELDS, prepare_song_csv_rows, write_song_csv


DEFAULT_REJECTION_CSV = Path("data/processed/validation/song_filtering/csv_views/songs_removed_by_step8_album_type.csv")
ALLOWED_ALBUM_TYPES = ("Single", "EP", "录音室专辑")
SONG_CSV_FIELDS = BASE_SONG_CSV_FIELDS


@dataclass(frozen=True)
class FilterConfig:
    db_path: Path
    rejection_csv: Path


def ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def connect(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise FileNotFoundError(f"Database does not exist: {db_path}")
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def fetch_removed_rows(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    placeholders = ", ".join("?" for _ in ALLOWED_ALBUM_TYPES)
    rows = connection.execute(
        f"""
        SELECT
            songs.mid AS song_mid,
            songs.id AS song_id,
            songs.name AS song_name,
            songs.title AS song_title,
            songs.language AS song_language,
            albums.name AS album_name,
            albums.albumType AS album_type,
            albums.publishDate AS album_publish_date
        FROM songs
        JOIN albums ON albums.mid = songs.album_mid
        WHERE albums.albumType NOT IN ({placeholders})
        ORDER BY songs.id, songs.mid
        """,
        ALLOWED_ALBUM_TYPES,
    ).fetchall()
    return prepare_song_csv_rows(connection, [dict(row) for row in rows], include_credits=False)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    write_song_csv(path, rows, include_credits=False)


def run(config: FilterConfig) -> dict[str, Any]:
    with connect(config.db_path) as connection:
        before_count = connection.execute("SELECT COUNT(*) FROM songs").fetchone()[0]
        removed_rows = fetch_removed_rows(connection)
        write_csv(config.rejection_csv, removed_rows)
        with connection:
            connection.executemany("DELETE FROM songs WHERE mid = ?", [(row["song_mid"],) for row in removed_rows])
        after_count = connection.execute("SELECT COUNT(*) FROM songs").fetchone()[0]
        song_singer_rows = connection.execute("SELECT COUNT(*) FROM song_singers").fetchone()[0]
    return {
        "db_path": config.db_path.as_posix(),
        "songs_before": before_count,
        "removed_by_album_type": len(removed_rows),
        "songs_after": after_count,
        "song_singer_rows_after": song_singer_rows,
        "rejection_csv": config.rejection_csv.as_posix(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Step 8: keep only Single, EP, and 录音室专辑 songs.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--rejection-csv", type=Path, default=DEFAULT_REJECTION_CSV)
    return parser.parse_args()


def _main() -> None:
    ensure_utf8_stdout()
    args = parse_args()
    print(json.dumps(run(FilterConfig(db_path=args.db, rejection_csv=args.rejection_csv)), ensure_ascii=False, indent=2))


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()

