"""
Word Count Completion Strategy for Video Scripts Script Generation

Section-based approach to ensure precise word count completion.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SectionType(Enum):
    HOOK_INTRO = "hook_intro"
    MAIN_CONTENT = "main_content"
    CONCLUSION = "conclusion"
    TRANSITION = "transition"


class TemplateStyleConfig:
    """Configuration for different template styles"""

    WORDS_PER_MINUTE = 140

    TEMPLATE_CONFIGS = {
        "short": {
            "min_words": 2800,
            "max_words": 3000,
            "duration_minutes": 20,
            "suggested_sections": 4,
        },
        "medium": {
            "min_words": 5600,
            "max_words": 6000,
            "duration_minutes": 40,
            "suggested_sections": 6,
        },
        "long": {
            "min_words": 8400,
            "max_words": 9000,
            "duration_minutes": 60,
            "suggested_sections": 8,
        },
    }


class WordCountStrategy:
    WORDS_PER_MINUTE = 140

    def __init__(self, template_style: str = "medium"):
        key = template_style.lower().replace(" ", "_").replace("-", "_")
        self.config = TemplateStyleConfig.TEMPLATE_CONFIGS.get(
            key, TemplateStyleConfig.TEMPLATE_CONFIGS["medium"]
        )
        self.template_style = key

    def calculate_section_word_targets(
        self, num_sections: Optional[int] = None
    ) -> Dict[str, int]:
        if num_sections is None:
            num_sections = self.config["suggested_sections"]

        min_words = self.config["min_words"]
        max_words = self.config["max_words"]
        target_words = int(min_words + (max_words - min_words) * 0.7)

        base_words_per_section = target_words // num_sections
        intro_sections = 1
        conclusion_sections = 1
        main_sections = max(1, num_sections - intro_sections - conclusion_sections)

        MAX_HOOK_WORDS = 75
        HARD_CAP_HOOK_WORDS = 150

        intro_words = int(base_words_per_section * 0.8)
        if intro_words > MAX_HOOK_WORDS:
            intro_words = MAX_HOOK_WORDS

        conclusion_words = int(base_words_per_section * 0.7)
        main_section_words = int(
            (target_words - intro_words - conclusion_words) / main_sections
        )

        total_allocated = (
            intro_words + (main_section_words * main_sections) + conclusion_words
        )
        if total_allocated > max_words:
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
            "max_hook_words": MAX_HOOK_WORDS,
            "hard_cap_hook_words": HARD_CAP_HOOK_WORDS,
        }

    def _determine_section_type(
        self, section_index: int, total_sections: int
    ) -> SectionType:
        if section_index == 0:
            return SectionType.HOOK_INTRO
        elif section_index == total_sections - 1:
            return SectionType.CONCLUSION
        else:
            return SectionType.MAIN_CONTENT

    def validate_word_count(
        self, content: str, target_words: int, tolerance: float = 0.05
    ) -> Tuple[bool, int, str]:
        actual_words = len(content.split())
        min_acceptable = int(target_words * (1 - tolerance))
        max_acceptable = int(target_words * (1 + tolerance))
        is_valid = min_acceptable <= actual_words <= max_acceptable
        if is_valid:
            message = f"OK: {actual_words} words (target: {target_words})"
        elif actual_words < min_acceptable:
            message = f"Too short: {actual_words} words (need {min_acceptable - actual_words} more)"
        else:
            message = f"Too long: {actual_words} words ({actual_words - max_acceptable} over)"
        return is_valid, actual_words, message

    def calculate_timing_for_sections(
        self, sections: List[Dict]
    ) -> List[Dict]:
        total_seconds = 0.0
        for section in sections:
            word_count = section.get("word_count", 0)
            duration_seconds = (word_count / self.WORDS_PER_MINUTE) * 60
            start_m = int(total_seconds // 60)
            start_s = int(total_seconds % 60)
            end_m = int((total_seconds + duration_seconds) // 60)
            end_s = int((total_seconds + duration_seconds) % 60)
            section["start_time"] = f"{start_m:02d}:{start_s:02d}"
            section["end_time"] = f"{end_m:02d}:{end_s:02d}"
            total_seconds += duration_seconds
        return sections
