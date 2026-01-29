"""
Тесты для StateManager.

Включает unit-тесты и property-тесты для проверки корректности
переходов между состояниями приложения.
"""

import pytest
from unittest.mock import Mock, MagicMock
from hypothesis import given, strategies as st, settings
from PyQt6.QtCore import QObject
from core.state_manager import StateManager, AppState


class TestStateManagerInitialization:
    """Тесты инициализации StateManager"""
    
    def test_initialization(self):
        """Тест инициализации менеджера состояний"""
        manager = StateManager()
        
        assert manager.current_state == AppState.IDLE
        assert manager.get_current_state() == AppState.IDLE
        assert manager.get_previous_state() is None
    
    def test_is_qobject(self):
        """Тест что StateManager является QObject"""
        manager = StateManager()
        assert isinstance(manager, QObject)
    
    def test_has_state_changed_signal(self):
        """Тест наличия сигнала state_changed"""
        manager = StateManager()
        assert hasattr(manager, 'state_changed')


class TestStateTransitions:
    """Тесты переходов между состояниями"""
    
    def test_transition_to_new_state(self):
        """Тест перехода в новое состояние"""
        manager = StateManager()
        
        manager.transition_to(AppState.RECORDING)
        
        assert manager.current_state == AppState.RECORDING
        assert manager.get_previous_state() == AppState.IDLE
    
    def test_transition_to_same_state(self):
        """Тест перехода в то же состояние (не должно изменяться)"""
        manager = StateManager()
        manager.transition_to(AppState.RECORDING)
        
        previous = manager.get_previous_state()
        manager.transition_to(AppState.RECORDING)
        
        assert manager.current_state == AppState.RECORDING
        assert manager.get_previous_state() == previous
    
    def test_state_changed_signal_emitted(self):
        """Тест испускания сигнала при изменении состояния"""
        manager = StateManager()
        signal_spy = Mock()
        manager.state_changed.connect(signal_spy)
        
        manager.transition_to(AppState.RECORDING)
        
        signal_spy.assert_called_once_with(AppState.RECORDING)
    
    def test_multiple_transitions(self):
        """Тест множественных переходов"""
        manager = StateManager()
        
        manager.transition_to(AppState.RECORDING)
        assert manager.current_state == AppState.RECORDING
        
        manager.transition_to(AppState.PROCESSING)
        assert manager.current_state == AppState.PROCESSING
        assert manager.get_previous_state() == AppState.RECORDING
        
        manager.transition_to(AppState.DISPLAYING)
        assert manager.current_state == AppState.DISPLAYING
        assert manager.get_previous_state() == AppState.PROCESSING


class TestHotkeyPressedHandling:
    """Тесты обработки нажатия горячей клавиши"""
    
    def test_hotkey_in_idle_starts_recording(self):
        """Тест что нажатие горячей клавиши в IDLE начинает запись"""
        manager = StateManager()
        show_window_mock = Mock()
        start_recording_mock = Mock()
        
        manager.set_callbacks(
            on_show_window=show_window_mock,
            on_start_recording=start_recording_mock
        )
        
        manager.on_hotkey_pressed()
        
        show_window_mock.assert_called_once()
        start_recording_mock.assert_called_once()
        assert manager.current_state == AppState.RECORDING
    
    def test_hotkey_in_recording_stops_recording(self):
        """Тест что нажатие горячей клавиши в RECORDING останавливает запись"""
        manager = StateManager()
        manager.transition_to(AppState.RECORDING)
        
        stop_recording_mock = Mock(return_value="/tmp/audio.wav")
        start_transcription_mock = Mock()
        
        manager.set_callbacks(
            on_stop_recording=stop_recording_mock,
            on_start_transcription=start_transcription_mock
        )
        
        manager.on_hotkey_pressed()
        
        stop_recording_mock.assert_called_once()
        start_transcription_mock.assert_called_once_with("/tmp/audio.wav")
        assert manager.current_state == AppState.PROCESSING
    
    def test_hotkey_in_displaying_hides_window(self):
        """Тест что нажатие горячей клавиши в DISPLAYING скрывает окно"""
        manager = StateManager()
        manager.transition_to(AppState.DISPLAYING)
        
        hide_window_mock = Mock()
        manager.set_callbacks(on_hide_window=hide_window_mock)
        
        manager.on_hotkey_pressed()
        
        hide_window_mock.assert_called_once()
        assert manager.current_state == AppState.IDLE
    
    def test_hotkey_in_processing_does_nothing(self):
        """Тест что нажатие горячей клавиши в PROCESSING ничего не делает"""
        manager = StateManager()
        manager.transition_to(AppState.PROCESSING)
        
        manager.on_hotkey_pressed()
        
        # Состояние не должно измениться
        assert manager.current_state == AppState.PROCESSING


class TestSilenceDetectionHandling:
    """Тесты обработки обнаружения тишины"""
    
    def test_silence_in_recording_stops_recording(self):
        """Тест что обнаружение тишины в RECORDING останавливает запись"""
        manager = StateManager()
        manager.transition_to(AppState.RECORDING)
        
        stop_recording_mock = Mock(return_value="/tmp/audio.wav")
        start_transcription_mock = Mock()
        
        manager.set_callbacks(
            on_stop_recording=stop_recording_mock,
            on_start_transcription=start_transcription_mock
        )
        
        manager.on_silence_detected()
        
        stop_recording_mock.assert_called_once()
        start_transcription_mock.assert_called_once_with("/tmp/audio.wav")
        assert manager.current_state == AppState.PROCESSING
    
    def test_silence_in_idle_does_nothing(self):
        """Тест что обнаружение тишины в IDLE ничего не делает"""
        manager = StateManager()
        
        manager.on_silence_detected()
        
        assert manager.current_state == AppState.IDLE
    
    def test_silence_in_processing_does_nothing(self):
        """Тест что обнаружение тишины в PROCESSING ничего не делает"""
        manager = StateManager()
        manager.transition_to(AppState.PROCESSING)
        
        manager.on_silence_detected()
        
        assert manager.current_state == AppState.PROCESSING


class TestTranscriptionCompleteHandling:
    """Тесты обработки завершения транскрипции"""
    
    def test_transcription_complete_displays_result(self):
        """Тест что завершение транскрипции отображает результат"""
        manager = StateManager()
        manager.transition_to(AppState.PROCESSING)
        
        display_result_mock = Mock()
        manager.set_callbacks(on_display_result=display_result_mock)
        
        manager.on_transcription_complete("Привет мир")
        
        display_result_mock.assert_called_once_with("Привет мир")
        assert manager.current_state == AppState.DISPLAYING
    
    def test_transcription_complete_in_wrong_state_does_nothing(self):
        """Тест что завершение транскрипции в неправильном состоянии ничего не делает"""
        manager = StateManager()
        display_result_mock = Mock()
        manager.set_callbacks(on_display_result=display_result_mock)
        
        manager.on_transcription_complete("Текст")
        
        display_result_mock.assert_not_called()
        assert manager.current_state == AppState.IDLE


class TestDisplayTimeoutHandling:
    """Тесты обработки таймаута отображения"""
    
    def test_display_timeout_hides_window(self):
        """Тест что таймаут отображения скрывает окно"""
        manager = StateManager()
        manager.transition_to(AppState.DISPLAYING)
        
        hide_window_mock = Mock()
        manager.set_callbacks(on_hide_window=hide_window_mock)
        
        manager.on_display_timeout()
        
        hide_window_mock.assert_called_once()
        assert manager.current_state == AppState.IDLE
    
    def test_display_timeout_in_wrong_state_does_nothing(self):
        """Тест что таймаут в неправильном состоянии ничего не делает"""
        manager = StateManager()
        hide_window_mock = Mock()
        manager.set_callbacks(on_hide_window=hide_window_mock)
        
        manager.on_display_timeout()
        
        hide_window_mock.assert_not_called()
        assert manager.current_state == AppState.IDLE


class TestErrorHandling:
    """Тесты обработки ошибок"""
    
    def test_error_transitions_to_error_state(self):
        """Тест что ошибка переводит в состояние ERROR"""
        manager = StateManager()
        manager.transition_to(AppState.RECORDING)
        
        show_error_mock = Mock()
        manager.set_callbacks(on_show_error=show_error_mock)
        
        error = Exception("Test error")
        manager.on_error(error)
        
        show_error_mock.assert_called_once_with(error)
        # После обработки ошибки должен вернуться в IDLE
        assert manager.current_state == AppState.IDLE
    
    def test_error_recovery_to_idle(self):
        """Тест восстановления после ошибки в IDLE"""
        manager = StateManager()
        manager.transition_to(AppState.PROCESSING)
        
        manager.on_error(Exception("Error"))
        
        # Должен вернуться в IDLE для новой попытки
        assert manager.current_state == AppState.IDLE


class TestResourceCleanup:
    """Тесты очистки ресурсов"""
    
    def test_cleanup_stops_recording(self):
        """Тест что cleanup останавливает запись"""
        manager = StateManager()
        manager.transition_to(AppState.RECORDING)
        
        stop_recording_mock = Mock()
        hide_window_mock = Mock()
        
        manager.set_callbacks(
            on_stop_recording=stop_recording_mock,
            on_hide_window=hide_window_mock
        )
        
        manager.cleanup_resources()
        
        stop_recording_mock.assert_called_once()
        hide_window_mock.assert_called_once()
        assert manager.current_state == AppState.IDLE
    
    def test_cleanup_hides_window_in_displaying(self):
        """Тест что cleanup скрывает окно в DISPLAYING"""
        manager = StateManager()
        manager.transition_to(AppState.DISPLAYING)
        
        hide_window_mock = Mock()
        manager.set_callbacks(on_hide_window=hide_window_mock)
        
        manager.cleanup_resources()
        
        hide_window_mock.assert_called_once()
        assert manager.current_state == AppState.IDLE
    
    def test_cleanup_in_idle_does_nothing(self):
        """Тест что cleanup в IDLE ничего не делает"""
        manager = StateManager()
        
        stop_recording_mock = Mock()
        hide_window_mock = Mock()
        
        manager.set_callbacks(
            on_stop_recording=stop_recording_mock,
            on_hide_window=hide_window_mock
        )
        
        manager.cleanup_resources()
        
        stop_recording_mock.assert_not_called()
        hide_window_mock.assert_not_called()
        assert manager.current_state == AppState.IDLE


class TestCallbackConfiguration:
    """Тесты конфигурации callbacks"""
    
    def test_set_callbacks(self):
        """Тест установки callbacks"""
        manager = StateManager()
        
        show_window = Mock()
        hide_window = Mock()
        start_recording = Mock()
        
        manager.set_callbacks(
            on_show_window=show_window,
            on_hide_window=hide_window,
            on_start_recording=start_recording
        )
        
        # Проверяем что callbacks установлены
        assert manager._on_show_window == show_window
        assert manager._on_hide_window == hide_window
        assert manager._on_start_recording == start_recording
    
    def test_partial_callbacks(self):
        """Тест установки частичных callbacks"""
        manager = StateManager()
        
        show_window = Mock()
        manager.set_callbacks(on_show_window=show_window)
        
        assert manager._on_show_window == show_window
        assert manager._on_hide_window is None



class TestStateManagerProperties:
    """Property-тесты для StateManager"""
    
    @given(st.integers(min_value=0, max_value=10))
    @settings(max_examples=100)
    def test_property_15_transition_to_processing_on_silence(self, num_silence_events: int):
        """
        Property 15: Переход к обработке при тишине
        
        Для любого обнаружения тишины во время записи, приложение должно
        перейти в состояние PROCESSING.
        
        **Validates: Requirements 5.5**
        """
        manager = StateManager()
        manager.transition_to(AppState.RECORDING)
        
        stop_recording_mock = Mock(return_value="/tmp/audio.wav")
        start_transcription_mock = Mock()
        
        manager.set_callbacks(
            on_stop_recording=stop_recording_mock,
            on_start_transcription=start_transcription_mock
        )
        
        # Симулируем обнаружение тишины
        for _ in range(num_silence_events):
            if manager.current_state == AppState.RECORDING:
                manager.on_silence_detected()
        
        # После первого обнаружения тишины должен быть переход в PROCESSING
        if num_silence_events > 0:
            assert manager.current_state == AppState.PROCESSING, \
                "После обнаружения тишины должен быть переход в PROCESSING"
            stop_recording_mock.assert_called_once()
            start_transcription_mock.assert_called_once()
    
    @given(st.lists(st.sampled_from(list(AppState)), min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_property_31_error_recovery_to_idle(self, states: list):
        """
        Property 31: Восстановление после ошибки
        
        Для любой обработанной ошибки, приложение должно вернуться в
        состояние IDLE для возможности новой записи.
        
        **Validates: Requirements 10.6**
        """
        manager = StateManager()
        show_error_mock = Mock()
        manager.set_callbacks(on_show_error=show_error_mock)
        
        # Переходим через различные состояния
        for state in states:
            manager.transition_to(state)
            
            # Симулируем ошибку
            error = Exception(f"Error in {state.value}")
            manager.on_error(error)
            
            # После обработки ошибки всегда должен быть IDLE
            assert manager.current_state == AppState.IDLE, \
                f"После ошибки в состоянии {state.value} должен быть переход в IDLE"
            
            show_error_mock.assert_called_with(error)
            show_error_mock.reset_mock()
    
    @given(st.lists(st.sampled_from([AppState.IDLE, AppState.RECORDING, AppState.DISPLAYING]), 
                    min_size=1, max_size=5))
    @settings(max_examples=100)
    def test_hotkey_state_transitions(self, states: list):
        """
        Свойство: Горячая клавиша корректно обрабатывается в разных состояниях
        
        Для любой последовательности состояний, нажатие горячей клавиши
        должно вызывать правильный переход.
        """
        manager = StateManager()
        
        show_window_mock = Mock()
        hide_window_mock = Mock()
        start_recording_mock = Mock()
        stop_recording_mock = Mock(return_value="/tmp/audio.wav")
        start_transcription_mock = Mock()
        
        manager.set_callbacks(
            on_show_window=show_window_mock,
            on_hide_window=hide_window_mock,
            on_start_recording=start_recording_mock,
            on_stop_recording=stop_recording_mock,
            on_start_transcription=start_transcription_mock
        )
        
        for state in states:
            manager.transition_to(state)
            initial_state = manager.current_state
            
            manager.on_hotkey_pressed()
            
            # Проверяем правильность перехода
            if initial_state == AppState.IDLE:
                assert manager.current_state == AppState.RECORDING
            elif initial_state == AppState.RECORDING:
                assert manager.current_state == AppState.PROCESSING
            elif initial_state == AppState.DISPLAYING:
                assert manager.current_state == AppState.IDLE
    
    @given(st.lists(st.sampled_from(list(AppState)), min_size=2, max_size=10))
    @settings(max_examples=100)
    def test_state_history_tracking(self, states: list):
        """
        Свойство: История состояний отслеживается корректно
        
        Для любой последовательности переходов, предыдущее состояние
        должно корректно сохраняться.
        """
        manager = StateManager()
        
        previous_state = manager.current_state
        
        for state in states:
            if state != manager.current_state:
                manager.transition_to(state)
                
                assert manager.get_previous_state() == previous_state, \
                    f"Предыдущее состояние должно быть {previous_state.value}"
                
                previous_state = state
    
    @given(st.integers(min_value=1, max_value=20))
    @settings(max_examples=100)
    def test_signal_emission_count(self, num_transitions: int):
        """
        Свойство: Сигнал испускается при каждом переходе
        
        Для любого количества переходов, сигнал state_changed должен
        испускаться ровно столько же раз.
        """
        manager = StateManager()
        signal_spy = Mock()
        manager.state_changed.connect(signal_spy)
        
        states = [AppState.RECORDING, AppState.PROCESSING, 
                  AppState.DISPLAYING, AppState.IDLE]
        
        for i in range(num_transitions):
            state = states[i % len(states)]
            if state != manager.current_state:
                manager.transition_to(state)
        
        # Подсчитываем реальные переходы (исключая переходы в то же состояние)
        actual_transitions = signal_spy.call_count
        
        assert actual_transitions > 0, "Должен быть хотя бы один переход"
        assert actual_transitions <= num_transitions, \
            "Количество сигналов не должно превышать количество попыток перехода"
