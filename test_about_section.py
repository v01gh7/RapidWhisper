"""Тест для проверки раздела О программе"""
import sys
from PyQt6.QtWidgets import QApplication
from core.config import Config
from ui.settings_window import SettingsWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Загрузить конфигурацию из config.jsonc
    config = Config.load_from_config()
    
    print("=== Проверка конфигурации ===")
    print(f"GitHub URL: {config.github_url}")
    print(f"Docs URL: {config.docs_url}")
    print(f"AI Provider: {config.ai_provider}")
    print(f"Has API Key: {config.has_api_key()}")
    
    # Открыть окно настроек на странице "О программе"
    window = SettingsWindow(config)
    window.sidebar.setCurrentRow(3)  # Выбрать страницу "О программе"
    window.show()
    
    sys.exit(app.exec())
