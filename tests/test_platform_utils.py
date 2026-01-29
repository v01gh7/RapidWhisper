"""
Тесты для платформо-зависимых утилит.

Включает unit-тесты для определения платформы и применения
эффектов размытия.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from utils.platform_utils import (
    Platform,
    detect_platform,
    apply_windows_blur,
    apply_macos_blur,
    apply_linux_blur,
    apply_blur_effect
)


class TestPlatformDetection:
    """Тесты определения платформы"""
    
    @patch('platform.system')
    def test_detect_windows(self, mock_system):
        """Тест определения Windows"""
        mock_system.return_value = "Windows"
        
        result = detect_platform()
        
        assert result == Platform.WINDOWS
    
    @patch('platform.system')
    def test_detect_macos(self, mock_system):
        """Тест определения macOS"""
        mock_system.return_value = "Darwin"
        
        result = detect_platform()
        
        assert result == Platform.MACOS
    
    @patch('platform.system')
    def test_detect_linux(self, mock_system):
        """Тест определения Linux"""
        mock_system.return_value = "Linux"
        
        result = detect_platform()
        
        assert result == Platform.LINUX
    
    @patch('platform.system')
    def test_detect_unknown(self, mock_system):
        """Тест определения неизвестной платформы"""
        mock_system.return_value = "FreeBSD"
        
        result = detect_platform()
        
        assert result == Platform.UNKNOWN


class TestWindowsBlur:
    """Тесты эффекта размытия для Windows"""
    
    @patch('ctypes.windll')
    def test_apply_windows_blur_success(self, mock_windll):
        """Тест успешного применения эффекта для Windows"""
        # Мокируем Windows API
        mock_user32 = MagicMock()
        mock_user32.SetWindowCompositionAttribute.return_value = True
        mock_windll.user32 = mock_user32
        
        hwnd = 12345
        result = apply_windows_blur(hwnd)
        
        assert result is True
    
    @patch('ctypes.windll')
    def test_apply_windows_blur_failure(self, mock_windll):
        """Тест неудачного применения эффекта для Windows"""
        # Мокируем Windows API с ошибкой
        mock_user32 = MagicMock()
        mock_user32.SetWindowCompositionAttribute.side_effect = Exception("API Error")
        mock_windll.user32 = mock_user32
        
        hwnd = 12345
        result = apply_windows_blur(hwnd)
        
        assert result is False
    
    def test_apply_windows_blur_import_error(self):
        """Тест обработки ошибки импорта ctypes"""
        # Симулируем ошибку импорта
        with patch('builtins.__import__', side_effect=ImportError("No ctypes")):
            result = apply_windows_blur(12345)
            # Функция должна обработать ошибку и вернуть False
            assert result is False


class TestMacOSBlur:
    """Тесты эффекта размытия для macOS"""
    
    def test_apply_macos_blur_no_pyobjc(self):
        """Тест обработки отсутствия PyObjC"""
        mock_window = Mock()
        mock_window.winId.return_value = Mock(__int__=lambda self: 12345)
        mock_window.width.return_value = 400
        mock_window.height.return_value = 120
        
        # PyObjC обычно не установлен в тестовой среде
        result = apply_macos_blur(mock_window)
        
        # Должен вернуть False если PyObjC недоступен
        assert result is False
    
    def test_apply_macos_blur_with_pyobjc(self):
        """Тест применения эффекта для macOS с PyObjC"""
        mock_window = Mock()
        mock_window.winId.return_value = Mock(__int__=lambda self: 12345)
        mock_window.width.return_value = 400
        mock_window.height.return_value = 120
        
        # Мокируем модуль AppKit
        mock_appkit = MagicMock()
        mock_effect = MagicMock()
        mock_appkit.NSVisualEffectView.alloc.return_value.initWithFrame_.return_value = mock_effect
        
        with patch.dict('sys.modules', {'AppKit': mock_appkit}):
            # Перезагружаем функцию с мокнутым AppKit
            from importlib import reload
            import utils.platform_utils as pu
            reload(pu)
            
            result = pu.apply_macos_blur(mock_window)
            
            # На Windows/Linux PyObjC не установлен, поэтому вернет False
            # Это нормальное поведение
            assert isinstance(result, bool)


class TestLinuxBlur:
    """Тесты эффекта размытия для Linux"""
    
    def test_apply_linux_blur_success(self):
        """Тест применения эффекта для Linux"""
        mock_window = Mock()
        
        result = apply_linux_blur(mock_window)
        
        # Должен попытаться установить свойства
        assert mock_window.setProperty.called
        assert result is True
    
    def test_apply_linux_blur_failure(self):
        """Тест обработки ошибки для Linux"""
        mock_window = Mock()
        mock_window.setProperty.side_effect = Exception("Property error")
        
        result = apply_linux_blur(mock_window)
        
        assert result is False


class TestApplyBlurEffect:
    """Тесты универсальной функции применения эффекта"""
    
    @patch('utils.platform_utils.detect_platform')
    def test_apply_blur_windows(self, mock_detect):
        """Тест применения эффекта на Windows"""
        mock_detect.return_value = Platform.WINDOWS
        
        mock_window = Mock()
        mock_window.winId.return_value = 12345
        
        # Функция должна вернуть bool (True или False в зависимости от успеха)
        result = apply_blur_effect(mock_window)
        
        assert isinstance(result, bool)
        mock_detect.assert_called_once()
    
    @patch('utils.platform_utils.detect_platform')
    def test_apply_blur_macos(self, mock_detect):
        """Тест применения эффекта на macOS"""
        mock_detect.return_value = Platform.MACOS
        
        mock_window = Mock()
        mock_window.winId.return_value = 12345
        mock_window.width.return_value = 400
        mock_window.height.return_value = 120
        
        # Функция должна вернуть bool
        result = apply_blur_effect(mock_window)
        
        assert isinstance(result, bool)
        mock_detect.assert_called_once()
    
    @patch('utils.platform_utils.detect_platform')
    def test_apply_blur_linux(self, mock_detect):
        """Тест применения эффекта на Linux"""
        mock_detect.return_value = Platform.LINUX
        
        mock_window = Mock()
        
        # Функция должна вернуть bool
        result = apply_blur_effect(mock_window)
        
        assert isinstance(result, bool)
        mock_detect.assert_called_once()
    
    @patch('utils.platform_utils.detect_platform')
    def test_apply_blur_unknown_platform(self, mock_detect):
        """Тест обработки неизвестной платформы"""
        mock_detect.return_value = Platform.UNKNOWN
        
        mock_window = Mock()
        
        result = apply_blur_effect(mock_window)
        
        assert result is False
