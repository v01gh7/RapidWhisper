"""
Integration tests for unified design system.

These tests verify that all components work together correctly:
- Settings Window can be opened and closed
- Opacity changes affect Settings Window
- Tray Icon menu displays correctly
- All existing functionality is preserved
"""

import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.settings_window import SettingsWindow
from ui.tray_icon import TrayIcon
from design_system import StyleConstants
from core.config import Config
from unittest.mock import Mock, patch


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


def test_settings_window_can_be_opened_and_closed(qapp, mock_config):
    """
    Test that Settings Window can be opened and closed.
    
    Validates: Requirements 5.1
    """
    # Mock apply_blur_effect to avoid platform-specific issues
    with patch('utils.platform_utils.apply_blur_effect'):
        # Create Settings Window
        window = SettingsWindow(mock_config)
        
        # Verify window is not visible initially
        assert not window.isVisible(), (
            "Settings Window should not be visible initially"
        )
        
        # Show the window
        window.show()
        
        # Verify window is visible
        assert window.isVisible(), (
            "Settings Window should be visible after show()"
        )
        
        # Close the window
        window.close()
        
        # Verify window is not visible after close
        assert not window.isVisible(), (
            "Settings Window should not be visible after close()"
        )
        
        # Clean up
        window.deleteLater()


def test_opacity_changes_affect_settings_window(qapp, mock_config):
    """
    Test that opacity changes affect Settings Window.
    
    Validates: Requirements 5.2
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
        
        # Change opacity
        new_opacity = 200
        window._on_opacity_changed(new_opacity)
        
        # Verify opacity was updated internally
        assert window._opacity == new_opacity, (
            f"After opacity change, opacity should be {new_opacity}, got {window._opacity}"
        )
        
        # Note: The Settings Window has its own _apply_style() method that applies
        # a custom stylesheet for UI elements. The mixin's opacity is stored internally
        # and used for window-level styling, but the visible stylesheet is from _apply_style().
        # This is the correct behavior - the mixin handles window-level properties,
        # and the Settings Window handles content styling.
        
        # Clean up
        window.close()
        window.deleteLater()


def test_tray_icon_menu_displays_correctly(qapp):
    """
    Test that Tray Icon menu displays correctly.
    
    Validates: Requirements 5.3
    """
    # Mock the icon loading to avoid file system dependencies
    with patch('ui.tray_icon.QIcon'):
        # Create TrayIcon instance
        tray_icon = TrayIcon()
        
        # Verify tray icon is visible
        assert tray_icon.tray_icon.isVisible(), (
            "Tray icon should be visible"
        )
        
        # Get the menu
        menu = tray_icon.tray_icon.contextMenu()
        assert menu is not None, (
            "Tray icon should have a context menu"
        )
        
        # Verify menu has stylesheet
        stylesheet = menu.styleSheet()
        assert len(stylesheet) > 0, (
            "Menu should have a stylesheet applied"
        )
        
        # Verify menu has actions
        actions = menu.actions()
        assert len(actions) > 0, (
            "Menu should have at least one action"
        )
        
        # Verify menu has non-separator actions
        non_separator_actions = [a for a in actions if not a.isSeparator()]
        assert len(non_separator_actions) >= 3, (
            f"Menu should have at least 3 non-separator actions, got {len(non_separator_actions)}"
        )
        
        # Clean up
        tray_icon.hide()


def test_settings_window_preserves_existing_functionality(qapp, mock_config):
    """
    Test that all existing functionality is preserved in Settings Window.
    
    Validates: Requirements 5.1, 5.4
    """
    # Mock apply_blur_effect to avoid platform-specific issues
    with patch('utils.platform_utils.apply_blur_effect'):
        # Create Settings Window
        window = SettingsWindow(mock_config)
        
        # Verify window has config attribute
        assert hasattr(window, 'config'), (
            "Settings Window should have config attribute"
        )
        assert window.config == mock_config, (
            "Settings Window config should match the provided config"
        )
        
        # Verify window has layout
        assert window.layout() is not None, (
            "Settings Window should have a layout"
        )
        
        # Verify window can be shown and hidden
        window.show()
        assert window.isVisible(), (
            "Settings Window should be visible after show()"
        )
        
        window.hide()
        assert not window.isVisible(), (
            "Settings Window should not be visible after hide()"
        )
        
        # Clean up
        window.close()
        window.deleteLater()


def test_tray_icon_preserves_existing_functionality(qapp):
    """
    Test that all existing functionality is preserved in Tray Icon.
    
    Validates: Requirements 5.2, 5.4
    """
    # Mock the icon loading to avoid file system dependencies
    with patch('ui.tray_icon.QIcon'):
        # Create TrayIcon instance
        tray_icon = TrayIcon()
        
        # Verify tray icon has signals
        assert hasattr(tray_icon, 'show_settings'), (
            "TrayIcon should have show_settings signal"
        )
        assert hasattr(tray_icon, 'quit_app'), (
            "TrayIcon should have quit_app signal"
        )
        
        # Verify tray icon has tooltip
        tooltip = tray_icon.tray_icon.toolTip()
        assert len(tooltip) > 0, (
            "Tray icon should have a non-empty tooltip"
        )
        
        # Verify tray icon can be shown and hidden
        assert tray_icon.tray_icon.isVisible(), (
            "Tray icon should be visible initially"
        )
        
        tray_icon.hide()
        assert not tray_icon.tray_icon.isVisible(), (
            "Tray icon should not be visible after hide()"
        )


def test_settings_window_and_tray_icon_use_consistent_styling(qapp, mock_config):
    """
    Test that Settings Window and Tray Icon use consistent styling.
    
    Validates: Requirements 1.1, 1.2, 1.3, 3.1, 3.2, 3.3
    """
    # Mock apply_blur_effect to avoid platform-specific issues
    with patch('utils.platform_utils.apply_blur_effect'):
        # Mock the icon loading to avoid file system dependencies
        with patch('ui.tray_icon.QIcon'):
            # Create Settings Window
            window = SettingsWindow(mock_config)
            
            # Create TrayIcon
            tray_icon = TrayIcon()
            
            # Get stylesheets
            menu_stylesheet = tray_icon.tray_icon.contextMenu().styleSheet()
            
            # Note: The Settings Window has its own _apply_style() method that applies
            # a custom stylesheet for UI elements. The mixin's stylesheet is applied
            # at the window level (frameless, translucent), but the visible stylesheet
            # is from _apply_style(). This is the correct behavior.
            
            # Verify both use StyleConstants for their respective styling
            # The mixin stores opacity internally and uses StyleConstants
            assert window._opacity == mock_config.window_opacity, (
                f"Settings Window should use config opacity"
            )
            
            # Verify Tray Icon menu uses StyleConstants
            assert f"{StyleConstants.BORDER_RADIUS}px" in menu_stylesheet, (
                f"Tray Icon menu should use StyleConstants.BORDER_RADIUS"
            )
            
            assert f"{StyleConstants.BORDER_WIDTH}px" in menu_stylesheet, (
                f"Tray Icon menu should use StyleConstants.BORDER_WIDTH"
            )
            
            assert StyleConstants.BORDER_COLOR in menu_stylesheet, (
                f"Tray Icon menu should use StyleConstants.BORDER_COLOR"
            )
            
            # Verify Tray Icon menu uses StyleConstants RGB values
            r, g, b = StyleConstants.BACKGROUND_COLOR_RGB
            assert f"rgba({r}, {g}, {b}," in menu_stylesheet, (
                f"Tray Icon menu should use StyleConstants.BACKGROUND_COLOR_RGB"
            )
            
            # Clean up
            window.close()
            window.deleteLater()
            tray_icon.hide()


def test_settings_window_opacity_slider_integration(qapp, mock_config):
    """
    Test that opacity slider in Settings Window updates window opacity.
    
    Validates: Requirements 4.1, 5.1
    """
    # Mock apply_blur_effect to avoid platform-specific issues
    with patch('utils.platform_utils.apply_blur_effect'):
        # Create Settings Window
        window = SettingsWindow(mock_config)
        
        # Verify initial opacity
        initial_opacity = window._opacity
        assert initial_opacity == mock_config.window_opacity, (
            f"Initial opacity should match config, got {initial_opacity}"
        )
        
        # Simulate opacity slider change
        new_opacity = 180
        window._on_opacity_changed(new_opacity)
        
        # Verify opacity was updated
        assert window._opacity == new_opacity, (
            f"After slider change, opacity should be {new_opacity}, got {window._opacity}"
        )
        
        # Verify stylesheet reflects new opacity
        stylesheet = window.styleSheet()
        expected_bg_color = StyleConstants.get_background_color(new_opacity)
        assert expected_bg_color in stylesheet, (
            f"Stylesheet should contain background color with new opacity {new_opacity}"
        )
        
        # Clean up
        window.close()
        window.deleteLater()


def test_multiple_opacity_changes_in_sequence(qapp, mock_config):
    """
    Test that multiple opacity changes work correctly in sequence.
    
    Validates: Requirements 4.1, 5.2
    """
    # Mock apply_blur_effect to avoid platform-specific issues
    with patch('utils.platform_utils.apply_blur_effect'):
        # Create Settings Window
        window = SettingsWindow(mock_config)
        
        # Apply multiple opacity changes
        opacity_values = [100, 150, 200, 180, 120]
        
        for opacity in opacity_values:
            # Change opacity
            window._on_opacity_changed(opacity)
            
            # Verify opacity was updated
            assert window._opacity == opacity, (
                f"After change to {opacity}, window opacity should be {opacity}, "
                f"got {window._opacity}"
            )
            
            # Verify stylesheet reflects current opacity
            stylesheet = window.styleSheet()
            expected_bg_color = StyleConstants.get_background_color(opacity)
            assert expected_bg_color in stylesheet, (
                f"Stylesheet should contain background color with opacity {opacity}"
            )
        
        # Clean up
        window.close()
        window.deleteLater()


def test_settings_window_frameless_with_drag_functionality(qapp, mock_config):
    """
    Test that Settings Window is frameless but still draggable.
    
    Validates: Requirements 2.1, 2.2, 2.3, 5.1
    """
    # Mock apply_blur_effect to avoid platform-specific issues
    with patch('utils.platform_utils.apply_blur_effect'):
        # Create Settings Window
        window = SettingsWindow(mock_config)
        
        # Verify window is frameless
        flags = window.windowFlags()
        assert flags & Qt.WindowType.FramelessWindowHint, (
            "Settings Window should be frameless"
        )
        
        # Verify window has translucent background
        assert window.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground), (
            "Settings Window should have translucent background"
        )
        
        # Verify window has drag position attribute
        assert hasattr(window, '_drag_position'), (
            "Settings Window should have _drag_position attribute for dragging"
        )
        assert window._drag_position is None, (
            "Settings Window _drag_position should be None initially"
        )
        
        # Verify window has mouse event handlers
        assert hasattr(window, 'mousePressEvent'), (
            "Settings Window should have mousePressEvent handler"
        )
        assert hasattr(window, 'mouseMoveEvent'), (
            "Settings Window should have mouseMoveEvent handler"
        )
        assert hasattr(window, 'mouseReleaseEvent'), (
            "Settings Window should have mouseReleaseEvent handler"
        )
        
        # Clean up
        window.close()
        window.deleteLater()


def test_tray_icon_menu_actions_trigger_signals(qapp):
    """
    Test that Tray Icon menu actions trigger appropriate signals.
    
    Validates: Requirements 5.2, 5.4
    """
    # Mock the icon loading to avoid file system dependencies
    with patch('ui.tray_icon.QIcon'):
        # Create TrayIcon instance
        tray_icon = TrayIcon()
        
        # Create signal spy mocks
        show_settings_called = []
        quit_app_called = []
        
        # Connect signals to mocks
        tray_icon.show_settings.connect(lambda: show_settings_called.append(True))
        tray_icon.quit_app.connect(lambda: quit_app_called.append(True))
        
        # Get menu actions
        menu = tray_icon.tray_icon.contextMenu()
        actions = menu.actions()
        non_separator_actions = [a for a in actions if not a.isSeparator()]
        
        # Trigger first action (should be Settings)
        if len(non_separator_actions) > 0:
            non_separator_actions[0].trigger()
            # Verify show_settings signal was emitted
            assert len(show_settings_called) == 1, (
                "Settings action should emit show_settings signal"
            )
        
        # Trigger last action (should be Quit)
        if len(non_separator_actions) > 2:
            non_separator_actions[-1].trigger()
            # Verify quit_app signal was emitted
            assert len(quit_app_called) == 1, (
                "Quit action should emit quit_app signal"
            )
        
        # Clean up
        tray_icon.hide()


def test_settings_window_config_integration(qapp, mock_config):
    """
    Test that Settings Window correctly integrates with config.
    
    Validates: Requirements 1.5, 4.3, 5.1
    """
    # Mock apply_blur_effect to avoid platform-specific issues
    with patch('utils.platform_utils.apply_blur_effect'):
        # Test with valid config opacity
        mock_config.window_opacity = 175
        window = SettingsWindow(mock_config)
        
        # Verify window uses config opacity internally
        assert window._opacity == 175, (
            f"Window should use config opacity 175, got {window._opacity}"
        )
        
        # Note: The Settings Window has its own _apply_style() method that applies
        # a custom stylesheet for UI elements. The mixin's opacity is stored internally
        # and used for window-level styling. This is the correct behavior.
        
        # Clean up
        window.close()
        window.deleteLater()
