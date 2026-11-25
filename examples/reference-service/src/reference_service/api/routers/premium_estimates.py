"""Premium-estimate endpoint: parse input, call one use case, map the result (ARC-011, ARC-012).

TODO: no authentication or authorization exists in the template, so the operation is declared
public (`security: []`, API-007). Add the org's auth scheme and a deny-path test (TST-046) before
exposing a real endpoint; docs/FINDINGS.md F-17.
"""

from typing import Annotated

from fastapi import APIRouter, Query

from reference_service.api.schemas.premium import PremiumEstimateQuery, PremiumEstimateResponse
from reference_service.application.use_cases.estimate_premium import estimate_premium

router = APIRouter(prefix="/v1", tags=["premium-estimates"])


@router.get(
    "/premium-estimates",
    operation_id="get_premium_estimate",
    openapi_extra={"security": []},
)
def get_premium_estimate(
    query: Annotated[PremiumEstimateQuery, Query()],
) -> PremiumEstimateResponse:
    """Estimate the monthly premium for a coverage amount and term (synthetic toy rule)."""
    estimate = estimate_premium(query.coverage_cents, query.term_years)
    return PremiumEstimateResponse(
        coverage_cents=estimate.coverage_cents,
        term_years=estimate.term_years,
        monthly_premium_cents=estimate.monthly_premium_cents,
    )
