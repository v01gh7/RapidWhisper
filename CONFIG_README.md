# Конфигурация RapidWhisper

## Быстрый старт

### 1. Миграция из .env

Если у вас уже есть `.env` файл:

```bash
python migrate_to_jsonc.py
```

Это создаст:
- `config.jsonc` - основной файл конфигурации
- `config/prompts/*.txt` - промпты для форматирования

### 2. Новая установка

Скопируйте пример конфигурации:

```bash
copy config.jsonc.example config.jsonc
```

Отредактируйте `config.jsonc` и добавьте ваши API ключи.

## Структура конфигурации

```
config.jsonc              # Основные настройки
config/prompts/           # Промпты для форматирования
  ├── notion.txt          # Notion
  ├── obsidian.txt        # Obsidian
  ├── markdown.txt        # Markdown
  ├── word.txt            # Microsoft Word
  ├── libreoffice.txt     # LibreOffice
  ├── vscode.txt          # VS Code
  ├── whatsapp.txt        # WhatsApp/Telegram/Discord
  ├── bbcode.txt          # Форумы (BBCode)
  └── _fallback.txt       # Fallback для неизвестных приложений
```

## Основные настройки

### AI Provider

```jsonc
"ai_provider": {
  "provider": "groq",  // openai, groq, glm, custom
  "api_keys": {
    "groq": "your_api_key_here"
  }
}
```

### Форматирование

```jsonc
"formatting": {
  "enabled": true,
  "provider": "groq",
  "model": "",  // пусто = default модель
  "temperature": 0.3
}
```

### Горячие клавиши

```jsonc
"application": {
  "hotkey": "ctrl+space",  // F1-F12, ctrl+shift+r, etc.
  "format_selection_hotkey": "ctrl+alt+space"  // Открывает диалог выбора формата
}
```

**format_selection_hotkey** - горячая клавиша для ручного выбора формата перед записью:
- Открывает диалог со списком доступных форматов
- Выбранный формат применяется только к текущей записи
- Имеет наивысший приоритет (выше автоопределения и фиксированного формата)
- По умолчанию: `ctrl+alt+space`

## Редактирование промптов

Откройте файл промпта в любом текстовом редакторе:

```bash
notepad config/prompts/whatsapp.txt
```

Или через VS Code:

```bash
code config/prompts/whatsapp.txt
```

## Проверка конфигурации

```bash
python test_config_loader.py
```

## Документация

Полная документация: [docs/CONFIG_MIGRATION.md](docs/CONFIG_MIGRATION.md)

## Обратная совместимость

Приложение поддерживает оба формата:
- `config.jsonc` (новый, рекомендуется)
- `.env` (старый, deprecated)

Если `config.jsonc` не найден, будет использован `.env`.
