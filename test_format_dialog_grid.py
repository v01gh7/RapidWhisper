"""
Manual test for FormatSelectionDialog with grid layout.

Run this script to visually verify the new grid-based design.
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.format_selection_dialog import FormatSelectionDialog
from services.formatting_config import FormattingConfig


def main():
    app = QApplication(sys.argv)
    
    # Create test configuration with multiple applications
    config = FormattingConfig(
        enabled=True,
        provider="groq",
        model="llama-3.3-70b-versatile",
        applications=["notion", "obsidian", "markdown", "slack", "telegram", "whatsapp", "vscode", "word"],
        temperature=0.3
    )
    
    # Create and show dialog
    dialog = FormatSelectionDialog(config)
    result = dialog.exec()
    
    if result:
        selected = dialog.get_selected_format()
        print(f"Selected format: {selected}")
    else:
        print("Dialog cancelled")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
