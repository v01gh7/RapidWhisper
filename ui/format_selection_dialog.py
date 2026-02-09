"""
Format Selection Dialog for RapidWhisper.

Provides a modal dialog for manual format selection triggered by hotkey.
Allows users to choose a formatting application for the current recording session.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
    QPushButton, QMessageBox, QWidget, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from services.formatting_config import FormattingConfig
from utils.i18n import t
from utils.logger import get_logger
from design_system.styled_window_mixin import StyledWindowMixin
from typing import Optional, List, Tuple

logger = get_logger()


class FormatSelectionDialog(QDialog, StyledWindowMixin):
    """
    Modal dialog for manual format selection.
    
    Displays a list of available formatting applications and allows
    the user to select one for the current recording session.
    
    Requirements: 2.1, 2.4, 7.1, 7.2, 7.3, 7.4
    """
    
    def __init__(self, formatting_config: FormattingConfig, parent=None):
        """
        Initialize the format selection dialog.
        
        Args:
            formatting_config: Configuration containing available formats
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize StyledWindowMixin
        StyledWindowMixin.__init__(self)
        
        self.formatting_config = formatting_config
        self._selected_format: Optional[str] = None
        self.format_buttons = {}  # Store format buttons
        
        # Set up the dialog
        self._create_ui()
        self._load_formats()
        
        # Apply unified styling
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Убрать border от окна
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        
        self.apply_unified_style(stay_on_top=True)
        
        logger.info("Format selection dialog initialized")

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.sync_rounded_surface()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.sync_rounded_surface()
    
    def _create_ui(self):
        """
        Create the dialog UI with format grid and buttons.
        
        Requirements: 2.1, 2.4
        """
        # Set window properties
        self.setWindowTitle(t("format_selection.title"))
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Main layout - БЕЗ BORDER ВООБЩЕ
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        
        # Title label
        title_label = QLabel(t("format_selection.select_format"))
        title_font = QFont()
        title_font.setPointSize(17)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setContentsMargins(20, 20, 20, 20)
        title_label.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(title_label)
        
        # Scroll area for format grid - БЕЗ BORDER
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setContentsMargins(0, 0, 0, 0)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        # Container widget for grid - БЕЗ BORDER
        container = QWidget()
        container.setContentsMargins(0, 0, 0, 0)
        container.setStyleSheet("QWidget { border: none; background: transparent; }")
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(20, 0, 20, 20)
        

        # Format grid layout (4 columns like in settings)
        self.formats_grid = QGridLayout()
        self.formats_grid.setSpacing(12)
        self.formats_grid.setHorizontalSpacing(12)
        self.formats_grid.setContentsMargins(0, 0, 0, 0)
        
        container_layout.addLayout(self.formats_grid)
        container_layout.addStretch()
        container.setLayout(container_layout)
        scroll_area.setWidget(container)
        
        layout.addWidget(scroll_area)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 0, 20, 20)
        button_layout.addStretch()
        
        # Cancel button
        cancel_btn = QPushButton(t("common.cancel"))
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self._on_cancel)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #fff;
                border-radius: 8px;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        logger.debug("Format selection dialog UI created")
    
    def _load_formats(self) -> List[Tuple[str, str]]:
        """
        Load available formats from configuration and create buttons.
        
        Returns:
            List of (format_id, display_name) tuples
            Universal format is always first
            
        Requirements: 2.2, 2.3, 6.1, 6.2, 6.3
        """
        try:
            formats = []
            
            # Always add Universal/_fallback format first
            universal_name = t("format_selection.universal_format")
            formats.append(("_fallback", universal_name))
            
            # Add configured applications
            if self.formatting_config and self.formatting_config.applications:
                for app_name in self.formatting_config.applications:
                    # Skip _fallback if it's in the list (we already added it)
                    if app_name == "_fallback":
                        continue
                    
                    # Create human-readable name (capitalize first letter)
                    display_name = app_name.replace("_", " ").title()
                    formats.append((app_name, display_name))
            
            # Create buttons in grid (4 columns like in settings)
            row = 0
            col = 0
            max_cols = 4
            
            for format_id, display_name in formats:
                # Create button for format
                btn = QPushButton(display_name)
                btn.setMinimumHeight(80)  # Same as settings
                btn.setMinimumWidth(120)  # Same as settings
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setCheckable(False)
                
                # Style button exactly like in settings
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2d2d2d;
                        color: #ffffff;
                        border: none;
                        border-radius: 8px;
                        padding: 8px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #3d3d3d;
                    }
                    QPushButton:pressed {
                        background-color: #0078d4;
                    }
                """)
                
                # Connect click to selection
                btn.clicked.connect(lambda checked, fid=format_id: self._on_format_button_clicked(fid))
                
                # Add to grid
                self.formats_grid.addWidget(btn, row, col)
                self.format_buttons[format_id] = btn
                
                # Move to next position
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            logger.info(f"Loaded {len(formats)} formats for selection")
            return formats
            
        except Exception as e:
            logger.error(f"Failed to load formats: {e}")
            
            # Display error message to user
            QMessageBox.warning(
                self,
                t("common.error"),
                t("format_selection.load_error")
            )
            
            # Fallback: show only Universal format
            universal_name = t("format_selection.universal_format")
            btn = QPushButton(universal_name)
            btn.setMinimumHeight(80)
            btn.setMinimumWidth(120)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    padding: 8px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                }
            """)
            btn.clicked.connect(lambda: self._on_format_button_clicked("_fallback"))
            self.formats_grid.addWidget(btn, 0, 0)
            self.format_buttons["_fallback"] = btn
            
            return [("_fallback", universal_name)]
    
    def _on_format_button_clicked(self, format_id: str):
        """
        Handle format button click.
        
        Args:
            format_id: ID of the selected format
        """
        self._selected_format = format_id
        logger.info(f"Format selected: {format_id}")
        self.accept()
    
    def _on_confirm(self):
        """
        Handle confirmation button click or double-click.
        
        Requirements: 3.1, 3.2
        """
        # Not used anymore - buttons directly select and close
        pass
    
    def _on_cancel(self):
        """
        Handle cancel button click or ESC key.
        
        Requirements: 3.3
        """
        logger.info("Format selection cancelled")
        self._selected_format = None
        self.reject()
    
    def get_selected_format(self) -> Optional[str]:
        """
        Get the user's selected format.
        
        Returns:
            Format identifier (e.g., "notion", "markdown", "_fallback")
            or None if dialog was cancelled
            
        Requirements: 3.1, 3.2
        """
        return self._selected_format
    
    def keyPressEvent(self, event):
        """
        Handle keyboard events for navigation.
        
        Requirements: 7.1, 7.2, 7.3
        """
        key = event.key()
        
        # ESC key - cancel
        if key == Qt.Key.Key_Escape:
            self._on_cancel()
        else:
            super().keyPressEvent(event)
