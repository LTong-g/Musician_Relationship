from __future__ import annotations
import json
import tempfile
import unittest
from typing import Any
from pathlib import Path
from music_metadata_graph.tools.collect_jay_chou_similar_singers import (
    ROOT_ARTIST,
    SimilarSingerConfig,
    fetch_batch,
    load_area_seed_artists,
    load_state,
    raw_request_path,
    rebuild_edges_from_raw,
    response_singers,
    save_state,
    wrap_raw_response,
    write_json,
    write_validation_outputs,
)


class FakeSingerApi:
    def get_similar(self, mid: str, number: int = 100) -> dict[str, Any]:
        return {"mid": mid, "number": number}


class FakeClient:
    def __init__(self) -> None:
        self.singer = FakeSingerApi()

        self.gather_calls: list[tuple[list[dict[str, Any]], int]] = []

    async def gather(
        self, requests: list[dict[str, Any]], *, batch_size: int, return_exceptions: bool
    ) -> list[dict[str, Any]]:
        self.gather_calls.append((requests, batch_size))

        return [
            {
                "code": 0,
                "err_msg": "",
                "singerlist": [{"id": 265, "mid": "001JDzPT3JdvqK", "name": "王力宏"}],
            }
            for _ in requests
        ]


class CollectJayChouSimilarSingersTests(unittest.TestCase):
    def test_initial_state_uses_area_0_1_seed_singers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            raw_dir = root / "raw"

            seed_dir = root / "singer_list"

            self._write_seed_list(seed_dir)

            manifest, frontier = load_state(
                SimilarSingerConfig(raw_dir=raw_dir, seed_singer_list_dir=seed_dir)
            )

            self.assertEqual(manifest["root"]["mid"], ROOT_ARTIST["mid"])

            self.assertEqual(manifest["seed_source"]["seed_count"], 2)

            self.assertEqual({item["mid"] for item in manifest["seen_artists"]}, {"mid_a", "mid_b"})

            self.assertEqual({item["mid"] for item in frontier}, {"mid_a", "mid_b"})

            self.assertTrue(all(item["depth"] == 0 for item in frontier))

            self.assertTrue((raw_dir / "manifest.json").exists())

            self.assertTrue((raw_dir / "frontier.json").exists())

    def test_raw_payload_records_depth_and_response(self) -> None:
        payload = wrap_raw_response(
            source_artist={**ROOT_ARTIST, "depth": 0},
            number=100,
            response={
                "code": 0,
                "err_msg": "",
                "singerlist": [{"id": 265, "mid": "001JDzPT3JdvqK", "name": "王力宏"}],
            },
        )

        self.assertEqual(payload["source"]["source_mid"], ROOT_ARTIST["mid"])

        self.assertEqual(payload["source"]["number"], 100)

        self.assertEqual(response_singers(payload)[0]["mid"], "001JDzPT3JdvqK")

    def test_rebuild_edges_and_validation_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            raw_dir = root / "raw"

            request_cache_dir = root / "request_cache"

            validation_dir = root / "validation"

            seed_dir = root / "singer_list"

            self._write_seed_list(seed_dir)

            manifest, frontier = load_state(
                SimilarSingerConfig(
                    raw_dir=raw_dir,
                    validation_dir=validation_dir,
                    seed_singer_list_dir=seed_dir,
                )
            )

            payload = wrap_raw_response(
                source_artist=frontier[0],
                number=100,
                response={
                    "code": 0,
                    "err_msg": "",
                    "singerlist": [
                        {"id": 265, "mid": "001JDzPT3JdvqK", "name": "王力宏", "title": "王力宏"},
                        {"id": 227, "mid": "0027pdHE4STooO", "name": "蔡依林", "title": "蔡依林"},
                    ],
                },
            )

            write_json(raw_request_path(request_cache_dir, frontier[0]["mid"]), payload)

            manifest["requested_mids"] = [frontier[0]["mid"]]

            manifest["seen_artists"].extend(
                [
                    {
                        "mid": "001JDzPT3JdvqK",
                        "id": 265,
                        "name": "王力宏",
                        "title": "王力宏",
                        "first_depth": 1,
                    },
                    {
                        "mid": "0027pdHE4STooO",
                        "id": 227,
                        "name": "蔡依林",
                        "title": "蔡依林",
                        "first_depth": 1,
                    },
                ]
            )

            save_state(raw_dir, manifest, [])

            edges = rebuild_edges_from_raw(raw_dir, request_cache_dir)

            write_validation_outputs(validation_dir, manifest, edges)

            self.assertEqual(len(edges), 2)

            summary = json.loads(
                (validation_dir / "similar_singers_summary.json").read_text(encoding="utf-8")
            )

            self.assertEqual(summary["seen_count"], 4)

            self.assertTrue((validation_dir / "csv_views" / "similar_singers_artists.csv").exists())

            self.assertTrue((validation_dir / "csv_views" / "similar_singers_edges.csv").exists())

    def test_fetch_batch_uses_client_gather_for_uncached_requests(self) -> None:
        async def run_case() -> None:
            with tempfile.TemporaryDirectory() as tmp:
                raw_dir = Path(tmp) / "raw"
                request_cache_dir = Path(tmp) / "request_cache"

                client = FakeClient()

                config = SimilarSingerConfig(
                    raw_dir=raw_dir, request_cache_dir=request_cache_dir, batch_size=20
                )

                seed = {**ROOT_ARTIST, "depth": 0}

                result = await fetch_batch(client, [seed], depth=1, config=config)

                self.assertEqual(len(client.gather_calls), 1)

                self.assertEqual(client.gather_calls[0][1], 20)

                self.assertEqual(result[0][1][1], "fetched")  # type: ignore[index]

                self.assertTrue(raw_request_path(request_cache_dir, ROOT_ARTIST["mid"]).exists())

        import asyncio

        asyncio.run(run_case())

    def test_load_area_seed_artists_filters_and_deduplicates_area_0_1(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            seed_dir = Path(tmp) / "singer_list"

            self._write_seed_list(seed_dir)

            seeds = load_area_seed_artists(seed_dir)

            self.assertEqual([seed["mid"] for seed in seeds], ["mid_a", "mid_b"])

            self.assertEqual([seed["area_id"] for seed in seeds], [0, 1])

            self.assertTrue(all(seed["first_depth"] == 0 for seed in seeds))

    def _write_seed_list(self, seed_dir: Path) -> None:
        write_json(
            seed_dir / "page_0001_size_80.json",
            {
                "singerlist": [
                    {"id": 1, "mid": "mid_a", "name": "歌手A", "title": "歌手A", "area_id": 0},
                    {"id": 2, "mid": "mid_b", "name": "歌手B", "title": "歌手B", "area_id": 1},
                    {"id": 3, "mid": "mid_c", "name": "歌手C", "title": "歌手C", "area_id": 2},
                    {
                        "id": 4,
                        "mid": "mid_a",
                        "name": "歌手A重复",
                        "title": "歌手A重复",
                        "area_id": 0,
                    },
                    {"id": 5, "mid": "", "name": "缺MID", "title": "缺MID", "area_id": 0},
                ]
            },
        )


if __name__ == "__main__":
    unittest.main()
