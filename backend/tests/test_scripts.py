"""
Integration tests for /api/v1/scripts/* endpoints.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

import pytest
from httpx import AsyncClient

from app.models.script import Tone, ToneScope, TemplateStyle


# ── GET /api/v1/scripts/tones ────────────────────────────────────────────────


async def test_list_tones_requires_auth(anon_client: AsyncClient):
    resp = await anon_client.get("/api/v1/scripts/tones")
    assert resp.status_code == 401


async def test_list_tones_success(client: AsyncClient, mock_db: AsyncMock):
    mock_tone = MagicMock(spec=Tone)
    mock_tone.id = 1
    mock_tone.name = "Informative"
    mock_tone.scope = ToneScope.script
    mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_tone]

    resp = await client.get("/api/v1/scripts/tones")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]["tones"]) == 1
    assert body["data"]["tones"][0]["name"] == "Informative"


async def test_list_tones_empty(client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalars.return_value.all.return_value = []
    resp = await client.get("/api/v1/scripts/tones")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["tones"] == []


# ── GET /api/v1/scripts/template-styles ──────────────────────────────────────


async def test_list_template_styles_requires_auth(anon_client: AsyncClient):
    resp = await anon_client.get("/api/v1/scripts/template-styles")
    assert resp.status_code == 401


async def test_list_template_styles_success(client: AsyncClient, mock_db: AsyncMock):
    mock_style = MagicMock(spec=TemplateStyle)
    mock_style.id = 1
    mock_style.name = "Short"
    mock_style.min_length = 2800
    mock_style.max_length = 3000
    mock_style.duration = 20
    mock_style.outline_sections = 4
    mock_style.description = "A short script"
    mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_style]

    resp = await client.get("/api/v1/scripts/template-styles")
    assert resp.status_code == 200
    styles = resp.json()["data"]["template_styles"]
    assert len(styles) == 1
    assert styles[0]["name"] == "Short"


# ── POST /api/v1/scripts/titles/generate ─────────────────────────────────────


async def test_generate_titles_requires_auth(anon_client: AsyncClient):
    resp = await anon_client.post(
        "/api/v1/scripts/titles/generate",
        json={"prompt": "How to grow on YouTube"},
    )
    assert resp.status_code == 401


async def test_generate_titles_prompt_too_short(client: AsyncClient):
    resp = await client.post(
        "/api/v1/scripts/titles/generate",
        json={"prompt": "abc"},  # min_length=5
    )
    assert resp.status_code == 422


async def test_generate_titles_prompt_too_long(client: AsyncClient):
    resp = await client.post(
        "/api/v1/scripts/titles/generate",
        json={"prompt": "x" * 2001},  # max_length=2000
    )
    assert resp.status_code == 422


async def test_generate_titles_title_count_out_of_range(client: AsyncClient):
    resp = await client.post(
        "/api/v1/scripts/titles/generate",
        json={"prompt": "How to grow on YouTube", "title_count": 25},  # max=20
    )
    assert resp.status_code == 422


async def test_generate_titles_success(client: AsyncClient, mock_db: AsyncMock):
    fake_titles = [
        {
            "title": "10 Ways to Grow Fast",
            "angle": "growth",
            "tension_pair": None,
            "levers": None,
            "emotion_target": None,
            "power_words": None,
            "length_chars": 22,
            "word_count": 5,
            "truncation_safe": True,
            "notes": None,
        }
    ]
    fake_metadata = {"model": "gpt-4.1", "tokens_used": 100, "generation_time": 1.5}

    async def _set_refresh_attrs(obj):
        obj.id = uuid.uuid4()
        obj.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)

    mock_db.refresh = AsyncMock(side_effect=_set_refresh_attrs)

    with patch(
        "app.api.v1.scripts.router.openai_service.generate_titles",
        return_value=(fake_titles, fake_metadata),
    ):
        resp = await client.post(
            "/api/v1/scripts/titles/generate",
            json={"prompt": "How to grow on YouTube fast"},
        )

    assert resp.status_code == 201
    assert resp.json()["success"] is True


# ── POST /api/v1/scripts/outlines/generate ───────────────────────────────────


async def test_generate_outline_requires_auth(anon_client: AsyncClient):
    resp = await anon_client.post(
        "/api/v1/scripts/outlines/generate",
        json={"description": "A video about productivity"},
    )
    assert resp.status_code == 401


async def test_generate_outline_description_too_short(client: AsyncClient):
    resp = await client.post(
        "/api/v1/scripts/outlines/generate",
        json={"description": "hi"},  # min_length=5
    )
    assert resp.status_code == 422


async def test_generate_outline_too_many_tones(client: AsyncClient):
    resp = await client.post(
        "/api/v1/scripts/outlines/generate",
        json={
            "description": "A video about productivity hacks",
            "tones": [1, 2, 3, 4, 5, 6],  # max 5
        },
    )
    assert resp.status_code == 422


# ── GET /api/v1/scripts/outlines ─────────────────────────────────────────────


async def test_list_outlines_requires_auth(anon_client: AsyncClient):
    resp = await anon_client.get("/api/v1/scripts/outlines")
    assert resp.status_code == 401


async def test_list_outlines_success(client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one.return_value = 0
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    resp = await client.get("/api/v1/scripts/outlines")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    # OutlineListResponse is nested under data: {outlines: [...], total: N}
    assert "outlines" in body["data"]
    assert isinstance(body["data"]["outlines"], list)


async def test_list_outlines_pagination_params(client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one.return_value = 0
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    resp = await client.get("/api/v1/scripts/outlines?limit=5&offset=10")
    assert resp.status_code == 200
    # Data is OutlineListResponse {outlines: [...], total: N}
    data = resp.json()["data"]
    assert "outlines" in data
    assert "total" in data


# ── GET /api/v1/scripts/outlines/{id} ────────────────────────────────────────


async def test_get_outline_not_found(client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    resp = await client.get(f"/api/v1/scripts/outlines/{uuid.uuid4()}")
    assert resp.status_code == 404


# ── GET /api/v1/scripts/scripts ──────────────────────────────────────────────


async def test_list_scripts_requires_auth(anon_client: AsyncClient):
    resp = await anon_client.get("/api/v1/scripts/scripts")
    assert resp.status_code == 401


async def test_list_scripts_success(client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one.return_value = 0
    mock_db.execute.return_value.scalars.return_value.all.return_value = []

    resp = await client.get("/api/v1/scripts/scripts")
    assert resp.status_code == 200
    assert resp.json()["success"] is True


# ── GET /api/v1/scripts/scripts/{id} ─────────────────────────────────────────


async def test_get_script_not_found(client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    resp = await client.get(f"/api/v1/scripts/scripts/{uuid.uuid4()}")
    assert resp.status_code == 404


# ── DELETE /api/v1/scripts/outlines/{id} ─────────────────────────────────────


async def test_delete_outline_requires_auth(anon_client: AsyncClient):
    resp = await anon_client.delete(f"/api/v1/scripts/outlines/{uuid.uuid4()}")
    assert resp.status_code == 401


async def test_delete_outline_not_found(client: AsyncClient, mock_db: AsyncMock):
    mock_db.execute.return_value.scalar_one_or_none.return_value = None
    resp = await client.delete(f"/api/v1/scripts/outlines/{uuid.uuid4()}")
    assert resp.status_code == 404
