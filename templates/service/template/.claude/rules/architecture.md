---
paths:
  - ".importlinter"
  - "tests/unit/architecture/**"
  - "docs/adr/**"
  - "src/*/adapters/**"
---

# Architecture boundaries and ADRs

<!-- Implements AGT-010, AGT-011. The import contracts themselves are enforced by `make lint` (ARC-015). -->

- Never edit `.importlinter` or `tests/unit/architecture/`, and never add `ignore_imports`, to make a violation pass (ARC-019).
- An `ignore_imports` entry needs an ADR or waiver reference and an expiry date in a comment (ARC-020); a human adds it, not an agent.
- Do not hide a boundary-crossing import behind `if TYPE_CHECKING:` (ARC-021).
- Outbound calls to other services live in `adapters/http_clients` behind a port, with timeouts and retries (ARC-027).
- A service owns its data store; talk to other services only through versioned APIs or events (ARC-023, ARC-024).
- Write an ADR for a new service, data store, external dependency or vendor SDK, top-level package, LLM pattern, or boundary exception (ARC-029).
- Put ADRs in `docs/adr/NNNN-short-title.md` using `0000-adr-template.md`; list at least two options, consequences and how the decision is verified (ARC-030, ARC-033).
- Draft ADRs as `proposed`; only a human sets `accepted`, and an accepted ADR is edited only for status (ARC-031, ARC-030).
