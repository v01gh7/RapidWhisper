"""
Tests for fallback formatting functionality.
"""

import pytest
from services.formatting_config import FormattingConfig, FALLBACK_FORMATTING_PROMPT, UNIVERSAL_DEFAULT_PROMPT


def test_fallback_is_in_default_applications():
    """Test that _fallback is included in default applications list."""
    config = FormattingConfig.from_env()
    
    assert "_fallback" in config.applications, "_fallback should be in applications list"


def test_fallback_has_default_prompt():
    """Test that _fallback has a default prompt when loaded from env."""
    config = FormattingConfig.from_env()
    
    fallback_prompt = config.get_prompt_for_app("_fallback")
    
    # Should have the fallback prompt (either custom or default)
    assert len(fallback_prompt) > 0, "_fallback should have a prompt"
    assert "TRANSCRIPT FORMATTING ENGINE" in fallback_prompt or "text formatting engine" in fallback_prompt.lower()


def test_unknown_app_uses_fallback_prompt():
    """Test that unknown applications use the fallback prompt."""
    config = FormattingConfig(
        enabled=True,
        applications=["notion", "obsidian", "_fallback"]
    )
    
    # Set a custom fallback prompt
    custom_fallback = "Custom fallback formatting prompt"
    config.set_prompt_for_app("_fallback", custom_fallback)
    
    # Unknown app should use fallback prompt
    unknown_prompt = config.get_prompt_for_app("unknown_app_12345")
    assert unknown_prompt == custom_fallback


def test_known_app_without_prompt_uses_universal_default():
    """Test that known apps without custom prompts use universal default."""
    config = FormattingConfig(
        enabled=True,
        applications=["notion", "obsidian", "_fallback"]
    )
    
    # Known app without custom prompt should use universal default
    notion_prompt = config.get_prompt_for_app("notion")
    assert notion_prompt == UNIVERSAL_DEFAULT_PROMPT


def test_fallback_prompt_is_editable():
    """Test that _fallback prompt can be customized."""
    config = FormattingConfig(
        enabled=True,
        applications=["notion", "_fallback"]
    )
    
    # Set custom fallback prompt
    custom_prompt = "My custom fallback prompt"
    config.set_prompt_for_app("_fallback", custom_prompt)
    
    # Verify it was set
    retrieved = config.get_prompt_for_app("_fallback")
    assert retrieved == custom_prompt
    
    # Verify unknown apps use it
    unknown_prompt = config.get_prompt_for_app("some_random_app")
    assert unknown_prompt == custom_prompt


def test_fallback_cannot_be_deleted_from_applications():
    """Test that _fallback is always present in applications list after from_env()."""
    config = FormattingConfig.from_env()
    
    # Even if we try to remove it, it should be re-added by from_env()
    original_count = len(config.applications)
    assert "_fallback" in config.applications
    
    # Save and reload
    config.save_to_env()
    reloaded_config = FormattingConfig.from_env()
    
    # Should still be there
    assert "_fallback" in reloaded_config.applications


def test_fallback_uses_hardcoded_default_when_empty():
    """Test that _fallback uses hardcoded default when no custom prompt is set."""
    config = FormattingConfig(
        enabled=True,
        applications=["notion", "_fallback"]
    )
    
    # Don't set any custom prompt for _fallback
    config.app_prompts["_fallback"] = ""
    
    # Should return hardcoded fallback prompt
    fallback_prompt = config.get_prompt_for_app("_fallback")
    assert fallback_prompt == FALLBACK_FORMATTING_PROMPT
    
    # Unknown apps should also use it
    unknown_prompt = config.get_prompt_for_app("unknown_app")
    assert unknown_prompt == FALLBACK_FORMATTING_PROMPT
