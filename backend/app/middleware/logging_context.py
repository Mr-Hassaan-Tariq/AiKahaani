"""
Context variables for request tracing.

Stores request_id and user_id in Python contextvars so they are automatically
available to every logger call within the same request, without passing them
explicitly through the call stack.

These are set by RequestTracingMiddleware at the start of each request and
cleared when the request completes.
"""

from contextvars import ContextVar
from typing import Optional

context_request_id: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
context_user_id: ContextVar[Optional[int]] = ContextVar("user_id", default=None)


def set_request_context(
    request_id: Optional[str] = None,
    user_id: Optional[int] = None,
) -> None:
    """Set request-scoped context variables."""
    if request_id is not None:
        context_request_id.set(request_id)
    if user_id is not None:
        context_user_id.set(user_id)


def get_request_context() -> dict:
    """Return current request context as a plain dict."""
    return {
        "request_id": context_request_id.get(),
        "user_id": context_user_id.get(),
    }


def clear_request_context() -> None:
    """Reset context variables to their defaults after each request."""
    context_request_id.set(None)
    context_user_id.set(None)
