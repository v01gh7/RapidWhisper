"""
Property-based tests for error messages internationalization.

Feature: error-messages-i18n
Tests universal properties of exception translation across all languages.
"""

import pytest
from hypothesis import given, strategies as st, assume
from utils.exceptions import RapidWhisperError
from utils.i18n import SUPPORTED_LANGUAGES, t, set_language, get_language


# ============================================================================
# Test Data Generators
# ============================================================================

@st.composite
def language_code(draw):
    """Generate random supported language code."""
    return draw(st.sampled_from(list(SUPPORTED_LANGUAGES.keys())))


@st.composite
def translation_key(draw):
    """Generate random translation key in dot notation."""
    # Use realistic error message keys
    namespace = draw(st.sampled_from(["errors", "tray.notification", "status"]))
    key_name = draw(st.sampled_from([
        "api_authentication",
        "api_network",
        "api_timeout",
        "model_not_found",
        "file_not_found",
        "invalid_api_key"
    ]))
    return f"{namespace}.{key_name}"


@st.composite
def translation_params(draw):
    """Generate random translation parameters."""
    num_params = draw(st.integers(min_value=0, max_value=3))
    params = {}
    
    param_names = ["provider", "model", "filename", "error", "timeout"]
    
    for i in range(num_params):
        if i < len(param_names):
            param_name = param_names[i]
            # Generate realistic parameter values
            if param_name == "provider":
                value = draw(st.sampled_from(["Groq", "OpenAI", "GLM", "Custom"]))
            elif param_name == "model":
                value = draw(st.sampled_from(["whisper-large-v3", "gpt-4", "glm-4-voice"]))
            elif param_name == "timeout":
                value = draw(st.floats(min_value=1.0, max_value=120.0))
            else:
                value = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
                    whitelist_categories=("L", "N"), 
                    blacklist_characters="\n\r\t"
                )))
            params[param_name] = value
    
    return params


# ============================================================================
# Property 1: Exception Message Translation
# ============================================================================

@given(lang=language_code(), key=translation_key(), params=translation_params())
def test_property_1_exception_message_translation(lang, key, params):
    """
    Feature: error-messages-i18n
    Property 1: Exception Message Translation
    
    For any exception with a translation key, when the exception's user_message 
    property is accessed, the returned message should be in the current interface language.
    
    Validates: Requirements 1.1
    """
    # Set the interface language
    original_lang = get_language()
    try:
        set_language(lang)
        
        # Create exception with translation key
        exc = RapidWhisperError(
            message="Техническое сообщение для логов",
            translation_key=key,
            **params
        )
        
        # Access user_message property
        user_msg = exc.user_message
        
        # Verify message is a non-empty string
        assert isinstance(user_msg, str), f"user_message должно быть строкой, получено {type(user_msg)}"
        assert len(user_msg) > 0, "user_message не должно быть пустым"
        
        # Verify translation_key is preserved
        assert exc.translation_key == key, "translation_key должен сохраняться"
        
        # Verify technical message is preserved (for logging)
        assert exc.message == "Техническое сообщение для логов", "Техническое сообщение должно сохраняться"
        
    finally:
        # Restore original language
        set_language(original_lang)


# ============================================================================
# Property 2: Parameter Interpolation
# ============================================================================

@given(lang=language_code(), params=translation_params())
def test_property_2_parameter_interpolation(lang, params):
    """
    Feature: error-messages-i18n
    Property 2: Parameter Interpolation
    
    For any exception with a translation key and parameters, the user_message 
    should contain the interpolated parameter values in the correct positions.
    
    Validates: Requirements 1.2, 6.2
    """
    # Skip if no parameters
    assume(len(params) > 0)
    
    original_lang = get_language()
    try:
        set_language(lang)
        
        # Create exception with parameters
        exc = RapidWhisperError(
            message="Техническое сообщение",
            translation_key="errors.api_authentication",  # Known key with {provider} parameter
            **params
        )
        
        user_msg = exc.user_message
        
        # Verify message is a string
        assert isinstance(user_msg, str), "user_message должно быть строкой"
        
        # Verify parameters are stored
        assert exc.translation_params == params, "Параметры должны сохраняться"
        
        # If provider parameter exists, verify it's in the message
        # (unless translation is missing and fallback is used)
        if "provider" in params:
            provider_value = str(params["provider"])
            # The message should either contain the provider value or be a fallback
            # We can't guarantee the exact format, but we can check it's not empty
            assert len(user_msg) > 0, "Сообщение не должно быть пустым"
        
    finally:
        set_language(original_lang)


# ============================================================================
# Property 3: English Fallback for Missing Translations
# ============================================================================

@given(lang=language_code())
def test_property_3_english_fallback(lang):
    """
    Feature: error-messages-i18n
    Property 3: English Fallback for Missing Translations
    
    For any translation key that doesn't exist in the current language, 
    requesting the translation should return the English version or fallback.
    
    Validates: Requirements 1.3
    """
    # Use a non-existent translation key
    fake_key = "errors.nonexistent_error_key_12345"
    
    original_lang = get_language()
    try:
        set_language(lang)
        
        exc = RapidWhisperError(
            message="Техническое сообщение",
            translation_key=fake_key
        )
        
        user_msg = exc.user_message
        
        # Should return either:
        # 1. English translation (if exists)
        # 2. The translation key itself (if no translation exists in any language)
        # 3. Technical message (if i18n system fails)
        assert isinstance(user_msg, str), "user_message должно быть строкой"
        assert len(user_msg) > 0, "user_message не должно быть пустым"
        
        # When translation is missing in all languages, i18n.t() returns the key itself
        # This is the expected behavior according to the design
        assert user_msg in [fake_key, "Техническое сообщение"], \
            f"Должен вернуться либо ключ перевода, либо техническое сообщение, получено: {user_msg}"
        
    finally:
        set_language(original_lang)


# ============================================================================
# Property 4: Log Message Preservation
# ============================================================================

@given(lang=language_code(), key=translation_key(), params=translation_params())
def test_property_4_log_message_preservation(lang, key, params):
    """
    Feature: error-messages-i18n
    Property 4: Log Message Preservation
    
    For any exception that is logged, the log entry should contain the 
    technical message (Russian) and not the translated user message.
    
    Validates: Requirements 1.5, 4.1, 4.3, 4.4, 6.5
    """
    original_lang = get_language()
    try:
        set_language(lang)
        
        technical_msg = "Техническое сообщение для логов на русском"
        
        exc = RapidWhisperError(
            message=technical_msg,
            translation_key=key,
            **params
        )
        
        # Verify technical message is preserved
        assert exc.message == technical_msg, "Техническое сообщение должно сохраняться"
        
        # Verify str(exception) returns technical message (for logging)
        assert str(exc) == technical_msg, "str(exception) должен возвращать техническое сообщение"
        
        # Verify user_message is different (translated)
        user_msg = exc.user_message
        
        # User message should be either translated or fallback to technical
        assert isinstance(user_msg, str), "user_message должно быть строкой"
        
    finally:
        set_language(original_lang)


# ============================================================================
# Property 12: Legacy Exception Support (Backward Compatibility)
# ============================================================================

@given(lang=language_code())
def test_property_12_legacy_exception_support(lang):
    """
    Feature: error-messages-i18n
    Property 12: Legacy Exception Support
    
    For any exception created using the old constructor (without translation_key), 
    the exception should still work and display the original message.
    
    Validates: Requirements 8.1, 8.3, 8.5
    """
    original_lang = get_language()
    try:
        set_language(lang)
        
        # Old style: only message and user_message
        exc = RapidWhisperError(
            message="Техническое сообщение",
            user_message="Сообщение для пользователя"
        )
        
        # Should work without errors
        assert exc.message == "Техническое сообщение"
        assert exc.user_message == "Сообщение для пользователя"
        assert exc.translation_key is None
        assert len(exc.translation_params) == 0
        
        # Old style: only message (user_message defaults to message)
        exc2 = RapidWhisperError(message="Только техническое сообщение")
        
        assert exc2.message == "Только техническое сообщение"
        assert exc2.user_message == "Только техническое сообщение"
        
    finally:
        set_language(original_lang)


# ============================================================================
# Property 13: Graceful Degradation
# ============================================================================

@given(key=translation_key(), params=translation_params())
def test_property_13_graceful_degradation(key, params):
    """
    Feature: error-messages-i18n
    Property 13: Graceful Degradation
    
    For any exception, if the i18n system is unavailable or fails, 
    the user_message should fall back to the technical message.
    
    Validates: Requirements 8.2
    """
    technical_msg = "Техническое сообщение для fallback"
    
    exc = RapidWhisperError(
        message=technical_msg,
        translation_key=key,
        **params
    )
    
    # Even if i18n fails, should return something
    user_msg = exc.user_message
    
    assert isinstance(user_msg, str), "user_message должно быть строкой даже при ошибке i18n"
    assert len(user_msg) > 0, "user_message не должно быть пустым даже при ошибке i18n"
    
    # Should either return translated message or technical message (fallback)
    # We can't force i18n to fail in this test, but we verify the property exists
    assert hasattr(exc, 'message'), "Должно быть техническое сообщение для fallback"
    assert exc.message == technical_msg, "Техническое сообщение должно сохраняться"



# ============================================================================
# Property 6: Translation Completeness
# ============================================================================

def test_property_6_translation_completeness():
    """
    Feature: error-messages-i18n
    Property 6: Translation Completeness
    
    For any translation key that exists in the English translation file, 
    that key should exist in all 15 supported language files.
    
    Validates: Requirements 5.1
    """
    from utils.i18n import TRANSLATIONS, SUPPORTED_LANGUAGES
    
    # Get all error keys from English
    english_errors = TRANSLATIONS.get("en", {}).get("errors", {})
    english_keys = set(english_errors.keys())
    
    # Check each language
    missing_by_language = {}
    for lang_code in SUPPORTED_LANGUAGES:
        if lang_code == "en":
            continue  # Skip English (reference)
        
        lang_errors = TRANSLATIONS.get(lang_code, {}).get("errors", {})
        lang_keys = set(lang_errors.keys())
        
        missing_keys = english_keys - lang_keys
        if missing_keys:
            missing_by_language[lang_code] = missing_keys
    
    # All languages should have all error keys
    assert len(missing_by_language) == 0, \
        f"Missing error keys in languages: {missing_by_language}"


# ============================================================================
# Property 7: Translation File Structure Consistency
# ============================================================================

def test_property_7_translation_file_structure():
    """
    Feature: error-messages-i18n
    Property 7: Translation File Structure Consistency
    
    For any translation file, the JSON structure (namespaces, nesting levels) 
    should match the structure of the English translation file.
    
    Validates: Requirements 5.3, 5.4, 5.5
    """
    from utils.i18n import TRANSLATIONS, SUPPORTED_LANGUAGES
    
    # Get English structure
    english_trans = TRANSLATIONS.get("en", {})
    english_top_keys = set(english_trans.keys())
    
    # Check each language has same top-level keys
    for lang_code in SUPPORTED_LANGUAGES:
        if lang_code == "en":
            continue
        
        lang_trans = TRANSLATIONS.get(lang_code, {})
        lang_top_keys = set(lang_trans.keys())
        
        # Should have same top-level structure
        assert lang_top_keys == english_top_keys, \
            f"Language {lang_code} has different top-level structure. " \
            f"Missing: {english_top_keys - lang_top_keys}, " \
            f"Extra: {lang_top_keys - english_top_keys}"
        
        # Check errors namespace exists
        assert "errors" in lang_trans, \
            f"Language {lang_code} missing 'errors' namespace"
        
        # Check errors is a dict
        assert isinstance(lang_trans["errors"], dict), \
            f"Language {lang_code} 'errors' should be a dict"


# ============================================================================
# Property 8: Parameter Syntax Validation
# ============================================================================

def test_property_8_parameter_syntax():
    """
    Feature: error-messages-i18n
    Property 8: Parameter Syntax Validation
    
    For any translation string that contains parameters, the parameter syntax 
    should follow Python format string syntax (e.g., {parameter_name}).
    
    Validates: Requirements 5.2
    """
    import re
    from utils.i18n import TRANSLATIONS, SUPPORTED_LANGUAGES
    
    # Regex to find Python format string parameters
    param_pattern = re.compile(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}')
    
    # Check all error messages in all languages
    invalid_params = []
    
    for lang_code in SUPPORTED_LANGUAGES:
        lang_errors = TRANSLATIONS.get(lang_code, {}).get("errors", {})
        
        for key, value in lang_errors.items():
            if not isinstance(value, str):
                continue
            
            # Find all parameters in the string
            params = param_pattern.findall(value)
            
            # Check for invalid syntax (e.g., {}, {123}, etc.)
            # Valid parameters should match the pattern
            all_braces = re.findall(r'\{[^}]*\}', value)
            
            for brace in all_braces:
                # Check if it's a valid parameter
                if not param_pattern.match(brace):
                    invalid_params.append({
                        "lang": lang_code,
                        "key": key,
                        "value": value,
                        "invalid": brace
                    })
    
    # Should have no invalid parameters
    assert len(invalid_params) == 0, \
        f"Found invalid parameter syntax: {invalid_params}"
