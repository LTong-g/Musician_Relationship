from __future__ import annotations

import argparse
import asyncio
import json
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

from music_metadata_graph.run_log import run_with_log
from music_metadata_graph.pipelines.defaults import DEFAULT_DB_PATH, DEFAULT_MVP_DB_PATH
from typing import Any

from music_metadata_graph.pipelines.collect_singer_song_tab_raw import CollectConfig as SongTabCollectConfig
from music_metadata_graph.pipelines.collect_singer_song_tab_raw import DEFAULT_PAGE_SIZE as SONG_TAB_PAGE_SIZE
from music_metadata_graph.pipelines.collect_singer_song_tab_raw import DEFAULT_SINGER_LIST_RAW_DIR
from music_metadata_graph.pipelines.collect_singer_song_tab_raw import parse_csv_values, resolve_targets
from music_metadata_graph.pipelines.import_singer_list_to_db import create_schema as create_artist_schema
from music_metadata_graph.pipelines.import_singer_song_tab_to_db import parse_page
from music_metadata_graph.pipelines.quick_search_artist_mid import MissingArtistName, fill_missing_artist_mids


DEFAULT_RAW_DIR = Path("data/raw/qqmusic")
DEFAULT_CSV = Path("data/processed/validation/song_singer_mid_fill/csv_views/song_singer_mid_fill.csv")


@dataclass(frozen=True)
class FillConfig:
    raw_dir: Path
    db_path: Path
    csv_path: Path
    singer_list_raw_dir: Path
    force: bool
    all_available_song_tabs: bool
    mvp: bool
    mids: tuple[str, ...]
    names: tuple[str, ...]
    max_names: int | None


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


def collect_missing_song_singer_sources(config: FillConfig) -> list[MissingArtistName]:
    collect_config = SongTabCollectConfig(
        raw_dir=config.raw_dir,
        db_path=config.db_path,
        page_size=SONG_TAB_PAGE_SIZE,
        singer_list_raw_dir=config.singer_list_raw_dir,
        max_pages_per_singer=None,
        force=config.force,
        all_singers=config.all_available_song_tabs,
        mvp=config.mvp,
        mids=config.mids,
        names=config.names,
    )
    sources: list[MissingArtistName] = []
    for target in resolve_targets(collect_config):
        source_dir = config.raw_dir / "singer_homepage_song_tab" / target.mid
        for path in sorted(source_dir.glob("page_*_size_*.json")):
            payload = load_json(path)
            page = parse_page(path)
            for index, song in enumerate(((payload.get("SongTab") or {}).get("List") or []), 1):
                singers = song.get("singer") if isinstance(song.get("singer"), list) else []
                for singer in singers:
                    if not isinstance(singer, dict):
                        continue
                    singer_mid = str(singer.get("mid") or "").strip()
                    singer_name = str(singer.get("name") or "").strip()
                    if singer_mid or not singer_name:
                        continue
                    sources.append(
                        MissingArtistName(
                            source_step="step4_song_singer",
                            source_role="演唱",
                            source_name=singer_name,
                            source_song_mid=str(song.get("mid") or ""),
                            source_song_id=str(song.get("id") or ""),
                            source_song_name=str(song.get("name") or song.get("title") or ""),
                            source_raw_json_path=path.as_posix(),
                            source_raw_page=page,
                            source_raw_row_index=index,
                        )
                    )
    return sources


async def run(config: FillConfig) -> dict[str, Any]:
    sources = collect_missing_song_singer_sources(config)
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

    with connect(config.db_path) as connection:
        create_artist_schema(connection)
        result = await fill_missing_artist_mids(
            connection,
            sources,
            raw_dir=config.raw_dir / "quick_search_artist_mid" / "song_singer",
            csv_path=config.csv_path,
            force=config.force,
        )
        result["db_artists"] = connection.execute("SELECT COUNT(*) FROM artists").fetchone()[0]
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fill missing song singer mids by QQ Music quick_search exact artist matches.")
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--singer-list-raw-dir", type=Path, default=DEFAULT_SINGER_LIST_RAW_DIR, help="Singer list raw directory used by step 3 and step 4 to define --all targets.")
    parser.add_argument("--force", action="store_true", help="Refetch and overwrite quick_search raw JSON.")
    parser.add_argument("--all", action="store_true", dest="all_available_song_tabs", help="Scan song-tab raw only for singers selected by the current step-3 singer-list import rules.")
    parser.add_argument("--mvp", action="store_true", help="MVP mode: --all uses the first 10 area 0/1 singers and the MVP database by default.")
    parser.add_argument("--mid", action="append", help="Singer mid whose song-tab raw JSON should be scanned. Can be repeated or comma-separated.")
    parser.add_argument("--name", action="append", help="Singer exact name whose song-tab raw JSON should be scanned. Can be repeated or comma-separated.")
    parser.add_argument("--max-names", type=int, default=None, help="Limit unique missing names for smoke tests.")
    return parser.parse_args()


def _main() -> None:
    ensure_utf8_stdout()
    args = parse_args()
    db_path = args.db if args.db is not None else (DEFAULT_MVP_DB_PATH if args.mvp else DEFAULT_DB_PATH)
    result = asyncio.run(
        run(
            FillConfig(
                raw_dir=args.raw_dir,
                db_path=db_path,
                csv_path=args.csv,
                singer_list_raw_dir=args.singer_list_raw_dir,
                force=args.force,
                all_available_song_tabs=args.all_available_song_tabs,
                mvp=args.mvp,
                mids=parse_csv_values(args.mid),
                names=parse_csv_values(args.name),
                max_names=args.max_names,
            )
        )
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()

