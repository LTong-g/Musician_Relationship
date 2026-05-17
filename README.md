# Musician Relationship

Musician Relationship 是一个本地运行的音乐人合作关系图谱工具。它围绕歌曲、音乐人和职能关系整理 QQ 音乐中的公开元数据，把“谁演唱了哪些歌”“谁给谁作词或作曲”“哪些音乐人之间有共同作品”转换成可以查询、筛选和浏览的关系网络。

这个项目面向个人技术研究、学习和本地分析，不提供音乐播放、下载或绕过平台限制的能力，也不承诺第三方接口长期稳定、完整或准确。

## 你可以用它做什么

- 从 QQ 音乐公开元数据中整理音乐人、歌曲、专辑、演唱、作词和作曲关系。
- 在本地生成可直接打开的静态网页图谱。
- 用头像节点查看音乐人之间的合作网络，头像不可用时自动显示姓名占位。
- 按目标歌手粉丝量、目标歌手、最小合作歌曲数筛选图谱。
- 搜索音乐人，点击节点或边查看支撑歌曲和关系明细。
- 在“作词/作曲分开”和“合并显示”之间切换，观察不同关系粒度。
- 查看输入/输出关系：别人给某位歌手作词作曲，或某位音乐人给别人作词作曲。

## 适合和不适合的使用场景

适合：

- 研究华语音乐人之间的演唱、作词、作曲合作关系。
- 做本地数据处理、图谱分析和可视化实验。
- 为个人项目或学习记录生成可打开的静态图谱页面。

不适合：

- 音乐播放、下载、试听或资源获取。
- 大规模、高频率、商业化数据抓取。
- 依赖第三方非官方接口构建稳定线上服务。
- 保存或提交 cookie、token、账号态、音频文件、大量头像缓存或大量原始抓取数据。

## 快速开始

项目使用 Python 3.12。以下命令默认你已经进入项目根目录，并且当前 `python` 指向项目环境。

安装项目依赖：

```powershell
python -m pip install -e .
```

运行完整本地流程：

```powershell
python -m music_metadata_graph.pipelines.run_full_pipeline
```

如果只想跑较小的 MVP 数据集：

```powershell
python -m music_metadata_graph.pipelines.run_full_pipeline --mvp
```

完整流程会依次完成元数据采集、原始响应缓存、SQLite 入库、歌曲过滤、作词作曲关系整理、头像缓存和网页生成。脚本会在关键节点做检查；如果发现必要 raw、CSV、SQLite 表、关系约束或网页资源缺失，会停止并提示问题。

## 打开图谱

生成完成后，用浏览器打开对应页面：

- `site/index.html`：完整标准图谱。
- `site_mvp/index.html`：MVP 图谱。
- `site_demo/index.html`：演示图谱。
- `site_large/index.html`：适合更大图谱的 large-graph 页面。

标准图谱顶部有两排控制区：第一排是显示开关，第二排是粉丝量筛选、目标歌手选择、最小歌曲数和搜索框。粉丝量筛选支持拖动双滑块，也支持直接输入普通数字、`500万` 这类简写或上限 `不限`。

图谱交互：

- 点击节点查看音乐人详情和相关歌曲。
- 按住 Ctrl 点击节点可以多选。
- 点击边查看两位音乐人之间的合作歌曲。
- 搜索框按 Enter 执行，只在当前图中找到音乐人时更新选中状态。
- 点击图谱空白处取消选中。
- “隐藏叶节点”会隐藏当前图中只连接另一个唯一节点的节点。
- “仅显示目标歌手”会隐藏扩展制作人或邻接音乐人，只保留目标歌手之间的关系。

选中单个歌手时，详情栏提供“全部 / 输入 / 输出”视图。“输入”表示别人给选中歌手作词或作曲，“输出”表示选中歌手给别人作词或作曲。选中多名歌手时，详情栏提供“交集 / 并集”关系模式，用于查看选中节点之间的关系或所有相关关系。

## 常用命令

重新准备网页资源和头像缓存：

```powershell
python -m music_metadata_graph.pipelines.prepare_static_graph_assets
```

重新生成标准图谱网页：

```powershell
python -m music_metadata_graph.pipelines.build_static_graph
```

重新生成 large-graph 网页：

```powershell
python -m music_metadata_graph.pipelines.build_large_graph_static
```

如果已经有部分歌手主页歌曲 raw 数据，并希望从歌曲数据继续后续流程：

```powershell
python -m music_metadata_graph.pipelines.run_from_song_tabs
```

## 输出内容

主要本地输出：

- `data/raw/`：接口原始响应缓存，用作可追溯证据。
- `data/music_metadata_graph.sqlite3`：完整流程的结构化 SQLite 数据库。
- `data/music_metadata_graph_mvp.sqlite3`：MVP 流程的结构化 SQLite 数据库。
- `data/processed/validation/`：过滤、拒绝和人工检查用 CSV。
- `site/`、`site_mvp/`、`site_demo/`、`site_large/`：生成后的静态网页。
- `site_assets/avatars/`：共享头像缓存。
- `logs/runs/`：每次正式脚本运行的日志。

这些运行产物默认不应提交到 Git。仓库主要保存源码、文档、测试、少量脱敏样例和配置。

## 数据口径

当前关系图谱以 QQ 音乐元数据为主，音乐人身份优先使用 QQ 音乐 singer mid。歌曲关系主要围绕三类职能：

- 演唱：歌曲的演唱者。
- 作词：歌曲制作人信息中的作词人员。
- 作曲：歌曲制作人信息中的作曲人员。

图谱中的方向口径是“作词/作曲人 -> 演唱者”。同一音乐人给自己作词或作曲的自我边不会进入图谱。

## 项目结构

```text
music_metadata_graph/     核心源码和 pipeline 入口
tests/                    单元测试
docs/                     补充文档和字段字典
site*/                    生成后的静态图谱页面
site_assets/              共享网页资源和头像缓存
data/                     本地 raw、SQLite 和 validation 产物
logs/                     本地运行日志
archive/                  历史流程和旧产物归档
```

## 注意事项

- 本项目只采集关系图谱研究需要的元数据，不采集音频文件。
- 请低频、克制地运行采集流程，避免对第三方接口造成不必要压力。
- 不要把 cookie、token、账号信息、代理配置或其他凭据写入仓库。
- 不要把大量原始 JSON、数据库文件、头像缓存或生成图谱提交到仓库。
- 第三方非官方接口可能变更、限流或返回缺失字段；图谱结果应作为研究材料，而不是权威数据源。
