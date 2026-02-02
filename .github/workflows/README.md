# GitHub Actions Workflows

## Build Workflow (build.yml)

Автоматическая сборка RapidWhisper для всех платформ.

### Когда запускается

- **Автоматически:**
  - При push в ветки `main` или `master`
  - При создании Pull Request
  - При создании тега `v*` (например, `v1.0.0`)

- **Вручную:**
  - GitHub → Actions → "Build RapidWhisper" → "Run workflow"

### Что собирается

1. **Windows** (`windows-latest`)
   - Исполняемый файл: `RapidWhisper.exe`
   - Артефакт: `RapidWhisper-Windows`

2. **macOS** (`macos-latest`)
   - DMG образ: `RapidWhisper-macOS.dmg`
   - Артефакт: `RapidWhisper-macOS`

3. **Linux** (`ubuntu-latest`)
   - Исполняемый файл: `RapidWhisper`
   - Артефакт: `RapidWhisper-Linux`

### Процесс сборки

Для каждой платформы:

1. **Checkout кода**
   ```yaml
   - uses: actions/checkout@v4
   ```

2. **Установка Python 3.13**
   ```yaml
   - uses: actions/setup-python@v5
     with:
       python-version: '3.13'
   ```

3. **Установка uv**
   ```bash
   pip install uv
   ```

4. **Создание виртуального окружения**
   ```bash
   uv venv
   uv pip install -r requirements.txt
   uv pip install pyinstaller
   ```

5. **Проверка файлов**
   - Проверяется наличие `RapidWhisper.spec`
   - Выводится список файлов в директории

6. **Сборка**
   ```bash
   uv run pyinstaller RapidWhisper.spec --clean
   ```

7. **Загрузка артефакта**
   - Артефакты хранятся 30 дней
   - Доступны для скачивания в разделе Actions

### Создание релиза

При создании тега `v*` автоматически:

1. Собираются все платформы
2. Создается GitHub Release
3. К релизу прикрепляются все исполняемые файлы

**Пример:**
```bash
git tag v1.0.0
git push origin v1.0.0
```

### Особенности платформ

#### Windows
- Использует PowerShell для проверки файлов
- Создает `.exe` файл с иконкой
- Без консольного окна

#### macOS
- Создает `.app` bundle
- Генерирует `Info.plist`
- Упаковывает в DMG образ
- Требует Python 3.13

#### Linux
- Устанавливает системные зависимости:
  - `portaudio19-dev` (для PyAudio)
  - `python3-pyqt6` (для GUI)
- Создает исполняемый файл без расширения

### Отладка

Если сборка не удалась:

1. **Проверьте логи:**
   - GitHub → Actions → Выберите запуск → Выберите job
   - Разверните шаги для просмотра деталей

2. **Шаг "Verify files":**
   - Показывает текущую директорию
   - Список файлов
   - Проверку наличия `RapidWhisper.spec`

3. **Локальное тестирование:**
   - Windows: запустите `build.bat`
   - macOS/Linux: используйте те же команды из workflow

### Требования

- Python 3.13
- uv (устанавливается автоматически)
- Все зависимости из `requirements.txt`
- PyInstaller

### Артефакты

После успешной сборки:

1. Перейдите в Actions
2. Выберите успешный запуск
3. Прокрутите вниз до "Artifacts"
4. Скачайте нужную платформу

Артефакты включают:
- Исполняемый файл
- Все необходимые библиотеки
- Иконки и ресурсы
- Промпты форматирования
- Переводы интерфейса

### Соответствие локальной сборке

GitHub Actions workflow полностью соответствует локальному `build.bat`:
- ✅ Использует `uv` для управления зависимостями
- ✅ Использует `uv run pyinstaller`
- ✅ Использует тот же `RapidWhisper.spec`
- ✅ Создает чистую сборку с `--clean`

### Поддержка

Если возникли проблемы:
1. Проверьте логи в GitHub Actions
2. Сравните с локальной сборкой
3. Создайте Issue с логами ошибки
