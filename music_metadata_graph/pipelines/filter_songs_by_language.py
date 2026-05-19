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
from music_metadata_graph.pipelines.song_csv import (
    CREDIT_SONG_CSV_FIELDS,
    prepare_song_csv_rows,
    write_song_csv,
)

REMOVED_LANGUAGE = 9
DEFAULT_REJECTION_CSV = Path(
    "data/processed/validation/song_filtering/csv_views/songs_removed_by_manual_language_9.csv"
)
DEFAULT_TEMP_KEPT_CSV = Path(
    "data/processed/validation/temp_song_filtering/csv_views/songs_after_manual_language_filter.csv"
)
DEFAULT_FOUR_SINGER_TEMP_KEPT_CSV = Path(
    "data/processed/validation/temp_song_filtering/csv_views/songs_after_manual_language_filter_四位歌手.csv"
)
DEFAULT_TEMP_EXPORT_ARTIST_NAMES = ("周杰伦", "林俊杰", "薛之谦", "汪苏泷")
SONG_CSV_FIELDS = CREDIT_SONG_CSV_FIELDS


@dataclass(frozen=True)
class FilterConfig:
    db_path: Path
    rejection_csv: Path
    temp_kept_csv: Path | None
    four_singer_temp_kept_csv: Path | None
    removed_language: int
    temp_export_artist_names: tuple[str, ...]


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


def fetch_song_rows(
    connection: sqlite3.Connection, where_sql: str = "", params: tuple[Any, ...] = ()
) -> list[dict[str, Any]]:
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


def prepare_csv_rows(
    connection: sqlite3.Connection, rows: list[dict[str, Any]], progress_label: str = ""
) -> list[dict[str, Any]]:
    return prepare_song_csv_rows(
        connection, rows, include_credits=True, progress_label=progress_label
    )


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    write_song_csv(path, rows, include_credits=True)


def write_rejection_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    write_song_csv(path, rows, include_credits=True, include_reason=True)


def load_artist_song_mids(
    connection: sqlite3.Connection, artist_names: tuple[str, ...]
) -> set[str]:
    if not artist_names:
        return set()
    placeholders = ", ".join("?" for _ in artist_names)
    rows = connection.execute(
        f"""
        SELECT DISTINCT song_singers.song_mid
        FROM song_singers
        JOIN artists ON artists.mid = song_singers.singer_mid
        WHERE artists.name IN ({placeholders})
        """,
        artist_names,
    ).fetchall()
    return {str(row["song_mid"]) for row in rows}


def delete_songs(connection: sqlite3.Connection, song_mids: list[str]) -> None:
    if not song_mids:
        return
    connection.executemany("DELETE FROM songs WHERE mid = ?", [(mid,) for mid in song_mids])


def run(config: FilterConfig) -> dict[str, Any]:
    with connect(config.db_path) as connection:
        before_count = connection.execute("SELECT COUNT(*) FROM songs").fetchone()[0]
        print(
            json.dumps(
                {
                    "stage": "fetch_language_removed_rows",
                    "songs_before": before_count,
                    "removed_language": config.removed_language,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        removed_rows = fetch_song_rows(
            connection,
            "WHERE songs.language = ?",
            (config.removed_language,),
        )
        removed_rows = [
            {**row, "reason_code": f"language_{config.removed_language}"} for row in removed_rows
        ]
        removed_mids = sorted({str(row["song_mid"]) for row in removed_rows})

        print(
            json.dumps(
                {
                    "stage": "write_language_rejection_csv",
                    "rows": len(removed_rows),
                    "csv": config.rejection_csv.as_posix(),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        write_rejection_csv(
            config.rejection_csv,
            prepare_csv_rows(connection, removed_rows, "prepare_language_rejection_csv"),
        )

        exported_temp_kept_rows = 0
        exported_four_singer_temp_kept_rows = 0
        if config.temp_kept_csv is not None or config.four_singer_temp_kept_csv is not None:
            removed_mid_set = set(removed_mids)
            kept_rows = [
                row
                for row in fetch_song_rows(connection)
                if str(row["song_mid"]) not in removed_mid_set
            ]
            if config.temp_kept_csv is not None:
                print(
                    json.dumps(
                        {
                            "stage": "write_language_temp_csv",
                            "rows": len(kept_rows),
                            "csv": config.temp_kept_csv.as_posix(),
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
                write_csv(
                    config.temp_kept_csv,
                    prepare_csv_rows(connection, kept_rows, "prepare_language_temp_csv"),
                )
                exported_temp_kept_rows = len(kept_rows)
            if config.four_singer_temp_kept_csv is not None:
                temp_export_song_mids = load_artist_song_mids(
                    connection, config.temp_export_artist_names
                )
                four_singer_kept_rows = [
                    row for row in kept_rows if str(row["song_mid"]) in temp_export_song_mids
                ]
                print(
                    json.dumps(
                        {
                            "stage": "write_language_four_singer_temp_csv",
                            "rows": len(four_singer_kept_rows),
                            "csv": config.four_singer_temp_kept_csv.as_posix(),
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
                write_csv(
                    config.four_singer_temp_kept_csv,
                    prepare_csv_rows(
                        connection, four_singer_kept_rows, "prepare_language_four_singer_temp_csv"
                    ),
                )
                exported_four_singer_temp_kept_rows = len(four_singer_kept_rows)

        with connection:
            print(
                json.dumps(
                    {"stage": "delete_language_removed_songs", "rows": len(removed_mids)},
                    ensure_ascii=False,
                ),
                flush=True,
            )
            delete_songs(connection, removed_mids)
            after_count = connection.execute("SELECT COUNT(*) FROM songs").fetchone()[0]

        song_singer_rows = connection.execute("SELECT COUNT(*) FROM song_singers").fetchone()[0]
        song_credit_rows = connection.execute(
            "SELECT COUNT(*) FROM song_credit_artists"
        ).fetchone()[0]

    return {
        "db_path": config.db_path.as_posix(),
        "removed_language": config.removed_language,
        "songs_before": before_count,
        "removed_by_language": len(removed_mids),
        "songs_after_manual_language_filter": after_count,
        "song_singer_rows_after_manual_language_filter": song_singer_rows,
        "song_credit_rows_after_manual_language_filter": song_credit_rows,
        "rejection_csv": config.rejection_csv.as_posix(),
        "temp_kept_csv": (
            config.temp_kept_csv.as_posix() if config.temp_kept_csv is not None else ""
        ),
        "four_singer_temp_kept_csv": (
            config.four_singer_temp_kept_csv.as_posix()
            if config.four_singer_temp_kept_csv is not None
            else ""
        ),
        "temp_export_artist_names": list(config.temp_export_artist_names),
        "exported_temp_kept_rows": exported_temp_kept_rows,
        "exported_four_singer_temp_kept_rows": exported_four_singer_temp_kept_rows,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manual maintenance: remove songs whose language equals 9."
    )
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--rejection-csv", type=Path, default=None)
    parser.add_argument("--temp-kept-csv", type=Path, default=None)
    parser.add_argument(
        "--no-temp-kept-csv",
        action="store_true",
        help="Do not write the temporary kept-song CSV view.",
    )
    parser.add_argument("--four-singer-temp-kept-csv", type=Path, default=None)
    parser.add_argument(
        "--no-four-singer-temp-kept-csv",
        action="store_true",
        help="Do not write the temporary four-singer kept-song CSV view.",
    )
    parser.add_argument(
        "--temp-export-artist-name",
        action="append",
        default=None,
        help="Singer name to include in the temporary four-singer kept-song CSV. Can be passed multiple times.",
    )
    parser.add_argument("--removed-language", type=int, default=REMOVED_LANGUAGE)
    parser.add_argument(
        "--mvp",
        action="store_true",
        help="Use the MVP database and MVP validation outputs by default.",
    )
    return parser.parse_args()


def _main() -> None:
    ensure_utf8_stdout()
    args = parse_args()
    db_path = (
        args.db if args.db is not None else (DEFAULT_MVP_DB_PATH if args.mvp else DEFAULT_DB_PATH)
    )
    rejection_csv = args.rejection_csv or (
        mvp_output_path(DEFAULT_REJECTION_CSV) if args.mvp else DEFAULT_REJECTION_CSV
    )
    temp_kept_csv = args.temp_kept_csv or (
        mvp_output_path(DEFAULT_TEMP_KEPT_CSV) if args.mvp else DEFAULT_TEMP_KEPT_CSV
    )
    four_singer_temp_kept_csv = args.four_singer_temp_kept_csv or (
        mvp_output_path(DEFAULT_FOUR_SINGER_TEMP_KEPT_CSV)
        if args.mvp
        else DEFAULT_FOUR_SINGER_TEMP_KEPT_CSV
    )
    result = run(
        FilterConfig(
            db_path=db_path,
            rejection_csv=rejection_csv,
            temp_kept_csv=None if args.no_temp_kept_csv else temp_kept_csv,
            four_singer_temp_kept_csv=(
                None if args.no_four_singer_temp_kept_csv else four_singer_temp_kept_csv
            ),
            removed_language=args.removed_language,
            temp_export_artist_names=(
                tuple(args.temp_export_artist_name)
                if args.temp_export_artist_name is not None
                else DEFAULT_TEMP_EXPORT_ARTIST_NAMES
            ),
        )
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()
