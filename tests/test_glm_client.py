"""
Unit-тесты для GLM API клиента.

Тестирует инициализацию клиента, отправку запросов на транскрипцию,
обработку ошибок API и извлечение текста из ответов.
"""

import os
import pytest
from unittest.mock import Mock, patch, mock_open
import openai

from services.glm_client import GLMClient
from utils.exceptions import (
    AuthenticationError,
    APIConnectionError,
    APITimeoutError,
    APIResponseError,
    MissingConfigError,
)


class TestGLMClientInitialization:
    """Тесты инициализации GLM клиента."""
    
    def test_initialization_with_api_key(self):
        """Тест инициализации с явно указанным API ключом."""
        client = GLMClient(api_key="test_api_key_123")
        
        assert client.api_key == "test_api_key_123"
        assert client.base_url == "https://open.bigmodel.cn/api/paas/v4/"
        assert client.model == "whisper-1"
        assert client.timeout == 30
        assert client.client is not None
    
    def test_initialization_from_environment(self, monkeypatch):
        """Тест загрузки API ключа из переменной окружения."""
        monkeypatch.setenv("GLM_API_KEY", "env_api_key_456")
        
        client = GLMClient()
        
        assert client.api_key == "env_api_key_456"
    
    def test_initialization_without_api_key(self, monkeypatch):
        """Тест ошибки при отсутствии API ключа."""
        monkeypatch.delenv("GLM_API_KEY", raising=False)
        
        with pytest.raises(MissingConfigError) as exc_info:
            GLMClient()
        
        assert "GLM_API_KEY" in str(exc_info.value)
    
    def test_initialization_prefers_parameter_over_env(self, monkeypatch):
        """Тест приоритета параметра над переменной окружения."""
        monkeypatch.setenv("GLM_API_KEY", "env_key")
        
        client = GLMClient(api_key="param_key")
        
        assert client.api_key == "param_key"


class TestGLMClientTranscription:
    """Тесты транскрипции аудио."""
    
    def test_transcribe_audio_success(self, tmp_path):
        """Тест успешной транскрипции аудио файла."""
        # Создать временный аудио файл
        audio_file = tmp_path / "test_audio.wav"
        audio_file.write_bytes(b"fake audio data")
        
        # Создать мок ответа API
        mock_response = Mock()
        mock_response.text = "Привет, это тестовая транскрипция"
        
        client = GLMClient(api_key="test_key")
        
        with patch.object(client.client.audio.transcriptions, 'create', return_value=mock_response):
            result = client.transcribe_audio(str(audio_file))
        
        assert result == "Привет, это тестовая транскрипция"
    
    def test_transcribe_audio_file_not_found(self):
        """Тест обработки отсутствующего файла."""
        client = GLMClient(api_key="test_key")
        
        with pytest.raises(FileNotFoundError):
            client.transcribe_audio("nonexistent_file.wav")
    
    def test_transcribe_audio_authentication_error(self, tmp_path):
        """Тест обработки ошибки аутентификации."""
        audio_file = tmp_path / "test_audio.wav"
        audio_file.write_bytes(b"fake audio data")
        
        client = GLMClient(api_key="invalid_key")
        
        # Создать мок ответа для AuthenticationError
        mock_response = Mock()
        mock_response.status_code = 401
        mock_body = {"error": {"message": "Invalid API key"}}
        
        with patch.object(
            client.client.audio.transcriptions, 
            'create', 
            side_effect=openai.AuthenticationError("Invalid API key", response=mock_response, body=mock_body)
        ):
            with pytest.raises(AuthenticationError) as exc_info:
                client.transcribe_audio(str(audio_file))
            
            assert "GLM_API_KEY" in exc_info.value.user_message
    
    def test_transcribe_audio_connection_error(self, tmp_path):
        """Тест обработки ошибки подключения."""
        audio_file = tmp_path / "test_audio.wav"
        audio_file.write_bytes(b"fake audio data")
        
        client = GLMClient(api_key="test_key")
        
        # Создать мок для APIConnectionError
        mock_request = Mock()
        
        with patch.object(
            client.client.audio.transcriptions, 
            'create', 
            side_effect=openai.APIConnectionError(request=mock_request)
        ):
            with pytest.raises(APIConnectionError) as exc_info:
                client.transcribe_audio(str(audio_file))
            
            assert "сети" in exc_info.value.user_message.lower() or "подключение" in exc_info.value.user_message.lower()
    
    def test_transcribe_audio_timeout_error(self, tmp_path):
        """Тест обработки таймаута."""
        audio_file = tmp_path / "test_audio.wav"
        audio_file.write_bytes(b"fake audio data")
        
        client = GLMClient(api_key="test_key")
        
        with patch.object(
            client.client.audio.transcriptions, 
            'create', 
            side_effect=openai.APITimeoutError("Request timeout")
        ):
            with pytest.raises(APITimeoutError) as exc_info:
                client.transcribe_audio(str(audio_file))
            
            assert "время" in exc_info.value.user_message.lower() or "таймаут" in exc_info.value.user_message.lower()
    
    def test_transcribe_audio_response_without_text(self, tmp_path):
        """Тест обработки ответа без поля text."""
        audio_file = tmp_path / "test_audio.wav"
        audio_file.write_bytes(b"fake audio data")
        
        # Создать мок ответа без поля text
        mock_response = Mock(spec=[])  # Пустой spec - нет атрибутов
        
        client = GLMClient(api_key="test_key")
        
        with patch.object(client.client.audio.transcriptions, 'create', return_value=mock_response):
            with pytest.raises(APIResponseError) as exc_info:
                client.transcribe_audio(str(audio_file))
            
            assert "text" in str(exc_info.value).lower()


class TestGLMClientPrepareAudioFile:
    """Тесты подготовки аудио файла."""
    
    def test_prepare_audio_file_success(self, tmp_path):
        """Тест успешного открытия файла."""
        audio_file = tmp_path / "test.wav"
        audio_file.write_bytes(b"test audio content")
        
        client = GLMClient(api_key="test_key")
        file_obj = client._prepare_audio_file(str(audio_file))
        
        assert file_obj is not None
        assert file_obj.mode == 'rb'
        
        # Прочитать содержимое для проверки
        content = file_obj.read()
        assert content == b"test audio content"
        
        file_obj.close()
    
    def test_prepare_audio_file_not_found(self):
        """Тест обработки отсутствующего файла."""
        client = GLMClient(api_key="test_key")
        
        with pytest.raises(FileNotFoundError):
            client._prepare_audio_file("nonexistent.wav")


class TestGLMClientErrorHandling:
    """Тесты обработки ошибок API."""
    
    def test_handle_authentication_error(self):
        """Тест преобразования ошибки аутентификации."""
        client = GLMClient(api_key="test_key")
        
        # Создать мок ответа для AuthenticationError
        mock_response = Mock()
        mock_response.status_code = 401
        mock_body = {"error": {"message": "Invalid API key"}}
        error = openai.AuthenticationError("Invalid API key", response=mock_response, body=mock_body)
        
        with pytest.raises(AuthenticationError):
            client._handle_api_error(error)
    
    def test_handle_connection_error(self):
        """Тест преобразования ошибки подключения."""
        client = GLMClient(api_key="test_key")
        
        # Создать мок для APIConnectionError
        mock_request = Mock()
        error = openai.APIConnectionError(request=mock_request)
        
        with pytest.raises(APIConnectionError):
            client._handle_api_error(error)
    
    def test_handle_timeout_error(self):
        """Тест преобразования ошибки таймаута."""
        client = GLMClient(api_key="test_key")
        error = openai.APITimeoutError("Request timeout")
        
        with pytest.raises(APITimeoutError):
            client._handle_api_error(error)
    
    def test_handle_generic_error(self):
        """Тест преобразования общей ошибки."""
        client = GLMClient(api_key="test_key")
        error = Exception("Unknown error")
        
        with pytest.raises(APIResponseError):
            client._handle_api_error(error)


class TestGLMClientIntegration:
    """Интеграционные тесты GLM клиента."""
    
    def test_full_transcription_flow(self, tmp_path):
        """Тест полного потока транскрипции."""
        # Создать временный аудио файл
        audio_file = tmp_path / "recording.wav"
        audio_file.write_bytes(b"simulated audio data")
        
        # Создать мок ответа
        mock_response = Mock()
        mock_response.text = "Это полная транскрипция аудио записи"
        
        client = GLMClient(api_key="integration_test_key")
        
        with patch.object(client.client.audio.transcriptions, 'create', return_value=mock_response) as mock_create:
            result = client.transcribe_audio(str(audio_file))
            
            # Проверить результат
            assert result == "Это полная транскрипция аудио записи"
            
            # Проверить, что API был вызван с правильными параметрами
            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs['model'] == 'whisper-1'
            assert call_kwargs['response_format'] == 'json'
    
    def test_error_recovery_flow(self, tmp_path):
        """Тест восстановления после ошибки."""
        audio_file = tmp_path / "test.wav"
        audio_file.write_bytes(b"audio data")
        
        client = GLMClient(api_key="test_key")
        
        # Первый вызов - ошибка
        with patch.object(
            client.client.audio.transcriptions, 
            'create', 
            side_effect=openai.APIConnectionError("Network error")
        ):
            with pytest.raises(APIConnectionError):
                client.transcribe_audio(str(audio_file))
        
        # Второй вызов - успех
        mock_response = Mock()
        mock_response.text = "Успешная транскрипция после ошибки"
        
        with patch.object(client.client.audio.transcriptions, 'create', return_value=mock_response):
            result = client.transcribe_audio(str(audio_file))
            assert result == "Успешная транскрипция после ошибки"
