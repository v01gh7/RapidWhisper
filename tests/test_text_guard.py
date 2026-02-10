"""Tests for formatted-text token guard behavior."""

from utils.text_guard import has_extra_tokens


def test_has_extra_tokens_ignores_bbcode_tags() -> None:
    original = "Помощь при алкогольной интоксикации и кодирование в Алматы 24/7 анонимно"
    candidate = (
        "[size=200][b]Помощь при алкогольной интоксикации и кодирование в Алматы[/b][/size]\n"
        "[list]\n[*]24/7\n[*]анонимно\n[/list]"
    )
    assert has_extra_tokens(original, candidate) is False


def test_has_extra_tokens_ignores_html_tags() -> None:
    original = "help with intoxication available 24 7 anonymous"
    candidate = "<h2><strong>help with intoxication</strong></h2><ul><li>available 24 7</li><li>anonymous</li></ul>"
    assert has_extra_tokens(original, candidate) is False


def test_has_extra_tokens_detects_real_new_word() -> None:
    original = "help with intoxication"
    candidate = "[b]help with intoxication[/b] premium"
    assert has_extra_tokens(original, candidate) is True


def test_has_extra_tokens_ignores_common_markup_words_without_brackets() -> None:
    original = "help with intoxication"
    candidate = "size b help with intoxication b size"
    assert has_extra_tokens(original, candidate) is False
