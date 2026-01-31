# Миграция конфигурации: .env → config.jsonc

## Обзор

Все настройки приложения перенесены из `.env` файла в более читаемый формат JSONC (JSON с комментариями).

### Преимущества новой структуры:

1. **Читаемость**: `.env` файл стал нечитаемым из-за огромного JSON в `FORMATTING_APP_PROMPTS`
2. **Комментарии**: JSONC поддерживает комментарии для документирования настроек
3. **Структура**: Иерархическая структура вместо плоского списка переменных
4. **Промпты**: Каждый промпт в отдельном файле вместо одной огромной строки
5. **Валидация**: JSON легче валидировать и проверять на ошибки

## Структура файлов

```
RapidWhisper/
├── config.jsonc                    # Основной файл конфигурации (в git)
├── config.jsonc.example            # Пример конфигурации (в git)
├── secrets.json                    # API ключи (НЕ в git!)
├── secrets.json.example            # Пример secrets (в git)
├── config/
│   └── prompts/                    # Промпты для форматирования (в git)
│       ├── notion.txt
│       ├── obsidian.txt
│       ├── markdown.txt
│       ├── word.txt
│       ├── libreoffice.txt
│       ├── vscode.txt
│       ├── whatsapp.txt
│       ├── bbcode.txt
│       └── _fallback.txt
├── .env                            # Старый формат (backup, НЕ в git)
├── .env.example                    # Пример .env (в git)
└── .gitignore                      # secrets.json добавлен!
```

## Миграция

### Автоматическая миграция

Запустите скрипт миграции:

```bash
python migrate_to_jsonc.py
```

Скрипт:
1. Читает все настройки из `.env`
2. Создает `config.jsonc` с правильной структурой
3. Создает `secrets.json` с API ключами
4. Сохраняет каждый промпт в отдельный файл `config/prompts/*.txt`
5. Обновляет `.gitignore` (добавляет `secrets.json`)
6. Сохраняет `.env` как backup

### Ручная миграция

Если нужно мигрировать вручную:

1. Скопируйте `config.jsonc.example` в `config.jsonc`
2. Заполните значения из вашего `.env` файла
3. Создайте директорию `config/prompts/`
4. Скопируйте промпты из `FORMATTING_APP_PROMPTS` в отдельные файлы

## Формат config.jsonc

### Основные секции:

```jsonc
{
  // AI Provider Configuration
  "ai_provider": {
    "provider": "groq",
    "api_keys": {
      "openai": "",
      "groq": "your_api_key_here",
      "glm": ""
    }
  },

  // Application Settings
  "application": {
    "app_user_model_id": "RapidWhisper",
    "hotkey": "ctrl+space"
  },

  // Audio Settings
  "audio": {
    "silence_threshold": 0.02,
    "silence_duration": 1.5,
    "manual_stop": false
  },

  // Window Settings
  "window": {
    "width": 400,
    "height": 120,
    "opacity": 100
  },

  // Formatting Settings
  "formatting": {
    "enabled": true,
    "provider": "groq",
    "model": "",
    "temperature": 0.3,
    "web_app_keywords": {
      "whatsapp": ["whatsapp", "telegram", "discord"]
    },
    "app_prompts": {
      "whatsapp": "config/prompts/whatsapp.txt"
    }
  }
}
```

## Использование в коде

### Загрузка конфигурации

```python
from core.config_loader import get_config_loader

# Получить loader
loader = get_config_loader()

# Загрузить конфигурацию
config = loader.load()

# Получить значение по пути
provider = loader.get("ai_provider.provider")
width = loader.get("window.width", default=400)
```

### Загрузка промптов

```python
# Получить промпт для приложения
whatsapp_prompt = loader.get_prompt("whatsapp")
fallback_prompt = loader.get_prompt("_fallback")
```

### FormattingConfig

```python
from services.formatting_config import FormattingConfig
from core.config_loader import get_config_loader

# Новый способ (рекомендуется)
loader = get_config_loader()
config = FormattingConfig.from_config(loader)

# Старый способ (deprecated, но работает)
config = FormattingConfig.from_env()
```

## Обратная совместимость

Код поддерживает оба формата:

1. **Приоритет**: Сначала пытается загрузить `config.jsonc`
2. **Fallback**: Если `config.jsonc` не найден, загружает из `.env`
3. **Предупреждение**: При использовании `.env` выводится предупреждение о deprecated формате

## Редактирование промптов

### Через файлы

Просто отредактируйте файл в `config/prompts/`:

```bash
# Открыть в редакторе
notepad config/prompts/whatsapp.txt

# Или в VS Code
code config/prompts/whatsapp.txt
```

### Через UI

Настройки форматирования можно редактировать через UI приложения:
- Settings → Formatting → Edit Prompts

## Проверка конфигурации

Запустите тест для проверки:

```bash
python test_config_loader.py
```

Тест проверяет:
- Загрузку `config.jsonc`
- Парсинг JSONC (с комментариями)
- Загрузку промптов из файлов
- Создание `FormattingConfig`
- Получение значений по путям

## Troubleshooting

### Ошибка: "Configuration file not found"

Решение:
```bash
# Запустите миграцию
python migrate_to_jsonc.py

# Или скопируйте пример
cp config.jsonc.example config.jsonc
```

### Ошибка: "Failed to parse JSONC file"

Проблема: Синтаксическая ошибка в JSON

Решение:
1. Проверьте запятые (trailing commas разрешены)
2. Проверьте кавычки (должны быть двойные `"`)
3. Используйте JSON validator

### Промпты не загружаются

Проблема: Файлы промптов не найдены

Решение:
```bash
# Проверьте наличие файлов
ls config/prompts/

# Запустите миграцию заново
python migrate_to_jsonc.py
```

## Миграция тестов

Тесты также нужно обновить для использования нового формата:

### Старый код:
```python
with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
    f.write("FORMATTING_ENABLED=true\n")
    f.write(f"FORMATTING_APP_PROMPTS={json.dumps(...)}\n")
```

### Новый код:
```python
# Создать временный config.jsonc
config = {
    "formatting": {
        "enabled": True,
        "app_prompts": {...}
    }
}
with open("test_config.jsonc", "w") as f:
    json.dump(config, f)

# Использовать ConfigLoader
loader = ConfigLoader("test_config.jsonc")
```

## Дальнейшие шаги

1. ✅ Миграция завершена
2. ✅ Тесты обновлены
3. ⏳ Обновить документацию
4. ⏳ Обновить UI для редактирования промптов
5. ⏳ Удалить deprecated код после полной миграции

## Вопросы?

Если возникли проблемы с миграцией:
1. Проверьте логи: `rapidwhisper.log`
2. Запустите тесты: `python test_config_loader.py`
3. Создайте issue на GitHub
