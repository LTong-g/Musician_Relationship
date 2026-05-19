from __future__ import annotations
import csv
import tempfile
import unittest
from pathlib import Path
from music_metadata_graph.pipelines.import_singer_song_tab_to_db import (
    build_rejection_row,
    write_rejection_csv,
)
from music_metadata_graph.pipelines.import_song_album_detail_to_db import (
    build_rejection_row as build_album_rejection_row,
)
from music_metadata_graph.pipelines.import_song_album_detail_to_db import (
    write_rejection_csv as write_album_rejection_csv,
)
from music_metadata_graph.pipelines.song_csv import write_song_csv


class RejectionReasonCsvTests(unittest.TestCase):
    def test_song_rejection_csv_appends_reason_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "song_rejections.csv"
            row = build_rejection_row(
                {
                    "song": {
                        "mid": "",
                        "id": 1,
                        "name": "Missing Mid",
                        "title": "Missing Mid",
                        "language": 0,
                        "album": {
                            "mid": "album_mid",
                            "name": "Album",
                            "albumType": "Single",
                            "publishDate": "2026-01-01",
                        },
                        "singer": [{"mid": "", "id": 10, "name": "Singer"}],
                    },
                    "raw_json_path": "raw/page.json",
                    "raw_page": 1,
                    "raw_row_index": 2,
                },
                ["missing_song_mid", "missing_singer_mid"],
                ["1::10:Singer"],
            )

            write_rejection_csv(path, [row])

            with path.open("r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                rows = list(reader)

            self.assertEqual(reader.fieldnames[-1], "reason_code")
            self.assertEqual(rows[0]["reason_code"], "missing_song_mid;missing_singer_mid")

    def test_album_rejection_csv_appends_reason_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "album_rejections.csv"
            row = build_album_rejection_row(
                {
                    "mid": "",
                    "id": 1,
                    "name": "Album",
                    "albumType": "",
                    "publishDate": "",
                    "raw_json_path": "raw/album.json",
                    "raw_page": 0,
                    "raw_row_index": 1,
                },
                ["missing_mid", "missing_albumType", "missing_publishDate"],
            )

            write_album_rejection_csv(path, [row])

            with path.open("r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                rows = list(reader)

            self.assertEqual(reader.fieldnames[-1], "reason_code")
            self.assertEqual(
                rows[0]["reason_code"], "missing_albumType;missing_mid;missing_publishDate"
            )

    def test_regular_song_csv_keeps_base_columns_without_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "kept.csv"

            write_song_csv(
                path,
                [
                    {
                        "song_mid": "song_mid",
                        "song_id": 1,
                        "song_name": "Song",
                        "song_title": "Song",
                        "song_language": 0,
                        "album_name": "Album",
                        "album_type": "Single",
                        "album_publish_date": "2026-01-01",
                        "singer_count": 1,
                        "singers_json": "[]",
                        "reason_code": "should_not_export",
                    }
                ],
                include_credits=False,
            )

            with path.open("r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                rows = list(reader)

            self.assertNotIn("reason_code", reader.fieldnames or [])
            self.assertEqual(rows[0]["song_mid"], "song_mid")


if __name__ == "__main__":
    unittest.main()
