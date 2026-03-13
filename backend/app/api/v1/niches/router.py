"""
Niches router — /api/v1/niches/*

Endpoints:
  GET /           — list active niches (paginated)
  GET /{niche_id} — get single niche detail
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_current_user
from app.core.responses import responses
from app.database import get_db
from app.models.niche import Niche, NicheStatus
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.niche import NicheDetailOut, NicheOut

logger = logging.getLogger(__name__)

niches_router = APIRouter(tags=["Niches"])


@niches_router.get("", response_model=PaginatedResponse[NicheOut])
async def list_niches(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List all active niches."""
    count_result = await db.execute(
        select(func.count()).select_from(Niche).where(Niche.status == NicheStatus.active)
    )
    total = count_result.scalar_one()

    result = await db.execute(
        select(Niche)
        .where(Niche.status == NicheStatus.active)
        .order_by(Niche.title)
        .offset(offset)
        .limit(limit)
    )
    niches = result.scalars().all()

    return responses.paginated(
        data=[NicheOut.model_validate(n) for n in niches],
        total=total,
        limit=limit,
        offset=offset,
        message="Niches retrieved",
    )


@niches_router.get("/{niche_id}", response_model=NicheDetailOut)
async def get_niche(
    niche_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get full niche detail including structure, tones, and pacings."""
    result = await db.execute(
        select(Niche)
        .where(Niche.id == niche_id, Niche.status == NicheStatus.active)
        .options(
            selectinload(Niche.niche_tones),
            selectinload(Niche.niche_pacings),
        )
    )
    niche = result.scalar_one_or_none()
    if not niche:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Niche not found"
        )

    return NicheDetailOut.model_validate(niche)
