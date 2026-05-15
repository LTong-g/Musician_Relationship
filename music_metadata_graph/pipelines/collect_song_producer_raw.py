from __future__ import annotations



import argparse

import asyncio

import csv

import json

import sqlite3

import sys

from dataclasses import dataclass

from dataclasses import replace as dataclass_replace

from pathlib import Path

from music_metadata_graph.run_log import run_with_log
from music_metadata_graph.pipelines.defaults import DEFAULT_DB_PATH

from typing import Any



from qqmusic_api import Client



from music_metadata_graph.pipelines.song_csv import escape_excel_formula_row





DEFAULT_RAW_DIR = Path("data/raw/qqmusic/song_producer")

DEFAULT_MISSING_MID_CSV = Path("data/processed/validation/song_producer/csv_views/song_producer_missing_mid.csv")

REQUEST_RATE = 0.5

REQUEST_CAPACITY = 1

REQUEST_BATCH_SIZE = 20

CREDIT_TITLES = ("作词", "作曲")





@dataclass(frozen=True)

class ProducerConfig:

    raw_dir: Path

    db_path: Path

    missing_mid_csv: Path

    force: bool

    max_songs: int | None

    artist_mid: str | None

    artist_name: str | None

    batch_size: int





@dataclass(frozen=True)

class FetchFailure:

    song_mid: str

    path: Path

    reason: str





def ensure_utf8_stdout() -> None:

    if hasattr(sys.stdout, "reconfigure"):

        sys.stdout.reconfigure(encoding="utf-8")





def dump_json(path: Path, payload: Any) -> None:

    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")





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





def producer_path(raw_dir: Path, song_mid: str) -> Path:

    return raw_dir / f"{song_mid}.json"





async def execute_or_load_batch(

    client: Client,

    config: ProducerConfig,

    song_mids: list[str],

) -> tuple[list[tuple[int, str, dict[str, Any], str, Path]], list[FetchFailure]]:

    loaded: list[tuple[int, str, dict[str, Any], str, Path]] = []

    failures: list[FetchFailure] = []

    pending: list[tuple[int, str, Path, Any]] = []



    def save_payload(index: int, song_mid: str, path: Path, result: Any) -> None:

        payload = result.model_dump(mode="json") if hasattr(result, "model_dump") else result

        dump_json(path, payload)

        loaded.append((index, song_mid, payload, "fetched", path))



    for index, song_mid in enumerate(song_mids):

        path = producer_path(config.raw_dir, song_mid)

        if path.exists() and not config.force:

            payload = try_load_cached_json(path)

            if payload is not None:

                loaded.append((index, song_mid, payload, "cache_hit", path))

                continue

        request = dataclass_replace(client.song.get_producer(song_mid), response_model=None)

        pending.append((index, song_mid, path, request))



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

            for index, song_mid, path, request in batch:

                try:

                    result = await client.execute(request)

                except Exception as item_exc:

                    failures.append(FetchFailure(song_mid=song_mid, path=path, reason=f"{type(item_exc).__name__}: {item_exc}"))

                    continue

                save_payload(index, song_mid, path, result)

            continue



        for (index, song_mid, path, _request), result in zip(batch, fetched_results, strict=True):

            if isinstance(result, Exception):

                failures.append(FetchFailure(song_mid=song_mid, path=path, reason=f"{type(result).__name__}: {result}"))

                continue

            save_payload(index, song_mid, path, result)



    return sorted(loaded, key=lambda item: item[0]), failures





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





def inspect_missing_mid(song_mid: str, payload: Any) -> list[dict[str, Any]]:

    missing: list[dict[str, Any]] = []

    for group in producer_groups(payload):

        title = str(group.get("title") or group.get("Title") or "")

        if title not in CREDIT_TITLES:

            continue

        producer_list = group.get("producers") if isinstance(group.get("producers"), list) else group.get("Producers")

        producers = producer_list if isinstance(producer_list, list) else []

        for order, producer in enumerate(producers, 1):

            if not isinstance(producer, dict):

                continue

            artist_mid = str(producer.get("singer_mid") or producer.get("SingerMid") or "").strip()

            if artist_mid:

                continue

            missing.append(

                {

                    "song_mid": song_mid,

                    "role": title,

                    "producer_order": order,

                    "producer_name": producer.get("name") or producer.get("Name") or "",

                    "producer_icon": producer.get("icon") or producer.get("Icon") or "",

                    "producer_type": producer.get("type") if producer.get("type") is not None else producer.get("Type") or "",

                    "producer_scheme": producer.get("scheme") or producer.get("Scheme") or "",

                }

            )

    return missing





def write_missing_mid_csv(path: Path, rows: list[dict[str, Any]]) -> None:

    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["song_mid", "role", "producer_order", "producer_name", "producer_icon", "producer_type", "producer_scheme"]

    with path.open("w", encoding="utf-8-sig", newline="") as file:

        writer = csv.DictWriter(file, fieldnames=fieldnames, lineterminator="\r\n")

        writer.writeheader()

        writer.writerows(escape_excel_formula_row(row) for row in rows)





async def collect(config: ProducerConfig) -> None:

    if config.batch_size <= 0:

        raise ValueError("--batch-size must be greater than 0.")

    with connect(config.db_path) as connection:

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

        song_mids = [

            str(row["mid"])

            for row in connection.execute(

                f"SELECT mid FROM songs {where_sql} ORDER BY name, id, mid",

                params,

            ).fetchall()

        ]

    if config.max_songs is not None:

        song_mids = song_mids[: config.max_songs]

    client = Client(rate=REQUEST_RATE, capacity=REQUEST_CAPACITY)

    fetched = 0

    cache_hits = 0

    fetch_failures: list[FetchFailure] = []

    missing_mid_rows: list[dict[str, Any]] = []

    try:

        loaded, fetch_failures = await execute_or_load_batch(client, config, song_mids)

        for loaded_index, song_mid, payload, status, path in loaded:

            display_index = loaded_index + 1

            fetched += int(status == "fetched")

            cache_hits += int(status == "cache_hit")

            missing_mid_rows.extend(inspect_missing_mid(song_mid, payload))

            print(f"[{display_index}/{len(song_mids)}] song_mid={song_mid} status={status} saved={path.as_posix()}")

        for failure in fetch_failures:

            print(f"song_mid={failure.song_mid} status=failed reason={failure.reason} saved={failure.path.as_posix()}")

    finally:

        await client.close()

    write_missing_mid_csv(config.missing_mid_csv, missing_mid_rows)

    print(

        json.dumps(

            {

                "songs": len(song_mids),

                "artist_mid": config.artist_mid or "",

                "artist_name": config.artist_name or "",

                "batch_size": config.batch_size,

                "fetched": fetched,

                "cache_hits": cache_hits,

                "failed_fetches": len(fetch_failures),

                "failed_song_mids": [failure.song_mid for failure in fetch_failures][:50],

                "missing_mid_rows": len(missing_mid_rows),

                "missing_mid_csv": config.missing_mid_csv.as_posix(),

            },

            ensure_ascii=False,

            indent=2,

        )

    )

    if fetch_failures:

        failed_mids = ", ".join(failure.song_mid for failure in fetch_failures)

        raise RuntimeError(f"Failed to fetch {len(fetch_failures)} song producer request(s). Rerun the command to continue from cached successes. Failed song mids: {failed_mids}")





def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(description="Step 9: collect QQ Music song producer raw JSON and inspect lyricist/composer missing mids.")

    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)

    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)

    parser.add_argument("--missing-mid-csv", type=Path, default=DEFAULT_MISSING_MID_CSV)

    parser.add_argument("--force", action="store_true", help="Refetch and overwrite cached producer raw JSON.")

    parser.add_argument("--max-songs", type=int, default=None, help="Limit songs for smoke tests.")

    parser.add_argument("--artist-mid", default=None, help="Only collect songs whose singer list contains this artist mid.")

    parser.add_argument("--artist-name", default=None, help="Only collect songs whose singer list contains this exact artist name.")

    parser.add_argument("--batch-size", type=int, default=REQUEST_BATCH_SIZE, help="Maximum request descriptors per QQ Music CGI batch.")

    return parser.parse_args()





def _main() -> None:

    ensure_utf8_stdout()

    args = parse_args()

    asyncio.run(

        collect(

            ProducerConfig(

                raw_dir=args.raw_dir,

                db_path=args.db,

                missing_mid_csv=args.missing_mid_csv,

                force=args.force,

                max_songs=args.max_songs,

                artist_mid=args.artist_mid,

                artist_name=args.artist_name,

                batch_size=args.batch_size,

            )

        )

    )





def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":

    main()


