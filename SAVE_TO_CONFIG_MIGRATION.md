# Миграция сохранения настроек на config.jsonc

## Проблема

После миграции с `.env` на `config.jsonc` приложение **загружало** настройки из нового формата, но **сохраняло** их обратно в старый `.env` файл. Это приводило к потере всех настроек при изменении через UI.

## Решение

Обновлены все места сохранения настроек для использования `config.jsonc` и `secrets.json`.

## Изменённые файлы

### 1. `services/formatting_config.py`

**Добавлен новый метод `save_to_config()`:**
- Сохраняет настройки форматирования в `config.jsonc`
- Сохраняет промпты в отдельные файлы `config/prompts/*.txt`
- Сохраняет API ключи в `secrets.json`

**Обновлён метод `save_to_env()`:**
- Теперь по умолчанию вызывает `save_to_config()`
- Старый формат используется только если явно указан путь к `.env` (для тестов)

### 2. `core/config_saver.py`

**Добавлен метод `update_multiple_values()`:**
- Позволяет обновить несколько значений за один раз
- Более эффективно, чем множественные вызовы `update_value()`

### 3. `utils/i18n.py`

**Обновлена функция `set_language()`:**
- Использует `ConfigSaver.update_value()` вместо `set_key()`
- Сохраняет язык в `config.jsonc` по пути `localization.language`

### 4. `ui/floating_window.py`

**Обновлён метод `save_position()`:**
- Использует `ConfigSaver.update_multiple_values()` вместо прямой записи в `.env`
- Сохраняет позицию окна в `config.jsonc`:
  - `window.position_x`
  - `window.position_y`
  - `window.position_preset`

### 5. `ui/settings_window.py`

**Обновлён метод `_save_settings()`:**
- Полностью переписан для использования `config.jsonc` и `secrets.json`
- Разделяет настройки на:
  - **config.jsonc**: все публичные настройки (окно, аудио, пост-обработка и т.д.)
  - **secrets.json**: API ключи (groq, openai, glm, custom)
- Использует `ConfigSaver.update_multiple_values()` для эффективного сохранения

**Обновлены методы работы с папкой записей:**
- `_on_change_folder_clicked()`: использует `ConfigSaver.update_value()`
- `_on_reset_folder_clicked()`: использует `ConfigSaver.update_value()`

**Методы работы с форматированием:**
- `_edit_prompt()`: вызывает `save_to_config()` вместо `save_to_env()`
- `_delete_application()`: вызывает `save_to_config()` вместо `save_to_env()`
- `_on_add_application_clicked()`: вызывает `save_to_config()` вместо `save_to_env()`
- `_on_web_keywords_clicked()`: вызывает `save_to_config()` вместо `save_to_env()`

## Структура сохранения

### config.jsonc (публичные настройки)
```jsonc
{
  "ai_provider": {
    "provider": "groq",
    "custom": {
      "base_url": "...",
      "model": "..."
    }
  },
  "application": {
    "hotkey": "ctrl+space"
  },
  "audio": {
    "silence_threshold": 0.02,
    "silence_duration": 2.5,
    // ...
  },
  "window": {
    "width": 400,
    "height": 120,
    "opacity": 76,
    "position_x": 1493,
    "position_y": 39,
    // ...
  },
  "recording": {
    "keep_recordings": true,
    "recordings_path": "D:/RapidWhisperCustom"
  },
  "post_processing": {
    "enabled": true,
    "provider": "groq",
    // ...
  },
  "localization": {
    "language": "ru"
  },
  "formatting": {
    "enabled": true,
    "provider": "groq",
    // ...
  }
}
```

### secrets.json (приватные данные)
```json
{
  "api_keys": {
    "openai": "sk-...",
    "groq": "gsk_...",
    "glm": "..."
  },
  "custom_providers": {
    "api_key": "...",
    "formatting_api_key": "..."
  }
}
```

### config/prompts/*.txt (промпты форматирования)
- `notion.txt`
- `obsidian.txt`
- `markdown.txt`
- `word.txt`
- `libreoffice.txt`
- `vscode.txt`
- `whatsapp.txt`
- `bbcode.txt`
- `_fallback.txt`

## Обратная совместимость

- Метод `save_to_env()` сохранён для тестов
- При вызове без параметров автоматически использует новый формат
- При вызове с путём к `.env` использует старый формат (для тестов)

## Тестирование

Все существующие тесты продолжают работать:
- `test_formatting_config_properties.py` - ✅ PASSED
- Тесты используют явный путь к `.env`, поэтому работают со старым форматом

## Результат

Теперь все изменения настроек через UI корректно сохраняются в `config.jsonc` и `secrets.json`, и не теряются при перезапуске приложения.
