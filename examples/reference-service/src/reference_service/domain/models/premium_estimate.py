"""Domain model for a premium estimate."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PremiumEstimate:
    """Result of estimating a monthly premium. Amounts are integer cents."""

    coverage_cents: int
    term_years: int
    monthly_premium_cents: int
