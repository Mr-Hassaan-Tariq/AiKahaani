# services/openai_service.py
import base64
import json
import logging
import re
import time
from typing import Any, Dict, List, Tuple, Optional

import openai
from django.conf import settings

# Import the storytelling manual
from .prompt import prompt as storytelling_manual
# Import word count strategy
from .word_count_strategy import WordCountStrategy

logger = logging.getLogger(__name__)

# Lazy client initialization to avoid import-time errors in tests
_client = None

# Compliant hook examples for prompts
EXAMPLE_COMPLIANT_HOOKS = """
HOOK SUCCESS EXAMPLES (≤30 SECONDS, ~75 WORDS MAX):

✅ Example 1 (Tutorial/Listicle):
[SCENE: Clock strikes 3 AM. Laptop screen glows.]
Sarah's phone buzzed with the interview invite. 9 hours away.
Zero prep done.
But here's what top coders know: 7 tricks that flip panic into performance.
Trick #1: Concurrency isn't scary...

✅ Example 2 (Narrative/Documentary):
The explosion shattered the Phoenix desert silence at exactly 8:47 PM.
10,000 witnesses. Mile-wide V-formation. Silent craft.
Military says: flares.
Pilots say: impossible.
Tonight: What really happened on March 13, 1997?

✅ Example 3 (Explainer/Listicle):
Mark discovered the file at 2:17 AM. Encrypted. 47 GB. Shouldn't exist.
Three months later: everything changed.
Today: 5 security mistakes that expose your entire system.
Mistake #1: The authentication trap...

HOOK FAILURE EXAMPLES TO AVOID:

❌ "Imagine this: you're sitting at your desk..." (weak starter)
❌ "Picture this scene: a dark forest..." (vague, no action)
❌ "Let me tell you about the time..." (channel trailer style)
❌ "In today's video, we're going to talk about..." (boring intro)
❌ "Welcome back to the channel..." (CTA violation)
❌ 6-minute atmospheric prologue about generic characters (CRITICAL FAILURE)
❌ "It's 11 PM. Deadline in 9 hours. Sound familiar? What if I told you..." (weak opening)

CRITICAL RULES:
- First sentence MUST start with action verb or concrete noun + action
- NO "Imagine," "Picture," "Let me," "Let's," "Welcome," "Today we"
- Duration ≤30 seconds (~75 words at 2.5 words/second)
- Create 2-3 specific questions, not rhetorical fluff
"""



def get_openai_client():
    """Get OpenAI client, initializing it lazily"""
    global _client
    if _client is None:
        _client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


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
        if 'framework_formula' in item:
            manual_text.append("Framework:")
            for step in item['framework_formula']:
                manual_text.append(f"• {step}")
        if 'case_study_example' in item:
            manual_text.append(f"Example: {item['case_study_example']}")
    
    # Add case studies
    manual_text.append("\n\n=== CASE STUDIES ===")
    for item in storytelling_manual[7:9]:  # Case studies
        manual_text.append(f"\n{item['id']}: {item['principle_rule']}")
        manual_text.append(f"Explanation: {item['explanation']}")
        if 'framework_formula' in item:
            manual_text.append("Framework:")
            for step in item['framework_formula']:
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
        "P17: Write with the Visual in Mind: Every line should suggest footage or graphics"
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
        "Visual cues/storyboard notes embedded"
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
            if "sections" in data and "section_order" in data and "outline_text" in data:
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
            required_outline_keys = ["sections", "section_order", "outline_text", "metadata"]
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
    required_metadata = ["tokens_used", "generation_time", "model", "assistant_id", "vector_store_id", "thread_id"]
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
    required_metadata = ["tokens_used", "generation_time", "model", "assistant_id", "vector_store_id", "thread_id"]
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
                        sections, parsed_data, template_style=script_data.get("template_style", "medium")
                    )
                    
                    return {
                        "sections": sections, 
                        "section_order": section_order,
                        "outline_text": outline_text_raw,
                        "validator_compliance": validator_check
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
                    "validator_compliance": validator_check
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
        prompt: str, title_count: int = 6, tones: list = None, user=None, save_log: bool = True
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
            client = get_openai_client()

            # Build the message content
            system_prompt = OpenAIScriptService._build_title_system_prompt()
            user_prompt = OpenAIScriptService._build_title_user_prompt(
                prompt, title_count, tones
            )

            # Use Chat Completions API instead of Assistant API
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=2000,
                temperature=0.7,
            )
            
            logger.info(f"[TITLES] Generated {title_count} titles using Chat Completions API")

            # Extract content and token usage with validation
            if not response.choices or len(response.choices) == 0:
                raise ValueError("OpenAI API returned no choices in response")
            
            choice = response.choices[0]
            if not hasattr(choice, 'message') or not choice.message:
                raise ValueError("OpenAI API returned invalid choice structure")
                
            titles_content = choice.message.content
            if not titles_content:
                raise ValueError("OpenAI API returned empty content - this may indicate rate limiting or API error")
                
            tokens_used = response.usage.total_tokens if response.usage else 0

            generation_time = time.time() - start_time
            
            logger.debug(f"[TITLES] OpenAI API response validated - content length: {len(titles_content)}, tokens: {tokens_used}")

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
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]  # Remove ```json
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]   # Remove ```
            
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]  # Remove trailing ```
            
        return cleaned.strip()

    @staticmethod
    def _build_title_system_prompt() -> str:
        """Build system prompt for title generation with metadata-enforced JSON output"""
        storytelling_manual = format_storytelling_manual_for_prompt()
        
        return f"""You are an expert YouTube title writer trained on TubeGenius Title Wizardry principles.
Your job is to generate clickable titles AND return them with metadata in JSON.

KEY PRINCIPLES:
- Urgency and open loops
- ≤54 characters preferred (58 max hard limit)
- Strong POV, superlatives, emotional triggers
- Curiosity, secrets, FOMO
- Proven formats (The Truth About X, You're Wrong About X, NEVER Do X, etc.)
- Accessible mass-audience framing
- Avoid safe/boring phrasing

=== TUBEGENIUS STORYTELLING MANUAL ===
{storytelling_manual}

Use the opening strategies and storytelling principles to create titles that promise compelling content. Focus on creating curiosity, setting up transformation arcs, and using emotional triggers that align with the storytelling techniques.

OUTPUT FORMAT:
Return ONLY valid JSON array, no prose. Each item must include:

{{
  "title": "5 DISTURBING Stories You Were Never Meant To Hear",
  "levers": ["power_word","curiosity","superlative"],
  "emotion_target": "fear",
  "power_words": ["Disturbing"],
  "length_chars": 52,
  "truncation_safe": true,
  "keyword_hint": "scary stories",
  "notes": "Open loop implied; no payoff revealed"
}}"""

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
        script=None, user_title=None, user_prompt=None, title_count=5, tones=None, user=None
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
    def generate_outline_with_assistant(
        script_data: Dict[str, Any],
        user=None,
        save_log: bool = True,
    ) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        """
        Generate outline using OpenAI Chat Completions API
        
        Args:
            script_data: Dictionary containing script parameters
            user: User object for logging (optional)
            save_log: Whether to save run log to database (default: True)
        """
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
            if template_style_id == 4 or template_style_name.lower() == "flexible_outline":
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
                wc_strategy = WordCountStrategy(script_data.get("template_style", "medium"))
                
                # Use strategy to calculate section targets
                suggested_sections = wc_strategy.config["suggested_sections"]
                word_targets = wc_strategy.calculate_section_word_targets(suggested_sections)
                
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
• MUST start with action verb (not "Imagine," "Picture," "Let me")
• MUST create 2-3 specific open loops with concrete questions
• MUST include vivid sensory details and fast pacing
• NO channel trailers, personal updates, or CTAs
• Examples: "Sarah's phone buzzed at 3 AM..." or "The explosion shattered..."

MAIN CONTENT SECTIONS:
• MUST show transformation: Before → Conflict → After
• MINIMUM 3 concrete sensory details per section
• MUST plant 2-3 specific open loops per section
• Use natural, spoken English (8th-10th grade level)
• Include emotional progression, not just setup + mystery
• Link beats with "therefore," "but," "because"

CONCLUSION SECTION:
• End with emotional reflection or haunting unresolved question
• NO clichés like "stay curious," "stay brave," "thanks for watching"
• Create original insights tied to transformation arc
• Examples: "The question is: what else don't we know?"

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
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": enhanced_prompt},
                ],
                max_tokens=3000,  # Enough for detailed outline with JSON structure
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            
            logger.info(f"[OUTLINE] Generated outline using Chat Completions API")

            # Extract content and token usage with validation
            if not response.choices or len(response.choices) == 0:
                raise ValueError("OpenAI API returned no choices in response")
            
            choice = response.choices[0]
            if not hasattr(choice, 'message') or not choice.message:
                raise ValueError("OpenAI API returned invalid choice structure")
                
            outline_text = choice.message.content
            if not outline_text:
                raise ValueError("OpenAI API returned empty content - this may indicate rate limiting or API error")
                
            tokens_used = response.usage.total_tokens if response.usage else 0

            generation_time = time.time() - start_time
            
            logger.debug(f"[OUTLINE] OpenAI API response validated - content length: {len(outline_text)}, tokens: {tokens_used}")

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
                template_style=script_data.get("template_style", "medium")
            )
            
            # ADD THIS: Block if compliance fails (optional - can make this configurable)
            if compliance_check["overall_compliance"] == "FAIL":
                violation_summary = "\n".join(f"  - {v}" for v in compliance_check["violations"])
                logger.error(
                    f"[OUTLINE] Validator compliance failed:\n{violation_summary}"
                )
                
                # Option 1: Raise exception to fail generation
                # raise ValueError(f"Outline validation failed: {violation_summary}")
                
                # Option 2: Log warning and continue (current behavior)
                logger.warning("[OUTLINE] Continuing despite validation failures (non-blocking mode)")
            
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
        
        try:
            start_time = time.time()
            client = get_openai_client()

            # Build script generation message with enhanced prompts
            system_prompt = OpenAIScriptService._build_script_system_prompt()
            user_prompt = OpenAIScriptService._build_script_user_prompt(outline_text, script_data)

            # Calculate expected duration and targets
            min_duration = min_length / 150
            max_duration = max_length / 150
            target_mid = (min_length + max_length) // 2
            target_duration = target_mid / 150
            
            # Add safety buffer to target - aim higher than minimum to account for AI variability
            safety_buffer = int(min_length * 0.1)  # 10% buffer
            safe_target = target_mid + safety_buffer
            
            # Enhanced prompt with length enforcement
            enhanced_prompt = f"""{user_prompt}

🚨 MANDATORY: {min_length:,}-{max_length:,} WORDS (Target: {safe_target:,})
Scripts under {min_length:,} words = AUTOMATIC REJECTION

SECTION LENGTH FORMULA:
- Hook/Intro: 400-500 words
- EACH main section: 450-550 words (80-100w intro + 3x100-120w points + 50-80w transition)
- Conclusion/CTA: 300-400 words

EXPANSION TECHNIQUES (USE ALL):
1. Examples: Add concrete story/case for every claim (50-100w each)
2. Analogies: Compare to familiar concepts (40-80w each)
3. Elaborate: Turn 1 sentence into 3-4 with "what/why/how"
4. Context: Add "why this matters" for all points
5. Storytelling: Setup→tension→resolution for facts
6. Engagement: Rhetorical questions, direct address
7. Transitions: 2-3 sentence bridges between sections
8. Background: Provide context before new concepts

VERIFY: full_text field has {min_length:,}+ words before submitting."""
            
            # Calculate reasonable max completion tokens based on target length
            # For a 3000 word script: ~4000 tokens for text + 2000 for JSON structure = 6000 total
            # Add 50% buffer for safety
            estimated_tokens = int((max_length * 1.5) + 2000)  # 1.5 tokens per word + JSON overhead
            max_tokens = min(estimated_tokens, 10000)  # Cap at 10k to prevent excessive usage
            
            # Use Chat Completions API instead of Assistant API
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": enhanced_prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            
            logger.info(f"[SCRIPT] Generated script using Chat Completions API (target: {min_length}-{max_length}w)")

            # Extract content and token usage with validation
            if not response.choices or len(response.choices) == 0:
                raise ValueError("OpenAI API returned no choices in response")
            
            choice = response.choices[0]
            if not hasattr(choice, 'message') or not choice.message:
                raise ValueError("OpenAI API returned invalid choice structure")
                
            script_content = choice.message.content
            if not script_content:
                raise ValueError("OpenAI API returned empty content - this may indicate rate limiting or API error")
                
            tokens_used = response.usage.total_tokens if response.usage else 0

            generation_time = time.time() - start_time
            
            logger.debug(f"[SCRIPT] OpenAI API response validated - content length: {len(script_content)}, tokens: {tokens_used}")

            # Parse script sections
            sections = OpenAIScriptService._parse_script_sections(script_content)
            
            # Extract actual script text from JSON for accurate word count
            actual_script_text = script_content  # Default to full content
            try:
                script_json_data = json.loads(script_content)
                if isinstance(script_json_data, dict) and "full_text" in script_json_data:
                    actual_script_text = script_json_data["full_text"]
            except json.JSONDecodeError:
                # Not JSON, use raw content
                pass
            
            # Calculate word count
            word_count = len(actual_script_text.split())
            is_valid, actual_word_count = OpenAIScriptService._validate_word_count(
                actual_script_text, min_length, max_length, "Script"
            )

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
                "length_valid": is_valid,
            }
            
            # Check validator compliance for scripts
            compliance_check = OpenAIScriptService._check_script_validator_compliance(
                actual_script_text, sections, script_json_data if 'script_json_data' in locals() else {}
            )
            
            # Add compliance check to metadata
            metadata["validator_compliance"] = compliance_check

            # Log result (success or warning about word count)
            if is_valid:
                logger.info(f"[SCRIPT] ✓ Success: {word_count}w ({generation_time:.1f}s)")
            else:
                logger.warning(f"[SCRIPT] ⚠️ Word count mismatch: {word_count}w (target: {min_length}-{max_length}w)")
            
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
                    run_type="script_generation",
                    generation_time=generation_time,
                    model=settings.OPENAI_MODEL,
                )
            
            return script_content, sections, metadata

        except Exception as e:
            logger.error(f"[SCRIPT] Generation failed: {str(e)}")
            raise

    @staticmethod
    def generate_script_with_word_count_strategy(
        outline_text: str,
        script_data: Dict[str, Any],
        user=None,
        save_log: bool = True,
    ) -> Tuple[str, List[Dict], Dict[str, Any]]:
        """
        Generate full script using section-based word count strategy
        
        This method implements the new word count completion strategy that:
        1. Calculates word targets for each section
        2. Generates each section individually with specific storytelling strategies
        3. Validates and expands content to meet word count requirements
        4. Combines sections into a cohesive script
        
        Args:
            outline_text: The outline text to generate script from
            script_data: Dictionary containing script parameters
            user: User object for logging (optional)
            save_log: Whether to save run log to database (default: True)
        """
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
                sections = [{"title": "Main Content", "description": outline_text, "key_points": []}]
            
            # Calculate word targets for each section
            num_sections = len(sections)
            word_targets = wc_strategy.calculate_section_word_targets(num_sections)
            
            logger.info(f"[WC_STRATEGY] Starting section-based generation: {num_sections} sections, target: {word_targets['total_target']} words")
            
            # Generate each section individually
            generated_sections = []
            total_tokens_used = 0
            total_words_generated = 0
            
            for i, section in enumerate(sections):
                section_type = wc_strategy._determine_section_type(i, num_sections)
                
                # Determine word target for this section
                if section_type.value == "hook_intro":
                    section_word_target = word_targets["intro"]
                elif section_type.value == "conclusion":
                    section_word_target = word_targets["conclusion"]
                else:
                    section_word_target = word_targets["main_sections"]
                
                # Build section-specific prompt
                storytelling_manual_formatted = format_storytelling_manual_for_prompt()
                section_prompt = wc_strategy.build_section_specific_prompt(
                    section_data=section,
                    section_index=i,
                    total_sections=num_sections,
                    word_target=section_word_target,
                    storytelling_manual=storytelling_manual_formatted
                )
                
                # Generate section content with quality validation
                logger.info(f"[WC_STRATEGY] Generating section {i+1}/{num_sections}: '{section.get('title', 'Untitled')}' ({section_word_target} words)")
                
                section_content, section_tokens = OpenAIScriptService._generate_single_section_with_quality_validation(
                    section_prompt, section_word_target, section_type, wc_strategy, client
                )
                
                # Validate word count
                is_valid, actual_words, message = wc_strategy.validate_word_count(
                    section_content, section_word_target
                )
                
                logger.info(f"[WC_STRATEGY] Section {i+1}: {message}")
                
                # Expand if needed (more aggressive - trigger at 95% instead of 90%)
                if not is_valid and actual_words < section_word_target * 0.95:
                    logger.info(f"[WC_STRATEGY] Expanding section {i+1} to meet word target")
                    expansion_strategies = wc_strategy.get_expansion_strategies(section_type)
                    
                    expansion_prompt = f"""
Expand the following content to EXACTLY {section_word_target} words using these strategies:
{', '.join(expansion_strategies)}

Current content ({actual_words} words):
{section_content}

CRITICAL: You must reach {section_word_target} words minimum. Add more detail, examples, and elaboration.

Requirements:
- Target: {section_word_target} words minimum (currently {actual_words})
- Maintain the same tone and style
- Add examples, details, and elaboration
- Keep the core message intact
- DO NOT fall short of the word count
- Use storytelling strategies to add depth and engagement

RESPONSE FORMAT: Return JSON object with this exact structure:
{{
    "content": "Your expanded script content here...",
    "word_count": {section_word_target},
    "expansion_applied": true
}}
"""
                    
                    section_content, expansion_tokens = OpenAIScriptService._generate_single_section(
                        expansion_prompt, section_word_target, client
                    )
                    section_tokens += expansion_tokens
                    
                    # Validate again
                    is_valid, actual_words, message = wc_strategy.validate_word_count(
                        section_content, section_word_target
                    )
                    logger.info(f"[WC_STRATEGY] After expansion: {message}")
                
                # Store generated section
                generated_sections.append({
                    "title": section.get("title", f"Section {i+1}"),
                    "content": section_content,
                    "word_count": actual_words,
                    "target_words": section_word_target,
                    "section_type": section_type.value,
                    "is_valid": is_valid
                })
                
                total_tokens_used += section_tokens
                total_words_generated += actual_words
            
            # Calculate timing for sections
            generated_sections = wc_strategy.calculate_timing_for_sections(generated_sections)
            
            # Combine sections into full script
            full_script_text = OpenAIScriptService._combine_sections(generated_sections)
            
            # Final validation (stricter tolerance for better word count compliance)
            final_is_valid, final_word_count, final_message = wc_strategy.validate_word_count(
                full_script_text, word_targets["total_target"], tolerance=0.05
            )
            
            logger.info(f"[WC_STRATEGY] Final result: {final_message}")
            
            # Format sections for JSON schema response
            formatted_sections = wc_strategy.format_sections_for_json_schema(generated_sections)
            
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
                "template_style": template_style
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
            
            # Return in the proper JSON schema format
            return {
                "full_text": full_script_text,
                "sections": formatted_sections,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"[WC_STRATEGY] Generation failed: {str(e)}")
            raise

    @staticmethod
    def _generate_single_section_with_quality_validation(
        section_prompt: str, 
        word_target: int, 
        section_type, 
        wc_strategy, 
        client
    ) -> Tuple[str, int]:
        """
        Generate content for a single section with quality validation and iterative improvement
        
        Args:
            section_prompt: The prompt for generating this section
            word_target: Target word count for this section
            section_type: Section type for validation
            wc_strategy: Word count strategy instance
            client: OpenAI client instance
            
        Returns:
            Tuple of (content, tokens_used)
        """
        max_attempts = 2  # Reduced from 3 to 2 attempts
        total_tokens = 0
        
        for attempt in range(max_attempts):
            # Generate content
            section_content, tokens_used = OpenAIScriptService._generate_single_section(
                section_prompt, word_target, client
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
                section_content, 
                section_type,
                validation_level=validation_level
            )
            
            if is_valid:
                logger.info(f"[WC_STRATEGY] Section passed quality validation on attempt {attempt + 1}")
                return section_content, total_tokens
            
            # If validation fails and we have attempts left, regenerate with feedback
            if attempt < max_attempts - 1:
                logger.warning(f"[WC_STRATEGY] Section failed quality validation on attempt {attempt + 1}: {errors}")
                
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
                logger.warning(f"[WC_STRATEGY] Section failed quality validation after {max_attempts} attempts. Using best attempt.")
        
        return section_content, total_tokens

    @staticmethod
    def _generate_single_section(section_prompt: str, word_target: int, client) -> Tuple[str, int]:
        """
        Generate content for a single section with word count enforcement
        
        Returns:
            Tuple of (content, tokens_used)
        """
        # Calculate reasonable max tokens for the target word count
        estimated_tokens = int(word_target * 1.5) + 500  # 1.5 tokens per word + buffer
        max_tokens = min(estimated_tokens, 4000)  # Cap at 4k tokens
        
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": f"You are an expert YouTube script writer. CRITICAL: You must generate exactly {word_target} words (±5% tolerance). Word count is MANDATORY and non-negotiable. Count your words before responding. Failure to meet word count will result in regeneration."},
                {"role": "user", "content": section_prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        
        content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0
        
        # Parse JSON response to extract content
        try:
            import json
            section_data = json.loads(content)
            if isinstance(section_data, dict) and "content" in section_data:
                return section_data["content"], tokens_used
            else:
                logger.warning(f"[WC_STRATEGY] Invalid JSON structure in section response: {content[:200]}...")
                return content, tokens_used
        except json.JSONDecodeError as e:
            logger.warning(f"[WC_STRATEGY] Failed to parse JSON response: {str(e)}, using raw content")
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
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,  # GPT-4o has vision capabilities
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": image_url_for_openai}},
                        ]
                    },
                ],
                max_tokens=500,
                temperature=0.7,
            )
            
            logger.info(f"[IMAGE_ANALYSIS] Generated analysis using Chat Completions API")

            # Extract content and token usage with validation
            if not response.choices or len(response.choices) == 0:
                raise ValueError("OpenAI API returned no choices in response")
            
            choice = response.choices[0]
            if not hasattr(choice, 'message') or not choice.message:
                raise ValueError("OpenAI API returned invalid choice structure")
                
            content = choice.message.content
            if not content:
                raise ValueError("OpenAI API returned empty content - this may indicate rate limiting or API error")
                
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            generation_time = time.time() - start_time
            
            logger.debug(f"[IMAGE_ANALYSIS] OpenAI API response validated - content length: {len(content)}, tokens: {tokens_used}")

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
    def _validate_word_count(content: str, min_length: int, max_length: int, content_type: str = "content") -> Tuple[bool, int]:
        """
        Validate if content meets word count requirements
        
        Returns:
            Tuple of (is_valid, actual_word_count)
        """
        word_count = len(content.split())
        is_valid = min_length <= word_count <= max_length
        
        # Only log validation failures to reduce noise
        if not is_valid:
            diff = min_length - word_count if word_count < min_length else word_count - max_length
            logger.debug(f"[LENGTH] {content_type}: {word_count}w ({'short' if word_count < min_length else 'over'} by {diff}w)")
        
        return is_valid, word_count


    @staticmethod
    def _build_outline_system_prompt() -> str:
        """Build system prompt for outline generation using Chat Completions"""
        storytelling_manual = format_storytelling_manual_for_prompt()
        
        return f"""You are an expert YouTube script writer and content strategist. Your task is to create detailed, actionable outlines that serve as blueprints for engaging YouTube videos.

CRITICAL: You MUST respond with valid JSON only. The API is configured to enforce JSON output format.

MANDATORY VALIDATOR ENFORCEMENT:
Before creating any outline, you MUST validate against these critical requirements:

S1 HOOK VALIDATORS (MANDATORY):
- Hook duration MUST be ≤30 seconds (hard cap: 60s when justified)
- Hook MUST contain action verb in first 1-2 sentences
- Hook MUST be 3-6 sentence micro-scene with filmable action
- Hook MUST pivot to chronology within 60 seconds
- NO vague language like "high-stakes moment" without concrete dramatization

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
    def _build_outline_user_prompt(script_data: Dict[str, Any]) -> str:
        """Build user prompt for outline generation"""
        tones = script_data.get("tones", ["informative"])
        template_style = script_data.get("template_style", "medium")
        description = script_data.get("description", "")
        min_length = script_data.get("min_length", 100)
        max_length = script_data.get("max_length", 1000)

        tone_text = (
            f"Tones: {', '.join(tones)}" if len(tones) > 1 else f"Tone: {tones[0]}"
        )

        return f"""Generate DETAILED outline in JSON for:

Topic: {description} | {tone_text} | Style: {template_style} | Target: {min_length:,}-{max_length:,}w script

CRITICAL VALIDATOR ENFORCEMENT REQUIRED:
• S1: Hook ≤30s, action verbs, 3-6 sentences, pivot within 60s
• S2: 2-3 specific questions, transformation statement, loop closure plan
• S6: First value point within 10s of hook end for tutorials/listicles
• Framework: Sensory details (P02), causal connectors (P03), emotional beats (P05/P11), visual cues (P17), cliffhangers (BONUS-02)

REQUIREMENTS:
• Each section: 80-150w description + 5-8 detailed key point sentences
• Include specific examples, stories, techniques to use
• Add timing + transition guidance
• Outline depth = script length (sparse = FAILS, detailed = success)
• MUST include validator_compliance_check in JSON response

CRITICAL: Return ONLY valid JSON matching the exact schema provided in the system prompt. The API enforces JSON format automatically.

REMEMBER: Rich outline (500-800w) → proper script. Sparse outline → short script (fails)!
VALIDATOR COMPLIANCE IS MANDATORY - NO EXCEPTIONS!"""

    @staticmethod
    def _build_script_system_prompt() -> str:
        """Build system prompt for script generation using Chat Completions"""
        storytelling_manual = format_storytelling_manual_for_prompt()
        
        return f"""You are an expert YouTube script writer with extensive experience creating engaging, retention-focused video content. Your specialty is transforming detailed outlines into compelling, conversational scripts that keep viewers watching.

CRITICAL: You MUST respond with valid JSON only. The API is configured to enforce JSON output format.

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
    def _build_script_user_prompt(outline_text: str, script_data: Dict[str, Any]) -> str:
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
        tutorial_keywords = ['trick', 'tip', 'hack', 'step', 'way', 'method', 'technique', 'secret']
        is_tutorial = any(keyword in outline_text.lower() for keyword in tutorial_keywords)
        
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
Use ≤60s prologue, then pivot to Chapter 1/chronological beginning.
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
    def _check_validator_compliance(sections: List[Dict], parsed_data: Dict, template_style: str = "medium") -> Dict[str, Any]:
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
            return OpenAIScriptService._check_flexible_outline_compliance(sections, parsed_data)
        
        compliance_check = {
            "s1_hook_structure": "PASS",
            "s2_open_loops": "PASS", 
            "s6_value_delivery": "PASS",
            "framework_gaps": [],
            "overall_compliance": "PASS",
            "violations": []
        }
        
        if not sections:
            compliance_check["overall_compliance"] = "FAIL"
            compliance_check["violations"].append("No sections provided")
            return compliance_check
        
        # Check S1 Hook Structure Validators
        first_section = sections[0]
        hook_content = first_section.get("description", "") + " " + first_section.get("content", "")
        
        # S1.1: Hook duration check (look for timing indicators)
        timing = first_section.get("timing", "")
        if "minute" in timing.lower() and any(char.isdigit() for char in timing):
            # Extract duration numbers
            duration_match = re.search(r'(\d+)', timing)
            if duration_match:
                duration = int(duration_match.group(1))
                if duration > 1:  # More than 1 minute
                    compliance_check["s1_hook_structure"] = "FAIL"
                    compliance_check["violations"].append(f"S1 violation: Hook duration {duration} minutes exceeds 60s limit")
        
        # S1.2: Action verbs in first 1-2 sentences
        hook_sentences = hook_content.split('.')[:2]
        action_verbs = ['start', 'begin', 'open', 'create', 'build', 'develop', 'launch', 'introduce', 'present', 'show', 'reveal', 'demonstrate']
        has_action_verb = any(verb in sentence.lower() for sentence in hook_sentences for verb in action_verbs)
        if not has_action_verb:
            compliance_check["s1_hook_structure"] = "FAIL"
            compliance_check["violations"].append("S1 violation: No action verbs in first 1-2 sentences")
        
        # S1.3: Vague language check
        vague_terms = ['high-stakes moment', 'dramatic', 'exciting', 'interesting', 'compelling']
        has_vague_language = any(term in hook_content.lower() for term in vague_terms)
        if has_vague_language:
            compliance_check["s1_hook_structure"] = "FAIL"
            compliance_check["violations"].append("S1 violation: Contains vague language without concrete dramatization")
        
        # Check S2 Open Loops Validators
        # S2.1: Specific questions check
        question_indicators = ['?', 'how', 'what', 'why', 'when', 'where']
        has_questions = any(indicator in hook_content.lower() for indicator in question_indicators)
        if not has_questions:
            compliance_check["s2_open_loops"] = "FAIL"
            compliance_check["violations"].append("S2 violation: No specific questions in hook")
        
        # S2.2: Transformation statement check
        transformation_indicators = ['learn', 'achieve', 'transform', 'change', 'improve', 'master']
        has_transformation = any(indicator in hook_content.lower() for indicator in transformation_indicators)
        if not has_transformation:
            compliance_check["s2_open_loops"] = "FAIL"
            compliance_check["violations"].append("S2 violation: No transformation statement (Learn X to achieve Y)")
        
        # Check S6 Value Delivery Validators
        # S6.1: First value point timing (for tutorials/listicles)
        if len(sections) > 1:
            second_section = sections[1]
            second_timing = second_section.get("timing", "")
            if "second" in second_timing.lower() or "10" in second_timing:
                # Check if it's within 10 seconds
                second_match = re.search(r'(\d+)', second_timing)
                if second_match:
                    second_duration = int(second_match.group(1))
                    if second_duration > 10:
                        compliance_check["s6_value_delivery"] = "FAIL"
                        compliance_check["violations"].append(f"S6 violation: First value point starts at {second_duration}s, exceeds 10s limit")
        
        # Check Framework Requirements
        framework_gaps = []
        
        # P02: Sensory details check
        sensory_words = ['see', 'hear', 'feel', 'smell', 'taste', 'touch', 'visual', 'sound', 'texture']
        has_sensory_details = any(word in str(sections).lower() for word in sensory_words)
        if not has_sensory_details:
            framework_gaps.append("P02: Missing sensory details")
        
        # P03: Causal connectors check
        causal_connectors = ['therefore', 'because', 'but', 'however', 'thus', 'as a result']
        has_causal_connectors = any(connector in str(sections).lower() for connector in causal_connectors)
        if not has_causal_connectors:
            framework_gaps.append("P03: Missing causal connectors")
        
        # P05/P11: Emotional beats and stakes check
        emotional_words = ['stakes', 'consequences', 'risk', 'danger', 'reward', 'goal', 'obstacle']
        has_emotional_beats = any(word in str(sections).lower() for word in emotional_words)
        if not has_emotional_beats:
            framework_gaps.append("P05/P11: Missing emotional beats and stakes")
        
        # P17: Visual cues check
        visual_words = ['show', 'visual', 'graphic', 'image', 'scene', 'cut to', 'camera']
        has_visual_cues = any(word in str(sections).lower() for word in visual_words)
        if not has_visual_cues:
            framework_gaps.append("P17: Missing visual cues/editor notes")
        
        # BONUS-02: Cliffhangers check
        cliffhanger_words = ['but', 'however', 'unresolved', 'tease', 'coming up', 'next']
        has_cliffhangers = any(word in str(sections).lower() for word in cliffhanger_words)
        if not has_cliffhangers:
            framework_gaps.append("BONUS-02: Missing cliffhangers/unresolved threads")
        
        compliance_check["framework_gaps"] = framework_gaps
        
        # Overall compliance check
        if (compliance_check["s1_hook_structure"] == "FAIL" or 
            compliance_check["s2_open_loops"] == "FAIL" or 
            compliance_check["s6_value_delivery"] == "FAIL" or 
            len(framework_gaps) > 2):  # Allow up to 2 framework gaps
            compliance_check["overall_compliance"] = "FAIL"
        
        return compliance_check

    @staticmethod
    def _check_flexible_outline_compliance(sections: List[Dict], parsed_data: Dict) -> Dict[str, Any]:
        """Relaxed validation for Flexible Outline template (100-300 words)"""
        compliance_check = {
            "s1_hook_structure": "N/A",  # Outlines don't need full hook validation
            "s2_open_loops": "N/A",
            "s6_value_delivery": "N/A",
            "framework_gaps": [],
            "overall_compliance": "PASS",
            "violations": [],
            "template_type": "flexible_outline"
        }
        
        # Only check basic structure
        if not sections or len(sections) < 3:
            compliance_check["overall_compliance"] = "FAIL"
            compliance_check["violations"].append("Flexible outline must have at least 3 sections")
        
        # Check total word count (100-300 range)
        total_words = sum(len(s.get("description", "").split()) for s in sections)
        if total_words < 100 or total_words > 300:
            compliance_check["overall_compliance"] = "FAIL"
            compliance_check["violations"].append(
                f"Flexible outline word count {total_words} outside range 100-300"
            )
        
        return compliance_check

    @staticmethod
    def _check_script_validator_compliance(full_text: str, sections: List[Dict], parsed_data: Dict) -> Dict[str, Any]:
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
            "violations": []
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
        hook_sentences = hook_content.split('.')[:2]
        action_verbs = ['start', 'begin', 'open', 'create', 'build', 'develop', 'launch', 'introduce', 'present', 'show', 'reveal', 'demonstrate', 'dive', 'jump', 'cut']
        has_action_verb = any(verb in sentence.lower() for sentence in hook_sentences for verb in action_verbs)
        if not has_action_verb:
            compliance_check["s1_hook_structure"] = "FAIL"
            compliance_check["violations"].append("S1 violation: No action verbs in first 1-2 sentences")
        
        # S1.3: Vague language check
        vague_terms = ['high-stakes moment', 'dramatic', 'exciting', 'interesting', 'compelling', 'atmospheric', 'eerie', 'muted hum', 'still air']
        has_vague_language = any(term in hook_content.lower() for term in vague_terms)
        if has_vague_language:
            compliance_check["s1_hook_structure"] = "FAIL"
            compliance_check["violations"].append("S1 violation: Contains vague language without concrete dramatization")
        
        # S1.4: Check for 6+ minute prologues (critical failure)
        if estimated_hook_duration > 6:
            compliance_check["s1_hook_structure"] = "FAIL"
            compliance_check["violations"].append(f"S1 CRITICAL FAILURE: {estimated_hook_duration:.1f} minute prologue - this is a complete failure")
        
        # Check S2 Open Loops Validators
        # S2.1: Specific questions check
        question_indicators = ['?', 'how', 'what', 'why', 'when', 'where']
        has_questions = any(indicator in hook_content.lower() for indicator in question_indicators)
        if not has_questions:
            compliance_check["s2_open_loops"] = "FAIL"
            compliance_check["violations"].append("S2 violation: No specific questions in hook")
        
        # S2.2: Transformation statement check
        transformation_indicators = ['learn', 'achieve', 'transform', 'change', 'improve', 'master', 'tricks', 'tips', 'secrets']
        has_transformation = any(indicator in hook_content.lower() for indicator in transformation_indicators)
        if not has_transformation:
            compliance_check["s2_open_loops"] = "FAIL"
            compliance_check["violations"].append("S2 violation: No transformation statement (Learn X to achieve Y)")
        
        # S2.3: Questions buried in monologue check
        if len(hook_content.split()) > 200:  # Very long hook
            compliance_check["s2_open_loops"] = "FAIL"
            compliance_check["violations"].append("S2 violation: Questions buried in long monologue")
        
        # Check S6 Value Delivery Validators
        # S6.1: First value point timing (for tutorials/listicles)
        if len(sections) > 1:
            second_section = sections[1]
            second_content = second_section.get("content", "")
            # Look for value indicators in second section
            value_indicators = ['trick', 'tip', 'hack', 'secret', 'method', 'technique', 'step', 'way']
            has_value_indicators = any(indicator in second_content.lower() for indicator in value_indicators)
            
            if has_value_indicators:
                # Estimate timing for second section
                second_word_count = len(second_content.split())
                second_duration = second_word_count / 150  # minutes
                if second_duration > 0.17:  # More than 10 seconds
                    compliance_check["s6_value_delivery"] = "FAIL"
                    compliance_check["violations"].append(f"S6 violation: First value point starts at {second_duration*60:.0f}s, exceeds 10s limit")
        
        # Check Framework Requirements
        framework_gaps = []
        
        # P02: Sensory details check
        sensory_words = ['see', 'hear', 'feel', 'smell', 'taste', 'touch', 'visual', 'sound', 'texture', 'scene', 'show']
        has_sensory_details = any(word in full_text.lower() for word in sensory_words)
        if not has_sensory_details:
            framework_gaps.append("P02: Missing sensory details")
        
        # P03: Causal connectors check
        causal_connectors = ['therefore', 'because', 'but', 'however', 'thus', 'as a result', 'so', 'then']
        has_causal_connectors = any(connector in full_text.lower() for connector in causal_connectors)
        if not has_causal_connectors:
            framework_gaps.append("P03: Missing causal connectors")
        
        # P05/P11: Emotional beats and stakes check
        emotional_words = ['stakes', 'consequences', 'risk', 'danger', 'reward', 'goal', 'obstacle', 'pressure', 'challenge']
        has_emotional_beats = any(word in full_text.lower() for word in emotional_words)
        if not has_emotional_beats:
            framework_gaps.append("P05/P11: Missing emotional beats and stakes")
        
        # P07: Simplify check - look for unnecessary tangents
        tangent_indicators = ['meanwhile', 'incidentally', 'by the way', 'speaking of which', 'on a side note']
        has_tangents = any(indicator in full_text.lower() for indicator in tangent_indicators)
        if has_tangents:
            framework_gaps.append("P07: Contains unnecessary tangents")
        
        # P09: Jargon/clichés check
        cliche_indicators = ['storm of thoughts', 'silent war', 'beacon in the darkness', 'journey to mastery', 'relentless pursuit', 'whirling inside']
        has_cliches = any(indicator in full_text.lower() for indicator in cliche_indicators)
        if has_cliches:
            framework_gaps.append("P09: Contains clichés and jargon")
        
        # P10: Reading level check - look for overly complex sentences
        complex_indicators = ['notwithstanding', 'furthermore', 'moreover', 'consequently', 'subsequently']
        has_complex_language = any(indicator in full_text.lower() for indicator in complex_indicators)
        if has_complex_language:
            framework_gaps.append("P10: Contains overly complex language")
        
        # P13: Concision check - look for verbose constructions
        verbose_indicators = ['in order to', 'due to the fact that', 'it is important to note that', 'at this point in time']
        has_verbose_constructions = any(indicator in full_text.lower() for indicator in verbose_indicators)
        if has_verbose_constructions:
            framework_gaps.append("P13: Contains verbose constructions")
        
        # P17: Visual cues check
        visual_words = ['show', 'visual', 'graphic', 'image', 'scene', 'cut to', 'camera', '[show', '[cut', '[visual']
        has_visual_cues = any(word in full_text.lower() for word in visual_words)
        if not has_visual_cues:
            framework_gaps.append("P17: Missing visual cues/editor notes")
        
        # BONUS-02: Cliffhangers check
        cliffhanger_words = ['but', 'however', 'unresolved', 'tease', 'coming up', 'next', 'stay tuned']
        has_cliffhangers = any(word in full_text.lower() for word in cliffhanger_words)
        if not has_cliffhangers:
            framework_gaps.append("BONUS-02: Missing cliffhangers/unresolved threads")
        
        compliance_check["framework_gaps"] = framework_gaps
        
        # Overall compliance check
        if (compliance_check["s1_hook_structure"] == "FAIL" or 
            compliance_check["s2_open_loops"] == "FAIL" or 
            compliance_check["s6_value_delivery"] == "FAIL" or 
            len(framework_gaps) > 3):  # Allow up to 3 framework gaps
            compliance_check["overall_compliance"] = "FAIL"
        
        return compliance_check
