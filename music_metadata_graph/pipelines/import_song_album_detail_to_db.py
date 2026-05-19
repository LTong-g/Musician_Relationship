from __future__ import annotations
import argparse
import csv
import json
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from music_metadata_graph.run_log import run_with_log
from music_metadata_graph.pipelines.defaults import DEFAULT_DB_PATH
from music_metadata_graph.progress import iter_progress
from typing import Any
from music_metadata_graph.pipelines.song_csv import escape_excel_formula_row

DEFAULT_RAW_DIR = Path("data/raw/qqmusic/song_album_detail")

DEFAULT_REJECTION_CSV = Path(
    "data/processed/validation/album_import_rejections/csv_views/album_import_rejections.csv"
)
PROGRESS_EVERY = 1000

ALBUM_REJECTION_CSV_FIELDS = [
    "album_mid",
    "album_id",
    "album_name",
    "album_type",
    "album_publish_date",
    "raw_json_path",
    "raw_page",
    "raw_row_index",
    "reason_code",
]


@dataclass(frozen=True)
class ImportConfig:
    raw_dir: Path

    db_path: Path

    rejection_csv: Path


def ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_albums(raw_dir: Path) -> list[dict[str, Any]]:
    files = sorted(raw_dir.glob("*.json"))

    if not files:
        raise FileNotFoundError(f"No song-derived album detail JSON files found: {raw_dir}")

    rows: list[dict[str, Any]] = []

    total = len(files)

    for path in iter_progress("加载专辑详情 raw", files, total=total):
        payload = load_json(path)

        basic_info = payload.get("basicInfo") if isinstance(payload.get("basicInfo"), dict) else {}

        rows.append(
            {
                "mid": basic_info.get("albumMid"),
                "id": basic_info.get("albumID"),
                "name": basic_info.get("albumName"),
                "albumType": basic_info.get("albumType"),
                "publishDate": basic_info.get("publishDate") or "",
                "raw_json_path": path.as_posix(),
                "raw_page": 0,
                "raw_row_index": 1,
            }
        )
    return rows


def split_valid_and_rejected_albums(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    required_fields = ("mid", "id", "name", "albumType", "publishDate")

    accepted: list[dict[str, Any]] = []

    rejected: list[dict[str, Any]] = []

    for row in rows:
        reasons = [f"missing_{field}" for field in required_fields if row.get(field) in (None, "")]

        if reasons:
            rejected.append(build_rejection_row(row, reasons))

            continue

        accepted.append(row)

    validate_unique_albums(accepted)

    return accepted, rejected


def validate_unique_albums(rows: list[dict[str, Any]]) -> None:
    if not rows:
        return

    mids = [str(row["mid"]) for row in rows]

    ids = [int(row["id"]) for row in rows]

    duplicate_mids = len(mids) - len(set(mids))

    duplicate_ids = len(ids) - len(set(ids))

    if duplicate_mids:
        raise ValueError(f"{duplicate_mids} duplicate album mid values found.")

    if duplicate_ids:
        raise ValueError(f"{duplicate_ids} duplicate album id values found.")


def build_rejection_row(row: dict[str, Any], reasons: list[str]) -> dict[str, Any]:
    reason_code = ";".join(sorted(set(reasons)))

    return {
        "album_mid": row.get("mid") or "",
        "album_id": row.get("id") if row.get("id") is not None else "",
        "album_name": row.get("name") or "",
        "album_type": row.get("albumType") or "",
        "album_publish_date": row.get("publishDate") or "",
        "reason_flags": reason_code,
        "raw_json_path": row.get("raw_json_path") or "",
        "raw_page": row.get("raw_page") if row.get("raw_page") is not None else "",
        "raw_row_index": row.get("raw_row_index") if row.get("raw_row_index") is not None else "",
        "reason_code": reason_code,
    }


def write_rejection_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=ALBUM_REJECTION_CSV_FIELDS,
            extrasaction="ignore",
            lineterminator="\r\n",
        )

        writer.writeheader()

        writer.writerows(escape_excel_formula_row(row) for row in rows)


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_schema(connection: sqlite3.Connection) -> None:
    connection.execute("""

        CREATE TABLE IF NOT EXISTS albums (

            mid TEXT PRIMARY KEY,

            id INTEGER NOT NULL UNIQUE,

            name TEXT NOT NULL,

            albumType TEXT NOT NULL,

            publishDate TEXT NOT NULL,

            raw_json_path TEXT NOT NULL DEFAULT '',

            raw_page INTEGER NOT NULL DEFAULT 0,

            raw_row_index INTEGER NOT NULL DEFAULT 0
        )

        """)


def replace_albums(connection: sqlite3.Connection, rows: list[dict[str, Any]]) -> int:
    payload = [
        (
            str(row["mid"]),
            int(row["id"]),
            str(row["name"]),
            str(row["albumType"]),
            str(row["publishDate"]),
            str(row["raw_json_path"]),
            int(row["raw_page"]),
            int(row["raw_row_index"]),
        )
        for row in rows
    ]

    with connection:
        clear_downstream_tables(connection)

        connection.execute("DELETE FROM albums")

        connection.executemany(
            """

            INSERT INTO albums (

                mid, id, name, albumType, publishDate,

                raw_json_path, raw_page, raw_row_index
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)

            """,
            payload,
        )

    return len(payload)


def clear_downstream_tables(connection: sqlite3.Connection) -> None:
    for table in ("song_credit_artists", "song_singers", "songs"):
        exists = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table,),
        ).fetchone()

        if exists:
            connection.execute(f"DELETE FROM {table}")


def run(config: ImportConfig) -> dict[str, Any]:
    rows = load_albums(config.raw_dir)
    print(
        json.dumps({"stage": "split_albums", "raw_rows": len(rows)}, ensure_ascii=False), flush=True
    )

    accepted_rows, rejected_rows = split_valid_and_rejected_albums(rows)
    print(
        json.dumps(
            {
                "stage": "replace_albums",
                "accepted_rows": len(accepted_rows),
                "rejected_rows": len(rejected_rows),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    with connect(config.db_path) as connection:
        create_schema(connection)

        imported = replace_albums(connection, accepted_rows)

        db_count = connection.execute("SELECT COUNT(*) FROM albums").fetchone()[0]

        downstream_counts = {
            table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ("songs", "song_singers", "song_credit_artists")
            if connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)
            ).fetchone()
        }

    print(
        json.dumps(
            {
                "stage": "write_album_rejection_csv",
                "rows": len(rejected_rows),
                "csv": config.rejection_csv.as_posix(),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    write_rejection_csv(config.rejection_csv, rejected_rows)

    return {
        "raw_rows": len(rows),
        "accepted_rows": len(accepted_rows),
        "rejected_rows": len(rejected_rows),
        "imported_rows": imported,
        "db_rows": db_count,
        "cleared_downstream_tables": downstream_counts,
        "db_path": config.db_path.as_posix(),
        "rejection_csv": config.rejection_csv.as_posix(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import raw QQ Music album detail JSON into SQLite."
    )

    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)

    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

    parser.add_argument("--rejection-csv", type=Path, default=DEFAULT_REJECTION_CSV)

    return parser.parse_args()


def _main() -> None:
    ensure_utf8_stdout()

    args = parse_args()

    result = run(
        ImportConfig(raw_dir=args.raw_dir, db_path=args.db, rejection_csv=args.rejection_csv)
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()
