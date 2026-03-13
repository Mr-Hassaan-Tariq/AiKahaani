"""
Integration tests for /api/v1/niches/* endpoints.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from app.models.niche import Niche, NicheStatus


def make_mock_niche(niche_id: int = 1) -> MagicMock:
    n = MagicMock(spec=Niche)
    n.id = niche_id
    n.title = f"Tech Reviews #{niche_id}"
    n.tagline = "Gadgets explained"
    n.thumbnail_url = None
    n.tone = ["informative", "engaging"]
    n.pacing = ["fast"]
    n.best_for = "tech creators"
    n.status = NicheStatus.active
    n.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    n.updated_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    n.prompt = "Write in tech review style"
    n.script_structure = {}
    n.top_channels = None
    n.niche_tones = []
    n.niche_pacings = []
    return n


# ── GET /api/v1/niches ────────────────────────────────────────────────────────


async def test_list_niches_requires_auth(anon_client: AsyncClient):
    resp = await anon_client.get("/api/v1/niches")
    assert resp.status_code == 401


async def test_list_niches_empty(client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one.return_value = 0
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    resp = await client.get("/api/v1/niches")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == []
    assert body["meta"]["total"] == 0


async def test_list_niches_returns_items(client: AsyncClient, mock_db: AsyncMock):
    niches = [make_mock_niche(1), make_mock_niche(2)]
    mock_db.execute.return_value.scalar_one.return_value = 2
    mock_db.execute.return_value.scalars.return_value.all.return_value = niches

    resp = await client.get("/api/v1/niches")
    assert resp.status_code == 200
    body = resp.json()
    assert body["meta"]["total"] == 2
    assert len(body["data"]) == 2
    assert body["data"][0]["title"] == "Tech Reviews #1"


async def test_list_niches_pagination(client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one.return_value = 50
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    resp = await client.get("/api/v1/niches?limit=10&offset=20")
    assert resp.status_code == 200
    meta = resp.json()["meta"]
    assert meta["limit"] == 10
    assert meta["offset"] == 20
    assert meta["total"] == 50
    assert meta["has_prev"] is True
    assert meta["has_next"] is True


async def test_list_niches_limit_out_of_range(client: AsyncClient):
    resp = await client.get("/api/v1/niches?limit=200")
    assert resp.status_code == 422


# ── GET /api/v1/niches/{niche_id} ────────────────────────────────────────────


async def test_get_niche_requires_auth(anon_client: AsyncClient):
    resp = await anon_client.get("/api/v1/niches/1")
    assert resp.status_code == 401


async def test_get_niche_not_found(client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    resp = await client.get("/api/v1/niches/999")
    assert resp.status_code == 404


async def test_get_niche_success(client: AsyncClient, mock_db: AsyncMock):
    niche = make_mock_niche(1)
    mock_db.execute.return_value.scalar_one_or_none.return_value = niche

    resp = await client.get("/api/v1/niches/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Tech Reviews #1"
    assert data["status"] == "active"
