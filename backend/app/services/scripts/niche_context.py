"""
Niche Context Builder for AI Prompt Injection (async SQLAlchemy)

Injects niche-specific tone/pacing/structure/channel context into AI prompts
while preserving core Video Scripts storytelling logic.
"""

import logging
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.niche import Niche, NicheStatus

logger = logging.getLogger(__name__)


async def build_niche_context(
    db: AsyncSession, niche_id: Optional[int]
) -> Dict[str, Any]:
    """
    Fetch niche from DB and build context dict for prompt injection.
    Returns {} if niche_id is None or niche not found.
    """
    if not niche_id:
        return {}

    result = await db.execute(
        select(Niche).where(
            Niche.id == niche_id,
            Niche.status == NicheStatus.active,
        )
    )
    niche = result.scalar_one_or_none()
    if not niche:
        logger.warning("[NICHE_CONTEXT] Niche %d not found or inactive", niche_id)
        return {}

    context: Dict[str, Any] = {
        "niche_name": niche.title,
        "niche_tagline": niche.tagline or "",
        "tone_guidance": _build_tone_guidance(niche),
        "pacing_guidance": _build_pacing_guidance(niche),
        "structure_guidance": _build_structure_guidance(niche),
        "reference_channels": _build_channel_references(niche),
    }
    logger.info("[NICHE_CONTEXT] Built context for niche: %s", niche.title)
    return context


def _build_tone_guidance(niche: Niche) -> str:
    if not niche.tone:
        return ""
    tones = ", ".join(niche.tone)
    return f"""
TONE REQUIREMENTS (CRITICAL - Must Match):
The script MUST use the tone style of: {tones}
- Word choice should reflect this tone
- Sentence rhythm and cadence should match this tone
- Emotional delivery should align with this tone
"""


def _build_pacing_guidance(niche: Niche) -> str:
    if not niche.pacing:
        return ""
    pacing = ", ".join(niche.pacing)
    return f"""
PACING REQUIREMENTS:
Maintain a {pacing} pace throughout the script:
- Sentence length should reflect this pacing
- Transition speed between ideas
- Overall rhythm of the content
"""


def _build_structure_guidance(niche: Niche) -> str:
    structure = niche.script_structure
    if not structure:
        return ""
    guidance = "SCRIPT STRUCTURE PREFERENCES:\n"
    if structure.get("intro"):
        guidance += f"- Intro Style: {structure['intro']}\n"
    if structure.get("body"):
        guidance += f"- Body Format: {structure['body']}\n"
    if structure.get("conclusion"):
        guidance += f"- Conclusion Approach: {structure['conclusion']}\n"
    return guidance


def _build_channel_references(niche: Niche) -> str:
    channels = niche.top_channels
    if not channels:
        return ""
    # top_channels may be a plain string (Text column) or a list/JSON
    if isinstance(channels, str):
        channel_list = channels.strip()
    elif isinstance(channels, list):
        channel_list = "\n".join(
            f"- {ch['name']}" if isinstance(ch, dict) else f"- {ch}"
            for ch in channels
        )
    else:
        return ""
    return f"""
REFERENCE CHANNELS (Study their style):
{channel_list}

Analyze the phrasing patterns, rhythm, and voice of these channels.
Match their word choice and sentence structure in your script.
"""


def inject_niche_into_system_prompt(
    base_prompt: str, niche_context: Dict[str, Any]
) -> str:
    """Merge base system prompt with niche context layer."""
    if not niche_context or not niche_context.get("niche_name"):
        return base_prompt

    niche_name = niche_context["niche_name"]
    niche_layer = f"""
=== NICHE STYLE CONTEXT ===
You are now writing in the style of: {niche_name}
Tagline: {niche_context.get('niche_tagline', 'N/A')}

CONTEXT INJECTION INSTRUCTIONS:
While maintaining Video Scripts storytelling principles (structure, chapters, pacing rules),
ADAPT the following to match this niche's style:
- Word choice and phrasing
- Sentence rhythm and emotional tone
- Overall voice and delivery

{niche_context.get('tone_guidance', '')}
{niche_context.get('pacing_guidance', '')}
{niche_context.get('structure_guidance', '')}
{niche_context.get('reference_channels', '')}

KEY RULE: Structure = Video Scripts logic | Style = {niche_name} style

When generating the script:
- Keep the Video Scripts structure (hooks, chapters, transitions, etc.)
- But adapt the WORDING, PHRASING, and TONE to match {niche_name}
- This creates a "channel clone" effect while maintaining proven storytelling
"""
    return f"{base_prompt}\n\n{niche_layer}"
