"""Premium-estimate rule.

SYNTHETIC TOY RULE for demonstrating the layers: it is not an actuarial calculation and must not
be used for pricing. Money is integer cents, never floats (doc 24 TST-020 names money logic as
needing property tests).
"""

from reference_service.domain.errors import DomainError

MIN_TERM_YEARS = 1
MAX_TERM_YEARS = 40
MIN_COVERAGE_CENTS = 1
MAX_COVERAGE_CENTS = 10**12
_BASE_RATE_BASIS_POINTS = 10
_BASIS_POINTS = 10_000
_MONTHS = 12


class InvalidEstimateInputError(DomainError):
    """The coverage amount or term is outside the supported range."""

    code = "invalid_estimate_input"


def monthly_premium_cents(coverage_cents: int, term_years: int) -> int:
    """Return the monthly premium in cents, rounded up.

    Annual rate is 10 basis points of coverage plus 1 basis point per five years of term.
    """
    if not MIN_COVERAGE_CENTS <= coverage_cents <= MAX_COVERAGE_CENTS:
        msg = "coverage out of range"
        raise InvalidEstimateInputError(msg)
    if not MIN_TERM_YEARS <= term_years <= MAX_TERM_YEARS:
        msg = "term out of range"
        raise InvalidEstimateInputError(msg)
    rate_basis_points = _BASE_RATE_BASIS_POINTS + term_years // 5
    annual_numerator = coverage_cents * rate_basis_points
    divisor = _BASIS_POINTS * _MONTHS
    return -(-annual_numerator // divisor)
