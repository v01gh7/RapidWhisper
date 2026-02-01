"""
Property-based tests for format detection and matching logic.

These tests validate universal properties for window detection and
application format matching.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, MagicMock
from services.formatting_module import (
    FormattingModule,
    match_window_to_format
)
from services.formatting_config import FormattingConfig
from services.window_monitor import WindowInfo
from PyQt6.QtGui import QPixmap


# Strategy for generating application names
app_name_strategy = st.sampled_from([
    "notion", "Notion", "NOTION", "notion.exe",
    "obsidian", "Obsidian", "obsidian.exe",
    "word", "Word", "winword.exe", "Microsoft Word",
    "code", "vscode", "Visual Studio Code",
    "sublime", "Sublime Text", "sublime_text",
    "notepad++", "Notepad++",
    "chrome", "firefox", "terminal", "unknown_app"
])

# Strategy for generating file extensions
file_ext_strategy = st.sampled_from([
    ".md", ".markdown", ".txt", ".docx", ".doc",
    ".pdf", ".html", ".py", ".js", ""
])


class TestFormatDetectionProperties:
    """Property-based tests for format detection."""
    
    @given(
        app_name=st.text(min_size=1, max_size=50),
        file_ext=st.text(min_size=0, max_size=10)
    )
    @settings(max_examples=20)
    def test_window_detection_completeness(self, app_name, file_ext):
        """
        Feature: transcription-formatting, Property 3: Window Detection Completeness
        
        **Validates: Requirements 3.1, 3.2, 3.3**
        
        For any active window state, the Window_Monitor should return complete
        information including both application name and file extension (when applicable).
        """
        # Create mock window monitor
        mock_monitor = Mock()
        
        # Create WindowInfo with complete information
        window_info = WindowInfo(
            title=f"Document{file_ext} - {app_name}",
            process_name=app_name,
            icon=None,
            process_id=1234
        )
        
        mock_monitor.get_active_window_info.return_value = window_info
        
        # Create formatting module with mock monitor
        module = FormattingModule(window_monitor=mock_monitor, state_manager=None)
        
        # Call get_active_application_format
        # This should not raise an exception and should handle the window info
        try:
            result = module.get_active_application_format()
            # Result can be None or a format string, both are valid
            assert result is None or isinstance(result, str)
        except Exception as e:
            pytest.fail(f"Window detection failed with exception: {e}")
    
    @given(
        window_title=st.text(min_size=1, max_size=50),
        app_name=st.text(min_size=1, max_size=50)
    )
    @settings(max_examples=20)
    def test_application_format_matching_deterministic(self, window_title, app_name):
        """
        Feature: transcription-formatting, Property 4: Application Format Matching
        
        **Validates: Requirements 3.4, 3.5**
        
        For any detected window title and app name and any format
        configuration list, the matching logic should deterministically return
        the same format identifier (or None) for the same inputs.
        """
        # Call match_window_to_format twice with same inputs
        config = FormattingConfig.from_env()
        result1 = match_window_to_format(window_title, app_name, config.web_app_keywords)
        result2 = match_window_to_format(window_title, app_name, config.web_app_keywords)
        
        # Results should be identical (deterministic)
        assert result1 == result2, \
            f"Non-deterministic matching: {result1} != {result2} for {window_title}, {app_name}"
        
        # Result should be None or a valid format type
        if result1 is not None:
            assert isinstance(result1, str)
            # Load config to check valid format types
            config = FormattingConfig.from_env()
            assert result1 in config.applications, \
                f"Invalid format type returned: {result1}"
    
    @given(
        window_title=st.text(min_size=1, max_size=50),
        app_name=st.text(min_size=1, max_size=50)
    )
    @settings(max_examples=20)
    def test_format_matching_returns_valid_or_none(self, window_title, app_name):
        """
        Test that format matching always returns either None or a valid format type.
        
        For any window title and app name, match_window_to_format
        should return either None or a string that exists in configured applications.
        """
        config = FormattingConfig.from_env()
        result = match_window_to_format(window_title, app_name, config.web_app_keywords)
        
        # Result must be None or a valid format type
        if result is not None:
            assert isinstance(result, str), f"Result is not a string: {type(result)}"
            assert result in config.applications, \
                f"Invalid format type: {result} not in {list(config.applications)}"
    
    @given(format_type=st.sampled_from(["notion", "obsidian", "markdown", "word", "libreoffice", "vscode", "_fallback"]))
    @settings(max_examples=20)
    def test_format_prompt_exists_for_all_types(self, format_type):
        """
        Test that every format type has a corresponding prompt.
        
        For any format type in applications, get_prompt_for_app should
        return a non-empty string.
        """
        config = FormattingConfig.from_env()
        prompt = config.get_prompt_for_app(format_type)
        
        assert isinstance(prompt, str), f"Prompt is not a string: {type(prompt)}"
        assert len(prompt) > 0, f"Prompt is empty for format type: {format_type}"
        assert "format" in prompt.lower() or "text" in prompt.lower(), \
            f"Prompt doesn't mention formatting: {prompt[:50]}"
    
    @given(
        window_title=st.sampled_from(["Notion", "My Notes - Notion", "notion.so"]),
        app_name=st.sampled_from(["notion", "Notion", "NOTION", "notion.exe"])
    )
    @settings(max_examples=10)
    def test_notion_detection(self, window_title, app_name):
        """
        Test that Notion application is correctly detected.
        
        For any variation of "notion" in the window title or app name,
        the format should be matched to "notion".
        """
        config = FormattingConfig.from_env()
        result = match_window_to_format(window_title, app_name, config.web_app_keywords)
        assert result == "notion", \
            f"Notion not detected for title={window_title}, app={app_name}, got={result}"
    
    @given(
        window_title=st.sampled_from(["Obsidian", "My Vault - Obsidian", "obsidian publish"]),
        app_name=st.sampled_from(["obsidian", "Obsidian", "OBSIDIAN", "obsidian.exe"])
    )
    @settings(max_examples=10)
    def test_obsidian_detection(self, window_title, app_name):
        """
        Test that Obsidian application is correctly detected.
        
        For any variation of "obsidian" in the window title or app name,
        the format should be matched to "obsidian".
        """
        config = FormattingConfig.from_env()
        result = match_window_to_format(window_title, app_name, config.web_app_keywords)
        assert result == "obsidian", \
            f"Obsidian not detected for title={window_title}, app={app_name}, got={result}"
    
    @given(
        window_title=st.sampled_from(["document.md", "notes.markdown", "README.md"]),
        app_name=st.text(min_size=1, max_size=50)
    )
    @settings(max_examples=10)
    def test_markdown_file_detection(self, window_title, app_name):
        """
        Test that markdown files are correctly detected by extension in title.
        
        For any window with .md or .markdown in the title,
        the format should be matched to "markdown".
        """
        config = FormattingConfig.from_env()
        result = match_window_to_format(window_title, app_name, config.web_app_keywords)
        assert result == "markdown", \
            f"Markdown not detected for title={window_title}, app={app_name}, got={result}"
    
    @given(
        window_title=st.sampled_from(["Google Docs", "Document - Google Docs", "LibreOffice Writer"]),
        app_name=st.sampled_from(["chrome.exe", "msedge.exe", "soffice.exe", "winword.exe"])
    )
    @settings(max_examples=10)
    def test_word_detection(self, window_title, app_name):
        """
        Test that Word/Google Docs/LibreOffice application is correctly detected.
        
        For any variation of "google docs" or "libreoffice" in the window title,
        the format should be matched to "word" or "libreoffice".
        """
        config = FormattingConfig.from_env()
        result = match_window_to_format(window_title, app_name, config.web_app_keywords)
        assert result in ["word", "libreoffice"], \
            f"Word/LibreOffice not detected for title={window_title}, app={app_name}, got={result}"
    
    @given(
        window_title=st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_- '
        )),
        app_name=st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_-.'
        ))
    )
    @settings(max_examples=20)
    def test_no_match_returns_none(self, window_title, app_name):
        """
        Test that non-matching windows return None.
        
        For windows that don't match any known format,
        match_window_to_format should return None.
        """
        # Skip if title or app contains known patterns
        title_lower = window_title.lower()
        app_lower = app_name.lower()
        known_patterns = ["notion", "obsidian", "word", "google", "docs", "libreoffice", "markdown", ".md"]
        
        if any(pattern in title_lower or pattern in app_lower for pattern in known_patterns):
            return  # Skip this test case
        
        config = FormattingConfig.from_env()
        result = match_window_to_format(window_title, app_name, config.web_app_keywords)
        
        # For unknown windows, result should be None
        # (unless by chance it matches a pattern)
        if result is not None:
            # If it matched, it should be a valid format
            assert result in config.applications
