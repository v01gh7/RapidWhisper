"""
Добавление ключевых слов для десктопных приложений в FORMATTING_WEB_APP_KEYWORDS.

Теперь все ключевые слова (и для веб, и для десктопа) хранятся в одном месте.
"""

import json
from pathlib import Path


# Ключевые слова для десктопных приложений
DESKTOP_KEYWORDS = {
    "notion": [
        # Веб
        "notion",
        "notion.so",
        # Десктоп
        "notion.exe",
        "notion.app",
    ],
    "obsidian": [
        # Веб
        "obsidian publish",
        # Десктоп
        "obsidian",
        "obsidian.exe",
        "obsidian.app",
    ],
    "markdown": [
        # Веб
        "hackmd",
        "stackedit",
        "dillinger",
        "typora online",
        "github.dev",
        "gitlab",
        "gitpod",
        # Десктоп и расширения
        ".md",
        ".markdown",
        "markdown",
    ],
    "word": [
        # Веб (уже есть в .env)
        "google docs",
        "google документы",
        "google документ",
        "google sheets",
        "google таблицы",
        "google таблица",
        "google slides",
        "google презентации",
        "google презентация",
        "google forms",
        "google формы",
        "google форма",
        "google keep",
        "microsoft word online",
        "microsoft excel online",
        "microsoft powerpoint online",
        "office online",
        "office 365",
        "zoho writer",
        "zoho sheet",
        "zoho show",
        "dropbox paper",
        "quip",
        "coda.io",
        "airtable",
        # Десктоп
        "word",
        "winword.exe",
        "microsoft word",
        ".docx",
        ".doc",
    ],
    "libreoffice": [
        # Десктоп
        "libreoffice",
        "soffice",
        "writer",
        ".odt",
    ],
    "vscode": [
        # Десктоп
        "code",
        "vscode",
        "visual studio code",
    ],
    "whatsapp": [
        # Веб (уже есть в .env)
        "whatsapp",
        "whats app",
        "ватсап",
        "вотсап",
        "slack",
        "слак",
        "discord",
        "дискорд",
        "telegram",
        "телеграм",
        "телеграмм",
        "signal",
        "сигнал",
        "viber",
        "вайбер",
        "skype",
        "скайп",
        "element",
        "matrix",
        "mattermost",
        "rocket.chat",
        "rocketchat",
        # Десктоп
        "whatsapp.exe",
        "whatsapp.app",
        "slack.exe",
        "slack.app",
        "discord.exe",
        "discord.app",
    ],
}


def add_desktop_keywords():
    """Добавить ключевые слова для десктопных приложений в .env файл."""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env файл не найден!")
        return
    
    print("=" * 80)
    print("ДОБАВЛЕНИЕ КЛЮЧЕВЫХ СЛОВ ДЛЯ ДЕСКТОПНЫХ ПРИЛОЖЕНИЙ")
    print("=" * 80)
    print()
    
    # Read .env file
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find FORMATTING_WEB_APP_KEYWORDS line
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
                
                # Merge desktop keywords with existing
                for format_type, keywords in DESKTOP_KEYWORDS.items():
                    if format_type in data:
                        # Merge with existing keywords
                        existing = set(data[format_type])
                        new_keywords = set(keywords)
                        merged = sorted(list(existing | new_keywords))
                        data[format_type] = merged
                        print(f"   ✅ {format_type}: обновлено ({len(existing)} → {len(merged)} ключевых слов)")
                    else:
                        # Add new format type
                        data[format_type] = keywords
                        print(f"   ✅ {format_type}: добавлено {len(keywords)} ключевых слов")
                
                print()
                print("Теперь все ключевые слова (веб + десктоп) в одном месте:")
                for format_type, keywords in data.items():
                    print(f"  - {format_type}: {len(keywords)} ключевых слов")
                print()
                
                # Save back
                new_json = json.dumps(data, ensure_ascii=False)
                lines[i] = f'FORMATTING_WEB_APP_KEYWORDS={new_json}\n'
                
                # Write back to file
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                print("✅ .env файл обновлен!")
                print()
                print("=" * 80)
                print("ЧТО ИЗМЕНИЛОСЬ:")
                print("=" * 80)
                print("1. Удалены хардкоженные FORMAT_MAPPINGS и BROWSER_TITLE_MAPPINGS")
                print("2. Все ключевые слова теперь в FORMATTING_WEB_APP_KEYWORDS")
                print("3. Работает для ВСЕХ приложений (веб + десктоп)")
                print("4. Можно редактировать через UI")
                print()
                print("Примеры:")
                print("  - Notion.exe → формат 'notion'")
                print("  - Google Docs в браузере → формат 'word'")
                print("  - WhatsApp.exe → формат 'whatsapp'")
                print("  - файл .md → формат 'markdown'")
                print()
                
                break
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                import traceback
                traceback.print_exc()
                return
    else:
        print("❌ FORMATTING_WEB_APP_KEYWORDS не найден в .env")


if __name__ == "__main__":
    add_desktop_keywords()
