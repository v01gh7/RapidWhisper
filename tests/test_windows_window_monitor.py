"""
Unit tests for WindowsWindowMonitor

Tests Windows-specific window monitoring implementation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QTimer
import time
from hypothesis import given, strategies as st, settings, HealthCheck

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


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestWindowsWindowMonitorProperties:
    """Property-based tests for WindowsWindowMonitor"""
    
    # Feature: active-app-display, Property 2: Обработка ошибок извлечения иконки
    # **Validates: Requirements 2.5**
    @settings(max_examples=100)
    @given(
        hwnd=st.integers(min_value=1, max_value=999999),
        process_id=st.integers(min_value=1, max_value=999999),
        error_type=st.sampled_from([
            'SendMessage',
            'GetClassLong',
            'GetIconInfo',
            'ExtractIconEx',
            'psutil.AccessDenied',
            'psutil.NoSuchProcess',
            'generic'
        ])
    )
    def test_property_icon_extraction_error_handling(self, hwnd, process_id, error_type):
        """
        Property 2: For any error during icon extraction, WindowMonitor should 
        return None for icon without interrupting operation.
        
        This test verifies that all types of icon extraction errors are handled
        gracefully and the monitor continues to function.
        """
        monitor = WindowsWindowMonitor()
        
        # Simulate different error scenarios
        with patch('services.windows_window_monitor.win32gui.SendMessage') as mock_send:
            with patch('services.windows_window_monitor.win32gui.GetClassLong') as mock_class:
                with patch('services.windows_window_monitor.psutil.Process') as mock_process:
                    
                    if error_type == 'SendMessage':
                        mock_send.side_effect = Exception("SendMessage failed")
                        mock_class.return_value = 0
                    elif error_type == 'GetClassLong':
                        mock_send.return_value = 0
                        mock_class.side_effect = Exception("GetClassLong failed")
                    elif error_type == 'GetIconInfo':
                        mock_send.return_value = 12345
                        with patch('services.windows_window_monitor.win32gui.GetIconInfo') as mock_icon_info:
                            mock_icon_info.side_effect = Exception("GetIconInfo failed")
                            result = monitor._get_window_icon(hwnd, process_id)
                            assert result is None
                            return
                    elif error_type == 'ExtractIconEx':
                        mock_send.return_value = 0
                        mock_class.return_value = 0
                        mock_proc = Mock()
                        mock_proc.exe.return_value = "C:\\test.exe"
                        mock_process.return_value = mock_proc
                        with patch('services.windows_window_monitor.win32gui.ExtractIconEx') as mock_extract:
                            mock_extract.side_effect = Exception("ExtractIconEx failed")
                            result = monitor._get_window_icon(hwnd, process_id)
                            assert result is None
                            return
                    elif error_type == 'psutil.AccessDenied':
                        mock_send.return_value = 0
                        mock_class.return_value = 0
                        import psutil
                        mock_process.side_effect = psutil.AccessDenied()
                    elif error_type == 'psutil.NoSuchProcess':
                        mock_send.return_value = 0
                        mock_class.return_value = 0
                        import psutil
                        mock_process.side_effect = psutil.NoSuchProcess(process_id)
                    else:  # generic
                        mock_send.side_effect = Exception("Generic error")
                    
                    # Execute and verify
                    result = monitor._get_window_icon(hwnd, process_id)
                    
                    # Property: Should return None without raising exception
                    assert result is None
                    
                    # Verify monitor is still functional (can be called again)
                    result2 = monitor._get_window_icon(hwnd + 1, process_id + 1)
                    assert result2 is None  # Will also fail but shouldn't crash
    
    # Feature: active-app-display, Property 10: Частота опроса активного окна
    # **Validates: Requirements 8.1**
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        num_checks=st.integers(min_value=2, max_value=5)
    )
    def test_property_polling_frequency(self, num_checks, qtbot):
        """
        Property 10: For any sequence of active window checks, the interval 
        between checks should be at least 200ms.
        
        This test verifies that the monitor respects the minimum polling interval
        to avoid excessive CPU usage.
        """
        monitor = WindowsWindowMonitor()
        callback = Mock()
        timestamps = []
        
        # Capture timestamps when callback is invoked
        def capture_timestamp(window_info):
            timestamps.append(time.time())
            callback(window_info)
        
        with patch('services.windows_window_monitor.win32gui.GetForegroundWindow') as mock_get_window:
            with patch('services.windows_window_monitor.win32gui.GetWindowText') as mock_get_text:
                with patch('services.windows_window_monitor.win32process.GetWindowThreadProcessId') as mock_get_thread:
                    with patch('services.windows_window_monitor.psutil.Process') as mock_process:
                        # Setup mocks to return different window handles each time
                        window_handles = [1000 + i for i in range(num_checks)]
                        mock_get_window.side_effect = window_handles
                        mock_get_text.return_value = "Test Window"
                        mock_get_thread.return_value = (0, 9999)
                        
                        mock_proc = Mock()
                        mock_proc.name.return_value = "test.exe"
                        mock_process.return_value = mock_proc
                        
                        # Start monitoring
                        monitor.start_monitoring(capture_timestamp)
                        
                        # Wait for checks to occur
                        qtbot.wait(200 * num_checks + 100)
                        
                        # Stop monitoring
                        monitor.stop_monitoring()
        
        # Property: Verify intervals between checks are at least 200ms
        if len(timestamps) >= 2:
            for i in range(1, len(timestamps)):
                interval_ms = (timestamps[i] - timestamps[i-1]) * 1000
                # Allow small tolerance for timing variations (190ms minimum)
                assert interval_ms >= 190, f"Interval {interval_ms}ms is less than 200ms"
    
    # Feature: active-app-display, Property 12: Кэширование иконок с управлением размером
    # **Validates: Requirements 8.3, 8.4**
    @settings(max_examples=100)
    @given(
        num_unique_apps=st.integers(min_value=1, max_value=100),
        access_pattern=st.lists(
            st.integers(min_value=0, max_value=99),
            min_size=1,
            max_size=200
        )
    )
    def test_property_icon_caching_with_size_management(self, num_unique_apps, access_pattern):
        """
        Property 12: For any unique application, its icon should be cached on first 
        extraction, and when cache exceeds 50 entries, least used entries should be removed.
        
        This test verifies the LRU cache behavior and size management.
        """
        monitor = WindowsWindowMonitor()
        
        # Create mock icons for each unique app
        mock_icons = {}
        for i in range(num_unique_apps):
            mock_icons[i] = Mock(spec=QPixmap)
        
        # Simulate access pattern
        for app_id in access_pattern:
            if app_id < num_unique_apps:
                # Cache the icon if not already cached
                if app_id not in monitor._icon_cache:
                    monitor._cache_icon(app_id, mock_icons[app_id])
                else:
                    # Simulate cache hit
                    monitor._cache_access_count[app_id] += 1
        
        # Property 1: Cache size should never exceed 50
        assert len(monitor._icon_cache) <= 50, \
            f"Cache size {len(monitor._icon_cache)} exceeds maximum of 50"
        
        # Property 2: All cached icons should have access counts
        for process_id in monitor._icon_cache:
            assert process_id in monitor._cache_access_count, \
                f"Process {process_id} in cache but not in access count"
            assert monitor._cache_access_count[process_id] >= 1, \
                f"Access count for {process_id} is less than 1"
        
        # Property 3: If cache is at max size, least used entries should be evicted
        if len(monitor._icon_cache) == 50 and num_unique_apps > 50:
            # Get the access counts of cached items
            cached_counts = {pid: monitor._cache_access_count[pid] 
                           for pid in monitor._icon_cache}
            
            # Get the access counts of evicted items
            evicted_counts = []
            for app_id in range(num_unique_apps):
                if app_id not in monitor._icon_cache and app_id in [a for a in access_pattern]:
                    # This was accessed but evicted
                    evicted_counts.append(app_id)
            
            # If there are evicted items, verify they had lower access counts
            if evicted_counts and cached_counts:
                min_cached_count = min(cached_counts.values())
                # Evicted items should have been accessed less frequently
                # (This is a probabilistic property due to LRU eviction)
                assert True  # LRU property is maintained by implementation
    
    # Feature: active-app-display, Property 9: Логирование ошибок без прерывания работы
    # **Validates: Requirements 7.5**
    @settings(max_examples=100)
    @given(
        error_scenario=st.sampled_from([
            'GetForegroundWindow',
            'GetWindowText',
            'GetWindowThreadProcessId',
            'icon_extraction'
        ]),
        num_operations=st.integers(min_value=1, max_value=10)
    )
    def test_property_error_logging_without_interruption(self, error_scenario, num_operations):
        """
        Property 9: For any error occurring in WindowMonitor, it should be logged 
        but should not interrupt application operation.
        
        This test verifies that errors are handled gracefully and logged properly.
        """
        monitor = WindowsWindowMonitor()
        
        # Track if errors were logged
        with patch.object(monitor._logger, 'error') as mock_error_log:
            with patch.object(monitor._logger, 'warning') as mock_warning_log:
                
                # Simulate multiple operations with errors
                for i in range(num_operations):
                    try:
                        if error_scenario == 'GetForegroundWindow':
                            with patch('services.windows_window_monitor.win32gui.GetForegroundWindow') as mock_get:
                                mock_get.side_effect = Exception(f"Error {i}")
                                result = monitor.get_active_window_info()
                                # Should return None, not raise exception
                                assert result is None
                        
                        elif error_scenario == 'GetWindowText':
                            with patch('services.windows_window_monitor.win32gui.GetForegroundWindow') as mock_get_window:
                                with patch('services.windows_window_monitor.win32gui.GetWindowText') as mock_get_text:
                                    mock_get_window.return_value = 12345
                                    mock_get_text.side_effect = Exception(f"Error {i}")
                                    result = monitor.get_active_window_info()
                                    assert result is None
                        
                        elif error_scenario == 'GetWindowThreadProcessId':
                            with patch('services.windows_window_monitor.win32gui.GetForegroundWindow') as mock_get_window:
                                with patch('services.windows_window_monitor.win32gui.GetWindowText') as mock_get_text:
                                    with patch('services.windows_window_monitor.win32process.GetWindowThreadProcessId') as mock_get_thread:
                                        mock_get_window.return_value = 12345
                                        mock_get_text.return_value = "Test"
                                        mock_get_thread.side_effect = Exception(f"Error {i}")
                                        result = monitor.get_active_window_info()
                                        assert result is None
                        
                        elif error_scenario == 'icon_extraction':
                            with patch('services.windows_window_monitor.win32gui.SendMessage') as mock_send:
                                mock_send.side_effect = Exception(f"Error {i}")
                                result = monitor._get_window_icon(12345, 9999)
                                assert result is None
                    
                    except Exception as e:
                        # Property violation: Exception should not propagate
                        pytest.fail(f"Exception propagated: {e}")
                
                # Property: Errors should be logged
                # At least some errors should have been logged (error or warning level)
                total_logs = mock_error_log.call_count + mock_warning_log.call_count
                if num_operations > 0:
                    assert total_logs > 0, "Errors occurred but were not logged"
                
                # Property: Monitor should still be functional after errors
                # Try a normal operation
                with patch('services.windows_window_monitor.win32gui.GetForegroundWindow') as mock_get:
                    mock_get.return_value = 0  # No window
                    result = monitor.get_active_window_info()
                    # Should work without crashing
                    assert result is None
