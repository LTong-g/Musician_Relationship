from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

DEFAULT_BASE_DIR = Path("data/raw/qqmusic/singer_similar")
DEFAULT_REQUEST_CACHE_DIR = DEFAULT_BASE_DIR / "request_cache"
DEFAULT_RUNS_DIR = DEFAULT_BASE_DIR / "runs"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2)
    path.write_text(text.replace("\n", "\r\n") + "\r\n", encoding="utf-8")


def equivalent_response(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return left.get("response") == right.get("response")


def normalize_payload(payload: dict[str, Any], source_mid: str, number: int) -> dict[str, Any]:
    source = dict(payload.get("source") or {})
    source.pop("root_mid", None)
    source.pop("root_name", None)
    source.pop("depth", None)
    source.setdefault("platform", "qqmusic")
    source.setdefault("api", "singer.get_similar")
    source["source_mid"] = source.get("source_mid") or source_mid
    source["number"] = source.get("number") or number
    return {"source": source, "response": payload.get("response", payload)}


def run_id_from_source_dir(path: Path) -> str:
    return path.name


def write_cache_payload(
    *,
    source_path: Path,
    target_path: Path,
    payload: dict[str, Any],
    conflicts: list[dict[str, str]],
) -> str:
    if target_path.exists():
        existing = read_json(target_path)
        if equivalent_response(existing, payload):
            return "reused"

        conflicts.append(
            {
                "source": source_path.as_posix(),
                "target": target_path.as_posix(),
                "reason": "same source_mid but different response",
            }
        )
        return "conflict"

    write_json(target_path, payload)
    return "migrated"


def parse_number_dir(path: Path) -> int:
    prefix = "number_"
    if path.name.startswith(prefix):
        try:
            return int(path.name[len(prefix) :])
        except ValueError:
            pass
    return 100


def flatten_numbered_cache_dirs(
    request_cache_dir: Path, conflicts: list[dict[str, str]]
) -> dict[str, int]:
    stats = {"migrated": 0, "reused": 0}

    if not request_cache_dir.exists():
        return stats

    for number_dir in sorted(request_cache_dir.glob("number_*")):
        if not number_dir.is_dir():
            continue

        number = parse_number_dir(number_dir)

        for request_path in sorted(number_dir.glob("*.json")):
            source_mid = request_path.stem
            payload = normalize_payload(read_json(request_path), source_mid, number)
            target_path = request_cache_dir / f"{source_mid}.json"
            result = write_cache_payload(
                source_path=request_path,
                target_path=target_path,
                payload=payload,
                conflicts=conflicts,
            )
            if result in stats:
                stats[result] += 1

    return stats


def migrate(base_dir: Path, request_cache_dir: Path, runs_dir: Path) -> dict[str, Any]:
    migrated_requests = 0
    reused_requests = 0
    conflicts: list[dict[str, str]] = []
    migrated_runs: list[str] = []

    flattened_stats = flatten_numbered_cache_dirs(request_cache_dir, conflicts)
    migrated_requests += flattened_stats["migrated"]
    reused_requests += flattened_stats["reused"]

    for source_dir in sorted(base_dir.iterdir() if base_dir.exists() else []):
        if not source_dir.is_dir() or source_dir.name in {"request_cache", "runs"}:
            continue

        manifest_path = source_dir / "manifest.json"
        frontier_path = source_dir / "frontier.json"
        requests_dir = source_dir / "requests"

        if not manifest_path.exists():
            continue

        manifest = read_json(manifest_path)
        number = int(manifest.get("number") or 100)

        if requests_dir.exists():
            for request_path in sorted(requests_dir.glob("*.json")):
                source_mid = request_path.stem
                payload = normalize_payload(read_json(request_path), source_mid, number)
                target_path = request_cache_dir / f"{source_mid}.json"
                result = write_cache_payload(
                    source_path=request_path,
                    target_path=target_path,
                    payload=payload,
                    conflicts=conflicts,
                )
                if result == "migrated":
                    migrated_requests += 1
                elif result == "reused":
                    reused_requests += 1

        run_dir = runs_dir / run_id_from_source_dir(source_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(manifest_path, run_dir / "manifest.json")
        if frontier_path.exists():
            shutil.copy2(frontier_path, run_dir / "frontier.json")
        migrated_runs.append(run_dir.as_posix())

    summary = {
        "base_dir": base_dir.as_posix(),
        "request_cache_dir": request_cache_dir.as_posix(),
        "runs_dir": runs_dir.as_posix(),
        "migrated_requests": migrated_requests,
        "reused_requests": reused_requests,
        "flattened_numbered_cache": flattened_stats,
        "conflict_count": len(conflicts),
        "conflicts": conflicts,
        "migrated_runs": migrated_runs,
    }

    if conflicts:
        raise RuntimeError(json.dumps(summary, ensure_ascii=False, indent=2))

    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Migrate QQ Music similar-singer raw requests into a shared request cache."
    )
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--request-cache-dir", type=Path, default=DEFAULT_REQUEST_CACHE_DIR)
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = migrate(args.base_dir, args.request_cache_dir, args.runs_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
