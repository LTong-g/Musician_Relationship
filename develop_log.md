Read this file as UTF-8.

# 开发日志

## 撰写规则
- 本日志记录项目开发过程中的需求理解、方案、实现、验证、事故、阶段回顾和版本准备事实。
- 本日志默认只能追加记录，不删除、不改写历史内容；除非用户明确要求。
- 追加记录必须写到对应日期下；若当天日期标题不存在，先创建当天日期标题。
- 每天只保留一个二级日期标题，格式为 `## YYYY-MM-DD`。
- 每次新增事件必须使用三级标题，格式为 `### 事件标题`。
- 事件标题必须描述单一事件，禁止使用“继续”“更新”“杂项”“延续上个话题”等模糊标题。
- 同一日期下发生不同性质事项时，必须拆成多个三级标题分别记录。
- 分析方案、代码实现、验证结果、事故复盘、版本更新必须分开记录，不得混写在同一标题下。
- 标题下使用 `-` 分点记录事实。
- 每条记录只写已经发生的事实、已经形成的方案、已经识别的风险、已经执行的验证或当前明确的缺口。
- 不把尚未执行的下一步计划写成已完成事实。
- 需要记录后续工作时，使用“剩余缺口”或“后续待处理”表述，并说明它尚未完成。
- 用户提出功能需求并要求方案时，必须记录需求理解、目标效果、实现方案、风险边界和本轮不做范围。
- 每次实质性代码改动后，必须记录改动内容、影响范围和对应验证。
- 验证记录必须写清验证对象、执行方式和观察结果；禁止只写“验证通过”“无问题”等空泛结论。
- 无法验证时，必须记录无法验证的原因、风险和替代检查。
- 发生误改、误删、误提交、构建异常、环境异常或需求理解偏差时，必须记录事故事实、影响范围、修复方式和防止复发的规则调整。
- 用户纠正需求、方案、表达方式或协作规则时，必须记录纠正内容和已做调整。
- 版本更新必须单独记录一条日志，不得混在功能实现记录里。
- 开发日志不得记录 token、密钥、密码、证书指纹、私有签名材料、未脱敏用户隐私、本机私有绝对路径或可复用凭据。
- 记录本机环境时使用泛化表述，例如“本机 Android SDK 路径”“项目原始长路径”“临时映射路径”。
- 开发日志不是版本记录；版本记录只写用户可感知的最终变化。
- 开发日志新增 5-10 条实质记录后，应做一次阶段回顾。
- 阶段回顾必须记录总目标、当前进度、已完成内容、剩余缺口、下一步方案、验收方式和完成后离总目标还差什么。

## 日志内容

## 2026-05-11

### 压缩记录：项目初始化与第一阶段目标收敛
- 本段压缩原第 33-1400 行中前两版开发日志，保留需求理解、实现决策、验证结果、事故和归档边界；删除重复的单点 UI 微调、临时报告修正和中间产物流水账。
- 项目初始化时，`AGENTS.md` 被补充为音乐人合作关系图谱项目协作规则，明确项目围绕音乐平台元数据采集、标准化、图谱分析和本地可视化，不做播放、下载、绕过平台限制或商业化服务。
- 运行环境确定为项目指定 Conda Python；第一阶段依赖包括 `qqmusic-api-python`、`pandas`、`pydantic`、`httpx`、`tenacity`、`python-dotenv`、`duckdb`、`networkx`、`pyvis` 和后续新增的 `pypinyin`。
- 初始产品目标从“命令行生成样例图谱”调整为“GitHub Pages 可打开的静态网页 + 本地离线采集生成静态数据”，网页只负责查看和交互，不在浏览器中实时请求 QQ 音乐接口。
- 用户多次纠正后，第一阶段数据获取主流程收敛为先获取音乐人列表，再获取歌手歌曲，过滤版本和噪声，补充作词/作曲等制作人员，最后生成可视化数据和网页。
- 搜索接口被降级为辅助能力，仅用于用户只给姓名时解析候选歌手或歌曲；不作为正式采集主路径。
- 一次中文搜索验证曾因 PowerShell 管道传参导致中文关键词变成问号，误判为 QQ 音乐搜索第一条不可靠；后续规则调整为涉及中文常量、报告和判断时优先使用明确 UTF-8 的 Python 工具或仓库脚本。

### 压缩记录：第一版端到端歌曲采集与过滤流程
- 第一版实现了热门歌手身份表采集、单歌手歌曲采集、版本过滤、专辑归属验证、制作人员请求、报告生成和网页数据导出等端到端流程。
- 歌手冷启动先从 `qqmusic.singer.get_singer_list_index` 获取歌手列表，记录歌手 `id/mid/name/other_name/spell/singer_pic` 等基础身份信息。
- 早期歌曲来源使用 `qqmusic.singer.get_songs_list`；后续复核发现该接口更像宽泛歌手标记索引，可能返回非主页官方语义的歌曲，因此切换到 `qqmusic.singer.get_tab_detail(mid, TabType.SONG)` 的主页歌曲 Tab。
- 周杰伦、薛之谦、林俊杰等全量样本验证显示，主页歌曲 Tab 与旧 `GetSingerSongList` 对周杰伦当前返回集合完全一致，因此异常歌曲问题不能只靠换接口解决，仍需要业务过滤和专辑验证。
- 歌曲初筛规则逐步收敛为：先判断 `name/title` 是否一致，再过滤空专辑，再按标题版本词过滤，之后对保留候选去重。
- 版本词和过滤顺序经过多轮修正，删除了容易误杀的专辑名“巡回”等触发条件，避免《周大侠》这类歌曲因专辑名被错误过滤。
- 通过周杰伦、薛之谦、林俊杰全量样本验证，`name/title` 不一致成为识别 Live、伴奏、语言版、演奏版、Session、口白和特别版的重要早期信号。
- 专辑归属验证使用 `album.get_detail` 请求专辑详情，结合专辑署名歌手、专辑类型、发行公司、语言、简介和版本词判断 kept/rejected/review。
- 对《发如雪 (醇享版)》《轨迹 (醇享版)》《Six Degrees》的 Instrumental/Slowed/Reverb/Sped Up 版本、《你听得到 (Inst.)》《土耳其进行曲》《- 夜访巴赫曲》等样例，验证了版本去重和强非目标专辑剔除规则。
- 对原声带、合辑、合作单曲、综艺首发、现场类作品等边界情况，第一版结论是不应简单按专辑歌手不含目标歌手或 Live/节目关键词一刀切删除，应保留 review 或后续证据链。
- 歌曲制作人员补全使用 `qqmusic.song.get_producer(song_mid 或 song_id)`，按“演唱、作词、作曲、编曲、制作人”等分组提取字段；上游返回 `Lst=null` 时记录为 `missing_producer_list`，不再中断批处理。
- 可视化前新增制作人员完整性过滤：默认 `songs_kept` 只保留 `credits.status=ok` 且作词、作曲均非空的歌曲；缺作词、缺作曲或制作人员列表缺失的歌曲写入隔离文件供调试。
- 周杰伦、薛之谦、林俊杰全量制作人员验证确认多数保留歌曲可取得作词作曲，但林俊杰样本中存在纯音乐、序曲或器乐类歌曲只有作曲没有作词，属于字段覆盖差异而非请求失败。
- 第一版报告生成曾多次出现 Markdown 表格空行、竖线未转义、中文问号、Windows 链接不可点击等问题；后续补充规则要求报告必须 UTF-8 回读、无 U+FFFD、表格列数和结构可校验，本地文件链接必须使用正斜杠绝对路径 Markdown 链接。

### 压缩记录：第一版静态网页与 force-graph 可视化
- 第一版网页从手写 SVG 图谱工作台开始，目标是静态 GitHub Pages 可打开，读取本地导出的 JSON，不提供在线采集。
- 网页语义被用户纠正为“QQ 音乐是数据集，周杰伦、薛之谦、林俊杰等是目标歌手筛选范围”，不是一个歌手一个数据集。
- 页面需要在图谱边稀疏时仍显示节点，不能因为没有边就只显示文字；目标歌手节点不能作为特殊中心节点或与同名普通节点重复出现。
- 手写 SVG 版本曾尝试网格布局、力导向布局、曲线边、箭头、标签阈值和概览过滤，但实际体验仍存在节点重叠、连线混乱、布局不自然和交互弱的问题。
- 经过框架调研，选择安装并接入 `force-graph`，本地 vendor 脚本复制到网页目录，保留静态页面打开方式且避免 CDN 依赖。
- `force-graph` 版本支持 Canvas 缩放、平移、拖拽、点击节点或边更新右侧详情、选中边方向表达、边粒子和头像节点兜底。
- 后续调整包括：目标歌手多选下拉、全选/反选、候选搜索、顶部状态栏压缩、控件原生风格、图谱自适应高度、右侧详情栏内部滚动、有向模式以慢速粒子表达方向。
- 用户反馈目标歌手不应出现“周杰伦连到另一个周杰伦”，因此导出脚本改为目标歌手节点也使用普通 artist 身份键，过滤自环边，`is_target` 只作为范围和统计字段，不参与视觉特殊化。
- 网页数据范围被纠正为只展示作词和作曲齐全的 `songs_kept`；隔离条目和数据质量页签从网页中移除，仅保留为本地调试产物。
- 第一版网页的主要剩余风险是缺少浏览器截图级自动化验证；当时多次只能用 `node --check`、HTTP 资源检查、JSON 协议检查和静态断言替代。

### 压缩记录：第一版归档前的工程整理和规则沉淀
- 源码包从 `musician_relationship/` 重命名为 `music_metadata_graph/`，正式实现集中到 `music_metadata_graph/pipelines/`，删除包根部旧薄包装脚本。
- `pyproject.toml` 曾暴露旧流程命令入口，包括热门歌手、单歌手歌曲、专辑验证、报告和网页导出；后续归档时这些入口被删除。
- `.gitignore` 多次整理，明确 `data/`、`archive/`、`reports/`、`node_modules/` 等本地数据、归档、报告和依赖目录不提交；源码、脚本、README、AGENTS、开发日志和项目配置不被忽略。
- 旧端到端流程的数据和缓存最终移动到 `archive/legacy_pipeline_2026-05-12/`，包括 `data/processed/singer_songs/`、`data/processed/validation/legacy/`、`data/raw/qqmusic/singer_songs/`、`data/raw/qqmusic/song_producers/` 和 `data/raw/qqmusic/album_probe/`。
- 旧端到端流程代码移动到 `archive/legacy_pipeline_2026-05-12/code/music_metadata_graph/pipelines/`，包括旧 `collect_singer_songs.py`、`validate_album_ownership.py`、`write_singer_pipeline_report.py` 和 `export_web_dataset.py`。
- 旧静态网页目录 `web/` 整体移动到 `archive/legacy_pipeline_2026-05-12/web/`，包括旧页面、样式、脚本、静态数据和本地 vendor 文件。
- 归档清单 `archive/legacy_pipeline_2026-05-12/manifest.txt` 记录旧流程数据、代码和网页的来源、移动状态、目录数、文件数和归档位置。
- README、AGENTS 和目录报告同步说明旧流程只作为历史参考，当前正式流程不得再从这些归档目录读取，也不得把旧流程代码、网页或数据写回当前正式目录。

## 2026-05-12

### 压缩记录：第二版高可信分支和补充分支的形成
- 第一版归档后，第二版目标转向重新整理歌曲输入来源，围绕高可信歌曲子集和补充分支建立更清晰的验证数据流。
- 高可信分支以歌手专辑列表和专辑歌曲为主：请求 `singer.get_album_list`，按专辑类型保留 `Single`、`EP`、`录音室专辑`，再对保留专辑请求 `album.get_song`，最后按歌曲 `singer[].mid` 是否包含目标歌手过滤。
- 四位开发样本为周杰伦、薛之谦、林俊杰、汪苏泷；四位样本高可信分支完整采集后，按专辑歌曲请求得到 1475 行，目标歌手匹配后 1062 行，后续同名去重后 828 行。
- 高可信流程曾在外层执行工具等待约 245 秒后超时，但复核发现四位歌手原始缓存、单人结果和汇总结果已完整落盘，没有观察到接口封禁、连续空响应或鉴权失败证据。
- 高可信 CSV 列名规则被纠正为非辅助列只能使用 QQ 音乐接口原始顶层键，项目新增列统一使用 `aux_` 前缀，`confidence` 等自造普通列被移除。
- 用户进一步纠正 CSV 只是人工查看版，正式流程不应默认保留 CSV；脚本新增 `--write-csv`，正式 JSON 输出和验证 CSV 目录分离，CSV 不得写入正式输出目录内部。
- 补充分支来自主页歌曲 Tab 全集，初始思路是全集减去高可信子集，后经多轮纠正统一命名为“补充分支”，不得再称为“全集分支”或“主页分支”。
- 补充分支最终阶段性流程为：filter1 空专辑过滤；filter2 专辑 id/mid 非空过滤；请求并缓存 `album.get_detail` 专辑详情；filter3 只保留 `Single`、`EP`、`录音室专辑`；filter4 去重；filter5 减去高可信子集已有歌名。
- 补充分支有效验证结果为：候选 3492 行，filter1 后 1856 行，filter2 后 1816 行，专辑详情补充后 1816 行，filter3 后 1126 行，filter4 后 954 行，filter5 后 128 行。
- 补充分支专辑详情缓存写入 `data/raw/qqmusic/supplement_album_details/`；重跑时 1816 行专辑详情补充全部为 `cache_hit`，说明已缓存专辑不会重复请求。
- 两个分支的去重规则最终统一为先按歌曲 `mid/id` 去重，再按原始 `name` 同名去重；同名不同专辑类型优先级为 `录音室专辑 > EP > Single > 较小 song id`。
- 两个分支都要求每一步同时输出保留行和被过滤行，验证阶段不得只保留最终结果；过滤原因、步骤、分支、目标歌手和来源记录必须可追溯。

### 压缩记录：第二版目录、CSV 和验证产物治理
- 第二版中，用户多次指出正式流程目录、验证目录、CSV 查看版和临时探查目录混在一起，要求重新划分边界。
- `data/processed/validation/four_singers/` 成为四位样本验证目录，按 `json_outputs/` 和 `csv_views/` 区分结构化验证输出与人工查看 CSV。
- 高可信分支验证输出移动到 `data/processed/validation/four_singers/json_outputs/high_confidence_singer_songs/` 和 `csv_views/high_confidence_singer_songs/`。
- 补充分支验证输出移动到 `data/processed/validation/four_singers/json_outputs/supplement_singer_songs/` 和 `csv_views/supplement_singer_songs/`。
- 正式流程目录不应保留四位样本 JSON 或 CSV；四位样本被认定为 validation 数据，不是全量正式结果。
- 目录报告脚本 `scripts/write_data_directory_report.py` 改为使用 Python UTF-8 生成中文报告，避免 PowerShell here-string 写中文导致问号乱码。
- `reports/data_directory_tree_2026-05-12.md` 被多次重写，从逐个列出叶子 JSON/CSV 文件调整为目录级别说明，并标注目录本级直接包含的文件类型和数量。
- 旧中间目录如 `album_probe`、`interface_compare`、`smoke`、临时 CSV check 目录和旧命名合并表被清理；清理前均检查目标路径位于当前工作区内。
- 跨歌手合并验证表被移除，两个分支统一只保留每个歌手自己的 JSON/CSV 验证文件，summary 只保留汇总计数，不再指向跨歌手表格产物。
- 歌曲相关 CSV 展示列在后续阶段被统一为固定列规则：歌曲基础字段、专辑字段、`singer_count` 和只包含 `mid/name` 的 `singers_json`；该规则后来沉淀进 AGENTS。

## 2026-05-13

### 压缩记录：第二版数据库化方向分析
- 用户指出当前处理仍依赖 JSON 文件，操作不方便，要求分析切换到数据库管理数据的可行性和边界。
- 早期分析认为可以先把现有 JSON 导入数据库再处理；用户纠正后，方案调整为采集阶段直接写入数据库，后续清洗、过滤、去重、关系边生成和查询都围绕数据库进行。
- 原生接口响应仍保存为 `data/raw/` JSON 文件，作为原始证据和可复现缓存；数据库不重复保存完整原生 JSON。
- 数据库只保存 `raw_json_path`、接口名、请求参数、抓取时间、状态、来源记录 ID 和抽取出的结构化字段；需要回看原始响应时通过路径回到 `data/raw/`。
- 初版数据库 UML 曾包含过多 staging、pipeline row、统计和身份映射内部表，被用户指出过度复杂；后续表达收敛为先说明核心概念：`SourceRecord`、`Run`、`Artist`、`Album`、`Song`、`SongArtist`、`Credit`、`SongFilterState`。
- 数据库化必须保留验证审计能力：每一步过滤都能查询保留行和被过滤行，且保留分支、步骤、结果、原因、目标歌手和来源记录追溯。
- SQLite 被判断为更适合当前本地个人分析和批处理阶段；DuckDB 可作为后续分析查询或批量导出补充。
- 本阶段只完成方向分析和 UML 边界纠正，未创建正式数据库文件，未改造采集脚本直接入库，也未删除既有 raw、JSON 或 CSV 验证产物。

### 归档当前流程和本地数据准备重新设计
- 用户要求把第二版当前流程全部归档，包括 raw 数据，以便重新设计请求顺序和存储。
- 已创建 `archive/redesign_reset_2026-05-13/`，归档当时的正式采集代码 `music_metadata_graph/pipelines/`、辅助脚本 `scripts/`、本地 `data/`、`reports/`、旧网页依赖配置、force-graph 参考文档和 Python 缓存。
- 初次直接移动 `data/` 时 Windows 返回访问拒绝；随后改为复制到归档目录、核对文件数与字节数一致后再删除当前目录，避免半归档或数据丢失。
- 归档统计为文件 1227 个、目录 308 个、字节数 177694935；新增 `archive/redesign_reset_2026-05-13/manifest.md` 后归档目录实际文件数为 1228 个。
- 当前根目录重新收敛为源码骨架，移除已归档脚本入口，README 和 AGENTS 明确 `archive/redesign_reset_2026-05-13/` 与 `archive/legacy_pipeline_2026-05-12/` 只作为历史参考，不得作为当前正式流程继续运行或写回当前正式目录。
- 验证确认归档清单、文本编码、包骨架语法、pyproject 解析和归档统计可用；Git 状态复核因 Windows dubious ownership 失败，本次未修改全局 `safe.directory` 配置。

### 重新设计启动和完整歌手列表 raw
- 用户要求重新设计一步一步来，并明确如果关键目标、输入、输出、验收或风险未明确，AI 应先停止设计并与用户讨论；该规则已写入 AGENTS 用户长期偏好。
- 第一步确认仍从 QQ 音乐完整歌手列表开始，先保存原生 JSON，不入库，以便检查字段键后再决定数据库设计；归档中未找到可复用的 `singer_list_index`、`singer_registry` 或 `hot_singer` 原生缓存。
- 新增 `collect_singer_list_raw.py` 和命令入口 `mr-collect-singer-list-raw`，请求 `qqmusic.singer.get_singer_list_index` 全量分页并保存到 `data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all/`。
- 完整采集保存 86 页原生 JSON，合计 6803 条歌手行，接口 `total` 也为 6803；顶层键包括 `area/code/genre/hotlist/index/sex/singerlist/tags/total`，`singerlist[]` 包含 `id/mid/name/title/type/uin/pmid/area_id/country_id/country/other_name/spell/trend/concern_num/singer_pic` 等字段。
- 为请求 JSON 字段检查新增 `music_metadata_graph/tools/write_request_json_key_dictionary.py`，生成 `docs/request_json_key_dictionary.xlsx`；初始 sheet `01_singer_list_index` 记录完整歌手列表 JSON 的键、出现次数、示例值和中文释义。

### 歌手表入库和主键边界
- 用户确认当前阶段只使用 QQ 音乐数据源，不再按多平台合并设计；歌手表使用 QQ 音乐 `mid` 作为主键，早期曾短暂保留数字 `id` 唯一字段，后续又按新规则移除数字 `id` 入库。
- 新增 `import_singer_list_to_db.py` 和命令入口 `mr-import-singer-list-db`，从完整歌手列表 raw JSON 导入 SQLite；初始 `singers` 表导入 6803 行。
- 后续为歌手表补充 `raw_json_path`、`raw_page`、`raw_row_index` 追溯字段；再根据当前数据库规则调整为 `artists` 表，并逐步收敛字段为 `mid/name/area_id/fans_num/fans_source/fans_raw_json_path/other_name/icon/spell/raw_json_path/raw_page/raw_row_index`。
- 早期关于 `pmid`、数字 `id` 和多平台身份字段的设计已被后续规则推翻；当前有效规则以 AGENTS 中 `artists.mid` 主键、QQ 音乐单数据源、不保存数字 `id` 为准。

### 主页歌曲 Tab raw 恢复和请求脚本
- 用户确认开发阶段仍只用周杰伦、薛之谦、林俊杰、汪苏泷四位歌手验证结构；正式流程后续再面向当前入库规则选中的全部目标歌手。
- 复核 `archive/redesign_reset_2026-05-13/data/raw/qqmusic/singer_homepage_song_tab/` 后，恢复四位歌手主页歌曲 Tab raw JSON 到当前 `data/raw/qqmusic/singer_homepage_song_tab/`，共 118 个 JSON 文件、14564795 字节。
- 四位 raw 行数为周杰伦 1012、薛之谦 528、林俊杰 1013、汪苏泷 939，合计 3492 行；字段字典 xlsx 增加第二个 sheet 记录歌曲 Tab JSON 结构。
- 用户指出恢复归档 raw 不等于已有请求脚本，因此补充独立主页歌曲 Tab 请求脚本 `collect_singer_homepage_song_tab_raw.py` 和命令入口，默认按低频、缓存优先、可恢复方式保存原生 JSON。
- 后续第四步确认正式流程只对第三步按当前规则入库选中的歌手请求主页歌曲接口；不得因为歌曲歌手或制作人后续补入 `artists` 就自动扩大第四步请求范围。

### 歌曲、专辑和数据库职责边界迭代
- 早期曾设计歌曲完整表与完备表分层，并试验导入 `song_rows_complete`、`songs_complete` 和 `song_singers_complete`；用户随后纠正数据库职责边界，要求当前只保存满足完备约束的唯一歌曲实体，不保留中间完整歌曲表作为正式表。
- 试验性歌曲完整表入库实现已删除；当前有效歌曲规则为 `songs.mid` 主键、`id` 唯一、`mid/id/name/title/language/album_mid` 非空、`album_mid` 外键到 `albums.mid`、演唱者列表非空且每个 `singer_mid` 外键到 `artists.mid`。
- 早期曾建立歌手专辑列表 raw 请求和专辑列表入库流程；后续用户纠正专辑来源和时机，确认专辑不再来自歌手专辑列表，而是从歌曲 raw 的 `album.mid` 或非 0 `album.id` 去重后请求 `qqmusic.album.get_detail`。
- 旧歌手专辑列表 raw、旧专辑表导出和旧专辑入库实现移动到 `archive/album_source_retiming_2026-05-13/`；当前正式流程不得再把 `data/raw/qqmusic/singer_album_list/` 作为专辑来源。
- 歌曲派生专辑详情流程改为写入 `data/raw/qqmusic/song_album_detail/`，`albums` 表从 `basicInfo` 抽取 `mid/id/name/albumType/publishDate` 和 raw 追溯字段；缺少必需字段的专辑写入拒绝 CSV。
- 关于允许专辑发行日期为空的设计曾被提出，随后被推翻；当前规则仍要求 `publishDate` 非空，不满足完备约束的专辑不得写入 `albums`。

### 歌曲歌手补全和完备歌曲入库
- 第五步确认在请求歌曲后、请求专辑前，扫描歌曲 `singer[].mid`，对不在 `artists` 表中的非空歌手 MID 请求 `qqmusic.singer.get_info`，保存 raw JSON 到 `data/raw/qqmusic/singer_info/` 并补入 `artists`。
- 对 `get_info` 做过单 MID 和批量边界验证；结论是可用 `Client.gather()` 合包请求，但必须按批渐进落盘，失败时降级单个请求并保留已成功结果。
- 缺失演唱者 MID 前置补全规则后续扩展为：先查当前 `artists` 表，姓名唯一命中则直接使用；未命中才读取或请求 `quick_search` raw；名字包含 `/` 时按片段拆分处理，不再按整体名字检索。
- 四位样本曾用韩红和《飞云之下》验证补歌手逻辑是否能覆盖合作歌手；完备歌曲入库后导出 `song_import_rejections.csv` 记录不满足约束的唯一歌曲。
- 入库后新增专辑类型过滤、同名同歌手去重和临时 CSV 导出；第九步后 CSV 逐步收敛为一首歌一行，`singers_json` 只保留歌手 `mid/name`，歌曲相关 CSV 列规则写入 AGENTS。

### 归档代码回看和作词作曲来源复查
- 用户多次要求回看第一版和第二版归档内容：第一版归档网页位于 `archive/legacy_pipeline_2026-05-12/web/`，可用本地静态服务预览；预览结束后按记录 PID 关闭服务。
- 复查第一版头像缺失可视化逻辑确认旧网页在头像不可用时使用默认视觉兜底；复查第一版 `get_producer` 来源确认作词作曲来自 QQ 音乐制作人员接口，而不是歌词全文解析。
- 复查第一版 raw 缓存发现 `get_producer` 返回同时存在大写键形态 `Lst/ReinforceMsg/Title/Producers/Name/SingerMid` 和小写键形态 `data/reinforce_msg/title/producers/name/singer_mid`，当前解析需兼容两类形态。
- 复查第二版归档确认两个歌曲输入分支分别是高可信歌曲子集分支和补充分支，它们只作为历史流程参考，不属于当前重新设计后的数据库直入流程。

## 2026-05-14

### 制作人 raw 请求和作词作曲关系入库
- 复查第一版作词作曲来源后，当前流程限定先对周杰伦范围请求制作人信息，验证 `song.get_producer` raw 结构和缺 MID 情况。
- 后续流程扩展为第十一步请求 `song.get_producer` 制作人 raw，第十二步前置补 MID，第十三步将 `作词`、`作曲` 导入 `song_credit_artists`，并将缺失制作人补入 `artists`。
- `song_credit_artists` 使用 `(song_mid, role, artist_order)` 作为主键，`song_mid` 外键到 `songs.mid`，`artist_mid` 外键到 `artists.mid`；当前只导入 `作词` 和 `作曲`。
- 第十步后临时 CSV 增加 `作词`、`作曲` 两列，位置放在演唱信息前；第十三步前后的歌曲 CSV 规则分别固定为 10 列和 12 列。

### 请求量、参数边界和断点续跑
- 评估完整流程全量请求量后，识别出歌手歌曲 Tab、缺失歌手详情、专辑详情和制作人 raw 是主要请求成本；第 4、5、9 步逐步改为使用 `Client.gather()` 合包。
- 复核第一步歌手列表接口参数和字段取值，短暂尝试默认地区筛选后恢复为全量地区 raw；后续第三步入库时再按 `area_id in (0, 1)` 等规则过滤。
- 调整第二步歌手入库字段和筛选，保留被过滤行可查询的验证要求；后续又被粉丝量规则进一步收紧。
- 支持从已有歌曲 Tab raw 继续第 4、5 步，后续统一第 4、5、7 步目标范围为“第四步当前目标范围与已落盘歌曲 Tab raw 的交集”，不再扫描历史落盘但已不属于当前目标范围的 raw。
- 坏缓存 JSON 被视为缓存未命中；第四步缺失歌手请求、第五步专辑详情请求和第九步制作人 raw 请求均改为渐进落盘，避免单批失败导致已成功结果丢失。

### CSV 安全和过滤步骤收敛
- 用户指出 CSV 可能存在 Excel 公式注入风险；实现所有正式或临时 CSV 文本单元格在去掉开头空白后以 `= + - @` 开头时加单引号，仅影响 CSV 展示值，不改数据库和 raw JSON。
- 插入作词作曲完整性过滤步骤：保留条件为至少 1 个 `作词` 且至少 1 个 `作曲`，过滤掉的歌曲导出到 `songs_removed_by_step11_incomplete_credits.csv`，并生成临时保留 CSV。
- 第十二步去重规则从同名同歌手调整为“规范化歌名 + 同作词集合 + 同作曲集合”，演唱歌手不参与判断；同一角色内人员顺序不影响比较。
- 歌名规范化后续复用 `music_metadata_graph.text_normalization.normalize_song_title_identity()`，覆盖 Unicode NFKC、中英文常见标点等价、省略号、feat/ft/featuring 写法、括号内侧空格和标点两侧空格，同时保留普通英文词间空格和括号语义版本文本。

## 2026-05-15

### quick_search 缺 MID 前置补全
- 多次手动测试姓名搜索、`search_by_type`、歌手列表接口和 `quick_search` 后，确认缺 MID 补全应优先查数据库，只有库内未唯一命中时才读取或请求本地 quick_search raw。
- 新增歌曲演唱者和制作人两条前置补 MID 流程，分别输出人工检查 CSV 到 `song_singer_mid_fill` 和 `song_credit_mid_fill`，但后续正式入库不读取这些 CSV，而是直接查询 `artists` 表。
- 名字不含 `/` 时先查 `artists` 表，唯一命中直接用，库内同名多 MID 标记 ambiguous；名字包含 `/` 时拆成片段分别执行同样规则，不再按原始整体名字检索。
- quick_search raw 分别写入 `data/raw/qqmusic/quick_search_artist_mid/song_singer/` 和 `data/raw/qqmusic/quick_search_artist_mid/song_credit/`；每次运行重写 CSV 视图，不把旧 CSV 当断点输入。

### 脚本运行日志和完整流程编排
- 设计并实现脚本运行日志保留功能，随后增强异常退出防护、后台异步写入和单次运行日志上下文复用；后续用于追踪完整流程每一步输出。
- 梳理当前完整数据流程、CSV 读取点和两个 quick_search 前置步骤，确认前置步骤不再读取旧 CSV 作为跳过依据。
- 实现一键完整流程编排入口 `python -m music_metadata_graph.pipelines.run_full_pipeline`，将 raw、CSV、SQLite 表、外键、目标覆盖、过滤约束、网站资源和网站生成结果检查纳入每一步前后置检查。
- 数据库默认路径集中到 `music_metadata_graph/pipelines/defaults.py` 的 `DEFAULT_DB_PATH`，脚本保留 `--db` 覆盖能力，避免各脚本重复硬编码 `data/music_metadata_graph.sqlite3`。
- 设计并实现 MVP 流程模式：默认数据库 `data/music_metadata_graph_mvp.sqlite3`，validation 产物写入 `data/processed/validation_mvp/`；MVP raw 复用正式 raw 目录，不另建 MVP raw。

### artists 范围、area_id 和目标口径修复
- 检查发现 `artists.area_id` 覆盖偏少，修复 artists upsert 保留已有 `area_id`，避免后续歌曲歌手或制作人补库覆盖第三步已有地区字段。
- 第三步歌曲 Tab 请求目标口径收紧为只请求第二步入库歌手；第四步前置补 MID、第五步和第七步后续流程也统一使用同一目标范围。
- 复查确认第四步全量尚未完成时，第 5、6、8 步使用 `--all` 只扫描第四步当前目标范围与已落盘歌曲 Tab raw 的交集，不再扫描历史落盘但不属于当前目标范围的 raw。
- 总数据库第四步缺失演唱者补库进度曾被检查并确认完成；第六步专辑详情 raw 落盘进度也做过阶段性复核。

### MVP 静态图谱生成和可视化迭代
- 用户要求实现 MVP 数据库最后一步可视化，确认目标是从 SQLite 生成本地静态图谱页面，不回写归档目录，不恢复旧 JSON 作为正式数据源。
- 新增 MVP 数据库静态图谱生成器，后续修复头像未显示、节点名字显示、悬停高亮、选中高亮、详情栏信息、自我边和自我创作开关等交互。
- 可视化方向逐步收敛为永久无向边，但保留方向提示和粒子效果开关；边宽、透明度、节点高亮、点击详情、布局稳定性和粒子方向经过多轮调整。
- 分析树形 DAG 后确认合作图谱不适合强制树形表达；仍以 force-graph 网络图为主，通过筛选、选中和详情表解释方向。
- 专辑详情单个失败导致全流程中断的问题被修复为失败阈值和失败清单机制，并补采单个失败专辑详情 raw。

## 2026-05-16

### 调整边详情为完整方向拆解
- 用户纠正边悬浮框和右侧详情不应保留总览行，而应只保留方向拆解行，并且每条方向拆解行都包含“谁到谁、职能、数量”。
- 已修改 `linkLabel(edge)`：不再返回 `职能 · 总歌曲数` 总览，而是直接返回 `directionLabels(edge).join("<br>")`。
- 已新增并复用 `directionLabels(edge)`，每条方向行格式为 `作词/作曲人 -> 演唱者：职能 · N 首`。
- 已修改右侧边详情：删除总览卡片，改为直接用 `directionLabels(item)` 生成方向拆解卡片；支撑歌曲列表保持不变。
- 已更新 `tests/test_static_graph_build.py`，断言方向行包含职能和数量，tooltip 使用 `directionLabels(edge)`，并断言旧的 `edge.role + edge.song_count` 总览返回不存在。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，悬浮框和右侧边详情都只使用方向拆解行，方向行包含方向、职能和数量，不再包含旧总览返回逻辑。

### 调整可视化节点大小上限
- 用户要求把节点大小上限改成 65。
- 已修改 `build_static_graph.py` 前端节点权重映射，将 `val` 的上限从 `24` 调整为 `65`。
- 已修改 `nodeRadius(node)`，将头像节点实际绘制半径上限从 `22` 调整为 `65`，避免只改 `val` 后被绘制半径二次截断。
- 已更新 `tests/test_static_graph_build.py`，断言 `val` 上限和 `nodeRadius` 上限均为 `65`。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，包含节点 `val` 和绘制半径的 `65` 上限，且旧的 `22` 绘制半径上限已移除。

### 修正粒子不贴合边路径
- 用户反馈粒子并没有在边上运行。
- 已定位当前自定义方向粒子按两端节点直线插值绘制，但图谱中作词和作曲边通过 `linkCurvature("curvature")` 画成曲线，因此粒子会看起来脱离实际边路径。
- 已新增 `edgeCurvePoint(edge, progress)`，按当前边的 `source`、`target` 和 `curvature` 计算二次贝塞尔曲线上的粒子坐标。
- 已修改 `drawDirectionalParticles()`，粒子位置改为调用 `edgeCurvePoint()`；当真实方向与合并边的 `source -> target` 相反时，用 `1 - progress` 反向沿同一曲线运行。
- 已更新 `tests/test_static_graph_build.py`，断言曲线坐标函数、贝塞尔控制点计算和反向运行逻辑存在。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，包含 `edgeCurvePoint()`、贝塞尔控制点计算、方向反转逻辑和粒子使用曲线坐标的代码。

### 修正粒子曲线侧和缩放行为
- 用户反馈粒子颜色和边颜色是反的，并且粒子大小固定，不会和图一起缩放。
- 已判断颜色反向表现来自粒子运行在另一侧曲线：自定义贝塞尔控制点方向与 force-graph 实际曲线方向相反，导致作词粒子视觉上贴到作曲边侧。
- 已修改 `edgeCurvePoint()` 的控制点计算，将 `controlX/controlY` 调整为与 force-graph 曲线侧一致。
- 已修改粒子半径，从 `2.2 / globalScale` 改为图坐标固定半径 `2.2`，使粒子随图谱缩放一起变大或变小，而不是保持屏幕像素固定。
- 已更新 `tests/test_static_graph_build.py`，断言新的控制点方向和固定图坐标粒子半径存在。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，包含修正后的贝塞尔控制点方向，且不再包含 `2.2 / globalScale` 的固定屏幕像素粒子半径。

### 调整非高亮边透明度
- 用户要求选中高亮时，非高亮边也统一压暗，透明度乘以 `0.5`。
- 已修改 `edgeAlpha(edge)`：高亮边仍直接返回透明度 `1`；非高亮边先按当前边权重计算 `0.05` 到 `1` 的连续透明度，再在存在高亮状态时乘以 `0.5`。
- 已更新 `tests/test_static_graph_build.py`，断言高亮边透明度保持 `1`，并断言非高亮边在 `hasActiveHighlight()` 时返回 `alpha * 0.5`。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，包含高亮边透明度为 `1` 和非高亮边透明度乘以 `0.5` 的逻辑。

### 禁用非高亮边悬浮框
- 用户要求选中高亮时，非高亮边不要触发悬浮框。
- 已修改 `linkLabel(edge)`：当 `hasActiveHighlight()` 为真且当前边不是高亮边时，返回空字符串，避免暗化的非高亮边显示 tooltip。
- 高亮边和未进入选中状态时的普通边仍保留原有方向拆解 tooltip。
- 已更新 `tests/test_static_graph_build.py`，断言非高亮边 tooltip 抑制逻辑存在。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，包含非高亮边 tooltip 返回空字符串的逻辑，并保留高亮边方向拆解 tooltip。

### 增加节点多选高亮
- 用户要求增加允许选中多个节点，参考 force-graph 官方 multi-selection 示例；选中多个节点时，只高亮选中的节点和选中节点之间的边。
- 已新增前端状态 `selectedNodeIds: new Set()`，用于维护多选节点集合。
- 已新增 `toggleNodeSelection(node)`，点击节点时在集合中加入或移除该节点；点击空白清空多选；点击边仍切换为单边选择并清空节点多选。
- 已新增 `setNodeSelectionHighlight()`，单选节点时保留原有“节点及相邻关系”高亮；多选节点时只把选中节点加入高亮，并只高亮两端都在 `selectedNodeIds` 中的边。
- 已新增 `syncNodeSelectionState()`，根据选中节点数量维护 `state.selected` 为 `null`、单节点或多节点状态。
- 已修改节点绘制的选中判断为 `state.selectedNodeIds.has(node.id)`，多选节点都会显示选中轮廓。
- 已修改右侧详情，多选状态下显示已选音乐人数、每个选中音乐人的演唱/作词/作曲统计，以及选中节点之间存在的关系边摘要。
- 已更新页面提示文案，说明点击节点可多选，多选时只高亮选中节点之间的边。
- 已更新 `tests/test_static_graph_build.py`，断言多选集合、节点切换函数、多节点状态和“边两端都在选中集合内才高亮”的条件存在。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，包含节点多选集合、点击切换、多节点状态、选中节点之间边高亮条件和多选详情文案。

### 修正关系明细表方向显示
- 用户截图指出底部“关系明细”表里的来源音乐人和目标音乐人看起来随机反着。
- 已定位原因：图谱线条为避免 4 条边而按无向 pair 合并，`edge.source` 和 `edge.target` 是排序后的无向端点；关系明细表仍直接使用 `edge.source/edge.target`，因此不代表真实 `作词/作曲人 -> 演唱者` 方向。
- 已修改 `renderTable()` 的关系明细分支：从 `buildGraph().edges.map(...)` 改为 `buildGraph().edges.flatMap(...)`，按每条合并边内部的 `directions` 展开真实方向行。
- 关系明细表的来源音乐人现在使用 `direction.source`，目标音乐人使用 `direction.target`，歌曲数使用 `direction.song_count`。
- 支撑歌曲列表按方向目标 `target_mid` 和方向职能过滤，避免方向行显示另一方向或另一职能的歌曲。
- 已更新 `tests/test_static_graph_build.py`，断言关系明细表使用 `direction.source`、`direction.target` 和 `direction.song_count`，并断言不再使用 `edge.source/edge.target` 作为表格方向。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，关系明细表已按 directions 展开，并且不再包含旧的 `source: nodeName(edge.source)` 或 `target: nodeName(edge.target)`。

### 调整节点多选触发方式
- 用户要求多选必须按住 Ctrl 才能触发；否则选中一个点后再点另一个点应切换为单选。
- 已修改 `toggleNodeSelection(node, event)`：只有 `event.ctrlKey` 或 `event.metaKey` 为真时才累积多选或移除节点。
- 普通点击节点时会清空 `selectedNodeIds` 后只加入当前节点，从而切换为单选。
- 已修改 `.onNodeClick((node, event) => ...)`，把点击事件传入选择处理函数；兼容 Ctrl 和 Meta 键。
- 已同步页面提示文案，将“点击节点可多选”改为“Ctrl+点击节点可多选”。
- 已同步 `README.md`，说明普通点击节点为单选，按住 Ctrl 点击节点可多选。
- 已更新 `tests/test_static_graph_build.py`，断言节点点击传入事件、Ctrl/Meta 多选判断、普通点击清空旧选择逻辑存在。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，包含 Ctrl/Meta 多选判断、普通点击清空旧选择逻辑和页面提示文案。

### 展开多选关系支撑歌曲
- 用户反馈选中多位歌手时右侧详情只显示关系摘要，没有显示具体歌曲。
- 已修改多选详情渲染：对选中节点之间的每条高亮边，先显示方向拆解行，再调用 `renderSongList(edge.songs || [])` 展开该关系的支撑歌曲。
- 已保留多选顶部“已选 N 位音乐人”和每位选中音乐人的演唱/作词/作曲统计。
- 已更新 `tests/test_static_graph_build.py`，断言多选详情读取选中节点之间的高亮边，并展开 `renderSongList(edge.songs || [])`。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，包含多选关系边读取逻辑和支撑歌曲展开逻辑。

### 尝试缓解节点重叠
- 用户希望尝试缓解节点之间的重叠，但不希望边太长。
- 已修改 `configureForces(api)`，新增 `d3.forceCollide((node) => nodeRadius(node) + 4).strength(0.9).iterations(2)`，优先通过节点碰撞半径减少头像重叠。
- 已将排斥力从 `-285` 小幅增强到 `-380`，避免过强排斥导致图谱过度扩散。
- 已将 link distance 从 `88 + ... * 7` 调整为 `92 + ... * 5`，只轻微增加基础距离，并降低随弱边额外拉长的幅度，控制边不要明显变长。
- 已更新 `tests/test_static_graph_build.py`，断言碰撞力、排斥力和边距参数存在。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 7 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，包含碰撞力、`chargeForce.strength(-380)` 和新的 link distance 参数。

### 回退导致图谱空白的碰撞力调用
- 用户反馈新加的防重叠改动让网页绘图显示不出来。
- 已定位最可疑原因是页面脚本调用 `d3.forceCollide(...)`，但当前静态 HTML 只通过 force-graph vendor 初始化图谱，不保证 `d3` 暴露为全局变量；该运行时错误会阻断后续绘图。
- 已移除 `api.d3Force("collide", d3.forceCollide(...))`，先恢复图谱正常显示。
- 保留不依赖全局 `d3` 的温和力导向调整：`chargeForce.strength(-380)` 和新的 link distance 参数。
- 已更新 `tests/test_static_graph_build.py`，断言不再包含 `d3.forceCollide`。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 7 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，不再包含 `d3.forceCollide`，仍保留 `chargeForce.strength(-380)` 和新的 link distance 参数。

### 分析同页 2D/3D 图谱切换方案
- 用户询问当前使用的图谱库存在 3D 版本，是否可以在同一个页面里用开关切换 2D/3D。
- 已确认当前可视化页面由 `music_metadata_graph/visualization/build_static_graph.py` 生成单页静态 HTML，现有前端使用本地 `force-graph.min.js`，数据结构已经是节点和边的图数据，适合复用到 3D 图谱。
- 已核对 `3d-force-graph` 官方仓库和 API，确认其 script tag 入口暴露 `ForceGraph3D`，使用 `{nodes, links}` 图数据，支持节点、边、方向粒子、点击事件、宽高和背景色等现有页面需要的核心能力。
- 目标效果确定为同一个 `index.html` 内新增“3D 视图”开关，默认保留现有 2D 体验；切到 3D 后复用相同筛选、搜索、高亮和右侧详情逻辑。
- 风险边界为 3D 视图依赖 WebGL，且首版不复刻 2D canvas 的圆形头像节点；头像完整展示仍以 2D 视图为主，3D 首版使用颜色球体节点展示网络空间结构。
- 本轮不做独立 3D 页面、后端服务、VR/AR 模式、3D 头像纹理精细化和数据管线重构。

### 实现同页 2D/3D 图谱切换
- 已新增本地 3D vendor 文件 `music_metadata_graph/visualization/vendor/3d-force-graph.min.js` 和对应 MIT 许可证文件，生成后的静态 HTML 不依赖在线 CDN。
- 已修改 `BuildConfig`、命令行参数和 HTML 生成逻辑，新增 `--vendor-3d` 参数，并把 2D 与 3D vendor 脚本都嵌入最终 HTML。
- 已在工具栏新增“3D 视图”开关，并在图谱区域新增 `graph-2d`、`graph-3d` 两个容器和 3D 降级提示区域。
- 已将前端图谱实例拆分为 `graphInstance2d` 和 `graphInstance3d`，新增 `setupGraph2d()`、`setupGraph3d()`、`syncGraphViews()`、`activeGraphInstance()` 等逻辑。
- 2D 视图保留原有头像节点、canvas 曲线粒子、曲线边、高亮和多选行为；3D 视图使用 `ForceGraph3D` 的球体节点、边颜色、边宽、方向粒子、点击节点、点击边和背景点击事件。
- 3D 视图复用现有 `buildGraph()`、`graphPayload()`、`edgeColor()`、`linkLabel()`、`toggleNodeSelection()`、`setLinkHighlight()`、`renderSelection()` 等数据和交互逻辑。
- 已同步 `README.md`，说明页面支持 2D/3D 视图开关、3D 使用本地 `3d-force-graph` WebGL 运行时，以及 3D 不可用时保留 2D。

### 验证同页 2D/3D 图谱切换
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过。
- 验证对象为 `build_static_graph.py` 和 `tests/test_static_graph_build.py`，执行项目指定 Conda Python 的 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 存在且大小约 3.75 MB，包含 `graph-2d`、`graph-3d`、`view-mode-toggle` 和 `ForceGraph3D`，无 U+FFFD 替换字符。
- 已尝试使用 Codex 内置浏览器打开本地 `file:///` 页面，但浏览器安全策略阻止访问；随后尝试通过 `127.0.0.1` 本地静态服务访问，也被浏览器策略拦截为 `ERR_BLOCKED_BY_CLIENT`，因此本轮未能完成真实浏览器截图和点击验收。
- `git status --short` 仍因本机 Git safe.directory 所有权检查失败无法执行，本轮未修改全局 Git 配置。

### 修正 3D 图谱空白加载问题
- 用户反馈 3D 视图加载不出来，并询问是加载时间较长还是存在问题。
- 已判断当前 MVP 规模为 1210 个节点、2271 条边，3D 首次初始化可能慢于 2D，但不应长期空白；更可能是 3D 初始化异常、WebGL 环境失败或渲染负载过重。
- 已将 3D 初始化从 `new ForceGraph3D(container)` 改为官方示例使用的 `ForceGraph3D()(container)` 形式，降低不同版本 UMD 包下的初始化兼容风险。
- 已降低 3D 首版渲染负载：3D 链接宽度改用库默认细线，链接透明度降为 `0.42`，降低 `linkResolution` 和 `nodeResolution`，减少 WebGL 几何压力。
- 已新增 3D 初始化状态提示：切换 3D 且重新喂图数据时显示“正在初始化 3D 视图”，初始化完成后清除提示。
- 已新增 3D 初始化异常捕获：如果构造实例、配置 force 或写入图数据时报错，页面会自动退回 2D，并在图谱右下角显示 `3D 初始化失败，已退回 2D` 及错误信息，避免用户只看到空白。
- 已新增一个临时排查页 `data/visualization_mvp/3d_smoke.html`，内嵌同一 3D vendor 和 3 个节点的小图，用于区分 3D 库/WebGL 是否可用和主图数据规模是否导致问题；该文件位于生成产物目录，不作为长期源码入口。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；执行 `py_compile` 未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成主页面；静态检查确认 HTML 包含官方初始化形式、3D 初始化提示、失败回退提示，且无 U+FFFD 替换字符。

### 瘦身 3D 引擎图数据
- 用户反馈 `3d_smoke.html` 正常，但主项目仍一直显示初始化，并询问为什么官方 large 示例没有问题。
- 已判断官方 large 示例通常只把节点和边的渲染必要字段传给 3D 引擎，而当前主项目此前把运行详情面板所需的完整边对象也传入 3D，包括每条边的支撑歌曲数组、方向拆解和其他展示字段；这些字段对 3D WebGL 渲染无用，会增加 3D 内部对象处理和布局负担。
- 已修改 `graphPayload(nodes, edges, options)`，新增 `thin` 参数；当 `state.viewMode === "3d"` 时，传给 3D 引擎的节点只保留 `id`、`mid`、`name`、目标标记和统计计数字段，边只保留 `id`、`source`、`target`、`role`、`roles`、`song_count` 和 `directions`。
- 右侧详情、关系明细和支撑歌曲仍继续从页面完整 `rawData` 和 `currentGraph` 中读取，不依赖 3D 引擎内的瘦身对象，因此用户可见详情能力不应丢失。
- 已移除 3D 的 `linkWidth(0)` 设置，让 3D 链接回到库默认轻量线段渲染，避免宽度为 0 触发不可见或不稳定渲染路径。
- 已新增 `clearGraphWarningSoon()`，在 3D `graphData()` 成功写入后短延迟清除初始化提示，避免仅因 force simulation 没有触发 `onEngineStop` 就一直显示初始化。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；执行 `py_compile` 未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成主页面；静态检查确认 HTML 包含 3D 瘦身 payload、官方初始化形式和短延迟清除提示逻辑，不再包含 `.linkWidth(0)`，且无 U+FFFD 替换字符。

### 移除 3D 同步预热阻塞
- 用户反馈主项目 3D 仍加载不出来，并追问到底是什么数据太重。
- 已统计当前主页面完整图数据：`window.GRAPH_DATA` 约 2.19 MB，包含 1210 个节点、2271 条原始边、1970 首歌曲；传给 3D 引擎的瘦身 payload 约 0.86 MB，并非单纯 JSON 体积过大。
- 已进一步定位更可能的阻塞点是 3D 配置中的 `warmupTicks(90)`：该设置会在 `api.graphData(...)` 内同步预跑 90 次 3D 力导向布局，导致主线程在首帧前被阻塞，初始化提示无法按时清除。
- 当前主图合并后约 1210 个节点、2227 条边，最高加权度节点约 941，存在明显中心节点；这种拓扑在同步 warmup 下比 `3d_smoke.html` 的 3 个节点和官方 thin payload 示例更容易首帧阻塞。
- 已将 3D 配置从 `warmupTicks(90)` 改为 `warmupTicks(0)`，并将 `cooldownTicks` 调整为 `180`，让 3D 视图先渲染首帧，再在浏览器中异步收敛布局，更接近官方 large 示例的加载方式。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；执行 `py_compile` 未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成主页面；静态检查确认 HTML 包含 `.warmupTicks(0)`、`.cooldownTicks(180)`、3D 瘦身 payload 和官方初始化形式，且无 U+FFFD 替换字符。

### 进一步压缩 3D 渲染对象
- 用户反馈初始化提示会很快消失，但 3D 画面仍一直加载不出来。
- 已判断 `api.graphData()` 不再同步卡死，问题从“初始化阻塞”转为“3D 实例返回后画布没有可见图形”；排查方向改为 3D canvas、尺寸、相机、节点尺寸和传入对象形态。
- 已进一步将 3D 引擎 payload 压缩到只包含渲染必要字段：3D 节点只保留 `id`、`name`、`is_target`、`degree` 和压缩后的 `val`，3D 边只保留 `id`、`source`、`target`、`role` 和 `song_count`；`directions`、`roles`、`songs` 和音乐人统计字段不再传给 3D 引擎。
- 为保持 tooltip 和详情能力，新增 `fullEdge(edge)`，3D hover 或点击得到瘦身边对象后通过 `edge.id` 回查 `currentGraph.edges` 中的完整边。
- 已将 3D 节点尺寸从沿用 2D 的 `val <= 65` 改为单独压缩到约 `1.2` 到 `7`，避免 2D 头像尺寸规则在 3D 球体中导致过大的几何体或异常取景。
- 已将 3D 背景从透明改为浅色 `#f8fafc`，并将 `nodeRelSize` 调整为 `2.6`，使 3D smoke 与主图背景/节点可见性更接近。
- 已停止对 3D 复用 2D 的强排斥力配置，3D 力布局改用库默认力配置，进一步接近官方 large 示例。
- 静态测算当前 3D 最终 payload 约 471 KB，包含 1210 个节点和 2227 条合并边，最大节点 `val` 约 6.8；当前剩余负载主要是图拓扑本身和最高加权度约 941 的中心节点，不再是支撑歌曲数组或 directions 等业务字段。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；执行 `py_compile` 未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成主页面；静态检查确认 HTML 包含浅色 3D 背景、压缩节点尺寸、3D 瘦身 payload、完整边回查逻辑，且无 U+FFFD 替换字符。

### 增加 3D 画布可见性诊断
- 用户反馈右下角初始化弹窗很快消失，但 3D 画面仍一直加载不出来，说明 `graphData()` 已返回，问题转向 3D canvas 尺寸、相机取景或材质可见性。
- 已新增 `graph3dDiagnostics()`，在 3D 图谱写入后显示节点数、边数、容器尺寸、canvas 像素尺寸和相机 z 值，便于判断是否存在 canvas 为 0、容器尺寸异常或相机位置异常。
- 已新增 `stabilize3dView()`，在 3D 数据写入后分 120ms、700ms、1800ms 三次重新设置图谱宽高、相机位置、`zoomToFit(500, 80)` 和 `refresh()`，避免首帧时容器尺寸尚未稳定或相机未对准。
- 已将 3D 链接颜色从动态 `rgba(...)` 改为纯 hex `solidEdgeColor(edge)`，并使用 `linkOpacity(0.36)` 控制透明度，排除 3D 材质解析 alpha 字符串导致线条不可见的可能。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；执行 `py_compile` 未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成主页面；静态检查确认 HTML 包含 3D 诊断、3D 稳定化取景、纯色链接和无 U+FFFD 替换字符。

### 固定 3D 初始坐标和远距相机
- 用户提供 3D 诊断结果：节点、边、容器、canvas 和相机 z 均正常，说明数据已写入且画布尺寸正常，但画面仍不可见。
- 已将排查重点从数据和尺寸转到坐标范围与取景：即节点可能被力布局或初始位置推到相机视野外。
- 已新增 `sphericalPosition()`，3D 初始节点不再使用随机盒状坐标，而是确定性铺到半径 520 的球面上，保证初始对象围绕原点分布。
- 已将 3D 相机从 `z=980` 拉远到 `z=2200`，并停止在稳定化步骤里调用 `zoomToFit()`，避免 bbox 尚未稳定时自动取景把相机放到不合适位置。
- 已扩展 `graph3dDiagnostics()`，额外显示节点坐标范围 `x/y/z min..max`，便于下一轮判断对象是否仍在视野范围内。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；执行 `py_compile` 未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成主页面；静态检查确认 HTML 包含球面初始坐标、远距相机和坐标范围诊断，且无 U+FFFD 替换字符。

### 增加 3D 层叠和场景诊断
- 用户提供新诊断结果显示节点 1025、边 1458、容器 1311x602、canvas 1966x903、相机 z=2200、坐标范围约 `±520`，但 3D 仍不可见且鼠标拖动缩放无效果。
- 已判断数据、canvas 尺寸、相机距离和坐标范围均已正常，剩余高概率问题为 3D canvas 被其他层覆盖、当前/隐藏视图指针事件冲突，或 Three 场景对象没有被实际创建/渲染。
- 已新增 CSS：隐藏视图显式 `display:none` 且禁用 pointer events；显示中的 `graph-3d` 和其 canvas 明确设置 z-index、浅色背景和蓝色半透明轮廓，用于判断用户看到的是否为真实 3D canvas 区域。
- 已将 3D 诊断扩展为显示 `scene` 对象数量，用于判断 Three 场景是否包含已创建对象。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；执行 `py_compile` 未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成主页面；静态检查确认 HTML 包含 3D canvas 轮廓、隐藏视图 CSS、scene 诊断和无 U+FFFD 替换字符。

### 使用自定义 Three 球体节点排查 3D 空白
- 用户反馈新版本只看到蓝色 canvas 框，看不到诊断消息和 3D 节点。
- 已判断蓝色框出现说明 3D canvas 层已经显示且没有被完全遮住，诊断消息消失是层级被 canvas 覆盖；节点仍不可见则可能是默认 3D 节点材质、灯光或对象创建路径问题。
- 已将 `.graph-warning` 的 z-index 提高到 10，确保诊断条显示在 3D canvas 上方。
- 已新增 `colorNumber()`，将 hex 颜色转换为 Three.js 可用数字颜色。
- 已在 3D 图谱中新增 `nodeThreeObject()`，绕过库默认节点材质，直接为每个节点创建 `THREE.SphereGeometry` 加 `THREE.MeshBasicMaterial` 的球体；该材质不依赖场景灯光，适合排除灯光和默认材质不可见问题。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；执行 `py_compile` 未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成主页面；静态检查确认 HTML 包含诊断条高层级、自定义 Three 球体节点、`MeshBasicMaterial` 和无 U+FFFD 替换字符。

### 修复 3D 自定义节点回退和诊断消失
- 用户反馈 3D 视图现在只能看到蓝色框，之前还能看到诊断消息，现在诊断消息也消失。
- 已重新定位蓝色框含义：蓝色框来自诊断 CSS，说明 3D canvas 已挂载；诊断消失主要是 `onEngineStop()` 会清空诊断条，且自定义节点逻辑可能在 `window.THREE` 不存在时返回空对象。
- 已修改 `setupGraph3d()`：只有检测到 `window.THREE` 时才注册 `api.nodeThreeObject()` 自定义球体；如果 3D vendor 没有把 Three.js 暴露到全局，则退回 `3d-force-graph` 默认节点渲染，避免把节点主动渲染为空。
- 已修改 `colorNumber()`，只接受合法 6 位 hex 颜色，其他颜色字符串统一回退到 `0x3b82f6`，避免高亮态 `rgba(...)` 被解析为 `NaN`。
- 已取消 3D 引擎停止后自动清空诊断条；3D 诊断现在会继续显示 `THREE yes/no`、renderer render calls 和 canvas 中心命中的 DOM 元素，便于判断是对象未创建、渲染未调用还是被层覆盖。
- 已限制 `zoomToFit()` 只在 2D 视图执行，3D 继续使用固定球面初始坐标和 `camera z=2200`，避免自动取景干扰当前排查。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；执行 `py_compile` 未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 存在且大小约 3.76 MB，无 U+FFFD 替换字符，包含 `if (window.THREE)`、`api.nodeThreeObject((node) =>`、`document.elementFromPoint` 和 3D 专用 `zoomToFit` 规避逻辑。

### 收缩 3D 配置并放宽相机裁剪范围
- 用户提供新诊断：节点 1025、边 1458、canvas 命中正常、`THREE no`、`scene 4`、`render 0`，说明 3D 实例和 canvas 存在，但主页面看不到实际图形。
- 已判断 `scene 4` 是 `3d-force-graph` 顶层 scene 的正常结构，真实节点/边位于内部 forceGraph 对象子树，需递归统计；同时 `camera z=2200` 存在被 Three 相机 far clipping 裁剪的风险。
- 已新增 `configure3dCamera(api)`，显式设置 `camera.near = 0.1`、`camera.far = 10000`，更新投影矩阵，启用 controls 并把 controls target 对准原点。
- 已将 3D 稳定化相机从 `z=2200` 调整为 `z=1500`，并在稳定化时调用 `resumeAnimation()` 和 `refresh()`，确保动画循环恢复。
- 已将 3D 配置收缩到更接近 smoke 示例：移除自定义 `nodeThreeObject()`、`nodeResolution()`、`linkResolution()` 和方向粒子相关配置，只保留背景、节点尺寸、颜色、标签、边颜色、边透明度和交互。
- 已增强 3D 诊断：显示 `far`、递归对象统计 `obj total/mesh/line/points`、controls 开关状态，便于判断对象是否已经创建以及是否被相机裁剪。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；执行 `py_compile` 未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 包含 `camera.far = 10000`、`api.resumeAnimation`、`.nodeRelSize(5.2)` 和递归对象诊断，且无 U+FFFD 替换字符。

### 增加 3D 手动渲染循环
- 用户提供新诊断：`obj 2488/1026/1458/0`，说明 1026 个 mesh 和 1458 条 line 已经创建，canvas、相机、坐标、控制器均正常，但 `render 0` 表示渲染器没有实际绘制场景。
- 已判断当前问题不再是数据量、对象创建、坐标、相机或层叠遮挡，而是 `3d-force-graph` 在主页面组合场景下内部渲染循环或 scene 可见状态没有正常推进。
- 已将 3D 初始化改为 `ForceGraph3D({ waitForLoadComplete: false })(container)`，绕过库内部等待加载完成后才显示 scene 的路径。
- 已新增 `force3dSceneVisible(api)`，强制 `api.scene().visible = true`；3D 诊断新增 `vis on/off` 显示 scene 可见状态。
- 已新增 `render3dFrame(api)` 和 `start3dManualRenderLoop(api)`：当 3D 视图激活时，本页面每帧调用 controls 更新并通过 post-processing composer 或 renderer 直接渲染当前 scene/camera；切回 2D 或实例失活后自动停止。
- 已在 3D 初始化和稳定化步骤调用手动渲染循环，并保留 `resumeAnimation()` 作为库内部循环的补充。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；执行 `py_compile` 未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 包含 `ForceGraph3D({ waitForLoadComplete: false })(container)`、`start3dManualRenderLoop`、`renderer.render(scene, camera)` 和 `vis` 诊断字段，且无 U+FFFD 替换字符。

### 固定 3D 节点位置并同步 Three 对象
- 用户反馈 3D 现在可以显示出来，但所有点都堆在同一个位置。
- 已判断前一轮手动渲染循环只负责把 Three scene 画出来，但没有等价执行库内部 forceGraph tick 位置同步；因此节点对象已可见，但可能仍停留在默认原点。
- 已修改 3D payload：3D 节点不再继承旧位置或等待力模拟展开，而是每次按确定性球面坐标写入 `x/y/z` 和 `fx/fy/fz`，让 3D 初始布局稳定分散。
- 已新增 `sync3dObjectPositions(api)`：手动渲染每帧前递归扫描 scene，把 `__graphObjType === "node"` 的 Three object 位置同步到对应节点的 `x/y/z`；对 link object 尝试同步 geometry position 的起点和终点。
- 已增强 3D 诊断：新增 `objxyz xMin..xMax/yMin..yMax/zMin..zMax`，用于直接观察实际 Three 节点对象是否仍堆叠在同一位置。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；执行 `py_compile` 未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 包含 `sync3dObjectPositions`、`fx/fy/fz` 固定坐标、Three object 位置同步和 `objxyz` 诊断字段，且无 U+FFFD 替换字符。

### 恢复 3D 真实关系布局
- 用户反馈 3D 已能正常显示，但固定球面坐标不是歌手关系图，要求恢复真正的效果。
- 已将 3D 坐标来源从前端球面兜底布局改为导出阶段预计算的关系布局：在 `build_graph_data()` 中按作词/作曲合作边构建无向加权图，边权使用 `log1p(song_count)`，再计算 3D Fruchterman-Reingold spring 坐标。
- 为避免新增 SciPy 依赖，已直接使用 NetworkX 的 dense `_fruchterman_reingold` 计算路径和 `nx.to_numpy_array()`；当前 MVP 约 1210 节点时可在本地环境完成生成，不要求安装 `scipy`。
- 已为每个节点写入 `layout_3d: {x, y, z}`；前端新增 `relationshipPosition3d()`，优先使用 `layout_3d`，仅在缺失时才回退到球面坐标。
- 3D 手动渲染和对象位置同步逻辑保留，用于绕开此前主页面中 `3d-force-graph` 内部渲染/tick 未推进的问题；但同步的坐标现在来自真实关系布局，不再是装饰性球面。
- 已同步 `README.md`，说明 3D 视图使用导出时按合作边权预计算的 3D spring 关系布局。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；执行 `py_compile` 未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 大小约 3.82 MB，1210 个节点均包含 `layout_3d`，坐标范围约 x `-554..613`、y `-820..551`、z `-707..699`，且无 U+FFFD 替换字符。

### 修复 3D 手动渲染下的点击交互
- 用户反馈 3D 与 2D 效果仍不完全一致，且 3D 点击交互不可用。
- 已判断 3D 与 2D 无法做到像素级一致：2D 是浏览器内实时 2D force 布局，3D 当前使用导出阶段预计算的 3D spring 关系布局；但 3D 应复用同一套节点/边详情、高亮和多选交互。
- 由于 3D 当前使用手动渲染和对象位置同步兜底，`3d-force-graph` 内部 raycast 可能与实际可见位置不同步；已新增手动 3D 命中逻辑，绕过内部 raycast。
- 新增 `collect3dNodeObjects()`、`screenPoint3d()`、`distanceToSegment()`、`pick3dGraphItem()` 和 `bind3dManualInteractions()`：点击时把 3D 节点投影到屏幕坐标，优先命中最近节点；未命中节点时按屏幕线段距离命中边；空白区域清空选择。
- 手动 3D 命中复用现有 `handleNodeClick()`、`handleLinkClick()` 和 `handleBackgroundClick()`，因此点击节点、点击边、Ctrl 多选、详情面板和高亮状态与 2D 走同一套逻辑。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；执行 `py_compile` 未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 包含 `bind3dManualInteractions`、`handleNodeClick(picked.item, event)`、`handleLinkClick(picked.item)`，文件大小约 3.83 MB，且无 U+FFFD 替换字符。

### 回退 3D 实验遗留未追踪文件
- 用户反馈 3D 效果不理想，已将除日志外的 Git 跟踪文件回退，并要求清理剩余 Git 未追踪内容，同时记录日志。
- 使用一次性 `git -c safe.directory=D:/B0Projects/my_tools/Musician_Relationship status --short --untracked-files=all` 检查状态，避免修改全局 Git safe.directory 配置；结果只显示 `develop_log.md` 修改，没有普通 untracked 文件。
- 进一步检查本轮 3D 排障期间明确创建过的临时/新增路径：`music_metadata_graph/visualization/vendor/3d-force-graph.min.js` 和 `music_metadata_graph/visualization/vendor/3d-force-graph.LICENSE` 已不存在；`data/visualization_mvp/3d_smoke.html` 仍存在，但被 `.gitignore` 的 `data/` 规则忽略。
- 已在确认目标解析后的绝对路径位于当前工作区内之后，删除临时诊断页 `data/visualization_mvp/3d_smoke.html`。
- 删除后复查 `Test-Path data/visualization_mvp/3d_smoke.html` 返回 `False`；复查 Git 状态仍只显示 `M develop_log.md`，说明剩余可见变更仅为本日志。

### 重新生成已回退源码对应的网页
- 用户反馈网页仍未恢复。
- 已确认当前跟踪源码中不再包含 `ForceGraph3D`、`graph-3d`、`view-mode-toggle`、`3D 视图`、`layout_3d` 或 `3d-force` 等 3D 实验代码，但 `data/visualization_mvp/index.html` 位于被忽略的 `data/` 目录中，Git 回退不会自动恢复该生成产物。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp`，用当前已回退源码覆盖生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认新生成的 `index.html` 大小约 2.41 MB，无 U+FFFD 替换字符，且不包含 `ForceGraph3D`、`graph-3d`、`view-mode-toggle`、`3D 视图`、`layout_3d` 或 `3d-force`。
- 复查 Git 状态仍只显示 `M develop_log.md`，说明剩余可见变更仍仅为本日志。

## 2026-05-16

### 清理 AGENTS 文档异常空行
- 用户指出 `AGENTS.md` 也出现异常，要求检查并修复。
- 复核确认 `AGENTS.md` 主要异常为空行膨胀：清理前文件大小为 89616 字节，共 29832 行，其中非空行 187 行；未发现 `BEL`、垂直制表、换页等隐藏控制字符。
- 本次生成压缩备份 `AGENTS.before_blank_cleanup.md.gz` 后执行机械空行压缩，保留全部 187 行非空内容，并在标题前保留单个空行以维持 Markdown 可读性。
- 清理后 `AGENTS.md` 文件大小为 30374 字节，共 206 行，其中非空行仍为 187 行。
- 验证结果：UTF-8 严格读取成功，隐藏控制字符列表为空，U+FFFD 替换字符数量为 0，未发现三连空行、`<BEL>` 字面标记、`eports/` 或 `ode_modules/` 断行残留。

### 清理 README 文档异常空行
- 用户指出 `README.md` 似乎也有异常，要求检查并修复。
- 复核确认 `README.md` 主要异常为空行膨胀：清理前文件大小为 284028 字节，共 123510 行，其中非空行 501 行；未发现 `BEL`、垂直制表、换页等隐藏控制字符，U+FFFD 替换字符数量为 0。
- 本次生成压缩备份 `README.before_blank_cleanup.md.gz` 后执行机械空行压缩，保留全部 501 行非空内容，并在标题前保留单个空行以维持 Markdown 可读性。
- 清理后 `README.md` 文件大小为 38060 字节，共 526 行，其中非空行仍为 501 行。
- 验证结果：UTF-8 严格读取成功，隐藏控制字符列表为空，U+FFFD 替换字符数量为 0，未发现三连空行、`<BEL>` 字面标记、`eports/`、`ode_modules/`、`ata/` 或 `rchive/` 断行残留。

## 2026-05-17

### 检查并清理 Python 文件异常空行
- 用户指出除文档外代码也似乎有异常，要求检查所有 `.py` 文件。
- 全量扫描所有 `.py` 文件，检查行数与非空行比例、隐藏控制字符、U+FFFD 替换字符、三连空行和异常文件大小；未发现隐藏控制字符或 U+FFFD 替换字符。
- 复核确认只有 `music_metadata_graph/pipelines/filter_imported_songs.py` 呈现明显异常空行膨胀：清理前文件大小为 19555 字节，共 3822 行，其中非空行 253 行，空行比例约 15:1；其它 `.py` 文件未达到同级异常阈值。
- 本次生成压缩备份 `filter_imported_songs.before_blank_cleanup.py.gz` 后，对 `filter_imported_songs.py` 执行机械空行压缩，保留全部 253 行非空代码内容。
- 清理后 `filter_imported_songs.py` 文件大小为 12901 字节，共 495 行，其中非空行仍为 253 行。
- 验证结果：`filter_imported_songs.py` 通过 `py_compile`；全量 `.py` 复扫显示剩余高疑似异常数量为 0；执行 `python -m unittest tests.test_text_normalization tests.test_filter_songs_by_album_type`，共 5 个测试全部通过。

## 2026-05-17

### 复查核心文档异常状态
- 用户要求再次检查 `AGENTS.md`、`README.md`、`develop_log.md` 是否仍有异常。
- 本次使用 Python 严格 UTF-8 读取三个文档，检查文件大小、总行数、非空行数、最大连续空行数、CRLF 与孤立 LF/CR、隐藏控制字符、U+FFFD 替换字符、`<BEL>/<VT>/<FF>` 字面标记和此前出现过的断行污染前缀。
- 复查结果：`AGENTS.md` 为 208 行、189 行非空、最大连续空行 1；`README.md` 为 148 行、102 行非空、最大连续空行 1；`develop_log.md` 为 4226 行、3709 行非空、最大连续空行 1。
- 三个文件均为 CRLF 换行，无孤立 LF/CR，无隐藏控制字符，无 U+FFFD 替换字符，未发现 `eports/`、`ode_modules/`、`ata/`、`rchive/` 等断行残留。
- `develop_log.md` 中存在 2 处 `<BEL>` 字面量，经定位均为此前修复记录中的检查项描述，不是控制字符污染。

### 设计 large-graph 风格可视化页面
- 用户要求新增一个脚本，页面与 MVP 可视化网页一样，但绘图区模仿 force-graph 官方 `example/large-graph/index.html`。
- 目标效果为生成独立 HTML，不覆盖 `data/visualization_mvp/index.html`；用户仍可使用 MVP 的目标歌手筛选、搜索、最小歌曲数、作词/作曲合并、详情栏和明细表，但绘图区改为轻量 2D 圆点和直线布局。
- 实现方案为复用现有 SQLite 图谱数据构建、HTML 外壳和详情逻辑，新增 `music_metadata_graph.visualization.build_large_graph_static`，仅替换前端 `ForceGraph` 初始化、节点 payload 和绘图区说明。
- 风险边界为该页面不加载头像自绘、不显示常驻文字节点、不做预热 tick 和自动 `zoomToFit`，节点名称保留在悬浮提示和详情栏中；本轮不重新引入 3D。

### 实现 large-graph 风格可视化脚本
- 新增 `music_metadata_graph/visualization/build_large_graph_static.py`，默认 `--mvp` 输出到 `data/visualization_mvp_large_graph/index.html`，正式模式输出到 `data/visualization_large_graph/index.html`。
- 将 `html_document()` 扩展为可传入自定义 CSS 和 JS，使新脚本能复用现有页面外壳而不复制整份 HTML 模板。
- large-graph 变体复用 MVP 的数据过滤和详情逻辑，但绘图区使用 `nodeAutoColorBy("large_group")`、默认圆点节点、直线边、内置力布局和按需粒子；移除了头像自绘、节点命中自绘、边自绘、预热 tick、自定义力参数和自动聚焦。
- 已更新 `README.md` 的 MVP 可视化章节，补充新脚本运行命令、默认输出路径和绘图区行为差异。
- 已新增 `tests.test_static_graph_build` 中的 large-graph 变体断言，覆盖轻量绘图区初始化和不包含主 MVP 自绘逻辑的约束。

### 验证 large-graph 风格可视化脚本
- 语法验证对象为 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，执行 `py_compile` 未输出错误。
- 单元测试对象为 `tests.test_static_graph_build`，执行项目指定 Conda Python 运行 7 个测试，结果全部通过。
- 生成验证对象为 MVP 数据库，执行 `python -m music_metadata_graph.visualization.build_large_graph_static --mvp`，输出 `data/visualization_mvp_large_graph/index.html`，统计为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认新 HTML 大小约 2.4 MB，无 U+FFFD 替换字符，包含 `Large-graph 风格合作网络`，且不包含 `.nodeCanvasObject(drawNode)`、`.warmupTicks(` 或 `api.zoomToFit`。
- 尝试使用本机 Chrome 和 Edge 无头模式对本地 `file://` HTML 截图做页面级冒烟检查，但命令未产出截图文件；本轮未完成浏览器视觉截图验证，剩余风险为实际浏览器首屏渲染仍需人工打开确认。
- 已将本轮改动的文本文件统一为 CRLF 行尾，并复跑语法检查、单元测试和 MVP 生成命令。

### 纠正 large-graph 模仿范围
- 用户纠正前一版理解不符合要求：不是在 MVP 页面中保留筛选、详情、头像和高亮后只调整绘图区，而是除允许鼠标交互外，其他应完全模仿 force-graph 官方 `example/large-graph`。
- 已将 `build_large_graph_static.py` 改为生成极简示例式 HTML：页面只包含 `body { margin: 0; }`、`#graph` 容器、`window.devicePixelRatio = 1` 和官方 large-graph 的 `ForceGraph` 链式配置。
- 当前唯一有意差异为将官方示例中的 `.enablePointerInteraction(false)` 改为 `.enablePointerInteraction(true)`，以保留鼠标悬浮、点击和拖拽等交互能力。
- 数据源仍使用项目 SQLite 导出的音乐人节点和关系边，但输出 payload 收缩为示例所需的 `nodes` 与 `links`，不再输出 MVP 的筛选、详情、表格、头像、粒子、高亮、边颜色分职能或自动聚焦逻辑。
- 已同步 `README.md`，明确该页面不包含 MVP 的筛选栏、详情栏、表格、头像节点、粒子、高亮或自动聚焦。
- 已更新单元测试，断言页面包含 `.d3AlphaDecay(0)`、`.d3VelocityDecay(0.08)`、`.cooldownTime(60000)`、`.linkColor(() => 'rgba(0,0,0,0.05)')`、`.zoom(0.05)` 和 `.enablePointerInteraction(true)`，并排除 MVP 外壳和自绘逻辑。

### 验证 large-graph 完全模仿版本
- 语法验证对象为 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，执行 `py_compile` 未输出错误。
- 单元测试对象为 `tests.test_static_graph_build`，执行项目指定 Conda Python 运行 7 个测试，结果全部通过。
- 生成验证对象为 MVP 数据库，执行 `python -m music_metadata_graph.visualization.build_large_graph_static --mvp`，输出 `data/visualization_mvp_large_graph/index.html`，统计为 1970 首歌曲、1210 个节点、2271 条链接。
- 静态检查确认新 HTML 大小约 386 KB，无 U+FFFD 替换字符，页面本体包含官方 large-graph 的核心配置和 `.enablePointerInteraction(true)`，且不包含 `topbar` 或 `detail-panel`。
- 输出 HTML 内仍包含 `nodeCanvasObject`、`linkDirectionalParticles`、`zoomToFit` 等字样，这是内嵌本地 `force-graph.min.js` 运行库自身的 API 名称，不是页面脚本主动调用。

### 再次纠正 large-graph 范围为仅绘图区
- 用户进一步纠正：要求完全模仿的是绘图区，不是整个网页；网页外壳仍应像 MVP 可视化网页。
- 已重新调整 `build_large_graph_static.py`：恢复复用 MVP 的 HTML 外壳、目标歌手筛选、搜索、最小歌曲数、作词/作曲合并、详情栏和明细表，只替换 `#graph` 绘图区的 `ForceGraph` 初始化和 payload。
- 绘图区当前设置 `window.devicePixelRatio = 1`，并使用官方 large-graph 的 `.d3AlphaDecay(0)`、`.d3VelocityDecay(0.08)`、`.cooldownTime(60000)`、`.linkColor(() => 'rgba(0,0,0,0.05)')`、`.zoom(0.05)`；唯一差异仍为 `.enablePointerInteraction(true)`。
- 绘图区不再调用 MVP 的 `.nodeCanvasObject()`、`.nodePointerAreaPaint()`、`.nodeAutoColorBy()`、`.linkCanvasObject()`、`.linkDirectionalParticles()`、`api.zoomToFit()` 或自定义 `api.d3Force()` 配置。
- 点击节点和边仍保留为鼠标交互的一部分，用于更新右侧详情；但绘图区视觉不再随点击执行 MVP 高亮颜色、线宽或粒子变化。
- 已同步 `README.md`，明确该页面保留 MVP 外壳，仅绘图区按 large-graph 示例配置生成。

### 验证绘图区版 large-graph 页面
- 语法验证对象为 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，执行 `py_compile` 未输出错误。
- 单元测试对象为 `tests.test_static_graph_build`，执行项目指定 Conda Python 运行 7 个测试，结果全部通过。
- 生成验证对象为 MVP 数据库，执行 `python -m music_metadata_graph.visualization.build_large_graph_static --mvp`，输出 `data/visualization_mvp_large_graph/index.html`，统计为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认 HTML 无 U+FFFD 替换字符，保留 `topbar`、`detail-panel` 和 `target-dropdown-toggle`，页面脚本包含 large-graph 核心配置和 `.enablePointerInteraction(true)`，不包含 `.enablePointerInteraction(false)`。
- 静态检查确认页面脚本未调用 `.nodeCanvasObject(`、`.nodeAutoColorBy(`、`.linkDirectionalParticles(`、`api.zoomToFit`、`api.d3Force("link")` 或 `api.d3Force("charge")`。

### 修正最近两次提交信息
- 用户指出最近两次提交标题和描述填写异常。
- 复核确认最新提交标题使用中文且无英文描述，前一提交虽然使用英文标题但缺少描述正文，不符合仓库提交规则中“使用英文填写提交标题和描述”的要求。
- 已在本地 `main` 分支重写最近两次提交信息，文件内容树保持不变；当前分支相对 `origin/main` 仍为本地 ahead 状态。
- 修正后的提交标题分别为 `[feat] Add QQ Music pipeline and static graph visualization` 与 `[doc] Record 3D graph rollback and troubleshooting`，并补充了对应英文描述正文。
- 验证对象为最近两次提交元数据，执行 `git log -2 --pretty=fuller`，结果显示两条提交均已使用修正后的英文标题和描述。

### 检查制作人 raw 与补 MID 状态
- 用户要求检查制作人补充情况和 JSON 文件数量。
- 检查对象为正式 raw 目录 `data/raw/qqmusic/song_producer/`、制作人缺 MID 搜索 raw 目录 `data/raw/qqmusic/quick_search_artist_mid/song_credit/`、正式 SQLite 数据库和 MVP SQLite 数据库。
- 统计结果显示制作人接口 raw JSON 共 246166 个，严格 UTF-8 JSON 解析均成功；制作人缺 MID quick_search raw JSON 共 18378 个，严格 UTF-8 JSON 解析均成功。
- 正式 SQLite 数据库当前有 296960 首歌曲，其中 225622 首歌曲存在制作人 raw，71338 首当前歌曲尚无制作人 raw；另有 20544 个制作人 raw 对应的歌曲已不在当前正式 `songs` 表中。
- 正式 SQLite 数据库当前仅有 `albums`、`artists`、`song_singers`、`songs` 四张表，尚无 `song_credit_artists` 表，因此作词/作曲关系尚未导入正式库。
- 解析全部制作人 raw 后观察到 152556 首歌曲包含作词或作曲条目，93610 首歌曲不含作词或作曲条目；作词条目 152653 行，作曲条目 210577 行。
- 解析全部制作人 raw 后观察到作词/作曲缺 MID 条目 131169 行，涉及 68300 首歌曲；这反映 raw 内容中的缺 MID 规模，不等同于已完成补入数据库的数量。
- 正式验证目录中的 `song_producer_missing_mid.csv` 当前有 175 行、138 个唯一名称；该 CSV 是采集脚本运行时重写的视图，当前内容不能代表全部制作人 raw 的缺 MID 规模。
- 正式验证目录中尚不存在 `song_credit_mid_fill.csv`；MVP 验证目录中该 CSV 有 146 行、138 个唯一名称，其中 `matched` 29 行、`db_matched` 8 行、`ambiguous_exact_match` 3 行、`no_singer_candidates` 77 行、`not_matched` 29 行。
- MVP SQLite 数据库已有 `song_credit_artists` 表，共 4644 行，其中作词 2339 行、作曲 2305 行，覆盖 1970 首歌曲，且这 1970 首歌曲均同时具备作词和作曲关系。

### 调高可视化边最低透明度
- 用户要求把图谱边的最低透明度调高到 `0.2`。
- 已修改 MVP 静态可视化的 `edgeAlpha(edge)`，未高亮边的连续透明度范围从 `0.05~1` 调整为 `0.2~1`，公式为 `0.2 + edgeWeightRatio(edge) * 0.8`。
- 高亮边仍固定为不透明 `1`；存在高亮状态时，非高亮边仍按最终透明度乘以 `0.5` 压暗。
- 已同步更新单元测试断言，覆盖新的透明度公式。
- 验证结果：`tests.test_static_graph_build` 共 7 个测试全部通过；`build_static_graph.py` 和 `tests/test_static_graph_build.py` 语法检查通过。
- 已重新生成 `data/visualization_mvp/index.html`，静态检查确认 HTML 包含新公式、不再包含旧 `0.05` 公式，且无 U+FFFD 替换字符。

### 保留可视化筛选切换时的选中状态
- 用户询问切换选项时能否不改变选中状态，或重新恢复选中状态。
- 目标效果为：切换目标歌手筛选、作词/作曲分开、最小歌曲数、搜索、显示名字或粒子效果后，如果原选中的节点或边仍存在于当前图中，则继续保持选中和高亮；如果筛选后对象已经不在当前图中，则自动清除选择。
- 已新增选中恢复逻辑：节点按 `artist:mid` 恢复；边优先按完整边 ID 恢复，职能合并/拆分导致 ID 变化时，按同一对音乐人和职能兼容恢复；合并关系切回作词/作曲分开时，可恢复为同一对音乐人之间对应的多条边。
- 已移除目标歌手勾选、全选、反选、职能分开切换、最小歌曲数和搜索输入中的主动 `clearSelectionHighlight()` 调用，改由重新构图后的恢复逻辑判断是否保留或清除。
- 已更新单元测试断言，覆盖选择恢复函数、单边/多边选中快照和不再主动清空选择的关键路径。
- 验证结果：`tests.test_static_graph_build` 共 7 个测试全部通过；`build_static_graph.py` 和 `tests/test_static_graph_build.py` 语法检查通过。
- 已重新生成 `data/visualization_mvp/index.html`，静态检查确认 HTML 包含选择恢复逻辑，且无 U+FFFD 替换字符。

### 让底部明细跟随选中节点过滤
- 用户要求选中节点后底部详情表也相应过滤，并在底部明细中新增搜索框。
- 目标效果为：未选中节点时底部表格保持原范围；选中单个或多个节点后，歌曲明细只保留这些音乐人在演唱、作词或作曲中参与过的歌曲，且作词、作曲、演唱列只显示被选中的音乐人；关系明细只保留这些音乐人位于来源或目标的方向行。
- 已新增底部独立搜索框 `table-search-input` 和状态 `state.tableSearch`，搜索只作用于当前底部明细的已过滤范围，不触发图谱重绘，也不复用顶部图谱搜索。
- 已新增 `selectedTableNodeIds()`、`songHasAnyPerson()`、`personNamesForTable()` 和 `matchesTableSearch()`，用于把节点选中范围与表格搜索范围拆开处理。
- 已调整 `renderSelection()`，节点点击、多选变化后会同时刷新右侧详情和底部表格。
- 已更新单元测试断言，覆盖底部搜索框、选中节点过滤、关系方向过滤和选中刷新表格的关键逻辑。
- 验证结果：`tests.test_static_graph_build` 共 7 个测试全部通过；`build_static_graph.py` 和 `tests/test_static_graph_build.py` 语法检查通过。
- 已重新生成 `data/visualization_mvp/index.html`，静态检查确认 HTML 包含底部搜索和选中节点过滤逻辑，且无 U+FFFD 替换字符。

### 分析 MVP 可视化后续优化方向
- 用户要求分析当前 MVP 可视化还可以如何优化，并明确先不记录日志；随后用户要求补记本次分析日志。
- 本次分析只读取 `AGENTS.md`、`develop_log.md`、README、可视化源码、测试和本地 MVP 数据状态，未修改可视化代码或生成新的页面产物。
- 当前 MVP 可视化入口为 `python -m music_metadata_graph.visualization.build_static_graph --mvp`，默认输出 `data/visualization_mvp/index.html`；另有 `build_large_graph_static --mvp` 生成绘图区参考 large-graph 示例的独立页面。
- 当前本地 MVP SQLite 数据规模为：`artists` 1839、`albums` 60025、`songs` 1970、`song_singers` 2347、`song_credit_artists` 4644，其中作词 2339、作曲 2305。
- 当前 MVP 图谱生成数据规模为 1210 个节点、2271 条边、1970 首歌曲；边中 1858 条只对应 1 首歌，2 到 4 首歌的边 332 条，5 首及以上的边 81 条。
- 当前 `data/visualization_mvp/index.html` 大小约 2.41 MB，其中内嵌图谱 JSON 约 2.19 MB，force-graph 运行库约 178 KB，说明后续规模扩大时主要体积压力来自重复嵌入的图谱数据。
- 已识别优先优化方向：默认视图应从全量弱关系收敛为更可读的核心网络，例如默认最小歌曲数调高或提供“核心关系/全部关系”模式；边方向应在选中关系时更明确展示“谁给谁作词/作曲”，而不是主要依赖悬浮提示和粒子效果。
- 已识别详情面板优化方向：点击音乐人后应优先展示“谁给 TA 写过歌”“TA 给谁写过歌”“自己演唱且自己作词/作曲的歌”和高频合作对象排行；点击边后应显示总支撑歌曲数、当前展示数量，并支持展开全部和排序。
- 已识别交互优化方向：搜索应从单纯过滤图和表升级为可导航结果列表；目标歌手筛选应区分种子歌手、演唱目标和协作者，避免正式数据扩大后只展示前 10 个目标歌手造成探索范围误解。
- 已识别性能与视觉优化方向：可将图谱数据拆为独立 JSON 或改为 `song_refs + songsById` 减少 HTML 体积；头像加载可优先加载目标歌手、高权重节点、选中节点和邻居节点；布局可引入轻量碰撞力或局部引力以减少大头像节点重叠。
- 风险边界：本次只是分析和方案整理，未执行浏览器视觉验证、未改默认筛选值、未调整数据结构、未改变现有 HTML 入口和用户可见行为。

### 固定底部明细区高度
- 用户指出底部详细区在搜索时高度反复变化，要求固定高度或打开网页时计算后固定。
- 已将 `#table-content` 从 `max-height: 420px` 改为固定 `height: 420px`，保留内部滚动，避免搜索结果变少时底部区域收缩。
- 已更新单元测试断言，覆盖固定高度 CSS，并确认旧 `max-height` 写法不再存在。
- 验证结果：`tests.test_static_graph_build` 共 7 个测试全部通过；`build_static_graph.py` 和 `tests/test_static_graph_build.py` 语法检查通过。
- 已重新生成 `data/visualization_mvp/index.html`，静态检查确认 HTML 包含固定高度、没有旧 `max-height`，且无 U+FFFD 替换字符。

### 修正右侧详情栏高度对齐
- 用户指出右侧详情框高度异常，比左侧绘图框短一段。
- 已将右侧详情栏高度计算从 `图高度 + panel-head.offsetHeight` 的手算方式，改为在设置图区域高度后直接读取左侧 `.graph-panel` 的实际 `getBoundingClientRect().height`。
- 右侧 `.detail-panel` 的 `height` 和 `maxHeight` 现在统一使用左侧图面板实际高度，避免标题栏、边框和盒模型差异造成短一截。
- 已更新单元测试断言，覆盖新的 `.graph-panel` 实际高度读取逻辑，并确认旧的 `panel-head` 手算方式不再存在。
- 验证结果：`tests.test_static_graph_build` 共 7 个测试全部通过；`build_static_graph.py` 和 `tests/test_static_graph_build.py` 语法检查通过。
- 已重新生成 `data/visualization_mvp/index.html`，静态检查确认 HTML 包含新的右侧高度同步逻辑，且无 U+FFFD 替换字符。

### 强化右侧详情栏高度同步
- 用户反馈上一版没有变化，右侧详情框仍然比左侧绘图框短。
- 已把 `.workspace` 从 `align-items: start` 改为 `align-items: stretch`，让桌面端两列先由 CSS 网格天然拉齐高度。
- 已新增 `syncDetailPanelHeight()`，改用左侧 `.graph-panel.offsetHeight` 读取最终布局后的 border-box 高度，同步到右侧详情栏的 `height` 和 `maxHeight`。
- 已在 `renderGraph()` 中立即同步一次，并通过 `requestAnimationFrame(syncDetailPanelHeight)` 在下一帧再同步一次，避免首次渲染时机过早；`ResizeObserver` 回调中也会重新同步。
- 已更新单元测试断言，覆盖 CSS 拉伸、`offsetHeight`、下一帧同步和旧 `panel-head` 手算逻辑移除。
- 验证结果：`tests.test_static_graph_build` 共 7 个测试全部通过；`build_static_graph.py` 和 `tests/test_static_graph_build.py` 语法检查通过。
- 已重新生成 `data/visualization_mvp/index.html`，静态检查确认 HTML 包含强化后的高度同步逻辑，且无 U+FFFD 替换字符。

### 调整顶部工具栏靠下对齐
- 用户指出顶部右侧工具栏应靠下，而不是靠上。
- 已将 `.topbar` 的垂直对齐改为 `align-items: end`，并将 `.toolbar` 设置为 `align-self: end`，使右侧控件与左侧两行标题信息的下沿对齐。
- 已更新单元测试断言，确认顶部不再使用 `align-items: start` 或 `align-items: center`。
- 验证结果：`tests.test_static_graph_build` 共 7 个测试全部通过；`build_static_graph.py` 和 `tests/test_static_graph_build.py` 语法检查通过。
- 已重新生成 `data/visualization_mvp/index.html`，静态检查确认 HTML 包含顶部靠下对齐逻辑，且无 U+FFFD 替换字符。

### 收紧顶部栏底部空白
- 用户指出顶部右侧工具栏下边距过大。
- 原因是 `.topbar` 使用统一 `padding: 16px 22px`，右侧工具栏靠下对齐后，控件下方仍保留 16px 底部内边距。
- 已将顶部栏 padding 改为 `16px 22px 8px`，保留上方留白，同时把底部空白收紧。
- 已更新单元测试断言，覆盖新的顶部栏 padding，并确认旧统一 padding 不再存在。
- 验证结果：`tests.test_static_graph_build` 共 7 个测试全部通过；`build_static_graph.py` 和 `tests/test_static_graph_build.py` 语法检查通过。
- 已重新生成 `data/visualization_mvp/index.html`，静态检查确认 HTML 包含新的顶部栏 padding，且无 U+FFFD 替换字符。

### 调整图标题行和动态图例
- 用户要求左侧图标题区域从两排改成一排，只改排版不改字体字号颜色；右侧图例不要永远显示三项，而是根据作词/作曲是否分开显示两个或一个，合并状态文案写作词/作曲。
- 已给图标题和说明外层增加 `.graph-heading`，使用 `display: flex` 和 `align-items: baseline` 将标题与说明排成同一行，未改原有 `h2` 和说明文字的字号、字重或颜色规则。
- 已将 `renderLegend()` 改为动态渲染：作词/作曲分开时只显示“作词”和“作曲”；合并时只显示一项“作词/作曲”。
- 已移除图例中的“合并”文案。
- 已更新单元测试断言，覆盖单行标题容器、动态图例、分开/合并文案和旧“合并”文案移除。
- 验证结果：`tests.test_static_graph_build` 共 7 个测试全部通过；`build_static_graph.py` 和 `tests/test_static_graph_build.py` 语法检查通过。
- 已重新生成 `data/visualization_mvp/index.html`，静态检查确认 HTML 包含单行标题和动态图例逻辑，且无 U+FFFD 替换字符。

### 明确目标歌手、数据库规模和当前图规模
- 用户指出顶部和图标题区同时出现“全部 10 位目标歌手”“1,839 位库内音乐人”“1,025 个节点”等数字，口径没有说明清楚，容易误解为同一类数量。
- 已明确三个口径：`目标歌手` 表示当前目标歌手筛选范围；`数据库` 表示当前 SQLite 数据库里的歌曲和音乐人总规模；`当前图` 表示当前筛选、最小歌曲数和搜索条件下实际显示的图节点和关系边。
- 顶部摘要改为 `目标歌手：... · 数据库：... 首歌曲 / ... 位音乐人 · 生成于 ...`。
- 图标题说明改为 `目标歌手：... · 当前图：... 个音乐人节点 / ... 条关系边 · ...`。
- 右侧默认详情中的“数据规模”改为“数据库规模”，并将“库内音乐人”改为“数据库音乐人”。
- 已更新单元测试断言，覆盖新文案并确认旧的混合口径文案不再存在。
- 验证结果：`tests.test_static_graph_build` 共 7 个测试全部通过；`build_static_graph.py` 和 `tests/test_static_graph_build.py` 语法检查通过。
- 已重新生成 `data/visualization_mvp/index.html`，静态检查确认 HTML 包含新口径文案，且无 U+FFFD 替换字符。

### 移除顶部摘要中的目标歌手范围
- 用户指出顶部摘要不需要再写“全部 10 位目标歌手”，因为图标题说明里已经写了。
- 已将顶部 `dataset-scope` 文案改为只显示 `SQLite 静态图谱`、数据库歌曲/音乐人规模和生成时间。
- 图标题说明里仍保留 `目标歌手：... · 当前图：...`，作为当前图范围说明。
- 已更新单元测试断言，确认顶部不再包含 `目标歌手：${currentScopeLabel()}`，同时保留数据库摘要和图标题范围文案。
- 验证结果：`tests.test_static_graph_build` 共 7 个测试全部通过；`build_static_graph.py` 和 `tests/test_static_graph_build.py` 语法检查通过。
- 已重新生成 `data/visualization_mvp/index.html`，静态检查确认 HTML 顶部摘要已移除目标歌手范围，且无 U+FFFD 替换字符。

### 分析当前目录结构调整方向
- 用户提出当前目录结构可能存在不合理之处，并询问如何调整。
- 已按协作规则读取 `AGENTS.md`、`develop_log.md`、顶层目录、正式源码目录、测试目录、文档目录、`.gitignore`、`pyproject.toml` 和 README 章节分布。
- 识别到当前主要问题不是单一目录命名，而是职责边界逐渐混杂：`pipelines/` 同时承载采集、入库、过滤、补 MID、编排和 CSV 工具；`data/` 同时承载 raw 缓存、SQLite、validation CSV 和可视化 HTML；README 过长并承担了流程手册、状态说明、归档说明等多种职责。
- 目标效果应是用户从顶层目录能清楚分辨正式源码、命令入口、运行产物、验证产物、可视化产物和历史归档；开发者修改代码时能按领域定位模块，不需要在一个 `pipelines/` 目录中寻找所有行为。
- 实现方案初步建议分为两层：先做文档和目录职责规范，再分批移动低风险模块；优先拆分 `pipelines/` 的内部职责，其次整理 `data/` 产物层级，最后拆分 README。
- 风险边界包括命令入口、测试导入、README 命令示例、AGENTS 项目规则和开发日志历史引用都可能依赖旧路径；目录迁移应避免一次性大改导致验证成本过高。
- 本轮未执行文件迁移、代码改名或清理数据，只形成结构调整建议和风险识别。

### 细化全项目目录交付边界
- 用户进一步指出问题不只在代码目录，而是整个项目目录：最后一步生成网站的代码没有进入主流程，生成的网站又输出到被 `.gitignore` 排除的 `data/` 目录。
- 已核对当前事实：`run_full_pipeline` 默认只运行 1 到 15 个编排步骤，最后一步是 `language=9` 歌曲过滤；静态图谱生成只通过独立入口 `music_metadata_graph.visualization.build_static_graph` 或 `mr-build-static-graph` 手动执行。
- 已核对当前事实：`build_static_graph.py` 的默认输出目录为 `data/visualization`，MVP 输出目录为 `data/visualization_mvp`；`.gitignore` 当前排除整个 `data/` 目录，因此生成的网站不属于仓库交付面。
- 调整后的目标效果应是完整主流程最后明确生成一个可打开、可发布的网站目录；网站生成代码作为正式流程的一部分保留在源码中；网站成品输出到独立的可追踪交付目录，而不是本地数据缓存目录。
- 初步目录方案为保留 `data/` 只承载 raw、SQLite、validation CSV 等本地运行产物；新增或明确 `site/` 作为 GitHub Pages 或本地打开的静态网站成品目录；新增 `web/` 或 `music_metadata_graph/web/` 承载网站模板、样式、脚本和静态资源来源。
- 主流程方案为在现有第 15 步之后增加第 16 步“生成静态网站”，调用当前可视化构建逻辑，默认输出到 `site/`；MVP 流程可输出到 `site_mvp/` 或通过参数指定同一 `site/`，具体取决于后续确认是否需要同时保留正式站和 MVP 站。
- 风险边界包括生成网站可能包含从数据库导出的派生数据，若提交 `site/`，需要确认站点数据体量、隐私边界、第三方数据使用说明和 GitHub Pages 发布方式；若只本地预览，则 `site/` 也可被忽略但不能作为项目交付网站。
- 本轮未执行目录迁移或代码改动，只记录新的整体目录调整方向。

### 移动静态网站生成脚本并调整输出目录
- 用户明确本轮不移动 `data` 目录中的 raw、数据库或其他数据产物，只移动最后一步生成网页的脚本和脚本内默认输出路径。
- 已将正式静态网页生成脚本从 `music_metadata_graph/visualization/build_static_graph.py` 移到 `music_metadata_graph/pipelines/build_static_graph.py`，使其语义上归入流程产物生成步骤。
- 已将该脚本默认输出从 `data/visualization` 改为 `site`，MVP 默认输出从 `data/visualization_mvp` 改为 `site_mvp`。
- 已保留 force-graph vendor 文件在 `music_metadata_graph/visualization/vendor/`，并调整生成脚本中的默认 vendor 路径，避免移动第三方资源。
- 已同步 `pyproject.toml` 的 `mr-build-static-graph` 入口、单元测试导入、large-graph 变体内部导入和 README 中正式静态图谱命令说明。
- 未迁移 large-graph 实验变体的脚本位置或默认输出目录，避免超出用户限定的本轮范围。

### 验证静态网站生成脚本移动
- 语法验证对象为移动后的 `music_metadata_graph/pipelines/build_static_graph.py`、依赖它的 `music_metadata_graph/visualization/build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，执行 `py_compile` 未报错。
- 单元验证对象为静态图谱生成逻辑，执行 `tests.test_static_graph_build`，共 7 个测试全部通过。
- 入口验证对象为移动后的模块路径，执行 `python -m music_metadata_graph.pipelines.build_static_graph --help`，命令正常输出参数帮助。
- 生成验证对象为 MVP 静态网站，执行 `python -m music_metadata_graph.pipelines.build_static_graph --mvp`，输出为 `site_mvp/index.html`，读取结果显示节点 1210 个、边 2271 条、歌曲 1970 首。
- 文件检查确认 `site_mvp/index.html` 存在且大小非零，UTF-8 读取无 U+FFFD 替换字符，并包含 force-graph 运行代码。

### 整理 large-graph 网页生成流程目录
- 用户要求继续整理项目目录，并将 large 图脚本也纳入正式流程，同时 large 图脚本使用完整数据库而不是 MVP 数据库。
- 已将 `music_metadata_graph/visualization/build_large_graph_static.py` 移动为 `music_metadata_graph/pipelines/build_large_graph_static.py`，使标准图和 large 图生成脚本都位于流程目录。
- 已将 force-graph vendor 文件从 `music_metadata_graph/visualization/vendor/` 移动到 `music_metadata_graph/pipelines/vendor/`，并更新标准图生成脚本默认 vendor 路径。
- 已删除不再承载正式内容的 `music_metadata_graph/visualization/` 包目录。
- 已新增命令入口 `mr-build-large-graph-static`，指向 `music_metadata_graph.pipelines.build_large_graph_static:main`。
- 已将一键完整流程默认终点从第 15 步扩展为第 17 步：第 16 步生成标准静态网站，第 17 步生成 large-graph 静态网站。
- 第 17 步固定以 `data/music_metadata_graph.sqlite3` 作为数据库输入，并默认输出到 `site_large/`；即使从 MVP 编排续跑，第 17 步也不会使用 MVP 数据库。
- 已移除 large-graph 生成脚本自身的 `--mvp` 分支；如需临时测试其他数据库或输出目录，只能显式传入 `--db` 和 `--output-dir`。
- 已同步 `run_from_song_tabs` 的默认终点和网站输出参数，使从已有歌曲 Tab 续跑时也能继续生成两个网站。
- 已同步 README 和 AGENTS 中的流程说明、large 图命令和默认输出路径。
- 尝试删除旧 `data/visualization_mvp*` 网页产物目录时被安全策略拦截；由于用户此前明确限制不动 data 侧目录，本轮保留这些旧产物，不再继续清理。

### 验证 large-graph 正式流程接入
- 语法验证对象为 `build_static_graph.py`、`build_large_graph_static.py`、`run_full_pipeline.py`、`run_from_song_tabs.py` 和相关测试文件，执行 `py_compile` 未报错。
- 单元验证对象为静态图谱生成和完整流程编排，执行 `tests.test_static_graph_build` 与 `tests.test_run_full_pipeline`，共 10 个测试全部通过。
- 流程验证对象为从第 16 步续跑到第 17 步，执行 `python -m music_metadata_graph.pipelines.run_full_pipeline --continue-from 16 --stop-after 17 --mvp`。
- 流程验证结果显示第 16 步使用 MVP 数据库生成 `site_mvp/index.html`，第 17 步使用完整数据库 `data/music_metadata_graph.sqlite3` 生成 `site_large/index.html`。
- `site_mvp/index.html` 当前大小约 2.4 MB，`site_large/index.html` 当前大小约 86.9 MB，两个文件均存在且由流程 postcheck 检查为非空、UTF-8 可读并包含 ForceGraph 运行代码。

### 明确标准图谱脚本为通用入口
- 用户提出可以再写一个与 MVP 一样但使用完整数据库的可视化脚本，或者将 MVP 可视化脚本改为根据传参决定使用哪个数据库。
- 复核后确认 `music_metadata_graph.pipelines.build_static_graph` 已具备通用能力：默认读取完整数据库并输出 `site/index.html`，传入 `--mvp` 时读取 MVP 数据库并输出 `site_mvp/index.html`。
- 已将脚本 `--mvp` 帮助文案调整为通用语义，明确默认使用完整数据库和 `site/` 输出目录。
- 已将 README 小节从“MVP 可视化”调整为“标准可视化”，同时列出完整数据库命令和 MVP 命令。
- 已执行 `python -m music_metadata_graph.pipelines.build_static_graph` 生成完整数据库标准图谱，输出为 `site/index.html`，读取结果显示节点 24361 个、边 104473 条、歌曲 77449 首。
- 验证结果显示 `site/index.html`、`site_mvp/index.html` 和 `site_large/index.html` 均存在且大小非零，UTF-8 读取无 U+FFFD 替换字符，并包含 ForceGraph 运行代码。
- 单元验证继续执行 `tests.test_static_graph_build` 与 `tests.test_run_full_pipeline`，共 10 个测试全部通过。

### 修正完整数据库标准图谱目标歌手截断
- 用户指出使用完整数据库时页面仍只显示 10 位歌手，完整数据库应把数据库里的所有关系都可视化出来。
- 问题原因是 `build_static_graph.py` 中 `TARGET_FILTER_LIMIT = 10` 截断了 `targets` 列表，前端默认只选择 `targets` 中的目标歌手，导致完整库页面默认只展示前 10 位目标歌手相关边。
- 已移除目标歌手数量截断，使标准图谱默认包含所有有演唱关系的目标歌手。
- 已新增回归测试，构造 12 位目标歌手的内存数据库，确认 `build_graph_data()` 不再把目标歌手截断为 10 位。
- 已重新生成完整数据库标准图谱 `site/index.html`，内嵌数据检查显示目标歌手 9746 位、节点 24361 个、边 104473 条、歌曲 77449 首。
- 已重新生成 MVP 标准图谱 `site_mvp/index.html`，内嵌数据检查显示目标歌手 260 位、节点 1210 个、边 2271 条、歌曲 1970 首。
- 验证结果显示两个 HTML 文件均 UTF-8 可读、无 U+FFFD 替换字符，并包含 ForceGraph 运行代码。
- 单元验证执行 `tests.test_static_graph_build` 与 `tests.test_run_full_pipeline`，共 11 个测试全部通过。
- 已同步 README 和 AGENTS，明确完整数据库标准图谱不得再限制为前 10 位目标歌手。

### 拆分网站资源并加入头像缓存准备步骤
- 用户指出当前头像图片没有落盘，浏览器可能在完整库可视化时并发请求大量远程头像，并要求在可视化之前、语言过滤之后增加头像请求下载与缓存步骤，同时尽量让数据库导出的图谱数据作为资源加载，而不是塞进单个网页文件。
- 已新增 `music_metadata_graph.pipelines.prepare_static_graph_assets`：从 SQLite 构建可视化图谱数据，复制 force-graph 运行库，按头像 URL 生成本地头像缓存路径，逐个低频下载头像到 `site*/assets/avatars/`，并写入 `assets/avatar-manifest.json`。
- 头像准备脚本支持断点续跑，已存在且状态为 `ok` 的本地头像会复用；下载失败的头像在图谱数据中改为空字符串，页面显示姓名首字占位，不再回退请求远程头像 URL。
- 头像准备脚本提供 `--skip-avatar-download` 和 `--max-avatar-downloads`，用于无网络验证或分批下载，避免一次性强制发起完整库的全部头像请求。
- 标准图谱数据从 HTML 内嵌改为 `assets/graph-data.js` 资源文件，force-graph 运行库从 HTML 内嵌改为 `assets/vendor/force-graph.min.js` 资源文件；`index.html` 只保留页面结构和业务脚本。
- large-graph 页面也改为从 `assets/graph-data.js` 与 `assets/vendor/force-graph.min.js` 加载资源；由于 large-graph 绘图区不使用头像，已清空 large-graph 资源数据中的 `icon` 字段，避免误触发远程头像请求。
- 一键完整流程调整为第 16 步准备标准网站资源、第 17 步生成标准静态网站、第 18 步生成 large-graph 静态网站；`run_from_song_tabs` 同步默认终点为第 18 步。
- 已新增命令入口 `mr-prepare-static-graph-assets`，指向 `music_metadata_graph.pipelines.prepare_static_graph_assets:main`。
- 已同步 README 和 AGENTS，说明标准网站资源目录、头像缓存、图谱数据资源和完整流程步骤。

### 验证网站资源拆分和头像缓存逻辑
- 语法验证对象为资源准备脚本、标准图谱脚本、large-graph 脚本、两个流程编排脚本和相关测试文件，执行 `py_compile` 未报错。
- 单元验证对象为静态图谱生成、外部资源 HTML、目标歌手不截断和完整流程编排，执行 `tests.test_static_graph_build` 与 `tests.test_run_full_pipeline`，共 12 个测试全部通过。
- 无网络资源验证执行 `python -m music_metadata_graph.pipelines.prepare_static_graph_assets --skip-avatar-download`，完整库输出 `site/assets/graph-data.js`、`site/assets/vendor/force-graph.min.js` 和 `site/assets/avatar-manifest.json`；完整库识别 17159 个头像 URL，本次全部按跳过记录，图谱数据中的远程头像 URL 被清空。
- 无网络 MVP 资源验证执行 `python -m music_metadata_graph.pipelines.prepare_static_graph_assets --mvp --skip-avatar-download`，MVP 识别 949 个头像 URL，本次全部按跳过记录，输出资源位于 `site_mvp/assets/`。
- 流程验证执行 `python -m music_metadata_graph.pipelines.run_full_pipeline --continue-from 16 --stop-after 18 --mvp --skip-avatar-download`，第 16 到 18 步全部完成，标准 MVP 网站与 full large-graph 网站均通过 postcheck。
- 文件检查确认 `site/index.html`、`site_mvp/index.html` 和 `site_large/index.html` 不再内嵌全量 `window.GRAPH_DATA`，均引用 `assets/graph-data.js`；三个图谱资源文件均无 U+FFFD 替换字符，且不包含 QQ 音乐远程头像域名。
- 本轮未执行完整头像下载，因为完整库当前识别到 17159 个头像 URL，直接下载会发起大量外部请求；后续可不带 `--skip-avatar-download` 运行资源准备步骤，或用 `--max-avatar-downloads N` 分批低频下载并续跑。

## 2026-05-16

### 增加头像缓存逐行进度和运行日志
- 用户要求头像下载脚本像制作人补充脚本一样每行打印 `[当前/总数]` 进度，并把输出写入运行日志，避免终端内容过长后看不到前面的记录。
- 已将 `music_metadata_graph.pipelines.prepare_static_graph_assets` 接入项目统一 `run_with_log` 运行日志机制，脚本启动时会打印 `run_id` 和 `run_log`，终端输出会同步写入 `logs/runs/prepare_static_graph_assets_*.log`。
- 已为头像缓存处理新增逐 URL 进度输出，状态包括 `cache_hit`、`downloaded`、`failed` 和 `skipped`；下载成功时输出本地保存路径，失败时输出失败原因。
- 已调整跳过判断顺序：显式传入 `--skip-avatar-download` 时，进度原因记录为 `avatar_download_disabled`；只有允许下载但达到 `--max-avatar-downloads` 时才记录 `download_limit`。
- 已同步 README 的标准可视化说明和 AGENTS 项目规则，明确头像准备步骤会逐行输出并进入正式运行日志。

### 验证头像缓存进度和运行日志
- 语法验证对象为头像资源准备脚本和静态图谱测试文件，执行 `py_compile` 未报错。
- 单元验证对象为静态图谱生成、流程编排和头像缓存进度输出，执行 `tests.test_static_graph_build` 与 `tests.test_run_full_pipeline`，共 14 个测试全部通过。
- 实跑验证对象为 MVP 头像资源准备入口，执行 `prepare_static_graph_assets --mvp --skip-avatar-download --max-avatar-downloads 0`，终端输出包含 `run_log=logs/runs/prepare_static_graph_assets_20260516_210805.log`，并逐行打印 `[1/949]` 到 `[949/949]` 的头像处理进度。
- 回读运行日志确认日志首部包含 `run_id`、`run_log`、`run_started_at` 和前几条头像进度，日志末尾包含汇总 JSON、`run_status=completed` 和 `run_log_closing_at`。
- 本轮验证未发起真实头像下载；实跑使用 `--skip-avatar-download`，仅验证逐行输出、日志写入、资源重写和跳过状态。

### 改为共享头像缓存目录
- 用户指出每个网页目录各自下载一份头像数据会造成重复，要求改成共享资源并迁移已有资源。
- 已将头像缓存从站点私有目录改为项目级共享目录：头像文件写入 `site_assets/avatars/`，头像清单写入 `site_assets/avatar-manifest.json`；`site/` 和 `site_mvp/` 仍各自保留自己的 `assets/graph-data.js` 与 `assets/vendor/force-graph.min.js`。
- `prepare_static_graph_assets` 新增 `--avatar-cache-dir` 参数，默认值为 `site_assets`；manifest 中的 `local_path` 改为相对共享缓存目录保存，生成图谱数据时再按站点目录写成 `../site_assets/avatars/...`。
- 一键完整流程和补充分支续跑入口已同步传递共享头像缓存目录，并在网站资源检查中检查 `site_assets/avatar-manifest.json`。
- 已将 `site_assets/` 加入 `.gitignore`，避免共享头像缓存和大量图片进入 Git。
- 已把现有 `site/assets/avatars/` 中的 90 个头像文件移动到 `site_assets/avatars/`，并把 `site/assets/avatar-manifest.json` 与 `site_mvp/assets/avatar-manifest.json` 合并为共享 manifest；合并后 manifest 共 17266 条记录，其中 `ok` 90 条、`skipped` 17176 条。
- 已删除迁移后的旧站点私有 manifest；旧 `site/assets/avatars/` 和 `site_mvp/assets/avatars/` 中已无头像文件。

### 验证共享头像缓存迁移
- 语法验证对象为头像资源准备脚本、完整流程编排、补充分支续跑入口和相关测试文件，执行 `py_compile` 未报错。
- 单元验证对象为静态图谱生成、流程编排和共享头像路径重写，执行 `tests.test_static_graph_build` 与 `tests.test_run_full_pipeline`，共 14 个测试全部通过。
- 资源重写验证分别执行完整库 `prepare_static_graph_assets --skip-avatar-download` 和 MVP `prepare_static_graph_assets --mvp --skip-avatar-download`，均复用共享 manifest 并重写对应站点 `assets/graph-data.js`。
- 迁移检查确认 `site_assets/avatar-manifest.json` 存在，`site_assets/avatars/` 下有 90 个头像文件，旧 `site/assets/avatar-manifest.json` 和 `site_mvp/assets/avatar-manifest.json` 已不存在，旧站点私有头像目录中头像文件数量为 0。
- 图谱数据检查确认 `site/assets/graph-data.js` 和 `site_mvp/assets/graph-data.js` 包含共享头像路径 `../site_assets/avatars/`，不再包含站点私有 `assets/avatars/` 路径，也不包含 QQ 音乐远程头像域名。
- 流程检查执行 `run_full_pipeline --continue-from 16 --stop-after 17 --mvp --skip-avatar-download --dry-run`，第 16 步命令包含 `--avatar-cache-dir site_assets`，postcheck 使用共享 `site_assets/avatar-manifest.json` 并通过。

### 禁用 large 图节点拖动
- 用户要求 large 图禁用拖动节点交互，但保留其他鼠标交互。
- 已在 `music_metadata_graph.pipelines.build_large_graph_static` 的 large 图专用 `ForceGraph` 初始化链中加入 `.enableNodeDrag(false)`，同时保留 `.enablePointerInteraction(true)` 和现有节点点击、边点击、背景点击逻辑。
- 已更新 large 图绘图区说明文案和生成结果摘要，明确 large 图保留鼠标交互但禁用节点拖动。
- 已同步 README 中 large-graph 页面说明，明确仍保留鼠标缩放、平移、节点点击、边点击和空白点击交互，但节点不可拖动。
- 已更新静态图谱测试，断言 large 图脚本包含 `.enableNodeDrag(false)` 且不包含 `.enableNodeDrag(true)`。

### 验证 large 图节点拖动禁用
- 语法验证对象为 `build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，执行 `py_compile` 未报错。
- 专项单元验证对象为 large-graph 变体初始化配置，执行 `tests.test_static_graph_build.StaticGraphBuildTests.test_large_graph_variant_keeps_mvp_shell_but_mirrors_official_drawing_area`，测试通过。
- 静态图谱单元验证执行 `tests.test_static_graph_build`，共 11 个测试全部通过。
- 生成验证执行 `python -m music_metadata_graph.pipelines.build_large_graph_static`，使用完整数据库重新生成 `site_large/index.html`、`site_large/assets/graph-data.js` 和 `site_large/assets/vendor/force-graph.min.js`；输出统计为 24361 个节点、104473 条边、77449 首歌曲。
- 静态检查确认 `site_large/index.html` 包含 `.enableNodeDrag(false)` 和“保留鼠标交互但禁用节点拖动”说明。
- 浏览器验证尝试先打开本地 `file://` 页面，被浏览器安全策略拦截；随后改用绑定 `127.0.0.1` 的临时静态文件服务器访问，浏览器返回 `net::ERR_BLOCKED_BY_CLIENT`，因此本轮未完成实际浏览器拖拽验证，剩余风险为未在浏览器中直接操作确认节点不可拖动。

### 核对第二步歌手列表入库字段
- 用户询问第二步入库的键和未入库的键。
- 已按协作规则读取 `AGENTS.md`、`develop_log.md`，并定位第二步脚本为 `music_metadata_graph/pipelines/import_singer_list_to_db.py`。
- 代码核对显示第二步从 `data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all/` 的 `singerlist[]` 读取歌手行，只保留 `area_id` 可解析为 `0` 或 `1` 的行写入 `artists`。
- `artists` 表当前入库列为 `mid`、`name`、`area_id`、`other_name`、`icon`、`spell`、`raw_json_path`、`raw_page`、`raw_row_index`；其中 `icon` 来自 raw 的 `icon` 或 `singer_pic`，后三个追溯字段由入库脚本根据 raw 文件路径、页码和行号生成。
- 当前 raw 样本共扫描 86 个文件、6803 条歌手行，原始歌手行实际出现键为 `area_id`、`concern_num`、`country`、`country_id`、`id`、`mid`、`name`、`other_name`、`pmid`、`singer_pic`、`spell`、`title`、`trend`、`type`、`uin`。
- 当前 raw 样本中 `area_id in (0, 1)` 的可入库行数为 2119；`area_id` 为 2、3、4、5、6 的行按第二步过滤规则不入库。
- 本轮未修改源码或数据库，仅追加本次字段核对分析记录。

### 核对第一步歌手请求接口
- 用户询问第一步使用的请求接口，以及是否还有其他歌手相关请求接口。
- 已按协作规则读取 `AGENTS.md`、`develop_log.md`，并定位第一步脚本为 `music_metadata_graph/pipelines/collect_singer_list_raw.py`。
- 代码核对显示第一步调用 `client.singer.get_singer_list_index(area, sex, genre, index, page, num)`，对应 `qqmusic-api-python` 中 `music.musichallSinger.SingerList` 模块的 `GetSingerListIndex` 方法；当前默认参数为 `AreaType.ALL`、`SexType.ALL`、`GenreType.ALL`、`IndexType.ALL`，分页大小 80。
- 本地 `qqmusic-api-python` 的 `SingerApi` 还提供 `get_singer_list`、`get_info`、`get_tab_detail`、`get_desc`、`get_similar`、`get_songs_list`、`get_album_list`、`get_mv_list` 等歌手相关方法。
- 当前正式流程中除第一步外，第三步使用 `get_tab_detail(..., TabType.SONG)` 请求歌手主页歌曲 Tab，第四步使用 `get_info(mid)` 补充缺失歌曲歌手信息；`get_album_list` 属于旧专辑来源，当前正式流程已改为从歌曲 album 字段请求专辑详情，不再把歌手专辑列表作为专辑来源。
- 本轮未修改源码或数据库，仅追加本次接口核对分析记录。

### 核对 singer.get_desc 接口含义
- 用户询问 `get_desc` 是什么接口。
- 已核对本地 `qqmusic-api-python` 源码，`client.singer.get_desc(mids)` 对应模块 `music.musichallSinger.SingerInfoInter`、方法 `GetSingerDetail`，请求参数为 `{"singer_mids": mids, "groups": 1, "wikis": 1}`。
- 返回模型为 `SingerDetailResponse`，主体字段是 `singer_list[]`；每个条目包含 `basic_info`、`ex_info`、`wiki`、`group_list`、`photos`、`group_info`。
- `basic_info` 映射字段包括 `singer_id`、`singer_mid`、`name`、`type`、`singer_pmid`、`has_photo`、`wikiurl`；`ex_info` 包含地区、描述文本、标签、身份、乐器、流派、外文名、生日、入驻或出道信息等扩展字段。
- 该接口偏批量歌手详情/百科扩展信息；当前正式流程未使用它，第四步补歌手仍使用 `get_info(mid)` 请求主页头部信息以获取更直接的头像和主页基础字段。
- 本轮未修改源码或数据库，仅追加本次接口核对分析记录。

### 实测前十个歌手的 get_desc 返回结构
- 用户要求对当前库里前 10 个歌手执行一次 `get_desc` 批量详情请求，并说明返回 JSON 结构。
- 已从默认 SQLite `artists` 表按 `rowid` 读取前 10 个歌手：周杰伦、林俊杰、陈奕迅、薛之谦、王力宏、汪苏泷、G.E.M. 邓紫棋、许嵩、孙燕姿、王源。
- 首次请求因沙箱网络权限被拦截，随后按权限规则申请放行后成功访问 `u.y.qq.com/cgi-bin/musicu.fcg`。
- 实际请求使用 `client.singer.get_desc([...])` 并关闭 response model 获取原始 JSON；返回根对象只有 `singer_list`，列表长度为 10。
- 每个 `singer_list[]` 条目包含 `basic_info`、`ex_info`、`wiki`、`group_list`、`pic`、`photos`、`group_info`。
- 本次 10 个样本中 `basic_info` 包含 `singer_mid`、`name`、`type`、`has_photo`、`singer_id`、`singer_pmid`、`wikiurl`；`ex_info` 包含 `area`、`desc`、`tag`、`identity`、`instrument`、`genre`、`foreign_name`、`birthday`、`enter`、`blogFlag`。
- 本次 10 个样本中 `wiki` 为空字符串，`group_list`、`photos`、`group_info` 为空数组，`pic` 下的 `big_black`、`big_white`、`pic` 为空字符串。
- 本轮未修改源码或数据库，仅追加本次真实接口结构观察记录。

### 摸底歌手粉丝量和出道信息接口
- 用户希望了解还有哪些接口能拿歌手信息，重点是歌手出道时间和粉丝量信息。
- 已实测周杰伦样本的 `get_info`、`get_desc`、`get_tab_detail(TabType.WIKI)` 和 `get_singer_list`。
- `get_info(mid)` 的原始响应 `Info.FansNum.Num` 返回粉丝数，本次样本为 50212116；同一响应还包含 `Info.FansNum.HasEntry` 和粉丝榜跳转 URL。`Info.NumButtonList` 与 `Info.MedalListNew` 中还出现“3857万杰迷守护”这类粉丝勋章/守护人数文案，但它不是同一个粉丝数字口径。
- `get_singer_list(area=ALL, sex=ALL, genre=ALL)` 的 `hotlist[]` 和 `singerlist[]` 返回 `concernNum`，本次样本周杰伦为 50212113；该值与 `get_info` 粉丝数接近但存在轻微差异，说明它是另一个关注数/粉丝数快照口径。
- `get_singer_list_index(area=ALL, sex=ALL, genre=ALL, index=ALL)` 是当前第一步使用的完整分页索引接口，但当前已落盘样本中的 `concern_num` 基本为 0，不适合作为粉丝量来源。
- `get_desc(mids)` 理论上有 `ex_info.enter`、`birthday`、`desc` 等字段，但本次前 10 个歌手样本和周杰伦样本中这些字段为空或 0，不能作为稳定出道时间来源。
- `get_tab_detail(mid, TabType.WIKI)` 的 `IntroductionTab.List[].SingerInfoList[].Content` 返回简介文本，周杰伦样本中包含“2000年被吴宗宪发掘，发行首张个人专辑《Jay》”等描述，可人工或规则解析出疑似出道相关时间，但这不是结构化字段，解析结果需要低置信度标记并人工复核。
- 当前结论：粉丝量优先候选为 `get_info.Info.FansNum.Num`，批量列表口径可用 `get_singer_list.concernNum` 做快照；出道时间目前没有确认稳定的结构化接口，最可用来源是 WIKI Tab 简介文本或 `get_desc.ex_info.enter` 这种可能为空的字段。
- 本轮未修改源码或数据库，仅追加本次接口摸底分析记录。

### 对比 get_singer_list 和 get_singer_list_index
- 用户询问 `get_singer_list` 和 `get_singer_list_index` 的区别。
- 已基于本地 `qqmusic-api-python` 源码和前序实测结果对比：`get_singer_list` 对应 `music.musichallSinger.SingerList.GetSingerList`，参数为 `hastag`、`area`、`sex`、`genre`，没有首字母索引参数和显式分页参数；`get_singer_list_index` 对应 `music.musichallSinger.SingerList.GetSingerListIndex`，参数为 `area`、`sex`、`genre`、`index`、`sin`、`cur_page`，用于按索引分页拉取更完整的歌手列表。
- 实测 `get_singer_list(ALL, ALL, ALL)` 返回 `hotlist` 和 `singerlist`，其中样本包含 `concernNum` 粉丝/关注数，适合做热门或批量关注数快照，但不是当前完整歌手索引来源。
- 当前第一步使用 `get_singer_list_index(ALL, ALL, ALL, ALL, page, num)`，已落盘 86 页、6803 条歌手行，适合做完整歌手列表 raw 缓存和第二步入库来源；但当前样本中的 `concern_num` 基本为 0，不适合做粉丝量来源。
- 当前结论：完整覆盖优先用 `get_singer_list_index`；需要热门列表或关注数快照时再评估 `get_singer_list`；两者字段名相近但返回规模、分页能力和字段可用性不同，不能直接互换。
- 本轮未修改源码或数据库，仅追加本次接口差异分析记录。

### 分析批量请求歌手粉丝量方案
- 用户询问如何批量请求粉丝量。
- 基于前序实测，当前可用的高可信粉丝数字段为 `get_info(mid)` 返回的 `Info.FansNum.Num`；该接口业务语义仍是单个歌手 MID 一个请求。
- `qqmusic-api-python` 支持把多个 request 描述符交给 `Client.gather()` 合包执行，因此工程上可以按小批量构造多个 `client.singer.get_info(mid)` 请求，批量发送并逐条解析、逐条缓存。
- 备选接口 `get_singer_list(area, sex, genre)` 可一次返回一批 `concernNum`，但它不是任意 MID 查询接口，覆盖范围更像热门或筛选列表快照；当前第一步 `get_singer_list_index` 的 `concern_num` 基本为 0，不适合做粉丝量来源。
- 若后续落地，应新增粉丝量快照流程，而不是改写 `artists` 主表：raw 缓存按 MID 保存，结构化结果写入独立快照表或导出 CSV，字段至少包含 `artist_mid`、`artist_name`、`fans_num`、`has_entry`、`source_interface`、`raw_json_path`、`fetched_at`。
- 本轮未修改源码或数据库，仅追加本次方案分析记录。

### 分析粉丝量快速补齐混合方案
- 用户追问为什么不先用可一次返回一批歌手的接口快速获取粉丝量，再用另一个接口补剩余。
- 已确认该方向可行：`get_singer_list(area, sex, genre)` 可作为快速覆盖来源，先按返回行的 `singer_mid/mid` 匹配当前 `artists`，写入 `concernNum` 快照；未覆盖的 MID 再用 `get_info(mid)` 的 `Info.FansNum.Num` 按小批量合包补齐。
- 风险边界是两个字段口径不同：`get_singer_list.concernNum` 是列表接口关注数快照，`get_info.FansNum.Num` 是主页粉丝数快照；两者周杰伦样本相差数个计数，不能无来源地混写为同一字段。
- 设计上应在快照表或 CSV 中保留 `source_interface`、`metric_name`、`metric_value`、`raw_json_path`、`fetched_at`，必要时另存 `confidence` 或 `priority`，例如主页 `FansNum.Num` 作为优先口径，列表 `concernNum` 作为快速初值。
- 若后续实现，推荐先做估算或 dry-run：计算 `get_singer_list` 不同筛选组合能命中当前目标 MID 的覆盖率，再决定是否值得发起更多筛选组合请求。
- 本轮未修改源码或数据库，仅追加本次混合方案分析记录。

### 调整粉丝量近似口径判断
- 用户说明当前只需要大概粉丝量，不需要实时精确值，只要两个接口数据差别不大就可以一起使用。
- 用户指出前序周杰伦样本中两个接口只差 3 个粉丝，可能是请求间隔中粉丝数自然增长造成的。
- 已调整判断：对于用户当前需求，可以把 `get_singer_list.concernNum` 和 `get_info.FansNum.Num` 作为同一近似粉丝量指标的不同来源使用。
- 风险边界从“不能混用”调整为“需要先用重叠样本验证误差范围”；若重叠样本的相对误差远小于用户分析粒度，例如远低于 1%，则可以合并成 `fans_num_approx` 供排序、筛选和图谱展示使用。
- 仍建议在底层保留来源字段，因为记录来源成本很低，并且后续发现某个接口异常、缓存为 0 或字段缺失时可以回溯。
- 本轮未修改源码或数据库，仅追加本次口径调整分析记录。

### 复测周杰伦两个粉丝量接口
- 用户要求重新请求周杰伦的两个粉丝量接口。
- 已联网请求 `get_info("0025NhlN2yWrP4")`，完成时间为 2026-05-16T21:20:12Z，返回 `Info.FansNum.Num=50212122`、`Info.FansNum.HasEntry=1`。
- 已随后请求 `get_singer_list(ALL, ALL, ALL)`，完成时间为 2026-05-16T21:20:14Z，在 `singerlist` 中命中周杰伦，返回 `concernNum=50212122`。
- 本次两个接口差值为 0，相对差异为 0；该结果支持当前“大概粉丝量”需求下将两者合并为近似口径使用。
- 本轮未修改源码或数据库，仅追加本次复测记录。

### 设计歌手粉丝量采集插入步骤
- 用户要求在第一步完整歌手列表 raw 之后插入粉丝量请求步骤，后续流程编号顺延，并在歌手入库时把粉丝量一并写入 `artists`。
- 目标效果为：完整流程第 2 步先低成本获取 `area_id in (0, 1)` 目标歌手的近似粉丝量 raw，第 3 步入库时 `artists` 中有可查询的 `fans_num`；后续歌曲 Tab、补 MID、专辑、歌曲、制作人、过滤和网站步骤全部顺延。
- 实现方案确定为：第 2 步先请求 `qqmusic.singer.get_singer_list` 的 `TAIWAN`、`CHINA` 两个 area，从 `concernNum` 快速覆盖当前目标；再扫描第三步入库目标中未覆盖的 MID，用 `qqmusic.singer.get_info` 的 `Info.FansNum.Num` 通过 `Client.gather()` 合包补齐。
- 断点与 raw 规则确定为：列表 raw 写入 `data/raw/qqmusic/singer_fans_list/`，单歌手补齐 raw 写入 `data/raw/qqmusic/singer_fans_info/`，汇总写入 `data/raw/qqmusic/singer_fans_summary.json`；重复运行默认复用已有 JSON，不追求实时更新。
- 风险边界为：两种接口已按周杰伦样本复测为同一粉丝量口径，可用于当前近似分析；仍保留 `fans_source` 和 `fans_raw_json_path` 便于后续排查异常 raw 或字段缺失。

### 实现歌手粉丝量采集和入库
- 新增 `music_metadata_graph.pipelines.collect_singer_fans_raw`，并新增命令入口 `mr-collect-singer-fans-raw`。
- 粉丝量采集脚本默认读取第一步歌手列表 raw，套用当前 `area_id in (0, 1)` 目标规则；MVP 模式只要求前 10 个目标歌手的粉丝量可用。
- 粉丝量采集脚本先请求 `get_singer_list` 的 `TAIWAN`、`CHINA` 两个 area 并立即落盘；对未覆盖目标构造 `get_info(mid)` 请求，按批调用 `Client.gather()`，每批成功后立即逐 MID 写入 raw；批次失败时降级为单个请求，仍失败时保留已成功结果并非零退出。
- `import_singer_list_to_db.py` 新增 `--fans-raw-dir` 参数，默认读取 `data/raw/qqmusic/singer_fans_summary.json`，把 `fans_num`、`fans_source`、`fans_raw_json_path` 合并到第三步入库行。
- `artists` schema 新增 `fans_num`、`fans_source`、`fans_raw_json_path`；既有表会通过迁移添加列，旧 schema 重建和旧 `singers` 表迁移路径同步兼容这些列。
- `import_artists()` 对后续歌曲歌手、制作人和 quick_search 补入的音乐人保持兼容：未提供粉丝量时不覆盖已有 `fans_num`、`fans_source`、`fans_raw_json_path`。
- 修正 `import_singer_list_to_db.run()` 中 SQLite 连接显式关闭，避免 Windows 测试临时数据库文件句柄残留。

### 顺延完整流程编号和文档规则
- `run_full_pipeline` 新增第 2 个编排步骤“歌手粉丝量 raw JSON”，第 3 步变为歌手列表入库，第 4 步变为歌手主页歌曲 Tab raw，后续步骤整体顺延到第 19 步。
- 完整流程新增粉丝量 postcheck：第 2 步检查 `singer_fans_summary.json` 非空且有可用 `fans_num`；第 3 步检查 `artists.fans_num` 列存在且至少有一行粉丝量。
- `run_from_song_tabs` 的起点从旧第 4 步调整为新第 5 步，继续表示从已有歌曲 Tab raw 后的 quick_search 补歌曲歌手缺 MID 开始。
- 已同步 `AGENTS.md`，记录新的第二步粉丝量 raw、第三步带粉丝量入库、后续步骤顺延、MVP 规则、单对象合包请求规则和 `artists` 新字段。
- 已同步 README，新增“步骤二：歌手粉丝量 raw JSON”说明、命令入口、raw 目录、断点规则，并更新一键流程步骤数量、网站生成步骤编号和已有歌曲 Tab 续跑说明。
- 已更新相关 pipeline 命令帮助文案，把歌手列表入库规则从旧 step 2 调整为新 step 3，把歌曲 Tab 目标从旧 step 3 调整为新 step 4。

### 验证歌手粉丝量流程改动
- 语法验证对象为新增粉丝量脚本、歌手入库脚本、完整流程编排、已有歌曲 Tab 续跑入口、相关下游脚本和新增测试文件，执行 `py_compile` 未报错。
- 单元验证执行 `tests.test_run_full_pipeline` 与 `tests.test_import_singer_list_to_db`，共 4 个测试通过；新增测试确认第三步入库能从 `singer_fans_summary.json` 写入 `artists.fans_num`、`fans_source`、`fans_raw_json_path`。
- 全量单元验证执行 `python -m unittest discover tests`，共 23 个测试全部通过。
- 入口验证执行 `collect_singer_fans_raw --help`、`import_singer_list_to_db --help`、`run_full_pipeline --help`，均能正常输出帮助；新增入库入口包含 `--fans-raw-dir` 参数。
- 真实 MVP 烟测执行 `python -m music_metadata_graph.pipelines.collect_singer_fans_raw --mvp`，成功请求 `TAIWAN` 和 `CHINA` 两个列表 raw，MVP 前 10 个目标歌手全部被列表接口覆盖，未触发单歌手补请求，写出 `data/raw/qqmusic/singer_fans_summary.json`。
- 本轮未执行完整 2119 个目标歌手的全量粉丝量补齐；剩余工作是用户确认后运行完整第 2 步和第 3 步，更新正式 SQLite 中的 `fans_num`。

### 修正头像下载有效频率判断
- 用户实测头像缓存步骤约 20 个头像耗时 23 秒，即实际有效频率约为 0.87 个头像/秒。
- 已修正对头像请求频率的理解：`prepare_static_graph_assets` 的 `DEFAULT_REQUEST_DELAY_SECONDS=0.05` 只是两次下载结束后的额外间隔，不等同于完整下载过程的实际请求吞吐；真实频率还包含 DNS、连接、响应和图片读取耗时。
- 当前头像步骤仍与前面 QQ 音乐业务接口限速机制不一致：业务接口使用 `Client(rate=0.5, capacity=1)`，约 2 秒 1 次；头像下载使用串行 `urlopen` 加额外 sleep。
- 当前风险判断调整为：实测约 0.87 个头像/秒不属于先前按 20 个/秒估算的高频，但高于业务接口默认的 0.5 次/秒；完整库上万头像仍应保留断点、上限和可调节延迟。
- 本轮未修改源码，仅记录用户实测数据和频率判断修正。

### 改造头像下载为按启动间隔异步调度
- 用户要求头像下载脚本改为异步方式，每 1 秒发起一个请求，下载耗时不影响后续请求启动间隔。
- 已将 `music_metadata_graph.pipelines.prepare_static_graph_assets` 的头像下载从同步循环改为 `asyncio` 调度：未缓存头像按 `--request-delay` 控制相邻下载任务的启动间隔，下载本身通过线程执行，慢下载不会阻塞后续请求启动。
- 已将默认 `DEFAULT_REQUEST_DELAY_SECONDS` 从 `0.05` 调整为 `1.0`，并将 `--request-delay` 帮助文案改为“头像请求启动最小间隔”，避免继续理解为下载完成后的固定等待。
- manifest 仍由主流程在下载任务完成后统一写入；缓存命中、禁用下载和达到 `--max-avatar-downloads` 上限的 URL 不发起远程请求。
- 由于异步下载完成顺序不再保证等同 URL 顺序，已调整测试只校验每条进度内容和汇总结果，不再依赖完成顺序。
- 已同步 README 和 AGENTS，记录头像准备步骤默认按 1 秒间隔启动未缓存头像下载，下载耗时不阻塞后续请求启动。

### 验证头像异步下载调度
- 语法验证对象为 `prepare_static_graph_assets.py`、`tests/test_static_graph_build.py` 和 `tests/test_run_full_pipeline.py`，执行 `py_compile` 未报错。
- 单元验证对象为静态图谱与头像缓存逻辑，执行 `tests.test_static_graph_build`，共 12 个测试全部通过；新增测试使用模拟慢下载确认下载任务可按启动间隔重叠执行，而不是等待前一个下载完成后再启动下一个。
- 流程编排验证对象为 `tests.test_run_full_pipeline`，共 3 个测试全部通过，确认第 16 步网站资源准备命令仍正确接入完整流程。
- 入口参数验证执行 `python -m music_metadata_graph.pipelines.prepare_static_graph_assets --help`，输出显示 `--request-delay` 为头像请求启动最小间隔参数。
- 本轮验证未发起真实头像下载，异步节奏通过模拟下载单元测试验证。

### 调整头像下载优先级排序
- 用户要求头像请求顺序改为按音乐人相关联行数量排序，即演唱、作词、作曲数量相加后从高到低请求。
- 已修改 `music_metadata_graph.pipelines.prepare_static_graph_assets.collect_icon_urls()`：从图谱节点读取 `sung_song_count`、`lyricist_song_count` 和 `composer_song_count`，按三者之和降序排序头像 URL；分数相同按 URL 字符串排序，保证顺序稳定。
- 如果多个节点共用同一个头像 URL，当前按这些节点中的最高关联数量作为该 URL 的排序分值，避免重复请求同一 URL。
- 已同步 README 和 AGENTS，说明未缓存头像按 `演唱 + 作词 + 作曲` 关联数量从高到低排序。

### 验证头像下载排序调整
- 语法验证对象为 `prepare_static_graph_assets.py` 和 `tests/test_static_graph_build.py`，执行 `py_compile` 未报错。
- 单元验证对象为头像 URL 收集排序、静态图谱和流程编排，执行 `tests.test_static_graph_build tests.test_run_full_pipeline`，共 16 个测试全部通过。
- 新增排序测试覆盖高关联数优先、同分 URL 稳定排序和重复头像 URL 取最高关联数。
- 本轮验证未发起真实头像下载。

### 定位粉丝量缺失歌手
- 用户询问全量粉丝量采集结果中 `covered_fans_num=2117` 相对 `target_singers=2119` 缺失的 2 个歌手是谁。
- 已解析 `data/raw/qqmusic/singer_fans_summary.json` 的 `rows`，确认缺失项为 `TRNOTEARS`（MID `001uzjHC3YbguP`）和 `伍心杰`（MID `004HhqT03L1TVX`）。
- 已检查对应单补 raw JSON，两个文件均存在，路径分别为 `data/raw/qqmusic/singer_fans_info/001uzjHC3YbguP.json` 和 `data/raw/qqmusic/singer_fans_info/004HhqT03L1TVX.json`。
- 两个 raw 的 `Info.FansNum` 均返回 `HasEntry=0`、`Num=0`，因此采集汇总按没有可用粉丝入口处理为 `fans_num=null`。

### 收紧第三步歌手入库粉丝量规则
- 用户要求第三步歌手入库在 `area_id in (0, 1)` 之外增加粉丝数必须有可用数值，并要求数据库粉丝数字段限制非空。
- 已将 `import_singer_list_to_db` 调整为先合并第二步 `singer_fans_summary.json`，再只导入 `area_id in (0, 1)` 且 `fans_num` 可解析为正数的歌手；本地当前 raw 验证结果为 2119 个 area 0/1 歌手中过滤掉 2 个无可用粉丝量歌手，导入目标为 2117 行。
- 已将 `artists.fans_num` schema 改为 `INTEGER NOT NULL DEFAULT 0`，旧 nullable `fans_num` 表会重建迁移，旧 NULL 值迁移为 0；新增 `fans_num` 列时也使用非空默认值。
- `import_artists()` 对新插入但没有粉丝量的后续补入音乐人写入 0 以满足非空约束；对已有正数粉丝量，后续无粉丝量写入不会覆盖正数。
- 一键流程第 3 步 postcheck 已检查 `artists.fans_num` 存在、非空约束生效、没有 NULL 粉丝量，并保留正数粉丝量计数与非正数计数。
- 已同步 `collect_singer_song_tab_raw.resolve_targets()`，使第四步 `--all` 目标范围复用第三步当前入库过滤规则，即同时要求 `area_id in (0, 1)` 和可用正数粉丝量。
- 修正 `collect_singer_song_tab_raw.resolve_targets()` 中 SQLite 连接未显式关闭的问题，避免 Windows 测试临时数据库文件句柄残留。
- 已同步 README 和 AGENTS，记录第三步导入条件、`fans_num` 非空约束、MVP 规则和后续补入音乐人的 0 默认值边界。
- 本轮格式处理过程中发现部分修改文件短暂出现 `CRCRLF` 异常换行，已规范化为标准 CRLF 并重新执行验证。

### 验证第三步粉丝量非空规则
- 语法验证对象为 `import_singer_list_to_db.py`、`run_full_pipeline.py`、相关单元测试文件，执行 `py_compile` 未报错。
- 单元验证执行 `tests.test_import_singer_list_to_db` 和 `tests.test_run_full_pipeline`，共 5 个测试通过；新增测试确认 area 0/1 但无粉丝量的歌手不会导入，`fans_num` 列为非空约束，并确认第四步 `--all` 目标范围会复用第三步粉丝量过滤。
- 全量单元验证执行 `python -m unittest discover tests`，共 24 个测试全部通过。
- 使用当前真实 raw 写入临时 SQLite 验证第三步导入和第四步目标解析结果：`filtered_rows_by_area=2119`、`filtered_out_missing_fans=2`、`imported_rows=2117`、`song_tab_all_targets=2117`、`fans_num` 非空约束生效，临时库中 `fans_num IS NULL` 为 0 且 `fans_num <= 0` 为 0。
- 本轮未改写正式数据库文件；正式库需要用户重新运行第三步入库命令后才会应用新 schema 和新过滤结果。

### 纠正粉丝量数据库非空约束
- 用户纠正粉丝量规则：数据库里的 `artists.fans_num` 不应限制非空，只在第三步导入目标和后续从歌手列表 JSON 解析目标范围时过滤无可用粉丝量的歌手。
- 已撤回 `artists.fans_num` 的 `NOT NULL DEFAULT 0` schema 约束，恢复为可空 `INTEGER`；新增列、旧表迁移和 schema 重建路径均不再把缺失粉丝量写成 0。
- `import_artists()` 恢复为无粉丝量时写入 `NULL`，并在冲突更新时保留已有正数粉丝量。
- 保留第三步导入前的 `area_id in (0, 1)` 加可用正数 `fans_num` 过滤，保留第四步 `--all` 从歌手列表 raw 和粉丝量 summary 解析目标时复用同一过滤规则。
- 已同步 README 和 AGENTS，把 `fans_num` 说明改为可空整数，并说明后续补入音乐人没有粉丝量时保留为空。

### 验证粉丝量可空规则
- 语法验证对象为 `import_singer_list_to_db.py`、`collect_singer_song_tab_raw.py`、`run_full_pipeline.py` 和相关测试文件，执行 `py_compile` 未报错。
- 单元验证执行 `tests.test_import_singer_list_to_db` 与 `tests.test_run_full_pipeline`，共 5 个测试通过；确认第三步会过滤无可用粉丝量歌手，且 `fans_num` 列不再是非空约束。
- 全量单元验证执行 `python -m unittest discover tests`，共 24 个测试全部通过。
- 使用当前真实 raw 写入临时 SQLite 验证：`filtered_rows_by_area=2119`、`filtered_out_missing_fans=2`、`imported_rows=2117`、`song_tab_all_targets=2117`、`fans_num_notnull=0`；第三步初始导入目标均有正数粉丝量。

### 检查正式库粉丝量导入状态
- 用户在正式 SQLite 上运行第三步入库后要求检查数据库状态。
- 已只读检查 `data/music_metadata_graph.sqlite3`，确认数据库存在，包含 `albums`、`artists`、`songs`、`song_singers`、`song_credit_artists` 五张表，外键检查无违规。
- `artists.fans_num` schema 为 `INTEGER` 且 `notnull=0`，符合可空字段规则。
- 当前正式库 `artists` 共 48597 行，其中 2117 行有正数粉丝量，46480 行粉丝量为空，非正数粉丝量为 0。
- 当前 `area_id in (0, 1)` 的歌手共 2119 行，其中 2117 行有正数粉丝量，2 行粉丝量为空；这 2 行为 `TRNOTEARS` 和 `伍心杰`。
- 粉丝量来源分布为列表接口 `qqmusic.singer.get_singer_list.concernNum` 1336 行，单补接口 `qqmusic.singer.get_info.FansNum.Num` 781 行。
- 因本次是在已有正式库上 upsert 第三步结果，第三步过滤无粉丝量歌手不会删除历史已存在的 `TRNOTEARS` 和 `伍心杰` 行，它们仍保留在库中且 `fans_num` 为空。

### 统计正式库粉丝量分布
- 用户要求统计 2117 个正数粉丝量数据的分布。
- 已只读统计 `artists.fans_num > 0` 的 2117 行，确认粉丝量呈明显长尾分布：最小值 2，最大值 50212124，均值约 456068，中位数 21993。
- 分位数结果为：P25=998、P50=21993、P75=248517、P90=931726、P95=2240317、P99=6524408。
- 数量级分桶结果为：1-99 共 150 行，100-999 共 380 行，1000-9999 共 399 行，10000-99999 共 442 行，100000-999999 共 541 行，1000000-9999999 共 195 行，10000000+ 共 10 行。
- 按来源统计：列表接口 1336 行，中位数 139033，最大值 50212124；单补接口 781 行，中位数 482，最大值 3210279。
- 按地区统计：area_id=0 共 336 行，中位数 226664；area_id=1 共 1781 行，中位数 9773。

### 删除正式库无粉丝量歌手及关联行
- 用户要求手动移除正式库中 `TRNOTEARS`（MID `001uzjHC3YbguP`）和 `伍心杰`（MID `004HhqT03L1TVX`），以及连锁相关行。
- 删除前已备份正式 SQLite 到 `data/music_metadata_graph.before_remove_no_fans_artists_20260516_224929.sqlite3`。
- 删除前检查发现两个 artist 直接关联 6 条 `song_singers` 和 6 条 `song_credit_artists`，涉及 6 首歌曲。
- 已在启用 SQLite 外键的事务中先删除这 6 首相关歌曲，再删除两个 artist；由于 `songs` 到 `song_singers`、`song_credit_artists` 配置了级联删除，最终级联减少 `song_singers` 7 行、`song_credit_artists` 13 行。
- 删除后正式库状态为：`artists` 48595 行、`songs` 77443 行、`song_singers` 99555 行、`song_credit_artists` 181371 行。
- 删除后两个目标 MID 在 `artists`、`song_singers`、`song_credit_artists` 中均无残留引用；`area_id in (0, 1)` 的 artist 为 2117 行且全部有正数粉丝量。
- 删除后执行 `PRAGMA foreign_key_check` 无外键违规。

## 2026-05-17

### 检查 MVP 库粉丝量状态
- 用户在运行 `collect_singer_fans_raw --mvp` 和 `import_singer_list_to_db --mvp` 后要求检查 MVP 库粉丝量数据。
- 已只读检查 `data/music_metadata_graph_mvp.sqlite3`，确认数据库存在，包含 `albums`、`artists`、`songs`、`song_singers`、`song_credit_artists` 五张表，外键检查无违规。
- `artists.fans_num` schema 为 `INTEGER` 且 `notnull=0`，符合可空字段规则。
- MVP 库当前 `artists` 共 1839 行，其中 10 行有正数粉丝量，1829 行粉丝量为空，非正数粉丝量为 0。
- MVP 库当前 `area_id in (0, 1)` 的 artist 共 10 行，且全部有正数粉丝量；后续补入 artist 没有地区字段或粉丝量为空符合当前规则。
- 10 个 MVP 初始歌手均来自 `qqmusic.singer.get_singer_list.concernNum`，分别为周杰伦、林俊杰、陈奕迅、薛之谦、王力宏、汪苏泷、G.E.M. 邓紫棋、许嵩、孙燕姿、王源。
- 检查中发现流程风险：`collect_singer_fans_raw --mvp` 当前会写入共享路径 `data/raw/qqmusic/singer_fans_summary.json`，使 summary 只剩 MVP 10 行；如果后续非 MVP 流程从该 summary 解析第三步或第四步目标，会被错误限制为 10 行。该问题尚未修复。

### 检查两个静态网页生成脚本布局复用关系
- 用户询问标准静态网页与 large-graph 静态网页除绘图内容外的布局是否分别写了两套相同实现。
- 已检查 `music_metadata_graph.pipelines.build_static_graph` 和 `music_metadata_graph.pipelines.build_large_graph_static`，确认 HTML 外壳、顶部工具栏、图谱面板、详情面板、歌曲明细和关系明细区域统一由 `build_static_graph.html_document()` 生成。
- `build_large_graph_static` 通过导入并调用同一个 `html_document()` 复用页面布局，只传入 `LARGE_GRAPH_CSS` 和 `LARGE_GRAPH_JS` 替换绘图区样式和绘图逻辑。
- large-graph 脚本当前额外替换 `graphPayload()`、`setupGraph()`、`configureForces()` 和 `renderGraph()`，并在 `CSS` 基础上追加少量 `#graph` 与 canvas 样式；因此不是两套完整布局重复实现，而是共享布局加绘图区差异。
- 本次只做源码阅读和结构确认，未修改网页生成逻辑，也未重新生成站点或运行构建。

### 增加网页目标歌手粉丝量范围筛选
- 用户要求在网页中增加粉丝量筛选条，用两个滑块决定展示的粉丝量范围，并要求目标歌手下拉菜单受该范围影响；初始默认范围为 10 万以上。
- 已将 `build_static_graph` 输出的图谱数据扩展为在 `nodes` 和 `targets` 中带出 `fans_num`，并兼容旧测试库中暂时没有 `artists.fans_num` 列的情况。
- 已在共享网页外壳顶部工具栏增加“目标歌手粉丝”双滑块控件，默认下限为 `100000`，上限为当前目标歌手最大粉丝量；滑块标签按万/亿格式展示。
- 已将 `targetItems()` 改为先按当前粉丝量范围过滤目标歌手，因此目标歌手下拉菜单、全选、反选、当前范围标签、图谱边筛选和歌曲明细均基于粉丝量范围内的目标歌手集合。
- 当前筛选语义限定为“目标歌手粉丝量范围”：作词/作曲补入音乐人没有粉丝量时不会因为缺粉丝量被提前删除，只会随着所选目标歌手的关系进入图谱。
- large-graph 页面继续复用标准页面外壳和筛选逻辑，只替换绘图区配置。
- 已同步 README，说明网页默认显示 10 万以上目标歌手、下拉菜单受粉丝量滑块约束；已同步 AGENTS，记录标准网页和 large-graph 网页必须共享该筛选行为。

### 验证网页粉丝量筛选
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 12 个测试通过；新增断言覆盖 `fans_num` 图谱输出、粉丝量滑块控件和目标歌手过滤函数存在。
- 编排验证执行 `tests.test_run_full_pipeline`，共 3 个测试通过。
- 全量测试执行 `python -m unittest discover tests`，共 25 个测试全部通过。
- 已用禁用头像下载方式重新生成 `site/`、`site_mvp/` 的网站资源和 HTML，并重新生成 `site_large/`；完整站点生成结果为 24357 个节点、104464 条边、77443 首歌，MVP 站点生成结果为 1210 个节点、2271 条边、1970 首歌。
- 文件级验证确认 `site/index.html`、`site_large/index.html` 和 `site_mvp/index.html` 均包含 `fans-min-range`、`fans-max-range` 和“目标歌手粉丝”；`site/assets/graph-data.js` 中 9744 个目标歌手条目均包含 `fans_num` 字段，其中默认 10 万以上范围内有 743 位目标歌手，100 万以上有 205 位目标歌手。
- 尝试用内置浏览器打开 `file://` 页面时被浏览器安全策略拒绝；改用本机临时 HTTP 服务访问 `http://127.0.0.1:8765/index.html` 时又被浏览器环境返回 `ERR_BLOCKED_BY_CLIENT`。已停止临时 HTTP 服务，未继续绕过浏览器策略；本轮实际页面交互验证以静态文件和数据级检查替代。
- 已按项目偏好把本轮修改过的源码、文档、测试和站点文本产物统一为 CRLF 行尾，并检查没有 `CRCRLF` 或残留裸 LF；随后重新执行 `py_compile`、`tests.test_static_graph_build` 和 `python -m unittest discover tests`，结果仍为 25 个测试全部通过。

### 修复粉丝量左滑块被轨道遮盖
- 用户反馈网页粉丝量筛选的左滑块被轨道遮盖。
- 已定位为两个 `range` 输入重叠时，各自浏览器原生轨道都在绘制，后一个滑块轨道会覆盖前一个滑块 thumb。
- 已把粉丝量滑块的可见轨道改为 `.fans-slider-shell::before` 统一绘制，并将两个实际 `input[type="range"]` 的 WebKit 与 Firefox 轨道背景改为透明，只保留 thumb 可见和可拖动。
- 已更新 `tests.test_static_graph_build`，增加对共享轨道伪元素和透明 input 轨道样式的断言。
- 已重新生成 `site/index.html`、`site_mvp/index.html` 和 `site_large/index.html`，使三个现有网页产物都包含该 CSS 修复。
- 验证执行 `py_compile` 覆盖 `build_static_graph.py` 和 `tests/test_static_graph_build.py`，未报错；执行 `tests.test_static_graph_build`，13 个测试通过；执行 `python -m unittest discover tests`，28 个测试全部通过。
- 文件级验证确认 `site/index.html`、`site_large/index.html` 和 `site_mvp/index.html` 均包含 `.fans-slider-shell::before` 和 `background: transparent`。

### 修正粉丝量滑块轨道垂直对齐
- 用户截图反馈粉丝量滑块轨道仍显示异常，轨道线位于滑块圆点上方。
- 已将 `.fans-slider-shell` 高度从 18px 调整为 24px，并将共享轨道改为 `top: 50%` 加 `transform: translateY(-50%)` 垂直居中，避免硬编码 `top: 7px` 与浏览器 range thumb 默认定位不一致。
- 已显式给 range input、WebKit track 和 WebKit thumb 设置 `-webkit-appearance: none`，并清除 input 默认 margin；WebKit thumb 尺寸调整为 16px，`margin-top` 调整为 -6px，使 thumb 中心与 4px 轨道中心线一致。
- 已更新 `tests.test_static_graph_build`，增加对居中轨道、WebKit 外观复位和透明轨道样式的断言。
- 已重新生成 `site/index.html`、`site_mvp/index.html` 和 `site_large/index.html`；第一次生成 large-graph 时 Windows 对 `site_large/assets/graph-data.js` 写入返回一次 `OSError: [Errno 22] Invalid argument`，随后串行重试成功。
- 验证执行 `py_compile` 覆盖 `build_static_graph.py` 和 `tests/test_static_graph_build.py`，未报错；执行 `tests.test_static_graph_build`，13 个测试通过；执行 `python -m unittest discover tests`，28 个测试全部通过。
- 文件级验证确认三个站点 HTML 均包含 `.fans-slider-shell::before`、`top: 50%`、`transform: translateY(-50%)` 和 `-webkit-appearance: none`。

### 修正目标歌手下拉菜单对齐
- 用户截图反馈目标歌手下拉菜单没有和 select 框左侧对齐。
- 已定位为 `target-dropdown-menu` 原本是 `.target-filter` 的绝对定位子元素，`left: 0` 会从“目标歌手”标签左侧开始，而不是从 select 框左侧开始。
- 已将 `target-dropdown-menu` 移入 `.target-select-shell` 内，使菜单和 select 共用同一个定位容器；`.target-dropdown-menu` 保持 `left: 0`，宽度改为 `100%`，`.target-select-shell` 宽度调整为 210px。
- 已更新 `tests.test_static_graph_build`，断言下拉菜单位于 `.target-select-shell` 内，并确认菜单宽度和定位样式。
- 已重新生成 `site/index.html`、`site_mvp/index.html` 和 `site_large/index.html`，使三个现有网页产物都包含对齐修复。
- 验证执行 `py_compile` 覆盖 `build_static_graph.py` 和 `tests/test_static_graph_build.py`，未报错；执行 `tests.test_static_graph_build`，13 个测试通过；执行 `python -m unittest discover tests`，28 个测试全部通过。
- 文件级验证确认三个站点 HTML 均包含 `.target-select-shell`、嵌套的 `target-dropdown-menu`、`.target-select-shell` 210px 宽度，以及菜单 `top: calc(100% + 4px); left: 0; width: 100%;` 样式。

### 拆分正式和 MVP 粉丝量 summary
- 用户指出正式流程和 MVP 流程不应共用同一个粉丝量 summary 文件。
- 已新增统一的 `singer_fans_summary_path()` 路径 helper：正式流程使用 `data/raw/qqmusic/singer_fans_summary.json`，MVP 流程使用 `data/raw/qqmusic/singer_fans_summary_mvp.json`。
- `collect_singer_fans_raw` 已改为按 `--mvp` 写入对应 summary，避免 MVP 运行覆盖正式完整 summary。
- `import_singer_list_to_db` 已改为按 `--mvp` 读取对应 summary；第三步的 area 过滤和可用正数粉丝量过滤规则保持不变，数据库 `fans_num` 仍为可空字段。
- `collect_singer_song_tab_raw --all` 已改为按 `--mvp` 读取对应 summary 来解析第三步目标范围，避免第四步目标被错误限制或放大。
- `run_full_pipeline` 的粉丝量 raw 检查已改为按当前流程模式检查对应 summary，并在检查结果中输出实际 summary 路径。
- 已同步 README 和 AGENTS，记录正式 summary 与 MVP summary 分离，且 MVP 流程不再覆盖正式 summary。

### 验证粉丝量 summary 拆分
- 语法验证执行 `py_compile`，覆盖 `collect_singer_fans_raw.py`、`import_singer_list_to_db.py`、`collect_singer_song_tab_raw.py`、`run_full_pipeline.py` 和相关测试文件，未报错。
- 单元验证执行 `tests.test_import_singer_list_to_db` 与 `tests.test_run_full_pipeline`，共 8 个测试通过；新增测试确认 MVP 入库和 MVP 歌曲 Tab 目标解析读取 `singer_fans_summary_mvp.json`，完整流程 MVP 检查也读取 MVP summary。
- 全量单元验证执行 `python -m unittest discover tests`，共 28 个测试全部通过。
- 真实 MVP 采集验证执行 `collect_singer_fans_raw --mvp`，两个列表 raw 均为 cache hit，写出 `data/raw/qqmusic/singer_fans_summary_mvp.json`，结果为 10 行且 10 个可用粉丝量。
- 真实正式采集验证执行 `collect_singer_fans_raw`，两个列表 raw 均为 cache hit，783 个单歌手补齐 raw 均从缓存读取，写出 `data/raw/qqmusic/singer_fans_summary.json`，结果为 2119 行且 2117 个可用粉丝量。
- 一键流程 dry-run 分别验证 MVP 与正式模式的第 2 到第 3 编排步骤：MVP postcheck 输出 `singer_fans_summary_mvp.json` 且为 10/10，正式 postcheck 输出 `singer_fans_summary.json` 且为 2119/2117；对应数据库检查分别显示 MVP 库 10 个带粉丝量 artist、正式库 2117 个带粉丝量 artist。

### 修复 MVP 网页粉丝量筛选产物
- 用户指出 MVP 网页中新增的粉丝量筛选读不到粉丝量。
- 检查确认 `data/music_metadata_graph_mvp.sqlite3` 中 MVP 初始 10 个 `area_id in (0, 1)` 歌手均有正数 `fans_num`，但当前 `site_mvp/assets/graph-data.js` 是旧生成产物，260 个 target 的 `fans_num` 全部为 `null`。
- 直接调用 `build_graph_data()` 读取 MVP 数据库验证生成逻辑本身正常：260 个 target 中 10 个带 `fans_num`，对应周杰伦、林俊杰、陈奕迅、薛之谦、王力宏、汪苏泷、G.E.M. 邓紫棋、许嵩、孙燕姿、王源。
- 已重新执行 `prepare_static_graph_assets --mvp --skip-avatar-download`，使用当前 MVP 数据库重写 `site_mvp/assets/graph-data.js` 并复用已有头像缓存，未发起新头像下载。
- 已重新执行 `build_static_graph --mvp`，重写 `site_mvp/index.html` 以使用更新后的外部 graph data。
- 重新检查 `site_mvp/assets/graph-data.js`：target 共 260 个，其中 10 个有 `fans_num`，默认 `100000` 以上粉丝量范围内可见 target 为 10 个；节点共 1210 个，其中 10 个带 `fans_num`。
- 单元验证执行 `tests.test_static_graph_build`，共 13 个测试通过。
- 全量单元验证执行 `python -m unittest discover tests`，共 28 个测试全部通过。

### 调整目标歌手下拉菜单为数据库默认顺序
- 用户询问目标歌手下拉菜单排序依据，并要求改成不排序，即使用库里的默认顺序。
- 已修改 `build_static_graph.build_graph_data()`：生成 `targets` 时先读取 `SELECT mid FROM artists` 的默认扫描顺序，再按该顺序输出当前图谱中的目标歌手候选，不再按歌曲数、粉丝量或姓名重新排序。
- 为避免极端情况下目标歌手不在默认 artists 扫描结果中，保留了兜底追加逻辑；正常数据库路径下不会改变目标歌手集合，只改变下拉候选顺序。
- 已更新 `tests.test_static_graph_build`，新增测试确认 `targets` 顺序跟随 `SELECT mid FROM artists` 的数据库默认顺序。
- 已同步 README 和 AGENTS，记录目标歌手下拉菜单候选顺序保留数据库默认扫描顺序，不再按歌曲数或粉丝量排序。
- 已重新生成 `site/`、`site_mvp/` 和 `site_large/` 的当前网页产物与 graph data，使现有页面直接采用新顺序。

### 验证目标歌手下拉默认顺序
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py` 和 `tests/test_static_graph_build.py`，未报错。
- 全量单元验证执行 `python -m unittest discover tests`，共 29 个测试全部通过。
- 数据级验证读取 `site/assets/graph-data.js`、`site_large/assets/graph-data.js` 和 `site_mvp/assets/graph-data.js`，分别解析 `targets[].mid` 并与对应 SQLite 数据库 `SELECT mid FROM artists` 过滤到 target 集合后的顺序逐项比较。
- 验证结果显示完整站点和 large-graph 站点均为 9744 个目标歌手且顺序完全匹配完整数据库默认扫描顺序，MVP 站点为 260 个目标歌手且顺序完全匹配 MVP 数据库默认扫描顺序。

### 改回目标歌手下拉粉丝量排序并简化菜单文本
- 用户要求目标歌手下拉菜单改回按粉丝量排序，同时菜单里除了人名不要写别的。
- 已修改 `build_static_graph.build_graph_data()`：`targets` 按 `fans_num` 从高到低排序，缺粉丝量的目标歌手排在最后；同粉丝量时用姓名和 MID 做稳定兜底。
- 已修改前端 `renderTargetCheckboxes()`，目标歌手下拉菜单项只渲染歌手名，不再显示歌曲数或粉丝量文本。
- 已同步 README 和 AGENTS，记录目标歌手下拉候选按粉丝量降序排列，菜单项文本只显示歌手名。
- 已重新生成 `site/`、`site_mvp/` 和 `site_large/` 的 graph data 与 HTML 页面产物。

### 验证目标歌手粉丝量排序和纯人名菜单
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 14 个测试全部通过；测试覆盖目标歌手按粉丝量降序输出，以及菜单模板不再输出歌曲数或粉丝量。
- 全量单元验证执行 `python -m unittest discover tests`，共 29 个测试全部通过。
- 数据级验证解析 `site/assets/graph-data.js`、`site_large/assets/graph-data.js` 和 `site_mvp/assets/graph-data.js`，确认三者 `targets` 的 `fans_num` 均为降序。
- 完整站点和 large-graph 站点目标歌手数均为 9744，MVP 站点目标歌手数为 260；三个站点前 5 位均为周杰伦、林俊杰、薛之谦、陈奕迅、G.E.M. 邓紫棋，对应粉丝量为 50212124、25620830、25352948、22122379、22091120。
- 文件级验证确认 `site/index.html`、`site_large/index.html` 和 `site_mvp/index.html` 均包含只显示 `item.name` 的目标歌手菜单模板，且不再包含旧的“歌曲数 / 粉丝量”菜单项模板。
- 已按项目偏好把本轮触碰的源码、测试、文档、日志和站点文本产物统一为 CRLF 行尾，并检查没有 `CRCRLF` 或残留裸 LF；随后重新执行 `py_compile` 和 `python -m unittest discover tests`，结果仍为 29 个测试全部通过。

### 保留粉丝量范围外目标歌手勾选状态
- 用户指出粉丝量范围缩小后再调回时，目标歌手下拉筛选应自动恢复此前勾选结果，不能只保持缩小范围后的 5 位。
- 已修改前端筛选状态：`state.selectedTargets` 继续保存全局勾选集合，粉丝量范围只决定当前下拉候选和实际绘图使用的 `activeTargetIds()` 交集。
- `syncSelectedTargetsWithFansRange()` 不再按当前粉丝量范围裁剪勾选集合，只清理不存在于原始目标歌手列表中的无效 ID，因此范围外的既有勾选会被记住。
- 已调整全选和反选按钮：二者只作用于当前粉丝量范围内的目标歌手，同时保留范围外已有勾选记忆。
- 已同步 README 和 AGENTS，记录粉丝量范围变化不得清除范围外目标歌手既有勾选，范围调回后必须恢复此前勾选状态。
- 已重新生成 `site/`、`site_mvp/` 和 `site_large/` 的 HTML 页面产物，使现有页面包含该交互修复。

### 验证粉丝量范围勾选恢复逻辑
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 14 个测试全部通过；新增断言确认存在 `activeTargetIds()`，且不再把 `selectedTargets` 裁剪到当前粉丝量范围。
- 文件级验证确认 `site/index.html`、`site_mvp/index.html` 和 `site_large/index.html` 均包含全局勾选与当前范围交集逻辑，并且不再包含旧的按当前范围裁剪勾选集合的代码。
- 已按项目偏好把本轮触碰的源码、测试、文档、日志和站点文本产物统一为 CRLF 行尾，并检查没有 `CRCRLF` 或残留裸 LF；随后重新执行 `py_compile` 和 `python -m unittest discover tests`，结果为 29 个测试全部通过。

### 调整粉丝量筛选默认下限为 500 万
- 用户要求把网页粉丝量筛选的默认下限从 10 万改为 500 万。
- 已修改 `build_static_graph` 的前端默认状态和滑块初始值：`DEFAULT_FANS_MIN`、`state.fansMin` 和初始 range value 均改为 `5000000`。
- 已同步 README 和 AGENTS，记录标准网页和 large-graph 网页的粉丝量筛选默认范围为 500 万以上。
- 已重新生成 `site/`、`site_mvp/` 和 `site_large/` 的 HTML 页面产物。

### 验证粉丝量默认下限 500 万
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 14 个测试全部通过；测试断言已更新为 `DEFAULT_FANS_MIN = 5000000`。
- 文件级验证确认 `site/index.html`、`site_mvp/index.html` 和 `site_large/index.html` 均包含 `DEFAULT_FANS_MIN = 5000000`、`fansMin: 5000000` 和最低粉丝量滑块初始值 `5000000`。
- 数据级检查显示当前完整站点和 large-graph 默认 500 万以上范围内各有 32 位目标歌手，MVP 站点默认范围内有 10 位目标歌手。

### 增加隐藏叶节点开关
- 用户要求网页增加“隐藏叶节点”开关，效果为隐藏只有一条边的节点；默认状态只在使用完整数据库且绘制完整图时开启，MVP、demo 和 large-graph 均不默认开启。
- 已在共享网页工具栏增加“隐藏叶节点”开关，并在前端状态中新增 `hideLeafNodes`。
- 已新增 `leafNodeIds()`，在当前筛选、搜索、作词/作曲合并状态生成的图上统计每个节点的可见边数；开关开启时隐藏度数为 1 的节点及其相关边。
- 默认值通过 HTML 生成参数注入：标准完整图生成时写入 `hideLeafNodes: true` 且开关 checked；MVP、demo 和 large-graph 生成时写入 `hideLeafNodes: false` 且开关未勾选。
- 已同步 README 和 AGENTS，记录开关语义和默认开启范围。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 HTML 页面产物。

### 验证隐藏叶节点开关
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 15 个测试全部通过；全量单元验证执行 `python -m unittest discover tests`，共 30 个测试全部通过。
- 文件级验证确认 `site/index.html` 包含“隐藏叶节点”、`leafNodeIds()`、`hideLeafNodes: true` 和 checked 状态。
- 文件级验证确认 `site_mvp/index.html`、`site_demo/index.html` 和 `site_large/index.html` 均包含“隐藏叶节点”和 `leafNodeIds()`，但默认状态为 `hideLeafNodes: false` 且开关未勾选。
- 已按项目偏好把本轮触碰的源码、测试、文档、日志和站点文本产物统一为 CRLF 行尾，并检查没有 `CRCRLF` 或残留裸 LF；随后重新执行 `py_compile` 和 `python -m unittest discover tests`，结果为 30 个测试全部通过。

### 调整完整库标准图默认合并作词作曲
- 用户要求完整库的标准图默认关闭“作词/作曲分开”。
- 已将 `html_document()` 的作词/作曲分开默认值改为可注入参数，JS 初始 `roleDisplay` 和 checkbox checked 状态由生成入口统一写入。
- 完整数据库标准图 `site/` 生成时默认写入 `roleDisplay: "merged"`，且“作词/作曲分开”开关未勾选。
- MVP、demo 和 large-graph 页面继续默认写入 `roleDisplay: "split"`，且“作词/作曲分开”开关保持勾选。
- 已同步 README 和 AGENTS，记录完整数据库标准完整图默认关闭“作词/作曲分开”，MVP、demo 和 large-graph 页面默认开启。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 HTML 页面产物。

### 验证作词作曲默认显示模式
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 15 个测试全部通过；新增断言覆盖默认 split/merged 注入和 checkbox 默认状态。
- 文件级验证确认 `site/index.html` 包含 `roleDisplay: "merged"`，且 `role-split-toggle` 未默认 checked。
- 文件级验证确认 `site_mvp/index.html`、`site_demo/index.html` 和 `site_large/index.html` 均包含 `roleDisplay: "split"`，且 `role-split-toggle` 默认 checked。
- 已按项目偏好把本轮触碰的源码、测试、文档、日志和站点文本产物统一为 CRLF 行尾，并检查没有 `CRCRLF` 或残留裸 LF；随后重新执行 `py_compile` 和 `python -m unittest discover tests`，结果为 30 个测试全部通过。

### 设计静态网页 demo 模式
- 用户要求在网页生成脚本中增加 demo 模式：使用完整数据库，但从 MVP 的 10 位目标歌手出发，不只显示 10 位目标歌手，而是追加这 10 位歌手参与的全部边和相连节点。
- 目标效果为用户可运行 `prepare_static_graph_assets --demo` 与 `build_static_graph --demo`，得到 `site_demo/index.html`；页面目标歌手下拉菜单仍围绕 MVP 10 位种子歌手，但图谱展示这些种子歌手作为演唱者、作词人或作曲人参与的全部关系边及邻接音乐人。
- 实现方案为在 `build_static_graph.build_graph_data()` 增加 demo 数据裁剪：从完整库 `artists` 中按第三步/MVP 口径取前 10 个 `area_id in (0, 1)` 且有正数粉丝量的种子歌手，筛出包含任一种子歌手的歌曲，并只保留任一端连接种子歌手的作词/作曲关系边。
- 前端方案为在图谱数据中增加 `target_match_mode`，普通模式继续按边的演唱者端匹配目标歌手，demo 模式改为按边任一端匹配目标歌手，以便展示种子歌手作为作词/作曲人参与的边。
- 风险边界为 demo 种子歌手依赖完整库中 `artists.area_id`、`artists.fans_num`、`raw_page` 和 `raw_row_index` 可用；若完整库缺少足够 10 位 MVP 口径种子歌手，生成脚本应报错而不是静默生成错误页面。
- 本轮不做范围为不改变完整站点、MVP 站点和 large-graph 的默认图谱口径，不把 demo 模式接入完整一键流程的 19 个编排步骤。

### 实现静态网页 demo 模式
- `build_static_graph.py` 新增 `--demo` 参数和 `site_demo/` 默认输出目录；`--demo` 使用完整数据库，且与 `--mvp` 互斥。
- `prepare_static_graph_assets.py` 新增 `--demo` 参数和 `site_demo/` 默认输出目录；demo 资源仍复用共享头像缓存 `site_assets/`，避免重复维护头像。
- `build_graph_data()` 新增 demo 裁剪逻辑，输出 `target_match_mode: incident`；普通模式继续输出 `target_match_mode: target` 并保持既有目标歌手生成方式。
- 前端 `baseEdges()` 在 demo 模式下按边任一端是否命中当前目标歌手筛选；歌曲明细在 demo 模式下按演唱、作词、作曲任一角色命中当前目标歌手筛选。
- 已新增单元测试覆盖 demo 种子歌手只取 MVP 口径前 10 位、保留种子歌手作为演唱者或作词/作曲人参与的边、排除不连接种子歌手的边，并覆盖前端 incident 匹配函数存在。
- 已同步 README 和 AGENTS，记录 `--demo` 入口、`site_demo/` 输出、完整库来源和 demo 的边/节点范围。

### 验证静态网页 demo 模式
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`、`prepare_static_graph_assets.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 15 个测试通过；全量单元验证执行 `python -m unittest discover tests`，共 30 个测试通过。
- 真实数据生成验证执行 `prepare_static_graph_assets --demo --skip-avatar-download`，使用完整数据库写出 `site_demo/assets/graph-data.js` 和站点 vendor 资源；结果为 1213 个节点、1828 条边、2119 首歌、10 位目标歌手，头像 URL 共 950 个，其中 835 个复用缓存、115 个因禁用下载跳过。
- 真实页面生成验证执行 `build_static_graph --demo`，写出 `site_demo/index.html`；返回节点 1213、边 1828、歌曲 2119。
- 数据级检查确认 `site_demo/assets/graph-data.js` 的 `target_match_mode` 为 `incident`，目标歌手为周杰伦、林俊杰、薛之谦、陈奕迅、G.E.M. 邓紫棋、许嵩、汪苏泷、王力宏、孙燕姿、王源；全部 1828 条边都至少有一端连接这 10 位目标歌手，且其中 446 条边为目标歌手作为作词/作曲来源端连接其他演唱者。
- 已按项目偏好把本轮触碰的源码、测试、文档、日志和 demo 站点文本产物统一为 CRLF 行尾，并检查没有 `CRCRLF` 或残留裸 LF；随后重新执行 `py_compile` 和 `python -m unittest discover tests`，结果仍为 30 个测试全部通过。

### 调整图谱空白处取消选中和节点拖动默认行为
- 用户要求完整库标准图也禁用节点拖拽，并把所有图谱的空白处取消选中从左键点击改为右键点击。
- 已在标准静态图生成配置中新增节点拖动默认值注入，完整数据库标准图 `site/` 生成时写入 `.enableNodeDrag(false)`，MVP 和 demo 页面继续写入 `.enableNodeDrag(true)`。
- large-graph 页面保持原有 `.enableNodeDrag(false)`；共享标准图和 large-graph 的空白背景取消选中绑定均从 `.onBackgroundClick()` 改为 `.onBackgroundRightClick()`。
- 已同步 README 和 AGENTS，记录完整库标准图默认禁用节点拖动，以及所有网页使用右键点击图谱空白处取消选中。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 HTML 页面产物。

### 验证图谱右键取消选中和节点拖动默认行为
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 15 个测试全部通过；全量单元验证执行 `python -m unittest discover tests`，共 30 个测试全部通过。
- 文件级验证确认 `site/index.html` 和 `site_large/index.html` 包含 `.enableNodeDrag(false)`、`.onBackgroundRightClick`，且不再包含 `.onBackgroundClick`。
- 文件级验证确认 `site_mvp/index.html` 和 `site_demo/index.html` 包含 `.enableNodeDrag(true)`、`.onBackgroundRightClick`，且不再包含 `.onBackgroundClick`。

### 增加仅显示目标歌手开关
- 用户要求新增“仅显示目标歌手”开关，默认关闭；开启后只显示目标歌手节点，不显示延伸制作人节点。
- 已在网页工具栏增加“仅显示目标歌手”开关，并在前端状态中新增 `onlyTargetNodes: false`。
- 开关开启时，图谱使用当前粉丝量范围和目标歌手勾选得到的 active targets，只保留两端都是当前目标歌手的关系边，同时保留当前目标歌手节点本身。
- 已同步 README 和 AGENTS，记录该开关默认关闭、开启后的节点和关系边范围。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 HTML 页面产物。

### 验证仅显示目标歌手开关
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 15 个测试全部通过；全量单元验证执行 `python -m unittest discover tests`，共 30 个测试全部通过。
- 文件级验证确认四个页面 `site/index.html`、`site_mvp/index.html`、`site_demo/index.html` 和 `site_large/index.html` 均包含“仅显示目标歌手”、`onlyTargetNodes: false`、开关绑定和两端均为目标歌手的边过滤逻辑，且默认未勾选。

### 修正右键取消选中作用范围
- 用户澄清右键取消选中不是只在空白处右键，而是图谱内任何地方右键都取消。
- 已在标准图和 large-graph 初始化链中增加 `.onNodeRightClick()` 与 `.onLinkRightClick()`，并保留 `.onBackgroundRightClick()`；三者都执行 `clearSelectionHighlight()` 和 `renderSelection()`。
- 已更新 README 和 AGENTS，将右键取消选中描述从“图谱空白处”修正为“图谱区域任意位置”。

### 验证右键取消选中作用范围
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 15 个测试全部通过；全量单元验证执行 `python -m unittest discover tests`，共 30 个测试全部通过。
- 文件级验证确认四个页面均同时包含 `.onNodeRightClick`、`.onLinkRightClick` 和 `.onBackgroundRightClick`，且不再包含 `.onBackgroundClick`；“仅显示目标歌手”开关也仍存在并保持默认关闭。

### 修正仅显示目标歌手保留孤立目标节点
- 用户指出“仅显示目标歌手”时应显示全部目标歌手节点，而不是隐藏孤立节点。
- 已调整 `buildGraph()`：在搜索、隐藏叶节点等筛选之后，如果 `onlyTargetNodes` 开启，会再次按当前 active targets 回填节点列表，确保全部当前目标歌手节点保留。
- 关系边仍只保留两端都是当前目标歌手的边；孤立目标歌手没有目标歌手之间关系边时仍作为节点显示。
- 已同步 README 和 AGENTS，把“仅显示目标歌手”的语义修正为显示全部当前目标歌手节点，孤立目标歌手也必须保留。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 HTML 页面产物。

### 验证仅显示目标歌手孤立节点保留
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 15 个测试全部通过；全量单元验证执行 `python -m unittest discover tests`，共 30 个测试全部通过。
- 文件级验证确认四个页面均包含回填目标歌手节点逻辑 `nodes = rawData.nodes.filter((node) => activeIds.has(node.id));`，且“仅显示目标歌手”开关仍默认关闭。

### 调整顶部搜索为选中音乐人
- 用户要求搜索功能改为执行后选中搜到的歌手，除非没搜到。
- 已移除顶部搜索对图谱的实时裁剪状态，不再使用 `state.search` 过滤节点或边。
- 顶部搜索框改为按 Enter 执行；执行时在当前图的可见节点中先精确匹配音乐人名称，再模糊匹配名称，最后匹配 MID。
- 搜到音乐人时写入单节点选中状态并重新渲染，从而高亮该节点和相邻关系；没搜到时直接返回，不改变当前选中状态。
- 已同步 README 和 AGENTS，记录顶部搜索按 Enter 执行、搜到才选中、没搜到不改变当前选择。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 HTML 页面产物。

### 验证顶部搜索选中音乐人
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 15 个测试全部通过；全量单元验证执行 `python -m unittest discover tests`，共 30 个测试全部通过。
- 文件级验证确认四个页面均包含 `runNodeSearch()`、Enter 键触发、`state.selectedNodeIds = new Set([node.id])` 和 `if (!node) return`；同时确认不再包含 `state.search` 和顶部搜索框 input 实时渲染监听。

### 恢复左键空白处取消选中
- 用户要求把空白处左键点击取消选中恢复回来，同时保持任意处右键取消选中功能不变。
- 已在标准图和 large-graph 的 force-graph 初始化链中恢复 `.onBackgroundClick()`，用于左键点击图谱空白处清空选中和高亮。
- 已保留 `.onNodeRightClick()`、`.onLinkRightClick()` 和 `.onBackgroundRightClick()`，因此右键点击节点、边或空白处仍都会取消选中。
- 已同步 README 和 AGENTS，记录左键空白处取消选中与右键图谱区域任意位置取消选中同时存在。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 HTML 页面产物。

### 验证左键空白取消与右键任意取消
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 15 个测试全部通过；全量单元验证执行 `python -m unittest discover tests`，共 30 个测试全部通过。
- 文件级验证确认四个页面均同时包含 `.onBackgroundClick`、`.onNodeRightClick`、`.onLinkRightClick` 和 `.onBackgroundRightClick`。

### 调整搜索多命中全选
- 用户要求搜索框命中多个歌手时选中多个，而不是按某种排序只选中第一个。
- 已将搜索函数从单节点返回改为节点列表返回；搜索仍按精确姓名、模糊姓名、MID 的优先级执行，但同一优先级下所有命中节点都会返回。
- 搜索命中一个节点时保持单节点选中状态；命中多个节点时写入 `state.selectedNodeIds` 集合并设置 `state.selected = { type: "nodes" }`，从而高亮这些节点之间存在的关系。
- 没有命中时仍直接返回，不改变当前选中状态。
- 已同步 README 和 AGENTS，记录顶部搜索命中多个音乐人时必须全部选中。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 HTML 页面产物。

### 验证搜索多命中全选
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 15 个测试全部通过；全量单元验证执行 `python -m unittest discover tests`，共 30 个测试全部通过。
- 文件级验证确认四个页面均包含 `findSearchNodes()`、精确姓名命中列表、模糊姓名命中列表、`state.selectedNodeIds = new Set(nodes.map((node) => node.id))`、多节点选中状态和未命中不改变选择逻辑。

### 调整粉丝量滑块垂直位置
- 用户指出粉丝量筛选滑块在顶部工具栏中视觉位置略微偏下，需要调整控件布局而不是粉丝量默认数值。
- 已在标准静态图模板的 `.fans-slider-shell` 中增加 `margin-top: -3px`，让滑块轨道和手柄整体上移。
- 已同步当前生成产物 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 `index.html`，避免当前打开页面仍显示旧布局。
- 本次改动只影响粉丝量筛选控件的 CSS 垂直位置，不改变筛选默认值、取值范围、事件绑定或图谱数据。

### 验证粉丝量滑块垂直位置调整
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`，未报错。
- 文件级验证确认标准静态图模板和四个当前生成页面均包含 `.fans-slider-shell` 的 `margin-top: -3px`。
- 本次为 CSS 微调，未重新运行全量单元测试；剩余风险是不同浏览器 range 控件渲染可能有细微差异，需要用户在实际页面中目视确认。

### 修正粉丝量滑块手柄对齐方式
- 用户澄清需要调整的是滑块手柄本身相对轨道的位置，而不是整个粉丝量筛选控件区域的位置。
- 已撤销 `.fans-slider-shell` 的外层 `margin-top: -3px`，避免同时移动轨道和手柄。
- 已将 WebKit range 手柄的 `margin-top` 从 `-6px` 调整为 `-8px`，并为 Firefox range 手柄增加 `transform: translateY(-2px)`，让圆形手柄视觉上回到轨道中心线。
- 已同步当前生成产物 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 `index.html`。

### 验证粉丝量滑块手柄对齐方式
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`，未报错。
- 文件级验证确认标准静态图模板和四个当前生成页面均不再包含 `.fans-slider-shell` 的 `margin-top: -3px`，并均包含 WebKit 手柄 `margin-top: -8px` 与 Firefox 手柄 `transform: translateY(-2px)`。
- 本次仍为 CSS 微调，未重新运行全量单元测试；剩余风险是不同浏览器原生 range 控件的垂直基线存在差异，需要在实际页面中目视确认。

### 补充验证粉丝量滑块手柄 CSS
- 补充执行 `tests.test_static_graph_build`，共 15 个测试全部通过。
- 复查测试目录未发现继续断言旧的 WebKit 手柄 `margin-top: -6px`。
- 尝试使用本地 Node 浏览器自动化检查页面渲染时，当前 REPL 环境未能解析 `playwright` 模块；因此本轮未取得浏览器截图验证，仍以代码级和单元测试验证为准。

### 调整粉丝量范围输入控件
- 用户指出粉丝量滑块上方的下限、上限和中间“至”字不应作为一段随数字宽度变化的文本显示，并要求上下限数值支持手动修改。
- 已将粉丝量范围显示拆成固定三列：左侧下限输入框、中间固定“至”、右侧上限输入框，避免上下限数字位数变化导致“至”字横向漂移。
- 上下限输入框支持普通数字、`500万`、`1.2亿` 和 `w` 后缀简写；上限输入框支持 `不限`，会映射为当前粉丝量范围上界。
- 输入框在失焦或按 Enter 时提交，提交后会同步两个滑块、目标歌手下拉菜单和图谱筛选；无效输入会回退到当前有效值。
- 已同步 README 和 AGENTS，记录粉丝量范围既可通过滑块调整，也可直接编辑上下限输入框。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 HTML 页面产物。

### 验证粉丝量范围输入控件
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 15 个测试全部通过；全量单元验证执行 `python -m unittest discover tests`，共 30 个测试全部通过。
- 文件级验证确认四个页面均包含 `fans-min-input`、`fans-max-input`、固定三列 `grid-template-columns: minmax(0, 1fr) 24px minmax(0, 1fr)`、`parseFansInputValue()` 和 `updateFansTextInput()`。
- 浏览器入口验证通过本地预览打开 `site/index.html`，确认粉丝量范围显示为固定三列布局，默认下限为 `500万`、上限为 `不限`；将下限输入为 `1000万` 并按 Enter 后，下限滑块同步为 `10000000`。

### 调整顶部控制区两排布局
- 用户要求把顶部左侧的粉丝量筛选和目标歌手下拉组件移到第二排，搜索框也移到第二排，第一排只保留开关。
- 已将顶部 HTML 结构拆为 `topbar-primary` 和 `toolbar-filter-row`：第一排左侧保留标题和数据库说明，右侧控制区只保留“作词/作曲分开”“显示名字”“粒子效果”“隐藏叶节点”“仅显示目标歌手”五个开关。
- 第二排放置目标歌手粉丝量筛选、目标歌手下拉、最小歌曲数和顶部搜索框；搜索框仍按 Enter 执行选中音乐人，不改变搜索逻辑。
- 已同步 README 和 AGENTS，记录顶部控制区分两排：第一排为图谱显示开关，第二排为筛选、最小歌曲数和搜索框。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 HTML 页面产物；large 页面首次生成时遇到一次 Windows 写入 `site_large/assets/graph-data.js` 的临时异常，重试后成功。

### 验证顶部控制区两排布局
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 15 个测试全部通过；全量单元验证执行 `python -m unittest discover tests`，共 30 个测试全部通过。
- 文件级验证确认四个页面均包含 `topbar-primary`、`toolbar-filter-row`、粉丝量输入框、目标歌手下拉和搜索框，且开关行位于筛选搜索行之前。
- 浏览器入口验证通过本地预览打开 `site/index.html`，确认第一排控制区只有 5 个开关，第二排包含粉丝量筛选、目标歌手下拉、最小歌曲数和搜索框，且第二排位于开关行下方。

### 调整粉丝量筛选为单行布局
- 用户要求粉丝量筛选组件改为单行，格式为“目标歌手粉丝、下限数字、双滑块轨道、上限数字”，删除中间“至”，并询问顶部左下和右上空白来源。
- 已将粉丝量筛选 HTML 改为下限输入框、滑块轨道、上限输入框同一行排列；下限和上限仍可手动编辑，并继续同步滑块、目标歌手下拉和图谱筛选。
- 已删除粉丝量范围中的中间“至”和 `fans-range-separator` 样式，避免控件占用上下两行。
- 顶部布局改为两列两行网格：左侧标题和数据库说明跨两行，右侧第一行为开关，右侧第二行为筛选、最小歌曲数和搜索框；上一版空白的原因是第二排整行右对齐，第一排右侧开关又被标题行高度撑开并底部对齐。
- 已同步 README 和 AGENTS，记录顶部两列两行布局和粉丝量筛选单行布局要求。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 HTML 页面产物。

### 验证粉丝量筛选单行布局
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 15 个测试全部通过；全量单元验证执行 `python -m unittest discover tests`，共 30 个测试全部通过。
- 文件级验证确认四个页面均使用 `topbar-title`、`grid-template-areas`、`fans-min-input`、`fans-slider-shell` 和 `fans-max-input`，且下限输入框、轨道、上限输入框顺序正确；同时确认不再包含 `fans-range-separator` 或中间“至”。
- 浏览器入口验证通过本地预览打开 `site/index.html`，确认粉丝量组件中下限输入框、滑块轨道和上限输入框位于同一行，且中间“至”不存在。

### 禁用 large 图无效开关
- 用户询问 large 图中的“显示名字”和“粒子效果”开关是否无效，并要求如果无效就在 large 图中置灰、不可交互。
- 复核 large 图绘图实现后确认：large 页面替换了标准图的自定义节点绘制和粒子绘制，不调用 `drawNode()`、`drawDirectionalParticles()`、`.nodeCanvasObject()` 或 `.linkCanvasObject()`，因此这两个开关在 large 图绘图区中确实没有效果。
- 已在共享 HTML 模板中增加 large 专用参数，让 `build_large_graph_static` 生成页面时给“显示名字”和“粒子效果”输入框加 `disabled`，并给对应 label 加灰态 `switch-control-disabled` 样式。
- 标准图、MVP 图和 demo 图仍保持这两个开关可交互。
- 已同步 README 和 AGENTS，记录 large-graph 页面中“显示名字”和“粒子效果”开关置灰且不可交互。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 HTML 页面产物。

### 验证 large 图无效开关禁用
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 15 个测试全部通过；全量单元验证执行 `python -m unittest discover tests`，共 30 个测试全部通过。
- 文件级验证确认 `site_large/index.html` 中 `label-toggle` 和 `particle-toggle` 均带 `disabled`，且包含 `switch-control-disabled` 灰态样式；同时确认 `site/`、`site_mvp/` 和 `site_demo/` 中这两个开关仍未禁用。
- 浏览器入口验证通过本地预览打开 `site_large/index.html`，确认“显示名字”和“粒子效果”两个输入框 `disabled=true`，对应控件 class 为 `switch-control switch-control-disabled`，灰态颜色为 `rgb(152, 162, 179)`。

### 调整隐藏叶节点定义
- 用户要求“隐藏叶节点”的叶节点定义改为只跟另一个节点相连的节点，不应受“作词/作曲分开”开关影响。
- 已将前端 `leafNodeIds()` 从统计当前显示边条数改为统计唯一邻居集合；同一对节点即使因为作词、作曲分开显示为多条边，只要唯一邻居只有 1 个，仍会被识别为叶节点。
- 该逻辑继续在当前粉丝量、目标歌手、最小歌曲数等筛选后的图上执行，只改变叶节点判定方式，不改变其他筛选条件。
- 已同步 README 和 AGENTS，将“隐藏叶节点”说明改为隐藏只连接另一个唯一节点的叶节点，并记录该判断不受作词/作曲是否分开影响。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 HTML 页面产物；large 页面首次生成时再次遇到一次 Windows 写入 `site_large/assets/graph-data.js` 的临时异常，重试后成功。

### 验证隐藏叶节点唯一定义
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 15 个测试全部通过；全量单元验证执行 `python -m unittest discover tests`，共 30 个测试全部通过。
- 文件级验证确认四个页面均包含 `const neighbors = new Map()`、`neighbors.get(source).add(target)`、`neighbors.get(target).add(source)` 和 `ids.size === 1`，且不再包含按 `degree === 1` 统计边条数的旧判断。

### 核对当前完整流程和一键入口
- 用户询问当前完整流程是什么，以及一键运行脚本会运行什么。
- 已按项目规则复核 `AGENTS.md`、`develop_log.md` 顶部撰写规则、`music_metadata_graph/pipelines/run_full_pipeline.py`、`music_metadata_graph/pipelines/run_from_song_tabs.py`、`music_metadata_graph/pipelines/defaults.py` 和 `pyproject.toml`。
- 当前完整一键入口为 `python -m music_metadata_graph.pipelines.run_full_pipeline` 或 console script `mr-run-full-pipeline`，默认数据库为 `data/music_metadata_graph.sqlite3`，默认标准网站输出为 `site/`，默认 large-graph 输出为 `site_large/`。
- `run_full_pipeline` 的实际编排包含 19 个步骤，每步执行前后都有检查；任一 raw、CSV、SQLite 外键、过滤约束、网站资源或页面产物检查失败都会停止。
- 另一个入口 `python -m music_metadata_graph.pipelines.run_from_song_tabs` 或 `mr-run-from-song-tabs` 固定从第 5 个编排步骤开始，适用于第 4 步主页歌曲 Tab raw 已有部分落盘后继续跑后续流程。

### 调整专辑类型过滤的孤立歌名保留规则
- 用户要求在“按专辑类型过滤歌曲，只保留 Single、EP、录音室专辑”步骤中增加判断：如果被去掉的歌的 `name` 在库里只有一个则不去掉。
- 已修改 `music_metadata_graph/pipelines/filter_songs_by_album_type.py`，删除条件从“专辑类型不在白名单”调整为“专辑类型不在白名单且同一个 `songs.name` 在当前库里出现不止一首”。
- 已同步 `music_metadata_graph/pipelines/run_full_pipeline.py` 的第十步后置检查，不再要求所有非白名单专辑类型完全消失，而是只检查是否还存在“非白名单且同名多首”的可过滤歌曲。
- 已修正 `filter_songs_by_album_type.run()` 的 SQLite 连接释放方式，避免 Windows 测试中临时数据库文件被未关闭连接占用。
- 已新增 `tests/test_filter_songs_by_album_type.py`，覆盖同名重复歌曲中的非白名单版本会删除、孤立歌名的非白名单歌曲会保留的行为。
- 已同步 README 和 AGENTS 中第十步专辑类型过滤规则说明。

### 验证专辑类型过滤孤立歌名保留规则
- 语法验证执行 `py_compile`，覆盖 `filter_songs_by_album_type.py`、`run_full_pipeline.py`、新增测试和 `tests/test_run_full_pipeline.py`，未报错。
- 定向单元验证执行 `python -m unittest tests.test_filter_songs_by_album_type tests.test_run_full_pipeline`，共 5 个测试全部通过。
- 全量单元验证执行 `python -m unittest discover tests`，共 31 个测试全部通过。
- 首次定向测试在 Windows 临时目录清理 SQLite 文件时出现文件占用错误，原因是测试与被测函数存在未关闭连接；已通过显式关闭连接和修正被测函数连接释放解决。

### 实现显示名字文字透明度权重映射
- 用户要求标准图开启“显示名字”时，名字文字透明度也按节点大小类似规则设置，最终视觉下限为 0.5、上限为 1。
- 已在标准静态图模板中新增 `textNodeOpacity()`，复用当前节点视觉半径从 10 到 65 的权重区间，将文字透明度映射到 0.5 到 1。
- 已调整 `drawTextNode()`，名字文字使用带 alpha 的 `rgba(...)` 绘制；非高亮节点在选中态下仍会降低可见性，但最低透明度保持 0.5。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的当前 HTML 页面产物；large-graph 页面不使用标准图名字绘制，但复用模板产物已同步。
- 已更新 README 和 AGENTS，记录标准图“显示名字”时名字文字透明度按节点权重映射，视觉透明度范围为 0.5 到 1。

### 验证显示名字文字透明度权重映射
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 15 个测试全部通过；全量单元验证执行 `python -m unittest discover tests`，共 30 个测试全部通过。
- 文件级验证确认标准图模板、`site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 页面均包含 `textNodeOpacity()`、0.5 下限计算和带 alpha 的文字 `rgba(...)`。
- 行尾验证确认本轮触碰的 AGENTS、README、标准图模板、测试和四个页面 HTML 没有裸 LF，已统一为 CRLF。
- 尝试使用浏览器自动化打开本地 `file://` 页面做页面级验证时被浏览器安全策略拦截；本轮没有继续绕过该限制，剩余风险是未取得实际浏览器截图验证。

### 纠正显示名字透明度范围语义
- 用户纠正“0.5 到 1”的范围只表示显示名字的默认基础透明度范围，不表示选中高亮淡化后的最终下限。
- 已将 `drawTextNode()` 调整为先用 `textNodeOpacity()` 按节点权重得到 0.5 到 1 的基础透明度；当节点处于淡化状态时，直接乘以淡化系数 `0.65`，淡化后的显示透明度可以低于 0.5。
- 已更新 README 和 AGENTS，将规则表述改为基础文字透明度默认范围为 0.5 到 1，选中高亮导致的淡化状态继续按淡化系数降低。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 页面产物。

### 验证显示名字透明度范围语义纠正
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 15 个测试全部通过；全量单元验证执行 `python -m unittest discover tests`，共 30 个测试全部通过。
- 文件级验证确认标准图模板和四个当前页面均包含 `const opacity = dimmed ? textNodeOpacity(node) * 0.65 : textNodeOpacity(node);`，且测试断言不再允许 `Math.max(0.5, textNodeOpacity(node) * 0.65)` 这种淡化后夹下限逻辑。

### 调整显示名字高亮节点不透明
- 用户要求标准图开启“显示名字”时，选中或高亮的名字节点应像高亮边一样直接调为不透明。
- 已调整 `drawTextNode()` 的透明度优先级：选中或高亮节点文字透明度为 `1`；未高亮节点继续使用基础透明度，淡化状态下继续乘以淡化系数。
- 已更新 `tests/test_static_graph_build.py`，断言文字节点透明度表达式包含 `selected || highlighted ? 1`。
- 已更新 README 和 AGENTS，记录显示名字时选中或高亮节点文字直接不透明，未高亮节点在淡化状态下继续按淡化系数降低。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 页面产物。

### 验证显示名字高亮节点不透明
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py`、`build_large_graph_static.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 15 个测试全部通过；全量单元验证执行 `python -m unittest discover tests`，共 30 个测试全部通过。
- 文件级验证确认标准图模板、四个当前页面、README 和 AGENTS 均包含选中或高亮节点文字不透明的规则。

### 增加选中歌手详情视图控制
- 用户要求选中歌手时在详情栏显示“视图”下拉菜单，默认“全部”，并提供“输入”和“输出”用于分别查看别人给选中歌手作词/作曲、选中歌手给别人作词/作曲的关系。
- 用户要求选中两名及以上歌手时在详情栏增加“边关系”下拉菜单，默认“交集”，并可切换“并集”以高亮显示所有选中节点的相关边及相连节点。
- 已在详情栏标题行加入 `detail-controls` 容器，并在选中节点时动态渲染“视图”下拉菜单；多选节点时额外渲染“边关系”下拉菜单。
- 已将选中节点高亮逻辑抽为 `selectedNodeHighlightEdges()`：单选节点始终按相关边高亮；多选节点默认只高亮选中节点之间的关系，切换“并集”后高亮任一选中节点相关边及相连节点。
- 已按边方向数据实现“输入/输出”过滤，其中图谱关系口径仍为“作词/作曲人 -> 演唱者”；详情栏的关系明细和支撑歌曲列表与当前视图、边关系模式保持一致。
- 已同步 README 和 AGENTS，记录选中歌手详情栏的“视图”和“边关系”下拉菜单行为。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的当前 HTML 页面产物。

### 验证选中歌手详情视图控制
- 语法验证执行 `py_compile`，覆盖 `build_static_graph.py` 和 `tests/test_static_graph_build.py`，未报错。
- 单元验证执行 `tests.test_static_graph_build`，共 15 个测试全部通过；全量单元验证第一次执行时，既有头像下载间隔测试因浮点边界出现 `0.014999999999...` 与 `0.015` 的精度差异失败，未做代码修改后立即重跑，全量 30 个测试全部通过。
- 文件级验证确认 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 页面均包含 `detail-controls`、`selected-node-view`、`selected-edge-mode`、默认 `selectedNodeView: "all"`、默认 `selectedEdgeMode: "intersection"`、`selectedNodeHighlightEdges()` 和 `edgeConnectsOnlySelectedNodes()`。
- 浏览器入口验证通过本地预览打开 `site/index.html`，确认页面标题为“音乐人合作关系图谱”，图谱 canvas 存在，详情栏控件容器存在，生成 HTML 中包含“视图”和“边关系”下拉菜单模板。

### 重写 README 为用户项目介绍
- 用户要求 README 应介绍项目给用户，而不是介绍开发状态和开发细节。
- 已将 README 从流程步骤、当前状态、归档说明和底层表结构说明，改写为面向用户的项目介绍。
- 新 README 主要说明项目用途、适用和不适用场景、快速开始、图谱打开方式、网页交互、常用命令、输出内容、数据口径、项目结构和注意事项。
- README 保留必要运行入口和数据边界说明，但不再把历史归档、逐步开发状态和细节流水账作为正文主体。
- 本次只修改用户文档和开发日志，未修改采集流程、数据库逻辑、测试代码或生成网页产物。

### 验证 README 用户介绍改写
- 文件级检查确认 README 不再包含“当前状态”“步骤一”“步骤二”“步骤三”“归档内容”“重新设计”“开发阶段”“当前已确认”等开发状态和流程日志式标题或措辞。
- UTF-8 回读 README，确认主要章节包括项目介绍、使用场景、快速开始、打开图谱、常用命令、输出内容、数据口径、项目结构和注意事项。
- 本次为纯文档改写，未运行单元测试或生成图谱；剩余风险是 README 中命令说明依赖当前 pipeline 入口继续保持兼容。

### 分析 GitHub Pages 头像资源发布策略
- 用户指出头像资源被 `.gitignore` 排除后，GitHub Pages 打开页面没有头像；若提交头像资源，当前本地头像缓存约 17744 个文件、442 MB。
- 已检查当前站点产物，`site/assets/graph-data.js` 中节点 `icon` 已被重写为 `../site_assets/avatars/...` 本地相对路径；而 `.gitignore` 明确排除 `site_assets/`，因此远端 Pages 上头像路径会缺失。
- 已核对 GitHub Pages 官方限制：Pages 源仓库推荐不超过 1 GB，发布站点不超过 1 GB，软带宽限制为每月 100 GB；Git LFS 官方说明不能用于 GitHub Pages 站点。
- 初步判断不应把完整头像缓存直接提交到当前主仓库；这会显著膨胀仓库和 Pages 站点体积，且未来每次头像缓存变化都会制造大量二进制变更。
- 建议方向为把头像发布策略从“全量本地缓存必需”拆成两层：GitHub Pages 默认使用数据库中的远程头像 URL 或缺省头像兜底；如需稳定展示，再生成一个受限发布头像集，只包含默认页面或 demo 页面真正需要的高价值节点缩略图。
- 风险边界为直接使用远程头像 URL 可能受第三方防盗链、跨域、失效或限流影响；发布缩略图集则需要新增压缩、筛选和体积预算规则，并避免把完整缓存误提交。
- 本轮只完成策略分析和事实记录，未修改头像生成脚本、`.gitignore` 或站点产物。

### 纠正远程头像 URL 兜底的并发风险
- 用户指出几千个节点同时请求远程头像资源会形成高并发。
- 已检查当前前端头像加载逻辑，`getNodeImage()` 在首次绘制带 `node.icon` 的节点时创建 `new Image()` 并立即设置 `image.src`；如果 `icon` 改为远程 URL，完整图首轮绘制可能触发大量浏览器并发图片请求。
- 已纠正策略判断：远程头像 URL 不能作为完整图默认裸兜底；若使用远程 URL，必须配合懒加载、并发队列、只加载选中/高亮/当前视口/高权重节点等限制。
- 更稳妥的发布策略调整为：GitHub Pages 默认使用受限发布头像缩略集和缺省头像；远程 URL 只作为手动补载或小规模 demo 的兜底，不在完整图首屏批量触发。
- 本轮只完成风险纠正和事实记录，未修改前端头像加载代码。

### 分析完整头像压缩上传方案
- 用户询问是否存在压缩解压或高效存储格式，可以把完整头像都上传到 GitHub Pages 使用。
- 已识别关键约束：GitHub 普通文件超过 50 MiB 会警告、超过 100 MiB 会阻止；GitHub Pages 源仓库和发布站点推荐不超过 1 GB；静态 Pages 没有服务端解压能力。
- 判断普通 ZIP、tar、zstd 等整包压缩不适合网页首屏使用：浏览器端必须先下载整包并在客户端解压，无法像普通图片 URL 一样按需随机加载，且单包容易触碰 GitHub 单文件上限。
- 判断 Git 自身压缩和 ZIP 对现有 JPEG、PNG、WebP 头像收益有限，无法解决大量二进制文件造成的仓库历史膨胀、Pages 请求数量和浏览器加载压力。
- 可行方向为把“完整头像”转成发布专用缩略图资产，而不是上传原始缓存：统一缩放到 64/96/128px，重编码为 WebP 或 AVIF，并可进一步打包为多张 sprite atlas 加 manifest，页面按需加载 atlas 并从画布裁切绘制。
- 风险边界为 sprite atlas 方案需要新增生成脚本、manifest 数据结构、前端裁切绘制逻辑和按需加载策略；若仍在完整图首屏绘制全部节点头像，体积和并发问题只会从“很多小文件”变成“若干大图集”。
- 本轮只完成方案分析，未修改资源生成和网页渲染逻辑。

### 设计 150 像素头像图集发布方案
- 用户确认可新增建议依赖库，要求小于 150 像素头像采用合适过采样且无需标记，处理后图片另设目录不覆盖原图，并询问扩展名不一致是否需要先修、前端是否可一次性加载图集甚至内嵌网页。
- 已检查当前项目依赖，`pyproject.toml` 尚未包含图像处理库；本机目标 Conda 环境当前没有 Pillow，但系统可用 `ffmpeg` 且包含 WebP 编码能力。
- 设计建议新增 `Pillow` 作为 Python pipeline 图像处理依赖，用于读取 JPEG/PNG/WebP/GIF、中心裁切、Lanczos 缩放、质量控制、图集拼接和 manifest 写出；若目标环境 Pillow WebP 编码不可用，再以 ffmpeg 作为实现兜底。
- 扩展名不一致不建议在原缓存目录中就地修复；发布生成脚本应按文件头识别真实格式并解码，在新目录输出统一 `.webp` 图集，同时把 mismatch 写入报告，保留原始缓存可追溯性。
- 处理目录建议与原始头像缓存分离，例如 `site_assets/avatar_atlas_150/` 作为本地生成目录，发布时复制到各站点 `site/assets/avatar_atlas_150/`；原始 `site_assets/avatars/` 继续作为忽略的下载缓存。
- 图像规格建议先固定头像单元为 `150x150` 像素；DPI 对网页 canvas 显示无实际影响，若输出中间单张 JPEG/PNG 可写入 96dpi 元数据，但 WebP 图集主要以像素尺寸为准。
- 图集 key 设计为稳定的 `avatar_key = sha256(normalized_icon_url)`，manifest 将头像 URL 哈希映射到 atlas 文件和裁切坐标，使完整库、MVP、demo、large-graph 或未来数据库都能复用同一套全局图集。
- 前端一次性加载图集可行方向是把数千张头像合并为几十张 atlas 图片并在页面初始化时 preload；不建议把全部 atlas base64 内嵌到 HTML 或 graph-data JS，因为 base64 会额外膨胀体积、破坏浏览器缓存，并可能触碰 GitHub 单文件限制。
- 本轮只完成设计分析，未安装依赖、未生成图集、未修改前端渲染或 `.gitignore`。

### 收敛头像 raw 缓存和 3000 图集方案
- 用户确认头像发布图只保留像素并去除不必要元数据，原始下载缓存可移动到 raw 体系，站点外层只放站点用小图；图集先暂定 3000 像素、WebP 质量 80，且不内嵌进网页。
- 目标效果收敛为：`data/raw/` 保存原始头像下载缓存和来源 manifest；`site_assets/` 或站点 `assets/` 只保存由 raw 头像生成的 150x150 WebP 图集、manifest 和必要报告。
- 实现方案调整为新增头像处理阶段：先迁移或兼容读取旧 `site_assets/avatars/` 原始头像缓存，再生成 `data/raw/qqmusic/avatar_cache/` 和原始 manifest；之后从 raw 缓存生成 `site_assets/avatar_atlas_150/atlas_*.webp` 与 `avatar-atlas-manifest.json`。
- 图集参数暂定为单元格 `150x150`、图集 `3000x3000`、每张图集 400 个头像、WebP quality 80；17,743 张头像约需 45 张图集。
- 前端方案为 `graph-data.js` 不再写单图头像路径，而写稳定 `avatar_key`；页面加载 `avatar-atlas-manifest.json` 后一次性 preload 图集文件，绘制节点时按 atlas 坐标裁切到 Canvas。
- 扩展名不一致不作为迁移前置修复；生成过程按真实文件头解码，输出统一 WebP 图集，并在报告中记录扩展名不一致、解码失败、过采样和跳过项，避免改写原始证据。
- 风险边界包括：一次性加载 45 张 3000 图集可能仍有首屏等待和内存压力；质量 80 是否足够需要抽样肉眼验证；Pillow WebP 编码能力需安装后确认；站点资源体积和 GitHub Pages 加载表现必须用真实生成结果验证。
- 本轮只完成方案收敛，未安装依赖、未移动缓存、未生成图集、未修改前端。

### 纠正共享头像图集目录边界
- 用户指出 `site_assets/avatar_atlas_150/` 与 `site/assets/avatar_atlas_150/` 的表述像重复产物，并明确希望所有站点共用一套图集；即使 MVP 会加载过多头像，也可以接受，以减少重复。
- 已纠正目录方案：发布图集只保留一个共享位置，例如仓库根目录 `site_assets/avatar_atlas_150/`；`site/`、`site_mvp/`、`site_demo/`、`site_large/` 的页面和 graph data 均通过相对路径 `../site_assets/avatar_atlas_150/...` 引用同一套 manifest 和 atlas 文件。
- `site/assets/` 后续只保留每个站点自己的 `graph-data.js` 和 `vendor/force-graph.min.js` 等站点专属资源，不再复制共享头像图集。
- 该方案会让 MVP、demo 和 large-graph 在一次性加载时读取完整共享图集，但换来发布资产只有一套、缓存可复用、Git 历史不重复和路径规则更简单。
- 本轮只做方案纠正和日志记录，未修改生成脚本或站点产物。

### 设计共享图集的分层前缀加载
- 用户提出进一步优化：制造图集时先放 MVP 用到的头像，再放 demo 用到的头像，最后放完整站点用到的头像，从而让 MVP 和 demo 按需加载图集前缀。
- 已检查当前站点 graph data：MVP 页面节点头像约 574 个，demo 页面节点头像约 835 个，完整站点节点头像约 17155 个；MVP 与 demo 的并集约 928 个，完整站点在二者之外还有约 16255 个头像。
- 方案判断为可行：仍维护一套共享 `site_assets/avatar_atlas_150/`，但生成顺序按分层优先级排序，manifest 同时记录每个站点需要加载的 atlas 文件列表或前缀数量。
- 图集参数为 3000x3000 且每张 400 个头像时，MVP 理论需要前 2 张左右，demo 如果包含 MVP 并集约需要前 3 张，完整站点加载全部约 43 到 45 张；这比所有页面都加载完整图集更合理。
- 建议排序层级为 `mvp -> demo 增量 -> full 增量 -> orphan cache`；其中 orphan cache 指 raw 缓存里存在但当前任何站点 graph data 未引用的头像，可选择是否放入发布图集。
- 前端方案为各站点 graph data 或一个站点配置字段写入 `avatar_atlas_files`；页面初始化只 preload 当前站点列出的 atlas 文件，但 manifest 仍是一份全局 manifest。
- 风险边界为站点 graph data 更新后必须重新生成图集 manifest，否则某站点可能引用尚未列入其 preload 列表的 atlas；可通过页面兜底在绘制时发现 atlas 未加载则补载对应 atlas。
- 本轮只完成分层前缀加载方案分析，未修改脚本或生成图集。

### 实现共享头像图集生成流程
- 按用户确认的方案新增 `Pillow` 依赖，并安装到项目指定 Conda 环境，用于头像解码、中心裁切、Lanczos 缩放和 WebP 图集输出。
- 新增 `music_metadata_graph/pipelines/avatar_assets.py`，统一提供头像 URL 规范化和 `avatar_key = sha256(normalized_icon_url)` 计算。
- 新增 `music_metadata_graph/pipelines/build_avatar_atlas.py` 和命令入口 `mr-build-avatar-atlas`，默认从 `data/raw/qqmusic/avatar_cache/` 读取原始头像缓存，输出共享 `site_assets/avatar_atlas_150/`。
- 图集生成参数默认实现为 `150x150` 单元格、`3000x3000` atlas、WebP quality 80；生成顺序按 `mvp -> demo -> full` 的头像使用集合分层排序，manifest 中写入各 profile 需要加载的 atlas 文件列表。
- 图集生成脚本按真实文件内容交给 Pillow 解码，不要求先修正扩展名；输出统一 WebP atlas，并写出 `avatar-atlas-manifest.json` 与 `avatar-atlas-report.json`。
- `prepare_static_graph_assets` 的默认原始头像缓存目录改为 `data/raw/qqmusic/avatar_cache/`；若默认 raw 缓存还不存在且旧 `site_assets/avatar-manifest.json` 存在，会兼容复制旧缓存到 raw 目录。
- `prepare_static_graph_assets` 生成 graph data 时不再写本地单头像路径，而是把命中的头像写为 `avatar_key` 并清空 `icon`，避免站点 graph data 继续引用被 ignore 的单头像文件。
- 标准网页前端改为读取共享 `../site_assets/avatar_atlas_150/avatar-atlas-manifest.json`，按 `rawData.avatar_profile` 预加载对应 atlas 文件，并在绘制节点时从 atlas 坐标裁切头像到 Canvas。
- 前端保留运行时补载兜底：若某节点头像所在 atlas 未在当前 profile 预加载列表中，绘制时会临时加载该 atlas 并刷新图谱。
- 一键完整流程从 19 步调整为 20 步：第 17 步准备网站 graph data、vendor 和原始头像缓存，第 18 步生成共享头像图集，第 19 步生成标准静态网站，第 20 步生成 large-graph 静态网站。
- `run_from_song_tabs` 同步使用新的 20 步默认终点；`.gitignore` 调整为继续忽略 `site_assets/` 下普通内容，但允许提交 `site_assets/avatar_atlas_150/` 共享图集发布资源。
- README 与 AGENTS 已同步头像 raw 缓存、共享图集目录、图集生成命令和完整流程编号变化。

### 验证共享头像图集生成流程
- 语法验证执行 `py_compile`，覆盖新增头像工具、图集生成脚本、资源准备脚本、标准网页生成脚本、一键流程、从歌曲 Tab 继续流程和相关测试文件，未报错。
- Pillow 能力验证使用内存中的 10x10 RGB 图像保存为 WebP，输出非空字节，确认当前 Conda 环境具备 WebP 写出能力。
- 定向单元验证执行 `python -m unittest tests.test_static_graph_build tests.test_run_full_pipeline`，共 20 个测试通过；新增测试覆盖头像图集按 MVP/demo/full profile 前缀排序，并确认 profile 只需加载对应 atlas 文件列表。
- 全量单元验证执行 `python -m unittest discover tests`，共 33 个测试全部通过。
- 行尾处理按项目偏好对本轮触碰的源码、测试、文档、配置和开发日志统一为 CRLF；处理后再次执行全量单元测试，33 个测试全部通过。
- 本轮未生成真实完整 `site_assets/avatar_atlas_150/` 图集，因此尚未取得完整头像集的实际输出体积、首屏加载时间和肉眼画质抽样结果；这些仍是后续验证缺口。

### 移动旧头像缓存并生成真实共享图集
- 按用户要求将旧 `site_assets/avatars/` 和 `site_assets/avatar-manifest.json` 直接移动到 `data/raw/qqmusic/avatar_cache/`，外层 `site_assets/` 不再保留原始单头像缓存。
- 同步测试和命令帮助中仍显式使用旧 `site_assets` 作为头像缓存的调用，改为 raw 头像缓存路径 `data/raw/qqmusic/avatar_cache/`。
- 使用禁用头像下载模式重新运行 `prepare_static_graph_assets`、`prepare_static_graph_assets --mvp` 和 `prepare_static_graph_assets --demo`，分别重写 `site/`、`site_mvp/`、`site_demo/` 的 `assets/graph-data.js`，使图谱数据使用 `avatar_key` 而不是单头像路径。
- 完整站点资源准备结果为 24357 个节点、104464 条边、77443 首歌、17156 个头像 URL，其中 17155 个复用 raw 缓存、1 个跳过；MVP 资源准备结果为 1210 个节点、2271 条边、1970 首歌、949 个头像 URL，其中 789 个复用、160 个跳过；demo 资源准备结果为 1213 个节点、1828 条边、2119 首歌、950 个头像 URL，全部复用缓存。
- 通过完整流程第 18 步 `run_full_pipeline --continue-from 18 --stop-after 18` 生成真实共享图集，输出 `site_assets/avatar_atlas_150/avatar-atlas-manifest.json`、`avatar-atlas-report.json` 和 `atlas_000.webp` 到 `atlas_042.webp`。
- 第 18 步后置检查结果为 17183 个头像条目、43 张 atlas、profiles 包含 `mvp`、`demo`、`full`，无失败项、无缺失 profile key。
- 图集发布目录共 45 个文件，包含 43 个 `.webp` 和 2 个 `.json`，总大小约 60.3 MB。
- manifest profile 显示 MVP 加载 2 张 atlas、demo 加载 3 张 atlas、full 加载 43 张 atlas；三个站点当前 graph data 中的唯一头像 key 均能在 manifest 中命中。
- 已重新生成 `site/index.html`、`site_mvp/index.html` 和 `site_demo/index.html`，使当前页面产物包含 atlas manifest 加载、profile preload 和 Canvas 裁切绘制逻辑。

### 验证真实共享图集生成结果
- 语法验证执行 `py_compile`，覆盖头像工具、图集生成脚本、资源准备脚本、标准网页生成脚本、一键流程、从歌曲 Tab 继续流程和相关测试文件，未报错。
- 全量单元验证执行 `python -m unittest discover tests`，共 33 个测试全部通过。
- 文件级验证确认 `site/`、`site_mvp/`、`site_demo/` 的 HTML 均包含 `AVATAR_ATLAS_BASE`、`avatar-atlas-manifest.json`、`loadAvatarAtlases()` 和 `getNodeAvatar()`。
- 数据级验证确认 `site/assets/graph-data.js`、`site_mvp/assets/graph-data.js` 和 `site_demo/assets/graph-data.js` 的节点 `icon` 均为空，头像改由 `avatar_key` 驱动；三个站点 graph data 中引用的唯一头像 key 均无 manifest 缺失。
- 本轮未做浏览器实际加载截图和肉眼画质抽样；剩余风险为 60.3 MB 图集在 GitHub Pages 上的首屏加载时间、不同浏览器解码内存和 WebP 画质需要后续实际页面验证。

### 修复本地打开网页时头像 manifest 加载失败
- 用户反馈网页打开后头像全部缺失。
- 已定位可疑原因：页面通过 `fetch("../site_assets/avatar_atlas_150/avatar-atlas-manifest.json")` 读取头像图集 manifest；直接双击本地 HTML 使用 `file://` 打开时，浏览器通常会拦截本地 JSON fetch，导致 manifest 为空并回退到缺失头像。
- 已修改图集生成脚本，同时输出 `site_assets/avatar_atlas_150/avatar-atlas-manifest.js`，内容为 `window.AVATAR_ATLAS_MANIFEST_DATA = ...`，使 manifest 能像 graph data 一样通过普通 script 标签加载。
- 已修改标准网页 HTML 生成模板，在 graph data 后加载 `../site_assets/avatar_atlas_150/avatar-atlas-manifest.js`；前端优先读取 `window.AVATAR_ATLAS_MANIFEST_DATA`，只有该全局对象不存在时才回退 fetch JSON。
- 已修正图集生成脚本的重复生成行为：每次生成前清理旧 `atlas_*.webp`、manifest 和 report，避免上一次生成残留多余 atlas 文件。
- 修复过程中曾误用 `--include-unused-cache` 生成过 45 张 atlas 和未使用缓存失败报告；随后按默认发布范围重跑，恢复为 17183 个头像条目、43 张 atlas、失败数 0。
- 已重新生成 `site/index.html`、`site_mvp/index.html`、`site_demo/index.html` 和共享图集 manifest 脚本；当前图集目录包含 43 个 `.webp`、1 个 `.js` 和 2 个 `.json`。
- 验证执行 `py_compile` 覆盖 `build_avatar_atlas.py`、`build_static_graph.py` 和 `run_full_pipeline.py`，未报错；全量单元验证 `python -m unittest discover tests` 共 33 个测试全部通过。
- 文件级验证确认三个 HTML 页面均引用 `avatar-atlas-manifest.js`，且 manifest 脚本可解析出 17183 个头像条目，profile 仍为 MVP 2 张、demo 3 张、full 43 张 atlas。

### 优化图集头像的首屏加载方式
- 用户反馈改为图集后页面加载速度明显慢于使用原始图。
- 已定位性能风险：完整站点 profile 需要 43 张 `3000x3000` WebP atlas，总发布图集约 60 MB；旧实现会在 manifest 就绪后等待当前 profile 的所有 atlas 加载完成，并且 canvas 绘制遍历节点时可能触发全部 atlas 同时开始加载。
- 已调整标准网页前端加载策略：页面先执行普通图谱渲染，不再等待全部 atlas；manifest 就绪后只触发轻量重绘，头像图集通过队列加载。
- 新增 atlas 加载队列、去重集合和并发上限，完整站点同时最多处理 2 张 atlas，MVP/demo 同时最多处理 3 张 atlas；节点绘制发现头像所在 atlas 未加载时只入队，不直接启动无限制图片请求。
- atlas 加载完成后优先调用 `graphInstance.refresh()` 进行 Canvas 轻量重绘，避免为了头像到位而重建图谱数据和重新启动布局。
- 已重新生成 `site/index.html`、`site_mvp/index.html` 和 `site_demo/index.html`，确保实际页面产物包含新的非阻塞队列加载逻辑。
- 验证执行 `py_compile music_metadata_graph/pipelines/build_static_graph.py`，未报错；全量单元验证 `python -m unittest discover tests` 共 33 个测试全部通过。
- 文件级验证确认三个标准 HTML 页面均包含 `initializeAvatarAtlases()` 和 `enqueueAtlasImage()`，且不再包含旧的 `loadAvatarAtlases()` 或 `Promise.all(files...)` 全量等待逻辑。
- 浏览器实际验证存在缺口：Codex 浏览器插件拒绝直接打开 `file://` 页面，并且本机 `localhost` 静态服务访问被浏览器端拦截为 `ERR_BLOCKED_BY_CLIENT`；因此本轮未取得真实浏览器首屏耗时截图或性能计时。

### 修复头像图集到位后的绘图区闪烁
- 用户反馈头像图集加载变快后，绘图区仍会在每次图集解析完成时闪一下，导致页面仍不好操作。
- 已复查当前 `force-graph` 运行库能力，确认当前版本公开了 `pauseAnimation/resumeAnimation`，但没有 `refresh()` 方法。
- 已定位闪烁原因：上一轮代码在 atlas 加载完成后尝试调用 `graphInstance.refresh()`；由于该方法不存在，实际落入 fallback `renderGraph()`，导致每张 atlas 到位都触发一次图谱重渲染。
- 已修改 `requestAvatarAtlasRender()`，不再在头像图集到位时调用 `renderGraph()`；现在只在可用时调用 `graphInstance.resumeAnimation()`，让既有动画循环在下一帧自然绘制已解码头像。
- 已重新生成 `site/index.html`、`site_mvp/index.html` 和 `site_demo/index.html`，实际页面产物已去除 atlas 到位后的重渲染 fallback。
- 已补充单元断言，确认模板中保留 `requestAvatarAtlasRender()` 和 `graphInstance.resumeAnimation()`，且不再包含 `graphInstance.refresh()`。
- 验证执行 `py_compile music_metadata_graph/pipelines/build_static_graph.py`，未报错；全量单元验证 `python -m unittest discover tests` 共 33 个测试全部通过。

### 分析头像图集重建判断策略
- 用户询问当前图集制作脚本是否会自动判断何时需要重建，或是否可以每次都重新制作。
- 已检查 `build_avatar_atlas.py`，当前脚本没有输入指纹、mtime 比较或增量跳过逻辑；每次运行都会删除旧 `atlas_*.webp`、`avatar-atlas-manifest.json`、`avatar-atlas-manifest.js` 和 `avatar-atlas-report.json`，然后完整重建。
- 当前完整图集产物为 43 张 WebP atlas，加 manifest/report 共 46 个文件，总大小约 62.7 MB；重建不需要网络请求，但需要重新读取、解码、裁切缩放 17183 张头像并重新 WebP 编码。
- 判断结论为不建议把图集制作作为每次普通网页生成都无条件执行；更合适的是在头像 raw 缓存、graph data 头像 key/profile、图集参数或图像处理算法变化后才重建。
- 后续可新增构建指纹：记录图集参数、脚本版本、profile graph data 中的 avatar_key 顺序、raw manifest 中对应记录的 local_path/status/文件大小/mtime 或内容 hash；指纹一致时直接复用已有图集。

### 完善头像图集重建判断边界
- 用户指出上一轮“何时重建图集”的判断不够完备，要求进一步仔细分析。
- 已补充判断边界：复用图集必须同时满足“输入等价”和“输出完整”两类条件；只比较 raw 缓存或 graph data 时间戳不能证明图集可复用。
- 输入等价需要覆盖图集参数、图像处理算法版本、Pillow/WebP 编码能力、profile graph data 的头像 key 集合与 profile 前缀顺序、当前发布范围内 raw manifest 记录、对应本地头像文件内容，以及失败/缺失头像集合。
- 输出完整需要覆盖 manifest JSON、manifest JS、atlas 文件列表、文件大小和文件 hash；还需要检查 manifest item 坐标在 atlas 边界内、坐标按 cell size 对齐、profile 需要的 atlas 文件全部存在，且没有旧构建残留的额外 atlas 混入发布目录。
- 已识别当前脚本的额外风险：图集构建开始时会先删除旧产物；如果中途失败或被中断，会留下不可用或不完整的发布目录。后续更稳妥的实现应先写入临时目录并验证，再替换正式目录。
- 建议后续实现三种运行模式：默认 `auto` 指纹匹配则跳过、`--force` 无条件重建、`--check` 只验证现有图集是否匹配当前输入和输出完整性。

### 实现头像图集指纹复用和安全重建
- 已在 `build_avatar_atlas.py` 中新增默认 `auto` 模式、`--force` 强制重建和 `--check` 只验证模式。
- 新增 `avatar-atlas-build-fingerprint.json`，记录图集参数、生成器版本、Pillow/WebP 环境摘要、profile key 摘要、ordered key 摘要、source entry 内容 hash 摘要，以及 manifest、manifest JS、report 和 atlas 文件的大小与 hash。
- 默认 `auto` 模式会先重新计算当前输入 hash，并验证现有输出文件集合、文件 hash、manifest 结构、坐标边界、profile atlas 引用和 manifest JS 是否与 manifest 一致；全部匹配时跳过重建。
- 当输入变化、fingerprint 缺失、输出 hash 不匹配、atlas 文件集合有旧残留或 manifest 结构错误时，`auto` 会重新制作图集。
- 重建流程已改为先写入 `site_assets` 下的临时目录，生成 manifest、report 和 fingerprint 后先验证临时目录；验证通过后再替换正式 `site_assets/avatar_atlas_150/`，避免中途失败破坏已有可用图集。
- `run_full_pipeline` 的第 18 步后置检查已接入同一套 fingerprint 校验，不再只检查图集文件是否存在和非空。
- README 已补充 `build_avatar_atlas` 默认 `auto`、`--force` 和 `--check` 的使用说明；AGENTS 已同步第 18 步和图集脚本运行规则。
- 单元测试新增覆盖：首次构建生成 fingerprint、输入输出一致时跳过、存在旧 atlas 残留时自动重建并清理、源头像文件内容变化时 `--check` 报告输入变化。

### 验证头像图集指纹复用和安全重建
- 语法验证执行 `py_compile`，覆盖 `build_avatar_atlas.py`、`run_full_pipeline.py` 和 `tests/test_static_graph_build.py`，未报错。
- 定向单元验证执行头像图集相关 4 个测试，全部通过；全量单元验证执行 `python -m unittest discover tests`，共 36 个测试全部通过。
- 首次使用新脚本处理真实图集时，因为旧图集尚无 fingerprint，执行完整重建；结果为 17183 个头像、43 张 atlas、失败数 0，耗时约 5 分 47 秒。
- 真实图集第二次执行同一命令时返回 `status=skipped`，确认默认 `auto` 模式可复用现有图集；严格 hash 检查和输出验证耗时约 1 分钟。
- `--check` 验证真实图集返回 `status=valid`，头像条目 17183，atlas 文件 43，输入 hash 为 `a53e905c6e72539543086a3bfc78af29e54a821db33e58558c84e0d1ea28deb7`。
- 运行完整编排第 18 步 `run_full_pipeline --continue-from 18 --stop-after 18`，步骤命令返回 `status=skipped`，后置检查返回 fingerprint 路径、输入 hash、17183 个头像条目和 43 张 atlas 文件。
- 初版 fingerprint 曾因记录完整输入明细达到约 11 MB；已改为只保存摘要 hash 并复用现有图集压缩 fingerprint，当前 fingerprint 文件约 9.6 KB，图集目录总大小约 62.5 MB。

### 实现过滤后临时歌曲 CSV 双导出
- 用户要求完整流程中原本导出四位歌手相关歌曲的 4 个临时 CSV 步骤，同时增加全量歌曲临时 CSV 导出；原四位歌手 CSV 文件名需要写明“四位歌手”，并使用新的 SQLite 数据库运行完整流程，CSV 路径仍覆盖当前验证目录。
- 已修改第 13 步 `import_song_credits_to_db.py`：默认 `--temp-songs-csv` 导出当前歌曲全量临时 CSV，新增 `--four-singer-temp-songs-csv` 导出周杰伦、林俊杰、薛之谦、汪苏泷四位歌手范围 CSV，文件名为 `songs_after_step10_credit_import_四位歌手.csv`。
- 已修改第 14 步 `filter_songs_by_credit_completeness.py`：默认 `--temp-kept-csv` 导出全量保留歌曲临时 CSV，新增 `--four-singer-temp-kept-csv` 导出四位歌手范围 CSV，文件名为 `songs_after_step11_complete_credits_四位歌手.csv`。
- 已修改第 15 步 `filter_imported_songs.py`：默认 `--temp-kept-csv` 导出全量保留歌曲临时 CSV，新增 `--four-singer-temp-kept-csv` 导出四位歌手范围 CSV，文件名为 `songs_after_step12_same_credit_name_dedupe_四位歌手.csv`。
- 已修改第 16 步 `filter_songs_by_language.py`：原全量临时 CSV 保持通用文件名，新增四位歌手范围 CSV，文件名为 `songs_after_step13_language_filter_四位歌手.csv`。
- 已修改 `run_full_pipeline.py`，让完整流程第 13 到 16 步同时传入全量 CSV 路径和四位歌手 CSV 路径，并在后置检查中检查两类 CSV 存在。
- 已新增 `tests.test_run_full_pipeline` 断言，确认完整流程第 13 到 16 步均包含全量和四位歌手两份临时 CSV 路径。

### 修复完整流程运行中的过滤和进度问题
- 使用新数据库 `data/music_metadata_graph_temp_csv_fullrun.sqlite3` 运行完整流程时，第 10 步专辑类型过滤在完整库规模上因相关子查询按歌曲逐行统计同名数量而长时间占用 CPU。
- 已将 `filter_songs_by_album_type.py` 和 `run_full_pipeline.py` 中对应检查改为先按 `songs.name` 聚合出重复歌名，再 JOIN 过滤非白名单专辑类型歌曲；真实库查询耗时约 2.79 秒，保持“非白名单专辑类型且同名歌曲不止一首才删除”的业务规则。
- 第 11 步 `collect_song_producer_raw.py` 原实现会在处理完整歌曲列表时长时间静默，容易被误判为卡住；已改为按批处理并定期打印进度，默认每 1000 首或实际新请求时输出状态，失败请求仍逐条输出。
- 第 11 步 smoke 验证使用新数据库和 `--max-songs 5`，5 首均命中制作人 raw 缓存，脚本正常输出进度和缺 MID CSV。

### 验证临时 CSV 双导出相关改动
- 语法验证执行 `py_compile`，覆盖 `import_song_credits_to_db.py`、`filter_songs_by_credit_completeness.py`、`filter_imported_songs.py`、`filter_songs_by_language.py`、`filter_songs_by_album_type.py`、`collect_song_producer_raw.py`、`run_full_pipeline.py` 和 `tests/test_run_full_pipeline.py`，未报错。
- 定向单元验证执行 `tests.test_filter_songs_by_album_type` 和 `tests.test_run_full_pipeline`，共 6 个测试通过。
- 新数据库完整流程实际运行完成了第 1 到第 10 步；第 10 步后临时数据库状态为 `artists=34076`、`albums=116186`、`songs=303401`、`song_singers=442831`，`PRAGMA foreign_key_check` 返回 0 行。
- 第 10 步专辑类型过滤日志显示从 331689 首歌曲删除 28288 首，保留 303401 首，删除 CSV 写入 `data/processed/validation/song_filtering/csv_views/songs_removed_by_step8_album_type.csv`。
- 第 11 步制作人 raw 请求在沙箱网络受限时出现 `WinError 5 拒绝访问`；申请网络放行后被用户中断并要求终止，已停止残留 Python 进程，不再继续运行完整流程。
- 终止时新数据库尚未创建 `song_credit_artists` 表，流程未到达第 13 到 16 步，因此本轮新增的 4 份“四位歌手”临时 CSV 尚未生成；当前验证目录中的旧临时 CSV 时间戳仍早于本轮运行。
- 终止时第 11 步制作人 raw 覆盖从缺 6473 个推进到缺 4225 个；后续若继续完整流程，应从第 11 步继续，并允许网络请求或提前补齐剩余 raw。

### 修正制作人 raw 采集进度输出的合包语义
- 用户指出第 11 步进度输出修改后可能不再按缺失请求合包，请求制作人 raw 的网络效率会下降。
- 复核确认上一版虽然仍调用 `Client.gather()`，但外层按全量歌曲每 20 首切批；当缺失 raw 稀疏分布时，实际会形成很多不足 20 个请求的小合包，削弱原有合包效率。
- 已修改 `collect_song_producer_raw.py`：扫描全量歌曲时缓存命中立即处理，缺失 raw 请求先加入 `pending_requests`，累计到 `--batch-size` 默认 20 个后再调用 `Client.gather()` 合包发送；扫描结束后再发送最后不足 20 个的尾批。
- 进度输出仍保留：`[x/总歌曲数]` 表示全量歌曲扫描位置，`status=fetched` 表示该歌曲 raw 刚请求成功，`status=cache_hit` 仍按 1000 首或末尾节流打印。
- 验证执行 `py_compile collect_song_producer_raw.py` 未报错；使用新数据库 `--max-songs 5` 执行缓存 smoke，5 首均为 `cache_hit`，脚本正常输出摘要。

### 压缩前两版开发日志
- 用户要求整理 `develop_log.md` 第 33 到 1400 行的前两版日志，允许合并、拆分、删除和局部调序，但不能破坏大的顺序和先后逻辑。
- 已将 `## 日志内容` 之后到 `### 归档当前流程和本地数据准备重新设计` 之前的前两版流水日志压缩为 7 条阶段性记录，覆盖项目初始化、第一版端到端采集与过滤、第一版静态网页与 force-graph、第一版归档、第二版高可信/补充分支、第二版目录与 CSV 治理、第二版数据库化方向分析。
- 压缩后保留两次归档位置：第一版旧端到端流程归档到 `archive/legacy_pipeline_2026-05-12/`，第二版重新设计前流程仍由后续原日志记录为归档到 `archive/redesign_reset_2026-05-13/`。
- 本次只修改 `develop_log.md` 的历史日志表达，不修改源码、数据库、raw 缓存、验证 CSV、网站产物或归档目录。
- 验证对象为 `develop_log.md` 标题结构、归档锚点、UTF-8 编码和行尾；检查结果显示压缩记录位于日志开头，`归档当前流程和本地数据准备重新设计` 仍保留在压缩段之后，文件无 U+FFFD 替换字符、无 BEL 控制字符、无裸 LF。

### 补充完整流程长步骤进度日志
- 用户指出除第 11 步外，还有几个完整流程步骤容易让人误以为卡住，要求改成类似第 11 步的日志显示方式，同时不得破坏落盘和请求规则。
- 已修改第 7 步 `collect_song_album_detail_raw.py`：专辑详情 raw 采集在缓存命中、请求成功和失败发生时即时输出 `[当前/总数]` 进度；缓存命中按 1000 条和末尾节流打印，新请求和失败逐条打印；保留原有 `Client.gather()` 按 `--batch-size` 合包请求语义、raw 路径和失败报告规则。
- 已修改第 8 步 `import_song_album_detail_to_db.py`：读取专辑详情 raw 时每 1000 个文件和末尾输出进度，并在拆分有效/拒绝、替换 `albums`、写拒绝 CSV 前输出阶段 JSON。
- 已修改第 9 步 `import_singer_song_tab_to_db.py`：读取歌曲 Tab raw、按 song mid 分组、评估入库/拒绝歌曲时输出固定间隔进度，并在替换歌曲表和写拒绝 CSV 前输出阶段 JSON。
- 已修改第 10、14、15、16 步过滤脚本：在查询待删除歌曲、准备 CSV 行、写正式删除 CSV、写全量临时 CSV、写“四位歌手”临时 CSV 和执行删除前输出阶段日志；过滤 SQL、删除规则、CSV 路径和临时 CSV 双导出语义保持不变。
- 已修改第 13 步 `import_song_credits_to_db.py`：扫描制作人 raw 时每 1000 个文件和末尾输出进度，导入制作人、替换作词作曲关系、写全量临时 CSV 和四位歌手临时 CSV 前输出阶段日志；未改变制作人 raw 读取范围、缺 MID 解析、艺人补入和关系入库规则。
- 已在 `song_csv.prepare_song_csv_rows()` 新增可选 `progress_label` 参数；默认不输出，只有长流程脚本显式传入时才打印 CSV 行准备进度，避免影响普通调用。
- 验证执行 `py_compile`，覆盖本轮修改的 `song_csv.py`、第 7/8/9/10/13/14/15/16 步相关脚本，未报错。
- 定向单元验证执行 `python -m unittest tests.test_filter_songs_by_album_type tests.test_run_full_pipeline`，共 6 个测试通过；测试日志中已能看到第 10 步阶段输出和 CSV 准备进度。

### 节流第十二步常规补 MID 进度输出
- 用户询问第 12 步逐条打印 `db_matched` 和 `cache_hit` 是否会增加 IO 耗时，并要求修改。
- 已修改 `quick_search_artist_mid.py`：新增 `PROGRESS_EVERY = 1000` 和 `should_print_progress()`，用于节流无需网络请求的常规成功日志。
- 第 12 步及共用补 MID 逻辑现在对 `db_matched` 和任意 `cache_hit` 结果只在每 1000 个唯一姓名及最后一个唯一姓名打印；真实 `fetched`、请求失败、库内姓名歧义、空拆分等仍逐条打印。
- 本次未修改 quick_search raw 读取/请求规则，未修改每条处理后重写补 MID CSV 的渐进落盘规则，未修改艺人入库和拆分姓名匹配规则。
- 验证执行 `py_compile quick_search_artist_mid.py fill_song_credit_missing_mids.py fill_song_singer_missing_mids.py`，未报错；定向单元验证 `python -m unittest tests.test_filter_songs_by_album_type tests.test_run_full_pipeline` 共 6 个测试通过。

### 轻度压缩当前版早期日志
- 用户要求对当前这一版日志做轻度压缩，不同于前两版归档日志压缩；本次只删除或合并明显低价值内容，例如纯“验证通过”记录、重复验证流水、以及已被后续设计推翻的早期方案，同时遵循越新的日志保留越多。
- 已将当前版较早部分从 `归档当前流程和本地数据准备重新设计` 到 2026-05-15 末尾的流水日志压缩为阶段性记录，保留重新设计启动、完整歌手列表 raw、歌手表入库、主页歌曲 Tab、歌曲/专辑数据库边界、缺失歌手补全、作词作曲关系、请求量与断点续跑、quick_search 补 MID、完整流程编排、MVP 可视化等关键事实。
- 本次保留 2026-05-16 及之后较新日志的详细记录，仅在早期段落中合并验证空话和被后续推翻的设计；未修改源码、数据库、raw 缓存、CSV、网站产物或归档目录。
- 验证对象为 `develop_log.md` 标题结构、UTF-8 编码和行尾；检查目标为无 U+FFFD 替换字符、无 BEL 控制字符、无裸 LF，并确认 `## 2026-05-16` 之后较新日志仍保留。

### 扩展补 MID 姓名拆分分隔符
- 用户指出补 MID 步骤里除带 `/` 的姓名要拆开，带中文逗号 `，` 和顿号 `、` 的姓名也应该拆开。
- 已将共用 `quick_search_artist_mid.split_artist_names()` 从仅按 `/` 拆分改为按 `/`、`，`、`、` 拆分，并新增 `has_artist_name_separator()` 供调用方统一判断是否进入拆分分支。
- 第五步前置补演唱歌手 MID、第十二步前置补作词作曲 MID、第八步歌曲入库缺 MID 歌手名解析、第十三步作词作曲导入缺 MID 制作人解析均复用同一分隔符判断。
- 新增 `tests/test_artist_name_split.py`，覆盖 `/`、`，`、`、` 混合拆分、重复片段去重、歌曲演唱者缺 MID 库内唯一姓名匹配、作词作曲缺 MID 库内唯一姓名匹配。
- AGENTS 项目规则已同步补 MID 分隔符范围，明确相关步骤不再只处理 `/`。

### 调整右侧详情栏歌曲卡片信息顺序
- 用户指出右侧详情栏选中歌手后，支撑歌曲卡片原本第一行只显示标题、第二行显示“演唱者 · 选中音乐人职能 · 专辑”，容易把职能理解为演唱者或专辑侧信息。
- 已调整标准静态图模板 `renderSongList()`：歌曲卡片第一行改为“歌曲标题 · 作词/作曲”，表示选中音乐人对该歌曲的贡献职能；第二行改为“演唱者 · 专辑”，表示贡献流向的演唱方和歌曲出处。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 `index.html`，使当前可打开网页产物同步新顺序。
- 已补充 `tests/test_static_graph_build.py` 静态断言，确认模板包含 `[song.name, song.role]` 和 `[song.target, song.album]` 两段拼接，且不再包含旧的 `[song.target, song.role, song.album]` 拼接。
- 验证执行 `py_compile build_static_graph.py tests/test_static_graph_build.py`，未报错；执行 `python -m unittest tests.test_static_graph_build.StaticGraphBuildTests`，19 个测试通过；执行 `python -m unittest discover tests`，39 个测试通过。
- 文件级验证确认 `site/index.html` 包含新顺序并不包含旧顺序；浏览器实际入口验证存在环境缺口，Codex 浏览器插件拦截 `file://` 访问，并且本地 HTTP `127.0.0.1` 页面返回 `ERR_BLOCKED_BY_CLIENT`。

### 调整网页标题下方数据来源和生成时间换行
- 用户要求把网页标题下方摘要中的“SQLite 静态图谱”改为“数据来源：QQ音乐”，并让“生成于”时间单独换行，避免时间戳在中间被动折断。
- 已修改标准静态图模板 `renderHeader()`，摘要第一行显示“数据来源：QQ音乐 · 数据库：歌曲数 / 音乐人数”，第二行显示“生成于 时间戳”。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 `index.html`，使当前网页产物同步新标题摘要。
- 已补充 `tests/test_static_graph_build.py` 断言，确认模板包含“数据来源：QQ音乐”和 `<br />`，且不再包含“SQLite 静态图谱”。
- 验证执行 `py_compile build_static_graph.py tests/test_static_graph_build.py`，未报错；执行 `python -m unittest tests.test_static_graph_build.StaticGraphBuildTests`，20 个测试通过；执行 `python -m unittest discover tests`，42 个测试通过。
- 文件级验证确认四个站点 HTML 均包含新文案和生成时间换行；`site_large/assets/graph-data.js` 因生成命令只改动生成时间戳，已按 HEAD 字节恢复，避免无关数据产物变更。

### 固定顶栏并同步明细表高度
- 用户要求底部“歌曲明细/关系明细”表的高度改成和右侧详情栏一样，从绘图区高度读取；同时要求顶部控制栏固定显示，不随页面滚动消失。
- 已将 `.topbar` 改为 `position: sticky; top: 0`，并通过 CSS 变量 `--topbar-height` 让右侧详情栏 sticky 偏移避开固定顶栏。
- 已将原 `syncDetailPanelHeight()` 扩展为 `syncPanelHeights()`，继续从 `.graph-panel` 读取实际高度，并同时写入右侧详情栏和底部 `.data-section` 的 `height/maxHeight`。
- 已把底部 `.data-section` 改为纵向 flex 容器，标签栏固定占位，`#table-content` 作为剩余空间滚动区，避免继续使用固定 `420px` 高度。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 `index.html`，使当前网页产物同步固定顶栏和明细表高度逻辑。
- 已补充 `tests/test_static_graph_build.py` 断言，覆盖顶栏 sticky、详情栏基于顶栏高度偏移、底部明细区 flex 高度、`syncPanelHeights()` 统一同步高度，并确认旧 `syncDetailPanelHeight()` 不再存在。
- 验证执行 `py_compile build_static_graph.py tests/test_static_graph_build.py`，未报错；执行 `python -m unittest tests.test_static_graph_build.StaticGraphBuildTests`，20 个测试通过；执行 `python -m unittest discover tests`，42 个测试通过。
- 文件级验证确认四个站点 HTML 均包含固定顶栏和统一高度同步逻辑；生成命令刷新过的各站点 `assets/graph-data.js` 只涉及生成时间戳，已按 HEAD 字节恢复，避免无关数据产物变更。

### 增加隐藏绘图表格查看模式
- 用户要求在顶栏右半部分第一行开关最左侧新增“隐藏绘图”开关，默认关闭；除非后续特别说明，该开关必须永远位于所有开关最左边。
- 已在开关区最左侧新增 `drawing-toggle`，状态字段为 `hideDrawing: false`，默认不勾选。
- 开启“隐藏绘图”后，页面给 `body` 增加 `drawing-hidden` 类，隐藏 `.workspace` 中的绘图区和右侧详情栏，并将底部 `.data-section` 顶到顶栏下方。
- 已调整 `render()` 和 `renderSelection()`：隐藏绘图时不调用 `renderGraph()` 和 `renderDetail()`，筛选、表格搜索和标签切换只刷新明细表与高度，避免图谱重绘卡顿。
- 已调整窗口 resize 逻辑，隐藏绘图时不触发 `renderGraph()`；`syncPanelHeights()` 在隐藏绘图时直接按明细区距离视口顶部计算表格区域高度。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 `index.html`，使当前网页产物同步隐藏绘图开关。
- 已补充 `tests/test_static_graph_build.py` 断言，覆盖开关默认关闭、开关位置在作词/作曲开关之前、隐藏绘图 body class、跳过 `renderGraph()`/`renderDetail()`、隐藏绘图时 resize 不重绘图谱。
- 验证执行 `py_compile build_static_graph.py tests/test_static_graph_build.py`，未报错；执行 `python -m unittest tests.test_static_graph_build.StaticGraphBuildTests`，20 个测试通过；执行 `python -m unittest discover tests`，42 个测试通过。
- 文件级验证确认四个站点 HTML 均包含“隐藏绘图”开关、`drawing-hidden` 样式和跳过绘图逻辑；`site_large/assets/graph-data.js` 因生成命令只改动生成时间戳，已按 HEAD 字节恢复，避免无关数据产物变更。

### 核对 singer.get_info 接口使用步骤
- 用户追问 `qqmusic.singer.get_info` 除粉丝量补充外还在哪些步骤使用。
- 已核对当前有效源码和一键完整流程编排，当前正式流程中 `get_info` 只在第 2 步歌手粉丝量 raw JSON 和第 6 步补全歌曲歌手信息中使用。
- 第 2 步 `collect_singer_fans_raw.py` 对 `get_singer_list.concernNum` 未覆盖的第三步目标歌手调用 `get_info(mid)`，读取 `Info.FansNum.Num` 并写入 `data/raw/qqmusic/singer_fans_info/` 和粉丝量汇总。
- 第 6 步 `collect_missing_song_singers_to_db.py` 扫描第四步主页歌曲 Tab 中不在 `artists` 表的非空歌手 MID，调用 `get_info(mid)`，保存到 `data/raw/qqmusic/singer_info/` 并补入 `artists`。
- 本次只做接口用途核对和日志记录，未修改业务代码。

### 第六步补入歌曲歌手粉丝量
- 用户确认第 6 步补全歌曲歌手信息时也应该将 `qqmusic.singer.get_info` 返回的粉丝量入库。
- 已修改 `collect_missing_song_singers_to_db.extract_singer_row()`：当 `Info.FansNum.Num` 为可用正数时，随补入歌手 row 写入 `fans_num`、`fans_source=qqmusic.singer.get_info.FansNum.Num` 和当前 `singer_info` raw 路径。
- 复用既有 `import_artists()` 的冲突更新规则，空粉丝量不会覆盖已有正数粉丝量，非空来源和 raw 路径才会更新来源追溯字段。
- 已新增 `tests/test_collect_missing_song_singers_to_db.py`，覆盖第 6 步从 `get_info` 抽取粉丝量，以及缺粉丝量时不覆盖已有粉丝量。
- AGENTS 项目规则已同步第 6 步粉丝量入库要求。

### 修正网页歌曲展示优先使用 title
- 用户指出内部去重等逻辑可以继续使用歌曲和专辑的 `name`，但网页展示应使用 `title`。
- 已修改 `build_static_graph.py`：图谱数据中的歌曲明细和边支撑歌曲同时导出 `name` 与 `title`；前端新增 `songDisplayTitle()`，右侧详情卡、关系表支撑歌曲和歌曲明细表均优先显示 `title`，缺失时回退 `name`。
- 已为专辑展示预留兼容字段：若 `albums` 表存在 `title` 列则导出 `album_title` 并优先显示；当前正式 `albums` 表仍只有 `name`，因此现有网页专辑展示会回退到 `album.name`，不改变专辑入库或过滤规则。
- 已同步 `AGENTS.md` 项目规则，明确网页展示层优先 `songs.title`，但过滤、去重、排序和身份判断仍按已确认的 `songs.name` 与 `albums.name` 规则执行。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的 HTML；并重写四个站点的 `assets/graph-data.js`，使外部图谱数据也包含 `title` 与 `album_title` 字段。

### 验证网页歌曲 title 展示修正
- 定向单元验证执行 `python -m unittest tests.test_static_graph_build`，共 20 个测试通过；新增测试覆盖 `songs.name` 与 `songs.title` 不同时图谱数据仍保留内部 `name`，并向网页展示层导出 `title`。
- 重新生成标准站点数据资产时使用 `prepare_static_graph_assets --skip-avatar-download`，未触发新头像网络下载；完整站点、MVP、demo 三个站点分别重写 `assets/graph-data.js`，large-graph 由 `build_large_graph_static --output-dir site_large` 重写。
- 文件级验证确认 `site/index.html`、`site_mvp/index.html`、`site_demo/index.html`、`site_large/index.html` 均包含 `songDisplayTitle()` 与 `albumDisplayTitle()`；四份 `graph-data.js` 均包含 `title` 与 `album_title` 字段。

### 核对 artists 入库步骤
- 用户询问当前完整流程还有哪些步骤会向 `artists` 表加人。
- 已核对当前有效源码中 `import_artists()` 调用点和一键完整流程编排，确认会新增或更新 `artists` 的正式步骤为第 3 步歌手列表入库、第 5 步前置 quick_search 补歌曲歌手缺 MID、第 6 步补全歌曲歌手信息、第 12 步前置 quick_search 补作词作曲缺 MID、第 13 步导入作词作曲关系。
- 第 2 步只生成粉丝量 raw 和汇总 JSON，不直接写数据库；第 4、7、8、9、10、11、14、15、16、17、18、19、20 步不负责向 `artists` 新增音乐人。

### 同步网页明细表范围与绘图筛选
- 用户要求网页下方明细表显示范围与上方绘图一致，所有绘图筛选都必须应用在明细表上。
- 已修改标准静态图模板：`renderTable()` 先获取当前 `buildGraph()` 结果，关系明细直接使用当前图的可见边，歌曲明细只展示当前可见边支撑到的歌曲。
- 歌曲明细的作词、作曲、演唱列现在按当前图可见节点过滤；当用户选中节点时，明细表仍可在当前图范围内进一步收窄到选中节点相关人员。
- 已同步 `AGENTS.md` 项目规则，明确明细表搜索和选中节点只能缩小当前图范围，不得重新扩大到原始全量歌曲集合。

### 验证网页明细表筛选同步
- 已执行 `py_compile build_static_graph.py tests/test_static_graph_build.py`，确认本轮修改的网页生成脚本和测试文件语法可编译。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 与 `site_large/` 的静态网页入口，使当前可打开网页产物同步明细表范围规则。
- 已执行 `python -m unittest tests.test_static_graph_build`，共 20 个测试通过；新增断言覆盖明细表复用 `buildGraph()`、歌曲明细按当前可见边提取歌曲、人员列按当前可见节点过滤，并确认旧的目标歌手独立过滤逻辑不再存在。

### 补充网页明细表保留节点自身歌曲
- 用户补充指出任何时候明细表都应该包含节点本身的歌曲，即使某些筛选会让图中出现孤岛节点，明细表仍应显示这些节点自己的歌曲。
- 已调整标准静态图模板：歌曲明细在当前图可见边支撑歌曲之外，额外合并当前可见节点作为演唱者参与的歌曲；该补充不改变关系明细表的可见边范围。
- 已同步 `AGENTS.md` 项目规则，明确孤岛节点自身演唱歌曲属于歌曲明细表当前图范围内应显示内容。

### 验证网页明细表保留节点自身歌曲
- 已执行 `py_compile build_static_graph.py tests/test_static_graph_build.py`，确认本轮补充修改语法可编译。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的静态网页入口；large-graph 生成命令带出的 `graph-data.js` 仅为生成时间戳刷新，已恢复为原字节，避免无关数据产物变化。
- 已执行 `python -m unittest tests.test_static_graph_build`，共 20 个测试通过；新增断言覆盖歌曲明细把当前可见节点作为演唱者参与的歌曲加入结果。

### 修正明细表歌曲行完整显示
- 用户指出顶栏筛选对明细表的影响应只决定歌曲条目本身是否出现；如果歌曲条目出现，作词、作曲、演唱等字段应显示完整内容，不应因为制作人节点被筛选掉而变成空白。
- 已调整标准静态图模板 `renderTable()`：继续使用当前 `buildGraph()` 结果和选中节点范围决定歌曲行集合，但歌曲行进入表格后，作词、作曲、演唱列直接使用歌曲完整人员列表渲染。
- 已移除前端 personNamesForTable() 对当前可见节点或选中节点的二次人员过滤，避免筛选后歌曲仍在但制作人/演唱者列被裁空。
- 已同步 AGENTS.md 网页明细表范围规则，明确绘图筛选只决定歌曲条目是否进入歌曲明细表，不得裁剪歌曲内部字段。
- 已重新生成 site/、site_mvp/、site_demo/ 和 site_large/ 的静态网页入口，使当前可打开页面同步修正后的明细表显示逻辑。

## 2026-05-18

### 修正隐藏绘图下绘图开关仍卡顿
- 用户指出开启“隐藏绘图”后，切换“作词/作曲分开”“显示名字”等只和绘图有关的开关仍会卡顿数秒。
- 已定位原因：这些开关虽然隐藏绘图时跳过 `renderGraph()`，但仍统一调用 `render()`，而 `render()` 末尾会执行 `renderTable()`；`renderTable()` 会重新 `buildGraph()` 并重写大表，因此仍有明显卡顿。
- 已新增 `renderDrawingOnlyChange()`，隐藏绘图时只同步 `drawing-hidden`、图例和面板高度，不再触发表格重算；绘图显示状态下则只刷新绘图和详情栏。
- 已将“隐藏绘图”“作词/作曲分开”“显示名字”“粒子效果”四个绘图表达开关改为调用 `renderDrawingOnlyChange()`，不再调用整页 `render()`。
- 已将明细表内部图范围固定为 `buildGraph({ roleDisplay: "split" })`，使“作词/作曲分开”只影响绘图区边的视觉合并/拆分，不再影响歌曲明细表的计算路径。
- 已同步 `AGENTS.md` 隐藏绘图性能规则，明确绘图专用开关在隐藏绘图时不得触发图谱重绘、`buildGraph()` 大表重算或明细表重写。

### 增加清除筛选与隐藏绘图清空确认
- 用户要求在顶栏右侧第一行开关区最左侧新增“清除筛选”按钮，并让“隐藏绘图”默认成为第二项。
- 已在 `html_document()` 顶栏模板中将“清除筛选”放在第一位，将“隐藏绘图”包入 `drawing-toggle-shell` 并放在第二位，同时新增向下弹出的 `drawing-clear-popover`，文案为“是否清空筛选？”，选项为“否”和“是”。
- 已实现 `resetFiltersToEmpty()`：清除筛选不是恢复默认值，而是重置为无筛选状态，包括粉丝量 0 到不限、目标歌手全选、隐藏叶节点关闭、仅显示目标歌手关闭、最小歌曲数 1、显示名字关闭、粒子效果关闭、作词/作曲分开关闭，并清除图表选中和明细表搜索。
- 已调整隐藏绘图开关事件：从关闭切换为开启时打开清空确认弹窗；点击“否”只关闭弹窗，点击“是”在保持隐藏绘图开启的前提下执行 `resetFiltersToEmpty({ preserveHideDrawing: true })`。
- 已补充 `tests/test_static_graph_build.py` 断言，覆盖控件顺序、确认弹窗、清除筛选状态重置、隐藏绘图开启时弹窗逻辑和“是/否”按钮行为。
- 已同步 `AGENTS.md` 顶栏筛选重置规则，固定“清除筛选”第一、“隐藏绘图”第二，以及无筛选状态的具体含义。

### 核查 artists 表中的虚拟歌手
- 用户要求检查默认数据库 `artists` 表中是否已有洛天依、乐正绫、言和、初音，以及未点名的其他虚拟歌手。
- 已使用项目指定 Conda Python 直接查询默认 SQLite `data/music_metadata_graph.sqlite3`，避免 PowerShell 中文编码影响判断；当前 `artists` 表共 48595 行。
- 点名对象中，洛天依、乐正绫、言和、初音未来均已在 `artists` 表命中；其中洛天依和乐正绫来自完整歌手列表并带近似粉丝量，言和和初音未来来自歌曲歌手 quick_search 补 MID。
- 扩展核查确认库中还存在镜音铃、镜音双子、镜音连、巡音流歌、MEIKO、KAITO、GUMI、v flower、VY1、重音テト、徵羽摩柯、墨清弦、乐正龙牙、星尘、海伊、诗岸、苍穹、赤羽、牧心、心华、东方栀子、VOCALOID 和 ACE虚拟歌姬等候选虚拟歌手或相关账号。
- 同时统计了候选人在 `song_singers` 与 `song_credit_artists` 中的引用情况；当前命中的虚拟歌手主要作为演唱者出现，作词作曲关系表中暂未发现对应引用。
- 本次只执行只读数据库核查和日志记录，未修改 SQLite 数据。

### 追溯洛天依Official无最终关系引用原因
- 用户追问 `洛天依Official` 为什么没有关系引用，以及库里是否没有她的歌曲。
- 已查询默认 SQLite：`artists.mid=000YMcoP4cQo22` 存在，但 `song_singers` 和 `song_credit_artists` 对该 MID 的最终引用数均为 0，最终 `songs` 表中也没有歌名或标题包含 `洛天依Official` 的歌曲。
- 已追溯 raw 歌曲缓存，`data/raw/qqmusic/singer_homepage_song_tab/003ktdcg3E4kaG/` 中有 9 个 raw 文件包含该 MID，去重后共 33 首歌曲的 `singer[]` 包含 `洛天依Official`。
- 已追溯 validation CSV，这 33 首歌曲全部出现在 `data/processed/validation/song_filtering/csv_views/songs_removed_by_step11_incomplete_credits.csv`，样例包括《孤独症患者》《晨光与橡皮》《春天认得我》《深海流萤》《The Cursive Healing》等。
- 这些歌曲在删除清单中作词、作曲列为空，说明它们不是没有进入过流程，而是在最终保留库前因作词或作曲不完整被过滤掉；因此当前最终关系表不再保留 `洛天依Official` 的演唱关系。
- 本次只做只读追溯和日志记录，未修改 SQLite 数据或 CSV 产物。

### 解释歌词页制作人信息与结构化制作人接口差异
- 用户指出 QQ 音乐客户端播放歌曲时歌词顶部能看到作词作曲信息，但歌曲信息本身似乎没有设置作词作曲。
- 已核对样例《孤独症患者》《晨光与橡皮》《春天认得我》的 `data/raw/qqmusic/song_producer/*.json`，三者均为 `{"Lst": null, "ReinforceMsg": ""}`，说明当前采集使用的 `song.get_producer` 结构化制作人接口未返回作词作曲列表。
- 已核对当前有效源码，作词作曲导入只读取 `song_producer` raw 中的 `Lst/data/producer/producers/list/items` 等结构化列表，并不采集或解析歌词页顶部的制作人文本。
- 当前判断为 QQ 音乐客户端歌词页展示的制作人信息可能来自歌词文本、歌词接口或客户端侧另一个展示数据源，而非当前流程使用的结构化 `song.get_producer` 字段；因此这些歌在客户端可见作词作曲，但在当前数据库中仍被视为结构化制作人缺失。
- 本次只做只读核查和原因分析，未修改采集流程；若后续引入歌词页制作人文本，应作为低于结构化制作人接口置信度的补充来源，并保留来源接口、原始文本和解析方式追溯。

### 小样例验证歌词接口补充作词作曲
- 用户要求测试可搜索歌曲的 QQ 音乐接口，后续补充只需选几首 `洛天依Official` 相关歌曲验证，不逐个验证全部 33 首。
- 已枚举本地 `qqmusic_api` 可用于找歌和查歌的接口：`search.complete`、`search.quick_search`、`search.general_search`、`search.search_by_type(SearchType.SONG)`、`search.search_by_type(SearchType.LYRIC)`、`song.query_song`、`song.get_detail`、`song.get_other_version`、`song.get_producer`、`lyric.get_lyric`，以及专辑侧 `album.get_detail/get_song` 可作为已知专辑入口。
- 已选取《孤独症患者》《晨光与橡皮》《Ebbing Love Flowing Tears》《蓝色共鸣宇宙》四首样例并进行低频联网探针；沙箱内首次请求被网络限制拦截，随后按审批联网重跑成功。
- 结果显示常规搜索、歌曲详情、批量查歌和 `song.get_producer` 均未直接提供可入库的结构化作词作曲；`song.get_producer` 对四首样例仍返回 `{"Lst": null, "ReinforceMsg": ""}`。
- `lyric.get_lyric(song_mid).decrypt()` 可从歌词头部解析出部分样例的词曲：《孤独症患者》为作词“枫黎酥”、作曲“不二兔”；《晨光与橡皮》为作词“不二兔”、作曲“不二兔”；《Ebbing Love Flowing Tears》为作词和作曲“Eden Alison Ro O'Connell”。
- `search.search_by_type(SearchType.LYRIC)` 的精确 `mid` 命中条目也包含歌词 `content` 字段，可作为定位和交叉验证来源；但同名检索会返回其他歌曲，必须按 `song_mid` 精确匹配，不能只按关键词命中判断。
- 《蓝色共鸣宇宙》样例对应的当前 MID 是 Piano Version，`lyric.get_lyric` 返回空，歌词搜索精确 MID 条目也无歌词头部；同名其他版本可返回词曲，但不能直接套用到该版本，除非后续规则确认版本间可继承。
- 探针结果已写入 `data/processed/validation/song_credit_source_probe/luotianyi_official_probe.json` 和 `data/processed/validation/song_credit_source_probe/luotianyi_official_exact_probe.json`；本次未修改采集流程、数据库或正式 CSV。

### 确认 lyric.get_lyric 返回结构
- 用户追问是否实际可靠接口就是 `lyric.get_lyric(song_mid).decrypt()`，以及返回 JSON 内容形态。
- 已基于本地 `qqmusic_api.models.lyric.GetLyricResponse` 确认，HTTP 返回核心字段为 `songID`、`crypt`、`lyric`、`trans`、`roma`；`decrypt()` 是本地模型方法，不是额外请求，会在 `crypt=1` 时把 `lyric`、`trans`、`roma` 解密为可读文本。
- 当前结论为：在 `song.get_producer` 结构化制作人为空时，`lyric.get_lyric(song_mid).decrypt().lyric` 是目前最直接可用的补充来源，但其本质仍是歌词文本解析，置信度应低于结构化制作人接口，且部分歌曲可能返回空歌词。

### 随机 30 首测试歌词头部解析行数
- 用户要求从第十四步作词作曲不完整删除 CSV 中随机抽 30 首，以 batchsize=30 合包请求一次，验证前多少行能稳定解析到词曲作者。
- 已从 `data/processed/validation/song_filtering/csv_views/songs_removed_by_step11_incomplete_credits.csv` 中用固定随机种子 `20260518` 抽取 30 首，使用 `Client.gather(requests)` 一次合包请求 30 个 `lyric.get_lyric(song_mid)`，并对 `crypt=1` 的歌词执行本地 `qrc_decrypt`。
- 合包请求 30 首均成功返回；其中 10 首返回空歌词，13 首同时解析到作词和作曲，7 首有歌词但未同时匹配到作词和作曲。
- 对 13 首可解析样例，按原始解密歌词行计数时，作词作曲最晚出现在第 8 行；按去掉 `[ti]`、`[ar]`、`[al]`、`[by]`、`[offset]` 元信息后的有效行计数时，作词作曲最晚出现在第 3 行。
- 覆盖统计显示原始前 8 行即可覆盖本次所有可解析样例，原始前 5 行覆盖 0 首；有效前 3 行即可覆盖本次所有可解析样例。
- 结果写入 `data/processed/validation/song_credit_source_probe/step14_random30_lyric_batch_probe.json`；控制台打印最后一条结果时因歌名含特殊符号触发 GBK 输出错误，但结果文件已完整写入并回读确认共有 30 条结果。
- 本次只做接口验证和日志记录，未修改采集流程、数据库或正式 CSV。

### 筛选后随机 30 首复测歌词头部解析
- 用户指出前一次 30 首抽样质量不好，应先筛 `album_type` 为 `Single`、`EP`、`录音室专辑` 且 `song_language != 9`，并补充歌词语言差异：日文应识别 `詞/作詞`，英文应大小写不敏感识别 `lyrics by/composed by`。
- 已按用户要求从第十四步删除 CSV 中筛选出 134681 行候选，再用固定随机种子 `20260518` 抽取 30 首，使用 `Client.gather(requests)` 一次合包请求 30 个 `lyric.get_lyric(song_mid)`。
- 已在本次探针解析规则中加入 `作詞/詞`，并对 `Lyrics/Lyricist/Lyrics by/Composed/Composer/Music` 使用大小写不敏感匹配。
- 合包请求 30 首均成功返回；其中 5 首返回空歌词，18 首同时解析到作词和作曲，7 首有歌词但未同时匹配到作词和作曲。
- 对 18 首可解析样例，按原始解密歌词行计数时，作词作曲最晚出现在第 9 行；按去掉 `[ti]`、`[ar]`、`[al]`、`[by]`、`[offset]` 元信息后的有效行计数时，最晚出现在第 4 行。
- 覆盖统计显示原始前 8 行覆盖 17 首、前 10 行覆盖全部 18 首；有效前 3 行覆盖 17 首、前 5 行覆盖全部 18 首。
- 结果写入 `data/processed/validation/song_credit_source_probe/step14_filtered_random30_lyric_batch_probe.json`；本次未修改采集流程、数据库或正式 CSV。

### 识别作曲编曲同标签解析缺口
- 用户指出《浪淘沙》的歌词头部为 `作曲、编曲：李志辉`，当前严格匹配 `作曲` 会漏掉这类作曲和编曲写在同一标签里的情况。
- 已回看未完整解析样例，《浪淘沙》前 4 行依次为歌名、`作词：古柳`、`作曲、编曲：李志辉`、`演唱：罗勤颖`，因此它应可解析出作曲“李志辉”。
- 后续正式解析器应先去掉时间戳并按冒号切分为左侧角色标签和右侧人员值；单字 `词/詞/曲` 只在角色标签严格等于该词时生效，避免把 `编曲` 误判为作曲；`作曲/作詞/作词` 这类明确角色词可在角色标签中包含匹配，以支持 `作曲、编曲`、`作词/作曲`、`作曲 Composer` 等组合标签。
- 风险边界：不能在整句歌词正文中全局搜索 `作曲`；匹配范围应限制在歌词头部有效前几行、且必须是冒号前角色标签，否则可能误把正文或说明性文字当作制作人字段。

### 调整清除筛选按钮样式
- 用户指出顶栏“清除筛选”按钮与周围开关相比过于违和，字号、字体和按钮大小不一致。
- 已调整 `.clear-filters-button` 样式：去掉输入框式边框和背景，改为透明工具栏文字按钮，字号为 12px，颜色与开关文字一致，并保留 hover 与键盘 focus-visible 状态。
- 已补充 `tests/test_static_graph_build.py` 断言，确认清除筛选按钮使用 22px 工具栏高度、透明背景、无边框和 12px 字号，并确认旧 26px 带 padding 的按钮样式不再存在。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的静态网页入口，使当前页面同步按钮样式。

### 细化清除筛选为纯文字按钮
- 用户继续指出“清除筛选”仍未与右侧开关文字对齐，怀疑仍有外框影响，并要求直接删除外框变成纯文字按钮。
- 已进一步调整 `.clear-filters-button`：将 `min-height` 改为 0，显式去除控件外观 `appearance`，保持无边框、无背景、无 padding 的纯文字按钮。
- 已将 hover 和键盘焦点状态从蓝色外框改为文字下划线，避免按钮获得焦点时再次出现外框视觉。
- 已补充 `tests/test_static_graph_build.py` 断言，确认纯文字按钮样式、无外框焦点，以及旧的 22px/26px 控件式高度不再使用。
- 已重新生成 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/` 的静态网页入口，使当前页面同步纯文字按钮样式。

### 整理长流程请求与日志规则
- 用户要求整理完整流程中涉及合包、断点续跑、及时落盘、日志合理跳过和及时打印的通用规则。
- 已核对当前有效源码中的长步骤实现：第 2 步粉丝量补 `get_info`、第 6 步歌曲歌手 `get_info`、第 7 步专辑详情、第 11 步制作人请求使用 `Client.gather()` 按批合包；第 4 步歌曲 Tab 为分页单请求缓存；第 5 和第 12 步 `quick_search` 为低频单请求并逐行重写 CSV；第 17 步头像缓存按间隔启动下载并边完成边写 manifest；第 18 步头像图集使用 fingerprint 跳过和临时目录校验后替换。
- 已在 `AGENTS.md` 同步项目补充规则：合包不得改变一个对象一个 raw JSON 文件的追溯方式；请求型步骤必须 cache 优先、`--force` 才覆盖；坏 JSON 可视为未命中；旧 CSV 不得作为断点输入；成功对象必须及时落盘；失败时保留成功结果并非零退出以便重跑补齐。
- 已补充日志规则：长步骤必须接入 `run_with_log`，打印 `run_id/run_log`、结构化摘要和 `[当前/总数]` 进度；新请求、失败和最后一项必须及时打印，大量缓存命中或数据库命中可间隔打印但要在摘要中计数；跳过必须区分 `fetched/cache_hits/db_matches/skipped/failed` 等状态，不得伪装成成功抓取。
- 本次只整理规则和文档记录，未修改采集、入库、过滤或网页生成代码。

### 改造请求调度为异步等待
- 用户要求把所有请求都改成异步，避免在请求间隔之外还要等待下载时间；已评估可行性，确认 `Client.gather()` 已用于第 2、6、7、11 步，头像缓存第 17 步也已按间隔启动下载并异步等待完成。
- 已修改第 1 步 `collect_singer_list_raw.py`：每个筛选组合先请求第一页获取 `total`，随后对已知剩余页使用 `Client.gather()` 批量启动并等待，避免逐页串行等待响应。
- 已修改第 4 步 `collect_singer_song_tab_raw.py`：同一歌手内部仍按 `HasMore` 顺序请求分页，但多个歌手之间使用异步任务并发推进，避免一个歌手的响应等待阻塞其他歌手启动请求。
- 已修改 `quick_search_artist_mid.py`：歌曲歌手和作词作曲补 MID 的 `quick_search` 按唯一搜索名创建异步任务并按完成顺序处理结果；同名搜索只请求一次，多条来源共享结果；数据库已命中、歧义和空拆分仍即时写 CSV。
- 已同步 `AGENTS.md` 异步请求调度规则：能提前构造请求的步骤应按限速启动请求并异步等待响应；分页依赖上一页 `HasMore` 或 `total` 的流程只能在已知页范围或不同歌手之间并发，不得请求未知页。
- 验证执行 `py_compile` 覆盖 `collect_singer_list_raw.py`、`collect_singer_song_tab_raw.py`、`quick_search_artist_mid.py`、两个补 MID 入口，未报错；定向单元验证 9 个测试通过；全量单元验证 `python -m unittest discover tests` 共 42 个测试通过。

### 修正歌曲 CSV 步骤编号命名
- 用户指出导出 CSV 中的 step 与完整编排实际 step 不一致。
- 已将后续歌曲 CSV 默认导出路径统一为当前 `run_full_pipeline` 编排步骤号：第 10 步专辑类型过滤导出 `songs_removed_by_step10_album_type.csv`，第 13 步作词作曲导入临时表导出 `songs_after_step13_credit_import.csv`，第 14 步作词作曲完整性过滤导出 `songs_removed_by_step14_incomplete_credits.csv` 和 `songs_after_step14_complete_credits.csv`，第 15 步同词曲同名去重导出 `songs_removed_by_step15_same_credit_name_dedupe.csv` 和 `songs_after_step15_same_credit_name_dedupe.csv`，第 16 步语言过滤导出 `songs_removed_by_step16_language_9.csv` 和 `songs_after_step16_language_filter.csv`。
- 已同步 `run_full_pipeline.py`、各过滤/导入脚本默认路径、帮助文案、去重摘要字段和 `tests/test_run_full_pipeline.py` 断言；作词作曲补 MID CSV 的 `source_step` 从旧 `step10_song_credit` 改为当前来源步骤 `step11_song_credit`。
- 已同步 `AGENTS.md` 歌曲入库后过滤规则，避免后续文档继续引用旧步骤号文件名。
- 已检查现有 `data/processed/validation*/` 下已生成的歌曲 CSV，并将旧步骤号文件复制出对应的新步骤号文件名；用户随后确认旧命名 CSV 可以删除，已只删除旧步骤号 CSV，保留新步骤号 CSV。
- 验证执行相关脚本 `py_compile` 未报错；执行 `python -m unittest tests.test_run_full_pipeline` 共 5 个测试通过。

### 追踪周大侠和断了的弦流程状态
- 用户要求检查歌曲名为《周大侠》和《断了的弦》的歌曲在当前完整流程中的入库、过滤和步骤位置。
- 已只读查询正式数据库 `data/music_metadata_graph.sqlite3` 的 `songs`、`song_singers`、`song_credit_artists`、`albums`、`artists`，并读取正式验证 CSV：歌曲入库拒绝、第 10 步专辑类型过滤、第 14 步作词作曲完整性过滤、第 15 步同词曲同名去重、第 16 步语言过滤，以及第 13/14/15/16 步临时保留 CSV。
- 当前正式数据库最终各保留 1 条：`周大侠` 为封茗囧菌《封茗囧菌翻唱合辑》版本，`断了的弦` 也为封茗囧菌《封茗囧菌翻唱合辑》版本；二者作词均为方文山，作曲均为周杰伦。
- 周杰伦原唱《断了的弦》在第 13 和第 14 步后仍存在，随后在第 15 步同词曲同名去重中被删除；原因是同名、同作词、同作曲分组内优先级为 `录音室专辑 > EP > Single > 较小 song id`，封茗囧菌翻唱合辑为 `录音室专辑`，周杰伦原唱所在《寻找周杰伦》为 `EP`。
- `周大侠` 的周杰伦现场专辑版本在第 10 步因 `现场专辑` 被过滤；伴奏、Demo 和部分空专辑/缺专辑信息版本在歌曲入库阶段写入拒绝 CSV，未进入 `songs`。
- 本次未修改源码、数据库、raw 缓存或正式 CSV；验证范围是只读 SQLite 查询和 CSV 回读。

### 分析第十步和第十五步去重设计缺口
- 用户追问第十步是否已特殊设计为保留原唱现场专辑，并询问同名同作词作曲去重规则是否应调整。
- 已核对当前 `filter_songs_by_album_type.py` 实现，第十步实际规则为：专辑类型不在 `Single`、`EP`、`录音室专辑` 白名单内，且同一个 `songs.name` 在当前库中出现不止一首时删除；代码没有识别原唱，也没有按演唱歌手或目标歌手保留现场专辑。
- 当前问题不在于 `录音室专辑 > EP > Single` 这个优先级本身，而在于第十步和第十五步把不同演唱歌手的同名同词曲歌曲放在同一个自动删除竞争里；这会把“同一歌手先发 Single/EP 后收录进录音室专辑”的合理场景，和“原唱/翻唱/现场/覆盖版本”的场景混在一起。
- 初步建议为：第十步不要只按 `songs.name` 删除非白名单专辑类型，应至少加入演唱歌手集合约束；非白名单版本只有在同名且同演唱歌手集合存在白名单版本时才自动删除，否则保留到后续步骤。
- 初步建议为：第十五步同名同作词作曲去重时，`录音室专辑 > EP > Single` 优先级只应在同一演唱歌手集合内部生效；不同演唱歌手集合默认不自动互删，若后续仍要压缩翻唱版本，应另设“原唱候选/翻唱候选”规则或人工检查 CSV。
- 本次只做规则核对和方案分析，未修改源码、数据库或 CSV。

### 纠正同名同词曲去重目标
- 用户纠正前一轮分析：项目目标不是不同演唱歌手之间都保留歌曲条目，而是同名同作词作曲歌曲需要跨演唱歌手合并并保留原唱或主版本。
- 已调整理解：第十五步仍应允许不同演唱歌手之间互相竞争，但不能只用 `录音室专辑 > EP > Single` 判断跨歌手原唱；该优先级更适合用于同一演唱歌手内部的发行版本选择。
- 后续方案应先识别或估算原唱/主版本，再在原唱候选内部使用专辑类型优先级；否则会出现翻唱录音室专辑压过原唱 EP 或现场版本的问题。
- 本次记录为需求纠正和方案边界调整，尚未修改源码、数据库或 CSV。

### 增加歌词补充作词作曲步骤
- 用户要求在结构化制作人 raw 请求之后新增歌词补充分支，只处理结构化作词/作曲不完整的歌曲，并且不得覆盖结构化制作人已有角色。
- 已新增 `collect_song_lyric_credit_raw.py`，按 `songs` 与 `song_producer` raw 判断目标歌曲，只对缺作词或缺作曲的歌曲合包请求 `lyric.get_lyric(song_mid)`，raw 写入 `data/raw/qqmusic/song_lyric_credit/`，解析视图写入 `data/processed/validation/song_lyric_credit/csv_views/song_lyric_credit.csv`。
- 歌词头部解析限制在原始前 10 行、去掉 LRC 元信息后的有效前 5 行内；按冒号前角色标签匹配，单字 `词/詞/曲` 要求标签严格相等，`作词/作詞/作曲` 与英文 `lyrics/lyricist/composed/composer/music` 可在标签内包含匹配，以支持 `作曲、编曲：李志辉` 并避免把 `编曲：某人` 误判为作曲。
- 已调整作词作曲补 MID 步骤：第十三步同时扫描结构化制作人缺 MID 和歌词补充得到的缺失角色姓名，仍使用“先查 artists、再 quick_search”的原有规则，CSV 继续写入 `song_credit_mid_fill.csv`。
- 已调整作词作曲导入步骤：第十四步先导入结构化制作人作词/作曲；只有结构化缺失的角色才从歌词解析结果补入，歌词来源通过 `raw_json_path/raw_row_index` 追溯，不会覆盖结构化已有角色。

### 调整语言过滤到歌曲入库阶段
- 用户要求 `language=9` 过滤移到歌曲入库后立即执行，或者在入库时筛选，同时照常导出过滤掉的歌曲。
- 已调整 `import_singer_song_tab_to_db.py`：歌曲先完成原有完备性约束判断；满足入库约束但 `language=9` 的歌曲写入 `data/processed/validation/song_filtering/csv_views/songs_removed_by_step9_language_9.csv`，不写入 `songs` 和 `song_singers`。
- 已从完整编排中移除后置独立 language 过滤步骤，新增第十二步歌词补充后，总步骤数仍为 20；第十三步补 MID、第十四步导入作词作曲、第十五步完整性过滤、第十六步同名同词曲去重、第十七到二十步仍为网站资源、头像图集、标准网站和 large-graph 网站。
- 已同步相关默认 CSV 步骤号：作词作曲导入临时 CSV 改为 `songs_after_step14_credit_import.csv`，完整性过滤改为 `songs_removed_by_step15_incomplete_credits.csv` / `songs_after_step15_complete_credits.csv`，同名同词曲去重改为 `songs_removed_by_step16_same_credit_name_dedupe.csv` / `songs_after_step16_same_credit_name_dedupe.csv`。
- 已同步 `AGENTS.md` 项目规则和 `pyproject.toml` 命令入口 `mr-collect-song-lyric-credit-raw`。

### 验证歌词补充与编排调整
- 已执行项目 Python 的 `py_compile`，覆盖歌词补充采集、作词作曲补 MID、作词作曲导入、歌曲入库、完整编排、作词作曲完整性过滤和同名同词曲去重脚本，未发现语法错误。
- 已新增 `tests/test_collect_song_lyric_credit_raw.py`，覆盖 `作曲、编曲` 可解析为作曲、`编曲` 不会误判为作曲、日文 `詞` 和英文大小写不敏感标签可解析、超出头部有效行限制的词曲不会被解析。
- 已更新 `tests/test_run_full_pipeline.py`，覆盖新增 `lyric_credit_raw_dir`、第九步 language 删除 CSV、第十二步歌词补充模块、第十四至十六步新临时 CSV 路径和网站步骤仍为第十七至二十步。
- 已执行 `python -m unittest tests.test_collect_song_lyric_credit_raw tests.test_run_full_pipeline`，共 9 个测试通过。

### 核查歌词补充落盘状态
- 用户询问通过歌词补充作词作曲时是否有落盘。
- 已核对当前实现：第十二步 `collect_song_lyric_credit_raw.py` 会把 `lyric.get_lyric(song_mid)` 原始响应保存到 `data/raw/qqmusic/song_lyric_credit/`，并把解析检查视图写入 `data/processed/validation/song_lyric_credit/csv_views/song_lyric_credit.csv`。
- 已核对第十四步导入逻辑：只有结构化制作人缺失的角色才会读取歌词 raw 解析结果补入 `song_credit_artists`，补入关系通过 `raw_json_path` 和 `raw_row_index` 追溯到歌词 raw，不覆盖结构化已有角色。
- 只读检查当前本地数据：歌词 raw 目录已有 92850 个 JSON 文件；歌词解析 CSV 有 92850 行，其中 38336 行解析到至少一个词曲角色、36212 行同时解析到作词和作曲。
- 只读查询当前正式数据库 `song_credit_artists`：现有 181371 条作词作曲关系，但 `raw_json_path` 指向 `song_lyric_credit` 的关系数为 0，说明当前最终库中尚没有保留下来的歌词来源关系，或最后一次导入/过滤结果未包含歌词来源关系。

### 核查歌词制作人 MID 补全来源
- 用户追问歌词解析到制作人只有姓名时 MID 在哪里补。
- 已核对当前实现：第十三步 `fill_song_credit_missing_mids.py` 会扫描第十二步歌词 raw 解析出的姓名，只处理结构化制作人缺失的角色，并把来源标记为 `step12_song_lyric_credit`。
- MID 补全复用 `quick_search_artist_mid.py`：先在当前 `artists` 表按姓名精确唯一匹配；库内唯一命中时写 `db_matched`，库内多 MID 时写 `db_ambiguous_name` 且不自动选择；库内未命中时请求或读取 `data/raw/qqmusic/quick_search_artist_mid/song_credit/` 下的 quick_search raw，只有搜索结果中歌手姓名精确且唯一命中时才把该 MID 导入 `artists`。
- 第十四步 `import_song_credits_to_db.py` 不读取补 MID CSV 作为关系输入，而是重新读取 `artists` 的唯一姓名映射；歌词姓名能唯一解析到 `artists.mid` 时才写入 `song_credit_artists.artist_mid`，关系来源仍追溯到歌词 raw。
- 只读检查当前 `song_credit_mid_fill.csv`：来自 `step12_song_lyric_credit` 的歌词姓名来源共有 21209 行，其中 `db_matched` 11019 行、`matched` 1682 行、`db_ambiguous_name` 1191 行、`ambiguous_exact_match` 126 行，其余为未匹配或无候选。

### 分析第十二步本地缓存扫描慢
- 用户询问第十二步扫描本地缓存为什么仍然很慢。
- 已核对 `collect_song_lyric_credit_raw.py`：本地缓存命中时仍会读取歌词 JSON、执行 `qrc_decrypt` 解密、解析头部词曲、统计歌词行数，并最终重写 `song_lyric_credit.csv`，不是只检查文件是否存在。
- 只读计时显示读取 2000 个歌词 JSON 并做 JSON 解析约 0.47 秒；按当前歌词解析逻辑处理 100 个缓存文件约 5.48 秒，说明主要瓶颈是歌词解密与解析而不是单纯磁盘枚举。
- 已识别当前实现中 `build_csv_row()` 会先调用 `parse_lyric_credit_rows()` 解密一次，又调用 `lyric_text_from_payload()` 统计行数再解密一次；缓存命中越多，重复解密成本越明显。
- 当前完整缓存规模为歌词 raw 92850 个 JSON；按上述小样本速度，纯本地重建解析 CSV 也会达到分钟级到小时级，且日志只每 1000 个 cache hit 打印一次，容易看起来像“卡在扫描本地”。

### 核查歌词 raw 落盘内容范围
- 用户询问歌词补充落盘的是完整歌词还是前几行。
- 已核对 `collect_song_lyric_credit_raw.py`：`dump_json()` 保存的是 `lyric.get_lyric(song_mid)` 的完整原始响应 payload，未在写 raw JSON 前截断歌词字段。
- 前几行限制只发生在 `parse_lyric_credit_rows()` 的解析阶段：只在原始前 10 行、去掉 LRC 元信息后的有效前 5 行里寻找作词作曲标签。
- 解析 CSV 不保存完整歌词，只保存 `matched_lines_json`、`lyric_line_count`、解析出的作词/作曲姓名和 raw 路径；需要回看完整接口响应时应打开 `data/raw/qqmusic/song_lyric_credit/*.json`。

### 讨论歌词缓存改为最小证据
- 用户提出可否把第十二步歌词落盘放到解析阶段，或把落盘内容改成解密后的前 10 行，不再保存完整加密歌词。
- 已形成初步判断：该方向更符合项目“不提交大量歌词”和最小化本地缓存的边界；完整加密歌词虽然不是明文，但可由本地库解密，仍不适合作为长期 raw 缓存。
- 目标效果应改为：第十二步联网请求后只在内存中持有完整接口响应，立即解密并抽取用于作词作曲解析的头部证据，再落盘有限 JSON；CSV 和第十三、十四步继续读取该有限证据，不依赖完整歌词。
- 建议有限 JSON 至少保存 `schema_version`、`source_api`、`song_mid`、`song_id`、`song_name`、`fetched_at`、`producer_missing_roles`、解密后的原始前 10 行、去掉 LRC 元信息后的有效前 5 行、解析出的词曲行、原接口 `crypt` 状态和必要的空歌词/解析失败状态，不保存完整 `lyric/trans/roma/qrc`。
- 风险边界：去掉完整歌词 raw 后，后续如果需要调整解析窗口或检查正文以外信息，只能重新请求接口；旧 `song_lyric_credit/*.json` 需要迁移或重建，否则会出现完整 raw 与有限证据两种格式混用。
- 初步实现方案应同步改第十二步采集、歌词解析函数、第十三步补 MID、第十四步关系导入和一键流程检查，并新增兼容测试覆盖旧完整 raw、有限证据 JSON 和空歌词样例。

### 确认旧歌词 raw 读时迁移策略
- 用户提出兼容旧完整加密缓存时，可以在读到旧格式后解析并按新的有限证据格式落盘覆盖旧文件。
- 已调整方案判断：采用读时迁移比一次性全目录清理更稳，能够随着第十二、十三、十四步正常读取逐步淘汰旧完整歌词缓存。
- 迁移规则应为：识别到旧 `lyric.get_lyric` 完整响应格式时，只在内存中解密并抽取有限证据，随后用临时文件加原子替换覆盖同一路径；若旧 JSON 损坏或无法解析，不覆盖原文件并按失败状态报告。
- 新格式文件仍可沿用原 `data/raw/qqmusic/song_lyric_credit/{song_mid}.json` 路径，避免改动数据库和 CSV 中的 raw 路径追溯字段；内容通过 `schema_version` 或 `cache_kind` 区分有限证据格式。
- 后续实现应统计并打印 `migrated_legacy_raw`、`evidence_cache_hits`、`fetched`、`failed_migrations` 等计数，避免把旧 raw 迁移伪装成普通缓存命中。

### 设计歌词补充有限证据缓存完整方案
- 用户要求整理不保存完整加密歌词、改为解密后前几行有限证据落盘的完整方案。
- 目标效果为：第十二步联网请求仍能补充结构化制作人缺失的作词/作曲，但本地长期缓存只保存解析词曲所需的头部证据，不保存完整 `lyric`、`trans`、`roma` 或 `qrc` 字段。
- 新缓存仍使用 `data/raw/qqmusic/song_lyric_credit/{song_mid}.json` 路径，文件通过 `cache_kind=qqmusic_lyric_credit_evidence` 和 `schema_version=1` 标识有限证据格式，保留现有 CSV 和数据库 raw 路径追溯口径。
- 有限证据 JSON 应包含歌曲标识、来源接口、抓取时间、结构化制作人缺失角色、原接口 `crypt` 状态、歌词是否为空、解密后原始前 10 行、去 LRC 元信息后的有效前 5 行、解析出的词曲行、解析状态和错误摘要；不得保存完整歌词正文、翻译、罗马音或 qrc 全文。
- 第十二步应在请求成功后只在内存中持有完整响应，解密一次并构造有限证据 JSON，然后立即写入缓存；缓存命中时直接读取有限证据，不再重复解密。
- 旧完整缓存兼容方案为读时迁移：第十二、十三、十四步读到旧完整响应时，解析并覆盖为有限证据；迁移失败不覆盖原文件，并输出 `failed_migrations`。
- 第十三步补 MID 和第十四步导入作词作曲应改为读取统一的 `parsed_credit_rows`，不再假设缓存文件一定是完整 `lyric.get_lyric` 响应。
- 验证方案包括单元测试覆盖新格式解析、旧格式读时迁移、空歌词、解密失败、只补结构化缺失角色、不保存完整歌词字段，以及小样本运行确认计数中区分 `evidence_cache_hits`、`migrated_legacy_raw`、`fetched` 和 `failed_migrations`。
- 风险边界为：未来若需要扩大解析窗口或回看完整歌词，只能重新请求接口；本轮不应一次性删除全部旧缓存，也不应把完整歌词复制到 CSV、日志、数据库或新缓存字段中。

### 增加第十三步来源扫描进度日志
- 用户确认第十三步主要问题是扫描 `song_producer` 和 `song_lyric_credit` raw、收集缺 MID 来源时没有进度输出，导致 raw 很多时看起来像卡住；本轮不调整 quick_search 阶段的缓存命中和数据库命中节流。
- 已修改 `fill_song_credit_missing_mids.py`：在 `collect_missing_credit_sources()` 开始时打印 `scan_credit_sources` 摘要，扫描 producer raw 时每 1000 个和最后一个打印 `[当前/总数] scan_credit_sources`，并在结束时打印 `scan_credit_sources_summary`。
- 新增扫描日志字段包括 producer raw 文件总数、目标歌曲数、跳过非目标歌曲数、已收集来源数、已检查歌词 raw 数和歌词补充来源行数，便于判断第十三步当前处于前置扫描阶段还是后续 quick_search 补 MID 阶段。
- 已新增 `tests/test_fill_song_credit_missing_mids.py`，用临时 SQLite 和 producer/lyric raw 样例验证扫描进度、跳过非目标 raw、歌词来源计数和来源步骤标识。
- 验证执行 `py_compile fill_song_credit_missing_mids.py tests/test_fill_song_credit_missing_mids.py` 未报错；定向单元验证 `python -m unittest tests.test_fill_song_credit_missing_mids` 通过 1 个测试。

### 梳理各类扫描步骤总量可知性
- 用户追问扫描阶段是在开始时知道总量，还是只能扫到没有更多才知道结束，并明确问题不只针对第十三步，而是所有涉及扫描的步骤。
- 已核对当前 pipeline 代表性实现：本地 raw 目录扫描和 SQLite 查询结果扫描通常可以在正式处理前得到候选总量，例如 `glob()` 结果列表、`SELECT ... fetchall()` 结果或已解析的目标列表。
- 已确认外部分页请求类步骤不完全相同：完整歌手列表第一页返回 `total` 后可推算剩余页数；歌手主页歌曲 Tab 目前依赖每页 `HasMore` 判断结束，单个歌手的总页数不是开始前已知。
- 当前判断：长步骤日志应区分 `known_total`、`discovered_total` 和 `unknown_until_has_more_false` 三种口径；本地扫描应优先打印 `[当前/总数]`，分页请求则应打印当前页、累计行数和结束原因。

### 区分均匀进度和请求型进度
- 用户继续要求分析哪些步骤的进度日志属于均匀本地进度，不会发生外部请求，例如本地扫描和入库。
- 已按当前完整流程判断：本地 raw 文件扫描、SQLite 查询结果处理、入库校验、过滤和 CSV 准备通常属于不发外部请求的进度，`[当前/总数]` 更接近线性进度；但单项解析、数据库查询和 CSV 排序仍可能让速度有小幅波动。
- 请求型进度包括歌手列表 raw、粉丝量补齐、主页歌曲 Tab、歌曲歌手信息、专辑详情、制作人 raw、歌词补充 raw、quick_search 补 MID 和头像下载；这些进度即使有 `[当前/总数]`，也会受网络、缓存命中、批量请求和失败降级影响，不应按线性剩余时间判断。
- 当前判断中第 9、14、15、16 步的主要本地处理或 CSV 准备更接近均匀进度；第 13 步新增的 `scan_credit_sources` 是均匀本地扫描，但后续 quick_search 是请求/缓存混合进度。

### 设计终端进度条和定时日志心跳
- 用户提出终端显示进度条时，run log 不应按每 1000 条或固定条数打印，而应每两分钟打印一行并带时间戳前缀。
- 当前判断为该方案更适合长流程日志：按墙钟时间输出能稳定判断进程仍在推进，避免不同数据规模或不同机器上按条数输出过密或过稀。
- 建议统一进度工具在终端使用 tqdm 纯进度条，日志侧输出机器可读心跳行，格式包含 UTC 时间戳、进度标题、当前值、总量、百分比、已耗时和可选速率；每个进度段开始打印标题，结束时无论是否满两分钟都打印完成摘要。
- 风险边界：定时心跳只能在循环迭代边界检查时间；如果单个对象处理本身阻塞超过两分钟，仍需要在该对象内部或请求型步骤另行打印请求开始/失败日志。

### 实现本地均匀进度 tqdm 和日志心跳
- 已安装 `tqdm` 到项目指定 Conda 环境，并在 `pyproject.toml` 依赖中新增 `tqdm`。
- 已新增 `music_metadata_graph/progress.py`，提供 `iter_progress()`：终端可交互时显示纯 tqdm 进度条，run log 中只写 `progress_start`、每 120 秒一次的 `progress` 心跳和 `progress_done`，每条日志带 UTC 时间戳、标题、当前值、总量、百分比、耗时和速率。
- 已扩展 `run_log.py`：暴露真实终端 stdout 和当前异步日志 writer，使 tqdm 输出只写终端，日志心跳直接写 run log，避免 tqdm 回车刷新污染日志文件。
- 已将本地均匀进度替换为 `iter_progress()`：第 8 步专辑详情 raw 加载，第 9 步歌曲 Tab raw 加载、歌曲 raw 分组、歌曲入库约束评估，第 13 步作词作曲来源 raw 扫描，第 14 步制作人 raw 扫描，以及第 14/15/16 步共享的歌曲 CSV 准备。
- 请求型步骤、quick_search 轮、头像下载和完整流程 step precheck/postcheck 未改为 tqdm，继续保留结构化日志。
- 已新增 `tests/test_progress.py`，覆盖 start/定时/done 日志、run log 与 tqdm 输出分流；已更新 `tests/test_fill_song_credit_missing_mids.py` 以匹配第十三步扫描的新进度日志。
- 验证执行 `py_compile` 覆盖新增进度工具、运行日志、被替换的 pipeline 文件和相关测试文件，未报错；定向单元验证 `tests.test_progress tests.test_fill_song_credit_missing_mids tests.test_filter_songs_by_album_type tests.test_run_full_pipeline` 共 9 个测试通过。
- 真实缓存 smoke 执行 `fill_song_credit_missing_mids --max-names 0`，第十三步扫描 324419 个 producer raw 文件完成，run log 中只记录 `progress_start/progress_done` 文本心跳，没有 tqdm 动态回车内容。

## 2026-05-18

### 再次清理开发日志异常空行
- 用户反馈日志又出问题，要求检查当前异常。
- 复核确认本次异常仍为空行膨胀：清理前 `develop_log.md` 文件大小为 1349776 字节，共 521543 行，其中非空行 1856 行；未发现隐藏控制字符或 U+FFFD 替换字符。
- 本次生成压缩备份 `develop_log.before_blank_cleanup_20260518_191127.md.gz` 后执行机械空行压缩，保留全部非空内容，并在标题前保留单个空行以维持 Markdown 可读性。

### 拆分多轮进度阶段提示
- 用户指出同一步骤内多个轮次的进度输出不能直接混在一起，尤其第十三步旧日志中第一轮到 `[55005/55005]` 后又出现 `[17000/55005]`，看起来像进度倒退。
- 已在 `progress.py` 新增统一阶段标题 `== 标题 ==`，并让 `iter_progress()` 在每个本地进度条前自动打印阶段标题；第 8、9、13、14、15、16 步的本地均匀轮次切换现在会有明确标题分隔。
- 已修改 `quick_search_artist_mid.py`：补 MID 流程拆成“解析缺失音乐人姓名并检查本地 artists”和“请求或读取 quick_search raw 并写入匹配结果”两个阶段；第二阶段进度改用 quick_search 搜索名完成数作为分母，不再复用第一阶段唯一姓名序号，避免异步结果按完成顺序打印时出现序号倒退。
- 已新增 `tests/test_quick_search_artist_mid.py`，验证 quick_search 阶段会打印阶段标题，并且搜索阶段输出 `[1/2]`、`[2/2]` 而不是继续使用第一阶段 `[2/3]` 这类混合分母。

### 探测 other_version 支撑原唱归并
- 用户表示可以放宽目标，不要求归到主版本，只要归到原唱，并询问是否有比启发式更靠谱的方案。
- 已核对本地 `qqmusic-api-python`，存在 `song.get_other_version(value)`，对应 QQ 音乐 `music.musichallSong.OtherVersionServer.GetOtherVersionSongs`，返回 `versionList`。
- 已联网只读探测《断了的弦》和《周大侠》的周杰伦/封茗囧菌版本；结果显示从封茗囧菌《断了的弦》请求 other_version 返回周杰伦《断了的弦》，从封茗囧菌《周大侠》请求 other_version 返回周杰伦《大灌篮 电影原声带》版本；从周杰伦《断了的弦》请求 other_version 返回多个翻唱版本；从周杰伦现场版《周大侠》请求返回空列表。
- 当前判断：`get_other_version` 比单纯发行日期、作曲人是否演唱等启发式更可靠，适合作为原唱归并的主要证据，但它不是直接返回“原唱字段”，需要围绕同名同词曲候选构建版本关系图，并用平台返回的版本关系把翻唱候选指向原唱候选。
- 后续规则设计应避免第十步提前删除潜在原唱；原唱归并应放在作词作曲导入之后，结合当前库候选和 other_version raw 证据执行。
- 本次只做接口能力探测和方案分析，未修改源码、数据库或正式 CSV。

### 扩展验证 other_version 原唱归并样本
- 用户要求用周杰伦相关《世界末日》《蜗牛》《一路向北》《我是如此相信》，以及当前最终保留歌曲中专辑名包含“翻唱”的样本验证 `song.get_other_version` 对原唱归并的可靠性。
- 已从正式数据库和正式过滤 CSV 定位样本：四首周杰伦相关歌曲覆盖最终保留、第十步删除、第十四步删除、第十五步删除和入库拒绝状态；翻唱专辑样本覆盖刘瑞琦、王俊凯、周深、排骨教主、封茗囧菌等当前最终保留歌曲。
- 联网只读批量请求 `song.get_other_version` 后观察到：鹿晗/曲肖冰/周杰伦现场《世界末日》均指向 S.B.D.W《世界末日》；周杰伦/庾澄庆等《蜗牛》版本指向许茹芸、齐秦、动力火车、熊天平《蜗牛》；《一路向北》的周杰伦 Live、吴岱林、丁芙妮版本指向周杰伦《J III MP3 Player》版本；多个翻唱专辑样本能指向平台版本关系中的更标准版本，例如 TFBOYS《宠爱》、A-Lin《P.S.我爱你》、大塚愛《星象仪》、洛天依/言和《普通Disco》、周杰伦《断了的弦》和《周大侠》电影原声带版本。
- 同时观察到两个限制：对原唱或主版本本身请求 `other_version` 时，返回的可能是翻唱列表，不能把返回第一条直接当原唱；部分返回目标 MID 当前不在最终库或已经被第十五步删除，例如《断了的弦》周杰伦 EP、《普通Disco》洛天依/言和 Single、《房间》刘瑞琦《私房歌》版本。
- 当前判断：`other_version` 适合作为原唱归并主证据，但流程必须在删除前采集并保存版本关系 raw；如果平台返回的原唱目标不在当前库，应把目标补入或至少阻止翻唱版本替代原唱直接保留。
- 本次未修改源码、数据库或正式 CSV；验证仅包含只读 SQLite/CSV 查询和联网只读接口探测。

### 核查周杰伦给别人写的歌流程状态
- 用户提供 `周杰伦给别人写的歌_每行歌名歌手.txt`，要求检查清单歌曲在当前完整流程中的状态。
- 已读取清单共 174 行，按歌名为主、歌手为辅助匹配当前默认 SQLite、歌曲入库拒绝 CSV、各步骤过滤 CSV 和主页歌曲 Tab raw；对 `4 in Love`、`Super Junior-M`、`Jesus Fashion Family` 这类歌手名含空格的行做了手动解析修正。
- 已生成核查 CSV `data/processed/validation/manual_checks/jay_chou_written_songs_flow/jay_chou_written_songs_flow_check.csv`，每行记录原始清单、解析歌名/歌手、流程状态、命中歌曲 MID/ID、实际演唱者、专辑、作词、作曲和来源 CSV/raw。
- 核查结果：按清单歌手精确或近似命中的行共 102 行，其中最终 `songs` 保留 76 行，歌曲入库拒绝 3 行，第 10 步专辑类型过滤 1 行，第 14 步作词作曲不完整过滤 21 行，第 15 步同名同词曲去重过滤 1 行；另有 72 行未命中清单歌手，其中 50 行在当前流程输出和 raw 中未找到，22 行只命中了同名但非清单歌手版本。
- 本次为只读核查和报告导出，未修改 SQLite、raw 缓存或正式流程代码。

### 生成周杰伦给别人写的歌逐条解释报告
- 用户反馈上一版状态统计看不懂，要求逐条解释每首歌是初始范围未包含、某一步过滤还是最终包含。
- 已基于上一版核查 CSV 生成 `data/processed/validation/manual_checks/jay_chou_written_songs_flow/jay_chou_written_songs_flow_explained.md` 和同目录 `jay_chou_written_songs_flow_explained.csv`。
- 逐条解释报告对每行输出清单原文和中文说明，说明是否最终包含、是否歌曲入库拒绝、第 10 步专辑类型过滤、第 14 步作词作曲不完整过滤、第 15 步同名同词曲去重，或当前初始范围未包含；只命中同名非清单歌手版本时单独说明为清单版本未命中。
- 已抽查《落雨声》《You Will Get My Heart》《倒带》《亲爱的那不是爱情》《命中注定》《幸福微甜》《Jesus Fashion》等边界样例，确认解释文本包含命中歌手、专辑、词曲或过滤原因。
- 本次只生成解释报告和开发日志，未修改数据库、raw 缓存或流程源码。

### 细化 other_version 原唱归并流程方案
- 用户要求把更靠谱的 `song.get_other_version` 原唱归并流程说详细。
- 已形成方案方向：第十步从提前删除非白名单同名歌曲调整为保守标记或只删除明确噪声；在作词作曲导入后、最终去重前新增版本关系请求步骤，按同名同词曲候选请求并缓存 `song.get_other_version` raw；随后在去重步骤中优先按平台版本关系选择被指向的原唱候选，只有缺少版本关系证据时才回退专辑类型优先级。
- 方案强调：`other_version` 返回的是其他版本列表，不是直接原唱字段；从翻唱或派生版本查通常可指向原唱，从原唱查通常返回翻唱列表，因此不能把任意返回第一条当原唱，必须在同名同词曲组内构建“源版本 -> 返回候选”的关系图。
- 方案边界：若平台指向的原唱 MID 不在当前库，不能让当前翻唱版本自动胜出，应导出待补原唱清单或补采该 MID；若组内没有稳定入边或出现冲突，应进入人工检查 CSV，不强行归并。
- 本次只记录流程方案，未修改源码、数据库或正式 CSV。

### 核查初始未包含歌曲演唱者是否在第一步歌手列表
- 用户要求针对大量初始范围未包含的歌曲，列出去重演唱者，并检查这些演唱者是否存在于第一步请求到的完整歌手列表 raw 中。
- 已从逐条核查结果中提取 72 行初始未包含或只命中同名非清单歌手的记录，按清单演唱者拆分去重后得到 41 个演唱者。
- 已扫描 `data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all/page_*.json` 的 `singerlist/hotlist` 中 `name/title/other_name` 字段做严格规范化匹配；第一步歌手列表中仅精确命中 `许慧欣` 1 个演唱者，其余 40 个未命中。
- 已输出 `data/processed/validation/manual_checks/jay_chou_written_songs_flow/initial_missing_expected_singers_step1_check_strict.csv`，记录每个演唱者、涉及歌曲、是否在第一步歌手列表、命中 MID 和 raw 路径。
- 本次为只读核查和报告导出，未修改数据库、raw 缓存或流程源码。

### 为失败和剔除 CSV 增加原因代码列
- 用户要求所有入库失败和过滤剔除 CSV 在导出时最后增加原因列，原因值使用有意义的短词组代码，不使用长句自然语言。
- 已修改歌曲 CSV 通用写出工具，新增可选 `reason_code` 末列；普通保留和临时查看 CSV 默认不输出该列。
- 已覆盖第九步歌曲入库拒绝 CSV、第九步 `language=9` 剔除 CSV、第十步专辑类型剔除 CSV、第十五步词曲不完整剔除 CSV、第十六步同名同词曲去重剔除 CSV，以及手动语言过滤剔除 CSV。
- 已修改第八步专辑入库拒绝 CSV，将短代码 `reason_code` 放在最后一列，并继续保留脚本内部原有原因统计所需字段。
- 已同步 `AGENTS.md` 中专辑入库、歌曲入库失败和歌曲 CSV 列规则，明确失败/剔除 CSV 追加 `reason_code`，临时保留 CSV 不追加原因列。

### 验证失败和剔除 CSV 原因代码列
- 已执行 `py_compile` 覆盖本轮修改的 CSV 工具、专辑入库、歌曲入库、歌曲过滤脚本和新增测试文件，未发现语法错误。
- 已执行 `python -m unittest tests.test_rejection_reason_csv tests.test_filter_songs_by_album_type`，共 4 个测试通过。
- 新增测试确认歌曲入库拒绝 CSV 和专辑入库拒绝 CSV 的最后一列为 `reason_code`，并确认普通歌曲 CSV 不会误输出原因列。

### 探测歌手数字 ID 请求接口
- 用户询问第一步歌手列表中缺失的数字 ID 是否可直接请求歌手。
- 已确认 `qqmusic_api` 当前 `singer.get_info()`、`get_tab_detail()`、`get_album_list()`、`get_mv_list()` 等封装方法公开参数均为歌手 MID。
- 已联网探测 `music.UnifiedHomepage.UnifiedHomepageSrv.GetHomepageHeader`：已知有效歌手 BEYOND 使用 `SingerMid=002pUZT93gF4Cu` 成功，但改用 `SingerId=2`、`SingerID=2` 或 `singerId=2` 均失败；此前对缺失 ID 传入 `get_info()` 也返回 CGI 错误。
- 已联网探测 `musichall.song_list_server.GetSingerSongList`：已知有效歌手 BEYOND 使用 `singerId=2` 或 `singerID=2` 均成功，并在响应中返回 `singerMid=002pUZT93gF4Cu` 和歌曲列表。
- 当前结论：主页信息接口不能按数字 ID 请求；旧歌手歌曲列表接口可按数字 ID 请求并可用于把有效数字 ID 反查 MID，但它不是主页 Tab 接口，也不等价于正式第四步歌曲来源。

### 探测按 MID 请求歌手接口的地区字段
- 用户指出旧歌曲列表接口只能得到 MID 和部分名字，继续询问按 MID 请求歌手接口是否能得到 `area_id`。
- 已用 BEYOND、数字 ID 3 反查的 dMDM、数字 ID 16 反查的杜德伟、以及数字 ID 11 反查到但无歌曲的 MID，联网探测 `get_info`、`get_desc`、`get_similar`、`get_songs_list`、`get_album_list`、`get_mv_list`、`get_tab_detail(song)` 和 `get_tab_detail(wiki)`。
- `get_info`、主页 Tab、歌曲列表、专辑列表、MV 列表和相似歌手返回中未发现 `area`、`area_id`、`country` 等地区相关字段。
- `get_desc` 返回中存在 `singer_list[0].ex_info.area`，但样本 BEYOND、dMDM、杜德伟均为 `0`，无歌曲样本未返回可用地区字段；该字段不等同于第一步歌手列表 raw 中可用于过滤的 `area_id`。
- 当前结论：按 MID 的现有歌手接口没有稳定可用的第一步 `area_id`；补全缺失数字 ID 的 MID 后，若需要按当前 `area_id in (0, 1)` 规则过滤，仍不能仅依赖 `get_info` 或其他按 MID 接口恢复地区。

### 按第一步 area_id 样本验证 get_desc 地区字段
- 用户要求从第一步歌手列表每个 `area_id` 值各取 3 人，用 MID 请求 `get_desc([mid])` 验证返回结果。
- 已确认第一步 raw 中存在 `area_id` 值 0、1、2、3、4、5、6，并按每类最小数字 ID 取 3 个样本，共 21 个 MID。
- 联网请求 `get_desc([mid])` 后，21 个样本均成功返回 `singer_list[0].basic_info`，其中 `basic_info.singer_id`、`basic_info.singer_mid`、`basic_info.name` 与第一步样本可对应。
- 21 个样本的 `singer_list[0].ex_info.area` 全部为 `0`，覆盖第一步 `area_id` 为 0 到 6 的所有类别。
- 当前结论进一步确认：`get_desc` 的 `ex_info.area` 不是第一步 `area_id` 的可用映射，不能用它恢复或校验当前第三步入库所需的地区过滤字段。

### 分析 Client.gather 合包请求原理
- 用户询问合包请求的底层原理以及设置很大合包量的后果。
- 已复核当前项目规则和源码调用点，确认本项目所说合包请求主要指 qqmusic_api.Client.gather()：业务语义仍是一个对象一个 request 描述符，脚本把多个描述符按批交给 client.gather()，并保持一个对象一个 raw JSON 文件的落盘追溯。
- 当前指定 Conda 环境未安装 qqmusic_api 包，无法在本机直接 inspect 安装包源码；结论基于项目调用方式、既有运行日志和 Client.gather() 这类 QQ 音乐 CGI 合包接口的一般机制。
- 形成解释结论：合包通常把多个子请求编码到一次 HTTP CGI 请求体中，由服务端分别执行并返回按

eq_0、

eq_1 等键组织的子响应；合包量过大不会改变业务请求数量，只会减少 HTTP 往返次数，同时增加单次请求体、响应体、服务端处理时间、超时概率、批次整体失败影响范围和风控风险。

- 本次只做原理分析和日志记录，未修改源码或运行外部采集请求。

### 核查 QQ 音乐 id 和 mid 对应关系
- 用户询问 QQ 音乐 `id` 和 `mid` 的对应关系，以及是否有说明计算方式。
- 已核对当前 `AGENTS.md`、开发日志、建表代码和导入代码：项目当前没有实现 `id` 与 `mid` 的计算或互转逻辑，也没有记录可信的计算公式。
- 当前有效规则为：`artists` 只使用 QQ 音乐 `mid` 作为主键且不保存歌手数字 `id`；`songs` 使用 `mid` 作为主键并保存数字 `id` 唯一约束；`albums` 使用 `mid` 作为主键并保存数字 `id` 唯一约束。
- 代码层面只把接口 raw 中返回的 `id` 和 `mid` 原样抽取为两个平台字段：歌手入库会主动移除旧 `id/pmid/singer_pic` 列；歌曲和专辑入库会校验 `mid`、`id` 均非空且 `id` 不重复，但不会由一个字段推导另一个字段。
- 当前结论：`id` 与 `mid` 应视为 QQ 音乐接口返回的并列身份标识；可通过同一接口响应、搜索或特定支持数字 ID 的接口反查对应关系，但项目中没有、也不应假设存在稳定公开计算方式。

### 分析 id 推导 mid 的可行性
- 用户明确希望找出计算方式，以便不再通过接口由数字 `id` 反查 `mid`。
- 已检索公开资料，未找到可信的 QQ 音乐 `id -> mid` 本地计算公式；公开接口文档和第三方 API 说明多把 `id` 与 `mid/songmid` 作为不同入参或通过查询服务获取 `mid`。
- 已从本地 QQ 音乐 raw 中抽取已有 `id/mid` 样本做模式验证：专辑详情唯一对约 11.7 万组、歌曲唯一对约 52.6 万组、第一步歌手列表 6803 组、歌曲演唱者唯一对约 4.3 万组。
- 样本观察到各类 `mid` 基本固定为 14 位，前三位主要分布在 `000`、`001`、`002`、`003`、`004`；数字 `id` 的十进制、base36、base62 表示几乎不出现在对应 `mid` 中，少量命中可解释为短字符偶然命中。
- 当前判断：没有证据支持 `mid` 是由数字 `id` 通过简单进制、前缀、后缀或可逆短码计算得到；更可能是 QQ 音乐服务端分配的另一套不透明标识或依赖服务端映射表。
- 可行替代方向是维护本地 `id <-> mid` 映射缓存：从已采集 raw、搜索结果、歌曲/专辑/歌手接口响应和特定支持数字 ID 的旧接口中渐进补全；缺失时仍需接口查询或放弃该对象。

### 评估两千万 ID 场景下避免反查 MID
- 用户指出两千万量级下，即使 20 个一组合包请求，也需要数天才能通过接口由 `id` 反查 `mid`，因此希望绕开反查。
- 已核对本地 `qqmusic_api` 源码：歌曲侧 `query_song`、`get_detail`、`get_other_version`、`get_producer`、`lyric.get_lyric` 均支持数字歌曲 ID；专辑侧 `album.get_detail` 和 `album.get_song` 支持数字专辑 ID；歌手主页、歌手详情、歌手主页 Tab、歌手专辑和歌手 MV 等当前封装主要支持歌手 MID。
- 当前判断：如果两千万对象主要是歌曲或专辑，流程不应先全量补 MID，而应改为以数字 `id` 作为采集入口和本地稳定键，只有在接口响应自然返回 `mid` 时再补充映射。
- 真正绕不开 MID 的场景主要是当前项目内部 schema 把 `songs.mid` 和 `albums.mid` 设为主键，以及歌手主页类接口只接受歌手 MID；这属于流程和数据模型设计问题，不应通过大规模反查弥补。
- 建议后续方案是引入“QQ 音乐数字 ID 优先”的采集分支或重构身份键：歌曲和专辑表允许以数字 `id` 作为主键或候选主键，关系表先以 song_id 承载，待响应中出现 MID 时再写入可空 `mid` 和映射表。

### 澄清补 MID 的真实原因
- 用户澄清希望补 MID 的原因是第一步请求结果严重缺少歌手，不是单纯为了任意对象做 `id -> mid` 映射。
- 当前判断：问题根源应从“第一步歌手列表是否能作为歌手全集”改为“第一步歌手列表只能作为种子来源，缺失歌手应由歌曲、专辑和制作人证据流逐步发现并入库”。
- 若缺失歌手来自歌曲列表或歌曲 ID，优先应通过歌曲详情、歌曲批量查询、专辑歌曲列表或制作人/歌词流程自然获得歌手 MID 和署名信息，而不是先对歌手数字 ID 做全量反查。
- 若缺失歌手只存在歌手数字 ID 而没有歌曲、专辑或姓名上下文，则仍缺少可离线计算 MID 的证据；这种场景需要重新确认输入来源、目标范围和是否必须覆盖这些歌手。

### 梳理 qqmusic-api-python 公开接口分类
- 用户要求按功能分类展示当前 API 库提供的所有接口。
- 已在指定 Conda 环境中确认本地安装包为 `qqmusic_api` 0.6.0，入口文件位于环境的 site-packages，公开客户端为 `Client`。
- 已读取 `qqmusic_api.modules` 和 `core.client` 源码，确认接口按 `album`、`comment`、`login`、`lyric`、`mv`、`recommend`、`search`、`singer`、`song`、`songlist`、`top`、`user` 模块暴露，并通过 `client.<module>.<method>()` 调用。
- 本次为只读接口梳理，未修改项目源码、数据库或 raw 缓存；仅追加开发日志。

### 调整 tqdm 进度条显示当前和总数
- 用户纠正所有 tqdm 进度条应显示 `几/几` 进度，而不是只有进度条本体。
- 已修改 `progress.py` 的 tqdm `bar_format` 为 `{bar} {n_fmt}/{total_fmt}`，标题仍由上一行 `== 标题 ==` 单独说明，进度条行只显示进度条和当前/总数。
- 已在 `tests/test_progress.py` 增加回归测试，确认 tqdm 构造参数包含 `{n_fmt}/{total_fmt}`，避免后续改回纯进度条。

## 2026-05-18

### 再次修复开发日志异常空行并固化检查规则
- 用户指出文档异常问题再次出现，要求再次修复，并把异常描述和修复规则写入 `AGENTS.md`，确保后续自动发现、自动保守修复，且不删除 Markdown 必要空行。
- 复核全仓 Markdown 后确认本次异常只出现在 `develop_log.md`：清理前文件大小为 345208 字节，共 17953 行，其中非空行 1973 行；`AGENTS.md` 与 `README.md` 未出现空行膨胀，三者均未发现隐藏控制字符或 U+FFFD 替换字符。
- 本次修复采用 Markdown 感知空行压缩：fenced code block 内部原样保留；fenced code block 外部连续空行最多保留一个；非空行内容不改写。
- 已新增 `scripts/repair_markdown_anomalies.py`，用于扫描或修复 Markdown 异常；扫描项包括 UTF-8 替换字符、非换行隐藏控制字符、fenced code block 外连续空行、文件总行数相对非空行异常膨胀等。
- 已在 `AGENTS.md` 补充“Markdown 文档异常自动修复规则”，要求每次读取 AGENTS、README、develop_log 或修改 Markdown 后自动运行扫描；发现异常时优先用该脚本保守修复，保留必要单个空行和代码块内部空行，并记录开发日志。
- 验证结果：`python -m py_compile scripts/repair_markdown_anomalies.py` 无语法错误；`python scripts/repair_markdown_anomalies.py --fix` 对核心文档扫描通过；`python scripts/repair_markdown_anomalies.py --all` 对全仓 Markdown 扫描通过，所有文件 `max_blank_run=1`、隐藏控制字符为空、U+FFFD 替换字符数量为 0。

### 纠正 Markdown 异常修复规则的空行语义
- 用户指出上一轮修复仍不正确：不应在每一行之间保留一个空行，`###` 开头的日志标题和紧随其后的 `-` 条目之间不应该隔空行，连续 `-` 条目之间也不应该隔空行。
- 已修改 `scripts/repair_markdown_anomalies.py`：新增结构性空行检查，把核心文档中“标题后紧跟列表项却有空行”和“连续列表项之间有空行”识别为异常；修复时删除这些异常空行，同时保留标题之间、代码块内部、段落和代码块等块级结构需要的单个空行。
- 已使用新规则修复 `develop_log.md` 和 `README.md`，非空内容不变；`develop_log.md` 修复后为 2297 行、非空 1993 行，`README.md` 修复后为 144 行、非空 108 行。
- 已收窄结构性空行检查范围：只对 `AGENTS.md`、`README.md`、`develop_log.md` 等核心文档执行结构性空行规则，避免对归档参考文档中的普通 Markdown 段落分隔误报。
- 已同步更新 `AGENTS.md` 的 Markdown 文档异常自动修复规则，明确结构性空行错误定义和保守修复边界。
- 已进一步修正脚本写回方式：不再用文本模式 `newline="\r\n"` 写入已经包含换行的内容，改为字节级写出 CRLF，避免 Windows 换行转换生成 `CRCRLF` 并再次表现为每行之间多空行。

### 探测歌手相似歌手接口返回数量
- 用户要求用周杰伦 MID 调用 `singer.get_similar`，并把 `number` 设置为 100 查看返回结果。
- 已从本地 raw 确认周杰伦 MID 为 `0025NhlN2yWrP4`，随后联网调用 `client.singer.get_similar('0025NhlN2yWrP4', number=100)`。
- 接口成功返回 `code=0`，但 `singerlist` 只有 5 个相似歌手：F.I.R.飞儿乐团、王力宏、范玮琪、蔡依林、李荣浩。
- 已核对本地 `qqmusic_api.modules.singer` 源码，封装会把 `number` 原样作为请求参数传给 `music.SimilarSingerSvr.GetSimilarSingerList`，因此本次 5 个结果不是客户端侧截断。
- 本次为只读接口探测，未写入 raw 缓存、数据库或正式流程代码。

### 合包探测第二层相似歌手接口
- 用户要求继续使用周杰伦相似歌手返回的 5 个 MID，各请求 `number=100` 的相似歌手，并用 5 个请求合包成一次请求。
- 已构造 F.I.R.飞儿乐团、王力宏、范玮琪、蔡依林、李荣浩 5 个 `client.singer.get_similar(mid, number=100)` 请求，并通过 `Client.gather(requests, batch_size=5)` 执行。
- 接口成功返回 5 个响应，F.I.R.飞儿乐团、王力宏、范玮琪、蔡依林各返回 5 个相似歌手，李荣浩返回 4 个相似歌手；所有响应 `code=0` 且 `err_msg` 为空。
- 当前观察：即使 `number=100`，该接口对这些样本仍只返回 4 到 5 个相似歌手，不能作为一次请求扩展到 100 个候选歌手的来源。
- 本次为只读接口探测，未写入 raw 缓存、数据库或正式流程代码。

### 递归探测周杰伦相似歌手 10 层
- 用户要求从第二层 14 个新歌手开始继续递归请求相似歌手，共得到 10 层，并且合包请求上限为 20 个。
- 已用 BFS 方式执行：每层只请求上一层新增歌手，每个请求调用 `client.singer.get_similar(mid, number=100)`，通过 `Client.gather()` 分批合包，单批最多 20 个请求。
- 本次完成到第 10 层，接口请求错误数为 0；各层新增歌手数依次为：第 1 层 5、第 2 层 14、第 3 层 27、第 4 层 52、第 5 层 74、第 6 层 87、第 7 层 86、第 8 层 94、第 9 层 131、第 10 层 151。
- 去重后累计发现 722 个唯一歌手，包括周杰伦起点；累计记录相似歌手边 2420 条。
- 已将层级结果写入 `data/processed/validation/manual_checks/similar_singers_jay_chou_10_layers/similar_singers_layers.json` 和同目录 CSV，将边关系写入 `similar_singers_edges.csv`，并写入 `similar_singers_summary.json`。
- 已复核输出文件存在且非空，层级 CSV 为 722 行，边 CSV 为 2420 行；本次未写入 raw 缓存、数据库或正式流程代码。

### 实现周杰伦相似歌手递归采集工具脚本
- 用户确认将相似歌手递归请求实现为正式独立工具脚本，但不并入完整流程编排。
- 已新增 `music_metadata_graph/tools/collect_jay_chou_similar_singers.py`，固定根节点为周杰伦 `0025NhlN2yWrP4`，递归调用 `qqmusic.singer.get_similar(mid, number=100)`。
- 工具默认不限制层数、歌手总数或运行时间；新增命令行参数 `--max-depth`、`--max-singers`、`--max-seconds`、`--number`、`--batch-size`、`--force`，其中合包批大小限制为 1 到 20。
- 已实现每个被请求歌手一个 raw JSON，默认写入 `data/raw/qqmusic/singer_similar/jay_chou_root/requests/<source_mid>.json`；raw 包含 `source` 元信息和 `response` 原始响应，元信息记录根节点、源歌手、层数、number 和抓取时间。
- 已实现 `manifest.json` 和 `frontier.json` 作为断点续跑状态，记录已请求 MID、已发现歌手、失败项和待请求队列；运行时会复用已存在 raw JSON 作为缓存，除非显式 `--force`。
- 已实现派生查看产物，默认写入 `data/processed/validation/singer_similar_jay_chou/`，包含摘要 JSON、歌手 CSV、边关系 CSV 和失败 CSV；这些产物只作为人工查看结果，不写入 SQLite 或主流程输入。
- 已复用 `run_with_log()`，运行日志默认写入 `logs/singer_similar_jay_chou/`，并打印每层、每批、停止原因和统计摘要。
- 已在 `pyproject.toml` 新增命令入口 `mr-collect-jay-similar-singers`；该入口仅指向工具脚本，不加入 `run_full_pipeline`。
- 已新增 `tests/test_collect_jay_chou_similar_singers.py`，覆盖初始断点状态、raw 包装层数信息、边关系重建、validation 输出，以及未缓存请求使用 `Client.gather()` 合包路径。

### 验证周杰伦相似歌手递归采集工具脚本
- 已执行 `python -m py_compile music_metadata_graph/tools/collect_jay_chou_similar_singers.py tests/test_collect_jay_chou_similar_singers.py`，未发现语法错误。
- 已执行 `python -m unittest tests.test_collect_jay_chou_similar_singers`，共 4 个测试通过。
- 已用临时 smoke 目录执行 `python -m music_metadata_graph.tools.collect_jay_chou_similar_singers --max-depth 1 --raw-dir data/raw/qqmusic/singer_similar/jay_chou_root_smoke_gather --validation-dir data/processed/validation/singer_similar_jay_chou_smoke_gather`，联网请求成功完成。
- smoke 运行观察到第 1 层请求 1 个源歌手，返回并新增 5 个相似歌手，保存 1 个 raw 请求文件、5 条边和 5 个待续跑 frontier；运行日志写入 `logs/singer_similar_jay_chou/`。
- 已回读 smoke raw JSON，确认 `source.depth=1`、`source.number=100`，且 `response.singerlist` 为 5 条；已确认 smoke validation CSV 存在。
- 本次未将相似歌手结果写入数据库、正式 pipeline raw 目录之外的既有缓存，未并入完整流程编排。

### 运行周杰伦相似歌手递归工具到 10 层
- 用户要求重新运行新工具脚本到 10 层，并把结果落到正式默认产物目录。
- 已执行 `python -m music_metadata_graph.tools.collect_jay_chou_similar_singers --max-depth 10`，运行日志写入 `logs/singer_similar_jay_chou/collect_jay_chou_similar_singers_20260518_231007.log`。
- 本次从周杰伦 `0025NhlN2yWrP4` 出发，递归完成 10 层；累计请求并保存 571 个源歌手 raw JSON，发现 722 个唯一歌手，记录 2420 条相似歌手边，失败数为 0。
- 默认 raw 产物已写入 `data/raw/qqmusic/singer_similar/jay_chou_root/`，其中 `requests/` 包含 571 个单请求 JSON，`manifest.json` 记录 722 个已发现歌手和 571 个已请求 MID，`frontier.json` 保留第 10 层新增的 151 个待续跑歌手。
- 默认查看产物已写入 `data/processed/validation/singer_similar_jay_chou/`，其中歌手 CSV 为 722 行，边关系 CSV 为 2420 行，失败 CSV 为 0 行，摘要 JSON 与 manifest 统计一致。
- 本次只运行独立工具并落盘 raw、validation 和日志；未写入 SQLite，未并入或触发完整 pipeline。

### 实现周杰伦相似歌手 DAG 静态站点生成工具
- 用户要求参考 force-graph `dag-yarn` 示例模板，生成一个与现有 `site/`、`site_mvp/`、`site_demo/`、`site_large/` 并列的正式站点，不复用现有顶部控制栏，不需要粒子效果，且重力模式固定为 `radialout` 不可切换。
- 已新增 `music_metadata_graph/tools/build_jay_chou_similar_dag_site.py`，默认读取 `data/processed/validation/singer_similar_jay_chou/csv_views/similar_singers_artists.csv` 和 `similar_singers_edges.csv`，输出到 `site_similar_singers/`。
- 已新增命令入口 `mr-build-jay-similar-dag-site`，该工具独立于完整 pipeline，不并入 `run_full_pipeline`。
- 生成站点包含 `index.html`、`assets/graph-data.js`、`assets/vendor/force-graph.min.js` 和对应 license；页面保持极简全屏图谱结构，只包含 `#graph` 和底部状态文字。
- 为满足 force-graph DAG radialout 布局约束，页面绘制边使用“首次发现父节点 -> 新歌手”的发现树/DAG，共 722 个节点和 721 条发现边；完整相似歌手原始边 2420 条仍保存在 `graph-data.js` 的 `similarLinks` 中，不在当前页面绘制，避免回边和环破坏 DAG 布局。
- 页面固定调用 `.dagMode("radialout")`，未加入 `dat.gui`、模式切换或 `linkDirectionalParticles` 粒子效果。
- 已新增 `tests/test_build_jay_chou_similar_dag_site.py`，验证图谱数据使用首次发现父节点生成 DAG 边、站点资源能写出、页面固定 radialout 且不包含粒子配置。

### 验证周杰伦相似歌手 DAG 静态站点
- 已执行 `python -m py_compile music_metadata_graph/tools/build_jay_chou_similar_dag_site.py tests/test_build_jay_chou_similar_dag_site.py`，未发现语法错误。
- 已执行 `python -m unittest tests.test_build_jay_chou_similar_dag_site`，共 2 个测试通过。
- 已执行 `python -m music_metadata_graph.tools.build_jay_chou_similar_dag_site`，生成 `site_similar_singers/`，摘要显示 722 个节点、721 条发现 DAG 边、2420 条完整相似边数据、`dagMode=radialout`。
- 已回读 `site_similar_singers/assets/graph-data.js`，确认节点数、DAG 边数和完整相似边数与摘要一致；已检查 `site_similar_singers/index.html` 中存在固定 `dagMode("radialout")`，未发现 `linkDirectionalParticles` 或 `dat.gui`。
- 已通过本地 HTTP 服务器和浏览器打开 `site_similar_singers/index.html`，确认页面标题、状态文字、canvas 生成和图谱可视化渲染；截图观察到全屏 radialout DAG 已显示。
- 验证过程中 Python 内置 `http.server` 在本机沙箱下传输大 JS 文件时出现资源提前断开，改用临时 HTTP/1.0 静态服务器完成浏览器验证；该问题只影响本次验证服务器，不影响静态站点文件本身。

### 纠正相似歌手 DAG 站点输入来源
- 用户指出 CSV 只是人工检查视图，任何时候都不应该依赖 CSV，并要求将该规则记录进 AGENTS。
- 已在 `AGENTS.md` 项目补充规则中新增 CSV 边界：CSV 永远只作为人工检查、验收查看或发布产物，不得作为正式脚本、工具、站点生成、断点续跑、清洗、过滤、入库或图谱构建的输入来源；正式输入必须来自 raw JSON、manifest、SQLite/数据库或明确结构化源文件。
- 已修改 `music_metadata_graph/tools/build_jay_chou_similar_dag_site.py`，移除 `--artists-csv` 和 `--edges-csv` 参数，默认改为读取 `data/raw/qqmusic/singer_similar/jay_chou_root/manifest.json` 和 `requests/*.json`。
- 站点生成逻辑现在从 manifest 的 `seen_artists` 构建节点和首次发现 DAG 边，从每个 raw 请求 JSON 的 `source` 与 `response.singerlist` 重建完整相似边数据，不再读取 validation CSV。
- 已更新 `tests/test_build_jay_chou_similar_dag_site.py`，用 raw manifest 与 raw request fixture 验证站点构建，并新增测试覆盖 raw loader 路径。
- 已重新执行 `python -m music_metadata_graph.tools.build_jay_chou_similar_dag_site`，从 raw/manifest 重新生成 `site_similar_singers/`；回读 `graph-data.js` 确认仍为 722 个节点、721 条 DAG 边、2420 条完整相似边。

### 验证相似歌手 DAG 站点输入来源纠正
- 已执行 `python -m py_compile music_metadata_graph/tools/build_jay_chou_similar_dag_site.py tests/test_build_jay_chou_similar_dag_site.py`，未发现语法错误。
- 已执行 `python -m unittest tests.test_build_jay_chou_similar_dag_site`，共 3 个测试通过。
- 已用 `rg` 检查站点生成脚本和测试，确认正式脚本中不再包含 CSV 输入路径或读取逻辑；测试中的 CSV 字样仅出现在防回归测试名称中。
- 已机械统一 `AGENTS.md`、站点生成脚本和对应测试文件为 CRLF 行尾。

### 纠正相似歌手 DAG 站点连线样式
- 用户指出页面连线不应是曲线，除用户明确要求的差异外，站点应尽量与 force-graph `dag-yarn` 示例模板保持一致。
- 已确认前一版页面因为手动设置 `.linkCurvature(0.24)` 导致连线变成曲线，该设置偏离模板。
- 已修改 `music_metadata_graph/tools/build_jay_chou_similar_dag_site.py` 的页面模板：恢复示例的文字节点背景、浅蓝文字、`dagLevelDistance(300)`、`d3AlphaDecay(0.02)`、`d3VelocityDecay(0.3)` 和基于 dagMode 的 `linkCurvature` 逻辑；由于页面固定 `radialout`，该逻辑在当前模式下返回 0，连线为直线。
- 保留用户明确要求的差异：不加入 GUI 模式切换，不加入粒子效果，DAG 模式固定为 `radialout`。
- 已重新生成 `site_similar_singers/`，并确认 `site_similar_singers/index.html` 中 `radialout/radialin` 分支的曲率为 0，未包含 `linkDirectionalParticles` 或 `dat.gui`。

### 验证相似歌手 DAG 站点直线连线
- 已执行 `python -m py_compile music_metadata_graph/tools/build_jay_chou_similar_dag_site.py tests/test_build_jay_chou_similar_dag_site.py`，未发现语法错误。
- 已执行 `python -m unittest tests.test_build_jay_chou_similar_dag_site`，共 3 个测试通过。
- 已通过本地 HTTP 服务器和浏览器重新打开 `site_similar_singers/index.html`，页面生成 1 个 canvas，状态文字显示 722 个节点和 721 条 discovery links；浏览器截图确认连线为直线。
- 浏览器日志中仍显示一次旧端口 8765 的历史脚本错误，但当前复核页面为 8766，当前页面已正常渲染。

### 设置相似歌手 DAG 力稳定时间为 10 秒
- 用户希望先把相似歌手 DAG 图结构的力稳定时间设置为 10 秒观察效果。
- 已修改 `music_metadata_graph/tools/build_jay_chou_similar_dag_site.py` 的页面模板，在 force-graph 初始化链中显式设置 `.cooldownTime(10000)`。
- 已移除原先 600ms 后执行的 `setTimeout(() => Graph.zoomToFit(...))`，改为 `.onEngineStop(() => Graph.zoomToFit(800, 60))`，使视图在 10 秒布局结束后再自适应。
- 已更新 `tests/test_build_jay_chou_similar_dag_site.py`，断言生成页面包含 10 秒冷却时间、引擎停止后缩放，并不再包含早期 `setTimeout` 缩放逻辑。
- 已重新执行 `python -m music_metadata_graph.tools.build_jay_chou_similar_dag_site`，生成 `site_similar_singers/`，统计仍为 722 个节点、721 条 DAG 边、2420 条完整相似边数据。
- 已执行 `python -m py_compile music_metadata_graph/tools/build_jay_chou_similar_dag_site.py tests/test_build_jay_chou_similar_dag_site.py`，未发现语法错误。
- 已执行 `python -m unittest tests.test_build_jay_chou_similar_dag_site`，共 3 个测试通过。

### 调整相似歌手 DAG 节点斥力
- 用户判断问题可能不在力稳定时间，要求删除刚刚设置的 10 秒稳定时间，并改为加大节点间斥力。
- 已从 `music_metadata_graph/tools/build_jay_chou_similar_dag_site.py` 页面模板中移除 `.cooldownTime(10000)` 和 `.onEngineStop(...)`，恢复 600ms 后执行 `zoomToFit`。
- 已在 force-graph 初始化后设置 `Graph.d3Force("charge").strength(-240)`，用于增强节点间斥力。
- 已更新 `tests/test_build_jay_chou_similar_dag_site.py`，断言生成页面包含新的 charge 设置、恢复早期 `zoomToFit`，且不再包含 10 秒冷却和引擎停止缩放逻辑。
- 已重新执行 `python -m music_metadata_graph.tools.build_jay_chou_similar_dag_site`，生成 `site_similar_singers/`，统计仍为 722 个节点、721 条 DAG 边、2420 条完整相似边数据。
- 已执行 `python -m py_compile music_metadata_graph/tools/build_jay_chou_similar_dag_site.py tests/test_build_jay_chou_similar_dag_site.py`，未发现语法错误。
- 已执行 `python -m unittest tests.test_build_jay_chou_similar_dag_site`，共 3 个测试通过。
- 已用简单文本搜索确认 `site_similar_singers/index.html` 和生成脚本包含 `Graph.d3Force("charge").strength(-240)`，生成页面和生成脚本不再包含 `cooldownTime`、`onEngineStop` 或 `linkDirectionalParticles`。

### 试调相似歌手 DAG 斥力为 -1000
- 用户要求把相似歌手 DAG 页面的节点斥力设置为 `-1000` 观察效果。
- 已将 `music_metadata_graph/tools/build_jay_chou_similar_dag_site.py` 中的 `Graph.d3Force("charge").strength(-240)` 调整为 `Graph.d3Force("charge").strength(-1000)`。
- 已同步更新 `tests/test_build_jay_chou_similar_dag_site.py` 中的生成页面断言。
- 已重新执行 `python -m music_metadata_graph.tools.build_jay_chou_similar_dag_site`，生成 `site_similar_singers/`，统计仍为 722 个节点、721 条 DAG 边、2420 条完整相似边数据。
- 已执行 `python -m py_compile music_metadata_graph/tools/build_jay_chou_similar_dag_site.py tests/test_build_jay_chou_similar_dag_site.py`，未发现语法错误。
- 已执行 `python -m unittest tests.test_build_jay_chou_similar_dag_site`，共 3 个测试通过。
- 已用简单文本搜索确认生成页面、生成脚本和测试断言包含 `Graph.d3Force("charge").strength(-1000)`，未再命中旧的 `-240` 设置。

### 改用固定径向树布局解决枝桠重叠
- 用户根据截图指出问题不是稳定时间或斥力，而是树枝在 radial DAG force 布局中互相穿插；按发现树结构，每个节点只有一个父节点，子树应清晰分区。
- 已判断 `force-graph` 的 `dagMode("radialout")` 只约束层级半径，不会为每棵子树分配互不重叠的角度扇区，因此同层和跨层枝桠仍会由力模拟自由旋转并出现穿插。
- 已新增 `apply_fixed_radial_tree_layout()`：从首次发现父子边构建树，按每棵子树叶子数量分配连续角度区间，使用层数乘 `300` 作为半径，为每个节点写入 `x/y/fx/fy/layoutAngle/layoutRadius`。
- 已调整相似歌手 DAG 页面模板：移除 `.dagMode("radialout")`、`.dagLevelDistance(300)` 和 `Graph.d3Force("charge").strength(-1000)`，保留直线 `.linkCurvature(0)`，并显式移除 `charge/link/center` force，让页面按预计算固定坐标绘制。
- 已更新 `tests/test_build_jay_chou_similar_dag_site.py`，覆盖 `meta.layout=fixedRadialTree`、节点固定坐标、根节点在中心、页面不再包含 radial DAG force 或强斥力。
- 开发中曾两次把 `layout_meta` 插入到错误位置，导致 `NameError`；已修正为只在 `build_graph_data()` 返回前计算，并重新跑验证。
- 已重新执行 `python -m music_metadata_graph.tools.build_jay_chou_similar_dag_site`，生成 `site_similar_singers/`，统计为 722 个节点、721 条 DAG 边、2420 条完整相似边数据、353 个叶子节点、固定径向树布局。
- 已执行 `python -m py_compile music_metadata_graph/tools/build_jay_chou_similar_dag_site.py tests/test_build_jay_chou_similar_dag_site.py`，未发现语法错误。
- 已执行 `python -m unittest tests.test_build_jay_chou_similar_dag_site`，共 3 个测试通过。
- 已做生成数据几何检查：`site_similar_singers/assets/graph-data.js` 中 722 个节点全部包含 `fx/fy`，根节点坐标为 `(0, 0)`，最大半径为 `3000`；页面脚本不再包含 `.dagMode("radialout")`、`.dagLevelDistance(300)` 或 `strength(-1000)`。
- 尝试用 Codex Browser 打开本地站点做截图验证时，`file://` 和本地 HTTP 导航被 Browser URL 策略拦截或连接失败；未继续绕过策略，改用静态文件和生成数据检查作为替代验证。

### 修复 Markdown 与 Python 文本换行异常并升级自动检查规则
- 用户指出异常再次出现，且不仅限于 Markdown，Python 文件也出现异常；要求修复并在 `AGENTS.md` 中给出更详细具体的预防和检查规则。
- 全仓扫描确认本次异常包括：`AGENTS.md` 出现 `CRCRLF` 和核心 Markdown 结构性空行错误；`develop_log.md` 出现大规模空行膨胀；`music_metadata_graph/tools/build_jay_chou_similar_dag_site.py` 行数异常膨胀；`music_metadata_graph/tools/collect_jay_chou_similar_singers.py` 与 `tests/test_collect_jay_chou_similar_singers.py` 出现 `CRCRLF`；多份 Python 文件存在连续空行超过 2 个的格式异常。
- 已新增 `scripts/repair_text_anomalies.py` 作为通用文本异常扫描与修复入口，覆盖 `.md` 和 `.py`；保留 `scripts/repair_markdown_anomalies.py` 作为兼容入口。
- 修复策略为：Markdown 保留 fenced code block 内部空行，核心 Markdown 删除标题到列表、列表到列表之间的异常空行；Python 删除连续 import、装饰器与定义、冒号后的首个代码行、括号/字典/列表/函数调用内部元素之间的结构性异常空行，并把其他连续 3 个及以上空行压缩为最多 2 个空行；写回前后用 AST 解析确认语法可解析；所有写回均使用字节级 CRLF，避免 Windows 文本模式产生 `CRCRLF`。
- 已运行 `python scripts/repair_text_anomalies.py --fix --all` 修复全仓支持文本，并再次运行 `python scripts/repair_text_anomalies.py --all` 验证通过；所有扫描文件均无 `CRCRLF`、无隐藏控制字符、无 U+FFFD 替换字符、无异常空行膨胀，Python 文件 AST 解析通过。
- 已更新 `AGENTS.md` 的文本异常自动扫描与修复规则，要求开始任务读取核心文档或修改任意 `.md`、`.py` 后运行扫描，涉及多文件或怀疑全仓异常时运行全仓扫描；发现异常后先用脚本保守修复，再全仓验证并记录日志。规则同时明确禁止把已含 `\n` 的字符串再用 `newline="\r\n"` 写入，避免再次产生 `CRCRLF`。

## 2026-05-19

### 安装 black 作为 Python 格式化工具
- 用户要求直接安装 `black` 之类的工具用于 Python 文件格式修复。
- 已在项目指定 Conda 环境中执行 `python -m pip install black`，安装结果为 `black 26.5.1`，同时安装其依赖 `click`、`mypy-extensions`、`pathspec`、`platformdirs` 和 `pytokens`。
- 已使用项目指定 Conda Python 执行 `python -m black --version`，确认 `black 26.5.1` 可用；`pip show black` 曾因 Windows 控制台 GBK 无法输出作者姓名中的非 ASCII 字符触发日志编码错误，因此改用 `importlib.metadata` 读取版本和包名进行验证。
- 已在 `pyproject.toml` 增加 `[project.optional-dependencies] dev = ["black>=26.5.1"]`，并增加 `[tool.black]` 配置：`line-length = 100`、`target-version = ["py312"]`。
- 本次只用 black 格式化并验证 `scripts/repair_text_anomalies.py` 和 `scripts/repair_markdown_anomalies.py`，未对全仓业务源码执行 black，避免把大量既有业务改动混入本次工具安装。
- 验证结果：`python -m black --check scripts/repair_text_anomalies.py scripts/repair_markdown_anomalies.py` 通过；`python -m py_compile scripts/repair_text_anomalies.py scripts/repair_markdown_anomalies.py` 通过；文本异常扫描确认核心文档和修复脚本无 `CRCRLF`、无隐藏控制字符、无 U+FFFD 替换字符。

### 用新相似歌手 raw 数据更新站点
- 用户说明已请求新数据，要求更新相似歌手网页。
- 已执行 `python -m music_metadata_graph.tools.build_jay_chou_similar_dag_site`，继续只读取 `data/raw/qqmusic/singer_similar/jay_chou_root/manifest.json` 和 `requests/*.json`，不读取 CSV。
- 已重新生成 `site_similar_singers/`，新站点统计为 7113 个节点、7112 条发现树边、32620 条完整相似歌手边、3204 个叶子节点，布局仍为 `fixedRadialTree`。
- 已执行 `python -m py_compile music_metadata_graph/tools/build_jay_chou_similar_dag_site.py tests/test_build_jay_chou_similar_dag_site.py`，未发现语法错误。
- 已执行 `python -m unittest tests.test_build_jay_chou_similar_dag_site`，共 3 个测试通过。
- 已检查 `site_similar_singers/assets/graph-data.js`：7113 个节点全部包含 `fx/fy` 固定坐标，根节点周杰伦坐标为 `(0, 0)`，最大半径为 `16200`。
- 已检查 `site_similar_singers/index.html`：页面保留 `linkCurvature(0)`，显式移除 `charge/link/center` force，未命中 `.dagMode("radialout")`、`.dagLevelDistance(300)` 或旧的 `strength(-1000)`。

### 统计相似歌手名称文字类型分布
- 用户要求检查所有相似歌手数据，统计名字纯中文、包含中文、纯英文和其他的分布。
- 已直接读取 `data/raw/qqmusic/singer_similar/jay_chou_root/manifest.json` 和 `requests/*.json` 统计，不读取 CSV。
- 已定义分类口径：纯中文为去掉空白后每个字符都是 CJK 汉字；包含中文为含至少一个 CJK 汉字但不是纯中文；纯英文为不含中文且只含 ASCII 字母、数字、空格和常见英文艺名符号；其他覆盖韩文、日文假名、西里尔字母、重音拉丁字母和符号型名称等。
- 唯一歌手 7113 个：纯中文 1479 个，占 20.79%；包含中文但不纯中文 341 个，占 4.79%；纯英文/ASCII 艺名 4837 个，占 68.00%；其他 456 个，占 6.41%。
- 原始返回行按边计数 32620 行：纯中文 6342 行，占 19.44%；包含中文但不纯中文 1445 行，占 4.43%；纯英文/ASCII 艺名 22759 行，占 69.77%；其他 2074 行，占 6.36%。
- 已将完整统计和示例写入 `data/processed/validation/singer_similar_jay_chou/name_script_distribution.json`。

### 检查 40 位指定艺人是否进入相似歌手递归结果
- 用户提供截图中的 40 位艺人名单，询问递归算法是否找到这些人。
- 已直接读取 `data/raw/qqmusic/singer_similar/jay_chou_root/manifest.json` 和 `requests/*.json` 检查，不读取 CSV。
- 初次尝试包含匹配时发现会产生误判，例如 `Selina` 命中 `Lina`、`4 in Love` 命中 `V`，因此最终只采用名称/标题精确匹配和大小写、全半角、常见连字符规范化后的严格等值匹配。
- 严格匹配结果：40 个查询名中只找到 1 个唯一艺人 `江语晨`，MID 为 `003UoVkR2GDjGX`，首次发现层数为 4，首次来源为 `BY2`。
- 其余 39 个查询名在 manifest 和 raw response singerlist 中均未严格命中。

### 使用 black 格式化当前 Python 文件
- 用户要求检查所有 Python 文件，对有必要的文件使用 black 修复格式。
- 先运行 `python scripts/repair_text_anomalies.py --all`，确认文本层面无 `CRCRLF`、隐藏控制字符、U+FFFD 替换字符或异常空行膨胀。
- 使用项目指定 Conda 环境执行 `python -m black --check music_metadata_graph scripts tests`，确认当前源码、脚本和测试目录中 46 个 Python 文件需要 black 格式化，归档目录未纳入本轮主动格式化范围。
- 已执行 `python -m black music_metadata_graph scripts tests`，格式化当前有效源码、脚本和测试文件；未对 `archive/` 历史参考目录执行 black，以避免改动归档材料。
- black 格式化后，自定义文本扫描器一度误报三引号 SQL 字符串内部空行，已调整 `scripts/repair_text_anomalies.py` 识别多行字符串范围，不再把字符串内容中的空行当作 Python 结构异常。
- 验证结果：`python scripts/repair_text_anomalies.py --all` 通过；`python -m black --check music_metadata_graph scripts tests` 通过；`python -m compileall -q music_metadata_graph scripts tests` 通过。
- 初次执行 `python -m unittest discover tests` 时误用了系统默认 Inkscape Python，因缺少 `qqmusic_api` 和 `pypinyin` 依赖失败；随后按项目规则使用指定 Conda Python 重跑 `python -m unittest discover tests`，共 61 个测试通过。

### 明确 Python 格式交给 black
- 用户确认 Python 正常格式应交给 black，不应继续由自定义文本规则判断 import、装饰器、函数体或括号内部空行。
- 已更新 `AGENTS.md`：自定义文本异常修复只负责编码、换行损坏、异常空行膨胀和 Markdown 结构性空行；Python 正常格式统一由 `black` 负责。
- 已调整 `scripts/repair_text_anomalies.py`：移除 Python 结构性空行判断，不再检查或修复 import/import、装饰器/定义、冒号后代码块首行、括号内部元素之间的空行；Python 扫描只保留 UTF-8、隐藏控制字符、`CRCRLF`、异常膨胀和 AST 可解析检查。
- 已明确 Python 修复顺序：先运行文本异常修复处理损坏，再运行 `black`，最后再运行文本异常扫描确认没有 `CRCRLF` 等损坏。
- 验证结果：`python -m black scripts/repair_text_anomalies.py` 通过；`python -m py_compile scripts/repair_text_anomalies.py` 通过；`python scripts/repair_text_anomalies.py AGENTS.md develop_log.md README.md scripts/repair_text_anomalies.py` 通过。

### 实现歌词补充有限证据缓存
- 用户要求开始实现第十二步歌词补充缓存改造，并在开始前重新读取 `AGENTS.md` 和 `develop_log.md`；本次已按要求重新读取两份文件，并在修改前运行核心文档文本异常扫描。
- 已修改 `music_metadata_graph/pipelines/collect_song_lyric_credit_raw.py`：新增 `qqmusic_lyric_credit_evidence` 有限证据缓存格式，请求返回的完整歌词只在内存中解密一次，落盘 JSON 不再保存完整 `lyric`、`trans`、`roma` 或 `qrc` 字段。
- 新的歌词证据 JSON 继续写入 `data/raw/qqmusic/song_lyric_credit/{song_mid}.json`，包含 `cache_kind`、`schema_version`、歌曲标识、来源接口、结构化制作人缺失角色、原接口 `crypt` 状态、歌词空状态、解密后原始前 10 行、有效前 5 行、解析出的词曲行、解析状态和歌词非空行数。
- 已实现旧完整歌词 raw 的读时迁移：第十二步读到旧 `lyric.get_lyric` 完整响应时会在内存中解密、构造有限证据，并用临时文件原子替换原路径；坏 JSON 或迁移失败不会覆盖旧文件，采集摘要中统计 `failed_migrations`。
- 已调整第十二步摘要计数，区分 `fetched`、`evidence_cache_hits`、`migrated_legacy_raw`、`failed_migrations`，并保留兼容字段 `cache_hits` 指向新证据缓存命中数。
- 已修复第十二步 SQLite 连接未显式关闭的问题；临时 smoke 验证确认旧完整缓存迁移后不再锁住临时数据库文件。

### 接入歌词证据缓存到补 MID 和作词作曲导入
- 已修改 `fill_song_credit_missing_mids.py`：扫描第十二步歌词缓存时改用统一加载/迁移函数，读到旧完整 raw 会先转换为有限证据，再从 `parsed_credit_rows` 生成 `step12_song_lyric_credit` 来源姓名。
- 已修改 `import_song_credits_to_db.py`：第十四步导入作词作曲关系时同样通过统一加载/迁移函数读取歌词证据，只有结构化制作人缺失的角色才使用歌词解析结果补充关系。
- 第十三步补 MID CSV 仍只作为人工检查视图；第十四步仍不读取该 CSV，而是从 `artists` 表按唯一姓名映射解析歌词姓名到 MID。
- 已同步 `AGENTS.md` 和 `README.md`：说明第十二步长期缓存为歌词头部有限证据，不保存完整歌词，旧完整歌词 raw 读到时应迁移覆盖为新格式。

### 验证歌词证据缓存改造
- 已新增和更新 `tests/test_collect_song_lyric_credit_raw.py`，覆盖新证据格式不包含完整歌词字段、新格式解析、旧完整 raw 读时迁移、请求成功后直接写有限证据。
- 已更新 `tests/test_fill_song_credit_missing_mids.py`，覆盖第十三步可从新证据格式中读取歌词来源姓名。
- 定向验证执行 `python -m unittest tests.test_collect_song_lyric_credit_raw tests.test_fill_song_credit_missing_mids tests.test_run_full_pipeline`，共 14 个测试通过。
- 临时 smoke 验证构造旧完整歌词缓存和最小 SQLite 数据库，执行第十二步采集入口后观察到 `migrated_legacy_raw=1`，缓存文件 `cache_kind=qqmusic_lyric_credit_evidence`，不再包含 `lyric` 字段，CSV 包含解析出的作词作曲姓名。
- 全量验证执行 `python -m unittest discover tests`，共 66 个测试通过。
- 格式和文本验证：已对本次触达 Python 文件运行 `black`，`black --check` 通过；`python scripts/repair_text_anomalies.py --all` 通过；`git diff --check` 对本次触达文件通过。

### 修改相似歌手递归脚本首轮种子
- 用户要求把相似歌手递归脚本首轮从周杰伦单点改为第一步完整歌手列表 raw 中 `area_id in (0, 1)` 的两千多个 MID，并把这些 MID 先设为已发现。
- 已修改 `music_metadata_graph/tools/collect_jay_chou_similar_singers.py`：新增 `DEFAULT_SEED_SINGER_LIST_DIR` 指向 `data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all/`，新增 `load_area_seed_artists()` 读取所有 `page_*.json` 的 `singerlist[]`，按 `area_id in (0, 1)`、MID 非空和 MID 去重构造第 0 层种子。
- 默认 raw 输出目录从 `data/raw/qqmusic/singer_similar/jay_chou_root/` 改为 `data/raw/qqmusic/singer_similar/area_0_1_singer_list_seed/`，默认 validation 目录改为 `data/processed/validation/singer_similar_area_0_1_seed/`，默认日志目录改为 `logs/singer_similar_area_0_1_seed/`，避免继续复用旧周杰伦根目录断点。
- 新 manifest 记录 `seed_source`，`seen_artists` 初始即为全部 area 0/1 种子，frontier 初始也为这些种子，深度均为 0；后续请求仍按原有 BFS、缓存优先、每个 MID 一个 raw JSON 和合包上限 20 执行。
- 已新增 `--seed-singer-list-dir` 参数，用于覆盖首轮种子来源目录；显式指定旧 `--raw-dir` 时，脚本仍按该目录已有 manifest/frontier 断点续跑，不自动迁移旧数据。
- 已更新 `tests/test_collect_jay_chou_similar_singers.py`，新增 area 0/1 种子过滤和去重测试，并把初始状态测试从周杰伦单点改为多种子 frontier。
- 已用真实第一步 raw 只读调用 `load_area_seed_artists()` 验证当前本地种子数为 2119，前 5 个为周杰伦、林俊杰、陈奕迅、薛之谦、王力宏。
- 验证结果：`python -m py_compile music_metadata_graph/tools/collect_jay_chou_similar_singers.py tests/test_collect_jay_chou_similar_singers.py` 通过；`python -m unittest tests.test_collect_jay_chou_similar_singers` 共 5 个测试通过；`python scripts/repair_text_anomalies.py music_metadata_graph/tools/collect_jay_chou_similar_singers.py tests/test_collect_jay_chou_similar_singers.py` 通过。
- 曾尝试使用 `--max-depth 0` 做只初始化 smoke，但该参数按现有规则表示“不限制”，因此实际进入第 1 层并因沙箱网络权限失败；临时 smoke 目录已清理，未保留半成品。

### 迁移相似歌手 raw 为全局请求缓存
- 用户要求把之前请求的相似歌手结果迁移到合适目录，并保证未来无论从哪个节点开始递归，都能自动复用已请求数据且不重复保存。
- 已确定新目录边界：`data/raw/qqmusic/singer_similar/request_cache/number_<number>/<source_mid>.json` 保存全局唯一的 `qqmusic.singer.get_similar(source_mid, number)` 原始响应；`data/raw/qqmusic/singer_similar/runs/<run_id>/manifest.json` 和 `frontier.json` 保存具体递归任务的根节点、种子、层数、首次来源、frontier 和 requested MID。
- 已修改 `music_metadata_graph/tools/collect_jay_chou_similar_singers.py`：新增 `request_cache_dir`，默认 raw 状态目录改为 `data/raw/qqmusic/singer_similar/runs/area_0_1_singer_list_seed`，默认请求缓存目录为 `data/raw/qqmusic/singer_similar/request_cache/number_100`；缓存命中、写 raw 和重建边均改为从全局请求缓存读取。
- 已修改 raw wrapper：全局请求缓存不再写入根节点和层数信息，层数和首次来源只保存在 run manifest/frontier 中。
- 已修改 `music_metadata_graph/tools/build_jay_chou_similar_dag_site.py`：默认读取 `runs/jay_chou_root` 的 manifest，并从 `request_cache/number_100` 读取完整相似歌手响应；页面生成仍不读取 CSV。
- 已新增 `music_metadata_graph/tools/migrate_singer_similar_raw_cache.py`，用于把旧根目录中的 `requests/*.json` 合并到全局请求缓存，并把旧 `manifest.json`、`frontier.json` 复制到 `runs/<旧目录名>/`；同一 `source_mid + number` 响应相同则复用，响应不同则报告冲突并停止。
- 已执行迁移脚本：从旧 `jay_chou_root`、`jay_chou_root_smoke`、`jay_chou_root_smoke_gather` 迁移/复用请求，结果为迁移 7113 个请求、复用 2 个请求、冲突 0 个；旧目录保留为兼容备份，未删除。
- 迁移后复核：`request_cache/number_100` 中有 7113 个 JSON；`runs/jay_chou_root` 保留周杰伦根节点状态，seen 7113、requested 7113、frontier 0；`runs/area_0_1_singer_list_seed` 初始化为 area 0/1 种子状态，seen 2119、requested 0、frontier 2119。
- 已用新目录重新执行 `python -m music_metadata_graph.tools.build_jay_chou_similar_dag_site --raw-dir data/raw/qqmusic/singer_similar/runs/jay_chou_root --request-cache-dir data/raw/qqmusic/singer_similar/request_cache/number_100`，站点统计仍为 7113 个节点、7112 条发现树边、32620 条完整相似边。
- 已执行 `python -m py_compile music_metadata_graph/tools/collect_jay_chou_similar_singers.py music_metadata_graph/tools/build_jay_chou_similar_dag_site.py music_metadata_graph/tools/migrate_singer_similar_raw_cache.py tests/test_collect_jay_chou_similar_singers.py tests/test_build_jay_chou_similar_dag_site.py`，未发现语法错误。
- 已执行 `python -m unittest tests.test_collect_jay_chou_similar_singers tests.test_build_jay_chou_similar_dag_site`，共 8 个测试通过。
- 已执行文本异常扫描，相关源码和测试均无 `CRCRLF`、隐藏控制字符、U+FFFD 替换字符或异常空行膨胀。
- 曾额外尝试 `python -m music_metadata_graph.tools.collect_jay_chou_similar_singers --max-seconds 1` 做默认采集 smoke，但沙箱网络权限导致连接 QQ 音乐失败；该失败不影响迁移和本地缓存复用验证。
- 已在 `AGENTS.md` 新增相似歌手递归缓存规则，明确后续不得按根节点重复保存相同 `source_mid + number` raw。

### 扁平化相似歌手请求缓存并删除旧目录
- 用户指出相似歌手请求缓存不应包含 `number_100` 父目录；无论以多少 number 参数请求，后续都应按源歌手 MID 直接复用同一个 raw 缓存文件。
- 已修改 `music_metadata_graph/tools/collect_jay_chou_similar_singers.py` 和 `music_metadata_graph/tools/build_jay_chou_similar_dag_site.py`，默认请求缓存目录从 `data/raw/qqmusic/singer_similar/request_cache/number_100/` 改为 `data/raw/qqmusic/singer_similar/request_cache/`。
- 已修改 `music_metadata_graph/tools/migrate_singer_similar_raw_cache.py`，迁移目标改为 `request_cache/<source_mid>.json`，并兼容把既有 `request_cache/number_*/*.json` 搬平到同一层缓存；冲突判断改为同一 source MID 响应不同即停止报告。
- 已更新 `AGENTS.md` 的相似歌手递归缓存规则：`number` 只允许作为 raw JSON 内部请求元信息，不得成为缓存父目录或缓存键。
- 已执行迁移脚本，`request_cache/number_100` 中 7113 个 JSON 已搬平为 `request_cache/*.json`，旧根目录请求复用 7115 次，冲突 0 个。
- 已在确认目标路径位于当前工作区和 `data/raw/qqmusic/singer_similar/` 下后，删除旧目录 `jay_chou_root/`、`jay_chou_root_smoke/`、`jay_chou_root_smoke_gather/` 和 `request_cache/number_100/`。
- 删除后复核 `data/raw/qqmusic/singer_similar/` 只保留 `request_cache/` 与 `runs/` 两个子目录，`request_cache/` 下无子目录且保留 7113 个 JSON；`runs/jay_chou_root/manifest.json` 仍保留 seen 7113、requested 7113。
- 已用扁平缓存重新生成 `site_similar_singers/`，统计为 7113 个节点、7112 条发现树边、32620 条完整相似边、3204 个叶子节点。
- 已新增 `tests/test_migrate_singer_similar_raw_cache.py` 覆盖旧 `number_*` 缓存搬平和旧根目录 run 迁移；已更新采集和站点测试中的请求缓存路径夹具。
- 验证结果：`python -m py_compile` 覆盖 3 个工具脚本和 3 个测试文件通过；`python -m unittest tests.test_collect_jay_chou_similar_singers tests.test_build_jay_chou_similar_dag_site tests.test_migrate_singer_similar_raw_cache` 共 9 个测试通过；文本异常扫描确认本次触达 Markdown 与 Python 文件无 `CRCRLF`、隐藏控制字符、U+FFFD 替换字符或异常空行膨胀。

### 删除相似歌手递归可视化站点和生成脚本
- 用户要求删除之前写的递归可视化站点和生成脚本，并明确不要误删其他内容。
- 已先搜索 `build_jay_chou_similar_dag_site`、`site_similar_singers`、`SimilarDagSite` 和命令入口引用，确认删除范围只包含递归可视化站点生成脚本、对应测试、命令入口和生成站点目录。
- 已删除 `music_metadata_graph/tools/build_jay_chou_similar_dag_site.py` 和 `tests/test_build_jay_chou_similar_dag_site.py`，并从 `pyproject.toml` 移除 `mr-build-jay-similar-dag-site` 命令入口。
- 已递归删除 `site_similar_singers/` 下的生成文件，包括 `index.html`、`assets/graph-data.js` 和 vendor 资源；Windows 当前仍报告空目录本身被其他进程占用，因此目录空壳暂时未能移除。
- 明确未删除 `music_metadata_graph/tools/collect_jay_chou_similar_singers.py`、`music_metadata_graph/tools/migrate_singer_similar_raw_cache.py`、`data/raw/qqmusic/singer_similar/request_cache/` 或 `data/raw/qqmusic/singer_similar/runs/`。
- 验证结果：`rg` 确认当前源码、测试、README、AGENTS 和 pyproject 中不再存在递归可视化生成脚本、命令入口或 `site_similar_singers` 引用；`python -m py_compile` 覆盖保留的相似歌手采集/迁移脚本和测试通过；`python -m unittest tests.test_collect_jay_chou_similar_singers tests.test_migrate_singer_similar_raw_cache` 共 6 个测试通过。

### 统计运行中的相似歌手递归当前快照
- 用户说明新的相似歌手递归脚本仍在运行中，要求基于当前已落盘结果统计名称文字类型分布，并检查截图中的 40 位艺人是否已找到。
- 本次只读取 `data/raw/qqmusic/singer_similar/runs/area_0_1_singer_list_seed/manifest.json`、`frontier.json` 和 `data/raw/qqmusic/singer_similar/request_cache/<mid>.json`，不读取 CSV，也不打断正在运行的脚本。
- 当前快照 `manifest_updated_at=2026-05-19T00:08:01Z`，manifest 中 seen 36304 个、requested 20361 个、frontier 15936 个；按 requested MID 读取 raw 缓存 20361 个，缺失 0 个，坏 JSON 0 个，raw 返回行 98082 行。
- 唯一艺人名称分布为：纯中文 26963 个、包含中文 3987 个、纯英文 5013 个、其他 341 个。
- raw 返回行名称分布为：纯中文 72634 行、包含中文 10716 行、纯英文 13866 行、其他 866 行。
- 40 位艺人严格等值匹配当前找到 7 位：余文乐、刘畊宏、江语晨、秀兰玛雅、谷祖琳、陈大天、魏如昀；其余 33 位当前快照未命中。

### 对 33 位未命中艺人做 quick_search 和反向相似歌手分析
- 用户要求对上次未命中的 33 位艺人使用 QQ 音乐 quick_search 查 MID，再对查到的 MID 合包请求一次 `get_similar(number=100)`，用于反向分析递归如何找到这些人。
- 已新增临时探查脚本 `scripts/probe_missing_similar_artists_33.py`，脚本只读取当前 `runs/area_0_1_singer_list_seed` manifest/frontier 和全局 `request_cache/<mid>.json`，写入 quick_search raw、相似歌手 raw 和分析 JSON，不修改正在运行的递归 manifest/frontier。
- 首次运行因沙箱网络权限失败；经授权后成功完成 33 个 quick_search 请求和 27 个唯一 MID 的相似歌手请求，其中 24 个 `get_similar` 为新请求、3 个为缓存命中。
- 脚本在最终向 GBK 终端打印完整 JSON 时遇到 `UnicodeEncodeError`，但分析 JSON 已在打印前成功写入 `data/processed/validation/singer_similar_reverse_probe_33/reverse_probe_summary.json`；后续已直接读取该 JSON 提炼结果。
- quick_search 可选中 MID 的查询 30 个，未选中 MID 的查询 3 个：`CUG嘻游记`、`Jesus Fashion Family`、`邱垲珊`；`黑珍珠` 的 top candidate 为韩文艺人相关的 `Yuri`，需视为低可信误匹配候选。
- 反向分析确认 7 个查询其实已在当前递归结果中，只是名称不完全等值或在本轮运行后才出现：`4 in Love` -> `4 In Love`、`SBDW`/`咻比嘟哗` -> `S.B.D.W`、`Selina`/`任家萱` -> `任家萱Selina`、`葛兆恩` -> `葛兆恩Kodii`、`郭书瑶` -> `郭书瑶`。
- 对尚未出现在当前递归结果的对象，反向相似列表中出现 frontier 邻居的包括 `吴宗宪`、`宋健彰`/`弹头`、`康康`、`林志玲`、`王澜霏`、`玺恩`、`许魏洲`、`黄俊郎`，这些只能作为后续继续跑时可能命中的候选入口，不能证明 QQ 音乐相似关系会反向返回目标。
- 反向相似列表只出现已请求邻居但当前 incoming 为 0 的对象包括 `Super Junior-M`、`伊能静`、`李威`、`杨颖`、`洪敬尧`、`浪花兄弟`、`游艾迪`、`芮恩`、`锦绣二重唱` 等；这些说明目标认为它们接近当前图，但当前已请求节点没有把目标返回出来，按当前算法不一定能自然发现。
- `Angelababy`、`柯有伦`、`黄怀晨` 的相似歌手结果未给出可用当前图入口；`江蕙` 仅返回未入图邻居 `童欣`；这些若必须覆盖，更适合作为额外种子或通过人工别名/目标名单补种。

### 统计相似歌手递归完成后的最终分布和 40 人命中情况
- 用户说明相似歌手递归已运行结束且找不到新的人，要求重新统计名称文字类型分布并检查截图中的 40 位艺人是否找到。
- 本次只读取最终 `runs/area_0_1_singer_list_seed/manifest.json`、`frontier.json` 和全局 `request_cache/<mid>.json`，不读取 CSV。
- 最终快照 `manifest_updated_at=2026-05-19T06:00:32Z`，seen 199973、requested 199972、frontier 0，raw 缓存读取 199972 个，缺失 0 个，坏 JSON 0 个，raw 返回行 989074 行。
- 唯一艺人名称分布为：纯中文 147514 个、包含中文 21984 个、纯英文 26175 个、其他 4300 个。
- raw 返回行名称分布为：纯中文 729993 行、包含中文 110397 行、纯英文 126532 行、其他 22152 行。
- 40 个查询名按严格名称等值命中 16 个，未命中 24 个；结合 quick_search MID 与已确认别名后，查询名层面实际命中 21 个、未命中 19 个。
- 若按现实对象口径合并 `Angelababy/杨颖`、`宋健彰/弹头`、`SBDW/咻比嘟哗`、`Selina/任家萱` 等别名，并排除 `黑珍珠 -> Yuri` 低可信候选，则 40 个查询对应的可信对象中命中 19 组、未命中 16 组。

### 分析临时完整运行站点目录未被忽略
- 用户指出 `site_temp_csv_fullrun/` 与 `site_large_temp_csv_fullrun/` 是未跟踪生成产物，且其中 `graph-data.js` 分别约 110MB 和 99MB，当前 `.gitignore` 没有拦截这两个目录。
- 已只读检查当前工作区状态，确认两个目录均为未跟踪目录，主要大文件分别为 `site_temp_csv_fullrun/assets/graph-data.js` 109720714 字节和 `site_large_temp_csv_fullrun/assets/graph-data.js` 98790223 字节。
- 已确认这两个目录不是默认正式输出名；默认站点输出仍是 `site/`、`site_mvp/`、`site_demo/` 和 `site_large/`，其中已有文件处于 Git 跟踪状态。
- 当前 `.gitignore` 只忽略 `data/`、`archive/`、`reports/`、数据库、日志和除共享头像图集外的 `site_assets/*`，没有覆盖临时站点输出目录；因此自定义 `--output-dir` 生成的 `site_temp_csv_fullrun/` 和 `site_large_temp_csv_fullrun/` 会显示为未跟踪。
- 风险边界：不宜简单使用宽泛的 `site*/` 或 `site_*` 规则，否则未来可能误隐藏新的站点发布目录或临时调试目录；更稳妥的规则是只补充本次确认的两个临时目录，或约定所有临时站点统一使用固定前缀后再按前缀忽略。
- 本次只完成分析和日志记录，未修改 `.gitignore`，未删除未跟踪目录，也未清理其中的大文件。

### 屏蔽临时完整运行站点目录
- 用户确认先只屏蔽 `site_temp_csv_fullrun/` 和 `site_large_temp_csv_fullrun/` 两个目录本身，不使用宽泛的 `*temp*` 忽略规则。
- 已在 `.gitignore` 的本地数据和生成产物区域精确追加 `site_temp_csv_fullrun/` 与 `site_large_temp_csv_fullrun/`。
- 影响范围仅限这两个临时完整运行站点目录；默认站点输出 `site/`、`site_mvp/`、`site_demo/`、`site_large/` 以及共享头像图集保留既有跟踪/忽略边界。

### 分析三个 graph-data.js 的无内容修改状态
- 用户指出 `site/assets/graph-data.js`、`site_demo/assets/graph-data.js`、`site_mvp/assets/graph-data.js` 显示为已修改，但 diff 和 numstat 没有内容变化，疑似换行状态噪音。
- 已检查 `git diff --numstat`、`git diff --stat`、`git diff --raw`、`git diff --summary` 和 `git diff --quiet`；这些命令均没有报告实际内容差异，`diff --quiet` 返回 clean。
- 已检查 `git status --porcelain=v2`，三个文件均为 `.M` 工作区状态，但显示的索引 hash 与工作区 hash 相同；`git hash-object` 计算出的三个工作区文件 blob hash 与 `git ls-files -s` 中索引 hash 完全一致。
- 已检查 `git ls-files --eol`，三个文件当前为 `i/lf w/lf`，仓库没有 `.gitattributes` 对其单独约束；当前 Git 配置启用了 `core.autocrlf=true`，因此 Git 提示这些 LF 文件在下次触碰时会被替换为 CRLF。
- 结论：这三个文件当前没有内容层面的变更，`status` 中的 `M` 是行尾/索引状态噪音；如需消除工作区噪音，应统一站点生成产物的行尾策略或刷新索引状态，但本次未修改这三个 `graph-data.js` 文件。
- 曾尝试对目标文件执行 `git update-index --refresh` 以刷新索引 stat 信息，但当前环境写入 `.git/objects` 权限不足而失败；该失败不改变前述内容无差异结论。

### 分析 Python 纯格式噪音来源
- 用户指出多个 Python 文件出现删除 `from __future__ import annotations` 后空行等纯格式噪音，怀疑不像 `black` 的标准输出，可能来自文本异常修复脚本。
- 已按规则重新读取 `AGENTS.md`、`develop_log.md` 和 `README.md`，并只读检查当前工作区 diff；当前工作区包含大量未提交源码、文档、站点产物和新增脚本改动，本次未回滚、未清理、未修改任何 Python 源码。
- 典型 diff 显示 `music_metadata_graph/pipelines/defaults.py` 和 `music_metadata_graph/text_normalization.py` 只有删除 `from __future__` 后空行、导入后空行这类变化；`collect_missing_song_singers_to_db.py` 中存在大量空行删除，覆盖 import、dataclass、函数体内部等位置。
- 已用指定 Conda Python 运行 `python -m black --diff --check` 检查典型文件，结果为 4 个文件都会被 black 保持不变；该结果只能说明当前文件已被整理到 black 可接受状态，不能证明这些空行删除由 black 首次产生。
- 已确认当前 `scripts/repair_text_anomalies.py` 仍包含 `compact_python()`，会把 Python 文件中连续空行压缩到最多 2 行，并在 `repair_text()` 中对 `.py` 调用该函数；这与当前 `AGENTS.md` 中“Python 正常格式统一交给 black，不得在文本修复脚本中重新规定 import、装饰器、函数体、括号内部空行等格式风格”的规则存在冲突。
- 当前判断：这些纯格式噪音更符合文本异常修复脚本对 Python 空行做过全局压缩后，再由 black 接受或进一步格式化的结果；不是单纯 black 的典型最小 diff。
- 验证结果：`python scripts/repair_text_anomalies.py` 核心文档扫描通过；`git diff --check -- '*.py'` 未报告空白错误；本次分析未执行任何源码修复。

### 统一仓库工作区行尾为 CRLF
- 用户指出 `git diff --check` 没有空白错误，但仍提示部分文件 `LF will be replaced by CRLF`，说明工作区行尾未完全统一。
- 已新增 `.gitattributes`，设置 `* text=auto eol=crlf`，并显式把压缩包、图片、Excel、数据库、文档包和可执行/二进制文件标记为 binary，避免 Git 对二进制做行尾转换。
- 已新增 `.editorconfig`，设置 UTF-8、`end_of_line = crlf` 和保存时保留文件末尾换行，用于约束支持 EditorConfig 的编辑器后续保存行为。
- 已用字节级 UTF-8 脚本对当前已跟踪和未跟踪的文本文件做机械式换行归一化，把 LF、CR 和混合换行统一为 CRLF；跳过 `.git`、`__pycache__`、`node_modules`、二进制扩展名、含 NUL 的文件和非 UTF-8 文件。
- 本次脚本实际归一化 25 个文本文件，跳过 43 个二进制文件、2 个已删除文件，未发现非 UTF-8 文本文件。
- 验证结果：`python scripts/repair_text_anomalies.py --all` 确认扫描到的 Markdown 与 Python 文件无 `CRCRLF`、隐藏控制字符、U+FFFD 替换字符或异常空行膨胀；`git diff --check` 无输出；`git ls-files --eol` 未再出现 `w/lf` 或 `w/mixed`，仅空文件显示 `w/none`。

### 复查 Python 纯格式噪音问题仍存在
- 用户追问“多个 Python 文件出现纯格式噪音，例如删除 `from __future__` 后空行”的问题当前是否仍存在。
- 已重新只读检查当前 `scripts/repair_text_anomalies.py`、Python diff 摘要和典型文件状态，未沿用上次结论。
- 当前 `scripts/repair_text_anomalies.py` 仍包含 `compact_python()`，并且 `repair_text()` 的 `.py` 分支仍会调用该函数压缩 Python 空行；这仍然违反“Python 正常格式交给 black，不由文本修复脚本定义 Python 空行风格”的当前规则。
- 当前 Python diff 中仍能看到大量删除空行的纯格式 hunk，包括 `build_large_graph_static.py`、`build_static_graph.py`、`collect_missing_song_singers_to_db.py`、`defaults.py`、`text_normalization.py`、`tests/test_run_full_pipeline.py` 等文件；`defaults.py` 与 `text_normalization.py` 仍显示只删除 import 后空行这类噪音。
- 当前结论：行尾 `CRCRLF` 问题已修复，但 Python 纯格式噪音的根因和既有 diff 噪音仍存在；需要后续单独修改文本修复脚本并整理/拆分这些 Python 格式 diff。

### 修复 Python 格式归属到 black
- 用户明确要求 Python 格式完全交给 black，并修复当前 Python 文件状态问题。
- 已修改 `scripts/repair_text_anomalies.py`：删除 `compact_python()`，`.py` 修复路径只做换行归一化和 AST 可解析验证，不再压缩或定义 Python 空行格式。
- 已进一步移除 `.py` 文件 `max_blank_run > 2` 作为异常和 `--fix` 触发条件的逻辑；脚本仍会输出 `max_blank_run` 统计，但不再把 Python 连续空行当成文本异常。
- 已运行 `python -m black --no-cache scripts/repair_text_anomalies.py`、`python -m black --no-cache --check music_metadata_graph scripts tests`，当前有效源码、脚本和测试目录 54 个 Python 文件均为 black 可接受状态。
- 已用临时 Python 文件验证 `python scripts/repair_text_anomalies.py --fix` 不再压缩 Python 连续空行；临时文件执行后已删除。
- 验证结果：`python scripts/repair_text_anomalies.py --all` 通过，扫描到的 Markdown 和 Python 文件均无 `CRCRLF`、隐藏控制字符、U+FFFD 替换字符、语法错误或文本异常；`python -m compileall -q music_metadata_graph scripts tests` 通过；`git diff --check -- scripts/repair_text_anomalies.py develop_log.md` 无输出。

### 修正同词曲同名去重步骤编号语义
- 用户指出 `filter_imported_songs.py` 的默认路径和 CSV 文件名已是第 16 步，但函数名、`filter_step`、运行摘要字段和 CLI 描述仍残留第 15 步语义；同时 `run_full_pipeline.py` 中部分错误文案仍引用旧步骤号。
- 已将 `filter_imported_songs.py` 中同词曲同名去重函数改为 `step16_dedupe_by_normalized_name()`，被剔除行的内部 `filter_step` 改为 `step16_same_credit_name_dedupe`，运行摘要字段改为 `step16_identity_dedupe`、`step16_removed_by_name_credit_dedupe`、`songs_after_step16` 和 `song_singer_rows_after_step16`。
- 已将 `filter_imported_songs.py` 的 CLI 描述改为 `Step 16`，并补充 `contextlib.closing()` 显式关闭 SQLite 连接，避免 Windows 测试临时数据库文件被未关闭连接占用。
- 已将 `run_full_pipeline.py` 的检查失败文案同步到当前编排步骤：专辑类型残留错误指向第 10 步，作词作曲关系缺失错误指向第 14 步。
- 已新增 `tests/test_filter_imported_songs.py`，构造最小 SQLite 数据验证第 16 步同词曲同名去重会写入 `filter_step=step16_same_credit_name_dedupe`，并检查运行摘要不再暴露旧第 15 步 key。
- 验证结果：指定 Conda Python 执行 `py_compile` 覆盖 `filter_imported_songs.py`、`run_full_pipeline.py` 和新增测试文件，未报错；执行 `python -m unittest tests.test_filter_imported_songs tests.test_run_full_pipeline`，共 6 个测试通过；执行 `python -m music_metadata_graph.pipelines.filter_imported_songs --help`，CLI 描述显示 `Step 16`。

### 分析头像图集和 large 站点产物的无内容修改状态
- 用户指出 `site_assets/avatar_atlas_150/*manifest*`、`site_large/assets/graph-data.js` 和 `site_large/assets/vendor/force-graph.min.js` 显示为已修改，但 `git diff` 无内容差异，疑似索引、换行或 mtime 状态噪音。
- 已限定路径检查 `git diff`、`git diff --raw` 和 `git diff --numstat`，这些命令均无输出，说明 Git 没有发现可展示的内容差异、模式差异或增删行统计。
- 已检查 `git ls-files --eol`，目标文件均为 `i/lf w/crlf attr/text=auto eol=crlf`，符合当前 `.gitattributes` 要求工作区使用 CRLF 的策略。
- 已检查 `git status --porcelain=v2` 和 `git ls-files -s`，目标文件的 HEAD blob、索引 blob 和模式值完全一致；`git hash-object --path` 计算出的工作区规范化 blob 也与索引 hash 完全一致。
- 曾对目标文件执行 `git update-index --refresh`；第一次因沙箱环境写入 `.git/objects` 权限不足失败，经授权后命令仍对其它真实改动文件报告 `needs update`，但目标路径后续限定 `git status` 已不再显示修改。
- 结论：这批文件没有内容层面的改动，原先 `status` 中的 `M` 属于索引/stat/行尾规范化状态噪音；本次未改写这些站点产物，也未处理工作区中其它真实改动。
- 验证结果：`git diff --check` 限定检查这批路径无输出；目标文件的 `hash-object --path` 结果分别与 `git ls-files -s` 中记录的 blob hash 一致。
