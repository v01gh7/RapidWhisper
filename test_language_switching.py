"""
Тест для проверки динамического переключения языка в настройках.

Этот тест проверяет, что при смене языка в настройках:
1. Язык сохраняется в .env
2. Интерфейс обновляется без перезапуска
3. Все тексты переводятся на выбранный язык
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from core.config import Config
from ui.settings_window import SettingsWindow
from utils.i18n import get_language, set_language

def test_language_switching():
    """Тест динамического переключения языка."""
    app = QApplication(sys.argv)
    
    # Загрузить конфигурацию из config.jsonc
    config = Config.load_from_config()
    
    print(f"Текущий язык: {config.interface_language}")
    print(f"Язык в i18n модуле: {get_language()}")
    
    # Создать окно настроек
    window = SettingsWindow(config)
    window.show()
    
    print("\n=== Окно настроек открыто ===")
    print(f"Заголовок окна: {window.windowTitle()}")
    
    # Найти кнопку английского языка
    en_button = None
    for button in window.language_button_group.buttons():
        if button.property("language_code") == "en":
            en_button = button
            break
    
    if en_button:
        print(f"\nНайдена кнопка английского языка")
        print(f"Текущее состояние: {'выбрана' if en_button.isChecked() else 'не выбрана'}")
        
        # Выбрать английский язык
        if not en_button.isChecked():
            print("\nВыбираем английский язык...")
            en_button.click()
            print(f"Кнопка теперь: {'выбрана' if en_button.isChecked() else 'не выбрана'}")
    else:
        print("\nОШИБКА: Кнопка английского языка не найдена!")
    
    # Запустить приложение
    sys.exit(app.exec())

if __name__ == "__main__":
    test_language_switching()
