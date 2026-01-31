"""
Визуальный тест окна настроек с новыми иконками и стилями сайдбара.
"""

import sys
from PyQt6.QtWidgets import QApplication
from core.config import Config
from ui.settings_window import SettingsWindow

def main():
    app = QApplication(sys.argv)
    
    # Создать конфигурацию
    config = Config()
    
    # Создать окно настроек
    window = SettingsWindow(config)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
