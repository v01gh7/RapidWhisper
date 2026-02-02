"""
macOS Window Monitor Module

Provides macOS-specific implementation for monitoring active windows using AppKit.
"""

import logging
from typing import Optional, Dict, Callable
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap

from services.window_monitor import WindowMonitor, WindowInfo

try:
    from AppKit import NSWorkspace, NSRunningApplication
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID
    )
    MACOS_AVAILABLE = True
except ImportError:
    MACOS_AVAILABLE = False


class MacOSWindowMonitor(WindowMonitor):
    """macOS implementation of window monitoring using AppKit and Quartz"""
    
    def __init__(self):
        """Initialize the macOS window monitor"""
        if not MACOS_AVAILABLE:
            raise ImportError("macOS window monitoring requires AppKit and Quartz (pyobjc)")
        
        self._timer: Optional[QTimer] = None
        self._callback: Optional[Callable[[WindowInfo], None]] = None
        self._icon_cache: Dict[str, QPixmap] = {}
        self._last_window_title: Optional[str] = None
        self._last_process_name: Optional[str] = None
        self._cache_max_size = 50
        self._cache_access_count: Dict[str, int] = {}
        self._logger = logging.getLogger(__name__)
        self._workspace = NSWorkspace.sharedWorkspace()
    
    def get_active_window_info(self) -> Optional[WindowInfo]:
        """
        Get information about the current active window via macOS APIs.
        
        Returns:
            WindowInfo if window is found, None on error
        """
        try:
            # Get active application
            active_app = self._workspace.activeApplication()
            if not active_app:
                return None
            
            # Get process name
            process_name = active_app.get('NSApplicationName', 'Unknown')
            process_id = active_app.get('NSApplicationProcessIdentifier', 0)
            
            # Get window title from frontmost window
            title = self._get_frontmost_window_title(process_id)
            if not title:
                title = process_name
            
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
    
    def _get_frontmost_window_title(self, process_id: int) -> Optional[str]:
        """
        Get the title of the frontmost window for a given process.
        
        Args:
            process_id: Process ID
            
        Returns:
            Window title or None
        """
        try:
            # Get list of all windows
            window_list = CGWindowListCopyWindowInfo(
                kCGWindowListOptionOnScreenOnly,
                kCGNullWindowID
            )
            
            # Find window for this process
            for window in window_list:
                if window.get('kCGWindowOwnerPID') == process_id:
                    title = window.get('kCGWindowName')
                    if title:
                        return title
            
            return None
        
        except Exception as e:
            self._logger.warning(f"Error getting window title: {e}")
            return None
    
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
            # Get running application
            app = NSRunningApplication.runningApplicationWithProcessIdentifier_(process_id)
            if not app:
                return None
            
            # Get icon
            ns_image = app.icon()
            if not ns_image:
                return None
            
            # Convert NSImage to QPixmap
            pixmap = self._nsimage_to_qpixmap(ns_image)
            if pixmap:
                self._cache_icon(cache_key, pixmap)
                return pixmap
        
        except Exception as e:
            self._logger.warning(f"Error getting app icon: {e}")
        
        return None
    
    def _nsimage_to_qpixmap(self, ns_image) -> Optional[QPixmap]:
        """
        Convert NSImage to QPixmap.
        
        Args:
            ns_image: NSImage object
            
        Returns:
            QPixmap or None
        """
        try:
            # Get TIFF representation
            tiff_data = ns_image.TIFFRepresentation()
            if not tiff_data:
                return None
            
            # Convert to bytes
            data = bytes(tiff_data)
            
            # Load into QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            
            return pixmap if not pixmap.isNull() else None
        
        except Exception as e:
            self._logger.warning(f"Error converting NSImage: {e}")
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
