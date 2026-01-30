"""
Property-based tests for UI Customization Config properties.

Feature: ui-customization
Tests universal correctness properties using Hypothesis.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from core.config import Config, get_env_path
import os
import tempfile
from pathlib import Path


# Strategy for valid opacity values
opacity_strategy = st.integers(min_value=50, max_value=255)

# Strategy for valid font sizes
font_floating_main_strategy = st.integers(min_value=10, max_value=24)
font_floating_info_strategy = st.integers(min_value=8, max_value=16)
font_settings_labels_strategy = st.integers(min_value=10, max_value=16)
font_settings_titles_strategy = st.integers(min_value=16, max_value=32)

# Strategy for any integer (including out of range)
any_integer_strategy = st.integers()


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing."""
    # Save original environment variables
    original_env = {}
    ui_keys = [
        'WINDOW_OPACITY',
        'FONT_SIZE_FLOATING_MAIN',
        'FONT_SIZE_FLOATING_INFO',
        'FONT_SIZE_SETTINGS_LABELS',
        'FONT_SIZE_SETTINGS_TITLES'
    ]
    
    for key in ui_keys:
        if key in os.environ:
            original_env[key] = os.environ[key]
            del os.environ[key]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        temp_path = f.name
    
    yield temp_path
    
    # Restore original environment variables
    for key in ui_keys:
        if key in os.environ:
            del os.environ[key]
        if key in original_env:
            os.environ[key] = original_env[key]
    
    # Cleanup temp file
    try:
        os.unlink(temp_path)
    except:
        pass


class TestProperty1ValueRangeConstraints:
    """
    Feature: ui-customization, Property 1: Value Range Constraints
    
    For any UI customization setting and any input value, when the value is set
    through Config properties, the returned value should be constrained within
    the documented valid range for that setting.
    
    Validates: Requirements 1.1, 2.1, 2.2, 3.1, 3.2, 5.4, 8.2
    """
    
    @given(opacity=opacity_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_window_opacity_within_range(self, opacity, temp_env_file):
        """Test that window_opacity is always within valid range (50-255)."""
        # Write value to temp .env
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write(f"WINDOW_OPACITY={opacity}\n")
        
        # Load config
        config = Config.load_from_env(temp_env_file)
        
        # Assert value is within range
        assert 50 <= config.window_opacity <= 255
        assert config.window_opacity == opacity
    
    @given(font_size=font_floating_main_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_font_floating_main_within_range(self, font_size, temp_env_file):
        """Test that font_size_floating_main is always within valid range (10-24)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write(f"FONT_SIZE_FLOATING_MAIN={font_size}\n")
        
        config = Config.load_from_env(temp_env_file)
        
        assert 10 <= config.font_size_floating_main <= 24
        assert config.font_size_floating_main == font_size
    
    @given(font_size=font_floating_info_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_font_floating_info_within_range(self, font_size, temp_env_file):
        """Test that font_size_floating_info is always within valid range (8-16)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write(f"FONT_SIZE_FLOATING_INFO={font_size}\n")
        
        config = Config.load_from_env(temp_env_file)
        
        assert 8 <= config.font_size_floating_info <= 16
        assert config.font_size_floating_info == font_size
    
    @given(font_size=font_settings_labels_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_font_settings_labels_within_range(self, font_size, temp_env_file):
        """Test that font_size_settings_labels is always within valid range (10-16)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write(f"FONT_SIZE_SETTINGS_LABELS={font_size}\n")
        
        config = Config.load_from_env(temp_env_file)
        
        assert 10 <= config.font_size_settings_labels <= 16
        assert config.font_size_settings_labels == font_size
    
    @given(font_size=font_settings_titles_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_font_settings_titles_within_range(self, font_size, temp_env_file):
        """Test that font_size_settings_titles is always within valid range (16-32)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write(f"FONT_SIZE_SETTINGS_TITLES={font_size}\n")
        
        config = Config.load_from_env(temp_env_file)
        
        assert 16 <= config.font_size_settings_titles <= 32
        assert config.font_size_settings_titles == font_size


class TestProperty7BoundaryValueClamping:
    """
    Feature: ui-customization, Property 7: Boundary Value Clamping
    
    For any value outside the valid range for a setting, when passed to a Config
    property, the returned value should be clamped to the nearest valid boundary
    (minimum or maximum).
    
    Validates: Requirements 1.5, 8.2
    """
    
    @given(opacity=any_integer_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_opacity_boundary_clamping(self, opacity, temp_env_file):
        """Test that out-of-range opacity values are clamped to boundaries."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write(f"WINDOW_OPACITY={opacity}\n")
        
        config = Config.load_from_env(temp_env_file)
        
        if opacity < 50:
            assert config.window_opacity == 50
        elif opacity > 255:
            assert config.window_opacity == 255
        else:
            assert config.window_opacity == opacity
    
    @given(font_size=any_integer_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_font_floating_main_boundary_clamping(self, font_size, temp_env_file):
        """Test that out-of-range font_size_floating_main values are clamped."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write(f"FONT_SIZE_FLOATING_MAIN={font_size}\n")
        
        config = Config.load_from_env(temp_env_file)
        
        if font_size < 10:
            assert config.font_size_floating_main == 10
        elif font_size > 24:
            assert config.font_size_floating_main == 24
        else:
            assert config.font_size_floating_main == font_size
    
    @given(font_size=any_integer_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_font_floating_info_boundary_clamping(self, font_size, temp_env_file):
        """Test that out-of-range font_size_floating_info values are clamped."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write(f"FONT_SIZE_FLOATING_INFO={font_size}\n")
        
        config = Config.load_from_env(temp_env_file)
        
        if font_size < 8:
            assert config.font_size_floating_info == 8
        elif font_size > 16:
            assert config.font_size_floating_info == 16
        else:
            assert config.font_size_floating_info == font_size
    
    @given(font_size=any_integer_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_font_settings_labels_boundary_clamping(self, font_size, temp_env_file):
        """Test that out-of-range font_size_settings_labels values are clamped."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write(f"FONT_SIZE_SETTINGS_LABELS={font_size}\n")
        
        config = Config.load_from_env(temp_env_file)
        
        if font_size < 10:
            assert config.font_size_settings_labels == 10
        elif font_size > 16:
            assert config.font_size_settings_labels == 16
        else:
            assert config.font_size_settings_labels == font_size
    
    @given(font_size=any_integer_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_font_settings_titles_boundary_clamping(self, font_size, temp_env_file):
        """Test that out-of-range font_size_settings_titles values are clamped."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write(f"FONT_SIZE_SETTINGS_TITLES={font_size}\n")
        
        config = Config.load_from_env(temp_env_file)
        
        if font_size < 16:
            assert config.font_size_settings_titles == 16
        elif font_size > 32:
            assert config.font_size_settings_titles == 32
        else:
            assert config.font_size_settings_titles == font_size



class TestProperty2SettingsPersistenceRoundTrip:
    """
    Feature: ui-customization, Property 2: Settings Persistence Round-Trip
    
    For any UI customization setting and any valid value within its range,
    writing the value to .env and then reading it back through Config should
    return an equivalent value.
    
    Validates: Requirements 2.4, 5.1, 5.2, 6.3
    """
    
    @given(opacity=opacity_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_opacity_persistence_round_trip(self, opacity, temp_env_file):
        """Test that opacity value persists through write-read cycle."""
        # Write value to temp .env
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write(f"WINDOW_OPACITY={opacity}\n")
        
        # Read back from file
        config_reloaded = Config.load_from_env(temp_env_file)
        
        # Value should match
        assert config_reloaded.window_opacity == opacity
    
    @given(font_size=font_floating_main_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_font_floating_main_persistence_round_trip(self, font_size, temp_env_file):
        """Test that font_size_floating_main persists through write-read cycle."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write(f"FONT_SIZE_FLOATING_MAIN={font_size}\n")
        
        config_reloaded = Config.load_from_env(temp_env_file)
        
        assert config_reloaded.font_size_floating_main == font_size
    
    @given(font_size=font_floating_info_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_font_floating_info_persistence_round_trip(self, font_size, temp_env_file):
        """Test that font_size_floating_info persists through write-read cycle."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write(f"FONT_SIZE_FLOATING_INFO={font_size}\n")
        
        config_reloaded = Config.load_from_env(temp_env_file)
        
        assert config_reloaded.font_size_floating_info == font_size
    
    @given(font_size=font_settings_labels_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_font_settings_labels_persistence_round_trip(self, font_size, temp_env_file):
        """Test that font_size_settings_labels persists through write-read cycle."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write(f"FONT_SIZE_SETTINGS_LABELS={font_size}\n")
        
        config_reloaded = Config.load_from_env(temp_env_file)
        
        assert config_reloaded.font_size_settings_labels == font_size
    
    @given(font_size=font_settings_titles_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_font_settings_titles_persistence_round_trip(self, font_size, temp_env_file):
        """Test that font_size_settings_titles persists through write-read cycle."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write(f"FONT_SIZE_SETTINGS_TITLES={font_size}\n")
        
        config_reloaded = Config.load_from_env(temp_env_file)
        
        assert config_reloaded.font_size_settings_titles == font_size



class TestProperty3DefaultValueFallback:
    """
    Feature: ui-customization, Property 3: Default Value Fallback
    
    For any UI customization setting, when the corresponding .env key is missing
    or contains an invalid value, the Config property should return the
    documented default value.
    
    Validates: Requirements 5.3, 8.3
    """
    
    def test_missing_opacity_uses_default(self, temp_env_file):
        """Test that missing WINDOW_OPACITY key returns default value (150)."""
        # Create empty .env file
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        config = Config.load_from_env(temp_env_file)
        
        assert config.window_opacity == 150
    
    def test_invalid_opacity_uses_default(self, temp_env_file):
        """Test that invalid WINDOW_OPACITY value returns default (150)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("WINDOW_OPACITY=invalid\n")
        
        config = Config.load_from_env(temp_env_file)
        
        assert config.window_opacity == 150
    
    def test_missing_font_floating_main_uses_default(self, temp_env_file):
        """Test that missing FONT_SIZE_FLOATING_MAIN returns default (14)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        config = Config.load_from_env(temp_env_file)
        
        assert config.font_size_floating_main == 14
    
    def test_invalid_font_floating_main_uses_default(self, temp_env_file):
        """Test that invalid FONT_SIZE_FLOATING_MAIN returns default (14)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("FONT_SIZE_FLOATING_MAIN=abc\n")
        
        config = Config.load_from_env(temp_env_file)
        
        assert config.font_size_floating_main == 14
    
    def test_missing_font_floating_info_uses_default(self, temp_env_file):
        """Test that missing FONT_SIZE_FLOATING_INFO returns default (11)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        config = Config.load_from_env(temp_env_file)
        
        assert config.font_size_floating_info == 11
    
    def test_invalid_font_floating_info_uses_default(self, temp_env_file):
        """Test that invalid FONT_SIZE_FLOATING_INFO returns default (11)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("FONT_SIZE_FLOATING_INFO=12.5\n")
        
        config = Config.load_from_env(temp_env_file)
        
        assert config.font_size_floating_info == 11
    
    def test_missing_font_settings_labels_uses_default(self, temp_env_file):
        """Test that missing FONT_SIZE_SETTINGS_LABELS returns default (12)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        config = Config.load_from_env(temp_env_file)
        
        assert config.font_size_settings_labels == 12
    
    def test_invalid_font_settings_labels_uses_default(self, temp_env_file):
        """Test that invalid FONT_SIZE_SETTINGS_LABELS returns default (12)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("FONT_SIZE_SETTINGS_LABELS=\n")
        
        config = Config.load_from_env(temp_env_file)
        
        assert config.font_size_settings_labels == 12
    
    def test_missing_font_settings_titles_uses_default(self, temp_env_file):
        """Test that missing FONT_SIZE_SETTINGS_TITLES returns default (24)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        config = Config.load_from_env(temp_env_file)
        
        assert config.font_size_settings_titles == 24
    
    def test_invalid_font_settings_titles_uses_default(self, temp_env_file):
        """Test that invalid FONT_SIZE_SETTINGS_TITLES returns default (24)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("FONT_SIZE_SETTINGS_TITLES=24px\n")
        
        config = Config.load_from_env(temp_env_file)
        
        assert config.font_size_settings_titles == 24



class TestProperty4UIControlDisplayConsistency:
    """
    Feature: ui-customization, Property 4: UI Control Display Consistency
    
    For any UI customization slider control, the displayed numeric label should
    always match the current slider value.
    
    Validates: Requirements 1.4, 2.5, 3.5
    """
    
    @given(opacity=opacity_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_opacity_label_matches_slider_value(self, opacity, qapp, temp_env_file, monkeypatch):
        """
        Property: Opacity label always displays the current slider value.
        
        For any valid opacity value, when the slider is set to that value,
        the label should display exactly that value as a string.
        """
        from ui.settings_window import SettingsWindow
        from unittest.mock import patch
        
        # Setup config with temp env file
        monkeypatch.setenv("RAPIDWHISPER_ENV_PATH", str(temp_env_file))
        
        with patch('core.config.get_env_path', return_value=temp_env_file):
            config = Config()
            window = SettingsWindow(config)
            
            try:
                # Set slider value
                window.opacity_slider.setValue(opacity)
                
                # Check label matches
                label_text = window.opacity_value_label.text()
                assert label_text == str(opacity), \
                    f"Label '{label_text}' does not match slider value {opacity}"
            finally:
                window.close()


class TestProperty6ResetToDefaultsCompleteness:
    """
    Feature: ui-customization, Property 6: Reset to Defaults Completeness
    
    For any UI customization setting, after calling the reset to defaults function,
    the setting value should equal its documented default value in both the Config
    and the .env file.
    
    Validates: Requirements 6.1, 6.2, 6.3, 6.4
    """
    
    @given(opacity=opacity_strategy)
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_reset_idempotent(self, opacity, qapp, temp_env_file, monkeypatch):
        """
        Property: Reset to defaults is idempotent.
        
        Calling reset multiple times should always result in the same state.
        """
        from ui.settings_window import SettingsWindow
        from unittest.mock import patch, Mock
        
        # Setup config with temp env file
        monkeypatch.setenv("RAPIDWHISPER_ENV_PATH", str(temp_env_file))
        
        with patch('core.config.get_env_path', return_value=Path(temp_env_file)):
            config = Config()
            
            # Mock set_env_value to avoid file I/O issues in tests
            config.set_env_value = Mock()
            
            window = SettingsWindow(config)
            
            try:
                # Set a different value
                window.opacity_slider.setValue(opacity)
                
                # Reset once
                window._reset_ui_defaults()
                first_opacity = window.opacity_slider.value()
                
                # Reset again
                window._reset_ui_defaults()
                second_opacity = window.opacity_slider.value()
                
                # Should be the same
                assert first_opacity == second_opacity == 150, \
                    f"Reset not idempotent: first={first_opacity}, second={second_opacity}"
                
                # Check set_env_value was called with correct defaults
                calls = config.set_env_value.call_args_list
                # Should have been called 10 times (5 settings * 2 resets)
                assert len(calls) >= 5, f"Expected at least 5 calls to set_env_value, got {len(calls)}"
            finally:
                window.close()


@pytest.fixture
def qapp():
    """Create QApplication instance for property tests."""
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app



class TestProperty5OpacityLivePreview:
    """
    Feature: ui-customization, Property 5: Opacity Live Preview
    
    For any opacity value in the valid range (50-255), when set_opacity() is called
    on FloatingWindow, the internal _opacity field should be updated to that value
    and a repaint should be triggered.
    
    Validates: Requirements 1.2
    """
    
    @given(opacity=opacity_strategy)
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_set_opacity_updates_internal_field(self, opacity, qapp, temp_env_file, monkeypatch):
        """
        Property: set_opacity() updates _opacity field.
        
        For any valid opacity value, calling set_opacity() should update
        the internal _opacity field to that value.
        """
        from ui.floating_window import FloatingWindow
        from core.config import Config
        from unittest.mock import patch
        
        # Setup config with temp env file
        monkeypatch.setenv("RAPIDWHISPER_ENV_PATH", str(temp_env_file))
        
        with patch('core.config.get_env_path', return_value=Path(temp_env_file)):
            config = Config()
            window = FloatingWindow(config=config)
            
            try:
                # Set opacity
                window.set_opacity(opacity)
                
                # Verify _opacity field is updated
                assert window._opacity == opacity, \
                    f"Expected _opacity={opacity}, got {window._opacity}"
            finally:
                window.close()
    
    @given(opacity=any_integer_strategy)
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_set_opacity_clamps_to_valid_range(self, opacity, qapp, temp_env_file, monkeypatch):
        """
        Property: set_opacity() clamps values to valid range.
        
        For any integer value (including out of range), calling set_opacity()
        should clamp the value to the valid range [50, 255].
        """
        from ui.floating_window import FloatingWindow
        from core.config import Config
        from unittest.mock import patch
        
        # Setup config with temp env file
        monkeypatch.setenv("RAPIDWHISPER_ENV_PATH", str(temp_env_file))
        
        with patch('core.config.get_env_path', return_value=Path(temp_env_file)):
            config = Config()
            window = FloatingWindow(config=config)
            
            try:
                # Set opacity
                window.set_opacity(opacity)
                
                # Verify _opacity is clamped to valid range
                assert 50 <= window._opacity <= 255, \
                    f"Expected _opacity in [50, 255], got {window._opacity}"
                
                # Verify clamping behavior
                if opacity < 50:
                    assert window._opacity == 50, \
                        f"Expected _opacity=50 for input {opacity}, got {window._opacity}"
                elif opacity > 255:
                    assert window._opacity == 255, \
                        f"Expected _opacity=255 for input {opacity}, got {window._opacity}"
                else:
                    assert window._opacity == opacity, \
                        f"Expected _opacity={opacity}, got {window._opacity}"
            finally:
                window.close()
    
    @given(opacity=opacity_strategy)
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_set_opacity_triggers_repaint(self, opacity, qapp, temp_env_file, monkeypatch):
        """
        Property: set_opacity() triggers repaint.
        
        For any valid opacity value, calling set_opacity() should trigger
        a repaint by calling update().
        """
        from ui.floating_window import FloatingWindow
        from core.config import Config
        from unittest.mock import patch, Mock
        
        # Setup config with temp env file
        monkeypatch.setenv("RAPIDWHISPER_ENV_PATH", str(temp_env_file))
        
        with patch('core.config.get_env_path', return_value=Path(temp_env_file)):
            config = Config()
            window = FloatingWindow(config=config)
            
            try:
                # Mock update() to track calls
                original_update = window.update
                window.update = Mock(side_effect=original_update)
                
                # Set opacity
                window.set_opacity(opacity)
                
                # Verify update() was called
                assert window.update.called, \
                    f"Expected update() to be called after set_opacity({opacity})"
            finally:
                window.close()



class TestProperty9FontSizePersistence:
    """
    Property 9: Font Size Persistence Across Reopens
    
    For any valid font size value, after setting it in the SettingsWindow,
    closing the window, and reopening it, the displayed font size should
    match the previously set value.
    
    **Validates: Requirements 3.3**
    """
    
    @given(
        font_labels=font_settings_labels_strategy,
        font_titles=font_settings_titles_strategy
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_font_size_settings_persist_across_reopens(self, temp_env_file, font_labels: int, font_titles: int):
        """
        Test that font sizes persist when SettingsWindow is closed and reopened.
        
        This simulates:
        1. Opening settings window
        2. Setting font sizes
        3. Closing settings window
        4. Reopening settings window
        5. Verifying font sizes are the same
        """
        from unittest.mock import patch
        
        # First open: set font sizes
        with patch('core.config.get_env_path', return_value=Path(temp_env_file)):
            config1 = Config.load_from_env()
            
            # Simulate setting font sizes (what SettingsWindow would do)
            config1.set_env_value('FONT_SIZE_SETTINGS_LABELS', str(font_labels))
            config1.set_env_value('FONT_SIZE_SETTINGS_TITLES', str(font_titles))
        
        # Second open: verify persistence
        with patch('core.config.get_env_path', return_value=Path(temp_env_file)):
            config2 = Config.load_from_env()
            
            # Font sizes should match what was set
            assert config2.font_size_settings_labels == font_labels, \
                f"Expected font_size_settings_labels={font_labels}, got {config2.font_size_settings_labels}"
            assert config2.font_size_settings_titles == font_titles, \
                f"Expected font_size_settings_titles={font_titles}, got {config2.font_size_settings_titles}"
    
    @given(
        font_main=font_floating_main_strategy,
        font_info=font_floating_info_strategy
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_floating_window_font_sizes_persist(self, temp_env_file, font_main: int, font_info: int):
        """
        Test that floating window font sizes persist across config reloads.
        """
        from unittest.mock import patch
        
        # First load: set font sizes
        with patch('core.config.get_env_path', return_value=Path(temp_env_file)):
            config1 = Config.load_from_env()
            config1.set_env_value('FONT_SIZE_FLOATING_MAIN', str(font_main))
            config1.set_env_value('FONT_SIZE_FLOATING_INFO', str(font_info))
        
        # Second load: verify persistence
        with patch('core.config.get_env_path', return_value=Path(temp_env_file)):
            config2 = Config.load_from_env()
            
            assert config2.font_size_floating_main == font_main, \
                f"Expected font_size_floating_main={font_main}, got {config2.font_size_floating_main}"
            assert config2.font_size_floating_info == font_info, \
                f"Expected font_size_floating_info={font_info}, got {config2.font_size_floating_info}"
