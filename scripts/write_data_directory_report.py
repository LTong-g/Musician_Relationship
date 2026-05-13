from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ARCHIVE = ROOT / "archive" / "legacy_pipeline_2026-05-12"
REPORT = ROOT / "reports" / "data_directory_tree_2026-05-12.md"


MAJOR_PATHS = [
    ("data/raw/qqmusic/high_confidence_singer_songs/", "高可信歌曲子集流程的原始 QQ 音乐缓存，包含歌手专辑列表页和专辑歌曲页。"),
    ("data/raw/qqmusic/singer_homepage_song_tab/", "当前补充分支的原始 QQ 音乐缓存，保存歌手歌曲 Tab 分页响应。"),
    ("data/processed/validation/four_singers/json_outputs/high_confidence_singer_songs/", "四位测试歌手高可信子集的 JSON 查看版，不属于正式全量输出。"),
    ("data/processed/validation/four_singers/json_outputs/supplement_singer_songs/", "四位测试歌手补充分支的 JSON 查看版，不属于正式全量输出；包含空专辑过滤和高可信歌名过滤两步结果。"),
    ("data/processed/validation/four_singers/csv_views/high_confidence_singer_songs/", "四位测试歌手高可信子集的 CSV 查看版，只用于人工检查。"),
    ("data/processed/validation/four_singers/csv_views/supplement_singer_songs/", "四位测试歌手补充分支的 CSV 查看版，只用于人工检查。"),
    ("archive/legacy_pipeline_2026-05-12/", "已从当前正式目录剥离的旧流程代码、旧网页、旧数据和旧缓存，不参与当前正式流程。"),
]

LEGACY_PATHS = [
    "archive/legacy_pipeline_2026-05-12/code/music_metadata_graph/pipelines/",
    "archive/legacy_pipeline_2026-05-12/web/",
    "archive/legacy_pipeline_2026-05-12/data/processed/singer_songs/",
    "archive/legacy_pipeline_2026-05-12/data/processed/validation/legacy/",
    "archive/legacy_pipeline_2026-05-12/data/raw/qqmusic/singer_songs/",
    "archive/legacy_pipeline_2026-05-12/data/raw/qqmusic/song_producers/",
    "archive/legacy_pipeline_2026-05-12/data/raw/qqmusic/album_probe/",
]

FILE_PATTERNS = [
    ("summary.json", "运行摘要，记录来源、规则、计数和输出位置。"),
    ("singer_song_snapshot.json", "单个歌手歌曲流程快照，记录目标歌手、请求参数和计数。"),
    ("singers.json", "该输出目录使用的目标歌手身份信息。"),
    ("albums_all.json", "高可信流程的专辑全集。"),
    ("songs_all.json", "高可信流程中已纳入专辑请求到的歌曲全集，不是过滤步骤。"),
    ("songs_after_filter1_target_singer_match.json", "高可信流程 filter1 后保留的目标歌手匹配行。"),
    ("songs_removed_by_filter1_target_singer_match.json", "高可信流程 filter1 中未命中目标歌手 mid 的移除行。"),
    ("songs_after_filter2_dedupe.json", "高可信流程 filter2 后的去重保留行；先按歌曲 mid/id 去重，再只按原始 name 去重，同 name 候选优先保留录音室专辑，其次 EP，再次 Single，仍相同时保留数值 id 更小的歌曲。"),
    ("songs_removed_by_filter2_dedupe.json", "高可信流程 filter2 中因重复 mid/id、缺失 mid/id 或同 name 优先级被移除的歌曲。"),
    ("albums_included.json", "高可信流程中因 albumType 命中规则而保留的专辑。"),
    ("albums_excluded.json", "高可信流程中因 albumType 不在规则内而排除的专辑。"),
    ("songs_all.json", "补充分支的候选歌曲集合。"),
    ("songs_after_filter1_empty_album_exclusion.json", "补充分支 filter1 后的空专辑过滤保留行。"),
    ("songs_removed_by_filter1_empty_album_exclusion.json", "补充分支 filter1 中因空专辑而移除的歌曲行。"),
    ("songs_after_filter2_album_identity.json", "补充分支 filter2 后的专辑 id/mid 非空保留行。"),
    ("songs_removed_by_filter2_album_identity.json", "补充分支 filter2 中因专辑 id/mid 为空而移除的歌曲行。"),
    ("songs_after_album_detail_enrich.json", "补充分支补充专辑详情后的歌曲行，包含 aux_album_detail_* 字段。"),
    ("songs_after_filter3_album_type.json", "补充分支 filter3 后的专辑类型保留行，只保留 Single、EP、录音室专辑。"),
    ("songs_removed_by_filter3_album_type.json", "补充分支 filter3 中因专辑类型不在规则内而移除的歌曲行。"),
    ("songs_after_filter4_dedupe.json", "补充分支 filter4 后的去重保留行；规则与高可信分支一致。"),
    ("songs_removed_by_filter4_dedupe.json", "补充分支 filter4 中因重复 mid/id、缺失 mid/id 或同 name 优先级被移除的歌曲。"),
    ("songs_after_filter5_high_confidence_name_exclusion.json", "补充分支 filter5 后的保留行。"),
    ("songs_removed_by_filter5_high_confidence_name_exclusion.json", "补充分支 filter5 中因命中高可信歌名而移除的歌曲行。"),
    ("filter1_filter2_filter3_summary.json", "补充分支多步过滤的规则、计数和输出位置摘要。"),
    ("*.csv", "JSON 的人工查看版本，只应位于 data/processed/validation/.../csv_views/。"),
    ("page_*.json", "原始分页接口响应缓存，具体接口由父目录说明。"),
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def count_dirs(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_dir()) if path.exists() else 0


def count_files(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file()) if path.exists() else 0


def extension_counts(root: Path) -> list[str]:
    counts: Counter[str] = Counter()
    for file in root.rglob("*"):
        if file.is_file():
            counts[file.suffix or "无扩展名"] += 1
    return [f"- `{ext}`：{count} 个" for ext, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))]


def direct_file_summary(path: Path) -> str:
    files = [item for item in path.iterdir() if item.is_file()]
    if not files:
        return ""
    counts = Counter(file.suffix or "无扩展名" for file in files)
    parts = [f"{count} 个 {ext}" for ext, count in sorted(counts.items())]
    return "（本级文件：" + "，".join(parts) + "）"


def directory_tree(path: Path, prefix: str = "") -> list[str]:
    dirs = sorted([item for item in path.iterdir() if item.is_dir()], key=lambda item: item.name.casefold())
    lines: list[str] = []
    for index, directory in enumerate(dirs):
        is_last = index == len(dirs) - 1
        branch = "`-- " if is_last else "|-- "
        summary = direct_file_summary(directory)
        lines.append(f"{prefix}{branch}{directory.name}/ {summary}".rstrip())
        extension = "    " if is_last else "|   "
        lines.extend(directory_tree(directory, prefix + extension))
    return lines


def csv_location_counts() -> tuple[int, int]:
    csv_files = list(DATA.rglob("*.csv"))
    outside_validation = [file for file in csv_files if "data/processed/validation/" not in rel(file)]
    return len(csv_files), len(outside_validation)


def write_report() -> None:
    total_csv, outside_validation_csv = csv_location_counts()
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        "# data 目录结构说明",
        "",
        f"生成时间：{datetime.now().isoformat(timespec='seconds')}",
        "",
        "## 范围和总数",
        "",
        f"- 根目录：`{rel(DATA)}/`",
        f"- `data` 下共有 {count_dirs(DATA)} 个子目录、{count_files(DATA)} 个文件。",
        f"- CSV 总数：{total_csv} 个；其中位于 `data/processed/validation/` 之外的 CSV：{outside_validation_csv} 个。",
        "- 当前 `data/processed/` 只保留验证数据；四位歌手样本 JSON 和 CSV 均在 `data/processed/validation/four_singers/` 下。",
        f"- 旧流程归档：`{rel(ARCHIVE)}/`，包含 {count_dirs(ARCHIVE)} 个子目录、{count_files(ARCHIVE)} 个文件。",
        "",
        "## 顶层目录",
        "",
    ]

    for child in sorted([item for item in DATA.iterdir() if item.is_dir()], key=lambda item: item.name.casefold()):
        lines.append(f"- `{rel(child)}/`：{count_dirs(child)} 个子目录，{count_files(child)} 个文件")

    lines.extend(["", "## 文件类型统计", ""])
    lines.extend(extension_counts(DATA))

    lines.extend(["", "## 主要目录用途", ""])
    for path, description in MAJOR_PATHS:
        lines.append(f"- `{path}`：{description}")

    lines.extend(["", "## 旧流程归档内容", ""])
    for path in LEGACY_PATHS:
        target = ROOT / path
        lines.append(f"- `{path}`：{count_dirs(target)} 个子目录，{count_files(target)} 个文件。")

    lines.extend(["", "## 常见文件名和模式含义", ""])
    for pattern, description in FILE_PATTERNS:
        lines.append(f"- `{pattern}`：{description}")

    lines.extend(
        [
            "",
            "## 目录树（目录级别，不列出每个叶子文件）",
            "",
            "说明：每个目录后括号中的文件统计只表示该目录本级直接包含的文件，不含子目录。",
            "",
            "```text",
            "data/",
        ]
    )
    lines.extend(directory_tree(DATA))
    lines.append("```")
    lines.append("")

    text = "\n".join(lines)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")
    REPORT.write_text(text, encoding="utf-8", newline="")


if __name__ == "__main__":
    write_report()
