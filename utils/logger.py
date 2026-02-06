"""
Logging utilities for RapidWhisper application.

Provides centralized logging configuration and error logging functionality.
"""

import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


MAX_LOG_BYTES = 5 * 1024 * 1024  # 5 MB


def rotate_file_if_too_large(path: Path, max_bytes: int = MAX_LOG_BYTES) -> None:
    """
    Delete log file if it exceeds max size.
    """
    try:
        if path.exists() and path.stat().st_size > max_bytes:
            path.unlink()
    except Exception:
        # Avoid raising during logging setup
        pass


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
        # Get configuration from config.jsonc or use defaults
        try:
            from core.config_loader import get_config_loader
            config_loader = get_config_loader()
            log_level = config_loader.get('logging.level', 'INFO').upper()
            log_file = config_loader.get('logging.file', 'rapidwhisper.log')
        except:
            # Fallback to defaults if config not available
            log_level = 'INFO'
            log_file = 'rapidwhisper.log'
        
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
            log_path = Path(log_file)
            rotate_file_if_too_large(log_path)
            self._log_path = log_path
            self._last_rotate_check = 0.0
            self._file_formatter = detailed_formatter
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(file_handler)
            self._file_handler = file_handler
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
        self._maybe_rotate_log()
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._maybe_rotate_log()
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._maybe_rotate_log()
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._maybe_rotate_log()
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._maybe_rotate_log()
        self.logger.critical(message, extra=kwargs)

    def _maybe_rotate_log(self) -> None:
        try:
            log_path = getattr(self, "_log_path", None)
            if not log_path:
                return
            now = time.time()
            last_check = getattr(self, "_last_rotate_check", 0.0)
            if now - last_check < 60.0:
                return
            self._last_rotate_check = now
            if Path(log_path).exists() and Path(log_path).stat().st_size > MAX_LOG_BYTES:
                self._rotate_log_file()
        except Exception:
            pass

    def _rotate_log_file(self) -> None:
        try:
            log_path = getattr(self, "_log_path", None)
            if not log_path:
                return
            file_handler = getattr(self, "_file_handler", None)
            if file_handler:
                self.logger.removeHandler(file_handler)
                file_handler.close()
            rotate_file_if_too_large(Path(log_path))
            formatter = getattr(self, "_file_formatter", None)
            new_handler = logging.FileHandler(Path(log_path), encoding='utf-8')
            new_handler.setLevel(logging.DEBUG)
            if formatter:
                new_handler.setFormatter(formatter)
            self.logger.addHandler(new_handler)
            self._file_handler = new_handler
        except Exception:
            pass
    
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


_hooks_logger_instance: Optional[logging.Logger] = None


def get_hooks_logger() -> logging.Logger:
    """
    Get a dedicated hooks logger that writes to hooks.log.
    """
    global _hooks_logger_instance
    if _hooks_logger_instance is None:
        try:
            from core.config_loader import get_config_loader
            config_loader = get_config_loader()
            log_file = config_loader.get('logging.file', 'rapidwhisper.log')
        except:
            log_file = 'rapidwhisper.log'

        hooks_log_path = Path(log_file).with_name("hooks.log")
        rotate_file_if_too_large(hooks_log_path)

        logger = logging.getLogger('RapidWhisperHooks')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            try:
                file_handler = logging.FileHandler(hooks_log_path, encoding='utf-8')
                file_handler.setLevel(logging.INFO)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
                logger.file_handler = file_handler
                logger.file_formatter = formatter
            except Exception as e:
                print(f"Warning: Could not create hooks log file: {e}")
        logger.log_path = hooks_log_path

        _hooks_logger_instance = logger
    return _hooks_logger_instance


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


# ============================================================================
# ErrorLogger - Специализированный логгер для ошибок
# ============================================================================

class ErrorLogger:
    """
    Специализированный логгер для обработки и записи ошибок.
    
    Предоставляет удобный интерфейс для логирования ошибок с контекстом,
    автоматической категоризацией и форматированием. Использует глобальный
    RapidWhisperLogger для фактической записи в лог.
    """
    
    def __init__(self, log_path: str = "rapidwhisper.log"):
        """
        Инициализирует ErrorLogger.
        
        Args:
            log_path: Путь к файлу логов (по умолчанию rapidwhisper.log)
        """
        self.log_path = log_path
        self.logger = get_logger()
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """
        Логирует ошибку с дополнительной контекстной информацией.
        
        Записывает детальную информацию об ошибке включая:
        - Тип исключения
        - Сообщение об ошибке
        - Временную метку
        - Контекстную информацию (если предоставлена)
        - Полный traceback
        
        Args:
            error: Исключение для логирования
            context: Опциональный словарь с дополнительной контекстной информацией
                    (например, текущее состояние приложения, параметры запроса)
        
        Example:
            >>> error_logger = ErrorLogger()
            >>> try:
            ...     # some code
            ... except Exception as e:
            ...     error_logger.log_error(e, {'state': 'RECORDING', 'duration': 5.2})
        """
        # Используем существующий метод log_error из RapidWhisperLogger
        self.logger.log_error(error, context)
        
        # Дополнительно логируем user-friendly сообщение если это RapidWhisperError
        try:
            from utils.exceptions import RapidWhisperError
            if isinstance(error, RapidWhisperError):
                self.logger.info(f"User message: {error.user_message}")
        except ImportError:
            pass
    
    def log_audio_error(self, error: Exception, audio_details: Optional[Dict[str, Any]] = None):
        """
        Логирует ошибку, связанную с аудио подсистемой.
        
        Args:
            error: Исключение аудио подсистемы
            audio_details: Детали аудио (sample_rate, duration, buffer_size и т.д.)
        """
        context = {'category': 'audio'}
        if audio_details:
            context.update(audio_details)
        self.log_error(error, context)
    
    def log_api_error(self, error: Exception, api_details: Optional[Dict[str, Any]] = None):
        """
        Логирует ошибку, связанную с API запросом.
        
        Args:
            error: Исключение API
            api_details: Детали запроса (endpoint, method, duration и т.д.)
        """
        context = {'category': 'api'}
        if api_details:
            context.update(api_details)
        self.log_error(error, context)
    
    def log_config_error(self, error: Exception, config_details: Optional[Dict[str, Any]] = None):
        """
        Логирует ошибку конфигурации.
        
        Args:
            error: Исключение конфигурации
            config_details: Детали конфигурации (параметр, значение и т.д.)
        """
        context = {'category': 'configuration'}
        if config_details:
            context.update(config_details)
        self.log_error(error, context)
