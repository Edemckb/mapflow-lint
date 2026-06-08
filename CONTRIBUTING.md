# Contributing

Contributions are welcome for new route archetypes, explainable audit rules, examples, and engine adapters.

1. Start from `workflows/route-design-plan.md`.
2. Add a focused route fixture or unit test.
3. Run `python -m unittest discover -s tests -v`.
4. Run `mapflow-lint audit --strict examples/ruins-route.json`.
5. Explain the player-facing problem solved by the rule.

Rules should remain engine-agnostic and understandable without machine learning.

