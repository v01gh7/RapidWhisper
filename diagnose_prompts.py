"""
Diagnostic script to check what's happening with prompts.
"""

import json
from services.formatting_config import FormattingConfig, UNIVERSAL_DEFAULT_PROMPT

def diagnose():
    """Diagnose prompt loading issue."""
    print("=" * 80)
    print("ДИАГНОСТИКА ПРОМПТОВ")
    print("=" * 80)
    print()
    
    # Load config
    print("1. Загрузка конфигурации из .env...")
    config = FormattingConfig.from_env()
    print(f"   ✅ Загружено {len(config.applications)} приложений")
    print(f"   ✅ Загружено {len(config.app_prompts)} промптов")
    print()
    
    # Check each application
    print("2. Проверка промптов для каждого приложения:")
    print()
    
    for app in config.applications:
        print(f"   📱 {app}:")
        
        # Get prompt from dict
        saved_prompt = config.app_prompts.get(app, "")
        print(f"      - Сохранен в app_prompts: {'Да' if saved_prompt else 'Нет (пустой)'}")
        print(f"      - Длина сохраненного: {len(saved_prompt)} символов")
        
        # Get prompt via method
        used_prompt = config.get_prompt_for_app(app)
        print(f"      - Длина используемого: {len(used_prompt)} символов")
        
        # Check if it's using default
        is_default = used_prompt == UNIVERSAL_DEFAULT_PROMPT
        print(f"      - Использует дефолтный: {'Да' if is_default else 'Нет (кастомный)'}")
        
        # Check if allows formatting
        allows_formatting = "ADD FORMATTING SYMBOLS" in used_prompt
        print(f"      - Разрешает форматирование: {'✅ Да' if allows_formatting else '❌ Нет'}")
        
        print()
    
    # Check UNIVERSAL_DEFAULT_PROMPT
    print("3. Проверка UNIVERSAL_DEFAULT_PROMPT:")
    print(f"   - Длина: {len(UNIVERSAL_DEFAULT_PROMPT)} символов")
    print(f"   - Разрешает форматирование: {'✅ Да' if 'ADD FORMATTING SYMBOLS' in UNIVERSAL_DEFAULT_PROMPT else '❌ Нет'}")
    print()
    
    # Check .env file directly
    print("4. Проверка .env файла напрямую:")
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'FORMATTING_APP_PROMPTS=' in content:
            # Extract JSON
            start = content.find('FORMATTING_APP_PROMPTS=') + len('FORMATTING_APP_PROMPTS=')
            end = content.find('\n', start)
            json_str = content[start:end]
            
            try:
                data = json.loads(json_str)
                print(f"   ✅ JSON валиден, {len(data)} приложений")
                
                # Check word and libreoffice
                for app in ['word', 'libreoffice']:
                    if app in data:
                        prompt = data[app].get('prompt', '')
                        print(f"   - {app}: {'пустой' if not prompt else f'{len(prompt)} символов'}")
                        if prompt and len(prompt) > 100:
                            print(f"     Начало: {prompt[:100]}...")
            except json.JSONDecodeError as e:
                print(f"   ❌ Ошибка парсинга JSON: {e}")
        else:
            print("   ❌ FORMATTING_APP_PROMPTS не найден в .env")
    except Exception as e:
        print(f"   ❌ Ошибка чтения .env: {e}")
    
    print()
    print("=" * 80)
    print("РЕКОМЕНДАЦИИ:")
    print("=" * 80)
    
    # Check if word/libreoffice use default
    word_prompt = config.get_prompt_for_app("word")
    libreoffice_prompt = config.get_prompt_for_app("libreoffice")
    
    if word_prompt == UNIVERSAL_DEFAULT_PROMPT:
        print("⚠️  'word' использует дефолтный промпт")
        if "ADD FORMATTING SYMBOLS" in word_prompt:
            print("   ✅ Дефолтный промпт разрешает форматирование")
            print("   → Форматирование должно работать после перезапуска")
        else:
            print("   ❌ Дефолтный промпт НЕ разрешает форматирование")
            print("   → Нужно обновить код и перезапустить")
    else:
        print("ℹ️  'word' использует кастомный промпт")
        if "ADD FORMATTING SYMBOLS" in word_prompt:
            print("   ✅ Кастомный промпт разрешает форматирование")
        else:
            print("   ❌ Кастомный промпт НЕ разрешает форматирование")
            print("   → Нужно отредактировать промпт в UI")
    
    print()


if __name__ == "__main__":
    diagnose()
