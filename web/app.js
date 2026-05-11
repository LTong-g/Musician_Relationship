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
};

const layoutVersion = "soft-edge-20260511";
const maxVisibleContributors = 36;

const roleClass = {
  作词: "role-lyric",
  作曲: "role-compose",
  合作: "role-merged",
};

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

function placeRing(nodes, centerX, centerY, radius, positions, offset) {
  const count = Math.max(nodes.length, 1);
  nodes.forEach((node, index) => {
    const angle = offset + (Math.PI * 2 * index) / count;
    positions.set(node.id, {
      x: centerX + Math.cos(angle) * radius,
      y: centerY + Math.sin(angle) * radius,
    });
  });
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function seededRandom(seed) {
  let hash = 2166136261;
  for (let index = 0; index < seed.length; index += 1) {
    hash ^= seed.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return ((hash >>> 0) % 10000) / 10000;
}

function edgeNodeMap(edges) {
  const map = new Map();
  edges.forEach((edge) => {
    if (!map.has(edge.source)) map.set(edge.source, []);
    if (!map.has(edge.target)) map.set(edge.target, []);
    map.get(edge.source).push(edge);
    map.get(edge.target).push(edge);
  });
  return map;
}

function connectedTargetIds(nodeId, edges, nodeById) {
  const ids = new Set();
  edges.forEach((edge) => {
    if (edge.source !== nodeId && edge.target !== nodeId) return;
    const otherId = edge.source === nodeId ? edge.target : edge.source;
    const otherNode = nodeById.get(otherId);
    if (otherNode?.type === "target") ids.add(otherId);
  });
  return [...ids];
}

function distributeRow(nodes, y, left, right, positions) {
  if (!nodes.length) return;
  const gap = nodes.length === 1 ? 0 : (right - left) / (nodes.length - 1);
  nodes.forEach((node, index) => {
    positions.set(node.id, {
      x: nodes.length === 1 ? (left + right) / 2 : left + gap * index,
      y,
    });
  });
}

function graphHeightFor(nodes, edges, width) {
  const targetCount = nodes.filter((node) => node.type === "target").length;
  const artistCount = nodes.filter((node) => node.type === "artist").length;
  const nodeCount = targetCount + artistCount;
  if (state.viewMode === "bridge") return clamp(620 + nodeCount * 10, 680, 1400);
  return clamp(640 + nodeCount * 5, 700, 1600);
}

function initialPositions(nodes, edges, width, height) {
  const positions = new Map();
  const targetNodes = nodes.filter((node) => node.type === "target");
  const artistNodes = nodes.filter((node) => node.type === "artist");

  const centerX = width / 2;
  const centerY = height / 2;
  const targetRadius = Math.min(width, height) * 0.15;
  targetNodes.forEach((node, index) => {
    const angle = -Math.PI / 2 + (Math.PI * 2 * index) / Math.max(targetNodes.length, 1);
    positions.set(node.id, {
      x: centerX + Math.cos(angle) * (targetNodes.length === 1 ? 0 : targetRadius),
      y: centerY + Math.sin(angle) * (targetNodes.length === 1 ? 0 : targetRadius),
    });
  });

  artistNodes.forEach((node, index) => {
    const jitter = seededRandom(node.id);
    const angle = Math.PI * 2 * ((index + jitter) / Math.max(artistNodes.length, 1));
    const radius = Math.min(width, height) * (state.viewMode === "bridge" ? 0.28 : 0.34);
    positions.set(node.id, {
      x: centerX + Math.cos(angle) * radius + (seededRandom(`${node.id}:x`) - 0.5) * 90,
      y: centerY + Math.sin(angle) * radius + (seededRandom(`${node.id}:y`) - 0.5) * 90,
    });
  });

  return positions;
}

function anchorForNode(node, width, height) {
  if (state.viewMode === "bridge") {
    if (node.type === "target") return { x: width * 0.5, y: height * 0.64, strength: 0.01 };
    return { x: width * 0.5, y: height * 0.36, strength: 0.009 };
  }
  if (node.type === "target") return { x: width * 0.52, y: height * 0.52, strength: 0.008 };
  return { x: width * 0.5, y: height * 0.5, strength: 0.003 };
}

function forceDirectedLayout(nodes, edges, width, height) {
  const positions = initialPositions(nodes, edges, width, height);
  const nodeById = new Map(nodes.map((node) => [node.id, node]));
  const velocities = new Map(nodes.map((node) => [node.id, { x: 0, y: 0 }]));
  const iterations = nodes.length > 130 ? 180 : 240;
  const charge = 2200;
  const edgeStrength = 0.024;

  for (let iteration = 0; iteration < iterations; iteration += 1) {
    const alpha = 1 - iteration / iterations;
    for (let i = 0; i < nodes.length; i += 1) {
      for (let j = i + 1; j < nodes.length; j += 1) {
        const a = nodes[i];
        const b = nodes[j];
        const pa = positions.get(a.id);
        const pb = positions.get(b.id);
        let dx = pa.x - pb.x;
        let dy = pa.y - pb.y;
        let distanceSq = dx * dx + dy * dy;
        if (distanceSq < 0.01) {
          dx = seededRandom(`${a.id}:${b.id}:dx`) - 0.5;
          dy = seededRandom(`${a.id}:${b.id}:dy`) - 0.5;
          distanceSq = dx * dx + dy * dy;
        }
        const distance = Math.sqrt(distanceSq);
        const minDistance = nodeRadius(a) + nodeRadius(b) + (a.type === "target" || b.type === "target" ? 34 : 22);
        const repel = (charge * alpha) / Math.max(distanceSq, 140);
        const overlap = Math.max(0, minDistance - distance) * 0.16;
        const force = repel + overlap;
        const fx = (dx / distance) * force;
        const fy = (dy / distance) * force;
        velocities.get(a.id).x += fx;
        velocities.get(a.id).y += fy;
        velocities.get(b.id).x -= fx;
        velocities.get(b.id).y -= fy;
      }
    }

    edges.forEach((edge) => {
      const sourceNode = nodeById.get(edge.source);
      const targetNode = nodeById.get(edge.target);
      const source = positions.get(edge.source);
      const target = positions.get(edge.target);
      if (!sourceNode || !targetNode || !source || !target) return;
      const dx = target.x - source.x;
      const dy = target.y - source.y;
      const distance = Math.max(Math.hypot(dx, dy), 1);
      const desired = 150;
      const force = (distance - desired) * edgeStrength * alpha;
      const fx = (dx / distance) * force;
      const fy = (dy / distance) * force;
      velocities.get(edge.source).x += fx;
      velocities.get(edge.source).y += fy;
      velocities.get(edge.target).x -= fx;
      velocities.get(edge.target).y -= fy;
    });

    nodes.forEach((node) => {
      const anchor = anchorForNode(node, width, height);
      const pos = positions.get(node.id);
      velocities.get(node.id).x += (anchor.x - pos.x) * anchor.strength * alpha;
      velocities.get(node.id).y += (anchor.y - pos.y) * anchor.strength * alpha;
    });

    nodes.forEach((node) => {
      const velocity = velocities.get(node.id);
      const pos = positions.get(node.id);
      velocity.x *= 0.76;
      velocity.y *= 0.76;
      positions.set(node.id, {
        x: clamp(pos.x + clamp(velocity.x, -9, 9), 42, width - 42),
        y: clamp(pos.y + clamp(velocity.y, -9, 9), 42, height - 52),
      });
    });
  }

  return positions;
}

function layoutNodes(nodes, edges, width, height) {
  const positions = forceDirectedLayout(nodes, edges, width, height);
  nodes.forEach((node) => {
    if (!positions.has(node.id)) positions.set(node.id, { x: width / 2, y: height / 2 });
  });
  return positions;
}

function nodeRadius(node) {
  if (node.type === "target") return 24;
  return 15;
}

function nodeClass(node) {
  if (node.type === "target") return "target-node";
  return "artist-node";
}

function shortenLine(source, target, sourceRadius, targetRadius) {
  const dx = target.x - source.x;
  const dy = target.y - source.y;
  const length = Math.max(Math.hypot(dx, dy), 1);
  const sx = source.x + (dx / length) * (sourceRadius + 3);
  const sy = source.y + (dy / length) * (sourceRadius + 3);
  const tx = target.x - (dx / length) * (targetRadius + 9);
  const ty = target.y - (dy / length) * (targetRadius + 9);
  return { sx, sy, tx, ty, dx, dy, length };
}

function edgeCurve(edge, sourceNode, targetNode, source, target, index) {
  const line = shortenLine(source, target, nodeRadius(sourceNode), nodeRadius(targetNode));
  const samePairOffset = index === 0 ? 0 : (index % 2 === 0 ? -1 : 1) * Math.ceil(index / 2) * 10;
  const roleOffset = edge.role === "作词" ? -5 : edge.role === "作曲" ? 5 : 0;
  const curveOffset = samePairOffset + roleOffset;
  const nx = -line.dy / line.length;
  const ny = line.dx / line.length;
  const cx = (line.sx + line.tx) / 2 + nx * curveOffset;
  const cy = (line.sy + line.ty) / 2 + ny * curveOffset;
  const labelT = 0.5;
  const labelX = (1 - labelT) * (1 - labelT) * line.sx + 2 * (1 - labelT) * labelT * cx + labelT * labelT * line.tx;
  const labelY = (1 - labelT) * (1 - labelT) * line.sy + 2 * (1 - labelT) * labelT * cy + labelT * labelT * line.ty;
  return {
    path: `M ${line.sx.toFixed(1)} ${line.sy.toFixed(1)} Q ${cx.toFixed(1)} ${cy.toFixed(1)} ${line.tx.toFixed(1)} ${line.ty.toFixed(1)}`,
    labelX,
    labelY,
  };
}

function edgeParallelIndex(edges) {
  const pairCounts = new Map();
  const indexes = new Map();
  edges.forEach((edge) => {
    const key = `${edge.source}->${edge.target}`;
    const index = pairCounts.get(key) || 0;
    pairCounts.set(key, index + 1);
    indexes.set(edge.id, index);
  });
  return indexes;
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

function renderGraph() {
  const svg = $("graph");
  const width = svg.clientWidth || 960;
  const graph = buildGraph();
  let nodes = graph.nodes;
  let edges = graph.edges;

  if (state.search) {
    const matchingIds = new Set(nodes.filter(nodeMatches).map((node) => node.id));
    edges = edges.filter((edge) => matchingIds.has(edge.source) || matchingIds.has(edge.target));
    const connected = new Set(edges.flatMap((edge) => [edge.source, edge.target]));
    nodes = nodes.filter((node) => matchingIds.has(node.id) || connected.has(node.id));
  }

  const height = graphHeightFor(nodes, edges, width);
  svg.style.height = `${height}px`;
  const positions = layoutNodes(nodes, edges, width, height);
  const nodeById = new Map(nodes.map((node) => [node.id, node]));
  const edgeIndexes = edgeParallelIndex(edges);
  const degrees = nodeDegreeMap(edges);
  const marker =
    state.directionMode === "directed"
      ? `<defs>
          <marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="4" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,8 L11,4 z" fill="#475467"></path>
          </marker>
        </defs>`
      : "";
  const edgeMarkup = edges
    .map((edge) => {
      const source = positions.get(edge.source);
      const target = positions.get(edge.target);
      if (!source || !target) return "";
      const sourceNode = nodeById.get(edge.source);
      const targetNode = nodeById.get(edge.target);
      if (!sourceNode || !targetNode) return "";
      const curve = edgeCurve(edge, sourceNode, targetNode, source, target, edgeIndexes.get(edge.id) || 0);
      const className = roleClass[edge.role] || "role-merged";
      const selected = state.selected?.type === "edge" && state.selected.id === edge.id ? " selected" : "";
      const markerEnd = state.directionMode === "directed" && selected ? ' marker-end="url(#arrow)"' : "";
      const label = selected
        ? `<text class="edge-label" x="${curve.labelX}" y="${curve.labelY - 5}">${escapeHtml(edge.role)} · ${formatNumber(edge.song_count)}</text>`
        : "";
      return `
        <g data-edge-id="${escapeHtml(edge.id)}">
          <path class="edge ${className}${selected}" d="${curve.path}"${markerEnd}></path>
          ${label}
        </g>
      `;
    })
    .join("");
  const nodeMarkup = nodes
    .map((node) => {
      const pos = positions.get(node.id);
      const selected = state.selected?.type === "node" && state.selected.id === node.id ? " selected" : "";
      const radius = nodeRadius(node);
      const labelOffset = 30;
      const showLabel = shouldShowNodeLabel(node, degrees.get(node.id) || 0, Boolean(selected));
      return `
        <g class="node${selected}" data-node-id="${escapeHtml(node.id)}" transform="translate(${pos.x},${pos.y})">
          <circle class="${nodeClass(node)}" r="${radius}"></circle>
          ${showLabel ? `<text text-anchor="middle" y="${labelOffset}">${escapeHtml(node.name)}</text>` : ""}
        </g>
      `;
    })
    .join("");

  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.innerHTML = `${marker}<g>${edgeMarkup}</g><g>${nodeMarkup}</g>`;
  svg.querySelectorAll("[data-node-id]").forEach((element) => {
    element.addEventListener("click", () => {
      state.selected = { type: "node", id: element.dataset.nodeId };
      renderGraph();
      renderDetail();
    });
  });
  svg.querySelectorAll("[data-edge-id]").forEach((element) => {
    element.addEventListener("click", () => {
      state.selected = { type: "edge", id: element.dataset.edgeId };
      renderGraph();
      renderDetail();
    });
  });

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
