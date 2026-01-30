"""
Окно настроек приложения RapidWhisper.

Предоставляет графический интерфейс для редактирования всех параметров
конфигурации из .env файла в стиле macOS с боковой панелью.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QDoubleSpinBox,
    QPushButton, QGroupBox, QMessageBox, QWidget, QListWidget, QStackedWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from core.config import Config
from utils.logger import get_logger
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
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Применить стиль
        self._apply_style()
        
        # Создать интерфейс
        self._create_ui()
        
        # Загрузить текущие значения
        self._load_values()
    
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
                margin-top: 16px;
                font-weight: bold;
                padding-top: 16px;
                background-color: #252525;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 6px 12px;
                background-color: transparent;
                color: #888888;
                font-size: 11px;
                font-weight: normal;
                text-transform: uppercase;
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
        
        # Добавить пункты меню
        items = [
            ("🤖 AI Provider", "ai"),
            ("⚡ Приложение", "app"),
            ("🎤 Аудио", "audio"),
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
        
        # Создать страницы
        self.content_stack.addWidget(self._create_ai_page())
        self.content_stack.addWidget(self._create_app_page())
        self.content_stack.addWidget(self._create_audio_page())
        self.content_stack.addWidget(self._create_about_page())
        
        right_panel_layout.addWidget(self.content_stack)
        
        # Кнопки внизу
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Сохранить")
        save_btn.clicked.connect(self._save_settings)
        buttons_layout.addWidget(save_btn)
        
        right_panel_layout.addLayout(buttons_layout)
        
        right_panel.setLayout(right_panel_layout)
        main_layout.addWidget(right_panel, 1)
        
        self.setLayout(main_layout)
    
    def _on_sidebar_changed(self, index: int):
        """Обработчик переключения пунктов в боковой панели."""
        self.content_stack.setCurrentIndex(index)
    
    def _create_ai_page(self) -> QWidget:
        """Создает страницу настроек AI Provider."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("AI Provider")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Группа: Выбор провайдера
        provider_group = QGroupBox("Провайдер")
        provider_layout = QFormLayout()
        provider_layout.setSpacing(12)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["groq", "openai", "glm", "custom"])
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
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
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_app_page(self) -> QWidget:
        """Создает страницу настроек приложения."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("Приложение")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Группа: Горячие клавиши
        hotkey_group = QGroupBox("Горячие клавиши")
        hotkey_layout = QFormLayout()
        hotkey_layout.setSpacing(12)
        
        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setPlaceholderText("ctrl+space")
        hotkey_label = QLabel("Горячая клавиша:")
        hotkey_label.setToolTip("Например: F1, ctrl+space, ctrl+shift+r")
        hotkey_layout.addRow(hotkey_label, self.hotkey_edit)
        
        hotkey_group.setLayout(hotkey_layout)
        layout.addWidget(hotkey_group)
        
        # Группа: Определение тишины
        silence_group = QGroupBox("Определение тишины")
        silence_layout = QFormLayout()
        silence_layout.setSpacing(12)
        
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
        
        silence_group.setLayout(silence_layout)
        layout.addWidget(silence_group)
        
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
        
        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)
        
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
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Группа: Параметры записи
        audio_group = QGroupBox("Параметры записи")
        audio_layout = QFormLayout()
        audio_layout.setSpacing(12)
        
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["16000", "44100", "48000"])
        rate_label = QLabel("Частота дискретизации:")
        rate_label.setToolTip("Гц. 16000 рекомендуется для речи")
        audio_layout.addRow(rate_label, self.sample_rate_combo)
        
        self.chunk_size_combo = QComboBox()
        self.chunk_size_combo.addItems(["256", "512", "1024", "2048", "4096"])
        chunk_label = QLabel("Размер чанка:")
        chunk_label.setToolTip("Фреймов. 1024 - оптимальное значение")
        audio_layout.addRow(chunk_label, self.chunk_size_combo)
        
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)
        
        # Информация
        info_label = QLabel(
            "⚠️ Внимание: Изменение параметров аудио может повлиять на качество записи.\n"
            "Рекомендуется оставить значения по умолчанию."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #ff8800; font-size: 11px; padding: 8px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_about_page(self) -> QWidget:
        """Создает страницу О программе."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Заголовок
        title = QLabel("О программе")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
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
        
        layout.addStretch()
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
        self.auto_hide_spin.setValue(self.config.auto_hide_delay)
        
        # Аудио
        self.sample_rate_combo.setCurrentText(str(self.config.sample_rate))
        self.chunk_size_combo.setCurrentText(str(self.config.chunk_size))
        
        # Обновить подсветку активного провайдера
        self._on_provider_changed(self.config.ai_provider)
    
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
    
    def _save_settings(self):
        """Сохраняет настройки в .env файл."""
        try:
            from core.config import get_env_path
            
            # Получить новые значения
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
                "AUTO_HIDE_DELAY": str(self.auto_hide_spin.value()),
                "SAMPLE_RATE": self.sample_rate_combo.currentText(),
                "CHUNK_SIZE": self.chunk_size_combo.currentText(),
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
