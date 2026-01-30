"""
Виджет информационной панели для отображения активного приложения и горячих клавиш.

Этот модуль предоставляет InfoPanelWidget - UI компонент для отображения
информации об активном приложении и доступных горячих клавишах в нижней
части плавающего окна RapidWhisper.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QPixmap, QFont
from typing import Optional
from utils.hotkey_formatter import HotkeyFormatter
from utils.i18n import t


class InfoPanelWidget(QWidget):
    """
    Панель информации об активном приложении и горячих клавишах.
    
    Отображает иконку и название активного приложения слева,
    и горячие клавиши справа. Панель имеет темный фон и
    гармонично вписывается в дизайн плавающего окна.
    
    Requirements: 1.1, 1.3, 1.4, 3.1, 3.2, 3.3, 5.1-5.8, 6.1-6.5
    """
    
    def __init__(self, config, parent=None):
        """
        Инициализирует панель информации.
        
        Args:
            config: Объект конфигурации для доступа к настройкам горячих клавиш
            parent: Родительский виджет
        """
        super().__init__(parent)
        self._config = config
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
        icon = QPixmap(20, 20)
        icon.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(icon)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Нарисовать серый квадрат с закругленными углами
        painter.setBrush(QColor("#555555"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(2, 2, 16, 16, 3, 3)
        
        painter.end()
        
        self._default_icon = icon
    
    def _setup_ui(self) -> None:
        """
        Настроить UI компоненты.
        
        Создает layout с иконкой и названием приложения слева,
        и кнопками горячих клавиш справа.
        
        Requirements: 5.3, 5.4, 6.1, 6.2, 6.3, 6.4, 6.5
        """
        # Главный layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 6, 8, 6)
        main_layout.setSpacing(8)  # Увеличиваем spacing между элементами
        
        # Левая часть: иконка + название приложения
        self._app_icon_label = QLabel()
        self._app_icon_label.setFixedSize(20, 20)
        self._app_icon_label.setScaledContents(True)
        
        self._app_name_label = QLabel(t("common.no_active_window"))
        self._app_name_label.setFont(QFont("Segoe UI", 11))
        self._app_name_label.setMaximumWidth(300)  # Ограничить максимальную ширину
        
        main_layout.addWidget(self._app_icon_label)
        main_layout.addWidget(self._app_name_label)
        
        # Добавить stretch между левой и правой частями
        main_layout.addStretch()
        
        # Правая часть: горячие клавиши
        # Кнопка записи
        self._record_hotkey_label = QLabel()
        self._record_hotkey_label.setFont(QFont("Segoe UI", 11))
        self._update_record_hotkey()
        
        # Кнопка отмены
        self._close_hotkey_label = QLabel(t("common.cancel_esc"))
        self._close_hotkey_label.setFont(QFont("Segoe UI", 11))
        
        main_layout.addWidget(self._record_hotkey_label)
        main_layout.addWidget(self._close_hotkey_label)
        
        # Установить фиксированную высоту
        self.setFixedHeight(40)
    
    def _apply_styles(self) -> None:
        """
        Применить стили к компонентам.
        
        Устанавливает темный фон, границы и цвета текста
        согласно дизайн-спецификации.
        
        Requirements: 5.1, 5.2, 5.6, 5.7, 5.8
        """
        # Стиль панели
        self.setStyleSheet("""
            InfoPanelWidget {
                background-color: #1a1a1a;
                border-top: 1px solid #333333;
            }
        """)
        
        # Стиль текста приложения
        self._app_name_label.setStyleSheet("color: #E0E0E0;")
        
        # Стиль горячих клавиш - белый цвет
        hotkey_style = "color: #FFFFFF;"
        self._record_hotkey_label.setStyleSheet(hotkey_style)
        self._close_hotkey_label.setStyleSheet(hotkey_style)
    
    def _update_record_hotkey(self) -> None:
        """
        Обновить отображение горячей клавиши записи.
        
        Читает горячую клавишу из конфигурации и форматирует
        её для отображения.
        
        Requirements: 3.2, 4.1-4.6
        """
        hotkey = self._config.hotkey
        formatted = HotkeyFormatter.format_hotkey(hotkey)
        self._record_hotkey_label.setText(f"{t('common.record')} {formatted}")
    
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
                20, 20,
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
        # Обновить текст кнопки записи
        self._update_record_hotkey()
        
        # Обновить текст кнопки отмены
        self._close_hotkey_label.setText(t("common.cancel_esc"))
        
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
