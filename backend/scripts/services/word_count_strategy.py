# services/word_count_strategy.py
"""
Word Count Completion Strategy for TubeGenius Script Generation

This module implements a section-based approach to ensure precise word count
completion using the storytelling strategies from prompt.py.
"""

import logging
import re
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
        # Normalize template style: lowercase and replace spaces with underscores
        self.template_style = template_style.lower().replace(" ", "_")
        self.config = TemplateStyleConfig.TEMPLATE_CONFIGS.get(
            self.template_style, 
            TemplateStyleConfig.TEMPLATE_CONFIGS["medium"]
        )
        self.WORDS_PER_MINUTE = TemplateStyleConfig.WORDS_PER_MINUTE
        
    def summarize_for_context(self, text: str, max_words: int = 60) -> str:
        """Heuristic, deterministic summary for threading context across sections.
        Picks first and last sentence (or first two), capped to max_words.
        """
        if not text:
            return ""
        # Split into sentences conservatively
        sentences = re.split(r"[.!?]\s+", text.strip())
        pick = []
        if sentences:
            pick.append(sentences[0])
            if len(sentences) > 1:
                pick.append(sentences[-1])
            elif len(sentences) > 2:
                pick = sentences[:2]
        summary = " ".join(s for s in pick if s).strip()
        words = summary.split()
        if len(words) > max_words:
            summary = " ".join(words[:max_words]) + "..."
        return summary

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
        
        # CRITICAL: Hook section must be ≤30 seconds (~75 words at 2.5 WPS)
        MAX_HOOK_WORDS = 75  # 30 seconds at 2.5 words/second
        HARD_CAP_HOOK_WORDS = 150  # 60 seconds absolute maximum
        
        # Cap intro_words to enforce hook duration
        intro_words = int(base_words_per_section * 0.8)  # 20% less for intro
        if intro_words > MAX_HOOK_WORDS:
            logger.warning(
                f"[WC_STRATEGY] Hook word target {intro_words} exceeds 30s guideline "
                f"({MAX_HOOK_WORDS}w). Capping at {MAX_HOOK_WORDS}w."
            )
            intro_words = MAX_HOOK_WORDS
        
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
            "max_words": max_words,
            "max_hook_words": MAX_HOOK_WORDS,  # Add for reference
            "hard_cap_hook_words": HARD_CAP_HOOK_WORDS,  # Add for reference
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
                "S1", "S2", "S3", "S4", "S5", "S6", "S7"  # All opening strategies
            ]
        elif section_type == SectionType.MAIN_CONTENT:
            return [
                "C1", "C2"  # Case studies for main content
            ]
        elif section_type == SectionType.CONCLUSION:
            return [
                "S1", "S2"  # Use opening strategies for strong conclusions
            ]
        else:  # TRANSITION
            return [
                "S2"  # Open loops for transitions
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
                                    storytelling_manual: str = "") -> str:
        """
        Build a section-specific prompt using relevant strategies from prompt.py
        
        Args:
            section_data: Section data from outline
            section_index: Current section index
            total_sections: Total number of sections
            word_target: Target word count for this section
            storytelling_manual: Deprecated parameter - filtering now happens internally
            
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
        
        # Filter storytelling manual to only include relevant rules
        filtered_manual = self._filter_storytelling_manual_for_strategies(strategies)
        
        prompt = f"""
Generate content for: {section_title}

Section Description: {section_description}

Key Points to Cover:
{self._format_key_points(key_points)}

🎙️ DURATION TARGET: {int(word_target / 140)} min {int((word_target / 140 % 1) * 60):02d} sec of spoken English (@ 140 words/minute)
📊 WORD COUNT RANGE: This section MUST have a word count between {int(word_target * 0.95)} and {int(word_target * 1.05)} words (±5%).
🎯 Approximate Token Target: ~{int(word_target * 1.33)} tokens.

⚠️  CRITICAL: You MUST generate {int(word_target / 140)} min {int((word_target / 140 % 1) * 60):02d} sec of content = {word_target} words.
    Think: "How much content does someone need to speak for {int(word_target / 140)} minutes?"
    This is not a suggestion - it's a strict requirement.

Section Type: {section_type.value.replace('_', ' ').title()}

🚨 IMPORTANT: The rules below reference structural concepts like "Before/Conflict/After", "Open Loops", "Chapter X". These are FRAMEWORKS to guide your narrative structure. Use them internally to shape your writing, but NEVER include them as literal labels or headings in the script output. Write natural, flowing narrative prose.

📚 LANGUAGE LEVEL - 6TH-7TH GRADE (MANDATORY):
- Every word should be instantly clear to a 10-year-old or 80-year-old
- ALWAYS use contractions: it's, don't, can't, wasn't, they're, couldn't, didn't

FORBIDDEN WORDS (Replace these):
❌ therefore, however, consequently, thus → ✅ so, but, because, that's why
❌ nevertheless, moreover, furthermore → ✅ but, also, and, plus
❌ phenomenon, subsequently, essentially → ✅ thing, then/next, basically
❌ utilize, implement, commence → ✅ use, do, start
❌ indicate, demonstrate, facilitate → ✅ show, prove, help

TALK LIKE THIS:
✅ "So here's what happened..."
✅ "But that's not the crazy part..."
✅ "It didn't make sense..."
- Talk like a friend, not a documentary

APPLY THESE STORYTELLING STRATEGIES:
{strategy_guidance}

SPECIFIC INSTRUCTIONS FOR THIS SECTION:
{section_instructions}

RELEVANT STORYTELLING RULES:
{filtered_manual}

REQUIREMENTS:
- 📊 WORD COUNT: Write AT LEAST {word_target} words (±5% acceptable, but NEVER fall short)
- Follow the storytelling strategies listed above
- END section with curiosity hook - unanswered question or unresolved tension
- Include specific examples, sensory details, and emotional reactions
- Write in simple, conversational language

🎭 CONVERSATIONAL TONE (CRITICAL):
- Talk like you're telling a story to a FRIEND, not narrating a documentary
- Start sentences with: "But here's the thing...", "And that's when...", "So...", "Now..."
- Show EMOTION first, facts second: "She couldn't believe it." not "The results indicated..."
- Create tension in EVERY line - make them curious about the next sentence

🚨 CONTRACTIONS - USE EVERYWHERE (MANDATORY):
You MUST use contractions throughout. Never write:
❌ it is, do not, does not, cannot, could not, would not, should not, did not, was not, were not, are not, will not, they are, we are, you are
✅ it's, don't, doesn't, can't, couldn't, wouldn't, shouldn't, didn't, wasn't, weren't, aren't, won't, they're, we're, you're
Apply contractions to EVERY sentence where natural. Scripts without contractions will be rejected.

🚨 WORD COUNT VERIFICATION (MANDATORY):
BEFORE submitting your response, verify the word count using code generation.

VERIFICATION PROCESS:
1. Write your content naturally following all the guidance above
2. Use code generation to count your words:
   - Split your content by whitespace
   - Count the number of words
   - Verify it meets the target
3. If the count shows you're under {int(word_target * 0.95)} words ({word_target} target):
   - ADD MORE CONTENT using the expansion strategies provided
   - Re-run the verification code with the expanded content
4. ONLY submit your final JSON response when code execution confirms {int(word_target * 0.95)}+ words

DO NOT guess word count - use code generation to get the accurate count.
The validation method used is: split by whitespace and count tokens.

RESPONSE FORMAT: Return JSON object with this exact structure:
{{
    "content": "Your script content here...",
    "word_count": {word_target},
    "section_type": "{section_type.value}"
}}
"""
        return prompt
    
    def _filter_storytelling_manual_for_strategies(self, strategies: List[str]) -> str:
        """
        Filter the storytelling manual to only include rules relevant to the given strategies
        
        Args:
            strategies: List of strategy IDs (e.g., ["S1", "S2", "P01"])
            
        Returns:
            Filtered storytelling manual text containing only relevant rules
        """
        from .prompt import prompt as storytelling_rules
        
        filtered_rules = []
        
        for rule in storytelling_rules:
            if rule.get("id") in strategies:
                # Format the rule for inclusion in prompt
                rule_text = f"\n{rule['id']}: {rule['principle_rule']}"
                rule_text += f"\nExplanation: {rule['explanation']}"
                
                if "framework_formula" in rule:
                    rule_text += "\nFramework:"
                    for step in rule["framework_formula"]:
                        rule_text += f"\n• {step}"
                
                if "validators" in rule:
                    rule_text += "\nValidators:"
                    for validator in rule["validators"]:
                        rule_text += f"\n• {validator}"
                
                if "case_study_example" in rule:
                    rule_text += f"\nExample: {rule['case_study_example']}"
                
                filtered_rules.append(rule_text)
        
        if not filtered_rules:
            return "No specific rules apply to this section type."
        
        return "\n".join(filtered_rules)
    
    def _build_strategy_guidance(self, section_type: SectionType, strategies: List[str]) -> str:
        """Build specific guidance based on strategies for the section type"""
        
        guidance_map = {
                SectionType.HOOK_INTRO: """
CRITICAL HOOK REQUIREMENTS (S1-S7 VALIDATOR ENFORCEMENT):
- S1: Line 1-2 must hook IMMEDIATELY with emotion or mystery - no setup first
- S1: Hook duration MUST be ≤30 seconds (hard cap: 60s when justified)
- S1: Jump straight into the moment - use simple, punchy language with contractions
- S1: FORBIDDEN: "Imagine", "Picture this", academic vocabulary, formal tone
- S1: NO 6+ minute atmospheric prologues (this is a CRITICAL FAILURE)
- S2: Create 2-3 unanswered questions in first 30 seconds (create curiosity naturally)
- S2: Use simple language a 10-year-old would understand
- S2: Questions MUST be stated cleanly in first 30-60 seconds
- S2: NO questions buried in long monologues
- S6: For tutorials/listicles: First value point MUST start within 10 seconds of hook end
- LANGUAGE: 6th-7th grade level, contractions required, NO formal connector words

NOTE: Terms like "open loops", "Before/Conflict/After" are structural frameworks - use them to guide writing, but don't include as literal labels in script.
- S6: Hook MUST be ≤30 seconds (exceptions explicitly justified)
- S6: NO standalone 1-2 minute opening sections
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
❌ 6+ minute atmospheric prologues (COMPLETE FAILURE)
❌ Questions buried in long monologues
❌ Missing transformation statements

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
□ Duration ≤30 seconds (not 6+ minutes)
□ Transformation statement present
□ Questions stated cleanly in first 30-60 seconds
□ First value point within 10 seconds for tutorials/listicles
""",
                SectionType.MAIN_CONTENT: """
MAIN CONTENT STRATEGIES (P01-P17 ENFORCEMENT):
- P01: EVERY section must show transformation: Before → Conflict → After (use as structural guide, not literal labels)
- P02: MINIMUM 1 concrete sensory detail per section (flexible requirement)
- P03: Link beats with simple words: "so", "but", "because", "and then" (NOT "therefore", "however", "consequently")
- P05: Create emotional progression - show reactions and feelings, not just events
- P09: NO academic or formal phrasing - write like talking to a friend over coffee
- P10: 6th-7th grade reading level - a 10-year-old should understand every word
- P12: Plant 2-3 specific open loops per section (create curiosity naturally, don't write "Open Loop:" as label)
- P13: End EVERY section with unanswered question or unresolved tension to maintain engagement
- CONTRACTIONS REQUIRED: Use it's, don't, can't, wasn't, they're in every section

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
- End with emotional reflection or haunting question that sticks with them
- Use simple, conversational language - talk like a friend, not a narrator
- NO cliché phrases like "stay curious," "stay brave," "that's all for today"
- Make them FEEL something or THINK about something new
- Use contractions and simple words: "So what's next?", "And that's the thing..."

CONCLUSION SUCCESS EXAMPLES (COPY THESE PATTERNS):
✅ "So here's the question: if this happened to them, what else don't we know?"
✅ "But the real mystery isn't what happened - it's why we're still talking about it."
✅ "Sarah never found out who sent that message. And maybe that's the point."
✅ "The system still runs today. But nobody talks about what happened that night."
✅ "The real question isn't what they found - it's what they're still looking for."
✅ "And that changes everything we thought we knew."

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
- P03: Link beats with SIMPLE words: "so", "but", "because" (NOT "therefore", "however", "consequently")
- P04: Vary sentence length for flow and rhythm - mix short punches with longer flow
- P12: End with curiosity hook - make them wonder what's next (not literal "Open Loop:" labels)
- P13: Remove unnecessary words, keep concise and punchy
- ALWAYS use contractions: it's, don't, can't, wasn't

TRANSITION EXAMPLES:
✅ "But this discovery led to something even more disturbing..."
✅ "And that's when things got really strange..."
✅ "So here's the question: why did this happen? And what happens next?"
✅ "But that's not even the weird part..."

❌ "However, what happened next..." (too formal)
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
HOOK/INTRO SPECIFIC (VALIDATOR ENFORCED):

🎯 HOOK IN 2 LINES (MANDATORY):
- Line 1: Something shocking, mysterious, or emotionally charged happens
- Line 2: Make them NEED to know why/what/how
- NO setup, NO context first - jump straight into the moment
- Example: "The call came at 3 AM. She knew something was wrong."

📚 SIMPLE LANGUAGE (6TH-7TH GRADE):
- Use words a 10-year-old understands instantly
- ALWAYS use contractions: it's, don't, can't, wasn't, didn't
- FORBIDDEN: academic words, formal phrases, "therefore/however/consequently"
- Talk like telling a friend a crazy story over coffee

✍️ CONVERSATIONAL VOICE:
- Short, punchy sentences mixed with natural flow
- Start with: "So...", "But here's the thing...", "And that's when..."
- Show EMOTION first: "She couldn't believe it." not "The results were surprising."
- Create tension in EVERY line - make them curious about the next sentence

🔥 CREATE OPEN LOOPS (MANDATORY):
- Plant 2-3 specific open loops with concrete questions in first 30 seconds
- Create curiosity naturally - make them wonder what happens next
- Example: "But why did it happen? And what was she hiding?"
- These questions should be answered later in the script

⚡ TECHNICAL REQUIREMENTS:
- Start with dramatic, high-stakes moment
- Include vivid, filmable details
- Anchor viewers within first 2 lines
- Duration MUST be ≤30 seconds (≈{word_target//3} words)
- CRITICAL: NO 6+ minute prologues (complete failure)
- For tutorials/listicles: First value point within 10 seconds of hook end
- MUST include transformation statement: "Learn X to achieve Y"

Remember: STORYTELLER pulling viewers in, not mechanical AI narrator!
"""
        elif section_type == SectionType.MAIN_CONTENT:
            return f"""
MAIN CONTENT SPECIFIC:

📚 SIMPLE LANGUAGE (6TH-7TH GRADE):
- Use words a 10-year-old understands - no academic vocabulary
- ALWAYS use contractions: it's, don't, can't, wasn't
- Link ideas with SIMPLE words: "so", "but", "because" (NOT "therefore", "however", "consequently")
- Talk like a friend, not a documentary narrator

🎭 CONVERSATIONAL TONE:
- Show emotional reactions, not just events: "She couldn't believe it." not "The results indicated..."
- Start sentences naturally: "So...", "But here's the thing...", "And that's when..."
- Mix short punchy sentences with natural flow
- Create tension in every line - make them curious about the next sentence

🔥 SECTION ENDING (MANDATORY):
- Plant 1-2 open loops at the end of section (create curiosity for what's next)
- END every section with unanswered question or unresolved tension
- Examples: "But that's not even the weird part.", "And then it got worse.", "The question is: why?"
- Make them need to keep watching
- Each major point: 150-200 words

Remember: Talk like a friend telling a story, not a narrator describing events!
"""
        elif section_type == SectionType.CONCLUSION:
            return f"""
CONCLUSION SPECIFIC:
- Answer the big questions raised earlier (don't write "Open Loop:")
- Complete the story journey with emotion
- Use simple, conversational language - talk like a friend
- End with a haunting question or reflection that sticks
- Examples: "So what would you do?", "And that's the thing - we'll never know."
- Use contractions: it's, don't, can't, wasn't
- Make them FEEL something or THINK about something new
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
                "end_time": section.get("end_time", "00:00"),
                "validator_compliance": section.get("validator_compliance", {})
            }
            formatted_sections.append(formatted_section)
        
        return formatted_sections
    
    def validate_section_quality(self, section_content: str, section_type: SectionType, validation_level: str = "normal") -> Tuple[bool, List[str]]:
        """
        Validate section content against storytelling requirements and validator enforcement
        Returns (is_valid, error_messages)
        
        Args:
            validation_level: 
                - "strict": All checks (first attempt)
                - "normal": Critical checks only (retry attempts)
                - "minimal": Blockers only (final attempt)
        """
        errors = []
        
        # ALWAYS check critical blockers regardless of level
        if section_type == SectionType.HOOK_INTRO:
            # S7: No CTAs (BLOCKER)
            if self._has_channel_ctas(section_content):
                errors.append("S7: Hook contains CTAs/subscribe requests (BLOCKER)")
            
            # S1: Hook duration hard cap (BLOCKER)
            word_count = len(section_content.split())
            estimated_duration = word_count / 150  # minutes
            
            if estimated_duration > 1.0:  # 60 seconds
                errors.append(
                    f"S1 BLOCKER: Hook {word_count}w (~{estimated_duration*60:.0f}s) "
                    f"exceeds 60s hard cap"
                )
        
        # Strict validation: all checks
        if validation_level == "strict":
            if section_type == SectionType.HOOK_INTRO:
                # S1.1: Hook duration check - estimate from word count
                word_count = len(section_content.split())
                estimated_duration = word_count / 150  # ~150 words per minute for spoken content
                
                # Add two-tier validation
                if estimated_duration > 0.5:  # 30 seconds
                    errors.append(
                        f"S1 violation: Hook duration {estimated_duration*60:.0f}s exceeds 30s target (60s hard cap)"
                    )
                    
                if estimated_duration > 1.0:  # 60 seconds - CRITICAL FAILURE
                    errors.append(
                        f"S1 CRITICAL FAILURE: Hook duration {estimated_duration*60:.0f}s exceeds 60s hard cap"
                    )
                
                # S1.4: Check for 6+ minute prologues (critical failure)
                if estimated_duration > 6:
                    errors.append(f"S1 CRITICAL FAILURE: {estimated_duration:.1f} minute prologue - this is a complete failure")
                
                # S1.2: Action verbs in first sentence (strengthened validation)
                if not self._has_action_verb_opening(section_content):
                    errors.append(
                        "S1 violation: Hook does not start with action verb "
                        "(forbidden starters: imagine, picture, let me, let's)"
                    )
                
                # S1.3: Vague language check
                vague_terms = ['high-stakes moment', 'dramatic', 'exciting', 'interesting', 'compelling', 'atmospheric', 'eerie', 'muted hum', 'still air']
                has_vague_language = any(term in section_content.lower() for term in vague_terms)
                if has_vague_language:
                    errors.append("S1 violation: Contains vague language without concrete dramatization")
                
                # S2 Open Loops Validators
                # S2.1: Specific questions check
                question_indicators = ['?', 'how', 'what', 'why', 'when', 'where']
                has_questions = any(indicator in section_content.lower() for indicator in question_indicators)
                if not has_questions:
                    errors.append("S2 violation: No specific questions in hook")
                
                # S2.2: Transformation statement check
                transformation_indicators = ['learn', 'achieve', 'transform', 'change', 'improve', 'master', 'tricks', 'tips', 'secrets']
                has_transformation = any(indicator in section_content.lower() for indicator in transformation_indicators)
                if not has_transformation:
                    errors.append("S2 violation: No transformation statement (Learn X to achieve Y)")
                
                # S2.3: Questions buried in monologue check
                if len(section_content.split()) > 200:  # Very long hook
                    errors.append("S2 violation: Questions buried in long monologue")
            
            # Check for P09/P10 compliance - natural voice (critical)
            if self._has_overdramatic_phrasing(section_content):
                errors.append("Content must use natural, spoken English (P09/P10) - avoid overdramatic phrasing")
            
            # Check for BONUS-02/BONUS-04 compliance - strong conclusions (critical)
            if section_type == SectionType.CONCLUSION:
                if self._has_cliche_conclusion(section_content):
                    errors.append("Conclusion must avoid clichés like 'stay curious' (BONUS-02/BONUS-04)")
        
        # Normal validation: critical issues only
        elif validation_level == "normal":
            if section_type == SectionType.HOOK_INTRO:
                if not self._has_action_verb_opening(section_content):
                    errors.append("S1: No action verb opening")
                
                if not self._has_specific_open_loops(section_content):
                    errors.append("S2: No specific open loops")
            
            # Check only the most critical P-rules
            if self._has_cliche_conclusion(section_content) and section_type == SectionType.CONCLUSION:
                errors.append("BONUS-02: Cliché conclusion")
        
        # Minimal validation: only blockers (already checked above)
        # No additional checks needed
        
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
    
    def _has_action_verb_opening(self, content: str) -> bool:
        """Check if content starts with strong action verb (S1 compliance)"""
        first_sentence = content.split('.')[0].strip().lower()
        
        # Forbidden weak starters - must NOT begin with these
        weak_starters = [
            'imagine', 'picture', 'let me', "let's", 'in today', 
            'welcome', 'hi', 'hello', 'today we', 'so here'
        ]
        
        if any(first_sentence.startswith(weak) for weak in weak_starters):
            return False
        
        # Strong action verbs that should appear in first 5 words
        strong_verbs = [
            'buzzed', 'shattered', 'crashed', 'exploded', 'discovered',
            'stopped', 'grabbed', 'fell', 'rang', 'struck', 'broke',
            'hit', 'slammed', 'burst', 'erupted', 'collapsed'
        ]
        
        first_five_words = ' '.join(first_sentence.split()[:5])
        return any(verb in first_five_words for verb in strong_verbs)
    
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
    
    def check_s6_value_delivery_timing(self, sections: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Check S6 value delivery timing for tutorials/listicles
        Returns (is_compliant, error_messages)
        """
        errors = []
        
        if len(sections) < 2:
            return True, errors  # Not enough sections to check
        
        # Check if this appears to be a tutorial/listicle
        first_section = sections[0]
        second_section = sections[1]
        
        # Look for tutorial/listicle indicators
        tutorial_indicators = ['trick', 'tip', 'hack', 'secret', 'method', 'technique', 'step', 'way', 'how to', 'guide']
        has_tutorial_indicators = any(indicator in str(sections).lower() for indicator in tutorial_indicators)
        
        if has_tutorial_indicators:
            # Check timing for first value point
            first_content = first_section.get("content", "")
            second_content = second_section.get("content", "")
            
            # Estimate timing
            first_word_count = len(first_content.split())
            second_word_count = len(second_content.split())
            
            first_duration = first_word_count / 150  # minutes
            second_duration = second_word_count / 150  # minutes
            
            # First value point should start within 10 seconds of hook end
            total_hook_duration = first_duration + second_duration
            if total_hook_duration > 0.17:  # More than 10 seconds
                errors.append(f"S6 violation: First value point starts at {total_hook_duration*60:.0f}s, exceeds 10s limit")
        
        return len(errors) == 0, errors
    
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
- Show change: Before → Conflict → After (as narrative flow, not as literal labels)
- Include emotional reactions and realizations, not just events
- Use simple language and contractions: it's, don't, can't
- End section with curiosity hook - make them want to keep watching""",
            
            "Content must use natural, spoken English (P09/P10)": """
- Write like talking to a friend: "So here's what happened..."
- Use 6th-7th grade reading level - a 10-year-old should understand every word
- FORBIDDEN: therefore, however, consequently, phenomenon, thus
- USE: so, but, because, and, that's why, then, next
- Always use contractions where natural""",
            
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
