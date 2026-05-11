const state = {
  catalog: null,
  datasets: new Map(),
  currentSlug: "",
  viewMode: "artist",
  edgeMode: "typed",
  directionMode: "directed",
  minCount: 1,
  search: "",
  activeTab: "songs",
  selected: null,
};

const roleClass = {
  作词: "role-lyric",
  作曲: "role-compose",
  合并: "role-merged",
};

const $ = (id) => document.getElementById(id);

async function loadJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`Cannot load ${path}: ${response.status}`);
  }
  return response.json();
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

async function init() {
  try {
    state.catalog = await loadJson("data/catalog.json");
    await Promise.all(
      state.catalog.datasets.map(async (item) => {
        const dataset = await loadJson(`data/${item.file}`);
        state.datasets.set(item.slug, dataset);
      }),
    );
    state.currentSlug = state.catalog.datasets[0]?.slug || "";
    bindControls();
    render();
  } catch (error) {
    $("dataset-scope").textContent = "数据加载失败";
    $("detail-content").innerHTML = `<div class="detail-card">${escapeHtml(error.message)}</div>`;
  }
}

function bindControls() {
  const datasetSelect = $("dataset-select");
  datasetSelect.innerHTML = state.catalog.datasets
    .map((item) => `<option value="${escapeHtml(item.slug)}">${escapeHtml(item.name)}</option>`)
    .join("");
  datasetSelect.value = state.currentSlug;
  datasetSelect.addEventListener("change", () => {
    state.currentSlug = datasetSelect.value;
    state.selected = null;
    render();
  });

  $("view-mode").addEventListener("change", (event) => {
    state.viewMode = event.target.value;
    state.selected = null;
    render();
  });
  $("edge-mode").addEventListener("change", (event) => {
    state.edgeMode = event.target.value;
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

function currentDataset() {
  return state.datasets.get(state.currentSlug);
}

function render() {
  const dataset = currentDataset();
  if (!dataset) return;
  $("dataset-scope").textContent =
    `当前覆盖 ${state.catalog.totals.datasets} 个目标歌手，` +
    `${formatNumber(state.catalog.totals.songs)} 首可视化歌曲，` +
    `${formatNumber(state.catalog.totals.credit_incomplete)} 首制作人员不完整条目已隔离。`;
  renderSummary(dataset);
  renderGraph();
  renderDetail();
  renderTable();
}

function renderSummary(dataset) {
  const summary = dataset.summary;
  const metrics = [
    ["可视化歌曲", summary.songs],
    ["贡献者节点", summary.contributors],
    ["关系边", summary.edges],
    ["自作词歌曲", summary.self_lyricist_songs],
    ["自作曲歌曲", summary.self_composer_songs],
    ["隔离条目", summary.credit_incomplete],
  ];
  $("summary-strip").innerHTML = metrics
    .map(([label, value]) => `<div class="metric"><span>${label}</span><strong>${formatNumber(value)}</strong></div>`)
    .join("");
}

function nodeMatches(node) {
  if (!state.search) return true;
  return String(node.name || "").toLowerCase().includes(state.search);
}

function buildArtistGraph(dataset) {
  const nodes = new Map(dataset.graph.nodes.map((node) => [node.id, { ...node }]));
  let edges = dataset.graph.edges.filter((edge) => edge.song_count >= state.minCount);
  if (state.edgeMode === "merged") {
    const merged = new Map();
    for (const edge of edges) {
      const key = `${edge.source}->${edge.target}`;
      const current = merged.get(key) || {
        id: key,
        source: edge.source,
        target: edge.target,
        role: "合并",
        roles: [],
        song_count: 0,
        songs: [],
      };
      current.roles.push(edge.role);
      current.song_count += edge.song_count;
      current.songs.push(...edge.songs.map((song) => ({ ...song, role: edge.role })));
      merged.set(key, current);
    }
    edges = [...merged.values()].filter((edge) => edge.song_count >= state.minCount);
  }
  return { nodes: [...nodes.values()], edges };
}

function buildSongGraph(dataset) {
  const nodes = new Map();
  const target = dataset.graph.nodes.find((node) => node.type === "target");
  if (target) nodes.set(target.id, { ...target });
  const songsById = new Map(dataset.graph.song_nodes.map((song) => [song.id, song]));
  const artistNodes = new Map(dataset.graph.nodes.filter((node) => node.type === "artist").map((node) => [node.id, node]));
  const edges = [];

  for (const edge of dataset.graph.edges.filter((item) => item.song_count >= state.minCount)) {
    for (const song of edge.songs) {
      const songId = song.mid ? `song:${song.mid}` : song.id != null ? `song:id:${song.id}` : "";
      if (!songId || !songsById.has(songId)) continue;
      const artist = artistNodes.get(edge.source);
      if (!artist) continue;
      nodes.set(artist.id, { ...artist });
      nodes.set(songId, { ...songsById.get(songId) });
      edges.push({
        id: `${edge.source}->${songId}:${edge.role}`,
        source: edge.source,
        target: songId,
        role: edge.role,
        song_count: 1,
        songs: [song],
      });
      if (target) {
        edges.push({
          id: `${songId}->${target.id}`,
          source: songId,
          target: target.id,
          role: "合并",
          song_count: 1,
          songs: [song],
        });
      }
    }
  }
  return { nodes: [...nodes.values()], edges };
}

function buildBridgeGraph() {
  const nodes = new Map();
  const edges = [];
  for (const dataset of state.datasets.values()) {
    const target = dataset.graph.nodes.find((node) => node.type === "target");
    if (target) nodes.set(target.id, { ...target });
  }
  for (const bridge of state.catalog.bridge_contributors) {
    if (bridge.target_count < state.minCount) continue;
    nodes.set(bridge.id, {
      id: bridge.id,
      type: "artist",
      name: bridge.name,
    });
    for (const slug of bridge.target_slugs) {
      const target = [...nodes.values()].find((node) => node.type === "target" && node.slug === slug);
      if (!target) continue;
      edges.push({
        id: `${bridge.id}->${target.id}`,
        source: bridge.id,
        target: target.id,
        role: "合并",
        song_count: 1,
        songs: [],
      });
    }
  }
  return { nodes: [...nodes.values()], edges };
}

function buildGraph() {
  const dataset = currentDataset();
  if (state.viewMode === "song") return buildSongGraph(dataset);
  if (state.viewMode === "bridge") return buildBridgeGraph();
  return buildArtistGraph(dataset);
}

function layoutNodes(nodes, edges, width, height) {
  const centerX = width / 2;
  const centerY = height / 2;
  const targetNodes = nodes.filter((node) => node.type === "target");
  const songNodes = nodes.filter((node) => node.type === "song");
  const artistNodes = nodes.filter((node) => node.type === "artist");
  const positions = new Map();

  if (targetNodes.length === 1) {
    positions.set(targetNodes[0].id, { x: centerX, y: centerY });
  } else {
    placeRing(targetNodes, centerX, centerY, Math.min(width, height) * 0.22, positions, -Math.PI / 2);
  }

  if (state.viewMode === "song") {
    placeRing(songNodes, centerX, centerY, Math.min(width, height) * 0.25, positions, -Math.PI / 2);
    placeRing(artistNodes, centerX, centerY, Math.min(width, height) * 0.42, positions, -Math.PI / 2);
  } else {
    placeRing(artistNodes, centerX, centerY, Math.min(width, height) * 0.38, positions, -Math.PI / 2);
    placeRing(songNodes, centerX, centerY, Math.min(width, height) * 0.28, positions, -Math.PI / 2);
  }

  for (const node of nodes) {
    if (!positions.has(node.id)) {
      positions.set(node.id, { x: centerX, y: centerY });
    }
  }
  return positions;
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

function renderGraph() {
  const svg = $("graph");
  const width = svg.clientWidth || 900;
  const height = svg.clientHeight || 550;
  const graph = buildGraph();
  let nodes = graph.nodes;
  let edges = graph.edges;

  if (state.search) {
    const matchingIds = new Set(nodes.filter(nodeMatches).map((node) => node.id));
    edges = edges.filter((edge) => matchingIds.has(edge.source) || matchingIds.has(edge.target));
    const connected = new Set(edges.flatMap((edge) => [edge.source, edge.target]));
    nodes = nodes.filter((node) => matchingIds.has(node.id) || connected.has(node.id));
  }

  const positions = layoutNodes(nodes, edges, width, height);
  const marker = state.directionMode === "directed"
    ? `<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#667085"></path></marker></defs>`
    : "";
  const edgeMarkup = edges
    .map((edge) => {
      const source = positions.get(edge.source);
      const target = positions.get(edge.target);
      if (!source || !target) return "";
      const role = state.edgeMode === "merged" ? "合并" : edge.role;
      const className = roleClass[role] || "role-merged";
      const selected = state.selected?.type === "edge" && state.selected.id === edge.id ? " selected" : "";
      const markerEnd = state.directionMode === "directed" ? ' marker-end="url(#arrow)"' : "";
      const labelX = (source.x + target.x) / 2;
      const labelY = (source.y + target.y) / 2;
      return `
        <g data-edge-id="${escapeHtml(edge.id)}">
          <line class="edge ${className}${selected}" x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}"${markerEnd}></line>
          <text class="edge-label" x="${labelX}" y="${labelY - 5}">${escapeHtml(role)} · ${edge.song_count}</text>
        </g>
      `;
    })
    .join("");
  const nodeMarkup = nodes
    .map((node) => {
      const pos = positions.get(node.id);
      const selected = state.selected?.type === "node" && state.selected.id === node.id ? " selected" : "";
      const radius = node.type === "target" ? 22 : node.type === "song" ? 9 : 14;
      const className = node.type === "target" ? "target-node" : node.type === "song" ? "song-node" : "artist-node";
      const labelOffset = node.type === "song" ? 20 : 28;
      return `
        <g class="node${selected}" data-node-id="${escapeHtml(node.id)}" transform="translate(${pos.x},${pos.y})">
          <circle class="${className}" r="${radius}"></circle>
          <text text-anchor="middle" y="${labelOffset}">${escapeHtml(node.name)}</text>
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
  $("graph-title").textContent = modeLabel;
  $("graph-note").textContent = edges.length
    ? `${nodes.length} 个节点，${edges.length} 条边`
    : `${nodes.length} 个孤立节点，当前筛选下暂无连边`;
}

function findSelected() {
  if (!state.selected) return null;
  const graph = buildGraph();
  if (state.selected.type === "node") {
    return graph.nodes.find((node) => node.id === state.selected.id);
  }
  return graph.edges.find((edge) => edge.id === state.selected.id);
}

function renderDetail() {
  const dataset = currentDataset();
  const item = findSelected();
  if (!item) {
    $("detail-content").innerHTML = `
      <div class="detail-card">
        <strong>${escapeHtml(dataset.name)}</strong>
        <p class="muted">选择节点或边查看支撑歌曲。当前图谱即使没有边，也会保留孤立节点。</p>
      </div>
    `;
    return;
  }
  if (state.selected.type === "edge") {
    $("detail-content").innerHTML = `
      <div class="detail-card">
        <strong>${escapeHtml(item.role)} · ${formatNumber(item.song_count)} 首</strong>
        <p class="muted">${escapeHtml(item.source)} -> ${escapeHtml(item.target)}</p>
      </div>
      ${renderSongList(item.songs || [])}
    `;
    return;
  }
  const relatedSongs = dataset.songs.filter((song) => {
    const names = [...(song.lyricists || []), ...(song.composers || [])];
    return names.includes(item.name) || song.target === item.name || song.name === item.name;
  });
  $("detail-content").innerHTML = `
    <div class="detail-card">
      <strong>${escapeHtml(item.name)}</strong>
      <p class="muted">${escapeHtml(item.type)}${item.mid ? ` · ${escapeHtml(item.mid)}` : ""}</p>
    </div>
    ${renderSongList(relatedSongs.slice(0, 30))}
  `;
}

function renderSongList(songs) {
  if (!songs.length) {
    return `<div class="detail-card muted">暂无支撑歌曲。</div>`;
  }
  return songs
    .map((song) => `<div class="detail-card"><strong>${escapeHtml(song.name)}</strong><p class="muted">${escapeHtml(song.album || "")}</p></div>`)
    .join("");
}

function renderTable() {
  const dataset = currentDataset();
  if (state.activeTab === "edges") {
    const rows = dataset.graph.edges.map((edge) => ({
      role: edge.role,
      source: getNodeName(dataset, edge.source),
      target: getNodeName(dataset, edge.target),
      count: edge.song_count,
      songs: edge.songs.map((song) => song.name).join(" / "),
    }));
    renderRows(["职能", "贡献者", "目标", "歌曲数", "支撑歌曲"], rows, ["role", "source", "target", "count", "songs"]);
    return;
  }
  if (state.activeTab === "quality") {
    const rows = Object.entries(dataset.quality.credit_filter_reason_counts || {}).map(([reason, count]) => ({ reason, count }));
    renderRows(["状态", "数量"], rows, ["reason", "count"]);
    return;
  }
  renderRows(
    ["歌曲", "专辑", "作词", "作曲", "目标歌手"],
    dataset.songs,
    ["name", "album", "lyricists", "composers", "target"],
  );
}

function getNodeName(dataset, id) {
  return dataset.graph.nodes.find((node) => node.id === id)?.name || id;
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
