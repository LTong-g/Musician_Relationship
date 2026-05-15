from __future__ import annotations

import atexit
import faulthandler
import queue
import sys
import threading
import traceback
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TextIO, TypeVar


DEFAULT_RUN_LOG_DIR = Path("logs/runs")
_T = TypeVar("_T")
_ACTIVE_LOG_WRITERS: list["AsyncLogWriter"] = []
_ACTIVE_RUN_CONTEXT: "RunLogContext | None" = None
_WINDOWS_CONSOLE_HANDLER: Any | None = None
_WINDOWS_CONSOLE_HANDLER_INSTALLED = False
_EXIT_FLUSH_INSTALLED = False
_LOG_SENTINEL = object()


@dataclass(frozen=True)
class RunLogIdentity:
    run_id: str
    log_path: Path


@dataclass
class RunLogContext:
    identity: RunLogIdentity
    writer: "AsyncLogWriter"


class TeeTextIO:
    def __init__(self, terminal: TextIO, log_writer: "AsyncLogWriter") -> None:
        self._terminal = terminal
        self._log_writer = log_writer

    @property
    def encoding(self) -> str | None:
        return self._terminal.encoding

    @property
    def errors(self) -> str | None:
        return self._terminal.errors

    def write(self, text: str) -> int:
        self._terminal.write(text)
        self._log_writer.write(text)
        self._terminal.flush()
        return len(text)

    def flush(self) -> None:
        self._terminal.flush()
        self._log_writer.flush()

    def isatty(self) -> bool:
        return self._terminal.isatty()

    def __getattr__(self, name: str) -> object:
        return getattr(self._terminal, name)


class AsyncLogWriter:
    def __init__(self, log_file: TextIO) -> None:
        self._log_file = log_file
        self._queue: queue.Queue[str | object] = queue.Queue()
        self._lock = threading.Lock()
        self._closed = False
        self._thread = threading.Thread(target=self._write_worker, name="run-log-writer", daemon=True)
        self._thread.start()

    def write(self, text: str) -> None:
        if self._closed:
            return
        self._queue.put(text)

    def flush(self) -> None:
        self._queue.join()
        with self._lock:
            self._log_file.flush()

    def write_immediate(self, text: str) -> None:
        if self._closed:
            return
        with self._lock:
            self._log_file.write(text)
            self._log_file.flush()

    def close(self) -> None:
        if self._closed:
            return
        self.flush()
        self._closed = True
        self._queue.put(_LOG_SENTINEL)
        self._queue.join()
        self._thread.join(timeout=5)
        with self._lock:
            self._log_file.flush()

    def _write_worker(self) -> None:
        while True:
            item = self._queue.get()
            try:
                if item is _LOG_SENTINEL:
                    return
                with self._lock:
                    self._log_file.write(str(item))
                    self._log_file.flush()
            finally:
                self._queue.task_done()


def safe_log_stem(script_name: str) -> str:
    invalid_chars = '<>:"/\\|?*'
    cleaned = "".join("_" if char in invalid_chars or ord(char) < 32 else char for char in script_name)
    cleaned = cleaned.strip().rstrip(". ")
    return cleaned or "script"


def build_run_log_identity(script_name: str, log_dir: Path = DEFAULT_RUN_LOG_DIR) -> RunLogIdentity:
    start_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = safe_log_stem(script_name)
    base_run_id = f"{stem}_{start_timestamp}"
    path = log_dir / f"{base_run_id}.log"
    if not path.exists():
        return RunLogIdentity(run_id=base_run_id, log_path=path)
    for suffix in range(2, 100):
        run_id = f"{base_run_id}_{suffix:02d}"
        candidate = log_dir / f"{run_id}.log"
        if not candidate.exists():
            return RunLogIdentity(run_id=run_id, log_path=candidate)
    raise RuntimeError(f"Could not allocate run log path for {base_run_id}")


def current_run_log_path() -> Path | None:
    return _ACTIVE_RUN_CONTEXT.identity.log_path if _ACTIVE_RUN_CONTEXT is not None else None


def current_run_id() -> str | None:
    return _ACTIVE_RUN_CONTEXT.identity.run_id if _ACTIVE_RUN_CONTEXT is not None else None


def utc_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def flush_active_logs() -> None:
    for log_writer in tuple(_ACTIVE_LOG_WRITERS):
        try:
            log_writer.flush()
        except Exception:
            pass


def install_exit_flush() -> None:
    global _EXIT_FLUSH_INSTALLED
    if _EXIT_FLUSH_INSTALLED:
        return
    atexit.register(flush_active_logs)
    _EXIT_FLUSH_INSTALLED = True


def install_windows_console_flush() -> None:
    global _WINDOWS_CONSOLE_HANDLER, _WINDOWS_CONSOLE_HANDLER_INSTALLED
    if _WINDOWS_CONSOLE_HANDLER_INSTALLED or sys.platform != "win32":
        return
    try:
        import ctypes
    except Exception:
        return

    handler_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_uint)

    def handler(control_type: int) -> bool:
        for log_writer in tuple(_ACTIVE_LOG_WRITERS):
            try:
                log_writer.write_immediate(f"\nrun_console_event={control_type} at={utc_timestamp()}\n")
                log_writer.flush()
            except Exception:
                pass
        return False

    callback = handler_type(handler)
    if ctypes.windll.kernel32.SetConsoleCtrlHandler(callback, True):
        _WINDOWS_CONSOLE_HANDLER = callback
        _WINDOWS_CONSOLE_HANDLER_INSTALLED = True


@contextmanager
def capture_run_log(script_name: str, log_dir: Path = DEFAULT_RUN_LOG_DIR):
    global _ACTIVE_RUN_CONTEXT
    log_dir.mkdir(parents=True, exist_ok=True)
    identity = build_run_log_identity(script_name, log_dir)
    path = identity.log_path
    with path.open("w", buffering=1, encoding="utf-8", newline="") as log_file:
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        faulthandler_was_enabled = faulthandler.is_enabled()
        log_writer = AsyncLogWriter(log_file)
        previous_context = _ACTIVE_RUN_CONTEXT
        _ACTIVE_RUN_CONTEXT = RunLogContext(identity=identity, writer=log_writer)
        _ACTIVE_LOG_WRITERS.append(log_writer)
        install_exit_flush()
        install_windows_console_flush()
        faulthandler.enable(file=log_file, all_threads=True)
        sys.stdout = TeeTextIO(original_stdout, log_writer)  # type: ignore[assignment]
        sys.stderr = TeeTextIO(original_stderr, log_writer)  # type: ignore[assignment]
        try:
            print(f"run_id={identity.run_id}")
            print(f"run_log={identity.log_path.as_posix()}")
            print(f"run_started_at={utc_timestamp()}")
            yield path
        finally:
            print(f"run_log_closing_at={utc_timestamp()}")
            sys.stdout.flush()
            sys.stderr.flush()
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            faulthandler.disable()
            if faulthandler_was_enabled:
                faulthandler.enable(file=original_stderr, all_threads=True)
            if log_writer in _ACTIVE_LOG_WRITERS:
                _ACTIVE_LOG_WRITERS.remove(log_writer)
            _ACTIVE_RUN_CONTEXT = previous_context
            log_writer.close()


def run_with_log(script_name: str, func: Callable[[], _T], log_dir: Path = DEFAULT_RUN_LOG_DIR) -> _T:
    if _ACTIVE_RUN_CONTEXT is not None:
        print(
            f"run_log_reused={_ACTIVE_RUN_CONTEXT.identity.log_path.as_posix()} "
            f"run_id={_ACTIVE_RUN_CONTEXT.identity.run_id} nested_script={safe_log_stem(script_name)}"
        )
        return func()
    with capture_run_log(script_name, log_dir):
        try:
            result = func()
            print(f"run_status=completed at={utc_timestamp()}")
            return result
        except SystemExit as exc:
            print(f"run_status=system_exit code={exc.code} at={utc_timestamp()}")
            raise
        except KeyboardInterrupt:
            print(f"run_status=keyboard_interrupt at={utc_timestamp()}")
            raise SystemExit(130) from None
        except BaseException:
            traceback.print_exc()
            print(f"run_status=failed at={utc_timestamp()}")
            raise SystemExit(1) from None
