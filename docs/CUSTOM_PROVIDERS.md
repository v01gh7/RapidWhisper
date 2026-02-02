# Кастомные AI провайдеры

## Обзор

RapidWhisper поддерживает любые OpenAI-совместимые API для транскрипции аудио. Это позволяет использовать локальные модели или альтернативные облачные сервисы.

## Поддерживаемые провайдеры

### Встроенные провайдеры

1. **Groq** (рекомендуется)
   - Бесплатный и быстрый
   - URL: https://console.groq.com/keys
   - Модель: whisper-large-v3

2. **OpenAI**
   - Официальный Whisper API
   - URL: https://platform.openai.com/api-keys
   - Модель: whisper-1

3. **GLM (Zhipu AI)**
   - Поддержка китайского языка
   - URL: https://open.bigmodel.cn/
   - Модель: glm-4-voice

### Кастомные провайдеры

Любой OpenAI-совместимый API, включая:

- **LM Studio** - Локальные модели на вашем компьютере
- **Ollama** - Простой запуск локальных моделей
- **vLLM** - Высокопроизводительный inference сервер
- **LocalAI** - Локальная альтернатива OpenAI
- **FastWhisper** - Оптимизированный Whisper сервер
- И любые другие совместимые API

## Настройка кастомного провайдера

### Через UI (рекомендуется)

1. Откройте настройки (иконка в трее → Настройки)
2. Выберите провайдер: **custom**
3. Заполните поля:
   - **Custom API Key**: Ваш API ключ (если требуется)
   - **Custom Base URL**: URL вашего API endpoint
   - **Custom Model**: Название модели
4. Нажмите "Сохранить"

### Через .env файл

Отредактируйте `.env` файл:

```env
AI_PROVIDER=custom
CUSTOM_API_KEY=your_api_key_here
CUSTOM_BASE_URL=http://localhost:1234/v1/
CUSTOM_MODEL=
```

## Примеры настройки

### LM Studio

LM Studio позволяет запускать модели локально на вашем компьютере.

1. Скачайте и установите [LM Studio](https://lmstudio.ai)
2. Загрузите Whisper модель в LM Studio
3. Запустите локальный сервер в LM Studio
4. Настройте RapidWhisper:

```env
AI_PROVIDER=custom
CUSTOM_API_KEY=lm-studio
CUSTOM_BASE_URL=http://localhost:1234/v1/
CUSTOM_MODEL=whisper-1
```

**Преимущества:**
- ✅ Полностью локально (без интернета)
- ✅ Приватность данных
- ✅ Бесплатно
- ❌ Требует мощный компьютер
- ❌ Медленнее облачных API

### Ollama

Ollama - простой способ запуска локальных моделей.

1. Установите [Ollama](https://ollama.ai)
2. Запустите Whisper модель:
   ```bash
   ollama run whisper
   ```
3. Настройте RapidWhisper:

```env
AI_PROVIDER=custom
CUSTOM_API_KEY=ollama
CUSTOM_BASE_URL=http://localhost:11434/v1/
CUSTOM_MODEL=whisper
```

**Преимущества:**
- ✅ Простая установка
- ✅ Локально
- ✅ Бесплатно
- ❌ Требует настройку

### vLLM

vLLM - высокопроизводительный inference сервер.

1. Установите vLLM:
   ```bash
   pip install vllm
   ```
2. Запустите сервер:
   ```bash
   python -m vllm.entrypoints.openai.api_server \
     --model openai/whisper-large-v3 \
     --port 8000
   ```
3. Настройте RapidWhisper:

```env
AI_PROVIDER=custom
CUSTOM_API_KEY=vllm
CUSTOM_BASE_URL=http://localhost:8000/v1/
CUSTOM_MODEL=openai/whisper-large-v3
```

**Преимущества:**
- ✅ Очень быстрый
- ✅ Поддержка GPU
- ✅ Оптимизирован для production
- ❌ Сложная настройка

### LocalAI

LocalAI - локальная альтернатива OpenAI API.

1. Установите [LocalAI](https://localai.io)
2. Запустите с Whisper моделью
3. Настройте RapidWhisper:

```env
AI_PROVIDER=custom
CUSTOM_API_KEY=local
CUSTOM_BASE_URL=http://localhost:8080/v1/
```

### Удаленный сервер

Если у вас есть удаленный сервер с Whisper API:

```env
AI_PROVIDER=custom
CUSTOM_API_KEY=your_secret_key
CUSTOM_BASE_URL=https://your-server.com/v1/
CUSTOM_MODEL=whisper-large-v3
```

## Требования к API

Кастомный API должен быть совместим с OpenAI API:

### Endpoint

```
POST {CUSTOM_BASE_URL}/audio/transcriptions
```

### Request

```bash
curl -X POST {CUSTOM_BASE_URL}/audio/transcriptions \
  -H "Authorization: Bearer {CUSTOM_API_KEY}" \
  -F "file=@audio.wav" \
  -F "model={CUSTOM_MODEL}" \
  -F "response_format=json"
```

### Response

```json
{
  "text": "Транскрибированный текст"
}
```

## Тестирование

### Проверка подключения

1. Запустите ваш локальный сервер
2. Проверьте что он доступен:
   ```bash
   curl http://localhost:1234/v1/models
   ```
3. Настройте RapidWhisper
4. Попробуйте записать аудио (Ctrl+Space)

### Отладка

Если не работает:

1. Проверьте логи: `rapidwhisper.log`
2. Проверьте что сервер запущен
3. Проверьте URL (должен заканчиваться на `/v1/`)
4. Проверьте что модель загружена
5. Проверьте API ключ (если требуется)

## Производительность

### Локальные модели

- **CPU**: 5-15 секунд на 10 секунд аудио
- **GPU**: 1-3 секунды на 10 секунд аудио

### Облачные API

- **Groq**: 1-2 секунды
- **OpenAI**: 2-4 секунды
- **Кастомные**: зависит от сервера

## Приватность

### Локальные модели
- ✅ Данные не покидают ваш компьютер
- ✅ Полная приватность
- ✅ Работает без интернета

### Облачные API
- ⚠️ Аудио отправляется на сервер
- ⚠️ Проверьте политику конфиденциальности провайдера

## Рекомендации

### Для начинающих
→ Используйте **Groq** (бесплатный и быстрый)

### Для приватности
→ Используйте **LM Studio** или **Ollama** (локально)

### Для production
→ Используйте **vLLM** на своем сервере

### Для экспериментов
→ Попробуйте разные провайдеры и сравните

## Поддержка

Если у вас проблемы с кастомным провайдером:

1. Проверьте что API совместим с OpenAI
2. Проверьте логи приложения
3. Проверьте документацию вашего провайдера
4. Создайте issue на GitHub с деталями

## Примеры конфигураций

### Минимальная (без ключа)

```env
AI_PROVIDER=custom
CUSTOM_API_KEY=
CUSTOM_BASE_URL=http://localhost:1234/v1/
CUSTOM_MODEL=whisper-1
```

### С аутентификацией

```env
AI_PROVIDER=custom
CUSTOM_API_KEY=sk-1234567890abcdef
CUSTOM_BASE_URL=https://api.example.com/v1/
CUSTOM_MODEL=whisper-large-v3
```

### Несколько моделей

Вы можете переключаться между моделями через настройки:

```env
# Для быстрой транскрипции
CUSTOM_MODEL=whisper-base

# Для точной транскрипции
CUSTOM_MODEL=whisper-large-v3
```

---

**Совет**: Начните с Groq для тестирования, затем переходите на локальные модели если нужна приватность.
