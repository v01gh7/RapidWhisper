# Requirements Document

## Introduction

This specification defines the Usage Statistics feature for the RapidWhisper application. The feature adds a new "Statistics" tab to the Settings Window that displays comprehensive usage metrics about recordings and transcriptions. Users can view statistics filtered by different time periods (day, week, month, year, all time) to understand their application usage patterns. All data is stored locally in JSON format to ensure privacy and offline functionality.

## Glossary

- **Statistics_Tab**: The new tab in Settings_Window displaying usage metrics
- **Statistics_Manager**: The component responsible for collecting, storing, and retrieving usage statistics
- **Statistics_Storage**: The JSON file (statistics.json) storing all usage data in the application configuration directory
- **Recording_Event**: A single audio recording session captured by the application
- **Transcription_Event**: A single text transcription generated from audio
- **Time_Filter**: The selected time period for filtering statistics (day/week/month/year/all time)
- **Metric_Card**: A UI component displaying a single statistic value with label
- **Silence_Removal**: The audio processing feature that removes silent portions from recordings
- **Config_Directory**: The application configuration folder where statistics.json is stored

## Requirements

### Requirement 1: Recording Statistics Tracking

**User Story:** As a user, I want to see how many recordings I've created, so that I can understand my usage patterns.

#### Acceptance Criteria

1. WHEN a recording is successfully completed, THE Statistics_Manager SHALL increment the total recordings counter
2. WHEN a recording is completed, THE Statistics_Manager SHALL store the recording duration in seconds
3. WHEN a recording is completed, THE Statistics_Manager SHALL store a timestamp for the recording event
4. THE Statistics_Manager SHALL calculate total recording time by summing all recording durations
5. WHEN displaying recording statistics, THE Statistics_Tab SHALL show the count of recordings for the selected Time_Filter

### Requirement 2: Transcription Statistics Tracking

**User Story:** As a user, I want to see how many transcriptions I've created and their content metrics, so that I can track my productivity.

#### Acceptance Criteria

1. WHEN a transcription is successfully completed, THE Statistics_Manager SHALL increment the total transcriptions counter
2. WHEN a transcription is completed, THE Statistics_Manager SHALL store the transcribed audio duration in seconds
3. WHEN a transcription is completed, THE Statistics_Manager SHALL count and store the number of characters in the transcribed text
4. WHEN a transcription is completed, THE Statistics_Manager SHALL count and store the number of words in the transcribed text
5. WHEN a transcription is completed, THE Statistics_Manager SHALL store a timestamp for the transcription event

### Requirement 3: Silence Removal Statistics Tracking

**User Story:** As a user, I want to see how much silence was removed from my recordings, so that I can understand the efficiency of audio processing.

#### Acceptance Criteria

1. WHEN silence removal processing completes, THE Statistics_Manager SHALL calculate the duration of removed silence in seconds
2. WHEN silence removal processing completes, THE Statistics_Manager SHALL store the removed silence duration with a timestamp
3. THE Statistics_Manager SHALL calculate total removed silence by summing all removal durations
4. WHEN displaying silence statistics, THE Statistics_Tab SHALL show the total removed silence for the selected Time_Filter
5. THE Statistics_Tab SHALL format removed silence duration in minutes and seconds or hours and minutes based on magnitude

### Requirement 4: Time Period Filtering

**User Story:** As a user, I want to filter statistics by different time periods, so that I can analyze my usage over specific timeframes.

#### Acceptance Criteria

1. THE Statistics_Tab SHALL provide a dropdown selector with options: "Today", "Last 7 Days", "Last 30 Days", "Last 365 Days", "All Time"
2. WHEN a user selects "Today", THE Statistics_Tab SHALL display metrics for events with timestamps from 00:00:00 today to current time
3. WHEN a user selects "Last 7 Days", THE Statistics_Tab SHALL display metrics for events from the last 7 complete days plus today
4. WHEN a user selects "Last 30 Days", THE Statistics_Tab SHALL display metrics for events from the last 30 complete days plus today
5. WHEN a user selects "Last 365 Days", THE Statistics_Tab SHALL display metrics for events from the last 365 complete days plus today
6. WHEN a user selects "All Time", THE Statistics_Tab SHALL display metrics for all recorded events regardless of timestamp
7. WHEN the Time_Filter changes, THE Statistics_Tab SHALL recalculate and update all displayed metrics immediately

### Requirement 5: Statistics Data Persistence

**User Story:** As a user, I want my statistics data saved locally, so that my usage history persists across application restarts and remains private.

#### Acceptance Criteria

1. THE Statistics_Manager SHALL store all statistics data in a file named "statistics.json" in the Config_Directory
2. WHEN a new statistic event occurs, THE Statistics_Manager SHALL append the event data to Statistics_Storage
3. WHEN the application starts, THE Statistics_Manager SHALL load existing statistics from Statistics_Storage
4. IF Statistics_Storage does not exist, THEN THE Statistics_Manager SHALL create it with an empty events array
5. THE Statistics_Manager SHALL write to Statistics_Storage immediately after each event to prevent data loss
6. THE Statistics_Storage SHALL use UTF-8 encoding to support all languages

### Requirement 6: Statistics Data Format

**User Story:** As a developer, I want statistics stored in a structured format, so that data can be easily queried and extended in the future.

#### Acceptance Criteria

1. THE Statistics_Storage SHALL use JSON format with a root object containing an "events" array
2. WHEN storing a recording event, THE Statistics_Manager SHALL include fields: type="recording", timestamp (ISO 8601), duration_seconds
3. WHEN storing a transcription event, THE Statistics_Manager SHALL include fields: type="transcription", timestamp (ISO 8601), audio_duration_seconds, character_count, word_count
4. WHEN storing a silence removal event, THE Statistics_Manager SHALL include fields: type="silence_removed", timestamp (ISO 8601), removed_duration_seconds
5. THE Statistics_Manager SHALL store timestamps in ISO 8601 format with timezone information
6. THE Statistics_Manager SHALL validate JSON structure when reading Statistics_Storage and handle corrupted files gracefully

### Requirement 7: Statistics Display UI

**User Story:** As a user, I want statistics displayed in an attractive and readable format, so that I can quickly understand my usage metrics.

#### Acceptance Criteria

1. THE Statistics_Tab SHALL display each metric in a Metric_Card with a label and value
2. THE Statistics_Tab SHALL display metrics in this order: recordings count, transcriptions count, total recording time, total transcribed audio time, character count, word count, removed silence
3. WHEN displaying time durations under 60 minutes, THE Statistics_Tab SHALL format as "MM:SS" (minutes:seconds)
4. WHEN displaying time durations of 60 minutes or more, THE Statistics_Tab SHALL format as "HH:MM" (hours:minutes)
5. THE Statistics_Tab SHALL display character and word counts with thousand separators for readability
6. THE Statistics_Tab SHALL use consistent spacing and alignment for all Metric_Cards
7. THE Statistics_Tab SHALL display a message "No data available for this period" when the selected Time_Filter returns zero events

### Requirement 8: Statistics Tab Integration

**User Story:** As a user, I want the Statistics tab easily accessible in the settings window, so that I can quickly check my usage metrics.

#### Acceptance Criteria

1. THE Settings_Window SHALL add a new tab labeled "📊 Statistics" (or translated equivalent)
2. THE Settings_Window SHALL position the Statistics tab between the "Recordings" tab and the "About" tab
3. WHEN the Statistics tab is opened, THE Statistics_Tab SHALL load and display current statistics for the default Time_Filter ("Last 7 Days")
4. THE Statistics_Tab SHALL update displayed metrics automatically when the Time_Filter selection changes
5. THE Settings_Window SHALL maintain the Statistics tab selection when the settings window is reopened during the same application session

### Requirement 9: Multilingual Support

**User Story:** As a user, I want statistics displayed in my preferred language, so that I can understand the metrics in my native language.

#### Acceptance Criteria

1. WHEN the Translation_System loads English translations, THE Translation_System SHALL include all statistics-related keys with English text
2. WHEN the Translation_System loads Russian translations, THE Translation_System SHALL include all statistics-related keys with Russian text
3. THE Statistics_Tab SHALL display the tab title using the translated "statistics.title" key
4. THE Statistics_Tab SHALL display all metric labels using their corresponding translation keys
5. THE Statistics_Tab SHALL display the Time_Filter dropdown options using translated keys
6. THE Statistics_Tab SHALL display the "No data available" message using the translated "statistics.no_data" key

### Requirement 10: Error Handling and Data Integrity

**User Story:** As a user, I want the application to handle statistics errors gracefully, so that statistics issues don't break the main application functionality.

#### Acceptance Criteria

1. IF Statistics_Storage cannot be read due to file corruption, THEN THE Statistics_Manager SHALL log an error and initialize with empty statistics
2. IF Statistics_Storage cannot be written due to permissions issues, THEN THE Statistics_Manager SHALL log an error and continue application operation
3. WHEN JSON parsing fails, THE Statistics_Manager SHALL create a backup of the corrupted file and initialize with empty statistics
4. IF a timestamp cannot be parsed, THEN THE Statistics_Manager SHALL skip that event and continue processing remaining events
5. THE Statistics_Manager SHALL validate that all numeric values (durations, counts) are non-negative before storing
6. WHEN the Statistics_Tab encounters an error loading data, THE Statistics_Tab SHALL display an error message instead of crashing

### Requirement 11: Performance and Efficiency

**User Story:** As a user, I want statistics tracking to have minimal impact on application performance, so that recording and transcription remain fast.

#### Acceptance Criteria

1. WHEN writing statistics to Storage, THE Statistics_Manager SHALL complete the write operation in under 100 milliseconds
2. WHEN loading statistics on application start, THE Statistics_Manager SHALL complete loading in under 500 milliseconds for files up to 10,000 events
3. WHEN filtering statistics by time period, THE Statistics_Tab SHALL complete filtering and display update in under 200 milliseconds
4. THE Statistics_Manager SHALL write to Statistics_Storage asynchronously to avoid blocking the main application thread
5. THE Statistics_Manager SHALL not load or parse Statistics_Storage until the Statistics_Tab is first opened by the user
