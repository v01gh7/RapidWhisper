import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # --- Настройки окна ---
        # Фиксированный размер, чтобы мы его нашли
        self.setFixedSize(300, 100)
        
        # Флаги: Поверх всех окон, Без рамок, Инструмент (не отображать в таскбаре)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Tool
        )
        
        # Включаем прозрачность фона
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # --- Интерфейс ---
        self.init_ui()
        
        # --- ПОКАЗАТЬ ОКНО СРАЗУ ---
        self.show()
        print("Окно запущено и должно быть видно!")
        
        # (Временный хак: закрыть окно через 5 сек, чтобы не висело вечно)
        QTimer.singleShot(5000, self.close)

    def init_ui(self):
        layout = QVBoxLayout()
        
        self.label = QLabel("PyQt6 Работает! ✅", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Стилизация: Делаем окно видимым (темный фон, скругления)
        # Без этого на прозрачном фоне текст будет сливаться с рабочим столом
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 240);
                border-radius: 20px;
                border: 2px solid rgba(255, 255, 255, 100);
            }
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: bold;
                padding: 20px;
            }
        """)
        
        layout.addWidget(self.label)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Создаем окно
    window = TestWindow()
    
    # Центрируем его на экране
    screen = app.primaryScreen()
    geometry = screen.availableGeometry()
    window.move(
        geometry.center().x() - window.width() // 2,
        geometry.center().y() - window.height() // 2
    )
    
    # Запускаем цикл событий
    sys.exit(app.exec())