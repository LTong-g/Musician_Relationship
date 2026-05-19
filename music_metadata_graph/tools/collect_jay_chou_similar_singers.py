from __future__ import annotations
import argparse
import asyncio
import json
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from qqmusic_api import Client
from music_metadata_graph.run_log import run_with_log

ROOT_ARTIST = {
    "id": "",
    "mid": "__area_0_1_singer_list_seed__",
    "name": "QQ音乐 area_id 0/1 歌手列表种子",
    "title": "QQ音乐 area_id 0/1 歌手列表种子",
}

DEFAULT_SEED_SINGER_LIST_DIR = Path(
    "data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all"
)

DEFAULT_BASE_DIR = Path("data/raw/qqmusic/singer_similar")

DEFAULT_RAW_DIR = DEFAULT_BASE_DIR / "runs" / "area_0_1_singer_list_seed"

DEFAULT_VALIDATION_DIR = Path("data/processed/validation/singer_similar_area_0_1_seed")

DEFAULT_LOG_DIR = Path("logs/singer_similar_area_0_1_seed")

DEFAULT_NUMBER = 100

DEFAULT_REQUEST_CACHE_DIR = DEFAULT_BASE_DIR / "request_cache"

DEFAULT_BATCH_SIZE = 20

MAX_BATCH_SIZE = 20


@dataclass(frozen=True)
class SimilarSingerConfig:
    raw_dir: Path = DEFAULT_RAW_DIR

    request_cache_dir: Path = DEFAULT_REQUEST_CACHE_DIR

    validation_dir: Path = DEFAULT_VALIDATION_DIR

    seed_singer_list_dir: Path = DEFAULT_SEED_SINGER_LIST_DIR

    max_depth: int | None = None

    max_singers: int | None = None

    max_seconds: float | None = None

    number: int = DEFAULT_NUMBER

    batch_size: int = DEFAULT_BATCH_SIZE

    force: bool = False


def utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_limit(value: int | None) -> int | None:
    if value is None or value <= 0:
        return None

    return value


def as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    if hasattr(value, "model_dump"):
        return value.model_dump()

    return dict(value)


def singer_key(singer: dict[str, Any]) -> str:
    mid = str(singer.get("mid") or "").strip()

    if mid:
        return mid

    artist_id = singer.get("id")

    return f"id:{artist_id}" if artist_id not in (None, "") else ""


def compact_singer(singer: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": singer.get("id") if singer.get("id") is not None else "",
        "mid": singer.get("mid") or "",
        "name": singer.get("name") or singer.get("title") or "",
        "title": singer.get("title") or singer.get("name") or "",
        "pmid": singer.get("pmid") or "",
        "singer_pic": singer.get("singer_pic") or "",
    }


def raw_request_path(request_cache_dir: Path, mid: str) -> Path:
    return request_cache_dir / f"{mid}.json"


def manifest_path(raw_dir: Path) -> Path:
    return raw_dir / "manifest.json"


def frontier_path(raw_dir: Path) -> Path:
    return raw_dir / "frontier.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any] | list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    text = json.dumps(data, ensure_ascii=False, indent=2)

    path.write_text(text.replace("\n", "\r\n") + "\r\n", encoding="utf-8")


def load_area_seed_artists(singer_list_dir: Path) -> list[dict[str, Any]]:
    if not singer_list_dir.exists():
        raise FileNotFoundError(f"Seed singer list raw directory not found: {singer_list_dir}")

    by_mid: dict[str, dict[str, Any]] = {}

    for path in sorted(singer_list_dir.glob("*.json")):
        payload = read_json(path)

        for row_index, row in enumerate(payload.get("singerlist") or []):
            singer = compact_singer(as_dict(row))

            mid = str(singer.get("mid") or "").strip()

            if not mid:
                continue

            try:
                area_id = int(row.get("area_id"))

            except (TypeError, ValueError):
                continue

            if area_id not in (0, 1) or mid in by_mid:
                continue

            by_mid[mid] = {
                **singer,
                "area_id": area_id,
                "first_depth": 0,
                "first_source_mid": "",
                "first_source_name": "",
                "depth": 0,
                "seed_source": "qqmusic.singer.get_singer_list_index.area_id_0_1",
                "seed_raw_json_path": path.as_posix(),
                "seed_raw_row_index": row_index,
            }

    if not by_mid:
        raise ValueError(f"No area_id 0/1 seed singers found in {singer_list_dir}")

    return list(by_mid.values())


def build_initial_manifest(config: SimilarSingerConfig) -> dict[str, Any]:
    seed_artists = load_area_seed_artists(config.seed_singer_list_dir)

    return {
        "root": ROOT_ARTIST,
        "api": "qqmusic.singer.get_similar",
        "number": config.number,
        "batch_size": config.batch_size,
        "seed_source": {
            "type": "qqmusic.singer.get_singer_list_index",
            "raw_dir": config.seed_singer_list_dir.as_posix(),
            "area_ids": [0, 1],
            "seed_count": len(seed_artists),
        },
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "requested_mids": [],
        "failed": [],
        "seen_artists": seed_artists,
        "stats": {
            "runs": 0,
            "raw_saved": 0,
            "cache_hits": 0,
            "failed": 0,
            "total_seen": len(seed_artists),
            "seed_count": len(seed_artists),
        },
    }


def load_state(config: SimilarSingerConfig) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest_file = manifest_path(config.raw_dir)

    frontier_file = frontier_path(config.raw_dir)

    if manifest_file.exists() and frontier_file.exists():
        manifest = read_json(manifest_file)

        frontier_data = read_json(frontier_file)

        frontier = list(frontier_data.get("frontier", []))

        return manifest, frontier

    manifest = build_initial_manifest(config)

    frontier = [
        {**artist, "depth": 0, "first_source_mid": "", "first_source_name": ""}
        for artist in manifest.get("seen_artists", [])
    ]

    write_json(manifest_file, manifest)

    write_json(
        frontier_file,
        {
            "root": ROOT_ARTIST,
            "seed_source": manifest.get("seed_source", {}),
            "updated_at": utc_now(),
            "frontier": frontier,
        },
    )

    return manifest, frontier


def save_state(raw_dir: Path, manifest: dict[str, Any], frontier: list[dict[str, Any]]) -> None:
    manifest["updated_at"] = utc_now()

    manifest["stats"]["total_seen"] = len(manifest.get("seen_artists", []))

    write_json(manifest_path(raw_dir), manifest)

    write_json(
        frontier_path(raw_dir),
        {
            "root": ROOT_ARTIST,
            "seed_source": manifest.get("seed_source", {}),
            "updated_at": utc_now(),
            "frontier": frontier,
        },
    )


def load_raw_response(request_cache_dir: Path, mid: str) -> dict[str, Any] | None:
    path = raw_request_path(request_cache_dir, mid)

    if not path.exists():
        return None

    try:
        return read_json(path)

    except json.JSONDecodeError:
        return None


def wrap_raw_response(
    *,
    source_artist: dict[str, Any],
    number: int,
    response: dict[str, Any],
) -> dict[str, Any]:
    return {
        "source": {
            "platform": "qqmusic",
            "api": "singer.get_similar",
            "source_mid": source_artist["mid"],
            "source_name": source_artist.get("name", ""),
            "number": number,
            "fetched_at": utc_now(),
        },
        "response": response,
    }


def response_singers(raw_payload: dict[str, Any]) -> list[dict[str, Any]]:
    response = raw_payload.get("response", raw_payload)

    singerlist = response.get("singerlist", [])

    return [compact_singer(as_dict(item)) for item in singerlist]


def write_validation_outputs(
    validation_dir: Path,
    manifest: dict[str, Any],
    edges: list[dict[str, Any]],
) -> None:
    csv_dir = validation_dir / "csv_views"

    csv_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "root": ROOT_ARTIST,
        "api": manifest.get("api"),
        "number": manifest.get("number"),
        "batch_size": manifest.get("batch_size"),
        "updated_at": utc_now(),
        "stats": manifest.get("stats", {}),
        "seen_count": len(manifest.get("seen_artists", [])),
        "edge_count": len(edges),
    }

    write_json(validation_dir / "similar_singers_summary.json", summary)

    write_csv(
        csv_dir / "similar_singers_artists.csv",
        [
            "mid",
            "id",
            "name",
            "title",
            "first_depth",
            "first_source_mid",
            "first_source_name",
            "singer_pic",
        ],
        manifest.get("seen_artists", []),
    )

    write_csv(
        csv_dir / "similar_singers_edges.csv",
        [
            "source_mid",
            "source_name",
            "source_depth",
            "target_rank",
            "target_mid",
            "target_id",
            "target_name",
            "target_title",
        ],
        edges,
    )

    write_csv(
        csv_dir / "similar_singers_failures.csv",
        ["mid", "name", "depth", "error", "failed_at"],
        manifest.get("failed", []),
    )


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    import csv

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)

        writer.writeheader()

        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def rebuild_edges_from_raw(
    raw_dir: Path, request_cache_dir: Path | None = None
) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []

    manifest = read_json(manifest_path(raw_dir))

    requested_mids = list(manifest.get("requested_mids") or [])

    artists_by_mid = {
        str(item.get("mid") or ""): item
        for item in manifest.get("seen_artists", [])
        if item.get("mid")
    }

    if request_cache_dir is None:
        request_cache_dir = raw_dir / "requests"

    if not requested_mids and request_cache_dir.exists():
        requested_mids = [path.stem for path in sorted(request_cache_dir.glob("*.json"))]

    for source_mid in sorted(set(requested_mids)):
        path = raw_request_path(request_cache_dir, source_mid)

        if not path.exists():
            continue

        try:
            raw_payload = read_json(path)

        except json.JSONDecodeError:
            continue

        source = raw_payload.get("source", {})

        source_artist = artists_by_mid.get(source_mid, {})

        for rank, target in enumerate(response_singers(raw_payload), start=1):
            edges.append(
                {
                    "source_mid": source.get("source_mid") or source_mid,
                    "source_name": source_artist.get("name") or source.get("source_name", ""),
                    "source_depth": source_artist.get("first_depth", ""),
                    "target_rank": rank,
                    "target_mid": target.get("mid", ""),
                    "target_id": target.get("id", ""),
                    "target_name": target.get("name", ""),
                    "target_title": target.get("title", ""),
                }
            )

    return edges


def should_stop(
    config: SimilarSingerConfig, manifest: dict[str, Any], start_time: float, current_depth: int
) -> str | None:
    if config.max_depth is not None and current_depth >= config.max_depth:
        return f"max_depth_reached:{config.max_depth}"

    if (
        config.max_singers is not None
        and len(manifest.get("seen_artists", [])) >= config.max_singers
    ):
        return f"max_singers_reached:{config.max_singers}"

    if config.max_seconds is not None and time.monotonic() - start_time >= config.max_seconds:
        return f"max_seconds_reached:{config.max_seconds}"

    return None


async def fetch_batch(
    client: Client,
    batch: list[dict[str, Any]],
    depth: int,
    config: SimilarSingerConfig,
) -> list[tuple[dict[str, Any], tuple[dict[str, Any], str] | Exception]]:
    results: list[tuple[dict[str, Any], tuple[dict[str, Any], str] | Exception]] = []

    uncached: list[dict[str, Any]] = []

    for seed in batch:
        cached = None if config.force else load_raw_response(config.request_cache_dir, seed["mid"])

        if cached is not None:
            results.append((seed, (cached, "cache_hit")))

        else:
            uncached.append(seed)

    if not uncached:
        return results

    requests = [client.singer.get_similar(seed["mid"], number=config.number) for seed in uncached]

    fetched = await client.gather(requests, batch_size=config.batch_size, return_exceptions=True)

    for seed, response in zip(uncached, fetched):
        if isinstance(response, Exception):
            results.append((seed, response))

            continue

        payload = wrap_raw_response(
            source_artist=seed,
            number=config.number,
            response=as_dict(response),
        )

        write_json(raw_request_path(config.request_cache_dir, seed["mid"]), payload)

        results.append((seed, (payload, "fetched")))

    return results


async def collect_async(config: SimilarSingerConfig) -> dict[str, Any]:
    if config.batch_size <= 0 or config.batch_size > MAX_BATCH_SIZE:
        raise ValueError(f"batch_size must be between 1 and {MAX_BATCH_SIZE}")

    manifest, frontier = load_state(config)

    manifest["stats"]["runs"] = int(manifest["stats"].get("runs", 0)) + 1

    requested_mids = set(manifest.get("requested_mids", []))

    seen_by_key = {
        singer_key(item): item for item in manifest.get("seen_artists", []) if singer_key(item)
    }

    start_time = time.monotonic()

    stop_reason = ""

    async with Client() as client:
        while frontier:
            depth = int(frontier[0].get("depth", 0)) + 1

            stop_reason = should_stop(config, manifest, start_time, depth - 1) or ""

            if stop_reason:
                break

            current_layer = [item for item in frontier if int(item.get("depth", 0)) == depth - 1]

            remaining_frontier = [
                item for item in frontier if int(item.get("depth", 0)) != depth - 1
            ]

            print(f"== depth {depth} ==")

            print(
                f"layer_sources={len(current_layer)} total_seen={len(seen_by_key)} requested={len(requested_mids)}"
            )

            next_layer: list[dict[str, Any]] = []

            for start in range(0, len(current_layer), config.batch_size):
                pending_current_layer = current_layer[start + config.batch_size :]

                batch = current_layer[start : start + config.batch_size]

                print(
                    f"batch={start // config.batch_size + 1}/"
                    f"{(len(current_layer) + config.batch_size - 1) // config.batch_size} size={len(batch)}"
                )

                results = await fetch_batch(client, batch, depth, config)

                for seed, result in results:
                    if isinstance(result, Exception):
                        failure = {
                            "mid": seed.get("mid", ""),
                            "name": seed.get("name", ""),
                            "depth": depth,
                            "error": repr(result),
                            "failed_at": utc_now(),
                        }

                        manifest["failed"].append(failure)

                        manifest["stats"]["failed"] = int(manifest["stats"].get("failed", 0)) + 1

                        print(
                            f"failed mid={failure['mid']} name={failure['name']} error={failure['error']}"
                        )

                        continue

                    raw_payload, status = result

                    if status == "cache_hit":
                        manifest["stats"]["cache_hits"] = (
                            int(manifest["stats"].get("cache_hits", 0)) + 1
                        )

                    else:
                        manifest["stats"]["raw_saved"] = (
                            int(manifest["stats"].get("raw_saved", 0)) + 1
                        )

                    requested_mids.add(seed["mid"])

                    for target in response_singers(raw_payload):
                        key = singer_key(target)

                        if not key or key in seen_by_key:
                            continue

                        enriched = {
                            **target,
                            "first_depth": depth,
                            "first_source_mid": seed.get("mid", ""),
                            "first_source_name": seed.get("name", ""),
                            "depth": depth,
                        }

                        seen_by_key[key] = enriched

                        next_layer.append(enriched)

                        if (
                            config.max_singers is not None
                            and len(seen_by_key) >= config.max_singers
                        ):
                            stop_reason = f"max_singers_reached:{config.max_singers}"

                            break

                    if stop_reason:
                        break

                manifest["requested_mids"] = sorted(requested_mids)

                manifest["seen_artists"] = list(seen_by_key.values())

                frontier = pending_current_layer + remaining_frontier + next_layer

                save_state(config.raw_dir, manifest, frontier)

                if stop_reason:
                    break

            print(
                f"depth={depth} new={len(next_layer)} total_seen={len(seen_by_key)} stop_reason={stop_reason or 'none'}"
            )

            if stop_reason:
                break

            frontier = remaining_frontier + next_layer

            if not next_layer and not remaining_frontier:
                stop_reason = "frontier_empty"

                break

    manifest["requested_mids"] = sorted(requested_mids)

    manifest["seen_artists"] = list(seen_by_key.values())

    save_state(config.raw_dir, manifest, frontier)

    edges = rebuild_edges_from_raw(config.raw_dir, config.request_cache_dir)

    write_validation_outputs(config.validation_dir, manifest, edges)

    summary = {
        "stop_reason": stop_reason or "frontier_empty",
        "requested_count": len(requested_mids),
        "seen_count": len(seen_by_key),
        "frontier_count": len(frontier),
        "edge_count": len(edges),
        "raw_dir": config.raw_dir.as_posix(),
        "request_cache_dir": config.request_cache_dir.as_posix(),
        "validation_dir": config.validation_dir.as_posix(),
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))

    return summary


def run(config: SimilarSingerConfig) -> dict[str, Any]:
    return asyncio.run(collect_async(config))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect QQ Music similar singer network from area_id 0/1 singer-list seeds."
    )

    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)

    parser.add_argument("--request-cache-dir", type=Path, default=DEFAULT_REQUEST_CACHE_DIR)

    parser.add_argument("--validation-dir", type=Path, default=DEFAULT_VALIDATION_DIR)

    parser.add_argument(
        "--seed-singer-list-dir",
        type=Path,
        default=DEFAULT_SEED_SINGER_LIST_DIR,
        help="First-step singer-list raw directory used to seed area_id 0/1 singers.",
    )

    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Maximum recursive depth. Omit or use <=0 for unlimited.",
    )

    parser.add_argument(
        "--max-singers",
        type=int,
        default=None,
        help="Maximum unique singer count including initial area_id 0/1 seeds. Omit or use <=0 for unlimited.",
    )

    parser.add_argument(
        "--max-seconds",
        type=float,
        default=None,
        help="Maximum runtime seconds. Omit or use <=0 for unlimited.",
    )

    parser.add_argument(
        "--number", type=int, default=DEFAULT_NUMBER, help="number parameter passed to get_similar."
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help="Requests per gather batch; maximum 20.",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Refetch even if a raw JSON for the source MID already exists.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config = SimilarSingerConfig(
        raw_dir=args.raw_dir,
        request_cache_dir=args.request_cache_dir,
        validation_dir=args.validation_dir,
        seed_singer_list_dir=args.seed_singer_list_dir,
        max_depth=normalize_limit(args.max_depth),
        max_singers=normalize_limit(args.max_singers),
        max_seconds=args.max_seconds if args.max_seconds and args.max_seconds > 0 else None,
        number=args.number,
        batch_size=args.batch_size,
        force=args.force,
    )

    run_with_log("collect_jay_chou_similar_singers", lambda: run(config), log_dir=DEFAULT_LOG_DIR)


if __name__ == "__main__":
    main()
