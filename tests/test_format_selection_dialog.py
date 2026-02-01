"""
Unit tests for FormatSelectionDialog.

Tests the basic functionality of the format selection dialog including
UI creation, format loading, button grid interaction, and selection handling.
"""

import pytest
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from ui.format_selection_dialog import FormatSelectionDialog
from services.formatting_config import FormattingConfig


@pytest.fixture
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def formatting_config():
    """Create a test formatting configuration."""
    config = FormattingConfig(
        enabled=True,
        provider="groq",
        model="llama-3.3-70b-versatile",
        applications=["notion", "obsidian", "markdown", "_fallback"],
        temperature=0.3
    )
    return config


def test_dialog_initialization(qapp, formatting_config):
    """Test that dialog initializes correctly."""
    dialog = FormatSelectionDialog(formatting_config)
    
    assert dialog is not None
    assert dialog.isModal()
    assert dialog.windowTitle() in ["Select Format", "Выбор формата"]
    assert len(dialog.format_buttons) > 0


def test_universal_format_first(qapp, formatting_config):
    """Test that Universal format is always first in the grid."""
    dialog = FormatSelectionDialog(formatting_config)
    
    # Check that _fallback button exists
    assert "_fallback" in dialog.format_buttons
    
    # Get the button at position (0, 0) in the grid
    first_button = dialog.formats_grid.itemAtPosition(0, 0)
    assert first_button is not None
    
    # Verify it's the Universal format button
    button_widget = first_button.widget()
    assert button_widget == dialog.format_buttons["_fallback"]
    
    # Check display name
    display_name = button_widget.text()
    assert display_name in ["Universal", "Универсальный"]


def test_format_buttons_populated(qapp, formatting_config):
    """Test that format buttons are populated with all applications."""
    dialog = FormatSelectionDialog(formatting_config)
    
    # Should have Universal + 3 other apps (notion, obsidian, markdown)
    # _fallback is not duplicated
    assert len(dialog.format_buttons) == 4
    
    # Check that all formats are present
    format_ids = list(dialog.format_buttons.keys())
    
    assert "_fallback" in format_ids
    assert "notion" in format_ids
    assert "obsidian" in format_ids
    assert "markdown" in format_ids


def test_cancel_returns_none(qapp, formatting_config):
    """Test that cancelling the dialog returns None."""
    dialog = FormatSelectionDialog(formatting_config)
    
    # Simulate cancel
    dialog._on_cancel()
    
    # Should return None
    assert dialog.get_selected_format() is None
    assert dialog.result() == QDialog.DialogCode.Rejected


def test_button_click_returns_selected_format(qapp, formatting_config):
    """Test that clicking a button returns the selected format."""
    dialog = FormatSelectionDialog(formatting_config)
    
    # Click notion button
    notion_button = dialog.format_buttons["notion"]
    notion_button.click()
    
    # Should return the selected format
    selected = dialog.get_selected_format()
    assert selected == "notion"
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_keyboard_esc_cancels(qapp, formatting_config):
    """Test that ESC key cancels the dialog."""
    dialog = FormatSelectionDialog(formatting_config)
    dialog.show()
    
    # Press ESC
    QTest.keyClick(dialog, Qt.Key.Key_Escape)
    
    # Should be cancelled
    assert dialog.get_selected_format() is None
    assert dialog.result() == QDialog.DialogCode.Rejected


def test_empty_config_shows_universal_only(qapp):
    """Test that empty config shows only Universal format."""
    config = FormattingConfig(
        enabled=True,
        provider="groq",
        model="llama-3.3-70b-versatile",
        applications=[],  # Empty
        temperature=0.3
    )
    
    dialog = FormatSelectionDialog(config)
    
    # Should have only Universal format
    assert len(dialog.format_buttons) == 1
    assert "_fallback" in dialog.format_buttons


def test_button_click_immediately_selects(qapp, formatting_config):
    """Test that clicking a button immediately selects and closes dialog."""
    dialog = FormatSelectionDialog(formatting_config)
    dialog.show()
    
    # Click obsidian button
    obsidian_button = dialog.format_buttons["obsidian"]
    obsidian_button.click()
    
    # Should be confirmed immediately
    assert dialog.get_selected_format() == "obsidian"
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_format_names_are_human_readable(qapp, formatting_config):
    """Test that format names are displayed in human-readable format."""
    dialog = FormatSelectionDialog(formatting_config)
    
    # Check that names are capitalized and formatted
    for format_id, button in dialog.format_buttons.items():
        if format_id == "_fallback":
            continue  # Skip Universal format
        
        display_name = button.text()
        
        # Should be title case
        assert display_name[0].isupper()
        
        # Should not contain underscores
        assert "_" not in display_name


def test_dialog_is_modal(qapp, formatting_config):
    """Test that dialog is modal."""
    dialog = FormatSelectionDialog(formatting_config)
    assert dialog.isModal()


def test_dialog_has_minimum_size(qapp, formatting_config):
    """Test that dialog has minimum size set."""
    dialog = FormatSelectionDialog(formatting_config)
    assert dialog.minimumWidth() == 500
    assert dialog.minimumHeight() == 400


def test_buttons_have_proper_styling(qapp, formatting_config):
    """Test that buttons have proper styling applied."""
    dialog = FormatSelectionDialog(formatting_config)
    
    # Check that buttons have styling
    for button in dialog.format_buttons.values():
        assert button.styleSheet() != ""
        assert button.minimumHeight() == 80  # Same as settings
        assert button.minimumWidth() == 120  # Same as settings
        assert button.cursor().shape() == Qt.CursorShape.PointingHandCursor


def test_grid_layout_has_4_columns(qapp, formatting_config):
    """Test that grid layout uses 4 columns."""
    dialog = FormatSelectionDialog(formatting_config)
    
    # With 4 formats, should have 1 row with 4 columns
    # Check that items exist in first row
    assert dialog.formats_grid.itemAtPosition(0, 0) is not None
    assert dialog.formats_grid.itemAtPosition(0, 1) is not None
    assert dialog.formats_grid.itemAtPosition(0, 2) is not None
    assert dialog.formats_grid.itemAtPosition(0, 3) is not None
    
    # Second row should be empty (only 4 formats)
    assert dialog.formats_grid.itemAtPosition(1, 0) is None
