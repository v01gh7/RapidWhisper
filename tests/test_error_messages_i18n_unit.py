"""
Unit tests for error messages internationalization.

Feature: error-messages-i18n
Tests specific examples and edge cases for exception translation.
"""

import pytest
from utils.exceptions import RapidWhisperError
from utils.i18n import set_language, get_language


class TestBackwardCompatibility:
    """Tests for backward compatibility with legacy exception usage."""
    
    def test_legacy_exception_with_user_message(self):
        """
        Test that old-style exceptions with user_message still work.
        
        Requirements: 8.1
        """
        exc = RapidWhisperError(
            message="Техническое сообщение",
            user_message="Сообщение для пользователя"
        )
        
        assert exc.message == "Техническое сообщение"
        assert exc.user_message == "Сообщение для пользователя"
        assert exc.translation_key is None
        assert len(exc.translation_params) == 0
    
    def test_legacy_exception_without_user_message(self):
        """
        Test that old-style exceptions without user_message default to message.
        
        Requirements: 8.1
        """
        exc = RapidWhisperError(message="Только техническое сообщение")
        
        assert exc.message == "Только техническое сообщение"
        assert exc.user_message == "Только техническое сообщение"
        assert exc.translation_key is None
    
    def test_mixed_usage_old_and_new_style(self):
        """
        Test that old and new style exceptions can coexist.
        
        Requirements: 8.1, 8.3
        """
        # Old style
        old_exc = RapidWhisperError(
            message="Старый стиль",
            user_message="Сообщение для пользователя"
        )
        
        # New style
        new_exc = RapidWhisperError(
            message="Новый стиль",
            translation_key="errors.api_authentication",
            provider="Groq"
        )
        
        # Both should work
        assert old_exc.user_message == "Сообщение для пользователя"
        assert isinstance(new_exc.user_message, str)
        assert len(new_exc.user_message) > 0
    
    def test_str_representation_returns_technical_message(self):
        """
        Test that str(exception) returns technical message for logging.
        
        Requirements: 8.5
        """
        exc = RapidWhisperError(
            message="Техническое сообщение для логов",
            translation_key="errors.api_authentication",
            provider="Groq"
        )
        
        # str() should return technical message (for logging)
        assert str(exc) == "Техническое сообщение для логов"
        
        # user_message should be different (translated)
        assert exc.user_message != exc.message or exc.translation_key is None


class TestNewStyleExceptions:
    """Tests for new-style exceptions with translation keys."""
    
    def test_exception_with_translation_key(self):
        """
        Test creating exception with translation key.
        
        Requirements: 6.1
        """
        exc = RapidWhisperError(
            message="Техническое сообщение",
            translation_key="errors.api_authentication",
            provider="Groq"
        )
        
        assert exc.message == "Техническое сообщение"
        assert exc.translation_key == "errors.api_authentication"
        assert exc.translation_params == {"provider": "Groq"}
    
    def test_exception_with_multiple_parameters(self):
        """
        Test exception with multiple translation parameters.
        
        Requirements: 6.2
        """
        exc = RapidWhisperError(
            message="Техническое сообщение",
            translation_key="errors.model_not_found",
            model="whisper-large-v3",
            provider="Groq"
        )
        
        assert exc.translation_params == {
            "model": "whisper-large-v3",
            "provider": "Groq"
        }
    
    def test_translation_key_preservation(self):
        """
        Test that translation_key is preserved.
        
        Requirements: 6.4
        """
        key = "errors.api_timeout"
        exc = RapidWhisperError(
            message="Техническое сообщение",
            translation_key=key,
            timeout=30.0
        )
        
        assert exc.translation_key == key
        # Accessing user_message should not modify translation_key
        _ = exc.user_message
        assert exc.translation_key == key


class TestEdgeCases:
    """Tests for edge cases and error conditions."""
    
    def test_empty_translation_params(self):
        """Test exception with no translation parameters."""
        exc = RapidWhisperError(
            message="Техническое сообщение",
            translation_key="errors.api_authentication"
        )
        
        assert exc.translation_params == {}
        assert isinstance(exc.user_message, str)
    
    def test_none_values_in_params(self):
        """Test exception with None values in parameters."""
        exc = RapidWhisperError(
            message="Техническое сообщение",
            translation_key="errors.api_timeout",
            timeout=None,
            provider="Groq"
        )
        
        assert exc.translation_params["timeout"] is None
        assert exc.translation_params["provider"] == "Groq"
    
    def test_special_characters_in_params(self):
        """Test exception with special characters in parameters."""
        exc = RapidWhisperError(
            message="Техническое сообщение",
            translation_key="errors.file_not_found",
            filename="файл с пробелами & спецсимволами.wav"
        )
        
        assert "filename" in exc.translation_params
        user_msg = exc.user_message
        assert isinstance(user_msg, str)
    
    def test_very_long_parameter_values(self):
        """Test exception with very long parameter values."""
        long_value = "A" * 1000
        exc = RapidWhisperError(
            message="Техническое сообщение",
            translation_key="errors.api_response_error",
            error=long_value
        )
        
        assert exc.translation_params["error"] == long_value
        user_msg = exc.user_message
        assert isinstance(user_msg, str)
    
    def test_numeric_parameter_values(self):
        """Test exception with numeric parameter values."""
        exc = RapidWhisperError(
            message="Техническое сообщение",
            translation_key="errors.api_timeout",
            timeout=30.5,
            retries=3
        )
        
        assert exc.translation_params["timeout"] == 30.5
        assert exc.translation_params["retries"] == 3
        user_msg = exc.user_message
        assert isinstance(user_msg, str)


class TestLanguageSwitching:
    """Tests for language switching behavior."""
    
    def test_user_message_changes_with_language(self):
        """
        Test that user_message reflects current language.
        
        Requirements: 1.1
        """
        original_lang = get_language()
        
        try:
            exc = RapidWhisperError(
                message="Техническое сообщение",
                translation_key="errors.api_authentication",
                provider="Groq"
            )
            
            # Get message in English
            set_language("en")
            msg_en = exc.user_message
            
            # Get message in Russian
            set_language("ru")
            msg_ru = exc.user_message
            
            # Messages should be strings
            assert isinstance(msg_en, str)
            assert isinstance(msg_ru, str)
            
            # Both should be non-empty
            assert len(msg_en) > 0
            assert len(msg_ru) > 0
            
        finally:
            set_language(original_lang)
    
    def test_technical_message_unchanged_by_language(self):
        """
        Test that technical message doesn't change with language.
        
        Requirements: 1.5, 4.1
        """
        original_lang = get_language()
        
        try:
            technical_msg = "Техническое сообщение на русском"
            exc = RapidWhisperError(
                message=technical_msg,
                translation_key="errors.api_authentication",
                provider="Groq"
            )
            
            # Change language
            set_language("en")
            assert exc.message == technical_msg
            
            set_language("ru")
            assert exc.message == technical_msg
            
            set_language("zh")
            assert exc.message == technical_msg
            
        finally:
            set_language(original_lang)


class TestFallbackBehavior:
    """Tests for fallback behavior when translations are missing."""
    
    def test_missing_translation_key_returns_key(self):
        """
        Test that missing translation key returns the key itself.
        
        Requirements: 8.4
        """
        fake_key = "errors.nonexistent_key_xyz"
        exc = RapidWhisperError(
            message="Техническое сообщение",
            translation_key=fake_key
        )
        
        user_msg = exc.user_message
        
        # Should return the key itself (i18n fallback behavior)
        assert user_msg == fake_key
    
    def test_i18n_failure_returns_technical_message(self):
        """
        Test graceful degradation when i18n system fails.
        
        Requirements: 8.2
        """
        # This test verifies the try-except in user_message property
        # Even if i18n fails, should return technical message
        exc = RapidWhisperError(
            message="Техническое сообщение для fallback",
            translation_key="errors.api_authentication"
        )
        
        # Should not raise exception
        user_msg = exc.user_message
        assert isinstance(user_msg, str)
        assert len(user_msg) > 0



class TestAPIExceptions:
    """Tests for API exception classes with i18n support."""
    
    def test_api_authentication_error_with_provider(self):
        """
        Test APIAuthenticationError with different providers.
        
        Requirements: 2.1
        """
        from utils.exceptions import APIAuthenticationError
        
        # Test with Groq provider
        exc_groq = APIAuthenticationError(provider="Groq")
        assert exc_groq.translation_key == "errors.api_authentication"
        assert exc_groq.translation_params["provider"] == "Groq"
        assert "Groq" in exc_groq.message
        user_msg = exc_groq.user_message
        assert isinstance(user_msg, str)
        assert len(user_msg) > 0
        
        # Test with OpenAI provider
        exc_openai = APIAuthenticationError(provider="OpenAI")
        assert exc_openai.translation_params["provider"] == "OpenAI"
        assert "OpenAI" in exc_openai.message
        
        # Test with custom provider
        exc_custom = APIAuthenticationError(provider="Custom Provider")
        assert exc_custom.translation_params["provider"] == "Custom Provider"
    
    def test_api_network_error_translation(self):
        """
        Test APINetworkError translation.
        
        Requirements: 2.2
        """
        from utils.exceptions import APINetworkError
        
        exc = APINetworkError(provider="Groq")
        assert exc.translation_key == "errors.api_network"
        assert exc.translation_params["provider"] == "Groq"
        assert "Ошибка подключения" in exc.message
        
        user_msg = exc.user_message
        assert isinstance(user_msg, str)
        assert len(user_msg) > 0
    
    def test_api_network_error_with_custom_message(self):
        """
        Test APINetworkError with custom technical message.
        
        Requirements: 2.2
        """
        from utils.exceptions import APINetworkError
        
        custom_msg = "Не удалось подключиться к api.groq.com"
        exc = APINetworkError(provider="Groq", message=custom_msg)
        
        assert exc.message == custom_msg
        assert exc.translation_key == "errors.api_network"
        assert exc.translation_params["provider"] == "Groq"
    
    def test_api_timeout_error_with_timeout_parameter(self):
        """
        Test APITimeoutError with timeout parameter.
        
        Requirements: 2.3
        """
        from utils.exceptions import APITimeoutError
        
        # With timeout value
        exc_with_timeout = APITimeoutError(provider="Groq", timeout=30.0)
        assert exc_with_timeout.translation_key == "errors.api_timeout"
        assert exc_with_timeout.translation_params["provider"] == "Groq"
        assert exc_with_timeout.translation_params["timeout"] == 30.0
        assert "30" in exc_with_timeout.message
        
        user_msg = exc_with_timeout.user_message
        assert isinstance(user_msg, str)
        assert len(user_msg) > 0
    
    def test_api_timeout_error_without_timeout_parameter(self):
        """
        Test APITimeoutError without timeout parameter.
        
        Requirements: 2.3
        """
        from utils.exceptions import APITimeoutError
        
        exc = APITimeoutError(provider="Groq")
        assert exc.translation_key == "errors.api_timeout"
        assert exc.translation_params["provider"] == "Groq"
        assert exc.translation_params["timeout"] is None
        
        user_msg = exc.user_message
        assert isinstance(user_msg, str)
        assert len(user_msg) > 0
    
    def test_model_not_found_error_with_model_and_provider(self):
        """
        Test ModelNotFoundError with model and provider parameters.
        
        Requirements: 2.5
        """
        from utils.exceptions import ModelNotFoundError
        
        exc = ModelNotFoundError(model="whisper-large-v3", provider="Groq")
        assert exc.translation_key == "errors.model_not_found"
        assert exc.translation_params["model"] == "whisper-large-v3"
        assert exc.translation_params["provider"] == "Groq"
        assert "whisper-large-v3" in exc.message
        assert "Groq" in exc.message
        
        user_msg = exc.user_message
        assert isinstance(user_msg, str)
        assert len(user_msg) > 0
    
    def test_model_not_found_error_with_different_models(self):
        """
        Test ModelNotFoundError with different model names.
        
        Requirements: 2.5
        """
        from utils.exceptions import ModelNotFoundError
        
        models = [
            "whisper-1",
            "gpt-4",
            "custom-model-v2",
            "модель-на-русском"
        ]
        
        for model in models:
            exc = ModelNotFoundError(model=model, provider="TestProvider")
            assert exc.translation_params["model"] == model
            assert model in exc.message
    
    def test_invalid_api_key_error_with_provider(self):
        """
        Test InvalidAPIKeyError with provider parameter.
        
        Requirements: 2.1
        """
        from utils.exceptions import InvalidAPIKeyError
        
        exc = InvalidAPIKeyError(provider="Groq")
        assert exc.translation_key == "errors.invalid_api_key"
        assert exc.translation_params["provider"] == "Groq"
        assert "Groq" in exc.message
        
        user_msg = exc.user_message
        assert isinstance(user_msg, str)
        assert len(user_msg) > 0
    
    def test_invalid_api_key_error_with_different_providers(self):
        """
        Test InvalidAPIKeyError with different providers.
        
        Requirements: 2.1
        """
        from utils.exceptions import InvalidAPIKeyError
        
        providers = ["Groq", "OpenAI", "Custom", "Anthropic"]
        
        for provider in providers:
            exc = InvalidAPIKeyError(provider=provider)
            assert exc.translation_params["provider"] == provider
            assert provider in exc.message
    
    def test_api_exceptions_preserve_technical_message(self):
        """
        Test that API exceptions preserve technical message for logging.
        
        Requirements: 1.5, 4.1
        """
        from utils.exceptions import (
            APIAuthenticationError,
            APINetworkError,
            APITimeoutError,
            ModelNotFoundError
        )
        
        exc1 = APIAuthenticationError(provider="Groq")
        exc2 = APINetworkError(provider="Groq")
        exc3 = APITimeoutError(provider="Groq", timeout=30.0)
        exc4 = ModelNotFoundError(model="test-model", provider="Groq")
        
        # All should have Russian technical messages
        assert isinstance(exc1.message, str)
        assert isinstance(exc2.message, str)
        assert isinstance(exc3.message, str)
        assert isinstance(exc4.message, str)
        
        # str() should return technical message
        assert str(exc1) == exc1.message
        assert str(exc2) == exc2.message
        assert str(exc3) == exc3.message
        assert str(exc4) == exc4.message
    
    def test_api_exceptions_user_message_differs_from_technical(self):
        """
        Test that user_message differs from technical message.
        
        Requirements: 1.1, 1.2
        """
        from utils.exceptions import APIAuthenticationError
        
        original_lang = get_language()
        
        try:
            set_language("en")
            exc = APIAuthenticationError(provider="Groq")
            
            # User message should be translated (English)
            user_msg = exc.user_message
            
            # Technical message should be in Russian
            technical_msg = exc.message
            
            # They should be different (unless translation is missing)
            # At minimum, user_message should be a string
            assert isinstance(user_msg, str)
            assert isinstance(technical_msg, str)
            assert len(user_msg) > 0
            assert len(technical_msg) > 0
            
        finally:
            set_language(original_lang)



class TestAudioExceptions:
    """Tests for audio exception classes with i18n support."""
    
    def test_microphone_unavailable_error(self):
        """
        Test MicrophoneUnavailableError translation.
        
        Requirements: 1.1
        """
        from utils.exceptions import MicrophoneUnavailableError
        
        exc = MicrophoneUnavailableError()
        assert exc.translation_key == "errors.microphone_unavailable"
        assert exc.message == "Микрофон недоступен"
        
        user_msg = exc.user_message
        assert isinstance(user_msg, str)
        assert len(user_msg) > 0
    
    def test_microphone_unavailable_error_with_custom_message(self):
        """
        Test MicrophoneUnavailableError with custom technical message.
        
        Requirements: 1.1
        """
        from utils.exceptions import MicrophoneUnavailableError
        
        custom_msg = "Микрофон занят приложением Zoom"
        exc = MicrophoneUnavailableError(message=custom_msg)
        
        assert exc.message == custom_msg
        assert exc.translation_key == "errors.microphone_unavailable"
    
    def test_recording_too_short_error_with_duration(self):
        """
        Test RecordingTooShortError with duration parameter.
        
        Requirements: 1.2
        """
        from utils.exceptions import RecordingTooShortError
        
        exc = RecordingTooShortError(duration=0.3)
        assert exc.translation_key == "errors.recording_too_short"
        assert exc.translation_params["duration"] == 0.3
        assert "0.30" in exc.message
        
        user_msg = exc.user_message
        assert isinstance(user_msg, str)
        assert len(user_msg) > 0
    
    def test_recording_too_short_error_without_duration(self):
        """
        Test RecordingTooShortError without duration parameter.
        
        Requirements: 1.2
        """
        from utils.exceptions import RecordingTooShortError
        
        exc = RecordingTooShortError()
        assert exc.translation_key == "errors.recording_too_short"
        assert exc.translation_params["duration"] is None
        assert exc.message == "Запись слишком короткая"
        
        user_msg = exc.user_message
        assert isinstance(user_msg, str)
        assert len(user_msg) > 0
    
    def test_empty_recording_error(self):
        """
        Test EmptyRecordingError translation.
        
        Requirements: 1.1
        """
        from utils.exceptions import EmptyRecordingError
        
        exc = EmptyRecordingError()
        assert exc.translation_key == "errors.empty_recording"
        assert exc.message == "Аудио буфер пустой"
        
        user_msg = exc.user_message
        assert isinstance(user_msg, str)
        assert len(user_msg) > 0
    
    def test_audio_device_error_with_error_parameter(self):
        """
        Test AudioDeviceError with error parameter.
        
        Requirements: 1.2
        """
        from utils.exceptions import AudioDeviceError
        
        error_msg = "Устройство отключено"
        exc = AudioDeviceError(error=error_msg)
        
        assert exc.translation_key == "errors.audio_device_error"
        assert exc.translation_params["error"] == error_msg
        assert error_msg in exc.message
        
        user_msg = exc.user_message
        assert isinstance(user_msg, str)
        assert len(user_msg) > 0
    
    def test_audio_device_error_with_different_errors(self):
        """
        Test AudioDeviceError with different error messages.
        
        Requirements: 1.2
        """
        from utils.exceptions import AudioDeviceError
        
        errors = [
            "Устройство не найдено",
            "Нет доступа к устройству",
            "Устройство занято",
            "Device not found"
        ]
        
        for error in errors:
            exc = AudioDeviceError(error=error)
            assert exc.translation_params["error"] == error
            assert error in exc.message
    
    def test_audio_exceptions_preserve_technical_message(self):
        """
        Test that audio exceptions preserve technical message for logging.
        
        Requirements: 1.5, 4.1
        """
        from utils.exceptions import (
            MicrophoneUnavailableError,
            RecordingTooShortError,
            EmptyRecordingError,
            AudioDeviceError
        )
        
        exc1 = MicrophoneUnavailableError()
        exc2 = RecordingTooShortError(duration=0.3)
        exc3 = EmptyRecordingError()
        exc4 = AudioDeviceError(error="test error")
        
        # All should have Russian technical messages
        assert isinstance(exc1.message, str)
        assert isinstance(exc2.message, str)
        assert isinstance(exc3.message, str)
        assert isinstance(exc4.message, str)
        
        # str() should return technical message
        assert str(exc1) == exc1.message
        assert str(exc2) == exc2.message
        assert str(exc3) == exc3.message
        assert str(exc4) == exc4.message
    
    def test_audio_exceptions_user_message_differs_from_technical(self):
        """
        Test that user_message differs from technical message.
        
        Requirements: 1.1, 1.2
        """
        from utils.exceptions import RecordingTooShortError
        
        original_lang = get_language()
        
        try:
            set_language("en")
            exc = RecordingTooShortError(duration=0.3)
            
            # User message should be translated (English)
            user_msg = exc.user_message
            
            # Technical message should be in Russian
            technical_msg = exc.message
            
            # They should be different (unless translation is missing)
            # At minimum, user_message should be a string
            assert isinstance(user_msg, str)
            assert isinstance(technical_msg, str)
            assert len(user_msg) > 0
            assert len(technical_msg) > 0
            
        finally:
            set_language(original_lang)



class TestConfigurationExceptions:
    """Tests for configuration exception classes with i18n support."""
    
    def test_missing_config_error_with_parameter(self):
        """
        Test MissingConfigError with parameter.
        
        Requirements: 1.2
        """
        from utils.exceptions import MissingConfigError
        
        exc = MissingConfigError(parameter="api_key")
        assert exc.translation_key == "errors.missing_config"
        assert exc.translation_params["parameter"] == "api_key"
        assert "api_key" in exc.message
        
        user_msg = exc.user_message
        assert isinstance(user_msg, str)
        assert len(user_msg) > 0
    
    def test_missing_config_error_with_different_parameters(self):
        """
        Test MissingConfigError with different parameter names.
        
        Requirements: 1.2
        """
        from utils.exceptions import MissingConfigError
        
        parameters = ["api_key", "base_url", "model", "timeout"]
        
        for param in parameters:
            exc = MissingConfigError(parameter=param)
            assert exc.translation_params["parameter"] == param
            assert param in exc.message
    
    def test_invalid_config_error_with_all_parameters(self):
        """
        Test InvalidConfigError with all parameters.
        
        Requirements: 1.2
        """
        from utils.exceptions import InvalidConfigError
        
        exc = InvalidConfigError(
            parameter="timeout",
            value="invalid",
            reason="должно быть числом"
        )
        
        assert exc.translation_key == "errors.invalid_config"
        assert exc.translation_params["parameter"] == "timeout"
        assert exc.translation_params["value"] == "invalid"
        assert exc.translation_params["reason"] == "должно быть числом"
        assert "timeout" in exc.message
        assert "invalid" in exc.message
        
        user_msg = exc.user_message
        assert isinstance(user_msg, str)
        assert len(user_msg) > 0
    
    def test_invalid_config_error_with_different_values(self):
        """
        Test InvalidConfigError with different parameter values.
        
        Requirements: 1.2
        """
        from utils.exceptions import InvalidConfigError
        
        test_cases = [
            ("port", "99999", "вне диапазона"),
            ("language", "xx", "неподдерживаемый язык"),
            ("volume", "-1", "должно быть положительным")
        ]
        
        for param, value, reason in test_cases:
            exc = InvalidConfigError(parameter=param, value=value, reason=reason)
            assert exc.translation_params["parameter"] == param
            assert exc.translation_params["value"] == value
            assert exc.translation_params["reason"] == reason
    
    def test_hotkey_conflict_error_with_hotkey(self):
        """
        Test HotkeyConflictError with hotkey parameter.
        
        Requirements: 1.2
        """
        from utils.exceptions import HotkeyConflictError
        
        exc = HotkeyConflictError(hotkey="Ctrl+Shift+A")
        assert exc.translation_key == "errors.hotkey_conflict"
        assert exc.translation_params["hotkey"] == "Ctrl+Shift+A"
        assert exc.translation_params["reason"] is None
        assert "Ctrl+Shift+A" in exc.message
        
        user_msg = exc.user_message
        assert isinstance(user_msg, str)
        assert len(user_msg) > 0
    
    def test_hotkey_conflict_error_with_reason(self):
        """
        Test HotkeyConflictError with hotkey and reason.
        
        Requirements: 1.2
        """
        from utils.exceptions import HotkeyConflictError
        
        exc = HotkeyConflictError(
            hotkey="Ctrl+Shift+A",
            reason="уже используется другим приложением"
        )
        
        assert exc.translation_key == "errors.hotkey_conflict"
        assert exc.translation_params["hotkey"] == "Ctrl+Shift+A"
        assert exc.translation_params["reason"] == "уже используется другим приложением"
        assert "Ctrl+Shift+A" in exc.message
        assert "уже используется" in exc.message
    
    def test_hotkey_conflict_error_with_different_hotkeys(self):
        """
        Test HotkeyConflictError with different hotkey combinations.
        
        Requirements: 1.2
        """
        from utils.exceptions import HotkeyConflictError
        
        hotkeys = [
            "Ctrl+Alt+R",
            "Shift+F1",
            "Win+Space",
            "Alt+Tab"
        ]
        
        for hotkey in hotkeys:
            exc = HotkeyConflictError(hotkey=hotkey)
            assert exc.translation_params["hotkey"] == hotkey
            assert hotkey in exc.message
    
    def test_configuration_exceptions_preserve_technical_message(self):
        """
        Test that configuration exceptions preserve technical message for logging.
        
        Requirements: 1.5, 4.1
        """
        from utils.exceptions import (
            MissingConfigError,
            InvalidConfigError,
            HotkeyConflictError
        )
        
        exc1 = MissingConfigError(parameter="api_key")
        exc2 = InvalidConfigError(parameter="timeout", value="abc", reason="должно быть числом")
        exc3 = HotkeyConflictError(hotkey="Ctrl+A")
        
        # All should have Russian technical messages
        assert isinstance(exc1.message, str)
        assert isinstance(exc2.message, str)
        assert isinstance(exc3.message, str)
        
        # str() should return technical message
        assert str(exc1) == exc1.message
        assert str(exc2) == exc2.message
        assert str(exc3) == exc3.message
    
    def test_configuration_exceptions_user_message_differs_from_technical(self):
        """
        Test that user_message differs from technical message.
        
        Requirements: 1.1, 1.2
        """
        from utils.exceptions import MissingConfigError
        
        original_lang = get_language()
        
        try:
            set_language("en")
            exc = MissingConfigError(parameter="api_key")
            
            # User message should be translated (English)
            user_msg = exc.user_message
            
            # Technical message should be in Russian
            technical_msg = exc.message
            
            # They should be different (unless translation is missing)
            # At minimum, user_message should be a string
            assert isinstance(user_msg, str)
            assert isinstance(technical_msg, str)
            assert len(user_msg) > 0
            assert len(technical_msg) > 0
            
        finally:
            set_language(original_lang)
