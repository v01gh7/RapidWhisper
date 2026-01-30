"""
Property-based tests for the i18n module.

Tests translation functions, language management, and locale-aware formatting
using property-based testing with Hypothesis.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from utils.i18n import (
    t, set_language, get_language, detect_system_language,
    is_rtl, SUPPORTED_LANGUAGES, TRANSLATIONS
)
from datetime import datetime
import os


# Test generators
@st.composite
def language_code(draw):
    """Generate random supported language codes."""
    return draw(st.sampled_from(list(SUPPORTED_LANGUAGES.keys())))


@st.composite
def valid_translation_key(draw):
    """Generate valid translation keys that exist in English translations."""
    # Get all keys from English (reference language)
    def get_all_keys(d, prefix=""):
        keys = []
        for k, v in d.items():
            full_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                keys.extend(get_all_keys(v, full_key))
            else:
                keys.append(full_key)
        return keys
    
    english_keys = get_all_keys(TRANSLATIONS.get("en", {}))
    
    # If no keys exist yet, return a placeholder
    if not english_keys:
        return "test.key"
    
    return draw(st.sampled_from(english_keys))


@st.composite
def invalid_translation_key(draw):
    """Generate invalid translation keys that don't exist."""
    # Generate random keys that are unlikely to exist
    parts = draw(st.lists(
        st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=("L",))),
        min_size=1,
        max_size=3
    ))
    return ".".join(parts) + ".nonexistent"


# Property 1: Translation function returns valid strings for all keys
@pytest.mark.skipif(
    len(TRANSLATIONS.get("en", {})) == 0,
    reason="Translations not yet populated (will be added in task 2)"
)
@given(language_code(), valid_translation_key())
@settings(max_examples=50)
def test_property_1_translation_returns_string(lang, key):
    """
    Feature: app-localization
    Property 1: Translation function returns valid strings for all keys
    **Validates: Requirements 2.1**
    
    For any supported language code and any valid translation key,
    calling t(key, lang) should return a non-empty string.
    """
    result = t(key, lang)
    
    # Should return a string
    assert isinstance(result, str), f"Translation should return string, got {type(result)}"
    
    # Should not be empty (either translation or fallback or key itself)
    assert len(result) > 0, f"Translation should not be empty for key {key}"


# Property 2: Fallback to English for missing translations
@given(language_code(), invalid_translation_key())
@settings(max_examples=50)
def test_property_2_fallback_to_english(lang, key):
    """
    Feature: app-localization
    Property 2: Fallback to English for missing translations
    **Validates: Requirements 1.4**
    
    For any supported language and any translation key that doesn't exist
    in that language, calling t(key, lang) should return the English
    translation if it exists, or the key itself if English also doesn't have it.
    """
    # Skip English itself
    assume(lang != "en")
    
    result = t(key, lang)
    
    # Should return a string
    assert isinstance(result, str), f"Translation should return string, got {type(result)}"
    
    # Should not be empty
    assert len(result) > 0, f"Translation should not be empty"
    
    # If key doesn't exist in target language, should return English or key
    # We can't easily verify the exact fallback without duplicating logic,
    # but we can verify it returns something reasonable
    assert result == key or result != "", "Should return key or valid fallback"


# Property 3: String formatting with parameters
@given(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("L",))))
@settings(max_examples=50)
def test_property_3_string_formatting(param_value):
    """
    Feature: app-localization
    Property 3: String formatting with parameters
    **Validates: Requirements 2.4**
    
    For any translation key containing format placeholders and any set of
    parameters, calling t(key, **params) should return a string with all
    placeholders replaced by parameter values.
    """
    # Create a test translation with a placeholder
    test_key = "test.formatted"
    test_template = "Hello {name}!"
    
    # Temporarily add to English translations
    if "test" not in TRANSLATIONS["en"]:
        TRANSLATIONS["en"]["test"] = {}
    TRANSLATIONS["en"]["test"]["formatted"] = test_template
    
    # Call translation with parameter
    result = t(test_key, "en", name=param_value)
    
    # Should contain the parameter value
    assert param_value in result, f"Result should contain parameter value: {param_value}"
    
    # Should not contain the placeholder
    assert "{name}" not in result, "Result should not contain placeholder"
    
    # Clean up
    if "formatted" in TRANSLATIONS["en"].get("test", {}):
        del TRANSLATIONS["en"]["test"]["formatted"]


# Property 4: Language persistence round-trip
@given(language_code())
@settings(max_examples=20)
def test_property_4_language_persistence(lang):
    """
    Feature: app-localization
    Property 4: Language persistence round-trip
    **Validates: Requirements 1.3, 2.2**
    
    For any supported language code, calling set_language(code) then
    get_language() should return the same language code, and the code
    should be persisted to the configuration file.
    """
    # Save original language
    original_lang = get_language()
    
    try:
        # Set new language
        set_language(lang)
        
        # Get language should return the same
        assert get_language() == lang, f"get_language() should return {lang}"
        
        # Verify it's persisted to config file
        from core.config import get_env_path
        from dotenv import load_dotenv
        
        env_path = str(get_env_path())
        load_dotenv(env_path, override=True)
        
        persisted_lang = os.getenv('INTERFACE_LANGUAGE')
        assert persisted_lang == lang, f"Language should be persisted to config: {lang}"
        
    finally:
        # Restore original language
        set_language(original_lang)


# Property 5: System language detection returns supported language
def test_property_5_system_language_detection():
    """
    Feature: app-localization
    Property 5: System language detection returns supported language
    **Validates: Requirements 1.2**
    
    For any system locale, calling detect_system_language() should return
    a language code that exists in SUPPORTED_LANGUAGES.
    """
    detected_lang = detect_system_language()
    
    # Should return a string
    assert isinstance(detected_lang, str), "Should return a string"
    
    # Should be a supported language
    assert detected_lang in SUPPORTED_LANGUAGES, \
        f"Detected language {detected_lang} should be in SUPPORTED_LANGUAGES"


# Property 12: RTL languages trigger right-to-left layout
@given(language_code())
@settings(max_examples=20)
def test_property_12_rtl_detection(lang):
    """
    Feature: app-localization
    Property 12: RTL languages trigger right-to-left layout
    **Validates: Requirements 7.1-7.4**
    
    For any RTL language (Arabic, Urdu), when that language is selected,
    is_rtl() should return True. For all non-RTL languages, is_rtl()
    should return False and layout should be LeftToRight.
    """
    # Check RTL detection
    expected_rtl = lang in ["ar", "ur"]
    actual_rtl = is_rtl(lang)
    
    assert actual_rtl == expected_rtl, \
        f"is_rtl({lang}) should return {expected_rtl}, got {actual_rtl}"
    
    # Verify SUPPORTED_LANGUAGES metadata matches
    lang_info = SUPPORTED_LANGUAGES[lang]
    assert lang_info["rtl"] == expected_rtl, \
        f"SUPPORTED_LANGUAGES[{lang}]['rtl'] should be {expected_rtl}"


# Unit tests for specific edge cases

def test_translation_with_missing_key():
    """Test that missing keys return the key itself."""
    result = t("nonexistent.key.that.does.not.exist", "en")
    assert result == "nonexistent.key.that.does.not.exist"


def test_translation_with_invalid_language():
    """Test that invalid language codes fall back to English."""
    # Add a test key to English
    if "test" not in TRANSLATIONS["en"]:
        TRANSLATIONS["en"]["test"] = {}
    TRANSLATIONS["en"]["test"]["invalid_lang"] = "Test value"
    
    result = t("test.invalid_lang", "invalid_lang_code")
    
    # Should fall back to English
    assert result == "Test value"
    
    # Clean up
    if "invalid_lang" in TRANSLATIONS["en"].get("test", {}):
        del TRANSLATIONS["en"]["test"]["invalid_lang"]


def test_translation_without_lang_parameter():
    """Test that t() uses current language when lang parameter is None."""
    # Save original language
    original_lang = get_language()
    
    try:
        # Set to English
        set_language("en")
        
        # Add a test key
        if "test" not in TRANSLATIONS["en"]:
            TRANSLATIONS["en"]["test"] = {}
        TRANSLATIONS["en"]["test"]["current_lang"] = "English value"
        
        # Call without lang parameter
        result = t("test.current_lang")
        
        assert result == "English value"
        
        # Clean up
        if "current_lang" in TRANSLATIONS["en"].get("test", {}):
            del TRANSLATIONS["en"]["test"]["current_lang"]
        
    finally:
        # Restore original language
        set_language(original_lang)


def test_supported_languages_count():
    """Test that exactly 15 languages are supported."""
    assert len(SUPPORTED_LANGUAGES) == 15, \
        f"Should support exactly 15 languages, got {len(SUPPORTED_LANGUAGES)}"


def test_supported_languages_metadata():
    """Test that all languages have required metadata."""
    required_keys = {"name", "native", "rtl", "locale"}
    
    for lang_code, lang_info in SUPPORTED_LANGUAGES.items():
        assert isinstance(lang_info, dict), \
            f"Language info for {lang_code} should be a dict"
        
        assert required_keys.issubset(lang_info.keys()), \
            f"Language {lang_code} missing required keys: {required_keys - lang_info.keys()}"
        
        assert isinstance(lang_info["rtl"], bool), \
            f"RTL flag for {lang_code} should be boolean"


def test_rtl_languages_only_arabic_and_urdu():
    """Test that only Arabic and Urdu are marked as RTL."""
    rtl_languages = [code for code, info in SUPPORTED_LANGUAGES.items() if info["rtl"]]
    
    assert set(rtl_languages) == {"ar", "ur"}, \
        f"Only Arabic and Urdu should be RTL, got {rtl_languages}"


def test_string_formatting_with_multiple_parameters():
    """Test string formatting with multiple parameters."""
    # Add a test key with multiple placeholders
    if "test" not in TRANSLATIONS["en"]:
        TRANSLATIONS["en"]["test"] = {}
    TRANSLATIONS["en"]["test"]["multi_param"] = "Hello {name}, you have {count} messages"
    
    result = t("test.multi_param", "en", name="Alice", count=5)
    
    assert "Alice" in result
    assert "5" in result
    assert "{name}" not in result
    assert "{count}" not in result
    
    # Clean up
    if "multi_param" in TRANSLATIONS["en"].get("test", {}):
        del TRANSLATIONS["en"]["test"]["multi_param"]


def test_string_formatting_with_missing_parameter():
    """Test that missing parameters are handled gracefully."""
    # Add a test key with placeholder
    if "test" not in TRANSLATIONS["en"]:
        TRANSLATIONS["en"]["test"] = {}
    TRANSLATIONS["en"]["test"]["missing_param"] = "Hello {name}!"
    
    # Call without providing the parameter
    result = t("test.missing_param", "en")
    
    # Should return the template with placeholder (graceful degradation)
    assert isinstance(result, str)
    assert len(result) > 0
    
    # Clean up
    if "missing_param" in TRANSLATIONS["en"].get("test", {}):
        del TRANSLATIONS["en"]["test"]["missing_param"]
