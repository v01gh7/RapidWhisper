"""Tests for Statistics Tab integration into Settings Window."""

import pytest
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from core.config import Config
from core.statistics_manager import StatisticsManager
from ui.settings_window import SettingsWindow
from ui.statistics_tab import StatisticsTab
import tempfile


@pytest.fixture
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def statistics_manager(temp_config_dir):
    """Create a StatisticsManager instance for testing."""
    return StatisticsManager(temp_config_dir)


@pytest.fixture
def config():
    """Create a Config instance for testing."""
    return Config.load_from_env()


@pytest.fixture
def settings_window_with_stats(qapp, config, statistics_manager):
    """Create SettingsWindow with StatisticsManager for testing."""
    window = SettingsWindow(config, statistics_manager=statistics_manager)
    yield window
    window.close()


@pytest.fixture
def settings_window_without_stats(qapp, config):
    """Create SettingsWindow without StatisticsManager for testing."""
    window = SettingsWindow(config, statistics_manager=None)
    yield window
    window.close()


class TestStatisticsTabIntegration:
    """Test Statistics Tab integration into Settings Window."""
    
    def test_statistics_tab_exists_with_manager(self, settings_window_with_stats):
        """Test that Statistics tab is added when statistics_manager is provided."""
        # Should have 9 tabs (including Statistics)
        assert settings_window_with_stats.content_stack.count() == 9
        assert settings_window_with_stats.sidebar.count() == 9
    
    def test_statistics_tab_position(self, settings_window_with_stats):
        """Test that Statistics tab is positioned after Recordings and before About."""
        # Find Statistics item in sidebar
        statistics_index = None
        for i in range(settings_window_with_stats.sidebar.count()):
            item = settings_window_with_stats.sidebar.item(i)
            if "Statistics" in item.text() or "📊" in item.text():
                statistics_index = i
                break
        
        assert statistics_index is not None, "Statistics tab not found in sidebar"
        assert statistics_index == 7, f"Statistics tab should be at index 7, found at {statistics_index}"
        
        # Verify Recordings is before Statistics
        recordings_item = settings_window_with_stats.sidebar.item(6)
        assert "🎙️" in recordings_item.text() or "Recordings" in recordings_item.text()
        
        # Verify About is after Statistics
        about_item = settings_window_with_stats.sidebar.item(8)
        assert "ℹ️" in about_item.text() or "About" in about_item.text()
    
    def test_statistics_tab_is_statistics_tab_instance(self, settings_window_with_stats):
        """Test that the Statistics tab is an instance of StatisticsTab."""
        # Navigate to Statistics tab
        settings_window_with_stats.sidebar.setCurrentRow(7)
        
        # Get the scroll area widget
        scroll_area = settings_window_with_stats.content_stack.widget(7)
        
        # Get the actual widget inside the scroll area
        statistics_widget = scroll_area.widget()
        
        assert isinstance(statistics_widget, StatisticsTab), \
            f"Expected StatisticsTab instance, got {type(statistics_widget)}"
    
    def test_statistics_tab_has_statistics_manager(self, settings_window_with_stats, statistics_manager):
        """Test that Statistics tab has access to the statistics manager."""
        # Navigate to Statistics tab
        settings_window_with_stats.sidebar.setCurrentRow(7)
        
        # Get the statistics tab widget
        scroll_area = settings_window_with_stats.content_stack.widget(7)
        statistics_widget = scroll_area.widget()
        
        assert hasattr(statistics_widget, 'statistics_manager')
        assert statistics_widget.statistics_manager is statistics_manager
    
    def test_statistics_tab_displays_data(self, settings_window_with_stats, statistics_manager):
        """Test that Statistics tab displays data from the statistics manager."""
        # Add some test data
        statistics_manager.track_recording(120.5)
        statistics_manager.track_transcription(120.5, "This is a test transcription.")
        statistics_manager.track_silence_removal(15.3)
        
        # Navigate to Statistics tab
        settings_window_with_stats.sidebar.setCurrentRow(7)
        
        # Get the statistics tab widget
        scroll_area = settings_window_with_stats.content_stack.widget(7)
        statistics_widget = scroll_area.widget()
        
        # Verify metric cards exist
        assert hasattr(statistics_widget, 'metric_cards')
        assert 'recordings' in statistics_widget.metric_cards
        assert 'transcriptions' in statistics_widget.metric_cards
        assert 'silence' in statistics_widget.metric_cards
    
    def test_placeholder_when_no_manager(self, settings_window_without_stats):
        """Test that a placeholder is shown when no statistics_manager is provided."""
        # Should still have 9 tabs (with placeholder)
        assert settings_window_without_stats.content_stack.count() == 9
        assert settings_window_without_stats.sidebar.count() == 9
        
        # Navigate to Statistics tab position
        settings_window_without_stats.sidebar.setCurrentRow(7)
        
        # Get the widget at Statistics position
        scroll_area = settings_window_without_stats.content_stack.widget(7)
        widget = scroll_area.widget()
        
        # Should not be a StatisticsTab instance
        assert not isinstance(widget, StatisticsTab)
    
    def test_statistics_tab_navigation(self, settings_window_with_stats):
        """Test that navigating to Statistics tab works correctly."""
        # Navigate to Statistics tab
        settings_window_with_stats.sidebar.setCurrentRow(7)
        
        # Verify the content stack shows the correct page
        assert settings_window_with_stats.content_stack.currentIndex() == 7
        
        # Verify the sidebar selection is correct
        assert settings_window_with_stats.sidebar.currentRow() == 7


class TestStatisticsTabLabel:
    """Test Statistics Tab label and icon."""
    
    def test_statistics_tab_has_icon(self, settings_window_with_stats):
        """Test that Statistics tab has the correct icon."""
        statistics_item = settings_window_with_stats.sidebar.item(7)
        assert "📊" in statistics_item.text()
    
    def test_statistics_tab_has_label(self, settings_window_with_stats):
        """Test that Statistics tab has the correct label."""
        from utils.i18n import t
        statistics_item = settings_window_with_stats.sidebar.item(7)
        # Check that the translated statistics title is in the text
        assert t('settings.statistics.title') in statistics_item.text()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
