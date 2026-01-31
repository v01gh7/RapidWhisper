# Implementation Plan: Unified Design System

## Overview

This implementation plan breaks down the unified design system feature into discrete coding tasks. The approach is to first create the reusable design system components (StyleConstants and StyledWindowMixin), then apply them to the Settings Window and Tray Icon, and finally add comprehensive testing.

## Tasks

- [ ] 1. Create design system foundation
  - [x] 1.1 Create `design_system` package directory structure
    - Create `design_system/__init__.py`
    - Set up package for importing StyleConstants and StyledWindowMixin
    - _Requirements: 7.3_

  - [x] 1.2 Implement StyleConstants class
    - Create `design_system/style_constants.py`
    - Define color constants (BACKGROUND_COLOR_RGB, BORDER_COLOR)
    - Define dimension constants (BORDER_RADIUS, BORDER_WIDTH)
    - Define opacity constants (OPACITY_MIN, OPACITY_MAX, OPACITY_DEFAULT)
    - Implement `get_background_color(opacity)` method
    - Implement `clamp_opacity(opacity)` method
    - _Requirements: 7.3, 4.2_

  - [x] 1.3 Write property test for opacity clamping
    - **Property 3: Opacity Clamping**
    - **Validates: Requirements 4.2**
    - Test that any integer value gets clamped to [50, 255]
    - Test boundary conditions (49→50, 256→255)
    - Use Hypothesis to generate random integers

  - [x] 1.4 Write property test for color consistency
    - **Property 7: StyleConstants Color Consistency**
    - **Validates: Requirements 1.1, 3.3**
    - Test that `get_background_color()` always returns correct format
    - Verify RGB values are (30, 30, 30)
    - Use Hypothesis to generate random opacity values (50-255)

- [ ] 2. Implement StyledWindowMixin
  - [x] 2.1 Create StyledWindowMixin class
    - Create `design_system/styled_window_mixin.py`
    - Implement `__init__()` with drag position and opacity state
    - Implement `apply_unified_style()` method
    - Set window flags (FramelessWindowHint, optional WindowStaysOnTopHint)
    - Set WA_TranslucentBackground attribute
    - Call `_apply_stylesheet()` and `_apply_blur()`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 7.1_

  - [x] 2.2 Implement stylesheet generation
    - Implement `_apply_stylesheet()` method
    - Generate QSS with background color, border, and border-radius
    - Use StyleConstants for all values
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 2.3 Implement blur effect integration
    - Implement `_apply_blur()` method
    - Import and call `apply_blur_effect()` from `utils.platform_utils`
    - Handle exceptions gracefully (graceful degradation)
    - _Requirements: 1.4, 6.1_

  - [x] 2.4 Implement dynamic opacity updates
    - Implement `update_opacity(opacity)` method
    - Clamp the new opacity value
    - Regenerate and apply stylesheet
    - _Requirements: 4.1_

  - [x] 2.5 Implement window dragging functionality
    - Implement `mousePressEvent()` to capture drag start position
    - Implement `mouseMoveEvent()` to move window during drag
    - Implement `mouseReleaseEvent()` to end drag
    - Ensure super() calls to preserve existing behavior
    - _Requirements: 2.3_

  - [x] 2.6 Write property test for dynamic opacity updates
    - **Property 4: Dynamic Opacity Updates**
    - **Validates: Requirements 4.1**
    - Create test window instances with random initial opacity
    - Call `update_opacity()` with random new values
    - Verify stylesheet contains new opacity
    - Use Hypothesis to generate opacity pairs

  - [x] 2.7 Write property test for window dragging
    - **Property 5: Window Dragging Behavior**
    - **Validates: Requirements 2.3**
    - Create test window at random initial position
    - Simulate mouse press, move, and release events
    - Verify window position changes by expected delta
    - Use pytest-qt for Qt event simulation

- [ ] 3. Checkpoint - Verify design system foundation
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Update Settings Window
  - [x] 4.1 Refactor SettingsWindow to use StyledWindowMixin
    - Modify `ui/settings_window.py`
    - Add StyledWindowMixin to class inheritance
    - Call both `__init__` methods properly
    - Remove old styling code (if any)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2_

  - [x] 4.2 Apply unified styling in Settings Window initialization
    - Get opacity from `config.window_opacity`
    - Call `apply_unified_style(opacity=opacity, stay_on_top=False)`
    - Handle missing config with default value
    - _Requirements: 1.5, 4.3_

  - [x] 4.3 Create draggable header for Settings Window
    - Implement `_create_header()` method
    - Create QWidget with fixed height (30px)
    - Style header with slightly different background for visual distinction
    - Add header to top of layout
    - _Requirements: 2.3_

  - [x] 4.4 Implement opacity change handler
    - Implement `on_opacity_changed(new_opacity)` method
    - Call `update_opacity()` from mixin
    - Connect to opacity slider signal (if exists)
    - _Requirements: 4.1_

  - [x] 4.5 Write property test for Settings Window stylesheet
    - **Property 1: Settings Window Stylesheet Application**
    - **Validates: Requirements 1.1, 1.2, 1.3**
    - Create Settings Window with random opacity values
    - Verify stylesheet contains correct background color
    - Verify stylesheet contains 5px border-radius
    - Verify stylesheet contains 2px border
    - Use Hypothesis to generate opacity values

  - [x] 4.6 Write property test for Settings Window config opacity
    - **Property 2: Settings Window Uses Config Opacity**
    - **Validates: Requirements 1.5**
    - Create config objects with random opacity values
    - Create Settings Windows with those configs
    - Verify stylesheet reflects config opacity
    - Use Hypothesis to generate config variations

  - [x] 4.7 Write unit tests for Settings Window integration
    - Test that window flags include FramelessWindowHint
    - Test that WA_TranslucentBackground attribute is set
    - Test that blur effect is called during initialization
    - Test missing config opacity uses default
    - Mock `apply_blur_effect` to verify it's called

- [ ] 5. Update Tray Icon menu
  - [x] 5.1 Refactor TrayIcon to apply custom menu styling
    - Modify `ui/tray_icon.py`
    - Implement `_create_styled_menu()` method
    - Create QMenu instance
    - _Requirements: 3.1, 3.2, 3.3_

  - [x] 5.2 Generate and apply menu stylesheet
    - Use StyleConstants for colors and dimensions
    - Set menu opacity (slightly higher for readability, e.g., 200)
    - Generate QSS for QMenu with background, border, border-radius
    - Generate QSS for QMenu::item with padding and color
    - Generate QSS for QMenu::item:selected (hover state)
    - Generate QSS for QMenu::item:pressed (pressed state)
    - Generate QSS for QMenu::separator
    - Apply stylesheet to menu
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [x] 5.3 Preserve existing menu functionality
    - Add all existing menu items to styled menu
    - Ensure all menu actions are connected correctly
    - Set the styled menu as context menu
    - _Requirements: 5.2, 5.4_

  - [x] 5.4 Write property test for Tray menu stylesheet
    - **Property 6: Tray Menu Stylesheet Application**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
    - Create TrayIcon instances
    - Verify menu stylesheet contains background color with StyleConstants
    - Verify menu stylesheet contains border-radius
    - Verify menu stylesheet contains hover state definitions
    - Test that menu items are preserved

  - [x] 5.5 Write unit tests for Tray Icon menu
    - Test that menu is created with correct styling
    - Test that all menu items are present
    - Test that menu actions are connected
    - Test hover state CSS is present in stylesheet

- [ ] 6. Final checkpoint and integration testing
  - [x] 6.1 Verify all windows use consistent styling
    - Manually test Settings Window appearance
    - Manually test Tray Icon menu appearance
    - Compare with Floating Window for consistency
    - _Requirements: 1.1, 1.2, 1.3, 3.1, 3.2, 3.3_

  - [x] 6.2 Write integration tests
    - Test that Settings Window can be opened and closed
    - Test that opacity changes affect Settings Window
    - Test that Tray Icon menu displays correctly
    - Test that all existing functionality is preserved
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 6.3 Final checkpoint - Ensure all tests pass
    - Run all unit tests
    - Run all property tests
    - Run integration tests
    - Ensure all tests pass, ask the user if questions arise.

## Notes

- All tasks are required for comprehensive implementation
- Each task references specific requirements for traceability
- Property tests use Hypothesis library with minimum 100 iterations
- Qt-specific tests use pytest-qt for event simulation
- The mixin pattern allows easy reuse for future windows
- Graceful degradation ensures functionality on all platforms
