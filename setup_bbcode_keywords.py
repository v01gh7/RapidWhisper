"""
Добавление ключевых слов для BBCode форматирования.

Добавляет ключевые слова для определения сайтов и приложений, которые используют BBCode.
"""

import json
from pathlib import Path

# Ключевые слова для BBCode
BBCODE_KEYWORDS = [
    # Bitrix24
    "bitrix24",
    "b24",
    "битрикс24",
    "битрикс",
    
    # Популярные форумы
    "phpbb",
    "vbulletin",
    "mybb",
    "smf",
    "simple machines",
    "xenforo",
    "invision",
    "ipboard",
    
    # Форумы по ключевым словам
    "forum",
    "форум",
    "board",
    "доска",
    
    # Discord (поддерживает BBCode-подобный синтаксис)
    "discord",
    "дискорд",
    
    # Telegram (поддерживает HTML, но BBCode тоже работает в некоторых ботах)
    "telegram",
    "телеграм",
    
    # Reddit (markdown, но можно использовать BBCode в некоторых сабреддитах)
    "reddit",
    "реддит",
    
    # Stack Overflow и подобные
    "stack overflow",
    "stackoverflow",
    "stack exchange",
    
    # Другие популярные платформы
    "4pda",
    "habr",
    "хабр",
    "pikabu",
    "пикабу",
]


def add_bbcode_keywords():
    """Добавить ключевые слова для BBCode в .env файл."""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env файл не найден!")
        return
    
    print("=" * 80)
    print("ДОБАВЛЕНИЕ КЛЮЧЕВЫХ СЛОВ ДЛЯ BBCODE")
    print("=" * 80)
    print()
    
    # Read .env file
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find FORMATTING_WEB_APP_KEYWORDS
    updated = False
    
    for i, line in enumerate(lines):
        if line.startswith('FORMATTING_WEB_APP_KEYWORDS='):
            try:
                # Extract JSON
                json_str = line.split('=', 1)[1].strip()
                
                # Parse JSON
                try:
                    data = json.loads(json_str)
                except json.JSONDecodeError:
                    print("⚠️  JSON сломан, создаем заново...")
                    data = {}
                
                # Add BBCode keywords
                if "bbcode" not in data:
                    data["bbcode"] = BBCODE_KEYWORDS
                    print(f"   ✅ Добавлено {len(BBCODE_KEYWORDS)} ключевых слов для BBCode")
                else:
                    # Merge with existing
                    existing = set(data["bbcode"])
                    new_keywords = set(BBCODE_KEYWORDS)
                    merged = list(existing | new_keywords)
                    data["bbcode"] = merged
                    print(f"   ✅ Обновлено: теперь {len(merged)} ключевых слов для BBCode")
                
                print()
                print("Ключевые слова для BBCode:")
                print("  - Bitrix24: bitrix24, b24, битрикс24")
                print("  - Форумы: phpbb, vbulletin, mybb, xenforo, forum")
                print("  - Мессенджеры: discord, telegram")
                print("  - Сайты: 4pda, habr, pikabu, reddit")
                print(f"  - Всего: {len(data['bbcode'])} ключевых слов")
                print()
                
                # Save back
                new_json = json.dumps(data, ensure_ascii=False)
                lines[i] = f'FORMATTING_WEB_APP_KEYWORDS={new_json}\n'
                
                updated = True
                break
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                import traceback
                traceback.print_exc()
                return
    
    if not updated:
        # FORMATTING_WEB_APP_KEYWORDS not found, add it
        print("⚠️  FORMATTING_WEB_APP_KEYWORDS не найден, добавляем...")
        
        # Load existing keywords from formatting_module
        from services.formatting_module import BROWSER_TITLE_MAPPINGS
        data = {
            format_type: list(patterns)
            for format_type, patterns in BROWSER_TITLE_MAPPINGS.items()
        }
        
        # Add BBCode
        data["bbcode"] = BBCODE_KEYWORDS
        
        # Add to end of file
        new_json = json.dumps(data, ensure_ascii=False)
        lines.append(f'FORMATTING_WEB_APP_KEYWORDS={new_json}\n')
        
        print(f"   ✅ Добавлено {len(BBCODE_KEYWORDS)} ключевых слов для BBCode")
        updated = True
    
    if updated:
        # Write back to file
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("✅ .env файл обновлен!")
        print()
        print("=" * 80)
        print("ЧТО ДАЛЬШЕ:")
        print("=" * 80)
        print("1. Перезапустите приложение")
        print("2. Откройте Bitrix24 в браузере")
        print("3. Создайте задачу или комментарий")
        print("4. Используйте голосовой ввод - текст будет отформатирован в BBCode!")
        print()
        print("Примеры:")
        print("  - 'Это важный текст' → [b]Это важный текст[/b]")
        print("  - 'Список: первое, второе, третье' → [list][*]первое[*]второе[*]третье[/list]")
        print("  - 'Ссылка на сайт example.com' → [url=https://example.com]ссылка[/url]")
        print()


if __name__ == "__main__":
    add_bbcode_keywords()
