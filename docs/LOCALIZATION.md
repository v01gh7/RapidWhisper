# Localization Guide

RapidWhisper supports 15 languages with full interface localization.

## Supported Languages

- 🇬🇧 English (en, en-us, en-gb)
- 🇨🇳 Chinese (zh)
- 🇮🇳 Hindi (hi)
- 🇪🇸 Spanish (es)
- 🇫🇷 French (fr)
- 🇸🇦 Arabic (ar) - RTL support
- 🇧🇩 Bengali (bn)
- 🇷🇺 Russian (ru)
- 🇵🇹 Portuguese (pt)
- 🇵🇰 Urdu (ur) - RTL support
- 🇮🇩 Indonesian (id)
- 🇩🇪 German (de)
- 🇯🇵 Japanese (ja)
- 🇹🇷 Turkish (tr)
- 🇰🇷 Korean (ko)

## Changing Interface Language

### Via Settings Window

1. Open RapidWhisper settings (click tray icon)
2. Go to "Languages" tab
3. Click on your preferred language
4. Click "Save"
5. Interface updates immediately

### Via Configuration File

Edit `.env` file:

```env
# Interface language
# Options: en, en-us, en-gb, ru, zh, hi, es, fr, ar, bn, pt, ur, id, de, ja, tr, ko
INTERFACE_LANGUAGE=en-us
```

## Automatic Language Detection

On first launch, RapidWhisper automatically detects your system language:
- Windows: Uses system locale
- macOS: Uses system locale
- Linux: Uses `LANG` environment variable

If your system language is not supported, English is used as default.

## Adding a New Language

### 1. Create Translation File

Create `utils/translations/{language_code}.json`:

```json
{
  "settings": {
    "title": "Your Translation Here",
    ...
  },
  "status": {
    "recording": "Recording...",
    "processing": "Processing...",
    "ready": "Ready"
  },
  ...
}
```

### 2. Update Supported Languages

Edit `utils/i18n.py`:

```python
SUPPORTED_LANGUAGES = {
    "xx": {
        "name": "Language Name",
        "native": "Native Name",
        "rtl": False,  # True for RTL languages
        "locale": "xx_XX"
    },
    ...
}
```

### 3. Add Language Button

Edit `ui/settings_window.py` in `_create_languages_tab()`:

```python
self._add_language_button(
    "XX",  # Country code
    "Language Name",
    "xx",  # Language code
    grid_layout,
    row, col
)
```

### 4. Test Translation

1. Run application
2. Switch to new language
3. Verify all UI elements are translated
4. Check for missing translations in logs

## Translation Keys Structure

Translations use dot notation:

```
category.subcategory.key
```

### Categories

- `settings.*` - Settings window
- `status.*` - Status messages
- `errors.*` - Error messages
- `tray.*` - Tray icon and notifications
- `common.*` - Common UI elements

### Example

```json
{
  "settings": {
    "title": "Settings",
    "ai_provider": {
      "title": "AI Provider",
      "label": "Provider:"
    }
  }
}
```

Usage in code:

```python
from utils.i18n import t

window_title = t("settings.title")
provider_label = t("settings.ai_provider.label")
```

## String Formatting

Translations support parameter substitution:

```json
{
  "errors": {
    "file_not_found": "File not found: {filename}"
  }
}
```

Usage:

```python
error_msg = t("errors.file_not_found", filename="test.wav")
# Result: "File not found: test.wav"
```

## RTL (Right-to-Left) Languages

Arabic and Urdu are RTL languages. The system automatically:
- Detects RTL languages
- Adjusts layout direction
- Mirrors UI elements

To check if current language is RTL:

```python
from utils.i18n import is_rtl

if is_rtl():
    # Apply RTL-specific logic
    pass
```

## Translation Validation

Check for missing translations:

```python
from utils.i18n import get_missing_translations

missing = get_missing_translations()
# Returns: {"zh": ["settings.new_key"], ...}
```

## Best Practices

### 1. Keep Keys Consistent

Use the same key structure across all languages:

```json
// ✅ Good
{"settings": {"title": "Settings"}}

// ❌ Bad
{"settings_title": "Settings"}
```

### 2. Preserve Formatting

Keep HTML tags and formatting:

```json
{
  "info": "💡 <b>Tip:</b> This is important"
}
```

### 3. Handle Plurals

Use separate keys for singular/plural:

```json
{
  "file": "file",
  "files": "files"
}
```

### 4. Context Matters

Provide context in key names:

```json
{
  "button_save": "Save",
  "status_saved": "Saved"
}
```

### 5. Test with Long Text

Some languages (German, Russian) have longer words. Test UI with long translations.

## Logging

All log messages remain in English for debugging purposes. Use separate strings for logs:

```python
# UI message (translated)
self.show_message(t("errors.connection_failed"))

# Log message (English only)
logger.error("Connection failed: timeout after 30s")
```

## Troubleshooting

### Translation Not Showing

1. Check translation file exists: `utils/translations/{lang}.json`
2. Verify JSON syntax is valid
3. Check key path matches exactly
4. Look for warnings in `rapidwhisper.log`

### Missing Translations

Check logs for warnings:

```
WARNING - Translation missing: settings.new_key for language ru
```

Add missing key to translation file.

### Language Not Detected

1. Check system locale settings
2. Verify language code in `SUPPORTED_LANGUAGES`
3. Set manually in `.env` file

## Contributing Translations

We welcome translations! To contribute:

1. Fork the repository
2. Create translation file for your language
3. Test thoroughly
4. Submit pull request

See `CONTRIBUTING.md` for details.

## Resources

- [Translation Files](../utils/translations/)
- [i18n Module](../utils/i18n.py)
- [Settings Window](../ui/settings_window.py)
- [Configuration Guide](./settings_guide.md)
