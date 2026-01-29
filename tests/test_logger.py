"""
Basic tests for the logging infrastructure.
"""

import os
import tempfile
from pathlib import Path
import pytest
from utils.logger import get_logger, RapidWhisperLogger


def test_logger_singleton():
    """Test that logger follows singleton pattern."""
    logger1 = get_logger()
    logger2 = get_logger()
    assert logger1 is logger2


def test_logger_initialization():
    """Test that logger initializes correctly."""
    logger = get_logger()
    assert logger.logger is not None
    assert logger.logger.name == 'RapidWhisper'


def test_logger_basic_logging():
    """Test basic logging methods."""
    logger = get_logger()
    
    # These should not raise exceptions
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")


def test_logger_error_with_context():
    """Test error logging with context."""
    logger = get_logger()
    
    try:
        raise ValueError("Test error")
    except ValueError as e:
        # Should not raise exception
        logger.log_error(e, context={'test': 'value'})


def test_logger_state_transition():
    """Test state transition logging."""
    logger = get_logger()
    logger.log_state_transition("IDLE", "RECORDING", "Hotkey pressed")


def test_logger_api_request():
    """Test API request logging."""
    logger = get_logger()
    logger.log_api_request("/api/transcribe", 1.5, True)
    logger.log_api_request("/api/transcribe", 2.0, False)


def test_logger_audio_event():
    """Test audio event logging."""
    logger = get_logger()
    logger.log_audio_event("recording_started")
    logger.log_audio_event("silence_detected", {"duration": 1.5})
