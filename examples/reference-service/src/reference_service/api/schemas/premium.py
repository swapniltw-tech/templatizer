"""Transport schemas for the premium-estimate endpoint (API-003, API-004, API-008)."""

from pydantic import BaseModel, ConfigDict, Field


class PremiumEstimateQuery(BaseModel):
    """Query parameters. Unknown parameters are rejected (API-008)."""

    model_config = ConfigDict(extra="forbid")

    coverage_cents: int = Field(
        ge=1, le=10**12, description="Coverage amount in cents", examples=[25_000_000]
    )
    term_years: int = Field(ge=1, le=40, description="Term in years", examples=[20])


class PremiumEstimateResponse(BaseModel):
    """Estimated monthly premium (synthetic toy rule)."""

    model_config = ConfigDict(extra="forbid")

    coverage_cents: int
    term_years: int
    monthly_premium_cents: int = Field(description="Monthly premium in cents, rounded up")
