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

ALLOWED ACTIONS:
- ANALYZE the content and identify natural sections
- ADD emphasis for important points
- INSERT line breaks between logical sections
- STRUCTURE the content for maximum readability

WHATSAPP/TELEGRAM FORMATTING REQUIRED:

TEXT FORMATTING (CRITICAL - USE EXACT SYNTAX):
- *word* for bold - SINGLE asterisk before AND after word (example: *важный*)
- _word_ for italic - SINGLE underscore before AND after word (example: _курсив_)
- ~word~ for strikethrough - SINGLE tilde before AND after word (example: ~ошибка~)
- `word` for monospace/code - SINGLE backtick before AND after word (example: `код`)

CRITICAL SYNTAX RULES:
- Bold: *text* (NOT **text**)
- Italic: _text_ (NOT __text__)
- Strikethrough: ~text~ (MUST use tilde ~, NOT underscore _)
- Code: `text` (backtick, NOT quote)
- NO SPACES between symbols and text: *bold* (CORRECT), * bold * (WRONG)

MULTI-LINE CODE:
```
code block
multiple lines
```

QUOTES:
> quoted text (greater-than sign at start of line)

LISTS (simple, no special syntax):
- Use dash at start: - item
- Or numbered: 1. item

CRITICAL SPACING RULES (MUST FOLLOW):
- Add ONE blank line between paragraphs when:
  * Topic changes
  * Speaker introduces new idea with "то есть", "но", "также", "кроме того"
  * Logical break in thought flow
  * Transition words like "however", "but", "also", "additionally"
- Keep related sentences together in same paragraph (NO blank lines between them)
- Add ONE blank line before and after code blocks
- Add ONE blank line before and after quotes

PARAGRAPH DETECTION:
- NEW paragraph when: topic shift, "то есть" (that is), "но" (but) at start, "также" (also), "кроме того" (besides)
- SAME paragraph when: continuing same thought, elaborating on previous sentence, providing details

EXAMPLE FORMAT:
First paragraph with *important text* and _italic emphasis_. Some ~crossed out~ text here.

Second paragraph with `code example` inline. More text with *bold* and _italic_.

> This is a quoted text from someone

Third paragraph after quote.

```
Multi-line code block
goes here
```

- List item with *bold*
- List item with _italic_
- List item with ~strikethrough~

Another paragraph with mixed formatting: *bold*, _italic_, ~strikethrough~, and `code`.

FORBIDDEN ACTIONS:
- Using ** for bold (use single * instead)
- Using __ for italic (use single _ instead)
- Using _ for strikethrough (use ~ instead)
- Adding spaces between symbols and text
- Adding blank lines between every sentence
- Using # for headings (WhatsApp doesn't support it)
- Adding explanations (like "This is used for...")
- Adding descriptions (like "These items are...")
- Adding context or background information
- Completing incomplete thoughts
- Adding examples that weren't spoken

Task: Transform the transcribed speech into well-structured WHATSAPP/TELEGRAM formatted text with CORRECT SYNTAX using ONLY the original words.

Output ONLY the reformatted text with proper WhatsApp/Telegram formatting."""


# Ключевые слова для WhatsApp/Telegram формата
WHATSAPP_KEYWORDS = [
    # WhatsApp
    "whatsapp",
    "ватсап",
    "вотсап",
    "whats app",
    
    # Telegram
    "telegram",
    "телеграм",
    "телеграмм",
    
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
