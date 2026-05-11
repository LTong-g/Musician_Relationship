from __future__ import annotations

import argparse
import asyncio
import csv
import json
import re
import sys
import codecs
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from qqmusic_api import Client
from qqmusic_api.modules.singer import AreaType, GenreType, IndexType, SexType


DEFAULT_RAW_DIR = Path("data/raw/qqmusic")
DEFAULT_PROCESSED_DIR = Path("data/processed")
DEFAULT_SINGER_LIMIT = 50
DEFAULT_PAGE_SIZE = 30
REQUEST_RATE = 0.5
REQUEST_CAPACITY = 1

TITLE_VERSION_KEYWORDS = (
    "live",
    "演唱会",
    "现场",
    "demo",
    "remix",
    "伴奏",
    "片段",
    "翻唱",
    "cover",
    "纯音乐",
    "纯音乐版",
    "试听",
    "铃声",
    "karaoke",
)
def find_keyword_by_priority(text: str, keywords: tuple[str, ...]) -> str | None:
    for keyword in keywords:
        if re.search(re.escape(keyword), text, re.IGNORECASE):
            return keyword
    return None


@dataclass(frozen=True)
class CollectConfig:
    singer_limit: int
    page_size: int
    max_pages_per_singer: int | None
    raw_dir: Path
    processed_dir: Path
    target_singer_mid: str | None
    target_singer_name: str | None


def ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_title_identity(value: str) -> str:
    text = unicodedata.normalize("NFKC", value or "").casefold()
    return normalize_spaces(text)


def decode_cli_text(value: str | None) -> str | None:
    if value is None:
        return None
    if "\\u" not in value and "\\U" not in value:
        return value
    return codecs.decode(value, "unicode_escape")


def title_version_text(song: dict[str, Any]) -> str:
    parts = [
        str(song.get("name") or ""),
        str(song.get("title") or ""),
        str(song.get("subtitle") or ""),
    ]
    return normalize_spaces(" ".join(parts))


def version_filter_reason(song: dict[str, Any]) -> str | None:
    title_keyword = find_keyword_by_priority(title_version_text(song), TITLE_VERSION_KEYWORDS)
    if title_keyword is not None:
        return f"title_version_keyword:{title_keyword}"
    return None


def name_title_filter_reason(song: dict[str, Any]) -> str | None:
    name = normalize_title_identity(str(song.get("name") or ""))
    title = normalize_title_identity(str(song.get("title") or ""))
    if name != title:
        return "name_title_mismatch"
    return None


def compact_singer(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": raw.get("id"),
        "mid": raw.get("mid"),
        "name": raw.get("name"),
        "other_name": raw.get("other_name"),
        "spell": raw.get("spell"),
        "singer_pic": raw.get("singer_pic"),
        "area_id": raw.get("area_id"),
        "country": raw.get("country"),
        "source": "qqmusic.singer.get_singer_list_index",
    }


def compact_song(song: dict[str, Any], source_singer: dict[str, Any], filter_reason: str | None) -> dict[str, Any]:
    album = song.get("album") or {}
    singers = song.get("singer") or []
    return {
        "id": song.get("id"),
        "mid": song.get("mid"),
        "name": song.get("name"),
        "title": song.get("title"),
        "subtitle": song.get("subtitle"),
        "album_id": album.get("id"),
        "album_mid": album.get("mid"),
        "album_name": album.get("name"),
        "album_title": album.get("title"),
        "album_time_public": album.get("time_public"),
        "time_public": song.get("time_public") or album.get("time_public"),
        "singers": [
            {
                "id": singer.get("id"),
                "mid": singer.get("mid"),
                "name": singer.get("name"),
                "title": singer.get("title"),
                "pmid": singer.get("pmid"),
            }
            for singer in singers
        ],
        "source_singer_mid": source_singer.get("mid"),
        "source_singer_name": source_singer.get("name"),
        "is_filtered": filter_reason is not None,
        "filter_reason": filter_reason,
    }


def album_filter_reason(song: dict[str, Any]) -> str | None:
    album_name = normalize_spaces(str(song.get("album_name") or song.get("album_title") or ""))
    if not album_name:
        return "empty_album"
    return None


def song_key(song: dict[str, Any]) -> str:
    mid = song.get("mid")
    if mid:
        return f"mid:{mid}"
    song_id = song.get("id")
    if song_id is not None:
        return f"id:{song_id}"
    singers = ",".join(sorted(s.get("mid") or s.get("name") or "" for s in song.get("singers") or []))
    return f"name:{normalize_spaces(str(song.get('name') or song.get('title') or '')).lower()}|{singers}"


async def execute_or_load(client: Client, cache_path: Path, request: Any) -> Any:
    if cache_path.exists():
        return load_json(cache_path)
    result = await client.execute(request)
    payload = result.model_dump(mode="json") if hasattr(result, "model_dump") else result
    dump_json(cache_path, payload)
    return payload


async def collect_singers(client: Client, config: CollectConfig) -> list[dict[str, Any]]:
    if config.target_singer_mid is not None:
        return [
            {
                "id": None,
                "mid": config.target_singer_mid,
                "name": config.target_singer_name or config.target_singer_mid,
                "other_name": None,
                "spell": None,
                "singer_pic": None,
                "area_id": None,
                "country": None,
                "source": "manual.target_singer",
            }
        ]
    cache_path = config.raw_dir / "singers" / f"hot_singers_{config.singer_limit}.json"
    request = client.singer.get_singer_list_index(
        area=AreaType.ALL,
        sex=SexType.ALL,
        genre=GenreType.ALL,
        index=IndexType.ALL,
        page=1,
        num=config.singer_limit,
    )
    payload = await execute_or_load(client, cache_path, request)
    singers = payload.get("singerlist") or []
    return [compact_singer(singer) for singer in singers[: config.singer_limit]]


async def collect_singer_songs(client: Client, singer: dict[str, Any], config: CollectConfig) -> list[dict[str, Any]]:
    singer_mid = singer["mid"]
    cache_dir = config.raw_dir / "singer_songs" / singer_mid
    all_songs: list[dict[str, Any]] = []
    page = 1
    total_num: int | None = None

    while True:
        if config.max_pages_per_singer is not None and page > config.max_pages_per_singer:
            break
        cache_path = cache_dir / f"page_{page:04d}_size_{config.page_size}.json"
        request = client.singer.get_songs_list(singer_mid, num=config.page_size, page=page)
        payload = await execute_or_load(client, cache_path, request)
        songs = payload.get("song_list") or []
        if total_num is None:
            total_num = payload.get("total_num")
        all_songs.extend(songs)
        print(f"{singer['name']} page={page} songs={len(songs)} total={total_num}")
        if not songs:
            break
        if total_num is not None and len(all_songs) >= total_num:
            break
        if len(songs) < config.page_size:
            break
        page += 1

    compacted_songs = [compact_song(song, singer, None) for song in all_songs]
    for song in compacted_songs:
        reason = name_title_filter_reason(song)
        if reason is None:
            reason = album_filter_reason(song)
        if reason is None:
            reason = version_filter_reason(song)
        song["is_filtered"] = reason is not None
        song["filter_reason"] = reason
    return compacted_songs


def dedupe_songs(songs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[str, dict[str, Any]] = {}
    for song in songs:
        key = song_key(song)
        existing = deduped.get(key)
        if existing is None:
            song["source_singers"] = [
                {
                    "mid": song.pop("source_singer_mid"),
                    "name": song.pop("source_singer_name"),
                }
            ]
            deduped[key] = song
            continue
        existing.setdefault("source_singers", []).append(
            {
                "mid": song.get("source_singer_mid"),
                "name": song.get("source_singer_name"),
            }
        )
    return list(deduped.values())


def split_filter_results(songs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    kept_candidates = [song for song in songs if not song["is_filtered"]]
    filtered = [song for song in songs if song["is_filtered"]]
    return dedupe_songs(kept_candidates), filtered


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id",
        "mid",
        "name",
        "title",
        "album_name",
        "time_public",
        "singer_names",
        "is_filtered",
        "filter_reason",
        "source_singer_names",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "id": row.get("id"),
                    "mid": row.get("mid"),
                    "name": row.get("name"),
                    "title": row.get("title"),
                    "album_name": row.get("album_name"),
                    "time_public": row.get("time_public"),
                    "singer_names": " / ".join(s.get("name") or "" for s in row.get("singers") or []),
                    "is_filtered": row.get("is_filtered"),
                    "filter_reason": row.get("filter_reason"),
                    "source_singer_names": " / ".join(s.get("name") or "" for s in row.get("source_singers") or []),
                }
            )


async def run(config: CollectConfig) -> None:
    client = Client(rate=REQUEST_RATE, capacity=REQUEST_CAPACITY)
    try:
        singers = await collect_singers(client, config)
        all_songs: list[dict[str, Any]] = []
        for index, singer in enumerate(singers, 1):
            print(f"[{index}/{len(singers)}] collecting {singer['name']} ({singer['mid']})")
            all_songs.extend(await collect_singer_songs(client, singer, config))

        kept, filtered = split_filter_results(all_songs)
        snapshot = {
            "generated_at": now_iso(),
            "config": {
                "singer_limit": config.singer_limit,
                "page_size": config.page_size,
                "max_pages_per_singer": config.max_pages_per_singer,
            },
            "counts": {
                "singers": len(singers),
                "song_rows_before_dedupe": len(all_songs),
                "songs_after_filter_before_dedupe": len([song for song in all_songs if not song["is_filtered"]]),
                "songs_after_dedupe": len(kept),
                "songs_kept": len(kept),
                "songs_filtered": len(filtered),
            },
            "singers": singers,
            "songs": kept,
        }
        config.processed_dir.mkdir(parents=True, exist_ok=True)
        dump_json(config.processed_dir / "singer_song_snapshot.json", snapshot)
        dump_json(config.processed_dir / "singers.json", singers)
        dump_json(config.processed_dir / "songs_all.json", all_songs)
        dump_json(config.processed_dir / "songs_kept.json", kept)
        dump_json(config.processed_dir / "songs_filtered.json", filtered)
        write_csv(config.processed_dir / "songs_all.csv", all_songs)
        write_csv(config.processed_dir / "songs_kept.csv", kept)
        write_csv(config.processed_dir / "songs_filtered.csv", filtered)
        print(json.dumps(snapshot["counts"], ensure_ascii=False, indent=2))
        print(f"saved: {config.processed_dir / 'singer_song_snapshot.json'}")
    finally:
        await client.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect QQ Music hot singers and their songs.")
    parser.add_argument("--singer-limit", type=int, default=DEFAULT_SINGER_LIMIT)
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)
    parser.add_argument(
        "--max-pages-per-singer",
        type=int,
        default=None,
        help="Limit song pages per singer for smoke tests. Omit to fetch all pages.",
    )
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--target-singer-mid", type=str, default=None, help="Collect a single singer by singer mid.")
    parser.add_argument("--target-singer-name", type=str, default=None, help="Display name for --target-singer-mid.")
    return parser.parse_args()


def main() -> None:
    ensure_utf8_stdout()
    args = parse_args()
    config = CollectConfig(
        singer_limit=args.singer_limit,
        page_size=args.page_size,
        max_pages_per_singer=args.max_pages_per_singer,
        raw_dir=args.raw_dir,
        processed_dir=args.processed_dir,
        target_singer_mid=args.target_singer_mid,
        target_singer_name=decode_cli_text(args.target_singer_name),
    )
    asyncio.run(run(config))


if __name__ == "__main__":
    main()
