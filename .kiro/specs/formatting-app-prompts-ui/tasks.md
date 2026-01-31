# Implementation Plan: Formatting Settings UI Improvements

## Overview

This implementation plan breaks down the formatting settings UI improvements into discrete, incremental coding tasks. Each task builds on previous work and includes testing to validate functionality early. The implementation follows the design document and ensures all requirements are met.

## Tasks

- [x] 1. Extend FormattingConfig data model for per-application prompts
  - Add `app_prompts: Dict[str, str]` field to FormattingConfig dataclass
  - Implement `get_prompt_for_app(app_name: str) -> str` method
  - Implement `set_prompt_for_app(app_name: str, prompt: str) -> None` method
  - Define `UNIVERSAL_DEFAULT_PROMPT` constant
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 6.1_

- [x] 1.1 Write property test for prompt storage isolation
  - **Property 9: Unique Prompt Storage**
  - **Validates: Requirements 5.1, 5.3**

- [x] 1.2 Write property test for default prompt assignment
  - **Property 10: Default Prompt Assignment**
  - **Validates: Requirements 5.2, 6.2**

- [x] 1.3 Write property test for correct prompt retrieval
  - **Property 11: Correct Prompt Retrieval**
  - **Validates: Requirements 5.4**

- [x] 2. Implement JSON serialization and migration logic
  - Update `to_env()` to serialize app_prompts to JSON string
  - Update `from_env()` to deserialize JSON from FORMATTING_APP_PROMPTS
  - Implement migration logic from old FORMATTING_APPLICATIONS format
  - Add `migrate_from_old_format(applications_str: str)` helper function
  - Handle missing or invalid JSON gracefully with fallback to defaults
  - _Requirements: 7.1, 7.2, 7.3, 7.5, 10.1, 10.2, 10.3, 10.5_

- [x] 2.1 Write property test for configuration round-trip
  - **Property 12: Configuration Round-Trip**
  - **Validates: Requirements 7.1, 7.3**

- [x] 2.2 Write property test for persistent storage location
  - **Property 13: Persistent Storage Location**
  - **Validates: Requirements 7.2**

- [x] 2.3 Write property test for migration preserves applications
  - **Property 14: Migration Preserves Applications**
  - **Validates: Requirements 7.5, 10.1, 10.2, 10.3**

- [x] 2.4 Write property test for migration cleanup
  - **Property 15: Migration Cleanup**
  - **Validates: Requirements 10.5**

- [x] 2.5 Write unit tests for migration edge cases
  - Test empty old format string
  - Test malformed JSON in new format
  - Test missing .env file

- [x] 3. Create PromptEditDialog component
  - Create new class `PromptEditDialog(QDialog)` in ui/settings_window.py
  - Add application name label (read-only)
  - Add QTextEdit for prompt editing (200px height)
  - Add Save and Cancel buttons with localization
  - Implement `get_prompt() -> str` method
  - Implement static `edit_prompt(app_name, current_prompt, parent) -> Optional[str]` method
  - Apply consistent styling matching existing dialogs
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [x] 3.1 Write property test for save persists changes
  - **Property 7: Save Persists Prompt Changes**
  - **Validates: Requirements 4.5**

- [x] 3.2 Write property test for cancel discards changes
  - **Property 8: Cancel Discards Changes**
  - **Validates: Requirements 4.6**

- [x] 3.3 Write unit tests for dialog behavior
  - Test dialog displays application name correctly
  - Test dialog pre-populates with current prompt
  - Test Save button returns edited text
  - Test Cancel button returns None

- [x] 4. Create AddApplicationDialog component
  - Create new class `AddApplicationDialog(QDialog)` in ui/settings_window.py
  - Add QLineEdit for application name input
  - Add QTextEdit for prompt input (pre-filled with universal default)
  - Add Add and Cancel buttons with localization
  - Implement validation for empty names
  - Implement validation for duplicate names
  - Implement `get_application_data() -> Tuple[str, str]` method
  - Implement static `add_application(existing_apps, default_prompt, parent) -> Optional[Tuple[str, str]]` method
  - Display error messages via QMessageBox for validation failures
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

- [x] 4.1 Write property test for empty name rejection
  - **Property 16: Empty Name Rejection**
  - **Validates: Requirements 8.5**

- [x] 4.2 Write property test for duplicate name rejection
  - **Property 17: Duplicate Name Rejection**
  - **Validates: Requirements 8.6**

- [x] 4.3 Write property test for valid application addition
  - **Property 18: Valid Application Addition**
  - **Validates: Requirements 8.7**

- [x] 4.4 Write unit tests for dialog validation
  - Test error message for empty name
  - Test error message for duplicate name
  - Test Add button returns (name, prompt) tuple
  - Test Cancel button returns None

- [x] 5. Checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Verify data model and dialogs work correctly
  - Ask the user if questions arise

- [x] 6. Implement application list widget in settings window
  - Replace existing formatting_applications_edit QLineEdit with QGridLayout
  - Create application card buttons using QPushButton (similar to language selection)
  - Style buttons to match language selection (80px height, 120px width, rounded corners)
  - Display application name on each card
  - Add visual indicator for custom vs default prompt (e.g., icon or badge)
  - Implement 4-column grid layout
  - Load applications from FormattingConfig on page initialization
  - _Requirements: 1.1, 1.2, 1.5, 2.1, 2.2, 2.3, 12.1_

- [x] 6.1 Write property test for application display completeness
  - **Property 1: Application Display Completeness**
  - **Validates: Requirements 1.2**

- [x] 6.2 Write property test for application name visibility
  - **Property 2: Application Name Visibility**
  - **Validates: Requirements 2.1**

- [x] 6.3 Write property test for visual prompt differentiation
  - **Property 3: Visual Prompt Differentiation**
  - **Validates: Requirements 2.2, 2.3**

- [x] 6.4 Write unit tests for UI rendering
  - Test empty list displays correctly
  - Test default applications display on first initialization
  - Test grid layout with various numbers of applications

- [x] 7. Add "Add Application" button and workflow
  - Add "Add Application" button below the application grid
  - Connect button click to open AddApplicationDialog
  - On successful add, update FormattingConfig with new application
  - Refresh application grid to show new application
  - Save configuration to .env file
  - _Requirements: 1.3, 8.1, 8.7, 8.8_

- [x] 7.1 Write unit test for Add Application button
  - Test button exists and is visible
  - Test button opens AddApplicationDialog on click

- [x] 8. Implement context menu for application cards
  - Add right-click event handler to application card buttons
  - Create QMenu with "Edit" and "Delete" options
  - Localize menu items using translation system
  - Disable "Delete" option when only one application remains
  - Connect "Edit" action to open PromptEditDialog
  - Connect "Delete" action to remove application from list
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 9.1, 9.3_

- [x] 8.1 Write property test for context menu availability
  - **Property 4: Context Menu Availability**
  - **Validates: Requirements 3.1, 3.2, 3.3**

- [x] 8.2 Write property test for edit dialog opens
  - **Property 5: Edit Dialog Opens**
  - **Validates: Requirements 3.4, 4.1, 4.2**

- [x] 8.3 Write property test for delete removes application
  - **Property 6: Delete Removes Application**
  - **Validates: Requirements 3.5**

- [x] 8.4 Write property test for delete enabled with multiple apps
  - **Property 19: Delete Enabled for Multiple Applications**
  - **Validates: Requirements 9.3**

- [x] 8.5 Write unit tests for context menu behavior
  - Test context menu appears on right-click
  - Test Delete disabled when one application remains
  - Test Delete enabled when multiple applications exist

- [x] 9. Implement edit workflow
  - On "Edit" action, get current prompt for application
  - Open PromptEditDialog with application name and current prompt
  - On Save, update FormattingConfig with new prompt
  - Refresh application card to show updated visual indicator
  - Save configuration to .env file
  - _Requirements: 3.4, 4.5, 5.3_

- [x] 9.1 Write integration test for complete edit workflow
  - Test edit → modify prompt → save → verify persistence

- [x] 10. Implement delete workflow with constraints
  - On "Delete" action, verify more than one application exists
  - Remove application from FormattingConfig
  - Refresh application grid to remove card
  - Save configuration to .env file
  - Ensure at least one application always remains
  - _Requirements: 3.5, 9.1, 9.3, 9.4_

- [x] 10.1 Write property test for minimum one application invariant
  - **Property 20: Minimum One Application Invariant**
  - **Validates: Requirements 9.4**

- [x] 10.2 Write unit test for last application delete prevention
  - Test delete disabled when one application remains
  - Test error handling if delete attempted on last application

- [x] 11. Update formatting module to use per-application prompts
  - Modify `format_text()` in FormattingModule to call `config.get_prompt_for_app(format_type)`
  - Remove fallback to `self.config.system_prompt` (deprecated)
  - Ensure universal default prompt is used when app has empty prompt
  - Update logging to indicate which prompt is being used
  - _Requirements: 5.4, 6.1_

- [x] 11.1 Write integration test for formatting with per-app prompts
  - Test formatting uses correct prompt for each application
  - Test formatting falls back to default for apps without custom prompts

- [x] 12. Add localization strings
  - Add translation keys for "Edit" and "Delete" menu items
  - Add translation keys for dialog titles and buttons
  - Add translation keys for error messages
  - Add translation keys for "Add Application" button
  - Update Russian and English translation files
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 12.1 Write unit test for localization key usage
  - Test all UI text uses translation keys
  - Test no hardcoded strings in UI components

- [x] 13. Update settings save/load workflow
  - Modify `_load_settings()` to load from new FORMATTING_APP_PROMPTS format
  - Modify `_save_settings()` to save to new FORMATTING_APP_PROMPTS format
  - Trigger migration on first load if old format detected
  - Remove old FORMATTING_APPLICATIONS and FORMATTING_SYSTEM_PROMPT fields from UI
  - _Requirements: 7.1, 7.2, 7.3, 10.1, 10.5_

- [x] 13.1 Write integration test for save/load workflow
  - Test save → restart → load preserves all configurations
  - Test migration → save → load works correctly

- [x] 14. Final checkpoint - Ensure all tests pass
  - Run complete test suite (unit + property + integration)
  - Verify all 20 correctness properties pass
  - Test manual workflows (add, edit, delete, migration)
  - Verify visual consistency with language selection page
  - Ask the user if questions arise

## Notes

- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties (minimum 100 iterations each)
- Unit tests validate specific examples and edge cases
- Integration tests validate complete workflows
- The implementation maintains backward compatibility through migration logic
