"""
Property-based tests for StyledWindowMixin.

These tests verify universal properties that should hold across all valid inputs
using the Hypothesis library for property-based testing.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from PyQt6.QtWidgets import QWidget, QApplication
from design_system import StyledWindowMixin, StyleConstants


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class StyledTestWindow(StyledWindowMixin, QWidget):
    """Test window class that uses the mixin"""
    
    def __init__(self):
        QWidget.__init__(self)
        StyledWindowMixin.__init__(self)


# Feature: unified-design-system, Property 4: Dynamic Opacity Updates
@given(
    initial_opacity=st.integers(min_value=50, max_value=255),
    new_opacity=st.integers(min_value=50, max_value=255)
)
@settings(max_examples=100)
def test_dynamic_opacity_updates(qapp, initial_opacity: int, new_opacity: int):
    """
    **Validates: Requirements 4.1**
    
    Property: For any styled window with an initial opacity, when update_opacity()
    is called with a new valid opacity value, the window's stylesheet should be
    updated to reflect the new opacity in the background color.
    """
    # Create a styled window with initial opacity
    window = StyledTestWindow()
    window.apply_unified_style(opacity=initial_opacity)
    
    # Verify initial state
    initial_stylesheet = window.styleSheet()
    initial_bg_color = StyleConstants.get_background_color(initial_opacity)
    assert initial_bg_color in initial_stylesheet, (
        f"Initial stylesheet should contain background color with opacity {initial_opacity}"
    )
    assert window._opacity == initial_opacity, (
        f"Window internal opacity should be {initial_opacity}, got {window._opacity}"
    )
    
    # Update opacity to new value
    window.update_opacity(new_opacity)
    
    # Verify the opacity was updated internally
    assert window._opacity == new_opacity, (
        f"After update_opacity({new_opacity}), internal opacity should be {new_opacity}, "
        f"got {window._opacity}"
    )
    
    # Verify the stylesheet was updated with new opacity
    updated_stylesheet = window.styleSheet()
    new_bg_color = StyleConstants.get_background_color(new_opacity)
    assert new_bg_color in updated_stylesheet, (
        f"Updated stylesheet should contain background color with opacity {new_opacity}. "
        f"Expected '{new_bg_color}' in stylesheet"
    )
    
    # If opacities are different, verify old opacity is no longer in stylesheet
    if initial_opacity != new_opacity:
        assert initial_bg_color not in updated_stylesheet, (
            f"Updated stylesheet should not contain old background color with opacity {initial_opacity}. "
            f"Old color '{initial_bg_color}' should not be in stylesheet"
        )
    
    # Verify other style properties are preserved
    assert "border:" in updated_stylesheet, (
        "Stylesheet should still contain border property after opacity update"
    )
    assert f"{StyleConstants.BORDER_WIDTH}px" in updated_stylesheet, (
        f"Stylesheet should still contain border width {StyleConstants.BORDER_WIDTH}px"
    )
    assert StyleConstants.BORDER_COLOR in updated_stylesheet, (
        f"Stylesheet should still contain border color {StyleConstants.BORDER_COLOR}"
    )
    assert "border-radius:" in updated_stylesheet, (
        "Stylesheet should still contain border-radius property"
    )
    assert f"{StyleConstants.BORDER_RADIUS}px" in updated_stylesheet, (
        f"Stylesheet should still contain border-radius {StyleConstants.BORDER_RADIUS}px"
    )


# Feature: unified-design-system, Property 4: Dynamic Opacity Updates - With Clamping
@given(
    initial_opacity=st.integers(min_value=50, max_value=255),
    new_opacity=st.integers()  # Any integer, including out of range
)
@settings(max_examples=100)
def test_dynamic_opacity_updates_with_clamping(qapp, initial_opacity: int, new_opacity: int):
    """
    **Validates: Requirements 4.1, 4.2**
    
    Property: For any styled window with an initial opacity, when update_opacity()
    is called with any integer value (including out of range), the window's stylesheet
    should be updated to reflect the clamped opacity value in the background color.
    """
    # Create a styled window with initial opacity
    window = StyledTestWindow()
    window.apply_unified_style(opacity=initial_opacity)
    
    # Update opacity to new value (may be out of range)
    window.update_opacity(new_opacity)
    
    # Calculate expected clamped opacity
    expected_opacity = StyleConstants.clamp_opacity(new_opacity)
    
    # Verify the opacity was clamped and updated internally
    assert window._opacity == expected_opacity, (
        f"After update_opacity({new_opacity}), internal opacity should be clamped to {expected_opacity}, "
        f"got {window._opacity}"
    )
    
    # Verify the opacity is within valid range
    assert StyleConstants.OPACITY_MIN <= window._opacity <= StyleConstants.OPACITY_MAX, (
        f"Window opacity {window._opacity} should be within valid range "
        f"[{StyleConstants.OPACITY_MIN}, {StyleConstants.OPACITY_MAX}]"
    )
    
    # Verify the stylesheet contains the clamped opacity
    updated_stylesheet = window.styleSheet()
    expected_bg_color = StyleConstants.get_background_color(expected_opacity)
    assert expected_bg_color in updated_stylesheet, (
        f"Updated stylesheet should contain background color with clamped opacity {expected_opacity}. "
        f"Expected '{expected_bg_color}' in stylesheet"
    )


# Feature: unified-design-system, Property 4: Dynamic Opacity Updates - Multiple Updates
@given(
    initial_opacity=st.integers(min_value=50, max_value=255),
    opacity_sequence=st.lists(
        st.integers(min_value=50, max_value=255),
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=100)
def test_dynamic_opacity_multiple_updates(qapp, initial_opacity: int, opacity_sequence: list):
    """
    **Validates: Requirements 4.1**
    
    Property: For any styled window, when update_opacity() is called multiple times
    in sequence, each update should correctly update the stylesheet to reflect the
    current opacity value.
    """
    # Create a styled window with initial opacity
    window = StyledTestWindow()
    window.apply_unified_style(opacity=initial_opacity)
    
    # Apply each opacity update in sequence
    for opacity in opacity_sequence:
        window.update_opacity(opacity)
        
        # Verify internal opacity is updated
        assert window._opacity == opacity, (
            f"After update_opacity({opacity}), internal opacity should be {opacity}, "
            f"got {window._opacity}"
        )
        
        # Verify stylesheet contains current opacity
        stylesheet = window.styleSheet()
        expected_bg_color = StyleConstants.get_background_color(opacity)
        assert expected_bg_color in stylesheet, (
            f"Stylesheet should contain background color with opacity {opacity}. "
            f"Expected '{expected_bg_color}' in stylesheet"
        )
        
        # Verify other style properties are still present
        assert "border:" in stylesheet, (
            f"Stylesheet should still contain border property after update to opacity {opacity}"
        )
        assert "border-radius:" in stylesheet, (
            f"Stylesheet should still contain border-radius property after update to opacity {opacity}"
        )


# Feature: unified-design-system, Property 5: Window Dragging Behavior
@given(
    initial_x=st.integers(min_value=0, max_value=1920),
    initial_y=st.integers(min_value=0, max_value=1080),
    drag_delta_x=st.integers(min_value=-500, max_value=500),
    drag_delta_y=st.integers(min_value=-500, max_value=500)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_window_dragging_behavior(qtbot, initial_x: int, initial_y: int, 
                                   drag_delta_x: int, drag_delta_y: int):
    """
    **Validates: Requirements 2.3**
    
    Property: For any frameless styled window, when mouse press, move, and release
    events are simulated with valid coordinates, the window position should change
    to follow the mouse movement delta.
    """
    # Create a styled window
    window = StyledTestWindow()
    window.apply_unified_style()
    
    # Set initial position
    window.move(initial_x, initial_y)
    window.show()
    qtbot.addWidget(window)
    qtbot.waitExposed(window)
    
    # Record initial position
    initial_pos = window.pos()
    assert initial_pos.x() == initial_x, (
        f"Window should be at x={initial_x}, got {initial_pos.x()}"
    )
    assert initial_pos.y() == initial_y, (
        f"Window should be at y={initial_y}, got {initial_pos.y()}"
    )
    
    # Calculate mouse positions for drag operation
    # Start drag from center of window
    window_center_x = initial_x + window.width() // 2
    window_center_y = initial_y + window.height() // 2
    
    # End position after drag
    drag_end_x = window_center_x + drag_delta_x
    drag_end_y = window_center_y + drag_delta_y
    
    # Simulate mouse press at window center
    from PyQt6.QtCore import QPoint, QPointF, Qt
    from PyQt6.QtGui import QMouseEvent
    
    press_pos = QPointF(window.width() / 2, window.height() / 2)
    press_global_pos = QPointF(window.mapToGlobal(QPoint(window.width() // 2, window.height() // 2)))
    
    press_event = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        press_pos,
        press_global_pos,
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier
    )
    window.mousePressEvent(press_event)
    
    # Verify drag position was captured
    assert window._drag_position is not None, (
        "After mouse press, _drag_position should be set"
    )
    
    # Simulate mouse move to new position
    move_global_pos = QPointF(drag_end_x, drag_end_y)
    move_local_pos = QPointF(window.mapFromGlobal(QPoint(int(drag_end_x), int(drag_end_y))))
    
    move_event = QMouseEvent(
        QMouseEvent.Type.MouseMove,
        move_local_pos,
        move_global_pos,
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier
    )
    window.mouseMoveEvent(move_event)
    
    # Verify window moved by expected delta
    new_pos = window.pos()
    expected_x = initial_x + drag_delta_x
    expected_y = initial_y + drag_delta_y
    
    # Allow small tolerance for rounding errors
    tolerance = 2
    assert abs(new_pos.x() - expected_x) <= tolerance, (
        f"Window x position should be approximately {expected_x}, got {new_pos.x()} "
        f"(delta: {new_pos.x() - initial_x}, expected delta: {drag_delta_x})"
    )
    assert abs(new_pos.y() - expected_y) <= tolerance, (
        f"Window y position should be approximately {expected_y}, got {new_pos.y()} "
        f"(delta: {new_pos.y() - initial_y}, expected delta: {drag_delta_y})"
    )
    
    # Simulate mouse release
    release_event = QMouseEvent(
        QMouseEvent.Type.MouseButtonRelease,
        move_local_pos,
        move_global_pos,
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier
    )
    window.mouseReleaseEvent(release_event)
    
    # Verify drag position was cleared
    assert window._drag_position is None, (
        "After mouse release, _drag_position should be None"
    )
    
    # Verify window position is stable after release
    final_pos = window.pos()
    assert abs(final_pos.x() - new_pos.x()) <= tolerance, (
        "Window position should not change after mouse release"
    )
    assert abs(final_pos.y() - new_pos.y()) <= tolerance, (
        "Window position should not change after mouse release"
    )


# Feature: unified-design-system, Property 5: Window Dragging Behavior - No Drag Without Press
@given(
    initial_x=st.integers(min_value=100, max_value=500),
    initial_y=st.integers(min_value=100, max_value=500),
    move_delta_x=st.integers(min_value=-200, max_value=200),
    move_delta_y=st.integers(min_value=-200, max_value=200)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_window_no_drag_without_press(qtbot, initial_x: int, initial_y: int,
                                       move_delta_x: int, move_delta_y: int):
    """
    **Validates: Requirements 2.3**
    
    Property: For any frameless styled window, when mouse move events are simulated
    without a preceding mouse press, the window position should not change.
    """
    # Create a styled window
    window = StyledTestWindow()
    window.apply_unified_style()
    
    # Set initial position
    window.move(initial_x, initial_y)
    window.show()
    qtbot.addWidget(window)
    qtbot.waitExposed(window)
    
    # Record initial position
    initial_pos = window.pos()
    
    # Verify drag position is None (no press occurred)
    assert window._drag_position is None, (
        "Before any mouse events, _drag_position should be None"
    )
    
    # Simulate mouse move without press
    from PyQt6.QtCore import QPoint, QPointF, Qt
    from PyQt6.QtGui import QMouseEvent
    
    move_global_pos = QPointF(initial_x + move_delta_x, initial_y + move_delta_y)
    move_local_pos = QPointF(window.mapFromGlobal(QPoint(initial_x + move_delta_x, initial_y + move_delta_y)))
    
    move_event = QMouseEvent(
        QMouseEvent.Type.MouseMove,
        move_local_pos,
        move_global_pos,
        Qt.MouseButton.NoButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier
    )
    window.mouseMoveEvent(move_event)
    
    # Verify window did not move
    final_pos = window.pos()
    assert final_pos.x() == initial_pos.x(), (
        f"Window x position should not change without mouse press. "
        f"Initial: {initial_pos.x()}, Final: {final_pos.x()}"
    )
    assert final_pos.y() == initial_pos.y(), (
        f"Window y position should not change without mouse press. "
        f"Initial: {initial_pos.y()}, Final: {final_pos.y()}"
    )
    
    # Verify drag position is still None
    assert window._drag_position is None, (
        "After mouse move without press, _drag_position should still be None"
    )
