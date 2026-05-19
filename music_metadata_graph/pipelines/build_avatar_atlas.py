from __future__ import annotations
import argparse
import hashlib
import json
import math
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from PIL import Image, ImageOps
from PIL import features as pillow_features
from music_metadata_graph.pipelines.avatar_assets import avatar_key, normalize_avatar_url
from music_metadata_graph.pipelines.prepare_static_graph_assets import (
    DEFAULT_AVATAR_CACHE_DIR,
    DEFAULT_LEGACY_AVATAR_CACHE_DIR,
    DEFAULT_MANIFEST_NAME,
    manifest_path,
)
from music_metadata_graph.pipelines.build_static_graph import read_graph_data_asset
from music_metadata_graph.run_log import run_with_log

DEFAULT_OUTPUT_DIR = Path("site_assets/avatar_atlas_150")
DEFAULT_CELL_SIZE = 150
DEFAULT_ATLAS_SIZE = 3000
DEFAULT_WEBP_QUALITY = 80
DEFAULT_MANIFEST_FILE = "avatar-atlas-manifest.json"
DEFAULT_MANIFEST_SCRIPT_FILE = "avatar-atlas-manifest.js"
DEFAULT_REPORT_FILE = "avatar-atlas-report.json"
DEFAULT_FINGERPRINT_FILE = "avatar-atlas-build-fingerprint.json"
ATLAS_BUILD_VERSION = "avatar-atlas-v2"
FINGERPRINT_SCHEMA_VERSION = 1
HASH_CHUNK_SIZE = 1024 * 1024
DEFAULT_GRAPH_DATA_BY_PROFILE = {
    "mvp": Path("site_mvp/assets/graph-data.js"),
    "demo": Path("site_demo/assets/graph-data.js"),
    "full": Path("site/assets/graph-data.js"),
}


@dataclass(frozen=True)
class AtlasConfig:
    avatar_cache_dir: Path
    output_dir: Path
    graph_data_by_profile: dict[str, Path]
    cell_size: int
    atlas_size: int
    webp_quality: int
    include_unused_cache: bool
    mode: str = "auto"
    legacy_avatar_cache_dir: Path | None = DEFAULT_LEGACY_AVATAR_CACHE_DIR


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def payload_sha256(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(HASH_CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_fingerprint(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {"size": stat.st_size, "sha256": file_sha256(path)}


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )


def safe_script_json(value: Any) -> str:
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .replace("</", "<\\/")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def save_manifest_script(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"window.AVATAR_ATLAS_MANIFEST_DATA = {safe_script_json(payload)};\n",
        encoding="utf-8",
        newline="\n",
    )


def migrate_legacy_avatar_cache(config: AtlasConfig) -> dict[str, Any]:
    source = config.legacy_avatar_cache_dir
    if source is None or source == config.avatar_cache_dir or not manifest_path(source).exists():
        return {"migrated": False, "reason": "legacy cache not available"}
    target_manifest = manifest_path(config.avatar_cache_dir)
    if target_manifest.exists():
        return {"migrated": False, "reason": "target manifest already exists"}

    legacy_manifest = load_json(manifest_path(source))
    avatars = legacy_manifest.get("avatars") or {}
    copied = 0
    skipped_missing = 0
    rewritten: dict[str, Any] = {"avatars": {}}
    for url, record in avatars.items():
        local_path = str((record or {}).get("local_path") or "")
        if not local_path:
            rewritten["avatars"][url] = record
            continue
        source_path = source / local_path
        if not source_path.exists():
            skipped_missing += 1
            rewritten["avatars"][url] = record
            continue
        target_path = config.avatar_cache_dir / local_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
        copied += 1
        rewritten["avatars"][url] = {**record, "local_path": local_path}
    save_json(target_manifest, rewritten)
    return {
        "migrated": True,
        "source": source.as_posix(),
        "target": config.avatar_cache_dir.as_posix(),
        "copied": copied,
        "skipped_missing": skipped_missing,
    }


def graph_avatar_keys(path: Path) -> set[str]:
    if not path.exists():
        return set()
    data = read_graph_data_asset(path)
    keys: set[str] = set()
    for collection_name in ("nodes", "targets"):
        for item in data.get(collection_name, []):
            key = str(item.get("avatar_key") or "")
            if not key and item.get("icon"):
                key = avatar_key(item.get("icon"))
            if key:
                keys.add(key)
    return keys


def ordered_keys_by_profiles(
    graph_data_by_profile: dict[str, Path],
) -> tuple[list[str], dict[str, list[str]], dict[str, int]]:
    profile_keys = {
        profile: graph_avatar_keys(path) for profile, path in graph_data_by_profile.items()
    }
    order: list[str] = []
    seen: set[str] = set()
    profile_files_start_counts: dict[str, int] = {}
    for profile in ("mvp", "demo", "full"):
        for key in sorted(profile_keys.get(profile, set())):
            if key not in seen:
                seen.add(key)
                order.append(key)
        profile_files_start_counts[profile] = len(order)
    return (
        order,
        {profile: sorted(keys) for profile, keys in profile_keys.items()},
        profile_files_start_counts,
    )


def source_records_by_key(
    avatar_cache_dir: Path,
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    manifest = load_json(manifest_path(avatar_cache_dir))
    records: dict[str, dict[str, Any]] = {}
    duplicate_urls: list[dict[str, Any]] = []
    for url, record in (manifest.get("avatars") or {}).items():
        normalized = normalize_avatar_url(url)
        key = avatar_key(normalized)
        if not key:
            continue
        current = records.get(key)
        value = {"url": normalized, **(record or {})}
        if current is not None and current.get("url") != normalized:
            duplicate_urls.append(
                {"avatar_key": key, "first": current.get("url"), "duplicate": normalized}
            )
            continue
        records[key] = value
    return records, duplicate_urls


def ordered_avatar_keys(config: AtlasConfig) -> tuple[list[str], dict[str, Any]]:
    profile_order, profile_keys, profile_counts = ordered_keys_by_profiles(
        config.graph_data_by_profile
    )
    records, duplicate_urls = source_records_by_key(config.avatar_cache_dir)
    ordered = [key for key in profile_order if key in records]
    missing_profile_keys = sorted(set(profile_order) - set(records))
    if config.include_unused_cache:
        for key in sorted(records):
            if key not in set(ordered):
                ordered.append(key)
    return ordered, {
        "profile_key_counts": {profile: len(keys) for profile, keys in profile_keys.items()},
        "profile_keys": profile_keys,
        "profile_order_counts": profile_counts,
        "cache_records": len(records),
        "missing_profile_keys": missing_profile_keys,
        "duplicate_urls": duplicate_urls,
    }


def image_ops_transpose(image: Image.Image) -> Image.Image:
    return ImageOps.exif_transpose(image)


def make_avatar_cell(path: Path, cell_size: int) -> Image.Image:
    with Image.open(path) as image:
        image = image_ops_transpose(image)
        image = image.convert("RGB")
        width, height = image.size
        side = min(width, height)
        left = max(0, (width - side) // 2)
        top = max(0, (height - side) // 2)
        cropped = image.crop((left, top, left + side, top + side))
        return cropped.resize((cell_size, cell_size), Image.Resampling.LANCZOS)


def atlas_files_for_count(count: int, cells_per_atlas: int) -> list[str]:
    if count <= 0:
        return []
    atlas_count = math.ceil(count / cells_per_atlas)
    return [f"atlas_{index:03d}.webp" for index in range(atlas_count)]


def cells_per_atlas(config: AtlasConfig) -> tuple[int, int]:
    cells_per_row = config.atlas_size // config.cell_size
    if cells_per_row <= 0 or config.atlas_size % config.cell_size != 0:
        raise ValueError("atlas_size must be a positive multiple of cell_size.")
    return cells_per_row, cells_per_row * cells_per_row


def source_entry_for_key(config: AtlasConfig, key: str, record: dict[str, Any]) -> dict[str, Any]:
    local_path = str(record.get("local_path") or "")
    entry: dict[str, Any] = {
        "avatar_key": key,
        "url": record.get("url") or "",
        "status": record.get("status") or "",
        "local_path": local_path,
        "content_type": record.get("content_type") or "",
    }
    if local_path and record.get("status") == "ok":
        source_path = config.avatar_cache_dir / local_path
        entry["exists"] = source_path.exists()
        if source_path.exists():
            entry["file"] = file_fingerprint(source_path)
    return entry


def build_input_payload(
    config: AtlasConfig,
    ordered_keys: list[str],
    records: dict[str, dict[str, Any]],
    order_report: dict[str, Any],
) -> dict[str, Any]:
    source_entries = [
        source_entry_for_key(config, key, records.get(key) or {}) for key in ordered_keys
    ]
    return {
        "schema_version": FINGERPRINT_SCHEMA_VERSION,
        "generator_version": ATLAS_BUILD_VERSION,
        "config": {
            "cell_size": config.cell_size,
            "atlas_size": config.atlas_size,
            "webp_quality": config.webp_quality,
            "include_unused_cache": config.include_unused_cache,
        },
        "environment": {
            "pillow_version": Image.__version__,
            "webp_supported": bool(pillow_features.check("webp")),
        },
        "profiles": {
            "profile_keys": order_report.get("profile_keys", {}),
            "profile_order_counts": order_report.get("profile_order_counts", {}),
        },
        "ordered_keys": ordered_keys,
        "source_entries": source_entries,
        "missing_profile_keys": order_report.get("missing_profile_keys", []),
        "duplicate_urls": order_report.get("duplicate_urls", []),
    }


def collect_build_inputs(
    config: AtlasConfig,
) -> tuple[dict[str, dict[str, Any]], list[str], dict[str, Any], dict[str, Any], str]:
    records, _duplicate_urls = source_records_by_key(config.avatar_cache_dir)
    ordered_keys, order_report = ordered_avatar_keys(config)
    input_payload = build_input_payload(config, ordered_keys, records, order_report)
    input_hash = payload_sha256(input_payload)
    return records, ordered_keys, order_report, input_payload, input_hash


def output_file_entry(output_dir: Path, filename: str) -> dict[str, Any]:
    path = output_dir / filename
    return {"name": filename, **file_fingerprint(path)}


def create_build_fingerprint(
    config: AtlasConfig,
    output_dir: Path,
    input_payload: dict[str, Any],
    input_hash: str,
    atlas_files: list[str],
) -> dict[str, Any]:
    output_names = [
        DEFAULT_MANIFEST_FILE,
        DEFAULT_MANIFEST_SCRIPT_FILE,
        DEFAULT_REPORT_FILE,
        *atlas_files,
    ]
    input_summary = {
        "config": input_payload.get("config", {}),
        "environment": input_payload.get("environment", {}),
        "profile_keys_hash": payload_sha256(
            (input_payload.get("profiles") or {}).get("profile_keys", {})
        ),
        "profile_order_counts": (input_payload.get("profiles") or {}).get(
            "profile_order_counts", {}
        ),
        "ordered_keys_count": len(input_payload.get("ordered_keys") or []),
        "ordered_keys_hash": payload_sha256(input_payload.get("ordered_keys") or []),
        "source_entries_count": len(input_payload.get("source_entries") or []),
        "source_entries_hash": payload_sha256(input_payload.get("source_entries") or []),
        "missing_profile_keys_hash": payload_sha256(
            input_payload.get("missing_profile_keys") or []
        ),
        "duplicate_urls_hash": payload_sha256(input_payload.get("duplicate_urls") or []),
    }
    return {
        "schema_version": FINGERPRINT_SCHEMA_VERSION,
        "generator_version": ATLAS_BUILD_VERSION,
        "input_hash": input_hash,
        "input_summary": input_summary,
        "outputs": {
            "files": [output_file_entry(output_dir, name) for name in output_names],
            "atlas_files": atlas_files,
        },
    }


def validate_manifest_structure(
    config: AtlasConfig, output_dir: Path, manifest: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    if manifest.get("version") != 1:
        errors.append("manifest version mismatch")
    if manifest.get("cell_size") != config.cell_size:
        errors.append("manifest cell_size mismatch")
    if manifest.get("atlas_size") != config.atlas_size:
        errors.append("manifest atlas_size mismatch")
    if manifest.get("webp_quality") != config.webp_quality:
        errors.append("manifest webp_quality mismatch")
    items = manifest.get("items")
    profiles = manifest.get("profiles")
    if not isinstance(items, dict):
        errors.append("manifest items must be an object")
        items = {}
    if not isinstance(profiles, dict):
        errors.append("manifest profiles must be an object")
        profiles = {}
    atlas_files = {path.name for path in output_dir.glob("atlas_*.webp")}
    for key, item in items.items():
        if not isinstance(item, dict):
            errors.append(f"manifest item is not an object: {key}")
            continue
        atlas = str(item.get("atlas") or "")
        x = item.get("x")
        y = item.get("y")
        w = item.get("w")
        h = item.get("h")
        if atlas not in atlas_files:
            errors.append(f"manifest item references missing atlas: {atlas}")
        if not all(isinstance(value, int) for value in (x, y, w, h)):
            errors.append(f"manifest item has non-integer geometry: {key}")
            continue
        if w != config.cell_size or h != config.cell_size:
            errors.append(f"manifest item cell size mismatch: {key}")
        if x < 0 or y < 0 or x + w > config.atlas_size or y + h > config.atlas_size:
            errors.append(f"manifest item outside atlas bounds: {key}")
        if x % config.cell_size != 0 or y % config.cell_size != 0:
            errors.append(f"manifest item is not cell-aligned: {key}")
    for profile, value in profiles.items():
        if not isinstance(value, dict):
            errors.append(f"profile is not an object: {profile}")
            continue
        profile_files = value.get("atlas_files") or []
        if not isinstance(profile_files, list):
            errors.append(f"profile atlas_files is not a list: {profile}")
            continue
        for filename in profile_files:
            if filename not in atlas_files:
                errors.append(f"profile references missing atlas: {profile}/{filename}")
    return errors


def check_existing_atlas(config: AtlasConfig) -> dict[str, Any]:
    _, _, _, input_payload, input_hash = collect_build_inputs(config)
    output_dir = config.output_dir
    fingerprint_path = output_dir / DEFAULT_FINGERPRINT_FILE
    if not fingerprint_path.exists():
        return {
            "ok": False,
            "status": "missing_fingerprint",
            "reason": "fingerprint file is missing",
            "input_hash": input_hash,
        }
    try:
        fingerprint = load_json(fingerprint_path)
    except Exception as exc:
        return {
            "ok": False,
            "status": "invalid_fingerprint",
            "reason": str(exc),
            "input_hash": input_hash,
        }
    if fingerprint.get("schema_version") != FINGERPRINT_SCHEMA_VERSION:
        return {"ok": False, "status": "fingerprint_schema_mismatch", "input_hash": input_hash}
    if fingerprint.get("generator_version") != ATLAS_BUILD_VERSION:
        return {"ok": False, "status": "generator_version_mismatch", "input_hash": input_hash}
    if fingerprint.get("input_hash") != input_hash:
        return {
            "ok": False,
            "status": "input_changed",
            "input_hash": input_hash,
            "stored_input_hash": fingerprint.get("input_hash"),
        }
    output_files = (fingerprint.get("outputs") or {}).get("files") or []
    expected_by_name = {str(item.get("name")): item for item in output_files if item.get("name")}
    expected_atlas_files = [
        str(name) for name in ((fingerprint.get("outputs") or {}).get("atlas_files") or [])
    ]
    actual_atlas_files = sorted(path.name for path in output_dir.glob("atlas_*.webp"))
    if actual_atlas_files != sorted(expected_atlas_files):
        return {
            "ok": False,
            "status": "atlas_file_set_mismatch",
            "expected": expected_atlas_files,
            "actual": actual_atlas_files,
            "input_hash": input_hash,
        }
    for filename, expected in expected_by_name.items():
        path = output_dir / filename
        if not path.is_file():
            return {
                "ok": False,
                "status": "output_missing",
                "file": filename,
                "input_hash": input_hash,
            }
        actual = file_fingerprint(path)
        if actual.get("size") != expected.get("size") or actual.get("sha256") != expected.get(
            "sha256"
        ):
            return {
                "ok": False,
                "status": "output_hash_mismatch",
                "file": filename,
                "input_hash": input_hash,
            }
    try:
        manifest = load_json(output_dir / DEFAULT_MANIFEST_FILE)
    except Exception as exc:
        return {
            "ok": False,
            "status": "invalid_manifest",
            "reason": str(exc),
            "input_hash": input_hash,
        }
    errors = validate_manifest_structure(config, output_dir, manifest)
    if errors:
        return {
            "ok": False,
            "status": "invalid_manifest_structure",
            "errors": errors[:20],
            "input_hash": input_hash,
        }
    manifest_script = (output_dir / DEFAULT_MANIFEST_SCRIPT_FILE).read_text(encoding="utf-8")
    expected_script = f"window.AVATAR_ATLAS_MANIFEST_DATA = {safe_script_json(manifest)};\n"
    if manifest_script != expected_script:
        return {"ok": False, "status": "manifest_script_mismatch", "input_hash": input_hash}
    return {
        "ok": True,
        "status": "up_to_date",
        "input_hash": input_hash,
        "avatar_items": len(manifest.get("items") or {}),
        "atlas_files": len(expected_atlas_files),
        "fingerprint": fingerprint_path.as_posix(),
    }


def build_atlas_files(
    config: AtlasConfig,
    output_dir: Path,
    records: dict[str, dict[str, Any]],
    ordered_keys: list[str],
    order_report: dict[str, Any],
    migrate_result: dict[str, Any],
) -> dict[str, Any]:
    cells_per_row, per_atlas = cells_per_atlas(config)
    output_dir.mkdir(parents=True, exist_ok=True)
    for stale in output_dir.glob("atlas_*.webp"):
        stale.unlink()
    for stale_name in (
        DEFAULT_MANIFEST_FILE,
        DEFAULT_MANIFEST_SCRIPT_FILE,
        DEFAULT_REPORT_FILE,
        DEFAULT_FINGERPRINT_FILE,
    ):
        stale = output_dir / stale_name
        if stale.exists():
            stale.unlink()

    items: dict[str, dict[str, Any]] = {}
    failures: list[dict[str, Any]] = []
    atlas_index = -1
    atlas_image: Image.Image | None = None
    written_files: list[str] = []
    placed_count = 0

    def flush() -> None:
        nonlocal atlas_image, atlas_index
        if atlas_image is None or atlas_index < 0:
            return
        filename = f"atlas_{atlas_index:03d}.webp"
        output = output_dir / filename
        atlas_image.save(output, format="WEBP", quality=config.webp_quality, method=6, exact=False)
        written_files.append(filename)
        atlas_image = None

    for key in ordered_keys:
        record = records.get(key) or {}
        local_path = str(record.get("local_path") or "")
        if not local_path or record.get("status") != "ok":
            failures.append(
                {
                    "avatar_key": key,
                    "url": record.get("url"),
                    "reason": "missing successful cache record",
                }
            )
            continue
        source_path = config.avatar_cache_dir / local_path
        if not source_path.exists():
            failures.append(
                {
                    "avatar_key": key,
                    "url": record.get("url"),
                    "path": source_path.as_posix(),
                    "reason": "source file missing",
                }
            )
            continue
        cell_index = placed_count % per_atlas
        if cell_index == 0:
            flush()
            atlas_index += 1
            atlas_image = Image.new("RGB", (config.atlas_size, config.atlas_size), (245, 247, 250))
        assert atlas_image is not None
        try:
            cell = make_avatar_cell(source_path, config.cell_size)
        except Exception as exc:
            failures.append(
                {
                    "avatar_key": key,
                    "url": record.get("url"),
                    "path": source_path.as_posix(),
                    "reason": str(exc),
                }
            )
            continue
        x = (cell_index % cells_per_row) * config.cell_size
        y = (cell_index // cells_per_row) * config.cell_size
        atlas_image.paste(cell, (x, y))
        filename = f"atlas_{atlas_index:03d}.webp"
        items[key] = {
            "atlas": filename,
            "x": x,
            "y": y,
            "w": config.cell_size,
            "h": config.cell_size,
        }
        placed_count += 1
    flush()

    profiles: dict[str, dict[str, Any]] = {}
    for profile, count in order_report["profile_order_counts"].items():
        usable_count = len([key for key in ordered_keys[:count] if key in items])
        profiles[profile] = {
            "atlas_files": atlas_files_for_count(usable_count, per_atlas),
            "avatar_count": usable_count,
        }

    manifest = {
        "version": 1,
        "cell_size": config.cell_size,
        "atlas_size": config.atlas_size,
        "webp_quality": config.webp_quality,
        "items": items,
        "profiles": profiles,
    }
    save_json(output_dir / DEFAULT_MANIFEST_FILE, manifest)
    save_manifest_script(output_dir / DEFAULT_MANIFEST_SCRIPT_FILE, manifest)
    report = {
        "avatar_cache_dir": config.avatar_cache_dir.as_posix(),
        "output_dir": config.output_dir.as_posix(),
        "migrate": migrate_result,
        "ordered_keys": len(ordered_keys),
        "placed": placed_count,
        "failed": len(failures),
        "atlas_files": written_files,
        "atlas_count": len(written_files),
        "duplicate_urls": order_report.get("duplicate_urls", []),
        "missing_profile_keys": order_report.get("missing_profile_keys", []),
        "failures": failures[:200],
    }
    save_json(output_dir / DEFAULT_REPORT_FILE, report)
    return {
        **report,
        "manifest": (output_dir / DEFAULT_MANIFEST_FILE).as_posix(),
        "manifest_script": (output_dir / DEFAULT_MANIFEST_SCRIPT_FILE).as_posix(),
    }


def replace_output_dir(temp_dir: Path, output_dir: Path) -> None:
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    backup_dir = output_dir.with_name(f".{output_dir.name}.replace_backup")
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    try:
        if output_dir.exists():
            output_dir.rename(backup_dir)
        temp_dir.rename(output_dir)
    except Exception:
        if output_dir.exists():
            shutil.rmtree(output_dir)
        if backup_dir.exists():
            backup_dir.rename(output_dir)
        raise
    if backup_dir.exists():
        shutil.rmtree(backup_dir)


def build_atlas(config: AtlasConfig) -> dict[str, Any]:
    if config.mode not in {"auto", "force", "check"}:
        raise ValueError("mode must be one of: auto, force, check")
    migrate_result = migrate_legacy_avatar_cache(config)
    records, ordered_keys, order_report, input_payload, input_hash = collect_build_inputs(config)
    had_output = config.output_dir.exists()
    existing = None if config.mode == "force" else check_existing_atlas(config)
    if existing and existing.get("ok"):
        fingerprint_path = config.output_dir / DEFAULT_FINGERPRINT_FILE
        fingerprint_compacted = False
        try:
            fingerprint = load_json(fingerprint_path)
        except Exception:
            fingerprint = {}
        if "input" in fingerprint or "input_summary" not in fingerprint:
            atlas_files = sorted(path.name for path in config.output_dir.glob("atlas_*.webp"))
            save_json(
                fingerprint_path,
                create_build_fingerprint(
                    config, config.output_dir, input_payload, input_hash, atlas_files
                ),
            )
            fingerprint_compacted = True
        return {
            **existing,
            "status": "valid" if config.mode == "check" else "skipped",
            "reason": "existing atlas matches current inputs",
            "fingerprint_compacted": fingerprint_compacted,
        }
    if config.mode == "check":
        return {
            "ok": False,
            "status": "invalid",
            "reason": "existing atlas does not match current inputs or is incomplete",
            "check": existing,
        }

    temp_root = config.output_dir.parent
    temp_root.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix=f".{config.output_dir.name}.", dir=temp_root))
    try:
        result = build_atlas_files(
            config, temp_dir, records, ordered_keys, order_report, migrate_result
        )
        fingerprint = create_build_fingerprint(
            config, temp_dir, input_payload, input_hash, result["atlas_files"]
        )
        save_json(temp_dir / DEFAULT_FINGERPRINT_FILE, fingerprint)
        validation_config = AtlasConfig(
            avatar_cache_dir=config.avatar_cache_dir,
            output_dir=temp_dir,
            graph_data_by_profile=config.graph_data_by_profile,
            cell_size=config.cell_size,
            atlas_size=config.atlas_size,
            webp_quality=config.webp_quality,
            include_unused_cache=config.include_unused_cache,
            mode="check",
            legacy_avatar_cache_dir=None,
        )
        validation = check_existing_atlas(validation_config)
        if not validation.get("ok"):
            raise RuntimeError(f"Temporary avatar atlas failed validation: {validation}")
        replace_output_dir(temp_dir, config.output_dir)
        return {
            "ok": True,
            "status": "rebuilt" if had_output else "built",
            "reason": None if config.mode == "force" else (existing or {}).get("status"),
            "fingerprint": (config.output_dir / DEFAULT_FINGERPRINT_FILE).as_posix(),
            **result,
            "manifest": (config.output_dir / DEFAULT_MANIFEST_FILE).as_posix(),
            "manifest_script": (config.output_dir / DEFAULT_MANIFEST_SCRIPT_FILE).as_posix(),
        }
    except Exception:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        raise


def parse_profile_args(values: Iterable[str]) -> dict[str, Path]:
    profiles = dict(DEFAULT_GRAPH_DATA_BY_PROFILE)
    for value in values:
        if "=" not in value:
            raise ValueError(f"Profile graph data must use name=path: {value}")
        name, path = value.split("=", 1)
        profiles[name.strip()] = Path(path)
    return profiles


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build shared 150x150 WebP avatar atlases for static graph sites."
    )
    parser.add_argument(
        "--avatar-cache-dir",
        type=Path,
        default=DEFAULT_AVATAR_CACHE_DIR,
        help="Raw avatar cache directory.",
    )
    parser.add_argument(
        "--legacy-avatar-cache-dir",
        type=Path,
        default=DEFAULT_LEGACY_AVATAR_CACHE_DIR,
        help="Legacy cache directory to migrate from if the raw cache is empty.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Shared avatar atlas output directory.",
    )
    parser.add_argument(
        "--profile-graph-data",
        action="append",
        default=[],
        help="Profile graph data path as name=path.",
    )
    parser.add_argument("--cell-size", type=int, default=DEFAULT_CELL_SIZE)
    parser.add_argument("--atlas-size", type=int, default=DEFAULT_ATLAS_SIZE)
    parser.add_argument("--webp-quality", type=int, default=DEFAULT_WEBP_QUALITY)
    parser.add_argument(
        "--include-unused-cache",
        action="store_true",
        help="Also include cached avatars not referenced by current graph data.",
    )
    parser.add_argument(
        "--mode",
        choices=("auto", "force", "check"),
        default="auto",
        help="auto reuses matching atlases, force rebuilds, check validates without writing.",
    )
    parser.add_argument("--force", action="store_true", help="Shortcut for --mode force.")
    parser.add_argument("--check", action="store_true", help="Shortcut for --mode check.")
    return parser.parse_args()


def _main() -> None:
    args = parse_args()
    if args.force and args.check:
        raise SystemExit("--force and --check cannot be used together.")
    mode = "force" if args.force else "check" if args.check else args.mode
    result = build_atlas(
        AtlasConfig(
            avatar_cache_dir=args.avatar_cache_dir,
            legacy_avatar_cache_dir=args.legacy_avatar_cache_dir,
            output_dir=args.output_dir,
            graph_data_by_profile=parse_profile_args(args.profile_graph_data),
            cell_size=args.cell_size,
            atlas_size=args.atlas_size,
            webp_quality=args.webp_quality,
            include_unused_cache=args.include_unused_cache,
            mode=mode,
        )
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if mode == "check" and not result.get("ok"):
        raise SystemExit(1)


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()
