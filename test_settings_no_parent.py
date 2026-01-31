"""
Тест окна настроек без parent для проверки видимости.
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from core.config import Config
from ui.settings_window import SettingsWindow
from utils.logger import get_logger

logger = get_logger()

def main():
    app = QApplication(sys.argv)
    
    # Создать конфигурацию
    config = Config()
    
    # Создать окно настроек БЕЗ parent
    logger.info("Creating settings window without parent...")
    window = SettingsWindow(config, parent=None)
    
    # Центрировать и показать окно
    logger.info("Centering and showing settings window...")
    window.center_on_screen()
    window.show()
    window.raise_()
    window.activateWindow()
    
    # Вывести информацию об окне
    logger.info(f"Window visible: {window.isVisible()}")
    logger.info(f"Window size: {window.size()}")
    logger.info(f"Window position: {window.pos()}")
    logger.info(f"Window parent: {window.parent()}")
    
    # Закрыть через 10 секунд
    QTimer.singleShot(10000, app.quit)
    
    logger.info("Window should be visible now. Waiting 10 seconds...")
    logger.info("Try clicking on the window or moving it!")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
