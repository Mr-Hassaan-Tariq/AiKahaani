"""
Response formatter.

All route handlers use these helpers instead of constructing response models
directly. This guarantees a consistent response shape across every endpoint.

Usage:
    from app.core.responses import responses

    @router.get("/items/{id}", response_model=ApiResponse[ItemSchema])
    async def get_item(id: int, db: AsyncSession = Depends(get_db)):
        item = await get_item_by_id(db, id)
        return responses.ok(data=ItemSchema.model_validate(item), message="Item retrieved")
"""

from typing import Any, Optional

from app.schemas.common import (
    ApiResponse,
    ErrorDetail,
    ErrorResponse,
    PaginatedResponse,
    PaginationMeta,
)


class ResponseFormatter:
    """
    Builds standardised response models.

    Methods mirror HTTP semantics:
        ok()        → 200 success with data
        created()   → 201 resource created
        deleted()   → 200 deletion acknowledged
        paginated() → 200 list with pagination meta
        no_data()   → 200/204 with no payload (e.g. mark-as-read)
        error()     → used by exception handlers, not route handlers directly
    """

    def ok(self, data: Any = None, message: str = "Success") -> ApiResponse:
        """200 — request succeeded, single object or None returned."""
        return ApiResponse(success=True, message=message, data=data)

    def created(self, data: Any = None, message: str = "Created successfully") -> ApiResponse:
        """201 — resource created."""
        return ApiResponse(success=True, message=message, data=data)

    def deleted(self, message: str = "Deleted successfully") -> ApiResponse:
        """200 — resource deleted, no data to return."""
        return ApiResponse(success=True, message=message, data=None)

    def no_data(self, message: str = "Done") -> ApiResponse:
        """200 — action performed, no meaningful data to return."""
        return ApiResponse(success=True, message=message, data=None)

    def paginated(
        self,
        data: list,
        total: int,
        limit: int,
        offset: int,
        message: str = "Retrieved successfully",
    ) -> PaginatedResponse:
        """200 — paginated list of resources."""
        return PaginatedResponse(
            success=True,
            message=message,
            data=data,
            meta=PaginationMeta(
                total=total,
                limit=limit,
                offset=offset,
                has_next=(offset + limit) < total,
                has_prev=offset > 0,
            ),
        )

    def error(
        self,
        message: str,
        errors: Optional[list[ErrorDetail]] = None,
    ) -> ErrorResponse:
        """Build an error response (used by exception handlers)."""
        return ErrorResponse(success=False, message=message, errors=errors)


# Module-level singleton — import this everywhere
responses = ResponseFormatter()
