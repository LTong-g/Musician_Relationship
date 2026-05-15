from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from music_metadata_graph.run_log import run_with_log
from music_metadata_graph.pipelines.defaults import DEFAULT_DB_PATH, DEFAULT_MVP_DB_PATH
from music_metadata_graph.pipelines.song_csv import CREDIT_SONG_CSV_FIELDS, prepare_song_csv_rows, write_song_csv


REMOVED_LANGUAGE = 9
DEFAULT_REJECTION_CSV = Path("data/processed/validation/song_filtering/csv_views/songs_removed_by_step13_language_9.csv")
DEFAULT_TEMP_KEPT_CSV = Path("data/processed/validation/temp_song_filtering/csv_views/songs_after_step13_language_filter.csv")
SONG_CSV_FIELDS = CREDIT_SONG_CSV_FIELDS


@dataclass(frozen=True)
class FilterConfig:
    db_path: Path
    rejection_csv: Path
    temp_kept_csv: Path | None
    removed_language: int


def ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def mvp_output_path(path: Path) -> Path:
    parts = path.parts
    try:
        index = parts.index("validation")
    except ValueError:
        return path
    return Path(*parts[:index], "validation_mvp", *parts[index + 1 :])


def connect(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise FileNotFoundError(f"Database does not exist: {db_path}")
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def fetch_song_rows(connection: sqlite3.Connection, where_sql: str = "", params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
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
        {where_sql}
        ORDER BY songs.id, songs.mid
        """,
        params,
    ).fetchall()
    return [dict(row) for row in rows]


def prepare_csv_rows(connection: sqlite3.Connection, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return prepare_song_csv_rows(connection, rows, include_credits=True)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    write_song_csv(path, rows, include_credits=True)


def delete_songs(connection: sqlite3.Connection, song_mids: list[str]) -> None:
    if not song_mids:
        return
    connection.executemany("DELETE FROM songs WHERE mid = ?", [(mid,) for mid in song_mids])


def run(config: FilterConfig) -> dict[str, Any]:
    with connect(config.db_path) as connection:
        before_count = connection.execute("SELECT COUNT(*) FROM songs").fetchone()[0]
        removed_rows = fetch_song_rows(
            connection,
            "WHERE songs.language = ?",
            (config.removed_language,),
        )
        removed_mids = sorted({str(row["song_mid"]) for row in removed_rows})

        write_csv(config.rejection_csv, prepare_csv_rows(connection, removed_rows))

        exported_temp_kept_rows = 0
        if config.temp_kept_csv is not None:
            removed_mid_set = set(removed_mids)
            kept_rows = [
                row
                for row in fetch_song_rows(connection)
                if str(row["song_mid"]) not in removed_mid_set
            ]
            write_csv(config.temp_kept_csv, prepare_csv_rows(connection, kept_rows))
            exported_temp_kept_rows = len(kept_rows)

        with connection:
            delete_songs(connection, removed_mids)
            after_count = connection.execute("SELECT COUNT(*) FROM songs").fetchone()[0]

        song_singer_rows = connection.execute("SELECT COUNT(*) FROM song_singers").fetchone()[0]
        song_credit_rows = connection.execute("SELECT COUNT(*) FROM song_credit_artists").fetchone()[0]

    return {
        "db_path": config.db_path.as_posix(),
        "removed_language": config.removed_language,
        "songs_before": before_count,
        "removed_by_language": len(removed_mids),
        "songs_after_step13": after_count,
        "song_singer_rows_after_step13": song_singer_rows,
        "song_credit_rows_after_step13": song_credit_rows,
        "rejection_csv": config.rejection_csv.as_posix(),
        "temp_kept_csv": config.temp_kept_csv.as_posix() if config.temp_kept_csv is not None else "",
        "exported_temp_kept_rows": exported_temp_kept_rows,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Step 13: remove songs whose language equals 9.")
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--rejection-csv", type=Path, default=None)
    parser.add_argument("--temp-kept-csv", type=Path, default=None)
    parser.add_argument("--no-temp-kept-csv", action="store_true", help="Do not write the temporary kept-song CSV view.")
    parser.add_argument("--removed-language", type=int, default=REMOVED_LANGUAGE)
    parser.add_argument("--mvp", action="store_true", help="Use the MVP database and MVP validation outputs by default.")
    return parser.parse_args()


def _main() -> None:
    ensure_utf8_stdout()
    args = parse_args()
    db_path = args.db if args.db is not None else (DEFAULT_MVP_DB_PATH if args.mvp else DEFAULT_DB_PATH)
    rejection_csv = args.rejection_csv or (mvp_output_path(DEFAULT_REJECTION_CSV) if args.mvp else DEFAULT_REJECTION_CSV)
    temp_kept_csv = args.temp_kept_csv or (mvp_output_path(DEFAULT_TEMP_KEPT_CSV) if args.mvp else DEFAULT_TEMP_KEPT_CSV)
    result = run(
        FilterConfig(
            db_path=db_path,
            rejection_csv=rejection_csv,
            temp_kept_csv=None if args.no_temp_kept_csv else temp_kept_csv,
            removed_language=args.removed_language,
        )
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()
