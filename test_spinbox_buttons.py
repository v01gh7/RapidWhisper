"""
Тест для проверки работы кнопок "Вверх" и "Вниз" в спинбоксах.

Этот скрипт создает простое окно с QSpinBox для проверки:
1. Кнопка "Вверх" увеличивает значение
2. Кнопка "Вниз" уменьшает значение
3. Значения остаются в пределах диапазона
"""

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSpinBox, QAbstractSpinBox
from PyQt6.QtCore import Qt


class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест кнопок SpinBox")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        # Инструкция
        instruction = QLabel(
            "Проверьте работу кнопок:\n\n"
            "1. Нажмите кнопку ↑ (Вверх) - значение должно увеличиться\n"
            "2. Нажмите кнопку ↓ (Вниз) - значение должно уменьшиться\n"
            "3. Попробуйте достичь минимума и максимума\n"
            "4. Убедитесь, что обе кнопки работают"
        )
        instruction.setWordWrap(True)
        layout.addWidget(instruction)
        
        # Тест 1: Шрифт основного текста (10-24)
        layout.addWidget(QLabel("\nШрифт основного текста (10-24 px):"))
        self.spin1 = QSpinBox()
        self.spin1.setRange(10, 24)
        self.spin1.setSingleStep(1)
        self.spin1.setSuffix(" px")
        self.spin1.setValue(14)
        self.spin1.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.spin1.valueChanged.connect(lambda v: print(f"Spin1 changed to: {v}"))
        layout.addWidget(self.spin1)
        
        # Тест 2: Шрифт инфо панели (8-16)
        layout.addWidget(QLabel("\nШрифт инфо панели (8-16 px):"))
        self.spin2 = QSpinBox()
        self.spin2.setRange(8, 16)
        self.spin2.setSingleStep(1)
        self.spin2.setSuffix(" px")
        self.spin2.setValue(11)
        self.spin2.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.spin2.valueChanged.connect(lambda v: print(f"Spin2 changed to: {v}"))
        layout.addWidget(self.spin2)
        
        # Тест 3: Шрифт меток (10-16)
        layout.addWidget(QLabel("\nШрифт меток (10-16 px):"))
        self.spin3 = QSpinBox()
        self.spin3.setRange(10, 16)
        self.spin3.setSingleStep(1)
        self.spin3.setSuffix(" px")
        self.spin3.setValue(12)
        self.spin3.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.spin3.valueChanged.connect(lambda v: print(f"Spin3 changed to: {v}"))
        layout.addWidget(self.spin3)
        
        # Тест 4: Шрифт заголовков (16-32)
        layout.addWidget(QLabel("\nШрифт заголовков (16-32 px):"))
        self.spin4 = QSpinBox()
        self.spin4.setRange(16, 32)
        self.spin4.setSingleStep(1)
        self.spin4.setSuffix(" px")
        self.spin4.setValue(24)
        self.spin4.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.UpDownArrows)
        self.spin4.valueChanged.connect(lambda v: print(f"Spin4 changed to: {v}"))
        layout.addWidget(self.spin4)
        
        # Результат
        self.result_label = QLabel("\n✅ Если обе кнопки работают - тест пройден!")
        self.result_label.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.result_label)
        
        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
