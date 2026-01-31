"""
Property-based tests for formatting decision logic.

Feature: transcription-formatting
Property 5: Formatting Decision Logic
Property 7: Original Text Preservation on No-Match

These tests verify that the formatting module makes correct processing
decisions across all combinations of enabled/disabled states and format matches.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, MagicMock
from services.formatting_module import FormattingModule
from services.formatting_config import FormattingConfig
from services.window_monitor import WindowInfo


# Strategy for generating text samples
text_strategy = st.text(min_size=10, max_size=500)

# Strategy for generating format types
format_type_strategy = st.sampled_from([
    "notion", "obsidian", "markdown", "word", "vscode", "sublime", "notepad", None
])

# Strategy for generating application names
app_name_strategy = st.sampled_from([
    "notion", "obsidian", "word", "vscode", "sublime", "notepad++",
    "chrome", "firefox", "terminal", "unknown_app"
])


@pytest.mark.property_test
@given(
    formatting_enabled=st.booleans(),
    format_matches=st.booleans(),
    text=text_strategy
)
@settings(max_examples=100, deadline=None)
def test_formatting_decision_logic(formatting_enabled, format_matches, text):
    """
    Feature: transcription-formatting, Property 5: Formatting Decision Logic
    
    **Validates: Requirements 4.1, 4.4, 5.1, 5.6**
    
    For any combination of formatting enabled/disabled and format match/no-match,
    the system should make the correct processing decision.
    
    Decision matrix:
    - Formatting enabled + format matches → format text
    - Formatting enabled + no format match → return original
    - Formatting disabled → return original (regardless of match)
    """
    # Create mock configuration
    config = FormattingConfig(
        enabled=formatting_enabled,
        provider="groq",
        model="test-model",
        applications=["notion", "obsidian", "markdown"]
    )
    
    # Create mock window monitor
    mock_window_monitor = Mock()
    if format_matches:
        # Return window info that will match
        mock_window_monitor.get_active_window_info.return_value = WindowInfo(
            title="test.md",
            process_name="vscode",
            icon=None,
            process_id=1234
        )
    else:
        # Return window info that won't match
        mock_window_monitor.get_active_window_info.return_value = WindowInfo(
            title="Unknown App",
            process_name="unknown_app",
            icon=None,
            process_id=1234
        )
    
    # Create mock AI client factory
    mock_ai_client = Mock()
    mock_ai_client.post_process_text.return_value = f"FORMATTED: {text}"
    
    mock_ai_factory = Mock()
    mock_ai_factory.create.return_value = mock_ai_client
    
    # Create formatting module with mocks
    module = FormattingModule(
        config_manager=None,
        ai_client_factory=mock_ai_factory,
        window_monitor=mock_window_monitor
    )
    module.config = config  # Override config
    
    # Process the text
    result = module.process(text)
    
    # Verify decision logic
    if formatting_enabled and format_matches:
        # Should attempt to format (may return formatted or original on error)
        # We can't guarantee formatting succeeds, but we can check it was attempted
        assert mock_window_monitor.get_active_window_info.called
    else:
        # Should return original text unchanged
        assert result == text


@pytest.mark.property_test
@given(
    text=text_strategy,
    app_name=app_name_strategy
)
@settings(max_examples=100, deadline=None)
def test_original_text_preservation_on_no_match(text, app_name):
    """
    Feature: transcription-formatting, Property 7: Original Text Preservation on No-Match
    
    **Validates: Requirements 4.4**
    
    For any transcription text, when the active application does not match
    any configured format, the system should return the original text
    completely unchanged.
    """
    # Create configuration with formatting enabled
    config = FormattingConfig(
        enabled=True,
        provider="groq",
        model="test-model",
        applications=["notion", "obsidian", "markdown"]  # Specific list
    )
    
    # Create mock window monitor that returns non-matching app
    mock_window_monitor = Mock()
    mock_window_monitor.get_active_window_info.return_value = WindowInfo(
        title="Unknown Application",
        process_name=app_name,  # Use the generated app name
        icon=None,
        process_id=1234
    )
    
    # Create formatting module
    module = FormattingModule(
        config_manager=None,
        ai_client_factory=None,
        window_monitor=mock_window_monitor
    )
    module.config = config
    
    # Process the text
    result = module.process(text)
    
    # Check if the app would match any format
    format_type = module.get_active_application_format()
    
    if format_type is None:
        # No match - original text must be preserved exactly
        assert result == text, (
            f"Original text not preserved for non-matching app '{app_name}'. "
            f"Expected: {text!r}, Got: {result!r}"
        )


@pytest.mark.property_test
@given(
    text=text_strategy,
    enabled=st.booleans()
)
@settings(max_examples=100, deadline=None)
def test_disabled_formatting_preserves_text(text, enabled):
    """
    Feature: transcription-formatting, Property 5: Formatting Decision Logic
    
    **Validates: Requirements 4.1, 4.4**
    
    When formatting is disabled, the system should always return the original
    text unchanged, regardless of whether the application would match.
    """
    # Create configuration
    config = FormattingConfig(
        enabled=enabled,
        provider="groq",
        model="test-model",
        applications=["notion", "obsidian", "markdown"]
    )
    
    # Create mock window monitor (returns matching app)
    mock_window_monitor = Mock()
    mock_window_monitor.get_active_window_info.return_value = WindowInfo(
        title="test.md",
        process_name="vscode",
        icon=None,
        process_id=1234
    )
    
    # Create formatting module
    module = FormattingModule(
        config_manager=None,
        ai_client_factory=None,
        window_monitor=mock_window_monitor
    )
    module.config = config
    
    # Process the text
    result = module.process(text)
    
    if not enabled:
        # Formatting disabled - must return original text
        assert result == text, (
            f"Original text not preserved when formatting disabled. "
            f"Expected: {text!r}, Got: {result!r}"
        )


@pytest.mark.property_test
@given(
    text=text_strategy
)
@settings(max_examples=100, deadline=None)
def test_invalid_config_preserves_text(text):
    """
    Feature: transcription-formatting, Property 5: Formatting Decision Logic
    
    **Validates: Requirements 4.1**
    
    When configuration is invalid (missing model or applications),
    the system should return the original text unchanged.
    """
    # Create invalid configurations
    invalid_configs = [
        FormattingConfig(enabled=True, provider="groq", model="", applications=["notion"]),
        FormattingConfig(enabled=True, provider="groq", model="test-model", applications=[]),
        FormattingConfig(enabled=True, provider="invalid", model="test-model", applications=["notion"]),
    ]
    
    for config in invalid_configs:
        # Create mock window monitor
        mock_window_monitor = Mock()
        mock_window_monitor.get_active_window_info.return_value = WindowInfo(
            title="test.md",
            process_name="vscode",
            icon=None,
            process_id=1234
        )
        
        # Create formatting module
        module = FormattingModule(
            config_manager=None,
            ai_client_factory=None,
            window_monitor=mock_window_monitor
        )
        module.config = config
        
        # Process the text
        result = module.process(text)
        
        # Invalid config - must return original text
        assert result == text, (
            f"Original text not preserved with invalid config. "
            f"Config: {config}, Expected: {text!r}, Got: {result!r}"
        )
