from __future__ import annotations
import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from music_metadata_graph.run_log import run_with_log
from music_metadata_graph.pipelines.defaults import (
    DEFAULT_DB_PATH,
    DEFAULT_MVP_DB_PATH,
    MVP_SINGER_LIMIT,
)
from typing import Any

DEFAULT_RAW_DIR = Path("data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all")
DEFAULT_FANS_RAW_DIR = Path("data/raw/qqmusic")
FANS_SUMMARY_FILENAME = "singer_fans_summary.json"
MVP_FANS_SUMMARY_FILENAME = "singer_fans_summary_mvp.json"
ALLOWED_AREA_IDS = {0, 1}


@dataclass(frozen=True)
class ImportConfig:
    raw_dir: Path
    db_path: Path
    fans_raw_dir: Path = DEFAULT_FANS_RAW_DIR
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
    return [row for row in rows if parse_area_id(row.get("area_id")) in ALLOWED_AREA_IDS]


def parse_fans_num(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        fans_num = int(value)
    except (TypeError, ValueError):
        return None
    return fans_num if fans_num > 0 else None


def singer_fans_summary_path(raw_dir: Path, *, mvp: bool = False) -> Path:
    filename = MVP_FANS_SUMMARY_FILENAME if mvp else FANS_SUMMARY_FILENAME
    return raw_dir / filename


def load_fans_map(raw_dir: Path, *, mvp: bool = False) -> dict[str, dict[str, Any]]:
    summary_path = singer_fans_summary_path(raw_dir, mvp=mvp)
    if not summary_path.exists():
        return {}
    payload = load_json(summary_path)
    rows = payload.get("rows") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return {}
    fans: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        mid = str(row.get("mid") or "").strip()
        fans_num = parse_fans_num(row.get("fans_num"))
        if not mid or fans_num is None:
            continue
        fans[mid] = {
            "fans_num": fans_num,
            "fans_source": str(row.get("source") or ""),
            "fans_raw_json_path": str(row.get("raw_json_path") or ""),
        }
    return fans


def attach_fans(
    rows: list[dict[str, Any]], fans_map: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        mid = str(item.get("mid") or "").strip()
        fans = fans_map.get(mid)
        if fans is not None:
            item.update(fans)
        enriched.append(item)
    return enriched


def filter_singers_by_fans(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if parse_fans_num(row.get("fans_num")) is not None]


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_schema(connection: sqlite3.Connection) -> None:
    migrate_singers_to_artists(connection)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS artists (
            mid TEXT NOT NULL PRIMARY KEY,
            name TEXT NOT NULL,
            area_id INTEGER,
            fans_num INTEGER,
            fans_source TEXT NOT NULL DEFAULT '',
            fans_raw_json_path TEXT NOT NULL DEFAULT '',
            other_name TEXT NOT NULL DEFAULT '',
            icon TEXT NOT NULL DEFAULT '',
            spell TEXT NOT NULL DEFAULT '',
            raw_json_path TEXT NOT NULL DEFAULT '',
            raw_page INTEGER NOT NULL DEFAULT 0,
            raw_row_index INTEGER NOT NULL DEFAULT 0
        )
        """)
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
        "fans_num": "ALTER TABLE artists ADD COLUMN fans_num INTEGER",
        "fans_source": "ALTER TABLE artists ADD COLUMN fans_source TEXT NOT NULL DEFAULT ''",
        "fans_raw_json_path": "ALTER TABLE artists ADD COLUMN fans_raw_json_path TEXT NOT NULL DEFAULT ''",
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
    fans_num_expr = "fans_num" if "fans_num" in singer_columns else "NULL"
    fans_source_expr = "fans_source" if "fans_source" in singer_columns else "''"
    fans_raw_json_path_expr = (
        "fans_raw_json_path" if "fans_raw_json_path" in singer_columns else "''"
    )
    other_name_expr = "other_name" if "other_name" in singer_columns else "''"
    spell_expr = "spell" if "spell" in singer_columns else "''"
    raw_json_path_expr = "raw_json_path" if "raw_json_path" in singer_columns else "''"
    raw_page_expr = "raw_page" if "raw_page" in singer_columns else "0"
    raw_row_index_expr = "raw_row_index" if "raw_row_index" in singer_columns else "0"
    with connection:
        connection.execute("""
            CREATE TABLE artists (
                mid TEXT NOT NULL PRIMARY KEY,
                name TEXT NOT NULL,
                area_id INTEGER,
                fans_num INTEGER,
                fans_source TEXT NOT NULL DEFAULT '',
                fans_raw_json_path TEXT NOT NULL DEFAULT '',
                other_name TEXT NOT NULL DEFAULT '',
                icon TEXT NOT NULL DEFAULT '',
                spell TEXT NOT NULL DEFAULT '',
                raw_json_path TEXT NOT NULL DEFAULT '',
                raw_page INTEGER NOT NULL DEFAULT 0,
                raw_row_index INTEGER NOT NULL DEFAULT 0
            )
            """)
        connection.execute(f"""
            INSERT INTO artists (
                mid, name, area_id, other_name, icon, spell,
                fans_num, fans_source, fans_raw_json_path,
                raw_json_path, raw_page, raw_row_index
            )
            SELECT
                mid, name, {area_id_expr}, {other_name_expr}, {icon_expr}, {spell_expr},
                {fans_num_expr}, {fans_source_expr}, {fans_raw_json_path_expr},
                {raw_json_path_expr}, {raw_page_expr}, {raw_row_index_expr}
            FROM singers
            """)
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
    existing_columns = {
        row[1] for row in connection.execute("PRAGMA table_info(artists)").fetchall()
    }
    icon_expr = (
        "icon"
        if "icon" in existing_columns
        else ("singer_pic" if "singer_pic" in existing_columns else "''")
    )
    area_id_expr = "area_id" if "area_id" in existing_columns else "0"
    fans_num_expr = "fans_num" if "fans_num" in existing_columns else "NULL"
    fans_source_expr = "fans_source" if "fans_source" in existing_columns else "''"
    fans_raw_json_path_expr = (
        "fans_raw_json_path" if "fans_raw_json_path" in existing_columns else "''"
    )
    other_name_expr = "other_name" if "other_name" in existing_columns else "''"
    spell_expr = "spell" if "spell" in existing_columns else "''"
    raw_json_path_expr = "raw_json_path" if "raw_json_path" in existing_columns else "''"
    raw_page_expr = "raw_page" if "raw_page" in existing_columns else "0"
    raw_row_index_expr = "raw_row_index" if "raw_row_index" in existing_columns else "0"
    with connection:
        connection.execute("ALTER TABLE artists RENAME TO artists_old")
        connection.execute("""
            CREATE TABLE artists (
                mid TEXT NOT NULL PRIMARY KEY,
                name TEXT NOT NULL,
                area_id INTEGER,
                fans_num INTEGER,
                fans_source TEXT NOT NULL DEFAULT '',
                fans_raw_json_path TEXT NOT NULL DEFAULT '',
                other_name TEXT NOT NULL DEFAULT '',
                icon TEXT NOT NULL DEFAULT '',
                spell TEXT NOT NULL DEFAULT '',
                raw_json_path TEXT NOT NULL DEFAULT '',
                raw_page INTEGER NOT NULL DEFAULT 0,
                raw_row_index INTEGER NOT NULL DEFAULT 0
            )
            """)
        connection.execute(f"""
            INSERT INTO artists (
                mid, name, area_id, other_name, icon, spell,
                fans_num, fans_source, fans_raw_json_path,
                raw_json_path, raw_page, raw_row_index
            )
            SELECT
                mid, name, {area_id_expr}, {other_name_expr}, {icon_expr}, {spell_expr},
                {fans_num_expr}, {fans_source_expr}, {fans_raw_json_path_expr},
                {raw_json_path_expr}, {raw_page_expr}, {raw_row_index_expr}
            FROM artists_old
            """)
        connection.execute("DROP TABLE artists_old")


def import_artists(connection: sqlite3.Connection, rows: list[dict[str, Any]]) -> int:
    payload = [
        (
            str(row.get("mid") or ""),
            str(row.get("name") or ""),
            parse_area_id(row.get("area_id")),
            parse_fans_num(row.get("fans_num")),
            str(row.get("fans_source") or ""),
            str(row.get("fans_raw_json_path") or ""),
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
                mid, name, area_id, fans_num, fans_source, fans_raw_json_path, other_name, icon, spell,
                raw_json_path, raw_page, raw_row_index
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(mid) DO UPDATE SET
                name = excluded.name,
                area_id = COALESCE(excluded.area_id, artists.area_id),
                fans_num = COALESCE(excluded.fans_num, artists.fans_num),
                fans_source = CASE WHEN excluded.fans_source <> '' THEN excluded.fans_source ELSE artists.fans_source END,
                fans_raw_json_path = CASE WHEN excluded.fans_raw_json_path <> '' THEN excluded.fans_raw_json_path ELSE artists.fans_raw_json_path END,
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
    fans_map = load_fans_map(config.fans_raw_dir, mvp=config.mvp)
    area_rows = filter_singers_by_area(rows)
    area_rows = attach_fans(area_rows, fans_map)
    rows_with_fans = filter_singers_by_fans(area_rows)
    if config.mvp:
        filtered_rows = rows_with_fans[:MVP_SINGER_LIMIT]
    else:
        filtered_rows = rows_with_fans
    if area_rows and not rows_with_fans:
        raise ValueError(
            f"No area 0/1 singer rows have usable fans_num from {config.fans_raw_dir}."
        )
    validate_singers(filtered_rows)
    connection = connect(config.db_path)
    try:
        create_schema(connection)
        imported = import_artists(connection, filtered_rows)
        db_count = connection.execute("SELECT COUNT(*) FROM artists").fetchone()[0]
    finally:
        connection.close()
    return {
        "raw_rows": len(rows),
        "filtered_rows_by_area": len(area_rows),
        "filtered_rows": len(filtered_rows),
        "filtered_out_rows": len(rows) - len(filtered_rows),
        "filtered_out_missing_fans": len(area_rows) - len(rows_with_fans),
        "allowed_area_ids": sorted(ALLOWED_AREA_IDS),
        "mvp": config.mvp,
        "mvp_singer_limit": MVP_SINGER_LIMIT if config.mvp else None,
        "fans_raw_dir": config.fans_raw_dir.as_posix(),
        "fans_rows_available": len(fans_map),
        "filtered_rows_with_fans": sum(
            1 for row in filtered_rows if parse_fans_num(row.get("fans_num")) is not None
        ),
        "imported_rows": imported,
        "db_rows": db_count,
        "db_path": config.db_path.as_posix(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import raw QQ Music singer list JSON into SQLite."
    )
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--fans-raw-dir", type=Path, default=DEFAULT_FANS_RAW_DIR)
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument(
        "--mvp",
        action="store_true",
        help="MVP mode: import only the first 10 area 0/1 singers into the MVP database by default.",
    )
    return parser.parse_args()


def _main() -> None:
    ensure_utf8_stdout()
    args = parse_args()
    db_path = (
        args.db if args.db is not None else (DEFAULT_MVP_DB_PATH if args.mvp else DEFAULT_DB_PATH)
    )
    result = run(
        ImportConfig(
            raw_dir=args.raw_dir, db_path=db_path, fans_raw_dir=args.fans_raw_dir, mvp=args.mvp
        )
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()
