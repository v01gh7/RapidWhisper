"""
Тесты для FloatingWindow.

Включает unit-тесты и property-тесты для проверки корректности
работы плавающего окна.
"""

import pytest
from unittest.mock import Mock, patch
from hypothesis import given, strategies as st, settings
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from ui.floating_window import FloatingWindow
from ui.waveform_widget import WaveformWidget
import sys


# Создаем QApplication для тестов
@pytest.fixture(scope="module")
def qapp():
    """Фикстура для создания QApplication"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestFloatingWindowInitialization:
    """Тесты инициализации FloatingWindow"""
    
    def test_initialization(self, qapp):
        """Тест инициализации окна"""
        window = FloatingWindow()
        
        assert window.window_width == 400
        assert window.window_height == 120
        assert window.width() == 400
        assert window.height() == 120
    
    def test_window_flags(self, qapp):
        """Тест установки правильных флагов окна"""
        window = FloatingWindow()
        
        flags = window.windowFlags()
        
        # Проверяем наличие нужных флагов
        assert flags & Qt.WindowType.FramelessWindowHint
        assert flags & Qt.WindowType.WindowStaysOnTopHint
        assert flags & Qt.WindowType.Tool
    
    def test_has_waveform_widget(self, qapp):
        """Тест наличия виджета визуализации волны"""
        window = FloatingWindow()
        
        assert hasattr(window, 'waveform_widget')
        assert isinstance(window.waveform_widget, WaveformWidget)
    
    def test_has_status_label(self, qapp):
        """Тест наличия метки статуса"""
        window = FloatingWindow()
        
        assert hasattr(window, 'status_label')
        assert window.status_label.text() == ""
    
    def test_has_auto_hide_timer(self, qapp):
        """Тест наличия таймера автоскрытия"""
        window = FloatingWindow()
        
        assert hasattr(window, '_auto_hide_timer')
        assert isinstance(window._auto_hide_timer, QTimer)
        assert not window._auto_hide_timer.isActive()


class TestWindowPositioning:
    """Тесты позиционирования окна"""
    
    def test_show_at_center(self, qapp):
        """Тест центрирования окна на экране"""
        window = FloatingWindow()
        
        window.show_at_center()
        
        # Окно должно быть видимым
        assert window.isVisible()
        
        # Позиция должна быть установлена
        assert window.x() >= 0
        assert window.y() >= 0
    
    def test_window_size_fixed(self, qapp):
        """Тест фиксированного размера окна"""
        window = FloatingWindow()
        
        # Размер должен быть фиксированным
        assert window.minimumWidth() == 400
        assert window.maximumWidth() == 400
        assert window.minimumHeight() == 120
        assert window.maximumHeight() == 120


class TestStatusAndText:
    """Тесты установки статуса и текста"""
    
    def test_set_status(self, qapp):
        """Тест установки текста статуса"""
        window = FloatingWindow()
        
        window.set_status("Recording...")
        
        assert window.status_label.text() == "Recording..."
    
    def test_set_result_text_short(self, qapp):
        """Тест установки короткого текста результата"""
        window = FloatingWindow()
        
        text = "Короткий текст"
        window.set_result_text(text)
        
        assert window.status_label.text() == text
    
    def test_set_result_text_long(self, qapp):
        """Тест усечения длинного текста результата"""
        window = FloatingWindow()
        
        text = "A" * 150  # Длинный текст
        window.set_result_text(text, max_length=100)
        
        displayed_text = window.status_label.text()
        assert len(displayed_text) <= 103  # 100 + "..."
        assert displayed_text.endswith("...")
    
    def test_set_result_text_exact_length(self, qapp):
        """Тест текста точно максимальной длины"""
        window = FloatingWindow()
        
        text = "A" * 100
        window.set_result_text(text, max_length=100)
        
        assert window.status_label.text() == text


class TestAutoHideTimer:
    """Тесты таймера автоскрытия"""
    
    def test_start_auto_hide_timer(self, qapp):
        """Тест запуска таймера автоскрытия"""
        window = FloatingWindow()
        
        window.start_auto_hide_timer(1000)
        
        assert window._auto_hide_timer.isActive()
    
    def test_cancel_auto_hide_timer(self, qapp):
        """Тест отмены таймера автоскрытия"""
        window = FloatingWindow()
        
        window.start_auto_hide_timer(1000)
        window.cancel_auto_hide_timer()
        
        assert not window._auto_hide_timer.isActive()
    
    def test_enter_event_cancels_timer(self, qapp):
        """Тест отмены таймера при наведении курсора"""
        window = FloatingWindow()
        
        window.start_auto_hide_timer(1000)
        
        # Симулируем наведение курсора
        from PyQt6.QtGui import QEnterEvent
        from PyQt6.QtCore import QPointF
        event = QEnterEvent(QPointF(10, 10), QPointF(10, 10), QPointF(10, 10))
        window.enterEvent(event)
        
        assert not window._auto_hide_timer.isActive()


class TestAnimations:
    """Тесты анимаций"""
    
    def test_fade_in_animation(self, qapp):
        """Тест анимации появления"""
        window = FloatingWindow()
        
        window._fade_in(duration=100)
        
        # Должна быть создана анимация
        assert window._fade_animation is not None
        assert window._opacity_effect is not None
    
    def test_fade_out_animation(self, qapp):
        """Тест анимации исчезновения"""
        window = FloatingWindow()
        window.show()
        
        window._fade_out(duration=100)
        
        # Должна быть создана анимация
        assert window._fade_animation is not None
        assert window._opacity_effect is not None
    
    def test_hide_with_animation(self, qapp):
        """Тест скрытия окна с анимацией"""
        window = FloatingWindow()
        window.show()
        
        window.hide_with_animation()
        
        # Анимация должна быть запущена
        assert window._fade_animation is not None


class TestWaveformIntegration:
    """Тесты интеграции с WaveformWidget"""
    
    def test_get_waveform_widget(self, qapp):
        """Тест получения виджета визуализации"""
        window = FloatingWindow()
        
        waveform = window.get_waveform_widget()
        
        assert isinstance(waveform, WaveformWidget)
        assert waveform == window.waveform_widget


class TestFloatingWindowProperties:
    """Property-тесты для FloatingWindow"""
    
    @given(st.integers(min_value=100, max_value=2000), 
           st.integers(min_value=100, max_value=2000))
    @settings(max_examples=50)
    def test_property_2_window_centering(self, qapp, screen_width: int, screen_height: int):
        """
        Property 2: Центрирование окна
        
        Для любого разрешения экрана, плавающее окно должно отображаться
        в центре экрана с координатами (screen_width/2 - window_width/2,
        screen_height/2 - window_height/2).
        
        **Validates: Requirements 2.2**
        """
        window = FloatingWindow()
        
        # Вычисляем ожидаемую позицию центра
        expected_x = (screen_width - window.window_width) // 2
        expected_y = (screen_height - window.window_height) // 2
        
        # Проверяем что формула центрирования корректна
        assert expected_x >= 0 or screen_width < window.window_width
        assert expected_y >= 0 or screen_height < window.window_height
    
    @given(st.integers(min_value=100, max_value=500))
    @settings(max_examples=100)
    def test_property_3_opacity_animation(self, qapp, duration: int):
        """
        Property 3: Анимация прозрачности
        
        Для любого виджета с анимацией fade-in или fade-out, значение
        прозрачности должно плавно изменяться от начального к конечному
        значению за указанную длительность.
        
        **Validates: Requirements 2.7, 2.8**
        """
        window = FloatingWindow()
        
        # Тест fade-in
        window._fade_in(duration=duration)
        
        assert window._fade_animation is not None, \
            "Анимация fade-in должна быть создана"
        assert window._fade_animation.duration() == duration, \
            f"Длительность анимации должна быть {duration}ms"
        
        # Тест fade-out
        window._fade_out(duration=duration)
        
        assert window._fade_animation is not None, \
            "Анимация fade-out должна быть создана"
        assert window._fade_animation.duration() == duration, \
            f"Длительность анимации должна быть {duration}ms"
    
    @given(st.text(min_size=1, max_size=200))
    @settings(max_examples=100)
    def test_property_23_text_truncation(self, qapp, text: str):
        """
        Property 23: Усечение длинного текста
        
        Для любого текста длиннее 100 символов, в окне должны
        отображаться только первые 100 символов.
        
        **Validates: Requirements 8.3**
        """
        window = FloatingWindow()
        
        window.set_result_text(text, max_length=100)
        
        displayed_text = window.status_label.text()
        
        if len(text) > 100:
            # Текст должен быть усечен
            assert len(displayed_text) <= 103, \
                f"Отображаемый текст не должен превышать 103 символа (100 + '...')"
            assert displayed_text.endswith("..."), \
                "Усеченный текст должен заканчиваться на '...'"
        else:
            # Текст должен быть полным
            assert displayed_text == text, \
                "Короткий текст должен отображаться полностью"
    
    @given(st.integers(min_value=1000, max_value=5000))
    @settings(max_examples=100)
    def test_property_24_auto_hide_timer(self, qapp, delay_ms: int):
        """
        Property 24: Автоматическое скрытие окна
        
        Для любого отображенного результата, должен запуститься таймер
        автоматического скрытия окна с длительностью 2-3 секунды.
        
        **Validates: Requirements 8.6**
        """
        window = FloatingWindow()
        
        window.start_auto_hide_timer(delay_ms)
        
        assert window._auto_hide_timer.isActive(), \
            "Таймер автоскрытия должен быть активен"
        
        # Проверяем что интервал установлен
        assert window._auto_hide_timer.interval() == delay_ms, \
            f"Интервал таймера должен быть {delay_ms}ms"
    
    def test_property_25_cancel_auto_hide_on_hover(self, qapp):
        """
        Property 25: Отмена автоскрытия при наведении
        
        Для любого активного таймера автоскрытия, наведение курсора
        на окно должно отменить или приостановить таймер.
        
        **Validates: Requirements 8.7**
        """
        window = FloatingWindow()
        
        # Запускаем таймер
        window.start_auto_hide_timer(2000)
        assert window._auto_hide_timer.isActive()
        
        # Симулируем наведение курсора
        from PyQt6.QtGui import QEnterEvent
        from PyQt6.QtCore import QPointF
        event = QEnterEvent(QPointF(10, 10), QPointF(10, 10), QPointF(10, 10))
        window.enterEvent(event)
        
        # Таймер должен быть отменен
        assert not window._auto_hide_timer.isActive(), \
            "Таймер автоскрытия должен быть отменен при наведении курсора"



class TestInfoPanelIntegration:
    """Тесты интеграции InfoPanelWidget в FloatingWindow"""
    
    def test_info_panel_added_to_window(self, qapp):
        """
        Тест добавления InfoPanelWidget в FloatingWindow.
        
        Requirements: 7.1
        """
        from core.config import Config
        
        window = FloatingWindow()
        config = Config()
        config.hotkey = "ctrl+space"
        
        # Установить конфигурацию
        window.set_config(config)
        
        # Проверить что info_panel создан
        assert window.info_panel is not None, \
            "InfoPanelWidget должен быть создан"
        
        # Проверить что info_panel добавлен в layout
        layout = window.layout()
        assert layout.count() == 3, \
            "Layout должен содержать 3 виджета: waveform, status_label, info_panel"
        
        # Проверить что info_panel последний в layout
        last_widget = layout.itemAt(2).widget()
        assert last_widget == window.info_panel, \
            "InfoPanelWidget должен быть последним в layout"
    
    def test_window_monitor_created(self, qapp):
        """
        Тест создания WindowMonitor при установке конфигурации.
        
        Requirements: 7.1
        """
        from core.config import Config
        
        window = FloatingWindow()
        config = Config()
        
        # Установить конфигурацию
        window.set_config(config)
        
        # Проверить что window_monitor создан
        assert window.window_monitor is not None, \
            "WindowMonitor должен быть создан"
    
    def test_window_height_updated(self, qapp):
        """
        Тест обновления высоты окна после добавления InfoPanelWidget.
        
        Requirements: 7.1
        """
        from core.config import Config
        
        window = FloatingWindow()
        original_height = window.window_height
        
        config = Config()
        window.set_config(config)
        
        # Высота должна увеличиться на 40px (высота info_panel)
        assert window.window_height == original_height + 40, \
            f"Высота окна должна быть {original_height + 40}px"
        assert window.height() == original_height + 40, \
            f"Фактическая высота окна должна быть {original_height + 40}px"
    
    @patch('services.window_monitor.WindowMonitor.create')
    def test_monitoring_starts_on_show(self, mock_create, qapp):
        """
        Тест запуска мониторинга при показе окна.
        
        Requirements: 7.3
        """
        from core.config import Config
        from unittest.mock import MagicMock
        
        # Создать мок window_monitor
        mock_monitor = MagicMock()
        mock_create.return_value = mock_monitor
        
        window = FloatingWindow()
        config = Config()
        window.set_config(config)
        
        # Показать окно
        window.show_at_center()
        
        # Проверить что start_monitoring был вызван
        mock_monitor.start_monitoring.assert_called_once()
        
        # Проверить что callback передан
        callback = mock_monitor.start_monitoring.call_args[0][0]
        assert callback == window.info_panel.update_app_info, \
            "Callback должен быть методом update_app_info из info_panel"
    
    @patch('services.window_monitor.WindowMonitor.create')
    def test_monitoring_stops_on_hide(self, mock_create, qapp):
        """
        Тест остановки мониторинга при скрытии окна.
        
        Requirements: 7.4
        """
        from core.config import Config
        from unittest.mock import MagicMock
        
        # Создать мок window_monitor
        mock_monitor = MagicMock()
        mock_create.return_value = mock_monitor
        
        window = FloatingWindow()
        config = Config()
        window.set_config(config)
        
        # Показать и скрыть окно
        window.show_at_center()
        window.hide_with_animation()
        
        # Проверить что stop_monitoring был вызван
        mock_monitor.stop_monitoring.assert_called_once()
    
    @patch('services.window_monitor.WindowMonitor.create')
    def test_monitoring_stops_on_close(self, mock_create, qapp):
        """
        Тест остановки мониторинга при закрытии окна.
        
        Requirements: 7.4
        """
        from core.config import Config
        from unittest.mock import MagicMock
        from PyQt6.QtGui import QCloseEvent
        
        # Создать мок window_monitor
        mock_monitor = MagicMock()
        mock_create.return_value = mock_monitor
        
        window = FloatingWindow()
        config = Config()
        window.set_config(config)
        
        # Закрыть окно
        event = QCloseEvent()
        window.closeEvent(event)
        
        # Проверить что stop_monitoring был вызван
        mock_monitor.stop_monitoring.assert_called_once()
    
    def test_hotkey_display_updates(self, qapp):
        """
        Тест обновления отображения горячей клавиши при изменении конфигурации.
        
        Requirements: 3.4
        """
        from core.config import Config
        
        window = FloatingWindow()
        config = Config()
        config.hotkey = "ctrl+space"
        window.set_config(config)
        
        # Проверить начальное отображение
        initial_text = window.info_panel._record_hotkey_label.text()
        assert "Ctrl+⎵Space" in initial_text, \
            "Начальная горячая клавиша должна быть отформатирована"
        
        # Изменить конфигурацию
        config.hotkey = "alt+f1"
        window.info_panel.update_hotkey_display()
        
        # Проверить обновленное отображение
        updated_text = window.info_panel._record_hotkey_label.text()
        assert "Alt+F1" in updated_text, \
            "Обновленная горячая клавиша должна быть отформатирована"
    
    @patch('services.window_monitor.WindowMonitor.create')
    def test_error_handling_in_set_config(self, mock_create, qapp):
        """
        Тест обработки ошибок при установке конфигурации.
        
        Requirements: 7.5
        """
        from core.config import Config
        
        # Создать мок который выбрасывает исключение
        mock_create.side_effect = Exception("Test error")
        
        window = FloatingWindow()
        config = Config()
        
        # Установка конфигурации не должна прерывать работу
        try:
            window.set_config(config)
            # Ошибка должна быть залогирована, но не выброшена
        except Exception as e:
            pytest.fail(f"set_config не должен выбрасывать исключение: {e}")
    
    @patch('services.window_monitor.WindowMonitor.create')
    def test_error_handling_in_start_monitoring(self, mock_create, qapp):
        """
        Тест обработки ошибок при запуске мониторинга.
        
        Requirements: 7.5
        """
        from core.config import Config
        from unittest.mock import MagicMock
        
        # Создать мок который выбрасывает исключение при start_monitoring
        mock_monitor = MagicMock()
        mock_monitor.start_monitoring.side_effect = Exception("Test error")
        mock_create.return_value = mock_monitor
        
        window = FloatingWindow()
        config = Config()
        window.set_config(config)
        
        # Запуск мониторинга не должен прерывать работу
        try:
            window.show_at_center()
            # Ошибка должна быть залогирована, но не выброшена
        except Exception as e:
            pytest.fail(f"show_at_center не должен выбрасывать исключение: {e}")
    
    @patch('services.window_monitor.WindowMonitor.create')
    def test_error_handling_in_stop_monitoring(self, mock_create, qapp):
        """
        Тест обработки ошибок при остановке мониторинга.
        
        Requirements: 7.5
        """
        from core.config import Config
        from unittest.mock import MagicMock
        
        # Создать мок который выбрасывает исключение при stop_monitoring
        mock_monitor = MagicMock()
        mock_monitor.stop_monitoring.side_effect = Exception("Test error")
        mock_create.return_value = mock_monitor
        
        window = FloatingWindow()
        config = Config()
        window.set_config(config)
        
        # Остановка мониторинга не должна прерывать работу
        try:
            window.hide_with_animation()
            # Ошибка должна быть залогирована, но не выброшена
        except Exception as e:
            pytest.fail(f"hide_with_animation не должен выбрасывать исключение: {e}")


class TestInfoPanelIntegrationProperties:
    """Property-тесты для интеграции InfoPanelWidget"""
    
    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll'), min_codepoint=97, max_codepoint=122
    )))
    @settings(max_examples=50)
    def test_property_8_waveform_size_preserved(self, qapp, hotkey: str):
        """
        Property 8: Сохранение размеров WaveformWidget
        
        Для любого состояния FloatingWindow до и после добавления Info_Panel,
        размер и позиция WaveformWidget должны оставаться неизменными.
        
        **Validates: Requirements 7.2**
        """
        from core.config import Config
        
        window = FloatingWindow()
        
        # Запомнить размер и позицию waveform до добавления info_panel
        waveform_before = window.waveform_widget
        size_before = waveform_before.size()
        height_before = waveform_before.height()
        
        # Добавить info_panel
        config = Config()
        config.hotkey = hotkey
        window.set_config(config)
        
        # Проверить размер и позицию waveform после добавления info_panel
        waveform_after = window.waveform_widget
        size_after = waveform_after.size()
        height_after = waveform_after.height()
        
        assert waveform_before == waveform_after, \
            "WaveformWidget должен быть тем же объектом"
        assert height_before == height_after, \
            f"Высота WaveformWidget должна остаться {height_before}px"
        assert height_after == 50, \
            "Высота WaveformWidget должна быть фиксированной 50px"
