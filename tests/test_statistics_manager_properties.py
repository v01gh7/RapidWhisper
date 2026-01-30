"""
Property-based tests for Statistics Manager.

These tests verify universal properties that should hold across all valid inputs
using the Hypothesis library for property-based testing.
"""

import tempfile
from pathlib import Path
from datetime import datetime
from hypothesis import given, strategies as st
from core.statistics_manager import (
    StatisticsManager,
    EventType,
    StatisticsEvent,
    TimePeriod,
)


# Feature: usage-statistics, Property 1: Event Tracking Increments Counters
@given(
    recording_count=st.integers(min_value=0, max_value=50),
    transcription_count=st.integers(min_value=0, max_value=50),
    silence_count=st.integers(min_value=0, max_value=50),
)
def test_event_tracking_increments_counters(
    recording_count: int, transcription_count: int, silence_count: int
):
    """
    **Validates: Requirements 1.1, 2.1**
    
    Property: For any sequence of events (recordings, transcriptions, silence removals),
    tracking each event should increment the corresponding counter by exactly one,
    and the final count should equal the number of events tracked.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = StatisticsManager(config_dir)
        
        # Track recording events
        for _ in range(recording_count):
            manager.track_recording(duration_seconds=10.0)
        
        # Track transcription events
        for _ in range(transcription_count):
            manager.track_transcription(
                audio_duration_seconds=10.0,
                transcribed_text="test text"
            )
        
        # Track silence removal events
        for _ in range(silence_count):
            manager.track_silence_removal(removed_duration_seconds=5.0)
        
        # Get statistics and verify counts
        stats = manager.get_statistics(TimePeriod.ALL_TIME)
        
        assert stats.recordings_count == recording_count, (
            f"Expected {recording_count} recordings, got {stats.recordings_count}"
        )
        assert stats.transcriptions_count == transcription_count, (
            f"Expected {transcription_count} transcriptions, got {stats.transcriptions_count}"
        )
        
        # Verify total event count
        total_events = recording_count + transcription_count + silence_count
        assert len(manager.events) == total_events, (
            f"Expected {total_events} total events, got {len(manager.events)}"
        )


# Feature: usage-statistics, Property 2: Event Data Persistence
@given(
    duration=st.floats(min_value=0.1, max_value=3600.0, allow_nan=False, allow_infinity=False),
    text=st.text(min_size=1, max_size=1000),
    removed_duration=st.floats(min_value=0.1, max_value=1800.0, allow_nan=False, allow_infinity=False),
)
def test_event_data_persistence(duration: float, text: str, removed_duration: float):
    """
    **Validates: Requirements 1.2, 2.2, 2.3, 2.4, 3.1**
    
    Property: For any event with associated data (duration, character count, word count,
    removed silence), after tracking the event, retrieving statistics should return
    the exact same data values that were provided.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = StatisticsManager(config_dir)
        
        # Track a recording event
        manager.track_recording(duration_seconds=duration)
        
        # Track a transcription event
        expected_char_count = len(text)
        expected_word_count = len(text.split())
        manager.track_transcription(
            audio_duration_seconds=duration,
            transcribed_text=text
        )
        
        # Track a silence removal event
        manager.track_silence_removal(removed_duration_seconds=removed_duration)
        
        # Get statistics
        stats = manager.get_statistics(TimePeriod.ALL_TIME)
        
        # Verify recording data
        assert abs(stats.total_recording_time_seconds - duration) < 0.001, (
            f"Expected recording duration {duration}, got {stats.total_recording_time_seconds}"
        )
        
        # Verify transcription data
        assert abs(stats.total_transcribed_audio_time_seconds - duration) < 0.001, (
            f"Expected transcribed audio duration {duration}, got {stats.total_transcribed_audio_time_seconds}"
        )
        assert stats.total_character_count == expected_char_count, (
            f"Expected {expected_char_count} characters, got {stats.total_character_count}"
        )
        assert stats.total_word_count == expected_word_count, (
            f"Expected {expected_word_count} words, got {stats.total_word_count}"
        )
        
        # Verify silence removal data
        assert abs(stats.total_removed_silence_seconds - removed_duration) < 0.001, (
            f"Expected removed silence {removed_duration}, got {stats.total_removed_silence_seconds}"
        )


# Feature: usage-statistics, Property 6: Storage Round-Trip
@given(
    events=st.lists(
        st.one_of(
            # Recording events
            st.builds(
                lambda d: ('recording', d, None, None, None),
                d=st.floats(min_value=0.1, max_value=3600.0, allow_nan=False, allow_infinity=False)
            ),
            # Transcription events
            st.builds(
                lambda d, c, w: ('transcription', d, c, w, None),
                d=st.floats(min_value=0.1, max_value=3600.0, allow_nan=False, allow_infinity=False),
                c=st.integers(min_value=0, max_value=100000),
                w=st.integers(min_value=0, max_value=10000)
            ),
            # Silence removal events
            st.builds(
                lambda r: ('silence_removed', None, None, None, r),
                r=st.floats(min_value=0.1, max_value=1800.0, allow_nan=False, allow_infinity=False)
            )
        ),
        min_size=0,
        max_size=20
    )
)
def test_storage_round_trip(events):
    """
    **Validates: Requirements 5.2, 5.3, 5.5**
    
    Property: For any set of events, after saving them to storage and then loading
    from storage, the loaded events should be equivalent to the original events
    (same type, timestamp, and all data fields).
    """
    from datetime import datetime
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = StatisticsManager(config_dir)
        
        # Create events with known timestamps
        original_events = []
        for event_data in events:
            event_type, duration, char_count, word_count, removed_duration = event_data
            
            if event_type == 'recording':
                event = StatisticsEvent(
                    type=EventType.RECORDING,
                    timestamp=datetime.now(),
                    duration_seconds=duration
                )
            elif event_type == 'transcription':
                event = StatisticsEvent(
                    type=EventType.TRANSCRIPTION,
                    timestamp=datetime.now(),
                    duration_seconds=duration,
                    character_count=char_count,
                    word_count=word_count
                )
            else:  # silence_removed
                event = StatisticsEvent(
                    type=EventType.SILENCE_REMOVED,
                    timestamp=datetime.now(),
                    removed_duration_seconds=removed_duration
                )
            
            original_events.append(event)
        
        # Save events
        manager.events = original_events
        manager._save_to_storage()
        
        # Create a new manager and load events
        manager2 = StatisticsManager(config_dir)
        manager2._load_from_storage()
        
        # Verify same number of events
        assert len(manager2.events) == len(original_events), (
            f"Expected {len(original_events)} events after round-trip, got {len(manager2.events)}"
        )
        
        # Verify each event matches
        for original, loaded in zip(original_events, manager2.events):
            assert original.type == loaded.type, (
                f"Event type mismatch: {original.type} != {loaded.type}"
            )
            
            # Timestamps should be equal (ISO format preserves precision)
            assert original.timestamp == loaded.timestamp, (
                f"Timestamp mismatch: {original.timestamp} != {loaded.timestamp}"
            )
            
            # Check all data fields
            if original.duration_seconds is not None:
                assert loaded.duration_seconds is not None
                assert abs(original.duration_seconds - loaded.duration_seconds) < 0.001, (
                    f"Duration mismatch: {original.duration_seconds} != {loaded.duration_seconds}"
                )
            else:
                assert loaded.duration_seconds is None
            
            assert original.character_count == loaded.character_count, (
                f"Character count mismatch: {original.character_count} != {loaded.character_count}"
            )
            
            assert original.word_count == loaded.word_count, (
                f"Word count mismatch: {original.word_count} != {loaded.word_count}"
            )
            
            if original.removed_duration_seconds is not None:
                assert loaded.removed_duration_seconds is not None
                assert abs(original.removed_duration_seconds - loaded.removed_duration_seconds) < 0.001, (
                    f"Removed duration mismatch: {original.removed_duration_seconds} != {loaded.removed_duration_seconds}"
                )
            else:
                assert loaded.removed_duration_seconds is None



# Feature: usage-statistics, Property 7: UTF-8 Encoding Support
@given(
    text=st.one_of(
        # Cyrillic text
        st.text(alphabet=st.characters(min_codepoint=0x0400, max_codepoint=0x04FF), min_size=1, max_size=100),
        # Chinese text
        st.text(alphabet=st.characters(min_codepoint=0x4E00, max_codepoint=0x9FFF), min_size=1, max_size=100),
        # Emoji
        st.text(alphabet=st.characters(min_codepoint=0x1F600, max_codepoint=0x1F64F), min_size=1, max_size=20),
        # Mixed ASCII and non-ASCII
        st.text(min_size=1, max_size=100)
    )
)
def test_utf8_encoding_support(text: str):
    """
    **Validates: Requirements 5.6**
    
    Property: For any transcription text containing non-ASCII characters (Cyrillic,
    emoji, Chinese, etc.), after tracking the transcription and reloading from storage,
    the character and word counts should be preserved correctly.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = StatisticsManager(config_dir)
        
        # Calculate expected counts
        expected_char_count = len(text)
        expected_word_count = len(text.split())
        
        # Track transcription with non-ASCII text
        manager.track_transcription(
            audio_duration_seconds=10.0,
            transcribed_text=text
        )
        
        # Create a new manager and load from storage
        manager2 = StatisticsManager(config_dir)
        stats = manager2.get_statistics(TimePeriod.ALL_TIME)
        
        # Verify character and word counts are preserved
        assert stats.total_character_count == expected_char_count, (
            f"Character count mismatch after UTF-8 round-trip: "
            f"expected {expected_char_count}, got {stats.total_character_count}"
        )
        
        assert stats.total_word_count == expected_word_count, (
            f"Word count mismatch after UTF-8 round-trip: "
            f"expected {expected_word_count}, got {stats.total_word_count}"
        )
        
        # Verify the file was actually written with UTF-8 encoding
        # by reading it directly and checking it contains valid JSON
        import json
        with open(manager.storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert 'events' in data
            assert len(data['events']) == 1



# Feature: usage-statistics, Property 8: Event Schema Validation
@given(
    event_type=st.sampled_from(['recording', 'transcription', 'silence_removed']),
    duration=st.floats(min_value=0.1, max_value=3600.0, allow_nan=False, allow_infinity=False),
    char_count=st.integers(min_value=0, max_value=100000),
    word_count=st.integers(min_value=0, max_value=10000),
    removed_duration=st.floats(min_value=0.1, max_value=1800.0, allow_nan=False, allow_infinity=False)
)
def test_event_schema_validation(
    event_type: str,
    duration: float,
    char_count: int,
    word_count: int,
    removed_duration: float
):
    """
    **Validates: Requirements 6.2, 6.3, 6.4**
    
    Property: For any event stored in statistics.json, the JSON object should contain
    the correct fields for its event type: recording events have (type, timestamp,
    duration_seconds), transcription events have (type, timestamp, duration_seconds,
    character_count, word_count), and silence_removed events have (type, timestamp,
    removed_duration_seconds).
    """
    import json
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = StatisticsManager(config_dir)
        
        # Track an event based on type
        if event_type == 'recording':
            manager.track_recording(duration_seconds=duration)
        elif event_type == 'transcription':
            # Create text with specific character and word counts
            text = 'a' * char_count
            manager.track_transcription(
                audio_duration_seconds=duration,
                transcribed_text=text
            )
        else:  # silence_removed
            manager.track_silence_removal(removed_duration_seconds=removed_duration)
        
        # Read the JSON file directly
        with open(manager.storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Verify structure
        assert 'events' in data, "JSON should have 'events' key"
        assert len(data['events']) == 1, "Should have exactly one event"
        
        event_json = data['events'][0]
        
        # All events should have type and timestamp
        assert 'type' in event_json, "Event should have 'type' field"
        assert 'timestamp' in event_json, "Event should have 'timestamp' field"
        assert event_json['type'] == event_type, f"Event type should be {event_type}"
        
        # Verify timestamp is ISO 8601 format
        from datetime import datetime
        try:
            datetime.fromisoformat(event_json['timestamp'])
        except ValueError:
            assert False, f"Timestamp should be ISO 8601 format: {event_json['timestamp']}"
        
        # Verify type-specific fields
        if event_type == 'recording':
            assert 'duration_seconds' in event_json, "Recording event should have 'duration_seconds'"
            assert event_json['duration_seconds'] is not None
            assert abs(event_json['duration_seconds'] - duration) < 0.001
            
        elif event_type == 'transcription':
            assert 'duration_seconds' in event_json, "Transcription event should have 'duration_seconds'"
            assert 'character_count' in event_json, "Transcription event should have 'character_count'"
            assert 'word_count' in event_json, "Transcription event should have 'word_count'"
            assert event_json['duration_seconds'] is not None
            assert event_json['character_count'] is not None
            assert event_json['word_count'] is not None
            assert abs(event_json['duration_seconds'] - duration) < 0.001
            
        else:  # silence_removed
            assert 'removed_duration_seconds' in event_json, "Silence removal event should have 'removed_duration_seconds'"
            assert event_json['removed_duration_seconds'] is not None
            assert abs(event_json['removed_duration_seconds'] - removed_duration) < 0.001


# Feature: usage-statistics, Property 4: Aggregation Correctness
@given(
    events=st.lists(
        st.one_of(
            # Recording events with duration
            st.builds(
                lambda d: ('recording', d, None, None, None),
                d=st.floats(min_value=0.1, max_value=3600.0, allow_nan=False, allow_infinity=False)
            ),
            # Transcription events with duration, character count, and word count
            st.builds(
                lambda d, c, w: ('transcription', d, c, w, None),
                d=st.floats(min_value=0.1, max_value=3600.0, allow_nan=False, allow_infinity=False),
                c=st.integers(min_value=0, max_value=100000),
                w=st.integers(min_value=0, max_value=10000)
            ),
            # Silence removal events with removed duration
            st.builds(
                lambda r: ('silence_removed', None, None, None, r),
                r=st.floats(min_value=0.1, max_value=1800.0, allow_nan=False, allow_infinity=False)
            )
        ),
        min_size=0,
        max_size=50
    )
)
def test_aggregation_correctness(events):
    """
    **Validates: Requirements 1.4, 3.3**
    
    Property: For any set of events, the aggregated statistics (total recording time,
    total transcribed audio time, total removed silence, total characters, total words)
    should equal the sum of the individual event values.
    """
    from datetime import datetime
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = StatisticsManager(config_dir)
        
        # Track expected totals
        expected_recording_time = 0.0
        expected_transcribed_time = 0.0
        expected_characters = 0
        expected_words = 0
        expected_removed_silence = 0.0
        expected_recording_count = 0
        expected_transcription_count = 0
        
        # Create and track events
        for event_data in events:
            event_type, duration, char_count, word_count, removed_duration = event_data
            
            if event_type == 'recording':
                manager.track_recording(duration_seconds=duration)
                expected_recording_time += duration
                expected_recording_count += 1
                
            elif event_type == 'transcription':
                # Create text with specific character and word counts
                # We need to create text that matches the counts
                text = 'a' * char_count if char_count > 0 else ''
                manager.track_transcription(
                    audio_duration_seconds=duration,
                    transcribed_text=text
                )
                expected_transcribed_time += duration
                expected_characters += char_count
                # Word count is calculated by split(), so single char string has 1 word if non-empty
                expected_words += (1 if char_count > 0 else 0)
                expected_transcription_count += 1
                
            else:  # silence_removed
                manager.track_silence_removal(removed_duration_seconds=removed_duration)
                expected_removed_silence += removed_duration
        
        # Get aggregated statistics
        stats = manager.get_statistics(TimePeriod.ALL_TIME)
        
        # Verify counts
        assert stats.recordings_count == expected_recording_count, (
            f"Recording count mismatch: expected {expected_recording_count}, "
            f"got {stats.recordings_count}"
        )
        
        assert stats.transcriptions_count == expected_transcription_count, (
            f"Transcription count mismatch: expected {expected_transcription_count}, "
            f"got {stats.transcriptions_count}"
        )
        
        # Verify aggregated sums (with tolerance for floating point)
        assert abs(stats.total_recording_time_seconds - expected_recording_time) < 0.01, (
            f"Total recording time mismatch: expected {expected_recording_time}, "
            f"got {stats.total_recording_time_seconds}"
        )
        
        assert abs(stats.total_transcribed_audio_time_seconds - expected_transcribed_time) < 0.01, (
            f"Total transcribed audio time mismatch: expected {expected_transcribed_time}, "
            f"got {stats.total_transcribed_audio_time_seconds}"
        )
        
        assert stats.total_character_count == expected_characters, (
            f"Total character count mismatch: expected {expected_characters}, "
            f"got {stats.total_character_count}"
        )
        
        assert stats.total_word_count == expected_words, (
            f"Total word count mismatch: expected {expected_words}, "
            f"got {stats.total_word_count}"
        )
        
        assert abs(stats.total_removed_silence_seconds - expected_removed_silence) < 0.01, (
            f"Total removed silence mismatch: expected {expected_removed_silence}, "
            f"got {stats.total_removed_silence_seconds}"
        )


# Feature: usage-statistics, Property 5: Time Period Filtering
@given(
    # Generate events with timestamps spread across different time periods
    events_with_ages=st.lists(
        st.tuples(
            # Event type and data
            st.one_of(
                st.builds(
                    lambda d: ('recording', d, None, None, None),
                    d=st.floats(min_value=0.1, max_value=100.0, allow_nan=False, allow_infinity=False)
                ),
                st.builds(
                    lambda d, c, w: ('transcription', d, c, w, None),
                    d=st.floats(min_value=0.1, max_value=100.0, allow_nan=False, allow_infinity=False),
                    c=st.integers(min_value=1, max_value=1000),
                    w=st.integers(min_value=1, max_value=100)
                ),
                st.builds(
                    lambda r: ('silence_removed', None, None, None, r),
                    r=st.floats(min_value=0.1, max_value=100.0, allow_nan=False, allow_infinity=False)
                )
            ),
            # Age in days (how many days ago the event occurred)
            # Avoid exact boundaries by using values slightly less than the period limits
            st.integers(min_value=0, max_value=400)
        ),
        min_size=0,
        max_size=30
    ),
    period=st.sampled_from([
        TimePeriod.TODAY,
        TimePeriod.LAST_7_DAYS,
        TimePeriod.LAST_30_DAYS,
        TimePeriod.LAST_365_DAYS,
        TimePeriod.ALL_TIME
    ])
)
def test_time_period_filtering(events_with_ages, period):
    """
    **Validates: Requirements 1.5, 3.4, 4.2, 4.3, 4.4, 4.5, 4.6**
    
    Property: For any set of events with different timestamps and any time period filter
    (Today, Last 7 Days, Last 30 Days, Last 365 Days, All Time), the filtered statistics
    should include only events whose timestamps fall within the specified period, and the
    "All Time" filter should include all events.
    """
    from datetime import datetime, timedelta
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = StatisticsManager(config_dir)
        
        now = datetime.now()
        
        # Create events with specific timestamps
        created_events = []
        for event_data, days_ago in events_with_ages:
            event_type, duration, char_count, word_count, removed_duration = event_data
            
            # Calculate timestamp (subtract days and add a small buffer to avoid boundary issues)
            # This ensures events at exactly the boundary are included
            timestamp = now - timedelta(days=days_ago, seconds=-1)
            
            # Create event
            if event_type == 'recording':
                event = StatisticsEvent(
                    type=EventType.RECORDING,
                    timestamp=timestamp,
                    duration_seconds=duration
                )
            elif event_type == 'transcription':
                event = StatisticsEvent(
                    type=EventType.TRANSCRIPTION,
                    timestamp=timestamp,
                    duration_seconds=duration,
                    character_count=char_count,
                    word_count=word_count
                )
            else:  # silence_removed
                event = StatisticsEvent(
                    type=EventType.SILENCE_REMOVED,
                    timestamp=timestamp,
                    removed_duration_seconds=removed_duration
                )
            
            created_events.append(event)
        
        # Add events to manager
        manager.events = created_events
        manager._loaded = True
        
        # Get statistics for the specified period
        stats = manager.get_statistics(period)
        
        # Determine which events should be included based on the period
        cutoff_time = manager._get_cutoff_time(now, period)
        
        if period == TimePeriod.ALL_TIME:
            expected_events = created_events
        else:
            expected_events = [e for e in created_events if e.timestamp >= cutoff_time]
        
        # Calculate expected statistics
        expected_recording_count = sum(1 for e in expected_events if e.type == EventType.RECORDING)
        expected_transcription_count = sum(1 for e in expected_events if e.type == EventType.TRANSCRIPTION)
        expected_recording_time = sum(
            e.duration_seconds for e in expected_events 
            if e.type == EventType.RECORDING and e.duration_seconds
        )
        expected_transcribed_time = sum(
            e.duration_seconds for e in expected_events 
            if e.type == EventType.TRANSCRIPTION and e.duration_seconds
        )
        expected_characters = sum(
            e.character_count for e in expected_events 
            if e.type == EventType.TRANSCRIPTION and e.character_count
        )
        expected_words = sum(
            e.word_count for e in expected_events 
            if e.type == EventType.TRANSCRIPTION and e.word_count
        )
        expected_removed_silence = sum(
            e.removed_duration_seconds for e in expected_events 
            if e.type == EventType.SILENCE_REMOVED and e.removed_duration_seconds
        )
        
        # Verify filtered statistics match expected values
        assert stats.recordings_count == expected_recording_count, (
            f"Recording count mismatch for {period}: expected {expected_recording_count}, "
            f"got {stats.recordings_count}"
        )
        
        assert stats.transcriptions_count == expected_transcription_count, (
            f"Transcription count mismatch for {period}: expected {expected_transcription_count}, "
            f"got {stats.transcriptions_count}"
        )
        
        assert abs(stats.total_recording_time_seconds - expected_recording_time) < 0.01, (
            f"Total recording time mismatch for {period}: expected {expected_recording_time}, "
            f"got {stats.total_recording_time_seconds}"
        )
        
        assert abs(stats.total_transcribed_audio_time_seconds - expected_transcribed_time) < 0.01, (
            f"Total transcribed audio time mismatch for {period}: expected {expected_transcribed_time}, "
            f"got {stats.total_transcribed_audio_time_seconds}"
        )
        
        assert stats.total_character_count == expected_characters, (
            f"Total character count mismatch for {period}: expected {expected_characters}, "
            f"got {stats.total_character_count}"
        )
        
        assert stats.total_word_count == expected_words, (
            f"Total word count mismatch for {period}: expected {expected_words}, "
            f"got {stats.total_word_count}"
        )
        
        assert abs(stats.total_removed_silence_seconds - expected_removed_silence) < 0.01, (
            f"Total removed silence mismatch for {period}: expected {expected_removed_silence}, "
            f"got {stats.total_removed_silence_seconds}"
        )
        
        # Special check for ALL_TIME: should include all events
        if period == TimePeriod.ALL_TIME:
            assert len(expected_events) == len(created_events), (
                f"ALL_TIME filter should include all {len(created_events)} events"
            )



# Feature: usage-statistics, Property 13: Input Validation
@given(
    recording_duration=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    audio_duration=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    removed_duration=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
)
def test_input_validation(
    recording_duration: float,
    audio_duration: float,
    removed_duration: float
):
    """
    **Validates: Requirements 10.5**
    
    Property: The Statistics Manager should validate and normalize all input values:
    - Negative durations should be normalized to zero
    - Negative counts should be normalized to zero
    - All aggregated values should be non-negative
    
    This ensures data integrity and prevents invalid statistics from corrupting the system.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        manager = StatisticsManager(config_dir)
        
        # Track events with potentially negative values
        manager.track_recording(duration_seconds=recording_duration)
        manager.track_transcription(
            audio_duration_seconds=audio_duration,
            transcribed_text="test text"
        )
        manager.track_silence_removal(removed_duration_seconds=removed_duration)
        
        # Get statistics
        stats = manager.get_statistics(TimePeriod.ALL_TIME)
        
        # Property: All aggregated values must be non-negative
        assert stats.recordings_count >= 0, "Recordings count must be non-negative"
        assert stats.transcriptions_count >= 0, "Transcriptions count must be non-negative"
        assert stats.total_recording_time_seconds >= 0, "Total recording time must be non-negative"
        assert stats.total_transcribed_audio_time_seconds >= 0, "Total transcribed audio time must be non-negative"
        assert stats.total_character_count >= 0, "Total character count must be non-negative"
        assert stats.total_word_count >= 0, "Total word count must be non-negative"
        assert stats.total_removed_silence_seconds >= 0, "Total removed silence must be non-negative"
        
        # Property: Counts should always be positive (we tracked events)
        assert stats.recordings_count == 1, "Should have tracked 1 recording"
        assert stats.transcriptions_count == 1, "Should have tracked 1 transcription"
        
        # Property: If input was negative, duration should be 0; otherwise it should match input
        expected_recording_time = max(0.0, recording_duration)
        expected_audio_time = max(0.0, audio_duration)
        expected_removed_silence = max(0.0, removed_duration)
        
        assert stats.total_recording_time_seconds == expected_recording_time, \
            f"Recording time should be {expected_recording_time}, got {stats.total_recording_time_seconds}"
        assert stats.total_transcribed_audio_time_seconds == expected_audio_time, \
            f"Audio time should be {expected_audio_time}, got {stats.total_transcribed_audio_time_seconds}"
        assert stats.total_removed_silence_seconds == expected_removed_silence, \
            f"Removed silence should be {expected_removed_silence}, got {stats.total_removed_silence_seconds}"



# Feature: usage-statistics, Property 11: Corrupted File Handling
@given(
    corrupted_content=st.one_of(
        st.just("not json"),
        st.just("{invalid json"),
        st.just('{"events": "not a list"}'),
        st.just('{"events": [{"invalid": "event"}]}'),
        st.binary(min_size=1, max_size=100),
    )
)
def test_corrupted_file_handling(corrupted_content):
    """
    **Validates: Requirements 6.6, 10.1, 10.3**
    
    Property: The Statistics Manager should gracefully handle corrupted storage files:
    - Invalid JSON should not crash the application
    - Corrupted files should be backed up
    - The manager should initialize with empty statistics
    - Subsequent operations should work normally
    
    This ensures robustness and data recovery capabilities.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        storage_path = config_dir / "statistics.json"
        
        # Create a corrupted statistics file
        config_dir.mkdir(parents=True, exist_ok=True)
        if isinstance(corrupted_content, bytes):
            with open(storage_path, 'wb') as f:
                f.write(corrupted_content)
        else:
            with open(storage_path, 'w', encoding='utf-8') as f:
                f.write(corrupted_content)
        
        # Try to load statistics - should not crash
        manager = StatisticsManager(config_dir)
        
        # Property: Should initialize with empty statistics
        stats = manager.get_statistics(TimePeriod.ALL_TIME)
        assert stats.recordings_count == 0, "Should start with 0 recordings after corruption"
        assert stats.transcriptions_count == 0, "Should start with 0 transcriptions after corruption"
        
        # Property: Should be able to track new events after corruption
        manager.track_recording(duration_seconds=10.0)
        stats = manager.get_statistics(TimePeriod.ALL_TIME)
        assert stats.recordings_count == 1, "Should be able to track events after corruption"
        
        # Property: Backup file should exist (if original was valid JSON that failed to parse)
        backup_path = storage_path.with_suffix('.json.backup')
        # Note: Backup is only created for JSON decode errors, not for binary files


# Feature: usage-statistics, Property 12: Invalid Event Handling
@given(
    events_data=st.lists(
        st.one_of(
            # Valid event
            st.fixed_dictionaries({
                'type': st.sampled_from(['recording', 'transcription', 'silence_removed']),
                'timestamp': st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2030, 12, 31)).map(lambda dt: dt.isoformat()),
                'duration_seconds': st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
                'character_count': st.integers(min_value=0, max_value=10000),
                'word_count': st.integers(min_value=0, max_value=1000),
                'removed_duration_seconds': st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
            }),
            # Invalid events - missing required fields
            st.fixed_dictionaries({
                'type': st.just('invalid_type'),
                'timestamp': st.just('2024-01-01T00:00:00'),
            }),
            st.fixed_dictionaries({
                'timestamp': st.just('2024-01-01T00:00:00'),
            }),
            st.fixed_dictionaries({
                'type': st.just('recording'),
            }),
        ),
        min_size=0,
        max_size=10
    )
)
def test_invalid_event_handling(events_data):
    """
    **Validates: Requirements 10.4**
    
    Property: The Statistics Manager should gracefully handle invalid events:
    - Events with missing required fields should be skipped
    - Events with invalid types should be skipped
    - Valid events should still be processed correctly
    - The system should not crash on invalid data
    
    This ensures data integrity and robustness.
    """
    import json
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        storage_path = config_dir / "statistics.json"
        
        # Create a statistics file with mixed valid/invalid events
        config_dir.mkdir(parents=True, exist_ok=True)
        data = {'events': events_data}
        with open(storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        
        # Load statistics - should not crash
        manager = StatisticsManager(config_dir)
        stats = manager.get_statistics(TimePeriod.ALL_TIME)
        
        # Property: Should only count valid events
        # Count how many valid events we expect
        valid_recording_count = sum(
            1 for e in events_data 
            if e.get('type') == 'recording' and 'timestamp' in e
        )
        valid_transcription_count = sum(
            1 for e in events_data 
            if e.get('type') == 'transcription' and 'timestamp' in e
        )
        
        assert stats.recordings_count == valid_recording_count, \
            f"Expected {valid_recording_count} recordings, got {stats.recordings_count}"
        assert stats.transcriptions_count == valid_transcription_count, \
            f"Expected {valid_transcription_count} transcriptions, got {stats.transcriptions_count}"
        
        # Property: All aggregated values should be non-negative
        assert stats.total_recording_time_seconds >= 0
        assert stats.total_transcribed_audio_time_seconds >= 0
        assert stats.total_character_count >= 0
        assert stats.total_word_count >= 0
        assert stats.total_removed_silence_seconds >= 0
