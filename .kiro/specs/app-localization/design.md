# Design Document: Application Localization

## Overview

This design implements a comprehensive internationalization (i18n) system for RapidWhisper, supporting 15 languages with dynamic language switching, RTL support, and locale-aware formatting. The system uses a centralized translation module with category-based organization and automatic fallback to English for missing translations.

The design follows a modular approach where:
- A central `i18n.py` module manages all translations and language logic
- UI components call translation functions instead of using hardcoded strings
- Language changes trigger UI updates without requiring application restart
- All translations are stored in structured dictionaries organized by category

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Settings   │  │   Floating   │  │  Tray Icon   │      │
│  │    Window    │  │    Window    │  │              │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
│                            ▼                                 │
│                   ┌────────────────┐                         │
│                   │  I18n Module   │                         │
│                   │  - t(key)      │                         │
│                   │  - set_lang()  │                         │
│                   │  - get_lang()  │                         │
│                   │  - format_date │                         │
│                   └────────┬───────┘                         │
│                            │                                 │
│                            ▼                                 │
│                   ┌────────────────┐                         │
│                   │  Translations  │                         │
│                   │   Dictionary   │                         │
│                   │  (15 langs)    │                         │
│                   └────────────────┘                         │
│                            │                                 │
│                            ▼                                 │
│                   ┌────────────────┐                         │
│                   │  Config (.env) │                         │
│                   │  INTERFACE_    │                         │
│                   │  LANGUAGE=ru   │                         │
│                   └────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### Module Structure

```
utils/
  i18n.py                    # Main i18n module
    - Translation dictionaries (TRANSLATIONS)
    - Translation function (t)
    - Language management (set_language, get_language)
    - Date/time formatting (format_date, format_time)
    - RTL detection (is_rtl)
    - System language detection (detect_system_language)
```

### Translation Key Naming Convention

Translation keys follow a hierarchical dot-notation structure:

```
category.subcategory.key

Examples:
- settings.title
- settings.ai_provider.label
- settings.ai_provider.groq_key
- status.recording
- status.processing
- errors.no_api_key
- tray.menu.settings
- common.save
- common.cancel
```

## Components and Interfaces

### I18n Module (`utils/i18n.py`)

#### Core Functions

```python
def t(key: str, lang: str = None, **kwargs) -> str:
    """
    Translate a key to the specified language.
    
    Args:
        key: Translation key in dot notation (e.g., "settings.title")
        lang: Language code (e.g., "en", "ru"). If None, uses current language.
        **kwargs: Format parameters for string interpolation
        
    Returns:
        Translated string with parameters interpolated
        
    Example:
        t("errors.file_not_found", filename="test.wav")
        # Returns: "File not found: test.wav" (in current language)
    """

def set_language(lang_code: str) -> None:
    """
    Set the current interface language.
    
    Args:
        lang_code: Language code (e.g., "en", "ru", "zh")
        
    Side Effects:
        - Updates global _current_language variable
        - Saves to config file (INTERFACE_LANGUAGE)
        - Emits language_changed signal if using Qt
    """

def get_language() -> str:
    """
    Get the current interface language code.
    
    Returns:
        Current language code (e.g., "en", "ru")
    """

def detect_system_language() -> str:
    """
    Detect the system's default language.
    
    Returns:
        Language code matching system locale, or "en" if not supported
        
    Implementation:
        - Uses locale.getdefaultlocale() on Windows/Linux
        - Uses NSLocale on macOS
        - Maps system locale to supported language codes
    """

def is_rtl(lang_code: str = None) -> bool:
    """
    Check if a language uses right-to-left text direction.
    
    Args:
        lang_code: Language code. If None, uses current language.
        
    Returns:
        True if language is RTL (Arabic, Urdu), False otherwise
    """

def format_date(dt: datetime, format_type: str = "short", lang: str = None) -> str:
    """
    Format a datetime according to locale conventions.
    
    Args:
        dt: Datetime object to format
        format_type: "short", "long", "time", or "datetime"
        lang: Language code. If None, uses current language.
        
    Returns:
        Formatted date/time string
        
    Examples:
        format_date(dt, "short", "en")  # "12/31/2024"
        format_date(dt, "short", "ru")  # "31.12.2024"
        format_date(dt, "time", "en")   # "2:30 PM"
        format_date(dt, "time", "ru")   # "14:30"
    """

def get_missing_translations() -> dict[str, list[str]]:
    """
    Validate translations and find missing keys.
    
    Returns:
        Dictionary mapping language codes to lists of missing keys
        
    Example:
        {
            "zh": ["settings.new_feature", "errors.new_error"],
            "ar": ["settings.new_feature"]
        }
    """
```

#### Translation Dictionary Structure

```python
TRANSLATIONS = {
    "en": {
        "settings": {
            "title": "RapidWhisper Settings",
            "ai_provider": {
                "title": "AI Provider",
                "label": "Provider:",
                "groq_key": "Groq API Key:",
                "openai_key": "OpenAI API Key:",
                # ... more keys
            },
            "app": {
                "title": "Application",
                "hotkey": "Hotkey:",
                # ... more keys
            },
            # ... more categories
        },
        "status": {
            "recording": "Recording...",
            "processing": "Processing...",
            "ready": "Ready",
            # ... more statuses
        },
        "errors": {
            "no_api_key": "No API key configured for {provider}",
            "recording_failed": "Recording failed: {error}",
            # ... more errors
        },
        "tray": {
            "menu": {
                "settings": "Settings",
                "about": "About",
                "quit": "Quit"
            },
            "tooltip": {
                "ready": "RapidWhisper - Ready! Press {hotkey} to record",
                "recording": "RapidWhisper - Recording..."
            },
            "notification": {
                "launched": "RapidWhisper Launched"
            }
        },
        "common": {
            "save": "Save",
            "cancel": "Cancel",
            "ok": "OK",
            "yes": "Yes",
            "no": "No",
            "delete": "Delete",
            "refresh": "Refresh",
            # ... more common words
        }
    },
    "ru": {
        # Russian translations (same structure)
    },
    "zh": {
        # Chinese translations (same structure)
    },
    # ... 12 more languages
}
```

#### Supported Languages

```python
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "native": "English", "rtl": False, "locale": "en_GB"},
    "zh": {"name": "Chinese", "native": "中文", "rtl": False, "locale": "zh_CN"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "rtl": False, "locale": "hi_IN"},
    "es": {"name": "Spanish", "native": "Español", "rtl": False, "locale": "es_ES"},
    "fr": {"name": "French", "native": "Français", "rtl": False, "locale": "fr_FR"},
    "ar": {"name": "Arabic", "native": "العربية", "rtl": True, "locale": "ar_SA"},
    "bn": {"name": "Bengali", "native": "বাংলা", "rtl": False, "locale": "bn_BD"},
    "ru": {"name": "Russian", "native": "Русский", "rtl": False, "locale": "ru_RU"},
    "pt": {"name": "Portuguese", "native": "Português", "rtl": False, "locale": "pt_PT"},
    "ur": {"name": "Urdu", "native": "اردو", "rtl": True, "locale": "ur_PK"},
    "id": {"name": "Indonesian", "native": "Indonesia", "rtl": False, "locale": "id_ID"},
    "de": {"name": "German", "native": "Deutsch", "rtl": False, "locale": "de_DE"},
    "ja": {"name": "Japanese", "native": "日本語", "rtl": False, "locale": "ja_JP"},
    "tr": {"name": "Turkish", "native": "Türkçe", "rtl": False, "locale": "tr_TR"},
    "ko": {"name": "Korean", "native": "한국어", "rtl": False, "locale": "ko_KR"},
}
```

### UI Component Updates

#### Settings Window (`ui/settings_window.py`)

**Changes Required:**
1. Import i18n module: `from utils.i18n import t, is_rtl`
2. Replace all hardcoded strings with `t()` calls
3. Add `reload_translations()` method to update UI when language changes
4. Apply RTL layout when RTL language is selected

**Example Transformation:**

Before:
```python
title = QLabel("Настройки RapidWhisper")
```

After:
```python
title = QLabel(t("settings.title"))
```

**Key Translation Points:**
- Window title
- Sidebar category names (7 categories)
- All group box titles
- All field labels
- All button text
- All tooltips
- All informational messages
- All placeholder text

#### Floating Window (`ui/floating_window.py`)

**Changes Required:**
1. Import i18n module
2. Replace status strings with translation calls
3. Update status messages dynamically

**Key Translation Points:**
- Status messages: "Recording...", "Processing...", "Ready"
- Error messages
- Startup notification message

#### Tray Icon (`ui/tray_icon.py`)

**Changes Required:**
1. Import i18n module
2. Replace menu item text with translations
3. Update tooltip dynamically
4. Translate notification messages

**Key Translation Points:**
- Menu items: Settings, About, Quit
- Tooltip text
- Notification messages
- About dialog text

## Data Models

### Language Configuration

Stored in `.env` file:
```
INTERFACE_LANGUAGE=ru
```

### Translation Data Structure

```python
# Type definitions
TranslationDict = dict[str, Union[str, dict]]
LanguageCode = str  # e.g., "en", "ru", "zh"
TranslationKey = str  # e.g., "settings.title"

# Global state
_current_language: LanguageCode = "en"
_translations: dict[LanguageCode, TranslationDict] = TRANSLATIONS
```

### Date/Time Format Patterns

```python
DATE_FORMATS = {
    "en": {
        "short": "%m/%d/%Y",      # 12/31/2024
        "long": "%B %d, %Y",      # December 31, 2024
        "time": "%I:%M %p",       # 2:30 PM
        "datetime": "%m/%d/%Y %I:%M %p"
    },
    "ru": {
        "short": "%d.%m.%Y",      # 31.12.2024
        "long": "%d %B %Y",       # 31 декабря 2024
        "time": "%H:%M",          # 14:30
        "datetime": "%d.%m.%Y %H:%M"
    },
    # ... patterns for all 15 languages
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Translation function returns valid strings for all keys
*For any* supported language code and any valid translation key, calling t(key, lang) should return a non-empty string.
**Validates: Requirements 2.1**

### Property 2: Fallback to English for missing translations
*For any* supported language and any translation key that doesn't exist in that language, calling t(key, lang) should return the English translation if it exists.
**Validates: Requirements 1.4**

### Property 3: String formatting with parameters
*For any* translation key containing format placeholders and any set of parameters, calling t(key, **params) should return a string with all placeholders replaced by parameter values.
**Validates: Requirements 2.4**

### Property 4: Language persistence round-trip
*For any* supported language code, calling set_language(code) then get_language() should return the same language code, and the code should be persisted to the configuration file.
**Validates: Requirements 1.3, 2.2**

### Property 5: System language detection returns supported language
*For any* system locale, calling detect_system_language() should return a language code that exists in SUPPORTED_LANGUAGES.
**Validates: Requirements 1.2**

### Property 6: Settings window displays all text in selected language
*For any* supported language, when the settings window is created with that language active, all UI elements (labels, buttons, tooltips, group titles, info messages) should contain text from that language's translation dictionary.
**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**

### Property 7: Floating window status messages are translated
*For any* supported language and any status type (recording, processing, error), the floating window should display the status message in the selected language.
**Validates: Requirements 4.1, 4.2, 4.4**

### Property 8: Transcription results are not translated
*For any* transcription result text, the floating window should display the exact result text without applying any translation.
**Validates: Requirements 4.3**

### Property 9: Tray icon displays all text in selected language
*For any* supported language, the tray icon's menu items, tooltips, and notifications should all display text in the selected language.
**Validates: Requirements 5.1, 5.2, 5.3, 5.4**

### Property 10: Error and dialog messages are translated
*For any* supported language, all user-facing error messages, confirmation dialogs, and validation messages should display in the selected language.
**Validates: Requirements 6.1, 6.2, 6.3**

### Property 11: Logs are always in English
*For any* selected interface language, all log messages should be written in English regardless of the interface language setting.
**Validates: Requirements 6.4**

### Property 12: RTL languages trigger right-to-left layout
*For any* RTL language (Arabic, Urdu), when that language is selected, is_rtl() should return True, the application layout direction should be RightToLeft, and text fields should align right. For all non-RTL languages, is_rtl() should return False and layout should be LeftToRight.
**Validates: Requirements 7.1, 7.2, 7.3, 7.4**

### Property 13: Dynamic language switching updates all UI
*For any* two different supported languages, switching from one to the other should update all visible UI text (settings window, tray icon, floating window) to the new language without requiring application restart.
**Validates: Requirements 8.1, 8.2, 8.3, 8.4**

### Property 14: Date and time formatting follows locale conventions
*For any* datetime value and any supported language, format_date() should return a string formatted according to that language's locale conventions (date order, separators, 12/24 hour format).
**Validates: Requirements 9.1, 9.2, 9.4**

### Property 15: Missing translation detection
*For any* language with incomplete translations, get_missing_translations() should return a list containing all translation keys that exist in English but not in that language.
**Validates: Requirements 10.3**

### Property 16: Missing translation warnings are logged
*For any* translation key that doesn't exist in the current language, calling t(key) should log a warning message containing the missing key and language code.
**Validates: Requirements 10.4**

## Error Handling

### Translation Errors

**Missing Translation Key:**
- Behavior: Return English translation if available, otherwise return the key itself
- Log: Warning level with format "Translation missing: {key} for language {lang}"
- User Impact: Minimal - English text appears instead of translated text

**Invalid Language Code:**
- Behavior: Fall back to English
- Log: Warning level with format "Invalid language code: {code}, falling back to English"
- User Impact: Interface appears in English

**Malformed Translation String:**
- Behavior: Return the malformed string as-is
- Log: Error level with format "Malformed translation: {key} in {lang}"
- User Impact: Potentially broken text display

### File System Errors

**Config File Not Writable:**
- Behavior: Language change succeeds in memory but not persisted
- Log: Error level with format "Failed to save language to config: {error}"
- User Impact: Language resets to default on next application start

**Config File Corrupted:**
- Behavior: Use default language (English)
- Log: Error level with format "Failed to read language from config: {error}"
- User Impact: Interface appears in English

### RTL Layout Errors

**RTL Layout Not Supported:**
- Behavior: Display text in RTL language but with LTR layout
- Log: Warning level with format "RTL layout not fully supported on this platform"
- User Impact: Text appears but layout may not be ideal

## Testing Strategy

### Unit Testing

Unit tests will focus on specific examples and edge cases:

**I18n Module Tests:**
- Test that SUPPORTED_LANGUAGES contains exactly 15 entries
- Test that each language has required metadata (name, native, rtl, locale)
- Test translation key lookup for known keys
- Test fallback behavior with missing keys
- Test string formatting with various parameter types
- Test RTL detection for Arabic and Urdu
- Test date formatting for each locale
- Test get_missing_translations() with incomplete dictionaries

**UI Component Tests:**
- Test that settings window calls t() for all text elements
- Test that floating window updates status text correctly
- Test that tray icon menu items are created with translated text
- Test that language change triggers UI refresh

**Edge Cases:**
- Empty translation key
- Translation key with special characters
- Format parameters with None values
- Format parameters with non-string types
- Very long translated strings (UI overflow)
- Switching languages rapidly
- RTL to LTR and LTR to RTL transitions

### Property-Based Testing

Property tests will verify universal properties across all inputs:

**Configuration:**
- Minimum 100 iterations per property test
- Use Hypothesis for generating test data
- Tag each test with feature name and property number

**Test Generators:**
```python
# Generate random language codes
@st.composite
def language_code(draw):
    return draw(st.sampled_from(list(SUPPORTED_LANGUAGES.keys())))

# Generate random translation keys
@st.composite
def translation_key(draw):
    category = draw(st.sampled_from(["settings", "status", "errors", "tray", "common"]))
    subcategory = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("L",))))
    key = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("L",))))
    return f"{category}.{subcategory}.{key}"

# Generate random datetime values
@st.composite
def datetime_value(draw):
    return draw(st.datetimes(min_value=datetime(2000, 1, 1), max_value=datetime(2030, 12, 31)))

# Generate random format parameters
@st.composite
def format_params(draw):
    num_params = draw(st.integers(min_value=0, max_value=5))
    params = {}
    for i in range(num_params):
        key = draw(st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=("L",))))
        value = draw(st.one_of(st.text(), st.integers(), st.floats(allow_nan=False)))
        params[key] = value
    return params
```

**Property Test Examples:**

```python
@given(language_code(), translation_key())
def test_property_1_translation_returns_string(lang, key):
    """Feature: app-localization, Property 1: Translation function returns valid strings"""
    # Assume key exists in translations
    if key_exists_in_translations(key, lang):
        result = t(key, lang)
        assert isinstance(result, str)
        assert len(result) > 0

@given(language_code())
def test_property_4_language_persistence(lang):
    """Feature: app-localization, Property 4: Language persistence round-trip"""
    set_language(lang)
    assert get_language() == lang
    # Verify persisted to config
    from core.config import Config
    config = Config()
    assert config.interface_language == lang

@given(language_code())
def test_property_12_rtl_detection(lang):
    """Feature: app-localization, Property 12: RTL languages trigger right-to-left layout"""
    set_language(lang)
    expected_rtl = lang in ["ar", "ur"]
    assert is_rtl() == expected_rtl
    
    if expected_rtl:
        assert QApplication.layoutDirection() == Qt.LayoutDirection.RightToLeft
    else:
        assert QApplication.layoutDirection() == Qt.LayoutDirection.LeftToRight

@given(datetime_value(), language_code())
def test_property_14_date_formatting(dt, lang):
    """Feature: app-localization, Property 14: Date formatting follows locale conventions"""
    result = format_date(dt, "short", lang)
    assert isinstance(result, str)
    assert len(result) > 0
    # Verify format matches locale conventions
    locale_info = SUPPORTED_LANGUAGES[lang]
    # Check that result contains date components
    assert str(dt.year) in result or str(dt.year)[2:] in result
```

### Integration Testing

Integration tests will verify that components work together:

**Language Switching Flow:**
1. Start application with default language
2. Open settings window
3. Change language
4. Save settings
5. Verify all UI components update
6. Restart application
7. Verify language persisted

**RTL Language Flow:**
1. Switch to Arabic
2. Verify layout direction changes
3. Verify text alignment changes
4. Open all windows and verify RTL layout
5. Switch back to English
6. Verify layout returns to LTR

**Translation Coverage:**
1. Iterate through all UI components
2. Verify no hardcoded strings remain
3. Verify all text uses t() function
4. Verify all translation keys exist in all languages

### Manual Testing Checklist

- [ ] Test each of 15 languages in settings window
- [ ] Verify all UI text translates correctly
- [ ] Test RTL languages (Arabic, Urdu) for proper layout
- [ ] Test language switching without restart
- [ ] Test date/time formatting in recordings list
- [ ] Verify error messages appear in selected language
- [ ] Test with very long translations (German, Finnish)
- [ ] Test with special characters (Chinese, Arabic, Hindi)
- [ ] Verify tooltips translate correctly
- [ ] Test tray icon menu in all languages
- [ ] Verify startup notification in selected language
- [ ] Test that transcription results are NOT translated
- [ ] Verify logs remain in English regardless of UI language

## Implementation Notes

### Translation File Organization

For maintainability, consider splitting translations into separate files:

```
utils/
  i18n/
    __init__.py          # Main module with t(), set_language(), etc.
    translations/
      en.py              # English translations
      ru.py              # Russian translations
      zh.py              # Chinese translations
      # ... 12 more files
```

Each translation file exports a dictionary:
```python
# translations/en.py
TRANSLATIONS = {
    "settings": {
        "title": "RapidWhisper Settings",
        # ...
    },
    # ...
}
```

### Performance Considerations

- Load all translations at startup (acceptable for 15 languages)
- Cache formatted dates to avoid repeated formatting
- Use lazy loading for large translation sections if needed
- Consider using Qt's built-in translation system (QTranslator) for better integration

### Future Enhancements

- Add translation management UI for contributors
- Support for regional variants (en-US vs en-GB)
- Pluralization rules for different languages
- Number formatting (thousands separators, decimal points)
- Currency formatting
- Automatic translation updates from translation service
- Translation memory for consistency
- Context-aware translations (same word, different meanings)

### Migration Strategy

1. **Phase 1:** Create i18n module with English and Russian translations
2. **Phase 2:** Update settings window to use translations
3. **Phase 3:** Update floating window and tray icon
4. **Phase 4:** Add remaining 13 languages
5. **Phase 5:** Implement RTL support
6. **Phase 6:** Add date/time localization
7. **Phase 7:** Comprehensive testing and bug fixes

### Translation Guidelines

For translators working on new languages:

1. **Maintain Consistency:** Use the same terms throughout the application
2. **Keep It Concise:** UI space is limited, avoid overly long translations
3. **Preserve Formatting:** Keep {placeholders} intact in translated strings
4. **Test RTL:** If translating RTL language, test the actual layout
5. **Cultural Sensitivity:** Adapt idioms and expressions appropriately
6. **Technical Terms:** Some terms (API, Whisper, etc.) may not need translation
7. **Keyboard Shortcuts:** Consider local keyboard layouts when translating shortcuts

### Accessibility Considerations

- Ensure translated text maintains proper contrast ratios
- Verify screen readers work with translated text
- Test keyboard navigation with RTL languages
- Ensure translated tooltips are not too long
- Verify translated error messages are clear and actionable
