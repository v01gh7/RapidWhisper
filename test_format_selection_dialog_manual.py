"""
Manual test for FormatSelectionDialog.

Run this script to visually test the format selection dialog.
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.format_selection_dialog import FormatSelectionDialog
from services.formatting_config import FormattingConfig


def main():
    """Run manual test of format selection dialog."""
    app = QApplication(sys.argv)
    
    # Create test configuration
    config = FormattingConfig(
        enabled=True,
        provider="groq",
        model="llama-3.3-70b-versatile",
        applications=["notion", "obsidian", "markdown", "vscode", "word", "_fallback"],
        temperature=0.3
    )
    
    # Create and show dialog
    dialog = FormatSelectionDialog(config)
    result = dialog.exec()
    
    # Print result
    if result == dialog.DialogCode.Accepted:
        selected = dialog.get_selected_format()
        print(f"✓ Format selected: {selected}")
    else:
        print("✗ Dialog cancelled")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
