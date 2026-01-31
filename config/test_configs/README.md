# Test Configurations

Эта папка содержит готовые конфигурации для тестов.

## Структура

```
config/test_configs/
├── README.md                           # Этот файл
├── minimal_config.jsonc                # Минимальная конфигурация
├── formatting_enabled_config.jsonc     # Конфигурация с форматированием
├── test_secrets.json                   # Тестовые API ключи
└── prompts/                            # Тестовые промпты
    ├── test_notion.txt
    ├── test_whatsapp.txt
    └── test_app.txt
```

## Конфигурации

### minimal_config.jsonc

Минимальная конфигурация для базовых тестов:
- Форматирование отключено
- Постобработка отключена
- Стандартные настройки

**Использование:**
```python
from core.config_loader import ConfigLoader

loader = ConfigLoader("config/test_configs/minimal_config.jsonc")
config = loader.load()
```

### formatting_enabled_config.jsonc

Конфигурация с включенным форматированием:
- Форматирование включено
- Постобработка включена
- 3 тестовых приложения (notion, whatsapp, test_app)
- Тестовые промпты

**Использование:**
```python
from core.config_loader import ConfigLoader

loader = ConfigLoader(
    "config/test_configs/formatting_enabled_config.jsonc",
    "config/test_configs/test_secrets.json"
)
config = loader.load()
```

### test_secrets.json

Тестовые API ключи для тестов:
- Не содержит реальных ключей
- Безопасно использовать в тестах
- Не требует настоящих API ключей

## Промпты

### prompts/test_notion.txt

Простой промпт для тестирования Notion форматирования.

### prompts/test_whatsapp.txt

Простой промпт для тестирования WhatsApp форматирования.

### prompts/test_app.txt

Универсальный промпт для тестирования.

## Использование в тестах

### Пример 1: Базовый тест

```python
import pytest
from core.config_loader import ConfigLoader

def test_basic_config():
    """Test basic configuration loading"""
    loader = ConfigLoader("config/test_configs/minimal_config.jsonc")
    config = loader.load()
    
    assert config["ai_provider"]["provider"] == "groq"
    assert config["formatting"]["enabled"] == False
```

### Пример 2: Тест форматирования

```python
import pytest
from core.config_loader import ConfigLoader
from services.formatting_config import FormattingConfig

def test_formatting_config():
    """Test formatting configuration"""
    loader = ConfigLoader(
        "config/test_configs/formatting_enabled_config.jsonc",
        "config/test_configs/test_secrets.json"
    )
    
    formatting_config = FormattingConfig.from_config(loader)
    
    assert formatting_config.enabled == True
    assert "notion" in formatting_config.applications
    assert "whatsapp" in formatting_config.applications
```

### Пример 3: Тест промптов

```python
import pytest
from core.config_loader import ConfigLoader

def test_prompt_loading():
    """Test prompt loading from files"""
    loader = ConfigLoader(
        "config/test_configs/formatting_enabled_config.jsonc"
    )
    
    notion_prompt = loader.get_prompt("notion")
    assert "Test prompt for Notion" in notion_prompt
    
    whatsapp_prompt = loader.get_prompt("whatsapp")
    assert "Test prompt for WhatsApp" in whatsapp_prompt
```

## Создание новых тестовых конфигов

### 1. Создайте новый JSONC файл

```bash
# Скопируйте существующий конфиг
copy config/test_configs/minimal_config.jsonc config/test_configs/my_test_config.jsonc

# Отредактируйте под ваши нужды
notepad config/test_configs/my_test_config.jsonc
```

### 2. Создайте тестовые промпты (если нужно)

```bash
# Создайте новый промпт
echo "My test prompt" > config/test_configs/prompts/my_test_prompt.txt
```

### 3. Используйте в тестах

```python
loader = ConfigLoader("config/test_configs/my_test_config.jsonc")
config = loader.load()
```

## Преимущества

### ✅ До (без test_configs):

```python
# Каждый тест создает временные файлы
def test_something():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write(f"FORMATTING_APP_PROMPTS={json.dumps(...)}\n")
        # ... много кода для создания конфига
```

**Проблемы:**
- ❌ Много дублирующегося кода
- ❌ Сложно поддерживать
- ❌ Медленно (создание файлов)
- ❌ Сложно отладить

### ✅ После (с test_configs):

```python
# Используем готовый конфиг
def test_something():
    loader = ConfigLoader("config/test_configs/formatting_enabled_config.jsonc")
    config = loader.load()
    # Тест...
```

**Преимущества:**
- ✅ Чистый код
- ✅ Легко поддерживать
- ✅ Быстро (нет создания файлов)
- ✅ Легко отладить
- ✅ Переиспользуемые конфиги

## Обновление тестов

### Старый код (с .env):

```python
with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
    f.write("FORMATTING_ENABLED=true\n")
    f.write(f"FORMATTING_APP_PROMPTS={json.dumps(app_prompts_data)}\n")
    temp_path = f.name

config = FormattingConfig.from_env(temp_path)
```

### Новый код (с test_configs):

```python
loader = ConfigLoader("config/test_configs/formatting_enabled_config.jsonc")
config = FormattingConfig.from_config(loader)
```

## Best Practices

1. **Используйте готовые конфиги** вместо создания временных файлов
2. **Создавайте специфичные конфиги** для специфичных тестов
3. **Не изменяйте существующие конфиги** - создавайте новые
4. **Документируйте** назначение каждого конфига
5. **Используйте test_secrets.json** для тестовых API ключей

## Troubleshooting

### Ошибка: "Configuration file not found"

Проблема: Неправильный путь к конфигу

Решение:
```python
# Используйте относительный путь от корня проекта
loader = ConfigLoader("config/test_configs/minimal_config.jsonc")
```

### Ошибка: "Prompt file not found"

Проблема: Промпт не существует

Решение:
```bash
# Проверьте что файл существует
ls config/test_configs/prompts/

# Создайте если нужно
echo "Test prompt" > config/test_configs/prompts/my_prompt.txt
```

### Тесты падают после обновления конфига

Проблема: Изменили существующий конфиг

Решение:
- Не изменяйте существующие конфиги
- Создайте новый конфиг для новых тестов
- Или обновите тесты под новый формат

## Вопросы?

Если возникли проблемы с тестовыми конфигами:
1. Проверьте пути к файлам
2. Проверьте формат JSON (используйте validator)
3. Посмотрите примеры использования выше
4. Создайте issue на GitHub
