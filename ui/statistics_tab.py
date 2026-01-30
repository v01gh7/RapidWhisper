"""Statistics Tab UI component for displaying usage statistics."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Dict

from core.statistics_manager import StatisticsManager, TimePeriod, AggregatedStats
from utils.i18n import t


class MetricCard(QFrame):
    """A card displaying a single metric with label and value."""
    
    def __init__(self, label: str, value: str, parent=None):
        """Initialize the metric card.
        
        Args:
            label: The label text for the metric
            value: The initial value to display
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        # Dark theme styling to match the rest of the application
        self.setStyleSheet("""
            MetricCard {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        self.label_widget = QLabel(label)
        # Установить шрифт программно
        label_font = QFont("Segoe UI", 12)
        self.label_widget.setFont(label_font)
        # Light gray text for labels, readable on dark background
        self.label_widget.setStyleSheet("color: #aaaaaa;")
        
        self.value_widget = QLabel(value)
        # Установить шрифт программно
        value_font = QFont("Segoe UI", 24)
        value_font.setBold(True)
        self.value_widget.setFont(value_font)
        # White text for values
        self.value_widget.setStyleSheet("color: #ffffff;")
        
        layout.addWidget(self.label_widget)
        layout.addWidget(self.value_widget)
    
    def update_value(self, value: str):
        """Update the displayed value.
        
        Args:
            value: The new value to display
        """
        self.value_widget.setText(value)


class StatisticsTab(QWidget):
    """Tab for displaying usage statistics with time period filtering."""
    
    def __init__(self, statistics_manager: StatisticsManager, parent=None):
        """Initialize the statistics tab.
        
        Args:
            statistics_manager: The statistics manager instance
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.statistics_manager = statistics_manager
        self.metric_cards: Dict[str, MetricCard] = {}
        self._init_ui()
        self._load_statistics(TimePeriod.LAST_7_DAYS)
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Time period filter section
        filter_layout = QHBoxLayout()
        filter_label = QLabel(t('settings.statistics.time_period_label'))
        filter_label.setStyleSheet("color: #ffffff;")
        filter_label.setFont(QFont("Segoe UI", 14))
        
        self.period_combo = QComboBox()
        
        # Установить шрифт программно для QComboBox
        combo_font = QFont("Segoe UI", 12)
        self.period_combo.setFont(combo_font)
        
        # Установить шрифт для выпадающего списка
        self.period_combo.view().setFont(combo_font)
        
        # Простой stylesheet БЕЗ кастомизации стрелочки - Qt сам её нарисует
        self.period_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 8px;
                min-width: 150px;
            }
            QComboBox:hover {
                border: 1px solid #0078d4;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
                border: 1px solid #3d3d3d;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 6px;
                min-height: 25px;
            }
        """)
        
        # Добавить элементы
        self.period_combo.addItem(t('settings.statistics.period_today'), TimePeriod.TODAY)
        self.period_combo.addItem(t('settings.statistics.period_last_7_days'), TimePeriod.LAST_7_DAYS)
        self.period_combo.addItem(t('settings.statistics.period_last_30_days'), TimePeriod.LAST_30_DAYS)
        self.period_combo.addItem(t('settings.statistics.period_last_365_days'), TimePeriod.LAST_365_DAYS)
        self.period_combo.addItem(t('settings.statistics.period_all_time'), TimePeriod.ALL_TIME)
        self.period_combo.setCurrentIndex(1)  # Default to "Last 7 Days"
        self.period_combo.currentIndexChanged.connect(self._on_period_changed)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.period_combo)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Metrics grid layout (2 columns)
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(16)
        
        # Create 7 MetricCard instances for each metric
        self.metric_cards['recordings'] = MetricCard(t('settings.statistics.metric_recordings'), "0")
        self.metric_cards['transcriptions'] = MetricCard(t('settings.statistics.metric_transcriptions'), "0")
        self.metric_cards['recording_time'] = MetricCard(t('settings.statistics.metric_recording_time'), "00:00")
        self.metric_cards['transcribed_time'] = MetricCard(t('settings.statistics.metric_transcribed_time'), "00:00")
        self.metric_cards['characters'] = MetricCard(t('settings.statistics.metric_characters'), "0")
        self.metric_cards['words'] = MetricCard(t('settings.statistics.metric_words'), "0")
        self.metric_cards['silence'] = MetricCard(t('settings.statistics.metric_silence'), "00:00")
        
        # Add cards to grid layout (2 columns)
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
        """Load and display statistics for the selected period.
        
        Args:
            period: The time period to filter statistics by
        """
        try:
            stats = self.statistics_manager.get_statistics(period)
            self._update_display(stats)
        except Exception as e:
            # Log error but don't crash the application
            print(f"Error loading statistics: {e}")
            # Display empty statistics on error
            empty_stats = AggregatedStats()
            self._update_display(empty_stats)
    
    def _update_display(self, stats: AggregatedStats):
        """Update the display with aggregated statistics.
        
        Args:
            stats: The aggregated statistics to display
        """
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
        """Format duration in seconds to HH:MM or MM:SS.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string (HH:MM for >= 1 hour, MM:SS otherwise)
        """
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
        """Format number with thousand separators.
        
        Args:
            number: Integer to format
            
        Returns:
            Formatted number string with comma separators
        """
        return f"{number:,}"
