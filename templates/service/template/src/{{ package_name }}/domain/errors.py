"""Typed domain errors (python-style rule: never return error strings)."""


class DomainError(Exception):
    """Base class for all domain errors."""
