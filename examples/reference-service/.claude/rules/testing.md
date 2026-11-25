---
paths:
  - "tests/**"
  - "evals/**"
---

# Tests and evals

- Write the failing test first, then the code. Never weaken, skip or delete a test to make it pass.
- Unit tests never call the network or a live model; inject the fake model client.
- Test data is synthetic. Never paste real customer data or real identifiers.
- Mirror the source tree: `tests/unit/<layer>/test_<module>.py`; name tests `test_<behavior>`.
- Mark slow or external tests with `@pytest.mark.integration`; model-quality checks with `@pytest.mark.eval`.
