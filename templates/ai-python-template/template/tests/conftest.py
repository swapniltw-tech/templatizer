"""Shared pytest setup. Hypothesis profiles per doc 24 (TST-024): `dev` locally, `gate` in CI."""

import os

from hypothesis import settings

settings.register_profile("dev", max_examples=50)
settings.register_profile("gate", max_examples=200, derandomize=True, deadline=None)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "dev"))
