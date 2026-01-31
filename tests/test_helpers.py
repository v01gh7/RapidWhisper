"""
Test helpers for RapidWhisper tests.

This module provides helper functions for loading test configurations
and creating test fixtures.
"""

from pathlib import Path
from core.config_loader import ConfigLoader
from services.formatting_config import FormattingConfig


# Test config paths
TEST_CONFIGS_DIR = Path("config/test_configs")
MINIMAL_CONFIG = TEST_CONFIGS_DIR / "minimal_config.jsonc"
FORMATTING_CONFIG = TEST_CONFIGS_DIR / "formatting_enabled_config.jsonc"
TEST_SECRETS = TEST_CONFIGS_DIR / "test_secrets.json"


def load_test_config(config_name: str = "minimal", with_secrets: bool = False):
    """
    Load test configuration.
    
    Args:
        config_name: Name of config to load ("minimal" or "formatting")
        with_secrets: Whether to load test secrets
    
    Returns:
        ConfigLoader instance with loaded config
    
    Example:
        >>> loader = load_test_config("minimal")
        >>> config = loader.config
        >>> assert config["ai_provider"]["provider"] == "groq"
    """
    if config_name == "minimal":
        config_path = str(MINIMAL_CONFIG)
    elif config_name == "formatting":
        config_path = str(FORMATTING_CONFIG)
    else:
        raise ValueError(f"Unknown config name: {config_name}")
    
    secrets_path = str(TEST_SECRETS) if with_secrets else None
    
    loader = ConfigLoader(config_path, secrets_path)
    loader.load()
    
    return loader


def create_test_formatting_config(config_name: str = "formatting"):
    """
    Create FormattingConfig from test configuration.
    
    Args:
        config_name: Name of config to load ("minimal" or "formatting")
    
    Returns:
        FormattingConfig instance
    
    Example:
        >>> config = create_test_formatting_config("formatting")
        >>> assert config.enabled == True
        >>> assert "notion" in config.applications
    """
    loader = load_test_config(config_name, with_secrets=True)
    return FormattingConfig.from_config(loader)


def get_test_prompt(app_name: str) -> str:
    """
    Get test prompt for application.
    
    Args:
        app_name: Application name (e.g., "notion", "whatsapp", "test_app")
    
    Returns:
        Prompt text
    
    Example:
        >>> prompt = get_test_prompt("notion")
        >>> assert "Test prompt for Notion" in prompt
    """
    loader = load_test_config("formatting")
    return loader.get_prompt(app_name)


def assert_config_valid(config: dict):
    """
    Assert that configuration is valid.
    
    Args:
        config: Configuration dictionary
    
    Raises:
        AssertionError: If configuration is invalid
    
    Example:
        >>> loader = load_test_config("minimal")
        >>> assert_config_valid(loader.config)
    """
    # Check required sections
    assert "ai_provider" in config, "Missing ai_provider section"
    assert "application" in config, "Missing application section"
    assert "audio" in config, "Missing audio section"
    assert "window" in config, "Missing window section"
    assert "recording" in config, "Missing recording section"
    assert "post_processing" in config, "Missing post_processing section"
    assert "localization" in config, "Missing localization section"
    assert "logging" in config, "Missing logging section"
    assert "about" in config, "Missing about section"
    assert "formatting" in config, "Missing formatting section"
    
    # Check ai_provider
    assert "provider" in config["ai_provider"], "Missing provider in ai_provider"
    assert config["ai_provider"]["provider"] in ["groq", "openai", "glm", "custom"], \
        f"Invalid provider: {config['ai_provider']['provider']}"
    
    # Check formatting
    assert "enabled" in config["formatting"], "Missing enabled in formatting"
    assert isinstance(config["formatting"]["enabled"], bool), "enabled must be boolean"


def assert_formatting_config_valid(config: FormattingConfig):
    """
    Assert that FormattingConfig is valid.
    
    Args:
        config: FormattingConfig instance
    
    Raises:
        AssertionError: If configuration is invalid
    
    Example:
        >>> config = create_test_formatting_config("formatting")
        >>> assert_formatting_config_valid(config)
    """
    assert config.provider in ["groq", "openai", "glm", "custom"], \
        f"Invalid provider: {config.provider}"
    
    assert 0.0 <= config.temperature <= 1.0, \
        f"Invalid temperature: {config.temperature}"
    
    assert isinstance(config.applications, list), "applications must be list"
    assert len(config.applications) > 0, "applications must not be empty"
    
    assert isinstance(config.app_prompts, dict), "app_prompts must be dict"
    assert isinstance(config.web_app_keywords, dict), "web_app_keywords must be dict"


# Pytest fixtures (if using pytest)
try:
    import pytest
    
    @pytest.fixture
    def minimal_config():
        """Fixture: Minimal test configuration"""
        return load_test_config("minimal")
    
    @pytest.fixture
    def formatting_config():
        """Fixture: Formatting test configuration"""
        return load_test_config("formatting", with_secrets=True)
    
    @pytest.fixture
    def test_formatting_config():
        """Fixture: FormattingConfig instance"""
        return create_test_formatting_config("formatting")
    
except ImportError:
    # pytest not installed, skip fixtures
    pass
