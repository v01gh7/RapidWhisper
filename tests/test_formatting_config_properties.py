"""
Property-based tests for transcription formatting configuration.

These tests validate universal properties that should hold across all
possible configuration values.
"""

import pytest
import tempfile
import os
from pathlib import Path
from hypothesis import given, strategies as st, settings
from services.formatting_config import FormattingConfig


# Strategy for generating valid configurations
@st.composite
def config_strategy(draw):
    """Generate valid FormattingConfig instances."""
    enabled = draw(st.booleans())
    provider = draw(st.sampled_from(["groq", "openai", "glm", "custom"]))
    model = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='-_.'
    )))
    applications = draw(st.lists(
        st.text(min_size=1, max_size=20, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='-_.'
        )),
        min_size=1,
        max_size=10
    ))
    
    return FormattingConfig(
        enabled=enabled,
        provider=provider,
        model=model,
        applications=applications
    )


class TestFormattingConfigProperties:
    """Property-based tests for FormattingConfig."""
    
    @given(config=config_strategy())
    @settings(max_examples=20)
    def test_config_round_trip_persistence(self, config):
        """
        Feature: transcription-formatting, Property 2: Configuration Round-Trip Persistence
        
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
        
        For any valid formatting configuration, saving then loading should preserve all values.
        """
        # Create temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            temp_env_path = f.name
        
        try:
            # Save configuration
            config.save_to_env(temp_env_path)
            
            # Load configuration
            loaded_config = FormattingConfig.from_env(temp_env_path)
            
            # Assert all values are preserved
            assert loaded_config.enabled == config.enabled, \
                f"Enabled mismatch: {loaded_config.enabled} != {config.enabled}"
            assert loaded_config.provider == config.provider, \
                f"Provider mismatch: {loaded_config.provider} != {config.provider}"
            assert loaded_config.model == config.model, \
                f"Model mismatch: {loaded_config.model} != {config.model}"
            assert loaded_config.applications == config.applications, \
                f"Applications mismatch: {loaded_config.applications} != {config.applications}"
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_env_path):
                os.remove(temp_env_path)
    
    @given(
        formatting_config=config_strategy(),
        other_key=st.text(min_size=1, max_size=20, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_'
        )),
        other_value=st.text(min_size=0, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
            whitelist_characters='-_./:'
        ))
    )
    @settings(max_examples=20)
    def test_config_independence(self, formatting_config, other_key, other_value):
        """
        Feature: transcription-formatting, Property 1: Configuration Independence
        
        **Validates: Requirements 1.7, 4.5, 7.6**
        
        For any formatting configuration changes, modifying formatting settings
        should not affect other configuration values.
        """
        # Skip if other_key conflicts with formatting keys
        formatting_keys = {
            "FORMATTING_ENABLED", "FORMATTING_PROVIDER", 
            "FORMATTING_MODEL", "FORMATTING_APPLICATIONS"
        }
        if other_key in formatting_keys:
            return
        
        # Skip if other_value contains newlines (not valid in .env values)
        if '\n' in other_value or '\r' in other_value:
            return
        
        # Create temporary .env file with other configuration
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
            temp_env_path = f.name
            f.write(f"{other_key}={other_value}\n")
        
        try:
            # Save formatting configuration
            formatting_config.save_to_env(temp_env_path)
            
            # Read the file and check other_key is preserved
            with open(temp_env_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check that other_key is still present
            assert f"{other_key}=" in content, \
                f"Other configuration key {other_key} was removed"
            
            # Verify the value is preserved
            lines = content.split('\n')
            other_key_found = False
            for line in lines:
                if line.strip().startswith(f"{other_key}="):
                    actual_value = line.split('=', 1)[1]
                    assert actual_value == other_value, \
                        f"Other configuration value changed: {actual_value} != {other_value}"
                    other_key_found = True
                    break
            
            assert other_key_found, f"Other configuration key {other_key} not found after save"
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_env_path):
                os.remove(temp_env_path)
    
    @given(config=config_strategy())
    @settings(max_examples=20)
    def test_to_env_format(self, config):
        """
        Test that to_env() produces valid environment variable format.
        
        For any configuration, to_env() should return a dictionary with
        string keys and string values.
        """
        env_dict = config.to_env()
        
        # Check all keys are present
        assert "FORMATTING_ENABLED" in env_dict
        assert "FORMATTING_PROVIDER" in env_dict
        assert "FORMATTING_MODEL" in env_dict
        assert "FORMATTING_APPLICATIONS" in env_dict
        
        # Check all values are strings
        for key, value in env_dict.items():
            assert isinstance(value, str), f"{key} value is not a string: {type(value)}"
        
        # Check enabled is "true" or "false"
        assert env_dict["FORMATTING_ENABLED"] in ["true", "false"]
        
        # Check provider is valid
        assert env_dict["FORMATTING_PROVIDER"] in ["groq", "openai", "glm", "custom"]
        
        # Check applications is comma-separated
        if config.applications:
            apps_str = env_dict["FORMATTING_APPLICATIONS"]
            parsed_apps = [app.strip() for app in apps_str.split(",") if app.strip()]
            assert parsed_apps == config.applications
    
    @given(
        enabled=st.booleans(),
        provider=st.sampled_from(["groq", "openai", "glm", "custom"]),
        model=st.text(min_size=1, max_size=50),
        applications=st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=10)
    )
    @settings(max_examples=20)
    def test_is_valid_property(self, enabled, provider, model, applications):
        """
        Test that is_valid() correctly identifies valid configurations.
        
        A configuration is valid if:
        - provider is in ["groq", "openai", "glm", "custom"]
        - model is not empty
        - applications list is not empty
        """
        config = FormattingConfig(
            enabled=enabled,
            provider=provider,
            model=model,
            applications=applications
        )
        
        expected_valid = (
            provider in ["groq", "openai", "glm", "custom"] and
            bool(model) and
            bool(applications)
        )
        
        assert config.is_valid() == expected_valid, \
            f"is_valid() returned {config.is_valid()}, expected {expected_valid}"
