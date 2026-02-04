"""
Property-based тесты для Z.AI провайдера.

Использует Hypothesis для генерации случайных входных данных и проверки
универсальных свойств системы, которые должны выполняться для всех входов.

Каждый property test помечен комментарием с номером свойства из design.md.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from unittest.mock import Mock, patch, MagicMock
from services.transcription_client import TranscriptionClient
from core.config import Config
from utils.exceptions import InvalidAPIKeyError


# Стратегии для генерации тестовых данных
@st.composite
def valid_api_keys(draw):
    """Генерирует валидные API ключи (непустые строки)."""
    # Генерируем строки длиной от 10 до 100 символов
    return draw(st.text(
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),  # Буквы и цифры
            min_codepoint=33,
            max_codepoint=126
        ),
        min_size=10,
        max_size=100
    ))


@st.composite
def model_names(draw):
    """Генерирует валидные имена моделей."""
    models = ["GLM-4.7", "GLM-4-Plus", "GLM-4.6", "GLM-4.5", "GLM-4.5-air"]
    return draw(st.sampled_from(models))


@st.composite
def text_inputs(draw):
    """Генерирует текстовые входы для обработки."""
    return draw(st.text(min_size=1, max_size=1000))


@st.composite
def system_prompts(draw):
    """Генерирует системные промпты."""
    return draw(st.text(min_size=10, max_size=500))


@st.composite
def temperatures(draw):
    """Генерирует валидные значения температуры (0.0-1.0)."""
    return draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))


class TestProperty1_ZAIClientInitialization:
    """
    Property 1: ZAIClient Initialization Correctness
    
    For any valid GLM API key, creating a ZAIClient should result in
    an Anthropic client configured with base_url="https://api.z.ai/api/anthropic",
    timeout=130.0, and the provided API key.
    
    Validates: Requirements 1.1, 1.2, 2.1
    """
    
    @given(api_key=valid_api_keys())
    @settings(max_examples=100)
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_zai_client_initialization_with_valid_key(self, mock_anthropic, api_key):
        """
        Feature: zai-provider, Property 1: ZAIClient Initialization Correctness
        
        For any valid API key, TranscriptionClient with provider="zai" should:
        1. Create an Anthropic client
        2. Configure it with correct base_url
        3. Set timeout to 130.0
        4. Use the provided API key
        """
        # Настроить mock
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        
        # Создать TranscriptionClient с провайдером zai
        client = TranscriptionClient(provider="zai", api_key=api_key)
        
        # Проверяем что клиент создан с правильными параметрами
        assert client.provider == "zai"
        assert client.base_url == "https://api.z.ai/api/anthropic"
        assert client.timeout == 130.0
        assert client.anthropic_client == mock_client
        
        # Проверяем что Anthropic клиент вызван с правильными параметрами
        mock_anthropic.assert_called_once_with(
            api_key=api_key,
            base_url="https://api.z.ai/api/anthropic",
            timeout=130.0
        )
    
    @given(api_key=valid_api_keys(), model=model_names())
    @settings(max_examples=100)
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_zai_client_initialization_with_custom_model(self, mock_anthropic, api_key, model):
        """
        Feature: zai-provider, Property 1: ZAIClient Initialization Correctness
        
        For any valid API key and model name, TranscriptionClient should
        store the model correctly.
        """
        # Настроить mock
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        
        # Создать TranscriptionClient с кастомной моделью
        client = TranscriptionClient(provider="zai", api_key=api_key, model=model)
        
        # Проверяем что модель сохранена
        assert client.model == model
    
    @given(api_key=valid_api_keys())
    @settings(max_examples=100)
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_zai_client_default_model(self, mock_anthropic, api_key):
        """
        Feature: zai-provider, Property 1: ZAIClient Initialization Correctness
        
        For any valid API key, if no model is specified, TranscriptionClient
        should use "GLM-4.7" as default.
        """
        # Настроить mock
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        
        # Создать TranscriptionClient без указания модели
        client = TranscriptionClient(provider="zai", api_key=api_key)
        
        # Проверяем что используется модель по умолчанию
        assert client.model == "GLM-4.7"


class TestProperty4_AnthropicAPIRequestStructure:
    """
    Property 4: Anthropic API Request Structure
    
    For any text input and system prompt, when post_process_text() is called
    with provider="zai", the underlying Anthropic client should receive a
    messages.create() call with parameters: model, max_tokens, temperature,
    system, and messages array.
    
    Validates: Requirements 2.2, 3.3
    """
    
    @given(
        text=text_inputs(),
        system_prompt=system_prompts(),
        temperature=temperatures(),
        model=model_names()
    )
    @settings(max_examples=100)
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_anthropic_api_request_structure(
        self, mock_anthropic, text, system_prompt, temperature, model
    ):
        """
        Feature: zai-provider, Property 4: Anthropic API Request Structure
        
        For any text, system prompt, temperature, and model, the Anthropic API
        should be called with correct structure.
        """
        # Настроить mock
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Обработанный текст"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        # Создать клиент
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Выполнить постобработку через Z.AI
        result = client.post_process_text(
            text=text,
            provider="zai",
            model=model,
            system_prompt=system_prompt,
            api_key="test_glm_key",
            temperature=temperature
        )
        
        # Проверяем что API вызван
        mock_client.messages.create.assert_called_once()
        
        # Проверяем структуру запроса
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs['model'] == model
        assert call_kwargs['max_tokens'] == 16000  # Дефолтное значение
        assert call_kwargs['temperature'] == temperature
        assert call_kwargs['system'] == system_prompt
        assert call_kwargs['messages'] == [{"role": "user", "content": text}]
        
        # Проверяем что результат извлечен правильно
        assert result == "Обработанный текст"
    
    @given(
        text=text_inputs(),
        system_prompt=system_prompts()
    )
    @settings(max_examples=100)
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_anthropic_api_default_parameters(
        self, mock_anthropic, text, system_prompt
    ):
        """
        Feature: zai-provider, Property 4: Anthropic API Request Structure
        
        For any text and system prompt, if temperature is not specified,
        default values should be used.
        """
        # Настроить mock
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = "Результат"
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        # Создать клиент
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Выполнить постобработку с параметрами по умолчанию
        result = client.post_process_text(
            text=text,
            provider="zai",
            model="GLM-4.7",
            system_prompt=system_prompt,
            api_key="test_key"
        )
        
        # Проверяем что используются значения по умолчанию
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs['temperature'] == 0.3  # Значение по умолчанию
        assert call_kwargs['max_tokens'] == 16000  # Значение по умолчанию


class TestProperty5_ResponseParsingCorrectness:
    """
    Property 5: Response Parsing Correctness
    
    For any valid Anthropic API response containing content[0].text,
    post_process_text() should extract and return the text value from
    response.content[0].text.
    
    Validates: Requirements 3.4, 9.2, 9.4
    """
    
    @given(
        input_text=text_inputs(),
        response_text=text_inputs()
    )
    @settings(max_examples=100)
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_response_parsing_extracts_text_correctly(
        self, mock_anthropic, input_text, response_text
    ):
        """
        Feature: zai-provider, Property 5: Response Parsing Correctness
        
        For any response text, the system should correctly extract it from
        response.content[0].text structure.
        """
        # Настроить mock с правильной структурой Anthropic response
        mock_client = Mock()
        mock_response = Mock()
        mock_content = Mock()
        mock_content.text = response_text
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        # Создать клиент
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Выполнить постобработку
        result = client.post_process_text(
            text=input_text,
            provider="zai",
            model="GLM-4.7",
            system_prompt="промпт",
            api_key="test_key"
        )
        
        # Проверяем что текст извлечен правильно
        assert result == response_text.strip()
    
    @given(input_text=text_inputs())
    @settings(max_examples=100)
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_empty_response_returns_original_text(
        self, mock_anthropic, input_text
    ):
        """
        Feature: zai-provider, Property 5: Response Parsing Correctness
        
        For any input text, if the response is empty or invalid,
        the original text should be returned.
        """
        # Настроить mock с пустым ответом
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = []
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        # Создать клиент
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Выполнить постобработку
        result = client.post_process_text(
            text=input_text,
            provider="zai",
            model="GLM-4.7",
            system_prompt="промпт",
            api_key="test_key"
        )
        
        # Проверяем что возвращен оригинальный текст
        assert result == input_text


class TestProperty6_InvalidAPIKeyRejection:
    """
    Property 6: Invalid API Key Rejection
    
    For any empty or None API key, attempting to create a TranscriptionClient
    with provider="zai" should raise InvalidAPIKeyError with provider="zai".
    
    Validates: Requirements 6.1
    """
    
    @given(empty_key=st.sampled_from(["", None]))
    @settings(max_examples=10)
    def test_empty_or_none_api_key_raises_error(self, empty_key):
        """
        Feature: zai-provider, Property 6: Invalid API Key Rejection
        
        For any empty or None API key, initialization should fail with
        InvalidAPIKeyError.
        """
        # Попытка создать клиент с пустым/None ключом
        with pytest.raises(InvalidAPIKeyError) as exc_info:
            TranscriptionClient(provider="zai", api_key=empty_key)
        
        # Проверяем что ошибка содержит информацию о провайдере
        assert "zai" in str(exc_info.value).lower()
    
    @given(whitespace_key=st.text(alphabet=st.characters(whitelist_categories=('Zs',)), min_size=1, max_size=20))
    @settings(max_examples=50)
    def test_whitespace_only_api_key_raises_error(self, whitespace_key):
        """
        Feature: zai-provider, Property 6: Invalid API Key Rejection
        
        For any whitespace-only API key, initialization should fail with
        InvalidAPIKeyError.
        """
        # Попытка создать клиент с ключом из пробелов
        with pytest.raises(InvalidAPIKeyError):
            TranscriptionClient(provider="zai", api_key=whitespace_key)


class TestProperty2_ProviderValidationCompleteness:
    """
    Property 2: Provider Validation Completeness
    
    For any provider value in the set {"openai", "groq", "glm", "custom", "zai"},
    Config.validate() should not return errors related to invalid provider.
    
    Validates: Requirements 1.5
    """
    
    @given(provider=st.sampled_from(["openai", "groq", "glm", "custom", "zai"]))
    @settings(max_examples=50)
    def test_all_valid_providers_accepted(self, provider):
        """
        Feature: zai-provider, Property 2: Provider Validation Completeness
        
        For any valid provider, Config.validate() should accept it without
        errors about invalid provider.
        """
        # Создать минимальную конфигурацию с валидным провайдером
        config = Config()
        config.ai_provider = provider
        
        # Установить необходимые API ключи в зависимости от провайдера
        if provider == "openai":
            config.openai_api_key = "test_key"
        elif provider == "groq":
            config.groq_api_key = "test_key"
        elif provider == "glm":
            config.glm_api_key = "test_key"
        elif provider == "zai":
            config.glm_api_key = "test_key"  # Z.AI использует GLM_API_KEY
        elif provider == "custom":
            config.custom_api_key = "test_key"
            config.custom_base_url = "https://example.com"
        
        # Валидировать конфигурацию
        errors = config.validate()
        
        # Проверяем что нет ошибок о невалидном провайдере
        provider_errors = [e for e in errors if "provider" in e.lower() and "must be one of" in e.lower()]
        assert len(provider_errors) == 0, f"Provider {provider} should be valid but got errors: {provider_errors}"


class TestProperty9_ErrorHandlingCompleteness:
    """
    Property 9: Error Handling Completeness
    
    For any error type in {AuthenticationError, APITimeoutError, APIConnectionError,
    NotFoundError, missing content field}, post_process_text() should catch the error
    and either raise the appropriate custom exception or return original text.
    
    Validates: Requirements 6.2, 6.3, 6.4, 6.5, 9.1, 9.3
    """
    
    @given(input_text=text_inputs())
    @settings(max_examples=50)
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_authentication_error_propagated(self, mock_anthropic, input_text):
        """
        Feature: zai-provider, Property 9: Error Handling Completeness
        
        For any input text, if AuthenticationError occurs, it should be
        propagated to the caller.
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
        with pytest.raises(AnthropicAuthenticationError):
            client.post_process_text(
                text=input_text,
                provider="zai",
                model="GLM-4.7",
                system_prompt="промпт",
                api_key="invalid_key"
            )
    
    @given(input_text=text_inputs())
    @settings(max_examples=50)
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_timeout_error_propagated(self, mock_anthropic, input_text):
        """
        Feature: zai-provider, Property 9: Error Handling Completeness
        
        For any input text, if APITimeoutError occurs, it should be
        propagated to the caller.
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
                text=input_text,
                provider="zai",
                model="GLM-4.7",
                system_prompt="промпт",
                api_key="test_key"
            )
    
    @given(input_text=text_inputs())
    @settings(max_examples=50)
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_connection_error_propagated(self, mock_anthropic, input_text):
        """
        Feature: zai-provider, Property 9: Error Handling Completeness
        
        For any input text, if APIConnectionError occurs, it should be
        propagated to the caller.
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
                text=input_text,
                provider="zai",
                model="GLM-4.7",
                system_prompt="промпт",
                api_key="test_key"
            )
    
    @given(input_text=text_inputs())
    @settings(max_examples=50)
    @patch('services.transcription_client.ANTHROPIC_AVAILABLE', True)
    @patch('services.transcription_client.Anthropic')
    def test_bad_request_returns_original_text(self, mock_anthropic, input_text):
        """
        Feature: zai-provider, Property 9: Error Handling Completeness
        
        For any input text, if BadRequestError occurs, the original text
        should be returned (graceful degradation).
        """
        from services.transcription_client import AnthropicBadRequestError
        
        # Создать mock response и body
        mock_response = Mock()
        mock_response.status_code = 400
        mock_body = {"error": {"message": "Bad request"}}
        
        # Настроить mock для выброса ошибки
        mock_client = Mock()
        anthropic_error = AnthropicBadRequestError(
            message="Bad request",
            response=mock_response,
            body=mock_body
        )
        mock_client.messages.create.side_effect = anthropic_error
        mock_anthropic.return_value = mock_client
        
        client = TranscriptionClient(provider="groq", api_key="test_key")
        
        # Выполнить постобработку
        result = client.post_process_text(
            text=input_text,
            provider="zai",
            model="GLM-4.7",
            system_prompt="промпт",
            api_key="test_key"
        )
        
        # Проверяем что возвращен оригинальный текст
        assert result == input_text
