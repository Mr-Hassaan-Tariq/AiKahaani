"""
Unit tests for app/services/scripts/word_count_strategy.py

Pure logic — no I/O.
"""

import pytest

from app.services.scripts.word_count_strategy import (
    SectionType,
    TemplateStyleConfig,
    WordCountStrategy,
)


# ── TemplateStyleConfig ───────────────────────────────────────────────────────


def test_short_template_config():
    cfg = TemplateStyleConfig.TEMPLATE_CONFIGS["short"]
    assert cfg["min_words"] == 2800
    assert cfg["max_words"] == 3000
    assert cfg["suggested_sections"] == 4


def test_medium_template_config():
    cfg = TemplateStyleConfig.TEMPLATE_CONFIGS["medium"]
    assert cfg["min_words"] == 5600
    assert cfg["max_words"] == 6000
    assert cfg["suggested_sections"] == 6


def test_long_template_config():
    cfg = TemplateStyleConfig.TEMPLATE_CONFIGS["long"]
    assert cfg["min_words"] == 8400
    assert cfg["max_words"] == 9000
    assert cfg["suggested_sections"] == 8


# ── WordCountStrategy.calculate_section_word_targets ─────────────────────────


@pytest.fixture
def short_strategy():
    return WordCountStrategy("short")


@pytest.fixture
def medium_strategy():
    return WordCountStrategy("medium")


def test_calculate_targets_returns_required_keys(short_strategy):
    targets = short_strategy.calculate_section_word_targets(4)
    assert "intro" in targets
    assert "main_sections" in targets
    assert "conclusion" in targets
    assert "total_target" in targets


def test_hook_word_cap_short(short_strategy):
    targets = short_strategy.calculate_section_word_targets(4)
    assert targets["intro"] <= 75, "Hook must be capped at 75 words"


def test_hook_word_cap_medium(medium_strategy):
    targets = medium_strategy.calculate_section_word_targets(6)
    assert targets["intro"] <= 75


def test_total_target_within_range_short(short_strategy):
    targets = short_strategy.calculate_section_word_targets(4)
    assert 2800 <= targets["total_target"] <= 3000


def test_total_target_within_range_medium(medium_strategy):
    targets = medium_strategy.calculate_section_word_targets(6)
    assert 5600 <= targets["total_target"] <= 6000


# ── SectionType determination ─────────────────────────────────────────────────


def test_first_section_is_hook_intro():
    strategy = WordCountStrategy("short")
    t = strategy._determine_section_type(section_index=0, total_sections=4)
    assert t == SectionType.HOOK_INTRO


def test_last_section_is_conclusion():
    strategy = WordCountStrategy("short")
    t = strategy._determine_section_type(section_index=3, total_sections=4)
    assert t == SectionType.CONCLUSION


def test_middle_sections_are_main_content():
    strategy = WordCountStrategy("short")
    for idx in range(1, 3):  # indices 1 and 2 in a 4-section script
        t = strategy._determine_section_type(section_index=idx, total_sections=4)
        assert t == SectionType.MAIN_CONTENT


# ── WordCountStrategy.validate_word_count ─────────────────────────────────────


def test_validate_within_tolerance():
    strategy = WordCountStrategy("medium")
    # target=1000, actual=980 → 2% under — within 5% tolerance
    content = " ".join(["word"] * 980)
    is_valid, actual, msg = strategy.validate_word_count(content, target_words=1000)
    assert is_valid is True
    assert actual == 980


def test_validate_too_short_fails():
    strategy = WordCountStrategy("medium")
    # target=1000, actual=800 → 20% under
    content = " ".join(["word"] * 800)
    is_valid, actual, msg = strategy.validate_word_count(content, target_words=1000)
    assert is_valid is False
    assert actual < 1000


def test_validate_too_long_fails():
    strategy = WordCountStrategy("medium")
    # target=1000, actual=1200 → 20% over
    content = " ".join(["word"] * 1200)
    is_valid, actual, msg = strategy.validate_word_count(content, target_words=1000)
    assert is_valid is False


# ── WordCountStrategy.calculate_timing_for_sections ──────────────────────────


def test_timing_starts_at_zero():
    strategy = WordCountStrategy("medium")
    # Use word_count key (not content) — that's what the method reads
    sections = [{"word_count": 280}]  # 280 words ≈ 2 min at 140 wpm
    result = strategy.calculate_timing_for_sections(sections)
    assert result[0]["start_time"] == "00:00"


def test_timing_format_is_mm_ss():
    strategy = WordCountStrategy("medium")
    sections = [{"word_count": 140}]  # exactly 1 minute
    result = strategy.calculate_timing_for_sections(sections)
    assert result[0]["end_time"] == "01:00"


def test_timing_chain_is_continuous():
    """The start_time of section N+1 equals the end_time of section N."""
    strategy = WordCountStrategy("medium")
    sections = [{"word_count": 140}, {"word_count": 140}]
    result = strategy.calculate_timing_for_sections(sections)
    assert result[1]["start_time"] == result[0]["end_time"]
