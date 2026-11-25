---
status: proposed
date: 2026-11-25
decision-makers: Architecture lead, Platform Engineering lead
consulted: Security lead
informed: Engineering teams
---

# Use FastAPI as the HTTP framework

<!-- Drafted by the template author. Implements ARC-029 (new external dependency needs an ADR) and
ARC-031 (an agent drafts; a human sets status to accepted). The standards do not name a web
framework (docs/FINDINGS.md F-01); this ADR records the template's working assumption. -->

## Context and Problem Statement
The standards require pydantic v2 request and response models (API-003), an OpenAPI document (API-001) and problem-details errors (API-009), but name no web framework. The template needs one to ship health probes and example endpoints.

## Decision Drivers
- First-class pydantic v2 models and generated OpenAPI (drift test, API-002)
- Typed (`mypy --strict`) and testable without sockets (`--disable-socket`, TST-008)
- Doc 03's import contracts already treat `fastapi` as the framework to keep out of `domain/`

## Considered Options
- Do nothing: no HTTP framework (the template could not serve probes)
- FastAPI with uvicorn
- Another ASGI framework (for example Litestar)

## Decision Outcome
Chosen option: "FastAPI with uvicorn" as the template default, pending acceptance, because it satisfies the drivers with the least custom code.

### Consequences
- Good: pydantic models double as the OpenAPI source; TestClient needs no network
- Bad: adds `fastapi`, `uvicorn` and their transitive dependencies to the licence and vulnerability review (doc 20)

### Confirmation
`tests/contract/test_openapi_contract.py` (drift), `lint-imports` (framework stays out of `domain/`), `make security` (dependency audit).

## More Information
Related rules: API-001, API-002, API-003, API-009, ARC-002, ARC-029, TEC-021. Template findings: F-01.
