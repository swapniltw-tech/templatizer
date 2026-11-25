---
paths:
  - "src/*/api/**"
  - "docs/api/**"
  - "tests/contract/**"
---

# HTTP API code

<!-- Implements AGT-010, AGT-011. Review-tagged rules only; CI already checks the OpenAPI drift test (API-002). -->

- Routers parse input, call one use case, map the result or error. No business rules (ARC-011).
- Map transport schemas to domain models explicitly; never return a domain model from an endpoint (ARC-012, API-004).
- Request and response bodies are pydantic v2 models with types, constraints and examples; never a bare `dict` (API-003).
- Reject unknown request fields (`extra="forbid"`) and set max lengths, array sizes and numeric ranges (API-008).
- Every operation declares its auth scheme and scope; none is public by default (API-007). Probes are the one declared exception.
- Errors are problem details built in `api/errors.py` only; no stack traces, SQL, hostnames, secrets or personal data in bodies (API-014, API-011, ARC-013).
- Give errors a stable `code`; `type` is an absolute documented URI, `about:blank` only for plain HTTP semantics (API-012, API-010).
- Change `docs/api/openapi.yaml` first, in the same MR as the behavior (run `scripts/export_openapi.py`) (API-001).
- Version in the URL path (`/v1/`) and announce deprecation in the OpenAPI document (API-020, API-022).
- Paginate every list endpoint with a bounded `limit` and an opaque cursor (API-017); return 202 plus a status resource for long work (API-019).
- Consumers ignore unknown response fields; providers never reuse a removed field name (API-023).
