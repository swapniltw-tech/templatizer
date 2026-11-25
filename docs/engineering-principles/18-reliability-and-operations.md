# Reliability and Operations

> **Owner:** Platform Engineering lead (SRE) · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** none (internal standard) for policy. Vendor behaviours (HTTP 429, `Retry-After`, Foundry quota semantics, Azure health probes) are `VERIFY:` against learn.microsoft.com. RFC 9110 for `Retry-After` semantics `VERIFY:`. Telemetry mechanics are owned by [10-logging-observability.md](./10-logging-observability.md).

## Purpose
Define how services and agents stay available, fail safely and are operated in a regulated insurer. Every external call can be slow, wrong or down, and every LLM call is also non-deterministic and rate limited. This doc owns timeouts, retries, circuit breaking, degradation, SLOs, health checks, incident response, runbooks, postmortems, agent kill switches and cost anomaly alerts. Telemetry setup is in doc 10. Idempotency key mechanics for HTTP are in [17-api-and-contracts.md](./17-api-and-contracts.md).

## Defaults at a glance
All numbers are starting points. `ASSUMPTION:` tune per service tier and record the values in the service README.

| Control | Default | Notes |
|---|---|---|
| Connect timeout | 2 s | Internal HTTP and DB |
| Read timeout | 10 s | Per-call, not per-request |
| LLM call timeout | set per use case, never unlimited | Streaming still needs an overall deadline |
| Retries | 3 attempts total, exponential backoff, full jitter, cap 30 s | Only idempotent or keyed operations |
| Circuit breaker | open after 5 consecutive failures or 50% failures over 20 calls; half-open probe after 30 s | Per dependency |
| Bulkhead | bounded concurrency per dependency | Prevents one slow provider exhausting workers |
| Request deadline | one propagated deadline per inbound request | Child calls get the remaining budget |

## Rules

### Timeouts, retries and breakers
- **REL-001** [MUST] [lint: ruff] Every outbound network call (HTTP, DB, queue, LLM) MUST set an explicit timeout. Library defaults MUST NOT be relied on. A custom lint or a wrapper client enforces this.
- **REL-002** [MUST] [review] Inbound requests MUST have a total deadline; downstream calls MUST use the remaining budget, never a fresh full timeout.
- **REL-003** [MUST] [test] Retries MUST use exponential backoff with jitter, a bounded attempt count and a maximum delay.
- **REL-004** [MUST] [review] Only idempotent operations, or operations carrying an idempotency key, MAY be retried. Non-idempotent writes MUST NOT be retried blindly.
- **REL-005** [MUST] [review] Retry only transient errors (timeouts, connection resets, 429, 502, 503, 504). Never retry 400, 401, 403, 404, 409 or schema validation failures.
- **REL-006** [MUST] [review] Retries MUST NOT be layered: exactly one layer (the client wrapper) retries. Retry budgets MUST be bounded so retries cannot exceed a small fraction (`ASSUMPTION:` 10%) of base traffic.
- **REL-007** [SHOULD] [review] Each remote dependency SHOULD sit behind a circuit breaker and a concurrency limit (bulkhead). Breaker state changes MUST emit a metric and a log event.
- **REL-008** [MUST] [review] Where the server sends `Retry-After` on 429 or 503, the client MUST honour it (capped by the request deadline). `VERIFY:` that the chosen provider SDK does not already retry, to avoid double retry.

### LLM provider limits and degradation
- **REL-009** [MUST] [review] LLM calls MUST go through the single wrapper client in `adapters/llm/`; the wrapper owns timeout, retry, 429 handling, breaker and telemetry.
- **REL-010** [MUST] [test] On 429 or quota errors the wrapper MUST back off, then fail fast with a typed error; it MUST NOT spin retries or silently switch to an unapproved model or provider.
- **REL-011** [MUST] [review] Each LLM-dependent feature MUST define a degradation mode in its design: (a) deterministic fallback, (b) queue for later, (c) human handoff, or (d) clear unavailable message in EN and FR. The choice is recorded in the service README.
- **REL-012** [MUST] [review] A fallback model MUST be a pre-approved deployment (placeholder `<fallback-deployment>`) per [15-llm-and-model-governance.md](./15-llm-and-model-governance.md) with evals passed; fallbacks MUST NOT be improvised at runtime.
- **REL-013** [SHOULD] [review] Prefer deterministic code paths for anything that must keep working when the LLM is down (see [04-engineering-principles.md](./04-engineering-principles.md)).
- **REL-014** [MUST] [runtime] Token and request quotas MUST be monitored; an alert MUST fire before saturation, not after the first 429.

### Durable and idempotent work
- **REL-015** [MUST] [test] Message and job handlers MUST be idempotent: processing the same message twice yields the same final state. A test MUST deliver each handler's message twice.
- **REL-016** [MUST] [review] Multi-step or long-running workflows MUST persist step state (queue, durable workflow engine or database) so a crash resumes rather than restarts. `ASSUMPTION:` engine choice is an ADR (see [05-decision-playbook.md](./05-decision-playbook.md)).
- **REL-017** [MUST] [review] Queues MUST have a dead-letter path, a maximum delivery count and an alert on dead-letter depth. Poison messages MUST NOT block the queue.
- **REL-018** [SHOULD] [review] Side effects with external parties (emails, payments, case updates) SHOULD use an outbox or an idempotency key so retries never duplicate them.

### Health, SLIs and SLOs
- **REL-019** [MUST] [test] Services MUST expose separate liveness and readiness endpoints. Liveness MUST NOT check dependencies; readiness MUST reflect ability to serve. `VERIFY:` probe settings for the chosen Azure host.
- **REL-020** [MUST] [review] Every user-facing or agent-facing service MUST define SLIs (availability, latency percentile, and for AI features, task success rate from evals) and a numeric SLO with an owner.
- **REL-021** [SHOULD] [review] Alert on SLO burn rate (multi-window) rather than raw thresholds; every alert MUST link to a runbook.
- **REL-022** [SHOULD] [review] Tier services (`ASSUMPTION:` tier 1 customer-impacting/regulated decision, tier 2 internal, tier 3 batch) and set SLO, on-call and recovery objectives by tier.
- **REL-023** [MUST] [review] Rate limiting MUST protect every public and internal API (per client identity); limit responses MUST use 429 with a problem body per [17-api-and-contracts.md](./17-api-and-contracts.md).

### Kill switch and cost control
- **REL-024** [MUST] [runtime] Every agent and every LLM-backed feature MUST have a kill switch (feature flag or config) that disables it without a deploy, is tested, and degrades per REL-011. The switch's location and owner are recorded in the agent manifest ([25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md)).
- **REL-025** [MUST] [review] The kill switch MUST be operable by on-call without code changes and MUST be exercised at least once per quarter (`ASSUMPTION:` cadence).
- **REL-026** [MUST] [runtime] Cost anomaly alerts MUST exist per LLM-using service (spend per day and tokens per request against a baseline) with a named responder; budgets are owned by doc 15.
- **REL-027** [SHOULD] [runtime] Agents SHOULD have hard per-run limits (steps, tool calls, tokens, wall clock) enforced in code, so a loop cannot run away.

### Incidents, runbooks and postmortems
- **REL-028** [MUST] [manual] Each service MUST have a runbook in `docs/runbooks/` using the template below, reviewed at least every 6 months (`ASSUMPTION:`) and after each incident.
- **REL-029** [MUST] [manual] Incidents MUST be classified by severity; AI-specific incidents (harmful output, data exposure through a model, runaway agent) MUST be escalated to the AI governance team and security per the incident process in [12-governance-and-compliance.md](./12-governance-and-compliance.md). `ASSUMPTION:` F1 policy names pending.
- **REL-030** [MUST] [manual] Sev 1 and Sev 2 incidents MUST have a blameless postmortem within 5 business days (`ASSUMPTION:`) with owned, dated actions tracked to closure.
- **REL-031** [MUST] [manual] Regulatory incident reporting obligations (for example technology or cyber incident reporting to OSFI) MUST be confirmed with Compliance and encoded in the runbook. `VERIFY:` timelines against primary OSFI text; none are asserted here.
- **REL-032** [SHOULD] [review] Run a game day or failure-injection test (provider 429s, provider down, dependency slow) for each tier 1 AI service before go-live and yearly.

## Runbook template
```
# Runbook: <service>
Owner / on-call rota:
Dependencies (and degrade mode per dependency):
SLOs and dashboards:
Alerts -> first action table:
Kill switch: location, how to flip, who may, how to verify
Common failures: symptom, cause, fix, escalation
LLM provider issues: 429/quota, deployment retired, content filter spikes
Data exposure steps: stop, preserve evidence, notify (link to incident process)
Rollback: see CI/CD standard
Last reviewed:
```

## Checklist
- [ ] All outbound calls have explicit timeouts and deadline propagation (REL-001, REL-002).
- [ ] One retry layer, backoff and jitter, idempotent only (REL-003 to REL-006).
- [ ] LLM wrapper handles 429 and quota; degradation mode documented for EN and FR (REL-009 to REL-011).
- [ ] Handlers tested for duplicate delivery; dead-letter queue and alert exist (REL-015, REL-017).
- [ ] Liveness and readiness endpoints; SLIs and SLO defined (REL-019, REL-020).
- [ ] Kill switch exists, tested, listed in the manifest (REL-024, REL-025).
- [ ] Cost anomaly alert and per-run agent limits (REL-026, REL-027).
- [ ] Runbook exists from the template (REL-028).

## Common AI failure modes
- Omitting timeouts, because the library default "works".
- Wrapping a retry decorator around code that already retries, multiplying attempts.
- Retrying non-idempotent POSTs or retrying on 400/401.
- Retrying 429 in a tight loop, or silently falling back to a different model or provider.
- Liveness probes that call the database or the LLM, causing restart storms during an outage.
- Swallowing exceptions and returning an empty "success" when the LLM fails.
- Agent loops with no step or token limit.
- Kill switches that exist in code but cannot be flipped without a deploy.
- Inventing Azure probe or quota settings instead of marking `VERIFY:`.
- Postmortems that blame an individual, or runbooks with no first action.

## Related docs
- [10-logging-observability.md](./10-logging-observability.md): telemetry, alert basics.
- [17-api-and-contracts.md](./17-api-and-contracts.md): idempotency, 429 problem body.
- [15-llm-and-model-governance.md](./15-llm-and-model-governance.md): fallback models, cost budgets.
- [16-cicd-and-deployment.md](./16-cicd-and-deployment.md): rollout and rollback.
- [25-ai-tool-and-agent-registry.md](./25-ai-tool-and-agent-registry.md): kill switch in manifest.
- [12-governance-and-compliance.md](./12-governance-and-compliance.md): incident escalation.
- [04-engineering-principles.md](./04-engineering-principles.md): deterministic-first.
- [05-decision-playbook.md](./05-decision-playbook.md): sync vs async, durable workflows.
- [22-localization-and-accessibility.md](./22-localization-and-accessibility.md): EN/FR error messages.
