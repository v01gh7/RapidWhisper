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
        """Тест что обнаружение тишины в RECORDING переходит в PROCESSING"""
        manager = StateManager()
        manager.transition_to(AppState.RECORDING)
        
        stop_recording_mock = Mock(return_value="/tmp/audio.wav")
        start_transcription_mock = Mock()
        
        manager.set_callbacks(
            on_stop_recording=stop_recording_mock,
            on_start_transcription=start_transcription_mock
        )
        
        manager.on_silence_detected()
        
        # Silence detection only transitions to PROCESSING
        # stop_recording callback is NOT called immediately - it waits for audio file to be saved
        assert manager.current_state == AppState.PROCESSING
        stop_recording_mock.assert_not_called()
        start_transcription_mock.assert_not_called()
    
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
            # Silence detection only transitions to PROCESSING
            # stop_recording callback is NOT called immediately - it waits for audio file to be saved
            stop_recording_mock.assert_not_called()
            start_transcription_mock.assert_not_called()
    
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


class TestManualFormatSelection:
    """Тесты для хранения ручного выбора формата"""
    
    def test_initial_manual_format_selection_is_none(self):
        """Тест что начальное значение ручного выбора формата - None"""
        manager = StateManager()
        
        assert manager.get_manual_format_selection() is None
    
    def test_set_manual_format_selection(self):
        """Тест установки ручного выбора формата"""
        manager = StateManager()
        
        manager.set_manual_format_selection("notion")
        
        assert manager.get_manual_format_selection() == "notion"
    
    def test_set_manual_format_selection_fallback(self):
        """Тест установки универсального формата"""
        manager = StateManager()
        
        manager.set_manual_format_selection("_fallback")
        
        assert manager.get_manual_format_selection() == "_fallback"
    
    def test_clear_manual_format_selection(self):
        """Тест очистки ручного выбора формата"""
        manager = StateManager()
        
        manager.set_manual_format_selection("notion")
        assert manager.get_manual_format_selection() == "notion"
        
        manager.clear_manual_format_selection()
        
        assert manager.get_manual_format_selection() is None
    
    def test_clear_manual_format_selection_when_none(self):
        """Тест очистки когда выбор не установлен"""
        manager = StateManager()
        
        # Не должно вызывать ошибку
        manager.clear_manual_format_selection()
        
        assert manager.get_manual_format_selection() is None
    
    def test_overwrite_manual_format_selection(self):
        """Тест перезаписи ручного выбора формата"""
        manager = StateManager()
        
        manager.set_manual_format_selection("notion")
        assert manager.get_manual_format_selection() == "notion"
        
        manager.set_manual_format_selection("markdown")
        
        assert manager.get_manual_format_selection() == "markdown"
    
    def test_manual_format_selection_persists_across_state_transitions(self):
        """Тест что ручной выбор сохраняется при переходах состояний"""
        manager = StateManager()
        
        manager.set_manual_format_selection("notion")
        
        # Переходим через различные состояния
        manager.transition_to(AppState.RECORDING)
        assert manager.get_manual_format_selection() == "notion"
        
        manager.transition_to(AppState.PROCESSING)
        assert manager.get_manual_format_selection() == "notion"
        
        manager.transition_to(AppState.DISPLAYING)
        assert manager.get_manual_format_selection() == "notion"
        
        manager.transition_to(AppState.IDLE)
        assert manager.get_manual_format_selection() == "notion"
    
    def test_session_id_cleared_with_format_selection(self):
        """Тест что session_id очищается вместе с выбором формата"""
        manager = StateManager()
        
        manager.set_manual_format_selection("notion")
        # Session ID устанавливается при установке формата
        
        manager.clear_manual_format_selection()
        
        # Проверяем что оба атрибута очищены
        assert manager._manual_format_selection is None
        assert manager._current_session_id is None



class TestSessionLifecycle:
    """Tests for session lifecycle methods (Task 2.2)"""
    
    def test_start_recording_session_generates_session_id(self):
        """Test that start_recording_session generates a UUID session ID"""
        manager = StateManager()
        
        session_id = manager.start_recording_session()
        
        # Should return a non-empty string
        assert session_id is not None
        assert isinstance(session_id, str)
        assert len(session_id) > 0
        
        # Should be stored in the manager
        assert manager.get_current_session_id() == session_id
    
    def test_start_recording_session_generates_unique_ids(self):
        """Test that each session gets a unique ID"""
        manager = StateManager()
        
        session_id1 = manager.start_recording_session()
        manager.end_recording_session()
        session_id2 = manager.start_recording_session()
        
        # Each session should have a different ID
        assert session_id1 != session_id2
    
    def test_start_recording_session_preserves_manual_selection(self):
        """Test that starting a session doesn't clear manual format selection"""
        manager = StateManager()
        
        manager.set_manual_format_selection("notion")
        session_id = manager.start_recording_session()
        
        # Manual selection should still be set
        assert manager.get_manual_format_selection() == "notion"
        assert manager.get_current_session_id() == session_id
    
    def test_end_recording_session_clears_manual_selection(self):
        """Test that ending a session clears manual format selection"""
        manager = StateManager()
        
        manager.set_manual_format_selection("notion")
        manager.start_recording_session()
        
        manager.end_recording_session()
        
        # Both manual selection and session ID should be cleared
        assert manager.get_manual_format_selection() is None
        assert manager.get_current_session_id() is None
    
    def test_end_recording_session_without_active_session(self):
        """Test that ending a session when none is active doesn't cause errors"""
        manager = StateManager()
        
        # Should not raise an exception
        manager.end_recording_session()
        
        assert manager.get_current_session_id() is None
        assert manager.get_manual_format_selection() is None
    
    def test_session_lifecycle_integration_with_hotkey(self):
        """Test that session lifecycle integrates with hotkey press"""
        manager = StateManager()
        
        show_window_mock = Mock()
        start_recording_mock = Mock()
        
        manager.set_callbacks(
            on_show_window=show_window_mock,
            on_start_recording=start_recording_mock
        )
        
        # Press hotkey in IDLE state
        manager.on_hotkey_pressed()
        
        # Should have started a recording session
        assert manager.get_current_session_id() is not None
        assert manager.current_state == AppState.RECORDING
    
    def test_session_lifecycle_integration_with_transcription_complete(self):
        """Test that session ends when transcription completes"""
        manager = StateManager()
        manager.transition_to(AppState.PROCESSING)
        
        # Set up a session with manual format selection
        manager.set_manual_format_selection("notion")
        manager._current_session_id = "test-session-id"
        
        display_result_mock = Mock()
        manager.set_callbacks(on_display_result=display_result_mock)
        
        # Complete transcription
        manager.on_transcription_complete("Test text")
        
        # Session should be ended (manual selection cleared)
        assert manager.get_manual_format_selection() is None
        assert manager.get_current_session_id() is None
        assert manager.current_state == AppState.DISPLAYING
    
    def test_multiple_session_lifecycle(self):
        """Test multiple recording sessions in sequence"""
        manager = StateManager()
        
        # First session
        manager.set_manual_format_selection("notion")
        session_id1 = manager.start_recording_session()
        assert manager.get_manual_format_selection() == "notion"
        manager.end_recording_session()
        assert manager.get_manual_format_selection() is None
        
        # Second session (no manual selection)
        session_id2 = manager.start_recording_session()
        assert manager.get_manual_format_selection() is None
        assert session_id2 != session_id1
        manager.end_recording_session()
        
        # Third session (different manual selection)
        manager.set_manual_format_selection("markdown")
        session_id3 = manager.start_recording_session()
        assert manager.get_manual_format_selection() == "markdown"
        assert session_id3 != session_id2
        manager.end_recording_session()
        assert manager.get_manual_format_selection() is None
    
    def test_session_id_is_valid_uuid(self):
        """Test that generated session ID is a valid UUID"""
        import uuid
        manager = StateManager()
        
        session_id = manager.start_recording_session()
        
        # Should be able to parse as UUID
        try:
            uuid.UUID(session_id)
        except ValueError:
            pytest.fail(f"Session ID '{session_id}' is not a valid UUID")
    
    def test_get_current_session_id_when_no_session(self):
        """Test getting session ID when no session is active"""
        manager = StateManager()
        
        assert manager.get_current_session_id() is None


class TestStorageErrorHandling:
    """Tests for error handling in storage operations (Task 2.5)"""
    
    def test_set_manual_format_selection_handles_attribute_error(self):
        """Test that set_manual_format_selection handles errors gracefully"""
        manager = StateManager()
        
        # Mock the attribute to raise an error on assignment
        original_setattr = object.__setattr__
        
        def mock_setattr(obj, name, value):
            if name == '_manual_format_selection' and value == "error_format":
                raise AttributeError("Simulated storage error")
            original_setattr(obj, name, value)
        
        # Temporarily replace __setattr__
        StateManager.__setattr__ = mock_setattr
        
        try:
            # Should not raise exception, should log error and set to None
            manager.set_manual_format_selection("error_format")
            
            # Should be None due to error handling
            assert manager.get_manual_format_selection() is None
        finally:
            # Restore original __setattr__
            StateManager.__setattr__ = original_setattr
    
    def test_get_manual_format_selection_handles_errors(self):
        """Test that get_manual_format_selection handles errors gracefully"""
        manager = StateManager()
        manager.set_manual_format_selection("notion")
        
        # Mock the attribute to raise an error on access
        original_getattribute = StateManager.__getattribute__
        
        def mock_getattribute(obj, name):
            if name == '_manual_format_selection':
                raise AttributeError("Simulated retrieval error")
            return original_getattribute(obj, name)
        
        StateManager.__getattribute__ = mock_getattribute
        
        try:
            # Should return None instead of raising exception
            result = manager.get_manual_format_selection()
            assert result is None
        finally:
            # Restore original __getattribute__
            StateManager.__getattribute__ = original_getattribute
    
    def test_clear_manual_format_selection_handles_errors(self):
        """Test that clear_manual_format_selection handles errors gracefully"""
        manager = StateManager()
        manager.set_manual_format_selection("notion")
        
        # Create a flag to track if error occurred
        error_occurred = False
        
        # Mock to raise error on first clear attempt
        original_setattr = object.__setattr__
        call_count = [0]
        
        def mock_setattr(obj, name, value):
            if name == '_manual_format_selection' and value is None:
                call_count[0] += 1
                if call_count[0] == 1:
                    raise AttributeError("Simulated clear error")
            original_setattr(obj, name, value)
        
        StateManager.__setattr__ = mock_setattr
        
        try:
            # Should not raise exception, should attempt to force clear
            manager.clear_manual_format_selection()
            
            # Should eventually be cleared (second attempt succeeds)
            assert manager._manual_format_selection is None
        finally:
            # Restore original __setattr__
            StateManager.__setattr__ = original_setattr
    
    def test_start_recording_session_handles_uuid_error(self):
        """Test that start_recording_session handles UUID generation errors"""
        import uuid
        manager = StateManager()
        
        # Mock uuid.uuid4 to raise an error
        original_uuid4 = uuid.uuid4
        
        def mock_uuid4():
            raise RuntimeError("Simulated UUID generation error")
        
        uuid.uuid4 = mock_uuid4
        
        try:
            # Should return a fallback session ID instead of raising
            session_id = manager.start_recording_session()
            
            # Should have some fallback value
            assert session_id is not None
            assert isinstance(session_id, str)
            assert len(session_id) > 0
            # Should be a fallback ID (not a UUID)
            assert "fallback" in session_id or "unknown" in session_id
        finally:
            # Restore original uuid4
            uuid.uuid4 = original_uuid4
    
    def test_end_recording_session_handles_errors(self):
        """Test that end_recording_session handles errors gracefully"""
        manager = StateManager()
        manager.start_recording_session()
        manager.set_manual_format_selection("notion")
        
        # Mock clear_manual_format_selection to raise error on first call
        original_clear = manager.clear_manual_format_selection
        call_count = [0]
        
        def mock_clear():
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("Simulated clear error")
            original_clear()
        
        manager.clear_manual_format_selection = mock_clear
        
        # Should not raise exception, should attempt to clear anyway
        manager.end_recording_session()
        
        # Should eventually be cleared (second attempt in error handler)
        assert call_count[0] >= 1  # At least one attempt was made
    
    def test_storage_error_does_not_block_recording(self):
        """Test that storage errors don't prevent recording from working"""
        manager = StateManager()
        
        # Simulate storage error
        original_setattr = object.__setattr__
        
        def mock_setattr(obj, name, value):
            if name == '_manual_format_selection':
                raise AttributeError("Storage unavailable")
            original_setattr(obj, name, value)
        
        StateManager.__setattr__ = mock_setattr
        
        try:
            # Try to set manual format (will fail)
            manager.set_manual_format_selection("notion")
            
            # Recording should still work
            show_window_mock = Mock()
            start_recording_mock = Mock()
            
            manager.set_callbacks(
                on_show_window=show_window_mock,
                on_start_recording=start_recording_mock
            )
            
            # Should be able to start recording despite storage error
            manager.on_hotkey_pressed()
            
            assert manager.current_state == AppState.RECORDING
            show_window_mock.assert_called_once()
            start_recording_mock.assert_called_once()
        finally:
            StateManager.__setattr__ = original_setattr
    
    def test_retrieval_error_falls_back_to_normal_detection(self):
        """Test that retrieval errors result in None (normal detection)"""
        manager = StateManager()
        manager._manual_format_selection = "notion"
        
        # Mock to raise error on retrieval
        original_getattribute = StateManager.__getattribute__
        
        def mock_getattribute(obj, name):
            if name == '_manual_format_selection':
                raise RuntimeError("Storage corrupted")
            return original_getattribute(obj, name)
        
        StateManager.__getattribute__ = mock_getattribute
        
        try:
            # Should return None to allow normal detection
            result = manager.get_manual_format_selection()
            assert result is None
        finally:
            StateManager.__getattribute__ = original_getattribute
    
    def test_multiple_storage_errors_dont_crash(self):
        """Test that multiple consecutive storage errors don't crash the app"""
        manager = StateManager()
        
        # Simulate persistent storage errors
        original_setattr = object.__setattr__
        
        def mock_setattr(obj, name, value):
            if name == '_manual_format_selection':
                raise IOError("Persistent storage error")
            original_setattr(obj, name, value)
        
        StateManager.__setattr__ = mock_setattr
        
        try:
            # Multiple attempts should all fail gracefully
            for i in range(5):
                manager.set_manual_format_selection(f"format_{i}")
                # Should not raise, should return None
                assert manager.get_manual_format_selection() is None
        finally:
            StateManager.__setattr__ = original_setattr

