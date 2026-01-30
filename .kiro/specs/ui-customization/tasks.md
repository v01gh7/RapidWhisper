# Implementation Plan: UI Customization

## Overview

This implementation plan breaks down the UI Customization feature into discrete coding tasks. The approach follows an incremental pattern: first extending the Config system for persistence, then creating the settings UI, then integrating with existing windows, and finally adding translations and tests.

## Tasks

- [x] 1. Extend Config class with UI customization properties
  - Add five new properties to `core/config.py`: window_opacity, font_size_floating_main, font_size_floating_info, font_size_settings_labels, font_size_settings_titles
  - Each property should read from .env with documented defaults and constrain values to valid ranges
  - Implement set_env_value() method to write key-value pairs to .env file
  - _Requirements: 1.1, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.4, 5.1, 5.2, 5.3, 5.4_

- [x] 1.1 Write property tests for Config value constraints
  - **Property 1: Value Range Constraints**
  - **Validates: Requirements 1.1, 2.1, 2.2, 3.1, 3.2, 5.4, 8.2**

- [x] 1.2 Write property test for settings persistence
  - **Property 2: Settings Persistence Round-Trip**
  - **Validates: Requirements 2.4, 5.1, 5.2, 6.3**

- [x] 1.3 Write property test for default value fallback
  - **Property 3: Default Value Fallback**
  - **Validates: Requirements 5.3, 8.3**

- [x] 1.4 Write property test for boundary clamping
  - **Property 7: Boundary Value Clamping**
  - **Validates: Requirements 1.5, 8.2**

- [x] 1.5 Write unit tests for Config class
  - Test each property with default, valid, and invalid values
  - Test set_env_value() creates and updates .env correctly
  - Test boundary values for each setting
  - _Requirements: 1.1, 1.3, 1.5, 2.1, 2.2, 2.3, 3.1, 3.2, 3.4, 5.3, 8.1, 8.2, 8.3_

- [x] 2. Create UI Customization settings page
  - Add _create_ui_customization_page() method to `ui/settings_window.py`
  - Create opacity slider with range 50-255 and numeric label display
  - Create four font size sliders with appropriate ranges and labels
  - Add "Reset to Defaults" button with click handler
  - Integrate page into settings tabs using translation key for title
  - _Requirements: 1.1, 1.4, 2.1, 2.2, 2.5, 3.1, 3.2, 3.5, 4.3, 6.1, 7.1, 7.4, 8.5_

- [x] 2.1 Implement opacity change handler with live preview
  - Create _on_opacity_changed() method that updates label and calls set_env_value()
  - Store reference to FloatingWindow for live preview updates
  - Handle case where FloatingWindow reference is None gracefully
  - _Requirements: 1.2, 1.4, 5.1_

- [x] 2.2 Implement reset to defaults functionality
  - Create _reset_ui_defaults() method that restores all settings to documented defaults
  - Update all UI controls to display default values
  - Write defaults to .env file
  - Trigger live preview update for opacity
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 2.3 Write property test for UI control display consistency
  - **Property 4: UI Control Display Consistency**
  - **Validates: Requirements 1.4, 2.5, 3.5**

- [x] 2.4 Write property test for reset to defaults
  - **Property 6: Reset to Defaults Completeness**
  - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**

- [x] 2.5 Write unit tests for SettingsWindow UI Customization page
  - Test tab is created and added with correct title
  - Test all sliders have correct min/max ranges
  - Test reset button restores all defaults
  - Test all translation keys are used correctly
  - _Requirements: 4.3, 4.4, 7.1, 7.4, 8.5_

- [x] 3. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Integrate opacity control with FloatingWindow
  - Modify `ui/floating_window.py` __init__() to read window_opacity from Config
  - Store opacity in _opacity instance variable
  - Create _apply_opacity() method that updates stylesheet with current opacity
  - Create set_opacity() method for live updates from settings
  - Update paintEvent() to use _opacity for background painting
  - _Requirements: 1.2, 1.3_

- [x] 4.1 Write property test for opacity live preview
  - **Property 5: Opacity Live Preview**
  - **Validates: Requirements 1.2**

- [x] 4.2 Write unit tests for FloatingWindow opacity
  - Test opacity is read from Config on initialization
  - Test set_opacity() updates _opacity field
  - Test set_opacity() triggers repaint
  - Test opacity is applied in stylesheet
  - _Requirements: 1.2, 1.3_

- [x] 5. Integrate font sizes with FloatingWindow components
  - Modify `ui/floating_window.py` to read font_size_floating_main from Config
  - Apply font size to status label in _setup_status_label() or equivalent method
  - Modify `ui/info_panel_widget.py` to read font_size_floating_info from Config
  - Apply font size to app name label and hotkey labels in _setup_ui()
  - _Requirements: 2.3_

- [x] 5.1 Write unit tests for FloatingWindow font sizes
  - Test font sizes are read from Config on initialization
  - Test fonts are applied to status label
  - _Requirements: 2.3_

- [x] 5.2 Write unit tests for InfoPanelWidget font sizes
  - Test font sizes are read from Config on initialization
  - Test fonts are applied to all labels (app name, hotkeys)
  - _Requirements: 2.3_

- [x] 6. Integrate font sizes with SettingsWindow components
  - Modify `ui/settings_window.py` to read font_size_settings_labels and font_size_settings_titles from Config
  - Apply font sizes to all labels and titles in settings window
  - Ensure font sizes are reapplied when settings window reopens
  - _Requirements: 3.3, 3.4_

- [x] 6.1 Write property test for font size persistence
  - **Property 9: Font Size Persistence Across Reopens**
  - **Validates: Requirements 3.3**

- [x] 6.2 Write unit tests for SettingsWindow font sizes
  - Test font sizes are read from Config on initialization
  - Test fonts are applied to labels and titles
  - Test font sizes persist across window close/reopen
  - _Requirements: 3.3, 3.4_

- [x] 7. Add translation keys for English and Russian
  - Add all UI customization translation keys to `utils/translations/en.json`
  - Add all UI customization translation keys to `utils/translations/ru.json`
  - Include keys for: title, window_opacity, window_opacity_tooltip, font_sizes, font_floating_main, font_floating_info, font_settings_labels, font_settings_titles, reset_defaults
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 7.1 Write unit tests for translations
  - Test all required keys exist in en.json
  - Test all required keys exist in ru.json
  - Test English and Russian translations are non-empty strings
  - _Requirements: 4.1, 4.2_

- [x] 8. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Write integration tests for end-to-end flows
  - Test opacity change persists across application restart
  - Test font size changes persist across settings dialog reopen
  - Test reset to defaults affects all settings and persists
  - Test simultaneous changes to multiple settings
  - _Requirements: 1.2, 2.4, 3.3, 5.1, 5.2, 6.1, 6.2, 6.3, 6.4_

- [x] 10. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- All tasks including tests are required for comprehensive implementation
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties with minimum 100 iterations
- Unit tests validate specific examples and edge cases
- The implementation follows the order: Config → Settings UI → FloatingWindow → Translations
- Live preview for opacity changes provides immediate user feedback
- Font size changes require window reopen to take effect
