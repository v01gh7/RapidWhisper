"""
Linux Window Monitor Module

Provides Linux-specific implementation for monitoring active windows using X11/Wayland.
"""

import logging
import subprocess
from typing import Optional, Dict, Callable
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap, QIcon

from services.window_monitor import WindowMonitor, WindowInfo

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class LinuxWindowMonitor(WindowMonitor):
    """Linux implementation of window monitoring using wmctrl and xdotool"""
    
    def __init__(self):
        """Initialize the Linux window monitor"""
        self._timer: Optional[QTimer] = None
        self._callback: Optional[Callable[[WindowInfo], None]] = None
        self._icon_cache: Dict[str, QPixmap] = {}
        self._last_window_title: Optional[str] = None
        self._last_process_name: Optional[str] = None
        self._cache_max_size = 50
        self._cache_access_count: Dict[str, int] = {}
        self._logger = logging.getLogger(__name__)
        
        # Check if required tools are available
        self._has_xdotool = self._check_command('xdotool')
        self._has_wmctrl = self._check_command('wmctrl')
        
        if not (self._has_xdotool or self._has_wmctrl):
            self._logger.warning(
                "Neither xdotool nor wmctrl found. Window monitoring may not work properly. "
                "Install with: sudo apt-get install xdotool wmctrl"
            )
    
    def _check_command(self, command: str) -> bool:
        """Check if a command is available"""
        try:
            subprocess.run(
                ['which', command],
                capture_output=True,
                check=True,
                timeout=1
            )
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def get_active_window_info(self) -> Optional[WindowInfo]:
        """
        Get information about the current active window via Linux tools.
        
        Returns:
            WindowInfo if window is found, None on error
        """
        try:
            # Get window ID
            window_id = self._get_active_window_id()
            if not window_id:
                return None
            
            # Get window title
            title = self._get_window_title(window_id)
            if not title:
                title = "Unknown Window"
            
            # Get process ID
            process_id = self._get_window_pid(window_id)
            
            # Get process name
            process_name = self._get_process_name(process_id)
            
            # Get icon
            icon = self._get_app_icon(process_name, process_id)
            
            return WindowInfo(
                title=title,
                process_name=process_name,
                icon=icon,
                process_id=process_id
            )
        
        except Exception as e:
            self._logger.error(f"Error getting window info: {e}")
            return None
    
    def _get_active_window_id(self) -> Optional[str]:
        """Get the ID of the active window"""
        try:
            if self._has_xdotool:
                result = subprocess.run(
                    ['xdotool', 'getactivewindow'],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            
            elif self._has_wmctrl:
                result = subprocess.run(
                    ['wmctrl', '-l'],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                if result.returncode == 0:
                    # Parse wmctrl output to find active window
                    # This is a simplified approach
                    lines = result.stdout.strip().split('\n')
                    if lines:
                        # Return first window ID (not perfect but works)
                        return lines[0].split()[0]
        
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self._logger.warning(f"Error getting active window ID: {e}")
        
        return None
    
    def _get_window_title(self, window_id: str) -> Optional[str]:
        """Get window title by window ID"""
        try:
            if self._has_xdotool:
                result = subprocess.run(
                    ['xdotool', 'getwindowname', window_id],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                if result.returncode == 0:
                    return result.stdout.strip()
        
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self._logger.warning(f"Error getting window title: {e}")
        
        return None
    
    def _get_window_pid(self, window_id: str) -> int:
        """Get process ID by window ID"""
        try:
            if self._has_xdotool:
                result = subprocess.run(
                    ['xdotool', 'getwindowpid', window_id],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                if result.returncode == 0:
                    return int(result.stdout.strip())
        
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError) as e:
            self._logger.warning(f"Error getting window PID: {e}")
        
        return 0
    
    def _get_process_name(self, process_id: int) -> str:
        """Get process name by process ID"""
        if not PSUTIL_AVAILABLE or process_id == 0:
            return "Unknown Process"
        
        try:
            process = psutil.Process(process_id)
            return process.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return "Unknown Process"
    
    def _get_app_icon(self, process_name: str, process_id: int) -> Optional[QPixmap]:
        """
        Get application icon with caching.
        
        Args:
            process_name: Application name
            process_id: Process ID
            
        Returns:
            QPixmap icon or None
        """
        # Check cache
        cache_key = f"{process_name}_{process_id}"
        if cache_key in self._icon_cache:
            self._cache_access_count[cache_key] += 1
            return self._icon_cache[cache_key]
        
        try:
            # Try to get icon from Qt icon theme
            icon = QIcon.fromTheme(process_name.lower())
            if not icon.isNull():
                pixmap = icon.pixmap(32, 32)
                if not pixmap.isNull():
                    self._cache_icon(cache_key, pixmap)
                    return pixmap
        
        except Exception as e:
            self._logger.warning(f"Error getting app icon: {e}")
        
        return None
    
    def _cache_icon(self, cache_key: str, icon: QPixmap) -> None:
        """
        Cache icon with LRU management.
        
        Args:
            cache_key: Cache key
            icon: Icon to cache
        """
        # Check cache size
        if len(self._icon_cache) >= self._cache_max_size:
            # Remove least used icon
            least_used = min(
                self._cache_access_count.items(),
                key=lambda x: x[1]
            )[0]
            del self._icon_cache[least_used]
            del self._cache_access_count[least_used]
        
        self._icon_cache[cache_key] = icon
        self._cache_access_count[cache_key] = 1
    
    def start_monitoring(self, callback: Callable[[WindowInfo], None]) -> None:
        """
        Start monitoring with 200ms interval.
        
        Args:
            callback: Function to call when active window changes
        """
        self._callback = callback
        self._timer = QTimer()
        self._timer.timeout.connect(self._check_active_window)
        self._timer.start(200)  # 200ms interval
    
    def _check_active_window(self) -> None:
        """Check active window and call callback on change"""
        try:
            window_info = self.get_active_window_info()
            
            if not window_info:
                return
            
            # Check if window changed
            if (window_info.title != self._last_window_title or
                window_info.process_name != self._last_process_name):
                
                self._last_window_title = window_info.title
                self._last_process_name = window_info.process_name
                
                if self._callback:
                    self._callback(window_info)
        
        except Exception as e:
            self._logger.error(f"Error checking active window: {e}")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring"""
        if self._timer:
            self._timer.stop()
            self._timer = None
        self._callback = None
