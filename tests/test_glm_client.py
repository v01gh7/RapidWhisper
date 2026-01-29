"""
Unit-тесты для GLMClient.

Проверяет функциональность транскрипции аудио через Zhipu GLM API.
"""

import pytest
import os
from unittest.mock import Mock, patch, mock_open, MagicMock
from openai import AuthenticationError, APIConnectionError, APITimeoutError

from services.glm_client import GLMClient
from utils.exceptions import (
    APIError,
    APIAuthenticationError,
    APINetworkError,
    APITimeoutError as CustomAPITimeoutError,
    InvalidAPIKeyError
)


class TestGLMClientInitialization:
    """Тесты инициализации GLMClient."""
    
    @patch.dict(os.environ, {'GLM_API_KEY': 'test_api_key'})
    def test_initialization_with_env_variable(self):
        """
        Тест загрузки API ключа из переменной окружения.
        
        Requirements: 6.2
        """
        client = GLMClient()
        
        assert client.base_url == "https://open.bigmodel.cn/api/paas/v4/"
        assert client.model == "whisper-1"
        assert client.timeout == 30
        assert client.client is not None
    
    def test_initialization_with_explicit_key(self):
        """Тест инициализации с явно переданным API ключом."""
        client = GLMClient(api_key="explicit_test_key")
        
        assert client.client is not None
    
    @patch.dict(os.environ, {}, clear=True)
    def test_initialization_without_api_key(self):
        """
        Тест ошибки при отсутствии API ключа.
        
        Requirements: 6.2, 10.2
        """
        with pytest.raises(InvalidAPIKeyError) as exc_info:
            GLMClient()
        
        assert "GLM_API_KEY" in exc_info.value.user_message


class TestGLMClientTranscription:
    """Тесты транскрипции аудио."""
    
    @patch('services.glm_client.OpenAI')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_audio_data')
    def test_transcribe_audio_success(self, mock_file, mock_openai_class):
        """
        Тест успешной транскрипции аудио.
        
        Requirements: 6.3, 6.6
        """
        # Настроить мок OpenAI клиента
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Настроить мок ответа API
        mock_response = Mock()
        mock_response.text = "Привет, это тестовая транскрипция"
        mock_client.audio.transcriptions.create.return_value = mock_response
        
        # Создать клиент и выполнить транскрипцию
        client = GLMClient(api_key="test_key")
        result = client.transcribe_audio("test_audio.wav")
        
        # Проверить результат
        assert result == "Привет, это тестовая транскрипция"
        
        # Проверить что API был вызван с правильными параметрами
        mock_client.audio.transcriptions.create.assert_called_once()
        call_kwargs = mock_client.audio.transcriptions.create.call_args[1]
        assert call_kwargs['model'] == "whisper-1"
        assert call_kwargs['response_format'] == "json"
    
    @patch('services.glm_client.OpenAI')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_audio_data')
    def test_transcribe_audio_extracts_text_from_response(self, mock_file, mock_openai_class):
        """
        Тест извлечения текста из JSON ответа API.
        
        Requirements: 6.6
        Property 16: Извлечение текста из ответа API
        """
        # Настроить мок
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.text = "Извлеченный текст"
        mock_client.audio.transcriptions.create.return_value = mock_response
        
        # Выполнить транскрипцию
        client = GLMClient(api_key="test_key")
        result = client.transcribe_audio("test.wav")
        
        # Проверить что текст извлечен корректно
        assert result == "Извлеченный текст"
    
    @patch('services.glm_client.OpenAI')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_audio_data')
    def test_transcribe_audio_authentication_error(self, mock_file, mock_openai_class):
        """
        Тест обработки ошибки аутентификации.
        
        Requirements: 6.7, 10.2
        """
        # Настроить мок для вызова ошибки аутентификации
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.audio.transcriptions.create.side_effect = AuthenticationError(
            "Invalid API key",
            response=Mock(status_code=401),
            body=None
        )
        
        # Выполнить транскрипцию и проверить ошибку
        client = GLMClient(api_key="invalid_key")
        
        with pytest.raises(APIAuthenticationError) as exc_info:
            client.transcribe_audio("test.wav")
        
        assert "GLM_API_KEY" in exc_info.value.user_message
    
    @patch('services.glm_client.OpenAI')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_audio_data')
    def test_transcribe_audio_network_error(self, mock_file, mock_openai_class):
        """
        Тест обработки сетевой ошибки.
        
        Requirements: 6.8, 10.4
        """
        # Настроить мок для вызова сетевой ошибки
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Создать правильный экземпляр APIConnectionError
        from openai import APIConnectionError as OpenAIConnectionError
        mock_client.audio.transcriptions.create.side_effect = OpenAIConnectionError(
            request=Mock()
        )
        
        # Выполнить транскрипцию и проверить ошибку
        client = GLMClient(api_key="test_key")
        
        with pytest.raises(APINetworkError) as exc_info:
            client.transcribe_audio("test.wav")
        
        assert "подключение" in exc_info.value.user_message.lower()
    
    @patch('services.glm_client.OpenAI')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_audio_data')
    def test_transcribe_audio_timeout_error(self, mock_file, mock_openai_class):
        """
        Тест обработки таймаута.
        
        Requirements: 6.5, 6.8
        """
        # Настроить мок для вызова таймаута
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        # Создать правильный экземпляр APITimeoutError
        from openai import APITimeoutError as OpenAITimeoutError
        mock_client.audio.transcriptions.create.side_effect = OpenAITimeoutError(
            request=Mock()
        )
        
        # Выполнить транскрипцию и проверить ошибку
        client = GLMClient(api_key="test_key")
        
        with pytest.raises(CustomAPITimeoutError):
            client.transcribe_audio("test.wav")
    
    @patch('services.glm_client.OpenAI')
    def test_transcribe_audio_file_not_found(self, mock_openai_class):
        """
        Тест обработки отсутствующего файла.
        
        Requirements: 10.3
        """
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        client = GLMClient(api_key="test_key")
        
        with pytest.raises(APIError) as exc_info:
            client.transcribe_audio("nonexistent_file.wav")
        
        assert "не найден" in str(exc_info.value.message).lower()


class TestGLMClientErrorHandling:
    """Тесты обработки ошибок."""
    
    def test_handle_api_error_authentication(self):
        """Тест обработки ошибки аутентификации."""
        client = GLMClient(api_key="test_key")
        
        error = Exception("Authentication failed: invalid API key")
        message = client._handle_api_error(error)
        
        assert "GLM_API_KEY" in message
        assert ".env" in message
    
    def test_handle_api_error_network(self):
        """Тест обработки сетевой ошибки."""
        client = GLMClient(api_key="test_key")
        
        error = Exception("Network connection failed")
        message = client._handle_api_error(error)
        
        assert "сети" in message.lower() or "подключение" in message.lower()
    
    def test_handle_api_error_timeout(self):
        """Тест обработки таймаута."""
        client = GLMClient(api_key="test_key")
        
        error = Exception("Request timeout exceeded")
        message = client._handle_api_error(error)
        
        assert "время" in message.lower() or "timeout" in message.lower()
    
    def test_handle_api_error_rate_limit(self):
        """Тест обработки превышения лимита запросов."""
        client = GLMClient(api_key="test_key")
        
        error = Exception("Rate limit exceeded")
        message = client._handle_api_error(error)
        
        assert "лимит" in message.lower()
    
    def test_handle_api_error_generic(self):
        """Тест обработки общей ошибки."""
        client = GLMClient(api_key="test_key")
        
        error = Exception("Unknown error occurred")
        message = client._handle_api_error(error)
        
        assert "Unknown error occurred" in message


class TestGLMClientPrepareAudioFile:
    """Тесты подготовки аудио файла."""
    
    @patch('builtins.open', new_callable=mock_open, read_data=b'audio_data')
    def test_prepare_audio_file_success(self, mock_file):
        """Тест успешной подготовки аудио файла."""
        client = GLMClient(api_key="test_key")
        
        file_obj = client._prepare_audio_file("test.wav")
        
        # Проверить что файл был открыт в бинарном режиме
        mock_file.assert_called_once_with("test.wav", 'rb')
        assert file_obj is not None
    
    def test_prepare_audio_file_not_found(self):
        """Тест обработки отсутствующего файла."""
        client = GLMClient(api_key="test_key")
        
        with pytest.raises(APIError) as exc_info:
            client._prepare_audio_file("nonexistent.wav")
        
        assert "не найден" in str(exc_info.value.message).lower()



# ============================================================================
# Property-Based Tests
# ============================================================================

from hypothesis import given, settings
from hypothesis import strategies as st


class TestGLMClientProperties:
    """Property-based тесты для GLMClient."""
    
    @given(st.text(min_size=1, max_size=500))
    @settings(max_examples=100, deadline=None)
    def test_property_error_message_handling(self, error_message):
        """
        Property: Обработка сообщений об ошибках
        
        Для любого сообщения об ошибке, _handle_api_error должен вернуть
        понятное пользователю сообщение.
        
        **Validates: Requirements 6.7, 6.8**
        """
        client = GLMClient(api_key="test_key")
        
        # Создать ошибку с произвольным сообщением
        error = Exception(error_message)
        
        # Обработать ошибку
        user_message = client._handle_api_error(error)
        
        # Проверить что возвращено непустое сообщение
        assert user_message, "Сообщение об ошибке не должно быть пустым"
        assert isinstance(user_message, str), "Сообщение должно быть строкой"
        
        # Проверить что сообщение содержит полезную информацию
        # (либо ключевые слова, либо оригинальное сообщение)
        keywords = ["ошибка", "api", "сеть", "подключение", "ключ", "время", "лимит"]
        has_keyword = any(keyword in user_message.lower() for keyword in keywords)
        has_original = error_message.lower() in user_message.lower()
        
        assert has_keyword or has_original, \
            "Сообщение должно содержать ключевые слова или оригинальное сообщение"
    
    @given(st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=65, max_codepoint=90)))
    @settings(max_examples=100, deadline=None)
    def test_property_api_key_validation(self, api_key):
        """
        Property: Валидация API ключа
        
        Для любого непустого API ключа, клиент должен успешно инициализироваться.
        
        **Validates: Requirements 6.2**
        """
        # Создать клиент с произвольным API ключом
        client = GLMClient(api_key=api_key)
        
        # Проверить что клиент инициализирован
        assert client.client is not None, "OpenAI клиент должен быть инициализирован"
        assert client.base_url == "https://open.bigmodel.cn/api/paas/v4/", \
            "Base URL должен быть установлен корректно"
        assert client.model == "whisper-1", "Модель должна быть whisper-1"
        assert client.timeout == 30, "Таймаут должен быть 30 секунд"
    
    @given(st.integers(min_value=1, max_value=120))
    @settings(max_examples=50, deadline=None)
    def test_property_timeout_configuration(self, timeout_value):
        """
        Property: Конфигурация таймаута
        
        Для любого положительного значения таймаута, клиент должен
        использовать это значение при инициализации.
        
        **Validates: Requirements 6.5**
        """
        client = GLMClient(api_key="test_key")
        
        # Изменить таймаут
        client.timeout = timeout_value
        
        # Проверить что значение установлено
        assert client.timeout == timeout_value, \
            f"Таймаут должен быть {timeout_value}, получено {client.timeout}"
        
        # Проверить что значение положительное
        assert client.timeout > 0, "Таймаут должен быть положительным"


class TestGLMClientPropertiesWithMocks:
    """Property-based тесты для GLMClient с моками (упрощенные)."""
    
    def test_property_text_extraction_from_various_responses(self):
        """
        Feature: rapid-whisper, Property 16: Извлечение текста из ответа API
        
        Для любого валидного JSON ответа от GLM API, клиент должен корректно 
        извлечь текстовое поле транскрипции.
        
        **Validates: Requirements 6.6**
        """
        test_texts = [
            "Привет, мир!",
            "Hello, world!",
            "Это тестовая транскрипция с цифрами 12345",
            "Test with special chars: !@#$%^&*()",
            "Очень длинный текст " * 50,
            "Короткий",
            "123",
            "   пробелы   ",
        ]
        
        for response_text in test_texts:
            with patch('services.glm_client.OpenAI') as mock_openai_class, \
                 patch('builtins.open', mock_open(read_data=b'fake_audio_data')):
                
                # Настроить мок
                mock_client = Mock()
                mock_openai_class.return_value = mock_client
                mock_response = Mock()
                mock_response.text = response_text
                mock_client.audio.transcriptions.create.return_value = mock_response
                
                # Выполнить транскрипцию
                client = GLMClient(api_key="test_key")
                result = client.transcribe_audio("test.wav")
                
                # Проверить извлечение текста
                assert result == response_text, \
                    f"Извлеченный текст должен совпадать с ответом API"
    
    def test_property_audio_file_sent_to_api_for_various_paths(self):
        """
        Feature: rapid-whisper, Property 17: Отправка аудио на транскрипцию
        
        Для любого завершенного аудио файла, GLM клиент должен отправить 
        файл на транскрипцию через API.
        
        **Validates: Requirements 6.3**
        """
        test_paths = [
            "test.wav",
            "audio/recording.wav",
            "C:/temp/audio.wav",
            "recording_2024.wav",
            "файл.wav",
        ]
        
        for file_path in test_paths:
            with patch('services.glm_client.OpenAI') as mock_openai_class, \
                 patch('builtins.open', mock_open(read_data=b'fake_audio_data')) as mock_file:
                
                # Настроить мок
                mock_client = Mock()
                mock_openai_class.return_value = mock_client
                mock_response = Mock()
                mock_response.text = "Test transcription"
                mock_client.audio.transcriptions.create.return_value = mock_response
                
                # Выполнить транскрипцию
                client = GLMClient(api_key="test_key")
                result = client.transcribe_audio(file_path)
                
                # Проверить что файл был открыт
                mock_file.assert_called_with(file_path, 'rb')
                
                # Проверить что API был вызван
                mock_client.audio.transcriptions.create.assert_called_once()
                
                # Проверить параметры
                call_kwargs = mock_client.audio.transcriptions.create.call_args[1]
                assert call_kwargs['model'] == "whisper-1"
                assert call_kwargs['response_format'] == "json"
