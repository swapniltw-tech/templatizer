# reference-service

Reference service generated from the template: one synthetic premium-estimate endpoint.

- **Owner:** `@example-org/platform-team` (see `CODEOWNERS`)
- **Runbook:** TODO: add `docs/runbooks/` (doc 18 owns the template) before production use.
- **API contract:** [`docs/api/openapi.yaml`](docs/api/openapi.yaml)
- **Decisions:** [`docs/adr/`](docs/adr/)

## Getting started

```bash
make install   # creates .venv from uv.lock
make run       # serves on http://127.0.0.1:8000 (see .env.example for settings)
make check     # the same gate CI runs
```

Generated from the engineering-standards Copier template. See `AGENTS.md` for the agent workflow and the standards each task should read.
