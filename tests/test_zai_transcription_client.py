"""
Unit-тесты для Z.AI провайдера в TranscriptionClient.

Проверяет функциональность Z.AI провайдера:
- Инициализация с Anthropic SDK
- Постобработка текста через Anthropic API
- Обработка ошибок Anthropic SDK
- Проверка что транскрипция аудио не поддерживается
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from services.transcription_client import TranscriptionClient
from utils.exceptions import (
    InvalidAPIKeyError,
    MissingConfigError,
    APIAuthenticationError,
    APINetworkError,
    APITimeoutError as CustomAPITimeoutError
)


class TestZAIClientInitialization:
    """Тесты инициализации TranscriptionClient с провайдером Z.AI."""
    
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_initialization_with_zai_provider(self, mock_anthropic):
        """
        Тест инициализации с провайдером Z.AI.
        
        Validates: Requirements 1.1, 1.2, 2.1
        """
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        
        client = TranscriptionClient(provider="zai", api_key="test_glm_key")
        
        assert client.provider == "zai"
        assert client.base_url == "https://api.z.ai/api/anthropic"
        assert client.model == "GLM-4.7"
        assert client.timeout == 130.0
        assert client.anthropic_client == mock_client
        assert client.client is None  # OpenAI client не создается для Z.AI
        
        # Проверяем что Anthropic клиент создан с правильными параметрами
        mock_anthropic.assert_called_once_with(
            api_key="test_glm_key",
            base_url="https://api.z.ai/api/anthropic",
            timeout=130.0
        )
    
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_initialization_with_custom_model(self, mock_anthropic):
        """
        Тест инициализации с кастомной моделью.
        
        Validates: Requirements 1.3
        """
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        
        client = TranscriptionClient(
            provider="zai", 
            api_key="test_key",
            model="GLM-4-Plus"
        )
        
        assert client.model == "GLM-4-Plus"
    
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', False)
    def test_initialization_without_anthropic_sdk(self):
        """
        Тест инициализации когда Anthropic SDK не установлен.
        
        Validates: Requirements 2.3
        """
        with pytest.raises(MissingConfigError) as exc_info:
            TranscriptionClient(provider="zai", api_key="test_key")
        
        # Проверяем что параметр содержит информацию об anthropic SDK
        assert "anthropic" in exc_info.value.message.lower()
    
    def test_initialization_without_api_key(self):
        """
        Тест инициализации без API ключа.
        
        Validates: Requirements 1.2
        """
        with pytest.raises(InvalidAPIKeyError):
            TranscriptionClient(provider="zai", api_key=None)
    
    def test_initialization_with_empty_api_key(self):
        """
        Тест инициализации с пустым API ключом.
        
        Validates: Requirements 1.2
        """
        with pytest.raises(InvalidAPIKeyError):
            TranscriptionClient(provider="zai", api_key="")


class TestZAIClientTranscribeAudio:
    """Тесты метода transcribe_audio для Z.AI провайдера."""
    
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_transcribe_audio_raises_not_implemented(self, mock_anthropic):
        """
        Тест что transcribe_audio выбрасывает NotImplementedError для Z.AI.
        
        Z.AI не поддерживает транскрипцию аудио, только постобработку текста.
        
        Validates: Requirements 4.1, 4.2
        """
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        
        client = TranscriptionClient(provider="zai", api_key="test_key")
        
        with pytest.raises(NotImplementedError) as exc_info:
            client.transcribe_audio("test_audio.wav")
        
        error_message = str(exc_info.value)
        assert "не поддерживает транскрипцию аудио" in error_message.lower()
        assert "постобработки текста" in error_message.lower()


class TestZAIClientPostProcessText:
    """Тесты метода post_process_text для Z.AI провайдера."""
    
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_post_process_text_success(self, mock_anthropic):
        """
        Тест успешной постобработки текста через Z.AI.
        
        Validates: Requirements 2.2, 3.3, 3.4, 9.1, 9.2, 9.4
        """
        # Настроить mock для Anthropic клиента
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Обработанный текст с пунктуацией."
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        # Создать TranscriptionClient (не используется для постобработки)
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Выполнить постобработку через Z.AI
        result = client.post_process_text(
            text="исходный текст без пунктуации",
            provider="zai",
            model="GLM-4.7",
            system_prompt="Добавь пунктуацию",
            api_key="test_glm_key",
            temperature=0.3
        )
        
        assert result == "Обработанный текст с пунктуацией."
        
        # Проверяем что Anthropic API вызван с правильными параметрами
        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs['model'] == "GLM-4.7"
        assert call_kwargs['max_tokens'] == 2000
        assert call_kwargs['temperature'] == 0.3
        assert call_kwargs['system'] == "Добавь пунктуацию"
        assert call_kwargs['messages'] == [
            {"role": "user", "content": "исходный текст без пунктуации"}
        ]
    
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_post_process_text_extracts_from_content(self, mock_anthropic):
        """
        Тест извлечения текста из response.content[0].text.
        
        Validates: Requirements 3.4, 9.2, 9.4
        """
        # Настроить mock с правильной структурой Anthropic response
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Извлеченный текст"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        result = client.post_process_text(
            text="тест",
            provider="zai",
            model="GLM-4.7",
            system_prompt="промпт",
            api_key="test_key"
        )
        
        assert result == "Извлеченный текст"
    
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_post_process_text_empty_response_returns_original(self, mock_anthropic):
        """
        Тест что пустой ответ возвращает оригинальный текст.
        
        Validates: Requirements 9.3
        """
        # Настроить mock с пустым ответом
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = []
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        original_text = "оригинальный текст"
        result = client.post_process_text(
            text=original_text,
            provider="zai",
            model="GLM-4.7",
            system_prompt="промпт",
            api_key="test_key"
        )
        
        assert result == original_text


class TestZAIClientErrorHandling:
    """Тесты обработки ошибок Anthropic SDK."""
    
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_post_process_text_authentication_error(self, mock_anthropic):
        """
        Тест обработки ошибки аутентификации Anthropic.
        
        Validates: Requirements 6.2, 6.3, 9.3
        """
        from services.transcription_client import AnthropicAuthenticationError
        
        # Создать mock response и body для Anthropic исключения
        mock_response = Mock()
        mock_response.status_code = 401
        mock_body = {"error": {"message": "Invalid API key"}}
        
        # Настроить mock для выброса AnthropicAuthenticationError
        mock_client = Mock()
        anthropic_error = AnthropicAuthenticationError(
            message="Invalid API key",
            response=mock_response,
            body=mock_body
        )
        mock_client.messages.create.side_effect = anthropic_error
        mock_anthropic.return_value = mock_client
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Должен пробросить Anthropic исключение как есть
        with pytest.raises(AnthropicAuthenticationError):
            client.post_process_text(
                text="тест",
                provider="zai",
                model="GLM-4.7",
                system_prompt="промпт",
                api_key="invalid_key"
            )
    
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_post_process_text_timeout_error(self, mock_anthropic):
        """
        Тест обработки таймаута Anthropic.
        
        Validates: Requirements 6.4, 9.3
        """
        from services.transcription_client import AnthropicAPITimeoutError
        
        # Создать mock request для Anthropic исключения
        mock_request = Mock()
        
        # Настроить mock для выброса AnthropicAPITimeoutError
        mock_client = Mock()
        anthropic_error = AnthropicAPITimeoutError(request=mock_request)
        mock_client.messages.create.side_effect = anthropic_error
        mock_anthropic.return_value = mock_client
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Должен пробросить Anthropic исключение как есть
        with pytest.raises(AnthropicAPITimeoutError):
            client.post_process_text(
                text="тест",
                provider="zai",
                model="GLM-4.7",
                system_prompt="промпт",
                api_key="test_key"
            )
    
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_post_process_text_connection_error(self, mock_anthropic):
        """
        Тест обработки ошибки подключения Anthropic.
        
        Validates: Requirements 6.3, 9.3
        """
        from services.transcription_client import AnthropicAPIConnectionError
        
        # Создать mock request для Anthropic исключения
        mock_request = Mock()
        
        # Настроить mock для выброса AnthropicAPIConnectionError
        mock_client = Mock()
        anthropic_error = AnthropicAPIConnectionError(request=mock_request)
        mock_client.messages.create.side_effect = anthropic_error
        mock_anthropic.return_value = mock_client
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Должен пробросить Anthropic исключение как есть
        with pytest.raises(AnthropicAPIConnectionError):
            client.post_process_text(
                text="тест",
                provider="zai",
                model="GLM-4.7",
                system_prompt="промпт",
                api_key="test_key"
            )
    
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_post_process_text_not_found_error(self, mock_anthropic):
        """
        Тест обработки ошибки "модель не найдена" Anthropic.
        
        Validates: Requirements 6.2, 9.3
        """
        from services.transcription_client import AnthropicNotFoundError
        
        # Создать mock response и body для Anthropic исключения
        mock_response = Mock()
        mock_response.status_code = 404
        mock_body = {"error": {"message": "Model not found"}}
        
        # Настроить mock для выброса AnthropicNotFoundError
        mock_client = Mock()
        anthropic_error = AnthropicNotFoundError(
            message="Model not found",
            response=mock_response,
            body=mock_body
        )
        mock_client.messages.create.side_effect = anthropic_error
        mock_anthropic.return_value = mock_client
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Должен пробросить Anthropic исключение как есть
        with pytest.raises(AnthropicNotFoundError):
            client.post_process_text(
                text="тест",
                provider="zai",
                model="invalid-model",
                system_prompt="промпт",
                api_key="test_key"
            )
    
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_post_process_text_bad_request_returns_original(self, mock_anthropic):
        """
        Тест что BadRequestError возвращает оригинальный текст.
        
        Validates: Requirements 6.4, 9.3
        """
        from services.transcription_client import AnthropicBadRequestError
        
        # Создать mock response и body для Anthropic исключения
        mock_response = Mock()
        mock_response.status_code = 400
        mock_body = {"error": {"message": "Bad request"}}
        
        # Настроить mock для выброса AnthropicBadRequestError
        mock_client = Mock()
        anthropic_error = AnthropicBadRequestError(
            message="Bad request",
            response=mock_response,
            body=mock_body
        )
        mock_client.messages.create.side_effect = anthropic_error
        mock_anthropic.return_value = mock_client
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        original_text = "оригинальный текст"
        result = client.post_process_text(
            text=original_text,
            provider="zai",
            model="GLM-4.7",
            system_prompt="промпт",
            api_key="test_key"
        )
        
        # Должен вернуть оригинальный текст вместо выброса исключения
        assert result == original_text
    
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_post_process_text_rate_limit_error(self, mock_anthropic):
        """
        Тест обработки ошибки превышения лимита Anthropic.
        
        Validates: Requirements 6.2, 9.3
        """
        from services.transcription_client import AnthropicRateLimitError
        
        # Создать mock response и body для Anthropic исключения
        mock_response = Mock()
        mock_response.status_code = 429
        mock_body = {"error": {"message": "Rate limit exceeded"}}
        
        # Настроить mock для выброса AnthropicRateLimitError
        mock_client = Mock()
        anthropic_error = AnthropicRateLimitError(
            message="Rate limit exceeded",
            response=mock_response,
            body=mock_body
        )
        mock_client.messages.create.side_effect = anthropic_error
        mock_anthropic.return_value = mock_client
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Должен пробросить Anthropic исключение как есть
        with pytest.raises(AnthropicRateLimitError):
            client.post_process_text(
                text="тест",
                provider="zai",
                model="GLM-4.7",
                system_prompt="промпт",
                api_key="test_key"
            )
