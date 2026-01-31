"""
Тест для проверки виджета HotkeyInput
"""

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from ui.hotkey_input import HotkeyInput


def main():
    app = QApplication(sys.argv)
    
    # Создать окно
    window = QWidget()
    window.setWindowTitle("Тест HotkeyInput")
    window.setMinimumWidth(400)
    window.setMinimumHeight(250)
    
    # Применить темный стиль
    window.setStyleSheet("""
        QWidget {
            background-color: rgba(30, 30, 30, 150);
            color: #ffffff;
        }
        QLabel {
            color: #ffffff;
            font-size: 14px;
            padding: 10px;
        }
        QPushButton {
            background-color: #0078d4;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 12px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #1084d8;
        }
    """)
    
    # Создать layout
    layout = QVBoxLayout()
    
    # Добавить инструкцию
    instruction = QLabel(
        "Кликните на поле ниже и нажмите сочетание клавиш\n"
        "(например: Ctrl+Space, F1, Ctrl+Shift+R)\n\n"
        "Кнопка 🔄 сбрасывает значение на 'ctrl+space'"
    )
    layout.addWidget(instruction)
    
    # Создать контейнер для HotkeyInput и кнопки сброса
    hotkey_container = QHBoxLayout()
    
    # Создать HotkeyInput
    hotkey_input = HotkeyInput()
    hotkey_input.setMinimumHeight(40)
    hotkey_input.setText("ctrl+space")  # Начальное значение
    hotkey_container.addWidget(hotkey_input)
    
    # Создать кнопку сброса
    reset_btn = QPushButton("🔄")
    reset_btn.setMaximumWidth(40)
    reset_btn.setToolTip("Сбросить на ctrl+space")
    reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    hotkey_container.addWidget(reset_btn)
    
    layout.addLayout(hotkey_container)
    
    # Добавить label для отображения результата
    result_label = QLabel("Результат: ctrl+space")
    layout.addWidget(result_label)
    
    # Подключить сигнал изменения
    def on_hotkey_changed(hotkey: str):
        result_label.setText(f"Результат: {hotkey}")
        print(f"Новая горячая клавиша: {hotkey}")
    
    hotkey_input.hotkey_changed.connect(on_hotkey_changed)
    
    # Подключить кнопку сброса
    def on_reset():
        hotkey_input.setText("ctrl+space")
        hotkey_input.clearFocus()
        result_label.setText("Результат: ctrl+space (сброшено)")
        print("Горячая клавиша сброшена на: ctrl+space")
    
    reset_btn.clicked.connect(on_reset)
    
    # Установить layout
    window.setLayout(layout)
    
    # Показать окно
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
