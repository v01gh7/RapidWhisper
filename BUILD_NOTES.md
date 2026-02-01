# Заметки по сборке RapidWhisper

## Обновления (Февраль 2026)

### Изменения в структуре проекта

1. **Конфигурация перенесена с .env на JSONC**
   - Основной конфиг: `config.jsonc`
   - Секреты (API ключи): `secrets.json`
   - Оба файла НЕ включаются в сборку
   - Создаются автоматически в `%APPDATA%\RapidWhisper\` при первом запуске

2. **Промпты форматирования вынесены в отдельные файлы**
   - Расположение: `config/prompts/*.txt`
   - Включаются в сборку (обязательны для работы)
   - Файлы:
     - `_fallback.txt` - универсальный промпт
     - `notion.txt` - для Notion
     - `obsidian.txt` - для Obsidian
     - `markdown.txt` - для Markdown
     - `word.txt` - для Word/Google Docs
     - `libreoffice.txt` - для LibreOffice
     - `vscode.txt` - для VS Code
     - `bbcode.txt` - для форумов (BBCode)
     - `whatsapp.txt` - для мессенджеров

3. **Иконки для UI**
   - Расположение: `public/icons/*.svg` и `*.png`
   - Включаются в сборку
   - Используются для:
     - Кнопки окон (minimize, maximize, close, restore)
     - Discord иконка в меню настроек
     - Иконки донатов (kofi, streamlabs)

### Что включается в сборку

✅ **Включается:**
- `public/RapidWhisper.ico` - основная иконка приложения
- `public/icons/*.svg` - SVG иконки для UI
- `public/icons/*.png` - PNG иконки для UI
- `config/prompts/*.txt` - промпты форматирования

❌ **НЕ включается:**
- `config.jsonc` - создается в AppData
- `secrets.json` - создается в AppData
- `config/test_configs/` - только для разработки
- `.env` файлы (устаревшие)

### Процесс сборки

1. **Сохранение конфигов разработчика**
   ```
   config.jsonc → config.jsonc.backup
   secrets.json → secrets.json.backup
   ```

2. **Очистка**
   ```
   Удаление папок build/ и dist/
   ```

3. **Сборка**
   ```
   PyInstaller с RapidWhisper.spec
   Включение иконок и промптов
   ```

4. **Восстановление конфигов**
   ```
   config.jsonc.backup → config.jsonc
   secrets.json.backup → secrets.json
   ```

### Тестовые конфигурации

Обновлены в соответствии с новой структурой:

- `config/test_configs/minimal_config.jsonc` - минимальная конфигурация
- `config/test_configs/formatting_enabled_config.jsonc` - с форматированием

Новые ключи добавлены:
- `ai_provider.transcription_model`
- `ai_provider.custom.*`
- `ai_provider.api_keys.*`
- `application.format_selection_hotkey`
- `window.font_sizes.*`
- `formatting.use_fixed_format`
- `formatting.custom.api_key`

### Запуск сборки

```bash
build.bat
```

Скрипт автоматически:
1. Проверит PyInstaller
2. Сохранит ваши конфиги
3. Соберет чистый .exe
4. Восстановит ваши конфиги

### Результат

Файл: `dist\RapidWhisper.exe`

При первом запуске:
- Создается `%APPDATA%\RapidWhisper\config.jsonc`
- Создается `%APPDATA%\RapidWhisper\secrets.json`
- Пользователь настраивает через окно настроек

### Кодировка

Все файлы сохранены в UTF-8:
- `build.bat` - UTF-8 с BOM
- `RapidWhisper.spec` - UTF-8
- Конфиги - UTF-8

### Для распространения

Нужен только один файл:
```
dist\RapidWhisper.exe
```

Все остальное создается автоматически при первом запуске.
