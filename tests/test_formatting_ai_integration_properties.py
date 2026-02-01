"""
Property-based tests for AI client integration in formatting.

These tests validate provider configuration selection and failure handling.
"""

import pytest
import tempfile
import os
from hypothesis import given, strategies as st, settings
from services.formatting_config import FormattingConfig


class TestFormattingAIIntegrationProperties:
    """Property-based tests for AI integration."""
    
    @given(
        provider=st.sampled_from(["groq", "openai", "glm", "custom"]),
        model=st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='-_.'
        ))
    )
    @settings(max_examples=20)
    def test_provider_configuration_selection(self, provider, model):
        """
        Feature: transcription-formatting, Property 11: Provider Configuration Selection
        
        **Validates: Requirements 7.2, 7.3**
        
        For any formatting request (when not combined with post-processing),
        the system should use the configured Formatting_AI_Provider and model,
        not the transcription or post-processing provider.
        """
        # Create temporary .env file with formatting configuration
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
            temp_env_path = f.name
            f.write(f"FORMATTING_ENABLED=true\n")
            f.write(f"FORMATTING_PROVIDER={provider}\n")
            f.write(f"FORMATTING_MODEL={model}\n")
            f.write(f"FORMATTING_APPLICATIONS=notion,obsidian\n")
        
        try:
            # Load configuration
            config = FormattingConfig.from_env(temp_env_path)
            
            # Verify configuration uses the specified provider and model
            assert config.provider == provider, \
                f"Provider mismatch: {config.provider} != {provider}"
            assert config.model == model, \
                f"Model mismatch: {config.model} != {model}"
            
            # Verify configuration is independent (not using transcription/post-processing config)
            assert config.provider in ["groq", "openai", "glm", "custom"]
            assert len(config.model) > 0
        
        finally:
            # Clean up
            if os.path.exists(temp_env_path):
                os.remove(temp_env_path)
    
    def test_graceful_failure_handling_unit(self):
        """
        Feature: transcription-formatting, Property 12: Graceful Failure Handling
        
        **Validates: Requirements 7.4, 7.5**
        
        Test that format_text returns original text on exception.
        """
        from unittest.mock import Mock, patch
        from services.formatting_module import FormattingModule
        
        # Create temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
            temp_env_path = f.name
            f.write(f"FORMATTING_ENABLED=true\n")
            f.write(f"FORMATTING_PROVIDER=groq\n")
            f.write(f"FORMATTING_MODEL=test-model\n")
            f.write(f"FORMATTING_APPLICATIONS=notion\n")
            f.write(f"GROQ_API_KEY=test_key\n")
        
        try:
            # Mock TranscriptionClient to raise an exception
            with patch('services.transcription_client.TranscriptionClient') as mock_client_class:
                mock_client = Mock()
                mock_client.post_process_text.side_effect = Exception("API Error")
                mock_client_class.return_value = mock_client
                
                # Mock get_env_path
                with patch('core.config.get_env_path', return_value=temp_env_path):
                    mock_monitor = Mock()
                    module = FormattingModule(window_monitor=mock_monitor, state_manager=None)
                    
                    # Call format_text - should return original text on failure
                    original_text = "This is test text"
                    result = module.format_text(original_text, "notion")
                    
                    # Verify original text is returned (no data loss)
                    assert result == original_text
        
        finally:
            # Clean up
            if os.path.exists(temp_env_path):
                os.remove(temp_env_path)
    
    def test_formatting_disabled_returns_original_text_unit(self):
        """
        Test that when formatting is disabled, original text is returned.
        """
        from unittest.mock import Mock, patch
        from services.formatting_module import FormattingModule
        
        # Create temporary .env file with formatting disabled
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
            temp_env_path = f.name
            f.write(f"FORMATTING_ENABLED=false\n")
            f.write(f"FORMATTING_PROVIDER=groq\n")
            f.write(f"FORMATTING_MODEL=test-model\n")
            f.write(f"FORMATTING_APPLICATIONS=notion\n")
        
        try:
            # Mock get_env_path
            with patch('core.config.get_env_path', return_value=temp_env_path):
                mock_monitor = Mock()
                module = FormattingModule(window_monitor=mock_monitor, state_manager=None)
                
                # Call process - should return original text
                original_text = "This is test text"
                result = module.process(original_text)
                
                # Verify original text is returned
                assert result == original_text
        
        finally:
            # Clean up
            if os.path.exists(temp_env_path):
                os.remove(temp_env_path)
