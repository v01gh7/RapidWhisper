"""
Utils module for RapidWhisper application.

Contains utility functions, logging, and platform-specific helpers.
"""

from utils.logger import get_logger
from utils.exceptions import (
    RapidWhisperError,
    MicrophoneUnavailableError,
    RecordingTooShortError,
    EmptyRecordingError,
    AudioDeviceError,
    InvalidAPIKeyError,
    APIConnectionError
)
from utils.platform_utils import get_platform_info, is_windows, is_macos, is_linux
from utils.single_instance import SingleInstance

__all__ = [
    'get_logger',
    'RapidWhisperError',
    'MicrophoneUnavailableError',
    'RecordingTooShortError',
    'EmptyRecordingError',
    'AudioDeviceError',
    'InvalidAPIKeyError',
    'APIConnectionError',
    'get_platform_info',
    'is_windows',
    'is_macos',
    'is_linux',
    'SingleInstance'
]
