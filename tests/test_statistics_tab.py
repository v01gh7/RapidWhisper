"""Unit tests for Statistics Tab UI component."""

import pytest
from pathlib import Path
from PyQt6.QtWidgets import QApplication
import sys
import tempfile

from ui.statistics_tab import StatisticsTab, MetricCard
from core.statistics_manager import StatisticsManager, TimePeriod


@pytest.fixture
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def temp_statistics_manager(tmp_path):
    """Create a temporary statistics manager for testing."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return StatisticsManager(config_dir)


def test_metric_card_creation(qapp):
    """Test that MetricCard can be created with label and value."""
    card = MetricCard("Test Label", "Test Value")
    assert card.label_widget.text() == "Test Label"
    assert card.value_widget.text() == "Test Value"


def test_metric_card_update_value(qapp):
    """Test that MetricCard value can be updated."""
    card = MetricCard("Test Label", "Initial Value")
    card.update_value("Updated Value")
    assert card.value_widget.text() == "Updated Value"


def test_statistics_tab_creation(qapp, temp_statistics_manager):
    """Test that StatisticsTab can be created."""
    tab = StatisticsTab(temp_statistics_manager)
    assert tab.statistics_manager == temp_statistics_manager
    assert len(tab.metric_cards) == 7


def test_statistics_tab_has_all_metric_cards(qapp, temp_statistics_manager):
    """Test that StatisticsTab creates all required metric cards."""
    tab = StatisticsTab(temp_statistics_manager)
    
    expected_cards = [
        'recordings',
        'transcriptions',
        'recording_time',
        'transcribed_time',
        'characters',
        'words',
        'silence'
    ]
    
    for card_name in expected_cards:
        assert card_name in tab.metric_cards
        assert isinstance(tab.metric_cards[card_name], MetricCard)


def test_statistics_tab_period_combo_has_all_options(qapp, temp_statistics_manager):
    """Test that the time period combo box has all required options."""
    tab = StatisticsTab(temp_statistics_manager)
    
    assert tab.period_combo.count() == 5
    assert tab.period_combo.itemData(0) == TimePeriod.TODAY
    assert tab.period_combo.itemData(1) == TimePeriod.LAST_7_DAYS
    assert tab.period_combo.itemData(2) == TimePeriod.LAST_30_DAYS
    assert tab.period_combo.itemData(3) == TimePeriod.LAST_365_DAYS
    assert tab.period_combo.itemData(4) == TimePeriod.ALL_TIME


def test_statistics_tab_default_period_is_last_7_days(qapp, temp_statistics_manager):
    """Test that the default time period is 'Last 7 Days'."""
    tab = StatisticsTab(temp_statistics_manager)
    assert tab.period_combo.currentIndex() == 1
    assert tab.period_combo.currentData() == TimePeriod.LAST_7_DAYS


def test_statistics_tab_initial_metric_values(qapp, temp_statistics_manager):
    """Test that metric cards have appropriate initial values."""
    tab = StatisticsTab(temp_statistics_manager)
    
    # Count metrics should show "0"
    assert tab.metric_cards['recordings'].value_widget.text() == "0"
    assert tab.metric_cards['transcriptions'].value_widget.text() == "0"
    assert tab.metric_cards['characters'].value_widget.text() == "0"
    assert tab.metric_cards['words'].value_widget.text() == "0"
    
    # Time metrics should show "00:00"
    assert tab.metric_cards['recording_time'].value_widget.text() == "00:00"
    assert tab.metric_cards['transcribed_time'].value_widget.text() == "00:00"
    assert tab.metric_cards['silence'].value_widget.text() == "00:00"


# Property-based tests
from hypothesis import given, strategies as st, settings, HealthCheck
import tempfile


# Feature: usage-statistics, Property 9: Duration Formatting
@given(
    seconds=st.floats(min_value=0.0, max_value=36000.0, allow_nan=False, allow_infinity=False)
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_duration_formatting_property(seconds: float):
    """
    **Validates: Requirements 3.5, 7.3, 7.4**
    
    Property: For any duration in seconds, the formatted string should use "MM:SS" format
    when the duration is less than 60 minutes, and "HH:MM" format when the duration is
    60 minutes or more, with proper zero-padding.
    """
    # Create QApplication if needed
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create temporary statistics manager
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "config"
        config_dir.mkdir()
        temp_manager = StatisticsManager(config_dir)
        
        tab = StatisticsTab(temp_manager)
        formatted = tab._format_duration(seconds)
    
    total_seconds = int(seconds)
    
    if total_seconds >= 3600:  # 1 hour or more
        # Should be in HH:MM format
        assert ':' in formatted, f"Duration {seconds}s should contain ':' separator"
        parts = formatted.split(':')
        assert len(parts) == 2, f"Duration {seconds}s should have exactly 2 parts (HH:MM)"
        
        hours_str, minutes_str = parts
        
        # Verify format
        assert len(hours_str) >= 2, f"Hours should be zero-padded: {hours_str}"
        assert len(minutes_str) == 2, f"Minutes should be zero-padded: {minutes_str}"
        
        # Verify values
        hours = int(hours_str)
        minutes = int(minutes_str)
        
        expected_hours = total_seconds // 3600
        expected_minutes = (total_seconds % 3600) // 60
        
        assert hours == expected_hours, (
            f"Hours mismatch for {seconds}s: expected {expected_hours}, got {hours}"
        )
        assert minutes == expected_minutes, (
            f"Minutes mismatch for {seconds}s: expected {expected_minutes}, got {minutes}"
        )
        assert 0 <= minutes < 60, f"Minutes should be 0-59, got {minutes}"
        
    else:  # Less than 1 hour
        # Should be in MM:SS format
        assert ':' in formatted, f"Duration {seconds}s should contain ':' separator"
        parts = formatted.split(':')
        assert len(parts) == 2, f"Duration {seconds}s should have exactly 2 parts (MM:SS)"
        
        minutes_str, secs_str = parts
        
        # Verify format
        assert len(minutes_str) == 2, f"Minutes should be zero-padded: {minutes_str}"
        assert len(secs_str) == 2, f"Seconds should be zero-padded: {secs_str}"
        
        # Verify values
        minutes = int(minutes_str)
        secs = int(secs_str)
        
        expected_minutes = total_seconds // 60
        expected_secs = total_seconds % 60
        
        assert minutes == expected_minutes, (
            f"Minutes mismatch for {seconds}s: expected {expected_minutes}, got {minutes}"
        )
        assert secs == expected_secs, (
            f"Seconds mismatch for {seconds}s: expected {expected_secs}, got {secs}"
        )
        assert 0 <= secs < 60, f"Seconds should be 0-59, got {secs}"


# Feature: usage-statistics, Property 10: Number Formatting
@given(
    number=st.integers(min_value=0, max_value=10000000)
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_number_formatting_property(number: int):
    """
    **Validates: Requirements 7.5**
    
    Property: For any integer count (characters, words), the formatted string should
    include thousand separators (commas) for numbers >= 1000.
    """
    # Create QApplication if needed
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create temporary statistics manager
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "config"
        config_dir.mkdir()
        temp_manager = StatisticsManager(config_dir)
        
        tab = StatisticsTab(temp_manager)
        formatted = tab._format_number(number)
    
    # Remove commas and verify it's the same number
    unformatted = formatted.replace(',', '')
    assert unformatted.isdigit(), f"Formatted number should only contain digits and commas: {formatted}"
    assert int(unformatted) == number, (
        f"Formatted number should represent the same value: {number} != {unformatted}"
    )
    
    # Verify thousand separators for numbers >= 1000
    if number >= 1000:
        assert ',' in formatted, (
            f"Numbers >= 1000 should have thousand separators: {number} formatted as {formatted}"
        )
        
        # Verify correct placement of commas
        # Split by comma and check each group
        parts = formatted.split(',')
        
        # First part can be 1-3 digits
        assert 1 <= len(parts[0]) <= 3, (
            f"First part should be 1-3 digits: {parts[0]} in {formatted}"
        )
        
        # All other parts should be exactly 3 digits
        for i, part in enumerate(parts[1:], 1):
            assert len(part) == 3, (
                f"Part {i} should be exactly 3 digits: {part} in {formatted}"
            )
    else:
        # Numbers < 1000 should not have commas
        assert ',' not in formatted, (
            f"Numbers < 1000 should not have thousand separators: {number} formatted as {formatted}"
        )
    
    # Verify the formatted string matches Python's built-in format
    expected = f"{number:,}"
    assert formatted == expected, (
        f"Formatted number should match Python's format: expected {expected}, got {formatted}"
    )



def test_statistics_tab_displays_data_correctly(qapp, temp_statistics_manager):
    """Test that the statistics tab correctly displays data from the statistics manager."""
    # Track some events
    temp_statistics_manager.track_recording(duration_seconds=125.5)
    temp_statistics_manager.track_recording(duration_seconds=60.0)
    temp_statistics_manager.track_transcription(
        audio_duration_seconds=125.5,
        transcribed_text="This is a test transcription with multiple words."
    )
    temp_statistics_manager.track_silence_removal(removed_duration_seconds=15.3)
    
    # Create the tab
    tab = StatisticsTab(temp_statistics_manager)
    
    # Verify the displayed values
    assert tab.metric_cards['recordings'].value_widget.text() == "2"
    assert tab.metric_cards['transcriptions'].value_widget.text() == "1"
    
    # Total recording time: 125.5 + 60.0 = 185.5 seconds = 3 minutes 5 seconds
    assert tab.metric_cards['recording_time'].value_widget.text() == "03:05"
    
    # Total transcribed audio time: 125.5 seconds = 2 minutes 5 seconds
    assert tab.metric_cards['transcribed_time'].value_widget.text() == "02:05"
    
    # Characters: 49 (length of the text without trailing space)
    assert tab.metric_cards['characters'].value_widget.text() == "49"
    
    # Words: 8 (split by spaces)
    assert tab.metric_cards['words'].value_widget.text() == "8"
    
    # Removed silence: 15.3 seconds = 0 minutes 15 seconds
    assert tab.metric_cards['silence'].value_widget.text() == "00:15"


def test_statistics_tab_updates_on_period_change(qapp, temp_statistics_manager):
    """Test that the statistics tab updates when the time period is changed."""
    from datetime import datetime, timedelta
    from core.statistics_manager import StatisticsEvent, EventType
    
    # Create events with different timestamps
    now = datetime.now()
    
    # Event from 2 days ago
    old_event = StatisticsEvent(
        type=EventType.RECORDING,
        timestamp=now - timedelta(days=2),
        duration_seconds=100.0
    )
    
    # Event from today
    recent_event = StatisticsEvent(
        type=EventType.RECORDING,
        timestamp=now,
        duration_seconds=50.0
    )
    
    # Add events directly to the manager
    temp_statistics_manager.events = [old_event, recent_event]
    temp_statistics_manager._loaded = True
    
    # Create the tab (defaults to Last 7 Days)
    tab = StatisticsTab(temp_statistics_manager)
    
    # Should show both events (both within last 7 days)
    assert tab.metric_cards['recordings'].value_widget.text() == "2"
    assert tab.metric_cards['recording_time'].value_widget.text() == "02:30"  # 150 seconds
    
    # Change to "Today" filter
    tab.period_combo.setCurrentIndex(0)  # TODAY
    
    # Should show only the recent event
    assert tab.metric_cards['recordings'].value_widget.text() == "1"
    assert tab.metric_cards['recording_time'].value_widget.text() == "00:50"  # 50 seconds
    
    # Change to "All Time" filter
    tab.period_combo.setCurrentIndex(4)  # ALL_TIME
    
    # Should show both events again
    assert tab.metric_cards['recordings'].value_widget.text() == "2"
    assert tab.metric_cards['recording_time'].value_widget.text() == "02:30"  # 150 seconds


def test_statistics_tab_formats_large_numbers(qapp, temp_statistics_manager):
    """Test that the statistics tab correctly formats large numbers with thousand separators."""
    # Create a transcription with a large amount of text
    large_text = "word " * 50000  # 50,000 words, 250,000 characters
    
    temp_statistics_manager.track_transcription(
        audio_duration_seconds=3600.0,
        transcribed_text=large_text
    )
    
    # Create the tab
    tab = StatisticsTab(temp_statistics_manager)
    
    # Verify large numbers are formatted with commas
    assert tab.metric_cards['characters'].value_widget.text() == "250,000"
    assert tab.metric_cards['words'].value_widget.text() == "50,000"
    
    # Verify duration is formatted as HH:MM (1 hour)
    assert tab.metric_cards['transcribed_time'].value_widget.text() == "01:00"


def test_statistics_tab_handles_empty_statistics(qapp, temp_statistics_manager):
    """Test that the statistics tab handles empty statistics correctly."""
    # Create the tab with no events
    tab = StatisticsTab(temp_statistics_manager)
    
    # All values should be zero or 00:00
    assert tab.metric_cards['recordings'].value_widget.text() == "0"
    assert tab.metric_cards['transcriptions'].value_widget.text() == "0"
    assert tab.metric_cards['recording_time'].value_widget.text() == "00:00"
    assert tab.metric_cards['transcribed_time'].value_widget.text() == "00:00"
    assert tab.metric_cards['characters'].value_widget.text() == "0"
    assert tab.metric_cards['words'].value_widget.text() == "0"
    assert tab.metric_cards['silence'].value_widget.text() == "00:00"
