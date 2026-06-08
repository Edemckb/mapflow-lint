from pathlib import Path
import tempfile
import unittest

from mapflow_lint import audit_route, generate_route
from mapflow_lint.model import Node, Route, load_route, save_route


class MapflowTests(unittest.TestCase):
    def test_generated_route_passes_quality_gate(self) -> None:
        route = generate_route(name="Ashen Ruins", archetype="ruins", branches=2, seed=7)
        report = audit_route(route)
        self.assertEqual(report.errors, 0)
        self.assertEqual(report.warnings, 0)
        self.assertGreaterEqual(report.score, 85)

    def test_missing_return_path_is_reported(self) -> None:
        route = Route(
            name="Broken Branch",
            genre="dungeon",
            nodes=(
                Node("start", "entrance", "Start"),
                Node("fight", "encounter", "Fight"),
                Node("reward", "reward", "Reward"),
                Node("exit", "exit", "Exit"),
            ),
            edges=(("start", "fight"), ("fight", "exit"), ("fight", "reward")),
        )
        codes = {item.code for item in audit_route(route).findings}
        self.assertIn("dead-end", codes)
        self.assertIn("no-exit-path", codes)

    def test_boss_requires_buildup_and_safe_node(self) -> None:
        route = Route(
            name="Rush",
            genre="fortress",
            nodes=(
                Node("start", "entrance", "Start"),
                Node("boss", "boss", "Boss"),
                Node("exit", "exit", "Exit"),
            ),
            edges=(("start", "boss"), ("boss", "exit")),
        )
        codes = {item.code for item in audit_route(route).findings}
        self.assertIn("boss-too-early", codes)
        self.assertIn("no-safe-before-boss", codes)

    def test_three_pressure_beats_trigger_pacing_warning(self) -> None:
        route = Route(
            name="Combat Corridor",
            genre="fortress",
            nodes=(
                Node("start", "entrance", "Start"),
                Node("fight-1", "encounter", "First fight"),
                Node("fight-2", "elite", "Second fight"),
                Node("fight-3", "encounter", "Third fight"),
                Node("safe", "safe", "Recovery"),
                Node("boss", "boss", "Boss"),
                Node("exit", "exit", "Exit"),
            ),
            edges=(
                ("start", "fight-1"),
                ("fight-1", "fight-2"),
                ("fight-2", "fight-3"),
                ("fight-3", "safe"),
                ("safe", "boss"),
                ("boss", "exit"),
            ),
        )
        codes = {item.code for item in audit_route(route).findings}
        self.assertIn("combat-fatigue", codes)

    def test_route_round_trip(self) -> None:
        route = generate_route(name="Forest Path", archetype="forest", branches=1, seed=3)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "route.json"
        save_route(route, path)
        self.assertEqual(load_route(path), route)


if __name__ == "__main__":
    unittest.main()
