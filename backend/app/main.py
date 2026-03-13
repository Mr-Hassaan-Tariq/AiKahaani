"""
FastAPI application factory.

This module creates the app, registers middleware, mounts all routers,
and installs exception handlers that ensure every error response — regardless
of where it originates — uses the standard ErrorResponse shape.
"""

import logging
import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.auth.router import auth_router
from app.api.health import router as health_router
from app.api.v1.router import v1_router
from app.config import settings
from app.core.logging import configure_logging
from app.core.rate_limit import limiter
from app.middleware.request_tracing import RequestTracingMiddleware
from app.schemas.common import ErrorDetail, ErrorResponse

logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Runs startup logic before yield and shutdown logic after.
    """
    configure_logging(debug=settings.debug)
    logger.info(
        f"Video Scripts API starting — environment={settings.environment} "
        f"debug={settings.debug}"
    )
    yield
    logger.info("Video Scripts API shutting down")


# ── App factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title="Video Scripts API",
        description="YouTube script generation platform API",
        version="2.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
        # Disable FastAPI's default 422 response in favour of our custom handler
        responses={
            422: {"model": ErrorResponse, "description": "Validation Error"},
            500: {"model": ErrorResponse, "description": "Internal Server Error"},
        },
    )

    _register_middleware(app)
    _register_routers(app)
    _register_exception_handlers(app)

    return app


def _register_middleware(app: FastAPI) -> None:
    # Order matters — middleware executes top-to-bottom on the way IN,
    # bottom-to-top on the way OUT.

    # CORSMiddleware must be registered before everything else so that
    # OPTIONS pre-flight requests get CORS headers even when they
    # never reach our middleware.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins if not settings.debug else ["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "accept",
            "accept-encoding",
            "authorization",
            "content-type",
            "dnt",
            "origin",
            "user-agent",
            "x-requested-with",
            "x-request-id",
        ],
        expose_headers=["X-Request-ID"],
    )

    # SlowAPI middleware checks rate limits on every request.
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    # RequestTracingMiddleware runs after CORS/rate-limit so request_id / user_id
    # are available to all subsequent handlers.
    app.add_middleware(RequestTracingMiddleware)


def _register_routers(app: FastAPI) -> None:
    app.include_router(health_router)
    app.include_router(auth_router, prefix="/api/auth")
    app.include_router(v1_router, prefix="/api/v1")


def _register_exception_handlers(app: FastAPI) -> None:
    """
    Global exception handlers that normalise every error into ErrorResponse.

    Handlers are listed from most-specific to least-specific. FastAPI calls
    the most specific matching handler.
    """

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(
        request: Request, exc: RateLimitExceeded
    ) -> JSONResponse:
        """Return 429 with our standard ErrorResponse envelope."""
        retry_after = str(getattr(exc, "retry_after", 60))
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=ErrorResponse(
                message="Rate limit exceeded. Please slow down and try again."
            ).model_dump(),
            headers={"Retry-After": retry_after},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
        Convert Pydantic / FastAPI validation errors into structured ErrorResponse.

        Each Pydantic error becomes an ErrorDetail with a dot-path field reference
        so the client knows exactly which field failed and why.
        """
        errors: list[ErrorDetail] = []
        for err in exc.errors():
            # loc is a tuple like ("body", "email") — skip "body" prefix
            loc_parts = [str(p) for p in err["loc"] if p not in ("body", "query", "path")]
            field = ".".join(loc_parts) if loc_parts else None
            errors.append(ErrorDetail(field=field, message=err["msg"]))

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                message="Validation failed",
                errors=errors,
            ).model_dump(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """
        Handles both FastAPI and Starlette HTTP exceptions.
        Starlette raises its own HTTPException for 404/405 route mismatches —
        registering on StarletteHTTPException catches all of them.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(message=str(exc.detail)).model_dump(),
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Catch-all for any unhandled exception.
        Logs the full traceback and returns a safe 500 message.
        """
        logger.error(
            f"Unhandled exception on {request.method} {request.url.path}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                message="An unexpected error occurred. Please try again later."
            ).model_dump(),
        )


# ── Application instance ──────────────────────────────────────────────────────
app = create_app()
