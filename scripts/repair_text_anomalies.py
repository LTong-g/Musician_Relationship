from __future__ import annotations
import argparse
import ast
from dataclasses import dataclass
from pathlib import Path

CORE_MARKDOWN = ("AGENTS.md", "README.md", "develop_log.md")
SUPPORTED_SUFFIXES = {".md", ".py"}
SKIP_PARTS = {".git", "__pycache__", "node_modules"}
ALLOWED_CONTROLS = {"\r", "\n", "\t"}


@dataclass(frozen=True)
class TextReport:
    path: Path
    size: int
    lines: int
    nonempty_lines: int
    suffix: str
    crcrlf_count: int
    replacement_chars: int
    hidden_controls: tuple[int, ...]
    max_blank_run: int
    structural_blank_issues: int
    python_blank_issues: int
    bloated_lines: bool
    syntax_error: str | None = None

    @property
    def has_anomaly(self) -> bool:
        return (
            self.crcrlf_count > 0
            or self.replacement_chars > 0
            or bool(self.hidden_controls)
            or self.structural_blank_issues > 0
            or self.python_blank_issues > 0
            or self.bloated_lines
            or self.syntax_error is not None
            or (self.suffix == ".md" and self.max_blank_run > 1)
        )


def _read_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def _write_crlf(path: Path, text: str) -> None:
    # Byte-level write prevents Windows text translation from producing CRCRLF.
    path.write_bytes(
        text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n").encode("utf-8")
    )


def _max_blank_run(text: str, *, ignore_fenced_code: bool) -> int:
    max_run = 0
    current_run = 0
    in_fence = False
    fence_marker: str | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if ignore_fenced_code and (stripped.startswith("```") or stripped.startswith("~~~")):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = None
            current_run = 0
            continue

        if ignore_fenced_code and in_fence:
            continue

        if stripped:
            current_run = 0
        else:
            current_run += 1
            max_run = max(max_run, current_run)

    return max_run


def _line_kind(value: str) -> str:
    stripped_value = value.strip()
    if stripped_value.startswith("#"):
        return "heading"
    if stripped_value.startswith(("- ", "* ", "+ ")):
        return "list"
    if stripped_value.startswith(">"):
        return "quote"
    if stripped_value.startswith("|"):
        return "table"
    if stripped_value.startswith(("```", "~~~")):
        return "fence"
    return "text"


def _markdown_structural_blank_issues(text: str) -> int:
    lines = text.splitlines()
    issues = 0
    in_fence = False
    fence_marker: str | None = None
    previous_nonblank: str | None = None
    blank_count = 0

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = None
            previous_nonblank = line
            blank_count = 0
            continue

        if in_fence:
            continue

        if not stripped:
            blank_count += 1
            continue

        if previous_nonblank is not None and blank_count > 0:
            previous_kind = _line_kind(previous_nonblank)
            current_kind = _line_kind(line)
            if (previous_kind == "heading" and current_kind == "list") or (
                previous_kind == "list" and current_kind == "list"
            ):
                issues += 1
        previous_nonblank = line
        blank_count = 0

    return issues


def compact_markdown(text: str, *, core_document: bool) -> str:
    lines = text.splitlines()
    out: list[str] = []
    blank_pending = False
    in_fence = False
    fence_marker: str | None = None

    def should_keep_pending_blank(previous: str, current: str) -> bool:
        if not core_document:
            return True
        previous_kind = _line_kind(previous)
        current_kind = _line_kind(current)
        if previous_kind == "heading" and current_kind == "list":
            return False
        if previous_kind == "list" and current_kind == "list":
            return False
        return True

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_fence:
                if (
                    blank_pending
                    and out
                    and out[-1] != ""
                    and should_keep_pending_blank(out[-1], line)
                ):
                    out.append("")
                blank_pending = False
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = None
            out.append(line.rstrip())
            continue

        if in_fence:
            out.append(line.rstrip())
            continue

        if not stripped:
            blank_pending = True
            continue

        if blank_pending and out and out[-1] != "" and should_keep_pending_blank(out[-1], line):
            out.append("")
        out.append(line.strip())
        blank_pending = False

    return "\n".join(out).rstrip() + "\n"


def scan_text(path: Path) -> TextReport:
    data = path.read_bytes()
    text = data.decode("utf-8", errors="strict")
    lines = text.splitlines()
    nonempty = sum(1 for line in lines if line.strip())
    hidden_controls = tuple(
        sorted({ord(char) for char in text if ord(char) < 32 and char not in ALLOWED_CONTROLS})
    )
    suffix = path.suffix.lower()
    line_count = len(lines)
    bloated_lines = nonempty > 0 and line_count > max(500, nonempty * 3)
    structural = 0
    if suffix == ".md" and path.name in CORE_MARKDOWN:
        structural = _markdown_structural_blank_issues(text)
    syntax_error = None
    if suffix == ".py":
        try:
            ast.parse(text.lstrip("\ufeff"), filename=str(path))
        except SyntaxError as exc:
            syntax_error = f"{exc.lineno}:{exc.offset}:{exc.msg}"
    return TextReport(
        path=path,
        size=path.stat().st_size,
        lines=line_count,
        nonempty_lines=nonempty,
        suffix=suffix,
        crcrlf_count=data.count(b"\r\r\n"),
        replacement_chars=text.count("\ufffd"),
        hidden_controls=hidden_controls,
        max_blank_run=_max_blank_run(text, ignore_fenced_code=suffix == ".md"),
        structural_blank_issues=structural,
        python_blank_issues=0,
        bloated_lines=bloated_lines,
        syntax_error=syntax_error,
    )


def repair_text(path: Path) -> bool:
    before = _read_utf8(path)
    suffix = path.suffix.lower()
    if suffix == ".md":
        after = compact_markdown(before, core_document=path.name in CORE_MARKDOWN)
    elif suffix == ".py":
        after = before.replace("\r\n", "\n").replace("\r", "\n")
        ast.parse(after.lstrip("\ufeff"), filename=str(path))
    else:
        after = before.replace("\r\n", "\n").replace("\r", "\n")
    if after == before and path.read_bytes().count(b"\r\r\n") == 0:
        return False
    _write_crlf(path, after)
    if suffix == ".py":
        ast.parse(_read_utf8(path).lstrip("\ufeff"), filename=str(path))
    return True


def _iter_all_targets() -> list[Path]:
    return sorted(
        path
        for suffix in SUPPORTED_SUFFIXES
        for path in Path(".").rglob(f"*{suffix}")
        if not any(part in SKIP_PARTS for part in path.parts)
    )


def _resolve_targets(args: argparse.Namespace) -> list[Path]:
    if args.all:
        return _iter_all_targets()
    if args.paths:
        return [Path(path) for path in args.paths]
    return [Path(path) for path in CORE_MARKDOWN if Path(path).exists()]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scan and repair UTF-8 text spacing/newline anomalies."
    )
    parser.add_argument("paths", nargs="*", help="Files to scan. Defaults to core Markdown docs.")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Scan all supported text files below the current directory.",
    )
    parser.add_argument(
        "--fix", action="store_true", help="Repair supported spacing/newline anomalies."
    )
    args = parser.parse_args()

    exit_code = 0
    for path in _resolve_targets(args):
        if not path.exists() or not path.is_file():
            print(f"missing path={path}")
            exit_code = 1
            continue
        if path.suffix.lower() not in SUPPORTED_SUFFIXES:
            print(f"skip unsupported path={path}")
            continue

        before = scan_text(path)
        changed = False
        if args.fix and (
            before.crcrlf_count > 0
            or (before.suffix == ".md" and before.max_blank_run > 1)
            or before.structural_blank_issues > 0
            or before.python_blank_issues > 0
            or before.bloated_lines
        ):
            changed = repair_text(path)
        report = scan_text(path)
        status = "changed" if changed else "ok"
        if report.has_anomaly:
            status = "anomaly"
            exit_code = 1
        print(
            f"{status} path={report.path.as_posix()} suffix={report.suffix} size={report.size} "
            f"lines={report.lines} nonempty={report.nonempty_lines} crcrlf={report.crcrlf_count} "
            f"max_blank_run={report.max_blank_run} structural_blank_issues={report.structural_blank_issues} "
            f"python_blank_issues={report.python_blank_issues} "
            f"controls={list(report.hidden_controls)} replacement={report.replacement_chars} "
            f"bloated={report.bloated_lines} syntax_error={report.syntax_error}"
        )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
