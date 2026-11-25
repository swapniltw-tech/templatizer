"""OpenAPI contract tests (API-001, API-002 drift, API-005, TST-017; contract smoke, TEC-012)."""

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from reference_service.api.schemas.health import StatusResponse
from reference_service.api.schemas.premium import PremiumEstimateResponse
from reference_service.config import Settings
from reference_service.main import create_app

SPEC_PATH = Path(__file__).resolve().parents[2] / "docs" / "api" / "openapi.yaml"
APP = create_app(Settings(_env_file=None))


@pytest.mark.contract
def test_published_spec_matches_generated_schema() -> None:
    """Fails when docs/api/openapi.yaml is stale: run scripts/export_openapi.py and review."""
    published = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))
    assert published == APP.openapi()


@pytest.mark.contract
@pytest.mark.parametrize("path", ["/livez", "/readyz"])
def test_probe_responses_conform_to_the_spec(path: str) -> None:
    spec = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))
    operation = spec["paths"][path]["get"]
    assert operation["security"] == []  # API-007: public on purpose, visible in the contract
    assert "200" in operation["responses"]
    body = TestClient(APP).get(path).json()
    assert StatusResponse.model_validate(body).status == "ok"


@pytest.mark.contract
def test_premium_estimate_response_conforms_to_the_spec() -> None:
    spec = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))
    operation = spec["paths"]["/v1/premium-estimates"]["get"]
    assert operation["security"] == []  # public until the org auth scheme is added (F-17)
    assert {"200", "422"} <= set(operation["responses"])
    body = (
        TestClient(APP)
        .get("/v1/premium-estimates", params={"coverage_cents": 1_000_000, "term_years": 10})
        .json()
    )
    assert PremiumEstimateResponse.model_validate(body).term_years == 10
