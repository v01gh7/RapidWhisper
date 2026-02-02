# Requirements Document

## Introduction

This document specifies requirements for internationalizing error messages and user-facing messages in the RapidWhisper application. Currently, the application has a localization system (utils/i18n.py) supporting 15 languages for the UI, but many error messages, notifications, and status messages are hardcoded in Russian. This creates poor user experience when the interface language is set to anything other than Russian.

The goal is to ensure all user-visible messages are translated through the i18n system, while preserving Russian for code comments and logs.

## Glossary

- **i18n_System**: The internationalization system implemented in utils/i18n.py
- **User_Message**: Any text displayed to the user through UI, notifications, or error dialogs
- **Log_Message**: Internal logging messages written to log files (not visible to users)
- **Code_Comment**: Documentation comments in source code
- **Translation_Key**: A dot-notation string used to retrieve translations (e.g., "errors.file_not_found")
- **Translation_File**: JSON files in utils/translations/ containing translations for each language
- **Exception_Message**: Text passed to exception constructors that may be shown to users
- **Notification_Message**: Text displayed in system tray notifications
- **Status_Message**: Text displayed in UI status indicators

## Requirements

### Requirement 1: Internationalize Exception Messages

**User Story:** As a user with a non-Russian interface language, I want to see error messages in my chosen language, so that I can understand what went wrong.

#### Acceptance Criteria

1. WHEN an exception is raised with a user-visible message, THE i18n_System SHALL translate the message using the current interface language
2. WHEN an exception message contains parameters (e.g., filename, provider name), THE i18n_System SHALL support parameter interpolation in translated messages
3. WHEN a translation key is missing for the current language, THE i18n_System SHALL fall back to English translation
4. THE Exception_Message SHALL use translation keys instead of hardcoded Russian text
5. WHEN an exception is logged, THE Log_Message SHALL remain in Russian (not translated)

### Requirement 2: Internationalize API Error Messages

**User Story:** As a user experiencing API errors, I want to see error descriptions in my interface language, so that I can troubleshoot the issue.

#### Acceptance Criteria

1. WHEN an API authentication error occurs, THE i18n_System SHALL display the error message in the current interface language
2. WHEN an API network error occurs, THE i18n_System SHALL display the error message in the current interface language
3. WHEN an API timeout error occurs, THE i18n_System SHALL display the error message in the current interface language
4. WHEN an API rate limit error occurs, THE i18n_System SHALL display the error message in the current interface language
5. WHEN a model not found error occurs, THE i18n_System SHALL display the error message with the model name in the current interface language

### Requirement 3: Internationalize Notification Messages

**User Story:** As a user receiving system notifications, I want to see notification text in my interface language, so that I understand the application status.

#### Acceptance Criteria

1. WHEN a transcription completes successfully, THE Notification_Message SHALL be displayed in the current interface language
2. WHEN a transcription fails, THE Notification_Message SHALL be displayed in the current interface language with error details
3. WHEN settings are saved, THE Notification_Message SHALL be displayed in the current interface language
4. WHEN a hotkey registration fails, THE Notification_Message SHALL be displayed in the current interface language
5. WHEN an API key is missing, THE Notification_Message SHALL be displayed in the current interface language

### Requirement 4: Preserve Non-User-Facing Text

**User Story:** As a developer debugging the application, I want log messages and code comments to remain in Russian, so that I can maintain consistency with the existing codebase.

#### Acceptance Criteria

1. WHEN logging to files, THE Log_Message SHALL remain in Russian
2. WHEN writing code comments, THE Code_Comment SHALL remain in Russian
3. WHEN logging debug information, THE Log_Message SHALL remain in Russian
4. THE i18n_System SHALL NOT translate logger.info, logger.error, logger.debug, or logger.warning messages
5. THE i18n_System SHALL NOT translate docstrings or inline comments

### Requirement 5: Add Translation Keys to Translation Files

**User Story:** As a translator, I want all error messages to have translation keys in translation files, so that I can provide translations for all supported languages.

#### Acceptance Criteria

1. WHEN a new error message is added, THE Translation_File SHALL contain the translation key for all 15 supported languages
2. WHEN an error message contains parameters, THE Translation_File SHALL use Python format string syntax (e.g., {filename})
3. THE Translation_File SHALL organize error messages under the "errors" namespace
4. THE Translation_File SHALL organize notification messages under the "tray.notification" namespace
5. THE Translation_File SHALL maintain consistency with existing translation file structure

### Requirement 6: Update Exception Classes

**User Story:** As a developer, I want exception classes to support internationalized messages, so that I can raise exceptions with translated text.

#### Acceptance Criteria

1. WHEN an exception is raised, THE Exception class SHALL accept a translation key instead of a hardcoded message
2. WHEN an exception is raised with parameters, THE Exception class SHALL support parameter passing for interpolation
3. THE Exception class SHALL use the i18n_System to translate messages when displayed to users
4. THE Exception class SHALL preserve the original translation key for logging purposes
5. WHEN an exception is caught and logged, THE Log_Message SHALL use the technical message, not the translated user message

### Requirement 7: Internationalize Status Messages

**User Story:** As a user, I want to see status messages (recording, processing, ready) in my interface language, so that I understand the current application state.

#### Acceptance Criteria

1. WHEN the application is recording, THE Status_Message SHALL display "Recording..." in the current interface language
2. WHEN the application is processing, THE Status_Message SHALL display "Processing..." in the current interface language
3. WHEN the application is ready, THE Status_Message SHALL display "Ready" in the current interface language
4. THE Status_Message SHALL update immediately when the interface language changes
5. THE Status_Message SHALL use translation keys from the "status" namespace

### Requirement 8: Maintain Backward Compatibility

**User Story:** As a developer, I want the i18n changes to maintain backward compatibility, so that existing code continues to work without modifications.

#### Acceptance Criteria

1. WHEN existing code raises exceptions with Russian messages, THE Exception class SHALL continue to work (with deprecation warning in logs)
2. WHEN the i18n_System is unavailable, THE Exception class SHALL fall back to the original message
3. THE Exception class SHALL maintain the same constructor signature for backward compatibility
4. WHEN translation keys are missing, THE i18n_System SHALL return the key itself as a fallback
5. THE Exception class SHALL not break existing error handling code
