from __future__ import annotations

import argparse
import asyncio
import json
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

from music_metadata_graph.run_log import run_with_log
from music_metadata_graph.pipelines.defaults import DEFAULT_DB_PATH
from typing import Any

from music_metadata_graph.pipelines.collect_song_producer_raw import CREDIT_TITLES, producer_groups
from music_metadata_graph.pipelines.import_singer_list_to_db import create_schema as create_artist_schema
from music_metadata_graph.pipelines.quick_search_artist_mid import MissingArtistName, fill_missing_artist_mids


DEFAULT_RAW_DIR = Path("data/raw/qqmusic")
DEFAULT_CSV = Path("data/processed/validation/song_credit_mid_fill/csv_views/song_credit_mid_fill.csv")


@dataclass(frozen=True)
class FillConfig:
    raw_dir: Path
    db_path: Path
    csv_path: Path
    force: bool
    max_names: int | None
    artist_mid: str | None
    artist_name: str | None


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


def load_target_song_mids(connection: sqlite3.Connection, config: FillConfig) -> set[str]:
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
    return {str(row["mid"]) for row in connection.execute(f"SELECT mid FROM songs {where_sql}", params).fetchall()}


def load_song_names(connection: sqlite3.Connection) -> dict[str, tuple[str, str]]:
    rows = connection.execute("SELECT mid, id, name FROM songs").fetchall()
    return {str(row["mid"]): (str(row["id"]), str(row["name"])) for row in rows}


def collect_missing_credit_sources(connection: sqlite3.Connection, config: FillConfig) -> list[MissingArtistName]:
    producer_raw_dir = config.raw_dir / "song_producer"
    target_song_mids = load_target_song_mids(connection, config)
    song_names = load_song_names(connection)
    sources: list[MissingArtistName] = []
    for path in sorted(producer_raw_dir.glob("*.json")):
        song_mid = path.stem
        if song_mid not in target_song_mids:
            continue
        payload = load_json(path)
        song_id, song_name = song_names.get(song_mid, ("", ""))
        for group in producer_groups(payload):
            role = str(group.get("title") or group.get("Title") or "")
            if role not in CREDIT_TITLES:
                continue
            producer_list = group.get("producers") if isinstance(group.get("producers"), list) else group.get("Producers")
            producers = producer_list if isinstance(producer_list, list) else []
            for order, producer in enumerate(producers, 1):
                if not isinstance(producer, dict):
                    continue
                artist_mid = str(producer.get("singer_mid") or producer.get("SingerMid") or "").strip()
                producer_name = str(producer.get("name") or producer.get("Name") or "").strip()
                if artist_mid or not producer_name:
                    continue
                sources.append(
                    MissingArtistName(
                        source_step="step10_song_credit",
                        source_role=role,
                        source_name=producer_name,
                        source_song_mid=song_mid,
                        source_song_id=song_id,
                        source_song_name=song_name,
                        source_raw_json_path=path.as_posix(),
                        source_raw_page=0,
                        source_raw_row_index=order,
                    )
                )
    return sources


async def run(config: FillConfig) -> dict[str, Any]:
    with connect(config.db_path) as connection:
        sources = collect_missing_credit_sources(connection, config)
        if config.max_names is not None:
            seen: set[str] = set()
            limited: list[MissingArtistName] = []
            for source in sources:
                if source.source_name in seen:
                    limited.append(source)
                    continue
                if len(seen) >= config.max_names:
                    continue
                seen.add(source.source_name)
                limited.append(source)
            sources = limited

        create_artist_schema(connection)
        result = await fill_missing_artist_mids(
            connection,
            sources,
            raw_dir=config.raw_dir / "quick_search_artist_mid" / "song_credit",
            csv_path=config.csv_path,
            force=config.force,
        )
        result["db_artists"] = connection.execute("SELECT COUNT(*) FROM artists").fetchone()[0]
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fill missing lyricist/composer mids by QQ Music quick_search exact artist matches.")
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--force", action="store_true", help="Refetch and overwrite quick_search raw JSON.")
    parser.add_argument("--max-names", type=int, default=None, help="Limit unique missing names for smoke tests.")
    parser.add_argument("--artist-mid", default=None, help="Only scan songs whose singer list contains this artist mid.")
    parser.add_argument("--artist-name", default=None, help="Only scan songs whose singer list contains this exact artist name.")
    return parser.parse_args()


def _main() -> None:
    ensure_utf8_stdout()
    args = parse_args()
    result = asyncio.run(
        run(
            FillConfig(
                raw_dir=args.raw_dir,
                db_path=args.db,
                csv_path=args.csv,
                force=args.force,
                max_names=args.max_names,
                artist_mid=args.artist_mid,
                artist_name=args.artist_name,
            )
        )
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()

