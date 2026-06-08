from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Union


VALID_NODE_TYPES = {
    "entrance",
    "exploration",
    "encounter",
    "elite",
    "puzzle",
    "reward",
    "safe",
    "shortcut",
    "boss",
    "exit",
}


@dataclass(frozen=True)
class Node:
    id: str
    type: str
    label: str


@dataclass(frozen=True)
class Route:
    name: str
    genre: str
    nodes: tuple[Node, ...]
    edges: tuple[tuple[str, str], ...]

    @property
    def node_map(self) -> dict[str, Node]:
        return {node.id: node for node in self.nodes}


def load_route(path: Union[str, Path]) -> Route:
    route_path = Path(path)
    value: dict[str, Any] = json.loads(route_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("route document must be a JSON object")
    if not isinstance(value.get("nodes", []), list):
        raise ValueError("'nodes' must be a JSON array")
    if not isinstance(value.get("edges", []), list):
        raise ValueError("'edges' must be a JSON array")
    nodes = tuple(
        Node(str(node["id"]), str(node["type"]), str(node.get("label", node["id"])))
        for node in value.get("nodes", [])
    )
    edges = tuple((str(edge["from"]), str(edge["to"])) for edge in value.get("edges", []))
    return Route(
        name=str(value.get("name", route_path.stem)),
        genre=str(value.get("genre", "unspecified")),
        nodes=nodes,
        edges=edges,
    )


def route_to_dict(route: Route) -> dict[str, object]:
    return {
        "name": route.name,
        "genre": route.genre,
        "nodes": [
            {"id": node.id, "type": node.type, "label": node.label}
            for node in route.nodes
        ],
        "edges": [{"from": source, "to": target} for source, target in route.edges],
    }


def save_route(route: Route, path: Union[str, Path]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(route_to_dict(route), indent=2) + "\n", encoding="utf-8")
    return output
