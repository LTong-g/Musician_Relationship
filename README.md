# Musician Relationship

音乐人合作关系图谱的本地元数据采集与清洗工具。当前阶段聚焦 QQ 音乐非官方接口，先建立歌手身份表，再采集单个歌手歌曲，过滤明显非原版条目，并补全作词、作曲等制作人员信息；后续可用专辑详情做归属验证。

本项目用于个人技术研究和元数据关系分析，不提供音乐播放、下载或绕过平台限制的能力；不保证第三方接口稳定、完整或准确。

## 目录结构

```text
music_metadata_graph/
  pipelines/
    collect_hot_singer_registry.py   # 采集热门歌手身份 registry
    collect_singer_songs.py          # 采集单个歌手全量歌曲、初过滤并补全制作人员
    validate_album_ownership.py      # 用专辑详情验证歌曲归属
    write_singer_pipeline_report.py  # 生成 pipeline 检查报告
    export_web_dataset.py            # 导出静态网页数据
web/
  index.html                         # 静态图谱工作台
  data/                              # 可提交的静态可视化数据
data/
  raw/                               # 本地原始缓存，不提交
  processed/                         # 本地处理结果，不提交
```

## Pipeline

### 1. 采集热门歌手身份表

```powershell
python -m music_metadata_graph.pipelines.collect_hot_singer_registry
```

默认输出：

```text
data/processed/singer_registry/qqmusic_hot/
```

其中 `singer_registry.json/csv` 用作歌手身份表；`hot_singer_discovery_snapshot.json` 记录本次热门榜发现快照。`mid` 是优先身份键，歌手名、头像和榜单排名都视为快照字段。

### 2. 采集单个歌手歌曲

```powershell
python -m music_metadata_graph.pipelines.collect_singer_songs `
  --target-singer-mid 001BLpXF2DyJe2 `
  --target-singer-name "\u6797\u4fca\u6770" `
  --processed-dir data/processed/singer_songs/linjunjie
```

初过滤顺序：

1. `name_title_mismatch`：`name` 与 `title` 规范化后不一致，认为不是原版候选。
2. `empty_album`：专辑为空。
3. `title_version_keyword:*`：标题命中 live、demo、remix、伴奏等版本词。

默认会对初过滤并去重后的 `songs_kept` 请求 QQ 音乐歌曲制作人员接口，并在每首歌的 `credits` 中写入：

- `groups`：按 QQ 音乐返回的“演唱、作词、作曲、编曲、制作人”等分组保存完整人员列表。
- `lyricists`、`composers`、`arrangers`、`producers`：常用职能的姓名展开字段，CSV 中也会同步写出。
- `status`：`ok` 表示成功取得制作人员列表；`missing_producer_list` 表示上游响应没有制作人员列表；`failed` 表示请求或解析异常。

制作人员补全开启时，`songs_kept` 默认只保留作词和作曲都非空的歌曲，作为后续图谱和可视化可直接消费的数据。缺作词或缺作曲的条目会写入 `songs_credit_incomplete.json/csv`，并带 `credit_filter_reason`；如果调试时需要保留这些条目，可加 `--keep-incomplete-credits`。

调试时可用 `--max-producer-songs` 限制制作人员请求数量；如果只想生成歌曲列表，可加 `--skip-producers`。

输出包括 `songs_all.json`、`songs_filtered.json`、`songs_kept.json`、`songs_credit_incomplete.json`、`singer_song_snapshot.json` 及对应 CSV。

### 3. 专辑归属验证

```powershell
python -m music_metadata_graph.pipelines.validate_album_ownership `
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
python -m music_metadata_graph.pipelines.write_singer_pipeline_report `
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

### 5. 导出静态网页数据

```powershell
python -m music_metadata_graph.pipelines.export_web_dataset
```

默认读取：

```text
data/processed/singer_songs/zhoujielun/
data/processed/singer_songs/xuezhiqian/
data/processed/singer_songs/linjunjie/
```

并输出到：

```text
web/data/catalog.json
web/data/zhoujielun.json
web/data/xuezhiqian.json
web/data/linjunjie.json
```

打开 `web/index.html` 可查看静态图谱工作台。网页中的“数据集”指 QQ 音乐元数据集；周杰伦、薛之谦、林俊杰等是当前数据集下的目标歌手覆盖范围，可以单独筛选或合并查看。网页支持不完整数据；即使当前视图没有边，也会保留孤立节点显示。

## 数据边界

- `data/raw/` 和 `data/processed/` 是本地数据目录，默认不提交。
- 不提交 cookie、token、账号态、代理配置、数据库、大量图片或抓取缓存。
- 如需提交样例数据，应单独制作小规模脱敏样例。
