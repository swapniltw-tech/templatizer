# Logging and Observability

> **Owner:** Platform Engineering lead (observability) · **Last verified:** 2026-11-25 · **Status:** Draft
> **Sources:** opentelemetry.io Python status page; opentelemetry-python-contrib logging instrumentation docs; learn.microsoft.com "Enable OpenTelemetry in Application Insights" (updated 2026-10); structlog standard-library docs; OpenTelemetry GenAI semantic-conventions repository (moved out of the main semconv repo; not re-read in full, so all `gen_ai.*` names are `VERIFY:`); in-repo spike (below).

## Purpose
Every service and agent MUST emit structured logs, traces and metrics that let an on-call engineer, an auditor and an AI agent reconstruct what happened, without leaking personal or secret data. This doc owns the logging and telemetry setup. It does **not** own redaction policy (see [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md)), SLOs and alerting thresholds ([18-reliability-and-operations.md](./18-reliability-and-operations.md)), or Foundry-side tracing configuration ([23-azure-foundry-standards.md](./23-azure-foundry-standards.md)).

## Signal maturity and package choices
| Item | Status (as read 2026-11-25) | Consequence |
|---|---|---|
| OTel Python traces | Stable (opentelemetry.io) | Safe to build on |
| OTel Python metrics | Stable (opentelemetry.io) | Safe to build on |
| OTel Python logs | **Development** (opentelemetry.io) | Keep the log pipeline swappable; stdout JSON is the fallback that must always work |
| SDK `LoggingHandler` | Contrib docs say the package `opentelemetry-instrumentation-logging` provides a handler that replaces the deprecated one in `opentelemetry-sdk` | `VERIFY:` the handler import path in the pinned release before use |
| `gen_ai.*` semantic conventions | Moved to a separate GenAI semconv repository; Development per secondary sources | `VERIFY:` against that repository; wrap names in one module |
| Microsoft distro for Python | `microsoft-opentelemetry` with `use_microsoft_opentelemetry(...)` is what Learn now recommends for **new** apps; `azure-monitor-opentelemetry` with `configure_azure_monitor(...)` remains supported ("no action needed" for existing users) | Choose **one**; Learn says do not initialize both |

Relationship of the two Azure entry points (from Learn): the Microsoft OpenTelemetry Distro is the newer, multi-destination package (Azure Monitor, any OTLP endpoint, Microsoft Agent 365). The Azure Monitor distro is the older Azure-only one. Standalone exporter packages keep their names. `ASSUMPTION:` new services adopt `microsoft-opentelemetry` only if the platform team confirms its release status is acceptable; otherwise they use `azure-monitor-opentelemetry`. `VERIFY:` the exact parameter names beyond `enable_azure_monitor` and `logger_name`, which Learn shows; earlier notes about `enable_trace_based_sampling_for_logs`, `log_record_processors` and `metric_readers` came from the Azure Monitor distro docs and are not re-confirmed here.

## Architecture options (record in an ADR)
| Option | Shape | Use when |
|---|---|---|
| A. In-process distro | App -> distro -> Application Insights | Low-risk services; simplest |
| B. Collector | App -> OTLP -> OpenTelemetry Collector -> Application Insights / other | Default for production: central redaction, sampling and routing before data leaves the network |

## Rules

### Structured logging
- **OBS-001** [MUST] [lint: ruff] Services MUST log through `structlog` layered on stdlib `logging`, rendering one JSON object per line to stdout. `print()` and ad hoc `logging.basicConfig` MUST NOT appear in `src/`.
- **OBS-002** [MUST] [review] Logging and telemetry MUST be configured in exactly one module (`observability.py`), called once from the composition root. Other modules obtain loggers only via `structlog.get_logger()`.
- **OBS-003** [MUST] [test] Every log line emitted inside an active span MUST carry `trace_id` and `span_id` (hex, 32 and 16 chars). A test MUST assert this (see the proven snippet below).
- **OBS-004** [MUST] [test] Third-party stdlib log records (for example from HTTP clients) MUST pass through the same processor chain via `foreign_pre_chain`, so they are JSON and correlated too.
- **OBS-005** [MUST] [review] Log events MUST use a stable snake_case event name as the message (`policy_lookup_failed`) with data in key-value fields, never interpolated into the string.
- **OBS-006** [MUST] [review] Every request MUST carry a correlation ID (inbound `X-Request-ID` honoured if well-formed, else generated), bound with `structlog.contextvars` and returned in the response.
- **OBS-007** [SHOULD] [review] Log levels: ERROR only for failures needing action, WARNING for degraded-but-served, INFO for business events, DEBUG off in production by default.
- **OBS-008** [MUST] [review] Exceptions MUST be logged once, at the boundary that handles them, with the traceback in a structured field (`exc_info`). Do not log and re-raise at every layer.

### Redaction and sensitive data
- **OBS-009** [MUST] [ci: unit test] A redaction processor MUST be the last processor before rendering, and a test MUST prove it scrubs the keys listed by the data-classification standard. Redaction policy, key lists and what counts as personal data are owned by [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md).
- **OBS-010** [MUST] [review] Key-name redaction is a safety net, not a control: code MUST NOT pass request bodies, prompts, documents or customer identifiers into log fields in the first place.
- **OBS-011** [MUST] [review] Span attributes, metric labels and log fields MUST NOT contain personal, health, financial or beneficiary data or secrets. Use opaque internal IDs.
- **OBS-012** [SHOULD] [runtime: collector] Production telemetry SHOULD pass through a Collector with an attribute-scrubbing processor as a second redaction layer (option B). `VERIFY:` the processor names in the pinned Collector distribution.

### OpenTelemetry setup
- **OBS-013** [MUST] [ci: lockfile check] All `opentelemetry-*` packages (api, sdk, semantic-conventions, exporters, instrumentations) MUST be pinned together to a mutually compatible set in the lockfile and upgraded in one MR after reading release notes.
- **OBS-014** [MUST] [review] Exactly one distro or manual SDK initialisation MUST exist per process. Do not call both `configure_azure_monitor` and `use_microsoft_opentelemetry`.
- **OBS-015** [MUST] [review] The Application Insights connection string MUST come from the `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable (injected per [06-secrets-and-env.md](./06-secrets-and-env.md)), not from code, outside local development.
- **OBS-016** [MUST] [review] When using an Azure distro, set `logger_name` to the application logger namespace so the SDK's own logs are not exported.
- **OBS-017** [MUST] [review] Each service MUST set `service.name` and the Azure cloud role name; services sharing an Application Insights resource are otherwise indistinguishable on the Application Map.
- **OBS-018** [SHOULD] [review] Auto-instrument HTTP server and client, database and queue libraries; add manual spans for LLM calls, tool calls, retrieval and agent steps.
- **OBS-019** [SHOULD] [review] Log export to the backend SHOULD be treated as Development-status: keep stdout JSON enabled alongside any OTel log exporter, and re-run the correlation test on every OTel upgrade.
- **OBS-020** [SHOULD] [runtime: collector] Sampling SHOULD always keep error and slow traces; use tail sampling in the Collector or `VERIFY:` the equivalent distro option. Record the sampling rate in the ADR.
- **OBS-021** [MUST] [review] Metric label sets MUST be bounded (enumerations, route templates, status classes). Never label by user, policy, claim, prompt or trace ID.

### LLM and agent telemetry
- **OBS-022** [MUST] [runtime] Capture of prompt and response content on spans or logs MUST be OFF by default in every environment except local development with synthetic data. Enabling it requires a waiver per [21-exceptions-and-waivers.md](./21-exceptions-and-waivers.md), redaction per doc 13, and treatment of the data as restricted.
- **OBS-023** [MUST] [review] LLM spans MUST record model deployment name (placeholder in docs: `<chat-deployment>`), token counts, latency, finish reason and error type; cost MUST be derived as a metric from tokens, not logged per prompt.
- **OBS-024** [MUST] [review] All `gen_ai.*` attribute names MUST be defined in one internal module (`observability/genai_attrs.py`) so upstream renames are a one-file change. `VERIFY:` names (for example `gen_ai.system` has reportedly become `gen_ai.provider.name`) against the GenAI semconv repository.
- **OBS-025** [MUST] [review] A request MUST produce one trace as the source of truth. If Foundry tracing ([23-azure-foundry-standards.md](./23-azure-foundry-standards.md)) is also enabled, agree which side creates the LLM span and suppress the duplicate.
- **OBS-026** [SHOULD] [review] Emit eval scores and guardrail outcomes as metrics so [14-evals-and-testing-ai.md](./14-evals-and-testing-ai.md) online monitoring has a data source.

### Audit trail
- **OBS-027** [MUST] [review] Regulated decisions MUST write an audit record separate from application logs, containing who or what acted, which model and prompt version, inputs by reference (not content), outcome, timestamp and correlation ID.
- **OBS-028** [MUST] [runtime] Audit records MUST go to append-only storage with retention set by [12-governance-and-compliance.md](./12-governance-and-compliance.md). `ASSUMPTION:` the specific store (for example immutable blob storage with a time-based retention policy) is chosen in an ADR.
- **OBS-029** [MUST] [review] Operational logs MUST NOT be used as the audit trail; they may be sampled, rotated or dropped.

### Alerting basics
- **OBS-030** [SHOULD] [review] Every service SHOULD define alerts on error rate, latency and saturation, each linked to a runbook; SLO-based alerting is owned by [18-reliability-and-operations.md](./18-reliability-and-operations.md).

## Proven snippet: structlog, stdlib logging and OpenTelemetry correlation
Spike result: **works**. Run in a fresh venv with `python -I`, in-memory span exporter, no network.

Versions used: Python 3.15.2, `structlog` 26.1.0, `opentelemetry-api` 1.45.2, `opentelemetry-sdk` 1.45.2, `opentelemetry-semantic-conventions` 0.66b2 (latest releases at spike time, unpinned; pin your own set per OBS-013).

Verified by assertion: a structlog event inside a span carries the span's `trace_id`/`span_id`; a plain stdlib `logging` record emitted in the same span is JSON-rendered and correlated; a line outside any span has no IDs; sensitive keys are scrubbed, including nested dict keys.

```python
import logging
import structlog
from opentelemetry import trace

SENSITIVE_KEYS = {"password", "token", "authorization", "api_key", "secret", "email"}  # real list: owned by doc 13


def add_trace_context(logger, method, event_dict):
    ctx = trace.get_current_span().get_span_context()
    if ctx.is_valid:
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict


def redact(logger, method, event_dict):
    def scrub(value):
        if isinstance(value, dict):
            return {k: "[REDACTED]" if k.lower() in SENSITIVE_KEYS else scrub(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [scrub(v) for v in value]
        return value

    return scrub(event_dict)


shared = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt="iso", utc=True),
    add_trace_context,
    redact,  # last before rendering (OBS-009)
]
structlog.configure(
    processors=shared + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
handler = logging.StreamHandler()  # stdout in production
handler.setFormatter(
    structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared,  # applies to non-structlog records (OBS-004)
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
    )
)
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)
```

Test pattern (OBS-003): create a `TracerProvider` with `SimpleSpanProcessor(InMemorySpanExporter())`, where `InMemorySpanExporter` is imported from `opentelemetry.sdk.trace.export.in_memory_span_exporter` in 1.45.2 (it is not exported from `opentelemetry.sdk.trace.export`). Log inside `tracer.start_as_current_span(...)`, capture the handler's stream, parse the JSON, and compare `trace_id`/`span_id` with the finished span's context.

Limits of the spike (do not over-read it):
- It proves correlation by our own processor reading the current span. It did **not** test the OTel logging handler, OTLP export, the Azure distros, or async/threaded context propagation beyond a single thread.
- The redaction processor is key-name based. It does not scrub secrets embedded in free-text messages or values; that is why OBS-010 exists.
- `opentelemetry-instrumentation-logging` offers its own injection (`otelTraceID`, `otelSpanID` record attributes, `set_logging_format`, `OTEL_PYTHON_LOG_CORRELATION`). Our processor does not depend on it; do not enable both formats. `VERIFY:` behaviour when both are active.

## Checklist
- [ ] `observability.py` is the only place logging and OTel are configured (OBS-002).
- [ ] Correlation test and redaction test exist and pass (OBS-003, OBS-009).
- [ ] `opentelemetry-*` packages pinned as one set (OBS-013).
- [ ] One distro only; connection string from environment (OBS-014, OBS-015).
- [ ] Prompt and response capture is off (OBS-022).
- [ ] `gen_ai.*` names live in one module (OBS-024).
- [ ] Audit records are separate from logs (OBS-027, OBS-029).
- [ ] Metric labels are bounded; no personal data in attributes (OBS-011, OBS-021).
- [ ] ADR records Collector vs in-process choice and sampling.

## Common AI failure modes
- Using `print()` or `logging.basicConfig` in new modules, or configuring logging in several files.
- Logging the full prompt, response, request body or an exception message containing customer data "for debugging".
- Interpolating values into the log message (`f"failed for {policy_id}"`) instead of fields.
- Importing `InMemorySpanExporter` from the wrong module, or inventing `configure_azure_monitor` keyword arguments.
- Initialising both Azure distros, or initialising the SDK in every module.
- Floating `opentelemetry-*` versions so api, sdk and instrumentation drift apart.
- Putting user IDs, policy numbers or prompts into metric labels (cardinality explosion and data leak).
- Treating application logs as the audit trail.
- Hard-coding `gen_ai.*` attribute strings across the codebase.
- Enabling content capture to make traces "more useful".

## Related docs
- [13-data-classification-and-privacy.md](./13-data-classification-and-privacy.md): redaction policy and sensitive-key list.
- [18-reliability-and-operations.md](./18-reliability-and-operations.md): SLOs, alerts, incident response.
- [23-azure-foundry-standards.md](./23-azure-foundry-standards.md): Foundry tracing.
- [15-llm-and-model-governance.md](./15-llm-and-model-governance.md): model pinning and cost budgets.
- [12-governance-and-compliance.md](./12-governance-and-compliance.md): audit retention.
- [06-secrets-and-env.md](./06-secrets-and-env.md): connection strings.
- [00-tech-stack.md](./00-tech-stack.md): library choices and versions.
- [24-testing-standards.md](./24-testing-standards.md): test layout.
