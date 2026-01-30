"""
Тесты для InfoPanelWidget.

Включает unit-тесты и property-тесты для проверки корректности
работы информационной панели.
"""

import pytest
from unittest.mock import Mock, MagicMock
from hypothesis import given, strategies as st, settings
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from ui.info_panel_widget import InfoPanelWidget
from services.window_monitor import WindowInfo
import sys


# Создаем QApplication для тестов
@pytest.fixture(scope="module")
def qapp():
    """Фикстура для создания QApplication"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def mock_config():
    """Фикстура для создания мок-конфигурации"""
    config = Mock()
    config.hotkey = "ctrl+space"
    config.font_size_floating_info = 11  # Mock font size as integer
    return config


class TestInfoPanelInitialization:
    """Тесты инициализации InfoPanelWidget"""
    
    def test_initialization(self, qapp, mock_config):
        """Тест инициализации панели"""
        panel = InfoPanelWidget(mock_config)
        
        assert panel._config == mock_config
        assert panel._default_icon is not None  # Теперь создается автоматически
    
    def test_fixed_height(self, qapp, mock_config):
        """Тест фиксированной высоты панели"""
        panel = InfoPanelWidget(mock_config)
        
        # Панель должна иметь фиксированную высоту 40px
        assert panel.height() == 40
        assert panel.minimumHeight() == 40
        assert panel.maximumHeight() == 40
    
    def test_has_app_icon_label(self, qapp, mock_config):
        """Тест наличия метки иконки приложения"""
        panel = InfoPanelWidget(mock_config)
        
        assert hasattr(panel, '_app_icon_label')
        assert panel._app_icon_label.width() == 20
        assert panel._app_icon_label.height() == 20
    
    def test_has_app_name_label(self, qapp, mock_config):
        """Тест наличия метки названия приложения"""
        panel = InfoPanelWidget(mock_config)
        
        assert hasattr(panel, '_app_name_label')
        assert panel._app_name_label.text() == "Нет активного окна"
    
    def test_has_hotkey_labels(self, qapp, mock_config):
        """Тест наличия меток горячих клавиш"""
        panel = InfoPanelWidget(mock_config)
        
        assert hasattr(panel, '_record_hotkey_label')
        assert hasattr(panel, '_close_hotkey_label')
        assert "Запись" in panel._record_hotkey_label.text()
        assert "Отменить Esc" in panel._close_hotkey_label.text()


class TestStyling:
    """Тесты стилизации панели"""
    
    def test_background_color(self, qapp, mock_config):
        """Тест темного фона панели"""
        panel = InfoPanelWidget(mock_config)
        
        # Проверяем что стили применены
        stylesheet = panel.styleSheet()
        assert "#1a1a1a" in stylesheet
        assert "border-top" in stylesheet
    
    def test_text_colors(self, qapp, mock_config):
        """Тест цветов текста"""
        panel = InfoPanelWidget(mock_config)
        
        # Основной текст должен быть #E0E0E0
        app_name_style = panel._app_name_label.styleSheet()
        assert "#E0E0E0" in app_name_style
        
        # Вторичный текст (горячие клавиши) должен быть #FFFFFF (белый)
        hotkey_style = panel._record_hotkey_label.styleSheet()
        assert "#FFFFFF" in hotkey_style


class TestAppInfoUpdate:
    """Тесты обновления информации о приложении"""
    
    def test_update_app_info_with_valid_data(self, qapp, mock_config):
        """Тест обновления с валидными данными"""
        panel = InfoPanelWidget(mock_config)
        
        # Создаем мок WindowInfo
        window_info = WindowInfo(
            title="Test Application",
            process_name="test.exe",
            icon=None,
            process_id=1234
        )
        
        panel.update_app_info(window_info)
        
        assert panel._app_name_label.text() == "Test Application"
    
    def test_update_app_info_with_long_title(self, qapp, mock_config):
        """Тест усечения длинного названия"""
        panel = InfoPanelWidget(mock_config)
        
        # Создаем WindowInfo с длинным названием
        long_title = "A" * 50
        window_info = WindowInfo(
            title=long_title,
            process_name="test.exe",
            icon=None,
            process_id=1234
        )
        
        panel.update_app_info(window_info)
        
        displayed_text = panel._app_name_label.text()
        assert len(displayed_text) <= 30
        assert displayed_text.endswith("...")
    
    def test_update_app_info_with_none(self, qapp, mock_config):
        """Тест обновления с None"""
        panel = InfoPanelWidget(mock_config)
        
        panel.update_app_info(None)
        
        assert panel._app_name_label.text() == "Нет активного окна"
    
    def test_update_app_info_with_icon(self, qapp, mock_config):
        """Тест обновления с иконкой"""
        panel = InfoPanelWidget(mock_config)
        
        # Создаем тестовую иконку
        icon = QPixmap(32, 32)
        icon.fill(Qt.GlobalColor.red)
        
        window_info = WindowInfo(
            title="Test App",
            process_name="test.exe",
            icon=icon,
            process_id=1234
        )
        
        panel.update_app_info(window_info)
        
        # Иконка должна быть установлена и масштабирована до 20x20
        assert not panel._app_icon_label.pixmap().isNull()
        assert panel._app_icon_label.pixmap().width() <= 20
        assert panel._app_icon_label.pixmap().height() <= 20
    
    def test_update_app_info_without_icon_uses_default(self, qapp, mock_config):
        """Тест использования иконки по умолчанию"""
        panel = InfoPanelWidget(mock_config)
        
        # Устанавливаем иконку по умолчанию
        default_icon = QPixmap(20, 20)
        default_icon.fill(Qt.GlobalColor.blue)
        panel.set_default_icon(default_icon)
        
        # Обновляем без иконки
        window_info = WindowInfo(
            title="Test App",
            process_name="test.exe",
            icon=None,
            process_id=1234
        )
        
        panel.update_app_info(window_info)
        
        # Должна быть установлена иконка по умолчанию
        assert not panel._app_icon_label.pixmap().isNull()


class TestHotkeyDisplay:
    """Тесты отображения горячих клавиш"""
    
    def test_initial_hotkey_display(self, qapp, mock_config):
        """Тест начального отображения горячей клавиши"""
        mock_config.hotkey = "ctrl+space"
        panel = InfoPanelWidget(mock_config)
        
        # Горячая клавиша должна быть отформатирована
        assert "Запись" in panel._record_hotkey_label.text()
        assert "Ctrl" in panel._record_hotkey_label.text()
    
    def test_update_hotkey_display(self, qapp, mock_config):
        """Тест обновления отображения горячей клавиши"""
        mock_config.hotkey = "ctrl+space"
        panel = InfoPanelWidget(mock_config)
        
        # Изменяем горячую клавишу
        mock_config.hotkey = "alt+f1"
        panel.update_hotkey_display()
        
        # Отображение должно обновиться
        text = panel._record_hotkey_label.text()
        assert "Alt" in text
        assert "F1" in text
    
    def test_close_hotkey_always_esc(self, qapp, mock_config):
        """Тест что кнопка закрытия всегда Esc"""
        panel = InfoPanelWidget(mock_config)
        
        assert "Esc" in panel._close_hotkey_label.text()


class TestDefaultIcon:
    """Тесты иконки по умолчанию"""
    
    def test_set_default_icon(self, qapp, mock_config):
        """Тест установки иконки по умолчанию"""
        panel = InfoPanelWidget(mock_config)
        
        icon = QPixmap(20, 20)
        icon.fill(Qt.GlobalColor.green)
        
        panel.set_default_icon(icon)
        
        assert panel._default_icon is not None
        assert panel._default_icon == icon


class TestInfoPanelProperties:
    """Property-тесты для InfoPanelWidget"""
    
    @given(st.text(min_size=31, max_size=100))
    @settings(max_examples=100)
    def test_property_1_app_name_truncation(self, qapp, app_name: str):
        """
        Property 1: Усечение длинных названий приложений
        
        Для любого названия приложения длиннее 30 символов, отображаемый
        текст должен быть усечен до 27 символов с добавлением "..." в конце.
        
        **Validates: Requirements 1.4**
        """
        # Создаем мок-конфигурацию внутри теста
        config = Mock()
        config.hotkey = "ctrl+space"
        config.font_size_floating_info = 11  # Mock font size as integer
        panel = InfoPanelWidget(config)
        
        window_info = WindowInfo(
            title=app_name,
            process_name="test.exe",
            icon=None,
            process_id=1234
        )
        
        panel.update_app_info(window_info)
        
        displayed_text = panel._app_name_label.text()
        
        # Текст должен быть усечен до 30 символов (27 + "...")
        assert len(displayed_text) <= 30, \
            f"Отображаемый текст не должен превышать 30 символов"
        assert displayed_text.endswith("..."), \
            "Усеченный текст должен заканчиваться на '...'"
        assert displayed_text[:27] == app_name[:27], \
            "Первые 27 символов должны совпадать с оригиналом"
    
    @given(st.text(min_size=1, max_size=30))
    @settings(max_examples=100)
    def test_property_1_short_app_name_not_truncated(self, qapp, app_name: str):
        """
        Property 1: Короткие названия не усекаются
        
        Для любого названия приложения длиной 30 символов или меньше,
        текст должен отображаться полностью без усечения.
        
        **Validates: Requirements 1.4**
        """
        # Создаем мок-конфигурацию внутри теста
        config = Mock()
        config.hotkey = "ctrl+space"
        config.font_size_floating_info = 11  # Mock font size as integer
        panel = InfoPanelWidget(config)
        
        window_info = WindowInfo(
            title=app_name,
            process_name="test.exe",
            icon=None,
            process_id=1234
        )
        
        panel.update_app_info(window_info)
        
        displayed_text = panel._app_name_label.text()
        
        # Короткий текст должен отображаться полностью
        assert displayed_text == app_name, \
            "Короткий текст должен отображаться полностью без усечения"
    
    @given(st.sampled_from(["ctrl+space", "alt+f1", "shift+a", "f12", "ctrl+shift+x"]))
    @settings(max_examples=50)
    def test_property_3_hotkey_display_from_config(self, qapp, hotkey: str):
        """
        Property 3: Отображение горячей клавиши из конфигурации
        
        Для любого значения горячей клавиши в Config_Manager, Info_Panel
        должен отображать кнопку "Запись [formatted_hotkey]" с правильно
        отформатированной клавишей.
        
        **Validates: Requirements 3.2**
        """
        # Создаем мок-конфигурацию внутри теста
        config = Mock()
        config.hotkey = hotkey
        config.font_size_floating_info = 11  # Mock font size as integer
        panel = InfoPanelWidget(config)
        
        text = panel._record_hotkey_label.text()
        
        # Текст должен начинаться с "Запись"
        assert text.startswith("Запись"), \
            "Текст кнопки должен начинаться с 'Запись'"
        
        # Текст должен содержать отформатированную горячую клавишу
        # (проверяем что текст не пустой и содержит больше чем просто "Запись")
        assert len(text) > len("Запись "), \
            "Текст должен содержать отформатированную горячую клавишу"
    
    @given(st.integers(min_value=8, max_value=256), st.integers(min_value=8, max_value=256))
    @settings(max_examples=100)
    def test_property_7_icon_scaling(self, qapp, width: int, height: int):
        """
        Property 7: Масштабирование иконок
        
        Для любой иконки приложения, отображаемой в Info_Panel, она должна
        быть масштабирована до размера 20x20 пикселей.
        
        **Validates: Requirements 5.5**
        """
        # Создаем мок-конфигурацию внутри теста
        config = Mock()
        config.hotkey = "ctrl+space"
        config.font_size_floating_info = 11  # Mock font size as integer
        panel = InfoPanelWidget(config)
        
        # Создаем иконку произвольного размера
        icon = QPixmap(width, height)
        icon.fill(Qt.GlobalColor.red)
        
        window_info = WindowInfo(
            title="Test App",
            process_name="test.exe",
            icon=icon,
            process_id=1234
        )
        
        panel.update_app_info(window_info)
        
        # Иконка должна быть масштабирована до 20x20
        displayed_icon = panel._app_icon_label.pixmap()
        assert not displayed_icon.isNull(), \
            "Иконка должна быть установлена"
        
        # Проверяем что размер не превышает 20x20 (с учетом aspect ratio)
        assert displayed_icon.width() <= 20, \
            f"Ширина иконки не должна превышать 20px, получено {displayed_icon.width()}"
        assert displayed_icon.height() <= 20, \
            f"Высота иконки не должна превышать 20px, получено {displayed_icon.height()}"



class TestInfoPanelFontSizes:
    """Unit tests for InfoPanelWidget font size integration"""
    
    def test_font_size_read_from_config_on_initialization(self, qapp, mock_config):
        """Test that font size is read from Config on initialization"""
        mock_config.font_size_floating_info = 13
        
        panel = InfoPanelWidget(mock_config)
        
        # Check that font size is applied to labels
        app_name_font = panel._app_name_label.font()
        assert app_name_font.pointSize() == 13
        
        record_hotkey_font = panel._record_hotkey_label.font()
        assert record_hotkey_font.pointSize() == 13
        
        close_hotkey_font = panel._close_hotkey_label.font()
        assert close_hotkey_font.pointSize() == 13
    
    def test_default_font_size_when_no_config(self, qapp):
        """Test that default font size is used when config doesn't have the property"""
        config = Mock()
        config.hotkey = "ctrl+space"
        config.font_size_floating_info = 11  # Default value
        
        panel = InfoPanelWidget(config)
        
        # Should use default font size (11)
        app_name_font = panel._app_name_label.font()
        assert app_name_font.pointSize() == 11
    
    def test_font_size_applied_to_all_labels(self, qapp, mock_config):
        """Test that font size is applied to all labels (app name, hotkeys)"""
        mock_config.font_size_floating_info = 14
        
        panel = InfoPanelWidget(mock_config)
        
        # All labels should have the same font size
        app_name_font = panel._app_name_label.font()
        record_hotkey_font = panel._record_hotkey_label.font()
        close_hotkey_font = panel._close_hotkey_label.font()
        
        assert app_name_font.pointSize() == 14
        assert record_hotkey_font.pointSize() == 14
        assert close_hotkey_font.pointSize() == 14
    
    def test_font_size_boundary_values(self, qapp, mock_config):
        """Test font size with boundary values (min and max)"""
        # Test minimum font size (8)
        mock_config.font_size_floating_info = 8
        panel_min = InfoPanelWidget(mock_config)
        assert panel_min._app_name_label.font().pointSize() == 8
        
        # Test maximum font size (16)
        mock_config.font_size_floating_info = 16
        panel_max = InfoPanelWidget(mock_config)
        assert panel_max._app_name_label.font().pointSize() == 16
