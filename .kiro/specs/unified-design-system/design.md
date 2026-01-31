# Design Document: Unified Design System

## Overview

This design implements a unified visual design system for the RapidWhisper application by extracting the modern styling from the Floating Window and applying it consistently to the Settings Window and Tray Icon menu. The design focuses on creating a reusable styling mechanism that can be easily applied to any window in the application.

The core approach is to:
1. Create a reusable `StyledWindowMixin` class that encapsulates all visual styling logic
2. Apply this mixin to the Settings Window
3. Create custom QSS (Qt Style Sheets) for the Tray Icon menu
4. Ensure all styling respects the `window_opacity` configuration setting

## Architecture

### Component Structure

```
RapidWhisper Application
├── UI Components
│   ├── Floating Window (existing, reference implementation)
│   ├── Settings Window (to be updated)
│   └── Tray Icon (to be updated)
├── Design System
│   ├── StyledWindowMixin (new)
│   └── StyleConstants (new)
└── Utils
    └── platform_utils.py (existing)
```

### Design Pattern

We will use a **Mixin Pattern** to provide reusable styling functionality:
- `StyledWindowMixin`: A mixin class that provides methods for applying the unified design
- Windows inherit from both their base class and the mixin
- The mixin handles window flags, attributes, styling, and blur effects

### Styling Approach

1. **Window-level styling**: Applied via Qt window flags and attributes
2. **Widget-level styling**: Applied via QSS (Qt Style Sheets)
3. **Platform-specific effects**: Applied via `apply_blur_effect()` utility

## Components and Interfaces

### 1. StyleConstants Class

A centralized location for all design system constants:

```python
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
        """Get background color with specified opacity"""
        r, g, b = StyleConstants.BACKGROUND_COLOR_RGB
        return f"rgba({r}, {g}, {b}, {opacity})"
    
    @staticmethod
    def clamp_opacity(opacity: int) -> int:
        """Clamp opacity to valid range"""
        return max(StyleConstants.OPACITY_MIN, 
                   min(StyleConstants.OPACITY_MAX, opacity))
```

### 2. StyledWindowMixin Class

A mixin that provides unified styling functionality:

```python
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QWidget

class StyledWindowMixin:
    """Mixin to apply unified design system styling to windows"""
    
    def __init__(self):
        self._drag_position = None
        self._opacity = StyleConstants.OPACITY_DEFAULT
    
    def apply_unified_style(self, opacity: int = None, stay_on_top: bool = False):
        """
        Apply the unified design system styling to this window
        
        Args:
            opacity: Window opacity (50-255), uses config default if None
            stay_on_top: Whether window should stay on top
        """
        # Set opacity
        if opacity is not None:
            self._opacity = StyleConstants.clamp_opacity(opacity)
        
        # Set window flags
        flags = Qt.WindowType.FramelessWindowHint
        if stay_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        
        # Enable translucent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Apply stylesheet
        self._apply_stylesheet()
        
        # Apply platform-specific blur effect
        self._apply_blur()
    
    def _apply_stylesheet(self):
        """Apply QSS styling to the window"""
        bg_color = StyleConstants.get_background_color(self._opacity)
        
        stylesheet = f"""
            QWidget {{
                background-color: {bg_color};
                border: {StyleConstants.BORDER_WIDTH}px solid {StyleConstants.BORDER_COLOR};
                border-radius: {StyleConstants.BORDER_RADIUS}px;
            }}
        """
        self.setStyleSheet(stylesheet)
    
    def _apply_blur(self):
        """Apply platform-specific blur effect"""
        from utils.platform_utils import apply_blur_effect
        apply_blur_effect(self)
    
    def update_opacity(self, opacity: int):
        """Update window opacity dynamically"""
        self._opacity = StyleConstants.clamp_opacity(opacity)
        self._apply_stylesheet()
    
    # Drag functionality for frameless windows
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_position is not None:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release to end dragging"""
        self._drag_position = None
        super().mouseReleaseEvent(event)
```

### 3. Updated Settings Window

The Settings Window will inherit from both `QWidget` and `StyledWindowMixin`:

```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from design_system.styled_window_mixin import StyledWindowMixin
from design_system.style_constants import StyleConstants

class SettingsWindow(QWidget, StyledWindowMixin):
    """Settings window with unified design system styling"""
    
    def __init__(self, config):
        QWidget.__init__(self)
        StyledWindowMixin.__init__(self)
        
        self.config = config
        
        # Apply unified styling
        opacity = config.get('window_opacity', StyleConstants.OPACITY_DEFAULT)
        self.apply_unified_style(opacity=opacity, stay_on_top=False)
        
        # Set up UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the settings UI components"""
        layout = QVBoxLayout()
        
        # Add a draggable header area
        header = self._create_header()
        layout.addWidget(header)
        
        # Add existing settings controls
        # ... (existing settings UI code)
        
        self.setLayout(layout)
    
    def _create_header(self):
        """Create a draggable header for the frameless window"""
        header = QWidget()
        header.setFixedHeight(30)
        # Style the header to be visually distinct
        header.setStyleSheet("""
            QWidget {
                background-color: rgba(40, 40, 40, 200);
                border: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
        """)
        return header
    
    def on_opacity_changed(self, new_opacity: int):
        """Handle opacity changes from settings"""
        self.update_opacity(new_opacity)
```

### 4. Updated Tray Icon Menu

The Tray Icon menu will use custom QSS styling:

```python
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from design_system.style_constants import StyleConstants

class TrayIcon(QSystemTrayIcon):
    """System tray icon with styled menu"""
    
    def __init__(self, icon, parent=None):
        super().__init__(icon, parent)
        self.menu = self._create_styled_menu()
        self.setContextMenu(self.menu)
    
    def _create_styled_menu(self):
        """Create a menu with unified design system styling"""
        menu = QMenu()
        
        # Apply custom stylesheet
        opacity = 200  # Slightly more opaque for readability
        bg_color = StyleConstants.get_background_color(opacity)
        
        stylesheet = f"""
            QMenu {{
                background-color: {bg_color};
                border: {StyleConstants.BORDER_WIDTH}px solid {StyleConstants.BORDER_COLOR};
                border-radius: {StyleConstants.BORDER_RADIUS}px;
                padding: 5px;
            }}
            
            QMenu::item {{
                padding: 8px 25px;
                border-radius: 3px;
                color: #ffffff;
            }}
            
            QMenu::item:selected {{
                background-color: rgba(70, 70, 70, 200);
            }}
            
            QMenu::item:pressed {{
                background-color: rgba(90, 90, 90, 200);
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: rgba(255, 255, 255, 50);
                margin: 5px 10px;
            }}
        """
        
        menu.setStyleSheet(stylesheet)
        
        # Add menu items (existing functionality)
        # ... (existing menu items code)
        
        return menu
```

## Data Models

### Configuration Schema

The existing configuration already includes the `window_opacity` setting. No changes to the data model are required, but we document it here for completeness:

```python
{
    "window_opacity": int,  # Range: 50-255, Default: 150
    # ... other config fields
}
```

### Style State

The mixin maintains minimal internal state:

```python
{
    "_drag_position": QPoint | None,  # Current drag position for window movement
    "_opacity": int  # Current opacity value (50-255)
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Settings Window Stylesheet Application

*For any* Settings Window instance with a given opacity value, the applied stylesheet should contain the correct background color with that opacity, a 5px border-radius, and a 2px semi-transparent white border.

**Validates: Requirements 1.1, 1.2, 1.3**

### Property 2: Settings Window Uses Config Opacity

*For any* valid opacity value in the configuration (50-255), when a Settings Window is created with that config, the resulting background color in the stylesheet should reflect that exact opacity value.

**Validates: Requirements 1.5**

### Property 3: Opacity Clamping

*For any* integer opacity value (including values outside the valid range), when passed to `clamp_opacity()`, the result should be within the range [50, 255], with values below 50 clamped to 50 and values above 255 clamped to 255.

**Validates: Requirements 4.2**

### Property 4: Dynamic Opacity Updates

*For any* styled window with an initial opacity, when `update_opacity()` is called with a new valid opacity value, the window's stylesheet should be updated to reflect the new opacity in the background color.

**Validates: Requirements 4.1**

### Property 5: Window Dragging Behavior

*For any* frameless styled window, when mouse press, move, and release events are simulated with valid coordinates, the window position should change to follow the mouse movement delta.

**Validates: Requirements 2.3**

### Property 6: Tray Menu Stylesheet Application

*For any* Tray Icon menu instance, the applied stylesheet should contain a semi-transparent dark background using StyleConstants colors, rounded corners, and hover state definitions for menu items.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

### Property 7: StyleConstants Color Consistency

*For any* opacity value, the background color generated by `StyleConstants.get_background_color(opacity)` should use the RGB values (30, 30, 30) and format them as `rgba(30, 30, 30, {opacity})`.

**Validates: Requirements 1.1, 3.3**

## Error Handling

### Blur Effect Failures

If the platform-specific blur effect fails to apply (e.g., on unsupported platforms or due to system limitations):
- The `apply_blur_effect()` utility should handle exceptions gracefully
- The window should still display with the semi-transparent background
- No error should be shown to the user
- The application should continue functioning normally

### Invalid Opacity Values

If invalid opacity values are provided:
- Values below 50 are clamped to 50
- Values above 255 are clamped to 255
- Non-integer values should be converted to integers
- The `clamp_opacity()` method ensures all values are valid

### Missing Configuration

If the `window_opacity` configuration value is missing:
- Use `StyleConstants.OPACITY_DEFAULT` (150) as the fallback
- Log a warning about the missing configuration
- Continue with default styling

### Window Flag Conflicts

If there are conflicts with window flags (e.g., on certain platforms):
- The mixin should apply flags in a safe order
- If FramelessWindowHint causes issues, the window should still be functional
- Platform-specific workarounds should be documented

## Testing Strategy

### Unit Testing

Unit tests will focus on:

1. **StyleConstants validation**:
   - Verify color constants are correct
   - Test `get_background_color()` formatting
   - Test `clamp_opacity()` boundary conditions

2. **StyledWindowMixin initialization**:
   - Verify window flags are set correctly
   - Verify attributes are set correctly
   - Verify blur effect is called

3. **Stylesheet generation**:
   - Verify correct QSS is generated for different opacity values
   - Verify all required style properties are present

4. **Settings Window integration**:
   - Verify Settings Window applies the mixin correctly
   - Verify header is created and styled
   - Verify opacity changes are handled

5. **Tray Icon menu styling**:
   - Verify menu stylesheet is applied
   - Verify menu items have correct styling

### Property-Based Testing

Property-based tests will verify universal properties across randomized inputs. Each test should run a minimum of 100 iterations.

1. **Property 1: Settings Window Stylesheet Application**
   - Generate random opacity values (50-255)
   - Create Settings Window instances
   - Verify stylesheet contains all required properties
   - **Tag: Feature: unified-design-system, Property 1: Settings Window Stylesheet Application**

2. **Property 2: Settings Window Uses Config Opacity**
   - Generate random valid opacity values
   - Create config objects with those values
   - Create Settings Windows with those configs
   - Verify stylesheet reflects the config opacity
   - **Tag: Feature: unified-design-system, Property 2: Settings Window Uses Config Opacity**

3. **Property 3: Opacity Clamping**
   - Generate random integers (including negative and very large values)
   - Apply `clamp_opacity()`
   - Verify result is always in [50, 255]
   - Verify values < 50 become 50
   - Verify values > 255 become 255
   - **Tag: Feature: unified-design-system, Property 3: Opacity Clamping**

4. **Property 4: Dynamic Opacity Updates**
   - Generate random initial and new opacity values
   - Create styled windows
   - Call `update_opacity()` with new values
   - Verify stylesheet is updated correctly
   - **Tag: Feature: unified-design-system, Property 4: Dynamic Opacity Updates**

5. **Property 5: Window Dragging Behavior**
   - Generate random initial window positions
   - Generate random mouse movement deltas
   - Simulate drag events
   - Verify window moves by the expected delta
   - **Tag: Feature: unified-design-system, Property 5: Window Dragging Behavior**

6. **Property 6: Tray Menu Stylesheet Application**
   - Create Tray Icon instances
   - Verify menu stylesheet contains background color
   - Verify menu stylesheet contains border-radius
   - Verify menu stylesheet contains hover states
   - **Tag: Feature: unified-design-system, Property 6: Tray Menu Stylesheet Application**

7. **Property 7: StyleConstants Color Consistency**
   - Generate random opacity values (50-255)
   - Call `get_background_color()` for each
   - Verify format is exactly `rgba(30, 30, 30, {opacity})`
   - **Tag: Feature: unified-design-system, Property 7: StyleConstants Color Consistency**

### Testing Framework

- **Unit Testing**: pytest
- **Property-Based Testing**: Hypothesis (Python property-based testing library)
- **Qt Testing**: pytest-qt for Qt-specific testing utilities
- **Mocking**: unittest.mock for mocking platform-specific functions

### Test Configuration

```python
# pytest configuration
# Minimum 100 iterations for property tests
@given(opacity=st.integers(min_value=50, max_value=255))
@settings(max_examples=100)
def test_property_example(opacity):
    # Property test implementation
    pass
```

### Integration Testing

Integration tests will verify:
- Settings Window can be opened, styled, and closed
- Tray Icon menu can be displayed with correct styling
- Opacity changes propagate correctly through the UI
- All windows maintain consistent styling
- Drag functionality works across different screen configurations

### Manual Testing Checklist

Due to the visual nature of this feature, manual testing is important:
- [ ] Settings Window appears with correct transparency and blur
- [ ] Settings Window has rounded corners
- [ ] Settings Window has semi-transparent white border
- [ ] Settings Window can be dragged by the header
- [ ] Tray Icon menu has modern dark styling
- [ ] Tray Icon menu items have hover effects
- [ ] Opacity slider in settings updates all windows in real-time
- [ ] Visual consistency across all windows
- [ ] Blur effect works on Windows
- [ ] Graceful degradation on non-Windows platforms
