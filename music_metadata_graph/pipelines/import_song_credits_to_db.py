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
from music_metadata_graph.pipelines.import_singer_list_to_db import (
    create_schema as create_artist_schema,
)
from music_metadata_graph.pipelines.import_singer_list_to_db import import_artists
from music_metadata_graph.pipelines.collect_song_lyric_credit_raw import (
    load_or_migrate_lyric_credit_evidence,
    missing_credit_roles_from_producer,
    parse_lyric_credit_rows,
)

from music_metadata_graph.pipelines.quick_search_artist_mid import (
    has_artist_name_separator,
    split_artist_names,
)
from music_metadata_graph.progress import iter_progress
from music_metadata_graph.pipelines.song_csv import prepare_song_csv_rows, write_song_csv

DEFAULT_RAW_DIR = Path("data/raw/qqmusic/song_producer")
DEFAULT_LYRIC_RAW_DIR = Path("data/raw/qqmusic/song_lyric_credit")

DEFAULT_TEMP_SONGS_CSV = Path(
    "data/processed/validation/temp_song_filtering/csv_views/songs_after_step14_credit_import.csv"
)
DEFAULT_FOUR_SINGER_TEMP_SONGS_CSV = Path(
    "data/processed/validation/temp_song_filtering/csv_views/songs_after_step14_credit_import_四位歌手.csv"
)
CREDIT_TITLES = ("作词", "作曲")
DEFAULT_TEMP_EXPORT_ARTIST_NAMES = ("周杰伦", "林俊杰", "薛之谦", "汪苏泷")
PROGRESS_EVERY = 1000


@dataclass(frozen=True)
class ImportConfig:
    raw_dir: Path
    lyric_raw_dir: Path

    db_path: Path

    temp_songs_csv: Path | None
    four_singer_temp_songs_csv: Path | None

    artist_mid: str | None
    artist_name: str | None
    temp_export_artist_names: tuple[str, ...]


def ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def connect(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise FileNotFoundError(f"Database does not exist: {db_path}")

    connection = sqlite3.connect(db_path)

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def producer_groups(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if not isinstance(payload, dict):
        return []

    for key in ("Lst", "data", "producer", "producers", "list", "items"):
        value = payload.get(key)

        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]

        if isinstance(value, dict):
            nested = producer_groups(value)

            if nested:
                return nested

    return []


def create_credit_schema(connection: sqlite3.Connection) -> None:
    connection.execute("""

        CREATE TABLE IF NOT EXISTS song_credit_artists (

            song_mid TEXT NOT NULL,

            role TEXT NOT NULL,

            artist_order INTEGER NOT NULL,

            artist_mid TEXT NOT NULL,

            raw_json_path TEXT NOT NULL DEFAULT '',

            raw_page INTEGER NOT NULL DEFAULT 0,

            raw_row_index INTEGER NOT NULL DEFAULT 0,

            PRIMARY KEY(song_mid, role, artist_order),

            FOREIGN KEY(song_mid) REFERENCES songs(mid) ON DELETE CASCADE,

            FOREIGN KEY(artist_mid) REFERENCES artists(mid)
        )

        """)


def load_valid_song_mids(connection: sqlite3.Connection, config: ImportConfig) -> set[str]:
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

    return {
        str(row["mid"])
        for row in connection.execute(f"SELECT mid FROM songs {where_sql}", params).fetchall()
    }


def load_unique_artist_name_map(
    connection: sqlite3.Connection,
) -> tuple[dict[str, dict[str, Any]], int]:
    rows = connection.execute("""
        SELECT mid, name, icon, raw_json_path, raw_page, raw_row_index
        FROM artists
        WHERE name <> ''
        ORDER BY rowid
        """).fetchall()
    rows_by_name: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        name = str(row["name"] or "").strip()
        mid = str(row["mid"] or "").strip()
        if name and mid:
            rows_by_name.setdefault(name, []).append(dict(row))
    unique_map = {
        name: rows[0]
        for name, rows in rows_by_name.items()
        if len({str(row["mid"]) for row in rows}) == 1
    }
    ambiguous_names = sum(
        1 for rows in rows_by_name.values() if len({str(row["mid"]) for row in rows}) > 1
    )
    return unique_map, ambiguous_names


def resolve_missing_artist_name_rows(
    name: str, artist_name_map: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    source_name = name.strip()
    if not source_name:
        return []
    search_names = (
        split_artist_names(source_name)
        if has_artist_name_separator(source_name)
        else (source_name,)
    )
    resolved: list[dict[str, Any]] = []
    seen: set[str] = set()
    for search_name in search_names:
        artist = artist_name_map.get(search_name)
        if artist is None:
            continue
        mid = str(artist["mid"])
        if mid in seen:
            continue
        seen.add(mid)
        resolved.append(artist)
    return resolved


def load_credit_rows(
    connection: sqlite3.Connection, config: ImportConfig
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    valid_song_mids = load_valid_song_mids(connection, config)
    artist_name_map, _ = load_unique_artist_name_map(connection)
    artist_rows: dict[str, dict[str, Any]] = {}
    credit_rows: list[dict[str, Any]] = []
    next_order_by_song_role: dict[tuple[str, str], int] = {}

    files = sorted(config.raw_dir.glob("*.json"))

    total = len(files)

    for path in iter_progress("扫描制作人 raw 并生成作词作曲关系", files, total=total):
        song_mid = path.stem

        if song_mid not in valid_song_mids:
            continue

        payload = load_json(path)
        missing_roles = missing_credit_roles_from_producer(payload)

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

            for order, producer in enumerate(producers, 1):
                if not isinstance(producer, dict):
                    continue

                name = str(producer.get("name") or producer.get("Name") or "").strip()
                artist_mid = str(
                    producer.get("singer_mid") or producer.get("SingerMid") or ""
                ).strip()
                resolved_artists: list[dict[str, Any]] = []
                if artist_mid:
                    resolved_artists.append(
                        {
                            "mid": artist_mid,
                            "name": name,
                            "icon": str(producer.get("icon") or producer.get("Icon") or ""),
                            "raw_json_path": path.as_posix(),
                            "raw_page": 0,
                            "raw_row_index": order,
                            "_from_raw_mid": True,
                        }
                    )
                else:
                    resolved_artists.extend(resolve_missing_artist_name_rows(name, artist_name_map))
                if not resolved_artists or not name:
                    continue
                for artist in resolved_artists:
                    resolved_mid = str(artist["mid"])
                    if artist.get("_from_raw_mid"):
                        artist_rows.setdefault(
                            resolved_mid,
                            {
                                "mid": resolved_mid,
                                "name": name,
                                "other_name": "",
                                "icon": str(artist.get("icon") or ""),
                                "spell": "",
                                "raw_json_path": path.as_posix(),
                                "raw_page": 0,
                                "raw_row_index": order,
                            },
                        )

                    order_key = (song_mid, role)
                    next_order_by_song_role[order_key] = (
                        next_order_by_song_role.get(order_key, 0) + 1
                    )
                    credit_rows.append(
                        {
                            "song_mid": song_mid,
                            "role": role,
                            "artist_order": next_order_by_song_role[order_key],
                            "artist_mid": resolved_mid,
                            "raw_json_path": path.as_posix(),
                            "raw_page": 0,
                            "raw_row_index": order,
                        }
                    )
        if missing_roles:
            lyric_path = config.lyric_raw_dir / f"{song_mid}.json"
            if lyric_path.exists():
                lyric_payload = load_or_migrate_lyric_credit_evidence(
                    lyric_path,
                    target={
                        "song_mid": song_mid,
                        "missing_roles": sorted(missing_roles),
                    },
                ).payload
                for lyric_row in parse_lyric_credit_rows(lyric_payload, raw_path=lyric_path):
                    role = str(lyric_row.get("role") or "")
                    name = str(lyric_row.get("name") or "").strip()
                    if role not in missing_roles or not name:
                        continue
                    resolved_artists = resolve_missing_artist_name_rows(name, artist_name_map)
                    if not resolved_artists:
                        continue
                    for artist in resolved_artists:
                        resolved_mid = str(artist["mid"])
                        order_key = (song_mid, role)
                        next_order_by_song_role[order_key] = (
                            next_order_by_song_role.get(order_key, 0) + 1
                        )
                        credit_rows.append(
                            {
                                "song_mid": song_mid,
                                "role": role,
                                "artist_order": next_order_by_song_role[order_key],
                                "artist_mid": resolved_mid,
                                "raw_json_path": lyric_path.as_posix(),
                                "raw_page": 0,
                                "raw_row_index": int(lyric_row.get("raw_row_index") or 0),
                            }
                        )
    return list(artist_rows.values()), credit_rows


def replace_credits(connection: sqlite3.Connection, credit_rows: list[dict[str, Any]]) -> None:
    with connection:
        connection.execute("DELETE FROM song_credit_artists")

        connection.executemany(
            """

            INSERT INTO song_credit_artists (

                song_mid, role, artist_order, artist_mid,

                raw_json_path, raw_page, raw_row_index
            )

            VALUES (?, ?, ?, ?, ?, ?, ?)

            """,
            [
                (
                    row["song_mid"],
                    row["role"],
                    row["artist_order"],
                    row["artist_mid"],
                    row["raw_json_path"],
                    row["raw_page"],
                    row["raw_row_index"],
                )
                for row in credit_rows
            ],
        )


def fetch_song_csv_rows(
    connection: sqlite3.Connection,
    config: ImportConfig,
    *,
    export_artist_names: tuple[str, ...] = (),
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

    elif export_artist_names:
        placeholders = ", ".join("?" for _ in export_artist_names)

        where_sql = (
            "WHERE EXISTS ("
            "SELECT 1 FROM song_singers "
            "JOIN artists ON artists.mid = song_singers.singer_mid "
            f"WHERE song_singers.song_mid = songs.mid AND artists.name IN ({placeholders})"
            ")"
        )

        params.extend(export_artist_names)

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


def run(config: ImportConfig) -> dict[str, Any]:
    with connect(config.db_path) as connection:
        create_artist_schema(connection)

        create_credit_schema(connection)

        target_song_count = len(load_valid_song_mids(connection, config))
        artist_name_map, ambiguous_artist_names = load_unique_artist_name_map(connection)

        artist_rows, credit_rows = load_credit_rows(connection, config)
        print(
            json.dumps(
                {
                    "stage": "import_credit_artists",
                    "raw_artist_rows": len(artist_rows),
                    "credit_rows": len(credit_rows),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

        imported_artists = import_artists(connection, artist_rows) if artist_rows else 0

        print(
            json.dumps(
                {"stage": "replace_song_credits", "credit_rows": len(credit_rows)},
                ensure_ascii=False,
            ),
            flush=True,
        )
        replace_credits(connection, credit_rows)

        exported_temp_song_rows = 0
        exported_four_singer_temp_song_rows = 0

        if config.temp_songs_csv is not None:
            temp_rows = prepare_song_csv_rows(
                connection,
                fetch_song_csv_rows(connection, config),
                include_credits=True,
                progress_label="prepare_credit_import_temp_csv",
            )

            print(
                json.dumps(
                    {
                        "stage": "write_temp_songs_csv",
                        "rows": len(temp_rows),
                        "csv": config.temp_songs_csv.as_posix(),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
            write_song_csv(config.temp_songs_csv, temp_rows, include_credits=True)

            exported_temp_song_rows = len(temp_rows)

        if config.four_singer_temp_songs_csv is not None:
            four_singer_temp_rows = prepare_song_csv_rows(
                connection,
                fetch_song_csv_rows(
                    connection, config, export_artist_names=config.temp_export_artist_names
                ),
                include_credits=True,
                progress_label="prepare_credit_import_four_singer_temp_csv",
            )

            print(
                json.dumps(
                    {
                        "stage": "write_four_singer_temp_songs_csv",
                        "rows": len(four_singer_temp_rows),
                        "csv": config.four_singer_temp_songs_csv.as_posix(),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
            write_song_csv(
                config.four_singer_temp_songs_csv, four_singer_temp_rows, include_credits=True
            )

            exported_four_singer_temp_song_rows = len(four_singer_temp_rows)

        db_artists = connection.execute("SELECT COUNT(*) FROM artists").fetchone()[0]

        db_credits = connection.execute("SELECT COUNT(*) FROM song_credit_artists").fetchone()[0]

    return {
        "raw_dir": config.raw_dir.as_posix(),
        "lyric_raw_dir": config.lyric_raw_dir.as_posix(),
        "artist_mid": config.artist_mid or "",
        "artist_name": config.artist_name or "",
        "target_songs": target_song_count,
        "credit_artists_in_raw": len(artist_rows),
        "imported_or_updated_artists": imported_artists,
        "credit_rows": len(credit_rows),
        "temp_songs_csv": (
            config.temp_songs_csv.as_posix() if config.temp_songs_csv is not None else ""
        ),
        "four_singer_temp_songs_csv": (
            config.four_singer_temp_songs_csv.as_posix()
            if config.four_singer_temp_songs_csv is not None
            else ""
        ),
        "temp_export_artist_names": (
            list(config.temp_export_artist_names)
            if not config.artist_mid and not config.artist_name
            else []
        ),
        "exported_temp_song_rows": exported_temp_song_rows,
        "exported_four_singer_temp_song_rows": exported_four_singer_temp_song_rows,
        "db_artists": db_artists,
        "db_song_credit_artists": db_credits,
        "artist_name_mid_matches": len(artist_name_map),
        "ambiguous_artist_names": ambiguous_artist_names,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import lyricist/composer credits from QQ Music producer raw JSON."
    )

    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--lyric-raw-dir", type=Path, default=DEFAULT_LYRIC_RAW_DIR)

    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

    parser.add_argument("--temp-songs-csv", type=Path, default=DEFAULT_TEMP_SONGS_CSV)
    parser.add_argument(
        "--no-temp-songs-csv",
        action="store_true",
        help="Do not write the temporary song CSV after importing credits.",
    )
    parser.add_argument(
        "--four-singer-temp-songs-csv", type=Path, default=DEFAULT_FOUR_SINGER_TEMP_SONGS_CSV
    )
    parser.add_argument(
        "--no-four-singer-temp-songs-csv",
        action="store_true",
        help="Do not write the temporary four-singer song CSV after importing credits.",
    )

    parser.add_argument(
        "--artist-mid",
        default=None,
        help="Only import credits for songs whose singer list contains this artist mid.",
    )

    parser.add_argument(
        "--artist-name",
        default=None,
        help="Only import credits for songs whose singer list contains this exact artist name.",
    )

    parser.add_argument(
        "--temp-export-artist-name",
        action="append",
        default=None,
        help="Singer name to include in the temporary song CSV when no --artist-mid/--artist-name import filter is set. Can be passed multiple times.",
    )

    parser.add_argument(
        "--all-temp-songs-csv",
        action="store_true",
        help="Export all current songs to the temporary song CSV.",
    )

    return parser.parse_args()


def _main() -> None:
    ensure_utf8_stdout()

    args = parse_args()

    if args.temp_export_artist_name is not None:
        temp_export_artist_names = tuple(args.temp_export_artist_name)

    else:
        temp_export_artist_names = DEFAULT_TEMP_EXPORT_ARTIST_NAMES

    print(
        json.dumps(
            run(
                ImportConfig(
                    raw_dir=args.raw_dir,
                    lyric_raw_dir=args.lyric_raw_dir,
                    db_path=args.db,
                    temp_songs_csv=None if args.no_temp_songs_csv else args.temp_songs_csv,
                    four_singer_temp_songs_csv=(
                        None
                        if args.no_four_singer_temp_songs_csv
                        else args.four_singer_temp_songs_csv
                    ),
                    artist_mid=args.artist_mid,
                    artist_name=args.artist_name,
                    temp_export_artist_names=temp_export_artist_names,
                )
            ),
            ensure_ascii=False,
            indent=2,
        )
    )


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()
