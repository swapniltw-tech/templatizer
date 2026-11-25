"""Application configuration. The only module that reads the environment.

Implements: SCR-010 (single reader), SCR-011 (typed BaseSettings, extra=forbid, SecretStr),
SCR-012 (no plain-env secrets outside local), TEC-018 (pydantic v2). Shape follows doc 06.
"""

from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, HttpUrl, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings loaded from environment variables (prefix APP_)."""

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",  # local development only; the file is absent when deployed (SCR-015)
        env_file_encoding="utf-8",
        extra="forbid",  # unknown keys in the .env file fail fast
        frozen=True,
    )

    service_name: str = "reference-service"
    environment: Literal["local", "dev", "test", "prod"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    # Bind address. Loopback by default; the container sets APP_HOST=0.0.0.0 (see Dockerfile).
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)
    request_timeout_s: float = Field(default=10.0, gt=0, le=120)

    # Non-secret pointer to where secrets live. Add SecretStr fields only together with the
    # Key Vault adapter (SCR-013); outside local they MUST come from the vault, not the env.
    key_vault_url: HttpUrl | None = None

    @model_validator(mode="after")
    def _check_environment_rules(self) -> Self:
        if self.environment != "local" and self.key_vault_url is None:
            msg = "APP_KEY_VAULT_URL is required outside the local environment"
            raise ValueError(msg)
        return self


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings (validated once, fails fast at startup)."""
    return Settings()
