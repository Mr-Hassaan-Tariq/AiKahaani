"""
Admin router — /api/v1/admin/*

All endpoints require admin or super_admin role (get_current_admin dependency).

Endpoints:
  GET  /stats                                 — platform statistics
  GET  /user-stats                            — user statistics breakdown

  GET  /users                                 — list users (search, filter)
  GET  /users/{user_id}                       — user detail
  PATCH /users/{user_id}                      — update user
  DELETE /users/{user_id}                     — soft-delete (is_active=False)
  POST /users/{user_id}/activate              — set is_active=True
  POST /users/{user_id}/deactivate            — set is_active=False
  PATCH /users/{user_id}/role                 — change user role

  GET  /niches                                — list all niches (admin view)
  POST /niches                                — create niche
  GET  /niches/{niche_id}                     — get niche detail
  PATCH /niches/{niche_id}                    — update niche
  DELETE /niches/{niche_id}                   — delete niche

  GET  /reports/users                         — usage report (JSON, paginated)
  GET  /reports/users/export                  — usage report (CSV)
  GET  /reports/conversion-funnel             — conversion funnel (JSON, paginated)
  GET  /reports/conversion-funnel/export      — conversion funnel (CSV)
"""

import csv
import io
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_admin
from app.core.responses import responses
from app.database import get_db
from app.models.niche import Niche, NichePacing, NicheStatus, NicheTone
from app.models.script import FullScript, TitleGeneration
from app.models.user import User, UserPlan, UserRole
from app.schemas.admin import (
    AdminNicheCreateRequest,
    AdminNicheOut,
    AdminNicheUpdateRequest,
    AdminRoleUpdateRequest,
    AdminUserDetailOut,
    AdminUserListOut,
    AdminUserUpdateRequest,
    ConversionFunnelItemOut,
    FeatureUsageOut,
    PlatformStatsOut,
    UserReportItemOut,
    UserStatsOut,
)
from app.schemas.common import ApiResponse, PaginatedResponse

logger = logging.getLogger(__name__)

admin_router = APIRouter(tags=["Admin"])


# ── Statistics ────────────────────────────────────────────────────────────────


@admin_router.get("/stats", response_model=ApiResponse[PlatformStatsOut])
async def get_platform_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """High-level platform statistics."""
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    total_users = (await db.execute(select(func.count()).select_from(User))).scalar_one()
    new_this_week = (
        await db.execute(
            select(func.count()).select_from(User).where(User.created_at >= one_week_ago)
        )
    ).scalar_one()
    script_count = (
        await db.execute(select(func.count()).select_from(FullScript))
    ).scalar_one()
    title_count = (
        await db.execute(select(func.count()).select_from(TitleGeneration))
    ).scalar_one()
    niche_count = (
        await db.execute(
            select(func.count()).select_from(Niche).where(Niche.status == NicheStatus.active)
        )
    ).scalar_one()

    return responses.ok(
        data=PlatformStatsOut(
            total_users=total_users,
            new_users_this_week=new_this_week,
            feature_usage=FeatureUsageOut(
                script_generator=script_count,
                title_generator=title_count,
                niche_vault=niche_count,
            ),
        ),
        message="Platform stats retrieved",
    )


@admin_router.get("/user-stats", response_model=ApiResponse[UserStatsOut])
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Detailed user statistics breakdown."""
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    total = (await db.execute(select(func.count()).select_from(User))).scalar_one()
    active = (
        await db.execute(
            select(func.count()).select_from(User).where(User.is_active == True)  # noqa: E712
        )
    ).scalar_one()
    inactive = (
        await db.execute(
            select(func.count()).select_from(User).where(User.is_active == False)  # noqa: E712
        )
    ).scalar_one()
    verified = (
        await db.execute(
            select(func.count()).select_from(User).where(User.is_email_verified == True)  # noqa: E712
        )
    ).scalar_one()
    admin_count = (
        await db.execute(
            select(func.count())
            .select_from(User)
            .where(User.role.in_([UserRole.admin, UserRole.super_admin]))
        )
    ).scalar_one()
    user_count = (
        await db.execute(
            select(func.count()).select_from(User).where(User.role == UserRole.user)
        )
    ).scalar_one()
    new_this_week = (
        await db.execute(
            select(func.count()).select_from(User).where(User.created_at >= one_week_ago)
        )
    ).scalar_one()
    pro_users = (
        await db.execute(
            select(func.count()).select_from(User).where(User.plan == UserPlan.pro)
        )
    ).scalar_one()
    free_users = (
        await db.execute(
            select(func.count()).select_from(User).where(User.plan == UserPlan.free)
        )
    ).scalar_one()

    return responses.ok(
        data=UserStatsOut(
            total_users=total,
            active_users=active,
            inactive_users=inactive,
            verified_users=verified,
            admin_count=admin_count,
            user_count=user_count,
            new_this_week=new_this_week,
            pro_users=pro_users,
            free_users=free_users,
        ),
        message="User stats retrieved",
    )


# ── User Management ───────────────────────────────────────────────────────────


@admin_router.get("/users", response_model=PaginatedResponse[AdminUserListOut])
async def list_users(
    search: Optional[str] = Query(None, description="Search by email, username, or fullname"),
    is_active: Optional[bool] = Query(None),
    role: Optional[str] = Query(None, description="Filter by role: user, admin, super_admin"),
    is_email_verified: Optional[bool] = Query(None),
    plan: Optional[str] = Query(None, description="Filter by plan: free, pro"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """List all users with optional search and filtering."""
    base = select(User)

    if search:
        term = f"%{search}%"
        base = base.where(
            or_(
                User.email.ilike(term),
                User.username.ilike(term),
                User.fullname.ilike(term),
            )
        )
    if is_active is not None:
        base = base.where(User.is_active == is_active)
    if role:
        try:
            base = base.where(User.role == UserRole(role))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Valid values: {[r.value for r in UserRole]}",
            )
    if is_email_verified is not None:
        base = base.where(User.is_email_verified == is_email_verified)
    if plan:
        try:
            base = base.where(User.plan == UserPlan(plan))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid plan. Valid values: {[p.value for p in UserPlan]}",
            )

    total = (
        await db.execute(select(func.count()).select_from(base.subquery()))
    ).scalar_one()
    result = await db.execute(
        base.order_by(User.created_at.desc()).offset(offset).limit(limit)
    )
    users = result.scalars().all()

    return responses.paginated(
        data=[AdminUserListOut.model_validate(u) for u in users],
        total=total,
        limit=limit,
        offset=offset,
        message="Users retrieved",
    )


@admin_router.get("/users/{user_id}", response_model=ApiResponse[AdminUserDetailOut])
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return responses.ok(
        data=AdminUserDetailOut.model_validate(user), message="User retrieved"
    )


@admin_router.patch("/users/{user_id}", response_model=ApiResponse[AdminUserDetailOut])
async def update_user(
    user_id: int,
    body: AdminUserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Update a user's profile fields (partial update)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = body.model_dump(exclude_none=True)

    if "email" in update_data and update_data["email"] != user.email:
        existing = await db.execute(
            select(User).where(User.email == update_data["email"], User.id != user_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already in use"
            )

    if "username" in update_data and update_data["username"] != user.username:
        existing = await db.execute(
            select(User).where(
                User.username == update_data["username"], User.id != user_id
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Username already in use"
            )

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    logger.info("[ADMIN] User %d updated by admin %d", user_id, admin.id)
    return responses.ok(data=AdminUserDetailOut.model_validate(user), message="User updated")


@admin_router.delete("/users/{user_id}", response_model=ApiResponse[None])
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Soft-delete a user (set is_active=False). Cannot delete own account."""
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = False
    await db.commit()
    logger.info("[ADMIN] User %d soft-deleted by admin %d", user_id, admin.id)
    return responses.deleted(message="User deactivated")


@admin_router.post("/users/{user_id}/activate", response_model=ApiResponse[AdminUserDetailOut])
async def activate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify your own account status",
        )
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = True
    await db.commit()
    await db.refresh(user)
    logger.info("[ADMIN] User %d activated by admin %d", user_id, admin.id)
    return responses.ok(data=AdminUserDetailOut.model_validate(user), message="User activated")


@admin_router.post(
    "/users/{user_id}/deactivate", response_model=ApiResponse[AdminUserDetailOut]
)
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify your own account status",
        )
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_active = False
    await db.commit()
    await db.refresh(user)
    logger.info("[ADMIN] User %d deactivated by admin %d", user_id, admin.id)
    return responses.ok(
        data=AdminUserDetailOut.model_validate(user), message="User deactivated"
    )


@admin_router.patch("/users/{user_id}/role", response_model=ApiResponse[AdminUserDetailOut])
async def update_user_role(
    user_id: int,
    body: AdminRoleUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Change a user's role. Only super_admin can assign super_admin role."""
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role",
        )

    new_role = UserRole(body.role)
    if new_role == UserRole.super_admin and admin.role != UserRole.super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super_admin can assign super_admin role",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.role = new_role
    await db.commit()
    await db.refresh(user)
    logger.info(
        "[ADMIN] User %d role set to %s by admin %d", user_id, body.role, admin.id
    )
    return responses.ok(
        data=AdminUserDetailOut.model_validate(user), message="User role updated"
    )


# ── Niche Management ──────────────────────────────────────────────────────────


async def _sync_niche_tones(db: AsyncSession, niche: Niche, tones: list[str]) -> None:
    """Replace niche's NicheTone rows with the provided list (deduplicated)."""
    await db.execute(
        NicheTone.__table__.delete().where(NicheTone.niche_id == niche.id)
    )
    seen: set[str] = set()
    for name in tones:
        name = name.strip()
        if name and name not in seen:
            db.add(NicheTone(niche_id=niche.id, name=name))
            seen.add(name)


async def _sync_niche_pacings(db: AsyncSession, niche: Niche, pacings: list[str]) -> None:
    """Replace niche's NichePacing rows with the provided list (deduplicated)."""
    await db.execute(
        NichePacing.__table__.delete().where(NichePacing.niche_id == niche.id)
    )
    seen: set[str] = set()
    for name in pacings:
        name = name.strip()
        if name and name not in seen:
            db.add(NichePacing(niche_id=niche.id, name=name))
            seen.add(name)


@admin_router.get("/niches", response_model=PaginatedResponse[AdminNicheOut])
async def admin_list_niches(
    search: Optional[str] = Query(None, description="Search by title or tagline"),
    niche_status: Optional[str] = Query(None, alias="status", description="active or inactive"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """List all niches (active and inactive) for admin review."""
    base = select(Niche)

    if search:
        term = f"%{search}%"
        base = base.where(
            or_(Niche.title.ilike(term), Niche.tagline.ilike(term))
        )
    if niche_status:
        try:
            base = base.where(Niche.status == NicheStatus(niche_status))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Valid values: active, inactive",
            )

    total = (
        await db.execute(select(func.count()).select_from(base.subquery()))
    ).scalar_one()
    result = await db.execute(
        base.order_by(Niche.created_at.desc()).offset(offset).limit(limit)
    )
    niches = result.scalars().all()

    return responses.paginated(
        data=[AdminNicheOut.model_validate(n) for n in niches],
        total=total,
        limit=limit,
        offset=offset,
        message="Niches retrieved",
    )


@admin_router.post("/niches", response_model=ApiResponse[AdminNicheOut], status_code=201)
async def admin_create_niche(
    body: AdminNicheCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Create a new niche. tone/pacing lists are synced to NicheTone/NichePacing rows."""
    existing = await db.execute(select(Niche).where(Niche.title == body.title))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A niche with this title already exists",
        )

    niche = Niche(
        title=body.title,
        tagline=body.tagline,
        prompt=body.prompt,
        thumbnail_url=body.thumbnail_url,
        script_structure=body.script_structure,
        tone=body.tone,
        pacing=body.pacing,
        top_channels=body.top_channels,
        best_for=body.best_for,
        status=NicheStatus(body.status),
    )
    db.add(niche)
    await db.flush()  # get niche.id before adding child rows

    if body.tone:
        await _sync_niche_tones(db, niche, body.tone)
    if body.pacing:
        await _sync_niche_pacings(db, niche, body.pacing)

    await db.commit()
    await db.refresh(niche)
    logger.info("[ADMIN] Niche %d '%s' created by admin %d", niche.id, niche.title, admin.id)
    return responses.created(
        data=AdminNicheOut.model_validate(niche), message="Niche created"
    )


@admin_router.get("/niches/{niche_id}", response_model=ApiResponse[AdminNicheOut])
async def admin_get_niche(
    niche_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    result = await db.execute(select(Niche).where(Niche.id == niche_id))
    niche = result.scalar_one_or_none()
    if not niche:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Niche not found")
    return responses.ok(data=AdminNicheOut.model_validate(niche), message="Niche retrieved")


@admin_router.patch("/niches/{niche_id}", response_model=ApiResponse[AdminNicheOut])
async def admin_update_niche(
    niche_id: int,
    body: AdminNicheUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    result = await db.execute(select(Niche).where(Niche.id == niche_id))
    niche = result.scalar_one_or_none()
    if not niche:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Niche not found")

    update_data = body.model_dump(exclude_none=True)

    if "title" in update_data and update_data["title"] != niche.title:
        existing = await db.execute(
            select(Niche).where(Niche.title == update_data["title"], Niche.id != niche_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A niche with this title already exists",
            )

    tone_list = update_data.pop("tone", None)
    pacing_list = update_data.pop("pacing", None)

    if "status" in update_data:
        update_data["status"] = NicheStatus(update_data["status"])

    for field, value in update_data.items():
        setattr(niche, field, value)

    if tone_list is not None:
        niche.tone = tone_list
        await _sync_niche_tones(db, niche, tone_list)
    if pacing_list is not None:
        niche.pacing = pacing_list
        await _sync_niche_pacings(db, niche, pacing_list)

    await db.commit()
    await db.refresh(niche)
    logger.info("[ADMIN] Niche %d updated by admin %d", niche_id, admin.id)
    return responses.ok(data=AdminNicheOut.model_validate(niche), message="Niche updated")


@admin_router.delete("/niches/{niche_id}", response_model=ApiResponse[None])
async def admin_delete_niche(
    niche_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    result = await db.execute(select(Niche).where(Niche.id == niche_id))
    niche = result.scalar_one_or_none()
    if not niche:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Niche not found")

    await db.delete(niche)
    await db.commit()
    logger.info("[ADMIN] Niche %d deleted by admin %d", niche_id, admin.id)
    return responses.deleted(message="Niche deleted")


# ── Reports ───────────────────────────────────────────────────────────────────


def _parse_date(date_str: Optional[str], param_name: str) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{param_name} must be in YYYY-MM-DD format",
        )


async def _build_user_report_rows(
    db: AsyncSession,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    limit: int,
    offset: int,
) -> tuple[list[UserReportItemOut], int]:
    """Return (rows, total) for the user usage report."""
    user_q = select(User)
    if start_date:
        user_q = user_q.where(User.created_at >= start_date)
    if end_date:
        user_q = user_q.where(User.created_at <= end_date)

    total = (
        await db.execute(select(func.count()).select_from(user_q.subquery()))
    ).scalar_one()
    result = await db.execute(
        user_q.order_by(User.created_at.desc()).offset(offset).limit(limit)
    )
    users = result.scalars().all()

    # Short: 2800-3500 words, Medium: 5500-6500 words, Long: 8000-9500 words
    rows: list[UserReportItemOut] = []
    for u in users:
        title_count = (
            await db.execute(
                select(func.count())
                .select_from(TitleGeneration)
                .where(TitleGeneration.user_id == u.id)
            )
        ).scalar_one()

        short_count = (
            await db.execute(
                select(func.count())
                .select_from(FullScript)
                .where(
                    and_(
                        FullScript.user_id == u.id,
                        FullScript.word_count.between(2800, 3500),
                    )
                )
            )
        ).scalar_one()
        medium_count = (
            await db.execute(
                select(func.count())
                .select_from(FullScript)
                .where(
                    and_(
                        FullScript.user_id == u.id,
                        FullScript.word_count.between(5500, 6500),
                    )
                )
            )
        ).scalar_one()
        long_count = (
            await db.execute(
                select(func.count())
                .select_from(FullScript)
                .where(
                    and_(
                        FullScript.user_id == u.id,
                        FullScript.word_count.between(8000, 9500),
                    )
                )
            )
        ).scalar_one()

        rows.append(
            UserReportItemOut(
                name=u.fullname or u.username,
                email=u.email,
                total_titles_generated=title_count,
                total_short_scripts=short_count,
                total_medium_scripts=medium_count,
                total_long_scripts=long_count,
            )
        )
    return rows, total


@admin_router.get(
    "/reports/users", response_model=PaginatedResponse[UserReportItemOut]
)
async def user_report(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """User usage report — titles and scripts generated per user."""
    sd = _parse_date(start_date, "start_date")
    ed = _parse_date(end_date, "end_date")
    rows, total = await _build_user_report_rows(db, sd, ed, limit, offset)
    return responses.paginated(
        data=rows,
        total=total,
        limit=limit,
        offset=offset,
        message="User report retrieved",
    )


@admin_router.get("/reports/users/export")
async def user_report_export(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Stream user usage report as a CSV file download."""
    sd = _parse_date(start_date, "start_date")
    ed = _parse_date(end_date, "end_date")
    rows, _ = await _build_user_report_rows(db, sd, ed, limit=10_000, offset=0)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Email", "Total Titles", "Short Scripts", "Medium Scripts", "Long Scripts"])
    for r in rows:
        writer.writerow([
            r.name, r.email,
            r.total_titles_generated,
            r.total_short_scripts,
            r.total_medium_scripts,
            r.total_long_scripts,
        ])
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users_report.csv"},
    )


async def _build_funnel_rows(
    db: AsyncSession,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    limit: int,
    offset: int,
) -> tuple[list[ConversionFunnelItemOut], int]:
    user_q = select(User)
    if start_date:
        user_q = user_q.where(User.created_at >= start_date)
    if end_date:
        user_q = user_q.where(User.created_at <= end_date)

    total = (
        await db.execute(select(func.count()).select_from(user_q.subquery()))
    ).scalar_one()
    result = await db.execute(
        user_q.order_by(User.created_at.desc()).offset(offset).limit(limit)
    )
    users = result.scalars().all()

    rows = [
        ConversionFunnelItemOut(
            name=u.fullname or u.username,
            email=u.email,
            plan=u.plan.value,
            is_active=u.is_active,
            is_email_verified=u.is_email_verified,
            created_at=u.created_at,
        )
        for u in users
    ]
    return rows, total


@admin_router.get(
    "/reports/conversion-funnel",
    response_model=PaginatedResponse[ConversionFunnelItemOut],
)
async def conversion_funnel(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """User conversion funnel — plan, activity, and verification status per user."""
    sd = _parse_date(start_date, "start_date")
    ed = _parse_date(end_date, "end_date")
    rows, total = await _build_funnel_rows(db, sd, ed, limit, offset)
    return responses.paginated(
        data=rows,
        total=total,
        limit=limit,
        offset=offset,
        message="Conversion funnel retrieved",
    )


@admin_router.get("/reports/conversion-funnel/export")
async def conversion_funnel_export(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Stream conversion funnel as a CSV file download."""
    sd = _parse_date(start_date, "start_date")
    ed = _parse_date(end_date, "end_date")
    rows, _ = await _build_funnel_rows(db, sd, ed, limit=10_000, offset=0)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Email", "Plan", "Active", "Email Verified", "Joined"])
    for r in rows:
        writer.writerow([
            r.name, r.email, r.plan,
            "Yes" if r.is_active else "No",
            "Yes" if r.is_email_verified else "No",
            r.created_at.strftime("%Y-%m-%d"),
        ])
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=conversion_funnel.csv"},
    )
