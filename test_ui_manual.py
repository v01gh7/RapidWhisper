"""
Ручной тест UI - показывает окно на 5 секунд.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from ui.floating_window import FloatingWindow


def main():
    app = QApplication(sys.argv)
    
    # Создать окно
    window = FloatingWindow()
    
    # Показать окно
    window.show_at_center()
    window.set_status("Тест UI - окно должно быть видно!")
    
    print("Окно показано! Должно быть видно в центре экрана.")
    print("Окно автоматически закроется через 5 секунд...")
    
    # Закрыть через 5 секунд
    QTimer.singleShot(5000, app.quit)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
