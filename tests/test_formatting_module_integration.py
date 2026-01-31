"""
Integration tests for formatting module with per-application prompts.

Tests that the formatting module correctly uses per-application prompts.
"""

import pytest
from services.formatting_config import FormattingConfig, UNIVERSAL_DEFAULT_PROMPT
from services.formatting_module import FormattingModule
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os


def test_integration_formatting_uses_correct_prompt_for_each_app():
    """
    Integration test: Formatting uses correct prompt for each application
    
    Validates: Requirements 5.4, 6.1
    """
    # Create temp .env with different prompts for different apps
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        f.write("GROQ_API_KEY=test_key\n")
        f.write("FORMATTING_APPLICATIONS=notion,markdown,word\n")
        
        import json
        app_prompts_data = {
            "notion": {"enabled": True, "prompt": "Format for Notion with headers"},
            "markdown": {"enabled": True, "prompt": "Format as clean markdown"},
            "word": {"enabled": True, "prompt": ""}  # Empty = use default
        }
        f.write(f"FORMATTING_APP_PROMPTS={json.dumps(app_prompts_data, ensure_ascii=False)}\n")
        
        # Add web app keywords (required for detection)
        web_keywords = {
            "notion": ["notion"],
            "markdown": ["markdown"],
            "word": ["word"]
        }
        f.write(f"FORMATTING_WEB_APP_KEYWORDS={json.dumps(web_keywords, ensure_ascii=False)}\n")
        temp_path = f.name
    
    try:
        # Load config
        config = FormattingConfig.from_env(temp_path)
        
        # Verify prompts are loaded correctly
        assert config.get_prompt_for_app("notion") == "Format for Notion with headers"
        assert config.get_prompt_for_app("markdown") == "Format as clean markdown"
        assert config.get_prompt_for_app("word") == UNIVERSAL_DEFAULT_PROMPT
        
        # Create formatting module
        module = FormattingModule(config)
        
        # Mock the TranscriptionClient.post_process_text method
        with patch('services.transcription_client.TranscriptionClient.post_process_text') as mock_post_process:
            mock_post_process.return_value = "Formatted text"
            
            # Test formatting for Notion
            result = module.format_text("Test text", "notion")
            
            # Verify correct prompt was used
            assert mock_post_process.called
            call_kwargs = mock_post_process.call_args.kwargs
            assert call_kwargs['system_prompt'] == "Format for Notion with headers"
            assert result == "Formatted text"
            
            # Test formatting for Markdown
            result = module.format_text("Test text", "markdown")
            call_kwargs = mock_post_process.call_args.kwargs
            assert call_kwargs['system_prompt'] == "Format as clean markdown"
            
            # Test formatting for Word (should use default)
            result = module.format_text("Test text", "word")
            call_kwargs = mock_post_process.call_args.kwargs
            assert call_kwargs['system_prompt'] == UNIVERSAL_DEFAULT_PROMPT
    finally:
        os.unlink(temp_path)


def test_integration_formatting_falls_back_to_default():
    """
    Integration test: Formatting falls back to default for apps without custom prompts
    
    Validates: Requirements 5.2, 6.2
    """
    # Create temp .env with apps that have no custom prompts
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        f.write("GROQ_API_KEY=test_key\n")
        f.write("FORMATTING_APPLICATIONS=app1,app2\n")
        
        import json
        app_prompts_data = {
            "app1": {"enabled": True, "prompt": ""},
            "app2": {"enabled": True, "prompt": ""}
        }
        f.write(f"FORMATTING_APP_PROMPTS={json.dumps(app_prompts_data, ensure_ascii=False)}\n")
        
        # Add web app keywords
        web_keywords = {
            "app1": ["app1"],
            "app2": ["app2"]
        }
        f.write(f"FORMATTING_WEB_APP_KEYWORDS={json.dumps(web_keywords, ensure_ascii=False)}\n")
        temp_path = f.name
    
    try:
        # Load config
        config = FormattingConfig.from_env(temp_path)
        
        # Verify both apps use default prompt
        assert config.get_prompt_for_app("app1") == UNIVERSAL_DEFAULT_PROMPT
        assert config.get_prompt_for_app("app2") == UNIVERSAL_DEFAULT_PROMPT
        
        # Create formatting module
        module = FormattingModule(config)
        
        # Mock the TranscriptionClient.post_process_text method
        with patch('services.transcription_client.TranscriptionClient.post_process_text') as mock_post_process:
            mock_post_process.return_value = "Formatted text"
            
            # Test formatting for both apps
            module.format_text("Test text", "app1")
            call_kwargs1 = mock_post_process.call_args.kwargs
            
            module.format_text("Test text", "app2")
            call_kwargs2 = mock_post_process.call_args.kwargs
            
            # Both should use the same default prompt
            assert call_kwargs1['system_prompt'] == UNIVERSAL_DEFAULT_PROMPT
            assert call_kwargs2['system_prompt'] == UNIVERSAL_DEFAULT_PROMPT
    finally:
        os.unlink(temp_path)


def test_integration_formatting_config_persistence():
    """
    Integration test: Formatting configuration persists across save/load cycles
    
    Validates: Requirements 7.1, 7.2, 7.3
    """
    # Create temp .env
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        
        import json
        # Add web app keywords
        web_keywords = {
            "app1": ["app1"],
            "app2": ["app2"],
            "app3": ["app3"]
        }
        f.write(f"FORMATTING_WEB_APP_KEYWORDS={json.dumps(web_keywords, ensure_ascii=False)}\n")
        temp_path = f.name
    
    try:
        # Create config with custom prompts
        config = FormattingConfig()
        config.applications = ["app1", "app2", "app3"]
        config.set_prompt_for_app("app1", "Custom prompt 1")
        config.set_prompt_for_app("app2", "Custom prompt 2")
        config.set_prompt_for_app("app3", "")  # Default
        
        # Save to file
        config.save_to_env(temp_path)
        
        # Load from file
        loaded_config = FormattingConfig.from_env(temp_path)
        
        # Verify all data persisted correctly
        # Note: _fallback is automatically added during save
        assert "app1" in loaded_config.applications
        assert "app2" in loaded_config.applications
        assert "app3" in loaded_config.applications
        assert loaded_config.get_prompt_for_app("app1") == "Custom prompt 1"
        assert loaded_config.get_prompt_for_app("app2") == "Custom prompt 2"
        assert loaded_config.get_prompt_for_app("app3") == UNIVERSAL_DEFAULT_PROMPT
    finally:
        os.unlink(temp_path)


def test_integration_formatting_with_unknown_app():
    """
    Integration test: Formatting handles unknown applications gracefully
    
    Validates: Requirements 5.2, 6.2
    """
    # Create temp .env
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        f.write("GROQ_API_KEY=test_key\n")
        f.write("FORMATTING_APPLICATIONS=known_app\n")
        
        import json
        app_prompts_data = {
            "known_app": {"enabled": True, "prompt": "Custom prompt"}
        }
        f.write(f"FORMATTING_APP_PROMPTS={json.dumps(app_prompts_data, ensure_ascii=False)}\n")
        
        # Add web app keywords
        web_keywords = {
            "known_app": ["known_app"]
        }
        f.write(f"FORMATTING_WEB_APP_KEYWORDS={json.dumps(web_keywords, ensure_ascii=False)}\n")
        temp_path = f.name
    
    try:
        # Load config
        config = FormattingConfig.from_env(temp_path)
        
        # Request prompt for unknown app - should return default
        unknown_prompt = config.get_prompt_for_app("unknown_app")
        assert unknown_prompt == UNIVERSAL_DEFAULT_PROMPT
        
        # Create formatting module
        module = FormattingModule(config)
        
        # Mock the TranscriptionClient.post_process_text method
        with patch('services.transcription_client.TranscriptionClient.post_process_text') as mock_post_process:
            mock_post_process.return_value = "Formatted text"
            
            # Format for unknown app - should use default prompt
            result = module.format_text("Test text", "unknown_app")
            
            # Verify default prompt was used
            call_kwargs = mock_post_process.call_args.kwargs
            assert call_kwargs['system_prompt'] == UNIVERSAL_DEFAULT_PROMPT
    finally:
        os.unlink(temp_path)


def test_integration_formatting_prompt_passed_to_ai():
    """
    Integration test: Verify prompt is correctly passed to AI client
    
    Validates: Requirements 5.4, 6.1
    """
    # Create temp .env
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        f.write("FORMATTING_ENABLED=true\n")
        f.write("FORMATTING_PROVIDER=groq\n")
        f.write("GROQ_API_KEY=test_key\n")
        f.write("FORMATTING_APPLICATIONS=test_app\n")
        
        import json
        app_prompts_data = {
            "test_app": {"enabled": True, "prompt": "Very specific custom prompt for testing"}
        }
        f.write(f"FORMATTING_APP_PROMPTS={json.dumps(app_prompts_data, ensure_ascii=False)}\n")
        
        # Add web app keywords
        web_keywords = {
            "test_app": ["test_app"]
        }
        f.write(f"FORMATTING_WEB_APP_KEYWORDS={json.dumps(web_keywords, ensure_ascii=False)}\n")
        temp_path = f.name
    
    try:
        # Load config
        config = FormattingConfig.from_env(temp_path)
        
        # Create formatting module
        module = FormattingModule(config)
        
        # Mock the TranscriptionClient.post_process_text method
        with patch('services.transcription_client.TranscriptionClient.post_process_text') as mock_post_process:
            mock_post_process.return_value = "Formatted output"
            
            # Format text
            input_text = "This is test input text"
            result = module.format_text(input_text, "test_app")
            
            # Verify the method was called with correct parameters
            assert mock_post_process.called
            call_args = mock_post_process.call_args
            
            # Check positional and keyword arguments
            assert call_args.kwargs['text'] == input_text
            assert call_args.kwargs['system_prompt'] == "Very specific custom prompt for testing"
            assert call_args.kwargs['provider'] == "groq"
            assert call_args.kwargs['temperature'] == 0.3
            assert result == "Formatted output"
    finally:
        os.unlink(temp_path)

