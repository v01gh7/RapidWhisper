# Requirements Document

## Introduction

This specification defines the UI Customization feature for the RapidWhisper application. The feature adds a new settings tab that allows users to customize the visual appearance of the application, specifically controlling window transparency and font sizes across different UI components. This enhancement improves user experience by providing personalization options for better readability and visual comfort.

## Glossary

- **Floating_Window**: The main recording window that displays recording status and waveform visualization
- **Settings_Window**: The application settings dialog containing multiple configuration tabs
- **Info_Panel**: The bottom section of the Floating_Window displaying application name and hotkey information
- **Opacity**: The alpha channel value controlling background transparency (0=fully transparent, 255=fully opaque)
- **Config**: The configuration management system that reads from .env file and provides application settings
- **Translation_System**: The internationalization system supporting English and Russian languages

## Requirements

### Requirement 1: Window Transparency Control

**User Story:** As a user, I want to adjust the transparency of the floating recording window, so that I can customize how the window blends with my desktop background.

#### Acceptance Criteria

1. WHEN a user adjusts the opacity slider, THE Settings_Window SHALL update the WINDOW_OPACITY value in the range 50-255
2. WHEN the opacity value changes, THE Floating_Window SHALL apply the new transparency immediately without requiring application restart
3. WHEN the application starts, THE Floating_Window SHALL read the WINDOW_OPACITY value from Config with default value 150
4. THE Settings_Window SHALL display the current opacity value numerically next to the slider
5. WHEN a user attempts to set opacity outside the valid range, THE Settings_Window SHALL constrain the value to the nearest valid boundary (50 or 255)

### Requirement 2: Font Size Customization for Floating Window

**User Story:** As a user, I want to adjust font sizes in the floating window, so that I can improve readability based on my screen resolution and visual preferences.

#### Acceptance Criteria

1. WHEN a user adjusts the main text font size control, THE Settings_Window SHALL update FONT_SIZE_FLOATING_MAIN in the range 10-24 pixels
2. WHEN a user adjusts the info panel font size control, THE Settings_Window SHALL update FONT_SIZE_FLOATING_INFO in the range 8-16 pixels
3. WHEN the application starts, THE Floating_Window SHALL read font size values from Config with defaults (14px for main text, 11px for info panel)
4. WHEN font size values are saved, THE Settings_Window SHALL persist them to the .env file
5. THE Settings_Window SHALL display current font size values numerically for each control

### Requirement 3: Font Size Customization for Settings Window

**User Story:** As a user, I want to adjust font sizes in the settings window, so that I can improve readability of configuration options.

#### Acceptance Criteria

1. WHEN a user adjusts the labels font size control, THE Settings_Window SHALL update FONT_SIZE_SETTINGS_LABELS in the range 10-16 pixels
2. WHEN a user adjusts the titles font size control, THE Settings_Window SHALL update FONT_SIZE_SETTINGS_TITLES in the range 16-32 pixels
3. WHEN the Settings_Window reopens, THE Settings_Window SHALL apply the configured font sizes to all labels and titles
4. WHEN the application starts, THE Settings_Window SHALL read font size values from Config with defaults (12px for labels, 24px for titles)
5. THE Settings_Window SHALL display current font size values numerically for each control

### Requirement 4: Multilingual Support

**User Story:** As a user, I want UI customization settings displayed in my preferred language, so that I can understand and configure the options easily.

#### Acceptance Criteria

1. WHEN the Translation_System loads English translations, THE Translation_System SHALL include all UI customization keys with English text
2. WHEN the Translation_System loads Russian translations, THE Translation_System SHALL include all UI customization keys with Russian text
3. THE Settings_Window SHALL display the UI Customization tab title using the translated "ui_customization.title" key
4. THE Settings_Window SHALL display all control labels using their corresponding translation keys
5. THE Settings_Window SHALL display tooltips using translated "tooltip" keys where applicable

### Requirement 5: Settings Persistence

**User Story:** As a user, I want my UI customization preferences saved, so that they persist across application restarts.

#### Acceptance Criteria

1. WHEN a user changes any UI customization setting, THE Settings_Window SHALL write the new value to the .env file
2. WHEN the application starts, THE Config SHALL read all UI customization values from the .env file
3. IF a UI customization value is missing from .env, THEN THE Config SHALL provide the documented default value
4. WHEN settings are saved, THE Config SHALL validate all values are within their specified ranges
5. THE Settings_Window SHALL update the .env file immediately when values change (for opacity) or when the settings dialog is closed (for font sizes)

### Requirement 6: Reset to Defaults Functionality

**User Story:** As a user, I want to reset all UI customization settings to their default values, so that I can easily recover from undesirable configurations.

#### Acceptance Criteria

1. WHEN a user clicks the "Reset to Defaults" button, THE Settings_Window SHALL restore all UI customization values to their documented defaults
2. WHEN defaults are restored, THE Settings_Window SHALL update all UI controls to display the default values
3. WHEN defaults are restored, THE Settings_Window SHALL write the default values to the .env file
4. THE Settings_Window SHALL apply the default opacity value immediately to the Floating_Window
5. WHEN the reset operation completes, THE Settings_Window SHALL provide visual confirmation to the user

### Requirement 7: User Interface Organization

**User Story:** As a user, I want UI customization settings organized logically, so that I can easily find and adjust specific options.

#### Acceptance Criteria

1. THE Settings_Window SHALL create a new tab labeled with the translated "ui_customization.title" key
2. THE Settings_Window SHALL group window transparency controls in a visually distinct section
3. THE Settings_Window SHALL group font size controls in a visually distinct section with the translated "font_sizes" label
4. THE Settings_Window SHALL display controls in a logical order: opacity first, then font sizes grouped by window type
5. THE Settings_Window SHALL use consistent spacing and alignment for all controls

### Requirement 8: Input Validation and Error Handling

**User Story:** As a user, I want the application to handle invalid input gracefully, so that I cannot configure settings that break the application.

#### Acceptance Criteria

1. WHEN a user provides a non-numeric value for any setting, THE Settings_Window SHALL reject the input and maintain the previous valid value
2. WHEN a user provides a value outside the valid range, THE Settings_Window SHALL constrain it to the nearest valid boundary
3. IF the .env file contains invalid values, THEN THE Config SHALL use default values and log a warning
4. WHEN reading configuration values, THE Config SHALL handle missing .env file gracefully by using all default values
5. THE Settings_Window SHALL prevent users from entering values outside valid ranges through UI controls (slider limits, spinbox bounds)
