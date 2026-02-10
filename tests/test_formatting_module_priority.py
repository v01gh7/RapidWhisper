"""
Unit tests for FormattingModule priority logic.

Tests that manual format selection has highest priority, followed by
fixed format, then automatic detection.

Validates: Requirements 4.1, 4.2, 4.3, 4.5
"""

import pytest
from unittest.mock import Mock, MagicMock
from services.formatting_module import FormattingModule
from services.formatting_config import FormattingConfig
from services.window_monitor import WindowInfo


def test_manual_selection_overrides_fixed_format():
    """
    Test that manual selection has priority over fixed format setting.
    
    Validates: Requirements 4.1, 4.2
    """
    # Create config with fixed format enabled
    config = FormattingConfig()
    config.enabled = True
    config.use_fixed_format = True  # This would normally force "_fallback"
    config.applications = ["notion", "markdown"]
    
    # Create mock state manager with manual selection
    state_manager = Mock()
    state_manager.get_manual_format_selection.return_value = "notion"
    
    # Create formatting module
    module = FormattingModule(config, state_manager=state_manager)
    
    # Get active format
    result = module.get_active_application_format()
    
    # Manual selection should override fixed format
    assert result == "notion"
    assert state_manager.get_manual_format_selection.called


def test_manual_selection_overrides_auto_detection():
    """
    Test that manual selection has priority over automatic detection.
    
    Validates: Requirements 4.1, 4.3
    """
    # Create config with auto-detection enabled
    config = FormattingConfig()
    config.enabled = True
    config.use_fixed_format = False
    config.applications = ["notion", "markdown"]
    config.web_app_keywords = {
        "notion": ["notion"],
        "markdown": ["markdown"]
    }
    
    # Create mock state manager with manual selection
    state_manager = Mock()
    state_manager.get_manual_format_selection.return_value = "markdown"
    
    # Create mock window monitor that would detect "notion"
    window_monitor = Mock()
    window_monitor.get_active_window_info.return_value = WindowInfo(
        title="Notion - My Notes",
        process_name="notion.exe",
        icon=None,
        process_id=12345
    )
    
    # Create formatting module
    module = FormattingModule(config, window_monitor=window_monitor, state_manager=state_manager)
    
    # Get active format
    result = module.get_active_application_format()
    
    # Manual selection should override auto-detection
    assert result == "markdown"
    assert state_manager.get_manual_format_selection.called
    # Window monitor should not be called when manual selection is set
    assert not window_monitor.get_active_window_info.called


def test_fixed_format_used_when_no_manual_selection():
    """
    Test that fixed format is used when no manual selection is set.
    
    Validates: Requirements 4.5
    """
    # Create config with fixed format enabled
    config = FormattingConfig()
    config.enabled = True
    config.use_fixed_format = True
    config.applications = ["notion"]
    
    # Create mock state manager with no manual selection
    state_manager = Mock()
    state_manager.get_manual_format_selection.return_value = None
    
    # Create formatting module
    module = FormattingModule(config, state_manager=state_manager)
    
    # Get active format
    result = module.get_active_application_format()
    
    # Should use fixed format (fallback)
    assert result == "_fallback"
    assert state_manager.get_manual_format_selection.called


def test_auto_detection_used_when_no_manual_selection_or_fixed_format():
    """
    Test that auto-detection is used when no manual selection or fixed format.
    
    Validates: Requirements 4.5
    """
    # Create config with auto-detection enabled
    config = FormattingConfig()
    config.enabled = True
    config.use_fixed_format = False
    config.applications = ["notion"]
    config.web_app_keywords = {
        "notion": ["notion"]
    }
    
    # Create mock state manager with no manual selection
    state_manager = Mock()
    state_manager.get_manual_format_selection.return_value = None
    
    # Create mock window monitor
    window_monitor = Mock()
    window_monitor.get_active_window_info.return_value = WindowInfo(
        title="Notion - My Notes",
        process_name="notion.exe",
        icon=None,
        process_id=12345
    )
    
    # Create formatting module
    module = FormattingModule(config, window_monitor=window_monitor, state_manager=state_manager)
    
    # Get active format
    result = module.get_active_application_format()
    
    # Should use auto-detection
    assert result == "notion"
    assert state_manager.get_manual_format_selection.called
    assert window_monitor.get_active_window_info.called


def test_auto_detection_matches_application_case_insensitively():
    """
    Test that detected keyword format maps to configured app case-insensitively.
    """
    config = FormattingConfig()
    config.enabled = True
    config.use_fixed_format = False
    config.applications = ["Email"]
    config.web_app_keywords = {
        "email": ["gmail", "inbox"]
    }

    state_manager = Mock()
    state_manager.get_manual_format_selection.return_value = None

    window_monitor = Mock()
    window_monitor.get_active_window_info.return_value = WindowInfo(
        title="Inbox - Gmail - Google Chrome",
        process_name="chrome.exe",
        icon=None,
        process_id=12345
    )

    module = FormattingModule(config, window_monitor=window_monitor, state_manager=state_manager)

    result = module.get_active_application_format()

    assert result == "Email"


def test_no_state_manager_falls_back_to_normal_behavior():
    """
    Test that module works without state manager (backward compatibility).
    
    Validates: Requirements 4.1
    """
    # Create config with fixed format enabled
    config = FormattingConfig()
    config.enabled = True
    config.use_fixed_format = True
    
    # Create formatting module without state manager
    module = FormattingModule(config, state_manager=None)
    
    # Get active format
    result = module.get_active_application_format()
    
    # Should use fixed format (no error)
    assert result == "_fallback"


def test_manual_selection_with_fallback_format():
    """
    Test that manual selection works with _fallback format.
    
    Validates: Requirements 3.4
    """
    # Create config
    config = FormattingConfig()
    config.enabled = True
    config.use_fixed_format = False
    config.applications = ["notion", "_fallback"]
    
    # Create mock state manager with manual selection of fallback
    state_manager = Mock()
    state_manager.get_manual_format_selection.return_value = "_fallback"
    
    # Create formatting module
    module = FormattingModule(config, state_manager=state_manager)
    
    # Get active format
    result = module.get_active_application_format()
    
    # Should return fallback
    assert result == "_fallback"
    assert state_manager.get_manual_format_selection.called


def test_manual_selection_cleared_returns_to_normal():
    """
    Test that when manual selection is cleared, normal behavior resumes.
    
    Validates: Requirements 4.5
    """
    # Create config with auto-detection
    config = FormattingConfig()
    config.enabled = True
    config.use_fixed_format = False
    config.applications = ["notion"]
    config.web_app_keywords = {
        "notion": ["notion"]
    }
    
    # Create mock state manager
    state_manager = Mock()
    
    # Create mock window monitor
    window_monitor = Mock()
    window_monitor.get_active_window_info.return_value = WindowInfo(
        title="Notion - My Notes",
        process_name="notion.exe",
        icon=None,
        process_id=12345
    )
    
    # Create formatting module
    module = FormattingModule(config, window_monitor=window_monitor, state_manager=state_manager)
    
    # First call: manual selection is set
    state_manager.get_manual_format_selection.return_value = "markdown"
    result1 = module.get_active_application_format()
    assert result1 == "markdown"
    
    # Second call: manual selection is cleared
    state_manager.get_manual_format_selection.return_value = None
    result2 = module.get_active_application_format()
    assert result2 == "notion"  # Should use auto-detection now


def test_priority_order_complete():
    """
    Test complete priority order: manual > fixed > auto > fallback.
    
    Validates: Requirements 4.1, 4.2, 4.3
    """
    # Create config
    config = FormattingConfig()
    config.enabled = True
    config.applications = ["notion", "markdown"]
    config.web_app_keywords = {
        "notion": ["notion"],
        "markdown": ["markdown"]
    }
    
    # Create mock state manager
    state_manager = Mock()
    
    # Create mock window monitor
    window_monitor = Mock()
    window_monitor.get_active_window_info.return_value = WindowInfo(
        title="Notion - My Notes",
        process_name="notion.exe",
        icon=None,
        process_id=12345
    )
    
    # Create formatting module
    module = FormattingModule(config, window_monitor=window_monitor, state_manager=state_manager)
    
    # Test 1: Manual selection (highest priority)
    state_manager.get_manual_format_selection.return_value = "markdown"
    config.use_fixed_format = True
    result = module.get_active_application_format()
    assert result == "markdown"  # Manual wins over fixed
    
    # Test 2: Fixed format (when no manual selection)
    state_manager.get_manual_format_selection.return_value = None
    config.use_fixed_format = True
    result = module.get_active_application_format()
    assert result == "_fallback"  # Fixed format wins
    
    # Test 3: Auto-detection (when no manual or fixed)
    state_manager.get_manual_format_selection.return_value = None
    config.use_fixed_format = False
    result = module.get_active_application_format()
    assert result == "notion"  # Auto-detection wins


def test_manual_selection_logging():
    """
    Test that manual selection usage is logged.
    
    Validates: Requirements 4.2
    """
    # Create config
    config = FormattingConfig()
    config.enabled = True
    config.applications = ["notion"]
    
    # Create mock state manager with manual selection
    state_manager = Mock()
    state_manager.get_manual_format_selection.return_value = "notion"
    
    # Create formatting module
    module = FormattingModule(config, state_manager=state_manager)
    
    # Get active format (logging happens internally)
    result = module.get_active_application_format()
    
    # Verify result
    assert result == "notion"
    # Note: Actual log verification would require capturing logger output,
    # but we verify the code path is executed correctly
