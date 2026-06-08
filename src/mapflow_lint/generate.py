from __future__ import annotations

import random

from .model import Node, Route


ARCHETYPES = {
    "dungeon": ("exploration", "encounter", "puzzle"),
    "ruins": ("exploration", "puzzle", "encounter"),
    "fortress": ("encounter", "exploration", "elite"),
    "forest": ("exploration", "encounter", "exploration"),
}


def generate_route(
    *,
    name: str,
    archetype: str = "dungeon",
    branches: int = 1,
    seed: int = 1,
) -> Route:
    if archetype not in ARCHETYPES:
        raise ValueError(f"Unknown archetype: {archetype}")
    if not 0 <= branches <= 3:
        raise ValueError("branches must be between 0 and 3")

    randomiser = random.Random(seed)
    middle = list(ARCHETYPES[archetype])
    randomiser.shuffle(middle)

    nodes = [
        Node("entrance", "entrance", "Readable entrance"),
        Node("read", middle[0], "First safe read"),
        Node("pressure", middle[1], "First pressure point"),
        Node("escalation", middle[2], "Route escalation"),
        Node("safe", "safe", "Recovery before climax"),
        Node("boss", "boss", "Climax encounter"),
        Node("exit", "exit", "Return or onward path"),
    ]
    edges = [
        ("entrance", "read"),
        ("read", "pressure"),
        ("pressure", "escalation"),
        ("escalation", "safe"),
        ("safe", "boss"),
        ("boss", "exit"),
    ]

    branch_types = ["reward", "puzzle", "elite"]
    for index in range(branches):
        branch_type = branch_types[index]
        branch_id = f"branch-{index + 1}"
        reward_id = f"branch-reward-{index + 1}"
        nodes.extend(
            [
                Node(branch_id, branch_type, f"Optional {branch_type} branch"),
                Node(reward_id, "reward", "Meaningful branch reward"),
            ]
        )
        branch_from = "read" if index % 2 == 0 else "pressure"
        branch_return = "pressure" if index % 2 == 0 else "escalation"
        edges.extend(
            [
                (branch_from, branch_id),
                (branch_id, reward_id),
                (reward_id, branch_return),
            ]
        )

    return Route(name=name, genre=archetype, nodes=tuple(nodes), edges=tuple(edges))

