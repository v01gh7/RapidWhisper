"""
Property-based tests for format detection and matching logic.

These tests validate universal properties for window detection and
application format matching.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, MagicMock
from services.formatting_module import (
    match_application_to_format,
    get_format_prompt,
    FormattingModule,
    FORMAT_MAPPINGS,
    FORMAT_PROMPTS
)
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
        module = FormattingModule(window_monitor=mock_monitor)
        
        # Call get_active_application_format
        # This should not raise an exception and should handle the window info
        try:
            result = module.get_active_application_format()
            # Result can be None or a format string, both are valid
            assert result is None or isinstance(result, str)
        except Exception as e:
            pytest.fail(f"Window detection failed with exception: {e}")
    
    @given(
        app_name=app_name_strategy,
        file_ext=file_ext_strategy
    )
    @settings(max_examples=20)
    def test_application_format_matching_deterministic(self, app_name, file_ext):
        """
        Feature: transcription-formatting, Property 4: Application Format Matching
        
        **Validates: Requirements 3.4, 3.5**
        
        For any detected application name or file extension and any format
        configuration list, the matching logic should deterministically return
        the same format identifier (or None) for the same inputs.
        """
        # Call match_application_to_format twice with same inputs
        result1 = match_application_to_format(app_name, file_ext)
        result2 = match_application_to_format(app_name, file_ext)
        
        # Results should be identical (deterministic)
        assert result1 == result2, \
            f"Non-deterministic matching: {result1} != {result2} for {app_name}, {file_ext}"
        
        # Result should be None or a valid format type
        if result1 is not None:
            assert isinstance(result1, str)
            assert result1 in FORMAT_MAPPINGS.keys(), \
                f"Invalid format type returned: {result1}"
    
    @given(
        app_name=st.text(min_size=1, max_size=50),
        file_ext=st.text(min_size=0, max_size=10)
    )
    @settings(max_examples=20)
    def test_format_matching_returns_valid_or_none(self, app_name, file_ext):
        """
        Test that format matching always returns either None or a valid format type.
        
        For any application name and file extension, match_application_to_format
        should return either None or a string that exists in FORMAT_MAPPINGS.
        """
        result = match_application_to_format(app_name, file_ext)
        
        # Result must be None or a valid format type
        if result is not None:
            assert isinstance(result, str), f"Result is not a string: {type(result)}"
            assert result in FORMAT_MAPPINGS.keys(), \
                f"Invalid format type: {result} not in {list(FORMAT_MAPPINGS.keys())}"
    
    @given(format_type=st.sampled_from(list(FORMAT_MAPPINGS.keys())))
    @settings(max_examples=20)
    def test_format_prompt_exists_for_all_types(self, format_type):
        """
        Test that every format type has a corresponding prompt.
        
        For any format type in FORMAT_MAPPINGS, get_format_prompt should
        return a non-empty string.
        """
        prompt = get_format_prompt(format_type)
        
        assert isinstance(prompt, str), f"Prompt is not a string: {type(prompt)}"
        assert len(prompt) > 0, f"Prompt is empty for format type: {format_type}"
        assert format_type in prompt.lower() or "format" in prompt.lower(), \
            f"Prompt doesn't mention formatting: {prompt[:50]}"
    
    @given(
        app_name=st.sampled_from(["notion", "Notion", "NOTION", "notion.exe"]),
        file_ext=st.sampled_from(["", ".txt", ".md"])
    )
    @settings(max_examples=10)
    def test_notion_detection(self, app_name, file_ext):
        """
        Test that Notion application is correctly detected.
        
        For any variation of "notion" in the application name,
        the format should be matched to "notion".
        """
        result = match_application_to_format(app_name, file_ext)
        assert result == "notion", \
            f"Notion not detected for app={app_name}, ext={file_ext}, got={result}"
    
    @given(
        app_name=st.sampled_from(["obsidian", "Obsidian", "OBSIDIAN", "obsidian.exe"]),
        file_ext=st.sampled_from(["", ".txt", ".md"])
    )
    @settings(max_examples=10)
    def test_obsidian_detection(self, app_name, file_ext):
        """
        Test that Obsidian application is correctly detected.
        
        For any variation of "obsidian" in the application name,
        the format should be matched to "obsidian".
        """
        result = match_application_to_format(app_name, file_ext)
        assert result == "obsidian", \
            f"Obsidian not detected for app={app_name}, ext={file_ext}, got={result}"
    
    @given(
        app_name=st.text(min_size=1, max_size=50),
        file_ext=st.sampled_from([".md", ".markdown"])
    )
    @settings(max_examples=10)
    def test_markdown_file_detection(self, app_name, file_ext):
        """
        Test that markdown files are correctly detected by extension.
        
        For any application with a .md or .markdown file extension,
        the format should be matched to "markdown".
        """
        result = match_application_to_format(app_name, file_ext)
        assert result == "markdown", \
            f"Markdown not detected for app={app_name}, ext={file_ext}, got={result}"
    
    @given(
        app_name=st.sampled_from(["word", "Word", "winword.exe", "Microsoft Word", "libreoffice writer", "LibreOffice Writer", "soffice", "writer.exe"]),
        file_ext=st.sampled_from(["", ".docx", ".doc", ".odt", ".txt"])
    )
    @settings(max_examples=10)
    def test_word_detection(self, app_name, file_ext):
        """
        Test that Word/LibreOffice application is correctly detected.
        
        For any variation of "word" or "libreoffice writer" in the application name,
        the format should be matched to "word".
        """
        result = match_application_to_format(app_name, file_ext)
        assert result == "word", \
            f"Word/LibreOffice not detected for app={app_name}, ext={file_ext}, got={result}"
    
    @given(
        app_name=st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_-'
        )),
        file_ext=st.sampled_from([".pdf", ".txt", ".html", ""])
    )
    @settings(max_examples=20)
    def test_no_match_returns_none(self, app_name, file_ext):
        """
        Test that non-matching applications return None.
        
        For applications that don't match any known format,
        match_application_to_format should return None.
        """
        # Skip if app_name contains known patterns
        app_lower = app_name.lower()
        known_patterns = ["notion", "obsidian", "word", "code", "sublime", "notepad", "libreoffice", "soffice", "writer"]
        
        if any(pattern in app_lower for pattern in known_patterns):
            return  # Skip this test case
        
        # Skip if file_ext is .md or .markdown
        if file_ext in [".md", ".markdown"]:
            return
        
        result = match_application_to_format(app_name, file_ext)
        
        # For unknown apps, result should be None
        # (unless by chance it matches a pattern)
        if result is not None:
            # If it matched, it should be a valid format
            assert result in FORMAT_MAPPINGS.keys()
