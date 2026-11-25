"""Log correlation and redaction (OBS-003, OBS-004, OBS-009; pattern from doc 10)."""

import io
import json
import logging

import structlog
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from reference_service.observability import configure_logging


def _lines(stream: io.StringIO) -> list[dict[str, object]]:
    return [json.loads(line) for line in stream.getvalue().splitlines()]


def test_log_lines_inside_a_span_carry_trace_and_span_ids() -> None:
    stream = io.StringIO()
    configure_logging("INFO", stream)
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("test")

    with tracer.start_as_current_span("work"):
        structlog.get_logger().info("inside_span")
        logging.getLogger("third.party").warning("foreign_record")  # OBS-004
    structlog.get_logger().info("outside_span")

    ctx = exporter.get_finished_spans()[0].context
    assert ctx is not None
    inside, foreign, outside = _lines(stream)
    for line in (inside, foreign):
        assert line["trace_id"] == format(ctx.trace_id, "032x")
        assert line["span_id"] == format(ctx.span_id, "016x")
    assert "trace_id" not in outside
    assert inside["event"] == "inside_span"


def test_sensitive_keys_are_scrubbed_including_nested() -> None:
    stream = io.StringIO()
    configure_logging("INFO", stream)

    structlog.get_logger().info(
        "login",
        password="not-a-real-password",
        ctx={"token": "x", "ok": 1, "items": [{"email": "e"}]},
    )

    (line,) = _lines(stream)
    assert line["password"] == "[REDACTED]"
    assert line["ctx"] == {"token": "[REDACTED]", "ok": 1, "items": [{"email": "[REDACTED]"}]}


def test_configure_logging_twice_does_not_duplicate_lines() -> None:
    stream = io.StringIO()
    configure_logging("INFO", stream)
    configure_logging("INFO", stream)
    structlog.get_logger().info("once")
    assert len(_lines(stream)) == 1
