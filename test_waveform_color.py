"""
Тест для проверки функциональности цвета волны с градиентом.
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from core.config import Config
from ui.floating_window import FloatingWindow


def test_waveform_color():
    """Тест изменения цвета волны с градиентом."""
    app = QApplication(sys.argv)
    
    # Загрузить конфигурацию
    config = Config.load_from_config()
    print(f"Loaded config with waveform color: {config.waveform_color}")
    
    # Создать плавающее окно
    window = FloatingWindow(config)
    window.show_at_center()
    
    # Получить виджет волны
    waveform = window.get_waveform_widget()
    print(f"Waveform widget color: {waveform._waveform_color}")
    
    # Запустить анимацию записи
    waveform.start_recording_animation()
    
    # Добавить тестовые данные с разной громкостью для демонстрации градиента
    import random
    def add_test_data():
        # Создаем волну с разной громкостью
        for i in range(50):
            # Синусоидальная волна для красивого эффекта
            import math
            rms = 0.3 + 0.5 * abs(math.sin(i * 0.2))
            waveform.update_rms(rms)
    
    # Добавить данные через 500мс
    QTimer.singleShot(500, add_test_data)
    
    # Изменить цвет через 3 секунды
    def change_color():
        print("Changing color to red...")
        waveform.set_waveform_color("#FF0000")
        add_test_data()
    
    QTimer.singleShot(3000, change_color)
    
    # Изменить цвет на зеленый через 6 секунд
    def change_to_green():
        print("Changing color to green...")
        waveform.set_waveform_color("#00FF00")
        add_test_data()
    
    QTimer.singleShot(6000, change_to_green)
    
    # Изменить цвет на фиолетовый через 9 секунд
    def change_to_purple():
        print("Changing color to purple...")
        waveform.set_waveform_color("#9B59B6")
        add_test_data()
    
    QTimer.singleShot(9000, change_to_purple)
    
    # Закрыть через 12 секунд
    QTimer.singleShot(12000, app.quit)
    
    print("Test started. Window should show waveform with gradient and changing colors.")
    print("Blue (gradient) -> Red (3s) -> Green (6s) -> Purple (9s) -> Close (12s)")
    print("Notice how each bar has different brightness based on volume!")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    test_waveform_color()
