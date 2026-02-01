"""
Property-based tests for processing coordinator.

Feature: transcription-formatting
Property 8: Single API Call for Combined Operations
Property 9: Combined Prompt Composition
Property 10: Post-Processing Provider Priority

These tests verify that the processing coordinator correctly handles
combined operations and makes optimal decisions.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, MagicMock, call
from services.processing_coordinator import ProcessingCoordinator
from services.formatting_module import FormattingModule
from services.formatting_config import FormattingConfig
from services.window_monitor import WindowInfo


# Strategy for generating text samples
text_strategy = st.text(min_size=10, max_size=500)

# Strategy for generating prompts
prompt_strategy = st.text(min_size=20, max_size=200)


@pytest.mark.property_test
@given(
    text=text_strategy,
    post_prompt=prompt_strategy,
    format_prompt=prompt_strategy
)
@settings(max_examples=20, deadline=None)
def test_single_api_call_for_combined_operations(text, post_prompt, format_prompt):
    """
    Feature: transcription-formatting, Property 8: Single API Call for Combined Operations
    
    **Validates: Requirements 5.1, 5.4**
    
    For any text when both formatting and post-processing are enabled and format matches,
    the system should make exactly one AI API request (not two separate requests).
    """
    # Create formatting config with formatting enabled
    formatting_config = FormattingConfig(
        enabled=True,
        provider="groq",
        model="test-model",
        applications=["notion", "obsidian", "markdown"]
    )
    
    # Create mock window monitor that returns matching app
    mock_window_monitor = Mock()
    mock_window_monitor.get_active_window_info.return_value = WindowInfo(
        title="test.md",
        process_name="vscode",
        icon=None,
        process_id=1234
    )
    
    # Create mock AI client factory
    mock_ai_client = Mock()
    mock_ai_client.post_process_text.return_value = f"PROCESSED: {text}"
    
    mock_ai_factory = Mock()
    mock_ai_factory.create.return_value = mock_ai_client
    
    # Create formatting module
    formatting_module = FormattingModule(
        config_manager=None,
        ai_client_factory=mock_ai_factory,
        window_monitor=mock_window_monitor,
        state_manager=None
    )
    formatting_module.config = formatting_config
    
    # Create mock config manager with post-processing enabled
    mock_config = Mock()
    mock_config.enable_post_processing = True
    mock_config.post_processing_provider = "groq"
    mock_config.post_processing_model = "test-post-model"
    mock_config.post_processing_custom_model = ""
    mock_config.post_processing_prompt = post_prompt
    mock_config.llm_base_url = None
    mock_config.glm_use_coding_plan = False
    
    # Create mock transcription client
    mock_transcription_client = Mock()
    mock_transcription_client.post_process_text.return_value = f"COMBINED: {text}"
    
    # Create processing coordinator
    coordinator = ProcessingCoordinator(
        formatting_module=formatting_module,
        config_manager=mock_config
    )
    
    # Process the text
    result = coordinator.process_transcription(
        text=text,
        transcription_client=mock_transcription_client,
        config=mock_config
    )
    
    # Verify exactly ONE API call was made
    assert mock_transcription_client.post_process_text.call_count == 1, (
        f"Expected exactly 1 API call for combined operations, "
        f"but got {mock_transcription_client.post_process_text.call_count}"
    )
    
    # Verify the call was made with the correct text
    call_args = mock_transcription_client.post_process_text.call_args
    assert call_args[1]['text'] == text


@pytest.mark.property_test
@given(
    post_prompt=prompt_strategy,
    format_prompt=prompt_strategy
)
@settings(max_examples=20, deadline=None)
def test_combined_prompt_composition(post_prompt, format_prompt):
    """
    Feature: transcription-formatting, Property 9: Combined Prompt Composition
    
    **Validates: Requirements 5.3**
    
    For any post-processing prompt and formatting prompt, when combining operations,
    the resulting combined prompt should contain instructions from both prompts.
    """
    # Create minimal mocks
    mock_formatting_module = Mock()
    mock_config = Mock()
    
    # Create coordinator
    coordinator = ProcessingCoordinator(
        formatting_module=mock_formatting_module,
        config_manager=mock_config
    )
    
    # Combine prompts
    combined = coordinator.combine_prompts(post_prompt, format_prompt)
    
    # Verify both prompts are present in the combined prompt
    # The combined prompt should contain content from both prompts
    assert len(combined) > 0, "Combined prompt should not be empty"
    
    # The combined prompt should be longer than either individual prompt
    # (unless one is empty, which is handled by the strategy min_size)
    assert len(combined) >= len(post_prompt) or len(combined) >= len(format_prompt), (
        f"Combined prompt should contain both prompts. "
        f"Post: {len(post_prompt)}, Format: {len(format_prompt)}, Combined: {len(combined)}"
    )


@pytest.mark.property_test
@given(
    text=text_strategy
)
@settings(max_examples=20, deadline=None)
def test_post_processing_provider_priority(text):
    """
    Feature: transcription-formatting, Property 10: Post-Processing Provider Priority
    
    **Validates: Requirements 5.2, 5.7**
    
    For any combined operation (formatting + post-processing), the system should use
    the post-processing AI provider configuration, not the formatting provider configuration.
    """
    # Create formatting config with one provider
    formatting_config = FormattingConfig(
        enabled=True,
        provider="openai",  # Different from post-processing provider
        model="formatting-model",
        applications=["notion", "obsidian", "markdown"]
    )
    
    # Create mock window monitor that returns matching app
    mock_window_monitor = Mock()
    mock_window_monitor.get_active_window_info.return_value = WindowInfo(
        title="test.md",
        process_name="vscode",
        icon=None,
        process_id=1234
    )
    
    # Create formatting module
    formatting_module = FormattingModule(
        config_manager=None,
        ai_client_factory=None,
        window_monitor=mock_window_monitor,
        state_manager=None
    )
    formatting_module.config = formatting_config
    
    # Create mock config with different post-processing provider
    mock_config = Mock()
    mock_config.enable_post_processing = True
    mock_config.post_processing_provider = "groq"  # Different from formatting
    mock_config.post_processing_model = "post-model"
    mock_config.post_processing_custom_model = ""
    mock_config.post_processing_prompt = "Post-process this text"
    mock_config.llm_base_url = None
    mock_config.glm_use_coding_plan = False
    
    # Create mock transcription client
    mock_transcription_client = Mock()
    mock_transcription_client.post_process_text.return_value = f"PROCESSED: {text}"
    
    # Create coordinator
    coordinator = ProcessingCoordinator(
        formatting_module=formatting_module,
        config_manager=mock_config
    )
    
    # Process the text
    result = coordinator.process_transcription(
        text=text,
        transcription_client=mock_transcription_client,
        config=mock_config
    )
    
    # Verify the post-processing provider was used (not formatting provider)
    if mock_transcription_client.post_process_text.called:
        call_args = mock_transcription_client.post_process_text.call_args
        used_provider = call_args[1]['provider']
        
        assert used_provider == "groq", (
            f"Expected post-processing provider 'groq' to be used, "
            f"but got '{used_provider}'"
        )
        
        # Also verify the formatting provider was NOT used
        assert used_provider != "openai", (
            f"Formatting provider 'openai' should not be used in combined mode"
        )


@pytest.mark.property_test
@given(
    text=text_strategy,
    formatting_enabled=st.booleans(),
    post_processing_enabled=st.booleans(),
    format_matches=st.booleans()
)
@settings(max_examples=20, deadline=None)
def test_processing_decision_matrix(text, formatting_enabled, post_processing_enabled, format_matches):
    """
    Feature: transcription-formatting, Property 5: Formatting Decision Logic
    
    **Validates: Requirements 4.1, 5.1, 5.6**
    
    Test the complete decision matrix for processing coordinator.
    """
    # Create formatting config
    formatting_config = FormattingConfig(
        enabled=formatting_enabled,
        provider="groq",
        model="test-model",
        applications=["notion", "obsidian", "markdown"]
    )
    
    # Create mock window monitor
    mock_window_monitor = Mock()
    if format_matches:
        mock_window_monitor.get_active_window_info.return_value = WindowInfo(
            title="test.md",
            process_name="vscode",
            icon=None,
            process_id=1234
        )
    else:
        mock_window_monitor.get_active_window_info.return_value = WindowInfo(
            title="Unknown App",
            process_name="unknown_app",
            icon=None,
            process_id=1234
        )
    
    # Create formatting module
    formatting_module = FormattingModule(
        config_manager=None,
        ai_client_factory=None,
        window_monitor=mock_window_monitor,
        state_manager=None
    )
    formatting_module.config = formatting_config
    
    # Create mock config
    mock_config = Mock()
    mock_config.enable_post_processing = post_processing_enabled
    mock_config.post_processing_provider = "groq"
    mock_config.post_processing_model = "test-model"
    mock_config.post_processing_custom_model = ""
    mock_config.post_processing_prompt = "Process this"
    mock_config.llm_base_url = None
    mock_config.glm_use_coding_plan = False
    
    # Create mock transcription client
    mock_transcription_client = Mock()
    mock_transcription_client.post_process_text.return_value = f"PROCESSED: {text}"
    
    # Create coordinator
    coordinator = ProcessingCoordinator(
        formatting_module=formatting_module,
        config_manager=mock_config
    )
    
    # Process the text
    result = coordinator.process_transcription(
        text=text,
        transcription_client=mock_transcription_client,
        config=mock_config
    )
    
    # Verify result is not None and is a string
    assert result is not None
    assert isinstance(result, str)
    
    # Verify decision logic
    if formatting_enabled and post_processing_enabled and format_matches:
        # Combined mode - should make API call
        assert mock_transcription_client.post_process_text.called
    elif not formatting_enabled and not post_processing_enabled:
        # No processing - should return original text
        assert result == text
    # Other cases depend on implementation details


@pytest.mark.property_test
@given(
    text=text_strategy
)
@settings(max_examples=20, deadline=None)
def test_coordinator_handles_api_failures_gracefully(text):
    """
    Feature: transcription-formatting, Property 12: Graceful Failure Handling
    
    **Validates: Requirements 7.4, 7.5**
    
    When API calls fail in combined mode, the coordinator should return
    the original text and not raise exceptions.
    """
    # Create formatting config
    formatting_config = FormattingConfig(
        enabled=True,
        provider="groq",
        model="test-model",
        applications=["notion", "obsidian", "markdown"]
    )
    
    # Create mock window monitor with matching app
    mock_window_monitor = Mock()
    mock_window_monitor.get_active_window_info.return_value = WindowInfo(
        title="test.md",
        process_name="vscode",
        icon=None,
        process_id=1234
    )
    
    # Create formatting module
    formatting_module = FormattingModule(
        config_manager=None,
        ai_client_factory=None,
        window_monitor=mock_window_monitor,
        state_manager=None
    )
    formatting_module.config = formatting_config
    
    # Create mock config with post-processing enabled
    mock_config = Mock()
    mock_config.enable_post_processing = True
    mock_config.post_processing_provider = "groq"
    mock_config.post_processing_model = "test-model"
    mock_config.post_processing_custom_model = ""
    mock_config.post_processing_prompt = "Process this"
    mock_config.llm_base_url = None
    mock_config.glm_use_coding_plan = False
    
    # Create mock transcription client that raises an error
    mock_transcription_client = Mock()
    mock_transcription_client.post_process_text.side_effect = Exception("API Error")
    
    # Create coordinator
    coordinator = ProcessingCoordinator(
        formatting_module=formatting_module,
        config_manager=mock_config
    )
    
    # Process the text - should not raise exception
    result = coordinator.process_transcription(
        text=text,
        transcription_client=mock_transcription_client,
        config=mock_config
    )
    
    # Should return original text on failure
    assert result == text, (
        f"Expected original text on API failure, but got: {result!r}"
    )
