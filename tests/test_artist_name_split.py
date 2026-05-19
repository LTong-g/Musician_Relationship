import unittest
from music_metadata_graph.pipelines.import_singer_song_tab_to_db import (
    resolve_missing_artist_name_mids,
)
from music_metadata_graph.pipelines.import_song_credits_to_db import (
    resolve_missing_artist_name_rows,
)
from music_metadata_graph.pipelines.quick_search_artist_mid import (
    has_artist_name_separator,
    split_artist_names,
)


class ArtistNameSplitTests(unittest.TestCase):
    def test_split_artist_names_supports_slash_comma_and_enumeration_comma(self) -> None:
        self.assertTrue(has_artist_name_separator("张三/李四"))
        self.assertTrue(has_artist_name_separator("张三，李四"))
        self.assertTrue(has_artist_name_separator("张三、李四"))
        self.assertEqual(split_artist_names(" 张三 / 李四，王五、张三 "), ("张三", "李四", "王五"))

    def test_song_singer_missing_mid_resolution_uses_all_name_separators(self) -> None:
        artist_name_mid_map = {
            "张三": "mid_zhang",
            "李四": "mid_li",
            "王五": "mid_wang",
        }
        self.assertEqual(
            resolve_missing_artist_name_mids("张三，李四、王五", artist_name_mid_map),
            ["mid_zhang", "mid_li", "mid_wang"],
        )

    def test_song_credit_missing_mid_resolution_uses_all_name_separators(self) -> None:
        artist_name_map = {
            "张三": {"mid": "mid_zhang", "name": "张三"},
            "李四": {"mid": "mid_li", "name": "李四"},
            "王五": {"mid": "mid_wang", "name": "王五"},
        }
        rows = resolve_missing_artist_name_rows("张三，李四、王五", artist_name_map)
        self.assertEqual([row["mid"] for row in rows], ["mid_zhang", "mid_li", "mid_wang"])


if __name__ == "__main__":
    unittest.main()
