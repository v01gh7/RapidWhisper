"""
Manual test for formatting UI with per-application prompts.
"""

import sys
from PyQt6.QtWidgets import QApplication
from core.config import Config
from ui.settings_window import SettingsWindow


def test_formatting_ui():
    """Test the new formatting UI with visual blocks."""
    app = QApplication(sys.argv)
    
    # Create config
    config = Config.from_env()
    
    # Create settings window
    window = SettingsWindow(config)
    
    # Navigate to processing page (index 3)
    window.sidebar.setCurrentRow(3)
    
    # Show window
    window.show()
    
    print("✅ Settings window opened successfully")
    print("📋 Navigate to 'Обработка' tab to see the new formatting UI")
    print("🎨 You should see visual blocks for applications instead of text field")
    print("🖱️ Right-click on any application to edit or delete")
    print("➕ Click 'Добавить приложение' to add new applications")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    test_formatting_ui()
