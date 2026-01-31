"""
Тестовый скрипт для окна настроек.
"""

import sys
from PyQt6.QtWidgets import QApplication
from core.config import Config
from ui.settings_window import SettingsWindow


def main():
    """Запускает окно настроек для тестирования."""
    app = QApplication(sys.argv)
    
    # Загрузить текущую конфигурацию из config.jsonc
    config = Config.load_from_config()
    
    # Создать и показать окно настроек
    settings_window = SettingsWindow(config)
    settings_window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
