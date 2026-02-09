"""
StyledWindowMixin - Mixin for applying unified design system styling to windows

This module provides a mixin class that encapsulates all visual styling logic
for windows in the RapidWhisper application, including frameless window setup,
translucent backgrounds, blur effects, and drag functionality.
"""

from PyQt6.QtCore import Qt, QPoint, QRectF
from PyQt6.QtGui import QPainterPath, QRegion
from PyQt6.QtWidgets import QWidget
from .style_constants import StyleConstants
from .window_themes import DEFAULT_WINDOW_THEME_ID, get_window_theme


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
        self._corner_radius = int(StyleConstants.BORDER_RADIUS)
        self._native_blur_enabled = True
        self._force_opaque_surface = False
        self._window_theme_id = DEFAULT_WINDOW_THEME_ID
        self._window_theme = get_window_theme(self._window_theme_id)
    
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
        # Keep windows fully opaque in the current theme model.
        self._opacity = 255
        self._corner_radius = int(StyleConstants.BORDER_RADIUS)

        cfg = getattr(self, "config", None)
        theme_id = getattr(cfg, "window_theme", self._window_theme_id)
        self.set_window_theme(theme_id, sync_surface=False)
        
        # Configure window surface.
        self.configure_translucent_surface(translucent=not self._force_opaque_surface)
        
        # Set window flags while preserving existing window type (Dialog/Tool/Window).
        base_type = self.windowFlags() & (
            Qt.WindowType.Window |
            Qt.WindowType.Dialog |
            Qt.WindowType.Tool |
            Qt.WindowType.Popup |
            Qt.WindowType.Sheet
        )
        if base_type == Qt.WindowType(0):
            base_type = Qt.WindowType.Window
        flags = (
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.NoDropShadowWindowHint |
            base_type
        )
        if stay_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        
        # Apply stylesheet
        self._apply_stylesheet()
        
        # Apply rounded mask + platform blur in one place.
        self.sync_rounded_surface()

    def configure_translucent_surface(self, corner_radius: int | None = None, translucent: bool = True):
        """
        Configure native surface attributes for transparent rounded windows.
        """
        if corner_radius is not None:
            self._corner_radius = int(corner_radius)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, bool(translucent))
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, bool(translucent))
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, not bool(translucent))
        if hasattr(self, "setAutoFillBackground"):
            self.setAutoFillBackground(not bool(translucent))

    def apply_rounded_mask(self, corner_radius: int | None = None):
        """
        Apply real rounded window region (OS-level shape).
        """
        if corner_radius is not None:
            self._corner_radius = int(corner_radius)

        # On Windows, native rounded region is applied via Win32 SetWindowRgn
        # inside blur path. Qt polygon mask can look jagged for translucent windows.
        try:
            from utils.platform_utils import is_windows
            if is_windows() and getattr(self, "_native_blur_enabled", True):
                self.clearMask()
                return
        except Exception:
            pass

        rect_f = QRectF(self.rect())
        if rect_f.width() <= 0 or rect_f.height() <= 0:
            return

        path = QPainterPath()
        path.addRoundedRect(rect_f, float(self._corner_radius), float(self._corner_radius))
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def sync_rounded_surface(self, corner_radius: int | None = None):
        """
        Keep rounded mask and native blur in sync with current window geometry.
        """
        self.apply_rounded_mask(corner_radius)
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
        theme = self._window_theme
        
        stylesheet = f"""
            QWidget, QDialog {{
                background-color: {theme["window_bg"]};
                border: {StyleConstants.BORDER_WIDTH}px solid {theme["window_border"]};
                border-radius: {StyleConstants.BORDER_RADIUS}px;
                color: {theme["text_primary"]};
                font-family: '{theme["font_family"]}';
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
        if not getattr(self, "_native_blur_enabled", True):
            return
        if not self.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground):
            return

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
        self._opacity = 255
        self._apply_stylesheet()
        self.sync_rounded_surface()

    def set_window_theme(self, theme_id: str | None, sync_surface: bool = True) -> None:
        """Applies the selected window theme to the mixin-managed base style."""
        self._window_theme_id = theme_id or DEFAULT_WINDOW_THEME_ID
        self._window_theme = get_window_theme(self._window_theme_id)
        self._apply_stylesheet()
        if sync_surface:
            self.sync_rounded_surface()
    
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
