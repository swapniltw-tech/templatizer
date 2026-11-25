"""Domain model for a premium estimate (STR-008, ARC-012: never returned by an endpoint as is)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PremiumEstimate:
    """Result of estimating a monthly premium. Amounts are integer cents."""

    coverage_cents: int
    term_years: int
    monthly_premium_cents: int
