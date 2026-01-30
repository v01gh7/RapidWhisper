"""
Integration tests for transcription statistics tracking.

Tests that transcription completion properly tracks statistics.
"""

import pytest
import tempfile
import wave
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from main import RapidWhisperApp
from core.state_manager import AppState
from core.statistics_manager import StatisticsManager, TimePeriod


class TestTranscriptionStatisticsIntegration:
    """Tests for transcription statistics integration."""
    
    def create_test_wav_file(self, duration_seconds: float = 2.0) -> str:
        """
        Create a test WAV file with specified duration.
        
        Args:
            duration_seconds: Duration of the audio file in seconds
            
        Returns:
            Path to the created WAV file
        """
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        filepath = temp_file.name
        temp_file.close()
        
        # WAV parameters
        sample_rate = 16000
        channels = 1
        sample_width = 2  # 16-bit
        
        # Calculate number of frames
        num_frames = int(sample_rate * duration_seconds)
        
        # Create WAV file
        with wave.open(filepath, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            
            # Write silent audio data
            silent_data = b'\x00\x00' * num_frames
            wav_file.writeframes(silent_data)
        
        return filepath
    
    @patch('main.TrayIcon')
    @patch('main.FloatingWindow')
    @patch('main.Config.load_from_env')
    @patch('main.HotkeyManager')
    @patch('main.get_config_dir')
    def test_transcription_completion_tracks_statistics(
        self, 
        mock_get_config_dir,
        mock_hotkey_manager, 
        mock_config_load,
        mock_floating_window,
        mock_tray_icon
    ):
        """Test that transcription completion tracks statistics with correct data."""
        # Create temporary directory for statistics
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            mock_get_config_dir.return_value = temp_path
            
            # Setup mock config
            mock_config = Mock()
            mock_config.has_api_key.return_value = True
            mock_config.validate.return_value = []
            mock_config.ai_provider = "openai"
            mock_config.openai_api_key = "test_key"
            mock_config.hotkey = "ctrl+shift+space"
            mock_config.manual_stop = False
            mock_config.silence_threshold = 0.01
            mock_config.silence_duration = 2.0
            mock_config_load.return_value = mock_config
            
            # Mock UI components
            mock_floating_window.return_value = Mock()
            mock_tray_icon.return_value = Mock()
            
            # Create app
            app = RapidWhisperApp()
            app.initialize()
            
            # Create test WAV file with 3.5 seconds duration
            test_duration = 3.5
            test_file = self.create_test_wav_file(test_duration)
            
            try:
                # Set the audio file path (as would happen after recording)
                app._audio_file_path = test_file
                
                # Mock state_manager.on_transcription_complete to prevent UI updates
                app.state_manager.on_transcription_complete = Mock()
                
                # Test transcription text
                test_text = "This is a test transcription with multiple words."
                expected_char_count = len(test_text)
                expected_word_count = len(test_text.split())
                
                # Call _on_transcription_complete
                app._on_transcription_complete(test_text)
                
                # Verify statistics were tracked
                stats = app.statistics_manager.get_statistics(TimePeriod.ALL_TIME)
                
                assert stats.transcriptions_count == 1
                # Allow small tolerance for floating point comparison
                assert abs(stats.total_transcribed_audio_time_seconds - test_duration) < 0.01
                assert stats.total_character_count == expected_char_count
                assert stats.total_word_count == expected_word_count
                
            finally:
                # Cleanup test file
                Path(test_file).unlink(missing_ok=True)
    
    @patch('main.TrayIcon')
    @patch('main.FloatingWindow')
    @patch('main.Config.load_from_env')
    @patch('main.HotkeyManager')
    @patch('main.get_config_dir')
    def test_transcription_statistics_error_handling(
        self,
        mock_get_config_dir,
        mock_hotkey_manager, 
        mock_config_load,
        mock_floating_window,
        mock_tray_icon
    ):
        """Test that statistics tracking errors don't break transcription flow."""
        # Create temporary directory for statistics
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            mock_get_config_dir.return_value = temp_path
            
            # Setup mock config
            mock_config = Mock()
            mock_config.has_api_key.return_value = True
            mock_config.validate.return_value = []
            mock_config.ai_provider = "openai"
            mock_config.openai_api_key = "test_key"
            mock_config.hotkey = "ctrl+shift+space"
            mock_config.manual_stop = False
            mock_config.silence_threshold = 0.01
            mock_config.silence_duration = 2.0
            mock_config_load.return_value = mock_config
            
            # Mock UI components
            mock_floating_window.return_value = Mock()
            mock_tray_icon.return_value = Mock()
            
            # Create app
            app = RapidWhisperApp()
            app.initialize()
            
            # Set invalid audio file path
            app._audio_file_path = "/nonexistent/file.wav"
            
            # Mock state_manager.on_transcription_complete
            app.state_manager.on_transcription_complete = Mock()
            
            # Call with test text (should handle error gracefully)
            test_text = "Test transcription"
            app._on_transcription_complete(test_text)
            
            # Verify state manager still gets called despite statistics error
            app.state_manager.on_transcription_complete.assert_called_once_with(test_text)
    
    @patch('main.TrayIcon')
    @patch('main.FloatingWindow')
    @patch('main.Config.load_from_env')
    @patch('main.HotkeyManager')
    @patch('main.get_config_dir')
    def test_multiple_transcriptions_accumulate_statistics(
        self,
        mock_get_config_dir,
        mock_hotkey_manager, 
        mock_config_load,
        mock_floating_window,
        mock_tray_icon
    ):
        """Test that multiple transcriptions accumulate in statistics."""
        # Create temporary directory for statistics
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            mock_get_config_dir.return_value = temp_path
            
            # Setup mock config
            mock_config = Mock()
            mock_config.has_api_key.return_value = True
            mock_config.validate.return_value = []
            mock_config.ai_provider = "openai"
            mock_config.openai_api_key = "test_key"
            mock_config.hotkey = "ctrl+shift+space"
            mock_config.manual_stop = False
            mock_config.silence_threshold = 0.01
            mock_config.silence_duration = 2.0
            mock_config_load.return_value = mock_config
            
            # Mock UI components
            mock_floating_window.return_value = Mock()
            mock_tray_icon.return_value = Mock()
            
            # Create app
            app = RapidWhisperApp()
            app.initialize()
            
            # Mock state_manager.on_transcription_complete
            app.state_manager.on_transcription_complete = Mock()
            
            # Test data
            test_cases = [
                (1.5, "First transcription."),
                (2.0, "Second transcription with more words here."),
                (3.5, "Third transcription has even more words in this sentence.")
            ]
            
            test_files = []
            
            try:
                for duration, text in test_cases:
                    # Create test file
                    test_file = self.create_test_wav_file(duration)
                    test_files.append(test_file)
                    
                    # Set audio file path
                    app._audio_file_path = test_file
                    
                    # Call _on_transcription_complete
                    app._on_transcription_complete(text)
                
                # Verify accumulated statistics
                stats = app.statistics_manager.get_statistics(TimePeriod.ALL_TIME)
                
                assert stats.transcriptions_count == 3
                
                # Check total audio duration
                expected_total_duration = sum(d for d, _ in test_cases)
                assert abs(stats.total_transcribed_audio_time_seconds - expected_total_duration) < 0.01
                
                # Check total character count
                expected_total_chars = sum(len(t) for _, t in test_cases)
                assert stats.total_character_count == expected_total_chars
                
                # Check total word count
                expected_total_words = sum(len(t.split()) for _, t in test_cases)
                assert stats.total_word_count == expected_total_words
                
            finally:
                # Cleanup test files
                for test_file in test_files:
                    Path(test_file).unlink(missing_ok=True)
    
    @patch('main.TrayIcon')
    @patch('main.FloatingWindow')
    @patch('main.Config.load_from_env')
    @patch('main.HotkeyManager')
    @patch('main.get_config_dir')
    def test_transcription_with_unicode_text(
        self,
        mock_get_config_dir,
        mock_hotkey_manager, 
        mock_config_load,
        mock_floating_window,
        mock_tray_icon
    ):
        """Test that transcription statistics handle Unicode text correctly."""
        # Create temporary directory for statistics
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            mock_get_config_dir.return_value = temp_path
            
            # Setup mock config
            mock_config = Mock()
            mock_config.has_api_key.return_value = True
            mock_config.validate.return_value = []
            mock_config.ai_provider = "openai"
            mock_config.openai_api_key = "test_key"
            mock_config.hotkey = "ctrl+shift+space"
            mock_config.manual_stop = False
            mock_config.silence_threshold = 0.01
            mock_config.silence_duration = 2.0
            mock_config_load.return_value = mock_config
            
            # Mock UI components
            mock_floating_window.return_value = Mock()
            mock_tray_icon.return_value = Mock()
            
            # Create app
            app = RapidWhisperApp()
            app.initialize()
            
            # Create test WAV file
            test_duration = 2.0
            test_file = self.create_test_wav_file(test_duration)
            
            try:
                # Set the audio file path
                app._audio_file_path = test_file
                
                # Mock state_manager.on_transcription_complete
                app.state_manager.on_transcription_complete = Mock()
                
                # Test with Unicode text (Russian, emoji, Chinese)
                test_text = "Привет мир! 你好世界 🌍 Hello world!"
                expected_char_count = len(test_text)
                expected_word_count = len(test_text.split())
                
                # Call _on_transcription_complete
                app._on_transcription_complete(test_text)
                
                # Verify statistics were tracked correctly
                stats = app.statistics_manager.get_statistics(TimePeriod.ALL_TIME)
                
                assert stats.transcriptions_count == 1
                assert stats.total_character_count == expected_char_count
                assert stats.total_word_count == expected_word_count
                
            finally:
                # Cleanup test file
                Path(test_file).unlink(missing_ok=True)
