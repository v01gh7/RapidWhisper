"""
Verification tests for Task 1.6: Implement selection handling and return value.

This test file specifically verifies the requirements for task 1.6:
- get_selected_format() method exists and works correctly
- OK button click accepts dialog and stores selection
- Cancel button rejects dialog and returns None
- ESC key rejects dialog and returns None

Requirements: 3.1, 3.2, 3.3
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


class TestTask16SelectionHandling:
    """Test suite for Task 1.6 requirements."""
    
    def test_get_selected_format_method_exists(self, qapp, formatting_config):
        """Verify that get_selected_format() method exists."""
        dialog = FormatSelectionDialog(formatting_config)
        
        # Method should exist
        assert hasattr(dialog, 'get_selected_format')
        assert callable(dialog.get_selected_format)
    
    def test_get_selected_format_returns_none_initially(self, qapp, formatting_config):
        """Verify that get_selected_format() returns None before any selection."""
        dialog = FormatSelectionDialog(formatting_config)
        
        # Should return None initially
        assert dialog.get_selected_format() is None
    
    def test_ok_button_accepts_dialog(self, qapp, formatting_config):
        """
        Verify OK button accepts dialog.
        
        Requirement 3.2: WHEN the user confirms the selection, 
        THE Format_Selection_Dialog SHALL close and return the selected format
        """
        dialog = FormatSelectionDialog(formatting_config)
        
        # Select a format (second item - notion)
        dialog.format_list.setCurrentRow(1)
        
        # Click OK button
        dialog._on_confirm()
        
        # Dialog should be accepted
        assert dialog.result() == QDialog.DialogCode.Accepted
    
    def test_ok_button_stores_selection(self, qapp, formatting_config):
        """
        Verify OK button stores the selected format.
        
        Requirement 3.1: WHEN a user selects a format from the Format_Selection_Dialog, 
        THE State_Manager SHALL store the selection as Manual_Format_Selection
        """
        dialog = FormatSelectionDialog(formatting_config)
        
        # Select a format (second item - notion)
        dialog.format_list.setCurrentRow(1)
        
        # Click OK button
        dialog._on_confirm()
        
        # Should store the selected format
        selected = dialog.get_selected_format()
        assert selected == "notion"
    
    def test_ok_button_with_universal_format(self, qapp, formatting_config):
        """Verify OK button works with Universal format (first item)."""
        dialog = FormatSelectionDialog(formatting_config)
        
        # First item should be selected by default (Universal)
        assert dialog.format_list.currentRow() == 0
        
        # Click OK button
        dialog._on_confirm()
        
        # Should store Universal format
        selected = dialog.get_selected_format()
        assert selected == "_fallback"
        assert dialog.result() == QDialog.DialogCode.Accepted
    
    def test_cancel_button_rejects_dialog(self, qapp, formatting_config):
        """
        Verify Cancel button rejects dialog.
        
        Requirement 3.3: WHEN the user cancels the dialog or presses ESC, 
        THE System SHALL maintain normal format detection behavior
        """
        dialog = FormatSelectionDialog(formatting_config)
        
        # Select a format
        dialog.format_list.setCurrentRow(1)
        
        # Click Cancel button
        dialog._on_cancel()
        
        # Dialog should be rejected
        assert dialog.result() == QDialog.DialogCode.Rejected
    
    def test_cancel_button_returns_none(self, qapp, formatting_config):
        """
        Verify Cancel button returns None.
        
        Requirement 3.3: WHEN the user cancels the dialog or presses ESC, 
        THE System SHALL maintain normal format detection behavior
        """
        dialog = FormatSelectionDialog(formatting_config)
        
        # Select a format
        dialog.format_list.setCurrentRow(1)
        
        # Click Cancel button
        dialog._on_cancel()
        
        # Should return None
        assert dialog.get_selected_format() is None
    
    def test_esc_key_rejects_dialog(self, qapp, formatting_config):
        """
        Verify ESC key rejects dialog.
        
        Requirement 3.3: WHEN the user cancels the dialog or presses ESC, 
        THE System SHALL maintain normal format detection behavior
        """
        dialog = FormatSelectionDialog(formatting_config)
        dialog.show()
        
        # Select a format
        dialog.format_list.setCurrentRow(1)
        
        # Press ESC key
        QTest.keyClick(dialog, Qt.Key.Key_Escape)
        
        # Dialog should be rejected
        assert dialog.result() == QDialog.DialogCode.Rejected
    
    def test_esc_key_returns_none(self, qapp, formatting_config):
        """
        Verify ESC key returns None.
        
        Requirement 3.3: WHEN the user cancels the dialog or presses ESC, 
        THE System SHALL maintain normal format detection behavior
        """
        dialog = FormatSelectionDialog(formatting_config)
        dialog.show()
        
        # Select a format
        dialog.format_list.setCurrentRow(1)
        
        # Press ESC key
        QTest.keyClick(dialog, Qt.Key.Key_Escape)
        
        # Should return None
        assert dialog.get_selected_format() is None
    
    def test_enter_key_accepts_dialog(self, qapp, formatting_config):
        """Verify Enter key accepts dialog and stores selection."""
        dialog = FormatSelectionDialog(formatting_config)
        dialog.show()
        
        # Select a format (third item - obsidian)
        dialog.format_list.setCurrentRow(2)
        
        # Press Enter key
        QTest.keyClick(dialog, Qt.Key.Key_Return)
        
        # Dialog should be accepted
        assert dialog.result() == QDialog.DialogCode.Accepted
        
        # Should store the selected format
        selected = dialog.get_selected_format()
        assert selected == "obsidian"
    
    def test_double_click_accepts_dialog(self, qapp, formatting_config):
        """Verify double-clicking an item accepts dialog and stores selection."""
        dialog = FormatSelectionDialog(formatting_config)
        dialog.show()
        
        # Select a format (second item - notion)
        dialog.format_list.setCurrentRow(1)
        
        # Simulate double-click by calling _on_confirm
        dialog._on_confirm()
        
        # Dialog should be accepted
        assert dialog.result() == QDialog.DialogCode.Accepted
        
        # Should store the selected format
        selected = dialog.get_selected_format()
        assert selected == "notion"
    
    def test_ok_button_without_selection(self, qapp, formatting_config):
        """Verify OK button behavior when no item is selected (edge case)."""
        dialog = FormatSelectionDialog(formatting_config)
        
        # Clear selection (shouldn't happen in normal use, but test edge case)
        dialog.format_list.setCurrentRow(-1)
        
        # Click OK button
        dialog._on_confirm()
        
        # Dialog should be rejected (no valid selection)
        assert dialog.result() == QDialog.DialogCode.Rejected
    
    def test_multiple_selections_last_wins(self, qapp, formatting_config):
        """Verify that multiple selections work and last confirmation wins."""
        dialog = FormatSelectionDialog(formatting_config)
        
        # Select first format
        dialog.format_list.setCurrentRow(0)
        dialog._on_confirm()
        assert dialog.get_selected_format() == "_fallback"
        
        # Create new dialog
        dialog2 = FormatSelectionDialog(formatting_config)
        
        # Select different format
        dialog2.format_list.setCurrentRow(1)
        dialog2._on_confirm()
        assert dialog2.get_selected_format() == "notion"
    
    def test_cancel_after_selection_clears_selection(self, qapp, formatting_config):
        """Verify that cancelling after selecting clears the selection."""
        dialog = FormatSelectionDialog(formatting_config)
        
        # Select a format
        dialog.format_list.setCurrentRow(1)
        
        # Cancel
        dialog._on_cancel()
        
        # Selection should be None
        assert dialog.get_selected_format() is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
