"""
Unit-тесты для модуля мониторинга активного окна.

Тестирует создание WindowInfo, фабричный метод create() для разных платформ,
и базовую функциональность абстрактного класса WindowMonitor.
"""

import pytest
import sys
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap
from services.window_monitor import WindowMonitor, WindowInfo


# Создаем QApplication для тестов
@pytest.fixture(scope="module")
def qapp():
    """Фикстура для создания QApplication"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestWindowInfo:
    """Тесты для dataclass WindowInfo."""
    
    def test_window_info_creation_with_all_fields(self):
        """Тест создания WindowInfo с корректными полями."""
        # Создать тестовую иконку
        test_icon = QPixmap(20, 20)
        
        # Создать WindowInfo
        window_info = WindowInfo(
            title="Test Window",
            process_name="test.exe",
            icon=test_icon,
            process_id=12345
        )
        
        # Проверить все поля
        assert window_info.title == "Test Window"
        assert window_info.process_name == "test.exe"
        assert window_info.icon == test_icon
        assert window_info.process_id == 12345
    
    def test_window_info_creation_with_none_icon(self):
        """Тест создания WindowInfo с иконкой None."""
        window_info = WindowInfo(
            title="Test Window",
            process_name="test.exe",
            icon=None,
            process_id=12345
        )
        
        assert window_info.title == "Test Window"
        assert window_info.process_name == "test.exe"
        assert window_info.icon is None
        assert window_info.process_id == 12345
    
    def test_window_info_creation_with_empty_title(self):
        """Тест создания WindowInfo с пустым заголовком."""
        window_info = WindowInfo(
            title="",
            process_name="test.exe",
            icon=None,
            process_id=12345
        )
        
        assert window_info.title == ""
        assert window_info.process_name == "test.exe"
        assert window_info.icon is None
        assert window_info.process_id == 12345
    
    def test_window_info_creation_with_long_title(self):
        """Тест создания WindowInfo с длинным заголовком."""
        long_title = "A" * 100
        window_info = WindowInfo(
            title=long_title,
            process_name="test.exe",
            icon=None,
            process_id=12345
        )
        
        assert window_info.title == long_title
        assert len(window_info.title) == 100
    
    def test_window_info_creation_with_special_characters(self):
        """Тест создания WindowInfo с специальными символами в заголовке."""
        special_title = "Test — Window • 2024 © ™"
        window_info = WindowInfo(
            title=special_title,
            process_name="test.exe",
            icon=None,
            process_id=12345
        )
        
        assert window_info.title == special_title
    
    def test_window_info_dataclass_equality(self):
        """Тест равенства двух WindowInfo объектов."""
        icon1 = QPixmap(20, 20)
        icon2 = QPixmap(20, 20)
        
        window_info1 = WindowInfo(
            title="Test",
            process_name="test.exe",
            icon=icon1,
            process_id=123
        )
        
        window_info2 = WindowInfo(
            title="Test",
            process_name="test.exe",
            icon=icon1,  # Тот же объект иконки
            process_id=123
        )
        
        # Dataclass должен поддерживать равенство
        assert window_info1 == window_info2
    
    def test_window_info_dataclass_inequality(self):
        """Тест неравенства двух WindowInfo объектов."""
        window_info1 = WindowInfo(
            title="Test1",
            process_name="test.exe",
            icon=None,
            process_id=123
        )
        
        window_info2 = WindowInfo(
            title="Test2",
            process_name="test.exe",
            icon=None,
            process_id=123
        )
        
        assert window_info1 != window_info2


class TestWindowMonitorFactory:
    """Тесты для фабричного метода WindowMonitor.create()."""
    
    @patch('platform.system')
    def test_create_windows_monitor(self, mock_system):
        """
        Тест фабричного метода create() для Windows платформы.
        
        Validates: Requirements 9.1, 9.3
        """
        # Настроить мок для возврата "Windows"
        mock_system.return_value = "Windows"
        
        # Создать монитор через фабричный метод
        monitor = WindowMonitor.create()
        
        # Проверить, что создан правильный тип монитора
        assert monitor is not None
        assert isinstance(monitor, WindowMonitor)
        
        # Проверить, что это WindowsWindowMonitor
        from services.windows_window_monitor import WindowsWindowMonitor
        assert isinstance(monitor, WindowsWindowMonitor)
        
        # Проверить, что platform.system() был вызван
        mock_system.assert_called_once()
    
    @patch('platform.system')
    def test_create_linux_monitor_raises_error(self, mock_system):
        """
        Тест фабричного метода create() для неподдерживаемой платформы Linux.
        
        Validates: Requirements 9.4
        """
        # Настроить мок для возврата "Linux"
        mock_system.return_value = "Linux"
        
        # Проверить, что создание монитора вызывает NotImplementedError
        with pytest.raises(NotImplementedError) as exc_info:
            WindowMonitor.create()
        
        # Проверить сообщение об ошибке
        assert "Unsupported platform: Linux" in str(exc_info.value)
        
        # Проверить, что platform.system() был вызван
        mock_system.assert_called_once()
    
    @patch('platform.system')
    def test_create_macos_monitor_raises_error(self, mock_system):
        """
        Тест фабричного метода create() для неподдерживаемой платформы macOS.
        
        Validates: Requirements 9.4
        """
        # Настроить мок для возврата "Darwin" (macOS)
        mock_system.return_value = "Darwin"
        
        # Проверить, что создание монитора вызывает NotImplementedError
        with pytest.raises(NotImplementedError) as exc_info:
            WindowMonitor.create()
        
        # Проверить сообщение об ошибке
        assert "Unsupported platform: Darwin" in str(exc_info.value)
        
        # Проверить, что platform.system() был вызван
        mock_system.assert_called_once()
    
    @patch('platform.system')
    def test_create_unknown_platform_raises_error(self, mock_system):
        """
        Тест фабричного метода create() для неизвестной платформы.
        
        Validates: Requirements 9.4
        """
        # Настроить мок для возврата неизвестную платформу
        mock_system.return_value = "UnknownOS"
        
        # Проверить, что создание монитора вызывает NotImplementedError
        with pytest.raises(NotImplementedError) as exc_info:
            WindowMonitor.create()
        
        # Проверить сообщение об ошибке
        assert "Unsupported platform: UnknownOS" in str(exc_info.value)
        
        # Проверить, что platform.system() был вызван
        mock_system.assert_called_once()
    
    @patch('platform.system')
    def test_create_windows_monitor_multiple_times(self, mock_system):
        """
        Тест создания нескольких экземпляров WindowsWindowMonitor.
        
        Validates: Requirements 9.3
        """
        # Настроить мок для возврата "Windows"
        mock_system.return_value = "Windows"
        
        # Создать несколько мониторов
        monitor1 = WindowMonitor.create()
        monitor2 = WindowMonitor.create()
        
        # Проверить, что оба монитора созданы
        assert monitor1 is not None
        assert monitor2 is not None
        
        # Проверить, что это разные экземпляры
        assert monitor1 is not monitor2
        
        # Проверить, что оба являются WindowsWindowMonitor
        from services.windows_window_monitor import WindowsWindowMonitor
        assert isinstance(monitor1, WindowsWindowMonitor)
        assert isinstance(monitor2, WindowsWindowMonitor)


class TestWindowMonitorAbstractMethods:
    """Тесты для абстрактных методов WindowMonitor."""
    
    def test_cannot_instantiate_abstract_class(self):
        """Тест, что нельзя создать экземпляр абстрактного класса WindowMonitor."""
        # Попытка создать экземпляр абстрактного класса должна вызвать TypeError
        with pytest.raises(TypeError) as exc_info:
            WindowMonitor()
        
        # Проверить, что ошибка связана с абстрактными методами
        assert "abstract" in str(exc_info.value).lower()
    
    def test_abstract_methods_defined(self):
        """Тест, что все абстрактные методы определены в базовом классе."""
        # Проверить, что абстрактные методы существуют
        assert hasattr(WindowMonitor, 'get_active_window_info')
        assert hasattr(WindowMonitor, 'start_monitoring')
        assert hasattr(WindowMonitor, 'stop_monitoring')
        
        # Проверить, что это абстрактные методы
        assert hasattr(WindowMonitor.get_active_window_info, '__isabstractmethod__')
        assert hasattr(WindowMonitor.start_monitoring, '__isabstractmethod__')
        assert hasattr(WindowMonitor.stop_monitoring, '__isabstractmethod__')
    
    def test_concrete_implementation_must_implement_all_methods(self):
        """Тест, что конкретная реализация должна реализовать все абстрактные методы."""
        # Создать неполную реализацию
        class IncompleteMonitor(WindowMonitor):
            def get_active_window_info(self):
                return None
            # Не реализуем start_monitoring и stop_monitoring
        
        # Попытка создать экземпляр должна вызвать TypeError
        with pytest.raises(TypeError) as exc_info:
            IncompleteMonitor()
        
        # Проверить, что ошибка связана с абстрактными методами
        assert "abstract" in str(exc_info.value).lower()


class TestWindowMonitorRequirements:
    """Тесты валидации требований для WindowMonitor."""
    
    def test_requirement_9_1_abstract_base_class(self):
        """
        Requirement 9.1: THE Window_Monitor SHALL быть реализован как абстрактный 
        базовый класс с методами get_active_window_info()
        """
        # Проверить, что WindowMonitor является абстрактным базовым классом
        from abc import ABC
        assert issubclass(WindowMonitor, ABC)
        
        # Проверить, что метод get_active_window_info() определен
        assert hasattr(WindowMonitor, 'get_active_window_info')
        assert hasattr(WindowMonitor.get_active_window_info, '__isabstractmethod__')
    
    @patch('platform.system')
    def test_requirement_9_3_automatic_implementation_selection(self, mock_system):
        """
        Requirement 9.3: THE Window_Monitor SHALL автоматически выбирать правильную 
        реализацию на основе platform.system()
        """
        # Настроить мок для возврата "Windows"
        mock_system.return_value = "Windows"
        
        # Создать монитор через фабричный метод
        monitor = WindowMonitor.create()
        
        # Проверить, что создан правильный тип монитора для Windows
        from services.windows_window_monitor import WindowsWindowMonitor
        assert isinstance(monitor, WindowsWindowMonitor)
        
        # Проверить, что platform.system() был использован для выбора
        mock_system.assert_called()
    
    @patch('platform.system')
    def test_requirement_9_4_unsupported_platform_handling(self, mock_system):
        """
        Requirement 9.4: WHERE платформа не Windows, THE Window_Monitor SHALL 
        возвращать заглушку с сообщением "Unsupported platform"
        """
        # Настроить мок для возврата неподдерживаемую платформу
        mock_system.return_value = "Linux"
        
        # Проверить, что создание монитора вызывает NotImplementedError
        # с сообщением о неподдерживаемой платформе
        with pytest.raises(NotImplementedError) as exc_info:
            WindowMonitor.create()
        
        # Проверить, что сообщение содержит "Unsupported platform"
        error_message = str(exc_info.value)
        assert "Unsupported platform" in error_message
        assert "Linux" in error_message


class TestWindowMonitorEdgeCases:
    """Тесты граничных случаев для WindowMonitor."""
    
    @patch('platform.system')
    def test_create_with_empty_platform_string(self, mock_system):
        """Тест фабричного метода с пустой строкой платформы."""
        # Настроить мок для возврата пустую строку
        mock_system.return_value = ""
        
        # Проверить, что создание монитора вызывает NotImplementedError
        with pytest.raises(NotImplementedError) as exc_info:
            WindowMonitor.create()
        
        # Проверить сообщение об ошибке
        assert "Unsupported platform" in str(exc_info.value)
    
    @patch('platform.system')
    def test_create_with_case_sensitive_platform(self, mock_system):
        """Тест фабричного метода с платформой в неправильном регистре."""
        # Настроить мок для возврата "windows" (в нижнем регистре)
        mock_system.return_value = "windows"
        
        # Проверить, что создание монитора вызывает NotImplementedError
        # так как проверка регистрозависима
        with pytest.raises(NotImplementedError) as exc_info:
            WindowMonitor.create()
        
        # Проверить сообщение об ошибке
        assert "Unsupported platform: windows" in str(exc_info.value)
    
    def test_window_info_with_zero_process_id(self):
        """Тест создания WindowInfo с process_id равным 0."""
        window_info = WindowInfo(
            title="System Process",
            process_name="System",
            icon=None,
            process_id=0
        )
        
        assert window_info.process_id == 0
    
    def test_window_info_with_negative_process_id(self):
        """Тест создания WindowInfo с отрицательным process_id."""
        # В некоторых системах могут быть отрицательные PID
        window_info = WindowInfo(
            title="Test",
            process_name="test.exe",
            icon=None,
            process_id=-1
        )
        
        assert window_info.process_id == -1
    
    def test_window_info_with_large_process_id(self):
        """Тест создания WindowInfo с очень большим process_id."""
        large_pid = 2**31 - 1  # Максимальный 32-битный signed int
        window_info = WindowInfo(
            title="Test",
            process_name="test.exe",
            icon=None,
            process_id=large_pid
        )
        
        assert window_info.process_id == large_pid
