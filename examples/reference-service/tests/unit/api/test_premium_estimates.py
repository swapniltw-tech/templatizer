"""Premium-estimate endpoint: success and problem-details failures (API-009, API-013)."""

import pytest
from fastapi.testclient import TestClient

from reference_service.config import Settings
from reference_service.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app(Settings(_env_file=None)))


def test_returns_the_estimate(client: TestClient) -> None:
    response = client.get(
        "/v1/premium-estimates", params={"coverage_cents": 25_000_000, "term_years": 20}
    )
    assert response.status_code == 200
    assert response.json() == {
        "coverage_cents": 25_000_000,
        "term_years": 20,
        "monthly_premium_cents": 2_917,
    }


@pytest.mark.parametrize(
    "params",
    [
        {"coverage_cents": 0, "term_years": 10},
        {"coverage_cents": 100, "term_years": 41},
        {"coverage_cents": 100},
        {"coverage_cents": "abc", "term_years": 10},
        {"coverage_cents": 100, "term_years": 10, "extra": 1},
    ],
)
def test_invalid_input_returns_422_problem_with_pointers(
    client: TestClient, params: dict[str, object]
) -> None:
    response = client.get("/v1/premium-estimates", params=params)  # type: ignore[arg-type]  # test passes mixed types on purpose
    body = response.json()
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")
    assert body["status"] == 422
    assert body["code"] == "validation_error"
    assert body["errors"]
    assert all(e["pointer"].startswith("/query/") for e in body["errors"])
