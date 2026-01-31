# Security Update: API Keys Separation

## Что изменилось

API ключи теперь хранятся в отдельном файле `secrets.json`, который **НЕ** добавляется в git.

## Проблема

**До:**
```jsonc
// config.jsonc (в git!)
{
  "ai_provider": {
    "api_keys": {
      "groq": "gsk_ВАШИ_СЕКРЕТНЫЕ_КЛЮЧИ_ВИДНЫ_ВСЕМ"  // ❌ В git!
    }
  }
}
```

**Риски:**
- ❌ API ключи видны в публичном репозитории
- ❌ Любой может использовать ваши ключи
- ❌ Потенциальные финансовые потери
- ❌ Нарушение безопасности

## Решение

**После:**
```jsonc
// config.jsonc (в git) ✅
{
  "ai_provider": {
    "provider": "groq"
    // API keys are stored in secrets.json (not in git)
  }
}
```

```json
// secrets.json (НЕ в git!) ✅
{
  "api_keys": {
    "groq": "gsk_ваш_секретный_ключ"
  }
}
```

```gitignore
# .gitignore ✅
secrets.json
config.jsonc
```

## Файлы

### В git (публичные):
- ✅ `config.jsonc.example` - пример конфигурации без ключей
- ✅ `secrets.json.example` - пример структуры secrets
- ✅ `config/prompts/*.txt` - промпты форматирования
- ✅ `.gitignore` - включает `secrets.json`

### НЕ в git (приватные):
- 🔒 `secrets.json` - ваши API ключи
- 🔒 `config.jsonc` - ваша конфигурация
- 🔒 `.env` - старый формат (backup)

## Миграция

### Автоматическая

```bash
python migrate_to_jsonc.py
```

Скрипт:
1. Извлекает API ключи из `.env`
2. Создает `secrets.json` с ключами
3. Создает `config.jsonc` без ключей
4. Обновляет `.gitignore`

### Ручная

1. Создайте `secrets.json`:
```bash
copy secrets.json.example secrets.json
```

2. Добавьте ваши ключи в `secrets.json`

3. Убедитесь что `secrets.json` в `.gitignore`:
```bash
echo "secrets.json" >> .gitignore
```

## Проверка безопасности

### ✅ Checklist:

- [ ] `secrets.json` создан
- [ ] API ключи в `secrets.json`
- [ ] `secrets.json` в `.gitignore`
- [ ] `config.jsonc` без API ключей
- [ ] `config.jsonc` в `.gitignore`
- [ ] Тест пройден: `python test_config_loader.py`

### Проверка git:

```bash
# Проверить что secrets.json НЕ в git
git status

# Должно быть:
# On branch main
# Untracked files:
#   secrets.json  (если не в .gitignore)
#
# Changes not staged for commit:
#   .gitignore

# Проверить .gitignore
cat .gitignore | grep secrets.json
# Должно вывести: secrets.json
```

## Что делать если ключи попали в git

### 1. Немедленно смените API ключи!

- OpenAI: https://platform.openai.com/api-keys
- Groq: https://console.groq.com/keys
- GLM: https://open.bigmodel.cn/usercenter/apikeys

### 2. Удалите из git:

```bash
# Удалить secrets.json из git (но оставить локально)
git rm --cached secrets.json

# Удалить config.jsonc из git (но оставить локально)
git rm --cached config.jsonc

# Обновить .gitignore
echo "secrets.json" >> .gitignore
echo "config.jsonc" >> .gitignore

# Закоммитить
git add .gitignore
git commit -m "Security: Remove API keys from git"
git push
```

### 3. Очистите историю (опционально):

⚠️ **ВНИМАНИЕ:** Это переписывает историю git!

```bash
# Используйте BFG Repo-Cleaner
# https://rtyley.github.io/bfg-repo-cleaner/

# Или git filter-branch (сложнее)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch secrets.json" \
  --prune-empty --tag-name-filter cat -- --all
```

## Best Practices

### ✅ Правильно:

1. **Secrets в отдельном файле**
   ```
   secrets.json (НЕ в git)
   ```

2. **Примеры в git**
   ```
   secrets.json.example (в git)
   config.jsonc.example (в git)
   ```

3. **Проверка перед коммитом**
   ```bash
   git status
   # Убедитесь что secrets.json НЕ в списке
   ```

4. **Backup secrets**
   - Менеджер паролей (1Password, Bitwarden)
   - Зашифрованное хранилище

### ❌ Неправильно:

1. **API ключи в коде**
   ```python
   API_KEY = "gsk_secret"  # ❌
   ```

2. **API ключи в config.jsonc**
   ```jsonc
   {"api_key": "secret"}  // ❌
   ```

3. **Secrets в git**
   ```bash
   git add secrets.json  # ❌
   ```

4. **Незашифрованный backup**
   - Email ❌
   - Dropbox ❌
   - Мессенджеры ❌

## Дополнительная безопасность

### Environment Variables

Для production можно использовать переменные окружения:

```bash
# Linux/Mac
export GROQ_API_KEY="your_key"

# Windows
set GROQ_API_KEY=your_key
```

### Encrypted Secrets

Для команды можно использовать зашифрованные secrets:

```bash
# Зашифровать secrets.json
gpg -c secrets.json

# Расшифровать
gpg secrets.json.gpg
```

### Git Hooks

Добавьте pre-commit hook для проверки:

```bash
# .git/hooks/pre-commit
#!/bin/bash
if git diff --cached --name-only | grep -q "secrets.json"; then
    echo "ERROR: Attempting to commit secrets.json!"
    exit 1
fi
```

## Вопросы?

Если возникли проблемы с безопасностью:
1. Проверьте `.gitignore`
2. Проверьте `git status`
3. Смените API ключи если они попали в git
4. Создайте issue на GitHub (без ключей!)

## Ресурсы

- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [Git Secrets](https://github.com/awslabs/git-secrets)
