import unittest
from music_metadata_graph.text_normalization import normalize_song_title_identity


class TextNormalizationTest(unittest.TestCase):
    def test_normalize_song_title_identity_unifies_mixed_chinese_english_variants(self) -> None:
        self.assertEqual(
            normalize_song_title_identity("（......醉鬼阿Q）（feat.孙燕姿）"),
            normalize_song_title_identity("（……醉鬼阿Q）（feat. 孙燕姿）"),
        )

    def test_normalize_song_title_identity_keeps_semantic_version_text(self) -> None:
        self.assertNotEqual(
            normalize_song_title_identity("K歌之王 (粤语)"),
            normalize_song_title_identity("K歌之王"),
        )

    def test_normalize_song_title_identity_preserves_word_boundaries(self) -> None:
        self.assertEqual(normalize_song_title_identity("After The Rain"), "after the rain")
        self.assertEqual(normalize_song_title_identity("AfterTheRain"), "aftertherain")

    def test_normalize_song_title_identity_unifies_width_case_and_punctuation_spacing(self) -> None:
        self.assertEqual(normalize_song_title_identity(" Ａ.Ｉ. 爱 "), "a.i. 爱")
        self.assertEqual(
            normalize_song_title_identity("Tonight,I feel close to you"),
            normalize_song_title_identity("Tonight, I feel close to you"),
        )
        self.assertEqual(
            normalize_song_title_identity("A / B"), normalize_song_title_identity("A/B")
        )


if __name__ == "__main__":
    unittest.main()
