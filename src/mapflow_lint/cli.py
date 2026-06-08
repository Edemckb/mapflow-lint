from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Optional, Sequence

from .audit import audit_route
from .generate import ARCHETYPES, generate_route
from .model import load_route, save_route


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mapflow-lint",
        description="Generate and audit explainable level-design route plans.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    generate = commands.add_parser("generate", help="Generate a route-plan JSON file")
    generate.add_argument("output", type=Path)
    generate.add_argument("--name", default="Generated Route")
    generate.add_argument("--archetype", choices=sorted(ARCHETYPES), default="dungeon")
    generate.add_argument("--branches", type=int, default=1)
    generate.add_argument("--seed", type=int, default=1)

    audit = commands.add_parser("audit", help="Audit a route-plan JSON file")
    audit.add_argument("path", type=Path)
    audit.add_argument("--json", action="store_true", dest="as_json")
    audit.add_argument("--strict", action="store_true", help="Fail below a score of 85 or on any warning")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "generate":
        try:
            route = generate_route(
                name=args.name,
                archetype=args.archetype,
                branches=args.branches,
                seed=args.seed,
            )
            output = save_route(route, args.output)
        except (OSError, ValueError) as error:
            print(f"mapflow-lint: {error}", file=sys.stderr)
            return 2
        print(f"Generated {len(route.nodes)} nodes and {len(route.edges)} edges in {output}.")
        return 0

    try:
        report = audit_route(load_route(args.path))
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        print(f"mapflow-lint: could not read {args.path}: {error}", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        status = "PASS" if report.passed else "REVISE"
        print(
            f"{status} {report.route}: {report.score}/100 "
            f"({report.errors} errors, {report.warnings} warnings)"
        )
        print(
            "  "
            + ", ".join(f"{key}={value}" for key, value in report.metrics.items())
        )
        for finding in report.findings:
            node = f" [{finding.node}]" if finding.node else ""
            print(f"  {finding.severity.upper():7} {finding.code}{node} - {finding.message}")
    if args.strict:
        return int(report.errors > 0 or report.warnings > 0 or report.score < 85)
    return int(not report.passed)
