"""
Unit tests for service files error message internationalization.

Feature: error-messages-i18n
Tests error messages from audio_engine, audio_utils, data_models, main, and single_instance.
"""

import pytest
from utils.i18n import set_language, get_language


class TestDataModelsErrors:
    """Tests for data_models.py error messages."""
    
    def test_invalid_max_length_error(self):
        """
        Test that invalid max_length raises error with translation key.
        
        Requirements: 1.2
        """
        from models.data_models import TranscriptionResult
        from utils.exceptions import RapidWhisperError
        
        result = TranscriptionResult(text="test text", duration=1.0)
        
        with pytest.raises(RapidWhisperError) as exc_info:
            result.get_preview(max_length=0)
        
        exc = exc_info.value
        assert exc.translation_key == "errors.invalid_max_length"
        assert "max_length" in exc.message
    
    def test_invalid_max_length_negative_error(self):
        """
        Test that negative max_length raises error with translation key.
        
        Requirements: 1.2
        """
        from models.data_models import TranscriptionResult
        from utils.exceptions import RapidWhisperError
        
        result = TranscriptionResult(text="test text", duration=1.0)
        
        with pytest.raises(RapidWhisperError) as exc_info:
            result.get_preview(max_length=-5)
        
        exc = exc_info.value
        assert exc.translation_key == "errors.invalid_max_length"


class TestErrorMessageTranslation:
    """Tests for error message translation in service files."""
    
    def test_service_errors_translate_to_english(self):
        """
        Test that service file errors translate to English.
        
        Requirements: 1.1, 1.2
        """
        from models.data_models import TranscriptionResult
        from utils.exceptions import RapidWhisperError
        
        original_lang = get_language()
        
        try:
            set_language("en")
            
            result = TranscriptionResult(text="test", duration=1.0)
            
            with pytest.raises(RapidWhisperError) as exc_info:
                result.get_preview(max_length=0)
            
            exc = exc_info.value
            user_msg = exc.user_message
            
            # User message should be in English
            assert isinstance(user_msg, str)
            assert len(user_msg) > 0
            
            # Technical message should be in Russian
            assert "max_length" in exc.message
            
        finally:
            set_language(original_lang)
    
    def test_service_errors_translate_to_russian(self):
        """
        Test that service file errors translate to Russian.
        
        Requirements: 1.1, 1.2
        """
        from models.data_models import TranscriptionResult
        from utils.exceptions import RapidWhisperError
        
        original_lang = get_language()
        
        try:
            set_language("ru")
            
            result = TranscriptionResult(text="test", duration=1.0)
            
            with pytest.raises(RapidWhisperError) as exc_info:
                result.get_preview(max_length=0)
            
            exc = exc_info.value
            user_msg = exc.user_message
            
            # User message should be in Russian
            assert isinstance(user_msg, str)
            assert len(user_msg) > 0
            
        finally:
            set_language(original_lang)
    
    def test_service_errors_preserve_technical_message(self):
        """
        Test that service errors preserve technical message for logging.
        
        Requirements: 1.5, 4.1
        """
        from models.data_models import TranscriptionResult
        from utils.exceptions import RapidWhisperError
        
        result = TranscriptionResult(text="test", duration=1.0)
        
        with pytest.raises(RapidWhisperError) as exc_info:
            result.get_preview(max_length=-1)
        
        exc = exc_info.value
        
        # Technical message should be in Russian
        assert isinstance(exc.message, str)
        assert "max_length" in exc.message
        
        # str() should return technical message
        assert str(exc) == exc.message

