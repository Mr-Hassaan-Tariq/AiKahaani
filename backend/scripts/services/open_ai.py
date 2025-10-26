# services/openai_service.py
import asyncio
import base64
import json
import logging
import re
import time
from typing import Any, Dict, List, Tuple

import openai
from django.conf import settings

# Import the storytelling manual
from .prompt import prompt as storytelling_manual

# Import word count strategy
from .word_count_strategy import WordCountStrategy

logger = logging.getLogger(__name__)

# Lazy client initialization to avoid import-time errors in tests
_client = None
_title_client = None

# Compliant hook examples for prompts
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
"Imagine sitting at your desk when suddenly..." → REJECTED (weak starter)
"In this video, we'll explore..." → REJECTED (channel trailer)
"Have you ever wondered why..." → REJECTED (generic question)
[6-minute atmospheric description] → CRITICAL FAILURE
"Let me paint you a picture..." → REJECTED (no action)
"Welcome back to the channel..." → REJECTED (CTA violation)
"Today we're going to talk about..." → REJECTED (boring intro)

VALIDATION: First word must be a NOUN or NAME + ACTION VERB within first 5 words.
HOOK LENGTH: Maximum 30 seconds (~75 words at 2.5 words/second)
"""


def get_openai_client():
    """Get OpenAI client, initializing it lazily"""
    global _client
    if _client is None:
        _client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        print(f"[OPENAI_CLIENT] Initialized with model: {settings.OPENAI_MODEL}")
        logger.info(f"[OPENAI_CLIENT] Initialized with model: {settings.OPENAI_MODEL}")
    return _client


def get_title_generation_client():
    """Get OpenAI client specifically for title generation, initializing it lazily"""
    global _title_client
    if _title_client is None:
        _title_client = openai.OpenAI(api_key=settings.TITLE_GENERATION_API_KEY)
        print(f"[TITLE_CLIENT] Initialized with model: {settings.TITLE_GENERATION_MODEL}")
        logger.info(f"[TITLE_CLIENT] Initialized with model: {settings.TITLE_GENERATION_MODEL}")
    return _title_client


def format_storytelling_manual_for_prompt() -> str:
    """
    Format the storytelling manual content for inclusion in AI prompts.
    Returns a condensed but comprehensive version of the manual.
    """
    manual_text = []
    
    # Add the opening strategies section
    manual_text.append("=== 7 STRATEGIES FOR BETTER OPENINGS ===")
    for item in storytelling_manual[:7]:  # First 7 items are opening strategies
        manual_text.append(f"\n{item['id']}: {item['principle_rule']}")
        manual_text.append(f"Explanation: {item['explanation']}")
        if "framework_formula" in item:
            manual_text.append("Framework:")
            for step in item["framework_formula"]:
                manual_text.append(f"• {step}")
        if "case_study_example" in item:
            manual_text.append(f"Example: {item['case_study_example']}")
    
    # Add case studies
    manual_text.append("\n\n=== CASE STUDIES ===")
    for item in storytelling_manual[7:9]:  # Case studies
        manual_text.append(f"\n{item['id']}: {item['principle_rule']}")
        manual_text.append(f"Explanation: {item['explanation']}")
        if "framework_formula" in item:
            manual_text.append("Framework:")
            for step in item["framework_formula"]:
                manual_text.append(f"• {step}")
    
    # Add key principles (condensed)
    manual_text.append("\n\n=== CORE STORYTELLING PRINCIPLES ===")
    key_principles = [
        "P01: Transformation (Beginning–Middle–End): Show transformation by contrasting ending with beginning",
        "P02: Worldbuilding with Specific, Sensory Detail: Use concrete, sensory details to make scenes felt",
        "P03: Causality: Link beats with 'therefore,' 'but,' or 'because,' not 'and then'",
        "P04: Rhythm: Vary sentence and word length to control pace and flow",
        "P05: Emotion: Make the audience feel what the character felt",
        "P06: Make the Audience Care Before Big Events: Build attachment before delivering major highs or lows",
        "P07: Simplify: Remove tangents and confusing details",
        "P11: Tension, Conflict, and Stakes: Define goal, obstacle, and consequences",
        "P12: Curiosity: Plant open loops and manage multiple curiosity threads",
        "P15: Show, Don't Tell: Demonstrate traits through actions and concrete images",
        "P17: Write with the Visual in Mind: Every line should suggest footage or graphics",
    ]
    
    for principle in key_principles:
        manual_text.append(f"• {principle}")
    
    # Add implementation checklist
    manual_text.append("\n\n=== IMPLEMENTATION CHECKLIST ===")
    checklist_items = [
        "Transformation arc explicit (A→B)",
        "Causal connectors present between major beats",
        "At least one clear stakes callback",
        "Two vivid sensory details per key scene",
        "Reading level ≈ high school; jargon removed",
        "Chapter ends with a tease or unresolved thread",
        "Visual cues/storyboard notes embedded",
    ]
    
    for item in checklist_items:
        manual_text.append(f"• {item}")
    
    return "\n".join(manual_text)


def validate_json_schema(data: Dict[str, Any], schema_type: str = "auto") -> bool:
    """
    Validate JSON data against the expected schema structure.
    Supports separate outline and script schemas.
    
    Args:
        data: Dictionary to validate
        schema_type: Type of schema ("outline", "script", or "auto")
    
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        if not isinstance(data, dict):
            return False
        
        # Handle separate schemas for outline and script
        if schema_type == "outline":
            return _validate_outline_schema(data)
        elif schema_type == "script":
            return _validate_script_schema(data)
        elif schema_type == "auto":
            # Auto-detect schema type
            if (
                "sections" in data
                and "section_order" in data
                and "outline_text" in data
            ):
                return _validate_outline_schema(data)
            elif "full_text" in data and "sections" in data:
                return _validate_script_schema(data)
            else:
                return False
        
        # Legacy combined format (for backward compatibility)
        if "outline" in data and "script" in data:
            outline = data["outline"]
            script = data["script"]
            
            # Basic validation of outline structure
            if not isinstance(outline, dict) or not isinstance(script, dict):
                return False
            
            # Check for required keys in outline
            required_outline_keys = [
                "sections",
                "section_order",
                "outline_text",
                "metadata",
            ]
            for key in required_outline_keys:
                if key not in outline:
                    return False
            
            # Check for required keys in script
            required_script_keys = ["full_text", "sections", "metadata"]
            for key in required_script_keys:
                if key not in script:
                    return False
            
            return True
        
        # Check for legacy structure
        elif "sections" in data:
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Schema validation failed: {str(e)}")
        return False


def _validate_outline_schema(data: Dict[str, Any]) -> bool:
    """Validate outline schema structure"""
    required_keys = ["sections", "section_order", "outline_text", "metadata"]
    for key in required_keys:
        if key not in data:
            return False
    
    # Validate metadata structure
    metadata = data.get("metadata", {})
    required_metadata = [
        "tokens_used",
        "generation_time",
        "model",
        "assistant_id",
        "vector_store_id",
        "thread_id",
    ]
    for key in required_metadata:
        if key not in metadata:
            return False
    
    return True


def _validate_script_schema(data: Dict[str, Any]) -> bool:
    """Validate script schema structure"""
    required_keys = ["full_text", "sections", "metadata"]
    for key in required_keys:
        if key not in data:
            return False
    
    # Validate metadata structure
    metadata = data.get("metadata", {})
    required_metadata = [
        "tokens_used",
        "generation_time",
        "model",
        "assistant_id",
        "vector_store_id",
        "thread_id",
    ]
    for key in required_metadata:
        if key not in metadata:
            return False
    
    return True


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
                max_tokens=4096,  # Maximum for GPT-4.1
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
    def _parse_outline_structure(outline_text: str) -> Dict[str, Any]:
        """Parse outline text into structured data - handles both JSON and text formats"""
        import json

        # First, try to parse as JSON (from assistant with new schema)
        try:
            parsed_data = json.loads(outline_text)
            
            # Validate against schema
            if validate_json_schema(parsed_data, "outline"):
                # Handle new schema structure with outline and script
                if "outline" in parsed_data:
                    outline_data = parsed_data["outline"]
                    sections = outline_data.get("sections", [])
                    section_order = outline_data.get("section_order", [])
                    outline_text_raw = outline_data.get("outline_text", outline_text)
                    
                    # Ensure all sections have required fields according to new schema
                    for section in sections:
                        section.setdefault("title", "")
                        section.setdefault("description", "")
                        section.setdefault("key_points", [])
                        section.setdefault("timing", "")
                        section.setdefault("transition", "")
                        section.setdefault("content", section.get("description", ""))
                    
                    # Create default section order if not provided
                    if not section_order:
                        section_order = list(range(len(sections)))
                    
                    # Check validator compliance
                    validator_check = OpenAIScriptService._check_validator_compliance(
                        sections,
                        parsed_data,
                        template_style=script_data.get("template_style", "medium"),
                    )
                    
                    return {
                        "sections": sections, 
                        "section_order": section_order,
                        "outline_text": outline_text_raw,
                        "validator_compliance": validator_check,
                    }
            
            # Handle legacy format with direct sections
            elif "sections" in parsed_data:
                sections = parsed_data["sections"]
                # Ensure all sections have required fields
                for section in sections:
                    section.setdefault("key_points", [])
                    section.setdefault("timing", "")
                    section.setdefault("transition", "")
                    section.setdefault("content", section.get("description", ""))

                # Create default section order if not provided
                default_section_order = parsed_data.get(
                    "section_order", list(range(len(sections)))
                )

                # Check validator compliance
                validator_check = OpenAIScriptService._check_validator_compliance(
                    sections, parsed_data, template_style="medium"
                )

                return {
                    "sections": sections, 
                    "section_order": default_section_order,
                    "validator_compliance": validator_check,
                }
        except json.JSONDecodeError:
            pass

        # Fallback to text parsing for backward compatibility
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

        # Create default section order (0, 1, 2, 3, ... based on number of sections)
        default_section_order = list(range(len(sections)))

        return {"sections": sections, "section_order": default_section_order}

    @staticmethod
    def generate_titles(
        prompt: str,
        title_count: int = 6,
        tones: list = None,
        user=None,
        save_log: bool = True,
    ) -> Tuple[list, Dict[str, Any]]:
        """
        Generate YouTube titles using the OpenAI Chat Completions API.
        Based on TubeGenius Title Wizardry principles.

        Args:
            prompt: Description or context for the video title generation
            title_count: Number of title variations to generate (default: 6)
            tones: List of tones/styles to apply (max 3, optional)
            user: User object for logging (optional)
            save_log: Whether to save run log to database (default: True)

        Returns:
            Tuple of (list of title dicts, metadata dict)
        """
        start_time = time.time()
        try:
            client = get_title_generation_client()

            # Build the message content
            system_prompt = OpenAIScriptService._build_title_system_prompt()
            user_prompt = OpenAIScriptService._build_title_user_prompt(
                prompt, title_count, tones
            )

            # Use Chat Completions API instead of Assistant API
            # GPT-5 and newer models use max_completion_tokens instead of max_tokens
            model_name = settings.TITLE_GENERATION_MODEL.lower()

            api_params = {
                "model": settings.TITLE_GENERATION_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            }

            # GPT-5 and o1 models have different parameter requirements
            if "gpt-5" in model_name or "o1" in model_name:
                # GPT-5 uses max_completion_tokens and doesn't support custom temperature
                # GPT-5 needs MUCH more tokens - consumes 3-4x more than GPT-4o
                api_params["max_completion_tokens"] = 8192  # Maximum for GPT-5
                # Don't set temperature - GPT-5 only accepts default (1)
                # Note: GPT-5 might not support JSON mode - we'll handle response parsing flexibly
                print(
                    f"[TITLES] Using max_completion_tokens=8192 (maximum) for {model_name} (no temperature, no JSON mode)"
                )
            elif "gpt-4.1" in model_name or "gpt-4-turbo" in model_name:
                # GPT-4.1 has 32,768 max output tokens
                api_params["max_tokens"] = 8192  # Plenty for titles
                api_params["temperature"] = 0.7
                print(f"[TITLES] Using max_tokens=8192 for {model_name}")
            else:
                # Older models use max_tokens and support temperature
                api_params["max_tokens"] = 4096
                api_params["temperature"] = 0.7
                print(f"[TITLES] Using max_tokens=4096 for {model_name}")

            try:
                response = client.chat.completions.create(**api_params)
            except Exception as e:
                print(f"[TITLES] ERROR during API call: {str(e)}")
                raise

            # Log what OpenAI actually used
            logger.info(
                f"[TITLES] Generated {title_count} titles using Chat Completions API"
            )

            # Extract content and token usage with validation
            if not response.choices or len(response.choices) == 0:
                raise ValueError("OpenAI API returned no choices in response")
            
            choice = response.choices[0]

            if not hasattr(choice, "message") or not choice.message:
                raise ValueError("OpenAI API returned invalid choice structure")
                
            titles_content = choice.message.content

            if not titles_content:
                raise ValueError(
                    f"OpenAI API returned empty content. Model: {response.model}, Finish reason: {choice.finish_reason}"
                )
                
            tokens_used = response.usage.total_tokens if response.usage else 0

            generation_time = time.time() - start_time
            
            logger.debug(
                f"[TITLES] OpenAI API response validated - content length: {len(titles_content)}, tokens: {tokens_used}"
            )

            # Parse JSON titles
            titles = OpenAIScriptService._parse_generated_titles(titles_content)
            
            # Calculate word count
            word_count = sum(len(t.get("title", "").split()) for t in titles)

            # Generate unique identifiers for logging
            thread_id = f"chat_{int(time.time())}"
            run_id = f"run_{int(time.time())}"

            metadata = {
                "tokens_used": tokens_used,
                "generation_time": generation_time,
                "model": settings.OPENAI_MODEL,
                "assistant_id": "chat-completions",
                "vector_store_id": "none",
                "thread_id": thread_id,
                "run_id": run_id,
                "title_count": len(titles),
                "file_search_used": False,
                "word_count": word_count,
            }

            if tones:
                metadata["tones_used"] = tones

            # Save run log to database
            if save_log:
                OpenAIScriptService._save_run_log(
                    user=user,
                    thread_id=thread_id,
                    run_id=run_id,
                    assistant_id="chat-completions",
                    tokens_used=tokens_used,
                    word_count=word_count,
                    file_search_used=False,
                    file_search_snippets=[],
                    run_type="title_generation",
                    generation_time=generation_time,
                    model=settings.OPENAI_MODEL,
                )

            return titles, metadata

        except Exception as e:
            logger.error(f"Chat completions title generation failed: {str(e)}")
            raise

    @staticmethod
    def _strip_markdown_json(text: str) -> str:
        """
        Strip markdown code blocks from JSON content
        Handles ```json, ```, and other markdown formatting
        """
        if not text:
            return text
            
        cleaned = text.strip()
        
        # Remove markdown code blocks
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]  # Remove ```json
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]  # Remove ```
            
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]  # Remove trailing ```
            
        return cleaned.strip()

    @staticmethod
    def _build_title_system_prompt() -> str:
        """Build the system prompt for title generation with humanization requirements."""
        storytelling_manual = format_storytelling_manual_for_prompt()
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
:rotating_light: CRITICAL LENGTH REQUIREMENTS (NON-NEGOTIABLE):
- **MAXIMUM 55 characters** (absolute hard limit - reject anything longer)
- **5-7 words ONLY** (ideal: 6 words)
- This is what fits on mobile screens - longer titles get cut off and FAIL
- Count characters BEFORE submitting. If over 55 chars, REWRITE SHORTER.
:performing_arts: HUMAN VOICE REQUIREMENTS (70% EMOTIONAL / 30% INFORMATIONAL):
**CRITICAL**: These titles MUST sound like a real YouTuber speaking, NOT like formal article headlines.
**Natural Language Rules**:
  • Use CONTRACTIONS: "I'm", "you're", "don't", "it's", "can't", "won't", "here's"
  • Sound CONVERSATIONAL: Like you're talking to a friend, not writing a thesis
  • Embrace slight "messiness": Real speech has rhythm, not perfect grammar
  • AVOID sterile academic tone: "Strange Truth: X" → "This Weird Truth About X"
  • AVOID formal colons/semicolons: Use dashes, questions, or natural breaks instead
**Emotional Calibration** (70% of title energy):
  • LEAD with emotion/feeling: "Why My Brain Felt Broken..." NOT "Cognitive Effects of..."
  • Use emotional verbs: destroyed, crushed, saved, shocked, transformed
  • Personal pronouns: "I", "My", "You", "Your" (makes it relatable)
  • Visceral language: broken, dead, alive, raw, real, brutal, gentle
  • Sound SPOKEN: Read each title aloud — does it flow naturally?
**Tone Consistency Check**:
  • Dramatic titles: Keep energy high throughout ("Hidden Trap Destroyed My Focus")
  • Soft titles: Stay warm and personal ("Why I Finally Let Go of X")
  • Warning titles: Sound urgent but not clinical ("Stop X—It's Killing Your Y")
  • AVOID mixing: Don't start dramatic then end sterile
:speaking_head_in_silhouette: SPEAK LIKE A REAL CREATOR:
:white_check_mark: GOOD (human, emotional, conversational):
  - "Why My Brain Felt Broken Before This"
  - "Stop Chasing Quick Fixes—Try This Instead"
  - "I'm Done Pretending Dopamine Detox Works"
  - "Your Morning Ritual Is Sabotaging You"
  - "This 5-Min Habit Saved My Focus"
  - "What Nobody Tells You About Burnout"
:x: BAD (robotic, formal, sterile):
  - "Strange Truth: Dopamine Cleanses Change Nothing" (too formal)
  - "The Cognitive Effects of Morning Routines" (academic)
  - "An Analysis of Productivity Systems" (article headline)
  - "Regarding the Issues with Focus Enhancement" (corporate memo)
:art: CREATIVE DIVERSITY RULES (AVOID REPETITION):
**Synonym Rotation** - NEVER repeat the same words across titles. Use varied vocabulary:
  • Numbers: 3, 5, 7, 10 → also try: Few, Several, Simple, Quick, Single
  • Morning → dawn, AM, early, daybreak, sunrise, start, beginning
  • Routine → pattern, system, ritual, habit, practice, method, schedule
  • Focus → attention, concentration, clarity, energy, flow, sharpness, drive
  • Productivity → output, work, results, performance, efficiency, momentum, progress
  • Habits → routines, patterns, systems, rituals, practices, methods, behaviors
  • Secrets → truths, facts, tricks, moves, tactics, insights, lessons, methods
  • Fix/Improve → transform, change, shift, boost, upgrade, enhance, optimize
**CRITICAL**: If you use "morning" in Title 1, use "dawn/AM/early" in others. If you use "routine" in Title 2, use "system/pattern/habit" in others. MAXIMUM FRESHNESS!
**Structure Variation** - Don't use same pattern twice in a batch:
  • Mix question marks, periods, dashes (prefer dashes over colons for natural flow)
  • Vary sentence structure (statements, questions, commands)
  • Alternate between "you" and implied subject
  • Some with numbers, some without
  • Include 1-2 story-based/quantified titles per batch
**Emotional Tone Mixing** - Vary confidence level across batch:
  • Bold/Confident: "Never Trust [X] Again" "This Changes Everything"
  • Relatable/Softer: "Why I Finally Quit [X]" "The One Thing That Worked"
  • Urgent/Warning: "Stop [X] Before It's Late" "Your [X] Is Broken"
  • Curious/Mystery: "What Nobody Tells You About [X]"
  • Story/Proof: "This 5-Minute Habit Fixed My [X]" "How I Doubled [X] in a Week"
:fire: INTRIGUING TITLE FORMULA:
1. **Start with a HOOK** (shock, number, power word, or mystery)
2. **Create CURIOSITY GAP** (make them NEED to click to find out)
3. **Use POWER WORDS**: Shocking, Secret, Never, Exposed, Hidden, Truth, Mistake, Banned, Forbidden, Weird, Strange, Broken, Failed, Destroyed, Crushed, Saved
4. **Add SPECIFICITY**: Numbers, time frames, exact details
5. **Contrast/Conflict**: Before vs After, X vs Y, Truth vs Lie
6. **SOUND HUMAN**: Use contractions, emotional language, conversational flow
:white_check_mark: WINNING PATTERNS (rotate, don't repeat):
- "This [shocking thing] Changed Everything"
- "Why [unexpected fact]?"
- "The [number] [thing] Nobody Tells You"
- "[Number] Secrets [authority figure] Hides"
- "I [did something extreme] for [time]"
- "Stop [common action]—Do This Instead" (note: dash, not parentheses)
- "[Thing] Is Lying to You. Here's Why"
- "What Happens When You [unexpected action]"
- "Your [X] Isn't Working. Here's Why"
- "The [X] Mistake Everyone Makes"
:dart: STORY-BASED / QUANTIFIED PATTERNS (include 1-2 per batch for human touch):
- "This [X]-Minute Habit Fixed My [Problem]"
- "How I Doubled [Benefit] in [Timeframe]"
- "I Tried [X] for [Time Period]—Here's What Happened"
- "[Specific Action] Changed [Outcome] in [Days/Weeks]"
- "The [Number]-[Unit] [Thing] That Transformed [Result]"
- "I Quit [X] for [Timeframe]—Results Shocked Me"
Examples: "This 5-Minute Habit Fixed My Focus" | "How I Doubled Energy in a Week" | "I Woke at 5AM for 30 Days"
:x: FORBIDDEN (AUTO-REJECT):
- "How to..." - BANNED
- "Top 10..." - BANNED
- "A Guide to..." - BANNED
- "Everything you need..." - BANNED
- "In 2025..." - BANNED
- "The Ultimate..." - BANNED
- "Welcome back..." - BANNED
- Formal colons in middle of title (use dashes instead)
- Academic/sterile language ("cognitive effects", "analysis of", "regarding")
- Repeated words/structures within same batch
- Any title over 55 characters - REJECTED
- Vague titles without specifics - REJECTED
- Titles that sound like article headlines, not spoken words
:dart: MAKE IT INTRIGUING:
- Front-load the mystery/shock in first 3 words
- Use unexpected angles (not obvious takes)
- Hint at forbidden/secret knowledge
- Create "I MUST know this" urgency
- Make viewer question what they think they know
- Vary emotional register (bold → soft → urgent → curious)
- **SOUND LIKE A REAL PERSON TALKING**
:microphone: FINAL HUMAN POLISH PASS:
Before finalizing each title, apply this filter:
1. **Read it out loud**: Does it sound natural? Would a YouTuber say this?
2. **Emotion check**: Is it 70% emotional / 30% informational?
3. **Contraction check**: Can you add "I'm", "don't", "here's", "you're"?
4. **Formality check**: Does it sound sterile or academic? If yes, REWRITE more casually
5. **Tone consistency**: Does the energy match throughout, or does it go flat?
6. **Human test**: Would you say this sentence to a friend? If no, rephrase
Example Polish:
  :x: Before: "Strange Truth: Dopamine Cleanses Change Nothing"
  :white_check_mark: After: "This Weird Truth About Dopamine Detox"
  :x: Before: "The Cognitive Effects of Morning Routines"
  :white_check_mark: After: "Why Your Morning Ritual Isn't Working"
  :x: Before: "Analysis: Focus Enhancement Methods Failed"
  :white_check_mark: After: "I Tried Every Focus Hack—They All Failed"
{storytelling_manual}
:dart: FINAL REMINDER:
- 55 characters max, 5-7 words
- INTRIGUING, curiosity-driven, DIVERSE
- 70% EMOTIONAL, 30% informational
- Sound like a REAL YouTuber, not a robot
- Use CONTRACTIONS and conversational flow
- Count characters before submitting!
"""

    @staticmethod
    def _build_title_user_prompt(
        prompt: str, title_count: int, tones: list = None
    ) -> str:
        """Build the user prompt for title generation with specific requirements."""
        base = f"""Video Concept: "{prompt}"
Generate {title_count} YouTube titles that will get HIGH CLICK-THROUGH RATES.
:rotating_light: MANDATORY REQUIREMENTS:
✓ Each title MUST be 55 characters or less (count them!)
✓ Each title MUST be 5-7 words (no more, no less)
✓ Each title MUST be intriguing (create curiosity gap)
✓ Each title MUST have a hook in the first 3 words
✓ Each title MUST sound HUMAN and CONVERSATIONAL (not robotic)
✓ Each title MUST be 70% emotional / 30% informational
✓ NO banned phrases (How to, Guide, Top X, etc.)
✓ NO repeated words/structures within this batch (keep it fresh!)
✓ NO sterile/formal language (avoid colons, academic tone)
:speaking_head_in_silhouette: HUMAN VOICE CHECKLIST (CRITICAL):
✓ Use CONTRACTIONS: "I'm", "you're", "don't", "it's", "here's"
✓ Sound CONVERSATIONAL: Like talking to a friend, not writing an essay
✓ Lead with EMOTION: "Why My Brain Felt Broken..." NOT "Cognitive Analysis..."
✓ Read OUT LOUD: Does it flow naturally when spoken?
✓ AVOID formal structure: Use dashes (—) not colons (:) for natural breaks
✓ Personal & relatable: Use "I", "My", "You", "Your" frequently
:art: DIVERSITY REQUIREMENTS (critical for this batch):
✓ Use different ANGLES across titles:
  - Mix: Contrarian, Story-Based, Single-Solution, Proof-Based, Cost-First, Mystery, Warning
✓ Vary EMOTIONAL TONE (keep natural throughout):
  - 2-3 titles: Bold/Confident ("Never Trust X Again" / "This Changed Everything")
  - 2-3 titles: Relatable/Personal ("Why I Finally Quit X" / "My Brain Felt Broken")
  - 1-2 titles: Story/Quantified ("This 5-Min Habit Fixed My Focus")
  - 2-3 titles: Urgent/Warning ("Stop X—It's Killing Your Y")
✓ Rotate VOCABULARY (CRITICAL - avoid word repetition):
  - NEVER repeat words like "morning," "routine," "focus" across titles
  - Use synonyms: If Title 1 uses "morning" → Title 2 uses "dawn/AM/early"
  - Use synonyms: If Title 2 uses "routine" → Title 3 uses "habit/system/pattern"
  - Use synonyms: output/focus/performance/results instead of repeating "productivity"
  - Vary structures: questions, statements, commands
  - Mix with/without numbers (not all "5 [X]")
✓ Different PATTERNS per title (don't template):
  - Title 1: Question format with emotion
  - Title 2: Story-based with specific metric ("This 10-Min Habit...")
  - Title 3: Personal statement with dash
  - Title 4: Command/Warning with urgency
  - Title 5: Mystery reveal with curiosity
  - Continue rotating...
:dart: ANGLE ROTATION - Use one per title, don't repeat:
1. **Contrarian**: "Everyone Says [X]—They're Wrong"
2. **Personal Story**: "I Changed [One Thing]—Everything Shifted"
3. **Story/Quantified**: "This 5-Min Habit Fixed My [Problem]" or "I Doubled [X] in a Week"
4. **Proof-Based**: "The [X] That Actually Worked for Me"
5. **Cost-First**: "Ignoring [X] Cost Me [Consequence]"
6. **Mystery/Secret**: "What Nobody Tells You About [X]"
7. **Warning**: "Your [X] Is Broken—Here's Why"
8. **Transformation**: "[Specific Action] Changed Everything"
9. **Forbidden Knowledge**: "The [X] Truth They Don't Share"
:fire: MAKE EACH TITLE:
- Start with a power word or number (vary which)
- Create "I MUST watch this" urgency
- Hint at forbidden/hidden knowledge
- Use specific details (numbers, time, exact facts)
- Make viewer question their assumptions
- Front-load the intrigue (don't bury the hook)
- **Feel human, not templated—like a real person speaking**
- **Use contractions and emotional language**
:warning: VALIDATION CHECKLIST (for each title):
□ Character count ≤ 55? (count spaces and punctuation)
□ Word count 5-7?
□ First 3 words create curiosity?
□ Sounds HUMAN when read aloud? (conversational, not robotic)
□ 70% emotional / 30% informational balance?
□ Uses contractions? ("I'm", "don't", "you're", "it's")
□ No formal/sterile language? (no colons, no academic tone)
□ No banned phrases?
□ Specific (not vague)?
□ Different angle from other titles in this batch?
□ Different emotional tone from neighbors?
□ No repeated vocabulary across batch? (Check: morning/routine/focus/productivity)
□ At least 1-2 story/quantified titles in batch? ("This 5-Min Habit..." / "I Doubled X in a Week")
□ Would a REAL YouTuber say this out loud?
:microphone: FINAL HUMAN POLISH:
After generating each title, apply this test:
1. Read it OUT LOUD—does it sound natural?
2. Is it 70% EMOTIONAL, not clinical?
3. Can you add MORE contractions or personal pronouns?
4. Does it sound like a CONVERSATION, not an article?
5. Would YOU click if you heard a friend say this title?
If any title fails the human test, REWRITE to sound more conversational and emotional.
Return ONLY valid JSON array. Every title MUST pass all checks above and feel FRESH, HUMAN, NOT TEMPLATED.
"""
        if tones:
            base += f"\n\n:art: Tones to incorporate: {', '.join(tones)}"
        return base

    @staticmethod
    def _parse_generated_titles(titles_content: str) -> list:
        """Parse JSON array of generated titles from GPT and validate length requirements"""
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
            rejected = []

            for t in data:
                title_text = t.get("title", "")
                length = len(title_text)
                word_count = len(title_text.split())

                # Calculate and add metadata
                t["length_chars"] = length
                t["word_count"] = word_count

                # Strict validation: 55 chars max, 5-7 words
                if length > 55:
                    t["truncation_safe"] = False
                    rejected.append(f"'{title_text}' ({length} chars - TOO LONG)")
                    logger.warning(
                        f"Rejected title (too long): '{title_text}' - {length} chars"
                    )
                    continue  # Skip titles over 55 characters

                if word_count < 5 or word_count > 7:
                    rejected.append(f"'{title_text}' ({word_count} words - need 5-7)")
                    logger.warning(
                        f"Rejected title (wrong word count): '{title_text}' - {word_count} words"
                    )
                    continue  # Skip titles with wrong word count

                # Title passes validation
                t["truncation_safe"] = True
                parsed.append(t)

            if rejected:
                logger.info(
                    f"Rejected {len(rejected)} titles for length violations: {rejected}"
                )

            logger.info(
                f"Accepted {len(parsed)} titles that meet 55 char / 5-7 word requirements"
            )
            return parsed

        except Exception as e:
            logger.error(
                f"Failed to parse GPT titles as JSON: {str(e)}\nContent was:\n{titles_content}"
            )
            return []

    @staticmethod
    def generate_optimized_titles(
        script=None,
        user_title=None,
        user_prompt=None,
        title_count=5,
        tones=None,
        user=None,
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
            user: User object for logging (optional)

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
            prompt=optimization_prompt, title_count=title_count, tones=tones, user=user
        )

    @staticmethod
    def _parse_script_sections(script_content: str) -> list:
        """Parse script content into sections with timestamps for card-based display"""
        import json
        
        # First, try to parse as JSON (from assistant with new schema)
        try:
            parsed_data = json.loads(script_content)
            
            # Validate against schema
            if validate_json_schema(parsed_data, "outline"):
                # Handle new schema structure with outline and script
                if "script" in parsed_data:
                    script_data = parsed_data["script"]
                    sections = script_data.get("sections", [])
                    
                    # Ensure all sections have required fields according to new schema
                    for section in sections:
                        section.setdefault("title", "")
                        section.setdefault("content", "")
                        section.setdefault("start_time", "0:00")
                        section.setdefault("end_time", "0:00")
                    
                    return sections
            
            # Handle legacy format with direct sections
            elif "sections" in parsed_data:
                return parsed_data["sections"]
                
        except json.JSONDecodeError:
            pass

        # Fallback to text parsing for backward compatibility
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
    def generate_outline_two_step(
        script_data: Dict[str, Any],
        user=None,
        save_log: bool = True,
    ) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        """
        Generate outline using two-step process: basic outline first, then validator enhancement
        
        Args:
            script_data: Dictionary containing script parameters
            user: User object for logging (optional)
            save_log: Whether to save run log to database (default: True)
        """
        start_time = time.time()
        try:
            client = get_openai_client()
            
            # STEP 1: Generate basic outline with minimal prompt
            print("=" * 80)
            print(f"[OUTLINE_STEP1] Generating basic outline with model: {settings.OPENAI_MODEL}")
            
            system_prompt = OpenAIScriptService._build_basic_outline_system_prompt()
            user_prompt = OpenAIScriptService._build_basic_outline_user_prompt(script_data)
            
            model_name = settings.OPENAI_MODEL.lower()
            api_params = {
                "model": settings.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "response_format": {"type": "json_object"},
            }
            
            # Set token limits for basic outline
            if "gpt-5" in model_name or "o1" in model_name:
                api_params["max_completion_tokens"] = 4096  # Lower limit for basic outline
            else:
                api_params["max_tokens"] = 4096  # Maximum for GPT-4.1
                api_params["temperature"] = 0.7
            
            response = client.chat.completions.create(**api_params)
            
            if not response.choices or len(response.choices) == 0:
                raise ValueError("OpenAI API returned no choices in response")
            
            choice = response.choices[0]
            if not hasattr(choice, "message") or not choice.message:
                raise ValueError("OpenAI API returned invalid choice structure")
                
            basic_outline_text = choice.message.content
            if not basic_outline_text:
                raise ValueError("OpenAI API returned empty content")
            
            print(f"[OUTLINE_STEP1] Basic outline generated successfully")
            
            # STEP 2: Enhance with validators
            print(f"[OUTLINE_STEP2] Enhancing with validators using model: {settings.OPENAI_MODEL}")
            
            enhancement_system_prompt = OpenAIScriptService._build_validator_enhancement_system_prompt()
            enhancement_user_prompt = OpenAIScriptService._build_validator_enhancement_user_prompt(basic_outline_text)
            
            enhancement_api_params = {
                "model": settings.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": enhancement_system_prompt},
                    {"role": "user", "content": enhancement_user_prompt},
                ],
                "response_format": {"type": "json_object"},
            }
            
            # Set token limits for enhancement
            if "gpt-5" in model_name or "o1" in model_name:
                enhancement_api_params["max_completion_tokens"] = 4096  # Lower limit for enhancement
            else:
                enhancement_api_params["max_tokens"] = 4096  # Maximum for GPT-4.1
                enhancement_api_params["temperature"] = 0.7
            
            enhancement_response = client.chat.completions.create(**enhancement_api_params)
            
            if not enhancement_response.choices or len(enhancement_response.choices) == 0:
                raise ValueError("OpenAI API returned no choices in enhancement response")
            
            enhancement_choice = enhancement_response.choices[0]
            if not hasattr(enhancement_choice, "message") or not enhancement_choice.message:
                raise ValueError("OpenAI API returned invalid enhancement choice structure")
                
            enhanced_outline_text = enhancement_choice.message.content
            if not enhanced_outline_text:
                raise ValueError("OpenAI API returned empty enhancement content")
            
            print(f"[OUTLINE_STEP2] Validator enhancement completed successfully")
            
            # Parse the enhanced outline
            outline_data = OpenAIScriptService._parse_outline_structure(enhanced_outline_text)
            
            # Build outline text from sections
            sections = outline_data.get("sections", [])
            outline_parts = []
            for section in sections:
                title = section.get("title", "")
                description = section.get("description", "")
                if title and description:
                    outline_parts.append(f"{title} - {description}")
            
            outline_text = "\n\n".join(outline_parts)
            
            # Clean up any document references
            outline_text = re.sub(r"■[^■]*?■", "", outline_text)
            outline_text = re.sub(r"[0-9]+:\d+†[^■]*?■", "", outline_text)
            outline_text = re.sub(r"\n\s*\n\s*\n", "\n\n", outline_text)
            outline_text = outline_text.strip()
            
            tokens_used = (response.usage.total_tokens if response.usage else 0) + \
                          (enhancement_response.usage.total_tokens if enhancement_response.usage else 0)
            
            generation_time = time.time() - start_time
            
            metadata = {
                "tokens_used": tokens_used,
                "generation_time": generation_time,
                "model_used": settings.OPENAI_MODEL,
                "method": "two_step_outline_generation",
                "steps": ["basic_outline", "validator_enhancement"]
            }
            
            print(f"[OUTLINE_TWO_STEP] Completed successfully - Tokens: {tokens_used}, Time: {generation_time:.2f}s")
            
            return outline_text, outline_data, metadata
            
        except Exception as e:
            logger.error(f"[OUTLINE_TWO_STEP] Error: {str(e)}")
            raise

    @staticmethod
    def generate_outline_chunked(
        script_data: Dict[str, Any],
        user=None,
        save_log: bool = True,
    ) -> Tuple[str, List[Dict], Dict[str, Any]]:
        """
        Generate outline using chunked approach to save tokens - only pass relevant rules for each step
        
        Args:
            script_data: Dictionary containing script parameters
            user: User object for logging (optional)
            save_log: Whether to save run log to database (default: True)
        """
        start_time = time.time()
        try:
            client = get_openai_client()
            
            print("=" * 80)
            print(f"[OUTLINE_CHUNKED] Generating outline with model: {settings.OPENAI_MODEL}")
            
            # STEP 1: Generate basic structure with minimal prompt
            print(f"[OUTLINE_CHUNKED_STEP1] Generating basic structure...")
            
            structure_user_prompt, suggested_sections = OpenAIScriptService._build_structure_user_prompt(script_data)
            structure_prompt = OpenAIScriptService._build_structure_system_prompt(suggested_sections)
            
            print(f"[OUTLINE_CHUNKED_STEP1] Template requires {suggested_sections} sections")
            
            model_name = settings.OPENAI_MODEL.lower()
            api_params = {
                "model": settings.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": structure_prompt},
                    {"role": "user", "content": structure_user_prompt},
                ],
                "response_format": {"type": "json_object"},
            }
            
            # Set token limits for structure generation
            # Priority: Quality & Speed over cost - generous limits prevent truncation
            if "gpt-5" in model_name or "o1" in model_name:
                api_params["max_completion_tokens"] = 6144  # Generous for 10+ section structures
            elif "gpt-4.1" in model_name or "gpt-4-turbo" in model_name:
                api_params["max_tokens"] = 6144  # 6K handles even 10-section outlines comfortably
                api_params["temperature"] = 0.7
            else:
                api_params["max_tokens"] = 4096
                api_params["temperature"] = 0.7
            
            response = client.chat.completions.create(**api_params)
            
            if not response.choices or len(response.choices) == 0:
                raise ValueError("OpenAI API returned no choices in response")
            
            choice = response.choices[0]
            if not hasattr(choice, "message") or not choice.message:
                raise ValueError("OpenAI API returned invalid choice structure")
                
            structure_text = choice.message.content
            if not structure_text:
                raise ValueError("OpenAI API returned empty content")
            
            print(f"[OUTLINE_CHUNKED_STEP1] Basic structure generated successfully")
            
            # Parse structure
            import json
            structure_data = json.loads(structure_text)
            sections = structure_data.get("sections", [])
            
            if not sections:
                raise ValueError("No sections found in structure")
            
            # STEP 2: Enhance each section individually with only relevant rules (PARALLEL)
            print(f"[OUTLINE_CHUNKED_STEP2] Enhancing {len(sections)} sections in parallel...")
            
            # Use asyncio to run all section enhancements in parallel
            enhanced_sections, total_tokens = OpenAIScriptService._enhance_sections_parallel(
                sections, client, model_name
            )
            
            print(f"[OUTLINE_CHUNKED_STEP2] All {len(enhanced_sections)} sections enhanced in parallel (with inline validation): {total_tokens} total tokens")
            
            # STEP 3: REMOVED - Validation now happens inline during enhancement (saves ~10-15 seconds)
            # Each section is validated as it's enhanced for better quality and faster execution
            # The validators_compliance field in each section contains verification status
            
            # Use enhanced sections directly as final output
            final_sections = enhanced_sections
            
            # Build final outline data
            final_outline_data = {
                "sections": final_sections,
                "section_order": list(range(len(final_sections))),
                "validator_compliance_check": {"overall_compliance": "PASS", "note": "Validation performed inline during enhancement"}
            }
            
            # Build outline text from sections
            outline_parts = []
            for section in final_sections:
                title = section.get("title", "")
                description = section.get("description", "")
                if title and description:
                    outline_parts.append(f"{title} - {description}")
            
            outline_text = "\n\n".join(outline_parts)
            
            generation_time = time.time() - start_time
            
            metadata = {
                "tokens_used": total_tokens,
                "generation_time": generation_time,
                "model_used": settings.OPENAI_MODEL,
                "method": "chunked_outline_generation",
                "sections_generated": len(final_sections),
                "steps_completed": 3
            }
            
            print(f"[OUTLINE_CHUNKED] Completed successfully - Sections: {len(final_sections)}, Tokens: {total_tokens}, Time: {generation_time:.2f}s")
            
            return outline_text, final_outline_data, metadata
            
        except Exception as e:
            logger.error(f"[OUTLINE_CHUNKED] Error: {str(e)}")
            raise

    @staticmethod
    def generate_outline_with_assistant(
        script_data: Dict[str, Any],
        user=None,
        save_log: bool = True,
        use_context_awareness: bool = False,
    ) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        """
        Generate outline using OpenAI Chat Completions API
        
        Args:
            script_data: Dictionary containing script parameters
            user: User object for logging (optional)
            save_log: Whether to save run log to database (default: True)
            use_context_awareness: Whether to use hybrid context-aware approach (default: False)
        """
        # Use hybrid context-aware approach if requested
        if use_context_awareness:
            return OpenAIScriptService.generate_outline_with_context_awareness(
                script_data, user, save_log
            )
        
        # Use chunked outline generation for best quality
        # Chunked approach provides section-specific rules for better accuracy
        # NOTE: Could be optimized with parallel API calls or increased token limits
        return OpenAIScriptService.generate_outline_chunked(
                script_data, user, save_log
            )
        
        # Original stateless approach
        try:
            start_time = time.time()
            client = get_openai_client()
            
            # Extract length requirements from script_data
            min_length = script_data.get("min_length", 1000)
            max_length = script_data.get("max_length", 5000)

            # Build message content with enhanced prompts for Chat Completions
            system_prompt = OpenAIScriptService._build_outline_system_prompt()
            user_prompt = OpenAIScriptService._build_outline_user_prompt(script_data)

            # Check if this is a Flexible Outline template (ID 4)
            template_style_id = script_data.get("template_style_id")
            template_style_name = script_data.get("template_style", "medium")
            
            # For Flexible Outline template, use simple outline generation
            if (
                template_style_id == 4
                or template_style_name.lower() == "flexible_outline"
            ):
                # Simple outline generation for Flexible templates
                enhanced_prompt = f"""{user_prompt}

OUTLINE REQUIREMENTS FOR FLEXIBLE TEMPLATE:
- Create a high-level structure with 3-4 main sections
- Each section should have a brief description (50-100 words)
- Focus on key points and structure, not detailed content
- Target: 100-300 words total for the entire outline
- Format as JSON with sections array

This is a flexible outline template - keep it concise and structural."""
            else:
                # Calculate expected duration and structure using word count strategy for full scripts
                wc_strategy = WordCountStrategy(
                    script_data.get("template_style", "medium")
                )
                
                # Use strategy to calculate section targets
                suggested_sections = wc_strategy.config["suggested_sections"]
                word_targets = wc_strategy.calculate_section_word_targets(
                    suggested_sections
                )
                
                min_duration = min_length / 150
                max_duration = max_length / 150
                words_per_section_min = word_targets["intro"]
                words_per_section_max = word_targets["main_sections"]
            
                # Enhanced prompt with word count strategy integration and quality requirements
                enhanced_prompt = f"""{user_prompt}

🚨 OUTLINE FOR {min_length:,}-{max_length:,} WORD SCRIPT ({min_duration:.1f}-{max_duration:.1f} min video)

STRUCTURE: {suggested_sections} sections with specific word count targets:
• Hook/Intro: {word_targets['intro']} words
• Main Sections: {word_targets['main_sections']} words each ({word_targets['main_sections_count']} sections)
• Conclusion: {word_targets['conclusion']} words
• Total Target: {word_targets['total_target']} words

QUALITY REQUIREMENTS FOR EACH SECTION:

HOOK/INTRO SECTION:
• Line 1-2: Hook with emotion or mystery - make them curious IMMEDIATELY
• MUST create 2-3 specific open loops with concrete questions in first 30 seconds
• Use simple, punchy language with contractions
• NO setup or context first - jump into the moment
• Examples: "The call came at 3 AM. She knew something was wrong." or "It started with a single message."
• FORBIDDEN: Academic words, formal tone, "Imagine/Picture/Let me" openings

NOTE: "Open loops", "Before/Conflict/After", etc. are structural concepts to guide outline creation - they should NOT appear as literal text/labels in the final script.

MAIN CONTENT SECTIONS:
• MUST show transformation: Before → Conflict → After (as narrative flow, not as labels in text)
• MINIMUM 3 concrete sensory details per section
• MUST plant 2-3 specific open loops per section (create curiosity naturally, don't write "Open Loop:" as label)
• MUST end section with unanswered question or unresolved tension - make them want to keep watching
• Use simple, conversational language (6th-7th grade level)
• Include emotional reactions and realizations, not just events
• Link ideas with simple words: "so", "but", "because", "and then" - NO "therefore", "however", "consequently"
• Use contractions in EVERY section: it's, don't, can't, wasn't

CONCLUSION SECTION:
• End with emotional reflection or haunting question that sticks
• Use simple, conversational language - talk like a friend
• NO clichés like "stay curious," "stay brave," "thanks for watching"
• Make them FEEL something or THINK about something new
• Examples: "So what else don't we know?", "And that's the thing - we'll never really know.", "The real question is: what would you do?"

EACH SECTION MUST HAVE:
• Description: 80-150 words (NOT 1-2 sentences!)
• Key points: 5-8 detailed sentences of specific guidance
• Target word count: {words_per_section_min} words
• Timing estimate
• Transition to next section
• Specific examples/stories/angles to include

CRITICAL: Outline detail = script length
• Sparse outline → short script (FAILS)
• Rich outline with word targets → precise script length

VERIFY: Each section has 80-150w description + 5-8 detailed key points + word count target + quality requirements met"""

            # Use Chat Completions API instead of Assistant API
            print("=" * 80)
            print(f"[OUTLINE] Sending request with model: {settings.OPENAI_MODEL}")

            # Build API parameters based on model
            model_name = settings.OPENAI_MODEL.lower()
            api_params = {
                "model": settings.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": enhanced_prompt},
                ],
                "response_format": {"type": "json_object"},
            }

            # GPT-5 and o1 models have different parameter requirements
            if "gpt-5" in model_name or "o1" in model_name:
                # GPT-5 needs more tokens - use maximum limits
                template_style = script_data.get("template_style", "medium")
                max_tokens = 8192
                temperature = None  # GPT-5 doesn't support custom temperature
                api_params["max_completion_tokens"] = max_tokens  # Maximum for GPT-5
                print(
                    f"[OUTLINE] Using max_completion_tokens={max_tokens} (maximum) for {template_style} template with {model_name} (no temperature)"
                )
            elif "gpt-4.1" in model_name or "gpt-4-turbo" in model_name:
                # GPT-4.1 has 32,768 max output tokens (not 4,096!)
                # Use higher limit for better quality and to avoid truncation
                template_style = script_data.get("template_style", "medium")
                max_tokens = 16384  # Use 16K (half of max) for cost efficiency
                temperature = 0.7
                api_params["max_tokens"] = max_tokens
                api_params["temperature"] = temperature
                print(
                    f"[OUTLINE] Using max_tokens={max_tokens} for {template_style} template with {model_name}"
                )
            else:
                # Older GPT-4 models (fallback)
                template_style = script_data.get("template_style", "medium")
                max_tokens = 8192
                temperature = 0.7
                api_params["max_tokens"] = max_tokens
                api_params["temperature"] = temperature
                print(
                    f"[OUTLINE] Using max_tokens={max_tokens} for {template_style} template with {model_name}"
                )

            response = client.chat.completions.create(**api_params)

            print(f"[OUTLINE] OpenAI Response - Model used: {response.model}")
            print(f"[OUTLINE] OpenAI Response - ID: {response.id}")
            print("=" * 80)
            logger.info("[OUTLINE] Generated outline using Chat Completions API")

            # Extract content and token usage with validation
            if not response.choices or len(response.choices) == 0:
                raise ValueError("OpenAI API returned no choices in response")
            
            choice = response.choices[0]
            if not hasattr(choice, "message") or not choice.message:
                raise ValueError("OpenAI API returned invalid choice structure")
                
            outline_text = choice.message.content
            if not outline_text:
                raise ValueError(
                    "OpenAI API returned empty content - this may indicate rate limiting or API error"
                )
                
            tokens_used = response.usage.total_tokens if response.usage else 0

            generation_time = time.time() - start_time
            
            logger.debug(
                f"[OUTLINE] OpenAI API response validated - content length: {len(outline_text)}, tokens: {tokens_used}"
            )

            # Parse outline structure
            outline_data = OpenAIScriptService._parse_outline_structure(outline_text)
            
            # Calculate word count
            word_count = len(outline_text.split())

            # Generate unique identifiers for logging
            thread_id = f"chat_{int(time.time())}"
            run_id = f"run_{int(time.time())}"

            # Initialize metadata first
            metadata = {
                "tokens_used": tokens_used,
                "generation_time": generation_time,
                "model": settings.OPENAI_MODEL,
                "assistant_id": "chat-completions",
                "vector_store_id": "none",
                "thread_id": thread_id,
                "run_id": run_id,
                "file_search_used": False,
                "word_count": word_count,
            }
            
            # Check validator compliance
            compliance_check = OpenAIScriptService._check_validator_compliance(
                outline_data["sections"],
                outline_data,
                template_style=script_data.get("template_style", "medium"),
            )
            
            # ENFORCEMENT STRATEGY: Retry with enhanced prompts if validation fails
            if compliance_check["overall_compliance"] == "FAIL":
                violation_summary = "\n".join(
                    f"  - {v}" for v in compliance_check["violations"]
                )
                logger.warning(
                    f"[OUTLINE] Validator compliance issues detected:\n{violation_summary}"
                )
                
                # Calculate compliance score for better error reporting
                score_info = OpenAIScriptService._calculate_compliance_score(compliance_check["violations"])
                
                logger.warning(f"[OUTLINE] Compliance score: {score_info['score']}/100, Grade: {score_info['grade']}")
                
                # For critical violations, retry with enhanced prompt
                if score_info["blocking"]:
                    logger.info(f"[OUTLINE] Retrying with enhanced enforcement prompt")
                    
                    # Build enhanced prompt with specific violation feedback
                    enhanced_prompt = OpenAIScriptService._build_enhanced_outline_prompt(
                        script_data, violation_summary, score_info
                    )
                    
                    # Retry generation with enhanced prompt
                    try:
                        retry_params = {
                            "model": settings.OPENAI_MODEL,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": enhanced_prompt}
                            ],
                        }
                        
                        # Add token limits based on model
                        if "gpt-5" in model_name or "o1" in model_name:
                            retry_params["max_completion_tokens"] = max_tokens
                        else:
                            retry_params["max_tokens"] = max_tokens
                            if temperature is not None:
                                retry_params["temperature"] = temperature
                        
                        response = client.chat.completions.create(**retry_params)
                        
                        # Parse the retry response
                        outline_data = OpenAIScriptService._parse_outline_response(response)
                        
                        # Re-validate the retry
                        compliance_check = OpenAIScriptService._check_validator_compliance(
                            outline_data["sections"],
                            outline_data,
                            template_style=script_data.get("template_style", "medium"),
                        )
                        
                        logger.info(f"[OUTLINE] Retry compliance: {compliance_check['overall_compliance']}")
                        
                    except Exception as e:
                        logger.error(f"[OUTLINE] Retry failed: {str(e)}")
                        # Continue with original response
                
                logger.info(f"[OUTLINE] Continuing with current response")
            
            # Add compliance check to metadata
            metadata["validator_compliance"] = compliance_check

            # Save run log to database
            if save_log:
                OpenAIScriptService._save_run_log(
                    user=user,
                    thread_id=thread_id,
                    run_id=run_id,
                    assistant_id="chat-completions",
                    tokens_used=tokens_used,
                    word_count=word_count,
                    file_search_used=False,
                    file_search_snippets=[],
                    run_type="outline_generation",
                    generation_time=generation_time,
                    model=settings.OPENAI_MODEL,
                )

            return outline_text, outline_data, metadata

        except Exception as e:
            logger.error(f"Chat completions outline generation failed: {str(e)}")
            raise

    @staticmethod
    def generate_outline_with_context_awareness(
        script_data: Dict[str, Any],
        user=None,
        save_log: bool = True,
    ) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        """
        Generate outline using hybrid approach: basic outline first, then enhance with context awareness
        
        Args:
            script_data: Dictionary containing script parameters
            user: User object for logging (optional)
            save_log: Whether to save run log to database (default: True)
        
        Returns:
            Tuple of (outline_text, outline_data, metadata)
        """
        try:
            logger.info("[HYBRID_OUTLINE] Starting hybrid outline generation with context awareness")
            
            # Step 1: Generate basic outline structure (current approach)
            logger.info("[HYBRID_OUTLINE] Step 1: Generating basic outline structure")
            outline_text, outline_data, metadata = OpenAIScriptService.generate_outline_with_assistant(
                script_data, user, save_log=False  # Don't save log for basic generation
            )
            
            # Step 2: Enhance each section with context awareness
            logger.info("[HYBRID_OUTLINE] Step 2: Enhancing sections with context awareness")
            enhanced_sections = []
            
            for i, section in enumerate(outline_data.get("sections", [])):
                logger.info(f"[HYBRID_OUTLINE] Enhancing section {i+1}: '{section.get('title', 'Untitled')}'")
                
                # Create context from previous sections
                context = OpenAIScriptService._create_section_context(enhanced_sections[:i])
                
                # Enhance this section with context
                enhanced_section = OpenAIScriptService._enhance_section_with_context(
                    section, context, i, len(outline_data.get("sections", [])), script_data
                )
                enhanced_sections.append(enhanced_section)
            
            # Update outline data with enhanced sections
            outline_data["sections"] = enhanced_sections
            
            # Update metadata
            metadata["generation_method"] = "hybrid_context_aware"
            metadata["sections_enhanced"] = len(enhanced_sections)
            
            # Save run log to database
            if save_log:
                OpenAIScriptService._save_run_log(
                    user=user,
                    thread_id=f"hybrid_outline_{int(time.time())}",
                    run_id=f"hybrid_{int(time.time())}",
                    assistant_id="hybrid-context-aware",
                    tokens_used=metadata.get("tokens_used", 0),
                    word_count=metadata.get("word_count", 0),
                    file_search_used=False,
                    file_search_snippets=[],
                    run_type="hybrid_outline_generation",
                    generation_time=metadata.get("generation_time", 0),
                    model=settings.OPENAI_MODEL,
                )
            
            logger.info("[HYBRID_OUTLINE] Hybrid outline generation completed successfully")
            return outline_text, outline_data, metadata
            
        except Exception as e:
            logger.error(f"[HYBRID_OUTLINE] Hybrid outline generation failed: {str(e)}")
            raise

    @staticmethod
    def _create_section_context(previous_sections: List[Dict]) -> str:
        """
        Create compressed context summary from previous sections
        
        Args:
            previous_sections: List of previously enhanced sections
            
        Returns:
            Compressed context string
        """
        if not previous_sections:
            return ""
        
        context_parts = []
        
        for i, section in enumerate(previous_sections[-3:]):  # Last 3 sections only
            title = section.get("title", f"Section {i+1}")
            description = section.get("description", "")[:100]  # First 100 chars
            key_points = section.get("key_points", [])[:3]  # First 3 key points
            
            section_summary = f"Section {i+1} ({title}): {description}"
            if key_points:
                section_summary += f" Key points: {', '.join(key_points[:3])}"
            
            context_parts.append(section_summary)
        
        return " | ".join(context_parts)

    @staticmethod
    def _enhance_section_with_context(
        section: Dict[str, Any], 
        context: str, 
        section_index: int, 
        total_sections: int,
        script_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance a single section with context awareness
        
        Args:
            section: The section to enhance
            context: Context from previous sections
            section_index: Index of current section
            total_sections: Total number of sections
            script_data: Original script data
            
        Returns:
            Enhanced section dictionary
        """
        try:
            client = get_openai_client()
            
            # Build enhancement prompt
            enhancement_prompt = f"""You are an expert YouTube script writer enhancing an outline section with context awareness.

CURRENT SECTION TO ENHANCE:
Title: {section.get('title', 'Untitled')}
Description: {section.get('description', '')}
Key Points: {section.get('key_points', [])}

PREVIOUS SECTIONS CONTEXT:
{context if context else "This is the first section - no previous context."}

SECTION POSITION: {section_index + 1} of {total_sections}

ENHANCEMENT REQUIREMENTS:
1. Improve transitions from previous sections (if not first section)
2. Ensure logical progression and flow
3. Avoid repetition of themes or phrases from previous sections
4. Enhance descriptions with more specific, actionable details
5. Strengthen key points with concrete examples
6. Improve timing estimates and transitions
7. Maintain consistency with overall script tone and style

RESPOND WITH VALID JSON ONLY:
{{
    "title": "Enhanced title",
    "description": "Enhanced description (80-150 words)",
    "key_points": ["Enhanced key point 1", "Enhanced key point 2", ...],
    "timing": "Enhanced timing estimate",
    "transition": "Enhanced transition to next section",
    "content": "Enhanced content summary"
}}

Focus on making this section flow naturally from previous sections while maintaining its unique value."""

            # Generate enhancement
            model_name = settings.OPENAI_MODEL.lower()
            api_params = {
                "model": settings.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": "You are an expert YouTube script writer. Respond with valid JSON only."},
                    {"role": "user", "content": enhancement_prompt}
                ],
                "response_format": {"type": "json_object"},
            }
            
            if "gpt-5" in model_name or "o1" in model_name:
                api_params["max_completion_tokens"] = 8192  # Maximum for GPT-5
            else:
                api_params["max_tokens"] = 4096  # Maximum for GPT-4.1
                api_params["temperature"] = 0.7
            
            response = client.chat.completions.create(**api_params)
            enhanced_content = response.choices[0].message.content
            
            # Parse enhanced content
            import json
            enhanced_section = json.loads(enhanced_content)
            
            # Merge with original section, keeping original fields that weren't enhanced
            merged_section = {
                **section,  # Keep original fields
                **enhanced_section  # Override with enhanced fields
            }
            
            logger.info(f"[HYBRID_OUTLINE] Enhanced section {section_index + 1} successfully")
            return merged_section
            
        except Exception as e:
            logger.warning(f"[HYBRID_OUTLINE] Enhancement failed for section {section_index + 1}: {str(e)}")
            # Return original section if enhancement fails
            return section

    @staticmethod
    def generate_outline_with_context_awareness_by_default(
        script_data: Dict[str, Any],
        user=None,
        save_log: bool = True,
    ) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        """
        Convenience method that uses context-aware outline generation by default
        
        Args:
            script_data: Dictionary containing script parameters
            user: User object for logging (optional)
            save_log: Whether to save run log to database (default: True)
        
        Returns:
            Tuple of (outline_text, outline_data, metadata)
        """
        return OpenAIScriptService.generate_outline_with_assistant(
            script_data, user, save_log, use_context_awareness=True
        )

    @staticmethod
    def generate_full_script_with_assistant(
        outline_text: str, 
        script_data: Dict[str, Any],
        user=None,
        save_log: bool = True,
    ) -> Tuple[str, List[Dict], Dict[str, Any]]:
        """
        Generate full script using OpenAI Chat Completions API
        
        Args:
            outline_text: The outline text to generate script from
            script_data: Dictionary containing script parameters
            user: User object for logging (optional)
            save_log: Whether to save run log to database (default: True)
        """
        min_length = script_data.get("min_length", 1000)
        max_length = script_data.get("max_length", 5000)
        
        # Try single-pass generation first (6x faster), fall back to section-by-section if needed
        logger.info("[SCRIPT_GEN] Attempting single-pass generation...")
        
        try:
            # Attempt single-pass generation
            full_script, sections, metadata = OpenAIScriptService.generate_script_single_pass(
                outline_text, script_data, user, save_log
            )
            
            logger.info(f"[SCRIPT_GEN] ✅ Single-pass SUCCESS! Time: {metadata.get('generation_time_seconds', 0)}s")
            return full_script, sections, metadata
            
        except Exception as e:
            logger.warning(f"[SCRIPT_GEN] Single-pass failed: {str(e)}")
            logger.info("[SCRIPT_GEN] Falling back to section-by-section generation...")
            
            # Fall back to section-by-section generation
            return OpenAIScriptService.generate_script_with_word_count_strategy(
                outline_text, script_data, user, save_log
            )

    @staticmethod
    def generate_script_iterative(
        outline_text: str,
        script_data: Dict[str, Any],
        user=None,
        save_log: bool = True,
    ) -> Dict[str, Any]:
        """
        ITERATIVE GENERATION: Generate script with parallel section expansion
        
        Strategy:
        1. First pass: Generate ALL sections together (maintains flow and tone)
        2. Check word count per section
        3. If any section is short: Expand EACH section in PARALLEL API calls
        4. Each API call focuses on one section (smaller problem, better accuracy)
        5. Combine expanded sections
        
        This approach:
        - First pass maintains narrative flow and tone consistency
        - Parallel expansion is faster than sequential
        - Smaller focused problems help AI hit word count targets better
        
        Args:
            outline_text: The outline text to generate script from
            script_data: Dictionary containing script parameters
            user: User object for logging (optional)
            save_log: Whether to save run log to database (default: True)
            
        Returns:
            Dictionary with keys: "full_text", "sections", "metadata"
        """
        from .word_count_strategy import WordCountStrategy, SectionType
        import json
        import concurrent.futures
        
        start_time = time.time()
        logger.info("="*80)
        logger.info("[ITERATIVE] Starting iterative script generation with parallel expansion...")
        
        try:
            client = get_openai_client()
            
            # Extract template style from script_data
            template_style = script_data.get("template_style", "medium")
            wc_strategy = WordCountStrategy(template_style)
            
            # Parse outline
            outline_data = OpenAIScriptService._parse_outline_structure(outline_text)
            sections = outline_data.get("sections", [])
            
            if not sections:
                raise ValueError("No sections found in outline")
            
            num_sections = len(sections)
            
            # Calculate word targets
            min_length = script_data.get("min_length", 1000)
            max_length = script_data.get("max_length", 5000)
            target_words = (min_length + max_length) // 2
            word_targets = wc_strategy.calculate_section_word_targets(num_sections)
            
            total_target = word_targets['total_target']
            min_acceptable = int(total_target * 0.90)  # 90% of target
            
            logger.info(
                f"[ITERATIVE] Generating {num_sections} sections together, "
                f"target: {total_target} words ({min_length}-{max_length}), "
                f"min acceptable: {min_acceptable} words"
            )
            
            # STEP 1: Generate all sections together (maintains flow)
            logger.info("[ITERATIVE] STEP 1: Generating all sections together...")
            
            system_prompt = OpenAIScriptService._build_single_pass_system_prompt(
                script_data, num_sections, word_targets
            )
            user_prompt = OpenAIScriptService._build_single_pass_user_prompt(
                sections, word_targets, wc_strategy
            )
            
            model_name = settings.OPENAI_MODEL.lower()
            api_params = {
                "model": settings.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 1.0,
            }
            
            if "gpt-4.1" in model_name or "gpt-4-turbo" in model_name:
                api_params["max_tokens"] = 32768
            elif "gpt-5" in model_name or "o1" in model_name:
                api_params["max_completion_tokens"] = 16384
            else:
                api_params["max_tokens"] = 16384
            
            response = client.chat.completions.create(**api_params)
            total_tokens_used = response.usage.total_tokens if response.usage else 0
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            current_sections = result.get("sections", [])
            
            # Add word counts
            for section in current_sections:
                section["word_count"] = len(section.get("content", "").split())
            
            current_word_count = sum(s["word_count"] for s in current_sections)
            
            logger.info(
                f"[ITERATIVE] Initial generation: {current_word_count} words "
                f"({int((current_word_count/total_target)*100)}% of target)"
            )
            
            # STEP 2: Iterative parallel expansion (up to 2 iterations)
            max_expansion_iterations = 2
            
            for expansion_iteration in range(max_expansion_iterations):
                current_word_count = sum(s["word_count"] for s in current_sections)
                
                if current_word_count < min_acceptable:
                    logger.info(
                        f"[ITERATIVE] Expansion iteration {expansion_iteration + 1}/{max_expansion_iterations}: "
                        f"Word count short ({current_word_count} < {min_acceptable}). "
                        f"Starting PARALLEL section expansion..."
                    )
                    
                    # Expand each section in parallel
                    expanded_sections, expansion_tokens = OpenAIScriptService._expand_sections_parallel(
                        current_sections, sections, word_targets, script_data, client, iteration=expansion_iteration + 1
                    )
                    
                    total_tokens_used += expansion_tokens
                    current_sections = expanded_sections
                    
                    # Recalculate word counts
                    for section in current_sections:
                        section["word_count"] = len(section.get("content", "").split())
                    
                    final_word_count = sum(s["word_count"] for s in current_sections)
                    
                    logger.info(
                        f"[ITERATIVE] After expansion iteration {expansion_iteration + 1}: {final_word_count} words "
                        f"({int((final_word_count/total_target)*100)}% of target)"
                    )
                    
                    # Check if we've reached acceptable word count
                    if final_word_count >= min_acceptable:
                        logger.info(f"[ITERATIVE] ✅ Word count acceptable after iteration {expansion_iteration + 1}!")
                        break
                else:
                    logger.info(f"[ITERATIVE] ✅ Word count acceptable, no expansion needed!")
                    break
            
            # Calculate timing for all sections
            current_sections = wc_strategy.calculate_timing_for_sections(current_sections)
            
            # Build full script text with section titles (for downloads)
            script_parts = []
            for section in current_sections:
                section_title = section.get("title", "Untitled Section").upper()
                section_content = section.get("content", "")
                script_parts.append(f"=== {section_title} ===")
                script_parts.append(section_content)
                script_parts.append("")  # Empty line between sections
            
            full_script = "\n".join(script_parts).strip()
            total_words = sum(s["word_count"] for s in current_sections)
            
            # Create metadata
            total_time = time.time() - start_time
            thread_id = f"iterative_{int(start_time)}"
            run_id = f"iterative_run_{int(start_time)}"
            
            metadata = {
                "tokens_used": total_tokens_used,
                "generation_time": round(total_time, 2),
                "model": settings.OPENAI_MODEL,
                "assistant_id": "iterative",
                "vector_store_id": "none",
                "thread_id": thread_id,
                "run_id": run_id,
                "file_search_used": False,
                "word_count": total_words,
                "length_valid": min_length <= total_words <= max_length * 1.1,
                "strategy_used": "iterative_parallel",
                "sections_generated": len(current_sections),
                "template_style": script_data.get("template_style", "medium"),
            }
            
            logger.info(
                f"[ITERATIVE] ✅ SUCCESS! Total time: {total_time:.1f}s "
                f"({total_words} words, {len(current_sections)} sections)"
            )
            
            return {
                "full_text": full_script,
                "sections": current_sections,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"[ITERATIVE] ❌ FAILED: {str(e)}")
            raise
    
    @staticmethod
    def _expand_sections_parallel(
        current_sections: list,
        original_outlines: list,
        word_targets: Dict[str, Any],
        script_data: Dict[str, Any],
        client,
        iteration: int = 1,
    ) -> Tuple[list, int]:
        """
        Expand each section in PARALLEL API calls
        
        This gives each section a focused expansion task, improving accuracy.
        Parallel execution is faster than sequential.
        
        Args:
            iteration: Which expansion iteration this is (1 or 2)
        """
        import concurrent.futures
        import json
        
        logger.info(f"[PARALLEL_EXPANSION] Iteration {iteration}: Expanding {len(current_sections)} sections in parallel...")
        
        total_tokens = 0
        
        def expand_single_section(index: int, section: Dict, outline: Dict) -> Tuple[int, Dict, int]:
            """Expand a single section - called in parallel"""
            try:
                # Determine target for this section
                if index == 0:  # Hook
                    target = word_targets.get('intro', 0)
                    section_type = "hook"
                elif index == len(current_sections) - 1:  # Conclusion
                    target = word_targets.get('conclusion', 0)
                    section_type = "conclusion"
                else:  # Main content
                    target = word_targets.get('main_sections', 0)
                    section_type = "main_content"
                
                current_words = section.get("word_count", 0)
                shortfall_words = target - current_words
                
                # Skip if already at target or over
                if shortfall_words <= 0:
                    logger.info(
                        f"[PARALLEL_EXPANSION] Iter {iteration}, Section {index+1} already at target "
                        f"({current_words}/{target} words), skipping"
                    )
                    return (index, section, 0)
                
                # Convert shortfall to minutes/seconds of speech @ 140 WPM
                shortfall_minutes = shortfall_words / 140
                shortfall_min_int = int(shortfall_minutes)
                shortfall_sec_int = int((shortfall_minutes % 1) * 60)
                
                logger.info(
                    f"[PARALLEL_EXPANSION] Iter {iteration}, Section {index+1}: {current_words} → {target} words "
                    f"(need +{shortfall_words} words = +{shortfall_min_int}:{shortfall_sec_int:02d} min of speech)"
                )
                
                # Build expansion prompt for this specific section (using duration, not word count)
                system_prompt = OpenAIScriptService._build_single_section_expansion_system_prompt(
                    current_words, target, shortfall_min_int, shortfall_sec_int, section_type
                )
                user_prompt = OpenAIScriptService._build_single_section_expansion_user_prompt(
                    section, outline, target, shortfall_min_int, shortfall_sec_int, script_data
                )
                
                # Make API call for this section
                model_name = settings.OPENAI_MODEL.lower()
                api_params = {
                    "model": settings.OPENAI_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 1.0,
                }
                
                if "gpt-4.1" in model_name or "gpt-4-turbo" in model_name:
                    api_params["max_tokens"] = 16384
                elif "gpt-5" in model_name or "o1" in model_name:
                    api_params["max_completion_tokens"] = 8192
                else:
                    api_params["max_tokens"] = 8192
                
                response = client.chat.completions.create(**api_params)
                tokens_used = response.usage.total_tokens if response.usage else 0
                
                content = response.choices[0].message.content
                result = json.loads(content)
                
                expanded_section = result.get("section", {})
                expanded_section["word_count"] = len(expanded_section.get("content", "").split())
                
                logger.info(
                    f"[PARALLEL_EXPANSION] Iter {iteration}, Section {index+1} expanded: "
                    f"{current_words} → {expanded_section['word_count']} words"
                )
                
                return (index, expanded_section, tokens_used)
                
            except Exception as e:
                logger.error(f"[PARALLEL_EXPANSION] Iter {iteration}, Section {index+1} failed: {str(e)}")
                # Return original section if expansion fails
                return (index, section, 0)
        
        # Execute all expansions in parallel
        expanded_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(current_sections)) as executor:
            futures = [
                executor.submit(expand_single_section, i, section, original_outlines[i])
                for i, section in enumerate(current_sections)
            ]
            
            for future in concurrent.futures.as_completed(futures):
                index, expanded_section, tokens = future.result()
                expanded_results.append((index, expanded_section, tokens))
                total_tokens += tokens
        
        # Sort by index to maintain order
        expanded_results.sort(key=lambda x: x[0])
        expanded_sections = [result[1] for result in expanded_results]
        
        logger.info(
            f"[PARALLEL_EXPANSION] Iteration {iteration} completed! Total tokens used: {total_tokens}"
        )
        
        return expanded_sections, total_tokens
    
    @staticmethod
    def _build_single_section_expansion_system_prompt(
        current_words: int, target_words: int, shortfall_min: int, shortfall_sec: int, section_type: str
    ) -> str:
        """System prompt for expanding a single section (uses duration, not word count)"""
        duration_current_min = int(current_words / 140)
        duration_current_sec = int((current_words / 140 % 1) * 60)
        duration_target_min = int(target_words / 140)
        duration_target_sec = int((target_words / 140 % 1) * 60)
        
        # Format duration strings
        current_duration_str = f"{duration_current_min}:{duration_current_sec:02d}" if duration_current_min >= 1 else f"{duration_current_sec}s"
        target_duration_str = f"{duration_target_min}:{duration_target_sec:02d}" if duration_target_min >= 1 else f"{duration_target_sec}s"
        shortfall_duration_str = f"{shortfall_min}:{shortfall_sec:02d}" if shortfall_min >= 1 else f"{shortfall_sec}s"
        
        return f"""You are an expert YouTube script writer. EXPAND this single {section_type} section to reach its duration target.

📊 CURRENT STATUS (THIS SECTION ONLY):
- Section type: {section_type}
- Current duration: {current_duration_str} min of spoken English (@ 140 words/minute)
- Target duration: {target_duration_str} min of spoken English (@ 140 words/minute)
- Need to add: {shortfall_duration_str} min MORE of spoken content

🎯 YOUR TASK:
Take the current section content and expand it by adding {shortfall_duration_str} minutes of spoken content.
Think: "How much content does someone need to speak for {shortfall_duration_str} minutes?"
This is a FOCUSED task - just this one section, not the whole script.

🎙️ DURATION-BASED THINKING:
- You're writing for someone to READ ALOUD at 140 words per minute
- Generate enough content to fill {shortfall_duration_str} minutes of speaking time
- This is approximately {int((shortfall_min * 60 + shortfall_sec) / 60 * 140)} additional words

📝 HOW TO EXPAND (DO NOT just add filler):
- Add MORE concrete examples and case studies
- Include MORE dialogue and quotes  
- Add MORE sensory details (what it looks like, sounds like, feels like)
- Expand emotional reactions at key moments
- Add MORE backstory and context
- Slow down important moments with rich description
- Elaborate on existing points with more depth

✂️ CONTRACTIONS: Use contractions throughout (it's, don't, can't, we're, you'll)
💬 LANGUAGE: Keep 6th-7th grade language (simple, conversational)
{"🎬 ACTION VERBS: Start with action verbs (Imagine, Picture, Think about...)" if section_type == "hook" else ""}
{"🔗 CURIOSITY HOOK: End with a hook to the next section" if section_type != "conclusion" else ""}

Return JSON with the EXPANDED section:
{{{{
  "section": {{{{
    "title": "Section title",
    "content": "EXPANDED content here...",
    "section_type": "{section_type}"
  }}}}
}}}}
"""
    
    @staticmethod
    def _build_single_section_expansion_user_prompt(
        section: Dict, outline: Dict, target_words: int, shortfall_min: int, shortfall_sec: int, script_data: Dict[str, Any]
    ) -> str:
        """User prompt for expanding a single section (uses duration, not word count)"""
        duration_target_min = int(target_words / 140)
        duration_target_sec = int((target_words / 140 % 1) * 60)
        target_duration_str = f"{duration_target_min}:{duration_target_sec:02d} min" if duration_target_min >= 1 else f"{duration_target_sec} sec"
        
        shortfall_duration_str = f"{shortfall_min}:{shortfall_sec:02d} min" if shortfall_min >= 1 else f"{shortfall_sec} sec"
        
        prompt_parts = [
            f"EXPAND this section by adding {shortfall_duration_str} of spoken content:",
            f"",
            f"🎙️ TARGET DURATION: {target_duration_str} of spoken English (@ 140 words/minute)",
            f"🎙️ NEED TO ADD: {shortfall_duration_str} MORE of spoken content",
            f"",
            f"OUTLINE:",
            f"Title: {outline.get('title', 'Untitled')}",
            f"Description: {outline.get('description', '')}",
        ]
        
        key_points = outline.get('key_points', [])
        if key_points:
            prompt_parts.append("Key Points:")
            for point in key_points:
                prompt_parts.append(f"• {point}")
        
        prompt_parts.append("")
        prompt_parts.append("CURRENT CONTENT:")
        prompt_parts.append(section.get('content', ''))
        prompt_parts.append("")
        prompt_parts.append(f"Topic: {script_data.get('topic', '')}")
        prompt_parts.append(f"Tone: {script_data.get('tone', 'engaging')}")
        prompt_parts.append("")
        prompt_parts.append(f"🚨 CRITICAL: Expand this content to fill {target_duration_str} of speaking time by adding examples, dialogue, details, and emotion.")
        prompt_parts.append(f"🚨 You need to add approximately {shortfall_duration_str} more of spoken content.")
        prompt_parts.append(f"🚨 Think: 'How much content does someone need to speak for {shortfall_duration_str} minutes?'")
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def _build_expansion_system_prompt_all_sections(
        current_word_count: int, target_word_count: int, shortfall: int, num_sections: int
    ) -> str:
        """Build system prompt for expansion iteration (ALL sections together)"""
        return f"""You are an expert YouTube script editor. You will receive the FULL CURRENT SCRIPT and must EXPAND it to reach the word count target.

📊 CURRENT STATUS:
- Current word count: {current_word_count} words
- Target word count: {target_word_count} words
- Shortfall: {shortfall} words ({int((shortfall/num_sections))} words per section on average)

🎯 YOUR TASK:
Take the COMPLETE script provided and expand ALL sections by adding {shortfall} total words across the entire script.
You will see the full current content of every section - use this to maintain perfect continuity.

🔗 CRITICAL - MAINTAIN FLOW AND TONE:
- Keep the narrative flow seamless from hook → main sections → conclusion
- Maintain consistent tone throughout all sections
- Preserve natural transitions between sections
- Keep the storytelling coherent and engaging
- Build on what's already there - don't rewrite, just expand naturally

📝 HOW TO EXPAND (DO NOT just add filler):
- Add MORE concrete examples and case studies
- Include MORE dialogue and quotes  
- Add MORE sensory details (what it looks like, sounds like, feels like)
- Expand emotional reactions at key moments
- Add MORE backstory and context
- Slow down important moments with rich description
- Add transitions between ideas
- Elaborate on existing points with more depth

✂️ CONTRACTIONS: Use contractions throughout (it's, don't, can't, we're, you'll)
💬 LANGUAGE: Keep 6th-7th grade language (simple, conversational)
🎬 ACTION VERBS: Maintain action verbs in hook (Imagine, Picture, Think about...)

⚠️  You MUST return ALL sections in your response, not just the ones you modified.

Return JSON with ALL EXPANDED sections:
{{{{
  "sections": [
    {{{{
      "title": "Section title",
      "content": "EXPANDED content here...",
      "section_type": "hook" | "main_content" | "conclusion"
    }}}}
  ]
}}}}
"""
    
    @staticmethod
    def _build_expansion_user_prompt_all_sections(
        current_sections: list, original_sections: list, shortfall: int, word_targets: Dict[str, Any]
    ) -> str:
        """Build user prompt for expansion iteration (ALL sections together)"""
        words_to_add_per_section = shortfall // len(current_sections)
        
        prompt_parts = [
            f"EXPAND this COMPLETE script by adding {shortfall} total words:",
            f"",
            f"Distribute approximately {words_to_add_per_section} words to EACH section.",
            f"",
            f"⚠️  IMPORTANT: You are receiving the FULL CONTENT of every section below.",
            f"⚠️  Use this complete context to maintain flow and tone consistency across ALL sections.",
            f"⚠️  Build on what's already there - expand naturally, don't rewrite from scratch.",
            f"",
            f"CURRENT SCRIPT (FULL CONTENT OF ALL SECTIONS):",
            f"",
        ]
        
        for i, section in enumerate(current_sections):
            current_words = section.get("word_count", 0)
            section_type = section.get("section_type", "main_content")
            
            # Determine target for this section
            if i == 0:  # Hook
                target = word_targets.get('intro', 0)
            elif i == len(current_sections) - 1:  # Conclusion
                target = word_targets.get('conclusion', 0)
            else:  # Main content
                target = word_targets.get('main_sections', 0)
            
            prompt_parts.append(f"{'='*60}")
            prompt_parts.append(f"SECTION {i+1}: {section.get('title', f'Section {i+1}')}")
            prompt_parts.append(f"Type: {section_type}")
            prompt_parts.append(f"Current: {current_words} words | Target: {target} words")
            prompt_parts.append(f"")
            
            # Show FULL content so AI can maintain flow and context
            full_content = section.get('content', '')
            prompt_parts.append(f"FULL CURRENT CONTENT:")
            prompt_parts.append(full_content)
            prompt_parts.append("")
        
        prompt_parts.append(f"{'='*60}")
        prompt_parts.append("")
        prompt_parts.append(f"🚨 EXPAND ALL sections by adding examples, dialogue, details, and emotion.")
        prompt_parts.append(f"🚨 The goal is to add {shortfall} total words across the ENTIRE script.")
        prompt_parts.append(f"🚨 MAINTAIN narrative flow from hook through main sections to conclusion.")
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def generate_script_single_pass(
        outline_text: str,
        script_data: Dict[str, Any],
        user=None,
        save_log: bool = True,
    ) -> Dict[str, Any]:
        """
        SINGLE-PASS GENERATION: Generate entire script in one API call for maximum speed
        
        This method generates the complete script in a single request, which:
        - Reduces time from 5-6 minutes to ~60-90 seconds (6x faster)
        - Maintains perfect narrative flow (no section breaks)
        - Uses comprehensive prompts with all storytelling rules
        - Falls back to section-by-section if validation fails
        
        Args:
            outline_text: The outline text to generate script from
            script_data: Dictionary containing script parameters
            user: User object for logging (optional)
            save_log: Whether to save run log to database (default: True)
            
        Returns:
            Dictionary with keys: "full_text", "sections", "metadata"
        """
        from .word_count_strategy import WordCountStrategy, SectionType
        
        start_time = time.time()
        logger.info("="*80)
        logger.info("[SINGLE_PASS] Starting single-pass script generation...")
        
        try:
            client = get_openai_client()
            
            # Extract template style from script_data
            template_style = script_data.get("template_style", "medium")
            wc_strategy = WordCountStrategy(template_style)
            
            # Parse outline
            outline_data = OpenAIScriptService._parse_outline_structure(outline_text)
            sections = outline_data.get("sections", [])
            
            if not sections:
                raise ValueError("No sections found in outline")
            
            num_sections = len(sections)
            
            # Calculate word targets
            min_length = script_data.get("min_length", 1000)
            max_length = script_data.get("max_length", 5000)
            target_words = (min_length + max_length) // 2
            word_targets = wc_strategy.calculate_section_word_targets(num_sections)
            
            logger.info(
                f"[SINGLE_PASS] Generating {num_sections} sections, "
                f"target: {target_words} words ({min_length}-{max_length})"
            )
            
            # Build comprehensive single-pass prompt
            system_prompt = OpenAIScriptService._build_single_pass_system_prompt(
                script_data, num_sections, word_targets
            )
            
            user_prompt = OpenAIScriptService._build_single_pass_user_prompt(
                sections, word_targets, wc_strategy
            )
            
            # Use MAXIMUM token limits for GPT-4.1
            model_name = settings.OPENAI_MODEL.lower()
            api_params = {
                "model": settings.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 1.0,  # Match dashboard setting for longer outputs
            }
            
            if "gpt-4.1" in model_name or "gpt-4-turbo" in model_name:
                # Use MAXIMUM output tokens for GPT-4.1: 32,768 tokens
                api_params["max_tokens"] = 32768
                logger.info(f"[SINGLE_PASS] Using maximum tokens: 32,768 for GPT-4.1")
            elif "gpt-5" in model_name or "o1" in model_name:
                api_params["max_completion_tokens"] = 16384
                logger.info(f"[SINGLE_PASS] Using maximum tokens: 16,384 for GPT-5")
            else:
                api_params["max_tokens"] = 16384
                logger.info(f"[SINGLE_PASS] Using maximum tokens: 16,384")
            
            # Generate entire script in one call
            logger.info("[SINGLE_PASS] Sending API request...")
            generation_start = time.time()
            
            response = client.chat.completions.create(**api_params)
            
            generation_time = time.time() - generation_start
            logger.info(f"[SINGLE_PASS] Generation completed in {generation_time:.1f}s")
            
            if not response.choices or len(response.choices) == 0:
                raise ValueError("No response from OpenAI")
            
            choice = response.choices[0]
            finish_reason = choice.finish_reason
            
            # CRITICAL: Check if response was truncated
            if finish_reason == "length":
                tokens_used = response.usage.total_tokens if response.usage else 0
                max_tokens_used = api_params.get("max_tokens") or api_params.get("max_completion_tokens")
                logger.error(
                    f"[SINGLE_PASS] ❌ RESPONSE TRUNCATED! finish_reason='length' "
                    f"- Hit token limit ({tokens_used} tokens, max={max_tokens_used})"
                )
                logger.error("[SINGLE_PASS] Script is incomplete - falling back to section-by-section")
                raise ValueError(f"Response truncated - hit {max_tokens_used} token limit")
            
            logger.info(f"[SINGLE_PASS] finish_reason: {finish_reason} ✓")
            
            content = choice.message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            logger.info(f"[SINGLE_PASS] Tokens used: {tokens_used}")
            
            # Parse JSON response
            import json
            script_data_response = json.loads(content)
            
            generated_sections = script_data_response.get("sections", [])
            if not generated_sections:
                raise ValueError("No sections in response")
            
            # Validate the generated script
            # Count actual words from content (AI no longer provides word_count field)
            for section in generated_sections:
                actual_word_count = len(section.get("content", "").split())
                section["word_count"] = actual_word_count  # Add actual count
            
            # Calculate timing for sections (start_time and end_time)
            generated_sections = wc_strategy.calculate_timing_for_sections(generated_sections)
            
            # Log timing info
            logger.info("[SINGLE_PASS] Section timing calculated:")
            for i, section in enumerate(generated_sections):
                logger.info(
                    f"  Section {i+1}: {section.get('start_time', 'NO_START')} - "
                    f"{section.get('end_time', 'NO_END')} ({section['word_count']} words)"
                )
            
            total_words = sum(s["word_count"] for s in generated_sections)
            
            logger.info(
                f"[SINGLE_PASS] Generated {len(generated_sections)} sections, "
                f"{total_words} words ACTUAL (target: {min_length}-{max_length})"
            )
            
            # Check if we need to expand (too short) or reject (way too short)
            is_way_too_short = total_words < min_length * 0.70  # Less than 70% of minimum
            is_too_short = total_words < min_length  # Less than minimum
            is_too_long = total_words > max_length * 1.15  # More than 115% of maximum
            
            if is_way_too_short:
                # Too far off - reject and fall back to section-by-section
                logger.warning(
                    f"[SINGLE_PASS] Word count WAY too short: {total_words} "
                    f"(need {min_length}+ minimum, got {int((total_words/min_length)*100)}%)"
                )
                raise ValueError(f"Word count too short: {total_words} words (need {min_length}+)")
            
            if is_too_long:
                # Too long - reject and fall back
                logger.warning(
                    f"[SINGLE_PASS] Word count too long: {total_words} "
                    f"(max {int(max_length * 1.15)})"
                )
                raise ValueError(f"Word count too long: {total_words} words")
            
            # Build full script text with section titles (for downloads)
            script_parts = []
            for section in generated_sections:
                section_title = section.get("title", "Untitled Section").upper()
                section_content = section.get("content", "")
                script_parts.append(f"=== {section_title} ===")
                script_parts.append(section_content)
                script_parts.append("")  # Empty line between sections
            
            full_script = "\n".join(script_parts).strip()
            
            # Create metadata (matching format expected by view)
            total_time = time.time() - start_time
            thread_id = f"single_pass_{int(start_time)}"
            run_id = f"single_pass_run_{int(start_time)}"
            
            metadata = {
                "tokens_used": tokens_used,
                "generation_time": round(total_time, 2),
                "model": settings.OPENAI_MODEL,
                "assistant_id": "single-pass",
                "vector_store_id": "none",
                "thread_id": thread_id,
                "run_id": run_id,
                "file_search_used": False,
                "word_count": total_words,
                "length_valid": min_length <= total_words <= max_length * 1.1,
                "strategy_used": "single_pass",
                "sections_generated": len(generated_sections),
                "template_style": script_data.get("template_style", "medium"),
            }
            
            logger.info(
                f"[SINGLE_PASS] ✅ SUCCESS! Total time: {total_time:.1f}s "
                f"({total_words} words, {len(generated_sections)} sections)"
            )
            
            # POLISH PASS SKIPPED - All requirements moved to single pass prompt
            logger.info("[SINGLE_PASS] Skipping polish pass - all requirements included in generation prompt")
            logger.info(f"[SINGLE_PASS] Final word count: {total_words} words")
            
            # Verify timing is present
            logger.info("[SINGLE_PASS] Verifying section timing:")
            for i, section in enumerate(generated_sections):
                if "start_time" not in section or "end_time" not in section:
                    logger.error(
                        f"[SINGLE_PASS] Section {i+1} MISSING timing! "
                        f"start_time={section.get('start_time', 'MISSING')}, "
                        f"end_time={section.get('end_time', 'MISSING')}"
                    )
                else:
                    logger.info(
                        f"  Section {i+1}: {section['start_time']} - {section['end_time']} ✓"
                    )
            
            return {
                "full_text": full_script,
                "sections": generated_sections,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"[SINGLE_PASS] ❌ FAILED: {str(e)}")
            logger.info("[SINGLE_PASS] Will fall back to section-by-section generation")
            raise
    
    @staticmethod
    def generate_script_with_word_count_strategy(
        outline_text: str,
        script_data: Dict[str, Any],
        user=None,
        save_log: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate full script using word count strategy
        
        NOW WITH ITERATIVE OPTIMIZATION:
        - Tries iterative generation first (generate + expand all sections together)
        - Falls back to section-by-section if iterative fails
        
        Iterative strategy:
        1. Generate ALL sections together (hook + main + conclusion) in first pass
        2. Check total word count
        3. If short (< 90% target): Re-pass ALL sections with expansion (up to 3 iterations)
        4. Return final script with proper timing
        
        This maintains narrative flow, tone consistency, and natural transitions.
        
        Args:
            outline_text: The outline text to generate script from
            script_data: Dictionary containing script parameters
            user: User object for logging (optional)
            save_log: Whether to save run log to database (default: True)
            
        Returns:
            Dictionary with keys: "full_text", "sections", "metadata"
        """
        # TRY ITERATIVE FIRST (generate all sections together, expand if needed)
        logger.info("="*80)
        logger.info("[SCRIPT_GEN] Attempting iterative generation (all sections together with expansion)...")
        
        try:
            # Attempt iterative generation
            result = OpenAIScriptService.generate_script_iterative(
                outline_text, script_data, user, save_log
            )
            
            logger.info(
                f"[SCRIPT_GEN] ✅ Iterative SUCCESS! "
                f"Time: {result['metadata'].get('generation_time', 0)}s, "
                f"Words: {result['metadata'].get('word_count', 0)}"
            )
            return result
            
        except Exception as e:
            logger.warning(f"[SCRIPT_GEN] ⚠️  Iterative generation failed: {str(e)}")
            logger.info("[SCRIPT_GEN] Falling back to section-by-section generation...")
        
        # FALLBACK TO SECTION-BY-SECTION (original method below)
        logger.info("[SECTION_BY_SECTION] Starting traditional section-by-section generation...")
        
        min_length = script_data.get("min_length", 1000)
        max_length = script_data.get("max_length", 5000)
        template_style = script_data.get("template_style", "medium")
        
        try:
            start_time = time.time()
            client = get_openai_client()
            
            # Initialize word count strategy
            wc_strategy = WordCountStrategy(template_style)
            
            # Parse outline to get sections
            import json

            try:
                outline_data = json.loads(outline_text)
                sections = outline_data.get("sections", [])
            except json.JSONDecodeError:
                # Fallback to basic parsing
                sections = [
                    {
                        "title": "Main Content",
                        "description": outline_text,
                        "key_points": [],
                    }
                ]
            
            # Calculate word targets for each section
            num_sections = len(sections)
            word_targets = wc_strategy.calculate_section_word_targets(num_sections)
            
            logger.info(
                f"[WC_STRATEGY] Starting section-based generation: {num_sections} sections, target: {word_targets['total_target']} words"
            )
            
            # Generate script using single conversation thread for natural context flow
            generated_sections = []
            total_tokens_used = 0
            total_words_generated = 0

            # Initialize conversation thread for continuous context
            conversation_messages = []
            
            # Add optimized system message (no full storytelling manual - rules are in section prompts)
            system_message = """You are an expert YouTube script writer. Generate engaging content section by section.

🚨 CRITICAL: STRUCTURAL LABELS ARE GUIDELINES, NOT OUTPUT TEXT
• The prompts contain structural concepts like "Before/Conflict/After", "Open Loops", "Chapter X"
• These are FRAMEWORKS to guide how you structure the narrative
• DO NOT include these labels as literal text in the script output
• Use these concepts internally to shape your writing, but write natural narrative prose
• Example: Don't write "Before: Sarah was happy. Conflict: She lost her job. After: She found meaning."
• Instead: Write a flowing narrative that naturally follows that arc without the labels

🎭 LANGUAGE LEVEL - 6TH-7TH GRADE (MANDATORY):
• A 10-year-old and an 80-year-old should both instantly understand every word
• Use SIMPLE, PLAIN language - no academic or documentary vocabulary
• ALWAYS use contractions: it's, don't, can't, they're, wasn't, couldn't, didn't
• FORBIDDEN WORDS: therefore, however, consequently, thus, nevertheless, phenomenon, essentially, fundamentally, significant, moreover, furthermore, subsequently
• USE INSTEAD: so, but, because, and, that's why, then, next, this means, here's the thing

🔥 CONVERSATIONAL TONE (CRITICAL):
• Write like you're TALKING to a friend, not writing an essay
• Use short, punchy sentences mixed with natural flow
• Start sentences with: "But here's the thing...", "And that's when...", "So...", "Now..."
• Show EMOTION first, facts second: "She couldn't believe it. The test results were..." not "The test results indicated..."
• Create tension in EVERY line - make them curious about the next sentence

🎯 INTROS MUST HOOK IN 2 LINES:
• Line 1: Something shocking, mysterious, or emotionally charged happens
• Line 2: Make them need to know why/what/how
• NO setup, NO context first - jump straight into the moment
• Examples: "The message arrived at 3 AM. Sarah's hands shook as she read it." NOT "Sarah was a normal person until one night..."

SECTION ENDINGS (MANDATORY):
• EVERY section must end with an unanswered question or unresolved tension
• Make them curious about what's next - create a mini-cliffhanger
• Examples: "But that wasn't even the strangest part.", "The question is: why?", "And then everything changed."
• NO neat conclusions - keep the loop open until the very end

TECHNICAL:
• Respond with valid JSON only: {{"content": "your script content here"}}
• WRITE CONCISELY: Use short, punchy sentences. No fluff.
• Build naturally on previous sections, maintaining narrative flow

Remember: Talk like a FRIEND telling a story, not a narrator describing events!"""

            conversation_messages.append({"role": "system", "content": system_message})
            
            for i, section in enumerate(sections):
                section_type = wc_strategy._determine_section_type(i, num_sections)
                
                # Determine word target for this section
                if section_type.value == "hook_intro":
                    section_word_target = word_targets["intro"]
                elif section_type.value == "conclusion":
                    section_word_target = word_targets["conclusion"]
                else:
                    section_word_target = word_targets["main_sections"]
                
                # Build section-specific prompt for conversation
                section_prompt = wc_strategy.build_section_specific_prompt(
                    section_data=section,
                    section_index=i,
                    total_sections=num_sections,
                    word_target=section_word_target,
                    storytelling_manual="",  # No longer needed - filtering happens internally
                )

                # Generate section content using conversation thread
                logger.info(
                    f"[WC_STRATEGY] Generating section {i+1}/{num_sections}: '{section.get('title', 'Untitled')}' ({section_word_target} words) using conversation thread"
                )

                section_content, section_tokens = (
                    OpenAIScriptService._generate_section_with_conversation(
                        conversation_messages,
                        section_prompt,
                        section_word_target,
                        section_type,
                        wc_strategy,
                        client,
                        section_index=i,
                    )
                )
                
                # Validate word count
                is_valid, actual_words, message = wc_strategy.validate_word_count(
                    section_content, section_word_target
                )
                
                logger.info(f"[WC_STRATEGY] Section {i+1}: {message}")
                
                # Expand if needed (more aggressive - trigger at 90% instead of 95%)
                if not is_valid and actual_words < section_word_target * 0.90:
                    logger.info(
                        f"[WC_STRATEGY] Expanding section {i+1} to meet word target using conversation thread"
                    )
                    expansion_strategies = wc_strategy.get_expansion_strategies(
                        section_type
                    )

                    expansion_prompt = f"""🚨 WORD COUNT SHORTFALL - EXPANSION REQUIRED

Your previous section fell SHORT of the word count target. You MUST expand it now.

CURRENT: {actual_words} words
REQUIRED: {section_word_target} words minimum
SHORTFALL: {section_word_target - actual_words} words needed

Current content (TOO SHORT):
{section_content}

🎯 EXPANSION STRATEGIES - Use these to add {section_word_target - actual_words} words:
{chr(10).join(f'• {strategy}' for strategy in expansion_strategies)}

CRITICAL REQUIREMENTS:
1. ADD {section_word_target - actual_words} words to reach the {section_word_target} word target
2. Maintain the same conversational 6th-7th grade tone and style
3. Add depth through examples, sensory details, emotional reactions, and elaboration
4. DO NOT add fluff - add meaningful, engaging content
5. Keep all existing story beats and structure intact
6. Distribute expansion naturally throughout the content
7. Maintain narrative flow with previous sections we've discussed

⚠️  VERIFICATION: After writing, COUNT your words. If still under {section_word_target}, add MORE content.
DO NOT submit until you reach at least {section_word_target} words.

RESPONSE FORMAT: Return JSON object with this exact structure:
{{
    "content": "Your EXPANDED script content here (minimum {section_word_target} words)...",
    "word_count": {section_word_target},
    "expansion_applied": true
}}
"""
                    
                    # Use conversation thread for expansion
                    section_content, expansion_tokens = (
                        OpenAIScriptService._generate_section_with_conversation(
                            conversation_messages,
                            expansion_prompt,
                            section_word_target,
                            section_type,
                            wc_strategy,
                            client,
                            section_index=i,
                        )
                    )
                    section_tokens += expansion_tokens
                    
                    # Validate again
                    is_valid, actual_words, message = wc_strategy.validate_word_count(
                        section_content, section_word_target
                    )
                    logger.info(f"[WC_STRATEGY] After expansion: {message}")
                
                # Store generated section
                generated_sections.append(
                    {
                    "title": section.get("title", f"Section {i+1}"),
                    "content": section_content,
                    "word_count": actual_words,
                    "target_words": section_word_target,
                    "section_type": section_type.value,
                        "is_valid": is_valid,
                    }
                )
                
                total_tokens_used += section_tokens
                total_words_generated += actual_words
            
            # Calculate timing for sections
            generated_sections = wc_strategy.calculate_timing_for_sections(
                generated_sections
            )
            
            # Log timing calculation results
            logger.info(f"[WC_STRATEGY] Calculated timing for {len(generated_sections)} sections")
            for i, section in enumerate(generated_sections):
                logger.info(
                    f"[WC_STRATEGY] Section {i+1}: {section.get('start_time', 'NO_START')} - "
                    f"{section.get('end_time', 'NO_END')} ({section.get('word_count', 0)} words)"
                )
            
            # Combine sections into full script
            full_script_text = OpenAIScriptService._combine_sections(generated_sections)
            
            # Final validation (stricter tolerance for better word count compliance)
            final_is_valid, final_word_count, final_message = (
                wc_strategy.validate_word_count(
                full_script_text, word_targets["total_target"], tolerance=0.05
                )
            )
            
            logger.info(f"[WC_STRATEGY] Final result: {final_message}")
            
            # Format sections for JSON schema response
            formatted_sections = wc_strategy.format_sections_for_json_schema(
                generated_sections
            )
            
            # Verify all sections have timing info
            for i, section in enumerate(formatted_sections):
                if "start_time" not in section or "end_time" not in section:
                    logger.error(
                        f"[WC_STRATEGY] Section {i+1} missing timing: "
                        f"start_time={section.get('start_time', 'MISSING')}, "
                        f"end_time={section.get('end_time', 'MISSING')}"
                    )
            
            generation_time = time.time() - start_time
            
            # Generate metadata
            thread_id = f"wc_strategy_{int(time.time())}"
            run_id = f"wc_run_{int(time.time())}"
            
            metadata = {
                "tokens_used": total_tokens_used,
                "generation_time": generation_time,
                "model": settings.OPENAI_MODEL,
                "assistant_id": "wc-strategy",
                "vector_store_id": "none",
                "thread_id": thread_id,
                "run_id": run_id,
                "file_search_used": False,
                "word_count": final_word_count,
                "length_valid": final_is_valid,
                "strategy_used": "section_based",
                "sections_generated": len(generated_sections),
                "template_style": template_style,
            }
            
            # Save run log
            if save_log:
                OpenAIScriptService._save_run_log(
                    user=user,
                    thread_id=thread_id,
                    run_id=run_id,
                    assistant_id="wc-strategy",
                    tokens_used=total_tokens_used,
                    word_count=final_word_count,
                    file_search_used=False,
                    file_search_snippets=[],
                    run_type="script_generation",
                    generation_time=generation_time,
                    model=settings.OPENAI_MODEL,
                )
            
            # Run final polish pass to validate and fix language/tone issues
            logger.info("[POLISH] Running final polish pass...")
            polished_script, polished_sections = OpenAIScriptService._polish_and_validate_script(
                full_script_text, formatted_sections, script_data, client,
                needs_expansion=False,  # Section-by-section already hits word count
                current_word_count=final_word_count
            )
            
            # Return in the proper JSON schema format
            return {
                "full_text": polished_script,
                "sections": polished_sections,
                "metadata": metadata,
            }
            
        except Exception as e:
            logger.error(f"[WC_STRATEGY] Generation failed: {str(e)}")
            raise

    @staticmethod
    def _generate_single_section_with_quality_validation(
        section_prompt: str, word_target: int, section_type, wc_strategy, client, previous_sections: List[Dict] = None
    ) -> Tuple[str, int]:
        """
        Generate content for a single section with quality validation and iterative improvement
        
        Args:
            section_prompt: The prompt for generating this section
            word_target: Target word count for this section
            section_type: Section type for validation
            wc_strategy: Word count strategy instance
            client: OpenAI client instance
            previous_sections: List of previously generated sections for context
            
        Returns:
            Tuple of (content, tokens_used)
        """
        max_attempts = 2  # Reduced from 3 to 2 attempts
        total_tokens = 0
        
        for attempt in range(max_attempts):
            # Generate content with context awareness
            section_content, tokens_used = OpenAIScriptService._generate_single_section(
                section_prompt, word_target, client, previous_sections=previous_sections
            )
            total_tokens += tokens_used
            
            # Adjust validation strictness by attempt
            if attempt == 0:
                validation_level = "strict"  # First attempt: full validation
            elif attempt == 1:
                validation_level = "normal"  # Retry: critical only
            else:
                validation_level = "minimal"  # Final: blockers only
            
            is_valid, errors = wc_strategy.validate_section_quality(
                section_content, section_type, validation_level=validation_level
            )
            
            if is_valid:
                logger.info(
                    f"[WC_STRATEGY] Section passed quality validation on attempt {attempt + 1}"
                )
                return section_content, total_tokens
            
            # If validation fails and we have attempts left, regenerate with feedback
            if attempt < max_attempts - 1:
                logger.warning(
                    f"[WC_STRATEGY] Section failed quality validation on attempt {attempt + 1}: {errors}"
                )
                
                # Generate improvement guidance
                improvement_guidance = wc_strategy.get_improvement_guidance(errors)
                
                # Create feedback prompt for regeneration
                feedback_prompt = f"""
The previous attempt failed quality validation. Please regenerate with these specific improvements:

QUALITY ISSUES FOUND:
{chr(10).join(f"- {error}" for error in errors)}

SPECIFIC IMPROVEMENTS NEEDED:
{improvement_guidance}

ORIGINAL PROMPT:
{section_prompt}

IMPORTANT: Apply the improvements above while maintaining the original requirements and word count target of {word_target} words.
"""
                
                section_prompt = feedback_prompt
            else:
                logger.warning(
                    f"[WC_STRATEGY] Section failed quality validation after {max_attempts} attempts. Using best attempt."
                )
        
        return section_content, total_tokens

    @staticmethod
    def _generate_section_with_conversation(
        conversation_messages: List[Dict],
        section_prompt: str,
        word_target: int,
        section_type,
        wc_strategy,
        client,
        section_index: int = 0,
    ) -> Tuple[str, int]:
        """
        Generate content for a single section using conversation thread for natural context flow

        Args:
            conversation_messages: List of conversation messages for context
            section_prompt: The prompt for generating this section
            word_target: Target word count for this section
            section_type: Section type for validation
            wc_strategy: Word count strategy instance
            client: OpenAI client instance
            section_index: Index of the section (0-based) for logging purposes
        
        Returns:
            Tuple of (content, tokens_used)
        """
        max_attempts = 2
        total_tokens = 0

        for attempt in range(max_attempts):
            # Add user message to conversation
            current_messages = conversation_messages.copy()
            current_messages.append({"role": "user", "content": section_prompt})

            # Use conservative token limits to avoid truncation and rate limiting
            model_name = settings.OPENAI_MODEL.lower()
            
            api_params = {
                "model": settings.OPENAI_MODEL,
                "messages": current_messages,
                "response_format": {"type": "json_object"},
                "temperature": 1.0,  # Match dashboard setting for longer outputs
            }

            # GPT-5 and o1 models have different parameter requirements
            if "gpt-5" in model_name or "o1" in model_name:
                # GPT-5 needs more tokens - use maximum
                api_params["max_completion_tokens"] = 16384  # Increased to prevent truncation
                max_tokens = 16384
            elif "gpt-4.1" in model_name or "gpt-4-turbo" in model_name:
                # GPT-4.1: Increase to 16K to prevent truncation for large sections
                api_params["max_tokens"] = 16384  # Increased from 8192
                max_tokens = 16384
                logger.info(f"[SECTION] Using max_tokens={max_tokens} for GPT-4.1 (increased to prevent truncation)")
            else:
                # Older GPT-4 models
                api_params["max_tokens"] = 8192  # Increased from 4096
                max_tokens = 8192

            try:
                # Add delay to help with rate limiting
                import time
                time.sleep(1.0)  # Keep 1 second delay to avoid rate limit errors
                
                response = client.chat.completions.create(**api_params)
                
                if not response.choices or len(response.choices) == 0:
                    raise ValueError("OpenAI API returned no choices in response")
                
                choice = response.choices[0]
                if not hasattr(choice, 'message') or not choice.message:
                    raise ValueError("OpenAI API returned invalid choice structure")
                
                # CRITICAL: Check if response was truncated
                finish_reason = choice.finish_reason
                if finish_reason == "length":
                    tokens_used = response.usage.total_tokens if response.usage else 0
                    logger.error(
                        f"[SECTION] ❌ Section {section_index+1} TRUNCATED! finish_reason='length' "
                        f"- Hit {max_tokens} token limit (used {tokens_used} tokens)"
                    )
                    logger.warning(
                        f"[SECTION] Section {section_index+1} is INCOMPLETE due to token limit. "
                        f"Consider reducing word target or increasing max_tokens."
                    )
                    # Continue anyway - might still be usable content
                
                logger.info(f"[SECTION] Section {section_index+1} finish_reason: {finish_reason}")
                    
                section_content_raw = choice.message.content
                if not section_content_raw:
                    logger.error(f"[CONVERSATION] OpenAI API returned empty content for section {section_index+1}")
                    logger.error(f"[CONVERSATION] API Response: {response}")
                    logger.error(f"[CONVERSATION] Model: {settings.OPENAI_MODEL}")
                    logger.error(f"[CONVERSATION] Max tokens: {max_tokens}")
                    raise ValueError("OpenAI API returned empty content")

                tokens_used = response.usage.total_tokens if response.usage else 0
                total_tokens += tokens_used
                
                # Log token usage for monitoring
                token_percentage = (tokens_used / max_tokens) * 100 if max_tokens > 0 else 0
                logger.info(
                    f"[TOKENS] Section {section_index+1} ({section_type.value}): Used {tokens_used}/{max_tokens} tokens "
                    f"({token_percentage:.1f}%) for {word_target} words"
                )
                
                # Warn if approaching token limit (>90%)
                if token_percentage > 90:
                    logger.warning(
                        f"[TOKENS] Section {section_index+1} used {token_percentage:.1f}% of token limit! "
                        f"Risk of truncation. Consider increasing max_tokens from {max_tokens}."
                    )

                # Parse JSON response
                import json
                try:
                    section_data = json.loads(section_content_raw)
                    section_content = section_data.get("content", "")
                    
                    if not section_content:
                        raise ValueError("No content found in JSON response")
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON response: {str(e)}")
                    logger.warning(f"Raw response content: {repr(section_content_raw[:500])}")
                    
                    # Try to extract content from malformed JSON
                    try:
                        # Look for content field in the raw response
                        import re
                        # More flexible pattern to handle truncated JSON
                        content_match = re.search(r'"content":\s*"([^"]*(?:\\.[^"]*)*)', section_content_raw, re.DOTALL)
                        if content_match:
                            # Extract the content and handle potential truncation
                            raw_content = content_match.group(1)
                            # Remove trailing backslashes and incomplete quotes
                            raw_content = raw_content.rstrip('\\').rstrip('"')
                            # Unescape the content
                            section_content = raw_content.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t').replace('\\\\', '\\')
                            # If content seems truncated, try to complete it gracefully
                            if section_content and not section_content.endswith(('.', '!', '?', '"', "'")):
                                # Add a simple completion if it looks truncated
                                section_content = section_content.rstrip() + "..."
                            logger.info("Successfully extracted content from truncated/malformed JSON")
                        else:
                            # Fallback to raw content
                            section_content = section_content_raw
                    except Exception as extract_error:
                        logger.warning(f"Failed to extract content from malformed JSON: {extract_error}")
                        section_content = section_content_raw

                # Add assistant response to conversation for context (but limit context size)
                conversation_messages.append({"role": "user", "content": section_prompt})
                conversation_messages.append({"role": "assistant", "content": section_content})

                # Limit conversation context to prevent token overflow
                # Keep only system message + last 2 exchanges (4 messages total)
                if len(conversation_messages) > 5:  # system + 4 messages = 5 total
                    # Keep system message + last 4 messages
                    conversation_messages = [conversation_messages[0]] + conversation_messages[-4:]
                    logger.info(f"[CONVERSATION] Trimmed conversation context to prevent token overflow (kept last 2 exchanges)")

                # Validate word count and quality
                actual_words = len(section_content.split())
                is_valid, _, message = wc_strategy.validate_word_count(section_content, word_target)
                
                # Additional quality validation
                quality_valid, quality_errors = OpenAIScriptService._validate_section_quality(
                    section_content, section_type, attempt, max_attempts
                )
                
                logger.info(f"[CONVERSATION] Section word count: {actual_words} words (target: {word_target})")
                logger.info(f"[CONVERSATION] Section quality: {'✅ PASS' if quality_valid else '❌ FAIL'}")
                
                if is_valid and quality_valid:
                    logger.info(f"[CONVERSATION] Section generated successfully: {message}")
                    return section_content, total_tokens
                else:
                    # Build comprehensive error message
                    error_parts = []
                    if not is_valid:
                        error_parts.append(f"Word count: {message}")
                    if not quality_valid:
                        error_parts.append(f"Quality: {', '.join(quality_errors)}")
                    
                    error_summary = " | ".join(error_parts)
                    logger.warning(f"[CONVERSATION] Section validation failed: ⚠️ {error_summary}")
                    
                    if attempt < max_attempts - 1:
                        # Add correction request to conversation
                        correction_prompt = OpenAIScriptService._build_correction_prompt(
                            quality_errors, section_content, word_target, not is_valid, actual_words
                        )
                        conversation_messages.append({"role": "user", "content": correction_prompt})
                        continue
                    else:
                        # Final attempt failed, return what we have
                        logger.error(f"[CONVERSATION] Final attempt failed: ⚠️ {error_summary}")
                        return section_content, total_tokens

            except Exception as e:
                logger.error(f"[CONVERSATION] Section generation failed: {str(e)}")
                if attempt < max_attempts - 1:
                    continue
                else:
                    # Fallback to old method if conversation fails
                    logger.warning(f"[CONVERSATION] Falling back to traditional section generation")
                    try:
                        section_content, section_tokens = (
                            OpenAIScriptService._generate_single_section_with_quality_validation(
                                section_prompt,
                                word_target,
                                section_type,
                                wc_strategy,
                                client,
                            )
                        )
                        return section_content, section_tokens
                    except Exception as fallback_error:
                        logger.error(f"[CONVERSATION] Fallback also failed: {str(fallback_error)}")
                        raise

        return section_content, total_tokens

    @staticmethod
    def _generate_single_section(
        section_prompt: str, word_target: int, client, previous_sections: List[Dict] = None
    ) -> Tuple[str, int]:
        """
        Generate content for a single section with word count enforcement and context awareness

        Args:
            section_prompt: The prompt for generating this section
            word_target: Target word count for this section
            client: OpenAI client instance
            previous_sections: List of previously generated sections for context

        Returns:
            Tuple of (content, tokens_used)
        """
        # Use full token limits since this is a separate OpenAI call
        # No need to calculate estimated tokens - use maximum available
        model_name = settings.OPENAI_MODEL.lower()
        
        if "gpt-5" in model_name or "o1" in model_name:
            max_tokens = 8192  # Maximum for GPT-5
        else:
            max_tokens = 4096  # Maximum for GPT-4.1

        # Build context-aware system prompt
        system_content = f"""You are an expert YouTube script writer. CRITICAL: You must generate exactly {word_target} words (±5% tolerance). Word count is MANDATORY and non-negotiable. Count your words before responding. Failure to meet word count will result in regeneration.

🚨 CRITICAL: STRUCTURAL LABELS ARE GUIDELINES, NOT OUTPUT TEXT
- Prompts will reference concepts like "Before/Conflict/After", "Open Loops", "Chapter X"
- These are FRAMEWORKS to guide narrative structure - use them internally
- NEVER write these as literal labels/headings in the script output
- Write natural, flowing narrative prose that embodies these concepts without naming them

📚 LANGUAGE LEVEL - 6TH-7TH GRADE (MANDATORY):
- Every word should be instantly clear to a 10-year-old or 80-year-old
- ALWAYS use contractions: it's, don't, can't, wasn't, they're, couldn't, didn't, wasn't

FORBIDDEN WORDS (Replace these):
❌ therefore, however, consequently, thus, hence → ✅ so, but, because, and, that's why
❌ nevertheless, moreover, furthermore → ✅ but, also, and, plus
❌ phenomenon, subsequently, essentially → ✅ thing, then/next, basically
❌ fundamentally, significant, substantial → ✅ really, big, huge, major
❌ utilize, implement, commence → ✅ use, do, start
❌ indicate, demonstrate, illustrate → ✅ show, prove, mean
❌ ascertain, endeavor, facilitate → ✅ find out, try, help

TALK LIKE THIS:
✅ "So here's what happened..."
✅ "But that's not the crazy part..."
✅ "And that's when things got weird..."
✅ "It didn't make sense..."
- Talk like a friend telling a story over coffee, not writing an essay

SECTION ENDINGS (MANDATORY):
- END every section with curiosity or unresolved tension
- Create mini-cliffhangers: "But that's not even the weird part.", "And then it got worse.", "The question is: why?"
- Make them need to keep watching

CONTEXT AWARENESS: You are writing a section of a larger script. Use the previous sections as context to:
- Maintain narrative flow and emotional continuity
- Build on previous content naturally
- Avoid repetition of phrases or structures
- Create smooth transitions with simple language
- Keep the conversational tone consistent"""

        # Add previous sections context if available
        if previous_sections and len(previous_sections) > 0:
            context_summary = "\n\nPREVIOUS SECTIONS CONTEXT:\n"
            for i, prev_section in enumerate(previous_sections[-3:]):  # Last 3 sections for context
                context_summary += f"Section {i+1}: {prev_section.get('content', '')[:200]}...\n"
            system_content += context_summary

        model_name = settings.OPENAI_MODEL.lower()
        api_params = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": system_content,
                },
                {"role": "user", "content": section_prompt},
            ],
            "response_format": {"type": "json_object"},
        }

        # GPT-5 and o1 models have different parameter requirements
        if "gpt-5" in model_name or "o1" in model_name:
            # GPT-5 needs more tokens - multiply by 2
            api_params["max_completion_tokens"] = max_tokens * 2
        else:
            api_params["max_tokens"] = max_tokens
            api_params["temperature"] = 0.7

        response = client.chat.completions.create(**api_params)
        
        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0
        
        # Parse JSON response to extract content
        try:
            import json

            section_data = json.loads(content)
            if isinstance(section_data, dict) and "content" in section_data:
                return section_data["content"], tokens_used
            else:
                logger.warning(
                    f"[WC_STRATEGY] Invalid JSON structure in section response: {content[:200]}..."
                )
                return content, tokens_used
        except json.JSONDecodeError as e:
            logger.warning(
                f"[WC_STRATEGY] Failed to parse JSON response: {str(e)}, using raw content"
            )
            logger.warning(f"[WC_STRATEGY] Raw response content: {repr(content[:500])}")
            
            # Try to extract content from malformed JSON
            try:
                # Look for content field in the raw response
                import re
                # More flexible pattern to handle truncated JSON
                content_match = re.search(r'"content":\s*"([^"]*(?:\\.[^"]*)*)', content, re.DOTALL)
                if content_match:
                    # Extract the content and handle potential truncation
                    raw_content = content_match.group(1)
                    # Remove trailing backslashes and incomplete quotes
                    raw_content = raw_content.rstrip('\\').rstrip('"')
                    # Unescape the content
                    extracted_content = raw_content.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t').replace('\\\\', '\\')
                    logger.info("[WC_STRATEGY] Successfully extracted content from truncated/malformed JSON")
                    return extracted_content, tokens_used
                else:
                    # Fallback to raw content
                    return content, tokens_used
            except Exception as extract_error:
                logger.warning(f"[WC_STRATEGY] Failed to extract content from malformed JSON: {extract_error}")
                return content, tokens_used

    @staticmethod
    def _combine_sections(sections: List[Dict]) -> str:
        """
        Combine individual sections into a cohesive full script
        
        Args:
            sections: List of generated sections with content
            
        Returns:
            Combined script text
        """
        combined_parts = []
        
        for section in sections:
            title = section["title"]
            content = section["content"]
            
            # Add section header
            combined_parts.append(f"=== {title.upper()} ===")
            combined_parts.append("")
            
            # Add section content
            combined_parts.append(content)
            combined_parts.append("")
        
        return "\n".join(combined_parts)

    @staticmethod
    def analyze_image_with_assistant(
        image_file=None, 
        image_url=None,
        user=None,
        save_log: bool = True,
    ) -> Tuple[str, str]:
        """
        Analyze an image using OpenAI Chat Completions API with Vision capabilities
        
        Args:
            image_file: Django UploadedFile object (optional)
            image_url: URL of the image to analyze (optional)
            user: User object for logging (optional)
            save_log: Whether to save run log to database (default: True)
        """
        try:
            start_time = time.time()
            client = get_openai_client()

            # Prepare image for analysis
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

            # Build system and user prompts
            storytelling_manual = format_storytelling_manual_for_prompt()
            
            system_prompt = f"""You are an expert YouTube content creator and image analyst. Your task is to analyze images and create engaging YouTube content concepts.

Key principles:
- Create catchy, clickable titles under 60 characters
- Provide detailed descriptions that can be used for script generation
- Focus on storytelling elements and viewer engagement
- Consider YouTube best practices for thumbnails and titles

=== TUBEGENIUS STORYTELLING MANUAL ===
{storytelling_manual}

Use the opening strategies and storytelling principles to analyze images and create compelling content concepts. Focus on transformation arcs, emotional triggers, and storytelling elements that will engage viewers."""

            user_prompt = """Analyze this image and provide:
1. A catchy, engaging YouTube video title (under 60 characters)
2. A detailed description of what's happening in the image that could be used for script generation

Format your response as:
TITLE: [your title here]
DESCRIPTION: [your description here]

Apply storytelling rules and hook techniques for creating an engaging title and description.

Note: Please provide your response in a clear, structured format (not JSON)."""

            # Use Chat Completions API with Vision
            model_name = settings.OPENAI_MODEL.lower()
            api_params = {
                "model": settings.OPENAI_MODEL,  # GPT-4o and GPT-5 have vision capabilities
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url_for_openai},
                            },
                        ],
                    },
                ],
            }

            # GPT-5 and o1 models have different parameter requirements
            if "gpt-5" in model_name or "o1" in model_name:
                api_params["max_completion_tokens"] = 8192  # Maximum for GPT-5
            else:
                api_params["max_tokens"] = 4096  # Maximum for GPT-4.1
                api_params["temperature"] = 0.7

            response = client.chat.completions.create(**api_params)

            logger.info(
                "[IMAGE_ANALYSIS] Generated analysis using Chat Completions API"
            )

            # Extract content and token usage with validation
            if not response.choices or len(response.choices) == 0:
                raise ValueError("OpenAI API returned no choices in response")
            
            choice = response.choices[0]
            if not hasattr(choice, "message") or not choice.message:
                raise ValueError("OpenAI API returned invalid choice structure")
                
            content = choice.message.content
            if not content:
                raise ValueError(
                    "OpenAI API returned empty content - this may indicate rate limiting or API error"
                )
                
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            generation_time = time.time() - start_time
            
            logger.debug(
                f"[IMAGE_ANALYSIS] OpenAI API response validated - content length: {len(content)}, tokens: {tokens_used}"
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
            
            # Calculate word count
            word_count = len(content.split())

            # Generate unique identifiers for logging
            thread_id = f"chat_{int(time.time())}"
            run_id = f"run_{int(time.time())}"

            # Save run log to database
            if save_log:
                OpenAIScriptService._save_run_log(
                    user=user,
                    thread_id=thread_id,
                    run_id=run_id,
                    assistant_id="chat-completions",
                    tokens_used=tokens_used,
                    word_count=word_count,
                    file_search_used=False,
                    file_search_snippets=[],
                    run_type="image_analysis",
                    generation_time=generation_time,
                    model=settings.OPENAI_MODEL,
                )

            return title, description

        except Exception as e:
            logger.error(f"Chat completions image analysis failed: {str(e)}")
            return "Image Analysis", "An image was provided for analysis."
    
    @staticmethod
    def _save_run_log(
        user,
        thread_id: str,
        run_id: str,
        assistant_id: str,
        tokens_used: int,
        word_count: int,
        file_search_used: bool,
        file_search_snippets: List[Dict],
        run_type: str,
        generation_time: float,
        model: str = "gpt-4",
        status: str = "completed",
        script_outline=None,
        full_script=None,
        script_title=None,
    ):
        """
        Save OpenAI run log to database
        """
        try:
            from scripts.models import OpenAIRunLog
            
            run_log = OpenAIRunLog.objects.create(
                user=user,
                thread_id=thread_id,
                run_id=run_id,
                assistant_id=assistant_id,
                tokens_used=tokens_used,
                word_count=word_count,
                file_search_used=file_search_used,
                file_search_snippets=file_search_snippets,
                run_type=run_type,
                generation_time=generation_time,
                model=model,
                status=status,
                script_outline=script_outline,
                full_script=full_script,
                script_title=script_title,
            )
            
            logger.info(f"Saved run log {run_log.uuid} for run_id {run_id}")
            return run_log
            
        except Exception as e:
            logger.error(f"Failed to save run log: {str(e)}")
            return None

    @staticmethod
    def _validate_word_count(
        content: str, min_length: int, max_length: int, content_type: str = "content"
    ) -> Tuple[bool, int]:
        """
        Validate if content meets word count requirements
        
        Returns:
            Tuple of (is_valid, actual_word_count)
        """
        word_count = len(content.split())
        is_valid = min_length <= word_count <= max_length
        
        # Only log validation failures to reduce noise
        if not is_valid:
            diff = (
                min_length - word_count
                if word_count < min_length
                else word_count - max_length
            )
            logger.debug(
                f"[LENGTH] {content_type}: {word_count}w ({'short' if word_count < min_length else 'over'} by {diff}w)"
            )
        
        return is_valid, word_count

    @staticmethod
    def _polish_and_validate_script(
        full_script: str,
        sections: List[Dict],
        script_data: Dict[str, Any],
        client,
        needs_expansion: bool = False,
        current_word_count: int = 0
    ) -> Tuple[str, List[Dict]]:
        """
        Final polish pass to validate and fix language/tone issues
        
        NOTE: This pass does NOT expand word count anymore - that's handled during section generation.
        
        Checks for:
        - Forbidden formal words (therefore, however, consequently, etc.)
        - Missing contractions (it is -> it's, do not -> don't)
        - Weak hook (no action verbs in first 2 sentences)
        - Weak section endings (no curiosity hooks)
        - Conversational tone and language level
        
        Args:
            needs_expansion: Ignored - kept for backward compatibility
            current_word_count: Current word count of the script
        
        Returns polished script and sections (word count unchanged)
        """
        import re
        
        logger.info("[POLISH] Analyzing script for language/tone issues (NOT expanding word count)...")
        
        # Log current word count for reference only
        min_length = script_data.get("min_length", 1000)
        if current_word_count > 0 and current_word_count < min_length:
            logger.info(
                f"[POLISH] Script word count: {current_word_count}/{min_length} words "
                f"(accepting as-is, no expansion in polish pass)"
            )
        
        # Define forbidden words and their replacements
        FORBIDDEN_WORDS = {
            "therefore": "so",
            "however": "but",
            "consequently": "so",
            "thus": "so",
            "nevertheless": "but",
            "phenomenon": "thing",
            "essentially": "",
            "fundamentally": "",
            "significant": "important",
            "moreover": "and",
            "furthermore": "also",
            "subsequently": "then",
        }
        
        # Check for issues
        issues = []
        
        # 1. Check for forbidden words
        forbidden_found = []
        for word, replacement in FORBIDDEN_WORDS.items():
            pattern = r'\b' + word + r'\b'
            if re.search(pattern, full_script, re.IGNORECASE):
                forbidden_found.append(word)
        
        if forbidden_found:
            issues.append(f"Found forbidden formal words: {', '.join(forbidden_found)}")
        
        # 2. Check for missing contractions
        contraction_patterns = [
            (r"\bit is\b", "it's"),
            (r"\bdo not\b", "don't"),
            (r"\bdoes not\b", "doesn't"),
            (r"\bcannot\b", "can't"),
            (r"\bcould not\b", "couldn't"),
            (r"\bwould not\b", "wouldn't"),
            (r"\bshould not\b", "shouldn't"),
            (r"\bdid not\b", "didn't"),
            (r"\bwas not\b", "wasn't"),
            (r"\bwere not\b", "weren't"),
            (r"\bare not\b", "aren't"),
            (r"\bwill not\b", "won't"),
            (r"\bthey are\b", "they're"),
            (r"\bwe are\b", "we're"),
            (r"\byou are\b", "you're"),
        ]
        
        missing_contractions = 0
        for pattern, _ in contraction_patterns:
            matches = re.findall(pattern, full_script, re.IGNORECASE)
            missing_contractions += len(matches)
        
        if missing_contractions > 3:  # Allow a few for emphasis
            issues.append(f"Found {missing_contractions} missing contractions")
        
        # 3. Check hook strength (first section)
        if sections and len(sections) > 0:
            first_section = sections[0]
            content = first_section.get("content", "")
            sentences = re.split(r'[.!?]+', content)
            if len(sentences) >= 2:
                first_two = ' '.join(sentences[:2])
                # Check for action verbs
                action_verbs = ['see', 'watch', 'hear', 'look', 'imagine', 'picture', 'feel', 'discover', 'witness', 'experience']
                has_action = any(verb in first_two.lower() for verb in action_verbs)
                if not has_action:
                    issues.append("Hook lacks action verbs in first 2 sentences")
        
        # 4. Check section endings for curiosity hooks
        weak_endings = 0
        curiosity_words = ['but', 'why', 'how', 'what', 'question', 'wonder', '?', 'next', 'however', 'strange', 'mystery']
        
        for i, section in enumerate(sections):
            content = section.get("content", "")
            # Get last 2 sentences
            sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
            if len(sentences) >= 2:
                last_two = ' '.join(sentences[-2:]).lower()
                has_curiosity = any(word in last_two for word in curiosity_words)
                if not has_curiosity and i < len(sections) - 1:  # Don't check conclusion
                    weak_endings += 1
        
        if weak_endings > 0:
            issues.append(f"{weak_endings} sections have weak endings (no curiosity hooks)")
        
        # NOTE: Word count checking/expansion removed - handled during section generation
        # Polish pass only fixes language and tone issues
        
        # Log issues found
        if issues:
            logger.warning(f"[POLISH] Found {len(issues)} issues:")
            for issue in issues:
                logger.warning(f"[POLISH]   - {issue}")
            
            # If there are issues, run a polish API call to fix them
            logger.info("[POLISH] Requesting polish/fix from AI (language & tone only, no word count changes)...")
            
            polish_prompt = f"""Review and polish this YouTube script to fix language and tone issues ONLY.

🚨 CRITICAL WORD COUNT RULE: 
- Original script has {current_word_count} words
- Your polished script MUST have {current_word_count} words (±10 words tolerance)
- DO NOT shorten, expand, or change the length
- Use code generation to verify word count before submitting
- This is a POLISH pass for language/tone only, NOT a rewrite

ISSUES TO FIX:
{chr(10).join(f'- {issue}' for issue in issues)}

POLISH REQUIREMENTS:
1. Replace formal words with conversational alternatives (therefore→so, however→but)
2. Add contractions everywhere (it is→it's, do not→don't)  
3. Strengthen hook (first sentence needs action verb)
4. Fix weak section endings (add curiosity hooks)
5. Maintain 6th-7th grade reading level
6. Keep conversational tone

🔍 WORD COUNT VERIFICATION (MANDATORY):
Before submitting, use code generation to verify your polished script:
- Split the polished content by whitespace
- Count the words
- Confirm it's within {current_word_count - 10} to {current_word_count + 10} words
- If it's shorter, ADD back words to reach {current_word_count}
- If it's longer, trim minimally to reach {current_word_count}

ORIGINAL SCRIPT ({current_word_count} words):
{full_script}

Return polished script with SAME word count. Only fix language/tone - keep all content.

RESPONSE FORMAT: Return JSON with this structure:
{{
    "polished_script": "Complete polished script here...",
    "sections": [
        {{"content": "Polished section 1 content..."}}
        {{"content": "Polished section 2 content..."}}
        ...
    ]
}}"""

            try:
                response = client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert script editor specializing in conversational, engaging YouTube content."},
                        {"role": "user", "content": polish_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3,  # Lower temperature for consistency
                    max_tokens=16384
                )
                
                import json
                polish_response = json.loads(response.choices[0].message.content)
                
                polished_script = polish_response.get("polished_script", full_script)
                polished_section_contents = polish_response.get("sections", [])
                
                # Update sections with polished content while preserving all other fields
                if polished_section_contents and len(polished_section_contents) == len(sections):
                    for i, section in enumerate(sections):
                        # Only update content, preserve start_time, end_time, validator_compliance, etc.
                        section["content"] = polished_section_contents[i].get("content", section.get("content", ""))
                        # Explicitly ensure these fields are preserved
                        if "start_time" not in section:
                            logger.warning(f"[POLISH] Section {i+1} missing start_time after polish")
                        if "end_time" not in section:
                            logger.warning(f"[POLISH] Section {i+1} missing end_time after polish")
                
                # Check if expansion was successful
                if needs_expansion:
                    final_word_count = len(polished_script.split())
                    if final_word_count >= min_length:
                        logger.info(
                            f"[POLISH] ✅ Script polished and expanded successfully: "
                            f"{current_word_count} → {final_word_count} words (target: {min_length}+)"
                        )
                    else:
                        logger.warning(
                            f"[POLISH] ⚠️ Expansion fell short: {current_word_count} → {final_word_count} words "
                            f"(target: {min_length}), but still improved"
                        )
                else:
                    logger.info(f"[POLISH] ✅ Script polished successfully")
                
                return polished_script, sections
                
            except Exception as e:
                logger.error(f"[POLISH] Polish API call failed: {str(e)}")
                logger.info("[POLISH] Returning original script")
                return full_script, sections
        
        else:
            logger.info("[POLISH] ✅ No issues found - script looks good!")
            return full_script, sections

    @staticmethod
    def _build_basic_outline_system_prompt() -> str:
        """Build minimal system prompt for basic outline generation"""
        return """You are an expert YouTube script writer. Create detailed outlines that serve as blueprints for engaging YouTube videos.

CRITICAL: You MUST respond with valid JSON only.

JSON SCHEMA:
{
  "sections": [
    {
      "title": "Section Title",
      "description": "Detailed 80-150 word description of what to cover and how to approach it",
      "key_points": [
        "Specific actionable point 1",
        "Specific actionable point 2",
        "Specific actionable point 3"
      ],
      "timing": "Estimated duration (e.g., '2-3 minutes')",
      "transition": "How to transition to next section",
      "content": "Specific examples, stories, or techniques to include"
    }
  ],
  "section_order": [0, 1, 2, 3, 4]
}

Key principles:
- Create outlines that are detailed enough to generate full scripts
- Focus on viewer engagement and storytelling
- Structure content for maximum retention
- Include specific examples, stories, and techniques
- Ensure each section has clear guidance for script writers

RESPONSE FORMAT: Return ONLY valid JSON matching the schema above. No markdown, no explanations, no additional text."""

    @staticmethod
    def _build_outline_system_prompt() -> str:
        """Build system prompt for outline generation using Chat Completions"""
        storytelling_manual = format_storytelling_manual_for_prompt()
        
        return f"""You are an expert YouTube script writer and content strategist. Your task is to create detailed, actionable outlines that serve as blueprints for engaging YouTube videos.

 CRITICAL: You MUST respond with valid JSON only. The API is configured to enforce JSON output format.

 MANDATORY VALIDATOR ENFORCEMENT - FIRST TRY SUCCESS REQUIRED 🚨
Before creating any outline, you MUST validate against these critical requirements:

S1 HOOK VALIDATORS (MANDATORY - NO EXCEPTIONS):
- Hook duration MUST be ≤30 seconds (hard cap: 60s when justified)
- Hook MUST contain action verb in first 1-2 sentences
- Hook MUST be 3-6 sentence micro-scene with filmable action
- Hook MUST pivot to chronology within 60 seconds
- NO vague language like "high-stakes moment" without concrete dramatization
- FORBIDDEN STARTERS: "Imagine", "Picture", "Let me", "Let's", "Welcome", "Today we"

S2 OPEN LOOPS VALIDATORS (MANDATORY - NO EXCEPTIONS):
- MUST state 2-3 specific high-value questions in hook
- MUST include transformation statement: "Learn X to achieve Y"
- MUST specify which loops will be closed in later sections
- NO generic "create curiosity by hinting" - be specific

S6 VALUE DELIVERY VALIDATORS (MANDATORY - NO EXCEPTIONS):
- For listicles/tutorials: First value point MUST start within 10 seconds of hook end
- Hook MUST be ≤30 seconds (exceptions explicitly justified)
- NO standalone 1-2 minute opening sections
- Get to main content FAST

FRAMEWORK REQUIREMENTS (MANDATORY - NO EXCEPTIONS):
- P02: Include specific sensory details in each section
- P03: Map causal connectors between sections
- P05/P11: Include emotional beats and stakes
- P17: Add editor cues/visual plans
- BONUS-02: End chapters with cliffhangers/unresolved threads

VALIDATION CHECKLIST (MANDATORY):
□ Hook starts with action verb/noun+action
□ Hook ≤75 words (30 seconds)
□ 2-3 specific questions in first 60 seconds
□ Transformation statement included
□ First value point within 10s for tutorials
□ Sensory details included
□ Emotional beats planned
□ Visual cues described

FAILURE TO MEET ANY REQUIREMENT WILL RESULT IN REGENERATION!

JSON SCHEMA REQUIREMENTS:
{{
  "sections": [
    {{
      "title": "Section Title",
      "description": "Detailed 80-150 word description of what to cover and how to approach it",
      "key_points": [
        "Specific actionable point 1",
        "Specific actionable point 2",
        "Specific actionable point 3"
      ],
      "timing": "Estimated duration (e.g., '2-3 minutes')",
      "transition": "How to transition to next section",
      "content": "Specific examples, stories, or techniques to include",
      "validators_compliance": {{
        "hook_duration": "≤30s",
        "action_verbs": "Present in opening",
        "open_loops": "2-3 specific questions listed",
        "value_delivery_speed": "First point within 10s of hook end",
        "sensory_details": "Concrete, filmable details included",
        "causal_connectors": "Therefore/but/because links mapped",
        "emotional_beats": "Stakes and consequences defined",
        "visual_cues": "Editor notes included",
        "cliffhangers": "Unresolved threads at section ends"
      }}
    }}
  ],
  "section_order": [0, 1, 2, 3, 4],
  "validator_compliance_check": {{
    "s1_hook_structure": "PASS/FAIL with specific violations",
    "s2_open_loops": "PASS/FAIL with specific violations", 
    "s6_value_delivery": "PASS/FAIL with specific violations",
    "framework_gaps": "List of missing P02, P03, P05, P11, P17, BONUS-02 elements"
  }}
}}

VALIDATION PROCESS:
1. Create outline structure
2. Check each validator against S1, S2, S6 requirements
3. Verify framework elements (P02, P03, P05, P11, P17, BONUS-02)
4. If ANY validator fails, REVISE the outline until ALL pass
5. Include validator_compliance_check in JSON response

{EXAMPLE_COMPLIANT_HOOKS}

Then immediately: First value point at the 30-second mark.

Key principles:
- Create outlines that are detailed enough to generate full scripts
- Focus on viewer engagement and storytelling
- Structure content for maximum retention
- Include specific examples, stories, and techniques
- Ensure each section has clear guidance for script writers
- ENFORCE ALL VALIDATORS - NO EXCEPTIONS

Your outlines should be comprehensive roadmaps that transform into compelling video content.

=== TUBEGENIUS STORYTELLING MANUAL ===
{storytelling_manual}

Use these proven storytelling principles to create outlines that will generate highly engaging, retention-focused YouTube scripts. Apply the opening strategies, core principles, and implementation checklist to ensure your outlines produce compelling content.

CRITICAL: Every outline MUST pass ALL validators. If you cannot create a compliant outline, explain why in the validator_compliance_check section.

RESPONSE FORMAT: Return ONLY valid JSON matching the schema above. No markdown, no explanations, no additional text."""

    @staticmethod
    def _build_basic_outline_user_prompt(script_data: Dict[str, Any]) -> str:
        """Build minimal user prompt for basic outline generation"""
        tones = script_data.get("tones", ["informative"])
        template_style = script_data.get("template_style", "medium")
        description = script_data.get("description", "")
        min_length = script_data.get("min_length", 0)
        max_length = script_data.get("max_length", 1000)

        # Convert tone IDs to names if needed
        if tones and isinstance(tones[0], int):
            from scripts.models import Tone
            tone_objects = Tone.objects.filter(id__in=tones)
            tones = [tone.name for tone in tone_objects]
        
        # Convert template_style ID to name if needed
        if isinstance(template_style, int):
            from scripts.models import TemplateStyle
            try:
                style_obj = TemplateStyle.objects.get(id=template_style)
                template_style = style_obj.name
            except TemplateStyle.DoesNotExist:
                template_style = "medium"

        tone_text = (
            f"Tones: {', '.join(tones)}" if len(tones) > 1 else f"Tone: {tones[0]}"
        )

        return f"""Generate DETAILED outline in JSON for:

Topic: {description} | {tone_text} | Style: {template_style} | Target: {min_length:,}-{max_length:,}w script

REQUIREMENTS:
• Each section: 80-150w description + 5-8 detailed key point sentences
• Include specific examples, stories, techniques to use
• Add timing + transition guidance
• Outline depth = script length (sparse = FAILS, detailed = success)

CRITICAL: Return ONLY valid JSON matching the exact schema provided in the system prompt."""

    @staticmethod
    def _build_validator_enhancement_system_prompt() -> str:
        """Build system prompt for validator enhancement"""
        return """You are an expert YouTube script validator. Your task is to enhance an existing outline with validator compliance checks.

CRITICAL: You MUST respond with valid JSON only.

ENHANCED JSON SCHEMA:
{
  "sections": [
    {
      "title": "Section Title",
      "description": "Detailed 80-150 word description of what to cover and how to approach it",
      "key_points": [
        "Specific actionable point 1",
        "Specific actionable point 2",
        "Specific actionable point 3"
      ],
      "timing": "Estimated duration (e.g., '2-3 minutes')",
      "transition": "How to transition to next section",
      "content": "Specific examples, stories, or techniques to include",
      "validators_compliance": {
        "hook_duration": "≤30s",
        "action_verbs": "Present in opening",
        "open_loops": "2-3 specific questions listed",
        "value_delivery_speed": "First point within 10s of hook end",
        "sensory_details": "Concrete, filmable details included",
        "causal_connectors": "Therefore/but/because links mapped",
        "emotional_beats": "Stakes and consequences defined",
        "visual_cues": "Editor notes included",
        "cliffhangers": "Unresolved threads at section ends"
      }
    }
  ],
  "section_order": [0, 1, 2, 3, 4],
  "validator_compliance_check": {
    "s1_hook_structure": "PASS/FAIL with specific violations",
    "s2_open_loops": "PASS/FAIL with specific violations", 
    "s6_value_delivery": "PASS/FAIL with specific violations",
    "framework_gaps": "List of missing P02, P03, P05, P11, P17, BONUS-02 elements"
  }
}

RESPONSE FORMAT: Return ONLY valid JSON matching the enhanced schema above. No markdown, no explanations, no additional text."""

    @staticmethod
    def _build_validator_enhancement_user_prompt(basic_outline: str) -> str:
        """Build user prompt for validator enhancement"""
        return f"""Enhance this basic outline with validator compliance checks:

BASIC OUTLINE:
{basic_outline}

VALIDATOR REQUIREMENTS:
S1 HOOK VALIDATORS (MANDATORY):
- Hook duration MUST be ≤30 seconds (hard cap: 60s when justified)
- Hook MUST contain action verb in first 1-2 sentences
- Hook MUST be 3-6 sentence micro-scene with filmable action
- Hook MUST pivot to chronology within 60 seconds
- NO vague language like "high-stakes moment" without concrete dramatization
- FORBIDDEN STARTERS: "Imagine", "Picture", "Let me", "Let's", "Welcome", "Today we"

S2 OPEN LOOPS VALIDATORS (MANDATORY):
- MUST state 2-3 specific high-value questions in hook
- MUST include transformation statement: "Learn X to achieve Y"
- MUST specify which loops will be closed in later sections
- NO generic "create curiosity by hinting" - be specific

S6 VALUE DELIVERY VALIDATORS (MANDATORY):
- For listicles/tutorials: First value point MUST start within 10 seconds of hook end
- Hook MUST be ≤30 seconds (exceptions explicitly justified)
- NO standalone 1-2 minute opening sections
- Get to main content FAST

FRAMEWORK REQUIREMENTS (MANDATORY):
- P02: Include specific sensory details in each section
- P03: Map causal connectors between sections
- P05/P11: Include emotional beats and stakes
- P17: Add editor cues/visual plans
- BONUS-02: End chapters with cliffhangers/unresolved threads

TASK: Enhance the basic outline by adding validators_compliance fields to each section and validator_compliance_check to the root object.

CRITICAL: Return ONLY valid JSON matching the enhanced schema provided in the system prompt."""

    @staticmethod
    def _build_hook_system_prompt() -> str:
        """Build minimal system prompt for hook section generation"""
        return """You are an expert YouTube script writer specializing in hook creation. Create compelling opening sections that immediately capture viewer attention.

CRITICAL: You MUST respond with valid JSON only.

🚨 IMPORTANT: Structural concepts mentioned below (like "open loops") are GUIDELINES for how to structure your writing. DO NOT include them as literal labels/headings in the script. Write natural narrative that embodies these concepts.

HOOK VALIDATORS (MANDATORY - NO EXCEPTIONS):
- Hook duration MUST be ≤30 seconds (hard cap: 60s when justified)
- Hook MUST contain action verb in first 1-2 sentences
- Hook MUST be 3-6 sentence micro-scene with filmable action
- Hook MUST pivot to main content within 60 seconds
- NO vague language like "high-stakes moment" without concrete dramatization
- FORBIDDEN STARTERS: "Imagine", "Picture", "Let me", "Let's", "Welcome", "Today we"

OPEN LOOPS VALIDATORS (MANDATORY - NO EXCEPTIONS):
- MUST state 2-3 specific high-value questions in hook
- MUST include transformation statement: "Learn X to achieve Y"
- MUST specify which loops will be closed in later sections
- NO generic "create curiosity by hinting" - be specific

VALUE DELIVERY VALIDATORS (MANDATORY - NO EXCEPTIONS):
- For tutorials/listicles: First value point MUST start within 10 seconds of hook end
- Hook MUST be ≤30 seconds (exceptions explicitly justified)
- NO standalone 1-2 minute opening sections
- Get to main content FAST

JSON SCHEMA:
{
  "content": "Your hook script content here...",
  "word_count": 450,
  "section_type": "hook_intro",
  "validators_compliance": {
    "hook_duration": "≤30s",
    "action_verbs": "Present in opening",
    "open_loops": "2-3 specific questions listed",
    "value_delivery_speed": "First point within 10s of hook end"
  }
}

RESPONSE FORMAT: Return ONLY valid JSON matching the schema above. No markdown, no explanations, no additional text."""

    @staticmethod
    def _build_main_content_system_prompt() -> str:
        """Build minimal system prompt for main content section generation"""
        return """You are an expert YouTube script writer specializing in main content creation. Create engaging, value-packed sections that deliver on the hook's promises.

CRITICAL: You MUST respond with valid JSON only.

🚨 IMPORTANT: Structural concepts mentioned below are GUIDELINES for narrative structure. Use them internally to shape your writing, but don't include them as literal labels in the script output.

MAIN CONTENT REQUIREMENTS (MANDATORY):
- Deliver specific value points promised in the hook
- Use storytelling techniques to maintain engagement
- Include concrete examples and actionable advice
- Maintain conversational, YouTube-friendly tone
- Build on previous sections naturally

FRAMEWORK REQUIREMENTS (MANDATORY):
- P02: Include specific sensory details in each section
- P03: Map causal connectors between sections
- P05/P11: Include emotional beats and stakes
- P07: Simplify - cut anything that doesn't advance the main story
- P09: Remove jargon and clichés - use plain language
- P10: Write at high-school reading level - conversational, not literary
- P13: Concision - say the same thing with fewer words
- P17: Write with visuals in mind - add editor cues and visual-friendly phrasing
- BONUS-02: End chapters with cliffhangers/unresolved threads

JSON SCHEMA:
{
  "content": "Your main content script here...",
  "word_count": 450,
  "section_type": "main_content",
  "validators_compliance": {
    "sensory_details": "Concrete, filmable details included",
    "causal_connectors": "Therefore/but/because links present",
    "emotional_beats": "Stakes and consequences defined",
    "visual_cues": "Editor notes included",
    "cliffhangers": "Unresolved threads at section ends",
    "simplified": "No tangents or unnecessary details",
    "plain_language": "No jargon or clichés",
    "conversational": "High-school reading level",
    "concise": "No verbose constructions"
  }
}

RESPONSE FORMAT: Return ONLY valid JSON matching the schema above. No markdown, no explanations, no additional text."""

    @staticmethod
    def _build_conclusion_system_prompt() -> str:
        """Build minimal system prompt for conclusion section generation"""
        return """You are an expert YouTube script writer specializing in conclusion creation. Create compelling closing sections that wrap up the content and drive action.

CRITICAL: You MUST respond with valid JSON only.

🚨 IMPORTANT: Structural concepts like "open loops" are GUIDELINES. Use them to shape your writing, but don't include them as literal labels in the script output.

CONCLUSION REQUIREMENTS (MANDATORY):
- Close all open loops established in the hook
- Provide clear next steps or call-to-action
- Reinforce the main value proposition
- End with a strong, memorable statement
- Include cliffhangers for future content (BONUS-02)

FRAMEWORK REQUIREMENTS (MANDATORY):
- P02: Include specific sensory details
- P03: Use causal connectors (therefore, but, because)
- P05/P11: Include emotional beats and stakes
- P17: Add editor cues/visual plans
- BONUS-02: End with cliffhangers/unresolved threads

JSON SCHEMA:
{
  "content": "Your conclusion script content here...",
  "word_count": 450,
  "section_type": "conclusion",
  "validators_compliance": {
    "open_loops_closed": "All hook questions answered",
    "call_to_action": "Clear next steps provided",
    "value_reinforced": "Main proposition restated",
    "cliffhangers": "Future content teased"
  }
}

RESPONSE FORMAT: Return ONLY valid JSON matching the schema above. No markdown, no explanations, no additional text."""

    @staticmethod
    def generate_script_section_specific(
        outline_text: str,
        script_data: Dict[str, Any],
        user=None,
        save_log: bool = True,
    ) -> Tuple[str, List[Dict], Dict[str, Any]]:
        """
        Generate script using section-specific prompts with only relevant rules for each section
        
        Args:
            outline_text: The outline text to generate script from
            script_data: Dictionary containing script parameters
            user: User object for logging (optional)
            save_log: Whether to save run log to database (default: True)
        """
        start_time = time.time()
        try:
            client = get_openai_client()
            
            # Parse outline to get sections
            outline_data = OpenAIScriptService._parse_outline_structure(outline_text)
            sections = outline_data.get("sections", [])
            
            if not sections:
                raise ValueError("No sections found in outline")
            
            print("=" * 80)
            print(f"[SCRIPT_SECTION_SPECIFIC] Generating script with {len(sections)} sections using model: {settings.OPENAI_MODEL}")
            
            # Calculate word targets for each section
            min_length = script_data.get("min_length", 1000)
            max_length = script_data.get("max_length", 5000)
            total_target = (min_length + max_length) // 2
            
            # Distribute word count across sections
            words_per_section = total_target // len(sections)
            
            generated_sections = []
            total_tokens = 0
            
            for i, section in enumerate(sections):
                # Determine section type and adjust word target
                if i == 0:  # Hook section
                    section_word_target = max(words_per_section // 2, 200)  # Shorter hook
                    section_type = "hook"
                    system_prompt = OpenAIScriptService._build_hook_system_prompt()
                elif i == len(sections) - 1:  # Conclusion section
                    section_word_target = max(words_per_section // 2, 200)  # Shorter conclusion
                    section_type = "conclusion"
                    system_prompt = OpenAIScriptService._build_conclusion_system_prompt()
                else:  # Main content sections
                    section_word_target = words_per_section
                    section_type = "main_content"
                    system_prompt = OpenAIScriptService._build_main_content_system_prompt()
                
                print(f"[SCRIPT_SECTION_SPECIFIC] Generating {section_type} section {i+1}/{len(sections)}: '{section.get('title', 'Untitled')}' ({section_word_target} words)")
                
                # Build section-specific user prompt
                section_title = section.get("title", f"Section {i+1}")
                section_description = section.get("description", "")
                key_points = section.get("key_points", [])
                
                # Add context from previous sections if available
                context_text = ""
                if generated_sections and len(generated_sections) > 0:
                    context_text = "\n\nPREVIOUS SECTIONS CONTEXT:\n"
                    for j, prev_section in enumerate(generated_sections[-2:]):  # Only last 2 sections
                        prev_title = prev_section.get("title", f"Section {j+1}")
                        prev_content = prev_section.get("content", "")
                        # Summarize previous content to save tokens
                        if len(prev_content) > 200:
                            prev_content = prev_content[:200] + "..."
                        context_text += f"- {prev_title}: {prev_content}\n"
                
                user_prompt = f"""Generate {section_type} content for: {section_title}

Section Description: {section_description}

Key Points to Cover:
{chr(10).join(f"• {point}" for point in key_points)}

Word Count Target: {section_word_target} words (STRICT REQUIREMENT)

Section Index: {i + 1} of {len(sections)}{context_text}

REQUIREMENTS:
- Write exactly {section_word_target} words (±5% tolerance - STRICT REQUIREMENT)
- Follow the {section_type}-specific strategies in the system prompt
- Ensure content flows naturally and maintains engagement
- Include specific examples, sensory details, and emotional beats
- Write in a conversational, YouTube-friendly tone

CRITICAL: Count words before submitting - content must be {section_word_target} words minimum.
FAILURE TO MEET WORD COUNT WILL RESULT IN REGENERATION."""
                
                # Use full token limits since this is a separate OpenAI call
                # No need to calculate estimated tokens - use maximum available
                model_name = settings.OPENAI_MODEL.lower()
                
                api_params = {
                    "model": settings.OPENAI_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.7,
                }
                
                # GPT-5 and o1 models have different parameter requirements
                if "gpt-5" in model_name or "o1" in model_name:
                    api_params["max_completion_tokens"] = 8192  # Maximum for GPT-5
                    max_tokens = 8192
                else:
                    api_params["max_tokens"] = 4096  # Maximum for GPT-4.1
                    max_tokens = 4096
                
                try:
                    response = client.chat.completions.create(**api_params)
                    
                    if not response.choices or len(response.choices) == 0:
                        raise ValueError("OpenAI API returned no choices in response")
                    
                    choice = response.choices[0]
                    if not hasattr(choice, "message") or not choice.message:
                        raise ValueError("OpenAI API returned invalid choice structure")
                        
                    content_text = choice.message.content
                    if not content_text:
                        raise ValueError("OpenAI API returned empty content")
                    
                    # Parse JSON response
                    import json
                    parsed_response = json.loads(content_text)
                    content = parsed_response.get("content", "")
                    
                    tokens_used = response.usage.total_tokens if response.usage else 0
                    total_tokens += tokens_used
                    
                    # Create section object
                    section_obj = {
                        "title": section_title,
                        "content": content,
                        "word_count": len(content.split()),
                        "section_index": i,
                        "section_type": section_type,
                        "validators_compliance": parsed_response.get("validators_compliance", {})
                    }
                    
                    generated_sections.append(section_obj)
                    
                    print(f"[SCRIPT_SECTION_SPECIFIC] {section_type.capitalize()} section {i+1} completed: {section_obj['word_count']} words, {tokens_used} tokens")
                    
                except Exception as e:
                    logger.error(f"[SCRIPT_SECTION_SPECIFIC] Error generating {section_type} section {i + 1}: {str(e)}")
                    raise
            
            # Combine all sections into full script
            full_text_parts = []
            for section in generated_sections:
                full_text_parts.append(f"## {section['title']}\n\n{section['content']}\n")
            
            full_text = "\n".join(full_text_parts)
            
            generation_time = time.time() - start_time
            
            metadata = {
                "tokens_used": total_tokens,
                "generation_time": generation_time,
                "model_used": settings.OPENAI_MODEL,
                "method": "section_specific_generation",
                "sections_generated": len(generated_sections),
                "target_length": f"{min_length}-{max_length} words",
                "actual_length": len(full_text.split())
            }
            
            print(f"[SCRIPT_SECTION_SPECIFIC] Completed successfully - Sections: {len(generated_sections)}, Tokens: {total_tokens}, Time: {generation_time:.2f}s")
            
            return full_text, generated_sections, metadata
            
        except Exception as e:
            logger.error(f"[SCRIPT_SECTION_SPECIFIC] Error: {str(e)}")
            raise

    @staticmethod
    def _build_outline_user_prompt(script_data: Dict[str, Any]) -> str:
        """Build user prompt for outline generation"""
        tones = script_data.get("tones", ["informative"])
        template_style = script_data.get("template_style", "medium")
        description = script_data.get("description", "")
        min_length = script_data.get("min_length", 0)
        max_length = script_data.get("max_length", 1000)

        tone_text = (
            f"Tones: {', '.join(tones)}" if len(tones) > 1 else f"Tone: {tones[0]}"
        )

        return f"""Generate DETAILED outline in JSON for:

Topic: {description} | {tone_text} | Style: {template_style} | Target: {min_length:,}-{max_length:,}w script

🚨 CRITICAL VALIDATOR ENFORCEMENT - FIRST TRY SUCCESS REQUIRED 🚨

S1 HOOK VALIDATION (MANDATORY):
- First sentence MUST start with ACTION VERB or CONCRETE NOUN + ACTION
- Examples: "Mark's system crashed", "The explosion shattered", "Sarah discovered"
- FORBIDDEN: "Imagine", "Picture", "Let me", "Let's", "Welcome", "Today we"
- Duration: ≤30 seconds (~75 words max)
- Structure: Action + 2-3 specific questions + transformation promise

S2 OPEN LOOPS VALIDATION (MANDATORY):
- Include 2-3 SPECIFIC questions in first 30-60 seconds
- Questions must create curiosity gaps
- Include transformation statement ("Today: X tactics that...")
- Plan for loop closure in conclusion

S6 VALUE DELIVERY VALIDATION (MANDATORY):
- For tutorials/listicles: First value point within 10s of hook end
- NO standalone intro sections after hook
- Immediate value delivery required

FRAMEWORK REQUIREMENTS (MANDATORY):
- Sensory details (P02): Include specific sights, sounds, textures
- Causal connectors (P03): "Because", "So", "Therefore" relationships
- Emotional beats (P05/P11): Include emotional moments and stakes
- Visual cues (P17): Describe what viewers will see
- Cliffhangers (BONUS-02): End sections with curiosity hooks

REQUIREMENTS:
• Each section: 80-150w description + 5-8 detailed key point sentences
• Include specific examples, stories, techniques to use
• Add timing + transition guidance
• Outline depth = script length (sparse = FAILS, detailed = success)
• MUST include validator_compliance_check in JSON response

VALIDATION CHECKLIST:
□ Hook starts with action verb/noun+action
□ Hook ≤75 words (30 seconds)
□ 2-3 specific questions in first 60 seconds
□ Transformation statement included
□ First value point within 10s for tutorials
□ Sensory details included
□ Emotional beats planned
□ Visual cues described

CRITICAL: Return ONLY valid JSON matching the exact schema provided in the system prompt.
VALIDATOR COMPLIANCE IS MANDATORY - NO EXCEPTIONS!
FAILURE TO MEET REQUIREMENTS WILL RESULT IN REGENERATION!"""

    @staticmethod
    def _build_script_system_prompt() -> str:
        """Build system prompt for script generation using Chat Completions"""
        storytelling_manual = format_storytelling_manual_for_prompt()
        
        return f"""You are an expert YouTube script writer with extensive experience creating engaging, retention-focused video content. Your specialty is transforming detailed outlines into compelling, conversational scripts that keep viewers watching.

CRITICAL: You MUST respond with valid JSON only. The API is configured to enforce JSON output format.

🚨 IMPORTANT: The validation rules below reference structural concepts like "open loops", "Before/Conflict/After", "Chapter X". These are FRAMEWORKS to guide your narrative structure. Use them to shape your writing, but NEVER include them as literal labels or headings in the script output. Write natural, flowing narrative prose.

MANDATORY VALIDATOR ENFORCEMENT FOR SCRIPTS:
Before creating any script, you MUST validate against these critical requirements:

S1 HOOK VALIDATORS (MANDATORY):
- Hook duration MUST be ≤30 seconds (hard cap: 60s when justified)
- Hook MUST contain action verb in first 1-2 sentences
- Hook MUST be 3-6 sentence micro-scene with filmable action
- Hook MUST pivot to main content within 60 seconds
- NO vague language like "high-stakes moment" without concrete dramatization
- NO 6+ minute atmospheric prologues (this is a CRITICAL FAILURE)

S2 OPEN LOOPS VALIDATORS (MANDATORY):
- MUST state 2-3 specific high-value questions in hook
- MUST include transformation statement: "Learn X to achieve Y"
- Questions MUST be stated cleanly in first 30-60 seconds
- NO questions buried in long monologues

S6 VALUE DELIVERY VALIDATORS (MANDATORY):
- For tutorials/listicles: First value point MUST start within 10 seconds of hook end
- Hook MUST be ≤30 seconds (exceptions explicitly justified)
- NO standalone 1-2 minute opening sections
- Get to main content FAST - NO 6+ minute delays

FRAMEWORK REQUIREMENTS (MANDATORY):
- P02: Include specific sensory details in each section
- P03: Use causal connectors (therefore, but, because) between beats
- P05/P11: Include emotional beats and stakes
- P07: Simplify - cut anything that doesn't advance the main story
- P09: Remove jargon and clichés - use plain language
- P10: Write at high-school reading level - conversational, not literary
- P13: Concision - say the same thing with fewer words
- P17: Write with visuals in mind - add editor cues and visual-friendly phrasing
- BONUS-02: End chapters with cliffhangers/unresolved threads

JSON SCHEMA REQUIREMENTS:
{{
  "full_text": "Complete script content with proper formatting and line breaks",
  "sections": [
    {{
      "title": "Section Title",
      "content": "Script content for this section",
      "word_count": 450,
      "validators_compliance": {{
        "hook_duration": "≤30s",
        "action_verbs": "Present in opening",
        "open_loops": "2-3 specific questions listed",
        "value_delivery_speed": "First point within 10s of hook end",
        "sensory_details": "Concrete, filmable details included",
        "causal_connectors": "Therefore/but/because links present",
        "emotional_beats": "Stakes and consequences defined",
        "visual_cues": "Editor notes included",
        "cliffhangers": "Unresolved threads at section ends",
        "simplified": "No tangents or unnecessary details",
        "plain_language": "No jargon or clichés",
        "conversational": "High-school reading level",
        "concise": "No verbose constructions"
      }}
    }}
  ],
  "total_word_count": 2500,
  "estimated_duration": "12-15 minutes",
  "validator_compliance_check": {{
    "s1_hook_structure": "PASS/FAIL with specific violations",
    "s2_open_loops": "PASS/FAIL with specific violations", 
    "s6_value_delivery": "PASS/FAIL with specific violations",
    "framework_gaps": "List of missing P02, P03, P05, P07, P09, P10, P13, P17, BONUS-02 elements"
  }}
}}

VALIDATION PROCESS FOR SCRIPTS:
1. Create script structure following outline
2. Check each validator against S1, S2, S6 requirements
3. Verify framework elements (P02, P03, P05, P07, P09, P10, P13, P17, BONUS-02)
4. If ANY validator fails, REVISE the script until ALL pass
5. Include validator_compliance_check in JSON response

{EXAMPLE_COMPLIANT_HOOKS}

Then immediately: Dive into first value point with concrete examples, no 6-minute preamble.

CRITICAL FAILURES TO AVOID:
- 6+ minute atmospheric prologues (COMPLETE FAILURE)
- Literary prose instead of conversational tone
- Buried questions in long monologues
- Missing action verbs in opening
- Vague language without concrete dramatization
- Missing editor cues and visual elements

Key principles:
- Write in a conversational, engaging tone suitable for YouTube
- Create content that maintains viewer attention throughout
- Use storytelling techniques, examples, and analogies
- Structure content for maximum retention and engagement
- Write scripts that feel natural when spoken aloud
- Focus on value delivery while maintaining entertainment value
- ENFORCE ALL VALIDATORS - NO EXCEPTIONS

Your scripts should be comprehensive, well-structured, and optimized for YouTube's algorithm and viewer behavior.

=== TUBEGENIUS STORYTELLING MANUAL ===
{storytelling_manual}

Apply these proven storytelling principles throughout your script generation. Use the opening strategies for compelling hooks, implement the core principles for engaging content, and follow the implementation checklist to ensure maximum retention and viewer engagement.

CRITICAL: Every script MUST pass ALL validators. If you cannot create a compliant script, explain why in the validator_compliance_check section.

RESPONSE FORMAT: Return ONLY valid JSON matching the schema above. No markdown, no explanations, no additional text."""

    @staticmethod
    def _build_script_user_prompt(
        outline_text: str, script_data: Dict[str, Any]
    ) -> str:
        """Build user prompt for script generation"""
        tones = script_data.get("tones", ["informative"])
        min_length = script_data.get("min_length", 1000)
        max_length = script_data.get("max_length", 5000)

        tone_text = (
            f"Tones: {', '.join(tones)}" if len(tones) > 1 else f"Tone: {tones[0]}"
        )

        # Calculate concrete targets
        target_words = (min_length + max_length) // 2
        
        # Detect if this is a tutorial/listicle
        tutorial_keywords = [
            "trick",
            "tip",
            "hack",
            "step",
            "way",
            "method",
            "technique",
            "secret",
        ]
        is_tutorial = any(
            keyword in outline_text.lower() for keyword in tutorial_keywords
        )
        
        if is_tutorial:
            s6_enforcement = """
🚨 S6 TUTORIAL/LISTICLE STRUCTURAL ENFORCEMENT:

MANDATORY SECTION ORDER:
1. Hook (≤30s, ~75 words): Action opening + 2-3 questions + transformation promise
2. First Value Point (starts at 0:30): IMMEDIATELY begin Trick/Tip #1 content
3. Remaining points in sequence
4. Conclusion

EXAMPLE STRUCTURE:
\"\"\"
Hook (0:00-0:30):
Mark's system crashed at 2 AM. Production down. Boss calling in 6 hours.
What do senior engineers do differently in crisis mode?
Today: 7 debugging tactics that cut recovery time by 80%.

Trick #1: The Binary Search Method (0:30-3:00)
When your system fails, most developers start guessing. Senior engineers...
[IMMEDIATE value delivery - NO standalone intro section]
\"\"\"

CRITICAL: NO standalone 1-2 minute intro section after hook. Hook → Value immediately.
"""
        else:
            s6_enforcement = """
S6 NARRATIVE ENFORCEMENT:
Use ≤60s prologue, then pivot to Chapter 1/chronological beginning. (Note: "Chapter 1" is a structural concept - don't write it as a heading in the script)
"""
        
        return f"""Generate complete script from outline below.

🎯 MANDATORY: {min_length:,}-{max_length:,} WORDS in full_text field (Target: {target_words:,})
Under {min_length:,} = REJECTION

CRITICAL VALIDATOR ENFORCEMENT REQUIRED FOR SCRIPTS:
• S1: Hook ≤30s, action verbs, 3-6 sentences, pivot within 60s, NO 6+ minute prologues
• S2: 2-3 specific questions, transformation statement, questions in first 30-60s
• S6: First value point within 10s of hook end for tutorials/listicles
• Framework: Sensory details (P02), causal connectors (P03), emotional beats (P05/P11), 
  simplified (P07), plain language (P09), conversational (P10), concise (P13), 
  visual cues (P17), cliffhangers (BONUS-02)

CRITICAL FAILURES TO AVOID:
• 6+ minute atmospheric prologues (COMPLETE FAILURE)
• Literary prose instead of conversational tone
• Buried questions in long monologues
• Missing action verbs in opening
• Vague language without concrete dramatization

CRITICAL:
- Follow outline structure EXACTLY, preserve section titles as-is
- {tone_text}
- NO document references/citations
- Write for direct narration
- Verify full_text ≥{min_length:,}w before submitting
- MUST include validator_compliance_check in JSON response

WORD COUNT VERIFICATION PROTOCOL:
1. Write your content
2. Count the words in full_text field
3. If under {min_length:,} words:
   - Add examples for each point (+50-100 words each)
   - Expand transitions (+30-50 words each)
   - Include backstory/context (+100-150 words)
4. VERIFY AGAIN before submitting
5. Include actual word count in response

EXPANSION CHECKLIST (if needed):
□ Every claim has an example/story
□ Every transition has 2-3 sentences
□ Every section has context/background
□ Every point has "why this matters"

{s6_enforcement}

PROVIDED OUTLINE TO FOLLOW:
{outline_text}

STRICT SECTION ORDER REQUIREMENTS:
1. Use the EXACT section titles from the outline in the SAME order
2. Do not skip, reorder, or combine sections
3. If the outline contains a "section_order" array, use it to determine the exact sequence
4. Each script section must correspond to the outline sections in the correct order

CRITICAL: Return ONLY valid JSON matching the exact schema provided in the system prompt. The API enforces JSON format automatically.
VALIDATOR COMPLIANCE IS MANDATORY - NO EXCEPTIONS!"""

    @staticmethod
    def _check_validator_compliance(
        sections: List[Dict], parsed_data: Dict, template_style: str = "medium"
    ) -> Dict[str, Any]:
        """
        Check outline compliance against S1, S2, S6 validators and framework requirements
        
        Args:
            sections: List of outline sections
            parsed_data: Full parsed JSON response
            template_style: Template style to determine validation strictness
            
        Returns:
            Dictionary with compliance check results
        """
        # Early return for Flexible Outline template
        if template_style.lower() == "flexible_outline":
            return OpenAIScriptService._check_flexible_outline_compliance(
                sections, parsed_data
            )
        
        compliance_check = {
            "s1_hook_structure": "PASS",
            "s2_open_loops": "PASS", 
            "s6_value_delivery": "PASS",
            "framework_gaps": [],
            "overall_compliance": "PASS",
            "violations": [],
        }
        
        if not sections:
            compliance_check["overall_compliance"] = "FAIL"
            compliance_check["violations"].append("No sections provided")
            return compliance_check
        
        # Check S1 Hook Structure Validators
        first_section = sections[0]
        hook_content = (
            first_section.get("description", "")
            + " "
            + first_section.get("content", "")
        )
        
        # S1.1: Hook duration check (look for timing indicators)
        timing = first_section.get("timing", "")
        if "minute" in timing.lower() and any(char.isdigit() for char in timing):
            # Extract duration numbers
            duration_match = re.search(r"(\d+)", timing)
            if duration_match:
                duration = int(duration_match.group(1))
                if duration > 1:  # More than 1 minute
                    compliance_check["s1_hook_structure"] = "FAIL"
                    compliance_check["violations"].append(
                        f"S1 violation: Hook duration {duration} minutes exceeds 60s limit"
                    )
        
        # S1.2: Action verbs in first 1-2 sentences
        hook_sentences = hook_content.split(".")[:2]
        action_verbs = [
            "start",
            "begin",
            "open",
            "create",
            "build",
            "develop",
            "launch",
            "introduce",
            "present",
            "show",
            "reveal",
            "demonstrate",
        ]
        has_action_verb = any(
            verb in sentence.lower()
            for sentence in hook_sentences
            for verb in action_verbs
        )
        if not has_action_verb:
            compliance_check["s1_hook_structure"] = "FAIL"
            compliance_check["violations"].append(
                "S1 violation: No action verbs in first 1-2 sentences"
            )
        
        # S1.3: Vague language check
        vague_terms = [
            "high-stakes moment",
            "dramatic",
            "exciting",
            "interesting",
            "compelling",
        ]
        has_vague_language = any(term in hook_content.lower() for term in vague_terms)
        if has_vague_language:
            compliance_check["s1_hook_structure"] = "FAIL"
            compliance_check["violations"].append(
                "S1 violation: Contains vague language without concrete dramatization"
            )
        
        # Check S2 Open Loops Validators
        # S2.1: Specific questions check
        question_indicators = ["?", "how", "what", "why", "when", "where"]
        has_questions = any(
            indicator in hook_content.lower() for indicator in question_indicators
        )
        if not has_questions:
            compliance_check["s2_open_loops"] = "FAIL"
            compliance_check["violations"].append(
                "S2 violation: No specific questions in hook"
            )
        
        # S2.2: Transformation statement check
        transformation_indicators = [
            "learn",
            "achieve",
            "transform",
            "change",
            "improve",
            "master",
        ]
        has_transformation = any(
            indicator in hook_content.lower() for indicator in transformation_indicators
        )
        if not has_transformation:
            compliance_check["s2_open_loops"] = "FAIL"
            compliance_check["violations"].append(
                "S2 violation: No transformation statement (Learn X to achieve Y)"
            )
        
        # Check S6 Value Delivery Validators
        # S6.1: First value point timing (for tutorials/listicles)
        if len(sections) > 1:
            second_section = sections[1]
            second_timing = second_section.get("timing", "")
            if "second" in second_timing.lower() or "10" in second_timing:
                # Check if it's within 10 seconds
                second_match = re.search(r"(\d+)", second_timing)
                if second_match:
                    second_duration = int(second_match.group(1))
                    if second_duration > 10:
                        compliance_check["s6_value_delivery"] = "FAIL"
                        compliance_check["violations"].append(
                            f"S6 violation: First value point starts at {second_duration}s, exceeds 10s limit"
                        )
        
        # Check Framework Requirements
        framework_gaps = []
        
        # P02: Sensory details check
        sensory_words = [
            "see",
            "hear",
            "feel",
            "smell",
            "taste",
            "touch",
            "visual",
            "sound",
            "texture",
        ]
        has_sensory_details = any(
            word in str(sections).lower() for word in sensory_words
        )
        if not has_sensory_details:
            framework_gaps.append("P02: Missing sensory details")
        
        # P03: Causal connectors check
        causal_connectors = [
            "therefore",
            "because",
            "but",
            "however",
            "thus",
            "as a result",
        ]
        has_causal_connectors = any(
            connector in str(sections).lower() for connector in causal_connectors
        )
        if not has_causal_connectors:
            framework_gaps.append("P03: Missing causal connectors")
        
        # P05/P11: Emotional beats and stakes check
        emotional_words = [
            "stakes",
            "consequences",
            "risk",
            "danger",
            "reward",
            "goal",
            "obstacle",
        ]
        has_emotional_beats = any(
            word in str(sections).lower() for word in emotional_words
        )
        if not has_emotional_beats:
            framework_gaps.append("P05/P11: Missing emotional beats and stakes")
        
        # P17: Visual cues check
        visual_words = [
            "show",
            "visual",
            "graphic",
            "image",
            "scene",
            "cut to",
            "camera",
        ]
        has_visual_cues = any(word in str(sections).lower() for word in visual_words)
        if not has_visual_cues:
            framework_gaps.append("P17: Missing visual cues/editor notes")
        
        # BONUS-02: Cliffhangers check
        cliffhanger_words = [
            "but",
            "however",
            "unresolved",
            "tease",
            "coming up",
            "next",
        ]
        has_cliffhangers = any(
            word in str(sections).lower() for word in cliffhanger_words
        )
        if not has_cliffhangers:
            framework_gaps.append("BONUS-02: Missing cliffhangers/unresolved threads")
        
        compliance_check["framework_gaps"] = framework_gaps
        
        # Overall compliance check
        if (
            compliance_check["s1_hook_structure"] == "FAIL"
            or compliance_check["s2_open_loops"] == "FAIL"
            or compliance_check["s6_value_delivery"] == "FAIL"
            or len(framework_gaps) > 2
        ):  # Allow up to 2 framework gaps
            compliance_check["overall_compliance"] = "FAIL"
        
        return compliance_check

    @staticmethod
    def _calculate_compliance_score(violations: List[str]) -> Dict[str, Any]:
        """Calculate a compliance score instead of binary pass/fail"""
        
        critical_violations = ['S1', 'S7']  # Must pass
        important_violations = ['S2', 'S6']  # Should pass
        minor_violations = ['P02', 'P03']  # Nice to have
        
        score = 100
        blocking = False
        
        for violation in violations:
            if any(critical in violation for critical in critical_violations):
                score -= 30
                blocking = True
            elif any(important in violation for important in important_violations):
                score -= 15
            else:
                score -= 5
        
        return {
            'score': max(0, score),
            'blocking': blocking,
            'grade': 'PASS' if score >= 70 and not blocking else 'FAIL',
            'severity': 'critical' if blocking else 'important' if score < 70 else 'minor'
        }

    @staticmethod
    def _validate_section_quality(content: str, section_type, attempt: int, max_attempts: int) -> Tuple[bool, List[str]]:
        """Validate section quality with specific checks"""
        errors = []
        
        # Basic quality checks
        if len(content.strip()) < 50:
            errors.append("Content too short")
        
        # Check for AI-like patterns
        ai_patterns = [
            "So here's what happened",
            "Let me tell you about",
            "In this video, we will",
            "Today we're going to",
            "First, let's start with",
            "Moving on to",
            "As you can see",
            "It's important to note"
        ]
        
        for pattern in ai_patterns:
            if pattern.lower() in content.lower():
                errors.append(f"AI pattern detected: '{pattern}'")
        
        # Check for variety in sentence length
        sentences = content.split('.')
        if len(sentences) > 3:
            sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
            if len(set(sentence_lengths)) < 3:  # Not enough variety
                errors.append("Insufficient sentence length variety")
        
        # Hook-specific validation
        if section_type.value == "hook_intro":
            first_sentence = content.split('.')[0].strip()
            if not any(word in first_sentence.lower().split()[:5] for word in ['crashed', 'exploded', 'discovered', 'warned', 'killed', 'shattered', 'buzzed', 'struck']):
                errors.append("Hook lacks action verb in first 5 words")
        
        # Determine if errors are critical
        critical_errors = [e for e in errors if "AI pattern" in e or "Hook lacks" in e]
        is_valid = len(critical_errors) == 0 or attempt >= max_attempts - 1
        
        return is_valid, errors

    @staticmethod
    def _build_correction_prompt(quality_errors: List[str], content: str, word_target: int, 
                                word_count_failed: bool, actual_words: int) -> str:
        """Build a specific correction prompt based on validation failures"""
        
        corrections = []
        
        if word_count_failed:
            corrections.append(f"WORD COUNT: Current {actual_words} words, need exactly {word_target} words")
        
        if quality_errors:
            corrections.append(f"QUALITY ISSUES: {', '.join(quality_errors)}")
        
        correction_prompt = f"""REGENERATION REQUIRED:

{chr(10).join(corrections)}

INSTRUCTIONS:
1. Fix ALL issues listed above
2. Maintain narrative flow and conversational tone
3. Use varied sentence lengths (3-25 words)
4. Include specific examples and emotional beats
5. Avoid repetitive AI patterns
6. Count words before submitting

Generate the corrected section now:"""
        
        return correction_prompt

    @staticmethod
    def _build_enhanced_outline_prompt(script_data: Dict[str, Any], violations: str, score_info: Dict) -> str:
        """Build enhanced prompt with specific violation feedback"""
        
        tones = script_data.get("tones", ["informative"])
        template_style = script_data.get("template_style", "medium")
        description = script_data.get("description", "")
        min_length = script_data.get("min_length", 0)
        max_length = script_data.get("max_length", 1000)

        tone_text = (
            f"Tones: {', '.join(tones)}" if len(tones) > 1 else f"Tone: {tones[0]}"
        )

        return f""" REGENERATION REQUIRED - CRITICAL VIOLATIONS DETECTED 

PREVIOUS ATTEMPT FAILED:
Score: {score_info['score']}/100 | Grade: {score_info['grade']} | Severity: {score_info['severity']}

VIOLATIONS TO FIX:
{violations}

TOPIC: {description} | {tone_text} | Style: {template_style} | Target: {min_length:,}-{max_length:,}w script

🚨 CRITICAL VALIDATOR ENFORCEMENT - MUST PASS THIS TIME 🚨

S1 HOOK VALIDATION (MANDATORY - NO EXCEPTIONS):
- First sentence MUST start with ACTION VERB or CONCRETE NOUN + ACTION
- Examples: "Mark's system crashed", "The explosion shattered", "Sarah discovered"
- FORBIDDEN: "Imagine", "Picture", "Let me", "Let's", "Welcome", "Today we"
- Duration: ≤30 seconds (~75 words max)
- Structure: Action + 2-3 specific questions + transformation promise

S2 OPEN LOOPS VALIDATION (MANDATORY - NO EXCEPTIONS):
- Include 2-3 SPECIFIC questions in first 30-60 seconds
- Questions must create curiosity gaps
- Include transformation statement ("Today: X tactics that...")
- Plan for loop closure in conclusion

S6 VALUE DELIVERY VALIDATION (MANDATORY - NO EXCEPTIONS):
- For tutorials/listicles: First value point within 10s of hook end
- NO standalone intro sections after hook
- Immediate value delivery required

FRAMEWORK REQUIREMENTS (MANDATORY - NO EXCEPTIONS):
- Sensory details (P02): Include specific sights, sounds, textures
- Causal connectors (P03): "Because", "So", "Therefore" relationships
- Emotional beats (P05/P11): Include emotional moments and stakes
- Visual cues (P17): Describe what viewers will see
- Cliffhangers (BONUS-02): End sections with curiosity hooks

VALIDATION CHECKLIST (MANDATORY):
□ Hook starts with action verb/noun+action
□ Hook ≤75 words (30 seconds)
□ 2-3 specific questions in first 60 seconds
□ Transformation statement included
□ First value point within 10s for tutorials
□ Sensory details included
□ Emotional beats planned
□ Visual cues described

CRITICAL: Return ONLY valid JSON matching the exact schema provided in the system prompt.
FAILURE TO MEET REQUIREMENTS WILL RESULT IN ANOTHER REGENERATION!
THIS IS YOUR FINAL ATTEMPT - MAKE IT COMPLIANT!"""

    @staticmethod
    def _check_flexible_outline_compliance(
        sections: List[Dict], parsed_data: Dict
    ) -> Dict[str, Any]:
        """Relaxed validation for Flexible Outline template (100-300 words)"""
        compliance_check = {
            "s1_hook_structure": "N/A",  # Outlines don't need full hook validation
            "s2_open_loops": "N/A",
            "s6_value_delivery": "N/A",
            "framework_gaps": [],
            "overall_compliance": "PASS",
            "violations": [],
            "template_type": "flexible_outline",
        }
        
        # Only check basic structure
        if not sections or len(sections) < 3:
            compliance_check["overall_compliance"] = "FAIL"
            compliance_check["violations"].append(
                "Flexible outline must have at least 3 sections"
            )
        
        # Check total word count (100-300 range)
        total_words = sum(len(s.get("description", "").split()) for s in sections)
        if total_words < 100 or total_words > 300:
            compliance_check["overall_compliance"] = "FAIL"
            compliance_check["violations"].append(
                f"Flexible outline word count {total_words} outside range 100-300"
            )
        
        return compliance_check

    @staticmethod
    def _check_script_validator_compliance(
        full_text: str, sections: List[Dict], parsed_data: Dict
    ) -> Dict[str, Any]:
        """
        Check script compliance against S1, S2, S6 validators and framework requirements
        
        Args:
            full_text: Complete script content
            sections: List of script sections
            parsed_data: Full parsed JSON response
            
        Returns:
            Dictionary with compliance check results
        """
        compliance_check = {
            "s1_hook_structure": "PASS",
            "s2_open_loops": "PASS", 
            "s6_value_delivery": "PASS",
            "framework_gaps": [],
            "overall_compliance": "PASS",
            "violations": [],
        }
        
        if not full_text or not sections:
            compliance_check["overall_compliance"] = "FAIL"
            compliance_check["violations"].append("No script content provided")
            return compliance_check
        
        # Extract hook content (first section or first 500 words)
        hook_content = ""
        if sections:
            first_section = sections[0]
            hook_content = first_section.get("content", "")
        
        # If no section content, use first 500 words of full_text
        if not hook_content:
            hook_content = full_text[:500]
        
        # Check S1 Hook Structure Validators
        # S1.1: Hook duration check - look for timing indicators or estimate from word count
        # Estimate: ~150 words per minute for spoken content
        hook_word_count = len(hook_content.split())
        estimated_hook_duration = hook_word_count / 150  # minutes
        
        # Add two-tier validation
        if estimated_hook_duration > 0.5:  # 30 seconds
            compliance_check["s1_hook_structure"] = "FAIL"
            compliance_check["violations"].append(
                f"S1 violation: Hook duration {estimated_hook_duration*60:.0f}s exceeds 30s target (60s hard cap)"
            )
            
        if estimated_hook_duration > 1.0:  # 60 seconds - CRITICAL FAILURE
            compliance_check["s1_hook_structure"] = "FAIL"
            compliance_check["violations"].append(
                f"S1 CRITICAL FAILURE: Hook duration {estimated_hook_duration*60:.0f}s exceeds 60s hard cap"
            )
        
        # S1.2: Action verbs in first 1-2 sentences
        hook_sentences = hook_content.split(".")[:2]
        action_verbs = [
            "start",
            "begin",
            "open",
            "create",
            "build",
            "develop",
            "launch",
            "introduce",
            "present",
            "show",
            "reveal",
            "demonstrate",
            "dive",
            "jump",
            "cut",
        ]
        has_action_verb = any(
            verb in sentence.lower()
            for sentence in hook_sentences
            for verb in action_verbs
        )
        if not has_action_verb:
            compliance_check["s1_hook_structure"] = "FAIL"
            compliance_check["violations"].append(
                "S1 violation: No action verbs in first 1-2 sentences"
            )
        
        # S1.3: Vague language check
        vague_terms = [
            "high-stakes moment",
            "dramatic",
            "exciting",
            "interesting",
            "compelling",
            "atmospheric",
            "eerie",
            "muted hum",
            "still air",
        ]
        has_vague_language = any(term in hook_content.lower() for term in vague_terms)
        if has_vague_language:
            compliance_check["s1_hook_structure"] = "FAIL"
            compliance_check["violations"].append(
                "S1 violation: Contains vague language without concrete dramatization"
            )
        
        # S1.4: Check for 6+ minute prologues (critical failure)
        if estimated_hook_duration > 6:
            compliance_check["s1_hook_structure"] = "FAIL"
            compliance_check["violations"].append(
                f"S1 CRITICAL FAILURE: {estimated_hook_duration:.1f} minute prologue - this is a complete failure"
            )
        
        # Check S2 Open Loops Validators
        # S2.1: Specific questions check
        question_indicators = ["?", "how", "what", "why", "when", "where"]
        has_questions = any(
            indicator in hook_content.lower() for indicator in question_indicators
        )
        if not has_questions:
            compliance_check["s2_open_loops"] = "FAIL"
            compliance_check["violations"].append(
                "S2 violation: No specific questions in hook"
            )
        
        # S2.2: Transformation statement check
        transformation_indicators = [
            "learn",
            "achieve",
            "transform",
            "change",
            "improve",
            "master",
            "tricks",
            "tips",
            "secrets",
        ]
        has_transformation = any(
            indicator in hook_content.lower() for indicator in transformation_indicators
        )
        if not has_transformation:
            compliance_check["s2_open_loops"] = "FAIL"
            compliance_check["violations"].append(
                "S2 violation: No transformation statement (Learn X to achieve Y)"
            )
        
        # S2.3: Questions buried in monologue check
        if len(hook_content.split()) > 200:  # Very long hook
            compliance_check["s2_open_loops"] = "FAIL"
            compliance_check["violations"].append(
                "S2 violation: Questions buried in long monologue"
            )
        
        # Check S6 Value Delivery Validators
        # S6.1: First value point timing (for tutorials/listicles)
        if len(sections) > 1:
            second_section = sections[1]
            second_content = second_section.get("content", "")
            # Look for value indicators in second section
            value_indicators = [
                "trick",
                "tip",
                "hack",
                "secret",
                "method",
                "technique",
                "step",
                "way",
            ]
            has_value_indicators = any(
                indicator in second_content.lower() for indicator in value_indicators
            )
            
            if has_value_indicators:
                # Estimate timing for second section
                second_word_count = len(second_content.split())
                second_duration = second_word_count / 150  # minutes
                if second_duration > 0.17:  # More than 10 seconds
                    compliance_check["s6_value_delivery"] = "FAIL"
                    compliance_check["violations"].append(
                        f"S6 violation: First value point starts at {second_duration*60:.0f}s, exceeds 10s limit"
                    )
        
        # Check Framework Requirements
        framework_gaps = []
        
        # P02: Sensory details check
        sensory_words = [
            "see",
            "hear",
            "feel",
            "smell",
            "taste",
            "touch",
            "visual",
            "sound",
            "texture",
            "scene",
            "show",
        ]
        has_sensory_details = any(word in full_text.lower() for word in sensory_words)
        if not has_sensory_details:
            framework_gaps.append("P02: Missing sensory details")
        
        # P03: Causal connectors check
        causal_connectors = [
            "therefore",
            "because",
            "but",
            "however",
            "thus",
            "as a result",
            "so",
            "then",
        ]
        has_causal_connectors = any(
            connector in full_text.lower() for connector in causal_connectors
        )
        if not has_causal_connectors:
            framework_gaps.append("P03: Missing causal connectors")
        
        # P05/P11: Emotional beats and stakes check
        emotional_words = [
            "stakes",
            "consequences",
            "risk",
            "danger",
            "reward",
            "goal",
            "obstacle",
            "pressure",
            "challenge",
        ]
        has_emotional_beats = any(word in full_text.lower() for word in emotional_words)
        if not has_emotional_beats:
            framework_gaps.append("P05/P11: Missing emotional beats and stakes")
        
        # P07: Simplify check - look for unnecessary tangents
        tangent_indicators = [
            "meanwhile",
            "incidentally",
            "by the way",
            "speaking of which",
            "on a side note",
        ]
        has_tangents = any(
            indicator in full_text.lower() for indicator in tangent_indicators
        )
        if has_tangents:
            framework_gaps.append("P07: Contains unnecessary tangents")
        
        # P09: Jargon/clichés check
        cliche_indicators = [
            "storm of thoughts",
            "silent war",
            "beacon in the darkness",
            "journey to mastery",
            "relentless pursuit",
            "whirling inside",
        ]
        has_cliches = any(
            indicator in full_text.lower() for indicator in cliche_indicators
        )
        if has_cliches:
            framework_gaps.append("P09: Contains clichés and jargon")
        
        # P10: Reading level check - look for overly complex sentences
        complex_indicators = [
            "notwithstanding",
            "furthermore",
            "moreover",
            "consequently",
            "subsequently",
        ]
        has_complex_language = any(
            indicator in full_text.lower() for indicator in complex_indicators
        )
        if has_complex_language:
            framework_gaps.append("P10: Contains overly complex language")
        
        # P13: Concision check - look for verbose constructions
        verbose_indicators = [
            "in order to",
            "due to the fact that",
            "it is important to note that",
            "at this point in time",
        ]
        has_verbose_constructions = any(
            indicator in full_text.lower() for indicator in verbose_indicators
        )
        if has_verbose_constructions:
            framework_gaps.append("P13: Contains verbose constructions")
        
        # P17: Visual cues check
        visual_words = [
            "show",
            "visual",
            "graphic",
            "image",
            "scene",
            "cut to",
            "camera",
            "[show",
            "[cut",
            "[visual",
        ]
        has_visual_cues = any(word in full_text.lower() for word in visual_words)
        if not has_visual_cues:
            framework_gaps.append("P17: Missing visual cues/editor notes")
        
        # BONUS-02: Cliffhangers check
        cliffhanger_words = [
            "but",
            "however",
            "unresolved",
            "tease",
            "coming up",
            "next",
            "stay tuned",
        ]
        has_cliffhangers = any(word in full_text.lower() for word in cliffhanger_words)
        if not has_cliffhangers:
            framework_gaps.append("BONUS-02: Missing cliffhangers/unresolved threads")
        
        compliance_check["framework_gaps"] = framework_gaps
        
        # Overall compliance check
        if (
            compliance_check["s1_hook_structure"] == "FAIL"
            or compliance_check["s2_open_loops"] == "FAIL"
            or compliance_check["s6_value_delivery"] == "FAIL"
            or len(framework_gaps) > 3
        ):  # Allow up to 3 framework gaps
            compliance_check["overall_compliance"] = "FAIL"
        
        return compliance_check

    # Helper functions for chunked outline generation
    @staticmethod
    def _determine_section_type(section_index: int, total_sections: int) -> str:
        """Determine the type of section based on its position"""
        if section_index == 0:
            return "hook"
        elif section_index == total_sections - 1:
            return "conclusion"
        else:
            return "main_content"

    @staticmethod
    def _enhance_sections_parallel(sections: List[Dict], client, model_name: str) -> Tuple[List[Dict], int]:
        """
        Enhance all sections in parallel for maximum speed
        
        Args:
            sections: List of basic section structures
            client: OpenAI client
            model_name: Model name string
            
        Returns:
            Tuple of (enhanced_sections, total_tokens)
        """
        import asyncio
        
        # Check if we're already in an event loop (Django async context)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, create a new loop in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        OpenAIScriptService._enhance_sections_async(sections, client, model_name)
                    )
                    return future.result()
            else:
                # No running loop, we can use asyncio.run
                return asyncio.run(
                    OpenAIScriptService._enhance_sections_async(sections, client, model_name)
                )
        except RuntimeError:
            # No event loop, we can use asyncio.run
            return asyncio.run(
                OpenAIScriptService._enhance_sections_async(sections, client, model_name)
            )

    @staticmethod
    async def _enhance_sections_async(sections: List[Dict], client, model_name: str) -> Tuple[List[Dict], int]:
        """
        Async coroutine to enhance all sections in parallel
        """
        # Create tasks for all sections
        tasks = []
        for i, section in enumerate(sections):
            section_type = OpenAIScriptService._determine_section_type(i, len(sections))
            task = OpenAIScriptService._enhance_single_section_async(
                section, section_type, i, len(sections), client, model_name
            )
            tasks.append(task)
        
        # Run all tasks in parallel
        print(f"[PARALLEL] Starting parallel enhancement of {len(tasks)} sections...")
        start_time = time.time()
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.time() - start_time
        print(f"[PARALLEL] All {len(tasks)} sections completed in {elapsed:.2f}s (parallel execution)")
        
        # Process results
        enhanced_sections = []
        total_tokens = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"[PARALLEL] Section {i+1} failed with error: {str(result)}")
                enhanced_sections.append(sections[i])  # Use original on failure
            else:
                section_data, tokens = result
                enhanced_sections.append(section_data)
                total_tokens += tokens
                print(f"[PARALLEL] Section {i+1} completed: {tokens} tokens")
        
        return enhanced_sections, total_tokens

    @staticmethod
    async def _enhance_single_section_async(
        section: Dict, 
        section_type: str, 
        section_index: int, 
        total_sections: int, 
        client, 
        model_name: str
    ) -> Tuple[Dict, int]:
        """
        Async coroutine to enhance a single section
        
        Returns:
            Tuple of (enhanced_section_data, tokens_used)
        """
        # Build section-specific prompt with only relevant rules
        section_system_prompt = OpenAIScriptService._build_section_enhancement_system_prompt(section_type)
        section_user_prompt = OpenAIScriptService._build_section_enhancement_user_prompt(section, section_type)
        
        section_api_params = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": section_system_prompt},
                {"role": "user", "content": section_user_prompt},
            ],
            "response_format": {"type": "json_object"},
        }
        
        # Set token limits for section enhancement
        # Priority: Quality & Speed (avoiding truncation) over cost
        # Using 4K provides generous buffer for complex sections without truncation risk
        if "gpt-5" in model_name or "o1" in model_name:
            section_api_params["max_completion_tokens"] = 4096  # Generous limit for quality
        elif "gpt-4.1" in model_name or "gpt-4-turbo" in model_name:
            section_api_params["max_tokens"] = 4096  # 4K ensures no truncation even for complex sections
            section_api_params["temperature"] = 0.7
        else:
            section_api_params["max_tokens"] = 2048
            section_api_params["temperature"] = 0.7
        
        # Make async API call
        # Note: OpenAI client is sync, so we run it in executor
        loop = asyncio.get_event_loop()
        section_response = await loop.run_in_executor(
            None,
            lambda: client.chat.completions.create(**section_api_params)
        )
        
        # Process response
        if not section_response.choices or len(section_response.choices) == 0:
            raise ValueError(f"Section {section_index+1}: No choices in response")
        
        section_content = section_response.choices[0].message.content
        if not section_content:
            raise ValueError(f"Section {section_index+1}: Empty content")
        
        # Parse JSON
        section_data = json.loads(section_content)
        tokens_used = section_response.usage.total_tokens if section_response.usage else 0
        
        return section_data, tokens_used

    @staticmethod
    def _build_single_pass_system_prompt(
        script_data: Dict[str, Any],
        num_sections: int,
        word_targets: Dict[str, Any]
    ) -> str:
        """
        Build comprehensive system prompt for single-pass generation
        Includes ALL storytelling rules, validators, and guidelines
        """
        # Get full storytelling manual (function is defined at module level in this file)
        storytelling_manual = format_storytelling_manual_for_prompt()
        
        return f"""You are an expert YouTube script writer generating a COMPLETE script in ONE response.

🎯 CRITICAL MISSION - WORD COUNT IS MANDATORY:
Generate ALL {num_sections} sections of the script in a single, cohesive response.

⚠️  DURATION & WORD COUNT REQUIREMENTS (STRICTLY ENFORCED):

🎙️ TOTAL DURATION: {int(word_targets['total_target'] / 140)} minutes of spoken English (@ 140 words/minute)
📊 WORD COUNT RANGE: The generated script MUST have a word count between {int(word_targets['total_target'] * 0.95)} and {int(word_targets['total_target'] * 1.05)} words (±5%).
🎯 Approximate Token Target: ~{int(word_targets['total_target'] * 1.33)} tokens.

SECTION BREAKDOWN:
- Hook/Intro (Section 1): {int(word_targets['intro'] / 140)} min = {word_targets['intro']} words (~{int(word_targets['intro'] * 1.33)} tokens)
- Main sections ({word_targets['main_sections_count']} sections): {int(word_targets['main_sections'] / 140)} min EACH = {word_targets['main_sections']} words each (~{int(word_targets['main_sections'] * 1.33)} tokens each)
- Conclusion (Last section): {int(word_targets['conclusion'] / 140)} min = {word_targets['conclusion']} words (~{int(word_targets['conclusion'] * 1.33)} tokens)

🎙️ THINK IN SPOKEN DURATION: You're writing for someone to READ ALOUD at 140 words per minute.
Generate enough content to fill {int(word_targets['total_target'] / 140)} minutes of speaking time.

🚨 CRITICAL: Scripts under {int(word_targets['total_target'] * 0.95)} words will be AUTOMATICALLY REJECTED

📏 HOW TO REACH WORD COUNT (EXPANSION TECHNIQUES):
If you find yourself falling short, expand using these techniques:
• Add MORE EXAMPLES: For each concept, give 2-3 concrete examples
• Add MORE DIALOGUE: Include what people said, exact quotes, internal thoughts
• Add MORE SENSORY DETAILS: What did it look like? Sound like? Feel like? Smell like?
• Add MORE EMOTIONAL BEATS: Show reactions, fears, hopes, doubts at each turning point
• Add MORE TRANSITIONS: Bridge ideas with "So here's what happened next...", "But that's when..."
• Add MORE BACKSTORY: Give context about characters, places, or situations
• Add MORE CONSEQUENCES: Show ripple effects, what happened next, long-term impacts
• SLOW DOWN KEY MOMENTS: Don't rush - let dramatic moments breathe with detail

⚡ REMEMBER: YouTube audiences want RICH, DETAILED stories, not bullet points. Give them the full experience.

🚨 STRUCTURAL LABELS ARE GUIDELINES - NOT OUTPUT TEXT:
• Concepts like "Before/Conflict/After", "Open Loops", "Chapter X" are FRAMEWORKS
• Use them to STRUCTURE your narrative, but DON'T write them as literal labels
• Write natural, flowing narrative prose
• Example: Don't write "Before: X. Conflict: Y. After: Z."
• Instead: Write a flowing story that naturally follows that arc

📚 LANGUAGE LEVEL - 6TH-7TH GRADE (MANDATORY):
• Every word must be instantly clear to a 10-year-old or 80-year-old
• ALWAYS use contractions: it's, don't, can't, they're, wasn't, couldn't, didn't

FORBIDDEN WORDS (Replace immediately):
❌ therefore, however, consequently, thus, hence → ✅ so, but, because, that's why
❌ nevertheless, moreover, furthermore → ✅ but, also, and, plus
❌ phenomenon, subsequently, essentially → ✅ thing, then/next, basically
❌ fundamentally, significant, substantial → ✅ really, big, huge, major
❌ utilize, implement, commence → ✅ use, do, start
❌ indicate, demonstrate, illustrate → ✅ show, prove, mean
❌ ascertain, endeavor, facilitate → ✅ find out, try, help

TALK LIKE THIS:
✅ "So here's what happened..."
✅ "But that's not the crazy part..."
✅ "And that's when things got weird..."
✅ "It didn't make sense..."

🔥 CONVERSATIONAL TONE (CRITICAL):
• Write like TALKING to a friend over coffee, not writing an essay
• Use short, punchy sentences mixed with natural flow
• Start sentences with: "But here's the thing...", "And that's when...", "So...", "Now..."
• Show EMOTION first, facts second: "She couldn't believe it." not "The results indicated..."
• Create tension in EVERY line - make them curious about the next sentence

🚨 CONTRACTIONS - USE EVERYWHERE (MANDATORY):
You MUST use contractions throughout your script. Never write:
❌ it is, do not, does not, cannot, could not, would not, should not, did not, was not, were not, are not, will not, they are, we are, you are
✅ it's, don't, doesn't, can't, couldn't, wouldn't, shouldn't, didn't, wasn't, weren't, aren't, won't, they're, we're, you're

Apply contractions to EVERY sentence where natural. Scripts without contractions will be rejected.

🎯 HOOK SECTION (First Section - CRITICAL):
• Line 1: MUST start with ACTION VERB (see, watch, hear, look, feel, discover, witness)
• Line 1-2: Hook IMMEDIATELY with emotion or mystery
• NO setup, NO context - jump straight into the moment
• Create 2-3 unanswered questions in first 30 seconds
• FORBIDDEN: "Imagine", "Picture", "Let me", "Have you ever"
• Example: "The call came at 3 AM. She knew something was wrong."
• ❌ BAD: "Imagine you're walking down the street..."
• ✅ GOOD: "She stopped walking. Something felt wrong."

📖 MAIN CONTENT SECTIONS:
• Show transformation: Before → Conflict → After (as narrative arc, not labels)
• Plant 2-3 open loops per section (curiosity questions for what's next)
• END every section (except last) with curiosity hook - MANDATORY:
  ✅ "But that wasn't even the strangest part."
  ✅ "The question is: why?"
  ✅ "And then everything changed."
  ✅ "So what happened next?"
  ❌ DO NOT end sections with neat conclusions - keep them wanting more
• Use simple words to link ideas: "so", "but", "because" (NOT "therefore", "however")
• Include emotional reactions, not just events

🎬 CONCLUSION SECTION (Last Section):
• End with emotional reflection or haunting question that sticks
• Use simple, conversational language
• NO clichés: "stay curious", "stay brave", "thanks for watching"
• Make them FEEL something or THINK about something new
• Examples: "So what else don't we know?", "And that's the thing - we'll never really know."

{storytelling_manual}

⚠️ SECTION ENDINGS (MANDATORY):
• EVERY section except the last must end with curiosity hook
• Create mini-cliffhangers to maintain engagement
• NO neat conclusions until the very end

💯 WORD COUNT ACCURACY (CRITICAL):
• Each section must hit its target word count (±5% tolerance)
• Hook: {word_targets['intro']}w, Main sections: {word_targets['main_sections']}w each, Conclusion: {word_targets['conclusion']}w
• Total script must be {word_targets['total_target']} words (±5%)

🔍 WORD COUNT VERIFICATION (MANDATORY):
BEFORE submitting your response, verify word count using code generation:
• For EACH section, use code generation to count words (split by whitespace and count)
• Check if each section meets its target (±5% tolerance)
• If any section is short, expand it with more examples, details, emotions
• Verify TOTAL word count = {word_targets['total_target']} (±5%)
• DO NOT guess - use code generation to get accurate counts

📋 JSON RESPONSE FORMAT (MANDATORY):
{{
  "sections": [
    {{
      "title": "Section 1 Title",
      "content": "Full script content for this section... (MUST be {word_targets['intro']} words)",
      "section_type": "hook_intro"
    }},
    {{
      "title": "Section 2 Title",
      "content": "Full script content for this section... (MUST be {word_targets['main_sections']} words)",
      "section_type": "main_content"
    }},
    ... (continue for all {num_sections} sections)
  ],
  "metadata": {{
    "generation_method": "single_pass",
    "sections_generated": {num_sections}
  }}
}}

⚠️  NOTE: Do NOT include "word_count" field - we will count the actual words from your content.
⚠️  Focus on generating FULL, DETAILED content that naturally reaches the target word count.

✅ QUALITY CHECKLIST (Self-validate before responding):
□ All {num_sections} sections generated
□ Total word count: {word_targets['total_target']} words (±5%)
□ Hook starts with action/emotion (no "Imagine/Picture")
□ 2-3 open loop questions in hook
□ Each main section ends with curiosity hook
□ Simple language (6th-7th grade level)
□ Contractions used throughout (it's, don't, can't)
□ NO forbidden words (therefore, however, consequently, etc.)
□ Conversational tone (talking to a friend)
□ Seamless transitions between sections
□ Natural narrative flow (no structural labels as text)

REMEMBER: Generate the COMPLETE script in ONE response. Make it conversational, engaging, and easy to understand!"""

    @staticmethod
    def _build_single_pass_user_prompt(
        sections: List[Dict],
        word_targets: Dict[str, Any],
        wc_strategy
    ) -> str:
        """
        Build comprehensive user prompt with all section details
        """
        prompt_parts = [
            "Generate a COMPLETE YouTube script based on this detailed outline:\n"
        ]
        
        for i, section in enumerate(sections):
            section_type = wc_strategy._determine_section_type(i, len(sections))
            
            # Determine word target
            if section_type.value == "hook_intro":
                target = word_targets["intro"]
            elif section_type.value == "conclusion":
                target = word_targets["conclusion"]
            else:
                target = word_targets["main_sections"]
            
            section_title = section.get("title", f"Section {i+1}")
            section_desc = section.get("description", "")
            key_points = section.get("key_points", [])
            
            # Calculate duration for this section
            duration_minutes = target / 140  # 140 words per minute
            duration_str = f"{int(duration_minutes)}:{int((duration_minutes % 1) * 60):02d}" if duration_minutes >= 1 else f"{int(duration_minutes * 60)}s"
            min_words = int(target * 0.95)
            max_words = int(target * 1.05)
            approx_tokens = int(target * 1.33)
            
            prompt_parts.append(f"\n{'='*60}")
            prompt_parts.append(f"SECTION {i+1}: {section_title}")
            prompt_parts.append(f"Type: {section_type.value.replace('_', ' ').title()}")
            prompt_parts.append(f"🎙️ DURATION: {duration_str} of spoken English (@ 140 words/minute)")
            prompt_parts.append(f"📊 WORD COUNT RANGE: This section MUST have between {min_words} and {max_words} words (±5%).")
            prompt_parts.append(f"🎯 Approximate Token Target: ~{approx_tokens} tokens.")
            prompt_parts.append(f"🚨 THIS SECTION ALONE MUST FILL {duration_str} OF SPEAKING TIME - expand with examples, details, emotion!")
            prompt_parts.append(f"\nDescription: {section_desc}")
            
            if key_points:
                prompt_parts.append(f"\nKey Points to Cover:")
                for point in key_points:
                    prompt_parts.append(f"• {point}")

        # Calculate total duration and tokens
        total_duration_minutes = word_targets['total_target'] / 140
        total_duration_str = f"{int(total_duration_minutes)} min {int((total_duration_minutes % 1) * 60)} sec"
        min_total_words = int(word_targets['total_target'] * 0.95)
        max_total_words = int(word_targets['total_target'] * 1.05)
        approx_total_tokens = int(word_targets['total_target'] * 1.33)
        
        prompt_parts.append(f"\n{'='*60}\n")
        prompt_parts.append(f"📊 FINAL REQUIREMENTS SUMMARY:")
        prompt_parts.append(f"• TOTAL SECTIONS: {len(sections)}")
        prompt_parts.append(f"• DURATION TARGET: {total_duration_str} of spoken English (@ 140 words/minute)")
        prompt_parts.append(f"• WORD COUNT RANGE: Script MUST be between {min_total_words} and {max_total_words} words (±5%)")
        prompt_parts.append(f"• TOKEN TARGET: Approximately ~{approx_total_tokens} tokens")
        prompt_parts.append("")
        prompt_parts.append("⚡ CRITICAL REQUIREMENTS:")
        prompt_parts.append(f"1. 🎙️ DURATION: Generate {total_duration_str} of spoken content")
        prompt_parts.append(f"2. 📊 WORD COUNT: Between {min_total_words}-{max_total_words} words (target: {word_targets['total_target']})")
        prompt_parts.append(f"3. 🎯 TOKEN COUNT: Approximately ~{approx_total_tokens} tokens")
        prompt_parts.append(f"4. 📝 COMPLETENESS: Generate ALL {len(sections)} sections in ONE response")
        prompt_parts.append("3. 🔗 FLOW: Maintain seamless narrative flow between sections")
        prompt_parts.append("4. 💬 LANGUAGE: Use 6th-7th grade language (simple, conversational)")
        prompt_parts.append("5. ✂️  CONTRACTIONS: Use contractions throughout (it's, don't, can't)")
        prompt_parts.append("6. NO structural labels in the script (Before/Conflict/After are guides only)")
        prompt_parts.append("7. End each section (except last) with curiosity hook")
        prompt_parts.append("8. Return valid JSON matching the schema in system prompt")
        prompt_parts.append("")
        prompt_parts.append("💡 HOW TO HIT WORD COUNT:")
        prompt_parts.append("• Add concrete examples, dialogue, sensory details")
        prompt_parts.append("• Show emotional reactions at turning points")
        prompt_parts.append("• Include backstory and context where relevant")
        prompt_parts.append("• Slow down key moments with rich detail")
        prompt_parts.append("• Use transitions to bridge ideas smoothly")
        prompt_parts.append("")
        prompt_parts.append("Begin generating the complete script now!")
        
        return "\n".join(prompt_parts)

    @staticmethod
    def _build_structure_system_prompt(suggested_sections: int) -> str:
        """Build minimal system prompt for basic structure generation"""
        return f"""You are an expert YouTube script writer. Create a basic outline structure with minimal details.

CRITICAL: You MUST respond with valid JSON only.

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
- Create exactly {suggested_sections} sections for a YouTube video
- Keep descriptions brief (20-30 words each)
- Focus on logical flow and structure
- No detailed validators or complex rules

RESPONSE FORMAT: Return ONLY valid JSON matching the schema above."""

    @staticmethod
    def _build_structure_user_prompt(script_data: Dict[str, Any]) -> Tuple[str, int]:
        """Build minimal user prompt for structure generation
        
        Returns:
            Tuple: (prompt string, suggested_sections count)
        """
        from scripts.services.word_count_strategy import TemplateStyleConfig
        
        tones = script_data.get("tones", ["informative"])
        template_style = script_data.get("template_style", "medium")
        description = script_data.get("description", "")
        min_length = script_data.get("min_length", 0)
        max_length = script_data.get("max_length", 1000)

        # Convert tone IDs to names if needed
        if tones and isinstance(tones[0], int):
            from scripts.models import Tone
            tone_objects = Tone.objects.filter(id__in=tones)
            tones = [tone.name for tone in tone_objects]
        
        # Convert template_style ID to name if needed
        if isinstance(template_style, int):
            from scripts.models import TemplateStyle
            try:
                style_obj = TemplateStyle.objects.get(id=template_style)
                template_style = style_obj.name
            except TemplateStyle.DoesNotExist:
                template_style = "medium"

        # Normalize template_style name for config lookup (lowercase, replace spaces with underscores)
        template_style_key = template_style.lower().replace(" ", "_")
        
        # Get suggested_sections from TemplateStyleConfig
        template_config = TemplateStyleConfig.TEMPLATE_CONFIGS.get(template_style_key, TemplateStyleConfig.TEMPLATE_CONFIGS["medium"])
        suggested_sections = template_config["suggested_sections"]
        
        print(f"[OUTLINE_STRUCTURE] Template style: {template_style} -> key: {template_style_key} -> sections: {suggested_sections}")

        tone_text = f"Tones: {', '.join(tones)}" if len(tones) > 1 else f"Tone: {tones[0]}"

        prompt = f"""Create basic outline structure for:

Topic: {description}
{tone_text} | Style: {template_style} | Target: {min_length:,}-{max_length:,} words

REQUIREMENTS:
- Create exactly {suggested_sections} sections with brief descriptions
- Logical flow from introduction to conclusion
- Keep it simple and structural

CRITICAL: Return ONLY valid JSON matching the schema provided."""

        return prompt, suggested_sections

    @staticmethod
    def _build_section_enhancement_system_prompt(section_type: str) -> str:
        """Build section-specific system prompt with only relevant rules"""
        if section_type == "hook":
            return """You are an expert YouTube hook writer. Enhance this hook section with specific validators.

CRITICAL: You MUST respond with valid JSON only.

HOOK VALIDATORS (MANDATORY):
- Hook duration MUST be ≤30 seconds
- Hook MUST contain action verb in first 1-2 sentences
- Hook MUST be 3-6 sentence micro-scene with filmable action
- Hook MUST pivot to main content within 60 seconds
- MUST state 2-3 specific high-value questions
- MUST include transformation statement: "Learn X to achieve Y"

✅ VALIDATION CHECKS (PERFORM INLINE):
- Verify hook duration estimate ≤30 seconds
- Confirm action verbs are present in first 1-2 sentences
- Check that 2-3 specific open loop questions are clearly stated
- Ensure first value point starts within 10 seconds of hook end
- If any validator fails, fix it in your enhancement before responding

JSON SCHEMA:
{
  "title": "Enhanced Hook Title",
  "description": "Very brief 1-2 sentence description (30-50 words max)",
  "key_points": ["Specific actionable point 1", "Specific actionable point 2", "Specific actionable point 3"],
  "timing": "≤30 seconds",
  "transition": "How to transition to next section",
  "content": "Specific examples, stories, or techniques to include",
  "validators_compliance": {
    "hook_duration": "≤30s - VERIFIED",
    "action_verbs": "Present in opening - VERIFIED",
    "open_loops": "2-3 specific questions listed - VERIFIED",
    "value_delivery_speed": "First point within 10s - VERIFIED"
  }
}

RESPONSE FORMAT: Return ONLY valid JSON matching the schema above."""

        elif section_type == "conclusion":
            return """You are an expert YouTube conclusion writer. Enhance this conclusion section.

CRITICAL: You MUST respond with valid JSON only.

CONCLUSION REQUIREMENTS:
- Close all open loops established in the hook
- Provide clear next steps or call-to-action
- Reinforce the main value proposition
- End with a strong, memorable statement
- Include cliffhangers for future content

✅ VALIDATION CHECKS (PERFORM INLINE):
- Verify all hook open loops are addressed/closed
- Confirm clear next steps or call-to-action are present
- Check that main value proposition is reinforced
- Ensure cliffhangers for future content are included
- If any validator fails, fix it in your enhancement before responding

JSON SCHEMA:
{
  "title": "Enhanced Conclusion Title",
  "description": "Very brief 1-2 sentence description (30-50 words max)",
  "key_points": ["Specific actionable point 1", "Specific actionable point 2", "Specific actionable point 3"],
  "timing": "Estimated duration",
  "transition": "How to transition to next section",
  "content": "Specific examples, stories, or techniques to include",
  "validators_compliance": {
    "open_loops_closed": "All hook questions answered - VERIFIED",
    "call_to_action": "Clear next steps provided - VERIFIED",
    "value_reinforced": "Main proposition restated - VERIFIED",
    "cliffhangers": "Future content teased - VERIFIED"
  }
}

RESPONSE FORMAT: Return ONLY valid JSON matching the schema above."""

        else:  # main_content
            return """You are an expert YouTube main content writer. Enhance this main content section.

CRITICAL: You MUST respond with valid JSON only.

MAIN CONTENT REQUIREMENTS:
- Deliver specific value points promised in the hook
- Use storytelling techniques to maintain engagement
- Include concrete examples and actionable advice
- Maintain conversational, YouTube-friendly tone
- Include sensory details and emotional beats

✅ VALIDATION CHECKS (PERFORM INLINE):
- Verify concrete, filmable sensory details are included
- Confirm causal connectors link ideas properly
- Check that emotional beats and stakes are defined
- Ensure proper structure and engagement maintained
- If any validator fails, fix it in your enhancement before responding

JSON SCHEMA:
{
  "title": "Enhanced Main Content Title",
  "description": "Very brief 1-2 sentence description (30-50 words max)",
  "key_points": ["Specific actionable point 1", "Specific actionable point 2", "Specific actionable point 3"],
  "timing": "Estimated duration",
  "transition": "How to transition to next section",
  "content": "Specific examples, stories, or techniques to include",
  "validators_compliance": {
    "sensory_details": "Concrete, filmable details included - VERIFIED",
    "causal_connectors": "Links present - VERIFIED",
    "emotional_beats": "Stakes and consequences defined - VERIFIED",
    "visual_cues": "Editor notes included - VERIFIED"
  }
}

RESPONSE FORMAT: Return ONLY valid JSON matching the schema above."""

    @staticmethod
    def _build_section_enhancement_user_prompt(section: Dict, section_type: str) -> str:
        """Build user prompt for section enhancement"""
        title = section.get("title", "Untitled Section")
        description = section.get("description", "")
        key_points = section.get("key_points", [])

        return f"""Enhance this {section_type} section:

Title: {title}
Description: {description}
Key Points: {', '.join(key_points)}

REQUIREMENTS:
- Keep description VERY BRIEF (30-50 words max) - this is an outline, not a script
- Add 3-5 detailed key points
- Include timing and transition guidance
- Apply {section_type}-specific validators
- Focus on structure, not detailed content
- Description should be 1-2 sentences max

CRITICAL: Return ONLY valid JSON matching the schema provided."""

    @staticmethod
    def _build_validation_system_prompt() -> str:
        """Build minimal system prompt for final validation"""
        return """You are an expert YouTube script validator. Perform final validation on this outline.

CRITICAL: You MUST respond with valid JSON only.

VALIDATION REQUIREMENTS:
- Check hook duration ≤30 seconds
- Verify open loops are properly stated
- Ensure value delivery speed is appropriate
- Confirm all sections have proper structure

JSON SCHEMA:
{
  "sections": [/* existing sections */],
  "validator_compliance_check": {
    "s1_hook_structure": "PASS/FAIL with specific violations",
    "s2_open_loops": "PASS/FAIL with specific violations",
    "s6_value_delivery": "PASS/FAIL with specific violations",
    "overall_compliance": "PASS/FAIL"
  }
}

RESPONSE FORMAT: Return ONLY valid JSON matching the schema above."""

    @staticmethod
    def _build_validation_user_prompt(sections: List[Dict]) -> str:
        """Build user prompt for validation"""
        sections_text = ""
        for i, section in enumerate(sections):
            sections_text += f"Section {i+1}: {section.get('title', 'Untitled')}\n"
            sections_text += f"Description: {section.get('description', '')}\n\n"

        return f"""Validate this outline:

{sections_text}

REQUIREMENTS:
- Check each validator against the sections
- Provide specific PASS/FAIL status
- List any violations found
- Ensure overall compliance

CRITICAL: Return ONLY valid JSON matching the schema provided."""
