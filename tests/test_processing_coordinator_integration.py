"""
Integration tests for processing coordinator.

These tests verify the complete processing pipeline with different
combinations of formatting and post-processing settings.
"""

import pytest
from unittest.mock import Mock, MagicMock
from services.processing_coordinator import ProcessingCoordinator
from services.formatting_module import FormattingModule
from services.formatting_config import FormattingConfig
from services.window_monitor import WindowInfo


class TestProcessingCoordinatorIntegration:
    """Integration tests for processing coordinator."""
    
    def test_formatting_only_pipeline(self):
        """
        Test formatting-only pipeline (post-processing disabled).
        
        **Validates: Requirements 4.1, 5.1**
        """
        # Create formatting config with formatting enabled
        formatting_config = FormattingConfig(
            enabled=True,
            provider="groq",
            model="test-model",
            applications=["notion", "obsidian", "markdown"]
        )
        
        # Create mock window monitor that returns matching app
        mock_window_monitor = Mock()
        mock_window_monitor.get_active_window_info.return_value = WindowInfo(
            title="test.md",
            process_name="vscode",
            icon=None,
            process_id=1234
        )
        
        # Create mock AI client
        mock_ai_client = Mock()
        mock_ai_client.post_process_text.return_value = "FORMATTED TEXT"
        
        mock_ai_factory = Mock()
        mock_ai_factory.create.return_value = mock_ai_client
        
        # Create formatting module
        formatting_module = FormattingModule(
            config_manager=None,
            ai_client_factory=mock_ai_factory,
            window_monitor=mock_window_monitor,
            state_manager=None
        )
        formatting_module.config = formatting_config
        
        # Create mock config with post-processing disabled
        mock_config = Mock()
        mock_config.enable_post_processing = False
        
        # Create mock transcription client
        mock_transcription_client = Mock()
        
        # Create coordinator
        coordinator = ProcessingCoordinator(
            formatting_module=formatting_module,
            config_manager=mock_config
        )
        
        # Process text
        result = coordinator.process_transcription(
            text="Original text",
            transcription_client=mock_transcription_client,
            config=mock_config
        )
        
        # Verify formatting was applied
        assert result == "FORMATTED TEXT"
        
        # Verify post-processing was NOT called
        assert not mock_transcription_client.post_process_text.called
    
    def test_combined_formatting_and_post_processing_pipeline(self):
        """
        Test combined formatting + post-processing pipeline.
        
        **Validates: Requirements 5.1, 5.4**
        """
        # Create formatting config
        formatting_config = FormattingConfig(
            enabled=True,
            provider="groq",
            model="formatting-model",
            applications=["notion", "obsidian", "markdown"]
        )
        
        # Create mock window monitor with matching app
        mock_window_monitor = Mock()
        mock_window_monitor.get_active_window_info.return_value = WindowInfo(
            title="test.md",
            process_name="vscode",
            icon=None,
            process_id=1234
        )
        
        # Create formatting module
        formatting_module = FormattingModule(
            config_manager=None,
            ai_client_factory=None,
            window_monitor=mock_window_monitor,
            state_manager=None
        )
        formatting_module.config = formatting_config
        
        # Create mock config with post-processing enabled
        mock_config = Mock()
        mock_config.enable_post_processing = True
        mock_config.post_processing_provider = "groq"
        mock_config.post_processing_model = "post-model"
        mock_config.post_processing_custom_model = ""
        mock_config.post_processing_prompt = "Post-process this text"
        mock_config.llm_base_url = None
        mock_config.glm_use_coding_plan = False
        
        # Create mock transcription client
        mock_transcription_client = Mock()
        mock_transcription_client.post_process_text.return_value = "COMBINED RESULT"
        
        # Create coordinator
        coordinator = ProcessingCoordinator(
            formatting_module=formatting_module,
            config_manager=mock_config
        )
        
        # Process text
        result = coordinator.process_transcription(
            text="Original text",
            transcription_client=mock_transcription_client,
            config=mock_config
        )
        
        # Verify combined processing was applied
        assert result == "COMBINED RESULT"
        
        # Verify exactly one API call was made
        assert mock_transcription_client.post_process_text.call_count == 1
        
        # Verify the combined prompt was used
        call_args = mock_transcription_client.post_process_text.call_args
        used_prompt = call_args[1]['system_prompt']
        
        # Combined prompt should contain both post-processing and formatting instructions
        assert "Post-process this text" in used_prompt
        assert len(used_prompt) > len("Post-process this text")
    
    def test_post_processing_only_pipeline_no_format_match(self):
        """
        Test combined processing with fallback formatting (no format match).
        
        When both post-processing and formatting are enabled, but the active
        application doesn't match any configured format, the system should
        use fallback formatting combined with post-processing.
        
        **Validates: Requirements 5.6**
        """
        # Create formatting config
        formatting_config = FormattingConfig(
            enabled=True,
            provider="groq",
            model="formatting-model",
            applications=["notion", "obsidian", "markdown"]
        )
        
        # Create mock window monitor with NON-matching app
        mock_window_monitor = Mock()
        mock_window_monitor.get_active_window_info.return_value = WindowInfo(
            title="Unknown App",
            process_name="unknown_app",
            icon=None,
            process_id=1234
        )
        
        # Create formatting module
        formatting_module = FormattingModule(
            config_manager=None,
            ai_client_factory=None,
            window_monitor=mock_window_monitor,
            state_manager=None
        )
        formatting_module.config = formatting_config
        
        # Create mock config with post-processing enabled
        mock_config = Mock()
        mock_config.enable_post_processing = True
        mock_config.post_processing_provider = "groq"
        mock_config.post_processing_model = "post-model"
        mock_config.post_processing_custom_model = ""
        mock_config.post_processing_prompt = "Post-process this text"
        mock_config.llm_base_url = None
        mock_config.glm_use_coding_plan = False
        
        # Create mock transcription client
        mock_transcription_client = Mock()
        mock_transcription_client.post_process_text.return_value = "POST-PROCESSED TEXT"
        
        # Create coordinator
        coordinator = ProcessingCoordinator(
            formatting_module=formatting_module,
            config_manager=mock_config
        )
        
        # Process text
        result = coordinator.process_transcription(
            text="Original text",
            transcription_client=mock_transcription_client,
            config=mock_config
        )
        
        # Verify combined processing was applied
        assert result == "POST-PROCESSED TEXT"
        
        # Verify post-processing was called
        assert mock_transcription_client.post_process_text.called
        
        # Verify the prompt CONTAINS both post-processing AND fallback formatting
        call_args = mock_transcription_client.post_process_text.call_args
        used_prompt = call_args[1]['system_prompt']
        assert "Post-process this text" in used_prompt
        assert "Additionally, apply the following formatting:" in used_prompt
        assert "Make the transcribed text readable and well-structured" in used_prompt
    
    def test_disabled_state_no_processing(self):
        """
        Test disabled state (no processing).
        
        **Validates: Requirements 4.1**
        """
        # Create formatting config with formatting disabled
        formatting_config = FormattingConfig(
            enabled=False,
            provider="groq",
            model="test-model",
            applications=["notion", "obsidian", "markdown"]
        )
        
        # Create mock window monitor
        mock_window_monitor = Mock()
        mock_window_monitor.get_active_window_info.return_value = WindowInfo(
            title="test.md",
            process_name="vscode",
            icon=None,
            process_id=1234
        )
        
        # Create formatting module
        formatting_module = FormattingModule(
            config_manager=None,
            ai_client_factory=None,
            window_monitor=mock_window_monitor,
            state_manager=None
        )
        formatting_module.config = formatting_config
        
        # Create mock config with post-processing disabled
        mock_config = Mock()
        mock_config.enable_post_processing = False
        
        # Create mock transcription client
        mock_transcription_client = Mock()
        
        # Create coordinator
        coordinator = ProcessingCoordinator(
            formatting_module=formatting_module,
            config_manager=mock_config
        )
        
        # Process text
        original_text = "Original text"
        result = coordinator.process_transcription(
            text=original_text,
            transcription_client=mock_transcription_client,
            config=mock_config
        )
        
        # Verify original text is returned unchanged
        assert result == original_text
        
        # Verify no API calls were made
        assert not mock_transcription_client.post_process_text.called
    
    def test_formatting_only_no_match_returns_original(self):
        """
        Test formatting-only with no format match applies fallback formatting.
        
        When formatting is enabled but the active application doesn't match
        any configured format, the system should apply fallback formatting.
        
        **Validates: Requirements 4.4**
        """
        # Create formatting config
        formatting_config = FormattingConfig(
            enabled=True,
            provider="groq",
            model="test-model",
            applications=["notion", "obsidian", "markdown"]
        )
        
        # Create mock window monitor with NON-matching app
        mock_window_monitor = Mock()
        mock_window_monitor.get_active_window_info.return_value = WindowInfo(
            title="Unknown App",
            process_name="unknown_app",
            icon=None,
            process_id=1234
        )
        
        # Create formatting module
        formatting_module = FormattingModule(
            config_manager=None,
            ai_client_factory=None,
            window_monitor=mock_window_monitor,
            state_manager=None
        )
        formatting_module.config = formatting_config
        
        # Create mock config with post-processing disabled
        mock_config = Mock()
        mock_config.enable_post_processing = False
        
        # Create mock transcription client
        mock_transcription_client = Mock()
        mock_transcription_client.post_process_text.return_value = "FALLBACK FORMATTED TEXT"
        
        # Create coordinator
        coordinator = ProcessingCoordinator(
            formatting_module=formatting_module,
            config_manager=mock_config
        )
        
        # Process text
        original_text = "Original text"
        result = coordinator.process_transcription(
            text=original_text,
            transcription_client=mock_transcription_client,
            config=mock_config
        )
        
        # Verify fallback formatting was applied
        assert result == "FALLBACK FORMATTED TEXT"
        
        # Verify API call was made with fallback prompt
        assert mock_transcription_client.post_process_text.called
        call_args = mock_transcription_client.post_process_text.call_args
        used_prompt = call_args[1]['system_prompt']
        assert "Make the transcribed text readable and well-structured" in used_prompt
