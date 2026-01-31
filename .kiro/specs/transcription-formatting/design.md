# Design Document: Transcription Formatting

## Overview

The Transcription Formatting feature adds intelligent, context-aware formatting to transcribed text based on the active application window. The system detects which application the user is working in (e.g., Notion, Obsidian, Word, Markdown files) and applies appropriate formatting rules using AI-powered text transformation.

The feature is designed as a modular component that integrates seamlessly with the existing transcription pipeline. It maintains its own AI provider configuration to avoid conflicts with transcription and post-processing settings, while intelligently combining operations when both formatting and post-processing are enabled to minimize API calls.

**Key Design Principles:**
- **Modularity**: Formatting is a self-contained module with clear interfaces
- **Efficiency**: Combines formatting with post-processing when both are enabled
- **Flexibility**: Users can configure different AI providers for different purposes
- **Robustness**: Gracefully handles failures by returning unformatted text
- **Reusability**: Leverages existing infrastructure (AI clients, window monitoring)

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Transcription System                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Transcription Pipeline                     │
│  ┌────────────┐    ┌──────────────┐    ┌────────────────┐  │
│  │  Audio     │───▶│ Transcription│───▶│  Processing    │  │
│  │  Input     │    │   Engine     │    │   Pipeline     │  │
│  └────────────┘    └──────────────┘    └────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Processing Pipeline                       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Processing Decision Logic                   │  │
│  │  • Check formatting enabled                           │  │
│  │  • Check post-processing enabled                      │  │
│  │  • Get active window from Window_Monitor              │  │
│  │  • Match against Format_Configuration                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                               │
│              ┌───────────────┼───────────────┐              │
│              ▼               ▼               ▼              │
│  ┌─────────────────┐ ┌─────────────┐ ┌──────────────────┐ │
│  │  Formatting     │ │  Combined   │ │  Post-Processing │ │
│  │  Only           │ │  Operation  │ │  Only            │ │
│  │  (Format AI)    │ │  (Post AI)  │ │  (Post AI)       │ │
│  └─────────────────┘ └─────────────┘ └──────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Output Text                             │
└─────────────────────────────────────────────────────────────┘

Supporting Components:
┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐
│  Window_Monitor  │  │  AI_Client       │  │  Config       │
│  (Existing)      │  │  (Existing)      │  │  Manager      │
└──────────────────┘  └──────────────────┘  └───────────────┘
```

### Component Interactions

1. **Window_Monitor**: Detects active application and file extension
2. **Config_Manager**: Loads formatting configuration from .env
3. **Formatting_Module**: Core formatting logic and decision-making
4. **AI_Client**: Handles communication with AI providers
5. **Processing_Pipeline**: Orchestrates formatting and post-processing

### Data Flow

**Scenario 1: Formatting Only (Post-Processing Disabled)**
```
Transcription Text → Check Active Window → Match Format Config
                                                    │
                                                    ▼
                                            Format Matched?
                                                    │
                                    ┌───────────────┴───────────────┐
                                    ▼                               ▼
                            Yes: Send to                    No: Return
                            Formatting AI                   Original Text
                            with format prompt
                                    │
                                    ▼
                            Formatted Text
```

**Scenario 2: Combined Operation (Both Enabled)**
```
Transcription Text → Check Active Window → Match Format Config
                                                    │
                                                    ▼
                                            Format Matched?
                                                    │
                                    ┌───────────────┴───────────────┐
                                    ▼                               ▼
                            Yes: Combine prompts           No: Post-process
                            Send to Post-Processing AI      only
                            with extended prompt
                                    │
                                    ▼
                            Formatted + Post-Processed Text
```

## Components and Interfaces

### 1. Formatting Module

**File**: `formatting_module.py`

**Responsibilities:**
- Determine if formatting should be applied
- Match active window against configured applications
- Generate application-specific formatting prompts
- Coordinate with AI client for text transformation
- Handle formatting failures gracefully

**Interface:**

```python
class FormattingModule:
    """
    Handles automatic formatting of transcribed text based on active application.
    """
    
    def __init__(self, config_manager, ai_client_factory, window_monitor):
        """
        Initialize the formatting module.
        
        Args:
            config_manager: Configuration manager for loading settings
            ai_client_factory: Factory for creating AI client instances
            window_monitor: Window monitoring component
        """
        pass
    
    def should_format(self) -> bool:
        """
        Check if formatting is enabled in configuration.
        
        Returns:
            bool: True if formatting is enabled
        """
        pass
    
    def get_active_application_format(self) -> Optional[str]:
        """
        Detect active application and match against configured formats.
        
        Returns:
            Optional[str]: Format identifier (e.g., "notion", "obsidian", "markdown")
                          or None if no match
        """
        pass
    
    def format_text(self, text: str, format_type: str) -> str:
        """
        Format text for the specified application type.
        
        Args:
            text: Original transcribed text
            format_type: Target format (e.g., "notion", "obsidian")
        
        Returns:
            str: Formatted text, or original text if formatting fails
        """
        pass
    
    def get_format_prompt(self, format_type: str) -> str:
        """
        Generate application-specific formatting prompt.
        
        Args:
            format_type: Target format identifier
        
        Returns:
            str: System prompt for AI formatting
        """
        pass
    
    def process(self, text: str) -> str:
        """
        Main entry point for formatting pipeline.
        
        Args:
            text: Original transcribed text
        
        Returns:
            str: Formatted text if applicable, otherwise original text
        """
        pass
```

### 2. Processing Pipeline Coordinator

**File**: `processing_coordinator.py`

**Responsibilities:**
- Orchestrate formatting and post-processing
- Decide between formatting-only, combined, or post-processing-only modes
- Combine prompts when both operations are enabled
- Ensure single API call for combined operations

**Interface:**

```python
class ProcessingCoordinator:
    """
    Coordinates formatting and post-processing operations.
    """
    
    def __init__(self, formatting_module, post_processing_module):
        """
        Initialize the coordinator.
        
        Args:
            formatting_module: Formatting module instance
            post_processing_module: Post-processing module instance
        """
        pass
    
    def process_transcription(self, text: str) -> str:
        """
        Process transcribed text through formatting and/or post-processing.
        
        Decision logic:
        - If only formatting enabled: use formatting module
        - If only post-processing enabled: use post-processing module
        - If both enabled: combine operations in single AI call
        - If neither enabled: return original text
        
        Args:
            text: Original transcribed text
        
        Returns:
            str: Processed text
        """
        pass
    
    def combine_prompts(self, post_prompt: str, format_prompt: str) -> str:
        """
        Combine post-processing and formatting prompts into single prompt.
        
        Args:
            post_prompt: Post-processing system prompt
            format_prompt: Formatting system prompt
        
        Returns:
            str: Combined system prompt
        """
        pass
    
    def should_combine_operations(self) -> Tuple[bool, Optional[str]]:
        """
        Determine if operations should be combined.
        
        Returns:
            Tuple[bool, Optional[str]]: (should_combine, format_type)
        """
        pass
```

### 3. Configuration Manager Extension

**File**: `config_manager.py` (extend existing)

**New Configuration Fields:**

```python
class FormattingConfig:
    """Configuration for formatting feature."""
    
    enabled: bool  # FORMATTING_ENABLED
    provider: str  # FORMATTING_PROVIDER (groq/openai/glm/custom)
    model: str     # FORMATTING_MODEL
    applications: List[str]  # FORMATTING_APPLICATIONS (parsed from comma-separated)
    
    @classmethod
    def from_env(cls) -> 'FormattingConfig':
        """Load formatting configuration from environment variables."""
        pass
    
    def to_env(self) -> Dict[str, str]:
        """Convert configuration to environment variable format."""
        pass
```

### 4. Settings UI Extension

**File**: `processing_page.py` (extend existing)

**New UI Components:**

```python
class FormattingSettingsWidget(QGroupBox):
    """
    UI widget for formatting settings.
    """
    
    def __init__(self, parent=None):
        """Initialize the formatting settings widget."""
        super().__init__("Formatting (Форматирование)", parent)
        self.setup_ui()
    
    def setup_ui(self):
        """
        Create UI components:
        - Enable/disable checkbox
        - Provider dropdown (groq, openai, glm, custom)
        - Model input field
        - Applications list input field
        - Info label
        """
        pass
    
    def load_settings(self, config: FormattingConfig):
        """Load settings from configuration."""
        pass
    
    def save_settings(self) -> FormattingConfig:
        """Save settings to configuration."""
        pass
    
    def on_provider_changed(self, provider: str):
        """Handle provider selection change."""
        pass
```

## Data Models

### Configuration Data

```python
@dataclass
class FormattingConfig:
    """Formatting configuration data model."""
    
    enabled: bool = False
    provider: str = "groq"  # groq, openai, glm, custom
    model: str = ""
    applications: List[str] = field(default_factory=list)
    
    def is_valid(self) -> bool:
        """Validate configuration completeness."""
        return (
            self.provider in ["groq", "openai", "glm", "custom"] and
            bool(self.model) and
            bool(self.applications)
        )
```

### Format Mapping

```python
# Application name patterns to format identifiers
FORMAT_MAPPINGS = {
    "notion": ["notion", "notion.exe", "notion.app"],
    "obsidian": ["obsidian", "obsidian.exe", "obsidian.app"],
    "markdown": [".md", ".markdown"],
    "word": ["word", "winword.exe", "microsoft word", ".docx", ".doc"],
    "vscode": ["code", "vscode", "visual studio code", ".md"],
    "sublime": ["sublime", "sublime_text"],
    "notepad": ["notepad++", "notepad"],
}

def match_application_to_format(app_name: str, file_ext: str) -> Optional[str]:
    """
    Match detected application/file to a format type.
    
    Args:
        app_name: Active application name (lowercase)
        file_ext: Active file extension (with dot)
    
    Returns:
        Optional[str]: Format identifier or None
    """
    app_lower = app_name.lower()
    
    for format_type, patterns in FORMAT_MAPPINGS.items():
        for pattern in patterns:
            if pattern.startswith("."):
                # File extension match
                if file_ext == pattern:
                    return format_type
            else:
                # Application name match
                if pattern in app_lower:
                    return format_type
    
    return None
```

### Format Prompts

```python
FORMAT_PROMPTS = {
    "notion": """Format the text for Notion with:
- Use Notion-style markdown
- Add appropriate headings with #
- Use bullet points with - or •
- Add line breaks for readability
- Use **bold** and *italic* appropriately
- Keep paragraphs concise""",
    
    "obsidian": """Format the text for Obsidian with:
- Use standard markdown syntax
- Add appropriate headings with #
- Use - for bullet points
- Add [[wiki-links]] where appropriate
- Use tags with #tag format
- Keep structure clean for linking""",
    
    "markdown": """Format the text as clean markdown with:
- Use standard markdown syntax
- Add appropriate headings with #
- Use - for unordered lists
- Use 1. for ordered lists
- Add code blocks with ``` where appropriate
- Keep formatting minimal and readable""",
    
    "word": """Format the text for Microsoft Word with:
- Use clear paragraph breaks
- Add appropriate headings
- Use bullet points for lists
- Keep formatting simple (Word will handle styling)
- Avoid special markdown syntax
- Focus on content structure""",
}

def get_format_prompt(format_type: str) -> str:
    """
    Get formatting prompt for application type.
    
    Args:
        format_type: Format identifier
    
    Returns:
        str: Formatting instructions for AI
    """
    return FORMAT_PROMPTS.get(format_type, FORMAT_PROMPTS["markdown"])
```

## 
Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Configuration Independence

*For any* formatting configuration changes, modifying formatting settings (provider, model, applications) should not affect transcription or post-processing configuration values, and vice versa.

**Validates: Requirements 1.7, 4.5, 7.6**

### Property 2: Configuration Round-Trip Persistence

*For any* valid formatting configuration (enabled state, provider, model, applications list), saving the configuration then loading it should produce an equivalent configuration with all values preserved.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

### Property 3: Window Detection Completeness

*For any* active window state, the Window_Monitor should return complete information including both application name and file extension (when applicable).

**Validates: Requirements 3.1, 3.2, 3.3**

### Property 4: Application Format Matching

*For any* detected application name or file extension and any format configuration list, the matching logic should deterministically return the same format identifier (or None) for the same inputs.

**Validates: Requirements 3.4, 3.5**

### Property 5: Formatting Decision Logic

*For any* combination of formatting enabled/disabled, post-processing enabled/disabled, and active application match/no-match states, the system should make the correct processing decision (format-only, combined, post-only, or none).

**Validates: Requirements 4.1, 4.4, 5.1, 5.6**

### Property 6: Format-Specific Prompt Selection

*For any* supported format type (notion, obsidian, markdown, word, etc.), the system should generate an appropriate format-specific prompt that contains instructions relevant to that format.

**Validates: Requirements 4.2, 6.5**

### Property 7: Original Text Preservation on No-Match

*For any* transcription text, when the active application does not match any configured format, the system should return the original text completely unchanged.

**Validates: Requirements 4.4**

### Property 8: Single API Call for Combined Operations

*For any* text when both formatting and post-processing are enabled and format matches, the system should make exactly one AI API request (not two separate requests).

**Validates: Requirements 5.1, 5.4**

### Property 9: Combined Prompt Composition

*For any* post-processing prompt and formatting prompt, when combining operations, the resulting combined prompt should contain instructions from both prompts.

**Validates: Requirements 5.3**

### Property 10: Post-Processing Provider Priority

*For any* combined operation (formatting + post-processing), the system should use the post-processing AI provider configuration, not the formatting provider configuration.

**Validates: Requirements 5.2, 5.7**

### Property 11: Provider Configuration Selection

*For any* formatting request (when not combined with post-processing), the system should use the configured Formatting_AI_Provider and model, not the transcription or post-processing provider.

**Validates: Requirements 7.2, 7.3**

### Property 12: Graceful Failure Handling

*For any* AI request failure during formatting, the system should return the original unformatted text and log an error, ensuring no data loss.

**Validates: Requirements 7.4, 7.5**

## Error Handling

### Error Scenarios and Responses

1. **AI Provider Connection Failure**
   - **Scenario**: Network error or provider unavailable
   - **Response**: Return original unformatted text, log error with details
   - **User Impact**: Minimal - user gets unformatted but complete transcription

2. **Invalid Configuration**
   - **Scenario**: Missing provider, empty model, or empty applications list
   - **Response**: Disable formatting automatically, log warning
   - **User Impact**: Formatting silently disabled until configuration fixed

3. **Window Detection Failure**
   - **Scenario**: Unable to detect active window
   - **Response**: Skip formatting, return original text
   - **User Impact**: No formatting applied, but transcription works

4. **Malformed AI Response**
   - **Scenario**: AI returns empty or invalid response
   - **Response**: Return original text, log error
   - **User Impact**: User gets original transcription

5. **Configuration File Corruption**
   - **Scenario**: .env file corrupted or unreadable
   - **Response**: Use default configuration values
   - **User Impact**: Settings reset to defaults

### Error Logging Strategy

```python
import logging

logger = logging.getLogger("formatting_module")

# Error levels:
# - ERROR: AI failures, configuration errors
# - WARNING: Invalid configuration, window detection issues
# - INFO: Formatting applied successfully
# - DEBUG: Detailed flow information

def log_formatting_error(error_type: str, details: dict):
    """
    Log formatting errors with context.
    
    Args:
        error_type: Type of error (ai_failure, config_invalid, etc.)
        details: Additional context (provider, model, error message)
    """
    logger.error(
        f"Formatting error: {error_type}",
        extra={
            "error_type": error_type,
            "timestamp": datetime.now().isoformat(),
            **details
        }
    )
```

### Fallback Behavior

The system follows a "fail-safe" approach:
- **Primary goal**: Never lose transcribed text
- **Secondary goal**: Provide formatted output when possible
- **Fallback chain**: Formatted → Original → Error message

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests for comprehensive coverage:

**Unit Tests** focus on:
- Specific UI component creation and layout
- Specific format examples (Notion, Obsidian, Word, Markdown)
- Error handling edge cases
- Configuration file parsing
- Integration between components

**Property-Based Tests** focus on:
- Configuration persistence across all possible values
- Format matching logic across all application names
- Decision logic across all state combinations
- Provider selection across all configurations
- Failure handling across all error types

### Property-Based Testing Configuration

**Library**: Use `hypothesis` for Python property-based testing

**Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with feature name and property number
- Tag format: `# Feature: transcription-formatting, Property {N}: {property_text}`

**Example Property Test Structure**:

```python
from hypothesis import given, strategies as st
import pytest

@given(
    enabled=st.booleans(),
    provider=st.sampled_from(["groq", "openai", "glm", "custom"]),
    model=st.text(min_size=1, max_size=50),
    applications=st.lists(st.text(min_size=1, max_size=20), min_size=1)
)
@pytest.mark.property_test
def test_config_round_trip_persistence(enabled, provider, model, applications):
    """
    Feature: transcription-formatting, Property 2: Configuration Round-Trip Persistence
    
    For any valid formatting configuration, saving then loading should preserve all values.
    """
    # Create configuration
    config = FormattingConfig(
        enabled=enabled,
        provider=provider,
        model=model,
        applications=applications
    )
    
    # Save to file
    config.save_to_env()
    
    # Load from file
    loaded_config = FormattingConfig.load_from_env()
    
    # Assert equivalence
    assert loaded_config.enabled == config.enabled
    assert loaded_config.provider == config.provider
    assert loaded_config.model == config.model
    assert loaded_config.applications == config.applications
```

### Unit Test Coverage

**UI Tests**:
- Test that FormattingSettingsWidget creates all required controls
- Test that settings load correctly into UI
- Test that UI saves settings correctly
- Test provider dropdown contains correct options

**Format Matching Tests**:
- Test Notion application detection
- Test Obsidian application detection
- Test .md file extension detection
- Test Word application detection
- Test no-match scenario

**Prompt Generation Tests**:
- Test Notion prompt contains Notion-specific instructions
- Test Obsidian prompt contains wiki-link instructions
- Test Markdown prompt contains standard markdown syntax
- Test Word prompt avoids markdown syntax

**Integration Tests**:
- Test formatting-only pipeline
- Test combined formatting + post-processing pipeline
- Test post-processing-only pipeline (no format match)
- Test disabled state (no processing)

### Test Data Generators

```python
from hypothesis import strategies as st

# Strategy for generating valid configurations
config_strategy = st.builds(
    FormattingConfig,
    enabled=st.booleans(),
    provider=st.sampled_from(["groq", "openai", "glm", "custom"]),
    model=st.text(min_size=1, max_size=50),
    applications=st.lists(st.text(min_size=1), min_size=1, max_size=10)
)

# Strategy for generating application names
app_name_strategy = st.sampled_from([
    "notion", "obsidian", "word", "vscode", "sublime",
    "notepad++", "chrome", "firefox", "terminal"
])

# Strategy for generating file extensions
file_ext_strategy = st.sampled_from([
    ".md", ".txt", ".docx", ".doc", ".pdf", ".html", ""
])

# Strategy for generating transcription text
text_strategy = st.text(min_size=10, max_size=1000)
```

### Testing Matrix

| Formatting | Post-Processing | Format Match | Expected Behavior | Test Type |
|------------|----------------|--------------|-------------------|-----------|
| Enabled    | Disabled       | Yes          | Format with formatting AI | Property |
| Enabled    | Disabled       | No           | Return original | Property |
| Enabled    | Enabled        | Yes          | Combined with post AI | Property |
| Enabled    | Enabled        | No           | Post-process only | Property |
| Disabled   | Enabled        | Yes          | Post-process only | Property |
| Disabled   | Enabled        | No           | Post-process only | Property |
| Disabled   | Disabled       | Yes          | Return original | Property |
| Disabled   | Disabled       | No           | Return original | Property |

Each row in this matrix should be covered by property-based tests that generate random configurations and verify the correct behavior.

## Implementation Notes

### Integration Points

1. **Existing Window Monitor**: The feature reuses `window_monitor.py` which already tracks active windows for the info panel. No modifications needed to window detection logic.

2. **Existing AI Client**: The feature uses `transcription_client.py` infrastructure. Create separate client instances for formatting to avoid configuration conflicts.

3. **Existing Config Manager**: Extend with new formatting configuration fields. Add validation for formatting-specific settings.

4. **Existing Processing Pipeline**: Modify to check formatting settings and route through appropriate processing path.

### Performance Considerations

1. **Single API Call Optimization**: When both formatting and post-processing are enabled, combining prompts reduces API calls by 50% and latency significantly.

2. **Window Detection Caching**: Window detection happens once per transcription, not per word. Minimal performance impact.

3. **Configuration Loading**: Load formatting configuration once at startup, cache in memory. No repeated file I/O.

4. **Prompt Generation**: Pre-generate format prompts at initialization, store in dictionary. No runtime string building.

### Localization

The UI should support both English and Russian labels:
- "Formatting" / "Форматирование"
- "Enable formatting" / "Включить форматирование"
- "AI Provider" / "AI провайдер"
- "Model" / "Модель"
- "Applications" / "Приложения"
- Info text should explain the feature in both languages

### Future Enhancements

1. **Custom Format Definitions**: Allow users to define custom format prompts for applications not in the default list

2. **Format Preview**: Show a preview of how text will be formatted before applying

3. **Format History**: Track which formats were applied to which transcriptions

4. **Smart Format Detection**: Use ML to detect document structure and apply appropriate formatting automatically

5. **Format Templates**: Pre-defined templates for common use cases (meeting notes, code documentation, etc.)
