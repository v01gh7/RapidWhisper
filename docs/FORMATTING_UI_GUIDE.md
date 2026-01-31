# Руководство по настройке форматирования

## Обзор

Новый интерфейс настройки форматирования позволяет настраивать индивидуальные промпты для каждого приложения. Это дает возможность точно контролировать, как будет форматироваться текст для Notion, Obsidian, Word и других приложений.

Система поддерживает как десктопные приложения, так и веб-приложения, работающие в браузере (Google Docs, Notion, HackMD и другие).

## Поддерживаемые приложения

### Десктопные приложения

- **Notion** - заметки и документы в стиле Notion
- **Obsidian** - markdown с wiki-ссылками и тегами
- **Markdown файлы** (.md, .markdown) - чистый markdown
- **Microsoft Word** - форматирование для Word документов
- **LibreOffice Writer** - форматирование для Writer (.odt)
- **VS Code** - markdown для .md файлов
- **Sublime Text** - стандартное текстовое форматирование
- **Notepad++** - стандартное текстовое форматирование

### Веб-приложения (определение в браузере)

Система автоматически определяет веб-приложения в браузерах (Chrome, Firefox, Edge, Opera, Brave, Vivaldi, Safari) по заголовку вкладки.

#### Google сервисы (формат word)
- **Google Docs** / **Google Документы** - редактирование документов
- **Google Sheets** / **Google Таблицы** - работа с таблицами
- **Google Slides** / **Google Презентации** - создание презентаций
- **Google Forms** / **Google Формы** - создание форм
- **Google Keep** - заметки

#### Microsoft Office Online (формат word)
- **Microsoft Word Online** - онлайн редактор документов
- **Microsoft Excel Online** - онлайн редактор таблиц
- **Microsoft PowerPoint Online** - онлайн редактор презентаций
- **Office 365** - веб-приложения Microsoft 365
- **Office Online** - веб-приложения Office

#### Инструменты для совместной работы (формат word)
- **Dropbox Paper** - совместное редактирование документов
- **Quip** - командные документы
- **Coda.io** - универсальная платформа для документов
- **Airtable** - гибрид таблиц и баз данных

#### Zoho Office Suite (формат word)
- **Zoho Writer** - редактор документов
- **Zoho Sheet** - редактор таблиц
- **Zoho Show** - редактор презентаций

#### Заметки и управление знаниями
- **Notion** / **Notion.so** (формат notion) - универсальное рабочее пространство
- **Obsidian Publish** (формат obsidian) - опубликованные заметки Obsidian

#### Markdown редакторы (формат markdown)
- **HackMD** - совместный markdown редактор
- **StackEdit** - браузерный markdown редактор
- **Dillinger** - онлайн markdown редактор
- **Typora Online** - минималистичный markdown редактор
- **GitHub.dev** - веб-редактор GitHub
- **GitLab** - веб-IDE GitLab
- **Gitpod** - облачная среда разработки

**Примечание:** Определение веб-приложений работает путем поиска ключевых слов в заголовке вкладки браузера. Система проверяет заголовки на английском и русском языках для обеспечения широкой языковой поддержки.

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
- **Названию процесса** (например: `notion.exe`, `obsidian.exe`)
- **Заголовку окна** (например: "Microsoft Word", "LibreOffice Writer")
- **Расширению файла** (например: `.md`, `.docx`)
- **Заголовку вкладки браузера** (для веб-приложений)

#### Определение веб-приложений

Когда обнаружен браузер (Chrome, Firefox, Edge, Opera, Brave, Vivaldi, Safari), система анализирует заголовок вкладки:

1. **Поиск по ключевым словам**: Проверяет наличие специфичных ключевых слов в заголовке
   - Пример: "Мой документ - Google Документы" → определяется как формат `word`
   - Пример: "Рабочее пространство - Notion" → определяется как формат `notion`

2. **Поддержка нескольких языков**: Работает с заголовками на английском и русском
   - "Google Docs" и "Google Документы" оба работают
   - "Google Sheets" и "Google Таблицы" оба работают

3. **Назначение формата**: Сопоставляет веб-приложения с соответствующими типами форматов
   - Google Docs/Sheets/Slides → формат `word`
   - Notion web → формат `notion`
   - HackMD/StackEdit → формат `markdown`

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
