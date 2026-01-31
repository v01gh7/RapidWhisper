"""
StyledWindowMixin - Mixin for applying unified design system styling to windows

This module provides a mixin class that encapsulates all visual styling logic
for windows in the RapidWhisper application, including frameless window setup,
translucent backgrounds, blur effects, and drag functionality.
"""

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QWidget
from .style_constants import StyleConstants


class StyledWindowMixin:
    """Mixin to apply unified design system styling to windows"""
    
    def __init__(self):
        """
        Initialize the mixin with default state
        
        Sets up:
        - Drag position tracking for frameless window movement
        - Default opacity value
        """
        self._drag_position = None
        self._opacity = StyleConstants.OPACITY_DEFAULT
    
    def apply_unified_style(self, opacity: int = None, stay_on_top: bool = False):
        """
        Apply the unified design system styling to this window
        
        This method configures the window with:
        - Frameless window flags
        - Optional stay-on-top behavior
        - Custom stylesheet with rounded corners and borders
        - Platform-specific blur effects
        
        NOTE: WA_TranslucentBackground should be set BEFORE calling this method
        for proper rendering on Windows.
        
        Args:
            opacity: Window opacity (50-255), uses config default if None
            stay_on_top: Whether window should stay on top of other windows
        """
        # Set opacity
        if opacity is not None:
            self._opacity = StyleConstants.clamp_opacity(opacity)
        
        # Set window flags
        flags = Qt.WindowType.FramelessWindowHint
        if stay_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        
        # Apply stylesheet
        self._apply_stylesheet()
        
        # Apply platform-specific blur effect
        self._apply_blur()
    
    def _apply_stylesheet(self):
        """
        Apply QSS styling to the window
        
        Generates and applies a stylesheet with:
        - Semi-transparent background color
        - Rounded corners (border-radius)
        - Semi-transparent white border
        
        NOTE: We target both QWidget and QDialog to ensure the style applies
        to all window types (QDialog, QWidget, etc.)
        """
        bg_color = StyleConstants.get_background_color(self._opacity)
        
        stylesheet = f"""
            QWidget, QDialog {{
                background-color: {bg_color};
                border: {StyleConstants.BORDER_WIDTH}px solid {StyleConstants.BORDER_COLOR};
                border-radius: {StyleConstants.BORDER_RADIUS}px;
            }}
        """
        self.setStyleSheet(stylesheet)
    
    def _apply_blur(self):
        """
        Apply platform-specific blur effect
        
        Calls the platform utility to apply blur effects like
        Windows Acrylic or Mica. Handles exceptions gracefully
        for unsupported platforms.
        
        Requirements: 1.4, 6.1
        """
        try:
            from utils.platform_utils import apply_blur_effect
            from utils.logger import get_logger
            logger = get_logger()
            
            success = apply_blur_effect(self)
            if success:
                logger.debug("Blur effect applied successfully")
            else:
                logger.debug("Blur effect not applied (platform may not support it)")
        except Exception as e:
            # Graceful degradation - if blur effect fails, continue without it
            # The window will still have the semi-transparent background
            from utils.logger import get_logger
            logger = get_logger()
            logger.debug(f"Failed to apply blur effect: {e}")
    
    def update_opacity(self, opacity: int):
        """
        Update window opacity dynamically
        
        Args:
            opacity: New opacity value (50-255)
        
        Requirements: 4.1
        """
        self._opacity = StyleConstants.clamp_opacity(opacity)
        self._apply_stylesheet()
    
    # Drag functionality for frameless windows
    
    def mousePressEvent(self, event):
        """
        Handle mouse press for window dragging
        
        Captures the initial drag position when the left mouse button is pressed,
        allowing the frameless window to be moved by the user.
        
        Args:
            event: Mouse press event
        
        Requirements: 2.3
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        # Call parent's mousePressEvent if it exists
        if hasattr(super(), 'mousePressEvent'):
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """
        Handle mouse move for window dragging
        
        Moves the window to follow the mouse cursor when the left button is held
        and a drag operation is in progress.
        
        Args:
            event: Mouse move event
        
        Requirements: 2.3
        """
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_position is not None:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
        # Call parent's mouseMoveEvent if it exists
        if hasattr(super(), 'mouseMoveEvent'):
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release to end dragging
        
        Resets the drag position to None, ending the drag operation.
        
        Args:
            event: Mouse release event
        
        Requirements: 2.3
        """
        self._drag_position = None
        # Call parent's mouseReleaseEvent if it exists
        if hasattr(super(), 'mouseReleaseEvent'):
            super().mouseReleaseEvent(event)
