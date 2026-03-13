"""
OpenAI Script Service (async)

Handles title generation, outline generation, and full script generation
using the AsyncOpenAI client. Mirrors the Django open_ai.py logic.
"""

import json
import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple

from openai import AsyncOpenAI

from app.config import settings
from app.services.scripts.niche_context import inject_niche_into_system_prompt
from app.services.scripts.prompt import prompt as storytelling_manual_raw
from app.services.scripts.word_count_strategy import SectionType, WordCountStrategy

logger = logging.getLogger(__name__)

# ── Compliant hook examples injected into prompts ─────────────────────────────

EXAMPLE_COMPLIANT_HOOKS = """
✅ MANDATORY HOOK PATTERNS (COPY THESE):

Tutorial/Listicle Hook:
"Mark's system crashed at 2:17 AM. Zero backups. Launch in 6 hours.
Three questions: How do you recover? What tools actually work? Why do 90% fail?
Today: 7 emergency recovery tactics that saved my career—twice."

Narrative Hook:
"The explosion shattered windows three blocks away.
Sarah had warned them. Nobody listened.
What she discovered in that abandoned server room changed everything we know about system failures."

Explainer Hook:
"Tesla's autopilot made a decision that killed someone. The code responsible? 47 lines.
But here's what's terrifying: Every autonomous system uses similar logic.
Today: The hidden flaw in AI decision-making that affects us all."

❌ INSTANT REJECTION PATTERNS:
"Imagine sitting at your desk when suddenly..." → REJECTED
"In this video, we'll explore..." → REJECTED
"Have you ever wondered why..." → REJECTED
"Let me paint you a picture..." → REJECTED
"Welcome back to the channel..." → REJECTED

VALIDATION: First word must be a NOUN or NAME + ACTION VERB within first 5 words.
HOOK LENGTH: Maximum 30 seconds (~75 words at 2.5 words/second)
"""


# ── Storytelling manual formatter ─────────────────────────────────────────────


def _format_storytelling_manual() -> str:
    manual = []
    manual.append("=== 7 STRATEGIES FOR BETTER OPENINGS ===")
    for item in storytelling_manual_raw[:7]:
        manual.append(f"\n{item['id']}: {item['principle_rule']}")
        manual.append(f"Explanation: {item['explanation']}")
        if "framework_formula" in item:
            manual.append("Framework:")
            for step in item["framework_formula"]:
                manual.append(f"• {step}")
        if "case_study_example" in item:
            manual.append(f"Example: {item['case_study_example']}")

    manual.append("\n\n=== CASE STUDIES ===")
    for item in storytelling_manual_raw[7:9]:
        manual.append(f"\n{item['id']}: {item['principle_rule']}")
        manual.append(f"Explanation: {item['explanation']}")

    manual.append("\n\n=== CORE STORYTELLING PRINCIPLES ===")
    for p in [
        "P01: Transformation (Beginning–Middle–End): Show transformation by contrasting ending with beginning",
        "P02: Worldbuilding with Specific, Sensory Detail: Use concrete, sensory details to make scenes felt",
        "P03: Causality: Link beats with 'therefore,' 'but,' or 'because,' not 'and then'",
        "P04: Rhythm: Vary sentence and word length to control pace and flow",
        "P05: Emotion: Make the audience feel what the character felt",
        "P06: Make the Audience Care Before Big Events: Build attachment before major highs or lows",
        "P07: Simplify: Remove tangents and confusing details",
        "P11: Tension, Conflict, and Stakes: Define goal, obstacle, and consequences",
        "P12: Curiosity: Plant open loops and manage multiple curiosity threads",
        "P15: Show, Don't Tell: Demonstrate traits through actions and concrete images",
        "P17: Write with the Visual in Mind: Every line should suggest footage or graphics",
    ]:
        manual.append(f"• {p}")

    manual.append("\n\n=== IMPLEMENTATION CHECKLIST ===")
    for item in [
        "Transformation arc explicit (A→B)",
        "Causal connectors present between major beats",
        "At least one clear stakes callback",
        "Two vivid sensory details per key scene",
        "Reading level ≈ high school; jargon removed",
        "Chapter ends with a tease or unresolved thread",
        "Visual cues/storyboard notes embedded",
    ]:
        manual.append(f"• {item}")

    return "\n".join(manual)


# ── Lazy async clients ─────────────────────────────────────────────────────────


def _get_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.openai_api_key)


def _get_title_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.title_generation_api_key)


# ── Title Generation ───────────────────────────────────────────────────────────


def _build_title_system_prompt() -> str:
    manual = _format_storytelling_manual()
    return f"""You are a world-class YouTube title creator specializing in high-CTR, viral titles.
OUTPUT: Return ONLY a JSON array of objects with this schema:
{{
  "title": "string",
  "angle": "what makes it click-worthy",
  "tension_pair": ["problem/hook", "solution/payoff"],
  "levers": ["curiosity","shock","emotion","urgency","mystery"],
  "emotion_target": "fear|shock|curiosity|desire|anger|surprise",
  "power_words": ["..."],
  "length_chars": 52,
  "word_count": 6,
  "truncation_safe": true,
  "notes": "why this works"
}}

🚨 CRITICAL LENGTH REQUIREMENTS (NON-NEGOTIABLE):
- MAXIMUM 55 characters (absolute hard limit)
- 5-7 words ONLY (ideal: 6 words)

🎭 HUMAN VOICE REQUIREMENTS (70% EMOTIONAL / 30% INFORMATIONAL):
- Use CONTRACTIONS: "I'm", "you're", "don't", "it's", "can't"
- Sound CONVERSATIONAL: Like talking to a friend
- Embrace slight "messiness": Real speech has rhythm
- AVOID sterile academic tone

✅ GOOD (human, emotional, conversational):
  - "Why My Brain Felt Broken Before This"
  - "Stop Chasing Quick Fixes—Try This Instead"
  - "Your Morning Ritual Is Sabotaging You"

❌ BAD (robotic, formal, sterile):
  - "Strange Truth: Dopamine Cleanses Change Nothing"
  - "The Cognitive Effects of Morning Routines"

❌ FORBIDDEN (AUTO-REJECT):
- "How to..." - BANNED
- "Top 10..." - BANNED
- "A Guide to..." - BANNED
- "In 2025..." - BANNED
- "The Ultimate..." - BANNED
- Any title over 55 characters - REJECTED

{manual}

FINAL REMINDER:
- 55 characters max, 5-7 words
- INTRIGUING, curiosity-driven, DIVERSE
- 70% EMOTIONAL, 30% informational
- Sound like a REAL YouTuber, not a robot
"""


def _build_title_user_prompt(
    prompt: str, title_count: int, tones: Optional[List[str]] = None
) -> str:
    base = f"""Video Concept: "{prompt}"
Generate {title_count} YouTube titles that will get HIGH CLICK-THROUGH RATES.

MANDATORY REQUIREMENTS:
✓ Each title MUST be 55 characters or less
✓ Each title MUST be 5-7 words
✓ Each title MUST be intriguing (create curiosity gap)
✓ Each title MUST sound HUMAN and CONVERSATIONAL
✓ Each title MUST be 70% emotional / 30% informational
✓ NO banned phrases (How to, Guide, Top X, etc.)
✓ NO repeated words/structures within this batch

Return ONLY valid JSON array. Every title MUST pass all checks above.
"""
    if tones:
        base += f"\nTones to incorporate: {', '.join(tones)}"
    return base


def _parse_titles(content: str) -> List[Dict[str, Any]]:
    try:
        cleaned = re.sub(r"^```(?:json)?|```$", "", content.strip(), flags=re.MULTILINE).strip()
        match = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(0)
        data = json.loads(cleaned)
        parsed = []
        for t in data:
            title_text = t.get("title", "")
            length = len(title_text)
            word_count = len(title_text.split())
            t["length_chars"] = length
            t["word_count"] = word_count
            if length > 55 or word_count < 5 or word_count > 7:
                logger.warning("[TITLES] Rejected: '%s' (%d chars, %d words)", title_text, length, word_count)
                continue
            t["truncation_safe"] = True
            parsed.append(t)
        return parsed
    except Exception as exc:
        logger.error("[TITLES] Failed to parse: %s", exc)
        return []


async def generate_titles(
    prompt: str,
    title_count: int = 6,
    tones: Optional[List[str]] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Generate YouTube titles via Chat Completions. Returns (titles, metadata)."""
    start = time.time()
    client = _get_title_client()
    model = settings.title_generation_model

    api_params: Dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": _build_title_system_prompt()},
            {"role": "user", "content": _build_title_user_prompt(prompt, title_count, tones)},
        ],
    }
    if "gpt-4.1" in model.lower() or "gpt-4-turbo" in model.lower():
        api_params["max_tokens"] = 8192
        api_params["temperature"] = 0.7
    elif "gpt-5" in model.lower() or "o1" in model.lower():
        api_params["max_completion_tokens"] = 8192
    else:
        api_params["max_tokens"] = 4096
        api_params["temperature"] = 0.7

    response = await client.chat.completions.create(**api_params)
    content = response.choices[0].message.content or ""
    tokens_used = response.usage.total_tokens if response.usage else 0
    generation_time = time.time() - start

    titles = _parse_titles(content)

    metadata: Dict[str, Any] = {
        "tokens_used": tokens_used,
        "generation_time": round(generation_time, 2),
        "model": model,
        "title_count": len(titles),
        "tones_used": tones or [],
    }
    logger.info("[TITLES] Generated %d titles in %.2fs (%d tokens)", len(titles), generation_time, tokens_used)
    return titles, metadata


# ── Outline Generation ─────────────────────────────────────────────────────────


def _build_outline_system_prompt(niche_context: Optional[Dict[str, Any]] = None) -> str:
    manual = _format_storytelling_manual()
    base = f"""You are an expert YouTube script writer and content strategist.

CRITICAL: Respond with valid JSON only.

S1 HOOK VALIDATORS (MANDATORY):
- Hook ≤30 seconds
- Action verb in first 1-2 sentences
- 3-6 sentence micro-scene
- Pivot to main content within 60s
- FORBIDDEN STARTERS: "Imagine", "Picture", "Let me", "Welcome", "Today we"

S2 OPEN LOOPS VALIDATORS (MANDATORY):
- State 2-3 specific high-value questions in hook
- Include transformation statement: "Learn X to achieve Y"

S6 VALUE DELIVERY VALIDATORS (MANDATORY):
- First value point within 10 seconds of hook end
- Hook ≤30 seconds

JSON SCHEMA:
{{
  "sections": [
    {{
      "title": "Section Title",
      "description": "Detailed 80-150 word description",
      "key_points": ["Specific point 1", "Specific point 2", "Specific point 3"],
      "timing": "Estimated duration",
      "transition": "How to transition to next section",
      "content": "Examples, stories, or techniques to include"
    }}
  ],
  "section_order": [0, 1, 2, 3, 4]
}}

{EXAMPLE_COMPLIANT_HOOKS}

=== VIDEO SCRIPTS STORYTELLING MANUAL ===
{manual}

RESPONSE FORMAT: Return ONLY valid JSON matching the schema above. No markdown, no explanations."""

    return inject_niche_into_system_prompt(base, niche_context or {})


def _build_outline_user_prompt(
    description: str,
    tones: List[str],
    template_style: str,
    min_length: int,
    max_length: int,
    suggested_sections: int,
) -> str:
    tone_text = f"Tones: {', '.join(tones)}" if len(tones) > 1 else f"Tone: {tones[0]}"
    return f"""Generate DETAILED outline in JSON for:

Topic: {description}
{tone_text} | Style: {template_style} | Target: {min_length:,}-{max_length:,}w script
Sections: {suggested_sections}

REQUIREMENTS:
• Each section: 80-150w description + 5-8 detailed key point sentences
• Include specific examples, stories, techniques
• Add timing + transition guidance
• Outline depth = script length (sparse = FAILS, detailed = success)

CRITICAL: Return ONLY valid JSON matching the exact schema provided."""


def _build_structure_system_prompt(
    suggested_sections: int,
    niche_context: Optional[Dict[str, Any]] = None,
) -> str:
    base = f"""You are an expert YouTube script writer. Create a basic outline structure.

CRITICAL: Respond with valid JSON only.

JSON SCHEMA:
{{
  "sections": [
    {{
      "title": "Section Title",
      "description": "Brief 20-30 word description",
      "key_points": ["Point 1", "Point 2", "Point 3"]
    }}
  ]
}}

REQUIREMENTS:
- Create exactly {suggested_sections} sections
- Keep descriptions brief (20-30 words each)
- Focus on logical flow and structure

RESPONSE FORMAT: Return ONLY valid JSON matching the schema above."""
    return inject_niche_into_system_prompt(base, niche_context or {})


def _parse_outline(text: str) -> Dict[str, Any]:
    try:
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        data = json.loads(cleaned.strip())
        sections = data.get("sections", [])
        for s in sections:
            s.setdefault("key_points", [])
            s.setdefault("timing", "")
            s.setdefault("transition", "")
            s.setdefault("content", s.get("description", ""))
        return {
            "sections": sections,
            "section_order": data.get("section_order", list(range(len(sections)))),
        }
    except Exception as exc:
        logger.error("[OUTLINE] Failed to parse outline JSON: %s", exc)
        return {"sections": [], "section_order": []}


async def generate_outline(
    description: str,
    tones: List[str],
    template_style: str,
    min_length: int,
    max_length: int,
    niche_context: Optional[Dict[str, Any]] = None,
) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
    """
    Generate outline using two-step chunked approach.
    Returns (outline_text, outline_data, metadata).
    """
    start = time.time()
    client = _get_client()
    model = settings.openai_model
    model_lower = model.lower()

    wc = WordCountStrategy(template_style)
    suggested_sections = wc.config["suggested_sections"]

    # STEP 1: Generate basic structure
    logger.info("[OUTLINE] Step 1 — basic structure (%d sections)", suggested_sections)
    structure_system = _build_structure_system_prompt(suggested_sections, niche_context)
    structure_user = (
        f"Create basic outline structure for:\n\nTopic: {description}\n"
        f"Tones: {', '.join(tones)} | Style: {template_style} | "
        f"Target: {min_length:,}-{max_length:,} words\n"
        f"Sections: exactly {suggested_sections}\n\n"
        "CRITICAL: Return ONLY valid JSON."
    )

    step1_params: Dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": structure_system},
            {"role": "user", "content": structure_user},
        ],
        "response_format": {"type": "json_object"},
    }
    if "gpt-4.1" in model_lower or "gpt-4-turbo" in model_lower:
        step1_params["max_tokens"] = 6144
        step1_params["temperature"] = 0.7
    elif "gpt-5" in model_lower or "o1" in model_lower:
        step1_params["max_completion_tokens"] = 6144
    else:
        step1_params["max_tokens"] = 4096
        step1_params["temperature"] = 0.7

    r1 = await client.chat.completions.create(**step1_params)
    tokens1 = r1.usage.total_tokens if r1.usage else 0
    structure_text = r1.choices[0].message.content or "{}"

    structure_data = json.loads(structure_text)
    sections = structure_data.get("sections", [])
    if not sections:
        raise ValueError("No sections returned from structure generation")

    # STEP 2: Enhance with full outline system prompt
    logger.info("[OUTLINE] Step 2 — detail enhancement (%d sections)", len(sections))
    outline_system = _build_outline_system_prompt(niche_context)
    outline_user = _build_outline_user_prompt(
        description, tones, template_style, min_length, max_length, len(sections)
    )

    step2_params: Dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": outline_system},
            {"role": "user", "content": outline_user},
        ],
        "response_format": {"type": "json_object"},
    }
    if "gpt-4.1" in model_lower or "gpt-4-turbo" in model_lower:
        step2_params["max_tokens"] = 16384
        step2_params["temperature"] = 0.7
    elif "gpt-5" in model_lower or "o1" in model_lower:
        step2_params["max_completion_tokens"] = 8192
    else:
        step2_params["max_tokens"] = 8192
        step2_params["temperature"] = 0.7

    r2 = await client.chat.completions.create(**step2_params)
    tokens2 = r2.usage.total_tokens if r2.usage else 0
    outline_text_raw = r2.choices[0].message.content or "{}"

    outline_data = _parse_outline(outline_text_raw)
    sections_out = outline_data.get("sections", [])

    # Build readable outline text
    outline_parts = []
    for s in sections_out:
        if s.get("title") and s.get("description"):
            outline_parts.append(f"{s['title']} - {s['description']}")
    outline_text = "\n\n".join(outline_parts)
    # Clean up doc refs
    outline_text = re.sub(r"■[^■]*?■", "", outline_text)
    outline_text = re.sub(r"\n\s*\n\s*\n", "\n\n", outline_text).strip()

    total_tokens = tokens1 + tokens2
    generation_time = time.time() - start

    metadata = {
        "tokens_used": total_tokens,
        "generation_time": round(generation_time, 2),
        "model_used": model,
        "method": "two_step_outline",
        "sections_generated": len(sections_out),
    }
    logger.info(
        "[OUTLINE] Done — %d sections, %d tokens, %.2fs",
        len(sections_out),
        total_tokens,
        generation_time,
    )
    return outline_text, outline_data, metadata


# ── Script Generation ──────────────────────────────────────────────────────────


def _build_single_pass_system_prompt(
    num_sections: int,
    word_targets: Dict[str, Any],
) -> str:
    manual = _format_storytelling_manual()
    return f"""You are an expert YouTube script writer generating a COMPLETE script in ONE response.

🎯 CRITICAL MISSION - WORD COUNT IS MANDATORY:
Generate ALL {num_sections} sections of the script in a single, cohesive response.

⚠️  DURATION & WORD COUNT REQUIREMENTS (STRICTLY ENFORCED):
🎙️ TOTAL DURATION: {int(word_targets['total_target'] / 140)} minutes of spoken English (@ 140 words/minute)
📊 WORD COUNT RANGE: {int(word_targets['total_target'] * 0.95)}-{int(word_targets['total_target'] * 1.05)} words (±5%).
SECTION BREAKDOWN:
- Hook/Intro (Section 1): {word_targets['intro']} words
- Main sections ({word_targets['main_sections_count']} sections): {word_targets['main_sections']} words each
- Conclusion (Last section): {word_targets['conclusion']} words

🚨 Scripts under {int(word_targets['total_target'] * 0.95)} words will be AUTOMATICALLY REJECTED

📏 HOW TO REACH WORD COUNT:
• Add MORE EXAMPLES: For each concept, give 2-3 concrete examples
• Add MORE DIALOGUE: Include what people said, exact quotes, internal thoughts
• Add MORE SENSORY DETAILS: What did it look like? Sound like? Feel like?
• Add MORE EMOTIONAL BEATS: Show reactions, fears, hopes at each turning point
• Add MORE TRANSITIONS: Bridge ideas with "So here's what happened next..."
• SLOW DOWN KEY MOMENTS: Let dramatic moments breathe with detail

🚨 STRUCTURAL LABELS ARE GUIDELINES — NOT OUTPUT TEXT:
Concepts like "Before/Conflict/After", "Open Loops" are FRAMEWORKS only.
Write natural, flowing narrative prose. Never write structural labels in output.

📚 LANGUAGE LEVEL - 6TH-7TH GRADE (MANDATORY):
• ALWAYS use contractions: it's, don't, can't, they're, wasn't, couldn't, didn't
• FORBIDDEN: therefore, however, consequently, thus, nevertheless, phenomenon, essentially
• USE INSTEAD: so, but, because, that's why, then, this means, here's the thing

🔥 CONVERSATIONAL TONE:
• Write like TALKING to a friend over coffee
• Use short punchy sentences mixed with natural flow
• Show EMOTION first, facts second

🎯 HOOK SECTION (First Section - CRITICAL):
• Line 1: Start with ACTION VERB
• Hook IMMEDIATELY with emotion or mystery
• Create 2-3 unanswered questions in first 30 seconds
• FORBIDDEN: "Imagine", "Picture", "Let me", "Have you ever"

📖 MAIN CONTENT SECTIONS:
• END every section (except last) with curiosity hook - MANDATORY
• Plant 2-3 open loops per section

🎬 CONCLUSION SECTION (Last Section):
• End with emotional reflection or haunting question
• NO clichés: "stay curious", "stay brave", "thanks for watching"

{manual}

📋 JSON RESPONSE FORMAT (MANDATORY):
{{
  "sections": [
    {{
      "title": "Section Title",
      "content": "Full script content...",
      "section_type": "hook_intro|main_content|conclusion"
    }}
  ]
}}

⚠️  Do NOT include "word_count" field — we count actual words from content.

REMEMBER: Generate the COMPLETE script in ONE response. Make it conversational, engaging, easy to understand!"""


def _build_single_pass_user_prompt(
    sections: List[Dict[str, Any]],
    word_targets: Dict[str, Any],
    wc_strategy: WordCountStrategy,
) -> str:
    parts = ["Generate a COMPLETE YouTube script based on this detailed outline:\n"]
    for i, section in enumerate(sections):
        stype = wc_strategy._determine_section_type(i, len(sections))
        if stype == SectionType.HOOK_INTRO:
            target = word_targets["intro"]
        elif stype == SectionType.CONCLUSION:
            target = word_targets["conclusion"]
        else:
            target = word_targets["main_sections"]

        duration_m = target / 140
        duration_str = f"{int(duration_m)}:{int((duration_m % 1) * 60):02d}" if duration_m >= 1 else f"{int(duration_m * 60)}s"
        min_words = int(target * 0.95)
        max_words = int(target * 1.05)

        parts.append(f"\n{'='*60}")
        parts.append(f"SECTION {i+1}: {section.get('title', f'Section {i+1}')}")
        parts.append(f"🎙️ DURATION: {duration_str} of spoken English")
        parts.append(f"📊 WORD COUNT RANGE: {min_words}-{max_words} words (±5%)")
        parts.append(f"\nDescription: {section.get('description', '')}")
        key_points = section.get("key_points", [])
        if key_points:
            parts.append("\nKey Points to Cover:")
            for point in key_points:
                parts.append(f"• {point}")

    total_m = word_targets["total_target"] / 140
    total_str = f"{int(total_m)} min {int((total_m % 1) * 60)} sec"
    parts.append(f"\n{'='*60}")
    parts.append(f"TOTAL: {len(sections)} sections | {total_str} | {word_targets['total_target']} words")
    parts.append("Return valid JSON matching the schema in system prompt.")
    return "\n".join(parts)


async def _expand_sections(
    current_sections: List[Dict[str, Any]],
    original_sections: List[Dict[str, Any]],
    word_targets: Dict[str, Any],
    client: AsyncOpenAI,
    model: str,
) -> Tuple[List[Dict[str, Any]], int]:
    """Expand short sections in parallel API calls."""
    import asyncio

    total_tokens = 0

    async def expand_one(
        index: int,
        section: Dict[str, Any],
        original: Dict[str, Any],
    ) -> Tuple[int, Dict[str, Any], int]:
        if index == 0:
            target = word_targets.get("intro", 0)
        elif index == len(current_sections) - 1:
            target = word_targets.get("conclusion", 0)
        else:
            target = word_targets.get("main_sections", 0)

        current_words = section.get("word_count", 0)
        if target - current_words <= 0:
            return index, section, 0

        shortfall = target - current_words
        shortfall_min = int(shortfall / 140)
        shortfall_sec = int((shortfall / 140 % 1) * 60)

        system = f"""You are an expert YouTube script writer expanding a section.

TASK: Add {shortfall} words to this script section.
CURRENT: {current_words} words → TARGET: {target} words
EXPANSION DURATION: +{shortfall_min}:{shortfall_sec:02d} min of spoken English

EXPANSION TECHNIQUES:
• Add concrete examples and case studies
• Include dialogue, exact quotes, internal thoughts
• Add sensory details (look, sound, feel, smell)
• Add emotional beats and reactions
• Slow down key moments with vivid detail

LANGUAGE REQUIREMENTS:
• 6th-7th grade level
• Contractions throughout (it's, don't, can't)
• Conversational tone (talking to a friend)
• NO forbidden words (therefore, however, consequently)

JSON RESPONSE FORMAT:
{{"content": "Your EXPANDED script content here..."}}"""

        user = f"""Expand this section to reach {target} words (currently {current_words} words):

SECTION: {section.get('title', 'Untitled')}
ORIGINAL OUTLINE: {original.get('description', '')}

CURRENT CONTENT:
{section.get('content', '')}

Add {shortfall} words while maintaining the same conversational tone and narrative flow.
Return ONLY valid JSON: {{"content": "expanded content here"}}"""

        model_lower = model.lower()
        params: Dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 1.0,
        }
        if "gpt-4.1" in model_lower or "gpt-4-turbo" in model_lower:
            params["max_tokens"] = 16384
        elif "gpt-5" in model_lower or "o1" in model_lower:
            params["max_completion_tokens"] = 8192
        else:
            params["max_tokens"] = 8192

        try:
            resp = await client.chat.completions.create(**params)
            tokens = resp.usage.total_tokens if resp.usage else 0
            content = resp.choices[0].message.content or "{}"
            result = json.loads(content)
            expanded_content = result.get("content", section.get("content", ""))
            expanded_section = {**section, "content": expanded_content}
            return index, expanded_section, tokens
        except Exception as exc:
            logger.warning("[EXPAND] Section %d expansion failed: %s", index + 1, exc)
            return index, section, 0

    tasks = [
        expand_one(i, current_sections[i], original_sections[i] if i < len(original_sections) else {})
        for i in range(len(current_sections))
    ]
    results = await asyncio.gather(*tasks)
    expanded = list(current_sections)
    for idx, expanded_section, tokens in results:
        expanded[idx] = expanded_section
        total_tokens += tokens
    return expanded, total_tokens


async def generate_script(
    outline_text: str,
    tones: List[str],
    template_style: str,
    min_length: int,
    max_length: int,
) -> Dict[str, Any]:
    """
    Generate full script using iterative approach (single pass + parallel expansion).
    Returns {"full_text": str, "sections": list, "metadata": dict}.
    """
    start = time.time()
    client = _get_client()
    model = settings.openai_model
    model_lower = model.lower()

    wc = WordCountStrategy(template_style)

    # Parse outline
    outline_data = _parse_outline(outline_text)
    sections = outline_data.get("sections", [])
    if not sections:
        # Fallback: try JSON parse of outline_text directly
        try:
            raw = json.loads(outline_text)
            sections = raw.get("sections", [])
        except Exception:
            pass

    if not sections:
        raise ValueError("No sections found in outline")

    num_sections = len(sections)
    word_targets = wc.calculate_section_word_targets(num_sections)
    total_target = word_targets["total_target"]
    min_acceptable = int(total_target * 0.90)

    logger.info(
        "[SCRIPT] Generating %d sections, target=%d words (%d-%d)",
        num_sections,
        total_target,
        min_length,
        max_length,
    )

    # STEP 1: Single-pass generation of all sections together
    system_prompt = _build_single_pass_system_prompt(num_sections, word_targets)
    user_prompt = _build_single_pass_user_prompt(sections, word_targets, wc)

    api_params: Dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 1.0,
    }
    if "gpt-4.1" in model_lower or "gpt-4-turbo" in model_lower:
        api_params["max_tokens"] = 32768
    elif "gpt-5" in model_lower or "o1" in model_lower:
        api_params["max_completion_tokens"] = 16384
    else:
        api_params["max_tokens"] = 16384

    response = await client.chat.completions.create(**api_params)
    total_tokens = response.usage.total_tokens if response.usage else 0
    content = response.choices[0].message.content or "{}"

    result = json.loads(content)
    current_sections: List[Dict[str, Any]] = result.get("sections", [])
    if not current_sections:
        raise ValueError("No sections returned from initial generation")

    # Add word counts
    for s in current_sections:
        s["word_count"] = len(s.get("content", "").split())

    current_word_count = sum(s["word_count"] for s in current_sections)
    logger.info("[SCRIPT] Initial pass: %d words (%d%% of target)", current_word_count, int(current_word_count / total_target * 100))

    # STEP 2: Iterative parallel expansion (up to 2 iterations)
    for iteration in range(2):
        current_word_count = sum(s["word_count"] for s in current_sections)
        if current_word_count >= min_acceptable:
            logger.info("[SCRIPT] Word count acceptable (%d words), no expansion needed", current_word_count)
            break
        logger.info(
            "[SCRIPT] Expansion iteration %d: %d words < %d min, expanding...",
            iteration + 1,
            current_word_count,
            min_acceptable,
        )
        current_sections, expansion_tokens = await _expand_sections(
            current_sections, sections, word_targets, client, model
        )
        total_tokens += expansion_tokens
        for s in current_sections:
            s["word_count"] = len(s.get("content", "").split())
        new_count = sum(s["word_count"] for s in current_sections)
        logger.info("[SCRIPT] After expansion %d: %d words", iteration + 1, new_count)
        if new_count >= min_acceptable:
            break

    # Add timing
    current_sections = wc.calculate_timing_for_sections(current_sections)

    # Build full script text
    script_parts = []
    for s in current_sections:
        title = s.get("title", "Untitled").upper()
        script_parts.append(f"=== {title} ===")
        script_parts.append(s.get("content", ""))
        script_parts.append("")
    full_script = "\n".join(script_parts).strip()
    # Clean doc refs
    full_script = re.sub(r"■[^■]*?■", "", full_script)
    full_script = re.sub(r"\n\s*\n\s*\n", "\n\n", full_script).strip()

    total_words = sum(s["word_count"] for s in current_sections)
    generation_time = time.time() - start

    metadata = {
        "tokens_used": total_tokens,
        "generation_time": round(generation_time, 2),
        "model": model,
        "word_count": total_words,
        "length_valid": min_length <= total_words <= int(max_length * 1.1),
        "sections_generated": len(current_sections),
        "template_style": template_style,
        "strategy_used": "iterative_parallel",
    }
    logger.info(
        "[SCRIPT] Done — %d words, %d tokens, %.2fs",
        total_words,
        total_tokens,
        generation_time,
    )
    return {
        "full_text": full_script,
        "sections": current_sections,
        "metadata": metadata,
    }
