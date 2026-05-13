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

### 初始化 AGENTS 项目协作文档

- 根据当前项目目标，将 `AGENTS.md` 从通用模板补充为音乐人合作关系图谱项目规则。
- 明确项目定位为面向个人技术研究和学习的音乐平台元数据采集、标准化、图谱分析和可视化工具。
- 明确第一阶段数据源优先级：QQ 音乐非官方接口作为主源，网易云音乐作为补充和交叉校验，酷我、酷狗作为缺失字段兜底来源。
- 明确推荐运行环境为独立 Conda 环境 `music-graph` 和 Python 3.12，不使用 base 环境承载项目依赖。
- 明确项目边界：不做音乐播放或下载工具，不提交大量抓取数据、歌词、头像、cookie、token 或账号信息到仓库。
- 补充内部数据模型原则、来源可追溯、身份消歧、请求策略、缓存与仓库、凭据管理、开源表述和 adapter 验证门槛。

### 安装项目指定 Conda 环境依赖

- 按用户要求未向 base 环境或 Python 虚拟环境安装依赖，使用项目指定 Conda 环境执行依赖安装。
- 安装了第一阶段数据采集、标准化、分析和可视化所需依赖：`qqmusic-api-python`、`pandas`、`pydantic`、`httpx`、`tenacity`、`python-dotenv`、`duckdb`、`networkx`、`pyvis`。
- 初次直接使用指定解释器安装时，因沙箱网络权限和环境目录写入权限受限失败，未完成依赖安装。
- 随后通过指定 Conda 环境执行 pip 安装并显式禁用 user site 安装，避免依赖落入 base 或用户级 site-packages。
- 验证对象为目标 Conda 环境的 pip 路径、`qqmusic-api-python` 安装位置和关键依赖导入能力。
- 验证结果显示 pip 和 `qqmusic-api-python` 均位于项目指定 Conda 环境的 `Lib/site-packages`，关键包 `qqmusic_api`、`pandas`、`pydantic`、`httpx`、`duckdb`、`networkx`、`pyvis` 可正常导入。

### 纠正依赖安装后漏记开发日志

- 用户指出依赖安装完成后没有记录开发日志，并询问 `AGENTS.md` 是否规定记录时机。
- 复核 `AGENTS.md` 后确认项目规则要求每次实质性分析、方案、实现、验证、事故或阶段回顾后按 `develop_log.md` 顶部规则追加开发日志。
- 复核 `develop_log.md` 后确认日志规则要求环境异常、协作规则纠正和验证结果需要记录事实、影响范围和修复方式。
- 已将依赖安装、验证结果和本次漏记纠正追加到当天开发日志。

### 设计音乐人关系图谱初版方案

- 用户要求设计初版方案，当前仓库除协作说明和开发日志外尚未建立源码、配置、样例数据或用户文档。
- 需求理解为先完成一个可本地运行、可验证、范围受控的最小闭环，而不是一次性抓取大量平台数据或建设完整产品。
- 目标效果为用户可以通过命令输入少量固定 QQ 音乐歌曲或歌手样例，生成标准化的歌曲、音乐人、职能关系边和来源记录，并输出一个本地 HTML 关系图页面。
- 用户验收路径为查看命令执行结果、样例输出文件、关系边明细和 HTML 图谱页面，确认节点包含音乐人姓名和可用头像 URL，边能区分演唱、作词、作曲等职能。
- 实现方案分为项目骨架、标准模型、QQ 音乐 adapter、采集缓存、持久化、图谱构建、HTML 可视化、样例命令和测试验证几个部分。
- 数据边界保持在元数据范围内，不采集音频文件，不实现播放或下载，不提交大量原始缓存、数据库、头像文件、cookie、token 或账号信息。
- 风险边界包括非官方接口稳定性、作词作曲字段可能缺失或只能从非结构化文本解析、同名音乐人消歧不完整、头像链接可能失效、初版图谱规模不适合大批量数据。
- 本轮不做范围为不做 GUI 应用、Web 后端、多平台完整聚合、自动化大规模抓取、复杂身份合并、歌词全文分析、社区发现算法和商业级数据服务。

### 调整初版方案为网页化打开体验

- 用户补充希望初版尽量不要依赖命令启动，而是包装成可直接使用的形式。
- 用户提出关系边需要两个开关：一个控制有向边或无向边，一个控制是否区分作词、作曲等职能类型。
- 用户对有向边的设想是能够表现 A 给 B 作词曲与 B 给 A 作词曲的方向差异，但具体视觉表达仍需设计。
- 用户询问能否做成带前后端的网页，并实现从 GitHub 打开就是网页，而不是必须克隆仓库、配置环境后运行。
- 已识别方案边界：GitHub Pages 可以承载静态前端和静态 JSON 数据，但不能直接承载常驻 Python 后端；如果需要真实后端采集能力，需要额外部署服务或使用 GitHub Actions 预生成静态数据。
- 调整后的目标效果为优先建设一个 GitHub Pages 可打开的静态网页初版，内置少量样例数据、关系边开关和图谱交互；采集与数据更新先作为离线生成流程或后续部署后端处理。
- 风险边界包括浏览器端直接调用第三方非官方接口可能遇到跨域、稳定性、限流和凭据问题，初版不应把 cookie、token 或账号态放入前端。
- 本轮不做范围调整为不承诺 GitHub Pages 同时提供后端采集服务，不做浏览器端绕过平台限制，不做需要私密凭据的在线采集。

### 收敛第一阶段为无服务器静态网页计划

- 用户明确没有服务器，因此第一阶段不做任何需要常驻后端服务的设计。
- 第一阶段边界收敛为 GitHub Pages 静态网页加静态 JSON 数据，网页打开即可查看和交互，不要求访问者克隆仓库或配置 Python 环境。
- 数据采集和标准化仍作为开发者本地或后续 GitHub Actions 离线生成流程，不作为网页实时功能。
- 第一阶段计划需要进一步拆分为数据样例、图谱数据协议、静态前端、关系边模式、GitHub Pages 发布、离线数据生成工具和验证验收几个独立步骤。
- 已确认初版关键交互仍为两个开关：有向边或无向边、区分职能或合并职能。

### 根据真实 QQ 音乐 API 调整第一阶段计划

- 用户纠正不希望先按手写样例拆分前两步，而是直接用 API 开发，通过小请求查看真实数据后再设计初版。
- 使用项目指定 Conda 环境检查 `qqmusic-api-python`，确认可用入口包括 `Client().search.search_by_type()`、`Client().song.get_detail()` 和 `Client().song.get_producer()`。
- 初次在沙箱内执行真实接口请求时因网络权限受限失败，随后按权限规则申请放行后完成小范围请求。
- 搜索接口返回 `SearchByTypeResponse`，包含歌曲、歌手、专辑等字段；歌曲结果包含 `id`、`mid`、`title`、`singer`、`album`、`time_public` 等可用于建立歌曲和演唱者基础信息。
- 歌曲详情接口返回 `GetSongDetailResponse`，包含发行公司、流派、语言、发行时间、简介和 `track` 明细，可作为歌曲元数据补充。
- 制作人员接口返回 `GetProducerResponse`，其中 `data` 按“演唱、作词、作曲、编曲、制作人”等职能分组，每个 producer 包含姓名、头像 URL、`singer_mid` 和职能类型，适合作为关系边的主要来源。
- 已发现搜索关键词可能返回与预期不一致的第一结果，因此第一阶段不能默认取搜索第一条，需要提供结果确认或按明确歌曲 `mid/id` 采集。
- 已发现部分歌曲调用制作人员接口时可能因为上游字段为空触发模型校验异常，adapter 需要把该类情况记录为制作人员缺失或接口解析失败，而不是中断整个流程。
- 第一阶段计划调整为 API 探针、QQ 音乐 adapter、标准化导出、静态网页图谱和 GitHub Pages 发布，不再以手写样例数据作为前置核心步骤。

### 纠正 QQ 音乐搜索结果判断

- 用户追问“搜索不能默认取第一条”的含义，并询问如何发现第一条不符合预期以及如果用 ID 采集如何知道歌曲 ID。
- 复核后确认前一次异常搜索结果并非 QQ 音乐按“稻香”真实返回错误，而是通过 PowerShell 管道执行临时 Python 脚本时中文关键词被传成问号，导致请求关键词失真。
- 使用 Unicode 转义重新请求“稻香”和“周杰伦 稻香”，结果显示第一条均为周杰伦《稻香》，其中歌曲 `id` 为 `449205`、`mid` 为 `003aAYrm3GE0Ac`。
- 已纠正方案判断：初版可以支持按歌名搜索采集，但产品流程不应完全静默依赖第一条；更合适的方式是在搜索结果页展示候选歌曲，让用户确认后系统自动使用对应 `id/mid` 继续采集。
- 仍保留风险事实：搜索结果中可能出现童声版、Demo、Live、翻唱、Remix 等同名版本，因此当关键词不够精确或需要避免版本误选时，需要展示歌名、歌手、专辑、发行时间和 `id/mid` 供确认。
- 事故原因是临时验证脚本的输入编码不可靠，后续涉及中文关键词的验证应使用 UTF-8 文件、Unicode 转义或确认输出中的 `repr(keyword)`，避免把本地编码问题误判为平台接口行为。

### 纠正第一阶段数据获取主流程

- 用户指出搜索单首歌只是数据获取的一步，不应设计成网页里的主要流程。
- 用户明确期望的数据生产流程是先获取音乐人列表，再对每个音乐人获取单曲，过滤 Live 版本，去重后对每个单曲获取作词、作曲人，最终得到 `{歌名，音乐人，作词，作曲，其他必要信息}` 形式的数据。
- 复核 `qqmusic-api-python` 接口后确认 `SingerApi.get_songs_list(mid)` 可按音乐人获取歌曲列表，`SongApi.get_producer(value)` 可按歌曲 `id/mid` 获取演唱、作词、作曲、编曲、制作人等职能分组。
- 第一阶段主流程调整为“种子音乐人列表 -> 歌手单曲列表 -> Live/版本过滤 -> 歌曲去重 -> 制作人员抓取 -> 标准行数据 -> 静态图谱 JSON -> GitHub Pages 网页”。
- 搜索接口在第一阶段降级为辅助能力：用于把用户给出的音乐人姓名解析成候选音乐人 `mid`，或在必要时人工查找缺失歌曲，不作为网页交互入口。
- 网页职责收敛为读取已生成数据并进行关系图展示、筛选和边模式切换，不承担在线搜索和在线采集。

### 调整冷启动来源为 QQ 音乐榜单

- 用户指出第一步仍不成立，因为一开始不知道任何 QQ 音乐中的音乐人或歌曲 `id/mid`。
- 用户建议通过获取排行榜的形式先取得一批音乐人。
- 复核 `qqmusic-api-python` 后确认 `TopApi.get_category()` 可获取榜单分类，`TopApi.get_detail(top_id, num, page)` 可获取具体榜单歌曲。
- 小范围请求榜单分类显示榜单项包含前几首歌曲，并提供歌曲 `id`、歌曲名、`singer_name`、`singer_mid`、专辑 `album_mid` 和封面 URL。
- 小范围请求热歌榜详情显示 `songs` 列表包含完整歌曲 `id/mid`、歌名、演唱者列表、专辑信息、发行时间等字段，可作为无已知 ID 状态下的冷启动入口。
- 第一阶段主流程进一步调整为“榜单分类/榜单详情 -> 榜单歌曲 -> 榜单音乐人 -> 音乐人单曲列表 -> 过滤与去重 -> 制作人员抓取 -> 标准行数据 -> 图谱 JSON -> 静态网页”。
- 初版可以默认选择少数榜单作为冷启动来源，例如热歌榜、新歌榜或飙升榜，并限制每个榜单、每个音乐人的采集数量，避免大规模请求。

### 纠正冷启动来源为歌手列表

- 用户指出需要的是歌手榜单，不是歌曲榜单；第一步应该先获取一批音乐人，而不是从歌曲获得音乐人。
- 复核 `qqmusic-api-python` 后确认 `SingerApi.get_singer_list()` 和 `SingerApi.get_singer_list_index()` 可直接获取歌手列表。
- 歌手列表接口支持按地区、性别、流派和首字母索引过滤，相关枚举包括 `AreaType`、`SexType`、`GenreType` 和 `IndexType`。
- 小范围请求 `get_singer_list()` 显示返回 `hotlist` 和 `singerlist`，其中热门歌手包含周杰伦、林俊杰、陈奕迅等，以及 `id`、`mid`、姓名、别名、拼音、关注数等字段。
- 小范围请求 `get_singer_list_index()` 显示返回分页歌手列表、总数和头像 URL，样例中每个歌手包含 `singer_pic`，更适合作为初版音乐人节点头像来源。
- 第一阶段主流程修正为“歌手列表/热门歌手 -> 音乐人 -> 音乐人单曲列表 -> 过滤与去重 -> 制作人员抓取 -> 标准行数据 -> 图谱 JSON -> 静态网页”。
- 歌曲榜单接口可保留为后续补充热门歌曲覆盖的辅助来源，但不作为第一阶段冷启动主入口。

### 实现热门歌手单曲采集脚本

- 用户要求开始写代码，先实现获取前 50 个热门歌手、每个歌手获取全部单曲、过滤 Live、Demo、Remix 等版本，并停在这里查看保存的数据形态。
- 新增 `.gitignore`，排除 `data/raw/`、`data/processed/`、`.env`、`__pycache__` 和 `*.pyc`，避免提交原始接口缓存和生成数据。
- 新增 `pyproject.toml`，记录项目包名、Python 版本要求和当前脚本依赖。
- 新增 `musician_relationship/collect_singer_songs.py`，实现从 `SingerApi.get_singer_list_index()` 获取热门歌手、按歌手 `mid` 分页调用 `SingerApi.get_songs_list()` 获取单曲、版本过滤、按 `song_mid/song_id` 去重，并输出 JSON 与 CSV。
- 采集脚本默认参数为前 50 个歌手、每页 30 首歌、不限制歌手分页页数；提供 `--max-pages-per-singer` 用于小样本验证。
- 原始响应缓存保存到 `data/raw/qqmusic/`，处理后结果保存到 `data/processed/`，包括 `singers.json`、`songs_all.json`、`songs_kept.json`、`songs_filtered.json`、对应 CSV 和 `singer_song_snapshot.json`。
- 初次小样本验证发现 QQ 音乐歌手单曲接口即使传入 `page_size=20` 仍返回 30 首，已将默认页大小改为 30，并在缓存文件名中加入 page size，避免分页 offset 与缓存混用风险。
- 初次过滤验证发现专辑名 `Live For Today` 会被简单 `Live` 关键词误判为现场版本，已调整过滤逻辑：歌名、标题和副标题检查 `Live/Demo/Remix` 等关键词，专辑名只检查“演唱会、现场、巡回、concert”等更明确关键词。
- 根据用户偏好，新增和修改的文本文件已统一为 CRLF 行尾。

### 验证热门歌手单曲采集脚本

- 语法验证对象为 `musician_relationship/collect_singer_songs.py`，执行方式为项目指定 Conda 解释器运行 `py_compile`，结果未报语法错误。
- 小样本接口验证对象为前 3 个热门歌手且每个歌手仅取 1 页，执行命令为 `python -m musician_relationship.collect_singer_songs --singer-limit 3 --page-size 30 --max-pages-per-singer 1 --processed-dir data/processed_smoke`。
- 小样本采集结果显示获取到周杰伦、林俊杰、陈奕迅 3 位歌手，每位歌手第一页返回 30 首单曲，共 90 条歌曲行，去重后仍为 90 条。
- 修正过滤逻辑后，小样本结果为保留 90 条、过滤 0 条；观察到样本第一页没有明显 Live、Demo、Remix 标题版本，因此该结果符合当前样本。
- 离线过滤规则验证显示 `晴天 (Live)` 返回 `title_version_keyword:Live`，`稻香 Demo` 返回 `title_version_keyword:Demo`，专辑名 `Live For Today` 不再误过滤，专辑名包含“演唱会”时返回 `album_version_keyword:演唱会`。
- 保存数据抽查显示 `songs_kept.json` 中每首歌包含 `id`、`mid`、歌名、标题、专辑、发行时间、演唱者列表、来源歌手、过滤状态和过滤原因，可作为下一步获取作词作曲信息的输入。
- 当前未执行前 50 个歌手的全量单曲采集；根据小样本返回的总数，热门歌手全量单曲可能产生较多分页请求，适合在确认当前数据形态后再执行。
- `git status --short` 因本机 Git safe.directory 所有权检查失败未能执行，未进行提交相关操作。

### 检查初步过滤后歌曲重名情况

- 用户要求检查初步过滤后的歌曲是否仍有重名或近似重名。
- 检查对象为最新小样本输出 `data/processed_smoke/songs_kept.json`，该文件包含前 3 个热门歌手各 1 页采集后保留的 90 首歌曲。
- 检查方式包括按原始标题精确分组、按去空白和常见分隔符后的标题分组、按去括号和 Live、Demo、Remix 等版本词后的标题分组，以及相似度阈值 0.92 的模糊标题两两比较。
- 检查结果显示当前 90 首小样本中没有精确重名组、没有基础规范化重名组、没有去版本词后的近似重名组，也没有相似度大于等于 0.92 的标题对。
- 额外扫描版本关键词残留发现 2 条歌曲的专辑名包含 `Live For Today`：陈奕迅《十面埋伏》和《岁月如歌》；当前规则没有过滤它们，因为该专辑名不是现场版本含义，符合前一次误过滤修正。
- 当前结论只覆盖小样本，不代表前 50 个热门歌手全量单曲；全量采集后需要再次执行同类检查。

### 采集周杰伦全量单曲并观察过滤结果

- 用户要求跑一个歌手的全部单曲，指定周杰伦，并查看初步筛除结果。
- 执行命令为 `python -m musician_relationship.collect_singer_songs --singer-limit 1 --page-size 30 --processed-dir data/processed_jay`，因热门歌手列表第一位为周杰伦，该命令只采集周杰伦。
- 采集结果显示周杰伦单曲接口共返回 1012 条歌曲行，分页 34 页，其中前 33 页每页 30 条，第 34 页 22 条。
- 去重后仍为 1012 条；当前过滤规则保留 410 条、过滤 602 条。
- 过滤原因分布为：`title_version_keyword:Live` 239 条，`title_version_keyword:版伴奏` 173 条，`title_version_keyword:演唱会` 65 条，`title_version_keyword:伴奏` 51 条，`title_version_keyword:现场` 31 条，`title_version_keyword:纯音乐` 16 条，`title_version_keyword:Demo` 11 条，`title_version_keyword:Remix` 8 条，`title_version_keyword:片段` 7 条，`album_version_keyword:巡回` 1 条。
- 抽查过滤样例显示大量过滤项为标题包含 `(Live)` 的现场版本，以及 `KTV版伴奏`、`原版伴奏`、`升调版伴奏` 等伴奏版本，符合当前过滤目标。
- 发现一条可能误杀：周杰伦《周大侠》标题不是 Live 版本，但因专辑名 `2007世界巡回演唱会` 命中 `album_version_keyword:巡回` 被过滤；后续应考虑去掉专辑名中的“巡回”触发，仅保留更明确的“演唱会、现场、concert”等专辑级过滤词。
- 本次运行输出保存到 `data/processed_jay/`，包括全量歌曲、保留歌曲、过滤歌曲和摘要快照。

### 生成并修正周杰伦过滤清单报告

- 用户要求列出完整过滤样例，因此基于 `data/processed_jay/songs_filtered.json` 生成 Markdown 报告 `data/processed_jay/songs_filtered_report.md`。
- 报告按过滤原因分组列出 602 条过滤歌曲，字段包括歌名、标题、歌手、专辑、`song_id` 和 `song_mid`。
- 用户指出报告中出现大量问号，复核确认报告文件中的中文标题和表头被写成问号，但歌曲数据字段本身仍保持中文，原始 JSON 未损坏。
- 事故原因是通过 PowerShell here-string 传入临时 Python 脚本时，脚本中的中文常量被当前控制台编码替换为问号。
- 已使用 Unicode 码点生成中文标题和表头，重新写入 `songs_filtered_report.md`，复核结果显示报告中问号数量为 0。
- 后续涉及临时 Python 脚本中的中文常量时，应使用 UTF-8 源文件、Unicode 转义或码点生成，避免通过 PowerShell here-string 直接写中文。

### 调整歌曲过滤顺序和专辑过滤规则

- 用户要求修改流程：先进行初过滤，再去重；关键词过滤前先根据专辑过滤，去掉专辑为空的歌曲；关键词中去掉“巡回”。
- 已修改 `musician_relationship/collect_singer_songs.py`：每首歌先生成紧凑记录，再按空专辑过滤，然后按版本关键词过滤，最后只对保留候选执行去重。
- 已从专辑级版本关键词中移除“巡回”，避免《周大侠》因专辑名 `2007世界巡回演唱会` 被误过滤。
- `songs_all.json` 现在保存过滤前全量行，`songs_kept.json` 保存先过滤再去重后的保留结果，`songs_filtered.json` 保存过滤掉的行。
- 摘要计数字段新增 `songs_after_filter_before_dedupe`，用于区分过滤后、去重前的数据规模。
- 语法验证对象为采集脚本，执行 `py_compile` 未报错。
- 离线过滤检查确认空专辑返回 `empty_album`，标题包含 `Live` 返回标题版本过滤原因，`周大侠` 专辑名含“巡回”不再触发版本过滤。

### 复跑周杰伦全量单曲新过滤流程

- 使用新流程复跑周杰伦全量单曲，输出目录为 `data/processed_jay_refiltered/`。
- 采集仍读取周杰伦 1012 条歌曲行，因原始响应缓存已存在，本次复跑主要验证处理流程变化。
- 新流程结果显示过滤前 1012 条，过滤后去重前 250 条，去重后保留 250 条，过滤 762 条。
- 过滤原因分布为：`empty_album` 591 条，`title_version_keyword:Live` 161 条，`title_version_keyword:Demo` 3 条，`title_version_keyword:Remix` 3 条，`title_version_keyword:现场` 2 条，`title_version_keyword:伴奏` 2 条。
- 抽查确认《周大侠》在新流程中保留，`filter_reason` 为 `null`。
- 已生成新的完整过滤报告 `data/processed_jay_refiltered/songs_filtered_report.md`，报告问号数量复核为 0。

### 调整关键词过滤优先级

- 用户指出关键词过滤规则没有固定顺序，名称中包含多个关键词的歌曲会按合并正则的匹配位置返回过滤原因，而不是按预期关键词顺序返回。
- 已将版本关键词过滤改为显式按 `TITLE_VERSION_KEYWORDS` 列表顺序检查，确保过滤原因由规则优先级决定。
- 用户进一步指出 `版伴奏` 不需要单独作为原因，普通 `伴奏` 可以覆盖，因此已删除 `版伴奏` 和 `伴奏版` 专门关键词。
- 关键词过滤现在只检查歌名、标题和副标题，不再检查专辑名；专辑名过滤仅用于前置的空专辑过滤。
- 语法验证对象为采集脚本，执行 `py_compile` 未报错。
- 离线验证显示“演唱会现场 Live 伴奏”按优先级返回 `title_version_keyword:live`，`KTV版伴奏` 和普通伴奏标题均返回 `title_version_keyword:伴奏`，仅专辑名含“巡回演唱会”的《周大侠》不再触发关键词过滤。
- 使用新规则复跑周杰伦处理结果到 `data/processed_jay_priority_filter/`，结果仍为过滤前 1012 条、过滤后去重前 250 条、去重后保留 250 条、过滤 762 条。
- 新过滤原因分布为：`empty_album` 591 条，`title_version_keyword:live` 161 条，`title_version_keyword:demo` 3 条，`title_version_keyword:remix` 3 条，`title_version_keyword:现场` 2 条，`title_version_keyword:伴奏` 2 条。
- 抽查确认《周大侠》仍被保留，已生成新报告 `data/processed_jay_priority_filter/songs_filtered_report.md`，报告问号数量为 0。

### 评估以专辑为主的采集流程

- 用户提出当前通过歌手歌曲列表采集后仍有较多噪声，询问是否可以改为先取歌手专辑列表，再按专辑取歌曲，以减少空专辑和非官方噪声。
- 复核 `SongApi.get_other_version(value)` 的真实返回后确认，该接口返回的是与目标歌曲相关的其他版本列表，返回类型为 `GetOtherVersionResponse`，字段为 `data`，其中元素是 `Song` 对象。
- 实际样例显示 `get_other_version('003aAPj81VWrbL')` 返回 `富士山下` 的其他版本，如 `富士山下 (深情版)`、`富士山下 (纯净女声版)`、`富士山下 (Live)` 等，说明该接口更适合做版本识别和版本补充，而不是原唱真值字段。
- 复核 `SingerApi.get_album_list(mid)` 后确认歌手专辑列表返回 `SingerAlbumListResponse`，字段包括 `singer_mid`、`total` 和 `album_list`；周杰伦样例返回 43 个专辑/单曲/演唱会/EP 等条目，并带有 `album_type`、`time_public`、`singer_name`。
- 复核 `AlbumApi.get_song(album_id_or_mid)` 后确认专辑歌曲列表返回 `GetAlbumSongResponse`，字段包括 `album_mid`、`total_num` 和 `song_list`，可直接按专辑取歌，无需再依赖歌手歌曲列表中的空专辑条目。
- 评估结果认为：以“歌手 -> 专辑 -> 专辑歌曲”作为主流程是可行的，并且理论上能减少 `empty_album` 这类噪声，因为专辑歌曲天然带专辑上下文。
- 同时保留风险：歌手专辑列表本身会包含录音室专辑、EP、Single、演唱会、原声带、合辑等多种类型，需要在专辑层做白名单或黑名单筛选，否则仍会引入现场、合辑和翻唱条目。
- 另一个风险是单曲、合作曲和跨歌手参与曲可能不会完全被专辑主流程覆盖，后续可能仍需要把歌手歌曲列表或搜索接口作为补充源，而不是完全删除。

### 修正保留歌曲 Markdown 表格报告

- 用户要求查看过滤后保留歌曲的全量 Markdown 清单，并指出生成的 Markdown 表格多次渲染失败且出现问号。
- 复核发现第一次失败原因是报告表格行之间被写入空行，Markdown 渲染器将表格拆断；后续又发现 Windows 文本模式写入 `\r\n` 时被二次转换为 `\r\n\r\n`，继续产生空行。
- 复核还发现 `Six Degrees (Slowed|Reverb)` 等字段中包含未转义竖线，会导致 Markdown 表格列数错乱。
- 已将 `data/processed_jay_priority_filter/songs_kept_alpha_report.md` 重新生成为单表格式，并对所有单元格内容中的 `|` 执行转义。
- 为避免 PowerShell 临时脚本中文常量再次被本机编码污染，报告标题和列名改为 ASCII，中文只来自 JSON 数据本身。
- 验证结果显示新版报告问号数量为 0，并且所有表格行的未转义竖线数量符合 7 列表格结构。

### 修正保留歌曲拼音排序报告

- 用户指出此前“首字母通排”并未真正按拼音排序，只是按英文、数字、Unicode 中文顺序排列，导致中文歌曲没有和英文按拼音混排。
- 复核确认当前环境未安装 `pypinyin`，因此此前无法进行真实拼音排序。
- 已将 `pypinyin` 加入 `pyproject.toml` 依赖，并安装到项目指定 Conda 环境。
- 使用 `pypinyin.lazy_pinyin()` 为歌曲标题生成无声调拼音排序键，重新生成 `data/processed_jay_priority_filter/songs_kept_pinyin_report.md`。
- 报告列包含 `Initial`、`Sort key`、`Song`、`Title`、`Release`、`Source singers`、`Album`、`song_id` 和 `song_mid`，用于检查排序依据。
- 已将同样内容同步覆盖到 `data/processed_jay_priority_filter/songs_kept_alpha_report.md`，避免继续打开旧错误报告。
- 验证结果显示两个报告的问号数量均为 0，粗略表格竖线检查均未发现异常行。

### 再次修正拼音排序报告表格渲染

- 用户指出拼音排序 Markdown 报告仍然渲染失败，并要求生成后先检查。
- 复核确认此前检查只覆盖问号和竖线列数，遗漏了 Markdown 表格前必须与前置段落或列表分隔的结构条件。
- 已重新生成 `songs_kept_pinyin_report.md` 和 `songs_kept_alpha_report.md`，将元信息从列表项改为普通段落，并在表格前保留空行。
- 已使用 CRLF 字节写入文件，避免 Windows 文本模式把换行二次转换为额外空行。
- 新增结构验证：确认表格前一行为空行、表格分隔行有效、表格内部无空行、表头和 250 条数据行列数一致。
- 验证结果显示问号数量为 0，表格起始行为第 7 行，表格行数为 252 行，结构验证错误列表为空。

### 分析包含式近似去重规则

- 用户提出需要增加去重规则：先模糊匹配重复歌曲，例如歌名 B 是 A 加前缀或后缀，保留原版 A。
- 使用当前 `data/processed_jay_priority_filter/songs_kept.json` 对保留的 250 首歌曲做包含式近似重复分析。
- 直接按“短标题规范化后是长标题子串”的规则只发现 3 组候选：`月光` 与 `天台的月光`、`天台` 与 `天台的月光`、`小雨写立可白Ⅰ` 与 `小雨写立可白Ⅱ`。
- 这些候选均不适合直接按“保留短标题、删除长标题”处理：`月光` 和 `天台的月光` 是不同歌曲，`天台` 和 `天台的月光` 也是不同歌曲，`小雨写立可白Ⅰ/Ⅱ` 是不同分段曲目。
- 结论是不能使用裸包含关系作为自动去重条件；需要只在多出来的前缀或后缀属于明确版本词、修饰词或括号附加信息时才自动合并。
- 推荐规则方向为：先做标准化标题，再识别括号内容、版本词、feat/with、remaster、radio edit、伴奏、live、demo、remix 等可丢弃修饰；对于普通中文词组前后缀不自动删除，只标记为人工复核候选。

### 调整去重方向为版本去重和专辑归属验证

- 用户指出实际需要去重的样例包括《发如雪》与《发如雪 (醇享版)》、《轨迹》与《轨迹 (醇享版)》、《Six Degrees》与 Instrumental/Slowed/Reverb/Sped Up 版本、《你听得到》与《你听得到 (Inst.)》等。
- 用户同时指出《土耳其进行曲》和《- 夜访巴赫曲》虽然出现在周杰伦歌曲列表中，但从专辑和上下文看明显不属于周杰伦，需要考虑通过专辑进一步验证是否属于目标音乐人。
- 抽查样例的专辑详情后确认，`AlbumApi.get_detail(album_mid)` 可取得专辑歌手、专辑类型、唱片公司、语种、简介等字段，可用于辅助判断专辑归属。
- 样例显示《十一月的萧邦》《寻找周杰伦》《Six Degrees》《叶惠美》等保留项的专辑歌手包含目标音乐人周杰伦；而《醇享好声音》的专辑歌手为 `2018中国好声音`，《Six Degrees (Remix)` 的专辑歌手仅为派伟俊，《最脍炙人口的古典音乐100首》的专辑歌手为古典音乐，《华语乐坛混剪集》的专辑歌手为飞天猫，《音乐情书6》的专辑歌手为华语群星，均不包含周杰伦。
- 结论是下一步去重不应只按标题包含关系处理，而应新增“专辑详情缓存 + 专辑归属验证 + 版本后缀去重”三类规则。
- 自动剔除的高置信规则应优先覆盖：目标歌曲存在同名原版且当前标题或专辑标题带 `醇享版`、`Instrumental`、`Inst.`、`Slowed`、`Reverb`、`Sped Up`、`Remix` 等版本词；以及专辑歌手不包含目标音乐人且专辑为群星、纯音乐、混剪、古典或来源公司为空的明显非目标专辑。
- 对原声带、合辑、合作单曲等边界情况不应直接用“专辑歌手不含目标音乐人”一刀切删除，应先标记为 `review_album_owner_mismatch`，避免误删真实参与作品。

### 验证专辑归属和版本去重规则

- 用户要求按新思路进行验证，并在验证前删除不再有用的旧产物。
- 已删除被 `data/processed_jay_priority_filter/` 取代的旧输出目录 `data/processed_smoke/`、`data/processed_jay/`、`data/processed_jay_refiltered/`，以及当前验证会替代的旧 Markdown 报告；保留当前验证输入 `songs_all/kept/filtered` 和原始缓存。
- 新增 `musician_relationship/validate_album_ownership.py`，作为独立后处理阶段读取初过滤后的 `songs_kept.json`，低频请求并缓存 `AlbumApi.get_detail(album_mid)` 到 `data/raw/qqmusic/albums/`，再输出专辑验证后的 kept/rejected/review 数据。
- 初版强规则过度依赖 `华语群星`、`群星` 和空公司，抽查发现会把《天台》原声带、《千山万水》《屋顶》等可能真实参与作品自动剔除，因此已收紧规则：`华语群星`、`群星`、空公司单独出现仅进入 review，不再自动剔除。
- 当前自动剔除规则集中在高置信场景：存在同名原版且标题或专辑标题带版本词；专辑歌手为古典音乐、飞天猫、2018中国好声音等强非目标来源；专辑标题或简介命中混剪、醇享、remix；专辑语种为纯音乐。
- 使用周杰伦初过滤保留的 250 首歌曲进行真实验证，共检查 59 张专辑；最终保留 214 首、自动剔除 9 首、待复核 27 首。
- 自动剔除清单命中用户指出的样例：《轨迹 (醇享版)》、《发如雪 (醇享版)》、《Six Degrees (Sped Up)》、《Six Degrees (Slowed|Reverb)》、《Six Degrees (Instrumental)》、《你听得到 (Inst.)》、《土耳其进行曲》、《- 夜访巴赫曲》，另有《Nunchucks》因纯音乐原声带进入自动剔除。
- 原版《发如雪》《轨迹》《你听得到》《Six Degrees》均在验证后保留。
- 待复核清单包含《布拉格广场》《屋顶》《不该》《千山万水》《天台的月光》《天台》《阿爸》《双节棍》等专辑歌手不含周杰伦但不能自动判定为噪声的边界项。
- 输出目录为 `data/processed_jay_album_validated/`，包含 `album_validation_snapshot.json`、`songs_kept_album_validated.json/csv`、`songs_rejected_album_validated.json/csv/md`、`songs_review_album_validated.json/csv/md` 和全量验证结果。
- 验证执行 `py_compile` 通过；真实专辑详情请求首次因沙箱网络权限被拒，按规则申请网络权限后完成请求，后续复跑使用本地专辑缓存。
- 已检查 rejected/review Markdown 报告，问号数量为 0，表格列数检查无异常。

### 复盘格式和编码问题并补充协作约束

- 用户指出近期开发中反复出现 Markdown 表格渲染失败、中文问号或乱码、本地文件链接被破坏等格式问题，要求反思并在必要时补充 `AGENTS.md` 约束。
- 复盘认为主要原因不是单点 Bug，而是输出产物缺少统一验收门槛：曾使用 PowerShell 临时脚本处理中文常量导致编码污染；Windows 文本换行被二次转换导致 Markdown 表格断裂；表格单元格中的 `|` 未转义导致列数错乱；对 Markdown 表格只做局部检查，遗漏表格前空行和整体结构；最终回复中的 Windows 反斜杠路径被 Markdown 渲染破坏。
- 另一个流程问题是过早把“报告已可用”“链接可打开”等结论告诉用户，但没有先按用户实际入口回读文件、检查链接格式和表格结构。
- 已在 `AGENTS.md` 的用户长期偏好中增加本地文件链接规则：必须提供可点击 Markdown 链接，Windows 链接目标使用正斜杠绝对路径，不使用反斜杠。
- 已在 `AGENTS.md` 的项目补充规则中增加中文与编码、Markdown 报告生成、临时脚本约束和报告链接验收规则。
- 后续涉及中文报告或数据清单时，必须显式 UTF-8 读写，回读检查无替换字符，校验 Markdown 表格列数和结构，确认文件存在且大小非零，再向用户提供链接。

### 跑通薛之谦全量验证

- 用户要求再跑一个薛之谦全量，用于验证当前 pipeline。
- 为避免伪造热门榜输入，已给 `collect_singer_songs.py` 增加 `--target-singer-mid` 和 `--target-singer-name` 参数，可直接按指定 singer mid 采集单个歌手，仍复用原有分页采集、初过滤、去重和输出逻辑。
- 使用小请求确认薛之谦 singer mid 为 `002J4UUk29y8BY`，接口返回总数 528，首页包含《演员》《其实》《天外来物》《认真的雪》等歌曲。
- 使用 `collect_singer_songs.py` 全量采集薛之谦歌曲到 `data/processed_xue_priority_filter/`，结果为原始歌曲行 528 条，初过滤后去重前 133 条，去重后保留 133 条，过滤 395 条。
- 初过滤原因分布为：`empty_album` 243 条，`title_version_keyword:live` 142 条，`title_version_keyword:伴奏` 5 条，`title_version_keyword:demo` 4 条，`title_version_keyword:现场` 1 条。
- 使用 `validate_album_ownership.py` 对 133 首初过滤保留歌曲做专辑归属验证，检查 33 张专辑，输出到 `data/processed_xue_album_validated/`；结果为保留 127 首，自动剔除 0 首，待复核 6 首。
- 待复核歌曲包括《重返十七岁 (新版)》《刚刚好 (DJ 改编版)》《守候 (2020重唱版)》《我的show》《绅士 (DJ版)》《认真的雪 (Single Version)》，主要原因是专辑歌手不含薛之谦或专辑为华语群星/空公司等弱异常。
- 抽查保留结果发现当前规则仍有版本去重缺口：`DJ版`、`DJ 改编版`、`吉他版`、`Single Version`、`新版`、`重唱版` 尚未纳入高置信版本词；《方圆几里》和《方圆几里 (吉他版)》仍同时保留。
- 抽查还发现同名不同专辑重复保留候选：《我们爱过就好》同时出现在《几个薛之谦》和单曲《我们爱过就好》，《马戏小丑》同时出现在《你过得好吗》和《未完成的歌》；这类不应简单按标题删除，需要后续按发行日期、专辑类型、专辑归属和 song mid 关系做候选复核。
- rejected/review Markdown 报告已回读检查，UTF-8 可读，无 U+FFFD 替换字符，表格列数检查无异常。

### 增加热门歌手身份 registry

- 用户提出应先把热门歌手跑一个全量并存储下来，作为歌手相关基础信息，主要用于保存 id 和名字等相对稳定字段。
- 评估后认为该方向合理，但需要区分稳定身份字段和会变化的榜单快照：QQ 音乐 singer id / mid 可作为相对稳定身份键，歌手名、头像、热度榜位置和是否在热门列表中仍可能变化。
- 新增 `musician_relationship/collect_hot_singer_registry.py`，按 `SingerApi.get_singer_list_index(area=ALL, sex=ALL, genre=ALL, index=ALL)` 分页采集热门歌手列表，原始响应缓存到 `data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all/`。
- 脚本输出两个语义不同的产物：`singer_registry.json/csv` 作为当前可用歌手身份表，`hot_singer_discovery_snapshot.json` 作为本次热门榜发现快照。
- 脚本支持 `--max-pages` 做 smoke test，完整运行时默认不限制页数，按接口 `total` 和分页数量停止。
- 已先执行一页 smoke test，确认第一页返回 80 个歌手，接口总量为 6803；随后完整跑完 86 页，最后一页 3 个歌手，共得到 6803 个唯一 singer mid。
- 完整输出目录为 `data/processed_hot_singers/`，包含 `singer_registry.json`、`singer_registry.csv` 和 `hot_singer_discovery_snapshot.json`。
- 回读验证显示三个输出文件 UTF-8 可读，无 U+FFFD 替换字符；唯一 singer mid 数量为 6803，与总行数一致。
- 抽查确认 registry 中包含周杰伦 `0025NhlN2yWrP4`，发现排名第 1；包含薛之谦 `002J4UUk29y8BY`，发现排名第 4。
- 已删除临时 smoke 输出目录 `data/processed_hot_singers_smoke/`，保留原始请求缓存和正式 processed 输出。

### 生成薛之谦 pipeline 全量报告

- 用户要求查看薛之谦全量验证过程，包括每一步筛除内容、筛除理由和留下内容。
- 新增 `musician_relationship/write_singer_pipeline_report.py`，用于把指定歌手的一次 pipeline 运行整理成 Markdown 报告，避免继续用临时脚本拼接表格。
- 报告输入为 `data/processed_xue_priority_filter/` 和 `data/processed_xue_album_validated/`，输出到 `data/processed_xue_pipeline_report/`。
- 生成的报告包括：`00_summary.md` 汇总计数和原因分布；`01_initial_filtered.md` 初过滤剔除的 395 条歌曲及理由；`02_initial_kept.md` 初过滤后留下的 133 条歌曲；`03_album_review.md` 专辑验证后需要复核的 6 条；`04_album_rejected.md` 专辑验证自动剔除的 0 条；`05_final_kept.md` 最终保留的 127 条。
- 首次报告校验发现 `00_summary.md` 含多个不同列数的 Markdown 表格，旧校验器把后续两列表误判为列数错误；已修正为按连续表格块分别校验。
- 已执行 `py_compile` 验证报告脚本，通过。
- 已独立回读检查 6 个 Markdown 文件，UTF-8 可读，无 U+FFFD 替换字符，所有表格块列数一致。

### 跑通林俊杰全量验证

- 用户要求再验证一个林俊杰全量。
- 从 `data/processed_hot_singers/singer_registry.json` 查询确认林俊杰 singer mid 为 `001BLpXF2DyJe2`，热门发现排名第 2。
- 使用 `collect_singer_songs.py` 全量采集林俊杰歌曲到 `data/processed_jj_priority_filter/`；首次命令为规避 PowerShell 中文编码传入了 Unicode 转义，导致 source singer name 显示为字面量转义字符串，随后为 CLI 文本参数增加 `unicode_escape` 解码并用缓存重跑，输出中的歌手名恢复为正常中文。
- 林俊杰全量采集结果为原始歌曲行 1013 条，初过滤后保留 288 条，过滤 725 条。
- 初过滤原因分布为：`empty_album` 572 条，`title_version_keyword:live` 133 条，`title_version_keyword:remix` 11 条，`title_version_keyword:演唱会` 3 条，`title_version_keyword:伴奏` 3 条，`title_version_keyword:demo` 2 条，`title_version_keyword:纯音乐` 1 条。
- 使用 `validate_album_ownership.py` 对 288 首初过滤保留歌曲做专辑归属验证，检查 94 张专辑，输出到 `data/processed_jj_album_validated/`；结果为保留 258 首，自动剔除 1 首，待复核 29 首。
- 自动剔除项为《钢琴曲 可惜没有如果（林俊杰）》，专辑《钢琴曲 可惜没有如果（林俊杰）-山水眩月》，原因包含专辑语种纯音乐和空公司。
- review 列表包含《被风吹过的夏天》《黑暗骑士》《抢玫瑰》《小说》《御龙三国志》《期待你的爱》《小酒窝 (粤语)》《Wild Child (Radio Edit)》等，主要是专辑歌手不含林俊杰、群星专辑或空公司等弱异常。
- 抽查最终保留结果发现版本词和重复规则仍有明显缺口：`Jazz Version`、`私享版`、`晚安版`、`JJ20版`、`粤语`、`Album Version`、`Radio Edit` 等尚未统一处理。
- 同名重复候选包括《伟大的渺小》与 Jazz Version、《修炼爱情》与 Jazz Version/私享版、《只要有你的地方》与晚安版、《江南》与粤语版、《那些你很冒险的梦》与 JJ20 版，以及《小酒窝》《爱与希望》等精选/自选辑重复。
- 已使用 `write_singer_pipeline_report.py` 生成林俊杰全流程报告到 `data/processed_jj_pipeline_report/`，包含 summary、初过滤剔除、初过滤保留、专辑复核、专辑剔除和最终保留 6 个 Markdown 文件。
- 已独立回读检查 6 个 Markdown 文件，UTF-8 可读，无 U+FFFD 替换字符，所有表格块列数一致。

### 修正 pipeline 报告排序

- 用户指出过程文档没有按歌曲首字母排列，不利于人工查歌。
- 复核确认 `write_singer_pipeline_report.py` 此前按 pipeline 原始输出顺序写表，仅便于追溯处理顺序，不适合作为人工检查清单。
- 已给报告脚本增加基于 `pypinyin.lazy_pinyin()` 的排序键，所有歌曲明细表按歌名拼音/英文混排，并在表格中新增 `Sort key` 列展示排序依据。
- 已重新生成薛之谦和林俊杰的 pipeline 报告：`data/processed_xue_pipeline_report/` 与 `data/processed_jj_pipeline_report/`。
- 抽查确认薛之谦最终保留表从 `AI`、`爱不走`、`爱的期限` 等开始；林俊杰最终保留表从 `2infinity And Beyond`、`After The Rain`、`爱不会绝迹` 等开始，符合拼音/英文混排预期。
- 已独立回读检查两个目录下共 12 个 Markdown 文件，UTF-8 可读，无 U+FFFD 替换字符，所有表格块列数一致。

### 评估 name/title 相等的原版过滤规则

- 用户提出流程可继续改进：在空专辑过滤前增加 `song` 和 `title` 必须一样才认为可能是原版，否则直接剔除。
- 使用周杰伦、薛之谦、林俊杰三组现有全量数据做离线评估，比较 `name` 与 `title` 规范化后是否一致。
- 周杰伦原始 1012 条中 `name/title` 不一致 685 条；当前最终保留 214 条中仍有 3 条不一致：《Secret (加长快板)》《菊花台 (周杰伦钢琴演奏)》《Secret (慢板)》。
- 薛之谦原始 528 条中不一致 376 条；当前最终保留 127 条中仍有 1 条不一致：《方圆几里 (吉他版)》。
- 林俊杰原始 1013 条中不一致 672 条；当前最终保留 258 条中仍有 18 条不一致，包括《江南 (粤语)》《Despacito 缓缓 (Mandarin Version)》《Stay With You (英文版)》《那些你很冒险的梦 (JJ20版)》《只要有你的地方 (晚安版)》《修炼爱情 (Jazz Version)》《伟大的渺小 (Jazz Version)》以及 iTunes Session/口白/私享版等。
- 评估结论：若第一阶段目标是尽量保留原版歌曲，`name/title` 相等是很强的早期过滤信号，能提前剔除大量版本、语言版、演奏版、Session 和口白类条目。
- 风险边界：该规则不能替代专辑归属验证；`name/title` 相等的翻唱、合辑、非目标专辑仍可能混入；同时它会剔除部分官方语言版、影视主题曲标注版或特别版，如果后续想研究所有正式发行版本，需要把这些放入 review 或另存版本表，而不是彻底丢弃。

### 将 name/title 不一致过滤加到最前面

- 用户确认按改进方案执行，把 `name/title` 必须一致的规则加到最前面。
- 已在 `collect_singer_songs.py` 增加 `name_title_filter_reason()`，对 `name` 和 `title` 执行 Unicode NFKC、忽略大小写、合并空格后比较；不一致时过滤原因记为 `name_title_mismatch`。
- 过滤顺序已调整为：`name_title_mismatch` -> `empty_album` -> 标题版本关键词。
- 使用缓存重跑周杰伦、薛之谦、林俊杰三组初过滤、专辑验证和 pipeline 报告。
- 周杰伦结果：原始 1012 条，初过滤保留 240 条，过滤 772 条；专辑验证后最终保留 211 条，自动剔除 3 条，复核 26 条。初过滤原因分布为 `name_title_mismatch` 685 条，`empty_album` 86 条，`title_version_keyword:现场` 1 条。
- 薛之谦结果：原始 528 条，初过滤保留 127 条，过滤 401 条；专辑验证后最终保留 126 条，自动剔除 0 条，复核 1 条。初过滤原因分布为 `name_title_mismatch` 376 条，`empty_album` 25 条。
- 林俊杰结果：原始 1013 条，初过滤保留 266 条，过滤 747 条；专辑验证后最终保留 240 条，自动剔除 1 条，复核 25 条。初过滤原因分布为 `name_title_mismatch` 672 条，`empty_album` 70 条，`title_version_keyword:演唱会` 3 条，`title_version_keyword:live` 1 条，`title_version_keyword:纯音乐` 1 条。
- 由于新规则位于最前面，许多原先会被标记为 live/remix/demo/伴奏的歌曲现在统一归因为 `name_title_mismatch`，这是预期行为，反映当前流程优先判定“非原版候选”。
- 已重新生成 `data/processed_jay_pipeline_report/`、`data/processed_xue_pipeline_report/`、`data/processed_jj_pipeline_report/`。
- 已回读检查三个目录共 18 个 Markdown 文件，UTF-8 可读，无 U+FFFD 替换字符，所有表格块列数一致。

### 清理实验产物并整理正式开发结构

- 用户确认当前流程基本可行，要求清理实验性数据和文档，并将流程、代码、目录结构调整为更正式的开发版本。
- 已删除本地实验数据目录 `data/` 和 Python 编译缓存 `__pycache__`，仓库回到只保留源码和文档的状态；后续数据由 pipeline 命令在本地重新生成。
- 已新增 `musician_relationship/pipelines/` 作为正式 pipeline 源码目录，并将热门歌手 registry、单歌手歌曲采集、专辑归属验证、pipeline 报告生成四个脚本移入该目录。
- 为兼容旧命令，`musician_relationship/collect_hot_singer_registry.py`、`collect_singer_songs.py`、`validate_album_ownership.py`、`write_singer_pipeline_report.py` 保留为只调用正式 pipeline `main()` 的薄包装。
- 已更新默认输出目录：歌手身份表为 `data/processed/singer_registry/qqmusic_hot/`；单歌手歌曲采集默认为 `data/processed/`，建议按歌手显式传入 `data/processed/singer_songs/<singer_slug>/`；专辑验证默认为 `data/processed/album_validated/`；报告默认为 `data/processed/reports/singer_pipeline/`。
- 已在 `pyproject.toml` 增加命令入口：`mr-collect-hot-singers`、`mr-collect-singer-songs`、`mr-validate-albums`、`mr-write-pipeline-report`。
- 已新增 `README.md`，说明项目定位、正式目录结构、四步 pipeline、推荐命令和数据边界。
- 已更新 `AGENTS.md` 项目补充规则，记录正式源码目录、数据目录边界和推荐 pipeline 输出路径。
- 已执行正式目录结构 smoke test：使用薛之谦第一页歌曲输出到 `data/processed/smoke/singer_songs/xuezhiqian`，采集 30 行、初过滤保留 28 行、过滤 2 行；验证后已删除 smoke 产物和 raw 缓存。
- 已对全部 Python 文件执行 `py_compile`，通过。

### 补全歌曲制作人员采集流程

- 用户要求继续使用周杰伦全量做后续开发验证；当前歌曲列表已经可用，下一步需要在流程中补上对歌曲信息或制作人员信息的请求，以取得作词和作曲。
- 目标效果为运行单歌手歌曲采集 pipeline 后，`songs_kept.json` 和 `songs_kept.csv` 中每首保留歌曲都能看到作词、作曲等制作人员字段；上游缺失或接口异常时记录状态，不中断整批。
- 已修改 `musician_relationship/pipelines/collect_singer_songs.py`，在初过滤和去重后默认调用 `SongApi.get_producer`，并将结果写入每首歌曲的 `credits` 字段。
- `credits` 中保留按 QQ 音乐返回分组整理的 `groups`，并展开 `lyricists`、`composers`、`arrangers`、`producers` 等常用字段；CSV 也同步新增这些列和 `credit_status`。
- 新增 `--skip-producers` 用于只生成歌曲列表，新增 `--max-producer-songs` 用于小样本调试制作人员请求数量。
- 初次真实全量验证发现 `qqmusic-api-python` 在上游 `Lst=null` 时会抛出模型校验异常；已将制作人员请求改为缓存原始响应并由 pipeline 宽松解析，`Lst=null` 统一记录为 `missing_producer_list`。
- 已更新 `README.md`，说明单歌手歌曲采集会默认补全制作人员信息、输出字段含义和调试参数。

### 验证周杰伦全量制作人员采集

- 验证对象为周杰伦 singer mid `0025NhlN2yWrP4` 的全量歌曲采集和制作人员补全，输出目录为 `data/processed/singer_songs/zhoujielun/`。
- 先执行 smoke test：限制歌曲页为 1 页、制作人员请求为 3 首，确认《晴天》《搁浅》《那天下雨了》均返回 `status=ok`，且作词、作曲字段非空。
- 全量验证共读取周杰伦歌曲接口 1012 条，按当前初过滤规则保留并去重 240 条，过滤 772 条。
- 对 240 条保留歌曲均发起或复用制作人员请求，结果为 `ok` 230 条、`missing_producer_list` 10 条。
- 抽查 `songs_kept.json` 中《晴天》显示 `credits.groups` 包含“演唱、作词、作曲、编曲、制作人”等分组，展开字段中 `lyricists=["周杰伦"]`、`composers=["周杰伦"]`。
- 10 条 `missing_producer_list` 代表上游响应没有制作人员列表，不再作为批处理失败处理；这些歌曲仍保留在输出中，供后续专辑验证或人工复核。
- 已执行全部 Python 文件 `py_compile`，未报语法错误。
- 已回读周杰伦 `singer_song_snapshot.json`、`songs_kept.json` 和 `songs_kept.csv`，确认 `songs_kept` 数量与 snapshot 一致，CSV 含 `lyricists`、`composers`、`arrangers`、`producers`、`credit_status` 列，且存在作词作曲非空样例。
- 已对修改后的 `README.md` 和 `collect_singer_songs.py` 执行 UTF-8 读取、无 U+FFFD 检查，并按用户偏好统一写回 CRLF 行尾。

### 验证薛之谦和林俊杰全量制作人员采集

- 用户要求继续全量验证薛之谦和林俊杰，用于确认歌曲制作人员补全流程在更多歌手上的稳定性。
- 验证对象为薛之谦 singer mid `002J4UUk29y8BY` 和林俊杰 singer mid `001BLpXF2DyJe2` 的单歌手全量歌曲采集、初过滤、去重和制作人员补全。
- 薛之谦输出目录为 `data/processed/singer_songs/xuezhiqian/`；原始歌曲行 528 条，初过滤后去重保留 127 条，过滤 401 条，制作人员请求 127 条。
- 薛之谦制作人员状态为 `ok` 124 条、`missing_producer_list` 3 条；非 `ok` 歌曲为《未完成的歌》《我们爱过就好》《我的show》。
- 林俊杰输出目录为 `data/processed/singer_songs/linjunjie/`；原始歌曲行 1013 条，初过滤后去重保留 266 条，过滤 747 条，制作人员请求 266 条。
- 林俊杰制作人员状态为 `ok` 248 条、`missing_producer_list` 18 条；非 `ok` 歌曲包括《达尔文》《恨幸福来过》《那女孩对我说》《想见你想见你想见你》《At Least I Had You》《Checkmate》《抢玫瑰》《Lose Control》《御龙三国志》《钢琴曲 可惜没有如果（林俊杰）》等。
- 林俊杰 `ok` 歌曲中存在序曲、纯音乐或器乐类条目只有作曲没有作词，因此作词和作曲同时非空的数量为 232 条；这属于字段覆盖差异，不等同于请求失败。
- 已回读两个歌手的 `singer_song_snapshot.json`、`songs_kept.json` 和 `songs_kept.csv`，确认 `songs_kept` 数量与 snapshot、CSV 行数一致，CSV 含 `lyricists`、`composers`、`arrangers`、`producers`、`credit_status` 列。
- 已对 `collect_singer_songs.py` 执行 `py_compile`，未报语法错误。

### 增加可视化前制作人员完整性过滤

- 用户指出可视化利用之前还需要删除缺作词或缺作曲的条目。
- 已将制作人员完整性过滤加到 `collect_singer_songs.py` 的制作人员补全之后：默认 `songs_kept` 只保留 `credits.status=ok` 且 `lyricists`、`composers` 都非空的歌曲。
- 被剔除的歌曲不会丢失，单独输出到 `songs_credit_incomplete.json/csv`，并写入 `credit_filter_reason` 和 `visualization_ready` 字段，便于回看是 `missing_lyricists`、`missing_composers` 还是 `credit_status:missing_producer_list`。
- 新增 `--keep-incomplete-credits` 参数，用于调试时保留缺作词或缺作曲条目在 `songs_kept` 中。
- 已更新 `README.md`，说明 `songs_kept` 默认作为图谱和可视化可直接消费的数据，缺作词或缺作曲条目进入 `songs_credit_incomplete`。
- 使用缓存重跑周杰伦，初过滤后 240 条，因制作人员不完整剔除 30 条，最终 `songs_kept` 210 条；剔除原因包括 `missing_lyricists` 20 条和 `credit_status:missing_producer_list` 10 条。
- 使用缓存重跑薛之谦，初过滤后 127 条，因制作人员不完整剔除 3 条，最终 `songs_kept` 124 条；剔除原因均为 `credit_status:missing_producer_list`。
- 重跑林俊杰原输出目录时，写入 `songs_kept.csv` 遇到 Windows 文件占用导致 `PermissionError`，推测该 CSV 被本机程序打开；为完成验证，改用 `data/processed/singer_songs/linjunjie_credit_filtered/` 作为备用输出目录。
- 林俊杰备用输出验证结果为初过滤后 266 条，因制作人员不完整剔除 34 条，最终 `songs_kept` 232 条；剔除原因包括 `credit_status:missing_producer_list` 18 条、`missing_lyricists` 15 条和 `missing_composers` 1 条。
- 已回读周杰伦、薛之谦和林俊杰备用输出的 `singer_song_snapshot.json`、`songs_kept.json/csv`、`songs_credit_incomplete.json/csv`，确认 `songs_kept` 全部满足作词和作曲非空，`songs_credit_incomplete` 全部带有剔除原因。
- 已对 `collect_singer_songs.py` 执行 `py_compile`，未报语法错误。

### 合并林俊杰正式输出和备用输出

- 用户要求把此前因 CSV 文件占用导致未完整更新的林俊杰正式输出和备用输出合并，只保留一个有效的新目录。
- 已将备用目录 `data/processed/singer_songs/linjunjie_credit_filtered/` 合并回正式目录 `data/processed/singer_songs/linjunjie/`，并删除备用目录。
- 初次合并后发现 PowerShell 通配复制没有把备用目录中的 `songs_credit_incomplete.csv` 带回正式目录，且正式目录部分 CSV 仍是旧状态。
- 为避免重新请求接口，已基于正式目录中的新 JSON 重新生成 `songs_all.csv`、`songs_filtered.csv`、`songs_kept.csv` 和 `songs_credit_incomplete.csv`。
- 回读验证显示正式林俊杰目录中 `songs_kept.json/csv` 均为 232 条，`songs_credit_incomplete.json/csv` 均为 34 条；`songs_kept` 全部满足作词和作曲非空，`songs_credit_incomplete` 全部带有剔除原因。
- 已确认备用目录 `data/processed/singer_songs/linjunjie_credit_filtered/` 不再存在。

### 重命名源码包并移除旧薄包装入口

- 用户指出源码包目录 `musician_relationship/` 与仓库根目录 `Musician_Relationship/` 语义接近，且包根部有四个薄包装脚本、`pipelines/` 下又有四个正式实现，容易造成目录和入口混淆。
- 已将正式 Python 包目录从 `musician_relationship/` 重命名为 `music_metadata_graph/`，使源码包名更贴近“音乐元数据图谱”职责。
- 已删除包根部四个旧薄包装脚本，只保留 `music_metadata_graph/pipelines/` 下的正式 pipeline 实现。
- 已更新 `pyproject.toml` 中四个脚本入口，使其指向 `music_metadata_graph.pipelines.*`。
- 已更新 `README.md` 中的目录结构和 `python -m` 示例命令，统一使用 `python -m music_metadata_graph.pipelines.<module>`。
- 已更新 `AGENTS.md` 的项目补充规则，明确主动开发落在 `music_metadata_graph/pipelines/`，不再保留包根同名薄包装入口。
- 已清理移动目录后残留的 `__pycache__`，避免旧薄包装 `.pyc` 继续混淆目录结构。
- 验证对象为新包目录下全部 Python 文件，执行 `py_compile` 未报语法错误。
- 验证新入口 `python -m music_metadata_graph.pipelines.collect_singer_songs --help` 和 `python -m music_metadata_graph.pipelines.collect_hot_singer_registry --help`，均能正常输出帮助信息。

### 构思静态网页可视化设计

- 用户要求开始构思网页如何设计，当前阶段尚未进入前端代码实现。
- 目标效果初步收敛为一个 GitHub Pages 可打开的静态数据分析网页，读取本地 pipeline 生成并提交的静态 JSON 数据，不在浏览器中实时请求 QQ 音乐接口。
- 网页首页不做营销落地页，而是直接进入图谱分析工作台，首屏展示数据集选择、核心计数、关系图和可追溯歌曲明细入口。
- 关系图设计方向为音乐人节点优先使用头像或头像 URL，边表示“作词/作曲/编曲/制作人等贡献者 -> 演唱者/目标音乐人”的合作关系；可切换有向/无向、区分职能/合并职能。
- 页面需要同时提供图谱视图和表格视图：图谱用于看合作网络，表格用于核查每条边来自哪些歌曲、哪些字段和哪次 pipeline 输出。
- 初步交互包括歌手/数据集选择、角色筛选、只看外部合作/包含自作自唱、最小合作次数过滤、搜索音乐人、点击节点查看参与歌曲和职能分布、点击边查看支撑歌曲列表。
- 数据输入应使用经过制作人员完整性过滤后的 `songs_kept.json`，不直接消费缺作词或缺作曲的 `songs_credit_incomplete`；后者可作为质量报告入口展示，但不参与图谱。
- 风险边界包括头像 URL 可能失效、节点过多导致静态浏览器图谱性能下降、同名音乐人消歧仍依赖 singer mid、部分歌曲只含作词作曲但缺头像或 singer mid。
- 本轮不做实时采集、账号态能力、歌词全文展示、音频播放下载、复杂社区发现算法和多平台融合。

### 调整网页设计以支持不完整数据

- 用户指出网页应支持不完整数据；即使当前只有周杰伦、薛之谦、林俊杰三个歌手的数据，也应该能可视化。
- 用户指出这三个数据集都是歌手维度，彼此之间可能没有或很少作词作曲关系，网页不能因此显示为空或显得不可用。
- 已调整设计理解：网页第一版不能只依赖“歌手之间互相作词作曲”的强关系图，而应支持以单个歌手曲库、歌曲、贡献者和职能为中心的多视图可视化。
- 目标效果应包含稀疏网络的有效展示：即使不同目标歌手之间没有边，也能展示每个目标歌手的曲库规模、作词/作曲贡献者分布、自作比例、外部合作者列表和歌曲级支撑明细。
- 图谱视图应允许孤立目标歌手节点存在，并用“目标歌手 -> 歌曲 -> 贡献者”或“贡献者 -> 目标歌手”的投影视图切换，避免单一投影造成边太少。
- 数据质量和覆盖范围需要在页面中明确展示，例如当前数据集包含哪些目标歌手、各自歌曲数、缺作词作曲剔除数、关系边数和跨目标歌手合作数。

### 明确空边图谱也要显示孤立节点

- 用户纠正网页在没有边时不应只显示文字说明，而应显示孤立节点。
- 已调整图谱渲染规则：任意图谱模式下，只要当前数据范围内存在节点，就应绘制节点；边为空时显示孤立节点布局，而不是把图谱区域替换为文字。
- 文案只作为辅助状态说明，例如说明当前筛选条件下没有连边；主视觉仍保留节点，体现数据存在但当前关系投影稀疏。
- 对跨目标歌手交集等容易稀疏的视图，应至少显示当前目标歌手节点；如模式允许，也显示候选贡献者节点，避免用户误以为数据未加载。

### 实现静态网页图谱工作台初版

- 用户要求开始实现网页，当前目标为先做 GitHub Pages 可打开的静态网页，不引入前端构建依赖。
- 新增 `music_metadata_graph/pipelines/export_web_dataset.py`，从 `data/processed/singer_songs/<slug>/songs_kept.json` 和质量数据导出网页可消费的静态 JSON。
- 新增 `web/index.html`、`web/styles.css` 和 `web/app.js`，实现静态图谱工作台初版。
- 网页支持数据集切换、图谱模式切换、边职能区分或合并、有向或无向显示、最小歌曲数过滤、搜索、节点/边详情、歌曲明细表、关系明细表和数据质量表。
- 图谱模式包括“歌手中心图”“歌曲桥接图”“跨歌手交集”；当筛选后没有边时，图谱区域仍保留孤立节点显示，并在辅助说明中提示暂无连边。
- 已在 `pyproject.toml` 增加 `mr-export-web-dataset` 脚本入口。
- 已更新 `README.md`，说明 `web/` 目录、静态数据导出命令和 `web/index.html` 入口。
- 使用当前三位歌手正式输出导出 `web/data/catalog.json`、`zhoujielun.json`、`xuezhiqian.json`、`linjunjie.json`；导出汇总为 3 个数据集、566 首可视化歌曲、67 首制作人员不完整隔离条目、186 个唯一节点、9 个跨目标歌手贡献者。
- 已对网页数据 JSON 执行 UTF-8 读取和 JSON 解析检查，四个数据文件均可解析。
- 已对新导出脚本和全部 pipeline Python 文件执行 `py_compile`，未报语法错误。
- 已启动本地静态预览服务，入口为 `http://127.0.0.1:8765/`；验证 `/`、`/styles.css`、`/app.js` 和四个 `/data/*.json` 资源均返回 HTTP 200。
- 当前未进行浏览器截图级交互验证；原因是本轮可用工具中没有暴露浏览器插件的 Node REPL 执行入口。已用本地 HTTP 资源验证和静态检查替代。

### 纠正网页数据集与目标歌手语义

- 用户指出当前网页把一个歌手显示成一个数据集不合理；正确语义应为 QQ 音乐是数据集，周杰伦、薛之谦、林俊杰等只是当前 QQ 音乐数据集下已覆盖的目标歌手范围。
- 用户指出“只能合并分开”等选项命名含糊，且切换到跨歌手交互后其他选项看起来失效，页面布局和交互体验较差。
- 已调整目标效果：网页顶部固定展示“QQ 音乐”作为数据集，目标歌手作为筛选范围；页面应支持全部目标歌手合并查看，也支持单个目标歌手查看。
- 已将 `export_web_dataset.py` 导出的 `catalog.json` 从旧的 `datasets` 结构调整为 `source_dataset` 与 `targets`，并在共同合作者数据中写入每个目标歌手下的角色、歌曲数和支撑歌曲，避免跨歌手视图只能显示空泛连线。
- 已重写 `web/app.js` 的前端状态：使用 `currentTarget` 表示目标歌手范围，保留“全部目标歌手”聚合视图；“共同合作者”视图在单个目标歌手范围下显示该歌手与其他目标歌手共享的合作者。
- 已将“边模式”改名为“职能显示”，选项改为“作词/作曲分开”和“合并为合作次数”；“图谱模式”改为“视图”，选项改为“贡献者网络”“歌曲桥接图”“共同合作者”。
- 已调整 `web/index.html` 和 `web/styles.css`：顶部只把 QQ 音乐作为数据集标识，目标歌手、视图、职能显示、连线方向、最小歌曲数作为操作控件；页面主体增加数据源说明和范围说明。
- 已更新 `README.md`，说明网页中的数据集指 QQ 音乐元数据集，歌手是当前数据集下的覆盖范围，不是独立数据集。
- 已重新导出 `web/data/catalog.json`、`zhoujielun.json`、`xuezhiqian.json`、`linjunjie.json`；导出汇总为 3 位目标歌手、566 首可视化歌曲、67 首制作人员不完整隔离条目、186 个唯一节点、9 个共同合作者。
- 已按用户偏好将本轮修改和生成的文本文件统一为 CRLF 行尾。

### 验证网页语义与静态资源

- 验证对象为 `music_metadata_graph/pipelines/export_web_dataset.py`，执行项目指定 Conda Python 的 `py_compile`，未报语法错误。
- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误。
- 验证对象为新版 `web/data/catalog.json`，执行 Node JSON 解析与协议检查，确认存在 `source_dataset.name=QQ 音乐`、`targets` 数量为 3、旧的顶层 `datasets` 键不再存在，且共同合作者条目包含目标歌手明细和正数歌曲数。
- 验证对象为本地静态预览服务，访问 `http://127.0.0.1:8765/`、`/styles.css`、`/app.js` 和 `/data/catalog.json` 均返回 HTTP 200。
- 验证对象为页面 HTML 控件 ID，检查 `source-name`、`source-description`、`target-select`、`view-mode`、`role-display`、`direction-mode`、`min-count`、`search-input`、`graph`、`detail-content`、`table-content` 均存在。
- 旧控件和旧状态搜索显示前端不再使用 `dataset-select`、`edge-mode`、`currentSlug`；`app.js` 中保留 `state.catalog?.datasets` 仅作为旧 `catalog.json` 兼容分支。
- 当前未完成浏览器截图级交互验证；原因是会话未暴露浏览器插件要求的 Node REPL 执行工具，且本地 Node 环境未安装 Playwright 包。已使用 HTTP 资源检查、语法检查和数据协议检查作为替代。
- `git status --short` 因本机 Git safe.directory 所有权检查失败未能执行，无法在本轮通过 Git 输出复核完整改动清单。

### 改善网页图谱节点布局和有向边表达

- 用户指出当前图谱节点位置没有设计调整，导致边重叠在一起看不清关系；有向边也没有明确方向体现。
- 已定位原因：原实现按节点类型统一放圆环，贡献者到同一个目标歌手的边大量向中心收束；边使用直线连到节点圆心，箭头被目标节点覆盖。
- 已修改 `web/app.js` 的图谱布局：贡献者网络按目标歌手分簇，单目标歌手时围绕目标节点分多圈，多目标歌手时把只关联单个目标的贡献者放到对应目标附近，把共同贡献者放在目标之间的上方。
- 已为共同合作者视图增加上下分层布局：共同合作者位于上层，目标歌手位于下层，减少交叉和节点遮挡。
- 已为歌曲桥接图增加左中右分层布局：贡献者、歌曲、目标歌手分列展示，避免所有歌曲节点与目标节点挤在同一个圆环。
- 已增加轻量节点避让计算，针对贡献者网络和共同合作者视图减少节点之间的近距离重叠；歌曲桥接图保持固定分层，避免大量歌曲节点被力导向打乱。
- 已将边从 SVG `<line>` 改为 `<path>` 二次曲线，按同一 source-target 组合和职能类型错开曲率，降低作词/作曲等平行边重叠。
- 已将有向边端点从节点圆心缩短到节点外侧，并把箭头 marker 放到曲线末端，使箭头不再被目标节点遮挡。
- 已更新 `web/styles.css`，增强边线宽度、圆角、标签描边和选中态，提升重叠场景下的辨识度。
- 已按用户偏好将修改后的 `web/app.js` 和 `web/styles.css` 统一为 CRLF 行尾。

### 验证图谱布局渲染改动

- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误。
- 验证对象为本地静态预览服务，访问 `http://127.0.0.1:8765/`、`/styles.css`、`/app.js` 均返回 HTTP 200。
- 静态搜索确认 `web/app.js` 已使用 `edgeCurve`、`layoutNodes` 和 `relaxPositions`，并保留 `marker-end="url(#arrow)"`；旧的图谱边 `<line>` 生成逻辑已不再存在。
- 当前仍未完成浏览器截图级视觉验证；原因同前，会话未暴露浏览器插件要求的 Node REPL 执行工具，且本地 Node 环境未安装 Playwright 包。

### 修正图谱节点继续重叠问题

- 用户反馈调整后节点仍然重叠在一起。
- 已进一步定位问题：上一版仍使用固定高度 SVG 画布，并依赖轻量力导向做局部避让；在节点数较多时，固定画布和全量文字标签会把节点和标签继续压在一起。
- 已将 `web/app.js` 的布局策略改为确定性网格占位，不再依赖力导向把节点临时推开。
- 贡献者网络的单目标歌手视图改为目标歌手固定在右侧，贡献者按连接权重排序后排入左侧多列网格，避免围绕中心点叠圈。
- 多目标贡献者网络中，各目标歌手对应贡献者进入各自网格区域，共同贡献者放在下方共享区域。
- 歌曲桥接图中，贡献者、歌曲、目标歌手继续分列，但歌曲节点间距扩大并按目标歌手分区排列。
- 共同合作者视图中，共同合作者从单行排列改为上方多列网格，目标歌手保持下方分布。
- 已新增按当前节点数量计算 SVG 高度的逻辑，图谱画布会随节点规模在合理范围内增高，避免把大量节点挤进固定 560px 高度。
- 已新增节点标签显示规则：目标歌手、搜索命中、选中节点和高连接节点显示常驻标签；低权重普通节点默认只显示圆点，点击或搜索时再显示名称，减少文字重叠造成的不可读。
- 已更新 `web/styles.css`，将图谱最小高度调整为 640px，并为节点增加可点击指针提示。
- 已删除已禁用的轻量力导向函数，避免后续维护误以为仍在使用力布局。
- 已按用户偏好将 `web/app.js` 和 `web/styles.css` 统一为 CRLF 行尾。

### 验证节点网格布局改动

- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误。
- 验证对象为本地静态预览服务，访问 `http://127.0.0.1:8765/`、`/styles.css`、`/app.js` 均返回 HTTP 200。
- 静态搜索确认 `web/app.js` 已使用 `graphHeightFor`、`distributeGrid` 和 `shouldShowNodeLabel`，并确认旧的 `relaxPositions` 不再存在。
- 当前仍未完成浏览器截图级视觉验证；原因同前，会话未暴露浏览器插件要求的 Node REPL 执行工具，且本地 Node 环境未安装 Playwright 包。

### 纠正图谱网格布局方向错误

- 用户指出上一版虽然减少了重叠，但节点固定在指定位置且像军训一样整齐排列，布局更糟糕，不符合关系图谱的自然表达。
- 已确认上一版为了避免重叠使用确定性网格占位，解决了重叠但牺牲了关系图应有的有机分布，这是方向错误。
- 已移除 `web/app.js` 中的网格式 `distributeGrid`、`layoutArtistGraph`、`layoutSongGraph` 和 `layoutBridgeGraph` 逻辑。
- 已新增基于稳定随机种子的初始布局，节点初始位置围绕图谱中心自然散开，同一数据在刷新后仍保持稳定。
- 已新增 `forceDirectedLayout`，通过节点排斥、边拉力、碰撞距离和边界约束计算最终位置，使关联强的节点自然靠近，弱关联节点自然散开。
- 已将原先固定目标歌手坐标改为软锚点：不同视图只给目标歌手、歌曲、贡献者提供轻微方向引导，不再把节点钉死在某个位置。
- 已保留按节点数量扩展 SVG 高度和低权重节点隐藏常驻标签的策略，用于减少文字遮挡，但不再把节点排成规整网格。
- 已收紧标签显示阈值：贡献者网络中默认只显示目标歌手和高连接节点标签；歌曲桥接图默认隐藏歌曲标签，点击或搜索时再展示具体名称。
- 已按用户偏好将 `web/app.js` 统一为 CRLF 行尾。

### 验证力导向图谱布局改动

- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误。
- 静态搜索确认 `web/app.js` 已使用 `initialPositions`、`anchorForNode` 和 `forceDirectedLayout`，旧网格布局函数名不再出现。
- 验证对象为本地静态预览服务，访问 `http://127.0.0.1:8765/app.js` 返回 HTTP 200。
- 当前仍未完成浏览器截图级视觉验证；原因同前，会话未暴露浏览器插件要求的 Node REPL 执行工具，且本地 Node 环境未安装 Playwright 包。

### 增加网页资源版本号以排查刷新无变化

- 用户反馈刷新网页后布局没有变化。
- 已检查当前 `web/index.html`，发现仍以裸路径引用 `styles.css` 和 `app.js`，浏览器可能继续使用缓存的旧静态资源。
- 已将 CSS 和 JS 引用改为 `styles.css?v=20260511-force-layout` 与 `app.js?v=20260511-force-layout`，用于强制浏览器重新请求当前版本资源。
- 已在 `web/app.js` 增加布局版本标记 `force-layout-20260511`，并显示在图谱说明行中，便于确认浏览器实际加载的是新版布局代码。
- 已按用户偏好将 `web/index.html` 和 `web/app.js` 统一为 CRLF 行尾。

### 验证版本化静态资源

- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误。
- 验证对象为本地静态预览服务，访问 `http://127.0.0.1:8765/index.html?check=force-layout`，确认返回 HTML 中包含 `app.js?v=20260511-force-layout` 和 `styles.css?v=20260511-force-layout`。
- 验证对象为版本化脚本资源，访问 `http://127.0.0.1:8765/app.js?v=20260511-force-layout`，确认返回内容包含 `force-layout-20260511`。
- 再次验证 `/index.html?check=2`、`/styles.css?v=20260511-force-layout`、`/app.js?v=20260511-force-layout` 均返回 HTTP 200。

### 删除歌曲桥接图视图

- 用户指出“歌曲桥接图”概念不清，且因歌曲节点过多导致全部叠在一起看不清，要求删除该视图。
- 已从 `web/index.html` 的视图下拉中移除“歌曲桥接图”选项，页面仅保留“贡献者网络”和“共同合作者”两个图谱视图。
- 已从 `web/app.js` 删除 `buildSongGraph` 以及 `viewMode === "song"` 的构图入口，图谱不再生成歌曲节点。
- 已删除歌曲节点相关布局、半径、样式分支和 CSS `.song-node` 样式。
- 底部“歌曲明细”表和边/节点详情中的支撑歌曲列表继续保留，因为它们用于核查关系来源，不再作为图谱节点展示。
- 已将静态资源版本号更新为 `20260511-no-song-view`，并将图谱说明中的布局版本标记更新为 `no-song-view-20260511`，避免浏览器继续缓存上一版脚本。
- 已按用户偏好将 `web/index.html`、`web/app.js` 和 `web/styles.css` 统一为 CRLF 行尾。

### 验证删除歌曲桥接图

- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误。
- 静态搜索确认 `web/index.html`、`web/app.js` 和 `web/styles.css` 中不再出现“歌曲桥接图”、`buildSongGraph`、`viewMode === "song"`、`type === "song"`、`song_nodes` 或 `.song-node`。
- 验证对象为本地静态预览服务，访问 `http://127.0.0.1:8765/index.html?check=no-song-view-2`，确认返回 HTML 不含“歌曲桥接图”，且包含 `app.js?v=20260511-no-song-view` 和 `styles.css?v=20260511-no-song-view`。
- 验证对象为版本化脚本资源，访问 `http://127.0.0.1:8765/app.js?v=20260511-no-song-view`，确认返回内容不含歌曲图构图分支，且包含 `no-song-view-20260511`。

### 将贡献者网络改为默认概览图

- 用户提供截图指出，即使只显示周杰伦的贡献者网络也已经非常混乱；显示三个目标歌手时更加不可读，未来增加更多歌手必然无法扩展。
- 已确认主要问题不是单纯节点布局，而是信息密度过载：所有 1 首歌长尾关系和所有边标签同时绘制，导致目标歌手周围形成密集边束和标签堆叠。
- 已将 `web/index.html` 中“最小歌曲数”默认值从 1 调整为 2，使默认图谱不再显示只支撑 1 首歌的低权重边。
- 已在 `web/app.js` 增加 `reduceGraphForOverview()`，贡献者网络默认按每个目标歌手保留高权重贡献者，上限为每个目标歌手 36 个贡献者；搜索时不应用该截断，便于查找特定节点。
- 已将常驻边标签改为仅在选中边时显示，避免大量“作词 · 1”“作曲 · 1”标签覆盖目标歌手周围区域。
- 已提高普通贡献者常驻标签阈值，仅目标歌手、高连接贡献者、搜索命中或选中节点显示名称。
- 图谱说明文字已改为提示“默认显示高权重关系，完整数据见关系明细”，明确图谱是概览，不是全量明细投影。
- 已将静态资源版本号更新为 `20260511-overview-filter`，并将布局版本标记更新为 `overview-filter-20260511`，避免浏览器继续缓存旧脚本。
- 已按用户偏好将 `web/index.html` 和 `web/app.js` 统一为 CRLF 行尾。

### 验证贡献者网络概览过滤

- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误。
- 验证对象为本地静态预览服务，访问 `http://127.0.0.1:8765/index.html?check=overview-filter`，确认返回 HTML 包含 `app.js?v=20260511-overview-filter` 且最小歌曲数默认值为 2。
- 验证对象为版本化脚本资源，访问 `http://127.0.0.1:8765/app.js?v=20260511-overview-filter`，确认返回内容包含 `overview-filter-20260511`、`reduceGraphForOverview` 和 `maxVisibleContributors`。

### 调整贡献者网络边线视觉

- 用户提供截图指出过滤后节点数量可控，但连线仍然非常不自然。
- 已定位主要视觉问题：边曲率偏移过大，导致多条边呈扇形强弯；有向箭头默认全部显示并堆在目标歌手节点周围，形成一圈灰色箭头。
- 已减小 `edgeCurve()` 的平行边偏移和职能偏移，使默认连线更接近柔和弧线，而不是大幅弯曲到一侧。
- 已将有向箭头改为仅在选中边时显示；默认图谱只显示关系线，避免目标歌手周围出现箭头堆叠。
- 已保留选中边标签，点击边后仍能看到职能、歌曲数和方向，右侧详情继续展示支撑歌曲。
- 已降低默认边线宽度和透明度，选中边再加粗突出。
- 图谱说明文字改为提示“选中边查看方向和歌曲”，避免误以为默认隐藏方向后方向信息丢失。
- 已将静态资源版本号更新为 `20260511-soft-edge`，并将布局版本标记更新为 `soft-edge-20260511`。
- 已按用户偏好将 `web/index.html`、`web/app.js` 和 `web/styles.css` 统一为 CRLF 行尾。

### 验证边线视觉调整

- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误。
- 验证对象为本地静态预览服务，访问 `http://127.0.0.1:8765/index.html?check=soft-edge`，确认返回 HTML 包含 `app.js?v=20260511-soft-edge` 和 `styles.css?v=20260511-soft-edge`。
- 验证对象为版本化脚本资源，访问 `http://127.0.0.1:8765/app.js?v=20260511-soft-edge`，确认返回内容包含 `soft-edge-20260511`，且有向箭头 marker 逻辑需要选中边才启用。

### 调研成熟网络图可视化框架

- 用户指出当前网络图呈现和交互体验仍然很差，并询问是否有成熟框架可替代当前手写 SVG 网络图。
- 已确认当前网页图谱问题不应继续靠手写布局微调解决；更合理的方向是用成熟图可视化引擎接管布局、缩放、拖拽、选中、高亮、碰撞和边渲染。
- 已在 GitHub 和项目官网调研 `Cytoscape.js`、`sigma.js`、`AntV G6`、`force-graph`、`vis-network`、`cosmos.gl`、`Graphin` 等方案。
- 目标效果为保留当前静态 GitHub Pages 打开方式和现有 JSON 数据来源，将图谱区域替换为成熟网络图组件；用户应能自然缩放、拖拽节点、点击节点或边查看右侧详情，并通过搜索或筛选聚焦局部关系。
- 实现方案倾向先做一个最小替换原型：不重建整个前端工程，只替换 `web/app.js` 中图谱渲染层，保留顶部筛选、右侧详情和底部明细表。
- 初步判断 `force-graph` 最适合快速验证：支持静态 script 标签引入、Canvas 渲染、d3-force 布局、缩放平移、节点拖拽、节点与边 hover/click、方向边、曲线边、图片节点和碰撞检测示例，迁移成本最低。
- `vis-network` 也适合快速替换，API 简单并支持图片节点、自动布局和聚类，但视觉风格较老，后续精细化交互可能不如 `force-graph` 和 `G6`。
- `AntV G6` 和 `Cytoscape.js` 更适合长期做完整图分析工作台，布局、插件和交互能力更强，但集成复杂度高于 `force-graph`。
- `sigma.js` 和 `cosmos.gl` 更偏大规模 WebGL 图浏览；当前数据规模尚未达到必须使用它们的程度，且头像节点、边方向和业务交互需要额外定制。
- 风险边界包括 CDN 依赖或本地 vendor 依赖管理、Canvas/WebGL 可访问性弱于 SVG、头像跨域加载失败、移动端性能和浏览器兼容性。
- 本轮不做代码替换，仅完成候选框架调研和迁移建议；后续若进入实现，需先做 `force-graph` 原型并进行浏览器实际交互验证。

### 生成 force-graph 中文 API 整理文档

- 用户要求先详细分析 `force-graph` 的能力，并将完整 API 文档整理到项目根目录，翻译成中文、使用 UTF-8 编码并合理分段，便于先理解可控范围再做设计。
- 已新增根目录文档 `force-graph-api-zh.md`，内容按“是什么、怎么接入、节点控制、边控制、布局、交互、视图控制、示例说明、适合本项目的用法”分段整理。
- 文档面向设计阶段使用，重点说明节点可用头像、颜色、文字和自定义绘制，边可用颜色、虚线、曲率、箭头和粒子流动，且可通过回调控制点击、悬停、聚焦和过滤。
- 文档中同时整理了官方示例的用途划分，帮助后续选择最合适的接入方式而不是直接照搬某个 sample。
- 本轮未修改现有网页实现，仅新增说明文档和本日志记录。

### 正式安装 force-graph 并核对包内文档

- 用户明确要求不再保留临时克隆仓库，改为正式安装库，并确认安装后库内是否自带 API 文档；若没有，再补英文文档供后续参考。
- 已在项目根目录执行正式安装，`package.json` 生成并记录了 `force-graph` 依赖，版本为 `^1.51.4`，并生成了 `package-lock.json`。
- 已确认 `node_modules/force-graph` 内包含 `README.md` 和 `dist/force-graph.d.ts`，说明库本身已经自带英文 API 说明与类型声明。
- 已确认安装结果可通过 `npm ls force-graph --depth=0` 直接看到本项目已依赖 `force-graph@1.51.4`。
- 由于库内文档已经存在，本轮未额外补写英文 API 文档，仅保留此前的中文整理文档供设计阶段阅读。

### 更新 AGENTS 依赖与文档约定

- 用户要求把依赖库使用情况和 API 文档约定记入 `AGENTS.md`，以便后续开发遵循统一规则。
- 已在项目补充规则中加入 `force-graph` 正式依赖约定，明确网页图谱优先围绕该库实现，不再依赖临时克隆仓库作为长期来源。
- 已在项目补充规则中加入 `force-graph` 文档使用约定，明确优先阅读 `node_modules/force-graph/README.md` 和 `dist/force-graph.d.ts` 作为英文 API 依据。
- 已明确本地中文整理文档只能作为设计阶段参考，不替代库本体文档。

### 重写 force-graph 中文文档为可控项速查表

- 用户要求将此前的 force-graph 中文文档重写为只记录可控制项的速查表，删除介绍、安装和分析内容。
- 已将根目录文档 `force-graph-api-zh.md` 重写为按“数据输入、容器布局、节点样式、边样式、力导向与布局、交互、视图控制、工具方法”分段的单行速查表。
- 已按用户要求把说明和函数名放在同一行，避免出现“说明一行、函数名下一行”的排版。
- 新版文档不再包含库介绍、安装说明、示例分析和使用判断，仅保留后续设计时需要的可控入口名称。

### 将网页图谱渲染替换为 force-graph

- 用户要求把当前绘图换成新安装的库，理解为将网页图谱区域从手写 SVG 布局和绘制替换为项目根目录正式安装的 `force-graph`。
- 已按项目规则读取 `node_modules/force-graph/README.md` 和 `node_modules/force-graph/dist/force-graph.d.ts`，确认可用能力包括 Canvas 渲染、节点自绘、边曲率、方向箭头、方向粒子、缩放平移、节点拖拽、节点/边点击和 d3 force 参数调整。
- 已将 `web/index.html` 的图谱容器从 `<svg>` 改为 `<div>`，并引入本地静态脚本 `web/vendor/force-graph.min.js`，避免静态网页依赖 CDN 或直接依赖发布时可能缺失的 `node_modules` 路径。
- 已在 `web/app.js` 保留原有数据构图、筛选、搜索、右侧详情和底部表格逻辑，仅替换 `renderGraph()` 的渲染层。
- 已删除上一版手写 SVG 的布局、曲线边、marker 箭头和节点/边 DOM 拼接逻辑，改为 `new ForceGraph(container)` 接收 `{ nodes, links }` 数据。
- 新图谱支持 Canvas 缩放、平移、节点拖拽、点击节点聚焦、点击节点或边更新右侧详情；有向模式下选中边显示方向箭头和方向粒子。
- 节点自绘继续优先使用音乐人头像，头像不可用时使用目标歌手蓝色、普通贡献者绿色的圆形节点兜底。
- 已配置边颜色、边宽、边曲率、连接距离、斥力和冷却参数，作词/作曲在分开显示模式下使用不同曲率和颜色，合并模式使用灰色合作边。
- 已更新 `web/styles.css`，删除旧 SVG 节点和边样式，保留图谱区域网格背景并增加 Canvas 拖拽光标。
- 已更新 `README.md`，说明静态网页图谱区域已使用本地 `force-graph` 脚本，支持缩放、平移、拖拽、点击详情和选中边方向表达。
- 已按用户偏好将修改后的 `README.md`、`web/index.html`、`web/app.js` 和 `web/styles.css` 统一为 CRLF 行尾。

### 验证 force-graph 图谱替换

- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误。
- 验证对象为 `README.md`、`web/index.html`、`web/app.js` 和 `web/styles.css` 的行尾，执行字节扫描确认不存在 LF-only 行尾。
- 验证对象为本地静态预览服务，访问 `http://127.0.0.1:8765/index.html?check=force-graph-final`、`/styles.css?v=20260511-force-graph`、`/app.js?v=20260511-force-graph`、`/vendor/force-graph.min.js` 和 `/data/catalog.json`，均返回 HTTP 200。
- 验证对象为网页入口和样例数据协议，执行 Node 脚本确认 `web/index.html` 引入 `vendor/force-graph.min.js`，`web/app.js` 包含 `new ForceGraph(container)`，样例目标歌手周杰伦数据包含 31 个节点、34 条边且边端点有效。
- 已确认 `web/vendor/force-graph.min.js` 文件存在且大小非零，来源为项目根目录安装的 `node_modules/force-graph/dist/force-graph.min.js`。
- 未完成浏览器截图级交互验证；原因是当前会话未暴露 Browser 插件所需的 Node 执行入口，本地项目也未安装 Playwright 或 Puppeteer，且系统命令未发现可直接调用的 Chrome/Edge 可执行入口。
- 替代检查已覆盖静态入口、脚本语法、资源加载和数据适配；剩余风险是实际浏览器中的 Canvas 视觉效果、头像加载和拖拽/点击体验仍需人工打开页面或后续补充浏览器自动化验证。

### 修正目标歌手重复节点和特殊中心节点

- 用户提供截图指出周杰伦不应和另一个周杰伦相连，并明确图谱中不应存在中间节点和其他节点的区别，所有节点都应该一样。
- 已定位原因：旧数据导出脚本为每个目标歌手生成独立 `target:<slug>` 节点，同时制作人员列表中又会生成同名 `artist:*` 节点；自作词或自作曲关系因此被画成“周杰伦 -> 周杰伦”的两节点连线。
- 已修改 `music_metadata_graph/pipelines/export_web_dataset.py`，目标歌手节点改用普通 artist 身份键，优先使用平台 mid 生成 `artist:<mid>`，不再生成 `target:*` 节点。
- 已修改导出逻辑：当制作人员姓名或 mid 与目标歌手一致时，计入 `self_lyricist_songs` 或 `self_composer_songs` 统计，但不再生成自环可视化边。
- 已修改 `web/app.js`，增加旧数据兼容映射：若静态 JSON 仍含旧 `target:*` 节点，前端会把它折叠到同名或同 mid 的 artist 节点，并过滤 source 与 target 相同的边。
- 已取消目标歌手的视觉特殊待遇，所有音乐人节点统一使用相同半径、相同颜色、相同标签规则和相同力导向参数；`is_target` 仅保留为范围和统计字段，不参与节点视觉表达。
- 已重新导出 `web/data/catalog.json`、`zhoujielun.json`、`xuezhiqian.json` 和 `linjunjie.json`，三位目标歌手均不再产生独立 target 节点。
- 已更新 `web/index.html` 资源版本号为 `20260511-equal-artist-nodes`，避免浏览器继续使用旧缓存。
- 已更新 `README.md`，说明图谱中所有音乐人节点按同一视觉规则绘制，目标歌手不会作为特殊中心节点或独立重复节点出现。
- 已按用户偏好将修改后的 `README.md`、`music_metadata_graph/pipelines/export_web_dataset.py`、`web/index.html`、`web/app.js` 和重新导出的静态 JSON 统一为 CRLF 行尾。

### 验证目标歌手节点统一修复

- 验证对象为 `music_metadata_graph/pipelines/export_web_dataset.py`，执行项目指定 Conda Python 的 `py_compile`，未报语法错误。
- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误。
- 验证对象为重新导出的三个目标歌手静态数据，执行 Node 断言确认 `zhoujielun.json`、`xuezhiqian.json` 和 `linjunjie.json` 均不存在 `type=target` 或 `target:*` 节点，均不存在自环边，且目标歌手姓名节点数量均为 1。
- 验证对象为周杰伦图谱数据，确认周杰伦唯一节点为 `artist:0025NhlN2yWrP4`，节点类型为 `artist`，有 32 条其他贡献者指向该节点的边，且自环边数量为 0。
- 验证对象为本地静态预览服务，访问 `http://127.0.0.1:8765/index.html?check=equal-artist-nodes`、`/styles.css?v=20260511-equal-artist-nodes`、`/app.js?v=20260511-equal-artist-nodes` 和 `/data/zhoujielun.json`，均返回 HTTP 200。
- 验证对象为修改文件行尾，执行字节扫描确认 `README.md`、导出脚本、网页入口、网页脚本、样式和三个静态 JSON 均不存在 LF-only 行尾。
- 静态搜索确认 `web/app.js` 中仍保留 `is_target` 兼容和范围保留逻辑，但不再用于节点颜色、半径、标签显示或力参数；`#2458c7` 仅用于选中描边和页签按钮，不再用于目标节点填充色。
- 当前仍未完成浏览器截图级视觉验证；原因同前，当前会话缺少可用浏览器自动化执行入口。替代检查已确认数据层和前端逻辑层不会再生成两个周杰伦节点或目标歌手特殊视觉分支。

### 更新 Node 依赖提交边界

- 提交前检查发现 `node_modules/` 作为本地安装目录出现在未跟踪文件中，不应作为仓库源码提交。
- 已将 `node_modules/` 加入 `.gitignore`，提交边界保留 `package.json`、`package-lock.json` 和 `web/vendor/force-graph.min.js`，用于记录依赖来源并保证静态网页可直接加载本地 vendor 脚本。
- 本次边界调整不改变网页功能，只影响 Git 提交范围和后续工作区状态。

### 记录提交后新增工作区改动处理规则

- 用户新增提交后工作区检查规则：提交后若发现工作区多出了刚刚没有的改动，不需要继续处理，只需要报告。
- 已明确该类改动通常视为刚刚新做的后续改动，与刚刚提交的内容无关。
- 已将该规则同步到 `AGENTS.md` 的提交规则中，后续提交后复核若出现新改动，默认只报告剩余改动，不继续处理或追加提交，除非用户明确要求。

### 修正关系支撑歌曲数筛选默认值和文案

- 用户指出网页控件“最小歌曲数”表述不清，且默认值应为 1 而不是 2。
- 已将 `web/index.html` 中控件文案改为“关系至少支撑歌曲数”，明确该输入筛选的是每条关系边背后的支撑歌曲数量。
- 已将 `web/index.html` 输入框默认值和 `web/app.js` 中 `state.minCount` 默认值统一改为 1，默认图谱不再隐藏只由 1 首歌曲支撑的关系边。
- 已更新 `web/index.html` 的前端脚本版本号，降低浏览器缓存旧脚本导致默认值仍为 2 的风险。

### 压缩网页顶部说明和统计卡片高度

- 用户提供截图指出顶部“当前数据源 / 范围切换”和统计卡片两行高度过高，导致图谱位置太靠下。
- 目标效果为在不改变数据、筛选逻辑和图谱绘制逻辑的前提下，压缩顶部两行信息卡占用的首屏高度，让图谱区域更早出现。
- 已修改 `web/styles.css`：页面主体间距从 14px 收紧为 10px，数据源说明卡最小高度从 58px 降为 44px，统计卡最小高度从 70px 降为 54px，并同步减小卡片内边距、行距和卡片间距。
- 已修改 `web/index.html` 的样式资源版本号为 `20260511-compact-top-cards`，降低浏览器继续加载旧 CSS 缓存的风险。
- 已按用户偏好将 `web/index.html` 和 `web/styles.css` 统一为 CRLF 行尾。

### 验证顶部卡片高度压缩

- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误；本次未修改脚本逻辑，但用该检查确认页面现有脚本仍可解析。
- 验证对象为本地静态预览服务，访问 `http://127.0.0.1:8765/index.html?check=compact-top-cards` 返回 HTTP 200，且 HTML 包含 `styles.css?v=20260511-compact-top-cards`。
- 验证对象为版本化样式资源，访问 `http://127.0.0.1:8765/styles.css?v=20260511-compact-top-cards` 返回 HTTP 200，且内容包含新的 `min-height: 44px`、`min-height: 54px` 和 `padding: 10px 14px 14px`。
- 验证对象为修改文件行尾，执行字节扫描确认 `web/index.html` 和 `web/styles.css` 均不存在 LF-only 行尾。
- 当前仍未完成浏览器截图级视觉验证；原因是当前会话没有暴露 Browser 插件所需的 Node 执行工具。替代检查已确认静态入口和样式资源加载到新版本，实际视觉位置仍需在浏览器中刷新页面查看。

## 2026-05-12

### 将目标歌手选择框改为勾选框

- 用户要求把网页顶部“目标歌手”选择框改成勾选框，并提供全选和反选功能。
- 已修改 `web/index.html`，将原 `select#target-select` 替换为目标歌手勾选列表、全选按钮和反选按钮。
- 已修改 `web/app.js`，将目标歌手筛选状态从单个 `currentTarget` 改为 `currentTargets` 集合，默认选中全部目标歌手；图谱、统计、详情和表格按当前勾选集合过滤。
- 已修改共同合作者范围逻辑：单个目标歌手时仍显示与其他目标歌手共享的合作者；多个非全量目标歌手时按勾选范围内的目标歌手计算。
- 已修改 `web/styles.css`，补充目标歌手勾选框、全选/反选按钮和滚动列表样式。

### 记录目标歌手勾选框修改未验证

- 用户明确要求修改后不需要验证，因此本次未运行构建、脚本语法检查、浏览器预览或自动化测试。
- 已进行代码定位和差异查看以控制改动范围，但未将其作为功能验证结果。
- 剩余风险是实际浏览器中的顶部控件布局、勾选交互和图谱刷新效果仍需用户打开网页后确认。

### 纠正目标歌手筛选控件形态

- 用户指出上一版把目标歌手勾选框直接铺在工具栏中不符合预期，正确目标是保留下拉菜单筛选形态，为后续全量歌手列表做准备。
- 已修改 `web/index.html`，将目标歌手控件改为下拉按钮，默认只显示当前选择摘要；展开后显示全选、反选和歌手勾选列表。
- 已修改 `web/app.js`，增加目标歌手下拉菜单的展开、收起、外部点击关闭和 Escape 关闭逻辑，并保持多选筛选集合不变。
- 已修改 `web/styles.css`，将目标歌手勾选列表改为绝对定位下拉面板，限制面板高度并允许滚动，以兼容后续更多目标歌手。
- 用户仍要求本次修改后不需要验证，因此未运行构建、脚本语法检查、浏览器预览或自动化测试。

### 调整目标歌手下拉列表排序和列数

- 用户要求目标歌手下拉菜单中的勾选项改为单列，并按热门排行榜排序。
- 已修改 `web/styles.css`，将目标歌手下拉菜单内的勾选列表从双列改为单列。
- 已修改 `web/app.js`，目标歌手列表渲染、全选、反选和筛选范围统一通过排序后的 catalog 目标列表生成，排序优先使用 `hot_rank`、`discovery_rank` 或 `hot_discovery_rank` 字段。
- 已修改 `web/data/catalog.json`，为当前三位目标歌手补充 `hot_rank` 字段，以支持当前页面按热门榜顺序显示。
- 已修改 `music_metadata_graph/pipelines/export_web_dataset.py`，默认导出参数包含当前三位歌手的热门榜顺序，并兼容 `slug=name=mid=directory=hot_rank` 输入格式，避免重新导出后排名字段丢失。
- 用户前序已要求这组 UI 修改不需要验证，因此本次未运行构建、脚本语法检查、浏览器预览或自动化测试。

### 调整顶部说明和统计卡为单行布局

- 用户提供截图要求将顶部两行卡片中的文字改成一行，并将两行卡片改成一行。
- 已修改 `web/styles.css`：页面主体改为两列网格，左侧承载“当前数据源 / 范围切换”说明卡，右侧承载 6 个统计指标卡；图谱工作区和数据表继续跨全宽显示。
- 已修改说明卡内部布局为横向排列，标题与说明文字在同一行显示，长说明使用省略号避免撑破容器。
- 已修改统计指标卡内部布局为横向排列，指标名称和数值在同一行显示，6 个统计卡在桌面宽度下保持同一行。
- 已更新 `web/index.html` 的 CSS 资源版本号为 `20260512-single-row-cards`，降低浏览器继续加载旧样式缓存的风险。

### 验证顶部卡片单行布局修改

- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误；本次未修改脚本逻辑，但确认现有页面脚本仍可解析。
- 验证对象为 `web/index.html` 和 `web/styles.css`，执行静态断言确认 HTML 已引用 `styles.css?v=20260512-single-row-cards`，样式中包含页面两列网格、说明卡横向布局、指标卡横向布局和图谱区域跨全宽规则。
- 验证对象为 `web/index.html`、`web/styles.css` 和 `develop_log.md` 的行尾，已按用户偏好统一为 CRLF。
- 当前未完成浏览器截图级视觉验证；原因是当前会话未暴露 Browser 插件可调用工具。替代检查已确认入口资源版本和关键布局规则已生效，实际首屏视觉仍需在浏览器刷新页面确认。

### 修正顶部单行布局横向溢出

- 用户提供截图指出上一版顶部布局不合理，右侧统计卡被挤出视口，属于单行压缩过度导致的横向溢出。
- 已修改 `web/styles.css`：页面顶部主网格从固定比例两列改为“说明区域弹性 + 指标区域自适应内容宽度”，避免指标区域在桌面宽度下继续被压缩或溢出。
- 已将 6 个统计卡改为紧凑固定范围列，指标标题禁止拆行，卡片高度进一步压缩为 44px。
- 已新增 1320px 响应式断点：可用宽度不足时说明卡和统计卡自动回到上下两行，优先保证不横向溢出。
- 已更新 `web/index.html` 的 CSS 资源版本号为 `20260512-balanced-top-cards`，降低浏览器缓存旧布局的风险。

### 验证顶部布局溢出修正

- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误；本次未修改脚本逻辑，但确认页面脚本仍可解析。
- 验证对象为 `web/index.html` 和 `web/styles.css`，执行静态断言确认 HTML 已引用 `styles.css?v=20260512-balanced-top-cards`，样式中包含弹性说明列、紧凑 6 列指标卡、1320px 响应式断点和标题不换行规则。
- 验证对象为 `web/index.html`、`web/styles.css` 和 `develop_log.md` 的行尾，字节扫描确认 LF-only 数量均为 0。
- 当前仍未完成浏览器截图级视觉验证；剩余风险是实际浏览器中不同缩放比例下的卡片宽度观感，需要用户刷新页面后确认。

### 将顶部信息区改为状态栏

- 用户再次提供截图指出上一版虽然未截断，但 8 个独立卡片横向排列仍然视觉割裂、比例不合理。
- 已修改 `web/index.html`：将“当前数据源 / 范围切换”和统计指标共同包入 `top-summary-bar`，从结构上改为一条顶部状态栏。
- 已修改 `web/styles.css`：左侧说明区保留两段信息但去掉独立卡片外框，仅用竖线分隔；右侧统计指标去掉独立卡片边框，改为轻量数值组。
- 状态栏桌面布局为左侧说明弹性展开、右侧指标按内容宽度靠右显示；1320px 以下自动拆成上下两行，1050px 以下统计指标改为三列网格，620px 以下改为两列网格。
- 已更新 `web/index.html` 的 CSS 资源版本号为 `20260512-top-status-bar`，降低浏览器缓存旧布局的风险。

### 验证顶部状态栏修改

- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误；本次未修改脚本逻辑，但确认页面脚本仍可解析。
- 验证对象为 `web/index.html` 和 `web/styles.css`，执行静态断言确认 HTML 包含 `top-summary-bar`，并引用 `styles.css?v=20260512-top-status-bar`。
- 验证对象为 `web/styles.css`，执行静态断言确认存在状态栏容器、左侧弹性说明列、右侧 flex 指标组、轻量指标项和分隔线样式。
- 当前仍未完成浏览器截图级视觉验证；剩余风险是实际浏览器中状态栏的字重、间距和换行断点仍需人工刷新页面确认。

### 定位连线方向可见性不足

- 用户反馈网页中“连线方向”控件看不出明显区别。
- 已定位当前 `web/app.js` 的实现：有向模式下只有选中某条边时才显示方向箭头和流动粒子，未选中状态下普通边和无向模式视觉差异很弱。
- 当前数据边本身仍有方向语义，表示贡献者到目标歌手的关系，例如“作词/作曲人 -> 演唱该歌曲的目标歌手”；切换为无向主要是弱化方向，只把两人视为存在合作关系。
- 已识别用户体验缺口：如果用户不点击边，几乎无法感知“有向/无向”的区别；后续应考虑在有向模式下默认显示更轻量的箭头、在说明文案中明确方向含义，或将控件改名为“显示贡献方向”。

### 改为有向模式默认显示方向粒子

- 用户明确有向模式不应只在选中边时显示方向，且不需要箭头，方向由流动粒子表达。
- 已修改 `web/app.js`：`linkDirectionalArrowLength` 固定为 `0`，不再显示箭头；`linkDirectionalParticles` 在有向模式下对所有边返回 `1`，在无向模式下返回 `0`。
- 已修改 `web/index.html`，将脚本资源版本号更新为 `20260512-directed-particles`，降低浏览器继续加载旧脚本缓存的风险。
- 已修改 `README.md`，说明有向模式下所有边直接显示流动粒子，粒子流动方向表示贡献关系方向，不额外显示箭头。

### 验证有向粒子显示修改

- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误。
- 验证对象为 `web/index.html`，执行静态断言确认入口已引用 `app.js?v=20260512-directed-particles`。
- 验证对象为 `web/app.js`，执行静态断言确认箭头长度固定为 `0`，方向粒子只由 `state.directionMode === "directed"` 控制，不再依赖 `selectedEdgeId()`。
- 验证对象为 `README.md`，执行静态断言确认文档已包含“流动粒子”和“不额外显示箭头”的说明。
- 当前未完成浏览器截图级视觉验证；剩余风险是不同边数和缩放比例下粒子密度的观感需要在浏览器中刷新页面确认。

### 纠正网页数据展示范围为完整作词作曲歌曲

- 用户指出网页使用数据有问题，应该只使用作词和作曲信息齐全的数据，因此不需要显示隔离条目或数据质量信息。
- 已复核现有采集流程，确认 `collect_singer_songs.py` 默认已经把缺作词或缺作曲歌曲从 `songs_kept` 剔除，网页数据问题主要来自导出脚本和页面仍展示 `songs_credit_incomplete` 的统计与质量页签。
- 已修改 `music_metadata_graph/pipelines/export_web_dataset.py`，网页静态 JSON 只从 `songs_kept.json` 导出图谱、歌曲明细、summary 和 catalog，不再读取或输出 `songs_credit_incomplete.json`、`credit_incomplete` 或 `quality` 字段。
- 已修改 `web/app.js`，顶部范围说明、统计条和表格渲染不再显示“制作人员不完整条目已隔离”“隔离条目”或数据质量表。
- 已修改 `web/index.html`，移除“数据质量”页签，并更新 CSS/JS 资源版本号为 `20260512-complete-credits-only`。
- 已更新 `README.md`，说明网页只使用 `songs_kept` 中作词和作曲都齐全的歌曲；缺作词或缺作曲文件仅作为本地调试输出。
- 已重新导出 `web/data/catalog.json`、`zhoujielun.json`、`xuezhiqian.json` 和 `linjunjie.json`；导出汇总为 3 位目标歌手、566 首作词作曲齐全歌曲、183 个唯一节点和 9 个共同合作者。
- 本轮不改变采集端保留本地调试文件的行为，不删除 `songs_credit_incomplete.json/csv` 输出能力。

### 验证完整作词作曲网页数据导出

- 验证对象为 `music_metadata_graph/pipelines/export_web_dataset.py`，执行项目指定 Conda Python 的 `py_compile`，未报语法错误。
- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误。
- 验证对象为 `web/data/*.json`，重新导出后扫描确认网页静态数据不再包含 `quality` 或 `credit_incomplete` 字段。
- 验证对象为网页歌曲明细数据，执行 Python 断言检查 `web/data/zhoujielun.json`、`xuezhiqian.json` 和 `linjunjie.json` 的 566 首歌曲，结果显示缺作词或缺作曲歌曲数量为 0。
- 静态搜索确认 `web/app.js`、`web/index.html` 和导出脚本中不再包含“隔离”“数据质量”“制作人员不完整”等网页展示逻辑；README 中仅保留本地调试输出说明。
- 已按用户偏好将本轮修改的 Python、JavaScript、HTML、Markdown 和重新导出的 JSON 文件统一为 CRLF 行尾。
- 当前未完成浏览器截图级视觉验证；剩余风险是用户浏览器缓存旧资源时可能仍看到旧页签，已通过更新入口资源版本号降低该风险。

### 降低有向边粒子动画速度

- 用户反馈网页图谱中的粒子动画太快。
- 已定位粒子动画由 `web/app.js` 中 `force-graph` 的有向边粒子配置控制，当前有向模式下每条边显示 1 个流动粒子。
- 已修改 `web/app.js`：新增 `directedParticleSpeed = 0.003`，并通过 `linkDirectionalParticleSpeed(directedParticleSpeed)` 显式设置粒子速度，约为 `force-graph` 默认值的三成。
- 已更新图谱说明中的布局版本标记为 `slow-particles-20260512`，便于刷新页面后确认加载到新脚本。
- 已修改 `web/index.html`，将脚本资源版本号更新为 `20260512-slow-particles`，降低浏览器继续加载旧脚本缓存的风险。
- 本轮不改动有向/无向切换逻辑、不改动粒子数量、不改动数据导出和静态 JSON。

### 验证有向边粒子速度调整

- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误。
- 验证对象为 `web/app.js`，执行静态断言确认存在 `slow-particles-20260512`、`directedParticleSpeed = 0.003` 和 `linkDirectionalParticleSpeed(directedParticleSpeed)`。
- 验证对象为 `web/index.html`，执行静态断言确认入口已引用 `app.js?v=20260512-slow-particles`。
- 当前未完成浏览器截图级视觉验证；剩余风险是粒子速度主观观感仍需在浏览器刷新页面后确认。

### 将顶部右侧控制面板改为单行

- 用户提供截图要求把顶部栏右半部分控制面板改成单行，目标效果为“数据集、目标歌手、视图、职能显示、连线方向、关系至少支撑歌曲数”在桌面宽度下同一水平行对齐。
- 已修改 `web/styles.css`：顶部栏改为垂直居中，右侧 `.toolbar` 在桌面端使用不换行横向布局，控件标签和输入控件从上下两行改为左右同排。
- 已为目标歌手下拉、视图、职能显示、连线方向和最小歌曲数设置稳定宽度或弹性约束，避免单行后控件互相挤压。
- 已保留 1280px、1050px 和 620px 响应式断点：宽度不足时允许换行或改为单列，避免移动端横向溢出。
- 已修改 `web/index.html` 的 CSS 资源版本号为 `20260512-single-line-toolbar`，降低浏览器继续加载旧样式缓存的风险。
- 本轮不改变目标歌手筛选逻辑、视图切换逻辑、图谱绘制逻辑和静态数据。

### 验证顶部右侧控制面板单行修改

- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误；本次未修改脚本逻辑，但确认页面现有脚本仍可解析。
- 验证对象为 `web/index.html` 和 `web/styles.css`，执行静态断言确认入口已引用 `styles.css?v=20260512-single-line-toolbar`，样式中包含工具栏不换行、控件行内 flex、桌面断点和目标歌手下拉弹性约束。
- 验证对象为本地静态预览服务，访问 `http://127.0.0.1:8765/index.html?check=single-line-toolbar`、`/styles.css?v=20260512-single-line-toolbar`、`/app.js?v=20260512-slow-particles` 和 `/data/catalog.json`，均返回 HTTP 200。
- 当前未完成浏览器截图级视觉验证；原因是当前会话没有暴露 Browser 插件所需的 Node 执行工具。替代检查已确认入口资源和关键布局规则已生效，实际视觉仍需在浏览器刷新页面后确认。

### 压缩顶部筛选控件并移除重复状态栏

- 用户指出顶部筛选控件仍过宽、过高，数据集框无实际操作价值，下一行状态卡大量重复信息。
- 已修改 `web/index.html`：移除顶部“数据集”框和主体第一行状态卡，只保留标题范围说明、图谱区、详情区和数据表。
- 已将“职能显示”的合并选项文案从“合并为合作次数”改为“不区分职能”，避免误解为双向合作关系被合并。
- 已将“连线方向”下拉改为“粒子效果”开关，开关只控制边上的流动粒子是否显示，不再展示有向/无向下拉。
- 已将“关系至少支撑歌曲数”改为“显示阈值”，并缩短数值输入框宽度。
- 已修改 `web/styles.css`：降低 select、input、button 的高度和内边距，缩短目标歌手、视图、职能显示和阈值控件宽度，让控件高度更接近文字高度。
- 已修改 `web/app.js`：移除已删除状态卡相关 DOM 写入，并把粒子显示逻辑从 `directionMode` 改为 `particlesEnabled`。

### 修正目标歌手筛选菜单并自适应图谱高度

- 用户指出目标歌手筛选菜单样式和宽度仍不同于普通下拉，并要求增加搜索栏筛选候选项。
- 已修改 `web/index.html`：在目标歌手下拉面板顶部增加 `target-filter-search` 搜索输入框。
- 已修改 `web/app.js`：新增 `targetFilterSearch` 状态，搜索目标歌手时只过滤下拉候选项，不改变当前勾选集合；未匹配时显示“没有匹配的目标歌手”。
- 已修改 `web/styles.css`：目标歌手下拉按钮宽度固定为 150px，下拉面板与按钮同宽并右对齐，搜索框、全选/反选按钮和勾选项使用同一套紧凑控件样式。
- 已将图谱高度从按节点数量估算改为按当前视口计算：使用图谱容器顶部到 `window.innerHeight` 的剩余高度，让打开页面时图谱区域贴近屏幕底部，不再把页面撑得过高。
- 已增加窗口 resize 时重新渲染图谱，保证浏览器高度变化后画布高度同步调整。
- 已更新 `web/index.html` 的 CSS/JS 资源版本号为 `20260512-filter-search-fit-graph`，降低浏览器继续加载旧资源缓存的风险。

### 验证筛选菜单和图谱高度修改

- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误。
- 验证对象为 `web/index.html`、`web/styles.css` 和 `web/app.js`，执行静态断言确认入口引用 `20260512-filter-search-fit-graph` 版本资源，目标歌手搜索输入、搜索状态、视口高度计算、resize 监听、目标歌手下拉统一宽度和旧状态卡移除均已存在。
- 静态搜索确认 `source-pill`、`top-summary-bar`、`summary-strip`、`source-description`、`source-name`、`direction-mode`、`directionMode`、`关系至少支撑歌曲数`、`合并为合作次数`、`连线方向` 等旧结构或文案不再出现在网页 HTML、CSS 和 JS 中。
- 验证对象为本地静态预览服务，访问 `http://127.0.0.1:8765/index.html?check=filter-search-fit-graph`、`/styles.css?v=20260512-filter-search-fit-graph`、`/app.js?v=20260512-filter-search-fit-graph` 和 `/data/catalog.json`，均返回 HTTP 200。
- 当前未完成浏览器截图级视觉验证；原因是当前会话没有暴露 Browser 插件所需的 Node 执行工具。替代检查已确认入口资源、核心 DOM、脚本逻辑和样式规则已生效，实际像素级视觉仍需在浏览器刷新页面后确认。

### 统一筛选控件为原生风格并限制详情栏高度

- 用户指出目标歌手筛选按钮仍与普通下拉不同，并补充“同意成原生样式，非必要不要自己实现样式”。
- 已保留原生 `select` 默认外观，不使用 `appearance: none` 或自绘 select 箭头；目标歌手因需要多选和搜索仍使用按钮加弹层，但只补回简单文本下拉符号，避免复杂自绘样式。
- 已调整目标歌手按钮和面板宽度，使其更接近当前顶部控件的原生尺寸和视觉节奏。
- 用户指出详情栏会被内容撑开，应该跟绘图区高度一样并在内部滚动。
- 已修改 `web/app.js`：图谱渲染时同步设置 `.detail-panel` 高度为图谱画布高度加图谱标题栏高度。
- 已修改 `web/styles.css`：详情栏外层隐藏溢出，`detail-content` 内部滚动，避免歌曲列表继续撑长页面。
- 已更新 `web/index.html` 的 CSS/JS 资源版本号为 `20260512-unified-controls-detail-height`，降低浏览器继续加载旧资源缓存的风险。

### 验证原生风格控件和详情栏高度限制

- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误。
- 验证对象为 `web/index.html`、`web/styles.css` 和 `web/app.js`，执行静态断言确认入口引用 `20260512-unified-controls-detail-height` 版本资源，目标歌手按钮保留文本下拉符号，详情栏高度同步逻辑和详情内容内部滚动样式均已存在。
- 静态搜索确认网页 HTML、CSS 和 JS 中没有 `appearance`、`webkit-appearance`、`moz-appearance`、`select-wrapper` 或 `custom-arrow` 等自定义原生下拉外观的规则。
- 当前未完成浏览器截图级视觉验证；原因是当前会话没有暴露 Browser 插件所需的 Node 执行工具。替代检查已确认不会覆盖原生 select 箭头，并且详情栏已有固定高度与内部滚动规则。

### 取消目标歌手按钮独立箭头区域

- 用户再次截图指出目标歌手控件仍与普通下拉不同，问题集中在右侧独立箭头区域。
- 已移除 `web/index.html` 中目标歌手按钮内单独的箭头 `span`，不再形成独立右侧小格。
- 已修改 `web/app.js`，将下拉符号并入 `target-dropdown-label` 文本末尾，避免目标歌手按钮内部布局不同于普通控件。
- 已修改 `web/styles.css`，取消目标歌手按钮的 flex 分散布局，按钮文字左对齐，保留浏览器 button 的基础外观。
- 已更新 `web/index.html` 的 CSS/JS 资源版本号为 `20260512-target-native-button`，降低浏览器继续加载旧按钮样式缓存的风险。
- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误。
- 静态断言确认目标歌手按钮中独立箭头节点已移除，标签文本末尾包含下拉符号，按钮文字左对齐规则已存在。

### 使用原生下拉作为目标歌手筛选视觉层

- 用户提出可在目标歌手位置放置原生下拉菜单作为视觉层，再用透明按钮覆盖处理点击，以兼顾原生外观和多选搜索面板。
- 已修改 `web/index.html`：在目标歌手控件中新增 `select#target-visual-select` 作为只读视觉层，并保留透明覆盖按钮打开多选面板。
- 已修改 `web/styles.css`：目标歌手视觉层使用原生 `select`，覆盖按钮绝对定位在其上方，背景和文字透明，不再自绘下拉控件外观。
- 已修改 `web/app.js`：当前目标歌手摘要同步写入 `target-visual-select` 的唯一 option，并为透明按钮设置 `aria-label`，避免可访问名称丢失。
- 已更新 `web/index.html` 的 CSS/JS 资源版本号为 `20260512-native-select-overlay`，降低浏览器继续加载旧按钮样式缓存的风险。
- 验证对象为 `web/app.js`，执行 `node --check`，未报 JavaScript 语法错误。
- 静态断言确认原生视觉 select、透明覆盖按钮、视觉文本同步、覆盖按钮可访问标签和新版资源号均已存在。

### 澄清 QQ 音乐歌手到歌曲数据流程

- 用户质疑当前数据流程是否只能通过音乐人名字搜索歌曲，并对照 QQ 音乐软件中“先搜索音乐人，再进入音乐人页查看歌曲”的路径提出疑问。
- 复核当前实现后确认，项目正式采集流程并不是“音乐人名字搜索歌曲”，而是先通过 `qqmusic.singer.get_singer_list_index` 建立歌手身份表，取得歌手 `mid`、姓名、头像等身份信息。
- 单歌手采集脚本在有 `target_singer_mid` 时直接使用该 `mid`，没有 `target_singer_mid` 时使用热门歌手列表接口取得候选歌手；随后通过 `qqmusic.singer.get_songs_list(singer_mid)` 按歌手 `mid` 分页获取歌曲列表。
- 歌曲制作人员补全继续使用 `qqmusic.song.get_producer(song_mid 或 song_id)`，因此完整主路径是“歌手身份 -> 歌手歌曲列表 -> 歌曲制作人员”，而不是“歌手名搜索歌曲”。
- 搜索接口在当前方案中的合理定位是辅助解析入口，例如用户只给出歌手名字时先搜索或候选确认出 QQ 音乐歌手 `mid`；它不应作为主采集路径，也不应直接用名字搜索歌曲替代歌手歌曲列表。
- 当前剩余缺口是用户侧入口和文档表达仍可能让人误以为需要手工知道 `mid` 或通过名字搜歌；后续若继续优化，应增加“按歌手名搜索并确认歌手身份”的小工具或页面入口，再把确认出的 `mid` 交给现有采集流程。

### 定位歌手歌曲接口返回非主页官方歌曲的原因

- 用户指出如果流程等价于 QQ 音乐客户端歌手主页歌曲页，不应返回 `安徽卫视非常静距离杰伦部分`、`土耳其进行曲` 这类明显不属于周杰伦官方歌曲的条目。
- 复核 `qqmusic-api-python` 源码后确认，当前 `collect_singer_songs.py` 使用的 `client.singer.get_songs_list(mid)` 实际请求 `musichall.song_list_server.GetSingerSongList`，参数为 `singerMid`、`order`、`number`、`begin`。
- 本地原始缓存 `data/raw/qqmusic/singer_songs/0025NhlN2yWrP4/page_0031_size_30.json` 中确实包含用户指出的两个异常条目，且原始 `songInfo.singer[0].mid` 均为周杰伦 `0025NhlN2yWrP4`；因此这些条目不是项目后处理混入，而是旧接口原始响应曾经直接返回。
- 缓存中的 `土耳其进行曲` 专辑为 `最脍炙人口的古典音乐100首`，`安徽卫视非常静距离杰伦部分` 专辑为空，二者说明旧接口更像“按歌手标记聚合的宽泛歌曲索引”，不等价于客户端歌手主页经过产品规则筛选后的官方歌曲列表。
- 进一步检查库中另一个接口 `client.singer.get_tab_detail(mid, TabType.SONG)`，该接口请求 `music.UnifiedHomepage.UnifiedHomepageSrv.GetHomepageTabDetail`，`TabID` 为 `song_sing`，从命名、参数和响应字段上更接近客户端歌手主页的“歌曲”Tab。
- 联网验证周杰伦主页 `song_sing` Tab 共翻页 34 页、检查 1012 首歌，未命中 `安徽卫视非常静距离` 或 `土耳其进行曲`。
- 联网重新扫描旧 `GetSingerSongList` 接口当前 1012 首结果时，也未命中这两个具体异常项；这说明本地缓存还叠加了平台数据已变化或旧缓存过期问题，但不改变旧缓存证据：历史采集时该接口确实返回过非主页官方歌曲。
- 当前结论是采集主流程不应继续把 `GetSingerSongList` 当作“客户端歌手主页官方歌曲列表”的等价来源；后续应优先切换到 `GetHomepageTabDetail + song_sing` 作为歌手主页歌曲来源，并将旧接口降级为补充或对照来源。

### 切换单歌手歌曲采集源到主页歌曲 Tab

- 用户要求开始切换采集源，并先采集周杰伦、薛之谦、林俊杰三位歌手的新接口全量数据，以 CSV 展示并按歌曲首字母排序，中文按拼音排序，英文中文混排。
- 已修改 `music_metadata_graph/pipelines/collect_singer_songs.py`：单歌手歌曲采集从 `client.singer.get_songs_list(mid)` 切换为 `client.singer.get_tab_detail(mid, TabType.SONG)`，并使用 `music.UnifiedHomepage.UnifiedHomepageSrv.GetHomepageTabDetail` 的 `SongTab.List` 作为歌曲来源。
- 新增 `SONG_SOURCE = qqmusic.singer.get_tab_detail.song_sing` 并写入每首歌曲的 `song_source` 字段，便于后续追溯采集源。
- 新接口原始缓存目录改为 `data/raw/qqmusic/singer_homepage_song_tab/<singer_mid>/`，避免与旧 `GetSingerSongList` 缓存混用。
- 新增 `sort_key` 字段，使用 `pypinyin.lazy_pinyin` 对歌曲名生成排序键；所有歌曲 CSV 输出按 `sort_key`、发行时间和歌曲 id/mid 排序。
- README 已同步说明默认主采集源为歌手主页歌曲 Tab，旧 `GetSingerSongList` 只作为补充或对照来源，不再作为默认主采集源。
- 本轮未执行逐首制作人员补全；三位歌手全量采集使用 `--skip-producers`，目的是先检查新接口歌曲列表本身的数据形态，避免把上千次制作人员请求混入采集源切换验证。

### 验证主页歌曲 Tab 全量采集结果

- 语法验证对象为 `music_metadata_graph/pipelines/collect_singer_songs.py`，执行项目指定 Conda 解释器的 `py_compile`，未报语法错误。
- Smoke 验证对象为周杰伦主页歌曲 Tab 第 1 页，采集 30 条歌曲，初过滤后保留 26 条、过滤 4 条，并对前 3 首请求制作人员，3 首均返回 `ok`，作词和作曲字段均非空。
- 全量采集周杰伦：主页歌曲 Tab 返回 1012 行，初过滤后保留 240 行，过滤 772 行，输出到 `data/processed/singer_songs_homepage/zhoujielun/`。
- 全量采集薛之谦：主页歌曲 Tab 返回 528 行，初过滤后保留 127 行，过滤 401 行，输出到 `data/processed/singer_songs_homepage/xuezhiqian/`。
- 全量采集林俊杰：主页歌曲 Tab 返回 1013 行，初过滤后保留 266 行，过滤 747 行，输出到 `data/processed/singer_songs_homepage/linjunjie/`。
- 已生成三位歌手合并 CSV `data/processed/singer_songs_homepage/three_singers_songs_all_sorted.csv`，共 2553 行，按歌手和拼音排序键排序，便于按歌手查看新接口全量返回。
- 已生成三位歌手全局混排 CSV `data/processed/singer_songs_homepage/three_singers_songs_all_global_sorted.csv`，共 2553 行，不按歌手分组，直接按歌曲拼音/英文排序键混排。
- 验证对象为每位歌手的 `songs_all.csv`、`songs_kept.csv`、`songs_filtered.csv` 和合并 CSV，检查结果显示文件均存在且非空、UTF-8 可读、包含 `sort_key` 和 `song_source` 字段。
- 新接口全量结果中仍出现用户点名的异常项：`安徽卫视非常静距离杰伦部分` 被 `name_title_mismatch` 过滤，`土耳其进行曲` 仍进入 `songs_kept`；因此接口切换降低了来源语义风险，但不能单独解决“官方歌曲”定义，后续需要继续增强专辑归属、空专辑、古典合集和非原创/非主唱条目的过滤或验证规则。

### 对比周杰伦两个歌手歌曲接口全量结果

- 用户质疑 `songs_all` 是否混入旧数据，并指出新结果中仍包含 `安徽卫视非常静距离杰伦部分`，要求分别全量请求两个接口对比差异。
- 已绕开现有缓存，实时全量请求周杰伦旧接口 `musichall.song_list_server.GetSingerSongList` 和主页歌曲 Tab 接口 `music.UnifiedHomepage.UnifiedHomepageSrv.GetHomepageTabDetail`，两者均按 30 条分页完整请求 34 页。
- 对比结果显示旧接口返回 1012 行、主页歌曲 Tab 返回 1012 行；按歌曲 `mid/id` 建立唯一 key 后，旧接口唯一 key 为 1012 个，主页歌曲 Tab 唯一 key 为 1012 个，两者交集为 1012 个，旧接口独有 0 个，主页 Tab 独有 0 个。
- 因此 `songs_all` 中出现 `安徽卫视非常静距离杰伦部分` 不是旧数据混入，而是主页歌曲 Tab 接口实时返回的原始全量数据本身包含该条目。
- 两个接口的主要差异不是歌曲集合，而是分页排序位置不同：例如 `土耳其进行曲` 在旧接口第 31 页第 9 行，在主页 Tab 第 5 页第 7 行；`安徽卫视非常静距离杰伦部分` 在旧接口第 31 页第 14 行，在主页 Tab 第 20 页第 5 行。
- 已生成对比输出目录 `data/processed/interface_compare/zhoujielun/`，其中包括两个接口全量 CSV、两个独有集合 CSV、共有歌曲位置对比 CSV 和 `summary.json`。
- 当前结论修正为：切换到主页歌曲 Tab 不能解决异常条目问题，因为两个接口当前返回的周杰伦歌曲集合完全一致；后续应把重点转向业务过滤规则和“官方歌曲”判定，而不是继续寻找这两个接口之间的数据集合差异。

### 梳理可用于歌曲和专辑请求的 QQ 音乐接口

- 用户要求继续查找是否还有其他接口可能有用，并先列出能用来请求歌曲或专辑的所有接口并分析。
- 本轮依据本地已安装的 `qqmusic-api-python` 源码梳理，重点查看 `modules/song.py`、`modules/album.py`、`modules/singer.py`、`modules/search.py`、`modules/top.py`、`modules/songlist.py`、`modules/recommend.py` 以及对应模型文件。
- 可直接返回目标歌手歌曲集合的接口包括 `singer.get_songs_list(mid)` 和 `singer.get_tab_detail(mid, TabType.SONG)`；前一轮已验证二者对周杰伦当前返回集合完全一致，不能单独解决异常条目问题。
- 歌手主页 Tab 还支持 `COMPOSER`、`LYRICIST`、`PRODUCER`、`ARRANGER`、`MUSICIAN` 等角色型歌曲 Tab；这些接口可能用于补充“该歌手参与创作/制作的歌曲”，但不能直接当作“该歌手演唱的官方歌曲”来源。
- 专辑相关接口包括 `singer.get_album_list(mid)`、`singer.get_tab_detail(mid, TabType.ALBUM)`、`album.get_detail(album_id/mid)` 和 `album.get_song(album_id/mid)`；其中专辑详情的专辑署名歌手、专辑类型、发行公司、发行日期和专辑歌曲列表对判定官方歌曲最有用。
- 歌曲相关接口包括 `song.query_song(ids/mids)`、`song.get_detail(id/mid)`、`song.get_other_version(id/mid)`、`song.get_producer(id/mid)`、`song.get_labels(songid)`、`song.get_similar_song(songid)`、`song.get_sheet(mid)`、`song.get_fav_num(song_ids)`；其中歌曲详情、制作人员、其他版本和标签对过滤规则有辅助价值，推荐/相似/收藏数不适合作为官方归属依据。
- 搜索接口包括 `search.search_by_type(keyword, SearchType.SONG/ALBUM/SINGER)` 和 `search.general_search(keyword)`；搜索专辑结果模型包含 `album_type`，注释指出通常 `1` 代表正规专辑，可作为候选专辑筛选或交叉验证，但搜索接口不适合做全量主采集。
- 排行榜、新歌推荐、歌单详情等接口能返回歌曲列表，但来源语义是榜单、推荐或用户歌单，不适合判定某个歌手的官方作品，只适合发现样本或交叉热度信息。
- 当前分析结论是：后续最有价值的路线不是再换一个单一歌曲列表接口，而是以歌手专辑列表和专辑详情/专辑歌曲列表作为官方作品验证主链路，再用歌曲详情、制作人员、其他版本和标签作为辅助证据。

### 探查汪苏泷歌手专辑列表返回形态

- 用户指出部分歌手作品首发语境可能就是综艺或 Live，例如“我是唱作人”，不能简单按 Live 或节目专辑一刀切过滤，并要求先用汪苏泷请求全量歌手专辑列表。
- 使用汪苏泷 QQ 音乐歌手 `mid=001z2JmX09LLgL` 请求 `client.singer.get_album_list(mid)`，按每页 30 条完整请求 4 页，接口返回总数 117，实际落盘 117 条。
- 输出目录为 `data/processed/album_probe/wangsulong/`，包含 `wangsulong_singer_album_list.csv`、`wangsulong_singer_album_list.json` 和 `summary.json`；原始缓存保存到 `data/raw/qqmusic/album_probe/wangsulong/singer_album_list/`。
- 专辑类型分布为：`Single` 77 条、`录音室专辑` 33 条、`演唱会` 5 条、`EP` 1 条、`人声音频` 1 条。
- 歌手专辑列表中包含普通录音室专辑、单曲、影视原声带、多人合集、演唱会、品牌活动/现场类专辑和人声音频；例如 `爱你 影视原声带`、`风起洛阳 影视原声带`、`登陆星球2016演唱会`、`就让这大雨全都落下 (Live)`、`雀巢咖啡1+2唤醒大咖秀 郁可唯汪苏泷专场`。
- 当前汪苏泷歌手专辑列表未检索到专辑名包含 `我是唱作人` 的条目；这说明综艺首发作品不一定会通过歌手专辑列表以节目名专辑形式出现，后续还需要结合歌曲列表、专辑详情、搜索专辑和歌曲制作人员验证。
- 本轮发现 `album_type=演唱会` 的条目可能既包含个人演唱会，也包含活动现场或合作现场；因此不能简单把 `演唱会` 或 `Live` 全部判为噪声，需要看目标歌手是否为专辑署名歌手、歌曲是否为该歌手演唱、制作人员是否匹配，以及是否属于明确节目/现场首发作品。

### 采集三位歌手全量专辑列表

- 用户要求继续用周杰伦、薛之谦、林俊杰请求全量歌手专辑列表查看结果。
- 使用 `client.singer.get_album_list(mid)` 分别请求三位歌手，每页 30 条，输出到 `data/processed/album_probe/three_singers/`，原始缓存写入 `data/raw/qqmusic/album_probe/three_singers/`。
- 周杰伦专辑列表返回 43 条，类型分布为 `录音室专辑` 18、`Single` 16、`演唱会` 7、`EP` 2；专辑署名包含目标歌手的数量为 43，多歌手专辑 4。
- 薛之谦专辑列表返回 32 条，类型分布为 `Single` 17、`录音室专辑` 14、`演唱会` 1；专辑署名包含目标歌手的数量为 32，多歌手专辑 4。
- 林俊杰专辑列表返回 76 条，类型分布为 `Single` 48、`录音室专辑` 18、`EP` 5、`演唱会` 5；专辑署名包含目标歌手的数量为 76，多歌手专辑 20。
- 三位歌手的歌手专辑列表均未命中 `声生不息`、`歌手`、`我是唱作人`、`综艺` 等关键词；这进一步说明歌手专辑列表适合作为高可信个人/署名专辑来源，但不能覆盖音乐综艺节目专辑。
- 已生成每位歌手的 `singer_album_list.csv/json`、`summary.json` 和合并表 `three_singers_album_list.csv`；验证确认文件存在、大小非零、UTF-8 可读，合并表共 151 行。

### 核对四位歌手高可信歌曲子集采集状态

- 用户反馈采集过程中程序卡死并重启电脑，要求检查周杰伦、薛之谦、林俊杰、汪苏泷四位歌手的高可信歌曲子集是否请求完整。
- 检查 `data/processed/high_confidence_singer_songs/summary.json`，汇总结果存在，生成时间为 `2026-05-12T18:21:32.562260+00:00`，记录歌手数 4、去重后高可信歌曲总数 1062。
- 周杰伦结果完整：歌手专辑列表 43 条，按 `Single`、`EP`、`录音室专辑` 保留 36 张专辑，原始专辑歌曲缓存目录 36 个，高可信歌曲 CSV 225 行。
- 薛之谦结果完整：歌手专辑列表 32 条，按规则保留 31 张专辑，原始专辑歌曲缓存目录 31 个，高可信歌曲 CSV 154 行。
- 林俊杰结果完整：歌手专辑列表 76 条，按规则保留 71 张专辑，原始专辑歌曲缓存目录 71 个，高可信歌曲 CSV 321 行。
- 汪苏泷结果完整：歌手专辑列表 117 条，按规则保留 111 张专辑，原始专辑歌曲缓存目录 111 个，高可信歌曲 CSV 362 行。
- 四位歌手单人 `songs_high_confidence.csv/json`、`album_song_rows_kept_before_dedupe.csv/json`、`album_song_rows_rejected.csv/json`、`albums_included.csv/json`、`albums_excluded.csv/json` 和 `summary.json` 均存在且非空。
- 汇总 CSV `four_singers_high_confidence_songs.csv` 存在且非空，行数为 1062，等于四位歌手单人高可信歌曲数之和，说明汇总未缺歌手、未出现汇总行数缺口。

### 分析高可信采集超时原因

- 首次高可信歌曲子集采集命令在外层执行工具等待约 245 秒后返回超时状态，属于本地执行工具的等待上限触发；该状态本身不是 QQ 音乐接口返回的封禁、限流或鉴权失败证据。
- 本轮采集需要请求四位歌手的专辑列表和 249 张保留专辑的歌曲列表，且脚本使用低频请求策略，因此运行时间超过 4 分钟属于可解释范围。
- 电脑重启前已经落盘四位歌手的原始缓存、单人结果和汇总结果；当前没有残留 Python 采集进程。
- 当前未发现接口封禁证据：没有观察到 HTTP 鉴权失败、封禁提示、连续空响应或脚本异常退出留下的半成品结果；相反，四位歌手的专辑数、原始缓存目录数、单人 CSV 行数和汇总 CSV 行数都能对齐。
- 剩余风险是脚本当前缺少结构化运行日志，无法精确复盘每个接口请求的耗时和最后一个成功请求；后续若继续扩展采集，建议增加每页/每专辑请求耗时、重试次数和异常摘要日志。

### 规范高可信歌曲 CSV 列名来源

- 用户指出整理 CSV 时不应增加或修改接口键名，列名只能是请求得到的键名或明确的辅助键，并质疑 `confidence` 不是有用的辅助键。
- 已修改 `music_metadata_graph/pipelines/collect_high_confidence_singer_songs.py`：歌曲 CSV 的非辅助列改为 QQ 音乐 `album.get_song` 歌曲响应顶层键，例如 `id`、`type`、`mid`、`name`、`title`、`subtitle`、`singer`、`album`、`time_public`、`file`、`pay`、`action` 等。
- 已修改专辑 CSV 的非辅助列为 QQ 音乐 `singer.get_album_list` 专辑响应顶层键，例如 `albumMid`、`albumName`、`albumTranName`、`publishDate`、`totalNum`、`albumType`、`pmid`、`albumID`、`singerName`、`tags`。
- 所有项目流程新增列统一改为 `aux_` 前缀，例如 `aux_target_singer`、`aux_target_singer_mid`、`aux_sort_key`、`aux_include_album`、`aux_album_filter_reason`、`aux_target_singer_match`、`aux_source`。
- 已移除 `confidence` 列；当前高可信含义由输出目录、脚本规则、summary 规则和辅助筛选列表达，不再作为 CSV 普通列写出。
- 已使用本地原始缓存重新生成四位歌手单人 CSV、专辑 CSV、拒绝行 CSV 和四位歌手汇总 CSV，未重新请求外部接口。
- 验证对象为 `collect_high_confidence_singer_songs.py`，执行项目指定 Conda 解释器的 `py_compile`，未报语法错误。
- 验证对象为四位歌手 `songs_high_confidence.csv`、`albums_included.csv` 和汇总 `four_singers_high_confidence_songs.csv`，检查确认不存在 `confidence` 列；非 `aux_` 列均属于对应接口原始顶层键；单人行数仍为周杰伦 225、薛之谦 154、林俊杰 321、汪苏泷 362，汇总 1062 行且等于单人行数之和。

### 澄清高可信歌曲子集与原采集流程关系

- 用户询问当前是否只得到高可信歌曲列表子集，后续流程是否仍存在，以及原来的流程是否保留。
- 复核 `pyproject.toml` 脚本入口后确认，原有入口 `mr-collect-hot-singers`、`mr-collect-singer-songs`、`mr-validate-albums`、`mr-write-pipeline-report`、`mr-export-web-dataset` 仍保留；新增入口为 `mr-collect-high-confidence-songs`。
- 复核源码后确认，`collect_high_confidence_singer_songs.py` 当前只负责从歌手专辑列表和专辑歌曲列表生成高可信歌曲子集，不请求 `song.get_producer`，也不直接生成作词、作曲、图谱边或网页数据。
- 原流程 `collect_singer_songs.py` 仍保留歌手主页歌曲 Tab 全量采集、初过滤、去重、制作人员补全和作词作曲完整性过滤能力，输出 `songs_kept.json/csv`、`songs_credit_incomplete.json/csv` 等。
- 原后处理 `validate_album_ownership.py`、`write_singer_pipeline_report.py` 和 `export_web_dataset.py` 仍按原数据结构读取 `songs_kept.json` 或专辑验证结果；当前尚未改成直接消费高可信子集。
- 当前明确状态是高可信子集已经作为新的候选入口完成，但还没有接入制作人员补全、关系边生成、网页导出等下游阶段；后续需要决定是把高可信子集作为主输入替换旧歌曲入口，还是与原全量入口并行并在下游合并。

### 展开当前数据流程的逐步细节

- 用户要求不要把步骤合并成“初过滤”“报告”“去重”等概括词，而是把流程中每一步具体做什么完整展开。
- 已复核 `collect_hot_singer_registry.py`、`collect_singer_songs.py`、`collect_high_confidence_singer_songs.py`、`validate_album_ownership.py`、`write_singer_pipeline_report.py` 和 `export_web_dataset.py` 的实际逻辑。
- 原歌手歌曲流程的具体步骤包括：可选请求热门歌手列表或手动使用目标歌手 `mid`；请求歌手主页歌曲 Tab；把原始歌曲压缩为项目行结构；按 `name` 与 `title` 是否一致、专辑是否为空、标题是否包含版本词依次标记过滤原因；对未过滤歌曲按 `mid/id/歌名+歌手` 去重；请求制作人员接口；展开演唱、作词、作曲、编曲、制作人；按制作人员请求状态、作词是否为空、作曲是否为空决定是否进入可视化候选；写出全量、过滤、保留、制作人员不完整和快照文件。
- 专辑归属验证流程的具体步骤包括：读取原流程 `songs_kept.json`；收集唯一 `album_mid`；请求专辑详情；构造非版本歌曲基础标题集合；识别歌曲或专辑标题中的版本词；判断专辑署名歌手是否匹配目标歌手；检查专辑歌手、专辑标题、语言、发行公司、简介等可疑信号；按版本重复、强专辑归属不匹配、弱专辑归属不匹配输出 kept、rejected 或 review。
- 报告流程的具体步骤包括：读取原始全量歌曲、原始过滤歌曲、原始保留歌曲、专辑验证保留、专辑验证拒绝和专辑验证待复核数据；统计各类原因；按拼音/英文排序；分别写出汇总、原始过滤、原始保留、专辑待复核、专辑拒绝和最终保留 Markdown 表；生成后逐个校验 Markdown 表格列数和 UTF-8 可读性。
- 网页导出流程的具体步骤包括：读取每个目标歌手目录下的 `songs_kept.json` 和快照；为目标歌手创建 artist 节点；为每首歌创建 song 节点记录；从 `credits.groups` 中只取“作词”和“作曲”；为词曲作者创建 artist 节点；把非目标词曲作者指向目标歌手生成边；统计角色、贡献者、跨目标贡献者；写出单歌手 JSON 和总 catalog。
- 高可信专辑子集流程的具体步骤包括：请求指定歌手专辑列表；按 `albumType` 只保留 `Single`、`EP`、`录音室专辑`；对每张保留专辑请求专辑歌曲；检查歌曲 `singer[].mid` 是否包含目标歌手 `mid`；不匹配的写入 rejected 行；匹配的写入保留行；按歌曲 `mid/id` 去重；按辅助拼音排序键排序；写出单人和四人汇总 CSV/JSON、保留专辑、排除专辑、专辑歌曲保留前行和拒绝行。
- 当前结论仍是：原流程是端到端网页图谱流程但入口召回偏宽；高可信流程是更可靠的歌曲入口但尚未接入制作人员补全、专辑验证、报告和网页导出。

### 纠正高可信流程正式边界和 CSV 定位

- 用户纠正：高可信流程正式目标应使用全部歌手，当前四位歌手只是测试流程；CSV 应与 JSON 内容一致，只是方便查看的版本；正式流程不应包含 CSV。
- 已修改 `collect_high_confidence_singer_songs.py`：默认不再内置四位歌手作为正式输入，而是读取 `data/processed/singer_registry/qqmusic_hot/singer_registry.json` 中的全部歌手。
- 已新增 `--test-four-singers` 参数，用于显式运行周杰伦、薛之谦、林俊杰、汪苏泷四位测试样本；`--singer slug=name=mid` 仍保留为手动测试入口；`--max-singers` 用于 registry smoke test。
- 已新增 `--write-csv` 参数；默认正式输出只写 JSON，只有显式传入该参数时才生成 CSV 查看文件。
- 汇总正式 JSON 文件名从带四人语义的 `four_singers_high_confidence_songs.json` 调整为通用的 `singers_high_confidence_songs.json`；CSV 查看文件同名但扩展名为 `.csv`。
- CSV 生成逻辑改为从同一批 JSON 行动态生成列，嵌套字段序列化为 JSON 字符串，避免 CSV 与 JSON 使用两套字段结构。
- README 已同步说明高可信流程的前置条件是先生成歌手身份表；正式流程默认读取全部歌手；四位歌手和 CSV 都是调试或查看参数，不是正式流程边界。
- 验证对象为 `collect_high_confidence_singer_songs.py`，执行项目指定 Conda 解释器的 `py_compile`，未报语法错误。
- 使用已有原始缓存执行 `--test-four-singers` 且不加 `--write-csv` 输出到临时目录，结果为 4 位测试歌手、1062 首高可信歌曲、26 个 JSON 文件、0 个 CSV 文件，确认默认不写 CSV。
- 使用已有原始缓存执行 `--test-four-singers --write-csv` 输出到临时目录，结果汇总 JSON 和汇总 CSV 均为 1062 行，确认 CSV 是同一批 JSON 行的查看版。
- 当前工作区没有默认路径下的 `singer_registry.json`，因此正式全部歌手流程需要先运行歌手身份表采集，或通过 `--registry` 指向已有身份表文件。

### 生成四位歌手全集减高可信子集差集

- 用户要求用原流程接口请求周杰伦、薛之谦、林俊杰、汪苏泷四位歌手的全量歌曲，不做任何过滤，并从全集中减去高可信子集生成差集 CSV。
- 检查本地结果后确认，周杰伦、薛之谦、林俊杰的主页歌曲 Tab 全量 `songs_all.json/csv` 已存在于 `data/processed/singer_songs_homepage/`。
- 汪苏泷此前没有主页歌曲 Tab 全量缓存；首次补请求因沙箱网络权限触发 `WinError 5` 连接失败，未观察到 QQ 音乐接口封禁或限流响应；随后按权限规则联网重跑成功。
- 已使用原流程接口 `singer.get_tab_detail(mid, TabType.SONG)` 补采汪苏泷主页歌曲 Tab 全量数据，输出到 `data/processed/singer_songs_homepage/wangsulong/`；本次使用 `--skip-producers`，未请求制作人员，也未使用过滤后的结果。
- 汪苏泷主页歌曲 Tab 全量返回 939 行，写入 `songs_all.json/csv`；脚本同时按旧逻辑生成了 `songs_kept` 和 `songs_filtered`，但本次差集只读取 `songs_all.json`。
- 差集计算读取四位歌手的全集 `songs_all.json` 和高可信 `songs_high_confidence.json`，按歌曲 `mid` 优先、其次 `id`、最后 `规范化歌名+歌手` 建立 key。
- 差集规则为：全集中的每一行只要其 key 不在高可信 key 集中，就写入 `full_minus_high_confidence`；因此差集保留全集中的原始剩余行，不会先对全集去重。
- 已生成输出目录 `data/processed/high_confidence_diff/`，包含四位歌手单独 CSV/JSON、四位汇总 CSV/JSON 和 `summary.json`。
- 差集结果为：周杰伦全集 1012 行、高可信 225 行、差集 792 行；薛之谦全集 528 行、高可信 154 行、差集 399 行；林俊杰全集 1013 行、高可信 321 行、差集 746 行；汪苏泷全集 939 行、高可信 362 行、差集 627 行。
- 四位歌手汇总全集 3492 行、高可信 1062 行、差集 2564 行；差集数量不等于全集行数直接减高可信行数，因为全集保留未去重原始行，而高可信集合是去重后的 key 集。
- 验证对象为四位单独差集 CSV 和汇总差集 CSV，回读确认行数分别为 792、399、746、627 和 2564，文件存在且非空，UTF-8 可读且无 U+FFFD 替换字符。

### 重算全集去重后差集

- 用户指出全集也应该先按同一规则去重后再作为全集参与集合运算，而不是直接保留所有请求结果。
- 已按与高可信子集一致的歌曲 key 规则重算差集：优先使用 `mid`，没有 `mid` 时使用 `id`，再缺失时使用 `规范化歌名+歌手标识`。
- 新输出目录为 `data/processed/high_confidence_diff_deduped_full/`，其中四位歌手单独差集文件名为 `songs_deduped_full_minus_high_confidence.csv/json`，汇总文件名为 `four_singers_deduped_full_minus_high_confidence.csv/json`。
- 本次重算结果显示四位歌手的主页歌曲 Tab 全集 `songs_all.json` 中按该 key 规则没有重复 key：全集去重前 3492 行，去重后仍为 3492 行，移除重复 0 行。
- 因全集本身没有重复 key，重算后的差集行数与上一版一致：周杰伦 792、薛之谦 399、林俊杰 746、汪苏泷 627，汇总 2564。
- 新差集 CSV 增加 `aux_song_key`、`aux_duplicate_count_in_full` 和 `aux_duplicate_sources_json`，用于说明全集去重依据和每个 key 在全集中的原始来源行数。
- 验证对象为四位单独新差集 CSV 和汇总新差集 CSV，回读确认行数分别为 792、399、746、627 和 2564，文件存在且非空，UTF-8 可读且无 U+FFFD 替换字符。

### 按歌名键重算补充候选差集

- 用户要求调整作差使用的键，不再用 `mid` 和 `id`，而是直接用歌名；全集和高可信集合内部去重规则保持不变。
- 已生成新输出目录 `data/processed/high_confidence_diff_name_key/`，保留原有按 `mid/id` 作差结果不覆盖。
- 新差集计算流程为：全集先按原去重规则去重；高可信子集保持现有去重结果；作差时把两边歌曲名规范化后作为 `aux_diff_name_key`，全集中歌名 key 不在高可信歌名 key 集中的歌曲进入差集。
- 本次四位歌手全集按原去重规则仍无重复 key：去重前 3492 行，去重后 3492 行。
- 高可信子集 1062 行对应 828 个规范化歌名 key，说明在歌名层面存在同名不同版本或不同 id 的合并。
- 按歌名 key 作差后结果为：周杰伦 300 行、薛之谦 167 行、林俊杰 333 行、汪苏泷 467 行，汇总 1267 行。
- 新 CSV 保留 `aux_song_key` 作为原去重 key，同时新增 `aux_diff_name_key` 记录本次作差使用的歌名 key。
- 验证对象为四位单独新差集 CSV 和汇总新差集 CSV，回读确认行数分别为 300、167、333、467 和 1267，文件存在且非空，UTF-8 可读且无 U+FFFD 替换字符。

### 对齐补充候选差集 CSV 与高可信子集列结构

- 用户指出差集 CSV 列名应该与高可信子集保持一致，而不是沿用原流程整理字段。
- 已使用主页歌曲 Tab 原始缓存 `data/raw/qqmusic/singer_homepage_song_tab/<mid>/page_*.json` 重新生成按歌名作差的差集，而不是从原流程整理后的 `songs_all.json` 导出。
- 新输出目录为 `data/processed/high_confidence_diff_name_key_raw_schema/`，保留上一版整理字段差集不覆盖。
- 新差集 CSV 的非辅助列使用 QQ 音乐歌曲原始顶层键，列顺序与高可信 CSV 前置原始列一致，例如 `id`、`type`、`mid`、`name`、`title`、`subtitle`、`singer`、`album`、`mv`、`interval`、`isonly`、`language` 等。
- 新差集 CSV 的项目新增字段统一使用 `aux_` 前缀，包括 `aux_target_singer`、`aux_target_singer_mid`、`aux_sort_key`、`aux_song_key`、`aux_diff_name_key`、`aux_set_relation`、`aux_duplicate_count_in_full`、`aux_duplicate_sources` 和 `aux_source`。
- 按歌名作差的结果行数保持不变：周杰伦 300、薛之谦 167、林俊杰 333、汪苏泷 467，汇总 1267。
- 验证对象为新汇总差集 CSV 和四位单独差集 CSV，回读确认非 `aux_` 列均属于 QQ 音乐歌曲原始顶层键；汇总 CSV 前 12 列与高可信 CSV 前 12 列一致；文件 UTF-8 可读且无 U+FFFD 替换字符。

### 清理高可信差集旧输出目录

- 用户要求清理没用的旧目录。
- 已保留当前仍在使用的高可信源 JSON 目录 `data/processed/high_confidence_singer_songs/`、高可信 CSV 查看目录 `data/processed/high_confidence_singer_songs_csv_check/` 和最新差集目录 `data/processed/high_confidence_diff_name_key_raw_schema/`。
- 已删除中间验证目录 `data/processed/high_confidence_diff/`、`data/processed/high_confidence_diff_deduped_full/`、`data/processed/high_confidence_diff_name_key/` 和 `data/processed/high_confidence_singer_songs_json_only_check/`。
- 删除前校验了解析后的目标路径均位于当前工作区内；未删除 `data/raw/` 原始缓存。
- 清理后复核确认 `data/processed/high_confidence_singer_songs_csv_check/singers_high_confidence_songs.csv` 和 `data/processed/high_confidence_diff_name_key_raw_schema/four_singers_deduped_full_minus_high_confidence_by_name.csv` 仍存在且非空。

### 进一步清理 processed 探查和临时目录

- 用户指出 `data/processed` 中仍有很多目录，质疑它们是否都有用。
- 复核后确认上次清理过于保守：`album_probe`、`interface_compare`、`smoke` 是阶段性探查或验证产物；`high_confidence_singer_songs_csv_check` 是临时 CSV 查看目录；`high_confidence_singer_songs` 中旧命名 `four_singers_high_confidence_songs.*` 也已经被新命名 `singers_high_confidence_songs.*` 取代。
- 已先使用已有缓存将高可信 CSV 查看版重新生成回正式目录 `data/processed/high_confidence_singer_songs/`，确保删除临时 CSV 查看目录后仍保留当前高可信 CSV。
- 已删除 `data/processed/album_probe/`、`data/processed/interface_compare/`、`data/processed/smoke/`、`data/processed/high_confidence_singer_songs_csv_check/`。
- 已删除 `data/processed/high_confidence_singer_songs/four_singers_high_confidence_songs.csv` 和 `four_singers_high_confidence_songs.json`，保留通用命名的 `singers_high_confidence_songs.csv/json`。
- 已删除 `data/processed/singer_songs_homepage/three_singers_songs_all_sorted.csv` 和 `three_singers_songs_all_global_sorted.csv`，保留四位歌手各自目录下的主页歌曲 Tab 全集。
- 当前 `data/processed` 只保留 4 个目录：`high_confidence_singer_songs/`、`high_confidence_diff_name_key_raw_schema/`、`singer_songs_homepage/` 和 `singer_songs/`。
- 保留 `singer_songs_homepage/` 是因为它是当前全集分支来源；保留 `singer_songs/` 是因为当前网页导出脚本和已生成网页数据仍引用原端到端流程目录。
- 复核确认当前高可信汇总 `singers_high_confidence_songs.csv/json`、最新差集汇总 `four_singers_deduped_full_minus_high_confidence_by_name.csv/json` 以及四位歌手主页全集 `songs_all.json` 均存在且非空。

### 纠正正式流程目录和验证 CSV 目录混放

- 用户指出目录结构仍不清晰，正式流程目录和测试验证目录混在一起，正式流程目录中不应该保留 CSV。
- 已将正式流程目录中的 CSV 全部迁移到验证视图目录：高可信子集 CSV 移到 `data/processed/validation/four_singers/csv_views/high_confidence_singer_songs/`；补充候选差集 CSV 移到 `data/processed/validation/four_singers/csv_views/supplement_candidates_by_name/`；主页全集 CSV 移到 `data/processed/validation/four_singers/csv_views/homepage_full_singer_songs/`；旧端到端流程 CSV 移到 `data/processed/validation/legacy/csv_views/singer_songs/`。
- 已将临时命名目录 `data/processed/high_confidence_diff_name_key_raw_schema/` 改名为 `data/processed/high_confidence_supplement_candidates/`，使其对应新流程的“高可信以外补充候选”分支。
- 已修正补充候选 `summary.json`：输出路径改为新正式 JSON 目录，CSV 只作为 `csv_view` 指向验证目录，并修复此前临时脚本编码导致的歌手名 `???`。
- 已修改 `collect_high_confidence_singer_songs.py`：`--write-csv` 生成的 CSV 默认写入验证目录；四位歌手测试模式默认写入 `data/processed/validation/four_singers/csv_views/high_confidence_singer_songs/`；新增校验禁止把 `--csv-output-dir` 放在正式 `--output-dir` 内。
- 已同步 README 和 `AGENTS.md`：正式流程输出目录只保留 JSON、摘要和后续正式数据库/图谱产物；CSV 只作为人工查看或测试验证视图，统一写入 `data/processed/validation/.../csv_views/`。
- 验证对象为 `data/processed` 目录结构、`collect_high_confidence_singer_songs.py` 语法和 CSV 目录防护逻辑。
- 验证结果显示：`data/processed` 中位于 `data/processed/validation/` 之外的 CSV 数量为 0；验证目录中保留 54 个 CSV；脚本 `py_compile` 无语法错误；当 `--csv-output-dir` 位于正式输出目录内时会抛出明确 `ValueError`。
- 本次调整没有删除 `data/raw/` 原始缓存；重新执行四位歌手高可信测试时使用已有缓存，结果仍为 4 位歌手、1062 首高可信歌曲。

### 生成 data 目录完整树清单

- 用户要求列出 `data` 目录完整树到最子一级文件，并说明每类目录和文件的用途。
- 已统计当前 `data` 目录共有 328 个子目录、1243 个文件，其中 `data/raw/` 包含 283 个目录和 1115 个文件，`data/processed/` 包含 43 个目录和 128 个文件。
- 已生成 `reports/data_directory_tree_2026-05-12.md`，报告包含顶层计数、文件扩展名计数、主要路径用途说明、常见文件名含义说明、原始缓存路径提示和完整 ASCII 目录树。
- 报告说明了 `data/raw/qqmusic/album_probe/` 为旧专辑探查缓存，`data/raw/qqmusic/high_confidence_singer_songs/` 为高可信分支原始缓存，`data/raw/qqmusic/singer_homepage_song_tab/` 为当前全集分支原始缓存，`data/raw/qqmusic/song_producers/` 为旧端到端制作人员缓存。
- 报告说明了 `data/processed/high_confidence_singer_songs/` 和 `data/processed/high_confidence_supplement_candidates/` 为正式 JSON 输出目录，`data/processed/validation/.../csv_views/` 为人工查看 CSV 目录。
- 验证对象为生成的 Markdown 报告，已回读确认文件大小非零、UTF-8 可读且没有 U+FFFD 替换字符；因完整树包含 1243 个叶子文件，最终向用户提供报告链接和摘要而不直接在对话中粘贴全文。
### 纠正 data 目录报告粒度和中文写入方式

- 用户要求报告不要具体到最后一级文件，改为目录级别说明，并要求报告使用中文 UTF-8。
- 已重写
eports/data_directory_tree_2026-05-12.md：完整树不再逐个列出 .json 或 .csv 叶子文件，只列目录层级，并在目录后标注该目录本级直接包含的文件类型和数量。
- 已将报告内容改为中文，保留总目录数、总文件数、CSV 位置检查、顶层目录统计、文件类型统计、主要目录用途和常见文件名/模式含义。
- 首次重写时通过 PowerShell here-string 承载中文常量，导致中文或中文冒号被写成问号；已按用户纠正改为只用 Python 按 UTF-8 读写中文内容，PowerShell 仅作为启动 Python 的外壳且不承载中文正文。
- 验证对象为重写后的报告文件，使用 Python 读取 UTF-8 内容确认问号数量为 0、U+FFFD 替换字符数量为 0、目录树中逐个列出的 .json/.csv 叶子文件行数为 0，文件大小非零。

### 剥离旧端到端流程数据

- 用户要求把旧流程的所有东西从当前目录剥离，放到别的地方，避免混入正式流程。
- 已将旧端到端流程数据和缓存整体移动到 rchive/legacy_pipeline_2026-05-12/，并生成 manifest.txt 记录来源、移动状态、目录数、文件数和目标位置。
- 已移动的旧流程内容包括：data/processed/singer_songs/、data/processed/validation/legacy/、data/raw/qqmusic/singer_songs/、data/raw/qqmusic/song_producers/ 和 data/raw/qqmusic/album_probe/。
- 当前 data/raw/qqmusic/ 只保留 high_confidence_singer_songs/ 和 singer_homepage_song_tab/；当前 data/processed/ 只保留 high_confidence_singer_songs/、high_confidence_supplement_candidates/、singer_songs_homepage/ 和 alidation/。
- 已修改 collect_singer_songs.py，使主页全集候选流程默认只写 JSON；CSV 只有显式 --write-csv 时才写入 --csv-output-dir 指定的 validation 目录，并禁止 CSV 输出目录位于正式 --processed-dir 内。
- 已同步 README 和 AGENTS.md，说明旧流程数据归档位置、当前主页全集候选目录、正式目录不放 CSV 的规则，以及旧网页导出路径需要读取 archive 中的旧输入。
- 已新增 scripts/write_data_directory_report.py，用 Python UTF-8 生成中文 data 目录报告，避免通过 PowerShell 承载中文正文。
- 已重新生成
eports/data_directory_tree_2026-05-12.md，报告显示当前 data 下共有 303 个子目录、483 个文件；旧流程归档包含 30 个子目录、761 个文件；当前 data 中 CSV 总数为 42 个且全部位于 data/processed/validation/ 下。
- 验证对象包括目录移动结果、CSV 位置、报告编码和脚本语法；验证结果显示旧流程候选目录在 data 下均不存在，归档目标均存在；py_compile 无语法错误；报告中问号数量为 0、U+FFFD 替换字符数量为 0、逐个列出的 .json/.csv 叶子文件行数为 0。

### 剥离旧端到端流程代码和旧网页

- 用户指出旧流程代码和网页也应该全部剥离，不应继续混在当前正式流程里。
- 已将旧端到端流程代码移动到 rchive/legacy_pipeline_2026-05-12/code/music_metadata_graph/pipelines/，包括旧 collect_singer_songs.py、alidate_album_ownership.py、write_singer_pipeline_report.py 和 export_web_dataset.py。
- 已将旧静态网页目录 web/ 整体移动到 rchive/legacy_pipeline_2026-05-12/web/，包括旧页面、样式、脚本、静态数据和本地 vendor 文件。
- 已更新 rchive/legacy_pipeline_2026-05-12/manifest.txt，追加记录旧代码和旧网页的来源、移动状态、目录数、文件数和归档位置。
- 已从 pyproject.toml 删除旧流程脚本入口，只保留 mr-collect-hot-singers 和 mr-collect-high-confidence-songs。
- 已同步 README 和 AGENTS.md，说明旧流程代码、旧网页、旧数据和旧缓存都位于 archive，当前正式流程不再从这些目录读取，也不再向当前正式目录写入旧流程内容。
- 已更新 scripts/write_data_directory_report.py 和重新生成
eports/data_directory_tree_2026-05-12.md，报告显示旧流程归档现在包含 36 个子目录、773 个文件。
- 验证对象包括当前源码目录、旧网页目录、脚本入口、归档目录、报告编码和剩余正式 pipeline 语法；验证结果显示当前 music_metadata_graph/pipelines/ 仅剩 collect_hot_singer_registry.py 与 collect_high_confidence_singer_songs.py 两个正式采集脚本，当前根目录不再存在 web/，旧流程入口不再出现在 pyproject.toml，旧代码和旧网页在 archive 中存在，py_compile 无语法错误。

### 将四位测试 JSON 从正式目录移入 validation

- 用户指出 data/processed 中除验证目录外的三个目录仍包含周杰伦、薛之谦、林俊杰、汪苏泷等四位测试歌手数据，导致正式流程目录不干净。
- 复核后确认 data/processed/high_confidence_singer_songs/、data/processed/high_confidence_supplement_candidates/ 和 data/processed/singer_songs_homepage/ 中保存的都是四位测试样本 JSON，而不是全量正式流程结果。
- 已将这三类四位样本 JSON 整体移入 data/processed/validation/four_singers/json_outputs/：高可信子集移入 high_confidence_singer_songs/，主页全集移入 homepage_full_singer_songs/，补充候选差集移入 supplement_candidates_by_name/。
- 当前 data/processed 顶层只剩 alidation/；四位歌手样本 JSON 和 CSV 均位于 data/processed/validation/four_singers/ 下，不再混入正式输出目录。
- 已同步 README、AGENTS.md 和 scripts/write_data_directory_report.py，说明正式输出目录只是未来全量正式运行的目标位置，当前四位样本属于 validation 数据。
- 已重新生成
eports/data_directory_tree_2026-05-12.md，报告显示当前 data/processed/ 只保留验证数据；四位歌手样本 JSON 和 CSV 均在 data/processed/validation/four_singers/ 下。
- 验证结果显示：data/processed 顶层目录仅有 alidation；validation 外不存在包含 zhoujielun、xuezhiqian、linjunjie、wangsulong 或 our_singers 的样本路径；四位样本 JSON 输出共 57 个文件，CSV 查看版共 42 个文件；报告无问号、无 U+FFFD，且不逐个列出 .json/.csv 叶子文件。

### 重新整理 gitignore

- 用户要求重新整理 .gitignore，以匹配当前正式流程、验证数据和旧流程归档边界。
- 已将 .gitignore 重写为分组规则：本地环境和密钥、Python 缓存和工具产物、虚拟环境、Node 依赖和构建产物、本地数据和生成物、本地数据库/二进制分析输出、日志和临时文件。
- 当前忽略 data/、rchive/、
eports/ 和
ode_modules/，确保验证数据、旧流程归档、生成报告和本地依赖不进入 Git；源码、脚本、README、AGENTS、开发日志和项目配置不被忽略。
- 已按项目偏好确认 .gitignore 使用 CRLF，且没有双回车换行。
- 尝试使用 git check-ignore 和 git status --ignored 验证时，Git 因仓库 owner 与当前用户 SID 不一致报 dubious ownership，未修改全局 safe.directory 配置。
- 替代验证使用 Python 检查规则覆盖：data/processed/...、rchive/...、
eports/...、
ode_modules/... 会被规则忽略；README.md、AGENTS.md、develop_log.md、pyproject.toml、正式 pipeline 脚本和 scripts/write_data_directory_report.py 不会被当前规则忽略。




### 补齐全集过滤步骤的移除视图

- 用户明确验证测试阶段每一步过滤除了查看留下的行，也必须查看被过滤掉的行。
- 已新增 `scripts/write_homepage_filter_validation_views.py`，用于从主页全集原始缓存和高可信子集生成全集分支第一步过滤的验证视图。
- 该脚本为每个歌手输出三类 JSON/CSV：`songs_after_high_confidence_name_filter`（留下）、`songs_removed_by_high_confidence_name_filter`（因歌名命中高可信子集被过滤掉）、`songs_removed_as_duplicate_before_high_confidence_name_filter`（进入该过滤前去重移除）。
- 已重跑四位样本：全集 3492 行，去重移除 0 行，按高可信歌名过滤留下 1267 行、移除 2225 行；四个歌手各自计数均满足 `songs_all = kept + removed + duplicates`。
- 已同步 README、AGENTS.md 和 scripts/write_data_directory_report.py，记录验证阶段每一步过滤都要同时输出保留行和过滤掉的行，并写明 `aux_filter_reason` 或分支已有原因字段。

### 统一全集分支 CSV 列结构

- 用户要求所有 CSV 列名都必须符合新规定结构，重新生成全集分支。
- 已修改 `scripts/write_homepage_filter_validation_views.py`，使 `songs_all.json/csv` 也从主页歌曲 Tab 原始缓存重建为 QQ 音乐原始歌曲顶层键加 `aux_` 辅助键结构，不再保留旧流程扁平字段如 `album_name`、`singer_names`、`lyricists`、`composers`。
- 已修正空 CSV 写出逻辑：即使某一步过滤移除 0 行，也写出标准表头，避免空文件没有列名。
- 已重跑四位样本全集分支，当前 `songs_all`、`songs_after_high_confidence_name_filter`、`songs_removed_by_high_confidence_name_filter`、`songs_removed_as_duplicate_before_high_confidence_name_filter` 均使用统一列结构。
- 验证结果显示当前四位样本下 41 个 CSV 均只包含接口原始顶层键或 `aux_` 辅助键；高可信分支 21 个表格 JSON 与 CSV 一一对应，全集分支 20 个表格 JSON 与 CSV 一一对应；全集计数仍闭合。

### 补齐高可信分支专辑歌曲全集和去重移除视图

- 用户指出高可信分支每个歌手只有保留和剔除结果，缺少专辑请求到的全集歌曲列表。
- 已修改 `music_metadata_graph/pipelines/collect_high_confidence_singer_songs.py`：请求保留专辑歌曲后先写出 `album_song_rows_all_before_artist_filter`，再按目标歌手 mid 分成 `album_song_rows_kept_before_dedupe` 和 `album_song_rows_rejected`。
- 已补充高可信歌曲去重移除视图 `album_song_rows_removed_as_duplicate`，并为歌曲过滤/去重步骤写入 `aux_filter_step`、`aux_filter_result`、`aux_filter_reason`。
- 已重跑四位样本高可信分支：专辑歌曲全集 1475 行，目标歌手过滤保留 1062 行、移除 413 行；去重移除 0 行，最终高可信 1062 行。
- 验证结果显示每个歌手均满足 `album_song_rows_all_before_artist_filter = album_song_rows_kept_before_dedupe + album_song_rows_rejected`，且 `album_song_rows_kept_before_dedupe = songs_high_confidence + album_song_rows_removed_as_duplicate`；当前高可信分支 29 个表格 JSON 与 29 个 CSV 一一对应，全部 CSV 列名符合接口原始顶层键或 `aux_` 辅助键规则。

### 移除跨歌手合并验证表

- 用户指出全集分支存在每个 CSV 的四人合并表，而高可信分支没有对应合并表，流程不统一；要求统一为不需要合并汇总。
- 已修改 `scripts/write_homepage_filter_validation_views.py`，不再生成 `four_singers_*` 合并 JSON/CSV；只保留每个歌手自己的全集、过滤保留、过滤移除和去重移除文件。
- 已修改 `music_metadata_graph/pipelines/collect_high_confidence_singer_songs.py`，不再生成 `singers_high_confidence_songs.json/csv`，总 `summary.json` 只保留汇总计数，不再指向跨歌手表格产物。
- 已删除当前验证目录中已有的 `four_singers_*` 和 `singers_high_confidence_songs.*` 合并表，并重跑高可信分支与全集分支验证输出。
- 验证结果显示当前不存在跨歌手合并表；高可信分支每个歌手 7 个表格 JSON/CSV，全集分支每个歌手 4 个表格 JSON/CSV，两个分支 JSON/CSV 一一对应；当前 44 个 CSV 均符合接口原始顶层键或 `aux_` 辅助键规则。

## 2026-05-13

### 人工核查全集分支剩余歌曲目标歌手覆盖

- 用户要求手动检查主页全集分支在过滤掉高可信子集已有歌曲后，剩余歌曲的歌手列表是否每一首都包含对应目标歌手，并明确 Python 检查只能作为临时人工核查，不能作为正式流程。
- 核查对象为四位样本歌手的 `songs_after_high_confidence_name_filter.json`：周杰伦、薛之谦、林俊杰、汪苏泷。
- 核查方式为临时只读 Python 脚本读取 `high_confidence_name_filter_summary.json` 中记录的目标歌手 `mid` 和剩余歌曲 JSON，逐行检查歌曲 `singer` 或 `singers` 列表是否包含目标歌手 `mid`，缺失时再用目标歌手姓名兜底判断；该脚本未写入仓库文件，也未纳入正式 pipeline。
- 验证结果显示周杰伦剩余 300 首、薛之谦剩余 167 首、林俊杰剩余 333 首、汪苏泷剩余 467 首均包含对应目标歌手。
- 四位样本合计核查 1267 条剩余歌曲，目标歌手缺失数为 0。

### 在主页全集分支追加空专辑过滤

- 用户纠正前一轮理解，明确空专辑过滤不是插入到第一步前面，而是接在现有“减去高可信歌名”之后继续过滤。
- 当前目标仅涉及主页全集分支的验证流水线，不改高可信子集分支和旧端到端流程。
- 实现方案是让 `scripts/write_homepage_filter_validation_views.py` 在 `songs_after_high_confidence_name_filter` 之后再执行一层空专辑过滤，按 `album.name/title/subtitle` 为空判定 `empty_album`，并分别输出保留行和移除行。
- 新增输出为 `songs_after_empty_album_filter.json/csv` 和 `songs_removed_by_empty_album_filter.json/csv`；现有第一步输出保持不变。
- 风险边界是空专辑判定依赖主页歌曲 `album` 对象是否存在且是否含有效名称字段；如果上游缓存的空值形态变化，规则可能需要再收敛。
- 本轮不做范围是：不把空专辑规则同步到高可信子集分支，不改正式 JSON 目录结构，不删除既有第一步输出。

### 分析歌曲反查专辑校验链路

- 用户询问当前高可信分支是否可以反过来验证：先用一首歌请求它所属专辑，再检查该专辑是否存在于目标歌手的专辑列表中。
- 复核当前高可信分支实现后确认正式流程为 `qqmusic.singer.get_album_list` 获取歌手专辑列表，再用 `qqmusic.album.get_song` 获取专辑歌曲，最后按歌曲 `singer[].mid` 是否包含目标歌手过滤。
- 检查本地 `qqmusic-api-python` 暴露接口后确认可用候选链路包括 `song.get_detail(song_id_or_mid)`、`album.get_detail(album_id_or_mid)`、`album.get_song(album_id_or_mid)` 和 `singer.get_album_list(singer_mid)`。
- 使用已知歌曲样例进行小范围真实请求验证，观察到 `song.get_detail` 返回的歌曲详情中包含 `album.id`、`album.mid`、`album.name`、`album.title` 和 `album.pmid`，可作为“歌曲 -> 所属专辑”的结构化依据。
- 同一验证中继续请求 `album.get_detail(album_mid)`，观察到专辑详情可返回 `albumID`、`albumMid` 和 `albumName`；请求 `singer.get_album_list(target_mid)` 可返回 `albumList`，其中包含 `albumID`、`albumMid`、`albumName`、`albumType` 和 `singerName`。
- 形成结论：可以设计反向验证规则，优先用歌曲详情里的 `album.mid` 或 `album.id` 与目标歌手专辑列表中的 `albumMid` 或 `albumID` 做精确匹配；专辑名只能作为人工排查或弱兜底，不应作为高可信自动合并依据。
- 风险边界为 `singer.get_album_list` 当前样例中未返回可靠的 `singerMid`，因此“专辑属于目标歌手”的判断应以目标歌手接口返回的专辑集合为准；部分歌曲可能属于合辑、影视原声、群星专辑或平台拆分版本，反向验证不宜直接替代现有专辑正向采集流程。

### 统一高可信分支与主页分支的 filter 命名

- 用户进一步明确，两个分支的验证产物命名都应统一为 `songs_after_filter1/2/3_xxx` 与 `songs_removed_by/as_filter1/2/3_xxx`，不再出现 `before` 之类容易误解的命名。
- 已将高可信分支的验证产物命名统一到 `songs_after_filter1_album_fetch.json/csv`、`songs_after_filter2_target_singer_match.json/csv`、`songs_after_filter3_dedupe.json/csv`、`songs_removed_by_filter2_target_singer_match.json/csv`、`songs_removed_as_filter3_dedupe.json/csv`，并同步清理旧名残留。
- 已将主页全集验证分支统一到 `songs_after_filter1_dedupe.json/csv`、`songs_removed_as_filter1_dedupe.json/csv`、`songs_after_filter2_high_confidence_name_exclusion.json/csv`、`songs_removed_by_filter2_high_confidence_name_exclusion.json/csv`、`songs_after_filter3_empty_album_exclusion.json/csv`、`songs_removed_by_filter3_empty_album_exclusion.json/csv`，同时把 summary 和目录报告中的旧命名改为对应的新格式。
- 已同步 `README.md`、`scripts/write_data_directory_report.py` 和主页验证脚本中的读取路径与说明文字，避免文档继续引用 `before`、`high_confidence_name_filter` 或其他旧术语。
- 风险边界是此次只做命名统一，不改高可信分支的过滤逻辑和主页分支的过滤顺序；主页分支仍然是先去重，再减去高可信歌名，最后过滤空专辑。

### 核对两个歌曲输入分支过滤口径

- 用户询问当前两个分支各过滤几次，以及分别如何过滤。
- 已复核 `README.md`、`music_metadata_graph/pipelines/collect_high_confidence_singer_songs.py` 和 `scripts/write_homepage_filter_validation_views.py`。
- 当前结论为：高可信歌曲子集分支有 3 个歌曲层面的 filter 产物，另有专辑层面的 albumType 纳入/排除；主页全集分支有 3 个歌曲层面的 filter 产物。
- 高可信歌曲子集分支的歌曲层面顺序为：filter1 请求已纳入专辑的歌曲全集；filter2 只保留 `song.singer[].mid` 包含目标歌手 `mid` 的行；filter3 按歌曲 `mid` 优先、其次 `id` 去重。
- 主页全集分支的歌曲层面顺序为：filter1 按歌曲 key 去重；filter2 按规范化歌名减去高可信子集已有歌名；filter3 过滤空专辑行。

### 纠正高可信分支取数步骤命名

- 用户指出高可信分支中的 `songs_all` 已经表达已纳入专辑请求到的歌曲全集，`songs_after_filter1_album_fetch` 与其重复，而且请求页不是过滤步骤。
- 已修改 `music_metadata_graph/pipelines/collect_high_confidence_singer_songs.py`：不再生成 `songs_after_filter1_album_fetch`；高可信歌曲层面 filter1 改为目标歌手匹配，输出 `songs_after_filter1_target_singer_match` 与 `songs_removed_by_filter1_target_singer_match`；filter2 改为去重，输出 `songs_after_filter2_dedupe` 与 `songs_removed_as_filter2_dedupe`。
- 已修改 `scripts/write_homepage_filter_validation_views.py`，主页全集分支读取高可信最终集合时改用 `songs_after_filter2_dedupe.json`，并将原因字段从旧的 `filter3_dedupe` 表述改为 `song_name_exists_in_high_confidence_dedupe`。
- 已同步 `README.md`、`scripts/write_data_directory_report.py` 和 `AGENTS.md`，说明高可信 `songs_all` 是取数全集而不是过滤步骤，主页全集分支顺序为去重、减去高可信歌名、过滤空专辑。
- 验证对象为高可信 pipeline、主页全集验证脚本、目录报告脚本和四位样本验证输出；执行 `py_compile` 未报语法错误。
- 已重跑四位样本高可信 JSON/CSV 验证目录，结果为 `songs_all` 1475 行、filter1 目标歌手匹配保留 1062 行、filter1 移除 413 行、filter2 去重保留 1062 行、filter2 移除 0 行。
- 已重跑主页全集验证脚本，确认其能读取新的高可信最终集合文件；结果为全集 3492 行、filter1 去重后 3492 行、filter2 减高可信后 1267 行、filter3 空专辑过滤后 564 行。

### 统一移除产物命名并补充高可信同名去重

- 用户要求移除产物命名统一使用 `removed_by`，不再使用 `removed_as`；同时要求高可信分支 filter2 在 `mid/id` 去重后，对同名但 `mid/id` 不同的歌曲优先保留录音室专辑版本，其次保留 EP 版本。
- 已修改 `music_metadata_graph/pipelines/collect_high_confidence_singer_songs.py`：高可信 filter2 先按歌曲 key 去重，再按规范化歌名二次去重；同名候选按 `aux_source_albumType` 优先级选择，`录音室专辑` 优先于 `EP`，其他类型排在后面。
- 高可信 filter2 移除产物改名为 `songs_removed_by_filter2_dedupe.json/csv`；移除原因区分 `duplicate_song_key_in_songs_after_filter1_target_singer_match` 与 `duplicate_song_name_prefer_recording_album_then_ep`。
- 已修改 `scripts/write_homepage_filter_validation_views.py`：主页全集 filter1 移除产物改为 `songs_removed_by_filter1_dedupe.json/csv`，并删除旧 `high_confidence_name_filter_summary.json` 以避免历史 `removed_as` 路径残留。
- 已同步 `README.md` 和 `scripts/write_data_directory_report.py`，说明新的移除产物命名和高可信 filter2 的同名专辑类型优先规则。
- 验证对象为高可信 pipeline、主页全集验证脚本、目录报告脚本和四位样本验证输出；执行 `py_compile` 未报语法错误。
- 已重跑四位样本高可信验证目录，结果为 `songs_all` 1475 行、filter1 保留 1062 行、filter1 移除 413 行、filter2 最终保留 828 行、filter2 移除 234 行。
- 已重跑主页全集验证目录，结果为全集 3492 行、filter1 去重后 3492 行、filter1 移除 0 行、filter2 减高可信后 1267 行、filter3 空专辑过滤后 564 行。
- 已检查当前源码、README、AGENTS 和四位样本验证输出目录中不再存在 `removed_as` 或 `songs_removed_as` 字符串。

### 统一第二歌曲输入分支命名为补充分支

- 用户纠正命名规范：高可信分支之外的另一个歌曲输入分支统一叫“补充分支”，不得再称为“全集分支”“主页分支”或其他名称。
- 已在 `AGENTS.md` 的用户长期偏好中记录该命名规则，并把项目补充规则中的输出目标改为 `data/processed/supplement_singer_songs/`。
- 已同步 `README.md`，将四位样本歌手相关说明统一改为补充分支，并将验证输出路径说明改为 `data/processed/validation/four_singers/json_outputs/supplement_singer_songs/` 和 `data/processed/validation/four_singers/csv_views/supplement_singer_songs/`。
- 已将验证脚本从 `scripts/write_homepage_filter_validation_views.py` 改名为 `scripts/write_supplement_filter_validation_views.py`，脚本后续生成目录改为 `supplement_singer_songs`，并将输出数据中的 `aux_filter_step`、`aux_set_relation` 和 summary `step/branch` 改为 supplement 语义。
- 已同步 `scripts/write_data_directory_report.py`，使目录报告中的主要目录和常见文件说明统一称为补充分支。
- 已重跑补充分支验证脚本，结果为补充候选 3492 行、filter1 去重后 3492 行、filter1 移除 0 行、filter2 减高可信后 1267 行、filter2 移除 2225 行、filter3 空专辑过滤后 564 行、filter3 移除 703 行。
- 已重跑目录报告 `reports/data_directory_tree_2026-05-12.md`，报告可用 UTF-8 回读，文件大小非零，无 U+FFFD 替换字符，也无问号乱码。
- 验证对象为 `scripts/write_data_directory_report.py` 和 `scripts/write_supplement_filter_validation_views.py`，执行 `py_compile` 未报语法错误；搜索 README、AGENTS、scripts、pyproject 和正式源码，除“不得称为”的规范句外未发现旧分支名称残留。
- 本轮未删除旧本地验证目录；如需清理旧目录，需要用户明确确认删除范围。

### 记录 PowerShell 中文处理偏好

- 用户新增长期偏好：由于 PowerShell 对中文不友好，必要时采用 Python 工具而不是 PowerShell。
- 已将该偏好写入 `AGENTS.md` 用户长期偏好，明确涉及中文常量、中文文件内容、Markdown 表格、报告生成或中文输出判断时，优先使用明确 UTF-8 配置的 Python 工具或仓库脚本。
- 本次仅同步协作规则和开发日志，未修改业务代码。

### 调换补充分支 filter2 与 filter3 顺序

- 用户要求把补充分支的过滤 2 和过滤 3 换顺序。
- 目标效果调整为：补充分支仍先执行 filter1 去重；filter2 改为过滤空专辑；filter3 改为在空专辑过滤后的剩余集合中减去高可信子集已有歌名。
- 已修改 `scripts/write_supplement_filter_validation_views.py`，将 filter2 输出改为 `songs_after_filter2_empty_album_exclusion.json/csv` 与 `songs_removed_by_filter2_empty_album_exclusion.json/csv`，将 filter3 输出改为 `songs_after_filter3_high_confidence_name_exclusion.json/csv` 与 `songs_removed_by_filter3_high_confidence_name_exclusion.json/csv`。
- 已同步 `README.md`、`AGENTS.md` 和 `scripts/write_data_directory_report.py` 中对补充分支过滤顺序与常见产物名的说明。
- 已重跑补充分支四位样本验证脚本，结果为补充候选 3492 行、filter1 去重后 3492 行、filter1 移除 0 行、filter2 空专辑过滤后 1856 行、filter2 移除 1636 行、filter3 减高可信歌名后 564 行、filter3 移除 1292 行。
- 验证对象为 `scripts/write_supplement_filter_validation_views.py` 和 `scripts/write_data_directory_report.py`，执行 `py_compile` 未报语法错误。
- 已检查补充分支 JSON/CSV 验证目录，当前只保留新顺序对应的 filter 文件名，不再残留旧的 filter2 高可信歌名过滤或 filter3 空专辑过滤产物名。

### 临时探查周杰伦补充分支专辑详情

- 用户要求手动尝试查询周杰伦补充分支 filter3 后结果的每首歌专辑信息，并写出 `tmp` 开头临时 CSV，不写入正式流程。
- 已新增临时脚本 `tmp_probe_jay_supplement_album_details.py`，读取 `data/processed/validation/four_singers/json_outputs/supplement_singer_songs/zhoujielun/songs_after_filter3_high_confidence_name_exclusion.json`，按歌曲自带的 `album.mid` 或 `album.id` 请求 `client.album.get_detail()`。
- 首次沙箱内请求 QQ 音乐接口失败，失败原因为本地网络访问被拒绝；随后按权限规则放行网络后重跑成功。
- 已生成临时 CSV `tmp_jay_supplement_filter3_album_details.csv`，共 88 行歌曲；其中 84 行成功取得专辑详情，4 行因原歌曲缺少专辑 mid/id 未请求。
- 专辑详情接口返回结构包含 `album`、`company` 和 `singers`，其中 `album.album_type` 可用于观察专辑类型；本次临时样本中专辑类型分布为：`现场专辑` 51 行、`录音室专辑` 24 行、`Single` 7 行、`人声音频` 2 行。
- 本次输出和缓存均为临时核查资产：`tmp_jay_supplement_filter3_album_details.csv`、`tmp_probe_jay_supplement_album_details.py` 和 `tmp_qqmusic_album_detail_cache/`，未接入正式 pipeline 或验证目录规则。

### 仅调整补充分支 filter1 与 filter2 脚本顺序

- 用户要求把补充分支 filter1 和 filter2 换顺序，并明确只更新脚本、不跑生成流程。
- 已修改 `scripts/write_supplement_filter_validation_views.py`：filter1 改为空专辑过滤，输出 `songs_after_filter1_empty_album_exclusion` 与 `songs_removed_by_filter1_empty_album_exclusion`；filter2 改为对 filter1 保留结果按歌曲 key 去重，输出 `songs_after_filter2_dedupe` 与 `songs_removed_by_filter2_dedupe`；filter3 仍为减去高可信子集已有歌名。
- 已同步脚本内 summary 的 `step`、`description`、`filter_rules`、计数字段和输出路径字段。
- 本次按用户要求未执行 `scripts/write_supplement_filter_validation_views.py`，因此现有 JSON/CSV 验证产物尚未更新到新命名和新顺序。
- 验证对象仅为脚本语法和静态命名检查：执行 `py_compile` 未报语法错误；搜索脚本未发现旧的补充分支 filter1 去重或 filter2 空专辑命名残留。

### 接入补充分支专辑详情与专辑类型过滤脚本

- 用户要求删除前一轮临时产物，并把临时专辑详情探针接入正式补充分支脚本；同时要求只改脚本、不跑验证。
- 已删除临时脚本 `tmp_probe_jay_supplement_album_details.py`、临时缓存目录 `tmp_qqmusic_album_detail_cache/` 和临时 CSV `tmp_jay_supplement_filter3_album_details.csv`；临时 CSV 初次删除时被进程占用，随后重试删除成功。
- 已修改 `scripts/write_supplement_filter_validation_views.py`，将补充分支改为 5 个过滤步骤：filter1 过滤空专辑；filter2 移除专辑 id/mid 为空的行；随后请求 `client.album.get_detail()` 补充专辑详情并缓存到 `data/raw/qqmusic/supplement_album_details/`；filter3 只保留专辑类型为 `Single`、`EP`、`录音室专辑` 的行；filter4 去重；filter5 减去高可信子集已有歌名。
- 新增输出命名包括 `songs_after_filter2_album_identity`、`songs_removed_by_filter2_album_identity`、`songs_after_album_detail_enrich`、`songs_after_filter3_album_type`、`songs_removed_by_filter3_album_type`、`songs_after_filter4_dedupe`、`songs_removed_by_filter4_dedupe`、`songs_after_filter5_high_confidence_name_exclusion` 和 `songs_removed_by_filter5_high_confidence_name_exclusion`。
- 已将专辑详情字段写入 `aux_` 辅助列，包括请求 key/status、专辑 id/mid/name/type、专辑歌手、语言、流派、发行时间、简介和缓存文件路径。
- 本次按用户要求未执行 `scripts/write_supplement_filter_validation_views.py`，因此未请求新专辑详情、未写入新正式缓存，也未更新补充分支 JSON/CSV 验证产物。
- 验证对象仅为脚本语法和静态命名检查：执行 `py_compile` 未报语法错误；搜索脚本确认旧补充分支 filter2 去重、filter3 高可信命名不再作为补充分支产物残留。

### 统一两个分支同名去重规则

- 用户要求高可信分支和补充分支都改为：先按歌曲 `id/mid` 去重；不再按歌名加歌手键去重；再只按原始 `name` 去重，不使用 `title`；同 `name` 不同专辑类型时按 `录音室专辑`、`EP`、`Single` 顺序保留；如果同 `name` 且同专辑类型仍有多条，保留数值 `id` 更小的歌曲。
- 已修改 `music_metadata_graph/pipelines/collect_high_confidence_singer_songs.py`：`song_key()` 不再使用 `name + singer` 兜底；`song_name_key()` 只读取原始 `name`；同名去重优先级加入 `Single`，并在专辑类型优先级后按数值歌曲 `id` 升序选择。
- 已修改高可信分支重复原因和辅助字段，补充记录同名组选中歌曲的数值 `id`，并将同名移除原因更新为包含 `录音室专辑 -> EP -> Single -> 最小 id` 的选择规则。
- 已修改 `scripts/write_supplement_filter_validation_views.py`：补充分支 filter4 先按歌曲 `mid/id` 去重，再只按原始 `name` 去重；同名优先级使用补充专辑详情中的 `aux_album_detail_type`，并以数值歌曲 `id` 作为最终 tie-breaker。
- 已同步 `README.md` 和 `scripts/write_data_directory_report.py`，说明两个分支共享的新去重口径以及补充分支当前 5 步过滤流程。
- 本次未运行高可信分支或补充分支生成流程，未更新 JSON/CSV 验证产物，也未请求新的专辑详情接口。
- 验证对象为 `music_metadata_graph/pipelines/collect_high_confidence_singer_songs.py`、`scripts/write_supplement_filter_validation_views.py` 和 `scripts/write_data_directory_report.py`，执行 `py_compile` 未报语法错误；静态搜索未发现旧的 `name + singer` 去重说明或补充分支旧 filter1/filter2/filter3 产物说明残留。

### 重跑四位样本歌曲输入全流程

- 用户要求现在跑一次全流程；本次按当前阶段上下文执行四位样本验证链路：先跑高可信分支，再跑补充分支。
- 已运行高可信分支命令：`python -m music_metadata_graph.pipelines.collect_high_confidence_singer_songs --test-four-singers --write-csv --output-dir data/processed/validation/four_singers/json_outputs/high_confidence_singer_songs --csv-output-dir data/processed/validation/four_singers/csv_views/high_confidence_singer_songs`。
- 高可信分支验证结果为：`songs_all` 1475 行，filter1 目标歌手匹配后 1062 行、移除 413 行，filter2 去重后 828 行、移除 234 行。
- 已运行补充分支脚本 `scripts/write_supplement_filter_validation_views.py`；首次沙箱内执行时专辑详情请求被本机网络权限拒绝，导致专辑类型缺失并使 filter3 全部移除，该结果被识别为无效中间结果。
- 随后按权限规则放行网络后重跑补充分支脚本，成功请求并缓存专辑详情到 `data/raw/qqmusic/supplement_album_details/`，当前缓存文件数为 654。
- 补充分支有效验证结果为：`songs_all` 3492 行；filter1 空专辑过滤后 1856 行、移除 1636 行；filter2 专辑 id/mid 非空过滤后 1816 行、移除 40 行；专辑详情补充后 1816 行；filter3 专辑类型过滤后 1126 行、移除 690 行；filter4 去重后 954 行、移除 172 行；filter5 减高可信歌名后 128 行、移除 826 行。
- 按歌手拆分的补充分支最终保留数为：周杰伦 29 行、薛之谦 8 行、林俊杰 26 行、汪苏泷 65 行。
- filter3 后保留行的专辑类型分布为：`录音室专辑` 863 行、`Single` 219 行、`EP` 44 行。
- 已重跑目录报告脚本 `scripts/write_data_directory_report.py`，更新 `reports/data_directory_tree_2026-05-12.md`；报告文件可用 UTF-8 回读，大小非零，无 U+FFFD 替换字符，也无问号乱码。
- 验证对象为高可信分支 summary、补充分支 summary、四位歌手每步 JSON 计数、专辑详情缓存数量、目录报告和三个脚本语法；观察结果显示每一步保留数与移除数加和关系成立，`py_compile` 未报语法错误。

### 移除补充分支 CSV 中的专辑简介字段并重跑全流程

- 用户要求补充分支 CSV 不写入 `aux_album_detail_desc`，并询问补充分支过滤过程中为何需要请求、是否只请求一次并缓存。
- 已修改 `scripts/write_supplement_filter_validation_views.py`：JSON 仍保留 `aux_album_detail_desc` 便于回看，CSV 查看版使用独立字段列表并禁止追加额外字段，因此不再输出 `aux_album_detail_desc` 列。
- 请求机制说明：补充分支在 filter2 后需要用歌曲自带的 `album.mid` 或 `album.id` 请求 `client.album.get_detail()`，以取得 `album.album_type` 等专辑详情供 filter3 专辑类型过滤；脚本先查 `data/raw/qqmusic/supplement_album_details/<album_mid_or_id>.json`，缓存存在则读取本地文件，只有缓存不存在才请求接口。
- 已按用户要求重跑四位样本全流程：高可信分支计数保持为 `songs_all` 1475 行、filter1 后 1062 行、filter2 后 828 行；补充分支计数保持为 `songs_all` 3492 行、filter1 后 1856 行、filter2 后 1816 行、专辑详情补充后 1816 行、filter3 后 1126 行、filter4 后 954 行、filter5 后 128 行。
- 重跑补充分支时，专辑详情补充的 1816 行请求状态全部为 `cache_hit`，说明本次没有重复请求已缓存专辑详情接口。
- 已检查 `data/processed/validation/four_singers/csv_views/supplement_singer_songs/` 下 48 个 CSV，均不包含 `aux_album_detail_desc` 列。
- 已重跑目录报告 `reports/data_directory_tree_2026-05-12.md`，并执行脚本语法检查；`py_compile` 未报语法错误。
