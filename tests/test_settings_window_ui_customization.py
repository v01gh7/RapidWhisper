"""
Unit tests for SettingsWindow UI Customization page.

Tests the UI Customization settings page functionality including:
- Page creation and integration
- Slider ranges and default values
- Reset to defaults functionality
- Translation key usage
"""

import pytest
from PyQt6.QtWidgets import QApplication, QSlider, QSpinBox, QPushButton, QLabel
from PyQt6.QtCore import Qt
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.settings_window import SettingsWindow
from core.config import Config


@pytest.fixture
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def temp_env_file(tmp_path):
    """Create a temporary .env file for testing."""
    env_file = tmp_path / ".env"
    env_file.write_text("""
AI_PROVIDER=groq
GROQ_API_KEY=test_key
HOTKEY=ctrl+space
WINDOW_OPACITY=150
FONT_SIZE_FLOATING_MAIN=16
FONT_SIZE_FLOATING_INFO=10
FONT_SIZE_SETTINGS_LABELS=12
FONT_SIZE_SETTINGS_TITLES=24
""")
    return env_file


@pytest.fixture
def config(temp_env_file, monkeypatch):
    """Create Config instance with temporary .env file."""
    monkeypatch.setenv("RAPIDWHISPER_ENV_PATH", str(temp_env_file))
    
    # Mock get_env_path to return our temp file
    with patch('core.config.get_env_path', return_value=temp_env_file):
        config = Config()
        yield config


@pytest.fixture
def settings_window(qapp, config):
    """Create SettingsWindow instance for testing."""
    window = SettingsWindow(config)
    yield window
    window.close()


class TestUICustomizationPageCreation:
    """Test UI Customization page creation and integration."""
    
    def test_page_exists_in_sidebar(self, settings_window):
        """Test that UI Customization page is added to sidebar."""
        # Check sidebar has correct number of items (8 pages including UI Customization)
        assert settings_window.sidebar.count() == 8
        
        # Find UI Customization item
        ui_customization_found = False
        for i in range(settings_window.sidebar.count()):
            item = settings_window.sidebar.item(i)
            if "🎨" in item.text():
                ui_customization_found = True
                break
        
        assert ui_customization_found, "UI Customization page not found in sidebar"
    
    def test_page_exists_in_content_stack(self, settings_window):
        """Test that UI Customization page is added to content stack."""
        # Should have 8 pages in content stack
        assert settings_window.content_stack.count() == 8
    
    def test_page_has_correct_title(self, settings_window):
        """Test that UI Customization page has correct translated title."""
        # Navigate to UI Customization page (index 5)
        settings_window.sidebar.setCurrentRow(5)
        
        # Get current page widget
        current_page = settings_window.content_stack.currentWidget()
        
        # Find title label (should have objectName "pageTitle")
        title_labels = current_page.findChildren(QLabel, "pageTitle")
        assert len(title_labels) > 0, "Page title not found"
        
        # Check title text contains expected translation key content
        title_text = title_labels[0].text()
        assert len(title_text) > 0, "Page title is empty"


class TestOpacityControls:
    """Test opacity slider and controls."""
    
    def test_opacity_slider_exists(self, settings_window):
        """Test that opacity slider exists."""
        assert hasattr(settings_window, 'opacity_slider')
        assert isinstance(settings_window.opacity_slider, QSlider)
    
    def test_opacity_slider_range(self, settings_window):
        """Test that opacity slider has correct range (50-255)."""
        assert settings_window.opacity_slider.minimum() == 50
        assert settings_window.opacity_slider.maximum() == 255
    
    def test_opacity_slider_default_value(self, settings_window):
        """Test that opacity slider loads default value from config."""
        # Default value should be 150
        assert settings_window.opacity_slider.value() == 150
    
    def test_opacity_value_label_exists(self, settings_window):
        """Test that opacity value label exists."""
        assert hasattr(settings_window, 'opacity_value_label')
        assert isinstance(settings_window.opacity_value_label, QLabel)
    
    def test_opacity_value_label_updates(self, settings_window):
        """Test that opacity value label updates when slider changes."""
        # Change slider value
        settings_window.opacity_slider.setValue(200)
        
        # Check label updated
        assert settings_window.opacity_value_label.text() == "200"
    
    def test_opacity_change_handler_connected(self, settings_window):
        """Test that opacity change handler is connected."""
        # Mock parent with set_opacity method
        mock_parent = Mock()
        mock_parent.set_opacity = Mock()
        
        with patch.object(settings_window, 'parent', return_value=mock_parent):
            # Change slider value
            settings_window.opacity_slider.setValue(180)
            
            # Handler should be called
            mock_parent.set_opacity.assert_called_with(180)


class TestFontSizeControls:
    """Test font size spinboxes."""
    
    def test_font_floating_main_exists(self, settings_window):
        """Test that floating main font spinbox exists."""
        assert hasattr(settings_window, 'font_floating_main_spin')
        assert isinstance(settings_window.font_floating_main_spin, QSpinBox)
    
    def test_font_floating_main_range(self, settings_window):
        """Test that floating main font has correct range (10-24)."""
        assert settings_window.font_floating_main_spin.minimum() == 10
        assert settings_window.font_floating_main_spin.maximum() == 24
    
    def test_font_floating_main_default(self, settings_window):
        """Test that floating main font loads default value (14)."""
        assert settings_window.font_floating_main_spin.value() == 14
    
    def test_font_floating_info_exists(self, settings_window):
        """Test that floating info font spinbox exists."""
        assert hasattr(settings_window, 'font_floating_info_spin')
        assert isinstance(settings_window.font_floating_info_spin, QSpinBox)
    
    def test_font_floating_info_range(self, settings_window):
        """Test that floating info font has correct range (8-16)."""
        assert settings_window.font_floating_info_spin.minimum() == 8
        assert settings_window.font_floating_info_spin.maximum() == 16
    
    def test_font_floating_info_default(self, settings_window):
        """Test that floating info font loads default value (11)."""
        assert settings_window.font_floating_info_spin.value() == 11
    
    def test_font_settings_labels_exists(self, settings_window):
        """Test that settings labels font spinbox exists."""
        assert hasattr(settings_window, 'font_settings_labels_spin')
        assert isinstance(settings_window.font_settings_labels_spin, QSpinBox)
    
    def test_font_settings_labels_range(self, settings_window):
        """Test that settings labels font has correct range (10-16)."""
        assert settings_window.font_settings_labels_spin.minimum() == 10
        assert settings_window.font_settings_labels_spin.maximum() == 16
    
    def test_font_settings_labels_default(self, settings_window):
        """Test that settings labels font loads default value (12)."""
        assert settings_window.font_settings_labels_spin.value() == 12
    
    def test_font_settings_titles_exists(self, settings_window):
        """Test that settings titles font spinbox exists."""
        assert hasattr(settings_window, 'font_settings_titles_spin')
        assert isinstance(settings_window.font_settings_titles_spin, QSpinBox)
    
    def test_font_settings_titles_range(self, settings_window):
        """Test that settings titles font has correct range (16-32)."""
        assert settings_window.font_settings_titles_spin.minimum() == 16
        assert settings_window.font_settings_titles_spin.maximum() == 32
    
    def test_font_settings_titles_default(self, settings_window):
        """Test that settings titles font loads default value (24)."""
        assert settings_window.font_settings_titles_spin.value() == 24


class TestResetToDefaults:
    """Test reset to defaults functionality."""
    
    def test_reset_button_exists(self, settings_window):
        """Test that reset button exists."""
        # Navigate to UI Customization page
        settings_window.sidebar.setCurrentRow(5)
        
        # Find reset button
        current_page = settings_window.content_stack.currentWidget()
        reset_buttons = [btn for btn in current_page.findChildren(QPushButton) 
                        if "reset" in btn.text().lower() or "сброс" in btn.text().lower()]
        
        assert len(reset_buttons) > 0, "Reset button not found"
    
    def test_reset_restores_opacity_default(self, settings_window):
        """Test that reset restores opacity to default (150)."""
        # Change opacity
        settings_window.opacity_slider.setValue(200)
        assert settings_window.opacity_slider.value() == 200
        
        # Reset
        settings_window._reset_ui_defaults()
        
        # Check restored
        assert settings_window.opacity_slider.value() == 150
    
    def test_reset_restores_font_floating_main_default(self, settings_window):
        """Test that reset restores floating main font to default (14)."""
        # Change value
        settings_window.font_floating_main_spin.setValue(20)
        assert settings_window.font_floating_main_spin.value() == 20
        
        # Reset
        settings_window._reset_ui_defaults()
        
        # Check restored
        assert settings_window.font_floating_main_spin.value() == 14
    
    def test_reset_restores_font_floating_info_default(self, settings_window):
        """Test that reset restores floating info font to default (11)."""
        # Change value
        settings_window.font_floating_info_spin.setValue(14)
        
        # Reset
        settings_window._reset_ui_defaults()
        
        # Check restored
        assert settings_window.font_floating_info_spin.value() == 11
    
    def test_reset_restores_font_settings_labels_default(self, settings_window):
        """Test that reset restores settings labels font to default (12)."""
        # Change value
        settings_window.font_settings_labels_spin.setValue(14)
        
        # Reset
        settings_window._reset_ui_defaults()
        
        # Check restored
        assert settings_window.font_settings_labels_spin.value() == 12
    
    def test_reset_restores_font_settings_titles_default(self, settings_window):
        """Test that reset restores settings titles font to default (24)."""
        # Change value
        settings_window.font_settings_titles_spin.setValue(28)
        
        # Reset
        settings_window._reset_ui_defaults()
        
        # Check restored
        assert settings_window.font_settings_titles_spin.value() == 24
    
    def test_reset_writes_to_env(self, settings_window, temp_env_file):
        """Test that reset writes default values to .env file."""
        # Mock config.set_env_value
        settings_window.config.set_env_value = Mock()
        
        # Reset
        settings_window._reset_ui_defaults()
        
        # Check set_env_value was called with defaults
        calls = settings_window.config.set_env_value.call_args_list
        
        # Should have 5 calls (one for each setting)
        assert len(calls) == 5
        
        # Check each call
        call_dict = {call[0][0]: call[0][1] for call in calls}
        assert call_dict["WINDOW_OPACITY"] == "150"
        assert call_dict["FONT_SIZE_FLOATING_MAIN"] == "14"
        assert call_dict["FONT_SIZE_FLOATING_INFO"] == "11"
        assert call_dict["FONT_SIZE_SETTINGS_LABELS"] == "12"
        assert call_dict["FONT_SIZE_SETTINGS_TITLES"] == "24"
    
    def test_reset_triggers_live_preview(self, settings_window):
        """Test that reset triggers live preview for opacity."""
        # Mock parent with set_opacity method
        mock_parent = Mock()
        mock_parent.set_opacity = Mock()
        
        with patch.object(settings_window, 'parent', return_value=mock_parent):
            # Reset
            settings_window._reset_ui_defaults()
            
            # Check set_opacity was called with default value
            mock_parent.set_opacity.assert_called_with(150)


class TestSaveSettings:
    """Test that UI customization settings are saved correctly."""
    
    def test_save_includes_opacity(self, settings_window, temp_env_file):
        """Test that save includes opacity value."""
        # Change opacity
        settings_window.opacity_slider.setValue(180)
        
        # Save settings
        with patch('core.config.get_env_path', return_value=temp_env_file):
            settings_window._save_settings()
        
        # Read .env file with UTF-8 encoding
        env_content = temp_env_file.read_text(encoding='utf-8')
        
        # Check opacity is saved
        assert "WINDOW_OPACITY=180" in env_content
    
    def test_save_includes_all_font_sizes(self, settings_window, temp_env_file):
        """Test that save includes all font size values."""
        # Change font sizes
        settings_window.font_floating_main_spin.setValue(18)
        settings_window.font_floating_info_spin.setValue(12)
        settings_window.font_settings_labels_spin.setValue(14)
        settings_window.font_settings_titles_spin.setValue(28)
        
        # Save settings
        with patch('core.config.get_env_path', return_value=temp_env_file):
            settings_window._save_settings()
        
        # Read .env file with UTF-8 encoding
        env_content = temp_env_file.read_text(encoding='utf-8')
        
        # Check all font sizes are saved
        assert "FONT_SIZE_FLOATING_MAIN=18" in env_content
        assert "FONT_SIZE_FLOATING_INFO=12" in env_content
        assert "FONT_SIZE_SETTINGS_LABELS=14" in env_content
        assert "FONT_SIZE_SETTINGS_TITLES=28" in env_content


class TestTranslationKeys:
    """Test that all translation keys are used correctly."""
    
    def test_page_title_uses_translation(self, settings_window):
        """Test that page title uses translation key."""
        # Navigate to UI Customization page
        settings_window.sidebar.setCurrentRow(5)
        
        # Get current page
        current_page = settings_window.content_stack.currentWidget()
        
        # Find title label
        title_labels = current_page.findChildren(QLabel, "pageTitle")
        assert len(title_labels) > 0
        
        # Title should not be empty (translation loaded)
        assert len(title_labels[0].text()) > 0
    
    def test_sidebar_item_uses_translation(self, settings_window):
        """Test that sidebar item uses translation key."""
        # Find UI Customization item in sidebar
        ui_item = None
        for i in range(settings_window.sidebar.count()):
            item = settings_window.sidebar.item(i)
            if "🎨" in item.text():
                ui_item = item
                break
        
        assert ui_item is not None
        # Should have text beyond just the emoji
        assert len(ui_item.text()) > 2



class TestSettingsWindowFontSizes:
    """Unit tests for SettingsWindow font size integration"""
    
    def test_font_sizes_read_from_config_on_initialization(self, qapp, temp_env_file):
        """Test that font sizes are read from Config on initialization"""
        from unittest.mock import patch
        from pathlib import Path
        
        # Create config with custom font sizes
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write('FONT_SIZE_SETTINGS_LABELS=14\n')
            f.write('FONT_SIZE_SETTINGS_TITLES=28\n')
        
        with patch('core.config.get_env_path', return_value=Path(temp_env_file)):
            config = Config.load_from_env()
            window = SettingsWindow(config)
            
            # Check that font sizes are applied in stylesheet
            stylesheet = window.styleSheet()
            assert 'font-size: 14px' in stylesheet, \
                "Label font size should be 14px"
            assert 'font-size: 28px' in stylesheet, \
                "Title font size should be 28px"
            
            window.close()
    
    def test_default_font_sizes_when_not_in_config(self, qapp, temp_env_file):
        """Test that default font sizes are used when not in config"""
        from unittest.mock import patch
        from pathlib import Path
        
        # Create empty config
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write('')
        
        with patch('core.config.get_env_path', return_value=Path(temp_env_file)):
            config = Config.load_from_env()
            window = SettingsWindow(config)
            
            # Check that default font sizes from Config are applied
            stylesheet = window.styleSheet()
            default_label_size = config.font_size_settings_labels
            default_title_size = config.font_size_settings_titles
            
            assert f'font-size: {default_label_size}px' in stylesheet, \
                f"Default label font size should be {default_label_size}px"
            assert f'font-size: {default_title_size}px' in stylesheet, \
                f"Default title font size should be {default_title_size}px"
            
            window.close()
    
    def test_font_sizes_applied_to_labels(self, qapp, temp_env_file):
        """Test that font sizes are applied to all labels"""
        from unittest.mock import patch
        from pathlib import Path
        
        # Create config with custom font sizes
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write('FONT_SIZE_SETTINGS_LABELS=15\n')
        
        with patch('core.config.get_env_path', return_value=Path(temp_env_file)):
            config = Config.load_from_env()
            window = SettingsWindow(config)
            
            # Stylesheet should contain the custom label font size
            stylesheet = window.styleSheet()
            assert 'QLabel' in stylesheet
            assert 'font-size: 15px' in stylesheet
            
            window.close()
    
    def test_font_sizes_applied_to_titles(self, qapp, temp_env_file):
        """Test that font sizes are applied to page titles"""
        from unittest.mock import patch
        from pathlib import Path
        
        # Create config with custom title font size
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write('FONT_SIZE_SETTINGS_TITLES=30\n')
        
        with patch('core.config.get_env_path', return_value=Path(temp_env_file)):
            config = Config.load_from_env()
            window = SettingsWindow(config)
            
            # Stylesheet should contain the custom title font size
            stylesheet = window.styleSheet()
            assert 'QLabel#pageTitle' in stylesheet
            assert 'font-size: 30px' in stylesheet
            
            window.close()
    
    def test_font_sizes_persist_across_window_close_reopen(self, qapp, temp_env_file):
        """Test that font sizes persist across window close/reopen"""
        from unittest.mock import patch
        from pathlib import Path
        
        # Create config with custom font sizes
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write('FONT_SIZE_SETTINGS_LABELS=13\n')
            f.write('FONT_SIZE_SETTINGS_TITLES=26\n')
        
        with patch('core.config.get_env_path', return_value=Path(temp_env_file)):
            # First open
            config1 = Config.load_from_env()
            window1 = SettingsWindow(config1)
            stylesheet1 = window1.styleSheet()
            window1.close()
            
            # Second open
            config2 = Config.load_from_env()
            window2 = SettingsWindow(config2)
            stylesheet2 = window2.styleSheet()
            
            # Font sizes should be the same
            assert 'font-size: 13px' in stylesheet1
            assert 'font-size: 13px' in stylesheet2
            assert 'font-size: 26px' in stylesheet1
            assert 'font-size: 26px' in stylesheet2
            
            window2.close()
    
    def test_font_size_boundary_values(self, qapp, temp_env_file):
        """Test font sizes with boundary values (min and max)"""
        from unittest.mock import patch
        from pathlib import Path
        
        # Test minimum font sizes
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write('FONT_SIZE_SETTINGS_LABELS=10\n')
            f.write('FONT_SIZE_SETTINGS_TITLES=16\n')
        
        with patch('core.config.get_env_path', return_value=Path(temp_env_file)):
            config_min = Config.load_from_env()
            window_min = SettingsWindow(config_min)
            stylesheet_min = window_min.styleSheet()
            assert 'font-size: 10px' in stylesheet_min
            assert 'font-size: 16px' in stylesheet_min
            window_min.close()
        
        # Test maximum font sizes
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write('FONT_SIZE_SETTINGS_LABELS=16\n')
            f.write('FONT_SIZE_SETTINGS_TITLES=32\n')
        
        with patch('core.config.get_env_path', return_value=Path(temp_env_file)):
            config_max = Config.load_from_env()
            window_max = SettingsWindow(config_max)
            stylesheet_max = window_max.styleSheet()
            assert 'font-size: 16px' in stylesheet_max
            assert 'font-size: 32px' in stylesheet_max
            window_max.close()
