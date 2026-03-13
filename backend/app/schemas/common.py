"""
Standardised API response schemas.

Every endpoint in this application returns one of three shapes:

    ApiResponse[T]          — single-object success response
    PaginatedResponse[T]    — list success response with pagination metadata
    ErrorResponse           — any error (validation, auth, not-found, server)

The response formatter in app/core/responses.py builds these models.
Route handlers never construct raw dicts — they always go through responses.py.
"""

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


# ── Pagination ────────────────────────────────────────────────────────────────

class PaginationMeta(BaseModel):
    total: int = Field(..., description="Total number of matching records")
    limit: int = Field(..., description="Page size requested")
    offset: int = Field(..., description="Number of records skipped")
    has_next: bool = Field(..., description="True if more records exist after this page")
    has_prev: bool = Field(..., description="True if records exist before this page")


# ── Success responses ─────────────────────────────────────────────────────────

class ApiResponse(BaseModel, Generic[DataT]):
    """Standard single-object response wrapper."""
    success: bool = True
    message: str
    data: Optional[DataT] = None


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Paginated list response wrapper."""
    success: bool = True
    message: str
    data: list[DataT]
    meta: PaginationMeta


# ── Error responses ───────────────────────────────────────────────────────────

class ErrorDetail(BaseModel):
    """Individual field-level error detail."""
    field: Optional[str] = Field(None, description="Dot-path to the invalid field, if applicable")
    message: str = Field(..., description="Human-readable error message")


class ErrorResponse(BaseModel):
    """Standard error response wrapper — used for all 4xx and 5xx responses."""
    success: bool = False
    message: str
    errors: Optional[list[ErrorDetail]] = Field(
        None,
        description="Field-level validation errors, present on 422 responses",
    )
