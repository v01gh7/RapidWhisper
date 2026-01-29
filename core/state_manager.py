"""
Менеджер состояний приложения RapidWhisper.

Координирует переходы между состояниями приложения и управляет
взаимодействием между компонентами.
"""

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
            
            # Вызвать callback для начала транскрипции
            if self._on_start_transcription:
                logger.info("Вызов callback _on_start_transcription")
                self._on_start_transcription()
            else:
                logger.warning("Callback _on_start_transcription не установлен!")
        else:
            logger.warning(f"Тишина обнаружена в неправильном состоянии: {self.current_state.value}")
    
    def on_transcription_complete(self, text: str) -> None:
        """
        Обрабатывает завершение транскрипции.
        
        Переходит в состояние DISPLAYING и отображает результат.
        
        Args:
            text: Транскрибированный текст
        
        Requirements: 8.1, 8.2
        """
        logger.info(f"Транскрипция завершена в состоянии {self.current_state.value}")
        
        if self.current_state == AppState.PROCESSING:
            # PROCESSING → DISPLAYING
            if self._on_display_result:
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
