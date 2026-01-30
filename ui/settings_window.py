"""
Окно настроек приложения RapidWhisper.

Предоставляет графический интерфейс для редактирования всех параметров
конфигурации из .env файла в стиле macOS с боковой панелью.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QDoubleSpinBox,
    QPushButton, QGroupBox, QMessageBox, QWidget, QListWidget, QStackedWidget, QListWidgetItem,
    QScrollArea, QApplication, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QScreen
from core.config import Config
from utils.logger import get_logger
from ui.hotkey_input import HotkeyInput
from pathlib import Path
import os

logger = get_logger()


class SettingsWindow(QDialog):
    """
    Окно настроек приложения.
    
    Позволяет редактировать все параметры конфигурации и сохранять их в .env файл.
    
    Signals:
        settings_saved: Сигнал при сохранении настроек
    """
    
    settings_saved = pyqtSignal()
    
    def __init__(self, config: Config, parent=None):
        """
        Инициализирует окно настроек.
        
        Args:
            config: Текущая конфигурация приложения
            parent: Родительский виджет
        """
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Настройки RapidWhisper")
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
        
        # Применить стиль
        self._apply_style()
        
        # Создать интерфейс
        self._create_ui()
        
        # Загрузить текущие значения
        self._load_values()
    
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
    
    def _apply_style(self):
        """Применяет стиль к окну настроек в стиле macOS."""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QLineEdit, QDoubleSpinBox, QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }
            QLineEdit:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border: 1px solid #0078d4;
            }
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006cc1;
            }
            QPushButton#cancelButton {
                background-color: #3d3d3d;
            }
            QPushButton#cancelButton:hover {
                background-color: #4d4d4d;
            }
            QGroupBox {
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
                margin-top: 20px;
                font-weight: bold;
                padding-top: 20px;
                background-color: #252525;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 8px 16px;
                background-color: #2d2d2d;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                border: 1px solid #0078d4;
            }
            QListWidget {
                background-color: #1a1a1a;
                border: none;
                border-right: 1px solid #2d2d2d;
                outline: none;
                padding: 8px 0px;
            }
            QListWidget::item {
                color: #ffffff;
                padding: 10px 16px;
                border-radius: 6px;
                margin: 2px 8px;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QListWidget::item:hover:!selected {
                background-color: #2d2d2d;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #1e1e1e;
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #3d3d3d;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4d4d4d;
            }
            QScrollBar::handle:vertical:pressed {
                background-color: #0078d4;
            }
            QLabel#pageTitle {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                padding: 12px 20px;
                background-color: #2d2d2d;
                border-radius: 6px;
                border: 2px solid #0078d4;
                margin-bottom: 8px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QLabel a {
                color: #0078d4;
                text-decoration: none;
            }
            QLabel a:hover {
                color: #1084d8;
                text-decoration: underline;
            }
        """)
    
    def _create_ui(self):
        """Создает интерфейс окна настроек в стиле macOS с боковой панелью."""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Левая панель навигации
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setSpacing(0)
        self.sidebar.setCursor(Qt.CursorShape.PointingHandCursor)  # Курсор "рука" для всего списка
        self.sidebar.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Не терять выделение при потере фокуса
        
        # Добавить пункты меню
        items = [
            ("🤖 AI Provider", "ai"),
            ("⚡ Приложение", "app"),
            ("🎤 Аудио", "audio"),
            ("✨ Обработка", "processing"),
            ("🌍 Языки", "languages"),
            ("🎙️ Записи", "recordings"),
            ("ℹ️ О программе", "about")
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
        self.content_stack.addWidget(self._wrap_in_scroll_area(self._create_recordings_page()))
        self.content_stack.addWidget(self._wrap_in_scroll_area(self._create_about_page()))
        
        right_panel_layout.addWidget(self.content_stack)
        
        # Кнопки внизу
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)  # Курсор "рука"
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Сохранить")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)  # Курсор "рука"
        save_btn.clicked.connect(self._save_settings)
        buttons_layout.addWidget(save_btn)
        
        right_panel_layout.addLayout(buttons_layout)
        
        right_panel.setLayout(right_panel_layout)
        main_layout.addWidget(right_panel, 1)
        
        self.setLayout(main_layout)
    
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
    
    def _create_ai_page(self) -> QWidget:
        """Создает страницу настроек AI Provider."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("AI Provider")
        title.setObjectName("pageTitle")  # Применить стиль
        layout.addWidget(title)
        
        # Группа: Выбор провайдера
        provider_group = QGroupBox("Провайдер")
        provider_layout = QFormLayout()
        provider_layout.setSpacing(12)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["groq", "openai", "glm", "custom"])
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
        self.provider_combo.setCursor(Qt.CursorShape.PointingHandCursor)  # Курсор "рука"
        provider_layout.addRow("Провайдер:", self.provider_combo)
        
        provider_group.setLayout(provider_layout)
        layout.addWidget(provider_group)
        
        # Группа: API ключи
        keys_group = QGroupBox("API Ключи")
        keys_layout = QFormLayout()
        
        # Groq API Key
        groq_layout = QHBoxLayout()
        self.groq_key_edit = QLineEdit()
        self.groq_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.groq_key_edit.setPlaceholderText("Введите Groq API ключ")
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
        
        groq_label = QLabel("Groq API Key:")
        groq_label.setToolTip("Получите на https://console.groq.com/keys")
        keys_layout.addRow(groq_label, groq_layout)
        
        # OpenAI API Key
        openai_layout = QHBoxLayout()
        self.openai_key_edit = QLineEdit()
        self.openai_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key_edit.setPlaceholderText("Введите OpenAI API ключ")
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
        
        openai_label = QLabel("OpenAI API Key:")
        openai_label.setToolTip("Получите на https://platform.openai.com/api-keys")
        keys_layout.addRow(openai_label, openai_layout)
        
        # GLM API Key
        glm_layout = QHBoxLayout()
        self.glm_key_edit = QLineEdit()
        self.glm_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.glm_key_edit.setPlaceholderText("Введите GLM API ключ")
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
        
        glm_label = QLabel("GLM API Key:")
        glm_label.setToolTip("Получите на https://open.bigmodel.cn/usercenter/apikeys")
        keys_layout.addRow(glm_label, glm_layout)
        
        # Custom API Key
        custom_layout = QHBoxLayout()
        self.custom_key_edit = QLineEdit()
        self.custom_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.custom_key_edit.setPlaceholderText("Введите Custom API ключ")
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
        
        custom_label = QLabel("Custom API Key:")
        custom_label.setToolTip("API ключ для кастомного OpenAI-совместимого API")
        keys_layout.addRow(custom_label, custom_layout)
        
        # Custom Base URL
        self.custom_url_edit = QLineEdit()
        self.custom_url_edit.setPlaceholderText("http://localhost:1234/v1/")
        custom_url_label = QLabel("Custom Base URL:")
        custom_url_label.setToolTip("URL endpoint для кастомного API (например, LM Studio, Ollama)")
        keys_layout.addRow(custom_url_label, self.custom_url_edit)
        
        # Custom Model
        self.custom_model_edit = QLineEdit()
        self.custom_model_edit.setPlaceholderText("whisper-1")
        custom_model_label = QLabel("Custom Model:")
        custom_model_label.setToolTip("Название модели для кастомного API")
        keys_layout.addRow(custom_model_label, self.custom_model_edit)
        
        keys_group.setLayout(keys_layout)
        layout.addWidget(keys_group)
        
        # Информация с кликабельными ссылками
        info_label = QLabel(
            "💡 <b>Совет:</b> Groq предоставляет бесплатный и быстрый API.<br>"
            "Рекомендуется для начала использования.<br><br>"
            "<b>Получить API ключи:</b><br>"
            "• Groq: <a href='https://console.groq.com/keys'>console.groq.com/keys</a><br>"
            "• OpenAI: <a href='https://platform.openai.com/api-keys'>platform.openai.com/api-keys</a><br>"
            "• GLM: <a href='https://open.bigmodel.cn/usercenter/apikeys'>open.bigmodel.cn/usercenter/apikeys</a><br><br>"
            "<b>Custom провайдер:</b><br>"
            "Поддерживает любые OpenAI-совместимые API:<br>"
            "• LM Studio: <a href='https://lmstudio.ai'>lmstudio.ai</a><br>"
            "• Ollama: <a href='https://ollama.ai'>ollama.ai</a><br>"
            "• vLLM, LocalAI и другие"
        )
        info_label.setWordWrap(True)
        info_label.setOpenExternalLinks(True)  # Открывать ссылки в браузере
        info_label.setToolTip("Кликните на ссылку чтобы открыть в браузере")
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
        title = QLabel("Приложение")
        title.setObjectName("pageTitle")  # Применить стиль
        layout.addWidget(title)
        
        # Группа: Горячие клавиши
        hotkey_group = QGroupBox("Горячие клавиши")
        hotkey_layout = QFormLayout()
        hotkey_layout.setSpacing(12)
        
        # Поле ввода горячей клавиши с кнопкой сброса
        hotkey_container = QHBoxLayout()
        self.hotkey_edit = HotkeyInput()
        self.hotkey_edit.setPlaceholderText("Нажмите сочетание клавиш...")
        hotkey_container.addWidget(self.hotkey_edit)
        
        # Кнопка сброса
        reset_hotkey_btn = QPushButton("🔄")
        reset_hotkey_btn.setMaximumWidth(40)
        reset_hotkey_btn.setToolTip("Сбросить на текущее сохраненное значение")
        reset_hotkey_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_hotkey_btn.clicked.connect(self._reset_hotkey)
        hotkey_container.addWidget(reset_hotkey_btn)
        
        hotkey_label = QLabel("Горячая клавиша:")
        hotkey_label.setToolTip("Нажмите сочетание клавиш для записи (например: Ctrl+Space, F1, Ctrl+Shift+R)")
        hotkey_layout.addRow(hotkey_label, hotkey_container)
        
        hotkey_group.setLayout(hotkey_layout)
        layout.addWidget(hotkey_group)
        
        # Группа: Интерфейс
        ui_group = QGroupBox("Интерфейс")
        ui_layout = QFormLayout()
        ui_layout.setSpacing(12)
        
        self.auto_hide_spin = QDoubleSpinBox()
        self.auto_hide_spin.setRange(1.0, 10.0)
        self.auto_hide_spin.setSingleStep(0.5)
        self.auto_hide_spin.setDecimals(1)
        self.auto_hide_spin.setSuffix(" сек")
        hide_label = QLabel("Автоскрытие:")
        hide_label.setToolTip("Задержка автоматического скрытия окна (1.0-10.0)")
        ui_layout.addRow(hide_label, self.auto_hide_spin)
        
        # Чекбокс для запоминания позиции окна
        self.remember_position_check = QCheckBox()
        self.remember_position_check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remember_position_check.toggled.connect(self._on_remember_position_changed)
        remember_label = QLabel("Запоминать позицию окна:")
        remember_label.setToolTip("Если включено, окно записи будет появляться в том месте, куда вы его перетащили")
        ui_layout.addRow(remember_label, self.remember_position_check)
        
        # Выпадающий список предустановленных позиций
        self.window_position_combo = QComboBox()
        self.window_position_combo.addItems([
            "Центр",
            "Левый верхний угол",
            "Правый верхний угол",
            "Левый нижний угол",
            "Правый нижний угол",
            "Пользовательская"
        ])
        self.window_position_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        position_label = QLabel("Позиция окна:")
        position_label.setToolTip("Выберите где будет появляться окно записи")
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
        title = QLabel("Аудио")
        title.setObjectName("pageTitle")  # Применить стиль
        layout.addWidget(title)
        
        # Группа: Параметры записи
        audio_group = QGroupBox("Параметры записи")
        audio_layout = QFormLayout()
        audio_layout.setSpacing(12)
        
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["16000", "44100", "48000"])
        self.sample_rate_combo.setCursor(Qt.CursorShape.PointingHandCursor)  # Курсор "рука"
        rate_label = QLabel("Частота дискретизации:")
        rate_label.setToolTip("Гц. 16000 рекомендуется для речи")
        audio_layout.addRow(rate_label, self.sample_rate_combo)
        
        self.chunk_size_combo = QComboBox()
        self.chunk_size_combo.addItems(["256", "512", "1024", "2048", "4096"])
        self.chunk_size_combo.setCursor(Qt.CursorShape.PointingHandCursor)  # Курсор "рука"
        chunk_label = QLabel("Размер чанка:")
        chunk_label.setToolTip("Фреймов. 1024 - оптимальное значение")
        audio_layout.addRow(chunk_label, self.chunk_size_combo)
        
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)
        
        # Группа: Определение тишины
        silence_group = QGroupBox("Определение тишины")
        silence_layout = QFormLayout()
        silence_layout.setSpacing(12)
        
        # Чекбокс ручной остановки
        self.manual_stop_check = QCheckBox()
        self.manual_stop_check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.manual_stop_check.toggled.connect(self._on_manual_stop_changed)
        manual_stop_label = QLabel("Ручная остановка:")
        manual_stop_label.setToolTip(
            "Если включено:\n"
            "• Запись НЕ останавливается автоматически по тишине\n"
            "• Вы сами останавливаете запись повторным нажатием горячей клавиши\n"
            "• Вся тишина автоматически удаляется перед отправкой"
        )
        silence_layout.addRow(manual_stop_label, self.manual_stop_check)
        
        # Описание режима
        manual_stop_info = QLabel(
            "💡 <b>Ручная остановка:</b> Запись продолжается даже при тишине. "
            "Остановите запись сами, нажав горячую клавишу повторно. "
            "Вся тишина будет автоматически удалена."
        )
        manual_stop_info.setWordWrap(True)
        manual_stop_info.setStyleSheet(
            "color: #888888; "
            "font-size: 11px; "
            "padding: 8px; "
            "background-color: #2d2d2d; "
            "border-radius: 4px;"
        )
        silence_layout.addRow("", manual_stop_info)
        
        self.silence_threshold_spin = QDoubleSpinBox()
        self.silence_threshold_spin.setRange(0.01, 0.1)
        self.silence_threshold_spin.setSingleStep(0.01)
        self.silence_threshold_spin.setDecimals(2)
        threshold_label = QLabel("Порог тишины:")
        threshold_label.setToolTip("RMS значение (0.01-0.1). Меньше = более чувствительно")
        silence_layout.addRow(threshold_label, self.silence_threshold_spin)
        
        self.silence_duration_spin = QDoubleSpinBox()
        self.silence_duration_spin.setRange(0.5, 5.0)
        self.silence_duration_spin.setSingleStep(0.5)
        self.silence_duration_spin.setDecimals(1)
        self.silence_duration_spin.setSuffix(" сек")
        duration_label = QLabel("Длительность тишины:")
        duration_label.setToolTip("Секунды тишины перед остановкой записи (0.5-5.0)")
        silence_layout.addRow(duration_label, self.silence_duration_spin)
        
        self.silence_padding_spin = QDoubleSpinBox()
        self.silence_padding_spin.setRange(100, 1000)
        self.silence_padding_spin.setSingleStep(50)
        self.silence_padding_spin.setDecimals(0)
        self.silence_padding_spin.setSuffix(" мс")
        padding_label = QLabel("Паддинг обрезки:")
        padding_label.setToolTip(
            "Отступ в миллисекундах перед и после звука при удалении тишины.\n"
            "Предотвращает обрезание на полуслове. (100-1000 мс)"
        )
        silence_layout.addRow(padding_label, self.silence_padding_spin)
        
        silence_group.setLayout(silence_layout)
        layout.addWidget(silence_group)
        
        # Информация
        info_label = QLabel(
            "⚠️ Внимание: Изменение параметров аудио может повлиять на качество записи.\n"
            "Рекомендуется оставить значения по умолчанию."
        )
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
        title = QLabel("Обработка")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        
        # Группа: Постобработка транскрипции
        post_processing_group = QGroupBox("Постобработка транскрипции")
        post_processing_layout = QVBoxLayout()
        post_processing_layout.setSpacing(12)
        
        # Чекбокс включения постобработки
        self.enable_post_processing_check = QCheckBox("Включить дополнительную обработку текста")
        self.enable_post_processing_check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.enable_post_processing_check.setToolTip(
            "После транскрипции текст будет отправлен на дополнительную обработку\n"
            "для исправления ошибок, добавления пунктуации и улучшения читаемости"
        )
        self.enable_post_processing_check.toggled.connect(self._on_post_processing_toggled)
        post_processing_layout.addWidget(self.enable_post_processing_check)
        
        # Описание
        info_label = QLabel(
            "💡 <b>Что делает постобработка:</b><br>"
            "• Исправляет грамматические ошибки<br>"
            "• Добавляет знаки препинания<br>"
            "• Улучшает структуру текста<br>"
            "• Сохраняет смысл и содержание<br><br>"
            "✅ <b>Groq</b> - бесплатный и быстрый (рекомендуется)<br>"
            "⚠️ <b>OpenAI</b> - платный, высокое качество<br>"
            "⚠️ <b>GLM</b> - обычный API (требует баланс) или Coding Plan<br>"
            "🖥️ <b>LLM</b> - локальные модели (LM Studio, Ollama, etc.)"
        )
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
        self.post_processing_provider_combo = QComboBox()
        self.post_processing_provider_combo.addItems(["groq", "openai", "glm", "llm"])
        self.post_processing_provider_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.post_processing_provider_combo.currentTextChanged.connect(self._on_post_processing_provider_changed)
        provider_label = QLabel("Провайдер:")
        provider_label.setToolTip(
            "AI провайдер для обработки текста\n\n"
            "💡 Groq - бесплатный и быстрый (рекомендуется)\n"
            "⚠️ OpenAI - платный, высокое качество\n"
            "⚠️ GLM - обычный API или Coding Plan (чекбокс ниже)\n"
            "🖥️ LLM - локальные модели (LM Studio, Ollama)"
        )
        settings_form.addRow(provider_label, self.post_processing_provider_combo)
        
        # Выбор модели
        self.post_processing_model_combo = QComboBox()
        self.post_processing_model_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        model_label = QLabel("Модель:")
        model_label.setToolTip("Модель для обработки текста")
        settings_form.addRow(model_label, self.post_processing_model_combo)
        
        # GLM Coding Plan чекбокс (показывается только для GLM)
        self.glm_coding_plan_check = QCheckBox("Использовать Coding Plan подписку")
        self.glm_coding_plan_check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.glm_coding_plan_check.setToolTip(
            "Если у вас есть подписка GLM Coding Plan,\n"
            "включите эту опцию для использования специального endpoint'а\n"
            "с доступом к моделям glm-4.5, glm-4.6, glm-4.7"
        )
        self.glm_coding_plan_check.toggled.connect(lambda: self._on_post_processing_provider_changed(self.post_processing_provider_combo.currentText()))
        self.glm_coding_plan_check.setVisible(False)  # Скрыто по умолчанию
        settings_form.addRow("", self.glm_coding_plan_check)
        
        # LLM Base URL (показывается только для LLM)
        self.llm_base_url_label = QLabel("LLM Base URL:")
        self.llm_base_url_label.setToolTip("URL локального LLM сервера (например, LM Studio, Ollama)")
        self.llm_base_url_edit = QLineEdit()
        self.llm_base_url_edit.setPlaceholderText("http://localhost:1234/v1/")
        self.llm_base_url_edit.setVisible(False)  # Скрыто по умолчанию
        self.llm_base_url_label.setVisible(False)
        settings_form.addRow(self.llm_base_url_label, self.llm_base_url_edit)
        
        # LLM API Key (показывается только для LLM)
        self.llm_api_key_label = QLabel("LLM API Key:")
        self.llm_api_key_label.setToolTip("API ключ для локального LLM (обычно не требуется, можно оставить 'local')")
        self.llm_api_key_edit = QLineEdit()
        self.llm_api_key_edit.setPlaceholderText("local")
        self.llm_api_key_edit.setVisible(False)  # Скрыто по умолчанию
        self.llm_api_key_label.setVisible(False)
        settings_form.addRow(self.llm_api_key_label, self.llm_api_key_edit)
        
        post_processing_layout.addLayout(settings_form)
        
        # Системный промпт (редактируемый)
        prompt_label = QLabel("Системный промпт:")
        prompt_label.setToolTip("Инструкция для модели по обработке текста")
        post_processing_layout.addWidget(prompt_label)
        
        from PyQt6.QtWidgets import QTextEdit
        self.post_processing_prompt_edit = QTextEdit()
        self.post_processing_prompt_edit.setPlaceholderText("Введите системный промпт для обработки текста...")
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
        title = QLabel("Языки")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        
        # Группа: Выбор языка
        language_group = QGroupBox("Язык интерфейса")
        language_layout = QVBoxLayout()
        language_layout.setSpacing(16)
        
        # Описание
        info_label = QLabel(
            "💡 <b>Язык интерфейса:</b><br>"
            "Выберите язык для будущей локализации интерфейса приложения.<br>"
            "Это НЕ влияет на язык транскрипции - вы можете говорить на любом языке."
        )
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
            ("GB", "English", "en"),
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
        
        # Добавить языки в сетку (5 колонок)
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
        
        # Выбрать русский по умолчанию (индекс 7)
        default_button = self.language_button_group.button(7)  # RU
        if default_button:
            default_button.setChecked(True)
        
        language_group.setLayout(language_layout)
        layout.addWidget(language_group)
        
        # Информация о будущей функциональности
        future_info = QLabel(
            "🚧 <b>В разработке:</b><br>"
            "• Перевод интерфейса на выбранный язык<br>"
            "• Локализация всех текстов и сообщений<br>"
            "• Адаптация форматов даты и времени"
        )
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
    
    def _create_recordings_page(self) -> QWidget:
        """Создает страницу управления записями."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("Записи")
        title.setObjectName("pageTitle")  # Применить стиль
        layout.addWidget(title)
        
        # Группа: Настройки сохранения
        save_group = QGroupBox("Настройки сохранения")
        save_layout = QVBoxLayout()
        save_layout.setSpacing(12)
        
        # Чекбокс для сохранения записей
        self.keep_recordings_check = QCheckBox("Сохранять записи после транскрипции")
        self.keep_recordings_check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.keep_recordings_check.setToolTip("Если включено, аудиозаписи будут сохраняться в папку recordings")
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
        self.recordings_path_label.setToolTip("Кликните чтобы открыть папку\n\nАудио: recordings/audio/\nТранскрипции: recordings/transcriptions/")
        folder_container.addWidget(self.recordings_path_label, 1)
        
        change_folder_btn = QPushButton("📁 Изменить папку")
        change_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        change_folder_btn.setToolTip("Выбрать другую папку для сохранения записей")
        change_folder_btn.clicked.connect(self._change_recordings_folder)
        change_folder_btn.setMaximumWidth(150)
        folder_container.addWidget(change_folder_btn)
        
        reset_folder_btn = QPushButton("🔄")
        reset_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_folder_btn.setToolTip("Сбросить на папку по умолчанию")
        reset_folder_btn.clicked.connect(self._reset_recordings_folder)
        reset_folder_btn.setMaximumWidth(40)
        folder_container.addWidget(reset_folder_btn)
        
        save_layout.addLayout(folder_container)
        
        save_group.setLayout(save_layout)
        layout.addWidget(save_group)
        
        # Группа: Сохраненные записи
        recordings_group = QGroupBox("Сохраненные записи")
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
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setToolTip("Обновить список записей")
        refresh_btn.clicked.connect(self._refresh_recordings_list)
        refresh_btn.setMaximumWidth(50)
        buttons_layout.addWidget(refresh_btn)
        
        play_btn = QPushButton("▶️ Аудио")
        play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        play_btn.setToolTip("Открыть выбранную аудиозапись в проигрывателе по умолчанию")
        play_btn.clicked.connect(self._open_recording)
        buttons_layout.addWidget(play_btn)
        
        self.text_btn = QPushButton("📝 Текст")
        self.text_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.text_btn.setToolTip("Открыть транскрипцию в текстовом редакторе")
        self.text_btn.clicked.connect(self._open_transcription)
        buttons_layout.addWidget(self.text_btn)
        
        folder_btn = QPushButton("📁 Папка")
        folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        folder_btn.setToolTip("Открыть папку с записями в проводнике")
        folder_btn.clicked.connect(self._open_recordings_folder)
        buttons_layout.addWidget(folder_btn)
        
        delete_btn = QPushButton("🗑️ Удалить")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setToolTip("Удалить выбранную запись (аудио и транскрипцию)")
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
            item = QListWidgetItem("📭 Нет сохраненных записей")
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
        open_audio_action = menu.addAction("▶️ Открыть аудио")
        open_audio_action.triggered.connect(self._open_recording)
        
        open_text_action = menu.addAction("📝 Открыть текст")
        open_text_action.setEnabled(has_transcription)
        open_text_action.triggered.connect(self._open_transcription)
        
        menu.addSeparator()
        
        open_folder_action = menu.addAction("📁 Открыть папку")
        open_folder_action.triggered.connect(self._open_recordings_folder)
        
        menu.addSeparator()
        
        delete_action = menu.addAction("🗑️ Удалить")
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
                "⚠️ Ошибка",
                f"Не удалось открыть запись:\n{str(e)}",
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
                "⚠️ Ошибка",
                f"Не удалось открыть транскрипцию:\n{str(e)}",
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
                "⚠️ Ошибка",
                f"Не удалось открыть папку:\n{str(e)}",
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
        message = f"Вы уверены что хотите удалить эту запись?\n\n{Path(recording_path).name}"
        if has_transcription:
            message += "\n\n(Аудио и транскрипция будут удалены)"
        
        reply = QMessageBox.question(
            self,
            "🗑️ Удалить запись?",
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
                    "❌ Ошибка",
                    f"Не удалось удалить запись:\n{str(e)}",
                    QMessageBox.StandardButton.Ok
                )
    
    def _change_recordings_folder(self):
        """Изменяет папку для сохранения записей."""
        from PyQt6.QtWidgets import QFileDialog
        from core.config import get_env_path
        from dotenv import set_key
        
        # Получить текущую папку
        from core.config import get_recordings_dir
        current_dir = str(get_recordings_dir())
        
        # Открыть диалог выбора папки
        new_folder = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для сохранения записей",
            current_dir,
            QFileDialog.Option.ShowDirsOnly
        )
        
        if new_folder:
            try:
                # Сохранить в .env
                env_path = str(get_env_path())
                set_key(env_path, "RECORDINGS_PATH", new_folder)
                
                # Обновить label
                self.recordings_path_label.setText(f"📁 <a href='file:///{new_folder}'>{new_folder}</a>")
                
                # Обновить список записей
                self._refresh_recordings_list()
                
                logger.info(f"Папка записей изменена на: {new_folder}")
                
                QMessageBox.information(
                    self,
                    "✅ Успешно",
                    f"Папка для записей изменена на:\n{new_folder}\n\nНовые записи будут сохраняться в:\n• {new_folder}/audio/\n• {new_folder}/transcriptions/",
                    QMessageBox.StandardButton.Ok
                )
            except Exception as e:
                logger.error(f"Не удалось изменить папку: {e}")
                QMessageBox.critical(
                    self,
                    "❌ Ошибка",
                    f"Не удалось изменить папку:\n{str(e)}",
                    QMessageBox.StandardButton.Ok
                )
    
    def _reset_recordings_folder(self):
        """Сбрасывает папку записей на значение по умолчанию."""
        from core.config import get_env_path, get_config_dir
        from dotenv import set_key
        
        # Подтверждение
        reply = QMessageBox.question(
            self,
            "🔄 Сбросить папку?",
            "Вы уверены что хотите вернуть папку записей по умолчанию?\n\n"
            "Новые записи будут сохраняться в:\n"
            f"{get_config_dir() / 'recordings'}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Удалить RECORDINGS_PATH из .env (установить пустое значение)
                env_path = str(get_env_path())
                set_key(env_path, "RECORDINGS_PATH", "")
                
                # Получить папку по умолчанию
                default_dir = get_config_dir() / 'recordings'
                
                # Обновить label
                self.recordings_path_label.setText(f"📁 <a href='file:///{default_dir}'>{default_dir}</a>")
                
                # Обновить список записей
                self._refresh_recordings_list()
                
                logger.info("Папка записей сброшена на значение по умолчанию")
                
                QMessageBox.information(
                    self,
                    "✅ Успешно",
                    f"Папка записей сброшена на значение по умолчанию:\n{default_dir}",
                    QMessageBox.StandardButton.Ok
                )
            except Exception as e:
                logger.error(f"Не удалось сбросить папку: {e}")
                QMessageBox.critical(
                    self,
                    "❌ Ошибка",
                    f"Не удалось сбросить папку:\n{str(e)}",
                    QMessageBox.StandardButton.Ok
                )
    
    def _create_about_page(self) -> QWidget:
        """Создает страницу О программе."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("О программе")
        title.setObjectName("pageTitle")  # Применить стиль
        layout.addWidget(title)
        
        # Информация о программе
        info_group = QGroupBox("RapidWhisper")
        info_layout = QVBoxLayout()
        info_layout.setSpacing(16)
        
        # Версия
        version_label = QLabel("<b>Версия:</b> 1.3.0")
        version_label.setStyleSheet("font-size: 13px;")
        info_layout.addWidget(version_label)
        
        # Описание
        desc_label = QLabel(
            "Быстрая транскрипция речи с микрофона<br>"
            "используя AI API (Groq, OpenAI, GLM, Custom)"
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #888888; font-size: 12px;")
        info_layout.addWidget(desc_label)
        
        # Ссылки (из конфигурации)
        github_url = self.config.github_url
        docs_url = self.config.docs_url
        
        links_label = QLabel(
            f"<b>Ссылки:</b><br>"
            f"• GitHub: <a href='{github_url}'>{github_url}</a><br>"
            f"• Документация: <a href='{docs_url}'>docs/</a><br>"
            f"• Поддержка: <a href='{github_url}/issues'>Создать issue</a>"
        )
        links_label.setWordWrap(True)
        links_label.setOpenExternalLinks(True)
        links_label.setStyleSheet("font-size: 12px;")
        info_layout.addWidget(links_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Используемые библиотеки
        libs_group = QGroupBox("Используемые библиотеки")
        libs_layout = QVBoxLayout()
        libs_layout.setSpacing(12)
        
        libs_label = QLabel(
            "<b>Основные:</b><br>"
            "• <a href='https://www.riverbankcomputing.com/software/pyqt/'>PyQt6</a> - GUI фреймворк<br>"
            "• <a href='https://github.com/openai/openai-python'>OpenAI Python SDK</a> - API клиент<br>"
            "• <a href='https://people.csail.mit.edu/hubert/pyaudio/'>PyAudio</a> - Запись аудио<br>"
            "• <a href='https://numpy.org/'>NumPy</a> - Обработка аудио<br>"
            "• <a href='https://github.com/boppreh/keyboard'>Keyboard</a> - Горячие клавиши<br>"
            "• <a href='https://github.com/asweigart/pyperclip'>Pyperclip</a> - Буфер обмена<br>"
            "• <a href='https://github.com/giampaolo/psutil'>Psutil</a> - Управление процессами<br>"
            "• <a href='https://github.com/theskumar/python-dotenv'>Python-dotenv</a> - Конфигурация<br><br>"
            "<b>Тестирование:</b><br>"
            "• <a href='https://pytest.org/'>Pytest</a> - Фреймворк тестирования<br>"
            "• <a href='https://hypothesis.readthedocs.io/'>Hypothesis</a> - Property-based testing"
        )
        libs_label.setWordWrap(True)
        libs_label.setOpenExternalLinks(True)
        libs_label.setStyleSheet("color: #888888; font-size: 11px;")
        libs_layout.addWidget(libs_label)
        
        libs_group.setLayout(libs_layout)
        layout.addWidget(libs_group)
        
        # Поддерживаемые провайдеры
        providers_group = QGroupBox("Поддерживаемые AI провайдеры")
        providers_layout = QVBoxLayout()
        providers_layout.setSpacing(12)
        
        providers_label = QLabel(
            "<b>Облачные:</b><br>"
            "• <a href='https://console.groq.com'>Groq</a> - Бесплатный и быстрый (рекомендуется)<br>"
            "• <a href='https://openai.com'>OpenAI</a> - Официальный Whisper API<br>"
            "• <a href='https://open.bigmodel.cn'>GLM (Zhipu AI)</a> - Поддержка китайского<br><br>"
            "<b>Локальные (Custom):</b><br>"
            "• <a href='https://lmstudio.ai'>LM Studio</a> - Простой запуск локальных моделей<br>"
            "• <a href='https://ollama.ai'>Ollama</a> - CLI для локальных моделей<br>"
            "• <a href='https://github.com/vllm-project/vllm'>vLLM</a> - Высокопроизводительный inference<br>"
            "• <a href='https://localai.io'>LocalAI</a> - Локальная альтернатива OpenAI<br>"
            "• Любые OpenAI-совместимые API"
        )
        providers_label.setWordWrap(True)
        providers_label.setOpenExternalLinks(True)
        providers_label.setStyleSheet("color: #888888; font-size: 11px;")
        providers_layout.addWidget(providers_label)
        
        providers_group.setLayout(providers_layout)
        layout.addWidget(providers_group)
        
        # Лицензия
        license_group = QGroupBox("Лицензия")
        license_layout = QVBoxLayout()
        
        license_label = QLabel("© 2026 RapidWhisper. Все права защищены.")
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
        
        # Установить промпт
        self.post_processing_prompt_edit.setPlainText(self.config.post_processing_prompt)
        
        # Обновить состояние полей
        self._on_post_processing_toggled(self.config.enable_post_processing)
        
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
        
        # Если не найдено, выбрать русский по умолчанию (индекс 7)
        if not found:
            default_button = self.language_button_group.button(7)  # RU
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
        
        # Показать/скрыть дополнительные поля
        if hasattr(self, 'glm_coding_plan_check'):
            self.glm_coding_plan_check.setVisible(provider == "glm")
        if hasattr(self, 'llm_base_url_edit'):
            self.llm_base_url_edit.setVisible(provider == "llm")
            self.llm_base_url_label.setVisible(provider == "llm")
        if hasattr(self, 'llm_api_key_edit'):
            self.llm_api_key_edit.setVisible(provider == "llm")
            self.llm_api_key_label.setVisible(provider == "llm")
    
    def _save_settings(self):
        """Сохраняет настройки в .env файл."""
        try:
            from core.config import get_env_path
            
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
            
            new_config = {
                "AI_PROVIDER": self.provider_combo.currentText(),
                "GROQ_API_KEY": self.groq_key_edit.text(),
                "OPENAI_API_KEY": self.openai_key_edit.text(),
                "GLM_API_KEY": self.glm_key_edit.text(),
                "CUSTOM_API_KEY": self.custom_key_edit.text(),
                "CUSTOM_BASE_URL": self.custom_url_edit.text(),
                "CUSTOM_MODEL": self.custom_model_edit.text(),
                "HOTKEY": self.hotkey_edit.text(),
                "SILENCE_THRESHOLD": str(self.silence_threshold_spin.value()),
                "SILENCE_DURATION": str(self.silence_duration_spin.value()),
                "MANUAL_STOP": "true" if self.manual_stop_check.isChecked() else "false",
                "AUTO_HIDE_DELAY": str(self.auto_hide_spin.value()),
                "SAMPLE_RATE": self.sample_rate_combo.currentText(),
                "CHUNK_SIZE": self.chunk_size_combo.currentText(),
                "SILENCE_PADDING": str(int(self.silence_padding_spin.value())),
                "REMEMBER_WINDOW_POSITION": "true" if self.remember_position_check.isChecked() else "false",
                "WINDOW_POSITION_PRESET": position_presets[position_index],
                "KEEP_RECORDINGS": "true" if self.keep_recordings_check.isChecked() else "false",
                "ENABLE_POST_PROCESSING": "true" if self.enable_post_processing_check.isChecked() else "false",
                "POST_PROCESSING_PROVIDER": self.post_processing_provider_combo.currentText(),
                "POST_PROCESSING_MODEL": self.post_processing_model_combo.currentText(),
                "POST_PROCESSING_PROMPT": self.post_processing_prompt_edit.toPlainText(),
                "GLM_USE_CODING_PLAN": "true" if self.glm_coding_plan_check.isChecked() else "false",
                "LLM_BASE_URL": self.llm_base_url_edit.text(),
                "LLM_API_KEY": self.llm_api_key_edit.text(),
                "INTERFACE_LANGUAGE": selected_language,
            }
            
            # Использовать правильный путь к .env (AppData для production)
            env_path = str(get_env_path())
            env_lines = []
            
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    env_lines = f.readlines()
            
            # Обновить значения
            updated_keys = set()
            for i, line in enumerate(env_lines):
                line_stripped = line.strip()
                if line_stripped and not line_stripped.startswith('#'):
                    key = line_stripped.split('=')[0].strip()
                    if key in new_config:
                        env_lines[i] = f"{key}={new_config[key]}\n"
                        updated_keys.add(key)
            
            # Добавить новые ключи если их не было
            for key, value in new_config.items():
                if key not in updated_keys:
                    env_lines.append(f"{key}={value}\n")
            
            # Сохранить обратно в файл
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(env_lines)
            
            logger.info(f"Настройки сохранены в {env_path}")
            
            # Показать сообщение
            QMessageBox.information(
                self,
                "✅ Успешно",
                "Настройки сохранены и применены!\n\n"
                "Новые настройки вступили в силу.",
                QMessageBox.StandardButton.Ok
            )
            
            # Испустить сигнал
            self.settings_saved.emit()
            
            # Закрыть окно
            self.accept()
            
        except Exception as e:
            logger.error(f"Ошибка сохранения настроек: {e}")
            QMessageBox.critical(
                self,
                "❌ Ошибка",
                f"Не удалось сохранить настройки:\n{str(e)}",
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
