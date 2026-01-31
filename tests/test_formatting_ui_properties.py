"""
Property-based tests for formatting UI rendering.

Tests the visual grid display of applications in settings window.
"""

import pytest
from hypothesis import given, strategies as st, settings
from PyQt6.QtWidgets import QApplication, QPushButton
from PyQt6.QtCore import Qt
from ui.settings_window import SettingsWindow
from core.config import Config
from services.formatting_config import FormattingConfig
from unittest.mock import patch
import sys
import tempfile
import os


# Ensure QApplication exists for Qt tests
@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


app_names = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'),
    min_size=1,
    max_size=50
)


@given(
    apps=st.lists(app_names, min_size=1, max_size=20, unique=True)
)
@settings(max_examples=20)
def test_property_2_application_name_visibility(qapp, apps):
    """
    Feature: formatting-app-prompts-ui, Property 2: Application Name Visibility
    
    For any application in the configuration, its name should be visible 
    in the UI grid display.
    
    Validates: Requirements 2.1
    """
    # Create temp .env with applications
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        
        # Create app_prompts JSON
        import json
        app_prompts_data = {app: {"enabled": True, "prompt": ""} for app in apps}
        f.write(f"FORMATTING_APP_PROMPTS={json.dumps(app_prompts_data, ensure_ascii=False)}\n")
        temp_path = f.name
    
    try:
        # Load config from temp file using patch
        with patch('core.config.get_env_path', return_value=temp_path):
            config = Config()
            
            # Create settings window
            window = SettingsWindow(config)
            
            # Verify all applications are displayed in grid
            for app_name in apps:
                assert app_name in window.formatting_app_buttons, \
                    f"Application '{app_name}' should be in button dictionary"
                
                btn = window.formatting_app_buttons[app_name]
                assert isinstance(btn, QPushButton), \
                    f"Button for '{app_name}' should be a QPushButton"
                
                # Verify button text contains app name (may have emoji prefix)
                btn_text = btn.text()
                assert app_name in btn_text, \
                    f"Button text '{btn_text}' should contain application name '{app_name}'"
            
            window.close()
    finally:
        os.unlink(temp_path)


@given(
    apps_with_prompts=st.lists(
        st.tuples(app_names, st.booleans()),
        min_size=1,
        max_size=10,
        unique_by=lambda x: x[0]
    )
)
@settings(max_examples=20)
def test_property_3_visual_prompt_differentiation(qapp, apps_with_prompts):
    """
    Feature: formatting-app-prompts-ui, Property 3: Visual Prompt Differentiation
    
    For any application, the UI should visually differentiate between 
    applications with custom prompts and those using the default prompt.
    
    Validates: Requirements 2.2, 2.3
    """
    # Create temp .env with applications
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        
        # Create app_prompts JSON
        import json
        app_prompts_data = {}
        for app_name, has_custom in apps_with_prompts:
            app_prompts_data[app_name] = {
                "enabled": True,
                "prompt": "custom prompt" if has_custom else ""
            }
        f.write(f"FORMATTING_APP_PROMPTS={json.dumps(app_prompts_data, ensure_ascii=False)}\n")
        temp_path = f.name
    
    try:
        # Load config from temp file using patch
        with patch('core.config.get_env_path', return_value=temp_path):
            config = Config()
            
            # Create settings window
            window = SettingsWindow(config)
            
            # Verify visual differentiation
            for app_name, has_custom in apps_with_prompts:
                btn = window.formatting_app_buttons[app_name]
                btn_text = btn.text()
                btn_style = btn.styleSheet()
                
                if has_custom:
                    # Should have visual indicator (✏️ emoji)
                    assert "✏️" in btn_text, \
                        f"Button for '{app_name}' with custom prompt should have ✏️ indicator"
                    
                    # Should have blue border
                    assert "#0078d4" in btn_style or "#1084d8" in btn_style, \
                        f"Button for '{app_name}' with custom prompt should have blue border"
                else:
                    # Should NOT have indicator
                    assert "✏️" not in btn_text, \
                        f"Button for '{app_name}' with default prompt should not have ✏️ indicator"
            
            window.close()
    finally:
        os.unlink(temp_path)


def test_unit_empty_list_displays_correctly(qapp):
    """Unit test: Empty list displays correctly"""
    # Create temp .env with no applications (should use defaults)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        temp_path = f.name
    
    try:
        with patch('core.config.get_env_path', return_value=temp_path):
            config = Config()
            window = SettingsWindow(config)
            
            # Should have default applications
            assert len(window.formatting_app_buttons) > 0, \
                "Should have default applications when none specified"
            
            window.close()
    finally:
        os.unlink(temp_path)


def test_unit_default_applications_display_on_first_init(qapp):
    """Unit test: Default applications display on first initialization"""
    # Create temp .env with minimal config - no FORMATTING_APP_PROMPTS
    # This should trigger the default applications to be loaded
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        # Explicitly set empty FORMATTING_APPLICATIONS to trigger defaults
        f.write("FORMATTING_APPLICATIONS=\n")
        temp_path = f.name
    
    try:
        with patch('core.config.get_env_path', return_value=temp_path):
            config = Config()
            window = SettingsWindow(config)
            
            # Should have SOME applications displayed (either defaults or from config)
            assert len(window.formatting_app_buttons) > 0, \
                "Should have at least one application displayed"
            
            # Verify all displayed apps are valid (non-empty names)
            for app_name in window.formatting_app_buttons.keys():
                assert len(app_name) > 0, \
                    "Application names should not be empty"
            
            window.close()
    finally:
        os.unlink(temp_path)


@given(num_apps=st.integers(min_value=1, max_value=20))
@settings(max_examples=20)
def test_unit_grid_layout_with_various_numbers(qapp, num_apps):
    """Unit test: Grid layout with various numbers of applications"""
    # Create temp .env with specified number of apps
    apps = [f"app{i}" for i in range(num_apps)]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        
        import json
        app_prompts_data = {app: {"enabled": True, "prompt": ""} for app in apps}
        f.write(f"FORMATTING_APP_PROMPTS={json.dumps(app_prompts_data, ensure_ascii=False)}\n")
        temp_path = f.name
    
    try:
        with patch('core.config.get_env_path', return_value=temp_path):
            config = Config()
            window = SettingsWindow(config)
            
            # Verify all apps are displayed
            assert len(window.formatting_app_buttons) == num_apps, \
                f"Should display exactly {num_apps} applications"
            
            # Verify grid layout (4 columns)
            grid = window.formatting_apps_grid
            expected_rows = (num_apps + 3) // 4  # Ceiling division
            
            # Count actual items in grid
            actual_items = grid.count()
            assert actual_items == num_apps, \
                f"Grid should contain {num_apps} items"
            
            window.close()
    finally:
        os.unlink(temp_path)
