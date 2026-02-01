# Requirements Document

## Introduction

This feature adds a manual format selection capability triggered by a hotkey (Ctrl+Alt+Space by default). When activated, it displays a dialog allowing users to choose a formatting application for the current recording session, overriding both automatic application detection and fixed format settings. The manual selection applies only to the current session and does not persist to subsequent recordings.

## Glossary

- **Format_Selection_Dialog**: A modal UI component that displays available formatting applications and allows user selection
- **Formatting_Module**: The system component responsible for determining which formatting application to use for transcription
- **State_Manager**: The system component that maintains application state during runtime
- **Hotkey_Manager**: The system component that registers and handles keyboard shortcuts
- **Manual_Format_Selection**: A user-initiated format choice that takes priority over automatic detection and fixed format settings
- **Recording_Session**: A single voice recording cycle from start to transcription completion
- **Fixed_Format_Setting**: A configuration option (use_fixed_format) that forces use of universal format instead of auto-detection
- **Universal_Format**: The fallback formatting application used when no specific application format is available

## Requirements

### Requirement 1: Hotkey Registration and Triggering

**User Story:** As a user, I want to press a hotkey to open the format selection dialog, so that I can quickly choose a formatting application without navigating through menus.

#### Acceptance Criteria

1. WHEN the system starts, THE Hotkey_Manager SHALL register the format selection hotkey with default binding Ctrl+Alt+Space
2. WHEN the user presses the registered hotkey, THE Hotkey_Manager SHALL trigger the Format_Selection_Dialog to open
3. WHEN the hotkey is triggered during an active recording, THE System SHALL queue the dialog to open after recording stops
4. WHEN the hotkey configuration is invalid or conflicts with system hotkeys, THE Hotkey_Manager SHALL log an error and use the default binding

### Requirement 2: Format Selection Dialog Display

**User Story:** As a user, I want to see all available formatting applications in a clear dialog, so that I can choose the appropriate format for my current task.

#### Acceptance Criteria

1. WHEN the Format_Selection_Dialog opens, THE System SHALL display a list of all available formatting applications
2. THE Format_Selection_Dialog SHALL display the Universal_Format as the first item in the list
3. WHEN displaying format options, THE Format_Selection_Dialog SHALL show human-readable names for each formatting application
4. THE Format_Selection_Dialog SHALL be modal and prevent interaction with other windows until closed
5. WHEN the dialog is displayed, THE System SHALL position it near the cursor or at the center of the screen

### Requirement 3: Format Selection and Application

**User Story:** As a user, I want my manual format selection to apply immediately to the current recording, so that I can control the output format regardless of automatic detection.

#### Acceptance Criteria

1. WHEN a user selects a format from the Format_Selection_Dialog, THE State_Manager SHALL store the selection as Manual_Format_Selection for the current session
2. WHEN the user confirms the selection, THE Format_Selection_Dialog SHALL close and return the selected format
3. WHEN the user cancels the dialog or presses ESC, THE System SHALL maintain normal format detection behavior
4. WHEN Manual_Format_Selection is set, THE Formatting_Module SHALL use it for the current Recording_Session

### Requirement 4: Priority System Implementation

**User Story:** As a user, I want my manual format selection to override all other format determination methods, so that I have full control when needed.

#### Acceptance Criteria

1. WHEN determining the active format, THE Formatting_Module SHALL check Manual_Format_Selection first before other methods
2. WHEN Manual_Format_Selection is set, THE Formatting_Module SHALL ignore the Fixed_Format_Setting
3. WHEN Manual_Format_Selection is set, THE Formatting_Module SHALL ignore automatic application detection
4. WHEN a Recording_Session completes, THE State_Manager SHALL clear the Manual_Format_Selection
5. WHEN a new Recording_Session starts without Manual_Format_Selection, THE Formatting_Module SHALL return to normal behavior using Fixed_Format_Setting or automatic detection

### Requirement 5: Hotkey Configuration UI

**User Story:** As a user, I want to customize the format selection hotkey in settings, so that I can avoid conflicts with other applications or match my preferred keyboard shortcuts.

#### Acceptance Criteria

1. WHEN the Settings window displays the Hotkeys section, THE System SHALL show the current format selection hotkey binding
2. WHEN displaying the hotkey, THE System SHALL show the format "Ctrl+Alt+Space: Format selection dialog" with localized text
3. WHEN a user modifies the hotkey binding, THE System SHALL validate the new binding for conflicts
4. WHEN a valid new binding is saved, THE Hotkey_Manager SHALL unregister the old binding and register the new one
5. WHEN an invalid binding is entered, THE System SHALL display an error message and maintain the previous binding

### Requirement 6: Format List Population

**User Story:** As a developer, I want the format selection dialog to automatically discover all available formatting applications, so that new formats are immediately available without code changes.

#### Acceptance Criteria

1. WHEN the Format_Selection_Dialog initializes, THE System SHALL scan the config/prompts directory for all .txt files
2. WHEN scanning for formats, THE System SHALL extract formatting application names from the configuration
3. THE System SHALL include the Universal_Format in the available formats list
4. WHEN no custom formats are found, THE System SHALL display only the Universal_Format option

### Requirement 7: Keyboard Navigation in Dialog

**User Story:** As a user, I want to navigate the format selection dialog with keyboard shortcuts, so that I can quickly select a format without using the mouse.

#### Acceptance Criteria

1. WHEN the Format_Selection_Dialog is open, THE System SHALL allow arrow key navigation through the format list
2. WHEN the user presses Enter, THE System SHALL confirm the currently highlighted format selection
3. WHEN the user presses ESC, THE System SHALL cancel the dialog and close it without making a selection
4. WHEN the dialog opens, THE System SHALL highlight the first format option by default

### Requirement 8: Session State Management

**User Story:** As a developer, I want the manual format selection to be properly scoped to a single recording session, so that the system behavior is predictable and doesn't leak state between sessions.

#### Acceptance Criteria

1. WHEN a Manual_Format_Selection is stored, THE State_Manager SHALL associate it with the current Recording_Session only
2. WHEN a Recording_Session completes transcription, THE State_Manager SHALL clear the Manual_Format_Selection
3. WHEN querying for Manual_Format_Selection in a new session, THE State_Manager SHALL return None if no selection has been made
4. WHEN the application restarts, THE State_Manager SHALL NOT persist Manual_Format_Selection from previous sessions

### Requirement 9: Translation Support

**User Story:** As a user, I want the format selection dialog to display in my preferred language, so that I can understand the options clearly.

#### Acceptance Criteria

1. WHEN displaying UI text in the Format_Selection_Dialog, THE System SHALL use the translation system with keys from en.json and ru.json
2. WHEN displaying the hotkey in settings, THE System SHALL use localized text for the description
3. WHEN displaying format names, THE System SHALL use human-readable names that may be localized if translations are available
4. WHEN a translation is missing, THE System SHALL fall back to English text

### Requirement 10: Error Handling

**User Story:** As a user, I want the system to handle errors gracefully when the format selection feature encounters problems, so that my workflow is not disrupted.

#### Acceptance Criteria

1. WHEN the Format_Selection_Dialog fails to load format list, THE System SHALL display an error message and fall back to normal format detection
2. WHEN the hotkey registration fails, THE System SHALL log the error and continue operation without the hotkey
3. WHEN the State_Manager fails to store Manual_Format_Selection, THE System SHALL log the error and proceed with normal format detection
4. WHEN the Format_Selection_Dialog encounters an unexpected error, THE System SHALL close the dialog and maintain normal operation
