"""
Простой тест для проверки видимости окна настроек.
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
    
    # Создать окно настроек
    logger.info("Creating settings window...")
    window = SettingsWindow(config)
    
    # Показать окно
    logger.info("Showing settings window...")
    window.show()
    window.raise_()
    window.activateWindow()
    window.repaint()
    window.update()
    
    # Вывести информацию об окне
    logger.info(f"Window visible: {window.isVisible()}")
    logger.info(f"Window size: {window.size()}")
    logger.info(f"Window position: {window.pos()}")
    logger.info(f"Window flags: {window.windowFlags()}")
    logger.info(f"Window opacity: {window.windowOpacity()}")
    from PyQt6.QtCore import Qt
    logger.info(f"WA_TranslucentBackground: {window.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)}")
    logger.info(f"Stylesheet length: {len(window.styleSheet())}")
    logger.info(f"Stylesheet preview: {window.styleSheet()[:500]}")
    
    # Закрыть через 5 секунд
    QTimer.singleShot(5000, app.quit)
    
    logger.info("Window should be visible now. Waiting 5 seconds...")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
