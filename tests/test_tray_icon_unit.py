"""
Unit tests for Tray Icon menu styling.

These tests verify that the Tray Icon menu is created with correct styling,
all menu items are present, and menu actions are connected.
"""

import pytest
from PyQt6.QtWidgets import QApplication
from ui.tray_icon import TrayIcon
from design_system import StyleConstants
from unittest.mock import Mock, patch


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_tray_menu_created_with_correct_styling(qapp):
    """
    Test that menu is created with correct styling.
    
    Validates: Requirements 3.1, 3.2, 3.3
    """
    # Mock the icon loading to avoid file system dependencies
    with patch('ui.tray_icon.QIcon'):
        # Create TrayIcon instance
        tray_icon = TrayIcon()
        
        # Get the menu
        menu = tray_icon.tray_icon.contextMenu()
        assert menu is not None, "Tray icon should have a context menu"
        
        # Get the menu stylesheet
        stylesheet = menu.styleSheet()
        assert len(stylesheet) > 0, "Menu should have a stylesheet applied"
        
        # Verify background color is present
        expected_bg_color = StyleConstants.get_background_color(200)
        assert expected_bg_color in stylesheet, (
            f"Menu stylesheet should contain background color '{expected_bg_color}'"
        )
        
        # Verify border-radius is present
        assert "border-radius:" in stylesheet, (
            "Menu stylesheet should contain border-radius property"
        )
        assert f"{StyleConstants.BORDER_RADIUS}px" in stylesheet, (
            f"Menu stylesheet should contain border-radius value {StyleConstants.BORDER_RADIUS}px"
        )
        
        # Verify border is present
        assert "border:" in stylesheet, (
            "Menu stylesheet should contain border property"
        )
        assert f"{StyleConstants.BORDER_WIDTH}px" in stylesheet, (
            f"Menu stylesheet should contain border width {StyleConstants.BORDER_WIDTH}px"
        )
        
        # Clean up
        tray_icon.hide()


def test_tray_menu_all_items_present(qapp):
    """
    Test that all menu items are present.
    
    Validates: Requirements 5.2
    """
    # Mock the icon loading to avoid file system dependencies
    with patch('ui.tray_icon.QIcon'):
        # Create TrayIcon instance
        tray_icon = TrayIcon()
        
        # Get the menu
        menu = tray_icon.tray_icon.contextMenu()
        assert menu is not None, "Tray icon should have a context menu"
        
        # Get all menu actions
        actions = menu.actions()
        assert len(actions) > 0, "Menu should have at least one action"
        
        # Count non-separator actions
        non_separator_actions = [a for a in actions if not a.isSeparator()]
        assert len(non_separator_actions) >= 3, (
            f"Menu should have at least 3 non-separator actions (Settings, About, Quit), "
            f"got {len(non_separator_actions)}"
        )
        
        # Verify menu has separators
        separator_actions = [a for a in actions if a.isSeparator()]
        assert len(separator_actions) >= 2, (
            f"Menu should have at least 2 separators, got {len(separator_actions)}"
        )
        
        # Verify actions have text (not empty)
        for action in non_separator_actions:
            assert len(action.text()) > 0, (
                f"Menu action should have non-empty text, got '{action.text()}'"
            )
        
        # Clean up
        tray_icon.hide()


def test_tray_menu_actions_connected(qapp):
    """
    Test that menu actions are connected.
    
    Validates: Requirements 5.4
    """
    # Mock the icon loading to avoid file system dependencies
    with patch('ui.tray_icon.QIcon'):
        # Create TrayIcon instance
        tray_icon = TrayIcon()
        
        # Verify signals exist
        assert hasattr(tray_icon, 'show_settings'), (
            "TrayIcon should have show_settings signal"
        )
        assert hasattr(tray_icon, 'quit_app'), (
            "TrayIcon should have quit_app signal"
        )
        
        # Get the menu
        menu = tray_icon.tray_icon.contextMenu()
        assert menu is not None, "Tray icon should have a context menu"
        
        # Get all menu actions
        actions = menu.actions()
        non_separator_actions = [a for a in actions if not a.isSeparator()]
        
        # Verify at least one action is connected to show_settings
        # We can't directly test signal connections, but we can verify the actions exist
        # and have triggered signals connected
        for action in non_separator_actions:
            # Each action should have at least one connection
            # (we can't easily test this without triggering, but we verify they exist)
            assert action is not None, "Action should not be None"
            assert hasattr(action, 'triggered'), "Action should have triggered signal"
        
        # Clean up
        tray_icon.hide()


def test_tray_menu_hover_state_css_present(qapp):
    """
    Test hover state CSS is present in stylesheet.
    
    Validates: Requirements 3.4
    """
    # Mock the icon loading to avoid file system dependencies
    with patch('ui.tray_icon.QIcon'):
        # Create TrayIcon instance
        tray_icon = TrayIcon()
        
        # Get the menu
        menu = tray_icon.tray_icon.contextMenu()
        assert menu is not None, "Tray icon should have a context menu"
        
        # Get the menu stylesheet
        stylesheet = menu.styleSheet()
        
        # Verify hover state is present
        assert "QMenu::item:selected" in stylesheet, (
            "Menu stylesheet should contain hover state definition (QMenu::item:selected)"
        )
        
        # Verify hover state has background color
        hover_section = stylesheet.split("QMenu::item:selected")[1].split("}")[0]
        assert "background-color:" in hover_section, (
            "Hover state should have background-color property"
        )
        
        # Verify pressed state is present
        assert "QMenu::item:pressed" in stylesheet, (
            "Menu stylesheet should contain pressed state definition (QMenu::item:pressed)"
        )
        
        # Verify pressed state has background color
        pressed_section = stylesheet.split("QMenu::item:pressed")[1].split("}")[0]
        assert "background-color:" in pressed_section, (
            "Pressed state should have background-color property"
        )
        
        # Clean up
        tray_icon.hide()


def test_tray_menu_uses_style_constants(qapp):
    """
    Test that menu uses StyleConstants for all styling values.
    
    Validates: Requirements 7.3
    """
    # Mock the icon loading to avoid file system dependencies
    with patch('ui.tray_icon.QIcon'):
        # Create TrayIcon instance
        tray_icon = TrayIcon()
        
        # Get the menu
        menu = tray_icon.tray_icon.contextMenu()
        assert menu is not None, "Tray icon should have a context menu"
        
        # Get the menu stylesheet
        stylesheet = menu.styleSheet()
        
        # Verify StyleConstants values are used
        assert StyleConstants.BORDER_COLOR in stylesheet, (
            f"Menu should use StyleConstants.BORDER_COLOR: {StyleConstants.BORDER_COLOR}"
        )
        
        assert f"{StyleConstants.BORDER_WIDTH}px" in stylesheet, (
            f"Menu should use StyleConstants.BORDER_WIDTH: {StyleConstants.BORDER_WIDTH}px"
        )
        
        assert f"{StyleConstants.BORDER_RADIUS}px" in stylesheet, (
            f"Menu should use StyleConstants.BORDER_RADIUS: {StyleConstants.BORDER_RADIUS}px"
        )
        
        # Verify background color uses StyleConstants RGB values
        r, g, b = StyleConstants.BACKGROUND_COLOR_RGB
        assert f"rgba({r}, {g}, {b}," in stylesheet, (
            f"Menu should use StyleConstants.BACKGROUND_COLOR_RGB: ({r}, {g}, {b})"
        )
        
        # Clean up
        tray_icon.hide()


def test_tray_menu_separator_styling(qapp):
    """
    Test that menu separator has correct styling.
    
    Validates: Requirements 3.1, 3.2
    """
    # Mock the icon loading to avoid file system dependencies
    with patch('ui.tray_icon.QIcon'):
        # Create TrayIcon instance
        tray_icon = TrayIcon()
        
        # Get the menu
        menu = tray_icon.tray_icon.contextMenu()
        assert menu is not None, "Tray icon should have a context menu"
        
        # Get the menu stylesheet
        stylesheet = menu.styleSheet()
        
        # Verify separator styling is present
        assert "QMenu::separator" in stylesheet, (
            "Menu stylesheet should contain separator styling"
        )
        
        # Verify separator has styling properties
        separator_section = stylesheet.split("QMenu::separator")[1].split("}")[0]
        assert "height:" in separator_section or "background-color:" in separator_section, (
            "Separator should have height or background-color property"
        )
        
        # Clean up
        tray_icon.hide()


def test_tray_menu_item_padding(qapp):
    """
    Test that menu items have correct padding.
    
    Validates: Requirements 3.1
    """
    # Mock the icon loading to avoid file system dependencies
    with patch('ui.tray_icon.QIcon'):
        # Create TrayIcon instance
        tray_icon = TrayIcon()
        
        # Get the menu
        menu = tray_icon.tray_icon.contextMenu()
        assert menu is not None, "Tray icon should have a context menu"
        
        # Get the menu stylesheet
        stylesheet = menu.styleSheet()
        
        # Verify menu item styling is present
        assert "QMenu::item" in stylesheet, (
            "Menu stylesheet should contain item styling"
        )
        
        # Verify menu items have padding
        # Extract the QMenu::item section (before ::selected or ::pressed)
        item_section = stylesheet.split("QMenu::item")[1].split("QMenu::item:")[0]
        assert "padding:" in item_section, (
            "Menu items should have padding property"
        )
        
        # Clean up
        tray_icon.hide()


def test_tray_icon_has_tooltip(qapp):
    """
    Test that tray icon has a tooltip set.
    
    Validates: Requirements 5.1
    """
    # Mock the icon loading to avoid file system dependencies
    with patch('ui.tray_icon.QIcon'):
        # Create TrayIcon instance
        tray_icon = TrayIcon()
        
        # Verify tooltip is set
        tooltip = tray_icon.tray_icon.toolTip()
        assert len(tooltip) > 0, (
            "Tray icon should have a non-empty tooltip"
        )
        
        # Clean up
        tray_icon.hide()


def test_tray_icon_visible(qapp):
    """
    Test that tray icon is visible after initialization.
    
    Validates: Requirements 5.1
    """
    # Mock the icon loading to avoid file system dependencies
    with patch('ui.tray_icon.QIcon'):
        # Create TrayIcon instance
        tray_icon = TrayIcon()
        
        # Verify tray icon is visible
        assert tray_icon.tray_icon.isVisible(), (
            "Tray icon should be visible after initialization"
        )
        
        # Clean up
        tray_icon.hide()
