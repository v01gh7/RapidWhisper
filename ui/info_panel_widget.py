"""
Виджет информационной панели для отображения активного приложения и горячих клавиш.

Этот модуль предоставляет InfoPanelWidget - UI компонент для отображения
информации об активном приложении и доступных горячих клавишах в нижней
части плавающего окна RapidWhisper.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QFrame, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QCursor
from typing import Optional, List
from utils.i18n import t
from design_system.window_themes import DEFAULT_WINDOW_THEME_ID, get_window_theme


class InfoPanelWidget(QWidget):
    """
    Панель информации об активном приложении и горячих клавишах.
    
    Отображает иконку и название активного приложения слева,
    и горячие клавиши справа. Панель имеет темный фон и
    гармонично вписывается в дизайн плавающего окна.
    
    Requirements: 1.1, 1.3, 1.4, 3.1, 3.2, 3.3, 5.1-5.8, 6.1-6.5
    """

    _KEYCAP_LABELS = {
        "ctrl": "CTRL",
        "control": "CTRL",
        "alt": "ALT",
        "shift": "SHIFT",
        "space": "SPACE",
        "esc": "ESC",
        "escape": "ESC",
        "enter": "ENTER",
        "tab": "TAB",
    }
    
    # Сигналы для кликов по кнопкам
    cancel_clicked = pyqtSignal()  # Сигнал при клике на "Отменить"
    record_clicked = pyqtSignal()  # Сигнал при клике на "Запись"
    
    def __init__(self, config, parent=None):
        """
        Инициализирует панель информации.
        
        Args:
            config: Объект конфигурации для доступа к настройкам горячих клавиш
            parent: Родительский виджет
        """
        super().__init__(parent)
        self._config = config
        self._theme_id = getattr(config, "window_theme", DEFAULT_WINDOW_THEME_ID)
        self._theme = get_window_theme(self._theme_id)
        self._default_icon: Optional[QPixmap] = None
        self._create_default_icon()
        self._setup_ui()
        self._apply_styles()
    
    def _create_default_icon(self) -> None:
        """
        Создать иконку по умолчанию.
        
        Создает простую серую иконку для отображения когда
        иконка приложения недоступна.
        """
        from PyQt6.QtGui import QPainter, QColor
        
        # Создать серую иконку 20x20
        icon = QPixmap(30, 30)
        icon.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(icon)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Нарисовать серый квадрат с закругленными углами (по центру)
        painter.setBrush(QColor("#555555"))
        painter.setPen(Qt.PenStyle.NoPen)
        square_size = 16
        square_offset = (icon.width() - square_size) // 2
        painter.drawRoundedRect(square_offset, square_offset, square_size, square_size, 4, 4)
        
        painter.end()
        
        self._default_icon = icon
    
    def _setup_ui(self) -> None:
        """
        Настроить UI компоненты.
        
        Создает layout с иконкой и названием приложения слева,
        и кнопками горячих клавиш справа.
        
        Requirements: 5.3, 5.4, 6.1, 6.2, 6.3, 6.4, 6.5
        """
        # Получить размер шрифта из конфигурации
        font_size = self._config.font_size_floating_info if self._config else 11
        sub_font_size = max(8, font_size - 2)
        self._hotkey_font_size = max(9, font_size - 1)
        
        # Главный layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 6, 0, 6)
        main_layout.setSpacing(8)
        
        # Левая часть: иконка + название приложения + подпись
        left_container = QWidget(self)
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        self._app_icon_label = QLabel()
        self._app_icon_label.setObjectName("appIcon")
        self._app_icon_label.setFixedSize(30, 30)
        self._app_icon_label.setScaledContents(False)
        self._app_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        text_container = QWidget(self)
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(0)
        
        self._app_name_label = QLabel(t("common.no_active_window"))
        self._app_name_label.setObjectName("appName")
        self._app_name_label.setFont(QFont(self._theme["font_family"], font_size))
        self._app_name_label.setMaximumWidth(245)  # Ограничить максимальную ширину (минус 15px)
        
        self._app_sub_label = QLabel(t("common.active_application"))
        self._app_sub_label.setObjectName("appSub")
        self._app_sub_label.setFont(QFont(self._theme["font_family"], sub_font_size))
        
        text_layout.addWidget(self._app_name_label)
        text_layout.addWidget(self._app_sub_label)
        
        left_layout.addWidget(self._app_icon_label)
        left_layout.addWidget(text_container)
        main_layout.addWidget(left_container)
        
        # Добавить stretch между левой и правой частями
        main_layout.addStretch()
        
        # Правая часть: горячие клавиши в виде чипов и keycap
        right_container = QWidget(self)
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)
        
        # Чип "Запись"
        self._record_chip = QLabel(self._chip_text(t("common.record")))
        self._record_chip.setObjectName("recordChip")
        self._record_chip.setFont(QFont(self._theme["font_family"], font_size))
        self._record_chip.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._record_chip.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self._record_chip.setMouseTracking(True)
        self._record_chip.mousePressEvent = self._on_record_clicked
        
        # Контейнер с клавишами записи
        self._record_keys_container = QWidget(self)
        self._record_keys_layout = QHBoxLayout(self._record_keys_container)
        self._record_keys_layout.setContentsMargins(0, 0, 0, 0)
        self._record_keys_layout.setSpacing(3)
        self._update_record_hotkey()
        
        # Разделитель
        divider = QFrame(self)
        divider.setObjectName("hotkeyDivider")
        divider.setFixedWidth(1)
        divider.setFixedHeight(16)
        
        # Чип "Отменить"
        self._cancel_chip = QLabel(self._chip_text(t("common.cancel_action")))
        self._cancel_chip.setObjectName("cancelChip")
        self._cancel_chip.setFont(QFont(self._theme["font_family"], font_size))
        self._cancel_chip.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._cancel_chip.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self._cancel_chip.setMouseTracking(True)
        self._cancel_chip.mousePressEvent = self._on_cancel_clicked
        
        # Клавиша Esc
        self._cancel_key_label = self._create_keycap_label("ESC")
        
        right_layout.addWidget(self._record_chip)
        right_layout.addWidget(self._record_keys_container)
        right_layout.addWidget(divider)
        right_layout.addWidget(self._cancel_chip)
        right_layout.addWidget(self._cancel_key_label)
        
        main_layout.addWidget(right_container)
        
        # Адаптивная высота (до 200px)
        self.setMaximumHeight(200)
        # Растягиваться по ширине контейнера, высота по содержимому
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    
    def _apply_styles(self) -> None:
        """
        Применить стили к компонентам.
        
        Устанавливает темный фон, границы и цвета текста
        согласно дизайн-спецификации.
        
        Requirements: 5.1, 5.2, 5.6, 5.7, 5.8
        """
        theme = self._theme
        self.setStyleSheet("""
            InfoPanelWidget {
                background-color: %s;
                border-top: 1px solid %s;
            }
            QLabel#appName {
                color: %s;
                font-weight: 600;
            }
            QLabel#appSub {
                color: %s;
            }
            QLabel#appIcon {
                background-color: %s;
                border: 1px solid %s;
                border-radius: 5px;
                padding: 2px;
            }
            QLabel#recordChip {
                background-color: %s;
                border: 1px solid %s;
                color: %s;
                border-radius: 9px;
                padding: 1px 6px;
                min-height: 22px;
                max-height: 22px;
                letter-spacing: 0px;
            }
            QLabel#recordChip:hover {
                background-color: %s;
                border: 1px solid %s;
                color: %s;
            }
            QLabel#recordChip[active="true"] {
                background-color: %s;
                border: 1px solid %s;
                color: %s;
            }
            QLabel#recordChip[active="true"]:hover {
                background-color: %s;
                border: 1px solid %s;
                color: %s;
            }
            QLabel#cancelChip {
                background-color: %s;
                border: 1px solid %s;
                color: %s;
                border-radius: 9px;
                padding: 1px 6px;
                min-height: 22px;
                max-height: 22px;
                letter-spacing: 0px;
            }
            QLabel#cancelChip:hover {
                background-color: %s;
                border: 1px solid %s;
                color: %s;
            }
            QLabel#cancelChip[active="true"] {
                background-color: %s;
                border: 1px solid %s;
                color: %s;
            }
            QLabel#cancelChip[active="true"]:hover {
                background-color: %s;
                border: 1px solid %s;
                color: %s;
            }
            QLabel[role="keycap"] {
                border: 1px solid %s;
                background: %s;
                border-radius: 6px;
                padding: 1px 5px;
                min-height: 22px;
                max-height: 22px;
                color: %s;
            }
            QFrame#hotkeyDivider {
                background-color: %s;
            }
        """ % (
            theme["panel_bg"],
            theme["panel_border_top"],
            theme["panel_app_name"],
            theme["panel_app_sub"],
            theme["panel_app_icon_bg"],
            theme["panel_app_icon_border"],
            theme["panel_record_bg"],
            theme["panel_record_border"],
            theme["panel_record_text"],
            theme["panel_record_bg_hover"],
            theme["panel_record_border_hover"],
            theme["panel_record_text_hover"],
            theme["panel_record_bg_active"],
            theme["panel_record_border_active"],
            theme["panel_record_text_active"],
            theme["panel_record_bg_hover"],
            theme["panel_record_border_hover"],
            theme["panel_record_text_hover"],
            theme["panel_cancel_bg"],
            theme["panel_cancel_border"],
            theme["panel_cancel_text"],
            theme["panel_cancel_bg_hover"],
            theme["panel_cancel_border_hover"],
            theme["panel_cancel_text_hover"],
            theme["panel_cancel_bg_active"],
            theme["panel_cancel_border_active"],
            theme["panel_cancel_text_active"],
            theme["panel_cancel_bg_hover"],
            theme["panel_cancel_border_hover"],
            theme["panel_cancel_text_hover"],
            theme["panel_keycap_border"],
            theme["panel_keycap_bg"],
            theme["panel_keycap_text"],
            theme["panel_divider"],
        ))

    def _apply_theme_fonts(self) -> None:
        """Applies current theme font family to panel labels."""
        font_size = self._config.font_size_floating_info if self._config else 11
        sub_font_size = max(8, font_size - 2)
        self._hotkey_font_size = max(9, font_size - 1)
        self._app_name_label.setFont(QFont(self._theme["font_family"], font_size))
        self._app_sub_label.setFont(QFont(self._theme["font_family"], sub_font_size))
        self._record_chip.setFont(QFont(self._theme["font_family"], font_size))
        self._cancel_chip.setFont(QFont(self._theme["font_family"], font_size))
        for label in self.findChildren(QLabel):
            if label.property("role") == "keycap":
                label.setFont(QFont(self._theme["font_family"], self._hotkey_font_size))

    def set_theme(self, theme_id: str) -> None:
        """Switches panel colors to a predefined theme."""
        self._theme_id = theme_id or DEFAULT_WINDOW_THEME_ID
        self._theme = get_window_theme(self._theme_id)
        self._apply_theme_fonts()
        self._apply_styles()

    def _chip_text(self, text: str) -> str:
        """Возвращает текст для чипа в верхнем регистре."""
        return text.upper() if text else ""

    def _format_hotkey_parts(self, hotkey: str) -> List[str]:
        """Разбивает горячую клавишу на части для keycap."""
        if not hotkey:
            return []
        parts = [part.strip().lower() for part in hotkey.split("+") if part.strip()]
        labels: List[str] = []
        for part in parts:
            labels.append(self._KEYCAP_LABELS.get(part, part.upper()))
        return labels

    def _create_keycap_label(self, text: str) -> QLabel:
        """Создает label-ключ в стиле keycap."""
        label = QLabel(text)
        label.setProperty("role", "keycap")
        label.setFont(QFont(self._theme["font_family"], getattr(self, "_hotkey_font_size", 11)))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _set_keycaps(self, layout: QHBoxLayout, keys: List[str]) -> None:
        """Обновляет набор keycap-лейблов в контейнере."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        for key in keys:
            layout.addWidget(self._create_keycap_label(key))
    
    def _update_record_hotkey(self) -> None:
        """
        Обновить отображение горячей клавиши записи.
        
        Читает горячую клавишу из конфигурации и форматирует
        её для отображения.
        
        Requirements: 3.2, 4.1-4.6
        """
        hotkey = self._config.hotkey if self._config else ""
        keys = self._format_hotkey_parts(hotkey)
        self._set_keycaps(self._record_keys_layout, keys)
    
    @pyqtSlot(object)
    def update_app_info(self, window_info) -> None:
        """
        Обновить информацию об активном приложении.
        
        Обновляет иконку и название приложения на основе
        переданной информации об окне. Усекает длинные названия
        и масштабирует иконки.
        
        Args:
            window_info: WindowInfo объект с информацией об окне
        
        Requirements: 1.1, 1.2, 1.3, 1.4, 5.5
        """
        if not window_info:
            self._app_name_label.setText(t("common.no_active_window"))
            self._app_icon_label.clear()
            return
        
        # Обновить название (с усечением)
        title = window_info.title
        if len(title) > 30:
            title = title[:27] + "..."
        self._app_name_label.setText(title)
        
        # Обновить иконку
        if window_info.icon:
            # Масштабировать иконку до 20x20
            scaled_icon = window_info.icon.scaled(
                25, 25,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self._app_icon_label.setPixmap(scaled_icon)
        else:
            # Использовать иконку по умолчанию
            if self._default_icon:
                self._app_icon_label.setPixmap(self._default_icon)
            else:
                self._app_icon_label.clear()
    
    def update_hotkey_display(self) -> None:
        """
        Обновить отображение горячей клавиши.
        
        Вызывается при изменении конфигурации для обновления
        отображаемой горячей клавиши.
        
        Requirements: 3.4
        """
        self._update_record_hotkey()
    
    def reload_translations(self) -> None:
        """
        Перезагружает все переводы в панели.
        
        Вызывается при смене языка интерфейса для обновления
        всех текстовых элементов.
        """
        # Обновить чипы и горячие клавиши
        self._record_chip.setText(self._chip_text(t("common.record")))
        self._cancel_chip.setText(self._chip_text(t("common.cancel_action")))
        self._update_record_hotkey()
        
        # Обновить подпись
        self._app_sub_label.setText(t("common.active_application"))
        
        # Обновить текст "Нет активного окна" если он отображается
        if not self._app_name_label.text() or self._app_name_label.text() in ["No active window", "Нет активного окна"]:
            self._app_name_label.setText(t("common.no_active_window"))
    
    def set_default_icon(self, icon: QPixmap) -> None:
        """
        Установить иконку по умолчанию для неизвестных приложений.
        
        Args:
            icon: QPixmap с иконкой по умолчанию
        
        Requirements: 1.3
        """
        self._default_icon = icon
    
    def _on_record_clicked(self, event) -> None:
        """
        Обработчик клика по кнопке "Запись".

        Отправляет сигнал record_clicked для остановки записи.
        """
        self.record_clicked.emit()
    
    def _on_cancel_clicked(self, event) -> None:
        """
        Обработчик клика по кнопке "Отменить".
        
        Отправляет сигнал cancel_clicked для отмены записи.
        """
        self.cancel_clicked.emit()
    
    def set_active_button(self, button_name: str) -> None:
        """
        Устанавливает активную кнопку (подчеркивает её и делает некликабельной).
        
        Args:
            button_name: Название кнопки ("record" или "cancel" или None для сброса)
        """
        # Сбросить активные состояния
        self._record_chip.setProperty("active", False)
        self._cancel_chip.setProperty("active", False)
        
        # Установить активную кнопку
        if button_name == "record":
            self._record_chip.setProperty("active", True)
        elif button_name == "cancel":
            self._cancel_chip.setProperty("active", True)
        
        # Переприменить стиль
        for widget in (self._record_chip, self._cancel_chip):
            widget.style().unpolish(widget)
            widget.style().polish(widget)
