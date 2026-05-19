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
from music_metadata_graph.pipelines.defaults import DEFAULT_DB_PATH, DEFAULT_MVP_DB_PATH
from typing import Any
from qqmusic_api import Client
from music_metadata_graph.pipelines.collect_singer_song_tab_raw import (
    CollectConfig as SongTabCollectConfig,
)
from music_metadata_graph.pipelines.collect_singer_song_tab_raw import (
    DEFAULT_PAGE_SIZE as SONG_TAB_PAGE_SIZE,
)
from music_metadata_graph.pipelines.collect_singer_song_tab_raw import DEFAULT_SINGER_LIST_RAW_DIR
from music_metadata_graph.pipelines.collect_singer_song_tab_raw import (
    resolve_targets as resolve_song_tab_targets,
)
from music_metadata_graph.pipelines.import_singer_list_to_db import create_schema, import_artists

DEFAULT_RAW_DIR = Path("data/raw/qqmusic")

REQUEST_RATE = 0.5

REQUEST_CAPACITY = 1

REQUEST_BATCH_SIZE = 20


@dataclass(frozen=True)
class SingerTarget:
    mid: str

    name: str


@dataclass(frozen=True)
class MissingSingerTarget:
    mid: str

    source_names: tuple[str, ...]

    source_song_count: int

    source_song_examples: tuple[str, ...]


@dataclass(frozen=True)
class FetchFailure:
    mid: str

    path: Path

    reason: str


@dataclass(frozen=True)
class CollectConfig:
    raw_dir: Path

    db_path: Path

    singer_list_raw_dir: Path

    force: bool

    all_available_song_tabs: bool
    mvp: bool
    mids: tuple[str, ...]

    names: tuple[str, ...]

    max_singers: int | None

    batch_size: int


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

    connection.execute("PRAGMA foreign_keys = ON")

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


def load_existing_song_tab_targets(
    connection: sqlite3.Connection, config: CollectConfig
) -> tuple[SingerTarget, ...]:
    source_root = config.raw_dir / "singer_homepage_song_tab"

    if not source_root.exists():
        raise FileNotFoundError(
            f"Singer homepage song-tab raw directory does not exist: {source_root}"
        )

    available_mids = {
        path.name
        for path in source_root.iterdir()
        if path.is_dir() and any(path.glob("page_*_size_*.json"))
    }

    if not available_mids:
        raise FileNotFoundError(f"No singer homepage song-tab raw JSON found under: {source_root}")

    rows = connection.execute("SELECT mid, name FROM artists ORDER BY rowid").fetchall()

    targets = [
        SingerTarget(mid=str(row["mid"]), name=str(row["name"]))
        for row in rows
        if str(row["mid"]) in available_mids
    ]

    if not targets:
        raise ValueError(
            "No current database artists have existing singer homepage song-tab raw JSON."
        )

    return tuple(targets)


def resolve_targets(config: CollectConfig) -> tuple[SingerTarget, ...]:
    with connect(config.db_path) as connection:
        if config.all_available_song_tabs:
            if config.mids or config.names:
                raise ValueError("--all cannot be combined with --mid or --name.")
            song_tab_config = SongTabCollectConfig(
                raw_dir=config.raw_dir,
                db_path=config.db_path,
                page_size=SONG_TAB_PAGE_SIZE,
                singer_list_raw_dir=config.singer_list_raw_dir,
                max_pages_per_singer=None,
                force=config.force,
                all_singers=True,
                mvp=config.mvp,
                mids=(),
                names=(),
            )
            targets = tuple(
                SingerTarget(mid=target.mid, name=target.name)
                for target in resolve_song_tab_targets(song_tab_config)
            )
            existing_targets = [
                target
                for target in targets
                if any(song_tab_dir(config, target).glob("page_*_size_*.json"))
            ]
            if not existing_targets:
                raise FileNotFoundError(
                    "No step-4 target singer homepage song-tab raw JSON exists yet."
                )
            return tuple(existing_targets)
        return load_partial_targets(connection, config)


def song_tab_dir(config: CollectConfig, target: SingerTarget) -> Path:
    return config.raw_dir / "singer_homepage_song_tab" / target.mid


def singer_info_path(config: CollectConfig, singer_mid: str) -> Path:
    return config.raw_dir / "singer_info" / f"{singer_mid}.json"


def load_existing_singer_mids(db_path: Path) -> set[str]:
    with connect(db_path) as connection:
        return {str(row["mid"]) for row in connection.execute("SELECT mid FROM artists").fetchall()}


def load_missing_song_singers(
    config: CollectConfig,
    singer_targets: tuple[SingerTarget, ...],
) -> tuple[list[MissingSingerTarget], int, int]:
    existing_mids = load_existing_singer_mids(config.db_path)

    missing: dict[str, dict[str, Any]] = {}

    missing_song_tab: list[str] = []

    song_rows = 0

    singer_items_without_mid = 0

    for target in singer_targets:
        source_dir = song_tab_dir(config, target)

        files = sorted(source_dir.glob("page_*_size_*.json"))

        if not files:
            missing_song_tab.append(f"{target.name}({target.mid})")

            continue

        for path in files:
            payload = load_json(path)

            for song in (payload.get("SongTab") or {}).get("List") or []:
                song_rows += 1

                song_name = str(song.get("name") or song.get("title") or "")

                for singer in song.get("singer") or []:
                    if not isinstance(singer, dict):
                        continue

                    singer_mid = str(singer.get("mid") or "").strip()

                    if not singer_mid:
                        singer_items_without_mid += 1

                        continue

                    if singer_mid in existing_mids:
                        continue

                    item = missing.setdefault(
                        singer_mid, {"song_count": 0, "examples": [], "names": []}
                    )

                    item["song_count"] += 1

                    singer_name = str(singer.get("name") or singer.get("title") or "").strip()
                    if singer_name and singer_name not in item["names"] and len(item["names"]) < 5:
                        item["names"].append(singer_name)

                    if song_name and len(item["examples"]) < 5:
                        item["examples"].append(song_name)

    if missing_song_tab:
        raise FileNotFoundError(
            "Singer homepage song-tab raw JSON is missing for targets: "
            + ", ".join(missing_song_tab)
            + ". Run collect_singer_song_tab_raw first."
        )

    targets = [
        MissingSingerTarget(
            mid=mid,
            source_names=tuple(info["names"]),
            source_song_count=int(info["song_count"]),
            source_song_examples=tuple(info["examples"]),
        )
        for mid, info in missing.items()
    ]

    return sorted(targets, key=lambda item: item.mid), song_rows, singer_items_without_mid


async def execute_or_load_batch(
    client: Client,
    config: CollectConfig,
    singers: list[MissingSingerTarget],
) -> tuple[list[tuple[int, MissingSingerTarget, dict[str, Any], str, Path]], list[FetchFailure]]:
    loaded: list[tuple[int, MissingSingerTarget, dict[str, Any], str, Path]] = []

    failures: list[FetchFailure] = []

    pending: list[tuple[int, MissingSingerTarget, Path, Any]] = []

    def save_payload(index: int, singer: MissingSingerTarget, path: Path, result: Any) -> None:
        payload = result.model_dump(mode="json") if hasattr(result, "model_dump") else result

        dump_json(path, payload)

        loaded.append((index, singer, payload, "fetched", path))

    for index, singer in enumerate(singers):
        path = singer_info_path(config, singer.mid)

        if path.exists() and not config.force:
            payload = try_load_cached_json(path)

            if payload is not None:
                loaded.append((index, singer, payload, "cache_hit", path))

                continue

        request = dataclass_replace(client.singer.get_info(singer.mid), response_model=None)

        pending.append((index, singer, path, request))

    for start in range(0, len(pending), config.batch_size):
        batch = pending[start : start + config.batch_size]

        batch_requests = [request for _, _, _, request in batch]

        try:
            fetched_results = await client.gather(
                batch_requests,
                batch_size=len(batch_requests),
                return_exceptions=True,
            )

        except Exception as exc:
            for index, singer, path, request in batch:
                try:
                    result = await client.execute(request)

                except Exception as item_exc:
                    failures.append(
                        FetchFailure(
                            mid=singer.mid,
                            path=path,
                            reason=f"{type(item_exc).__name__}: {item_exc}",
                        )
                    )

                    continue

                save_payload(index, singer, path, result)

            continue

        for (index, singer, path, _request), result in zip(batch, fetched_results, strict=True):
            if isinstance(result, Exception):
                failures.append(
                    FetchFailure(
                        mid=singer.mid, path=path, reason=f"{type(result).__name__}: {result}"
                    )
                )

                continue

            save_payload(index, singer, path, result)

    return sorted(loaded, key=lambda item: item[0]), failures


def extract_singer_row(
    requested_mid: str,
    payload: dict[str, Any],
    path: Path,
    fallback_name: str = "",
) -> tuple[dict[str, Any] | None, str]:
    info = payload.get("Info") if isinstance(payload.get("Info"), dict) else {}

    singer = payload.get("singer") if isinstance(payload.get("singer"), dict) else {}

    if not singer:
        singer = info.get("Singer") if isinstance(info.get("Singer"), dict) else {}

    base_info = payload.get("base_info") if isinstance(payload.get("base_info"), dict) else {}

    if not base_info:
        base_info = info.get("BaseInfo") if isinstance(info.get("BaseInfo"), dict) else {}

    singer_mid = str(singer.get("mid") or singer.get("SingerMid") or requested_mid or "").strip()

    name = str(singer.get("name") or singer.get("Name") or fallback_name or "").strip()

    if not singer_mid:
        return None, "missing_mid"

    if not name:
        return None, "missing_name"

    icon = str(
        singer.get("singer_pic")
        or singer.get("SingerPic")
        or singer.get("pic")
        or base_info.get("avatar")
        or base_info.get("Avatar")
        or base_info.get("singer_pic")
        or ""
    ).strip()

    if not icon:
        icon = str(
            base_info.get("background_image") or base_info.get("BackgroundImage") or ""
        ).strip()

    fans = info.get("FansNum") if isinstance(info.get("FansNum"), dict) else {}
    try:
        fans_num = int(fans.get("Num"))
    except (TypeError, ValueError):
        fans_num = None
    if fans_num is not None and fans_num <= 0:
        fans_num = None

    return (
        {
            "mid": singer_mid,
            "name": name,
            "other_name": str(
                singer.get("other_name")
                or singer.get("transName")
                or singer.get("ForeignName")
                or ""
            ),
            "fans_num": fans_num,
            "fans_source": "qqmusic.singer.get_info.FansNum.Num" if fans_num is not None else "",
            "fans_raw_json_path": path.as_posix() if fans_num is not None else "",
            "icon": icon,
            "spell": "",
            "raw_json_path": path.as_posix(),
            "raw_page": 0,
            "raw_row_index": 1,
        },
        "ok",
    )


async def collect(config: CollectConfig) -> None:
    if config.batch_size <= 0:
        raise ValueError("--batch-size must be greater than 0.")

    singer_targets = resolve_targets(config)

    missing_singers, song_rows, singer_items_without_mid = load_missing_song_singers(
        config, singer_targets
    )

    if config.max_singers is not None:
        missing_singers = missing_singers[: config.max_singers]

    print(
        json.dumps(
            {
                "target_singers": len(singer_targets),
                "song_rows": song_rows,
                "singer_items_without_mid": singer_items_without_mid,
                "missing_song_singers": len(missing_singers),
                "all_available_song_tabs": config.all_available_song_tabs,
                "batch_size": config.batch_size,
            },
            ensure_ascii=False,
        )
    )

    client = Client(rate=REQUEST_RATE, capacity=REQUEST_CAPACITY)

    rows: list[dict[str, Any]] = []

    skipped: dict[str, int] = {}

    fetched = 0

    cache_hits = 0

    fetch_failures: list[FetchFailure] = []

    try:
        loaded, fetch_failures = await execute_or_load_batch(client, config, missing_singers)

        for loaded_index, singer, payload, status, path in loaded:
            display_index = loaded_index + 1

            fetched += int(status == "fetched")

            cache_hits += int(status == "cache_hit")

            fallback_name = singer.source_names[0] if singer.source_names else ""
            row, reason = extract_singer_row(singer.mid, payload, path, fallback_name=fallback_name)

            if row is None:
                skipped[reason] = skipped.get(reason, 0) + 1

                print(
                    f"[{display_index}/{len(missing_singers)}] singer_mid={singer.mid} status={status} skipped={reason} saved={path.as_posix()}"
                )

                continue

            rows.append(row)

            print(
                f"[{display_index}/{len(missing_singers)}] artist={row['name']} mid={row['mid']} "
                f"status={status} songs={singer.source_song_count} saved={path.as_posix()}"
            )

        for failure in fetch_failures:
            print(
                f"singer_mid={failure.mid} status=failed reason={failure.reason} saved={failure.path.as_posix() if str(failure.path) else ''}"
            )

    finally:
        await client.close()

    imported = 0

    db_rows = 0

    with connect(config.db_path) as connection:
        create_schema(connection)

        if rows:
            imported = import_artists(connection, rows)

        db_rows = connection.execute("SELECT COUNT(*) FROM artists").fetchone()[0]

    print(
        json.dumps(
            {
                "target_singers": len(singer_targets),
                "song_rows": song_rows,
                "singer_items_without_mid": singer_items_without_mid,
                "missing_song_singers": len(missing_singers),
                "all_available_song_tabs": config.all_available_song_tabs,
                "batch_size": config.batch_size,
                "fetched": fetched,
                "cache_hits": cache_hits,
                "failed_fetches": len(fetch_failures),
                "failed_mids": [failure.mid for failure in fetch_failures][:50],
                "importable_singers": len(rows),
                "imported_singers": imported,
                "skipped": skipped,
                "db_artists": db_rows,
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    if fetch_failures:
        failed_mids = ", ".join(failure.mid for failure in fetch_failures)

        raise RuntimeError(
            f"Failed to fetch {len(fetch_failures)} singer info request(s). Rerun the command to continue from cached successes. Failed mids: {failed_mids}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect missing singer info from song singer mids and import it into SQLite."
    )

    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)

    parser.add_argument("--db", type=Path, default=None)

    parser.add_argument(
        "--singer-list-raw-dir",
        type=Path,
        default=DEFAULT_SINGER_LIST_RAW_DIR,
        help="Singer list raw directory used by step 3 and step 4 to define --all targets.",
    )

    parser.add_argument(
        "--force", action="store_true", help="Refetch and overwrite cached raw JSON files."
    )

    parser.add_argument(
        "--all",
        action="store_true",
        dest="all_available_song_tabs",
        help="Scan song-tab raw only for singers selected by the current step-3 singer-list import rules.",
    )
    parser.add_argument(
        "--mvp",
        action="store_true",
        help="MVP mode: --all uses the first 10 area 0/1 singers and the MVP database by default.",
    )
    parser.add_argument(
        "--mid",
        action="append",
        help="Singer mid whose song-tab raw JSON should be scanned. Can be repeated or comma-separated.",
    )

    parser.add_argument(
        "--name",
        action="append",
        help="Singer exact name whose song-tab raw JSON should be scanned. Can be repeated or comma-separated.",
    )

    parser.add_argument(
        "--max-singers",
        type=int,
        default=None,
        help="Limit missing singer requests for smoke tests.",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=REQUEST_BATCH_SIZE,
        help="Maximum request descriptors per QQ Music CGI batch.",
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
        singer_list_raw_dir=args.singer_list_raw_dir,
        force=args.force,
        all_available_song_tabs=args.all_available_song_tabs,
        mvp=args.mvp,
        mids=parse_csv_values(args.mid),
        names=parse_csv_values(args.name),
        max_singers=args.max_singers,
        batch_size=args.batch_size,
    )

    asyncio.run(collect(config))


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()
