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
- 复核发现第一次失败原因是报告表格行之间被写入空行，Markdown 渲染器将表格拆断；后续又发现 Windows 文本模式写入 `\r\n` 时被二次转换为 `\r\r\n`，继续产生空行。
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
