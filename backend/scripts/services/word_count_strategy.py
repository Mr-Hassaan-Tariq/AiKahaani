# services/word_count_strategy.py
"""
Word Count Completion Strategy for TubeGenius Script Generation

This module implements a section-based approach to ensure precise word count
completion using the storytelling strategies from prompt.py.
"""

import logging
from typing import Dict, List, Tuple, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class SectionType(Enum):
    """Types of sections in a script"""
    HOOK_INTRO = "hook_intro"
    MAIN_CONTENT = "main_content"
    CONCLUSION = "conclusion"
    TRANSITION = "transition"


class TemplateStyleConfig:
    """Configuration for different template styles"""
    
    # Words per minute for speech (140 WPM is average English speaking rate)
    WORDS_PER_MINUTE = 140
    
    TEMPLATE_CONFIGS = {
        "short": {
            "min_words": 2800,  # 20 min * 140 WPM
            "max_words": 3000,  # ~21.4 min * 140 WPM
            "duration_minutes": 20,
            "suggested_sections": 4,
            "description": "Great for concise explainers or presentations"
        },
        "medium": {
            "min_words": 5600,  # 40 min * 140 WPM
            "max_words": 6000,  # ~42.9 min * 140 WPM
            "duration_minutes": 40,
            "suggested_sections": 6,
            "description": "Ideal for in-depth videos, product demos, interviews"
        },
        "long": {
            "min_words": 8400,  # 60 min * 140 WPM
            "max_words": 9000,  # ~64.3 min * 140 WPM
            "duration_minutes": 60,
            "suggested_sections": 8,
            "description": "Best for comprehensive tutorials, webinars, lectures"
        },
        "flexible_outline": {
            "min_words": 100,
            "max_words": 300,
            "duration_minutes": 0,
            "suggested_sections": 3,
            "description": "High-level structure without full script"
        }
    }


class WordCountStrategy:
    """
    Main strategy class for handling word count completion
    """
    
    def __init__(self, template_style: str = "medium"):
        self.template_style = template_style.lower()
        self.config = TemplateStyleConfig.TEMPLATE_CONFIGS.get(
            self.template_style, 
            TemplateStyleConfig.TEMPLATE_CONFIGS["medium"]
        )
        self.WORDS_PER_MINUTE = TemplateStyleConfig.WORDS_PER_MINUTE
        
    def calculate_section_word_targets(self, num_sections: Optional[int] = None) -> Dict[str, int]:
        """
        Calculate word count targets for each section type based on template requirements
        
        Args:
            num_sections: Optional override for number of sections
            
        Returns:
            Dictionary with word count targets for each section type
        """
        if num_sections is None:
            num_sections = self.config["suggested_sections"]
            
        min_words = self.config["min_words"]
        max_words = self.config["max_words"]
        target_words = (min_words + max_words) // 2
        
        # Calculate base words per section
        base_words_per_section = target_words // num_sections
        
        # Reserve sections for intro and conclusion
        intro_sections = 1
        conclusion_sections = 1
        main_sections = max(1, num_sections - intro_sections - conclusion_sections)
        
        # Distribute words with emphasis on main content
        intro_words = int(base_words_per_section * 0.8)  # 20% less for intro
        conclusion_words = int(base_words_per_section * 0.7)  # 30% less for conclusion
        main_section_words = int((target_words - intro_words - conclusion_words) / main_sections)
        
        # Ensure we don't exceed max_words
        total_allocated = intro_words + (main_section_words * main_sections) + conclusion_words
        
        if total_allocated > max_words:
            # Scale down proportionally
            scale_factor = max_words / total_allocated
            intro_words = int(intro_words * scale_factor)
            conclusion_words = int(conclusion_words * scale_factor)
            main_section_words = int(main_section_words * scale_factor)
        
        return {
            "intro": intro_words,
            "main_sections": main_section_words,
            "conclusion": conclusion_words,
            "total_target": target_words,
            "num_sections": num_sections,
            "intro_sections": intro_sections,
            "main_sections_count": main_sections,
            "conclusion_sections": conclusion_sections,
            "min_words": min_words,
            "max_words": max_words
        }
    
    def get_strategies_for_section_type(self, section_index: int, total_sections: int) -> List[str]:
        """
        Get relevant storytelling strategies from prompt.py for each section type
        
        Args:
            section_index: Current section index (0-based)
            total_sections: Total number of sections
            
        Returns:
            List of strategy IDs to apply for this section
        """
        section_type = self._determine_section_type(section_index, total_sections)
        
        if section_type == SectionType.HOOK_INTRO:
            return [
                "S1", "S2", "S3", "S4", "S5", "S6", "S7",  # Opening strategies
                "P01", "P02", "P05", "P11", "P12"  # Core principles for hooks
            ]
        elif section_type == SectionType.MAIN_CONTENT:
            return [
                "P01", "P02", "P03", "P04", "P05", "P06", "P07",  # Core principles
                "P08", "P09", "P10", "P11", "P12", "P13", "P14", "P15", "P16", "P17",
                "APP-01", "APP-02", "APP-03"  # Application techniques
            ]
        elif section_type == SectionType.CONCLUSION:
            return [
                "P01", "P05", "P11", "P12",  # Transformation and stakes
                "BONUS-02", "BONUS-04"  # Strong endings and emphasis
            ]
        else:  # TRANSITION
            return [
                "P03", "P04", "P12", "P13"  # Causality, rhythm, open loops, concision
            ]
    
    def _determine_section_type(self, section_index: int, total_sections: int) -> SectionType:
        """Determine the type of section based on its position"""
        if section_index == 0:
            return SectionType.HOOK_INTRO
        elif section_index == total_sections - 1:
            return SectionType.CONCLUSION
        elif section_index < total_sections - 1:
            return SectionType.MAIN_CONTENT
        else:
            return SectionType.TRANSITION
    
    def build_section_specific_prompt(self, 
                                    section_data: Dict, 
                                    section_index: int, 
                                    total_sections: int,
                                    word_target: int,
                                    storytelling_manual: str) -> str:
        """
        Build a section-specific prompt using relevant strategies from prompt.py
        
        Args:
            section_data: Section data from outline
            section_index: Current section index
            total_sections: Total number of sections
            word_target: Target word count for this section
            storytelling_manual: Formatted storytelling manual from prompt.py
            
        Returns:
            Section-specific prompt string
        """
        section_type = self._determine_section_type(section_index, total_sections)
        strategies = self.get_strategies_for_section_type(section_index, total_sections)
        
        section_title = section_data.get("title", f"Section {section_index + 1}")
        section_description = section_data.get("description", "")
        key_points = section_data.get("key_points", [])
        
        # Build strategy-specific guidance
        strategy_guidance = self._build_strategy_guidance(section_type, strategies)
        
        # Section-specific instructions
        section_instructions = self._get_section_instructions(section_type, word_target)
        
        prompt = f"""
Generate content for: {section_title}

Section Description: {section_description}

Key Points to Cover:
{self._format_key_points(key_points)}

Word Count Target: {word_target} words (STRICT REQUIREMENT)

Section Type: {section_type.value.replace('_', ' ').title()}

APPLY THESE STORYTELLING STRATEGIES:
{strategy_guidance}

SPECIFIC INSTRUCTIONS FOR THIS SECTION:
{section_instructions}

STORYTELLING MANUAL REFERENCE:
{storytelling_manual}

REQUIREMENTS:
- Write exactly {word_target} words (±10% tolerance)
- Follow the storytelling strategies listed above
- Ensure content flows naturally and maintains engagement
- Include specific examples, sensory details, and emotional beats
- Write in a conversational, YouTube-friendly tone

VERIFY: Count words before submitting - content must be {word_target} words minimum.

RESPONSE FORMAT: Return JSON object with this exact structure:
{{
    "content": "Your script content here...",
    "word_count": {word_target},
    "section_type": "{section_type.value}"
}}
"""
        return prompt
    
    def _build_strategy_guidance(self, section_type: SectionType, strategies: List[str]) -> str:
        """Build specific guidance based on strategies for the section type"""
        
        guidance_map = {
            SectionType.HOOK_INTRO: """
HOOK/INTRO STRATEGIES (S1-S7):
- Open with action from the first line (S1)
- Create open loops and explicit reasons to keep watching (S2)
- Balance delivering expectations with artfully defying them (S4)
- Edit densely and keep early pace fast (S5)
- Get to main content fast - avoid standalone intro (S6)
- NO channel trailers or subscribe requests (S7)

APPLY: Use dramatic metaphors, seed plot points, create curiosity hooks.
""",
            SectionType.MAIN_CONTENT: """
MAIN CONTENT STRATEGIES (P01-P17):
- Show transformation: Beginning → Middle → End (P01)
- Use concrete, sensory details (P02)
- Link beats with "therefore," "but," "because" (P03)
- Vary sentence length for rhythm (P04)
- Make audience feel what character felt (P05)
- Build attachment before big events (P06)
- Remove tangents and confusing details (P07)
- Focus on best, fascinating, extreme (P08)
- Remove jargon and clichés (P09)
- Write at high-school reading level (P10)
- Define goal, obstacle, consequences (P11)
- Plant open loops and manage curiosity threads (P12)
- Remove unnecessary words (P13)
- Use vivid word choices (P14)
- Show, don't tell (P15)
- Defy expectations with twists (P16)
- Write with visual in mind (P17)

APPLY: Use mini-stories, examples, analogies, and clear transitions.
""",
            SectionType.CONCLUSION: """
CONCLUSION STRATEGIES:
- Complete the transformation arc (P01)
- Resolve open loops and deliver payoffs (P12)
- End chapters strong with cliffhangers (BONUS-02)
- Place most important idea at sentence end (BONUS-04)
- Show consequences of the journey

APPLY: Provide closure while maintaining engagement, summarize key takeaways.
""",
            SectionType.TRANSITION: """
TRANSITION STRATEGIES:
- Link beats with causal connectors (P03)
- Vary sentence length for flow (P04)
- Plant open loops for next section (P12)
- Remove unnecessary words (P13)

APPLY: Create smooth bridges between sections, maintain momentum.
"""
        }
        
        return guidance_map.get(section_type, "Apply general storytelling principles.")
    
    def _get_section_instructions(self, section_type: SectionType, word_target: int) -> str:
        """Get specific instructions based on section type and word target"""
        
        if section_type == SectionType.HOOK_INTRO:
            return f"""
HOOK/INTRO SPECIFIC:
- Start with a dramatic, high-stakes moment
- Create 2-3 open-loop questions to be answered later
- Include vivid, filmable details
- Keep pace fast with varied sentence lengths
- Anchor viewers within first 2 lines
- Duration should be 20-60 seconds (≈{word_target//3} words)
"""
        elif section_type == SectionType.MAIN_CONTENT:
            return f"""
MAIN CONTENT SPECIFIC:
- Develop each key point with examples and stories
- Use "therefore," "but," "because" between ideas
- Add sensory details and concrete images
- Include emotional beats and character development
- Maintain engagement with rhetorical questions
- Each major point: 150-200 words
"""
        elif section_type == SectionType.CONCLUSION:
            return f"""
CONCLUSION SPECIFIC:
- Resolve all open loops from earlier sections
- Complete the transformation arc
- Summarize key takeaways clearly
- End with strong, memorable statement
- Include call-to-action if appropriate
- Provide closure while maintaining engagement
"""
        else:  # TRANSITION
            return f"""
TRANSITION SPECIFIC:
- Create smooth bridge to next section
- Plant curiosity for upcoming content
- Use causal connectors
- Keep concise but engaging
- Maintain narrative momentum
"""
    
    def _format_key_points(self, key_points: List[str]) -> str:
        """Format key points for inclusion in prompt"""
        if not key_points:
            return "- (No specific key points provided)"
        
        formatted = []
        for i, point in enumerate(key_points, 1):
            formatted.append(f"{i}. {point}")
        
        return "\n".join(formatted)
    
    def validate_word_count(self, content: str, target_words: int, tolerance: float = 0.1) -> Tuple[bool, int, str]:
        """
        Validate if content meets word count requirements
        
        Args:
            content: Content to validate
            target_words: Target word count
            tolerance: Acceptable deviation (0.1 = 10%)
            
        Returns:
            Tuple of (is_valid, actual_words, message)
        """
        actual_words = len(content.split())
        min_acceptable = int(target_words * (1 - tolerance))
        max_acceptable = int(target_words * (1 + tolerance))
        
        is_valid = min_acceptable <= actual_words <= max_acceptable
        
        if is_valid:
            message = f"✓ Word count OK: {actual_words} words (target: {target_words})"
        elif actual_words < min_acceptable:
            short_by = min_acceptable - actual_words
            message = f"⚠️ Too short: {actual_words} words (need {short_by} more, target: {target_words})"
        else:
            over_by = actual_words - max_acceptable
            message = f"⚠️ Too long: {actual_words} words ({over_by} over target: {target_words})"
        
        return is_valid, actual_words, message
    
    def get_expansion_strategies(self, section_type: SectionType) -> List[str]:
        """Get strategies for expanding content when word count is too low"""
        
        expansion_map = {
            SectionType.HOOK_INTRO: [
                "Add more sensory details and vivid imagery",
                "Include additional open-loop questions",
                "Expand the dramatic scene with more context",
                "Add character motivations and stakes"
            ],
            SectionType.MAIN_CONTENT: [
                "Add concrete examples and case studies",
                "Include analogies and comparisons",
                "Expand each key point with supporting details",
                "Add emotional beats and character development",
                "Include rhetorical questions and direct address",
                "Add background context and explanations"
            ],
            SectionType.CONCLUSION: [
                "Add summary of key transformation points",
                "Include specific examples of outcomes",
                "Expand on implications and next steps",
                "Add emotional resonance and callbacks"
            ],
            SectionType.TRANSITION: [
                "Add more context about the upcoming section",
                "Include teasers and curiosity hooks",
                "Expand on the connection between sections"
            ]
        }
        
        return expansion_map.get(section_type, ["Add more detail and examples"])
    
    def calculate_timing_for_sections(self, sections: List[Dict]) -> List[Dict]:
        """
        Calculate start_time and end_time for each section based on word count and WPM
        
        Args:
            sections: List of sections with word_count information
            
        Returns:
            List of sections with timing information added
        """
        total_seconds = 0
        
        for section in sections:
            word_count = section.get("word_count", 0)
            duration_seconds = (word_count / self.WORDS_PER_MINUTE) * 60
            
            # Format timing as MM:SS
            start_minutes = int(total_seconds // 60)
            start_seconds = int(total_seconds % 60)
            end_minutes = int((total_seconds + duration_seconds) // 60)
            end_seconds = int((total_seconds + duration_seconds) % 60)
            
            section["start_time"] = f"{start_minutes:02d}:{start_seconds:02d}"
            section["end_time"] = f"{end_minutes:02d}:{end_seconds:02d}"
            
            total_seconds += duration_seconds
        
        return sections
    
    def format_sections_for_json_schema(self, sections: List[Dict]) -> List[Dict]:
        """
        Format sections to match the required JSON schema
        
        Args:
            sections: List of sections with content and timing
            
        Returns:
            List formatted for JSON schema response
        """
        formatted_sections = []
        
        for section in sections:
            formatted_section = {
                "title": section.get("title", "Untitled Section"),
                "content": section.get("content", ""),
                "start_time": section.get("start_time", "00:00"),
                "end_time": section.get("end_time", "00:00")
            }
            formatted_sections.append(formatted_section)
        
        return formatted_sections
