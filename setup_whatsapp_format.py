"""
Добавление поддержки WhatsApp/Telegram форматирования.

WhatsApp использует упрощенный Markdown формат.
Тот же формат используют: Telegram, Slack, Discord, Signal.
"""

import json
from pathlib import Path

# WhatsApp/Telegram prompt - упрощенный Markdown
WHATSAPP_PROMPT = """CRITICAL: You are a TEXT FORMATTER, not a writer. Your ONLY job is to format existing text.

STRICT RULES:
1. DO NOT ADD ANY NEW WORDS - Use ONLY the words from the original text
2. DO NOT EXPLAIN - No descriptions, no examples, no elaborations
3. DO NOT EXPAND - Keep the exact same content, just reorganize it
4. DO NOT COMPLETE - If a sentence is incomplete, leave it incomplete
5. DO NOT randomly apply formatting - only format when it makes sense

ALLOWED ACTIONS:
- ANALYZE the content and identify natural sections
- ADD emphasis for TRULY important points (not random words)
- INSERT line breaks between logical sections
- STRUCTURE the content for maximum readability
- Format lists properly with line breaks

WHATSAPP FORMATTING SYNTAX:

TEXT FORMATTING (use sparingly, only for emphasis):
- *word* for bold - ONLY for truly important words (example: *важно*)
- _word_ for italic - ONLY for emphasis or foreign words (example: _emphasis_)
- ~word~ for strikethrough - ONLY for corrections or deleted text (example: ~ошибка~)
- `word` for code/technical terms (example: `wikipedia.com`)

CRITICAL SYNTAX RULES:
- Bold: *text* (NOT **text**)
- Italic: _text_ (NOT __text__)
- Strikethrough: ~text~ (use tilde ~, NOT underscore _)
- Code: `text` (backtick, NOT quote)
- NO SPACES between symbols and text: *bold* (CORRECT), * bold * (WRONG)

LISTS - CRITICAL RULES (MUST FOLLOW):
1. Each list item MUST be on SEPARATE LINE
2. Press ENTER after EACH item
3. DO NOT format list items (no bold/italic/strikethrough)
4. Keep list items as PLAIN TEXT
5. Add blank line BEFORE list
6. Add blank line AFTER list

CORRECT LIST FORMAT:
- First item
- Second item
- Third item

WRONG LIST FORMATS (DO NOT DO THIS):
❌ - First item, - Second item, - Third item (all on one line)
❌ - *First item* (formatted)
❌ - _Second item_ (formatted)
❌ - ~Third item~ (formatted)

MULTI-LINE CODE:
```
code block
multiple lines
```

QUOTES:
> quoted text

CRITICAL SPACING RULES:
- Add ONE blank line between paragraphs when topic changes
- Add ONE blank line before and after lists
- Each list item on NEW LINE (press Enter after each item)
- Add ONE blank line before and after code blocks
- Keep related sentences together in same paragraph

PARAGRAPH DETECTION:
- NEW paragraph when: topic shift, "то есть", "но", "также", "кроме того"
- SAME paragraph when: continuing same thought

FORMATTING GUIDELINES:
- DO NOT format every word - only truly important ones
- DO NOT format list items (keep them plain)
- Lists should be plain text unless specific emphasis needed
- Use formatting sparingly and meaningfully

EXAMPLE FORMAT:
First paragraph about *important topic*. Multiple sentences together.

Second paragraph with different topic. Has _emphasis_ on key word.

List of items (each on new line, NO formatting):
- First item
- Second item
- Third item

Another paragraph with `code` or technical term.

WRONG EXAMPLE (DO NOT DO THIS):
- *First item*
- _Second item_
- ~Third item~

This is wrong because list items should NOT be formatted!

FORBIDDEN ACTIONS:
- Formatting list items (bold/italic/strikethrough)
- Putting all list items on one line
- Using ** for bold (use single *)
- Using __ for italic (use single _)
- Using _ for strikethrough (use ~)
- Adding spaces between symbols and text
- Adding blank lines between every sentence
- Using # for headings (WhatsApp doesn't support it)

Task: Transform the transcribed speech into well-structured WHATSAPP formatted text with PROPER LINE BREAKS and NO FORMATTING ON LIST ITEMS using ONLY the original words.

Output ONLY the reformatted text."""


# Ключевые слова для WhatsApp/Telegram формата
WHATSAPP_KEYWORDS = [
    # WhatsApp
    "whatsapp",
    "ватсап",
    "вотсап",
    "whats app",
    
    # Slack
    "slack",
    "слак",
    
    # Discord (частично поддерживает)
    "discord",
    "дискорд",
    
    # Signal
    "signal",
    "сигнал",
    
    # Viber
    "viber",
    "вайбер",
    
    # Skype
    "skype",
    "скайп",
    
    # Matrix/Element
    "element",
    "matrix",
    
    # Mattermost
    "mattermost",
    
    # Rocket.Chat
    "rocket.chat",
    "rocketchat",
]


def add_whatsapp_support():
    """Добавить поддержку WhatsApp/Telegram формата в .env файл."""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env файл не найден!")
        return
    
    print("=" * 80)
    print("ДОБАВЛЕНИЕ ПОДДЕРЖКИ WHATSAPP/TELEGRAM ФОРМАТА")
    print("=" * 80)
    print()
    
    # Read .env file
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and update FORMATTING_APP_PROMPTS line
    updated_prompts = False
    
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
                
                # Add WhatsApp application
                if "whatsapp" not in data:
                    data["whatsapp"] = {
                        "enabled": True,
                        "prompt": WHATSAPP_PROMPT
                    }
                    print(f"   ✅ whatsapp → WhatsApp/Telegram промпт добавлен ({len(WHATSAPP_PROMPT)} символов)")
                else:
                    # Update existing
                    data["whatsapp"]["prompt"] = WHATSAPP_PROMPT
                    print(f"   ✅ whatsapp → WhatsApp/Telegram промпт обновлен ({len(WHATSAPP_PROMPT)} символов)")
                
                print()
                print("WhatsApp/Telegram форматирование:")
                print("  - Жирный: *текст*")
                print("  - Курсив: _текст_")
                print("  - Зачеркнутый: ~текст~")
                print("  - Код: `текст`")
                print("  - Цитата: > текст")
                print("  - Списки: - пункт или 1. пункт")
                print()
                
                # Save back - SINGLE LINE with escaped newlines
                new_json = json.dumps(data, ensure_ascii=False)
                new_json = new_json.replace('\\n', '\\\\n')
                lines[i] = f'FORMATTING_APP_PROMPTS={new_json}\n'
                
                # Remove any continuation lines
                if j > i + 1:
                    del lines[i+1:j]
                
                updated_prompts = True
                break
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                import traceback
                traceback.print_exc()
                return
    
    if updated_prompts:
        # Write back to file
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("✅ .env файл обновлен (промпты)!")
        print()
        
        # Also update FORMATTING_APPLICATIONS
        for i, line in enumerate(lines):
            if line.startswith('FORMATTING_APPLICATIONS='):
                apps = line.split('=', 1)[1].strip().split(',')
                if 'whatsapp' not in apps:
                    apps.append('whatsapp')
                    lines[i] = f'FORMATTING_APPLICATIONS={",".join(apps)}\n'
                    with open(env_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    print("✅ whatsapp добавлен в список приложений")
                break
    
    # Now add keywords
    updated_keywords = False
    
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
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
                
                # Add WhatsApp keywords
                if "whatsapp" not in data:
                    data["whatsapp"] = WHATSAPP_KEYWORDS
                    print(f"   ✅ Добавлено {len(WHATSAPP_KEYWORDS)} ключевых слов для WhatsApp/Telegram")
                else:
                    # Merge with existing
                    existing = set(data["whatsapp"])
                    new_keywords = set(WHATSAPP_KEYWORDS)
                    merged = list(existing | new_keywords)
                    data["whatsapp"] = merged
                    print(f"   ✅ Обновлено: теперь {len(merged)} ключевых слов для WhatsApp/Telegram")
                
                print()
                print("Ключевые слова для WhatsApp/Telegram:")
                print("  - Мессенджеры: whatsapp, telegram, slack, discord, signal")
                print("  - Viber, Skype, Element, Mattermost")
                print(f"  - Всего: {len(data['whatsapp'])} ключевых слов")
                print()
                
                # Save back
                new_json = json.dumps(data, ensure_ascii=False)
                lines[i] = f'FORMATTING_WEB_APP_KEYWORDS={new_json}\n'
                
                updated_keywords = True
                break
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                import traceback
                traceback.print_exc()
                return
    
    if updated_keywords:
        # Write back to file
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("✅ .env файл обновлен (ключевые слова)!")
        print()
        print("=" * 80)
        print("ЧТО ДАЛЬШЕ:")
        print("=" * 80)
        print("1. Перезапустите приложение")
        print("2. Откройте WhatsApp Web или Telegram Web в браузере")
        print("3. Используйте голосовой ввод - текст будет отформатирован!")
        print()
        print("Примеры:")
        print("  - 'Это важный текст' → *Это важный текст*")
        print("  - 'Это курсив' → _Это курсив_")
        print("  - 'Список: первое, второе, третье' → - первое\\n- второе\\n- третье")
        print()
    else:
        print("❌ FORMATTING_WEB_APP_KEYWORDS не найден в .env")


if __name__ == "__main__":
    add_whatsapp_support()
