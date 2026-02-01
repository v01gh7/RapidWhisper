"""
Property-based tests for FormatSelectionDialog keyboard navigation.

Tests that keyboard navigation works correctly across all format lists.
Feature: manual-format-selection-hotkey
Property 5: Keyboard navigation works correctly
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from ui.format_selection_dialog import FormatSelectionDialog
from services.formatting_config import FormattingConfig
import sys


# Ensure QApplication exists for Qt tests
@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


# Strategy for generating application names
app_names = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'),
    min_size=1,
    max_size=30
)

# Strategy for generating lists of application names
app_lists = st.lists(app_names, min_size=0, max_size=10, unique=True)


@given(applications=app_lists)
@settings(max_examples=100, deadline=2000)
def test_property_5_arrow_down_navigation(qapp, applications):
    """
    **Validates: Requirements 7.1, 7.2**
    
    Feature: manual-format-selection-hotkey, Property 5: Keyboard navigation works correctly
    
    For any list of formatting applications, pressing the Down arrow key should 
    navigate to the next item in the list, wrapping to the first item when at the end.
    """
    # Create formatting config with test applications
    config = FormattingConfig(
        enabled=True,
        provider="groq",
        model="llama-3.3-70b-versatile",
        applications=applications,
        temperature=0.3
    )
    
    # Create dialog
    dialog = FormatSelectionDialog(config)
    dialog.show()
    
    # Get total number of items (Universal + applications, but _fallback not duplicated)
    total_items = dialog.format_list.count()
    
    # Should have at least Universal format
    assert total_items >= 1, "Dialog should have at least Universal format"
    
    # Start at first item (Universal)
    assert dialog.format_list.currentRow() == 0, "Should start at first item"
    
    # Navigate through all items with Down arrow
    for i in range(total_items):
        current_row = dialog.format_list.currentRow()
        assert current_row == i, f"Should be at row {i}"
        
        # Press Down arrow
        QTest.keyClick(dialog.format_list, Qt.Key.Key_Down)
        
        # Check new position
        expected_row = (i + 1) % total_items
        new_row = dialog.format_list.currentRow()
        assert new_row == expected_row, \
            f"After Down from row {i}, should be at row {expected_row}, but got {new_row}"
    
    dialog.close()


@given(applications=app_lists)
@settings(max_examples=100, deadline=2000)
def test_property_5_arrow_up_navigation(qapp, applications):
    """
    **Validates: Requirements 7.1, 7.2**
    
    Feature: manual-format-selection-hotkey, Property 5: Keyboard navigation works correctly
    
    For any list of formatting applications, pressing the Up arrow key should 
    navigate to the previous item in the list, wrapping to the last item when at the beginning.
    """
    # Create formatting config with test applications
    config = FormattingConfig(
        enabled=True,
        provider="groq",
        model="llama-3.3-70b-versatile",
        applications=applications,
        temperature=0.3
    )
    
    # Create dialog
    dialog = FormatSelectionDialog(config)
    dialog.show()
    
    # Get total number of items
    total_items = dialog.format_list.count()
    
    # Should have at least Universal format
    assert total_items >= 1, "Dialog should have at least Universal format"
    
    # Start at first item
    assert dialog.format_list.currentRow() == 0, "Should start at first item"
    
    # Press Up arrow from first item - should wrap to last
    QTest.keyClick(dialog.format_list, Qt.Key.Key_Up)
    assert dialog.format_list.currentRow() == total_items - 1, \
        "Up from first item should wrap to last item"
    
    # Navigate backwards through all items
    for i in range(total_items - 1, -1, -1):
        current_row = dialog.format_list.currentRow()
        assert current_row == i, f"Should be at row {i}"
        
        # Press Up arrow
        QTest.keyClick(dialog.format_list, Qt.Key.Key_Up)
        
        # Check new position
        expected_row = (i - 1) % total_items
        new_row = dialog.format_list.currentRow()
        assert new_row == expected_row, \
            f"After Up from row {i}, should be at row {expected_row}, but got {new_row}"
    
    dialog.close()


@given(applications=app_lists, navigation_steps=st.integers(min_value=0, max_value=20))
@settings(max_examples=100, deadline=2000)
def test_property_5_enter_confirms_current_selection(qapp, applications, navigation_steps):
    """
    **Validates: Requirements 7.1, 7.2**
    
    Feature: manual-format-selection-hotkey, Property 5: Keyboard navigation works correctly
    
    For any list of formatting applications and any navigation sequence, 
    pressing Enter should confirm the currently highlighted format selection.
    """
    # Create formatting config with test applications
    config = FormattingConfig(
        enabled=True,
        provider="groq",
        model="llama-3.3-70b-versatile",
        applications=applications,
        temperature=0.3
    )
    
    # Create dialog
    dialog = FormatSelectionDialog(config)
    dialog.show()
    
    # Get total number of items
    total_items = dialog.format_list.count()
    
    # Should have at least Universal format
    assume(total_items >= 1)
    
    # Navigate to a specific position
    target_row = navigation_steps % total_items
    dialog.format_list.setCurrentRow(target_row)
    
    # Get the format at current position
    current_item = dialog.format_list.currentItem()
    expected_format = current_item.data(Qt.ItemDataRole.UserRole)
    
    # Press Enter to confirm
    QTest.keyClick(dialog, Qt.Key.Key_Return)
    
    # Verify dialog was accepted
    assert dialog.result() == dialog.DialogCode.Accepted, \
        "Dialog should be accepted when Enter is pressed"
    
    # Verify correct format was selected
    selected_format = dialog.get_selected_format()
    assert selected_format == expected_format, \
        f"Selected format should be {expected_format}, but got {selected_format}"
    
    dialog.close()


@given(applications=app_lists, down_steps=st.integers(min_value=0, max_value=20))
@settings(max_examples=100, deadline=2000)
def test_property_5_mixed_navigation_sequence(qapp, applications, down_steps):
    """
    **Validates: Requirements 7.1, 7.2**
    
    Feature: manual-format-selection-hotkey, Property 5: Keyboard navigation works correctly
    
    For any list of formatting applications and any sequence of arrow key presses,
    the dialog should maintain correct position tracking and allow confirmation
    of the currently highlighted item.
    """
    # Create formatting config with test applications
    config = FormattingConfig(
        enabled=True,
        provider="groq",
        model="llama-3.3-70b-versatile",
        applications=applications,
        temperature=0.3
    )
    
    # Create dialog
    dialog = FormatSelectionDialog(config)
    dialog.show()
    
    # Get total number of items
    total_items = dialog.format_list.count()
    
    # Should have at least Universal format
    assume(total_items >= 1)
    
    # Start at first item
    expected_position = 0
    assert dialog.format_list.currentRow() == expected_position
    
    # Perform a sequence of Down arrow presses
    for _ in range(down_steps):
        QTest.keyClick(dialog.format_list, Qt.Key.Key_Down)
        expected_position = (expected_position + 1) % total_items
        assert dialog.format_list.currentRow() == expected_position, \
            f"Position should be {expected_position} after navigation"
    
    # Now press Up a few times
    up_steps = min(down_steps // 2, total_items)
    for _ in range(up_steps):
        QTest.keyClick(dialog.format_list, Qt.Key.Key_Up)
        expected_position = (expected_position - 1) % total_items
        assert dialog.format_list.currentRow() == expected_position, \
            f"Position should be {expected_position} after navigation"
    
    # Get the format at final position
    current_item = dialog.format_list.currentItem()
    expected_format = current_item.data(Qt.ItemDataRole.UserRole)
    
    # Confirm with Enter
    QTest.keyClick(dialog, Qt.Key.Key_Return)
    
    # Verify correct format was selected
    selected_format = dialog.get_selected_format()
    assert selected_format == expected_format, \
        f"After mixed navigation, selected format should be {expected_format}"
    
    dialog.close()


@given(applications=app_lists)
@settings(max_examples=100, deadline=2000)
def test_property_5_esc_cancels_regardless_of_position(qapp, applications):
    """
    **Validates: Requirements 7.1, 7.2**
    
    Feature: manual-format-selection-hotkey, Property 5: Keyboard navigation works correctly
    
    For any list of formatting applications and any navigation position,
    pressing ESC should cancel the dialog without making a selection.
    """
    # Create formatting config with test applications
    config = FormattingConfig(
        enabled=True,
        provider="groq",
        model="llama-3.3-70b-versatile",
        applications=applications,
        temperature=0.3
    )
    
    # Create dialog
    dialog = FormatSelectionDialog(config)
    dialog.show()
    
    # Get total number of items
    total_items = dialog.format_list.count()
    
    # Should have at least Universal format
    assume(total_items >= 1)
    
    # Navigate to a random position
    if total_items > 1:
        target_row = (total_items // 2) % total_items
        dialog.format_list.setCurrentRow(target_row)
    
    # Press ESC to cancel
    QTest.keyClick(dialog, Qt.Key.Key_Escape)
    
    # Verify dialog was rejected
    assert dialog.result() == dialog.DialogCode.Rejected, \
        "Dialog should be rejected when ESC is pressed"
    
    # Verify no format was selected
    selected_format = dialog.get_selected_format()
    assert selected_format is None, \
        "No format should be selected when dialog is cancelled"
    
    dialog.close()


@given(applications=app_lists)
@settings(max_examples=100, deadline=2000)
def test_property_5_navigation_preserves_list_integrity(qapp, applications):
    """
    **Validates: Requirements 7.1, 7.2**
    
    Feature: manual-format-selection-hotkey, Property 5: Keyboard navigation works correctly
    
    For any list of formatting applications, keyboard navigation should not
    modify the list contents or order - only the selection position.
    """
    # Create formatting config with test applications
    config = FormattingConfig(
        enabled=True,
        provider="groq",
        model="llama-3.3-70b-versatile",
        applications=applications,
        temperature=0.3
    )
    
    # Create dialog
    dialog = FormatSelectionDialog(config)
    dialog.show()
    
    # Get total number of items
    total_items = dialog.format_list.count()
    
    # Should have at least Universal format
    assume(total_items >= 1)
    
    # Capture initial list state
    initial_formats = []
    for i in range(total_items):
        item = dialog.format_list.item(i)
        format_id = item.data(Qt.ItemDataRole.UserRole)
        display_name = item.text()
        initial_formats.append((format_id, display_name))
    
    # Perform extensive navigation
    for _ in range(total_items * 3):
        QTest.keyClick(dialog.format_list, Qt.Key.Key_Down)
    
    for _ in range(total_items * 2):
        QTest.keyClick(dialog.format_list, Qt.Key.Key_Up)
    
    # Verify list contents unchanged
    assert dialog.format_list.count() == total_items, \
        "List size should not change during navigation"
    
    for i in range(total_items):
        item = dialog.format_list.item(i)
        format_id = item.data(Qt.ItemDataRole.UserRole)
        display_name = item.text()
        
        assert (format_id, display_name) == initial_formats[i], \
            f"Item at position {i} should remain unchanged"
    
    # Verify Universal is still first
    first_item = dialog.format_list.item(0)
    first_format_id = first_item.data(Qt.ItemDataRole.UserRole)
    assert first_format_id == "_fallback", \
        "Universal format should remain first after navigation"
    
    dialog.close()


# Unit tests for edge cases

def test_unit_single_item_navigation(qapp):
    """Unit test: Navigation with only Universal format"""
    config = FormattingConfig(
        enabled=True,
        provider="groq",
        model="llama-3.3-70b-versatile",
        applications=[],  # Empty - only Universal
        temperature=0.3
    )
    
    dialog = FormatSelectionDialog(config)
    dialog.show()
    
    # Should have exactly 1 item
    assert dialog.format_list.count() == 1
    
    # Should start at row 0
    assert dialog.format_list.currentRow() == 0
    
    # Down arrow should stay at row 0 (wraps to same item)
    QTest.keyClick(dialog.format_list, Qt.Key.Key_Down)
    assert dialog.format_list.currentRow() == 0
    
    # Up arrow should stay at row 0
    QTest.keyClick(dialog.format_list, Qt.Key.Key_Up)
    assert dialog.format_list.currentRow() == 0
    
    # Enter should still work
    QTest.keyClick(dialog, Qt.Key.Key_Return)
    assert dialog.result() == dialog.DialogCode.Accepted
    assert dialog.get_selected_format() == "_fallback"
    
    dialog.close()


def test_unit_navigation_boundary_conditions(qapp):
    """Unit test: Navigation at list boundaries"""
    config = FormattingConfig(
        enabled=True,
        provider="groq",
        model="llama-3.3-70b-versatile",
        applications=["app1", "app2", "app3"],
        temperature=0.3
    )
    
    dialog = FormatSelectionDialog(config)
    dialog.show()
    
    total_items = dialog.format_list.count()
    assert total_items == 4  # Universal + 3 apps
    
    # Start at first item (row 0)
    assert dialog.format_list.currentRow() == 0
    
    # Up from first should go to last
    QTest.keyClick(dialog.format_list, Qt.Key.Key_Up)
    assert dialog.format_list.currentRow() == total_items - 1
    
    # Down from last should go to first
    QTest.keyClick(dialog.format_list, Qt.Key.Key_Down)
    assert dialog.format_list.currentRow() == 0
    
    dialog.close()


def test_unit_enter_on_each_item(qapp):
    """Unit test: Enter key works on each item in the list"""
    config = FormattingConfig(
        enabled=True,
        provider="groq",
        model="llama-3.3-70b-versatile",
        applications=["notion", "obsidian"],
        temperature=0.3
    )
    
    # Test each item
    for target_row in range(3):  # Universal + 2 apps
        dialog = FormatSelectionDialog(config)
        dialog.show()
        
        # Navigate to target row
        dialog.format_list.setCurrentRow(target_row)
        
        # Get expected format
        item = dialog.format_list.item(target_row)
        expected_format = item.data(Qt.ItemDataRole.UserRole)
        
        # Press Enter
        QTest.keyClick(dialog, Qt.Key.Key_Return)
        
        # Verify
        assert dialog.result() == dialog.DialogCode.Accepted
        assert dialog.get_selected_format() == expected_format
        
        dialog.close()
