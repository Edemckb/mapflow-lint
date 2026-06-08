# mapflow-lint

[![CI](https://github.com/Edemckb/mapflow-lint/actions/workflows/ci.yml/badge.svg)](https://github.com/Edemckb/mapflow-lint/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

`mapflow-lint` generates and audits explainable level-design route plans before production map work begins.

It focuses on player traversal rather than decorative tile placement: critical paths, optional branches, meaningful rewards, encounter pacing, recovery before a climax, return paths, and unreachable content.

## Why this exists

A map can be technically valid and still be difficult to read, empty, repetitive, or impossible to complete safely. This project turns reusable level-design principles into a small CLI and a set of public workflows that can run before and during implementation.

## Install

```bash
python -m pip install .
```

## Generate a route plan

```bash
mapflow-lint generate routes/ruins.json \
  --name "Sunken Archive" \
  --archetype ruins \
  --branches 2 \
  --seed 7
```

Available archetypes: `dungeon`, `ruins`, `fortress`, and `forest`.

## Audit a route

```bash
mapflow-lint audit examples/ruins-route.json
mapflow-lint audit --strict examples/ruins-route.json
mapflow-lint audit --json examples/ruins-route.json
```

The strict quality gate requires a score of at least 85 with no warnings.

## What it checks

- one readable entrance and at least one exit
- all nodes are reachable
- optional branches have return paths
- branches provide meaningful rewards
- climax encounters have enough buildup
- recovery or a safe read exists before a boss
- combat pacing avoids unexplained repetition
- dead ends and missing graph connections are reported

## Reusable workflows

- [`workflows/route-design-plan.md`](workflows/route-design-plan.md): route-first planning before tile placement
- [`workflows/map-review-checklist.md`](workflows/map-review-checklist.md): structural and playtest review
- [CI quality gate](.github/workflows/ci.yml): tests generated and example routes
- [route audit workflow](.github/workflows/audit-routes.yml): audits changed route plans in pull requests

These workflows are engine-agnostic. They can be adapted to RPG Maker, Unity, Godot, Unreal, or custom engines.

## Route schema

```json
{
  "name": "Example Route",
  "genre": "dungeon",
  "nodes": [
    {"id": "entrance", "type": "entrance", "label": "Entrance"},
    {"id": "boss", "type": "boss", "label": "Boss"},
    {"id": "exit", "type": "exit", "label": "Exit"}
  ],
  "edges": [
    {"from": "entrance", "to": "boss"},
    {"from": "boss", "to": "exit"}
  ]
}
```

## Development

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
mapflow-lint audit --strict examples/ruins-route.json
```

## Roadmap

- adapters for engine-specific map formats
- graph visualisation
- encounter-density and traversal-distance metrics
- annotated playtest reports

## License

MIT

