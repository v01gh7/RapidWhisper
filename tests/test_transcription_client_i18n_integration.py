"""
Integration tests for transcription_client error message internationalization.

Feature: error-messages-i18n
Tests error message translation in transcription flow.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from services.transcription_client import TranscriptionClient
from utils.exceptions import (
    InvalidAPIKeyError,
    MissingConfigError,
    InvalidConfigError,
    APIAuthenticationError,
    APINetworkError,
    APITimeoutError,
    ModelNotFoundError,
    APIResponseError
)
from utils.i18n import set_language, get_language


class TestTranscriptionClientInit:
    """Tests for TranscriptionClient.__init__ error handling."""
    
    def test_init_without_api_key_raises_invalid_api_key_error(self):
        """
        Test that initializing without API key raises InvalidAPIKeyError.
        
        Requirements: 1.1, 1.2, 2.1
        """
        with pytest.raises(InvalidAPIKeyError) as exc_info:
            TranscriptionClient(provider="groq", api_key=None)
        
        exc = exc_info.value
        assert exc.translation_key == "errors.invalid_api_key"
        assert exc.translation_params["provider"] == "groq"
        assert "groq" in exc.message.lower()
    
    def test_init_with_empty_api_key_raises_invalid_api_key_error(self):
        """
        Test that initializing with empty API key raises InvalidAPIKeyError.
        
        Requirements: 1.1, 1.2, 2.1
        """
        with pytest.raises(InvalidAPIKeyError) as exc_info:
            TranscriptionClient(provider="openai", api_key="")
        
        exc = exc_info.value
        assert exc.translation_key == "errors.invalid_api_key"
        assert exc.translation_params["provider"] == "openai"
    
    def test_init_custom_provider_without_base_url_raises_missing_config_error(self):
        """
        Test that custom provider without base_url raises MissingConfigError.
        
        Requirements: 1.2
        """
        with pytest.raises(MissingConfigError) as exc_info:
            TranscriptionClient(
                provider="custom",
                api_key="test_key",
                base_url=None,
                model="test-model"
            )
        
        exc = exc_info.value
        assert exc.translation_key == "errors.missing_config"
        assert "parameter" in exc.translation_params
    
    def test_init_custom_provider_without_model_raises_missing_config_error(self):
        """
        Test that custom provider without model raises MissingConfigError.
        
        Requirements: 1.2
        """
        with pytest.raises(MissingConfigError) as exc_info:
            TranscriptionClient(
                provider="custom",
                api_key="test_key",
                base_url="https://api.example.com",
                model=None
            )
        
        exc = exc_info.value
        assert exc.translation_key == "errors.missing_config"
    
    def test_init_unknown_provider_raises_invalid_config_error(self):
        """
        Test that unknown provider raises InvalidConfigError.
        
        Requirements: 1.2
        """
        with pytest.raises(InvalidConfigError) as exc_info:
            TranscriptionClient(
                provider="unknown_provider",
                api_key="test_key"
            )
        
        exc = exc_info.value
        assert exc.translation_key == "errors.invalid_config"
        assert exc.translation_params["parameter"] == "provider"
        assert exc.translation_params["value"] == "unknown_provider"


class TestTranscriptionClientTranscribeAudio:
    """Tests for TranscriptionClient.transcribe_audio error handling."""
    
    @patch('services.transcription_client.OpenAI')
    def test_transcribe_audio_authentication_error(self, mock_openai):
        """
        Test that authentication error is properly translated.
        
        Requirements: 2.1
        """
        from openai import AuthenticationError
        
        # Create mock response and body for AuthenticationError
        mock_response = Mock()
        mock_response.status_code = 401
        mock_body = {"error": {"message": "Invalid API key"}}
        
        # Setup mock to raise AuthenticationError with required parameters
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.audio.transcriptions.create.side_effect = AuthenticationError(
            "Invalid API key",
            response=mock_response,
            body=mock_body
        )
        
        client = TranscriptionClient(provider="groq", api_key="invalid_key")
        
        with pytest.raises(APIAuthenticationError) as exc_info:
            with patch('builtins.open', return_value=Mock()):
                client.transcribe_audio("test.wav")
        
        exc = exc_info.value
        assert exc.translation_key == "errors.api_authentication"
        assert exc.translation_params["provider"] == "groq"
    
    @patch('services.transcription_client.OpenAI')
    def test_transcribe_audio_network_error(self, mock_openai):
        """
        Test that network error is properly translated.
        
        Requirements: 2.2
        """
        from openai import APIConnectionError
        
        # Setup mock to raise APIConnectionError with required request parameter
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_request = Mock()
        mock_client.audio.transcriptions.create.side_effect = APIConnectionError(
            request=mock_request
        )
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        with pytest.raises(APINetworkError) as exc_info:
            with patch('builtins.open', return_value=Mock()):
                client.transcribe_audio("test.wav")
        
        exc = exc_info.value
        assert exc.translation_key == "errors.api_network"
        assert exc.translation_params["provider"] == "groq"
    
    @patch('services.transcription_client.OpenAI')
    def test_transcribe_audio_timeout_error(self, mock_openai):
        """
        Test that timeout error is properly translated.
        
        Requirements: 2.3
        """
        from openai import APITimeoutError as OpenAITimeoutError
        
        # Setup mock to raise APITimeoutError with required request parameter
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_request = Mock()
        mock_client.audio.transcriptions.create.side_effect = OpenAITimeoutError(
            request=mock_request
        )
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Should raise our custom APITimeoutError (not OpenAI's)
        with pytest.raises(APITimeoutError) as exc_info:
            with patch('builtins.open', return_value=Mock()):
                client.transcribe_audio("test.wav")
        
        exc = exc_info.value
        assert exc.translation_key == "errors.api_timeout"
        assert exc.translation_params["provider"] == "groq"
        assert exc.translation_params["timeout"] == 30
    
    @patch('services.transcription_client.OpenAI')
    def test_transcribe_audio_model_not_found_error(self, mock_openai):
        """
        Test that model not found error is properly translated.
        
        Requirements: 2.5
        """
        from openai import NotFoundError
        
        # Create mock response and body for NotFoundError
        mock_response = Mock()
        mock_response.status_code = 404
        mock_body = {"error": {"message": "Model not found"}}
        
        # Setup mock to raise NotFoundError with required parameters
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.audio.transcriptions.create.side_effect = NotFoundError(
            "Model not found",
            response=mock_response,
            body=mock_body
        )
        
        client = TranscriptionClient(provider="groq", api_key="test_key", model="invalid-model")
        
        with pytest.raises(ModelNotFoundError) as exc_info:
            with patch('builtins.open', return_value=Mock()):
                client.transcribe_audio("test.wav")
        
        exc = exc_info.value
        assert exc.translation_key == "errors.model_not_found"
        assert exc.translation_params["model"] == "invalid-model"
        assert exc.translation_params["provider"] == "groq"


class TestTranscriptionClientPostProcessText:
    """Tests for TranscriptionClient.post_process_text error handling."""
    
    @patch('services.transcription_client.OpenAI')
    def test_post_process_without_api_key_returns_original_text(self, mock_openai):
        """
        Test that post_process without API key returns original text.
        
        The post_process_text method catches all exceptions and returns
        the original text for graceful degradation.
        
        Requirements: 1.2, 2.1
        """
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Should return original text instead of raising exception
        result = client.post_process_text(
            text="test text",
            provider="openai",
            model="gpt-4",
            system_prompt="test prompt",
            api_key=None
        )
        
        # Verify it returns the original text
        assert result == "test text"
    
    @patch('services.transcription_client.OpenAI')
    def test_post_process_llm_without_base_url_returns_original_text(self, mock_openai):
        """
        Test that LLM provider without base_url returns original text.
        
        The post_process_text method catches all exceptions and returns
        the original text for graceful degradation.
        
        Requirements: 1.2
        """
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Should return original text instead of raising exception
        result = client.post_process_text(
            text="test text",
            provider="llm",
            model="local-model",
            system_prompt="test prompt",
            api_key="test_key",
            base_url=None
        )
        
        # Verify it returns the original text
        assert result == "test text"
    
    @patch('services.transcription_client.OpenAI')
    def test_post_process_unknown_provider_returns_original_text(self, mock_openai):
        """
        Test that unknown provider returns original text.
        
        The post_process_text method catches all exceptions and returns
        the original text for graceful degradation.
        
        Requirements: 1.2
        """
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Should return original text instead of raising exception
        result = client.post_process_text(
            text="test text",
            provider="unknown_provider",
            model="test-model",
            system_prompt="test prompt",
            api_key="test_key"
        )
        
        # Verify it returns the original text
        assert result == "test text"


class TestErrorMessageTranslation:
    """Tests for error message translation with different languages."""
    
    @patch('services.transcription_client.OpenAI')
    def test_error_messages_translate_to_english(self, mock_openai):
        """
        Test that error messages are translated to English.
        
        Requirements: 1.1, 1.2
        """
        original_lang = get_language()
        
        try:
            set_language("en")
            
            with pytest.raises(InvalidAPIKeyError) as exc_info:
                TranscriptionClient(provider="groq", api_key=None)
            
            exc = exc_info.value
            user_msg = exc.user_message
            
            # User message should be in English
            assert isinstance(user_msg, str)
            assert len(user_msg) > 0
            
            # Technical message should still be in Russian
            assert "groq" in exc.message.lower()
            
        finally:
            set_language(original_lang)
    
    @patch('services.transcription_client.OpenAI')
    def test_error_messages_translate_to_russian(self, mock_openai):
        """
        Test that error messages are translated to Russian.
        
        Requirements: 1.1, 1.2
        """
        original_lang = get_language()
        
        try:
            set_language("ru")
            
            with pytest.raises(InvalidAPIKeyError) as exc_info:
                TranscriptionClient(provider="groq", api_key=None)
            
            exc = exc_info.value
            user_msg = exc.user_message
            
            # User message should be in Russian
            assert isinstance(user_msg, str)
            assert len(user_msg) > 0
            
        finally:
            set_language(original_lang)
