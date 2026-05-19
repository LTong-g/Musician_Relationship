from __future__ import annotations
import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from music_metadata_graph.progress import iter_progress
from music_metadata_graph.run_log import capture_run_log


class ProgressTests(unittest.TestCase):
    def test_iter_progress_writes_start_timed_and_done_lines(self) -> None:
        stdout = io.StringIO()
        ticks = iter([0.0, 0.0, 0.5, 121.0, 122.0, 123.0, 124.0])
        with patch("music_metadata_graph.progress.time.monotonic", side_effect=lambda: next(ticks)):
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(
                    list(iter_progress("测试进度", [1, 2], log_interval_seconds=120.0)), [1, 2]
                )

        output = stdout.getvalue()
        self.assertIn("== 测试进度 ==", output)
        self.assertIn('progress_start title="测试进度" current=0 total=2', output)
        self.assertIn('progress title="测试进度" current=2 total=2', output)
        self.assertIn('progress_done title="测试进度" current=2 total=2', output)

    def test_iter_progress_keeps_tqdm_output_out_of_run_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log_dir = Path(tmp)
            with capture_run_log("progress_test", log_dir=log_dir) as log_path:
                with patch("music_metadata_graph.progress.should_use_tqdm", return_value=True):
                    with patch(
                        "music_metadata_graph.progress.current_terminal_stdout",
                        return_value=io.StringIO(),
                    ):
                        self.assertEqual(
                            list(iter_progress("日志分流", [1, 2], log_interval_seconds=0.0)),
                            [1, 2],
                        )

            text = log_path.read_text(encoding="utf-8")

        self.assertIn("== 日志分流 ==", text)
        self.assertIn('progress_start title="日志分流"', text)
        self.assertIn('progress_done title="日志分流"', text)
        self.assertNotIn("\r", text)

    def test_tqdm_bar_includes_current_and_total_counts(self) -> None:
        class FakeTqdm:
            calls: list[dict[str, object]] = []

            def __init__(self, **kwargs: object) -> None:
                self.calls.append(kwargs)

            def update(self, value: int) -> None:
                pass

            def close(self) -> None:
                pass

        with patch("music_metadata_graph.progress.should_use_tqdm", return_value=True):
            with patch(
                "music_metadata_graph.progress.current_terminal_stdout", return_value=io.StringIO()
            ):
                with patch.dict(
                    "sys.modules", {"tqdm": type("FakeTqdmModule", (), {"tqdm": FakeTqdm})}
                ):
                    self.assertEqual(list(iter_progress("带计数进度条", [1, 2])), [1, 2])

        self.assertEqual(FakeTqdm.calls[-1]["bar_format"], "{bar} {n_fmt}/{total_fmt}")


if __name__ == "__main__":
    unittest.main()
