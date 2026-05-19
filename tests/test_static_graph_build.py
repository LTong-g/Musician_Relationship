import io
import json
import sqlite3
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from music_metadata_graph.pipelines import prepare_static_graph_assets
from PIL import Image
from music_metadata_graph.pipelines.avatar_assets import avatar_key
from music_metadata_graph.pipelines.build_avatar_atlas import (
    DEFAULT_FINGERPRINT_FILE,
    AtlasConfig,
    build_atlas,
    check_existing_atlas,
)
from music_metadata_graph.pipelines.build_static_graph import (
    JS,
    build_graph_data,
    graph_data_script,
    html_document,
    normalize_icon_url,
    safe_script_json,
)
from music_metadata_graph.pipelines.build_large_graph_static import (
    LARGE_GRAPH_JS,
    large_graph_html_document,
)
from music_metadata_graph.pipelines.prepare_static_graph_assets import (
    DEFAULT_VENDOR_PATH,
    PrepareAssetsConfig,
    avatar_filename,
    collect_icon_urls,
    prepare_avatar_cache,
    rewrite_icons_to_avatar_keys,
    rewrite_icons_to_local,
    save_manifest,
)


class StaticGraphBuildTests(unittest.TestCase):
    def make_avatar_atlas_fixture(
        self, root: Path, url_count: int = 5
    ) -> tuple[AtlasConfig, list[str], Path]:
        avatar_cache_dir = root / "raw_avatar_cache"
        avatar_dir = avatar_cache_dir / "avatars"
        avatar_dir.mkdir(parents=True)
        urls = [f"https://example.test/{index}.jpg" for index in range(url_count)]
        manifest = {"avatars": {}}
        for index, url in enumerate(urls):
            filename = f"{index}.jpg"
            Image.new("RGB", (180 + index, 160 + index), (index * 30, 80, 140)).save(
                avatar_dir / filename, format="JPEG"
            )
            manifest["avatars"][url] = {"status": "ok", "local_path": f"avatars/{filename}"}
        save_manifest(avatar_cache_dir / "avatar-manifest.json", manifest)

        def write_graph(path: Path, selected_urls: list[str], profile: str) -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            graph_data = {
                "avatar_profile": profile,
                "nodes": [
                    {"id": f"artist:{index}", "avatar_key": avatar_key(url), "icon": ""}
                    for index, url in enumerate(selected_urls)
                ],
                "targets": [],
                "edges": [],
                "songs": [],
                "summary": {},
            }
            path.write_text(graph_data_script(graph_data), encoding="utf-8", newline="\n")

        mvp_graph = root / "site_mvp" / "assets" / "graph-data.js"
        demo_graph = root / "site_demo" / "assets" / "graph-data.js"
        full_graph = root / "site" / "assets" / "graph-data.js"
        write_graph(mvp_graph, urls[:1], "mvp")
        write_graph(demo_graph, urls[:2], "demo")
        write_graph(full_graph, urls, "full")

        output_dir = root / "site_assets" / "avatar_atlas_150"
        config = AtlasConfig(
            avatar_cache_dir=avatar_cache_dir,
            output_dir=output_dir,
            graph_data_by_profile={"mvp": mvp_graph, "demo": demo_graph, "full": full_graph},
            cell_size=150,
            atlas_size=300,
            webp_quality=80,
            include_unused_cache=False,
            legacy_avatar_cache_dir=None,
        )
        return config, urls, output_dir

    def test_build_graph_data_excludes_self_edges(self):
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        self.addCleanup(connection.close)
        connection.executescript("""
            CREATE TABLE artists (
                mid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                area_id INTEGER,
                fans_num INTEGER,
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
            INSERT INTO artists(mid, name, fans_num, icon) VALUES
                ('singer_mid', 'Singer', 123456, 'https://example.test/singer.jpg'),
                ('writer_mid', 'Writer', 234567, '');
            INSERT INTO albums(mid, id, name, albumType, publishDate)
                VALUES ('album_mid', 1, 'Album', 'Single', '2026-01-01');
            INSERT INTO songs(mid, id, name, title, language, album_mid)
                VALUES ('song_mid', 100, 'Song', 'Song', 0, 'album_mid');
            INSERT INTO song_singers(song_mid, singer_order, singer_mid)
                VALUES ('song_mid', 0, 'singer_mid');
            INSERT INTO song_credit_artists(song_mid, role, artist_order, artist_mid) VALUES
                ('song_mid', '作词', 0, 'writer_mid'),
                ('song_mid', '作曲', 0, 'singer_mid');
            """)
        data = build_graph_data(connection)
        self.assertEqual(data["summary"]["songs"], 1)
        self.assertEqual(len(data["songs"]), 1)
        self.assertEqual(len(data["nodes"]), 2)
        self.assertEqual(
            data["targets"],
            [
                {
                    "id": "artist:singer_mid",
                    "mid": "singer_mid",
                    "name": "Singer",
                    "icon": "https://example.test/singer.jpg",
                    "fans_num": 123456,
                    "song_count": 1,
                }
            ],
        )
        nodes = {node["id"]: node for node in data["nodes"]}
        self.assertEqual(nodes["artist:singer_mid"]["fans_num"], 123456)
        self.assertEqual(nodes["artist:writer_mid"]["fans_num"], 234567)
        self.assertEqual(nodes["artist:singer_mid"]["sung_song_count"], 1)
        self.assertEqual(nodes["artist:singer_mid"]["composer_song_count"], 1)
        self.assertEqual(nodes["artist:writer_mid"]["lyricist_song_count"], 1)
        edge_ids = {edge["id"] for edge in data["edges"]}
        self.assertIn("artist:writer_mid->artist:singer_mid:作词", edge_ids)
        self.assertNotIn("artist:singer_mid->artist:singer_mid:作曲", edge_ids)

    def test_build_graph_data_exports_song_title_for_website_display(self):
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        self.addCleanup(connection.close)
        connection.executescript("""
            CREATE TABLE artists (
                mid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                area_id INTEGER,
                fans_num INTEGER,
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
                title TEXT NOT NULL,
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
            INSERT INTO artists(mid, name, fans_num, icon) VALUES
                ('singer_mid', 'Singer', 123456, ''),
                ('writer_mid', 'Writer', 234567, '');
            INSERT INTO albums(mid, id, name, title, albumType, publishDate)
                VALUES ('album_mid', 1, 'Album Name', 'Album Display Title', 'Single', '2026-01-01');
            INSERT INTO songs(mid, id, name, title, language, album_mid)
                VALUES ('song_mid', 100, 'Internal Name', 'Website Display Title', 0, 'album_mid');
            INSERT INTO song_singers(song_mid, singer_order, singer_mid)
                VALUES ('song_mid', 0, 'singer_mid');
            INSERT INTO song_credit_artists(song_mid, role, artist_order, artist_mid)
                VALUES ('song_mid', '作词', 0, 'writer_mid');
            """)

        data = build_graph_data(connection)

        self.assertEqual(data["songs"][0]["name"], "Internal Name")
        self.assertEqual(data["songs"][0]["title"], "Website Display Title")
        self.assertEqual(data["songs"][0]["album"], "Album Name")
        self.assertEqual(data["songs"][0]["album_title"], "Album Display Title")
        edge_song = data["edges"][0]["songs"][0]
        self.assertEqual(edge_song["name"], "Internal Name")
        self.assertEqual(edge_song["title"], "Website Display Title")
        self.assertEqual(edge_song["album"], "Album Name")
        self.assertEqual(edge_song["album_title"], "Album Display Title")

    def test_build_graph_data_keeps_all_target_singers(self):
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        self.addCleanup(connection.close)
        connection.executescript("""
            CREATE TABLE artists (
                mid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                area_id INTEGER,
                fans_num INTEGER,
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
            INSERT INTO albums(mid, id, name, albumType, publishDate)
                VALUES ('album_mid', 1, 'Album', 'Single', '2026-01-01');
            INSERT INTO artists(mid, name, fans_num, icon) VALUES ('writer_mid', 'Writer', 200000, '');
            """)
        for index in range(12):
            singer_mid = f"singer_{index:02d}"
            song_mid = f"song_{index:02d}"
            connection.execute(
                "INSERT INTO artists(mid, name, fans_num, icon) VALUES (?, ?, ?, '')",
                (singer_mid, f"Singer {index:02d}", 100000 + index),
            )
            connection.execute(
                "INSERT INTO songs(mid, id, name, title, language, album_mid) VALUES (?, ?, ?, ?, 0, 'album_mid')",
                (song_mid, 1000 + index, f"Song {index:02d}", f"Song {index:02d}"),
            )
            connection.execute(
                "INSERT INTO song_singers(song_mid, singer_order, singer_mid) VALUES (?, 0, ?)",
                (song_mid, singer_mid),
            )
            connection.execute(
                "INSERT INTO song_credit_artists(song_mid, role, artist_order, artist_mid) VALUES (?, '作词', 0, 'writer_mid')",
                (song_mid,),
            )
        data = build_graph_data(connection)
        self.assertEqual(len(data["targets"]), 12)
        self.assertEqual(len(data["edges"]), 12)

    def test_build_graph_data_orders_targets_by_fans_desc(self):
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        self.addCleanup(connection.close)
        connection.executescript("""
            CREATE TABLE artists (
                mid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                area_id INTEGER,
                fans_num INTEGER,
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
            INSERT INTO albums(mid, id, name, albumType, publishDate)
                VALUES ('album_mid', 1, 'Album', 'Single', '2026-01-01');
            INSERT INTO artists(mid, name, fans_num, icon) VALUES
                ('writer_mid', 'Writer', 200000, ''),
                ('target_z', 'Zed Target', 300000, ''),
                ('target_a', 'Alpha Target', 400000, '');
            INSERT INTO songs(mid, id, name, title, language, album_mid) VALUES
                ('song_z', 100, 'Song Z', 'Song Z', 0, 'album_mid'),
                ('song_a', 101, 'Song A', 'Song A', 0, 'album_mid');
            INSERT INTO song_singers(song_mid, singer_order, singer_mid) VALUES
                ('song_z', 0, 'target_z'),
                ('song_a', 0, 'target_a');
            INSERT INTO song_credit_artists(song_mid, role, artist_order, artist_mid) VALUES
                ('song_z', '作词', 0, 'writer_mid'),
                ('song_a', '作词', 0, 'writer_mid');
            """)
        data = build_graph_data(connection)
        self.assertEqual([item["mid"] for item in data["targets"]], ["target_a", "target_z"])

    def test_demo_graph_uses_first_ten_mvp_seed_artists_and_incident_edges(self):
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        self.addCleanup(connection.close)
        connection.executescript("""
            CREATE TABLE artists (
                mid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                area_id INTEGER,
                fans_num INTEGER,
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
            INSERT INTO albums(mid, id, name, albumType, publishDate)
                VALUES ('album_mid', 1, 'Album', 'Single', '2026-01-01');
            INSERT INTO artists(mid, name, area_id, fans_num, raw_page, raw_row_index) VALUES
                ('neighbor_singer', 'Neighbor Singer', NULL, NULL, 0, 50),
                ('neighbor_writer', 'Neighbor Writer', NULL, NULL, 0, 51);
            """)
        for index in range(11):
            connection.execute(
                """
                INSERT INTO artists(mid, name, area_id, fans_num, raw_page, raw_row_index)
                VALUES (?, ?, 0, ?, 0, ?)
                """,
                (f"seed_{index:02d}", f"Seed {index:02d}", 1000000 + index, index),
            )
        connection.executescript("""
            INSERT INTO songs(mid, id, name, title, language, album_mid) VALUES
                ('song_seed_sung', 100, 'Seed Sung', 'Seed Sung', 0, 'album_mid'),
                ('song_seed_written', 101, 'Seed Written', 'Seed Written', 0, 'album_mid'),
                ('song_unrelated', 102, 'Unrelated', 'Unrelated', 0, 'album_mid');
            INSERT INTO song_singers(song_mid, singer_order, singer_mid) VALUES
                ('song_seed_sung', 0, 'seed_00'),
                ('song_seed_written', 0, 'neighbor_singer'),
                ('song_unrelated', 0, 'neighbor_singer');
            INSERT INTO song_credit_artists(song_mid, role, artist_order, artist_mid) VALUES
                ('song_seed_sung', '作词', 0, 'neighbor_writer'),
                ('song_seed_written', '作词', 0, 'seed_01'),
                ('song_unrelated', '作词', 0, 'neighbor_writer');
            """)
        data = build_graph_data(connection, demo=True)
        self.assertEqual(data["target_match_mode"], "incident")
        self.assertEqual(
            {item["mid"] for item in data["targets"]}, {f"seed_{index:02d}" for index in range(10)}
        )
        self.assertNotIn("seed_10", {item["mid"] for item in data["targets"]})
        self.assertEqual(
            {song["mid"] for song in data["songs"]}, {"song_seed_sung", "song_seed_written"}
        )
        edge_ids = {edge["id"] for edge in data["edges"]}
        self.assertIn("artist:neighbor_writer->artist:seed_00:作词", edge_ids)
        self.assertIn("artist:seed_01->artist:neighbor_singer:作词", edge_ids)
        self.assertNotIn("artist:neighbor_writer->artist:neighbor_singer:作词", edge_ids)
        node_ids = {node["id"] for node in data["nodes"]}
        self.assertIn("artist:neighbor_singer", node_ids)
        self.assertIn("artist:neighbor_writer", node_ids)

    def test_safe_script_json_escapes_script_close(self):
        payload = safe_script_json({"title": "before </script> after"})
        self.assertNotIn("</script>", payload.lower())
        self.assertIn("<\\/script>", payload)

    def test_html_can_load_external_graph_assets(self):
        html = html_document(
            "测试",
            {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}},
            "",
            graph_data_src="assets/graph-data.js",
            vendor_src="assets/vendor/force-graph.min.js",
        )
        self.assertIn('<script src="assets/vendor/force-graph.min.js"></script>', html)
        self.assertIn('<script src="assets/graph-data.js"></script>', html)
        self.assertIn("window.GRAPH_TITLE", html)
        self.assertNotIn("window.GRAPH_DATA = {", html)
        self.assertNotIn("const vendorScript =", html)

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
        self.assertIn(".onNodeRightClick", JS)
        self.assertIn(".onLinkRightClick", JS)
        self.assertIn(".onBackgroundClick", JS)
        self.assertIn(".onBackgroundRightClick", JS)
        self.assertIn("toggleNodeSelection(node, event)", JS)
        self.assertIn("const multiSelect = Boolean(event?.ctrlKey || event?.metaKey)", JS)
        self.assertIn("state.selectedNodeIds.clear();", JS)
        self.assertIn("function setNodeSelectionHighlight", JS)
        self.assertIn('state.selected = { type: "nodes" }', JS)
        self.assertIn('selectedNodeView: "all"', JS)
        self.assertIn('selectedEdgeMode: "intersection"', JS)
        self.assertIn("function directionMatchesSelectedNodeView", JS)
        self.assertIn('state.selectedNodeView === "input"', JS)
        self.assertIn('state.selectedNodeView === "output"', JS)
        self.assertIn("function edgeMatchesSelectedNodeView", JS)
        self.assertIn("function edgeConnectsOnlySelectedNodes", JS)
        self.assertIn("function selectedNodeHighlightEdges", JS)
        self.assertIn('state.selectedEdgeMode === "union"', JS)
        self.assertIn("selectedNodeHighlightEdges().forEach", JS)
        self.assertIn("function renderDetailControls", JS)
        self.assertIn('<select id="selected-node-view">', JS)
        self.assertIn('<option value="all"', JS)
        self.assertIn('<option value="input"', JS)
        self.assertIn('<option value="output"', JS)
        self.assertIn('<select id="selected-edge-mode">', JS)
        self.assertIn('<option value="intersection"', JS)
        self.assertIn('<option value="union"', JS)
        self.assertIn("const selectedEdges = selectedNodeHighlightEdges();", JS)
        self.assertIn('const relationText = state.selectedEdgeMode === "union"', JS)
        self.assertIn("renderSelectedNodeEdgeDetails", JS)
        self.assertIn("当前视图下没有匹配的关系", JS)
        self.assertIn("renderSongList(edge.songs || [])", JS)
        self.assertIn("function songDisplayTitle(song)", JS)
        self.assertIn('return song?.title || song?.name || "";', JS)
        self.assertIn('[songDisplayTitle(song), song.role].filter(Boolean).join(" · ")', JS)
        self.assertIn("function albumDisplayTitle(song)", JS)
        self.assertIn('return song?.album_title || song?.album || "";', JS)
        self.assertIn('[song.target, albumDisplayTitle(song)].filter(Boolean).join(" · ")', JS)
        self.assertIn(".map(songDisplayTitle)", JS)
        self.assertIn("name: songDisplayTitle(song)", JS)
        self.assertIn("album: albumDisplayTitle(song)", JS)
        self.assertNotIn('[song.target, song.role, song.album].filter(Boolean).join(" · ")', JS)
        self.assertIn("setLinkHighlight(edge)", JS)
        self.assertIn("particlesEnabled: false", JS)
        html = html_document(
            "测试", {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}}, ""
        )
        self.assertIn('<div class="detail-panel-head">', html)
        self.assertIn('<div id="detail-controls" class="detail-controls"></div>', html)
        self.assertIn(".detail-controls {", html)
        self.assertIn(".detail-control select {", html)
        self.assertIn("particle-toggle", html)
        self.assertIn('id="label-toggle" type="checkbox" />', html)
        self.assertIn('id="particle-toggle" type="checkbox" />', html)
        self.assertIn('id="clear-filters"', html)
        self.assertIn('id="drawing-toggle" type="checkbox" />', html)
        self.assertIn('id="drawing-clear-popover"', html)
        self.assertIn('id="drawing-clear-no"', html)
        self.assertIn('id="drawing-clear-yes"', html)
        self.assertLess(html.index('id="clear-filters"'), html.index('id="drawing-toggle"'))
        self.assertLess(html.index('id="drawing-toggle"'), html.index('id="role-split-toggle"'))
        self.assertIn(
            ".clear-filters-button {\n  min-height: 0;\n  padding: 0;\n  border: 0;\n  background: transparent;",
            html,
        )
        self.assertIn("color: #475467;\n  font-size: 12px;\n  line-height: 1.2;", html)
        self.assertIn("appearance: none;\n  -webkit-appearance: none;", html)
        self.assertIn(
            ".clear-filters-button:hover {\n  color: #172033;\n  text-decoration: underline;", html
        )
        self.assertIn(
            ".clear-filters-button:focus-visible {\n  outline: none;\n  color: #172033;", html
        )
        self.assertNotIn("outline: 2px solid #1570ef", html)
        self.assertNotIn(".clear-filters-button {\n  min-height: 26px;\n  padding: 3px 10px;", html)
        self.assertNotIn('<label class="switch-control switch-control-disabled">', html)
        self.assertIn("function drawDirectionalParticles", JS)
        self.assertIn('roleDisplay: "__DEFAULT_ROLE_DISPLAY__"', JS)
        self.assertIn(
            'id="role-split-toggle" type="checkbox" checked',
            html_document(
                "测试", {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}}, ""
            ),
        )
        self.assertIn(
            'id="role-split-toggle" type="checkbox" />',
            html_document(
                "测试",
                {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}},
                "",
                default_role_split=False,
            ),
        )
        self.assertIn(
            'roleDisplay: "split"',
            html_document(
                "测试", {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}}, ""
            ),
        )
        self.assertIn(
            'roleDisplay: "merged"',
            html_document(
                "测试",
                {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}},
                "",
                default_role_split=False,
            ),
        )
        self.assertIn(".enableNodeDrag(__DEFAULT_NODE_DRAG__)", JS)
        self.assertIn(
            ".enableNodeDrag(true)",
            html_document(
                "测试", {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}}, ""
            ),
        )
        self.assertIn(
            ".enableNodeDrag(false)",
            html_document(
                "测试",
                {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}},
                "",
                default_node_drag=False,
            ),
        )
        self.assertIn("hideLeafNodes: __DEFAULT_HIDE_LEAF_NODES__", JS)
        self.assertIn("onlyTargetNodes: false", JS)
        self.assertIn("数据来源：QQ音乐", JS)
        self.assertIn("<br />", JS)
        self.assertNotIn("SQLite 静态图谱", JS)
        self.assertIn("function leafNodeIds", JS)
        self.assertIn("const neighbors = new Map();", JS)
        self.assertIn("neighbors.get(source).add(target);", JS)
        self.assertIn("neighbors.get(target).add(source);", JS)
        self.assertIn("ids.size === 1", JS)
        self.assertNotIn("filter(([, degree]) => degree === 1)", JS)
        self.assertIn("if (state.hideLeafNodes)", JS)
        self.assertIn("if (state.onlyTargetNodes)", JS)
        self.assertIn(
            "activeIds.has(nodeId(edge.source)) && activeIds.has(nodeId(edge.target))", JS
        )
        self.assertIn("nodes = rawData.nodes.filter((node) => activeIds.has(node.id));", JS)
        self.assertIn('target-only-toggle").addEventListener("change"', JS)
        self.assertIn('hide-leaf-toggle").addEventListener("change"', JS)
        self.assertIn('drawing-toggle").addEventListener("change"', JS)
        self.assertIn("hideDrawing: false", JS)
        self.assertIn('document.body.classList.toggle("drawing-hidden", state.hideDrawing)', JS)
        self.assertIn("function renderDrawingOnlyChange", JS)
        self.assertIn("function resetFiltersToEmpty(options = {})", JS)
        self.assertIn("function renderDrawingClearPopover", JS)
        self.assertIn("function syncToolbarControlStates", JS)
        self.assertIn("state.drawingClearPromptOpen = false", JS)
        self.assertIn("state.selectedTargets = new Set(targetIdsRaw())", JS)
        self.assertIn("setFansState(bounds.min, bounds.max)", JS)
        self.assertIn("state.hideLeafNodes = false", JS)
        self.assertIn("state.onlyTargetNodes = false", JS)
        self.assertIn('state.roleDisplay = "merged"', JS)
        self.assertIn("state.showLabels = false", JS)
        self.assertIn("state.particlesEnabled = false", JS)
        self.assertIn("state.minCount = 1", JS)
        self.assertIn("clearSelectionHighlight()", JS)
        self.assertIn(
            "if (!state.hideDrawing) {\n    renderGraph();\n    renderDetail();\n  } else {", JS
        )
        self.assertIn("if (!state.hideDrawing) renderDetail();", JS)
        self.assertIn("if (graphInstance && !state.hideDrawing) renderGraph();", JS)
        self.assertIn("const shouldPrompt = nextHideDrawing && !state.hideDrawing;", JS)
        self.assertIn("state.hideDrawing = nextHideDrawing;", JS)
        self.assertIn("state.drawingClearPromptOpen = shouldPrompt;", JS)
        self.assertIn("renderDrawingClearPopover();\n    renderDrawingOnlyChange();", JS)
        self.assertIn(
            '$("clear-filters").addEventListener("click", () => resetFiltersToEmpty());', JS
        )
        self.assertIn('$("drawing-clear-no").addEventListener("click"', JS)
        self.assertIn("resetFiltersToEmpty({ preserveHideDrawing: true });", JS)
        self.assertIn(
            'state.roleDisplay = event.target.checked ? "split" : "merged";\n    renderDrawingOnlyChange();',
            JS,
        )
        self.assertIn(
            "state.showLabels = event.target.checked;\n    renderDrawingOnlyChange();", JS
        )
        self.assertIn(
            "state.particlesEnabled = event.target.checked;\n    renderDrawingOnlyChange();", JS
        )
        self.assertIn(
            'id="hide-leaf-toggle" type="checkbox"',
            html_document(
                "测试", {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}}, ""
            ),
        )
        self.assertIn(
            'id="target-only-toggle" type="checkbox"',
            html_document(
                "测试", {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}}, ""
            ),
        )
        self.assertNotIn(
            'id="target-only-toggle" type="checkbox" checked',
            html_document(
                "测试", {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}}, ""
            ),
        )
        self.assertNotIn(
            'id="drawing-toggle" type="checkbox" checked',
            html_document(
                "测试", {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}}, ""
            ),
        )
        self.assertIn(
            'id="hide-leaf-toggle" type="checkbox" checked',
            html_document(
                "测试",
                {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}},
                "",
                default_hide_leaf_nodes=True,
            ),
        )
        self.assertIn(
            "hideLeafNodes: true",
            html_document(
                "测试",
                {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}},
                "",
                default_hide_leaf_nodes=True,
            ),
        )
        self.assertIn(
            "hideLeafNodes: false",
            html_document(
                "测试", {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}}, ""
            ),
        )
        self.assertIn("function edgeCurvePoint", JS)
        self.assertIn("const controlX = (source.x + target.x) / 2 + dy * curvature", JS)
        self.assertIn("const radius = 2.2;", JS)
        self.assertIn(
            "const t = sourceId === nodeId(edge.__particleDirectionSource) ? progress : 1 - progress",
            JS,
        )
        self.assertIn(".linkCanvasObject(drawDirectionalParticles)", JS)
        self.assertIn('.linkCanvasObjectMode(() => "after")', JS)
        self.assertIn(".linkDirectionalParticles(0)", JS)
        self.assertIn("direction.source", JS)
        self.assertIn("direction.target", JS)
        self.assertIn("renderSelection()", JS)
        self.assertNotIn("graphInstance.graphData(graphInstance.graphData())", JS)
        self.assertIn("function requestAvatarAtlasRender()", JS)
        self.assertIn("graphInstance.resumeAnimation()", JS)
        self.assertNotIn("graphInstance.refresh()", JS)
        self.assertNotIn("directionMode", JS)
        self.assertNotIn(
            "direction-mode",
            html_document(
                "测试", {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}}, ""
            ),
        )
        self.assertNotIn(".onNodeHover", JS)
        self.assertNotIn(".onLinkHover", JS)
        self.assertNotIn(".centerAt(", JS)
        self.assertNotIn("includeSelfEdges", JS)
        self.assertNotIn("self-toggle", JS)
        self.assertIn("function findSearchNodes", JS)
        self.assertIn("function runNodeSearch", JS)
        self.assertIn('event.key !== "Enter"', JS)
        self.assertIn("const exactNameMatches = graph.nodes.filter", JS)
        self.assertIn("const partialNameMatches = graph.nodes.filter", JS)
        self.assertIn("state.selectedNodeIds = new Set(nodes.map((node) => node.id));", JS)
        self.assertIn(
            'state.selected = nodes.length === 1 ? { type: "node", id: nodes[0].id } : { type: "nodes" };',
            JS,
        )
        self.assertIn("if (!nodes.length) return;", JS)
        self.assertNotIn("function findSearchNode(", JS)
        self.assertNotIn("state.search", JS)
        self.assertNotIn('$("search-input").addEventListener("input"', JS)

    def test_target_filter_controls_exist(self):
        html = html_document(
            "测试", {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}}, ""
        )
        self.assertIn("selectedTargets", JS)
        self.assertIn("targetItems()", JS)
        self.assertIn("renderTargetCheckboxes", JS)
        self.assertIn("target-dropdown-toggle", JS)
        self.assertIn("target-select-all", JS)
        self.assertIn("target-invert", JS)
        self.assertIn('<div class="target-select-shell">', html)
        self.assertIn('<div id="target-dropdown-menu" class="target-dropdown-menu" hidden>', html)
        self.assertLess(
            html.index('<div class="target-select-shell">'),
            html.index('<div id="target-dropdown-menu" class="target-dropdown-menu" hidden>'),
        )
        self.assertLess(
            html.index('<button id="clear-filters"'),
            html.index('<div class="drawing-toggle-shell">'),
        )
        self.assertLess(
            html.index('<div class="drawing-toggle-shell">'),
            html.index('<label class="switch-control">\n        作词/作曲分开'),
        )
        self.assertLess(
            html.index('<label class="switch-control">\n        作词/作曲分开'),
            html.index('<div class="toolbar-filter-row">'),
        )
        self.assertLess(
            html.index('<div class="toolbar-filter-row">'), html.index('<div class="fans-filter">')
        )
        self.assertLess(
            html.index('id="fans-min-input"'), html.index('<div class="fans-slider-shell">')
        )
        self.assertLess(
            html.index('<div class="fans-slider-shell">'), html.index('id="fans-max-input"')
        )
        self.assertLess(
            html.index('<div class="fans-filter">'), html.index('<div class="target-filter">')
        )
        self.assertLess(
            html.index('<div class="target-filter">'),
            html.index(
                '<input id="search-input" type="search" placeholder="搜索音乐人后按 Enter" />'
            ),
        )
        self.assertLess(
            html.index('<div id="target-dropdown-menu" class="target-dropdown-menu" hidden>'),
            html.index("<label>最小歌曲数"),
        )
        self.assertIn(".target-select-shell {\n  position: relative;\n  width: 210px;", html)
        self.assertIn(
            ".target-dropdown-menu {\n  position: absolute;\n  z-index: 20;\n  top: calc(100% + 4px);\n  left: 0;\n  width: 100%;",
            html,
        )
        self.assertIn("fans-min-range", html)
        self.assertIn("fans-max-range", html)
        self.assertIn("fans-min-input", html)
        self.assertIn("fans-max-input", html)
        self.assertIn('inputmode="numeric"', html)
        self.assertIn("DEFAULT_FANS_MIN = __DEFAULT_FANS_MIN__", JS)
        self.assertIn("const DEFAULT_FANS_MIN = 5000000", html)
        self.assertIn("function fansInRange", JS)
        self.assertIn("function parseFansInputValue", JS)
        self.assertIn('if (raw === "不限") return bounds.max;', JS)
        self.assertIn('normalized.endsWith("万") || normalized.endsWith("w")', JS)
        self.assertIn("function updateFansTextInput", JS)
        self.assertIn('["fans-min-input", "fans-max-input"].forEach((id) => {', JS)
        self.assertIn("updateFansTextInput(event.target.id, event.target.value);", JS)
        self.assertIn("targetItemsRaw().filter((item) => fansInRange(item))", JS)
        self.assertIn("function syncSelectedTargetsWithFansRange", JS)
        self.assertIn("syncSelectedTargetsWithFansRange()", JS)
        self.assertIn("function activeTargetIds", JS)
        self.assertIn("const activeIds = activeTargetIds();", JS)
        self.assertIn("function edgeMatchesActiveTargets", JS)
        self.assertIn('rawData.target_match_mode === "incident"', JS)
        self.assertIn("activeIds.has(edge.source) || activeIds.has(edge.target)", JS)
        self.assertIn(
            "state.selectedTargets = new Set([...state.selectedTargets].filter((id) => knownIds.has(id)))",
            JS,
        )
        self.assertNotIn(
            "state.selectedTargets = new Set([...state.selectedTargets].filter((id) => availableIds.has(id)))",
            JS,
        )
        self.assertIn("const nextTargets = new Set(state.selectedTargets);", JS)
        self.assertIn("initFansControls()", JS)
        self.assertIn("<span>${escapeHtml(item.name)}</span>", JS)
        self.assertNotIn(
            "formatNumber(item.song_count)} 首 / ${formatFansValue(item.fans_num)} 粉丝", JS
        )
        self.assertIn(
            ".fans-range {\n  display: grid;\n  grid-template-columns: 52px 220px 52px;", html
        )
        self.assertIn(".fans-value-input", html)
        self.assertNotIn("fans-range-separator", html)
        self.assertNotIn(">至</span>", html)
        self.assertIn(".fans-slider-shell::before", html)
        self.assertIn("top: 50%", html)
        self.assertIn("transform: translateY(-50%)", html)
        self.assertIn("-webkit-appearance: none", html)
        self.assertIn("background: transparent", html)

    def test_text_node_and_detail_behaviors_exist(self):
        html = html_document(
            "测试", {"nodes": [], "edges": [], "songs": [], "targets": [], "summary": {}}, ""
        )
        self.assertIn("function drawTextNode", JS)
        self.assertIn("function textNodeMetrics", JS)
        self.assertIn("function textNodeOpacity", JS)
        self.assertIn("return Math.max(0.5, Math.min(1, 0.5 + ((radius - 10) / 55) * 0.5))", JS)
        self.assertIn(
            "const opacity = selected || highlighted ? 1 : dimmed ? textNodeOpacity(node) * 0.65 : textNodeOpacity(node);",
            JS,
        )
        self.assertNotIn("Math.max(0.5, textNodeOpacity(node) * 0.65)", JS)
        self.assertIn("rgba(23, 32, 51, ${opacity.toFixed(3)})", JS)
        self.assertIn("if (state.showLabels)", JS)
        self.assertIn(
            "display: grid;\n  grid-template-columns: minmax(280px, 1fr) minmax(0, auto);\n  grid-template-areas:",
            html,
        )
        self.assertIn('"title switches"\n    "title filters";', html)
        self.assertIn(".topbar-title {\n  grid-area: title;\n  align-self: center;", html)
        self.assertIn(
            ".toolbar-filter-row {\n  grid-area: filters;\n  display: flex;\n  align-items: center;\n  justify-content: flex-end;",
            html,
        )
        self.assertIn("padding: 14px 22px 8px", html)
        self.assertNotIn(
            "padding: 16px 22px;\n  background: #ffffff;\n  border-bottom: 1px solid #d8dee8;", html
        )
        self.assertNotIn("align-self: end", html)
        self.assertNotIn(
            ".topbar {\n  display: grid;\n  grid-template-columns: minmax(280px, 1fr) minmax(0, auto);\n  gap: 14px;\n  align-items: start;",
            html,
        )
        self.assertNotIn(
            ".topbar {\n  display: grid;\n  grid-template-columns: minmax(280px, 1fr) minmax(0, auto);\n  gap: 14px;\n  align-items: center;",
            html,
        )
        self.assertIn("align-items: stretch", html)
        self.assertIn("body.drawing-hidden .workspace {\n  display: none;\n}", html)
        self.assertIn("body.drawing-hidden .data-section {\n  margin-top: 0;\n}", html)
        self.assertIn("function syncPanelHeights", JS)
        self.assertNotIn("function syncDetailPanelHeight", JS)
        self.assertIn(
            "graphPanel.offsetHeight || Math.round(graphPanel.getBoundingClientRect().height)", JS
        )
        self.assertIn("if (state.hideDrawing) {", JS)
        self.assertIn("Math.floor(window.innerHeight - top - 16)", JS)
        self.assertIn("panel.style.height = `${panelHeight}px`", JS)
        self.assertIn("window.requestAnimationFrame(syncPanelHeights)", JS)
        self.assertIn("syncPanelHeights();", JS)
        self.assertNotIn("window.requestAnimationFrame(syncDetailPanelHeight)", JS)
        self.assertNotIn("syncDetailPanelHeight();", JS)
        self.assertNotIn('height + document.querySelector(".panel-head").offsetHeight', JS)
        self.assertIn("lyricist_song_count", JS)
        self.assertIn("composer_song_count", JS)
        self.assertIn("Math.min(65, 7 + Math.sqrt(degree || 1) * 2.2)", JS)
        self.assertIn("Math.max(10, Math.min(65, node.val || 12))", JS)
        self.assertIn(
            "linkForce.distance((edge) => 92 + Math.max(0, 8 - Math.sqrt(edge.song_count || 1)) * 5)",
            JS,
        )
        self.assertIn("chargeForce.strength(-380)", JS)
        self.assertNotIn("d3.forceCollide", JS)
        self.assertIn("let currentEdgeWeightScale = { min: 1, max: 1 }", JS)
        self.assertIn("function updateEdgeWeightScale", JS)
        self.assertIn("function edgeWeightRatio", JS)
        self.assertIn("directions: new Map()", JS)
        self.assertIn("nodeName(direction.source)} -> ${nodeName(direction.target)", JS)
        self.assertIn("function directionLabels", JS)
        self.assertIn("const roles = (direction.roles || []).join", JS)
        self.assertIn("formatNumber(direction.song_count)", JS)
        self.assertIn('if (hasActiveHighlight() && !isHighlightedLink(edge)) return "";', JS)
        self.assertIn('return directionLabels(edge).join("<br>")', JS)
        self.assertIn("const rows = graph.edges.flatMap((edge) =>", JS)
        self.assertIn("source: nodeName(direction.source)", JS)
        self.assertIn("target: nodeName(direction.target)", JS)
        self.assertIn("count: direction.song_count", JS)
        self.assertNotIn("source: nodeName(edge.source)", JS)
        self.assertNotIn("target: nodeName(edge.target)", JS)
        self.assertNotIn("return `${edge.role} · ${formatNumber(edge.song_count)} 首", JS)
        self.assertIn("return 1 + edgeWeightRatio(edge) * 4", JS)
        self.assertIn("if (isHighlightedLink(edge)) return 1", JS)
        self.assertIn("const alpha = 0.2 + edgeWeightRatio(edge) * 0.8", JS)
        self.assertIn("return hasActiveHighlight() ? alpha * 0.5 : alpha", JS)
        self.assertIn("updateEdgeWeightScale(graph.edges)", JS)
        self.assertIn("function restoreSelectionForCurrentGraph", JS)
        self.assertIn("function resolveSelectedEdges", JS)
        self.assertIn("function resolveSelectedEdge", JS)
        self.assertIn("function edgeGroupSelectionSnapshot", JS)
        self.assertIn("state.selected = edgeSelectionSnapshot(edge)", JS)
        self.assertIn(
            "state.selected = edges.length === 1 ? edgeSelectionSnapshot(edges[0]) : edgeGroupSelectionSnapshot(edges)",
            JS,
        )
        self.assertIn('state.selected?.type === "edges"', JS)
        self.assertIn("restoreSelectionForCurrentGraph()", JS)
        self.assertNotIn(
            'state.roleDisplay = event.target.checked ? "split" : "merged";\n    clearSelectionHighlight();',
            JS,
        )
        self.assertNotIn(
            "state.minCount = Math.max(1, Number(event.target.value || 1));\n    clearSelectionHighlight();",
            JS,
        )
        self.assertNotIn(
            "state.search = event.target.value.trim();\n    clearSelectionHighlight();", JS
        )
        self.assertIn("rgba(31, 120, 180, ${alpha})", JS)
        self.assertIn("rgba(217, 95, 2, ${alpha})", JS)
        self.assertIn("rgba(20, 132, 117, ${alpha})", JS)
        self.assertIn("ctx.lineWidth = selected || highlighted ? 0.65 / globalScale", JS)
        self.assertIn("radius + 0.6 / globalScale", JS)
        self.assertIn(
            "目标歌手：${currentScopeLabel()} · 当前图：${formatNumber(graph.nodes.length)} 个音乐人节点",
            JS,
        )
        self.assertIn(
            "数据库：${formatNumber(summary.songs)} 首歌曲 / ${formatNumber(summary.artists)} 位音乐人",
            JS,
        )
        self.assertNotIn("SQLite 静态图谱 · 目标歌手：${currentScopeLabel()}", JS)
        self.assertIn("<strong>数据库规模</strong>", JS)
        self.assertIn("位数据库音乐人", JS)
        self.assertNotIn("`${currentScopeLabel()} · ${formatNumber(graph.nodes.length)} 个节点", JS)
        self.assertNotIn("位库内音乐人", JS)
        self.assertIn("role-split-toggle", html)
        self.assertIn('class="graph-heading"', html)
        self.assertIn(".graph-heading {\n  display: flex;\n  align-items: baseline;", html)
        self.assertIn(".topbar {\n  position: sticky;\n  top: 0;\n  z-index: 30;", html)
        self.assertIn("top: calc(var(--topbar-height, 0px) + 14px);", html)
        self.assertIn('const items = state.roleDisplay === "split"', JS)
        self.assertIn('["rgba(31, 120, 180, 0.75)", "作词"]', JS)
        self.assertIn('["rgba(217, 95, 2, 0.75)", "作曲"]', JS)
        self.assertIn('[["rgba(20, 132, 117, 0.75)", "作词/作曲"]]', JS)
        self.assertNotIn("</span>合并</span>", JS)
        self.assertIn("table-search-input", html)
        self.assertIn(
            ".data-section {\n  margin-top: 14px;\n  overflow: hidden;\n  display: flex;\n  flex-direction: column;",
            html,
        )
        self.assertIn(
            "#table-content {\n  flex: 1 1 auto;\n  min-height: 0;\n  overflow: auto;", html
        )
        self.assertNotIn("#table-content {\n  max-height: 420px;", html)
        self.assertIn("function syncPanelHeights", JS)
        self.assertIn('document.documentElement.style.setProperty("--topbar-height"', JS)
        self.assertIn("[detailPanel, dataSection].forEach", JS)
        self.assertNotIn("function syncDetailPanelHeight", JS)
        self.assertIn("tableSearch", JS)
        self.assertIn("function selectedTableNodeIds", JS)
        self.assertIn("function songHasAnyPerson", JS)
        self.assertNotIn("function personNamesForTable", JS)
        self.assertIn("function mergeEdges(edges, roleDisplay = state.roleDisplay)", JS)
        self.assertIn('const roleKey = roleDisplay === "split" ? edge.role : "合作";', JS)
        self.assertIn("function buildGraph(options = {})", JS)
        self.assertIn("const roleDisplay = options.roleDisplay || state.roleDisplay;", JS)
        self.assertIn('const graph = buildGraph({ roleDisplay: "split" });', JS)
        self.assertIn("const graph = buildGraph();", JS)
        self.assertIn("const visibleNodeIds = new Set(graph.nodes.map((node) => node.id));", JS)
        self.assertIn("const rows = graph.edges.flatMap((edge) =>", JS)
        self.assertIn("const rows = filteredSongs(graph, visibleNodeIds)", JS)
        self.assertIn("function filteredSongs(graph, visibleNodeIds)", JS)
        self.assertIn("const visibleSongMids = new Set();", JS)
        self.assertIn('visibleSongMids.has(String(song.mid || ""))', JS)
        self.assertIn(
            "(song.singers || []).some((person) => visibleNodeIds.has(`artist:${person.mid}`))", JS
        )
        self.assertIn("visibleSongMids.add(mid);", JS)
        self.assertIn("lyricists: personNames(song.lyricists)", JS)
        self.assertIn("composers: personNames(song.composers)", JS)
        self.assertIn("singers: personNames(song.singers)", JS)
        self.assertNotIn("personNamesForTable(song.lyricists, selectedIds, visibleNodeIds)", JS)
        self.assertNotIn("const scopeIds = selectedIds.size ? selectedIds : visibleNodeIds;", JS)
        self.assertIn("function matchesTableSearch", JS)
        self.assertIn("renderDetail();\n  renderTable();", JS)
        self.assertIn("state.tableSearch = event.target.value.trim()", JS)
        self.assertIn("!selectedIds.size || songHasAnyPerson(song, selectedIds)", JS)
        self.assertIn(
            "!selectedIds.size || selectedIds.has(direction.source) || selectedIds.has(direction.target)",
            JS,
        )
        self.assertNotIn(
            'const ids = rawData.target_match_mode === "incident" ? activeTargetIds() : state.selectedTargets;',
            JS,
        )
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
        self.assertIn('class="switch-control switch-control-disabled"', html)
        self.assertIn('id="label-toggle" type="checkbox" disabled', html)
        self.assertIn('id="particle-toggle" type="checkbox" disabled', html)
        self.assertIn('id="role-split-toggle" type="checkbox" disabled', html)
        self.assertNotIn('id="role-split-toggle" type="checkbox" checked', html)
        self.assertIn(
            'id="fans-min-input" class="fans-value-input fans-value-min" type="text" inputmode="numeric" aria-label="最低粉丝量" value="0"',
            html,
        )
        self.assertIn(
            'id="fans-min-range" type="range" min="0" max="5000000" step="10000" value="0"', html
        )
        self.assertIn("const DEFAULT_FANS_MIN = 0", html)
        self.assertIn(".switch-control-disabled {\n  color: #98a2b3;", html)
        self.assertIn(
            "window.devicePixelRatio = 1; // use standard resolution in retina displays",
            LARGE_GRAPH_JS,
        )
        self.assertIn("graphInstance = new ForceGraph(container)", LARGE_GRAPH_JS)
        self.assertIn("api.graphData(graphPayload(graph.nodes, graph.edges))", LARGE_GRAPH_JS)
        self.assertIn(".d3AlphaDecay(0)", LARGE_GRAPH_JS)
        self.assertIn(".d3VelocityDecay(0.08)", LARGE_GRAPH_JS)
        self.assertIn(".cooldownTime(60000)", LARGE_GRAPH_JS)
        self.assertIn(".linkColor(() => 'rgba(0,0,0,0.05)')", LARGE_GRAPH_JS)
        self.assertIn(".zoom(0.05)", LARGE_GRAPH_JS)
        self.assertIn(".enablePointerInteraction(true)", LARGE_GRAPH_JS)
        self.assertIn(".enableNodeDrag(false)", LARGE_GRAPH_JS)
        self.assertNotIn(".enableNodeDrag(true)", LARGE_GRAPH_JS)
        self.assertIn(".onNodeRightClick", LARGE_GRAPH_JS)
        self.assertIn(".onLinkRightClick", LARGE_GRAPH_JS)
        self.assertIn(".onBackgroundClick", LARGE_GRAPH_JS)
        self.assertIn(".onBackgroundRightClick", LARGE_GRAPH_JS)
        self.assertNotIn(".nodeCanvasObject(", LARGE_GRAPH_JS)
        self.assertNotIn(".nodePointerAreaPaint(", LARGE_GRAPH_JS)
        self.assertNotIn(".nodeAutoColorBy(", LARGE_GRAPH_JS)
        self.assertNotIn(".linkCanvasObject(", LARGE_GRAPH_JS)
        self.assertNotIn(".linkDirectionalParticles(", LARGE_GRAPH_JS)
        self.assertNotIn("api.zoomToFit", LARGE_GRAPH_JS)
        self.assertNotIn('api.d3Force("link")', LARGE_GRAPH_JS)
        self.assertNotIn('api.d3Force("charge")', LARGE_GRAPH_JS)

    def test_prepare_avatar_cache_prints_each_avatar_progress_line(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            avatar_cache_dir = output_dir.parent / f"{output_dir.name}_shared"
            cached_url = "https://example.test/a.jpg"
            skipped_url = "https://example.test/b.jpg"
            cached_path = avatar_cache_dir / "avatars" / avatar_filename(cached_url)
            cached_path.parent.mkdir(parents=True, exist_ok=True)
            cached_path.write_bytes(b"cached")
            save_manifest(
                avatar_cache_dir / "avatar-manifest.json",
                {
                    "avatars": {
                        cached_url: {
                            "status": "ok",
                            "local_path": cached_path.relative_to(avatar_cache_dir).as_posix(),
                        }
                    }
                },
            )
            graph_data = {
                "nodes": [
                    {"id": "artist:a", "icon": cached_url},
                    {"id": "artist:b", "icon": skipped_url},
                ]
            }
            config = PrepareAssetsConfig(
                db_path=Path("unused.sqlite3"),
                output_dir=output_dir,
                vendor_path=DEFAULT_VENDOR_PATH,
                avatar_cache_dir=avatar_cache_dir,
                download_avatars=False,
                max_avatar_downloads=None,
                request_delay_seconds=0,
                timeout_seconds=1,
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                result = prepare_avatar_cache(graph_data, config)
            progress_lines = [
                line for line in stdout.getvalue().splitlines() if line.startswith("[")
            ]
            self.assertEqual(len(progress_lines), 2)
            self.assertIn("[1/2]", progress_lines[0])
            self.assertIn("status=cache_hit", progress_lines[0])
            self.assertIn("[2/2]", progress_lines[1])
            self.assertIn("status=skipped", progress_lines[1])
            self.assertIn("reason=avatar_download_disabled", progress_lines[1])
            self.assertEqual(result["reused"], 1)
            self.assertEqual(result["skipped"], 1)
            rewritten = rewrite_icons_to_local(
                {"nodes": [{"icon": cached_url}], "targets": []}, output_dir, avatar_cache_dir
            )
            self.assertEqual(
                rewritten["nodes"][0]["icon"],
                f"../{avatar_cache_dir.name}/avatars/{avatar_filename(cached_url)}",
            )
            keyed = rewrite_icons_to_avatar_keys(
                {"nodes": [{"icon": cached_url}], "targets": [{"icon": skipped_url}]},
                avatar_cache_dir,
            )
            self.assertEqual(keyed["nodes"][0]["avatar_key"], avatar_key(cached_url))
            self.assertEqual(keyed["nodes"][0]["icon"], "")
            self.assertEqual(keyed["targets"][0]["avatar_key"], "")
            self.assertEqual(keyed["targets"][0]["icon"], "")

    def test_build_avatar_atlas_orders_profiles_as_shared_prefix(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config, _urls, output_dir = self.make_avatar_atlas_fixture(root)
            result = build_atlas(config)

            atlas_manifest = json.loads(
                (output_dir / "avatar-atlas-manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(result["placed"], 5)
            self.assertEqual(atlas_manifest["profiles"]["mvp"]["atlas_files"], ["atlas_000.webp"])
            self.assertEqual(atlas_manifest["profiles"]["demo"]["atlas_files"], ["atlas_000.webp"])
            self.assertEqual(
                atlas_manifest["profiles"]["full"]["atlas_files"],
                ["atlas_000.webp", "atlas_001.webp"],
            )
            self.assertTrue((output_dir / "atlas_000.webp").is_file())
            self.assertTrue((output_dir / "atlas_001.webp").is_file())
            self.assertTrue((output_dir / DEFAULT_FINGERPRINT_FILE).is_file())

    def test_build_avatar_atlas_skips_when_fingerprint_and_outputs_match(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config, _urls, output_dir = self.make_avatar_atlas_fixture(root)
            first = build_atlas(config)
            first_hash = (output_dir / "atlas_000.webp").read_bytes()

            second = build_atlas(config)
            check = check_existing_atlas(config)

            self.assertEqual(first["status"], "built")
            self.assertEqual(second["status"], "skipped")
            self.assertTrue(check["ok"])
            self.assertEqual(first_hash, (output_dir / "atlas_000.webp").read_bytes())

    def test_build_avatar_atlas_rebuilds_when_output_has_stale_atlas_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config, _urls, output_dir = self.make_avatar_atlas_fixture(root)
            build_atlas(config)
            (output_dir / "atlas_999.webp").write_bytes(b"stale")

            stale_check = check_existing_atlas(config)
            rebuilt = build_atlas(config)

            self.assertFalse(stale_check["ok"])
            self.assertEqual(stale_check["status"], "atlas_file_set_mismatch")
            self.assertEqual(rebuilt["status"], "rebuilt")
            self.assertFalse((output_dir / "atlas_999.webp").exists())

    def test_build_avatar_atlas_check_mode_reports_source_changes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config, _urls, output_dir = self.make_avatar_atlas_fixture(root)
            build_atlas(config)

            Image.new("RGB", (180, 160), (250, 10, 20)).save(
                config.avatar_cache_dir / "avatars" / "0.jpg", format="JPEG"
            )
            check_result = build_atlas(
                AtlasConfig(
                    avatar_cache_dir=config.avatar_cache_dir,
                    output_dir=output_dir,
                    graph_data_by_profile=config.graph_data_by_profile,
                    cell_size=config.cell_size,
                    atlas_size=config.atlas_size,
                    webp_quality=config.webp_quality,
                    include_unused_cache=config.include_unused_cache,
                    mode="check",
                    legacy_avatar_cache_dir=None,
                )
            )

            self.assertFalse(check_result["ok"])
            self.assertEqual(check_result["status"], "invalid")
            self.assertEqual(check_result["check"]["status"], "input_changed")

    def test_collect_icon_urls_orders_by_artist_relationship_count(self):
        graph_data = {
            "nodes": [
                {
                    "id": "artist:low",
                    "icon": "https://example.test/low.jpg",
                    "sung_song_count": 1,
                    "lyricist_song_count": 0,
                    "composer_song_count": 0,
                },
                {
                    "id": "artist:high",
                    "icon": "https://example.test/high.jpg",
                    "sung_song_count": 2,
                    "lyricist_song_count": 3,
                    "composer_song_count": 1,
                },
                {
                    "id": "artist:tie-b",
                    "icon": "https://example.test/tie-b.jpg",
                    "sung_song_count": 1,
                    "lyricist_song_count": 1,
                    "composer_song_count": 0,
                },
                {
                    "id": "artist:tie-a",
                    "icon": "https://example.test/tie-a.jpg",
                    "sung_song_count": 2,
                    "lyricist_song_count": 0,
                    "composer_song_count": 0,
                },
                {
                    "id": "artist:shared",
                    "icon": "https://example.test/low.jpg",
                    "sung_song_count": 9,
                    "lyricist_song_count": 0,
                    "composer_song_count": 0,
                },
            ]
        }
        self.assertEqual(
            collect_icon_urls(graph_data),
            [
                "https://example.test/low.jpg",
                "https://example.test/high.jpg",
                "https://example.test/tie-a.jpg",
                "https://example.test/tie-b.jpg",
            ],
        )

    def test_prepare_avatar_cache_prints_download_and_failure_progress(self):
        graph_data = {
            "nodes": [
                {"id": "artist:a", "icon": "https://example.test/a.jpg"},
                {"id": "artist:b", "icon": "https://example.test/b.jpg"},
            ]
        }

        def fake_download(url: str, path: Path, timeout_seconds: float) -> tuple[bool, str]:
            if url.endswith("/a.jpg"):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"avatar")
                return True, "image/jpeg"
            return False, "timeout"

        with tempfile.TemporaryDirectory() as temp_dir:
            config = PrepareAssetsConfig(
                db_path=Path("unused.sqlite3"),
                output_dir=Path(temp_dir),
                vendor_path=DEFAULT_VENDOR_PATH,
                avatar_cache_dir=Path(temp_dir) / "shared",
                download_avatars=True,
                max_avatar_downloads=None,
                request_delay_seconds=0,
                timeout_seconds=1,
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                original_download = prepare_static_graph_assets.download_avatar
                try:
                    prepare_static_graph_assets.download_avatar = fake_download
                    result = prepare_avatar_cache(graph_data, config)
                finally:
                    prepare_static_graph_assets.download_avatar = original_download
            progress_lines = [
                line for line in stdout.getvalue().splitlines() if line.startswith("[")
            ]
            self.assertEqual(len(progress_lines), 2)
            progress_text = "\n".join(progress_lines)
            self.assertIn("[1/2]", progress_text)
            self.assertIn("status=downloaded", progress_text)
            self.assertIn("[2/2]", progress_text)
            self.assertIn("status=failed", progress_text)
            self.assertIn("reason=timeout", progress_text)
            self.assertEqual(result["downloaded"], 1)
            self.assertEqual(result["failed"], 1)

    def test_prepare_avatar_cache_starts_downloads_on_interval_without_waiting_for_completion(self):
        graph_data = {
            "nodes": [
                {"id": "artist:a", "icon": "https://example.test/a.jpg"},
                {"id": "artist:b", "icon": "https://example.test/b.jpg"},
                {"id": "artist:c", "icon": "https://example.test/c.jpg"},
            ]
        }
        start_times: list[float] = []

        def fake_download(url: str, path: Path, timeout_seconds: float) -> tuple[bool, str]:
            start_times.append(time.monotonic())
            time.sleep(0.08)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(url.encode("utf-8"))
            return True, "image/jpeg"

        with tempfile.TemporaryDirectory() as temp_dir:
            config = PrepareAssetsConfig(
                db_path=Path("unused.sqlite3"),
                output_dir=Path(temp_dir),
                vendor_path=DEFAULT_VENDOR_PATH,
                avatar_cache_dir=Path(temp_dir) / "shared",
                download_avatars=True,
                max_avatar_downloads=None,
                request_delay_seconds=0.02,
                timeout_seconds=1,
            )
            original_download = prepare_static_graph_assets.download_avatar
            try:
                prepare_static_graph_assets.download_avatar = fake_download
                started_at = time.monotonic()
                with redirect_stdout(io.StringIO()):
                    result = prepare_avatar_cache(graph_data, config)
                elapsed = time.monotonic() - started_at
            finally:
                prepare_static_graph_assets.download_avatar = original_download
            self.assertEqual(result["downloaded"], 3)
            self.assertEqual(len(start_times), 3)
            gaps = [right - left for left, right in zip(start_times, start_times[1:])]
            self.assertTrue(all(gap >= 0.015 for gap in gaps), gaps)
            self.assertLess(elapsed, 0.24)


if __name__ == "__main__":
    unittest.main()
