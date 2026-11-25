"""Transport schema for the probe endpoints (API-003, API-004, API-008)."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class StatusResponse(BaseModel):
    """Body of /livez and /readyz."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]
