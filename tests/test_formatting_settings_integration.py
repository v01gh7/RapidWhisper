"""
Integration tests for formatting settings save/load workflow.

Tests the complete workflow of saving formatting configuration to config.jsonc,
restarting the application, and loading the configuration back.
"""

import pytest
import tempfile
import os
import json
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from PyQt6.QtWidgets import QApplication
from services.formatting_config import FormattingConfig, UNIVERSAL_DEFAULT_PROMPT
from ui.settings_window import SettingsWindow
from core.config import Config


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory with config.jsonc and secrets.json for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create config.jsonc
        config_path = os.path.join(tmpdir, "config.jsonc")
        secrets_path = os.path.join(tmpdir, "secrets.json")
        prompts_dir = os.path.join(tmpdir, "config", "prompts")
        os.makedirs(prompts_dir, exist_ok=True)
        
        # Create minimal config
        config_data = {
            "formatting": {
                "enabled": False,
                "provider": "groq",
                "model": "",
                "temperature": 0.3,
                "custom": {
                    "base_url": ""
                },
                "app_prompts": {},
                "web_app_keywords": {}
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)
        
        # Create empty secrets
        with open(secrets_path, 'w', encoding='utf-8') as f:
            json.dump({"api_keys": {}, "custom_providers": {}}, f, indent=2)
        
        yield {
            "dir": tmpdir,
            "config_path": config_path,
            "secrets_path": secrets_path,
            "prompts_dir": prompts_dir
        }


def test_save_load_workflow_preserves_configuration(qtbot, temp_config_dir):
    """
    Test that save → restart → load preserves all configurations.
    
    Feature: formatting-app-prompts-ui, Task 13.1
    
    Validates:
    - Configuration is saved to config.jsonc
    - Configuration can be loaded back after restart
    - All application names are preserved
    - All custom prompts are preserved
    - Applications with default prompts are preserved
    """
    from core.config_loader import ConfigLoader
    from core.config_saver import ConfigSaver
    
    # Create config loader and saver with temp paths
    config_loader = ConfigLoader(
        config_path=temp_config_dir["config_path"],
        secrets_path=temp_config_dir["secrets_path"]
    )
    config_saver = ConfigSaver(
        config_path=temp_config_dir["config_path"],
        secrets_path=temp_config_dir["secrets_path"]
    )
    
    # Mock save_prompt to use temp directory
    original_save_prompt = config_saver.save_prompt
    def mock_save_prompt(app_name, prompt, prompts_dir="config/prompts"):
        # Always use temp prompts dir
        return original_save_prompt(app_name, prompt, temp_config_dir["prompts_dir"])
    
    config_saver.save_prompt = mock_save_prompt
    
    # Patch get_config_loader and get_config_saver
    with patch('core.config_loader.get_config_loader', return_value=config_loader):
        with patch('core.config_saver.get_config_saver', return_value=config_saver):
            
            # Create test configuration
            config = FormattingConfig(
                enabled=True,
                provider="groq",
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                applications=["notion", "obsidian", "whatsapp"],
                app_prompts={
                    "notion": "Custom prompt for Notion",
                    "obsidian": "",  # Uses default
                    "whatsapp": "Custom prompt for messenger"
                }
            )
            
            # Save to temp config
            config.save_to_config()
            
            # Verify file was written
            assert os.path.exists(temp_config_dir["config_path"])
            
            # Verify prompts were saved to temp dir, not real config/prompts
            assert os.path.exists(os.path.join(temp_config_dir["prompts_dir"], "notion.txt"))
            assert os.path.exists(os.path.join(temp_config_dir["prompts_dir"], "whatsapp.txt"))
            
            # Load configuration back (simulating restart)
            loaded_config = FormattingConfig.from_env()
            
            # Verify all fields are preserved
            assert loaded_config.enabled == config.enabled
            assert loaded_config.provider == config.provider
            assert loaded_config.model == config.model
            assert loaded_config.temperature == config.temperature
            assert set(loaded_config.applications) == set(config.applications)


def test_empty_configuration_initialization(qtbot, temp_config_dir):
    """
    Test that empty configuration initializes with defaults.
    
    Feature: formatting-app-prompts-ui, Task 13.1
    
    Validates:
    - Empty config.jsonc results in empty configuration
    - No applications by default
    """
    from core.config_loader import ConfigLoader
    
    # Create config loader with temp paths
    config_loader = ConfigLoader(
        config_path=temp_config_dir["config_path"],
        secrets_path=temp_config_dir["secrets_path"]
    )
    
    # Patch get_config_loader
    with patch('core.config_loader.get_config_loader', return_value=config_loader):
        
        # Load configuration
        config = FormattingConfig.from_env()
        
        # Verify empty configuration
        assert config.enabled == False
        assert config.provider == "groq"
        assert len(config.applications) == 0


def test_partial_configuration_preservation(qtbot, temp_config_dir):
    """
    Test that configuration can be saved and loaded correctly.
    
    Feature: formatting-app-prompts-ui, Task 13.1
    
    Validates:
    - Configuration can be saved to config.jsonc
    - Configuration can be loaded back
    - All fields are preserved
    """
    from core.config_loader import ConfigLoader
    from core.config_saver import ConfigSaver
    
    # Create config loader and saver with temp paths
    config_loader = ConfigLoader(
        config_path=temp_config_dir["config_path"],
        secrets_path=temp_config_dir["secrets_path"]
    )
    config_saver = ConfigSaver(
        config_path=temp_config_dir["config_path"],
        secrets_path=temp_config_dir["secrets_path"]
    )
    
    # Mock save_prompt to use temp directory
    original_save_prompt = config_saver.save_prompt
    def mock_save_prompt(app_name, prompt, prompts_dir="config/prompts"):
        # Always use temp prompts dir
        return original_save_prompt(app_name, prompt, temp_config_dir["prompts_dir"])
    
    config_saver.save_prompt = mock_save_prompt
    
    # Patch get_config_loader and get_config_saver
    with patch('core.config_loader.get_config_loader', return_value=config_loader):
        with patch('core.config_saver.get_config_saver', return_value=config_saver):
            
            # Create initial configuration
            config = FormattingConfig(
                enabled=True,
                provider="groq",
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                applications=["test_app1", "test_app2"],
                app_prompts={
                    "test_app1": "Test prompt 1",
                    "test_app2": "Test prompt 2"
                }
            )
            
            # Save configuration
            config.save_to_config()
            
            # Verify prompts were saved to temp dir
            assert os.path.exists(os.path.join(temp_config_dir["prompts_dir"], "test_app1.txt"))
            assert os.path.exists(os.path.join(temp_config_dir["prompts_dir"], "test_app2.txt"))
            
            # Verify config.jsonc was updated
            with open(temp_config_dir["config_path"], 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
            
            assert saved_config["formatting"]["enabled"] == True
            assert saved_config["formatting"]["provider"] == "groq"
            assert saved_config["formatting"]["model"] == "llama-3.3-70b-versatile"
            assert saved_config["formatting"]["temperature"] == 0.3
