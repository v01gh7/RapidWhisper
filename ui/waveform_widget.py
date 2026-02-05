"""
Виджет визуализации звуковой волны для RapidWhisper.

Отображает динамическую звуковую волну во время записи и
спиннер загрузки во время обработки.
"""

from enum import Enum
from typing import List
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QPaintEvent
import math


class AnimationState(Enum):
    """Состояния анимации виджета"""
    IDLE = "idle"
    WAVEFORM = "waveform"
    SPINNER = "spinner"


class WaveformWidget(QWidget):
    """
    Виджет для отрисовки звуковой волны и индикатора загрузки.
    
    Отображает динамическую визуализацию звуковой волны во время записи
    и вращающийся спиннер во время обработки через API.
    
    Requirements: 4.1, 4.2, 4.4, 4.6, 7.1, 7.2, 7.3
    """
    
    def __init__(self, parent=None, config=None):
        """
        Инициализирует виджет визуализации.
        
        Args:
            parent: Родительский виджет
            config: Объект конфигурации для получения цвета волны
        """
        super().__init__(parent)
        
        # Сохранить конфигурацию
        self.config = config
        
        # Параметры визуализации
        self.rms_values: List[float] = []
        self.max_bars: int = 50
        self.smoothed_rms: float = 0.0
        self.smoothing_factor: float = 0.3  # Для exponential smoothing
        
        # Цвет волны (по умолчанию синий)
        self._waveform_color = "#64AAFF"
        if config and hasattr(config, 'waveform_color'):
            self._waveform_color = config.waveform_color
        
        # Состояние анимации
        self.animation_state: AnimationState = AnimationState.IDLE
        
        # Таймер для обновления анимации
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_animation)
        self.update_interval_ms: int = 50  # 20 FPS
        
        # Параметры спиннера
        self.spinner_angle: float = 0.0
        self.spinner_speed: float = 10.0  # Градусов за кадр
        
        # Настройка виджета
        self.setMinimumSize(300, 80)
        self.setMaximumHeight(100)
    
    def set_waveform_color(self, color: str) -> None:
        """
        Устанавливает цвет волны.
        
        Args:
            color: Цвет в формате HEX (например, "#64AAFF")
        """
        self._waveform_color = color
        self.update()  # Перерисовать виджет
    
    def update_rms(self, rms: float) -> None:
        """
        Обновляет значение RMS для визуализации.
        
        Применяет exponential smoothing для плавности и добавляет
        значение в скользящее окно.
        
        Args:
            rms: Текущее RMS значение громкости (0.0 - 1.0)
        
        Requirements: 4.1, 4.2, 4.6
        """
        # Применяем exponential smoothing
        self.smoothed_rms = (self.smoothing_factor * rms + 
                            (1 - self.smoothing_factor) * self.smoothed_rms)
        
        # Добавляем в скользящее окно
        self.rms_values.append(self.smoothed_rms)
        
        # Ограничиваем размер окна
        if len(self.rms_values) > self.max_bars:
            self.rms_values.pop(0)
        
        # Перерисовываем виджет
        self.update()
    
    def start_recording_animation(self) -> None:
        """
        Запускает анимацию волны.
        
        Переключает виджет в режим отображения звуковой волны
        и запускает таймер обновления.
        
        Requirements: 4.1
        """
        self.animation_state = AnimationState.WAVEFORM
        self.rms_values.clear()
        self.smoothed_rms = 0.0
        
        if not self.timer.isActive():
            self.timer.start(self.update_interval_ms)
        
        self.update()
    
    def start_loading_animation(self) -> None:
        """
        Переключается на спиннер загрузки.
        
        Трансформирует визуализацию из волны в спиннер для
        отображения процесса обработки через API.
        
        Requirements: 7.1, 7.2
        """
        self.animation_state = AnimationState.SPINNER
        self.spinner_angle = 0.0
        
        if not self.timer.isActive():
            self.timer.start(self.update_interval_ms)
        
        self.update()
    
    def stop_animation(self) -> None:
        """
        Останавливает все анимации.
        
        Останавливает таймер и переводит виджет в состояние IDLE.
        
        Requirements: 7.5
        """
        self.animation_state = AnimationState.IDLE
        
        if self.timer.isActive():
            self.timer.stop()
        
        self.rms_values.clear()
        self.smoothed_rms = 0.0
        self.update()
    
    def _update_animation(self) -> None:
        """
        Обновляет анимацию по таймеру.
        
        Вызывается таймером для обновления спиннера или других
        анимационных эффектов.
        """
        if self.animation_state == AnimationState.SPINNER:
            # Обновляем угол спиннера
            self.spinner_angle = (self.spinner_angle + self.spinner_speed) % 360
            self.update()
    
    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Отрисовывает волну или спиннер.
        
        Вызывается Qt для отрисовки содержимого виджета.
        
        Args:
            event: Событие отрисовки
        
        Requirements: 4.1, 7.1, 7.2
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self.animation_state == AnimationState.WAVEFORM:
            self._draw_waveform(painter)
        elif self.animation_state == AnimationState.SPINNER:
            self._draw_spinner(painter)
    
    def _draw_waveform(self, painter: QPainter) -> None:
        """
        Рисует звуковую волну из RMS значений.
        
        Отрисовывает вертикальные бары с высотой пропорциональной
        RMS значениям. Использует градиент оттенка и яркости от базового цвета.
        
        Args:
            painter: QPainter для отрисовки
        
        Requirements: 4.1, 4.2, 4.4
        """
        if not self.rms_values:
            return
        
        width = self.width()
        height = self.height()
        center_y = height / 2
        
        # Вычисляем ширину каждого бара
        num_bars = len(self.rms_values)
        bar_width = width / max(num_bars, self.max_bars)
        bar_spacing = 2
        
        # Нормализуем значения
        max_rms = max(self.rms_values) if self.rms_values else 1.0
        if max_rms < 0.01:
            max_rms = 0.01  # Избегаем деления на ноль
        
        # Парсим базовый цвет из HEX
        base_color = QColor(self._waveform_color)
        
        # Получаем HSV компоненты базового цвета
        base_h = base_color.hue()
        base_s = base_color.saturation()
        base_v = base_color.value()
        
        # Отрисовываем бары
        for i, rms in enumerate(self.rms_values):
            # Нормализуем высоту (0.0 - 1.0)
            normalized = rms / max_rms
            
            # Вычисляем высоту бара (максимум 80% от высоты виджета)
            bar_height = normalized * height * 0.8
            
            # Позиция бара
            x = i * bar_width
            y = center_y - bar_height / 2
            
            # Создаем градиент оттенка и яркости от базового цвета
            # Диапазон изменения оттенка: ±40 градусов от базового
            # При низкой громкости - сдвиг в одну сторону (темнее)
            # При высокой громкости - сдвиг в другую сторону (ярче)
            hue_shift = int((normalized - 0.5) * 80)  # От -40 до +40
            new_h = (base_h + hue_shift) % 360  # Оборачиваем по кругу (0-359)
            
            # Также меняем яркость для большей выразительности
            # При низкой громкости - 60% яркости, при высокой - 100%
            brightness_factor = 0.6 + (normalized * 0.4)  # От 0.6 до 1.0
            new_v = int(base_v * brightness_factor)
            new_v = max(0, min(255, new_v))  # Ограничиваем диапазон
            
            # Создаем цвет с новым оттенком и яркостью
            color = QColor.fromHsv(new_h, base_s, new_v)
            
            # Рисуем бар
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawRoundedRect(
                int(x + bar_spacing / 2),
                int(y),
                int(bar_width - bar_spacing),
                int(bar_height),
                2, 2
            )
    
    def _draw_spinner(self, painter: QPainter) -> None:
        """
        Рисует вращающийся индикатор загрузки.
        
        Отрисовывает круговой спиннер в центре виджета для
        индикации процесса обработки.
        
        Args:
            painter: QPainter для отрисовки
        
        Requirements: 7.2, 7.3
        """
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        
        # Параметры спиннера
        radius = min(width, height) / 4
        pen_width = 4
        
        # Настройка пера
        pen = QPen(QColor(100, 150, 255))
        pen.setWidth(pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Рисуем дугу спиннера
        num_segments = 8
        for i in range(num_segments):
            angle = self.spinner_angle + (i * 360 / num_segments)
            
            # Вычисляем прозрачность (fade effect)
            alpha = int(255 * (i + 1) / num_segments)
            color = QColor(100, 150, 255, alpha)
            pen.setColor(color)
            painter.setPen(pen)
            
            # Вычисляем позицию точки
            rad = math.radians(angle)
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)
            
            # Рисуем точку
            painter.drawEllipse(
                int(x - pen_width / 2),
                int(y - pen_width / 2),
                pen_width,
                pen_width
            )
    
    def get_update_frequency(self) -> float:
        """
        Возвращает частоту обновления визуализации в FPS.
        
        Returns:
            Частота обновления в кадрах в секунду
        
        Requirements: 9.3
        """
        return 1000.0 / self.update_interval_ms
    
    def set_update_frequency(self, fps: float) -> None:
        """
        Устанавливает частоту обновления визуализации.
        
        Args:
            fps: Желаемая частота в кадрах в секунду (минимум 20 FPS)
        
        Requirements: 9.3
        """
        fps = max(fps, 20.0)  # Минимум 20 FPS
        self.update_interval_ms = int(1000.0 / fps)
        
        if self.timer.isActive():
            self.timer.setInterval(self.update_interval_ms)
