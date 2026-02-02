# Cross-Platform Build Implementation

## Обзор

Реализована полноценная кросс-платформенная сборка RapidWhisper для Windows, macOS и Linux с правильными зависимостями и функциональностью для каждой платформы.

## Структура файлов

### Requirements файлы

Созданы отдельные файлы зависимостей для каждой платформы:

1. **`requirements-windows.txt`** - Windows зависимости
   - Включает `pywin32==311` и `pywin32-ctypes==0.2.3`
   - Для работы с Windows API

2. **`requirements-macos.txt`** - macOS зависимости
   - Включает `pyobjc-core`, `pyobjc-framework-Cocoa`, `pyobjc-framework-Quartz`
   - Для работы с macOS AppKit и Quartz APIs

3. **`requirements-linux.txt`** - Linux зависимости
   - Без platform-specific пакетов
   - Использует системные утилиты (xdotool, wmctrl)

### PyInstaller Spec файлы

Созданы отдельные spec файлы для каждой платформы:

1. **`RapidWhisper.spec`** - Windows
   - Использует `.ico` иконку
   - Windows-specific параметры

2. **`RapidWhisper-macOS.spec`** - macOS
   - `argv_emulation=True` для macOS
   - Без иконки (добавляется в .app bundle)

3. **`RapidWhisper-Linux.spec`** - Linux
   - Минимальная конфигурация
   - Без иконки

### Window Monitor реализации

Созданы полноценные реализации мониторинга окон для каждой платформы:

1. **`services/windows_window_monitor.py`** - Windows
   - Использует win32 API
   - Извлекает иконки из HICON
   - Кэширование иконок

2. **`services/macos_window_monitor.py`** - macOS
   - Использует AppKit (NSWorkspace, NSRunningApplication)
   - Использует Quartz для получения информации об окнах
   - Конвертирует NSImage в QPixmap
   - Кэширование иконок

3. **`services/linux_window_monitor.py`** - Linux
   - Использует xdotool и wmctrl
   - Использует Qt icon theme для иконок
   - Кэширование иконок
   - Graceful fallback если утилиты не установлены

## Функциональность по платформам

### Windows
✅ Мониторинг активного окна через win32 API
✅ Извлечение иконок приложений
✅ Определение процесса и названия окна
✅ Rich clipboard (HTML форматирование)

### macOS
✅ Мониторинг активного окна через AppKit
✅ Извлечение иконок приложений через NSRunningApplication
✅ Определение процесса и названия окна
✅ Поддержка .app bundle и DMG

### Linux
✅ Мониторинг активного окна через xdotool/wmctrl
✅ Извлечение иконок через Qt icon theme
✅ Определение процесса и названия окна
✅ Graceful degradation без xdotool/wmctrl

## GitHub Actions Workflow

Обновлен `.github/workflows/build.yml`:

### Windows Build
```yaml
- name: Create virtual environment and install dependencies
  run: |
    uv venv
    uv pip install -r requirements-windows.txt

- name: Build Windows executable
  run: |
    uv run pyinstaller RapidWhisper.spec --clean
```

### macOS Build
```yaml
- name: Install system dependencies
  run: |
    brew install portaudio

- name: Create virtual environment and install dependencies
  run: |
    uv venv
    uv pip install -r requirements-macos.txt

- name: Build macOS executable
  run: |
    uv run pyinstaller RapidWhisper-macOS.spec --clean
```

### Linux Build
```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y portaudio19-dev python3-pyqt6 xdotool wmctrl

- name: Create virtual environment and install dependencies
  run: |
    uv venv
    uv pip install -r requirements-linux.txt

- name: Build Linux executable
  run: |
    uv run pyinstaller RapidWhisper-Linux.spec --clean
```

## Системные зависимости

### Windows
- Нет дополнительных системных зависимостей
- Все через Python пакеты

### macOS
- Python 3.13
- PortAudio (через Homebrew)
- pyobjc (устанавливается через pip)

Установка на macOS:
```bash
brew install portaudio
```

### Linux
- `portaudio19-dev` - для PyAudio
- `python3-pyqt6` - для Qt
- `xdotool` - для мониторинга окон (опционально)
- `wmctrl` - для мониторинга окон (опционально)

Установка на Linux:
```bash
sudo apt-get install portaudio19-dev python3-pyqt6 xdotool wmctrl
```

## Локальная сборка

### Windows
```bash
# Установить зависимости
uv pip install -r requirements-windows.txt

# Собрать
uv run pyinstaller RapidWhisper.spec --clean
```

### macOS
```bash
# Установить системные зависимости
brew install portaudio

# Установить Python зависимости
uv pip install -r requirements-macos.txt

# Собрать
uv run pyinstaller RapidWhisper-macOS.spec --clean

# Создать DMG (опционально)
mkdir -p "dist/RapidWhisper.app/Contents/MacOS"
mv dist/RapidWhisper "dist/RapidWhisper.app/Contents/MacOS/"
# ... создать Info.plist ...
hdiutil create -volname "RapidWhisper" -srcfolder "dist/RapidWhisper.app" -ov -format UDZO "dist/RapidWhisper-macOS.dmg"
```

### Linux
```bash
# Установить системные зависимости
sudo apt-get install portaudio19-dev python3-pyqt6 xdotool wmctrl

# Установить Python зависимости
uv pip install -r requirements-linux.txt

# Собрать
uv run pyinstaller RapidWhisper-Linux.spec --clean
```

## Особенности реализации

### Кэширование иконок
Все реализации используют LRU кэш для иконок:
- Максимум 50 иконок в кэше
- Автоматическое удаление наименее используемых
- Кэш по ключу `process_name_process_id`

### Мониторинг изменений
Все реализации проверяют изменения каждые 200ms:
- Отслеживание изменения названия окна
- Отслеживание изменения процесса
- Callback только при изменениях

### Обработка ошибок
Все реализации gracefully обрабатывают ошибки:
- Логирование ошибок
- Возврат None при ошибках
- Продолжение работы при частичных сбоях

## Тестирование

### Локальное тестирование
```bash
# Windows
pytest tests/test_windows_window_monitor.py

# macOS
pytest tests/test_macos_window_monitor.py

# Linux
pytest tests/test_linux_window_monitor.py
```

### GitHub Actions
Автоматическая сборка при:
- Push в main/master
- Pull Request
- Создание тега v*
- Ручной запуск (workflow_dispatch)

## Артефакты

После успешной сборки доступны:
- `RapidWhisper-Windows/RapidWhisper.exe`
- `RapidWhisper-macOS/RapidWhisper-macOS.dmg`
- `RapidWhisper-Linux/RapidWhisper`

Хранятся 30 дней.

## Создание релиза

```bash
git tag v1.0.0
git push origin v1.0.0
```

Автоматически:
1. Соберет все платформы
2. Создаст GitHub Release
3. Прикрепит все исполняемые файлы

## Дата реализации
2 февраля 2026
