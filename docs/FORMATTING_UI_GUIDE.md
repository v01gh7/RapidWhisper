# Руководство по настройке форматирования

## Обзор

Новый интерфейс настройки форматирования позволяет настраивать индивидуальные промпты для каждого приложения. Это дает возможность точно контролировать, как будет форматироваться текст для Notion, Obsidian, Word и других приложений.

## Основные возможности

### 1. Визуальный список приложений

Приложения отображаются в виде карточек (как выбор языка), что делает интерфейс более интуитивным:

- **Синяя рамка и иконка ✏️** - приложение имеет кастомный промпт
- **Серая рамка** - приложение использует универсальный промпт по умолчанию

### 2. Добавление приложений

1. Нажмите кнопку **"➕ Добавить приложение"**
2. Введите название приложения (например: `vscode`, `sublime`, `notepad++`)
3. Отредактируйте промпт или оставьте универсальный по умолчанию
4. Нажмите **"Добавить"**

**Валидация:**
- Название не может быть пустым
- Название должно быть уникальным

### 3. Редактирование промптов

1. **Правый клик** на карточке приложения
2. Выберите **"Редактировать"** из контекстного меню
3. Измените промпт в текстовом редакторе
4. Нажмите **"Сохранить"** для применения изменений

**Совет:** Оставьте промпт пустым, чтобы использовать универсальный промпт по умолчанию.

### 4. Удаление приложений

1. **Правый клик** на карточке приложения
2. Выберите **"Удалить"** из контекстного меню

**Ограничение:** Нельзя удалить последнее приложение - должно остаться хотя бы одно.

## Универсальный промпт по умолчанию

Все новые приложения автоматически получают универсальный промпт, который работает для всех форматов:

```
CRITICAL INSTRUCTIONS:
1. PRESERVE ALL CONTENT: Keep every word from the original text
2. ADD STRUCTURE: Actively identify and create proper formatting
3. NO NEW CONTENT: Do not add examples, explanations, or text that wasn't spoken

Task: Transform the transcribed speech into well-structured text.

Your job:
- ANALYZE the content and identify natural sections
- CREATE headings where appropriate for main topics and subtopics
- CONVERT lists when the speaker mentions multiple items
- ADD emphasis for important points
- INSERT line breaks between logical sections
- STRUCTURE the content for maximum readability

Remember: Use ALL the original words, just organize them better.

Output ONLY the reformatted text.
```

## Примеры кастомных промптов

### Notion
```
Format this text for Notion with:
- Use ## for main headings, ### for subheadings
- Create toggle lists for detailed sections
- Use callout blocks for important notes
- Add database properties where relevant
```

### Obsidian
```
Format this text for Obsidian with:
- Use [[wiki-links]] for internal references
- Add #tags for categorization
- Use > for callouts
- Create YAML frontmatter if needed
```

### Markdown
```
Format this text as clean Markdown with:
- Standard # heading syntax
- Proper list formatting (-, *, 1.)
- Code blocks with ``` when needed
- Bold **text** and italic *text* where appropriate
```

### Word/LibreOffice
```
Format this text for Word/LibreOffice with:
- Clear paragraph structure
- Numbered and bulleted lists
- NO markdown syntax
- Professional document formatting
```

## Хранение конфигурации

Все настройки сохраняются в файле `.env` в формате JSON:

```env
FORMATTING_APP_PROMPTS={"notion":{"enabled":true,"prompt":"Custom prompt..."},"obsidian":{"enabled":true,"prompt":""}}
```

## Миграция со старого формата

Если у вас была старая конфигурация с `FORMATTING_APPLICATIONS`, она автоматически мигрирует в новый формат при первом запуске:

**Старый формат:**
```env
FORMATTING_APPLICATIONS=notion,obsidian,markdown,word
```

**Новый формат:**
```env
FORMATTING_APP_PROMPTS={"notion":{"enabled":true,"prompt":""},"obsidian":{"enabled":true,"prompt":""},...}
```

Все приложения из старого формата получат пустой промпт (используется универсальный по умолчанию).

## Локализация

Интерфейс поддерживает русский и английский языки:

**Русский:**
- Редактировать
- Удалить
- Добавить приложение
- Сохранить / Отменить

**English:**
- Edit
- Delete
- Add Application
- Save / Cancel

Язык интерфейса настраивается в разделе **"Языки"** настроек.

## Технические детали

### Приоритет промптов

1. **Кастомный промпт приложения** - если задан для конкретного приложения
2. **Универсальный промпт по умолчанию** - если промпт пустой или не задан

### Определение активного приложения

Система автоматически определяет активное приложение по:
- Названию процесса (например: `notion.exe`, `obsidian.exe`)
- Заголовку окна (например: "Microsoft Word", "LibreOffice Writer")
- Расширению файла (например: `.md`, `.docx`)

### API

Для программного доступа к конфигурации:

```python
from services.formatting_config import FormattingConfig

# Загрузить конфигурацию
config = FormattingConfig.from_env()

# Получить промпт для приложения
prompt = config.get_prompt_for_app("notion")

# Установить кастомный промпт
config.set_prompt_for_app("vscode", "Custom VSCode prompt...")

# Сохранить изменения
config.save_to_env()
```

## Решение проблем

### Промпт не применяется

1. Проверьте, что форматирование включено в настройках
2. Убедитесь, что приложение правильно определяется
3. Проверьте логи на наличие ошибок

### Приложение не определяется

1. Добавьте приложение вручную через интерфейс
2. Используйте точное название процесса (например: `code.exe` для VSCode)
3. Проверьте, что приложение есть в списке настроенных

### Миграция не работает

1. Проверьте формат старой конфигурации в `.env`
2. Убедитесь, что файл `.env` доступен для записи
3. Проверьте логи на наличие ошибок парсинга JSON

## Обратная связь

Если вы нашли баг или хотите предложить улучшение, создайте issue на GitHub:
https://github.com/your-repo/RapidWhisper/issues
