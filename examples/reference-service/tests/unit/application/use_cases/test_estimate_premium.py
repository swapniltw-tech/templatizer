"""Use case maps the domain result into a PremiumEstimate."""

from reference_service.application.use_cases.estimate_premium import estimate_premium


def test_estimate_carries_inputs_and_premium() -> None:
    estimate = estimate_premium(25_000_000, 20)
    assert (estimate.coverage_cents, estimate.term_years) == (25_000_000, 20)
    assert estimate.monthly_premium_cents == 2_917
