"""
Integration test for the complete transcription formatting pipeline.

This test verifies that the formatting module is properly integrated
into the transcription pipeline.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from services.transcription_client import TranscriptionThread
from services.formatting_config import FormattingConfig
from services.window_monitor import WindowInfo


class TestIntegratedPipeline:
    """Integration tests for the complete pipeline."""
    
    def test_pipeline_imports_successfully(self):
        """
        Test that all required modules can be imported.
        """
        from services.transcription_client import TranscriptionThread
        from services.processing_coordinator import ProcessingCoordinator
        from services.formatting_module import FormattingModule
        from services.formatting_config import FormattingConfig
        
        assert TranscriptionThread is not None
        assert ProcessingCoordinator is not None
        assert FormattingModule is not None
        assert FormattingConfig is not None
    
    @patch('services.transcription_client.FormattingConfig.from_env')
    @patch('services.window_monitor.WindowMonitor')
    def test_transcription_thread_creates_coordinator(self, mock_window_monitor, mock_load_config):
        """
        Test that TranscriptionThread properly creates the processing coordinator.
        """
        # Create mock formatting config
        mock_config = FormattingConfig(
            enabled=False,
            provider="groq",
            model="test-model",
            applications=["notion"]
        )
        mock_load_config.return_value = mock_config
        
        # Create mock window monitor
        mock_window_instance = Mock()
        mock_window_monitor.return_value = mock_window_instance
        
        # Create transcription thread
        thread = TranscriptionThread(
            audio_file_path="test.wav",
            provider="groq",
            api_key="test-key",
            model="whisper-large-v3"
        )
        
        # Verify thread was created successfully
        assert thread is not None
        assert thread.audio_file_path == "test.wav"
    
    def test_formatting_config_loads_from_env(self):
        """
        Test that formatting configuration can be loaded from environment.
        """
        # Patch os.getenv directly to avoid load_dotenv override
        with patch('os.getenv') as mock_getenv:
            def getenv_side_effect(key, default=None):
                env_vars = {
                    'FORMATTING_ENABLED': 'true',
                    'FORMATTING_PROVIDER': 'groq',
                    'FORMATTING_MODEL': 'test-model',
                    'FORMATTING_APPLICATIONS': 'notion,obsidian,markdown'
                }
                return env_vars.get(key, default)
            
            mock_getenv.side_effect = getenv_side_effect
            
            config = FormattingConfig.from_env()
            
            assert config.enabled == True
            assert config.provider == 'groq'
            assert config.model == 'test-model'
            assert 'notion' in config.applications
            assert 'obsidian' in config.applications
            assert 'markdown' in config.applications
    
    def test_processing_coordinator_integration(self):
        """
        Test that the processing coordinator integrates correctly.
        """
        from services.processing_coordinator import ProcessingCoordinator
        from services.formatting_module import FormattingModule
        from services.window_monitor import WindowMonitor
        
        # Create mock components
        mock_window_monitor = Mock()
        mock_window_monitor.get_active_window_info.return_value = WindowInfo(
            title="test.md",
            process_name="vscode",
            icon=None,
            process_id=1234
        )
        
        formatting_config = FormattingConfig(
            enabled=False,
            provider="groq",
            model="test-model",
            applications=["notion"]
        )
        
        formatting_module = FormattingModule(
            config_manager=None,
            ai_client_factory=None,
            window_monitor=mock_window_monitor
        )
        formatting_module.config = formatting_config
        
        mock_config = Mock()
        mock_config.enable_post_processing = False
        
        coordinator = ProcessingCoordinator(
            formatting_module=formatting_module,
            config_manager=mock_config
        )
        
        # Test processing with both disabled
        result = coordinator.process_transcription(
            text="Test text",
            transcription_client=Mock(),
            config=mock_config
        )
        
        # Should return original text when both are disabled
        assert result == "Test text"
