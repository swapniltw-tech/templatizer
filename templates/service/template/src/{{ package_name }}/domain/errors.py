"""Typed domain errors (API-012 stable codes; ARC-013 mapped in api/errors.py)."""


class DomainError(Exception):
    """Base class for all domain errors. `code` is the stable machine-readable code (API-012)."""

    code = "domain_error"
