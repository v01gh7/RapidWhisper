# Design Document: UI Customization

## Overview

The UI Customization feature adds a new settings tab to the RapidWhisper application, enabling users to personalize the visual appearance of both the floating recording window and settings window. The design focuses on immediate visual feedback for transparency changes and persistent storage of all customization preferences.

The implementation extends the existing settings infrastructure by adding a new page to the tabbed settings dialog, integrating with the existing Config system for persistence, and applying changes dynamically to UI components.

## Architecture

### Component Structure

```
SettingsWindow
├── _create_ui_customization_page()  [NEW]
│   ├── Opacity Controls
│   │   └── QSlider + QLabel (live preview)
│   └── Font Size Controls
│       ├── Floating Window Group
│       │   ├── Main Text Slider
│       │   └── Info Panel Slider
│       └── Settings Window Group
│           ├── Labels Slider
│           └── Titles Slider
│
FloatingWindow
├── __init__() - reads Config.window_opacity
├── setStyleSheet() - applies opacity to background
└── paintEvent() - applies opacity to custom painting
│
InfoPanelWidget
├── __init__() - reads Config.font_size_floating_info
└── _setup_ui() - applies font sizes to labels
│
Config
├── window_opacity property [NEW]
├── font_size_floating_main property [NEW]
├── font_size_floating_info property [NEW]
├── font_size_settings_labels property [NEW]
└── font_size_settings_titles property [NEW]
```

### Data Flow

1. **Initialization Flow:**
   - Application starts → Config reads .env file → Default values used if keys missing
   - FloatingWindow created → Reads opacity from Config → Applies to stylesheet and paint
   - SettingsWindow opened → Reads all font sizes from Config → Populates UI controls

2. **User Interaction Flow:**
   - User adjusts opacity slider → Signal emitted → FloatingWindow.set_opacity() called → Visual update immediate
   - User adjusts font slider → Value stored in memory → On dialog close → Written to .env
   - User clicks "Reset to Defaults" → All controls reset → Values written to .env → FloatingWindow updated

3. **Persistence Flow:**
   - Settings changed → Config.set_env_value() called → .env file updated
   - Application restart → Config reads .env → Stored values applied

## Components and Interfaces

### 1. Config Class Extensions

**Location:** `core/config.py`

**New Properties:**

```python
@property
def window_opacity(self) -> int:
    """Get window opacity value (50-255). Default: 150"""
    value = int(os.getenv('WINDOW_OPACITY', '150'))
    return max(50, min(255, value))  # Constrain to valid range

@property
def font_size_floating_main(self) -> int:
    """Get floating window main text font size (10-24px). Default: 14"""
    value = int(os.getenv('FONT_SIZE_FLOATING_MAIN', '14'))
    return max(10, min(24, value))

@property
def font_size_floating_info(self) -> int:
    """Get floating window info panel font size (8-16px). Default: 11"""
    value = int(os.getenv('FONT_SIZE_FLOATING_INFO', '11'))
    return max(8, min(16, value))

@property
def font_size_settings_labels(self) -> int:
    """Get settings window labels font size (10-16px). Default: 12"""
    value = int(os.getenv('FONT_SIZE_SETTINGS_LABELS', '12'))
    return max(10, min(16, value))

@property
def font_size_settings_titles(self) -> int:
    """Get settings window titles font size (16-32px). Default: 24"""
    value = int(os.getenv('FONT_SIZE_SETTINGS_TITLES', '24'))
    return max(16, min(32, value))

def set_env_value(self, key: str, value: str) -> None:
    """Write a value to .env file"""
    # Implementation: Read .env, update key, write back
```

**Interface Contract:**
- All properties return constrained integer values within valid ranges
- Missing .env keys return documented default values
- Invalid values (non-numeric, out of range) are constrained to valid boundaries
- set_env_value() handles .env file I/O with proper error handling

### 2. SettingsWindow Extensions

**Location:** `ui/settings_window.py`

**New Method:**

```python
def _create_ui_customization_page(self) -> QWidget:
    """Create the UI Customization settings page"""
    page = QWidget()
    layout = QVBoxLayout(page)
    
    # Window Opacity Group
    opacity_group = QGroupBox(self.tr("ui_customization.window_opacity"))
    opacity_layout = QHBoxLayout()
    
    self.opacity_slider = QSlider(Qt.Horizontal)
    self.opacity_slider.setRange(50, 255)
    self.opacity_slider.setValue(self.config.window_opacity)
    self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
    
    self.opacity_label = QLabel(str(self.config.window_opacity))
    opacity_layout.addWidget(self.opacity_slider)
    opacity_layout.addWidget(self.opacity_label)
    opacity_group.setLayout(opacity_layout)
    
    # Font Sizes Group
    font_group = QGroupBox(self.tr("ui_customization.font_sizes"))
    font_layout = QFormLayout()
    
    # Create sliders for each font size setting
    self.font_floating_main_slider = self._create_font_slider(10, 24, 
        self.config.font_size_floating_main)
    self.font_floating_info_slider = self._create_font_slider(8, 16, 
        self.config.font_size_floating_info)
    self.font_settings_labels_slider = self._create_font_slider(10, 16, 
        self.config.font_size_settings_labels)
    self.font_settings_titles_slider = self._create_font_slider(16, 32, 
        self.config.font_size_settings_titles)
    
    font_layout.addRow(self.tr("ui_customization.font_floating_main"), 
        self.font_floating_main_slider)
    font_layout.addRow(self.tr("ui_customization.font_floating_info"), 
        self.font_floating_info_slider)
    font_layout.addRow(self.tr("ui_customization.font_settings_labels"), 
        self.font_settings_labels_slider)
    font_layout.addRow(self.tr("ui_customization.font_settings_titles"), 
        self.font_settings_titles_slider)
    
    font_group.setLayout(font_layout)
    
    # Reset Button
    reset_button = QPushButton(self.tr("ui_customization.reset_defaults"))
    reset_button.clicked.connect(self._reset_ui_defaults)
    
    layout.addWidget(opacity_group)
    layout.addWidget(font_group)
    layout.addWidget(reset_button)
    layout.addStretch()
    
    return page

def _on_opacity_changed(self, value: int) -> None:
    """Handle opacity slider changes with immediate preview"""
    self.opacity_label.setText(str(value))
    self.config.set_env_value('WINDOW_OPACITY', str(value))
    # Signal floating window to update
    if hasattr(self, 'floating_window_ref'):
        self.floating_window_ref.set_opacity(value)

def _reset_ui_defaults(self) -> None:
    """Reset all UI customization settings to defaults"""
    defaults = {
        'WINDOW_OPACITY': '150',
        'FONT_SIZE_FLOATING_MAIN': '14',
        'FONT_SIZE_FLOATING_INFO': '11',
        'FONT_SIZE_SETTINGS_LABELS': '12',
        'FONT_SIZE_SETTINGS_TITLES': '24'
    }
    for key, value in defaults.items():
        self.config.set_env_value(key, value)
    
    # Update UI controls
    self.opacity_slider.setValue(150)
    self.font_floating_main_slider.setValue(14)
    self.font_floating_info_slider.setValue(11)
    self.font_settings_labels_slider.setValue(12)
    self.font_settings_titles_slider.setValue(24)
```

**Integration Point:**
- Add tab in `__init__()`: `self.tabs.addTab(self._create_ui_customization_page(), self.tr("ui_customization.title"))`
- Store reference to FloatingWindow for live opacity updates

### 3. FloatingWindow Modifications

**Location:** `ui/floating_window.py`

**Changes:**

```python
def __init__(self, config: Config):
    super().__init__()
    self.config = config
    self._opacity = config.window_opacity
    # ... existing initialization ...
    self._apply_opacity()

def _apply_opacity(self) -> None:
    """Apply opacity to window background"""
    # Update stylesheet with current opacity
    self.setStyleSheet(f"""
        QWidget {{
            background-color: rgba(30, 30, 30, {self._opacity});
            color: white;
        }}
    """)
    self.update()  # Trigger repaint

def set_opacity(self, value: int) -> None:
    """Update window opacity (called from settings)"""
    self._opacity = max(50, min(255, value))
    self._apply_opacity()

def paintEvent(self, event):
    """Custom paint with opacity support"""
    painter = QPainter(self)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Apply opacity to background
    bg_color = QColor(30, 30, 30, self._opacity)
    painter.fillRect(self.rect(), bg_color)
    
    # ... existing paint code ...
```

**Font Size Application:**

```python
def _setup_status_label(self) -> None:
    """Setup status label with configured font size"""
    font_size = self.config.font_size_floating_main
    font = QFont()
    font.setPointSize(font_size)
    self.status_label.setFont(font)
```

### 4. InfoPanelWidget Modifications

**Location:** `ui/info_panel_widget.py`

**Changes:**

```python
def _setup_ui(self) -> None:
    """Setup UI with configured font sizes"""
    font_size = self.config.font_size_floating_info
    font = QFont()
    font.setPointSize(font_size)
    
    self.app_name_label.setFont(font)
    self.record_hotkey_label.setFont(font)
    self.cancel_hotkey_label.setFont(font)
```

### 5. Translation Files

**Location:** `utils/translations/en.json`

```json
{
  "settings": {
    "ui_customization": {
      "title": "UI Customization",
      "window_opacity": "Window Transparency:",
      "window_opacity_tooltip": "Adjust background transparency (50=very transparent, 255=opaque)",
      "font_sizes": "Font Sizes",
      "font_floating_main": "Floating Window - Main Text:",
      "font_floating_info": "Floating Window - Info Panel:",
      "font_settings_labels": "Settings Window - Labels:",
      "font_settings_titles": "Settings Window - Titles:",
      "preview": "Preview",
      "reset_defaults": "Reset to Defaults"
    }
  }
}
```

**Location:** `utils/translations/ru.json`

```json
{
  "settings": {
    "ui_customization": {
      "title": "Настройки интерфейса",
      "window_opacity": "Прозрачность окна:",
      "window_opacity_tooltip": "Настройка прозрачности фона (50=очень прозрачно, 255=непрозрачно)",
      "font_sizes": "Размеры шрифтов",
      "font_floating_main": "Плавающее окно - Основной текст:",
      "font_floating_info": "Плавающее окно - Инфопанель:",
      "font_settings_labels": "Окно настроек - Метки:",
      "font_settings_titles": "Окно настроек - Заголовки:",
      "preview": "Предпросмотр",
      "reset_defaults": "Сбросить по умолчанию"
    }
  }
}
```

## Data Models

### Configuration Schema

**.env File Format:**

```bash
# UI Customization Settings
WINDOW_OPACITY=150          # Range: 50-255, Default: 150
FONT_SIZE_FLOATING_MAIN=14  # Range: 10-24, Default: 14
FONT_SIZE_FLOATING_INFO=11  # Range: 8-16, Default: 11
FONT_SIZE_SETTINGS_LABELS=12 # Range: 10-16, Default: 12
FONT_SIZE_SETTINGS_TITLES=24 # Range: 16-32, Default: 24
```

### Value Constraints

| Setting | Type | Min | Max | Default | Unit |
|---------|------|-----|-----|---------|------|
| WINDOW_OPACITY | int | 50 | 255 | 150 | alpha |
| FONT_SIZE_FLOATING_MAIN | int | 10 | 24 | 14 | px |
| FONT_SIZE_FLOATING_INFO | int | 8 | 16 | 11 | px |
| FONT_SIZE_SETTINGS_LABELS | int | 10 | 16 | 12 | px |
| FONT_SIZE_SETTINGS_TITLES | int | 16 | 32 | 24 | px |

### State Management

**Runtime State:**
- Current opacity value stored in FloatingWindow._opacity
- Font sizes read from Config on widget initialization
- Settings dialog maintains slider values in memory until save

**Persistence:**
- All values written to .env file immediately (opacity) or on dialog close (fonts)
- Config class reads from .env on application startup
- Missing keys trigger default value usage with no error


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Value Range Constraints

*For any* UI customization setting and any input value, when the value is set through Config properties, the returned value should be constrained within the documented valid range for that setting.

**Validates: Requirements 1.1, 2.1, 2.2, 3.1, 3.2, 5.4, 8.2**

### Property 2: Settings Persistence Round-Trip

*For any* UI customization setting and any valid value within its range, writing the value to .env and then reading it back through Config should return an equivalent value.

**Validates: Requirements 2.4, 5.1, 5.2, 6.3**

### Property 3: Default Value Fallback

*For any* UI customization setting, when the corresponding .env key is missing or contains an invalid value, the Config property should return the documented default value.

**Validates: Requirements 5.3, 8.3**

### Property 4: UI Control Display Consistency

*For any* UI customization slider control, the displayed numeric label should always match the current slider value.

**Validates: Requirements 1.4, 2.5, 3.5**

### Property 5: Opacity Live Preview

*For any* opacity value in the valid range (50-255), when set_opacity() is called on FloatingWindow, the internal _opacity field should be updated to that value and a repaint should be triggered.

**Validates: Requirements 1.2**

### Property 6: Reset to Defaults Completeness

*For any* UI customization setting, after calling the reset to defaults function, the setting value should equal its documented default value in both the Config and the .env file.

**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

### Property 7: Boundary Value Clamping

*For any* value outside the valid range for a setting, when passed to a Config property, the returned value should be clamped to the nearest valid boundary (minimum or maximum).

**Validates: Requirements 1.5, 8.2**

### Property 8: Non-Numeric Input Rejection

*For any* non-numeric string value, when attempting to parse it as a configuration value, the Config should reject it and return the default value instead.

**Validates: Requirements 8.1**

### Property 9: Font Size Persistence Across Reopens

*For any* valid font size value, after setting it in the Settings_Window, closing the window, and reopening it, the displayed font size should match the previously set value.

**Validates: Requirements 3.3**

## Error Handling

### Input Validation Errors

**Invalid Opacity Values:**
- **Error:** User provides opacity < 50 or > 255
- **Handling:** Clamp to nearest boundary (50 or 255), no error message needed
- **Recovery:** System continues with clamped value

**Invalid Font Size Values:**
- **Error:** User provides font size outside valid range for that setting
- **Handling:** Clamp to nearest boundary, no error message needed
- **Recovery:** System continues with clamped value

**Non-Numeric Input:**
- **Error:** .env file contains non-numeric value for a setting
- **Handling:** Log warning, use default value
- **Recovery:** System continues with default, user can reconfigure

### File I/O Errors

**Missing .env File:**
- **Error:** .env file doesn't exist on startup
- **Handling:** Use all default values, no error message
- **Recovery:** System creates .env on first setting change

**Permission Denied Writing .env:**
- **Error:** Cannot write to .env file
- **Handling:** Log error, show user notification
- **Recovery:** Settings remain in memory for current session, user must fix permissions

**Corrupted .env File:**
- **Error:** .env file exists but is malformed
- **Handling:** Log warning, use defaults for unparseable values
- **Recovery:** System overwrites corrupted values on next save

### UI State Errors

**FloatingWindow Reference Lost:**
- **Error:** Settings window cannot update FloatingWindow opacity (reference is None)
- **Handling:** Update .env file only, skip live preview
- **Recovery:** Opacity applies on next FloatingWindow creation

**Translation Key Missing:**
- **Error:** Required translation key not found in language file
- **Handling:** Fall back to English key, log warning
- **Recovery:** Display English text, user can add translation

## Testing Strategy

### Dual Testing Approach

The UI Customization feature requires both unit tests and property-based tests for comprehensive coverage:

**Unit Tests** focus on:
- Specific examples of valid configurations (e.g., opacity=150, font_size=14)
- Edge cases (minimum and maximum values for each setting)
- Error conditions (missing .env, invalid values, permission errors)
- Integration between components (Settings → Config → FloatingWindow)
- Translation key presence in both language files
- UI element ordering and structure

**Property-Based Tests** focus on:
- Universal properties that hold for all valid inputs
- Range constraints across all possible values
- Round-trip persistence for any valid configuration
- Boundary clamping behavior for out-of-range values
- Default fallback for any missing or invalid configuration

Together, these approaches ensure both concrete correctness (unit tests) and general correctness across the input space (property tests).

### Property-Based Testing Configuration

**Framework:** pytest with Hypothesis library (Python)

**Configuration:**
- Minimum 100 iterations per property test
- Each test tagged with feature name and property number
- Tag format: `# Feature: ui-customization, Property N: [property text]`

**Example Test Structure:**

```python
from hypothesis import given, strategies as st
import pytest

@given(opacity=st.integers(min_value=50, max_value=255))
def test_opacity_range_constraint(opacity):
    """
    Feature: ui-customization, Property 1: Value Range Constraints
    Test that opacity values are always within valid range
    """
    config = Config()
    config.set_env_value('WINDOW_OPACITY', str(opacity))
    result = config.window_opacity
    assert 50 <= result <= 255

@given(opacity=st.integers())
def test_opacity_boundary_clamping(opacity):
    """
    Feature: ui-customization, Property 7: Boundary Value Clamping
    Test that out-of-range values are clamped to boundaries
    """
    config = Config()
    config.set_env_value('WINDOW_OPACITY', str(opacity))
    result = config.window_opacity
    
    if opacity < 50:
        assert result == 50
    elif opacity > 255:
        assert result == 255
    else:
        assert result == opacity
```

### Unit Test Coverage

**Config Class Tests:**
- Test each property with default value (no .env key)
- Test each property with valid value in .env
- Test each property with invalid value in .env
- Test set_env_value() creates/updates .env correctly
- Test boundary values (min, max) for each setting

**SettingsWindow Tests:**
- Test UI Customization tab is created and added
- Test all sliders have correct min/max ranges
- Test opacity slider triggers live preview
- Test reset button restores all defaults
- Test font size changes are saved on dialog close
- Test all translation keys are used correctly

**FloatingWindow Tests:**
- Test opacity is read from Config on initialization
- Test set_opacity() updates _opacity field
- Test set_opacity() triggers repaint
- Test opacity is applied in stylesheet and paintEvent

**InfoPanelWidget Tests:**
- Test font sizes are read from Config on initialization
- Test fonts are applied to all labels

**Translation Tests:**
- Test all required keys exist in en.json
- Test all required keys exist in ru.json
- Test English and Russian translations are non-empty

### Integration Tests

**End-to-End Opacity Change:**
1. Start application with default opacity
2. Open settings, change opacity slider
3. Verify FloatingWindow updates immediately
4. Close and restart application
5. Verify opacity persists

**End-to-End Font Size Change:**
1. Start application with default font sizes
2. Open settings, change font sizes
3. Close settings dialog
4. Reopen settings dialog
5. Verify font sizes persisted and are displayed correctly

**Reset to Defaults:**
1. Change all settings to non-default values
2. Click "Reset to Defaults"
3. Verify all UI controls show defaults
4. Verify .env file contains defaults
5. Verify FloatingWindow shows default opacity

### Test Data

**Valid Test Values:**
- Opacity: 50, 100, 150, 200, 255
- Font sizes: minimum, default, maximum for each setting

**Invalid Test Values:**
- Opacity: -10, 0, 49, 256, 300, 1000
- Font sizes: 0, 1, 100, 999
- Non-numeric: "abc", "", "12.5", "12px", null

**Edge Cases:**
- Empty .env file
- Missing specific keys in .env
- .env with only some keys present
- Simultaneous changes to multiple settings
- Rapid slider movements (stress test)
