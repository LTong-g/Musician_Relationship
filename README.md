# Musician Relationship
音乐人合作关系图谱的本地元数据采集、标准化、图谱分析和可视化工具。

## 标准可视化
标准图谱生成脚本是通用入口：默认读取完整数据库 `data/music_metadata_graph.sqlite3` 并输出 `site/index.html`，完整库页面默认包含数据库中全部可视化关系，不再把目标歌手限制为前 10 位；传入 `--mvp` 时读取 MVP 数据库 `data/music_metadata_graph_mvp.sqlite3` 并输出 `site_mvp/index.html`；传入 `--demo` 时读取完整数据库并输出 `site_demo/index.html`，目标歌手从 MVP 的 10 位种子歌手出发，同时纳入这 10 位歌手作为演唱者、作词人或作曲人参与的全部关系边及相连音乐人节点。生成 HTML 前先准备网站资源，图谱数据写入各站点自己的 `assets/graph-data.js`，force-graph 运行库写入各站点自己的 `assets/vendor/force-graph.min.js`；头像下载到共享目录 `site_assets/avatars/`，并通过 `site_assets/avatar-manifest.json` 记录结果，避免 `site/`、`site_mvp/` 和 `site_demo/` 重复下载同一头像。头像准备时每个头像 URL 都会打印一行 `[当前/总数]` 进度，状态包括 `cache_hit`、`downloaded`、`failed` 和 `skipped`；未缓存头像按音乐人的 `演唱 + 作词 + 作曲` 关联数量从高到低排序，默认按 1 秒间隔启动下载请求，下载耗时不阻塞后续请求启动；这些输出会同步写入 `logs/runs/prepare_static_graph_assets_*.log`。

```powershell
D:\ASoftware\anaconda3\envs\Musician_Relationship\python.exe -m music_metadata_graph.pipelines.prepare_static_graph_assets
```

```powershell
D:\ASoftware\anaconda3\envs\Musician_Relationship\python.exe -m music_metadata_graph.pipelines.build_static_graph
```

```powershell
D:\ASoftware\anaconda3\envs\Musician_Relationship\python.exe -m music_metadata_graph.pipelines.prepare_static_graph_assets --mvp
```

```powershell
D:\ASoftware\anaconda3\envs\Musician_Relationship\python.exe -m music_metadata_graph.pipelines.build_static_graph --mvp
```

```powershell
D:\ASoftware\anaconda3\envs\Musician_Relationship\python.exe -m music_metadata_graph.pipelines.prepare_static_graph_assets --demo
```

```powershell
D:\ASoftware\anaconda3\envs\Musician_Relationship\python.exe -m music_metadata_graph.pipelines.build_static_graph --demo
```

生成页面可直接用浏览器打开，顶部控制区分为两列两行：左侧标题和数据库说明跨两行，右侧第一排只放图谱显示开关，右侧第二排放粉丝量筛选、目标歌手下拉、最小歌曲数和搜索框。页面支持用两个滑块筛选目标歌手粉丝量范围，也支持直接编辑轨道左右两端的下限和上限输入框，输入框可填写普通数字、`500万` 这类简写或上限 `不限`，默认范围为 500 万以上；目标歌手下拉菜单只显示当前粉丝量范围内的目标歌手，候选项按粉丝量从高到低排列，菜单项文本只显示歌手名。粉丝量范围变化不会清除范围外目标歌手的既有勾选，范围调回后会恢复此前勾选状态。页面还支持勾选目标歌手、按音乐人搜索并选中、按最小歌曲数筛选、用开关控制作词作曲分开或合并显示、切换头像节点或名字节点、切换粒子效果、隐藏只连接另一个唯一节点的叶节点、仅显示当前目标歌手节点，并可点击节点或边查看支撑歌曲和高亮相邻关系；显示名字时基础文字透明度按节点权重映射，默认范围为 0.5 到 1，选中或高亮节点文字直接不透明，未高亮节点在淡化状态下继续按淡化系数降低。普通点击节点为单选，按住 Ctrl 点击节点可多选。顶部搜索框按 Enter 执行，只在当前图中找到音乐人时选中并高亮节点；命中多个音乐人时会全部选中，没搜到时保留当前选中状态。点击高亮只更新选中状态和详情栏，不重新聚焦或重跑图布局；左键点击图谱空白处取消选中，右键点击图谱区域任意位置取消选中。选中歌手时，详情栏会显示“视图”下拉菜单，默认“全部”；“输入”仅显示别人给选中歌手作词/作曲的关系，“输出”仅显示选中歌手给别人作词/作曲的关系；选中两名及以上歌手时，详情栏还会显示“边关系”下拉菜单，默认“交集”，可切换到“并集”以高亮所有选中节点的相关边及相连节点。“仅显示目标歌手”默认关闭，开启后不显示扩展制作人或邻接音乐人节点，只保留两端都是当前目标歌手的关系边，并显示全部当前目标歌手节点，孤立目标歌手也会保留。完整数据库的标准完整图默认关闭“作词/作曲分开”、默认开启“隐藏叶节点”并禁用节点拖动；MVP、demo 和 large-graph 页面默认开启“作词/作曲分开”并关闭“隐藏叶节点”；large-graph 页面中的“显示名字”和“粒子效果”开关置灰且不可交互。
关系口径为“作词/作曲人 -> 演唱者”，图谱按两位音乐人和职能合并线条，避免互相作词作曲时显示 4 条边；悬浮边、右侧边详情和粒子方向会按真实方向拆出 `A -> B` 与 `B -> A`。图谱永远排除同一音乐人自己给自己作词或作曲的自我边。节点优先使用本地缓存头像；头像未缓存或下载失败时，页面会显示姓名首字占位，不再回退请求远程头像 URL。生成的 HTML 位于 `site/`、`site_mvp/` 或 `site_demo/`；SQLite 数据库、raw 缓存和 validation 产物仍位于 `data/`，默认不提交 Git。
完整流程 `python -m music_metadata_graph.pipelines.run_full_pipeline` 现在会在过滤步骤之后继续生成网页：第 17 步准备标准网站资源和头像缓存，第 18 步生成标准图谱，标准图谱输出到 `site/index.html`，MVP 模式输出到 `site_mvp/index.html`；第 19 步生成 large-graph 图谱，始终默认使用完整数据库并输出到 `site_large/index.html`。
如果只想替换绘图区为 force-graph 官方 large-graph 示例风格，可以生成独立页面：

```powershell
D:\ASoftware\anaconda3\envs\Musician_Relationship\python.exe -m music_metadata_graph.pipelines.build_large_graph_static
```

默认使用完整数据库 `data/music_metadata_graph.sqlite3`，输出为 `site_large/index.html`。该页面保留标准页面外壳、目标歌手粉丝量范围筛选、目标歌手筛选、搜索、最小歌曲数、作词/作曲合并、隐藏叶节点开关、详情栏和明细表；只有绘图区按 force-graph 官方 `example/large-graph` 的绘图配置生成：设置 `window.devicePixelRatio = 1`，并使用 `.d3AlphaDecay(0)`、`.d3VelocityDecay(0.08)`、`.cooldownTime(60000)`、`.linkColor(() => 'rgba(0,0,0,0.05)')` 和 `.zoom(0.05)`；保留鼠标缩放、平移、点击节点、点击边、左键点击空白处取消选中和右键点击图谱区域任意位置取消选中，即 `.enablePointerInteraction(true)`，但禁用节点拖动，即 `.enableNodeDrag(false)`。绘图区不使用标准图谱的头像节点、自定义节点绘制、粒子、高亮线宽、自定义力参数或自动聚焦，因此“显示名字”和“粒子效果”开关在 large-graph 页面置灰且不可交互，隐藏叶节点默认关闭。
本项目用于个人技术研究和元数据关系分析，不提供音乐播放、下载或绕过平台限制的能力；不保证第三方接口稳定、完整或准确。

## 当前状态
当前仓库处于请求顺序与存储结构重新设计阶段。旧的端到端流程、旧 raw 数据、旧 processed 产物和旧网页都已归档，不再作为当前正式流程运行入口。
当前已确认的顺序是：
1. 请求 QQ 音乐完整歌手列表 raw JSON。
2. 将歌手列表导入 SQLite 的 `artists` 表。
3. 请求歌手主页歌曲 Tab raw JSON。
4. 验证歌曲 `singer[].mid` 是否存在于 `artists` 表；缺失时请求歌手信息并补入库。
5. 从歌曲 raw JSON 的 `album.mid` 或非 0 `album.id` 去重后，请求专辑详情 raw JSON。
6. 将专辑详情中的核心专辑字段导入 SQLite 的 `albums` 表。
7. 将满足完备约束的歌曲导入 SQLite，并把入库失败歌曲写入拒绝 CSV。
8. 从已入库歌曲中只保留专辑类型为 `Single`、`EP`、`录音室专辑` 的歌曲，并把被过滤歌曲写入正式 CSV。
9. 对步骤八后歌曲请求 `song.get_producer` 制作人 raw JSON；开发阶段可先限定为歌曲歌手包含周杰伦的歌曲。
10. 将作词、作曲制作人写入 `song_credit_artists`，并把缺失的制作人补入 `artists`。
11. 删除作词或作曲不完整的歌曲，确保后续可视化歌曲至少有 1 个作词和 1 个作曲，并把被过滤歌曲写入正式 CSV。
12. 从剩余歌曲中按“规范化歌名 + 同作词 + 同作曲”去重，优先级为 `录音室专辑 > EP > Single > 较小 song id`，并把被过滤歌曲写入正式 CSV。
13. 从剩余歌曲中筛除 `language = 9` 的歌曲，把删除歌曲写入正式 CSV，并临时导出过滤后的保留歌曲 CSV。
一键完整流程入口：

```powershell
python -m music_metadata_graph.pipelines.run_full_pipeline
```

该入口按当前正式顺序调用各步骤，并在每一步前后做安全检查；检查包括必要 raw/CSV/SQLite 是否存在、关键表是否有行、步骤二粉丝量 raw 是否存在、步骤三 `artists` 是否写入可用粉丝量、步骤四目标歌手是否都有歌曲 Tab raw、步骤六后歌曲 Tab 中非空歌手 MID 是否都已进入 `artists`、步骤九后是否只剩允许专辑类型、步骤十一后每首保留歌曲是否都有制作人 raw、步骤十三后作词/作曲关系是否存在、步骤十四后是否仍有缺作词或作曲的歌曲、步骤十五后歌曲 `mid/id` 是否仍唯一、步骤十六后是否仍有 `language=9` 歌曲。任一检查失败会立即停止，不会默认上一脚本已经正确跑完。
各 pipeline 入口的默认 SQLite 路径统一由 `music_metadata_graph/pipelines/defaults.py` 中的 `DEFAULT_DB_PATH` 提供；手动运行时仍可通过 `--db` 覆盖。
MVP 一键流程使用共享 raw 数据，不另建 raw 目录；默认数据库为 `data/music_metadata_graph_mvp.sqlite3`，validation 产物写入 `data/processed/validation_mvp/`。MVP 模式下第一步只确保歌手列表第一页 raw 存在，第二步只确保前 10 个 `area_id in (0, 1)` 歌手的粉丝量 raw 可用，第三步只导入满足 `area_id in (0, 1)` 且有可用正数粉丝量的前 10 个歌手，后续流程逻辑不变：

```powershell
python -m music_metadata_graph.pipelines.run_full_pipeline --mvp
```

可以用 `--continue-from N` 和 `--stop-after N` 从编排步骤中间继续或只跑到某一步；这里的编排步骤把粉丝量 raw、两个前置补 MID 步骤、网站资源准备和两个网页生成步骤也单独编号，因此一键入口显示的是 1 到 19 个编排步骤。可用 `--dry-run` 打印命令并运行当前已有产物检查，不执行真实采集或入库命令。
一键流程的第 7 个编排步骤“按歌曲请求专辑详情 raw JSON”默认传入 `--max-failed-fetches 10`，用于避免 10 万级长跑采集中极少数 QQ 音乐 CGI 业务错误反复卡死整条流程；失败 key、raw 路径和异常原因仍会写入专辑详情失败清单 JSON。超过 10 个失败仍会中断。
如果已经请求过步骤四 `--all`，并希望只根据当前已经落盘的步骤四目标歌手主页歌曲 Tab raw 继续后续测试流程，可使用：

```powershell
python -m music_metadata_graph.pipelines.run_from_song_tabs
```

该测试入口等价于完整编排的 `--continue-from 5`，也就是从“五前置：quick_search 补歌曲歌手缺 MID”开始。它仍会先检查步骤四 `--all` 目标范围内是否至少已有可处理的主页歌曲 Tab raw；不会要求步骤四目标歌手全部落盘。对应脚本入口为：

```powershell
mr-run-from-song-tabs
```

专辑不再先按歌手请求“歌手专辑列表”。旧歌手专辑列表 raw、旧专辑表导出和旧专辑入库实现已归档；当前专辑表只从“歌曲 -> 专辑详情”的 `basicInfo` 中抽取核心字段，不导入专辑署名歌手信息。

## 运行日志
所有正式脚本入口会自动保留本次运行输出。运行时终端会先打印日志路径，例如：

```text
run_log=logs/runs/collect_singer_list_raw_20260515_140638.log
```

日志文件保存在 `logs/runs/`，按 `脚本名_YYYYMMDD_HHMMSS.log` 命名；终端仍照常显示输出，脚本异常时 traceback 也会写入同一个日志文件。`logs/` 默认不提交 Git。
日志文件写入采用后台线程队列：脚本主线程只负责把输出入队，后台日志线程负责写盘并 flush，避免频繁日志写盘占用请求循环时间。脚本会记录 `run_started_at`、`run_status` 和 `run_log_closing_at`；正常退出、异常退出和 Windows 控制台关闭/中断/系统关机事件触发时都会尽量 drain 队列并 flush 当前日志。Python fatal error 也会通过 `faulthandler` 写入线程栈。边界是：如果进程被操作系统直接强杀、机器断电或磁盘写入本身失败，最后极短时间内的输出仍无法绝对保证保存。
每次脚本启动时只生成一次 `run_id` 和 `run_log`。同一进程内后续脚本代码都复用这个日志上下文；如果某个脚本内部又调用了另一个已接入日志包装的入口，会在原日志中记录 `run_log_reused=...`，不会按新的实时时间再创建第二个日志文件。

## 字段字典
字段字典文件：

```text
docs/request_json_key_dictionary.xlsx
```

当前包含三个 sheet：
- `01_singer_list_index`：完整歌手列表请求 JSON 的顶层键、`singerlist[]` 字段、`tags` 筛选项字段、字段出现次数、示例值和中文释义。
- `02_song_album_detail`：从歌曲专辑字段派生请求的专辑详情 JSON 结构，包括 `basicInfo`、`company`、`singer.singerList[]` 等字段。
- `03_singer_song_tab`：歌手主页歌曲 Tab 请求 JSON 的顶层键、`SongTab` 字段、`SongTab.List[]` 歌曲字段、常见嵌套字段、字段出现次数、示例值和中文释义。
生成入口：

```powershell
python -m music_metadata_graph.tools.write_request_json_key_dictionary
```

## 步骤一：完整歌手列表 raw JSON
第一步准备 QQ 音乐完整歌手列表的原生 JSON，用于检查接口字段并支撑歌手表入库。
运行入口：

```powershell
python -m music_metadata_graph.pipelines.collect_singer_list_raw
```

默认输出：

```text
data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all/
```

可选筛选参数：

```powershell
python -m music_metadata_graph.pipelines.collect_singer_list_raw --area CHINA,TAIWAN --sex MALE,FEMALE --genre POP --index A,B
```

`--area`、`--sex`、`--genre`、`--index` 都接收列表形式，可以逗号分隔，也可以重复传参；不传时默认都是 `ALL`。脚本会对四类列表做组合并依次请求，输出目录按组合命名，例如：

```text
data/raw/qqmusic/singer_list_index/area_china_sex_male_genre_pop_index_a/
```

当前已请求完整分页：
- 页数：86。
- 歌手行数：6803。
- 接口 `total`：6803。
- 页大小：80。

## 步骤二：歌手粉丝量 raw JSON
第二步请求歌手近似粉丝量 raw。脚本先调用 `qqmusic.singer.get_singer_list`，默认只请求 `AreaType.TAIWAN` 和 `AreaType.CHINA` 两个地区，从 `concernNum` 快速覆盖当前入库目标；再扫描 `area_id in (0, 1)` 但未覆盖的歌手 MID，用 `qqmusic.singer.get_info` 的 `Info.FansNum.Num` 通过 `Client.gather()` 合包补齐。
两种字段已经按周杰伦样本复测为同一粉丝量口径，可合并为近似粉丝量使用。第二步仍保留 raw 来源：列表 raw 写入 `data/raw/qqmusic/singer_fans_list/`，单歌手补齐 raw 写入 `data/raw/qqmusic/singer_fans_info/`；正式汇总写入 `data/raw/qqmusic/singer_fans_summary.json`，MVP 汇总写入 `data/raw/qqmusic/singer_fans_summary_mvp.json`。重复运行时已有 JSON 不再重复请求，不追求实时更新。

```powershell
python -m music_metadata_graph.pipelines.collect_singer_fans_raw
```

命令入口：

```powershell
mr-collect-singer-fans-raw
```

## 步骤三：歌手列表入库
第三步读取第一步完整歌手列表 raw，并按运行模式合并第二步 summary：正式流程读取 `singer_fans_summary.json`，MVP 流程读取 `singer_fans_summary_mvp.json`。正式入库目标必须同时满足两个条件：`area_id` 明确为 `0` 或 `1`，并且 `fans_num` 是可用正数。粉丝量不可用的歌手不会作为第三步目标写入 `artists`，例如第二步 summary 中 `fans_num: null` 或 `0` 的行会被过滤掉。
`artists.fans_num` 使用可空 `INTEGER`。第三步导入的初始歌手必须写入正数粉丝量；后续歌曲歌手或制作人补入 `artists` 时，如果暂时没有粉丝量，则保留为空，且不会覆盖已有正数粉丝量。
当前 SQLite 数据库：

```text
data/music_metadata_graph.sqlite3
```

当前数据库保留五张正式表：`artists`、`albums`、`songs`、`song_singers`、`song_credit_artists`。
`artists` 字段：

```text
mid           TEXT NOT NULL PRIMARY KEY
name          TEXT NOT NULL
area_id       INTEGER
other_name    TEXT NOT NULL DEFAULT ''
icon          TEXT NOT NULL DEFAULT ''
spell         TEXT NOT NULL DEFAULT ''
raw_json_path TEXT NOT NULL DEFAULT ''
raw_page      INTEGER NOT NULL DEFAULT 0
raw_row_index INTEGER NOT NULL DEFAULT 0
```

导入入口：

```powershell
python -m music_metadata_graph.pipelines.import_singer_list_to_db
```

第三步从完整歌手列表 raw 入库前只保留 `area_id` 明确为 `0` 或 `1` 且第二步粉丝量汇总中有可用正数 `fans_num` 的歌手行，并把 `area_id` 和粉丝量追溯字段写入 `artists`。后续通过歌曲歌手或制作人补入的音乐人如果没有地区字段，则 `area_id` 保留为空。当前完整歌手列表 raw 共 6803 行，其中 `area_id` 为 `0` 或 `1` 的歌手行共 2119 行；按现有粉丝量 raw，2 个歌手没有可用粉丝量，第三步目标为 2117 行。
当前历史 `artists` 表曾包含 7266 行，其中旧完整歌手列表曾导入 6803 行，歌曲歌手补全后为 7134 行，制作人补入后为 7266 行；如果按当前第三步规则从头重建数据库，完整歌手列表初始导入行数应为满足 `area_id in (0, 1)` 且有可用正数粉丝量的歌手数，再由后续缺失歌手和制作人补入扩展。

## 步骤四：歌手主页歌曲 Tab raw JSON
`--all` 的目标范围不是当前 `artists` 全表，而是重新读取第一步使用的歌手列表 raw 目录，并套用第三步当前入库过滤规则得到的歌手集合。当前第三步规则是 `area_id in (0, 1)` 且有可用正数粉丝量，因此第四步默认只对满足该规则的歌手请求主页歌曲；后续由歌曲歌手、quick_search 或制作人补入 `artists` 的人员不会自动进入第四步请求范围。
如果第三步后续改了过滤规则，第四步会复用同一套过滤函数；如果第一步使用了非默认 raw 目录，第四步也需要传入相同的 `--singer-list-raw-dir`。
正式流程目标是对全部歌手请求主页歌曲接口，作为歌曲全量源数据。开发阶段先使用四位歌手验证请求结构：
- 周杰伦：`0025NhlN2yWrP4`
- 薛之谦：`002J4UUk29y8BY`
- 林俊杰：`001BLpXF2DyJe2`
- 汪苏泷：`001z2JmX09LLgL`
默认 raw 目录：

```text
data/raw/qqmusic/singer_homepage_song_tab/
```

当前四位歌手结果：
- 周杰伦：34 页，1012 行。
- 薛之谦：18 页，528 行。
- 林俊杰：34 页，1013 行。
- 汪苏泷：32 页，939 行。
- 合计：118 页，3492 行。
请求脚本：

```powershell
python -m music_metadata_graph.pipelines.collect_singer_song_tab_raw --name 周杰伦 --name 薛之谦 --name 林俊杰 --name 汪苏泷
```

部分请求支持两种输入：

```powershell
python -m music_metadata_graph.pipelines.collect_singer_song_tab_raw --mid 0025NhlN2yWrP4
python -m music_metadata_graph.pipelines.collect_singer_song_tab_raw --name 周杰伦
```

正式全量请求入口：

```powershell
python -m music_metadata_graph.pipelines.collect_singer_song_tab_raw --all

# 如果第二步导入使用了非默认歌手列表 raw 目录：
python -m music_metadata_graph.pipelines.collect_singer_song_tab_raw --all --singer-list-raw-dir data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all
```

部分请求会先检查每一个目标歌手是否存在于 SQLite 的 `artists` 表；只要任意一个目标不存在，就停止，不发起请求。

## 步骤五前置：quick_search 补歌曲歌手缺 MID
本步骤扫描步骤四目标范围内歌曲 raw 中 `SongTab.List[].singer[]` 里 `mid` 为空、`name` 非空的演唱歌手名。`--all` 的歌手目标范围与第四步一致：重新读取第一步使用的歌手列表 raw 目录，并套用第三步当前入库过滤规则；不会扫描历史落盘但已不属于第四步目标范围的歌手主页歌曲 raw。名字不含 `/` 时，先查当前 `artists` 表，库内姓名精确且唯一命中时直接记录为 `db_matched`，不再请求 `quick_search`；库内同名多 MID 时记录为 `db_ambiguous_name`，不自动选择；库内未命中时才调用 `quick_search`，并先读取本地 quick_search raw 缓存，缓存不存在时才请求 QQ 音乐。名字包含 `/` 时不再按原始整体名字检索，而是直接按 `/` 拆开，对每个拆分片段分别执行同样的“先查库、再搜索”唯一精确匹配补 MID。第九步歌曲入库遇到缺 MID 且名字包含 `/` 的演唱者时，也按拆分片段分别查 `artists`；能唯一命中的片段会入库，不能唯一命中的片段跳过，只有没有任何片段命中时才按缺 MID 拒绝。本步骤每次运行都会重写 CSV 视图，CSV 只用于人工检查，不再作为断点输入或跳过依据。
默认 CSV：

```text
data/processed/validation/song_singer_mid_fill/csv_views/song_singer_mid_fill.csv
```

默认 quick_search raw 缓存：

```text
data/raw/qqmusic/quick_search_artist_mid/song_singer/
```

按第三步当前目标范围扫描：

```powershell
python -m music_metadata_graph.pipelines.fill_song_singer_missing_mids --all
```

如果第三步使用了非默认歌手列表 raw 目录，第四步前置也传入相同目录：

```powershell
python -m music_metadata_graph.pipelines.fill_song_singer_missing_mids --all --singer-list-raw-dir data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all
```

也可以限制到指定歌手：

```powershell
python -m music_metadata_graph.pipelines.fill_song_singer_missing_mids --name 周杰伦 --name 薛之谦 --name 林俊杰 --name 汪苏泷
```

后续第九步歌曲入库不读取该 CSV，而是直接查询 `artists` 表；当缺 MID 的演唱歌手名在 `artists.name` 中精确且唯一命中时，用该库内 MID 补齐。

## 步骤六：补全歌曲歌手信息
本步骤扫描步骤三的 `SongTab.List[].singer[]`。如果某个非空 `singer.mid` 不在 `artists` 表里，则请求 `qqmusic.singer.get_info` 保存 raw JSON，并把满足 `mid`、`name` 非空的歌手补入库。
如果 `icon` 为空，会尝试使用 `Info.BaseInfo.BackgroundImage` 作为 `icon`；如果仍为空，则保留空字符串。
默认 raw 目录：

```text
data/raw/qqmusic/singer_info/
```

请求并入库入口：

```powershell
python -m music_metadata_graph.pipelines.collect_missing_song_singers_to_db --name 周杰伦 --name 薛之谦 --name 林俊杰 --name 汪苏泷
```

本步骤使用 `qqmusic-api-python` 的 `Client.gather()` 合包请求缺失歌手信息，默认每批 20 个 request；可用 `--batch-size` 覆盖。脚本按批渐进处理，成功响应会立即按一个歌手一个文件写入 raw JSON；如果某批整体失败，会降级为单个请求逐个尝试。仍有失败 MID 时，脚本会先把已成功解析的歌手写入数据库，再以非零退出提示重新运行继续补齐。
如果第三步歌曲 Tab 只跑了一部分，使用第三步目标范围与已落盘 raw 的交集继续处理；历史落盘但已不属于第四步目标范围的 raw 不会参与：

```powershell
python -m music_metadata_graph.pipelines.collect_missing_song_singers_to_db --all
```

`--all` 只扫描当前数据库 `artists` 中、且本地已经有 `data/raw/qqmusic/singer_homepage_song_tab/<mid>/page_*_size_*.json` 的歌手；不会因为数据库里其他歌手缺少歌曲 Tab raw 而停止。
当前四位歌手结果：
- 歌曲行：3492。
- 歌曲歌手条目缺 `mid`：22，无法通过本步骤补全。
- 本轮新补入歌手：326。
- 当前 `artists` 表总行数：7266。

## 步骤七：按歌曲请求专辑详情 raw JSON
专辑 raw 数据现在从歌曲派生：脚本先读取步骤四的 `SongTab.List[]`，从每首歌的 `album.mid` 或非 0 `album.id` 提取专辑请求键，去重后调用 `qqmusic.album.get_detail`。
默认 raw 目录：

```text
data/raw/qqmusic/song_album_detail/
```

当前四位歌手结果：
- 输入歌曲行：3492。
- 缺少可请求专辑键的歌曲行：1676。
- 去重后请求专辑详情：654。
- 当前专辑详情 JSON 文件：654。
请求脚本：

```powershell
python -m music_metadata_graph.pipelines.collect_song_album_detail_raw --name 周杰伦 --name 薛之谦 --name 林俊杰 --name 汪苏泷
```

部分请求支持两种输入：

```powershell
python -m music_metadata_graph.pipelines.collect_song_album_detail_raw --mid 0025NhlN2yWrP4
python -m music_metadata_graph.pipelines.collect_song_album_detail_raw --name 周杰伦
```

按第三步目标范围与已落盘 raw 的交集请求专辑详情；历史落盘但已不属于第四步目标范围的 raw 不会参与：

```powershell
python -m music_metadata_graph.pipelines.collect_song_album_detail_raw --all
```

本步骤使用 `qqmusic-api-python` 的 `Client.gather()` 合包请求专辑详情，默认每批 20 个 request；可用 `--batch-size` 覆盖。脚本按批渐进处理，成功响应会立即按一个专辑一个文件写入 raw JSON；如果某批整体失败，会降级为单个请求逐个尝试。默认 `--max-failed-fetches 0`，仍有失败专辑 key 时会以非零退出提示重新运行继续补齐；若确认是少量平台业务错误，可显式设置 `--max-failed-fetches N` 允许流程继续。失败清单会写入 `--failure-json` 指定的 JSON，默认路径为 `data/processed/validation/album_detail_fetch_failures/album_detail_fetch_failures.json`，MVP 模式默认写入 `data/processed/validation_mvp/album_detail_fetch_failures/album_detail_fetch_failures.json`。
`--all` 只扫描当前数据库 `artists` 中、且本地已经有歌曲 Tab raw 的歌手；不会因为数据库里其他歌手缺少歌曲 Tab raw 而停止。

## 步骤八：专辑详情入库
专辑表只导入五个业务字段，不导入 `singer.singerList[]`：

```text
mid           TEXT PRIMARY KEY
id            INTEGER NOT NULL UNIQUE
name          TEXT NOT NULL
albumType     TEXT NOT NULL
publishDate   TEXT NOT NULL
raw_json_path TEXT NOT NULL DEFAULT ''
raw_page      INTEGER NOT NULL DEFAULT 0
raw_row_index INTEGER NOT NULL DEFAULT 0
```

字段来源：

```text
mid         <- $.basicInfo.albumMid
id          <- $.basicInfo.albumID
name        <- $.basicInfo.albumName
albumType   <- $.basicInfo.albumType
publishDate <- $.basicInfo.publishDate
```

导入入口：

```powershell
python -m music_metadata_graph.pipelines.import_song_album_detail_to_db
```

当前导入结果：654 行。
不满足完备约束的专辑不会写入 `albums`，会写入拒绝 CSV：

```text
data/processed/validation/album_import_rejections/csv_views/album_import_rejections.csv
```

当前全量结果：50,624 个专辑详情 raw，其中 50,547 个专辑导入 `albums`，77 个专辑因 `publishDate` 为空被写入拒绝 CSV。
`raw_page` 对专辑详情这种“一文件一专辑”的请求固定为 0；`raw_row_index` 固定为 1。

## 步骤九：歌曲入库与拒绝 CSV
歌曲入库直接写完备歌曲表。入库约束：

```text
song.mid 非空且唯一，作为主键
song.id 非空且唯一
song.name/title 非空
language 非空
album_mid 非空且存在于 albums.mid
singer 列表非空
每个 singer_mid 非空且存在于 artists.mid
```

通过约束的歌曲写入 `songs`，演唱者关系写入 `song_singers`：

```text
songs:
mid           TEXT NOT NULL PRIMARY KEY
id            INTEGER NOT NULL UNIQUE
name          TEXT NOT NULL
title         TEXT NOT NULL
language      INTEGER NOT NULL
album_mid     TEXT NOT NULL REFERENCES albums(mid)
raw_json_path TEXT NOT NULL DEFAULT ''
raw_page      INTEGER NOT NULL DEFAULT 0
raw_row_index INTEGER NOT NULL DEFAULT 0
song_singers:
song_mid      TEXT NOT NULL REFERENCES songs(mid)
singer_order  INTEGER NOT NULL
singer_mid    TEXT NOT NULL REFERENCES artists(mid)
raw_json_path TEXT NOT NULL DEFAULT ''
raw_page      INTEGER NOT NULL DEFAULT 0
raw_row_index INTEGER NOT NULL DEFAULT 0
PRIMARY KEY (song_mid, singer_order)
```

入库失败歌曲写入 CSV：

```text
data/processed/validation/song_import_rejections/csv_views/song_import_rejections.csv
```

歌曲导出 CSV 统一按歌名拼音首字母和拼音排序，避免按 Unicode 字符顺序排列。
当前第十步之前的歌曲导出 CSV 统一只保留以下列：

```text
song_mid
song_id
song_name
song_title
song_language
album_name
album_type
album_publish_date
singer_count
singers_json
```

其中 `singers_json` 为 JSON 数组，每个歌手对象只包含 `mid` 和 `name`。
所有导出 CSV 会对文本单元格做 Excel 公式安全转义：如果去掉开头空白后以 `=`、`+`、`-`、`@` 开头，会在 CSV 展示值前加单引号，避免 Excel 打开时把歌名、专辑名或制作人名当成公式；数据库和 raw JSON 不改写。
第十步及之后的歌曲 CSV 会使用以下列；`作词`、`作曲` 放在演唱信息前面：

```text
song_mid
song_id
song_name
song_title
song_language
album_name
album_type
album_publish_date
作词
作曲
singer_count
singers_json
```

导入入口：

```powershell
python -m music_metadata_graph.pipelines.import_singer_song_tab_to_db --name 周杰伦 --name 薛之谦 --name 林俊杰 --name 汪苏泷
```

如果第三步歌曲 Tab 只跑了一部分，歌曲入库也使用第三步目标范围与已落盘 raw 的交集；历史落盘但已不属于第四步目标范围的 raw 不会参与：

```powershell
python -m music_metadata_graph.pipelines.import_singer_song_tab_to_db --all
```

当前四位歌手结果：
- raw 歌曲行：3492。
- 唯一歌曲：3479。
- 入库歌曲：1809。
- 入库歌曲-歌手关系：2977。
- 拒绝歌曲 CSV：1670 行。
- 拒绝原因：`missing_album_mid` 1668 首，`missing_singer_mid` 18 首。

## 步骤十：按专辑类型过滤已入库歌曲
本步骤作用于 SQLite 中已通过完备约束的 `songs` 表，只保留专辑类型为：

```text
Single
EP
录音室专辑
```

被过滤歌曲会从 `songs` 删除，`song_singers` 通过外键级联删除。被过滤记录写入正式 CSV：

```text
data/processed/validation/song_filtering/csv_views/songs_removed_by_step8_album_type.csv
```

## 步骤十一：请求制作人 raw JSON
本步骤作用于步骤十之后的 `songs` 表。
正式全量流程会对步骤十保留下来的歌曲请求 `qqmusic.song.get_producer`，保存原始 JSON 到：

```text
data/raw/qqmusic/song_producer/
```

开发阶段为了控制耗时，可以先只请求歌曲歌手包含周杰伦的歌曲：

```powershell
python -m music_metadata_graph.pipelines.collect_song_producer_raw --artist-mid 0025NhlN2yWrP4
```

本步骤使用 `qqmusic-api-python` 的 `Client.gather()` 合包请求制作人信息，默认每批 20 个 request；可用 `--batch-size` 覆盖。脚本按批渐进处理，成功响应会立即按一首歌一个文件写入 raw JSON；如果某批整体失败，会降级为单个请求逐个尝试。仍有失败歌曲 MID 时，脚本会先写出已成功歌曲的缺制作人 MID 检查 CSV，再以非零退出提示重新运行继续补齐。
本步骤同时检查作词、作曲条目是否缺少制作人 `mid`，检查结果写入：

```text
data/processed/validation/song_producer/csv_views/song_producer_missing_mid.csv
```

当前周杰伦范围结果：步骤十后 261 首歌，261 个 raw JSON 均已存在，作词/作曲缺 `mid` 行数为 0。

## 步骤十二前置：quick_search 补作词作曲缺 MID
本步骤扫描步骤九制作人 raw 中 `作词`、`作曲` 条目里制作人 `mid` 为空、`name` 非空的名字。名字不含 `/` 时，先查当前 `artists` 表，库内姓名精确且唯一命中时直接记录为 `db_matched`，不再请求 `quick_search`；库内同名多 MID 时记录为 `db_ambiguous_name`，不自动选择；库内未命中时才调用 `quick_search`，并先读取本地 quick_search raw 缓存，缓存不存在时才请求 QQ 音乐。名字包含 `/` 时不再按原始整体名字检索，而是直接按 `/` 拆开，对每个拆分片段分别执行同样的“先查库、再搜索”唯一精确匹配补 MID。第十步作词作曲入库遇到缺 MID 且名字包含 `/` 的制作人时，也按拆分片段分别查 `artists`；能唯一命中的片段会入库，不能唯一命中的片段跳过。本步骤每次运行都会重写 CSV 视图，CSV 只用于人工检查，不再作为断点输入或跳过依据。
默认 CSV：

```text
data/processed/validation/song_credit_mid_fill/csv_views/song_credit_mid_fill.csv
```

默认 quick_search raw 缓存：

```text
data/raw/qqmusic/quick_search_artist_mid/song_credit/
```

运行命令：

```powershell
python -m music_metadata_graph.pipelines.fill_song_credit_missing_mids
```

后续第十步导入作词作曲关系不读取该 CSV，而是直接查询 `artists` 表；当缺 MID 的制作人名在 `artists.name` 中精确且唯一命中时，用该库内 MID 补齐。

## 步骤十三：导入作词作曲关系
本步骤读取步骤九的制作人 raw JSON，只导入作词、作曲。制作人如果尚未存在于 `artists`，则按 `mid`、`name`、`icon` 补入。
本步骤导入完成后会额外导出一份临时歌曲 CSV：

```text
data/processed/validation/temp_song_filtering/csv_views/songs_after_step10_credit_import.csv
```

该 CSV 包含 `作词`、`作曲` 两列，且两列位于 `singer_count`、`singers_json` 之前。默认只导出演唱歌手包含周杰伦、林俊杰、薛之谦、汪苏泷任意一人的歌曲；这只限制临时 CSV 的查看范围，不限制第十步作词作曲关系入库范围。
如果需要覆盖默认临时 CSV 歌手范围，可重复传入：

```powershell
python -m music_metadata_graph.pipelines.import_song_credits_to_db --temp-export-artist-name 周杰伦 --temp-export-artist-name 林俊杰
```

如果需要恢复导出当前 `songs` 表全部歌曲，可传入：

```powershell
python -m music_metadata_graph.pipelines.import_song_credits_to_db --all-temp-songs-csv
```

关系表 `song_credit_artists`：

```text
song_mid      TEXT NOT NULL REFERENCES songs(mid)
role          TEXT NOT NULL
artist_order  INTEGER NOT NULL
artist_mid    TEXT NOT NULL REFERENCES artists(mid)
raw_json_path TEXT NOT NULL DEFAULT ''
raw_page      INTEGER NOT NULL DEFAULT 0
raw_row_index INTEGER NOT NULL DEFAULT 0
PRIMARY KEY (song_mid, role, artist_order)
```

开发阶段限定周杰伦范围导入：

```powershell
python -m music_metadata_graph.pipelines.import_song_credits_to_db --artist-mid 0025NhlN2yWrP4
```

当前第十步导入后，歌曲歌手包含周杰伦的歌曲对应作词/作曲关系 455 条。

## 步骤十四：删除作词作曲不完整歌曲
本步骤作用于第十步之后的 `songs` 表。为了保证网页可视化中的歌曲都有可用作词、作曲关系，一首歌必须同时满足：

```text
至少 1 个 作词
至少 1 个 作曲
```

缺少任一角色的歌曲会从 `songs` 删除，`song_singers` 和 `song_credit_artists` 通过外键级联删除。被过滤记录写入正式 CSV：

```text
data/processed/validation/song_filtering/csv_views/songs_removed_by_step11_incomplete_credits.csv
```

为了人工查看，本步骤默认额外导出保留歌曲临时 CSV：

```text
data/processed/validation/temp_song_filtering/csv_views/songs_after_step11_complete_credits.csv
```

该临时 CSV 与正式歌曲过滤 CSV 使用同一组 12 列，包含 `作词` 和 `作曲`。默认只导出演唱歌手包含周杰伦、林俊杰、薛之谦、汪苏泷任意一人的保留歌曲；这只限制临时 CSV 的查看范围，不影响第十一步全库删除逻辑。
如果需要覆盖默认临时 CSV 歌手范围，可重复传入：

```powershell
python -m music_metadata_graph.pipelines.filter_songs_by_credit_completeness --temp-export-artist-name 周杰伦 --temp-export-artist-name 林俊杰
```

如果需要导出第十一步后的全部保留歌曲，可传入：

```powershell
python -m music_metadata_graph.pipelines.filter_songs_by_credit_completeness --all-temp-kept-csv
```

运行入口：

```powershell
python -m music_metadata_graph.pipelines.filter_songs_by_credit_completeness
```

## 步骤十五：按规范化歌名和同作词作曲去重
本步骤作用于制作人请求之后的 `songs` 表。
`songs.mid` 是主键，`songs.id` 是唯一字段，所以“先按歌曲 mid/id 去重”已经由第七步的数据库约束保证；本步骤不再重复导出 mid/id 重复项，只会在运行结果中报告唯一性检查。
随后按“规范化歌名 + 同作词 + 同作曲”去重。规范化规则由 `music_metadata_graph.text_normalization.normalize_song_title_identity()` 统一维护：先做 Unicode `NFKC`、中英文常见标点等价转换、连续省略号归一、`feat./ft./featuring` 写法归一、连续空白压缩，再去除括号内侧空格和逗号、斜杠、连接符等标点两侧空格，最后做大小写折叠和首尾空白去除；该规则保留普通英文词间空格，不删除括号中的语义版本文本。作词和作曲分别按 `artist_mid` 集合判断，同一角色内的人员顺序不影响比较。只有歌名、作词集合、作曲集合都相同的歌曲才进入同一去重组；演唱歌手不再参与本步骤去重判断。重复组优先保留：

```text
录音室专辑 > EP > Single > 较小 song id
```

被过滤记录会从 `songs` 删除，`song_singers` 通过外键级联删除。被过滤记录写入正式 CSV：

```text
data/processed/validation/song_filtering/csv_views/songs_removed_by_step12_same_credit_name_dedupe.csv
```

运行入口：

```powershell
python -m music_metadata_graph.pipelines.filter_imported_songs
```

本轮为了人工查看，去重之后保留的歌曲会额外导出临时 CSV：

```text
data/processed/validation/temp_song_filtering/csv_views/songs_after_step12_same_credit_name_dedupe.csv
```

该临时 CSV 与正式歌曲过滤 CSV 使用同一组 12 列，包含追加的 `作词` 和 `作曲`。默认只导出演唱歌手包含周杰伦、林俊杰、薛之谦、汪苏泷任意一人的保留歌曲；这只限制临时 CSV 的查看范围，不影响第十二步全库去重和正式删除清单。
如果需要覆盖默认临时 CSV 歌手范围，可重复传入：

```powershell
python -m music_metadata_graph.pipelines.filter_imported_songs --temp-export-artist-name 周杰伦 --temp-export-artist-name 林俊杰
```

如果需要恢复导出第十二步后的全部保留歌曲，可传入：

```powershell
python -m music_metadata_graph.pipelines.filter_imported_songs --all-temp-kept-csv
```

## 当前不做
- 当前不导入专辑署名歌手信息；如果后续需要专辑-歌手关系，应另行设计关系表。
- 当前不再使用歌手专辑列表作为正式专辑来源。
- 当前不提交原始缓存、数据库文件、大量图片或生成图谱到 Git。

## 归档内容

### `archive/album_source_retiming_2026-05-13/`
本次专辑请求时机调整前的歌手专辑列表相关内容归档，包含：
- 旧 `data/raw/qqmusic/singer_album_list/` raw JSON。
- 旧 SQLite `albums` 表导出。

### `archive/redesign_reset_2026-05-13/`
重新设计前的当前流程归档，包含旧采集脚本、旧验证脚本、旧 raw 数据、旧 processed 产物、旧报告和旧网页依赖配置。

### `archive/legacy_pipeline_2026-05-12/`
更早的端到端旧流程归档，包含旧采集、旧专辑验证、旧报告、旧网页、旧制作人员缓存和旧图谱导出相关内容。
