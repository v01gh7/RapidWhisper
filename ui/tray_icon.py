"""
Системный трей для RapidWhisper.

Предоставляет иконку в системном трее с меню для управления приложением.
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal


class TrayIcon(QObject):
    """
    Иконка в системном трее с меню.
    
    Signals:
        show_settings: Сигнал для открытия настроек
        quit_app: Сигнал для выхода из приложения
    """
    
    show_settings = pyqtSignal()
    quit_app = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        Инициализирует иконку трея.
        
        Args:
            parent: Родительский объект
        """
        super().__init__(parent)
        
        # Создать системный трей
        self.tray_icon = QSystemTrayIcon(parent)
        
        # Создать иконку (используем стандартную иконку Qt)
        # TODO: Заменить на кастомную иконку
        from PyQt6.QtWidgets import QStyle, QApplication
        icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        self.tray_icon.setIcon(icon)
        
        # Создать меню
        self._create_menu()
        
        # Показать иконку
        self.tray_icon.show()
        
        # Подсказка при наведении
        self.tray_icon.setToolTip("RapidWhisper - Готово! Нажмите Ctrl+Space для записи")
    
    def set_status(self, status: str) -> None:
        """
        Устанавливает статус в подсказке трея.
        
        Args:
            status: Текст статуса
        """
        self.tray_icon.setToolTip(f"RapidWhisper - {status}")
    
    def _create_menu(self) -> None:
        """Создает контекстное меню трея."""
        menu = QMenu()
        
        # Действие: Настройки
        settings_action = QAction("⚙️ Настройки", menu)
        settings_action.triggered.connect(self.show_settings.emit)
        menu.addAction(settings_action)
        
        # Разделитель
        menu.addSeparator()
        
        # Действие: О программе
        about_action = QAction("ℹ️ О программе", menu)
        about_action.triggered.connect(self._show_about)
        menu.addAction(about_action)
        
        # Разделитель
        menu.addSeparator()
        
        # Действие: Выход
        quit_action = QAction("❌ Выход", menu)
        quit_action.triggered.connect(self.quit_app.emit)
        menu.addAction(quit_action)
        
        # Установить меню
        self.tray_icon.setContextMenu(menu)
    
    def _show_about(self) -> None:
        """Показывает информацию о программе."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            None,
            "О программе RapidWhisper",
            "RapidWhisper v1.0\n\n"
            "Быстрая транскрипция речи с микрофона\n"
            "используя Zhipu GLM API.\n\n"
            "Горячая клавиша: Ctrl+Space\n\n"
            "© 2026 RapidWhisper"
        )
    
    def show_message(self, title: str, message: str, duration: int = 5000) -> None:
        """
        Показывает уведомление в трее.
        
        Args:
            title: Заголовок уведомления
            message: Текст уведомления
            duration: Длительность показа в миллисекундах (по умолчанию 5 секунд)
        """
        self.tray_icon.showMessage(
            title,
            message,
            QSystemTrayIcon.MessageIcon.Information,
            duration
        )
    
    def hide(self) -> None:
        """Скрывает иконку трея."""
        self.tray_icon.hide()
