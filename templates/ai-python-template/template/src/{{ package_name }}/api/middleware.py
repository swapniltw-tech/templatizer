"""Request-ID middleware (OBS-006): honour a well-formed X-Request-ID, else generate one.

The ID is bound with structlog.contextvars for every log line of the request and returned in
the response header. Pure ASGI (not BaseHTTPMiddleware) so contextvars propagate reliably.
"""

import re
import uuid

import structlog
from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUEST_ID_HEADER = "X-Request-ID"
_WELL_FORMED = re.compile(r"^[A-Za-z0-9._-]{8,64}$")


def get_request_id(scope: Scope) -> str:
    """Return the request ID stored on the scope (set by RequestIdMiddleware)."""
    return str(scope.get("request_id", ""))


class RequestIdMiddleware:
    """Bind a correlation ID per HTTP request and echo it in the response."""

    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return
        inbound = Headers(scope=scope).get(REQUEST_ID_HEADER, "")
        request_id = inbound if _WELL_FORMED.match(inbound) else uuid.uuid4().hex
        scope["request_id"] = request_id
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        async def send_with_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message)[REQUEST_ID_HEADER] = request_id
            await send(message)

        try:
            await self._app(scope, receive, send_with_id)
        finally:
            structlog.contextvars.clear_contextvars()
