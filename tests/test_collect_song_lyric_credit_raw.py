from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from music_metadata_graph.pipelines.collect_song_lyric_credit_raw import (
    CACHE_KIND,
    build_lyric_credit_evidence,
    execute_request_batch,
    load_or_migrate_lyric_credit_evidence,
    parse_lyric_credit_rows,
)


class CollectSongLyricCreditRawTests(unittest.TestCase):
    def roles(self, lyric: str) -> dict[str, str]:
        rows = parse_lyric_credit_rows({"crypt": 0, "lyric": lyric}, raw_path="raw/song.json")
        return {str(row["role"]): str(row["name"]) for row in rows}

    def test_parse_combined_composer_arranger_label(self) -> None:
        roles = self.roles("[ti:浪淘沙]\n作词：古柳\n作曲、编曲：李志辉\n演唱：罗勤颖")

        self.assertEqual(roles["作词"], "古柳")
        self.assertEqual(roles["作曲"], "李志辉")

    def test_single_character_composer_label_does_not_match_arranger(self) -> None:
        roles = self.roles("词：甲\n编曲：乙\n曲：丙")

        self.assertEqual(roles["作词"], "甲")
        self.assertEqual(roles["作曲"], "丙")

    def test_parse_japanese_and_english_labels_case_insensitively(self) -> None:
        rows = parse_lyric_credit_rows(
            {
                "crypt": 0,
                "lyric": "[00:01.00]詞：山田\n[00:02.00]COMPOSED BY: Alice\nLyrics by: Bob",
            }
        )
        pairs = {(str(row["role"]), str(row["name"])) for row in rows}

        self.assertIn(("作词", "山田"), pairs)
        self.assertIn(("作曲", "Alice"), pairs)
        self.assertIn(("作词", "Bob"), pairs)

    def test_parser_only_uses_early_effective_header_lines(self) -> None:
        lyric = "\n".join(
            [
                "[ti:Song]",
                "演唱：A",
                "发行：B",
                "监制：C",
                "出品：D",
                "歌词正文",
                "作词：太晚",
                "作曲：太晚",
            ]
        )

        self.assertEqual(parse_lyric_credit_rows({"crypt": 0, "lyric": lyric}), [])

    def test_build_evidence_keeps_only_header_and_parsed_rows(self) -> None:
        evidence = build_lyric_credit_evidence(
            {
                "crypt": 0,
                "lyric": "[ti:Song]\n作词：甲\n作曲：乙\n正文第一行\n正文第二行",
                "trans": "完整翻译",
                "roma": "完整罗马音",
                "qrc": "完整 qrc",
            },
            target={
                "song_mid": "song_mid",
                "song_id": "123",
                "song_name": "Song",
                "missing_roles": ["作词", "作曲"],
            },
            raw_path="raw/song_mid.json",
        )

        self.assertEqual(evidence["cache_kind"], CACHE_KIND)
        self.assertEqual(evidence["song_mid"], "song_mid")
        self.assertEqual(evidence["producer_missing_roles"], ["作词", "作曲"])
        self.assertNotIn("lyric", evidence)
        self.assertNotIn("trans", evidence)
        self.assertNotIn("roma", evidence)
        self.assertNotIn("qrc", evidence)
        self.assertEqual(
            {(row["role"], row["name"]) for row in evidence["parsed_credit_rows"]},
            {("作词", "甲"), ("作曲", "乙")},
        )

    def test_parse_evidence_rows(self) -> None:
        evidence = build_lyric_credit_evidence(
            {"crypt": 0, "lyric": "作词：甲\n作曲：乙"},
            raw_path="raw/song_mid.json",
        )

        rows = parse_lyric_credit_rows(evidence, raw_path="raw/song_mid.json")

        self.assertEqual(
            [(row["role"], row["name"]) for row in rows],
            [("作词", "甲"), ("作曲", "乙")],
        )
        self.assertTrue(all(row["raw_json_path"] == "raw/song_mid.json" for row in rows))

    def test_legacy_raw_is_migrated_in_place(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "song_mid.json"
            path.write_text(
                json.dumps(
                    {"crypt": 0, "lyric": "作词：甲\n作曲：乙", "trans": "完整翻译"},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = load_or_migrate_lyric_credit_evidence(
                path,
                target={"song_mid": "song_mid", "song_id": "1", "song_name": "Song"},
            )
            saved = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(result.status, "migrated_legacy_raw")
        self.assertEqual(saved["cache_kind"], CACHE_KIND)
        self.assertNotIn("lyric", saved)
        self.assertNotIn("trans", saved)
        self.assertEqual(
            [(row["role"], row["name"]) for row in saved["parsed_credit_rows"]],
            [("作词", "甲"), ("作曲", "乙")],
        )

    def test_fetched_payload_is_saved_as_evidence(self) -> None:
        class FakeClient:
            async def gather(self, requests, *, batch_size, return_exceptions):
                return [{"crypt": 0, "lyric": "作词：甲\n作曲：乙", "trans": "完整翻译"}]

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "song_mid.json"
            loaded, failures = self.run_async(
                execute_request_batch(
                    FakeClient(),
                    config=None,
                    batch=[
                        (
                            0,
                            {
                                "song_mid": "song_mid",
                                "song_id": "1",
                                "song_name": "Song",
                                "missing_roles": ["作词", "作曲"],
                            },
                            path,
                            object(),
                        )
                    ],
                )
            )
            saved = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(failures, [])
        self.assertEqual(loaded[0][3], "fetched")
        self.assertEqual(saved["cache_kind"], CACHE_KIND)
        self.assertNotIn("lyric", saved)
        self.assertNotIn("trans", saved)

    def run_async(self, coroutine):
        import asyncio

        return asyncio.run(coroutine)


if __name__ == "__main__":
    unittest.main()
