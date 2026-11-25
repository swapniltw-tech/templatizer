"""Premium rule: examples and property tests for invariants (TST-020)."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from reference_service.domain.rules.premium import (
    MAX_COVERAGE_CENTS,
    MAX_TERM_YEARS,
    InvalidEstimateInputError,
    monthly_premium_cents,
)

coverage = st.integers(min_value=1, max_value=MAX_COVERAGE_CENTS)
term = st.integers(min_value=1, max_value=MAX_TERM_YEARS)


def test_known_value() -> None:
    # 25,000,000 cents at 14 bp a year = 35,000 cents; /12 = 2,916.67, rounded up
    assert monthly_premium_cents(25_000_000, 20) == 2_917


def test_rounds_up_to_the_next_cent() -> None:
    assert monthly_premium_cents(1, 1) == 1


@pytest.mark.parametrize("bad", [0, -1, MAX_COVERAGE_CENTS + 1])
def test_rejects_coverage_out_of_range(bad: int) -> None:
    with pytest.raises(InvalidEstimateInputError):
        monthly_premium_cents(bad, 10)


@pytest.mark.parametrize("bad", [0, -5, MAX_TERM_YEARS + 1])
def test_rejects_term_out_of_range(bad: int) -> None:
    with pytest.raises(InvalidEstimateInputError):
        monthly_premium_cents(100_000, bad)


@given(coverage, term)
def test_premium_is_positive(c: int, t: int) -> None:
    assert monthly_premium_cents(c, t) >= 1


@given(coverage, coverage, term)
def test_premium_is_monotonic_in_coverage(c1: int, c2: int, t: int) -> None:
    low, high = sorted((c1, c2))
    assert monthly_premium_cents(low, t) <= monthly_premium_cents(high, t)


@given(coverage, term, term)
def test_premium_is_monotonic_in_term(c: int, t1: int, t2: int) -> None:
    low, high = sorted((t1, t2))
    assert monthly_premium_cents(c, low) <= monthly_premium_cents(c, high)
