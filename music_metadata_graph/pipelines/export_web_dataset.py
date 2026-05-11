from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT = Path("web/data/catalog.json")
DEFAULT_SINGER_INPUTS = (
    "zhoujielun=周杰伦=0025NhlN2yWrP4=data/processed/singer_songs/zhoujielun",
    "xuezhiqian=薛之谦=002J4UUk29y8BY=data/processed/singer_songs/xuezhiqian",
    "linjunjie=林俊杰=001BLpXF2DyJe2=data/processed/singer_songs/linjunjie",
)
EDGE_ROLES = ("作词", "作曲")


def ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_singer_input(value: str) -> dict[str, Any]:
    parts = value.split("=", 3)
    if len(parts) != 4:
        raise ValueError("Singer input must be slug=name=mid=directory")
    slug, name, mid, directory = parts
    return {
        "slug": slug,
        "name": name,
        "mid": mid,
        "directory": Path(directory),
    }


def artist_key(name: str, mid: str | None = None) -> str:
    if mid:
        return f"artist:{mid}"
    return f"artist:name:{name.strip().casefold()}"


def target_key(name: str, mid: str | None = None) -> str:
    return artist_key(name, mid)


def song_key(slug: str, song: dict[str, Any]) -> str:
    if song.get("mid"):
        return f"song:{song['mid']}"
    if song.get("id") is not None:
        return f"song:id:{song['id']}"
    return f"song:{slug}:{song.get('name') or song.get('title')}"


def compact_artist(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": raw.get("id"),
        "mid": raw.get("mid"),
        "name": raw.get("name"),
        "title": raw.get("title"),
        "icon": raw.get("icon"),
    }


def find_role_artists(song: dict[str, Any], role: str) -> list[dict[str, Any]]:
    credits = song.get("credits") or {}
    for group in credits.get("groups") or []:
        if group.get("role") == role:
            return [compact_artist(artist) for artist in group.get("artists") or [] if artist.get("name")]
    return []


def add_node(nodes: dict[str, dict[str, Any]], node: dict[str, Any]) -> None:
    existing = nodes.get(node["id"])
    if existing is None:
        nodes[node["id"]] = node
        return
    for key, value in node.items():
        if value and not existing.get(key):
            existing[key] = value


def build_dataset(config: dict[str, Any]) -> dict[str, Any]:
    slug = config["slug"]
    name = config["name"]
    mid = config["mid"]
    directory = config["directory"]
    songs_path = directory / "songs_kept.json"
    incomplete_path = directory / "songs_credit_incomplete.json"
    snapshot_path = directory / "singer_song_snapshot.json"
    songs = load_json(songs_path)
    incomplete = load_json(incomplete_path) if incomplete_path.exists() else []
    snapshot = load_json(snapshot_path) if snapshot_path.exists() else {}

    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[tuple[str, str, str], dict[str, Any]] = {}
    song_nodes: list[dict[str, Any]] = []
    song_records: list[dict[str, Any]] = []
    role_counts: Counter[str] = Counter()
    contributor_counts: Counter[str] = Counter()
    self_role_counts: Counter[str] = Counter()

    target_id = target_key(name, mid)
    add_node(
        nodes,
        {
            "id": target_id,
            "type": "artist",
            "name": name,
            "mid": mid,
            "slug": slug,
            "is_target": True,
            "song_count": len(songs),
        },
    )

    for song in songs:
        current_song_key = song_key(slug, song)
        song_node = {
            "id": current_song_key,
            "type": "song",
            "name": song.get("name") or song.get("title"),
            "mid": song.get("mid"),
            "song_id": song.get("id"),
            "album": song.get("album_name"),
            "target_slug": slug,
        }
        song_nodes.append(song_node)

        roles: dict[str, list[dict[str, Any]]] = {}
        for role in EDGE_ROLES:
            artists = find_role_artists(song, role)
            roles[role] = artists
            for artist in artists:
                artist_id = artist_key(str(artist["name"]), artist.get("mid"))
                if artist.get("mid") == mid or artist.get("name") == name:
                    artist_id = target_id
                add_node(
                    nodes,
                    {
                        "id": artist_id,
                        "type": "artist",
                        "name": artist["name"],
                        "mid": artist.get("mid") or (mid if artist_id == target_id else None),
                        "icon": artist.get("icon"),
                        "slug": slug if artist_id == target_id else None,
                        "is_target": artist_id == target_id,
                        "song_count": len(songs) if artist_id == target_id else None,
                    },
                )
                if artist_id == target_id:
                    self_role_counts[role] += 1
                    continue
                edge_key = (artist_id, target_id, role)
                edge = edges.setdefault(
                    edge_key,
                    {
                        "id": f"{artist_id}->{target_id}:{role}",
                        "source": artist_id,
                        "target": target_id,
                        "role": role,
                        "song_count": 0,
                        "songs": [],
                    },
                )
                edge["song_count"] += 1
                edge["songs"].append(
                    {
                        "id": song.get("id"),
                        "mid": song.get("mid"),
                        "name": song.get("name") or song.get("title"),
                        "album": song.get("album_name"),
                    }
                )
                role_counts[role] += 1
                contributor_counts[str(artist["name"])] += 1

        song_records.append(
            {
                "id": song.get("id"),
                "mid": song.get("mid"),
                "name": song.get("name") or song.get("title"),
                "album": song.get("album_name"),
                "time_public": song.get("time_public"),
                "lyricists": [artist["name"] for artist in roles["作词"]],
                "composers": [artist["name"] for artist in roles["作曲"]],
                "target": name,
                "target_slug": slug,
            }
        )

    graph_edges = list(edges.values())
    return {
        "slug": slug,
        "name": name,
        "mid": mid,
        "source_dir": str(directory).replace("\\", "/"),
        "generated_at": now_iso(),
        "summary": {
            "songs": len(songs),
            "initial_candidates": (snapshot.get("counts") or {}).get("songs_after_initial_dedupe", len(songs)),
            "credit_incomplete": len(incomplete),
            "nodes": len(nodes),
            "edges": len(graph_edges),
            "contributors": len([node for node in nodes.values() if node["type"] == "artist"]),
            "self_lyricist_songs": self_role_counts.get("作词", 0),
            "self_composer_songs": self_role_counts.get("作曲", 0),
        },
        "role_counts": dict(role_counts),
        "top_contributors": contributor_counts.most_common(20),
        "graph": {
            "nodes": list(nodes.values()),
            "edges": graph_edges,
            "song_nodes": song_nodes,
        },
        "songs": song_records,
        "quality": {
            "credit_incomplete": len(incomplete),
            "credit_filter_reason_counts": snapshot.get("credit_filter_reason_counts") or {},
        },
    }


def build_catalog(datasets: list[dict[str, Any]]) -> dict[str, Any]:
    all_nodes: dict[str, dict[str, Any]] = {}
    contributor_targets: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "name": "",
            "targets": defaultdict(
                lambda: {
                    "song_count": 0,
                    "roles": defaultdict(lambda: {"song_count": 0, "songs": []}),
                }
            ),
        }
    )
    target_names = {dataset["slug"]: dataset["name"] for dataset in datasets}
    target_node_ids = {dataset["slug"]: target_key(dataset["name"], dataset.get("mid")) for dataset in datasets}
    for dataset in datasets:
        for node in dataset["graph"]["nodes"]:
            add_node(all_nodes, dict(node))
        for edge in dataset["graph"]["edges"]:
            node = all_nodes.get(edge["source"])
            if not node or node.get("type") != "artist":
                continue
            contributor = contributor_targets[edge["source"]]
            contributor["name"] = node.get("name") or edge["source"]
            target = contributor["targets"][dataset["slug"]]
            target["song_count"] += edge["song_count"]
            role = target["roles"][edge["role"]]
            role["song_count"] += edge["song_count"]
            role["songs"].extend(
                {
                    "id": song.get("id"),
                    "mid": song.get("mid"),
                    "name": song.get("name"),
                    "album": song.get("album"),
                    "target": dataset["name"],
                    "target_slug": dataset["slug"],
                    "role": edge["role"],
                }
                for song in edge.get("songs") or []
            )
    bridge_contributors = [
        {
            "id": node_id,
            "name": payload["name"],
            "target_slugs": sorted(payload["targets"]),
            "target_count": len(payload["targets"]),
            "song_count": sum(target["song_count"] for target in payload["targets"].values()),
            "targets": [
                {
                    "slug": slug,
                    "name": target_names.get(slug, slug),
                    "target_id": target_node_ids.get(slug, target_key(target_names.get(slug, slug))),
                    "song_count": target["song_count"],
                    "roles": {
                        role_name: {
                            "song_count": role_payload["song_count"],
                            "songs": role_payload["songs"],
                        }
                        for role_name, role_payload in sorted(target["roles"].items())
                    },
                }
                for slug, target in sorted(payload["targets"].items())
            ],
        }
        for node_id, payload in contributor_targets.items()
        if len(payload["targets"]) > 1
    ]
    return {
        "generated_at": now_iso(),
        "source_dataset": {
            "slug": "qqmusic",
            "name": "QQ 音乐",
            "description": "由 QQ 音乐元数据离线采集生成的静态关系图谱数据。",
        },
        "targets": [
            {
                "slug": dataset["slug"],
                "name": dataset["name"],
                "mid": dataset["mid"],
                "file": f"{dataset['slug']}.json",
                "summary": dataset["summary"],
            }
            for dataset in datasets
        ],
        "totals": {
            "targets": len(datasets),
            "songs": sum(dataset["summary"]["songs"] for dataset in datasets),
            "credit_incomplete": sum(dataset["summary"]["credit_incomplete"] for dataset in datasets),
            "unique_nodes": len(all_nodes),
            "bridge_contributors": len(bridge_contributors),
        },
        "bridge_contributors": bridge_contributors,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export static web datasets from processed singer song outputs.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--singer",
        action="append",
        default=None,
        help="Singer dataset as slug=name=mid=directory. Can be repeated.",
    )
    return parser.parse_args()


def main() -> None:
    ensure_utf8_stdout()
    args = parse_args()
    singer_inputs = args.singer or list(DEFAULT_SINGER_INPUTS)
    configs = [parse_singer_input(value) for value in singer_inputs]
    output_dir = args.output.parent
    datasets = [build_dataset(config) for config in configs]
    for dataset in datasets:
        dump_json(output_dir / f"{dataset['slug']}.json", dataset)
    catalog = build_catalog(datasets)
    dump_json(args.output, catalog)
    print(json.dumps(catalog["totals"], ensure_ascii=False, indent=2))
    print(f"saved: {args.output}")


if __name__ == "__main__":
    main()
