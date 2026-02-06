# Руководство по созданию хуков RapidWhisper

Это документ, который можно передать исполнителю. Здесь описано, как устроены хуки, какие события есть, какую структуру данных они получают и как писать корректные скрипты.

## 1. Что такое хук
Хук — это Python‑скрипт, который выполняется на определенном шаге пайплайна.  
Один файл = один хук = одно событие.

Хук получает `options` (словарь) и **обязан вернуть словарь** той же структуры, чтобы цепочка могла продолжиться.

## 2. Где хранить хук
Скрипты хуков лежат по умолчанию в:
```
config/hooks
```

Файлы с префиксом `__` игнорируются.  
Чтобы включить пример — уберите `__` из названия файла.

## 3. Обязательная структура файла
Минимальный файл хука:
```python
HOOK_EVENT = "transcription_received"

def hookHandler(options):
    # ваш код
    return options
```

**Обязательные требования:**
- В файле должен быть `HOOK_EVENT` (строка).
- В файле должна быть функция `hookHandler(options)`.
- `hookHandler` возвращает словарь `options`.

Если `HOOK_EVENT` отсутствует или невалидный — файл **не будет зарегистрирован**.

## 4. Список доступных событий
- `before_recording` — до начала записи
- `after_recording` — после записи (аудиофайл сохранен)
- `transcription_received` — получен текст из ASR
- `formatting_step` — шаг форматирования
- `post_formatting_step` — шаг пост‑форматирования
- `task_completed` — финальный текст перед показом

## 5. Структура `options`
Пример типичного payload:
```json
{
  "event": "transcription_received",
  "session_id": "session_123",
  "timestamps": {
    "event_time": "2026-02-06T20:11:22.123456"
  },
  "data": {
    "audio_file_path": "D:/recordings/clip.wav",
    "text": "Raw text from ASR"
  },
  "hooks": [
    {
      "name": "normalize_text",
      "event": "transcription_received",
      "status": "ok",
      "duration_ms": 12,
      "background": false
    }
  ],
  "errors": [
    {"hook": "foo", "event": "transcription_received", "error": "Traceback..."}
  ]
}
```

### Ключи `data` по событиям
| Событие | Ключи `data` | Что можно менять |
| --- | --- | --- |
| `before_recording` | *(empty)* | Можно добавлять свои поля |
| `after_recording` | `audio_file_path` | Можно заменить путь |
| `transcription_received` | `text`, `audio_file_path` | Можно менять `text` |
| `formatting_step` | `text`, `format_type`, `combined` | Можно менять `text` |
| `post_formatting_step` | `text`, `format_type`, `combined` | Можно менять `text` |
| `task_completed` | `text` | Можно менять `text` |

## 6. Фоновые хуки
В UI можно пометить хук как **"В фоне"**.  
В этом случае:
- хук выполняется асинхронно
- основная цепочка не ждет его результата
- результат хука не влияет на текст

Используйте фоновые хуки **только для побочных действий**: логирование, статистика, отправка в внешние сервисы и т.д.

## 7. Примеры

### Пример 1 — Очистка пробелов после транскрипции
```python
HOOK_EVENT = "transcription_received"

def hookHandler(options):
    data = options.get("data") or {}
    text = data.get("text")
    if not isinstance(text, str):
        return options

    lines = [line.strip() for line in text.splitlines()]
    data["text"] = "\n".join(lines).strip()
    options["data"] = data
    return options
```

### Пример 2 — Добавление метаданных после записи
```python
import os

HOOK_EVENT = "after_recording"

def hookHandler(options):
    data = options.get("data") or {}
    audio_path = data.get("audio_file_path")
    if isinstance(audio_path, str) and audio_path:
        data["audio_basename"] = os.path.basename(audio_path)
    options["data"] = data
    return options
```

### Пример 3 — Добавить заголовок перед форматированием
```python
HOOK_EVENT = "formatting_step"

def hookHandler(options):
    data = options.get("data") or {}
    text = data.get("text")
    if not isinstance(text, str) or not text.strip():
        return options

    if not text.lstrip().startswith("#"):
        data["text"] = "# Draft\n\n" + text
        options["data"] = data
    return options
```

## 8. Шаблон запроса к ИИ (чтобы сгенерировать хук)
Скопируйте и вставьте этот запрос в модель:

```text
Ты — Python‑разработчик. Сгенерируй файл хука для RapidWhisper.

Требования:
- Один файл = один хук
- В файле должен быть HOOK_EVENT
- Функция hookHandler(options) возвращает options
- Менять можно только options["data"]
- Нельзя ломать структуру options

Событие: <ВСТАВЬ_СОБЫТИЕ>
Моя задача: <ОПИШИ_ЧТО_ДОЛЖЕН_ДЕЛАТЬ_ХУК>

Сделай аккуратный код, добавь проверки типов и безопасные условия.
Верни только код файла без объяснений.
```

## 9. Проверка и включение
1. Сохраните файл в `config/hooks/`
2. Убедитесь, что нет префикса `__`
3. В UI включите хуки и выберите событие
4. Убедитесь, что хук появился в списке и включен

