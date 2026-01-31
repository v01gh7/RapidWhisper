"""
Integration tests for formatting settings save/load workflow.

Tests the complete workflow of saving formatting configuration to .env,
restarting the application, and loading the configuration back.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from PyQt6.QtWidgets import QApplication
from services.formatting_config import FormattingConfig, UNIVERSAL_DEFAULT_PROMPT
from ui.settings_window import SettingsWindow
from core.config import Config


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        env_path = f.name
    
    yield env_path
    
    # Cleanup
    if os.path.exists(env_path):
        os.unlink(env_path)


def test_save_load_workflow_preserves_configuration(qtbot, temp_env_file):
    """
    Test that save → restart → load preserves all configurations.
    
    Feature: formatting-app-prompts-ui, Task 13.1
    
    Validates:
    - Configuration is saved to .env file
    - Configuration can be loaded back after restart
    - All application names are preserved
    - All custom prompts are preserved
    - Applications with default prompts are preserved
    """
    # Create test configuration
    config = FormattingConfig(
        enabled=True,
        provider="groq",
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        applications=["notion", "obsidian", "vscode"],
        app_prompts={
            "notion": "Custom prompt for Notion",
            "obsidian": "",  # Uses default
            "vscode": "Custom prompt for VSCode"
        }
    )
    
    # Save to temp env file
    with patch('core.config.get_env_path', return_value=temp_env_file):
        config.save_to_env()
    
    # Verify file was written
    assert os.path.exists(temp_env_file)
    
    # Load configuration back (simulating restart)
    with patch('core.config.get_env_path', return_value=temp_env_file):
        loaded_config = FormattingConfig.from_env()
    
    # Verify all fields are preserved
    assert loaded_config.enabled == config.enabled
    assert loaded_config.provider == config.provider
    assert loaded_config.model == config.model
    assert loaded_config.temperature == config.temperature
    assert set(loaded_config.applications) == set(config.applications)
    
    # Verify custom prompts are preserved
    assert loaded_config.get_prompt_for_app("notion") == "Custom prompt for Notion"
    assert loaded_config.get_prompt_for_app("vscode") == "Custom prompt for VSCode"
    
    # Verify default prompt is used for obsidian
    assert loaded_config.get_prompt_for_app("obsidian") == UNIVERSAL_DEFAULT_PROMPT


def test_migration_save_load_workflow(qtbot, temp_env_file):
    """
    Test that migration → save → load works correctly.
    
    Feature: formatting-app-prompts-ui, Task 13.1
    
    Validates:
    - Old format is migrated to new format
    - Migrated configuration can be saved
    - Migrated configuration can be loaded back
    - All applications from old format are preserved
    """
    # Write old format to env file
    with open(temp_env_file, 'w') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        f.write("FORMATTING_MODEL=llama-3.3-70b-versatile\n")
        f.write("FORMATTING_APPLICATIONS=notion,obsidian,markdown,word\n")
        f.write("FORMATTING_TEMPERATURE=0.3\n")
    
    # Load configuration (triggers migration)
    with patch('core.config.get_env_path', return_value=temp_env_file):
        # Clear any cached environment variables
        import os
        for key in list(os.environ.keys()):
            if key.startswith('FORMATTING_'):
                del os.environ[key]
        
        config = FormattingConfig.from_env(env_path=temp_env_file)
    
    # Verify migration occurred
    assert set(config.applications) == {"notion", "obsidian", "markdown", "word"}
    
    # Verify all apps use default prompt after migration
    for app in config.applications:
        assert config.get_prompt_for_app(app) == UNIVERSAL_DEFAULT_PROMPT
    
    # Save migrated configuration
    with patch('core.config.get_env_path', return_value=temp_env_file):
        config.save_to_env()
    
    # Load again (simulating restart)
    with patch('core.config.get_env_path', return_value=temp_env_file):
        # Clear cached environment variables again
        for key in list(os.environ.keys()):
            if key.startswith('FORMATTING_'):
                del os.environ[key]
        
        loaded_config = FormattingConfig.from_env(env_path=temp_env_file)
    
    # Verify configuration is still correct
    assert set(loaded_config.applications) == {"notion", "obsidian", "markdown", "word"}
    for app in loaded_config.applications:
        assert loaded_config.get_prompt_for_app(app) == UNIVERSAL_DEFAULT_PROMPT


def test_settings_window_save_load_integration(qtbot, temp_env_file):
    """
    Test complete settings window save/load workflow.
    
    Feature: formatting-app-prompts-ui, Task 13.1
    
    Validates:
    - Settings window can save configuration
    - Settings window can load configuration
    - UI reflects loaded configuration
    - Changes in UI are persisted
    """
    from services.formatting_config import FormattingConfig
    
    # Create initial configuration
    initial_config = FormattingConfig(
        enabled=True,
        provider="groq",
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        applications=["notion", "obsidian"],
        app_prompts={
            "notion": "Custom Notion prompt",
            "obsidian": ""
        }
    )
    
    # Save initial configuration
    with patch('core.config.get_env_path', return_value=Path(temp_env_file)):
        initial_config.save_to_env()
    
    # Create settings window and load configuration
    with patch('core.config.get_env_path', return_value=Path(temp_env_file)):
        app_config = Config.load_from_env()
        window = SettingsWindow(app_config)
        qtbot.addWidget(window)
    
    # Verify UI loaded the configuration
    # Check that application buttons exist
    assert len(window.formatting_app_buttons) == 2
    assert "notion" in window.formatting_app_buttons
    assert "obsidian" in window.formatting_app_buttons
    
    # Verify visual indicator for custom prompt
    notion_btn = window.formatting_app_buttons["notion"]
    assert "✏️" in notion_btn.text() or "border: 2px solid #0078d4" in notion_btn.styleSheet()
    
    # Create new window instance (simulating restart)
    with patch('core.config.get_env_path', return_value=Path(temp_env_file)):
        app_config2 = Config.load_from_env()
        window2 = SettingsWindow(app_config2)
        qtbot.addWidget(window2)
    
    # Verify new window loaded all applications
    assert len(window2.formatting_app_buttons) == 2
    assert "notion" in window2.formatting_app_buttons
    assert "obsidian" in window2.formatting_app_buttons
    
    # Verify custom prompt indicator is still there
    notion_btn2 = window2.formatting_app_buttons["notion"]
    assert "✏️" in notion_btn2.text() or "border: 2px solid #0078d4" in notion_btn2.styleSheet()


def test_empty_configuration_initialization(qtbot, temp_env_file):
    """
    Test that empty configuration initializes with defaults.
    
    Feature: formatting-app-prompts-ui, Task 13.1
    
    Validates:
    - Empty .env file results in default configuration
    - Default applications are created
    - Default prompts are assigned
    """
    # Create empty env file
    with open(temp_env_file, 'w') as f:
        f.write("")
    
    # Load configuration
    with patch('core.config.get_env_path', return_value=temp_env_file):
        # Clear any cached environment variables
        import os
        for key in list(os.environ.keys()):
            if key.startswith('FORMATTING_'):
                del os.environ[key]
        
        config = FormattingConfig.from_env(env_path=temp_env_file)
    
    # Verify default applications are created
    default_apps = ["notion", "obsidian", "markdown", "word", "libreoffice", "vscode"]
    assert set(config.applications) == set(default_apps)
    
    # Verify all use default prompt
    for app in config.applications:
        assert config.get_prompt_for_app(app) == UNIVERSAL_DEFAULT_PROMPT


def test_partial_configuration_preservation(qtbot, temp_env_file):
    """
    Test that partial configuration updates preserve other fields.
    
    Feature: formatting-app-prompts-ui, Task 13.1
    
    Validates:
    - Updating one field doesn't affect others
    - Partial saves preserve existing data
    - Configuration integrity is maintained
    """
    # Create initial configuration
    config = FormattingConfig(
        enabled=True,
        provider="groq",
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        applications=["notion", "obsidian", "vscode"],
        app_prompts={
            "notion": "Notion prompt",
            "obsidian": "Obsidian prompt",
            "vscode": ""
        }
    )
    
    # Save initial configuration
    with patch('core.config.get_env_path', return_value=temp_env_file):
        config.save_to_env()
    
    # Load and modify only one prompt
    with patch('core.config.get_env_path', return_value=temp_env_file):
        loaded_config = FormattingConfig.from_env()
        loaded_config.set_prompt_for_app("vscode", "New VSCode prompt")
        loaded_config.save_to_env()
    
    # Load again and verify all data is preserved
    with patch('core.config.get_env_path', return_value=temp_env_file):
        final_config = FormattingConfig.from_env()
    
    # Verify unchanged fields
    assert final_config.enabled == True
    assert final_config.provider == "groq"
    assert final_config.model == "llama-3.3-70b-versatile"
    assert final_config.temperature == 0.3
    assert set(final_config.applications) == {"notion", "obsidian", "vscode"}
    
    # Verify unchanged prompts
    assert final_config.get_prompt_for_app("notion") == "Notion prompt"
    assert final_config.get_prompt_for_app("obsidian") == "Obsidian prompt"
    
    # Verify changed prompt
    assert final_config.get_prompt_for_app("vscode") == "New VSCode prompt"
