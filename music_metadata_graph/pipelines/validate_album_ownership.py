from __future__ import annotations

import argparse
import asyncio
import csv
import json
import re
import sys
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from qqmusic_api import Client


DEFAULT_INPUT = Path("data/processed/singer_songs/songs_kept.json")
DEFAULT_RAW_DIR = Path("data/raw/qqmusic")
DEFAULT_OUTPUT_DIR = Path("data/processed/album_validated")
REQUEST_RATE = 0.5
REQUEST_CAPACITY = 1

VERSION_KEYWORDS = (
    "醇享版",
    "instrumental",
    "inst.",
    "inst",
    "slowed",
    "reverb",
    "sped up",
    "remix",
    "伴奏",
    "纯音乐",
    "karaoke",
    "demo",
    "live",
    "现场",
    "演唱会",
    "片段",
    "试听",
    "铃声",
    "cover",
    "翻唱",
)
WEAK_GENERIC_ALBUM_SINGER_NAMES = (
    "华语群星",
    "群星",
)
STRONG_GENERIC_ALBUM_SINGER_NAMES = (
    "古典音乐",
    "飞天猫",
    "2018中国好声音",
)
SUSPICIOUS_ALBUM_TITLE_KEYWORDS = (
    "混剪",
    "翻唱",
    "cover",
    "伴奏",
    "纯音乐",
    "remix",
    "醇享",
)
SUSPICIOUS_ALBUM_LANGUAGE_KEYWORDS = ("纯音乐",)


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


def normalize_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_text(value: str) -> str:
    return unicodedata.normalize("NFKC", value or "").casefold()


def has_keyword(value: str, keywords: tuple[str, ...]) -> str | None:
    text = normalize_text(value)
    for keyword in keywords:
        if normalize_text(keyword) in text:
            return keyword
    return None


def compact_title_key(value: str) -> str:
    text = normalize_text(value)
    return re.sub(r"[\W_]+", "", text, flags=re.UNICODE)


def remove_version_brackets(value: str) -> str:
    text = value or ""

    def replace(match: re.Match[str]) -> str:
        inner = match.group(1)
        return "" if has_keyword(inner, VERSION_KEYWORDS) else match.group(0)

    text = re.sub(r"[\(（\[]([^()\[\]（）]+)[\)）\]]", replace, text)
    return normalize_spaces(text)


def title_text(song: dict[str, Any]) -> str:
    parts = [
        str(song.get("name") or ""),
        str(song.get("title") or ""),
        str(song.get("subtitle") or ""),
    ]
    return normalize_spaces(" ".join(part for part in parts if part))


def song_base_key(song: dict[str, Any]) -> str:
    title = str(song.get("title") or song.get("name") or "")
    stripped = remove_version_brackets(title)
    key = compact_title_key(stripped)
    if key:
        return key
    return compact_title_key(str(song.get("name") or title))


def version_marker(song: dict[str, Any]) -> str | None:
    title_marker = has_keyword(title_text(song), VERSION_KEYWORDS)
    if title_marker:
        return title_marker
    album_title = " ".join(
        str(song.get(field) or "")
        for field in ("album_name", "album_title")
    )
    return has_keyword(album_title, VERSION_KEYWORDS)


def singer_names(singers: list[dict[str, Any]]) -> list[str]:
    return [str(singer.get("name") or singer.get("title") or "") for singer in singers]


def singer_mids(singers: list[dict[str, Any]]) -> list[str]:
    return [str(singer.get("mid") or "") for singer in singers]


def target_matches_singers(
    singers: list[dict[str, Any]],
    target_mids: set[str],
    target_names: set[str],
) -> bool:
    mids = set(singer_mids(singers))
    names = set(singer_names(singers))
    return bool((target_mids and mids.intersection(target_mids)) or (target_names and names.intersection(target_names)))


def compact_album_detail(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not payload:
        return {
            "album": {},
            "company": {},
            "singers": [],
        }
    album = payload.get("album") or {}
    company = payload.get("company") or {}
    singers = payload.get("singers") or []
    return {
        "album": {
            "id": album.get("id"),
            "mid": album.get("mid"),
            "name": album.get("name"),
            "title": album.get("title"),
            "time_public": album.get("time_public"),
            "language": album.get("language"),
            "album_type": album.get("album_type"),
            "genre": album.get("genre"),
            "desc": album.get("desc"),
        },
        "company": {
            "id": company.get("id"),
            "name": company.get("name"),
            "is_show": company.get("is_show"),
        },
        "singers": [
            {
                "id": singer.get("id"),
                "mid": singer.get("mid"),
                "name": singer.get("name"),
                "title": singer.get("title"),
            }
            for singer in singers
        ],
    }


async def execute_or_load(client: Client, cache_path: Path, request: Any) -> Any:
    if cache_path.exists():
        return load_json(cache_path)
    result = await client.execute(request)
    payload = result.model_dump(mode="json") if hasattr(result, "model_dump") else result
    dump_json(cache_path, payload)
    return payload


async def collect_album_details(
    client: Client,
    songs: list[dict[str, Any]],
    raw_dir: Path,
) -> dict[str, dict[str, Any]]:
    details: dict[str, dict[str, Any]] = {}
    album_mids = sorted({str(song.get("album_mid") or "") for song in songs if song.get("album_mid")})
    for index, album_mid in enumerate(album_mids, 1):
        cache_path = raw_dir / "albums" / f"{album_mid}.json"
        payload = await execute_or_load(client, cache_path, client.album.get_detail(album_mid))
        details[album_mid] = compact_album_detail(payload)
        album_name = (details[album_mid].get("album") or {}).get("name") or album_mid
        print(f"[{index}/{len(album_mids)}] album={album_name} ({album_mid})")
    return details


def build_original_base_keys(songs: list[dict[str, Any]]) -> set[str]:
    originals: set[str] = set()
    for song in songs:
        marker = version_marker(song)
        if marker is None:
            originals.add(song_base_key(song))
    return originals


def album_suspicion_reasons(album_detail: dict[str, Any]) -> list[str]:
    album = album_detail.get("album") or {}
    company = album_detail.get("company") or {}
    album_singers = album_detail.get("singers") or []
    reasons: list[str] = []
    names = singer_names(album_singers)
    for name in names:
        if name in STRONG_GENERIC_ALBUM_SINGER_NAMES:
            reasons.append(f"strong_generic_album_singer:{name}")
        elif name in WEAK_GENERIC_ALBUM_SINGER_NAMES:
            reasons.append(f"weak_generic_album_singer:{name}")
    album_name = str(album.get("name") or album.get("title") or "")
    title_keyword = has_keyword(album_name, SUSPICIOUS_ALBUM_TITLE_KEYWORDS)
    if title_keyword:
        reasons.append(f"suspicious_album_title:{title_keyword}")
    language_keyword = has_keyword(str(album.get("language") or ""), SUSPICIOUS_ALBUM_LANGUAGE_KEYWORDS)
    if language_keyword:
        reasons.append(f"suspicious_album_language:{language_keyword}")
    company_name = str(company.get("name") or "")
    if not company_name:
        reasons.append("empty_album_company")
    desc = str(album.get("desc") or "")
    if "混剪" in desc or "侵权" in desc:
        reasons.append("suspicious_album_desc")
    return reasons


def strong_album_suspicion_reasons(reasons: list[str]) -> list[str]:
    return [
        reason
        for reason in reasons
        if reason.startswith("strong_generic_album_singer:")
        or reason.startswith("suspicious_album_title:")
        or reason.startswith("suspicious_album_language:")
        or reason == "suspicious_album_desc"
    ]


def validate_song(
    song: dict[str, Any],
    album_detail: dict[str, Any],
    original_base_keys: set[str],
    target_mids: set[str],
    target_names: set[str],
) -> dict[str, Any]:
    marker = version_marker(song)
    base_key = song_base_key(song)
    album = album_detail.get("album") or {}
    company = album_detail.get("company") or {}
    album_singers = album_detail.get("singers") or []
    album_owner_match = target_matches_singers(album_singers, target_mids, target_names)
    song_singer_match = target_matches_singers(song.get("singers") or [], target_mids, target_names)
    suspicion_reasons = album_suspicion_reasons(album_detail)
    strong_suspicion_reasons = strong_album_suspicion_reasons(suspicion_reasons)
    reasons: list[str] = []

    if marker is not None and base_key in original_base_keys:
        reasons.append(f"version_duplicate:{marker}")
    if not album_owner_match:
        if strong_suspicion_reasons:
            reasons.append("strong_album_owner_mismatch")
            reasons.extend(suspicion_reasons)
        elif song_singer_match:
            reasons.append("review_album_owner_mismatch")
            reasons.extend(suspicion_reasons)
        else:
            reasons.append("weak_album_owner_mismatch")
            reasons.extend(suspicion_reasons)

    if any(reason.startswith("version_duplicate:") for reason in reasons):
        decision = "rejected"
    elif "strong_album_owner_mismatch" in reasons:
        decision = "rejected"
    elif "review_album_owner_mismatch" in reasons or "weak_album_owner_mismatch" in reasons:
        decision = "review"
    else:
        decision = "kept"

    enriched = dict(song)
    enriched["album_validation"] = {
        "decision": decision,
        "reasons": reasons,
        "base_key": base_key,
        "version_marker": marker,
        "album_owner_match": album_owner_match,
        "song_singer_match": song_singer_match,
        "album_singers": album_singers,
        "album_type": album.get("album_type"),
        "album_language": album.get("language"),
        "album_company": company.get("name"),
    }
    return enriched


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "decision",
        "reasons",
        "name",
        "title",
        "time_public",
        "singer_names",
        "album_name",
        "album_singers",
        "album_company",
        "album_type",
        "album_language",
        "id",
        "mid",
        "album_mid",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            validation = row.get("album_validation") or {}
            writer.writerow(
                {
                    "decision": validation.get("decision"),
                    "reasons": "; ".join(validation.get("reasons") or []),
                    "name": row.get("name"),
                    "title": row.get("title"),
                    "time_public": row.get("time_public"),
                    "singer_names": " / ".join(singer_names(row.get("singers") or [])),
                    "album_name": row.get("album_name"),
                    "album_singers": " / ".join(singer_names(validation.get("album_singers") or [])),
                    "album_company": validation.get("album_company"),
                    "album_type": validation.get("album_type"),
                    "album_language": validation.get("album_language"),
                    "id": row.get("id"),
                    "mid": row.get("mid"),
                    "album_mid": row.get("album_mid"),
                }
            )


def markdown_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "&#124;").replace("\r", " ").replace("\n", " ")


def write_song_report(path: Path, rows: list[dict[str, Any]], title: str, limit: int | None = None) -> None:
    report_rows = rows if limit is None else rows[:limit]
    lines = [
        f"# {title}",
        "",
        f"Rows: {len(rows)}",
        "",
        "| Reason | Song | Title | Album | Album singers | Company | song_id | song_mid |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report_rows:
        validation = row.get("album_validation") or {}
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_escape("; ".join(validation.get("reasons") or [])),
                    markdown_escape(row.get("name")),
                    markdown_escape(row.get("title")),
                    markdown_escape(row.get("album_name")),
                    markdown_escape(" / ".join(singer_names(validation.get("album_singers") or []))),
                    markdown_escape(validation.get("album_company")),
                    markdown_escape(row.get("id")),
                    markdown_escape(row.get("mid")),
                ]
            )
            + " |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(("\r\n".join(lines) + "\r\n").encode("utf-8"))


def infer_targets(songs: list[dict[str, Any]], target_mid: str | None, target_name: str | None) -> tuple[set[str], set[str]]:
    mids: set[str] = set()
    names: set[str] = set()
    if target_mid:
        mids.add(target_mid)
    if target_name:
        names.add(target_name)
    if mids or names:
        return mids, names
    source_singers = songs[0].get("source_singers") or [] if songs else []
    for singer in source_singers:
        if singer.get("mid"):
            mids.add(str(singer["mid"]))
        if singer.get("name"):
            names.add(str(singer["name"]))
    return mids, names


async def run(args: argparse.Namespace) -> None:
    songs = load_json(args.input)
    target_mids, target_names = infer_targets(songs, args.target_mid, args.target_name)
    client = Client(rate=REQUEST_RATE, capacity=REQUEST_CAPACITY)
    try:
        album_details = await collect_album_details(client, songs, args.raw_dir)
    finally:
        await client.close()

    original_base_keys = build_original_base_keys(songs)
    validated = [
        validate_song(
            song=song,
            album_detail=album_details.get(str(song.get("album_mid") or ""), {}),
            original_base_keys=original_base_keys,
            target_mids=target_mids,
            target_names=target_names,
        )
        for song in songs
    ]
    kept = [song for song in validated if song["album_validation"]["decision"] == "kept"]
    rejected = [song for song in validated if song["album_validation"]["decision"] == "rejected"]
    review = [song for song in validated if song["album_validation"]["decision"] == "review"]
    reason_counts = Counter(
        reason
        for song in validated
        for reason in song["album_validation"]["reasons"]
    )
    snapshot = {
        "generated_at": now_iso(),
        "input": str(args.input),
        "target": {
            "mids": sorted(target_mids),
            "names": sorted(target_names),
        },
        "counts": {
            "input_songs": len(songs),
            "albums_checked": len(album_details),
            "kept": len(kept),
            "rejected": len(rejected),
            "review": len(review),
        },
        "reason_counts": dict(reason_counts.most_common()),
        "songs": kept,
        "rejected_songs": rejected,
        "review_songs": review,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    dump_json(args.output_dir / "album_validation_snapshot.json", snapshot)
    dump_json(args.output_dir / "songs_album_validated_all.json", validated)
    dump_json(args.output_dir / "songs_kept_album_validated.json", kept)
    dump_json(args.output_dir / "songs_rejected_album_validated.json", rejected)
    dump_json(args.output_dir / "songs_review_album_validated.json", review)
    write_csv(args.output_dir / "songs_album_validated_all.csv", validated)
    write_csv(args.output_dir / "songs_kept_album_validated.csv", kept)
    write_csv(args.output_dir / "songs_rejected_album_validated.csv", rejected)
    write_csv(args.output_dir / "songs_review_album_validated.csv", review)
    write_song_report(args.output_dir / "songs_rejected_album_validated.md", rejected, "Album validation rejected songs")
    write_song_report(args.output_dir / "songs_review_album_validated.md", review, "Album validation review songs")
    print(json.dumps(snapshot["counts"], ensure_ascii=False, indent=2))
    print(json.dumps(snapshot["reason_counts"], ensure_ascii=False, indent=2))
    print(f"saved: {args.output_dir / 'album_validation_snapshot.json'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate kept songs by QQ Music album ownership details.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--target-mid", type=str, default=None)
    parser.add_argument("--target-name", type=str, default=None)
    return parser.parse_args()


def main() -> None:
    ensure_utf8_stdout()
    asyncio.run(run(parse_args()))


if __name__ == "__main__":
    main()
