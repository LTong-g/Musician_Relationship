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



from music_metadata_graph.pipelines.song_csv import CREDIT_SONG_CSV_FIELDS, prepare_song_csv_rows, write_song_csv





DEFAULT_REJECTION_CSV = Path("data/processed/validation/song_filtering/csv_views/songs_removed_by_step11_incomplete_credits.csv")

DEFAULT_TEMP_KEPT_CSV = Path("data/processed/validation/temp_song_filtering/csv_views/songs_after_step11_complete_credits.csv")

DEFAULT_TEMP_EXPORT_ARTIST_NAMES = ("周杰伦", "林俊杰", "薛之谦", "汪苏泷")

REQUIRED_CREDIT_ROLES = ("作词", "作曲")

SONG_CSV_FIELDS = CREDIT_SONG_CSV_FIELDS





@dataclass(frozen=True)

class FilterConfig:

    db_path: Path

    rejection_csv: Path

    temp_kept_csv: Path | None

    temp_export_artist_names: tuple[str, ...]





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

            albums.publishDate AS album_publish_date,

            (

                SELECT COUNT(*)

                FROM song_credit_artists

                WHERE song_credit_artists.song_mid = songs.mid

                  AND song_credit_artists.role = '作词'

            ) AS lyricist_count,

            (

                SELECT COUNT(*)

                FROM song_credit_artists

                WHERE song_credit_artists.song_mid = songs.mid

                  AND song_credit_artists.role = '作曲'

            ) AS composer_count

        FROM songs

        JOIN albums ON albums.mid = songs.album_mid

        {where_sql}

        ORDER BY songs.id, songs.mid

        """,

        params,

    ).fetchall()

    return [dict(row) for row in rows]





def fetch_incomplete_credit_rows(connection: sqlite3.Connection) -> list[dict[str, Any]]:

    return fetch_song_rows(

        connection,

        """

        WHERE NOT EXISTS (

            SELECT 1

            FROM song_credit_artists

            WHERE song_credit_artists.song_mid = songs.mid

              AND song_credit_artists.role = '作词'

        )

        OR NOT EXISTS (

            SELECT 1

            FROM song_credit_artists

            WHERE song_credit_artists.song_mid = songs.mid

              AND song_credit_artists.role = '作曲'

        )

        """,

    )





def prepare_csv_rows(connection: sqlite3.Connection, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:

    return prepare_song_csv_rows(connection, rows, include_credits=True)


def load_artist_song_mids(connection: sqlite3.Connection, artist_names: tuple[str, ...]) -> set[str]:

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





def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:

    write_song_csv(path, rows, include_credits=True)





def delete_songs(connection: sqlite3.Connection, song_mids: list[str]) -> None:

    if not song_mids:

        return

    connection.executemany("DELETE FROM songs WHERE mid = ?", [(mid,) for mid in song_mids])





def count_missing_reasons(rows: list[dict[str, Any]]) -> dict[str, int]:

    missing_lyricist = sum(1 for row in rows if int(row.get("lyricist_count") or 0) == 0)

    missing_composer = sum(1 for row in rows if int(row.get("composer_count") or 0) == 0)

    missing_both = sum(

        1

        for row in rows

        if int(row.get("lyricist_count") or 0) == 0 and int(row.get("composer_count") or 0) == 0

    )

    return {

        "missing_lyricist": missing_lyricist,

        "missing_composer": missing_composer,

        "missing_both": missing_both,

    }





def run(config: FilterConfig) -> dict[str, Any]:

    with connect(config.db_path) as connection:

        before_count = connection.execute("SELECT COUNT(*) FROM songs").fetchone()[0]

        removed_rows = fetch_incomplete_credit_rows(connection)

        reason_counts = count_missing_reasons(removed_rows)

        removed_mids = sorted({str(row["song_mid"]) for row in removed_rows})



        write_csv(config.rejection_csv, prepare_csv_rows(connection, removed_rows))

        exported_temp_kept_rows = 0

        if config.temp_kept_csv is not None:

            removed_mid_set = set(removed_mids)

            temp_export_song_mids = load_artist_song_mids(connection, config.temp_export_artist_names)

            kept_rows = [

                row

                for row in fetch_song_rows(connection)

                if str(row["song_mid"]) not in removed_mid_set

                and (not config.temp_export_artist_names or str(row["song_mid"]) in temp_export_song_mids)

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

        "required_credit_roles": list(REQUIRED_CREDIT_ROLES),

        "songs_before": before_count,

        "removed_by_incomplete_credits": len(removed_mids),

        "missing_reason_counts": reason_counts,

        "songs_after_step11": after_count,

        "song_singer_rows_after_step11": song_singer_rows,

        "song_credit_rows_after_step11": song_credit_rows,

        "rejection_csv": config.rejection_csv.as_posix(),

        "temp_kept_csv": config.temp_kept_csv.as_posix() if config.temp_kept_csv is not None else "",

        "temp_export_artist_names": list(config.temp_export_artist_names),

        "exported_temp_kept_rows": exported_temp_kept_rows,

    }





def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(description="Step 11: remove songs without both lyricist and composer credits.")

    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

    parser.add_argument("--rejection-csv", type=Path, default=DEFAULT_REJECTION_CSV)

    parser.add_argument("--temp-kept-csv", type=Path, default=DEFAULT_TEMP_KEPT_CSV)

    parser.add_argument("--no-temp-kept-csv", action="store_true", help="Do not write the temporary kept-song CSV view.")

    parser.add_argument(

        "--temp-export-artist-name",

        action="append",

        default=None,

        help="Singer name to include in the temporary kept-song CSV. Can be passed multiple times.",

    )

    parser.add_argument("--all-temp-kept-csv", action="store_true", help="Export all kept songs to the temporary kept-song CSV.")

    return parser.parse_args()





def _main() -> None:

    ensure_utf8_stdout()

    args = parse_args()

    if args.all_temp_kept_csv:

        temp_export_artist_names: tuple[str, ...] = ()

    elif args.temp_export_artist_name is not None:

        temp_export_artist_names = tuple(args.temp_export_artist_name)

    else:

        temp_export_artist_names = DEFAULT_TEMP_EXPORT_ARTIST_NAMES

    result = run(

        FilterConfig(

            db_path=args.db,

            rejection_csv=args.rejection_csv,

            temp_kept_csv=None if args.no_temp_kept_csv else args.temp_kept_csv,

            temp_export_artist_names=temp_export_artist_names,

        )

    )

    print(json.dumps(result, ensure_ascii=False, indent=2))





def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":

    main()


