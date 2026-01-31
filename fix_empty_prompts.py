"""
Fix empty/old prompts in .env file.
This script will clear all OLD prompts (without "ADD FORMATTING SYMBOLS") 
so they use the new UNIVERSAL_DEFAULT_PROMPT.
"""

import json
from pathlib import Path

def fix_prompts():
    """Clear old prompts to use new default."""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env file not found!")
        return
    
    print("=" * 80)
    print("ИСПРАВЛЕНИЕ УСТАРЕВШИХ ПРОМПТОВ")
    print("=" * 80)
    print()
    
    # Read .env file
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and update FORMATTING_APP_PROMPTS line
    updated = False
    cleared_count = 0
    
    for i, line in enumerate(lines):
        if line.startswith('FORMATTING_APP_PROMPTS='):
            try:
                # Extract JSON
                json_str = line.split('=', 1)[1].strip()
                data = json.loads(json_str)
                
                print(f"Найдено {len(data)} приложений")
                print()
                
                # Check and clear OLD prompts (without "ADD FORMATTING SYMBOLS")
                for app in data:
                    old_prompt = data[app].get('prompt', '')
                    
                    if old_prompt:
                        # Check if prompt is OLD (doesn't have "ADD FORMATTING SYMBOLS")
                        is_old = "ADD FORMATTING SYMBOLS" not in old_prompt
                        
                        if is_old:
                            print(f"   🧹 Очистка УСТАРЕВШЕГО промпта для {app}")
                            print(f"      Длина: {len(old_prompt)} символов")
                            print(f"      Причина: отсутствует 'ADD FORMATTING SYMBOLS'")
                            data[app]['prompt'] = ""
                            cleared_count += 1
                        else:
                            print(f"   ✓ {app} - промпт актуальный, оставляем")
                    else:
                        print(f"   ✓ {app} - уже пустой (будет использовать дефолтный)")
                
                print()
                
                if cleared_count > 0:
                    print(f"Результат: {cleared_count} устаревших промптов очищено")
                    print("Они будут использовать новый UNIVERSAL_DEFAULT_PROMPT с поддержкой форматирования")
                else:
                    print("Результат: все промпты актуальные, изменений не требуется")
                
                print()
                
                # Save back
                new_json = json.dumps(data, ensure_ascii=False)
                lines[i] = f'FORMATTING_APP_PROMPTS={new_json}\n'
                updated = True
                
            except json.JSONDecodeError as e:
                print(f"❌ Ошибка парсинга JSON: {e}")
                return
    
    if updated:
        # Write back to file
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        if cleared_count > 0:
            print("✅ .env файл обновлен!")
            print()
            print("=" * 80)
            print("ЧТО ДАЛЬШЕ:")
            print("=" * 80)
            print("1. Перезапустите приложение")
            print("2. Попробуйте форматирование в LibreOffice/Word/Notion/Obsidian")
            print("3. Теперь должны появиться заголовки (# ## ###) и списки (- * 1.)")
            print("4. Если нужно, можете настроить промпты в UI (они сохранятся)")
            print()
        else:
            print("✅ Все промпты актуальные, изменений не требуется")
            print()
    else:
        print("❌ FORMATTING_APP_PROMPTS не найден в .env")


if __name__ == "__main__":
    fix_prompts()
