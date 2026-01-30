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
        
        # Загрузить кастомную иконку
        import sys
        import os
        
        # Определить путь к иконке (работает и в dev, и в .exe)
        if getattr(sys, 'frozen', False):
            # Запущено из .exe
            base_path = sys._MEIPASS
        else:
            # Запущено из исходников
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        icon_path = os.path.join(base_path, 'public', 'RapidWhisper.ico')
        
        try:
            icon = QIcon(icon_path)
            if not icon.isNull():
                self.tray_icon.setIcon(icon)
            else:
                # Fallback на стандартную иконку
                from PyQt6.QtWidgets import QStyle, QApplication
                icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
                self.tray_icon.setIcon(icon)
        except Exception:
            # Fallback на стандартную иконку
            from PyQt6.QtWidgets import QStyle, QApplication
            icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            self.tray_icon.setIcon(icon)
        
        # Создать меню
        self._create_menu()
        
        # Подключить клик на иконку для открытия настроек
        self.tray_icon.activated.connect(self._on_tray_icon_activated)
        
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
    
    def _on_tray_icon_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """
        Обработчик клика на иконку трея.
        
        Args:
            reason: Причина активации (клик, двойной клик и т.д.)
        """
        # Открыть настройки при одинарном клике левой кнопкой
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_settings.emit()
    
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
        from PyQt6.QtWidgets import QMessageBox, QApplication
        import sys
        
        # Создаем окно БЕЗ parent, чтобы оно центрировалось на экране
        msg = QMessageBox()
        msg.setWindowTitle("О программе RapidWhisper")
        msg.setIcon(QMessageBox.Icon.Information)
        
        # Установить иконку окна
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            import os
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        icon_path = os.path.join(base_path, 'public', 'RapidWhisper.ico')
        try:
            icon = QIcon(icon_path)
            if not icon.isNull():
                msg.setWindowIcon(icon)
        except Exception:
            pass
        
        msg.setText(
            "RapidWhisper v1.0\n\n"
            "Быстрая транскрипция речи с микрофона\n"
            "используя AI API (Groq, OpenAI, GLM).\n\n"
            "Горячая клавиша: Ctrl+Space\n"
            "Отмена записи: ESC\n\n"
            "© 2026 RapidWhisper"
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # Центрируем окно на экране
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            msg_size = msg.sizeHint()
            x = screen_geometry.center().x() - msg_size.width() // 2
            y = screen_geometry.center().y() - msg_size.height() // 2
            msg.move(x, y)
        
        msg.exec()
    
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
