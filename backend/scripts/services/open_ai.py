# services/openai_service.py
import base64
import json
import logging
import re
import time
from typing import Any, Dict, List, Tuple, Optional

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
                    
                    return {
                        "sections": sections, 
                        "section_order": section_order,
                        "outline_text": outline_text_raw
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

                return {"sections": sections, "section_order": default_section_order}
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
        Generate YouTube titles using the OpenAI Assistant API (with vector store KB).
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

            # Create thread
            thread = client.beta.threads.create()

            # Build the message content
            system_prompt = OpenAIScriptService._build_title_system_prompt()
            user_prompt = OpenAIScriptService._build_title_user_prompt(
                prompt, title_count, tones
            )

            # Add message to thread (system + user)
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=[
                    {"type": "text", "text": system_prompt},
                    {"type": "text", "text": user_prompt},
                ],
            )

            # Run the assistant with explicit file_search requirement
            # Force file_search to ensure knowledge base is used
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=settings.OPENAI_ASSISTANT_ID_TITLES,
                # Note: tool_choice forces the assistant to use file_search
                # Remove this if you want the assistant to decide when to use it
                # tool_choice={"type": "file_search"}  # Uncomment to force file search
            )
            
            logger.info(f"[ASSISTANT_RUN] Started title generation run: {run.id}")

            # Wait for completion
            titles_content, tokens_used = (
                OpenAIScriptService._wait_for_assistant_completion(
                    client, thread.id, run.id
                )
            )

            generation_time = time.time() - start_time

            # Parse JSON titles
            titles = OpenAIScriptService._parse_generated_titles(titles_content)
            
            # Calculate word count
            word_count = sum(len(t.get("title", "").split()) for t in titles)

            # Extract file search info
            file_search_used, file_search_snippets = OpenAIScriptService._extract_file_search_info(
                client, thread.id, run.id
            )

            metadata = {
                "tokens_used": tokens_used,
                "generation_time": generation_time,
                "model": "gpt-4-assistant",
                "assistant_id": settings.OPENAI_ASSISTANT_ID_TITLES,
                "vector_store_id": settings.OPENAI_VECTOR_STORE_ID_TITLES,
                "thread_id": thread.id,
                "run_id": run.id,
                "title_count": len(titles),
                "file_search_used": file_search_used,
                "word_count": word_count,
            }

            if tones:
                metadata["tones_used"] = tones

            # Save run log to database
            if save_log:
                OpenAIScriptService._save_run_log(
                    user=user,
                    thread_id=thread.id,
                    run_id=run.id,
                    assistant_id=settings.OPENAI_ASSISTANT_ID_TITLES,
                    tokens_used=tokens_used,
                    word_count=word_count,
                    file_search_used=file_search_used,
                    file_search_snippets=file_search_snippets,
                    run_type="title_generation",
                    generation_time=generation_time,
                    model="gpt-4-assistant",
                )

            return titles, metadata

        except Exception as e:
            logger.error(f"Assistant title generation failed: {str(e)}")
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
        Generate outline using OpenAI Assistant API with vector store knowledge base
        
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

            # Create thread
            thread = client.beta.threads.create()

            # Build message content (simplified - let assistant use its configured instructions)
            message_content = OpenAIScriptService._build_assistant_outline_message(
                script_data
            )

            # Add message to thread (vector store is already attached to the assistant)
            client.beta.threads.messages.create(
                thread_id=thread.id, role="user", content=message_content
            )

            # Run the assistant with additional length enforcement instructions
            # Force file_search to ensure knowledge base is used
            
            # Calculate expected duration (assuming ~150 words per minute narration speed)
            min_duration = min_length / 150
            max_duration = max_length / 150
            suggested_sections = max(3, min_length // 500)
            max_sections = max(5, max_length // 400)
            words_per_section_min = min_length // suggested_sections
            words_per_section_max = max_length // suggested_sections
            
            length_instructions = f"""
🚨 OUTLINE FOR {min_length:,}-{max_length:,} WORD SCRIPT ({min_duration:.1f}-{max_duration:.1f} min video)

STRUCTURE: {suggested_sections}-{max_sections} detailed sections (each supports {words_per_section_min:,}-{words_per_section_max:,}w script)

EACH SECTION MUST HAVE:
• Description: 80-150 words (NOT 1-2 sentences!)
• Key points: 5-8 detailed sentences of specific guidance
• Timing estimate
• Transition to next section
• Specific examples/stories/angles to include

CRITICAL: Outline detail = script length
• Sparse outline → short script (FAILS)
• Rich outline (500-800w total) → proper script length

VERIFY: Each section has 80-150w description + 5-8 detailed key points
"""
            
            # Set reasonable max completion tokens for outline (typically 500-1000 words)
            # Outlines are much shorter than scripts
            max_outline_tokens = 3000  # Enough for detailed outline with JSON structure
            
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=settings.OPENAI_ASSISTANT_ID_OUTLINE,
                additional_instructions=length_instructions,
                # tool_choice={"type": "file_search"},
                max_completion_tokens=max_outline_tokens
            )
            
            logger.info(f"[ASSISTANT_RUN] Set max_completion_tokens to {max_outline_tokens} for outline")
            
            logger.info(f"[ASSISTANT_RUN] Started outline generation run: {run.id}")

            # Wait for completion
            outline_text, tokens_used = (
                OpenAIScriptService._wait_for_assistant_completion(
                    client, thread.id, run.id
                )
            )

            generation_time = time.time() - start_time

            # Parse outline structure
            outline_data = OpenAIScriptService._parse_outline_structure(outline_text)
            
            # Calculate word count
            word_count = len(outline_text.split())

            # Extract file search info
            file_search_used, file_search_snippets = OpenAIScriptService._extract_file_search_info(
                client, thread.id, run.id
            )

            metadata = {
                "tokens_used": tokens_used,
                "generation_time": generation_time,
                "model": "gpt-4-assistant",
                "assistant_id": settings.OPENAI_ASSISTANT_ID_OUTLINE,
                "vector_store_id": settings.OPENAI_VECTOR_STORE_ID_SCRIPT,
                "thread_id": thread.id,
                "run_id": run.id,
                "file_search_used": file_search_used,
                "word_count": word_count,
            }

            # Save run log to database
            if save_log:
                OpenAIScriptService._save_run_log(
                    user=user,
                    thread_id=thread.id,
                    run_id=run.id,
                    assistant_id=settings.OPENAI_ASSISTANT_ID_OUTLINE,
                    tokens_used=tokens_used,
                    word_count=word_count,
                    file_search_used=file_search_used,
                    file_search_snippets=file_search_snippets,
                    run_type="outline_generation",
                    generation_time=generation_time,
                    model="gpt-4-assistant",
                )

            return outline_text, outline_data, metadata

        except Exception as e:
            logger.error(f"Assistant outline generation failed: {str(e)}")
            raise

    @staticmethod
    def generate_full_script_with_assistant(
        outline_text: str, 
        script_data: Dict[str, Any],
        user=None,
        save_log: bool = True,
        max_retries: int = 4,
    ) -> Tuple[str, List[Dict], Dict[str, Any]]:
        """
        Generate full script using OpenAI Assistant API with vector store knowledge base
        Includes word count validation and retry logic.
        
        Args:
            outline_text: The outline text to generate script from
            script_data: Dictionary containing script parameters
            user: User object for logging (optional)
            save_log: Whether to save run log to database (default: True)
            max_retries: Maximum retry attempts if length doesn't match (default: 4)
        """
        min_length = script_data.get("min_length", 1000)
        max_length = script_data.get("max_length", 5000)
        
        # Track previous attempt word count for better retry messaging
        previous_word_count = 0
        
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                client = get_openai_client()

                # Create thread
                thread = client.beta.threads.create()

                # Build script generation message (simplified)
                message_content = OpenAIScriptService._build_assistant_script_message(
                    outline_text, script_data
                )

                # Add message to thread (vector store is already attached to the assistant)
                client.beta.threads.messages.create(
                    thread_id=thread.id, role="user", content=message_content
                )

                # Run the assistant with additional length enforcement instructions
                # Force file_search to ensure knowledge base is used
                
                # Calculate expected duration (assuming ~150 words per minute narration speed)
                min_duration = min_length / 150
                max_duration = max_length / 150
                target_mid = (min_length + max_length) // 2
                target_duration = target_mid / 150
                
                # Add safety buffer to target - aim higher than minimum to account for AI variability
                safety_buffer = int(min_length * 0.1)  # 10% buffer
                safe_target = target_mid + safety_buffer
                
                length_instructions = f"""
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

VERIFY: full_text field has {min_length:,}+ words before submitting.
"""
                
                if attempt > 0:
                    words_needed = min_length - previous_word_count if previous_word_count > 0 else min_length
                    length_instructions += f"\n⚠️ RETRY #{attempt}: Previous={previous_word_count:,}w, Need +{words_needed:,}w more. Expand examples & stories!"
                
                # Calculate reasonable max completion tokens based on target length
                # For a 3000 word script: ~4000 tokens for text + 2000 for JSON structure = 6000 total
                # Add 50% buffer for safety
                estimated_tokens = int((max_length * 1.5) + 2000)  # 1.5 tokens per word + JSON overhead
                max_tokens = min(estimated_tokens, 10000)  # Cap at 10k to prevent excessive usage
                
                run = client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=settings.OPENAI_ASSISTANT_ID_SCRIPT,
                    additional_instructions=length_instructions,
                    # tool_choice={"type": "file_search"},
                    max_completion_tokens=max_tokens
                )
                
                logger.info(f"[ASSISTANT_RUN] Set max_completion_tokens to {max_tokens} (target script: {max_length} words)")
                
                logger.info(f"[ASSISTANT_RUN] Started script generation run: {run.id} (Attempt {attempt + 1}/{max_retries + 1})")

                # Wait for completion
                script_content, tokens_used = (
                    OpenAIScriptService._wait_for_assistant_completion(
                        client, thread.id, run.id
                    )
                )

                generation_time = time.time() - start_time

                # Parse script sections
                sections = OpenAIScriptService._parse_script_sections(script_content)
                
                # Extract actual script text from JSON for accurate word count
                actual_script_text = script_content  # Default to full content
                try:
                    script_data = json.loads(script_content)
                    if isinstance(script_data, dict) and "full_text" in script_data:
                        actual_script_text = script_data["full_text"]
                except json.JSONDecodeError:
                    # Not JSON, use raw content
                    pass
                
                # Calculate word count and validate using actual script text
                word_count = len(actual_script_text.split())
                is_valid, actual_word_count = OpenAIScriptService._validate_word_count(
                    actual_script_text, min_length, max_length, "Script"
                )

                # Extract file search info
                file_search_used, file_search_snippets = OpenAIScriptService._extract_file_search_info(
                    client, thread.id, run.id
                )

                metadata = {
                    "tokens_used": tokens_used,
                    "generation_time": generation_time,
                    "model": "gpt-4-assistant",
                    "assistant_id": settings.OPENAI_ASSISTANT_ID_SCRIPT,
                    "vector_store_id": settings.OPENAI_VECTOR_STORE_ID_SCRIPT,
                    "thread_id": thread.id,
                    "run_id": run.id,
                    "file_search_used": file_search_used,
                    "word_count": word_count,
                    "length_valid": is_valid,
                    "attempt": attempt + 1,
                }

                # If length is valid or this is the last attempt, return the result
                if is_valid:
                    logger.info(f"[LENGTH_CHECK] ✓ Script generation successful with valid length on attempt {attempt + 1}")
                    
                    # Save run log to database
                    if save_log:
                        OpenAIScriptService._save_run_log(
                            user=user,
                            thread_id=thread.id,
                            run_id=run.id,
                            assistant_id=settings.OPENAI_ASSISTANT_ID_SCRIPT,
                            tokens_used=tokens_used,
                            word_count=word_count,
                            file_search_used=file_search_used,
                            file_search_snippets=file_search_snippets,
                            run_type="script_generation",
                            generation_time=generation_time,
                            model="gpt-4-assistant",
                        )
                    
                    return script_content, sections, metadata
                
                elif attempt == max_retries:
                    # Last attempt, return even if invalid
                    logger.warning(f"[LENGTH_CHECK] ⚠️ Returning script after {max_retries + 1} attempts. Word count {word_count} is outside range {min_length}-{max_length}")
                    
                    # Save run log to database
                    if save_log:
                        OpenAIScriptService._save_run_log(
                            user=user,
                            thread_id=thread.id,
                            run_id=run.id,
                            assistant_id=settings.OPENAI_ASSISTANT_ID_SCRIPT,
                            tokens_used=tokens_used,
                            word_count=word_count,
                            file_search_used=file_search_used,
                            file_search_snippets=file_search_snippets,
                            run_type="script_generation",
                            generation_time=generation_time,
                            model="gpt-4-assistant",
                        )
                    
                    return script_content, sections, metadata
                
                else:
                    # Retry - save word count for next attempt's messaging
                    previous_word_count = word_count
                    logger.warning(f"[LENGTH_CHECK] Retrying script generation. Current: {word_count} words, Required: {min_length}-{max_length}")
                    continue

            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"Assistant script generation failed after {max_retries + 1} attempts: {str(e)}")
                    raise
                else:
                    # Track word count even on exception if available
                    if 'word_count' in locals():
                        previous_word_count = word_count
                    
                    # Check if it's a rate limit error and add delay
                    error_str = str(e).lower()
                    if 'rate_limit' in error_str or 'rate limit' in error_str:
                        wait_time = 10  # Wait 10 seconds between attempts on rate limit
                        logger.warning(f"Rate limit detected, waiting {wait_time}s before retry")
                        time.sleep(wait_time)
                    
                    logger.warning(f"Attempt {attempt + 1} failed, retrying: {str(e)}")
                    continue

    @staticmethod
    def analyze_image_with_assistant(
        image_file=None, 
        image_url=None,
        user=None,
        save_log: bool = True,
    ) -> Tuple[str, str]:
        """
        Analyze an image using OpenAI Assistant API with Vision capabilities and vector store knowledge base
        
        Args:
            image_file: Django UploadedFile object (optional)
            image_url: URL of the image to analyze (optional)
            user: User object for logging (optional)
            save_log: Whether to save run log to database (default: True)
        """
        try:
            start_time = time.time()
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

Use the knowledge base files to apply appropriate storytelling rules and hook techniques for creating an engaging title and description.

Note: Please provide your response in a clear, structured format (not JSON)."""

            # Add message to thread (vector store is already attached to the assistant)
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=[
                    {"type": "text", "text": message_content},
                    {"type": "image_url", "image_url": {"url": image_url_for_openai}},
                ],
            )

            # Run the assistant (it already has detailed instructions configured)
            # Force file_search to ensure knowledge base is used
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=settings.OPENAI_ASSISTANT_ID_OUTLINE,
                # Note: tool_choice forces the assistant to use file_search
                # Remove this if you want the assistant to decide when to use it
                # tool_choice={"type": "file_search"}  # Uncomment to force file search
            )
            
            logger.info(f"[ASSISTANT_RUN] Started image analysis run: {run.id}")

            # Wait for completion
            content, tokens_used = OpenAIScriptService._wait_for_assistant_completion(
                client, thread.id, run.id
            )
            
            generation_time = time.time() - start_time

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

            # Extract file search info
            file_search_used, file_search_snippets = OpenAIScriptService._extract_file_search_info(
                client, thread.id, run.id
            )

            # Save run log to database
            if save_log:
                OpenAIScriptService._save_run_log(
                    user=user,
                    thread_id=thread.id,
                    run_id=run.id,
                    assistant_id=settings.OPENAI_ASSISTANT_ID_OUTLINE,
                    tokens_used=tokens_used,
                    word_count=word_count,
                    file_search_used=file_search_used,
                    file_search_snippets=file_search_snippets,
                    run_type="image_analysis",
                    generation_time=generation_time,
                    model="gpt-4-assistant",
                )

            return title, description

        except Exception as e:
            logger.error(f"Assistant image analysis failed: {str(e)}")
            return "Image Analysis", "An image was provided for analysis."

    @staticmethod
    def _extract_file_search_info(client, thread_id: str, run_id: str) -> Tuple[bool, List[Dict]]:
        """
        Extract file search usage and snippets from run steps
        
        Returns:
            Tuple of (file_search_used, file_search_snippets)
        """
        try:
            logger.info(f"[FILE_SEARCH_CHECK] Checking file search usage for run_id: {run_id}")
            
            # Get run steps to check for file_search tool usage
            run_steps = client.beta.threads.runs.steps.list(
                thread_id=thread_id,
                run_id=run_id
            )
            
            logger.info(f"[FILE_SEARCH_CHECK] Found {len(run_steps.data)} steps in run")
            
            file_search_used = False
            file_search_snippets = []
            
            for idx, step in enumerate(run_steps.data):
                logger.info(f"[FILE_SEARCH_CHECK] Step {idx + 1}: type={getattr(step, 'type', 'unknown')}, "
                           f"step_details_type={getattr(step.step_details, 'type', 'unknown') if hasattr(step, 'step_details') else 'no_details'}")
                
                # Check if this step used file_search tool
                if hasattr(step, 'step_details') and hasattr(step.step_details, 'type'):
                    if step.step_details.type == 'tool_calls':
                        tool_calls = step.step_details.tool_calls
                        logger.info(f"[FILE_SEARCH_CHECK] Step {idx + 1} has {len(tool_calls)} tool calls")
                        
                        for tool_idx, tool_call in enumerate(tool_calls):
                            tool_type = getattr(tool_call, 'type', 'unknown')
                            logger.info(f"[FILE_SEARCH_CHECK] Tool call {tool_idx + 1}: type={tool_type}")
                            
                            if tool_type == 'file_search':
                                file_search_used = True
                                logger.info(f"[FILE_SEARCH_CHECK] ✓ FILE_SEARCH TOOL DETECTED in step {idx + 1}")
                                
                                # Extract snippets if available
                                if hasattr(tool_call, 'file_search') and hasattr(tool_call.file_search, 'results'):
                                    results = tool_call.file_search.results
                                    logger.info(f"[FILE_SEARCH_CHECK] Found {len(results)} file search results")
                                    
                                    for res_idx, result in enumerate(results[:3]):  # Limit to 3 samples
                                        snippet = {
                                            'file_id': getattr(result, 'file_id', None),
                                            'file_name': getattr(result, 'file_name', None),
                                            'score': getattr(result, 'score', None),
                                        }
                                        
                                        logger.info(f"[FILE_SEARCH_CHECK] Result {res_idx + 1}: "
                                                   f"file_name={snippet.get('file_name', 'N/A')}, "
                                                   f"score={snippet.get('score', 'N/A')}")
                                        
                                        # Add content snippet if available
                                        if hasattr(result, 'content') and result.content:
                                            content_items = result.content[:1]  # Take first content item
                                            for content_item in content_items:
                                                if hasattr(content_item, 'text'):
                                                    snippet['text'] = content_item.text[:200]  # Limit to 200 chars
                                                    logger.info(f"[FILE_SEARCH_CHECK] Content preview: {snippet['text'][:100]}...")
                                        
                                        file_search_snippets.append(snippet)
                                else:
                                    logger.warning(f"[FILE_SEARCH_CHECK] file_search tool detected but no results available")
            
            if file_search_used:
                logger.info(f"[FILE_SEARCH_CHECK] ✓ FINAL RESULT: File search WAS used, {len(file_search_snippets)} snippets extracted")
            else:
                logger.warning(f"[FILE_SEARCH_CHECK] ✗ FINAL RESULT: File search NOT detected in any steps")
            
            return file_search_used, file_search_snippets
            
        except Exception as e:
            logger.error(f"[FILE_SEARCH_CHECK] Failed to extract file search info: {str(e)}", exc_info=True)
            return False, []
    
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
        
        if is_valid:
            logger.info(f"[LENGTH_CHECK] ✓ {content_type} word count {word_count} is within range {min_length}-{max_length}")
        else:
            logger.warning(f"[LENGTH_CHECK] ✗ {content_type} word count {word_count} is OUTSIDE range {min_length}-{max_length}")
            if word_count < min_length:
                logger.warning(f"[LENGTH_CHECK] Content is {min_length - word_count} words SHORT")
            else:
                logger.warning(f"[LENGTH_CHECK] Content is {word_count - max_length} words OVER")
        
        return is_valid, word_count

    @staticmethod
    def _wait_for_assistant_completion(
        client, thread_id: str, run_id: str, max_retries: int = 3
    ) -> Tuple[str, int]:
        """Wait for assistant run to complete and return content"""
        logger.info(f"[ASSISTANT_RUN] Waiting for completion: thread_id={thread_id}, run_id={run_id}")
        
        retry_count = 0
        while True:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            
            logger.debug(f"[ASSISTANT_RUN] Current status: {run.status}")

            if run.status == "completed":
                logger.info(f"[ASSISTANT_RUN] ✓ Run completed successfully")
                
                # Log tool usage if available
                if hasattr(run, 'tools') and run.tools:
                    tool_names = [getattr(tool, 'type', 'unknown') for tool in run.tools]
                    logger.info(f"[ASSISTANT_RUN] Tools available on assistant: {tool_names}")
                
                # Get the latest message
                messages = client.beta.threads.messages.list(
                    thread_id=thread_id, limit=1
                )

                content = messages.data[0].content[0].text.value
                tokens_used = run.usage.total_tokens if run.usage else 0
                
                logger.info(f"[ASSISTANT_RUN] Response length: {len(content)} chars, Tokens used: {tokens_used}")

                return content, tokens_used

            elif run.status in ["failed", "cancelled", "expired"]:
                # Get detailed error information
                error_details = "No error details available"
                error_code = "unknown"
                if hasattr(run, 'last_error') and run.last_error:
                    error_code = getattr(run.last_error, 'code', 'unknown')
                    error_message = getattr(run.last_error, 'message', 'unknown')
                    error_details = f"Code: {error_code}, Message: {error_message}"
                
                # Handle rate limit errors with retry
                if error_code == 'rate_limit_exceeded' and retry_count < max_retries:
                    retry_count += 1
                    
                    # Try to parse wait time from error message
                    wait_time = 2 ** retry_count  # Default exponential backoff
                    if 'Please try again in' in error_message:
                        match = re.search(r'try again in ([\d.]+)s', error_message)
                        if match:
                            suggested_wait = float(match.group(1))
                            wait_time = max(suggested_wait, wait_time)
                    
                    logger.warning(f"[RATE_LIMIT] Rate limit hit. Retry {retry_count}/{max_retries} after {wait_time:.1f}s")
                    logger.info(f"[RATE_LIMIT] Error message: {error_message}")
                    time.sleep(wait_time)
                    
                    # Create a new run with the same parameters
                    try:
                        # Get the original run details to recreate it
                        new_run = client.beta.threads.runs.create(
                            thread_id=thread_id,
                            assistant_id=run.assistant_id,
                            instructions=run.instructions,
                            tool_choice=run.tool_choice,
                        )
                        run_id = new_run.id
                        logger.info(f"[RATE_LIMIT] Created new run {run_id} after rate limit")
                        continue
                    except Exception as retry_error:
                        logger.error(f"[RATE_LIMIT] Failed to create retry run: {str(retry_error)}")
                        raise
                
                logger.error(f"[ASSISTANT_RUN] ✗ Run failed with status: {run.status}")
                logger.error(f"[ASSISTANT_RUN] Error details: {error_details}")
                
                # Log the full run object for debugging
                logger.error(f"[ASSISTANT_RUN] Full run details: {run}")
                
                raise Exception(f"Run failed with status: {run.status}. Details: {error_details}")

            time.sleep(1)  # Wait before checking again

    @staticmethod
    def _build_assistant_outline_message(script_data: Dict[str, Any]) -> str:
        """Build simplified message for outline generation - let assistant use its configured instructions"""
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

Use knowledge base storytelling rules for this topic/tone.

REQUIREMENTS (CRITICAL):
• Each section: 80-150w description + 5-8 detailed key point sentences
• Include specific examples, stories, techniques to use
• Add timing + transition guidance
• Outline depth = script length (sparse = FAILS, detailed = success)

STRUCTURE:
• NO document references/citations
• Clean, engaging sections
• Descriptions explain WHAT to cover + HOW to approach
• Actionable key points (not vague bullets)
• Suggest examples, analogies, rhetorical questions

Return JSON: sections array with title, description, key_points, timing, transition, content

REMEMBER: Rich outline (500-800w) → proper script. Sparse outline → short script (fails)!"""

    @staticmethod
    def _build_assistant_script_message(
        outline_text: str, script_data: Dict[str, Any]
    ) -> str:
        """Build simplified message for script generation - let assistant use its configured instructions"""
        tones = script_data.get("tones", ["informative"])
        min_length = script_data.get("min_length", 1000)
        max_length = script_data.get("max_length", 5000)

        tone_text = (
            f"Tones: {', '.join(tones)}" if len(tones) > 1 else f"Tone: {tones[0]}"
        )

        # Calculate concrete targets
        target_words = (min_length + max_length) // 2
        
        return f"""Expert YouTube script writer: Generate complete script from outline below.

🎯 MANDATORY: {min_length:,}-{max_length:,} WORDS in full_text field (Target: {target_words:,})
Under {min_length:,} = REJECTION

PER-SECTION FORMULA:
- Hook: 400-500w | Each main section: 450-550w | Conclusion: 300-400w

450W SECTION STRUCTURE:
1. Intro (80-100w) 2. Point 1 w/example (100-120w) 3. Point 2 w/example (100-120w) 
4. Point 3 w/example (100-120w) 5. Transition (50-80w)

EXPAND WITH:
• Examples: Concrete stories (50-100w each)
• Elaboration: what/why/how (3-4 sentences vs 1)
• Analogies: Familiar comparisons
• Transitions: 2-3 sentences between sections
• Engagement: Questions, direct address
• Context: "Why this matters" for all points

CRITICAL:
- Follow outline structure EXACTLY, preserve section titles/apostrophes as-is
- {tone_text}
- Use knowledge base storytelling rules
- NO document references/citations
- Write for direct narration
- Verify full_text ≥{min_length:,}w before submitting

PROVIDED OUTLINE TO FOLLOW:
{outline_text}

STRICT SECTION ORDER REQUIREMENTS:
1. Use the EXACT section titles from the outline in the SAME order
2. Do not skip, reorder, or combine sections
3. CRITICAL: If the outline contains a "section_order" array, use it to determine the exact sequence of sections
4. The section_order array contains the correct order of sections (e.g., [0, 1, 2, 3, 4])
5. Each script section must correspond to the outline sections in the order specified by section_order
6. Maintain the exact chronological flow from the outline using section_order as the guide

INSTRUCTIONS:
1. Parse the outline to extract the section_order array if present
2. Use section_order to determine the correct sequence of sections
3. Convert each outline section into engaging script content IN THE ORDER specified by section_order
4. Use the exact section titles from the outline, following the section_order sequence
5. Transform key points into narrative script format while preserving structure
6. Use storytelling techniques from the knowledge base to make it engaging
7. Ensure the script flows naturally from section to section as specified by section_order
8. Do not add, remove, or reorder sections - follow the section_order array strictly
9. Each script section should have the same title as its corresponding outline section in the correct order

Return your response in JSON format with full_text and sections array, ensuring sections follow the exact order specified by the section_order array."""
