from __future__ import annotations
import csv
import sqlite3
import tempfile
import unittest
from pathlib import Path
from music_metadata_graph.pipelines.filter_imported_songs import FilterConfig, fetch_song_rows, run
from music_metadata_graph.pipelines.filter_imported_songs import step16_dedupe_by_normalized_name


class FilterImportedSongsTests(unittest.TestCase):
    def test_step16_dedupe_uses_current_step_number_in_csv_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "songs.sqlite3"
            rejection_csv = root / "removed.csv"
            temp_kept_csv = root / "kept.csv"
            four_singer_temp_kept_csv = root / "kept_four.csv"
            connection = sqlite3.connect(db_path)
            try:
                connection.row_factory = sqlite3.Row
                connection.execute("PRAGMA foreign_keys = ON")
                connection.executescript("""
                CREATE TABLE artists (
                    mid TEXT PRIMARY KEY,
                    name TEXT NOT NULL
                );
                CREATE TABLE albums (
                    mid TEXT PRIMARY KEY,
                    id INTEGER NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    albumType TEXT NOT NULL,
                    publishDate TEXT NOT NULL
                );
                CREATE TABLE songs (
                    mid TEXT PRIMARY KEY,
                    id INTEGER NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    language INTEGER NOT NULL,
                    album_mid TEXT NOT NULL,
                    raw_json_path TEXT,
                    raw_page INTEGER,
                    raw_row_index INTEGER,
                    FOREIGN KEY(album_mid) REFERENCES albums(mid)
                );
                CREATE TABLE song_singers (
                    song_mid TEXT NOT NULL,
                    singer_order INTEGER NOT NULL,
                    singer_mid TEXT NOT NULL,
                    PRIMARY KEY(song_mid, singer_order),
                    FOREIGN KEY(song_mid) REFERENCES songs(mid) ON DELETE CASCADE,
                    FOREIGN KEY(singer_mid) REFERENCES artists(mid)
                );
                CREATE TABLE song_credit_artists (
                    song_mid TEXT NOT NULL,
                    role TEXT NOT NULL,
                    artist_order INTEGER NOT NULL,
                    artist_mid TEXT NOT NULL,
                    PRIMARY KEY(song_mid, role, artist_order),
                    FOREIGN KEY(song_mid) REFERENCES songs(mid) ON DELETE CASCADE,
                    FOREIGN KEY(artist_mid) REFERENCES artists(mid)
                );
                INSERT INTO artists(mid, name) VALUES
                    ('singer_mid', '周杰伦'),
                    ('lyricist_mid', 'Lyricist'),
                    ('composer_mid', 'Composer');
                INSERT INTO albums(mid, id, name, albumType, publishDate) VALUES
                    ('studio_album', 1, 'Studio Album', '录音室专辑', '2026-01-01'),
                    ('single_album', 2, 'Single Album', 'Single', '2026-01-02');
                INSERT INTO songs(mid, id, name, title, language, album_mid) VALUES
                    ('kept_song', 100, '重复歌名', '重复歌名', 0, 'studio_album'),
                    ('removed_song', 101, '重复歌名', '重复歌名', 0, 'single_album');
                INSERT INTO song_singers(song_mid, singer_order, singer_mid) VALUES
                    ('kept_song', 0, 'singer_mid'),
                    ('removed_song', 0, 'singer_mid');
                INSERT INTO song_credit_artists(song_mid, role, artist_order, artist_mid) VALUES
                    ('kept_song', '作词', 0, 'lyricist_mid'),
                    ('kept_song', '作曲', 0, 'composer_mid'),
                    ('removed_song', '作词', 0, 'lyricist_mid'),
                    ('removed_song', '作曲', 0, 'composer_mid');
                """)
                connection.commit()
                all_rows = fetch_song_rows(connection)
                removed_rows = step16_dedupe_by_normalized_name(connection, all_rows)
                self.assertEqual(removed_rows[0]["filter_step"], "step16_same_credit_name_dedupe")
            finally:
                connection.close()

            summary = run(
                FilterConfig(
                    db_path=db_path,
                    name_dedupe_rejection_csv=rejection_csv,
                    temp_kept_csv=temp_kept_csv,
                    four_singer_temp_kept_csv=four_singer_temp_kept_csv,
                    temp_export_artist_names=("周杰伦",),
                )
            )

            self.assertIn("step16_identity_dedupe", summary)
            self.assertIn("step16_removed_by_name_credit_dedupe", summary)
            self.assertIn("songs_after_step16", summary)
            self.assertNotIn("step15_removed_by_name_credit_dedupe", summary)
            self.assertEqual(summary["step16_removed_by_name_credit_dedupe"], 1)
            self.assertEqual(summary["songs_after_step16"], 1)
            with rejection_csv.open("r", encoding="utf-8-sig", newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual([row["song_mid"] for row in rows], ["removed_song"])
            self.assertEqual(rows[0]["reason_code"], "same_credit_name_dedupe")
            self.assertEqual(summary["exported_temp_kept_rows"], 1)
            self.assertEqual(summary["exported_four_singer_temp_kept_rows"], 1)


if __name__ == "__main__":
    unittest.main()
