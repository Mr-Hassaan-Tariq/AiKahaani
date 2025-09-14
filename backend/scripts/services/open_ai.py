# services/openai_service.py
import openai
import time
from django.conf import settings
from typing import Dict, Any, Tuple
import logging

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
                        "content": "You are an expert YouTube script writer. Create engaging, well-structured script outlines."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )

            generation_time = time.time() - start_time
            outline_text = response.choices[0].message.content

            # Parse the outline into structured data
            outline_data = OpenAIScriptService._parse_outline_structure(outline_text)

            metadata = {
                'tokens_used': response.usage.total_tokens,
                'generation_time': generation_time,
                'model': 'gpt-4'
            }

            return outline_text, outline_data, metadata

        except Exception as e:
            logger.error(f"OpenAI outline generation failed: {str(e)}")
            raise

    @staticmethod
    def generate_full_script(outline_text: str, script_data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
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
                        "content": "You are an expert YouTube script writer. Create engaging, detailed scripts with natural flow and clear structure."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.8
            )

            generation_time = time.time() - start_time
            script_content = response.choices[0].message.content

            # Parse script into sections
            sections = OpenAIScriptService._parse_script_sections(script_content)

            metadata = {
                'tokens_used': response.usage.total_tokens,
                'generation_time': generation_time,
                'model': 'gpt-4'
            }

            return script_content, sections, metadata

        except Exception as e:
            logger.error(f"OpenAI script generation failed: {str(e)}")
            raise

    @staticmethod
    def _build_outline_prompt(script_data: Dict[str, Any]) -> str:
        """Build prompt for outline generation"""
        tone = script_data.get('tone', 'informative')
        template_style = script_data.get('template_style', 'medium')
        description = script_data.get('description', '')
        target_length = script_data.get('length', 500)

        return f"""
Create a detailed script outline for a YouTube video with the following requirements:

Topic: {description}
Tone: {tone}
Style: {template_style}
Target Length: ~{target_length} words

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

Make it engaging and suitable for the {tone} tone.
"""

    @staticmethod
    def _build_script_prompt(outline_text: str, script_data: Dict[str, Any]) -> str:
        """Build prompt for full script generation"""
        tone = script_data.get('tone', 'informative')

        return f"""
Based on the following outline, write a complete, detailed YouTube script:

OUTLINE:
{outline_text}

REQUIREMENTS:
- Tone: {tone}
- Write in a conversational, engaging style
- Include natural transitions between sections
- Add specific examples and details
- Write exactly what the speaker should say
- Include [PAUSE], [VISUAL], or [EMPHASIS] cues where helpful
- Make it flow naturally when spoken aloud

Write the complete script with natural dialogue and engaging content.
"""

    @staticmethod
    def _parse_outline_structure(outline_text: str) -> Dict[str, Any]:
        """Parse outline text into structured data"""
        sections = []
        current_section = None
        
        lines = outline_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect main section headers (numbered sections like "1. Hook/Opening")
            if line and line[0].isdigit() and '.' in line and not line.startswith('-'):
                # Save previous section if exists
                if current_section:
                    sections.append(current_section)
                
                # Start new main section
                current_section = {
                    'title': line,
                    'description': '',
                    'key_points': [],
                    'timing': '',
                    'transition': ''
                }
            
            # Handle sub-points under current section
            elif current_section and line.startswith('-'):
                # Remove the dash and clean up
                content = line[1:].strip()
                
                if content.startswith('Description:'):
                    current_section['description'] = content.replace('Description:', '').strip()
                elif content.startswith('Key talking points:'):
                    current_section['key_points'].append(content.replace('Key talking points:', '').strip())
                elif content.startswith('Estimated timing:'):
                    current_section['timing'] = content.replace('Estimated timing:', '').strip()
                elif content.startswith('Transition notes:'):
                    current_section['transition'] = content.replace('Transition notes:', '').strip()
                else:
                    # Generic sub-point
                    current_section['key_points'].append(content)
            
            # Handle nested sub-sections (like "Key Point 1: Origin Story")
            elif current_section and line.startswith('-') and ':' in line:
                content = line[1:].strip()
                current_section['key_points'].append(content)
        
        # Add the last section
        if current_section:
            sections.append(current_section)
        
        return {'sections': sections}

    @staticmethod
    def _parse_script_sections(script_content: str) -> list:
        """Parse script content into sections"""
        sections = []
        current_section = {'title': 'Opening', 'content': ''}

        for line in script_content.split('\n'):
            if line.strip().upper() in ['HOOK:', 'INTRODUCTION:', 'MAIN CONTENT:', 'CONCLUSION:', 'CALL TO ACTION:']:
                if current_section['content'].strip():
                    sections.append(current_section)
                current_section = {'title': line.strip(), 'content': ''}
            else:
                current_section['content'] += line + '\n'

        if current_section['content'].strip():
            sections.append(current_section)

        return sections
