from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from music_metadata_graph.pipelines.collect_song_album_detail_raw import FetchFailure
from music_metadata_graph.pipelines.collect_song_album_detail_raw import validate_fetch_failure_limit
from music_metadata_graph.pipelines.collect_song_album_detail_raw import write_failure_report


class CollectSongAlbumDetailRawTests(unittest.TestCase):
    def test_failure_limit_allows_failures_within_threshold(self) -> None:
        failures = [
            FetchFailure(
                key="002o6oXX3GgGCM",
                path=Path("data/raw/qqmusic/song_album_detail/002o6oXX3GgGCM.json"),
                reason="CgiApiException: CGI request error",
            )
        ]

        validate_fetch_failure_limit(failures, max_failed_fetches=1)

    def test_failure_limit_rejects_failures_above_threshold(self) -> None:
        failures = [
            FetchFailure(
                key="002o6oXX3GgGCM",
                path=Path("data/raw/qqmusic/song_album_detail/002o6oXX3GgGCM.json"),
                reason="CgiApiException: CGI request error",
            )
        ]

        with self.assertRaisesRegex(RuntimeError, "002o6oXX3GgGCM"):
            validate_fetch_failure_limit(failures, max_failed_fetches=0)

    def test_write_failure_report_keeps_key_path_and_reason(self) -> None:
        failures = [
            FetchFailure(
                key="002o6oXX3GgGCM",
                path=Path("data/raw/qqmusic/song_album_detail/002o6oXX3GgGCM.json"),
                reason="CgiApiException: CGI request error",
            )
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            report_path = Path(tmp_dir) / "nested" / "failures.json"
            write_failure_report(report_path, failures)
            payload = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["failed_fetches"], 1)
        self.assertEqual(payload["failed_album_keys"], ["002o6oXX3GgGCM"])
        self.assertEqual(payload["failures"][0]["album_key"], "002o6oXX3GgGCM")
        self.assertEqual(
            payload["failures"][0]["raw_json_path"],
            "data/raw/qqmusic/song_album_detail/002o6oXX3GgGCM.json",
        )
        self.assertIn("CgiApiException", payload["failures"][0]["reason"])


if __name__ == "__main__":
    unittest.main()
