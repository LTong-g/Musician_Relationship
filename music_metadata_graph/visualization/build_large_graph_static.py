from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from music_metadata_graph.pipelines.defaults import DEFAULT_DB_PATH, DEFAULT_MVP_DB_PATH
from music_metadata_graph.visualization.build_static_graph import (
    CSS,
    JS,
    DEFAULT_VENDOR_PATH,
    BuildConfig,
    build_graph_data,
    connect_database,
    html_document,
    read_vendor_script,
)


DEFAULT_OUTPUT_DIR = Path("data/visualization_large_graph")
DEFAULT_MVP_OUTPUT_DIR = Path("data/visualization_mvp_large_graph")


def replace_function(source: str, name: str, replacement: str) -> str:
    marker = f"function {name}("
    start = source.index(marker)
    next_start = source.find("\nfunction ", start + len(marker))
    if next_start == -1:
        raise ValueError(f"Cannot find end of JavaScript function: {name}")
    return source[:start] + replacement.rstrip() + "\n" + source[next_start + 1 :]


LARGE_GRAPH_GRAPH_PAYLOAD = r"""
function graphPayload(nodes, edges) {
  return {
    nodes: nodes.map((node) => ({
      ...node,
      name: node.name || node.id,
    })),
    links: edges.map((edge) => ({ ...edge })),
  };
}
"""


LARGE_GRAPH_SETUP_GRAPH = r"""
function setupGraph(container) {
  if (graphInstance) return graphInstance;
  window.devicePixelRatio = 1; // use standard resolution in retina displays
  graphInstance = new ForceGraph(container)
    .d3AlphaDecay(0)
    .d3VelocityDecay(0.08)
    .cooldownTime(60000)
    .linkColor(() => 'rgba(0,0,0,0.05)')
    .zoom(0.05)
    .enablePointerInteraction(true)
    .onNodeClick((node, event) => {
      toggleNodeSelection(node, event);
      renderSelection();
    })
    .onLinkClick((edge) => {
      state.selected = { type: "edge", id: edge.id };
      setLinkHighlight(edge);
      renderSelection();
    })
    .onBackgroundClick(() => {
      clearSelectionHighlight();
      renderSelection();
    });
  return graphInstance;
}
"""


LARGE_GRAPH_CONFIGURE_FORCES = r"""
function configureForces(api) {
  return api;
}
"""


LARGE_GRAPH_RENDER_GRAPH = r"""
function renderGraph() {
  const graph = buildGraph();
  currentGraph = graph;
  updateEdgeWeightScale(graph.edges);
  if (state.selectedNodeIds.size) {
    setNodeSelectionHighlight();
  } else if (!state.selected) {
    clearHighlights();
  }
  const container = $("graph");
  const height = graphHeight();
  container.style.height = `${height}px`;
  const detailPanel = document.querySelector(".detail-panel");
  if (detailPanel) {
    detailPanel.style.height = `${height + document.querySelector(".panel-head").offsetHeight}px`;
    detailPanel.style.maxHeight = `${height + document.querySelector(".panel-head").offsetHeight}px`;
  }
  const width = container.clientWidth || 960;
  const key = JSON.stringify({
    nodes: graph.nodes.map((node) => node.id).sort(),
    edges: graph.edges.map((edge) => edge.id).sort(),
  });
  const shouldReloadData = key !== graphDataKey;
  graphDataKey = key;
  const api = setupGraph(container);
  configureForces(api);
  api.width(width).height(height);
  if (shouldReloadData) {
    api.graphData(graphPayload(graph.nodes, graph.edges));
    api.d3ReheatSimulation();
  }
  if (!graphResizeObserver) {
    graphResizeObserver = new ResizeObserver(() => {
      if (graphInstance) graphInstance.width(container.clientWidth || width).height(container.clientHeight || height);
    });
    graphResizeObserver.observe(container);
  }
  $("graph-title").textContent = "Large-graph 示例绘图区";
  $("graph-note").textContent = `${currentScopeLabel()} · ${formatNumber(graph.nodes.length)} 个节点，${formatNumber(graph.edges.length)} 条边 · 绘图区配置按 force-graph 官方 large-graph 示例，仅开启鼠标交互`;
}
"""


def make_large_graph_js(base_js: str = JS) -> str:
    js = replace_function(base_js, "graphPayload", LARGE_GRAPH_GRAPH_PAYLOAD)
    js = replace_function(js, "setupGraph", LARGE_GRAPH_SETUP_GRAPH)
    js = replace_function(js, "configureForces", LARGE_GRAPH_CONFIGURE_FORCES)
    return replace_function(js, "renderGraph", LARGE_GRAPH_RENDER_GRAPH)


LARGE_GRAPH_JS = make_large_graph_js()
LARGE_GRAPH_CSS = (
    CSS
    + r"""

#graph {
  background: #ffffff;
}

#graph canvas {
  display: block;
}
"""
)


def large_graph_html_document(title: str, graph_data: dict[str, Any], vendor_script: str) -> str:
    return html_document(title, graph_data, vendor_script, css=LARGE_GRAPH_CSS, js=LARGE_GRAPH_JS)


def write_visualization(config: BuildConfig) -> dict[str, Any]:
    with connect_database(config.db_path) as connection:
        graph_data = build_graph_data(connection)

    vendor_script = read_vendor_script(config.vendor_path)
    config.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = config.output_dir / "index.html"
    output_path.write_text(large_graph_html_document(config.title, graph_data, vendor_script), encoding="utf-8", newline="\n")
    return {
        "output": output_path.as_posix(),
        "db": config.db_path.as_posix(),
        "nodes": len(graph_data["nodes"]),
        "edges": len(graph_data["edges"]),
        "songs": len(graph_data["songs"]),
        "drawing": "MVP shell with force-graph example/large-graph drawing configuration and pointer interaction enabled",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an MVP static page whose drawing area mirrors force-graph example/large-graph.")
    parser.add_argument("--db", type=Path, default=None, help="SQLite database path.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Directory for index.html.")
    parser.add_argument("--title", default="音乐人合作关系图谱 Large Graph", help="HTML page title.")
    parser.add_argument("--vendor", type=Path, default=DEFAULT_VENDOR_PATH, help="Local force-graph runtime path.")
    parser.add_argument("--mvp", action="store_true", help="Use the MVP database and MVP large-graph visualization output directory.")
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


if __name__ == "__main__":
    main()
