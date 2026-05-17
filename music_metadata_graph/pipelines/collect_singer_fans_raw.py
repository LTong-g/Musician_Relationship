from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass
from dataclasses import replace as dataclass_replace
from pathlib import Path
from typing import Any

from qqmusic_api import Client
from qqmusic_api.modules.singer import AreaType, GenreType, SexType

from music_metadata_graph.pipelines.defaults import MVP_SINGER_LIMIT
from music_metadata_graph.pipelines.import_singer_list_to_db import DEFAULT_RAW_DIR as DEFAULT_SINGER_LIST_RAW_DIR
from music_metadata_graph.pipelines.import_singer_list_to_db import filter_singers_by_area
from music_metadata_graph.pipelines.import_singer_list_to_db import load_singers
from music_metadata_graph.pipelines.import_singer_list_to_db import singer_fans_summary_path
from music_metadata_graph.run_log import run_with_log


DEFAULT_RAW_DIR = Path("data/raw/qqmusic")
DEFAULT_PAGE_SIZE = 80
DEFAULT_BATCH_SIZE = 20
REQUEST_RATE = 0.5
REQUEST_CAPACITY = 1
DEFAULT_AREAS = (AreaType.TAIWAN, AreaType.CHINA)
DEFAULT_SEX = SexType.ALL
DEFAULT_GENRE = GenreType.ALL


@dataclass(frozen=True)
class SingerTarget:
    mid: str
    name: str


@dataclass(frozen=True)
class FetchFailure:
    mid: str
    name: str
    path: Path
    reason: str


@dataclass(frozen=True)
class CollectConfig:
    raw_dir: Path
    singer_list_raw_dir: Path
    areas: tuple[AreaType, ...]
    sex: SexType
    genre: GenreType
    batch_size: int
    force: bool
    mvp: bool = False


def ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def enum_label(value: AreaType | SexType | GenreType) -> str:
    return value.name.lower()


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def list_cache_path(config: CollectConfig, area: AreaType) -> Path:
    return (
        config.raw_dir
        / "singer_fans_list"
        / f"area_{enum_label(area)}_sex_{enum_label(config.sex)}_genre_{enum_label(config.genre)}.json"
    )


def info_cache_path(config: CollectConfig, mid: str) -> Path:
    return config.raw_dir / "singer_fans_info" / f"{mid}.json"


def target_singers(config: CollectConfig) -> list[SingerTarget]:
    rows = filter_singers_by_area(load_singers(config.singer_list_raw_dir))
    if config.mvp:
        rows = rows[:MVP_SINGER_LIMIT]
    targets: list[SingerTarget] = []
    seen: set[str] = set()
    for row in rows:
        mid = str(row.get("mid") or "").strip()
        name = str(row.get("name") or "").strip()
        if not mid or mid in seen:
            continue
        seen.add(mid)
        targets.append(SingerTarget(mid=mid, name=name))
    return targets


def list_item_mid(item: dict[str, Any]) -> str:
    return str(item.get("singer_mid") or item.get("mid") or "").strip()


def list_item_name(item: dict[str, Any]) -> str:
    return str(item.get("singer_name") or item.get("name") or "").strip()


def list_item_fans_num(item: dict[str, Any]) -> int | None:
    raw_value = item.get("concernNum")
    if raw_value is None:
        raw_value = item.get("concern_num")
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def info_fans_num(payload: dict[str, Any]) -> int | None:
    fans = ((payload.get("Info") or {}).get("FansNum") or {})
    try:
        value = int(fans.get("Num"))
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def info_has_entry(payload: dict[str, Any]) -> int:
    fans = ((payload.get("Info") or {}).get("FansNum") or {})
    try:
        return int(fans.get("HasEntry") or 0)
    except (TypeError, ValueError):
        return 0


def list_fans_by_mid(payloads: list[tuple[dict[str, Any], Path]]) -> dict[str, dict[str, Any]]:
    fans: dict[str, dict[str, Any]] = {}
    for payload, path in payloads:
        for group in ("singerlist", "hotlist"):
            items = payload.get(group)
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                mid = list_item_mid(item)
                fans_num = list_item_fans_num(item)
                if not mid or fans_num is None:
                    continue
                fans.setdefault(
                    mid,
                    {
                        "fans_num": fans_num,
                        "name": list_item_name(item),
                        "source": "qqmusic.singer.get_singer_list.concernNum",
                        "raw_json_path": path.as_posix(),
                        "has_entry": 1,
                    },
                )
    return fans


async def execute_or_load_list(
    client: Client,
    config: CollectConfig,
    area: AreaType,
) -> tuple[dict[str, Any], str, Path]:
    path = list_cache_path(config, area)
    if path.exists() and not config.force:
        return load_json(path), "cache_hit", path
    request = dataclass_replace(
        client.singer.get_singer_list(area=area, sex=config.sex, genre=config.genre),
        response_model=None,
    )
    result = await client.execute(request)
    payload = result.model_dump(mode="json") if hasattr(result, "model_dump") else result
    dump_json(path, payload)
    return payload, "fetched", path


async def execute_or_load_info_batch(
    client: Client,
    config: CollectConfig,
    targets: list[SingerTarget],
) -> tuple[list[tuple[int, SingerTarget, dict[str, Any], str, Path]], list[FetchFailure]]:
    loaded: list[tuple[int, SingerTarget, dict[str, Any], str, Path]] = []
    pending: list[tuple[int, SingerTarget, Path, Any]] = []
    failures: list[FetchFailure] = []

    for index, target in enumerate(targets):
        path = info_cache_path(config, target.mid)
        if path.exists() and not config.force:
            try:
                loaded.append((index, target, load_json(path), "cache_hit", path))
                continue
            except (OSError, json.JSONDecodeError):
                pass
        request = dataclass_replace(client.singer.get_info(target.mid), response_model=None)
        pending.append((index, target, path, request))

    for start in range(0, len(pending), config.batch_size):
        batch = pending[start : start + config.batch_size]
        requests = [request for _, _, _, request in batch]
        try:
            results = await client.gather(requests, batch_size=len(requests))
            for (index, target, path, _), result in zip(batch, results):
                payload = result.model_dump(mode="json") if hasattr(result, "model_dump") else result
                dump_json(path, payload)
                loaded.append((index, target, payload, "fetched", path))
        except Exception as batch_exc:
            for index, target, path, request in batch:
                try:
                    result = await client.execute(request)
                    payload = result.model_dump(mode="json") if hasattr(result, "model_dump") else result
                    dump_json(path, payload)
                    loaded.append((index, target, payload, "fetched", path))
                except Exception as single_exc:
                    failures.append(
                        FetchFailure(
                            mid=target.mid,
                            name=target.name,
                            path=path,
                            reason=f"batch_error={type(batch_exc).__name__}: {batch_exc}; "
                            f"single_error={type(single_exc).__name__}: {single_exc}",
                        )
                    )

    loaded.sort(key=lambda item: item[0])
    return loaded, failures


def write_summary(config: CollectConfig, rows: list[dict[str, Any]]) -> Path:
    path = singer_fans_summary_path(config.raw_dir, mvp=config.mvp)
    dump_json(path, {"rows": rows})
    return path


async def collect(config: CollectConfig) -> None:
    targets = target_singers(config)
    if not targets:
        raise ValueError(f"No area 0/1 singer targets found in raw JSON: {config.singer_list_raw_dir}")

    client = Client(rate=REQUEST_RATE, capacity=REQUEST_CAPACITY)
    list_payloads: list[tuple[dict[str, Any], Path]] = []
    list_fetched = 0
    list_cache_hits = 0
    try:
        for index, area in enumerate(config.areas, 1):
            payload, status, path = await execute_or_load_list(client, config, area)
            list_payloads.append((payload, path))
            list_fetched += int(status == "fetched")
            list_cache_hits += int(status == "cache_hit")
            singer_rows = len(payload.get("singerlist") or [])
            hot_rows = len(payload.get("hotlist") or [])
            print(
                f"[{index}/{len(config.areas)}] area={area.name} status={status} "
                f"singerlist={singer_rows} hotlist={hot_rows} saved={path.as_posix()}"
            )

        list_fans = list_fans_by_mid(list_payloads)
        missing_targets = [target for target in targets if target.mid not in list_fans]
        loaded_info, failures = await execute_or_load_info_batch(client, config, missing_targets)
    finally:
        await client.close()

    summary_rows: list[dict[str, Any]] = []
    for index, target in enumerate(targets, 1):
        row = list_fans.get(target.mid)
        if row is not None:
            summary_rows.append(
                {
                    "mid": target.mid,
                    "name": target.name,
                    "fans_num": row["fans_num"],
                    "source": row["source"],
                    "has_entry": row["has_entry"],
                    "raw_json_path": row["raw_json_path"],
                    "status": "covered_by_list",
                }
            )

    for loaded_index, target, payload, status, path in loaded_info:
        fans_num = info_fans_num(payload)
        summary_rows.append(
            {
                "mid": target.mid,
                "name": target.name,
                "fans_num": fans_num,
                "source": "qqmusic.singer.get_info.FansNum.Num",
                "has_entry": info_has_entry(payload),
                "raw_json_path": path.as_posix(),
                "status": status,
            }
        )
        print(
            f"[{loaded_index + 1}/{len(targets)}] mid={target.mid} name={target.name} "
            f"status={status} fans_num={fans_num or ''} saved={path.as_posix()}"
        )

    for failure in failures:
        print(f"mid={failure.mid} name={failure.name} status=failed reason={failure.reason} saved={failure.path.as_posix()}")

    summary_rows.sort(key=lambda row: (str(row["mid"])))
    summary_path = write_summary(config, summary_rows)
    covered = sum(1 for row in summary_rows if row.get("fans_num") is not None)
    print(
        json.dumps(
            {
                "target_singers": len(targets),
                "areas": [area.name for area in config.areas],
                "list_fetched": list_fetched,
                "list_cache_hits": list_cache_hits,
                "covered_by_list": len(targets) - len(missing_targets),
                "missing_after_list": len(missing_targets),
                "info_fetched_or_loaded": len(loaded_info),
                "failed_info_fetches": len(failures),
                "covered_fans_num": covered,
                "summary_json": summary_path.as_posix(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if failures:
        failed = ", ".join(f"{failure.name}({failure.mid})" for failure in failures)
        raise RuntimeError(f"Failed to fetch {len(failures)} singer fans request(s). Rerun to continue. Failed singers: {failed}")


def parse_csv_values(values: list[str] | None) -> tuple[str, ...]:
    if not values:
        return ()
    parsed: list[str] = []
    for value in values:
        parsed.extend(part.strip() for part in value.split(",") if part.strip())
    return tuple(parsed)


def parse_area_list(values: list[str] | None) -> tuple[AreaType, ...]:
    parsed_values = parse_csv_values(values)
    if not parsed_values:
        return DEFAULT_AREAS
    result: list[AreaType] = []
    seen: set[AreaType] = set()
    for raw_value in parsed_values:
        key = raw_value.upper().replace("-", "_")
        try:
            item = AreaType[key]
        except KeyError:
            try:
                item = AreaType(int(raw_value))
            except ValueError as exc:
                choices = ", ".join(member.name for member in AreaType)
                raise ValueError(f"Invalid AreaType value: {raw_value}. Choices: {choices}") from exc
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return tuple(result)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect QQ Music approximate singer fan-count raw JSON.")
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--singer-list-raw-dir", type=Path, default=DEFAULT_SINGER_LIST_RAW_DIR)
    parser.add_argument("--area", action="append", help="AreaType list for quick list fan-count requests. Defaults to TAIWAN,CHINA.")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="Maximum request descriptors per get_info batch.")
    parser.add_argument("--force", action="store_true", help="Refetch and overwrite cached fan-count raw JSON.")
    parser.add_argument("--mvp", action="store_true", help="MVP mode: only require fan counts for the first 10 area 0/1 singer targets.")
    args = parser.parse_args()
    try:
        args.areas = parse_area_list(args.area)
    except ValueError as exc:
        parser.error(str(exc))
    return args


def _main() -> None:
    ensure_utf8_stdout()
    args = parse_args()
    asyncio.run(
        collect(
            CollectConfig(
                raw_dir=args.raw_dir,
                singer_list_raw_dir=args.singer_list_raw_dir,
                areas=args.areas,
                sex=DEFAULT_SEX,
                genre=DEFAULT_GENRE,
                batch_size=args.batch_size,
                force=args.force,
                mvp=args.mvp,
            )
        )
    )


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()
