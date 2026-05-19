from __future__ import annotations
import argparse
import asyncio
import hashlib
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from music_metadata_graph.pipelines.avatar_assets import avatar_key
from music_metadata_graph.pipelines.build_static_graph import (
    DEFAULT_DEMO_OUTPUT_DIR,
    DEFAULT_MVP_OUTPUT_DIR,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_VENDOR_PATH,
    build_graph_data,
    connect_database,
    graph_asset_path,
    graph_data_script,
    read_vendor_script,
    vendor_asset_path,
)
from music_metadata_graph.pipelines.defaults import DEFAULT_DB_PATH, DEFAULT_MVP_DB_PATH
from music_metadata_graph.run_log import run_with_log

DEFAULT_AVATAR_DIR_NAME = "avatars"
DEFAULT_MANIFEST_NAME = "avatar-manifest.json"
DEFAULT_AVATAR_CACHE_DIR = Path("data/raw/qqmusic/avatar_cache")
DEFAULT_LEGACY_AVATAR_CACHE_DIR = Path("site_assets")
DEFAULT_REQUEST_DELAY_SECONDS = 1.0
DEFAULT_TIMEOUT_SECONDS = 10.0


@dataclass(frozen=True)
class PrepareAssetsConfig:
    db_path: Path
    output_dir: Path
    vendor_path: Path
    avatar_cache_dir: Path
    download_avatars: bool
    max_avatar_downloads: int | None
    request_delay_seconds: float
    timeout_seconds: float
    demo: bool = False


@dataclass(frozen=True)
class AvatarDownloadJob:
    index: int
    total: int
    url: str
    path: Path
    timeout_seconds: float


@dataclass(frozen=True)
class AvatarDownloadResult:
    job: AvatarDownloadJob
    success: bool
    detail: str


def avatar_dir(avatar_cache_dir: Path) -> Path:
    return avatar_cache_dir / DEFAULT_AVATAR_DIR_NAME


def manifest_path(avatar_cache_dir: Path) -> Path:
    return avatar_cache_dir / DEFAULT_MANIFEST_NAME


def avatar_extension(url: str, content_type: str = "") -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        return suffix
    if "png" in content_type:
        return ".png"
    if "webp" in content_type:
        return ".webp"
    if "gif" in content_type:
        return ".gif"
    return ".jpg"


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"avatars": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def save_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )


def migrate_legacy_avatar_cache_if_needed(
    avatar_cache_dir: Path, legacy_avatar_cache_dir: Path = DEFAULT_LEGACY_AVATAR_CACHE_DIR
) -> dict[str, Any]:
    if avatar_cache_dir != DEFAULT_AVATAR_CACHE_DIR:
        return {"migrated": False, "reason": "custom cache directory"}
    target_manifest = manifest_path(avatar_cache_dir)
    legacy_manifest = manifest_path(legacy_avatar_cache_dir)
    if target_manifest.exists():
        return {"migrated": False, "reason": "target manifest already exists"}
    if avatar_cache_dir == legacy_avatar_cache_dir or not legacy_manifest.exists():
        return {"migrated": False, "reason": "legacy manifest not available"}
    payload = load_manifest(legacy_manifest)
    copied = 0
    missing = 0
    rewritten: dict[str, Any] = {"avatars": {}}
    for url, record in (payload.get("avatars") or {}).items():
        local_path = str((record or {}).get("local_path") or "")
        if not local_path:
            rewritten["avatars"][url] = record
            continue
        source = legacy_avatar_cache_dir / local_path
        if not source.exists():
            missing += 1
            rewritten["avatars"][url] = record
            continue
        target = avatar_cache_dir / local_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied += 1
        rewritten["avatars"][url] = {**record, "local_path": local_path}
    save_manifest(target_manifest, rewritten)
    return {
        "migrated": True,
        "source": legacy_avatar_cache_dir.as_posix(),
        "target": avatar_cache_dir.as_posix(),
        "copied": copied,
        "missing": missing,
    }


def cache_avatar_relpath(avatar_cache_dir: Path, path: Path) -> str:
    return path.relative_to(avatar_cache_dir).as_posix()


def site_avatar_relpath(output_dir: Path, avatar_cache_dir: Path, cache_relative_path: str) -> str:
    path = avatar_cache_dir / cache_relative_path
    return Path(os.path.relpath(path, start=output_dir)).as_posix()


def avatar_filename(url: str, extension: str = ".jpg") -> str:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:32]
    return f"{digest}{extension}"


def download_avatar(url: str, path: Path, timeout_seconds: float) -> tuple[bool, str]:
    request = Request(url, headers={"User-Agent": "MusicianRelationshipGraph/0.1"})
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            content_type = response.headers.get("Content-Type", "")
            data = response.read()
    except (OSError, URLError) as exc:
        return False, str(exc)

    if not data:
        return False, "empty response"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return True, content_type


def run_avatar_download(job: AvatarDownloadJob) -> AvatarDownloadResult:
    try:
        success, detail = download_avatar(job.url, job.path, job.timeout_seconds)
    except Exception as exc:
        return AvatarDownloadResult(job=job, success=False, detail=str(exc))
    return AvatarDownloadResult(job=job, success=success, detail=detail)


def ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def collect_icon_urls(graph_data: dict[str, Any]) -> list[str]:
    priorities: dict[str, int] = {}
    for node in graph_data.get("nodes", []):
        url = str(node.get("icon") or "").strip()
        if not url.startswith(("http://", "https://")):
            continue
        priority = avatar_download_priority(node)
        priorities[url] = max(priorities.get(url, 0), priority)
    return sorted(priorities, key=lambda url: (-priorities[url], url))


def avatar_download_priority(node: dict[str, Any]) -> int:
    return (
        safe_int(node.get("sung_song_count"))
        + safe_int(node.get("lyricist_song_count"))
        + safe_int(node.get("composer_song_count"))
    )


def safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def print_avatar_progress(
    index: int,
    total: int,
    url: str,
    status: str,
    *,
    saved: Path | None = None,
    reason: str = "",
) -> None:
    parts = [f"[{index}/{total}] avatar={url}", f"status={status}"]
    if saved is not None:
        parts.append(f"saved={saved.as_posix()}")
    if reason:
        parts.append(f"reason={reason}")
    print(" ".join(parts))


def record_avatar_download_result(
    result: AvatarDownloadResult,
    manifest: dict[str, Any],
    avatars: dict[str, Any],
    config: PrepareAssetsConfig,
    manifest_file: Path,
    counters: dict[str, int],
) -> None:
    job = result.job
    if result.success:
        extension = avatar_extension(job.url, result.detail)
        final_path = avatar_dir(config.avatar_cache_dir) / avatar_filename(job.url, extension)
        if final_path != job.path:
            job.path.replace(final_path)
        avatars[job.url] = {
            "status": "ok",
            "local_path": cache_avatar_relpath(config.avatar_cache_dir, final_path),
            "content_type": result.detail,
        }
        counters["downloaded"] += 1
        print_avatar_progress(job.index, job.total, job.url, "downloaded", saved=final_path)
    else:
        avatars[job.url] = {"status": "failed", "local_path": "", "error": result.detail}
        counters["failed"] += 1
        print_avatar_progress(
            job.index, job.total, job.url, "failed", saved=job.path, reason=result.detail
        )
    save_manifest(manifest_file, manifest)


async def drain_completed_downloads(
    pending: set[asyncio.Task[AvatarDownloadResult]],
    manifest: dict[str, Any],
    avatars: dict[str, Any],
    config: PrepareAssetsConfig,
    manifest_file: Path,
    counters: dict[str, int],
    *,
    timeout: float | None,
) -> set[asyncio.Task[AvatarDownloadResult]]:
    if not pending:
        if timeout is not None and timeout > 0:
            await asyncio.sleep(timeout)
        return pending
    done, remaining = await asyncio.wait(
        pending, timeout=timeout, return_when=asyncio.FIRST_COMPLETED
    )
    for task in done:
        record_avatar_download_result(
            task.result(), manifest, avatars, config, manifest_file, counters
        )
    return set(remaining)


async def wait_for_next_download_slot(
    pending: set[asyncio.Task[AvatarDownloadResult]],
    manifest: dict[str, Any],
    avatars: dict[str, Any],
    config: PrepareAssetsConfig,
    manifest_file: Path,
    counters: dict[str, int],
    earliest_start: float,
) -> set[asyncio.Task[AvatarDownloadResult]]:
    loop = asyncio.get_running_loop()
    while True:
        remaining = earliest_start - loop.time()
        if remaining <= 0:
            return pending
        pending = await drain_completed_downloads(
            pending,
            manifest,
            avatars,
            config,
            manifest_file,
            counters,
            timeout=remaining,
        )


async def wait_for_all_downloads(
    pending: set[asyncio.Task[AvatarDownloadResult]],
    manifest: dict[str, Any],
    avatars: dict[str, Any],
    config: PrepareAssetsConfig,
    manifest_file: Path,
    counters: dict[str, int],
) -> None:
    while pending:
        pending = await drain_completed_downloads(
            pending,
            manifest,
            avatars,
            config,
            manifest_file,
            counters,
            timeout=None,
        )


async def prepare_avatar_cache_async(
    graph_data: dict[str, Any], config: PrepareAssetsConfig
) -> dict[str, Any]:
    migrate_legacy_avatar_cache_if_needed(config.avatar_cache_dir)
    manifest_file = manifest_path(config.avatar_cache_dir)
    manifest = load_manifest(manifest_file)
    avatars: dict[str, Any] = manifest.setdefault("avatars", {})
    urls = collect_icon_urls(graph_data)
    counters = {"downloaded": 0, "reused": 0, "failed": 0, "skipped": 0}
    pending: set[asyncio.Task[AvatarDownloadResult]] = set()
    scheduled_downloads = 0
    last_download_started_at: float | None = None
    loop = asyncio.get_running_loop()

    for index, url in enumerate(urls, start=1):
        record = avatars.get(url) or {}
        local_path_value = str(record.get("local_path") or "")
        if (
            local_path_value
            and (config.avatar_cache_dir / local_path_value).exists()
            and record.get("status") == "ok"
        ):
            counters["reused"] += 1
            print_avatar_progress(
                index, len(urls), url, "cache_hit", saved=config.avatar_cache_dir / local_path_value
            )
            continue
        if not config.download_avatars:
            avatars[url] = {
                "status": "skipped",
                "local_path": "",
                "error": "avatar download disabled",
            }
            counters["skipped"] += 1
            print_avatar_progress(
                index, len(urls), url, "skipped", reason="avatar_download_disabled"
            )
            continue
        if (
            config.max_avatar_downloads is not None
            and scheduled_downloads >= config.max_avatar_downloads
        ):
            counters["skipped"] += 1
            print_avatar_progress(index, len(urls), url, "skipped", reason="download_limit")
            continue

        if last_download_started_at is not None and config.request_delay_seconds > 0:
            pending = await wait_for_next_download_slot(
                pending,
                manifest,
                avatars,
                config,
                manifest_file,
                counters,
                last_download_started_at + config.request_delay_seconds,
            )
        guessed_path = avatar_dir(config.avatar_cache_dir) / avatar_filename(url)
        job = AvatarDownloadJob(index, len(urls), url, guessed_path, config.timeout_seconds)
        pending.add(asyncio.create_task(asyncio.to_thread(run_avatar_download, job)))
        scheduled_downloads += 1
        last_download_started_at = loop.time()
        pending = await drain_completed_downloads(
            pending,
            manifest,
            avatars,
            config,
            manifest_file,
            counters,
            timeout=0,
        )

    await wait_for_all_downloads(pending, manifest, avatars, config, manifest_file, counters)
    save_manifest(manifest_file, manifest)
    return {
        "avatar_urls": len(urls),
        "downloaded": counters["downloaded"],
        "reused": counters["reused"],
        "failed": counters["failed"],
        "skipped": counters["skipped"],
        "manifest": manifest_file.as_posix(),
    }


def prepare_avatar_cache(graph_data: dict[str, Any], config: PrepareAssetsConfig) -> dict[str, Any]:
    return asyncio.run(prepare_avatar_cache_async(graph_data, config))


def rewrite_icons_to_avatar_keys(
    graph_data: dict[str, Any], avatar_cache_dir: Path
) -> dict[str, Any]:
    manifest = load_manifest(manifest_path(avatar_cache_dir))
    avatars = manifest.get("avatars") or {}

    def key_for_icon(value: Any) -> str:
        url = str(value or "").strip()
        if not url:
            return ""
        record = avatars.get(url) or {}
        if record.get("status") == "ok" and record.get("local_path"):
            return avatar_key(url)
        return ""

    for node in graph_data.get("nodes", []):
        node["avatar_key"] = key_for_icon(node.get("icon"))
        node["icon"] = ""
    for target in graph_data.get("targets", []):
        target["avatar_key"] = key_for_icon(target.get("icon"))
        target["icon"] = ""
    return graph_data


def rewrite_icons_to_local(
    graph_data: dict[str, Any], output_dir: Path, avatar_cache_dir: Path
) -> dict[str, Any]:
    """Compatibility wrapper for older tests and one-off scripts."""
    manifest = load_manifest(manifest_path(avatar_cache_dir))
    avatars = manifest.get("avatars") or {}

    def local_icon(value: Any) -> str:
        url = str(value or "").strip()
        if not url:
            return ""
        record = avatars.get(url) or {}
        if record.get("status") == "ok" and record.get("local_path"):
            return site_avatar_relpath(output_dir, avatar_cache_dir, str(record["local_path"]))
        return ""

    for node in graph_data.get("nodes", []):
        node["icon"] = local_icon(node.get("icon"))
    for target in graph_data.get("targets", []):
        target["icon"] = local_icon(target.get("icon"))
    return graph_data


def copy_vendor(config: PrepareAssetsConfig) -> Path:
    vendor_output = vendor_asset_path(config.output_dir)
    vendor_output.parent.mkdir(parents=True, exist_ok=True)
    if config.vendor_path.exists():
        shutil.copy2(config.vendor_path, vendor_output)
    else:
        vendor_output.write_text(
            read_vendor_script(config.vendor_path), encoding="utf-8", newline="\n"
        )
    license_path = config.vendor_path.with_name("force-graph.LICENSE")
    if license_path.exists():
        shutil.copy2(license_path, vendor_output.with_name("force-graph.LICENSE"))
    return vendor_output


def prepare_assets(config: PrepareAssetsConfig) -> dict[str, Any]:
    with connect_database(config.db_path) as connection:
        graph_data = build_graph_data(connection, demo=config.demo)

    config.output_dir.mkdir(parents=True, exist_ok=True)
    vendor_output = copy_vendor(config)
    avatar_result = prepare_avatar_cache(graph_data, config)
    graph_data = rewrite_icons_to_avatar_keys(graph_data, config.avatar_cache_dir)
    graph_data["avatar_profile"] = (
        "demo"
        if config.demo
        else (
            "mvp"
            if config.db_path == DEFAULT_MVP_DB_PATH or config.output_dir == DEFAULT_MVP_OUTPUT_DIR
            else "full"
        )
    )
    graph_output = graph_asset_path(config.output_dir)
    graph_output.parent.mkdir(parents=True, exist_ok=True)
    graph_output.write_text(graph_data_script(graph_data), encoding="utf-8", newline="\n")

    return {
        "db": config.db_path.as_posix(),
        "output_dir": config.output_dir.as_posix(),
        "graph_data": graph_output.as_posix(),
        "vendor": vendor_output.as_posix(),
        "avatar_cache_dir": config.avatar_cache_dir.as_posix(),
        "nodes": len(graph_data["nodes"]),
        "edges": len(graph_data["edges"]),
        "songs": len(graph_data["songs"]),
        "targets": len(graph_data["targets"]),
        **avatar_result,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare static graph site assets from SQLite.")
    parser.add_argument("--db", type=Path, default=None, help="SQLite database path.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Site directory.")
    parser.add_argument(
        "--vendor", type=Path, default=DEFAULT_VENDOR_PATH, help="Local force-graph runtime path."
    )
    parser.add_argument(
        "--avatar-cache-dir",
        type=Path,
        default=DEFAULT_AVATAR_CACHE_DIR,
        help="Raw avatar cache directory.",
    )
    parser.add_argument(
        "--mvp", action="store_true", help="Use the MVP database and site_mvp output directory."
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Use the full database and site_demo output directory, seeded by the MVP 10 target artists plus their incident edges.",
    )
    parser.add_argument(
        "--skip-avatar-download",
        action="store_true",
        help="Do not download avatars; write graph data with empty local avatar paths.",
    )
    parser.add_argument(
        "--max-avatar-downloads",
        type=int,
        default=None,
        help="Maximum number of new avatars to download in this run.",
    )
    parser.add_argument(
        "--request-delay",
        type=float,
        default=DEFAULT_REQUEST_DELAY_SECONDS,
        help="Minimum interval between starting avatar requests, in seconds.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Per-avatar request timeout, in seconds.",
    )
    return parser.parse_args()


def _main() -> None:
    ensure_utf8_stdout()
    args = parse_args()
    if args.mvp and args.demo:
        raise ValueError("--mvp and --demo cannot be used together.")
    db_path = args.db or (DEFAULT_MVP_DB_PATH if args.mvp else DEFAULT_DB_PATH)
    output_dir = args.output_dir or (
        DEFAULT_DEMO_OUTPUT_DIR
        if args.demo
        else DEFAULT_MVP_OUTPUT_DIR if args.mvp else DEFAULT_OUTPUT_DIR
    )
    result = prepare_assets(
        PrepareAssetsConfig(
            db_path=db_path,
            output_dir=output_dir,
            vendor_path=args.vendor,
            avatar_cache_dir=args.avatar_cache_dir,
            download_avatars=not args.skip_avatar_download,
            max_avatar_downloads=args.max_avatar_downloads,
            request_delay_seconds=max(0.0, args.request_delay),
            timeout_seconds=max(0.1, args.timeout),
            demo=args.demo,
        )
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()
