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
- 已重写 reports/data_directory_tree_2026-05-12.md：完整树不再逐个列出 .json 或 .csv 叶子文件，只列目录层级，并在目录后标注该目录本级直接包含的文件类型和数量。
- 已将报告内容改为中文，保留总目录数、总文件数、CSV 位置检查、顶层目录统计、文件类型统计、主要目录用途和常见文件名/模式含义。
- 首次重写时通过 PowerShell here-string 承载中文常量，导致中文或中文冒号被写成问号；已按用户纠正改为只用 Python 按 UTF-8 读写中文内容，PowerShell 仅作为启动 Python 的外壳且不承载中文正文。
- 验证对象为重写后的报告文件，使用 Python 读取 UTF-8 内容确认问号数量为 0、U+FFFD 替换字符数量为 0、目录树中逐个列出的 .json/.csv 叶子文件行数为 0，文件大小非零。

### 剥离旧端到端流程数据
- 用户要求把旧流程的所有东西从当前目录剥离，放到别的地方，避免混入正式流程。
- 已将旧端到端流程数据和缓存整体移动到 archive/legacy_pipeline_2026-05-12/，并生成 manifest.txt 记录来源、移动状态、目录数、文件数和目标位置。
- 已移动的旧流程内容包括：data/processed/singer_songs/、data/processed/validation/legacy/、data/raw/qqmusic/singer_songs/、data/raw/qqmusic/song_producers/ 和 data/raw/qqmusic/album_probe/。
- 当前 data/raw/qqmusic/ 只保留 high_confidence_singer_songs/ 和 singer_homepage_song_tab/；当前 data/processed/ 只保留 high_confidence_singer_songs/、high_confidence_supplement_candidates/、singer_songs_homepage/ 和 validation/。
- 已修改 collect_singer_songs.py，使主页全集候选流程默认只写 JSON；CSV 只有显式 --write-csv 时才写入 --csv-output-dir 指定的 validation 目录，并禁止 CSV 输出目录位于正式 --processed-dir 内。
- 已同步 README 和 AGENTS.md，说明旧流程数据归档位置、当前主页全集候选目录、正式目录不放 CSV 的规则，以及旧网页导出路径需要读取 archive 中的旧输入。
- 已新增 scripts/write_data_directory_report.py，用 Python UTF-8 生成中文 data 目录报告，避免通过 PowerShell 承载中文正文。
- 已重新生成 reports/data_directory_tree_2026-05-12.md，报告显示当前 data 下共有 303 个子目录、483 个文件；旧流程归档包含 30 个子目录、761 个文件；当前 data 中 CSV 总数为 42 个且全部位于 data/processed/validation/ 下。
- 验证对象包括目录移动结果、CSV 位置、报告编码和脚本语法；验证结果显示旧流程候选目录在 data 下均不存在，归档目标均存在；py_compile 无语法错误；报告中问号数量为 0、U+FFFD 替换字符数量为 0、逐个列出的 .json/.csv 叶子文件行数为 0。

### 剥离旧端到端流程代码和旧网页
- 用户指出旧流程代码和网页也应该全部剥离，不应继续混在当前正式流程里。
- 已将旧端到端流程代码移动到 archive/legacy_pipeline_2026-05-12/code/music_metadata_graph/pipelines/，包括旧 collect_singer_songs.py、validate_album_ownership.py、write_singer_pipeline_report.py 和 export_web_dataset.py。
- 已将旧静态网页目录 web/ 整体移动到 archive/legacy_pipeline_2026-05-12/web/，包括旧页面、样式、脚本、静态数据和本地 vendor 文件。
- 已更新 archive/legacy_pipeline_2026-05-12/manifest.txt，追加记录旧代码和旧网页的来源、移动状态、目录数、文件数和归档位置。
- 已从 pyproject.toml 删除旧流程脚本入口，只保留 mr-collect-hot-singers 和 mr-collect-high-confidence-songs。
- 已同步 README 和 AGENTS.md，说明旧流程代码、旧网页、旧数据和旧缓存都位于 archive，当前正式流程不再从这些目录读取，也不再向当前正式目录写入旧流程内容。
- 已更新 scripts/write_data_directory_report.py 和重新生成 reports/data_directory_tree_2026-05-12.md，报告显示旧流程归档现在包含 36 个子目录、773 个文件。
- 验证对象包括当前源码目录、旧网页目录、脚本入口、归档目录、报告编码和剩余正式 pipeline 语法；验证结果显示当前 music_metadata_graph/pipelines/ 仅剩 collect_hot_singer_registry.py 与 collect_high_confidence_singer_songs.py 两个正式采集脚本，当前根目录不再存在 web/，旧流程入口不再出现在 pyproject.toml，旧代码和旧网页在 archive 中存在，py_compile 无语法错误。

### 将四位测试 JSON 从正式目录移入 validation
- 用户指出 data/processed 中除验证目录外的三个目录仍包含周杰伦、薛之谦、林俊杰、汪苏泷等四位测试歌手数据，导致正式流程目录不干净。
- 复核后确认 data/processed/high_confidence_singer_songs/、data/processed/high_confidence_supplement_candidates/ 和 data/processed/singer_songs_homepage/ 中保存的都是四位测试样本 JSON，而不是全量正式流程结果。
- 已将这三类四位样本 JSON 整体移入 data/processed/validation/four_singers/json_outputs/：高可信子集移入 high_confidence_singer_songs/，主页全集移入 homepage_full_singer_songs/，补充候选差集移入 supplement_candidates_by_name/。
- 当前 data/processed 顶层只剩 validation/；四位歌手样本 JSON 和 CSV 均位于 data/processed/validation/four_singers/ 下，不再混入正式输出目录。
- 已同步 README、AGENTS.md 和 scripts/write_data_directory_report.py，说明正式输出目录只是未来全量正式运行的目标位置，当前四位样本属于 validation 数据。
- 已重新生成 reports/data_directory_tree_2026-05-12.md，报告显示当前 data/processed/ 只保留验证数据；四位歌手样本 JSON 和 CSV 均在 data/processed/validation/four_singers/ 下。
- 验证结果显示：data/processed 顶层目录仅有 validation；validation 外不存在包含 zhoujielun、xuezhiqian、linjunjie、wangsulong 或 four_singers 的样本路径；四位样本 JSON 输出共 57 个文件，CSV 查看版共 42 个文件；报告无问号、无 U+FFFD，且不逐个列出 .json/.csv 叶子文件。

### 重新整理 gitignore
- 用户要求重新整理 .gitignore，以匹配当前正式流程、验证数据和旧流程归档边界。
- 已将 .gitignore 重写为分组规则：本地环境和密钥、Python 缓存和工具产物、虚拟环境、Node 依赖和构建产物、本地数据和生成物、本地数据库/二进制分析输出、日志和临时文件。
- 当前忽略 data/、archive/、reports/ 和 node_modules/，确保验证数据、旧流程归档、生成报告和本地依赖不进入 Git；源码、脚本、README、AGENTS、开发日志和项目配置不被忽略。
- 已按项目偏好确认 .gitignore 使用 CRLF，且没有双回车换行。
- 尝试使用 git check-ignore 和 git status --ignored 验证时，Git 因仓库 owner 与当前用户 SID 不一致报 dubious ownership，未修改全局 safe.directory 配置。
- 替代验证使用 Python 检查规则覆盖：data/processed/...、archive/...、reports/...、node_modules/... 会被规则忽略；README.md、AGENTS.md、develop_log.md、pyproject.toml、正式 pipeline 脚本和 scripts/write_data_directory_report.py 不会被当前规则忽略。

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

## 2026-05-14

### 修正第九步后临时 CSV 为一歌一行
- 用户指出第九步之后的临时 CSV 不应按一首歌的一个歌手展开，而应按一首歌一行，多歌手合并成嵌套字段。
- 已覆盖导出 `data/processed/validation/temp_song_filtering/csv_views/songs_after_step9_same_singer_name_dedupe.csv`。
- 新 CSV 每行对应一首 `songs` 记录，普通列包含歌曲字段和专辑字段；多歌手信息合并到 `singers_json` 字段，字段值为 JSON 数组，每个数组元素同时包含 `song_singers` 关系字段和 `singers` 歌手字段。
- 验证结果：CSV 文件存在且非零，大小 1270025 字节；共 983 行、19 列；`singers_json` 可正常解析；当前数据库 `songs` 为 983 首、`song_singers` 为 1442 条；`PRAGMA foreign_key_check` 无结果。

### 简化第九步后临时 CSV 歌手嵌套字段
- 用户指出 `singers_json` 不需要完整关系表和歌手表字段，只需要歌手 `mid` 和 `name`。
- 已覆盖导出 `data/processed/validation/temp_song_filtering/csv_views/songs_after_step9_same_singer_name_dedupe.csv`，保持一首歌一行，普通歌曲和专辑列不变。
- 新 `singers_json` 为 JSON 数组，每个歌手对象只包含 `mid` 和 `name` 两个键；额外保留 `singer_count` 方便快速查看歌手数量。
- 验证结果：CSV 共 983 行、19 列，大小 355454 字节；首行 `singers_json` 可解析且所有歌手对象键集合均为 `mid/name`；数据库仍为 `songs` 983 首、`song_singers` 1442 条，`PRAGMA foreign_key_check` 无结果。

### 精简第九步后临时 CSV 展示列
- 用户指出第九步之后临时 CSV 中不需要 `song_album_mid`、歌曲 raw 追溯字段、专辑 mid/id/raw 追溯字段等列。
- 已在用户关闭占用文件后覆盖导出 `data/processed/validation/temp_song_filtering/csv_views/songs_after_step9_same_singer_name_dedupe.csv`。
- 当前临时 CSV 只保留 10 列：`song_mid`、`song_id`、`song_name`、`song_title`、`song_language`、`album_name`、`album_type`、`album_publish_date`、`singer_count`、`singers_json`。
- `singers_json` 继续保持 JSON 数组，每个歌手对象只包含 `mid` 和 `name`。
- 验证结果：CSV 共 983 行、10 列，大小 176858 字节；`singers_json` 可正常解析且所有歌手对象键集合均为 `mid/name`；数据库仍为 `songs` 983 首、`song_singers` 1442 条，`PRAGMA foreign_key_check` 无结果。

### 统一所有歌曲 CSV 导出列
- 用户要求所有导出 CSV 都只需要 `song_mid`、`song_id`、`song_name`、`song_title`、`song_language`、`album_name`、`album_type`、`album_publish_date`、`singer_count`、`singers_json` 这 10 列。
- 已修改 `music_metadata_graph/pipelines/import_singer_song_tab_to_db.py`，第七步入库失败 CSV 也按统一 10 列输出；`singers_json` 只包含歌手 `mid` 和 `name`。
- 已修改 `music_metadata_graph/pipelines/filter_imported_songs.py`，第八步过滤 CSV、第九步过滤 CSV 和第九步后临时查看 CSV 均按统一 10 列输出；脚本层面保留过滤判断所需内部字段，但不写入 CSV。
- 已更新 `README.md` 和 `AGENTS.md`，记录歌曲相关导出 CSV 的统一列规则，并移除旧的“拒绝 CSV 额外输出拒绝原因和 raw 追溯字段”要求。
- 已重新运行四位歌手第七步入库和第八、第九步过滤，重新生成四个 CSV：`song_import_rejections.csv` 1670 行，`songs_removed_by_step8_album_type.csv` 685 行，`songs_removed_by_step9_same_singer_name_dedupe.csv` 141 行，`songs_after_step9_same_singer_name_dedupe.csv` 983 行。
- 验证结果：两个脚本均通过 `py_compile`；四个 CSV 表头均严格等于统一 10 列；四个 CSV 的 `singers_json` 首行均可解析且歌手对象只包含 `mid/name`；数据库最终为 `songs` 983 首、`song_singers` 1442 条，`PRAGMA foreign_key_check` 无结果，同名且同歌手重复组为 0。

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

### 分析从 JSON 文件切换到数据库管理数据
- 用户提出当前处理数据仍依赖 JSON 文件，操作不方便，要求先分析切换到数据库管理数据的可行性、注意事项、前后操作对应关系和潜在遗漏点。
- 复核当前正式源码后确认，现有正式处理入口主要是 `collect_hot_singer_registry.py`、`collect_high_confidence_singer_songs.py` 和 `scripts/write_supplement_filter_validation_views.py`；它们把原始接口缓存、正式处理产物、验证产物和摘要都写为 JSON，CSV 只作为人工查看版。
- 可行性结论是适合切换，但不应一次性把所有 JSON 都替换为数据库：原始接口响应缓存继续保留为 JSON 更利于复现和隔离第三方接口变化；处理后的结构化数据、过滤步骤、摘要和图谱查询数据适合写入 SQLite 或 DuckDB。
- 当前项目以本地个人分析、批处理、可视化导出为主，没有多用户并发写入需求；SQLite 更适合作为第一阶段持久化数据库，DuckDB 更适合作为后续分析查询或批量导出引擎。
- 推荐目标效果是用户运行采集或验证脚本后，数据进入本地数据库文件，用户可以按歌手、歌曲、专辑、分支、过滤步骤、过滤原因、作词人、作曲人等字段查询，而不需要手动打开多个目录下的 JSON 文件。
- 迁移方案应分阶段落地：先建立数据库 schema 和只读导入器，把现有四位样本 JSON 导入数据库并与原 JSON 计数对账；再让高可信分支和补充分支直接写入数据库；最后再从数据库导出网页静态 JSON 和人工 CSV 视图。
- 操作对应关系需要保留当前语义：`singer_registry.json` 对应 `artists` 与 `artist_snapshots`；高可信分支的 `songs_all`、`songs_after_filter1_target_singer_match`、`songs_after_filter2_dedupe` 等对应同一批歌曲在 `pipeline_rows` 或 `song_pipeline_states` 中的阶段状态；补充分支的 filter1 到 filter5 对应按 `branch`、`step`、`result` 和 `reason` 查询。
- 数据库设计需要特别保留审计能力：每一步过滤都必须能同时查询保留行和被过滤行，不能只保留最终结果；每条行还需要保留来源接口、原始缓存路径、目标歌手、分支、步骤、原因字段和必要原始 JSON 片段。
- 风险边界包括 schema 过早定死、嵌套字段扁平化丢信息、同名音乐人或同名歌曲误合并、数据库文件被误提交、Windows 文件占用导致写入失败、迁移后网页仍需要静态 JSON 发布、以及历史 JSON 与新数据库并存期间可能出现双写不一致。
- 本轮不做代码实现、不迁移数据、不删除现有 JSON/CSV 产物，也不改变原始接口缓存策略；后续如果进入实现，应先补充数据库依赖声明、schema 文档、导入验证脚本和对账命令。

### 纠正数据库切换方案为采集即入库
- 用户指出前一版方案仍保留“采集后生成 JSON，再从 JSON 清洗”的思路有问题，因为当前痛点正是 JSON 清洗不方便。
- 已调整方案判断：后续数据库化不应把数据库只作为 JSON 之后的最终存储或导入目标，而应改为采集阶段直接写入数据库，后续清洗、过滤、去重、补充分支减高可信子集、摘要统计和人工查看导出都围绕数据库表或视图执行。
- 调整后的操作边界是：接口响应返回后应在同一次采集运行中写入数据库的原始记录表和规范化 staging 表；JSON 文件不再作为正式清洗输入，只可作为可选调试导出或过渡期只读对账材料。
- 数据库内需要保留当前验证要求：每一步过滤必须能查询保留行和被过滤行，并保留 `aux_filter_reason` 或等价原因字段；因此数据库 schema 需要支持 pipeline run、branch、step、result、reason、target singer 和 source record 追溯。
- 后续实现优先级应从“现有 JSON 导入器”调整为“新采集写入路径 + 四位样本小范围重采集入库 + 与旧 JSON 计数对账”；旧 JSON 导入器只作为迁移历史样本的辅助工具，不应成为新正式流程主路径。

### 设计数据库 UML 初稿
- 用户确认可以同时保存原生 JSON 并写入数据库，用原始 JSON 保留接口响应，但后续正式清洗应在数据库内完成。
- 用户要求设计数据库结构，包括应设计几个类、每个类主键和属性，并用 Mermaid Live Editor 可用的 UML 模型代码表达。
- 初稿设计按职责分为五组：原始响应与运行记录、采集 staging 表、流程过滤状态表、最终标准实体表、导出与摘要表。
- 关键设计约束是 `SourceRecord` 负责关联本地原生 JSON 缓存与数据库记录；`PipelineRun` 负责标识一次采集或清洗运行；`PipelineSongRow` 负责保留每个分支每一步的保留行和被过滤行，避免丢失验证审计能力。
- 主键策略初稿为内部主键使用 UUID 或自增整数均可，但逻辑唯一性必须依赖平台身份键，例如 `source_platform + source_artist_mid`、`source_platform + source_song_mid/id` 和 `source_platform + source_album_mid/id`；最终实体通过 identity 表承载多平台 ID，避免同名音乐人或同名歌曲误合并。
- 本轮只形成 UML 设计初稿，未创建数据库文件、未修改 pipeline 代码，也未迁移或重采集数据。

### 纠正数据库 UML 初稿过度复杂
- 用户指出前一版 Mermaid UML 中出现过多难以理解的内部类，并追问图中下方的类是什么。
- 已确认前一版 UML 把 staging、pipeline row、统计表和身份映射表等内部实现细节直接暴露在第一视图中，导致模型表达不清晰。
- 调整后的表达方式应先给核心概念模型：`SourceRecord`、`Run`、`Artist`、`Album`、`Song`、`SongArtist`、`Credit`、`SongFilterState`，只在实现细节中再解释 staging 表和统计表。
- 后续 Mermaid 设计应优先服务用户理解和数据库落地，不应把所有可选内部表一次性画进主图。

### 明确原生 JSON 与数据库的边界
- 用户指出如果外部已经保留原生 JSON 文件，数据库就不应该再包含完整 JSON，否则外部 JSON 缓存和数据库原始载荷会重复。
- 已调整数据库边界：原生接口响应只保存在 `data/raw/` 的 JSON 文件中；数据库只保存 `raw_json_path`、请求参数、接口名、抓取状态、时间戳、来源记录 ID 和从原始响应抽取出的结构化字段。
- 数据库内不再设计 `raw_json`、`raw_payload_json`、`row_snapshot_json` 这类完整 JSON 载荷字段；如需调试，应通过 `source_record_id` 或 `raw_json_path` 回到外部原生 JSON 文件。
- 仍可在数据库中保留少量非原始载荷的结构化辅助字段，例如规范化歌名、过滤原因、去重 key 和计数字段；这些字段服务查询和清洗，不替代原生 JSON。

### 归档当前流程和本地数据准备重新设计
- 用户要求把当前流程全部归档，包括 raw 数据，以便重新设计请求顺序和存储。
- 已创建新归档目录 `archive/redesign_reset_2026-05-13/`，用于保存重新设计前的当前流程资产。
- 已归档当前正式采集代码 `music_metadata_graph/pipelines/` 到 `archive/redesign_reset_2026-05-13/code/music_metadata_graph/pipelines/`，包括热门歌手身份表采集和高可信歌曲子集采集脚本。
- 已归档当前辅助脚本 `scripts/` 到 `archive/redesign_reset_2026-05-13/code/scripts/`，包括补充分支验证视图脚本和数据目录报告脚本。
- 已归档当前本地数据目录 `data/` 到 `archive/redesign_reset_2026-05-13/data/`，其中 `data/raw/` 包含旧 QQ 音乐原始接口缓存，`data/processed/` 包含旧四位歌手验证 JSON/CSV 产物。
- 已归档当前生成报告 `reports/`、旧网页依赖配置 `package.json` 与 `package-lock.json`、旧 force-graph 本地参考文档和当时存在的 Python 缓存。
- 初次直接移动 `data/` 时 Windows 返回访问拒绝；随后改为复制到归档目录、核对文件数与字节数一致后再删除当前目录，避免半归档或数据丢失。
- 归档资产统计为文件 1227 个、目录 308 个、字节数 177694935；其中 `data/raw/` 为 1039 个文件、23178855 字节，`data/processed/` 为 167 个文件、154147976 字节；新增归档清单后归档目录实际文件数为 1228 个。
- 已新增 `archive/redesign_reset_2026-05-13/manifest.md`，记录归档范围、内容、统计和后续使用边界。
- 已将当前根目录重新收敛为源码骨架：保留 `music_metadata_graph/__init__.py` 和空的 `music_metadata_graph/pipelines/__init__.py`，不再保留活跃采集脚本、`scripts/`、`data/` 或 `reports/`。
- 已更新 `README.md`，说明项目进入请求顺序与数据库存储重新设计阶段，旧流程和数据已归档，新的正式流程尚未实现。
- 已更新 `pyproject.toml`，移除已归档脚本对应的 `mr-collect-hot-singers` 和 `mr-collect-high-confidence-songs` 命令入口，避免误运行旧流程。
- 已更新 `AGENTS.md` 项目补充规则，明确 `archive/redesign_reset_2026-05-13/` 和 `archive/legacy_pipeline_2026-05-12/` 只作为历史参考，不得作为当前正式流程继续运行或写回当前正式目录。
- 验证对象包括 README、AGENTS、develop_log、pyproject、归档清单编码与行尾、包骨架语法、pyproject 解析、当前根目录和归档统计；结果显示相关文本 UTF-8 可读、无 U+FFFD、无裸 LF，包骨架 `py_compile` 无报错，当前根目录不再存在 `data/`、`reports/` 或 `scripts/`。
- Git 状态复核因 Windows 仓库 owner 与当前用户 SID 不一致被 Git 判定为 dubious ownership 而失败，本次未修改全局 `safe.directory` 配置。

### 记录重新设计阶段先讨论关键未决问题
- 用户要求现在开始重新设计流程，并明确如果设计过程中存在用户没想清楚或没考虑周到的地方，AI 应停止设计并先与用户讨论，不应为了推进而设计一个糟糕方案。
- 已将该要求写入 `AGENTS.md` 用户长期偏好：重新设计请求顺序、存储结构、数据模型或流程边界时，如果存在关键目标、输入、输出、验收或风险未明确，AI 应先停止设计并与用户讨论，不得用未经确认的假设继续设计。
- 本次因此不直接给完整新流程，而是先梳理需要确认的关键设计问题。

### 准备完整歌手列表原生 JSON
- 用户要求重新设计一步一步来，第一步仍从请求完整歌手列表开始，并要求如果归档数据中已有这一步数据可以重新拿回来。
- 复核 `archive/redesign_reset_2026-05-13/` 和 `archive/legacy_pipeline_2026-05-12/` 后，未发现 `singer_list_index`、`singer_registry` 或 `hot_singer` 对应的原生 JSON 缓存，因此本次需要重新请求接口。
- 用户随后明确先不要入库，只把 JSON 准备好，以便查看有哪些键后再决定数据库设计。
- 已新增 `music_metadata_graph/pipelines/collect_singer_list_raw.py`，只请求 `qqmusic.singer.get_singer_list_index` 的完整分页并保存原生 JSON，不写数据库，不写 `data/processed/`。
- 已在 `pyproject.toml` 新增命令入口 `mr-collect-singer-list-raw`，对应当前已确认的 raw-only 第一步。
- 首次在沙箱内请求第一页因网络访问权限被拒绝失败；随后按权限规则放行网络后成功请求并保存第一页。
- 已运行完整歌手列表采集，输出目录为 `data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all/`；共保存 86 页原生 JSON，合计 6803 条歌手行，接口 `total` 也为 6803。
- 已只读检查字段键：顶层 JSON 键为 `area`、`code`、`genre`、`hotlist`、`index`、`sex`、`singerlist`、`tags`、`total`；`singerlist` 单行字段为 `id`、`mid`、`name`、`title`、`type`、`uin`、`pmid`、`area_id`、`country_id`、`country`、`other_name`、`spell`、`trend`、`concern_num`、`singer_pic`。
- 已更新 `README.md` 和 `AGENTS.md`，说明当前重新设计第一步只保存完整歌手列表原生 JSON，用于字段检查和后续数据库结构讨论。
- 本轮未设计数据库表、未入库、未生成 processed 产物。

### 生成请求 JSON 字段字典 xlsx
- 用户要求新建一个 xlsx 文档，记录每一步请求的 JSON 中包含的键和对应中文释义，每个 sheet 记录一种 JSON。
- 当前只存在重新设计第一步 `qqmusic.singer.get_singer_list_index` 的完整歌手列表原生 JSON，因此本次 xlsx 先创建一个 sheet：`01_singer_list_index`。
- 本机 Conda 环境未安装 `openpyxl` 或 `xlsxwriter`，因此未引入新依赖，改用 Python 标准库按 xlsx Open XML 结构生成工作簿。
- 已新增工具脚本 `music_metadata_graph/tools/write_request_json_key_dictionary.py`，用于从当前 raw JSON 生成 `docs/request_json_key_dictionary.xlsx`。
- 已生成 `docs/request_json_key_dictionary.xlsx`，记录完整歌手列表请求 JSON 的顶层键、`singerlist[]` 字段、`tags` 筛选项字段、字段出现次数、示例值和中文释义。
- 验证对象为 xlsx 文件结构和生成工具脚本；检查结果显示 xlsx 文件存在且非零，工作簿包含 sheet `01_singer_list_index`，sheet XML 中包含 `中文释义` 和 `singer_pic`，工具脚本 `py_compile` 无报错。

### 确认 QQ 音乐单数据源和歌手主键
- 用户确认当前项目只使用 QQ 音乐数据源，不再按多平台合并设计数据库结构。
- 用户确认歌手表使用 QQ 音乐 `mid` 作为主键，QQ 音乐数字 `id` 作为唯一字段，不额外引入内部 `artist_id`。
- 当前歌手入库字段范围先收敛为 `mid`、`id`、`name`、`other_name`、`pmid`、`singer_pic`、`spell`。
- 已将该约束写入 `AGENTS.md` 项目补充规则，作为后续数据库设计和实现依据。

### 导入完整歌手列表到 SQLite
- 用户要求把刚刚请求下来的完整歌手数据入数据库。
- 入库前只读检查 6803 条 raw 歌手行，确认 `mid` 缺失数为 0、`id` 缺失数为 0、重复 `mid` 数为 0、重复 `id` 数为 0，满足当前主键和唯一约束。
- 已新增 `music_metadata_graph/pipelines/import_singer_list_to_db.py`，从完整歌手列表 raw JSON 导入 SQLite。
- 已在 `pyproject.toml` 新增命令入口 `mr-import-singer-list-db`。
- 已创建数据库 `data/music_metadata_graph.sqlite3`，当前只包含 `singers` 表。
- `singers` 表 schema 为：`mid TEXT PRIMARY KEY`、`id INTEGER NOT NULL UNIQUE`、`name TEXT NOT NULL`、`other_name TEXT NOT NULL DEFAULT ''`、`pmid TEXT NOT NULL DEFAULT ''`、`singer_pic TEXT NOT NULL DEFAULT ''`、`spell TEXT NOT NULL DEFAULT ''`。
- 导入结果为 raw 行数 6803、导入行数 6803、数据库 `singers` 表行数 6803。
- 抽查数据库前三行对应周杰伦、林俊杰、陈奕迅，字段值与 raw JSON 中的 `mid`、`id`、`name`、`other_name`、`singer_pic` 和 `spell` 对应。
- 验证对象为导入脚本语法、`pyproject.toml` 命令入口、SQLite schema、行数和样例查询；除一次验证查询命令因 PowerShell 引号写错导致 SyntaxError 外，重新查询后观察结果符合预期。

### 恢复四位歌手主页歌曲 Tab raw JSON 并更新字段字典
- 用户提出第二步应直接请求歌手全量歌曲作为全量源数据，避免先请求不完整集合再反复补齐。
- 用户明确正式流程当然是请求全部歌手的全部歌曲，但当前只是构建流程，开发阶段只用指定四位歌手：周杰伦、薛之谦、林俊杰、汪苏泷。
- 用户确认全量接口使用主页歌曲接口，并要求如果归档中已有请求数据就直接拿回来用；本轮先不入库，只确认请求到的 JSON 结构，并在 xlsx 中新增第二个 sheet 记录歌曲 JSON 键结构。
- 复核 `archive/redesign_reset_2026-05-13/data/raw/qqmusic/singer_homepage_song_tab/` 后确认归档中已有四位歌手主页歌曲 Tab raw JSON：周杰伦 `0025NhlN2yWrP4`、薛之谦 `002J4UUk29y8BY`、林俊杰 `001BLpXF2DyJe2`、汪苏泷 `001z2JmX09LLgL`。
- 已将归档中的 `singer_homepage_song_tab` raw JSON 复制回当前 `data/raw/qqmusic/singer_homepage_song_tab/`，复制后核对文件数和字节数一致：118 个 JSON 文件，14564795 字节。
- 当前四位歌手 raw 行数为：周杰伦 34 页 1012 行，薛之谦 18 页 528 行，林俊杰 34 页 1013 行，汪苏泷 32 页 939 行，合计 118 页 3492 行。
- 已只读分析主页歌曲 Tab JSON 结构：顶层键包括 `AlbumTab`、`ArtistWorksTab`、`CalendarTab`、`DiscTab`、`HasMore`、`IntroductionTab`、`MomentTab`、`NeedShowTab`、`Order`、`PersonalTab`、`PutaoProductTab`、`ShowTab`、`SongTab`、`TabID`、`TabList`、`VideoTab`；`SongTab` 键包括 `IsShowQLIcon`、`List`、`SearchText`、`SongTagInfoList`。
- 已分析 `SongTab.List[]` 歌曲行结构，四位样本 3492 行均包含 42 个顶层字段，包括 `id`、`mid`、`name`、`title`、`subtitle`、`singer`、`album`、`interval`、`time_public`、`file`、`pay`、`action` 等。
- 已扩展 `music_metadata_graph/tools/write_request_json_key_dictionary.py`，支持一个 xlsx 写多个 sheet，并新增 `02_singer_song_tab` sheet。
- 已重新生成 `docs/request_json_key_dictionary.xlsx`，当前包含 `01_singer_list_index` 和 `02_singer_song_tab` 两个 sheet；第二个 sheet 记录主页歌曲 Tab 顶层键、`SongTab` 字段、`SongTab.List[]` 歌曲字段和常见嵌套字段。
- 验证对象为恢复后的 raw JSON、xlsx 工作簿和字段字典生成脚本；结果显示四位歌手页数和行数符合归档统计，xlsx 文件包含两个 sheet，第二个 sheet XML 包含 `SongTab`、`album`、`singer` 和 `time_public`，脚本 `py_compile` 无报错。
- 本轮未请求网络、未入库、未设计歌曲表。

### 建立独立主页歌曲 Tab 请求脚本
- 用户确认上一轮只是使用归档数据，因此没有建立主页歌曲请求脚本，并要求把脚本补上。
- 用户要求主页歌曲请求脚本不要和第一步完整歌手列表请求脚本混在一起。
- 用户要求歌曲请求脚本支持正式全量请求，以及指定 `id` 列表、`mid` 列表、歌手名列表三种部分请求。
- 用户要求部分请求时必须先验证每一个目标歌手都存在于数据库 `singers` 表；只要任意一个不存在，就不应该开始请求。
- 用户确认刚刚从归档恢复的四位歌手主页歌曲 raw JSON 可以视为指定四个人的部分请求结果。
- 已新增独立脚本 `music_metadata_graph/pipelines/collect_singer_song_tab_raw.py`，使用 `client.singer.get_tab_detail(singer_mid, TabType.SONG, num=30, page=page)` 请求主页歌曲 Tab，并将原生 JSON 写入 `data/raw/qqmusic/singer_homepage_song_tab/<mid>/page_XXXX_size_30.json`。
- 已在 `pyproject.toml` 新增命令入口 `mr-collect-singer-song-tab-raw`。
- 脚本支持 `--all` 全量请求数据库中所有歌手，也支持 `--mid`、`--id`、`--name` 三种部分请求参数；参数可重复，也支持逗号分隔。
- 部分请求解析阶段会查询 `data/music_metadata_graph.sqlite3` 的 `singers` 表；若任意目标不存在，脚本抛出错误并停止，不进入请求循环。
- 已用四位歌手歌手名执行部分请求验证，所有 118 页均为 `cache_hit`，合计 3492 行，未发起新网络请求。
- 已分别用 `--mid 0025NhlN2yWrP4` 和 `--id 4558` 加 `--max-pages-per-singer 1` 验证部分请求参数，均命中周杰伦第一页缓存。
- 已用不存在的 `--mid not_exists_mid` 验证失败路径，脚本在目标解析阶段报错 `Singer targets not found in database`，未开始请求循环。
- 验证对象为新脚本语法、四位歌手缓存请求、`mid`/`id` 参数请求和不存在目标失败路径；观察结果符合“先验证数据库目标，再请求或读取缓存”的设计。

### 为歌手表补充 raw JSON 追溯字段
- 用户确认当前数据库只有 `singers` 表，并询问是否需要额外保存 JSON 路径。
- 已形成判断：歌手表不应保存完整原生 JSON，但应保存轻量追溯字段，便于定位回 `data/raw/` 中的原始分页文件和行号。
- 已修改 `music_metadata_graph/pipelines/import_singer_list_to_db.py`，为导入行补充 `raw_json_path`、`raw_page` 和 `raw_row_index`。
- 已为 `singers` 表增加迁移逻辑：如果旧表缺少 `raw_json_path`、`raw_page` 或 `raw_row_index`，导入脚本会自动 `ALTER TABLE` 补列。
- 已重跑 `python -m music_metadata_graph.pipelines.import_singer_list_to_db`，数据库仍为 6803 行。
- 当前 `singers` 表字段为 `mid`、`id`、`name`、`other_name`、`pmid`、`singer_pic`、`spell`、`raw_json_path`、`raw_page`、`raw_row_index`。
- 验证结果显示 6803 行均有非空 raw 追溯信息，前三行分别定位到 `page_0001_size_80.json` 的第 1、2、3 行。
- 本次未新增其他数据库表。

### 确认歌曲表不记录来源主页关系
- 用户指出判断歌曲 `mid` 是否能作主键时，关键不是同一 `mid` 是否出现在多个歌手主页，而是同一 `mid` 对应的歌曲对象内容是否完全相同。
- 已按当前四位样本检查 13 组重复 `song_mid`，对完整 `SongTab.List[]` 歌曲对象进行排序 JSON 序列化和哈希比较，结果显示 13 组重复 `song_mid` 的完整对象均完全一致，差异组数为 0。
- 用户进一步确认来源不重要，只要记录歌曲即可。
- 已将该决策写入 `AGENTS.md` 项目补充规则：歌曲表只记录唯一歌曲实体，不记录歌曲来自哪个歌手主页的来源关系；QQ 音乐歌曲 `mid` 作为主键，除非后续用户明确要求恢复来源追溯。
- 后续歌曲入库设计应围绕唯一 `songs` 表和必要关系表进行，不再设计 `song_sources` 或 `raw_song_id` 作为必需表。

### 设计歌曲完整表和完备表分层
- 用户要求按“完整表”和“从完整表筛选出来的完备表”重新设计歌曲入库结构。
- 当前设计依据为：完整表用于接住主页歌曲接口中按 `song_mid` 去重后的唯一歌曲实体；完备表用于保存满足后续分析最低结构要求的歌曲。
- 完备表筛选条件按此前讨论暂定为 `mid`、`id`、演唱者、`language`、`album_mid` 必须非空。
- 当前四位样本已知风险是 `album_mid` 为空的歌曲较多，因此完备表会明显少于完整表；需要通过过滤结果表记录被排除原因。
- 复核当前四位歌手主页歌曲样本后确认 raw 行数为 3492，按 `song_mid` 去重后为 3479 首唯一歌曲，13 条重复 `song_mid` 行的完整歌曲对象均完全一致，未发现同一 `song_mid` 对应不同对象的冲突。
- 若完备表要求 `id`、`name`、`title`、`language`、`album_mid`、歌手列表和每个歌手 `singer_mid` 均非空，当前样本中可进入完备表的唯一歌曲为 1809 首。
- 当前样本中唯一歌曲层面的主要筛除原因是 `album_mid` 缺失，共 1668 首；另有 18 首存在歌手条目缺少 `singer_mid`；`language` 和歌手列表本身未发现缺失。
- 初步建议完整表和完备表都以 QQ 音乐歌曲 `mid` 为主键；完整表允许 `album_mid` 和关系表中的 `singer_mid` 缺失以保留事实，完备表只接收满足约束的子集。
- 已识别未决点：若要求 `album_mid` 作为外键，必须先设计或生成专辑表；在专辑表未建立前只能先把 `album_mid` 作为非空字段，暂不启用外键约束。
- 用户进一步确认完备歌曲表不应另行设计独立 `song_singers` 关系表；关系表应统一服务完整歌曲和完备歌曲，完备歌曲通过筛选条件或视图查询得到对应关系。
- 用户指出过滤记录表不应使用自增 id，而应围绕歌曲 `mid` 记录；数据库化之后所有歌曲可统一记录在一个过滤记录表中，查看时通过条件筛选，不再每次过滤写一个独立表。
- 已据此调整设计：`song_singers` 统一以 `(song_mid, singer_order)` 为主键并关联完整歌曲表；`singer_mid` 在完整层允许为空，完备性由过滤状态表和查询条件判断。
- 已据此调整设计：过滤状态表以 `song_mid` 为主键，保存当前完备性判断、筛除原因摘要和检查时间；若后续需要多个原因的结构化查询，可再加以 `(song_mid, reason_code)` 为主键的原因明细表。
- 已抽查缺少歌手 `singer_mid` 的真实例子，包括《飞云之下》中 `072-韩红`、《我们的爱 (消音伴奏)》中 `G.E.M.邓紫棋`、《微音乐剧：每道光》中 `世界技能大赛中国获奖选手代表`、《剑魂 (Live)》中 `王可乔` 和 `李豪横` 等。

### 导入歌曲完整表和歌曲歌手关系表
- 用户确认歌曲完整表已无争议，只要歌曲 `mid` 和 `id` 非空即可写入，并要求先把完整表和关系表入库。
- 已新增 `music_metadata_graph/pipelines/import_singer_song_tab_to_db.py`，独立负责从 `data/raw/qqmusic/singer_homepage_song_tab/` 读取主页歌曲 Tab raw JSON 并写入 SQLite。
- 已在 `pyproject.toml` 增加脚本入口 `mr-import-singer-song-tab-db`。
- 新增 `songs_all` 表作为歌曲完整表，字段为 `mid`、`id`、`name`、`title`、`time_public`、`language`、`album_mid`、`raw_json_path`、`raw_page`、`raw_row_index`；其中 `mid` 为主键、`id` 为唯一非空字段。
- 新增 `song_singers` 表作为唯一歌曲-歌手关系表，字段为 `song_mid`、`singer_order`、`singer_mid`、`singer_id`、`singer_name`，主键为 `(song_mid, singer_order)`。
- 当前未给 `song_singers.singer_mid` 增加到 `singers.mid` 的外键，因为当前四位歌手样本中歌曲关系涉及 578 个非空歌手 `mid`，其中 331 个未出现在当前 `singers` 表；若强制外键会导致真实数据无法导入。
- 导入脚本对同一 `song_mid` 执行完整 payload 去重检查；当前样本中 13 条重复 `song_mid` 行均与已有 payload 完全一致，未发现冲突。
- 已执行 `python -m music_metadata_graph.pipelines.import_singer_song_tab_to_db`，结果为 raw 歌曲行 3492、唯一歌曲 3479、缺 `mid` 或 `id` 跳过 0、导入 `songs_all` 3479 行、导入 `song_singers` 5114 行。
- 验证结果显示 `song_singers` 中缺 `singer_mid` 的关系行有 22 行，非空但未进入当前 `singers` 表的关系行有 573 行；这说明关系表应先保存事实，再通过后续完备性过滤或歌手补全处理。
- 已同步更新 `README.md` 的 SQLite 入库说明，移除“当前只包含一张表”的过期描述，并补充 `songs_all`、`song_singers` 的字段和当前导入行数。
- 已执行语法验证，`import_singer_song_tab_to_db.py`、`import_singer_list_to_db.py` 和 `collect_singer_song_tab_raw.py` 均通过 `py_compile`。
- 已查询 SQLite schema 和样例数据，确认当前表为 `singers`、`songs_all`、`song_singers`，行数分别为 6803、3479、5114；`songs_all` 无空 `mid` 或空 `id`，`song_singers` 无空 `song_mid`。
- 尝试执行 `git status --short` 时被 Git dubious ownership 保护阻止；未擅自修改全局 `safe.directory` 配置。

### 设计采集即入库的数据库 UML
- 用户要求继续保留接口原生 JSON，同时采集后写入数据库，并要求设计数据库结构、类、主键、属性和可粘贴到 PlantText 的 UML 代码。
- 设计目标调整为：接口响应保存到 `data/raw/` 作为原始证据，同步登记到数据库原始记录表；清洗流程不再读取 JSON 文件，而是读取数据库中的 staging 表、pipeline 行状态表和最终实体关系表。
- 形成的核心类包括运行类 `PipelineRun`、原始记录类 `SourceRecord`、平台实体类 `Artist`、`Album`、`Song`、关系类 `SongArtist`、`ArtistAlbumCandidate`、清洗行状态类 `PipelineSongRow` 和最终关系边类 `CreditEdge`。
- 主键设计原则为内部数据库使用整数自增主键，平台身份通过 `source_platform + source_id/source_mid` 唯一约束表达；`PipelineSongRow` 用独立行主键保存每一步过滤状态，避免覆盖历史步骤。
- 审计设计要求每个清洗行状态关联 `PipelineRun`、目标歌手、歌曲、专辑、分支、步骤、结果、原因和 `SourceRecord`，确保可以查询每一步保留行和被过滤行，并追溯到原生 JSON 缓存路径。
- 本轮只产出 UML 设计和说明，不实现数据库代码、不修改 pipeline、不迁移既有 JSON/CSV 数据。

### 设计采集入库后的数据库逻辑结构
- 用户进一步确认可以保存原生 JSON，同时写入数据库，以保留原始响应，并询问数据库结构如何设计、需要几个类、每个类的主键和属性。
- 当前结构设计目标调整为：原生 JSON 文件继续作为原始响应证据和可重放缓存；数据库承担正式处理链路，包括原始响应索引、staging 结构化展开、过滤步骤审计、最终实体表、关系边和导出视图。
- 初步推荐以 SQLite 为第一阶段数据库，并以表/类的形式划分为四层：采集审计层、staging 层、标准实体层、pipeline 审计和导出层。
- 采集审计层建议包含 `SourceRecord` 和 `PipelineRun`：前者记录平台、接口、请求参数、缓存路径、响应状态、抓取时间和原始 payload 摘要；后者记录一次 pipeline 运行的分支、参数、开始结束时间、代码版本和运行状态。
- 标准实体层建议包含 `Artist`、`Album`、`Song`、`SongArtist` 和 `CreditEdge`：实体主键使用平台身份键优先，例如 `qqmusic:artist_mid:<mid>`、`qqmusic:album_mid:<mid>`、`qqmusic:song_mid:<mid>`；没有平台 ID 的制作人员先用 unresolved credit key，不能只按姓名合并。
- staging 层建议包含 `StagingArtistRow`、`StagingAlbumRow` 和 `StagingSongRow`，用于保存采集响应中展开出的原始顶层字段和 `aux_` 辅助字段，主键为行级 `staging_row_id`，并通过 `source_record_id` 追溯到原始 JSON。
- pipeline 审计层建议包含 `PipelineSongRow` 和 `PipelineStepStat`：前者按 `run_id`、分支、目标歌手、步骤、结果、原因记录每一步歌曲行状态；后者保存每一步计数，便于替代当前 summary JSON。
- 设计注意事项包括：不要过早删除 staging 行；每一步过滤必须保留 kept 和 removed；同名去重选择结果需要记录被选中的歌曲 key、专辑类型优先级和数值歌曲 id；网页和 CSV 都应从数据库视图导出，而不是重新读取 JSON 文件。

### 建立歌手专辑列表 raw JSON 请求流程
- 用户要求在歌手列表入库和主页歌曲请求之间插入独立流程：先请求每个歌手的专辑列表，并根据 JSON 结构更新 xlsx 字段字典。
- 用户要求当前开发阶段仍只使用周杰伦、薛之谦、林俊杰、汪苏泷四名歌手；归档数据如可用可以恢复，但脚本必须补上。
- 已确认归档 `archive/redesign_reset_2026-05-13/data/raw/qqmusic/high_confidence_singer_songs/` 中存在四位歌手的 `singer_album_list` raw JSON 缓存。
- 已将四位歌手专辑列表 raw JSON 恢复到当前正式目录 `data/raw/qqmusic/singer_album_list/<singer_mid>/`，共 11 个分页 JSON。
- 已新增独立脚本 `music_metadata_graph/pipelines/collect_singer_album_list_raw.py`，使用 `client.singer.get_album_list(singer_mid, num=30, page=page)` 请求歌手专辑列表。
- 已在 `pyproject.toml` 新增命令入口 `mr-collect-singer-album-list-raw`。
- 新脚本支持 `--all` 全量请求，也支持 `--mid`、`--id`、`--name` 三种部分请求参数；参数可重复，也支持逗号分隔。
- 部分请求解析阶段会查询 SQLite 的 `singers` 表；若任意目标不存在，脚本抛出 `Singer targets not found in database` 并停止，不进入请求循环。
- 已用四位歌手姓名执行部分请求验证，所有 11 页均为 `cache_hit`，未发起新网络请求；结果为周杰伦 2 页 43 行、薛之谦 2 页 32 行、林俊杰 3 页 76 行、汪苏泷 4 页 117 行，合计 268 行。
- 已用不存在的 `--mid not_exists_mid` 验证失败路径，脚本在目标解析阶段报错，未开始请求循环。
- 已扩展 `music_metadata_graph/tools/write_request_json_key_dictionary.py`，新增 `02_singer_album_list` sheet，并将主页歌曲 Tab sheet 调整为 `03_singer_song_tab`。
- 已重新生成 `docs/request_json_key_dictionary.xlsx`，当前 sheet 为 `01_singer_list_index`、`02_singer_album_list`、`03_singer_song_tab`；验证确认 xlsx 中包含 `albumMid`、`albumName`、`albumType`、`publishDate`、`totalNum`、`singerMid` 等专辑列表字段。
- 已同步更新 `README.md`，将当前流程顺序调整为完整歌手列表 raw、歌手列表入库、歌手专辑列表 raw、主页歌曲 Tab raw，并记录四位歌手专辑列表缓存统计。
- 验证对象为新增脚本语法、四位歌手缓存请求、缺失目标失败路径、xlsx sheet 和关键字段；观察结果符合预期。

### 建立专辑详情 raw JSON 请求流程
- 用户要求在请求专辑列表后增加请求专辑详情的流程和脚本，并在 xlsx 字段字典中补充专辑详情结构。
- 已新增独立脚本 `music_metadata_graph/pipelines/collect_album_detail_raw.py`，读取 `data/raw/qqmusic/singer_album_list/<singer_mid>/` 中的 `albumMid`，再调用 `client.album.get_detail(album_mid)` 请求专辑详情。
- 已在 `pyproject.toml` 新增命令入口 `mr-collect-album-detail-raw`。
- 脚本支持 `--all`，也支持 `--mid`、`--id`、`--name` 三种指定歌手方式；指定歌手时会先校验目标存在于 `singers` 表，并要求对应专辑列表 raw JSON 已存在。
- 已从归档 `archive/redesign_reset_2026-05-13/data/raw/qqmusic/supplement_album_details/` 恢复当前四位歌手专辑列表可对应的 251 个专辑详情缓存到 `data/raw/qqmusic/album_detail/`。
- 当前四位歌手专辑列表共 268 个唯一 `albumMid`；归档缺失 17 个专辑详情，已按权限规则放行网络后请求补齐。
- 已执行 `python -m music_metadata_graph.pipelines.collect_album_detail_raw --name 周杰伦 --name 薛之谦 --name 林俊杰 --name 汪苏泷`，结果为 albums 268、cache_hits 251、fetched 17。
- 已扩展 `music_metadata_graph/tools/write_request_json_key_dictionary.py`，新增 `03_album_detail` sheet，并将主页歌曲 Tab sheet 调整为 `04_singer_song_tab`。
- 已重新生成 `docs/request_json_key_dictionary.xlsx`，当前 sheet 为 `01_singer_list_index`、`02_singer_album_list`、`03_album_detail`、`04_singer_song_tab`；验证确认专辑详情 sheet 包含 `album_type`、`company`、`singers`、`time_public`、`language`、`desc` 等字段。
- 已同步更新 `README.md`，记录专辑详情 raw JSON 目录、请求脚本、四位歌手 268 个详情文件统计和当前流程顺序。
- 验证结果显示当前数据库仍只包含 `singers` 表，未新增专辑表或歌曲表；新增脚本和字段字典脚本均通过 `py_compile`。

### 删除专辑详情流程并导入专辑列表表
- 用户判断专辑详情补充信息没有足够价值，要求删除刚刚新增的专辑详情请求流程、脚本、请求到的数据和 xlsx 中的 sheet，但在日志中记录补充信息的键。
- 已统计被删除前的 268 个专辑详情 JSON 结构：顶层键包括 `basicInfo`、`company`、`singer`、`album`、`singers`。
- 专辑详情中 `basicInfo` 出现 17 次，包含 `albumMid`、`albumName`、`tranName`、`publishDate`、`desc`、`genre`、`language`、`albumType`、`genreURL`、`lanURL`、`albumTag3`、`recordNum`、`albumID`、`pmid`、`type`、`modifyTime`、`color`、`fpaymid`、`topListContent`、`topListSchema`、`adStatus`、`encourageVideoStatus`、`wikiurl`、`awards`、`LanRenBookUrl`、`adJson`、`vid`、`operateStatus`、`genres`、`album_right`、`adTag`、`headVideoVid`、`headVideoFrame`、`headMediaList`、`brand`、`albumDuration`、`recText`、`recLabels`、`genreNew`、`bookletUrl`、`singerInterpretation`、`bookletUrlNew`、`debutBtn`、`isReserved`、`reservedTotalCnt`、`dynamicCoverVid`、`threeDUrl`、`album_right_new`。
- 专辑详情中 `album` 出现 251 次，包含 `id`、`mid`、`name`、`title`、`subtitle`、`time_public`、`pmid`、`desc`、`language`、`album_type`、`genre`、`wikiurl`。
- 专辑详情中 `company` 出现 268 次，字段口径有两种：17 条包含 `ID`、`name`、`headPic`、`isShow`、`brief`；251 条包含 `id`、`name`、`is_show`、`brief`。
- 专辑详情中 `singer` 出现 17 次，包含 `singerList`；`singers[]` 出现 251 组详情中的署名歌手条目，条目字段包括 `id`、`mid`、`name`、`title`、`type`、`uin`、`pmid`。
- 已删除 `music_metadata_graph/pipelines/collect_album_detail_raw.py`，并从 `pyproject.toml` 删除 `mr-collect-album-detail-raw` 命令入口。
- 已删除 `data/raw/qqmusic/album_detail/` 目录，移除本轮专辑详情 raw JSON。
- 已从 `music_metadata_graph/tools/write_request_json_key_dictionary.py` 删除专辑详情 sheet 生成逻辑，并重新生成 `docs/request_json_key_dictionary.xlsx`；当前 sheet 恢复为 `01_singer_list_index`、`02_singer_album_list`、`03_singer_song_tab`。
- 用户要求请求专辑列表后直接把专辑表入库，专辑表主键为 `mid`，属性包括 `id`、`name`、`type`、`publishDate`、`singerName`。
- 已检查当前四位歌手专辑列表 268 行，`albumMid`、`albumID`、`albumName`、`albumType`、`publishDate`、`singerName` 均无缺失；`albumMid` 唯一 268 个，无重复。
- 已检查当前四位歌手专辑列表的 `singerName`，并确认不是所有专辑署名都是单人：当前有 66 种署名文本，其中 65 行包含 `/`、`、`、`,`、`，` 或 `&` 等多人署名迹象；因此 `singerName` 先作为文本属性保存，不作为歌手外键。
- 已新增 `music_metadata_graph/pipelines/import_singer_album_list_to_db.py`，从 `data/raw/qqmusic/singer_album_list/` 读取专辑列表 raw JSON 并写入 SQLite。
- 已在 `pyproject.toml` 新增 `mr-import-singer-album-list-db` 命令入口。
- 新增 `albums` 表，字段为 `mid`、`id`、`name`、`type`、`publishDate`、`singerName`、`raw_json_path`、`raw_page`、`raw_row_index`；其中 `mid` 为主键，`id` 为唯一非空字段。
- 已执行 `python -m music_metadata_graph.pipelines.import_singer_album_list_to_db`，结果为 raw album rows 268、unique album rows 268、skipped missing mid or id 0、duplicate same album rows 0、imported albums 268、db album rows 268、multi-like singerName rows 65。
- 已同步更新 `README.md`，删除专辑详情流程说明，补充 `albums` 表字段、导入入口、导入行数和 `singerName` 不作外键的原因。

### 纠正歌曲数据库职责边界
- 用户重新评估后指出：歌曲入库应只写入完备歌曲，而不是先把完整歌曲写入数据库再从完整表筛选完备表。
- 用户明确完整数据的职责应由原始 JSON 提供，数据库应承载后续可分析、可约束、结构化程度足够的数据。
- 已形成新的设计方向：取消或不再继续使用 `songs_all` 作为正式歌曲实体表，正式歌曲表应直接命名为 `songs` 或等价名称，并只接收满足完备条件的歌曲。
- 新方向下，`song_singers` 应只服务正式完备歌曲，`song_mid` 可外键到正式歌曲表；若要求 `singer_mid` 外键到 `singers.mid`，则缺失或无法匹配歌手维表的歌曲不能入正式歌曲表。
- 已识别待讨论点：是否需要保留数据库内的导入拒绝记录表，或只用 raw JSON 加导入报告记录未入库原因；该点会影响是否还需要 `song_filter_status`。

### 删除试验性歌曲完整表入库实现
- 用户要求删除刚刚新增的歌曲入库脚本和数据库中的新增两张表，并汇报保留下来的流程。
- 已删除 `music_metadata_graph/pipelines/import_singer_song_tab_to_db.py`。
- 已从 `pyproject.toml` 删除 `mr-import-singer-song-tab-db` 命令入口。
- 已在 SQLite 中执行 `DROP TABLE IF EXISTS song_singers` 和 `DROP TABLE IF EXISTS songs_all`，仅删除本轮试验性歌曲完整表和关系表。
- 已更新 `README.md`，将 SQLite 当前状态改回只保留 `singers` 表，并说明歌曲数据目前只保留 raw JSON，后续歌曲数据库结构将重新设计为只写入完备歌曲。
- 验证结果显示当前数据库表清单仅为 `singers`，`singers` 行数仍为 6803，四位歌手主页歌曲 raw JSON 仍为 118 个文件。
- 验证结果显示 `import_singer_song_tab_to_db.py` 已不存在，当前脚本入口仅保留完整歌手列表采集、歌手列表入库和主页歌曲 Tab raw 采集三个入口。
- 已执行语法验证，`import_singer_list_to_db.py`、`collect_singer_list_raw.py` 和 `collect_singer_song_tab_raw.py` 均通过 `py_compile`。

### 纠正专辑请求来源和时机
- 用户指出专辑列表来源和请求时机有问题：专辑信息不应在请求歌曲前按歌手请求，而应先请求歌曲，再按歌曲中的专辑请求专辑信息。
- 已将旧 `data/raw/qqmusic/singer_album_list/` 移入 `archive/album_source_retiming_2026-05-13/`，当前正式 raw 目录不再保留旧歌手专辑列表。
- 已将旧 SQLite `albums` 表导出到本次归档目录，并从当前数据库删除旧 `albums` 表；当前数据库表清单恢复为仅 `singers`。
- 已删除旧歌手专辑列表请求脚本和旧专辑列表入库脚本，并从 `pyproject.toml` 删除对应命令入口。
- 已新增 `music_metadata_graph/pipelines/collect_song_album_detail_raw.py`，脚本读取歌手主页歌曲 Tab raw JSON，从 `album.mid` 或非 0 `album.id` 去重得到专辑请求键，再调用 `qqmusic.album.get_detail` 保存原生 JSON 到 `data/raw/qqmusic/song_album_detail/`。
- 新脚本支持 `--all` 全量请求，也支持 `--mid`、`--id`、`--name` 三种指定歌手方式；指定歌手时会先校验目标存在于 `singers` 表，并要求对应主页歌曲 Tab raw JSON 已存在。
- 初次请求时发现歌曲中存在 `album.id = 0` 且 `album.mid` 为空的情况，若把 0 当作请求键会触发接口错误；已修正为只把非空 `album.mid` 或非 0 `album.id` 作为可请求专辑键。
- 已按四位开发阶段歌手周杰伦、薛之谦、林俊杰、汪苏泷请求新的专辑详情 raw JSON；输入主页歌曲行 3492，缺少可请求专辑键的歌曲行 1676，去重后专辑详情 654 个，当前 `data/raw/qqmusic/song_album_detail/` 中有 654 个 JSON 文件。

### 更新字段字典和流程文档为歌曲派生专辑详情
- 已更新 `music_metadata_graph/tools/write_request_json_key_dictionary.py`，删除旧歌手专辑列表 sheet 生成逻辑，新增 `02_song_album_detail` sheet，记录 `qqmusic.album.get_detail` 的 `basicInfo`、`company`、`singer` 和 `singer.singerList[]` 等字段。
- 已重新生成 `docs/request_json_key_dictionary.xlsx`；当前 sheet 为 `01_singer_list_index`、`02_song_album_detail`、`03_singer_song_tab`，不再包含 `02_singer_album_list`。
- 已更新 `README.md`，把当前流程调整为完整歌手列表 raw、歌手列表入库、主页歌曲 Tab raw、按歌曲请求专辑详情 raw，并说明专辑入库规则尚待基于新详情 JSON 重新确认。
- 已更新 `AGENTS.md` 项目补充规则，记录旧歌手专辑列表不得继续作为正式专辑来源，后续专辑入库需要基于 `song_album_detail` 的 `basicInfo` 和 `singer.singerList[]` 重新设计。
- 验证对象为新脚本语法、字段字典脚本语法、xlsx sheet 名和关键字段、SQLite 表清单、旧 raw 目录迁移状态和新 raw 文件数量。
- 验证结果显示 `collect_song_album_detail_raw.py` 与字段字典脚本均通过 `py_compile`；xlsx 存在且包含 `basicInfo`、`albumMid`、`albumName`、`albumType`、`singerList`，不包含旧 `02_singer_album_list`；SQLite 当前仅有 `singers` 表且行数为 6803；旧正式 raw 目录 `data/raw/qqmusic/singer_album_list/` 不存在，归档目录存在；新 `song_album_detail` JSON 文件数为 654。

### 检查歌曲派生专辑详情字段和多歌手结构
- 用户要求检查两件事：新请求的专辑信息是否包含之前约定的键，以及多歌手专辑在新 JSON 中如何记录并给出样本。
- 已检查当前 `data/raw/qqmusic/song_album_detail/` 下 654 个专辑详情 JSON。
- 之前约定的专辑入库键在新结构中对应为：`mid` 对应 `$.basicInfo.albumMid`，`id` 对应 `$.basicInfo.albumID`，`name` 对应 `$.basicInfo.albumName`，`type` 对应 `$.basicInfo.albumType`，`publishDate` 对应 `$.basicInfo.publishDate`。
- 654 个 JSON 中上述 5 个专辑基础字段均存在且均非空，`albumID` 均为非 0 整数。
- 旧约定中的 `singerName` 不再以单个标量字段出现；新详情接口通过 `$.singer.singerList[]` 记录署名歌手列表，若继续保留 `singerName` 字段，需要从 `singerList[].name` 派生拼接文本。
- 当前 654 个专辑详情中 `singer.singerList` 均存在且非空；署名歌手数量分布为单歌手 594 张，多歌手 60 张，最多 59 个署名歌手。
- `singer.singerList[]` 条目字段包括 `mid`、`name`、`transName`、`role`、`instrument`、`singerID`、`type`、`singerType`、`pmid`、`indentity`。
- 904 个署名歌手条目中有 1 个缺少 `mid`：专辑 `Promise To You` 中汪苏泷条目为 `mid=""`、`singerID=0`、`pmid=""`；这说明后续若建立专辑-歌手关系，不能无条件要求每个详情署名歌手都能马上外键到 `singers.mid`。
- 多歌手样本包括 `Season for Love`，署名歌手为汪苏泷和 Lenka；`爱你 影视原声带`，署名歌手包含汪苏泷、颜人中、米卡、符雅凝等 11 人；`新年到`，署名歌手包含林俊杰、林宇中、李志清、BY2 等 12 人。

### 导入歌曲派生专辑详情表
- 用户确认下一步做专辑入库，要求不导入歌手信息，只导入五个业务键：`mid` 主键、`id`、`name`、`albumType`、`publishDate`。
- 用户同时要求每个入库表都带三个跟文件路径有关的追溯键；本次专辑表补充 `raw_json_path`、`raw_page`、`raw_row_index`。
- 已新增 `music_metadata_graph/pipelines/import_song_album_detail_to_db.py`，从 `data/raw/qqmusic/song_album_detail/*.json` 读取 `basicInfo` 并写入 SQLite。
- 已在 `pyproject.toml` 新增命令入口 `mr-import-song-album-detail-db`。
- 新增 `albums` 表，字段为 `mid`、`id`、`name`、`albumType`、`publishDate`、`raw_json_path`、`raw_page`、`raw_row_index`；其中 `mid` 为主键，`id` 为唯一非空字段。
- 对专辑详情这种“一文件一专辑”的请求，`raw_page` 固定为 0，`raw_row_index` 固定为 1。
- 已执行 `python -m music_metadata_graph.pipelines.import_song_album_detail_to_db`，结果为 raw rows 654、imported rows 654、db rows 654。
- 已更新 `README.md`，记录当前数据库表为 `singers`、`albums`，并补充专辑表字段、字段来源、导入入口和当前行数。
- 已更新 `AGENTS.md` 项目补充规则，记录专辑表只从 `song_album_detail` 的 `basicInfo` 抽取核心字段，当前不导入 `singer.singerList[]`。
- 验证对象为导入脚本语法、导入结果、SQLite schema、主键和唯一约束、必填字段缺失情况和样例行。
- 验证结果显示导入脚本通过 `py_compile`；当前数据库表为 `albums`、`singers`；`albums` 行数为 654，`singers` 行数为 6803；`albums.mid` 为主键，`albums.id` 为唯一索引；`name`、`albumType`、`publishDate`、`raw_json_path` 均无空值。

### 评估歌曲直接入完备表约束
- 用户要求重新考虑歌曲是否可以直接入完备表，并给出约束：`song.mid` 非空唯一作主键，`song.id` 非空唯一，`song.name/title` 非空，`language` 非空，`album_mid` 非空且外键到专辑表，`singer` 列表非空，每个 `singer_mid` 非空且外键到歌手表。
- 已基于当前四位歌手主页歌曲 raw JSON、当前 `albums` 表和 `singers` 表模拟该约束，未执行歌曲入库。
- 当前样本有主页歌曲 raw 行 3492，按 `song.mid` 去重后唯一歌曲 3479；13 组重复 `song.mid` 的完整歌曲对象一致，未发现冲突；`song.id` 在唯一歌曲中无重复。
- 严格执行上述约束时可入库唯一歌曲为 1539 首，被拒绝 1940 首。
- 拒绝原因按唯一歌曲计数为：`missing_album_mid` 1668 首，`singer_mid_not_in_singers` 366 首，`missing_singer_mid` 18 首；同一首歌可同时命中多个原因。
- 当前专辑表覆盖所有非空 `album_mid`，本轮未发现 `album_mid_not_in_albums`；说明先按歌曲请求专辑详情再入库专辑，能满足歌曲外键到专辑表的前置条件。
- 当前未发现 `song.mid`、`song.id`、`name`、`title`、`language` 或 `singer` 列表为空导致的拒绝；注意 `language=0` 是有效语言编码，不能按布尔假值当作空。
- 若暂不要求每个演唱者外键到 `singers.mid`，可入库上限为 1811 首；因此当前严格方案额外排除了 272 首主要由补充歌手未在 `singers` 表导致的歌曲。
- 典型 `missing_album_mid` 样本包括《有我 (Demo)》、《背对背拥抱 + 她说 (Live)》、《微笑上海》；典型 `singer_mid_not_in_singers` 样本包括《绝不绝》中的“无畏契约”、《Hanggang》中的 Troy Laureta、《At Least I Had You》中的 Gentle Bones；典型 `missing_singer_mid` 样本包括《飞云之下》中的 `072-韩红`、《我们的爱 (消音伴奏)》中的 `G.E.M.邓紫棋`。
- 初步结论：该约束技术上可实现，适合定义“高完备、强外键”的正式歌曲表，但会显著牺牲当前主页歌曲 raw 的覆盖率；若目标是尽量保留有效合作歌曲，需要先讨论是否补全歌手表或为拒绝歌曲保留导入拒绝记录。

### 取消歌手表 pmid 入库
- 用户要求修改歌手入库流程，把 `pmid` 取消入库。
- 已修改 `music_metadata_graph/pipelines/import_singer_list_to_db.py`，新建 `singers` 表时不再包含 `pmid`，导入 payload 和 upsert 语句也不再读取或写入 `pmid`。
- 已为已有 SQLite 数据库增加迁移逻辑：如果 `singers` 表仍存在 `pmid` 列，优先执行 `ALTER TABLE singers DROP COLUMN pmid`；若 SQLite 版本不支持直接删列，则通过临时表重建保留其他字段。
- 已重跑 `python -m music_metadata_graph.pipelines.import_singer_list_to_db`，结果为 raw rows 6803、imported rows 6803、db rows 6803。
- 当前 `singers` 表字段为 `mid`、`id`、`name`、`other_name`、`singer_pic`、`spell`、`raw_json_path`、`raw_page`、`raw_row_index`。
- 已更新 `README.md` 的 `singers` 字段说明，删除 `pmid`；已更新 `AGENTS.md` 项目补充规则，记录歌手入库字段不再包含 `pmid`。
- 验证对象为导入脚本语法、重跑导入结果、SQLite `singers` schema、`singers` 和 `albums` 行数、关键字段缺失情况。
- 验证结果显示 `import_singer_list_to_db.py` 通过 `py_compile`；当前 `singers` 表无 `pmid` 列，行数仍为 6803；`albums` 行数仍为 654；`mid`、`id`、`name`、`singer_pic`、`raw_json_path` 均无空值。

### 在歌曲和专辑请求之间补全缺失歌手
- 用户要求歌手库的 `mid`、`id`、`name` 都必须做非空限制，并要求在请求歌曲和请求专辑之间插入一步：验证歌曲中每个非空 `singer.mid` 是否在歌手库里，如果不在则用 `get_info` 请求歌手信息并入库。
- 用户要求补入歌手时如果 `id` 或 `name` 为空则不入库；如果 `singer_pic` 为空，尝试用 `base_info.background_image` 作为 `singer_pic`，如果仍为空则留空。
- 已修改 `music_metadata_graph/pipelines/import_singer_list_to_db.py`，显式校验 `mid`、`id`、`name` 非空，并在 schema 迁移时重建 `singers` 表使 `mid TEXT NOT NULL PRIMARY KEY` 生效。
- 已新增 `music_metadata_graph/pipelines/collect_missing_song_singers_to_db.py`，扫描 `data/raw/qqmusic/singer_homepage_song_tab/` 中的 `SongTab.List[].singer[]`，对不在 `singers` 表中的非空 `mid` 请求 `client.singer.get_info(mid)`。
- 新脚本保存原始响应到 `data/raw/qqmusic/singer_info/<singer_mid>.json`，并只向 `singers` 表写入现有字段：`mid`、`id`、`name`、`other_name`、`singer_pic`、`spell`、`raw_json_path`、`raw_page`、`raw_row_index`。
- 已在 `pyproject.toml` 新增命令入口 `mr-collect-missing-song-singers-db`。
- 初次解析按旧预期读取顶层 `singer/base_info` 时失败；检查 raw 后确认 `get_info` 当前响应结构为 `Info.Singer` 和 `Info.BaseInfo`，字段为 `SingerID`、`SingerMid`、`Name`、`SingerPic`、`BackgroundImage` 等；已修正解析逻辑。
- 已先用周杰伦样本和 `--max-singers 5` 验证缓存读取与入库，成功补入 5 个歌手，`singers` 从 6803 行变为 6808 行。
- 已对四位开发阶段歌手周杰伦、薛之谦、林俊杰、汪苏泷执行完整补全，扫描歌曲行 3492，发现歌曲歌手条目缺 `mid` 22 个，发现不在库的非空歌手 MID 326 个，请求并入库 326 个，跳过 0 个，`singers` 表变为 7134 行。
- 补全后重新模拟歌曲严格入库约束，唯一歌曲 3479 首中可通过约束的歌曲从补全前 1539 首提升到 1809 首；`singer_mid_not_in_singers` 已清零，剩余拒绝原因为 `missing_album_mid` 1668 首和 `missing_singer_mid` 18 首。
- 已更新 `README.md`，将当前流程调整为完整歌手列表 raw、歌手列表入库、主页歌曲 Tab raw、补全歌曲歌手、按歌曲请求专辑详情 raw、专辑详情入库。
- 已更新 `AGENTS.md` 项目补充规则，记录补全歌曲歌手步骤、歌手表 `mid/id/name` 非空约束和头像兜底规则。
- 验证对象为新增脚本语法、歌手导入脚本语法、联网小样本请求、四位歌手完整补全请求、SQLite `singers` schema、补全后歌曲入库约束模拟。
- 验证结果显示两个脚本均通过 `py_compile`；`singers` 表字段中 `mid`、`id`、`name` 均为非空约束，当前 `singers` 行数为 7134，`albums` 行数为 654；当前 `singers.mid/id/name/singer_pic/raw_json_path` 均无空值。

### 验证按 mid 查询歌手信息接口
- 用户询问是否存在根据歌手 `mid` 查询歌手信息的接口。
- 已检查当前安装的 `qqmusic-api-python`，`Client().singer` 下存在 `get_info(mid)` 和 `get_desc(mids)` 两个相关入口。
- `get_info(mid)` 对应 `music.UnifiedHomepage.UnifiedHomepageSrv.GetHomepageHeader`，参数为 `SingerMid`，用途偏歌手主页头部信息。
- 使用周杰伦 `mid=0025NhlN2yWrP4` 实测 `get_info`，返回包含 `singer.id=4558`、`singer.mid`、`singer.name`、`singer.singer_pmid`、`base_info.avatar`、`base_info.background_image`、`base_info.is_singer` 等字段。
- `get_desc(mids)` 对应 `music.musichallSinger.SingerInfoInter.GetSingerDetail`，参数为 `singer_mids` 列表，用途偏批量歌手详情、百科和扩展信息。
- 使用周杰伦 `mid=0025NhlN2yWrP4` 实测 `get_desc`，返回 `singer_list[]`，其中包含 `basic_info.id`、`basic_info.mid`、`basic_info.name`、`basic_info.pmid`、`basic_info.wikiurl`、`ex_info`、`wiki`、`group_list`、`photos`、`group_info` 等字段；当前样例中多数字段为空。
- 验证时本地沙箱网络默认拒绝访问 QQ 音乐接口，按权限规则放行后完成真实接口请求；未新增或修改项目源码。

### 修复开发日志追加编码异常
- 追加“验证按 mid 查询歌手信息接口”日志时，曾通过 PowerShell here-string 传入中文内容，导致新增中文记录被写成问号。
- 已改用补丁方式修复该段日志内容，使标题和正文恢复为 UTF-8 可读中文。
- 该问题未影响项目源码、数据库或 raw JSON 数据；影响范围仅为 `develop_log.md` 尾部新增日志段落。

### 验证指定 mid 的歌手信息返回
- 用户要求使用 `mid=002Z462D2amcz9` 验证按 mid 查询歌手信息接口，并列出返回 JSON 的所有键和值，长值可省略。
- 已联网请求 `Client().singer.get_info("002Z462D2amcz9")`，返回歌手为杨瑞代，包含 `status`、`singer`、`base_info`、`tab_detail`、`prompt` 等结构。
- 已联网请求 `Client().singer.get_desc(["002Z462D2amcz9"])`，返回 `singer_list[]`，其中包含 `basic_info`、`ex_info`、`wiki`、`group_list`、`photos`、`group_info` 等结构。
- 当前样例中 `get_info.base_info.avatar`、`get_info.base_info.name`、`get_desc.ex_info` 多数字段为空；`get_info.base_info.background_image` 和 `get_desc.singer_list[0].basic_info.wikiurl` 有值。
- 本次仅做接口验证和日志记录，未新增或修改项目源码、数据库结构或 raw JSON 缓存文件。

### 确认 get_info 批量查询边界
- 用户询问 `get_info` 是否支持批量查询。
- 已根据当前 `qqmusic-api-python` 源码确认 `SingerApi.get_info` 签名为 `get_info(self, mid: str)`，请求参数为单个 `SingerMid`，接口本身不支持一次传入多个 `mid`。
- 已确认同模块的 `get_desc(mids: list[str])` 支持传入 `singer_mids` 列表，可作为批量补充歌手详情的候选接口。
- 若后续需要批量获取主页头部信息，应在项目脚本中对 `get_info(mid)` 做低频循环、缓存和失败重试，而不是把多个 `mid` 直接塞给 `get_info`。

### 验证指定歌手 mid 信息返回
- 用户要求使用 `mid=002Z462D2amcz9` 验证按 mid 查询歌手信息接口。
- 已联网调用 `Client().singer.get_info("002Z462D2amcz9")`，接口返回 `status=0`，识别歌手为杨瑞代，`singer.id=13886`、`singer.mid=002Z462D2amcz9`、`singer.name=杨瑞代`、`singer.singer_pmid=002Z462D2amcz9_2`。
- `get_info` 的 `base_info.background_image` 返回 `http://y.gtimg.cn/music/photo_new/T001R800x800M000002Z462D2amcz9_2.jpg`，但 `base_info.avatar` 和 `base_info.name` 为空；说明该接口对部分歌手未必提供完整头像字段。
- 已联网调用 `Client().singer.get_desc(["002Z462D2amcz9"])`，返回 `singer_list[0].basic_info`，其中包含 `id=13886`、`mid=002Z462D2amcz9`、`name=杨瑞代`、`pmid=002Z462D2amcz9_2`、`has_photo=2`、`wikiurl=https://wiki.y.qq.com/i/cb3pioe3deas2l871mag`。
- `get_desc` 的 `ex_info`、`wiki`、`photos`、`group_list` 和 `group_info` 在该样例中为空；后续若补歌手扩展资料，需要允许这些字段缺失。

### 检查第一版归档头像缺失可视化逻辑
- 用户询问归档的第一版中头像缺少时如何可视化默认头像。
- 已检查 `archive/legacy_pipeline_2026-05-12/code/music_metadata_graph/pipelines/export_web_dataset.py` 和 `archive/legacy_pipeline_2026-05-12/web/app.js`。
- 第一版数据导出阶段只把制作人员接口里的 `artist.icon` 原样写入图谱节点的 `icon` 字段；目标歌手节点在首次创建时没有额外补默认头像 URL。
- 第一版前端绘制阶段通过 `getNodeImage(node)` 读取 `node.icon`；当 `icon` 为空时返回 `null`，当图片加载失败或未完成时也不会绘制图片。
- 第一版所谓“默认头像”不是独立图片资源，而是 Canvas 先画一个固定绿色圆形节点，再在图片可用时把头像裁剪进圆形；头像缺失时只保留绿色圆形、白色描边和节点姓名标签。
- 本次仅做归档实现分析和日志记录，未修改当前正式源码、归档源码或数据文件。

### 启动第一版归档网页预览
- 用户询问归档代码是否还能运行，并要求查看归档网页。
- 已确认第一版归档网页位于 `archive/legacy_pipeline_2026-05-12/web/`，包含 `index.html`、`app.js`、`styles.css`、`vendor/force-graph.min.js` 和 `data/catalog.json`、三位目标歌手数据 JSON。
- 已使用项目指定 Conda 环境中的 Python 3.12 启动静态 HTTP 服务，只服务归档的 `web` 目录，未把归档代码迁回当前正式目录。
- 初次使用 PowerShell `Start-Process` 启动服务时，本机环境变量存在 `Path/PATH` 键冲突导致失败；改用 PowerShell 后台 Job 后启动成功。
- 验证方式为请求 `http://127.0.0.1:8765/data/catalog.json`，返回 HTTP 200，说明归档网页数据可通过本地 HTTP 服务读取。
- 本次没有修改归档源码、当前正式源码或归档数据；仅新增本条开发日志。

### 修正归档网页服务未保持运行
- 用户反馈 `http://127.0.0.1:8765/` 拒绝连接，并质疑服务是否保持运行。
- 已复查确认此前通过沙箱内 `Start-Job` 和 .NET `Process` 启动的 Python 静态服务只在同一工具调用内短暂可用，跨工具调用后即无法连接；此前向用户报告“应该保持运行”不准确。
- 已改用沙箱外权限启动独立 Python 静态服务进程，只服务 `archive/legacy_pipeline_2026-05-12/web/` 目录。
- 验证方式为跨工具调用重新请求 `http://127.0.0.1:8765/data/catalog.json`，返回 HTTP 200；同时检查到 `python.exe` 服务进程仍存在，进程 ID 为 `30568`。
- 当前归档网页入口为 `http://127.0.0.1:8765/`；本次未修改归档源码、当前正式源码或归档数据。

### 关闭第一版归档网页预览服务
- 用户确认已看完归档网页，并要求关闭进程。
- 已按记录的 PID `30568` 只停止本次归档网页预览对应的 `python.exe` 服务进程，未处理其他 Python 进程。
- 验证方式为再次请求 `http://127.0.0.1:8765/data/catalog.json`，结果为无法连接；同时按 PID 查询不到该进程，说明预览服务已关闭。
- 本次仅关闭本地预览服务并记录日志，未修改归档源码、当前正式源码或归档数据。

### 验证歌手库是否包含韩红
- 用户要求验证当前歌手库中是否存在“韩红”。
- 已确认当前正式数据库为 `data/music_metadata_graph.sqlite3`，当前正式流程脚本默认也指向该 SQLite 文件。
- 已查询 `singers` 表，当前总行数为 7134。
- 精确查询 `name = '韩红'` 命中 1 条记录：`mid=003WlPvN2EvRaj`、`id=4419`、`name=韩红`、`spell=hanhong`。
- 模糊查询 `name` 或 `other_name` 包含“韩红”同样只命中该 1 条记录。
- 命中记录来源为 `data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all/page_0002_size_80.json`，`raw_page=2`，`raw_row_index=64`。
- 本次仅做数据库查询和日志记录，未修改业务数据或源码。

### 验证韩红歌曲列表包含飞云之下
- 用户要求使用韩红 `mid=003WlPvN2EvRaj` 请求韩红歌曲，并验证是否存在“飞云之下”，若存在则给出完整 JSON。
- 已使用当前正式脚本 `music_metadata_graph.pipelines.collect_singer_song_tab_raw` 请求 QQ 音乐歌手主页歌曲 Tab，目标歌手为韩红。
- 沙箱内首次联网请求因本地网络权限限制失败，按权限规则放行同一正式采集命令后请求成功。
- 已保存韩红歌曲 Tab raw JSON 到 `data/raw/qqmusic/singer_homepage_song_tab/003WlPvN2EvRaj/`，共 21 页、630 条歌曲行，最后一页 `HasMore=false`。
- 已扫描 21 页 raw JSON，标题包含“飞云之下”的歌曲行共 11 条；其中标题精确等于“飞云之下”的歌曲行 1 条。
- 精确命中记录位于 `page_0007_size_30.json` 的 `SongTab.List[11]`，歌曲 `mid=000fVqPH1RjwS3`，QQ 音乐数字 `id=213773480`，歌手为韩红和林俊杰，专辑 `mid=000XAvOz4exGKL`。
- 已将全部标题包含“飞云之下”的匹配摘要保存到 `found_feiyunzhixia_matches.json`，并将精确命中的完整歌曲对象保存到 `exact_feiyunzhixia.json`。
- 已确认 `exact_feiyunzhixia.json` 文件非空且 UTF-8 可读，无 U+FFFD 替换字符。

### 导入完备歌曲并输出拒绝 CSV
- 用户要求第七步做歌曲入库，直接入完备表；约束为 `song.mid` 非空唯一作主键，`song.id` 非空唯一，`song.name/title` 非空，`language` 非空，`album_mid` 非空且在专辑表中，`singer` 列表非空，每个 `singer_mid` 非空且在歌手表中。
- 用户要求入库失败的歌曲保存为 CSV，并明确这是正式流程的一部分。
- 已新增 `music_metadata_graph/pipelines/import_singer_song_tab_to_db.py`，读取歌手主页歌曲 Tab raw JSON，按 `song.mid` 去重，满足约束的歌曲写入 `songs`，演唱者关系写入 `song_singers`。
- 已在 `pyproject.toml` 新增命令入口 `mr-import-singer-song-tab-db`。
- `songs` 表字段为 `mid`、`id`、`name`、`title`、`language`、`album_mid`、`raw_json_path`、`raw_page`、`raw_row_index`；其中 `mid` 为非空主键，`id` 为非空唯一字段，`album_mid` 外键到 `albums.mid`。
- `song_singers` 表字段为 `song_mid`、`singer_order`、`singer_mid`、`raw_json_path`、`raw_page`、`raw_row_index`；主键为 `(song_mid, singer_order)`，`song_mid` 外键到 `songs.mid`，`singer_mid` 外键到 `singers.mid`。
- 入库失败歌曲 CSV 输出到 `data/processed/validation/song_import_rejections/csv_views/song_import_rejections.csv`，记录歌曲身份、专辑字段、歌手摘要、问题歌手、拒绝原因和 raw 追溯字段。
- 首次运行脚本默认扫描全部 `data/raw/qqmusic/singer_homepage_song_tab/` 时，把此前为验证韩红而请求的韩红歌曲 raw 也纳入了入库范围，导致 raw 行数变为 4122、拒绝原因额外出现 `album_mid_not_in_albums` 和 `singer_mid_not_in_singers`；这说明正式脚本需要支持指定目标歌手范围，避免临时验证 raw 污染开发阶段四位样本。
- 已补充脚本参数 `--all`、`--mid`、`--id`、`--name`，可像前序脚本一样指定导入范围；没有指定范围时仍可扫描全部已有 raw，正式开发阶段使用四位歌手姓名指定范围。
- 已重新执行 `python -m music_metadata_graph.pipelines.import_singer_song_tab_to_db --name 周杰伦 --name 薛之谦 --name 林俊杰 --name 汪苏泷`，结果为 raw rows 3492、unique song rows 3479、imported songs 1809、imported song singers 2977、rejected songs 1670。
- 当前拒绝原因计数为 `missing_album_mid` 1668、`missing_singer_mid` 18；同一首歌可同时命中多个原因，因此原因计数之和可大于拒绝歌曲行数。
- 已更新 `README.md`，新增第七步歌曲入库与拒绝 CSV，记录 `songs`、`song_singers` 字段、导入入口和当前四位歌手结果。
- 已更新 `AGENTS.md` 项目补充规则，记录歌曲完备入库约束和拒绝 CSV 产物路径。
- 验证对象为新脚本语法、四位歌手导入结果、SQLite schema、外键完整性、必填字段空值、拒绝 CSV 文件存在性和行数。
- 验证结果显示 `import_singer_song_tab_to_db.py` 通过 `py_compile`；当前数据库表为 `albums`、`singers`、`songs`、`song_singers`；`songs` 1809 行，`song_singers` 2977 行，`PRAGMA foreign_key_check` 无结果；`songs` 中 `mid/id/name/title/language/album_mid/raw_json_path` 均无空值；拒绝 CSV 存在且为 1670 行。

### 复查第二版归档歌曲双分支流程
- 用户询问归档的第二版里两个分支的流程分别是什么。
- 已复查 `archive/redesign_reset_2026-05-13/manifest.md`、`archive/redesign_reset_2026-05-13/code/music_metadata_graph/pipelines/collect_high_confidence_singer_songs.py` 和 `archive/redesign_reset_2026-05-13/code/scripts/write_supplement_filter_validation_views.py`。
- 确认第二版归档中的两个歌曲输入分支分别是高可信歌曲子集分支和补充分支，不属于当前重新设计后的数据库直入流程。
- 高可信歌曲子集分支从歌手专辑列表开始，请求允许类型专辑的歌曲，先保留歌曲歌手列表中包含目标歌手 mid 的记录，再按歌曲 mid/id 和规范化歌名去重；正式 JSON 输出在 `data/processed/high_confidence_singer_songs/`，CSV 仅作为验证视图。
- 补充分支从歌手主页歌曲 Tab raw JSON 开始，先过滤空专辑，再过滤缺失专辑 id/mid，再请求专辑详情补充专辑类型，然后保留 Single、EP、录音室专辑，再去重，最后按规范化歌名排除已在高可信子集中的歌曲；四歌手验证 JSON/CSV 输出在 `data/processed/validation/four_singers/` 下。
- 本次仅做归档流程复查和日志记录，未修改当前正式源码、数据库或数据产物。

### 添加入库后歌曲过滤步骤
- 用户要求在当前流程中添加第八步和第九步：第八步只保留专辑类型为 `Single`、`EP`、`录音室专辑` 的歌曲，第九步按规范化歌名去重，优先级为 `录音室专辑 > EP > Single > 较小 song id`；每一步过滤掉的歌曲都要正式导出 CSV，并临时导出第九步后保留歌曲 CSV。
- 已确认当前 `songs.mid` 为主键、`songs.id` 为唯一字段，所以第九步中的 mid/id 去重已由第七步入库约束和数据库唯一约束保证；新过滤步骤只报告 mid/id 唯一性检查，不再单独执行 mid/id 过滤。
- 已新增 `music_metadata_graph/pipelines/filter_imported_songs.py` 和命令入口 `mr-filter-imported-songs`，脚本作用于已入库的 `songs` 与 `song_singers`；过滤删除 `songs` 记录时通过外键级联删除对应 `song_singers`。
- 第八步过滤 CSV 正式输出到 `data/processed/validation/song_filtering/csv_views/songs_removed_by_step8_album_type.csv`；第九步过滤 CSV 正式输出到 `data/processed/validation/song_filtering/csv_views/songs_removed_by_step9_name_dedupe.csv`。
- 第九步后保留歌曲临时 CSV 输出到 `data/processed/validation/temp_song_filtering/csv_views/songs_after_step9_name_dedupe.csv`，用于本轮人工查看，不作为正式流程长期产物。
- 已更新 `README.md` 和 `AGENTS.md`，记录第八步、第九步职责、输出路径和 mid/id 唯一性由数据库保证的结论。
- 验证方式：先重新运行四位歌手第七步入库，再运行第八和第九步过滤脚本，检查 CSV 文件存在、非零、行数匹配，检查数据库外键、专辑类型分布和规范化歌名重复。
- 验证结果：第七步恢复入库歌曲 1809 首、歌曲歌手关系 2977 条；第八步按专辑类型过滤 685 首，剩余 1124 首；第九步按规范化歌名过滤 179 首，最终剩余 945 首、歌曲歌手关系 1369 条；`PRAGMA foreign_key_check` 无结果；剩余专辑类型只包含 `录音室专辑`、`Single`、`EP`；规范化歌名重复组为 0。

### 修正第九步为同名且同歌手去重
- 用户指出第九步按单纯同名去重有问题，应改为同名且同歌手才去重。
- 已修改 `music_metadata_graph/pipelines/filter_imported_songs.py`，第九步分组键从单一规范化歌名改为 `(规范化歌名, singer_mid 顺序序列)`；同歌手按 `song_singers.singer_order` 排序后的 `singer_mid` 序列判断。
- 已同步更新 `README.md` 和 `AGENTS.md`，记录第九步按“规范化歌名 + 同歌手”去重。
- 同时修正过滤脚本的执行顺序：先计算过滤结果并成功写出正式 CSV 和临时 CSV，再执行数据库删除，避免 CSV 被占用时数据库进入半过滤状态。
- 原第九步正式 CSV 路径 `songs_removed_by_step9_name_dedupe.csv` 在本机被其他程序占用，且语义对应旧的单纯同名去重规则；新正式路径改为 `data/processed/validation/song_filtering/csv_views/songs_removed_by_step9_same_singer_name_dedupe.csv`，临时保留歌曲 CSV 改为 `data/processed/validation/temp_song_filtering/csv_views/songs_after_step9_same_singer_name_dedupe.csv`。
- 已重新运行四位歌手第七步入库恢复数据库，再运行第八和第九步过滤。新规则结果：第八步仍过滤 685 首，剩余 1124 首；第九步按同名且同歌手过滤 141 首，最终剩余 983 首、歌曲歌手关系 1442 条。
- 验证结果：`filter_imported_songs.py` 通过 `py_compile`；新第八步 CSV 685 行，新第九步 CSV 141 行，新临时保留歌曲 CSV 983 行；`PRAGMA foreign_key_check` 无结果；剩余专辑类型只包含 `录音室专辑`、`Single`、`EP`；同名且同歌手重复组为 0；单纯同名但不同歌手重复组仍有 32 组，符合用户修正后的规则。

### 清理歌曲过滤旧产物
- 用户确认旧的第九步 CSV 已关闭，要求删除旧产物和临时产物，并重新整理产物路径，只保留第九步之后的结果这一个临时 CSV。
- 已删除旧规则正式 CSV `data/processed/validation/song_filtering/csv_views/songs_removed_by_step9_name_dedupe.csv`。
- 已删除旧临时 CSV `data/processed/validation/temp_song_filtering/csv_views/songs_after_step9_name_dedupe.csv`。
- 已删除新规则验证时产生的临时 CSV：`tmp_step8_album_type.csv`、`tmp_step9_same_singer_name_dedupe.csv`、`tmp_songs_after_step9_same_singer.csv`。
- 已删除新规则验证时产生的临时 SQLite 副本 `data/music_metadata_graph.temp_step9_same_singer.sqlite3`。
- 当前保留的正式过滤产物只有两个：第八步过滤 CSV `data/processed/validation/song_filtering/csv_views/songs_removed_by_step8_album_type.csv` 和第九步过滤 CSV `data/processed/validation/song_filtering/csv_views/songs_removed_by_step9_same_singer_name_dedupe.csv`。
- 当前唯一保留的临时查看产物为第九步之后保留歌曲 CSV：`data/processed/validation/temp_song_filtering/csv_views/songs_after_step9_same_singer_name_dedupe.csv`。
- 验证结果：第八步正式 CSV 685 行，第九步正式 CSV 141 行，第九步后临时保留 CSV 983 行；`data/processed/validation/song_filtering/` 下仅剩两个正式 CSV，`data/processed/validation/temp_song_filtering/` 下仅剩一个临时 CSV。

### 重新导出第九步后完整串表临时 CSV
- 用户要求重新导出一次第九步之后的临时 CSV，并包含完整串起来的表。
- 已覆盖导出 `data/processed/validation/temp_song_filtering/csv_views/songs_after_step9_same_singer_name_dedupe.csv`。
- 新 CSV 按一首歌的一个歌手关系一行展开，串联 `songs`、`albums`、`song_singers`、`singers` 四张表，避免多歌手歌曲被压缩成单个字符串后看不清关系表字段。
- 导出字段使用前缀区分来源表：`song_*`、`album_*`、`song_singer_*`、`singer_*`。
- 验证结果：文件存在且非零，大小 882195 字节；共 1442 行、32 列；当前 `songs` 为 983 首，`song_singers` 为 1442 条，因此临时 CSV 行数与歌曲-歌手关系数一致。

## 2026-05-14

### 复查第一版作词作曲来源
- 用户询问归档第一版或直接 API 中作词、作曲信息是如何查到的。
- 已复查 `archive/legacy_pipeline_2026-05-12/code/music_metadata_graph/pipelines/collect_singer_songs.py`、`archive/legacy_pipeline_2026-05-12/code/music_metadata_graph/pipelines/export_web_dataset.py` 和第一版 raw 缓存目录 `archive/legacy_pipeline_2026-05-12/data/raw/qqmusic/song_producers/`。
- 确认第一版不是从歌词文本中解析作词作曲，而是在歌曲初过滤和去重后，对每首保留歌曲调用 `Client().song.get_producer(song_mid_or_id)` 获取 QQ 音乐制作人员信息。
- 已检查当前本机安装的 `qqmusic-api-python` 实现，`SongApi.get_producer(value)` 接收歌曲数字 `id` 或歌曲 `mid`；数字值会作为 `songid` 请求，非数字字符串会作为 `songmid` 请求；底层模块为 `music.sociality.KolWorksTag`，方法为 `SongProducer`。
- 第一版 raw 返回存在两种键名形态：成功样例可见顶层 `data`，旧模型或空结果也可能出现 `Lst`；代码通过兼容读取 `data/Lst`、`title/Title`、`producers/Producers` 处理。
- 成功样例中制作人员列表按分组返回，例如 `title=演唱`、`title=作词`、`title=作曲`；每个制作人员对象包含 `name`、`singer_mid`、`icon`、`scheme`、`type` 等字段。
- 第一版把 `title=作词` 分组中的 `producer.name` 展开为 `credits.lyricists`，把 `title=作曲` 分组中的 `producer.name` 展开为 `credits.composers`，同时保留完整分组到 `credits.groups`。
- 网页导出阶段只从 `songs_kept.json` 读取 `credits.groups`，再提取“作词”和“作曲”两类贡献者生成歌曲明细和图谱边。
- 本次仅做归档源码、raw 缓存和本机 API 实现复查，未修改当前正式源码、数据库或归档源码。

### 复查 get_producer 返回结构
- 用户询问 `get_producer` 返回的完整结构。
- 已读取本机指定 Conda 环境中 `qqmusic-api-python` 的 `qqmusic_api.models.song.GetProducerResponse`、`SongProducerGroup` 和 `SongProducer` 模型定义。
- 当前模型结构为顶层 `Lst` 和 `ReinforceMsg`；`Lst[]` 中每个分组包含 `Title`、`Producers`、`Type`；`Producers[]` 中每个制作人员包含 `Type`、`Name`、`Icon`、`Scheme`、`SingerMid`、`Follow`。
- 已扫描第一版 raw 缓存目录 `archive/legacy_pipeline_2026-05-12/data/raw/qqmusic/song_producers/`，样例中同时存在大写键形态 `Lst/ReinforceMsg/Title/Producers/Name/SingerMid` 和小写键形态 `data/reinforce_msg/title/producers/name/singer_mid`。
- 第一版 raw 缓存共扫描到 602 个非空制作人员返回和 31 个空返回；分组标题包括 `演唱`、`作曲`、`作词`、`编曲`、`制作人`、`混音`、`录音`、`母带`、`吉他`、`鼓`、`贝斯`、`键盘`、`大提琴`、`小提琴`。
- 成功样例显示顶层摘要字段 `reinforce_msg` 可返回类似“词：方文山 / 曲：周杰伦”的文案，但正式结构化抽取仍应以分组中的 `Title=作词/作曲` 和 `Producers[]` 为准。
- 用户进一步纠正需要的是完整字段结构，而不是解释型摘要；后续回答应按 schema 形式列出顶层、分组和制作人员字段。
- 用户要求随便使用一首歌给出真实完整返回值。
- 已从第一版归档 raw 缓存读取歌曲 `0001bLnu2ULqYf` 的 `get_producer` 返回；该歌曲在当前歌曲视图中对应周杰伦《太阳之子》，QQ 音乐数字 `id=649556361`。
- 该 raw 返回包含 `data[]` 三个分组：`演唱`、`作词`、`作曲`，以及顶层 `reinforce_msg`；本次未重新联网请求接口。

### 限定周杰伦范围请求制作人信息
- 用户指出步骤八后 1124 首歌曲按 0.5 秒一次请求约需 37 分钟，要求先只请求歌曲歌手包含周杰伦的歌。
- 已使用 `collect_song_producer_raw --artist-mid 0025NhlN2yWrP4` 将第九步制作人 raw 请求范围限定为 `song_singers` 中包含周杰伦 MID 的歌曲。
- 本次第八步后命中周杰伦相关歌曲 261 首；运行结果为 0 个新请求、261 个缓存命中，未继续执行 1124 首全量联网请求。
- 作词、作曲制作人缺 MID 检查结果为 0 行，检查 CSV 为 `data/processed/validation/song_producer/csv_views/song_producer_missing_mid.csv`。
- 已同步调整 `import_song_credits_to_db.py`，让作词作曲关系入库也支持 `--artist-mid` 和 `--artist-name`，避免把此前中断全量请求留下的零散 raw 缓存混入当前周杰伦范围的关系表。
- 周杰伦范围制作人关系入库在第十一步去重前为目标歌曲 261 首、作词作曲关系 497 条；第十一步去重后重新限定周杰伦范围导入为目标歌曲 238 首、作词作曲关系 455 条。

### 同步 artists 与作词作曲关系表流程
- 已将当前音乐人表从旧 `singers` 迁移为 `artists`，字段为 `mid`、`name`、`other_name`、`icon`、`spell`、`raw_json_path`、`raw_page`、`raw_row_index`；不再保存 QQ 音乐数字 `id`，旧 `singer_pic` 语义改为 `icon`。
- 已将歌曲、专辑、补全歌手、制作人请求相关脚本的正式查询对象改为 `artists`，并废弃部分请求中的 `--id` 参数；当前部分请求使用 `--mid` 或 `--name`。
- 已新增 `song_credit_artists` 关系表，主键为 `(song_mid, role, artist_order)`，外键为 `song_mid -> songs.mid` 和 `artist_mid -> artists.mid`；当前只导入 `作词` 和 `作曲`。
- 已将第八步后的同名同歌手去重脚本命名与输出调整为第十步路径：`songs_removed_by_step10_same_singer_name_dedupe.csv` 和 `songs_after_step10_same_singer_name_dedupe.csv`；mid/id 去重仍由 `songs.mid` 主键和 `songs.id` 唯一约束保证。
- 已同步 `README.md` 和 `AGENTS.md`，记录当前流程、`artists` 表、制作人 raw 请求步骤、作词作曲关系表、周杰伦范围开发运行方式和新的 CSV 路径。
- 验证结果：`collect_song_producer_raw.py`、`import_song_credits_to_db.py`、`filter_imported_songs.py` 均通过 `py_compile`；第十一步同名同歌手去重从 1124 首过滤到 983 首，过滤 CSV 141 行，临时保留 CSV 983 行，两个 CSV 当时均为统一 10 列。
- 当前数据库表为 `albums`、`artists`、`songs`、`song_singers`、`song_credit_artists`；行数分别为 654、7266、983、1442、455；`PRAGMA foreign_key_check` 无结果。

### 第十步后 CSV 追加作词作曲列
- 用户要求第十步之后的 CSV 增加 `作词` 和 `作曲` 两列。
- 已修改 `filter_imported_songs.py`，使第十步及之后导出的歌曲 CSV 在原有 10 列后追加 `作词`、`作曲`；两列从 `song_credit_artists` 关联 `artists` 后按 `artist_order` 拼接，多个名字用 ` / ` 分隔。
- 为避免重跑去重脚本导致现有 141 行过滤 CSV 被覆盖，已对现有两个第十步后 CSV 原地补列。
- `songs_after_step10_same_singer_name_dedupe.csv` 仍为 983 行，新增列后 204 行有作词、227 行有作曲。
- `songs_removed_by_step10_same_singer_name_dedupe.csv` 仍为 141 行；由于去重删除时相关数据库关系已级联删除，已从现有 raw 制作人 JSON 尽量回填，67 行存在 raw，35 行有作词、46 行有作曲；其余为空是因为当前只请求了周杰伦相关歌曲的制作人 raw。
- 已同步 `README.md` 和 `AGENTS.md`：第十步之前歌曲 CSV 保持 10 列，第十步及之后歌曲 CSV 使用 12 列。

### 评估当前流程全量请求量
- 用户询问是否存在不请求数据、只查看数据量的接口，用于预估当前流程从 0 跑全量所需请求次数。
- 复核当前采集脚本后确认：`qqmusic.singer.get_singer_list_index` 返回顶层 `total`，当前缓存首批返回 `total=6803`，可用约 1 次请求预估完整歌手列表页数；但歌手主页歌曲 Tab `qqmusic.singer.get_tab_detail(..., TabType.SONG)` 的本地 raw 样本未发现 `total/count` 类字段，当前只能按 `HasMore` 分页到末页；`qqmusic.singer.get_info`、`qqmusic.album.get_detail`、`qqmusic.song.get_producer` 都是一对象一请求，没有发现只返回数量的现成接口。
- 本地样本统计：完整歌手列表缓存 86 页、6803 条；四位样本歌手加 1 个额外验证目录的主页歌曲 Tab 共 5 个歌手目录、139 页、4122 行，单歌手页数最小 18、中位 32、平均 27.8、最大 34，歌曲行最小 528、中位 939、平均 824.4、最大 1013；当前 SQLite 行数为 artists 7266、albums 654、songs 983、song_singers 1442、song_credit_artists 455。
- 按当前脚本默认限速 `REQUEST_RATE=0.5`、`REQUEST_CAPACITY=1` 粗略理解为约 2 秒 1 次请求；如果把 6803 位歌手都按样本均值 27.8 页请求主页歌曲 Tab，仅歌曲 Tab 约 18.9 万次请求，联网时间约 105 小时，不含补全歌手、专辑详情和制作人请求；因此直接全量从 0 跑存在明显时间和风控风险。
- 粗略公式记录为：总请求约等于 `ceil(歌手总数 / 歌手列表 page_size)` + `sum(每歌手歌曲页数)` + `歌曲歌手中缺失 artists 的唯一 singer_mid 数` + `歌曲 raw 中唯一 album_mid/album_id 数` + `第八步后需要请求制作人的唯一 song_mid 数`。其中后四项无法通过当前已验证接口在不拉取数据的情况下准确得出，只能通过小样本外推或先低频抽样估计。

### 分析批量请求与降请求量优化方向
- 用户继续询问当前流程是否存在可以优化减少请求的位置，尤其是多处只能一首一首遍历请求导致时间复杂度高，是否有批量办法。
- 复核本地 `qqmusic-api-python` 后确认，库中存在少数真实业务批量接口：`song.query_song(list[int|str])` 可以按歌曲 ID 或 MID 批量获取歌曲信息；`singer.get_desc(list[str])` 可以按多个歌手 MID 批量获取歌手详情描述；`song.get_fav_num(list[int])` 也支持批量歌曲收藏数，但当前流程不需要收藏数。
- 当前正式流程使用的 `song.get_producer(song_mid)`、`album.get_detail(album_mid|id)`、`singer.get_info(singer_mid)`、`singer.get_tab_detail(singer_mid, TabType.SONG)` 在库公开签名层面仍是单对象或单歌手分页接口；其中制作人和专辑详情未发现可直接传入列表的业务批量接口。
- 复核库底层 `Client.gather()` 后确认，它会把多个 request 描述符按协议、平台、公共参数和凭据分组，再按 `batch_size` 合并成一次 QQ 音乐 CGI HTTP 请求；默认 `batch_size=20`。这不能减少 QQ 音乐服务端需要处理的逻辑模块数，但可以显著减少本地等待、连接开销和脚本串行时间，适合用于专辑详情、制作人、补全歌手等当前逐个 `execute()` 的环节。
- 结构性降请求方向：歌曲 Tab 阶段目前是最大请求源，不能简单批量多个歌手分页；真正降量需要缩小目标歌手集合、只跑抽样或分层目标、优先使用已有歌手列表和歌曲 raw 里的内嵌字段，避免为后续不会进入图谱的歌曲提前请求制作人；制作人请求应继续放在专辑类型过滤和同名同歌手去重之后，避免对明显会被过滤的歌曲请求逐首详情。
- 后续若实现优化，建议先做三类小改动：第一，把专辑详情、制作人、缺失歌手补全改为低 batch size 的 `Client.gather()` 合包请求并保持单文件 raw 落盘；第二，评估用 `singer.get_desc(list[mid])` 替代部分 `singer.get_info(mid)` 的可行性，但要先验证其返回字段是否满足 `artists.mid/name/icon/other_name/spell/raw_json_path` 入库要求；第三，增加 dry-run/estimate 命令，从现有 raw 和数据库计算剩余请求数，避免盲目全量启动。

### 核对第一步歌手列表请求参数
- 用户询问当前第一步使用哪个请求接口、传入什么参数以及可传哪些参数。
- 当前脚本 `collect_singer_list_raw.py` 使用 `client.singer.get_singer_list_index()`，底层 QQ 音乐模块为 `music.musichallSinger.SingerList`，方法为 `GetSingerListIndex`。
- 当前固定传参为 `area=AreaType.ALL`、`sex=SexType.ALL`、`genre=GenreType.ALL`、`index=IndexType.ALL`、`page=page`、`num=config.page_size`；脚本默认 `page_size=80`，实际请求参数中写入 `area=-100`、`sex=-100`、`genre=-100`、`index=-100`、`sin=(page-1)*num`、`cur_page=page`。
- 本地库支持的筛选参数包括地区 `AreaType`、性别 `SexType`、风格 `GenreType`、首字母 `IndexType`、页码 `page` 和每页数量 `num`；当前项目脚本只把 `page_size`、`max_pages`、`raw_dir`、`force` 暴露为命令行参数，未暴露地区、性别、风格和首字母筛选。

### 核对歌手列表字段取值说明
- 用户询问第一步歌手列表 JSON 中 `id`、`mid`、`name`、`title`、`type`、`uin`、`pmid`、`area_id`、`country_id`、`country`、`other_name`、`spell`、`trend`、`concern_num`、`singer_pic` 等字段是否有 API 规定说明，例如 `area_id` 的枚举值。
- 复核本地 86 页完整歌手列表 raw 后确认，接口顶层 `tags` 明确返回请求筛选枚举：`area` 为 `-100 全部`、`2 港台`、`3 韩国`、`4 日本`、`5 欧美`、`200 内地`；`sex` 为 `-100 全部`、`0 男`、`1 女`、`2 组合`；`genre` 为 `-100 全部`、`2 电子`、`3 说唱`、`4 摇滚`、`7 流行`、`8 民谣`、`10 蓝调`、`11 R&B`、`13 乡村`、`14 爵士`、`19 国风`、`33 古典`、`37 民族乐`、`93 轻音乐`；`index` 为 `-100 全部`、`1-26 A-Z`、`27 #`。
- 复核 `qqmusic-api-python` 模型后确认，库只对歌手行字段给出字段含义级说明，例如 `area_id` 是地区 ID、`country_id` 是国家或地区 ID、`concern_num` 是关注数、`singer_pic` 是歌手图片地址；库没有给出 `area_id`、`type`、`trend`、`country_id` 等歌手行字段的枚举映射。
- 当前完整歌手列表样本中，`type` 恒为 `-1`，`country_id` 恒为 `0`，`country` 恒为空字符串，`trend` 恒为 `0`，`title`、`pmid`、`concern_num` 在有效值口径下均为空或 0；`area_id` 出现 `0`、`1`、`2`、`3`、`4`、`5`、`6`，次数分别为 336、1783、2374、2291、9、3、7。
- 样本推断上，`area_id=1` 多为内地歌手，`area_id=2` 多为韩国歌手，`area_id=3` 多为欧美歌手；但 `area_id=0` 包含周杰伦、林俊杰、陈奕迅、孙燕姿、BEYOND 等港台和东南亚/华语歌手混合，`area_id=4/5/6` 样本很少且含义不稳定，因此不能把 `area_id` 直接当作顶层 `tags.area` 的枚举值使用。
- 当前结论：项目正式入库仍应只使用已确认稳定的 `mid`、`name`、`other_name`、`spell`、`singer_pic/icon` 和 raw 追溯字段；`id`、`type`、`uin`、`pmid`、`area_id`、`country_id`、`country`、`trend`、`concern_num` 可保留在 raw 或字段字典中观察，不应作为当前业务筛选或身份合并依据。

### 统计当前歌手缓存地区字段取值
- 用户要求查看当前缓存的所有歌手 JSON 中 `area_id`、`country_id`、`country` 三个键的全部取值。
- 本次按歌手缓存范围扫描 `data/raw/qqmusic/singer_list_index/` 和 `data/raw/qqmusic/singer_info/` 下的 JSON 文件，共读取 417 个 JSON，解析错误 0 个。
- 统计结果显示三个键只出现在 `singer_list_index` 缓存中，`singer_info` 缓存未出现这些键。
- `area_id` 的去重取值为 `0`、`1`、`2`、`3`、`4`、`5`、`6`，出现次数分别为 336、1783、2374、2291、9、3、7；`country_id` 只有 `0`，出现 6803 次；`country` 只有空字符串，出现 6803 次。

### 分析歌手条目 area_id 地区含义
- 用户追问是否能分析出当前缓存歌手条目中 `area_id` 代表的具体地区。
- 复核 `qqmusic_api.modules.singer.AreaType` 和当前歌手列表响应顶层 `tags.area` 后确认，请求筛选地区标签为 `200=内地`、`2=港台`、`5=欧美`、`4=日本`、`3=韩国`；这些是请求筛选参数，不等同于歌手条目返回的 `area_id` 小整数。
- 结合当前 6803 条歌手列表样本反推，歌手条目 `area_id=0` 的代表样本为周杰伦、林俊杰、陈奕迅、五月天、蔡依林等，可高置信判断为港台/新马华语；`area_id=1` 的代表样本为薛之谦、汪苏泷、许嵩、李荣浩、周深等，可高置信判断为内地；`area_id=2` 的代表样本以 BIGBANG、EXO、BLACKPINK、BTS 等韩语艺人为主，也夹有米津玄師等少量日语艺人，可判断为日韩或更偏韩国的外语分组；`area_id=3` 的代表样本为 Justin Bieber、Taylor Swift、Lady Gaga、The Weeknd、Adele 等，可高置信判断为欧美。
- `area_id=4`、`5`、`6` 当前分别只有 9、3、7 条样本，且歌手名混杂；本地 `singer_info` 缓存没有这些小样本 MID 的详情可交叉验证，因此当前缓存不足以可靠命名这三个地区 ID。

### 暴露第一步歌手列表筛选参数
- 用户要求第一步采集脚本暴露 `AreaType`、`SexType`、`GenreType`、`IndexType` 四类传参，默认均为全量，传参接收列表形式，内部对列表参数组合依次请求。
- 已修改 `music_metadata_graph/pipelines/collect_singer_list_raw.py`，新增 `--area`、`--sex`、`--genre`、`--index` 参数；参数支持枚举名或枚举值，支持逗号分隔和重复传参，不传时分别默认 `ALL`。
- 脚本现在会对四类参数做笛卡尔组合并依次分页请求；raw 输出目录按组合命名，例如默认仍为 `area_all_sex_all_genre_all_index_all`，筛选组合为 `area_china_sex_male_genre_pop_index_a`。
- 已更新 `README.md` 的步骤一说明，补充列表参数示例和组合输出目录示例。
- 验证结果：`collect_singer_list_raw.py` 通过 `py_compile`；`--help` 显示新增参数；默认 `ALL/ALL/ALL/ALL` 加 `--max-pages 1` 命中既有缓存且未联网；`--max-pages 0 --area CHINA,TAIWAN --sex MALE --genre POP,RAP --index A,B,27` 正确展开 12 个组合且未发请求。

### 调整第一步默认地区筛选
- 用户要求把第一步脚本的默认 `area` 参数改成 `--area CHINA,TAIWAN`，其他默认参数保持不变。
- 已修改 `collect_singer_list_raw.py`，当未传 `--area` 时默认使用 `AreaType.CHINA` 和 `AreaType.TAIWAN` 两个地区；`--sex`、`--genre`、`--index` 仍默认 `ALL`。
- 已同步更新 `README.md`，说明不传参数时 `--area` 默认是 `CHINA,TAIWAN`，其余筛选默认 `ALL`。
- 验证结果：`collect_singer_list_raw.py` 通过 `py_compile`；`--help` 显示 `--area` 默认 `CHINA,TAIWAN`；`--max-pages 0` 默认展开为 `area_china_sex_all_genre_all_index_all` 和 `area_taiwan_sex_all_genre_all_index_all` 两个组合，未发请求。

### 分析第一步地区筛选后的缓存与入库边界
- 用户指出第一步歌手列表默认地区已从 ALL 改为 CHINA,TAIWAN，旧 area_all_sex_all_genre_all_index_all 缓存不再会被新默认请求命中，并询问如何删除冗余缓存、重新入库得到更少的 artists。
- 复核当前实现后确认，collect_singer_list_raw.py 新默认会请求 area_china_sex_all_genre_all_index_all 和 area_taiwan_sex_all_genre_all_index_all 两个组合目录；旧 area_all... 目录只在显式传 --area ALL 时命中。
- 复核当前本地 raw 目录后确认，目前 data/raw/qqmusic/singer_list_index/ 下仍只有旧 area_all_sex_all_genre_all_index_all 目录，共 86 个分页文件；因此不能立即删除旧缓存，否则在新两个地区缓存尚未采集完成前会失去第一步 raw 证据。
- 复核 import_singer_list_to_db.py 后确认，当前默认入库 raw 目录仍指向旧 area_all...，且入库逻辑为 upsert，不会删除数据库中旧的 artists 行；要得到更少 artists，需要先采集新地区 raw，再让第二步只读取新地区 raw，并以替换/重建方式刷新 artists 表或使用新的数据库文件。
- 风险边界：如果数据库中已有 songs、song_singers、song_credit_artists 等依赖旧 artists 的下游数据，直接缩小 artists 表可能造成外键或语义不一致；在重新设计阶段更稳妥的做法是从步骤二开始重建数据库，或同步清空后续表再按新流程重跑。

### 解释歌手列表 raw 缓存保留请求参数目录的原因
- 用户询问旧第一步为何不直接把 data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all/ 内数据移动到 singer_list_index/ 根目录，而要按请求参数区分目录。
- 本次判断：歌手列表 raw 缓存目录名承担请求参数缓存键和来源追溯职责；同一个 page_0001_size_80.json 在 area=ALL、area=CHINA、area=TAIWAN 等参数下代表不同响应，若直接平铺到根目录会发生文件名冲突、缓存误命中、入库范围不可辨认和后续验证不可追溯。
- 对当前需求而言，旧 area_all... 数据即使移动到根目录，本质仍是旧全地区请求结果，不能变成新默认 CHINA,TAIWAN 的更小数据集；要减少 artists，仍需要按新参数采集对应 raw，并让入库脚本只读取这些新参数目录后替换数据库中的歌手表。

### 恢复第一步默认全量地区参数
- 用户要求把第一步歌手列表请求默认参数改回全 ALL，并提供只请求内地和港台两个地区的显式指令。
- 已修改 music_metadata_graph/pipelines/collect_singer_list_raw.py，未传 --area 时恢复为 AreaType.ALL；--sex、--genre、--index 仍默认 ALL。
- 已同步更新 README.md 步骤一说明，改为不传四类筛选参数时默认均为 ALL。
- 验证结果：collect_singer_list_raw.py 通过 py_compile；--max-pages 0 默认展开为 area_all_sex_all_genre_all_index_all 一个组合；--max-pages 0 --area CHINA,TAIWAN 展开为 area_china_sex_all_genre_all_index_all 和 area_taiwan_sex_all_genre_all_index_all 两个组合且不发请求。

### 复核第二步歌手列表入库字段
- 用户询问第二步入库的键和未入库的键。
- 复核 `music_metadata_graph/pipelines/import_singer_list_to_db.py` 后确认，当前第二步写入 `artists` 的字段为 `mid`、`name`、`other_name`、`icon`、`spell`、`raw_json_path`、`raw_page`、`raw_row_index`；其中 `icon` 从 raw 行的 `icon` 或 `singer_pic` 取值，当前完整歌手列表 raw 实际使用 `singer_pic`。
- 只读扫描 `data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all/` 下 86 个分页 JSON，确认当前 6803 条 `singerlist[]` 行实际 raw 键为 `area_id`、`concern_num`、`country`、`country_id`、`id`、`mid`、`name`、`other_name`、`pmid`、`singer_pic`、`spell`、`title`、`trend`、`type`、`uin`。
- 因此当前 raw 行中未以原名入库的键为 `area_id`、`concern_num`、`country`、`country_id`、`id`、`pmid`、`singer_pic`、`title`、`trend`、`type`、`uin`；其中 `singer_pic` 并非丢弃，而是映射到 `artists.icon`。
- 本次只做字段复核和日志记录，未修改业务代码、数据库或 raw JSON。

### 调整第二步歌手入库地区字段和筛选
- 用户要求修改第二步代码，把 `area_id` 写入 `artists`，并在入库前只保留 `area_id` 为 `0` 和 `1` 的歌手行。
- 已修改 `music_metadata_graph/pipelines/import_singer_list_to_db.py`：新增 `ALLOWED_AREA_IDS = {0, 1}`、`parse_area_id()` 和 `filter_singers_by_area()`；`run()` 先加载 raw，再按 `area_id` 过滤，再执行 `mid`、`name` 和重复 `mid` 校验，最后只导入过滤后的行。
- 已将 `artists` schema、旧 `singers` 迁移、旧 `artists` schema 重建和 upsert 写入逻辑同步加入 `area_id INTEGER`；第二步完整歌手列表导入只写明确解析到的 `area_id`，后续通过歌曲歌手或制作人补入的音乐人如果没有地区字段，则保留 `area_id` 为空；`run()` 输出增加 `filtered_rows`、`filtered_out_rows` 和 `allowed_area_ids`，便于确认筛选规模。
- 已同步 `README.md` 和 `AGENTS.md`，记录 `artists.area_id` 字段和第二步只导入 `area_id` 为 `0` 或 `1` 的规则。
- 验证结果：`import_singer_list_to_db.py` 通过 `py_compile`；使用当前完整歌手列表 raw 和内存 SQLite 运行导入逻辑，6803 条 raw 行过滤后为 2119 条，实际导入 2119 条，`artists.area_id` 分布为 `0=336`、`1=1783`，schema 字段包含 `area_id`。
- 本次未改写现有 `data/music_metadata_graph.sqlite3`；如果直接对已有旧库重跑第二步，upsert 不会自动删除历史已入库的其他地区歌手，若需要数据库结果也只保留新规则范围，应从第二步开始重建数据库或另行设计受控清理。

### 将第 4、5、9 步请求改为合包
- 用户要求优化第 4、5、9 步，把原本串行的单对象请求改成 `qqmusic-api-python` 的 `Client.gather()` 合包请求，并由脚本顶部参数控制 batch size；后续类似单对象请求也应使用合包。
- 已修改 `collect_missing_song_singers_to_db.py`：新增 `REQUEST_BATCH_SIZE = 20`、`CollectConfig.batch_size` 和 `--batch-size`；缺失歌手信息请求先处理缓存命中，再把未命中的 `singer.get_info(mid)` request 描述符交给 `Client.gather()` 合包，返回后仍按一个歌手一个 raw JSON 文件写入 `data/raw/qqmusic/singer_info/`。
- 已修改 `collect_song_album_detail_raw.py`：新增 `REQUEST_BATCH_SIZE = 20`、`CollectConfig.batch_size` 和 `--batch-size`；专辑详情请求先处理缓存命中，再把未命中的 `album.get_detail(album_mid/id)` request 描述符交给 `Client.gather()` 合包，返回后仍按一个专辑一个 raw JSON 文件写入 `data/raw/qqmusic/song_album_detail/`。
- 已修改 `collect_song_producer_raw.py`：新增 `REQUEST_BATCH_SIZE = 20`、`ProducerConfig.batch_size` 和 `--batch-size`；制作人请求先处理缓存命中，再把未命中的 `song.get_producer(song_mid)` request 描述符交给 `Client.gather()` 合包，返回后仍按一首歌一个 raw JSON 文件写入 `data/raw/qqmusic/song_producer/`。
- 已同步 `README.md`，在步骤四、五、九说明默认每批 20 个 request，可通过 `--batch-size` 覆盖，合包只减少 HTTP 往返次数，不改变 raw JSON 落盘粒度。
- 已同步 `AGENTS.md` 项目规则：后续 QQ 音乐单对象请求如果可构造多个 request 描述符，优先使用 `Client.gather()` 按批合包；批大小使用脚本顶部常量并提供命令行参数覆盖；合包不得改变单对象 raw JSON 落盘和低频请求边界。
- 验证结果：三个脚本通过 `py_compile`；三个脚本 `--help` 均显示 `--batch-size`；使用伪 `gather()` 做不联网批量函数验证，三条批量路径均以 `batch_size=7` 调用 `gather()`，并分别生成两个歌手、两个专辑、两首歌的 raw JSON 文件；使用 `--max-singers 0`、`--max-albums 0`、`--max-songs 0` 做本地烟测，确认摘要中包含 `batch_size=3` 且未发起联网请求。

### 复核四位歌手重建数据库运行结果
- 用户运行一键重建命令后提供终端输出文件，要求查看运行结果。
- 运行结果显示旧数据库已备份为 `data/music_metadata_graph_20260514_154010.bak.sqlite3`，新数据库从第二步开始重建；完整歌手列表 raw 为 6803 行，按 `area_id` 为 `0` 或 `1` 过滤后导入 2119 行。
- 四位歌手主页歌曲 Tab 请求全部命中缓存；步骤四缺失歌曲歌手补全扫描 3492 条歌曲行，发现 352 个缺失歌手，其中 21 个新请求、331 个缓存命中，补入后 `artists` 为 2471 行。
- 专辑详情请求去重后 654 个专辑全部命中缓存，并导入 654 行专辑；歌曲入库读取 3492 条 raw 歌曲行；步骤八后保留 1124 首歌。
- 步骤九制作人请求作用于 1124 首歌，其中 519 个新请求、605 个缓存命中，作词/作曲缺 MID 检查输出 48 行；步骤十导入制作人后 `artists` 为 2744 行，`song_credit_artists` 为 2076 条。
- 最后按“规范化歌名 + 同歌手”去重删除 141 首歌，最终剩余 983 首歌、1442 条歌曲演唱关系；本次复核当前 SQLite 结果为 `artists=2744`、`albums=654`、`songs=983`、`song_singers=1442`、`song_credit_artists=1913`，`PRAGMA foreign_key_check` 无结果，歌曲 mid/id 重复组均为 0。
- 当前 `artists.area_id` 分布为 `NULL=668`、`0=319`、`1=1757`；其中 `NULL` 来自后续缺失歌曲歌手和制作人补入路径没有地区字段，符合当前可空设计。

### 分析断点续跑边界安全性
- 用户询问全量运行时手动终止是否可能断在坏位置，尤其是否会写入一半 raw 文件留下坏文件。
- 复核当前采集脚本后确认，`collect_singer_song_tab_raw.py`、`collect_missing_song_singers_to_db.py`、`collect_song_album_detail_raw.py`、`collect_song_producer_raw.py` 的 raw JSON 写入目前使用 `Path.write_text()` 直接覆盖目标文件，不是临时文件加原子替换；因此如果进程刚好在写文件过程中被终止，理论上可能留下截断或不完整 JSON。
- 当前缓存读取使用 `json.loads()`，如果后续断点续跑遇到坏 JSON，通常会报解析错误并停止，而不是静默当作有效缓存；但这仍不是理想的可恢复边界。
- 数据库写入侧多数关键替换操作使用 `with connection:` 事务包住，例如歌曲表删除重建、过滤删除和关系表替换；如果在事务中中断，SQLite 通常会回滚未提交事务，数据库比 raw 文件更安全。
- 当前更稳妥的后续修复方向：为 raw JSON 和正式 CSV 写入增加同目录临时文件、写完后校验、再 `os.replace()` 原子替换；读取缓存时遇到 JSON 解析失败应把该文件视为坏缓存，提示删除或在 `--force` 下重新请求。

### 将坏缓存 JSON 视为缓存未命中
- 用户提出断点续跑时可以在 load 缓存失败后把该文件当作未命中处理，从而重新请求覆盖坏文件。
- 已修改 `collect_singer_song_tab_raw.py`、`collect_missing_song_singers_to_db.py`、`collect_song_album_detail_raw.py`、`collect_song_producer_raw.py`，新增 `try_load_cached_json()`；只有缓存命中判断使用该函数，遇到 `OSError` 或 `json.JSONDecodeError` 时返回未命中并进入请求路径。
- 上游 raw 扫描仍使用严格 `load_json()`，不吞掉真正的数据结构或输入文件错误；因此本次修复只覆盖“目标缓存文件存在但损坏”的断点续跑场景。
- 验证结果：四个脚本通过 `py_compile`；使用临时目录构造半截 JSON 缓存，分别验证歌手主页歌曲 Tab、缺失歌手信息、专辑详情、制作人 raw 四条路径都会把坏缓存当作未命中，调用请求路径并覆盖为有效 JSON。

### 支持从已有歌曲 Tab raw 继续第 4、5 步
- 用户在第三步歌曲 Tab 全量采集中途停止后，要求后续先不继续请求全量歌曲，而是假设当前已有歌曲 Tab raw 已足够，直接从第四步开始处理现有数据。
- 已确认报错原因：`collect_missing_song_singers_to_db --all` 会按当前数据库 `artists` 全量歌手解析目标，并严格要求每个目标都有步骤三歌曲 Tab raw；当前本地只有部分歌手 raw，因此缺失列表触发 `FileNotFoundError`。
- 已修改 `collect_missing_song_singers_to_db.py` 和 `collect_song_album_detail_raw.py`，新增 `--existing-song-tabs` 参数；该参数只选择当前数据库 `artists` 中、且本地存在 `data/raw/qqmusic/singer_homepage_song_tab/<mid>/page_*_size_*.json` 的歌手，适用于第三步未全量完成但需要继续处理已有 raw 的场景。
- 已同步修改 `import_singer_song_tab_to_db.py`，为第 7 步歌曲入库增加同名 `--existing-song-tabs` 参数，避免第 4、5 步按当前数据库已有 raw 处理后，第 7 步又用旧 `--all` 扫入数据库外的历史 raw 目录。
- `--all` 语义保持不变：仍表示数据库歌手全量，缺任意目标的歌曲 Tab raw 就停止，避免把严格全量流程和部分续跑流程混在一起。
- 已同步 `README.md` 和 `AGENTS.md`，记录第 4、5、7 步部分续跑应使用 `--existing-song-tabs`。
- 验证结果：第 4、5 步脚本通过 `py_compile`；两个脚本 `--help` 均显示 `--existing-song-tabs`；使用 `--existing-song-tabs --max-singers 0 --batch-size 3` 本地烟测第 4 步，扫描到 542 个已有歌曲 Tab raw 的当前数据库歌手、226800 条歌曲行，未发起请求；使用 `--existing-song-tabs --max-albums 0 --batch-size 3` 本地烟测第 5 步，同样扫描到 542 个歌手、226800 条歌曲行，未因数据库其他歌手缺 raw 报错。

### 梳理当前流程参数和全量语义
- 用户询问当前每一步支持哪些参数，以及全量流程里的“全”如何定义。
- 已复核 `music_metadata_graph/pipelines/` 下当前有效脚本的 `argparse` 参数、目标解析逻辑和 README 流程说明。
- 当前不同步骤的“全量”不是同一个集合：第一步不传筛选参数时是 QQ 音乐歌手列表接口四类筛选维度均为 `ALL`；第三、四、五步的 `--all` 是当前 SQLite `artists` 表内全部歌手；第七步的 `--all` 是当前歌曲 Tab raw 目录下所有已有 raw；第九、十、十一步默认作用于当前 SQLite `songs` 表。
- 已确认 `--existing-song-tabs` 的语义是只选择当前数据库 `artists` 中已经存在歌曲 Tab raw 的歌手，用于第三步未全量完成时继续处理已有 raw；它不能与 `--all`、`--mid`、`--name` 混用。
- 本次仅做流程参数分析和说明，未修改业务代码或运行采集、入库、过滤命令。

### 调整已有歌曲 Tab raw 续跑参数命名
- 用户确认第七步旧 `--all` 和 `--existing-song-tabs` 的区别后，要求把三个带 `--existing-song-tabs` 参数的脚本删除旧 `--all` 参数，并把 `--existing-song-tabs` 改名为 `--all`。
- 已修改 `collect_missing_song_singers_to_db.py`、`collect_song_album_detail_raw.py`、`import_singer_song_tab_to_db.py`：三个脚本的 `--all` 现在统一表示“当前数据库 `artists` 中且本地已有歌曲 Tab raw 的歌手”；旧的 `--existing-song-tabs` 参数不再暴露。
- 已移除第 4、5 步旧的数据库 `artists` 严格全量分支；已移除第 7 步旧的全 raw 目录扫描分支，并让第 7 步无参数时停止提示必须传 `--all`、`--mid` 或 `--name`。
- 已同步 `README.md` 和 `AGENTS.md`，将第 4、5、7 步的已有歌曲 Tab raw 续跑命令改为 `--all`，并记录这三个脚本不再提供旧的严格全量或全 raw 目录扫描语义。
- 验证结果：三个脚本通过 `py_compile`；三个脚本 `--help` 均只显示 `--all`、`--mid`、`--name`，不再显示 `--existing-song-tabs`；分别使用旧 `--existing-song-tabs` 调用三个脚本均被 argparse 拒绝；第七步无参数运行会停止并提示 `Provide --all, or at least one --mid or --name.`。

### 调整第四步缺失歌手请求为渐进落盘
- 用户指出第四步当前先找出所有缺失歌手 MID，再一次性进入 `execute_or_load_batch` 大批量请求，只有全部请求完成后才解析入库；一旦大批量请求中途失败，就得不到任何缓存，而大批量中途失败概率很高。
- 已修改 `collect_missing_song_singers_to_db.py`：缺失歌手信息请求改为按 `--batch-size` 分批处理，每批成功响应立即写入对应 `data/raw/qqmusic/singer_info/<mid>.json`，不再等所有缺失歌手请求完成后统一落盘。
- 如果 `Client.gather()` 返回部分异常，脚本会保留并写入同批成功项，只把失败 MID 记录为失败；如果整批 `gather()` 抛异常，脚本会降级为单个请求逐个尝试，尽量挽救可成功的 raw 缓存。
- 脚本会先解析并导入已成功获取或命中缓存的歌手，再在仍有失败请求时以非零退出提示重新运行继续补齐；下次重跑会复用已写入的 raw 缓存。
- 已同步 `README.md` 和 `AGENTS.md`，记录第四步必须按批渐进落盘、批次失败降级单请求、失败后可重跑补齐的规则。
- 验证结果：`collect_missing_song_singers_to_db.py` 通过 `py_compile`；使用伪客户端验证 `gather()` 返回部分异常时成功项会写入 raw、失败项不写；验证整批 `gather()` 抛异常时会降级单请求，并保存单请求成功项。

### 调整第五步和第九步 raw 请求为渐进落盘
- 用户要求第 5 步专辑详情请求和第 9 步制作人请求也改成与第四步一致的安全流程，避免大批量请求中途失败导致已成功响应无法缓存。
- 已修改 `collect_song_album_detail_raw.py`：专辑详情请求按 `--batch-size` 分批处理，每批成功响应立即写入 `data/raw/qqmusic/song_album_detail/<album_key>.json`；批内部分失败只记录失败专辑 key；整批 `gather()` 抛异常时降级为单个专辑请求逐个尝试。
- 已修改 `collect_song_producer_raw.py`：制作人请求按 `--batch-size` 分批处理，每首歌成功响应立即写入 `data/raw/qqmusic/song_producer/<song_mid>.json`；批内部分失败只记录失败歌曲 MID；整批 `gather()` 抛异常时降级为单个歌曲请求逐个尝试。
- 两个脚本都会在汇总中输出 `failed_fetches` 和失败对象列表；第 5 步仍有失败专辑 key 时以非零退出提示重跑；第 9 步会先写出已成功歌曲的缺制作人 MID 检查 CSV，再在仍有失败歌曲 MID 时以非零退出提示重跑。
- 已同步 `README.md` 和 `AGENTS.md`，把单对象批量 raw 请求的规则扩展为第 4、5、9 步都必须按批渐进落盘、整批失败降级单请求、失败后可重跑补齐。
- 验证结果：`collect_song_album_detail_raw.py` 和 `collect_song_producer_raw.py` 通过 `py_compile`；分别使用伪客户端验证 `gather()` 返回部分异常时成功项会写入 raw、失败项不写；验证整批 `gather()` 抛异常时会降级单请求，并保存单请求成功项。

### 允许专辑发行日期为空
- 用户运行第六步 `import_song_album_detail_to_db` 时遇到 `ValueError: 77 album rows are missing publishDate.`，说明当前全量专辑详情 raw 中存在 `basicInfo.publishDate` 为空字符串的专辑。
- 已抽样复核缺失项，确认这些 raw 仍有 `albumMid`、`albumID`、`albumName`、`albumType` 等核心字段，发行日期为空不应阻断专辑实体入库；后续歌曲过滤主要依赖 `albumType`。
- 已修改 `import_song_album_detail_to_db.py`：专辑导入校验不再要求 `publishDate` 非空，`publishDate` 缺失或为空时保留为空字符串；建表语句保持 `publishDate TEXT NOT NULL DEFAULT ''`。
- 已同步 `README.md` 和 `AGENTS.md`，记录 `albums.publishDate` 可为空字符串且不阻断专辑入库。
- 验证结果：脚本通过 `py_compile`；重新运行第六步成功导入 `raw_rows=50624`、`imported_rows=50624`、`db_rows=50624`；数据库中 `publishDate=''` 的专辑为 77 行；`PRAGMA foreign_key_check` 返回 0 行。

### 改为拒绝缺发行日期专辑
- 用户纠正第六步规则：不应该允许发布日期为空的专辑导入，应该像第七步歌曲导入一样，把导入失败记录写到拒绝 CSV。
- 已修改 `import_song_album_detail_to_db.py`：`mid`、`id`、`name`、`albumType`、`publishDate` 都恢复为专辑入库必填字段；缺字段的专辑不写入 `albums`，而是写入 `data/processed/validation/album_import_rejections/csv_views/album_import_rejections.csv`。
- 专辑拒绝 CSV 列包含 `album_mid`、`album_id`、`album_name`、`album_type`、`album_publish_date`、`reason_flags`、`raw_json_path`、`raw_page`、`raw_row_index`，当前缺日期原因写作 `missing_publishDate`。
- 第六步导入改为用本轮合格专辑集合替换 `albums` 表，并清空下游 `songs`、`song_singers`、`song_credit_artists`，避免上一轮已导入的缺日期专辑或其派生歌曲关系残留；这些下游表会在第七步及之后重新生成。
- 已同步 `README.md` 和 `AGENTS.md`，记录专辑完备约束和拒绝 CSV 路径。
- 验证结果：脚本通过 `py_compile`；重新运行第六步得到 `raw_rows=50624`、`accepted_rows=50547`、`rejected_rows=77`、`db_rows=50547`；拒绝 CSV 存在且 77 行，首条原因为 `missing_publishDate`；数据库中 `publishDate=''` 的专辑为 0 行；`PRAGMA foreign_key_check` 返回 0 行；下游 `songs`、`song_singers`、`song_credit_artists` 均已清空等待后续步骤重建。

### 调整歌曲 CSV 排序和作词作曲列位置
- 用户要求每次导出歌曲 CSV 时按歌名拼音首字母混排，不再按 Unicode 字符顺序排序；第十步跑完后导出临时歌曲表并包含 `作词`、`作曲` 两列；包含 `作词`、`作曲` 时两列应放在演唱信息前面，而不是放在最后。
- 已新增 `music_metadata_graph/pipelines/song_csv.py`，集中定义歌曲 CSV 字段顺序、歌名拼音排序、演唱者 JSON、作词作曲名称查询和 CSV 写出逻辑。
- 已修改第 7 步歌曲入库拒绝 CSV、第 8 步专辑类型过滤 CSV、第 11 步同歌手同名去重 CSV，写出时统一按歌名拼音首字母和拼音排序。
- 已修改第 10 步 `import_song_credits_to_db.py`，默认在导入作词作曲关系后导出 `data/processed/validation/temp_song_filtering/csv_views/songs_after_step10_credit_import.csv`；新增 `--temp-songs-csv` 和 `--no-temp-songs-csv` 参数控制该临时 CSV。
- 已调整第 10 步及之后歌曲 CSV 字段顺序为 `song_mid`、`song_id`、`song_name`、`song_title`、`song_language`、`album_name`、`album_type`、`album_publish_date`、`作词`、`作曲`、`singer_count`、`singers_json`。
- 已同步 `README.md` 和 `AGENTS.md`，记录歌曲 CSV 拼音排序、第十步临时 CSV 路径和作词作曲列必须位于演唱信息前的规则。
- 验证结果：相关脚本通过 `py_compile`；第十步默认运行成功，导出 `songs_after_step10_credit_import.csv` 共 105705 行，表头顺序符合新规则；第十一步使用临时输出路径和 `--no-temp-kept-csv` 做烟测，去重删除数为 0，未改变歌曲数量；拼音排序样例输出为 `A Song`、`阿飞`、`白日梦`、`曾经`、`周杰伦`。

## 2026-05-15

### 分析 CSV Excel 公式风险
- 用户指出部分歌曲名以等号开头，使用 Excel 打开 CSV 时会被识别为公式。
- 已确认风险不只限于 `=`，Excel 对以 `=`、`+`、`-`、`@` 开头的文本也可能按公式解释；即使 CSV 字段被引号包住，Excel 仍可能执行公式解析。
- 本次处理边界确定为只在导出 CSV 的展示值上增加 Excel 文本转义，不改写 SQLite 数据库、raw JSON 和业务字段原值。

### 实现 CSV Excel 公式转义
- 已在 `music_metadata_graph/pipelines/song_csv.py` 新增 CSV 文本单元格转义函数：文本去掉开头空白后如果以 `=`、`+`、`-`、`@` 开头，则在 CSV 输出值前加单引号。
- 已让歌曲 CSV 统一写出函数在排序后、写入前应用该转义，覆盖第 7 步歌曲拒绝 CSV、第 8 步歌曲过滤 CSV、第 10 步临时歌曲 CSV 和第 11 步过滤/临时歌曲 CSV。
- 已让第 6 步专辑拒绝 CSV 和第 9 步制作人缺 MID 检查 CSV 复用同一转义函数，避免专辑名、制作人名、图标 URL 或其他文本被 Excel 误当公式。
- 已同步 `README.md` 和 `AGENTS.md`，记录导出 CSV 的 Excel 安全规则以及数据库和 raw JSON 不改写的边界。

### 验证 CSV Excel 公式转义
- 语法验证对象为 `song_csv.py`、`import_song_album_detail_to_db.py`、`collect_song_producer_raw.py`，执行项目指定 Conda 解释器的 `py_compile`，结果未报错。
- 写出验证使用临时目录分别调用歌曲 CSV、专辑拒绝 CSV 和制作人缺 MID CSV 写出函数，构造 `=SUM(1,1)`、`+title`、`-lang`、`@producer` 等文本值。
- 回读临时 CSV 后确认相关文本单元格均以单引号开头，例如 `'=SUM(1,1)`、`'+title`、`'-lang`、`'@producer`，可避免 Excel 按公式解析。
- 已复查当前有效 `music_metadata_graph/pipelines/` 中直接使用 `csv.DictWriter` 的入口，只剩上述三个写出点，均已接入统一转义。

### 重新生成第十步临时歌曲 CSV
- 用户要求重新生成第十步导出的临时歌曲 CSV，以应用新的 Excel 公式安全转义规则。
- 本次未重新写入 `song_credit_artists` 关系表，而是复用第十步导出函数从当前 SQLite `songs`、`albums`、`song_singers`、`song_credit_artists` 重新生成 `data/processed/validation/temp_song_filtering/csv_views/songs_after_step10_credit_import.csv`。
- 导出结果为 105,705 行，文件大小约 19.5 MB，表头为 `song_mid`、`song_id`、`song_name`、`song_title`、`song_language`、`album_name`、`album_type`、`album_publish_date`、`作词`、`作曲`、`singer_count`、`singers_json`。
- 验证方式为回读新 CSV，检查文本字段中是否仍存在去掉开头空白后以 `=`、`+`、`-`、`@` 开头且未加单引号的值；结果未发现未转义样本，并观察到 `'+ -×÷`、`'+-×÷` 等已转义歌名。

### 插入作词作曲完整性过滤步骤
- 用户要求在第十步导入作词作曲之后先删除作词作曲不完整的歌曲，因为后续网页可视化必须有作词和作曲关系；用户已确认当前会删除很多歌曲。
- 本次将“不完整”定义为歌曲在 `song_credit_artists` 中缺少至少 1 个 `作词` 或缺少至少 1 个 `作曲`；只有同时至少存在 1 个 `作词` 和 1 个 `作曲` 的歌曲才保留。
- 已新增 `music_metadata_graph/pipelines/filter_songs_by_credit_completeness.py` 作为新的第十一步，默认导出删除清单 `data/processed/validation/song_filtering/csv_views/songs_removed_by_step11_incomplete_credits.csv`，并额外导出保留歌曲临时 CSV `data/processed/validation/temp_song_filtering/csv_views/songs_after_step11_complete_credits.csv`。
- 新第十一步删除 `songs` 记录，`song_singers` 和 `song_credit_artists` 依赖外键级联删除；删除清单和保留清单均使用第十步及之后的 12 列歌曲 CSV 规则，包含 `作词`、`作曲` 并应用 Excel 公式安全转义。
- 已将原“规范化歌名 + 同歌手”去重顺延为第十二步，默认输出路径改为 `songs_removed_by_step12_same_singer_name_dedupe.csv` 和 `songs_after_step12_same_singer_name_dedupe.csv`，命令入口仍为 `music_metadata_graph.pipelines.filter_imported_songs`。
- 已在 `pyproject.toml` 增加脚本入口 `mr-filter-songs-credit-completeness`，并同步 `README.md` 和 `AGENTS.md` 的流程、路径和规则说明。

### 验证并执行第十一步作词作曲完整性过滤
- 语法验证对象为 `filter_songs_by_credit_completeness.py` 和 `filter_imported_songs.py`，执行项目指定 Conda 解释器的 `py_compile`，结果未报错。
- 先在临时 SQLite 副本上运行新第十一步，结果为 105,705 首歌曲中删除 84,785 首，保留 20,920 首；其中缺作词 82,872 首，缺作曲 80,565 首，同时缺两者 78,652 首；临时库执行后缺作词或缺作曲歌曲为 0，`PRAGMA foreign_key_check` 返回 0 行。
- 正式执行前已备份当前数据库到 `data/music_metadata_graph_before_step11_credit_filter_20260515_014018.bak.sqlite3`。
- 正式库执行新第十一步后，`songs` 为 20,920 行，`song_singers` 为 24,689 行，`song_credit_artists` 为 53,593 行；缺作词或缺作曲歌曲为 0，`PRAGMA foreign_key_check` 返回 0 行。
- 删除清单 CSV 为 84,785 行，保留临时 CSV 为 20,920 行；两份 CSV 表头均为 `song_mid`、`song_id`、`song_name`、`song_title`、`song_language`、`album_name`、`album_type`、`album_publish_date`、`作词`、`作曲`、`singer_count`、`singers_json`。
- 已回读两份新 CSV 检查 Excel 公式风险，未发现去掉开头空白后仍以 `=`、`+`、`-`、`@` 开头且未转义的文本样本。

### 限定第十步临时 CSV 导出范围
- 用户要求第十步导出的临时歌曲 CSV 改为只导出演唱歌手包含周杰伦、林俊杰、薛之谦、汪苏泷的歌曲。
- 已修改 `music_metadata_graph/pipelines/import_song_credits_to_db.py`：第十步作词作曲关系入库范围保持不变，只有临时 CSV 导出查询在未显式传入 `--artist-mid` 或 `--artist-name` 时默认筛选演唱歌手包含上述四位任意一人的歌曲。
- 已新增 `--temp-export-artist-name` 参数，可重复传入以覆盖默认临时 CSV 歌手范围；已新增 `--all-temp-songs-csv` 参数，可恢复导出当前 `songs` 表全部歌曲。
- 已同步 `README.md` 和 `AGENTS.md`，记录第十步临时 CSV 的默认四歌手范围，以及该范围只影响临时 CSV、不影响作词作曲关系入库的边界。
- 已使用第十一步执行前的 SQLite 备份重新生成 `data/processed/validation/temp_song_filtering/csv_views/songs_after_step10_credit_import.csv`，确保该文件仍对应“第十步后、第十一步前”的阶段；新 CSV 为 985 行。
- 验证结果：`import_song_credits_to_db.py` 通过 `py_compile`；`--help` 显示新增 `--temp-export-artist-name` 和 `--all-temp-songs-csv`；默认导出查询的入库目标歌曲数仍为 20,920，当前正式库默认临时导出范围为 801 行，未缩小导入范围；基于第十一步前备份生成的第十步临时 CSV 为 985 行，所有行的 `singers_json` 均包含四位目标歌手之一，且未发现 Excel 公式未转义样本。

### 调整第十二步去重规则为同作词作曲
- 用户要求第十二步不再按“歌名相同且演唱歌手相同”去重，改为“歌名相同且作词、作曲也分别相同”时再按既有优先级删除。
- 已修改 `music_metadata_graph/pipelines/filter_imported_songs.py`：第十二步分组键改为规范化歌名、作词签名、作曲签名；作词和作曲分别按 `song_credit_artists.artist_order` 排序后的 `artist_mid` 序列生成签名，演唱歌手不再参与本步骤去重判断。
- 第十二步保留优先级继续沿用 `录音室专辑 > EP > Single > 较小 song id`；`songs.mid` 主键和 `songs.id` 唯一约束仍只做唯一性检查，不额外执行 mid/id 去重。
- 已将第十二步默认导出路径改为 `data/processed/validation/song_filtering/csv_views/songs_removed_by_step12_same_credit_name_dedupe.csv` 和 `data/processed/validation/temp_song_filtering/csv_views/songs_after_step12_same_credit_name_dedupe.csv`，避免文件名继续表达旧的同歌手规则。
- 已同步 `README.md` 和 `AGENTS.md`，记录第十二步新规则、作词作曲签名判断方式、演唱歌手不参与判断和新 CSV 路径。

### 验证并执行第十二步同作词作曲去重
- 语法验证对象为 `filter_imported_songs.py`，执行项目指定 Conda 解释器的 `py_compile`，结果未报错。
- 先在临时 SQLite 副本上运行新第十二步，结果为 20,920 首歌曲中删除 814 首，保留 20,106 首；临时库执行后按规范化歌名、作词签名、作曲签名检查重复组为 0，`PRAGMA foreign_key_check` 返回 0 行。
- 正式执行前已备份当前数据库到 `data/music_metadata_graph_before_step12_credit_name_dedupe_20260515_015741.bak.sqlite3`。
- 正式库执行新第十二步后，`songs` 为 20,106 行，`song_singers` 为 23,592 行，`song_credit_artists` 为 51,812 行；按代码同一套规范化函数和作词作曲签名检查，剩余重复组为 0，`PRAGMA foreign_key_check` 返回 0 行。
- 删除清单 CSV 为 814 行，保留临时 CSV 为 20,106 行；两份 CSV 表头均为 `song_mid`、`song_id`、`song_name`、`song_title`、`song_language`、`album_name`、`album_type`、`album_publish_date`、`作词`、`作曲`、`singer_count`、`singers_json`。
- 已回读两份新 CSV 检查 Excel 公式风险，未发现去掉开头空白后仍以 `=`、`+`、`-`、`@` 开头且未转义的文本样本。

### 限定第十二步临时保留 CSV 导出范围
- 用户要求第十二步导出的临时 CSV 也改为只保留周杰伦、林俊杰、薛之谦、汪苏泷四位歌手相关歌曲。
- 已修改 `music_metadata_graph/pipelines/filter_imported_songs.py`：第十二步全库去重和正式删除清单范围保持不变，只有临时保留 CSV 默认筛选演唱歌手包含上述四位任意一人的保留歌曲。
- 已新增 `--temp-export-artist-name` 参数，可重复传入以覆盖默认临时 CSV 歌手范围；已新增 `--all-temp-kept-csv` 参数，可恢复导出第十二步后的全部保留歌曲。
- 已同步 `README.md` 和 `AGENTS.md`，记录第十二步临时保留 CSV 的默认四歌手范围，以及该范围只影响临时 CSV 查看范围、不影响全库去重和正式删除清单的边界。
- 已直接重写 `data/processed/validation/temp_song_filtering/csv_views/songs_after_step12_same_credit_name_dedupe.csv`，未重跑第十二步删除逻辑，也未覆盖正式删除清单。
- 验证结果：`filter_imported_songs.py` 通过 `py_compile`；`--help` 显示新增 `--temp-export-artist-name` 和 `--all-temp-kept-csv`；新临时 CSV 为 777 行，所有行的 `singers_json` 均包含四位目标歌手之一；未发现 Excel 公式未转义样本；当前数据库仍为 `songs=20106`、`song_singers=23592`、`song_credit_artists=51812`，`PRAGMA foreign_key_check` 返回 0 行。

### 修正第十二步作词作曲比较为集合语义
- 用户指出第十二步多人作词作曲比较不应按字符串顺序比较，同一角色内的人员顺序不应影响是否判定为相同。
- 已修改 `music_metadata_graph/pipelines/filter_imported_songs.py`：`credit_signature()` 改为对同一 `song_mid`、同一 `role` 下的 `artist_mid` 做集合去重并排序后生成签名，因此 `A/B` 与 `B/A` 会被视为同一组作词或作曲。
- CSV 展示中的 `作词`、`作曲` 仍沿用 `song_credit_artists.artist_order` 输出，不影响人工查看顺序；本次只改变第十二步去重比较语义。
- 已同步 `README.md` 和 `AGENTS.md`，记录第十二步按作词集合、作曲集合判断，同一角色内人员顺序不影响比较。
- 为避免正式删除清单只记录增量，已使用第十二步执行前的 SQLite 备份重新跑完整第十二步，并在替换当前数据库前备份当前库到 `data/music_metadata_graph_before_step12_credit_set_dedupe_20260515_021847.bak.sqlite3`。
- 新集合语义第十二步完整结果：从第十一步后的 20,920 首歌曲中删除 827 首，保留 20,093 首；相比旧顺序语义多删除 13 首。
- 当前正式库结果为 `songs=20093`、`song_singers=23573`、`song_credit_artists=51763`；按集合语义检查剩余重复组为 0，`PRAGMA foreign_key_check` 返回 0 行。
- 正式删除清单 `songs_removed_by_step12_same_credit_name_dedupe.csv` 为 827 行；第十二步四歌手临时保留 CSV `songs_after_step12_same_credit_name_dedupe.csv` 为 776 行，所有行的 `singers_json` 均包含周杰伦、林俊杰、薛之谦、汪苏泷之一；未发现 Excel 公式未转义样本。
- 验证结果：`filter_imported_songs.py` 通过 `py_compile`。

### 临时验证单曲作词作曲信息
- 用户要求验证歌曲 `001rG4cI4L2Qqc` 的作词、作曲信息，并明确不要使用缓存。
- 本次使用项目指定 Conda Python 直接调用 `qqmusic_api.Client().song.get_producer("001rG4cI4L2Qqc")` 实时请求 QQ 音乐制作人接口；未读取 `data/raw/qqmusic/song_producer/`，未写入 raw JSON 缓存。
- 沙箱内首次请求因网络权限返回 `WinError 5 拒绝访问`；随后经授权在沙箱外重试成功。
- 实时结果确认歌曲为《御龙镜中隐》，QQ 音乐制作人接口返回 `ReinforceMsg` 为 `词：汪苏泷、刘颜嘉/马寅生 / 曲：金若晨、岳敉亮/汪苏泷/刘颜嘉 / 编曲：金若晨`。
- 结构化 `Lst` 中 `作词` 为两条：`汪苏泷`（`SingerMid=001z2JmX09LLgL`）和 `刘颜嘉/马寅生`（`SingerMid` 为空）；`作曲` 为两条：`金若晨`（`SingerMid=0039cGaQ3kEu8n`）和 `岳敉亮/汪苏泷/刘颜嘉`（`SingerMid` 为空）。
- 边界记录：接口把部分多人姓名以斜杠合并为单个 producer 文本且不提供 `SingerMid`，当前结果只作为该接口实时返回的验证结论，不做自动拆分或入库修改。

### 检查错误源头制作人姓名在库命中
- 用户指出歌曲 `001rG4cI4L2Qqc` 的作词、作曲从第二位开始为源头信息错误，要求检查 `刘颜嘉`、`马寅生`、`岳敉亮` 三人在当前数据库中是否有命中。
- 本次只查询当前 SQLite `data/music_metadata_graph.sqlite3` 的 `artists` 表，未请求外部接口，未修改数据库。
- 精确查询结果：`刘颜嘉` 命中 1 条，`mid=003Y7awa2OLBok`；`马寅生` 命中 1 条，`mid=00449dq60zHQt4`；`岳敉亮` 命中 0 条。
- 包含查询结果：`刘颜嘉`、`马寅生` 各自只命中同名记录；`岳敉亮` 在 `name` 和 `other_name` 中均无命中。进一步按单字检查，`敉` 在 `artists.name/other_name` 中命中 0 条。
- 结论：当前库可以为 `刘颜嘉` 和 `马寅生` 提供已有 QQ 音乐 MID；`岳敉亮` 暂无库内身份记录。

### 实时请求岳敉亮歌手信息
- 用户提供歌手 MID `001ijwI032LEGX`，要求请求该歌手信息。
- 本次使用项目指定 Conda Python 直接调用 `qqmusic_api.Client().singer.get_info("001ijwI032LEGX")` 实时请求 QQ 音乐歌手信息接口；未写入数据库，也未写入 `data/raw/qqmusic/singer_info/` 缓存。
- 沙箱内首次请求因网络权限返回 `WinError 5 拒绝访问`；随后经授权在沙箱外重试成功。
- 实时结果：`Info.Singer.SingerMid=001ijwI032LEGX`，`Info.Singer.Name=岳敉亮`，`Info.Singer.SingerID=6122657`，`Info.Singer.SingerPic` 为空；`Info.BaseInfo.Name` 和 `Info.BaseInfo.Avatar` 为空，`Info.BaseInfo.BackgroundImage` 为 `https://y.qq.com/music/common/upload/t_celebrity_certification/1899104.png`。
- 边界记录：该 MID 可作为当前库中缺失的 `岳敉亮` 身份候选，但本次只完成实时验证，未自动补入 `artists`。

### 按岳敉亮姓名请求主页歌曲并检查 MID
- 用户要求通过 `岳敉亮` 的名字请求歌曲主页，检查返回歌曲有哪些，以及哪些歌曲的 `singer[]` 中包含他的 MID。
- 本次使用项目指定 Conda Python 实时调用 QQ 音乐接口：先用 `search.search_by_type("岳敉亮", SearchType.SINGER)` 搜索歌手，再用搜索命中的 `001ijwI032LEGX` 调用 `singer.get_tab_detail(..., TabType.SONG, page=1, num=30)`；未读取或写入本地 raw 缓存，未修改数据库。
- 搜索结果命中 1 位歌手：`singerName=岳敉亮`，`singerMID=001ijwI032LEGX`，`singerID=6122657`，接口摘要显示歌曲 7 首、专辑 3 张。
- 主页歌曲 Tab 返回 1 页 7 首，`HasMore=false`；7 首歌曲的 `singer[]` 均包含 `001ijwI032LEGX`，未发现返回歌曲缺少该 MID。
- 返回歌曲为：`年轻的窦唯`（`004ZWpfV13BN4l`）、`Tizzy T-橘子999`（`000AoJP63cnVr7`）、`YJC no bottom line 2022cypher`（`002R0Xtt3UquQU`）、`飞天茅台`（`0047Usrm1zKa7Y`）、`天上的星星不说话`（`000O57eZ1joZN4`）、`欺骗游戏`（`003UDF8h2sYKri`）、`Show Time`（`003LwWHn3xklYR`）。
- 边界记录：本次只验证歌手主页歌曲列表的演唱歌手 MID，不代表 `001rG4cI4L2Qqc` 制作人接口中错误合并的作曲文本已被自动纠正。

### 测试张杰姓名搜索接口返回
- 用户要求用 `张杰` 搜索测试按名字查歌手的接口表现。
- 本次先实时调用 `search.search_by_type("张杰", SearchType.SINGER, num=10, page=1)`，接口返回风控错误 `触发风控, 需登录或者安全验证`，未得到候选列表。
- 随后实时调用更轻量的 `search.quick_search("张杰")` 成功，未读取或写入本地缓存，未修改数据库。
- `quick_search` 的歌手区块返回 2 条：`张杰`（`mid=002azErJ0UcDN6`，`id=6499`）和 `张杰峰`（`mid=000FUs8S16Fen3`，`id=12453042`）。
- 边界记录：`quick_search` 可用于姓名到候选 MID 的轻量解析，但返回结构比 `search_by_type` 简略；对热门关键词，正式分页歌手搜索可能触发登录或安全验证。

### 复测张杰 search_by_type 歌手搜索
- 用户直接要求执行 `search_by_type("张杰", SearchType.SINGER)`。
- 本次使用项目指定 Conda Python 构造 `Client().search.search_by_type("张杰", SearchType.SINGER)`，确认该调用返回 `PaginatedRequest`，需要通过 `await Client().execute(request)` 执行；未读取或写入本地 raw 缓存，未修改数据库。
- 沙箱内首次执行因网络权限返回 `WinError 5 拒绝访问`；随后经授权在沙箱外重试。
- 实时执行结果仍为 QQ 音乐接口风控：`RatelimitedError`，业务码 `2001`，提示 `触发风控, 需登录或者安全验证`；响应体中 `singer=[]`，未得到候选歌手列表。
- 边界记录：对热门关键词 `张杰`，当前未登录状态下 `search_by_type(..., SearchType.SINGER)` 不稳定，可能无法作为姓名到 MID 的可靠入口；此前 `quick_search("张杰")` 可返回轻量候选，但结果结构不等同于分页歌手搜索。

### 对比测试周杰伦与菠萝塞东 search_by_type 歌手搜索
- 用户要求分别执行 `search_by_type("周杰伦", SearchType.SINGER)` 和 `search_by_type("菠萝塞东", SearchType.SINGER)`。
- 本次使用项目指定 Conda Python 实时构造两个 `Client().search.search_by_type(..., SearchType.SINGER)` 请求，并通过 `await Client().execute(request)` 执行；未读取或写入本地 raw 缓存，未修改数据库。
- 沙箱内首次执行两个关键词均因网络权限返回 `WinError 5 拒绝访问`；随后经授权在沙箱外重试。
- `周杰伦` 实时执行结果为 QQ 音乐接口风控：`RatelimitedError`，业务码 `2001`，提示 `触发风控, 需登录或者安全验证`；响应体中 `singer=[]`，未得到候选歌手列表，`estimate_sum=1`。
- `菠萝塞东` 实时执行结果同样为 QQ 音乐接口风控：`RatelimitedError`，业务码 `2001`，提示 `触发风控, 需登录或者安全验证`；响应体中 `singer=[]`，未得到候选歌手列表，`estimate_sum=12`。
- 边界记录：本次对比说明当前未登录状态下 `search_by_type(..., SearchType.SINGER)` 对常见和非常见关键词都可能被同一风控拦截，不能仅用关键词热门程度解释失败。

### 复测岳敉亮 search_by_type 歌手搜索
- 用户要求再次执行 `search_by_type("岳敉亮", SearchType.SINGER)`。
- 本次使用项目指定 Conda Python 实时构造 `Client().search.search_by_type("岳敉亮", SearchType.SINGER)` 请求，并通过 `await Client().execute(request)` 执行；未读取或写入本地 raw 缓存，未修改数据库。
- 沙箱内首次执行因网络权限返回 `WinError 5 拒绝访问`；随后经授权在沙箱外重试。
- 实时执行结果为 QQ 音乐接口风控：`RatelimitedError`，业务码 `2001`，提示 `触发风控, 需登录或者安全验证`；响应体中 `singer=[]`，未得到候选歌手列表，`estimate_sum=0`。
- 边界记录：此前同一姓名曾通过 `search_by_type("岳敉亮", SearchType.SINGER)` 成功命中候选，但当前连续复测显示分页歌手搜索已被风控拦截；后续若要稳定做姓名到 MID 解析，应优先考虑本地歌手表、已知 MID、或在合规登录态下测试接口稳定性。

### 测试第一步歌手列表接口一页
- 用户要求尝试其他接口，并指定尝试第一步使用的歌手请求接口请求一页。
- 本次先复核当前第一步脚本，确认使用 `client.singer.get_singer_list_index(area=AreaType.ALL, sex=SexType.ALL, genre=GenreType.ALL, index=IndexType.ALL, page=1, num=80)`，底层模块为 `music.musichallSinger.SingerList`，方法为 `GetSingerListIndex`。
- 本次直接实时请求接口并只打印摘要；未运行正式采集脚本，未读取或写入本地 raw 缓存，未修改数据库。
- 沙箱内首次执行因网络权限返回 `WinError 5 拒绝访问`；随后经授权在沙箱外重试成功。
- 实时结果返回 `SingerIndexPageResponse`，`total=6803`，第一页返回 `singer_count=80`。前几条包括：周杰伦 `0025NhlN2yWrP4`、林俊杰 `001BLpXF2DyJe2`、陈奕迅 `003Nz2So3XXYek`、薛之谦 `002J4UUk29y8BY`、王力宏 `001JDzPT3JdvqK`、汪苏泷 `001z2JmX09LLgL`。
- 边界记录：当前未登录状态下，第一步歌手列表接口可以成功返回分页歌手数据，而 `search_by_type(..., SearchType.SINGER)` 连续多次返回风控；因此姓名到 MID 的稳定策略应优先使用本地已采集歌手列表或重新采集歌手列表索引，再按姓名/拼音筛选，而不是依赖分页搜索接口。

### 测试 quick_search 快搜接口
- 用户要求尝试另一个可以搜索歌手的接口，推测为 `quick_search`。
- 本次先确认当前库中 `Client().search.quick_search` 签名为 `quick_search(keyword: str) -> dict[str, Any]`；该方法本身是异步调用，不返回 `Request` 描述符。
- 本次使用项目指定 Conda Python 实时调用 `await client.search.quick_search(keyword)`，测试关键词为 `张杰`、`周杰伦`、`菠萝塞东`、`岳敉亮`；未读取或写入本地 raw 缓存，未修改数据库。
- 沙箱内首次请求 `c.y.qq.com/splcloud/fcgi-bin/smartbox_new.fcg` 因网络连接失败未得到业务返回；随后经授权在沙箱外重试成功。
- `张杰` 的歌手区块返回 2 条：`张杰`（`mid=002azErJ0UcDN6`，`id=6499`）和 `张杰峰`（`mid=000FUs8S16Fen3`，`id=12453042`）；同时返回 4 首单曲、2 张专辑和 2 个 MV 的轻量候选。
- `周杰伦` 的歌手区块返回 2 条：`周杰伦`（`mid=0025NhlN2yWrP4`，`id=4558`）和 `周杰伦微博台`（`mid=004Frj3P4Emgu1`，`id=4331423`）；同时返回 4 首单曲、2 张专辑和 2 个 MV 的轻量候选。
- `菠萝塞东` 的歌手、单曲、专辑、MV 区块均返回 `count=0`。
- `岳敉亮` 的歌手区块返回 1 条：`岳敉亮`（`mid=001ijwI032LEGX`，`id=6122657`）；单曲区块返回 1 条 `飞天茅台`（`mid=0047Usrm1zKa7Y`，`id=426982979`）。
- 边界记录：`quick_search` 当前可作为姓名到候选 MID 的轻量入口，且本轮未触发 `search_by_type(..., SearchType.SINGER)` 遇到的风控；但它返回的是智能框候选，不是完整分页搜索结果，候选数量少且需要结合本地歌手列表或后续 `singer.get_info(mid)` 校验。

## 2026-05-15
### 清理开发日志异常空行
- 用户指出 `develop_log.md` 日志行数明显失控，要求先去掉异常空行再判断是否恢复正常。
- 清理前文件大小为 593830012 字节，流式统计原始行数为 395660010 行，其中非空行 1982 行。
- 本次仅执行机械空行清理：保留所有非空日志文本，移除异常重复空行，并在标题前保留单个空行以维持 Markdown 可读性。
- 清理前已生成压缩备份 `develop_log.before_blank_cleanup.md.gz`，用于必要时追溯原始文件。

## 2026-05-15
### 修复开发日志 BEL 控制字符
- 用户指出 `develop_log.md` 约 1956-1972 行存在 `BEL` 异常字符。
- 复核确认异常为 ASCII 控制字符 `\x07`，来源形态符合把 `\a` 当作转义写入后丢失字母 `a`，影响 `archive`、`area`、`artists` 等词。
- 本次按同一根因修复全文件 26 处 `BEL` 控制字符，将其恢复为字母 `a`；随后继续修复 4 处垂直制表控制字符为 `v`、1 处换页控制字符为 `f`，并恢复 6 处因 `\r` 转义断裂的 `reports/` 路径、2 处因 `\n` 转义断裂的 `node_modules/` 路径。

### 插入 quick_search 缺 MID 前置补全步骤
- 用户要求在第四步和第十步之前分别插入一个缺 MID 补全步骤：对 artists 相关来源中只有姓名、没有 MID 的条目调用 quick_search，仅当返回 artist 候选中存在唯一姓名完全匹配且 MID 非空的结果时补入 artists，并分别导出 CSV 记录补充情况。
- 已新增通用 helper music_metadata_graph/pipelines/quick_search_artist_mid.py，统一 quick_search raw 缓存、唯一精确匹配判断、CSV 写出、Excel 公式安全转义和渐进落盘；脚本中途失败或被中断时，已处理名字会保留在 CSV，后续重跑会跳过已完成非失败行。
- 已新增第四步前置脚本 fill_song_singer_missing_mids.py，扫描步骤三歌曲 raw 的 SongTab.List[].singer[] 中缺 MID 演唱歌手，默认 CSV 为 data/processed/validation/song_singer_mid_fill/csv_views/song_singer_mid_fill.csv，raw 缓存为 data/raw/qqmusic/quick_search_artist_mid/song_singer/。
- 已新增第十步前置脚本 fill_song_credit_missing_mids.py，扫描步骤九制作人 raw 的 作词、作曲 缺 MID 制作人，默认 CSV 为 data/processed/validation/song_credit_mid_fill/csv_views/song_credit_mid_fill.csv，raw 缓存为 data/raw/qqmusic/quick_search_artist_mid/song_credit/。
- 已修改第七步歌曲入库脚本，默认读取第四步前置 CSV，将 matched 行按 source_name -> matched_mid 用于补齐歌曲演唱者缺失 MID；已修改第十步作词作曲导入脚本，默认读取第十步前置 CSV，将 matched 行按制作人名补齐缺失 artist_mid，并优先保留 quick_search 的头像和 raw 路径。
- 已在 pyproject.toml 增加 mr-fill-song-singer-missing-mids 和 mr-fill-song-credit-missing-mids 两个命令入口，并同步 README.md、AGENTS.md 的流程、路径和规则说明。
- 验证结果：新增和修改的五个 pipeline 文件均通过项目指定 Conda 解释器 py_compile；两个新增脚本的 --help 可正常显示参数。
- 已运行第四步前置正式四歌手范围补全，输出 CSV 共 21 个唯一缺 MID 名字，其中 12 个为唯一精确匹配并补入 artists，状态分布为 matched=12、no_singer_candidates=6、not_matched=2、ambiguous_exact_match=1。
- 第十步前置当前正式库统计为 1509 条缺 MID 制作人来源、954 个唯一名字；本次只做 5 个名字的 smoke 验证并写出临时 CSV，未执行完整 954 名字全量 quick_search，原因是低频请求预计耗时较长，正式命令已支持从已写 CSV 和 raw 缓存继续。

### 改为数据库命中缺 MID 补全结果
- 用户指出第七步歌曲入库和第十步制作人入库不应读取对应补全 CSV，因为后续不一定保留 CSV；CSV 应只作为补充情况审计产物。
- 已修改 `music_metadata_graph/pipelines/import_singer_song_tab_to_db.py`，移除 `--singer-mid-fill-csv` 参数和 CSV 读取逻辑；第七步现在直接从 `artists` 表构建 `name -> mid` 映射，只有 `artists.name` 精确且唯一命中时才补齐歌曲演唱者缺失 MID，同名多 MID 不自动选择。
- 已修改 `music_metadata_graph/pipelines/import_song_credits_to_db.py`，移除 `--credit-mid-fill-csv` 参数和 CSV 读取逻辑；第十步现在直接从 `artists` 表命中缺 MID 的作词/作曲制作人姓名，只有精确且唯一命中时才补齐 `artist_mid`。
- 已同步 `README.md` 和 `AGENTS.md`，记录两个 quick_search 前置步骤导出的 CSV 只是补充情况记录，第七步和第十步不依赖 CSV，而依赖数据库中的 `artists` 表。
- 验证结果：第七步和第十步入库脚本通过 `py_compile`；两个脚本的 `--help` 中已不再出现补全 CSV 参数；临时内存库验证确认唯一姓名可命中 MID、同名多 MID 不命中；检索确认代码和文档中不再保留“后续读取补全 CSV”的旧描述。

### 增加斜杠姓名拆分补 MID 兜底
- 用户要求两个补 MID 前置步骤增加兜底检查：当原名字搜索没有直接匹配且名字包含 `/` 时，认为可能是源信息把多个 artists 拼在一起，应按 `/` 拆分后分别搜索实际 artists。
- 已修改 `music_metadata_graph/pipelines/quick_search_artist_mid.py` 的共用 quick_search 补全逻辑：先对原名字执行唯一精确匹配；若没有直接精确命中且原名字包含 `/`，则按 `/` 拆分去重后逐个 quick_search，并继续只接受唯一精确匹配且 MID 非空的 artist。
- CSV 字段新增 `search_name` 和 `match_mode`，用于区分原始脏名字和实际搜索名；原名字行记录为 `direct`，拆分后名字记录为 `split`。补入数据库的仍是命中的真实 artist 名和 MID。
- 已调整断点恢复逻辑：旧 CSV 中只有斜杠原名字未匹配记录时，不再把该 source 视为完成，后续重跑会重新执行拆分兜底；已有 split 记录的 source 才按完成处理。
- 已同步 `README.md` 和 `AGENTS.md`，记录第四步前置和第十步前置都会在原名字无直接精确命中且包含 `/` 时按 `/` 拆分搜索。
- 验证结果：`quick_search_artist_mid.py`、`fill_song_singer_missing_mids.py`、`fill_song_credit_missing_mids.py` 通过 `py_compile`；纯函数验证确认 `刘颜嘉/马寅生` 会拆为 `刘颜嘉`、`马寅生`，重复和空片段会被去除；模拟 quick_search 验证确认 `A/B` 原名未匹配时会写出 direct 未匹配行和两个 split matched 行，并把两个拆分 artist 写入 `artists`；恢复判断验证确认旧斜杠未匹配记录不会阻止新兜底重跑。

### 优先用 artists 表避免重复补 MID 请求
- 用户指出缺 MID 条目可能已经能在第二步导入的 `artists` 表中命中，此时补 MID 前置步骤继续请求 `quick_search` 会产生不必要请求。
- 已修改 `music_metadata_graph/pipelines/quick_search_artist_mid.py`：每个待补名字先查询当前 `artists` 表，姓名精确且唯一命中时写出 `db_matched` 并跳过 `quick_search`；姓名命中多个 MID 时写出 `db_ambiguous_name` 并不自动选择；只有库内未命中时才请求 `quick_search`。
- 斜杠拆分兜底也改为同样的优先级：每个拆分名先查库，库内唯一命中则直接记录 `db_matched`，只有库内未命中才搜索。
- 汇总 JSON 新增 `db_matches`，统计本次直接从数据库命中的名字数；`matched_names` 现在同时统计 `matched` 和 `db_matched`。
- 已同步 `README.md` 和 `AGENTS.md`，记录第四步前置和第十步前置均采用“先查库、再搜索”的补 MID 策略。
- 验证结果：`quick_search_artist_mid.py`、`fill_song_singer_missing_mids.py`、`fill_song_credit_missing_mids.py` 通过 `py_compile`；模拟验证确认库内唯一命中和库内同名多 MID 均不会触发 quick_search；模拟验证确认 `A/B` 原名无候选时，拆分出的 `A`、`B` 若已在库内唯一命中，会记录 split `db_matched` 且不会对拆分名发起请求。

### 梳理当前完整数据流程
- 用户询问当前完整流程是什么。
- 本次复核 `AGENTS.md`、`develop_log.md`、`README.md`、`pyproject.toml` 和 `music_metadata_graph/pipelines/` 当前入口，确认正式流程为 QQ 音乐单数据源的 raw JSON、SQLite 入库、过滤验证 CSV 流程。
- 当前完整流程包含步骤一到步骤十二，并在步骤四和步骤十前各有一个 quick_search 缺 MID 前置补全步骤；第七步和第十步不依赖补全 CSV，而是直接查询 `artists` 表做唯一姓名命中补齐。
- 当前网页和旧端到端流程已归档，不属于正式运行入口；当前流程产物以 `data/raw/qqmusic/`、`data/music_metadata_graph.sqlite3` 和 `data/processed/validation/` 为主。

### 设计脚本运行日志保留方案
- 用户指出长时间终端运行会挤掉最早输出，要求所有脚本自动保留日志，并按脚本名和日期时间命名。
- 目标效果确定为：运行正式脚本时终端继续实时显示输出，同时在 `logs/runs/` 生成一份完整日志，文件名形如 `collect_singer_list_raw_YYYYMMDD_HHMMSS.log`；脚本异常退出时也保留 traceback。
- 实现范围限定为当前正式 Python 脚本入口，包括 `pyproject.toml` 中暴露的 pipeline 命令和字段字典工具；`song_csv.py`、`quick_search_artist_mid.py` 等 helper 模块不作为独立入口产生日志。
- 风险边界：该机制只能记录脚本启动后的 Python `stdout` 和 `stderr`，不能恢复脚本启动前已被终端 scrollback 丢弃的历史，也不记录外部 shell 提示符历史。

### 实现脚本运行日志保留功能
- 新增 `music_metadata_graph/run_log.py`，提供 `run_with_log()` 和 tee 输出对象，统一创建 `logs/runs/`、生成 `脚本名_YYYYMMDD_HHMMSS.log` 文件，并把 `stdout`、`stderr` 同步写入终端和日志文件。
- 已把 `music_metadata_graph/pipelines/` 中 14 个正式 pipeline 入口和 `music_metadata_graph/tools/write_request_json_key_dictionary.py` 的 `main()` 包装为日志入口；helper 模块保持无副作用导入。
- 已同步 `README.md` 的运行日志说明，记录日志目录、命名规则、异常输出保留行为和 `logs/` 不提交 Git 的规则。
- 已同步 `.gitignore`，明确忽略 `logs/`，避免自动生成的运行日志进入版本库。

### 验证脚本运行日志保留功能
- 验证对象为 `music_metadata_graph/` 下所有 Python 文件，执行方式为项目指定 Conda Python 运行 `py_compile`，结果未输出语法错误。
- 验证对象为 15 个正式脚本入口，执行方式为逐个运行 `python -m <module> --help`，结果全部退出码为 0，未触发真实 QQ 音乐请求。
- 日志生成验证显示 `logs/runs/` 下已生成 15 个按脚本名和时间命名的 help 日志文件；抽查 `collect_singer_list_raw_20260515_140638.log`，内容包含终端显示的 `run_log=...` 行和完整 `--help` 输出。
- 当前 Git 状态检查仍受本机 safe.directory 所有权限制影响，`git status --short` 返回 dubious ownership 提示，未据此判断工作区完整差异。

### 增强脚本日志异常退出防护
- 用户补充要求考虑终端异常退出场景，避免日志只依赖终端 scrollback 或普通缓冲。
- 已修改 `music_metadata_graph/run_log.py`：日志文件改为行缓冲打开，tee 输出每次写入后同步 flush 终端和日志文件，降低终端关闭或进程中断时最后输出丢失的概率。
- 已增加运行状态标记：每次日志记录 `run_started_at`、正常或异常的 `run_status`、以及 `run_log_closing_at`；未处理异常会先写入完整 traceback，再写入失败状态。
- 已启用 `faulthandler` 写入当前日志文件，用于 Python fatal error 时保留线程栈；退出时恢复原始 `stderr` 的 faulthandler 状态。
- Windows 下已注册控制台事件 flush 钩子，在 Ctrl+C、关闭控制台窗口、注销或关机等控制台事件触发时尽量写入事件标记并 flush 当前日志。
- 已同步 `README.md`，说明低缓冲写入、状态标记、Windows 控制台事件 flush 和无法绝对保证的边界：操作系统强杀、断电或磁盘写入失败仍可能丢失最后极短时间输出。

### 验证脚本日志异常退出防护
- 验证对象为 `music_metadata_graph/run_log.py`，执行方式为项目指定 Conda Python 运行 `py_compile`，结果未输出语法错误。
- 验证对象为正常退出路径，执行 `python -m music_metadata_graph.pipelines.collect_singer_list_raw --help`，日志 `collect_singer_list_raw_20260515_141039.log` 包含 `run_started_at`、完整 help 输出、`run_status=system_exit code=0` 和 `run_log_closing_at`。
- 验证对象为未处理异常路径，执行 `run_with_log("smoke_failure", ...)` 抛出模拟 `RuntimeError`，日志 `smoke_failure_20260515_141038.log` 包含完整 traceback、`run_status=failed` 和 `run_log_closing_at`，命令按预期以非零退出。
- 验证对象为 15 个正式脚本入口，逐个执行 `python -m <module> --help`，结果全部退出码为 0，未触发真实 QQ 音乐请求。

### 改为后台异步写入运行日志
- 用户提出写日志不应阻塞请求节奏，避免日志写入耗时后下一次请求还要再等待完整请求间隔。
- 已修改 `music_metadata_graph/run_log.py`：日志文件写入由 `AsyncLogWriter` 后台线程负责，主线程的 `stdout/stderr` tee 只把文本放入队列，后台线程顺序写盘并 flush。
- 正常退出、异常退出、`atexit` 和 Windows 控制台事件 flush 均改为 drain 当前日志队列，尽量保留已有安全防护。
- `faulthandler` 仍直接绑定真实日志文件，用于 fatal error 时写入线程栈；常规 print 日志通过后台队列写入，避免同步磁盘写入参与请求循环耗时。
- 已同步 `README.md`，说明日志写入采用后台线程队列，退出时 drain，且操作系统强杀、断电或磁盘失败仍可能丢失最后极短时间输出。

### 验证后台异步写入运行日志
- 验证对象为 `music_metadata_graph/run_log.py`，执行方式为项目指定 Conda Python 运行 `py_compile`，结果未输出语法错误。
- 验证对象为正常退出路径，执行 `python -m music_metadata_graph.pipelines.collect_singer_list_raw --help`，日志 `collect_singer_list_raw_20260515_141331.log` 包含开始时间、完整 help 输出、退出状态和关闭时间。
- 验证对象为未处理异常路径，执行 `run_with_log("smoke_async_failure", ...)` 抛出模拟 `RuntimeError`，日志 `smoke_async_failure_20260515_141330.log` 包含完整 traceback、`run_status=failed` 和 `run_log_closing_at`；命令按预期以非零退出。
- 验证对象为 `music_metadata_graph/` 下所有 Python 文件，执行方式为项目指定 Conda Python 运行 `py_compile`，结果未输出语法错误。
- 验证对象为 15 个正式脚本入口，逐个执行 `python -m <module> --help`，结果全部退出码为 0，未触发真实 QQ 音乐请求。

### 固定单次运行日志上下文
- 用户指出按实时时间生成日志名可能导致一次运行内出现多个日志，要求每次脚本开始时确定一个日志名，脚本内都复用这个日志名，不再按实时当前时间派生新日志。
- 已修改 `music_metadata_graph/run_log.py`：新增 `RunLogIdentity` 和 `RunLogContext`，在进入 `run_with_log()` 时一次性生成 `run_id` 和 `log_path`，并在日志开头写入 `run_id=...` 与 `run_log=...`。
- 已将同一进程内嵌套 `run_with_log()` 调用改为复用当前活动日志上下文；嵌套入口会写入 `run_log_reused=... nested_script=...`，不会创建第二个日志文件。
- 日志文件名冲突处理不再重新读取实时当前时间，而是在启动时固定的 `run_id` 后追加 `_02`、`_03` 等序号；若同一秒内冲突过多则显式报错。
- 已同步 `README.md`，说明每次脚本启动只生成一次 `run_id` 和 `run_log`，同一进程内后续脚本代码复用该日志上下文。

### 验证单次运行日志上下文复用
- 验证对象为 `music_metadata_graph/run_log.py`，执行方式为项目指定 Conda Python 运行 `py_compile`，结果未输出语法错误。
- 验证对象为普通入口启动，执行 `python -m music_metadata_graph.pipelines.collect_singer_list_raw --help`，日志 `collect_singer_list_raw_20260515_142036.log` 开头包含固定 `run_id` 和对应 `run_log`，后续状态行未生成新日志名。
- 验证对象为嵌套入口调用，执行外层 `run_with_log("outer_nested_smoke", ...)` 内部再调用 `run_with_log("inner_nested_smoke", ...)`；结果只生成 `outer_nested_smoke_20260515_142035.log`，未生成 `inner_nested_smoke` 日志文件，日志中包含 `run_log_reused=... nested_script=inner_nested_smoke`。
- 验证对象为 15 个正式脚本入口，逐个执行 `python -m <module> --help`，结果全部退出码为 0，未触发真实 QQ 音乐请求。

### 分析当前运行日志状态
- 用户要求查看现有日志并分析。
- 本次检查对象为 `logs/runs/` 下 9 个日志文件，总大小约 27.4 MB；其中 8 个日志已写入 `run_status=completed` 和 `run_log_closing_at`，1 个日志仍在运行中。
- 已完成日志未发现 `Traceback`、`run_status=failed`、`KeyboardInterrupt`，也未发现已完成采集步骤的 `failed_fetches` 或 `failed_searches` 非零记录。
- 已完成流程显示：歌手列表导入 6803 行 raw，按地区规则导入 2119 位 artists；歌曲歌手缺 MID 补全处理 976 个唯一姓名并导入 528 位 artists；缺失歌曲歌手信息补入 12623 位 artists；专辑详情 56293 个请求键全部命中缓存且无失败；专辑入库 56218 行、拒绝 91 行；歌曲入库 181837 首、拒绝 70558 首；第八步专辑类型过滤后保留 153979 首；制作人 raw 检查 153979 首全部命中缓存且无失败，发现缺 MID 制作人来源 79130 行。
- 当前仍在运行的日志为 `fill_song_credit_missing_mids_20260515_142807.log`，对应 Python 进程仍响应；检查时进度约为 `13754/20359`，约 67.56%，剩余 6605 个唯一姓名。
- 当前第十步前置补 MID CSV 已有 14043 行，状态分布以 `no_singer_candidates`、`not_matched`、`matched`、`db_matched` 为主；日志前段大量 `csv_existing` 表示断点恢复已生效，后段包含实际 quick_search 请求，因此速度明显慢于缓存阶段。

### 检查 artists 表 area_id 覆盖情况
- 用户要求检查当前数据库中 `artists` 数量、有 `area_id` 的数量以及 `area_id` 分布。
- 检查对象为 `data/music_metadata_graph.sqlite3` 的 `artists` 表，执行方式为项目指定 Conda Python 只读打开 SQLite 并按 `area_id` 分组统计。
- 统计快照时间为 2026-05-15 14:44:34，本次快照显示 `artists` 共 16978 行，其中 `area_id IS NOT NULL` 为 1665 行，`area_id IS NULL` 为 15313 行。
- `area_id` 分布为：`NULL` 15313 行、`0` 177 行、`1` 1488 行；有值的 `area_id` 只出现 0 和 1。
- 检查时仍有 `fill_song_credit_missing_mids_20260515_142807.log` 对应的第十步前置补 MID 脚本运行中，两次查询间 `artists` 总数发生增长，因此该结果是运行中的当前时刻快照，不是该脚本结束后的最终稳定值。

### 诊断 artists 表 area_id 数量偏少
- 用户指出第一步请求到的 JSON 中 `area_id` 为 0 和 1 的数量似乎不应只有当前数据库统计的规模。
- 本次复查第一步 raw 目录 `data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all/`，共有 86 个 page JSON、6803 行 `singerlist`，接口 `total` 为 6803。
- 第一份 raw 的 `area_id` 原始分布为：0 共 336 行、1 共 1783 行、2 共 2374 行、3 共 2291 行、4 共 9 行、5 共 3 行、6 共 7 行；按当前第二步规则应导入的 0/1 合计为 2119 行。
- 对比 raw 中 2119 个 `area_id` 为 0/1 的 MID 与当前数据库，确认 2119 个 MID 全部存在，但其中 454 个数据库 `area_id` 已变为 `NULL`，没有缺失 MID，也没有被改成其他非空地区。
- 根因定位为 `import_artists()` 的 upsert 逻辑使用 `area_id = excluded.area_id`，后续歌曲歌手、quick_search 和作词作曲制作人补入流程在同一 MID 上传入 `area_id=None` 时会覆盖第一步 raw 中已有的地区值。

### 修复 artists upsert 保留已有 area_id
- 已修改 `music_metadata_graph/pipelines/import_singer_list_to_db.py`，将 `artists` 冲突更新中的 `area_id` 改为 `COALESCE(excluded.area_id, artists.area_id)`，使后续无地区来源不会清空已有地区字段，非空新地区仍可覆盖旧值。
- 验证对象为 `music_metadata_graph/pipelines/import_singer_list_to_db.py`，执行方式为项目指定 Conda Python 运行 `py_compile`，结果未输出语法错误。
- 验证对象为临时内存 SQLite，先导入同一 MID 的 `area_id=1`，再用 `area_id=None` 更新，观察结果保留 `area_id=1`；随后用 `area_id=0` 更新，观察结果变为 `area_id=0`。
- 当前数据库中已被清空的 454 条 `area_id` 尚未回填；原因是第十步前置补 MID 脚本仍在运行并写入同一数据库，直接写库可能产生并发冲突。后续应在该脚本结束后用第一步 raw 对这 454 条进行回填验证。

### 确认第三步歌曲 Tab 请求目标口径
- 用户询问第三步歌手主页歌曲请求是否使用 `artists` 表中的全部人，以及后续补充 `artists` 后重跑第三步是否会多出需要请求歌曲的歌手。
- 复核 `music_metadata_graph/pipelines/collect_singer_song_tab_raw.py` 确认：第三步使用 `--all` 时会在脚本启动时执行 `SELECT mid, name FROM artists ORDER BY rowid`，因此目标集合是当时数据库中全部 `artists`。
- 第三步已有缓存逻辑：每个目标歌手的页面 raw 路径为 `data/raw/qqmusic/singer_homepage_song_tab/<mid>/page_XXXX_size_30.json`；文件存在且可读时默认 `cache_hit`，不会重新请求，除非传入 `--force`。
- 当前快照显示数据库 `artists` 为 16990 行，已有歌曲 Tab raw 的数据库内歌手目录为 610 个，数据库内尚无歌曲 Tab raw 的 artists 为 16380 个；另有 60 个歌曲 Tab raw 目录对应 MID 已不在当前数据库中。
- 检查时此前运行的第十步前置补 MID 日志已写入 `run_status=keyboard_interrupt`，当前未发现仍在运行的 Python 进程。

### 限定第三步只请求第二步入库歌手
- 用户要求第三步不要再对当前 `artists` 全表请求主页歌曲，而是只对第二步入库的歌手请求；当前第二步规则为 `area_id in (0, 1)`，后续规则可能变化，但不希望为此新增数据库字段。
- 已修改 `music_metadata_graph/pipelines/collect_singer_song_tab_raw.py`：第三步 `--all` 改为读取第二步同一歌手列表 raw 目录，并复用 `import_singer_list_to_db.py` 中的 `load_singers()` 和 `filter_singers_by_area()` 得到目标 MID，再与当前数据库 `artists` 做存在性校验。
- 新增第三步参数 `--singer-list-raw-dir`，默认值与第二步默认 raw 目录一致；如果第二步后续使用非默认 raw 目录，第三步可显式传入相同目录，不需要在数据库增加来源字段。
- 保留 `--mid` 和 `--name` 的手动指定行为；`--all` 仍与 `--mid`、`--name` 互斥。
- 已同步 `README.md` 和 `AGENTS.md`，记录第三步 `--all` 目标范围来自第二步当前入库规则，不会因后续补入 `artists` 自动扩大。
- 验证对象为 `collect_singer_song_tab_raw.py` 和 `import_singer_list_to_db.py`，执行方式为项目指定 Conda Python 运行 `py_compile`，结果未输出语法错误。
- 验证对象为第三步 `--help`，输出已包含 `--singer-list-raw-dir`，且 `--all` 说明为按当前第二步歌手列表入库规则选择目标。
- 验证对象为第三步目标解析，当前数据库 `artists` 为 14963 行时，`resolve_targets(--all)` 返回 2119 个目标，前几个目标为周杰伦、林俊杰、陈奕迅、薛之谦、王力宏，确认不再按全库 artists 请求。
- 本次尝试使用 `git diff` 查看差异时，当前目录未被 Git 识别为仓库，命令返回 “Not a git repository”；本次未依赖 Git 差异完成验证。

### 限定第四步前置补 MID 扫描范围
- 用户指出第四步前置补 MID 如果扫描落盘的全部歌曲 Tab raw，会混入旧第三步请求到的非目标歌手歌曲，要求改成与第三步歌曲范围一致。
- 已修改 `music_metadata_graph/pipelines/fill_song_singer_missing_mids.py`：`--all` 不再通过 `collect_missing_song_singers_to_db.py` 的“当前数据库 artists 且已有 raw”口径解析目标，而是复用第三步 `collect_singer_song_tab_raw.py` 的目标解析逻辑。
- 新增第四步前置参数 `--singer-list-raw-dir`，默认与第二步和第三步一致；如果第三步使用非默认歌手列表 raw 目录，第四步前置可传入同一目录保持范围一致。
- 保留手动 `--mid` 和 `--name` 行为，`--all` 仍与手动目标互斥。
- 当前验证显示第三步目标 MID 为 2119 个，落盘歌曲 Tab raw 目录共 670 个，其中 542 个属于第三步当前目标范围，128 个属于旧落盘但当前非目标范围；第四步前置新逻辑只会扫描目标范围内的 542 个目录。
- 源扫描验证在不触发 quick_search 的情况下完成：按第三步范围收集到 2045 条缺 MID 演唱者来源、976 个唯一名字，来源于 378 个目标歌手 raw 目录。
- 已同步 `README.md` 和 `AGENTS.md`，记录第四步前置 `--all` 范围必须与第三步一致，不得扫描历史落盘但已不属于第三步目标范围的歌手主页歌曲 raw。
- 验证对象为 `fill_song_singer_missing_mids.py` 和 `collect_singer_song_tab_raw.py`，执行方式为项目指定 Conda Python 运行 `py_compile`，结果未输出语法错误。
- 验证对象为第四步前置 `--help`，输出已包含 `--singer-list-raw-dir`，且 `--all` 说明为只扫描当前第二步歌手列表入库规则选中的歌手歌曲 raw。

### 统一第 4、5、7 步目标范围
- 用户要求把第 4、5、7 步中类似“已有 raw 目录”的口径也改成与第三步相同的目标解析，避免历史落盘但当前非目标的歌手主页歌曲 raw 继续进入流程。
- 已修改 `music_metadata_graph/pipelines/collect_missing_song_singers_to_db.py`：第 4 步 `--all` 复用第三步目标解析，并只处理第三步目标范围内已落盘 song-tab raw 的歌手。
- 已修改 `music_metadata_graph/pipelines/collect_song_album_detail_raw.py`：第 5 步 `--all` 复用第三步目标解析，并只从第三步目标范围内已落盘 song-tab raw 提取专辑请求目标。
- 已修改 `music_metadata_graph/pipelines/import_singer_song_tab_to_db.py`：第 7 步 `--all` 复用第三步目标解析，并只导入第三步目标范围内已落盘 song-tab raw；新增 `--singer-list-raw-dir` 和 `--qqmusic-raw-dir` 参数用于保持目标解析来源可配置。
- 三个步骤的 `--all` 语义统一为“第三步当前目标范围与已落盘歌曲 Tab raw 的交集”；显式 `--mid` 和 `--name` 仍按用户指定目标执行，目标 raw 缺失时仍报错。
- 当前验证显示第 4、5、7 步解析出的 `--all` 目标均为 542 个歌手，不再是所有落盘 raw 目录 670 个，也不是第三步完整目标 2119 个。
- 本地 raw 扫描验证显示三步读取的歌曲范围一致：第 4 步扫描 542 个目标歌手、226679 条歌曲 raw，发现 28 个缺失歌手信息的非空 MID 目标和 2045 个缺 MID 演唱者条目；第 5 步扫描 542 个目标歌手、226679 条歌曲 raw，提取 44078 个专辑目标，57248 条歌曲缺专辑 key；第 7 步扫描 542 个目标歌手、226679 条歌曲 raw，来源目录数为 542。
- 验证对象为 `collect_missing_song_singers_to_db.py`、`collect_song_album_detail_raw.py`、`import_singer_song_tab_to_db.py`、`fill_song_singer_missing_mids.py` 和 `collect_singer_song_tab_raw.py`，执行方式为项目指定 Conda Python 运行 `py_compile`，结果未输出语法错误。
- 验证对象为第 4、5、7 步 `--help`，输出均已包含 `--singer-list-raw-dir`，第 7 步额外包含 `--qqmusic-raw-dir`；三个脚本的 `--all` 文案均改为按当前第二步歌手列表入库规则选择目标。
- 已同步 `README.md` 和 `AGENTS.md`，记录第 4、5、7 步 `--all` 不再使用旧的“所有已有 raw 目录”口径。

### 复查当前 artists 表 area_id 状态
- 用户要求重新检查当前数据库 `artists` 表。
- 检查对象为 `data/music_metadata_graph.sqlite3` 的 `artists` 表，执行方式为项目指定 Conda Python 只读打开 SQLite 并统计总量、`area_id` 覆盖和分布。
- 统计快照时间为 2026-05-15 18:02:39，本次快照显示 `artists` 共 25997 行，其中 `area_id IS NOT NULL` 为 2119 行，`area_id IS NULL` 为 23878 行。
- `area_id` 分布为：`NULL` 23878 行、`0` 336 行、`1` 1783 行；有值的 `area_id` 只出现 0 和 1。
- 对比第一步 raw `data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all/`，raw 中 `area_id` 原始分布仍为 0 共 336 行、1 共 1783 行、2 共 2374 行、3 共 2291 行、4 共 9 行、5 共 3 行、6 共 7 行。
- 第一阶段规则选中的 2119 个 `area_id` 为 0/1 的 raw MID 当前全部存在于数据库，且数据库 `area_id` 与 raw 完全一致；未发现缺失 MID、被清空为 `NULL` 或改成其他非空值的情况。

### 梳理当前完整流程说明
- 用户要求说明当前完整流程，并明确每一步及前置步骤，不使用项目符号和编号格式。
- 已复核 `README.md`、`develop_log.md`、`pyproject.toml` 和 `music_metadata_graph/pipelines/`，确认当前正式流程为步骤一到步骤十二，并在步骤四和步骤十前各有一个 quick_search 缺 MID 前置补全步骤。
- 当前流程边界为元数据采集、SQLite 入库、歌曲过滤和人工查看 CSV；旧网页、旧图谱导出和旧端到端流程已经归档，不属于当前正式运行入口。
- 当前最新目标范围规则为：第三步 `--all` 使用第二步当前入库规则选中的歌手；第四步前置、第四步、第五步和第七步的 `--all` 使用第三步当前目标范围与已落盘歌曲 Tab raw 的交集，避免历史落盘但当前非目标的 raw 混入流程。

### 梳理当前流程 CSV 读取点
- 用户询问当前哪些步骤会读取 CSV。
- 已检查 `music_metadata_graph/pipelines/` 中的 CSV 相关代码，确认正式流程里真正打开并读取 CSV 文件的是 `quick_search_artist_mid.read_mid_fill_csv()`，用于断点续跑和复用已匹配结果。
- 第四步前置 `fill_song_singer_missing_mids.py` 会读取 `data/processed/validation/song_singer_mid_fill/csv_views/song_singer_mid_fill.csv`；第十步前置 `fill_song_credit_missing_mids.py` 会读取 `data/processed/validation/song_credit_mid_fill/csv_views/song_credit_mid_fill.csv`。
- 第七步、第八步、第九步、第十步、第十一步和第十二步会写出 CSV 供人工检查或记录过滤结果，但当前后续正式流程不读取这些 CSV 作为输入。

### 梳理两个 quick_search 前置步骤内部流程
- 用户要求说明第四步前置和第十步前置的完整内部流程，包括读取顺序、命中处理、未命中处理和后续读取行为。
- 已复核 `fill_song_singer_missing_mids.py`、`fill_song_credit_missing_mids.py` 和公共模块 `quick_search_artist_mid.py`。
- 两个前置步骤的差异在于缺 MID 名字来源：第四步前置从第三步目标范围内的歌曲 Tab raw 读取 `singer[].name` 且 `singer[].mid` 为空的演唱者；第十步前置从第九步制作人 raw 读取作词、作曲条目里 `singer_mid` 为空的制作人。
- 两个前置步骤的公共匹配顺序为：去重缺 MID 名字源；非 `--force` 时读取已有 CSV 判断已完成项；读取 `artists` 表按姓名精确匹配；未命中时读取 quick_search raw 缓存或请求 QQ 音乐；只在唯一精确命中时补入 `artists`；无精确命中且名字含 `/` 时拆分后按同样顺序处理。
- CSV 的作用是断点续跑和复用匹配结果；第七步和第十步正式导入不会读取该 CSV，而是查询 `artists` 表中已经补入或已有的唯一姓名匹配。

### 调整 quick_search 前置步骤不再读取 CSV
- 用户要求第四步前置和第十步前置保留 CSV 写出，但去掉读取旧 CSV 作为断点输入或跳过依据的逻辑；权威链路调整为缺 MID 来源 raw、`artists` 表、quick_search raw 缓存、必要时请求接口、写 CSV 视图。
- 已修改 `music_metadata_graph/pipelines/quick_search_artist_mid.py`，删除 `read_mid_fill_csv()`、旧 CSV 完成判断、从旧 CSV 反补 `artists`、`csv_existing` 统计和 `csv_existing` 跳过分支。
- 保留 `write_mid_fill_csv()`，运行中仍会把 `db_matched`、`db_ambiguous_name`、`matched`、`not_matched`、`no_singer_candidates`、`failed:*` 等结果写入 CSV 供人工检查。
- 保留 `execute_or_load_quick_search()` 的缓存逻辑：库内未唯一命中时先按名字查 quick_search raw JSON，缓存存在且未传 `--force` 时读缓存，缓存不存在或传入 `--force` 时才请求 QQ 音乐。
- 已同步 `README.md` 和 `AGENTS.md`，说明第四步前置和第十步前置每次运行都会重写 CSV 视图，流程不再读取旧 CSV 作为断点输入或跳过依据。

### 验证 quick_search 前置步骤 CSV 读取移除
- 验证对象为 `quick_search_artist_mid.py`、`fill_song_singer_missing_mids.py` 和 `fill_song_credit_missing_mids.py`，执行方式为项目指定 Conda Python 运行 `py_compile`，结果未输出语法错误。
- 验证对象为第四步前置和第十步前置入口，执行 `python -m music_metadata_graph.pipelines.fill_song_singer_missing_mids --help` 和 `python -m music_metadata_graph.pipelines.fill_song_credit_missing_mids --help`，结果均退出码为 0，未触发真实 QQ 音乐请求。
- 源码搜索确认 `quick_search_artist_mid.py` 中不再存在 `read_mid_fill_csv`、`existing_source_complete`、`build_artist_row_from_csv` 或 `csv_existing`。

### 检查补 MID CSV 拆分检索记录
- 用户询问第四步前置和第十步前置补 MID CSV 是否记录名字包含 `/` 的拆分检索过程，并希望查看这些不干净源数据的解析情况。
- 检查 `song_singer_mid_fill.csv` 显示当前第四步前置 CSV 共有 976 行，`match_mode` 全部为 `direct`，当前没有 `source_name` 包含 `/` 的记录。
- 检查 `song_credit_mid_fill.csv` 显示当前第十步前置 CSV 共有 18952 行，其中 `source_name` 包含 `/` 的记录 723 行，涉及 216 个唯一原始名字；其中 `match_mode=direct` 为 216 行，`match_mode=split` 为 507 行。
- 第十步前置拆分记录状态分布为：`split/no_singer_candidates` 238 行、`split/db_matched` 173 行、`split/not_matched` 53 行、`split/matched` 30 行、`split/db_ambiguous_name` 7 行、`split/ambiguous_exact_match` 6 行。
- 已导出便于人工查看的过滤 CSV：`data/processed/validation/song_credit_mid_fill/csv_views/song_credit_mid_fill_slash_sources.csv`，包含原始 `source_name`、拆分 `search_name`、`match_mode`、`status`、匹配 MID、匹配姓名、候选计数和来源歌曲信息。

### 修正拆分检索检查 CSV 编码
- 用户指出手工导出的 `song_credit_mid_fill_slash_sources.csv` 内容编码有问题。
- 复查文件头确认首次导出没有 UTF-8 BOM，不符合项目 CSV 通过 `utf-8-sig` 兼容 Excel 查看的一贯做法。
- 已使用 PowerShell `Export-Csv -Encoding utf8BOM` 重新导出 `song_credit_mid_fill_slash_sources.csv`。
- 验证方式为 `Format-Hex -Count 16` 检查文件头，结果显示开头字节为 `EF BB BF`，确认已改为带 BOM 的 UTF-8。

### 检查带斜杠原始名是否整体命中
- 用户询问补 MID CSV 中是否存在原始名字包含 `/` 且整体 direct 检索成功的情况，用于判断是否有真实艺人名本身带 `/`。
- 检查 `song_credit_mid_fill.csv` 中 `source_name` 包含 `/` 且 `match_mode=direct` 的 216 行，状态分布为 `no_singer_candidates` 214 行、`not_matched` 2 行，没有 `matched` 或 `db_matched`。
- 两条 direct 非 `no_singer_candidates` 记录为 `N/A` 和 `GAI/周延`，均为 `not_matched`，没有整体命中 MID。
- 当前 `song_singer_mid_fill.csv` 中没有 `source_name` 包含 `/` 且 `match_mode=direct` 的记录。

### 调整带斜杠缺 MID 名字拆分策略
- 用户判断带 `/` 的名字可直接拆分，不需要按原始整体名字搜索，并纠正拆分后不要求每个片段都能匹配；能唯一匹配的片段应入库，不能匹配的片段跳过。
- 已修改 `music_metadata_graph/pipelines/quick_search_artist_mid.py`：补 MID 前置遇到 `source_name` 包含 `/` 时不再执行整体 direct 查库或 quick_search，而是直接按 `/` 拆分，并对每个拆分片段执行查库、读 quick_search raw 缓存、必要时请求接口和写 CSV。
- 已修改 `music_metadata_graph/pipelines/import_singer_song_tab_to_db.py`：第七步歌曲入库遇到缺 MID 且歌手名包含 `/` 时，按拆分片段查询 `artists` 唯一姓名映射；能命中的片段写入 `song_singers`，不能命中的片段跳过；只有没有任何片段命中时才把歌曲按缺歌手 MID 拒绝。
- 已修改 `music_metadata_graph/pipelines/import_song_credits_to_db.py`：第十步作词作曲入库遇到缺 MID 且制作人名包含 `/` 时，按拆分片段查询 `artists` 唯一姓名映射；能命中的片段写入 `song_credit_artists`，不能命中的片段跳过。
- 已同步 `README.md` 和 `AGENTS.md`，记录带 `/` 名字不再整体搜索、拆分片段部分命中即可入库、CSV 仍只作为人工检查视图。

### 验证带斜杠拆分策略代码
- 验证对象为 `quick_search_artist_mid.py`、`import_singer_song_tab_to_db.py`、`import_song_credits_to_db.py`、`fill_song_singer_missing_mids.py` 和 `fill_song_credit_missing_mids.py`，执行方式为项目指定 Conda Python 运行 `py_compile`，结果未输出语法错误。
- 验证对象为拆分解析辅助函数，执行内联 Python 导入 `resolve_missing_artist_name_mids()` 和 `resolve_missing_artist_name_rows()`，用 `A/B/C` 和只包含 `A`、`C` 的唯一姓名映射测试，结果分别返回 `mid_a` 和 `mid_c`，确认部分片段命中即可返回。
- 本次未重跑第四步前置、第十步前置、第七步或第十步正式入库，因此现有数据库和现有补 MID CSV 仍反映旧运行结果；需要重新运行对应步骤后才会应用新拆分策略到数据产物。

### 实现一键完整流程编排入口
- 用户要求写一个脚本按顺序一键运行完整流程，并且做安全检查，不能默认上一个脚本正确跑完。
- 新增 `music_metadata_graph/pipelines/run_full_pipeline.py`，作为完整流程编排入口；该入口使用当前 Python 解释器逐个子进程调用现有正式 pipeline，保留各子脚本自身运行日志。
- 编排步骤共 14 个，将第四步前置和第十步前置补 MID 作为独立编排步骤纳入顺序；对应业务流程仍是步骤一到步骤十二加两个前置步骤。
- 编排入口在每一步前后执行检查，检查范围包括：歌手列表 raw 页和行数、`artists` 表、步骤三目标歌手歌曲 Tab raw 覆盖、歌曲 Tab 中非空歌手 MID 是否进入 `artists`、专辑 raw、`albums` 表、`songs/song_singers` 表、SQLite 外键、步骤八后专辑类型是否只剩允许值、步骤九后每首保留歌曲是否都有制作人 raw、`song_credit_artists` 表、作词/作曲角色是否存在、步骤十一后是否仍有缺作词或作曲歌曲、步骤十二后歌曲 `mid/id` 是否仍唯一。
- 新增命令行参数 `--continue-from`、`--stop-after` 和 `--dry-run`，支持从编排步骤中间继续、只跑到某一步、以及只打印命令并检查当前已有产物。
- 已在 `pyproject.toml` 增加脚本入口 `mr-run-full-pipeline = "music_metadata_graph.pipelines.run_full_pipeline:main"`。
- 已同步 `README.md` 和 `AGENTS.md`，说明一键入口、检查边界和 14 个编排步骤与 12 个业务步骤的对应关系。

### 验证一键完整流程编排入口
- 验证对象为 `run_full_pipeline.py`，执行方式为项目指定 Conda Python 运行 `py_compile`，结果未输出语法错误。
- 验证对象为 `pyproject.toml`，执行方式为项目指定 Conda Python 使用 `tomllib` 解析，结果输出 `pyproject ok`。
- 验证对象为一键入口帮助信息，执行 `python -m music_metadata_graph.pipelines.run_full_pipeline --help`，结果退出码为 0，并显示 `--continue-from`、`--stop-after` 和 `--dry-run` 参数。
- 验证对象为 dry-run 单步检查，执行 `python -m music_metadata_graph.pipelines.run_full_pipeline --dry-run --stop-after 1`，结果未执行真实采集命令，检查到当前歌手列表 raw 为 86 页、6803 行。

### 检查运行日志对应步骤
- 用户要求查看当前运行日志实际运行的是流程中的哪几步。
- 本次检查对象为 `logs/runs/` 下 13 个日志文件，文件名显示已运行第二步、第四步前置、第四步、第五步、第六步、第七步、第八步、第九步、第十步前置、第十步、第十一步和第十二步。
- 已完成日志均包含 `run_status=completed`，未在这些完成日志的尾部看到 `failed_fetches`、`failed_searches` 非零或失败状态。
- 当前未看到本轮第一步 `collect_singer_list_raw` 的运行日志，说明本轮日志目录中没有记录重新请求完整歌手列表，第二步使用的是已有歌手列表 raw。
- 当前 `collect_singer_song_tab_raw_20260515_152010.log` 对应第三步仍在写入，检查时未出现 `run_status` 结束行；日志进度从 `[1099/2119]` 增长到 `[1103/2119]`，说明第三步仍在运行中。
- 当前观察到第三步运行时间与后续步骤完成时间存在重叠，后续步骤已经基于当时已落盘的歌曲 Tab raw 和缓存继续完成；第三步本次全目标采集尚未结束。

### 重命名非本轮生成的 validation CSV
- 用户要求检查 `data/processed/validation/` 中的 CSV，并把不是本次生成的文件改名为 `deleted_1/2/3`。
- 本次将 `data/processed/validation/` 下 12 个 CSV 与 `logs/runs/` 中本轮日志明确输出的 CSV 路径交叉比对。
- 确认 11 个 CSV 出现在本轮日志输出路径中，且修改时间集中在本轮运行时间段。
- 发现旧文件 `songs_removed_by_step10_same_singer_name_dedupe.csv` 未出现在本轮日志输出路径中，修改时间为本轮运行前的旧时间。
- 已将该旧文件在原目录内重命名为 `deleted_1.csv`，未发现需要改名为 `deleted_2.csv` 或 `deleted_3.csv` 的其他旧 CSV。
- 验证结果显示原文件名已不存在，`data/processed/validation/song_filtering/csv_views/deleted_1.csv` 存在，其余本轮生成 CSV 保持原名。

### 区分 validation 中的歌曲 CSV
- 用户询问本轮 11 个 validation CSV 中哪些内容是歌曲，以及分别在哪些步骤导出。
- 已读取 11 个本轮 CSV 的表头，并与 `logs/runs/` 中的 CSV 输出路径对应。
- 确认以歌曲行为主体的 CSV 共 7 个：第七步歌曲入库拒绝 CSV、第八步专辑类型过滤删除 CSV、第十步后临时歌曲 CSV、第十一步作词作曲不完整删除 CSV、第十一步后临时保留歌曲 CSV、第十二步同名同作词作曲去重删除 CSV、第十二步后临时保留歌曲 CSV。
- 确认其余 4 个 CSV 不是歌曲明细表：第六步专辑导入拒绝 CSV、第四步前置歌曲歌手缺 MID 补全 CSV、第九步制作人缺 MID 明细 CSV、第十步前置作词作曲缺 MID 补全 CSV。

### 调整第十一步临时歌曲 CSV 导出范围
- 用户指出第十步临时 CSV 默认只导出周杰伦、林俊杰、薛之谦、汪苏泷四个人，并要求第十一步临时 CSV 也改成同样范围。
- 已确认当前数据库已经执行到第十二步，不能直接从数据库重导“第十一步后、第十二步前”的完整状态；但现有第十一步完整临时 CSV 仍保留，因此可用该 CSV 直接过滤出四个人范围。
- 已修改 `music_metadata_graph/pipelines/filter_songs_by_credit_completeness.py`：新增默认临时导出歌手范围 `周杰伦`、`林俊杰`、`薛之谦`、`汪苏泷`，新增 `--temp-export-artist-name` 和 `--all-temp-kept-csv` 参数，并在日志结果中输出 `temp_export_artist_names` 与 `exported_temp_kept_rows`。
- 已同步 `README.md` 的第十一步说明，记录第十一步临时 CSV 默认只导出四个人范围；全量保留歌曲需要显式传入 `--all-temp-kept-csv`。
- 已用现有 `songs_after_step11_complete_credits.csv` 过滤覆盖同名文件，数据行从 52821 行变为 869 行；验证显示所有 869 行的 `singers_json` 均包含四位目标歌手之一。
- 验证对象为第十一步脚本，执行方式为项目指定 Conda Python 运行 `py_compile`，结果未输出语法错误；执行 `--help` 显示新增参数已生效。

### 纠正从歌曲 Tab 后续测试入口语义
- 用户纠正“默认歌手的主页已经全请求到了”指的是步骤三按完整 `--all` 参数目标范围全部请求完成，不是指四位临时导出歌手或默认四个歌手。
- 已确认 `run_full_pipeline.py` 未保留按默认四人筛选的参数或分支；`run_from_song_tabs.py` 固定等价于完整编排 `--continue-from 4`，即从四前置开始，并先检查步骤三 `--all` 目标歌手主页歌曲 Tab raw 覆盖完整性。
- 已修改 `run_from_song_tabs.py` 的帮助描述，将前提明确为 “all step-3 --all target singer homepage song-tab raw JSON already exists”。
- 已同步 `README.md` 和 `AGENTS.md`，把测试入口前提从“默认歌手主页歌曲 Tab raw 已完成”改为“步骤三 `--all` 目标歌手主页歌曲 Tab raw 已全部完成”。

### 验证从歌曲 Tab 后续测试入口
- 验证对象为 `run_from_song_tabs.py` 和 `run_full_pipeline.py`，执行方式为项目指定 Conda Python 运行 `py_compile`，结果未输出语法错误。
- 验证对象为 `run_from_song_tabs` 帮助信息，执行 `python -m music_metadata_graph.pipelines.run_from_song_tabs --help`，结果退出码为 0，并显示该入口假设全部步骤三 `--all` 目标歌手主页歌曲 Tab raw 已存在。
- 验证对象为 dry-run 前置检查，执行 `python -m music_metadata_graph.pipelines.run_from_song_tabs --dry-run --stop-after 4`，结果在四前置前停止，提示当前仍缺少 9 个步骤三 `--all` 目标歌手的主页歌曲 Tab raw，确认该入口不会假设步骤三已经正确完成。

### 修正歌曲 Tab 后续测试入口检查口径
- 用户指出步骤三之后的 `--all` 续跑语义不是要求步骤三目标歌手主页歌曲 Tab raw 全部存在，而是只根据当前已经落盘的歌手主页歌曲 Tab raw 继续处理。
- 已确认单步脚本当前行为为：第四步前置会解析步骤三 `--all` 目标范围但只读取已存在的 raw 文件；第四步、第五步和第七步的 `--all` 也按步骤三目标范围与已落盘 raw 的交集处理。
- 已修改 `run_full_pipeline.py`，新增 `ensure_song_tab_available()`：从四前置及后续依赖歌曲 Tab raw 的步骤继续时，只要求步骤三目标范围内至少有可处理的 raw，并报告 `available_song_tab_singers`；第三步自身的 postcheck 仍保留 `ensure_song_tab_complete()`，完整一键从第三步跑完后仍检查目标覆盖完整性。
- 已修改 `run_from_song_tabs.py`、`README.md` 和 `AGENTS.md`，将该测试入口前提改为“根据当前已落盘步骤三 `--all` 目标 raw 继续”，不再表述为要求全部目标落盘。

### 验证歌曲 Tab 后续测试入口检查口径修正
- 验证对象为 `run_full_pipeline.py` 和 `run_from_song_tabs.py`，执行项目指定 Conda Python `py_compile`，结果未输出语法错误。
- 验证对象为 `run_from_song_tabs --help`，输出已说明该入口从已有步骤三 `--all` 目标主页歌曲 raw 继续，并只检查至少一个范围内 raw 目录存在。
- 验证对象为 dry-run 前置检查，执行 `python -m music_metadata_graph.pipelines.run_from_song_tabs --dry-run --stop-after 4`，结果退出码为 0，未执行真实四前置命令，只打印命令并完成已有 CSV postcheck；当前检查结果显示步骤三目标歌手 2119 个、可用主页歌曲 raw 歌手 2119 个、raw 文件 16527 个。

### 整理完整手动流程命令
- 用户要求从请求歌手开始列出完整流程每一步命令。
- 已按 `run_full_pipeline.py` 当前 `build_steps()` 中的实际模块和参数核对，确认完整编排为 14 个步骤，其中第四步前置和第十步前置 quick_search 补 MID 被单独编号。
- 当前命令口径使用项目默认数据库、QQ 音乐 raw 根目录、默认歌手列表 raw 目录和各步骤默认 validation CSV 路径。

### 检查数据库默认路径定义
- 用户询问数据库路径在几个脚本里写死。
- 源码搜索确认 `music_metadata_graph/pipelines/` 下共有 14 个脚本直接定义 `DEFAULT_DB_PATH = Path("data/music_metadata_graph.sqlite3")`。
- 另有 `run_from_song_tabs.py` 从 `run_full_pipeline.py` 导入 `DEFAULT_DB_PATH` 作为默认值，不重复写死字符串。
- 所有这些入口均暴露 `--db` 参数，因此该路径是 CLI 默认值，不是不可覆盖的固定路径。

### 集中数据库默认路径常量
- 用户要求新增单独常量文件，让所有脚本从常量文件导入数据库默认路径，避免每个脚本重复写死。
- 新增 `music_metadata_graph/pipelines/defaults.py`，定义统一的 `DEFAULT_DB_PATH = Path("data/music_metadata_graph.sqlite3")`。
- 已修改 14 个原先直接定义 `DEFAULT_DB_PATH` 的 pipeline 脚本，改为从 `music_metadata_graph.pipelines.defaults` 导入该常量；`run_from_song_tabs.py` 继续通过 `run_full_pipeline.py` 复用默认值。
- 已同步 `README.md` 和 `AGENTS.md`，记录 pipeline 默认 SQLite 路径必须复用 `defaults.py`，命令行入口仍保留 `--db` 覆盖能力。

### 验证数据库默认路径常量集中
- 验证对象为 16 个相关 pipeline 文件，执行项目指定 Conda Python `py_compile`，结果未输出语法错误。
- 验证对象为入口帮助信息，执行 `run_full_pipeline --help`、`import_singer_list_to_db --help`、`fill_song_singer_missing_mids --help`，结果均退出码为 0，`--db` 参数仍存在。
- 验证对象为所有改动模块导入链，执行内联 Python 使用 `importlib.import_module()` 导入 15 个相关模块，结果输出 `imports ok 15`。
- 源码搜索确认除 `music_metadata_graph/pipelines/defaults.py` 外，`music_metadata_graph/pipelines/` 下不再直接定义 `DEFAULT_DB_PATH = Path("data/music_metadata_graph.sqlite3")`。

### 设计并实现 MVP 流程模式
- 用户要求定义新的数据库路径用于 MVP 流程，并为需要的脚本添加 MVP 参数，以便查看最小实现；随后纠正 raw 数据仍然共用，不应另建 MVP raw 目录或重复请求已有 raw。
- 已在 `music_metadata_graph/pipelines/defaults.py` 增加 `DEFAULT_MVP_DB_PATH = Path("data/music_metadata_graph_mvp.sqlite3")` 和 `MVP_SINGER_LIMIT = 10`。
- 已修改 `collect_singer_list_raw.py`，新增 `--mvp`；MVP 模式在未显式传入 `--max-pages` 时只确保歌手列表第一页 raw 存在，raw 根目录仍使用 `data/raw/qqmusic`。
- 已修改 `import_singer_list_to_db.py`，新增 `--mvp`；MVP 模式默认写入 MVP 数据库，并只导入 `area_id in (0, 1)` 过滤后的前 10 个歌手。
- 已修改第三步目标解析和依赖该目标解析的脚本：`collect_singer_song_tab_raw.py`、`fill_song_singer_missing_mids.py`、`collect_missing_song_singers_to_db.py`、`collect_song_album_detail_raw.py`、`import_singer_song_tab_to_db.py` 新增 `--mvp`，使 `--all` 在 MVP 模式下使用同一前 10 个歌手范围。
- 已修改 `run_full_pipeline.py`，新增 `--mvp`；MVP 模式默认使用共享 raw 目录、MVP 数据库，并把 validation 输出路径从 `data/processed/validation/` 映射到 `data/processed/validation_mvp/`。
- 已修改 `run_from_song_tabs.py`，新增 `--mvp`，用于从已有共享 raw 继续 MVP 后续流程。
- 已同步 `README.md` 和 `AGENTS.md`，记录 MVP raw 共享、MVP 数据库、MVP validation 产物目录和一键命令。

### 验证 MVP 流程模式
- 验证对象为新增和修改的 MVP 相关 pipeline 文件，执行项目指定 Conda Python `py_compile`，结果未输出语法错误。
- 验证对象为 `run_full_pipeline --help`、`import_singer_list_to_db --help`、`collect_singer_song_tab_raw --help`，输出均包含 `--mvp` 参数。
- 验证对象为一键 MVP dry-run 第一段，执行 `python -m music_metadata_graph.pipelines.run_full_pipeline --mvp --dry-run --stop-after 1`，结果未执行真实请求，打印的第一步命令使用共享 raw 根目录 `data/raw/qqmusic` 并携带 `--mvp`。
- 验证对象为 MVP 编排命令生成，执行内联 Python 构造 MVP `PipelineContext` 并输出 14 个步骤参数；结果显示数据库路径均为 `data/music_metadata_graph_mvp.sqlite3`，raw 路径仍为 `data/raw/qqmusic`，validation 产物路径均位于 `data/processed/validation_mvp/`。

### 修复 MVP 第五步歌手详情缺名导致 postcheck 失败
- 用户反馈 MVP 一键流程第 5 步 `collect_missing_song_singers_to_db` 完成后，编排 postcheck 仍失败，提示歌曲 Tab 中 `0006dV7e442viT` 不在 `artists`。
- 已定位该 MID 来自 `data/raw/qqmusic/singer_homepage_song_tab/000CK5xN3yZDJt/page_0012_size_30.json` 中歌曲《不得不爱》的歌手项，歌曲 raw 里的歌手名为 `w别丢下甜甜`。
- 已检查对应 `singer_info/0006dV7e442viT.json`，QQ 音乐详情返回 `Info.Singer.Name` 为空，因此第 5 步原逻辑按 `missing_name` 跳过，导致 postcheck 失败。
- 已修改 `collect_missing_song_singers_to_db.py`：收集缺失歌手 MID 时同步保存歌曲 raw 中出现的源歌手名；当 singer_info 详情缺 name 时，`extract_singer_row()` 使用源歌手名作为兜底入库姓名。

### 验证第五步缺名兜底修复
- 验证对象为 `collect_missing_song_singers_to_db.py` 和 `run_full_pipeline.py`，执行项目指定 Conda Python `py_compile`，结果未输出语法错误。
- 验证对象为 `extract_singer_row()`，使用 `singer_info/0006dV7e442viT.json` 和 fallback name `w别丢下甜甜` 执行内联 Python，结果返回 `ok`，并生成 MID 为 `0006dV7e442viT`、姓名为 `w别丢下甜甜` 的 artist row。
- 已实际重跑 MVP 编排第 5 步：`python -m music_metadata_graph.pipelines.run_full_pipeline --mvp --continue-from 5 --stop-after 5`；结果只处理 1 个缺失 MID，命中本地缓存，导入 `w别丢下甜甜(0006dV7e442viT)`，`db_artists` 变为 921，postcheck 显示 `missing_artist_mids=0`。

### 新增业务第十三步 language 过滤
- 用户要求增加业务第 13 步，对应总编排第 15 步，筛除 `language=9` 的歌曲，导出删除 CSV，并临时导出留下的 CSV。
- 新增 `music_metadata_graph/pipelines/filter_songs_by_language.py`，默认删除 `songs.language = 9` 的歌曲；删除 CSV 默认写入 `data/processed/validation/song_filtering/csv_views/songs_removed_by_step13_language_9.csv`，临时保留歌曲 CSV 默认写入 `data/processed/validation/temp_song_filtering/csv_views/songs_after_step13_language_filter.csv`。
- 新脚本使用现有 `song_csv.write_song_csv()` 和 `include_credits=True`，因此删除 CSV 与保留 CSV 都包含歌曲基础字段、作词、作曲和歌手 JSON。
- 已接入 `run_full_pipeline.py` 第 15 个编排步骤，postcheck 会确认 `songs` 表中不再存在 `language=9`；`run_from_song_tabs.py` 默认结束步骤改为 15。
- 已在 `pyproject.toml` 增加脚本入口 `mr-filter-songs-language`。
- 已同步 `README.md` 和 `AGENTS.md`，记录业务流程从 12 步扩展为 13 步，一键编排从 14 步扩展为 15 步。

### 验证业务第十三步 language 过滤
- 验证对象为 `filter_songs_by_language.py`、`run_full_pipeline.py` 和 `run_from_song_tabs.py`，执行项目指定 Conda Python `py_compile`，结果未输出语法错误。
- 验证对象为 `filter_songs_by_language --help` 和 `run_full_pipeline --help`，结果退出码为 0，前者显示 `--rejection-csv`、`--temp-kept-csv`、`--removed-language` 和 `--mvp` 参数，后者默认 `--stop-after` 已改为 15。
- 验证对象为 `pyproject.toml`，执行项目指定 Conda Python `tomllib` 解析，结果输出 `pyproject ok`。
- 已实际在 MVP 数据库执行第 15 步：`python -m music_metadata_graph.pipelines.run_full_pipeline --mvp --continue-from 15 --stop-after 15`；结果从 1980 首中删除 9 首 `language=9`，剩余 1971 首，postcheck 显示 `language_9_songs=0`。
- 验证输出 CSV：`data/processed/validation_mvp/song_filtering/csv_views/songs_removed_by_step13_language_9.csv` 有 9 行，首行 `song_language=9`；`data/processed/validation_mvp/temp_song_filtering/csv_views/songs_after_step13_language_filter.csv` 有 1971 行。

### 复核第九步来源歌曲范围
- 用户询问第九步制作人 raw 请求的来源歌曲范围来自数据库还是 raw。
- 已复核 `collect_song_producer_raw.py`：第九步先连接 SQLite，并从当前 `songs` 表执行 `SELECT mid FROM songs ... ORDER BY name, id, mid` 得到目标歌曲 MID；正式完整流程未传 `--artist-mid`、`--artist-name` 或 `--max-songs`，因此目标范围是第八步过滤后仍保留在数据库 `songs` 表里的全部歌曲。
- 已确认第九步不会扫描歌曲 Tab raw、专辑 raw 或已有 producer raw 来决定目标歌曲范围；producer raw 目录只用于按 `song_mid` 判断缓存命中，存在且 JSON 可读时复用，不存在或缓存损坏时请求接口并写入 raw。

### 纠正当前库测试重跑范围
- 用户指出当前目标是用现有数据库测试带 `/` 名字拆分入库效果，而不是等待重新补全新增歌曲的制作人 raw。
- 已复核第七步 `import_singer_song_tab_to_db.py`：该步骤会从已有歌曲 Tab raw 重建 `songs` 和 `song_singers`，不适合作为当前只测试制作人拆分入库的最小动作。
- 已复核第十步 `import_song_credits_to_db.py`：该步骤只读取当前 SQLite 的 `songs/song_singers/artists` 与已有 `data/raw/qqmusic/song_producer/*.json`，会重建 `song_credit_artists` 并导出临时歌曲 CSV，不会请求 `song.get_producer`，也不会导入新歌曲。
- 已复核第九步 `collect_song_producer_raw.py` 才会请求制作人 raw；第十步前置 `fill_song_credit_missing_mids.py` 才可能触发 quick_search 补 MID 请求。
- 当前若只想验证新拆分逻辑，最小重跑范围应是备份数据库后只跑第十步导入；该方式不会补新增歌曲缺失的 producer raw，新增但没有 producer raw 的歌曲不会产生作词作曲关系。

### 检查总数据库第四步缺失演唱者补库进度
- 用户截图显示当前正在运行 `collect_missing_song_singers_to_db --all`，本次检查按该脚本实际 `--all` 目标解析口径只读复算进度。
- 当前默认总数据库路径为 `data/music_metadata_graph.sqlite3`，检查时数据库只有 `artists` 表，`artists` 可见行数为 2746，数据库修改时间仍停留在本步骤启动前，说明脚本尚未进入最终统一导入阶段。
- 该步骤启动口径为目标歌手 2119 个、扫描歌曲 Tab 行 463375 条、无 MID 的演唱者条目 6496 条、需要补入的唯一缺失演唱者 MID 为 31331 个。
- 只读复算显示 31331 个缺失演唱者 MID 中已有 30897 个存在 `data/raw/qqmusic/singer_info/` 详情 JSON，仍有 434 个缺失详情 JSON，按 raw 落盘口径约完成 98.61%。
- 以本次运行开始时间之后新写入或更新的详情 JSON 计，当前运行已处理 19120 个缺失 MID，约占本轮目标 61.03%；其余已存在的详情 JSON 来自历史缓存。
- 抽查已存在的 30897 个缺失演唱者详情 JSON 均可提取为可导入 artist 行；当前未发现这批缓存因缺 MID 或缺姓名不可导入。
- 当前日志文件尾部仍只有启动摘要，尚未输出逐个歌手进度或最终 JSON 汇总；因此最终导入数量、失败 MID 和跳过原因需等脚本结束后再以日志尾部和数据库行数确认。

### 确认总数据库第四步缺失演唱者补库完成
- `logs/runs/collect_missing_song_singers_to_db_20260515_211725.log` 已输出 `run_status=completed`，完成时间为 2026-05-15T20:50:40Z。
- 本次第四步共处理缺失演唱者 MID 31331 个，其中请求新增详情 JSON 19494 个、命中历史缓存 11837 个，请求失败数为 0。
- 脚本最终提取可导入歌手 31293 个，并实际导入 31293 个；`artists` 表从检查时的 2746 行增长到 34039 行。
- 本次仍跳过 38 个缺失演唱者，日志原因均为 `missing_name`；后续只读复算确认剩余 38 个 MID 均已有 `singer_info` JSON，但详情无法提取姓名且未被当前兜底逻辑导入。
- 导入完成后按同一 `--all` 目标范围复算：目标歌手 2119 个、歌曲 Tab 行 463375 条、无 MID 演唱者条目 6496 条，剩余唯一缺失演唱者 MID 为 38 个。
### 查询 MVP 库歌曲名包含空格的歌曲
- 用户要求从 MVP 库中查找歌曲名包含空格的歌曲。
- 查询对象为 `data/music_metadata_graph_mvp.sqlite3` 的 `songs` 表，当前共有 1971 首歌曲。
- 查询口径为 `songs.name` 或 `songs.title` 任一字段包含普通 ASCII 空格，并关联 `albums`、`song_singers`、`artists` 输出专辑类型和演唱者信息。
- 查询结果共 291 首；因 Windows 控制台 GBK 编码无法完整打印日文和特殊字符，已将完整结果以 UTF-8 BOM CSV 导出到 `data/processed/validation_mvp/song_name_space_query.csv`，文件大小 32606 字节。
- 追加核对严格歌名口径：仅 `songs.name` 包含普通 ASCII 空格的歌曲为 195 首；`songs.title` 包含空格为 291 首，其中 96 首属于 `name` 不含空格但 `title` 含版本信息空格。
- 已额外导出严格歌名口径 CSV 到 `data/processed/validation_mvp/song_name_space_query_name_only.csv`，文件大小 21320 字节。

### 设计第十二步中英文混排歌名规范化规则
- 用户指出第十二步现有歌名规范化过于保守，导致 `（......醉鬼阿Q）（feat.孙燕姿）` 与 `（……醉鬼阿Q）（feat. 孙燕姿）` 这类等价标题未被去重，并要求整理更完备的中英文混合书写规范或使用工具库，而不是针对单例打补丁。
- 已将第十二步歌名身份规范化抽为 `music_metadata_graph.text_normalization.normalize_song_title_identity()`，作为独立可测试能力供去重复用。
- 新规则使用确定性等价规范化，不引入模糊相似度库；覆盖 Unicode `NFKC`、中英文常见标点等价、连续省略号归一、`feat./ft./featuring` 写法归一、连续空白压缩、括号内侧空格清理、逗号/斜杠/连接符等标点两侧空格清理、大小写折叠和首尾空白清理。
- 风险边界：规则保留普通英文词间空格，不删除括号中的语义版本文本，避免把不同版本或不同英文词边界误合并；后续如需更激进的版本名处理，应单独设计人工复核视图。

### 实现第十二步歌名规范化复用
- 新增 `music_metadata_graph/text_normalization.py`，集中维护歌曲标题身份规范化规则。
- 修改 `music_metadata_graph/pipelines/filter_imported_songs.py`，使第十二步 `normalize_song_name()` 调用新的 `normalize_song_title_identity()`。
- 新增 `tests/test_text_normalization.py`，使用标准库 `unittest` 固化中英文混排等价、保留语义版本文本、保留英文词间空格、全半角与标点空格等测试场景。
- 已同步 `README.md` 和 `AGENTS.md`，记录第十二步歌名规范化必须复用统一函数及当前规则边界。

### 验证第十二步歌名规范化修正
- 验证对象为 `music_metadata_graph/text_normalization.py`、`music_metadata_graph/pipelines/filter_imported_songs.py` 和 `tests/test_text_normalization.py`，执行项目指定 Conda Python `py_compile`，结果未输出语法错误。
- 验证对象为新增单元测试，执行 `python -m unittest tests.test_text_normalization`，结果运行 4 个测试并全部通过。
- 验证对象为用户给出的两条标题，执行函数级检查后两者均规范化为 `(...醉鬼阿q)(feat.孙燕姿)`，确认得到同一身份 key。
- 验证对象为第十二步分组逻辑，使用内存 SQLite 构造两首同作词同作曲歌曲，专辑类型分别为 `Single` 与 `录音室专辑`；结果第十二步删除 `003hfx1A3MavCH`，保留 `001LID6n1Szd9Z`，符合现有保留优先级。
- 当前未重跑真实 MVP 或正式数据库第十二步，因此现有 SQLite 与已导出 CSV 尚未被本次代码修改改写。

### 检查第六步专辑详情 raw 落盘进度
- 用户截图显示当前正在运行第六步 `collect_song_album_detail_raw --all`，本次检查仅读取 raw 目录与 SQLite 元信息，不中断正在运行的采集进程。
- 第一次检查 `data/raw/qqmusic/song_album_detail/` 下已有 57789 个 `.json` 文件；间隔 15 秒后复查已有 58089 个 `.json` 文件，说明当前进程仍在持续写入专辑详情 raw。
- 按本次运行启动摘要中的目标专辑数 104844 估算，复查时 raw 文件数约占目标的 55.4%；该比例按目录文件数粗略计算，最终完成数量仍需等运行日志输出完成汇总后确认。
- 当前 `data/music_metadata_graph.sqlite3` 可见表仅有 `artists`，本次第六步检查未发现专辑详情已经导入数据库表；当前可确认的是 raw JSON 文件落盘进度。

### 设计 MVP 数据库可视化方案
- 用户说明 MVP 流程已跑通且已有 MVP 数据库，要求实现最后一步可视化，并指出归档第一版可视化可参考但旧版数据源是 JSON。
- 已按当前流程边界确认本轮目标为从 SQLite 数据库生成本地静态图谱页面，不回写归档目录，不恢复旧 JSON 作为正式数据源。
- 目标效果为运行一个命令后生成 `data/visualization_mvp/index.html`，页面打开即可查看音乐人合作关系图谱，支持搜索、最小歌曲数筛选、有向/无向切换、作词作曲分开或合并显示、自我创作边显示开关、节点详情、边详情、歌曲明细和关系明细。
- 关系口径定义为“作词/作曲人 -> 演唱者”；边的支撑歌曲来自当前 `songs`、`song_singers`、`song_credit_artists`、`artists`、`albums` 表联查；节点优先使用 `artists.icon` 作为头像。
- 风险边界为头像 URL 依赖外部网络、正式大库边数可能需要后续切片或导出上限、浏览器真实渲染仍需在用户本机打开页面确认。
- 本轮不做在线采集、不做后端服务、不提交生成的 HTML 或数据库、不修改归档旧网页。

### 实现 MVP 数据库静态图谱生成器
- 新增 `music_metadata_graph/visualization/build_static_graph.py`，实现从 SQLite 读取当前标准表并生成自包含 `index.html`。
- 新增 `music_metadata_graph/visualization/__init__.py` 和 `music_metadata_graph/visualization/vendor/`，将 force-graph 前端运行时及其 MIT 许可证作为当前可视化模块的本地资源，避免默认依赖被 `.gitignore` 排除的 `node_modules`。
- 新增命令入口 `mr-build-static-graph`；模块入口支持 `--mvp`、`--db`、`--output-dir`、`--title`、`--vendor` 和 `--include-self-edges`。
- 页面端内联图谱数据和 force-graph 运行时代码，避免直接双击 HTML 时浏览器因 `file://` 跨文件读取限制无法加载外部 JSON。
- 页面默认隐藏自我创作边，但导出数据保留自我边，由“自我创作”开关在浏览器端控制显示，避免生成阶段丢失可切换信息。
- 同步 `README.md`，增加 MVP 可视化命令、默认输出路径、页面功能、关系口径和生成物不提交 Git 的说明。
- 新增 `tests/test_static_graph_build.py`，覆盖 SQLite 到图谱数据的核心关系口径以及嵌入 HTML 的 JSON 脚本闭合转义。

### 验证 MVP 数据库静态图谱生成器
- 验证对象为 `music_metadata_graph/visualization/build_static_graph.py` 和 `tests/test_static_graph_build.py`，执行项目指定 Conda Python `py_compile`，结果未输出语法错误。
- 验证对象为新增单元测试，执行 `python -m unittest tests.test_static_graph_build`，结果运行 2 个测试并全部通过。
- 验证对象为 `pyproject.toml`，执行项目指定 Conda Python `tomllib` 解析，结果输出 `pyproject ok`；执行 `python -m music_metadata_graph.visualization.build_static_graph --help`，结果显示可视化入口参数和说明。
- 已实际执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp`，输出 `data/visualization_mvp/index.html`，当前 MVP 数据库导出结果为 1970 首歌曲、1210 个图谱节点、2365 条关系边，默认不显示自我创作边。
- 验证输出 HTML 文件存在且大小约 2.7 MB，UTF-8 可读，无 U+FFFD 替换字符，内联数据块中没有未转义的 `</script>` 提前闭合字符串，页面包含有向/无向、职能、自我创作、阈值和搜索控件，并包含 force-graph 初始化代码。
- 尝试使用 Codex in-app browser 打开本地 `file://` 输出时被浏览器安全策略拒绝；尝试通过 `127.0.0.1` 临时 HTTP 服务验证时也被当前环境拦截或连接拒绝，因此本轮未完成真实浏览器 canvas 渲染截图验证。
- 当前替代验证覆盖了文件生成、数据规模、HTML 编码、脚本边界、入口参数和单元测试；剩余风险是用户本机浏览器实际渲染仍需打开 `data/visualization_mvp/index.html` 目检确认。

### 修复可视化节点头像未显示
- 用户反馈可视化节点不是头像。
- 复核 MVP 数据库确认 `artists` 表 1839 位音乐人均有非空 `icon`，当前图谱涉及的 1210 个节点也均有头像 URL，因此问题不在数据库头像字段缺失。
- 定位页面端 `getNodeImage()` 曾设置 `image.crossOrigin = "anonymous"`；QQ 音乐头像服务未必返回允许匿名跨域的响应，可能导致图片加载失败或无法绘制到 canvas。
- 已修改 `build_static_graph.py`：移除图片 `crossOrigin` 设置；新增 `normalize_icon_url()`，导出图谱时将 `http://` 头像 URL 升级为 `https://`。
- 已更新 `tests/test_static_graph_build.py`，新增头像 URL 升级测试；重新执行 `python -m unittest tests.test_static_graph_build`，结果运行 3 个测试并全部通过。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；静态检查确认 HTML 中不再包含 `crossOrigin`，不再包含 QQ 头像 `http://` URL，仍包含 HTTPS 头像 URL。

### 调整可视化节点名字显示和悬停高亮
- 用户要求节点名字做成开关，默认不显示名字；鼠标悬停边或节点时高亮并显示名字，高亮效果参考 force-graph 官方 highlight 示例。
- 已修改 `build_static_graph.py` 的静态页面模板，工具栏新增“显示名字”开关，页面状态 `showLabels` 默认值为 `false`。
- 已参考 force-graph highlight 示例新增 `highlightNodes`、`highlightLinks`、`hoveredNode` 和 `hoveredLink` 状态；节点悬停时高亮该节点、相邻节点和相关边；边悬停时高亮边和两端节点。
- 已调整 canvas 绘制逻辑：默认只绘制头像节点；打开“显示名字”时绘制全部名字；悬停或选中的节点即使开关关闭也会显示名字；非高亮元素在悬停状态下降低透明度。
- 已调整边绘制逻辑：高亮边加粗并加深颜色，非高亮边在悬停状态下降低宽度和颜色权重；有向/无向、职能拆分/合并逻辑保持不变。
- 已更新 `tests/test_static_graph_build.py`，新增默认名字关闭、hover 高亮集合和 hover 回调存在性测试；执行 `python -m unittest tests.test_static_graph_build`，结果运行 4 个测试并全部通过。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；静态检查确认 HTML 包含 `label-toggle`、`showLabels: false`、`highlightNodes`、`highlightLinks`、`.onNodeHover` 和 `.onLinkHover`，无 U+FFFD 替换字符，内联数据块无提前闭合脚本字符串。

### 修改可视化选中高亮交互
- 用户要求移除悬停判断，并把原来的点击选中聚焦放大改成点击选中高亮，不再聚焦放大。
- 已修改 `build_static_graph.py`：移除 `hoveredNode`、`hoveredLink` 状态和 `.onNodeHover()`、`.onLinkHover()` 回调；保留 `highlightNodes` 和 `highlightLinks` 集合，但只由点击事件更新。
- 点击节点时设置选中状态并调用 `setNodeHighlight(node)`，高亮该节点、相邻节点和相关边；点击边时调用 `setLinkHighlight(edge)`，高亮该边和两端节点；点击空白处清空选中和高亮。
- 已删除点击节点后的 `centerAt()` 和 `zoom()` 行为，页面不再因点击节点自动居中或放大。
- 已更新页面提示文案为“点击高亮相邻关系”。
- 已更新 `tests/test_static_graph_build.py`，断言默认名字关闭、点击高亮函数存在、hover 回调不存在且源码中不再包含点击聚焦放大调用；执行 `python -m unittest tests.test_static_graph_build`，结果运行 4 个测试并全部通过。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；静态检查确认源码不含 `.onNodeHover`、`.onLinkHover`、`centerAt()` 或 `.zoom()` 调用，输出 HTML 保留点击高亮文案且无 U+FFFD 替换字符。

### 移除可视化自我创作开关和自我边
- 用户要求永远不要显示自我创作，并删除“自我创作”开关。
- 已修改 `build_static_graph.py`：`build_graph_data()` 不再接收自我边显示参数，构建关系边时遇到 `source == target` 直接跳过，静态数据层不再导出自我作词或自我作曲边。
- 已删除页面工具栏中的“自我创作”开关，删除前端 `includeSelfEdges` 状态、`self-toggle` 事件处理和自我边浏览器端过滤逻辑。
- 已删除 CLI 参数 `--include-self-edges`，避免后续通过命令重新启用自我边。
- 已更新 `README.md`，说明可视化关系口径永远排除同一音乐人自己给自己作词或作曲的自我边。
- 已更新 `tests/test_static_graph_build.py`，将原“保留自我边给页面开关”测试改为“自我边永远排除”，并断言前端不再包含 `includeSelfEdges` 或 `self-toggle`。
- 验证对象为新增测试，执行 `python -m unittest tests.test_static_graph_build`，结果运行 4 个测试并全部通过；初次 `py_compile` 因 Windows 写入 `tests/__pycache__` 权限拒绝失败，随后设置 `PYTHONDONTWRITEBYTECODE=1` 重新执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边，自我边移除后边数从上一版 2365 降至 2271。
- 静态检查确认输出 HTML 不含 `self-toggle`、“自我创作”、`includeSelfEdges` 或 `initial_show_self_edges`，不含 U+FFFD 替换字符，内联数据块无提前闭合脚本字符串。

### 恢复目标歌手下拉筛选并调细高亮轮廓
- 用户反馈当前高亮轮廓太粗，并要求参考归档旧版恢复可勾选周杰伦、林俊杰等目标歌手的下拉筛选框。
- 已修改 `build_static_graph.py`，导出图谱数据时新增 `targets` 列表，取当前数据库演唱歌曲数前 10 位演唱者作为目标歌手筛选项；当前 MVP 包含陈奕迅、汪苏泷、林俊杰、周杰伦、王力宏、孙燕姿、许嵩、薛之谦、G.E.M. 邓紫棋、王源等。
- 已在页面工具栏恢复“目标歌手”下拉，支持搜索、勾选、全选和反选；筛选逻辑作用于关系边目标端，即只显示指向已勾选演唱者的作词/作曲合作关系。
- 已同步调整歌曲明细表，使其只显示当前勾选目标歌手演唱的歌曲；图谱标题和顶部说明显示当前目标歌手筛选范围。
- 已调细选中高亮轮廓：高亮外圈从 `radius + 5`、`lineWidth = 5` 调整为 `radius + 3`、`lineWidth = 2`，节点选中描边从 `3.4` 调整为 `2.2`，普通描边从 `2` 调整为 `1.5`。
- 已更新 `README.md`，补充页面支持勾选目标歌手。
- 已更新 `tests/test_static_graph_build.py`，新增目标歌手筛选数据与前端控件存在性测试；执行 `python -m unittest tests.test_static_graph_build`，结果运行 5 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；静态检查确认 HTML 包含目标歌手下拉、全选、反选、周杰伦、林俊杰，不含“自我创作”开关，无 U+FFFD 替换字符，内联数据块无提前闭合脚本字符串。

### 调整名字节点模式和详情栏信息
- 用户要求“显示名字”开关打开时名字作为节点，参考 force-graph 官方 text-nodes 示例；同时指出高亮轮廓仍太粗、不区分职能边颜色不好看、右侧详情栏未与图同高且内部滚动、节点详情第一条不应显示 MID 而应显示有用统计。
- 已修改 `build_static_graph.py`：导出节点时保留并新增 `sung_song_count`、`lyricist_song_count`、`composer_song_count`，用于节点详情统计。
- 已新增文字节点绘制逻辑：`showLabels` 打开时，节点绘制为带浅色背景和细边框的文字节点，并同步调整 `nodePointerAreaPaint`，让点击区域匹配文字节点矩形；关闭时仍使用头像圆点节点，选中节点仍显示名字标签。
- 已进一步调细高亮：高亮外圈改为 `radius + 2`、`lineWidth = 1`，选中描边改为 `1.5`，文字标签描边从 `4` 调整为 `3`。
- 已将“不区分职能”合并边颜色从灰色改为克制的绿色 `rgba(20, 132, 117, ...)`，并同步图例颜色。
- 已调整右侧详情栏：在 `renderGraph()` 中按图区域高度加面板头高度同步设置 `.detail-panel` 的 `height` 和 `maxHeight`；`.detail-panel` 改为 flex 容器，`.detail-content` 独立内部滚动。
- 已修改节点详情第一张卡，去掉 MID，改为显示“演唱 N 首 · 作词 N 首 · 作曲 N 首”；边详情和歌曲列表保持原逻辑。
- 已更新 `README.md`，把“显示节点名字”描述改为“切换头像节点或名字节点”。
- 已更新 `tests/test_static_graph_build.py`，新增节点统计字段、文字节点绘制、详情栏高度同步、合并边颜色和细轮廓检查；执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；静态检查确认 HTML 包含文字节点函数、细高亮参数、合并边新颜色、右栏高度同步逻辑、节点详情统计文案，不再包含旧的节点详情 MID 文案，无 U+FFFD 替换字符，内联数据块无提前闭合脚本字符串。

### 分析树形 DAG 效果用于合作图谱的影响
- 用户询问如果强行使用 force-graph 官方 tree 示例的层级 DAG 效果展示音乐人合作关系会产生什么后果。
- 已确认该示例的核心机制是通过 `dagMode()` 将有向无环关系按固定方向或放射方向分层排布，适合父子层级、依赖树、目录树等数据。
- 对当前音乐人合作图谱而言，作词、作曲人与演唱者之间是多对多网络，可能存在互相合作、共同作者、跨歌曲重复连接等结构，并不天然满足树或 DAG 的语义。
- 识别出的主要影响为：视觉上会更整齐、有方向感，但会把网络关系误读成上下级层级；存在环或双向关系时 DAG 布局可能需要打散、挤压或无法表达完整语义；中心音乐人和跨圈层合作关系可能被层级方向人为扭曲。
- 适合保留为可选视图或局部视图，例如“某个音乐人的作品贡献展开图”“歌曲 -> 职能 -> 音乐人”的层级钻取，不适合作为全局音乐人合作网络的默认视图。

### 调细可视化高亮边框并降低边透明度
- 用户反馈高光边框仍然太粗，并要求把边透明度降到 `0.05`。
- 已修改 `build_static_graph.py`：普通作词、作曲、合并边颜色分别调整为 `rgba(..., 0.05)`；点击选中的高亮边保留较高透明度以便与普通边区分。
- 已继续压细节点高亮视觉：头像节点高亮外圈改为 `radius + 0.6 / globalScale`、外圈线宽改为 `0.25 / globalScale`，选中或高亮头像描边改为 `0.65 / globalScale`，文字节点选中描边改为 `0.55 / globalScale`。
- 已将高亮边宽从 `2.2` 调整为 `1.8`，使点击选中关系仍可识别但不再显得过粗。
- 已更新 `tests/test_static_graph_build.py`，断言普通边透明度、细节点边框和高亮边宽参数存在。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，内联数据块无提前闭合脚本字符串，三类普通边均包含 `0.05` 透明度，高亮边和节点细边框参数均已写入产物。

### 修正可视化点击重布局和高亮语义
- 用户反馈每点一下图都会转一下，要求“作词/作曲分开”改成开关，询问有向边含义，并要求高光只给节点加轮廓、边只改为不透明，名字显示模式默认不要边框和底色。
- 已定位点击后图会继续转动的原因：点击节点、边或背景后调用完整 `render()`，`renderGraph()` 每次都会向 force-graph 重新写入 `graphData()`，触发布局继续模拟。
- 已修改点击路径：节点、边和背景点击后只调用 `renderSelection()`，刷新 canvas 和详情栏，不再重新写入图数据、重新聚焦或重跑布局；筛选、搜索、方向和职能模式变化仍会按数据变化重新渲染图谱。
- 已将“职能”下拉改为“作词/作曲分开”开关；开启时作词和作曲分别成边，关闭时合并为合作边。
- 已在页面视图控件和图谱说明中补充有向/无向含义：有向模式表示“作词/作曲人 -> 演唱者”，无向模式只合并两位音乐人的合作关系，不表达谁给谁写。
- 已修改高亮逻辑：相关边不再因高亮加粗，只把颜色透明度从 `0.05` 提升为 `1`；节点高亮仍只加细轮廓。
- 已修改名字节点绘制：未选中、未高亮时只绘制文字，不再绘制底色和边框；选中或高亮时只绘制细轮廓，不填充底色。
- 已同步 `README.md` 的 MVP 可视化说明，记录作词作曲开关、有向边含义以及点击高亮不重跑布局。
- 已更新 `tests/test_static_graph_build.py`，覆盖点击选中刷新路径、职能开关、动态边透明度、移除高亮边加粗和名字节点默认背景。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，内联数据块无提前闭合脚本字符串，包含 `role-split-toggle`、`renderSelection()`、边透明度动态逻辑和有向边说明，不再包含旧 `role-display` 下拉、选中边加粗逻辑或名字节点默认底色。

### 修复可视化节点点击详情不显示
- 用户反馈当前选中一个人后右侧数据不显示。
- 已定位为上一轮 `renderSelection()` 使用了 `graphInstance.refresh()`，当前 force-graph 实例未提供该 API 时会在点击处理里抛出异常，导致后续 `renderDetail()` 未执行。
- 已修改 `renderSelection()`：改用 `graphInstance.graphData(graphInstance.graphData())` 请求 canvas 重新绘制当前数据，再执行 `renderDetail()`；该调用不改变图数据，也不触发重新聚焦。
- 已更新 `tests/test_static_graph_build.py`，断言选中刷新路径使用 `graphInstance.graphData(graphInstance.graphData())`，并断言不再包含 `graphInstance.refresh()`。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，包含新的选中重绘调用，不再包含 `graphInstance.refresh()`，并确认 `renderDetail()` 在重绘调用之后执行。

### 修复可视化点击后布局再次转动
- 用户反馈上一轮修复详情栏后，点击图谱又变成点一下转一下。
- 已确认原因是 `renderSelection()` 中的 `graphInstance.graphData(graphInstance.graphData())` 虽然复用了当前数据，但仍会向 force-graph 重新写入图数据，触发布局模拟继续运行。
- 已修改 `renderSelection()` 为只执行 `renderDetail()`，点击节点、边或背景时不再调用任何 force-graph 实例刷新或数据写入方法。
- 已同步移除 `renderGraph()` 非数据变化分支中的 `api.refresh()` 残留，避免窗口尺寸或轻量刷新路径调用不存在或会引发副作用的刷新方法。
- 当前高亮绘制依赖页面已开启的 `.autoPauseRedraw(false)` 持续重绘画布状态，不通过重写图数据触发刷新。
- 已更新 `tests/test_static_graph_build.py`，断言不再包含 `graphInstance.graphData(graphInstance.graphData())` 和 `graphInstance.refresh()`。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，`renderSelection()` 只调用 `renderDetail()`，不含 `.refresh(` 或 `graphData(graphInstance.graphData())`，且只在图数据 key 变化时调用 `api.graphData(...)`。

### 调整可视化边宽和透明度连续映射
- 用户要求边的粗细和透明度都按当前图谱边权重连续过渡，而不是固定公式或离散状态；示例为当前图最小边 `song_count=1` 时宽度为 `1`、透明度为 `0.05`，最大边 `song_count=72` 时宽度为 `5`、透明度为 `1`，中间连续过渡。
- 用户随后补充选中高亮仍然要把边设为不透明。
- 已修改前端逻辑：每次生成当前可见图后调用 `updateEdgeWeightScale(graph.edges)`，按当前筛选结果中的最小和最大 `song_count` 计算边权重范围。
- 新增 `edgeWeightRatio(edge)`，按 `(song_count - min) / (max - min)` 得到 `0` 到 `1` 的连续比例；若当前只有一种边权重，则比例为 `0`，避免除零。
- 新增 `edgeWidth(edge)`，将比例线性映射为 `1 + ratio * 4`，即当前最小边宽 `1`、最大边宽 `5`。
- 新增 `edgeAlpha(edge)`，未高亮时将比例线性映射为 `0.05 + ratio * 0.95`，即当前最小边透明度 `0.05`、最大边透明度 `1`；选中高亮边直接返回 `1`。
- 已删除旧边宽公式 `Math.min(4, 0.8 + Math.sqrt(edge.song_count || 1) * 0.38)`，边宽不再使用平方根和 `4px` 封顶。
- 已更新 `tests/test_static_graph_build.py`，断言连续映射函数、当前边权重范围更新、选中边透明度覆盖为 `1`，并断言旧平方根宽度公式不存在。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，包含连续边宽、连续透明度、选中边不透明逻辑，不再包含旧平方根边宽公式或旧高亮边宽覆盖逻辑。

### 改为永久无向边并保留方向提示
- 用户要求删除有向边和无向边下拉菜单，图谱永远以无向边显示，但悬浮在边上时要按方向显示 `A -> B` 和 `B -> A`。
- 已删除页面“视图”下拉控件，移除前端 `directionMode` 状态和对应事件绑定。
- 已修改边合并逻辑：所有边都按两端节点排序后的无向 pair 合并；“作词/作曲分开”开启时按无向 pair + 职能合并，关闭时按无向 pair + 合作合并。
- 已将合并边内部的方向来源从字符串集合升级为 `directions` 统计数组，每个方向记录 `source`、`target`、`song_count` 和包含的职能列表。
- 已修改边悬浮提示：第一行仍显示无向两端和总歌曲数，随后按方向显示 `作词/作曲人 -> 演唱者：职能 · N 首`。
- 已修改右侧边详情：在无向总览卡片后增加方向拆解卡片，再显示支撑歌曲列表。
- 已强制关闭图上方向箭头和方向粒子，页面标题固定为“无向合作网络”，图谱说明提示“悬浮边可查看作词/作曲人 -> 演唱者方向”。
- 已同步 `README.md` 的 MVP 可视化说明，删除有向/无向切换描述，说明页面永远无向显示但悬浮和详情保留方向拆解。
- 已更新 `tests/test_static_graph_build.py`，断言不再包含方向状态或方向下拉，并断言方向拆解数据和 tooltip 文案存在。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，不含 `direction-mode` 或 `directionMode`，包含方向拆解数据、边悬浮方向文案、右侧详情方向文案，且方向箭头和方向粒子均关闭。

### 恢复可视化粒子效果开关
- 用户要求保留粒子效果，并参考归档版本改成开关控制，默认关闭。
- 已参考归档旧版 `particle-toggle` 和 `particlesEnabled` 命名，在当前工具栏新增“粒子效果”开关。
- 已新增前端状态 `particlesEnabled: false`，页面加载时默认关闭粒子效果。
- 已将 force-graph 的 `.linkDirectionalParticles()` 从固定 `0` 改为 `() => (state.particlesEnabled ? 1 : 0)`；打开开关后每条边显示 1 个流动粒子。
- 当前图谱仍永久无向显示，方向箭头继续固定关闭；粒子仅作为流动视觉效果，不表示有向边模式。
- 已同步 `README.md`，在 MVP 可视化能力说明中加入粒子效果开关。
- 已更新 `tests/test_static_graph_build.py`，断言粒子默认关闭、开关存在且粒子数量由 `state.particlesEnabled` 控制。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，包含 `particle-toggle`、`particlesEnabled: false`、粒子开关事件处理和按状态启用粒子的配置，方向箭头仍固定关闭。

### 修正粒子方向语义
- 用户纠正“粒子应该代表箭头方向”，并说明“无向边”的意思只是两个人互有作词作曲时不要显示 4 条边，而是按两人和职能合并为 2 条边。
- 已调整理解：图谱线条按两位音乐人和职能合并显示，但每条合并边内部仍保留真实 `作词/作曲人 -> 演唱者` 方向。
- 已停止使用 force-graph 内置 `linkDirectionalParticles` 表达粒子，因为内置粒子只能沿当前合并边的 `source -> target` 单一方向流动，无法在同一条合并边上同时表达 `A -> B` 和 `B -> A`。
- 已新增 `drawDirectionalParticles(edge, ctx, globalScale)` 自定义粒子绘制函数，读取边内 `directions` 数组，按每个方向的 `source` 和 `target` 节点坐标绘制流动粒子。
- 已将 `.linkCanvasObject(drawDirectionalParticles)` 和 `.linkCanvasObjectMode(() => "after")` 接入 force-graph，使粒子绘制在线条之后；保留 `.linkDirectionalParticles(0)`，避免内置单向粒子与自定义方向粒子叠加。
- 粒子开关仍默认关闭；打开后，如果一条合并边同时包含 `A -> B` 和 `B -> A`，会在同一条线上出现两个相反方向运动的粒子。
- 方向箭头仍固定关闭，避免视觉上重新拆成有向边；方向由粒子、悬浮提示和右侧详情表达。
- 已同步 `README.md`，说明图谱按两位音乐人和职能合并线条，避免互相作词作曲时显示 4 条边，但悬浮边、右侧边详情和粒子方向会按真实方向拆出 `A -> B` 与 `B -> A`。
- 已更新 `tests/test_static_graph_build.py`，断言自定义方向粒子绘制函数、link canvas 接入、内置粒子关闭，以及 direction source/target 使用存在。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，包含粒子开关、自定义方向粒子函数、方向 source/target 使用和 link canvas 接入，内置粒子和方向箭头保持关闭。

### 简化边悬浮和详情方向显示
- 用户截图指出边悬浮框和右侧详情中信息重复显示，要求先显示“作词 1 首”，再显示“谁到谁”。
- 已修改 `linkLabel(edge)`：悬浮框第一行只显示 `职能 · N 首`，后续方向行只显示 `A -> B`，不再重复显示方向行的职能和数量。
- 已修改右侧边详情：总览卡片只显示 `职能 · N 首`，方向卡片只显示 `A -> B`，不再重复显示方向行的职能和数量。
- 支撑歌曲列表保持不变，继续显示歌曲名和歌曲层面的演唱目标、职能、专辑信息。
- 已更新 `tests/test_static_graph_build.py`，断言 tooltip 总览优先显示 `edge.role` 和 `edge.song_count`，并断言前端不再包含 `formatNumber(direction.song_count)` 或方向行角色拼接展示逻辑。
- 验证对象为可视化生成器和测试文件，执行 `python -m unittest tests.test_static_graph_build`，结果运行 6 个测试并全部通过；设置 `PYTHONDONTWRITEBYTECODE=1` 执行 `py_compile`，结果未输出语法错误。
- 已重新执行 `python -m music_metadata_graph.visualization.build_static_graph --mvp` 生成 `data/visualization_mvp/index.html`；导出结果为 1970 首歌曲、1210 个节点、2271 条边。
- 静态检查确认输出 HTML 文件存在且大小约 2.4 MB，无 U+FFFD 替换字符，悬浮框保留总览和方向行，方向行不再重复显示职能和歌曲数。

### 分析专辑详情单个失败导致全流程中断
- 用户提供完整流程第 6 个编排步骤失败日志：104844 个专辑详情请求中 60734 个新请求成功、44109 个缓存命中，只有专辑 key `002o6oXX3GgGCM` 返回 `CgiApiException: CGI 请求错误 (code=104500)`，随后 `collect_song_album_detail_raw.py` 因 `failed_fetches=1` 抛出 `RuntimeError`，导致 `run_full_pipeline.py` 以 Step 6 失败中断。
- 已确认原有规则是批量单对象 raw 请求在仍有失败对象时非零退出，适合可重跑补齐的网络失败；本次边界是单个 QQ 音乐 CGI 业务错误可能长期稳定失败，继续严格失败会使 10 万级长跑在最后阶段反复卡住。
- 目标效果调整为：手动采集入口默认继续严格失败；一键完整流程对极少量专辑详情失败设置小阈值，保留失败 key、raw 路径和异常原因清单后允许继续，超过阈值仍中断。
- 风险边界为失败专辑对应歌曲后续可能因 `album_mid_not_in_albums` 被拒绝入库；这比静默伪造专辑数据更可追溯，且失败清单可用于后续人工复查或单独补采。

### 实现专辑详情失败阈值和失败清单
- 已修改 `music_metadata_graph/pipelines/collect_song_album_detail_raw.py`，新增 `--max-failed-fetches` 参数，默认值为 `0`，保持手动入口原有严格行为。
- 已新增 `--failure-json` 参数和失败报告写出逻辑，报告包含 `failed_fetches`、`failed_album_keys` 以及每个失败项的 `album_key`、`raw_json_path` 和 `reason`。
- 正式默认失败报告路径为 `data/processed/validation/album_detail_fetch_failures/album_detail_fetch_failures.json`；MVP 直接运行时默认写入 `data/processed/validation_mvp/album_detail_fetch_failures/album_detail_fetch_failures.json`。
- 已修改 `music_metadata_graph/pipelines/run_full_pipeline.py`，第 6 个编排步骤传入 `--max-failed-fetches 10` 和对应失败报告路径；`run_from_song_tabs.py` 复用完整编排，因此会继承同一 Step 6 参数。
- 已新增 `tests/test_collect_song_album_detail_raw.py` 覆盖失败阈值允许、超过阈值报错和失败 JSON 字段；新增 `tests/test_run_full_pipeline.py` 覆盖 Step 6 传参、Step 5 不误带该参数，以及 MVP 失败报告路径。
- 已同步 `README.md`，说明手动入口默认严格、可显式容忍少量失败、一键流程 Step 6 默认容忍 10 个以内失败，以及失败清单路径。

### 验证专辑详情失败阈值修复
- 验证对象为新增专辑详情失败阈值测试和完整编排传参测试，执行 `python -m unittest tests.test_collect_song_album_detail_raw tests.test_run_full_pipeline`，结果运行 5 个测试并全部通过。
- 验证对象为 `collect_song_album_detail_raw.py`、`run_full_pipeline.py` 和新增测试文件，执行项目指定 Conda Python 的 `py_compile`，结果未输出语法错误。
- 验证对象为 `collect_song_album_detail_raw --help`，输出已包含 `--max-failed-fetches` 和 `--failure-json` 参数。
- 验证对象为正式完整编排 Step 6 dry-run，执行 `run_full_pipeline --dry-run --continue-from 6 --stop-after 6`，输出命令已包含 `--max-failed-fetches 10` 和正式失败清单路径。
- 验证对象为 MVP 完整编排 Step 6 dry-run，执行 `run_full_pipeline --mvp --dry-run --continue-from 6 --stop-after 6`，输出命令已包含 `--max-failed-fetches 10`、MVP 数据库路径和 `validation_mvp` 失败清单路径。
- 当前未重新执行真实全量 Step 6 或 Step 7；本次 dry-run 观察到当前专辑详情 raw 目录已有 117043 个 JSON 文件，超过用户日志中的本轮目标 104844，说明目录内存在历史或其他范围缓存，本次修复未删除或改写这些 raw 文件。

### 补采单个失败专辑详情 raw
- 用户询问第 6 步失败是否影响其他成功落盘，并要求再次尝试请求失败专辑 key。
- 已检查用户失败日志附近的成功样本 `004ge2cw2gVAJZ`、`004geCpD31NPBI`、`004gePDM2bN0Fh`、`004geTTk3j4p3h`、`004geqQg1x80BW`，对应 raw JSON 文件均存在且可解析；失败 key `002o6oXX3GgGCM` 在重试前不存在 raw JSON 文件。
- 第一次单独请求因当前沙箱网络限制无法连接 `u.y.qq.com`，错误为本地连接拒绝，不是 QQ 音乐 CGI 业务错误。
- 经用户授权外网请求后，单独请求 `002o6oXX3GgGCM` 成功返回，专辑名为 `鹿鼎记-洗山河`，`albumMid` 为 `002o6oXX3GgGCM`。
- 已将成功响应保存到 `data/raw/qqmusic/song_album_detail/002o6oXX3GgGCM.json`，回读确认文件存在、大小为 3138 字节、JSON 可解析，`basicInfo.albumName` 为 `鹿鼎记-洗山河`。
- 随后执行 `run_full_pipeline --dry-run --continue-from 6 --stop-after 7` 仅用于检查编排命令和 raw 文件数；Step 6 postcheck 显示专辑详情 raw 文件数变为 117044。
- 该 dry-run 在 Step 7 postcheck 因数据库尚无 `albums` 表失败，原因是 dry-run 不执行 Step 7 入库命令但仍执行 postcheck；这不代表补采 raw 失败，也没有改写数据库。

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
