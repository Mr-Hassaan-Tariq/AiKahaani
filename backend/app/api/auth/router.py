"""
Auth router — /api/auth/*

Auth endpoints are not versioned because the authentication contract
(signup, login, logout, token refresh) is stable and shared across all
API versions.
"""

import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.rate_limit import limiter
from app.core.responses import responses
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    AdminLoginOut,
    AdminLoginRequest,
    AuthTokensOut,
    GoogleAuthRequest,
    LogoutRequest,
    MagicLinkRequest,
    MagicLinkVerifyOut,
    MagicLinkVerifyRequest,
    RefreshTokenOut,
    RefreshTokenRequest,
    SignupRequest,
    SignupResponse,
    UserBasicOut,
    UserOut,
)
from app.schemas.common import ApiResponse
from app.services.auth import service as auth_service

logger = logging.getLogger(__name__)

auth_router = APIRouter(tags=["Auth"])


# ── POST /api/auth/signup ─────────────────────────────────────────────────────


@auth_router.post(
    "/signup",
    response_model=ApiResponse[SignupResponse],
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/hour")
async def signup(
    request: Request,
    body: SignupRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[SignupResponse]:
    """Create a new user account with email and password."""
    if body.password != body.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Passwords don't match",
        )
    try:
        user = await auth_service.signup(
            db,
            email=str(body.email),
            username=body.username,
            fullname=body.fullname,
            password=body.password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return responses.created(
        data=SignupResponse(user=UserOut.model_validate(user)),
        message="User created successfully",
    )


# ── POST /api/auth/google ─────────────────────────────────────────────────────


@auth_router.post(
    "/google",
    response_model=ApiResponse[AuthTokensOut],
)
@limiter.limit("20/minute")
async def google_login(
    request: Request,
    body: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AuthTokensOut]:
    """Authenticate with a Google ID token or authorization code."""
    try:
        access, refresh, user, created = await auth_service.google_auth(
            db,
            id_token=body.id_token,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except httpx.HTTPError as exc:
        logger.error("Google auth HTTP error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service temporarily unavailable",
        )

    return responses.ok(
        data=AuthTokensOut(
            access=access,
            refresh=refresh,
            user=UserBasicOut.model_validate(user),
            created=created,
        ),
        message="Authentication successful",
    )


# ── POST /api/auth/magic-link ─────────────────────────────────────────────────


@auth_router.post(
    "/magic-link",
    response_model=ApiResponse[None],
)
@limiter.limit("5/10minutes")
async def magic_link_send(
    request: Request,
    body: MagicLinkRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    """Send a magic link to the provided email for passwordless login."""
    try:
        await auth_service.send_magic_link(db, email=str(body.email))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))

    return responses.no_data(message="Magic link sent to your email")


# ── POST /api/auth/magic-link/verify ─────────────────────────────────────────


@auth_router.post(
    "/magic-link/verify",
    response_model=ApiResponse[MagicLinkVerifyOut],
)
@limiter.limit("10/minute")
async def magic_link_verify(
    request: Request,
    body: MagicLinkVerifyRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MagicLinkVerifyOut]:
    """Verify a magic link token and return JWT tokens."""
    try:
        access, refresh, user = await auth_service.verify_magic_link(
            db,
            token=body.token,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return responses.ok(
        data=MagicLinkVerifyOut(
            access=access,
            refresh=refresh,
            user=UserBasicOut.model_validate(user),
        ),
        message="Authentication successful",
    )


# ── POST /api/auth/admin/login ────────────────────────────────────────────────


@auth_router.post(
    "/admin/login",
    response_model=ApiResponse[AdminLoginOut],
)
async def admin_login(
    body: AdminLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AdminLoginOut]:
    """Login for admin and super_admin users (email + password)."""
    try:
        access, refresh, user = await auth_service.admin_login(
            db,
            email=str(body.email),
            password=body.password,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return responses.ok(
        data=AdminLoginOut(
            access_token=access,
            refresh_token=refresh,
            user=UserOut.model_validate(user),
            message="Admin login successful",
        ),
        message="Admin login successful",
    )


# ── POST /api/auth/refresh ────────────────────────────────────────────────────


@auth_router.post(
    "/refresh",
    response_model=ApiResponse[RefreshTokenOut],
)
@limiter.limit("30/minute")
async def refresh_token(
    request: Request,
    body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[RefreshTokenOut]:
    """Exchange a valid refresh token for a new access + refresh token pair."""
    try:
        new_access, new_refresh = await auth_service.refresh_tokens(
            db, refresh_token=body.refresh_token
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return responses.ok(
        data=RefreshTokenOut(
            access_token=new_access,
            refresh_token=new_refresh,
            message="Token refreshed successfully",
        ),
        message="Token refreshed successfully",
    )


# ── POST /api/auth/logout ─────────────────────────────────────────────────────


@auth_router.post(
    "/logout",
    response_model=ApiResponse[None],
)
async def logout(
    body: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    """Logout the current user by invalidating their refresh token."""
    await auth_service.logout(
        db,
        user_id=current_user.id,
        refresh_token=body.refresh_token,
    )
    return responses.no_data(message="Logged out successfully")
