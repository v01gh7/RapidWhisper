# Implementation Plan: Manual Format Selection Hotkey

## Overview

This implementation plan breaks down the manual format selection hotkey feature into discrete coding tasks. Each task builds on previous work and includes testing to validate functionality incrementally. The implementation follows the priority: core functionality first, then UI integration, then configuration and polish.

## Tasks

- [ ] 1. Create FormatSelectionDialog component
  - [x] 1.1 Create ui/format_selection_dialog.py with basic dialog structure
    - Implement QDialog subclass with modal behavior
    - Add basic UI layout (title, list widget, buttons)
    - Implement keyboard navigation (arrow keys, Enter, ESC)
    - _Requirements: 2.1, 2.4, 7.1, 7.2, 7.3, 7.4_
  
  - [x] 1.2 Write property test for keyboard navigation
    - **Property 5: Keyboard navigation works correctly**
    - **Validates: Requirements 7.1, 7.2**
  
  - [x] 1.3 Implement format loading from FormattingConfig
    - Add _load_formats() method to scan config/prompts directory
    - Extract application names from configuration
    - Ensure Universal/_fallback format is always first
    - Add human-readable name formatting
    - _Requirements: 2.2, 2.3, 6.1, 6.2, 6.3_
  
  - [~] 1.4 Write property test for format discovery
    - **Property 6: Format discovery from configuration**
    - **Validates: Requirements 6.1, 6.2**
  
  - [~] 1.5 Write property test for universal format first
    - **Property 3: Format list includes universal format first**
    - **Validates: Requirements 2.2, 6.3**
  
  - [x] 1.6 Implement selection handling and return value
    - Add get_selected_format() method
    - Handle OK button click (accept dialog)
    - Handle Cancel button and ESC key (reject dialog)
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [x] 1.7 Write unit tests for dialog behavior (UPDATED for button grid)
    - Test cancellation returns None
    - Test button click returns selected format
    - Test ESC key behavior
    - Test button styling and grid layout
    - _Requirements: 3.2, 3.3_
  
  - [x] 1.8 Add error handling for format loading failures
    - Handle empty format list (show Universal only)
    - Display error message if loading fails
    - Log errors appropriately
    - _Requirements: 10.1_

- [ ] 2. Extend StateManager for session-scoped manual selection
  - [x] 2.1 Add manual format selection storage to StateManager
    - Add _manual_format_selection attribute
    - Add _current_session_id attribute
    - Implement set_manual_format_selection() method
    - Implement get_manual_format_selection() method
    - Implement clear_manual_format_selection() method
    - _Requirements: 3.1, 8.1, 8.3_
  
  - [x] 2.2 Implement session lifecycle methods
    - Add start_recording_session() method with session ID generation
    - Add end_recording_session() method that clears manual selection
    - Integrate with existing state transitions
    - _Requirements: 4.4, 8.2, 8.4_
  
  - [~] 2.3 Write property test for session scoping
    - **Property 4: Selection is session-scoped**
    - **Validates: Requirements 4.4, 8.1, 8.2, 8.3**
  
  - [~] 2.4 Write unit tests for state management
    - Test manual selection storage and retrieval
    - Test session ID generation
    - Test clearing on session end
    - Test no persistence across app restarts
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [x] 2.5 Add error handling for storage failures
    - Wrap storage operations in try-except
    - Log errors and continue with normal detection
    - _Requirements: 10.3_

- [ ] 3. Checkpoint - Ensure core components work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Extend FormattingModule to check manual selection
  - [x] 4.1 Add StateManager dependency to FormattingModule
    - Update __init__ to accept state_manager parameter
    - Store state_manager as instance variable
    - Update all FormattingModule instantiations in codebase
    - _Requirements: 4.1_
  
  - [x] 4.2 Modify get_active_application_format() for priority checking
    - Add manual selection check as first priority
    - Return manual selection if set
    - Fall through to existing logic if not set
    - Add logging for manual selection usage
    - _Requirements: 4.1, 4.2, 4.3, 3.4_
  
  - [~] 4.3 Write property test for manual selection priority
    - **Property 2: Manual selection has highest priority**
    - **Validates: Requirements 4.1, 4.2, 4.3**
  
  - [~] 4.4 Write unit tests for priority logic
    - Test manual selection overrides fixed format
    - Test manual selection overrides auto-detection
    - Test fallback when no manual selection
    - _Requirements: 4.1, 4.2, 4.3, 4.5_

- [ ] 5. Extend HotkeyManager for format selection hotkey
  - [x] 5.1 Add format selection hotkey registration
    - Implement register_format_selection_hotkey() method
    - Use existing register_hotkey() with callback parameter
    - Store format selection hotkey separately from main hotkey
    - _Requirements: 1.1, 1.2_
  
  - [~] 5.2 Write property test for hotkey triggering
    - **Property 1: Hotkey triggers dialog opening**
    - **Validates: Requirements 1.2, 2.1**
  
  - [x] 5.3 Add error handling for registration failures
    - Try default binding if custom binding fails
    - Log errors and continue without format selection hotkey
    - _Requirements: 1.4, 10.2_
  
  - [~] 5.4 Write unit tests for hotkey registration
    - Test successful registration
    - Test registration failure handling
    - Test default fallback
    - _Requirements: 1.1, 1.2, 1.4_

- [ ] 6. Integrate format selection into main application
  - [x] 6.1 Add format selection hotkey callback to main.py
    - Implement _on_format_selection_hotkey() method
    - Check if recording is active (queue dialog if yes)
    - Show dialog if not recording
    - Handle dialog result and store selection
    - Automatically start recording after selection
    - _Requirements: 1.2, 1.3, 3.1, 3.2_
  
  - [x] 6.2 Implement _show_format_selection_dialog() method
    - Create FormatSelectionDialog instance
    - Execute dialog modally
    - Get selected format from dialog
    - Store selection in StateManager
    - Log selection
    - _Requirements: 2.1, 3.1, 3.2_
  
  - [x] 6.3 Integrate session lifecycle with transcription completion
    - Call state_manager.end_recording_session() in _on_transcription_complete()
    - Ensure manual selection is cleared after each recording
    - _Requirements: 4.4, 8.2_
  
  - [x] 6.4 Register format selection hotkey on app startup
    - Load format_selection_hotkey from config (default: "ctrl+alt+space")
    - Register hotkey with HotkeyManager
    - Pass StateManager to FormattingModule
    - _Requirements: 1.1, 1.2_
  
  - [~] 6.5 Write integration tests for end-to-end flow
    - Test hotkey press → dialog → selection → recording → formatting → clear
    - Test cancellation flow
    - Test queuing during recording
    - _Requirements: 1.2, 1.3, 3.1, 3.2, 3.4, 4.4_
  
  - [~] 6.6 Add error handling for dialog failures
    - Wrap dialog operations in try-except
    - Log errors and continue normal operation
    - Don't block recording functionality
    - _Requirements: 10.4_

- [ ] 7. Checkpoint - Ensure core functionality works end-to-end
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Add format selection hotkey configuration to settings
  - [~] 8.1 Extend SettingsWindow with format hotkey field
    - Add format_hotkey_edit HotkeyInput widget to _create_app_page()
    - Add reset button for format hotkey
    - Add label with tooltip
    - Position below main hotkey configuration
    - _Requirements: 5.1, 5.2_
  
  - [~] 8.2 Implement hotkey validation
    - Add _validate_hotkey() method
    - Check for valid modifiers and key combinations
    - Display error message for invalid hotkeys
    - _Requirements: 5.3, 5.5_
  
  - [~] 8.3 Write property test for hotkey validation
    - **Property 7: Hotkey binding validation**
    - **Validates: Requirements 5.3, 5.4, 5.5**
  
  - [~] 8.4 Add format hotkey to settings save/load
    - Add format_selection_hotkey to _get_values()
    - Add format_selection_hotkey to _set_values()
    - Add format_selection_hotkey to _save_settings()
    - Update config.jsonc with new field
    - _Requirements: 5.4_
  
  - [ ] 8.4 Implement _reset_format_hotkey() method
    - Load current value from config
    - Set in HotkeyInput field
    - Clear focus
    - _Requirements: 5.1_
  
  - [~] 8.5 Write unit tests for settings integration
    - Test field display
    - Test validation
    - Test save/load
    - Test reset button
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 9. Add configuration schema updates
  - [x] 9.1 Update config.jsonc.example with format_selection_hotkey
    - Add "format_selection_hotkey": "ctrl+alt+space" to application section
    - Add comment explaining the setting
    - _Requirements: 5.1_
  
  - [x] 9.2 Update Config class to include format_selection_hotkey
    - Add format_selection_hotkey attribute with default value
    - Update config loading to read this field
    - _Requirements: 5.1_
  
  - [x] 9.3 Update CONFIG_README.md documentation
    - Document format_selection_hotkey setting
    - Explain default value and customization
    - _Requirements: 5.1_

- [ ] 10. Add translation support
  - [x] 10.1 Add English translations to utils/translations/en.json
    - Add "settings.app.format_hotkey" key
    - Add "settings.app.format_hotkey_tooltip" key
    - Add "format_selection.title" key
    - Add "format_selection.select_format" key
    - Add "format_selection.universal_format" key
    - _Requirements: 9.1, 9.2_
  
  - [x] 10.2 Add Russian translations to utils/translations/ru.json
    - Add Russian translations for all new keys
    - Ensure consistency with existing translation style
    - _Requirements: 9.1, 9.2_
  
  - [~] 10.3 Write property test for translation usage
    - **Property 8: Translation system usage**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4**
  
  - [~] 10.4 Write unit tests for translation fallback
    - Test missing translation falls back to English
    - Test format name localization
    - _Requirements: 9.4_

- [ ] 11. Add styling to FormatSelectionDialog
  - [x] 11.1 Apply unified design system styling
    - Use StyledWindowMixin for consistent appearance
    - Apply window opacity from config
    - Add rounded corners and blur effects
    - Match settings window styling
    - _Requirements: 2.4, 2.5_
  
  - [x] 11.2 Style dialog components
    - Style list widget with hover effects
    - Style buttons with cursor changes
    - Add proper spacing and margins
    - Ensure readability with dark theme
    - _Requirements: 2.3_
  
  - [~] 11.3 Write unit tests for dialog appearance
    - Test dialog is modal
    - Test dialog positioning
    - Test styling is applied
    - _Requirements: 2.4, 2.5_

- [ ] 12. Final integration and polish
  - [~] 12.1 Test hotkey re-registration on settings change
    - Verify old hotkey is unregistered
    - Verify new hotkey is registered
    - Test with various hotkey combinations
    - _Requirements: 5.4_
  
  - [~] 12.2 Add logging throughout the feature
    - Log hotkey registration
    - Log dialog opening/closing
    - Log format selection
    - Log session lifecycle events
    - Log errors with appropriate levels
    - _Requirements: 1.4, 10.1, 10.2, 10.3, 10.4_
  
  - [~] 12.3 Write integration tests for settings workflow
    - Test opening settings → changing hotkey → saving → using new hotkey
    - Test validation errors in settings
    - _Requirements: 5.3, 5.4, 5.5_
  
  - [~] 12.4 Update documentation
    - Add feature description to README.md
    - Update docs/hotkeys.md with new hotkey
    - Add usage examples
    - Document configuration options
    - _Requirements: 5.1, 5.2_

- [ ] 13. Final checkpoint - Comprehensive testing
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end workflows
- The implementation follows a bottom-up approach: core components first, then integration, then UI polish
