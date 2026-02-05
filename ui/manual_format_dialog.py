"""
Manual formatting dialog for RapidWhisper.

Allows the user to select a formatting prompt and apply it to any pasted text.
"""

from typing import Optional, Tuple

from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QMessageBox,
)

from core.config_loader import get_config_loader
from design_system.styled_window_mixin import StyledWindowMixin
from services.clipboard_manager import ClipboardManager
from services.formatting_config import FormattingConfig
from services.formatting_module import FormattingModule
from utils.i18n import t
from utils.logger import get_logger

logger = get_logger()


class _FormatWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, text: str, format_id: str, formatting_config: FormattingConfig):
        super().__init__()
        self._text = text
        self._format_id = format_id
        self._config = formatting_config

    def run(self) -> None:
        try:
            module = FormattingModule(config_manager=self._config, state_manager=None)
            formatted = module.format_text(self._text, self._format_id)
            self.finished.emit(formatted)
        except Exception as exc:
            self.error.emit(str(exc))


class ManualFormatDialog(QDialog, StyledWindowMixin):
    def __init__(self, formatting_config: FormattingConfig, format_id: str, parent=None):
        super().__init__(parent)
        StyledWindowMixin.__init__(self)

        self.formatting_config = formatting_config
        self.format_id = format_id

        self._formatting_thread: Optional[QThread] = None
        self._formatting_worker: Optional[_FormatWorker] = None
        self._is_formatting = False

        self._create_ui()

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.apply_unified_style(stay_on_top=True)

        logger.info("Manual format dialog initialized")

    def _create_ui(self) -> None:
        self.setWindowTitle(t("manual_format.title"))
        self.setModal(True)
        self.setMinimumWidth(720)
        self.setMinimumHeight(520)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_label = QLabel(t("manual_format.title"))
        title_font = QFont()
        title_font.setPointSize(17)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(title_label)

        format_label = QLabel(t("manual_format.selected_format", format=self._format_display_name()))
        format_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        format_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        layout.addWidget(format_label)

        input_label = QLabel(t("manual_format.input_label"))
        layout.addWidget(input_label)

        self.input_edit = QTextEdit()
        self.input_edit.setMinimumHeight(160)
        self.input_edit.setStyleSheet(self._text_edit_style())
        layout.addWidget(self.input_edit)

        output_label = QLabel(t("manual_format.output_label"))
        layout.addWidget(output_label)

        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setMinimumHeight(160)
        self.output_edit.setStyleSheet(self._text_edit_style(read_only=True))
        layout.addWidget(self.output_edit)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(self.status_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.format_button = QPushButton(t("manual_format.format_button"))
        self.format_button.clicked.connect(self._on_format_clicked)
        self.format_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.format_button.setStyleSheet(self._button_style())
        button_layout.addWidget(self.format_button)

        self.copy_button = QPushButton(t("manual_format.copy_button"))
        self.copy_button.clicked.connect(self._on_copy_clicked)
        self.copy_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_button.setStyleSheet(self._button_style())
        self.copy_button.setEnabled(False)
        button_layout.addWidget(self.copy_button)

        self.close_button = QPushButton(t("common.close"))
        self.close_button.clicked.connect(self.reject)
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setStyleSheet(self._button_style())
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _format_display_name(self) -> str:
        if self.format_id == "_fallback":
            return t("format_selection.universal_format")
        return self.format_id.replace("_", " ").title()

    def _text_edit_style(self, read_only: bool = False) -> str:
        background = "#242424" if read_only else "#2d2d2d"
        return f"""
            QTextEdit {{
                background-color: {background};
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
            }}
            QTextEdit:focus {{
                border: 1px solid #0078d4;
            }}
        """

    def _button_style(self) -> str:
        return """
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
                min-width: 110px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:disabled {
                color: #777777;
                background-color: #242424;
                border: 1px solid #2a2a2a;
            }
        """

    def _on_format_clicked(self) -> None:
        if self._is_formatting:
            return

        text = self.input_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, t("common.error"), t("manual_format.empty_input_message"))
            return

        if not self._has_formatting_credentials():
            QMessageBox.warning(
                self,
                t("common.error"),
                t("manual_format.no_api_key_message", provider=self.formatting_config.provider),
            )
            return

        self._set_formatting_state(True)
        self._set_status("")

        self._formatting_thread = QThread(self)
        self._formatting_worker = _FormatWorker(text, self.format_id, self.formatting_config)
        self._formatting_worker.moveToThread(self._formatting_thread)

        self._formatting_thread.started.connect(self._formatting_worker.run)
        self._formatting_worker.finished.connect(self._on_formatting_finished)
        self._formatting_worker.error.connect(self._on_formatting_error)
        self._formatting_worker.finished.connect(self._formatting_worker.deleteLater)
        self._formatting_worker.error.connect(self._formatting_worker.deleteLater)
        self._formatting_worker.finished.connect(self._formatting_thread.quit)
        self._formatting_worker.error.connect(self._formatting_thread.quit)
        self._formatting_thread.finished.connect(self._formatting_thread.deleteLater)

        self._formatting_thread.start()

    def _on_formatting_finished(self, formatted_text: str) -> None:
        self.output_edit.setPlainText(formatted_text)
        self.copy_button.setEnabled(bool(formatted_text.strip()))
        self._set_formatting_state(False)

    def _on_formatting_error(self, error_message: str) -> None:
        logger.error(f"Manual formatting error: {error_message}")
        QMessageBox.warning(self, t("common.error"), t("manual_format.format_error_message"))
        self._set_formatting_state(False)

    def _on_copy_clicked(self) -> None:
        text = self.output_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, t("common.error"), t("manual_format.no_output_message"))
            return

        if ClipboardManager.copy_to_clipboard(text):
            self._set_status(t("manual_format.copy_success_message"))
        else:
            QMessageBox.warning(self, t("common.error"), t("manual_format.copy_failed_message"))

    def _set_formatting_state(self, is_formatting: bool) -> None:
        self._is_formatting = is_formatting
        self.input_edit.setReadOnly(is_formatting)
        self.format_button.setEnabled(not is_formatting)
        self.close_button.setEnabled(not is_formatting)
        self.copy_button.setEnabled(not is_formatting and bool(self.output_edit.toPlainText().strip()))
        if is_formatting:
            self.format_button.setText(t("manual_format.formatting_button"))
        else:
            self.format_button.setText(t("manual_format.format_button"))

    def _set_status(self, message: str) -> None:
        self.status_label.setText(message)
        if message:
            QTimer.singleShot(2000, lambda: self.status_label.setText(""))

    def _has_formatting_credentials(self) -> bool:
        api_key, base_url = self._get_formatting_credentials()
        if not api_key:
            return False
        if self.formatting_config.provider == "custom" and not base_url:
            return False
        return True

    def _get_formatting_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        provider = self.formatting_config.provider
        base_url = None
        api_key = None

        config_loader = get_config_loader()

        if provider == "groq":
            api_key = config_loader.get("ai_provider.api_keys.groq")
        elif provider == "openai":
            api_key = config_loader.get("ai_provider.api_keys.openai")
        elif provider == "glm":
            api_key = config_loader.get("ai_provider.api_keys.glm")
        elif provider == "zai":
            api_key = config_loader.get("ai_provider.api_keys.glm")
        elif provider == "custom":
            api_key = self.formatting_config.custom_api_key
            base_url = self.formatting_config.custom_base_url

        return api_key, base_url

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape and self._is_formatting:
            event.accept()
            return
        super().keyPressEvent(event)
