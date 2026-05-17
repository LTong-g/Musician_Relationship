from __future__ import annotations

import argparse
import json
from pathlib import Path

from music_metadata_graph.run_log import run_with_log
from music_metadata_graph.pipelines.run_full_pipeline import (
    DEFAULT_DB_PATH,
    DEFAULT_LARGE_SITE_DIR,
    DEFAULT_MVP_DB_PATH,
    DEFAULT_MVP_SITE_DIR,
    DEFAULT_QQMUSIC_ROOT,
    DEFAULT_SINGER_LIST_RAW_DIR_PATH,
    DEFAULT_SITE_DIR,
    DEFAULT_AVATAR_CACHE_DIR,
    PipelineContext,
    ensure_utf8_stdout,
    run_pipeline,
)


START_FROM_SONG_TABS_STEP = 5
DEFAULT_STOP_AFTER = 19


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the test pipeline from existing step-4 --all target singer homepage song-tab raw JSON. "
            "The runner checks that at least one in-scope step-4 raw directory exists before continuing."
        )
    )
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--qqmusic-root", type=Path, default=DEFAULT_QQMUSIC_ROOT)
    parser.add_argument("--singer-list-raw-dir", type=Path, default=DEFAULT_SINGER_LIST_RAW_DIR_PATH)
    parser.add_argument("--stop-after", type=int, default=DEFAULT_STOP_AFTER, help="Last orchestrator step number to run.")
    parser.add_argument("--site-dir", type=Path, default=None, help="Directory for the standard static site.")
    parser.add_argument("--large-site-dir", type=Path, default=None, help="Directory for the large-graph static site.")
    parser.add_argument("--avatar-cache-dir", type=Path, default=DEFAULT_AVATAR_CACHE_DIR, help="Shared avatar cache directory.")
    parser.add_argument("--skip-avatar-download", action="store_true", help="Prepare graph assets without downloading avatars.")
    parser.add_argument("--max-avatar-downloads", type=int, default=None, help="Maximum number of new avatars to download during the asset step.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands and run checks without executing step commands.")
    parser.add_argument("--mvp", action="store_true", help="Run from existing shared raw data using the MVP database and MVP validation outputs.")
    return parser.parse_args()


def _main() -> None:
    ensure_utf8_stdout()
    args = parse_args()
    db_path = args.db if args.db is not None else (DEFAULT_MVP_DB_PATH if args.mvp else DEFAULT_DB_PATH)
    site_dir = args.site_dir if args.site_dir is not None else (DEFAULT_MVP_SITE_DIR if args.mvp else DEFAULT_SITE_DIR)
    large_site_dir = args.large_site_dir if args.large_site_dir is not None else DEFAULT_LARGE_SITE_DIR
    ctx = PipelineContext(
        db_path=db_path,
        qqmusic_root=args.qqmusic_root,
        singer_list_raw_dir=args.singer_list_raw_dir,
        fans_raw_dir=args.qqmusic_root,
        song_tab_raw_dir=args.qqmusic_root / "singer_homepage_song_tab",
        album_detail_raw_dir=args.qqmusic_root / "song_album_detail",
        producer_raw_dir=args.qqmusic_root / "song_producer",
        continue_from=START_FROM_SONG_TABS_STEP,
        stop_after=args.stop_after,
        dry_run=args.dry_run,
        mvp=args.mvp,
        site_dir=site_dir,
        large_site_dir=large_site_dir,
        avatar_cache_dir=args.avatar_cache_dir,
        skip_avatar_download=args.skip_avatar_download,
        max_avatar_downloads=args.max_avatar_downloads,
    )
    print(json.dumps(run_pipeline(ctx), ensure_ascii=False, indent=2))


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()
