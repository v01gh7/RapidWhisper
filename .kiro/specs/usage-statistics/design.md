# Design Document: Usage Statistics

## Overview

The Usage Statistics feature adds comprehensive usage tracking and visualization to the RapidWhisper application. This feature collects metrics about recordings, transcriptions, and audio processing, storing them locally in JSON format for privacy. Users can view statistics through a new tab in the Settings Window, with filtering capabilities by time period (day, week, month, year, all time).

The design follows the existing RapidWhisper architecture patterns:
- **Statistics Manager**: Core component for collecting and storing statistics
- **Statistics Tab**: UI component integrated into Settings Window
- **JSON Storage**: Local file-based persistence in the config directory
- **Event-driven updates**: Statistics update automatically after each operation

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     RapidWhisper App                         │
│                                                              │
│  ┌────────────────┐         ┌──────────────────┐           │
│  │ Audio Recorder │────────▶│ Statistics       │           │
│  │                │         │ Manager          │           │
│  └────────────────┘         │                  │           │
│                             │ - track_event()  │           │
│  ┌────────────────┐         │ - get_stats()    │           │
│  │ Transcription  │────────▶│ - filter_by_time│           │
│  │ Service        │         └────────┬─────────┘           │
│  └────────────────┘                  │                     │
│                                      │                     │
│  ┌────────────────┐                  │                     │
│  │ Silence        │──────────────────┘                     │
│  │ Remover        │                                        │
│  └────────────────┘                                        │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │            Settings Window                          │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │         Statistics Tab                        │  │    │
│  │  │                                               │  │    │
│  │  │  ┌─────────────────────────────────────┐    │  │    │
│  │  │  │  Time Filter Dropdown               │    │  │    │
│  │  │  └─────────────────────────────────────┘    │  │    │
│  │  │                                               │  │    │
│  │  │  ┌─────────────────────────────────────┐    │  │    │
│  │  │  │  Metric Cards Grid                  │    │  │    │
│  │  │  │  - Recordings Count                 │    │  │    │
│  │  │  │  - Transcriptions Count             │    │  │    │
│  │  │  │  - Total Recording Time             │    │  │    │
│  │  │  │  - Total Transcribed Audio Time     │    │  │    │
│  │  │  │  - Character Count                  │    │  │    │
│  │  │  │  - Word Count                       │    │  │    │
│  │  │  │  - Removed Silence                  │    │  │    │
│  │  │  └─────────────────────────────────────┘    │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Statistics Storage (statistics.json)              │    │
│  │  Location: Config Directory                        │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points

1. **Audio Recorder Integration**
   - Hook into recording completion event
   - Capture recording duration
   - Track timestamp

2. **Transcription Service Integration**
   - Hook into transcription completion event
   - Capture audio duration, character count, word count
   - Track timestamp

3. **Silence Remover Integration**
   - Hook into silence removal completion event
   - Capture removed silence duration
   - Track timestamp

4. **Settings Window Integration**
   - Add new tab between "Recordings" and "About"
   - Follow existing tab creation patterns
   - Use consistent styling

## Components and Interfaces

### 1. Statistics Manager (`core/statistics_manager.py`)

The Statistics Manager is responsible for collecting, storing, and retrieving usage statistics.

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import json
from enum import Enum

class EventType(Enum):
    """Types of statistics events."""
    RECORDING = "recording"
    TRANSCRIPTION = "transcription"
    SILENCE_REMOVED = "silence_removed"

@dataclass
class StatisticsEvent:
    """Represents a single statistics event."""
    type: EventType
    timestamp: datetime
    duration_seconds: Optional[float] = None  # For recording and transcribed audio
    character_count: Optional[int] = None  # For transcription
    word_count: Optional[int] = None  # For transcription
    removed_duration_seconds: Optional[float] = None  # For silence removal

class TimePeriod(Enum):
    """Time period filters for statistics."""
    TODAY = "today"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    LAST_365_DAYS = "last_365_days"
    ALL_TIME = "all_time"

@dataclass
class AggregatedStats:
    """Aggregated statistics for a time period."""
    recordings_count: int = 0
    transcriptions_count: int = 0
    total_recording_time_seconds: float = 0.0
    total_transcribed_audio_time_seconds: float = 0.0
    total_character_count: int = 0
    total_word_count: int = 0
    total_removed_silence_seconds: float = 0.0

class StatisticsManager:
    """Manages statistics collection, storage, and retrieval."""
    
    def __init__(self, config_dir: Path):
        """Initialize the statistics manager.
        
        Args:
            config_dir: Path to the application configuration directory
        """
        self.config_dir = config_dir
        self.storage_path = config_dir / "statistics.json"
        self.events: List[StatisticsEvent] = []
        self._loaded = False
    
    def track_recording(self, duration_seconds: float) -> None:
        """Track a recording event.
        
        Args:
            duration_seconds: Duration of the recording in seconds
        """
        event = StatisticsEvent(
            type=EventType.RECORDING,
            timestamp=datetime.now(),
            duration_seconds=duration_seconds
        )
        self._add_event(event)
    
    def track_transcription(
        self, 
        audio_duration_seconds: float,
        transcribed_text: str
    ) -> None:
        """Track a transcription event.
        
        Args:
            audio_duration_seconds: Duration of the transcribed audio
            transcribed_text: The transcribed text content
        """
        character_count = len(transcribed_text)
        word_count = len(transcribed_text.split())
        
        event = StatisticsEvent(
            type=EventType.TRANSCRIPTION,
            timestamp=datetime.now(),
            duration_seconds=audio_duration_seconds,
            character_count=character_count,
            word_count=word_count
        )
        self._add_event(event)
    
    def track_silence_removal(self, removed_duration_seconds: float) -> None:
        """Track a silence removal event.
        
        Args:
            removed_duration_seconds: Duration of removed silence in seconds
        """
        event = StatisticsEvent(
            type=EventType.SILENCE_REMOVED,
            timestamp=datetime.now(),
            removed_duration_seconds=removed_duration_seconds
        )
        self._add_event(event)
    
    def get_statistics(self, period: TimePeriod) -> AggregatedStats:
        """Get aggregated statistics for a time period.
        
        Args:
            period: The time period to filter by
            
        Returns:
            Aggregated statistics for the specified period
        """
        self._ensure_loaded()
        filtered_events = self._filter_events_by_period(period)
        return self._aggregate_events(filtered_events)
    
    def _add_event(self, event: StatisticsEvent) -> None:
        """Add an event and save to storage."""
        self._ensure_loaded()
        self.events.append(event)
        self._save_to_storage()
    
    def _ensure_loaded(self) -> None:
        """Ensure statistics are loaded from storage."""
        if not self._loaded:
            self._load_from_storage()
            self._loaded = True
    
    def _load_from_storage(self) -> None:
        """Load statistics from JSON file."""
        if not self.storage_path.exists():
            self.events = []
            return
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.events = self._deserialize_events(data.get('events', []))
        except (json.JSONDecodeError, IOError) as e:
            # Log error and start with empty statistics
            print(f"Error loading statistics: {e}")
            self.events = []
    
    def _save_to_storage(self) -> None:
        """Save statistics to JSON file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            data = {'events': self._serialize_events(self.events)}
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving statistics: {e}")
    
    def _serialize_events(self, events: List[StatisticsEvent]) -> List[Dict]:
        """Convert events to JSON-serializable format."""
        return [
            {
                'type': event.type.value,
                'timestamp': event.timestamp.isoformat(),
                'duration_seconds': event.duration_seconds,
                'character_count': event.character_count,
                'word_count': event.word_count,
                'removed_duration_seconds': event.removed_duration_seconds
            }
            for event in events
        ]
    
    def _deserialize_events(self, data: List[Dict]) -> List[StatisticsEvent]:
        """Convert JSON data to StatisticsEvent objects."""
        events = []
        for item in data:
            try:
                event = StatisticsEvent(
                    type=EventType(item['type']),
                    timestamp=datetime.fromisoformat(item['timestamp']),
                    duration_seconds=item.get('duration_seconds'),
                    character_count=item.get('character_count'),
                    word_count=item.get('word_count'),
                    removed_duration_seconds=item.get('removed_duration_seconds')
                )
                events.append(event)
            except (KeyError, ValueError) as e:
                # Skip invalid events
                print(f"Skipping invalid event: {e}")
                continue
        return events
    
    def _filter_events_by_period(
        self, 
        period: TimePeriod
    ) -> List[StatisticsEvent]:
        """Filter events by time period."""
        if period == TimePeriod.ALL_TIME:
            return self.events
        
        now = datetime.now()
        cutoff_time = self._get_cutoff_time(now, period)
        
        return [
            event for event in self.events 
            if event.timestamp >= cutoff_time
        ]
    
    def _get_cutoff_time(self, now: datetime, period: TimePeriod) -> datetime:
        """Calculate the cutoff time for a period."""
        from datetime import timedelta
        
        if period == TimePeriod.TODAY:
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == TimePeriod.LAST_7_DAYS:
            return now - timedelta(days=7)
        elif period == TimePeriod.LAST_30_DAYS:
            return now - timedelta(days=30)
        elif period == TimePeriod.LAST_365_DAYS:
            return now - timedelta(days=365)
        else:
            return datetime.min
    
    def _aggregate_events(
        self, 
        events: List[StatisticsEvent]
    ) -> AggregatedStats:
        """Aggregate statistics from events."""
        stats = AggregatedStats()
        
        for event in events:
            if event.type == EventType.RECORDING:
                stats.recordings_count += 1
                if event.duration_seconds:
                    stats.total_recording_time_seconds += event.duration_seconds
            
            elif event.type == EventType.TRANSCRIPTION:
                stats.transcriptions_count += 1
                if event.duration_seconds:
                    stats.total_transcribed_audio_time_seconds += event.duration_seconds
                if event.character_count:
                    stats.total_character_count += event.character_count
                if event.word_count:
                    stats.total_word_count += event.word_count
            
            elif event.type == EventType.SILENCE_REMOVED:
                if event.removed_duration_seconds:
                    stats.total_removed_silence_seconds += event.removed_duration_seconds
        
        return stats
```

**Key Design Decisions:**

1. **Event-based tracking**: Each action (recording, transcription, silence removal) creates a separate event with a timestamp
2. **Lazy loading**: Statistics are only loaded from disk when first accessed
3. **Immediate persistence**: Each new event is immediately saved to prevent data loss
4. **Flexible aggregation**: Events can be filtered by any time period and aggregated on-demand

### 2. Statistics Tab (`ui/statistics_tab.py`)

The Statistics Tab provides the user interface for viewing statistics.

```python
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt
from typing import Dict
from core.statistics_manager import StatisticsManager, TimePeriod, AggregatedStats

class MetricCard(QFrame):
    """A card displaying a single metric."""
    
    def __init__(self, label: str, value: str, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            MetricCard {
                background-color: #f5f5f5;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        self.label_widget = QLabel(label)
        self.label_widget.setStyleSheet("font-size: 12px; color: #666;")
        
        self.value_widget = QLabel(value)
        self.value_widget.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        layout.addWidget(self.label_widget)
        layout.addWidget(self.value_widget)
    
    def update_value(self, value: str):
        """Update the displayed value."""
        self.value_widget.setText(value)

class StatisticsTab(QWidget):
    """Tab for displaying usage statistics."""
    
    def __init__(self, statistics_manager: StatisticsManager, parent=None):
        super().__init__(parent)
        self.statistics_manager = statistics_manager
        self.metric_cards: Dict[str, MetricCard] = {}
        self._init_ui()
        self._load_statistics(TimePeriod.LAST_7_DAYS)
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Time period filter
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Time Period:")
        self.period_combo = QComboBox()
        self.period_combo.addItem("Today", TimePeriod.TODAY)
        self.period_combo.addItem("Last 7 Days", TimePeriod.LAST_7_DAYS)
        self.period_combo.addItem("Last 30 Days", TimePeriod.LAST_30_DAYS)
        self.period_combo.addItem("Last 365 Days", TimePeriod.LAST_365_DAYS)
        self.period_combo.addItem("All Time", TimePeriod.ALL_TIME)
        self.period_combo.setCurrentIndex(1)  # Default to Last 7 Days
        self.period_combo.currentIndexChanged.connect(self._on_period_changed)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.period_combo)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Metrics grid
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(16)
        
        # Create metric cards
        self.metric_cards['recordings'] = MetricCard("Recordings", "0")
        self.metric_cards['transcriptions'] = MetricCard("Transcriptions", "0")
        self.metric_cards['recording_time'] = MetricCard("Total Recording Time", "00:00")
        self.metric_cards['transcribed_time'] = MetricCard("Total Transcribed Audio", "00:00")
        self.metric_cards['characters'] = MetricCard("Characters", "0")
        self.metric_cards['words'] = MetricCard("Words", "0")
        self.metric_cards['silence'] = MetricCard("Removed Silence", "00:00")
        
        # Add cards to grid (2 columns)
        metrics_grid.addWidget(self.metric_cards['recordings'], 0, 0)
        metrics_grid.addWidget(self.metric_cards['transcriptions'], 0, 1)
        metrics_grid.addWidget(self.metric_cards['recording_time'], 1, 0)
        metrics_grid.addWidget(self.metric_cards['transcribed_time'], 1, 1)
        metrics_grid.addWidget(self.metric_cards['characters'], 2, 0)
        metrics_grid.addWidget(self.metric_cards['words'], 2, 1)
        metrics_grid.addWidget(self.metric_cards['silence'], 3, 0)
        
        layout.addLayout(metrics_grid)
        layout.addStretch()
    
    def _on_period_changed(self):
        """Handle time period selection change."""
        period = self.period_combo.currentData()
        self._load_statistics(period)
    
    def _load_statistics(self, period: TimePeriod):
        """Load and display statistics for the selected period."""
        stats = self.statistics_manager.get_statistics(period)
        self._update_display(stats)
    
    def _update_display(self, stats: AggregatedStats):
        """Update the display with aggregated statistics."""
        self.metric_cards['recordings'].update_value(str(stats.recordings_count))
        self.metric_cards['transcriptions'].update_value(str(stats.transcriptions_count))
        
        self.metric_cards['recording_time'].update_value(
            self._format_duration(stats.total_recording_time_seconds)
        )
        self.metric_cards['transcribed_time'].update_value(
            self._format_duration(stats.total_transcribed_audio_time_seconds)
        )
        
        self.metric_cards['characters'].update_value(
            self._format_number(stats.total_character_count)
        )
        self.metric_cards['words'].update_value(
            self._format_number(stats.total_word_count)
        )
        
        self.metric_cards['silence'].update_value(
            self._format_duration(stats.total_removed_silence_seconds)
        )
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to HH:MM or MM:SS."""
        total_seconds = int(seconds)
        
        if total_seconds >= 3600:  # 1 hour or more
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours:02d}:{minutes:02d}"
        else:
            minutes = total_seconds // 60
            secs = total_seconds % 60
            return f"{minutes:02d}:{secs:02d}"
    
    def _format_number(self, number: int) -> str:
        """Format number with thousand separators."""
        return f"{number:,}"
```

**Key Design Decisions:**

1. **Card-based layout**: Each metric is displayed in a visually distinct card
2. **Responsive updates**: Statistics update immediately when the time period changes
3. **Smart formatting**: Durations and numbers are formatted for readability
4. **Consistent styling**: Follows PyQt6 patterns used elsewhere in RapidWhisper

### 3. Settings Window Integration

The Statistics Tab is integrated into the existing Settings Window by adding it as a new tab.

```python
# In ui/settings_window.py

from ui.statistics_tab import StatisticsTab

class SettingsWindow(QDialog):
    def __init__(self, statistics_manager: StatisticsManager, ...):
        # ... existing initialization ...
        
        # Add statistics tab
        self.statistics_tab = StatisticsTab(statistics_manager, self)
        self.tabs.addTab(self.statistics_tab, "📊 Statistics")
```

## Data Models

### Statistics Event Schema

Each event stored in `statistics.json` follows this schema:

```json
{
  "events": [
    {
      "type": "recording",
      "timestamp": "2024-01-15T14:30:00.123456+00:00",
      "duration_seconds": 125.5,
      "character_count": null,
      "word_count": null,
      "removed_duration_seconds": null
    },
    {
      "type": "transcription",
      "timestamp": "2024-01-15T14:32:15.789012+00:00",
      "duration_seconds": 125.5,
      "character_count": 542,
      "word_count": 98,
      "removed_duration_seconds": null
    },
    {
      "type": "silence_removed",
      "timestamp": "2024-01-15T14:31:00.456789+00:00",
      "duration_seconds": null,
      "character_count": null,
      "word_count": null,
      "removed_duration_seconds": 15.3
    }
  ]
}
```

**Field Descriptions:**

- `type`: Event type (recording, transcription, silence_removed)
- `timestamp`: ISO 8601 timestamp with timezone
- `duration_seconds`: Audio duration (for recording and transcription events)
- `character_count`: Number of characters (for transcription events only)
- `word_count`: Number of words (for transcription events only)
- `removed_duration_seconds`: Duration of removed silence (for silence_removed events only)

### Aggregated Statistics Model

The `AggregatedStats` dataclass represents computed statistics for a time period:

```python
@dataclass
class AggregatedStats:
    recordings_count: int              # Total number of recordings
    transcriptions_count: int          # Total number of transcriptions
    total_recording_time_seconds: float    # Sum of all recording durations
    total_transcribed_audio_time_seconds: float  # Sum of all transcribed audio durations
    total_character_count: int         # Sum of all characters
    total_word_count: int              # Sum of all words
    total_removed_silence_seconds: float   # Sum of all removed silence
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Event Tracking Increments Counters

*For any* sequence of events (recordings, transcriptions, silence removals), tracking each event should increment the corresponding counter by exactly one, and the final count should equal the number of events tracked.

**Validates: Requirements 1.1, 2.1**

### Property 2: Event Data Persistence

*For any* event with associated data (duration, character count, word count, removed silence), after tracking the event, retrieving statistics should return the exact same data values that were provided.

**Validates: Requirements 1.2, 2.2, 2.3, 2.4, 3.1**

### Property 3: Timestamp Storage

*For any* tracked event, the stored timestamp should be within a few seconds of the current time when the event was tracked, and should be parseable as an ISO 8601 datetime.

**Validates: Requirements 1.3, 2.5, 3.2, 6.5**

### Property 4: Aggregation Correctness

*For any* set of events, the aggregated statistics (total recording time, total transcribed audio time, total removed silence, total characters, total words) should equal the sum of the individual event values.

**Validates: Requirements 1.4, 3.3**

### Property 5: Time Period Filtering

*For any* set of events with different timestamps and any time period filter (Today, Last 7 Days, Last 30 Days, Last 365 Days, All Time), the filtered statistics should include only events whose timestamps fall within the specified period, and the "All Time" filter should include all events.

**Validates: Requirements 1.5, 3.4, 4.2, 4.3, 4.4, 4.5, 4.6**

### Property 6: Storage Round-Trip

*For any* set of events, after saving them to storage and then loading from storage, the loaded events should be equivalent to the original events (same type, timestamp, and all data fields).

**Validates: Requirements 5.2, 5.3, 5.5**

### Property 7: UTF-8 Encoding Support

*For any* transcription text containing non-ASCII characters (Cyrillic, emoji, Chinese, etc.), after tracking the transcription and reloading from storage, the character and word counts should be preserved correctly.

**Validates: Requirements 5.6**

### Property 8: Event Schema Validation

*For any* event stored in statistics.json, the JSON object should contain the correct fields for its event type: recording events have (type, timestamp, duration_seconds), transcription events have (type, timestamp, duration_seconds, character_count, word_count), and silence_removed events have (type, timestamp, removed_duration_seconds).

**Validates: Requirements 6.2, 6.3, 6.4**

### Property 9: Duration Formatting

*For any* duration in seconds, the formatted string should use "MM:SS" format when the duration is less than 60 minutes, and "HH:MM" format when the duration is 60 minutes or more, with proper zero-padding.

**Validates: Requirements 3.5, 7.3, 7.4**

### Property 10: Number Formatting

*For any* integer count (characters, words), the formatted string should include thousand separators (commas) for numbers >= 1000.

**Validates: Requirements 7.5**

### Property 11: Corrupted File Handling

*For any* corrupted or invalid JSON file in the statistics storage location, loading statistics should not crash the application, should log an error, and should initialize with empty statistics.

**Validates: Requirements 6.6, 10.1, 10.3**

### Property 12: Invalid Event Handling

*For any* statistics file containing some valid events and some invalid events (unparseable timestamps, missing required fields), loading should skip the invalid events, log errors for them, and successfully load all valid events.

**Validates: Requirements 10.4**

### Property 13: Input Validation

*For any* attempt to track an event with negative numeric values (negative duration, negative counts), the Statistics Manager should either reject the event or normalize the values to non-negative before storing.

**Validates: Requirements 10.5**

### Property 14: Write Performance

*For any* single event, writing it to storage should complete in under 100 milliseconds on a standard system.

**Validates: Requirements 11.1**

### Property 15: Load Performance

*For any* statistics file containing up to 10,000 events, loading the statistics should complete in under 500 milliseconds on a standard system.

**Validates: Requirements 11.2**

### Property 16: Filter Performance

*For any* set of loaded events and any time period filter, filtering and aggregating the statistics should complete in under 200 milliseconds on a standard system.

**Validates: Requirements 11.3**

### Property 17: Lazy Loading

*For any* Statistics Manager instance, the statistics file should not be read from disk until the first call to get_statistics() or track_event(), ensuring no unnecessary I/O on application startup.

**Validates: Requirements 11.5**

## Error Handling

### File System Errors

1. **Missing Config Directory**: If the config directory doesn't exist, create it automatically
2. **Missing Statistics File**: If statistics.json doesn't exist, create it with an empty events array
3. **Corrupted JSON**: If the file contains invalid JSON:
   - Create a backup file (statistics.json.backup)
   - Log the error with details
   - Initialize with empty statistics
   - Continue normal operation

4. **Permission Errors**: If the file cannot be written:
   - Log the error
   - Continue operation (statistics will be lost on restart)
   - Don't crash the application

### Data Validation Errors

1. **Invalid Timestamps**: Skip events with unparseable timestamps, log warning
2. **Missing Required Fields**: Skip events missing required fields, log warning
3. **Invalid Event Types**: Skip events with unknown types, log warning
4. **Negative Values**: Normalize negative numeric values to zero, log warning

### UI Errors

1. **Empty Statistics**: Display "No data available for this period" message
2. **Load Failures**: Display error message in the tab instead of crashing
3. **Filter Errors**: Fall back to "All Time" filter if selected filter fails

## Testing Strategy

The Usage Statistics feature will be tested using a dual approach combining unit tests and property-based tests.

### Unit Testing

Unit tests will focus on:

1. **Specific Examples**:
   - Test tracking a single recording event
   - Test tracking a single transcription event
   - Test tracking a single silence removal event
   - Test the "Today" filter with events from today and yesterday
   - Test the "All Time" filter includes all events

2. **Edge Cases**:
   - Empty statistics (no events)
   - Statistics file doesn't exist (first run)
   - Events with zero duration
   - Transcription with empty text
   - Very large numbers (millions of characters)

3. **Error Conditions**:
   - Corrupted JSON file
   - File with invalid event types
   - File with missing required fields
   - Read-only statistics file
   - Invalid timestamps

4. **Integration Points**:
   - Statistics Manager integration with file system
   - Statistics Tab integration with Statistics Manager
   - Settings Window integration with Statistics Tab

### Property-Based Testing

Property-based tests will verify universal properties across randomized inputs using the Hypothesis library for Python. Each property test will run a minimum of 100 iterations.

**Test Configuration**:
- Library: Hypothesis (Python property-based testing)
- Minimum iterations: 100 per property
- Tag format: `# Feature: usage-statistics, Property N: [property description]`

**Properties to Test**:

1. **Property 1: Event Tracking Increments Counters**
   - Generate: Random sequences of events
   - Verify: Counter equals number of events tracked
   - Tag: `# Feature: usage-statistics, Property 1: Event Tracking Increments Counters`

2. **Property 2: Event Data Persistence**
   - Generate: Random events with random data values
   - Verify: Retrieved data matches stored data
   - Tag: `# Feature: usage-statistics, Property 2: Event Data Persistence`

3. **Property 3: Timestamp Storage**
   - Generate: Random events at different times
   - Verify: Timestamps are recent and ISO 8601 parseable
   - Tag: `# Feature: usage-statistics, Property 3: Timestamp Storage`

4. **Property 4: Aggregation Correctness**
   - Generate: Random sets of events with random values
   - Verify: Aggregated totals equal sum of individual values
   - Tag: `# Feature: usage-statistics, Property 4: Aggregation Correctness`

5. **Property 5: Time Period Filtering**
   - Generate: Random events with timestamps across different periods
   - Verify: Filtered results include only events in the period
   - Tag: `# Feature: usage-statistics, Property 5: Time Period Filtering`

6. **Property 6: Storage Round-Trip**
   - Generate: Random sets of events
   - Verify: Save then load produces equivalent events
   - Tag: `# Feature: usage-statistics, Property 6: Storage Round-Trip`

7. **Property 7: UTF-8 Encoding Support**
   - Generate: Random text with non-ASCII characters
   - Verify: Character/word counts preserved after round-trip
   - Tag: `# Feature: usage-statistics, Property 7: UTF-8 Encoding Support`

8. **Property 8: Event Schema Validation**
   - Generate: Random events of each type
   - Verify: Stored JSON has correct fields for event type
   - Tag: `# Feature: usage-statistics, Property 8: Event Schema Validation`

9. **Property 9: Duration Formatting**
   - Generate: Random durations from 0 to 10 hours
   - Verify: Format is MM:SS for <60min, HH:MM for >=60min
   - Tag: `# Feature: usage-statistics, Property 9: Duration Formatting`

10. **Property 10: Number Formatting**
    - Generate: Random integers from 0 to 1 million
    - Verify: Numbers >=1000 have thousand separators
    - Tag: `# Feature: usage-statistics, Property 10: Number Formatting`

11. **Property 11: Corrupted File Handling**
    - Generate: Random invalid JSON content
    - Verify: Loading doesn't crash, returns empty statistics
    - Tag: `# Feature: usage-statistics, Property 11: Corrupted File Handling`

12. **Property 12: Invalid Event Handling**
    - Generate: Mix of valid and invalid events
    - Verify: Valid events loaded, invalid events skipped
    - Tag: `# Feature: usage-statistics, Property 12: Invalid Event Handling`

13. **Property 13: Input Validation**
    - Generate: Events with negative values
    - Verify: Values are rejected or normalized to non-negative
    - Tag: `# Feature: usage-statistics, Property 13: Input Validation`

14. **Property 14: Write Performance**
    - Generate: Random single events
    - Verify: Write completes in <100ms
    - Tag: `# Feature: usage-statistics, Property 14: Write Performance`

15. **Property 15: Load Performance**
    - Generate: Files with up to 10,000 events
    - Verify: Load completes in <500ms
    - Tag: `# Feature: usage-statistics, Property 15: Load Performance`

16. **Property 16: Filter Performance**
    - Generate: Random event sets and filters
    - Verify: Filtering completes in <200ms
    - Tag: `# Feature: usage-statistics, Property 16: Filter Performance`

17. **Property 17: Lazy Loading**
    - Generate: Statistics Manager instances
    - Verify: File not read until first get_statistics() or track_event()
    - Tag: `# Feature: usage-statistics, Property 17: Lazy Loading`

### Test Organization

```
tests/
├── unit/
│   ├── test_statistics_manager.py      # Unit tests for Statistics Manager
│   ├── test_statistics_tab.py          # Unit tests for Statistics Tab
│   └── test_integration.py             # Integration tests
└── property/
    ├── test_statistics_properties.py   # Property-based tests for all properties
    └── generators.py                   # Custom Hypothesis generators
```

### Testing Tools

- **pytest**: Test runner and framework
- **Hypothesis**: Property-based testing library
- **pytest-qt**: PyQt6 testing utilities
- **pytest-mock**: Mocking utilities for file system operations
