"""
Internationalization (i18n) module for RapidWhisper.

This module provides translation functions, language management,
and locale-aware formatting for 15 supported languages.
"""

import os
import locale
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

# Global state
_current_language: str = "en"

# Supported languages with metadata
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "native": "English", "rtl": False, "locale": "en_GB"},
    "zh": {"name": "Chinese", "native": "中文", "rtl": False, "locale": "zh_CN"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "rtl": False, "locale": "hi_IN"},
    "es": {"name": "Spanish", "native": "Español", "rtl": False, "locale": "es_ES"},
    "fr": {"name": "French", "native": "Français", "rtl": False, "locale": "fr_FR"},
    "ar": {"name": "Arabic", "native": "العربية", "rtl": True, "locale": "ar_SA"},
    "bn": {"name": "Bengali", "native": "বাংলা", "rtl": False, "locale": "bn_BD"},
    "ru": {"name": "Russian", "native": "Русский", "rtl": False, "locale": "ru_RU"},
    "pt": {"name": "Portuguese", "native": "Português", "rtl": False, "locale": "pt_PT"},
    "ur": {"name": "Urdu", "native": "اردو", "rtl": True, "locale": "ur_PK"},
    "id": {"name": "Indonesian", "native": "Indonesia", "rtl": False, "locale": "id_ID"},
    "de": {"name": "German", "native": "Deutsch", "rtl": False, "locale": "de_DE"},
    "ja": {"name": "Japanese", "native": "日本語", "rtl": False, "locale": "ja_JP"},
    "tr": {"name": "Turkish", "native": "Türkçe", "rtl": False, "locale": "tr_TR"},
    "ko": {"name": "Korean", "native": "한국어", "rtl": False, "locale": "ko_KR"},
}

# Translation dictionaries (loaded from JSON files)
TRANSLATIONS: Dict[str, Dict[str, Any]] = {}


def _load_translations() -> None:
    """
    Load translations from JSON files in utils/translations/ directory.
    
    Loads translation files for all supported languages. If a translation file
    is missing or cannot be loaded, logs a warning and continues with empty
    translations for that language.
    """
    global TRANSLATIONS
    
    # Get the directory where this module is located
    module_dir = Path(__file__).parent
    translations_dir = module_dir / "translations"
    
    # Initialize empty translations for all languages
    for lang_code in SUPPORTED_LANGUAGES:
        TRANSLATIONS[lang_code] = {}
    
    # Load translation files
    for lang_code in SUPPORTED_LANGUAGES:
        translation_file = translations_dir / f"{lang_code}.json"
        
        if translation_file.exists():
            try:
                with open(translation_file, 'r', encoding='utf-8') as f:
                    TRANSLATIONS[lang_code] = json.load(f)
            except Exception as e:
                # Log error but continue
                from utils.logger import get_logger
                logger = get_logger()
                logger.error(f"Failed to load translations for {lang_code}: {e}")
        else:
            # Log warning if translation file is missing (except for languages not yet implemented)
            if lang_code in ["en", "ru"]:
                from utils.logger import get_logger
                logger = get_logger()
                logger.warning(f"Translation file not found: {translation_file}")


# Load translations on module import
_load_translations()


def t(key: str, lang: Optional[str] = None, **kwargs) -> str:
    """
    Translate a key to the specified language.
    
    Args:
        key: Translation key in dot notation (e.g., "settings.title")
        lang: Language code (e.g., "en", "ru"). If None, uses current language.
        **kwargs: Format parameters for string interpolation
        
    Returns:
        Translated string with parameters interpolated
        
    Example:
        t("errors.file_not_found", filename="test.wav")
        # Returns: "File not found: test.wav" (in current language)
    """
    global _current_language
    
    # Use current language if not specified
    if lang is None:
        lang = _current_language
    
    # Normalize language code (en-gb, en-us -> en)
    base_lang = lang.split('-')[0] if '-' in lang else lang
    
    # Validate language code
    if base_lang not in SUPPORTED_LANGUAGES:
        from utils.logger import get_logger
        logger = get_logger()
        logger.warning(f"Invalid language code: {lang}, falling back to English")
        base_lang = "en"
    
    # Split key into parts
    parts = key.split(".")
    
    # Try to get translation for specified language
    translation = TRANSLATIONS.get(base_lang, {})
    for part in parts:
        if isinstance(translation, dict):
            translation = translation.get(part)
        else:
            translation = None
            break
    
    # If translation not found, try English fallback
    if translation is None:
        from utils.logger import get_logger
        logger = get_logger()
        logger.warning(f"Translation missing: {key} for language {lang}")
        
        translation = TRANSLATIONS.get("en", {})
        for part in parts:
            if isinstance(translation, dict):
                translation = translation.get(part)
            else:
                translation = None
                break
    
    # If still not found, return the key itself
    if translation is None:
        return key
    
    # Format string with parameters if provided
    if kwargs:
        try:
            return str(translation).format(**kwargs)
        except (KeyError, ValueError) as e:
            from utils.logger import get_logger
            logger = get_logger()
            logger.error(f"Malformed translation: {key} in {lang}, error: {e}")
            return str(translation)
    
    return str(translation)


def set_language(lang_code: str) -> None:
    """
    Set the current interface language.
    
    Args:
        lang_code: Language code (e.g., "en", "ru", "zh", "en-gb", "en-us")
        
    Side Effects:
        - Updates global _current_language variable
        - Saves to config file (INTERFACE_LANGUAGE)
    """
    global _current_language
    
    # Normalize language code (en-gb, en-us -> en for validation)
    base_lang = lang_code.split('-')[0] if '-' in lang_code else lang_code
    
    # Validate language code
    if base_lang not in SUPPORTED_LANGUAGES:
        from utils.logger import get_logger
        logger = get_logger()
        logger.warning(f"Invalid language code: {lang_code}, falling back to English")
        lang_code = "en"
    
    # Update global state (keep full code like en-gb, en-us)
    _current_language = lang_code
    
    # Save to config file
    try:
        from core.config_saver import get_config_saver
        
        config_saver = get_config_saver()
        config_saver.update_value("localization.language", lang_code)
        
        from utils.logger import get_logger
        logger = get_logger()
        logger.info(f"Language changed to: {lang_code}")
    except Exception as e:
        from utils.logger import get_logger
        logger = get_logger()
        logger.error(f"Failed to save language to config: {e}")


def get_language() -> str:
    """
    Get the current interface language code.
    
    Returns:
        Current language code (e.g., "en", "ru")
    """
    global _current_language
    return _current_language


def detect_system_language() -> str:
    """
    Detect the system's default language.
    
    Returns:
        Language code matching system locale, or "en" if not supported
        
    Implementation:
        - Uses locale.getlocale() on Windows/Linux
        - Falls back to environment variables
        - Maps system locale to supported language codes
    """
    try:
        # Try to get system locale
        try:
            system_locale = locale.getlocale()[0]
        except Exception:
            # Fallback to environment variables
            system_locale = os.getenv('LANG') or os.getenv('LANGUAGE') or os.getenv('LC_ALL')
        
        if not system_locale:
            return "en"
        
        # Extract language code (first 2 characters)
        lang_code = str(system_locale).lower()[:2]
        
        # Return if supported, otherwise English
        if lang_code in SUPPORTED_LANGUAGES:
            return lang_code
        else:
            return "en"
            
    except Exception:
        # In case of any error, return English
        return "en"


def is_rtl(lang_code: Optional[str] = None) -> bool:
    """
    Check if a language uses right-to-left text direction.
    
    Args:
        lang_code: Language code. If None, uses current language.
        
    Returns:
        True if language is RTL (Arabic, Urdu), False otherwise
    """
    global _current_language
    
    if lang_code is None:
        lang_code = _current_language
    
    # Validate language code
    if lang_code not in SUPPORTED_LANGUAGES:
        return False
    
    return SUPPORTED_LANGUAGES[lang_code]["rtl"]


def get_missing_translations() -> Dict[str, List[str]]:
    """
    Validate translations and find missing keys.
    
    Returns:
        Dictionary mapping language codes to lists of missing keys
        
    Example:
        {
            "zh": ["settings.new_feature", "errors.new_error"],
            "ar": ["settings.new_feature"]
        }
    """
    missing = {}
    
    # Get all keys from English (reference language)
    def get_all_keys(d: Dict[str, Any], prefix: str = "") -> List[str]:
        keys = []
        for k, v in d.items():
            full_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                keys.extend(get_all_keys(v, full_key))
            else:
                keys.append(full_key)
        return keys
    
    english_keys = set(get_all_keys(TRANSLATIONS.get("en", {})))
    
    # Check each language for missing keys
    for lang_code in SUPPORTED_LANGUAGES:
        if lang_code == "en":
            continue  # Skip English (reference)
        
        lang_keys = set(get_all_keys(TRANSLATIONS.get(lang_code, {})))
        missing_keys = english_keys - lang_keys
        
        if missing_keys:
            missing[lang_code] = sorted(list(missing_keys))
    
    return missing


# Initialize current language from config on module load
def _initialize_language():
    """Initialize current language from config file."""
    global _current_language
    
    try:
        from core.config import Config
        config = Config.load_from_config()
        _current_language = config.interface_language
    except Exception:
        # If config loading fails, use system language
        _current_language = detect_system_language()


# Initialize on module import
_initialize_language()
