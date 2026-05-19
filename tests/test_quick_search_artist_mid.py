from __future__ import annotations
import contextlib
import io
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from music_metadata_graph.pipelines.quick_search_artist_mid import MissingArtistName
from music_metadata_graph.pipelines.quick_search_artist_mid import fill_missing_artist_mids


class QuickSearchArtistMidTests(unittest.IsolatedAsyncioTestCase):
    async def test_search_phase_uses_search_job_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raw_dir = Path(tmp) / "raw"
            csv_path = Path(tmp) / "fill.csv"
            connection = sqlite3.connect(":memory:")
            connection.row_factory = sqlite3.Row
            connection.execute("""
                CREATE TABLE artists (
                    mid TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    area_id INTEGER,
                    fans_num INTEGER,
                    fans_source TEXT NOT NULL DEFAULT '',
                    fans_raw_json_path TEXT NOT NULL DEFAULT '',
                    other_name TEXT NOT NULL DEFAULT '',
                    icon TEXT NOT NULL DEFAULT '',
                    spell TEXT NOT NULL DEFAULT '',
                    raw_json_path TEXT NOT NULL DEFAULT '',
                    raw_page INTEGER NOT NULL DEFAULT 0,
                    raw_row_index INTEGER NOT NULL DEFAULT 0
                )
                """)
            connection.execute(
                "INSERT INTO artists (mid, name, raw_json_path) VALUES ('db_mid', 'Db Artist', 'db.json')"
            )
            sources = [
                missing_source("Db Artist"),
                missing_source("Search A"),
                missing_source("Search B"),
            ]

            async def fake_execute_or_load(client, raw_dir, artist_name, *, force):
                path = raw_dir / f"{artist_name}.json"
                payload = {
                    "singer": {
                        "itemlist": [{"name": artist_name, "mid": f"mid_{artist_name}", "pic": ""}]
                    }
                }
                return payload, "fetched", path

            stdout = io.StringIO()
            with patch(
                "music_metadata_graph.pipelines.quick_search_artist_mid.execute_or_load_quick_search",
                side_effect=fake_execute_or_load,
            ):
                with contextlib.redirect_stdout(stdout):
                    result = await fill_missing_artist_mids(
                        connection,
                        sources,
                        raw_dir=raw_dir,
                        csv_path=csv_path,
                        force=False,
                    )

        output = stdout.getvalue()
        self.assertIn("== 解析缺失音乐人姓名并检查本地 artists ==", output)
        self.assertIn("== 请求或读取 quick_search raw 并写入匹配结果 ==", output)
        self.assertIn("[1/2] name=Search", output)
        self.assertIn("[2/2] name=Search", output)
        self.assertNotIn("[2/3] name=Search", output)
        self.assertEqual(result["unique_names"], 3)
        self.assertEqual(result["fetched"], 2)


def missing_source(name: str) -> MissingArtistName:
    return MissingArtistName(
        source_step="test",
        source_role="作词",
        source_name=name,
        source_song_mid="song_mid",
        source_song_id="1",
        source_song_name="song",
        source_raw_json_path="raw.json",
        source_raw_page=0,
        source_raw_row_index=1,
    )


if __name__ == "__main__":
    unittest.main()
