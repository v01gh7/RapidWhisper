# Requirements Document: Transcription Formatting

## Introduction

This feature adds automatic formatting capabilities to transcribed text based on the active application window. When enabled, the system will detect which application is currently active (e.g., Notion, Obsidian, Word) and format the transcription output accordingly using AI-powered formatting. The feature integrates with existing post-processing capabilities to avoid redundant API calls.

## Glossary

- **Transcription_System**: The core system that converts speech to text
- **Formatting_Module**: The component responsible for applying application-specific formatting to transcribed text
- **Post_Processing_Module**: The existing component that processes transcribed text for improvements
- **Window_Monitor**: The component that detects the currently active application window
- **AI_Provider**: The service used for AI-powered text processing (groq, openai, glm, or custom)
- **Formatting_AI_Provider**: The dedicated AI provider configuration for formatting operations, independent from transcription and post-processing providers
- **Format_Configuration**: The list of supported applications and their formatting rules
- **Settings_UI**: The user interface for configuring system settings
- **Processing_Settings**: The settings category containing transcription processing options

## Requirements

### Requirement 1: Formatting Settings Configuration

**User Story:** As a user, I want to configure formatting settings, so that I can control how my transcriptions are formatted for different applications.

#### Acceptance Criteria

1. THE Settings_UI SHALL display a "Formatting" section within the Processing_Settings category
2. WHEN the Formatting section is displayed, THE Settings_UI SHALL show an enable/disable toggle control
3. WHEN the Formatting section is displayed, THE Settings_UI SHALL show a Formatting_AI_Provider selection dropdown with options: groq, openai, glm, custom
4. WHEN the Formatting section is displayed, THE Settings_UI SHALL show a model selection field specific to formatting
5. WHEN the Formatting section is displayed, THE Settings_UI SHALL show an application list input field for comma-separated application names
6. WHEN the Formatting section is displayed, THE Settings_UI SHALL show an informational label explaining the feature
7. THE Formatting_AI_Provider configuration SHALL be independent from transcription and post-processing AI provider settings

### Requirement 2: Configuration Persistence

**User Story:** As a user, I want my formatting settings to be saved, so that they persist across application restarts.

#### Acceptance Criteria

1. WHEN formatting settings are modified, THE Transcription_System SHALL save the FORMATTING_ENABLED boolean value to the configuration file
2. WHEN formatting settings are modified, THE Transcription_System SHALL save the FORMATTING_PROVIDER string value to the configuration file
3. WHEN formatting settings are modified, THE Transcription_System SHALL save the FORMATTING_MODEL string value to the configuration file
4. WHEN formatting settings are modified, THE Transcription_System SHALL save the FORMATTING_APPLICATIONS comma-separated list to the configuration file
5. WHEN the application starts, THE Transcription_System SHALL load all formatting configuration values from the configuration file

### Requirement 3: Active Window Detection

**User Story:** As a user, I want the system to detect which application I'm using, so that transcriptions are formatted appropriately for that application.

#### Acceptance Criteria

1. WHEN a transcription is initiated, THE Window_Monitor SHALL detect the currently active application window
2. WHEN the active window is detected, THE Window_Monitor SHALL return the application name
3. WHEN the active window is detected, THE Window_Monitor SHALL return the active file extension if applicable
4. THE Formatting_Module SHALL match the detected application name against the Format_Configuration list
5. THE Formatting_Module SHALL match the detected file extension against the Format_Configuration list
6. THE Window_Monitor SHALL reuse existing window detection infrastructure from the info panel

### Requirement 4: Formatting with Post-Processing Disabled

**User Story:** As a user, I want transcriptions to be formatted when post-processing is disabled, so that I can get formatted output without additional processing.

#### Acceptance Criteria

1. WHEN formatting is enabled AND post-processing is disabled AND the active application matches the Format_Configuration, THE Formatting_Module SHALL send the original transcription text to the Formatting_AI_Provider
2. WHEN sending text to the Formatting_AI_Provider, THE Formatting_Module SHALL include an application-specific formatting prompt
3. WHEN the Formatting_AI_Provider returns formatted text, THE Formatting_Module SHALL return the formatted text as the final transcription output
4. WHEN the active application does not match the Format_Configuration, THE Formatting_Module SHALL return the original transcription text unchanged
5. THE Formatting_Module SHALL use its own dedicated AI provider configuration, separate from post-processing

### Requirement 5: Combined Formatting with Post-Processing

**User Story:** As a user, I want formatting and post-processing to happen in a single AI request, so that I avoid duplicate API calls and reduce processing time.

#### Acceptance Criteria

1. WHEN formatting is enabled AND post-processing is enabled AND the active application matches the Format_Configuration, THE Transcription_System SHALL combine both operations into a single AI request
2. WHEN combining operations, THE Transcription_System SHALL use the post-processing AI provider for the combined request
3. WHEN combining operations, THE Transcription_System SHALL extend the post-processing system prompt to include formatting instructions
4. WHEN combining operations, THE Transcription_System SHALL send only one request to the AI provider
5. WHEN the AI provider returns processed text, THE Transcription_System SHALL return the text that is both post-processed and formatted
6. WHEN formatting is enabled AND post-processing is enabled AND the active application does not match the Format_Configuration, THE Transcription_System SHALL perform only post-processing
7. THE combined operation SHALL prioritize the post-processing AI provider to avoid conflicts between different provider configurations

### Requirement 6: Application-Specific Formatting

**User Story:** As a user, I want different formatting for different applications, so that the output matches the conventions of each tool I use.

#### Acceptance Criteria

1. WHEN the active application is Notion, THE Formatting_Module SHALL apply Notion-specific formatting rules
2. WHEN the active application is Obsidian, THE Formatting_Module SHALL apply Obsidian-specific markdown formatting rules
3. WHEN the active file extension is .md, THE Formatting_Module SHALL apply standard markdown formatting rules
4. WHEN the active application is Word, THE Formatting_Module SHALL apply Word-compatible formatting rules
5. THE Formatting_Module SHALL support custom application formats defined in the Format_Configuration

### Requirement 7: AI Provider Integration

**User Story:** As a developer, I want to reuse existing AI client infrastructure, so that formatting uses the same reliable communication patterns as other AI features.

#### Acceptance Criteria

1. THE Formatting_Module SHALL use the existing AI client infrastructure for communication with AI providers
2. WHEN formatting is requested, THE Formatting_Module SHALL select the configured Formatting_AI_Provider (groq, openai, glm, or custom)
3. WHEN formatting is requested, THE Formatting_Module SHALL use the configured model for the selected Formatting_AI_Provider
4. WHEN an AI request fails, THE Formatting_Module SHALL return the original unformatted text
5. WHEN an AI request fails, THE Formatting_Module SHALL log the error for debugging
6. THE Formatting_Module SHALL maintain separate AI client instances to avoid conflicts with transcription and post-processing

### Requirement 8: UI Layout and Design

**User Story:** As a user, I want the formatting settings UI to be consistent with existing settings, so that the interface is familiar and easy to use.

#### Acceptance Criteria

1. THE Settings_UI SHALL create a QGroupBox widget for the Formatting section
2. THE Settings_UI SHALL position the Formatting section within the Processing settings page
3. THE Settings_UI SHALL use the same visual style as the post-processing settings section
4. WHEN displaying the application list field, THE Settings_UI SHALL show placeholder text indicating comma-separated format
5. WHEN displaying the informational label, THE Settings_UI SHALL explain that formatting applies based on the active window
