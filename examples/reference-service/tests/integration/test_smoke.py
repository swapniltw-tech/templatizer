"""Smoke test so `make test-integration` never exits with status 5 (TEC-012).

Replace with real-dependency tests (containers or emulators) as adapters are added (TST-014).
"""

import pytest
from fastapi.testclient import TestClient

from reference_service.config import Settings
from reference_service.main import create_app


@pytest.mark.integration
def test_app_serves_through_the_full_asgi_stack() -> None:
    with TestClient(create_app(Settings(_env_file=None))) as client:
        assert client.get("/readyz").status_code == 200
