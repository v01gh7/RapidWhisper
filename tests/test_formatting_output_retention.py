"""Regression tests for retaining formatted output with structural tokens."""

from unittest.mock import Mock

from services.formatting_config import FormattingConfig
from services.formatting_module import FormattingModule
from services.processing_coordinator import ProcessingCoordinator


def test_format_text_keeps_email_output_with_mailto(monkeypatch):
    original_text = "привет отправь письмо клиенту завтра в 10 тема встреча"
    formatted_text = (
        "To: client@example.com\n"
        "Subject: Встреча завтра в 10\n"
        "Body:\n"
        "Привет, отправляю письмо клиенту.\n"
        "mailto: mailto:client@example.com?subject=%D0%92%D1%81%D1%82%D1%80%D0%B5%D1%87%D0%B0"
    )

    class FakeTranscriptionClient:
        def __init__(self, *args, **kwargs):
            pass

        def post_process_text(self, **kwargs):
            return formatted_text

    monkeypatch.setattr("services.transcription_client.TranscriptionClient", FakeTranscriptionClient)

    config = FormattingConfig(
        enabled=True,
        provider="custom",
        model="test-model",
        applications=["Email", "_fallback"],
        app_prompts={"Email": "email prompt", "_fallback": "fallback prompt"},
        custom_base_url="http://localhost:1234/v1",
        custom_api_key="test-key",
    )

    module = FormattingModule(config_manager=config, window_monitor=Mock())
    result = module.format_text(original_text, "Email")

    assert result == formatted_text


def test_fallback_formatting_keeps_bbcode_output():
    original_text = "Помощь при алкогольной интоксикации и кодирование в Алматы 24/7 анонимно"
    formatted_text = (
        "[size=200][b]Помощь при алкогольной интоксикации и кодирование в Алматы[/b][/size]\n"
        "[list]\n[*]24/7\n[*]Анонимно\n[/list]"
    )

    class FakeTranscriptionClient:
        def post_process_text(self, **kwargs):
            return formatted_text

    formatting_config = FormattingConfig(
        enabled=True,
        provider="custom",
        model="test-model",
        applications=["_fallback"],
        app_prompts={"_fallback": "fallback prompt"},
        custom_base_url="http://localhost:1234/v1",
        custom_api_key="test-key",
    )

    formatting_module = Mock()
    formatting_module.config = formatting_config

    coordinator = ProcessingCoordinator(formatting_module=formatting_module, config_manager=Mock())
    coordinator._run_hook_event = lambda event, text, format_type=None, combined=False: text

    runtime_config = Mock()
    runtime_config.post_processing_max_tokens = 4000

    result = coordinator._process_fallback_formatting(
        text=original_text,
        transcription_client=FakeTranscriptionClient(),
        config=runtime_config,
    )

    assert result == formatted_text
