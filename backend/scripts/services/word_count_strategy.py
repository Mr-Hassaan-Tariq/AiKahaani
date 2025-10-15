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
        
        # Aim for 70% of the range (closer to max) instead of average to ensure we meet minimum requirements
        target_words = int(min_words + (max_words - min_words) * 0.7)
        
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
- Write exactly {word_target} words (±5% tolerance - STRICT REQUIREMENT)
- Follow the storytelling strategies listed above
- Ensure content flows naturally and maintains engagement
- Include specific examples, sensory details, and emotional beats
- Write in a conversational, YouTube-friendly tone

CRITICAL: Count words before submitting - content must be {word_target} words minimum.
FAILURE TO MEET WORD COUNT WILL RESULT IN REGENERATION.

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
CRITICAL HOOK REQUIREMENTS (S1-S7 ENFORCEMENT):
- S1: MUST start with ACTION VERB in first sentence (not "Imagine" or "Picture this")
- S2: MUST create 2-3 SPECIFIC open loops with concrete questions
- S4: MUST subvert expectations while staying on-topic
- S5: MUST include specific sensory details and fast pacing
- S7: ABSOLUTELY NO channel trailers, personal updates, or CTAs

HOOK SUCCESS EXAMPLES (COPY THESE PATTERNS):
✅ "Sarah's phone buzzed at 3 AM with a message that would change everything."
✅ "The explosion shattered the silence at exactly 11:47 PM."
✅ "Three months ago, Mark discovered something in his basement that shouldn't exist."
✅ "The system crashed at the worst possible moment - during a live broadcast."
✅ "Dr. Chen's hands shook as she stared at the test results that shouldn't exist."
✅ "The alarm blared through the empty building at precisely 2:17 AM."

HOOK FAILURE EXAMPLES TO AVOID:
❌ "Imagine this..." (vague, no action)
❌ "Picture this scene..." (generic setup)
❌ "Let me tell you about..." (boring intro)
❌ "In today's video..." (channel trailer style)
❌ "Welcome to my channel..." (CTA violation)

SENSORY DETAILS EXAMPLES:
✅ "The smell of ozone filled the air as the machine hummed with a metallic vibration"
✅ "Cold air bit at exposed skin while footsteps echoed off concrete walls"
✅ "The coffee tasted burnt, and the clock ticked loudly in the silent room"

HOOK VALIDATION CHECKLIST:
□ Starts with action verb (not "Imagine," "Picture," "Let me")
□ Creates 2-3 specific, concrete questions
□ Includes vivid sensory details
□ Subverts expectations while staying on-topic
□ No CTAs or channel references
""",
                SectionType.MAIN_CONTENT: """
MAIN CONTENT STRATEGIES (P01-P17 ENFORCEMENT):
- P01: EVERY section must show transformation: Before → Conflict → After
- P02: MINIMUM 1 concrete sensory detail per section (flexible requirement)
- P03: Link beats with "therefore," "but," "because" (not "and then")
- P05: Create emotional progression, not just setup + mystery
- P09: NO overdramatic phrasing - write like talking to a friend
- P10: 8th-10th grade reading level, spoken English flow
- P12: Plant 2-3 specific open loops per section

SENSORY DETAIL REQUIREMENTS (P02) - FLEXIBLE:
✅ "The smell of ozone filled the air as the machine hummed with a metallic vibration"
✅ "Cold air bit at exposed skin while footsteps echoed off concrete walls"
✅ "The coffee tasted burnt, and the clock ticked loudly in the silent room"
✅ "Bright lights flickered overhead as the alarm system activated"
✅ "The room felt warm and stuffy, making it hard to concentrate"

❌ "creepy atmosphere" → "the air smelled of mildew and something metallic"
❌ "mysterious glow" → "the light pulsed like a heartbeat, casting shadows that moved"
❌ "haunting silence" → "only the sound of water dripping and distant traffic"

VOICE REQUIREMENTS (P09/P10):
✅ "So here's what actually happened..."
✅ "But wait, there's something weird about this..."
✅ "Now, you're probably thinking..."
✅ "Here's the thing that got me..."
✅ "This is where it gets interesting..."
✅ "But then something unexpected happened..."

❌ "shadowy silhouettes" → "dark shapes"
❌ "haunting mysteries" → "weird stuff that happened"
❌ "questions that linger" → "things we still don't know"

CURIOSITY THREAD EXAMPLES (P12):
✅ "But why did the system fail at exactly 11:47 PM? And what was in that encrypted file?"
✅ "The real question is: did Sarah know what she was downloading? We'll find out in a moment."
✅ "This raises three critical questions: Who had access? When did they know? And what happened next?"

❌ "If you think that's strange..." (vague, generic)
❌ "But there's more to this story..." (no specific question)
❌ "Stay tuned for more..." (no curiosity hook)

TRANSFORMATION CHECKLIST (P01):
□ What changes from beginning to end of this section?
□ What emotion does the audience feel at the start vs. end?
□ What realization or insight is gained?
□ How does this section advance the overall transformation arc?
""",
            SectionType.CONCLUSION: """
CONCLUSION REQUIREMENTS (BONUS-02/BONUS-04 ENFORCEMENT):
- End with emotional reflection or haunting unresolved question
- NO cliché phrases like "stay curious," "stay brave," "that's all for today"
- Create original, deeper reflection that ties to the transformation arc
- Use strong sentence endings with key insights

CONCLUSION SUCCESS EXAMPLES (COPY THESE PATTERNS):
✅ "The question is: if this happened to them, what else don't we know?"
✅ "But the real mystery isn't what happened - it's why we're still talking about it today."
✅ "Sarah never found out who sent that message. And maybe that's the point."
✅ "The system still runs today, but nobody talks about what happened that night."
✅ "The real question isn't what they found, but what they're still looking for."
✅ "This changes everything we thought we knew about how the system works."

CONCLUSION FAILURES TO AVOID:
❌ "Stay curious, stay brave" (cliché)
❌ "That's all for today" (generic)
❌ "Thanks for watching" (CTA, not reflection)
❌ "Until next time" (channel trailer style)
❌ "Keep exploring and learning" (generic ending)

CONCLUSION VALIDATION CHECKLIST:
□ Ends with emotional reflection or haunting unresolved question
□ No cliché phrases or CTAs
□ Ties back to the transformation arc
□ Creates original, deeper insight
""",
            SectionType.TRANSITION: """
TRANSITION STRATEGIES (P03, P04, P12, P13):
- P03: Link beats with causal connectors ("therefore," "but," "because")
- P04: Vary sentence length for flow and rhythm
- P12: Plant open loops for next section with specific questions
- P13: Remove unnecessary words, keep concise

TRANSITION EXAMPLES:
✅ "But this discovery led to something even more disturbing..."
✅ "However, what happened next would change everything they thought they knew."
✅ "The question is: why did this happen? And more importantly, what happens next?"

❌ "Now let's move on to..." (generic transition)
❌ "In the next part..." (boring setup)
❌ "Speaking of which..." (weak connection)
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
    
    def validate_word_count(self, content: str, target_words: int, tolerance: float = 0.05) -> Tuple[bool, int, str]:
        """
        Validate if content meets word count requirements with stricter tolerance
        
        Args:
            content: Content to validate
            target_words: Target word count
            tolerance: Acceptable deviation (0.05 = 5% for stricter enforcement)
            
        Returns:
            Tuple of (is_valid, actual_words, message)
        """
        actual_words = len(content.split())
        min_acceptable = int(target_words * (1 - tolerance))  # 95% instead of 90%
        max_acceptable = int(target_words * (1 + tolerance))  # 105% instead of 110%
        
        is_valid = min_acceptable <= actual_words <= max_acceptable
        
        if is_valid:
            message = f"✓ Word count OK: {actual_words} words (target: {target_words}, range: {min_acceptable}-{max_acceptable})"
        elif actual_words < min_acceptable:
            short_by = min_acceptable - actual_words
            message = f"⚠️ Too short: {actual_words} words (need {short_by} more, target: {target_words}, min: {min_acceptable})"
        else:
            over_by = actual_words - max_acceptable
            message = f"⚠️ Too long: {actual_words} words ({over_by} over target: {target_words}, max: {max_acceptable})"
        
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
    
    def validate_section_quality(self, section_content: str, section_type: SectionType) -> Tuple[bool, List[str]]:
        """
        Validate section content against storytelling requirements - more lenient approach
        Returns (is_valid, error_messages)
        """
        errors = []
        
        if section_type == SectionType.HOOK_INTRO:
            # Only check critical validations for hooks
            if self._has_channel_ctas(section_content):
                errors.append("Hook must NOT include channel trailers or CTAs (S7)")
        
        # Check for P09/P10 compliance - natural voice (critical)
        if self._has_overdramatic_phrasing(section_content):
            errors.append("Content must use natural, spoken English (P09/P10) - avoid overdramatic phrasing")
        
        # Check for BONUS-02/BONUS-04 compliance - strong conclusions (critical)
        if section_type == SectionType.CONCLUSION:
            if self._has_cliche_conclusion(section_content):
                errors.append("Conclusion must avoid clichés like 'stay curious' (BONUS-02/BONUS-04)")
        
        # Only return errors for critical issues that significantly impact quality
        return len(errors) == 0, errors
    
    def validate_critical_quality_only(self, section_content: str, section_type: SectionType) -> Tuple[bool, List[str]]:
        """
        Validate only critical quality issues for subsequent attempts
        Returns (is_valid, error_messages)
        """
        errors = []
        
        # Only check the most critical issues on retry
        if self._has_channel_ctas(section_content):
            errors.append("Hook must NOT include channel trailers or CTAs (S7)")
        
        if self._has_overdramatic_phrasing(section_content):
            errors.append("Content must use natural, spoken English (P09/P10) - avoid overdramatic phrasing")
        
        return len(errors) == 0, errors
    
    def _has_action_verb_start(self, content: str) -> bool:
        """Check if content starts with action verb (S1 compliance)"""
        first_sentence = content.split('.')[0].strip()
        weak_starters = ['imagine', 'picture', 'let me', 'in today', 'welcome', 'hi', 'hello']
        return not any(first_sentence.lower().startswith(starter) for starter in weak_starters)
    
    def _has_specific_open_loops(self, content: str) -> bool:
        """Check if content creates specific open loops (S2 compliance)"""
        question_indicators = ['?', 'what', 'why', 'how', 'when', 'where', 'who']
        return any(indicator in content.lower() for indicator in question_indicators)
    
    def _has_channel_ctas(self, content: str) -> bool:
        """Check if content contains channel CTAs (S7 compliance) - improved detection"""
        cta_phrases = [
            'subscribe to my channel', 'like and subscribe', 'hit the subscribe button',
            'don\'t forget to subscribe', 'subscribe for more', 'thanks for watching',
            'hit the bell', 'turn on notifications', 'follow me on'
        ]
        # Only flag if it's clearly a CTA, not just mentioning these words in context
        content_lower = content.lower()
        return any(phrase in content_lower for phrase in cta_phrases)
    
    def _has_concrete_sensory_details(self, content: str) -> bool:
        """Check if content has concrete sensory details (P02 compliance) - more flexible"""
        # Look for specific sensory words and concrete descriptions
        sensory_words = ['smell', 'sound', 'taste', 'feel', 'touch', 'saw', 'heard', 'felt', 'smelled', 'tasted', 
                        'buzzed', 'shattered', 'hummed', 'vibration', 'ozone', 'metallic', 'cold', 'bit', 
                        'dripping', 'echoed', 'pulsed', 'heartbeat', 'burned', 'ticked', 'clicked',
                        'bright', 'loud', 'quiet', 'sharp', 'soft', 'rough', 'smooth', 'warm', 'hot']
        generic_adjectives = ['creepy', 'mysterious', 'haunting', 'eerie', 'strange', 'weird', 'shadowy', 'dark']
        
        # Count sensory words
        sensory_count = sum(1 for word in sensory_words if word in content.lower())
        has_generic = any(adj in content.lower() for adj in generic_adjectives)
        
        # More flexible: require 1+ sensory words OR no generic adjectives (not both)
        return sensory_count >= 1 or not has_generic
    
    def _has_transformation_arc(self, content: str) -> bool:
        """Check if content shows transformation/change (P01 compliance)"""
        change_indicators = ['changed', 'transformed', 'became', 'realized', 'discovered', 'learned', 'understood', 'shifted', 'evolved']
        return any(indicator in content.lower() for indicator in change_indicators)
    
    def _has_overdramatic_phrasing(self, content: str) -> bool:
        """Check if content uses overdramatic phrasing (P09/P10 compliance)"""
        overdramatic_phrases = [
            'shadowy silhouettes', 'haunting mysteries', 'questions that linger', 'mysterious depths',
            'dark secrets', 'ancient wisdom', 'profound implications', 'eternal mysteries'
        ]
        return any(phrase in content.lower() for phrase in overdramatic_phrases)
    
    def _has_specific_curiosity_threads(self, content: str) -> bool:
        """Check if content has specific curiosity threads (P12 compliance)"""
        vague_transitions = ['stay tuned', 'more to come', 'that\'s not all', 'if you think that\'s']
        specific_questions = ['what', 'why', 'how', 'when', 'where', 'who']
        
        has_vague = any(phrase in content.lower() for phrase in vague_transitions)
        has_specific = any(question in content.lower() for question in specific_questions)
        
        return has_specific and not has_vague
    
    def _has_cliche_conclusion(self, content: str) -> bool:
        """Check if conclusion uses clichés (BONUS-02/BONUS-04 compliance)"""
        cliche_phrases = [
            'stay curious', 'stay brave', 'that\'s all for today', 'thanks for watching',
            'until next time', 'see you next time', 'keep exploring', 'keep learning'
        ]
        return any(phrase in content.lower() for phrase in cliche_phrases)
    
    def _has_emotional_reflection(self, content: str) -> bool:
        """Check if conclusion has emotional reflection or haunting question"""
        reflection_indicators = ['the question is', 'the real mystery', 'but maybe that\'s', 'what we don\'t know', 'nobody talks about']
        return any(indicator in content.lower() for indicator in reflection_indicators)
    
    def get_improvement_guidance(self, errors: List[str]) -> str:
        """Generate specific improvement guidance based on validation errors"""
        guidance_map = {
            "Hook must start with action verb (S1)": """
- Replace weak starters like "Imagine this..." with action: "Sarah's phone buzzed..."
- Use specific verbs: buzzed, shattered, discovered, crashed, exploded
- Start mid-action or mid-crisis, not with setup""",
            
            "Hook must create 2-3 specific open loops with concrete questions (S2)": """
- Add specific questions: "Why did this happen at 11:47 PM exactly?"
- Create concrete mysteries: "What was in that encrypted file?"
- Avoid vague suspense - be specific about what's unknown""",
            
            "Section must include concrete sensory details (P02)": """
- Add specific sensory details: "the smell of ozone," "metallic hum," "cold air bit"
- Replace generic adjectives: "creepy" → "smelled of mildew and metal"
- Use concrete, filmable details that create immersion""",
            
            "Main content must show transformation/change (P01)": """
- Show change: Before → Conflict → After
- Include emotional progression, not just setup + mystery
- Add realizations, discoveries, or character development""",
            
            "Content must use natural, spoken English (P09/P10)": """
- Write like talking to a friend: "So here's what happened..."
- Avoid overdramatic phrasing: "shadowy silhouettes" → "dark shapes"
- Use simple, conversational language""",
            
            "Section must plant specific curiosity threads (P12)": """
- Add specific questions: "But why did the system fail exactly then?"
- Create concrete mysteries to be resolved later
- Avoid vague transitions like "stay tuned" or "more to come""",
            
            "Conclusion must avoid clichés like 'stay curious' (BONUS-02/BONUS-04)": """
- End with emotional reflection: "The question is: what else don't we know?"
- Create original insights tied to the transformation arc
- Use haunting unresolved questions instead of generic endings"""
        }
        
        guidance_parts = []
        for error in errors:
            for key, guidance in guidance_map.items():
                if key in error:
                    guidance_parts.append(guidance)
                    break
        
        return "\n\n".join(guidance_parts) if guidance_parts else "Apply general storytelling principles from the manual."
