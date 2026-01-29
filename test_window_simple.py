"""
Простейший тест окна - копия skeleto.py логики
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from ui.floating_window import FloatingWindow


def main():
    app = QApplication(sys.argv)
    
    # Создать окно
    window = FloatingWindow()
    
    # Установить текст
    window.set_status("RapidWhisper работает! ✅")
    
    # Показать окно
    window.show_at_center()
    
    print("=" * 50)
    print("ОКНО ДОЛЖНО БЫТЬ ВИДНО В ЦЕНТРЕ ЭКРАНА!")
    print("Темное окно с текстом 'RapidWhisper работает! ✅'")
    print("Окно закроется через 5 секунд...")
    print("=" * 50)
    
    # Закрыть через 5 секунд
    QTimer.singleShot(5000, app.quit)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
