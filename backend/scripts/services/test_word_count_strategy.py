#!/usr/bin/env python3
"""
Test script for the Word Count Strategy implementation

This script tests the new word count completion strategy to ensure it works correctly.
Run this from the Django shell or as a standalone test.
"""

import os
import sys
import django
from typing import Dict, Any

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from scripts.services.word_count_strategy import WordCountStrategy, SectionType


def test_word_count_calculations():
    """Test word count calculation for different template styles"""
    print("=== Testing Word Count Calculations ===")
    
    templates = ["short", "medium", "long"]
    
    for template in templates:
        print(f"\n--- {template.upper()} Template ---")
        strategy = WordCountStrategy(template)
        
        # Test with default sections
        targets = strategy.calculate_section_word_targets()
        print(f"Default sections ({targets['num_sections']}):")
        print(f"  Intro: {targets['intro']} words")
        print(f"  Main sections: {targets['main_sections']} words each ({targets['main_sections_count']} sections)")
        print(f"  Conclusion: {targets['conclusion']} words")
        print(f"  Total target: {targets['total_target']} words")
        print(f"  Min/Max: {targets['min_words']}-{targets['max_words']} words")
        
        # Test with custom sections
        custom_targets = strategy.calculate_section_word_targets(8)
        print(f"\nCustom sections (8):")
        print(f"  Total target: {custom_targets['total_target']} words")
        print(f"  Main sections: {custom_targets['main_sections']} words each")


def test_section_type_detection():
    """Test section type detection logic"""
    print("\n=== Testing Section Type Detection ===")
    
    strategy = WordCountStrategy("medium")
    
    test_cases = [
        (0, 5, "First section"),
        (1, 5, "Second section"),
        (2, 5, "Middle section"),
        (3, 5, "Second to last"),
        (4, 5, "Last section"),
    ]
    
    for section_index, total_sections, description in test_cases:
        section_type = strategy._determine_section_type(section_index, total_sections)
        print(f"{description} (index {section_index}/{total_sections-1}): {section_type.value}")


def test_strategy_selection():
    """Test strategy selection for different section types"""
    print("\n=== Testing Strategy Selection ===")
    
    strategy = WordCountStrategy("medium")
    
    section_types = [SectionType.HOOK_INTRO, SectionType.MAIN_CONTENT, SectionType.CONCLUSION]
    
    for section_type in section_types:
        strategies = strategy.get_strategies_for_section_type(0, 5)  # Mock parameters
        print(f"{section_type.value}: {len(strategies)} strategies")
        print(f"  Sample strategies: {strategies[:5]}...")


def test_word_count_validation():
    """Test word count validation logic"""
    print("\n=== Testing Word Count Validation ===")
    
    strategy = WordCountStrategy("medium")
    
    test_cases = [
        ("Short content with few words", 50, 100, False),
        ("This is a medium length content that should be around the target word count for validation testing purposes.", 100, 100, True),
        ("This is a very long content that exceeds the maximum word count by a significant margin. It contains many more words than the target and should be flagged as too long for the validation system to properly handle.", 100, 100, False),
    ]
    
    for content, target, expected_target, should_be_valid in test_cases:
        is_valid, actual_words, message = strategy.validate_word_count(content, target)
        print(f"Target: {target} words")
        print(f"Actual: {actual_words} words")
        print(f"Valid: {is_valid} (expected: {should_be_valid})")
        print(f"Message: {message}")
        print()


def test_expansion_strategies():
    """Test expansion strategies for different section types"""
    print("\n=== Testing Expansion Strategies ===")
    
    strategy = WordCountStrategy("medium")
    
    for section_type in [SectionType.HOOK_INTRO, SectionType.MAIN_CONTENT, SectionType.CONCLUSION]:
        strategies = strategy.get_expansion_strategies(section_type)
        print(f"{section_type.value}:")
        for i, strategy_text in enumerate(strategies, 1):
            print(f"  {i}. {strategy_text}")
        print()


def test_prompt_building():
    """Test section-specific prompt building"""
    print("\n=== Testing Prompt Building ===")
    
    strategy = WordCountStrategy("medium")
    
    sample_section = {
        "title": "Introduction to Python",
        "description": "Learn the basics of Python programming language",
        "key_points": [
            "Python is a versatile programming language",
            "It's great for beginners",
            "Used in web development, data science, and AI"
        ]
    }
    
    storytelling_manual = "Sample storytelling manual content..."
    
    prompt = strategy.build_section_specific_prompt(
        section_data=sample_section,
        section_index=0,
        total_sections=5,
        word_target=500,
        storytelling_manual=storytelling_manual
    )
    
    print("Generated prompt preview:")
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)


def run_all_tests():
    """Run all tests"""
    print("🧪 Running Word Count Strategy Tests")
    print("=" * 50)
    
    try:
        test_word_count_calculations()
        test_section_type_detection()
        test_strategy_selection()
        test_word_count_validation()
        test_expansion_strategies()
        test_prompt_building()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
