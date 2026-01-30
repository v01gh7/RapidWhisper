"""Integration tests for silence removal statistics tracking.

This module tests the integration between the silence removal functionality
and the statistics manager to ensure that removed silence durations are
properly tracked.
"""

import pytest
import tempfile
import wave
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch

from core.statistics_manager import StatisticsManager, TimePeriod, EventType
from services.transcription_client import TranscriptionThread
from utils.audio_utils import trim_silence


class TestSilenceRemovalStatisticsIntegration:
    """Test suite for silence removal statistics integration."""
    
    def test_trim_silence_returns_removed_duration(self, tmp_path):
        """Test that trim_silence returns both file path and removed duration.
        
        **Validates: Requirements 3.1, 3.2**
        """
        # Create a test audio file with silence
        audio_file = tmp_path / "test_audio.wav"
        
        # Create audio with silence at beginning and end
        sample_rate = 16000
        duration = 3.0  # 3 seconds total
        
        # 1 second of silence, 1 second of sound, 1 second of silence
        silence_samples = int(sample_rate * 1.0)
        sound_samples = int(sample_rate * 1.0)
        
        silence = np.zeros(silence_samples, dtype=np.int16)
        sound = (np.random.random(sound_samples) * 10000).astype(np.int16)
        
        audio_data = np.concatenate([silence, sound, silence])
        
        # Write to WAV file
        with wave.open(str(audio_file), 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())
        
        # Call trim_silence
        result_path, removed_duration = trim_silence(str(audio_file))
        
        # Verify return values
        assert result_path == str(audio_file)
        assert removed_duration > 0.0
        # Should have removed approximately 2 seconds (beginning and end silence)
        # Allow some tolerance due to padding
        assert 1.0 < removed_duration < 2.5
    
    def test_trim_silence_no_silence_returns_zero(self, tmp_path):
        """Test that trim_silence returns 0 duration when no silence is removed.
        
        **Validates: Requirements 3.1, 3.2**
        """
        # Create a test audio file with no silence (all sound)
        audio_file = tmp_path / "test_audio_no_silence.wav"
        
        sample_rate = 16000
        duration = 2.0
        samples = int(sample_rate * duration)
        
        # All sound, no silence
        audio_data = (np.random.random(samples) * 10000).astype(np.int16)
        
        # Write to WAV file
        with wave.open(str(audio_file), 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())
        
        # Call trim_silence
        result_path, removed_duration = trim_silence(str(audio_file))
        
        # Verify return values
        assert result_path == str(audio_file)
        # Should be very small or zero since there's no silence
        assert removed_duration < 0.5
    
    def test_transcription_thread_tracks_silence_removal(self, tmp_path):
        """Test that TranscriptionThread tracks silence removal statistics.
        
        **Validates: Requirements 3.1, 3.2**
        """
        # Create statistics manager
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        statistics_manager = StatisticsManager(config_dir)
        
        # Create a test audio file with silence
        audio_file = tmp_path / "test_audio.wav"
        sample_rate = 16000
        
        # 1 second of silence, 1 second of sound, 1 second of silence
        silence_samples = int(sample_rate * 1.0)
        sound_samples = int(sample_rate * 1.0)
        
        silence = np.zeros(silence_samples, dtype=np.int16)
        sound = (np.random.random(sound_samples) * 10000).astype(np.int16)
        
        audio_data = np.concatenate([silence, sound, silence])
        
        # Write to WAV file
        with wave.open(str(audio_file), 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())
        
        # Mock the config to enable manual_stop
        with patch('core.config.Config') as MockConfig:
            mock_config = Mock()
            mock_config.manual_stop = True
            mock_config.silence_threshold = 0.02
            mock_config.silence_padding = 300
            mock_config.enable_post_processing = False
            MockConfig.load_from_env.return_value = mock_config
            
            # Mock the transcription client to avoid actual API calls
            with patch('services.transcription_client.TranscriptionClient') as MockClient:
                mock_client_instance = Mock()
                mock_client_instance.transcribe_audio.return_value = "Test transcription"
                MockClient.return_value = mock_client_instance
                
                # Create TranscriptionThread with statistics_manager
                thread = TranscriptionThread(
                    str(audio_file),
                    provider="openai",
                    api_key="test_key",
                    statistics_manager=statistics_manager
                )
                
                # Run the thread synchronously for testing
                thread.run()
        
        # Verify that silence removal was tracked
        stats = statistics_manager.get_statistics(TimePeriod.ALL_TIME)
        assert stats.total_removed_silence_seconds > 0.0
        
        # Verify that an event was created
        assert len(statistics_manager.events) > 0
        silence_events = [e for e in statistics_manager.events if e.type == EventType.SILENCE_REMOVED]
        assert len(silence_events) == 1
        assert silence_events[0].removed_duration_seconds > 0.0
    
    def test_transcription_thread_without_statistics_manager(self, tmp_path):
        """Test that TranscriptionThread works without statistics_manager.
        
        **Validates: Requirements 3.1, 3.2**
        """
        # Create a test audio file
        audio_file = tmp_path / "test_audio.wav"
        sample_rate = 16000
        duration = 1.0
        samples = int(sample_rate * duration)
        audio_data = (np.random.random(samples) * 10000).astype(np.int16)
        
        # Write to WAV file
        with wave.open(str(audio_file), 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())
        
        # Mock the config to enable manual_stop
        with patch('core.config.Config') as MockConfig:
            mock_config = Mock()
            mock_config.manual_stop = True
            mock_config.silence_threshold = 0.02
            mock_config.silence_padding = 300
            mock_config.enable_post_processing = False
            MockConfig.load_from_env.return_value = mock_config
            
            # Mock the transcription client
            with patch('services.transcription_client.TranscriptionClient') as MockClient:
                mock_client_instance = Mock()
                mock_client_instance.transcribe_audio.return_value = "Test transcription"
                MockClient.return_value = mock_client_instance
                
                # Create TranscriptionThread WITHOUT statistics_manager
                thread = TranscriptionThread(
                    str(audio_file),
                    provider="openai",
                    api_key="test_key",
                    statistics_manager=None
                )
                
                # Run the thread - should not crash
                thread.run()
        
        # Test passes if no exception was raised
        assert True
    
    def test_manual_stop_disabled_no_silence_tracking(self, tmp_path):
        """Test that silence removal is not tracked when manual_stop is disabled.
        
        **Validates: Requirements 3.1, 3.2**
        """
        # Create statistics manager
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        statistics_manager = StatisticsManager(config_dir)
        
        # Create a test audio file
        audio_file = tmp_path / "test_audio.wav"
        sample_rate = 16000
        duration = 1.0
        samples = int(sample_rate * duration)
        audio_data = (np.random.random(samples) * 10000).astype(np.int16)
        
        # Write to WAV file
        with wave.open(str(audio_file), 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())
        
        # Mock the config to DISABLE manual_stop
        with patch('core.config.Config') as MockConfig:
            mock_config = Mock()
            mock_config.manual_stop = False  # Disabled
            mock_config.enable_post_processing = False
            MockConfig.load_from_env.return_value = mock_config
            
            # Mock the transcription client
            with patch('services.transcription_client.TranscriptionClient') as MockClient:
                mock_client_instance = Mock()
                mock_client_instance.transcribe_audio.return_value = "Test transcription"
                MockClient.return_value = mock_client_instance
                
                # Create TranscriptionThread with statistics_manager
                thread = TranscriptionThread(
                    str(audio_file),
                    provider="openai",
                    api_key="test_key",
                    statistics_manager=statistics_manager
                )
                
                # Run the thread
                thread.run()
        
        # Verify that NO silence removal was tracked
        stats = statistics_manager.get_statistics(TimePeriod.ALL_TIME)
        assert stats.total_removed_silence_seconds == 0.0
        
        # Verify that no silence removal events were created
        silence_events = [e for e in statistics_manager.events if e.type == EventType.SILENCE_REMOVED]
        assert len(silence_events) == 0
