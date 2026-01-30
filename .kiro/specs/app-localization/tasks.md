# Implementation Plan: Application Localization

## Overview

This plan implements full internationalization (i18n) for RapidWhisper, supporting 15 languages with dynamic language switching, RTL support, and locale-aware formatting. The implementation follows a phased approach, starting with core infrastructure and progressively adding language support and UI updates.

## Tasks

- [x] 1. Create i18n module infrastructure
  - Create `utils/i18n.py` module
  - Define SUPPORTED_LANGUAGES dictionary with 15 language entries
  - Implement core translation function `t(key, lang=None, **kwargs)`
  - Implement language management functions: `set_language()`, `get_language()`
  - Implement system language detection: `detect_system_language()`
  - Implement RTL detection: `is_rtl(lang=None)`
  - Add global state management for current language
  - _Requirements: 1.1, 1.2, 2.1, 2.2, 7.1_

- [x] 1.1 Write property test for translation function
  - **Property 1: Translation function returns valid strings for all keys**
  - **Validates: Requirements 2.1**

- [x] 1.2 Write property test for fallback behavior
  - **Property 2: Fallback to English for missing translations**
  - **Validates: Requirements 1.4**

- [x] 1.3 Write property test for system language detection
  - **Property 5: System language detection returns supported language**
  - **Validates: Requirements 1.2**

- [x] 2. Implement translation dictionaries for English and Russian
  - Create TRANSLATIONS dictionary structure
  - Add English translations for all categories: settings, status, errors, tray, common
  - Add Russian translations for all categories
  - Organize translations hierarchically (category.subcategory.key)
  - Include all existing UI strings from settings_window.py, floating_window.py, tray_icon.py
  - _Requirements: 2.3, 3.1-3.6, 4.1-4.4, 5.1-5.4_

- [x] 2.1 Write property test for string formatting
  - **Property 3: String formatting with parameters**
  - **Validates: Requirements 2.4**

- [x] 3. Implement language persistence
  - Add config file read/write for INTERFACE_LANGUAGE
  - Implement `set_language()` to save to .env file
  - Implement `get_language()` to read from config
  - Handle missing or invalid language codes with fallback to English
  - _Requirements: 1.3, 2.2_

- [x] 3.1 Write property test for language persistence
  - **Property 4: Language persistence round-trip**
  - **Validates: Requirements 1.3, 2.2**

- [x] 4. Update settings window for localization
  - Import i18n module in `ui/settings_window.py`
  - Replace window title with `t("settings.title")`
  - Replace all sidebar category names with translation calls
  - Replace all group box titles with translation calls
  - Replace all field labels with translation calls
  - Replace all button text with translation calls
  - Replace all tooltips with translation calls
  - Replace all placeholder text with translation calls
  - Replace all informational messages with translation calls
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [ ] 4.1 Write property test for settings window translation
  - **Property 6: Settings window displays all text in selected language**
  - **Validates: Requirements 3.1-3.6**

- [-] 5. Update floating window for localization
  - Import i18n module in `ui/floating_window.py`
  - Replace "Recording..." status with `t("status.recording")`
  - Replace "Processing..." status with `t("status.processing")`
  - Replace "Ready" status with `t("status.ready")`
  - Replace error messages with translation calls
  - Ensure transcription results are NOT translated (display as-is)
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 5.1 Write property test for floating window status messages
  - **Property 7: Floating window status messages are translated**
  - **Validates: Requirements 4.1, 4.2, 4.4**

- [ ] 5.2 Write property test for transcription result preservation
  - **Property 8: Transcription results are not translated**
  - **Validates: Requirements 4.3**

- [x] 6. Update tray icon for localization
  - Import i18n module in `ui/tray_icon.py`
  - Replace menu item text with translation calls (Settings, About, Quit)
  - Replace tooltip text with translation calls
  - Replace notification messages with translation calls
  - Replace about dialog text with translation calls
  - Update "RapidWhisper Launched" notification with `t("tray.notification.launched")`
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 6.1 Write property test for tray icon translation
  - **Property 9: Tray icon displays all text in selected language**
  - **Validates: Requirements 5.1-5.4**

- [x] 7. Implement error message localization
  - Identify all QMessageBox calls in the codebase
  - Replace error message text with translation calls
  - Replace confirmation dialog text with translation calls
  - Replace validation messages with translation calls
  - Ensure log messages remain in English (use separate logging strings)
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 7.1 Write property test for error message translation
  - **Property 10: Error and dialog messages are translated**
  - **Validates: Requirements 6.1, 6.2, 6.3**

- [ ] 7.2 Write property test for English-only logging
  - **Property 11: Logs are always in English**
  - **Validates: Requirements 6.4**

- [x] 8. Checkpoint - Test English and Russian translations
  - Ensure all tests pass
  - Manually test switching between English and Russian
  - Verify all UI elements display correctly in both languages
  - Ask the user if questions arise

- [ ] 9. Implement RTL language support
  - Add RTL detection logic in `is_rtl()` function
  - Implement layout direction switching in main application
  - Update QApplication.setLayoutDirection() when RTL language is selected
  - Update text field alignment for RTL languages
  - Test with Arabic and Urdu (add placeholder translations)
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 9.1 Write property test for RTL detection and layout
  - **Property 12: RTL languages trigger right-to-left layout**
  - **Validates: Requirements 7.1-7.4**

- [x] 10. Implement dynamic language switching
  - Add `reload_translations()` method to settings window
  - Connect language change to UI refresh in settings window
  - Update tray icon menu when language changes
  - Update floating window status text when language changes
  - Emit signal when language changes to notify all components
  - Test switching between multiple languages without restart
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ] 10.1 Write property test for dynamic language switching
  - **Property 13: Dynamic language switching updates all UI**
  - **Validates: Requirements 8.1-8.4**

- [ ] 11. Implement date and time localization
  - Create DATE_FORMATS dictionary with patterns for all 15 languages
  - Implement `format_date(dt, format_type, lang)` function
  - Support format types: "short", "long", "time", "datetime"
  - Update recordings list to use `format_date()` for timestamps
  - Test date formatting for all locales
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [ ] 11.1 Write property test for date formatting
  - **Property 14: Date and time formatting follows locale conventions**
  - **Validates: Requirements 9.1, 9.2, 9.4**

- [ ] 12. Add remaining 13 language translations
  - Add Chinese (zh) translations for all categories
  - Add Hindi (hi) translations for all categories
  - Add Spanish (es) translations for all categories
  - Add French (fr) translations for all categories
  - Add Arabic (ar) translations for all categories
  - Add Bengali (bn) translations for all categories
  - Add Portuguese (pt) translations for all categories
  - Add Urdu (ur) translations for all categories
  - Add Indonesian (id) translations for all categories
  - Add German (de) translations for all categories
  - Add Japanese (ja) translations for all categories
  - Add Turkish (tr) translations for all categories
  - Add Korean (ko) translations for all categories
  - _Requirements: 1.1_

- [ ] 13. Implement translation validation
  - Implement `get_missing_translations()` function
  - Check for missing keys across all languages
  - Return dictionary mapping language codes to missing keys
  - Add logging for missing translations when `t()` is called
  - _Requirements: 10.3, 10.4_

- [ ] 13.1 Write unit test for missing translation detection
  - **Property 15: Missing translation detection**
  - **Validates: Requirements 10.3**

- [ ] 13.2 Write property test for missing translation warnings
  - **Property 16: Missing translation warnings are logged**
  - **Validates: Requirements 10.4**

- [ ] 14. Checkpoint - Comprehensive testing
  - Ensure all tests pass
  - Test all 15 languages in settings window
  - Test RTL languages (Arabic, Urdu) for proper layout
  - Test language switching without restart
  - Test date/time formatting in recordings list
  - Verify error messages appear in selected language
  - Verify logs remain in English
  - Ask the user if questions arise

- [x] 15. Update configuration and documentation
  - Update Config class to include interface_language property
  - Update .env.example with INTERFACE_LANGUAGE setting
  - Add comments explaining language codes
  - Update README with localization information
  - Document how to add new languages
  - _Requirements: 1.3_

- [x] 16. Final integration and polish
  - Verify no hardcoded strings remain in UI code
  - Test all UI components with very long translations
  - Test all UI components with special characters
  - Verify tooltips display correctly in all languages
  - Test startup language detection
  - Verify language persists across application restarts
  - _Requirements: 10.1, 10.2_

## Notes

- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Implementation uses Python with PyQt6 for UI components
- Translation keys use dot notation (e.g., "settings.title")
- All translations are stored in a centralized TRANSLATIONS dictionary
- RTL support requires Qt layout direction changes
- Date formatting uses Python's datetime.strftime() with locale-specific patterns
