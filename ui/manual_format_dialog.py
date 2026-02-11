"""
Manual formatting dialog for RapidWhisper.

Allows the user to select a formatting prompt and apply it to any pasted text.
"""

from typing import Optional, Tuple
import os
from pathlib import Path

from PyQt6.QtCore import Qt, QObject, pyqtSignal, QThread, QTimer, QMimeData
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QMessageBox,
    QMenu,
)

from core.config_loader import get_config_loader
from design_system.styled_window_mixin import StyledWindowMixin
from design_system.window_themes import DEFAULT_WINDOW_THEME_ID, get_window_theme
from services.clipboard_manager import ClipboardManager
from services.formatting_config import FormattingConfig
from services.formatting_module import FormattingModule
from utils.i18n import t
from utils.logger import get_logger

logger = get_logger()


class _TranscriptionWorker(QObject):
    """Worker for transcribing audio files in background thread."""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, audio_path: str, formatting_config: FormattingConfig):
        super().__init__()
        self._audio_path = audio_path
        self._formatting_config = formatting_config

    def run(self) -> None:
        """Transcribe audio file and emit result."""
        try:
            from services.transcription_client import TranscriptionClient
            from core.config_loader import get_config_loader
            from core.config import Config

            config_loader = get_config_loader()
            config = Config.load_from_config()

            # Get transcription provider settings
            provider = config_loader.get("ai_provider.provider", "groq")
            api_key = None
            base_url = None
            model = config_loader.get("ai_provider.transcription_custom_model")

            if provider == "groq":
                api_key = config_loader.get("ai_provider.api_keys.groq")
            elif provider == "openai":
                api_key = config_loader.get("ai_provider.api_keys.openai")
            elif provider == "glm":
                api_key = config_loader.get("ai_provider.api_keys.glm")
            elif provider == "custom":
                api_key = config_loader.get("ai_provider.api_keys.custom")
                base_url = config_loader.get("ai_provider.custom_base_url")

            if not api_key:
                self.error.emit(t("manual_format.no_transcription_api_key"))
                return

            # Create client and transcribe
            client = TranscriptionClient(
                provider=provider,
                api_key=api_key,
                base_url=base_url,
                model=model
            )

            # Convert to WAV if needed (for mp3, m4a, etc.)
            audio_to_transcribe = self._ensure_wav_format(self._audio_path)

            try:
                text = client.transcribe_audio(audio_to_transcribe)
                self.finished.emit(text)
            finally:
                # Clean up temporary WAV file if created
                if audio_to_transcribe != self._audio_path and os.path.exists(audio_to_transcribe):
                    os.remove(audio_to_transcribe)

        except Exception as exc:
            logger.error(f"Transcription worker error: {exc}")
            self.error.emit(str(exc))

    def _ensure_wav_format(self, audio_path: str) -> str:
        """Convert audio to WAV format if needed. Returns path to WAV file."""
        suffix = Path(audio_path).suffix.lower()

        if suffix == '.wav':
            return audio_path

        # For non-WAV files, convert using ffmpeg if available
        import tempfile
        import subprocess

        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_path = tmp_file.name

            # Try to convert with ffmpeg
            subprocess.run(
                ['ffmpeg', '-y', '-i', audio_path, tmp_path],
                capture_output=True,
                check=True
            )
            logger.info(f"Converted {audio_path} to WAV format")
            return tmp_path
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            logger.warning(f"Could not convert to WAV: {e}")
            # Try using original file anyway
            return audio_path


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
    RESULT_BACK_TO_SELECTION = 1001

    # Signals for transcription and re-transcription
    transcription_complete = pyqtSignal(str)  # Text from audio transcription
    transcription_error = pyqtSignal(str)  # Error message

    def __init__(self, formatting_config: FormattingConfig, format_id: str, parent=None, theme_id: Optional[str] = None):
        super().__init__(parent)
        StyledWindowMixin.__init__(self)

        self.formatting_config = formatting_config
        self.format_id = format_id
        self._theme_id = theme_id or DEFAULT_WINDOW_THEME_ID
        self._theme = get_window_theme(self._theme_id)
        self._window_theme_id = self._theme_id
        self._window_theme = self._theme
        self._force_opaque_surface = True
        self._title_label: Optional[QLabel] = None
        self._format_label: Optional[QLabel] = None
        self._input_label: Optional[QLabel] = None
        self._output_label: Optional[QLabel] = None

        self._formatting_thread: Optional[QThread] = None
        self._formatting_worker: Optional[_FormatWorker] = None
        self._is_formatting = False
        self.back_button: Optional[QPushButton] = None
        self._transcription_thread: Optional[QThread] = None
        self._transcription_worker: Optional["_TranscriptionWorker"] = None
        self._is_transcribing = False

        self._create_ui()

        # Enable drag-drop
        self.setAcceptDrops(True)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.apply_unified_style(opacity=255, stay_on_top=True)

        logger.info("Manual format dialog initialized")

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.sync_rounded_surface()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.sync_rounded_surface()

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
        title_font.setFamily(self._theme["font_family"])
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"border: none; background: transparent; color: {self._theme['text_primary']};")
        layout.addWidget(title_label)
        self._title_label = title_label

        format_label = QLabel(t("manual_format.selected_format", format=self._format_display_name()))
        format_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        format_label.setStyleSheet(
            f"color: {self._theme['text_secondary']}; font-size: 12px; font-family: '{self._theme['font_family']}';"
        )
        layout.addWidget(format_label)
        self._format_label = format_label

        input_label = QLabel(t("manual_format.input_label"))
        input_label.setStyleSheet(
            f"color: {self._theme['text_primary']}; font-size: 12px; font-family: '{self._theme['font_family']}';"
        )
        layout.addWidget(input_label)
        self._input_label = input_label

        self.input_edit = QTextEdit()
        self.input_edit.setMinimumHeight(160)
        self.input_edit.setStyleSheet(self._text_edit_style())
        layout.addWidget(self.input_edit)

        output_label = QLabel(t("manual_format.output_label"))
        output_label.setStyleSheet(
            f"color: {self._theme['text_primary']}; font-size: 12px; font-family: '{self._theme['font_family']}';"
        )
        layout.addWidget(output_label)
        self._output_label = output_label

        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setMinimumHeight(160)
        self.output_edit.setStyleSheet(self._text_edit_style(read_only=True))
        layout.addWidget(self.output_edit)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet(
            f"color: {self._theme['text_secondary']}; font-size: 11px; font-family: '{self._theme['font_family']}';"
        )
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

        self.back_button = QPushButton(t("manual_format.back_to_formats_button"))
        self.back_button.clicked.connect(self._on_back_clicked)
        self.back_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_button.setStyleSheet(self._button_style())
        button_layout.addWidget(self.back_button)

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
        background = self._theme["input_bg_alt"] if read_only else self._theme["input_bg"]
        color = self._theme["text_secondary"] if read_only else self._theme["text_primary"]
        return f"""
            QTextEdit {{
                background-color: {background};
                color: {color};
                border: 1px solid {self._theme["input_border"]};
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                font-family: '{self._theme["font_family"]}';
            }}
            QTextEdit:focus {{
                border: 1px solid {self._theme["input_focus"]};
            }}
        """

    def _button_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {self._theme["input_bg"]};
                color: {self._theme["text_primary"]};
                border: 1px solid {self._theme["input_border"]};
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12px;
                min-width: 110px;
                font-family: '{self._theme["font_family"]}';
            }}
            QPushButton:hover {{
                background-color: {self._theme["sidebar_hover"]};
                border: 1px solid {self._theme["input_focus"]};
            }}
            QPushButton:disabled {{
                color: {self._theme["text_secondary"]};
                background-color: {self._theme["input_bg_alt"]};
                border: 1px solid {self._theme["input_border"]};
            }}
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
        details = error_message.strip()
        if details:
            QMessageBox.warning(
                self,
                t("common.error"),
                f"{t('manual_format.format_error_message')}\n\n{details}"
            )
        else:
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

    def _on_back_clicked(self) -> None:
        if self._is_formatting:
            return
        self.done(self.RESULT_BACK_TO_SELECTION)

    def _set_formatting_state(self, is_formatting: bool) -> None:
        self._is_formatting = is_formatting
        self.input_edit.setReadOnly(is_formatting)
        self.format_button.setEnabled(not is_formatting)
        if self.back_button is not None:
            self.back_button.setEnabled(not is_formatting)
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

    # Drag and drop support
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            # Check if any URL is a supported file type
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path:
                    suffix = Path(file_path).suffix.lower()
                    if suffix in ('.wav', '.mp3', '.ogg', '.flac', '.m4a', '.mp4', '.txt', '.md'):
                        event.acceptProposedAction()
                        return
        event.ignore()

    def dragMoveEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag move event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop event - process dropped files."""
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if not file_path:
                continue

            path = Path(file_path)
            suffix = path.suffix.lower()

            # Audio files - transcribe then format
            if suffix in ('.wav', '.mp3', '.ogg', '.flac', '.m4a', '.mp4'):
                self._start_transcription(str(path))
                event.acceptProposedAction()
                return

            # Text files - load directly
            elif suffix in ('.txt', '.md'):
                self._load_text_file(str(path))
                event.acceptProposedAction()
                return

        event.ignore()

    def _load_text_file(self, file_path: str) -> None:
        """Load text file content into input area."""
        try:
            text = Path(file_path).read_text(encoding='utf-8')
            self.input_edit.setPlainText(text)
            self._set_status(t("manual_format.file_loaded", filename=Path(file_path).name))
        except Exception as e:
            logger.error(f"Failed to load text file: {e}")
            QMessageBox.warning(
                self,
                t("common.error"),
                t("manual_format.file_load_error", error=str(e))
            )

    def _start_transcription(self, audio_path: str) -> None:
        """Start audio transcription in background thread."""
        if self._is_transcribing:
            logger.warning("Transcription already in progress")
            return

        # Check transcription credentials
        if not self._has_transcription_credentials():
            QMessageBox.warning(
                self,
                t("common.error"),
                t("manual_format.no_transcription_api_key")
            )
            return

        self._set_transcription_state(True)
        self._set_status(t("manual_format.transcribing"))

        # Create and start transcription thread
        self._transcription_thread = QThread(self)
        self._transcription_worker = _TranscriptionWorker(audio_path, self.formatting_config)
        self._transcription_worker.moveToThread(self._transcription_thread)

        self._transcription_thread.started.connect(self._transcription_worker.run)
        self._transcription_worker.finished.connect(self._on_transcription_finished)
        self._transcription_worker.error.connect(self._on_transcription_error)
        self._transcription_worker.finished.connect(self._transcription_worker.deleteLater)
        self._transcription_worker.error.connect(self._transcription_worker.deleteLater)
        self._transcription_worker.finished.connect(self._transcription_thread.quit)
        self._transcription_worker.error.connect(self._transcription_thread.quit)
        self._transcription_thread.finished.connect(self._transcription_thread.deleteLater)

        self._transcription_thread.start()

    def _on_transcription_finished(self, text: str) -> None:
        """Handle successful transcription."""
        self.input_edit.setPlainText(text)
        self._set_transcription_state(False)
        self._set_status(t("manual_format.transcription_complete"))

    def _on_transcription_error(self, error_message: str) -> None:
        """Handle transcription error."""
        logger.error(f"Transcription error: {error_message}")
        QMessageBox.warning(
            self,
            t("common.error"),
            f"{t('manual_format.transcription_error')}\n\n{error_message}"
        )
        self._set_transcription_state(False)

    def _set_transcription_state(self, is_transcribing: bool) -> None:
        """Update UI state during transcription."""
        self._is_transcribing = is_transcribing
        self.input_edit.setReadOnly(is_transcribing)
        self.format_button.setEnabled(not is_transcribing)
        if self.back_button is not None:
            self.back_button.setEnabled(not is_transcribing)
        self.close_button.setEnabled(not is_transcribing)

        if is_transcribing:
            # Show transcription in progress
            self.format_button.setText(t("manual_format.transcribing_button"))
        else:
            self.format_button.setText(t("manual_format.format_button"))

    def _has_transcription_credentials(self) -> bool:
        """Check if transcription API credentials are configured."""
        from core.config_loader import get_config_loader
        config_loader = get_config_loader()

        provider = config_loader.get("ai_provider.provider", "groq")
        api_key = None

        if provider == "groq":
            api_key = config_loader.get("ai_provider.api_keys.groq")
        elif provider == "openai":
            api_key = config_loader.get("ai_provider.api_keys.openai")
        elif provider == "glm":
            api_key = config_loader.get("ai_provider.api_keys.glm")
        elif provider == "custom":
            api_key = config_loader.get("ai_provider.api_keys.custom")

        return bool(api_key)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape and self._is_formatting:
            event.accept()
            return
        super().keyPressEvent(event)

    def set_theme(self, theme_id: str) -> None:
        """Apply theme to dialog at runtime."""
        self._theme_id = theme_id or DEFAULT_WINDOW_THEME_ID
        self._theme = get_window_theme(self._theme_id)
        self.set_window_theme(self._theme_id)

        if self._title_label is not None:
            title_font = self._title_label.font()
            title_font.setFamily(self._theme["font_family"])
            self._title_label.setFont(title_font)
            self._title_label.setStyleSheet(
                f"border: none; background: transparent; color: {self._theme['text_primary']};"
            )

        if self._format_label is not None:
            self._format_label.setStyleSheet(
                f"color: {self._theme['text_secondary']}; font-size: 12px; font-family: '{self._theme['font_family']}';"
            )

        if self._input_label is not None:
            self._input_label.setStyleSheet(
                f"color: {self._theme['text_primary']}; font-size: 12px; font-family: '{self._theme['font_family']}';"
            )
        if self._output_label is not None:
            self._output_label.setStyleSheet(
                f"color: {self._theme['text_primary']}; font-size: 12px; font-family: '{self._theme['font_family']}';"
            )

        if hasattr(self, "status_label") and self.status_label is not None:
            self.status_label.setStyleSheet(
                f"color: {self._theme['text_secondary']}; font-size: 11px; font-family: '{self._theme['font_family']}';"
            )
        if hasattr(self, "input_edit") and self.input_edit is not None:
            self.input_edit.setStyleSheet(self._text_edit_style())
        if hasattr(self, "output_edit") and self.output_edit is not None:
            self.output_edit.setStyleSheet(self._text_edit_style(read_only=True))
        if hasattr(self, "format_button") and self.format_button is not None:
            self.format_button.setStyleSheet(self._button_style())
        if hasattr(self, "copy_button") and self.copy_button is not None:
            self.copy_button.setStyleSheet(self._button_style())
        if hasattr(self, "back_button") and self.back_button is not None:
            self.back_button.setStyleSheet(self._button_style())
        if hasattr(self, "close_button") and self.close_button is not None:
            self.close_button.setStyleSheet(self._button_style())
