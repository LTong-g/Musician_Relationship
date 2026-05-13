# Musician Relationship

音乐人合作关系图谱的本地元数据采集与清洗工具。当前阶段聚焦 QQ 音乐非官方接口，先建立歌手身份表，再通过歌手主页歌曲 Tab 采集单个歌手歌曲，过滤明显非原版条目，并补全作词、作曲等制作人员信息；后续可用专辑详情做归属验证。

本项目用于个人技术研究和元数据关系分析，不提供音乐播放、下载或绕过平台限制的能力；不保证第三方接口稳定、完整或准确。

## 目录结构

```text
music_metadata_graph/
  pipelines/
    collect_hot_singer_registry.py   # 采集热门歌手身份 registry
    collect_high_confidence_singer_songs.py  # 通过歌手专辑列表生成高可信歌曲子集
data/
  raw/                               # 本地原始缓存，不提交
  processed/                         # 本地处理结果，不提交
archive/
  legacy_pipeline_2026-05-12/        # 已剥离的旧流程数据、旧流程代码和旧网页，不参与当前正式流程
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

### 2. 采集高可信歌曲子集

```powershell
python -m music_metadata_graph.pipelines.collect_high_confidence_singer_songs
```

正式流程前置条件是先完成第 1 步歌手身份表采集。默认读取：

```text
data/processed/singer_registry/qqmusic_hot/singer_registry.json
```

也就是对歌手身份表中的全部歌手逐个执行专辑子集采集；当前周杰伦、薛之谦、林俊杰、汪苏泷四位歌手只是流程验证样本，不是正式流程边界。

每个歌手的具体步骤：

1. 请求 `client.singer.get_album_list(mid)`，取得该歌手专辑列表。
2. 只保留 `albumType` 为 `Single`、`EP`、`录音室专辑` 的专辑。
3. 对保留专辑逐个请求 `client.album.get_song(albumMid)`。
4. 只保留歌曲 `singer[].mid` 中包含目标歌手 `mid` 的歌曲。
5. 先按歌曲 `mid` 优先、其次 `id` 去重；再只按歌曲原始 `name` 去重，不使用 `title` 或歌手键。同 `name` 不同专辑类型时，按 `录音室专辑`、`EP`、`Single` 的顺序保留；如果同 `name` 且同专辑类型仍有多条，保留数值 `id` 更小的歌曲。
6. 输出 JSON 作为正式产物。

默认输出：

```text
data/processed/high_confidence_singer_songs/
```

正式产物目录只保留 JSON，包括每个歌手自己的 `albums_all.json`、`songs_all.json`、`songs_after_filter1_target_singer_match.json`、`songs_removed_by_filter1_target_singer_match.json`、`songs_after_filter2_dedupe.json`、`songs_removed_by_filter2_dedupe.json`，以及 `albums_included.json`、`albums_excluded.json` 和 `summary.json`。其中 `songs_all.json` 是已纳入专辑请求到的歌曲全集，不是过滤步骤；filter1 只保留歌曲歌手列表包含目标歌手 `mid` 的行；filter2 对 filter1 保留结果去重：先按歌曲 `mid/id` 去重，再只按原始 `name` 去重；同 `name` 候选按 `录音室专辑`、`EP`、`Single` 顺序保留，仍无法区分时保留数值 `id` 更小的歌曲。当前四位歌手样本只是验证数据，已放在 `data/processed/validation/four_singers/json_outputs/high_confidence_singer_songs/`，不放在正式目录；验证输出不再生成跨歌手合并表。

CSV 只是人工查看版本，不属于正式数据流程默认产物；需要时显式加，并写入验证目录：

```powershell
python -m music_metadata_graph.pipelines.collect_high_confidence_singer_songs --write-csv
```

默认 CSV 视图输出到：

```text
data/processed/validation/csv_views/high_confidence_singer_songs/
```

调试四位样本歌手时显式加：

```powershell
python -m music_metadata_graph.pipelines.collect_high_confidence_singer_songs --test-four-singers --write-csv
```

如果需要为特定验证批次生成 CSV，使用 `--csv-output-dir` 指向对应的 `data/processed/validation/.../csv_views/...` 目录，不要把 CSV 写回正式流程目录。例如四位样本歌手当前使用 `data/processed/validation/four_singers/csv_views/high_confidence_singer_songs/`。

CSV 内容由同一批 JSON 行转换而来，嵌套字段会序列化为 JSON 字符串，列名只使用接口原始顶层键或 `aux_` 辅助键。

当前四位样本歌手的补充分支位于：

```text
data/processed/validation/four_singers/json_outputs/supplement_singer_songs/
```

其中 `songs_all.json` 是补充候选集合。补充分支当前顺序为：filter1 过滤空专辑；filter2 移除专辑 `id/mid` 为空的行；随后请求并补充专辑详情；filter3 只保留专辑类型为 `Single`、`EP`、`录音室专辑` 的行；filter4 去重，规则与高可信分支一致，先按歌曲 `mid/id` 去重，再只按原始 `name` 去重，同 `name` 候选按 `录音室专辑`、`EP`、`Single` 顺序保留，仍无法区分时保留数值 `id` 更小的歌曲；filter5 减去高可信子集已有歌名。验证阶段每一步过滤都要同时输出留下和过滤掉的行，并写明 `aux_filter_reason`。对应 CSV 查看版本位于：

```text
data/processed/validation/four_singers/csv_views/supplement_singer_songs/
```

专辑详情缓存写入 `data/raw/qqmusic/supplement_album_details/`；补充分支最终结果输出为 `songs_after_filter5_high_confidence_name_exclusion.json` 和 `songs_removed_by_filter5_high_confidence_name_exclusion.json`，对应 CSV 查看版本也位于同一验证目录。

当前高可信子集流程只生成更可靠的歌曲候选入口，尚未接入制作人员补全、关系边生成和网页导出。

## 旧流程归档

旧端到端流程代码、旧网页、旧数据产物和旧原始缓存已从当前正式目录剥离，统一放在：

```text
archive/legacy_pipeline_2026-05-12/
```

归档内容包括旧的 `collect_singer_songs.py`、`validate_album_ownership.py`、`write_singer_pipeline_report.py`、`export_web_dataset.py`、`web/` 目录、旧 `data/processed/singer_songs/`、旧制作人员缓存和旧专辑探查缓存。当前正式流程不再从这些目录读取，也不再向这些目录写入。

## 数据边界

- `data/raw/` 和 `data/processed/` 是本地数据目录，默认不提交。
- 不提交 cookie、token、账号态、代理配置、数据库、大量图片或抓取缓存。
- 如需提交样例数据，应单独制作小规模脱敏样例。
