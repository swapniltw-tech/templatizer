"""Smoke test so `make eval` never exits with status 5 (TEC-012).

No model code exists yet (the AI layer is out of scope for this template). Replace with real evals
per docs/14-evals-and-testing-ai.md; datasets must be synthetic and thresholds live in
evals/<suite>/thresholds.yaml.
"""

import pytest


@pytest.mark.eval
def test_eval_marker_selects_this_suite(request: pytest.FixtureRequest) -> None:
    assert request.node.get_closest_marker("eval") is not None
