"""
Integration tests for recording statistics tracking.

Tests that recording completion properly tracks statistics.
"""

import pytest
import tempfile
import wave
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from main import RapidWhisperApp
from core.state_manager import AppState
from core.statistics_manager import StatisticsManager, TimePeriod


class TestRecordingStatisticsIntegration:
    """Tests for recording statistics integration."""
    
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
    def test_recording_completion_tracks_statistics(
        self, 
        mock_get_config_dir,
        mock_hotkey_manager, 
        mock_config_load,
        mock_floating_window,
        mock_tray_icon
    ):
        """Test that recording completion tracks statistics with correct duration."""
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
            
            # Create test WAV file with 2.5 seconds duration
            test_duration = 2.5
            test_file = self.create_test_wav_file(test_duration)
            
            try:
                # Set state to PROCESSING (as would happen during recording stop)
                app.state_manager.transition_to(AppState.PROCESSING)
                
                # Mock _start_transcription to prevent actual transcription
                app._start_transcription = Mock()
                
                # Call _on_recording_stopped
                app._on_recording_stopped(test_file)
                
                # Verify statistics were tracked
                stats = app.statistics_manager.get_statistics(TimePeriod.ALL_TIME)
                
                assert stats.recordings_count == 1
                # Allow small tolerance for floating point comparison
                assert abs(stats.total_recording_time_seconds - test_duration) < 0.01
                
            finally:
                # Cleanup test file
                Path(test_file).unlink(missing_ok=True)
    
    @patch('main.TrayIcon')
    @patch('main.FloatingWindow')
    @patch('main.Config.load_from_env')
    @patch('main.HotkeyManager')
    @patch('main.get_config_dir')
    def test_recording_statistics_error_handling(
        self,
        mock_get_config_dir,
        mock_hotkey_manager, 
        mock_config_load,
        mock_floating_window,
        mock_tray_icon
    ):
        """Test that statistics tracking errors don't break recording flow."""
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
            
            # Set state to PROCESSING
            app.state_manager.transition_to(AppState.PROCESSING)
            
            # Mock _start_transcription
            app._start_transcription = Mock()
            
            # Call with invalid file path (should handle error gracefully)
            app._on_recording_stopped("/nonexistent/file.wav")
            
            # Verify transcription still starts despite statistics error
            app._start_transcription.assert_called_once()
    
    @patch('main.TrayIcon')
    @patch('main.FloatingWindow')
    @patch('main.Config.load_from_env')
    @patch('main.HotkeyManager')
    @patch('main.get_config_dir')
    def test_multiple_recordings_accumulate_statistics(
        self,
        mock_get_config_dir,
        mock_hotkey_manager, 
        mock_config_load,
        mock_floating_window,
        mock_tray_icon
    ):
        """Test that multiple recordings accumulate in statistics."""
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
            
            # Create test files with different durations
            durations = [1.5, 2.0, 3.5]
            test_files = []
            
            try:
                for duration in durations:
                    test_file = self.create_test_wav_file(duration)
                    test_files.append(test_file)
                    
                    # Set state to PROCESSING
                    app.state_manager.transition_to(AppState.PROCESSING)
                    
                    # Mock _start_transcription
                    app._start_transcription = Mock()
                    
                    # Call _on_recording_stopped
                    app._on_recording_stopped(test_file)
                    
                    # Reset to IDLE for next recording
                    app.state_manager.transition_to(AppState.IDLE)
                
                # Verify accumulated statistics
                stats = app.statistics_manager.get_statistics(TimePeriod.ALL_TIME)
                
                assert stats.recordings_count == 3
                expected_total = sum(durations)
                assert abs(stats.total_recording_time_seconds - expected_total) < 0.01
                
            finally:
                # Cleanup test files
                for test_file in test_files:
                    Path(test_file).unlink(missing_ok=True)
