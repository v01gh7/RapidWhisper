"""
Тест для проверки исправления проблемы с QGraphicsOpacityEffect.

Проверяет, что эффект прозрачности удаляется после анимации
и не влияет на дочерние виджеты.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from core.config import Config
from ui.floating_window import FloatingWindow
from ui.settings_window import SettingsWindow


def test_opacity_effect_removal():
    """Тест удаления эффекта прозрачности."""
    app = QApplication(sys.argv)
    
    # Создать конфигурацию
    config = Config()
    
    # Создать FloatingWindow
    floating_window = FloatingWindow(config)
    floating_window.set_config(config)
    
    # Показать окно (запустит fade-in анимацию)
    floating_window.show_at_center()
    floating_window.set_status("Запись...")
    floating_window.show_info_panel()
    
    print("=== FloatingWindow показано ===")
    print(f"Opacity effect: {floating_window._opacity_effect}")
    print(f"Graphics effect: {floating_window.graphicsEffect()}")
    
    # Проверить через 500ms (после завершения fade-in анимации)
    QTimer.singleShot(500, lambda: check_after_animation(floating_window))
    
    # Открыть настройки через 1 секунду
    QTimer.singleShot(1000, lambda: open_settings(floating_window, config))
    
    # Закрыть через 3 секунды
    QTimer.singleShot(3000, lambda: close_all(floating_window))
    
    sys.exit(app.exec())


def check_after_animation(floating_window):
    """Проверить состояние после анимации."""
    print("\n=== После завершения fade-in анимации ===")
    print(f"Opacity effect: {floating_window._opacity_effect}")
    print(f"Graphics effect: {floating_window.graphicsEffect()}")
    
    if floating_window.graphicsEffect() is None:
        print("✅ Эффект прозрачности успешно удален!")
    else:
        print("❌ Эффект прозрачности все еще активен!")


def open_settings(floating_window, config):
    """Открыть окно настроек."""
    print("\n=== Открытие окна настроек ===")
    
    # Создать окно настроек
    settings_window = SettingsWindow(config, parent=floating_window)
    settings_window.center_on_screen()
    settings_window.show()
    
    print("Окно настроек открыто")
    print("Проверьте FloatingWindow визуально:")
    print("- InfoPanelWidget должен иметь темный фон #1a1a1a")
    print("- Текст должен быть четким без артефактов")
    print("- Иконка и название приложения должны отображаться корректно")


def close_all(floating_window):
    """Закрыть все окна."""
    print("\n=== Закрытие окон ===")
    floating_window.close()
    QApplication.quit()


if __name__ == "__main__":
    test_opacity_effect_removal()
