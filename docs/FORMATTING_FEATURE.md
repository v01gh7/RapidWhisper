# Transcription Formatting Feature

## Overview

The Transcription Formatting feature automatically formats transcribed text based on the active application window. When enabled, the system detects which application you're working in (e.g., Notion, Obsidian, Word, Markdown files) and applies appropriate formatting rules using AI-powered text transformation.

## Features

- **Automatic Application Detection**: Detects the currently active application window
- **Application-Specific Formatting**: Applies formatting rules tailored to each application
- **Combined Operations**: Intelligently combines formatting with post-processing in a single API call to minimize latency
- **Independent Configuration**: Separate AI provider and model settings for formatting
- **Graceful Fallback**: Returns original text if formatting fails

## Supported Applications

### Desktop Applications

- **Notion**: Notion-style markdown with appropriate headings and bullet points
- **Obsidian**: Standard markdown with wiki-links and tags
- **Markdown Files** (.md, .markdown): Clean standard markdown formatting
- **Microsoft Word**: Simple formatting suitable for Word documents
- **LibreOffice Writer**: Simple formatting suitable for Writer documents (.odt files)
- **VS Code**: Markdown formatting for .md files
- **Sublime Text**: Standard text formatting
- **Notepad++**: Standard text formatting

### Web Applications (Browser Detection)

The system automatically detects web applications running in browsers by analyzing the browser tab title. Supported browsers include Chrome, Firefox, Edge, Opera, Brave, Vivaldi, and Safari.

#### Google Services (word format)
- **Google Docs** / **Google Документы** - Document editing
- **Google Sheets** / **Google Таблицы** - Spreadsheet editing
- **Google Slides** / **Google Презентации** - Presentation editing
- **Google Forms** / **Google Формы** - Form creation
- **Google Keep** - Note-taking

#### Microsoft Office Online (word format)
- **Microsoft Word Online** - Online document editing
- **Microsoft Excel Online** - Online spreadsheet editing
- **Microsoft PowerPoint Online** - Online presentation editing
- **Office 365** - Microsoft 365 web apps
- **Office Online** - Legacy Office web apps

#### Collaboration Tools (word format)
- **Dropbox Paper** - Collaborative document editing
- **Quip** - Team collaboration documents
- **Coda.io** - All-in-one doc platform
- **Airtable** - Spreadsheet-database hybrid

#### Zoho Office Suite (word format)
- **Zoho Writer** - Document editing
- **Zoho Sheet** - Spreadsheet editing
- **Zoho Show** - Presentation editing

#### Note-Taking & Knowledge Management
- **Notion** / **Notion.so** (notion format) - All-in-one workspace
- **Obsidian Publish** (obsidian format) - Published Obsidian notes

#### Markdown Editors (markdown format)
- **HackMD** - Collaborative markdown editor
- **StackEdit** - In-browser markdown editor
- **Dillinger** - Online markdown editor
- **Typora Online** - Minimalist markdown editor
- **GitHub.dev** - GitHub web-based editor
- **GitLab** - GitLab web IDE
- **Gitpod** - Cloud development environment

**Note:** Web application detection works by matching keywords in the browser tab title. The system checks the title in both English and Russian (where applicable) to ensure broad language support.

## Configuration

### Environment Variables

Add the following variables to your `.env` file:

```env
# Enable/disable formatting
FORMATTING_ENABLED=true

# AI provider for formatting (groq, openai, glm, custom)
FORMATTING_PROVIDER=groq

# Model to use for formatting
FORMATTING_MODEL=llama-3.3-70b-versatile

# Comma-separated list of applications to format for
FORMATTING_APPLICATIONS=notion,obsidian,markdown,word,libreoffice,vscode
```

### UI Configuration

1. Open Settings window
2. Navigate to "Processing" page
3. Scroll to "Formatting (Форматирование)" section
4. Enable formatting with the checkbox
5. Select your preferred AI provider
6. Enter the model name
7. Specify applications (comma-separated)
8. Click "Save Settings"

## How It Works

### Processing Decision Logic

The system makes intelligent decisions based on your configuration:

1. **Both Formatting and Post-Processing Enabled + Format Match**
   - Combines both operations in a single AI call
   - Uses post-processing AI provider
   - Extends post-processing prompt with formatting instructions
   - Result: Formatted and post-processed text

2. **Only Formatting Enabled + Format Match**
   - Applies formatting using formatting AI provider
   - Result: Formatted text

3. **Only Post-Processing Enabled OR No Format Match**
   - Applies only post-processing
   - Result: Post-processed text

4. **Both Disabled OR No Format Match**
   - Returns original transcribed text
   - Result: Original text

### Format Matching

The system matches applications using:
- **Application Name**: Matches process name (e.g., "notion", "obsidian", "word")
- **File Extension**: Matches file extension (e.g., ".md", ".docx")
- **Browser Tab Title**: Detects web applications by analyzing browser window titles

#### Browser Detection

When a browser is detected (Chrome, Firefox, Edge, Opera, Brave, Vivaldi, Safari), the system analyzes the tab title to identify web applications:

1. **Title Pattern Matching**: Checks if the tab title contains specific keywords
   - Example: "My Document - Google Docs" → detected as `word` format
   - Example: "Workspace - Notion" → detected as `notion` format

2. **Multi-Language Support**: Supports both English and Russian titles
   - "Google Docs" and "Google Документы" both work
   - "Google Sheets" and "Google Таблицы" both work

3. **Format Assignment**: Maps web apps to appropriate format types
   - Google Docs/Sheets/Slides → `word` format
   - Notion web → `notion` format
   - HackMD/StackEdit → `markdown` format

Matching is case-insensitive and supports partial matches.

## Architecture

### Components

1. **FormattingModule** (`services/formatting_module.py`)
   - Core formatting logic
   - Application detection and matching
   - Format-specific prompt generation
   - AI client integration

2. **ProcessingCoordinator** (`services/processing_coordinator.py`)
   - Orchestrates formatting and post-processing
   - Decides between formatting-only, combined, or post-processing-only modes
   - Combines prompts when both operations are enabled

3. **FormattingConfig** (`services/formatting_config.py`)
   - Configuration data model
   - Environment variable loading/saving
   - Configuration validation

4. **Settings UI** (`ui/settings_window.py`)
   - User interface for configuration
   - Settings persistence
   - Localization support

### Data Flow

```
Transcription
    ↓
Processing Coordinator
    ↓
Decision Logic
    ├─→ Formatting Only (if post-processing disabled)
    ├─→ Combined (if both enabled + format match)
    ├─→ Post-Processing Only (if formatting disabled or no match)
    └─→ Original Text (if both disabled)
    ↓
Formatted Output
```

## API Usage

### Programmatic Configuration

```python
from services.formatting_config import FormattingConfig

# Load configuration
config = FormattingConfig.from_env()

# Create new configuration
config = FormattingConfig(
    enabled=True,
    provider="groq",
    model="llama-3.3-70b-versatile",
    applications=["notion", "obsidian", "markdown"]
)

# Save configuration
env_dict = config.to_env()
# Write env_dict to .env file
```

### Using the Formatting Module

```python
from services.formatting_module import FormattingModule
from services.window_monitor import WindowMonitor

# Create window monitor
window_monitor = WindowMonitor()

# Create formatting module
formatting_module = FormattingModule(
    config_manager=None,
    ai_client_factory=None,
    window_monitor=window_monitor
)

# Process text
formatted_text = formatting_module.process("Original transcribed text")
```

### Using the Processing Coordinator

```python
from services.processing_coordinator import ProcessingCoordinator
from services.formatting_module import FormattingModule
from core.config import Config

# Create components
formatting_module = FormattingModule(...)
config = Config.load_from_env()

# Create coordinator
coordinator = ProcessingCoordinator(
    formatting_module=formatting_module,
    config_manager=config
)

# Process transcription
result = coordinator.process_transcription(
    text="Original text",
    transcription_client=transcription_client,
    config=config
)
```

## Testing

### Running Tests

```bash
# Run all formatting tests
pytest tests/test_formatting*.py -v

# Run property-based tests
pytest tests/test_formatting_config_properties.py -v
pytest tests/test_formatting_decision_properties.py -v

# Run integration tests
pytest tests/test_processing_coordinator_integration.py -v
pytest tests/test_integrated_pipeline.py -v
```

### Test Coverage

- **Property-Based Tests**: Verify universal correctness properties
- **Unit Tests**: Test specific functionality and edge cases
- **Integration Tests**: Test complete processing pipelines
- **End-to-End Tests**: Verify full transcription flow

## Troubleshooting

### Formatting Not Applied

1. **Check if formatting is enabled**
   - Open Settings → Processing → Formatting
   - Ensure "Enable formatting" is checked

2. **Verify application is in the list**
   - Check FORMATTING_APPLICATIONS in .env
   - Ensure your application name is included

3. **Check API key**
   - Verify the API key for your selected provider is set
   - Check GROQ_API_KEY, OPENAI_API_KEY, or GLM_API_KEY

4. **Review logs**
   - Check application logs for formatting errors
   - Look for "FORMATTING" or "PROCESSING COORDINATOR" messages

### Original Text Returned

This is expected behavior when:
- Formatting is disabled
- Active application doesn't match configured applications
- API request fails (graceful fallback)
- Configuration is invalid

### Combined Mode Not Working

Ensure both conditions are met:
1. Formatting is enabled AND post-processing is enabled
2. Active application matches a configured format

Check logs for "COMBINED MODE" message to verify.

## Performance Considerations

### API Call Optimization

When both formatting and post-processing are enabled:
- **Without optimization**: 2 API calls (formatting + post-processing)
- **With optimization**: 1 API call (combined operation)
- **Latency reduction**: ~50% faster processing

### Window Detection

- Window detection happens once per transcription
- Minimal performance impact (<10ms)
- Cached during processing

## Future Enhancements

1. **Custom Format Definitions**: Allow users to define custom format prompts
2. **Format Preview**: Show preview before applying formatting
3. **Format History**: Track which formats were applied
4. **Smart Format Detection**: Use ML to detect document structure
5. **Format Templates**: Pre-defined templates for common use cases

## Contributing

When contributing to the formatting feature:

1. **Follow the architecture**: Use existing components and patterns
2. **Write tests**: Add property-based and unit tests for new functionality
3. **Update documentation**: Keep this document up-to-date
4. **Test edge cases**: Verify graceful failure handling
5. **Check performance**: Ensure changes don't impact transcription speed

## License

This feature is part of RapidWhisper and follows the same license.
