from __future__ import annotations

import unittest
from pathlib import Path

from music_metadata_graph.pipelines.run_full_pipeline import PipelineContext
from music_metadata_graph.pipelines.run_full_pipeline import build_steps


class RunFullPipelineTests(unittest.TestCase):
    def test_step_6_allows_small_album_detail_failure_count(self) -> None:
        ctx = PipelineContext(
            db_path=Path("data/music_metadata_graph.sqlite3"),
            qqmusic_root=Path("data/raw/qqmusic"),
            singer_list_raw_dir=Path("data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all"),
            song_tab_raw_dir=Path("data/raw/qqmusic/singer_homepage_song_tab"),
            album_detail_raw_dir=Path("data/raw/qqmusic/song_album_detail"),
            producer_raw_dir=Path("data/raw/qqmusic/song_producer"),
            continue_from=1,
            stop_after=15,
            dry_run=True,
            mvp=False,
        )

        step_6 = next(step for step in build_steps(ctx) if step.number == 6)
        step_5 = next(step for step in build_steps(ctx) if step.number == 5)

        self.assertIn("--max-failed-fetches", step_6.args)
        self.assertIn("--failure-json", step_6.args)
        self.assertIn("data\\processed\\validation\\album_detail_fetch_failures\\album_detail_fetch_failures.json", step_6.args)
        self.assertNotIn("--max-failed-fetches", step_5.args)

    def test_step_6_uses_mvp_failure_report_path_in_mvp_mode(self) -> None:
        ctx = PipelineContext(
            db_path=Path("data/music_metadata_graph_mvp.sqlite3"),
            qqmusic_root=Path("data/raw/qqmusic"),
            singer_list_raw_dir=Path("data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all"),
            song_tab_raw_dir=Path("data/raw/qqmusic/singer_homepage_song_tab"),
            album_detail_raw_dir=Path("data/raw/qqmusic/song_album_detail"),
            producer_raw_dir=Path("data/raw/qqmusic/song_producer"),
            continue_from=1,
            stop_after=15,
            dry_run=True,
            mvp=True,
        )

        step_6 = next(step for step in build_steps(ctx) if step.number == 6)

        self.assertIn("data\\processed\\validation_mvp\\album_detail_fetch_failures\\album_detail_fetch_failures.json", step_6.args)


if __name__ == "__main__":
    unittest.main()
