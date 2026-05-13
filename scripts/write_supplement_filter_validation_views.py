from __future__ import annotations

import asyncio
import csv
import json
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

from pypinyin import Style, lazy_pinyin
from qqmusic_api import Client


ROOT = Path(__file__).resolve().parents[1]
VALIDATION_ROOT = ROOT / "data/processed/validation/four_singers"
RAW_ROOT = ROOT / "data/raw/qqmusic/singer_homepage_song_tab"
ALBUM_DETAIL_RAW_ROOT = ROOT / "data/raw/qqmusic/supplement_album_details"
JSON_ROOT = VALIDATION_ROOT / "json_outputs"
CSV_ROOT = VALIDATION_ROOT / "csv_views"
SUPPLEMENT_JSON = JSON_ROOT / "supplement_singer_songs"
SUPPLEMENT_CSV = CSV_ROOT / "supplement_singer_songs"
HIGH_CONFIDENCE_JSON = JSON_ROOT / "high_confidence_singer_songs"
ALLOWED_SUPPLEMENT_ALBUM_TYPES = {"Single", "EP", "录音室专辑"}

SINGERS = [
    ("zhoujielun", "周杰伦", "0025NhlN2yWrP4"),
    ("xuezhiqian", "薛之谦", "002J4UUk29y8BY"),
    ("linjunjie", "林俊杰", "001BLpXF2DyJe2"),
    ("wangsulong", "汪苏泷", "001z2JmX09LLgL"),
]

SONG_RAW_FIELDS = [
    "id",
    "type",
    "mid",
    "name",
    "title",
    "subtitle",
    "singer",
    "album",
    "mv",
    "interval",
    "isonly",
    "language",
    "genre",
    "index_cd",
    "index_album",
    "time_public",
    "status",
    "fnote",
    "file",
    "pay",
    "action",
    "ksong",
    "volume",
    "label",
    "url",
    "bpm",
    "version",
    "trace",
    "data_type",
    "modify_stamp",
    "pingpong",
    "aid",
    "ppurl",
    "tid",
    "ov",
    "sa",
    "es",
    "vs",
    "vi",
    "ktag",
    "vf",
    "va",
]
SONG_AUX_FIELDS = [
    "aux_target_singer",
    "aux_target_singer_mid",
    "aux_sort_key",
    "aux_song_key",
    "aux_diff_name_key",
    "aux_filter_step",
    "aux_filter_result",
    "aux_filter_reason",
    "aux_set_relation",
    "aux_duplicate_count_in_full",
    "aux_duplicate_sources",
    "aux_album_detail_request_key",
    "aux_album_detail_request_status",
    "aux_album_detail_id",
    "aux_album_detail_mid",
    "aux_album_detail_name",
    "aux_album_detail_subtitle",
    "aux_album_detail_type",
    "aux_album_detail_singer_names",
    "aux_album_detail_singer_mids",
    "aux_album_detail_company_name",
    "aux_album_detail_language",
    "aux_album_detail_genre",
    "aux_album_detail_public_time",
    "aux_album_detail_desc",
    "aux_album_detail_cache_file",
    "aux_filter4_name_key",
    "aux_filter4_name_group_size",
    "aux_filter4_name_preferred_album_type",
    "aux_filter4_name_preferred_song_id",
    "aux_filter4_selected_song_key",
    "aux_filter4_selected_album_type",
    "aux_filter4_selected_song_id",
    "aux_raw_cache_file",
    "aux_source",
]
SONG_FIELDS = SONG_RAW_FIELDS + SONG_AUX_FIELDS
SONG_CSV_FIELDS = [field for field in SONG_FIELDS if field != "aux_album_detail_desc"]


def normalize_text(value: Any) -> str:
    return unicodedata.normalize("NFKC", str(value or "")).casefold().strip()


def sort_key(value: Any) -> str:
    return " ".join(lazy_pinyin(normalize_text(value), style=Style.NORMAL, errors="default"))


def song_singers(song: dict[str, Any]) -> list[dict[str, Any]]:
    return list(song.get("singer") or song.get("singers") or [])


def song_key(song: dict[str, Any]) -> str:
    mid = song.get("mid")
    if mid:
        return f"mid:{mid}"
    song_id = song.get("id")
    if song_id is not None:
        return f"id:{song_id}"
    return ""


def name_key(song: dict[str, Any]) -> str:
    return normalize_text(song.get("name") or "")


def album_filter_reason(song: dict[str, Any]) -> str | None:
    album = song.get("album")
    if not isinstance(album, dict):
        return "empty_album"
    album_name = normalize_text(album.get("name") or album.get("title") or album.get("subtitle") or "")
    return None if album_name else "empty_album"


def album_key(row: dict[str, Any]) -> str:
    album = row.get("album") if isinstance(row.get("album"), dict) else {}
    return str(album.get("mid") or album.get("id") or "")


def album_identity_filter_reason(row: dict[str, Any]) -> str | None:
    return None if album_key(row) else "missing_album_mid_and_id"


def extract_album_detail(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
        return data if isinstance(data, dict) else {}
    return {}


def detail_text(payload: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = payload.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def album_detail_type(row: dict[str, Any]) -> str:
    return str(row.get("aux_album_detail_type") or "")


def album_type_filter_reason(row: dict[str, Any]) -> str | None:
    album_type = album_detail_type(row)
    if album_type in ALLOWED_SUPPLEMENT_ALBUM_TYPES:
        return None
    return f"excluded_album_type:{album_type or 'missing'}"


def dedupe_album_type_priority(row: dict[str, Any]) -> int:
    return {"录音室专辑": 0, "EP": 1, "Single": 2}.get(album_detail_type(row), 3)


def numeric_song_id(row: dict[str, Any]) -> int:
    try:
        return int(row.get("id") or 0)
    except (TypeError, ValueError):
        return 0


def compact_raw_song(song: dict[str, Any], target_name: str, target_mid: str, cache_file: Path) -> dict[str, Any]:
    row = dict(song)
    row.update(
        {
            "aux_target_singer": target_name,
            "aux_target_singer_mid": target_mid,
            "aux_sort_key": sort_key(song.get("name") or song.get("title") or ""),
            "aux_song_key": song_key(song),
            "aux_diff_name_key": name_key(song),
            "aux_raw_cache_file": cache_file.relative_to(ROOT).as_posix(),
            "aux_source": "qqmusic.singer.get_tab_detail.song_sing",
        }
    )
    return row


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_raw_songs(target_mid: str, target_name: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted((RAW_ROOT / target_mid).glob("page_*.json")):
        payload = load_json(path)
        for song in (((payload.get("SongTab") or {}).get("List")) or []):
            rows.append(compact_raw_song(song, target_name, target_mid, path))
    return rows


async def fetch_album_detail(client: Client, key: str) -> tuple[dict[str, Any] | None, str, str]:
    cache_path = ALBUM_DETAIL_RAW_ROOT / f"{key}.json"
    if cache_path.exists():
        return load_json(cache_path), "cache_hit", cache_path.relative_to(ROOT).as_posix()
    try:
        result = await client.execute(client.album.get_detail(key))
        payload = result.model_dump(mode="json") if hasattr(result, "model_dump") else result
        dump_json(cache_path, payload)
        await asyncio.sleep(0.35)
        return payload, "fetched", cache_path.relative_to(ROOT).as_posix()
    except Exception as exc:  # noqa: BLE001 - keep row-level failure details in validation outputs.
        return None, f"error:{type(exc).__name__}:{exc}", ""


async def enrich_album_details(client: Client, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    details: dict[str, tuple[dict[str, Any] | None, str, str]] = {}
    enriched: list[dict[str, Any]] = []
    for source_row in rows:
        row = dict(source_row)
        key = album_key(row)
        row["aux_album_detail_request_key"] = key
        if not key:
            row["aux_album_detail_request_status"] = "missing_album_mid_and_id"
            enriched.append(row)
            continue
        if key not in details:
            details[key] = await fetch_album_detail(client, key)
        payload, status, cache_file = details[key]
        detail = extract_album_detail(payload)
        detail_album = detail.get("album") if isinstance(detail.get("album"), dict) else {}
        detail_company = detail.get("company") if isinstance(detail.get("company"), dict) else {}
        detail_singers = detail.get("singers") if isinstance(detail.get("singers"), list) else []
        row.update(
            {
                "aux_album_detail_request_status": status,
                "aux_album_detail_id": detail_text(detail_album, "albumID", "albumId", "id"),
                "aux_album_detail_mid": detail_text(detail_album, "albumMid", "mid"),
                "aux_album_detail_name": detail_text(detail_album, "albumName", "name", "title"),
                "aux_album_detail_subtitle": detail_text(detail_album, "subtitle"),
                "aux_album_detail_type": detail_text(detail_album, "albumType", "type", "album_type"),
                "aux_album_detail_singer_names": "; ".join(
                    str(singer.get("name") or singer.get("title") or "") for singer in detail_singers if isinstance(singer, dict)
                ),
                "aux_album_detail_singer_mids": "; ".join(
                    str(singer.get("mid") or "") for singer in detail_singers if isinstance(singer, dict)
                ),
                "aux_album_detail_company_name": detail_text(detail_company, "name"),
                "aux_album_detail_language": detail_text(detail_album, "lan", "language"),
                "aux_album_detail_genre": detail_text(detail_album, "genre"),
                "aux_album_detail_public_time": detail_text(detail_album, "aDate", "publishDate", "time_public"),
                "aux_album_detail_desc": detail_text(detail_album, "desc", "description"),
                "aux_album_detail_cache_file": cache_file,
            }
        )
        enriched.append(row)
    return enriched


def duplicate_sources(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "mid": row.get("mid"),
            "id": row.get("id"),
            "name": row.get("name"),
            "aux_album_detail_type": row.get("aux_album_detail_type"),
            "aux_raw_cache_file": row.get("aux_raw_cache_file"),
        }
        for row in rows
    ]


def dedupe_by_song_key(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_key: dict[str, dict[str, Any]] = {}
    groups: dict[str, list[dict[str, Any]]] = {}
    duplicates: list[dict[str, Any]] = []
    for row in rows:
        key = row["aux_song_key"]
        if not key:
            duplicate = dict(row)
            duplicate["aux_filter_step"] = "supplement_branch_filter4_dedupe"
            duplicate["aux_filter_result"] = "removed"
            duplicate["aux_filter_reason"] = "missing_song_mid_and_id"
            duplicate["aux_set_relation"] = "supplement_removed_by_filter4_missing_song_identity"
            duplicates.append(duplicate)
            continue
        groups.setdefault(key, []).append(row)
        if key not in by_key:
            by_key[key] = row
            continue
        duplicate = dict(row)
        duplicate["aux_filter_step"] = "supplement_branch_filter4_dedupe"
        duplicate["aux_filter_result"] = "removed"
        duplicate["aux_filter_reason"] = "duplicate_song_key_in_songs_after_filter3_album_type"
        duplicate["aux_set_relation"] = "supplement_removed_by_filter4_duplicate"
        duplicates.append(duplicate)

    for key, group in groups.items():
        source_rows = duplicate_sources(group)
        by_key[key]["aux_duplicate_count_in_full"] = len(group)
        by_key[key]["aux_duplicate_sources"] = source_rows
    for duplicate in duplicates:
        group = groups[duplicate["aux_song_key"]]
        duplicate["aux_duplicate_count_in_full"] = len(group)
        duplicate["aux_duplicate_sources"] = duplicate_sources(group)
    return list(by_key.values()), duplicates


def dedupe_by_song_name(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    groups: dict[str, list[tuple[int, dict[str, Any]]]] = {}
    for index, row in enumerate(rows):
        key = name_key(row)
        row["aux_filter4_name_key"] = key
        groups.setdefault(key, []).append((index, row))

    kept: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    for key, indexed_group in groups.items():
        if len(indexed_group) == 1:
            kept.append(indexed_group[0][1])
            continue
        _, selected = min(indexed_group, key=lambda item: (dedupe_album_type_priority(item[1]), numeric_song_id(item[1]), item[0]))
        selected_key = song_key(selected)
        selected["aux_filter4_name_group_size"] = len(indexed_group)
        selected["aux_filter4_name_preferred_album_type"] = album_detail_type(selected)
        selected["aux_filter4_name_preferred_song_id"] = numeric_song_id(selected)
        kept.append(selected)
        for _, row in indexed_group:
            if row is selected:
                continue
            duplicate = dict(row)
            duplicate["aux_filter_step"] = "supplement_branch_filter4_dedupe"
            duplicate["aux_filter_result"] = "removed"
            duplicate["aux_filter_reason"] = "duplicate_song_name_prefer_recording_album_then_ep_then_single_then_lowest_id"
            duplicate["aux_filter4_name_key"] = key
            duplicate["aux_filter4_name_group_size"] = len(indexed_group)
            duplicate["aux_filter4_selected_song_key"] = selected_key
            duplicate["aux_filter4_selected_album_type"] = album_detail_type(selected)
            duplicate["aux_filter4_selected_song_id"] = numeric_song_id(selected)
            duplicate["aux_set_relation"] = "supplement_removed_by_filter4_duplicate_name"
            removed.append(duplicate)
    return kept, removed


def dedupe_full(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    key_deduped, key_duplicates = dedupe_by_song_key(rows)
    name_deduped, name_duplicates = dedupe_by_song_name(key_deduped)
    return name_deduped, key_duplicates + name_duplicates


def load_high_confidence_name_keys(slug: str) -> set[str]:
    rows = load_json(HIGH_CONFIDENCE_JSON / slug / "songs_after_filter2_dedupe.json")
    return {name_key(row) for row in rows if name_key(row)}


def sorted_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            str(row.get("aux_target_singer") or ""),
            str(row.get("aux_sort_key") or ""),
            str(row.get("time_public") or ""),
            str(row.get("mid") or row.get("id") or ""),
        ),
    )


def csv_cell(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return value


def row_fieldnames(rows: list[dict[str, Any]], preferred: list[str], include_extra: bool = True) -> list[str]:
    seen: set[str] = set()
    fields: list[str] = []
    for field in preferred:
        if field in seen:
            continue
        if any(field in row for row in rows):
            seen.add(field)
            fields.append(field)
    if not include_extra:
        return fields
    for row in rows:
        for field in row:
            if field not in seen:
                seen.add(field)
                fields.append(field)
    return fields


def write_csv(path: Path, rows: list[dict[str, Any]], preferred_fields: list[str], include_extra: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = row_fieldnames(rows, preferred_fields, include_extra=include_extra) if rows else list(dict.fromkeys(preferred_fields))
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows([{key: csv_cell(row.get(key)) for key in fieldnames} for row in rows])


def cleanup_song_output_files(path: Path) -> None:
    keep = {
        "songs_all.json",
        "songs_all.csv",
        "songs_after_filter1_empty_album_exclusion.json",
        "songs_after_filter1_empty_album_exclusion.csv",
        "songs_removed_by_filter1_empty_album_exclusion.json",
        "songs_removed_by_filter1_empty_album_exclusion.csv",
        "songs_after_filter2_album_identity.json",
        "songs_after_filter2_album_identity.csv",
        "songs_removed_by_filter2_album_identity.json",
        "songs_removed_by_filter2_album_identity.csv",
        "songs_after_album_detail_enrich.json",
        "songs_after_album_detail_enrich.csv",
        "songs_after_filter3_album_type.json",
        "songs_after_filter3_album_type.csv",
        "songs_removed_by_filter3_album_type.json",
        "songs_removed_by_filter3_album_type.csv",
        "songs_after_filter4_dedupe.json",
        "songs_after_filter4_dedupe.csv",
        "songs_removed_by_filter4_dedupe.json",
        "songs_removed_by_filter4_dedupe.csv",
        "songs_after_filter5_high_confidence_name_exclusion.json",
        "songs_after_filter5_high_confidence_name_exclusion.csv",
        "songs_removed_by_filter5_high_confidence_name_exclusion.json",
        "songs_removed_by_filter5_high_confidence_name_exclusion.csv",
        "high_confidence_name_filter_summary.json",
    }
    if not path.exists():
        return
    for file in path.iterdir():
        if file.is_file() and file.name not in keep:
            file.unlink(missing_ok=True)


def split_by_filter1(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    kept: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    for source_row in rows:
        row = dict(source_row)
        row["aux_filter_step"] = "supplement_branch_filter1_empty_album_exclusion"
        reason = album_filter_reason(row)
        if reason is not None:
            row["aux_filter_result"] = "removed"
            row["aux_filter_reason"] = reason
            row["aux_set_relation"] = "supplement_removed_by_filter1_empty_album_exclusion"
            removed.append(row)
        else:
            row["aux_filter_result"] = "kept"
            row["aux_filter_reason"] = ""
            row["aux_set_relation"] = "supplement_after_filter1_empty_album_exclusion"
            kept.append(row)
    return sorted_rows(kept), sorted_rows(removed)


def split_by_filter2(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    kept: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    for source_row in rows:
        row = dict(source_row)
        row["aux_filter_step"] = "supplement_branch_filter2_album_identity"
        reason = album_identity_filter_reason(row)
        if reason is not None:
            row["aux_filter_result"] = "removed"
            row["aux_filter_reason"] = reason
            row["aux_set_relation"] = "supplement_removed_by_filter2_album_identity"
            removed.append(row)
        else:
            row["aux_filter_result"] = "kept"
            row["aux_filter_reason"] = ""
            row["aux_set_relation"] = "supplement_after_filter2_album_identity"
            kept.append(row)
    return sorted_rows(kept), sorted_rows(removed)


def split_by_filter3(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    kept: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    for source_row in rows:
        row = dict(source_row)
        row["aux_filter_step"] = "supplement_branch_filter3_album_type"
        reason = album_type_filter_reason(row)
        if reason is not None:
            row["aux_filter_result"] = "removed"
            row["aux_filter_reason"] = reason
            row["aux_set_relation"] = "supplement_removed_by_filter3_album_type"
            removed.append(row)
        else:
            row["aux_filter_result"] = "kept"
            row["aux_filter_reason"] = ""
            row["aux_set_relation"] = "supplement_after_filter3_album_type"
            kept.append(row)
    return sorted_rows(kept), sorted_rows(removed)


def split_by_filter5(
    rows: list[dict[str, Any]],
    high_confidence_name_keys: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    kept: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    for source_row in rows:
        row = dict(source_row)
        row["aux_filter_step"] = "supplement_branch_filter5_high_confidence_name_exclusion"
        if row["aux_diff_name_key"] in high_confidence_name_keys:
            row["aux_filter_result"] = "removed"
            row["aux_filter_reason"] = "song_name_exists_in_high_confidence_dedupe"
            row["aux_set_relation"] = "supplement_removed_by_filter5_high_confidence_name_exclusion"
            removed.append(row)
        else:
            row["aux_filter_result"] = "kept"
            row["aux_filter_reason"] = ""
            row["aux_set_relation"] = "supplement_after_filter5_high_confidence_name_exclusion"
            kept.append(row)
    return sorted_rows(kept), sorted_rows(removed)


def write_song_outputs(
    slug: str,
    all_rows: list[dict[str, Any]],
    songs_after_filter1_empty_album_exclusion: list[dict[str, Any]],
    songs_removed_by_filter1_empty_album_exclusion: list[dict[str, Any]],
    songs_after_filter2_album_identity: list[dict[str, Any]],
    songs_removed_by_filter2_album_identity: list[dict[str, Any]],
    songs_after_album_detail_enrich: list[dict[str, Any]],
    songs_after_filter3_album_type: list[dict[str, Any]],
    songs_removed_by_filter3_album_type: list[dict[str, Any]],
    songs_after_filter4_dedupe: list[dict[str, Any]],
    songs_removed_by_filter4_dedupe: list[dict[str, Any]],
    songs_after_filter5_high_confidence_name_exclusion: list[dict[str, Any]],
    songs_removed_by_filter5_high_confidence_name_exclusion: list[dict[str, Any]],
) -> None:
    json_dir = SUPPLEMENT_JSON / slug
    csv_dir = SUPPLEMENT_CSV / slug
    cleanup_song_output_files(json_dir)
    cleanup_song_output_files(csv_dir)
    dump_json(json_dir / "songs_all.json", all_rows)
    dump_json(json_dir / "songs_after_filter1_empty_album_exclusion.json", songs_after_filter1_empty_album_exclusion)
    dump_json(json_dir / "songs_removed_by_filter1_empty_album_exclusion.json", songs_removed_by_filter1_empty_album_exclusion)
    dump_json(json_dir / "songs_after_filter2_album_identity.json", songs_after_filter2_album_identity)
    dump_json(json_dir / "songs_removed_by_filter2_album_identity.json", songs_removed_by_filter2_album_identity)
    dump_json(json_dir / "songs_after_album_detail_enrich.json", songs_after_album_detail_enrich)
    dump_json(json_dir / "songs_after_filter3_album_type.json", songs_after_filter3_album_type)
    dump_json(json_dir / "songs_removed_by_filter3_album_type.json", songs_removed_by_filter3_album_type)
    dump_json(json_dir / "songs_after_filter4_dedupe.json", songs_after_filter4_dedupe)
    dump_json(json_dir / "songs_removed_by_filter4_dedupe.json", songs_removed_by_filter4_dedupe)
    dump_json(json_dir / "songs_after_filter5_high_confidence_name_exclusion.json", songs_after_filter5_high_confidence_name_exclusion)
    dump_json(json_dir / "songs_removed_by_filter5_high_confidence_name_exclusion.json", songs_removed_by_filter5_high_confidence_name_exclusion)
    write_csv(csv_dir / "songs_all.csv", all_rows, SONG_CSV_FIELDS, include_extra=False)
    write_csv(csv_dir / "songs_after_filter1_empty_album_exclusion.csv", songs_after_filter1_empty_album_exclusion, SONG_CSV_FIELDS, include_extra=False)
    write_csv(csv_dir / "songs_removed_by_filter1_empty_album_exclusion.csv", songs_removed_by_filter1_empty_album_exclusion, SONG_CSV_FIELDS, include_extra=False)
    write_csv(csv_dir / "songs_after_filter2_album_identity.csv", songs_after_filter2_album_identity, SONG_CSV_FIELDS, include_extra=False)
    write_csv(csv_dir / "songs_removed_by_filter2_album_identity.csv", songs_removed_by_filter2_album_identity, SONG_CSV_FIELDS, include_extra=False)
    write_csv(csv_dir / "songs_after_album_detail_enrich.csv", songs_after_album_detail_enrich, SONG_CSV_FIELDS, include_extra=False)
    write_csv(csv_dir / "songs_after_filter3_album_type.csv", songs_after_filter3_album_type, SONG_CSV_FIELDS, include_extra=False)
    write_csv(csv_dir / "songs_removed_by_filter3_album_type.csv", songs_removed_by_filter3_album_type, SONG_CSV_FIELDS, include_extra=False)
    write_csv(csv_dir / "songs_after_filter4_dedupe.csv", songs_after_filter4_dedupe, SONG_CSV_FIELDS, include_extra=False)
    write_csv(csv_dir / "songs_removed_by_filter4_dedupe.csv", songs_removed_by_filter4_dedupe, SONG_CSV_FIELDS, include_extra=False)
    write_csv(csv_dir / "songs_after_filter5_high_confidence_name_exclusion.csv", songs_after_filter5_high_confidence_name_exclusion, SONG_CSV_FIELDS, include_extra=False)
    write_csv(csv_dir / "songs_removed_by_filter5_high_confidence_name_exclusion.csv", songs_removed_by_filter5_high_confidence_name_exclusion, SONG_CSV_FIELDS, include_extra=False)


async def main() -> None:
    (SUPPLEMENT_JSON / "high_confidence_name_filter_summary.json").unlink(missing_ok=True)
    client = Client()
    summaries: list[dict[str, Any]] = []

    for slug, target_name, target_mid in SINGERS:
        raw_rows = load_raw_songs(target_mid, target_name)
        raw_rows = sorted_rows(raw_rows)
        high_confidence_name_keys = load_high_confidence_name_keys(slug)
        songs_after_filter1_empty_album_exclusion, songs_removed_by_filter1_empty_album_exclusion = split_by_filter1(raw_rows)
        songs_after_filter2_album_identity, songs_removed_by_filter2_album_identity = split_by_filter2(songs_after_filter1_empty_album_exclusion)
        songs_after_album_detail_enrich = sorted_rows(await enrich_album_details(client, songs_after_filter2_album_identity))
        songs_after_filter3_album_type, songs_removed_by_filter3_album_type = split_by_filter3(songs_after_album_detail_enrich)
        deduped_rows, duplicate_rows = dedupe_full(songs_after_filter3_album_type)
        songs_after_filter4_dedupe = sorted_rows(deduped_rows)
        songs_removed_by_filter4_dedupe = sorted_rows(duplicate_rows)
        songs_after_filter5_high_confidence_name_exclusion, songs_removed_by_filter5_high_confidence_name_exclusion = split_by_filter5(songs_after_filter4_dedupe, high_confidence_name_keys)
        write_song_outputs(
            slug,
            raw_rows,
            songs_after_filter1_empty_album_exclusion,
            songs_removed_by_filter1_empty_album_exclusion,
            songs_after_filter2_album_identity,
            songs_removed_by_filter2_album_identity,
            songs_after_album_detail_enrich,
            songs_after_filter3_album_type,
            songs_removed_by_filter3_album_type,
            songs_after_filter4_dedupe,
            songs_removed_by_filter4_dedupe,
            songs_after_filter5_high_confidence_name_exclusion,
            songs_removed_by_filter5_high_confidence_name_exclusion,
        )

        summaries.append(
            {
                "slug": slug,
                "name": target_name,
                "mid": target_mid,
                "full_raw_rows": len(raw_rows),
                "songs_after_filter1_empty_album_exclusion": len(songs_after_filter1_empty_album_exclusion),
                "songs_removed_by_filter1_empty_album_exclusion": len(songs_removed_by_filter1_empty_album_exclusion),
                "songs_after_filter2_album_identity": len(songs_after_filter2_album_identity),
                "songs_removed_by_filter2_album_identity": len(songs_removed_by_filter2_album_identity),
                "songs_after_album_detail_enrich": len(songs_after_album_detail_enrich),
                "songs_after_filter3_album_type": len(songs_after_filter3_album_type),
                "songs_removed_by_filter3_album_type": len(songs_removed_by_filter3_album_type),
                "songs_after_filter4_dedupe": len(songs_after_filter4_dedupe),
                "songs_removed_by_filter4_dedupe": len(songs_removed_by_filter4_dedupe),
                "songs_after_filter5_high_confidence_name_exclusion": len(songs_after_filter5_high_confidence_name_exclusion),
                "songs_removed_by_filter5_high_confidence_name_exclusion": len(songs_removed_by_filter5_high_confidence_name_exclusion),
                "songs_after_filter1_empty_album_exclusion_json": f"data/processed/validation/four_singers/json_outputs/supplement_singer_songs/{slug}/songs_after_filter1_empty_album_exclusion.json",
                "songs_removed_by_filter1_empty_album_exclusion_json": f"data/processed/validation/four_singers/json_outputs/supplement_singer_songs/{slug}/songs_removed_by_filter1_empty_album_exclusion.json",
                "songs_after_filter2_album_identity_json": f"data/processed/validation/four_singers/json_outputs/supplement_singer_songs/{slug}/songs_after_filter2_album_identity.json",
                "songs_removed_by_filter2_album_identity_json": f"data/processed/validation/four_singers/json_outputs/supplement_singer_songs/{slug}/songs_removed_by_filter2_album_identity.json",
                "songs_after_album_detail_enrich_json": f"data/processed/validation/four_singers/json_outputs/supplement_singer_songs/{slug}/songs_after_album_detail_enrich.json",
                "songs_after_filter3_album_type_json": f"data/processed/validation/four_singers/json_outputs/supplement_singer_songs/{slug}/songs_after_filter3_album_type.json",
                "songs_removed_by_filter3_album_type_json": f"data/processed/validation/four_singers/json_outputs/supplement_singer_songs/{slug}/songs_removed_by_filter3_album_type.json",
                "songs_after_filter4_dedupe_json": f"data/processed/validation/four_singers/json_outputs/supplement_singer_songs/{slug}/songs_after_filter4_dedupe.json",
                "songs_removed_by_filter4_dedupe_json": f"data/processed/validation/four_singers/json_outputs/supplement_singer_songs/{slug}/songs_removed_by_filter4_dedupe.json",
                "songs_after_filter5_high_confidence_name_exclusion_json": f"data/processed/validation/four_singers/json_outputs/supplement_singer_songs/{slug}/songs_after_filter5_high_confidence_name_exclusion.json",
                "songs_removed_by_filter5_high_confidence_name_exclusion_json": f"data/processed/validation/four_singers/json_outputs/supplement_singer_songs/{slug}/songs_removed_by_filter5_high_confidence_name_exclusion.json",
                "songs_after_filter1_empty_album_exclusion_csv_view": f"data/processed/validation/four_singers/csv_views/supplement_singer_songs/{slug}/songs_after_filter1_empty_album_exclusion.csv",
                "songs_removed_by_filter1_empty_album_exclusion_csv_view": f"data/processed/validation/four_singers/csv_views/supplement_singer_songs/{slug}/songs_removed_by_filter1_empty_album_exclusion.csv",
                "songs_after_filter2_album_identity_csv_view": f"data/processed/validation/four_singers/csv_views/supplement_singer_songs/{slug}/songs_after_filter2_album_identity.csv",
                "songs_removed_by_filter2_album_identity_csv_view": f"data/processed/validation/four_singers/csv_views/supplement_singer_songs/{slug}/songs_removed_by_filter2_album_identity.csv",
                "songs_after_album_detail_enrich_csv_view": f"data/processed/validation/four_singers/csv_views/supplement_singer_songs/{slug}/songs_after_album_detail_enrich.csv",
                "songs_after_filter3_album_type_csv_view": f"data/processed/validation/four_singers/csv_views/supplement_singer_songs/{slug}/songs_after_filter3_album_type.csv",
                "songs_removed_by_filter3_album_type_csv_view": f"data/processed/validation/four_singers/csv_views/supplement_singer_songs/{slug}/songs_removed_by_filter3_album_type.csv",
                "songs_after_filter4_dedupe_csv_view": f"data/processed/validation/four_singers/csv_views/supplement_singer_songs/{slug}/songs_after_filter4_dedupe.csv",
                "songs_removed_by_filter4_dedupe_csv_view": f"data/processed/validation/four_singers/csv_views/supplement_singer_songs/{slug}/songs_removed_by_filter4_dedupe.csv",
                "songs_after_filter5_high_confidence_name_exclusion_csv_view": f"data/processed/validation/four_singers/csv_views/supplement_singer_songs/{slug}/songs_after_filter5_high_confidence_name_exclusion.csv",
                "songs_removed_by_filter5_high_confidence_name_exclusion_csv_view": f"data/processed/validation/four_singers/csv_views/supplement_singer_songs/{slug}/songs_removed_by_filter5_high_confidence_name_exclusion.csv",
                "removed_reason_counts": {
                    "filter1_empty_album_exclusion": dict(Counter(row.get("aux_filter_reason") or "" for row in songs_removed_by_filter1_empty_album_exclusion).most_common()),
                    "filter2_album_identity": dict(Counter(row.get("aux_filter_reason") or "" for row in songs_removed_by_filter2_album_identity).most_common()),
                    "filter3_album_type": dict(Counter(row.get("aux_filter_reason") or "" for row in songs_removed_by_filter3_album_type).most_common()),
                    "filter4_dedupe": dict(Counter(row.get("aux_filter_reason") or "" for row in songs_removed_by_filter4_dedupe).most_common()),
                    "filter5_high_confidence_name_exclusion": dict(Counter(row.get("aux_filter_reason") or "" for row in songs_removed_by_filter5_high_confidence_name_exclusion).most_common()),
                },
            }
        )

    summary = {
        "step": "supplement_branch_filter1_empty_album_then_filter2_album_identity_then_album_detail_enrich_then_filter3_album_type_then_filter4_dedupe_then_filter5_high_confidence_name_exclusion",
        "description": "Validation output for the supplement branch. Filter1 removes empty albums, filter2 removes rows without album id/mid, album details are enriched, filter3 keeps only Single/EP/录音室专辑 albums, filter4 dedupes by song key, and filter5 removes rows whose normalized song name exists in the high-confidence subset.",
        "source": {
            "full_set": "data/raw/qqmusic/singer_homepage_song_tab/<mid>/page_*.json SongTab.List",
            "album_detail_set": "data/raw/qqmusic/supplement_album_details/<album_mid_or_id>.json",
            "high_confidence_set": "data/processed/validation/four_singers/json_outputs/high_confidence_singer_songs/<slug>/songs_after_filter2_dedupe.json",
        },
        "schema_rule": "non-aux columns keep QQ Music raw song keys; project helper columns use aux_ prefix",
        "dedupe_key_rule": "filter4 first dedupes by song mid/id only, then dedupes by normalized raw song name; same-name rows prefer 录音室专辑, then EP, then Single, then the lowest numeric song id",
        "album_type_allowlist": sorted(ALLOWED_SUPPLEMENT_ALBUM_TYPES),
        "filter_rules": [
            "filter1: album name/title/subtitle must not be empty",
            "filter2: album id/mid must not be empty",
            "album detail enrich: request qqmusic album.get_detail by album mid first, then id",
            "filter3: album detail type must be Single, EP, or 录音室专辑",
            "filter4: dedupe by song mid/id, then by raw name with album type priority and lowest numeric song id tie-breaker",
            "filter5: normalized song name only",
        ],
        "validation_rule": "each filter step writes both kept rows and removed rows with aux_filter_reason",
        "output_semantics": "remaining supplement-branch rows after filter1, filter2, and filter3; not a separate pipeline branch",
        "singers": summaries,
        "counts": {
            "singers": len(SINGERS),
            "full_raw_rows": sum(item["full_raw_rows"] for item in summaries),
            "songs_after_filter1_empty_album_exclusion": sum(item["songs_after_filter1_empty_album_exclusion"] for item in summaries),
            "songs_removed_by_filter1_empty_album_exclusion": sum(item["songs_removed_by_filter1_empty_album_exclusion"] for item in summaries),
            "songs_after_filter2_album_identity": sum(item["songs_after_filter2_album_identity"] for item in summaries),
            "songs_removed_by_filter2_album_identity": sum(item["songs_removed_by_filter2_album_identity"] for item in summaries),
            "songs_after_album_detail_enrich": sum(item["songs_after_album_detail_enrich"] for item in summaries),
            "songs_after_filter3_album_type": sum(item["songs_after_filter3_album_type"] for item in summaries),
            "songs_removed_by_filter3_album_type": sum(item["songs_removed_by_filter3_album_type"] for item in summaries),
            "songs_after_filter4_dedupe": sum(item["songs_after_filter4_dedupe"] for item in summaries),
            "songs_removed_by_filter4_dedupe": sum(item["songs_removed_by_filter4_dedupe"] for item in summaries),
            "songs_after_filter5_high_confidence_name_exclusion": sum(item["songs_after_filter5_high_confidence_name_exclusion"] for item in summaries),
            "songs_removed_by_filter5_high_confidence_name_exclusion": sum(item["songs_removed_by_filter5_high_confidence_name_exclusion"] for item in summaries),
        },
        "outputs": {},
        "directory_policy": {
            "branch": "supplement_branch",
            "json_outputs": "JSON files stay under data/processed/validation/four_singers/json_outputs/supplement_singer_songs/ for the four-singer validation sample.",
            "csv_views": "CSV files are validation-only and stay under data/processed/validation/four_singers/csv_views/supplement_singer_songs/.",
        },
    }
    dump_json(SUPPLEMENT_JSON / "filter1_filter2_filter3_summary.json", summary)
    print(json.dumps(summary["counts"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
