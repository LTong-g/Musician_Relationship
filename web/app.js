const state = {
  catalog: null,
  targetData: new Map(),
  currentTarget: "all",
  viewMode: "artist",
  roleDisplay: "split",
  directionMode: "directed",
  minCount: 2,
  search: "",
  activeTab: "songs",
  selected: null,
  hoveredNode: null,
  hoveredEdge: null,
};

let graphInstance = null;
let graphResizeObserver = null;
let graphDataKey = "";
const imageCache = new Map();
const layoutVersion = "force-graph-20260511";
const maxVisibleContributors = 36;

const roleLabels = {
  split: "作词/作曲分开",
  merged: "合并为合作次数",
};

const $ = (id) => document.getElementById(id);

async function loadJson(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Cannot load ${path}: ${response.status}`);
  return response.json();
}

function catalogTargets() {
  return state.catalog?.targets || state.catalog?.datasets || [];
}

function sourceDataset() {
  return state.catalog?.source_dataset || {
    name: "QQ 音乐",
    description: "由 QQ 音乐元数据离线采集生成的静态关系图谱数据。",
  };
}

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

function joinNames(values) {
  return (values || []).filter(Boolean).join(" / ");
}

function addNode(nodes, node) {
  if (!node?.id) return;
  const existing = nodes.get(node.id);
  if (!existing) {
    nodes.set(node.id, { ...node });
    return;
  }
  Object.entries(node).forEach(([key, value]) => {
    if (value && !existing[key]) existing[key] = value;
  });
}

async function init() {
  try {
    state.catalog = await loadJson("data/catalog.json");
    await Promise.all(
      catalogTargets().map(async (item) => {
        const dataset = await loadJson(`data/${item.file}`);
        state.targetData.set(item.slug, dataset);
      }),
    );
    bindControls();
    render();
  } catch (error) {
    $("dataset-scope").textContent = "数据加载失败";
    $("detail-content").innerHTML = `<div class="detail-card">${escapeHtml(error.message)}</div>`;
  }
}

function bindControls() {
  const targetSelect = $("target-select");
  targetSelect.innerHTML = [
    `<option value="all">全部目标歌手</option>`,
    ...catalogTargets().map((item) => `<option value="${escapeHtml(item.slug)}">${escapeHtml(item.name)}</option>`),
  ].join("");
  targetSelect.value = state.currentTarget;
  targetSelect.addEventListener("change", () => {
    state.currentTarget = targetSelect.value;
    state.selected = null;
    render();
  });

  $("view-mode").addEventListener("change", (event) => {
    state.viewMode = event.target.value;
    state.selected = null;
    render();
  });
  $("role-display").addEventListener("change", (event) => {
    state.roleDisplay = event.target.value;
    state.selected = null;
    render();
  });
  $("direction-mode").addEventListener("change", (event) => {
    state.directionMode = event.target.value;
    renderGraph();
  });
  $("min-count").addEventListener("input", (event) => {
    state.minCount = Math.max(1, Number(event.target.value || 1));
    state.selected = null;
    render();
  });
  $("search-input").addEventListener("input", (event) => {
    state.search = event.target.value.trim().toLowerCase();
    renderGraph();
  });
  document.querySelectorAll(".tab").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      state.activeTab = button.dataset.tab;
      renderTable();
    });
  });
}

function selectedTargets() {
  if (state.currentTarget === "all") return [...state.targetData.values()];
  return state.targetData.has(state.currentTarget) ? [state.targetData.get(state.currentTarget)] : [];
}

function mergeSummary(targets) {
  return targets.reduce(
    (summary, dataset) => {
      summary.songs += dataset.summary.songs || 0;
      summary.initial_candidates += dataset.summary.initial_candidates || 0;
      summary.credit_incomplete += dataset.summary.credit_incomplete || 0;
      summary.edges += dataset.summary.edges || 0;
      summary.contributors += dataset.summary.contributors || 0;
      summary.self_lyricist_songs += dataset.summary.self_lyricist_songs || 0;
      summary.self_composer_songs += dataset.summary.self_composer_songs || 0;
      return summary;
    },
    {
      songs: 0,
      initial_candidates: 0,
      credit_incomplete: 0,
      edges: 0,
      contributors: 0,
      self_lyricist_songs: 0,
      self_composer_songs: 0,
    },
  );
}

function currentScopeLabel() {
  if (state.currentTarget === "all") return `全部 ${formatNumber(catalogTargets().length)} 位目标歌手`;
  return catalogTargets().find((item) => item.slug === state.currentTarget)?.name || "当前目标歌手";
}

function render() {
  const source = sourceDataset();
  const totals = state.catalog.totals || {};
  $("dataset-scope").textContent =
    `${source.name}数据集 · 当前范围：${currentScopeLabel()} · ` +
    `${formatNumber(totals.songs)} 首可视化歌曲，${formatNumber(totals.credit_incomplete)} 首制作人员不完整条目已隔离。`;
  $("source-name").textContent = source.name;
  $("source-description").textContent = source.description || "";
  renderSummary(selectedTargets());
  renderGraph();
  renderDetail();
  renderTable();
}

function renderSummary(targets) {
  const summary = mergeSummary(targets);
  const bridgeCount = countBridgeContributorsForScope();
  const graph = buildArtistGraph();
  const metrics = [
    ["目标歌手", state.currentTarget === "all" ? targets.length : 1],
    ["可视化歌曲", summary.songs],
    ["贡献者", countUniqueContributors(targets)],
    ["当前图谱边", graph.edges.length],
    ["共同合作者", bridgeCount],
    ["隔离条目", summary.credit_incomplete],
  ];
  $("summary-strip").innerHTML = metrics
    .map(([label, value]) => `<div class="metric"><span>${label}</span><strong>${formatNumber(value)}</strong></div>`)
    .join("");
}

function countUniqueContributors(targets) {
  const ids = new Set();
  targets.forEach((dataset) => {
    dataset.graph.nodes.forEach((node) => {
      if (node.type === "artist") ids.add(node.id);
    });
  });
  return ids.size;
}

function countBridgeContributorsForScope() {
  return bridgeItemsForScope().length;
}

function roleAllows(edgeRole) {
  return edgeRole === "作词" || edgeRole === "作曲" || edgeRole === "合作";
}

function mergeEdges(edges) {
  if (state.roleDisplay === "split") return edges;
  const merged = new Map();
  for (const edge of edges) {
    const key = `${edge.source}->${edge.target}`;
    const current = merged.get(key) || {
      id: key,
      source: edge.source,
      target: edge.target,
      role: "合作",
      roles: [],
      song_count: 0,
      songs: [],
    };
    current.roles.push(edge.role);
    current.song_count += edge.song_count;
    current.songs.push(...(edge.songs || []).map((song) => ({ ...song, role: edge.role })));
    merged.set(key, current);
  }
  return [...merged.values()];
}

function edgeWeight(edge) {
  return edge.song_count || 0;
}

function reduceGraphForOverview(edges) {
  if (state.search || state.viewMode !== "artist") return edges;
  const byTarget = new Map();
  edges.forEach((edge) => {
    const target = edge.target;
    const contributor = edge.source;
    const current = byTarget.get(target) || new Map();
    const item = current.get(contributor) || {
      contributor,
      total: 0,
      strongest: 0,
    };
    item.total += edgeWeight(edge);
    item.strongest = Math.max(item.strongest, edgeWeight(edge));
    current.set(contributor, item);
    byTarget.set(target, current);
  });

  const allowedPairs = new Set();
  byTarget.forEach((contributors, target) => {
    [...contributors.values()]
      .sort((a, b) => b.total - a.total || b.strongest - a.strongest || a.contributor.localeCompare(b.contributor))
      .slice(0, maxVisibleContributors)
      .forEach((item) => allowedPairs.add(`${item.contributor}->${target}`));
  });
  return edges.filter((edge) => allowedPairs.has(`${edge.source}->${edge.target}`));
}

function buildArtistGraph() {
  const nodes = new Map();
  let edges = [];
  selectedTargets().forEach((dataset) => {
    dataset.graph.nodes.forEach((node) => addNode(nodes, node));
    edges.push(
      ...dataset.graph.edges
        .filter((edge) => roleAllows(edge.role))
        .map((edge) => ({ ...edge, target_slug: dataset.slug, target_name: dataset.name })),
    );
  });
  edges = reduceGraphForOverview(mergeEdges(edges).filter((edge) => edge.song_count >= state.minCount));
  const usedNodeIds = new Set(edges.flatMap((edge) => [edge.source, edge.target]));
  nodes.forEach((node) => {
    if (node.type === "target") usedNodeIds.add(node.id);
  });
  return { nodes: [...nodes.values()].filter((node) => usedNodeIds.has(node.id)), edges };
}

function bridgeItemsForScope() {
  const selectedSlug = state.currentTarget === "all" ? "" : state.currentTarget;
  const allowed = new Set(catalogTargets().map((target) => target.slug));
  return (state.catalog.bridge_contributors || [])
    .map((bridge) => {
      if (selectedSlug && !(bridge.target_slugs || []).includes(selectedSlug)) return null;
      const targets = (bridge.targets || []).filter((target) => allowed.has(target.slug));
      if (!targets.length) return null;
      return {
        ...bridge,
        targets,
        target_slugs: targets.map((target) => target.slug),
        target_count: targets.length,
        song_count: targets.reduce((sum, target) => sum + (target.song_count || 0), 0),
      };
    })
    .filter((bridge) => bridge && bridge.target_count > 1);
}

function buildBridgeGraph() {
  const nodes = new Map();
  const edges = [];
  const targetsBySlug = new Map();
  const bridgeItems = bridgeItemsForScope();
  const targetSlugs = new Set(bridgeItems.flatMap((bridge) => bridge.target_slugs || []));
  if (state.currentTarget !== "all") targetSlugs.add(state.currentTarget);
  if (!targetSlugs.size) {
    selectedTargets().forEach((dataset) => targetSlugs.add(dataset.slug));
  }
  [...targetSlugs].forEach((slug) => {
    const dataset = state.targetData.get(slug);
    if (!dataset) return;
    const target = dataset.graph.nodes.find((node) => node.type === "target");
    if (target) {
      addNode(nodes, target);
      targetsBySlug.set(dataset.slug, target);
    }
  });
  bridgeItems.forEach((bridge) => {
    addNode(nodes, {
      id: bridge.id,
      type: "artist",
      name: bridge.name,
    });
    bridge.targets.forEach((target) => {
      const targetNode = targetsBySlug.get(target.slug);
      if (!targetNode) return;
      if (state.roleDisplay === "merged") {
        edges.push({
          id: `${bridge.id}->${targetNode.id}:合作`,
          source: bridge.id,
          target: targetNode.id,
          role: "合作",
          song_count: target.song_count,
          songs: Object.values(target.roles || {}).flatMap((role) => role.songs || []),
        });
        return;
      }
      Object.entries(target.roles || {}).forEach(([role, payload]) => {
        edges.push({
          id: `${bridge.id}->${targetNode.id}:${role}`,
          source: bridge.id,
          target: targetNode.id,
          role,
          song_count: payload.song_count || 0,
          songs: payload.songs || [],
        });
      });
    });
  });
  return {
    nodes: [...nodes.values()],
    edges: edges.filter((edge) => edge.song_count >= state.minCount),
  };
}

function buildGraph() {
  if (state.viewMode === "bridge") return buildBridgeGraph();
  return buildArtistGraph();
}

function nodeMatches(node) {
  if (!state.search) return true;
  return String(node.name || "").toLowerCase().includes(state.search);
}

function seededRandom(seed) {
  let hash = 2166136261;
  for (let index = 0; index < seed.length; index += 1) {
    hash ^= seed.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return ((hash >>> 0) % 10000) / 10000;
}

function graphHeightFor(nodes) {
  const targetCount = nodes.filter((node) => node.type === "target").length;
  const artistCount = nodes.filter((node) => node.type === "artist").length;
  const nodeCount = targetCount + artistCount;
  if (state.viewMode === "bridge") return Math.max(660, Math.min(1180, 610 + nodeCount * 8));
  return Math.max(660, Math.min(1220, 620 + nodeCount * 4));
}

function nodeRadius(node) {
  if (node.type === "target") return 17;
  return Math.min(15, 8 + Math.sqrt(node.degree || 1) * 1.4);
}

function nodeColor(node) {
  if (node.type === "target") return "#2458c7";
  return "#13956f";
}

function edgeColor(edge) {
  if (edge.role === "作词") return "rgba(31, 120, 180, 0.58)";
  if (edge.role === "作曲") return "rgba(217, 95, 2, 0.58)";
  return "rgba(71, 84, 103, 0.52)";
}

function selectedNodeId() {
  return state.selected?.type === "node" ? state.selected.id : "";
}

function selectedEdgeId() {
  return state.selected?.type === "edge" ? state.selected.id : "";
}

function nodeDegreeMap(edges) {
  const degrees = new Map();
  edges.forEach((edge) => {
    degrees.set(edge.source, (degrees.get(edge.source) || 0) + edge.song_count);
    degrees.set(edge.target, (degrees.get(edge.target) || 0) + edge.song_count);
  });
  return degrees;
}

function shouldShowNodeLabel(node, degree, selected) {
  if (selected) return true;
  if (node.type === "target") return true;
  if (state.search) return true;
  if (state.viewMode === "bridge") return true;
  return degree >= 8;
}

function forceGraphData(nodes, edges) {
  const degrees = nodeDegreeMap(edges);
  const previousNodes = graphInstance?.graphData()?.nodes || [];
  const previousPositions = new Map(previousNodes.map((node) => [node.id, node]));
  const graphNodes = nodes.map((node) => ({
    ...node,
    degree: degrees.get(node.id) || 0,
    val: node.type === "target" ? 18 : Math.max(6, Math.sqrt(degrees.get(node.id) || 1) * 4),
  })).map((node) => {
    const previous = previousPositions.get(node.id);
    if (!previous) {
      return {
        ...node,
        x: (seededRandom(`${node.id}:x`) - 0.5) * 520,
        y: (seededRandom(`${node.id}:y`) - 0.5) * 380,
      };
    }
    return {
      ...node,
      x: previous.x,
      y: previous.y,
      vx: previous.vx,
      vy: previous.vy,
      fx: previous.fx,
      fy: previous.fy,
    };
  });
  const graphLinks = edges.map((edge) => ({
    ...edge,
    source: edge.source,
    target: edge.target,
    curvature: edge.role === "作词" ? -0.12 : edge.role === "作曲" ? 0.12 : 0,
  }));
  return { nodes: graphNodes, links: graphLinks };
}

function getNodeImage(node) {
  if (!node.icon) return null;
  if (imageCache.has(node.icon)) return imageCache.get(node.icon);
  const image = new Image();
  image.src = node.icon;
  imageCache.set(node.icon, image);
  return image;
}

function drawNode(node, ctx, globalScale) {
  const radius = nodeRadius(node);
  const selected = selectedNodeId() === node.id;
  const hovered = state.hoveredNode?.id === node.id;
  const degree = node.degree || 0;
  const image = getNodeImage(node);

  ctx.save();
  ctx.beginPath();
  ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
  ctx.fillStyle = nodeColor(node);
  ctx.fill();

  if (image?.complete && image.naturalWidth) {
    ctx.save();
    ctx.clip();
    ctx.drawImage(image, node.x - radius, node.y - radius, radius * 2, radius * 2);
    ctx.restore();
  }

  ctx.lineWidth = selected || hovered ? 3.4 / globalScale : 2.2 / globalScale;
  ctx.strokeStyle = selected ? "#2458c7" : hovered ? "#111827" : "#ffffff";
  ctx.stroke();

  const showLabel = shouldShowNodeLabel(node, degree, selected || hovered);
  if (showLabel) {
    const fontSize = node.type === "target" ? 13 : 11;
    ctx.font = `${fontSize / globalScale}px "Segoe UI", "Microsoft YaHei", Arial, sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    const label = node.name || node.id;
    const labelY = node.y + radius + 5 / globalScale;
    ctx.lineWidth = 4 / globalScale;
    ctx.strokeStyle = "rgba(255, 255, 255, 0.92)";
    ctx.strokeText(label, node.x, labelY);
    ctx.fillStyle = "#182230";
    ctx.fillText(label, node.x, labelY);
  }
  ctx.restore();
}

function paintNodePointerArea(node, color, ctx) {
  const radius = nodeRadius(node) + 4;
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
  ctx.fill();
}

function linkLabel(edge) {
  return `${getNodeName(edge.source?.id || edge.source)} -> ${getNodeName(edge.target?.id || edge.target)}<br>${edge.role} · ${formatNumber(edge.song_count)} 首`;
}

function setupGraphInstance(container) {
  if (graphInstance) return graphInstance;
  graphInstance = new ForceGraph(container)
    .nodeId("id")
    .linkSource("source")
    .linkTarget("target")
    .backgroundColor("rgba(0,0,0,0)")
    .nodeRelSize(1)
    .nodeVal("val")
    .nodeLabel((node) => node.name || node.id)
    .nodeColor(nodeColor)
    .nodeCanvasObject(drawNode)
    .nodePointerAreaPaint(paintNodePointerArea)
    .linkLabel(linkLabel)
    .linkColor((edge) => (selectedEdgeId() === edge.id ? "#111827" : edgeColor(edge)))
    .linkWidth((edge) => (selectedEdgeId() === edge.id ? 2.8 : Math.min(2.2, 0.7 + Math.sqrt(edge.song_count || 1) * 0.36)))
    .linkCurvature("curvature")
    .linkDirectionalArrowLength((edge) => (state.directionMode === "directed" && selectedEdgeId() === edge.id ? 8 : 0))
    .linkDirectionalArrowRelPos(0.88)
    .linkDirectionalArrowColor((edge) => (selectedEdgeId() === edge.id ? "#111827" : edgeColor(edge)))
    .linkDirectionalParticles((edge) => (state.directionMode === "directed" && selectedEdgeId() === edge.id ? 1 : 0))
    .linkDirectionalParticleWidth(3)
    .linkDirectionalParticleColor((edge) => edgeColor(edge))
    .linkHoverPrecision(8)
    .autoPauseRedraw(false)
    .enableNodeDrag(true)
    .enableZoomInteraction(true)
    .enablePanInteraction(true)
    .showPointerCursor((item) => Boolean(item))
    .warmupTicks(80)
    .cooldownTicks(220)
    .d3AlphaDecay(0.035)
    .d3VelocityDecay(0.32)
    .onNodeHover((node) => {
      state.hoveredNode = node;
    })
    .onLinkHover((edge) => {
      state.hoveredEdge = edge;
    })
    .onNodeClick((node) => {
      state.selected = { type: "node", id: node.id };
      renderGraph();
      renderDetail();
      graphInstance.centerAt(node.x, node.y, 450);
      graphInstance.zoom(Math.max(graphInstance.zoom(), 1.7), 450);
    })
    .onLinkClick((edge) => {
      state.selected = { type: "edge", id: edge.id };
      renderGraph();
      renderDetail();
    })
    .onBackgroundClick(() => {
      state.selected = null;
      renderGraph();
      renderDetail();
    });

  return graphInstance;
}

function configureGraphForces(graphApi) {
  const linkForce = graphApi.d3Force("link");
  if (linkForce?.distance) {
    linkForce.distance((edge) => (state.viewMode === "bridge" ? 120 : 95) + Math.max(0, 6 - (edge.song_count || 1)) * 8);
    linkForce.strength((edge) => Math.min(0.78, 0.16 + Math.sqrt(edge.song_count || 1) * 0.08));
  }
  const chargeForce = graphApi.d3Force("charge");
  if (chargeForce?.strength) chargeForce.strength((node) => (node.type === "target" ? -650 : -280));
}

function renderGraph() {
  const container = $("graph");
  const graph = buildGraph();
  let nodes = graph.nodes;
  let edges = graph.edges;

  if (state.search) {
    const matchingIds = new Set(nodes.filter(nodeMatches).map((node) => node.id));
    edges = edges.filter((edge) => matchingIds.has(edge.source) || matchingIds.has(edge.target));
    const connected = new Set(edges.flatMap((edge) => [edge.source, edge.target]));
    nodes = nodes.filter((node) => matchingIds.has(node.id) || connected.has(node.id));
  }

  const height = graphHeightFor(nodes);
  container.style.height = `${height}px`;
  const width = container.clientWidth || 960;
  const nextGraphDataKey = JSON.stringify({
    nodes: nodes.map((node) => node.id).sort(),
    edges: edges.map((edge) => edge.id).sort(),
  });
  const shouldFit = nextGraphDataKey !== graphDataKey;
  graphDataKey = nextGraphDataKey;
  const fgData = forceGraphData(nodes, edges);
  const graphApi = setupGraphInstance(container);
  configureGraphForces(graphApi);
  graphApi.width(width).height(height).graphData(fgData);
  if (shouldFit) {
    graphApi.d3ReheatSimulation();
    window.setTimeout(() => {
      if (graphInstance === graphApi) graphApi.zoomToFit(500, 56);
    }, 360);
  }
  if (!graphResizeObserver) {
    graphResizeObserver = new ResizeObserver(() => {
      const currentWidth = container.clientWidth || 960;
      const currentHeight = container.clientHeight || height;
      if (graphInstance) graphInstance.width(currentWidth).height(currentHeight);
    });
    graphResizeObserver.observe(container);
  }

  const modeLabel = $("view-mode").selectedOptions[0]?.textContent || "图谱";
  $("graph-title").textContent = `${modeLabel} · ${currentScopeLabel()}`;
  $("graph-note").textContent = edges.length
    ? `${formatNumber(nodes.length)} 个节点，${formatNumber(edges.length)} 条边 · 选中边查看方向和歌曲 · ${layoutVersion}`
    : `${formatNumber(nodes.length)} 个节点，当前筛选下暂无连边 · ${layoutVersion}`;
}

function findSelected() {
  if (!state.selected) return null;
  const graph = buildGraph();
  if (state.selected.type === "node") return graph.nodes.find((node) => node.id === state.selected.id);
  return graph.edges.find((edge) => edge.id === state.selected.id);
}

function allSongs() {
  const targets =
    state.viewMode === "bridge"
      ? [...new Set(bridgeItemsForScope().flatMap((bridge) => bridge.target_slugs || []))]
          .map((slug) => state.targetData.get(slug))
          .filter(Boolean)
      : selectedTargets();
  return targets.flatMap((dataset) => dataset.songs.map((song) => ({ ...song, target: dataset.name })));
}

function renderDetail() {
  const item = findSelected();
  if (!item) {
    $("detail-content").innerHTML = `
      <div class="detail-card">
        <strong>${escapeHtml(sourceDataset().name)}数据集</strong>
        <p class="muted">当前查看 ${escapeHtml(currentScopeLabel())}。点击节点或边查看支撑歌曲。</p>
      </div>
    `;
    return;
  }
  if (state.selected.type === "edge") {
    $("detail-content").innerHTML = `
      <div class="detail-card">
        <strong>${escapeHtml(item.role)} · ${formatNumber(item.song_count)} 首</strong>
        <p class="muted">${escapeHtml(getNodeName(item.source))} -> ${escapeHtml(getNodeName(item.target))}</p>
      </div>
      ${renderSongList(item.songs || [])}
    `;
    return;
  }
  const relatedSongs = allSongs().filter((song) => {
    const names = [...(song.lyricists || []), ...(song.composers || [])];
    return names.includes(item.name) || song.target === item.name || song.name === item.name;
  });
  $("detail-content").innerHTML = `
    <div class="detail-card">
      <strong>${escapeHtml(item.name)}</strong>
      <p class="muted">${escapeHtml(item.type)}${item.mid ? ` · ${escapeHtml(item.mid)}` : ""}</p>
    </div>
    ${renderSongList(relatedSongs.slice(0, 40))}
  `;
}

function getNodeName(id) {
  for (const dataset of state.targetData.values()) {
    const node = dataset.graph.nodes.find((item) => item.id === id);
    if (node) return node.name;
  }
  return id;
}

function renderSongList(songs) {
  if (!songs.length) return `<div class="detail-card muted">暂无支撑歌曲。</div>`;
  return songs
    .map(
      (song) =>
        `<div class="detail-card"><strong>${escapeHtml(song.name)}</strong><p class="muted">${escapeHtml(
          [song.target, song.role, song.album].filter(Boolean).join(" · "),
        )}</p></div>`,
    )
    .join("");
}

function renderTable() {
  if (state.activeTab === "edges") {
    const rows = buildArtistGraph().edges.map((edge) => ({
      role: edge.role,
      source: getNodeName(edge.source),
      target: getNodeName(edge.target),
      count: edge.song_count,
      songs: (edge.songs || []).map((song) => song.name).join(" / "),
    }));
    renderRows(["职能", "贡献者", "目标歌手", "歌曲数", "支撑歌曲"], rows, ["role", "source", "target", "count", "songs"]);
    return;
  }
  if (state.activeTab === "quality") {
    const rows = selectedTargets().flatMap((dataset) =>
      Object.entries(dataset.quality.credit_filter_reason_counts || {}).map(([reason, count]) => ({
        target: dataset.name,
        reason,
        count,
      })),
    );
    renderRows(["目标歌手", "隔离原因", "数量"], rows, ["target", "reason", "count"]);
    return;
  }
  renderRows(["歌曲", "专辑", "作词", "作曲", "目标歌手"], allSongs(), ["name", "album", "lyricists", "composers", "target"]);
}

function renderRows(headers, rows, keys) {
  $("table-content").innerHTML = `
    <table>
      <thead><tr>${headers.map((header) => `<th>${escapeHtml(header)}</th>`).join("")}</tr></thead>
      <tbody>
        ${rows
          .map(
            (row) => `<tr>${keys
              .map((key) => `<td>${escapeHtml(Array.isArray(row[key]) ? joinNames(row[key]) : row[key])}</td>`)
              .join("")}</tr>`,
          )
          .join("")}
      </tbody>
    </table>
  `;
}

init();
