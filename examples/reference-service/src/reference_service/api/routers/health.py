"""Liveness and readiness probes (REL-019).

Liveness never checks dependencies. Readiness reflects ability to serve; this template has no
dependencies yet, so it only reports that the process is up. Add port health checks here when
adapters are added.

Both operations are intentionally unauthenticated (platform probes), declared with an explicit
empty `security` list so API-007 ("no operation is public by default") is visibly a decision.
"""

from fastapi import APIRouter

from reference_service.api.schemas.health import StatusResponse

router = APIRouter(tags=["probes"])

_PUBLIC: dict[str, object] = {"security": []}


@router.get("/livez", operation_id="get_livez", openapi_extra=_PUBLIC)
def livez() -> StatusResponse:
    """The process is running."""
    return StatusResponse(status="ok")


@router.get("/readyz", operation_id="get_readyz", openapi_extra=_PUBLIC)
def readyz() -> StatusResponse:
    """The service can accept traffic."""
    return StatusResponse(status="ok")
