from __future__ import annotations

from collections import Counter, deque
from dataclasses import asdict, dataclass
from typing import Optional

from .model import Route, VALID_NODE_TYPES


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    node: Optional[str] = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class AuditReport:
    route: str
    score: int
    findings: tuple[Finding, ...]
    metrics: dict[str, int]

    @property
    def errors(self) -> int:
        return sum(item.severity == "error" for item in self.findings)

    @property
    def warnings(self) -> int:
        return sum(item.severity == "warning" for item in self.findings)

    @property
    def passed(self) -> bool:
        return self.errors == 0 and self.score >= 70

    def to_dict(self) -> dict[str, object]:
        return {
            "route": self.route,
            "score": self.score,
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "metrics": self.metrics,
            "findings": [item.to_dict() for item in self.findings],
        }


def _adjacency(route: Route) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    outgoing = {node.id: [] for node in route.nodes}
    incoming = {node.id: [] for node in route.nodes}
    for source, target in route.edges:
        if source in outgoing:
            outgoing[source].append(target)
        if target in incoming:
            incoming[target].append(source)
    return outgoing, incoming


def _reachable(start: str, adjacency: dict[str, list[str]]) -> set[str]:
    visited: set[str] = set()
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        queue.extend(adjacency.get(node, []))
    return visited


def _reachable_from_many(starts: list[str], adjacency: dict[str, list[str]]) -> set[str]:
    visited: set[str] = set()
    queue = deque(starts)
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        queue.extend(adjacency.get(node, []))
    return visited


def _shortest_distance(start: str, goal: str, adjacency: dict[str, list[str]]) -> Optional[int]:
    queue = deque([(start, 0)])
    visited: set[str] = set()
    while queue:
        node, distance = queue.popleft()
        if node == goal:
            return distance
        if node in visited:
            continue
        visited.add(node)
        queue.extend((target, distance + 1) for target in adjacency.get(node, []))
    return None


def audit_route(route: Route) -> AuditReport:
    findings: list[Finding] = []
    ids = [node.id for node in route.nodes]
    counts = Counter(ids)
    node_map = route.node_map

    for node_id, count in counts.items():
        if count > 1:
            findings.append(Finding("error", "duplicate-node-id", "Node IDs must be unique.", node_id))

    for node in route.nodes:
        if node.type not in VALID_NODE_TYPES:
            findings.append(Finding("error", "unknown-node-type", f"Unknown node type '{node.type}'.", node.id))

    for source, target in route.edges:
        if source not in node_map:
            findings.append(Finding("error", "missing-edge-source", "Edge source does not exist.", source))
        if target not in node_map:
            findings.append(Finding("error", "missing-edge-target", "Edge target does not exist.", target))
        if source == target:
            findings.append(Finding("warning", "self-loop", "Self-loops rarely create meaningful traversal.", source))

    outgoing, incoming = _adjacency(route)
    entrances = [node.id for node in route.nodes if node.type == "entrance"]
    bosses = [node.id for node in route.nodes if node.type == "boss"]
    exits = [node.id for node in route.nodes if node.type == "exit"]

    if len(entrances) != 1:
        findings.append(Finding("error", "entrance-count", "A route should have exactly one entrance."))
    if not exits:
        findings.append(Finding("error", "missing-exit", "Add a clear exit or return path."))
    if not bosses:
        findings.append(Finding("warning", "missing-climax", "Add a boss or equivalent climax for this route."))

    reachable: set[str] = set()
    if len(entrances) == 1:
        reachable = _reachable(entrances[0], outgoing)
        for node in route.nodes:
            if node.id not in reachable:
                findings.append(Finding("error", "unreachable-node", "Node cannot be reached from the entrance.", node.id))

    can_reach_exit: set[str] = set()
    if exits:
        can_reach_exit = _reachable_from_many(exits, incoming)
        for node_id in sorted(reachable - can_reach_exit):
            findings.append(Finding("error", "no-exit-path", "Reachable node cannot lead to an exit.", node_id))

    for node in route.nodes:
        if node.id not in entrances and not incoming.get(node.id):
            findings.append(Finding("warning", "no-entry", "Node has no incoming path.", node.id))
        if node.type not in {"exit"} and not outgoing.get(node.id):
            findings.append(Finding("warning", "dead-end", "Dead end has no explicit return path.", node.id))

    branch_nodes = [node.id for node in route.nodes if len(outgoing.get(node.id, [])) > 1]
    rewards = [node.id for node in route.nodes if node.type == "reward"]
    safe_nodes = [node.id for node in route.nodes if node.type == "safe"]
    combat_nodes = [node.id for node in route.nodes if node.type in {"encounter", "elite", "boss"}]

    if not branch_nodes:
        findings.append(Finding("warning", "no-branch", "The route has no meaningful optional branch."))
    if branch_nodes and not rewards:
        findings.append(Finding("warning", "branch-without-reward", "Branches should offer information, resources, or progression."))

    if bosses and entrances:
        for boss in bosses:
            distance = _shortest_distance(entrances[0], boss, outgoing)
            if distance is not None and distance < 4:
                findings.append(Finding("warning", "boss-too-early", "The climax arrives before enough buildup.", boss))
            predecessors = incoming.get(boss, [])
            if not any(node_map.get(node_id) and node_map[node_id].type == "safe" for node_id in predecessors):
                findings.append(Finding("warning", "no-safe-before-boss", "Place recovery or a safe read immediately before the boss.", boss))

    pressure_types = {"encounter", "elite", "boss"}
    for node in route.nodes:
        if node.type not in pressure_types:
            continue
        has_pressure_before = any(
            node_map.get(source) and node_map[source].type in pressure_types
            for source in incoming.get(node.id, [])
        )
        has_pressure_after = any(
            node_map.get(target) and node_map[target].type in pressure_types
            for target in outgoing.get(node.id, [])
        )
        if has_pressure_before and has_pressure_after:
            findings.append(
                Finding(
                    "warning",
                    "combat-fatigue",
                    "Three pressure beats in a row need a recovery, read, or new decision.",
                    node.id,
                )
            )

    errors = sum(item.severity == "error" for item in findings)
    warnings = sum(item.severity == "warning" for item in findings)
    score = max(
        0,
        min(
            100,
            100
            - errors * 18
            - warnings * 6
            - (10 if len(route.nodes) < 6 else 0),
        ),
    )
    metrics = {
        "nodes": len(route.nodes),
        "edges": len(route.edges),
        "branches": len(branch_nodes),
        "rewards": len(rewards),
        "safe_nodes": len(safe_nodes),
        "combat_nodes": len(combat_nodes),
        "reachable_nodes": len(reachable),
    }
    return AuditReport(route.name, score, tuple(findings), metrics)
