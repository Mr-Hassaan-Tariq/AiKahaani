# services/openai_service.py
import logging
import time
from typing import Any, Dict, Tuple

import openai
from django.conf import settings

logger = logging.getLogger(__name__)

# Lazy client initialization to avoid import-time errors in tests
_client = None


def get_openai_client():
    """Get OpenAI client, initializing it lazily"""
    global _client
    if _client is None:
        _client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


class OpenAIScriptService:
    """
    Service for generating script outlines and full scripts using OpenAI
    """

    @staticmethod
    def generate_outline(script_data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a script outline based on script parameters
        """
        start_time = time.time()
        prompt = OpenAIScriptService._build_outline_prompt(script_data)
        try:
            client = get_openai_client()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert YouTube script writer. Create engaging, well-structured script outlines.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1500,
                temperature=0.7,
            )

            generation_time = time.time() - start_time
            outline_text = response.choices[0].message.content

            # Parse the outline into structured data
            outline_data = OpenAIScriptService._parse_outline_structure(outline_text)

            metadata = {
                "tokens_used": response.usage.total_tokens,
                "generation_time": generation_time,
                "model": "gpt-4",
            }

            return outline_text, outline_data, metadata

        except Exception as e:
            logger.error(f"OpenAI outline generation failed: {str(e)}")
            raise

    @staticmethod
    def generate_full_script(
        outline_text: str, script_data: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate full script from outline
        """
        start_time = time.time()

        prompt = OpenAIScriptService._build_script_prompt(outline_text, script_data)

        try:
            client = get_openai_client()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert YouTube script writer. Create engaging, detailed scripts with natural flow and clear structure.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=3000,
                temperature=0.8,
            )

            generation_time = time.time() - start_time
            script_content = response.choices[0].message.content

            # Parse script into sections
            sections = OpenAIScriptService._parse_script_sections(script_content)

            metadata = {
                "tokens_used": response.usage.total_tokens,
                "generation_time": generation_time,
                "model": "gpt-4",
            }

            return script_content, sections, metadata

        except Exception as e:
            logger.error(f"OpenAI script generation failed: {str(e)}")
            raise

    @staticmethod
    def _build_outline_prompt(script_data: Dict[str, Any]) -> str:
        """Build prompt for outline generation"""
        tone = script_data.get("tone", "informative")
        template_style = script_data.get("template_style", "medium")
        description = script_data.get("description", "")
        min_length = script_data.get("min_length", 100)
        max_length = script_data.get("max_length", 1000)

        return f"""
Create a detailed script outline for a YouTube video with the following requirements:

Topic: {description}
Tone: {tone}
Style: {template_style}
Target Length: {min_length}-{max_length} words

Please structure the outline with:
1. Hook/Opening (attention-grabbing start)
2. Introduction (brief topic overview)
3. Main Content (3-5 key points with subpoints)
4. Call to Action (engagement request)
5. Closing (memorable ending)

For each section, provide:
- Brief description of what to cover
- Key talking points
- Estimated timing
- Transition notes

Make it engaging and suitable for the {tone} tone. Ensure the final script will be between {min_length} and {max_length} words.
"""

    @staticmethod
    def _build_script_prompt(outline_text: str, script_data: Dict[str, Any]) -> str:
        """Build prompt for full script generation"""
        tone = script_data.get("tone", "informative")
        min_length = script_data.get("min_length", 1000)
        max_length = script_data.get("max_length", 5000)

        return f"""
Based on the following outline, write a complete, detailed YouTube script:

OUTLINE:
{outline_text}

REQUIREMENTS:
- Tone: {tone}
- Target Length: {min_length}-{max_length} words
- Write in a conversational, engaging style
- Include natural transitions between sections
- Add specific examples and details
- Write exactly what the speaker should say
- Include [PAUSE], [VISUAL], or [EMPHASIS] cues where helpful
- Make it flow naturally when spoken aloud
- Ensure the final script is between {min_length} and {max_length} words

Write the complete script with natural dialogue and engaging content.
"""

    @staticmethod
    def _parse_outline_structure(outline_text: str) -> Dict[str, Any]:
        """Parse outline text into structured data"""
        sections = []
        current_section = None

        lines = outline_text.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect main section headers (numbered sections like "1. Hook/Opening")
            if line and line[0].isdigit() and "." in line and not line.startswith("-"):
                # Save previous section if exists
                if current_section:
                    sections.append(current_section)

                # Start new main section
                current_section = {
                    "title": line,
                    "description": "",
                    "key_points": [],
                    "timing": "",
                    "transition": "",
                }

            # Handle sub-points under current section
            elif current_section and line.startswith("-"):
                # Remove the dash and clean up
                content = line[1:].strip()

                if content.startswith("Description:"):
                    current_section["description"] = content.replace(
                        "Description:", ""
                    ).strip()
                elif content.startswith("Key talking points:"):
                    current_section["key_points"].append(
                        content.replace("Key talking points:", "").strip()
                    )
                elif content.startswith("Estimated timing:"):
                    current_section["timing"] = content.replace(
                        "Estimated timing:", ""
                    ).strip()
                elif content.startswith("Transition notes:"):
                    current_section["transition"] = content.replace(
                        "Transition notes:", ""
                    ).strip()
                else:
                    # Generic sub-point
                    current_section["key_points"].append(content)

            # Handle nested sub-sections (like "Key Point 1: Origin Story")
            elif current_section and line.startswith("-") and ":" in line:
                content = line[1:].strip()
                current_section["key_points"].append(content)

        # Add the last section
        if current_section:
            sections.append(current_section)

        return {"sections": sections}

    @staticmethod
    def generate_titles(
        prompt: str, title_count: int = 10, tones: list = None
    ) -> Tuple[list, Dict[str, Any]]:
        """
        Generate YouTube titles based on TubeGenius Title Wizardry principles

        Args:
            prompt: Description or context for the video title generation
            title_count: Number of title variations to generate (default: 10)
            tones: List of tones/styles to apply (max 3, optional)

        Returns:
            Tuple of (list of titles, metadata dict)
        """
        start_time = time.time()

        try:
            client = get_openai_client()

            system_prompt = OpenAIScriptService._build_title_system_prompt()
            user_prompt = OpenAIScriptService._build_title_user_prompt(
                prompt, title_count, tones
            )

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=2000,
                temperature=0.8,
            )

            generation_time = time.time() - start_time
            titles_content = response.choices[0].message.content

            # Parse titles from response
            titles = OpenAIScriptService._parse_generated_titles(titles_content)

            metadata = {
                "tokens_used": response.usage.total_tokens,
                "generation_time": generation_time,
                "model": "gpt-4",
                "title_count": len(titles),
            }

            # Add tones to metadata if provided
            if tones and len(tones) > 0:
                metadata["tones_used"] = tones

            return titles, metadata

        except Exception as e:
            logger.error(f"OpenAI title generation failed: {str(e)}")
            raise

    @staticmethod
    def _build_title_system_prompt() -> str:
        """Build system prompt for title generation based on TubeGenius principles"""
        return """You are an expert YouTube title writer trained on TubeGenius Title Wizardry principles. Your goal is to create titles that maximize clicks while staying truthful to the content.

KEY PRINCIPLES:
1. Create urgency with "I need to click this now" reaction
2. Keep titles ≤54 characters when possible
3. Use proven formats that work
4. Make content accessible to wider audiences
5. Leverage curiosity gaps and open loops
6. Sell the end result, not the process
7. Challenge assumptions with contrarian angles
8. Use strong POV and superlatives
9. Trigger emotions (fear, anger, desire, joy)
10. Add secrets, FOMO, and urgency appropriately

POWER WORDS TO USE:
- Emotion: SHOCKING, INSANE, DISTURBING, HORRIFYING, AMAZING, INCREDIBLE
- Urgency: URGENT, BREAKING, WARNING, NEVER, MUST, NEED
- Secrets: SECRET, REAL REASON, TRUTH, HIDDEN, WHAT NO ONE TELLS YOU
- Results: CHANGED MY LIFE, 10X, ESCAPE, ACHIEVE, GET RICH, DOMINATE

PROVEN FORMATS:
- "The Truth About X"
- "X Changed My Life"
- "The Rise & Fall of X"
- "You're Wrong About X"
- "I Stopped X—Here's What Happened"
- "How X Really Works"
- "Why You NEED X"
- "NEVER Do X"
- "The Most [Adjective] X"
- "How X Makes Money"
- "The Secret X That Owns Everything"

Generate titles that combine multiple strategies intelligently without being overly complex."""

    @staticmethod
    def _build_title_user_prompt(
        prompt: str, title_count: int, tones: list = None
    ) -> str:
        """Build user prompt for title generation"""
        base_prompt = f"""Based on this video concept/topic: "{prompt}"

Generate {title_count} high-converting YouTube titles following TubeGenius principles:

REQUIREMENTS:
- Each title should be ≤54 characters when possible
- Use different strategic combinations (emotion + curiosity, fame jacking + urgency, etc.)
- Include variety: some contrarian, some outcome-focused, some secret-revealing
- Apply appropriate capitalization and power words
- Ensure each title creates curiosity without revealing the answer
- Make titles accessible to broad audiences
- Each title should trigger an emotional response
- Vary the formats but keep all titles compelling"""

        # Add tone-specific instructions if tones are provided
        if tones and len(tones) > 0:
            tone_instruction = f"""

TONE/STYLE REQUIREMENTS:
Focus on incorporating these specific tones/styles: {', '.join(tones)}
- Distribute the {title_count} titles across these tones
- Adapt the power words and formats to match each tone
- Ensure each tone's personality comes through clearly"""

            # Add tone-specific guidance
            tone_guidance = {
                "Controversial": "- Challenge popular opinions, use contrarian statements, create debate",
                "Shocking": "- Use extreme statements, surprising facts, jaw-dropping revelations",
                "Persuasive": '- Focus on benefits, use "you need this" language, compelling reasons',
                "Mysterious": "- Create intrigue, use secrets and hidden knowledge, unexplained phenomena",
                "Dramatic": "- Use intense language, high-stakes scenarios, emotional peaks",
                "Question-based": "- Pose compelling questions, use interrogative formats, create curiosity gaps",
                "Sarcastic": "- Use irony and wit, playful mockery, clever wordplay",
                "Witty": "- Use humor and cleverness, wordplay, smart observations",
                "Neutral": "- Use factual approach, informative tone, straightforward language",
            }

            specific_guidance = []
            for tone in tones:
                if tone in tone_guidance:
                    specific_guidance.append(f"{tone}: {tone_guidance[tone]}")

            if specific_guidance:
                tone_instruction += "\n\nTONE-SPECIFIC GUIDANCE:\n" + "\n".join(
                    specific_guidance
                )

            base_prompt += tone_instruction

        base_prompt += """

Format your response as a numbered list:
1. [Title]
2. [Title]
...

Focus on creating titles that would make someone stop scrolling and click immediately."""

        return base_prompt

    @staticmethod
    def _parse_generated_titles(titles_content: str) -> list:
        """Parse generated titles from OpenAI response"""
        titles = []
        lines = titles_content.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Remove numbering (1., 2., etc.) and clean up
            if line and (line[0].isdigit() or line.startswith("-")):
                # Find the title after the number/bullet
                if "." in line:
                    title = line.split(".", 1)[1].strip()
                elif line.startswith("-"):
                    title = line[1:].strip()
                else:
                    title = line

                # Remove quotes if present
                title = title.strip("\"'")

                if title and len(title) > 5:  # Basic validation
                    titles.append(title)
            elif len(line) > 5:  # Handle titles without numbering
                titles.append(line.strip("\"'"))

        return titles

    @staticmethod
    def generate_optimized_titles(
        script=None, user_title=None, user_prompt=None, title_count=5, tones=None
    ) -> Tuple[list, Dict[str, Any]]:
        """
        Generate optimized YouTube titles from script content or user-provided title

        Args:
            script: Script object with content to optimize (optional)
            user_title: User-provided title to optimize (optional)
            user_prompt: User instructions for optimization
            title_count: Number of title variations to generate (default: 5)
            tones: List of tones/styles to apply (optional)

        Returns:
            Tuple of (list of titles, metadata dict)
        """
        if script:
            # Script-based optimization
            script_content = script.content or script.description
            script_title = script.title or "Untitled Script"

            optimization_prompt = f"""
Optimize YouTube titles for the following script:

Script Title: {script_title}
Script Content: {script_content[:1000]}{'...' if len(script_content) > 1000 else ''}

User Instructions: {user_prompt}

Generate engaging, clickable YouTube titles that capture the essence of this script content while following the user's specific optimization instructions.
"""
        else:
            # Title-based optimization
            optimization_prompt = f"""
Optimize the following YouTube title:

Original Title: {user_title}

User Instructions: {user_prompt}

Generate improved, more engaging YouTube title variations that maintain the original intent while following the user's optimization instructions.
"""

        # Use the existing generate_titles method with the optimization prompt
        return OpenAIScriptService.generate_titles(
            prompt=optimization_prompt, title_count=title_count, tones=tones
        )

    @staticmethod
    def _parse_script_sections(script_content: str) -> list:
        """Parse script content into sections"""
        sections = []
        current_section = {"title": "Opening", "content": ""}

        for line in script_content.split("\n"):
            if line.strip().upper() in [
                "HOOK:",
                "INTRODUCTION:",
                "MAIN CONTENT:",
                "CONCLUSION:",
                "CALL TO ACTION:",
            ]:
                if current_section["content"].strip():
                    sections.append(current_section)
                current_section = {"title": line.strip(), "content": ""}
            else:
                current_section["content"] += line + "\n"

        if current_section["content"].strip():
            sections.append(current_section)

        return sections
