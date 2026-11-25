"""Typed domain errors (python-style rule: never return error strings)."""


class DomainError(Exception):
    """Base class for all domain errors. `code` is the stable machine-readable code (API-012)."""

    code = "domain_error"
