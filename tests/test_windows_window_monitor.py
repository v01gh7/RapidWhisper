"""
Unit tests for WindowsWindowMonitor

Tests Windows-specific window monitoring implementation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QTimer

from services.windows_window_monitor import WindowsWindowMonitor
from services.window_monitor import WindowInfo


class TestWindowsWindowMonitor:
    """Test suite for WindowsWindowMonitor"""
    
    @pytest.fixture
    def monitor(self):
        """Create a WindowsWindowMonitor instance"""
        return WindowsWindowMonitor()
    
    @patch('services.windows_window_monitor.win32gui.GetForegroundWindow')
    @patch('services.windows_window_monitor.win32gui.GetWindowText')
    @patch('services.windows_window_monitor.win32process.GetWindowThreadProcessId')
    @patch('services.windows_window_monitor.psutil.Process')
    def test_get_active_window_info_success(
        self, mock_process, mock_get_thread, mock_get_text, mock_get_window, monitor
    ):
        """Test successful retrieval of window information"""
        # Setup mocks
        mock_get_window.return_value = 12345
        mock_get_text.return_value = "Test Window"
        mock_get_thread.return_value = (0, 9999)
        
        mock_proc = Mock()
        mock_proc.name.return_value = "test.exe"
        mock_process.return_value = mock_proc
        
        # Execute
        info = monitor.get_active_window_info()
        
        # Verify
        assert info is not None
        assert info.title == "Test Window"
        assert info.process_name == "test.exe"
        assert info.process_id == 9999
        assert info.icon is None  # Icon extraction will fail in test environment
    
    @patch('services.windows_window_monitor.win32gui.GetForegroundWindow')
    def test_get_active_window_info_no_window(self, mock_get_window, monitor):
        """Test handling of no active window"""
        mock_get_window.return_value = 0
        
        info = monitor.get_active_window_info()
        
        assert info is None
    
    @patch('services.windows_window_monitor.win32gui.GetForegroundWindow')
    @patch('services.windows_window_monitor.win32gui.GetWindowText')
    @patch('services.windows_window_monitor.win32process.GetWindowThreadProcessId')
    @patch('services.windows_window_monitor.psutil.Process')
    def test_get_active_window_info_unknown_window(
        self, mock_process, mock_get_thread, mock_get_text, mock_get_window, monitor
    ):
        """Test handling of window with no title"""
        mock_get_window.return_value = 12345
        mock_get_text.return_value = ""
        mock_get_thread.return_value = (0, 9999)
        
        mock_proc = Mock()
        mock_proc.name.return_value = "test.exe"
        mock_process.return_value = mock_proc
        
        info = monitor.get_active_window_info()
        
        assert info is not None
        assert info.title == "Unknown Window"
    
    @patch('services.windows_window_monitor.win32gui.GetForegroundWindow')
    @patch('services.windows_window_monitor.win32gui.GetWindowText')
    @patch('services.windows_window_monitor.win32process.GetWindowThreadProcessId')
    @patch('services.windows_window_monitor.psutil.Process')
    def test_get_active_window_info_access_denied(
        self, mock_process, mock_get_thread, mock_get_text, mock_get_window, monitor
    ):
        """Test handling of AccessDenied error for process"""
        import psutil
        
        mock_get_window.return_value = 12345
        mock_get_text.return_value = "Protected Window"
        mock_get_thread.return_value = (0, 9999)
        mock_process.side_effect = psutil.AccessDenied()
        
        info = monitor.get_active_window_info()
        
        assert info is not None
        assert info.title == "Protected Window"
        assert info.process_name == "Unknown Process"
        assert info.process_id == 9999
    
    @patch('services.windows_window_monitor.win32gui.GetForegroundWindow')
    @patch('services.windows_window_monitor.win32gui.GetWindowText')
    @patch('services.windows_window_monitor.win32process.GetWindowThreadProcessId')
    @patch('services.windows_window_monitor.psutil.Process')
    def test_get_active_window_info_no_such_process(
        self, mock_process, mock_get_thread, mock_get_text, mock_get_window, monitor
    ):
        """Test handling of NoSuchProcess error"""
        import psutil
        
        mock_get_window.return_value = 12345
        mock_get_text.return_value = "Terminated Process Window"
        mock_get_thread.return_value = (0, 9999)
        mock_process.side_effect = psutil.NoSuchProcess(9999)
        
        info = monitor.get_active_window_info()
        
        assert info is not None
        assert info.title == "Terminated Process Window"
        assert info.process_name == "Unknown Process"
    
    @patch('services.windows_window_monitor.win32gui.GetForegroundWindow')
    def test_get_active_window_info_exception(self, mock_get_window, monitor):
        """Test handling of general exception"""
        mock_get_window.side_effect = Exception("Test error")
        
        info = monitor.get_active_window_info()
        
        assert info is None
    
    def test_icon_caching(self, monitor):
        """Test that icons are cached properly"""
        # Create a mock pixmap
        mock_pixmap = Mock(spec=QPixmap)
        
        # Cache an icon
        monitor._cache_icon(1234, mock_pixmap)
        
        # Verify it's in cache
        assert 1234 in monitor._icon_cache
        assert monitor._icon_cache[1234] == mock_pixmap
        assert monitor._cache_access_count[1234] == 1
    
    def test_icon_cache_lru_eviction(self, monitor):
        """Test LRU eviction when cache exceeds max size"""
        # Fill cache to max
        for i in range(50):
            mock_pixmap = Mock(spec=QPixmap)
            monitor._cache_icon(i, mock_pixmap)
        
        # Access some icons to increase their count
        for i in range(10, 20):
            monitor._cache_access_count[i] += 5
        
        # Add one more icon (should evict least used)
        new_pixmap = Mock(spec=QPixmap)
        monitor._cache_icon(999, new_pixmap)
        
        # Verify cache size is still at max
        assert len(monitor._icon_cache) == 50
        
        # Verify new icon is in cache
        assert 999 in monitor._icon_cache
        
        # Verify one of the least used icons was evicted
        # (one of 0-9 or 20-49 with access count of 1)
        evicted_found = False
        for i in range(50):
            if i not in range(10, 20) and i not in monitor._icon_cache:
                evicted_found = True
                break
        assert evicted_found
    
    def test_get_window_icon_from_cache(self, monitor):
        """Test retrieving icon from cache"""
        mock_pixmap = Mock(spec=QPixmap)
        monitor._icon_cache[1234] = mock_pixmap
        monitor._cache_access_count[1234] = 1
        
        result = monitor._get_window_icon(12345, 1234)
        
        assert result == mock_pixmap
        assert monitor._cache_access_count[1234] == 2
    
    @patch('services.windows_window_monitor.win32gui.SendMessage')
    def test_get_window_icon_extraction_failure(self, mock_send_message, monitor):
        """Test that None is returned when icon extraction fails"""
        mock_send_message.return_value = 0
        
        result = monitor._get_window_icon(12345, 1234)
        
        assert result is None
    
    def test_start_monitoring(self, monitor, qtbot):
        """Test starting window monitoring"""
        callback = Mock()
        
        monitor.start_monitoring(callback)
        
        assert monitor._callback == callback
        assert monitor._timer is not None
        assert monitor._timer.isActive()
        assert monitor._timer.interval() == 200
        
        # Cleanup
        monitor.stop_monitoring()
    
    def test_stop_monitoring(self, monitor, qtbot):
        """Test stopping window monitoring"""
        callback = Mock()
        monitor.start_monitoring(callback)
        
        monitor.stop_monitoring()
        
        assert monitor._timer is None
        assert monitor._callback is None
    
    @patch('services.windows_window_monitor.win32gui.GetForegroundWindow')
    def test_check_active_window_no_change(self, mock_get_window, monitor):
        """Test that callback is not called when window doesn't change"""
        mock_get_window.return_value = 12345
        monitor._last_window_handle = 12345
        callback = Mock()
        monitor._callback = callback
        
        monitor._check_active_window()
        
        callback.assert_not_called()
    
    @patch('services.windows_window_monitor.win32gui.GetForegroundWindow')
    @patch('services.windows_window_monitor.win32gui.GetWindowText')
    @patch('services.windows_window_monitor.win32process.GetWindowThreadProcessId')
    @patch('services.windows_window_monitor.psutil.Process')
    def test_check_active_window_with_change(
        self, mock_process, mock_get_thread, mock_get_text, mock_get_window, monitor
    ):
        """Test that callback is called when window changes"""
        mock_get_window.return_value = 54321
        mock_get_text.return_value = "New Window"
        mock_get_thread.return_value = (0, 9999)
        
        mock_proc = Mock()
        mock_proc.name.return_value = "new.exe"
        mock_process.return_value = mock_proc
        
        monitor._last_window_handle = 12345
        callback = Mock()
        monitor._callback = callback
        
        monitor._check_active_window()
        
        callback.assert_called_once()
        args = callback.call_args[0]
        assert isinstance(args[0], WindowInfo)
        assert args[0].title == "New Window"
    
    @patch('services.windows_window_monitor.win32gui.GetForegroundWindow')
    def test_check_active_window_exception_handling(self, mock_get_window, monitor):
        """Test that exceptions in check_active_window are handled gracefully"""
        mock_get_window.side_effect = Exception("Test error")
        callback = Mock()
        monitor._callback = callback
        
        # Should not raise exception
        monitor._check_active_window()
        
        # Callback should not be called
        callback.assert_not_called()
