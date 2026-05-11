const state = {
  catalog: null,
  targetData: new Map(),
  currentTarget: "all",
  viewMode: "artist",
  roleDisplay: "split",
  directionMode: "directed",
  minCount: 1,
  search: "",
  activeTab: "songs",
  selected: null,
};

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

function targetFiles() {
  return catalogTargets().map((item) => item.file);
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
  const metrics = [
    ["目标歌手", state.currentTarget === "all" ? targets.length : 1],
    ["可视化歌曲", summary.songs],
    ["贡献者", countUniqueContributors(targets)],
    ["关系边", buildArtistGraph().edges.length],
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
  edges = mergeEdges(edges).filter((edge) => edge.song_count >= state.minCount);
  const usedNodeIds = new Set(edges.flatMap((edge) => [edge.source, edge.target]));
  nodes.forEach((node) => {
    if (node.type === "target") usedNodeIds.add(node.id);
  });
  return { nodes: [...nodes.values()].filter((node) => usedNodeIds.has(node.id)), edges };
}

function buildSongGraph() {
  const nodes = new Map();
  const edges = [];
  selectedTargets().forEach((dataset) => {
    const target = dataset.graph.nodes.find((node) => node.type === "target");
    const songsById = new Map(dataset.graph.song_nodes.map((song) => [song.id, song]));
    const artistNodes = new Map(dataset.graph.nodes.filter((node) => node.type === "artist").map((node) => [node.id, node]));
    if (target) addNode(nodes, target);
    dataset.graph.edges
      .filter((edge) => edge.song_count >= state.minCount)
      .forEach((edge) => {
        (edge.songs || []).forEach((song) => {
          const songId = song.mid ? `song:${song.mid}` : song.id != null ? `song:id:${song.id}` : "";
          const songNode = songsById.get(songId);
          const artist = artistNodes.get(edge.source);
          if (!songNode || !artist) return;
          addNode(nodes, artist);
          addNode(nodes, { ...songNode, target_name: dataset.name });
          edges.push({
            id: `${edge.source}->${songId}:${edge.role}`,
            source: edge.source,
            target: songId,
            role: edge.role,
            song_count: 1,
            songs: [{ ...song, role: edge.role, target: dataset.name, target_slug: dataset.slug }],
          });
          if (target) {
            edges.push({
              id: `${songId}->${target.id}`,
              source: songId,
              target: target.id,
              role: "合作",
              song_count: 1,
              songs: [{ ...song, target: dataset.name, target_slug: dataset.slug }],
            });
          }
        });
      });
  });
  return { nodes: [...nodes.values()], edges: state.roleDisplay === "merged" ? mergeEdges(edges) : edges };
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
  if (state.viewMode === "song") return buildSongGraph();
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

function layoutNodes(nodes, width, height) {
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
    placeRing(songNodes, centerX, centerY, Math.min(width, height) * 0.31, positions, -Math.PI / 2);
    placeRing(artistNodes, centerX, centerY, Math.min(width, height) * 0.45, positions, -Math.PI / 2);
  } else {
    placeRing(artistNodes, centerX, centerY, Math.min(width, height) * 0.42, positions, -Math.PI / 2);
    placeRing(songNodes, centerX, centerY, Math.min(width, height) * 0.3, positions, -Math.PI / 2);
  }
  nodes.forEach((node) => {
    if (!positions.has(node.id)) positions.set(node.id, { x: centerX, y: centerY });
  });
  return positions;
}

function nodeRadius(node) {
  if (node.type === "target") return 24;
  if (node.type === "song") return 8;
  return 15;
}

function nodeClass(node) {
  if (node.type === "target") return "target-node";
  if (node.type === "song") return "song-node";
  return "artist-node";
}

function renderGraph() {
  const svg = $("graph");
  const width = svg.clientWidth || 960;
  const height = svg.clientHeight || 560;
  const graph = buildGraph();
  let nodes = graph.nodes;
  let edges = graph.edges;

  if (state.search) {
    const matchingIds = new Set(nodes.filter(nodeMatches).map((node) => node.id));
    edges = edges.filter((edge) => matchingIds.has(edge.source) || matchingIds.has(edge.target));
    const connected = new Set(edges.flatMap((edge) => [edge.source, edge.target]));
    nodes = nodes.filter((node) => matchingIds.has(node.id) || connected.has(node.id));
  }

  const positions = layoutNodes(nodes, width, height);
  const marker =
    state.directionMode === "directed"
      ? `<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#667085"></path></marker></defs>`
      : "";
  const edgeMarkup = edges
    .map((edge) => {
      const source = positions.get(edge.source);
      const target = positions.get(edge.target);
      if (!source || !target) return "";
      const className = roleClass[edge.role] || "role-merged";
      const selected = state.selected?.type === "edge" && state.selected.id === edge.id ? " selected" : "";
      const markerEnd = state.directionMode === "directed" ? ' marker-end="url(#arrow)"' : "";
      const labelX = (source.x + target.x) / 2;
      const labelY = (source.y + target.y) / 2;
      return `
        <g data-edge-id="${escapeHtml(edge.id)}">
          <line class="edge ${className}${selected}" x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}"${markerEnd}></line>
          <text class="edge-label" x="${labelX}" y="${labelY - 5}">${escapeHtml(edge.role)} · ${formatNumber(edge.song_count)}</text>
        </g>
      `;
    })
    .join("");
  const nodeMarkup = nodes
    .map((node) => {
      const pos = positions.get(node.id);
      const selected = state.selected?.type === "node" && state.selected.id === node.id ? " selected" : "";
      const radius = nodeRadius(node);
      const labelOffset = node.type === "song" ? 19 : 30;
      return `
        <g class="node${selected}" data-node-id="${escapeHtml(node.id)}" transform="translate(${pos.x},${pos.y})">
          <circle class="${nodeClass(node)}" r="${radius}"></circle>
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
  $("graph-title").textContent = `${modeLabel} · ${currentScopeLabel()}`;
  $("graph-note").textContent = edges.length
    ? `${formatNumber(nodes.length)} 个节点，${formatNumber(edges.length)} 条边 · ${roleLabels[state.roleDisplay]}`
    : `${formatNumber(nodes.length)} 个节点，当前筛选下暂无连边`;
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
