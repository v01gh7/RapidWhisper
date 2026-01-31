# Requirements Document

## Introduction

This specification defines improvements to the RapidWhisper formatting settings UI. The current implementation uses a single text field for comma-separated applications and a single system prompt field. The improved UI will provide a visual list of applications with per-application customizable prompts, similar to the language selection interface.

## Glossary

- **Application**: A software program that can receive formatted transcription output (e.g., Notion, Obsidian, Word)
- **System_Prompt**: Instructions given to the AI model to format text in a specific way
- **Formatting_Module**: The component responsible for detecting active applications and formatting transcribed text
- **Settings_Window**: The configuration interface where users manage application settings
- **Application_List**: A visual list widget displaying configured applications
- **Context_Menu**: A right-click menu providing actions for application items
- **Modal_Dialog**: A popup window for editing application-specific prompts
- **Universal_Prompt**: A default system prompt that works for all application formats
- **Environment_File**: The .env file where configuration is persisted as JSON

## Requirements

### Requirement 1: Visual Application List Management

**User Story:** As a user, I want to see my configured applications in a visual list, so that I can easily understand which applications are configured for formatting.

#### Acceptance Criteria

1. THE Settings_Window SHALL display applications in a visual list widget similar to the language selection UI
2. WHEN the formatting settings page is opened, THE Settings_Window SHALL display all configured applications as individual items in the list
3. THE Settings_Window SHALL provide an "Add Application" button to add new applications to the list
4. WHEN no applications are configured, THE Settings_Window SHALL display an empty list with the "Add Application" button visible
5. THE Settings_Window SHALL display default applications (notion, obsidian, markdown, word, libreoffice, vscode) when first initialized

### Requirement 2: Application Item Display

**User Story:** As a user, I want each application to be displayed as a clear, distinct item, so that I can easily identify and interact with individual applications.

#### Acceptance Criteria

1. THE Settings_Window SHALL display each application as a card or list item with the application name visible
2. WHEN an application has a custom prompt, THE Settings_Window SHALL indicate this visually on the application item
3. WHEN an application uses the universal default prompt, THE Settings_Window SHALL indicate this visually on the application item
4. THE Settings_Window SHALL display application items with consistent styling matching the existing UI design system

### Requirement 3: Context Menu Operations

**User Story:** As a user, I want to right-click on an application to access actions, so that I can edit or remove applications efficiently.

#### Acceptance Criteria

1. WHEN a user right-clicks on an application item, THE Settings_Window SHALL display a context menu
2. THE Context_Menu SHALL provide an "Edit" option to open the prompt editor
3. THE Context_Menu SHALL provide a "Delete" option to remove the application from the list
4. WHEN the user selects "Edit", THE Settings_Window SHALL open a modal dialog for editing the application's prompt
5. WHEN the user selects "Delete", THE Settings_Window SHALL remove the application from the list immediately

### Requirement 4: Modal Dialog for Prompt Editing

**User Story:** As a user, I want to edit an application's system prompt in a dedicated dialog, so that I can customize formatting behavior per application.

#### Acceptance Criteria

1. WHEN the user selects "Edit" from the context menu, THE Settings_Window SHALL open a modal dialog
2. THE Modal_Dialog SHALL display the application name as read-only text
3. THE Modal_Dialog SHALL provide a large text area for editing the system prompt
4. THE Modal_Dialog SHALL provide "Save" and "Cancel" buttons
5. WHEN the user clicks "Save", THE Modal_Dialog SHALL save the prompt and close the dialog
6. WHEN the user clicks "Cancel", THE Modal_Dialog SHALL discard changes and close the dialog
7. THE Modal_Dialog SHALL use styling consistent with the language selection UI

### Requirement 5: Per-Application Prompt Management

**User Story:** As a user, I want each application to have its own customizable system prompt, so that I can tailor formatting to each application's specific needs.

#### Acceptance Criteria

1. THE Formatting_Module SHALL store a unique system prompt for each configured application
2. WHEN a new application is added without a custom prompt, THE Formatting_Module SHALL assign the universal default prompt
3. WHEN a user edits an application's prompt, THE Formatting_Module SHALL save the custom prompt for that application only
4. WHEN formatting text for an application, THE Formatting_Module SHALL use that application's specific prompt
5. THE Settings_Window SHALL allow users to view and edit each application's prompt independently

### Requirement 6: Universal Default Prompt

**User Story:** As a developer, I want a universal default prompt that works for all formats, so that new applications have sensible formatting behavior without requiring immediate customization.

#### Acceptance Criteria

1. THE Formatting_Module SHALL define a universal default prompt that works for all application formats
2. WHEN a new application is added, THE Formatting_Module SHALL assign the universal default prompt
3. THE Universal_Prompt SHALL provide general formatting instructions suitable for markdown, notion, obsidian, word, and other formats
4. THE Settings_Window SHALL allow users to customize the universal prompt per application after creation

### Requirement 7: Data Persistence

**User Story:** As a user, I want my application configurations and prompts to be saved, so that they persist across application restarts.

#### Acceptance Criteria

1. THE Settings_Window SHALL serialize application configurations and prompts to JSON format
2. THE Settings_Window SHALL store the JSON data in the .env file under the key FORMATTING_APP_PROMPTS
3. WHEN the application starts, THE Settings_Window SHALL load application configurations from the .env file
4. THE Settings_Window SHALL parse the JSON data and populate the application list
5. THE Settings_Window SHALL maintain backward compatibility with existing comma-separated application configuration

### Requirement 8: Add Application Workflow

**User Story:** As a user, I want to add new applications to the formatting list, so that I can extend formatting support to additional programs.

#### Acceptance Criteria

1. WHEN the user clicks "Add Application", THE Settings_Window SHALL open a modal dialog for adding a new application
2. THE Modal_Dialog SHALL provide a text field for entering the application name
3. THE Modal_Dialog SHALL provide a text area for entering or editing the system prompt
4. THE Modal_Dialog SHALL display a default prompt template in the text area
5. THE Settings_Window SHALL validate that the application name is not empty
6. THE Settings_Window SHALL validate that the application name is not already in the list
7. WHEN a valid application name is provided, THE Settings_Window SHALL add the application to the list with the specified prompt
8. THE Settings_Window SHALL display the newly added application in the list immediately

### Requirement 9: Delete Application Constraints

**User Story:** As a user, I want to be prevented from deleting the last application, so that the formatting feature always has at least one configured application.

#### Acceptance Criteria

1. WHEN only one application remains in the list, THE Context_Menu SHALL disable the "Delete" option
2. WHEN the user attempts to delete the last application, THE Settings_Window SHALL display an error message
3. WHEN multiple applications exist, THE Context_Menu SHALL enable the "Delete" option for all applications
4. THE Settings_Window SHALL maintain at least one application in the list at all times

### Requirement 10: Backward Compatibility

**User Story:** As a developer, I want the new configuration format to be backward compatible, so that existing user configurations are preserved during migration.

#### Acceptance Criteria

1. WHEN the application loads and detects the old comma-separated format in FORMATTING_APPLICATIONS, THE Settings_Window SHALL migrate the configuration to the new JSON format
2. THE Settings_Window SHALL assign the universal default prompt to all migrated applications
3. WHEN migration occurs, THE Settings_Window SHALL preserve all application names from the old format
4. THE Settings_Window SHALL write the migrated configuration to FORMATTING_APP_PROMPTS in the .env file
5. THE Settings_Window SHALL remove the old FORMATTING_APPLICATIONS key after successful migration

### Requirement 11: Localization Support

**User Story:** As a user, I want the UI to display in my preferred language, so that I can use the application in Russian or English.

#### Acceptance Criteria

1. THE Settings_Window SHALL display all UI text in the user's selected language (Russian or English)
2. THE Context_Menu SHALL display "Редактировать" and "Удалить" in Russian when Russian is selected
3. THE Context_Menu SHALL display "Edit" and "Delete" in English when English is selected
4. THE Modal_Dialog SHALL display localized button text ("Сохранить"/"Save", "Отменить"/"Cancel")
5. THE Settings_Window SHALL display localized error messages and tooltips

### Requirement 12: Visual Consistency

**User Story:** As a user, I want the formatting settings UI to match the existing application design, so that the interface feels cohesive and familiar.

#### Acceptance Criteria

1. THE Settings_Window SHALL use the same styling as the language selection page for application items
2. THE Settings_Window SHALL use consistent colors, fonts, and spacing with the rest of the application
3. THE Modal_Dialog SHALL use the same button styles and layout as other dialogs in the application
4. THE Context_Menu SHALL use the same styling as other context menus in the application
5. THE Settings_Window SHALL maintain visual consistency across all formatting-related UI components
