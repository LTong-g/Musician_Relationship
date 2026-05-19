from __future__ import annotations
import contextlib
import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from music_metadata_graph.pipelines.fill_song_credit_missing_mids import FillConfig
from music_metadata_graph.pipelines.fill_song_credit_missing_mids import (
    collect_missing_credit_sources,
)
from music_metadata_graph.pipelines.collect_song_lyric_credit_raw import build_lyric_credit_evidence


class FillSongCreditMissingMidsTests(unittest.TestCase):
    def test_collect_missing_credit_sources_prints_scan_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw_root = root / "qqmusic"
            producer_dir = raw_root / "song_producer"
            lyric_dir = raw_root / "song_lyric_credit"
            producer_dir.mkdir(parents=True)
            lyric_dir.mkdir(parents=True)

            db_path = root / "music.sqlite3"
            connection = sqlite3.connect(db_path)
            try:
                connection.row_factory = sqlite3.Row
                connection.execute(
                    "CREATE TABLE songs (mid TEXT PRIMARY KEY, id INTEGER, name TEXT)"
                )
                connection.execute(
                    "INSERT INTO songs (mid, id, name) VALUES ('song_a', 1, 'Song A')"
                )

                (producer_dir / "song_a.json").write_text(
                    json.dumps(
                        {
                            "Lst": [
                                {
                                    "Title": "作词",
                                    "Producers": [{"Name": "No Mid Lyricist", "SingerMid": ""}],
                                }
                            ]
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                (producer_dir / "song_b.json").write_text(
                    json.dumps({"Lst": []}, ensure_ascii=False),
                    encoding="utf-8",
                )
                (lyric_dir / "song_a.json").write_text(
                    json.dumps(
                        build_lyric_credit_evidence(
                            {
                                "crypt": 0,
                                "lyric": "作词: Lyricist From Producer\n作曲: Composer From Lyric\n",
                            },
                            target={
                                "song_mid": "song_a",
                                "song_id": "1",
                                "song_name": "Song A",
                                "missing_roles": ["作曲"],
                            },
                            raw_path=lyric_dir / "song_a.json",
                        ),
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )

                stdout = io.StringIO()
                config = FillConfig(
                    raw_dir=raw_root,
                    db_path=db_path,
                    csv_path=root / "song_credit_mid_fill.csv",
                    force=False,
                    max_names=None,
                    artist_mid=None,
                    artist_name=None,
                )
                with patch(
                    "music_metadata_graph.pipelines.fill_song_credit_missing_mids.SCAN_PROGRESS_EVERY",
                    1,
                ):
                    with contextlib.redirect_stdout(stdout):
                        sources = collect_missing_credit_sources(connection, config)
            finally:
                connection.close()

            output = stdout.getvalue()
            self.assertIn("scan_credit_sources producer_raw_files=2 target_songs=1", output)
            self.assertIn("扫描作词作曲来源 raw", output)
            self.assertIn('progress_start title="扫描作词作曲来源 raw" current=0 total=2', output)
            self.assertIn('progress_done title="扫描作词作曲来源 raw" current=2 total=2', output)
            self.assertIn("scan_credit_sources_summary", output)
            self.assertIn("skipped_non_target=1", output)
            self.assertIn("sources=2", output)
            self.assertIn("lyric_source_rows=1", output)
            self.assertEqual(
                [source.source_step for source in sources],
                ["step11_song_credit", "step12_song_lyric_credit"],
            )


if __name__ == "__main__":
    unittest.main()
