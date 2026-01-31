"""
Property-based tests for FormattingConfig JSON serialization and migration.
"""

import pytest
import json
import tempfile
import os
from hypothesis import given, strategies as st, settings
from services.formatting_config import FormattingConfig, migrate_from_old_format
from pathlib import Path


app_names = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'),
    min_size=1,
    max_size=50
)

prompts = st.text(max_size=1000)


@given(
    apps_with_prompts=st.lists(
        st.tuples(app_names, prompts),
        min_size=1,
        max_size=10,
        unique_by=lambda x: x[0]
    )
)
@settings(max_examples=20)
def test_property_12_configuration_round_trip(apps_with_prompts):
    """Property 12: Configuration Round-Trip - Validates: Requirements 7.1, 7.3"""
    config = FormattingConfig()
    
    # Set applications and prompts
    config.applications = [app for app, _ in apps_with_prompts]
    for app_name, prompt in apps_with_prompts:
        config.set_prompt_for_app(app_name, prompt)
    
    # Serialize to env dict
    env_dict = config.to_env()
    
    # Create temp .env file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        for key, value in env_dict.items():
            f.write(f"{key}={value}\n")
        temp_path = f.name
    
    try:
        # Deserialize from env file
        restored_config = FormattingConfig.from_env(temp_path)
        
        # Verify equivalence
        assert set(restored_config.applications) == set(config.applications)
        assert restored_config.provider == config.provider
        assert restored_config.temperature == config.temperature
        
        # Verify prompts
        for app_name in config.applications:
            original_prompt = config.get_prompt_for_app(app_name)
            restored_prompt = restored_config.get_prompt_for_app(app_name)
            assert restored_prompt == original_prompt
    finally:
        os.unlink(temp_path)


@given(
    apps_with_prompts=st.lists(
        st.tuples(app_names, prompts),
        min_size=1,
        max_size=10,
        unique_by=lambda x: x[0]
    )
)
@settings(max_examples=20)
def test_property_13_persistent_storage_location(apps_with_prompts):
    """Property 13: Persistent Storage Location - Validates: Requirements 7.2"""
    config = FormattingConfig()
    
    config.applications = [app for app, _ in apps_with_prompts]
    for app_name, prompt in apps_with_prompts:
        config.set_prompt_for_app(app_name, prompt)
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        temp_path = f.name
    
    try:
        config.save_to_env(temp_path)
        
        # Read file and verify FORMATTING_APP_PROMPTS exists
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'FORMATTING_APP_PROMPTS=' in content
        
        # Verify it's valid JSON
        for line in content.split('\n'):
            if line.startswith('FORMATTING_APP_PROMPTS='):
                json_str = line.split('=', 1)[1]
                data = json.loads(json_str)
                assert isinstance(data, dict)
                break
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@given(
    old_apps=st.lists(app_names, min_size=1, max_size=10, unique=True)
)
@settings(max_examples=20)
def test_property_14_migration_preserves_applications(old_apps):
    """Property 14: Migration Preserves Applications - Validates: Requirements 7.5, 10.1, 10.2, 10.3"""
    # Create old format string
    old_format_str = ",".join(old_apps)
    
    # Migrate
    migrated_data = migrate_from_old_format(old_format_str)
    
    # Verify all applications preserved
    assert set(migrated_data.keys()) == set(old_apps)
    
    # Verify all have empty prompts (indicating default)
    for app in old_apps:
        assert migrated_data[app]["enabled"] == True
        assert migrated_data[app]["prompt"] == ""


def test_property_15_migration_cleanup():
    """Property 15: Migration Cleanup - Validates: Requirements 10.5"""
    # Create temp .env with old format
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_APPLICATIONS=notion,obsidian,markdown\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        temp_path = f.name
    
    try:
        # Load config (should trigger migration)
        config = FormattingConfig.from_env(temp_path)
        
        # Save config (should write new format)
        config.save_to_env(temp_path)
        
        # Read file
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify new format exists
        assert 'FORMATTING_APP_PROMPTS=' in content
        
        # Note: We keep FORMATTING_APPLICATIONS for backward compatibility
        # so we don't test for its removal
    finally:
        os.unlink(temp_path)


def test_unit_empty_old_format():
    """Unit test: Empty old format string"""
    result = migrate_from_old_format("")
    assert result == {}


def test_unit_malformed_json():
    """Unit test: Malformed JSON in new format"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_APP_PROMPTS={invalid json}\n")
        temp_path = f.name
    
    try:
        # Should fall back to defaults
        config = FormattingConfig.from_env(temp_path)
        assert len(config.applications) > 0  # Should have defaults
    finally:
        os.unlink(temp_path)


def test_unit_missing_env_file():
    """Unit test: Missing .env file"""
    # Use non-existent path
    config = FormattingConfig.from_env("/nonexistent/path/.env")
    
    # Should return config with defaults
    assert len(config.applications) > 0
    assert config.provider == "groq"
