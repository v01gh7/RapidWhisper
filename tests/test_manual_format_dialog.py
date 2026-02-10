"""
Tests for manual formatting dialog behavior.
"""

from services.formatting_config import FormattingConfig
from ui.manual_format_dialog import ManualFormatDialog


def test_manual_format_dialog_initializes_without_style_errors(qtbot):
    config = FormattingConfig(
        enabled=True,
        provider="groq",
        applications=["_fallback"],
        app_prompts={"_fallback": "test"},
    )

    dialog = ManualFormatDialog(config, "_fallback")
    qtbot.addWidget(dialog)

    assert dialog.format_button is not None
    assert dialog.copy_button is not None
    assert dialog.back_button is not None
    assert dialog.close_button is not None


def test_manual_format_dialog_back_button_returns_to_selection(qtbot):
    config = FormattingConfig(
        enabled=True,
        provider="groq",
        applications=["_fallback"],
        app_prompts={"_fallback": "test"},
    )

    dialog = ManualFormatDialog(config, "_fallback")
    qtbot.addWidget(dialog)

    dialog.back_button.click()
    assert dialog.result() == ManualFormatDialog.RESULT_BACK_TO_SELECTION
