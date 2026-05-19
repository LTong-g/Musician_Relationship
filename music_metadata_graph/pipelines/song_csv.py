from __future__ import annotations
import csv
import json
import sqlite3
from pathlib import Path
from typing import Any
from pypinyin import Style, lazy_pinyin
from music_metadata_graph.progress import iter_progress

EXCEL_FORMULA_PREFIXES = ("=", "+", "-", "@")
EXCEL_IGNORED_PREFIX_CHARS = " \t\r\n"
BASE_SONG_CSV_FIELDS = [
    "song_mid",
    "song_id",
    "song_name",
    "song_title",
    "song_language",
    "album_name",
    "album_type",
    "album_publish_date",
    "singer_count",
    "singers_json",
]
SONG_REASON_CODE_FIELD = "reason_code"
CREDIT_SONG_CSV_FIELDS = [
    "song_mid",
    "song_id",
    "song_name",
    "song_title",
    "song_language",
    "album_name",
    "album_type",
    "album_publish_date",
    "作词",
    "作曲",
    "singer_count",
    "singers_json",
]


def song_name_pinyin_sort_key(row: dict[str, Any]) -> tuple[str, str, int, str]:
    name = str(row.get("song_name") or row.get("name") or "")
    initials = "".join(lazy_pinyin(name, style=Style.FIRST_LETTER)).casefold()
    pinyin = "".join(lazy_pinyin(name)).casefold()
    try:
        song_id = int(row.get("song_id") or row.get("id") or 0)
    except (TypeError, ValueError):
        song_id = 0
    song_mid = str(row.get("song_mid") or row.get("mid") or "")
    return initials, pinyin, song_id, song_mid


def sort_song_csv_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=song_name_pinyin_sort_key)


def escape_excel_formula_value(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    stripped = value.lstrip(EXCEL_IGNORED_PREFIX_CHARS)
    if stripped.startswith(EXCEL_FORMULA_PREFIXES):
        return "'" + value
    return value


def escape_excel_formula_row(row: dict[str, Any]) -> dict[str, Any]:
    return {key: escape_excel_formula_value(value) for key, value in row.items()}


def singer_rows_json(connection: sqlite3.Connection, song_mid: str) -> str:
    rows = connection.execute(
        """
        SELECT artists.mid AS mid, artists.name AS name
        FROM song_singers
        JOIN artists ON artists.mid = song_singers.singer_mid
        WHERE song_singers.song_mid = ?
        ORDER BY song_singers.singer_order
        """,
        (song_mid,),
    ).fetchall()
    payload = [{"mid": str(row["mid"]), "name": str(row["name"])} for row in rows]
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def credit_names(connection: sqlite3.Connection, song_mid: str, role: str) -> str:
    rows = connection.execute(
        """
        SELECT artists.name AS name
        FROM song_credit_artists
        JOIN artists ON artists.mid = song_credit_artists.artist_mid
        WHERE song_credit_artists.song_mid = ?
          AND song_credit_artists.role = ?
        ORDER BY song_credit_artists.artist_order
        """,
        (song_mid, role),
    ).fetchall()
    return " / ".join(str(row["name"]) for row in rows)


def prepare_song_csv_rows(
    connection: sqlite3.Connection,
    rows: list[dict[str, Any]],
    *,
    include_credits: bool,
    progress_label: str = "",
    progress_every: int = 50000,  # Kept for backward-compatible callers; tqdm progress uses timed log heartbeats.
) -> list[dict[str, Any]]:
    prepared: list[dict[str, Any]] = []
    total = len(rows)

    iterator = iter_progress(progress_label, rows, total=total) if progress_label else rows

    for source in iterator:
        row = dict(source)
        song_mid = str(row.get("song_mid") or "")
        row["singer_count"] = connection.execute(
            "SELECT COUNT(*) FROM song_singers WHERE song_mid = ?",
            (song_mid,),
        ).fetchone()[0]
        row["singers_json"] = singer_rows_json(connection, song_mid)
        if include_credits:
            row["作词"] = credit_names(connection, song_mid, "作词")
            row["作曲"] = credit_names(connection, song_mid, "作曲")
        prepared.append(row)
    return sort_song_csv_rows(prepared)


def write_song_csv(
    path: Path, rows: list[dict[str, Any]], *, include_credits: bool, include_reason: bool = False
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = CREDIT_SONG_CSV_FIELDS if include_credits else BASE_SONG_CSV_FIELDS
    if include_reason:
        fieldnames = [*fieldnames, SONG_REASON_CODE_FIELD]
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\r\n"
        )
        writer.writeheader()
        writer.writerows(escape_excel_formula_row(row) for row in sort_song_csv_rows(rows))
