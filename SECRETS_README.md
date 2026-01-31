# Secrets Management

## Обзор

API ключи и другие секретные данные хранятся в отдельном файле `secrets.json`, который **НЕ** добавляется в git.

## Структура

```
secrets.json          # Ваши API ключи (НЕ в git!)
secrets.json.example  # Пример структуры (в git)
```

## Настройка

### 1. Создайте secrets.json

```bash
copy secrets.json.example secrets.json
```

### 2. Добавьте ваши API ключи

Отредактируйте `secrets.json`:

```json
{
  "api_keys": {
    "openai": "sk-your-openai-key-here",
    "groq": "gsk_your-groq-key-here",
    "glm": "your-glm-key-here"
  },
  "custom_providers": {
    "api_key": "your-custom-transcription-key",
    "formatting_api_key": "your-custom-formatting-key"
  }
}
```

### 3. Проверьте .gitignore

Убедитесь что `secrets.json` в `.gitignore`:

```gitignore
# Secrets (API keys, tokens, etc.)
secrets.json
```

## Безопасность

### ✅ Правильно:

- `secrets.json` в `.gitignore`
- API ключи только в `secrets.json`
- `secrets.json.example` без реальных ключей

### ❌ Неправильно:

- API ключи в `config.jsonc`
- API ключи в коде
- `secrets.json` в git

## Получение API ключей

### OpenAI
1. Зайдите на https://platform.openai.com/api-keys
2. Создайте новый API ключ
3. Скопируйте в `secrets.json`

### Groq (бесплатно!)
1. Зайдите на https://console.groq.com/keys
2. Создайте новый API ключ
3. Скопируйте в `secrets.json`

### GLM
1. Зайдите на https://open.bigmodel.cn/usercenter/apikeys
2. Создайте новый API ключ
3. Скопируйте в `secrets.json`

## Миграция из .env

Если у вас уже есть `.env` с ключами:

```bash
python migrate_to_jsonc.py
```

Скрипт автоматически:
1. Извлечет API ключи из `.env`
2. Создаст `secrets.json`
3. Обновит `.gitignore`

## Использование в коде

ConfigLoader автоматически загружает secrets:

```python
from core.config_loader import get_config_loader

loader = get_config_loader()
config = loader.load()

# API ключи доступны через config
groq_key = config["ai_provider"]["api_keys"]["groq"]
```

## Troubleshooting

### Ошибка: "Secrets file not found"

Решение:
```bash
copy secrets.json.example secrets.json
# Отредактируйте secrets.json и добавьте ваши ключи
```

### Ошибка: "API key not found"

Проблема: Ключ не указан в `secrets.json`

Решение:
1. Откройте `secrets.json`
2. Добавьте нужный API ключ
3. Перезапустите приложение

### secrets.json попал в git

Если случайно закоммитили `secrets.json`:

```bash
# Удалить из git (но оставить локально)
git rm --cached secrets.json

# Добавить в .gitignore
echo "secrets.json" >> .gitignore

# Закоммитить изменения
git add .gitignore
git commit -m "Remove secrets.json from git"
```

⚠️ **ВАЖНО:** Если ключи попали в публичный репозиторий, **немедленно** смените их!

## Backup

Рекомендуется хранить backup `secrets.json` в безопасном месте:

- Менеджер паролей (1Password, LastPass, Bitwarden)
- Зашифрованное облако
- Локальный зашифрованный диск

**НЕ** храните backup в:
- Незашифрованном облаке (Dropbox, Google Drive)
- Email
- Мессенджерах
- Публичных репозиториях

## Вопросы?

Если возникли проблемы с secrets:
1. Проверьте что `secrets.json` существует
2. Проверьте формат JSON (используйте validator)
3. Проверьте что ключи правильные (попробуйте в API напрямую)
4. Проверьте логи: `rapidwhisper.log`
