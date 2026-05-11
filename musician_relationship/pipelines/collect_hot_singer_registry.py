from __future__ import annotations

import argparse
import asyncio
import csv
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from qqmusic_api import Client
from qqmusic_api.modules.singer import AreaType, GenreType, IndexType, SexType


DEFAULT_RAW_DIR = Path("data/raw/qqmusic")
DEFAULT_OUTPUT_DIR = Path("data/processed/singer_registry/qqmusic_hot")
DEFAULT_PAGE_SIZE = 80
REQUEST_RATE = 0.5
REQUEST_CAPACITY = 1


@dataclass(frozen=True)
class CollectConfig:
    page_size: int
    max_pages: int | None
    raw_dir: Path
    output_dir: Path


def ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


async def execute_or_load(client: Client, cache_path: Path, request: Any) -> Any:
    if cache_path.exists():
        return load_json(cache_path)
    result = await client.execute(request)
    payload = result.model_dump(mode="json") if hasattr(result, "model_dump") else result
    dump_json(cache_path, payload)
    return payload


def compact_singer(raw: dict[str, Any], page: int, rank: int) -> dict[str, Any]:
    return {
        "id": raw.get("id"),
        "mid": raw.get("mid"),
        "name": raw.get("name"),
        "title": raw.get("title"),
        "other_name": raw.get("other_name"),
        "spell": raw.get("spell"),
        "singer_pic": raw.get("singer_pic"),
        "area_id": raw.get("area_id"),
        "country_id": raw.get("country_id"),
        "country": raw.get("country"),
        "type": raw.get("type"),
        "pmid": raw.get("pmid"),
        "source": "qqmusic.singer.get_singer_list_index",
        "discovery_page": page,
        "discovery_rank": rank,
    }


async def collect_hot_singers(client: Client, config: CollectConfig) -> tuple[list[dict[str, Any]], int | None]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    page = 1
    total: int | None = None

    while True:
        if config.max_pages is not None and page > config.max_pages:
            break
        cache_path = (
            config.raw_dir
            / "singer_list_index"
            / "area_all_sex_all_genre_all_index_all"
            / f"page_{page:04d}_size_{config.page_size}.json"
        )
        request = client.singer.get_singer_list_index(
            area=AreaType.ALL,
            sex=SexType.ALL,
            genre=GenreType.ALL,
            index=IndexType.ALL,
            page=page,
            num=config.page_size,
        )
        payload = await execute_or_load(client, cache_path, request)
        singers = payload.get("singerlist") or []
        if total is None:
            total = payload.get("total")
        print(f"page={page} singers={len(singers)} total={total}")
        if not singers:
            break
        for singer in singers:
            mid = str(singer.get("mid") or "")
            key = mid or f"id:{singer.get('id')}"
            if key in seen:
                continue
            seen.add(key)
            rows.append(compact_singer(singer, page, len(rows) + 1))
        if total is not None and len(rows) >= total:
            break
        if len(singers) < config.page_size:
            break
        page += 1

    return rows, total


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "discovery_rank",
        "id",
        "mid",
        "name",
        "other_name",
        "spell",
        "country",
        "area_id",
        "country_id",
        "singer_pic",
        "source",
        "discovery_page",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fieldnames})


async def run(config: CollectConfig) -> None:
    generated_at = now_iso()
    client = Client(rate=REQUEST_RATE, capacity=REQUEST_CAPACITY)
    try:
        singers, total = await collect_hot_singers(client, config)
    finally:
        await client.close()

    registry = {
        "generated_at": generated_at,
        "source": "qqmusic.singer.get_singer_list_index",
        "identity_key": "mid",
        "notes": [
            "Singer id and mid are treated as stable identity keys.",
            "Names, pictures, ranks, and hot-list membership are snapshots and may change.",
        ],
        "counts": {
            "api_total": total,
            "singers": len(singers),
        },
        "singers": singers,
    }
    discovery = {
        "generated_at": generated_at,
        "source": "qqmusic.singer.get_singer_list_index",
        "query": {
            "area": "ALL",
            "sex": "ALL",
            "genre": "ALL",
            "index": "ALL",
            "page_size": config.page_size,
            "max_pages": config.max_pages,
        },
        "counts": registry["counts"],
        "ranked_singers": singers,
    }
    config.output_dir.mkdir(parents=True, exist_ok=True)
    dump_json(config.output_dir / "singer_registry.json", registry)
    dump_json(config.output_dir / "hot_singer_discovery_snapshot.json", discovery)
    write_csv(config.output_dir / "singer_registry.csv", singers)
    print(json.dumps(registry["counts"], ensure_ascii=False, indent=2))
    print(f"saved: {config.output_dir / 'singer_registry.json'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect QQ Music hot singer identity registry.")
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)
    parser.add_argument("--max-pages", type=int, default=None, help="Limit pages for smoke tests. Omit for full list.")
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    ensure_utf8_stdout()
    args = parse_args()
    config = CollectConfig(
        page_size=args.page_size,
        max_pages=args.max_pages,
        raw_dir=args.raw_dir,
        output_dir=args.output_dir,
    )
    asyncio.run(run(config))


if __name__ == "__main__":
    main()
