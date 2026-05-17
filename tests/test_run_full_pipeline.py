from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from music_metadata_graph.pipelines.run_full_pipeline import PipelineContext
from music_metadata_graph.pipelines.run_full_pipeline import build_steps
from music_metadata_graph.pipelines.run_full_pipeline import check_singer_fans_raw


class RunFullPipelineTests(unittest.TestCase):
    def test_mvp_fans_check_reads_mvp_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "singer_fans_summary.json").write_text(
                json.dumps({"rows": []}, ensure_ascii=False),
                encoding="utf-8",
            )
            (root / "singer_fans_summary_mvp.json").write_text(
                json.dumps({"rows": [{"mid": "mid_a", "fans_num": 100}]}, ensure_ascii=False),
                encoding="utf-8",
            )
            ctx = PipelineContext(
                db_path=Path("data/music_metadata_graph_mvp.sqlite3"),
                qqmusic_root=root,
                singer_list_raw_dir=Path("data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all"),
                fans_raw_dir=root,
                song_tab_raw_dir=root / "singer_homepage_song_tab",
                album_detail_raw_dir=root / "song_album_detail",
                producer_raw_dir=root / "song_producer",
                continue_from=1,
                stop_after=19,
                dry_run=True,
                mvp=True,
                site_dir=Path("site_mvp"),
                large_site_dir=Path("site_large"),
                avatar_cache_dir=Path("site_assets"),
                skip_avatar_download=False,
                max_avatar_downloads=None,
            )

            result = check_singer_fans_raw(ctx)

            self.assertEqual(result["summary_json"], (root / "singer_fans_summary_mvp.json").as_posix())
            self.assertEqual(result["singer_fans_rows"], 1)

    def test_step_7_allows_small_album_detail_failure_count(self) -> None:
        ctx = PipelineContext(
            db_path=Path("data/music_metadata_graph.sqlite3"),
            qqmusic_root=Path("data/raw/qqmusic"),
            singer_list_raw_dir=Path("data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all"),
            fans_raw_dir=Path("data/raw/qqmusic"),
            song_tab_raw_dir=Path("data/raw/qqmusic/singer_homepage_song_tab"),
            album_detail_raw_dir=Path("data/raw/qqmusic/song_album_detail"),
            producer_raw_dir=Path("data/raw/qqmusic/song_producer"),
            continue_from=1,
            stop_after=15,
            dry_run=True,
            mvp=False,
            site_dir=Path("site"),
            large_site_dir=Path("site_large"),
            avatar_cache_dir=Path("site_assets"),
            skip_avatar_download=False,
            max_avatar_downloads=None,
        )

        step_7 = next(step for step in build_steps(ctx) if step.number == 7)
        step_6 = next(step for step in build_steps(ctx) if step.number == 6)

        self.assertIn("--max-failed-fetches", step_7.args)
        self.assertIn("--failure-json", step_7.args)
        self.assertIn("data\\processed\\validation\\album_detail_fetch_failures\\album_detail_fetch_failures.json", step_7.args)
        self.assertNotIn("--max-failed-fetches", step_6.args)

    def test_step_7_uses_mvp_failure_report_path_in_mvp_mode(self) -> None:
        ctx = PipelineContext(
            db_path=Path("data/music_metadata_graph_mvp.sqlite3"),
            qqmusic_root=Path("data/raw/qqmusic"),
            singer_list_raw_dir=Path("data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all"),
            fans_raw_dir=Path("data/raw/qqmusic"),
            song_tab_raw_dir=Path("data/raw/qqmusic/singer_homepage_song_tab"),
            album_detail_raw_dir=Path("data/raw/qqmusic/song_album_detail"),
            producer_raw_dir=Path("data/raw/qqmusic/song_producer"),
            continue_from=1,
            stop_after=15,
            dry_run=True,
            mvp=True,
            site_dir=Path("site_mvp"),
            large_site_dir=Path("site_large"),
            avatar_cache_dir=Path("site_assets"),
            skip_avatar_download=False,
            max_avatar_downloads=None,
        )

        step_7 = next(step for step in build_steps(ctx) if step.number == 7)

        self.assertIn("data\\processed\\validation_mvp\\album_detail_fetch_failures\\album_detail_fetch_failures.json", step_7.args)

    def test_static_site_steps_are_part_of_full_pipeline(self) -> None:
        ctx = PipelineContext(
            db_path=Path("data/music_metadata_graph_mvp.sqlite3"),
            qqmusic_root=Path("data/raw/qqmusic"),
            singer_list_raw_dir=Path("data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all"),
            fans_raw_dir=Path("data/raw/qqmusic"),
            song_tab_raw_dir=Path("data/raw/qqmusic/singer_homepage_song_tab"),
            album_detail_raw_dir=Path("data/raw/qqmusic/song_album_detail"),
            producer_raw_dir=Path("data/raw/qqmusic/song_producer"),
            continue_from=1,
            stop_after=19,
            dry_run=True,
            mvp=True,
            site_dir=Path("site_mvp"),
            large_site_dir=Path("site_large"),
            avatar_cache_dir=Path("site_assets"),
            skip_avatar_download=True,
            max_avatar_downloads=5,
        )

        steps = build_steps(ctx)
        step_2 = next(step for step in steps if step.number == 2)
        step_3 = next(step for step in steps if step.number == 3)
        step_17 = next(step for step in steps if step.number == 17)
        step_18 = next(step for step in steps if step.number == 18)
        step_19 = next(step for step in steps if step.number == 19)

        self.assertEqual(step_2.module, "music_metadata_graph.pipelines.collect_singer_fans_raw")
        self.assertEqual(step_3.module, "music_metadata_graph.pipelines.import_singer_list_to_db")
        self.assertIn("--fans-raw-dir", step_3.args)
        self.assertEqual(step_17.module, "music_metadata_graph.pipelines.prepare_static_graph_assets")
        self.assertIn("site_mvp", step_17.args)
        self.assertIn("--avatar-cache-dir", step_17.args)
        self.assertIn("site_assets", step_17.args)
        self.assertIn("--skip-avatar-download", step_17.args)
        self.assertIn("--max-avatar-downloads", step_17.args)
        self.assertIn("5", step_17.args)
        self.assertEqual(step_18.module, "music_metadata_graph.pipelines.build_static_graph")
        self.assertIn("site_mvp", step_18.args)
        self.assertEqual(step_19.module, "music_metadata_graph.pipelines.build_large_graph_static")
        self.assertIn("data\\music_metadata_graph.sqlite3", step_19.args)
        self.assertIn("site_large", step_19.args)


if __name__ == "__main__":
    unittest.main()
