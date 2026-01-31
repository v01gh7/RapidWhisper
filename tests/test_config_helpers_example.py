"""
Example tests using test_helpers.

This file demonstrates how to use test_helpers for cleaner tests.
"""

import pytest
from tests.test_helpers import (
    load_test_config,
    create_test_formatting_config,
    get_test_prompt,
    assert_config_valid,
    assert_formatting_config_valid
)


def test_load_minimal_config():
    """Test loading minimal configuration"""
    loader = load_test_config("minimal")
    
    assert loader.config is not None
    assert loader.config["ai_provider"]["provider"] == "groq"
    assert loader.config["formatting"]["enabled"] == False
    
    # Validate config structure
    assert_config_valid(loader.config)


def test_load_formatting_config():
    """Test loading formatting configuration"""
    loader = load_test_config("formatting", with_secrets=True)
    
    assert loader.config is not None
    assert loader.config["formatting"]["enabled"] == True
    assert "api_keys" in loader.config["ai_provider"]
    
    # Validate config structure
    assert_config_valid(loader.config)


def test_create_formatting_config():
    """Test creating FormattingConfig from test config"""
    config = create_test_formatting_config("formatting")
    
    assert config.enabled == True
    assert config.provider == "groq"
    assert "notion" in config.applications
    assert "whatsapp" in config.applications
    assert "test_app" in config.applications
    
    # Validate FormattingConfig
    assert_formatting_config_valid(config)


def test_get_test_prompts():
    """Test loading test prompts"""
    notion_prompt = get_test_prompt("notion")
    assert "Test prompt for Notion" in notion_prompt
    assert "markdown" in notion_prompt.lower()
    
    whatsapp_prompt = get_test_prompt("whatsapp")
    assert "Test prompt for WhatsApp" in whatsapp_prompt
    assert "*bold*" in whatsapp_prompt
    
    test_app_prompt = get_test_prompt("test_app")
    assert "Test prompt for generic" in test_app_prompt


def test_config_values():
    """Test accessing configuration values"""
    loader = load_test_config("minimal")
    
    # Test dot-notation access
    provider = loader.get("ai_provider.provider")
    assert provider == "groq"
    
    width = loader.get("window.width")
    assert width == 400
    
    enabled = loader.get("formatting.enabled")
    assert enabled == False
    
    # Test default values
    missing = loader.get("nonexistent.key", "default")
    assert missing == "default"


def test_formatting_config_prompts():
    """Test FormattingConfig prompt loading"""
    config = create_test_formatting_config("formatting")
    
    # Test getting prompts for different apps
    notion_prompt = config.get_prompt_for_app("notion")
    assert len(notion_prompt) > 0
    assert "Test prompt for Notion" in notion_prompt
    
    whatsapp_prompt = config.get_prompt_for_app("whatsapp")
    assert len(whatsapp_prompt) > 0
    assert "Test prompt for WhatsApp" in whatsapp_prompt


# Pytest fixtures examples
def test_with_minimal_fixture(minimal_config):
    """Test using minimal_config fixture"""
    assert minimal_config.config["ai_provider"]["provider"] == "groq"


def test_with_formatting_fixture(formatting_config):
    """Test using formatting_config fixture"""
    assert formatting_config.config["formatting"]["enabled"] == True


def test_with_formatting_config_fixture(test_formatting_config):
    """Test using test_formatting_config fixture"""
    assert test_formatting_config.enabled == True
    assert "notion" in test_formatting_config.applications


if __name__ == "__main__":
    # Run tests without pytest
    print("Running tests...")
    
    test_load_minimal_config()
    print("✓ test_load_minimal_config")
    
    test_load_formatting_config()
    print("✓ test_load_formatting_config")
    
    test_create_formatting_config()
    print("✓ test_create_formatting_config")
    
    test_get_test_prompts()
    print("✓ test_get_test_prompts")
    
    test_config_values()
    print("✓ test_config_values")
    
    test_formatting_config_prompts()
    print("✓ test_formatting_config_prompts")
    
    print("\nAll tests passed! ✅")
