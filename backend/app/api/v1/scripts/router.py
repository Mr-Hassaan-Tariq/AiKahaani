"""
Scripts router — /api/v1/scripts/*

Endpoints:
  GET  /tones                          — list all tones
  GET  /template-styles                — list all template styles
  POST /titles/generate                — generate YouTube titles
  POST /outlines/generate              — generate script outline
  GET  /outlines                       — list user's outlines
  GET  /outlines/{outline_id}          — get single outline
  DELETE /outlines/{outline_id}        — delete outline
  POST /outlines/{outline_id}/script   — generate full script from outline
  GET  /scripts                        — list user's full scripts
  GET  /scripts/{script_id}            — get single full script
  DELETE /scripts/{script_id}          — delete full script
"""

import json
import logging
import re
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_current_user
from app.core.rate_limit import limiter
from app.core.responses import responses
from app.database import get_db
from app.models.script import (
    FullScript,
    OutlineTone,
    ScriptOutline,
    TemplateStyle,
    TitleGeneration,
    TitleGenerationType,
    Tone,
)
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.script import (
    FullScriptOut,
    GenerateOutlineRequest,
    GenerateOutlineResponse,
    GenerateScriptRequest,
    GenerateScriptResponse,
    GenerateTitlesRequest,
    GenerateTitlesResponse,
    OutlineListResponse,
    ScriptListResponse,
    ScriptOutlineOut,
    ScriptConfigOut,
    TemplateStyleOut,
    TemplateStylesListResponse,
    TitleGenerationOut,
    TitleItemOut,
    ToneOut,
    TonesListResponse,
    UpdateOutlineStatusRequest,
    UpdateScriptStatusRequest,
)
from app.services.scripts import article_scraper, openai_service, youtube_transcript
from app.services.scripts.niche_context import build_niche_context
from app.services.scripts.word_count_strategy import TemplateStyleConfig

logger = logging.getLogger(__name__)

scripts_router = APIRouter(tags=["Scripts"])


# ── Lookup endpoints ───────────────────────────────────────────────────────────


@scripts_router.get("/tones", response_model=ApiResponse[TonesListResponse])
async def list_tones(
    scope: Optional[str] = Query(
        None, description="Filter by scope: script, title, both"
    ),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> ApiResponse[TonesListResponse]:
    """List all available tones."""
    q = select(Tone).order_by(Tone.name)
    if scope:
        q = q.where(Tone.scope == scope)
    result = await db.execute(q)
    tones = result.scalars().all()
    return responses.ok(
        data=TonesListResponse(tones=[ToneOut.model_validate(t) for t in tones]),
        message="Tones retrieved",
    )


@scripts_router.get(
    "/template-styles", response_model=ApiResponse[TemplateStylesListResponse]
)
async def list_template_styles(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> ApiResponse[TemplateStylesListResponse]:
    """List all template styles."""
    result = await db.execute(select(TemplateStyle).order_by(TemplateStyle.id))
    styles = result.scalars().all()
    return responses.ok(
        data=TemplateStylesListResponse(
            template_styles=[TemplateStyleOut.model_validate(s) for s in styles]
        ),
        message="Template styles retrieved",
    )


# ── Script config (new-script UI) ────────────────────────────────────────────


@scripts_router.get("/config", response_model=ScriptConfigOut)
@scripts_router.get("/config/", response_model=ScriptConfigOut, include_in_schema=False)
async def get_script_config(
    db: AsyncSession = Depends(get_db),
) -> ScriptConfigOut:
    """
    Return the exact config shape the web-app's new-script page expects.

    This endpoint is intentionally "raw" (not wrapped in ApiResponse) because
    the web-app fetches it via `getServerDataAction`, which directly parses JSON
    into `GenerationPromptType`.
    """

    tones_result = await db.execute(select(Tone).order_by(Tone.name))
    tones = tones_result.scalars().all()

    styles_result = await db.execute(select(TemplateStyle).order_by(TemplateStyle.id))
    styles = styles_result.scalars().all()

    styles_min = min((s.min_length for s in styles), default=300)
    styles_max = max((s.max_length for s in styles), default=3000)
    default_words = 1000
    if default_words < styles_min:
        default_words = styles_min
    if default_words > styles_max:
        default_words = styles_max

    return ScriptConfigOut(
        tones=[ToneOut.model_validate(t) for t in tones],
        template_styles=[
            {
                **TemplateStyleOut.model_validate(s).model_dump(
                    exclude={"outline_sections"}
                ),
                "word_range": f"{s.min_length}-{s.max_length} words",
            }
            for s in styles
        ],
        length_range={"min": styles_min, "max": styles_max, "default": default_words},
    )


# ── Title Generation ───────────────────────────────────────────────────────────


@scripts_router.post(
    "/titles/generate",
    response_model=ApiResponse[GenerateTitlesResponse],
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/minute")
async def generate_titles(
    request: Request,
    body: GenerateTitlesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[GenerateTitlesResponse]:
    """Generate YouTube titles via Chat Completions."""
    if not body.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    try:
        titles, metadata = await openai_service.generate_titles(
            prompt=body.prompt,
            title_count=body.title_count,
            tones=body.tones,
        )
    except Exception as exc:
        logger.error("[TITLES] Generation failed for user %s: %s", current_user.id, exc)
        raise HTTPException(
            status_code=500, detail="Title generation failed. Please try again."
        )

    # Persist to TitleGeneration table
    tg = TitleGeneration(
        user_id=current_user.id,
        generation_type=TitleGenerationType.from_idea,
        prompt=body.prompt,
        tones=body.tones or [],
        titles=titles,
        titles_count=len(titles),
    )
    db.add(tg)
    await db.commit()
    await db.refresh(tg)

    return responses.created(
        data=GenerateTitlesResponse(
            generation=TitleGenerationOut(
                id=tg.id,
                generation_type=tg.generation_type.value,
                titles=tg.titles,
                titles_count=tg.titles_count,
                tones=tg.tones,
                created_at=tg.created_at,
            ),
            titles=[TitleItemOut(**t) for t in titles],
            metadata=metadata,
        ),
        message="Titles generated successfully",
    )


# ── Outline Generation ─────────────────────────────────────────────────────────


@scripts_router.post(
    "/outlines/generate",
    response_model=ApiResponse[GenerateOutlineResponse],
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
async def generate_outline(
    request: Request,
    body: GenerateOutlineRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[GenerateOutlineResponse]:
    """Generate a script outline from a description/topic."""
    # --- Resolve tones ---
    if body.tones:
        result = await db.execute(select(Tone).where(Tone.id.in_(body.tones)))
        tone_rows = result.scalars().all()
        if len(tone_rows) != len(body.tones):
            raise HTTPException(status_code=400, detail="One or more invalid tone IDs")
        tone_names = [t.name for t in tone_rows]
    else:
        result = await db.execute(
            select(Tone).where(Tone.name.ilike("Informative")).limit(1)
        )
        default_tone = result.scalar_one_or_none()
        if not default_tone:
            result = await db.execute(select(Tone).limit(1))
            default_tone = result.scalar_one_or_none()
        tone_rows = [default_tone] if default_tone else []
        tone_names = [default_tone.name] if default_tone else ["Informative"]

    # --- Resolve template style ---
    template_style_row: Optional[TemplateStyle] = None
    if body.template_style_id:
        result = await db.execute(
            select(TemplateStyle).where(TemplateStyle.id == body.template_style_id)
        )
        template_style_row = result.scalar_one_or_none()
        if not template_style_row:
            raise HTTPException(status_code=400, detail="Invalid template style ID")
        min_length = template_style_row.min_length
        max_length = template_style_row.max_length
        template_style_name = template_style_row.name.lower().replace(" ", "_")
    else:
        # Use body values or fall back to medium defaults
        wc_config = TemplateStyleConfig.TEMPLATE_CONFIGS.get("medium")
        min_length = body.min_length or wc_config["min_words"]
        max_length = body.max_length or wc_config["max_words"]
        template_style_name = "medium"

    # --- Build combined description with optional attachments ---
    description = body.description
    additional_contexts: List[str] = []

    if body.article_url:
        try:
            a_title, a_content = await article_scraper.scrape_article(body.article_url)
            additional_contexts.append(f"[ARTICLE CONTEXT - {a_title}]: {a_content}")
            logger.info("[OUTLINE] Article context added from: %s", body.article_url)
        except Exception as exc:
            logger.warning("[OUTLINE] Article scrape failed, continuing: %s", exc)

    if body.youtube_url:
        try:
            v_title, transcript = await youtube_transcript.fetch_transcript(
                body.youtube_url
            )
            additional_contexts.append(
                f"[YOUTUBE TRANSCRIPT - {v_title}]: {transcript}"
            )
            logger.info("[OUTLINE] YouTube context added from: %s", body.youtube_url)
        except Exception as exc:
            logger.warning("[OUTLINE] YouTube transcript failed, continuing: %s", exc)

    if additional_contexts:
        description = (
            description.strip()
            + "\n\n"
            + "\n\n".join(c.strip() for c in additional_contexts)
        )

    # --- Niche context ---
    niche_context = await build_niche_context(db, body.niche_id)

    # --- Generate outline ---
    try:
        outline_text, outline_data, metadata = await openai_service.generate_outline(
            description=description,
            tones=tone_names,
            template_style=template_style_name,
            min_length=min_length,
            max_length=max_length,
            niche_context=niche_context or None,
        )
    except Exception as exc:
        logger.error(
            "[OUTLINE] Generation failed for user %s: %s", current_user.id, exc
        )
        raise HTTPException(
            status_code=500, detail="Outline generation failed. Please try again."
        )

    sections = outline_data.get("sections", [])
    if not sections:
        raise HTTPException(
            status_code=500, detail="Outline generation returned no sections"
        )

    # --- Auto-generate title if not provided ---
    if body.title and body.title.strip():
        outline_title = body.title.strip()
    else:
        try:
            gen_titles, _ = await openai_service.generate_titles(
                prompt=body.description[:500],
                title_count=1,
                tones=tone_names,
            )
            outline_title = (
                gen_titles[0]["title"]
                if gen_titles
                else f"Outline: {body.description[:50]}"
            )
        except Exception:
            outline_title = f"Outline: {body.description[:50]}"

    # --- Save outline_data with template params ---
    outline_data_with_params = {
        **outline_data,
        "template_style": template_style_name,
        "template_style_id": body.template_style_id,
        "min_length": min_length,
        "max_length": max_length,
        "description": body.description,
    }
    section_order = outline_data.get("section_order", list(range(len(sections))))

    # --- Persist outline ---
    outline = ScriptOutline(
        user_id=current_user.id,
        niche_id=body.niche_id,
        template_style_id=body.template_style_id,
        title=outline_title,
        outline_text=outline_text,
        outline_data=outline_data_with_params,
        section_order=section_order,
        original_outline=outline_text,
        status="generated",
        openai_model=metadata.get("model_used", metadata.get("model", "")),
        tokens_used=metadata.get("tokens_used", 0),
        generation_time=metadata.get("generation_time", 0.0),
    )
    db.add(outline)
    await db.flush()  # get outline.id

    # --- Persist outline tones ---
    for tone_row in tone_rows:
        db.add(OutlineTone(outline_id=outline.id, tone_id=tone_row.id))

    await db.commit()
    await db.refresh(outline)

    # Reload with tones
    result = await db.execute(
        select(ScriptOutline)
        .where(ScriptOutline.id == outline.id)
        .options(
            selectinload(ScriptOutline.outline_tones).selectinload(OutlineTone.tone)
        )
    )
    outline = result.scalar_one()
    tones_out = [ToneOut.model_validate(ot.tone) for ot in outline.outline_tones]
    outline_out = ScriptOutlineOut(
        **{
            "id": outline.id,
            "title": outline.title,
            "outline_text": outline.outline_text,
            "outline_data": outline.outline_data,
            "section_order": outline.section_order,
            "status": outline.status.value,
            "openai_model": outline.openai_model,
            "tokens_used": outline.tokens_used,
            "generation_time": outline.generation_time,
            "tones": tones_out,
            "created_at": outline.created_at,
            "updated_at": outline.updated_at,
        }
    )

    logger.info(
        "[OUTLINE] Created outline '%s' for user %s (id=%s, tokens=%d)",
        outline_title,
        current_user.id,
        outline.id,
        metadata.get("tokens_used", 0),
    )

    return responses.created(
        data=GenerateOutlineResponse(
            outline=outline_out,
            metadata=metadata,
            is_script_allowed=True,
        ),
        message="Script outline generated successfully",
    )


# ── Outline CRUD ───────────────────────────────────────────────────────────────


@scripts_router.get("/outlines", response_model=ApiResponse[OutlineListResponse])
async def list_outlines(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[OutlineListResponse]:
    """List the current user's script outlines."""
    result = await db.execute(
        select(ScriptOutline)
        .where(ScriptOutline.user_id == current_user.id)
        .options(
            selectinload(ScriptOutline.outline_tones).selectinload(OutlineTone.tone)
        )
        .order_by(ScriptOutline.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    outlines = result.scalars().all()

    count_result = await db.execute(
        select(ScriptOutline).where(ScriptOutline.user_id == current_user.id)
    )
    total = len(count_result.scalars().all())

    outlines_out = [_outline_to_out(o) for o in outlines]
    return responses.ok(
        data=OutlineListResponse(outlines=outlines_out, total=total),
        message="Outlines retrieved",
    )


@scripts_router.get(
    "/outlines/{outline_id}", response_model=ApiResponse[ScriptOutlineOut]
)
async def get_outline(
    outline_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ScriptOutlineOut]:
    """Get a single script outline by ID."""
    outline = await _get_outline_or_404(db, outline_id, current_user.id)
    return responses.ok(data=_outline_to_out(outline), message="Outline retrieved")


@scripts_router.delete(
    "/outlines/{outline_id}",
    response_model=ApiResponse[None],
)
async def delete_outline(
    outline_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    """Delete a script outline."""
    outline = await _get_outline_or_404(db, outline_id, current_user.id)
    await db.delete(outline)
    await db.commit()
    return responses.no_data(message="Outline deleted")


# ── Script Generation ──────────────────────────────────────────────────────────


@scripts_router.post(
    "/outlines/{outline_id}/script",
    response_model=ApiResponse[GenerateScriptResponse],
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("3/minute")
async def generate_script(
    request: Request,
    outline_id: uuid.UUID,
    body: GenerateScriptRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[GenerateScriptResponse]:
    """Generate a full script from an existing outline."""
    # Load outline with tones
    result = await db.execute(
        select(ScriptOutline)
        .where(
            ScriptOutline.id == outline_id,
            ScriptOutline.user_id == current_user.id,
        )
        .options(
            selectinload(ScriptOutline.outline_tones).selectinload(OutlineTone.tone)
        )
    )
    outline = result.scalar_one_or_none()
    if not outline:
        raise HTTPException(status_code=404, detail="Outline not found")

    tone_names = [ot.tone.name for ot in outline.outline_tones] or ["Informative"]
    template_style_name = outline.outline_data.get("template_style", "medium")
    min_length = outline.outline_data.get("min_length", 1000)
    max_length = outline.outline_data.get("max_length", 5000)

    # Allow override via request body
    if body.template_style_id:
        result = await db.execute(
            select(TemplateStyle).where(TemplateStyle.id == body.template_style_id)
        )
        ts = result.scalar_one_or_none()
        if ts:
            min_length = ts.min_length
            max_length = ts.max_length
            template_style_name = ts.name.lower().replace(" ", "_")

    # Build structured outline JSON for the service
    if outline.outline_data.get("sections"):
        outline_for_script = json.dumps(
            {
                "sections": outline.outline_data.get("sections", []),
                "section_order": outline.outline_data.get("section_order", []),
                "outline_text": outline.outline_text,
            }
        )
    else:
        outline_for_script = outline.outline_text

    # Generate
    try:
        script_response = await openai_service.generate_script(
            outline_text=outline_for_script,
            tones=tone_names,
            template_style=template_style_name,
            min_length=min_length,
            max_length=max_length,
        )
    except Exception as exc:
        logger.error("[SCRIPT] Generation failed for user %s: %s", current_user.id, exc)
        raise HTTPException(
            status_code=500, detail="Script generation failed. Please try again."
        )

    script_content = script_response["full_text"]
    sections = script_response["sections"]
    metadata = script_response["metadata"]

    if not script_content or not script_content.strip():
        raise HTTPException(
            status_code=500, detail="Empty script returned from generation"
        )

    # Clean doc references
    script_content = re.sub(r"■[^■]*?■", "", script_content)
    script_content = re.sub(r"\n\s*\n\s*\n", "\n\n", script_content).strip()

    # Generate title from first 500 chars
    try:
        gen_titles, _ = await openai_service.generate_titles(
            prompt=script_content[:500],
            title_count=1,
            tones=tone_names,
        )
        script_title = gen_titles[0]["title"] if gen_titles else outline.title
    except Exception:
        script_title = outline.title

    total_words = metadata.get("word_count", len(script_content.split()))
    estimated_duration = round(total_words / 140, 2)  # minutes at 140 WPM

    full_script = FullScript(
        user_id=current_user.id,
        outline_id=outline.id,
        title=script_title,
        content=script_content,
        sections=sections,
        word_count=total_words,
        estimated_duration=estimated_duration,
        status="generated",
        openai_model=metadata.get("model", ""),
        tokens_used=metadata.get("tokens_used", 0),
        generation_time=metadata.get("generation_time", 0.0),
    )
    db.add(full_script)

    # Update outline status
    outline.status = "saved"
    await db.commit()
    await db.refresh(full_script)

    logger.info(
        "[SCRIPT] Created script '%s' for user %s (id=%s, words=%d, tokens=%d)",
        script_title,
        current_user.id,
        full_script.id,
        total_words,
        metadata.get("tokens_used", 0),
    )

    return responses.created(
        data=GenerateScriptResponse(
            script=FullScriptOut.model_validate(full_script),
            metadata=metadata,
        ),
        message="Full script generated successfully",
    )


# ── Script CRUD ────────────────────────────────────────────────────────────────


@scripts_router.get("/scripts", response_model=ApiResponse[ScriptListResponse])
async def list_scripts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ScriptListResponse]:
    """List the current user's full scripts."""
    result = await db.execute(
        select(FullScript)
        .where(FullScript.user_id == current_user.id)
        .order_by(FullScript.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    scripts = result.scalars().all()

    count_result = await db.execute(
        select(FullScript).where(FullScript.user_id == current_user.id)
    )
    total = len(count_result.scalars().all())

    return responses.ok(
        data=ScriptListResponse(
            scripts=[FullScriptOut.model_validate(s) for s in scripts],
            total=total,
        ),
        message="Scripts retrieved",
    )


@scripts_router.get("/scripts/{script_id}", response_model=ApiResponse[FullScriptOut])
async def get_script(
    script_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[FullScriptOut]:
    """Get a single full script by ID."""
    script = await _get_script_or_404(db, script_id, current_user.id)
    return responses.ok(
        data=FullScriptOut.model_validate(script), message="Script retrieved"
    )


@scripts_router.delete("/scripts/{script_id}", response_model=ApiResponse[None])
async def delete_script(
    script_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[None]:
    """Delete a full script."""
    script = await _get_script_or_404(db, script_id, current_user.id)
    await db.delete(script)
    await db.commit()
    return responses.no_data(message="Script deleted")


# ── Status updates ─────────────────────────────────────────────────────────────


@scripts_router.patch(
    "/outlines/{outline_id}/status", response_model=ApiResponse[ScriptOutlineOut]
)
async def update_outline_status(
    outline_id: uuid.UUID,
    body: UpdateOutlineStatusRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ScriptOutlineOut]:
    """Update outline status."""
    outline = await _get_outline_or_404(db, outline_id, current_user.id)
    outline.status = body.status
    await db.commit()
    await db.refresh(outline)
    return responses.ok(data=_outline_to_out(outline), message="Status updated")


@scripts_router.patch(
    "/scripts/{script_id}/status", response_model=ApiResponse[FullScriptOut]
)
async def update_script_status(
    script_id: uuid.UUID,
    body: UpdateScriptStatusRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[FullScriptOut]:
    """Update script status."""
    script = await _get_script_or_404(db, script_id, current_user.id)
    script.status = body.status
    await db.commit()
    await db.refresh(script)
    return responses.ok(
        data=FullScriptOut.model_validate(script), message="Status updated"
    )


# ── Internal helpers ───────────────────────────────────────────────────────────


async def _get_outline_or_404(
    db: AsyncSession,
    outline_id: uuid.UUID,
    user_id: int,
) -> ScriptOutline:
    result = await db.execute(
        select(ScriptOutline)
        .where(ScriptOutline.id == outline_id, ScriptOutline.user_id == user_id)
        .options(
            selectinload(ScriptOutline.outline_tones).selectinload(OutlineTone.tone)
        )
    )
    outline = result.scalar_one_or_none()
    if not outline:
        raise HTTPException(status_code=404, detail="Outline not found")
    return outline


async def _get_script_or_404(
    db: AsyncSession,
    script_id: uuid.UUID,
    user_id: int,
) -> FullScript:
    result = await db.execute(
        select(FullScript).where(
            FullScript.id == script_id,
            FullScript.user_id == user_id,
        )
    )
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    return script


def _outline_to_out(outline: ScriptOutline) -> ScriptOutlineOut:
    tones_out = [ToneOut.model_validate(ot.tone) for ot in outline.outline_tones]
    return ScriptOutlineOut(
        id=outline.id,
        title=outline.title,
        outline_text=outline.outline_text,
        outline_data=outline.outline_data,
        section_order=outline.section_order,
        status=outline.status.value,
        openai_model=outline.openai_model,
        tokens_used=outline.tokens_used,
        generation_time=outline.generation_time,
        tones=tones_out,
        created_at=outline.created_at,
        updated_at=outline.updated_at,
    )
