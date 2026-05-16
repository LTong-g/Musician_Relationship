import sqlite3
import unittest

from music_metadata_graph.visualization.build_static_graph import JS, build_graph_data, html_document, normalize_icon_url, safe_script_json
from music_metadata_graph.visualization.build_large_graph_static import LARGE_GRAPH_JS, large_graph_html_document


class StaticGraphBuildTests(unittest.TestCase):
    def test_build_graph_data_excludes_self_edges(self):
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        self.addCleanup(connection.close)
        connection.executescript(
            """
            CREATE TABLE artists (
                mid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                area_id INTEGER,
                other_name TEXT NOT NULL DEFAULT '',
                icon TEXT NOT NULL DEFAULT '',
                spell TEXT NOT NULL DEFAULT '',
                raw_json_path TEXT NOT NULL DEFAULT '',
                raw_page INTEGER NOT NULL DEFAULT 0,
                raw_row_index INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE albums (
                mid TEXT PRIMARY KEY,
                id INTEGER NOT NULL UNIQUE,
                name TEXT NOT NULL,
                albumType TEXT NOT NULL,
                publishDate TEXT NOT NULL,
                raw_json_path TEXT NOT NULL DEFAULT '',
                raw_page INTEGER NOT NULL DEFAULT 0,
                raw_row_index INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE songs (
                mid TEXT PRIMARY KEY,
                id INTEGER NOT NULL UNIQUE,
                name TEXT NOT NULL,
                title TEXT NOT NULL,
                language INTEGER NOT NULL,
                album_mid TEXT NOT NULL
            );
            CREATE TABLE song_singers (
                song_mid TEXT NOT NULL,
                singer_order INTEGER NOT NULL,
                singer_mid TEXT NOT NULL,
                PRIMARY KEY(song_mid, singer_order)
            );
            CREATE TABLE song_credit_artists (
                song_mid TEXT NOT NULL,
                role TEXT NOT NULL,
                artist_order INTEGER NOT NULL,
                artist_mid TEXT NOT NULL,
                PRIMARY KEY(song_mid, role, artist_order)
            );
            INSERT INTO artists(mid, name, icon) VALUES
                ('singer_mid', 'Singer', 'https://example.test/singer.jpg'),
                ('writer_mid', 'Writer', '');
            INSERT INTO albums(mid, id, name, albumType, publishDate)
                VALUES ('album_mid', 1, 'Album', 'Single', '2026-01-01');
            INSERT INTO songs(mid, id, name, title, language, album_mid)
                VALUES ('song_mid', 100, 'Song', 'Song', 0, 'album_mid');
            INSERT INTO song_singers(song_mid, singer_order, singer_mid)
                VALUES ('song_mid', 0, 'singer_mid');
            INSERT INTO song_credit_artists(song_mid, role, artist_order, artist_mid) VALUES
                ('song_mid', '作词', 0, 'writer_mid'),
                ('song_mid', '作曲', 0, 'singer_mid');
            """
        )

        data = build_graph_data(connection)

        self.assertEqual(data["summary"]["songs"], 1)
        self.assertEqual(len(data["songs"]), 1)
        self.assertEqual(len(data["nodes"]), 2)
        self.assertEqual(data["targets"], [
            {
                "id": "artist:singer_mid",
                "mid": "singer_mid",
                "name": "Singer",
                "icon": "https://example.test/singer.jpg",
                "song_count": 1,
            }
        ])
        nodes = {node["id"]: node for node in data["nodes"]}
        self.assertEqual(nodes["artist:singer_mid"]["sung_song_count"], 1)
        self.assertEqual(nodes["artist:singer_mid"]["composer_song_count"], 1)
        self.assertEqual(nodes["artist:writer_mid"]["lyricist_song_count"], 1)
        edge_ids = {edge["id"] for edge in data["edges"]}
        self.assertIn("artist:writer_mid->artist:singer_mid:作词", edge_ids)
        self.assertNotIn("artist:singer_mid->artist:singer_mid:作曲", edge_ids)

    def test_safe_script_json_escapes_script_close(self):
        payload = safe_script_json({"title": "before </script> after"})

        self.assertNotIn("</script>", payload.lower())
        self.assertIn("<\\/script>", payload)

    def test_normalize_icon_url_upgrades_http(self):
        self.assertEqual(
            normalize_icon_url("http://y.gtimg.cn/music/photo_new/example.jpg"),
            "https://y.gtimg.cn/music/photo_new/example.jpg",
        )
        self.assertEqual(
            normalize_icon_url("https://y.qq.com/music/photo_new/example.jpg"),
            "https://y.qq.com/music/photo_new/example.jpg",
        )

    def test_graph_labels_default_off_with_click_highlight(self):
        self.assertIn("showLabels: false", JS)
        self.assertIn("highlightNodes", JS)
        self.assertIn("highlightLinks", JS)
        self.assertIn("selectedNodeIds: new Set()", JS)
        self.assertIn(".onNodeClick", JS)
        self.assertIn(".onLinkClick", JS)
        self.assertIn("toggleNodeSelection(node, event)", JS)
        self.assertIn("const multiSelect = Boolean(event?.ctrlKey || event?.metaKey)", JS)
        self.assertIn("state.selectedNodeIds.clear();", JS)
        self.assertIn("function setNodeSelectionHighlight", JS)
        self.assertIn("state.selected = { type: \"nodes\" }", JS)
        self.assertIn("state.selectedNodeIds.has(source) && state.selectedNodeIds.has(target)", JS)
        self.assertIn("const selectedEdges = currentGraph.edges.filter((edge) => highlightLinks.has(edge.id))", JS)
        self.assertIn("renderSongList(edge.songs || [])", JS)
        self.assertIn("setLinkHighlight(edge)", JS)
        self.assertIn("particlesEnabled: false", JS)
        self.assertIn("particle-toggle", html_document("测试", {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}}, ""))
        self.assertIn("function drawDirectionalParticles", JS)
        self.assertIn("function edgeCurvePoint", JS)
        self.assertIn("const controlX = (source.x + target.x) / 2 + dy * curvature", JS)
        self.assertIn("const radius = 2.2;", JS)
        self.assertIn("const t = sourceId === nodeId(edge.__particleDirectionSource) ? progress : 1 - progress", JS)
        self.assertIn(".linkCanvasObject(drawDirectionalParticles)", JS)
        self.assertIn(".linkCanvasObjectMode(() => \"after\")", JS)
        self.assertIn(".linkDirectionalParticles(0)", JS)
        self.assertIn("direction.source", JS)
        self.assertIn("direction.target", JS)
        self.assertIn("renderSelection()", JS)
        self.assertNotIn("graphInstance.graphData(graphInstance.graphData())", JS)
        self.assertNotIn("graphInstance.refresh()", JS)
        self.assertNotIn("directionMode", JS)
        self.assertNotIn("direction-mode", html_document("测试", {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}}, ""))
        self.assertNotIn(".onNodeHover", JS)
        self.assertNotIn(".onLinkHover", JS)
        self.assertNotIn(".centerAt(", JS)
        self.assertNotIn("includeSelfEdges", JS)
        self.assertNotIn("self-toggle", JS)

    def test_target_filter_controls_exist(self):
        self.assertIn("selectedTargets", JS)
        self.assertIn("targetItems()", JS)
        self.assertIn("renderTargetCheckboxes", JS)
        self.assertIn("target-dropdown-toggle", JS)
        self.assertIn("target-select-all", JS)
        self.assertIn("target-invert", JS)

    def test_text_node_and_detail_behaviors_exist(self):
        html = html_document("测试", {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}}, "")
        self.assertIn("function drawTextNode", JS)
        self.assertIn("function textNodeMetrics", JS)
        self.assertIn("if (state.showLabels)", JS)
        self.assertIn("detailPanel.style.height", JS)
        self.assertIn("lyricist_song_count", JS)
        self.assertIn("composer_song_count", JS)
        self.assertIn("Math.min(65, 7 + Math.sqrt(degree || 1) * 2.2)", JS)
        self.assertIn("Math.max(10, Math.min(65, node.val || 12))", JS)
        self.assertIn("let currentEdgeWeightScale = { min: 1, max: 1 }", JS)
        self.assertIn("function updateEdgeWeightScale", JS)
        self.assertIn("function edgeWeightRatio", JS)
        self.assertIn("directions: new Map()", JS)
        self.assertIn("nodeName(direction.source)} -> ${nodeName(direction.target)", JS)
        self.assertIn("function directionLabels", JS)
        self.assertIn("const roles = (direction.roles || []).join", JS)
        self.assertIn("formatNumber(direction.song_count)", JS)
        self.assertIn('if (hasActiveHighlight() && !isHighlightedLink(edge)) return "";', JS)
        self.assertIn("return directionLabels(edge).join(\"<br>\")", JS)
        self.assertIn("buildGraph().edges.flatMap", JS)
        self.assertIn("source: nodeName(direction.source)", JS)
        self.assertIn("target: nodeName(direction.target)", JS)
        self.assertIn("count: direction.song_count", JS)
        self.assertNotIn("source: nodeName(edge.source)", JS)
        self.assertNotIn("target: nodeName(edge.target)", JS)
        self.assertNotIn("return `${edge.role} · ${formatNumber(edge.song_count)} 首", JS)
        self.assertIn("return 1 + edgeWeightRatio(edge) * 4", JS)
        self.assertIn("if (isHighlightedLink(edge)) return 1", JS)
        self.assertIn("const alpha = 0.05 + edgeWeightRatio(edge) * 0.95", JS)
        self.assertIn("return hasActiveHighlight() ? alpha * 0.5 : alpha", JS)
        self.assertIn("updateEdgeWeightScale(graph.edges)", JS)
        self.assertIn("rgba(31, 120, 180, ${alpha})", JS)
        self.assertIn("rgba(217, 95, 2, ${alpha})", JS)
        self.assertIn("rgba(20, 132, 117, ${alpha})", JS)
        self.assertIn("ctx.lineWidth = selected || highlighted ? 0.65 / globalScale", JS)
        self.assertIn("radius + 0.6 / globalScale", JS)
        self.assertIn("role-split-toggle", html)
        self.assertNotIn("role-display", html)
        self.assertNotIn("Math.sqrt(edge.song_count || 1) * 0.38", JS)
        self.assertNotIn("rgba(239, 246, 255", JS)

    def test_large_graph_variant_keeps_mvp_shell_but_mirrors_official_drawing_area(self):
        graph_data = {
            "nodes": [{"id": "artist:a", "name": "A"}, {"id": "artist:b", "name": "B"}],
            "edges": [{"source": "artist:a", "target": "artist:b", "role": "作词"}],
            "songs": [],
            "targets": [],
            "summary": {},
        }
        html = large_graph_html_document("测试", graph_data, "")

        self.assertIn("topbar", html)
        self.assertIn("detail-panel", html)
        self.assertIn("target-dropdown-toggle", html)
        self.assertIn("window.devicePixelRatio = 1; // use standard resolution in retina displays", LARGE_GRAPH_JS)
        self.assertIn("graphInstance = new ForceGraph(container)", LARGE_GRAPH_JS)
        self.assertIn("api.graphData(graphPayload(graph.nodes, graph.edges))", LARGE_GRAPH_JS)
        self.assertIn(".d3AlphaDecay(0)", LARGE_GRAPH_JS)
        self.assertIn(".d3VelocityDecay(0.08)", LARGE_GRAPH_JS)
        self.assertIn(".cooldownTime(60000)", LARGE_GRAPH_JS)
        self.assertIn(".linkColor(() => 'rgba(0,0,0,0.05)')", LARGE_GRAPH_JS)
        self.assertIn(".zoom(0.05)", LARGE_GRAPH_JS)
        self.assertIn(".enablePointerInteraction(true)", LARGE_GRAPH_JS)
        self.assertNotIn(".nodeCanvasObject(", LARGE_GRAPH_JS)
        self.assertNotIn(".nodePointerAreaPaint(", LARGE_GRAPH_JS)
        self.assertNotIn(".nodeAutoColorBy(", LARGE_GRAPH_JS)
        self.assertNotIn(".linkCanvasObject(", LARGE_GRAPH_JS)
        self.assertNotIn(".linkDirectionalParticles(", LARGE_GRAPH_JS)
        self.assertNotIn("api.zoomToFit", LARGE_GRAPH_JS)
        self.assertNotIn("api.d3Force(\"link\")", LARGE_GRAPH_JS)
        self.assertNotIn("api.d3Force(\"charge\")", LARGE_GRAPH_JS)


if __name__ == "__main__":
    unittest.main()
