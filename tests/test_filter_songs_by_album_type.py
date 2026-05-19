from __future__ import annotations
import csv
import sqlite3
import tempfile
import unittest
from pathlib import Path
from music_metadata_graph.pipelines.filter_songs_by_album_type import FilterConfig, run


class FilterSongsByAlbumTypeTests(unittest.TestCase):
    def test_keeps_disallowed_album_type_when_song_name_is_unique(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "songs.sqlite3"
            csv_path = root / "removed.csv"
            connection = sqlite3.connect(db_path)
            self.addCleanup(connection.close)
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
                INSERT INTO artists(mid, name) VALUES ('artist_mid', 'Artist');
                INSERT INTO albums(mid, id, name, albumType, publishDate) VALUES
                    ('studio_album', 1, 'Studio Album', '录音室专辑', '2026-01-01'),
                    ('concert_album', 2, 'Concert Album', '演唱会', '2026-01-02'),
                    ('soundtrack_album', 3, 'Soundtrack Album', '原声带', '2026-01-03');
                INSERT INTO songs(mid, id, name, title, language, album_mid) VALUES
                    ('allowed_song', 100, '重复歌名', '重复歌名', 0, 'studio_album'),
                    ('duplicate_disallowed_song', 101, '重复歌名', '重复歌名 Live', 0, 'concert_album'),
                    ('unique_disallowed_song', 102, '孤立歌名', '孤立歌名', 0, 'soundtrack_album');
                INSERT INTO song_singers(song_mid, singer_order, singer_mid) VALUES
                    ('allowed_song', 0, 'artist_mid'),
                    ('duplicate_disallowed_song', 0, 'artist_mid'),
                    ('unique_disallowed_song', 0, 'artist_mid');
                """)
            connection.commit()
            connection.close()

            summary = run(FilterConfig(db_path=db_path, rejection_csv=csv_path))

            self.assertEqual(summary["songs_before"], 3)
            self.assertEqual(summary["removed_by_album_type"], 1)
            self.assertEqual(summary["songs_after"], 2)
            check = sqlite3.connect(db_path)
            try:
                remaining_mids = {row[0] for row in check.execute("SELECT mid FROM songs")}
            finally:
                check.close()
            self.assertEqual(remaining_mids, {"allowed_song", "unique_disallowed_song"})
            with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                rows = list(reader)
            self.assertEqual(reader.fieldnames[-1], "reason_code")
            self.assertEqual([row["song_mid"] for row in rows], ["duplicate_disallowed_song"])
            self.assertEqual(rows[0]["reason_code"], "album_type_not_allowed_duplicate_name")


if __name__ == "__main__":
    unittest.main()
