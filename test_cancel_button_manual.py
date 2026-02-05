"""
Manual test for cancel button functionality in InfoPanelWidget.

This test verifies that:
1. The cancel button emits cancel_clicked signal when clicked
2. The set_active_button method properly underlines and makes buttons non-clickable
3. The record button is set as active when recording starts
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from ui.info_panel_widget import InfoPanelWidget
from core.config import Config


def test_cancel_button():
    """Test cancel button functionality."""
    app = QApplication(sys.argv)
    
    # Load config
    config = Config.load_from_config()
    
    # Create info panel
    info_panel = InfoPanelWidget(config)
    info_panel.show()
    info_panel.setWindowTitle("InfoPanel Cancel Button Test")
    
    # Track signal emissions
    cancel_clicked_count = [0]
    
    def on_cancel_clicked():
        cancel_clicked_count[0] += 1
        print(f"✅ cancel_clicked signal emitted! Count: {cancel_clicked_count[0]}")
    
    # Connect signal
    info_panel.cancel_clicked.connect(on_cancel_clicked)
    
    # Test sequence
    def test_sequence():
        print("\n=== Test 1: Initial state (no active button) ===")
        print("Both buttons should be clickable with pointer cursor")
        
        QTimer.singleShot(2000, lambda: test_active_record())
    
    def test_active_record():
        print("\n=== Test 2: Set 'record' as active ===")
        info_panel.set_active_button("record")
        print("Record button should be underlined, bold, and non-clickable (arrow cursor)")
        print("Cancel button should be clickable (pointer cursor)")
        
        QTimer.singleShot(2000, lambda: test_reset())
    
    def test_reset():
        print("\n=== Test 3: Reset active button ===")
        info_panel.set_active_button(None)
        print("Both buttons should be clickable again")
        
        QTimer.singleShot(2000, lambda: test_cancel_click())
    
    def test_cancel_click():
        print("\n=== Test 4: Click cancel button ===")
        print("Simulating cancel button click...")
        # Simulate click by calling the handler directly
        info_panel._on_cancel_clicked(None)
        
        QTimer.singleShot(1000, lambda: finish_test())
    
    def finish_test():
        print("\n=== Test Results ===")
        if cancel_clicked_count[0] > 0:
            print(f"✅ SUCCESS: cancel_clicked signal was emitted {cancel_clicked_count[0]} time(s)")
        else:
            print("❌ FAILURE: cancel_clicked signal was NOT emitted")
        
        print("\nManual verification:")
        print("1. Did the record button become underlined and bold when set as active? (Test 2)")
        print("2. Did both buttons return to normal when reset? (Test 3)")
        print("3. Did clicking cancel emit the signal? (Test 4)")
        
        QTimer.singleShot(3000, app.quit)
    
    # Start test sequence
    QTimer.singleShot(1000, test_sequence)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    test_cancel_button()
