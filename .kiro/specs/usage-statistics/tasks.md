# Implementation Plan: Usage Statistics

## Overview

This implementation plan breaks down the Usage Statistics feature into discrete coding tasks. The feature adds comprehensive usage tracking and visualization to RapidWhisper, including a Statistics Manager for data collection, JSON-based local storage, and a Statistics Tab UI component integrated into the Settings Window.

The implementation follows an incremental approach:
1. Core Statistics Manager with storage
2. Statistics Tab UI component
3. Integration with existing components (Audio Recorder, Transcription Service, Silence Remover)
4. Testing and validation

## Tasks

- [x] 1. Set up Statistics Manager core structure
  - Create `core/statistics_manager.py` file
  - Implement `EventType` enum (RECORDING, TRANSCRIPTION, SILENCE_REMOVED)
  - Implement `StatisticsEvent` dataclass with all fields
  - Implement `TimePeriod` enum (TODAY, LAST_7_DAYS, LAST_30_DAYS, LAST_365_DAYS, ALL_TIME)
  - Implement `AggregatedStats` dataclass
  - Implement `StatisticsManager` class skeleton with `__init__` method
  - _Requirements: 5.1, 6.1, 6.2, 6.3, 6.4_

- [x] 2. Implement Statistics Manager event tracking
  - [x] 2.1 Implement `track_recording()` method
    - Accept duration_seconds parameter
    - Create StatisticsEvent with type RECORDING
    - Store current timestamp
    - Call `_add_event()` to persist
    - _Requirements: 1.1, 1.2, 1.3_
  
  - [x] 2.2 Implement `track_transcription()` method
    - Accept audio_duration_seconds and transcribed_text parameters
    - Calculate character_count using `len(transcribed_text)`
    - Calculate word_count using `len(transcribed_text.split())`
    - Create StatisticsEvent with type TRANSCRIPTION
    - Store current timestamp
    - Call `_add_event()` to persist
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 2.3 Implement `track_silence_removal()` method
    - Accept removed_duration_seconds parameter
    - Create StatisticsEvent with type SILENCE_REMOVED
    - Store current timestamp
    - Call `_add_event()` to persist
    - _Requirements: 3.1, 3.2_
  
  - [x] 2.4 Write property test for event tracking
    - **Property 1: Event Tracking Increments Counters**
    - **Validates: Requirements 1.1, 2.1**
  
  - [x] 2.5 Write property test for data persistence
    - **Property 2: Event Data Persistence**
    - **Validates: Requirements 1.2, 2.2, 2.3, 2.4, 3.1**

- [x] 3. Implement Statistics Manager storage operations
  - [x] 3.1 Implement `_save_to_storage()` method
    - Create config directory if it doesn't exist
    - Serialize events using `_serialize_events()`
    - Write JSON to statistics.json with UTF-8 encoding
    - Handle IOError gracefully (log and continue)
    - _Requirements: 5.1, 5.2, 5.5, 5.6, 10.2_
  
  - [x] 3.2 Implement `_load_from_storage()` method
    - Check if statistics.json exists
    - If not exists, initialize with empty events list
    - Read JSON file with UTF-8 encoding
    - Deserialize events using `_deserialize_events()`
    - Handle JSON decode errors (log, backup file, initialize empty)
    - Handle IOError gracefully (log and initialize empty)
    - _Requirements: 5.3, 5.4, 10.1, 10.3_
  
  - [x] 3.3 Implement `_serialize_events()` method
    - Convert list of StatisticsEvent to list of dictionaries
    - Format timestamps as ISO 8601 using `isoformat()`
    - Include all event fields (type, timestamp, duration_seconds, character_count, word_count, removed_duration_seconds)
    - _Requirements: 6.2, 6.3, 6.4, 6.5_
  
  - [x] 3.4 Implement `_deserialize_events()` method
    - Convert list of dictionaries to list of StatisticsEvent objects
    - Parse timestamps from ISO 8601 format
    - Skip events with invalid data (log warning)
    - Validate event types
    - _Requirements: 6.6, 10.4_
  
  - [x] 3.5 Write property test for storage round-trip
    - **Property 6: Storage Round-Trip**
    - **Validates: Requirements 5.2, 5.3, 5.5**
  
  - [x] 3.6 Write property test for UTF-8 encoding
    - **Property 7: UTF-8 Encoding Support**
    - **Validates: Requirements 5.6**
  
  - [x] 3.7 Write property test for event schema validation
    - **Property 8: Event Schema Validation**
    - **Validates: Requirements 6.2, 6.3, 6.4**

- [x] 4. Implement Statistics Manager aggregation and filtering
  - [x] 4.1 Implement `get_statistics()` method
    - Accept TimePeriod parameter
    - Call `_ensure_loaded()` to lazy load data
    - Filter events using `_filter_events_by_period()`
    - Aggregate events using `_aggregate_events()`
    - Return AggregatedStats
    - _Requirements: 4.1, 11.5_
  
  - [x] 4.2 Implement `_filter_events_by_period()` method
    - Handle ALL_TIME case (return all events)
    - Calculate cutoff time using `_get_cutoff_time()`
    - Filter events where timestamp >= cutoff_time
    - _Requirements: 4.2, 4.3, 4.4, 4.5, 4.6_
  
  - [x] 4.3 Implement `_get_cutoff_time()` method
    - Handle TODAY: return midnight today
    - Handle LAST_7_DAYS: return now - 7 days
    - Handle LAST_30_DAYS: return now - 30 days
    - Handle LAST_365_DAYS: return now - 365 days
    - _Requirements: 4.2, 4.3, 4.4, 4.5_
  
  - [x] 4.4 Implement `_aggregate_events()` method
    - Initialize AggregatedStats with zeros
    - Loop through events and accumulate counts and sums
    - For RECORDING events: increment recordings_count, sum duration
    - For TRANSCRIPTION events: increment transcriptions_count, sum duration, characters, words
    - For SILENCE_REMOVED events: sum removed_duration_seconds
    - Return AggregatedStats
    - _Requirements: 1.4, 1.5, 3.3, 3.4_
  
  - [x] 4.5 Write property test for aggregation correctness
    - **Property 4: Aggregation Correctness**
    - **Validates: Requirements 1.4, 3.3**
  
  - [x] 4.6 Write property test for time period filtering
    - **Property 5: Time Period Filtering**
    - **Validates: Requirements 1.5, 3.4, 4.2, 4.3, 4.4, 4.5, 4.6**

- [x] 5. Checkpoint - Ensure Statistics Manager tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement Statistics Tab UI component
  - [x] 6.1 Create `ui/statistics_tab.py` file
    - Import PyQt6 widgets (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QFrame, QGridLayout)
    - Import StatisticsManager, TimePeriod, AggregatedStats
    - _Requirements: 7.1, 8.1_
  
  - [x] 6.2 Implement MetricCard class
    - Inherit from QFrame
    - Accept label and value in `__init__`
    - Create vertical layout with label and value widgets
    - Style with background color, border radius, padding
    - Implement `update_value()` method to change displayed value
    - _Requirements: 7.1_
  
  - [x] 6.3 Implement StatisticsTab class skeleton
    - Inherit from QWidget
    - Accept statistics_manager in `__init__`
    - Store reference to statistics_manager
    - Initialize metric_cards dictionary
    - Call `_init_ui()` and `_load_statistics(TimePeriod.LAST_7_DAYS)`
    - _Requirements: 8.3_
  
  - [x] 6.4 Implement `_init_ui()` method
    - Create main vertical layout with spacing
    - Create time period filter section with QComboBox
    - Add filter options: "Today", "Last 7 Days", "Last 30 Days", "Last 365 Days", "All Time"
    - Set default to "Last 7 Days" (index 1)
    - Connect combo box to `_on_period_changed()` slot
    - Create metrics grid layout (2 columns)
    - Create 7 MetricCard instances for each metric
    - Add cards to grid layout
    - _Requirements: 4.1, 7.1, 7.2, 8.3_

- [x] 7. Implement Statistics Tab data display
  - [x] 7.1 Implement `_on_period_changed()` method
    - Get selected TimePeriod from combo box data
    - Call `_load_statistics()` with selected period
    - _Requirements: 4.7_
  
  - [x] 7.2 Implement `_load_statistics()` method
    - Call statistics_manager.get_statistics(period)
    - Call `_update_display()` with returned stats
    - _Requirements: 4.7_
  
  - [x] 7.3 Implement `_update_display()` method
    - Update recordings card with recordings_count
    - Update transcriptions card with transcriptions_count
    - Update recording_time card with formatted duration
    - Update transcribed_time card with formatted duration
    - Update characters card with formatted number
    - Update words card with formatted number
    - Update silence card with formatted duration
    - _Requirements: 7.2, 7.3, 7.4, 7.5_
  
  - [x] 7.4 Implement `_format_duration()` method
    - Convert seconds to integer
    - If >= 3600 seconds (1 hour): format as "HH:MM"
    - If < 3600 seconds: format as "MM:SS"
    - Use zero-padding for all components
    - _Requirements: 3.5, 7.3, 7.4_
  
  - [x] 7.5 Implement `_format_number()` method
    - Use Python's format with comma separator: `f"{number:,}"`
    - _Requirements: 7.5_
  
  - [x] 7.6 Write property test for duration formatting
    - **Property 9: Duration Formatting**
    - **Validates: Requirements 3.5, 7.3, 7.4**
  
  - [x] 7.7 Write property test for number formatting
    - **Property 10: Number Formatting**
    - **Validates: Requirements 7.5**

- [x] 8. Integrate Statistics Tab into Settings Window
  - [x] 8.1 Update `ui/settings_window.py`
    - Import StatisticsTab
    - Accept statistics_manager parameter in `__init__`
    - Create StatisticsTab instance
    - Add tab to QTabWidget with label "📊 Statistics"
    - Position after "Recordings" tab
    - _Requirements: 8.1, 8.2_
  
  - [x] 8.2 Update main application to pass statistics_manager
    - Create StatisticsManager instance in main app
    - Pass to SettingsWindow constructor
    - _Requirements: 8.1_

- [x] 9. Integrate Statistics Manager with Audio Recorder
  - [x] 9.1 Hook into recording completion event
    - Find the signal/callback when recording completes
    - Get recording duration from audio recorder
    - Call statistics_manager.track_recording(duration_seconds)
    - _Requirements: 1.1, 1.2, 1.3_

- [x] 10. Integrate Statistics Manager with Transcription Service
  - [x] 10.1 Hook into transcription completion event
    - Find the signal/callback when transcription completes
    - Get audio duration and transcribed text
    - Call statistics_manager.track_transcription(audio_duration, text)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 11. Integrate Statistics Manager with Silence Remover
  - [x] 11.1 Hook into silence removal completion event
    - Find the signal/callback when silence removal completes
    - Calculate removed silence duration (original - processed)
    - Call statistics_manager.track_silence_removal(removed_duration)
    - _Requirements: 3.1, 3.2_

- [x] 12. Add translation keys for Statistics feature
  - [x] 12.1 Add English translations
    - Add "statistics.title" key with value "Statistics"
    - Add keys for all metric labels (recordings, transcriptions, etc.)
    - Add keys for time period options (today, last_7_days, etc.)
    - Add "statistics.no_data" key with value "No data available for this period"
    - _Requirements: 9.1_
  
  - [x] 12.2 Add Russian translations
    - Add "statistics.title" key with value "Статистика"
    - Add Russian translations for all metric labels
    - Add Russian translations for time period options
    - Add "statistics.no_data" key with Russian translation
    - _Requirements: 9.2_
  
  - [x] 12.3 Update Statistics Tab to use translations
    - Replace hardcoded strings with translation keys
    - Use translation system for tab title, metric labels, filter options
    - _Requirements: 9.3, 9.4, 9.5, 9.6_

- [x] 13. Implement error handling and validation
  - [x] 13.1 Add input validation to Statistics Manager
    - Validate that duration values are non-negative
    - Validate that count values are non-negative
    - Log warnings for invalid values
    - Normalize negative values to zero
    - _Requirements: 10.5_
  
  - [x] 13.2 Add error handling to Statistics Tab
    - Wrap `_load_statistics()` in try-except
    - Display error message if loading fails
    - Don't crash the application
    - _Requirements: 10.6_
  
  - [x] 13.3 Write property test for corrupted file handling
    - **Property 11: Corrupted File Handling**
    - **Validates: Requirements 6.6, 10.1, 10.3**
  
  - [x] 13.4 Write property test for invalid event handling
    - **Property 12: Invalid Event Handling**
    - **Validates: Requirements 10.4**
  
  - [x] 13.5 Write property test for input validation
    - **Property 13: Input Validation**
    - **Validates: Requirements 10.5**

- [x] 14. Checkpoint - Ensure all integration tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 15. Add performance optimizations
  - [~] 15.1 Implement lazy loading in Statistics Manager
    - Add `_loaded` flag to track if data is loaded
    - Implement `_ensure_loaded()` method
    - Only load from storage on first access
    - _Requirements: 11.5_
  
  - [~] 15.2 Implement asynchronous storage writes
    - Use threading or asyncio for `_save_to_storage()`
    - Ensure writes don't block main thread
    - _Requirements: 11.4_
  
  - [~] 15.3 Write property test for write performance
    - **Property 14: Write Performance**
    - **Validates: Requirements 11.1**
  
  - [~] 15.4 Write property test for load performance
    - **Property 15: Load Performance**
    - **Validates: Requirements 11.2**
  
  - [~] 15.5 Write property test for filter performance
    - **Property 16: Filter Performance**
    - **Validates: Requirements 11.3**
  
  - [~] 15.6 Write property test for lazy loading
    - **Property 17: Lazy Loading**
    - **Validates: Requirements 11.5**

- [ ] 16. Write unit tests for edge cases
  - [~] 16.1 Test empty statistics (no events)
    - Verify all counts are zero
    - Verify all durations are zero
    - _Requirements: 7.7_
  
  - [~] 16.2 Test first run (no statistics file)
    - Verify file is created
    - Verify empty events array is initialized
    - _Requirements: 5.4_
  
  - [~] 16.3 Test events with zero duration
    - Verify zero durations are handled correctly
    - _Requirements: 1.2, 2.2_
  
  - [~] 16.4 Test transcription with empty text
    - Verify character_count is 0
    - Verify word_count is 0
    - _Requirements: 2.3, 2.4_
  
  - [~] 16.5 Test very large numbers
    - Test with millions of characters
    - Verify formatting works correctly
    - _Requirements: 7.5_

- [x] 17. Final checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Verify all requirements are covered
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties using Hypothesis library
- Unit tests validate specific examples and edge cases
- Integration tasks connect Statistics Manager with existing RapidWhisper components
- Translation tasks ensure multilingual support (English and Russian)
- All tests are required for comprehensive validation
