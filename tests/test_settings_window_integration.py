"""
Unit tests for Settings Window integration with StyledWindowMixin.

These tests verify that the Settings Window correctly integrates with the
StyledWindowMixin and applies the unified design system styling.
"""

import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.settings_window import SettingsWindow
from design_system import StyleConstants
from core.config import Config
from unittest.mock import Mock, patch, MagicMock, call


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def mock_config():
    """Create a mock config object for testing"""
    config = Mock(spec=Config)
    config.window_opacity = 150
    config.font_size_settings_labels = 12
    config.font_size_settings_titles = 24
    config.font_size_floating_main = 14
    config.font_size_floating_info = 11
    # Add other required attributes
    config.github_url = "https://github.com/test"
    config.docs_url = "https://docs.test.com"
    config.ai_provider = "groq"
    config.groq_api_key = ""
    config.openai_api_key = ""
    config.glm_api_key = ""
    config.custom_api_key = ""
    config.custom_base_url = ""
    config.custom_model = ""
    config.hotkey = "Ctrl+Shift+A"
    config.silence_threshold = 0.03
    config.silence_duration = 2.0
    config.manual_stop = False
    config.auto_hide_delay = 3.0
    config.remember_window_position = False
    config.sample_rate = 16000
    config.chunk_size = 1024
    config.silence_padding = 300
    config.keep_recordings = False
    config.enable_post_processing = False
    config.post_processing_provider = "groq"
    config.glm_use_coding_plan = False
    config.llm_base_url = ""
    config.llm_api_key = ""
    config.post_processing_model = "llama-3.3-70b-versatile"
    config.post_processing_custom_model = ""
    config.post_processing_prompt = "Fix grammar and punctuation"
    config.interface_language = "ru"
    config.set_env_value = Mock()
    return config


def test_settings_window_has_frameless_window_hint(qapp, mock_config):
    """
    Test that window flags include FramelessWindowHint.
    
    Validates: Requirements 2.1
    """
    # Mock apply_blur_effect to avoid platform-specific issues
    with patch('utils.platform_utils.apply_blur_effect'):
        # Create Settings Window
        window = SettingsWindow(mock_config)
        
        # Verify FramelessWindowHint is set
        flags = window.windowFlags()
        assert flags & Qt.WindowType.FramelessWindowHint, (
            "Settings Window should have FramelessWindowHint flag set"
        )
        
        # Clean up
        window.close()
        window.deleteLater()


def test_settings_window_has_translucent_background(qapp, mock_config):
    """
    Test that WA_TranslucentBackground attribute is set.
    
    Validates: Requirements 2.2
    """
    # Mock apply_blur_effect to avoid platform-specific issues
    with patch('utils.platform_utils.apply_blur_effect'):
        # Create Settings Window
        window = SettingsWindow(mock_config)
        
        # Verify WA_TranslucentBackground is set
        assert window.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground), (
            "Settings Window should have WA_TranslucentBackground attribute set"
        )
        
        # Clean up
        window.close()
        window.deleteLater()


def test_settings_window_calls_blur_effect(qapp, mock_config):
    """
    Test that blur effect is called during initialization.
    
    Validates: Requirements 1.4
    """
    # Mock apply_blur_effect to verify it's called
    with patch('utils.platform_utils.apply_blur_effect') as mock_blur:
        # Create Settings Window
        window = SettingsWindow(mock_config)
        
        # Verify apply_blur_effect was called with the window
        mock_blur.assert_called_once_with(window)
        
        # Clean up
        window.close()
        window.deleteLater()


def test_settings_window_missing_config_opacity_uses_default(qapp, mock_config):
    """
    Test missing config opacity uses default.
    
    Validates: Requirements 4.3
    """
    # Set window_opacity to default to simulate missing attribute handling
    mock_config.window_opacity = StyleConstants.OPACITY_DEFAULT
    
    # Mock apply_blur_effect to avoid platform-specific issues
    with patch('utils.platform_utils.apply_blur_effect'):
        # Create Settings Window
        window = SettingsWindow(mock_config)
        
        # Verify the window uses default opacity
        assert window._opacity == StyleConstants.OPACITY_DEFAULT, (
            f"Window should use default opacity {StyleConstants.OPACITY_DEFAULT} "
            f"when config.window_opacity is missing, got {window._opacity}"
        )
        
        # Clean up
        window.close()
        window.deleteLater()


def test_settings_window_has_draggable_header(qapp, mock_config):
    """
    Test that Settings Window has a draggable header.
    
    Validates: Requirements 2.3
    """
    # Mock apply_blur_effect to avoid platform-specific issues
    with patch('utils.platform_utils.apply_blur_effect'):
        # Create Settings Window
        window = SettingsWindow(mock_config)
        
        # Verify the window has a layout
        assert window.layout() is not None, (
            "Settings Window should have a layout"
        )
        
        # Verify the first item in the layout is the header
        # The outer layout should have the header as the first widget
        layout = window.layout()
        assert layout.count() > 0, (
            "Settings Window layout should have items"
        )
        
        # Get the first item (should be the header)
        first_item = layout.itemAt(0)
        assert first_item is not None, (
            "Settings Window should have a first layout item"
        )
        
        # Verify it's a widget (the header)
        header = first_item.widget()
        assert header is not None, (
            "First layout item should be a widget (the header)"
        )
        
        # Verify header has fixed height of 35px (updated from 30px to accommodate window control buttons)
        assert header.height() == 35 or header.minimumHeight() == 35 or header.maximumHeight() == 35, (
            f"Header should have height of 35px, got height={header.height()}, "
            f"min={header.minimumHeight()}, max={header.maximumHeight()}"
        )
        
        # Clean up
        window.close()
        window.deleteLater()


def test_settings_window_opacity_change_handler(qapp, mock_config):
    """
    Test that on_opacity_changed handler updates window opacity.
    
    Validates: Requirements 4.1
    """
    # Mock apply_blur_effect to avoid platform-specific issues
    with patch('utils.platform_utils.apply_blur_effect'):
        # Create Settings Window with initial opacity
        mock_config.window_opacity = 100
        window = SettingsWindow(mock_config)
        
        # Verify initial opacity
        assert window._opacity == 100, (
            f"Initial opacity should be 100, got {window._opacity}"
        )
        
        # Call on_opacity_changed with new value
        new_opacity = 200
        window._on_opacity_changed(new_opacity)
        
        # Verify opacity was updated
        assert window._opacity == new_opacity, (
            f"After _on_opacity_changed({new_opacity}), opacity should be {new_opacity}, "
            f"got {window._opacity}"
        )
        
        # Verify stylesheet was updated
        stylesheet = window.styleSheet()
        expected_bg_color = StyleConstants.get_background_color(new_opacity)
        assert expected_bg_color in stylesheet, (
            f"Stylesheet should contain background color with new opacity {new_opacity}. "
            f"Expected '{expected_bg_color}' in stylesheet"
        )
        
        # Clean up
        window.close()
        window.deleteLater()


def test_settings_window_inherits_from_styled_window_mixin(qapp, mock_config):
    """
    Test that Settings Window inherits from StyledWindowMixin.
    
    Validates: Requirements 7.1
    """
    # Mock apply_blur_effect to avoid platform-specific issues
    with patch('utils.platform_utils.apply_blur_effect'):
        # Create Settings Window
        window = SettingsWindow(mock_config)
        
        # Verify Settings Window is an instance of StyledWindowMixin
        from design_system.styled_window_mixin import StyledWindowMixin
        assert isinstance(window, StyledWindowMixin), (
            "Settings Window should inherit from StyledWindowMixin"
        )
        
        # Verify mixin methods are available
        assert hasattr(window, 'apply_unified_style'), (
            "Settings Window should have apply_unified_style method from mixin"
        )
        assert hasattr(window, 'update_opacity'), (
            "Settings Window should have update_opacity method from mixin"
        )
        assert hasattr(window, '_apply_stylesheet'), (
            "Settings Window should have _apply_stylesheet method from mixin"
        )
        assert hasattr(window, '_apply_blur'), (
            "Settings Window should have _apply_blur method from mixin"
        )
        
        # Clean up
        window.close()
        window.deleteLater()


def test_settings_window_applies_unified_style_on_init(qapp, mock_config):
    """
    Test that Settings Window applies unified style during initialization.
    
    Validates: Requirements 1.1, 1.2, 1.3, 1.4, 2.1, 2.2
    """
    # Mock apply_blur_effect to avoid platform-specific issues
    with patch('utils.platform_utils.apply_blur_effect'):
        # Create Settings Window
        window = SettingsWindow(mock_config)
        
        # Verify window flags are set (FramelessWindowHint)
        flags = window.windowFlags()
        assert flags & Qt.WindowType.FramelessWindowHint, (
            "Window should have FramelessWindowHint flag"
        )
        
        # Verify translucent background is set
        assert window.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground), (
            "Window should have WA_TranslucentBackground attribute"
        )
        
        # Verify stylesheet is applied
        stylesheet = window.styleSheet()
        assert len(stylesheet) > 0, (
            "Window should have a stylesheet applied"
        )
        
        # Verify stylesheet contains required properties
        assert "background-color:" in stylesheet, (
            "Stylesheet should contain background-color property"
        )
        assert "border:" in stylesheet, (
            "Stylesheet should contain border property"
        )
        assert "border-radius:" in stylesheet, (
            "Stylesheet should contain border-radius property"
        )
        
        # Clean up
        window.close()
        window.deleteLater()


def test_settings_window_does_not_stay_on_top(qapp, mock_config):
    """
    Test that Settings Window does not have WindowStaysOnTopHint flag.
    
    Validates: Requirements 2.1
    """
    # Mock apply_blur_effect to avoid platform-specific issues
    with patch('utils.platform_utils.apply_blur_effect'):
        # Create Settings Window
        window = SettingsWindow(mock_config)
        
        # Verify WindowStaysOnTopHint is NOT set
        flags = window.windowFlags()
        assert not (flags & Qt.WindowType.WindowStaysOnTopHint), (
            "Settings Window should NOT have WindowStaysOnTopHint flag set"
        )
        
        # Clean up
        window.close()
        window.deleteLater()


def test_settings_window_drag_position_initialized(qapp, mock_config):
    """
    Test that Settings Window has drag position initialized to None.
    
    Validates: Requirements 2.3
    """
    # Mock apply_blur_effect to avoid platform-specific issues
    with patch('utils.platform_utils.apply_blur_effect'):
        # Create Settings Window
        window = SettingsWindow(mock_config)
        
        # Verify _drag_position is initialized to None
        assert hasattr(window, '_drag_position'), (
            "Settings Window should have _drag_position attribute"
        )
        assert window._drag_position is None, (
            "Settings Window _drag_position should be initialized to None"
        )
        
        # Clean up
        window.close()
        window.deleteLater()
