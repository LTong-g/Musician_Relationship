from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from music_metadata_graph.run_log import run_with_log
from music_metadata_graph.pipelines.defaults import DEFAULT_DB_PATH, DEFAULT_MVP_DB_PATH
from music_metadata_graph.pipelines.collect_singer_song_tab_raw import (
    CollectConfig as SongTabCollectConfig,
)
from music_metadata_graph.pipelines.collect_singer_song_tab_raw import (
    DEFAULT_PAGE_SIZE as SONG_TAB_PAGE_SIZE,
)
from music_metadata_graph.pipelines.collect_singer_song_tab_raw import (
    DEFAULT_RAW_DIR as DEFAULT_QQMUSIC_RAW_DIR,
)
from music_metadata_graph.pipelines.collect_singer_song_tab_raw import (
    DEFAULT_SINGER_LIST_RAW_DIR,
)
from music_metadata_graph.pipelines.collect_singer_song_tab_raw import (
    resolve_targets as resolve_song_tab_targets,
)


DEFAULT_QQMUSIC_ROOT = Path("data/raw/qqmusic")
DEFAULT_SINGER_LIST_RAW_DIR_PATH = Path("data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all")
DEFAULT_SONG_TAB_RAW_DIR = Path("data/raw/qqmusic/singer_homepage_song_tab")
DEFAULT_ALBUM_DETAIL_RAW_DIR = Path("data/raw/qqmusic/song_album_detail")
DEFAULT_PRODUCER_RAW_DIR = Path("data/raw/qqmusic/song_producer")
DEFAULT_SONG_SINGER_MID_FILL_CSV = Path(
    "data/processed/validation/song_singer_mid_fill/csv_views/song_singer_mid_fill.csv"
)
DEFAULT_SONG_CREDIT_MID_FILL_CSV = Path(
    "data/processed/validation/song_credit_mid_fill/csv_views/song_credit_mid_fill.csv"
)
DEFAULT_SONG_IMPORT_REJECTION_CSV = Path(
    "data/processed/validation/song_import_rejections/csv_views/song_import_rejections.csv"
)
DEFAULT_ALBUM_IMPORT_REJECTION_CSV = Path(
    "data/processed/validation/album_import_rejections/csv_views/album_import_rejections.csv"
)
DEFAULT_ALBUM_DETAIL_FETCH_FAILURE_JSON = Path(
    "data/processed/validation/album_detail_fetch_failures/album_detail_fetch_failures.json"
)
DEFAULT_STEP8_REJECTION_CSV = Path(
    "data/processed/validation/song_filtering/csv_views/songs_removed_by_step8_album_type.csv"
)
DEFAULT_STEP11_REJECTION_CSV = Path(
    "data/processed/validation/song_filtering/csv_views/songs_removed_by_step11_incomplete_credits.csv"
)
DEFAULT_STEP12_REJECTION_CSV = Path(
    "data/processed/validation/song_filtering/csv_views/songs_removed_by_step12_same_credit_name_dedupe.csv"
)
DEFAULT_STEP13_REJECTION_CSV = Path(
    "data/processed/validation/song_filtering/csv_views/songs_removed_by_step13_language_9.csv"
)
DEFAULT_STEP10_TEMP_SONGS_CSV = Path(
    "data/processed/validation/temp_song_filtering/csv_views/songs_after_step10_credit_import.csv"
)
DEFAULT_STEP11_TEMP_KEPT_CSV = Path(
    "data/processed/validation/temp_song_filtering/csv_views/songs_after_step11_complete_credits.csv"
)
DEFAULT_STEP12_TEMP_KEPT_CSV = Path(
    "data/processed/validation/temp_song_filtering/csv_views/songs_after_step12_same_credit_name_dedupe.csv"
)
DEFAULT_STEP13_TEMP_KEPT_CSV = Path(
    "data/processed/validation/temp_song_filtering/csv_views/songs_after_step13_language_filter.csv"
)

ALLOWED_ALBUM_TYPES = {"Single", "EP", "录音室专辑"}
REQUIRED_CREDIT_ROLES = {"作词", "作曲"}
REMOVED_LANGUAGE = 9


class PipelineCheckError(RuntimeError):
    pass


@dataclass(frozen=True)
class PipelineContext:
    db_path: Path
    qqmusic_root: Path
    singer_list_raw_dir: Path
    song_tab_raw_dir: Path
    album_detail_raw_dir: Path
    producer_raw_dir: Path
    continue_from: int
    stop_after: int
    dry_run: bool
    mvp: bool


@dataclass(frozen=True)
class PipelineStep:
    number: int
    label: str
    module: str
    args: tuple[str, ...]
    precheck: Callable[[PipelineContext], None]
    postcheck: Callable[[PipelineContext], dict[str, Any]]


def ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def fail(message: str) -> None:
    raise PipelineCheckError(message)


def ensure_file(path: Path) -> None:
    if not path.exists() or not path.is_file():
        fail(f"Required file does not exist: {path}")


def ensure_dir(path: Path) -> None:
    if not path.exists() or not path.is_dir():
        fail(f"Required directory does not exist: {path}")


def ensure_db(path: Path) -> None:
    if not path.exists() or not path.is_file():
        fail(f"Database does not exist: {path}")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def json_files(path: Path, pattern: str = "*.json") -> list[Path]:
    ensure_dir(path)
    return sorted(path.glob(pattern))


def connect(db_path: Path) -> sqlite3.Connection:
    ensure_db(db_path)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def db_scalar(db_path: Path, sql: str, params: tuple[Any, ...] = ()) -> Any:
    with connect(db_path) as connection:
        return connection.execute(sql, params).fetchone()[0]


def table_exists(db_path: Path, table: str) -> bool:
    with connect(db_path) as connection:
        return (
            connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
                (table,),
            ).fetchone()
            is not None
        )


def table_count(db_path: Path, table: str) -> int:
    if not table_exists(db_path, table):
        fail(f"Required table does not exist: {table}")
    return int(db_scalar(db_path, f"SELECT COUNT(*) FROM {table}"))


def foreign_key_violations(db_path: Path) -> list[dict[str, Any]]:
    with connect(db_path) as connection:
        return [dict(row) for row in connection.execute("PRAGMA foreign_key_check").fetchall()]


def ensure_no_foreign_key_violations(db_path: Path) -> None:
    violations = foreign_key_violations(db_path)
    if violations:
        fail(f"SQLite foreign key violations detected: {violations[:10]}")


def count_singer_list_rows(raw_dir: Path) -> tuple[int, int]:
    files = json_files(raw_dir, "page_*.json")
    rows = 0
    for path in files:
        payload = load_json(path)
        singerlist = payload.get("singerlist")
        hotlist = payload.get("hotlist")
        if isinstance(singerlist, list):
            rows += len(singerlist)
        if isinstance(hotlist, list):
            rows += len(hotlist)
    return len(files), rows


def song_tab_targets(ctx: PipelineContext):
    config = SongTabCollectConfig(
        raw_dir=ctx.qqmusic_root,
        db_path=ctx.db_path,
        page_size=SONG_TAB_PAGE_SIZE,
        singer_list_raw_dir=ctx.singer_list_raw_dir,
        max_pages_per_singer=None,
        force=False,
        all_singers=True,
        mvp=ctx.mvp,
        mids=(),
        names=(),
    )
    return resolve_song_tab_targets(config)


def song_tab_files_for_target(ctx: PipelineContext, mid: str) -> list[Path]:
    return sorted((ctx.song_tab_raw_dir / mid).glob("page_*_size_*.json"))


def ensure_song_tab_complete(ctx: PipelineContext) -> dict[str, Any]:
    targets = song_tab_targets(ctx)
    if not targets:
        fail("Step 3 target resolution returned no singers.")
    missing = [f"{target.name}({target.mid})" for target in targets if not song_tab_files_for_target(ctx, target.mid)]
    if missing:
        fail(f"Song-tab raw JSON is missing for {len(missing)} step-3 target singer(s): {missing[:20]}")
    file_count = sum(len(song_tab_files_for_target(ctx, target.mid)) for target in targets)
    return {"target_singers": len(targets), "song_tab_files": file_count}


def ensure_song_tab_available(ctx: PipelineContext) -> dict[str, Any]:
    targets = song_tab_targets(ctx)
    if not targets:
        fail("Step 3 target resolution returned no singers.")
    existing = [target for target in targets if song_tab_files_for_target(ctx, target.mid)]
    if not existing:
        fail("No step-3 target singer homepage song-tab raw JSON exists yet.")
    file_count = sum(len(song_tab_files_for_target(ctx, target.mid)) for target in existing)
    return {
        "target_singers": len(targets),
        "available_song_tab_singers": len(existing),
        "song_tab_files": file_count,
    }


def song_tab_singer_mid_set(ctx: PipelineContext) -> set[str]:
    mids: set[str] = set()
    for target in song_tab_targets(ctx):
        for path in song_tab_files_for_target(ctx, target.mid):
            payload = load_json(path)
            for song in ((payload.get("SongTab") or {}).get("List") or []):
                singers = song.get("singer") if isinstance(song, dict) and isinstance(song.get("singer"), list) else []
                for singer in singers:
                    if not isinstance(singer, dict):
                        continue
                    mid = str(singer.get("mid") or "").strip()
                    if mid:
                        mids.add(mid)
    return mids


def artist_mid_set(db_path: Path) -> set[str]:
    with connect(db_path) as connection:
        return {str(row["mid"]) for row in connection.execute("SELECT mid FROM artists").fetchall()}


def ensure_song_tab_singer_mids_in_artists(ctx: PipelineContext) -> dict[str, Any]:
    source_mids = song_tab_singer_mid_set(ctx)
    db_mids = artist_mid_set(ctx.db_path)
    missing = sorted(source_mids - db_mids)
    if missing:
        fail(f"{len(missing)} song-tab singer MID(s) are not in artists after step 4: {missing[:20]}")
    return {"song_tab_singer_mids": len(source_mids), "missing_artist_mids": 0}


def song_mids(db_path: Path) -> set[str]:
    with connect(db_path) as connection:
        return {str(row["mid"]) for row in connection.execute("SELECT mid FROM songs").fetchall()}


def ensure_producer_raw_complete(ctx: PipelineContext) -> dict[str, Any]:
    mids = song_mids(ctx.db_path)
    if not mids:
        fail("No songs exist before checking producer raw JSON.")
    missing = sorted(mid for mid in mids if not (ctx.producer_raw_dir / f"{mid}.json").exists())
    if missing:
        fail(f"Producer raw JSON is missing for {len(missing)} song(s): {missing[:20]}")
    return {"songs": len(mids), "producer_raw_files_for_songs": len(mids)}


def ensure_no_disallowed_album_types(ctx: PipelineContext) -> dict[str, Any]:
    with connect(ctx.db_path) as connection:
        rows = connection.execute(
            """
            SELECT albums.albumType AS album_type, COUNT(*) AS count
            FROM songs
            JOIN albums ON albums.mid = songs.album_mid
            GROUP BY albums.albumType
            """
        ).fetchall()
    distribution = {str(row["album_type"]): int(row["count"]) for row in rows}
    disallowed = {album_type: count for album_type, count in distribution.items() if album_type not in ALLOWED_ALBUM_TYPES}
    if disallowed:
        fail(f"Disallowed album types remain after step 8: {disallowed}")
    return {"album_type_distribution": distribution}


def ensure_credit_roles_exist(ctx: PipelineContext) -> dict[str, Any]:
    with connect(ctx.db_path) as connection:
        rows = connection.execute(
            "SELECT role, COUNT(*) AS count FROM song_credit_artists GROUP BY role"
        ).fetchall()
    distribution = {str(row["role"]): int(row["count"]) for row in rows}
    missing = sorted(REQUIRED_CREDIT_ROLES - set(distribution))
    if missing:
        fail(f"Missing required credit role(s) after step 10: {missing}")
    return {"credit_role_distribution": distribution}


def ensure_no_removed_language_songs(ctx: PipelineContext) -> dict[str, Any]:
    count = int(db_scalar(ctx.db_path, "SELECT COUNT(*) FROM songs WHERE language = ?", (REMOVED_LANGUAGE,)))
    if count:
        fail(f"{count} song(s) still have language={REMOVED_LANGUAGE}.")
    return {"language_9_songs": 0}


def ensure_no_incomplete_credit_songs(ctx: PipelineContext) -> dict[str, Any]:
    with connect(ctx.db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                songs.mid,
                SUM(CASE WHEN song_credit_artists.role = '作词' THEN 1 ELSE 0 END) AS lyricist_count,
                SUM(CASE WHEN song_credit_artists.role = '作曲' THEN 1 ELSE 0 END) AS composer_count
            FROM songs
            LEFT JOIN song_credit_artists ON song_credit_artists.song_mid = songs.mid
            GROUP BY songs.mid
            HAVING lyricist_count = 0 OR composer_count = 0
            LIMIT 20
            """
        ).fetchall()
    if rows:
        fail(f"Songs without both lyricist and composer remain after step 11: {[dict(row) for row in rows]}")
    return {"incomplete_credit_songs": 0}


def ensure_song_ids_unique(ctx: PipelineContext) -> dict[str, Any]:
    duplicate_mid_count = int(
        db_scalar(
            ctx.db_path,
            "SELECT COUNT(*) FROM (SELECT mid FROM songs GROUP BY mid HAVING COUNT(*) > 1)",
        )
    )
    duplicate_id_count = int(
        db_scalar(
            ctx.db_path,
            "SELECT COUNT(*) FROM (SELECT id FROM songs GROUP BY id HAVING COUNT(*) > 1)",
        )
    )
    if duplicate_mid_count or duplicate_id_count:
        fail(
            "Duplicate song identifiers remain after step 12: "
            f"mid_groups={duplicate_mid_count}, id_groups={duplicate_id_count}"
        )
    return {"duplicate_song_mid_groups": duplicate_mid_count, "duplicate_song_id_groups": duplicate_id_count}


def check_singer_list_raw(ctx: PipelineContext) -> dict[str, Any]:
    page_count, row_count = count_singer_list_rows(ctx.singer_list_raw_dir)
    if page_count == 0 or row_count == 0:
        fail(f"Singer list raw JSON is empty: pages={page_count}, rows={row_count}")
    return {"singer_list_pages": page_count, "singer_list_rows": row_count}


def check_artists(ctx: PipelineContext) -> dict[str, Any]:
    count = table_count(ctx.db_path, "artists")
    if count <= 0:
        fail("artists table is empty.")
    ensure_no_foreign_key_violations(ctx.db_path)
    return {"artists": count}


def check_album_raw(ctx: PipelineContext) -> dict[str, Any]:
    files = json_files(ctx.album_detail_raw_dir, "*.json")
    if not files:
        fail("Album detail raw JSON directory is empty.")
    return {"album_detail_raw_files": len(files)}


def check_albums(ctx: PipelineContext) -> dict[str, Any]:
    count = table_count(ctx.db_path, "albums")
    if count <= 0:
        fail("albums table is empty.")
    ensure_no_foreign_key_violations(ctx.db_path)
    return {"albums": count}


def check_songs(ctx: PipelineContext) -> dict[str, Any]:
    songs = table_count(ctx.db_path, "songs")
    song_singers = table_count(ctx.db_path, "song_singers")
    if songs <= 0:
        fail("songs table is empty.")
    if song_singers <= 0:
        fail("song_singers table is empty.")
    ensure_no_foreign_key_violations(ctx.db_path)
    return {"songs": songs, "song_singers": song_singers}


def check_song_credit_rows(ctx: PipelineContext) -> dict[str, Any]:
    credits = table_count(ctx.db_path, "song_credit_artists")
    if credits <= 0:
        fail("song_credit_artists table is empty.")
    ensure_no_foreign_key_violations(ctx.db_path)
    return {"song_credit_artists": credits}


def check_csv(path: Path) -> dict[str, Any]:
    ensure_file(path)
    if path.stat().st_size <= 0:
        fail(f"CSV is empty: {path}")
    return {"csv": path.as_posix(), "bytes": path.stat().st_size}


def check_db_exists(ctx: PipelineContext) -> dict[str, Any]:
    ensure_db(ctx.db_path)
    return {"db_path": ctx.db_path.as_posix()}


def check_noop(_: PipelineContext) -> dict[str, Any]:
    return {}


def command_args(*values: str | Path) -> tuple[str, ...]:
    return tuple(str(value) for value in values)


def mode_args(ctx: PipelineContext) -> tuple[str, ...]:
    return ("--mvp",) if ctx.mvp else ()


def output_path(ctx: PipelineContext, path: Path) -> Path:
    if not ctx.mvp:
        return path
    parts = path.parts
    try:
        index = parts.index("validation")
    except ValueError:
        return path
    return Path(*parts[:index], "validation_mvp", *parts[index + 1 :])


def build_steps(ctx: PipelineContext) -> list[PipelineStep]:
    return [
        PipelineStep(
            1,
            "完整歌手列表 raw JSON",
            "music_metadata_graph.pipelines.collect_singer_list_raw",
            command_args("--raw-dir", ctx.qqmusic_root) + mode_args(ctx),
            lambda _: None,
            check_singer_list_raw,
        ),
        PipelineStep(
            2,
            "歌手列表入库",
            "music_metadata_graph.pipelines.import_singer_list_to_db",
            command_args("--raw-dir", ctx.singer_list_raw_dir, "--db", ctx.db_path) + mode_args(ctx),
            lambda c: check_singer_list_raw(c),
            check_artists,
        ),
        PipelineStep(
            3,
            "歌手主页歌曲 Tab raw JSON",
            "music_metadata_graph.pipelines.collect_singer_song_tab_raw",
            command_args(
                "--raw-dir",
                ctx.qqmusic_root,
                "--db",
                ctx.db_path,
                "--singer-list-raw-dir",
                ctx.singer_list_raw_dir,
                "--all",
            )
            + mode_args(ctx),
            lambda c: check_artists(c),
            ensure_song_tab_complete,
        ),
        PipelineStep(
            4,
            "前置 quick_search 补歌曲歌手缺 MID",
            "music_metadata_graph.pipelines.fill_song_singer_missing_mids",
            command_args(
                "--raw-dir",
                ctx.qqmusic_root,
                "--db",
                ctx.db_path,
                "--csv",
                output_path(ctx, DEFAULT_SONG_SINGER_MID_FILL_CSV),
                "--singer-list-raw-dir",
                ctx.singer_list_raw_dir,
                "--all",
            )
            + mode_args(ctx),
            lambda c: ensure_song_tab_available(c),
            lambda c: check_csv(output_path(c, DEFAULT_SONG_SINGER_MID_FILL_CSV)),
        ),
        PipelineStep(
            5,
            "补全歌曲歌手信息",
            "music_metadata_graph.pipelines.collect_missing_song_singers_to_db",
            command_args(
                "--raw-dir",
                ctx.qqmusic_root,
                "--db",
                ctx.db_path,
                "--singer-list-raw-dir",
                ctx.singer_list_raw_dir,
                "--all",
            )
            + mode_args(ctx),
            lambda c: ensure_song_tab_available(c),
            ensure_song_tab_singer_mids_in_artists,
        ),
        PipelineStep(
            6,
            "按歌曲请求专辑详情 raw JSON",
            "music_metadata_graph.pipelines.collect_song_album_detail_raw",
            command_args(
                "--raw-dir",
                ctx.qqmusic_root,
                "--db",
                ctx.db_path,
                "--singer-list-raw-dir",
                ctx.singer_list_raw_dir,
                "--max-failed-fetches",
                "10",
                "--failure-json",
                output_path(ctx, DEFAULT_ALBUM_DETAIL_FETCH_FAILURE_JSON),
                "--all",
            )
            + mode_args(ctx),
            lambda c: ensure_song_tab_available(c),
            check_album_raw,
        ),
        PipelineStep(
            7,
            "专辑详情入库",
            "music_metadata_graph.pipelines.import_song_album_detail_to_db",
            command_args(
                "--raw-dir",
                ctx.album_detail_raw_dir,
                "--db",
                ctx.db_path,
                "--rejection-csv",
                output_path(ctx, DEFAULT_ALBUM_IMPORT_REJECTION_CSV),
            ),
            check_album_raw,
            check_albums,
        ),
        PipelineStep(
            8,
            "歌曲入库与拒绝 CSV",
            "music_metadata_graph.pipelines.import_singer_song_tab_to_db",
            command_args(
                "--raw-dir",
                ctx.song_tab_raw_dir,
                "--db",
                ctx.db_path,
                "--rejection-csv",
                output_path(ctx, DEFAULT_SONG_IMPORT_REJECTION_CSV),
                "--singer-list-raw-dir",
                ctx.singer_list_raw_dir,
                "--qqmusic-raw-dir",
                ctx.qqmusic_root,
                "--all",
            )
            + mode_args(ctx),
            lambda c: {**check_artists(c), **check_albums(c), **ensure_song_tab_available(c)},
            check_songs,
        ),
        PipelineStep(
            9,
            "按专辑类型过滤已入库歌曲",
            "music_metadata_graph.pipelines.filter_songs_by_album_type",
            command_args("--db", ctx.db_path, "--rejection-csv", output_path(ctx, DEFAULT_STEP8_REJECTION_CSV)),
            check_songs,
            lambda c: {**check_songs(c), **ensure_no_disallowed_album_types(c)},
        ),
        PipelineStep(
            10,
            "请求制作人 raw JSON",
            "music_metadata_graph.pipelines.collect_song_producer_raw",
            command_args("--raw-dir", ctx.producer_raw_dir, "--db", ctx.db_path),
            check_songs,
            ensure_producer_raw_complete,
        ),
        PipelineStep(
            11,
            "前置 quick_search 补作词作曲缺 MID",
            "music_metadata_graph.pipelines.fill_song_credit_missing_mids",
            command_args(
                "--raw-dir",
                ctx.qqmusic_root,
                "--db",
                ctx.db_path,
                "--csv",
                output_path(ctx, DEFAULT_SONG_CREDIT_MID_FILL_CSV),
            ),
            ensure_producer_raw_complete,
            lambda c: check_csv(output_path(c, DEFAULT_SONG_CREDIT_MID_FILL_CSV)),
        ),
        PipelineStep(
            12,
            "导入作词作曲关系",
            "music_metadata_graph.pipelines.import_song_credits_to_db",
            command_args(
                "--raw-dir",
                ctx.producer_raw_dir,
                "--db",
                ctx.db_path,
                "--temp-songs-csv",
                output_path(ctx, DEFAULT_STEP10_TEMP_SONGS_CSV),
            ),
            ensure_producer_raw_complete,
            lambda c: {**check_song_credit_rows(c), **ensure_credit_roles_exist(c)},
        ),
        PipelineStep(
            13,
            "删除作词作曲不完整歌曲",
            "music_metadata_graph.pipelines.filter_songs_by_credit_completeness",
            command_args(
                "--db",
                ctx.db_path,
                "--rejection-csv",
                output_path(ctx, DEFAULT_STEP11_REJECTION_CSV),
                "--temp-kept-csv",
                output_path(ctx, DEFAULT_STEP11_TEMP_KEPT_CSV),
            ),
            lambda c: {**check_songs(c), **check_song_credit_rows(c)},
            lambda c: {**check_songs(c), **ensure_no_incomplete_credit_songs(c)},
        ),
        PipelineStep(
            14,
            "按规范化歌名和同作词作曲去重",
            "music_metadata_graph.pipelines.filter_imported_songs",
            command_args(
                "--db",
                ctx.db_path,
                "--name-dedupe-rejection-csv",
                output_path(ctx, DEFAULT_STEP12_REJECTION_CSV),
                "--temp-kept-csv",
                output_path(ctx, DEFAULT_STEP12_TEMP_KEPT_CSV),
            ),
            lambda c: {**check_songs(c), **ensure_no_incomplete_credit_songs(c)},
            lambda c: {**check_songs(c), **ensure_song_ids_unique(c)},
        ),
        PipelineStep(
            15,
            "按 language=9 过滤歌曲",
            "music_metadata_graph.pipelines.filter_songs_by_language",
            command_args(
                "--db",
                ctx.db_path,
                "--rejection-csv",
                output_path(ctx, DEFAULT_STEP13_REJECTION_CSV),
                "--temp-kept-csv",
                output_path(ctx, DEFAULT_STEP13_TEMP_KEPT_CSV),
            ),
            lambda c: {**check_songs(c), **ensure_no_incomplete_credit_songs(c), **ensure_song_ids_unique(c)},
            lambda c: {**check_songs(c), **ensure_no_removed_language_songs(c)},
        ),
    ]


def run_subprocess(step: PipelineStep, ctx: PipelineContext) -> None:
    command = [sys.executable, "-m", step.module, *step.args]
    print(json.dumps({"step": step.number, "label": step.label, "command": command}, ensure_ascii=False))
    if ctx.dry_run:
        return
    result = subprocess.run(command, cwd=Path.cwd())
    if result.returncode != 0:
        fail(f"Step {step.number} failed with exit code {result.returncode}: {step.label}")


def run_pipeline(ctx: PipelineContext) -> dict[str, Any]:
    if ctx.continue_from > ctx.stop_after:
        fail("--continue-from cannot be greater than --stop-after.")
    summaries: list[dict[str, Any]] = []
    for step in build_steps(ctx):
        if step.number < ctx.continue_from or step.number > ctx.stop_after:
            continue
        print(f"precheck step {step.number}: {step.label}")
        precheck_result = step.precheck(ctx)
        if precheck_result:
            print(json.dumps({"step": step.number, "precheck": precheck_result}, ensure_ascii=False, indent=2))
        run_subprocess(step, ctx)
        print(f"postcheck step {step.number}: {step.label}")
        postcheck_result = step.postcheck(ctx)
        print(json.dumps({"step": step.number, "postcheck": postcheck_result}, ensure_ascii=False, indent=2))
        summaries.append({"step": step.number, "label": step.label, "postcheck": postcheck_result})
    return {
        "status": "completed",
        "steps_run": [item["step"] for item in summaries],
        "summaries": summaries,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full metadata graph pipeline with safety checks between steps.")
    parser.add_argument("--db", type=Path, default=None)
    parser.add_argument("--qqmusic-root", type=Path, default=DEFAULT_QQMUSIC_ROOT)
    parser.add_argument("--singer-list-raw-dir", type=Path, default=DEFAULT_SINGER_LIST_RAW_DIR_PATH)
    parser.add_argument("--continue-from", type=int, default=1, help="First orchestrator step number to run.")
    parser.add_argument("--stop-after", type=int, default=15, help="Last orchestrator step number to run.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands and run checks without executing step commands.")
    parser.add_argument("--mvp", action="store_true", help="Run the MVP flow with shared raw data, MVP database, and MVP validation outputs.")
    return parser.parse_args()


def _main() -> None:
    ensure_utf8_stdout()
    args = parse_args()
    db_path = args.db if args.db is not None else (DEFAULT_MVP_DB_PATH if args.mvp else DEFAULT_DB_PATH)
    ctx = PipelineContext(
        db_path=db_path,
        qqmusic_root=args.qqmusic_root,
        singer_list_raw_dir=args.singer_list_raw_dir,
        song_tab_raw_dir=args.qqmusic_root / "singer_homepage_song_tab",
        album_detail_raw_dir=args.qqmusic_root / "song_album_detail",
        producer_raw_dir=args.qqmusic_root / "song_producer",
        continue_from=args.continue_from,
        stop_after=args.stop_after,
        dry_run=args.dry_run,
        mvp=args.mvp,
    )
    print(json.dumps(run_pipeline(ctx), ensure_ascii=False, indent=2))


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()
