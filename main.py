"""
RapidWhisper - Главное приложение.

Минималистичное приложение для быстрой транскрипции речи с микрофона
используя Zhipu GLM API.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject

from core.config import Config
from core.state_manager import StateManager, AppState
from services.hotkey_manager import HotkeyManager
from services.audio_engine import AudioRecordingThread
from services.glm_client import TranscriptionThread
from services.clipboard_manager import ClipboardManager
from services.silence_detector import SilenceDetector
from ui.floating_window import FloatingWindow
from utils.logger import get_logger


class RapidWhisperApp(QObject):
    """
    Главное приложение RapidWhisper.
    
    Координирует все компоненты приложения:
    - Управление горячими клавишами
    - Запись аудио с микрофона
    - Определение тишины
    - Транскрипция через GLM API
    - Отображение результатов
    - Копирование в буфер обмена
    
    Requirements: 12.1, 12.2, 12.6
    """
    
    def __init__(self):
        """Инициализирует приложение."""
        super().__init__()
        
        # Логгер
        self.logger = get_logger()
        
        # Конфигурация
        self.config: Config = None
        
        # Компоненты
        self.state_manager: StateManager = None
        self.hotkey_manager: HotkeyManager = None
        self.floating_window: FloatingWindow = None
        self.clipboard_manager: ClipboardManager = None
        self.silence_detector: SilenceDetector = None
        
        # Потоки
        self.recording_thread: AudioRecordingThread = None
        self.transcription_thread: TranscriptionThread = None
        
        # Флаг инициализации
        self._initialized = False
    
    def initialize(self) -> None:
        """
        Инициализирует все компоненты приложения.
        
        Загружает конфигурацию, создает компоненты и подключает сигналы.
        
        Requirements: 12.1
        """
        try:
            # Загрузить конфигурацию
            self.config = Config()
            self.config.load_from_env()
            self.config.validate()
            
            self.logger.info("Конфигурация загружена успешно")
            
            # Создать компоненты
            self._create_components()
            
            # Подключить сигналы
            self._connect_signals()
            
            # Зарегистрировать горячую клавишу
            self._register_hotkey()
            
            self._initialized = True
            self.logger.info("RapidWhisper инициализирован успешно")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации: {e}")
            raise
    
    def _create_components(self) -> None:
        """Создает все компоненты приложения."""
        # State Manager
        self.state_manager = StateManager()
        
        # Floating Window
        self.floating_window = FloatingWindow()
        self.floating_window.apply_blur_effect()
        
        # Clipboard Manager
        self.clipboard_manager = ClipboardManager()
        
        # Silence Detector
        self.silence_detector = SilenceDetector(
            threshold=self.config.silence_threshold,
            silence_duration=self.config.silence_duration
        )
        
        # Hotkey Manager (создается без callback, callback устанавливается позже)
        # Временно создаем с пустым callback
        self.hotkey_manager = None
        
        self.logger.info("Компоненты созданы")
    
    def _connect_signals(self) -> None:
        """
        Подключает сигналы между компонентами.
        
        Requirements: 1.2, 4.1, 5.5, 8.1, 8.2, 8.6
        """
        # State Manager callbacks
        self.state_manager.set_callbacks(
            on_start_recording=self._start_recording,
            on_stop_recording=self._stop_recording,
            on_start_transcription=self._start_transcription,
            on_display_result=self._display_result,
            on_hide_window=self._hide_window,
            on_show_error=self._show_error
        )
        
        # State Manager signal
        self.state_manager.state_changed.connect(self._on_state_changed)
        
        self.logger.info("Сигналы подключены")
    
    def _register_hotkey(self) -> None:
        """
        Регистрирует глобальную горячую клавишу.
        
        Requirements: 1.1, 1.4
        """
        try:
            # Создать HotkeyManager с callback
            self.hotkey_manager = HotkeyManager(self._on_hotkey_pressed)
            
            # Зарегистрировать горячую клавишу
            self.hotkey_manager.register_hotkey(self.config.hotkey)
            
            self.logger.info(f"Горячая клавиша зарегистрирована: {self.config.hotkey}")
            
        except Exception as e:
            self.logger.error(f"Не удалось зарегистрировать горячую клавишу: {e}")
            raise
    
    def _on_hotkey_pressed(self) -> None:
        """
        Обработчик нажатия горячей клавиши.
        
        Requirements: 1.2
        """
        self.logger.info("Горячая клавиша нажата")
        self.state_manager.on_hotkey_pressed()
    
    def _on_state_changed(self, new_state: AppState) -> None:
        """
        Обработчик изменения состояния приложения.
        
        Args:
            new_state: Новое состояние
        """
        self.logger.info(f"Состояние изменено: {new_state.value}")
    
    def _start_recording(self) -> None:
        """
        Начинает запись аудио.
        
        Показывает окно, запускает поток записи и визуализацию.
        
        Requirements: 3.1, 4.1
        """
        try:
            # Показать окно
            self.floating_window.show_at_center()
            self.floating_window.set_status("Запись...")
            
            # Запустить анимацию записи
            self.floating_window.get_waveform_widget().start_recording_animation()
            
            # Сбросить детектор тишины
            self.silence_detector.reset()
            
            # Создать и запустить поток записи
            self.recording_thread = AudioRecordingThread(self.silence_detector)
            
            # Подключить сигналы потока
            self.recording_thread.rms_updated.connect(
                self.floating_window.get_waveform_widget().update_rms
            )
            self.recording_thread.silence_detected.connect(
                self.state_manager.on_silence_detected
            )
            self.recording_thread.recording_stopped.connect(
                self._on_recording_stopped
            )
            self.recording_thread.recording_error.connect(
                self._on_recording_error
            )
            
            # Запустить поток
            self.recording_thread.start()
            
            self.logger.info("Запись начата")
            
        except Exception as e:
            self.logger.error(f"Ошибка начала записи: {e}")
            self.state_manager.on_error(e)
    
    def _stop_recording(self) -> None:
        """
        Останавливает запись аудио.
        
        Requirements: 5.5
        """
        try:
            if self.recording_thread and self.recording_thread.isRunning():
                self.recording_thread.stop()
                self.logger.info("Запись остановлена")
                
        except Exception as e:
            self.logger.error(f"Ошибка остановки записи: {e}")
            self.state_manager.on_error(e)
    
    def _on_recording_stopped(self, audio_file_path: str) -> None:
        """
        Обработчик завершения записи.
        
        Args:
            audio_file_path: Путь к сохраненному аудио файлу
        """
        self.logger.info(f"Запись сохранена: {audio_file_path}")
        self.state_manager.on_silence_detected()
        
        # Сохранить путь для транскрипции
        self._audio_file_path = audio_file_path
    
    def _on_recording_error(self, error: Exception) -> None:
        """
        Обработчик ошибки записи.
        
        Args:
            error: Исключение
        """
        self.logger.error(f"Ошибка записи: {error}")
        self.state_manager.on_error(error)
    
    def _start_transcription(self) -> None:
        """
        Начинает транскрипцию аудио.
        
        Запускает поток транскрипции и показывает индикатор загрузки.
        
        Requirements: 6.3, 7.1
        """
        try:
            # Показать индикатор загрузки
            self.floating_window.set_status("Обработка...")
            self.floating_window.get_waveform_widget().start_loading_animation()
            
            # Создать и запустить поток транскрипции
            self.transcription_thread = TranscriptionThread(
                self._audio_file_path,
                api_key=self.config.glm_api_key
            )
            
            # Подключить сигналы потока
            self.transcription_thread.transcription_complete.connect(
                self._on_transcription_complete
            )
            self.transcription_thread.transcription_error.connect(
                self._on_transcription_error
            )
            
            # Запустить поток
            self.transcription_thread.start()
            
            self.logger.info("Транскрипция начата")
            
        except Exception as e:
            self.logger.error(f"Ошибка начала транскрипции: {e}")
            self.state_manager.on_error(e)
    
    def _on_transcription_complete(self, text: str) -> None:
        """
        Обработчик завершения транскрипции.
        
        Args:
            text: Транскрибированный текст
        """
        self.logger.info(f"Транскрипция завершена: {text[:50]}...")
        self.state_manager.on_transcription_complete(text)
    
    def _on_transcription_error(self, error: Exception) -> None:
        """
        Обработчик ошибки транскрипции.
        
        Args:
            error: Исключение
        """
        self.logger.error(f"Ошибка транскрипции: {error}")
        self.state_manager.on_error(error)
    
    def _display_result(self, text: str) -> None:
        """
        Отображает результат транскрипции.
        
        Показывает текст в окне, копирует в буфер обмена и
        запускает таймер автоскрытия.
        
        Requirements: 8.1, 8.2, 8.3, 8.6
        """
        try:
            # Остановить анимацию загрузки
            self.floating_window.get_waveform_widget().stop_animation()
            
            # Отобразить текст (с усечением если нужно)
            self.floating_window.set_result_text(text, max_length=100)
            
            # Скопировать в буфер обмена
            self.clipboard_manager.copy_to_clipboard(text)
            
            # Запустить таймер автоскрытия
            self.floating_window.start_auto_hide_timer(
                self.config.auto_hide_delay
            )
            
            self.logger.info("Результат отображен")
            
        except Exception as e:
            self.logger.error(f"Ошибка отображения результата: {e}")
            self.state_manager.on_error(e)
    
    def _hide_window(self) -> None:
        """
        Скрывает окно с анимацией.
        
        Requirements: 2.8
        """
        try:
            self.floating_window.hide_with_animation()
            self.logger.info("Окно скрыто")
            
        except Exception as e:
            self.logger.error(f"Ошибка скрытия окна: {e}")
    
    def _show_error(self, error: Exception) -> None:
        """
        Показывает сообщение об ошибке.
        
        Args:
            error: Исключение
        
        Requirements: 10.6
        """
        try:
            # Остановить анимации
            self.floating_window.get_waveform_widget().stop_animation()
            
            # Показать сообщение об ошибке
            error_message = f"Ошибка: {str(error)}"
            self.floating_window.set_status(error_message)
            
            # Автоматически скрыть через 3 секунды
            self.floating_window.start_auto_hide_timer(3000)
            
            self.logger.error(f"Показана ошибка: {error}")
            
        except Exception as e:
            self.logger.error(f"Ошибка показа ошибки: {e}")
    
    def run(self) -> int:
        """
        Запускает главный цикл событий приложения.
        
        Returns:
            Код возврата приложения
        
        Requirements: 12.6
        """
        if not self._initialized:
            raise RuntimeError("Приложение не инициализировано. Вызовите initialize() сначала.")
        
        self.logger.info("RapidWhisper запущен")
        return QApplication.instance().exec()
    
    def shutdown(self) -> None:
        """
        Корректно завершает работу приложения.
        
        Освобождает все ресурсы и закрывает компоненты.
        
        Requirements: 12.2, 12.3, 12.4
        """
        try:
            self.logger.info("Завершение работы RapidWhisper...")
            
            # Остановить потоки
            if self.recording_thread and self.recording_thread.isRunning():
                self.recording_thread.stop()
                self.recording_thread.wait(1000)
            
            if self.transcription_thread and self.transcription_thread.isRunning():
                self.transcription_thread.wait(1000)
            
            # Отменить регистрацию горячей клавиши
            if self.hotkey_manager:
                self.hotkey_manager.unregister_hotkey()
            
            # Скрыть окно
            if self.floating_window:
                self.floating_window.hide()
            
            # Очистить ресурсы state manager
            if self.state_manager:
                self.state_manager.cleanup_resources()
            
            self.logger.info("RapidWhisper завершен")
            
        except Exception as e:
            self.logger.error(f"Ошибка при завершении: {e}")


def main():
    """Точка входа в приложение."""
    # Создать QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("RapidWhisper")
    app.setOrganizationName("RapidWhisper")
    
    # Создать и инициализировать приложение
    rapid_whisper = RapidWhisperApp()
    
    try:
        rapid_whisper.initialize()
        exit_code = rapid_whisper.run()
        
    except KeyboardInterrupt:
        print("\nПрервано пользователем")
        exit_code = 0
        
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        exit_code = 1
        
    finally:
        rapid_whisper.shutdown()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
