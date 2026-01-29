"""
Тесты для иерархии исключений RapidWhisper.

Проверяет корректность создания, наследования и обработки всех
пользовательских исключений приложения.
"""

import pytest
from utils.exceptions import (
    # Базовое исключение
    RapidWhisperError,
    # Аудио ошибки
    AudioError,
    MicrophoneUnavailableError,
    RecordingTooShortError,
    EmptyRecordingError,
    AudioDeviceError,
    # API ошибки
    APIError,
    AuthenticationError,
    APIConnectionError,
    APITimeoutError,
    APIResponseError,
    # Ошибки конфигурации
    ConfigurationError,
    MissingConfigError,
    InvalidConfigError,
    HotkeyConflictError,
    # Вспомогательные функции
    get_user_friendly_message,
    is_recoverable_error,
)


# ============================================================================
# Тесты базового исключения
# ============================================================================

class TestRapidWhisperError:
    """Тесты для базового класса RapidWhisperError."""
    
    def test_basic_error_creation(self):
        """Тест создания базового исключения с сообщением."""
        error = RapidWhisperError("Test error message")
        
        assert error.message == "Test error message"
        assert error.user_message == "Test error message"
        assert str(error) == "Test error message"
    
    def test_error_with_user_message(self):
        """Тест создания исключения с отдельным пользовательским сообщением."""
        error = RapidWhisperError(
            message="Technical error: connection failed",
            user_message="Проблема с подключением"
        )
        
        assert error.message == "Technical error: connection failed"
        assert error.user_message == "Проблема с подключением"
    
    def test_error_is_exception(self):
        """Тест что RapidWhisperError является Exception."""
        error = RapidWhisperError("test")
        assert isinstance(error, Exception)
    
    def test_error_can_be_raised(self):
        """Тест что исключение можно выбросить и поймать."""
        with pytest.raises(RapidWhisperError) as exc_info:
            raise RapidWhisperError("test error")
        
        assert exc_info.value.message == "test error"


# ============================================================================
# Тесты аудио ошибок
# ============================================================================

class TestAudioErrors:
    """Тесты для ошибок аудио подсистемы."""
    
    def test_audio_error_inheritance(self):
        """Тест что AudioError наследуется от RapidWhisperError."""
        error = AudioError("test")
        assert isinstance(error, RapidWhisperError)
        assert isinstance(error, AudioError)
    
    def test_microphone_unavailable_error(self):
        """Тест исключения недоступного микрофона."""
        error = MicrophoneUnavailableError()
        
        assert isinstance(error, AudioError)
        assert "Микрофон недоступен" in error.message
        assert "Микрофон занят" in error.user_message
    
    def test_microphone_unavailable_custom_message(self):
        """Тест исключения недоступного микрофона с кастомным сообщением."""
        error = MicrophoneUnavailableError("Device not found")
        
        assert error.message == "Device not found"
        assert "Микрофон занят" in error.user_message
    
    def test_recording_too_short_error(self):
        """Тест исключения слишком короткой записи."""
        error = RecordingTooShortError()
        
        assert isinstance(error, AudioError)
        assert "слишком короткая" in error.message.lower()
        assert "попробуйте еще раз" in error.user_message
    
    def test_recording_too_short_with_duration(self):
        """Тест исключения слишком короткой записи с указанием длительности."""
        error = RecordingTooShortError(duration=0.3)
        
        assert "0.30" in error.message or "0.3" in error.message
        assert "секунд" in error.message
    
    def test_empty_recording_error(self):
        """Тест исключения пустой записи."""
        error = EmptyRecordingError()
        
        assert isinstance(error, AudioError)
        assert "пустой" in error.message.lower()
        assert "Не удалось записать" in error.user_message
    
    def test_audio_device_error(self):
        """Тест общей ошибки аудио устройства."""
        error = AudioDeviceError("Sample rate not supported")
        
        assert isinstance(error, AudioError)
        assert "Sample rate not supported" in error.message
        assert "аудио устройством" in error.user_message


# ============================================================================
# Тесты API ошибок
# ============================================================================

class TestAPIErrors:
    """Тесты для ошибок API."""
    
    def test_api_error_inheritance(self):
        """Тест что APIError наследуется от RapidWhisperError."""
        error = APIError("API error")
        assert isinstance(error, RapidWhisperError)
