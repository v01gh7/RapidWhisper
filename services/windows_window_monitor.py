"""
Windows Window Monitor Module

Provides Windows-specific implementation for monitoring active windows using win32 API.
"""

import logging
from typing import Optional, Dict, Callable
import win32gui
import win32process
import win32con
import win32ui
import psutil
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap, QImage

from services.window_monitor import WindowMonitor, WindowInfo


class WindowsWindowMonitor(WindowMonitor):
    """Windows implementation of window monitoring using win32 API"""
    
    def __init__(self):
        """Initialize the Windows window monitor"""
        self._timer: Optional[QTimer] = None
        self._callback: Optional[Callable[[WindowInfo], None]] = None
        self._icon_cache: Dict[int, QPixmap] = {}
        self._last_window_handle: Optional[int] = None
        self._cache_max_size = 50
        self._cache_access_count: Dict[int, int] = {}
        self._logger = logging.getLogger(__name__)
    
    def get_active_window_info(self) -> Optional[WindowInfo]:
        """
        Get information about the current active window via Windows API.
        
        Returns:
            WindowInfo if window is found, None on error
        """
        try:
            # Get handle of active window
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None
            
            # Get window title
            title = win32gui.GetWindowText(hwnd)
            if not title:
                title = "Unknown Window"
            
            # Get process ID
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            
            # Get process name
            try:
                process = psutil.Process(process_id)
                process_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "Unknown Process"
            
            # Get icon (with caching)
            icon = self._get_window_icon(hwnd, process_id)
            
            return WindowInfo(
                title=title,
                process_name=process_name,
                icon=icon,
                process_id=process_id
            )
        
        except Exception as e:
            self._logger.error(f"Error getting window info: {e}")
            return None
    
    def _get_window_icon(self, hwnd: int, process_id: int) -> Optional[QPixmap]:
        """
        Get window icon with caching.
        
        Args:
            hwnd: Window handle
            process_id: Process ID for caching
            
        Returns:
            QPixmap icon or None if extraction fails
        """
        # Check cache
        if process_id in self._icon_cache:
            self._cache_access_count[process_id] += 1
            return self._icon_cache[process_id]
        
        # Extract icon
        try:
            # Attempt 1: Get icon from window
            icon_handle = win32gui.SendMessage(
                hwnd, win32con.WM_GETICON, win32con.ICON_SMALL, 0
            )
            
            if not icon_handle:
                # Attempt 2: Get icon from window class
                icon_handle = win32gui.GetClassLong(hwnd, win32con.GCL_HICON)
            
            if icon_handle:
                # Convert HICON to QPixmap
                pixmap = self._hicon_to_qpixmap(icon_handle)
                if pixmap:
                    self._cache_icon(process_id, pixmap)
                    return pixmap
            
            # Attempt 3: Extract icon from executable file
            try:
                process = psutil.Process(process_id)
                exe_path = process.exe()
                pixmap = self._extract_icon_from_exe(exe_path)
                if pixmap:
                    self._cache_icon(process_id, pixmap)
                    return pixmap
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        except Exception as e:
            self._logger.warning(f"Error extracting icon: {e}")
        
        return None
    
    def _hicon_to_qpixmap(self, icon_handle: int) -> Optional[QPixmap]:
        """
        Convert Windows HICON to QPixmap.
        
        Args:
            icon_handle: Windows icon handle
            
        Returns:
            QPixmap or None on error
        """
        try:
            # Get icon information
            icon_info = win32gui.GetIconInfo(icon_handle)
            hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
            hbmp = win32ui.CreateBitmapFromHandle(icon_info[4])
            
            # Get dimensions
            bmp_info = hbmp.GetInfo()
            width, height = bmp_info['bmWidth'], bmp_info['bmHeight']
            
            # Create compatible DC and copy bitmap
            mem_dc = hdc.CreateCompatibleDC()
            mem_dc.SelectObject(hbmp)
            
            # Convert to QImage
            bmp_str = hbmp.GetBitmapBits(True)
            image = QImage(
                bmp_str, width, height, QImage.Format.Format_ARGB32
            )
            
            # Cleanup resources
            win32gui.DeleteObject(icon_info[4])
            mem_dc.DeleteDC()
            hdc.DeleteDC()
            
            return QPixmap.fromImage(image)
        
        except Exception as e:
            self._logger.warning(f"Error converting HICON: {e}")
            return None
    
    def _extract_icon_from_exe(self, exe_path: str) -> Optional[QPixmap]:
        """
        Extract icon from executable file.
        
        Args:
            exe_path: Path to executable file
            
        Returns:
            QPixmap or None on error
        """
        try:
            # Extract icon
            large, small = win32gui.ExtractIconEx(exe_path, 0)
            if small:
                icon_handle = small[0]
                pixmap = self._hicon_to_qpixmap(icon_handle)
                # Cleanup
                for icon in small:
                    win32gui.DestroyIcon(icon)
                for icon in large:
                    win32gui.DestroyIcon(icon)
                return pixmap
        
        except Exception as e:
            self._logger.warning(f"Error extracting icon from exe: {e}")
        
        return None
    
    def _cache_icon(self, process_id: int, icon: QPixmap) -> None:
        """
        Cache icon with LRU management.
        
        Args:
            process_id: Process ID to use as cache key
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
        
        self._icon_cache[process_id] = icon
        self._cache_access_count[process_id] = 1
    
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
            hwnd = win32gui.GetForegroundWindow()
            
            # Check if window changed
            if hwnd != self._last_window_handle:
                self._last_window_handle = hwnd
                window_info = self.get_active_window_info()
                
                if window_info and self._callback:
                    self._callback(window_info)
        
        except Exception as e:
            self._logger.error(f"Error checking active window: {e}")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring"""
        if self._timer:
            self._timer.stop()
            self._timer = None
        self._callback = None
