"""
Добавление поддержки BBCode форматирования.

BBCode используется на форумах, в Discord, Telegram и других платформах.
"""

import json
from pathlib import Path

# BBCode prompt - полная поддержка всех тегов
BBCODE_PROMPT = """CRITICAL: You are a TEXT FORMATTER, not a writer. Your ONLY job is to format existing text.

STRICT RULES:
1. DO NOT ADD ANY NEW WORDS - Use ONLY the words from the original text
2. DO NOT EXPLAIN - No descriptions, no examples, no elaborations
3. DO NOT EXPAND - Keep the exact same content, just reorganize it
4. DO NOT COMPLETE - If a sentence is incomplete, leave it incomplete

ALLOWED ACTIONS:
- ANALYZE the content and identify natural sections
- CREATE headings where appropriate for main topics and subtopics
- CONVERT lists when the speaker mentions multiple items
- ADD emphasis for important points
- INSERT line breaks between logical sections
- STRUCTURE the content for maximum readability

BBCODE FORMATTING REQUIRED:

TEXT FORMATTING:
- [b]text[/b] for bold
- [i]text[/i] for italic
- [u]text[/u] for underline
- [s]text[/s] for strikethrough
- [code]text[/code] for inline code
- [quote]text[/quote] for quotes
- [spoiler]text[/spoiler] for spoilers

HEADINGS (use size tags):
- [size=200]Heading 1[/size] for main heading
- [size=150]Heading 2[/size] for subheading
- [size=120]Heading 3[/size] for minor heading

COLORS:
- [color=red]text[/color] for colored text
- [color=#FF0000]text[/color] for hex colors

LISTS:
- [list]
[*]item 1
[*]item 2
[*]item 3
[/list]

NUMBERED LISTS:
- [list=1]
[*]first item
[*]second item
[*]third item
[/list]

LINKS:
- [url=https://example.com]link text[/url]

IMAGES:
- [img]https://example.com/image.jpg[/img]

CODE BLOCKS:
- [code]
multi-line code
goes here
[/code]

ALIGNMENT:
- [center]centered text[/center]
- [left]left aligned[/left]
- [right]right aligned[/right]

CRITICAL SPACING RULES (MUST FOLLOW):
- ALWAYS add TWO newlines (blank line) after EVERY heading
- ALWAYS add TWO newlines (blank line) between paragraphs
- ALWAYS add TWO newlines (blank line) before and after lists
- Each list item on separate line
- Separate different topics with TWO newlines

EXAMPLE FORMAT:
[size=200]Main Heading[/size]

First paragraph text here.

Second paragraph text here.

[size=150]Subheading[/size]

Paragraph under subheading.

[list]
[*]List item 1
[*]List item 2
[*]List item 3
[/list]

Another paragraph after list.

FORBIDDEN ACTIONS:
- Adding explanations (like "This is used for...")
- Adding descriptions (like "These items are...")
- Adding context or background information
- Completing incomplete thoughts
- Adding examples that weren't spoken

Task: Transform the transcribed speech into well-structured BBCODE text with PROPER SPACING using ONLY the original words.

Output ONLY the reformatted BBCode text with proper blank lines."""


def add_bbcode_support():
    """Добавить поддержку BBCode в .env файл."""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env файл не найден!")
        return
    
    print("=" * 80)
    print("ДОБАВЛЕНИЕ ПОДДЕРЖКИ BBCODE")
    print("=" * 80)
    print()
    
    # Read .env file
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and update FORMATTING_APP_PROMPTS line
    updated = False
    
    for i, line in enumerate(lines):
        if line.startswith('FORMATTING_APP_PROMPTS='):
            try:
                # Extract JSON
                json_start = i
                json_lines = [line.split('=', 1)[1]]
                
                # Check if JSON continues on next lines
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith(('FORMATTING_', '#', '')):
                    json_lines.append(lines[j])
                    j += 1
                
                json_str = ''.join(json_lines).strip()
                
                # Parse JSON
                try:
                    data = json.loads(json_str)
                except json.JSONDecodeError:
                    print("⚠️  JSON сломан, создаем заново...")
                    data = {}
                
                # Add BBCode application
                if "bbcode" not in data:
                    data["bbcode"] = {
                        "enabled": True,
                        "prompt": BBCODE_PROMPT
                    }
                    print(f"   ✅ bbcode → BBCode промпт добавлен ({len(BBCODE_PROMPT)} символов)")
                else:
                    # Update existing
                    data["bbcode"]["prompt"] = BBCODE_PROMPT
                    print(f"   ✅ bbcode → BBCode промпт обновлен ({len(BBCODE_PROMPT)} символов)")
                
                print()
                print("BBCode теги:")
                print("  - Текст: [b]жирный[/b], [i]курсив[/i], [u]подчеркнутый[/u], [s]зачеркнутый[/s]")
                print("  - Код: [code]код[/code]")
                print("  - Заголовки: [size=200]Заголовок[/size]")
                print("  - Списки: [list][*]пункт 1[*]пункт 2[/list]")
                print("  - Ссылки: [url=https://example.com]текст[/url]")
                print("  - Цвета: [color=red]красный текст[/color]")
                print("  - Цитаты: [quote]цитата[/quote]")
                print("  - Спойлеры: [spoiler]скрытый текст[/spoiler]")
                print()
                
                # Save back - SINGLE LINE with escaped newlines
                new_json = json.dumps(data, ensure_ascii=False)
                new_json = new_json.replace('\\n', '\\\\n')
                lines[i] = f'FORMATTING_APP_PROMPTS={new_json}\n'
                
                # Remove any continuation lines
                if j > i + 1:
                    del lines[i+1:j]
                
                updated = True
                break
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                import traceback
                traceback.print_exc()
                return
    
    if updated:
        # Write back to file
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("✅ .env файл обновлен!")
        print()
        
        # Also update FORMATTING_APPLICATIONS
        for i, line in enumerate(lines):
            if line.startswith('FORMATTING_APPLICATIONS='):
                apps = line.split('=', 1)[1].strip().split(',')
                if 'bbcode' not in apps:
                    apps.append('bbcode')
                    lines[i] = f'FORMATTING_APPLICATIONS={",".join(apps)}\n'
                    with open(env_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    print("✅ bbcode добавлен в список приложений")
                break
        
        print()
        print("=" * 80)
        print("ЧТО ДАЛЬШЕ:")
        print("=" * 80)
        print("1. Перезапустите приложение")
        print("2. В настройках → Форматирование:")
        print("   - Найдите приложение 'bbcode'")
        print("   - Добавьте ключевые слова для поиска (например: 'forum', 'discord')")
        print()
        print("3. Или используйте в UI:")
        print("   - Откройте настройки форматирования")
        print("   - Нажмите 'Настроить ключевые слова'")
        print("   - Добавьте для 'bbcode': forum, discord, telegram, и т.д.")
        print()
    else:
        print("❌ FORMATTING_APP_PROMPTS не найден в .env")


if __name__ == "__main__":
    add_bbcode_support()
