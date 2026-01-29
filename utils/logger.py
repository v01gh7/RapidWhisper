"""
Logging utilities for RapidWhisper application.

Provides centralized logging configuration and error logging functionality.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class RapidWhisperLogger:
    """
    Centralized logger for RapidWhisper application.
    
    Provides structured logging with file and console handlers,
    automatic log rotation, and error tracking.
    """
    
    _instance: Optional['RapidWhisperLogger'] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern to ensure only one logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the logger (only once)."""
        if not self._initialized:
            self._setup_logger()
            RapidWhisperLogger._initialized = True
    
    def _setup_logger(self):
        """Configure the logging system."""
        # Get configuration from environment or use defaults
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        log_file = os.getenv('LOG_FILE', 'rapidwhisper.log')
        
        # Create logger
        self.logger = logging.getLogger('RapidWhisper')
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler - detailed logging
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not create log file: {e}")
        
        # Console handler - simpler logging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)
        
        self.logger.info("RapidWhisper logger initialized")
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(message, extra=kwargs)
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """
        Log an error with additional context information.
        
        Args:
            error: The exception that occurred
            context: Optional dictionary with additional context information
        """
        error_info = {
            'type': type(error).__name__,
            'message': str(error),
            'timestamp': datetime.now().isoformat(),
        }
        
        if context:
            error_info['context'] = context
        
        self.logger.error(
            f"Error occurred: {error_info['type']} - {error_info['message']}",
            exc_info=True,
            extra={'error_info': error_info}
        )
    
    def log_state_transition(self, from_state: str, to_state: str, reason: str = ""):
        """
        Log application state transitions.
        
        Args:
            from_state: Previous state
            to_state: New state
            reason: Optional reason for transition
        """
        message = f"State transition: {from_state} -> {to_state}"
        if reason:
            message += f" (Reason: {reason})"
        self.logger.info(message)
    
    def log_api_request(self, endpoint: str, duration: float, success: bool):
        """
        Log API request information.
        
        Args:
            endpoint: API endpoint called
            duration: Request duration in seconds
            success: Whether the request was successful
        """
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(
            f"API Request [{status}]: {endpoint} - Duration: {duration:.2f}s"
        )
    
    def log_audio_event(self, event: str, details: Optional[Dict[str, Any]] = None):
        """
        Log audio-related events.
        
        Args:
            event: Event description (e.g., "recording_started", "silence_detected")
            details: Optional dictionary with event details
        """
        message = f"Audio Event: {event}"
        if details:
            detail_str = ", ".join(f"{k}={v}" for k, v in details.items())
            message += f" ({detail_str})"
        self.logger.debug(message)


# Global logger instance
_logger_instance: Optional[RapidWhisperLogger] = None


def get_logger() -> RapidWhisperLogger:
    """
    Get the global logger instance.
    
    Returns:
        RapidWhisperLogger: The singleton logger instance
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = RapidWhisperLogger()
    return _logger_instance


# Convenience functions for direct logging
def debug(message: str, **kwargs):
    """Log debug message."""
    get_logger().debug(message, **kwargs)


def info(message: str, **kwargs):
    """Log info message."""
    get_logger().info(message, **kwargs)


def warning(message: str, **kwargs):
    """Log warning message."""
    get_logger().warning(message, **kwargs)


def error(message: str, **kwargs):
    """Log error message."""
    get_logger().error(message, **kwargs)


def critical(message: str, **kwargs):
    """Log critical message."""
    get_logger().critical(message, **kwargs)


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """Log an error with context."""
    get_logger().log_error(error, context)


def log_state_transition(from_state: str, to_state: str, reason: str = ""):
    """Log state transition."""
    get_logger().log_state_transition(from_state, to_state, reason)


def log_api_request(endpoint: str, duration: float, success: bool):
    """Log API request."""
    get_logger().log_api_request(endpoint, duration, success)


def log_audio_event(event: str, details: Optional[Dict[str, Any]] = None):
    """Log audio event."""
    get_logger().log_audio_event(event, details)
