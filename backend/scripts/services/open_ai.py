# services/openai_service.py
import base64
import json
import logging
import re
import time
from typing import Any, Dict, List, Tuple

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
    def analyze_image(image_file=None, image_url=None) -> Tuple[str, str]:
        """
        Analyze an image using OpenAI Vision model to generate title and description

        Args:
            image_file: Django UploadedFile object (optional)
            image_url: URL of the image to analyze (optional)

        Returns:
            Tuple of (title, description)
        """
        try:
            # Determine the image URL for OpenAI
            if image_file:
                # Convert uploaded file to base64
                image_content = image_file.read()
                # Reset file pointer for potential future use
                image_file.seek(0)
                # Convert to base64
                base64_image = base64.b64encode(image_content).decode("utf-8")
                image_url_for_openai = f"data:image/jpeg;base64,{base64_image}"
            elif image_url:
                # Use the provided URL directly
                image_url_for_openai = image_url
            else:
                raise ValueError("Either image_file or image_url must be provided")

            client = get_openai_client()
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this image and provide:
1. A catchy, engaging YouTube video title (under 60 characters)
2. A detailed description of what's happening in the image that could be used for script generation

Format your response as:
TITLE: [your title here]
DESCRIPTION: [your description here]

Make the title clickable and engaging for YouTube, and the description detailed enough to generate a good script outline.""",
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url_for_openai},
                            },
                        ],
                    }
                ],
                max_tokens=500,
                temperature=0.7,
            )

            content = response.choices[0].message.content

            # Parse the response to extract title and description
            title = ""
            description = ""

            lines = content.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("TITLE:"):
                    title = line.replace("TITLE:", "").strip()
                elif line.startswith("DESCRIPTION:"):
                    description = line.replace("DESCRIPTION:", "").strip()

            # If parsing failed, use the whole response as description
            if not title and not description:
                description = content.strip()
                title = "Image Analysis"

            return title, description

        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            # Return fallback values
            return "Image Analysis", "An image was provided for analysis."

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
        tones = script_data.get("tones", ["informative"])
        # Ensure we always have at least one tone
        if not tones or (isinstance(tones, list) and len(tones) == 0):
            tones = ["informative"]

        template_style = script_data.get("template_style", "medium")
        description = script_data.get("description", "")
        min_length = script_data.get("min_length", 100)
        max_length = script_data.get("max_length", 1000)

        # Handle multiple tones
        if isinstance(tones, list) and len(tones) > 1:
            tone_text = f"Tones: {', '.join(tones)} (blend these tones naturally throughout the content)"
        else:
            tone_text = f"Tone: {tones[0] if isinstance(tones, list) else tones}"

        return f"""
Create a detailed script outline for a YouTube video following proven optimization strategies:

Topic: {description}
{tone_text}
Style: {template_style}
Target Length: {min_length}-{max_length} words

## OUTLINE STRUCTURE (Following YouTube Best Practices):

**1. Hook/Opening (≤30 seconds)**
- Start with ACTION from first line (avoid slow exposition)
- Create 2-3 open-loop questions that will be resolved later
- Include a dramatic, emotionally charged micro-scene (3-6 sentences)
- Ensure hook contains action verbs in first 1-2 sentences
- Plan for fast-paced visuals with shot changes every 1-3 seconds

**2. Introduction/Context (30-60 seconds)**
- Anchor viewers so they know they're in the right video
- Don't repeat title verbatim - add surprising angle while staying coherent
- If premise is unbelievable, immediately confirm with proof
- Seed key plot points or value propositions

**3. Main Content (bulk of video)**
- Deliver on the promise made in title/thumbnail
- Structure as 3-5 key points with clear subpoints
- Include specific examples and evidence
- Plan for visual variety and engagement

**4. Call to Action (after delivering value)**
- Place after meaningful value has been delivered
- Encourage engagement without being pushy
- Include clear next steps for viewers

**5. Closing (memorable ending)**
- Summarize key takeaways
- End on a strong, memorable note
- Avoid abrupt endings

## FOR EACH SECTION, PROVIDE:
- Brief description of what to cover
- Key talking points with specific examples
- Estimated timing (total video should be appropriate for {template_style} style)
- Transition notes to next section
- Visual/editing suggestions where relevant

{f'Make it engaging and blend the {", ".join(tones)} tones naturally throughout the content.' if isinstance(tones, list) and len(tones) > 1 else f'Make it engaging and suitable for the {tones[0] if isinstance(tones, list) else tones} tone.'}

## VALIDATION CHECKLIST:
- Hook ≤ 30 seconds with action verbs
- At least 2 open-loop questions in opening
- No channel trailer/CTA in first 30 seconds
- Fast-paced intro with visual variety
- Value delivered early in main content
- Clear transitions between sections

Ensure the final script will be between {min_length} and {max_length} words.
"""

    @staticmethod
    def _build_script_prompt(outline_text: str, script_data: Dict[str, Any]) -> str:
        """Build prompt for full script generation using advanced YouTube optimization strategies"""
        tones = script_data.get("tones", ["informative"])
        # Ensure we always have at least one tone
        if not tones or (isinstance(tones, list) and len(tones) == 0):
            tones = ["informative"]

        min_length = script_data.get("min_length", 1000)
        max_length = script_data.get("max_length", 5000)

        # Handle multiple tones
        if isinstance(tones, list) and len(tones) > 1:
            tone_text = f"Tones: {', '.join(tones)} (blend these tones naturally throughout the script)"
        else:
            tone_text = f"Tone: {tones[0] if isinstance(tones, list) else tones}"

        return f"""
You are an expert YouTube script writer with deep knowledge of proven optimization strategies. Write a complete, engaging YouTube script following these advanced principles:

## 7 STRATEGIES FOR BETTER OPENINGS:

**S1 - Action-First Openings:**
- Start with action from the first line, avoid slow exposition
- Begin inside a dramatic, emotionally charged scene
- Hook contains an action verb in the first 1-2 sentences
- Micro-scene length: 3-6 sentences, duration ≤ 30 seconds

**S2 - Open Loops & Reasons to Keep Watching:**
- Present unanswered questions the video will resolve
- Include transformation lines: "Learn X to achieve Y"
- Seed future plot points in first 30-60 seconds
- At least 2 open-loop questions in the hook

**S3 - Write Hook After Finishing Script:**
- Preview strongest beats without spoiling outcomes
- Reference at least 2 later beats in the hook
- Ensure alignment with title/thumbnail promises

**S4 - Balance Expectations with Surprise:**
- Don't repeat title/thumbnail verbatim
- If premise is unbelievable, confirm instantly with proof
- Anchor viewers within 2 lines so they know they're in the right video

**S5 - Dense Editing & Fast Pace:**
- Plan 20-45 second fast-cut sequence
- Layer modalities: visuals + text + SFX + music cues
- Average shot length ≤ 3 seconds in intro
- Reduce to baseline pace after hook

**S6 - Get to Main Content Fast:**
- Hook ≤ 30 seconds (exceptions justified)
- Start with first value point within 10 seconds of hook end
- Deliver promised value quickly

**S7 - No Channel Trailer/CTA in Opening:**
- No subscribe request in first 30 seconds
- No personal updates in first 30-45 seconds
- First 10 seconds deliver topic value

## SCRIPT REQUIREMENTS:

OUTLINE TO FOLLOW:
{outline_text}

TECHNICAL SPECS:
- {tone_text}
- Target Length: {min_length}-{max_length} words (CRITICAL: Must be within this exact range)
- Write exactly what the speaker should say
- Make it flow naturally when spoken aloud

STRUCTURE VALIDATION:
- Opening hook ≤ 30 seconds with action verbs
- At least 2 open-loop questions that resolve later
- Fast-paced intro with layered visual cues
- Clear transitions between sections
- Value delivered early, CTAs placed after value

WORD COUNT ENFORCEMENT:
- The script MUST be between {min_length} and {max_length} words
- Count words carefully and ensure the final script meets this requirement
- If the script is too short, add more detail, examples, or explanations
- If the script is too long, condense content while maintaining key points
- This word count constraint is non-negotiable

{f'Write the complete script blending the {", ".join(tones)} tones naturally while following these optimization strategies.' if isinstance(tones, list) and len(tones) > 1 else f'Write the complete script in a {tones[0] if isinstance(tones, list) else tones} tone following these optimization strategies.'}
"""

    @staticmethod
    def _parse_outline_structure(outline_text: str) -> Dict[str, Any]:
        """Parse outline text into structured data - simple format for UI"""
        sections = []

        lines = outline_text.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for numbered sections: "1. [Title]: [Description]"
            if line and line[0].isdigit() and "." in line and ":" in line:
                # Split on the first colon
                parts = line.split(":", 1)
                if len(parts) == 2:
                    title_part = parts[0].strip()
                    description = parts[1].strip()

                    # Extract title (remove number and period)
                    title = (
                        title_part.split(".", 1)[1].strip()
                        if "." in title_part
                        else title_part
                    )

                    sections.append(
                        {
                            "title": title,
                            "description": description,
                            "key_points": [],
                            "timing": "",
                            "transition": "",
                            "content": description,
                        }
                    )

        return {"sections": sections}

    #     @staticmethod
    #     def generate_titles(
    #         prompt: str, title_count: int = 10, tones: list = None
    #     ) -> Tuple[list, Dict[str, Any]]:
    #         """
    #         Generate YouTube titles based on TubeGenius Title Wizardry principles

    #         Args:
    #             prompt: Description or context for the video title generation
    #             title_count: Number of title variations to generate (default: 10)
    #             tones: List of tones/styles to apply (max 3, optional)

    #         Returns:
    #             Tuple of (list of titles, metadata dict)
    #         """
    #         start_time = time.time()

    #         try:
    #             client = get_openai_client()

    #             system_prompt = OpenAIScriptService._build_title_system_prompt()
    #             user_prompt = OpenAIScriptService._build_title_user_prompt(
    #                 prompt, title_count, tones
    #             )

    #             response = client.chat.completions.create(
    #                 model="gpt-4",
    #                 messages=[
    #                     {"role": "system", "content": system_prompt},
    #                     {"role": "user", "content": user_prompt},
    #                 ],
    #                 max_tokens=2000,
    #                 temperature=0.8,
    #             )

    #             generation_time = time.time() - start_time
    #             titles_content = response.choices[0].message.content

    #             # Parse titles from response
    #             titles = OpenAIScriptService._parse_generated_titles(titles_content)

    #             metadata = {
    #                 "tokens_used": response.usage.total_tokens,
    #                 "generation_time": generation_time,
    #                 "model": "gpt-4",
    #                 "title_count": len(titles),
    #             }

    #             # Add tones to metadata if provided
    #             if tones and len(tones) > 0:
    #                 metadata["tones_used"] = tones

    #             return titles, metadata

    #         except Exception as e:
    #             logger.error(f"OpenAI title generation failed: {str(e)}")
    #             raise

    #     @staticmethod
    #     def _build_title_system_prompt() -> str:
    #         """Build system prompt for title generation based on TubeGenius principles"""
    #         return """You are an expert YouTube title writer trained on TubeGenius Title Wizardry principles. Your goal is to create titles that maximize clicks while staying truthful to the content.

    # KEY PRINCIPLES:
    # 1. Create urgency with "I need to click this now" reaction
    # 2. Keep titles ≤54 characters when possible
    # 3. Use proven formats that work
    # 4. Make content accessible to wider audiences
    # 5. Leverage curiosity gaps and open loops
    # 6. Sell the end result, not the process
    # 7. Challenge assumptions with contrarian angles
    # 8. Use strong POV and superlatives
    # 9. Trigger emotions (fear, anger, desire, joy)
    # 10. Add secrets, FOMO, and urgency appropriately

    # POWER WORDS TO USE:
    # - Emotion: SHOCKING, INSANE, DISTURBING, HORRIFYING, AMAZING, INCREDIBLE
    # - Urgency: URGENT, BREAKING, WARNING, NEVER, MUST, NEED
    # - Secrets: SECRET, REAL REASON, TRUTH, HIDDEN, WHAT NO ONE TELLS YOU
    # - Results: CHANGED MY LIFE, 10X, ESCAPE, ACHIEVE, GET RICH, DOMINATE

    # PROVEN FORMATS:
    # - "The Truth About X"
    # - "X Changed My Life"
    # - "The Rise & Fall of X"
    # - "You're Wrong About X"
    # - "I Stopped X—Here's What Happened"
    # - "How X Really Works"
    # - "Why You NEED X"
    # - "NEVER Do X"
    # - "The Most [Adjective] X"
    # - "How X Makes Money"
    # - "The Secret X That Owns Everything"

    # Generate titles that combine multiple strategies intelligently without being overly complex."""

    #     @staticmethod
    #     def _build_title_user_prompt(
    #         prompt: str, title_count: int, tones: list = None
    #     ) -> str:
    #         """Build user prompt for title generation"""
    #         base_prompt = f"""Based on this video concept/topic: "{prompt}"

    # Generate {title_count} high-converting YouTube titles following TubeGenius principles:

    # REQUIREMENTS:
    # - Each title should be ≤54 characters when possible
    # - Use different strategic combinations (emotion + curiosity, fame jacking + urgency, etc.)
    # - Include variety: some contrarian, some outcome-focused, some secret-revealing
    # - Apply appropriate capitalization and power words
    # - Ensure each title creates curiosity without revealing the answer
    # - Make titles accessible to broad audiences
    # - Each title should trigger an emotional response
    # - Vary the formats but keep all titles compelling"""

    #         # Add tone-specific instructions if tones are provided
    #         if tones and len(tones) > 0:
    #             tone_instruction = f"""

    # TONE/STYLE REQUIREMENTS:
    # Focus on incorporating these specific tones/styles: {', '.join(tones)}
    # - Distribute the {title_count} titles across these tones
    # - Adapt the power words and formats to match each tone
    # - Ensure each tone's personality comes through clearly"""

    #             # Add tone-specific guidance
    #             tone_guidance = {
    #                 "Controversial": "- Challenge popular opinions, use contrarian statements, create debate",
    #                 "Shocking": "- Use extreme statements, surprising facts, jaw-dropping revelations",
    #                 "Persuasive": '- Focus on benefits, use "you need this" language, compelling reasons',
    #                 "Mysterious": "- Create intrigue, use secrets and hidden knowledge, unexplained phenomena",
    #                 "Dramatic": "- Use intense language, high-stakes scenarios, emotional peaks",
    #                 "Question-based": "- Pose compelling questions, use interrogative formats, create curiosity gaps",
    #                 "Sarcastic": "- Use irony and wit, playful mockery, clever wordplay",
    #                 "Witty": "- Use humor and cleverness, wordplay, smart observations",
    #                 "Neutral": "- Use factual approach, informative tone, straightforward language",
    #             }

    #             specific_guidance = []
    #             for tone in tones:
    #                 if tone in tone_guidance:
    #                     specific_guidance.append(f"{tone}: {tone_guidance[tone]}")

    #             if specific_guidance:
    #                 tone_instruction += "\n\nTONE-SPECIFIC GUIDANCE:\n" + "\n".join(
    #                     specific_guidance
    #                 )

    #             base_prompt += tone_instruction

    #         base_prompt += """

    # Format your response as a numbered list:
    # 1. [Title]
    # 2. [Title]
    # ...

    # Focus on creating titles that would make someone stop scrolling and click immediately."""

    #         return base_prompt

    #     @staticmethod
    #     def _parse_generated_titles(titles_content: str) -> list:
    #         """Parse generated titles from OpenAI response"""
    #         titles = []
    #         lines = titles_content.strip().split("\n")

    #         for line in lines:
    #             line = line.strip()
    #             if not line:
    #                 continue

    #             # Remove numbering (1., 2., etc.) and clean up
    #             if line and (line[0].isdigit() or line.startswith("-")):
    #                 # Find the title after the number/bullet
    #                 if "." in line:
    #                     title = line.split(".", 1)[1].strip()
    #                 elif line.startswith("-"):
    #                     title = line[1:].strip()
    #                 else:
    #                     title = line

    #                 # Remove quotes if present
    #                 title = title.strip("\"'")

    #                 if title and len(title) > 5:  # Basic validation
    #                     titles.append(title)
    #             elif len(line) > 5:  # Handle titles without numbering
    #                 titles.append(line.strip("\"'"))

    #         return titles

    #     @staticmethod
    #     def generate_optimized_titles(
    #         script=None, user_title=None, user_prompt=None, title_count=5, tones=None
    #     ) -> Tuple[list, Dict[str, Any]]:
    #         """
    #         Generate optimized YouTube titles from script content or user-provided title

    #         Args:
    #             script: Script object with content to optimize (optional)
    #             user_title: User-provided title to optimize (optional)
    #             user_prompt: User instructions for optimization
    #             title_count: Number of title variations to generate (default: 5)
    #             tones: List of tones/styles to apply (optional)

    #         Returns:
    #             Tuple of (list of titles, metadata dict)
    #         """
    #         if script:
    #             # Script-based optimization
    #             script_content = script.content
    #             script_title = script.title or "Untitled Script"

    #             optimization_prompt = f"""
    # Optimize YouTube titles for the following script:

    # Script Title: {script_title}
    # Script Content: {script_content[:1000]}{'...' if len(script_content) > 1000 else ''}

    # User Instructions: {user_prompt}

    # Generate engaging, clickable YouTube titles that capture the essence of this script content while following the user's specific optimization instructions.
    # """
    #         else:
    #             # Title-based optimization
    #             optimization_prompt = f"""
    # Optimize the following YouTube title:

    # Original Title: {user_title}

    # User Instructions: {user_prompt}

    # Generate improved, more engaging YouTube title variations that maintain the original intent while following the user's optimization instructions.
    # """

    #         # Use the existing generate_titles method with the optimization prompt
    #         return OpenAIScriptService.generate_titles(
    #             prompt=optimization_prompt, title_count=title_count, tones=tones
    #         )

    #     @staticmethod
    #     def _parse_script_sections(script_content: str) -> list:
    #         """Parse script content into sections"""
    #         sections = []
    #         current_section = {"title": "Opening", "content": ""}

    #         for line in script_content.split("\n"):
    #             if line.strip().upper() in [
    #                 "HOOK:",
    #                 "INTRODUCTION:",
    #                 "MAIN CONTENT:",
    #                 "CONCLUSION:",
    #                 "CALL TO ACTION:",
    #             ]:
    #                 if current_section["content"].strip():
    #                     sections.append(current_section)
    #                 current_section = {"title": line.strip(), "content": ""}
    #             else:
    #                 current_section["content"] += line + "\n"

    #         if current_section["content"].strip():
    #             sections.append(current_section)

    #         return sections

    @staticmethod
    def generate_titles(
        prompt: str, title_count: int = 6, tones: list = None
    ) -> Tuple[list, Dict[str, Any]]:
        """
        Generate YouTube titles based on TubeGenius Title Wizardry principles

        Args:
            prompt: Description or context for the video title generation
            title_count: Number of title variations to generate (default: 6 to enforce lever variety)
            tones: List of tones/styles to apply (max 3, optional)

        Returns:
            Tuple of (list of title dicts, metadata dict)
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
                max_tokens=1200,
                temperature=0.7,
                timeout=300,
            )

            generation_time = time.time() - start_time
            titles_content = response.choices[0].message.content

            # Parse JSON titles from response
            titles = OpenAIScriptService._parse_generated_titles(titles_content)

            metadata = {
                "tokens_used": response.usage.total_tokens,
                "generation_time": generation_time,
                "model": "gpt-4",
                "title_count": len(titles),
            }

            if tones and len(tones) > 0:
                metadata["tones_used"] = tones

            return titles, metadata

        except Exception as e:
            logger.error(f"OpenAI title generation failed: {str(e)}")
            raise

    @staticmethod
    def _build_title_system_prompt() -> str:
        """Build system prompt for title generation with metadata-enforced JSON output"""
        return """You are an expert YouTube title writer trained on TubeGenius Title Wizardry principles.
Your job is to generate clickable titles AND return them with metadata in JSON.

KEY PRINCIPLES:
- Urgency and open loops
- ≤54 characters preferred (58 max hard limit)
- Strong POV, superlatives, emotional triggers
- Curiosity, secrets, FOMO
- Proven formats (The Truth About X, You're Wrong About X, NEVER Do X, etc.)
- Accessible mass-audience framing
- Avoid safe/boring phrasing

OUTPUT FORMAT:
Return ONLY valid JSON array, no prose. Each item must include:

{
  "title": "5 DISTURBING Stories You Were Never Meant To Hear",
  "levers": ["power_word","curiosity","superlative"],
  "emotion_target": "fear",
  "power_words": ["Disturbing"],
  "length_chars": 52,
  "truncation_safe": true,
  "keyword_hint": "scary stories",
  "notes": "Open loop implied; no payoff revealed"
}"""

    @staticmethod
    def _build_title_user_prompt(
        prompt: str, title_count: int, tones: list = None
    ) -> str:
        """Build user prompt for title generation"""
        base_prompt = f"""Video concept/topic: "{prompt}"

Generate {title_count} titles with metadata JSON as per system instructions.

REQUIREMENTS:
- Each title ≤54 chars (≤58 only if unavoidable)
- Cover all lever categories per batch:
  • Curiosity/open-loop
  • Power-word emphasis
  • Superlative/POV
  • Contrarian/assumption challenge
  • Outcome/benefit
  • Fame-anchor or long-tail SEO variant
- Apply variety of formats from TubeGenius swipe file
- Trigger emotional response without giving away payoff
- Include keyword early (e.g., "scary stories") but avoid stuffing
"""

        if tones and len(tones) > 0:
            base_prompt += f"\nIncorporate these tones: {', '.join(tones)}"

        return base_prompt

    @staticmethod
    def _parse_generated_titles(titles_content: str) -> list:
        """Parse JSON array of generated titles from GPT"""
        try:
            # Remove markdown code fences if present
            cleaned = re.sub(
                r"^```(?:json)?|```$", "", titles_content.strip(), flags=re.MULTILINE
            ).strip()

            # Some models wrap JSON in prose, extract first JSON array
            match = re.search(r"\[.*\]", cleaned, re.DOTALL)
            if match:
                cleaned = match.group(0)

            data = json.loads(cleaned)
            parsed = []
            for t in data:
                length = len(t.get("title", ""))
                t["length_chars"] = length
                t["truncation_safe"] = length <= 54
                if length > 58:
                    t["truncation_safe"] = False
                parsed.append(t)
            return parsed
        except Exception as e:
            logger.error(
                f"Failed to parse GPT titles as JSON: {str(e)}\nContent was:\n{titles_content}"
            )
            return []

    @staticmethod
    def generate_optimized_titles(
        script=None, user_title=None, user_prompt=None, title_count=5, tones=None
    ) -> Tuple[list, Dict[str, Any]]:
        """
        Generate optimized YouTube titles from script content or user-provided title.
        Always returns structured JSON with metadata for each title.

        Args:
            script: Script object with content to optimize (optional)
            user_title: User-provided title to optimize (optional)
            user_prompt: User instructions for optimization
            title_count: Number of title variations to generate (default: 5)
            tones: List of tones/styles to apply (optional)

        Returns:
            Tuple of (list of title dicts, metadata dict)
        """
        if script:
            # Script-based optimization
            script_content = script.content
            script_title = script.title or "Untitled Script"

            optimization_prompt = f"""
Optimize YouTube titles for the following script:

Script Title: {script_title}
Script Content: {script_content[:1000]}{'...' if len(script_content) > 1000 else ''}

User Instructions: {user_prompt}

Follow TubeGenius principles:
- ≤54 chars preferred (≤58 hard max)
- Use power words, curiosity, superlatives, contrarian angles, outcomes
- Include at least one curiosity/open-loop, one contrarian, one power-word-heavy, one outcome-focused, one superlative/POV, and one fame-anchor/SEO variant
- Output MUST be a JSON array with metadata as per system instructions.
"""
        else:
            # Title-based optimization
            optimization_prompt = f"""
Optimize the following YouTube title:

Original Title: {user_title}

User Instructions: {user_prompt}

Follow TubeGenius principles:
- ≤54 chars preferred (≤58 hard max)
- Use power words, curiosity, superlatives, contrarian angles, outcomes
- Include at least one curiosity/open-loop, one contrarian, one power-word-heavy, one outcome-focused, one superlative/POV, and one fame-anchor/SEO variant
- Output MUST be a JSON array with metadata as per system instructions.
"""

        # Reuse core generator so both paths output structured metadata
        return OpenAIScriptService.generate_titles(
            prompt=optimization_prompt, title_count=title_count, tones=tones
        )

    @staticmethod
    def _parse_script_sections(script_content: str) -> list:
        """Parse script content into sections with timestamps for card-based display"""
        sections = []
        current_section = None
        section_counter = 0
        time_per_section = 15  # seconds per section

        for line in script_content.split("\n"):
            line_upper = line.strip().upper()

            # Check for section headers
            if line_upper in [
                "HOOK:",
                "INTRODUCTION:",
                "MAIN CONTENT:",
                "CONCLUSION:",
                "CALL TO ACTION:",
            ]:
                # Save previous section if exists
                if current_section and current_section["content"].strip():
                    sections.append(current_section)
                    section_counter += 1

                # Calculate timestamps for new section
                start_seconds = section_counter * time_per_section
                end_seconds = (section_counter + 1) * time_per_section
                start_time = f"{start_seconds // 60}:{start_seconds % 60:02d}"
                end_time = f"{end_seconds // 60}:{end_seconds % 60:02d}"

                # Create new section
                current_section = {
                    "title": line.strip().replace(":", "").upper(),
                    "content": "",
                    "start_time": start_time,
                    "end_time": end_time,
                }
            elif current_section:
                # Add content to current section
                if line.strip():  # Only add non-empty lines
                    current_section["content"] += line.strip() + "\n"

        # Add the last section
        if current_section and current_section["content"].strip():
            sections.append(current_section)

        return sections

    # Assistant API Integration Methods
    @staticmethod
    def generate_outline_with_assistant(
        script_data: Dict[str, Any],
    ) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        """
        Generate outline using OpenAI Assistant API with knowledge base
        """
        try:
            start_time = time.time()
            client = get_openai_client()

            # Create thread
            thread = client.beta.threads.create()

            # Build message content
            message_content = OpenAIScriptService._build_assistant_outline_message(
                script_data
            )

            # Add message to thread
            client.beta.threads.messages.create(
                thread_id=thread.id, role="user", content=message_content
            )

            # Run the assistant
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id="asst_0DYOjLGGsWULC54slHkY4Lsx",  # Your assistant ID
            )

            # Wait for completion
            outline_text, tokens_used = (
                OpenAIScriptService._wait_for_assistant_completion(
                    client, thread.id, run.id
                )
            )

            generation_time = time.time() - start_time

            # Parse outline structure
            outline_data = OpenAIScriptService._parse_outline_structure(outline_text)

            metadata = {
                "tokens_used": tokens_used,
                "generation_time": generation_time,
                "model": "gpt-4-assistant",
                "assistant_id": "asst_0DYOjLGGsWULC54slHkY4Lsx",
                "thread_id": thread.id,
            }

            return outline_text, outline_data, metadata

        except Exception as e:
            logger.error(f"Assistant outline generation failed: {str(e)}")
            raise

    @staticmethod
    def generate_full_script_with_assistant(
        outline_text: str, script_data: Dict[str, Any]
    ) -> Tuple[str, List[Dict], Dict[str, Any]]:
        """
        Generate full script using OpenAI Assistant API
        """
        try:
            start_time = time.time()
            client = get_openai_client()

            # Create thread
            thread = client.beta.threads.create()

            # Build script generation message
            message_content = OpenAIScriptService._build_assistant_script_message(
                outline_text, script_data
            )

            # Add message to thread
            client.beta.threads.messages.create(
                thread_id=thread.id, role="user", content=message_content
            )

            # Run the assistant
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id="asst_0DYOjLGGsWULC54slHkY4Lsx",  # Your assistant ID
            )

            # Wait for completion
            script_content, tokens_used = (
                OpenAIScriptService._wait_for_assistant_completion(
                    client, thread.id, run.id
                )
            )

            generation_time = time.time() - start_time

            # Parse script sections
            sections = OpenAIScriptService._parse_script_sections(script_content)

            metadata = {
                "tokens_used": tokens_used,
                "generation_time": generation_time,
                "model": "gpt-4-assistant",
                "assistant_id": "asst_0DYOjLGGsWULC54slHkY4Lsx",
                "thread_id": thread.id,
            }

            return script_content, sections, metadata

        except Exception as e:
            logger.error(f"Assistant script generation failed: {str(e)}")
            raise

    @staticmethod
    def analyze_image_with_assistant(
        image_file=None, image_url=None
    ) -> Tuple[str, str]:
        """
        Analyze an image using OpenAI Assistant API with Vision capabilities
        """
        try:
            client = get_openai_client()

            # Create thread
            thread = client.beta.threads.create()

            # Build image analysis message
            if image_file:
                # Convert uploaded file to base64
                image_content = image_file.read()
                image_file.seek(0)
                base64_image = base64.b64encode(image_content).decode("utf-8")
                image_url_for_openai = f"data:image/jpeg;base64,{base64_image}"
            elif image_url:
                image_url_for_openai = image_url
            else:
                raise ValueError("Either image_file or image_url must be provided")

            message_content = """Analyze this image and provide:
1. A catchy, engaging YouTube video title (under 60 characters)
2. A detailed description of what's happening in the image that could be used for script generation

Format your response as:
TITLE: [your title here]
DESCRIPTION: [your description here]

Make the title clickable and engaging for YouTube, and the description detailed enough to generate a good script outline using the storytelling rules and hook techniques from the knowledge base.

Note: Please provide your response in a clear, structured format (not JSON)."""

            # Add message to thread
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=[
                    {"type": "text", "text": message_content},
                    {"type": "image_url", "image_url": {"url": image_url_for_openai}},
                ],
            )

            # Run the assistant
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id="asst_0DYOjLGGsWULC54slHkY4Lsx",  # Your assistant ID
            )

            # Wait for completion
            content, _ = OpenAIScriptService._wait_for_assistant_completion(
                client, thread.id, run.id
            )

            # Parse the response to extract title and description
            title = ""
            description = ""

            lines = content.split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("TITLE:"):
                    title = line.replace("TITLE:", "").strip()
                elif line.startswith("DESCRIPTION:"):
                    description = line.replace("DESCRIPTION:", "").strip()

            # If parsing failed, use the whole response as description
            if not title and not description:
                description = content.strip()
                title = "Image Analysis"

            return title, description

        except Exception as e:
            logger.error(f"Assistant image analysis failed: {str(e)}")
            return "Image Analysis", "An image was provided for analysis."

    @staticmethod
    def _wait_for_assistant_completion(
        client, thread_id: str, run_id: str
    ) -> Tuple[str, int]:
        """Wait for assistant run to complete and return content"""
        while True:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

            if run.status == "completed":
                # Get the latest message
                messages = client.beta.threads.messages.list(
                    thread_id=thread_id, limit=1
                )

                content = messages.data[0].content[0].text.value
                tokens_used = run.usage.total_tokens if run.usage else 0

                return content, tokens_used

            elif run.status in ["failed", "cancelled", "expired"]:
                raise Exception(f"Run failed with status: {run.status}")

            time.sleep(1)  # Wait before checking again

    @staticmethod
    def _build_assistant_outline_message(script_data: Dict[str, Any]) -> str:
        """Build message for outline generation using assistant"""
        tones = script_data.get("tones", ["informative"])
        template_style = script_data.get("template_style", "medium")
        description = script_data.get("description", "")
        min_length = script_data.get("min_length", 100)
        max_length = script_data.get("max_length", 1000)

        tone_text = (
            f"Tones: {', '.join(tones)}" if len(tones) > 1 else f"Tone: {tones[0]}"
        )

        return f"""Create a concise script outline for a YouTube video using the storytelling rules and hook guidelines from the knowledge base:

Topic: {description}
{tone_text}
Style: {template_style}
Target Length: {min_length}-{max_length} words (CRITICAL: Final script must be within this exact range)

Please reference the uploaded files for:
- 17 rules of storytelling principles
- Hook people techniques and strategies

Create a simple, numbered outline with 4-6 sections. Each section should have:
- A brief title (2-5 words)
- One descriptive sentence explaining what to cover

Format like this:
1. [Section Title]: [One sentence description]
2. [Section Title]: [One sentence description]
3. [Section Title]: [One sentence description]
4. [Section Title]: [One sentence description]
5. [Section Title]: [One sentence description]

WORD COUNT REQUIREMENT:
- The final script generated from this outline MUST be between {min_length} and {max_length} words
- Plan the outline to ensure the resulting script will meet this word count requirement
- Consider the depth and detail needed for each section to achieve the target length

Apply the storytelling rules and hook techniques from the knowledge base, but keep the outline format simple and concise.

Note: Please provide your response in a clear, structured format (not JSON)."""

    @staticmethod
    def _build_assistant_script_message(
        outline_text: str, script_data: Dict[str, Any]
    ) -> str:
        """Build message for script generation using assistant"""
        tones = script_data.get("tones", ["informative"])
        min_length = script_data.get("min_length", 1000)
        max_length = script_data.get("max_length", 5000)

        tone_text = (
            f"Tones: {', '.join(tones)}" if len(tones) > 1 else f"Tone: {tones[0]}"
        )

        return f"""Generate a complete YouTube script based on this outline, applying the storytelling rules and hook techniques from the knowledge base:

OUTLINE:
{outline_text}

REQUIREMENTS:
- {tone_text}
- Target Length: {min_length}-{max_length} words (CRITICAL: Must be within this exact range)
- Apply the 17 storytelling rules from the knowledge base
- Use hook techniques to create engaging opening
- Include [PAUSE], [VISUAL], [EMPHASIS] cues
- Make it flow naturally when spoken

WORD COUNT ENFORCEMENT:
- The script MUST be between {min_length} and {max_length} words
- Count words carefully and ensure the final script meets this requirement
- If the script is too short, add more detail, examples, or explanations
- If the script is too long, condense content while maintaining key points
- This word count constraint is non-negotiable

FORMAT YOUR RESPONSE AS:
HOOK:
[Script content for hook section]

INTRODUCTION:
[Script content for introduction section]

MAIN CONTENT:
[Script content for main content section]

CONCLUSION:
[Script content for conclusion section]

CALL TO ACTION:
[Script content for call to action section]

Reference the uploaded files to ensure the script follows proven storytelling principles and engagement techniques.

Note: Please provide your response in a clear, structured format (not JSON)."""
