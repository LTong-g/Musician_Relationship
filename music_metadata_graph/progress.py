from __future__ import annotations
import sys
import time
from collections.abc import Iterable, Iterator
from typing import TypeVar
from music_metadata_graph.run_log import current_log_writer
from music_metadata_graph.run_log import current_terminal_stdout
from music_metadata_graph.run_log import utc_timestamp

T = TypeVar("T")
DEFAULT_LOG_INTERVAL_SECONDS = 120.0


def print_progress_stage(title: str) -> None:
    print(f"== {title} ==", flush=True)


def format_duration(seconds: float) -> str:
    seconds_int = max(0, int(seconds))
    hours, remainder = divmod(seconds_int, 3600)
    minutes, seconds_part = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds_part:02d}"


def format_progress_line(
    kind: str, title: str, current: int, total: int | None, started_at: float
) -> str:
    elapsed = max(0.0, time.monotonic() - started_at)
    rate = current / elapsed if elapsed > 0 else 0.0
    parts = [
        utc_timestamp(),
        kind,
        f'title="{title}"',
        f"current={current}",
    ]
    if total is not None:
        percent = (current / total * 100.0) if total else 100.0
        parts.extend([f"total={total}", f"percent={percent:.2f}"])
    else:
        parts.append("total=unknown")
    parts.extend([f"elapsed={format_duration(elapsed)}", f"rate={rate:.2f}/s"])
    return " ".join(parts) + "\n"


def write_progress_log(
    kind: str, title: str, current: int, total: int | None, started_at: float
) -> None:
    writer = current_log_writer()
    line = format_progress_line(kind, title, current, total, started_at)
    if writer is not None:
        writer.write(line)
        return
    sys.stdout.write(line)
    sys.stdout.flush()


def should_use_tqdm() -> bool:
    terminal = current_terminal_stdout()
    return bool(getattr(terminal, "isatty", lambda: False)())


def iter_progress(
    title: str,
    iterable: Iterable[T],
    *,
    total: int | None = None,
    log_interval_seconds: float = DEFAULT_LOG_INTERVAL_SECONDS,
) -> Iterator[T]:
    if total is None:
        try:
            total = len(iterable)  # type: ignore[arg-type]
        except TypeError:
            total = None

    print_progress_stage(title)
    started_at = time.monotonic()
    last_log_at = started_at
    current = 0
    write_progress_log("progress_start", title, current, total, started_at)

    progress_bar = None
    if should_use_tqdm():
        try:
            from tqdm import tqdm

            progress_bar = tqdm(
                total=total,
                file=current_terminal_stdout(),
                bar_format="{bar} {n_fmt}/{total_fmt}",
                leave=True,
            )
        except Exception:
            progress_bar = None

    try:
        for item in iterable:
            yield item
            current += 1
            if progress_bar is not None:
                progress_bar.update(1)
            now = time.monotonic()
            if now - last_log_at >= log_interval_seconds:
                write_progress_log("progress", title, current, total, started_at)
                last_log_at = now
    finally:
        if progress_bar is not None:
            progress_bar.close()
        write_progress_log("progress_done", title, current, total, started_at)
