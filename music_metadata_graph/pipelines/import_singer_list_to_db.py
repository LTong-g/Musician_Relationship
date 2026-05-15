from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

from music_metadata_graph.run_log import run_with_log
from music_metadata_graph.pipelines.defaults import DEFAULT_DB_PATH, DEFAULT_MVP_DB_PATH, MVP_SINGER_LIMIT
from typing import Any


DEFAULT_RAW_DIR = Path("data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all")
ALLOWED_AREA_IDS = {0, 1}


@dataclass(frozen=True)
class ImportConfig:
    raw_dir: Path
    db_path: Path
    mvp: bool = False


def ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_singers(raw_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    files = sorted(raw_dir.glob("page_*_size_80.json"))
    if not files:
        raise FileNotFoundError(f"No singer list JSON files found: {raw_dir}")
    for path in files:
        payload = load_json(path)
        page = path.stem.split("_")[1] if "_" in path.stem else ""
        for index, singer in enumerate(payload.get("singerlist") or [], 1):
            row = dict(singer)
            row["raw_json_path"] = path.as_posix()
            row["raw_page"] = int(page) if page.isdigit() else None
            row["raw_row_index"] = index
            rows.append(row)
    return rows


def validate_singers(rows: list[dict[str, Any]]) -> None:
    missing_mid = [row for row in rows if not str(row.get("mid") or "").strip()]
    missing_name = [row for row in rows if not str(row.get("name") or "").strip()]
    if missing_mid:
        raise ValueError(f"{len(missing_mid)} singer rows are missing mid.")
    if missing_name:
        raise ValueError(f"{len(missing_name)} singer rows are missing name.")
    mids = [str(row.get("mid")) for row in rows]
    duplicate_mids = len(mids) - len(set(mids))
    if duplicate_mids:
        raise ValueError(f"{duplicate_mids} duplicate singer mid values found.")


def parse_area_id(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def filter_singers_by_area(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if parse_area_id(row.get("area_id")) in ALLOWED_AREA_IDS
    ]


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_schema(connection: sqlite3.Connection) -> None:
    migrate_singers_to_artists(connection)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS artists (
            mid TEXT NOT NULL PRIMARY KEY,
            name TEXT NOT NULL,
            area_id INTEGER,
            other_name TEXT NOT NULL DEFAULT '',
            icon TEXT NOT NULL DEFAULT '',
            spell TEXT NOT NULL DEFAULT '',
            raw_json_path TEXT NOT NULL DEFAULT '',
            raw_page INTEGER NOT NULL DEFAULT 0,
            raw_row_index INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    existing_columns = {
        row[1] for row in connection.execute("PRAGMA table_info(artists)").fetchall()
    }
    if should_rebuild_artists(connection, existing_columns):
        rebuild_artists_schema(connection)
        existing_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(artists)").fetchall()
        }
    migrations = {
        "area_id": "ALTER TABLE artists ADD COLUMN area_id INTEGER",
        "raw_json_path": "ALTER TABLE artists ADD COLUMN raw_json_path TEXT NOT NULL DEFAULT ''",
        "raw_page": "ALTER TABLE artists ADD COLUMN raw_page INTEGER NOT NULL DEFAULT 0",
        "raw_row_index": "ALTER TABLE artists ADD COLUMN raw_row_index INTEGER NOT NULL DEFAULT 0",
    }
    for column, statement in migrations.items():
        if column not in existing_columns:
            connection.execute(statement)


def migrate_singers_to_artists(connection: sqlite3.Connection) -> None:
    singers_exists = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'singers'"
    ).fetchone()
    artists_exists = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'artists'"
    ).fetchone()
    if not singers_exists or artists_exists:
        return
    singer_columns = {row[1] for row in connection.execute("PRAGMA table_info(singers)").fetchall()}
    icon_expr = "singer_pic" if "singer_pic" in singer_columns else "''"
    area_id_expr = "area_id" if "area_id" in singer_columns else "0"
    other_name_expr = "other_name" if "other_name" in singer_columns else "''"
    spell_expr = "spell" if "spell" in singer_columns else "''"
    raw_json_path_expr = "raw_json_path" if "raw_json_path" in singer_columns else "''"
    raw_page_expr = "raw_page" if "raw_page" in singer_columns else "0"
    raw_row_index_expr = "raw_row_index" if "raw_row_index" in singer_columns else "0"
    with connection:
        connection.execute(
            """
            CREATE TABLE artists (
                mid TEXT NOT NULL PRIMARY KEY,
                name TEXT NOT NULL,
                area_id INTEGER,
                other_name TEXT NOT NULL DEFAULT '',
                icon TEXT NOT NULL DEFAULT '',
                spell TEXT NOT NULL DEFAULT '',
                raw_json_path TEXT NOT NULL DEFAULT '',
                raw_page INTEGER NOT NULL DEFAULT 0,
                raw_row_index INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        connection.execute(
            f"""
            INSERT INTO artists (
                mid, name, area_id, other_name, icon, spell,
                raw_json_path, raw_page, raw_row_index
            )
            SELECT
                mid, name, {area_id_expr}, {other_name_expr}, {icon_expr}, {spell_expr},
                {raw_json_path_expr}, {raw_page_expr}, {raw_row_index_expr}
            FROM singers
            """
        )
        try:
            connection.execute("DROP TABLE singers")
        except sqlite3.DatabaseError:
            # Legacy song_singers may still reference singers. The song import
            # step rebuilds that table against artists and then removes singers.
            pass


def should_rebuild_artists(connection: sqlite3.Connection, existing_columns: set[str]) -> bool:
    if {"id", "pmid", "singer_pic"} & existing_columns:
        return True
    table_info = connection.execute("PRAGMA table_info(artists)").fetchall()
    columns = {row[1]: row for row in table_info}
    if columns.get("area_id") and int(columns["area_id"][3]):
        return True
    return bool(columns.get("mid") and not int(columns["mid"][3]))


def rebuild_artists_schema(connection: sqlite3.Connection) -> None:
    existing_columns = {row[1] for row in connection.execute("PRAGMA table_info(artists)").fetchall()}
    icon_expr = "icon" if "icon" in existing_columns else ("singer_pic" if "singer_pic" in existing_columns else "''")
    area_id_expr = "area_id" if "area_id" in existing_columns else "0"
    other_name_expr = "other_name" if "other_name" in existing_columns else "''"
    spell_expr = "spell" if "spell" in existing_columns else "''"
    raw_json_path_expr = "raw_json_path" if "raw_json_path" in existing_columns else "''"
    raw_page_expr = "raw_page" if "raw_page" in existing_columns else "0"
    raw_row_index_expr = "raw_row_index" if "raw_row_index" in existing_columns else "0"
    with connection:
        connection.execute("ALTER TABLE artists RENAME TO artists_old")
        connection.execute(
            """
            CREATE TABLE artists (
                mid TEXT NOT NULL PRIMARY KEY,
                name TEXT NOT NULL,
                area_id INTEGER,
                other_name TEXT NOT NULL DEFAULT '',
                icon TEXT NOT NULL DEFAULT '',
                spell TEXT NOT NULL DEFAULT '',
                raw_json_path TEXT NOT NULL DEFAULT '',
                raw_page INTEGER NOT NULL DEFAULT 0,
                raw_row_index INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        connection.execute(
            f"""
            INSERT INTO artists (
                mid, name, area_id, other_name, icon, spell,
                raw_json_path, raw_page, raw_row_index
            )
            SELECT
                mid, name, {area_id_expr}, {other_name_expr}, {icon_expr}, {spell_expr},
                {raw_json_path_expr}, {raw_page_expr}, {raw_row_index_expr}
            FROM artists_old
            """
        )
        connection.execute("DROP TABLE artists_old")


def import_artists(connection: sqlite3.Connection, rows: list[dict[str, Any]]) -> int:
    payload = [
        (
            str(row.get("mid") or ""),
            str(row.get("name") or ""),
            parse_area_id(row.get("area_id")),
            str(row.get("other_name") or ""),
            str(row.get("icon") or row.get("singer_pic") or ""),
            str(row.get("spell") or ""),
            str(row.get("raw_json_path") or ""),
            int(row.get("raw_page") or 0),
            int(row.get("raw_row_index") or 0),
        )
        for row in rows
    ]
    with connection:
        connection.executemany(
            """
            INSERT INTO artists (
                mid, name, area_id, other_name, icon, spell,
                raw_json_path, raw_page, raw_row_index
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(mid) DO UPDATE SET
                name = excluded.name,
                area_id = COALESCE(excluded.area_id, artists.area_id),
                other_name = excluded.other_name,
                icon = excluded.icon,
                spell = excluded.spell,
                raw_json_path = excluded.raw_json_path,
                raw_page = excluded.raw_page,
                raw_row_index = excluded.raw_row_index
            """,
            payload,
        )
    return len(payload)


import_singers = import_artists


def run(config: ImportConfig) -> dict[str, Any]:
    rows = load_singers(config.raw_dir)
    filtered_rows = filter_singers_by_area(rows)
    if config.mvp:
        filtered_rows = filtered_rows[:MVP_SINGER_LIMIT]
    validate_singers(filtered_rows)
    with connect(config.db_path) as connection:
        create_schema(connection)
        imported = import_artists(connection, filtered_rows)
        db_count = connection.execute("SELECT COUNT(*) FROM artists").fetchone()[0]
    return {
        "raw_rows": len(rows),
        "filtered_rows": len(filtered_rows),
        "filtered_out_rows": len(rows) - len(filtered_rows),
        "allowed_area_ids": sorted(ALLOWED_AREA_IDS),
        "mvp": config.mvp,
        "mvp_singer_limit": MVP_SINGER_LIMIT if config.mvp else None,
        "imported_rows": imported,
        "db_rows": db_count,
        "db_path": config.db_path.as_posix(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import raw QQ Music singer list JSON into SQLite.")
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--mvp", action="store_true", help="MVP mode: import only the first 10 area 0/1 singers into the MVP database by default.")
    return parser.parse_args()


def _main() -> None:
    ensure_utf8_stdout()
    args = parse_args()
    db_path = args.db if args.db is not None else (DEFAULT_MVP_DB_PATH if args.mvp else DEFAULT_DB_PATH)
    result = run(ImportConfig(raw_dir=args.raw_dir, db_path=db_path, mvp=args.mvp))
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()

