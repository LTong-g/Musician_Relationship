from __future__ import annotations
import argparse
import asyncio
import json
import sqlite3
import sys
from dataclasses import dataclass
from dataclasses import replace as dataclass_replace
from pathlib import Path
from music_metadata_graph.run_log import run_with_log
from music_metadata_graph.pipelines.defaults import (
    DEFAULT_DB_PATH,
    DEFAULT_MVP_DB_PATH,
    MVP_SINGER_LIMIT,
)
from typing import Any
from qqmusic_api import Client
from qqmusic_api.modules.singer import TabType
from music_metadata_graph.pipelines.import_singer_list_to_db import (
    DEFAULT_RAW_DIR as DEFAULT_SINGER_LIST_RAW_DIR,
)
from music_metadata_graph.pipelines.import_singer_list_to_db import attach_fans
from music_metadata_graph.pipelines.import_singer_list_to_db import filter_singers_by_area
from music_metadata_graph.pipelines.import_singer_list_to_db import filter_singers_by_fans
from music_metadata_graph.pipelines.import_singer_list_to_db import load_fans_map
from music_metadata_graph.pipelines.import_singer_list_to_db import load_singers

DEFAULT_RAW_DIR = Path("data/raw/qqmusic")
DEFAULT_PAGE_SIZE = 30
REQUEST_RATE = 0.5
REQUEST_CAPACITY = 1
TARGET_CONCURRENCY = 10


@dataclass(frozen=True)
class SingerTarget:
    mid: str
    name: str


@dataclass(frozen=True)
class CollectConfig:
    raw_dir: Path
    db_path: Path
    page_size: int
    singer_list_raw_dir: Path
    max_pages_per_singer: int | None
    force: bool
    all_singers: bool
    mvp: bool
    mids: tuple[str, ...]
    names: tuple[str, ...]


def ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def try_load_cached_json(path: Path) -> Any | None:
    try:
        return load_json(path)
    except (OSError, json.JSONDecodeError):
        return None


def connect(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise FileNotFoundError(f"Database does not exist: {db_path}")
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def parse_csv_values(values: list[str] | None) -> tuple[str, ...]:
    if not values:
        return ()
    parsed: list[str] = []
    for value in values:
        parsed.extend(part.strip() for part in value.split(",") if part.strip())
    return tuple(parsed)


def unique_targets(rows: list[sqlite3.Row]) -> tuple[SingerTarget, ...]:
    targets: list[SingerTarget] = []
    seen: set[str] = set()
    for row in rows:
        mid = str(row["mid"])
        if mid in seen:
            continue
        seen.add(mid)
        targets.append(SingerTarget(mid=mid, name=str(row["name"])))
    return tuple(targets)


def load_all_targets(
    connection: sqlite3.Connection, config: CollectConfig
) -> tuple[SingerTarget, ...]:
    third_step_rows = filter_singers_by_area(load_singers(config.singer_list_raw_dir))
    third_step_rows = attach_fans(third_step_rows, load_fans_map(config.raw_dir, mvp=config.mvp))
    third_step_rows = filter_singers_by_fans(third_step_rows)
    if config.mvp:
        third_step_rows = third_step_rows[:MVP_SINGER_LIMIT]
    if not third_step_rows:
        raise ValueError(
            f"No third-step singer rows found in raw JSON: {config.singer_list_raw_dir}"
        )
    db_rows = {
        str(row["mid"]): row
        for row in connection.execute("SELECT mid, name FROM artists ORDER BY rowid").fetchall()
    }
    targets: list[SingerTarget] = []
    missing_mids: list[str] = []
    seen: set[str] = set()
    for row in third_step_rows:
        mid = str(row.get("mid") or "").strip()
        if not mid or mid in seen:
            continue
        seen.add(mid)
        db_row = db_rows.get(mid)
        if db_row is None:
            missing_mids.append(mid)
            continue
        targets.append(SingerTarget(mid=mid, name=str(db_row["name"])))
    if missing_mids:
        raise ValueError(
            "Third-step singer targets are missing from artists. "
            "Run import_singer_list_to_db before collecting song tabs. "
            f"Missing mids: {', '.join(missing_mids[:20])}"
        )
    if not targets:
        raise ValueError("No third-step singer targets found in artists.")
    return tuple(targets)


def load_partial_targets(
    connection: sqlite3.Connection, config: CollectConfig
) -> tuple[SingerTarget, ...]:
    requested_count = len(config.mids) + len(config.names)
    if requested_count == 0:
        raise ValueError("Provide --all, or at least one --mid or --name.")
    rows: list[sqlite3.Row] = []
    missing: list[str] = []
    for mid in config.mids:
        row = connection.execute("SELECT mid, name FROM artists WHERE mid = ?", (mid,)).fetchone()
        if row is None:
            missing.append(f"mid:{mid}")
        else:
            rows.append(row)
    for name in config.names:
        matched = connection.execute(
            "SELECT mid, name FROM artists WHERE name = ? ORDER BY rowid", (name,)
        ).fetchall()
        if not matched:
            missing.append(f"name:{name}")
        elif len(matched) > 1:
            choices = ", ".join(f"{row['name']}({row['mid']})" for row in matched[:10])
            raise ValueError(f"Name is ambiguous, use --mid instead: {name}; matches: {choices}")
        else:
            rows.append(matched[0])
    if missing:
        raise ValueError("Singer targets not found in database: " + ", ".join(missing))
    targets = unique_targets(rows)
    if len(targets) == 0:
        raise ValueError("No singer targets resolved.")
    return targets


def resolve_targets(config: CollectConfig) -> tuple[SingerTarget, ...]:
    connection = connect(config.db_path)
    try:
        if config.all_singers:
            if config.mids or config.names:
                raise ValueError("--all cannot be combined with --mid or --name.")
            return load_all_targets(connection, config)
        return load_partial_targets(connection, config)
    finally:
        connection.close()


def cache_path(config: CollectConfig, target: SingerTarget, page: int) -> Path:
    return (
        config.raw_dir
        / "singer_homepage_song_tab"
        / target.mid
        / f"page_{page:04d}_size_{config.page_size}.json"
    )


async def execute_or_load(
    client: Client,
    config: CollectConfig,
    target: SingerTarget,
    page: int,
) -> tuple[dict[str, Any], str, Path]:
    path = cache_path(config, target, page)
    if path.exists() and not config.force:
        payload = try_load_cached_json(path)
        if payload is not None:
            return payload, "cache_hit", path
    request = dataclass_replace(
        client.singer.get_tab_detail(target.mid, TabType.SONG, num=config.page_size, page=page),
        response_model=None,
    )
    result = await client.execute(request)
    payload = result.model_dump(mode="json") if hasattr(result, "model_dump") else result
    dump_json(path, payload)
    return payload, "fetched", path


async def collect_target(
    client: Client, config: CollectConfig, target: SingerTarget
) -> dict[str, Any]:
    page = 1
    pages = 0
    rows = 0
    fetched = 0
    cache_hits = 0
    while True:
        if config.max_pages_per_singer is not None and page > config.max_pages_per_singer:
            break
        payload, status, path = await execute_or_load(client, config, target, page)
        songs = ((payload.get("SongTab") or {}).get("List")) or []
        has_more = bool(payload.get("HasMore"))
        pages += 1
        rows += len(songs)
        fetched += int(status == "fetched")
        cache_hits += int(status == "cache_hit")
        print(
            f"{target.name} mid={target.mid} page={page} status={status} songs={len(songs)} has_more={has_more} saved={path.as_posix()}"
        )
        if not songs:
            break
        if not has_more:
            break
        page += 1
    return {
        "mid": target.mid,
        "name": target.name,
        "pages": pages,
        "rows": rows,
        "fetched_pages": fetched,
        "cache_hit_pages": cache_hits,
    }


async def collect(config: CollectConfig) -> None:
    targets = resolve_targets(config)
    print(
        json.dumps({"targets": len(targets), "all_singers": config.all_singers}, ensure_ascii=False)
    )
    client = Client(rate=REQUEST_RATE, capacity=REQUEST_CAPACITY)
    summaries_by_index: dict[int, dict[str, Any]] = {}
    semaphore = asyncio.Semaphore(TARGET_CONCURRENCY)

    async def collect_indexed_target(index: int, target: SingerTarget) -> None:
        async with semaphore:
            print(f"[{index}/{len(targets)}] collect song tab: {target.name} ({target.mid})")
            summaries_by_index[index] = await collect_target(client, config, target)

    try:
        await asyncio.gather(
            *(collect_indexed_target(index, target) for index, target in enumerate(targets, 1))
        )
    finally:
        await client.close()
    summaries = [summaries_by_index[index] for index in sorted(summaries_by_index)]
    print(
        json.dumps(
            {
                "targets": len(summaries),
                "pages": sum(item["pages"] for item in summaries),
                "rows": sum(item["rows"] for item in summaries),
                "fetched_pages": sum(item["fetched_pages"] for item in summaries),
                "cache_hit_pages": sum(item["cache_hit_pages"] for item in summaries),
                "singers": summaries,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect raw QQ Music singer homepage song-tab JSON pages."
    )
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)
    parser.add_argument(
        "--singer-list-raw-dir",
        type=Path,
        default=DEFAULT_SINGER_LIST_RAW_DIR,
        help="Singer list raw directory used by step 3 to define --all targets.",
    )
    parser.add_argument(
        "--max-pages-per-singer",
        type=int,
        default=None,
        help="Limit pages per singer for smoke tests.",
    )
    parser.add_argument(
        "--force", action="store_true", help="Refetch and overwrite cached raw JSON pages."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="all_singers",
        help="Collect song-tab pages for singers selected by the current step-3 singer-list import rules.",
    )
    parser.add_argument(
        "--mvp",
        action="store_true",
        help="MVP mode: --all uses the first 10 area 0/1 singers and the MVP database by default.",
    )
    parser.add_argument(
        "--mid", action="append", help="Singer mid to collect. Can be repeated or comma-separated."
    )
    parser.add_argument(
        "--name",
        action="append",
        help="Singer exact name to collect. Can be repeated or comma-separated.",
    )
    return parser.parse_args()


def _main() -> None:
    ensure_utf8_stdout()
    args = parse_args()
    db_path = (
        args.db if args.db is not None else (DEFAULT_MVP_DB_PATH if args.mvp else DEFAULT_DB_PATH)
    )
    config = CollectConfig(
        raw_dir=args.raw_dir,
        db_path=db_path,
        page_size=args.page_size,
        singer_list_raw_dir=args.singer_list_raw_dir,
        max_pages_per_singer=args.max_pages_per_singer,
        force=args.force,
        all_singers=args.all_singers,
        mvp=args.mvp,
        mids=parse_csv_values(args.mid),
        names=parse_csv_values(args.name),
    )
    asyncio.run(collect(config))


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()
