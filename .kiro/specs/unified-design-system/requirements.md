# Requirements Document

## Introduction

This specification defines the requirements for implementing a unified design system across the RapidWhisper application. The goal is to apply the modern floating window design (semi-transparent background, blur effects, rounded corners, and custom borders) to all application windows, specifically the Settings Window and Tray Icon menu, ensuring visual consistency throughout the application.

## Glossary

- **Floating_Window**: The main transcription display window with modern visual styling
- **Settings_Window**: The configuration interface window for application settings
- **Tray_Icon**: The system tray icon and its associated context menu
- **Blur_Effect**: Platform-specific visual effect (Windows Acrylic/Mica) that blurs content behind windows
- **Opacity**: Transparency level of window backgrounds (range 50-255, where 255 is fully opaque)
- **Border_Radius**: The curvature applied to window corners, measured in pixels
- **Frameless_Window**: A window without standard OS-provided title bar and borders
- **Design_System**: The collection of visual styling rules applied consistently across the application

## Requirements

### Requirement 1: Settings Window Visual Styling

**User Story:** As a user, I want the Settings Window to have the same modern visual appearance as the Floating Window, so that the application has a consistent and polished look.

#### Acceptance Criteria

1. WHEN the Settings Window is displayed, THE Settings_Window SHALL apply a semi-transparent background with color `rgba(30, 30, 30, {opacity})`
2. WHEN the Settings Window is displayed, THE Settings_Window SHALL apply a border-radius of 5 pixels to all corners
3. WHEN the Settings Window is displayed, THE Settings_Window SHALL apply a 2-pixel border with color `rgba(255, 255, 255, 100)`
4. WHEN the Settings Window is displayed, THE Settings_Window SHALL apply the platform-specific blur effect using the `apply_blur_effect()` method
5. WHEN the Settings Window is displayed, THE Settings_Window SHALL use the opacity value from `config.window_opacity`

### Requirement 2: Settings Window Frameless Behavior

**User Story:** As a user, I want the Settings Window to be frameless but still movable, so that I can position it anywhere on my screen while maintaining the modern aesthetic.

#### Acceptance Criteria

1. WHEN the Settings Window is created, THE Settings_Window SHALL set window flags to `Qt.WindowType.FramelessWindowHint`
2. WHEN the Settings Window is created, THE Settings_Window SHALL set the `Qt.WidgetAttribute.WA_TranslucentBackground` attribute
3. WHEN a user clicks and drags the Settings Window header area, THE Settings_Window SHALL move to follow the mouse cursor
4. WHEN the Settings Window is moved, THE Settings_Window SHALL maintain its visual styling and blur effects

### Requirement 3: Tray Icon Menu Styling

**User Story:** As a user, I want the Tray Icon menu to have modern dark theme styling consistent with the application, so that all UI elements feel cohesive.

#### Acceptance Criteria

1. WHEN the Tray Icon menu is displayed, THE Tray_Icon SHALL apply a semi-transparent dark background
2. WHEN the Tray Icon menu is displayed, THE Tray_Icon SHALL apply rounded corners to the menu container
3. WHEN the Tray Icon menu is displayed, THE Tray_Icon SHALL use consistent color scheme with the Floating Window and Settings Window
4. WHEN a user hovers over menu items, THE Tray_Icon SHALL provide visual feedback with appropriate hover states

### Requirement 4: Configuration Integration

**User Story:** As a user, I want all windows to respect my opacity preferences, so that I can customize the transparency level across the entire application.

#### Acceptance Criteria

1. WHEN the `config.window_opacity` value changes, THE Settings_Window SHALL update its background opacity to match
2. WHEN the `config.window_opacity` value is outside the range 50-255, THE Design_System SHALL clamp the value to valid bounds
3. WHEN the application starts, THE Settings_Window SHALL read the opacity value from the configuration file

### Requirement 5: Functional Preservation

**User Story:** As a user, I want all existing functionality to continue working after the visual updates, so that I don't lose any features.

#### Acceptance Criteria

1. WHEN the Settings Window visual styling is applied, THE Settings_Window SHALL maintain all existing configuration controls and their functionality
2. WHEN the Tray Icon menu styling is applied, THE Tray_Icon SHALL maintain all existing menu actions and their functionality
3. WHEN the Settings Window is closed, THE Settings_Window SHALL save configuration changes as before
4. WHEN the Tray Icon menu items are clicked, THE Tray_Icon SHALL execute the corresponding actions as before

### Requirement 6: Cross-Platform Compatibility

**User Story:** As a user on any supported platform, I want the design system to work correctly, so that I have a consistent experience regardless of my operating system.

#### Acceptance Criteria

1. WHEN the blur effect is not available on a platform, THE Design_System SHALL gracefully degrade to solid backgrounds
2. WHEN the application runs on Windows, THE Design_System SHALL use Windows Acrylic or Mica blur effects
3. WHEN the application runs on non-Windows platforms, THE Design_System SHALL apply appropriate fallback styling

### Requirement 7: Design System Reusability

**User Story:** As a developer, I want the design system to be implemented in a reusable way, so that future windows can easily adopt the same styling.

#### Acceptance Criteria

1. THE Design_System SHALL provide a reusable method or mixin for applying the unified visual style
2. WHEN a new window needs the unified design, THE Design_System SHALL allow applying the style with minimal code duplication
3. THE Design_System SHALL centralize styling constants (colors, border-radius, opacity ranges) in a single location
