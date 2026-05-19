from __future__ import annotations
import argparse
import asyncio
import itertools
import json
import sys
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from music_metadata_graph.run_log import run_with_log
from typing import Any
from qqmusic_api import Client
from qqmusic_api.modules.singer import AreaType, GenreType, IndexType, SexType

DEFAULT_RAW_DIR = Path("data/raw/qqmusic")

DEFAULT_PAGE_SIZE = 80

REQUEST_RATE = 0.5

REQUEST_CAPACITY = 1
REQUEST_BATCH_SIZE = 20


@dataclass(frozen=True)
class CollectConfig:
    raw_dir: Path

    page_size: int

    max_pages: int | None

    force: bool

    areas: tuple[AreaType, ...]

    sexes: tuple[SexType, ...]

    genres: tuple[GenreType, ...]

    indexes: tuple[IndexType, ...]


@dataclass(frozen=True)
class FilterCombination:
    area: AreaType

    sex: SexType

    genre: GenreType

    index: IndexType


def ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    text = json.dumps(payload, ensure_ascii=False, indent=2)

    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def enum_label(value: IntEnum) -> str:
    return value.name.lower()


def combination_dir_name(combination: FilterCombination) -> str:
    return (
        f"area_{enum_label(combination.area)}"
        f"_sex_{enum_label(combination.sex)}"
        f"_genre_{enum_label(combination.genre)}"
        f"_index_{enum_label(combination.index)}"
    )


def cache_path(config: CollectConfig, combination: FilterCombination, page: int) -> Path:
    return (
        config.raw_dir
        / "singer_list_index"
        / combination_dir_name(combination)
        / f"page_{page:04d}_size_{config.page_size}.json"
    )


async def execute_or_load(
    client: Client,
    config: CollectConfig,
    combination: FilterCombination,
    page: int,
) -> tuple[dict[str, Any], str, Path]:
    path = cache_path(config, combination, page)

    if path.exists() and not config.force:
        return load_json(path), "cache_hit", path

    request = client.singer.get_singer_list_index(
        area=combination.area,
        sex=combination.sex,
        genre=combination.genre,
        index=combination.index,
        page=page,
        num=config.page_size,
    )

    result = await client.execute(request)

    payload = result.model_dump(mode="json") if hasattr(result, "model_dump") else result

    dump_json(path, payload)

    return payload, "fetched", path


def build_request(
    client: Client, config: CollectConfig, combination: FilterCombination, page: int
) -> Any:
    return client.singer.get_singer_list_index(
        area=combination.area,
        sex=combination.sex,
        genre=combination.genre,
        index=combination.index,
        page=page,
        num=config.page_size,
    )


async def execute_or_load_pages(
    client: Client,
    config: CollectConfig,
    combination: FilterCombination,
    pages: list[int],
) -> list[tuple[int, dict[str, Any], str, Path]]:
    loaded: list[tuple[int, dict[str, Any], str, Path]] = []
    pending: list[tuple[int, Path, Any]] = []
    for page in pages:
        path = cache_path(config, combination, page)
        if path.exists() and not config.force:
            loaded.append((page, load_json(path), "cache_hit", path))
            continue
        pending.append((page, path, build_request(client, config, combination, page)))

    if pending:
        results = await client.gather(
            [request for _, _, request in pending], batch_size=REQUEST_BATCH_SIZE
        )
        for (page, path, _request), result in zip(pending, results, strict=True):
            payload = result.model_dump(mode="json") if hasattr(result, "model_dump") else result
            dump_json(path, payload)
            loaded.append((page, payload, "fetched", path))

    return sorted(loaded, key=lambda item: item[0])


def combinations(config: CollectConfig) -> tuple[FilterCombination, ...]:
    return tuple(
        FilterCombination(area=area, sex=sex, genre=genre, index=index)
        for area, sex, genre, index in itertools.product(
            config.areas,
            config.sexes,
            config.genres,
            config.indexes,
        )
    )


async def collect_combination(
    client: Client, config: CollectConfig, combination: FilterCombination
) -> dict[str, Any]:
    page = 1

    total: int | None = None

    total_rows = 0

    pages = 0

    fetched = 0

    cache_hits = 0

    while True:
        if config.max_pages is not None and page > config.max_pages:
            break

        payload, status, path = await execute_or_load(client, config, combination, page)

        singers = payload.get("singerlist") or []

        if total is None and payload.get("total") is not None:
            total = int(payload["total"])

        pages += 1

        total_rows += len(singers)

        fetched += int(status == "fetched")

        cache_hits += int(status == "cache_hit")

        print(
            f"combination={combination_dir_name(combination)} page={page} "
            f"status={status} singers={len(singers)} total={total} saved={path.as_posix()}"
        )

        if not singers:
            break

        if total is not None and total_rows >= total:
            break

        if len(singers) < config.page_size:
            break

        if total is not None:
            total_pages = (total + config.page_size - 1) // config.page_size
            if config.max_pages is not None:
                total_pages = min(total_pages, config.max_pages)
            remaining_pages = list(range(page + 1, total_pages + 1))
            for loaded_page, payload, status, path in await execute_or_load_pages(
                client, config, combination, remaining_pages
            ):
                singers = payload.get("singerlist") or []
                pages += 1
                total_rows += len(singers)
                fetched += int(status == "fetched")
                cache_hits += int(status == "cache_hit")
                print(
                    f"combination={combination_dir_name(combination)} page={loaded_page} "
                    f"status={status} singers={len(singers)} total={total} saved={path.as_posix()}"
                )
            break

        page += 1

    return {
        "area": combination.area.name,
        "sex": combination.sex.name,
        "genre": combination.genre.name,
        "index": combination.index.name,
        "directory": combination_dir_name(combination),
        "pages": pages,
        "rows": total_rows,
        "api_total": total,
        "fetched_pages": fetched,
        "cache_hit_pages": cache_hits,
    }


async def collect(config: CollectConfig) -> None:
    targets = combinations(config)

    print(
        json.dumps(
            {"combinations": len(targets), "page_size": config.page_size}, ensure_ascii=False
        )
    )

    client = Client(rate=REQUEST_RATE, capacity=REQUEST_CAPACITY)

    summaries: list[dict[str, Any]] = []

    try:
        for index, combination in enumerate(targets, 1):
            print(
                f"[{index}/{len(targets)}] collect singer list: {combination_dir_name(combination)}"
            )

            summaries.append(await collect_combination(client, config, combination))

    finally:
        await client.close()

    print(
        json.dumps(
            {
                "combinations": len(summaries),
                "pages": sum(item["pages"] for item in summaries),
                "rows": sum(item["rows"] for item in summaries),
                "fetched_pages": sum(item["fetched_pages"] for item in summaries),
                "cache_hit_pages": sum(item["cache_hit_pages"] for item in summaries),
                "items": summaries,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def parse_csv_values(values: list[str] | None) -> tuple[str, ...]:
    if not values:
        return ()

    parsed: list[str] = []

    for value in values:
        parsed.extend(part.strip() for part in value.split(",") if part.strip())

    return tuple(parsed)


def parse_enum_list(
    values: list[str] | None,
    enum_type: type[AreaType] | type[SexType] | type[GenreType] | type[IndexType],
    default: tuple[Any, ...] | None = None,
) -> tuple[Any, ...]:
    parsed_values = parse_csv_values(values)

    if not parsed_values:
        return default or (enum_type.ALL,)

    result: list[Any] = []

    seen: set[Any] = set()

    for raw_value in parsed_values:
        value = raw_value.strip()

        key = value.upper().replace("-", "_")

        try:
            item = enum_type[key]

        except KeyError:
            try:
                item = enum_type(int(value))

            except ValueError as exc:
                choices = ", ".join(member.name for member in enum_type)

                raise ValueError(
                    f"Invalid {enum_type.__name__} value: {raw_value}. Choices: {choices}"
                ) from exc

        if item in seen:
            continue

        seen.add(item)

        result.append(item)

    return tuple(result)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect raw QQ Music singer list index JSON pages only."
    )

    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)

    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)

    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Limit pages for smoke tests. Omit to request the full singer list.",
    )
    parser.add_argument(
        "--mvp",
        action="store_true",
        help="MVP mode: use shared raw cache but only ensure the first page exists.",
    )

    parser.add_argument(
        "--force", action="store_true", help="Refetch and overwrite cached raw JSON pages."
    )

    parser.add_argument(
        "--area",
        action="append",
        help="AreaType list. Use names or values, repeated or comma-separated. Defaults to ALL.",
    )

    parser.add_argument(
        "--sex",
        action="append",
        help="SexType list. Use names or values, repeated or comma-separated. Defaults to ALL.",
    )

    parser.add_argument(
        "--genre",
        action="append",
        help="GenreType list. Use names or values, repeated or comma-separated. Defaults to ALL.",
    )

    parser.add_argument(
        "--index",
        action="append",
        help="IndexType list. Use names or values, repeated or comma-separated. Defaults to ALL.",
    )

    args = parser.parse_args()

    try:
        args.areas = parse_enum_list(args.area, AreaType)

        args.sexes = parse_enum_list(args.sex, SexType)

        args.genres = parse_enum_list(args.genre, GenreType)

        args.indexes = parse_enum_list(args.index, IndexType)

    except ValueError as exc:
        parser.error(str(exc))

    return args


def _main() -> None:
    ensure_utf8_stdout()

    args = parse_args()

    config = CollectConfig(
        raw_dir=args.raw_dir,
        page_size=args.page_size,
        max_pages=1 if args.mvp and args.max_pages is None else args.max_pages,
        force=args.force,
        areas=args.areas,
        sexes=args.sexes,
        genres=args.genres,
        indexes=args.indexes,
    )

    asyncio.run(collect(config))


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()
