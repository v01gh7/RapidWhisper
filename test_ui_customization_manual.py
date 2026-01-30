"""
Ручной тест для проверки UI Customization.

Этот скрипт позволяет вручную протестировать:
1. Изменение прозрачности окна с live preview
2. Изменение размеров шрифтов с автосохранением
3. Кнопку "Сброс на значения по умолчанию"
4. Сохранение всех настроек при нажатии "Сохранить"
"""

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from core.config import Config
from ui.settings_window import SettingsWindow
from ui.floating_window import FloatingWindow


def main():
    """Запускает тестовое окно настроек."""
    app = QApplication(sys.argv)
    
    # Загрузить конфигурацию
    config = Config()
    
    # Создать плавающее окно (для live preview прозрачности)
    floating_window = FloatingWindow(config)
    floating_window.show()
    floating_window.set_status("Тестовое окно для проверки прозрачности")
    
    # Создать окно настроек с родителем floating_window
    settings = SettingsWindow(config, parent=floating_window)
    
    # Перейти на страницу UI Customization (индекс 5)
    settings.sidebar.setCurrentRow(5)
    
    # Показать инструкции
    QMessageBox.information(
        settings,
        "Тест UI Customization",
        "Проверьте следующее:\n\n"
        "1. Измените прозрачность слайдером - окно должно меняться сразу\n"
        "2. Измените размеры шрифтов - они должны сохраняться автоматически\n"
        "3. Нажмите 'Сброс на значения по умолчанию' - все должно вернуться к дефолтам\n"
        "4. Нажмите 'Сохранить' - все настройки должны сохраниться в .env\n\n"
        "Проверьте, что кнопки 'Вверх' и 'Вниз' работают для всех спинбоксов."
    )
    
    # Показать окно настроек
    settings.exec()
    
    # Закрыть приложение
    floating_window.close()
    sys.exit(0)


if __name__ == "__main__":
    main()
