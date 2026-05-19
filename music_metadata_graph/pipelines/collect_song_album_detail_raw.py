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

DEFAULT_RAW_DIR = Path("data/raw/qqmusic")
DEFAULT_FAILURE_JSON = Path(
    "data/processed/validation/album_detail_fetch_failures/album_detail_fetch_failures.json"
)
DEFAULT_MVP_FAILURE_JSON = Path(
    "data/processed/validation_mvp/album_detail_fetch_failures/album_detail_fetch_failures.json"
)

REQUEST_RATE = 0.5

REQUEST_CAPACITY = 1

REQUEST_BATCH_SIZE = 20
PROGRESS_EVERY = 1000


@dataclass(frozen=True)
class SingerTarget:
    mid: str

    name: str


@dataclass(frozen=True)
class AlbumTarget:
    key: str

    source_song_count: int

    source_singer_mids: tuple[str, ...]


@dataclass(frozen=True)
class FetchFailure:
    key: str

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

    max_albums: int | None

    batch_size: int

    max_failed_fetches: int

    failure_json: Path


def ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    text = json.dumps(payload, ensure_ascii=False, indent=2)

    path.write_text(text, encoding="utf-8")


def write_failure_report(path: Path, failures: list[FetchFailure]) -> None:
    dump_json(
        path,
        {
            "failed_fetches": len(failures),
            "failed_album_keys": [failure.key for failure in failures],
            "failures": [
                {
                    "album_key": failure.key,
                    "raw_json_path": failure.path.as_posix(),
                    "reason": failure.reason,
                }
                for failure in failures
            ],
        },
    )


def validate_fetch_failure_limit(failures: list[FetchFailure], max_failed_fetches: int) -> None:
    if max_failed_fetches < 0:
        raise ValueError("--max-failed-fetches must be greater than or equal to 0.")
    if len(failures) > max_failed_fetches:
        failed_keys = ", ".join(failure.key for failure in failures)
        raise RuntimeError(
            f"Failed to fetch {len(failures)} album detail request(s). "
            "Rerun the command to continue from cached successes. "
            f"Failed album keys: {failed_keys}"
        )


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


def album_detail_path(config: CollectConfig, album_key: str) -> Path:
    return config.raw_dir / "song_album_detail" / f"{album_key}.json"


def print_album_progress(
    display_index: int,
    total: int,
    album: AlbumTarget,
    payload: dict[str, Any] | None,
    status: str,
    path: Path,
) -> None:
    should_print = (
        status != "cache_hit" or display_index == total or display_index % PROGRESS_EVERY == 0
    )
    if not should_print:
        return
    payload_obj = payload if isinstance(payload, dict) else {}
    album_obj = payload_obj.get("album") or payload_obj.get("basicInfo") or {}
    album_name = album_obj.get("name") or album_obj.get("albumName") or album.key
    print(
        f"[{display_index}/{total}] album={album_name} key={album.key} "
        f"status={status} songs={album.source_song_count} saved={path.as_posix()}",
        flush=True,
    )


def album_key_from_song(song: dict[str, Any]) -> str:
    album = song.get("album") if isinstance(song.get("album"), dict) else {}

    album_mid = str(album.get("mid") or "").strip()

    if album_mid:
        return album_mid

    album_id = album.get("id")

    if album_id not in (None, "", 0, "0"):
        return str(album_id)

    return ""


def load_album_targets(
    config: CollectConfig, singer_targets: tuple[SingerTarget, ...]
) -> tuple[list[AlbumTarget], int, int]:
    albums: dict[str, dict[str, Any]] = {}

    missing_song_tab: list[str] = []

    song_rows = 0

    songs_missing_album_key = 0

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

                album_key = album_key_from_song(song)

                if not album_key:
                    songs_missing_album_key += 1

                    continue

                item = albums.setdefault(album_key, {"song_count": 0, "source_singer_mids": set()})

                item["song_count"] += 1

                item["source_singer_mids"].add(target.mid)

    if missing_song_tab:
        raise FileNotFoundError(
            "Singer homepage song-tab raw JSON is missing for targets: "
            + ", ".join(missing_song_tab)
            + ". Run collect_singer_song_tab_raw first."
        )

    result = [
        AlbumTarget(
            key=key,
            source_song_count=int(info["song_count"]),
            source_singer_mids=tuple(sorted(info["source_singer_mids"])),
        )
        for key, info in albums.items()
    ]

    return sorted(result, key=lambda item: item.key), song_rows, songs_missing_album_key


async def execute_or_load_batch(
    client: Client,
    config: CollectConfig,
    albums: list[AlbumTarget],
) -> tuple[list[tuple[int, AlbumTarget, dict[str, Any], str, Path]], list[FetchFailure]]:
    loaded: list[tuple[int, AlbumTarget, dict[str, Any], str, Path]] = []

    failures: list[FetchFailure] = []

    pending: list[tuple[int, AlbumTarget, Path, Any]] = []
    total = len(albums)

    def save_payload(index: int, album: AlbumTarget, path: Path, result: Any) -> None:
        payload = result.model_dump(mode="json") if hasattr(result, "model_dump") else result

        dump_json(path, payload)

        loaded.append((index, album, payload, "fetched", path))
        print_album_progress(index + 1, total, album, payload, "fetched", path)

    for index, album in enumerate(albums):
        path = album_detail_path(config, album.key)

        if path.exists() and not config.force:
            payload = try_load_cached_json(path)

            if payload is not None:
                loaded.append((index, album, payload, "cache_hit", path))
                print_album_progress(index + 1, total, album, payload, "cache_hit", path)

                continue

        request = dataclass_replace(client.album.get_detail(album.key), response_model=None)

        pending.append((index, album, path, request))

    for start in range(0, len(pending), config.batch_size):
        batch = pending[start : start + config.batch_size]

        batch_requests = [request for _, _, _, request in batch]

        try:
            fetched_results = await client.gather(
                batch_requests,
                batch_size=len(batch_requests),
                return_exceptions=True,
            )

        except Exception:
            for index, album, path, request in batch:
                try:
                    result = await client.execute(request)

                except Exception as item_exc:
                    failures.append(
                        FetchFailure(
                            key=album.key,
                            path=path,
                            reason=f"{type(item_exc).__name__}: {item_exc}",
                        )
                    )
                    print(
                        f"[{index + 1}/{total}] album_key={album.key} status=failed "
                        f"reason={type(item_exc).__name__}: {item_exc} saved={path.as_posix()}",
                        flush=True,
                    )

                    continue

                save_payload(index, album, path, result)

            continue

        for (index, album, path, _request), result in zip(batch, fetched_results, strict=True):
            if isinstance(result, Exception):
                failures.append(
                    FetchFailure(
                        key=album.key, path=path, reason=f"{type(result).__name__}: {result}"
                    )
                )
                print(
                    f"[{index + 1}/{total}] album_key={album.key} status=failed "
                    f"reason={type(result).__name__}: {result} saved={path.as_posix()}",
                    flush=True,
                )

                continue

            save_payload(index, album, path, result)

    return sorted(loaded, key=lambda item: item[0]), failures


async def collect(config: CollectConfig) -> None:
    if config.batch_size <= 0:
        raise ValueError("--batch-size must be greater than 0.")

    singer_targets = resolve_targets(config)

    albums, song_rows, songs_missing_album_key = load_album_targets(config, singer_targets)

    if config.max_albums is not None:
        albums = albums[: config.max_albums]

    print(
        json.dumps(
            {
                "singers": len(singer_targets),
                "song_rows": song_rows,
                "songs_missing_album_key": songs_missing_album_key,
                "albums": len(albums),
                "all_available_song_tabs": config.all_available_song_tabs,
                "batch_size": config.batch_size,
            },
            ensure_ascii=False,
        )
    )

    client = Client(rate=REQUEST_RATE, capacity=REQUEST_CAPACITY)

    fetched = 0

    cache_hits = 0

    fetch_failures: list[FetchFailure] = []

    try:
        loaded, fetch_failures = await execute_or_load_batch(client, config, albums)

        for _loaded_index, _album, _payload, status, _path in loaded:
            fetched += int(status == "fetched")

            cache_hits += int(status == "cache_hit")

    finally:
        await client.close()

    print(
        json.dumps(
            {
                "singers": len(singer_targets),
                "song_rows": song_rows,
                "songs_missing_album_key": songs_missing_album_key,
                "albums": len(albums),
                "all_available_song_tabs": config.all_available_song_tabs,
                "batch_size": config.batch_size,
                "fetched": fetched,
                "cache_hits": cache_hits,
                "failed_fetches": len(fetch_failures),
                "failed_album_keys": [failure.key for failure in fetch_failures][:50],
                "max_failed_fetches": config.max_failed_fetches,
                "failure_json": config.failure_json.as_posix(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    write_failure_report(config.failure_json, fetch_failures)

    validate_fetch_failure_limit(fetch_failures, config.max_failed_fetches)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect raw QQ Music album detail JSON from singer homepage song-tab raw JSON."
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
        help="Collect album details only from singers selected by the current step-3 singer-list import rules.",
    )
    parser.add_argument(
        "--mvp",
        action="store_true",
        help="MVP mode: --all uses the first 10 area 0/1 singers and the MVP database by default.",
    )
    parser.add_argument(
        "--mid",
        action="append",
        help="Singer mid whose song-tab raw JSON should be used. Can be repeated or comma-separated.",
    )

    parser.add_argument(
        "--name",
        action="append",
        help="Singer exact name whose song-tab raw JSON should be used. Can be repeated or comma-separated.",
    )

    parser.add_argument(
        "--max-albums", type=int, default=None, help="Limit albums for smoke tests."
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=REQUEST_BATCH_SIZE,
        help="Maximum request descriptors per QQ Music CGI batch.",
    )
    parser.add_argument(
        "--max-failed-fetches",
        type=int,
        default=0,
        help="Allow up to this many album detail fetch failures after writing the failure report.",
    )
    parser.add_argument(
        "--failure-json",
        type=Path,
        default=None,
        help="JSON report path for album detail fetch failures.",
    )

    return parser.parse_args()


def _main() -> None:
    ensure_utf8_stdout()

    args = parse_args()
    db_path = (
        args.db if args.db is not None else (DEFAULT_MVP_DB_PATH if args.mvp else DEFAULT_DB_PATH)
    )
    failure_json = (
        args.failure_json
        if args.failure_json is not None
        else (DEFAULT_MVP_FAILURE_JSON if args.mvp else DEFAULT_FAILURE_JSON)
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
        max_albums=args.max_albums,
        batch_size=args.batch_size,
        max_failed_fetches=args.max_failed_fetches,
        failure_json=failure_json,
    )

    asyncio.run(collect(config))


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()
