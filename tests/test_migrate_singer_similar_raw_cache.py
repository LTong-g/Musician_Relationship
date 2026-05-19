from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from music_metadata_graph.tools.migrate_singer_similar_raw_cache import migrate


class MigrateSingerSimilarRawCacheTests(unittest.TestCase):
    def test_flattens_numbered_cache_and_legacy_run_requests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base_dir = root / "singer_similar"
            request_cache_dir = base_dir / "request_cache"
            runs_dir = base_dir / "runs"

            self._write_json(
                request_cache_dir / "number_100" / "mid_a.json",
                {
                    "source": {"source_mid": "mid_a", "number": 100},
                    "response": {"singerlist": [{"mid": "mid_b", "name": "B"}]},
                },
            )
            self._write_json(
                base_dir / "legacy_root" / "manifest.json",
                {"number": 100, "requested_mids": ["mid_b"], "seen_artists": []},
            )
            self._write_json(base_dir / "legacy_root" / "frontier.json", {"frontier": []})
            self._write_json(
                base_dir / "legacy_root" / "requests" / "mid_b.json",
                {
                    "source": {"source_mid": "mid_b", "number": 100, "depth": 1},
                    "response": {"singerlist": [{"mid": "mid_c", "name": "C"}]},
                },
            )

            summary = migrate(base_dir, request_cache_dir, runs_dir)

            self.assertEqual(summary["conflict_count"], 0)
            self.assertTrue((request_cache_dir / "mid_a.json").exists())
            self.assertTrue((request_cache_dir / "mid_b.json").exists())
            self.assertTrue((runs_dir / "legacy_root" / "manifest.json").exists())

            flattened_payload = self._read_json(request_cache_dir / "mid_b.json")
            self.assertNotIn("depth", flattened_payload["source"])

    def _write_json(self, path: Path, data: dict[str, object]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_json(self, path: Path) -> dict[str, object]:
        return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
