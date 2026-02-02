"""
Configuration Loader for JSONC format

This module loads configuration from config.jsonc file
and provides backward compatibility with .env format.
"""

import json
import os
import sys
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger()


def create_default_configs():
    """
    Создает дефолтные config.jsonc и secrets.json если их нет.
    
    Копирует из примеров или создает с минимальными настройками.
    """
    from core.config import get_config_dir
    
    config_dir = get_config_dir()
    config_path = config_dir / "config.jsonc"
    secrets_path = config_dir / "secrets.json"
    
    # Создать config.jsonc если его нет
    if not config_path.exists():
        logger.info(f"Creating default config.jsonc at {config_path}")
        
        # Попробовать скопировать из примера
        example_path = Path("config.jsonc.example")
        if example_path.exists():
            shutil.copy(example_path, config_path)
            logger.info("Copied from config.jsonc.example")
        else:
            # Создать минимальный конфиг
            # Читаем из встроенного ресурса если это .exe
            if hasattr(sys, '_MEIPASS'):
                # Запущено из PyInstaller
                example_path = Path(sys._MEIPASS) / "config.jsonc.example"
                if example_path.exists():
                    shutil.copy(example_path, config_path)
                    logger.info("Copied from bundled config.jsonc.example")
                else:
                    _create_minimal_config(config_path)
            else:
                _create_minimal_config(config_path)
    
    # Создать secrets.json если его нет
    if not secrets_path.exists():
        logger.info(f"Creating default secrets.json at {secrets_path}")
        
        example_path = Path("secrets.json.example")
        if example_path.exists():
            shutil.copy(example_path, secrets_path)
            logger.info("Copied from secrets.json.example")
        else:
            # Создать минимальный secrets
            if hasattr(sys, '_MEIPASS'):
                example_path = Path(sys._MEIPASS) / "secrets.json.example"
                if example_path.exists():
                    shutil.copy(example_path, secrets_path)
                    logger.info("Copied from bundled secrets.json.example")
                else:
                    _create_minimal_secrets(secrets_path)
            else:
                _create_minimal_secrets(secrets_path)


def _create_minimal_config(config_path: Path):
    """Создает минимальный config.jsonc с полными app_prompts и web_keywords"""
    minimal_config = {
        "ai_provider": {
            "provider": "groq",
            "transcription_model": "",
            "api_keys": {
                "groq": "",
                "openai": "",
                "glm": ""
            },
            "custom": {
                "api_key": "",
                "base_url": "http://localhost:1234/v1/",
                "model": ""
            }
        },
        "application": {
            "hotkey": "ctrl+space",
            "format_selection_hotkey": "ctrl+alt+space"
        },
        "audio": {
            "silence_threshold": 0.02,
            "silence_duration": 1.5,
            "sample_rate": 16000,
            "chunk_size": 1024,
            "silence_padding": 650,
            "manual_stop": False
        },
        "window": {
            "auto_hide_delay": 2.5,
            "remember_position": True,
            "position_preset": "center",
            "position_x": None,
            "position_y": None,
            "opacity": 150,
            "font_sizes": {
                "floating_main": 14,
                "floating_info": 11,
                "settings_labels": 12,
                "settings_titles": 24
            }
        },
        "recording": {
            "keep_recordings": False,
            "recordings_path": ""
        },
        "post_processing": {
            "enabled": False,
            "provider": "groq",
            "model": "llama-3.3-70b-versatile",
            "custom_model": "",
            "prompt": "You are a text editor. Your task: fix grammatical errors, add punctuation and improve text readability. Preserve the original meaning and style. Don't add anything extra. Return only the corrected text without comments.",
            "glm_use_coding_plan": False,
            "llm": {
                "base_url": "http://localhost:1234/v1/",
                "api_key": "local"
            }
        },
        "formatting": {
            "enabled": True,
            "use_fixed_format": False,
            "fixed_format_name": "whatsapp",
            "app_prompts": {
                "notion": "config/prompts/notion.txt",
                "obsidian": "config/prompts/obsidian.txt",
                "markdown": "config/prompts/markdown.txt",
                "word": "config/prompts/word.txt",
                "libreoffice": "config/prompts/libreoffice.txt",
                "vscode": "config/prompts/vscode.txt",
                "_fallback": "config/prompts/_fallback.txt",
                "bbcode": "config/prompts/bbcode.txt",
                "whatsapp": "config/prompts/whatsapp.txt"
            },
            "web_app_keywords": {
                "bbcode": [
                    "bitrix24", "b24", "битрикс24", "битрикс", "phpbb", "vbulletin", "mybb",
                    "smf", "simple machines", "xenforo", "invision", "ipboard", "forum", "форум",
                    "board", "доска", "reddit", "реддит", "stack overflow", "stackoverflow",
                    "stack exchange", "мои задачи", "4pda", "habr", "хабр", "pikabu", "пикабу"
                ],
                "libreoffice": [
                    "libreoffice", "soffice", "writer", ".odt"
                ],
                "markdown": [
                    ".markdown", ".md", "dillinger", "github.dev", "gitlab", "gitpod",
                    "hackmd", "markdown", "stackedit", "typora online"
                ],
                "notion": [
                    "notion", "notion.app", "notion.exe", "notion.so"
                ],
                "obsidian": [
                    "obsidian", "obsidian publish", "obsidian.app", "obsidian.exe"
                ],
                "vscode": [
                    "code", "vscode", "visual studio code"
                ],
                "whatsapp": [
                    "discord", "discord.app", "discord.exe", "element", "matrix", "mattermost",
                    "rocket.chat", "rocketchat", "signal", "skype", "slack", "slack.app",
                    "slack.exe", "telegram", "viber", "whats app", "whatsapp", "whatsapp.app",
                    "whatsapp.exe", "вайбер", "ватсап", "вотсап", "дискорд", "сигнал",
                    "скайп", "слак", "телеграм", "телеграмм"
                ],
                "word": [
                    ".doc", ".docx", "airtable", "coda.io", "dropbox paper", "google docs",
                    "google forms", "google keep", "google sheets", "google slides",
                    "google документ", "google документы", "google презентации",
                    "google презентация", "google таблица", "google таблицы",
                    "google форма", "google формы", "microsoft excel online",
                    "microsoft powerpoint online", "microsoft word", "microsoft word online",
                    "office 365", "office online", "quip", "winword.exe", "word",
                    "zoho sheet", "zoho show", "zoho writer"
                ]
            },
            "custom": {
                "api_key": "",
                "base_url": "http://localhost:1234/v1/",
                "model": "llama-3.3-70b-versatile"
            }
        },
        "localization": {
            "language": "en"
        },
        "logging": {
            "level": "INFO",
            "file": "rapidwhisper.log"
        },
        "about": {
            "github_url": "https://github.com/yourusername/rapidwhisper",
            "docs_url": "https://github.com/yourusername/rapidwhisper/tree/main/docs"
        }
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(minimal_config, f, indent=2, ensure_ascii=False)
    logger.info(f"Created minimal config at {config_path}")


def _create_minimal_secrets(secrets_path: Path):
    """Создает минимальный secrets.json"""
    minimal_secrets = {
        "ai_provider": {
            "api_keys": {
                "groq": "",
                "openai": "",
                "glm": ""
            },
            "custom": {
                "api_key": ""
            }
        },
        "formatting": {
            "custom": {
                "api_key": ""
            }
        }
    }
    
    with open(secrets_path, 'w', encoding='utf-8') as f:
        json.dump(minimal_secrets, f, indent=2, ensure_ascii=False)
    logger.info(f"Created minimal secrets at {secrets_path}")


def strip_json_comments(json_str: str) -> str:
    """
    Remove comments from JSONC string.
    
    Supports:
    - Single-line comments: // comment
    - Multi-line comments: /* comment */
    
    Args:
        json_str: JSONC string with comments
        
    Returns:
        JSON string without comments
    """
    lines = []
    in_multiline_comment = False
    in_string = False
    escape_next = False
    
    for line in json_str.split('\n'):
        cleaned_line = []
        i = 0
        
        while i < len(line):
            char = line[i]
            
            # Handle escape sequences in strings
            if escape_next:
                cleaned_line.append(char)
                escape_next = False
                i += 1
                continue
            
            if char == '\\' and in_string:
                escape_next = True
                cleaned_line.append(char)
                i += 1
                continue
            
            # Handle string boundaries
            if char == '"' and not in_multiline_comment:
                in_string = not in_string
                cleaned_line.append(char)
                i += 1
                continue
            
            # Skip content inside strings
            if in_string:
                cleaned_line.append(char)
                i += 1
                continue
            
            # Handle multi-line comments
            if in_multiline_comment:
                if i + 1 < len(line) and line[i:i+2] == '*/':
                    in_multiline_comment = False
                    i += 2
                    continue
                i += 1
                continue
            
            # Check for comment start
            if i + 1 < len(line):
                two_chars = line[i:i+2]
                
                # Single-line comment
                if two_chars == '//':
                    break  # Skip rest of line
                
                # Multi-line comment start
                if two_chars == '/*':
                    in_multiline_comment = True
                    i += 2
                    continue
            
            cleaned_line.append(char)
            i += 1
        
        if cleaned_line:
            lines.append(''.join(cleaned_line))
    
    return '\n'.join(lines)


def load_jsonc(file_path: str) -> Dict[str, Any]:
    """
    Load JSONC file (JSON with comments).
    
    Args:
        file_path: Path to JSONC file
        
    Returns:
        Parsed configuration dictionary
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove comments
        json_str = strip_json_comments(content)
        
        # Parse JSON
        config = json.loads(json_str)
        
        logger.info(f"✓ Loaded configuration from {file_path}")
        return config
        
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSONC file: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise


def load_prompt_file(file_path: str) -> str:
    """
    Load prompt from text file.
    
    Args:
        file_path: Path to prompt file
        
    Returns:
        Prompt text
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"Prompt file not found: {file_path}")
        return ""
    except Exception as e:
        logger.error(f"Error loading prompt file {file_path}: {e}")
        return ""


class ConfigLoader:
    """
    Configuration loader with backward compatibility.
    
    Loads configuration from:
    1. config.jsonc (new format)
    2. secrets.json (API keys and sensitive data)
    3. .env (legacy format, fallback)
    """
    
    def __init__(self, config_path: str = "config.jsonc", secrets_path: str = "secrets.json"):
        """
        Initialize configuration loader.
        
        Args:
            config_path: Path to config.jsonc file
            secrets_path: Path to secrets.json file
        """
        self.config_path = config_path
        self.secrets_path = secrets_path
        self.config = None
        self.secrets = None
        self.prompts_cache = {}
    
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Configuration dictionary
        """
        # Создать дефолтные конфиги если их нет
        create_default_configs()
        
        # Try to load from config.jsonc
        if os.path.exists(self.config_path):
            logger.info(f"Loading configuration from {self.config_path}")
            self.config = load_jsonc(self.config_path)
            
            # Load secrets
            self._load_secrets()
            
            # Merge secrets into config
            self._merge_secrets()
            
            return self.config
        
        # Fallback to .env
        logger.warning(f"{self.config_path} not found, falling back to .env")
        return self._load_from_env()
    
    def _load_secrets(self):
        """Load secrets from secrets.json"""
        if not self.secrets_path:
            logger.info("No secrets path specified, skipping secrets loading")
            self.secrets = {}
            return
        
        if os.path.exists(self.secrets_path):
            try:
                with open(self.secrets_path, 'r', encoding='utf-8') as f:
                    self.secrets = json.load(f)
                logger.info(f"✓ Loaded secrets from {self.secrets_path}")
            except Exception as e:
                logger.warning(f"Failed to load secrets: {e}")
                self.secrets = {}
        else:
            logger.warning(f"Secrets file not found: {self.secrets_path}")
            logger.warning("API keys will not be available. Create secrets.json from secrets.json.example")
            self.secrets = {}
    
    def _merge_secrets(self):
        """Merge secrets into configuration"""
        if not self.secrets:
            return
        
        # NEW STRUCTURE: secrets.json mirrors config.jsonc structure
        # Merge ai_provider section
        if "ai_provider" in self.secrets:
            if "ai_provider" not in self.config:
                self.config["ai_provider"] = {}
            
            # Merge API keys
            if "api_keys" in self.secrets["ai_provider"]:
                self.config["ai_provider"]["api_keys"] = self.secrets["ai_provider"]["api_keys"]
            
            # Merge custom API key
            if "custom" in self.secrets["ai_provider"]:
                if "custom" not in self.config["ai_provider"]:
                    self.config["ai_provider"]["custom"] = {}
                if "api_key" in self.secrets["ai_provider"]["custom"]:
                    self.config["ai_provider"]["custom"]["api_key"] = self.secrets["ai_provider"]["custom"]["api_key"]
        
        # Merge formatting section
        if "formatting" in self.secrets:
            if "formatting" not in self.config:
                self.config["formatting"] = {}
            
            # Merge custom formatting API key
            if "custom" in self.secrets["formatting"]:
                if "custom" not in self.config["formatting"]:
                    self.config["formatting"]["custom"] = {}
                if "api_key" in self.secrets["formatting"]["custom"]:
                    self.config["formatting"]["custom"]["api_key"] = self.secrets["formatting"]["custom"]["api_key"]
        
        # LEGACY SUPPORT: Old structure for backward compatibility
        if "api_keys" in self.secrets:
            if "ai_provider" not in self.config:
                self.config["ai_provider"] = {}
            self.config["ai_provider"]["api_keys"] = self.secrets["api_keys"]
        
        if "custom_providers" in self.secrets:
            # Custom transcription API key
            if "api_key" in self.secrets["custom_providers"]:
                if "ai_provider" not in self.config:
                    self.config["ai_provider"] = {}
                if "custom" not in self.config["ai_provider"]:
                    self.config["ai_provider"]["custom"] = {}
                self.config["ai_provider"]["custom"]["api_key"] = self.secrets["custom_providers"]["api_key"]
            
            # Custom formatting API key
            if "formatting_api_key" in self.secrets["custom_providers"]:
                if "formatting" not in self.config:
                    self.config["formatting"] = {}
                if "custom" not in self.config["formatting"]:
                    self.config["formatting"]["custom"] = {}
                self.config["formatting"]["custom"]["api_key"] = self.secrets["custom_providers"]["formatting_api_key"]
    
    def _load_from_env(self) -> Dict[str, Any]:
        """
        Load configuration from .env file (legacy format).
        
        Returns:
            Configuration dictionary
        """
        from dotenv import load_dotenv
        
        # DEPRECATED: Этот метод оставлен только для обратной совместимости с тестами
        # В основном коде используйте ConfigLoader напрямую
        load_dotenv(".env", override=True)
        
        # This is a simplified version - full implementation would mirror migrate_to_jsonc.py
        logger.warning("Loading from .env is deprecated. Please run migrate_to_jsonc.py")
        
        return {
            "ai_provider": {
                "provider": os.getenv("AI_PROVIDER", "groq")
            }
            # ... rest of the configuration
        }
    
    def get_prompt(self, app_name: str) -> str:
        """
        Get formatting prompt for application.
        
        Args:
            app_name: Application name
            
        Returns:
            Prompt text
        """
        if not self.config:
            self.load()
        
        # Check cache first
        if app_name in self.prompts_cache:
            return self.prompts_cache[app_name]
        
        # Get prompt file path from config
        formatting = self.config.get("formatting", {})
        app_prompts = formatting.get("app_prompts", {})
        prompt_file = app_prompts.get(app_name, "")
        
        if not prompt_file:
            logger.warning(f"No prompt file configured for '{app_name}'")
            return ""
        
        # Load prompt from file
        prompt = load_prompt_file(prompt_file)
        
        # Cache it
        self.prompts_cache[app_name] = prompt
        
        return prompt
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated path.
        
        Examples:
            config.get("ai_provider.provider")
            config.get("window.width")
            config.get("formatting.enabled")
        
        Args:
            key_path: Dot-separated path to configuration value
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        if not self.config:
            self.load()
        
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value


# Global configuration loader instance
_config_loader = None


def get_config_loader() -> ConfigLoader:
    """Get global configuration loader instance"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader
