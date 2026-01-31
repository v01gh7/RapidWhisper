"""
Property-based tests for Tray Icon menu styling.

These tests verify universal properties that should hold across all valid inputs
using the Hypothesis library for property-based testing.
"""

import pytest
from hypothesis import given, strategies as st, settings
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


# Feature: unified-design-system, Property 6: Tray Menu Stylesheet Application
@given(seed=st.integers(min_value=0, max_value=1000))
@settings(max_examples=100)
def test_tray_menu_stylesheet_application(qapp, seed: int):
    """
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
    
    Property: For any Tray Icon menu instance, the applied stylesheet should contain
    a semi-transparent dark background using StyleConstants colors, rounded corners,
    and hover state definitions for menu items.
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
        
        # Verify background color uses StyleConstants
        # The menu uses opacity 200 for readability
        expected_bg_color = StyleConstants.get_background_color(200)
        assert expected_bg_color in stylesheet, (
            f"Menu stylesheet should contain background color '{expected_bg_color}'. "
            f"Stylesheet: {stylesheet}"
        )
        
        # Verify background color uses correct RGB values (30, 30, 30)
        r, g, b = StyleConstants.BACKGROUND_COLOR_RGB
        assert (r, g, b) == (30, 30, 30), (
            f"StyleConstants.BACKGROUND_COLOR_RGB should be (30, 30, 30), got ({r}, {g}, {b})"
        )
        assert f"rgba({r}, {g}, {b}, 200)" in stylesheet, (
            f"Menu stylesheet should contain 'rgba({r}, {g}, {b}, 200)'"
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
        assert StyleConstants.BORDER_COLOR in stylesheet, (
            f"Menu stylesheet should contain border color {StyleConstants.BORDER_COLOR}"
        )
        
        # Verify hover state definitions are present
        assert "QMenu::item:selected" in stylesheet, (
            "Menu stylesheet should contain hover state definition (QMenu::item:selected)"
        )
        assert "background-color:" in stylesheet.split("QMenu::item:selected")[1].split("}")[0], (
            "Hover state should have background-color property"
        )
        
        # Verify pressed state definitions are present
        assert "QMenu::item:pressed" in stylesheet, (
            "Menu stylesheet should contain pressed state definition (QMenu::item:pressed)"
        )
        
        # Verify separator styling is present
        assert "QMenu::separator" in stylesheet, (
            "Menu stylesheet should contain separator styling"
        )
        
        # Clean up
        tray_icon.hide()


# Feature: unified-design-system, Property 6: Tray Menu Stylesheet Application - Menu Items Preserved
@given(seed=st.integers(min_value=0, max_value=1000))
@settings(max_examples=100)
def test_tray_menu_items_preserved(qapp, seed: int):
    """
    **Validates: Requirements 5.2, 5.4**
    
    Property: For any Tray Icon instance, the menu should contain all expected
    menu items with their actions properly connected.
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
        
        # Verify signals are connected
        # The TrayIcon class should have show_settings and quit_app signals
        assert hasattr(tray_icon, 'show_settings'), (
            "TrayIcon should have show_settings signal"
        )
        assert hasattr(tray_icon, 'quit_app'), (
            "TrayIcon should have quit_app signal"
        )
        
        # Clean up
        tray_icon.hide()


# Feature: unified-design-system, Property 6: Tray Menu Stylesheet Application - Color Consistency
@given(seed=st.integers(min_value=0, max_value=1000))
@settings(max_examples=100)
def test_tray_menu_color_consistency(qapp, seed: int):
    """
    **Validates: Requirements 3.3**
    
    Property: For any Tray Icon menu instance, the menu should use consistent
    color scheme with StyleConstants (same RGB values as other windows).
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
        
        # Verify the menu uses the same RGB values as StyleConstants
        r, g, b = StyleConstants.BACKGROUND_COLOR_RGB
        expected_rgb_string = f"rgba({r}, {g}, {b},"
        assert expected_rgb_string in stylesheet, (
            f"Menu stylesheet should use StyleConstants RGB values. "
            f"Expected '{expected_rgb_string}' in stylesheet"
        )
        
        # Verify the menu uses the same border color as StyleConstants
        assert StyleConstants.BORDER_COLOR in stylesheet, (
            f"Menu stylesheet should use StyleConstants border color '{StyleConstants.BORDER_COLOR}'"
        )
        
        # Verify the menu uses the same border radius as StyleConstants
        assert f"{StyleConstants.BORDER_RADIUS}px" in stylesheet, (
            f"Menu stylesheet should use StyleConstants border radius {StyleConstants.BORDER_RADIUS}px"
        )
        
        # Verify the menu uses the same border width as StyleConstants
        assert f"{StyleConstants.BORDER_WIDTH}px" in stylesheet, (
            f"Menu stylesheet should use StyleConstants border width {StyleConstants.BORDER_WIDTH}px"
        )
        
        # Clean up
        tray_icon.hide()


# Feature: unified-design-system, Property 6: Tray Menu Stylesheet Application - Hover State Colors
@given(seed=st.integers(min_value=0, max_value=1000))
@settings(max_examples=100)
def test_tray_menu_hover_state_colors(qapp, seed: int):
    """
    **Validates: Requirements 3.4**
    
    Property: For any Tray Icon menu instance, the hover and pressed states
    should have appropriate background colors defined.
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
        
        # Extract hover state section
        assert "QMenu::item:selected" in stylesheet, (
            "Menu stylesheet should contain hover state (QMenu::item:selected)"
        )
        hover_section = stylesheet.split("QMenu::item:selected")[1].split("}")[0]
        
        # Verify hover state has background color
        assert "background-color:" in hover_section, (
            "Hover state should define background-color"
        )
        # Verify hover state uses rgba format
        assert "rgba(" in hover_section, (
            "Hover state background-color should use rgba format"
        )
        
        # Extract pressed state section
        assert "QMenu::item:pressed" in stylesheet, (
            "Menu stylesheet should contain pressed state (QMenu::item:pressed)"
        )
        pressed_section = stylesheet.split("QMenu::item:pressed")[1].split("}")[0]
        
        # Verify pressed state has background color
        assert "background-color:" in pressed_section, (
            "Pressed state should define background-color"
        )
        # Verify pressed state uses rgba format
        assert "rgba(" in pressed_section, (
            "Pressed state background-color should use rgba format"
        )
        
        # Clean up
        tray_icon.hide()
