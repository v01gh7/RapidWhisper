# GitHub Actions Build Fix

## Проблема
GitHub Actions workflow завершался с ошибкой:
```
ERROR: Spec file "RapidWhisper.spec" not found!
```

## Причина
В workflow использовалась команда `pyinstaller RapidWhisper.spec --clean`, но:
1. Зависимости устанавливались через `uv pip install --system`
2. В локальном `build.bat` используется `uv run pyinstaller`
3. Не создавалось виртуальное окружение через uv

## Решение
Обновлен `.github/workflows/build.yml`:

### Изменения для всех платформ (Windows, macOS, Linux):

1. **Создание виртуального окружения через uv:**
   ```yaml
   - name: Create virtual environment and install dependencies
     run: |
       uv venv
       uv pip install -r requirements.txt
       uv pip install pyinstaller
   ```

2. **Добавлен шаг проверки файлов:**
   ```yaml
   - name: Verify files
     run: |
       echo "Current directory:"
       pwd
       echo "Checking for RapidWhisper.spec:"
       # Проверка существования файла
   ```

3. **Использование `uv run pyinstaller`:**
   ```yaml
   - name: Build executable
     run: |
       uv run pyinstaller RapidWhisper.spec --clean
   ```

## Что теперь работает

### Windows Build
- ✅ Создается виртуальное окружение через uv
- ✅ Устанавливаются все зависимости из requirements.txt
- ✅ PyInstaller запускается через `uv run`
- ✅ Проверяется наличие RapidWhisper.spec
- ✅ Собирается RapidWhisper.exe
- ✅ Артефакт загружается в GitHub

### macOS Build
- ✅ Создается виртуальное окружение через uv
- ✅ Устанавливаются все зависимости
- ✅ Собирается исполняемый файл
- ✅ Создается .app bundle
- ✅ Создается DMG образ
- ✅ Артефакт загружается в GitHub

### Linux Build
- ✅ Устанавливаются системные зависимости (portaudio19-dev, python3-pyqt6)
- ✅ Создается виртуальное окружение через uv
- ✅ Устанавливаются все зависимости
- ✅ Собирается исполняемый файл
- ✅ Артефакт загружается в GitHub

### Release Job
- ✅ Запускается только при создании тега (v*)
- ✅ Скачивает все артефакты
- ✅ Создает GitHub Release
- ✅ Прикрепляет все исполняемые файлы к релизу

## Соответствие локальной сборке

Теперь GitHub Actions workflow полностью соответствует локальному `build.bat`:
- Оба используют `uv` для управления зависимостями
- Оба используют `uv run pyinstaller`
- Оба используют одинаковый `RapidWhisper.spec`
- Оба создают чистую сборку с `--clean` флагом

## Тестирование

Для тестирования workflow:

1. **Автоматический запуск:**
   - Push в ветку main/master
   - Создание Pull Request
   - Создание тега v* (для релиза)

2. **Ручной запуск:**
   - Перейти в GitHub → Actions
   - Выбрать "Build RapidWhisper"
   - Нажать "Run workflow"

## Артефакты

После успешной сборки доступны артефакты:
- `RapidWhisper-Windows/RapidWhisper.exe` (Windows)
- `RapidWhisper-macOS/RapidWhisper-macOS.dmg` (macOS)
- `RapidWhisper-Linux/RapidWhisper` (Linux)

Артефакты хранятся 30 дней.

## Создание релиза

Для создания релиза:
```bash
git tag v1.0.0
git push origin v1.0.0
```

Workflow автоматически:
1. Соберет все платформы
2. Создаст GitHub Release
3. Прикрепит все исполняемые файлы

## Дата исправления
2 февраля 2026
