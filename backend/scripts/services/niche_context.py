"""
Niche Context Builder for AI Prompt Injection

This module handles the injection of niche-specific context into AI prompts
while preserving the core TubeGenius storytelling logic.

Architecture:
- BasePrompt = TubeGenius storytelling manual + core logic
- NicheLayer = Tone + Pacing + Structure + Channel references  
- FinalPrompt = BasePrompt + NicheLayer

Result: AI writes with TubeGenius structure but niche-specific style
"""

from typing import Dict, Any, Optional
import logging

from admins.models import Niche

logger = logging.getLogger(__name__)


class NicheContextBuilder:
    """Builds niche-specific context for AI prompt injection"""

    @staticmethod
    def build_niche_context(niche_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Retrieve niche and build context dictionary for prompt injection.

        Returns dict with:
        - tone_guidance: Instructions for tone matching
        - pacing_guidance: Instructions for pacing matching
        - structure_guidance: Script structure preferences
        - reference_channels: Example channels for style reference
        """
        if not niche_id:
            return {}

        try:
            niche = Niche.objects.get(id=niche_id, status="active")
            logger.info(f"Building niche context for niche: {niche.title} (ID: {niche_id})")
        except Niche.DoesNotExist:
            logger.warning(f"Niche with ID {niche_id} not found or inactive")
            return {}

        context = {
            "niche_name": niche.title,
            "niche_tagline": niche.tagline,
            "tone_guidance": NicheContextBuilder._build_tone_guidance(niche),
            "pacing_guidance": NicheContextBuilder._build_pacing_guidance(niche),
            "structure_guidance": NicheContextBuilder._build_structure_guidance(niche),
            "reference_channels": NicheContextBuilder._build_channel_references(niche),
        }

        return context

    @staticmethod
    def _build_tone_guidance(niche) -> str:
        """Build tone matching instructions from niche"""
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

    @staticmethod
    def _build_pacing_guidance(niche) -> str:
        """Build pacing instructions from niche"""
        if not niche.pacing:
            return ""

        pacing_list = ", ".join(niche.pacing)
        return f"""
PACING REQUIREMENTS:
Maintain a {pacing_list} pace throughout the script:
- Sentence length should reflect this pacing
- Transition speed between ideas
- Overall rhythm of the content
"""

    @staticmethod
    def _build_structure_guidance(niche) -> str:
        """Build structure preferences from niche"""
        if not niche.script_structure:
            return ""

        structure = niche.script_structure
        guidance = "SCRIPT STRUCTURE PREFERENCES:\n"

        if structure.get("intro"):
            guidance += f"- Intro Style: {structure['intro']}\n"
        if structure.get("body"):
            guidance += f"- Body Format: {structure['body']}\n"
        if structure.get("conclusion"):
            guidance += f"- Conclusion Approach: {structure['conclusion']}\n"

        return guidance

    @staticmethod
    def _build_channel_references(niche) -> str:
        """Build channel reference context"""
        if not niche.top_channels:
            return ""

        channels = "\n".join([f"- {ch['name']}" for ch in niche.top_channels])
        return f"""
REFERENCE CHANNELS (Study their style):
{channels}

Analyze the phrasing patterns, rhythm, and voice of these channels.
Match their word choice and sentence structure in your script.
"""

    @staticmethod
    def inject_niche_into_system_prompt(base_prompt: str, niche_context: Dict[str, Any]) -> str:
        """
        Merge base system prompt with niche context.

        This ensures:
        - Base logic from TubeGenius storytelling stays intact
        - Tone, pacing, and voice shift to match niche
        - Only word choice, rhythm, and emotional tone are adapted
        """
        if not niche_context or niche_context.get("niche_name") is None:
            return base_prompt

        niche_name = niche_context.get("niche_name", "selected niche")

        # Build niche style layer
        niche_layer = f"""
=== NICHE STYLE CONTEXT ===
You are now writing in the style of: {niche_name}
Tagline: {niche_context.get('niche_tagline', 'N/A')}

CONTEXT INJECTION INSTRUCTIONS:
While maintaining TubeGenius storytelling principles (structure, chapters, pacing rules),
ADAPT the following to match this niche's style:
- Word choice and phrasing
- Sentence rhythm and emotional tone
- Overall voice and delivery

{niche_context.get('tone_guidance', '')}
{niche_context.get('pacing_guidance', '')}
{niche_context.get('structure_guidance', '')}
{niche_context.get('reference_channels', '')}

KEY RULE: Structure = TubeGenius logic | Style = {niche_name} style

When generating the script:
- Keep the TubeGenius structure (hooks, chapters, transitions, etc.)
- But adapt the WORDING, PHRASING, and TONE to match {niche_name}
- This creates a "channel clone" effect while maintaining proven storytelling
"""
        return f"{base_prompt}\n\n{niche_layer}"

