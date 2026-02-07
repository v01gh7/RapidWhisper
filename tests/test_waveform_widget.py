"""
Тесты для WaveformWidget.

Включает unit-тесты и property-тесты для проверки корректности
визуализации звуковой волны и анимаций.
"""

import pytest
from unittest.mock import Mock, patch
from hypothesis import given, strategies as st, settings, assume
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from ui.waveform_widget import WaveformWidget, AnimationState
import sys


# Создаем QApplication для тестов (требуется для Qt виджетов)
@pytest.fixture(scope="module")
def qapp():
    """Фикстура для создания QApplication"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestWaveformWidgetInitialization:
    """Тесты инициализации WaveformWidget"""
    
    def test_initialization(self, qapp):
        """Тест инициализации виджета"""
        widget = WaveformWidget()
        
        assert widget.animation_state == AnimationState.IDLE
        assert len(widget.rms_values) == 0
        assert widget.smoothed_rms == 0.0
        assert widget.max_bars == 60
        assert not widget.timer.isActive()
    
    def test_has_timer(self, qapp):
        """Тест наличия таймера"""
        widget = WaveformWidget()
        
        assert isinstance(widget.timer, QTimer)
        assert widget.update_interval_ms == 50  # 20 FPS
    
    def test_minimum_size(self, qapp):
        """Тест минимального размера виджета"""
        widget = WaveformWidget()
        
        assert widget.minimumWidth() == 300
        assert widget.minimumHeight() == 80
        assert widget.maximumHeight() == 100


class TestRMSUpdate:
    """Тесты обновления RMS значений"""
    
    def test_update_rms_adds_value(self, qapp):
        """Тест добавления RMS значения"""
        widget = WaveformWidget()
        
        widget.update_rms(0.5)
        
        assert len(widget.rms_values) == 1
        assert widget.smoothed_rms > 0.0
    
    def test_update_rms_smoothing(self, qapp):
        """Тест сглаживания RMS значений"""
        widget = WaveformWidget()
        
        # Первое значение
        widget.update_rms(1.0)
        first_smoothed = widget.smoothed_rms
        
        # Второе значение (должно быть сглажено)
        widget.update_rms(0.0)
        second_smoothed = widget.smoothed_rms
        
        # Сглаженное значение должно быть между 0 и первым значением
        assert 0.0 < second_smoothed < first_smoothed
    
    def test_update_rms_sliding_window(self, qapp):
        """Тест скользящего окна RMS значений"""
        widget = WaveformWidget()
        
        # Добавляем больше значений чем max_bars
        for i in range(60):
            widget.update_rms(0.5)
        
        # Размер не должен превышать max_bars
        assert len(widget.rms_values) == widget.max_bars


class TestAnimationControl:
    """Тесты управления анимацией"""
    
    def test_start_recording_animation(self, qapp):
        """Тест запуска анимации записи"""
        widget = WaveformWidget()
        
        widget.start_recording_animation()
        
        assert widget.animation_state == AnimationState.WAVEFORM
        assert widget.timer.isActive()
        assert len(widget.rms_values) == 0
    
    def test_start_loading_animation(self, qapp):
        """Тест запуска анимации загрузки"""
        widget = WaveformWidget()
        
        widget.start_loading_animation()
        
        assert widget.animation_state == AnimationState.SPINNER
        assert widget.timer.isActive()
        assert widget.spinner_angle == 0.0
    
    def test_stop_animation(self, qapp):
        """Тест остановки анимации"""
        widget = WaveformWidget()
        widget.start_recording_animation()
        
        widget.stop_animation()
        
        assert widget.animation_state == AnimationState.IDLE
        assert not widget.timer.isActive()
        assert len(widget.rms_values) == 0
    
    def test_animation_state_transition(self, qapp):
        """Тест перехода между состояниями анимации"""
        widget = WaveformWidget()
        
        # IDLE -> WAVEFORM
        widget.start_recording_animation()
        assert widget.animation_state == AnimationState.WAVEFORM
        
        # WAVEFORM -> SPINNER
        widget.start_loading_animation()
        assert widget.animation_state == AnimationState.SPINNER
        
        # SPINNER -> IDLE
        widget.stop_animation()
        assert widget.animation_state == AnimationState.IDLE


class TestUpdateFrequency:
    """Тесты частоты обновления"""
    
    def test_get_update_frequency(self, qapp):
        """Тест получения частоты обновления"""
        widget = WaveformWidget()
        
        frequency = widget.get_update_frequency()
        
        # Должно быть 20 FPS (1000ms / 50ms)
        assert frequency == 20.0
    
    def test_set_update_frequency(self, qapp):
        """Тест установки частоты обновления"""
        widget = WaveformWidget()
        
        widget.set_update_frequency(30.0)
        
        assert widget.update_interval_ms == int(1000.0 / 30.0)
        assert widget.get_update_frequency() == pytest.approx(30.0, rel=0.1)
    
    def test_minimum_update_frequency(self, qapp):
        """Тест минимальной частоты обновления (20 FPS)"""
        widget = WaveformWidget()
        
        widget.set_update_frequency(10.0)  # Меньше минимума
        
        # Должно быть установлено минимум 20 FPS
        assert widget.get_update_frequency() >= 20.0


class TestWaveformWidgetProperties:
    """Property-тесты для WaveformWidget"""
    
    @given(st.lists(st.floats(min_value=0.0, max_value=1.0), min_size=1, max_size=100))
    @settings(max_examples=100)
    def test_property_7_waveform_updates(self, qapp, rms_values: list):
        """
        Property 7: Обновление визуализации волны
        
        Для любого активного процесса записи, визуализатор волны должен
        получать обновления RMS значений с частотой не менее 20 раз в секунду.
        
        **Validates: Requirements 4.1, 4.2**
        """
        widget = WaveformWidget()
        widget.start_recording_animation()
        
        # Проверяем что таймер активен
        assert widget.timer.isActive(), \
            "Таймер должен быть активен во время записи"
        
        # Проверяем частоту обновления
        frequency = widget.get_update_frequency()
        assert frequency >= 20.0, \
            f"Частота обновления должна быть не менее 20 FPS, получено {frequency}"
        
        # Добавляем RMS значения
        for rms in rms_values:
            widget.update_rms(rms)
        
        # Проверяем что значения добавлены
        assert len(widget.rms_values) > 0, \
            "RMS значения должны быть добавлены в визуализатор"
    
    @given(st.floats(min_value=0.0, max_value=1.0), 
           st.floats(min_value=0.0, max_value=1.0))
    @settings(max_examples=100)
    def test_property_9_amplitude_proportionality(self, qapp, rms1: float, rms2: float):
        """
        Property 9: Пропорциональность амплитуды RMS
        
        Для любых двух RMS значений rms1 и rms2, где rms1 > rms2,
        высота визуализации для rms1 должна быть больше высоты для rms2.
        
        **Validates: Requirements 4.4**
        """
        assume(abs(rms1 - rms2) > 0.1)  # Избегаем очень близких значений
        
        widget = WaveformWidget()
        widget.smoothing_factor = 1.0  # Отключаем сглаживание для этого теста
        widget.start_recording_animation()
        
        # Добавляем значения
        widget.update_rms(rms1)
        value1 = widget.rms_values[-1]
        
        widget.update_rms(rms2)
        value2 = widget.rms_values[-1]
        
        # Проверяем что значения в правильном порядке
        if rms1 > rms2:
            assert value1 > value2, \
                f"Большее RMS значение ({rms1}) должно давать большую высоту ({value1}) чем меньшее ({rms2}, {value2})"
        elif rms2 > rms1:
            assert value2 > value1, \
                f"Большее RMS значение ({rms2}) должно давать большую высоту ({value2}) чем меньшее ({rms1}, {value1})"
    
    @given(st.lists(st.floats(min_value=0.0, max_value=1.0), min_size=2, max_size=50))
    @settings(max_examples=100)
    def test_property_10_smoothness(self, qapp, rms_values: list):
        """
        Property 10: Плавность интерполяции
        
        Для любых двух последовательных значений визуализации, разница
        между ними не должна превышать максимальный порог изменения за один кадр.
        
        **Validates: Requirements 4.6**
        """
        widget = WaveformWidget()
        widget.start_recording_animation()
        
        # Добавляем значения
        for rms in rms_values:
            widget.update_rms(rms)
        
        # Проверяем плавность между последовательными значениями
        if len(widget.rms_values) >= 2:
            for i in range(1, len(widget.rms_values)):
                diff = abs(widget.rms_values[i] - widget.rms_values[i-1])
                
                # Разница не должна быть слишком большой благодаря сглаживанию
                # Максимальное изменение за кадр ограничено smoothing_factor
                max_change = widget.smoothing_factor * 1.5
                assert diff <= max_change, \
                    f"Разница между кадрами ({diff}) превышает порог ({max_change})"
    
    @given(st.floats(min_value=20.0, max_value=60.0))
    @settings(max_examples=100)
    def test_property_27_update_frequency(self, qapp, fps: float):
        """
        Property 27: Частота обновления визуализации
        
        Для любого процесса визуализации волны, частота обновления должна
        быть не менее 20 FPS (кадров в секунду).
        
        **Validates: Requirements 9.3**
        """
        widget = WaveformWidget()
        
        # Устанавливаем частоту
        widget.set_update_frequency(fps)
        
        # Проверяем что частота установлена корректно
        actual_fps = widget.get_update_frequency()
        
        # Частота должна быть не менее 20 FPS
        assert actual_fps >= 20.0, \
            f"Частота обновления должна быть не менее 20 FPS, получено {actual_fps}"
        
        # Частота должна быть близка к запрошенной (с учетом округления интервала)
        # Погрешность может быть больше из-за округления миллисекунд
        if fps >= 20.0:
            assert abs(actual_fps - fps) < 5.0, \
                f"Установленная частота ({actual_fps}) должна быть близка к запрошенной ({fps})"


class TestWaveformWidgetAnimationProperties:
    """Property-тесты для анимаций"""
    
    @given(st.integers(min_value=0, max_value=10))
    @settings(max_examples=100)
    def test_property_18_visualization_transformation(self, qapp, num_transitions: int):
        """
        Property 18: Трансформация визуализации
        
        Для любого перехода из состояния RECORDING в PROCESSING,
        визуализатор должен изменить режим отображения с волны на спиннер.
        
        **Validates: Requirements 7.1**
        """
        widget = WaveformWidget()
        
        for _ in range(num_transitions):
            # Симулируем переход RECORDING -> PROCESSING
            widget.start_recording_animation()
            assert widget.animation_state == AnimationState.WAVEFORM, \
                "Во время записи должна быть анимация волны"
            
            widget.start_loading_animation()
            assert widget.animation_state == AnimationState.SPINNER, \
                "Во время обработки должен быть спиннер"
            
            widget.stop_animation()
    
    def test_property_19_spinner_during_api_request(self, qapp):
        """
        Property 19: Отображение индикатора во время API запроса
        
        Для любого активного API запроса, приложение должно отображать
        анимированный индикатор прогресса.
        
        **Validates: Requirements 7.2**
        """
        widget = WaveformWidget()
        
        # Запускаем анимацию загрузки
        widget.start_loading_animation()
        
        assert widget.animation_state == AnimationState.SPINNER, \
            "Во время API запроса должен отображаться спиннер"
        assert widget.timer.isActive(), \
            "Таймер анимации должен быть активен"
    
    def test_property_20_hide_spinner_after_response(self, qapp):
        """
        Property 20: Скрытие индикатора после ответа
        
        Для любого полученного ответа от API, индикатор загрузки
        должен быть скрыт.
        
        **Validates: Requirements 7.5**
        """
        widget = WaveformWidget()
        
        # Запускаем анимацию загрузки
        widget.start_loading_animation()
        assert widget.animation_state == AnimationState.SPINNER
        
        # Останавливаем анимацию (симулируем получение ответа)
        widget.stop_animation()
        
        assert widget.animation_state == AnimationState.IDLE, \
            "После получения ответа индикатор должен быть скрыт"
        assert not widget.timer.isActive(), \
            "Таймер анимации должен быть остановлен"
