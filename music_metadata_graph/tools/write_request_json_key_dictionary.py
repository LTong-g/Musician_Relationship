from __future__ import annotations
import argparse
import html
import json
import zipfile
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from music_metadata_graph.run_log import run_with_log
from typing import Any

DEFAULT_SINGER_LIST_DIR = Path(
    "data/raw/qqmusic/singer_list_index/area_all_sex_all_genre_all_index_all"
)
DEFAULT_SONG_TAB_DIR = Path("data/raw/qqmusic/singer_homepage_song_tab")
DEFAULT_SONG_ALBUM_DETAIL_DIR = Path("data/raw/qqmusic/song_album_detail")
DEFAULT_OUTPUT = Path("docs/request_json_key_dictionary.xlsx")


def col_name(index: int) -> str:
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def cell_xml(value: Any, row_index: int, col_index: int) -> str:
    ref = f"{col_name(col_index)}{row_index}"
    if value is None:
        value = ""
    if isinstance(value, bool):
        return f'<c r="{ref}" t="b"><v>{1 if value else 0}</v></c>'
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f'<c r="{ref}"><v>{value}</v></c>'
    text = html.escape(str(value), quote=False)
    return f'<c r="{ref}" t="inlineStr"><is><t>{text}</t></is></c>'


def worksheet_xml(rows: list[list[Any]]) -> str:
    row_xml = []
    for row_index, row in enumerate(rows, 1):
        cells = "".join(
            cell_xml(value, row_index, col_index) for col_index, value in enumerate(row, 1)
        )
        row_xml.append(f'<row r="{row_index}">{cells}</row>')
    widths = (
        "<cols>"
        '<col min="1" max="1" width="24" customWidth="1"/>'
        '<col min="2" max="2" width="14" customWidth="1"/>'
        '<col min="3" max="3" width="22" customWidth="1"/>'
        '<col min="4" max="4" width="42" customWidth="1"/>'
        '<col min="5" max="5" width="18" customWidth="1"/>'
        '<col min="6" max="6" width="12" customWidth="1"/>'
        '<col min="7" max="7" width="48" customWidth="1"/>'
        '<col min="8" max="8" width="42" customWidth="1"/>'
        "</cols>"
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheetViews><sheetView workbookViewId="0"><pane ySplit="8" topLeftCell="A9" '
        'activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
        f"{widths}<sheetData>{''.join(row_xml)}</sheetData></worksheet>"
    )


def write_xlsx(path: Path, sheets: list[tuple[str, list[list[Any]]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    sheet_overrides = "\n".join(
        f'  <Override PartName="/xl/worksheets/sheet{index}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for index, _ in enumerate(sheets, 1)
    )
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
{sheet_overrides}
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>""".format(sheet_overrides=sheet_overrides)
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""
    sheet_entries = "".join(
        f'<sheet name="{html.escape(sheet_name)}" sheetId="{index}" r:id="rId{index}"/>'
        for index, (sheet_name, _) in enumerate(sheets, 1)
    )
    workbook = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>{sheet_entries}</sheets>
</workbook>"""
    worksheet_relationships = "\n".join(
        f'  <Relationship Id="rId{index}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{index}.xml"/>'
        for index, _ in enumerate(sheets, 1)
    )
    style_rid = len(sheets) + 1
    workbook_rels = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
{worksheet_relationships}
  <Relationship Id="rId{style_rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""
    styles = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>
  <fills count="1"><fill><patternFill patternType="none"/></fill></fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>
</styleSheet>"""
    core = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>请求 JSON 字段字典</dc:title><dc:creator>Codex</dc:creator><cp:lastModifiedBy>Codex</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>"""
    app = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Codex</Application></Properties>"""

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        archive.writestr("xl/styles.xml", styles)
        for index, (_, rows) in enumerate(sheets, 1):
            archive.writestr(f"xl/worksheets/sheet{index}.xml", worksheet_xml(rows))
        archive.writestr("docProps/core.xml", core)
        archive.writestr("docProps/app.xml", app)


def json_type(value: Any) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        if value and isinstance(value[0], dict):
            return "array<object>"
        return "array"
    if isinstance(value, dict):
        return "object"
    if value is None:
        return "null"
    return type(value).__name__


def build_singer_list_rows(raw_dir: Path) -> list[list[Any]]:
    files = sorted(raw_dir.glob("page_*_size_80.json"))
    if not files:
        raise FileNotFoundError(f"No singer list JSON files found: {raw_dir}")
    pages = []
    singers = []
    top_counts: Counter[str] = Counter()
    singer_counts: Counter[str] = Counter()
    tag_item_counts: Counter[str] = Counter()
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        pages.append(payload)
        top_counts.update(payload.keys())
        for singer in payload.get("singerlist") or []:
            singers.append(singer)
            singer_counts.update(singer.keys())
        tags = payload.get("tags") if isinstance(payload.get("tags"), dict) else {}
        for group_name, group_items in tags.items():
            if not isinstance(group_items, list):
                continue
            for item in group_items:
                if isinstance(item, dict):
                    for key in item:
                        tag_item_counts[f"tags.{group_name}[].{key}"] += 1

    sample_page = pages[0]
    sample_singer = singers[0] if singers else {}
    header = ["JSON路径", "层级", "键名", "中文释义", "数据类型", "出现次数", "示例值", "备注"]
    rows: list[list[Any]] = [
        ["请求名称", "qqmusic.singer.get_singer_list_index"],
        ["原始目录", raw_dir.as_posix()],
        ["分页文件数", len(files)],
        ["歌手行数", len(singers)],
        ["接口total", sample_page.get("total")],
        ["生成时间", datetime.now().isoformat(timespec="seconds")],
        [],
        header,
    ]
    fields = [
        (
            "$",
            "根对象",
            "area",
            "当前请求的地区筛选 ID。-100 表示全部。",
            sample_page.get("area"),
            "请求条件回显，不是歌手属性。",
        ),
        (
            "$",
            "根对象",
            "sex",
            "当前请求的性别筛选 ID。-100 表示全部。",
            sample_page.get("sex"),
            "请求条件回显。",
        ),
        (
            "$",
            "根对象",
            "genre",
            "当前请求的流派筛选 ID。-100 表示全部。",
            sample_page.get("genre"),
            "请求条件回显。",
        ),
        (
            "$",
            "根对象",
            "index",
            "当前请求的首字母索引筛选 ID。-100 表示全部。",
            sample_page.get("index"),
            "请求条件回显。",
        ),
        (
            "$",
            "根对象",
            "code",
            "接口返回状态码。0 通常表示成功。",
            sample_page.get("code"),
            "用于判断请求是否成功。",
        ),
        (
            "$",
            "根对象",
            "total",
            "当前筛选条件下的歌手总数。",
            sample_page.get("total"),
            "本次完整列表为 6803。",
        ),
        (
            "$",
            "根对象",
            "singerlist",
            "当前页歌手列表。",
            f"第一页 {len(sample_page.get('singerlist') or [])} 条",
            "主要数据数组。",
        ),
        (
            "$",
            "根对象",
            "hotlist",
            "热门歌手列表。当前完整索引请求中为空数组。",
            sample_page.get("hotlist"),
            "暂不作为主数据来源。",
        ),
        (
            "$",
            "根对象",
            "tags",
            "筛选项字典，包含地区、性别、流派和索引选项。",
            "area/genre/index/sex",
            "可用于后续构建请求维度说明。",
        ),
    ]
    for path, level, key, description, sample, note in fields:
        rows.append(
            [
                path,
                level,
                key,
                description,
                json_type(sample_page.get(key)),
                top_counts[key],
                sample,
                note,
            ]
        )

    singer_field_descriptions = {
        "id": ("QQ 音乐歌手数字 ID。", "可作为平台身份键之一。"),
        "mid": ("QQ 音乐歌手 MID。", "优先平台身份键。"),
        "name": ("歌手中文名或主要显示名。", "展示与检索字段。"),
        "title": ("接口返回标题字段；当前样例多为空。", "暂不作为主显示名。"),
        "type": ("歌手类型编码。", "含义需后续结合接口文档或样本再确认。"),
        "uin": ("QQ 音乐返回的 uin 字段。", "当前样例为 -1，暂不作为身份键。"),
        "pmid": ("接口返回的 pmid 字段。", "含义待确认。"),
        "area_id": ("歌手地区 ID。", "当前样例为 0，可能需要对照 tags.area。"),
        "country_id": ("歌手国家或地区 ID。", "当前样例为 0。"),
        "country": ("歌手国家或地区文本。", "当前样例多为空。"),
        "other_name": ("歌手别名、英文名或其他名称。", "可用于搜索和展示辅助。"),
        "spell": ("歌手名拼音或检索拼写。", "可用于排序和搜索。"),
        "trend": ("趋势字段。", "含义待确认。"),
        "concern_num": ("关注数或关注相关计数字段。", "当前样例为 0，需确认是否可信。"),
        "singer_pic": ("歌手头像 URL。", "节点头像候选来源。"),
    }
    for key in sorted(singer_counts):
        description, note = singer_field_descriptions.get(key, ("接口返回字段，含义待确认。", ""))
        sample = sample_singer.get(key)
        rows.append(
            [
                "$.singerlist[]",
                "歌手行",
                key,
                description,
                json_type(sample),
                singer_counts[key],
                sample,
                note,
            ]
        )

    tag_descriptions = {
        "area": "地区筛选项",
        "genre": "流派筛选项",
        "index": "首字母或索引筛选项",
        "sex": "性别筛选项",
    }
    for group, meaning in tag_descriptions.items():
        items = sample_page.get("tags", {}).get(group, [])
        sample = items[0] if items else {}
        for key in ("id", "name"):
            description = f"{meaning}{' ID' if key == 'id' else '名称'}。"
            rows.append(
                [
                    f"$.tags.{group}[]",
                    "筛选项",
                    key,
                    description,
                    json_type(sample.get(key) if isinstance(sample, dict) else ""),
                    tag_item_counts[f"tags.{group}[].{key}"],
                    sample.get(key) if isinstance(sample, dict) else "",
                    "用于理解请求参数，不是歌手行字段。",
                ]
            )
    return rows


def build_song_tab_rows(raw_dir: Path) -> list[list[Any]]:
    files = sorted(raw_dir.glob("*/*.json"))
    if not files:
        raise FileNotFoundError(f"No singer homepage song tab JSON files found: {raw_dir}")
    pages = []
    songs = []
    top_counts: Counter[str] = Counter()
    song_tab_counts: Counter[str] = Counter()
    song_counts: Counter[str] = Counter()
    nested_counts: dict[str, Counter[str]] = {}
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        pages.append(payload)
        top_counts.update(payload.keys())
        song_tab = payload.get("SongTab") if isinstance(payload.get("SongTab"), dict) else {}
        song_tab_counts.update(song_tab.keys())
        for song in song_tab.get("List") or []:
            songs.append(song)
            song_counts.update(song.keys())
            for key, value in song.items():
                if isinstance(value, dict):
                    nested_counts.setdefault(key, Counter()).update(value.keys())
                elif isinstance(value, list) and value and isinstance(value[0], dict):
                    nested_counts.setdefault(f"{key}[]", Counter()).update(value[0].keys())

    sample_page = pages[0]
    sample_song_tab = (
        sample_page.get("SongTab") if isinstance(sample_page.get("SongTab"), dict) else {}
    )
    sample_song = songs[0] if songs else {}
    header = ["JSON路径", "层级", "键名", "中文释义", "数据类型", "出现次数", "示例值", "备注"]
    rows: list[list[Any]] = [
        ["请求名称", "qqmusic.singer homepage song tab"],
        ["原始目录", raw_dir.as_posix()],
        ["分页文件数", len(files)],
        ["歌曲行数", len(songs)],
        ["生成时间", datetime.now().isoformat(timespec="seconds")],
        [],
        header,
    ]

    top_descriptions = {
        "SongTab": ("歌曲 Tab 数据对象。", "本轮主要使用的歌曲列表来源。"),
        "AlbumTab": ("专辑 Tab 数据对象。", "本轮不作为歌曲全集主来源。"),
        "ArtistWorksTab": ("艺人作品 Tab 数据对象。", "含义待确认。"),
        "CalendarTab": ("日历 Tab 数据对象。", "含义待确认。"),
        "DiscTab": ("唱片或碟片 Tab 数据对象。", "含义待确认。"),
        "HasMore": ("是否还有更多分页。", "用于分页续跑判断。"),
        "IntroductionTab": ("简介 Tab 数据对象。", "含义待确认。"),
        "MomentTab": ("动态或时刻 Tab 数据对象。", "含义待确认。"),
        "NeedShowTab": ("需要展示的 Tab 标记。", "含义待确认。"),
        "Order": ("排序字段或排序配置。", "含义待确认。"),
        "PersonalTab": ("个人信息 Tab 数据对象。", "含义待确认。"),
        "PutaoProductTab": ("葡萄产品 Tab 数据对象。", "含义待确认。"),
        "ShowTab": ("演出或展示 Tab 数据对象。", "含义待确认。"),
        "TabID": ("当前 Tab ID。", "请求结果元信息。"),
        "TabList": ("Tab 列表。", "请求结果元信息。"),
        "VideoTab": ("视频 Tab 数据对象。", "本轮不作为歌曲全集主来源。"),
    }
    for key in sorted(top_counts):
        description, note = top_descriptions.get(key, ("接口返回顶层字段，含义待确认。", ""))
        sample = sample_page.get(key)
        rows.append(
            [
                "$",
                "根对象",
                key,
                description,
                json_type(sample),
                top_counts[key],
                compact_sample(sample),
                note,
            ]
        )

    song_tab_descriptions = {
        "List": ("当前页歌曲列表。", "主要数据数组。"),
        "SearchText": ("搜索或筛选文本。", "当前样本通常为空。"),
        "IsShowQLIcon": ("是否展示 QL 图标。", "界面展示相关。"),
        "SongTagInfoList": ("歌曲标签信息列表。", "含义待确认。"),
    }
    for key in sorted(song_tab_counts):
        description, note = song_tab_descriptions.get(key, ("SongTab 内字段，含义待确认。", ""))
        sample = sample_song_tab.get(key)
        rows.append(
            [
                "$.SongTab",
                "歌曲Tab",
                key,
                description,
                json_type(sample),
                song_tab_counts[key],
                compact_sample(sample),
                note,
            ]
        )

    song_descriptions = {
        "id": ("QQ 音乐歌曲数字 ID。", "歌曲身份键候选。"),
        "mid": ("QQ 音乐歌曲 MID。", "歌曲身份键候选，后续请求常用。"),
        "name": ("歌曲原始名称。", "后续去重优先使用的歌名字段候选。"),
        "title": ("歌曲标题。", "通常与 name 相同，但不应默认等同。"),
        "subtitle": ("歌曲副标题。", "可用于识别版本信息。"),
        "singer": ("歌曲演唱者列表。", "嵌套数组，记录参与演唱者。"),
        "album": ("歌曲所属专辑对象。", "嵌套对象，含专辑 id/mid/name 等。"),
        "mv": ("MV 信息对象。", "本轮不作为主字段。"),
        "interval": ("歌曲时长，单位通常为秒。", "可入库为 duration_seconds。"),
        "isonly": ("接口返回的独占或限制标记。", "含义待确认。"),
        "language": ("语言编码。", "需要后续映射。"),
        "genre": ("流派编码。", "需要后续映射。"),
        "index_cd": ("CD 内序号。", "专辑曲序相关。"),
        "index_album": ("专辑内序号。", "专辑曲序相关。"),
        "time_public": ("歌曲发行时间。", "字符串日期。"),
        "status": ("歌曲状态码。", "含义待确认。"),
        "fnote": ("接口返回的 fnote 字段。", "含义待确认。"),
        "file": ("音频文件规格信息对象。", "只用于元数据观察，不采集音频。"),
        "pay": ("付费状态信息对象。", "本项目不做播放下载，只保留元数据理解。"),
        "action": ("可操作状态信息对象。", "平台 UI/权限相关。"),
        "ksong": ("K 歌相关对象。", "本轮不作为主字段。"),
        "volume": ("音量分析信息对象。", "本轮不作为主字段。"),
        "label": ("标签编码。", "含义待确认。"),
        "url": ("URL 字段。", "当前样本通常为空；不用于播放下载。"),
        "bpm": ("BPM 字段。", "当前样本多为 0。"),
        "version": ("版本字段。", "含义待确认。"),
        "trace": ("trace 字段。", "含义待确认。"),
        "data_type": ("数据类型编码。", "含义待确认。"),
        "modify_stamp": ("修改时间戳或版本戳。", "含义待确认。"),
        "pingpong": ("pingpong 字段。", "含义待确认。"),
        "aid": ("aid 字段。", "含义待确认。"),
        "ppurl": ("ppurl 字段。", "含义待确认。"),
        "tid": ("tid 字段。", "含义待确认。"),
        "ov": ("ov 字段。", "含义待确认。"),
        "sa": ("sa 字段。", "含义待确认。"),
        "es": ("es 字段。", "含义待确认。"),
        "vs": ("vs 数组字段。", "含义待确认。"),
        "vi": ("vi 数组字段。", "含义待确认。"),
        "ktag": ("ktag 字段。", "含义待确认。"),
        "vf": ("vf 数组字段。", "含义待确认。"),
        "va": ("va 数组字段。", "含义待确认。"),
    }
    for key in sorted(song_counts):
        description, note = song_descriptions.get(key, ("歌曲行字段，含义待确认。", ""))
        sample = sample_song.get(key)
        rows.append(
            [
                "$.SongTab.List[]",
                "歌曲行",
                key,
                description,
                json_type(sample),
                song_counts[key],
                compact_sample(sample),
                note,
            ]
        )

    nested_descriptions = {
        "album": {
            "id": "QQ 音乐专辑数字 ID。",
            "mid": "QQ 音乐专辑 MID。",
            "name": "专辑名称。",
            "title": "专辑标题。",
            "subtitle": "专辑副标题。",
            "time_public": "专辑发行时间。",
            "pmid": "专辑 pmid。",
        },
        "singer[]": {
            "id": "演唱者 QQ 音乐数字 ID。",
            "mid": "演唱者 QQ 音乐 MID。",
            "name": "演唱者名称。",
            "title": "演唱者标题字段。",
            "type": "演唱者类型编码。",
            "uin": "演唱者 uin 字段。",
            "pmid": "演唱者 pmid。",
        },
        "mv": {
            "id": "MV 数字 ID。",
            "vid": "MV vid。",
            "name": "MV 名称。",
            "title": "MV 标题。",
            "vt": "MV 类型或状态字段。",
        },
        "file": {
            "media_mid": "媒体文件 MID。",
            "size_128mp3": "128kbps MP3 文件大小。",
            "size_320mp3": "320kbps MP3 文件大小。",
            "size_flac": "FLAC 文件大小。",
            "size_try": "试听文件大小。",
            "try_begin": "试听开始位置。",
            "try_end": "试听结束位置。",
            "url": "文件 URL 字段。",
        },
        "pay": {
            "pay_month": "包月付费标记。",
            "price_track": "单曲价格。",
            "price_album": "专辑价格。",
            "pay_play": "播放付费标记。",
            "pay_down": "下载付费标记。",
            "pay_status": "付费状态。",
            "time_free": "限免时间字段。",
        },
        "action": {
            "switch": "操作开关字段。",
            "msgid": "消息 ID。",
            "alert": "提醒标记。",
            "icons": "图标标记。",
            "msgshare": "分享消息标记。",
            "msgfav": "收藏消息标记。",
            "msgdown": "下载消息标记。",
            "msgpay": "付费消息标记。",
            "switch2": "第二操作开关字段。",
            "icon2": "第二图标字段。",
        },
        "ksong": {
            "id": "K 歌数字 ID。",
            "mid": "K 歌 MID。",
        },
        "volume": {
            "gain": "音量增益。",
            "peak": "峰值。",
            "lra": "响度范围。",
        },
    }
    sample_nested = {}
    for key, value in sample_song.items():
        if isinstance(value, dict):
            sample_nested[key] = value
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            sample_nested[f"{key}[]"] = value[0]
    for parent in sorted(nested_counts):
        for key in sorted(nested_counts[parent]):
            sample_parent = sample_nested.get(parent, {})
            sample = sample_parent.get(key) if isinstance(sample_parent, dict) else ""
            description = nested_descriptions.get(parent, {}).get(key, "嵌套字段，含义待确认。")
            rows.append(
                [
                    f"$.SongTab.List[].{parent}",
                    "嵌套字段",
                    key,
                    description,
                    json_type(sample),
                    nested_counts[parent][key],
                    compact_sample(sample),
                    "嵌套字段先记录结构，是否入库后续再定。",
                ]
            )
    return rows


def build_song_album_detail_rows(raw_dir: Path) -> list[list[Any]]:
    files = sorted(raw_dir.glob("*.json"))
    if not files:
        raise FileNotFoundError(f"No song-derived album detail JSON files found: {raw_dir}")
    payloads = []
    top_counts: Counter[str] = Counter()
    basic_info_counts: Counter[str] = Counter()
    company_counts: Counter[str] = Counter()
    singer_counts: Counter[str] = Counter()
    singer_item_counts: Counter[str] = Counter()
    legacy_album_counts: Counter[str] = Counter()
    legacy_singer_item_counts: Counter[str] = Counter()
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        payloads.append(payload)
        top_counts.update(payload.keys())
        basic_info = payload.get("basicInfo") if isinstance(payload.get("basicInfo"), dict) else {}
        basic_info_counts.update(basic_info.keys())
        company = payload.get("company") if isinstance(payload.get("company"), dict) else {}
        company_counts.update(company.keys())
        singer = payload.get("singer") if isinstance(payload.get("singer"), dict) else {}
        singer_counts.update(singer.keys())
        for item in singer.get("singerList") or []:
            if isinstance(item, dict):
                singer_item_counts.update(item.keys())
        legacy_album = payload.get("album") if isinstance(payload.get("album"), dict) else {}
        legacy_album_counts.update(legacy_album.keys())
        for item in payload.get("singers") or []:
            if isinstance(item, dict):
                legacy_singer_item_counts.update(item.keys())

    sample_page = payloads[0]
    sample_basic_info = (
        sample_page.get("basicInfo") if isinstance(sample_page.get("basicInfo"), dict) else {}
    )
    sample_company = (
        sample_page.get("company") if isinstance(sample_page.get("company"), dict) else {}
    )
    sample_singer = sample_page.get("singer") if isinstance(sample_page.get("singer"), dict) else {}
    sample_singer_item = (
        (sample_singer.get("singerList") or [{}])[0] if isinstance(sample_singer, dict) else {}
    )
    sample_legacy_album = (
        sample_page.get("album") if isinstance(sample_page.get("album"), dict) else {}
    )
    sample_legacy_singer_item = (
        (sample_page.get("singers") or [{}])[0]
        if isinstance(sample_page.get("singers"), list)
        else {}
    )
    header = ["JSON路径", "层级", "键名", "中文释义", "数据类型", "出现次数", "示例值", "备注"]
    rows: list[list[Any]] = [
        ["请求名称", "qqmusic.album.get_detail"],
        ["原始目录", raw_dir.as_posix()],
        ["专辑详情文件数", len(files)],
        [
            "来源说明",
            "先请求歌手主页歌曲 Tab，再按歌曲 album.mid 或非 0 album.id 去重请求专辑详情。",
        ],
        ["生成时间", datetime.now().isoformat(timespec="seconds")],
        [],
        header,
    ]

    top_descriptions = {
        "basicInfo": ("专辑基础信息对象。", "本轮专辑入库字段主要从这里取。"),
        "company": ("唱片公司或版权方信息对象。", "当前不作为专辑入库必需字段。"),
        "singer": (
            "专辑署名歌手对象，内部包含 singerList。",
            "可用于派生 singerName 或后续专辑-歌手关系。",
        ),
        "album": (
            "兼容口径下的专辑基础信息对象。",
            "如未来接口返回旧口径，可作为 basicInfo 的结构参照。",
        ),
        "singers": (
            "兼容口径下的署名歌手列表。",
            "如未来接口返回旧口径，可作为 singer.singerList 的结构参照。",
        ),
    }
    for key in sorted(top_counts):
        description, note = top_descriptions.get(key, ("接口返回顶层字段，含义待确认。", ""))
        sample = sample_page.get(key)
        rows.append(
            [
                "$",
                "根对象",
                key,
                description,
                json_type(sample),
                top_counts[key],
                compact_sample(sample),
                note,
            ]
        )

    basic_info_descriptions = {
        "albumMid": ("QQ 音乐专辑 MID。", "后续专辑表主键候选。"),
        "albumName": ("专辑名称。", "可映射到专辑表 name。"),
        "tranName": ("专辑译名或英文名。", "可用于辅助展示。"),
        "publishDate": ("专辑发行日期。", "字符串日期。"),
        "albumType": ("专辑类型文本。", "可映射到专辑表 type。"),
        "type": ("专辑类型编码或补充类型字段。", "不等同于 albumType 文本，入库前需确认取舍。"),
        "albumID": ("QQ 音乐专辑数字 ID。", "可映射到专辑表 id 并设置唯一约束。"),
        "pmid": ("专辑 pmid。", "平台图片或版本相关字段，含义待确认。"),
        "desc": ("专辑简介。", "当前不作为入库必需字段。"),
        "genre": ("专辑流派文本或编码。", "当前不作为入库必需字段。"),
        "language": ("专辑语言。", "当前不作为入库必需字段。"),
        "recordNum": ("专辑曲目数量或记录数。", "当前不作为入库必需字段。"),
        "modifyTime": ("平台侧修改时间。", "当前不作为入库必需字段。"),
    }
    for key in sorted(basic_info_counts):
        description, note = basic_info_descriptions.get(key, ("专辑基础信息字段，含义待确认。", ""))
        sample = sample_basic_info.get(key)
        rows.append(
            [
                "$.basicInfo",
                "专辑基础信息",
                key,
                description,
                json_type(sample),
                basic_info_counts[key],
                compact_sample(sample),
                note,
            ]
        )

    company_descriptions = {
        "ID": "唱片公司或版权方数字 ID。",
        "id": "唱片公司或版权方数字 ID。",
        "name": "唱片公司或版权方名称。",
        "headPic": "公司头像或图片 URL。",
        "isShow": "是否展示公司信息。",
        "is_show": "是否展示公司信息。",
        "brief": "公司简介。",
    }
    for key in sorted(company_counts):
        sample = sample_company.get(key)
        rows.append(
            [
                "$.company",
                "公司信息",
                key,
                company_descriptions.get(key, "公司信息字段，含义待确认。"),
                json_type(sample),
                company_counts[key],
                compact_sample(sample),
                "当前不作为专辑入库必需字段。",
            ]
        )

    singer_descriptions = {
        "singerList": (
            "专辑署名歌手列表。",
            "详情接口没有旧列表中的单个 singerName 字段；需要时可由此派生署名文本。",
        ),
    }
    for key in sorted(singer_counts):
        description, note = singer_descriptions.get(key, ("专辑署名歌手对象字段，含义待确认。", ""))
        sample = sample_singer.get(key)
        rows.append(
            [
                "$.singer",
                "署名歌手对象",
                key,
                description,
                json_type(sample),
                singer_counts[key],
                compact_sample(sample),
                note,
            ]
        )

    singer_item_descriptions = {
        "id": "署名歌手 QQ 音乐数字 ID。",
        "mid": "署名歌手 QQ 音乐 MID。",
        "name": "署名歌手名称。",
        "title": "署名歌手标题字段。",
        "type": "署名歌手类型编码。",
        "uin": "署名歌手 uin 字段。",
        "pmid": "署名歌手 pmid。",
    }
    for key in sorted(singer_item_counts):
        sample = sample_singer_item.get(key) if isinstance(sample_singer_item, dict) else ""
        rows.append(
            [
                "$.singer.singerList[]",
                "署名歌手行",
                key,
                singer_item_descriptions.get(key, "署名歌手行字段，含义待确认。"),
                json_type(sample),
                singer_item_counts[key],
                compact_sample(sample),
                "可用于后续构造 singerName 或专辑-歌手关系。",
            ]
        )

    for key in sorted(legacy_album_counts):
        sample = sample_legacy_album.get(key)
        rows.append(
            [
                "$.album",
                "兼容专辑信息",
                key,
                "兼容口径专辑字段，含义待确认。",
                json_type(sample),
                legacy_album_counts[key],
                compact_sample(sample),
                "当前样本如未出现则计数为 0；保留用于识别接口口径变化。",
            ]
        )
    for key in sorted(legacy_singer_item_counts):
        sample = (
            sample_legacy_singer_item.get(key)
            if isinstance(sample_legacy_singer_item, dict)
            else ""
        )
        rows.append(
            [
                "$.singers[]",
                "兼容署名歌手行",
                key,
                "兼容口径署名歌手字段，含义待确认。",
                json_type(sample),
                legacy_singer_item_counts[key],
                compact_sample(sample),
                "当前样本如未出现则计数为 0；保留用于识别接口口径变化。",
            ]
        )
    return rows


def compact_sample(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False)
        return text[:300] + ("..." if len(text) > 300 else "")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write an XLSX dictionary for collected request JSON keys."
    )
    parser.add_argument("--singer-list-dir", type=Path, default=DEFAULT_SINGER_LIST_DIR)
    parser.add_argument("--song-tab-dir", type=Path, default=DEFAULT_SONG_TAB_DIR)
    parser.add_argument("--song-album-detail-dir", type=Path, default=DEFAULT_SONG_ALBUM_DETAIL_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def _main() -> None:
    args = parse_args()
    sheets = [
        ("01_singer_list_index", build_singer_list_rows(args.singer_list_dir)),
        ("02_song_album_detail", build_song_album_detail_rows(args.song_album_detail_dir)),
        ("03_singer_song_tab", build_song_tab_rows(args.song_tab_dir)),
    ]
    write_xlsx(args.output, sheets)
    print(args.output.as_posix())


def main() -> None:
    run_with_log(Path(__file__).stem, _main)


if __name__ == "__main__":
    main()
