---
paths:
  - "src/*/domain/**"
  - "src/*/application/**"
---

# Domain and application code

<!-- Implements AGT-010, AGT-011. `domain/` purity is enforced by import contracts (ARC-002, STR-008). -->

- Write a business rule that can be code as deterministic code in `domain/`, never as a model call (ARC-014).
- Inject dependencies by constructor or function parameter against a `Protocol` from `application/ports.py`; no global singletons or module-level clients (ARC-010).
- Name things in domain language (`PremiumQuote`, `is_eligible_for_waiver`), not `process` or `utils` (CLN-010, STR-019).
- Make domain values immutable (frozen dataclasses or models); no module-level mutable state (CLN-008).
- Signal failure by raising a specific domain exception from `domain/errors.py` with a stable `code`; never return error strings or `None` for failure (CLN-019).
- Keep functions small and linear: early returns and guard clauses over nesting (CLN-005).
- Cite the source of a business-rule comment by identifier or document name (CLN-031).
- Money is integer cents, never floats; add Hypothesis property tests for invariants (TST-020).
