from __future__ import annotations
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from music_metadata_graph.pipelines.collect_singer_song_tab_raw import (
    CollectConfig as SongTabCollectConfig,
)
from music_metadata_graph.pipelines.collect_singer_song_tab_raw import resolve_targets
from music_metadata_graph.pipelines.import_singer_list_to_db import ImportConfig
from music_metadata_graph.pipelines.import_singer_list_to_db import run


class ImportSingerListToDbTests(unittest.TestCase):
    def test_imports_fans_num_from_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_dir = root / "singer_list"
            raw_dir.mkdir(parents=True)
            (raw_dir / "page_0001_size_80.json").write_text(
                json.dumps(
                    {
                        "singerlist": [
                            {
                                "mid": "mid_a",
                                "name": "Artist A",
                                "area_id": 0,
                                "other_name": "A",
                                "spell": "artista",
                                "singer_pic": "https://example.test/a.jpg",
                            },
                            {
                                "mid": "mid_missing_fans",
                                "name": "Artist Missing Fans",
                                "area_id": 1,
                            },
                            {
                                "mid": "mid_b",
                                "name": "Artist B",
                                "area_id": 2,
                            },
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            fans_dir = root / "fans"
            fans_dir.mkdir(parents=True)
            (fans_dir / "singer_fans_summary.json").write_text(
                json.dumps(
                    {
                        "rows": [
                            {
                                "mid": "mid_a",
                                "fans_num": 12345,
                                "source": "qqmusic.singer.get_singer_list.concernNum",
                                "raw_json_path": "data/raw/qqmusic/singer_fans_list/area_china.json",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            db_path = root / "test.sqlite3"
            result = run(ImportConfig(raw_dir=raw_dir, fans_raw_dir=fans_dir, db_path=db_path))
            self.assertEqual(result["filtered_rows"], 1)
            self.assertEqual(result["filtered_rows_by_area"], 2)
            self.assertEqual(result["filtered_out_missing_fans"], 1)
            self.assertEqual(result["filtered_rows_with_fans"], 1)
            connection = sqlite3.connect(db_path)
            try:
                fans_num_column = {
                    row[1]: row
                    for row in connection.execute("PRAGMA table_info(artists)").fetchall()
                }["fans_num"]
                self.assertEqual(fans_num_column[3], 0)
                row = connection.execute(
                    "SELECT mid, fans_num, fans_source, fans_raw_json_path FROM artists WHERE mid = 'mid_a'"
                ).fetchone()
                missing_fans_row = connection.execute(
                    "SELECT mid FROM artists WHERE mid = 'mid_missing_fans'"
                ).fetchone()
            finally:
                connection.close()
            self.assertEqual(
                row,
                (
                    "mid_a",
                    12345,
                    "qqmusic.singer.get_singer_list.concernNum",
                    "data/raw/qqmusic/singer_fans_list/area_china.json",
                ),
            )
            self.assertIsNone(missing_fans_row)

    def test_mvp_import_reads_mvp_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_dir = root / "singer_list"
            raw_dir.mkdir(parents=True)
            (raw_dir / "page_0001_size_80.json").write_text(
                json.dumps(
                    {
                        "singerlist": [
                            {"mid": "mid_a", "name": "Artist A", "area_id": 0},
                            {"mid": "mid_b", "name": "Artist B", "area_id": 1},
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            fans_dir = root / "fans"
            fans_dir.mkdir(parents=True)
            (fans_dir / "singer_fans_summary.json").write_text(
                json.dumps({"rows": [{"mid": "mid_b", "fans_num": 200}]}, ensure_ascii=False),
                encoding="utf-8",
            )
            (fans_dir / "singer_fans_summary_mvp.json").write_text(
                json.dumps({"rows": [{"mid": "mid_a", "fans_num": 100}]}, ensure_ascii=False),
                encoding="utf-8",
            )
            db_path = root / "test.sqlite3"

            result = run(
                ImportConfig(raw_dir=raw_dir, fans_raw_dir=fans_dir, db_path=db_path, mvp=True)
            )

            self.assertEqual(result["fans_rows_available"], 1)
            self.assertEqual(result["filtered_rows"], 1)
            connection = sqlite3.connect(db_path)
            try:
                rows = connection.execute(
                    "SELECT mid, fans_num FROM artists ORDER BY mid"
                ).fetchall()
            finally:
                connection.close()
            self.assertEqual(rows, [("mid_a", 100)])

    def test_song_tab_all_targets_reuse_fans_filter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_dir = root / "singer_list"
            raw_dir.mkdir(parents=True)
            (raw_dir / "page_0001_size_80.json").write_text(
                json.dumps(
                    {
                        "singerlist": [
                            {"mid": "mid_a", "name": "Artist A", "area_id": 0},
                            {
                                "mid": "mid_missing_fans",
                                "name": "Artist Missing Fans",
                                "area_id": 1,
                            },
                            {"mid": "mid_b", "name": "Artist B", "area_id": 2},
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            qqmusic_root = root / "qqmusic"
            qqmusic_root.mkdir(parents=True)
            (qqmusic_root / "singer_fans_summary.json").write_text(
                json.dumps(
                    {
                        "rows": [
                            {"mid": "mid_a", "fans_num": 12345},
                            {"mid": "mid_missing_fans", "fans_num": None},
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            db_path = root / "test.sqlite3"
            run(ImportConfig(raw_dir=raw_dir, fans_raw_dir=qqmusic_root, db_path=db_path))
            targets = resolve_targets(
                SongTabCollectConfig(
                    raw_dir=qqmusic_root,
                    db_path=db_path,
                    page_size=30,
                    singer_list_raw_dir=raw_dir,
                    max_pages_per_singer=None,
                    force=False,
                    all_singers=True,
                    mvp=False,
                    mids=(),
                    names=(),
                )
            )
            self.assertEqual(
                [(target.mid, target.name) for target in targets], [("mid_a", "Artist A")]
            )

    def test_song_tab_mvp_targets_reuse_mvp_fans_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_dir = root / "singer_list"
            raw_dir.mkdir(parents=True)
            (raw_dir / "page_0001_size_80.json").write_text(
                json.dumps(
                    {
                        "singerlist": [
                            {"mid": "mid_a", "name": "Artist A", "area_id": 0},
                            {"mid": "mid_b", "name": "Artist B", "area_id": 1},
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            qqmusic_root = root / "qqmusic"
            qqmusic_root.mkdir(parents=True)
            (qqmusic_root / "singer_fans_summary.json").write_text(
                json.dumps({"rows": [{"mid": "mid_b", "fans_num": 200}]}, ensure_ascii=False),
                encoding="utf-8",
            )
            (qqmusic_root / "singer_fans_summary_mvp.json").write_text(
                json.dumps({"rows": [{"mid": "mid_a", "fans_num": 100}]}, ensure_ascii=False),
                encoding="utf-8",
            )
            db_path = root / "test.sqlite3"
            run(ImportConfig(raw_dir=raw_dir, fans_raw_dir=qqmusic_root, db_path=db_path, mvp=True))

            targets = resolve_targets(
                SongTabCollectConfig(
                    raw_dir=qqmusic_root,
                    db_path=db_path,
                    page_size=30,
                    singer_list_raw_dir=raw_dir,
                    max_pages_per_singer=None,
                    force=False,
                    all_singers=True,
                    mvp=True,
                    mids=(),
                    names=(),
                )
            )

            self.assertEqual(
                [(target.mid, target.name) for target in targets], [("mid_a", "Artist A")]
            )


if __name__ == "__main__":
    unittest.main()
