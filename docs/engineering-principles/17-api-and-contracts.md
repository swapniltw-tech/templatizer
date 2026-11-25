# API and Contracts

> **Owner:** Architecture lead (API standards) · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** RFC 9457 (Problem Details for HTTP APIs; read, obsoletes RFC 7807); spec.openapis.org (latest listed at read time: OpenAPI 3.2.1, 10 September 2026; only the first part of the page was read); RFC 9110 for `Accept-Language`, `Content-Language`, `Retry-After`, `Idempotency-Key` draft status are `VERIFY:`.

## Purpose
Every interface between services, and between an agent and its tools, is a written, versioned, testable contract. This doc owns HTTP API design, the error format, idempotency, pagination, versioning and deprecation, async and event schemas, locale handling in APIs and the principle that agent tool schemas are contracts. Boundary rules are in [03-architecture.md](./03-architecture.md). Contract test mechanics are in [24-testing-standards.md](./24-testing-standards.md). Tool manifests and registry rules are in [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md) (linked only; not restated here). Language and translation policy is in [22-localization-and-accessibility.md](./22-localization-and-accessibility.md).

## Decisions and tensions to know
- **OpenAPI-first vs pydantic as single source.** The plan lists both. Resolution used here: the reviewed `docs/api/openapi.yaml` is the **contract of record**; pydantic v2 models in `api/schemas/` are the **implementation**, and CI proves they agree (drift test). Do not maintain two unchecked descriptions.
- **OpenAPI version.** The specification site lists 3.2.1 as latest. `ASSUMPTION:` use the newest version your validators, codegen and gateway support (3.1.x is the safe floor, JSON Schema 2020-12 based, `VERIFY:`); record the choice in an ADR. Never hand-write features your tooling cannot validate.
- **RFC 9457** is confirmed as the current problem details RFC (obsoletes 7807). `VERIFY:` that the chosen web framework and API gateway emit `application/problem+json` correctly.

## Rules

### Contract-first
- **API-001** [MUST] [ci: openapi lint] Every HTTP API MUST have an OpenAPI document at `docs/api/openapi.yaml`, reviewed in the same merge request as any behaviour change, and validated by a linter in CI. `VERIFY:` linter choice (for example Spectral) and ruleset.
- **API-002** [MUST] [test] CI MUST fail when the running application's generated schema differs from `openapi.yaml` (drift test), or when a change breaks backward compatibility versus the default branch. `VERIFY:` diff tool.
- **API-003** [MUST] [review] Request and response bodies MUST be pydantic v2 models with explicit types, constraints and examples; handlers MUST NOT accept or return bare `dict`.
- **API-004** [MUST] [review] Domain entities MUST NOT be exposed directly; API schemas live in `api/schemas/` and are mapped to domain models (see doc 03).
- **API-005** [MUST] [test] Every operation MUST have a contract test (schema conformance of responses, including error responses); consumers MUST have consumer-driven or schema-based tests against providers they depend on.
- **API-006** [SHOULD] [review] Resources use plural nouns, standard verbs, `snake_case` or `camelCase` consistently across the org (`ASSUMPTION:` `snake_case`), ISO 8601 UTC timestamps and ISO 4217/ISO 3166 codes.
- **API-007** [MUST] [review] Every operation MUST declare its auth scheme and required scope or role; no operation is public by default. Authn and authz mechanics are owned by [02-security.md](./02-security.md).
- **API-008** [MUST] [review] Schemas MUST reject unknown fields on requests (`extra="forbid"` or equivalent) and MUST define maximum lengths, array sizes and numeric ranges.

### Errors (RFC 9457)
- **API-009** [MUST] [test] Error responses MUST use RFC 9457 problem details with media type `application/problem+json`, containing at least `type`, `title`, `status` and a correlation ID extension member (`trace_id`). `status` MUST equal the HTTP status.
- **API-010** [MUST] [review] `type` MUST be a stable, absolute URI identifying the problem type and resolving to documentation (`VERIFY:` hosting); if no specific type exists, use `about:blank` only for plain HTTP semantics.
- **API-011** [MUST] [review] Problem bodies MUST NOT contain stack traces, SQL, internal hostnames, secrets, prompts or personal data (RFC 9457 security guidance; see [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md)). `detail` is for humans and MUST NOT be parsed by clients.
- **API-012** [MUST] [review] Machine-readable branching MUST use an extension member `code` (stable, documented) and, for validation, an `errors` array with JSON pointer and `code`; extension members need at least three characters and start with a letter.
- **API-013** [MUST] [test] Validation errors return 422 (or 400 as chosen once per org, `ASSUMPTION:` 422); 401, 403, 404, 409, 429 and 5xx all use the same problem shape. 429 and 503 SHOULD include `Retry-After` (see [18-reliability-and-operations.md](./18-reliability-and-operations.md)).
- **API-014** [MUST] [review] The problem-details exception handler MUST live in `api/errors.py` and be the only place that maps exceptions to responses.

### Idempotency, pagination, concurrency
- **API-015** [MUST] [test] Non-idempotent operations that create or change state (POST, and PATCH where not naturally idempotent) MUST accept an `Idempotency-Key` header (`VERIFY:` header name; the IETF draft status) and return the stored result for a repeated key and identical request; a repeated key with a different body MUST return a conflict problem.
- **API-016** [MUST] [review] Idempotency records MUST be stored durably with a documented retention (`ASSUMPTION:` 24 hours or more) and scoped per caller identity.
- **API-017** [MUST] [review] List endpoints MUST paginate with a bounded `limit` (documented default and maximum) and an opaque cursor; unbounded lists MUST NOT exist.
- **API-018** [SHOULD] [review] Resources that can be modified concurrently SHOULD use `ETag` with `If-Match` and return 412 or 409 on conflict.
- **API-019** [MUST] [review] Long-running work MUST return 202 with a status resource rather than holding the request open beyond the API deadline.

### Versioning and deprecation
- **API-020** [MUST] [review] APIs MUST be versioned in the URL path (`/v1/`) or a documented header, chosen once org-wide (`ASSUMPTION:` path). Within a version, changes MUST be backward compatible: additive fields and endpoints only.
- **API-021** [MUST] [ci] Breaking changes (removing or renaming fields, tightening validation, changing types, status codes or semantics) MUST ship as a new major version; the compatibility check (API-002) enforces this.
- **API-022** [MUST] [review] Deprecation MUST be announced in the OpenAPI document (`deprecated: true`), in response headers (`VERIFY:` `Deprecation` and `Sunset` headers, RFC status), and to registered consumers, with a sunset date of at least `ASSUMPTION:` 6 months and usage telemetry showing remaining callers.
- **API-023** [MUST] [review] Consumers MUST ignore unknown response fields (tolerant reader); providers MUST NOT reuse removed field names with new meaning.

### Async and event schemas
- **API-024** [MUST] [ci] Every event or message type MUST have a versioned schema (JSON Schema or Avro, `ASSUMPTION:` JSON Schema) in a registry or in-repo `schemas/` directory, validated in CI. `ASSUMPTION:` platform decides whether Azure Schema Registry or Git-only; `VERIFY:`.
- **API-025** [MUST] [review] Events MUST carry an envelope with `id`, `type`, `version`, `source`, `time`, `correlation_id` and a data classification label; `VERIFY:` whether to adopt the CloudEvents specification as the envelope.
- **API-026** [MUST] [review] Schema evolution MUST be backward compatible for the supported consumer window; breaking changes use a new event type or version with dual publishing during migration.
- **API-027** [MUST] [test] Consumers MUST be idempotent and MUST dead-letter messages that fail schema validation (see doc 18). Event payloads MUST NOT contain personal data beyond what the data-classification matrix permits.

### Locale handling (EN/FR)
- **API-028** [MUST] [test] APIs that return user-facing text MUST honour `Accept-Language` (`en`, `fr`, `fr-CA`, `en-CA`), parse quality values, fall back to `en` (`ASSUMPTION:` default pending F6), and return `Content-Language` for the language actually used. `VERIFY:` against RFC 9110.
- **API-029** [MUST] [review] Machine-readable fields (`code`, `type`, enums, identifiers, dates, amounts) MUST be locale-independent. Only human text (`title`, `detail`, display labels) is localized; RFC 9457 allows `title` to vary only by localization.
- **API-030** [MUST] [test] Both EN and FR strings MUST exist for every user-facing error `title` and `detail` and be covered by a test; message catalogues live outside code and follow doc 22.
- **API-031** [SHOULD] [review] APIs SHOULD return structured data and let clients format dates, numbers and currency; where formatted values are returned, they MUST follow the requested locale. Generated LLM text MUST carry its language in the response metadata.
- **API-032** [MUST] [review] Locale MUST be an explicit input to any LLM-backed endpoint (not inferred silently from message text), and MUST be recorded in telemetry as a bounded attribute.

### Agent tool schemas as contracts
- **API-033** [MUST] [review] A tool exposed to an agent is an API: it MUST have a versioned input schema, output schema and error schema, validated at runtime, and subject to API-002 to API-005 and API-020 to API-023. The manifest format, lifecycle, approval and eval requirements are owned by [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md).
- **API-034** [MUST] [review] Tool errors MUST reuse the problem-details shape (API-009) so agents and logs handle failures uniformly, without leaking data into the model context.
- **API-035** [MUST] [test] LLM-facing structured output schemas MUST be pydantic models validated on every response, with a typed failure on invalid output (retry policy owned by doc 18).

## Checklist
- [ ] `openapi.yaml` updated, linted, and passing the drift and compatibility checks (API-001, API-002, API-021).
- [ ] Request and response models are pydantic v2, forbid unknown fields (API-003, API-008).
- [ ] Errors are `application/problem+json` with `type`, `title`, `status`, `trace_id`, `code` (API-009 to API-013).
- [ ] Idempotency keys on state-changing operations; pagination bounded (API-015, API-017).
- [ ] Deprecation announced with a sunset date (API-022).
- [ ] Event schemas versioned and validated; envelope fields present (API-024, API-025).
- [ ] EN and FR text for every user-facing message; `Content-Language` returned (API-028, API-030).
- [ ] Tool schemas have input, output and error schemas (API-033).

## Common AI failure modes
- Generating the OpenAPI file from code once and never reviewing it, so drift goes unnoticed.
- Returning `{"error": "something went wrong"}` or plain-text 500s instead of problem details.
- Putting exception messages, SQL or stack traces in `detail`.
- Localizing machine fields (translated enum values or error codes), breaking clients.
- Hard-coding English strings and ignoring `Accept-Language`, or switching language based on guessing from user text.
- Retrying POST handlers without idempotency keys, producing duplicate claims or letters.
- Renaming a field "for clarity" within `/v1/`.
- Unbounded list endpoints and offset pagination on large tables.
- Creating tool functions with untyped `**kwargs` and prose-only descriptions.
- Inventing header names (`X-Idempotency`, `Deprecated`) and RFC numbers without checking.

## Related docs
- [03-architecture.md](./03-architecture.md): boundaries, contract tests.
- [24-testing-standards.md](./24-testing-standards.md): contract test mechanics.
- [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md): tool manifests and schemas.
- [22-localization-and-accessibility.md](./22-localization-and-accessibility.md): EN/FR policy.
- [18-reliability-and-operations.md](./18-reliability-and-operations.md): retries, 429, dead letters.
- [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md): data in payloads and errors.
- [02-security.md](./02-security.md): authn and authz.
- [10-logging-observability.md](./10-logging-observability.md): correlation IDs.
