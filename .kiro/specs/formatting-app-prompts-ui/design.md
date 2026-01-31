# Design Document: Formatting Settings UI Improvements

## Overview

This design document describes the improvements to the RapidWhisper formatting settings UI. The current implementation uses a simple text field for comma-separated application names and a single system prompt field. The improved UI will provide a visual, card-based interface for managing applications with per-application customizable prompts, similar to the existing language selection page.

The design focuses on:
- Visual consistency with existing UI patterns (language selection page)
- Per-application prompt customization
- Intuitive add/edit/delete workflows
- Backward compatibility with existing configurations
- Localization support (Russian/English)

## Architecture

### Component Overview

The implementation consists of three main components:

1. **UI Components** (ui/settings_window.py)
   - Application list widget with visual cards
   - Context menu for edit/delete operations
   - Modal dialog for prompt editing
   - Add application button and workflow

2. **Data Model** (services/formatting_config.py)
   - Extended FormattingConfig to support per-application prompts
   - JSON serialization/deserialization
   - Migration from old comma-separated format

3. **Formatting Module** (services/formatting_module.py)
   - Updated to use per-application prompts
   - Fallback to universal default prompt

### Data Flow

```
User Interaction (UI)
    ↓
Settings Window
    ↓
FormattingConfig (Data Model)
    ↓
.env File (JSON Storage)
    ↓
Formatting Module (Runtime)
    ↓
AI Client (Formatting)
```

## Components and Interfaces

### 1. Application List Widget

**Purpose**: Display configured applications as visual cards similar to language selection

**Implementation**:
- Use QGridLayout with 4 columns (matching language selection)
- Each application displayed as a QPushButton with:
  - Application name (centered, bold)
  - Visual indicator for custom vs default prompt
  - Hover and selection states
- Styling matches language selection buttons:
  - Background: #2d2d2d (default), #3d3d3d (hover), #0078d4 (selected)
  - Border: 2px solid #3d3d3d (default), #0078d4 (hover/selected)
  - Border radius: 8px
  - Minimum height: 80px, minimum width: 120px

**Interface**:
```python
class ApplicationListWidget(QWidget):
    """Widget for displaying and managing application list."""
    
    application_selected = pyqtSignal(str)  # Emits application name
    application_edited = pyqtSignal(str)    # Emits application name
    application_deleted = pyqtSignal(str)   # Emits application name
    
    def __init__(self, parent=None):
        """Initialize the application list widget."""
        pass
    
    def set_applications(self, apps: Dict[str, Dict[str, Any]]) -> None:
        """
        Set the list of applications to display.
        
        Args:
            apps: Dictionary mapping app names to config dicts
                  Format: {"app_name": {"enabled": bool, "prompt": str}}
        """
        pass
    
    def get_selected_application(self) -> Optional[str]:
        """Get the currently selected application name."""
        pass
    
    def refresh(self) -> None:
        """Refresh the display of all application cards."""
        pass
```

### 2. Context Menu

**Purpose**: Provide right-click actions for application cards

**Implementation**:
- QMenu with two actions: "Edit" (Редактировать) and "Delete" (Удалить)
- Localized text based on current language setting
- Delete action disabled when only one application remains
- Triggered on right-click of application card

**Interface**:
```python
def _show_application_context_menu(self, app_name: str, position: QPoint) -> None:
    """
    Show context menu for an application card.
    
    Args:
        app_name: Name of the application
        position: Position to show the menu
    """
    menu = QMenu(self)
    
    edit_action = menu.addAction(t("settings.formatting.edit_application"))
    delete_action = menu.addAction(t("settings.formatting.delete_application"))
    
    # Disable delete if only one application
    if len(self.applications) <= 1:
        delete_action.setEnabled(False)
    
    action = menu.exec(position)
    
    if action == edit_action:
        self._edit_application_prompt(app_name)
    elif action == delete_action:
        self._delete_application(app_name)
```

### 3. Modal Dialog for Prompt Editing

**Purpose**: Allow users to edit per-application system prompts

**Implementation**:
- QDialog with modal behavior
- Components:
  - Title label showing application name (read-only)
  - QTextEdit for prompt (200px height, matching existing prompt editor)
  - Save button (Сохранить/Save)
  - Cancel button (Отменить/Cancel)
- Styling consistent with existing dialogs
- Pre-populated with current prompt or universal default

**Interface**:
```python
class PromptEditDialog(QDialog):
    """Dialog for editing application-specific prompts."""
    
    def __init__(self, app_name: str, current_prompt: str, parent=None):
        """
        Initialize the prompt edit dialog.
        
        Args:
            app_name: Name of the application
            current_prompt: Current prompt text (or default)
            parent: Parent widget
        """
        pass
    
    def get_prompt(self) -> str:
        """Get the edited prompt text."""
        pass
    
    @staticmethod
    def edit_prompt(app_name: str, current_prompt: str, parent=None) -> Optional[str]:
        """
        Show dialog and return edited prompt, or None if cancelled.
        
        Args:
            app_name: Name of the application
            current_prompt: Current prompt text
            parent: Parent widget
            
        Returns:
            Edited prompt text, or None if cancelled
        """
        pass
```

### 4. Add Application Dialog

**Purpose**: Allow users to add new applications with custom prompts

**Implementation**:
- QDialog with modal behavior
- Components:
  - QLineEdit for application name
  - QTextEdit for prompt (pre-filled with universal default)
  - Add button (Добавить/Add)
  - Cancel button (Отменить/Cancel)
- Validation:
  - Application name not empty
  - Application name not already in list
- Error messages displayed via QMessageBox

**Interface**:
```python
class AddApplicationDialog(QDialog):
    """Dialog for adding a new application."""
    
    def __init__(self, existing_apps: List[str], default_prompt: str, parent=None):
        """
        Initialize the add application dialog.
        
        Args:
            existing_apps: List of existing application names
            default_prompt: Universal default prompt
            parent: Parent widget
        """
        pass
    
    def get_application_data(self) -> Tuple[str, str]:
        """Get the application name and prompt."""
        pass
    
    @staticmethod
    def add_application(existing_apps: List[str], default_prompt: str, parent=None) -> Optional[Tuple[str, str]]:
        """
        Show dialog and return (app_name, prompt), or None if cancelled.
        
        Args:
            existing_apps: List of existing application names
            default_prompt: Universal default prompt
            parent: Parent widget
            
        Returns:
            Tuple of (app_name, prompt), or None if cancelled
        """
        pass
```

### 5. Extended FormattingConfig

**Purpose**: Support per-application prompt storage and management

**Implementation**:
- Add new field: `app_prompts: Dict[str, str]` mapping app names to prompts
- Maintain backward compatibility with `applications: List[str]`
- New environment variable: `FORMATTING_APP_PROMPTS` (JSON format)
- Migration logic from old format to new format

**Interface**:
```python
@dataclass
class FormattingConfig:
    """Extended formatting configuration with per-application prompts."""
    
    enabled: bool = False
    provider: str = "groq"
    model: str = ""
    applications: List[str] = field(default_factory=list)  # Kept for compatibility
    temperature: float = 0.3
    system_prompt: str = ""  # Deprecated, kept for migration
    app_prompts: Dict[str, str] = field(default_factory=dict)  # New field
    
    def get_prompt_for_app(self, app_name: str) -> str:
        """
        Get the prompt for a specific application.
        
        Args:
            app_name: Application name
            
        Returns:
            Application-specific prompt, or universal default if not set
        """
        pass
    
    def set_prompt_for_app(self, app_name: str, prompt: str) -> None:
        """
        Set the prompt for a specific application.
        
        Args:
            app_name: Application name
            prompt: Prompt text (empty string for default)
        """
        pass
    
    @classmethod
    def from_env(cls, env_path: Optional[str] = None) -> 'FormattingConfig':
        """
        Load configuration from .env with migration support.
        
        Checks for FORMATTING_APP_PROMPTS (new format).
        If not found, migrates from FORMATTING_APPLICATIONS (old format).
        """
        pass
    
    def to_env(self) -> dict:
        """
        Convert to environment variables.
        
        Returns dict with FORMATTING_APP_PROMPTS as JSON string.
        """
        pass
```

## Data Models

### Application Configuration Format

**New JSON Format** (stored in FORMATTING_APP_PROMPTS):
```json
{
  "notion": {
    "enabled": true,
    "prompt": ""
  },
  "obsidian": {
    "enabled": true,
    "prompt": "Custom prompt for Obsidian..."
  },
  "markdown": {
    "enabled": true,
    "prompt": ""
  }
}
```

**Field Descriptions**:
- `enabled`: Boolean indicating if application is active (always true in current design)
- `prompt`: Custom prompt string, or empty string to use universal default

**Universal Default Prompt**:
```python
UNIVERSAL_DEFAULT_PROMPT = """CRITICAL INSTRUCTIONS:
1. PRESERVE ALL CONTENT: Keep every word from the original text
2. ADD STRUCTURE: Actively identify and create proper formatting
3. NO NEW CONTENT: Do not add examples, explanations, or text that wasn't spoken

Task: Transform the transcribed speech into well-structured text.

Your job:
- ANALYZE the content and identify natural sections
- CREATE headings where appropriate for main topics and subtopics
- CONVERT lists when the speaker mentions multiple items
- ADD emphasis for important points
- INSERT line breaks between logical sections
- STRUCTURE the content for maximum readability

Remember: Use ALL the original words, just organize them better.

Output ONLY the reformatted text."""
```

### Migration Strategy

**Old Format** (FORMATTING_APPLICATIONS):
```
FORMATTING_APPLICATIONS=notion,obsidian,markdown,word
```

**Migration Process**:
1. Check if FORMATTING_APP_PROMPTS exists
2. If not, check for FORMATTING_APPLICATIONS
3. If old format found:
   - Parse comma-separated list
   - Create new JSON structure with empty prompts
   - Write to FORMATTING_APP_PROMPTS
   - Keep FORMATTING_APPLICATIONS for backward compatibility
4. If neither exists, use default applications

**Migration Code**:
```python
def migrate_from_old_format(applications_str: str) -> Dict[str, Dict[str, Any]]:
    """
    Migrate from old comma-separated format to new JSON format.
    
    Args:
        applications_str: Comma-separated application names
        
    Returns:
        Dictionary in new format with empty prompts
    """
    apps = [app.strip() for app in applications_str.split(",") if app.strip()]
    return {
        app: {"enabled": True, "prompt": ""}
        for app in apps
    }
```

## Error Handling

### Validation Errors

1. **Empty Application Name**
   - When: User tries to add application with empty name
   - Action: Show error message "Application name cannot be empty"
   - UI: QMessageBox with warning icon

2. **Duplicate Application Name**
   - When: User tries to add application that already exists
   - Action: Show error message "Application '{name}' already exists"
   - UI: QMessageBox with warning icon

3. **Delete Last Application**
   - When: User tries to delete the only remaining application
   - Action: Disable delete option in context menu
   - UI: Grayed out "Delete" menu item

### Data Loading Errors

1. **Invalid JSON in FORMATTING_APP_PROMPTS**
   - When: JSON parsing fails
   - Action: Log error, fall back to default applications
   - Recovery: Use default application list with empty prompts

2. **Missing .env File**
   - When: .env file doesn't exist
   - Action: Create with default configuration
   - Recovery: Use default applications and prompts

3. **Corrupted Configuration**
   - When: Configuration data is malformed
   - Action: Log error, reset to defaults
   - Recovery: Backup old config, create new default config

### Runtime Errors

1. **Prompt Too Long**
   - When: User enters extremely long prompt (>10000 chars)
   - Action: Show warning, allow but recommend shorter
   - UI: Warning message in dialog

2. **Special Characters in Application Name**
   - When: User enters name with special chars
   - Action: Allow but sanitize for file system safety
   - Sanitization: Replace invalid chars with underscores

## Testing Strategy

### Unit Tests

Unit tests will verify specific functionality and edge cases:

1. **Configuration Migration**
   - Test migration from old comma-separated format
   - Test handling of missing configuration
   - Test JSON parsing and serialization

2. **Validation Logic**
   - Test empty application name rejection
   - Test duplicate application name rejection
   - Test last application delete prevention

3. **Prompt Management**
   - Test getting prompt for application (custom vs default)
   - Test setting custom prompt
   - Test clearing custom prompt (revert to default)

4. **UI Component Behavior**
   - Test application card creation and display
   - Test context menu enable/disable logic
   - Test dialog accept/reject behavior

### Property-Based Tests

Property-based tests will verify universal correctness properties across all inputs. Each test will run a minimum of 100 iterations with randomized inputs.


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified the following redundancies:
- Properties 2.2 and 2.3 can be combined into one property about visual differentiation between custom and default prompts
- Property 3.4 is redundant with 4.1 (both test opening edit dialog)
- Property 5.5 is covered by other UI interaction properties
- Property 6.2 is redundant with 5.2 (both test default prompt assignment)
- Property 6.4 is covered by edit workflow properties
- Property 7.3 can be combined with 7.1 as a round-trip property
- Property 7.4 is redundant with 1.2 and 7.3
- Property 8.8 is redundant with 8.7
- Property 9.2 is redundant with 9.1 (if delete is disabled, error shouldn't be reachable)
- Property 10.4 is covered by 10.1

The following properties provide unique validation value:

### Property 1: Application Display Completeness
*For any* set of configured applications, when the formatting settings page is opened, all applications should appear as individual items in the list.

**Validates: Requirements 1.2**

### Property 2: Application Name Visibility
*For any* application in the list, the application's name should be visible in its rendered card or list item.

**Validates: Requirements 2.1**

### Property 3: Visual Prompt Differentiation
*For any* two applications where one has a custom prompt and one uses the default prompt, their visual representations should differ in a detectable way (e.g., icon, color, badge).

**Validates: Requirements 2.2, 2.3**

### Property 4: Context Menu Availability
*For any* application item, right-clicking on it should display a context menu with "Edit" and "Delete" options.

**Validates: Requirements 3.1, 3.2, 3.3**

### Property 5: Edit Dialog Opens
*For any* application, selecting "Edit" from its context menu should open a modal dialog containing the application's name and current prompt.

**Validates: Requirements 3.4, 4.1, 4.2**

### Property 6: Delete Removes Application
*For any* application in a list with multiple applications, selecting "Delete" from its context menu should remove that application from the list.

**Validates: Requirements 3.5**

### Property 7: Save Persists Prompt Changes
*For any* application and any prompt text, editing the prompt in the dialog and clicking "Save" should persist the new prompt to that application's configuration.

**Validates: Requirements 4.5**

### Property 8: Cancel Discards Changes
*For any* application and any prompt changes made in the edit dialog, clicking "Cancel" should leave the application's prompt unchanged.

**Validates: Requirements 4.6**

### Property 9: Unique Prompt Storage
*For any* set of applications with different prompts, each application should store and retrieve its own unique prompt without affecting other applications.

**Validates: Requirements 5.1, 5.3**

### Property 10: Default Prompt Assignment
*For any* newly added application without a specified custom prompt, the application should be assigned the universal default prompt.

**Validates: Requirements 5.2, 6.2**

### Property 11: Correct Prompt Retrieval
*For any* application with a custom prompt, when formatting text for that application, the system should use that application's specific prompt, not the default or another application's prompt.

**Validates: Requirements 5.4**

### Property 12: Configuration Round-Trip
*For any* valid application configuration (set of applications with prompts), serializing to JSON then deserializing should produce an equivalent configuration.

**Validates: Requirements 7.1, 7.3**

### Property 13: Persistent Storage Location
*For any* application configuration, after saving, the JSON data should be stored in the .env file under the key FORMATTING_APP_PROMPTS.

**Validates: Requirements 7.2**

### Property 14: Migration Preserves Applications
*For any* old format comma-separated application list, migrating to the new format should preserve all application names with empty prompts (indicating default).

**Validates: Requirements 7.5, 10.1, 10.2, 10.3**

### Property 15: Migration Cleanup
*For any* old format configuration, after successful migration to the new format, the old FORMATTING_APPLICATIONS key should be removed from the .env file.

**Validates: Requirements 10.5**

### Property 16: Empty Name Rejection
*For any* attempt to add an application with an empty or whitespace-only name, the system should reject the addition and display an error message.

**Validates: Requirements 8.5**

### Property 17: Duplicate Name Rejection
*For any* existing application name, attempting to add another application with the same name should be rejected with an error message.

**Validates: Requirements 8.6**

### Property 18: Valid Application Addition
*For any* valid application name (non-empty, non-duplicate) and prompt text, adding the application should result in it appearing in the list with the specified prompt.

**Validates: Requirements 8.7**

### Property 19: Delete Enabled for Multiple Applications
*For any* application list with two or more applications, the "Delete" option should be enabled in the context menu for all applications.

**Validates: Requirements 9.3**

### Property 20: Minimum One Application Invariant
*For any* sequence of add and delete operations, the application list should always contain at least one application.

**Validates: Requirements 9.4**

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests for comprehensive coverage:

**Unit Tests** will verify:
- Specific UI component creation and layout
- Edge cases (empty list, single application, last application delete attempt)
- Error message display and formatting
- Dialog accept/reject behavior
- Migration from specific old format examples
- Localization key usage

**Property-Based Tests** will verify:
- Universal properties across all possible configurations
- Round-trip serialization/deserialization
- Prompt isolation between applications
- Configuration persistence
- Migration correctness for any old format
- Input validation for any invalid inputs

### Property-Based Testing Configuration

**Library**: Use `hypothesis` for Python (PyQt6 UI testing)

**Configuration**:
- Minimum 100 iterations per property test
- Each test tagged with: `Feature: formatting-app-prompts-ui, Property {number}: {property_text}`
- Use custom strategies for generating:
  - Valid application names (alphanumeric, 1-50 chars)
  - Invalid application names (empty, whitespace, duplicates)
  - Prompt texts (0-10000 chars)
  - Application configurations (1-20 applications)
  - Old format strings (comma-separated lists)

**Example Test Structure**:
```python
from hypothesis import given, strategies as st
import pytest

@given(
    apps=st.lists(
        st.tuples(
            st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=1, max_size=50),
            st.text(max_size=10000)
        ),
        min_size=1,
        max_size=20,
        unique_by=lambda x: x[0]
    )
)
def test_property_12_configuration_round_trip(apps):
    """
    Feature: formatting-app-prompts-ui, Property 12: Configuration Round-Trip
    
    For any valid application configuration, serializing to JSON then 
    deserializing should produce an equivalent configuration.
    """
    # Create configuration
    config = FormattingConfig()
    for app_name, prompt in apps:
        config.set_prompt_for_app(app_name, prompt)
    
    # Serialize to JSON
    json_str = config.to_json()
    
    # Deserialize
    restored_config = FormattingConfig.from_json(json_str)
    
    # Verify equivalence
    assert config.app_prompts == restored_config.app_prompts
    assert config.applications == restored_config.applications
```

### Integration Testing

Integration tests will verify:
1. Complete add → edit → delete workflow
2. Configuration save → restart → load workflow
3. Migration → save → load workflow
4. UI interaction → data persistence → formatting module usage

### Manual Testing Checklist

Due to the visual nature of this feature, manual testing is required for:
- [ ] Visual consistency with language selection page
- [ ] Hover and selection state animations
- [ ] Context menu positioning and appearance
- [ ] Dialog modal behavior and focus management
- [ ] Localization display in Russian and English
- [ ] Responsive layout with different numbers of applications
- [ ] Accessibility (keyboard navigation, screen reader support)
