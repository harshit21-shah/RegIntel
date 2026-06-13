"""Log scrubbing middleware — redact secrets from log output."""

from __future__ import annotations

import logging
import re
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{10,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]+", re.I),
    re.compile(r"(password|secret|api_key)\s*[:=]\s*\S+", re.I),
)


class LogScrubFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            msg = record.msg
            for pattern in SECRET_PATTERNS:
                msg = pattern.sub("[REDACTED]", msg)
            record.msg = msg
        return True


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
