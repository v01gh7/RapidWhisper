"""
Unit tests for format-specific prompts.

These tests validate that each format type has appropriate
formatting instructions in its prompt.
"""

import pytest
from services.formatting_module import get_format_prompt, FORMAT_PROMPTS


class TestFormattingPrompts:
    """Unit tests for formatting prompts."""
    
    def test_notion_prompt_contains_notion_instructions(self):
        """
        Test that Notion prompt contains Notion-specific instructions.
        
        Requirements: 6.1
        """
        prompt = get_format_prompt("notion")
        
        # Check for Notion-specific keywords
        assert "notion" in prompt.lower(), "Prompt should mention Notion"
        assert "#" in prompt, "Prompt should mention headings with #"
        assert "bullet" in prompt.lower() or "-" in prompt or "•" in prompt, \
            "Prompt should mention bullet points"
        assert "bold" in prompt.lower() or "**" in prompt, \
            "Prompt should mention bold formatting"
    
    def test_obsidian_prompt_contains_wiki_links(self):
        """
        Test that Obsidian prompt contains wiki-link instructions.
        
        Requirements: 6.2
        """
        prompt = get_format_prompt("obsidian")
        
        # Check for Obsidian-specific keywords
        assert "obsidian" in prompt.lower(), "Prompt should mention Obsidian"
        assert "[[" in prompt or "wiki" in prompt.lower(), \
            "Prompt should mention wiki-links"
        assert "#" in prompt, "Prompt should mention headings or tags"
        assert "markdown" in prompt.lower(), "Prompt should mention markdown"
    
    def test_markdown_prompt_contains_standard_syntax(self):
        """
        Test that Markdown prompt contains standard markdown syntax.
        
        Requirements: 6.3
        """
        prompt = get_format_prompt("markdown")
        
        # Check for standard markdown keywords
        assert "markdown" in prompt.lower(), "Prompt should mention markdown"
        assert "#" in prompt, "Prompt should mention headings"
        assert "-" in prompt or "list" in prompt.lower(), \
            "Prompt should mention lists"
        assert "```" in prompt or "code" in prompt.lower(), \
            "Prompt should mention code blocks"
    
    def test_word_prompt_avoids_markdown_syntax(self):
        """
        Test that Word prompt avoids markdown syntax.
        
        Requirements: 6.4
        """
        prompt = get_format_prompt("word")
        
        # Check for Word-specific keywords
        assert "word" in prompt.lower(), "Prompt should mention Word"
        assert "paragraph" in prompt.lower() or "heading" in prompt.lower(), \
            "Prompt should mention paragraphs or headings"
        
        # Word prompt should avoid complex markdown syntax
        # It's okay to mention simple formatting, but should emphasize simplicity
        assert "simple" in prompt.lower() or "avoid" in prompt.lower(), \
            "Prompt should emphasize simple formatting"
    
    def test_all_format_types_have_prompts(self):
        """
        Test that all format types in FORMAT_PROMPTS have non-empty prompts.
        """
        for format_type in FORMAT_PROMPTS.keys():
            prompt = get_format_prompt(format_type)
            assert prompt, f"Prompt for {format_type} is empty"
            assert len(prompt) > 20, f"Prompt for {format_type} is too short"
    
    def test_unknown_format_returns_markdown_prompt(self):
        """
        Test that unknown format types return the markdown prompt as default.
        """
        unknown_format = "unknown_format_xyz"
        prompt = get_format_prompt(unknown_format)
        markdown_prompt = get_format_prompt("markdown")
        
        assert prompt == markdown_prompt, \
            "Unknown format should return markdown prompt as default"
    
    def test_prompts_are_strings(self):
        """
        Test that all prompts are strings.
        """
        for format_type, prompt in FORMAT_PROMPTS.items():
            assert isinstance(prompt, str), \
                f"Prompt for {format_type} is not a string: {type(prompt)}"
    
    def test_prompts_contain_formatting_instructions(self):
        """
        Test that all prompts contain formatting-related keywords.
        """
        formatting_keywords = ["format", "use", "add", "heading", "list", "bullet"]
        
        for format_type, prompt in FORMAT_PROMPTS.items():
            prompt_lower = prompt.lower()
            has_keyword = any(keyword in prompt_lower for keyword in formatting_keywords)
            assert has_keyword, \
                f"Prompt for {format_type} doesn't contain formatting instructions"
