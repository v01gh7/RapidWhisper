"""Statistics Manager for tracking and aggregating usage statistics.

This module provides the core functionality for collecting, storing, and retrieving
usage statistics for the RapidWhisper application. Statistics are stored locally
in JSON format for privacy and offline functionality.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from enum import Enum


class EventType(Enum):
    """Types of statistics events."""
    RECORDING = "recording"
    TRANSCRIPTION = "transcription"
    SILENCE_REMOVED = "silence_removed"


@dataclass
class StatisticsEvent:
    """Represents a single statistics event.
    
    Attributes:
        type: The type of event (recording, transcription, or silence removal)
        timestamp: When the event occurred
        duration_seconds: Duration in seconds (for recording and transcribed audio)
        character_count: Number of characters (for transcription events)
        word_count: Number of words (for transcription events)
        removed_duration_seconds: Duration of removed silence (for silence removal events)
    """
    type: EventType
    timestamp: datetime
    duration_seconds: Optional[float] = None
    character_count: Optional[int] = None
    word_count: Optional[int] = None
    removed_duration_seconds: Optional[float] = None


class TimePeriod(Enum):
    """Time period filters for statistics."""
    TODAY = "today"
    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    LAST_365_DAYS = "last_365_days"
    ALL_TIME = "all_time"


@dataclass
class AggregatedStats:
    """Aggregated statistics for a time period.
    
    Attributes:
        recordings_count: Total number of recordings
        transcriptions_count: Total number of transcriptions
        total_recording_time_seconds: Sum of all recording durations
        total_transcribed_audio_time_seconds: Sum of all transcribed audio durations
        total_character_count: Sum of all characters transcribed
        total_word_count: Sum of all words transcribed
        total_removed_silence_seconds: Sum of all removed silence durations
    """
    recordings_count: int = 0
    transcriptions_count: int = 0
    total_recording_time_seconds: float = 0.0
    total_transcribed_audio_time_seconds: float = 0.0
    total_character_count: int = 0
    total_word_count: int = 0
    total_removed_silence_seconds: float = 0.0


class StatisticsManager:
    """Manages statistics collection, storage, and retrieval.
    
    The StatisticsManager is responsible for:
    - Tracking events (recordings, transcriptions, silence removal)
    - Persisting events to local JSON storage
    - Loading events from storage
    - Filtering events by time period
    - Aggregating statistics from events
    
    Statistics are stored in a JSON file in the application's config directory.
    The manager uses lazy loading - data is only loaded from disk when first accessed.
    """
    
    def __init__(self, config_dir: Path):
        """Initialize the statistics manager.
        
        Args:
            config_dir: Path to the application configuration directory where
                       statistics.json will be stored
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
        # Validate and normalize duration
        if duration_seconds < 0:
            print(f"Warning: Negative recording duration {duration_seconds}, normalizing to 0")
            duration_seconds = 0.0
        
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
        # Validate and normalize duration
        if audio_duration_seconds < 0:
            print(f"Warning: Negative audio duration {audio_duration_seconds}, normalizing to 0")
            audio_duration_seconds = 0.0
        
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
        # Validate and normalize duration
        if removed_duration_seconds < 0:
            print(f"Warning: Negative removed silence duration {removed_duration_seconds}, normalizing to 0")
            removed_duration_seconds = 0.0
        
        event = StatisticsEvent(
            type=EventType.SILENCE_REMOVED,
            timestamp=datetime.now(),
            removed_duration_seconds=removed_duration_seconds
        )
        self._add_event(event)
    
    def _add_event(self, event: StatisticsEvent) -> None:
        """Add an event and save to storage.
        
        Args:
            event: The StatisticsEvent to add
        """
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
        import json
        import shutil
        
        if not self.storage_path.exists():
            self.events = []
            return
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Validate that data is a dictionary
                if not isinstance(data, dict):
                    print(f"Warning: JSON root is not a dictionary, got {type(data).__name__}")
                    self.events = []
                    return
                
                events_data = data.get('events', [])
                
                # Validate that events is a list
                if not isinstance(events_data, list):
                    print(f"Warning: 'events' is not a list, got {type(events_data).__name__}")
                    events_data = []
                
                self.events = self._deserialize_events(events_data)
        except UnicodeDecodeError as e:
            # Binary file or encoding issue - create backup and start fresh
            backup_path = self.storage_path.with_suffix('.json.backup')
            try:
                shutil.copy2(self.storage_path, backup_path)
                print(f"Unicode decode error: {e}. Created backup at {backup_path}")
            except IOError as backup_error:
                print(f"Failed to create backup: {backup_error}")
            print(f"Error loading statistics: {e}")
            self.events = []
        except json.JSONDecodeError as e:
            # Create backup of corrupted file and start with empty statistics
            backup_path = self.storage_path.with_suffix('.json.backup')
            try:
                shutil.copy2(self.storage_path, backup_path)
                print(f"JSON decode error: {e}. Created backup at {backup_path}")
            except IOError as backup_error:
                print(f"Failed to create backup: {backup_error}")
            print(f"Error loading statistics: {e}")
            self.events = []
        except IOError as e:
            # Log error and start with empty statistics
            print(f"Error loading statistics: {e}")
            self.events = []
    
    def _save_to_storage(self) -> None:
        """Save statistics to JSON file."""
        import json
        
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            data = {'events': self._serialize_events(self.events)}
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving statistics: {e}")
    
    def _serialize_events(self, events: List[StatisticsEvent]) -> List[dict]:
        """Convert events to JSON-serializable format.
        
        Args:
            events: List of StatisticsEvent objects to serialize
            
        Returns:
            List of dictionaries representing the events
        """
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
    
    def _deserialize_events(self, data: List[dict]) -> List[StatisticsEvent]:
        """Convert JSON data to StatisticsEvent objects.
        
        Args:
            data: List of dictionaries representing events
            
        Returns:
            List of StatisticsEvent objects
        """
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
    
    def _filter_events_by_period(
        self, 
        period: TimePeriod
    ) -> List[StatisticsEvent]:
        """Filter events by time period.
        
        Args:
            period: The time period to filter by
            
        Returns:
            List of events within the specified period
        """
        if period == TimePeriod.ALL_TIME:
            return self.events
        
        now = datetime.now()
        cutoff_time = self._get_cutoff_time(now, period)
        
        return [
            event for event in self.events 
            if event.timestamp >= cutoff_time
        ]
    
    def _get_cutoff_time(self, now: datetime, period: TimePeriod) -> datetime:
        """Calculate the cutoff time for a period.
        
        Args:
            now: The current datetime
            period: The time period
            
        Returns:
            The cutoff datetime for filtering
        """
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
        """Aggregate statistics from events.
        
        Args:
            events: List of events to aggregate
            
        Returns:
            Aggregated statistics
        """
        stats = AggregatedStats()
        
        for event in events:
            if event.type == EventType.RECORDING:
                stats.recordings_count += 1
                if event.duration_seconds and event.duration_seconds >= 0:
                    stats.total_recording_time_seconds += event.duration_seconds
            
            elif event.type == EventType.TRANSCRIPTION:
                stats.transcriptions_count += 1
                if event.duration_seconds and event.duration_seconds >= 0:
                    stats.total_transcribed_audio_time_seconds += event.duration_seconds
                if event.character_count and event.character_count >= 0:
                    stats.total_character_count += event.character_count
                if event.word_count and event.word_count >= 0:
                    stats.total_word_count += event.word_count
            
            elif event.type == EventType.SILENCE_REMOVED:
                if event.removed_duration_seconds and event.removed_duration_seconds >= 0:
                    stats.total_removed_silence_seconds += event.removed_duration_seconds
        
        return stats
