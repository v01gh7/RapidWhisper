"""
StyleConstants - Centralized design system constants

This module provides a centralized location for all design system constants
used throughout the RapidWhisper application, including colors, dimensions,
and opacity values.
"""


class StyleConstants:
    """Centralized design system constants"""
    
    # Colors
    BACKGROUND_COLOR_RGB = (30, 30, 30)  # Dark gray
    BORDER_COLOR = "rgba(255, 255, 255, 100)"  # Semi-transparent white
    
    # Dimensions
    BORDER_RADIUS = 5  # pixels
    BORDER_WIDTH = 2  # pixels
    
    # Opacity
    OPACITY_MIN = 50
    OPACITY_MAX = 255
    OPACITY_DEFAULT = 150
    
    @staticmethod
    def get_background_color(opacity: int) -> str:
        """
        Get background color with specified opacity
        
        Args:
            opacity: Opacity value (0-255)
            
        Returns:
            RGBA color string in format "rgba(r, g, b, opacity)"
        """
        r, g, b = StyleConstants.BACKGROUND_COLOR_RGB
        return f"rgba({r}, {g}, {b}, {opacity})"
    
    @staticmethod
    def clamp_opacity(opacity: int) -> int:
        """
        Clamp opacity to valid range
        
        Args:
            opacity: Opacity value to clamp
            
        Returns:
            Clamped opacity value in range [OPACITY_MIN, OPACITY_MAX]
        """
        return max(StyleConstants.OPACITY_MIN, 
                   min(StyleConstants.OPACITY_MAX, opacity))
