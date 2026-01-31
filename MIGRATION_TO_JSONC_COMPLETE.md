# Миграция на config.jsonc завершена

## Что изменилось

Приложение полностью перешло с `.env` файлов на `config.jsonc` и `secrets.json`.

### Структура конфигурации

```
config.jsonc          # Основная конфигурация (в .gitignore)
secrets.json          # API ключи (в .gitignore)
config/prompts/*.txt  # Промпты форматирования (в git)
```

### Изменения в коде

1. **FormattingConfig**:
   - `from_env()` теперь загружает из `config.jsonc` (имя метода сохранено для обратной совместимости)
   - `save_to_env()` теперь сохраняет в `config.jsonc` (имя метода сохранено для обратной совместимости)
   - Удален метод `to_env()` - больше не нужен
   - Удален код парсинга `.env` файлов

2. **SettingsWindow**:
   - `_save_settings()` сохраняет в `config.jsonc` и `secrets.json` через `ConfigSaver`
   - Все вызовы `FormattingConfig.from_env()` и `save_to_env()` работают с `config.jsonc`

3. **Другие модули**:
   - `services/transcription_client.py` - использует `FormattingConfig.from_env()`
   - `services/formatting_module.py` - использует `FormattingConfig.from_env()`

### Тесты

Обновлены интеграционные тесты:
- `tests/test_formatting_settings_integration.py` - полностью переписаны для работы с `config.jsonc`
- Удалены тесты миграции из `.env` (больше не актуально)
- Все тесты используют временные `config.jsonc` файлы

### Обратная совместимость

Методы `from_env()` и `save_to_env()` сохранены для обратной совместимости, но теперь работают с `config.jsonc`:
- `from_env()` → загружает из `config.jsonc`
- `save_to_env()` → сохраняет в `config.jsonc`

Параметр `env_path` в этих методах игнорируется (оставлен только для совместимости с тестами).

### Промпты форматирования

Промпты сохраняются в `config/prompts/` относительно текущей директории проекта:
- Это правильное поведение - промпты являются частью проекта
- Промпты должны быть в git (не в .gitignore)
- При сохранении конфигурации промпты автоматически сохраняются в файлы

## Проверка

Все тесты проходят:
```bash
uv run pytest tests/test_formatting_settings_integration.py -xvs
```

Результат: **3 passed**

## Что дальше

Приложение полностью работает с `config.jsonc`. Файлы `.env` больше не используются для конфигурации форматирования.
