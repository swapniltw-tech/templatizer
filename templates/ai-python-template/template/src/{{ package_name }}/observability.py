"""Logging setup: structlog over stdlib logging, JSON to stdout, one init point.

Implements: OBS-001 (structlog + stdlib, JSON per line), OBS-002 (single module, called once
from the composition root), OBS-003 (trace_id/span_id on every line inside a span),
OBS-004 (foreign records share the chain), OBS-009 (redaction last before rendering).
Shape is the spike snippet in doc 10.

TODO: tracing/metrics export (OTel distro or Collector) is not set up here. The choice is an
ADR (doc 10 "Architecture options", OBS-014); until then spans come from whatever provider the
process installs and this module only correlates logs with the current span.
"""

import logging
import sys
from collections.abc import Mapping, MutableMapping, Sequence
from typing import Any, TextIO

import structlog
from opentelemetry import trace
from structlog.typing import EventDict, Processor, WrappedLogger

# ASSUMPTION: placeholder key list. Doc 10 says doc 13 owns the real list, but doc 13 has none
# (docs/FINDINGS.md F-05). Replace when the owner publishes it.
SENSITIVE_KEYS = frozenset({"password", "token", "authorization", "api_key", "secret", "email"})
_REDACTED = "[REDACTED]"
_HANDLER_NAME = "service-json"


def add_trace_context(_logger: WrappedLogger, _method: str, event_dict: EventDict) -> EventDict:
    """Add trace_id and span_id (hex, 32 and 16 chars) when a span is active (OBS-003)."""
    ctx = trace.get_current_span().get_span_context()
    if ctx.is_valid:
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict


def _scrub(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            k: _REDACTED if str(k).lower() in SENSITIVE_KEYS else _scrub(v)
            for k, v in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_scrub(v) for v in value]
    return value


def redact(_logger: WrappedLogger, _method: str, event_dict: EventDict) -> EventDict:
    """Scrub sensitive keys, including nested ones. A safety net, not a control (OBS-010)."""
    scrubbed: MutableMapping[str, Any] = {
        k: _REDACTED if k.lower() in SENSITIVE_KEYS else _scrub(v) for k, v in event_dict.items()
    }
    return dict(scrubbed)


def configure_logging(level: str = "INFO", stream: TextIO | None = None) -> None:
    """Configure structlog and the root stdlib logger. Safe to call again (replaces its handler)."""
    shared: Sequence[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        add_trace_context,
        redact,  # last before rendering (OBS-009)
    ]
    structlog.configure(
        processors=[*shared, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        # Not cached, so tests can reconfigure; the cost is negligible at this scale.
        cache_logger_on_first_use=False,
    )
    handler = logging.StreamHandler(stream if stream is not None else sys.stdout)
    handler.set_name(_HANDLER_NAME)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared,  # non-structlog records get the same chain (OBS-004)
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.JSONRenderer(),
            ],
        )
    )
    root = logging.getLogger()
    for old in [h for h in root.handlers if h.get_name() == _HANDLER_NAME]:
        root.removeHandler(old)
    root.addHandler(handler)
    root.setLevel(level)
