"""
Health check endpoint.

Used by Railway and any uptime monitoring to verify the service is running.
Returns 200 immediately — no DB check to avoid false negatives when the
database is briefly unreachable during rolling deploys.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Health check",
    include_in_schema=False,
)
async def health_check() -> JSONResponse:
    return JSONResponse(content={"status": "ok"})
