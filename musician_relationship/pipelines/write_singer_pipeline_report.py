from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from pypinyin import lazy_pinyin


DEFAULT_INITIAL_DIR = Path("data/processed/singer_songs")
DEFAULT_VALIDATED_DIR = Path("data/processed/album_validated")
DEFAULT_OUTPUT_DIR = Path("data/processed/reports/singer_pipeline")


def ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def md_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "&#124;").replace("\r", " ").replace("\n", " ")


def singer_names(row: dict[str, Any]) -> str:
    return " / ".join(str(singer.get("name") or "") for singer in row.get("singers") or [])


def source_singer_names(row: dict[str, Any]) -> str:
    source_singers = row.get("source_singers") or []
    if source_singers:
        return " / ".join(str(singer.get("name") or "") for singer in source_singers)
    return str(row.get("source_singer_name") or "")


def validation_reasons(row: dict[str, Any]) -> str:
    validation = row.get("album_validation") or {}
    return "; ".join(str(reason) for reason in validation.get("reasons") or [])


def validation_album_singers(row: dict[str, Any]) -> str:
    validation = row.get("album_validation") or {}
    return " / ".join(str(singer.get("name") or "") for singer in validation.get("album_singers") or [])


def sort_key_text(row: dict[str, Any]) -> str:
    title = str(row.get("name") or row.get("title") or "")
    pinyin = "".join(lazy_pinyin(title)).casefold()
    return pinyin or title.casefold()


def sort_songs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            sort_key_text(row),
            str(row.get("title") or "").casefold(),
            str(row.get("time_public") or ""),
            str(row.get("id") or ""),
        ),
    )


def song_columns(row: dict[str, Any]) -> list[Any]:
    return [
        sort_key_text(row),
        row.get("name"),
        row.get("title"),
        row.get("time_public"),
        singer_names(row),
        source_singer_names(row),
        row.get("album_name"),
        row.get("id"),
        row.get("mid"),
    ]


def write_table(path: Path, title: str, description: list[str], headers: list[str], rows: list[list[Any]]) -> None:
    lines = [f"# {title}", ""]
    lines.extend(description)
    lines.append("")
    lines.append("| " + " | ".join(md_escape(header) for header in headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append("| " + " | ".join(md_escape(cell) for cell in row) + " |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(("\r\n".join(lines) + "\r\n").encode("utf-8"))


def write_summary(
    path: Path,
    singer_name: str,
    initial_dir: Path,
    validated_dir: Path,
    output_dir: Path,
    songs_all: list[dict[str, Any]],
    initial_filtered: list[dict[str, Any]],
    initial_kept: list[dict[str, Any]],
    validated_kept: list[dict[str, Any]],
    validated_rejected: list[dict[str, Any]],
    validated_review: list[dict[str, Any]],
) -> None:
    filter_counts = Counter(str(row.get("filter_reason")) for row in initial_filtered)
    review_counts = Counter(
        reason
        for row in validated_review
        for reason in (row.get("album_validation") or {}).get("reasons") or []
    )
    rejected_counts = Counter(
        reason
        for row in validated_rejected
        for reason in (row.get("album_validation") or {}).get("reasons") or []
    )
    lines = [
        f"# {singer_name} pipeline report",
        "",
        "## Counts",
        "",
        "| Step | Count | Meaning |",
        "| --- | --- | --- |",
        f"| Raw input | {len(songs_all)} | Singer song rows before filtering |",
        f"| Initial filtered | {len(initial_filtered)} | Removed by empty album or title version keyword |",
        f"| Initial kept | {len(initial_kept)} | Passed initial filter and id/mid dedupe |",
        f"| Album rejected | {len(validated_rejected)} | Automatically removed by album ownership/version validation |",
        f"| Album review | {len(validated_review)} | Needs manual review, not final kept |",
        f"| Final kept | {len(validated_kept)} | Passed album validation |",
        "",
        "## Initial Filter Reasons",
        "",
        "| Reason | Count |",
        "| --- | --- |",
    ]
    for reason, count in filter_counts.most_common():
        lines.append(f"| {md_escape(reason)} | {count} |")
    lines.extend(["", "## Album Review Reasons", "", "| Reason | Count |", "| --- | --- |"])
    if review_counts:
        for reason, count in review_counts.most_common():
            lines.append(f"| {md_escape(reason)} | {count} |")
    else:
        lines.append("| none | 0 |")
    lines.extend(["", "## Album Rejected Reasons", "", "| Reason | Count |", "| --- | --- |"])
    if rejected_counts:
        for reason, count in rejected_counts.most_common():
            lines.append(f"| {md_escape(reason)} | {count} |")
    else:
        lines.append("| none | 0 |")
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- Initial all source: `{initial_dir.as_posix()}/songs_all.json`",
            f"- Initial filtered report: `{output_dir.as_posix()}/01_initial_filtered.md`",
            f"- Initial kept report: `{output_dir.as_posix()}/02_initial_kept.md`",
            f"- Album review report: `{output_dir.as_posix()}/03_album_review.md`",
            f"- Album rejected report: `{output_dir.as_posix()}/04_album_rejected.md`",
            f"- Final kept report: `{output_dir.as_posix()}/05_final_kept.md`",
            f"- Album validation source: `{validated_dir.as_posix()}/album_validation_snapshot.json`",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(("\r\n".join(lines) + "\r\n").encode("utf-8"))


def validate_markdown_table(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if chr(0xFFFD) in text:
        errors.append("contains U+FFFD replacement character")
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        if not lines[index].startswith("|"):
            index += 1
            continue
        first = index
        if first > 0 and lines[first - 1] != "":
            errors.append(f"line {first + 1} table is not separated from previous paragraph by a blank line")
        expected = lines[first].count("|")
        while index < len(lines) and lines[index].startswith("|"):
            line = lines[index]
            if line.count("|") != expected:
                errors.append(f"line {index + 1} has {line.count('|')} pipes, expected {expected}")
            index += 1
    return errors


def run(args: argparse.Namespace) -> None:
    songs_all = load_json(args.initial_dir / "songs_all.json")
    initial_filtered = load_json(args.initial_dir / "songs_filtered.json")
    initial_kept = load_json(args.initial_dir / "songs_kept.json")
    validated_kept = load_json(args.validated_dir / "songs_kept_album_validated.json")
    validated_rejected = load_json(args.validated_dir / "songs_rejected_album_validated.json")
    validated_review = load_json(args.validated_dir / "songs_review_album_validated.json")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_summary(
        args.output_dir / "00_summary.md",
        args.singer_name,
        args.initial_dir,
        args.validated_dir,
        args.output_dir,
        songs_all,
        initial_filtered,
        initial_kept,
        validated_kept,
        validated_rejected,
        validated_review,
    )
    write_table(
        args.output_dir / "01_initial_filtered.md",
        f"{args.singer_name} initial filtered songs",
        ["Rows removed by the initial filter. Reason comes from empty album or title version keyword."],
        [
            "Filter reason",
            "Sort key",
            "Song",
            "Title",
            "Release",
            "Singers",
            "Source singer",
            "Album",
            "song_id",
            "song_mid",
        ],
        [[row.get("filter_reason"), *song_columns(row)] for row in sort_songs(initial_filtered)],
    )
    write_table(
        args.output_dir / "02_initial_kept.md",
        f"{args.singer_name} initial kept songs",
        ["Rows that passed the initial filter before album ownership validation. Sorted by pinyin/English song name."],
        ["Sort key", "Song", "Title", "Release", "Singers", "Source singer", "Album", "song_id", "song_mid"],
        [song_columns(row) for row in sort_songs(initial_kept)],
    )
    write_table(
        args.output_dir / "03_album_review.md",
        f"{args.singer_name} album validation review songs",
        ["Rows that passed the initial filter but need manual review after album ownership validation."],
        [
            "Validation reason",
            "Sort key",
            "Song",
            "Title",
            "Release",
            "Singers",
            "Album",
            "Album singers",
            "Album company",
            "song_id",
            "song_mid",
        ],
        [
            [
                validation_reasons(row),
                sort_key_text(row),
                row.get("name"),
                row.get("title"),
                row.get("time_public"),
                singer_names(row),
                row.get("album_name"),
                validation_album_singers(row),
                (row.get("album_validation") or {}).get("album_company"),
                row.get("id"),
                row.get("mid"),
            ]
            for row in sort_songs(validated_review)
        ],
    )
    write_table(
        args.output_dir / "04_album_rejected.md",
        f"{args.singer_name} album validation rejected songs",
        ["Rows automatically removed after album ownership and version validation."],
        [
            "Validation reason",
            "Sort key",
            "Song",
            "Title",
            "Release",
            "Singers",
            "Album",
            "Album singers",
            "Album company",
            "song_id",
            "song_mid",
        ],
        [
            [
                validation_reasons(row),
                sort_key_text(row),
                row.get("name"),
                row.get("title"),
                row.get("time_public"),
                singer_names(row),
                row.get("album_name"),
                validation_album_singers(row),
                (row.get("album_validation") or {}).get("album_company"),
                row.get("id"),
                row.get("mid"),
            ]
            for row in sort_songs(validated_rejected)
        ],
    )
    write_table(
        args.output_dir / "05_final_kept.md",
        f"{args.singer_name} final kept songs",
        ["Rows kept after initial filtering, dedupe, and album ownership validation. Sorted by pinyin/English song name."],
        ["Sort key", "Song", "Title", "Release", "Singers", "Source singer", "Album", "song_id", "song_mid"],
        [song_columns(row) for row in sort_songs(validated_kept)],
    )

    errors: dict[str, list[str]] = {}
    for path in sorted(args.output_dir.glob("*.md")):
        path_errors = validate_markdown_table(path)
        if path_errors:
            errors[path.name] = path_errors
    if errors:
        raise SystemExit(json.dumps(errors, ensure_ascii=False, indent=2))
    print(
        json.dumps(
            {
                "raw": len(songs_all),
                "initial_filtered": len(initial_filtered),
                "initial_kept": len(initial_kept),
                "album_rejected": len(validated_rejected),
                "album_review": len(validated_review),
                "final_kept": len(validated_kept),
                "output_dir": str(args.output_dir),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write Markdown reports for a singer pipeline run.")
    parser.add_argument("--singer-name", type=str, required=True)
    parser.add_argument("--initial-dir", type=Path, default=DEFAULT_INITIAL_DIR)
    parser.add_argument("--validated-dir", type=Path, default=DEFAULT_VALIDATED_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    ensure_utf8_stdout()
    run(parse_args())


if __name__ == "__main__":
    main()
