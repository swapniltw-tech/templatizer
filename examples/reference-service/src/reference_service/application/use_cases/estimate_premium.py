"""Use case: estimate a monthly premium (ARC-003, ARC-011). No ports needed: the rule is pure."""

from reference_service.domain.models.premium_estimate import PremiumEstimate
from reference_service.domain.rules.premium import monthly_premium_cents


def estimate_premium(coverage_cents: int, term_years: int) -> PremiumEstimate:
    """Return the estimate for the given coverage and term."""
    return PremiumEstimate(
        coverage_cents=coverage_cents,
        term_years=term_years,
        monthly_premium_cents=monthly_premium_cents(coverage_cents, term_years),
    )
