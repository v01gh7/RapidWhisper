"""
Unified Design System Package

This package provides reusable styling components for the RapidWhisper application,
ensuring visual consistency across all windows and UI elements.

Components:
- StyleConstants: Centralized design system constants (colors, dimensions, opacity)
- StyledWindowMixin: Mixin class for applying unified window styling

Usage:
    from design_system import StyleConstants, StyledWindowMixin
    
    class MyWindow(QWidget, StyledWindowMixin):
        def __init__(self):
            QWidget.__init__(self)
            StyledWindowMixin.__init__(self)
            
            opacity = StyleConstants.OPACITY_DEFAULT
            self.apply_unified_style(opacity=opacity)
"""

# Package imports will be added as components are implemented
from .style_constants import StyleConstants
from .styled_window_mixin import StyledWindowMixin
from .window_themes import (
    DEFAULT_WINDOW_THEME_ID,
    get_window_theme,
    get_window_theme_ids,
    get_window_theme_name_key,
)

__all__ = [
    'StyleConstants',
    'StyledWindowMixin',
    'DEFAULT_WINDOW_THEME_ID',
    'get_window_theme',
    'get_window_theme_ids',
    'get_window_theme_name_key',
]

__version__ = '1.0.0'
