Read this file as UTF-8.

# AGENTS 协作说明

## 目的

本文档定义本仓库中用户与 AI 编码代理的协作方式、开发边界、验证要求和记录要求。

本项目采用 vibe-coding 协作方式：用户负责项目目标、方向、优先级和验收，AI 编码代理负责需求澄清、方案设计、代码实现、验证、文档同步和开发日志记录。

## 范围

这些规则适用于整个项目目录。

## 项目定位

当前项目信息：

- 项目名称：Musician_Relationship / 音乐人合作关系图谱。
- 项目类型：音乐平台元数据采集、标准化、图谱分析和可视化工具。
- 核心目标：围绕歌曲、音乐人和职能关系，采集并整理“演唱、作词、作曲”等合作信息，生成可查询、可分析、可视化的音乐人关系网络；节点优先使用音乐人头像展示。
- 主要用户：项目作者本人，用于技术研究、学习和个人本地分析；代码可开源，但数据采集与使用不面向商业化。
- 技术栈：Python 3.12、Conda、qqmusic-api-python、pandas、pydantic、httpx、tenacity、python-dotenv、duckdb/SQLite、networkx、pyvis，后续按需要加入 FastAPI、Streamlit 或独立前端。
- 运行环境：Windows 本地开发环境，使用指定的Conda环境：`D:\ASoftware\anaconda3\envs\Musician_Relationship\python.exe`。
- 当前不做的方向：不做音乐播放或下载工具；不提供绕过平台限制的能力；不追求一次性抓取全平台全量数据；不把大量歌词、头像、音频链接、cookie、token 或用户账号信息提交到仓库；不将第三方非官方接口包装成商用稳定服务。

AI 在执行任务时必须围绕项目定位工作，不得擅自扩大产品方向、引入无关能力或把临时方案当作长期架构。

## 协作职责

### 用户职责
- 提出需求、目标效果、优先级和验收意见。
- 对 AI 给出的方案进行确认、调整或否定。
- 重点检查项目整体进度、方案合理性、用户可见效果和关键代码。
- 保留最终决策权。

### AI 职责
- 主动理解用户需求，补全必要上下文，识别歧义、风险和边界。
- 先整理目标效果，再整理实现方案，最后执行开发。
- 按项目既有技术栈、目录结构、代码风格和文档规则实现。
- 完成必要验证，不凭推理宣称完成。
- 每次实质性分析、方案、实现、验证、事故或阶段回顾后，按 `develop_log.md` 顶部规则追加开发日志。
- 向用户汇报时优先描述用户可见效果、入口、页面、按钮、数据变化、验证路径和剩余风险。

## 必读顺序

AI 开始任务前按以下顺序读取上下文：

1. `AGENTS.md`：确认协作规则、边界和强约束。

2. `develop_log.md`：确认相关历史方案、决策、实现、验证和事故记录。

3. 当前任务相关源码、文档、配置和测试。

涉及已有功能时，必须先搜索并阅读相关实现，不得凭文件名或记忆假设代码结构。

## 需求处理规则
- 用户提出功能需求时，AI 必须先整理“目标效果”。
- 目标效果应描述用户最终能看到什么、从哪里进入、如何操作、成功和失败时分别发生什么。
- 目标效果明确后，再整理“实现方案”。
- 实现方案应描述涉及的模块、数据、页面、接口、验证方式和风险。
- 重大歧义必须先询问用户；轻微歧义可以作保守假设，并在方案中说明。
- 不得发明用户没有提出的偏好、约束或目标。
- 用户纠正 AI 理解时，应把纠正视为协作规则或上下文缺口，立即调整当前方案。

## 方案表达规则

AI 给方案时使用以下顺序：

1. 目标效果：用户可见结果和验收方式。

2. 实现方案：代码、数据、接口、文档和验证如何落地。

3. 风险边界：兼容性、数据安全、权限、性能、测试缺口。

4. 本轮不做：明确排除的范围。

涉及重构、抽组件、架构调整时，优先按用户可见页面、入口、弹窗、列表、按钮、图表和验证路径说明，再补充内部代码结构。

## 代码修改规则
- 修改前先搜索、阅读和定位，不直接猜测。
- 优先沿用项目现有模式、命名、目录、组件、工具函数和测试方式。
- 保持改动范围服务当前目标，不做无关重构。
- 新增抽象必须解决真实重复、真实复杂度或明确的职责边界问题。
- 大文件修改前先定位函数、状态和调用链，避免全局替换。
- 仓库存在上游参考目录、模板目录、示例目录或历史快照目录时，默认只作为参考材料；主动开发应落在当前项目的有效源码目录，除非用户明确要求回写参考目录。
- 从上游参考代码迁移功能时，优先复用其成熟实现、注释和边界处理，并调整到当前项目结构中；不应在不了解原实现意图时重写一套行为不一致的逻辑。
- 涉及 UI 时保持项目现有设计系统、样式变量、组件结构和交互习惯。
- 涉及数据导入、导出、删除、覆盖、迁移、权限和账号凭据时，优先保护用户数据和可回退性。
- 不得执行破坏性回滚命令，不得擅自删除用户改动。
- 发现非本人造成的意外改动时，立即停止当前写入动作，向用户说明并询问如何继续。

## 语言与代码风格规则
- 新增代码、注释、文档和提交信息应使用项目既有主要语言；项目明确要求单一语言时，严格保持一致。
- 函数、类、模块、注释、docstring、章节分隔符等风格遵循项目现有规范。
- 项目没有明确注释规范时，只在复杂分支、循环、数据转换、边界处理和非显然业务规则前添加简洁注释。
- 不写占位式注释、空泛 docstring 或重复代码本身含义的说明。
- 用户明确表达的命名、格式、术语、大小写、拼写、引用、图表标题或文体偏好，应记录到“用户长期偏好”或“项目补充规则”。

## 文档同步规则
- 用户可见功能变化必须同步项目的用户文档、帮助说明、版本记录或发布说明。
- 数据结构、架构边界、运行方式、构建流程、验证门槛变化必须同步项目开发文档。
- 协作规则、用户长期偏好、提交规则、验证规则变化必须同步 `AGENTS.md`。
- 开发过程、方案、实现、验证、事故和阶段回顾必须记录到 `develop_log.md`。
- 版本记录只写相对上一版本的最终用户可感知变化，不写开发过程、调试过程、临时方案、反复修正或内部实现细节。

## 开发日志规则入口
- 每次实质性变更后，必须追加 `develop_log.md`。
- 用户提出功能需求并要求方案时，分析结果和方案也必须追加到 `develop_log.md`。
- 开发日志的具体格式、分段和追加规则，以 `develop_log.md` 顶部“撰写规则”为准。
- 开发日志不是版本记录；版本记录不是开发日志。

## 验证规则
- 代码改动后必须运行与风险匹配的验证命令。
- 项目存在统一构建命令时，仓库追踪代码改动完成后默认运行构建。
- 根据改动性质选择验证强度；小范围文案或注释改动可以使用轻量检查，依赖、引用、结构、入口、构建配置或数据流程变化必须使用更完整的验证。
- Bug 修复优先先复现，再修复，再补回归验证。
- UI 改动需要验证用户实际入口，不只验证内部函数。
- 无法运行验证时，必须说明原因、风险和替代检查。
- 用户明确暂停某类验证时，按用户最新规则执行，并在开发日志中记录暂停范围和恢复条件。

## 提交规则
- 不允许空提交。
- 提交应按职责边界拆分，不把不相关改动混在一次提交中。
- 提交前执行 `git status --short`，确认全部改动清单。
- 提交前检查目标文件 diff，确认提交边界。
- 只暂存目标文件或目标 hunk，不使用无差别全量暂存。
- 用户要求只提交部分文件或部分改动时，优先使用选择性暂存；不得通过删除或改写工作区内容来排除无关改动。
- 提交后复核提交文件范围，并确认无关改动仍留在工作区。
- 提交后若发现工作区出现刚提交前未观察到的新改动，默认只报告剩余改动，不继续处理或追加提交；除非用户明确要求。
- 提交信息必须说明改动目的和主要内容，避免 `update`、`fix`、`misc` 等空泛描述。
- 使用英文填写提交标题和描述。
- 你可以自行决定提交时机，在你认为合适的时机提交，例如完成了一个方案的多次分析确定了方案/进行了多次开发完成了一个模块/等等。

推荐提交类型：

- `[feat]`：用户可见功能或交互行为新增。
- `[fix]`：缺陷修复。
- `[dev]`：构建、测试、脚本、工程流程、开发体验。
- `[doc]`：文档更新。
- `[ver]`：版本更新。

## 安全与隐私规则
- 不得把 token、密钥、密码、证书指纹、私有签名材料写入代码、日志、文档、提交信息或示例配置。
- 不得在日志中记录未脱敏的用户私密内容、本机私有路径、账号信息或可复用凭据。
- 不得伪造外部服务返回、数据权限、统计结果、测试结果或构建结果。
- 涉及用户数据删除、覆盖、迁移、导入和导出时，必须明确影响范围和回退方式。
- 不得擅自清理构建产物、编译中间文件、报告生成文件、缓存或归档文件；只有在项目规则明确允许或用户明确要求时才执行清理。
- 对外说明投资、医疗、法律、财务等高风险内容时，必须保持项目定位，不输出超出项目职责的结论。

## 用户长期偏好

本节只记录用户明确表达且会长期影响项目开发方式的偏好。

记录规则：

- 只记录用户实际说明的偏好。
- 不记录 AI 推测出的偏好。
- 偏好过期时更新原规则，不保留互相冲突的规则。
- 每条偏好必须可操作，能指导后续开发。

当前偏好：

- 用户主要通过项目实际效果、整体方案和关键代码验收开发结果。
- AI 说明方案时应优先使用用户可见效果和验收路径表达。
- 修改文件后进行机械式替换，把行尾符统一为CRLF。
- 用户需要本地文件以可点击 Markdown 链接形式给出，不接受只给纯文本路径；Windows 本地链接必须使用正斜杠绝对路径，例如 `[文件名](D:/B0Projects/my_tools/Musician_Relationship/path/file.md)`，不得在链接目标中使用反斜杠。
- 高可信分支之外的另一个歌曲输入分支统一称为“补充分支”，不得称为“全集分支”“主页分支”或其他名称。
- 由于 PowerShell 对中文和编码处理不稳定，涉及中文常量、中文文件内容、Markdown 表格、报告生成或中文输出判断时，必要时优先使用明确 UTF-8 配置的 Python 工具或仓库脚本，而不是直接依赖 PowerShell。
- 重新设计请求顺序、存储结构、数据模型或流程边界时，如果存在关键目标、输入、输出、验收或风险未明确，AI 应先停止设计并与用户讨论，不得用未经确认的假设继续设计。

## 项目补充规则

项目初始化或后续开发中，把本项目特有规则追加到本节。

可记录内容：

- 目录结构和模块职责。
- 上游参考目录、模板目录、示例目录和历史快照目录的使用边界。
- 项目语言、注释、docstring、章节分隔符和文体格式。
- 平台、设备、浏览器或运行环境约束。
- 构建、发布、签名和归档流程。
- 生成产物、编译中间文件、缓存和归档文件的保留/清理规则。
- 数据模型和兼容规则。
- UI 设计系统和交互约束。
- 测试门槛和回归清单。

当前项目规则：

- 当前状态：项目已进入请求顺序和存储结构重新设计阶段，当前活跃流程围绕 QQ 音乐 raw 缓存、SQLite 结构化入库、过滤 CSV 和关系表逐步确认。
- 当前有效源码保留在 `music_metadata_graph/`；主动开发应落在该包及后续正式子目录中。新的命令入口必须随新流程逐步确认后再写入 `pyproject.toml`，不得继续暴露已归档脚本入口。
- 重新设计第一步已确认：先请求 QQ 音乐完整歌手列表并保存原生 JSON 到 `data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all/`，用于检查字段键和支撑歌手表入库。
- 重新设计第二步已确认：在完整歌手列表 raw 之后请求歌手近似粉丝量 raw。先调用 `qqmusic.singer.get_singer_list`，默认只传入 `AreaType.TAIWAN` 和 `AreaType.CHINA`，从 `concernNum` 快速覆盖；再扫描第三步入库目标范围内 `area_id in (0, 1)` 但未覆盖的 MID，使用 `qqmusic.singer.get_info` 的 `Info.FansNum.Num` 以 `Client.gather()` 合包补齐。两种粉丝量可无条件合并为近似粉丝量；重复运行时已存在 raw JSON 不再重复请求，不追求实时更新。正式汇总写入 `data/raw/qqmusic/singer_fans_summary.json`，MVP 汇总写入 `data/raw/qqmusic/singer_fans_summary_mvp.json`，二者不得互相覆盖。批量补齐必须按批渐进落盘，批次失败时降级单个请求，仍有失败时保留已成功结果并非零退出。
- 重新设计第三步已确认：音乐人表统一命名为 `artists`，使用 QQ 音乐 `mid` 作为主键，不再保存 QQ 音乐数字 `id` 字段；第三步歌手列表入库时必须同时满足 `area_id in (0, 1)` 和第二步粉丝量汇总中存在可用正数 `fans_num`，并写入近似粉丝量来源和 raw 路径追溯字段。
- 重新设计第四步已确认：正式流程应对第三步按当前入库规则从歌手列表 raw 中选中的歌手请求主页歌曲接口作为歌曲源数据；不得因为后续歌曲歌手或制作人补入 `artists` 就自动扩大第四步请求范围。开发阶段可使用四位歌手周杰伦、薛之谦、林俊杰、汪苏泷的主页歌曲 Tab raw JSON 验证结构。
- 重新设计第五步已确认：在请求歌曲后、请求专辑前，扫描歌曲 `singer[].mid`，对不在 `artists` 表中的非空歌手 MID 请求 `qqmusic.singer.get_info`，保存 raw JSON 到 `data/raw/qqmusic/singer_info/` 并补入 `artists`；`mid`、`name` 任一为空则不入库，`icon` 优先取接口歌手头像，空时尝试 `Info.BaseInfo.BackgroundImage`，仍为空则保留空字符串；若 `Info.FansNum.Num` 为可用正数，必须同时写入 `fans_num`、`fans_source=qqmusic.singer.get_info.FansNum.Num` 和 `fans_raw_json_path`，且不得用空粉丝量覆盖已有正数粉丝量。
- 第五步前置补 MID 已确认：扫描步骤四当前目标范围内歌曲 raw 中 `SongTab.List[].singer[]` 的 `mid` 为空、`name` 非空演唱歌手；`--all` 目标范围必须与第四步一致，读取第一步歌手列表 raw 并套用第三步当前入库过滤规则，不得扫描历史落盘但已不属于第四步目标范围的歌手主页歌曲 raw。名字不含 `/`、`，`、`、` 时，先查当前 `artists` 表，库内姓名精确且唯一命中时直接记录为 `db_matched`，不请求 `quick_search`，库内同名多 MID 时记录为 `db_ambiguous_name` 且不自动选择；库内未命中时才调用 `quick_search`，并先读取本地 quick_search raw 缓存，缓存不存在时才请求 QQ 音乐。名字包含 `/`、`，`、`、` 时不再按原始整体名字检索，而是直接按这些分隔符拆开后分别执行同样的“先查库、再搜索”唯一精确匹配补 MID。每次运行都会重写 `data/processed/validation/song_singer_mid_fill/csv_views/song_singer_mid_fill.csv` 作为人工检查视图，流程不再读取旧 CSV 作为断点输入或跳过依据；quick_search raw 写入 `data/raw/qqmusic/quick_search_artist_mid/song_singer/`；第八步歌曲入库不读取该 CSV，而是直接查询 `artists` 表，缺 MID 演唱歌手名包含 `/`、`，`、`、` 时同样按这些分隔符拆分，能唯一命中的片段会入库，不能唯一命中的片段跳过，只有没有任何片段命中时才按缺 MID 拒绝。
- 重新设计第六步已确认：专辑请求不再按歌手请求歌手专辑列表，而是在请求歌曲和补全歌曲歌手之后，从歌曲 raw JSON 的 `album.mid` 或非 0 `album.id` 去重后请求 `qqmusic.album.get_detail`，raw JSON 写入 `data/raw/qqmusic/song_album_detail/`。
- 第四步歌曲 Tab raw 未全量完成但需要继续后续流程时，第 5、6、8 步使用 `--all`，只扫描第四步当前目标范围与已落盘歌曲 Tab raw 的交集；不得扫描历史落盘但已不属于第四步目标范围的歌手主页歌曲 raw。这三个脚本不再暴露旧的 `--existing-song-tabs` 参数，也不再提供旧的数据库歌手严格全量或全 raw 目录扫描语义。
- 旧歌手专辑列表 raw、旧专辑表导出和旧专辑入库实现已归档到 `archive/album_source_retiming_2026-05-13/`；当前正式流程不得再把 `data/raw/qqmusic/singer_album_list/` 作为专辑来源。
- 重新设计前的当前流程已归档到 `archive/redesign_reset_2026-05-13/`，包括 `music_metadata_graph/pipelines/`、`scripts/`、`data/raw/`、`data/processed/`、`reports/`、旧网页依赖配置和 force-graph 参考文档；这些内容只作为历史参考，不得作为当前正式流程继续运行或写回当前正式目录。
- 更早的旧端到端流程已归档到 `archive/legacy_pipeline_2026-05-12/`，包括旧采集、旧验证、旧报告、旧网页、旧数据产物和旧缓存；当前正式流程不得再从这些目录读取，也不得把旧流程代码、网页或数据写回当前正式目录。
- 新存储方向：接口响应后可以先保存原生 JSON 到本地 raw 缓存作为原始证据，同时在同一次采集过程中把结构化字段写入数据库；后续清洗、过滤、去重、关系边生成和查询应围绕数据库进行，不再把 JSON 文件作为正式清洗输入。
- 数据库边界：数据库不重复保存完整原生 JSON；只保存原始 JSON 路径、接口名、请求参数、抓取时间、状态、来源记录 ID 和抽取出的结构化字段。需要回看原始响应时，通过数据库记录中的路径回到 `data/raw/` JSON 文件。
- 后续重新引入本地数据目录时，`data/raw/` 保存接口原始缓存，数据库保存结构化处理数据，导出的 CSV 或网页静态 JSON 只作为查看或发布产物；原始缓存、数据库文件、大量图片和生成图谱默认不提交 Git。
- CSV 边界：CSV 永远只作为人工检查、验收查看或发布产物，不得作为任何正式脚本、工具、站点生成、断点续跑、清洗、过滤、入库或图谱构建的输入来源；正式输入必须来自 raw JSON、manifest、SQLite/数据库或明确的结构化源文件。
- 相似歌手递归缓存规则：`qqmusic.singer.get_similar(mid, number)` 原始响应按源歌手 MID 全局复用，默认写入 `data/raw/qqmusic/singer_similar/request_cache/<source_mid>.json`；`number` 只能作为 raw JSON 内部请求元信息，不得成为缓存父目录或缓存键。具体递归任务的 `manifest.json`、`frontier.json`、发现层数、首次来源和种子信息写入 `data/raw/qqmusic/singer_similar/runs/<run_id>/`。后续无论从哪个根节点、种子集合或 number 参数递归，都不得把相同 `source_mid` 的 raw 重复保存在根节点目录下；合包请求也不得改变“一个 source MID 一个 raw JSON”的追溯方式。
- 验证测试阶段每一步过滤仍必须能同时查询保留行和被过滤行；被过滤行不得丢弃，必须保留过滤步骤、结果、原因、目标歌手和来源记录追溯信息。
- 数据源优先级：第一阶段以 QQ 音乐非官方接口作为主数据源，优先验证 `qqmusic-api-python`；网易云音乐作为补充和交叉校验；酷我、酷狗等平台仅作为缺失字段兜底来源。
- 当前重新设计约束：项目只使用 QQ 音乐数据源，不再为网易云、酷我、酷狗或其他平台预留多平台合并结构，除非用户后续明确变更。
- 音乐人身份规则：`artists` 表使用 QQ 音乐 `mid` 作为主键；当前不引入额外内部 artist_id，也不保存 QQ 音乐数字 `id` 字段。
- 音乐人入库字段：`artists` 表只保存 `mid`、`name`、`area_id`、`fans_num`、`fans_source`、`fans_raw_json_path`、`other_name`、`icon`、`spell` 和 `raw_json_path`、`raw_page`、`raw_row_index`；`fans_num` 为可空整数。第三步从完整歌手列表 raw 入库前只保留 `area_id` 明确为 `0` 或 `1` 且从第二步粉丝量 raw 汇总中合并到可用正数粉丝量的歌手行；后续通过歌曲歌手或制作人补入的音乐人如果没有地区字段，则 `area_id` 保留为空，没有粉丝量则 `fans_num` 保留为空，且不得覆盖已有正数粉丝量；`mid`、`name` 必须非空，`mid` 为主键；不再保存完整歌手列表中的 `id`、`pmid` 或旧 `singer_pic` 字段。
- 专辑入库规则：`albums` 表从 `data/raw/qqmusic/song_album_detail/` 的 `basicInfo` 抽取字段，使用 `mid` 作为主键，`id` 作为唯一字段，只保存 `mid`、`id`、`name`、`albumType`、`publishDate` 和 `raw_json_path`、`raw_page`、`raw_row_index`；`mid`、`id`、`name`、`albumType`、`publishDate` 必须非空，不满足完备约束的专辑不得写入 `albums`，必须写入 `data/processed/validation/album_import_rejections/csv_views/album_import_rejections.csv`，且 CSV 最后一列必须为短代码 `reason_code`；当前不导入 `singer.singerList[]`，不得继续沿用旧歌手专辑列表的字段来源假设。
- 歌曲入库规则：歌曲表只记录唯一歌曲实体，不记录歌曲来自哪个歌手主页的来源关系；QQ 音乐歌曲 `mid` 作为主键；当前 `songs` 只入库完备歌曲，约束为 `mid/id/name/title/language/album_mid` 非空，`id` 唯一，`album_mid` 外键到 `albums.mid`，歌曲演唱者列表非空，且每个 `singer_mid` 非空并外键到 `artists.mid`。
- 歌曲入库失败记录：不满足完备歌曲约束的唯一歌曲必须写入拒绝 CSV，当前路径为 `data/processed/validation/song_import_rejections/csv_views/song_import_rejections.csv`；该 CSV 遵守第十步之前歌曲相关导出 CSV 的统一基础列规则，并在最后追加短代码 `reason_code`，不得输出长句自然语言原因或 raw 追溯字段。
- 歌曲入库后过滤规则：第九步歌曲入库时先判断歌曲满足完备入库约束，再把 `language=9` 的完整歌曲写入 `data/processed/validation/song_filtering/csv_views/songs_removed_by_step9_language_9.csv` 并排除出 `songs`，后续步骤不得再处理 `language=9` 歌曲；第十步从 `songs` 中优先保留专辑类型为 `Single`、`EP`、`录音室专辑` 的歌曲；非白名单专辑类型歌曲只有在同一个 `songs.name` 于当前库里出现不止一首时才过滤，若该 `name` 在库里只有一首则保留；过滤掉的歌曲正式导出到 `data/processed/validation/song_filtering/csv_views/songs_removed_by_step10_album_type.csv`；第十一步在步骤十后请求 `song.get_producer` 制作人 raw JSON 并检查作词/作曲缺 MID；第十二步只对结构化制作人作词/作曲不完整的歌曲请求 `lyric.get_lyric(song_mid)`，请求返回的完整歌词只允许在内存中解密和解析，长期缓存必须写入 `data/raw/qqmusic/song_lyric_credit/` 下的有限证据 JSON：保存 `cache_kind=qqmusic_lyric_credit_evidence`、歌曲标识、来源接口、结构化缺失角色、解密后原始前 10 行、有效前 5 行、解析出的词曲行、解析状态和必要计数，不得保存完整 `lyric`、`trans`、`roma` 或 `qrc`；读到旧完整歌词 raw 时应读时迁移并覆盖为有限证据格式；歌词解析视图写入 `data/processed/validation/song_lyric_credit/csv_views/song_lyric_credit.csv`；歌词补充只可补结构化制作人缺失的角色，不得覆盖结构化已有作词或作曲。第十三步前置补 MID 同时扫描结构化制作人缺 MID 和歌词补充得到的缺失角色姓名；第十四步导入作词/作曲到 `song_credit_artists`，并将结构化制作人中带 MID 的缺失制作人补入 `artists`，同时导出 `data/processed/validation/temp_song_filtering/csv_views/songs_after_step14_credit_import.csv` 临时歌曲 CSV；第十四步临时 CSV 默认只导出演唱歌手包含周杰伦、林俊杰、薛之谦、汪苏泷任意一人的歌曲，这只限制临时 CSV 查看范围，不限制作词作曲关系入库范围；第十五步删除作词或作曲不完整的歌曲，保留条件为至少 1 个 `作词` 且至少 1 个 `作曲`，过滤掉的歌曲正式导出到 `data/processed/validation/song_filtering/csv_views/songs_removed_by_step15_incomplete_credits.csv`，默认额外导出 `data/processed/validation/temp_song_filtering/csv_views/songs_after_step15_complete_credits.csv` 临时保留 CSV；第十六步在剩余歌曲中按“规范化歌名 + 同作词 + 同作曲”去重，歌名规范化必须复用 `music_metadata_graph.text_normalization.normalize_song_title_identity()`，该规则覆盖 Unicode `NFKC`、中英文常见标点等价、连续省略号、`feat./ft./featuring` 写法、括号内侧空格和标点两侧空格，但保留普通英文词间空格和括号中的语义版本文本；作词和作曲分别按 `artist_mid` 集合判断，同一角色内的人员顺序不影响比较，演唱歌手不再参与本步骤去重判断，优先级为 `录音室专辑 > EP > Single > 较小 song id`，过滤掉的歌曲正式导出到 `data/processed/validation/song_filtering/csv_views/songs_removed_by_step16_same_credit_name_dedupe.csv`；第十六步临时保留 CSV 默认只导出演唱歌手包含周杰伦、林俊杰、薛之谦、汪苏泷任意一人的保留歌曲，这只限制临时 CSV 查看范围，不影响全库去重和正式删除清单。`songs.mid` 主键和 `songs.id` 唯一约束已保证 mid/id 唯一，去重步骤只需报告唯一性检查，不再单独执行 mid/id 去重。
- 作词作曲关系规则：`song_credit_artists` 使用 `(song_mid, role, artist_order)` 作为主键，`song_mid` 外键到 `songs.mid`，`artist_mid` 外键到 `artists.mid`；`role` 当前只导入 `作词` 和 `作曲`。
- 第十三步前置补 MID 已确认：扫描步骤十一制作人 raw 中 `作词`、`作曲` 条目的 `mid` 为空、`name` 非空制作人，并扫描第十二步歌词补充 raw 中只用于结构化缺失角色的姓名；名字不含 `/`、`，`、`、` 时，先查当前 `artists` 表，库内姓名精确且唯一命中时直接记录为 `db_matched`，不请求 `quick_search`，库内同名多 MID 时记录为 `db_ambiguous_name` 且不自动选择；库内未命中时才调用 `quick_search`，并先读取本地 quick_search raw 缓存，缓存不存在时才请求 QQ 音乐。名字包含 `/`、`，`、`、` 时不再按原始整体名字检索，而是直接按这些分隔符拆开后分别执行同样的“先查库、再搜索”唯一精确匹配补 MID。每次运行都会重写 `data/processed/validation/song_credit_mid_fill/csv_views/song_credit_mid_fill.csv` 作为人工检查视图，流程不再读取旧 CSV 作为断点输入或跳过依据；quick_search raw 写入 `data/raw/qqmusic/quick_search_artist_mid/song_credit/`；第十四步作词作曲导入不读取该 CSV，而是直接查询 `artists` 表，缺 MID 制作人名包含 `/`、`，`、`、` 时同样按这些分隔符拆分，能唯一命中的片段会入库，不能唯一命中的片段跳过。
- 歌曲相关导出 CSV 列规则：所有歌曲 CSV 按歌名拼音首字母和拼音排序，不按 Unicode 字符顺序排序；第十四步导入作词作曲之前的歌曲基础列为 `song_mid`、`song_id`、`song_name`、`song_title`、`song_language`、`album_name`、`album_type`、`album_publish_date`、`singer_count`、`singers_json` 这 10 列；第十四步及之后的歌曲基础列为 `song_mid`、`song_id`、`song_name`、`song_title`、`song_language`、`album_name`、`album_type`、`album_publish_date`、`作词`、`作曲`、`singer_count`、`singers_json` 这 12 列，`作词`、`作曲` 必须放在演唱信息前；所有入库失败或过滤剔除 CSV 必须在基础列最后追加 `reason_code`，原因值使用有意义的短词组代码，不写长句自然语言；临时保留 CSV 不追加原因列；`singers_json` 为 JSON 数组，每个歌手对象只包含 `mid` 和 `name`。
- CSV Excel 安全规则：所有正式或临时导出 CSV 在写出文本单元格时，如果去掉开头空白后以 `=`、`+`、`-`、`@` 开头，必须在 CSV 展示值前加单引号，避免 Excel 打开时把歌名、专辑名、制作人名等文本当成公式；该转义只作用于 CSV 输出，不得改写数据库和 raw JSON。
- 数据采集边界：只采集关系图谱研究需要的元数据，例如歌曲名、音乐人名、平台 ID、头像 URL、专辑、发行信息、演唱/作词/作曲/编曲/制作人关系、榜单或热度快照；不采集音频文件，不实现下载播放能力。
- 数据模型原则：内部标准模型至少包含 `Artist`、`Song`、`CreditEdge`、`PopularitySnapshot`、`SourceRecord`；平台原始字段必须通过 adapter 转换为标准模型，业务层不得直接依赖某个平台响应结构。
- 来源可追溯：每条关系边必须记录来源平台、来源接口、原始字段或原始文本、抓取时间、解析方式和置信度；解析自歌词文本的作词/作曲关系置信度低于结构化制作人接口。
- 身份消歧：同名音乐人不得只按姓名合并；优先使用平台 artist id / singer mid；没有平台 ID 的词曲作者先保留为 unresolved credit name，后续再人工或半自动匹配。
- 请求策略：采集脚本必须有低频请求、失败重试、可恢复断点和本地缓存；不得写高并发、无限循环或规避风控的默认行为。
- pipeline 脚本的默认 SQLite 路径必须复用 `music_metadata_graph/pipelines/defaults.py` 中的 `DEFAULT_DB_PATH`；不得在各脚本中重复写 `data/music_metadata_graph.sqlite3`，但命令行入口仍应保留 `--db` 覆盖能力。
- MVP 流程必须复用正式 raw 目录，不另建 MVP raw；默认数据库为 `data/music_metadata_graph_mvp.sqlite3`，validation 产物写入 `data/processed/validation_mvp/`。MVP 模式第一步只确保歌手列表第一页 raw 存在，第二步只确保前 10 个 `area_id in (0, 1)` 歌手的粉丝量 raw 可用并写入独立的 `singer_fans_summary_mvp.json`，第三步只导入满足 `area_id in (0, 1)` 且有可用正数粉丝量的前 10 个歌手，后续步骤逻辑不变但目标解析使用同一 MVP 范围。
- 一键完整流程入口为 `python -m music_metadata_graph.pipelines.run_full_pipeline`；该入口必须在每一步前后做 raw、CSV、SQLite 表、外键、目标覆盖、过滤约束、网站资源和网站生成结果检查，任一检查失败应立即停止，不得默认上一脚本已经正确跑完。该编排入口把粉丝量 raw、歌词补充 raw、两个前置补 MID 步骤、一个网站资源准备步骤、一个共享头像图集步骤和两个网站生成步骤单独编号，因此显示 1 到 20 个编排步骤；第 9 步歌曲入库同时筛除 `language=9` 的完整歌曲并导出删除 CSV；第 12 步请求歌词补充 raw；第 13 步补作词作曲缺 MID；第 14 步导入作词作曲关系；第 15 步删除作词作曲不完整歌曲；第 16 步按同名同词曲去重；第 17 步准备标准网站资源并缓存原始头像到 `data/raw/qqmusic/avatar_cache/`，第 18 步按默认 `auto` 模式生成或复用共享 150x150 WebP 头像图集到 `site_assets/avatar_atlas_150/`，第 19 步生成标准静态网站，第 20 步生成 large-graph 静态网站，large-graph 默认使用完整数据库并输出到 `site_large/`。
- 标准静态网站生成脚本为 `python -m music_metadata_graph.pipelines.build_static_graph`；默认使用完整数据库并输出到 `site/`，必须包含数据库中全部可视化目标歌手和关系，不得再截断为前 10 位目标歌手；只有显式传入 `--mvp` 时才使用 MVP 数据库并输出到 `site_mvp/`；显式传入 `--demo` 时使用完整数据库并输出到 `site_demo/`，目标歌手从 MVP 的 10 位种子歌手出发，但图谱数据必须纳入这 10 位歌手作为演唱者、作词人或作曲人参与的全部关系边及相连音乐人节点。标准网站生成前必须先运行 `python -m music_metadata_graph.pipelines.prepare_static_graph_assets` 准备各站点自己的 `assets/graph-data.js`、`assets/vendor/force-graph.min.js` 并缓存原始头像到 `data/raw/qqmusic/avatar_cache/`；随后运行 `python -m music_metadata_graph.pipelines.build_avatar_atlas` 生成或复用项目级共享 `site_assets/avatar_atlas_150/`，图集使用 150x150 像素头像、3000x3000 WebP atlas、质量 80、去除不必要元数据，并按 MVP、demo、完整站点的头像使用顺序制作，使各站点可按 profile 加载共享图集前缀；图集脚本必须支持默认 `auto` 指纹复用、`--force` 强制重建和 `--check` 只验证不写入，重建时应先写临时目录并验证通过后替换正式目录；头像准备步骤必须对每个头像 URL 打印 `[当前/总数]` 进度并接入正式运行日志，未缓存头像按音乐人的 `演唱 + 作词 + 作曲` 关联数量从高到低排序，默认按 1 秒间隔启动下载请求，下载耗时不阻塞后续请求启动；生成后的标准网页不得再把全量图谱数据和 force-graph 运行库内嵌进单个 HTML，且 `site/`、`site_mvp/` 与 `site_demo/` 不得各自重复维护头像缓存或头像图集。标准网页和 large-graph 网页顶部控制区必须使用两列两行布局：左侧标题和数据库说明跨两行，右侧第一排只放图谱显示开关，右侧第二排放目标歌手粉丝量筛选、目标歌手下拉、最小歌曲数和搜索框；目标歌手粉丝量筛选控件使用单行布局，格式为“目标歌手粉丝、可编辑下限输入框、双滑块轨道、可编辑上限输入框”，不得再显示中间“至”；输入框支持普通数字、`500万` 这类简写和上限 `不限`，默认范围为 500 万以上；目标歌手下拉菜单只显示当前粉丝量范围内的目标歌手，候选顺序按粉丝量从高到低排列，菜单项文本只显示歌手名；粉丝量范围变化不得清除范围外目标歌手的既有勾选，范围调回后必须恢复此前勾选状态；顶部搜索框必须按 Enter 执行，只在当前图中找到音乐人时选中并高亮节点，命中多个音乐人时必须全部选中，没搜到时不得改变当前选中状态；页面必须提供“隐藏叶节点”开关，开启后隐藏当前图中只连接另一个唯一节点的叶节点及相关边，叶节点判断不得受作词/作曲是否分开影响，该开关只在完整数据库的标准完整图默认开启，MVP、demo 和 large-graph 页面默认关闭；页面必须提供“仅显示目标歌手”开关且默认关闭，开启后不显示扩展制作人或邻接音乐人节点，只保留两端都是当前目标歌手的关系边，并显示全部当前目标歌手节点，孤立目标歌手也必须保留；标准图开启“显示名字”时，名字基础文字透明度必须按节点权重映射，默认范围为 0.5 到 1，选中或高亮节点文字必须直接不透明，未高亮节点在淡化状态下继续按淡化系数降低；完整数据库的标准完整图默认关闭“作词/作曲分开”并禁用节点拖动，MVP、demo 和 large-graph 页面默认开启“作词/作曲分开”；large-graph 页面不使用标准图谱的名字绘制或粒子效果，“显示名字”和“粒子效果”开关必须置灰且不可交互；所有网页都支持左键点击图谱空白处取消选中，并保留右键点击图谱区域任意位置取消选中；选中歌手时详情栏必须显示“视图”下拉菜单，默认“全部”，“输入”仅显示别人给选中歌手作词/作曲的关系，“输出”仅显示选中歌手给别人作词/作曲的关系；选中两名及以上歌手时详情栏必须显示“边关系”下拉菜单，默认“交集”，切换到“并集”时必须高亮所有选中节点的相关边及相连节点。
- 网页展示字段规则：标准网页和 large-graph 网页中的歌曲展示必须优先使用 `songs.title`，仅在标题缺失时回退 `songs.name`；专辑展示若图谱数据存在 `album_title` 则优先使用 `album_title`，否则回退 `album.name`。该规则只影响网页展示层，过滤、去重、排序和身份判断仍按当前已确认的 `songs.name` 与 `albums.name` 规则执行。
- 网页明细表范围规则：标准网页和 large-graph 网页底部的关系明细表与歌曲明细表必须以当前绘图区的 `buildGraph()` 结果为上限，目标歌手、粉丝量范围、最小歌曲数、隐藏叶节点、只看目标歌手等绘图筛选都必须同步作用到明细表；这些筛选只决定歌曲条目本身是否出现在歌曲明细表中，一旦歌曲出现，作词、作曲、演唱、专辑等列必须显示该歌曲完整内容，不得按当前可见节点或选中节点把制作人/演唱者过滤为空；歌曲明细必须同时包含当前可见边支撑到的歌曲和当前可见节点作为演唱者参与的歌曲，即使这会让某些无可见边的孤岛节点仍在明细表中显示自己的歌曲；明细表搜索和选中节点只能在当前图范围内继续缩小歌曲条目，不得重新扩大到原始全量歌曲集合。
- 隐藏绘图性能规则：标准网页和 large-graph 网页开启“隐藏绘图”后，作词/作曲分开、显示名字、粒子效果等只影响绘图表达的开关不得触发图谱重绘、`buildGraph()` 大表重算或明细表重写；只有目标歌手、粉丝量范围、最小歌曲数、隐藏叶节点、只看目标歌手、节点选择、明细表搜索等会改变歌曲条目集合或表格视图的操作才刷新明细表。
- 顶栏筛选重置规则：标准网页和 large-graph 网页顶栏右侧第一行开关区最左侧必须是“清除筛选”按钮，第二项必须是“隐藏绘图”开关；“清除筛选”不是恢复默认值，而是进入无筛选状态：粉丝量范围为 0 到不限、目标歌手全选、隐藏叶节点关闭、仅显示目标歌手关闭、最小歌曲数为 1、显示名字关闭、粒子效果关闭、作词/作曲分开关闭，并清除当前图表选中和明细表搜索；用户从关闭切换到开启“隐藏绘图”时必须向下弹出是否清空筛选的确认框，选项为“否”和“是”。
- 已请求过步骤四 `--all` 且需要根据当前已落盘主页歌曲 Tab raw 继续测试时，一键入口为 `python -m music_metadata_graph.pipelines.run_from_song_tabs` 或 `mr-run-from-song-tabs`；该入口等价于完整编排 `--continue-from 5`，从五前置开始，但只要求步骤四 `--all` 目标范围内至少已有可处理的主页歌曲 Tab raw，不要求步骤四目标歌手全部落盘。
- QQ 音乐单对象请求优化规则：当接口业务语义仍是一个对象一个 request，但 `qqmusic-api-python` 能构造多个 request 描述符时，优先使用 `Client.gather()` 按批合包请求；批大小使用脚本顶部常量并提供命令行参数覆盖；合包不得改变一个对象一个 raw JSON 文件的落盘和追溯方式，也不得绕过低频请求边界。第 2 步缺失粉丝量补齐、第 6、7、11、12 步这类单对象批量 raw 请求必须按批渐进落盘：每批成功响应立即写入对应 raw JSON；批次整体失败时降级为单个请求逐个尝试；仍有失败对象时，应先保留已成功结果，再以非零退出提示后续重跑补齐。
- 长流程断点续跑规则：所有外部请求型步骤必须先检查本地 raw 缓存或 manifest，已存在且可 UTF-8 JSON 解析的结果默认视为 `cache_hit` 并跳过请求；只有显式 `--force` 才允许重抓并覆盖对应缓存。坏 JSON 或缺失文件视为缓存未命中，可以重抓；重跑时不得依赖旧 CSV 作为断点输入，CSV 只能作为当次人工检查视图重写。第 4 步歌曲 Tab 按歌手分页缓存，第 5、6、7、8 步在第四步未全量完成时只能扫描第四步当前目标范围与已落盘 raw 的交集继续处理。
- 及时落盘规则：凡是可恢复的长请求步骤，成功拿到一个对象或一个批次的响应后必须立即写入对应 raw JSON、CSV 或 manifest，不得等全步骤结束才统一落盘。`quick_search` 补 MID 每处理一个姓名或拆分姓名后必须重写补 MID CSV；头像缓存每完成一个下载结果必须更新 manifest；头像图集重建必须先写临时目录并完成校验，再替换正式输出目录，避免半成品覆盖可用产物。
- 异步请求调度规则：外部请求不应在请求启动间隔之外额外串行等待下载完成；能提前构造 request 或下载任务的步骤，应按限速间隔启动请求并异步等待响应，使下载等待时间与后续请求启动重叠。`Client.gather()` 可用时优先用它合包并发；`quick_search` 这类单请求接口应为每个唯一搜索名创建异步任务并按完成顺序处理结果；同一歌手歌曲 Tab、完整歌手列表这类分页依赖上一页 `HasMore` 或 `total` 的流程，只能在已知页范围或不同歌手之间并发，不得提前请求未知页。
- 长步骤日志规则：完整流程和子脚本必须接入 `run_with_log`，运行开始打印 `run_id`、`run_log` 和开始时间，退出时打印状态。长请求步骤必须打印可判断进度的结构化摘要和 `[当前/总数]` 进度；新请求、失败、最后一项必须及时打印，纯缓存命中或数据库命中的大量重复项可按固定间隔抽样打印但必须打印最后一项。失败日志必须包含对象标识、状态、原因和目标保存路径；流程总入口每步必须打印 precheck、实际命令和 postcheck 摘要。
- 合理跳过规则：缓存命中、数据库已唯一命中、头像图集 fingerprint 与当前输入一致、头像下载被 `--skip-avatar-download` 或 `--max-avatar-downloads` 限制跳过，都应在日志或最终摘要中明确计数和原因。跳过不得伪装成成功抓取；摘要字段应区分 `fetched`、`cache_hits`、`db_matches`、`skipped`、`failed` 等状态，便于用户判断到底做了哪些实际请求。
- 缓存与仓库：原始抓取缓存、数据库文件、大量图片和生成图谱默认不提交到 Git；仓库只提交代码、少量脱敏样例、schema、文档和测试。
- 凭据管理：cookie、账号态、代理、API key 等只能通过本地 `.env` 或用户本机配置读取，示例文件必须使用占位值。
- 开源表述：README 和文档应明确项目用于个人技术研究和元数据关系分析，不保证第三方接口稳定性，不承诺数据完整准确，不鼓励大规模抓取。
- 验证门槛：数据 adapter 至少使用少量固定歌曲或歌手样例做解析验证；涉及数据模型变更时同步更新样例输出或测试。
- 中文与编码：读取或写入中文文档、日志、报告时必须显式使用 UTF-8；在 PowerShell 中读取中文文件必须加 `-Encoding UTF8`，Python 命令输出中文时必须配置 `sys.stdout.reconfigure(encoding="utf-8")` 或等效方式；不得根据乱码终端输出判断文件内容。
- Markdown 报告生成：生成 Markdown 表格报告时必须转义单元格内的 `|`，统一换行并避免表格内部空行；生成后必须回读文件，检查 UTF-8 可读、无 U+FFFD 替换字符、表格前有空行、分隔行有效、所有表格行列数一致。未完成这些检查不得向用户声明报告可用。
- 文本异常自动扫描与修复规则：每次开始任务读取 `AGENTS.md`、`develop_log.md`、`README.md`，或修改任意 `.md`、`.py` 文本文件后，必须运行 `python scripts/repair_text_anomalies.py` 扫描核心文档；涉及多份文本、生成脚本、报告、日志或怀疑全仓异常时运行 `python scripts/repair_text_anomalies.py --all`。自定义文本修复只负责文件损坏和 Markdown 结构问题，不负责定义 Python 正常格式。异常定义包括 UTF-8 替换字符、非换行隐藏控制字符、`CRCRLF` 换行、总行数相对非空行异常膨胀、Markdown fenced code block 外连续空行超过 1 个；对核心 Markdown 文档还包括结构性空行错误，即 `###` 等标题后紧跟 `-` 条目时中间不应空行，连续 `-` 条目之间不应空行。Python 文件的正常格式统一交给 `black`，不得在 `repair_text_anomalies.py` 中重新规定 import、装饰器、函数体、括号内部空行等格式风格；Python 自定义扫描只保留损坏层面的检查：UTF-8 可读、无替换字符、无非换行隐藏控制字符、无 `CRCRLF`、无异常空行膨胀，并用 AST 确认可解析。发现异常时优先运行 `python scripts/repair_text_anomalies.py --fix` 做保守修复：Markdown 代码块内部内容和空行原样保留，核心 Markdown 中标题到列表、列表到列表之间的异常空行删除，其他块级结构之间的必要单个空行保留；Python 只修复换行、编码和异常膨胀这类 black 不负责的问题，不按自定义规则整理正常格式。Python 格式修复顺序为：先运行文本异常修复，随后运行 `python -m black music_metadata_graph scripts tests` 或针对本次修改的 Python 文件运行 black，最后再运行文本异常扫描确认没有 `CRCRLF` 等损坏。所有脚本化写回文本文件时必须避免 Windows 文本模式二次换行转换，不得把已含 `\n` 的字符串再用 `newline="\r\n"` 写入；应使用字节级写入统一 CRLF，或使用明确不会产生 `CRCRLF` 的写入方式。修复后必须再次运行 `python scripts/repair_text_anomalies.py --all` 确认异常消失，并把异常范围、修复方式、black 执行范围和验证结果记录到 `develop_log.md`。保留 `scripts/repair_markdown_anomalies.py` 仅作为兼容入口，新规则以 `repair_text_anomalies.py` 为准。不得为了压缩行数删除 Markdown 必要的单个空行、代码块内部空行、表格所需结构空行，或用自定义 Python 空行规则替代 black。
- 临时脚本约束：涉及中文常量、Markdown 表格、排序或报告生成的逻辑，优先写入仓库脚本或使用 UTF-8 明确的 Python 执行；避免在 PowerShell here-string 中直接写中文常量后生成正式产物。
- 相似歌手递归工具规则：`music_metadata_graph.tools.collect_jay_chou_similar_singers` 是独立工具脚本，不并入完整 pipeline。该脚本默认首轮不再从周杰伦单点开始，而是读取第一步完整歌手列表 raw 目录 `data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all/`，将 `singerlist[].area_id in (0, 1)` 且 MID 非空的歌手去重后全部作为第 0 层已发现种子和首轮 frontier；默认 raw 输出目录为 `data/raw/qqmusic/singer_similar/area_0_1_singer_list_seed/`，validation 输出目录为 `data/processed/validation/singer_similar_area_0_1_seed/`。合包请求上限仍为 20，每个被请求 MID 仍必须一个 raw JSON，CSV 只可作为人工查看产物，不得作为断点或正式输入。若显式指定旧 `--raw-dir`，脚本会按该目录已有 manifest/frontier 断点续跑，不会自动迁移旧周杰伦根目录。
- 报告链接验收：向用户提供生成产物时，必须先确认文件存在和大小非零；最终回复中的本地文件链接必须使用正斜杠绝对路径并手动检查渲染格式，不得使用会被 Markdown 破坏的 Windows 反斜杠链接。
