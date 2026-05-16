from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from music_metadata_graph.pipelines.defaults import DEFAULT_DB_PATH, DEFAULT_MVP_DB_PATH


DEFAULT_OUTPUT_DIR = Path("data/visualization")
DEFAULT_MVP_OUTPUT_DIR = Path("data/visualization_mvp")
DEFAULT_VENDOR_PATH = Path(__file__).resolve().parent / "vendor" / "force-graph.min.js"
ROLE_LABELS = ("作词", "作曲")
TARGET_FILTER_LIMIT = 10


@dataclass(frozen=True)
class BuildConfig:
    db_path: Path
    output_dir: Path
    title: str
    vendor_path: Path


def connect_database(path: Path) -> sqlite3.Connection:
    if not path.exists():
        raise FileNotFoundError(f"SQLite database does not exist: {path}")
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def fetch_summary(connection: sqlite3.Connection) -> dict[str, Any]:
    role_counts = {
        row["role"]: row["count"]
        for row in connection.execute(
            """
            SELECT role, COUNT(*) AS count
            FROM song_credit_artists
            GROUP BY role
            ORDER BY role
            """
        )
    }
    return {
        "artists": scalar_count(connection, "artists"),
        "songs": scalar_count(connection, "songs"),
        "song_singers": scalar_count(connection, "song_singers"),
        "song_credit_artists": scalar_count(connection, "song_credit_artists"),
        "roles": role_counts,
    }


def scalar_count(connection: sqlite3.Connection, table: str) -> int:
    return int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def fetch_song_rows(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(
        connection.execute(
            """
            SELECT
                s.mid AS song_mid,
                s.id AS song_id,
                s.name AS song_name,
                s.title AS song_title,
                s.language AS song_language,
                a.mid AS album_mid,
                a.name AS album_name,
                a.albumType AS album_type,
                a.publishDate AS album_publish_date
            FROM songs s
            JOIN albums a ON a.mid = s.album_mid
            ORDER BY s.name, s.id, s.mid
            """
        )
    )


def fetch_people_by_song(connection: sqlite3.Connection, table: str, role: str | None = None) -> dict[str, list[dict[str, str]]]:
    if table == "song_singers":
        rows = connection.execute(
            """
            SELECT
                ss.song_mid,
                ss.singer_order AS person_order,
                ar.mid,
                ar.name,
                ar.icon
            FROM song_singers ss
            JOIN artists ar ON ar.mid = ss.singer_mid
            ORDER BY ss.song_mid, ss.singer_order
            """
        )
    elif table == "song_credit_artists" and role:
        rows = connection.execute(
            """
            SELECT
                ca.song_mid,
                ca.artist_order AS person_order,
                ar.mid,
                ar.name,
                ar.icon
            FROM song_credit_artists ca
            JOIN artists ar ON ar.mid = ca.artist_mid
            WHERE ca.role = ?
            ORDER BY ca.song_mid, ca.artist_order
            """,
            (role,),
        )
    else:
        raise ValueError(f"Unsupported people query: {table}, role={role}")

    people: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        people[row["song_mid"]].append(
            {
                "mid": row["mid"],
                "name": row["name"],
                "icon": row["icon"] or "",
            }
        )
    return people


def artist_node(person: dict[str, str], *, is_target: bool = False) -> dict[str, Any]:
    return {
        "id": f"artist:{person['mid']}",
        "mid": person["mid"],
        "name": person["name"],
        "icon": normalize_icon_url(person.get("icon", "")),
        "type": "artist",
        "is_target": is_target,
    }


def normalize_icon_url(value: str) -> str:
    url = str(value or "").strip()
    if url.startswith("http://"):
        return "https://" + url.removeprefix("http://")
    return url


def song_payload(row: sqlite3.Row, singers: list[dict[str, str]], lyricists: list[dict[str, str]], composers: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "mid": row["song_mid"],
        "id": row["song_id"],
        "name": row["song_name"],
        "title": row["song_title"],
        "language": row["song_language"],
        "album_mid": row["album_mid"],
        "album": row["album_name"],
        "album_type": row["album_type"],
        "album_publish_date": row["album_publish_date"],
        "singers": [{"mid": item["mid"], "name": item["name"]} for item in singers],
        "lyricists": [{"mid": item["mid"], "name": item["name"]} for item in lyricists],
        "composers": [{"mid": item["mid"], "name": item["name"]} for item in composers],
    }


def build_graph_data(connection: sqlite3.Connection) -> dict[str, Any]:
    songs = fetch_song_rows(connection)
    singers_by_song = fetch_people_by_song(connection, "song_singers")
    lyricists_by_song = fetch_people_by_song(connection, "song_credit_artists", "作词")
    composers_by_song = fetch_people_by_song(connection, "song_credit_artists", "作曲")

    nodes: dict[str, dict[str, Any]] = {}
    edge_songs: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    song_items: list[dict[str, Any]] = []

    for row in songs:
        song_mid = row["song_mid"]
        singers = singers_by_song.get(song_mid, [])
        lyricists = lyricists_by_song.get(song_mid, [])
        composers = composers_by_song.get(song_mid, [])
        payload = song_payload(row, singers, lyricists, composers)
        song_items.append(payload)

        for singer in singers:
            node_id = f"artist:{singer['mid']}"
            current = nodes.get(node_id) or artist_node(singer, is_target=True)
            current["is_target"] = True
            current["sung_song_count"] = int(current.get("sung_song_count") or 0) + 1
            nodes[node_id] = current

        for role, contributors in (("作词", lyricists), ("作曲", composers)):
            for contributor in contributors:
                source = f"artist:{contributor['mid']}"
                nodes.setdefault(source, artist_node(contributor))
                nodes[source]["credit_song_count"] = int(nodes[source].get("credit_song_count") or 0) + 1
                role_count_key = "lyricist_song_count" if role == "作词" else "composer_song_count"
                nodes[source][role_count_key] = int(nodes[source].get(role_count_key) or 0) + 1
                for singer in singers:
                    target = f"artist:{singer['mid']}"
                    if source == target:
                        continue
                    edge_songs[(source, target, role)].append(
                        {
                            "mid": payload["mid"],
                            "id": payload["id"],
                            "name": payload["name"],
                            "album": payload["album"],
                            "album_type": payload["album_type"],
                            "target": singer["name"],
                            "target_mid": singer["mid"],
                            "role": role,
                        }
                    )

    edges = [
        {
            "id": f"{source}->{target}:{role}",
            "source": source,
            "target": target,
            "role": role,
            "song_count": len(items),
            "songs": sorted(items, key=lambda item: (item["name"], item["id"], item["mid"])),
        }
        for (source, target, role), items in edge_songs.items()
    ]

    used_node_ids = set()
    for edge in edges:
        used_node_ids.add(edge["source"])
        used_node_ids.add(edge["target"])

    target_filter_items = sorted(
        (
            {
                "id": node["id"],
                "mid": node["mid"],
                "name": node["name"],
                "icon": node.get("icon", ""),
                "song_count": int(node.get("sung_song_count") or 0),
            }
            for node in nodes.values()
            if node.get("is_target")
        ),
        key=lambda item: (-item["song_count"], item["name"]),
    )[:TARGET_FILTER_LIMIT]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": fetch_summary(connection),
        "nodes": sorted((node for node_id, node in nodes.items() if node_id in used_node_ids), key=lambda item: item["name"]),
        "edges": sorted(edges, key=lambda item: (-item["song_count"], item["role"], item["source"], item["target"])),
        "songs": song_items,
        "targets": target_filter_items,
        "roles": list(ROLE_LABELS),
        "relationship_direction": "作词/作曲人 -> 演唱者",
    }


def read_vendor_script(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")

    fallback = Path("archive/legacy_pipeline_2026-05-12/web/vendor/force-graph.min.js")
    if fallback.exists():
        return fallback.read_text(encoding="utf-8")

    raise FileNotFoundError(f"force-graph runtime not found: {path}")


def html_document(
    title: str,
    graph_data: dict[str, Any],
    vendor_script: str,
    *,
    css: str | None = None,
    js: str | None = None,
) -> str:
    css = CSS if css is None else css
    js = JS if js is None else js
    data_json = safe_script_json(graph_data)
    vendor_json = safe_script_json(vendor_script)
    title_json = json.dumps(title, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape_html(title)}</title>
  <style>{css}</style>
</head>
<body>
  <header class="topbar">
    <div>
      <h1>{escape_html(title)}</h1>
      <p id="dataset-scope">加载图谱数据...</p>
    </div>
    <div class="toolbar">
      <div class="target-filter">
        <span class="control-label">目标歌手</span>
        <div class="target-select-shell">
          <select id="target-visual-select" class="target-visual-select" aria-hidden="true" tabindex="-1">
            <option>全部目标歌手</option>
          </select>
          <button id="target-dropdown-toggle" class="target-dropdown-toggle" type="button" aria-haspopup="true" aria-expanded="false">
            <span id="target-dropdown-label" class="target-dropdown-label">全部目标歌手</span>
          </button>
        </div>
        <div id="target-dropdown-menu" class="target-dropdown-menu" hidden>
          <input id="target-filter-search" class="target-filter-search" type="search" placeholder="搜索目标歌手" />
          <div class="target-actions">
            <button id="target-select-all" type="button">全选</button>
            <button id="target-invert" type="button">反选</button>
          </div>
          <div id="target-checkboxes" class="target-checkboxes"></div>
        </div>
      </div>
      <label class="switch-control">
        作词/作曲分开
        <input id="role-split-toggle" type="checkbox" checked />
        <span class="switch-track" aria-hidden="true"></span>
      </label>
      <label class="switch-control">
        显示名字
        <input id="label-toggle" type="checkbox" />
        <span class="switch-track" aria-hidden="true"></span>
      </label>
      <label class="switch-control">
        粒子效果
        <input id="particle-toggle" type="checkbox" />
        <span class="switch-track" aria-hidden="true"></span>
      </label>
      <label>最小歌曲数
        <input id="min-count" type="number" min="1" value="1" />
      </label>
      <input id="search-input" type="search" placeholder="搜索音乐人或歌曲" />
    </div>
  </header>

  <main class="layout">
    <section class="workspace">
      <div class="graph-panel">
        <div class="panel-head">
          <div class="graph-heading">
            <h2 id="graph-title">图谱</h2>
            <p id="graph-note"></p>
          </div>
          <div id="legend" class="legend"></div>
        </div>
        <div id="graph" role="img" aria-label="音乐人合作关系图谱"></div>
      </div>
      <aside class="detail-panel">
        <h2>详情</h2>
        <div id="detail-content" class="detail-content"></div>
      </aside>
    </section>

    <section class="data-section">
      <div class="tabs">
        <div class="tab-buttons">
          <button class="tab active" data-tab="songs" type="button">歌曲明细</button>
          <button class="tab" data-tab="edges" type="button">关系明细</button>
        </div>
        <input id="table-search-input" type="search" placeholder="搜索当前明细" />
      </div>
      <div id="table-content"></div>
    </section>
  </main>

  <script>
    const vendorScript = {vendor_json};
    (0, eval)(vendorScript);
    window.GRAPH_TITLE = {title_json};
    window.GRAPH_DATA = {data_json};
  </script>
  <script>{js}</script>
</body>
</html>
"""


def escape_html(value: Any) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def safe_script_json(value: Any) -> str:
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .replace("</", "<\\/")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def write_visualization(config: BuildConfig) -> dict[str, Any]:
    with connect_database(config.db_path) as connection:
        graph_data = build_graph_data(connection)

    vendor_script = read_vendor_script(config.vendor_path)
    config.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = config.output_dir / "index.html"
    output_path.write_text(html_document(config.title, graph_data, vendor_script), encoding="utf-8", newline="\n")
    return {
        "output": output_path.as_posix(),
        "db": config.db_path.as_posix(),
        "nodes": len(graph_data["nodes"]),
        "edges": len(graph_data["edges"]),
        "songs": len(graph_data["songs"]),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a static musician relationship graph HTML from SQLite.")
    parser.add_argument("--db", type=Path, default=None, help="SQLite database path.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Directory for index.html.")
    parser.add_argument("--title", default="音乐人合作关系图谱", help="HTML page title.")
    parser.add_argument("--vendor", type=Path, default=DEFAULT_VENDOR_PATH, help="Local force-graph runtime path.")
    parser.add_argument("--mvp", action="store_true", help="Use the MVP database and MVP visualization output directory.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_path = args.db or (DEFAULT_MVP_DB_PATH if args.mvp else DEFAULT_DB_PATH)
    output_dir = args.output_dir or (DEFAULT_MVP_OUTPUT_DIR if args.mvp else DEFAULT_OUTPUT_DIR)
    result = write_visualization(
        BuildConfig(
            db_path=db_path,
            output_dir=output_dir,
            title=args.title,
            vendor_path=args.vendor,
        )
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


CSS = r"""
:root {
  color-scheme: light;
  font-family: "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
  background: #f5f7fa;
  color: #172033;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
}

.topbar {
  display: grid;
  grid-template-columns: minmax(280px, 1fr) minmax(0, auto);
  gap: 14px;
  align-items: end;
  padding: 16px 22px 8px;
  background: #ffffff;
  border-bottom: 1px solid #d8dee8;
}

h1,
h2,
p {
  margin: 0;
}

h1 {
  font-size: 23px;
  font-weight: 700;
}

h2 {
  font-size: 16px;
}

.topbar p,
.panel-head p,
.muted {
  color: #667085;
  font-size: 13px;
}

.toolbar {
  display: flex;
  align-items: center;
  align-self: end;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 10px;
}

label {
  display: flex;
  align-items: center;
  gap: 7px;
  min-width: 0;
  font-size: 12px;
  color: #475467;
  white-space: nowrap;
}

.target-filter {
  position: relative;
  display: flex;
  align-items: center;
  gap: 7px;
  min-width: 0;
  font-size: 12px;
  color: #475467;
  white-space: nowrap;
}

.control-label {
  color: #475467;
}

.target-select-shell {
  position: relative;
  width: 168px;
}

.target-visual-select {
  width: 100%;
  pointer-events: none;
}

.target-dropdown-toggle {
  position: absolute;
  inset: 0;
  width: 100%;
  min-height: 100%;
  padding: 0;
  border: 0;
  background: transparent;
  color: transparent;
  cursor: pointer;
}

.target-dropdown-label {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}

.target-dropdown-menu {
  position: absolute;
  z-index: 20;
  top: calc(100% + 4px);
  left: 0;
  width: 190px;
  padding: 7px;
  border: 1px solid #c7ced9;
  border-radius: 5px;
  background: #ffffff;
  box-shadow: 0 12px 28px rgba(16, 24, 40, 0.14);
}

.target-filter-search {
  width: 100%;
  margin-bottom: 6px;
}

.target-actions {
  display: flex;
  gap: 6px;
}

.target-actions button {
  min-height: 24px;
  padding: 2px 8px;
  cursor: pointer;
}

.target-checkboxes {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 4px;
  max-height: 210px;
  overflow: auto;
  margin-top: 8px;
}

.target-option {
  display: flex;
  align-items: center;
  gap: 5px;
  min-height: 22px;
  color: #172033;
  white-space: nowrap;
}

.target-option input {
  min-height: 0;
  width: 14px;
  height: 14px;
  margin: 0;
}

.target-empty {
  padding: 4px 0;
  color: #667085;
}

select,
input,
button {
  min-height: 28px;
  border: 1px solid #c7ced9;
  border-radius: 5px;
  background: #ffffff;
  color: #172033;
  font: inherit;
  line-height: 1.2;
}

select,
input {
  padding: 4px 8px;
}

#min-count {
  width: 62px;
}

#search-input {
  width: 190px;
}

.switch-control input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.switch-track {
  position: relative;
  display: inline-flex;
  width: 34px;
  height: 18px;
  flex: 0 0 auto;
  border: 1px solid #c7ced9;
  border-radius: 999px;
  background: #f2f4f7;
  cursor: pointer;
}

.switch-track::after {
  content: "";
  position: absolute;
  top: 2px;
  left: 2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.25);
  transition: transform 140ms ease;
}

.switch-control input:checked + .switch-track {
  border-color: #1570ef;
  background: #1570ef;
}

.switch-control input:checked + .switch-track::after {
  transform: translateX(16px);
}

.layout {
  padding: 14px;
}

.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 330px;
  gap: 14px;
  align-items: stretch;
}

.graph-panel,
.detail-panel,
.data-section {
  background: #ffffff;
  border: 1px solid #d8dee8;
  border-radius: 8px;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  border-bottom: 1px solid #e6ebf2;
}

.graph-heading {
  display: flex;
  align-items: baseline;
  gap: 8px;
  min-width: 0;
}

.graph-heading h2 {
  flex: 0 0 auto;
}

.legend {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
  font-size: 12px;
  color: #475467;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.legend-swatch {
  width: 18px;
  height: 3px;
  border-radius: 99px;
}

#graph {
  min-height: 420px;
}

.detail-panel {
  position: sticky;
  top: 14px;
  padding: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.detail-panel h2 {
  flex: 0 0 auto;
  margin-bottom: 10px;
}

.detail-content {
  min-height: 0;
  overflow: auto;
  padding-right: 2px;
}

.detail-card {
  padding: 10px;
  margin-bottom: 8px;
  border: 1px solid #e6ebf2;
  border-radius: 6px;
  background: #fbfcfe;
}

.detail-card strong {
  display: block;
  margin-bottom: 3px;
}

.data-section {
  margin-top: 14px;
  overflow: hidden;
}

.tabs {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-bottom: 1px solid #e6ebf2;
}

.tab-buttons {
  display: flex;
  gap: 6px;
}

.tab {
  padding: 5px 10px;
  cursor: pointer;
}

.tab.active {
  border-color: #1570ef;
  background: #eff6ff;
  color: #175cd3;
}

#table-search-input {
  width: min(260px, 42vw);
}

#table-content {
  height: 420px;
  overflow: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

th,
td {
  padding: 8px 10px;
  border-bottom: 1px solid #edf1f6;
  text-align: left;
  vertical-align: top;
}

th {
  position: sticky;
  top: 0;
  z-index: 1;
  background: #f8fafc;
  color: #475467;
  font-weight: 600;
}

td {
  max-width: 520px;
}

@media (max-width: 980px) {
  .topbar,
  .workspace {
    grid-template-columns: 1fr;
  }

  .toolbar {
    justify-content: flex-start;
  }

  label,
  .target-filter {
    align-items: stretch;
  }

  .detail-panel {
    position: static;
  }
}
"""


JS = r"""
const rawData = window.GRAPH_DATA;
const state = {
  selectedTargets: new Set(),
  targetMenuOpen: false,
  targetFilterSearch: "",
  roleDisplay: "split",
  showLabels: false,
  particlesEnabled: false,
  minCount: 1,
  search: "",
  tableSearch: "",
  selected: null,
  selectedNodeIds: new Set(),
  activeTab: "songs",
};

let graphInstance = null;
let graphResizeObserver = null;
let graphDataKey = "";
let currentGraph = { nodes: [], edges: [] };
let currentEdgeWeightScale = { min: 1, max: 1 };
const highlightNodes = new Set();
const highlightLinks = new Set();
const imageCache = new Map();

const $ = (id) => document.getElementById(id);

function formatNumber(value) {
  return Number(value || 0).toLocaleString("zh-CN");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function personNames(values) {
  return (values || []).map((item) => item.name || item).filter(Boolean).join(" / ");
}

function targetItems() {
  return [...(rawData.targets || [])];
}

function targetIds() {
  return targetItems().map((item) => item.id);
}

function selectedTargetItems() {
  return targetItems().filter((item) => state.selectedTargets.has(item.id));
}

function allTargetsSelected() {
  const ids = targetIds();
  return ids.length > 0 && ids.every((id) => state.selectedTargets.has(id));
}

function currentScopeLabel() {
  const selected = selectedTargetItems();
  if (!selected.length) return "未选择目标歌手";
  if (allTargetsSelected()) return `全部 ${formatNumber(targetItems().length)} 位目标歌手`;
  if (selected.length <= 3) return selected.map((item) => item.name).join("、");
  return `${selected.slice(0, 3).map((item) => item.name).join("、")} 等 ${formatNumber(selected.length)} 位目标歌手`;
}

function nodeById() {
  return new Map(rawData.nodes.map((node) => [node.id, node]));
}

function nodeName(idOrNode) {
  const id = typeof idOrNode === "object" ? idOrNode.id : idOrNode;
  return nodeById().get(id)?.name || id;
}

function updateEdgeWeightScale(edges) {
  const counts = edges.map((edge) => Number(edge.song_count || 0)).filter((count) => count > 0);
  currentEdgeWeightScale = counts.length
    ? { min: Math.min(...counts), max: Math.max(...counts) }
    : { min: 1, max: 1 };
}

function edgeWeightRatio(edge) {
  const min = currentEdgeWeightScale.min;
  const max = currentEdgeWeightScale.max;
  if (max <= min) return 0;
  const count = Number(edge.song_count || min);
  return Math.max(0, Math.min(1, (count - min) / (max - min)));
}

function edgeWidth(edge) {
  return 1 + edgeWeightRatio(edge) * 4;
}

function edgeAlpha(edge) {
  if (isHighlightedLink(edge)) return 1;
  const alpha = 0.2 + edgeWeightRatio(edge) * 0.8;
  return hasActiveHighlight() ? alpha * 0.5 : alpha;
}

function edgeColor(edge) {
  const alpha = edgeAlpha(edge).toFixed(3);
  if (edge.role === "作词") return `rgba(31, 120, 180, ${alpha})`;
  if (edge.role === "作曲") return `rgba(217, 95, 2, ${alpha})`;
  return `rgba(20, 132, 117, ${alpha})`;
}

function edgeParticleColor(edge) {
  if (edge.role === "作词") return "rgba(31, 120, 180, 0.9)";
  if (edge.role === "作曲") return "rgba(217, 95, 2, 0.9)";
  return "rgba(20, 132, 117, 0.9)";
}

function baseEdges() {
  return rawData.edges.filter((edge) => {
    if (!state.selectedTargets.has(edge.target)) return false;
    return edge.song_count >= state.minCount;
  });
}

function undirectedPair(edge) {
  return edgePairId(edge);
}

function edgePairId(edge) {
  return [nodeId(edge.source), nodeId(edge.target)].sort().join("--");
}

function mergeEdges(edges) {
  const merged = new Map();
  for (const edge of edges) {
    const pair = undirectedPair(edge);
    const roleKey = state.roleDisplay === "split" ? edge.role : "合作";
    const key = `${pair}:${roleKey}`;
    const [source, target] = pair.split("--");
    const current = merged.get(key) || {
      id: key,
      source,
      target,
      role: roleKey,
      roles: [],
      song_count: 0,
      songs: [],
      directions: new Map(),
    };
    current.roles.push(edge.role);
    current.song_count += edge.song_count;
    current.songs.push(...(edge.songs || []));
    const directionKey = `${edge.source}->${edge.target}`;
    const direction = current.directions.get(directionKey) || {
      source: edge.source,
      target: edge.target,
      song_count: 0,
      roles: [],
    };
    direction.song_count += edge.song_count;
    direction.roles.push(edge.role);
    current.directions.set(directionKey, direction);
    merged.set(key, current);
  }
  return [...merged.values()].map((edge) => ({
    ...edge,
    roles: [...new Set(edge.roles)],
    directions: [...edge.directions.values()].map((direction) => ({
      ...direction,
      roles: [...new Set(direction.roles)],
    })),
    songs: uniqueSongs(edge.songs),
  }));
}

function uniqueSongs(songs) {
  const seen = new Set();
  const rows = [];
  for (const song of songs) {
    const key = `${song.mid}:${song.role}:${song.target_mid}`;
    if (seen.has(key)) continue;
    seen.add(key);
    rows.push(song);
  }
  return rows.sort((a, b) => (a.name || "").localeCompare(b.name || "", "zh-CN") || Number(a.id || 0) - Number(b.id || 0));
}

function buildGraph() {
  const edges = mergeEdges(baseEdges());
  const used = new Set(edges.flatMap((edge) => [edge.source, edge.target]));
  let nodes = rawData.nodes.filter((node) => used.has(node.id));
  let graphEdges = edges;
  if (state.search) {
    const search = state.search.toLowerCase();
    const matchingNodeIds = new Set(
      nodes.filter((node) => String(node.name || "").toLowerCase().includes(search)).map((node) => node.id),
    );
    const matchingSongEdges = new Set(
      graphEdges
        .filter((edge) => (edge.songs || []).some((song) => String(song.name || "").toLowerCase().includes(search)))
        .map((edge) => edge.id),
    );
    graphEdges = graphEdges.filter(
      (edge) => matchingNodeIds.has(edge.source) || matchingNodeIds.has(edge.target) || matchingSongEdges.has(edge.id),
    );
    const connected = new Set(graphEdges.flatMap((edge) => [edge.source, edge.target]));
    nodes = nodes.filter((node) => matchingNodeIds.has(node.id) || connected.has(node.id));
  }
  return { nodes, edges: graphEdges };
}

function nodeId(value) {
  return typeof value === "object" ? value.id : value;
}

function edgeId(edge) {
  return edge?.id || "";
}

function selectedEdgePair(selected) {
  if (selected?.pair) return selected.pair;
  const id = selected?.id || "";
  const separator = id.lastIndexOf(":");
  return separator > 0 ? id.slice(0, separator) : "";
}

function selectedEdgeRole(selected) {
  if (selected?.role) return selected.role;
  const id = selected?.id || "";
  const separator = id.lastIndexOf(":");
  return separator > 0 ? id.slice(separator + 1) : "";
}

function edgeSelectionSnapshot(edge) {
  return {
    type: "edge",
    id: edge.id,
    pair: edgePairId(edge),
    role: edge.role,
    roles: [...new Set(edge.roles || [edge.role])].filter(Boolean),
  };
}

function edgeGroupSelectionSnapshot(edges) {
  const roles = new Set();
  edges.forEach((edge) => (edge.roles || [edge.role]).forEach((role) => roles.add(role)));
  return {
    type: "edges",
    ids: edges.map((edge) => edge.id),
    pair: edgePairId(edges[0]),
    roles: [...roles].filter(Boolean),
  };
}

function resolveSelectedEdges() {
  if (state.selected?.type !== "edge" && state.selected?.type !== "edges") return [];
  const exactIds = new Set(state.selected.ids || [state.selected.id].filter(Boolean));
  const exact = currentGraph.edges.filter((edge) => exactIds.has(edge.id));
  if (exact.length) return exact;
  const pair = selectedEdgePair(state.selected);
  if (!pair) return [];
  const candidates = currentGraph.edges.filter((edge) => edgePairId(edge) === pair);
  if (!candidates.length) return [];
  const role = selectedEdgeRole(state.selected);
  if (role) {
    const sameRole = candidates.find((edge) => edge.role === role || (edge.roles || []).includes(role));
    if (sameRole) return [sameRole];
  }
  const selectedRoles = new Set(state.selected.roles || []);
  if (selectedRoles.size) {
    const relatedRoles = candidates.filter((edge) => (edge.roles || [edge.role]).some((item) => selectedRoles.has(item)));
    if (relatedRoles.length) return relatedRoles;
  }
  return candidates;
}

function resolveSelectedEdge() {
  return resolveSelectedEdges()[0] || null;
}

function hasActiveHighlight() {
  return highlightNodes.size > 0 || highlightLinks.size > 0;
}

function isHighlightedNode(node) {
  return highlightNodes.has(node.id);
}

function isHighlightedLink(edge) {
  return (
    highlightLinks.has(edgeId(edge)) ||
    (state.selected?.type === "edge" && state.selected.id === edgeId(edge)) ||
    (state.selected?.type === "edges" && (state.selected.ids || []).includes(edgeId(edge)))
  );
}

function clearHighlights() {
  highlightNodes.clear();
  highlightLinks.clear();
}

function setNodeHighlight(node) {
  clearHighlights();
  if (!node) return;
  highlightNodes.add(node.id);
  currentGraph.edges.forEach((edge) => {
    const source = nodeId(edge.source);
    const target = nodeId(edge.target);
    if (source === node.id || target === node.id) {
      highlightLinks.add(edge.id);
      highlightNodes.add(source);
      highlightNodes.add(target);
    }
  });
}

function setNodeSelectionHighlight() {
  clearHighlights();
  const selectedIds = [...state.selectedNodeIds];
  if (!selectedIds.length) return;
  selectedIds.forEach((id) => highlightNodes.add(id));
  if (selectedIds.length === 1) {
    const node = currentGraph.nodes.find((item) => item.id === selectedIds[0]);
    setNodeHighlight(node);
    return;
  }
  currentGraph.edges.forEach((edge) => {
    const source = nodeId(edge.source);
    const target = nodeId(edge.target);
    if (state.selectedNodeIds.has(source) && state.selectedNodeIds.has(target)) {
      highlightLinks.add(edge.id);
    }
  });
}

function syncNodeSelectionState() {
  const selectedIds = [...state.selectedNodeIds];
  if (!selectedIds.length) {
    state.selected = null;
  } else if (selectedIds.length === 1) {
    state.selected = { type: "node", id: selectedIds[0] };
  } else {
    state.selected = { type: "nodes" };
  }
  setNodeSelectionHighlight();
}

function toggleNodeSelection(node, event) {
  if (!node) return;
  if (state.selected?.type === "edge") state.selected = null;
  const multiSelect = Boolean(event?.ctrlKey || event?.metaKey);
  if (multiSelect) {
    if (state.selectedNodeIds.has(node.id)) {
      state.selectedNodeIds.delete(node.id);
    } else {
      state.selectedNodeIds.add(node.id);
    }
  } else {
    state.selectedNodeIds.clear();
    state.selectedNodeIds.add(node.id);
  }
  syncNodeSelectionState();
}

function setLinkHighlight(edge) {
  clearHighlights();
  if (!edge) return;
  state.selectedNodeIds.clear();
  highlightLinks.add(edge.id);
  highlightNodes.add(nodeId(edge.source));
  highlightNodes.add(nodeId(edge.target));
}

function setLinksHighlight(edges) {
  clearHighlights();
  state.selectedNodeIds.clear();
  edges.forEach((edge) => {
    highlightLinks.add(edge.id);
    highlightNodes.add(nodeId(edge.source));
    highlightNodes.add(nodeId(edge.target));
  });
}

function clearSelectionHighlight() {
  state.selected = null;
  state.selectedNodeIds.clear();
  clearHighlights();
}

function restoreSelectionForCurrentGraph() {
  const currentNodeIds = new Set(currentGraph.nodes.map((node) => node.id));
  if (state.selectedNodeIds.size || state.selected?.type === "node" || state.selected?.type === "nodes") {
    const selectedIds = state.selectedNodeIds.size ? [...state.selectedNodeIds] : [state.selected?.id].filter(Boolean);
    state.selectedNodeIds = new Set(selectedIds.filter((id) => currentNodeIds.has(id)));
    syncNodeSelectionState();
    return;
  }
  if (state.selected?.type === "edge" || state.selected?.type === "edges") {
    const edges = resolveSelectedEdges();
    if (edges.length) {
      state.selected = edges.length === 1 ? edgeSelectionSnapshot(edges[0]) : edgeGroupSelectionSnapshot(edges);
      setLinksHighlight(edges);
      return;
    }
    clearSelectionHighlight();
    return;
  }
  clearHighlights();
}

function graphHeight() {
  const graphTop = $("graph")?.getBoundingClientRect().top || 0;
  return Math.max(430, Math.floor(window.innerHeight - graphTop - 16));
}

function syncDetailPanelHeight() {
  const detailPanel = document.querySelector(".detail-panel");
  const graphPanel = document.querySelector(".graph-panel");
  if (!detailPanel || !graphPanel) return;
  const panelHeight = graphPanel.offsetHeight || Math.round(graphPanel.getBoundingClientRect().height);
  detailPanel.style.height = `${panelHeight}px`;
  detailPanel.style.maxHeight = `${panelHeight}px`;
}

function nodeDegreeMap(edges) {
  const degrees = new Map();
  edges.forEach((edge) => {
    degrees.set(edge.source, (degrees.get(edge.source) || 0) + edge.song_count);
    degrees.set(edge.target, (degrees.get(edge.target) || 0) + edge.song_count);
  });
  return degrees;
}

function seededRandom(seed) {
  let hash = 2166136261;
  for (let index = 0; index < seed.length; index += 1) {
    hash ^= seed.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return ((hash >>> 0) % 10000) / 10000;
}

function graphPayload(nodes, edges) {
  const degrees = nodeDegreeMap(edges);
  const previousNodes = graphInstance?.graphData()?.nodes || [];
  const previousPositions = new Map(previousNodes.map((node) => [node.id, node]));
  return {
    nodes: nodes.map((node) => {
      const previous = previousPositions.get(node.id);
      const degree = degrees.get(node.id) || 0;
      const base = {
        ...node,
        degree,
        val: Math.max(6, Math.min(65, 7 + Math.sqrt(degree || 1) * 2.2)),
      };
      if (!previous) {
        return {
          ...base,
          x: (seededRandom(`${node.id}:x`) - 0.5) * 560,
          y: (seededRandom(`${node.id}:y`) - 0.5) * 420,
        };
      }
      return { ...base, x: previous.x, y: previous.y, vx: previous.vx, vy: previous.vy, fx: previous.fx, fy: previous.fy };
    }),
    links: edges.map((edge) => ({
      ...edge,
      curvature: edge.role === "作词" ? -0.12 : edge.role === "作曲" ? 0.12 : 0,
    })),
  };
}

function getNodeImage(node) {
  if (!node.icon) return null;
  if (imageCache.has(node.icon)) return imageCache.get(node.icon);
  const image = new Image();
  image.src = node.icon;
  imageCache.set(node.icon, image);
  return image;
}

function nodeRadius(node) {
  return Math.max(10, Math.min(65, node.val || 12));
}

function nodeLabelText(node) {
  return String(node.name || node.id);
}

function textNodeMetrics(node, ctx, globalScale) {
  const fontSize = Math.max(10, Math.min(14, 10 + Math.sqrt(node.degree || 1) * 0.28));
  ctx.font = `600 ${fontSize / globalScale}px "Microsoft YaHei", "Segoe UI", Arial, sans-serif`;
  const text = nodeLabelText(node);
  const paddingX = 8 / globalScale;
  const paddingY = 4 / globalScale;
  const width = ctx.measureText(text).width + paddingX * 2;
  const height = fontSize / globalScale + paddingY * 2;
  return { text, fontSize, width, height, paddingX, paddingY };
}

function drawRoundRect(ctx, x, y, width, height, radius) {
  const r = Math.min(radius, width / 2, height / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + width - r, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + r);
  ctx.lineTo(x + width, y + height - r);
  ctx.quadraticCurveTo(x + width, y + height, x + width - r, y + height);
  ctx.lineTo(x + r, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
}

function drawTextNode(node, ctx, globalScale, selected, highlighted, dimmed) {
  const metrics = textNodeMetrics(node, ctx, globalScale);
  const x = node.x - metrics.width / 2;
  const y = node.y - metrics.height / 2;
  ctx.save();
  ctx.globalAlpha = dimmed ? 0.34 : 1;
  if (highlighted || selected) {
    drawRoundRect(ctx, x, y, metrics.width, metrics.height, 5 / globalScale);
    ctx.lineWidth = 0.55 / globalScale;
    ctx.strokeStyle = "rgba(17, 24, 39, 0.48)";
    ctx.stroke();
  }
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillStyle = highlighted || selected ? "#111827" : "#172033";
  ctx.fillText(metrics.text, node.x, node.y);
  ctx.restore();
}

function drawNodeLabel(node, ctx, globalScale, radius) {
  ctx.font = `${11 / globalScale}px "Microsoft YaHei", Arial, sans-serif`;
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  const labelY = node.y + radius + 5 / globalScale;
  ctx.lineWidth = 3 / globalScale;
  ctx.strokeStyle = "rgba(255, 255, 255, 0.96)";
  ctx.strokeText(node.name || node.id, node.x, labelY);
  ctx.fillStyle = "#172033";
  ctx.fillText(node.name || node.id, node.x, labelY);
}

function drawNode(node, ctx, globalScale) {
  const radius = nodeRadius(node);
  const selected = state.selectedNodeIds.has(node.id);
  const highlighted = isHighlightedNode(node);
  const dimmed = hasActiveHighlight() && !highlighted;
  const image = getNodeImage(node);
  if (state.showLabels) {
    drawTextNode(node, ctx, globalScale, selected, highlighted, dimmed);
    return;
  }
  ctx.save();
  ctx.globalAlpha = dimmed ? 0.28 : 1;
  ctx.beginPath();
  ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
  ctx.fillStyle = node.is_target ? "#11936f" : "#3b82f6";
  ctx.fill();
  if (image?.complete && image.naturalWidth) {
    ctx.save();
    ctx.clip();
    ctx.drawImage(image, node.x - radius, node.y - radius, radius * 2, radius * 2);
    ctx.restore();
  } else {
    ctx.fillStyle = "#ffffff";
    ctx.font = `${Math.max(9, radius * 0.8) / globalScale}px "Microsoft YaHei", Arial, sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(String(node.name || "?").slice(0, 1), node.x, node.y);
  }
  if (highlighted) {
    ctx.beginPath();
    ctx.arc(node.x, node.y, radius + 0.6 / globalScale, 0, Math.PI * 2);
    ctx.lineWidth = 0.25 / globalScale;
    ctx.strokeStyle = "rgba(17, 24, 39, 0.08)";
    ctx.stroke();
  }
  ctx.lineWidth = selected || highlighted ? 0.65 / globalScale : 0.75 / globalScale;
  ctx.strokeStyle = selected || highlighted ? "rgba(17, 24, 39, 0.58)" : "#ffffff";
  ctx.stroke();
  if (highlighted || selected) {
    ctx.globalAlpha = 1;
    drawNodeLabel(node, ctx, globalScale, radius);
  }
  ctx.restore();
}

function paintNodePointerArea(node, color, ctx) {
  if (state.showLabels) {
    const metrics = textNodeMetrics(node, ctx, 1);
    ctx.fillStyle = color;
    drawRoundRect(ctx, node.x - metrics.width / 2, node.y - metrics.height / 2, metrics.width, metrics.height, 5);
    ctx.fill();
    return;
  }
  const radius = nodeRadius(node) + 5;
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
  ctx.fill();
}

function linkLabel(edge) {
  if (hasActiveHighlight() && !isHighlightedLink(edge)) return "";
  return directionLabels(edge).join("<br>");
}

function directionLabels(edge) {
  return (edge.directions || []).map((direction) => {
    const roles = (direction.roles || []).join("/");
    return `${nodeName(direction.source)} -> ${nodeName(direction.target)}：${roles} · ${formatNumber(direction.song_count)} 首`;
  });
}

function edgeEndpoint(edge, id) {
  const source = edge.source;
  const target = edge.target;
  if (nodeId(source) === id) return source;
  if (nodeId(target) === id) return target;
  return null;
}

function edgeCurvePoint(edge, progress) {
  const source = edge.source;
  const target = edge.target;
  const sourceId = nodeId(source);
  const t = sourceId === nodeId(edge.__particleDirectionSource) ? progress : 1 - progress;
  const dx = target.x - source.x;
  const dy = target.y - source.y;
  const curvature = Number(edge.curvature || 0);
  if (!curvature) {
    return { x: source.x + dx * t, y: source.y + dy * t };
  }
  const controlX = (source.x + target.x) / 2 + dy * curvature;
  const controlY = (source.y + target.y) / 2 - dx * curvature;
  const oneMinusT = 1 - t;
  return {
    x: oneMinusT * oneMinusT * source.x + 2 * oneMinusT * t * controlX + t * t * target.x,
    y: oneMinusT * oneMinusT * source.y + 2 * oneMinusT * t * controlY + t * t * target.y,
  };
}

function drawDirectionalParticles(edge, ctx, globalScale) {
  if (!state.particlesEnabled) return;
  const directions = edge.directions || [];
  if (!directions.length) return;
  const now = performance.now();
  const radius = 2.2;
  directions.forEach((direction, index) => {
    const source = edgeEndpoint(edge, direction.source);
    const target = edgeEndpoint(edge, direction.target);
    if (!source || !target) return;
    const seed = seededRandom(`${edge.id}:${direction.source}->${direction.target}`);
    const progress = (now * 0.00012 + seed + index * 0.31) % 1;
    edge.__particleDirectionSource = direction.source;
    const point = edgeCurvePoint(edge, progress);
    delete edge.__particleDirectionSource;
    ctx.save();
    ctx.beginPath();
    ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
    ctx.fillStyle = edgeParticleColor(edge);
    ctx.fill();
    ctx.restore();
  });
}

function setupGraph(container) {
  if (graphInstance) return graphInstance;
  graphInstance = new ForceGraph(container)
    .nodeId("id")
    .linkSource("source")
    .linkTarget("target")
    .backgroundColor("rgba(0,0,0,0)")
    .nodeRelSize(1)
    .nodeVal("val")
    .nodeLabel((node) => node.name || node.id)
    .nodeCanvasObject(drawNode)
    .nodePointerAreaPaint(paintNodePointerArea)
    .linkLabel(linkLabel)
    .linkColor((edge) => edgeColor(edge))
    .linkWidth((edge) => edgeWidth(edge))
    .linkCanvasObject(drawDirectionalParticles)
    .linkCanvasObjectMode(() => "after")
    .linkCurvature("curvature")
    .linkDirectionalArrowLength(0)
    .linkDirectionalArrowRelPos(0.88)
    .linkDirectionalParticles(0)
    .linkDirectionalParticleSpeed(0.003)
    .linkDirectionalParticleWidth(3)
    .linkDirectionalParticleColor((edge) => edgeColor(edge))
    .linkHoverPrecision(8)
    .autoPauseRedraw(false)
    .enableNodeDrag(true)
    .enableZoomInteraction(true)
    .enablePanInteraction(true)
    .showPointerCursor((item) => Boolean(item))
    .warmupTicks(70)
    .cooldownTicks(220)
    .d3AlphaDecay(0.035)
    .d3VelocityDecay(0.32)
    .onNodeClick((node, event) => {
      toggleNodeSelection(node, event);
      renderSelection();
    })
    .onLinkClick((edge) => {
      state.selected = edgeSelectionSnapshot(edge);
      setLinkHighlight(edge);
      renderSelection();
    })
    .onBackgroundClick(() => {
      clearSelectionHighlight();
      renderSelection();
    });
  return graphInstance;
}

function configureForces(api) {
  const linkForce = api.d3Force("link");
  if (linkForce?.distance) {
    linkForce.distance((edge) => 92 + Math.max(0, 8 - Math.sqrt(edge.song_count || 1)) * 5);
    linkForce.strength((edge) => Math.min(0.8, 0.16 + Math.sqrt(edge.song_count || 1) * 0.08));
  }
  const chargeForce = api.d3Force("charge");
  if (chargeForce?.strength) chargeForce.strength(-380);
}

function renderGraph() {
  const graph = buildGraph();
  currentGraph = graph;
  updateEdgeWeightScale(graph.edges);
  restoreSelectionForCurrentGraph();
  const container = $("graph");
  const height = graphHeight();
  container.style.height = `${height}px`;
  const width = container.clientWidth || 960;
  const key = JSON.stringify({
    nodes: graph.nodes.map((node) => node.id).sort(),
    edges: graph.edges.map((edge) => edge.id).sort(),
  });
  const shouldFit = key !== graphDataKey;
  graphDataKey = key;
  const api = setupGraph(container);
  configureForces(api);
  api.width(width).height(height);
  syncDetailPanelHeight();
  window.requestAnimationFrame(syncDetailPanelHeight);
  if (shouldFit) {
    api.graphData(graphPayload(graph.nodes, graph.edges));
  }
  if (shouldFit) {
    api.d3ReheatSimulation();
    window.setTimeout(() => {
      if (graphInstance === api) api.zoomToFit(500, 58);
    }, 360);
  }
  if (!graphResizeObserver) {
    graphResizeObserver = new ResizeObserver(() => {
      if (graphInstance) graphInstance.width(container.clientWidth || width).height(container.clientHeight || height);
      syncDetailPanelHeight();
    });
    graphResizeObserver.observe(container);
  }
  $("graph-title").textContent = "无向合作网络";
  $("graph-note").textContent = `目标歌手：${currentScopeLabel()} · 当前图：${formatNumber(graph.nodes.length)} 个音乐人节点 / ${formatNumber(graph.edges.length)} 条关系边 · Ctrl+点击节点可多选 · 多选时只高亮选中节点之间的边`;
}

function findSelected() {
  if (!state.selected) return null;
  const graph = buildGraph();
  if (state.selected.type === "node") return graph.nodes.find((node) => node.id === state.selected.id);
  if (state.selected.type === "nodes") return graph.nodes.filter((node) => state.selectedNodeIds.has(node.id));
  if (state.selected.type === "edges") {
    const ids = new Set(state.selected.ids || []);
    return graph.edges.filter((edge) => ids.has(edge.id));
  }
  return graph.edges.find((edge) => edge.id === state.selected.id);
}

function renderSongList(songs) {
  if (!songs.length) return `<div class="detail-card muted">暂无支撑歌曲。</div>`;
  return songs
    .slice(0, 60)
    .map(
      (song) =>
        `<div class="detail-card"><strong>${escapeHtml(song.name)}</strong><p class="muted">${escapeHtml(
          [song.target, song.role, song.album].filter(Boolean).join(" · "),
        )}</p></div>`,
    )
    .join("");
}

function renderDetail() {
  const item = findSelected();
  if (!item) {
    $("detail-content").innerHTML = `
      <div class="detail-card">
        <strong>${escapeHtml(window.GRAPH_TITLE)}</strong>
        <p class="muted">${escapeHtml(rawData.relationship_direction)}。Ctrl+点击节点可多选，点击边查看支撑歌曲。</p>
      </div>
      <div class="detail-card">
        <strong>数据库规模</strong>
        <p class="muted">${formatNumber(rawData.summary.songs)} 首歌曲 · ${formatNumber(rawData.summary.artists)} 位数据库音乐人 · ${formatNumber(rawData.summary.song_credit_artists)} 条作词/作曲记录</p>
      </div>
    `;
    return;
  }
  if (state.selected.type === "edge" || state.selected.type === "edges") {
    const edges = Array.isArray(item) ? item : [item];
    $("detail-content").innerHTML = `
      ${edges
        .map((edge) => {
          const directionRows = directionLabels(edge)
            .map((label) => `<div class="detail-card"><strong>${escapeHtml(label)}</strong></div>`)
            .join("");
          return `${directionRows}${renderSongList(edge.songs || [])}`;
        })
        .join("")}
    `;
    return;
  }
  if (state.selected.type === "nodes") {
    const selectedEdges = currentGraph.edges.filter((edge) => highlightLinks.has(edge.id));
    $("detail-content").innerHTML = `
      <div class="detail-card">
        <strong>已选 ${formatNumber(item.length)} 位音乐人</strong>
        <p class="muted">只高亮选中节点之间存在的关系。</p>
      </div>
      ${item
        .map(
          (node) => `
            <div class="detail-card">
              <strong>${escapeHtml(node.name)}</strong>
              <p class="muted">演唱 ${formatNumber(node.sung_song_count || 0)} 首 · 作词 ${formatNumber(node.lyricist_song_count || 0)} 首 · 作曲 ${formatNumber(node.composer_song_count || 0)} 首</p>
            </div>
          `,
        )
        .join("")}
      ${selectedEdges
        .map(
          (edge) => `
            ${directionLabels(edge).map((label) => `<div class="detail-card"><strong>${escapeHtml(label)}</strong></div>`).join("")}
            ${renderSongList(edge.songs || [])}
          `,
        )
        .join("")}
    `;
    return;
  }
  const related = rawData.songs.filter((song) => {
    const id = item.mid;
    return (
      (song.singers || []).some((person) => person.mid === id) ||
      (song.lyricists || []).some((person) => person.mid === id) ||
      (song.composers || []).some((person) => person.mid === id)
    );
  });
  $("detail-content").innerHTML = `
    <div class="detail-card">
      <strong>${escapeHtml(item.name)}</strong>
      <p class="muted">演唱 ${formatNumber(item.sung_song_count || 0)} 首 · 作词 ${formatNumber(item.lyricist_song_count || 0)} 首 · 作曲 ${formatNumber(item.composer_song_count || 0)} 首</p>
    </div>
    ${renderSongList(related.map((song) => ({ ...song, target: personNames(song.singers) })))}
  `;
}

function renderTable() {
  const selectedIds = selectedTableNodeIds();
  const tableSearch = state.tableSearch.toLowerCase();
  if (state.activeTab === "edges") {
    const rows = buildGraph().edges.flatMap((edge) =>
      (edge.directions || [])
        .filter((direction) => !selectedIds.size || selectedIds.has(direction.source) || selectedIds.has(direction.target))
        .map((direction) => ({
          role: (direction.roles || []).join("/"),
          source: nodeName(direction.source),
          target: nodeName(direction.target),
          count: direction.song_count,
          songs: (edge.songs || [])
            .filter((song) => song.target_mid === String(direction.target).replace(/^artist:/, ""))
            .filter((song) => (direction.roles || []).includes(song.role))
            .map((song) => song.name)
            .join(" / "),
        })),
    ).filter((row) => matchesTableSearch(row, tableSearch, ["role", "source", "target", "count", "songs"]));
    renderRows(["职能", "来源音乐人", "目标音乐人", "歌曲数", "支撑歌曲"], rows, ["role", "source", "target", "count", "songs"]);
    return;
  }
  const rows = filteredSongs()
    .filter((song) => !selectedIds.size || songHasAnyPerson(song, selectedIds))
    .map((song) => ({
      name: song.name,
      album: song.album,
      lyricists: personNamesForTable(song.lyricists, selectedIds),
      composers: personNamesForTable(song.composers, selectedIds),
      singers: personNamesForTable(song.singers, selectedIds),
    }))
    .filter((song) => {
      if (!tableSearch) return true;
      return [song.name, song.album, song.lyricists, song.composers, song.singers].join(" ").toLowerCase().includes(tableSearch);
    });
  renderRows(["歌曲", "专辑", "作词", "作曲", "演唱"], rows, ["name", "album", "lyricists", "composers", "singers"]);
}

function filteredSongs() {
  return rawData.songs.filter((song) => (song.singers || []).some((person) => state.selectedTargets.has(`artist:${person.mid}`)));
}

function selectedTableNodeIds() {
  if (state.selected?.type !== "node" && state.selected?.type !== "nodes") return new Set();
  return new Set([...state.selectedNodeIds]);
}

function songHasAnyPerson(song, selectedIds) {
  return ["singers", "lyricists", "composers"].some((key) =>
    (song[key] || []).some((person) => selectedIds.has(`artist:${person.mid}`)),
  );
}

function personNamesForTable(values, selectedIds) {
  const people = selectedIds.size ? (values || []).filter((person) => selectedIds.has(`artist:${person.mid}`)) : values;
  return personNames(people);
}

function matchesTableSearch(row, search, keys) {
  if (!search) return true;
  return keys.map((key) => row[key]).join(" ").toLowerCase().includes(search);
}

function renderRows(headers, rows, keys) {
  $("table-content").innerHTML = `
    <table>
      <thead><tr>${headers.map((header) => `<th>${escapeHtml(header)}</th>`).join("")}</tr></thead>
      <tbody>
        ${rows
          .map((row) => `<tr>${keys.map((key) => `<td>${escapeHtml(row[key])}</td>`).join("")}</tr>`)
          .join("")}
      </tbody>
    </table>
  `;
}

function renderLegend() {
  const items = state.roleDisplay === "split"
    ? [
      ["rgba(31, 120, 180, 0.75)", "作词"],
      ["rgba(217, 95, 2, 0.75)", "作曲"],
    ]
    : [["rgba(20, 132, 117, 0.75)", "作词/作曲"]];
  $("legend").innerHTML = items
    .map(([color, label]) => `<span class="legend-item"><span class="legend-swatch" style="background: ${color}"></span>${label}</span>`)
    .join("");
}

function renderHeader() {
  const summary = rawData.summary;
  $("dataset-scope").textContent = `SQLite 静态图谱 · 数据库：${formatNumber(summary.songs)} 首歌曲 / ${formatNumber(summary.artists)} 位音乐人 · 生成于 ${rawData.generated_at}`;
}

function render() {
  renderHeader();
  renderLegend();
  updateTargetDropdownLabel();
  renderGraph();
  renderDetail();
  renderTable();
}

function renderSelection() {
  renderDetail();
  renderTable();
}

function renderTargetMenuState() {
  $("target-dropdown-menu").hidden = !state.targetMenuOpen;
  $("target-dropdown-toggle").setAttribute("aria-expanded", String(state.targetMenuOpen));
}

function updateTargetDropdownLabel() {
  const label = currentScopeLabel();
  $("target-dropdown-label").textContent = label;
  $("target-dropdown-toggle").setAttribute("aria-label", `目标歌手：${label}`);
  $("target-visual-select").innerHTML = `<option>${escapeHtml(label)}</option>`;
}

function renderTargetCheckboxes() {
  const keyword = state.targetFilterSearch;
  const targets = targetItems().filter((item) => {
    if (!keyword) return true;
    return `${item.name} ${item.mid}`.toLowerCase().includes(keyword);
  });
  $("target-checkboxes").innerHTML = targets.length
    ? targets
      .map(
        (item) => `
          <label class="target-option">
            <input type="checkbox" value="${escapeHtml(item.id)}" ${state.selectedTargets.has(item.id) ? "checked" : ""} />
            <span>${escapeHtml(item.name)} (${formatNumber(item.song_count)})</span>
          </label>
        `,
      )
      .join("")
    : `<div class="target-empty">没有匹配的目标歌手</div>`;
  document.querySelectorAll("#target-checkboxes input").forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      if (checkbox.checked) {
        state.selectedTargets.add(checkbox.value);
      } else {
        state.selectedTargets.delete(checkbox.value);
      }
      updateTargetDropdownLabel();
      render();
    });
  });
}

function bindControls() {
  state.selectedTargets = new Set(targetIds());
  renderTargetCheckboxes();
  updateTargetDropdownLabel();
  $("target-dropdown-toggle").addEventListener("click", () => {
    state.targetMenuOpen = !state.targetMenuOpen;
    renderTargetMenuState();
    if (state.targetMenuOpen) $("target-filter-search").focus();
  });
  document.addEventListener("click", (event) => {
    if (!state.targetMenuOpen || event.target.closest(".target-filter")) return;
    state.targetMenuOpen = false;
    renderTargetMenuState();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || !state.targetMenuOpen) return;
    state.targetMenuOpen = false;
    renderTargetMenuState();
  });
  $("target-select-all").addEventListener("click", () => {
    state.selectedTargets = new Set(targetIds());
    renderTargetCheckboxes();
    render();
  });
  $("target-invert").addEventListener("click", () => {
    const nextTargets = new Set();
    targetIds().forEach((id) => {
      if (!state.selectedTargets.has(id)) nextTargets.add(id);
    });
    state.selectedTargets = nextTargets;
    renderTargetCheckboxes();
    render();
  });
  $("target-filter-search").addEventListener("input", (event) => {
    state.targetFilterSearch = event.target.value.trim().toLowerCase();
    renderTargetCheckboxes();
  });
  $("label-toggle").checked = state.showLabels;
  $("particle-toggle").checked = state.particlesEnabled;
  $("role-split-toggle").checked = state.roleDisplay === "split";
  $("role-split-toggle").addEventListener("change", (event) => {
    state.roleDisplay = event.target.checked ? "split" : "merged";
    render();
  });
  $("label-toggle").addEventListener("change", (event) => {
    state.showLabels = event.target.checked;
    render();
  });
  $("particle-toggle").addEventListener("change", (event) => {
    state.particlesEnabled = event.target.checked;
    render();
  });
  $("min-count").addEventListener("input", (event) => {
    state.minCount = Math.max(1, Number(event.target.value || 1));
    render();
  });
  $("search-input").addEventListener("input", (event) => {
    state.search = event.target.value.trim();
    render();
  });
  $("table-search-input").addEventListener("input", (event) => {
    state.tableSearch = event.target.value.trim();
    renderTable();
  });
  document.querySelectorAll(".tab").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      state.activeTab = button.dataset.tab;
      renderTable();
    });
  });
  window.addEventListener("resize", () => {
    if (graphInstance) renderGraph();
  });
}

bindControls();
render();
"""


if __name__ == "__main__":
    main()
