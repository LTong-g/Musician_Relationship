# Musician Relationship

音乐人合作关系图谱的本地元数据采集与清洗工具。当前阶段聚焦 QQ 音乐非官方接口，先建立歌手身份表，再采集单个歌手歌曲，过滤明显非原版条目，并用专辑详情做归属验证。

本项目用于个人技术研究和元数据关系分析，不提供音乐播放、下载或绕过平台限制的能力；不保证第三方接口稳定、完整或准确。

## 目录结构

```text
musician_relationship/
  pipelines/
    collect_hot_singer_registry.py   # 采集热门歌手身份 registry
    collect_singer_songs.py          # 采集单个歌手全量歌曲并初过滤
    validate_album_ownership.py      # 用专辑详情验证歌曲归属
    write_singer_pipeline_report.py  # 生成 pipeline 检查报告
data/
  raw/                               # 本地原始缓存，不提交
  processed/                         # 本地处理结果，不提交
```

## Pipeline

### 1. 采集热门歌手身份表

```powershell
python -m musician_relationship.pipelines.collect_hot_singer_registry
```

默认输出：

```text
data/processed/singer_registry/qqmusic_hot/
```

其中 `singer_registry.json/csv` 用作歌手身份表；`hot_singer_discovery_snapshot.json` 记录本次热门榜发现快照。`mid` 是优先身份键，歌手名、头像和榜单排名都视为快照字段。

### 2. 采集单个歌手歌曲

```powershell
python -m musician_relationship.pipelines.collect_singer_songs `
  --target-singer-mid 001BLpXF2DyJe2 `
  --target-singer-name "\u6797\u4fca\u6770" `
  --processed-dir data/processed/singer_songs/linjunjie
```

初过滤顺序：

1. `name_title_mismatch`：`name` 与 `title` 规范化后不一致，认为不是原版候选。
2. `empty_album`：专辑为空。
3. `title_version_keyword:*`：标题命中 live、demo、remix、伴奏等版本词。

输出包括 `songs_all.json`、`songs_filtered.json`、`songs_kept.json` 及 CSV。

### 3. 专辑归属验证

```powershell
python -m musician_relationship.pipelines.validate_album_ownership `
  --input data/processed/singer_songs/linjunjie/songs_kept.json `
  --output-dir data/processed/album_validated/linjunjie `
  --target-mid 001BLpXF2DyJe2 `
  --target-name "\u6797\u4fca\u6770"
```

该步骤请求并缓存专辑详情，输出：

```text
songs_kept_album_validated.json
songs_rejected_album_validated.json
songs_review_album_validated.json
album_validation_snapshot.json
```

专辑歌手不含目标歌手时，不直接一刀切删除。强噪声自动 rejected；原声带、合辑、合作曲等边界项进入 review。

### 4. 生成检查报告

```powershell
python -m musician_relationship.pipelines.write_singer_pipeline_report `
  --singer-name "\u6797\u4fca\u6770" `
  --initial-dir data/processed/singer_songs/linjunjie `
  --validated-dir data/processed/album_validated/linjunjie `
  --output-dir data/processed/reports/singer_pipeline/linjunjie
```

报告按拼音/英文混排，并包含排序键：

```text
00_summary.md
01_initial_filtered.md
02_initial_kept.md
03_album_review.md
04_album_rejected.md
05_final_kept.md
```

## 数据边界

- `data/raw/` 和 `data/processed/` 是本地数据目录，默认不提交。
- 不提交 cookie、token、账号态、代理配置、数据库、大量图片或抓取缓存。
- 如需提交样例数据，应单独制作小规模脱敏样例。
