"""
Final test for formatting UI improvements.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from ui.settings_window import SettingsWindow
from core.config import Config

def main():
    app = QApplication(sys.argv)
    
    # Create config
    config = Config()
    
    # Create settings window
    window = SettingsWindow(config)
    
    # Navigate to formatting page (index 3)
    window.content_stack.setCurrentIndex(3)
    
    window.show()
    
    # Show instructions
    QMessageBox.information(
        window,
        "Финальный тест форматирования",
        "Проверь исправления:\n\n"
        "1. Поле 'Модель' должно иметь placeholder:\n"
        "   'опционально, по умолчанию используется стандартная модель провайдера'\n\n"
        "2. Выбери 'groq' - placeholder должен быть:\n"
        "   'опционально, по умолчанию: llama-3.3-70b-versatile'\n\n"
        "3. Выбери 'custom' - должны появиться:\n"
        "   - Custom Base URL\n"
        "   - Custom API Key с кнопкой 👁\n\n"
        "4. Выбери обратно 'groq' - поля Custom должны исчезнуть\n"
        "   ВКЛЮЧАЯ кнопку 👁 (глазок)\n\n"
        "5. Убедись, что глазок не остаётся видимым!\n\n"
        "Закрой это окно, чтобы начать тест."
    )
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
