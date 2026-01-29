"""
UI module for RapidWhisper application.

Contains PyQt6-based user interface components.
"""

from ui.floating_window import FloatingWindow
from ui.tray_icon import TrayIcon
from ui.waveform_widget import WaveformWidget
from ui.settings_window import SettingsWindow

__all__ = ['FloatingWindow', 'TrayIcon', 'WaveformWidget', 'SettingsWindow']
