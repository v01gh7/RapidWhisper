"""
Window Monitor Module

Provides abstract interface and factory for monitoring active windows across platforms.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Callable
import platform
from PyQt6.QtGui import QPixmap


@dataclass
class WindowInfo:
    """Information about an active window"""
    title: str
    process_name: str
    icon: Optional[QPixmap]
    process_id: int


class WindowMonitor(ABC):
    """Abstract base class for monitoring active windows"""
    
    @abstractmethod
    def get_active_window_info(self) -> Optional[WindowInfo]:
        """
        Get information about the current active window.
        
        Returns:
            WindowInfo if window is found, None on error
        """
        pass
    
    @abstractmethod
    def start_monitoring(self, callback: Callable[[WindowInfo], None]) -> None:
        """
        Start monitoring the active window.
        
        Args:
            callback: Function to call when active window changes
        """
        pass
    
    @abstractmethod
    def stop_monitoring(self) -> None:
        """Stop monitoring the active window"""
        pass
    
    @staticmethod
    def create() -> 'WindowMonitor':
        """
        Factory method to create appropriate WindowMonitor implementation.
        
        Returns:
            WindowMonitor instance for the current platform
            
        Raises:
            NotImplementedError: If platform is not supported
        """
        system = platform.system()
        
        if system == "Windows":
            from services.windows_window_monitor import WindowsWindowMonitor
            return WindowsWindowMonitor()
        else:
            raise NotImplementedError(f"Unsupported platform: {system}")
