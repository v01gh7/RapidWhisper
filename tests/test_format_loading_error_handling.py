"""
Test error handling for format loading failures in FormatSelectionDialog.

This test verifies that the dialog properly handles:
1. Empty format list (shows Universal only)
2. Format loading failures (displays error message)
3. Appropriate error logging

Requirements: 10.1
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QMessageBox
from ui.format_selection_dialog import FormatSelectionDialog
from services.formatting_config import FormattingConfig


@pytest.fixture
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_empty_format_list_shows_universal_only(qapp):
    """
    Test that when no formats are configured, only Universal format is shown.
    
    Requirements: 10.1
    """
    # Create a config with no applications
    config = Mock(spec=FormattingConfig)
    config.applications = []
    
    # Create dialog
    dialog = FormatSelectionDialog(config)
    
    # Verify Universal format is shown
    assert dialog.format_list.count() == 1
    item = dialog.format_list.item(0)
    assert item is not None
    assert "Universal" in item.text() or "Универсальный" in item.text()
    assert item.data(0x0100) == "_fallback"  # Qt.ItemDataRole.UserRole


def test_none_config_shows_universal_only(qapp):
    """
    Test that when config.applications is None, only Universal format is shown.
    
    Requirements: 10.1
    """
    # Create a config with None applications
    config = Mock(spec=FormattingConfig)
    config.applications = None
    
    # Create dialog
    dialog = FormatSelectionDialog(config)
    
    # Verify Universal format is shown
    assert dialog.format_list.count() == 1
    item = dialog.format_list.item(0)
    assert item is not None
    assert item.data(0x0100) == "_fallback"


def test_format_loading_exception_shows_error_message(qapp):
    """
    Test that when format loading fails, an error message is displayed.
    
    Requirements: 10.1
    """
    # Create a config that will raise an exception
    config = Mock(spec=FormattingConfig)
    config.applications = Mock()
    config.applications.__iter__ = Mock(side_effect=Exception("Test error"))
    
    # Mock QMessageBox to prevent actual dialog display
    with patch('ui.format_selection_dialog.QMessageBox.warning') as mock_warning:
        # Create dialog (should trigger error handling)
        dialog = FormatSelectionDialog(config)
        
        # Verify error message was displayed
        mock_warning.assert_called_once()
        call_args = mock_warning.call_args
        assert call_args is not None
        # Check that error message contains appropriate text
        assert len(call_args[0]) >= 3  # parent, title, message


def test_format_loading_exception_logs_error(qapp, caplog):
    """
    Test that when format loading fails, the error is logged.
    
    Requirements: 10.1
    """
    # Create a config that will raise an exception
    config = Mock(spec=FormattingConfig)
    config.applications = Mock()
    config.applications.__iter__ = Mock(side_effect=Exception("Test error"))
    
    # Mock QMessageBox to prevent actual dialog display
    with patch('ui.format_selection_dialog.QMessageBox.warning'):
        # Create dialog (should trigger error handling)
        dialog = FormatSelectionDialog(config)
        
        # Verify error was logged
        assert any("Failed to load formats" in record.message for record in caplog.records)


def test_format_loading_exception_fallback_to_universal(qapp):
    """
    Test that when format loading fails, dialog falls back to Universal format.
    
    Requirements: 10.1
    """
    # Create a config that will raise an exception
    config = Mock(spec=FormattingConfig)
    config.applications = Mock()
    config.applications.__iter__ = Mock(side_effect=Exception("Test error"))
    
    # Mock QMessageBox to prevent actual dialog display
    with patch('ui.format_selection_dialog.QMessageBox.warning'):
        # Create dialog (should trigger error handling)
        dialog = FormatSelectionDialog(config)
        
        # Verify Universal format is shown as fallback
        assert dialog.format_list.count() == 1
        item = dialog.format_list.item(0)
        assert item is not None
        assert item.data(0x0100) == "_fallback"


def test_user_can_select_universal_after_error(qapp):
    """
    Test that user can still select Universal format after loading error.
    
    Requirements: 10.1
    """
    # Create a config that will raise an exception
    config = Mock(spec=FormattingConfig)
    config.applications = Mock()
    config.applications.__iter__ = Mock(side_effect=Exception("Test error"))
    
    # Mock QMessageBox to prevent actual dialog display
    with patch('ui.format_selection_dialog.QMessageBox.warning'):
        # Create dialog (should trigger error handling)
        dialog = FormatSelectionDialog(config)
        
        # Verify first item is selected by default
        assert dialog.format_list.currentRow() == 0
        
        # Simulate user confirming selection
        dialog._on_confirm()
        
        # Verify Universal format was selected
        assert dialog.get_selected_format() == "_fallback"


def test_user_can_cancel_after_error(qapp):
    """
    Test that user can cancel dialog after loading error.
    
    Requirements: 10.1
    """
    # Create a config that will raise an exception
    config = Mock(spec=FormattingConfig)
    config.applications = Mock()
    config.applications.__iter__ = Mock(side_effect=Exception("Test error"))
    
    # Mock QMessageBox to prevent actual dialog display
    with patch('ui.format_selection_dialog.QMessageBox.warning'):
        # Create dialog (should trigger error handling)
        dialog = FormatSelectionDialog(config)
        
        # Simulate user cancelling
        dialog._on_cancel()
        
        # Verify no format was selected
        assert dialog.get_selected_format() is None


def test_normal_format_loading_with_multiple_formats(qapp):
    """
    Test that normal format loading works correctly with multiple formats.
    
    This is a positive test to ensure error handling doesn't break normal operation.
    """
    # Create a config with multiple applications
    config = Mock(spec=FormattingConfig)
    config.applications = ["notion", "markdown", "slack"]
    
    # Create dialog
    dialog = FormatSelectionDialog(config)
    
    # Verify all formats are shown (Universal + 3 custom)
    assert dialog.format_list.count() == 4
    
    # Verify Universal is first
    first_item = dialog.format_list.item(0)
    assert first_item.data(0x0100) == "_fallback"
    
    # Verify other formats are present
    format_ids = [dialog.format_list.item(i).data(0x0100) for i in range(dialog.format_list.count())]
    assert "_fallback" in format_ids
    assert "notion" in format_ids
    assert "markdown" in format_ids
    assert "slack" in format_ids
