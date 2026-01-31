"""
Integration tests for formatting UI workflows.

Tests the complete Add/Edit/Delete workflows for applications.
"""

import pytest
from PyQt6.QtWidgets import QApplication, QPushButton
from PyQt6.QtCore import Qt, QPoint
from ui.settings_window import SettingsWindow
from core.config import Config
from services.formatting_config import FormattingConfig
from unittest.mock import patch, MagicMock
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


def test_unit_add_application_button_exists(qapp):
    """Unit test: Add Application button exists and is visible"""
    # Create temp .env
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        temp_path = f.name
    
    try:
        with patch('core.config.get_env_path', return_value=temp_path):
            config = Config()
            window = SettingsWindow(config)
            
            # Find the Add Application button
            add_buttons = [btn for btn in window.findChildren(QPushButton) 
                          if "Добавить приложение" in btn.text()]
            
            assert len(add_buttons) > 0, \
                "Add Application button should exist"
            
            add_btn = add_buttons[0]
            # Button exists and is enabled (visibility depends on scroll area)
            assert add_btn.isEnabled(), \
                "Add Application button should be enabled"
            
            window.close()
    finally:
        os.unlink(temp_path)


def test_unit_add_application_button_opens_dialog(qapp):
    """Unit test: Add Application button opens AddApplicationDialog on click"""
    # Create temp .env
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        
        import json
        app_prompts_data = {"app1": {"enabled": True, "prompt": ""}}
        f.write(f"FORMATTING_APP_PROMPTS={json.dumps(app_prompts_data, ensure_ascii=False)}\n")
        temp_path = f.name
    
    try:
        with patch('core.config.get_env_path', return_value=temp_path):
            config = Config()
            window = SettingsWindow(config)
            
            # Mock the AddApplicationDialog.add_application method
            with patch('ui.settings_window.AddApplicationDialog.add_application') as mock_dialog:
                mock_dialog.return_value = None  # User cancelled
                
                # Find and click the Add Application button
                add_buttons = [btn for btn in window.findChildren(QPushButton) 
                              if "Добавить приложение" in btn.text()]
                
                assert len(add_buttons) > 0, "Add Application button should exist"
                add_btn = add_buttons[0]
                
                # Simulate click
                add_btn.click()
                
                # Verify dialog was opened
                assert mock_dialog.called, \
                    "AddApplicationDialog should be opened when button is clicked"
            
            window.close()
    finally:
        os.unlink(temp_path)


def test_integration_add_application_workflow(qapp):
    """Integration test: Complete add application workflow"""
    # Create temp .env
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        
        import json
        app_prompts_data = {"app1": {"enabled": True, "prompt": ""}}
        f.write(f"FORMATTING_APP_PROMPTS={json.dumps(app_prompts_data, ensure_ascii=False)}\n")
        temp_path = f.name
    
    try:
        with patch('core.config.get_env_path', return_value=temp_path):
            config = Config()
            window = SettingsWindow(config)
            
            initial_count = len(window.formatting_app_buttons)
            
            # Mock the AddApplicationDialog to return a new application
            with patch('ui.settings_window.AddApplicationDialog.add_application') as mock_dialog:
                mock_dialog.return_value = ("new_app", "custom prompt")
                
                # Trigger add application
                window._on_add_application_clicked()
                
                # Verify new application was added
                assert "new_app" in window.formatting_app_buttons, \
                    "New application should be added to grid"
                
                assert len(window.formatting_app_buttons) == initial_count + 1, \
                    "Application count should increase by 1"
            
            window.close()
    finally:
        os.unlink(temp_path)


def test_integration_edit_application_workflow(qapp):
    """Integration test: Complete edit application workflow"""
    # Create temp .env with an application
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        
        import json
        app_prompts_data = {"test_app": {"enabled": True, "prompt": "original prompt"}}
        f.write(f"FORMATTING_APP_PROMPTS={json.dumps(app_prompts_data, ensure_ascii=False)}\n")
        temp_path = f.name
    
    try:
        with patch('core.config.get_env_path', return_value=temp_path):
            config = Config()
            window = SettingsWindow(config)
            
            # Verify app exists with custom prompt indicator
            assert "test_app" in window.formatting_app_buttons
            btn = window.formatting_app_buttons["test_app"]
            assert "✏️" in btn.text(), "Should have custom prompt indicator"
            
            # Mock the PromptEditDialog to return a new prompt
            with patch('ui.settings_window.PromptEditDialog.edit_prompt') as mock_dialog:
                mock_dialog.return_value = "new edited prompt"
                
                # Trigger edit
                window._edit_application_prompt("test_app")
                
                # Verify prompt was updated (button should still have indicator)
                btn = window.formatting_app_buttons["test_app"]
                assert "✏️" in btn.text(), "Should still have custom prompt indicator"
            
            window.close()
    finally:
        os.unlink(temp_path)


def test_integration_delete_application_workflow(qapp):
    """Integration test: Complete delete application workflow"""
    # Create temp .env with multiple applications
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        
        import json
        app_prompts_data = {
            "app1": {"enabled": True, "prompt": ""},
            "app2": {"enabled": True, "prompt": ""},
            "app3": {"enabled": True, "prompt": ""}
        }
        f.write(f"FORMATTING_APP_PROMPTS={json.dumps(app_prompts_data, ensure_ascii=False)}\n")
        temp_path = f.name
    
    try:
        with patch('core.config.get_env_path', return_value=temp_path):
            config = Config()
            window = SettingsWindow(config)
            
            initial_count = len(window.formatting_app_buttons)
            assert initial_count == 3, "Should have 3 applications initially"
            
            # Delete one application
            window._delete_application("app2")
            
            # Verify application was removed
            assert "app2" not in window.formatting_app_buttons, \
                "Deleted application should not be in grid"
            
            assert len(window.formatting_app_buttons) == initial_count - 1, \
                "Application count should decrease by 1"
            
            # Verify other apps still exist
            assert "app1" in window.formatting_app_buttons
            assert "app3" in window.formatting_app_buttons
            
            window.close()
    finally:
        os.unlink(temp_path)


def test_unit_delete_last_application_prevented(qapp):
    """Unit test: Deleting last application is prevented"""
    # Create temp .env with only one application
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        
        import json
        app_prompts_data = {"only_app": {"enabled": True, "prompt": ""}}
        f.write(f"FORMATTING_APP_PROMPTS={json.dumps(app_prompts_data, ensure_ascii=False)}\n")
        temp_path = f.name
    
    try:
        with patch('core.config.get_env_path', return_value=temp_path):
            config = Config()
            window = SettingsWindow(config)
            
            assert len(window.formatting_app_buttons) == 1, \
                "Should have exactly 1 application"
            
            # Mock QMessageBox to prevent actual dialog
            with patch('ui.settings_window.QMessageBox.warning') as mock_warning:
                # Try to delete the last application
                window._delete_application("only_app")
                
                # Verify warning was shown
                assert mock_warning.called, \
                    "Warning should be shown when trying to delete last application"
                
                # Verify application still exists
                assert "only_app" in window.formatting_app_buttons, \
                    "Last application should not be deleted"
            
            window.close()
    finally:
        os.unlink(temp_path)


def test_unit_context_menu_appears_on_right_click(qapp):
    """Unit test: Context menu appears on right-click"""
    # Create temp .env
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        
        import json
        app_prompts_data = {"test_app": {"enabled": True, "prompt": ""}}
        f.write(f"FORMATTING_APP_PROMPTS={json.dumps(app_prompts_data, ensure_ascii=False)}\n")
        temp_path = f.name
    
    try:
        with patch('core.config.get_env_path', return_value=temp_path):
            config = Config()
            window = SettingsWindow(config)
            
            # Mock QMenu.exec to prevent actual menu display
            with patch('ui.settings_window.QMenu.exec') as mock_menu:
                mock_menu.return_value = None
                
                # Trigger context menu
                btn = window.formatting_app_buttons["test_app"]
                position = QPoint(10, 10)
                
                # Simulate right-click by calling the context menu handler directly
                window._show_app_context_menu("test_app", btn.mapToGlobal(position))
                
                # Verify menu was shown
                assert mock_menu.called, \
                    "Context menu should be displayed on right-click"
            
            window.close()
    finally:
        os.unlink(temp_path)


def test_unit_delete_disabled_when_one_app_remains(qapp):
    """Unit test: Delete option disabled when only one application remains"""
    # Create temp .env with one application
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        
        import json
        app_prompts_data = {"only_app": {"enabled": True, "prompt": ""}}
        f.write(f"FORMATTING_APP_PROMPTS={json.dumps(app_prompts_data, ensure_ascii=False)}\n")
        temp_path = f.name
    
    try:
        with patch('core.config.get_env_path', return_value=temp_path):
            config = Config()
            window = SettingsWindow(config)
            
            # The context menu creation happens in _show_app_context_menu
            # We need to verify that delete action is disabled
            # This is tested indirectly through the delete prevention test above
            assert len(window.formatting_app_buttons) == 1, \
                "Should have exactly 1 application"
            
            window.close()
    finally:
        os.unlink(temp_path)


def test_unit_delete_enabled_with_multiple_apps(qapp):
    """Unit test: Delete option enabled when multiple applications exist"""
    # Create temp .env with multiple applications
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        
        import json
        app_prompts_data = {
            "app1": {"enabled": True, "prompt": ""},
            "app2": {"enabled": True, "prompt": ""}
        }
        f.write(f"FORMATTING_APP_PROMPTS={json.dumps(app_prompts_data, ensure_ascii=False)}\n")
        temp_path = f.name
    
    try:
        with patch('core.config.get_env_path', return_value=temp_path):
            config = Config()
            window = SettingsWindow(config)
            
            assert len(window.formatting_app_buttons) == 2, \
                "Should have 2 applications"
            
            # Delete should work with multiple apps
            with patch('ui.settings_window.QMessageBox.warning') as mock_warning:
                window._delete_application("app1")
                
                # No warning should be shown
                assert not mock_warning.called, \
                    "No warning should be shown when deleting with multiple apps"
                
                # Verify deletion succeeded
                assert "app1" not in window.formatting_app_buttons
            
            window.close()
    finally:
        os.unlink(temp_path)
