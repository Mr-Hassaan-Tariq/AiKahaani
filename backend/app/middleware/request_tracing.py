"""
Request tracing middleware.

Attaches a unique request_id to every inbound request, extracts the user_id
from the JWT (if present), injects both into contextvars so loggers pick them
up automatically, and appends X-Request-ID to the response header.
"""

import json
import logging
import time
import uuid
from typing import Optional

from fastapi import Request, Response
from jose import jwt
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response as StarletteResponse

from app.config import settings
from app.middleware.logging_context import clear_request_context, set_request_context

logger = logging.getLogger(__name__)

# Paths that generate too much noise and don't need per-request logging
_EXCLUDED_PREFIXES = ("/health", "/api/docs", "/api/openapi.json", "/static", "/media")

# Request body fields that must never appear in logs
_SENSITIVE_FIELDS = frozenset({
    "password", "token", "secret", "api_key",
    "access_token", "refresh_token", "hashed_password",
})


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """
    Starlette/FastAPI middleware that:
      1. Generates a UUID request_id for every request
      2. Extracts user_id from Bearer JWT without fully verifying it
         (verification happens in get_current_user; here we just want the claim for logging)
      3. Sets both into contextvars for loggers
      4. Logs request start and end with method, path, status, and duration
      5. Appends X-Request-ID header to the response
      6. Clears context after response is sent
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> StarletteResponse:
        # Skip noisy infrastructure paths
        if any(request.url.path.startswith(p) for p in _EXCLUDED_PREFIXES):
            return await call_next(request)

        request_id = str(uuid.uuid4())
        user_id = self._extract_user_id(request)
        set_request_context(request_id=request_id, user_id=user_id)

        start = time.perf_counter()
        self._log_start(request)

        try:
            response: Response = await call_next(request)
            duration = time.perf_counter() - start
            # Log end BEFORE clearing context so request_id/user_id appear in the log
            self._log_end(request, response.status_code, duration)
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as exc:
            duration = time.perf_counter() - start
            logger.error(
                f"Request failed: {request.method} {request.url.path} ({duration:.3f}s)",
                exc_info=True,
                extra={"exception_type": type(exc).__name__},
            )
            raise
        finally:
            # Always clear context, even if an exception was raised
            clear_request_context()

    # ── Private helpers ───────────────────────────────────────────────────────

    def _extract_user_id(self, request: Request) -> Optional[int]:
        """
        Decode the JWT from Authorization header without full verification.
        We only want the user_id claim for log context — auth is done later
        inside get_current_user().
        """
        try:
            auth = request.headers.get("authorization", "")
            if not auth.startswith("Bearer "):
                return None
            token = auth.split(" ", 1)[1]
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.jwt_algorithm],
            )
            return payload.get("sub") or payload.get("user_id")
        except Exception:
            return None

    def _log_start(self, request: Request) -> None:
        logger.info(
            f"→ {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params) or None,
                "ip": self._client_ip(request),
            },
        )

    def _log_end(self, request: Request, status_code: int, duration: float) -> None:
        level = logging.WARNING if status_code >= 500 else logging.INFO
        logger.log(
            level,
            f"← {request.method} {request.url.path} {status_code} ({duration:.3f}s)",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": round(duration * 1000, 2),
            },
        )

    @staticmethod
    def _client_ip(request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else ""
