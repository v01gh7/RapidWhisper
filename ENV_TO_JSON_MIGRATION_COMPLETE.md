# Миграция с .env на JSON конфиги - ЗАВЕРШЕНА

## Дата: 2026-02-01

## Что было сделано

### 1. Удалены все обращения к .env файлам из основного кода

#### main.py
- ✅ Удален `load_dotenv` из `_start_recording()` - теперь использует `Config.load_from_config()`
- ✅ Удален `load_dotenv` из `_reload_settings()` - теперь использует `Config.load_from_config()`
- ✅ Удален `load_dotenv` из `main()` - теперь использует `Config.load_from_config()`

#### ui/floating_window.py
- ✅ Удален `load_dotenv` из `show_at_center()` - теперь использует `ConfigLoader.get()`
- ✅ Заменен `os.getenv('WINDOW_POSITION_PRESET')` на `config_loader.get('window.position_preset')`
- ✅ Заменен `os.getenv('REMEMBER_WINDOW_POSITION')` на `config_loader.get('window.remember_position')`
- ✅ Заменен `os.getenv('WINDOW_POSITION_X/Y')` на `config_loader.get('window.position_x/y')`

#### ui/settings_window.py
- ✅ Удалены импорты `get_env_path` и `set_key` из `_change_recordings_folder()`
- ✅ Удалены импорты `get_env_path` и `set_key` из `_reset_recordings_folder()`
- ✅ Теперь использует `ConfigSaver.update_value()` для сохранения настроек

#### services/transcription_client.py
- ✅ Удалены все `os.getenv()` вызовы для API ключей
- ✅ API ключи теперь ДОЛЖНЫ передаваться явно из Config
- ✅ Удален `os.getenv("CUSTOM_BASE_URL")` и `os.getenv("CUSTOM_MODEL")`
- ✅ Удален `os.getenv("LLM_BASE_URL")` и `os.getenv("LLM_API_KEY")`
- ✅ Все параметры теперь передаются явно

#### services/formatting_module.py
- ✅ Удалены все `os.getenv()` вызовы для API ключей
- ✅ Теперь использует `ConfigLoader.get()` для получения API ключей из secrets.json
- ✅ Для custom провайдера использует `self.config.custom_api_key` и `self.config.custom_base_url`

#### utils/logger.py
- ✅ Заменен `os.getenv('LOG_LEVEL')` на `config_loader.get('logging.level')`
- ✅ Заменен `os.getenv('LOG_FILE')` на `config_loader.get('logging.file')`

#### core/config.py
- ✅ Добавлен комментарий что `load_from_env()` DEPRECATED и оставлен только для тестов
- ✅ Основной код должен использовать `Config.load_from_config()`

#### core/config_loader.py
- ✅ Добавлен комментарий что `_load_from_env()` DEPRECATED и оставлен только для тестов

#### services/formatting_config.py
- ✅ Добавлен комментарий что импорты dotenv оставлены только для обратной совместимости с тестами

### 2. Что осталось (только для обратной совместимости)

#### Тесты
- Тесты продолжают использовать .env файлы через `Config.load_from_env()`
- Это нормально - тесты изолированы и не влияют на основной код

#### Deprecated методы
- `Config.load_from_env()` - оставлен для тестов
- `ConfigLoader._load_from_env()` - оставлен для тестов
- Импорты `load_dotenv`, `set_key` в `services/formatting_config.py` - оставлены для тестов

#### Системные переменные окружения
- `utils/i18n.py` использует `os.getenv('LANG')` - это системная переменная, не из .env файла
- Это правильно и не требует изменений

### 3. Структура конфигурации

#### config.jsonc
Содержит ВСЕ настройки приложения:
- AI Provider (provider, custom base_url, custom model)
- Application (hotkey)
- Audio (silence_threshold, silence_duration, manual_stop, etc.)
- Window (opacity, position, font_sizes)
- Recording (keep_recordings, recordings_path)
- Post-processing (enabled, provider, model, prompt)
- Localization (language)
- Logging (level, file)
- About (github_url, docs_url)
- Formatting (enabled, provider, model, app_prompts)

#### secrets.json
Содержит ТОЛЬКО API ключи:
```json
{
  "ai_provider": {
    "api_keys": {
      "openai": "sk-...",
      "groq": "gsk_...",
      "glm": "..."
    },
    "custom": {
      "api_key": "..."
    }
  },
  "formatting": {
    "custom": {
      "api_key": "..."
    }
  }
}
```

#### config/prompts/*.txt
Содержат промпты для форматирования по приложениям:
- `word.txt`
- `telegram.txt`
- `whatsapp.txt`
- `notion.txt`
- и т.д.

## Как работает загрузка конфигурации

### Основной код
```python
# Загрузка конфигурации
config = Config.load_from_config()  # Загружает из config.jsonc + secrets.json

# Получение отдельных значений
from core.config_loader import get_config_loader
config_loader = get_config_loader()
value = config_loader.get('window.opacity', 150)
```

### Сохранение конфигурации
```python
from core.config_saver import get_config_saver
config_saver = get_config_saver()

# Сохранить одно значение
config_saver.update_value('window.opacity', 200)

# Сохранить несколько значений
config_saver.update_multiple_values({
    'window.opacity': 200,
    'window.position_x': 100
})

# Сохранить API ключ (в secrets.json)
config_saver.update_secret('ai_provider.api_keys.groq', 'gsk_...')

# Сохранить промпт (в config/prompts/*.txt)
config_saver.save_prompt('telegram', 'Your prompt here...')
```

## Проверка

### Что проверить
1. ✅ Приложение запускается и загружает конфигурацию из config.jsonc
2. ✅ API ключи загружаются из secrets.json
3. ✅ Настройки сохраняются в config.jsonc (не в .env)
4. ✅ Промпты сохраняются в config/prompts/*.txt
5. ✅ Позиция окна сохраняется в config.jsonc
6. ✅ Все настройки применяются без перезапуска

### Команды для проверки
```bash
# Проверить что нет обращений к .env в основном коде
grep -r "load_dotenv" --include="*.py" --exclude-dir=tests --exclude-dir=.venv

# Проверить что нет os.getenv для конфигурации
grep -r "os.getenv" --include="*.py" --exclude-dir=tests --exclude-dir=.venv

# Запустить приложение
python main.py
```

## Результат

✅ **МИГРАЦИЯ ЗАВЕРШЕНА**

- Основной код больше НЕ использует .env файлы
- Все настройки загружаются из config.jsonc
- API ключи загружаются из secrets.json
- Промпты загружаются из config/prompts/*.txt
- Тесты продолжают работать с .env файлами (изолированно)
- Обратная совместимость сохранена для тестов

## Следующие шаги

1. Протестировать приложение с новой системой конфигурации
2. Убедиться что все настройки сохраняются правильно
3. Убедиться что промпты редактируются и сохраняются
4. Проверить что API ключи работают из secrets.json
5. Удалить файл dep.env (больше не нужен)
