---
paths:
  - "src/**"
---

# Logging and telemetry

<!-- Implements AGT-010, AGT-011. JSON output, trace correlation and redaction are tested (OBS-003, OBS-004, OBS-009). -->

- Get loggers only with `structlog.get_logger()`; configure logging in `observability.py` alone, once, from `main.py` (OBS-002).
- Log a stable snake_case event name as the message with data in key-value fields; never interpolate values into the message (OBS-005).
- Log an exception once, at the boundary that handles it, with the traceback in a structured field; do not log and re-raise at every layer (OBS-008).
- Never pass request bodies, documents or customer identifiers into log fields; key-name redaction is only a safety net (OBS-010).
- No personal, health, financial or beneficiary data or secrets in log fields, span attributes or metric labels; use opaque IDs (OBS-011).
- Bound metric labels (enums, route templates, status classes); never label by user, policy, claim or trace ID (OBS-021).
- Levels: ERROR only for failures needing action, WARNING for degraded-but-served, INFO for business events, DEBUG off in production (OBS-007).
- Do not use operational logs as the audit trail; regulated decisions write a separate audit record (OBS-029, OBS-027).
- Tracing export is not set up yet; do not initialise an OpenTelemetry distro without the ADR (OBS-014).
