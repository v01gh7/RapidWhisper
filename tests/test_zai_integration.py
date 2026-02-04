"""
Integration тесты для Z.AI провайдера.

Проверяет интеграцию Z.AI с другими компонентами системы:
- Постобработка текста через TranscriptionClient
- Форматирование текста через FormattingModule
- Обработка ошибок в реальных сценариях
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from services.transcription_client import TranscriptionClient
from services.formatting_module import FormattingModule
from core.config import Config


class TestZAIPostProcessingIntegration:
    """Integration тесты для постобработки с Z.AI провайдером."""
    
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_post_processing_with_zai_provider(self, mock_anthropic):
        """
        Integration тест: постобработка текста с провайдером Z.AI.
        
        Проверяет полный цикл постобработки:
        1. TranscriptionClient создает Anthropic клиент
        2. Отправляет запрос к Z.AI API
        3. Извлекает и возвращает обработанный текст
        
        Validates: Requirements 3.1
        """
        # Настроить mock для Anthropic клиента
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Привет, мир! Это тестовое сообщение."
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        # Создать TranscriptionClient для транскрипции
        transcription_client = TranscriptionClient(
            provider="groq",  # Используем groq для транскрипции
            api_key="test_groq_key"
        )
        
        # Выполнить постобработку через Z.AI
        original_text = "привет мир это тестовое сообщение"
        processed_text = transcription_client.post_process_text(
            text=original_text,
            provider="zai",
            model="GLM-4.7",
            system_prompt="Добавь пунктуацию и исправь регистр",
            api_key="test_glm_key",
            temperature=0.3
        )
        
        # Проверяем результат
        assert processed_text == "Привет, мир! Это тестовое сообщение."
        
        # Проверяем что Anthropic API вызван с правильными параметрами
        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs['model'] == "GLM-4.7"
        assert call_kwargs['system'] == "Добавь пунктуацию и исправь регистр"
        assert call_kwargs['messages'][0]['content'] == original_text
    
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_post_processing_with_different_models(self, mock_anthropic):
        """
        Тест постобработки с разными моделями Z.AI.
        
        Validates: Requirements 3.1, 1.3
        """
        # Настроить mock
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Обработанный текст"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Тест с моделью GLM-4.7
        result1 = client.post_process_text(
            text="тест",
            provider="zai",
            model="GLM-4.7",
            system_prompt="промпт",
            api_key="test_key"
        )
        assert result1 == "Обработанный текст"
        assert mock_client.messages.create.call_args[1]['model'] == "GLM-4.7"
        
        # Тест с моделью GLM-4-Plus
        result2 = client.post_process_text(
            text="тест",
            provider="zai",
            model="GLM-4-Plus",
            system_prompt="промпт",
            api_key="test_key"
        )
        assert result2 == "Обработанный текст"
        assert mock_client.messages.create.call_args[1]['model'] == "GLM-4-Plus"
    
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_post_processing_with_custom_temperature(self, mock_anthropic):
        """
        Тест постобработки с кастомной температурой.
        
        Validates: Requirements 3.1, 3.3
        """
        # Настроить mock
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Результат"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Тест с температурой 0.7
        result = client.post_process_text(
            text="тест",
            provider="zai",
            model="GLM-4.7",
            system_prompt="промпт",
            api_key="test_key",
            temperature=0.7
        )
        
        assert result == "Результат"
        assert mock_client.messages.create.call_args[1]['temperature'] == 0.7


class TestZAIFormattingIntegration:
    """Integration тесты для форматирования с Z.AI провайдером."""
    
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    @patch('core.config_loader.get_config_loader')
    def test_formatting_with_zai_provider(self, mock_config_loader, mock_anthropic):
        """
        Integration тест: форматирование текста с провайдером Z.AI.
        
        Проверяет что FormattingModule корректно использует Z.AI
        для форматирования текста.
        
        Validates: Requirements 3.2
        """
        # Настроить mock для Anthropic клиента
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Отформатированный текст для WhatsApp"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        # Настроить mock для config loader
        mock_loader = Mock()
        mock_loader.get.side_effect = lambda key, default=None: {
            'formatting.enabled': True,
            'formatting.provider': 'zai',
            'formatting.model': 'GLM-4.7',
            'formatting.temperature': 0.3,
            'formatting.custom_base_url': '',
            'formatting.use_fixed_format': False,
            'formatting.applications': ['whatsapp'],
            'formatting.prompts.whatsapp': 'Форматируй для WhatsApp',
            'ai_provider.api_keys.glm': 'test_glm_key'
        }.get(key, default)
        mock_config_loader.return_value = mock_loader
        
        # Создать FormattingModule
        formatting_module = FormattingModule()
        
        # Выполнить форматирование
        original_text = "привет как дела"
        formatted_text = formatting_module.format_text(
            text=original_text,
            format_type="whatsapp"
        )
        
        # Проверяем результат
        assert formatted_text == "Отформатированный текст для WhatsApp"
        
        # Проверяем что Anthropic API вызван
        mock_client.messages.create.assert_called_once()


class TestZAIErrorHandlingIntegration:
    """Integration тесты для обработки ошибок Z.AI."""
    
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_authentication_error_handling(self, mock_anthropic):
        """
        Тест обработки ошибки аутентификации в реальном сценарии.
        
        Validates: Requirements 6.1, 6.2, 6.3, 6.4, 4.2
        """
        from services.transcription_client import AnthropicAuthenticationError
        
        # Создать mock response и body
        mock_response = Mock()
        mock_response.status_code = 401
        mock_body = {"error": {"message": "Invalid API key"}}
        
        # Настроить mock для выброса ошибки
        mock_client = Mock()
        anthropic_error = AnthropicAuthenticationError(
            message="Invalid API key",
            response=mock_response,
            body=mock_body
        )
        mock_client.messages.create.side_effect = anthropic_error
        mock_anthropic.return_value = mock_client
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Проверяем что ошибка пробрасывается
        with pytest.raises(AnthropicAuthenticationError) as exc_info:
            client.post_process_text(
                text="тест",
                provider="zai",
                model="GLM-4.7",
                system_prompt="промпт",
                api_key="invalid_key"
            )
        
        assert "Invalid API key" in str(exc_info.value)
    
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_timeout_error_handling(self, mock_anthropic):
        """
        Тест обработки таймаута в реальном сценарии.
        
        Validates: Requirements 6.1, 6.2, 6.3, 6.4, 4.2
        """
        from services.transcription_client import AnthropicAPITimeoutError
        
        # Создать mock request
        mock_request = Mock()
        
        # Настроить mock для выброса таймаута
        mock_client = Mock()
        anthropic_error = AnthropicAPITimeoutError(request=mock_request)
        mock_client.messages.create.side_effect = anthropic_error
        mock_anthropic.return_value = mock_client
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Проверяем что ошибка пробрасывается
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
    def test_network_error_handling(self, mock_anthropic):
        """
        Тест обработки сетевой ошибки в реальном сценарии.
        
        Validates: Requirements 6.1, 6.2, 6.3, 6.4, 4.2
        """
        from services.transcription_client import AnthropicAPIConnectionError
        
        # Создать mock request
        mock_request = Mock()
        
        # Настроить mock для выброса сетевой ошибки
        mock_client = Mock()
        anthropic_error = AnthropicAPIConnectionError(request=mock_request)
        mock_client.messages.create.side_effect = anthropic_error
        mock_anthropic.return_value = mock_client
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Проверяем что ошибка пробрасывается
        with pytest.raises(AnthropicAPIConnectionError):
            client.post_process_text(
                text="тест",
                provider="zai",
                model="GLM-4.7",
                system_prompt="промпт",
                api_key="test_key"
            )


class TestZAIBackwardCompatibility:
    """Тесты обратной совместимости после добавления Z.AI."""
    
    @patch('services.transcription_client.OpenAI')
    def test_existing_providers_still_work(self, mock_openai):
        """
        Тест что существующие провайдеры продолжают работать.
        
        Validates: Requirements 8.1, 8.2, 8.4
        """
        # Настроить mock для OpenAI клиента
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Тест с провайдером groq
        client_groq = TranscriptionClient(provider="groq", api_key="test_key")
        assert client_groq.provider == "groq"
        assert client_groq.client is not None
        assert not hasattr(client_groq, 'anthropic_client') or client_groq.anthropic_client is None
        
        # Тест с провайдером openai
        client_openai = TranscriptionClient(provider="openai", api_key="test_key")
        assert client_openai.provider == "openai"
        assert client_openai.client is not None
        
        # Тест с провайдером glm
        client_glm = TranscriptionClient(provider="glm", api_key="test_key")
        assert client_glm.provider == "glm"
        assert client_glm.client is not None
    
    @patch('services.transcription_client.OpenAI')
    def test_openai_post_processing_unchanged(self, mock_openai):
        """
        Тест что постобработка через OpenAI-based провайдеры не изменилась.
        
        Validates: Requirements 8.1, 8.2, 8.4
        """
        # Настроить mock для OpenAI клиента
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Обработанный текст"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Выполнить постобработку через groq (OpenAI-based)
        result = client.post_process_text(
            text="тест",
            provider="groq",
            model="llama-3.3-70b-versatile",
            system_prompt="промпт",
            api_key="test_key"
        )
        
        assert result == "Обработанный текст"
        
        # Проверяем что OpenAI API вызван (не Anthropic)
        mock_client.chat.completions.create.assert_called_once()
