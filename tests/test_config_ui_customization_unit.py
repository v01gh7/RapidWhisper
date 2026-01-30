"""
Unit tests for UI Customization Config properties.

Tests specific examples, edge cases, and error conditions.
"""

import pytest
from core.config import Config, get_env_path
import os
import tempfile
from pathlib import Path


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False, encoding='utf-8') as f:
        temp_path = f.name
    yield temp_path
    # Cleanup
    try:
        os.unlink(temp_path)
    except:
        pass


class TestWindowOpacity:
    """Test window_opacity property."""
    
    def test_default_value(self, temp_env_file):
        """Test that default opacity is 150."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        config = Config.load_from_env(temp_env_file)
        assert config.window_opacity == 150
    
    def test_valid_value(self, temp_env_file):
        """Test loading valid opacity value."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("WINDOW_OPACITY=200\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.window_opacity == 200
    
    def test_minimum_boundary(self, temp_env_file):
        """Test minimum boundary value (50)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("WINDOW_OPACITY=50\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.window_opacity == 50
    
    def test_maximum_boundary(self, temp_env_file):
        """Test maximum boundary value (255)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("WINDOW_OPACITY=255\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.window_opacity == 255
    
    def test_below_minimum_clamped(self, temp_env_file):
        """Test value below minimum is clamped to 50."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("WINDOW_OPACITY=30\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.window_opacity == 50
    
    def test_above_maximum_clamped(self, temp_env_file):
        """Test value above maximum is clamped to 255."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("WINDOW_OPACITY=300\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.window_opacity == 255
    
    def test_invalid_value_uses_default(self, temp_env_file):
        """Test invalid value uses default."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("WINDOW_OPACITY=abc\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.window_opacity == 150


class TestFontSizeFloatingMain:
    """Test font_size_floating_main property."""
    
    def test_default_value(self, temp_env_file):
        """Test that default font size is 14."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        config = Config.load_from_env(temp_env_file)
        assert config.font_size_floating_main == 14
    
    def test_valid_value(self, temp_env_file):
        """Test loading valid font size."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("FONT_SIZE_FLOATING_MAIN=18\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.font_size_floating_main == 18
    
    def test_minimum_boundary(self, temp_env_file):
        """Test minimum boundary value (10)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("FONT_SIZE_FLOATING_MAIN=10\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.font_size_floating_main == 10
    
    def test_maximum_boundary(self, temp_env_file):
        """Test maximum boundary value (24)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("FONT_SIZE_FLOATING_MAIN=24\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.font_size_floating_main == 24
    
    def test_below_minimum_clamped(self, temp_env_file):
        """Test value below minimum is clamped to 10."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("FONT_SIZE_FLOATING_MAIN=5\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.font_size_floating_main == 10
    
    def test_above_maximum_clamped(self, temp_env_file):
        """Test value above maximum is clamped to 24."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("FONT_SIZE_FLOATING_MAIN=30\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.font_size_floating_main == 24


class TestFontSizeFloatingInfo:
    """Test font_size_floating_info property."""
    
    def test_default_value(self, temp_env_file):
        """Test that default font size is 11."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        config = Config.load_from_env(temp_env_file)
        assert config.font_size_floating_info == 11
    
    def test_valid_value(self, temp_env_file):
        """Test loading valid font size."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("FONT_SIZE_FLOATING_INFO=12\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.font_size_floating_info == 12
    
    def test_minimum_boundary(self, temp_env_file):
        """Test minimum boundary value (8)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("FONT_SIZE_FLOATING_INFO=8\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.font_size_floating_info == 8
    
    def test_maximum_boundary(self, temp_env_file):
        """Test maximum boundary value (16)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("FONT_SIZE_FLOATING_INFO=16\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.font_size_floating_info == 16


class TestFontSizeSettingsLabels:
    """Test font_size_settings_labels property."""
    
    def test_default_value(self, temp_env_file):
        """Test that default font size is 12."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        config = Config.load_from_env(temp_env_file)
        assert config.font_size_settings_labels == 12
    
    def test_valid_value(self, temp_env_file):
        """Test loading valid font size."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("FONT_SIZE_SETTINGS_LABELS=14\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.font_size_settings_labels == 14
    
    def test_minimum_boundary(self, temp_env_file):
        """Test minimum boundary value (10)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("FONT_SIZE_SETTINGS_LABELS=10\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.font_size_settings_labels == 10
    
    def test_maximum_boundary(self, temp_env_file):
        """Test maximum boundary value (16)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("FONT_SIZE_SETTINGS_LABELS=16\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.font_size_settings_labels == 16


class TestFontSizeSettingsTitles:
    """Test font_size_settings_titles property."""
    
    def test_default_value(self, temp_env_file):
        """Test that default font size is 24."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        config = Config.load_from_env(temp_env_file)
        assert config.font_size_settings_titles == 24
    
    def test_valid_value(self, temp_env_file):
        """Test loading valid font size."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("FONT_SIZE_SETTINGS_TITLES=28\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.font_size_settings_titles == 28
    
    def test_minimum_boundary(self, temp_env_file):
        """Test minimum boundary value (16)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("FONT_SIZE_SETTINGS_TITLES=16\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.font_size_settings_titles == 16
    
    def test_maximum_boundary(self, temp_env_file):
        """Test maximum boundary value (32)."""
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("FONT_SIZE_SETTINGS_TITLES=32\n")
        
        config = Config.load_from_env(temp_env_file)
        assert config.font_size_settings_titles == 32


class TestSetEnvValue:
    """Test set_env_value method."""
    
    def test_creates_new_key(self, temp_env_file):
        """Test that set_env_value creates new key in empty file."""
        # Create empty file
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("")
        
        # Create config and set value
        config = Config()
        # Temporarily override get_env_path to use temp file
        import core.config as config_module
        original_get_env_path = config_module.get_env_path
        config_module.get_env_path = lambda: Path(temp_env_file)
        
        try:
            config.set_env_value('WINDOW_OPACITY', '200')
            
            # Read file and verify
            with open(temp_env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert 'WINDOW_OPACITY=200' in content
        finally:
            config_module.get_env_path = original_get_env_path
    
    def test_updates_existing_key(self, temp_env_file):
        """Test that set_env_value updates existing key."""
        # Create file with existing key
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("WINDOW_OPACITY=150\n")
            f.write("OTHER_KEY=value\n")
        
        config = Config()
        import core.config as config_module
        original_get_env_path = config_module.get_env_path
        config_module.get_env_path = lambda: Path(temp_env_file)
        
        try:
            config.set_env_value('WINDOW_OPACITY', '200')
            
            # Read file and verify
            with open(temp_env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert 'WINDOW_OPACITY=200' in content
            assert 'OTHER_KEY=value' in content
            assert content.count('WINDOW_OPACITY') == 1  # Only one occurrence
        finally:
            config_module.get_env_path = original_get_env_path
    
    def test_preserves_comments(self, temp_env_file):
        """Test that set_env_value preserves comments."""
        # Create file with comments
        with open(temp_env_file, 'w', encoding='utf-8') as f:
            f.write("# This is a comment\n")
            f.write("WINDOW_OPACITY=150\n")
            f.write("# Another comment\n")
        
        config = Config()
        import core.config as config_module
        original_get_env_path = config_module.get_env_path
        config_module.get_env_path = lambda: Path(temp_env_file)
        
        try:
            config.set_env_value('WINDOW_OPACITY', '200')
            
            # Read file and verify
            with open(temp_env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert '# This is a comment' in content
            assert '# Another comment' in content
            assert 'WINDOW_OPACITY=200' in content
        finally:
            config_module.get_env_path = original_get_env_path
