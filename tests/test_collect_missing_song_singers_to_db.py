from __future__ import annotations
import sqlite3
import tempfile
import unittest
from pathlib import Path
from music_metadata_graph.pipelines.collect_missing_song_singers_to_db import extract_singer_row
from music_metadata_graph.pipelines.import_singer_list_to_db import create_schema
from music_metadata_graph.pipelines.import_singer_list_to_db import import_artists


class CollectMissingSongSingersToDbTests(unittest.TestCase):
    def test_extract_singer_row_includes_fans_from_get_info(self) -> None:
        row, reason = extract_singer_row(
            "mid_a",
            {
                "Info": {
                    "Singer": {
                        "SingerMid": "mid_a",
                        "Name": "Artist A",
                        "SingerPic": "https://example.test/a.jpg",
                    },
                    "FansNum": {"Num": 12345},
                }
            },
            Path("data/raw/qqmusic/singer_info/mid_a.json"),
        )

        self.assertEqual(reason, "ok")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row["fans_num"], 12345)
        self.assertEqual(row["fans_source"], "qqmusic.singer.get_info.FansNum.Num")
        self.assertEqual(row["fans_raw_json_path"], "data/raw/qqmusic/singer_info/mid_a.json")

    def test_missing_fans_does_not_overwrite_existing_fans(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.sqlite3"
            connection = sqlite3.connect(db_path)
            try:
                create_schema(connection)
                import_artists(
                    connection,
                    [
                        {
                            "mid": "mid_a",
                            "name": "Artist A",
                            "fans_num": 999,
                            "fans_source": "existing",
                            "fans_raw_json_path": "existing.json",
                        }
                    ],
                )

                row, reason = extract_singer_row(
                    "mid_a",
                    {
                        "Info": {
                            "Singer": {"SingerMid": "mid_a", "Name": "Artist A"},
                            "FansNum": {"Num": 0},
                        }
                    },
                    Path("data/raw/qqmusic/singer_info/mid_a.json"),
                )
                self.assertEqual(reason, "ok")
                self.assertIsNotNone(row)
                assert row is not None
                import_artists(connection, [row])

                stored = connection.execute(
                    "SELECT fans_num, fans_source, fans_raw_json_path FROM artists WHERE mid = 'mid_a'"
                ).fetchone()
            finally:
                connection.close()

        self.assertEqual(stored, (999, "existing", "existing.json"))


if __name__ == "__main__":
    unittest.main()
