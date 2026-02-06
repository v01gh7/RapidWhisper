"""
Менеджер состояний приложения RapidWhisper.

Координирует переходы между состояниями приложения и управляет
взаимодействием между компонентами.
"""

import uuid
from enum import Enum
from typing import Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal
from utils.logger import get_logger

logger = get_logger()


class AppState(Enum):
    """
    Состояния приложения.
    
    IDLE: Приложение ожидает активации
    RECORDING: Идет запись аудио
    PROCESSING: Обработка аудио через API
    DISPLAYING: Отображение результата
    ERROR: Состояние ошибки
    """
    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"
    DISPLAYING = "displaying"
    ERROR = "error"


class StateManager(QObject):
    """
    Менеджер состояний приложения.
    
    Координирует переходы между состояниями и управляет жизненным циклом
    приложения. Использует PyQt сигналы для уведомления компонентов о
    изменениях состояния.
    
    Requirements: 1.2, 1.3, 5.5, 10.6
    """
    
    # PyQt сигналы
    state_changed = pyqtSignal(AppState)
    
    def __init__(self):
        """Инициализирует менеджер состояний."""
        super().__init__()
        self.current_state: AppState = AppState.IDLE
        self._previous_state: Optional[AppState] = None
        
        # Manual format selection storage (Requirements 3.1, 8.1, 8.3)
        self._manual_format_selection: Optional[str] = None
        self._current_session_id: Optional[str] = None
        
        # Callbacks для действий при переходах состояний
        self._on_show_window: Optional[Callable] = None
        self._on_hide_window: Optional[Callable] = None
        self._on_start_recording: Optional[Callable] = None
        self._on_stop_recording: Optional[Callable] = None
        self._on_start_transcription: Optional[Callable] = None
        self._on_display_result: Optional[Callable] = None
        self._on_show_error: Optional[Callable] = None
        
        logger.info("StateManager инициализирован")
    
    def set_callbacks(
        self,
        on_show_window: Optional[Callable] = None,
        on_hide_window: Optional[Callable] = None,
        on_start_recording: Optional[Callable] = None,
        on_stop_recording: Optional[Callable] = None,
        on_start_transcription: Optional[Callable] = None,
        on_display_result: Optional[Callable] = None,
        on_show_error: Optional[Callable] = None
    ):
        """
        Устанавливает callbacks для действий при переходах состояний.
        
        Args:
            on_show_window: Callback для показа окна
            on_hide_window: Callback для скрытия окна
            on_start_recording: Callback для начала записи
            on_stop_recording: Callback для остановки записи
            on_start_transcription: Callback для начала транскрипции
            on_display_result: Callback для отображения результата
            on_show_error: Callback для показа ошибки
        """
        self._on_show_window = on_show_window
        self._on_hide_window = on_hide_window
        self._on_start_recording = on_start_recording
        self._on_stop_recording = on_stop_recording
        self._on_start_transcription = on_start_transcription
        self._on_display_result = on_display_result
        self._on_show_error = on_show_error
    
    def transition_to(self, new_state: AppState) -> None:
        """
        Переходит в новое состояние.
        
        Args:
            new_state: Новое состояние для перехода
        
        Requirements: 1.2, 1.3
        """
        if new_state == self.current_state:
            logger.debug(f"Уже в состоянии {new_state.value}")
            return
        
        self._previous_state = self.current_state
        old_state = self.current_state
        self.current_state = new_state
        
        logger.log_state_transition(old_state.value, new_state.value)
        
        # Испускаем сигнал об изменении состояния
        self.state_changed.emit(new_state)
    
    def on_hotkey_pressed(self) -> None:
        """
        Обрабатывает нажатие горячей клавиши.
        
        Логика зависит от текущего состояния:
        - IDLE: Показать окно и начать запись
        - RECORDING: Остановить запись и начать обработку
        - DISPLAYING: Скрыть окно и вернуться в IDLE
        
        Requirements: 1.2, 1.3
        """
        logger.info(f"Горячая клавиша нажата в состоянии {self.current_state.value}")
        
        if self.current_state == AppState.IDLE:
            # IDLE → RECORDING
            # Start a new recording session
            self.start_recording_session()
            try:
                from services.hooks_manager import get_hook_manager, build_hook_options
                options = build_hook_options(
                    "before_recording",
                    session_id=self._current_session_id,
                    data={}
                )
                get_hook_manager().run_event("before_recording", options)
            except Exception as e:
                logger.error(f"Hook before_recording failed: {e}")
            if self._on_show_window:
                self._on_show_window()
            if self._on_start_recording:
                self._on_start_recording()
            self.transition_to(AppState.RECORDING)
            
        elif self.current_state == AppState.RECORDING:
            # RECORDING → PROCESSING
            if self._on_stop_recording:
                audio_path = self._on_stop_recording()
                if audio_path and self._on_start_transcription:
                    self._on_start_transcription(audio_path)
            self.transition_to(AppState.PROCESSING)
            
        elif self.current_state == AppState.DISPLAYING:
            # DISPLAYING → IDLE
            if self._on_hide_window:
                self._on_hide_window()
            self.transition_to(AppState.IDLE)
    
    def on_silence_detected(self) -> None:
        """
        Обрабатывает обнаружение тишины.
        
        Если в состоянии RECORDING, останавливает запись и переходит в PROCESSING.
        
        Requirements: 5.5
        """
        logger.info(f"Тишина обнаружена в состоянии {self.current_state.value}")
        
        if self.current_state == AppState.RECORDING:
            # RECORDING → PROCESSING
            logger.info("Переход RECORDING → PROCESSING")
            self.transition_to(AppState.PROCESSING)
            
            # НЕ вызываем callback сразу - ждем сохранения файла
            # Callback будет вызван из _on_recording_stopped
            logger.info("Ожидание сохранения аудио файла...")
        else:
            logger.warning(f"Тишина обнаружена в неправильном состоянии: {self.current_state.value}")
    
    def on_transcription_complete(self, text: str) -> None:
        """
        Обрабатывает завершение транскрипции.
        
        Переходит в состояние DISPLAYING и отображает результат.
        Ends the recording session and clears manual format selection.
        
        Args:
            text: Транскрибированный текст
        
        Requirements: 8.1, 8.2, 4.4
        """
        logger.info(f"Транскрипция завершена в состоянии {self.current_state.value}")
        
        if self.current_state == AppState.PROCESSING:
            session_id = self._current_session_id
            # End the recording session (clears manual format selection)
            self.end_recording_session()
            
            # PROCESSING → DISPLAYING
            if self._on_display_result:
                try:
                    from services.hooks_manager import get_hook_manager, build_hook_options
                    options = build_hook_options(
                        "task_completed",
                        session_id=session_id,
                        data={"text": text}
                    )
                    options = get_hook_manager().run_event("task_completed", options)
                    text = options.get("data", {}).get("text", text)
                except Exception as e:
                    logger.error(f"Hook task_completed failed: {e}")
                self._on_display_result(text)
            self.transition_to(AppState.DISPLAYING)
    
    def on_display_timeout(self) -> None:
        """
        Обрабатывает таймаут отображения результата.
        
        Скрывает окно и возвращается в IDLE.
        
        Requirements: 8.6
        """
        logger.info(f"Таймаут отображения в состоянии {self.current_state.value}")
        
        if self.current_state == AppState.DISPLAYING:
            # DISPLAYING → IDLE
            if self._on_hide_window:
                self._on_hide_window()
            self.transition_to(AppState.IDLE)
    
    def on_error(self, error: Exception) -> None:
        """
        Обрабатывает ошибки.
        
        Переходит в состояние ERROR, показывает ошибку и возвращается в IDLE.
        
        Args:
            error: Исключение, которое произошло
        
        Requirements: 10.6
        """
        logger.error(f"Ошибка в состоянии {self.current_state.value}: {error}")
        
        # Переход в ERROR
        self.transition_to(AppState.ERROR)
        
        # Показать ошибку пользователю
        if self._on_show_error:
            self._on_show_error(error)
        
        # Вернуться в IDLE для возможности новой попытки
        self.transition_to(AppState.IDLE)
    
    def cleanup_resources(self) -> None:
        """
        Освобождает ресурсы при завершении работы.
        
        Останавливает запись, закрывает окна и очищает состояние.
        
        Requirements: 12.2, 12.3, 12.4
        """
        logger.info("Очистка ресурсов StateManager")
        
        # Остановить запись если она активна
        if self.current_state == AppState.RECORDING:
            if self._on_stop_recording:
                self._on_stop_recording()
        
        # Скрыть окно если оно открыто
        if self.current_state in [AppState.RECORDING, AppState.PROCESSING, 
                                   AppState.DISPLAYING, AppState.ERROR]:
            if self._on_hide_window:
                self._on_hide_window()
        
        # Вернуться в IDLE
        self.transition_to(AppState.IDLE)
    
    def get_current_state(self) -> AppState:
        """
        Возвращает текущее состояние приложения.
        
        Returns:
            Текущее состояние
        """
        return self.current_state
    
    def get_previous_state(self) -> Optional[AppState]:
        """
        Возвращает предыдущее состояние приложения.
        
        Returns:
            Предыдущее состояние или None
        """
        return self._previous_state
    
    def set_manual_format_selection(self, format_id: str) -> None:
        """
        Store manual format selection for current session.
        
        Args:
            format_id: Format identifier (e.g., "notion", "_fallback")
        
        Requirements: 3.1, 8.1, 10.3
        """
        try:
            self._manual_format_selection = format_id
            logger.info(f"Manual format selection set: {format_id}")
        except Exception as e:
            logger.error(f"Failed to store manual format selection: {e}")
            # Try to set to None using object.__setattr__ to bypass potential issues
            try:
                object.__setattr__(self, '_manual_format_selection', None)
            except:
                pass  # Continue with normal detection even if we can't clear
    
    def get_manual_format_selection(self) -> Optional[str]:
        """
        Get manual format selection for current session.
        
        Returns:
            Format identifier or None if not set
        
        Requirements: 8.3, 10.3
        """
        try:
            return self._manual_format_selection
        except Exception as e:
            logger.error(f"Failed to retrieve manual format selection: {e}")
            return None  # Continue with normal detection
    
    def clear_manual_format_selection(self) -> None:
        """
        Clear manual format selection.
        
        Called when recording session completes.
        
        Requirements: 8.1, 8.3, 10.3
        """
        try:
            if self._manual_format_selection:
                logger.info(f"Clearing manual format selection: {self._manual_format_selection}")
            self._manual_format_selection = None
            self._current_session_id = None
        except Exception as e:
            logger.error(f"Failed to clear manual format selection: {e}")
            # Attempt to force clear even if logging fails
            try:
                self._manual_format_selection = None
                self._current_session_id = None
            except:
                pass  # Continue operation even if clearing fails
    
    def start_recording_session(self) -> str:
        """
        Start a new recording session.
        
        Generates a new session ID for tracking the recording lifecycle.
        Does not clear manual format selection - that should be set before
        starting the session.
        
        Returns:
            The generated session ID
        
        Requirements: 4.4, 8.2, 8.4, 10.3
        """
        try:
            self._current_session_id = str(uuid.uuid4())
            logger.info(f"Recording session started: {self._current_session_id}")
            if self._manual_format_selection:
                logger.info(f"  Manual format selection active: {self._manual_format_selection}")
            return self._current_session_id
        except Exception as e:
            logger.error(f"Failed to start recording session: {e}")
            # Generate a fallback session ID to allow recording to continue
            try:
                self._current_session_id = f"fallback-{id(self)}"
                return self._current_session_id
            except:
                return "unknown-session"  # Last resort fallback
    
    def end_recording_session(self) -> None:
        """
        End the current recording session.
        
        Clears manual format selection and session ID. This should be called
        when transcription completes to ensure the manual selection doesn't
        persist to the next recording.
        
        Requirements: 4.4, 8.2, 8.4, 10.3
        """
        try:
            if self._current_session_id:
                logger.info(f"Recording session ended: {self._current_session_id}")
            self.clear_manual_format_selection()
        except Exception as e:
            logger.error(f"Failed to end recording session: {e}")
            # Attempt to clear anyway to prevent state leakage
            try:
                self.clear_manual_format_selection()
            except:
                pass  # Continue operation even if clearing fails
    
    def get_current_session_id(self) -> Optional[str]:
        """
        Get the current session ID.
        
        Returns:
            Current session ID or None if no session is active
        """
        return self._current_session_id

