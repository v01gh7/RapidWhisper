"""
Окно настроек приложения RapidWhisper.

Предоставляет графический интерфейс для редактирования всех параметров
конфигурации из .env файла в стиле macOS с боковой панелью.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox,
    QPushButton, QGroupBox, QMessageBox, QWidget, QListWidget, QStackedWidget, QListWidgetItem,
    QScrollArea, QApplication, QCheckBox, QTextEdit, QGridLayout, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QFont, QIcon, QScreen, QPainter, QPainterPath, QRegion
from core.config import Config
from core.statistics_manager import StatisticsManager
from utils.logger import get_logger
from utils.i18n import t
from ui.hotkey_input import HotkeyInput
from ui.statistics_tab import StatisticsTab
from design_system.styled_window_mixin import StyledWindowMixin
from pathlib import Path
from typing import Optional, List, Dict, Any
import os

logger = get_logger()


class NoScrollComboBox(QComboBox):
    """
    QComboBox that ignores wheel events when not focused.
    This prevents accidental value changes when scrolling the page.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set focus policy to require click to focus
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def wheelEvent(self, event):
        """Override wheel event to ignore when not focused."""
        if self.hasFocus():
            # Allow wheel scrolling when focused
            super().wheelEvent(event)
        else:
            # Ignore wheel event and pass it to parent (for page scrolling)
            event.ignore()


class NoScrollSpinBox(QSpinBox):
    """
    QSpinBox that ignores wheel events when not focused.
    This prevents accidental value changes when scrolling the page.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set focus policy to require click to focus
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def wheelEvent(self, event):
        """Override wheel event to ignore when not focused."""
        if self.hasFocus():
            # Allow wheel scrolling when focused
            super().wheelEvent(event)
        else:
            # Ignore wheel event and pass it to parent (for page scrolling)
            event.ignore()


class NoScrollDoubleSpinBox(QDoubleSpinBox):
    """
    QDoubleSpinBox that ignores wheel events when not focused.
    This prevents accidental value changes when scrolling the page.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set focus policy to require click to focus
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def wheelEvent(self, event):
        """Override wheel event to ignore when not focused."""
        if self.hasFocus():
            # Allow wheel scrolling when focused
            super().wheelEvent(event)
        else:
            # Ignore wheel event and pass it to parent (for page scrolling)
            event.ignore()


class SettingsWindow(QDialog, StyledWindowMixin):
    """
    Окно настроек приложения.
    
    Позволяет редактировать все параметры конфигурации и сохранять их в .env файл.
    
    Signals:
        settings_saved: Сигнал при сохранении настроек
    """
    
    settings_saved = pyqtSignal()
    
    def __init__(self, config: Config, statistics_manager: StatisticsManager = None, tray_icon=None, parent=None):
        """
        Инициализирует окно настроек.
        
        Args:
            config: Текущая конфигурация приложения
            statistics_manager: Менеджер статистики использования (опционально)
            tray_icon: Иконка трея для показа уведомлений
            parent: Родительский виджет
        """
        QDialog.__init__(self, parent)
        StyledWindowMixin.__init__(self)
        self.config = config
        self.statistics_manager = statistics_manager
        self.tray_icon = tray_icon
        self.setWindowTitle(t("settings.title"))
        self.setMinimumWidth(950)  # Увеличена ширина для новых кнопок
        self.setMinimumHeight(650)  # Увеличена высота
        
        # Установить иконку окна
        self._set_window_icon()
        
        # Установить максимальную высоту (высота экрана - 160 пикселей)
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            max_height = screen_geometry.height() - 160
            self.setMaximumHeight(max_height)
        
        # Set translucent background BEFORE applying unified style
        # This is critical for Windows to properly render the transparent window
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # IMPORTANT: Set WA_OpaquePaintEvent to False for proper transparency rendering
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        
        # Apply unified styling from mixin (Task 4.2)
        from design_system.style_constants import StyleConstants
        opacity = getattr(config, 'window_opacity', StyleConstants.OPACITY_DEFAULT)
        self.apply_unified_style(opacity=opacity, stay_on_top=False)
        
        # Apply child widget styles (must be called AFTER apply_unified_style)
        # This will merge with the mixin's stylesheet
        self._apply_style()
        
        # Создать интерфейс
        self._create_ui()
        
        # Загрузить текущие значения
        self._load_values()
    
    def showEvent(self, event):
        """
        Override showEvent to ensure proper rendering on Windows.
        
        This is critical for Windows to properly render the transparent window
        with blur effects and rounded corners.
        """
        super().showEvent(event)
        self.repaint()
        self.update()
    
    def paintEvent(self, event):
        """
        Custom paint event to properly render rounded corners and prevent white artifacts.
        
        This creates a clipping region with rounded corners to ensure the window
        background is properly masked, preventing white corner artifacts on Windows.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create rounded rectangle path
        from design_system.style_constants import StyleConstants
        path = QPainterPath()
        path.addRoundedRect(
            0, 0, 
            self.width(), self.height(),
            StyleConstants.BORDER_RADIUS, StyleConstants.BORDER_RADIUS
        )
        
        # Set clipping region to rounded rectangle
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)
        
        # Call parent's paintEvent
        super().paintEvent(event)
    
    def _set_window_icon(self):
        """Устанавливает иконку окна."""
        import sys
        
        # Определить путь к иконке
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        icon_path = os.path.join(base_path, 'public', 'RapidWhisper.ico')
        
        try:
            icon = QIcon(icon_path)
            if not icon.isNull():
                self.setWindowIcon(icon)
        except Exception:
            pass  # Игнорируем ошибки загрузки иконки
        """Устанавливает иконку окна."""
        import sys
        
        # Определить путь к иконке
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        icon_path = os.path.join(base_path, 'public', 'RapidWhisper.ico')
        
        try:
            icon = QIcon(icon_path)
            if not icon.isNull():
                self.setWindowIcon(icon)
        except Exception:
            pass  # Игнорируем ошибки загрузки иконки
    
    def _apply_style(self):
        """
        Применяет стиль к дочерним виджетам окна настроек.
        
        ВАЖНО: Этот метод объединяет стили миксина (для окна) со стилями
        дочерних виджетов. Вызывается ПОСЛЕ apply_unified_style().
        """
        # Получить размеры шрифтов из конфигурации
        label_font_size = self.config.font_size_settings_labels if hasattr(self.config, 'font_size_settings_labels') else 12
        title_font_size = self.config.font_size_settings_titles if hasattr(self.config, 'font_size_settings_titles') else 24
        
        # Get the mixin's background style
        from design_system.style_constants import StyleConstants
        bg_color = StyleConstants.get_background_color(self._opacity)
        
        # Combine mixin styles (window-level) with child widget styles
        # The mixin sets the window background, we add styles for child widgets
        self.setStyleSheet(f"""
            /* Window-level styles from mixin */
            QDialog {{
                background-color: {bg_color};
                border: {StyleConstants.BORDER_WIDTH}px solid {StyleConstants.BORDER_COLOR};
                border-radius: {StyleConstants.BORDER_RADIUS}px;
                color: #ffffff;
            }}
            QLabel {{
                color: #ffffff;
                font-size: {label_font_size}px;
            }}
            QLineEdit, QDoubleSpinBox {{
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 8px;
            }}
            QComboBox {{
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 8px;
            }}
            QLineEdit:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                border: 1px solid #0078d4;
            }}
            QPushButton {{
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1084d8;
            }}
            QPushButton:pressed {{
                background-color: #006cc1;
            }}
            QPushButton#cancelButton {{
                background-color: #3d3d3d;
            }}
            QPushButton#cancelButton:hover {{
                background-color: #4d4d4d;
            }}
            QGroupBox {{
                color: #ffffff;
                border: {StyleConstants.BORDER_WIDTH}px solid rgba(255, 255, 255, 80);
                border-radius: 8px;
                margin-top: 20px;
                font-weight: bold;
                padding-top: 20px;
                background-color: rgba(37, 37, 37, {int(self._opacity * 0.7)});
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 8px 16px;
                background-color: rgba(200, 200, 200, {int(self._opacity * 0.7)});
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                border: 1px solid rgba(255, 255, 255, 100);
            }}
            QListWidget {{
                background-color: rgba(26, 26, 26, {int(self._opacity * 0.9)});
                border: none;
                border-right: 1px solid rgba(255, 255, 255, 50);
                outline: none;
                padding: 8px 0px;
                color: #ffffff;
            }}
            QWidget#rightPanel {{
                background-color: rgba(26, 26, 26, {int(self._opacity * 0.9)});
                border: none;
            }}
            QListWidget::item {{
                color: #ffffff;
                padding: 10px 16px;
                border-radius: 6px;
                margin: 2px 8px;
                background-color: transparent;
            }}
            QListWidget::item:selected {{
                background-color: rgba(0, 120, 212, {int(self._opacity * 0.8)});
                color: #ffffff;
            }}
            QListWidget::item:hover:!selected {{
                background-color: rgba(45, 45, 45, {int(self._opacity * 0.6)});
                color: #ffffff;
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollArea > QWidget {{
                background-color: transparent;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: rgba(30, 30, 30, {int(self._opacity * 0.6)});
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #3d3d3d;
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: #4d4d4d;
            }}
            QScrollBar::handle:vertical:pressed {{
                background-color: #0078d4;
            }}
            QLabel#pageTitle {{
                color: #ffffff;
                font-size: {title_font_size}px;
                font-weight: bold;
                padding: 12px 20px;
                background-color: rgba(45, 45, 45, {int(self._opacity * 0.8)});
                border-radius: 6px;
                border: 2px solid rgba(255, 255, 255, 100);
                margin-bottom: 8px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
            QLabel a {{
                color: #0078d4;
                text-decoration: none;
            }}
            QLabel a:hover {{
                color: #1084d8;
                text-decoration: underline;
            }}
        """)
    
    def _create_ui(self):
        """Создает интерфейс окна настроек в стиле macOS с боковой панелью."""
        # Create outer vertical layout to hold header and main content (Task 4.3)
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        
        # Add draggable header at the top (Task 4.3)
        header = self._create_header()
        outer_layout.addWidget(header)
        
        # Create main horizontal layout for sidebar and content
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Левая панель навигации
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(210)  # Увеличена ширина с 200 до 210 для предотвращения горизонтальной прокрутки
        self.sidebar.setSpacing(0)
        self.sidebar.setCursor(Qt.CursorShape.PointingHandCursor)  # Курсор "рука" для всего списка
        self.sidebar.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Не терять выделение при потере фокуса
        
        # Добавить пункты меню
        items = [
            (f"🤖 {t('settings.ai_provider.title')}", "ai"),
            (f"⚡ {t('settings.app.title')}", "app"),
            (f"🎤 {t('settings.audio.title')}", "audio"),
            (f"✨ {t('settings.processing.title')}", "processing"),
            (f"🌍 {t('settings.languages.title')}", "languages"),
            (f"🎨 {t('settings.ui_customization.title')}", "ui_customization"),
            (f"🎙️ {t('settings.recordings.title')}", "recordings"),
            (f"📊 {t('settings.statistics.title')}", "statistics"),  # Statistics tab
            (f"ℹ️ {t('settings.about.title')}", "about")
        ]
        
        for text, data in items:
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, data)
            self.sidebar.addItem(item)
        
        # Выбрать первый пункт
        self.sidebar.setCurrentRow(0)
        
        # Подключить сигнал переключения
        self.sidebar.currentRowChanged.connect(self._on_sidebar_changed)
        
        main_layout.addWidget(self.sidebar)
        
        # Правая панель с содержимым
        right_panel = QWidget()
        right_panel.setObjectName("rightPanel")  # Set object name for CSS targeting
        right_panel_layout = QVBoxLayout()
        right_panel_layout.setContentsMargins(32, 32, 32, 32)
        right_panel_layout.setSpacing(24)
        
        # Стек виджетов для разных страниц
        self.content_stack = QStackedWidget()
        
        # Создать страницы с прокруткой
        self.content_stack.addWidget(self._wrap_in_scroll_area(self._create_ai_page()))
        self.content_stack.addWidget(self._wrap_in_scroll_area(self._create_app_page()))
        self.content_stack.addWidget(self._wrap_in_scroll_area(self._create_audio_page()))
        self.content_stack.addWidget(self._wrap_in_scroll_area(self._create_processing_page()))
        self.content_stack.addWidget(self._wrap_in_scroll_area(self._create_languages_page()))
        self.content_stack.addWidget(self._wrap_in_scroll_area(self._create_ui_customization_page()))
        self.content_stack.addWidget(self._wrap_in_scroll_area(self._create_recordings_page()))
        
        # Add Statistics tab if statistics_manager is provided
        if self.statistics_manager:
            self.statistics_tab = StatisticsTab(self.statistics_manager)
            self.content_stack.addWidget(self._wrap_in_scroll_area(self.statistics_tab))
        else:
            # Add placeholder if no statistics manager
            placeholder = QWidget()
            placeholder_layout = QVBoxLayout()
            placeholder_label = QLabel(t('settings.statistics.no_data'))
            placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder_layout.addWidget(placeholder_label)
            placeholder.setLayout(placeholder_layout)
            self.content_stack.addWidget(self._wrap_in_scroll_area(placeholder))
        
        self.content_stack.addWidget(self._wrap_in_scroll_area(self._create_about_page()))
        
        right_panel_layout.addWidget(self.content_stack)
        
        # Кнопки внизу
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton(t("common.cancel"))
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)  # Курсор "рука"
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton(t("common.save"))
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)  # Курсор "рука"
        save_btn.clicked.connect(self._save_settings)
        buttons_layout.addWidget(save_btn)
        
        right_panel_layout.addLayout(buttons_layout)
        
        right_panel.setLayout(right_panel_layout)
        main_layout.addWidget(right_panel, 1)
        
        # Add main layout to outer layout (Task 4.3)
        outer_layout.addLayout(main_layout)
        
        self.setLayout(outer_layout)
    
    def _on_sidebar_changed(self, index: int):
        """Обработчик переключения пунктов в боковой панели."""
        if index >= 0:  # Проверка что индекс валидный
            self.content_stack.setCurrentIndex(index)
            # Убедиться что элемент остается выделенным
            self.sidebar.setCurrentRow(index)
    
    def _wrap_in_scroll_area(self, widget: QWidget) -> QScrollArea:
        """
        Оборачивает виджет в QScrollArea с красивым скроллом.
        
        Args:
            widget: Виджет для обертывания
            
        Returns:
            QScrollArea: Область прокрутки с виджетом
        """
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        return scroll
    
    def _create_header(self) -> QWidget:
        """
        Create a draggable header for the frameless window (Task 4.3)
        
        Returns:
            QWidget: Header widget with fixed height, distinct styling, and window control buttons
        
        Requirements: 2.3
        """
        header = QWidget()
        header.setFixedHeight(35)
        
        # Create horizontal layout for header content
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 0, 5, 0)
        header_layout.setSpacing(0)
        
        # Add title label
        title_label = QLabel("RapidWhisper - " + t("settings.title"))
        title_font = QFont("Segoe UI", 10)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff; background: transparent;")
        header_layout.addWidget(title_label)
        
        # Add stretch to push buttons to the right
        header_layout.addStretch()
        
        # Get icon paths
        import sys
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        icons_path = os.path.join(base_path, 'public', 'icons')
        
        # Create window control buttons
        # Minimize button
        minimize_btn = QPushButton()
        minimize_btn.setFixedSize(35, 35)
        minimize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        minimize_icon = QIcon(os.path.join(icons_path, 'minimize.svg'))
        minimize_btn.setIcon(minimize_icon)
        minimize_btn.setIconSize(minimize_btn.size() * 0.5)
        minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30);
                border-radius: 4px;
            }
        """)
        minimize_btn.clicked.connect(self.showMinimized)
        header_layout.addWidget(minimize_btn)
        
        # Maximize/Restore button
        self.maximize_btn = QPushButton()
        self.maximize_btn.setFixedSize(35, 35)
        self.maximize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.maximize_icon = QIcon(os.path.join(icons_path, 'maximize.svg'))
        self.restore_icon = QIcon(os.path.join(icons_path, 'restore.svg'))
        self.maximize_btn.setIcon(self.maximize_icon)
        self.maximize_btn.setIconSize(self.maximize_btn.size() * 0.5)
        self.maximize_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30);
                border-radius: 4px;
            }
        """)
        self.maximize_btn.clicked.connect(self._toggle_maximize)
        header_layout.addWidget(self.maximize_btn)
        
        # Close button
        close_btn = QPushButton()
        close_btn.setFixedSize(35, 35)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_icon = QIcon(os.path.join(icons_path, 'close.svg'))
        close_btn.setIcon(close_icon)
        close_btn.setIconSize(close_btn.size() * 0.5)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(232, 17, 35, 200);
                border-radius: 4px;
            }
        """)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        
        # Style the header to be visually distinct
        header_opacity = int(self._opacity * 0.8)
        header.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(40, 40, 40, {header_opacity});
                border: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }}
        """)
        return header
    
    def _toggle_maximize(self):
        """Toggle between maximized and normal window state."""
        if self.isMaximized():
            self.showNormal()
            self.maximize_btn.setIcon(self.maximize_icon)
        else:
            self.showMaximized()
            self.maximize_btn.setIcon(self.restore_icon)
    
    def _create_ai_page(self) -> QWidget:
        """Создает страницу настроек AI Provider."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel(t("settings.ai_provider.title"))
        title.setObjectName("pageTitle")  # Применить стиль
        layout.addWidget(title)
        
        # Группа: Выбор провайдера
        provider_group = QGroupBox(t("settings.ai_provider.title"))
        provider_layout = QFormLayout()
        provider_layout.setSpacing(12)
        
        self.provider_combo = NoScrollComboBox()
        self.provider_combo.addItems(["groq", "openai", "glm", "custom"])
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
        self.provider_combo.setCursor(Qt.CursorShape.PointingHandCursor)  # Курсор "рука"
        provider_layout.addRow(t("settings.ai_provider.label"), self.provider_combo)
        
        provider_group.setLayout(provider_layout)
        layout.addWidget(provider_group)
        
        # Группа: API ключи
        keys_group = QGroupBox(t("settings.ai_provider.title"))
        keys_layout = QFormLayout()
        
        # Groq API Key
        groq_layout = QHBoxLayout()
        self.groq_key_edit = QLineEdit()
        self.groq_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.groq_key_edit.setPlaceholderText(t("settings.ai_provider.groq_key_placeholder"))
        groq_layout.addWidget(self.groq_key_edit)
        
        groq_show_btn = QPushButton("👁")
        groq_show_btn.setMaximumWidth(40)
        groq_show_btn.setCheckable(True)
        groq_show_btn.setCursor(Qt.CursorShape.PointingHandCursor)  # Курсор "рука"
        groq_show_btn.toggled.connect(
            lambda checked: self.groq_key_edit.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            )
        )
        groq_layout.addWidget(groq_show_btn)
        
        groq_label = QLabel(t("settings.ai_provider.groq_key"))
        groq_label.setToolTip(t("settings.ai_provider.groq_key_tooltip"))
        keys_layout.addRow(groq_label, groq_layout)
        
        # OpenAI API Key
        openai_layout = QHBoxLayout()
        self.openai_key_edit = QLineEdit()
        self.openai_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key_edit.setPlaceholderText(t("settings.ai_provider.openai_key_placeholder"))
        openai_layout.addWidget(self.openai_key_edit)
        
        openai_show_btn = QPushButton("👁")
        openai_show_btn.setMaximumWidth(40)
        openai_show_btn.setCheckable(True)
        openai_show_btn.setCursor(Qt.CursorShape.PointingHandCursor)  # Курсор "рука"
        openai_show_btn.toggled.connect(
            lambda checked: self.openai_key_edit.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            )
        )
        openai_layout.addWidget(openai_show_btn)
        
        openai_label = QLabel(t("settings.ai_provider.openai_key"))
        openai_label.setToolTip(t("settings.ai_provider.openai_key_tooltip"))
        keys_layout.addRow(openai_label, openai_layout)
        
        # GLM API Key
        glm_layout = QHBoxLayout()
        self.glm_key_edit = QLineEdit()
        self.glm_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.glm_key_edit.setPlaceholderText(t("settings.ai_provider.glm_key_placeholder"))
        glm_layout.addWidget(self.glm_key_edit)
        
        glm_show_btn = QPushButton("👁")
        glm_show_btn.setMaximumWidth(40)
        glm_show_btn.setCheckable(True)
        glm_show_btn.setCursor(Qt.CursorShape.PointingHandCursor)  # Курсор "рука"
        glm_show_btn.toggled.connect(
            lambda checked: self.glm_key_edit.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            )
        )
        glm_layout.addWidget(glm_show_btn)
        
        glm_label = QLabel(t("settings.ai_provider.glm_key"))
        glm_label.setToolTip(t("settings.ai_provider.glm_key_tooltip"))
        keys_layout.addRow(glm_label, glm_layout)
        
        # Custom API Key
        custom_layout = QHBoxLayout()
        self.custom_key_edit = QLineEdit()
        self.custom_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.custom_key_edit.setPlaceholderText(t("settings.ai_provider.custom_key_placeholder"))
        custom_layout.addWidget(self.custom_key_edit)
        
        custom_show_btn = QPushButton("👁")
        custom_show_btn.setMaximumWidth(40)
        custom_show_btn.setCheckable(True)
        custom_show_btn.setCursor(Qt.CursorShape.PointingHandCursor)  # Курсор "рука"
        custom_show_btn.toggled.connect(
            lambda checked: self.custom_key_edit.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            )
        )
        custom_layout.addWidget(custom_show_btn)
        
        custom_label = QLabel(t("settings.ai_provider.custom_key"))
        custom_label.setToolTip(t("settings.ai_provider.custom_key_tooltip"))
        keys_layout.addRow(custom_label, custom_layout)
        
        # Custom Base URL
        self.custom_url_edit = QLineEdit()
        self.custom_url_edit.setPlaceholderText(t("settings.ai_provider.custom_url_placeholder"))
        custom_url_label = QLabel(t("settings.ai_provider.custom_url"))
        custom_url_label.setToolTip(t("settings.ai_provider.custom_url_tooltip"))
        keys_layout.addRow(custom_url_label, self.custom_url_edit)
        
        # Custom Model (используется для всех провайдеров если указано)
        self.custom_model_edit = QLineEdit()
        self.custom_model_edit.setPlaceholderText(t("settings.ai_provider.custom_model_placeholder"))
        custom_model_label = QLabel(t("settings.ai_provider.custom_model"))
        custom_model_label.setToolTip(t("settings.ai_provider.custom_model_tooltip"))
        keys_layout.addRow(custom_model_label, self.custom_model_edit)
        
        keys_group.setLayout(keys_layout)
        layout.addWidget(keys_group)
        
        # Группа: Модель транскрипции
        transcription_group = QGroupBox("Transcription Model")
        transcription_layout = QFormLayout()
        transcription_layout.setSpacing(12)
        
        # Выбор модели транскрипции
        self.transcription_model_combo = NoScrollComboBox()
        self.transcription_model_combo.addItems([
            "whisper-large-v3 (Groq default)",
            "whisper-large-v3-turbo",
            "distil-whisper-large-v3-en",
            "whisper-1 (OpenAI default)",
            "glm-4-voice (GLM default)"
        ])
        self.transcription_model_combo.setEditable(True)  # Позволяет вводить кастомную модель
        self.transcription_model_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        
        transcription_model_label = QLabel("Transcription Model")
        transcription_model_label.setToolTip(
            "Select transcription model or enter custom model name.\n"
            "Leave empty to use provider default:\n"
            "• Groq: whisper-large-v3\n"
            "• OpenAI: whisper-1\n"
            "• GLM: glm-4-voice"
        )
        transcription_layout.addRow(transcription_model_label, self.transcription_model_combo)
        
        transcription_group.setLayout(transcription_layout)
        layout.addWidget(transcription_group)
        
        # Информация с кликабельными ссылками
        info_label = QLabel(t("settings.ai_provider.info"))
        info_label.setWordWrap(True)
        info_label.setOpenExternalLinks(True)  # Открывать ссылки в браузере
        info_label.setToolTip(t("settings.ai_provider.info_tooltip") if "info_tooltip" in t("settings.ai_provider") else "Click link to open in browser")
        info_label.setStyleSheet(
            "color: #888888; "
            "font-size: 11px; "
            "padding: 8px; "
            "background-color: #2d2d2d; "
            "border-radius: 4px;"
        )
        layout.addWidget(info_label)
        
        widget.setLayout(layout)
        return widget
    
    def _create_app_page(self) -> QWidget:
        """Создает страницу настроек приложения."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)  # Возвращен отступ в 20
        
        # Заголовок
        title = QLabel(t("settings.app.title"))
        title.setObjectName("pageTitle")  # Применить стиль
        layout.addWidget(title)
        
        # Группа: Горячие клавиши
        hotkey_group = QGroupBox(t("settings.app.hotkey"))
        hotkey_layout = QFormLayout()
        hotkey_layout.setSpacing(12)
        
        # Поле ввода горячей клавиши с кнопкой сброса
        hotkey_container = QHBoxLayout()
        self.hotkey_edit = HotkeyInput()
        self.hotkey_edit.setPlaceholderText(t("settings.app.hotkey_placeholder"))
        hotkey_container.addWidget(self.hotkey_edit)
        
        # Кнопка сброса
        reset_hotkey_btn = QPushButton("🔄")
        reset_hotkey_btn.setMaximumWidth(40)
        reset_hotkey_btn.setToolTip(t("common.reset"))
        reset_hotkey_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_hotkey_btn.clicked.connect(self._reset_hotkey)
        hotkey_container.addWidget(reset_hotkey_btn)
        
        hotkey_label = QLabel(t("settings.app.hotkey"))
        hotkey_label.setToolTip(t("settings.app.hotkey_tooltip"))
        hotkey_layout.addRow(hotkey_label, hotkey_container)
        
        hotkey_group.setLayout(hotkey_layout)
        layout.addWidget(hotkey_group)
        
        # Группа: Интерфейс
        ui_group = QGroupBox(t("settings.app.title"))
        ui_layout = QFormLayout()
        ui_layout.setSpacing(12)
        
        self.auto_hide_spin = NoScrollDoubleSpinBox()
        self.auto_hide_spin.setRange(1.0, 10.0)
        self.auto_hide_spin.setSingleStep(0.5)
        self.auto_hide_spin.setDecimals(1)
        self.auto_hide_spin.setSuffix(f" {t('common.seconds')}")
        hide_label = QLabel(t("settings.app.auto_hide"))
        hide_label.setToolTip(t("settings.app.auto_hide_tooltip"))
        ui_layout.addRow(hide_label, self.auto_hide_spin)
        
        # Чекбокс для запоминания позиции окна
        self.remember_position_check = QCheckBox()
        self.remember_position_check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remember_position_check.toggled.connect(self._on_remember_position_changed)
        remember_label = QLabel(t("settings.app.remember_position"))
        remember_label.setToolTip(t("settings.app.remember_position_tooltip"))
        ui_layout.addRow(remember_label, self.remember_position_check)
        
        # Выпадающий список предустановленных позиций
        self.window_position_combo = NoScrollComboBox()
        self.window_position_combo.addItems([
            t("settings.app.position_center"),
            t("settings.app.position_top_left"),
            t("settings.app.position_top_right"),
            t("settings.app.position_bottom_left"),
            t("settings.app.position_bottom_right"),
            t("settings.app.position_custom")
        ])
        self.window_position_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        position_label = QLabel(t("settings.app.window_position"))
        position_label.setToolTip(t("settings.app.window_position_tooltip"))
        ui_layout.addRow(position_label, self.window_position_combo)
        
        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)
        
        # Прижать контент вверх
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _create_audio_page(self) -> QWidget:
        """Создает страницу настроек аудио."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel(t("settings.audio.title"))
        title.setObjectName("pageTitle")  # Применить стиль
        layout.addWidget(title)
        
        # Группа: Параметры записи
        audio_group = QGroupBox(t("settings.audio.title"))
        audio_layout = QFormLayout()
        audio_layout.setSpacing(12)
        
        self.sample_rate_combo = NoScrollComboBox()
        self.sample_rate_combo.addItems(["16000", "44100", "48000"])
        self.sample_rate_combo.setCursor(Qt.CursorShape.PointingHandCursor)  # Курсор "рука"
        rate_label = QLabel(t("settings.audio.sample_rate"))
        rate_label.setToolTip(t("settings.audio.sample_rate_tooltip"))
        audio_layout.addRow(rate_label, self.sample_rate_combo)
        
        self.chunk_size_combo = NoScrollComboBox()
        self.chunk_size_combo.addItems(["256", "512", "1024", "2048", "4096"])
        self.chunk_size_combo.setCursor(Qt.CursorShape.PointingHandCursor)  # Курсор "рука"
        chunk_label = QLabel(t("settings.audio.chunk_size"))
        chunk_label.setToolTip(t("settings.audio.chunk_size_tooltip"))
        audio_layout.addRow(chunk_label, self.chunk_size_combo)
        
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)
        
        # Группа: Определение тишины
        silence_group = QGroupBox(t("settings.audio.title"))
        silence_layout = QFormLayout()
        silence_layout.setSpacing(12)
        
        # Чекбокс ручной остановки
        self.manual_stop_check = QCheckBox()
        self.manual_stop_check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.manual_stop_check.toggled.connect(self._on_manual_stop_changed)
        manual_stop_label = QLabel(t("settings.audio.manual_stop"))
        manual_stop_label.setToolTip(t("settings.audio.manual_stop_tooltip"))
        silence_layout.addRow(manual_stop_label, self.manual_stop_check)
        
        # Описание режима
        manual_stop_info = QLabel(t("settings.audio.manual_stop_info"))
        manual_stop_info.setWordWrap(True)
        manual_stop_info.setStyleSheet(
            "color: #888888; "
            "font-size: 11px; "
            "padding: 8px; "
            "background-color: #2d2d2d; "
            "border-radius: 4px;"
        )
        silence_layout.addRow("", manual_stop_info)
        
        self.silence_threshold_spin = NoScrollDoubleSpinBox()
        self.silence_threshold_spin.setRange(0.01, 0.1)
        self.silence_threshold_spin.setSingleStep(0.01)
        self.silence_threshold_spin.setDecimals(2)
        threshold_label = QLabel(t("settings.audio.silence_threshold"))
        threshold_label.setToolTip(t("settings.audio.silence_threshold_tooltip"))
        silence_layout.addRow(threshold_label, self.silence_threshold_spin)
        
        self.silence_duration_spin = NoScrollDoubleSpinBox()
        self.silence_duration_spin.setRange(0.5, 5.0)
        self.silence_duration_spin.setSingleStep(0.5)
        self.silence_duration_spin.setDecimals(1)
        self.silence_duration_spin.setSuffix(f" {t('common.seconds')}")
        duration_label = QLabel(t("settings.audio.silence_duration"))
        duration_label.setToolTip(t("settings.audio.silence_duration_tooltip"))
        silence_layout.addRow(duration_label, self.silence_duration_spin)
        
        self.silence_padding_spin = NoScrollDoubleSpinBox()
        self.silence_padding_spin.setRange(100, 1000)
        self.silence_padding_spin.setSingleStep(50)
        self.silence_padding_spin.setDecimals(0)
        self.silence_padding_spin.setSuffix(f" {t('common.milliseconds')}")
        padding_label = QLabel(t("settings.audio.silence_padding"))
        padding_label.setToolTip(t("settings.audio.silence_padding_tooltip"))
        silence_layout.addRow(padding_label, self.silence_padding_spin)
        
        silence_group.setLayout(silence_layout)
        layout.addWidget(silence_group)
        
        # Информация
        info_label = QLabel(t("settings.audio.warning"))
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #ff8800; font-size: 11px; padding: 8px;")
        layout.addWidget(info_label)
        
        # Прижать контент вверх
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _create_processing_page(self) -> QWidget:
        """Создает страницу настроек обработки транскрипции."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel(t("settings.processing.title"))
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        
        # Группа: Постобработка транскрипции
        post_processing_group = QGroupBox(t("settings.processing.title"))
        post_processing_layout = QVBoxLayout()
        post_processing_layout.setSpacing(12)
        
        # Чекбокс включения постобработки
        self.enable_post_processing_check = QCheckBox(t("settings.processing.enable"))
        self.enable_post_processing_check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.enable_post_processing_check.setToolTip(t("settings.processing.enable_tooltip"))
        self.enable_post_processing_check.toggled.connect(self._on_post_processing_toggled)
        post_processing_layout.addWidget(self.enable_post_processing_check)
        
        # Описание
        info_label = QLabel(t("settings.processing.info"))
        info_label.setWordWrap(True)
        info_label.setStyleSheet(
            "color: #888888; "
            "font-size: 11px; "
            "padding: 8px; "
            "background-color: #2d2d2d; "
            "border-radius: 4px;"
        )
        post_processing_layout.addWidget(info_label)
        
        # Форма настроек
        settings_form = QFormLayout()
        settings_form.setSpacing(12)
        
        # Выбор провайдера
        self.post_processing_provider_combo = NoScrollComboBox()
        self.post_processing_provider_combo.addItems(["groq", "openai", "glm", "llm"])
        self.post_processing_provider_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.post_processing_provider_combo.currentTextChanged.connect(self._on_post_processing_provider_changed)
        provider_label = QLabel(t("settings.processing.provider"))
        provider_label.setToolTip(t("settings.processing.provider_tooltip"))
        settings_form.addRow(provider_label, self.post_processing_provider_combo)
        
        # Выбор модели
        self.post_processing_model_combo = NoScrollComboBox()
        self.post_processing_model_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        model_label = QLabel(t("settings.processing.model"))
        model_label.setToolTip(t("settings.processing.model_tooltip"))
        settings_form.addRow(model_label, self.post_processing_model_combo)
        
        # Кастомная модель (для всех провайдеров)
        self.post_processing_custom_model_label = QLabel(t("settings.processing.custom_model"))
        self.post_processing_custom_model_label.setToolTip(t("settings.processing.custom_model_tooltip"))
        self.post_processing_custom_model_edit = QLineEdit()
        self.post_processing_custom_model_edit.setPlaceholderText(t("settings.processing.custom_model_placeholder"))
        settings_form.addRow(self.post_processing_custom_model_label, self.post_processing_custom_model_edit)
        
        # GLM Coding Plan чекбокс (показывается только для GLM)
        self.glm_coding_plan_check = QCheckBox(t("settings.processing.glm_coding_plan"))
        self.glm_coding_plan_check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.glm_coding_plan_check.setToolTip(t("settings.processing.glm_coding_plan_tooltip"))
        self.glm_coding_plan_check.toggled.connect(lambda: self._on_post_processing_provider_changed(self.post_processing_provider_combo.currentText()))
        self.glm_coding_plan_check.setVisible(False)  # Скрыто по умолчанию
        settings_form.addRow("", self.glm_coding_plan_check)
        
        # LLM Base URL (показывается только для LLM)
        self.llm_base_url_label = QLabel(t("settings.processing.llm_base_url"))
        self.llm_base_url_label.setToolTip(t("settings.processing.llm_base_url_tooltip"))
        self.llm_base_url_edit = QLineEdit()
        self.llm_base_url_edit.setPlaceholderText(t("settings.processing.llm_base_url_placeholder"))
        self.llm_base_url_edit.setVisible(False)  # Скрыто по умолчанию
        self.llm_base_url_label.setVisible(False)
        settings_form.addRow(self.llm_base_url_label, self.llm_base_url_edit)
        
        # LLM API Key (показывается только для LLM)
        self.llm_api_key_label = QLabel(t("settings.processing.llm_api_key"))
        self.llm_api_key_label.setToolTip(t("settings.processing.llm_api_key_tooltip"))
        self.llm_api_key_edit = QLineEdit()
        self.llm_api_key_edit.setPlaceholderText(t("settings.processing.llm_api_key_placeholder"))
        self.llm_api_key_edit.setVisible(False)  # Скрыто по умолчанию
        self.llm_api_key_label.setVisible(False)
        settings_form.addRow(self.llm_api_key_label, self.llm_api_key_edit)
        
        post_processing_layout.addLayout(settings_form)
        
        # Системный промпт (редактируемый)
        prompt_label = QLabel(t("settings.processing.prompt"))
        prompt_label.setToolTip(t("settings.processing.prompt_tooltip"))
        post_processing_layout.addWidget(prompt_label)
        
        from PyQt6.QtWidgets import QTextEdit
        self.post_processing_prompt_edit = QTextEdit()
        self.post_processing_prompt_edit.setPlaceholderText(t("settings.processing.prompt_placeholder"))
        self.post_processing_prompt_edit.setMinimumHeight(100)
        self.post_processing_prompt_edit.setMaximumHeight(150)
        self.post_processing_prompt_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }
            QTextEdit:focus {
                border: 1px solid #0078d4;
            }
        """)
        post_processing_layout.addWidget(self.post_processing_prompt_edit)
        
        post_processing_group.setLayout(post_processing_layout)
        layout.addWidget(post_processing_group)
        
        # Группа: Форматирование транскрипции
        formatting_group = QGroupBox("Форматирование")
        formatting_layout = QVBoxLayout()
        formatting_layout.setSpacing(12)
        
        # Чекбокс включения форматирования
        self.enable_formatting_check = QCheckBox("Включить форматирование")
        self.enable_formatting_check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.enable_formatting_check.setToolTip("Автоматически форматировать текст в зависимости от активного приложения")
        self.enable_formatting_check.toggled.connect(self._on_formatting_toggled)
        formatting_layout.addWidget(self.enable_formatting_check)
        
        # Описание
        formatting_info_label = QLabel(
            "Автоматически форматирует транскрибированный текст в зависимости от активного приложения. "
            "Поддерживает Notion, Obsidian, Markdown файлы, Word, LibreOffice и другие."
        )
        formatting_info_label.setObjectName("infoLabel")
        formatting_info_label.setWordWrap(True)
        formatting_layout.addWidget(formatting_info_label)
        
        # Форма настроек форматирования
        formatting_form = QFormLayout()
        formatting_form.setSpacing(12)
        
        # Выбор провайдера для форматирования
        self.formatting_provider_combo = NoScrollComboBox()
        self.formatting_provider_combo.addItems(["groq", "openai", "glm", "custom"])
        self.formatting_provider_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.formatting_provider_combo.currentTextChanged.connect(self._on_formatting_provider_changed)
        formatting_provider_label = QLabel("AI провайдер")
        formatting_provider_label.setToolTip("AI провайдер для операций форматирования")
        formatting_form.addRow(formatting_provider_label, self.formatting_provider_combo)
        
        # Модель для форматирования
        self.formatting_model_edit = QLineEdit()
        self.formatting_model_edit.setPlaceholderText("опционально, по умолчанию используется стандартная модель провайдера")
        formatting_model_label = QLabel("Модель")
        formatting_model_label.setToolTip("Модель для форматирования текста (опционально)")
        formatting_form.addRow(formatting_model_label, self.formatting_model_edit)
        
        # Custom Base URL (только для custom провайдера)
        self.formatting_custom_url_edit = QLineEdit()
        self.formatting_custom_url_edit.setPlaceholderText("например: http://localhost:1234/v1/")
        self.formatting_custom_url_label = QLabel("Custom Base URL")
        self.formatting_custom_url_label.setToolTip("URL для custom OpenAI-совместимого API")
        formatting_form.addRow(self.formatting_custom_url_label, self.formatting_custom_url_edit)
        
        # Custom API Key (только для custom провайдера)
        formatting_custom_key_layout = QHBoxLayout()
        self.formatting_custom_key_edit = QLineEdit()
        self.formatting_custom_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.formatting_custom_key_edit.setPlaceholderText("API ключ для custom провайдера")
        formatting_custom_key_layout.addWidget(self.formatting_custom_key_edit)
        
        self.formatting_custom_key_show_btn = QPushButton("👁")
        self.formatting_custom_key_show_btn.setMaximumWidth(40)
        self.formatting_custom_key_show_btn.setCheckable(True)
        self.formatting_custom_key_show_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.formatting_custom_key_show_btn.toggled.connect(
            lambda checked: self.formatting_custom_key_edit.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            )
        )
        formatting_custom_key_layout.addWidget(self.formatting_custom_key_show_btn)
        
        self.formatting_custom_key_label = QLabel("Custom API Key")
        self.formatting_custom_key_label.setToolTip("API ключ для custom провайдера")
        formatting_form.addRow(self.formatting_custom_key_label, formatting_custom_key_layout)
        
        # Температура
        self.formatting_temperature_spin = NoScrollDoubleSpinBox()
        self.formatting_temperature_spin.setRange(0.0, 1.0)
        self.formatting_temperature_spin.setSingleStep(0.1)
        self.formatting_temperature_spin.setDecimals(1)
        self.formatting_temperature_spin.setValue(0.3)
        self.formatting_temperature_spin.setCursor(Qt.CursorShape.PointingHandCursor)
        formatting_temperature_label = QLabel("Температура")
        formatting_temperature_label.setToolTip("Температура AI модели (0.0-1.0). Меньше = более предсказуемо")
        formatting_form.addRow(formatting_temperature_label, self.formatting_temperature_spin)
        
        formatting_layout.addLayout(formatting_form)
        
        # Приложения - визуальные блоки (как в языках)
        applications_label = QLabel("Приложения для форматирования:")
        applications_label.setToolTip("Выберите приложения, для которых будет применяться форматирование")
        formatting_layout.addWidget(applications_label)
        
        # Сетка с приложениями (4 колонки)
        self.formatting_apps_grid = QGridLayout()
        self.formatting_apps_grid.setSpacing(12)
        self.formatting_apps_grid.setHorizontalSpacing(12)
        
        # Словарь для хранения кнопок приложений
        self.formatting_app_buttons = {}
        
        # Контейнер для сетки
        apps_container = QWidget()
        apps_container.setLayout(self.formatting_apps_grid)
        formatting_layout.addWidget(apps_container)
        
        # Кнопка "Добавить приложение"
        add_app_btn = QPushButton(f"➕ {t('settings.formatting.add_application')}")
        add_app_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_app_btn.clicked.connect(self._on_add_application_clicked)
        add_app_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                border: 2px dashed #3d3d3d;
                border-radius: 8px;
                padding: 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #0078d4;
            }
        """)
        formatting_layout.addWidget(add_app_btn)
        
        # Кнопка "Настроить ключевые слова веб-приложений"
        web_keywords_btn = QPushButton("🌐 Настроить ключевые слова веб-приложений")
        web_keywords_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        web_keywords_btn.clicked.connect(self._on_web_keywords_clicked)
        web_keywords_btn.setToolTip("Настройте ключевые слова для определения веб-приложений в браузерах (Google Docs, Notion, и т.д.)")
        web_keywords_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                border: 2px solid #3d3d3d;
                border-radius: 8px;
                padding: 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #0078d4;
            }
        """)
        formatting_layout.addWidget(web_keywords_btn)
        
        formatting_group.setLayout(formatting_layout)
        layout.addWidget(formatting_group)
        
        # Прижать контент вверх
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _create_languages_page(self) -> QWidget:
        """Создает страницу выбора языка интерфейса."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel(t("settings.languages.title"))
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        
        # Группа: Выбор языка
        language_group = QGroupBox(t("settings.languages.interface_language"))
        language_layout = QVBoxLayout()
        language_layout.setSpacing(16)
        
        # Описание
        info_label = QLabel(t("settings.languages.info"))
        info_label.setWordWrap(True)
        info_label.setStyleSheet(
            "color: #888888; "
            "font-size: 11px; "
            "padding: 8px; "
            "background-color: #2d2d2d; "
            "border-radius: 4px;"
        )
        language_layout.addWidget(info_label)
        
        # Сетка с языками (4 колонки для оптимального отображения)
        from PyQt6.QtWidgets import QGridLayout, QPushButton, QButtonGroup
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)
        grid_layout.setHorizontalSpacing(12)
        
        # Создать группу кнопок
        self.language_button_group = QButtonGroup()
        
        # Топ-15 языков мира с кодами
        languages = [
            ("GB", "English", "en-gb"),
            ("US", "English", "en-us"),
            ("CN", "中文", "zh"),
            ("IN", "हिन्दी", "hi"),
            ("ES", "Español", "es"),
            ("FR", "Français", "fr"),
            ("SA", "العربية", "ar"),
            ("BD", "বাংলা", "bn"),
            ("RU", "Русский", "ru"),
            ("PT", "Português", "pt"),
            ("PK", "اردو", "ur"),
            ("ID", "Indonesia", "id"),
            ("DE", "Deutsch", "de"),
            ("JP", "日本語", "ja"),
            ("TR", "Türkçe", "tr"),
            ("KR", "한국어", "ko"),
        ]
        
        # Добавить языки в сетку (4 колонки)
        row = 0
        col = 0
        for idx, (code, name, lang_code) in enumerate(languages):
            # Создать контейнер для кнопки с вертикальным layout
            btn_container = QWidget()
            btn_layout = QVBoxLayout(btn_container)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(0)
            
            # Создать кнопку
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setMinimumHeight(80)
            btn.setMinimumWidth(120)
            btn.setProperty("language_code", lang_code)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Создать layout внутри кнопки
            btn_inner_layout = QVBoxLayout(btn)
            btn_inner_layout.setContentsMargins(8, 8, 8, 8)
            btn_inner_layout.setSpacing(4)
            btn_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Код страны (крупный)
            code_label = QLabel(code)
            code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            code_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
            code_label.setFont(code_font)
            code_label.setStyleSheet("color: #ffffff; background: transparent;")
            btn_inner_layout.addWidget(code_label)
            
            # Название языка (мелкий)
            name_label = QLabel(name)
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_font = QFont("Segoe UI", 10)
            name_label.setFont(name_font)
            name_label.setStyleSheet("color: #ffffff; background: transparent;")
            btn_inner_layout.addWidget(name_label)
            
            # Стиль кнопки
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 2px solid #3d3d3d;
                    border-radius: 8px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                    border: 2px solid #0078d4;
                }
                QPushButton:checked {
                    background-color: #0078d4;
                    border: 2px solid #1084d8;
                }
            """)
            
            # Подключить к группе
            self.language_button_group.addButton(btn, idx)
            
            # Подключить сигнал для эксклюзивного выбора
            btn.clicked.connect(lambda checked, button=btn: self._on_language_button_clicked(button))
            
            grid_layout.addWidget(btn, row, col)
            
            col += 1
            if col >= 4:  # 4 колонки
                col = 0
                row += 1
        
        language_layout.addLayout(grid_layout)
        
        # Выбрать русский по умолчанию (индекс 8)
        default_button = self.language_button_group.button(8)  # RU
        if default_button:
            default_button.setChecked(True)
        
        language_group.setLayout(language_layout)
        layout.addWidget(language_group)
        
        # Информация о будущей функциональности
        future_info = QLabel(t("settings.languages.future_info"))
        future_info.setWordWrap(True)
        future_info.setStyleSheet(
            "color: #888888; "
            "font-size: 11px; "
            "padding: 8px; "
            "background-color: #2d2d2d; "
            "border-radius: 4px; "
            "border-left: 3px solid #ff8800;"
        )
        layout.addWidget(future_info)
        
        # Прижать контент вверх
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _on_language_button_clicked(self, clicked_button):
        """Обработчик клика на кнопку языка для эксклюзивного выбора."""
        # Снять выделение со всех кнопок
        for button in self.language_button_group.buttons():
            if button != clicked_button:
                button.setChecked(False)
        # Убедиться что нажатая кнопка выбрана
        clicked_button.setChecked(True)
    
    def _create_ui_customization_page(self) -> QWidget:
        """Создает страницу настройки интерфейса."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel(t("settings.ui_customization.title"))
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        
        # Группа: Прозрачность окна
        opacity_group = QGroupBox(t("settings.ui_customization.window_opacity"))
        opacity_layout = QVBoxLayout()
        opacity_layout.setSpacing(12)
        
        # Слайдер прозрачности с меткой значения
        opacity_container = QHBoxLayout()
        opacity_container.setSpacing(12)
        
        from PyQt6.QtWidgets import QSlider
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setMinimum(50)
        self.opacity_slider.setMaximum(255)
        self.opacity_slider.setValue(self.config.window_opacity)
        self.opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.opacity_slider.setTickInterval(25)
        self.opacity_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.opacity_slider.setToolTip(t("settings.ui_customization.window_opacity_tooltip"))
        opacity_container.addWidget(self.opacity_slider, 1)
        
        # Метка со значением
        self.opacity_value_label = QLabel(str(self.config.window_opacity))
        self.opacity_value_label.setMinimumWidth(40)
        self.opacity_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.opacity_value_label.setStyleSheet("""
            QLabel {
                background-color: #0078d4;
                color: #ffffff;
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
            }
        """)
        opacity_container.addWidget(self.opacity_value_label)
        
        # Подключить обновление метки
        self.opacity_slider.valueChanged.connect(
            lambda value: self.opacity_value_label.setText(str(value))
        )
        # Подключить live preview для opacity
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        
        opacity_layout.addLayout(opacity_container)
        opacity_group.setLayout(opacity_layout)
        layout.addWidget(opacity_group)
        
        # Группа: Размеры шрифтов
        fonts_group = QGroupBox(t("settings.ui_customization.font_sizes"))
        fonts_layout = QFormLayout()
        fonts_layout.setSpacing(12)
        
        # Плавающее окно - Основной текст
        from PyQt6.QtWidgets import QAbstractSpinBox
        self.font_floating_main_spin = NoScrollSpinBox()
        self.font_floating_main_spin.setRange(10, 24)
        self.font_floating_main_spin.setSingleStep(1)
        self.font_floating_main_spin.setSuffix(" px")
        self.font_floating_main_spin.setValue(self.config.font_size_floating_main)
        self.font_floating_main_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.font_floating_main_spin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.font_floating_main_spin.valueChanged.connect(self._on_font_floating_main_changed)
        font_main_label = QLabel(t("settings.ui_customization.font_floating_main"))
        font_main_label.setToolTip(t("settings.ui_customization.font_floating_main_tooltip"))
        fonts_layout.addRow(font_main_label, self.font_floating_main_spin)
        
        # Плавающее окно - Инфо панель
        self.font_floating_info_spin = NoScrollSpinBox()
        self.font_floating_info_spin.setRange(8, 16)
        self.font_floating_info_spin.setSingleStep(1)
        self.font_floating_info_spin.setSuffix(" px")
        self.font_floating_info_spin.setValue(self.config.font_size_floating_info)
        self.font_floating_info_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.font_floating_info_spin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.font_floating_info_spin.valueChanged.connect(self._on_font_floating_info_changed)
        font_info_label = QLabel(t("settings.ui_customization.font_floating_info"))
        font_info_label.setToolTip(t("settings.ui_customization.font_floating_info_tooltip"))
        fonts_layout.addRow(font_info_label, self.font_floating_info_spin)
        
        # Окно настроек - Метки
        self.font_settings_labels_spin = NoScrollSpinBox()
        self.font_settings_labels_spin.setRange(10, 16)
        self.font_settings_labels_spin.setSingleStep(1)
        self.font_settings_labels_spin.setSuffix(" px")
        self.font_settings_labels_spin.setValue(self.config.font_size_settings_labels)
        self.font_settings_labels_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.font_settings_labels_spin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.font_settings_labels_spin.valueChanged.connect(self._on_font_settings_labels_changed)
        font_labels_label = QLabel(t("settings.ui_customization.font_settings_labels"))
        font_labels_label.setToolTip(t("settings.ui_customization.font_settings_labels_tooltip"))
        fonts_layout.addRow(font_labels_label, self.font_settings_labels_spin)
        
        # Окно настроек - Заголовки
        self.font_settings_titles_spin = NoScrollSpinBox()
        self.font_settings_titles_spin.setRange(16, 32)
        self.font_settings_titles_spin.setSingleStep(1)
        self.font_settings_titles_spin.setSuffix(" px")
        self.font_settings_titles_spin.setValue(self.config.font_size_settings_titles)
        self.font_settings_titles_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.font_settings_titles_spin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.font_settings_titles_spin.valueChanged.connect(self._on_font_settings_titles_changed)
        font_titles_label = QLabel(t("settings.ui_customization.font_settings_titles"))
        font_titles_label.setToolTip(t("settings.ui_customization.font_settings_titles_tooltip"))
        fonts_layout.addRow(font_titles_label, self.font_settings_titles_spin)
        
        fonts_group.setLayout(fonts_layout)
        layout.addWidget(fonts_group)
        
        # Кнопка сброса на значения по умолчанию
        reset_btn = QPushButton(t("settings.ui_customization.reset_defaults"))
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.setToolTip(t("settings.ui_customization.reset_defaults_tooltip"))
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
        """)
        reset_btn.clicked.connect(self._reset_ui_defaults)
        layout.addWidget(reset_btn)
        
        # Прижать контент вверх
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _reset_ui_defaults(self):
        """Сбрасывает все настройки интерфейса на значения по умолчанию."""
        from core.config_saver import get_config_saver
        
        # Установить значения по умолчанию в UI контролы
        self.opacity_slider.setValue(150)
        self.font_floating_main_spin.setValue(14)
        self.font_floating_info_spin.setValue(11)
        self.font_settings_labels_spin.setValue(12)
        self.font_settings_titles_spin.setValue(24)
        
        # Записать значения в config.jsonc
        config_saver = get_config_saver()
        config_saver.update_multiple_values({
            "window.opacity": 150,
            "window.font_sizes.floating_main": 14,
            "window.font_sizes.floating_info": 11,
            "window.font_sizes.settings_labels": 12,
            "window.font_sizes.settings_titles": 24
        })
        
        # Обновить конфиг в памяти
        self.config.window_opacity = 150
        self.config.font_size_floating_main = 14
        self.config.font_size_floating_info = 11
        self.config.font_size_settings_labels = 12
        self.config.font_size_settings_titles = 24
        
        # Обновить FloatingWindow если доступно (для live preview opacity)
        if self.parent() and hasattr(self.parent(), 'set_opacity'):
            self.parent().set_opacity(150)
        
        logger.info("UI customization settings reset to defaults")
    
    def _on_opacity_changed(self, value: int):
        """
        Обработчик изменения прозрачности окна с live preview (Task 4.4)
        
        Args:
            value: Новое значение прозрачности (50-255)
        
        Requirements: 4.1
        """
        # Update this Settings Window's opacity using mixin (Task 4.4)
        # We override update_opacity to also update child widget styles
        self.update_opacity(value)
        
        # Also update FloatingWindow if available for consistency
        if self.parent() and hasattr(self.parent(), 'set_opacity'):
            try:
                self.parent().set_opacity(value)
                logger.debug(f"Opacity changed to {value} with live preview")
            except Exception as e:
                logger.warning(f"Failed to apply live opacity preview: {e}")
        else:
            logger.debug(f"Opacity changed to {value} (no live preview available)")
    
    def update_opacity(self, opacity: int):
        """
        Override mixin's update_opacity to also update child widget styles.
        
        Args:
            opacity: New opacity value (50-255)
        
        Requirements: 4.1
        """
        from design_system.style_constants import StyleConstants
        self._opacity = StyleConstants.clamp_opacity(opacity)
        # Re-apply full stylesheet (window + child widgets)
        self._apply_style()
    
    def _on_font_floating_main_changed(self, value: int):
        """
        Обработчик изменения размера шрифта основного текста плавающего окна.
        
        Args:
            value: Новый размер шрифта (10-24)
        """
        from core.config_saver import get_config_saver
        
        # Сохранить значение в config.jsonc
        config_saver = get_config_saver()
        config_saver.update_value("window.font_sizes.floating_main", value)
        
        # Обновить конфиг в памяти
        self.config.font_size_floating_main = value
        
        # Применить изменения к FloatingWindow если доступно
        if self.parent() and hasattr(self.parent(), '_apply_opacity'):
            try:
                # Вызываем _apply_opacity() чтобы обновить стили с новым размером шрифта
                self.parent()._apply_opacity()
                logger.debug(f"Font size floating main changed to {value} with live preview")
            except Exception as e:
                logger.warning(f"Failed to apply live font preview: {e}")
        else:
            logger.debug(f"Font size floating main changed to {value} (no live preview available)")
    
    def _on_font_floating_info_changed(self, value: int):
        """
        Обработчик изменения размера шрифта инфо панели плавающего окна.
        
        Args:
            value: Новый размер шрифта (8-16)
        """
        from core.config_saver import get_config_saver
        
        # Сохранить значение в config.jsonc
        config_saver = get_config_saver()
        config_saver.update_value("window.font_sizes.floating_info", value)
        
        # Обновить конфиг в памяти
        self.config.font_size_floating_info = value
        
        # Применить изменения к FloatingWindow если доступно
        if self.parent() and hasattr(self.parent(), '_apply_opacity'):
            try:
                # Вызываем _apply_opacity() чтобы обновить стили с новым размером шрифта
                self.parent()._apply_opacity()
                logger.debug(f"Font size floating info changed to {value} with live preview")
            except Exception as e:
                logger.warning(f"Failed to apply live font preview: {e}")
        else:
            logger.debug(f"Font size floating info changed to {value} (no live preview available)")
    
    def _on_font_settings_labels_changed(self, value: int):
        """
        Обработчик изменения размера шрифта меток окна настроек.
        
        Args:
            value: Новый размер шрифта (10-16)
        """
        from core.config_saver import get_config_saver
        
        # Сохранить значение в config.jsonc
        config_saver = get_config_saver()
        config_saver.update_value("window.font_sizes.settings_labels", value)
        
        # Обновить конфиг в памяти
        self.config.font_size_settings_labels = value
        # Обновить стиль окна настроек
        self._apply_style()
        logger.debug(f"Font size settings labels changed to {value}")
    
    def _on_font_settings_titles_changed(self, value: int):
        """
        Обработчик изменения размера шрифта заголовков окна настроек.
        
        Args:
            value: Новый размер шрифта (16-32)
        """
        from core.config_saver import get_config_saver
        
        # Сохранить значение в config.jsonc
        config_saver = get_config_saver()
        config_saver.update_value("window.font_sizes.settings_titles", value)
        
        # Обновить конфиг в памяти
        self.config.font_size_settings_titles = value
        # Обновить стиль окна настроек
        self._apply_style()
        logger.debug(f"Font size settings titles changed to {value}")
    
    def _create_recordings_page(self) -> QWidget:
        """Создает страницу управления записями."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel(t("settings.recordings.title"))
        title.setObjectName("pageTitle")  # Применить стиль
        layout.addWidget(title)
        
        # Группа: Настройки сохранения
        save_group = QGroupBox(t("settings.recordings.title"))
        save_layout = QVBoxLayout()
        save_layout.setSpacing(12)
        
        # Чекбокс для сохранения записей
        self.keep_recordings_check = QCheckBox(t("settings.recordings.keep_recordings"))
        self.keep_recordings_check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.keep_recordings_check.setToolTip(t("settings.recordings.keep_recordings_tooltip"))
        save_layout.addWidget(self.keep_recordings_check)
        
        # Информация о папке с кнопкой изменения
        from core.config import get_recordings_dir
        recordings_dir = get_recordings_dir()
        
        folder_container = QHBoxLayout()
        folder_container.setSpacing(8)
        
        self.recordings_path_label = QLabel(f"📁 <a href='file:///{recordings_dir}'>{recordings_dir}</a>")
        self.recordings_path_label.setWordWrap(True)
        self.recordings_path_label.setOpenExternalLinks(True)
        self.recordings_path_label.setStyleSheet("color: #888888; font-size: 11px; padding: 8px;")
        # Tooltip will be set dynamically when path is updated
        folder_container.addWidget(self.recordings_path_label, 1)
        
        change_folder_btn = QPushButton(t("settings.recordings.change_folder"))
        change_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        change_folder_btn.setToolTip(t("settings.recordings.change_folder_tooltip"))
        change_folder_btn.clicked.connect(self._change_recordings_folder)
        change_folder_btn.setMaximumWidth(150)
        folder_container.addWidget(change_folder_btn)
        
        reset_folder_btn = QPushButton(t("settings.recordings.reset_folder"))
        reset_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_folder_btn.setToolTip(t("settings.recordings.reset_folder_tooltip"))
        reset_folder_btn.clicked.connect(self._reset_recordings_folder)
        reset_folder_btn.setMaximumWidth(40)
        folder_container.addWidget(reset_folder_btn)
        
        save_layout.addLayout(folder_container)
        
        save_group.setLayout(save_layout)
        layout.addWidget(save_group)
        
        # Группа: Сохраненные записи
        recordings_group = QGroupBox(t("settings.recordings.title"))
        recordings_layout = QVBoxLayout()
        recordings_layout.setSpacing(12)
        
        # Список записей
        self.recordings_list = QListWidget()
        self.recordings_list.setMinimumHeight(250)  # Фиксированная минимальная высота
        self.recordings_list.setMaximumHeight(350)  # Фиксированная максимальная высота
        self.recordings_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px 0px;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
            }
            QListWidget::item:hover:!selected {
                background-color: #3d3d3d;
            }
        """)
        recordings_layout.addWidget(self.recordings_list)
        
        # Подключить двойной клик для открытия аудио
        self.recordings_list.itemDoubleClicked.connect(self._open_recording)
        
        # Включить контекстное меню
        self.recordings_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.recordings_list.customContextMenuRequested.connect(self._show_recordings_context_menu)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)  # Отступ между кнопками
        
        refresh_btn = QPushButton(t("settings.recordings.refresh"))
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setToolTip(t("settings.recordings.refresh_tooltip"))
        refresh_btn.clicked.connect(self._refresh_recordings_list)
        refresh_btn.setMaximumWidth(50)
        buttons_layout.addWidget(refresh_btn)
        
        play_btn = QPushButton(t("settings.recordings.play_audio"))
        play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        play_btn.setToolTip(t("settings.recordings.play_audio_tooltip"))
        play_btn.clicked.connect(self._open_recording)
        buttons_layout.addWidget(play_btn)
        
        self.text_btn = QPushButton(t("settings.recordings.open_text"))
        self.text_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.text_btn.setToolTip(t("settings.recordings.open_text_tooltip"))
        self.text_btn.clicked.connect(self._open_transcription)
        buttons_layout.addWidget(self.text_btn)
        
        folder_btn = QPushButton(t("settings.recordings.open_folder"))
        folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        folder_btn.setToolTip(t("settings.recordings.open_folder_tooltip"))
        folder_btn.clicked.connect(self._open_recordings_folder)
        buttons_layout.addWidget(folder_btn)
        
        delete_btn = QPushButton(t("settings.recordings.delete"))
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setToolTip(t("settings.recordings.delete_tooltip"))
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #d13438;
            }
            QPushButton:hover {
                background-color: #e13438;
            }
        """)
        delete_btn.clicked.connect(self._delete_recording)
        buttons_layout.addWidget(delete_btn)
        
        recordings_layout.addLayout(buttons_layout)
        
        recordings_group.setLayout(recordings_layout)
        layout.addWidget(recordings_group)
        
        # Подключить сигнал изменения выбора
        self.recordings_list.currentItemChanged.connect(self._on_recording_selection_changed)
        
        # Загрузить список записей
        self._refresh_recordings_list()
        
        # Прижать контент вверх
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _refresh_recordings_list(self):
        """Обновляет список сохраненных записей."""
        from core.config import get_audio_recordings_dir, get_transcriptions_dir
        from pathlib import Path
        
        self.recordings_list.clear()
        
        audio_dir = get_audio_recordings_dir()
        transcriptions_dir = get_transcriptions_dir()
        
        # Получить все аудио файлы
        recordings = sorted(audio_dir.glob("*.wav"), reverse=True)  # Новые сверху
        
        if not recordings:
            item = QListWidgetItem(t("settings.recordings.no_recordings"))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)  # Не выбираемый
            self.recordings_list.addItem(item)
        else:
            for recording in recordings:
                # Получить размер файла
                size_mb = recording.stat().st_size / (1024 * 1024)
                
                # Получить время создания
                from datetime import datetime
                mtime = datetime.fromtimestamp(recording.stat().st_mtime)
                time_str = mtime.strftime("%d.%m.%Y %H:%M:%S")
                
                # Проверить наличие транскрипции
                transcription_path = transcriptions_dir / f"{recording.stem}.txt"
                has_transcription = transcription_path.exists()
                
                # Создать элемент списка
                transcription_icon = "📝" if has_transcription else ""
                item_text = f"🎙️ {recording.name}  {transcription_icon}  |  {size_mb:.2f} MB  |  {time_str}"
                item = QListWidgetItem(item_text)
                
                # Сохранить пути к аудио и транскрипции
                item.setData(Qt.ItemDataRole.UserRole, str(recording))  # Путь к аудио
                item.setData(Qt.ItemDataRole.UserRole + 1, str(transcription_path) if has_transcription else None)  # Путь к транскрипции
                
                self.recordings_list.addItem(item)
        
        # Обновить состояние кнопки текста
        self._on_recording_selection_changed()
    
    def _on_recording_selection_changed(self):
        """Обновляет состояние кнопки текста в зависимости от наличия транскрипции."""
        current_item = self.recordings_list.currentItem()
        
        if not current_item:
            self.text_btn.setEnabled(False)
            return
        
        # Проверить наличие транскрипции
        transcription_path = current_item.data(Qt.ItemDataRole.UserRole + 1)
        has_transcription = transcription_path is not None
        
        # Включить/отключить кнопку
        self.text_btn.setEnabled(has_transcription)
        
        # Обновить стиль кнопки
        if has_transcription:
            self.text_btn.setStyleSheet("")
        else:
            self.text_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3d3d3d;
                    color: #808080;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                    color: #808080;
                }
            """)
    
    def _show_recordings_context_menu(self, position):
        """Показывает контекстное меню для списка записей."""
        from PyQt6.QtWidgets import QMenu
        
        # Получить элемент под курсором
        item = self.recordings_list.itemAt(position)
        if not item:
            return
        
        # Проверить что это не пустой список
        recording_path = item.data(Qt.ItemDataRole.UserRole)
        if not recording_path:
            return
        
        # Проверить наличие транскрипции
        transcription_path = item.data(Qt.ItemDataRole.UserRole + 1)
        has_transcription = transcription_path is not None
        
        # Создать контекстное меню
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #0078d4;
            }
            QMenu::item:disabled {
                color: #808080;
            }
        """)
        
        # Добавить действия
        open_audio_action = menu.addAction(t("settings.recordings.play_audio_context"))
        open_audio_action.triggered.connect(self._open_recording)
        
        open_text_action = menu.addAction(t("settings.recordings.open_text_context"))
        open_text_action.setEnabled(has_transcription)
        open_text_action.triggered.connect(self._open_transcription)
        
        menu.addSeparator()
        
        open_folder_action = menu.addAction(t("settings.recordings.open_folder_context"))
        open_folder_action.triggered.connect(self._open_recordings_folder)
        
        menu.addSeparator()
        
        delete_action = menu.addAction(t("settings.recordings.delete_context"))
        delete_action.triggered.connect(self._delete_recording)
        
        # Показать меню в позиции курсора
        menu.exec(self.recordings_list.mapToGlobal(position))
    
    def _open_recording(self):
        """Открывает выбранную аудиозапись в проигрывателе по умолчанию."""
        current_item = self.recordings_list.currentItem()
        if not current_item:
            return
        
        recording_path = current_item.data(Qt.ItemDataRole.UserRole)
        if not recording_path:
            return
        
        # Открыть файл в проигрывателе по умолчанию
        import subprocess
        import platform
        
        try:
            if platform.system() == 'Windows':
                os.startfile(recording_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', recording_path])
            else:  # Linux
                subprocess.run(['xdg-open', recording_path])
        except Exception as e:
            logger.error(f"Не удалось открыть запись: {e}")
            QMessageBox.warning(
                self,
                t("settings.recordings.open_error_title"),
                t("settings.recordings.open_error_message", error=str(e)),
                QMessageBox.StandardButton.Ok
            )
    
    def _open_transcription(self):
        """Открывает транскрипцию в текстовом редакторе."""
        current_item = self.recordings_list.currentItem()
        if not current_item:
            return
        
        transcription_path = current_item.data(Qt.ItemDataRole.UserRole + 1)
        if not transcription_path:
            return
        
        # Открыть файл в текстовом редакторе по умолчанию
        import subprocess
        import platform
        
        try:
            if platform.system() == 'Windows':
                os.startfile(transcription_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', transcription_path])
            else:  # Linux
                subprocess.run(['xdg-open', transcription_path])
        except Exception as e:
            logger.error(f"Не удалось открыть транскрипцию: {e}")
            QMessageBox.warning(
                self,
                t("settings.recordings.open_error_title"),
                t("settings.recordings.open_text_error_message", error=str(e)),
                QMessageBox.StandardButton.Ok
            )
    
    def _open_recordings_folder(self):
        """Открывает папку с записями в проводнике."""
        from core.config import get_recordings_dir
        import subprocess
        import platform
        
        recordings_dir = get_recordings_dir()
        
        try:
            if platform.system() == 'Windows':
                os.startfile(str(recordings_dir))
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(recordings_dir)])
            else:  # Linux
                subprocess.run(['xdg-open', str(recordings_dir)])
        except Exception as e:
            logger.error(f"Не удалось открыть папку: {e}")
            QMessageBox.warning(
                self,
                t("settings.recordings.open_error_title"),
                t("settings.recordings.open_folder_error_message", error=str(e)),
                QMessageBox.StandardButton.Ok
            )
    
    def _delete_recording(self):
        """Удаляет выбранную запись (аудио и транскрипцию)."""
        current_item = self.recordings_list.currentItem()
        if not current_item:
            return
        
        recording_path = current_item.data(Qt.ItemDataRole.UserRole)
        transcription_path = current_item.data(Qt.ItemDataRole.UserRole + 1)
        
        if not recording_path:
            return
        
        # Подтверждение удаления
        has_transcription = transcription_path is not None
        message = t("settings.recordings.delete_confirm_message", filename=Path(recording_path).name)
        if has_transcription:
            message += t("settings.recordings.delete_confirm_with_text")
        
        reply = QMessageBox.question(
            self,
            t("settings.recordings.delete_confirm_title"),
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Удалить аудио файл
                if os.path.exists(recording_path):
                    os.remove(recording_path)
                    logger.info(f"Аудио удалено: {recording_path}")
                
                # Удалить транскрипцию если есть
                if has_transcription and os.path.exists(transcription_path):
                    os.remove(transcription_path)
                    logger.info(f"Транскрипция удалена: {transcription_path}")
                
                self._refresh_recordings_list()
            except Exception as e:
                logger.error(f"Не удалось удалить запись: {e}")
                QMessageBox.critical(
                    self,
                    t("settings.recordings.delete_error_title"),
                    t("settings.recordings.delete_error_message", error=str(e)),
                    QMessageBox.StandardButton.Ok
                )
    
    def _change_recordings_folder(self):
        """Изменяет папку для сохранения записей."""
        from PyQt6.QtWidgets import QFileDialog
        
        # Получить текущую папку
        from core.config import get_recordings_dir
        current_dir = str(get_recordings_dir())
        
        # Открыть диалог выбора папки
        new_folder = QFileDialog.getExistingDirectory(
            self,
            t("settings.recordings.change_folder_dialog"),
            current_dir,
            QFileDialog.Option.ShowDirsOnly
        )
        
        if new_folder:
            try:
                # Сохранить в config.jsonc
                from core.config_saver import get_config_saver
                config_saver = get_config_saver()
                config_saver.update_value("recording.recordings_path", new_folder)
                
                # Обновить label
                self.recordings_path_label.setText(f"📁 <a href='file:///{new_folder}'>{new_folder}</a>")
                
                # Обновить список записей
                self._refresh_recordings_list()
                
                logger.info(f"Папка записей изменена на: {new_folder}")
                
                QMessageBox.information(
                    self,
                    t("settings.recordings.change_folder_success_title"),
                    t("settings.recordings.change_folder_success_message", folder=new_folder),
                    QMessageBox.StandardButton.Ok
                )
            except Exception as e:
                logger.error(f"Не удалось изменить папку: {e}")
                QMessageBox.critical(
                    self,
                    t("settings.recordings.change_folder_error_title"),
                    t("settings.recordings.change_folder_error_message", error=str(e)),
                    QMessageBox.StandardButton.Ok
                )
    
    def _reset_recordings_folder(self):
        """Сбрасывает папку записей на значение по умолчанию."""
        from core.config import get_config_dir
        
        # Подтверждение
        reply = QMessageBox.question(
            self,
            t("settings.recordings.reset_folder_confirm_title"),
            t("settings.recordings.reset_folder_confirm_message", folder=str(get_config_dir() / 'recordings')),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Удалить RECORDINGS_PATH из config.jsonc (установить пустое значение)
                from core.config_saver import get_config_saver
                config_saver = get_config_saver()
                config_saver.update_value("recording.recordings_path", "")
                
                # Получить папку по умолчанию
                default_dir = get_config_dir() / 'recordings'
                
                # Обновить label
                self.recordings_path_label.setText(f"📁 <a href='file:///{default_dir}'>{default_dir}</a>")
                
                # Обновить список записей
                self._refresh_recordings_list()
                
                logger.info("Папка записей сброшена на значение по умолчанию")
                
                QMessageBox.information(
                    self,
                    t("settings.recordings.reset_folder_success_title"),
                    t("settings.recordings.reset_folder_success_message", folder=str(default_dir)),
                    QMessageBox.StandardButton.Ok
                )
            except Exception as e:
                logger.error(f"Не удалось сбросить папку: {e}")
                QMessageBox.critical(
                    self,
                    t("settings.recordings.reset_folder_error_title"),
                    t("settings.recordings.reset_folder_error_message", error=str(e)),
                    QMessageBox.StandardButton.Ok
                )
    
    def _create_about_page(self) -> QWidget:
        """Создает страницу О программе."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel(t("settings.about.title"))
        title.setObjectName("pageTitle")  # Применить стиль
        layout.addWidget(title)
        
        # Информация о программе
        info_group = QGroupBox("RapidWhisper")
        info_layout = QVBoxLayout()
        info_layout.setSpacing(16)
        
        # Версия
        version_label = QLabel(t("settings.about.version"))
        version_label.setStyleSheet("font-size: 13px;")
        info_layout.addWidget(version_label)
        
        # Описание
        desc_label = QLabel(t("settings.about.description"))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #888888; font-size: 12px;")
        info_layout.addWidget(desc_label)
        
        # Ссылки (из конфигурации)
        github_url = self.config.github_url
        docs_url = self.config.docs_url
        
        links_label = QLabel(t("settings.about.links", github_url=github_url, docs_url=docs_url))
        links_label.setWordWrap(True)
        links_label.setOpenExternalLinks(True)
        links_label.setStyleSheet("font-size: 12px;")
        info_layout.addWidget(links_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Используемые библиотеки
        libs_group = QGroupBox(t("settings.about.libraries"))
        libs_layout = QVBoxLayout()
        libs_layout.setSpacing(12)
        
        libs_label = QLabel(t("settings.about.libraries_main"))
        libs_label.setWordWrap(True)
        libs_label.setOpenExternalLinks(True)
        libs_label.setStyleSheet("color: #888888; font-size: 11px;")
        libs_layout.addWidget(libs_label)
        
        libs_group.setLayout(libs_layout)
        layout.addWidget(libs_group)
        
        # Поддерживаемые провайдеры
        providers_group = QGroupBox(t("settings.about.providers"))
        providers_layout = QVBoxLayout()
        providers_layout.setSpacing(12)
        
        providers_label = QLabel(t("settings.about.providers_list"))
        providers_label.setWordWrap(True)
        providers_label.setOpenExternalLinks(True)
        providers_label.setStyleSheet("color: #888888; font-size: 11px;")
        providers_layout.addWidget(providers_label)
        
        providers_group.setLayout(providers_layout)
        layout.addWidget(providers_group)
        
        # Лицензия
        license_group = QGroupBox(t("settings.about.license"))
        license_layout = QVBoxLayout()
        
        license_label = QLabel(t("settings.about.license_text"))
        license_label.setStyleSheet("color: #888888; font-size: 11px;")
        license_layout.addWidget(license_label)
        
        license_group.setLayout(license_layout)
        layout.addWidget(license_group)
        
        widget.setLayout(layout)
        return widget
    
    def _load_values(self):
        """Загружает текущие значения конфигурации в поля."""
        # AI Provider
        self.provider_combo.setCurrentText(self.config.ai_provider)
        self.groq_key_edit.setText(self.config.groq_api_key)
        self.openai_key_edit.setText(self.config.openai_api_key)
        self.glm_key_edit.setText(self.config.glm_api_key)
        self.custom_key_edit.setText(self.config.custom_api_key)
        self.custom_url_edit.setText(self.config.custom_base_url)
        self.custom_model_edit.setText(self.config.custom_model)
        
        # Transcription Model
        transcription_model = getattr(self.config, 'transcription_model', '')
        if transcription_model:
            self.transcription_model_combo.setCurrentText(transcription_model)
        else:
            # Установить дефолтное значение в зависимости от провайдера
            if self.config.ai_provider == "groq":
                self.transcription_model_combo.setCurrentText("whisper-large-v3 (Groq default)")
            elif self.config.ai_provider == "openai":
                self.transcription_model_combo.setCurrentText("whisper-1 (OpenAI default)")
            elif self.config.ai_provider == "glm":
                self.transcription_model_combo.setCurrentText("glm-4-voice (GLM default)")
            else:
                self.transcription_model_combo.setCurrentText("")
        
        # Приложение
        self.hotkey_edit.setText(self.config.hotkey)
        self.silence_threshold_spin.setValue(self.config.silence_threshold)
        self.silence_duration_spin.setValue(self.config.silence_duration)
        self.manual_stop_check.setChecked(self.config.manual_stop)
        self.auto_hide_spin.setValue(self.config.auto_hide_delay)
        self.remember_position_check.setChecked(self.config.remember_window_position)
        
        # Загрузить предустановленную позицию
        position_preset = getattr(self.config, 'window_position_preset', 'center')
        position_map = {
            'center': 0,
            'top_left': 1,
            'top_right': 2,
            'bottom_left': 3,
            'bottom_right': 4,
            'custom': 5
        }
        self.window_position_combo.setCurrentIndex(position_map.get(position_preset, 0))
        
        # Обновить состояние выпадающего списка
        self._on_remember_position_changed(self.config.remember_window_position)
        
        # Обновить состояние настроек тишины
        self._on_manual_stop_changed(self.config.manual_stop)
        
        # Аудио
        self.sample_rate_combo.setCurrentText(str(self.config.sample_rate))
        self.chunk_size_combo.setCurrentText(str(self.config.chunk_size))
        self.silence_padding_spin.setValue(self.config.silence_padding)
        
        # Записи
        self.keep_recordings_check.setChecked(self.config.keep_recordings)
        
        # Постобработка
        self.enable_post_processing_check.setChecked(self.config.enable_post_processing)
        self.post_processing_provider_combo.setCurrentText(self.config.post_processing_provider)
        
        # GLM Coding Plan
        self.glm_coding_plan_check.setChecked(self.config.glm_use_coding_plan)
        
        # LLM настройки
        self.llm_base_url_edit.setText(self.config.llm_base_url)
        self.llm_api_key_edit.setText(self.config.llm_api_key)
        
        # Загрузить модели для выбранного провайдера
        self._on_post_processing_provider_changed(self.config.post_processing_provider)
        
        # Установить модель
        self.post_processing_model_combo.setCurrentText(self.config.post_processing_model)
        
        # Установить кастомную модель
        self.post_processing_custom_model_edit.setText(self.config.post_processing_custom_model)
        
        # Установить промпт
        self.post_processing_prompt_edit.setPlainText(self.config.post_processing_prompt)
        
        # Обновить состояние полей
        self._on_post_processing_toggled(self.config.enable_post_processing)
        
        # Форматирование
        from services.formatting_config import FormattingConfig
        from core.config_loader import get_config_loader
        formatting_config = FormattingConfig.from_config(get_config_loader())
        self.enable_formatting_check.setChecked(formatting_config.enabled)
        self.formatting_provider_combo.setCurrentText(formatting_config.provider)
        self.formatting_model_edit.setText(formatting_config.model)
        self.formatting_custom_url_edit.setText(formatting_config.custom_base_url)
        self.formatting_custom_key_edit.setText(formatting_config.custom_api_key)
        
        # Загрузить приложения в визуальную сетку
        self._refresh_formatting_apps_grid()
        
        self.formatting_temperature_spin.setValue(formatting_config.temperature)
        
        # Обновить состояние полей форматирования
        self._on_formatting_toggled(formatting_config.enabled)
        
        # Обновить видимость custom полей
        self._on_formatting_provider_changed(formatting_config.provider)
        
        # Обновить подсветку активного провайдера
        self._on_provider_changed(self.config.ai_provider)
        
        # Язык интерфейса
        language_code = self.config.interface_language
        # Найти кнопку с нужным language_code
        found = False
        for button in self.language_button_group.buttons():
            if button.property("language_code") == language_code:
                button.setChecked(True)
                found = True
                break
        
        # Если не найдено, выбрать русский по умолчанию (индекс 8)
        if not found:
            default_button = self.language_button_group.button(8)  # RU
            if default_button:
                default_button.setChecked(True)
    
    def _on_remember_position_changed(self, checked: bool):
        """
        Обработчик изменения чекбокса запоминания позиции.
        
        Включает/выключает выпадающий список позиций.
        """
        # Если чекбокс выключен, показываем выпадающий список
        # Если включен, скрываем (используется пользовательская позиция)
        self.window_position_combo.setEnabled(not checked)
    
    def _on_manual_stop_changed(self, checked: bool):
        """
        Обработчик изменения чекбокса ручной остановки.
        
        Включает/выключает настройки автоматического определения тишины.
        """
        # Если ручная остановка включена, отключаем настройки тишины
        self.silence_threshold_spin.setEnabled(not checked)
        self.silence_duration_spin.setEnabled(not checked)
    
    def _reset_hotkey(self):
        """
        Сбрасывает горячую клавишу на текущее сохраненное значение.
        
        Загружает значение из конфигурации и устанавливает в поле.
        """
        # Загрузить текущее значение из конфигурации
        current_hotkey = self.config.hotkey
        
        # Установить в поле
        self.hotkey_edit.setText(current_hotkey)
        
        # Убрать фокус с поля
        self.hotkey_edit.clearFocus()
        
        logger.info(f"Горячая клавиша сброшена на: {current_hotkey}")
    
    def _on_provider_changed(self, provider: str):
        """
        Обработчик изменения провайдера AI.
        
        Подсвечивает соответствующее поле API ключа.
        """
        # Сбросить стили
        self.groq_key_edit.setStyleSheet("")
        self.openai_key_edit.setStyleSheet("")
        self.glm_key_edit.setStyleSheet("")
        self.custom_key_edit.setStyleSheet("")
        self.custom_url_edit.setStyleSheet("")
        self.custom_model_edit.setStyleSheet("")
        
        # Подсветить активное поле
        if provider == "groq":
            self.groq_key_edit.setStyleSheet("border: 2px solid #0078d4;")
        elif provider == "openai":
            self.openai_key_edit.setStyleSheet("border: 2px solid #0078d4;")
        elif provider == "glm":
            self.glm_key_edit.setStyleSheet("border: 2px solid #0078d4;")
        elif provider == "custom":
            self.custom_key_edit.setStyleSheet("border: 2px solid #0078d4;")
            self.custom_url_edit.setStyleSheet("border: 2px solid #0078d4;")
            self.custom_model_edit.setStyleSheet("border: 2px solid #0078d4;")
    
    def _on_post_processing_toggled(self, checked: bool):
        """Обработчик включения/выключения постобработки."""
        self.post_processing_provider_combo.setEnabled(checked)
        self.post_processing_model_combo.setEnabled(checked)
        self.post_processing_custom_model_edit.setEnabled(checked)
        self.post_processing_prompt_edit.setEnabled(checked)
    
    def _on_post_processing_provider_changed(self, provider: str):
        """Обработчик изменения провайдера постобработки."""
        # Обновить список моделей в зависимости от провайдера
        self.post_processing_model_combo.clear()
        
        if provider == "groq":
            models = [
                "llama-3.3-70b-versatile",
                "llama-3.1-70b-versatile",
                "mixtral-8x7b-32768"
            ]
        elif provider == "openai":
            models = [
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo"
            ]
        elif provider == "glm":
            # GLM модели (зависит от чекбокса Coding Plan)
            if hasattr(self, 'glm_coding_plan_check') and self.glm_coding_plan_check.isChecked():
                # Coding Plan модели
                models = [
                    "glm-4.7",
                    "glm-4.6",
                    "glm-4.5",
                    "glm-4.5-air"
                ]
            else:
                # Обычные GLM модели
                models = [
                    "glm-4-plus",
                    "glm-4-0520",
                    "glm-4-air",
                    "glm-4-airx",
                    "glm-4-flash"
                ]
        elif provider == "llm":
            # LLM - локальные модели (пользователь вводит название сам)
            models = [
                "llama-3.3-70b-versatile",
                "mistral-7b-instruct",
                "mixtral-8x7b-instruct",
                "qwen-2.5-72b-instruct",
                "custom"  # Пользователь может ввести свою модель
            ]
        else:
            models = ["llama-3.3-70b-versatile"]
        
        self.post_processing_model_combo.addItems(models)
        
        # Показать/скрыть GLM Coding Plan чекбокс
        if hasattr(self, 'glm_coding_plan_check'):
            self.glm_coding_plan_check.setVisible(provider == "glm")
        
        # Показать/скрыть LLM Base URL и API Key
        if hasattr(self, 'llm_base_url_edit'):
            self.llm_base_url_edit.setVisible(provider == "llm")
            self.llm_base_url_label.setVisible(provider == "llm")
        if hasattr(self, 'llm_api_key_edit'):
            self.llm_api_key_edit.setVisible(provider == "llm")
            self.llm_api_key_label.setVisible(provider == "llm")
    
    def _on_formatting_toggled(self, checked: bool):
        """Handler for enabling/disabling formatting."""
        self.formatting_provider_combo.setEnabled(checked)
        self.formatting_model_edit.setEnabled(checked)
        self.formatting_temperature_spin.setEnabled(checked)
        # Enable/disable application buttons
        for btn in self.formatting_app_buttons.values():
            btn.setEnabled(checked)
    
    def _on_formatting_provider_changed(self, provider: str):
        """Handler for formatting provider change."""
        # Update placeholder text based on provider
        if provider == "groq":
            self.formatting_model_edit.setPlaceholderText("опционально, по умолчанию: llama-3.3-70b-versatile")
        elif provider == "openai":
            self.formatting_model_edit.setPlaceholderText("опционально, по умолчанию: gpt-4o-mini")
        elif provider == "glm":
            self.formatting_model_edit.setPlaceholderText("опционально, по умолчанию: glm-4-flash")
        elif provider == "custom":
            self.formatting_model_edit.setPlaceholderText("название модели для custom провайдера")
        
        # Show/hide custom provider fields (including the eye button)
        is_custom = provider == "custom"
        self.formatting_custom_url_edit.setVisible(is_custom)
        self.formatting_custom_url_label.setVisible(is_custom)
        self.formatting_custom_key_edit.setVisible(is_custom)
        self.formatting_custom_key_label.setVisible(is_custom)
        self.formatting_custom_key_show_btn.setVisible(is_custom)
        
        # Показать/скрыть дополнительные поля для постобработки
        if hasattr(self, 'glm_coding_plan_check'):
            self.glm_coding_plan_check.setVisible(provider == "glm")
        if hasattr(self, 'llm_base_url_edit'):
            self.llm_base_url_edit.setVisible(provider == "llm")
            self.llm_base_url_label.setVisible(provider == "llm")
        if hasattr(self, 'llm_api_key_edit'):
            self.llm_api_key_edit.setVisible(provider == "llm")
            self.llm_api_key_label.setVisible(provider == "llm")
    
    def _refresh_formatting_apps_grid(self):
        """Refresh the visual grid of formatting applications."""
        # Clear existing buttons
        for i in reversed(range(self.formatting_apps_grid.count())):
            widget = self.formatting_apps_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        self.formatting_app_buttons.clear()
        
        # Load current config
        from services.formatting_config import FormattingConfig
        from core.config_loader import get_config_loader
        config = FormattingConfig.from_config(get_config_loader())
        
        # Create buttons for each application
        row = 0
        col = 0
        for app_name in config.applications:
            # Get display name for special apps
            if app_name == "_fallback":
                display_name = "🌐 Универсальный"
            else:
                display_name = app_name
            
            btn = QPushButton(display_name)
            btn.setCheckable(False)
            btn.setMinimumHeight(80)
            btn.setMinimumWidth(120)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(
                lambda pos, name=app_name, button=btn: self._show_app_context_menu(name, button.mapToGlobal(pos))
            )
            
            # Check if app has custom prompt
            has_custom_prompt = app_name in config.app_prompts and config.app_prompts[app_name]
            
            # Style button
            if has_custom_prompt:
                # Custom prompt - show with indicator
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2d2d2d;
                        color: #ffffff;
                        border: 2px solid #0078d4;
                        border-radius: 8px;
                        padding: 8px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #3d3d3d;
                        border-color: #1084d8;
                    }
                """)
                btn.setText(f"✏️ {display_name}")
            else:
                # Default prompt
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2d2d2d;
                        color: #ffffff;
                        border: 2px solid #3d3d3d;
                        border-radius: 8px;
                        padding: 8px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #3d3d3d;
                        border-color: #0078d4;
                    }
                """)
                btn.setText(display_name)
            
            self.formatting_apps_grid.addWidget(btn, row, col)
            self.formatting_app_buttons[app_name] = btn
            
            col += 1
            if col >= 4:
                col = 0
                row += 1
    
    def _show_app_context_menu(self, app_name: str, position: QPoint):
        """Show context menu for application card."""
        menu = QMenu(self)
        
        edit_action = menu.addAction(f"✏️ {t('settings.formatting.edit_application')}")
        delete_action = menu.addAction(f"🗑️ {t('settings.formatting.delete_application')}")
        
        # Disable delete for system applications (_fallback) or if only one application
        from services.formatting_config import FormattingConfig
        from core.config_loader import get_config_loader
        config = FormattingConfig.from_config(get_config_loader())
        if len(config.applications) <= 1 or app_name == "_fallback":
            delete_action.setEnabled(False)
        
        action = menu.exec(position)
        
        if action == edit_action:
            self._edit_application_prompt(app_name)
        elif action == delete_action:
            self._delete_application(app_name)
    
    def _edit_application_prompt(self, app_name: str):
        """Open dialog to edit application prompt."""
        from services.formatting_config import FormattingConfig
        from core.config_loader import get_config_loader
        from core.config_saver import get_config_saver
        
        # Load current config
        config = FormattingConfig.from_config(get_config_loader())
        current_prompt = config.get_prompt_for_app(app_name)
        
        # Show edit dialog
        new_prompt = PromptEditDialog.edit_prompt(app_name, current_prompt, self)
        
        if new_prompt is not None:
            # Save new prompt to file immediately
            config_saver = get_config_saver()
            config_saver.save_prompt(app_name, new_prompt)
            
            # Clear the prompts cache to force reload
            config_loader = get_config_loader()
            config_loader.prompts_cache.clear()
            
            # Also update the config structure to ensure prompt file path exists
            config_loader.load()
            
            if "formatting" not in config_loader.config:
                config_loader.config["formatting"] = {}
            if "app_prompts" not in config_loader.config["formatting"]:
                config_loader.config["formatting"]["app_prompts"] = {}
            
            # Ensure prompt file path is registered
            if app_name not in config_loader.config["formatting"]["app_prompts"]:
                config_loader.config["formatting"]["app_prompts"][app_name] = f"config/prompts/{app_name}.txt"
                config_saver.save_config(config_loader.config)
            
            logger.info(f"✓ Prompt for '{app_name}' saved and applied without restart")
            
            # Emit settings_saved signal to trigger hot reload in main app
            self.settings_saved.emit()
            
            # Show notification
            if self.tray_icon:
                self.tray_icon.show_message(
                    t("tray.notification.prompt_saved"),
                    t("tray.notification.prompt_saved_message", app=app_name),
                    duration=3000
                )
            
            # Refresh grid
            self._refresh_formatting_apps_grid()
    
    def _delete_application(self, app_name: str):
        """Delete application from list."""
        from services.formatting_config import FormattingConfig
        from core.config_loader import get_config_loader
        from core.config_saver import get_config_saver
        
        # Load current config
        config = FormattingConfig.from_config(get_config_loader())
        
        # Check if it's the last application
        if len(config.applications) <= 1:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Нельзя удалить последнее приложение. Должно остаться хотя бы одно.",
                QMessageBox.StandardButton.Ok
            )
            return
        
        # Remove application
        config.applications.remove(app_name)
        if app_name in config.app_prompts:
            del config.app_prompts[app_name]
        
        # Save config
        config.save_to_config()
        
        # Refresh grid
        self._refresh_formatting_apps_grid()
    
    def _on_add_application_clicked(self):
        """Handle add application button click."""
        from services.formatting_config import FormattingConfig
        from core.config_loader import get_config_loader
        from core.config_saver import get_config_saver
        
        # Load current config
        config = FormattingConfig.from_config(get_config_loader())
        
        # Show add dialog (empty prompt by default)
        result = AddApplicationDialog.add_application(config.applications, "", self)
        
        if result:
            app_name, prompt = result
            
            # Add application
            config.applications.append(app_name)
            config.set_prompt_for_app(app_name, prompt)
            
            # Save config
            config.save_to_config()
            
            # Save prompt to file
            config_saver = get_config_saver()
            config_saver.save_prompt(app_name, prompt)
            
            # Refresh grid
            self._refresh_formatting_apps_grid()
    
    def _on_web_keywords_clicked(self):
        """Handle web keywords configuration button click."""
        from services.formatting_config import FormattingConfig
        from core.config_loader import get_config_loader
        
        # Load current config
        config = FormattingConfig.from_config(get_config_loader())
        
        # Show web keywords dialog
        dialog = WebKeywordsDialog(config.web_app_keywords, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get updated keywords
            updated_keywords = dialog.get_keywords()
            
            # Update config
            config.web_app_keywords = updated_keywords
            
            # Save config
            config.save_to_config()
            
            # Show success message
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Успешно",
                "Ключевые слова веб-приложений обновлены!"
            )
    
    
    def _reload_ui_texts(self):
        """Перезагружает все тексты в интерфейсе после смены языка."""
        # Обновить заголовок окна
        self.setWindowTitle(t("settings.title"))
        
        # Обновить боковую панель
        sidebar_items = [
            (f"🤖 {t('settings.ai_provider.title')}", 0),
            (f"⚡ {t('settings.app.title')}", 1),
            (f"🎤 {t('settings.audio.title')}", 2),
            (f"✨ {t('settings.processing.title')}", 3),
            (f"🌍 {t('settings.languages.title')}", 4),
            (f"🎨 {t('settings.ui_customization.title')}", 5),
            (f"🎙️ {t('settings.recordings.title')}", 6),
            (f"ℹ️ {t('settings.about.title')}", 7)
        ]
        
        for text, index in sidebar_items:
            item = self.sidebar.item(index)
            if item:
                item.setText(text)
        
        # Обновить кнопки внизу
        # Найти кнопки по objectName
        for button in self.findChildren(QPushButton):
            if button.objectName() == "cancelButton":
                button.setText(t("common.cancel"))
            elif button.text().startswith("💾"):
                button.setText(t("common.save"))
        
        # Обновить info panel в floating window если доступен
        parent_widget = self.parent()
        if parent_widget and hasattr(parent_widget, 'info_panel') and parent_widget.info_panel:
            parent_widget.info_panel.reload_translations()
        
        # Перезагрузить текущую страницу
        current_index = self.content_stack.currentIndex()
        
        # Сохранить текущие значения полей
        current_values = self._get_current_values()
        
        # Пересоздать страницы с новыми переводами
        self.content_stack.removeWidget(self.content_stack.widget(0))
        self.content_stack.insertWidget(0, self._wrap_in_scroll_area(self._create_ai_page()))
        
        self.content_stack.removeWidget(self.content_stack.widget(1))
        self.content_stack.insertWidget(1, self._wrap_in_scroll_area(self._create_app_page()))
        
        self.content_stack.removeWidget(self.content_stack.widget(2))
        self.content_stack.insertWidget(2, self._wrap_in_scroll_area(self._create_audio_page()))
        
        self.content_stack.removeWidget(self.content_stack.widget(3))
        self.content_stack.insertWidget(3, self._wrap_in_scroll_area(self._create_processing_page()))
        
        self.content_stack.removeWidget(self.content_stack.widget(4))
        self.content_stack.insertWidget(4, self._wrap_in_scroll_area(self._create_languages_page()))
        
        self.content_stack.removeWidget(self.content_stack.widget(5))
        self.content_stack.insertWidget(5, self._wrap_in_scroll_area(self._create_ui_customization_page()))
        
        self.content_stack.removeWidget(self.content_stack.widget(6))
        self.content_stack.insertWidget(6, self._wrap_in_scroll_area(self._create_recordings_page()))
        
        self.content_stack.removeWidget(self.content_stack.widget(7))
        self.content_stack.insertWidget(7, self._wrap_in_scroll_area(self._create_about_page()))
        
        # Восстановить текущую страницу
        self.content_stack.setCurrentIndex(current_index)
        
        # Восстановить значения полей
        self._restore_current_values(current_values)
    
    def _get_current_values(self):
        """Сохраняет текущие значения всех полей."""
        return {
            'provider': self.provider_combo.currentText(),
            'groq_key': self.groq_key_edit.text(),
            'openai_key': self.openai_key_edit.text(),
            'glm_key': self.glm_key_edit.text(),
            'custom_key': self.custom_key_edit.text(),
            'custom_url': self.custom_url_edit.text(),
            'custom_model': self.custom_model_edit.text(),
            'hotkey': self.hotkey_edit.text(),
            'silence_threshold': self.silence_threshold_spin.value(),
            'silence_duration': self.silence_duration_spin.value(),
            'manual_stop': self.manual_stop_check.isChecked(),
            'auto_hide': self.auto_hide_spin.value(),
            'remember_position': self.remember_position_check.isChecked(),
            'window_position': self.window_position_combo.currentIndex(),
            'sample_rate': self.sample_rate_combo.currentText(),
            'chunk_size': self.chunk_size_combo.currentText(),
            'silence_padding': self.silence_padding_spin.value(),
            'keep_recordings': self.keep_recordings_check.isChecked(),
            'enable_post_processing': self.enable_post_processing_check.isChecked(),
            'post_processing_provider': self.post_processing_provider_combo.currentText(),
            'post_processing_model': self.post_processing_model_combo.currentText(),
            'post_processing_custom_model': self.post_processing_custom_model_edit.text(),
            'post_processing_prompt': self.post_processing_prompt_edit.toPlainText(),
            'glm_coding_plan': self.glm_coding_plan_check.isChecked(),
            'llm_base_url': self.llm_base_url_edit.text(),
            'llm_api_key': self.llm_api_key_edit.text(),
            'opacity': self.opacity_slider.value(),
            'font_floating_main': self.font_floating_main_spin.value(),
            'font_floating_info': self.font_floating_info_spin.value(),
            'font_settings_labels': self.font_settings_labels_spin.value(),
            'font_settings_titles': self.font_settings_titles_spin.value(),
        }
    
    def _restore_current_values(self, values):
        """Восстанавливает значения всех полей."""
        self.provider_combo.setCurrentText(values['provider'])
        self.groq_key_edit.setText(values['groq_key'])
        self.openai_key_edit.setText(values['openai_key'])
        self.glm_key_edit.setText(values['glm_key'])
        self.custom_key_edit.setText(values['custom_key'])
        self.custom_url_edit.setText(values['custom_url'])
        self.custom_model_edit.setText(values['custom_model'])
        self.hotkey_edit.setText(values['hotkey'])
        self.silence_threshold_spin.setValue(values['silence_threshold'])
        self.silence_duration_spin.setValue(values['silence_duration'])
        self.manual_stop_check.setChecked(values['manual_stop'])
        self.auto_hide_spin.setValue(values['auto_hide'])
        self.remember_position_check.setChecked(values['remember_position'])
        self.window_position_combo.setCurrentIndex(values['window_position'])
        self.sample_rate_combo.setCurrentText(values['sample_rate'])
        self.chunk_size_combo.setCurrentText(values['chunk_size'])
        self.silence_padding_spin.setValue(values['silence_padding'])
        self.keep_recordings_check.setChecked(values['keep_recordings'])
        self.enable_post_processing_check.setChecked(values['enable_post_processing'])
        self.post_processing_provider_combo.setCurrentText(values['post_processing_provider'])
        self.post_processing_model_combo.setCurrentText(values['post_processing_model'])
        self.post_processing_custom_model_edit.setText(values['post_processing_custom_model'])
        
        # Проверить, является ли промпт дефолтным на любом языке
        current_prompt = values['post_processing_prompt']
        is_default_prompt = self._is_default_prompt(current_prompt)
        
        if is_default_prompt:
            # Если промпт дефолтный, заменить на переведенную версию
            self.post_processing_prompt_edit.setPlainText(t("settings.processing.prompt_default"))
        else:
            # Если промпт изменен пользователем, оставить как есть
            self.post_processing_prompt_edit.setPlainText(current_prompt)
        
        self.glm_coding_plan_check.setChecked(values['glm_coding_plan'])
        self.llm_base_url_edit.setText(values['llm_base_url'])
        self.llm_api_key_edit.setText(values['llm_api_key'])
        
        # UI Customization settings
        self.opacity_slider.setValue(int(values['opacity']))
        self.font_floating_main_spin.setValue(values['font_floating_main'])
        self.font_floating_info_spin.setValue(values['font_floating_info'])
        self.font_settings_labels_spin.setValue(values['font_settings_labels'])
        self.font_settings_titles_spin.setValue(values['font_settings_titles'])
        
        # Восстановить выбранный язык
        from utils.i18n import get_language
        current_language = get_language()
        for button in self.language_button_group.buttons():
            if button.property("language_code") == current_language:
                button.setChecked(True)
                break
        
        # Обновить состояния
        self._on_remember_position_changed(values['remember_position'])
        self._on_manual_stop_changed(values['manual_stop'])
        self._on_post_processing_toggled(values['enable_post_processing'])
        self._on_provider_changed(values['provider'])
        self._on_post_processing_provider_changed(values['post_processing_provider'])
    
    def _is_default_prompt(self, prompt: str) -> bool:
        """
        Проверяет, является ли промпт дефолтным на любом языке.
        
        Args:
            prompt: Текст промпта для проверки
            
        Returns:
            True если промпт совпадает с дефолтным на любом языке
        """
        # Список дефолтных промптов на всех языках
        default_prompts = [
            # English
            "You are a text editor. Your task: fix grammatical errors, add punctuation and improve text readability. Preserve the original meaning and style. Don't add anything extra. Return only the corrected text without comments.",
            # Russian
            "Ты - редактор текста. Твоя задача: исправить грамматические ошибки, добавить знаки препинания и улучшить читаемость текста. Сохрани оригинальный смысл и стиль. Не добавляй ничего лишнего. Верни только исправленный текст без комментариев.",
        ]
        
        # Проверить совпадение (игнорируя пробелы в начале/конце)
        prompt_stripped = prompt.strip()
        return any(prompt_stripped == default.strip() for default in default_prompts)
    
    def _get_transcription_model_value(self) -> str:
        """
        Получает значение модели транскрипции из комбобокса.
        Убирает суффиксы типа " (Groq default)" и возвращает чистое имя модели.
        Если выбрано дефолтное значение, возвращает пустую строку.
        """
        text = self.transcription_model_combo.currentText().strip()
        
        # Убрать суффиксы
        if " (Groq default)" in text:
            text = text.replace(" (Groq default)", "")
        elif " (OpenAI default)" in text:
            text = text.replace(" (OpenAI default)", "")
        elif " (GLM default)" in text:
            text = text.replace(" (GLM default)", "")
        
        # Если это дефолтная модель для провайдера, вернуть пустую строку
        provider = self.provider_combo.currentText()
        if provider == "groq" and text == "whisper-large-v3":
            return ""
        elif provider == "openai" and text == "whisper-1":
            return ""
        elif provider == "glm" and text == "glm-4-voice":
            return ""
        
        return text
    
    def _save_settings(self):
        """Сохраняет настройки в config.jsonc и secrets.json."""
        try:
            from core.config_saver import get_config_saver
            from utils.i18n import set_language
            
            # Получить новые значения
            position_index = self.window_position_combo.currentIndex()
            position_presets = ['center', 'top_left', 'top_right', 'bottom_left', 'bottom_right', 'custom']
            
            # Получить выбранный язык интерфейса
            selected_language = "ru"  # По умолчанию русский
            checked_button = self.language_button_group.checkedButton()
            if checked_button:
                language_code = checked_button.property("language_code")
                if language_code:
                    selected_language = language_code
            
            # Проверить, изменился ли язык
            old_language = self.config.interface_language
            language_changed = (selected_language != old_language)
            
            # Экранировать многострочные значения (заменить переносы строк на \n)
            post_processing_prompt = self.post_processing_prompt_edit.toPlainText().replace('\n', '\\n')
            
            # Подготовить обновления для config.jsonc
            config_updates = {
                "ai_provider.provider": self.provider_combo.currentText(),
                "ai_provider.custom.base_url": self.custom_url_edit.text(),
                "ai_provider.custom.model": self.custom_model_edit.text(),
                "ai_provider.transcription_model": self._get_transcription_model_value(),
                "application.hotkey": self.hotkey_edit.text(),
                "audio.silence_threshold": self.silence_threshold_spin.value(),
                "audio.silence_duration": self.silence_duration_spin.value(),
                "audio.manual_stop": self.manual_stop_check.isChecked(),
                "audio.sample_rate": int(self.sample_rate_combo.currentText()),
                "audio.chunk_size": int(self.chunk_size_combo.currentText()),
                "audio.silence_padding": int(self.silence_padding_spin.value()),
                "window.auto_hide_delay": self.auto_hide_spin.value(),
                "window.remember_position": self.remember_position_check.isChecked(),
                "window.position_preset": position_presets[position_index],
                "window.opacity": int(self.opacity_slider.value()),
                "window.font_sizes.floating_main": int(self.font_floating_main_spin.value()),
                "window.font_sizes.floating_info": int(self.font_floating_info_spin.value()),
                "window.font_sizes.settings_labels": int(self.font_settings_labels_spin.value()),
                "window.font_sizes.settings_titles": int(self.font_settings_titles_spin.value()),
                "recording.keep_recordings": self.keep_recordings_check.isChecked(),
                "post_processing.enabled": self.enable_post_processing_check.isChecked(),
                "post_processing.provider": self.post_processing_provider_combo.currentText(),
                "post_processing.model": self.post_processing_model_combo.currentText(),
                "post_processing.custom_model": self.post_processing_custom_model_edit.text(),
                "post_processing.prompt": post_processing_prompt,
                "post_processing.glm_use_coding_plan": self.glm_coding_plan_check.isChecked(),
                "post_processing.llm.base_url": self.llm_base_url_edit.text(),
                "post_processing.llm.api_key": self.llm_api_key_edit.text(),
                "localization.language": selected_language,
            }
            
            # Подготовить обновления для secrets.json (API ключи)
            secret_updates = {
                "ai_provider.api_keys.groq": self.groq_key_edit.text(),
                "ai_provider.api_keys.openai": self.openai_key_edit.text(),
                "ai_provider.api_keys.glm": self.glm_key_edit.text(),
                "ai_provider.custom.api_key": self.custom_key_edit.text(),
            }
            
            # Сохранить настройки форматирования через FormattingConfig
            from services.formatting_config import FormattingConfig
            from core.config_loader import get_config_loader
            formatting_config = FormattingConfig.from_config(get_config_loader())
            formatting_config.enabled = self.enable_formatting_check.isChecked()
            formatting_config.provider = self.formatting_provider_combo.currentText()
            formatting_config.model = self.formatting_model_edit.text()
            formatting_config.temperature = self.formatting_temperature_spin.value()
            formatting_config.custom_base_url = self.formatting_custom_url_edit.text()
            formatting_config.custom_api_key = self.formatting_custom_key_edit.text()
            # Applications and prompts are already managed through the grid UI
            formatting_config.save_to_config()
            
            # Сохранить все обновления config.jsonc
            config_saver = get_config_saver()
            config_saver.update_multiple_values(config_updates)
            
            # Сохранить все API ключи в secrets.json
            for key_path, value in secret_updates.items():
                if value:  # Сохранять только непустые ключи
                    config_saver.update_secret(key_path, value)
            
            logger.info("Настройки сохранены в config.jsonc и secrets.json")
            
            # Если язык изменился, обновить интерфейс ПЕРЕД показом сообщения
            if language_changed:
                logger.info(f"Language changed from {old_language} to {selected_language}")
                
                # Установить новый язык в модуле i18n
                set_language(selected_language)
                
                # Обновить конфигурацию
                self.config.interface_language = selected_language
                
                # Перезагрузить все тексты в окне
                self._reload_ui_texts()
                
                # Проверить что язык действительно изменился
                from utils.i18n import get_language
                current_lang = get_language()
                logger.info(f"Current language after set_language: {current_lang}")
                logger.info(f"Testing translation: {t('common.success')}")
            
            # Показать уведомление через tray icon (уже на новом языке если язык изменился)
            if self.tray_icon:
                success_title = t("tray.notification.settings_updated")
                success_message = t("tray.notification.settings_updated_message")
                logger.info(f"Notification title: {success_title}")
                logger.info(f"Notification message: {success_message}")
                
                self.tray_icon.show_message(
                    success_title,
                    success_message,
                    duration=3000
                )
            
            # Испустить сигнал
            self.settings_saved.emit()
            
            # НЕ закрываем окно автоматически - пользователь сам решает когда закрыть
            # Это обеспечивает последовательное поведение и позволяет изменить еще настройки
            
        except Exception as e:
            logger.error(f"Ошибка сохранения настроек: {e}")
            QMessageBox.critical(
                self,
                t("common.error"),
                t("errors.save_settings_failed", error=str(e)),
                QMessageBox.StandardButton.Ok
            )
    
    def center_on_screen(self) -> None:
        """
        Центрирует окно настроек на экране.
        
        Вызывается перед показом окна, чтобы оно всегда появлялось по центру,
        независимо от настроек позиции окна записи.
        """
        # Получить геометрию экрана
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            
            # Вычислить центр
            x = screen_geometry.center().x() - self.width() // 2
            y = screen_geometry.center().y() - self.height() // 2
            
            # Переместить окно
            self.move(x, y)
    
    def showEvent(self, event):
        """
        Override showEvent to force window update on Windows.
        
        This ensures the frameless transparent window is properly rendered.
        
        Args:
            event: Show event
        """
        super().showEvent(event)
        # Force repaint and update for proper rendering on Windows
        self.repaint()
        self.update()


class PromptEditDialog(QDialog):
    """Dialog for editing application-specific prompts."""
    
    def __init__(self, app_name: str, current_prompt: str, parent=None):
        """
        Initialize the prompt edit dialog.
        
        Args:
            app_name: Name of the application
            current_prompt: Current prompt text (or default)
            parent: Parent widget
        """
        super().__init__(parent)
        self.app_name = app_name
        self.setWindowTitle(t("settings.formatting.edit_prompt_title"))
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Get display name for special apps
        if app_name == "_fallback":
            display_name = "🌐 Универсальный (по умолчанию)"
        else:
            display_name = app_name
        
        # Application name label (read-only)
        app_label = QLabel(f"{t('settings.formatting.application_label')} {display_name}")
        app_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(app_label)
        
        # Prompt text edit
        prompt_label = QLabel(t("settings.formatting.system_prompt_label"))
        layout.addWidget(prompt_label)
        
        from PyQt6.QtWidgets import QTextEdit
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlainText(current_prompt)
        self.prompt_edit.setMinimumHeight(200)
        layout.addWidget(self.prompt_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton(t("settings.formatting.cancel_button"))
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton(t("settings.formatting.save_button"))
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def get_prompt(self) -> str:
        """Get the edited prompt text."""
        return self.prompt_edit.toPlainText()
    
    @staticmethod
    def edit_prompt(app_name: str, current_prompt: str, parent=None) -> Optional[str]:
        """
        Show dialog and return edited prompt, or None if cancelled.
        
        Args:
            app_name: Name of the application
            current_prompt: Current prompt text
            parent: Parent widget
            
        Returns:
            Edited prompt text, or None if cancelled
        """
        dialog = PromptEditDialog(app_name, current_prompt, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_prompt()
        return None


class AddApplicationDialog(QDialog):
    """Dialog for adding a new application."""
    
    def __init__(self, existing_apps: List[str], default_prompt: str, parent=None):
        """
        Initialize the add application dialog.
        
        Args:
            existing_apps: List of existing application names
            default_prompt: Universal default prompt
            parent: Parent widget
        """
        super().__init__(parent)
        self.existing_apps = existing_apps
        self.setWindowTitle(t("settings.formatting.add_application_title"))
        self.setMinimumWidth(600)
        self.setMinimumHeight(450)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Application name input
        name_label = QLabel(t("settings.formatting.application_name_label"))
        layout.addWidget(name_label)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(t("settings.formatting.application_name_placeholder"))
        layout.addWidget(self.name_edit)
        
        # Prompt text edit
        prompt_label = QLabel(t("settings.formatting.system_prompt_label"))
        layout.addWidget(prompt_label)
        
        from PyQt6.QtWidgets import QTextEdit
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlainText(default_prompt)
        self.prompt_edit.setMinimumHeight(200)
        layout.addWidget(self.prompt_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton(t("settings.formatting.cancel_button"))
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        add_btn = QPushButton(t("settings.formatting.add_button"))
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._on_add_clicked)
        button_layout.addWidget(add_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _on_add_clicked(self):
        """Handle add button click with validation."""
        app_name = self.name_edit.text().strip()
        
        # Validate empty name
        if not app_name:
            QMessageBox.warning(
                self,
                t("settings.formatting.error_title"),
                t("settings.formatting.error_empty_name"),
                QMessageBox.StandardButton.Ok
            )
            return
        
        # Validate duplicate name
        if app_name.lower() in [app.lower() for app in self.existing_apps]:
            QMessageBox.warning(
                self,
                t("settings.formatting.error_title"),
                t("settings.formatting.error_duplicate_name", name=app_name),
                QMessageBox.StandardButton.Ok
            )
            return
        
        # Accept dialog
        self.accept()
    
    def get_application_data(self) -> tuple[str, str]:
        """Get the application name and prompt."""
        return self.name_edit.text().strip(), self.prompt_edit.toPlainText()
    
    @staticmethod
    def add_application(existing_apps: List[str], default_prompt: str, parent=None) -> Optional[tuple[str, str]]:
        """
        Show dialog and return (app_name, prompt), or None if cancelled.
        
        Args:
            existing_apps: List of existing application names
            default_prompt: Universal default prompt
            parent: Parent widget
            
        Returns:
            Tuple of (app_name, prompt), or None if cancelled
        """
        dialog = AddApplicationDialog(existing_apps, default_prompt, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_application_data()
        return None



class WebKeywordsDialog(QDialog):
    """Dialog for editing web application keywords for browser detection."""
    
    def __init__(self, keywords_dict: Dict[str, List[str]], parent=None):
        """
        Initialize the web keywords dialog.
        
        Args:
            keywords_dict: Dictionary mapping format types to keyword lists
            parent: Parent widget
        """
        super().__init__(parent)
        self.keywords_dict = keywords_dict.copy()  # Work with a copy
        self.setWindowTitle("Настройка ключевых слов веб-приложений")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Info label
        info_label = QLabel(
            "Настройте ключевые слова для определения веб-приложений в браузерах.\n"
            "Система ищет эти слова в заголовке вкладки браузера."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(
            "color: #888888; "
            "font-size: 11px; "
            "padding: 8px; "
            "background-color: #2d2d2d; "
            "border-radius: 4px;"
        )
        layout.addWidget(info_label)
        
        # Tab widget for different format types
        from PyQt6.QtWidgets import QTabWidget, QTextEdit
        self.tab_widget = QTabWidget()
        self.keyword_editors = {}
        
        # Create a tab for each format type
        for format_type, keywords in sorted(self.keywords_dict.items()):
            tab = QWidget()
            tab_layout = QVBoxLayout()
            tab_layout.setSpacing(12)
            
            # Label
            label = QLabel(f"Ключевые слова для формата '{format_type}':")
            label.setStyleSheet("font-weight: bold;")
            tab_layout.addWidget(label)
            
            # Help text
            help_text = QLabel(
                "Введите ключевые слова, по одному на строку.\n"
                "Например: google docs, google документы"
            )
            help_text.setStyleSheet("color: #888888; font-size: 10px;")
            tab_layout.addWidget(help_text)
            
            # Text editor for keywords
            editor = QTextEdit()
            editor.setPlainText("\n".join(keywords))
            editor.setMinimumHeight(300)
            tab_layout.addWidget(editor)
            
            # Store editor reference
            self.keyword_editors[format_type] = editor
            
            tab.setLayout(tab_layout)
            self.tab_widget.addTab(tab, format_type)
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Reset to defaults button
        reset_btn = QPushButton("🔄 Сбросить к стандартным")
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.clicked.connect(self._on_reset_clicked)
        reset_btn.setToolTip("Восстановить стандартные ключевые слова")
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Отменить")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Сохранить")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _on_reset_clicked(self):
        """Reset keywords to defaults."""
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите сбросить все ключевые слова к стандартным значениям?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Load default keywords from config
            from services.formatting_config import FormattingConfig
            from core.config_loader import get_config_loader
            config = FormattingConfig.from_config(get_config_loader())
            
            # Update editors with default values from config
            for format_type, keywords in config.web_app_keywords.items():
                if format_type in self.keyword_editors:
                    self.keyword_editors[format_type].setPlainText("\n".join(keywords))
    
    def get_keywords(self) -> Dict[str, List[str]]:
        """Get the updated keywords dictionary."""
        result = {}
        
        for format_type, editor in self.keyword_editors.items():
            # Get text and split by lines
            text = editor.toPlainText()
            keywords = [
                line.strip()
                for line in text.split("\n")
                if line.strip()  # Skip empty lines
            ]
            result[format_type] = keywords
        
        return result
