"""
RapidWhisper - Главное приложение.

Минималистичное приложение для быстрой транскрипции речи с микрофона
используя Zhipu GLM API.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from core.config import Config
from core.state_manager import StateManager, AppState
from services.hotkey_manager import HotkeyManager
from services.audio_engine import AudioRecordingThread
from services.transcription_client import TranscriptionThread
from services.clipboard_manager import ClipboardManager
from services.silence_detector import SilenceDetector
from ui.floating_window import FloatingWindow
from ui.tray_icon import TrayIcon
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
    
    # Сигналы для безопасного вызова UI методов из других потоков
    _show_window_signal = pyqtSignal()
    _hide_window_signal = pyqtSignal()
    _set_status_signal = pyqtSignal(str)
    _set_result_signal = pyqtSignal(str)
    _start_recording_animation_signal = pyqtSignal()
    _start_loading_animation_signal = pyqtSignal()
    _stop_animation_signal = pyqtSignal()
    _start_auto_hide_signal = pyqtSignal(int)
    
    # ВАЖНО: Сигнал для обработки нажатия горячей клавиши из другого потока
    _hotkey_pressed_signal = pyqtSignal()
    
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
        self.tray_icon: TrayIcon = None
        
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
            self.config = Config.load_from_env()
            errors = self.config.validate()
            
            if errors:
                for error in errors:
                    self.logger.error(f"Ошибка конфигурации: {error}")
                raise ValueError("Ошибки в конфигурации. Проверьте .env файл")
            
            self.logger.info("Конфигурация загружена успешно")
            
            # Логировать информацию о провайдере
            api_key = self._get_api_key_for_provider()
            if api_key:
                self.logger.info(f"AI Provider: {self.config.ai_provider}")
                self.logger.info(f"API ключ загружен: {api_key[:10]}...")
            else:
                self.logger.warning(f"API ключ для провайдера {self.config.ai_provider} не найден!")
            
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
        
        # Tray Icon
        self.tray_icon = TrayIcon()
        self.tray_icon.show_settings.connect(self._show_settings)
        self.tray_icon.quit_app.connect(self._quit_app)
        
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
        
        # Подключаем внутренние сигналы к UI методам
        self._show_window_signal.connect(self.floating_window.show_at_center)
        self._hide_window_signal.connect(self.floating_window.hide_with_animation)
        self._set_status_signal.connect(self.floating_window.set_status)
        self._set_result_signal.connect(lambda text: self.floating_window.set_result_text(text, max_length=100))
        self._start_recording_animation_signal.connect(self.floating_window.get_waveform_widget().start_recording_animation)
        self._start_loading_animation_signal.connect(self.floating_window.get_waveform_widget().start_loading_animation)
        self._stop_animation_signal.connect(self.floating_window.get_waveform_widget().stop_animation)
        self._start_auto_hide_signal.connect(self.floating_window.start_auto_hide_timer)
        
        # ВАЖНО: Подключаем сигнал горячей клавиши к обработчику в главном потоке
        self._hotkey_pressed_signal.connect(self._handle_hotkey_in_main_thread)
        
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
        
        Вызывается из потока keyboard, поэтому использует сигнал
        для безопасной передачи в главный поток Qt.
        
        Requirements: 1.2
        """
        self.logger.info("Горячая клавиша нажата")
        # Отправляем сигнал в главный поток Qt
        self._hotkey_pressed_signal.emit()
    
    def _handle_hotkey_in_main_thread(self) -> None:
        """
        Обрабатывает нажатие горячей клавиши в главном потоке Qt.
        
        Этот метод вызывается через сигнал из главного потока.
        Повторное нажатие останавливает запись.
        """
        self.logger.info("Обработка горячей клавиши в главном потоке Qt")
        
        # Проверяем текущее состояние
        current_state = self.state_manager.current_state
        
        if current_state == AppState.RECORDING:
            # Если идет запись - останавливаем её
            self.logger.info("Остановка записи по нажатию горячей клавиши")
            
            # СРАЗУ СКРЫТЬ ОКНО
            self._hide_window_signal.emit()
            
            # Остановить поток записи - он сам вызовет _on_recording_stopped
            # который запустит транскрипцию
            if self.recording_thread and self.recording_thread.isRunning():
                self.recording_thread.stop()
                self.logger.info("Поток записи остановлен, ожидаем сохранения файла...")
            
            # Переход к обработке
            self.state_manager.transition_to(AppState.PROCESSING)
        else:
            # Иначе обрабатываем как обычно
            self.state_manager.on_hotkey_pressed()
        
        self.logger.info("StateManager.on_hotkey_pressed() вызван")
    
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
            self.logger.info("_start_recording вызван")
            
            # Показать окно через сигнал (безопасно для потоков)
            self.logger.info("Отправка сигнала показа окна...")
            self._show_window_signal.emit()
            
            self.logger.info("Отправка сигнала установки статуса...")
            self._set_status_signal.emit("Запись...")
            
            # Запустить анимацию записи
            self.logger.info("Отправка сигнала запуска анимации...")
            self._start_recording_animation_signal.emit()
            
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
            import traceback
            self.logger.error(traceback.format_exc())
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
        
        # Сохранить путь для транскрипции
        self._audio_file_path = audio_file_path
        
        # Если мы уже в состоянии PROCESSING (остановлено вручную),
        # запустить транскрипцию
        if self.state_manager.current_state == AppState.PROCESSING:
            self.logger.info("Состояние уже PROCESSING, запуск транскрипции...")
            self._start_transcription()
        else:
            # Иначе вызвать state manager для перехода
            self.logger.info("Вызов state_manager.on_silence_detected()")
            self.state_manager.on_silence_detected()
    
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
            self.logger.info(f"_start_transcription вызван, файл: {self._audio_file_path}")
            
            # СКРЫТЬ ОКНО при обработке
            self._hide_window_signal.emit()
            
            # Показать статус в трее
            self.tray_icon.set_status("Обработка аудио...")
            self.logger.info("Статус трея обновлен: Обработка аудио...")
            
            # Создать и запустить поток транскрипции
            self.transcription_thread = TranscriptionThread(
                self._audio_file_path,
                provider=self.config.ai_provider,
                api_key=self._get_api_key_for_provider()
            )
            
            self.logger.info("TranscriptionThread создан")
            
            # Подключить сигналы потока
            self.transcription_thread.transcription_complete.connect(
                self._on_transcription_complete
            )
            self.transcription_thread.transcription_error.connect(
                self._on_transcription_error
            )
            
            self.logger.info("Сигналы TranscriptionThread подключены")
            
            # Запустить поток
            self.transcription_thread.start()
            
            self.logger.info("TranscriptionThread запущен")
            
        except Exception as e:
            self.logger.error(f"Ошибка начала транскрипции: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
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
            # Сбросить статус трея
            self.tray_icon.set_status("Готово! Нажмите Ctrl+Space для записи")
            
            # Показать окно с результатом
            self._show_window_signal.emit()
            
            # Остановить анимацию загрузки
            self._stop_animation_signal.emit()
            
            # Отобразить текст (с усечением если нужно)
            self._set_result_signal.emit(text)
            
            # Скопировать в буфер обмена
            self.clipboard_manager.copy_to_clipboard(text)
            
            # Запустить таймер автоскрытия
            self._start_auto_hide_signal.emit(self.config.auto_hide_delay)
            
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
            self._hide_window_signal.emit()
            # Сбросить статус трея
            self.tray_icon.set_status("Готово! Нажмите Ctrl+Space для записи")
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
            self._stop_animation_signal.emit()
            
            # Показать сообщение об ошибке
            error_message = f"Ошибка: {str(error)}"
            self._set_status_signal.emit(error_message)
            
            # Автоматически скрыть через 3 секунды
            self._start_auto_hide_signal.emit(3000)
            
            self.logger.error(f"Показана ошибка: {error}")
            
        except Exception as e:
            self.logger.error(f"Ошибка показа ошибки: {e}")
    
    def _get_api_key_for_provider(self) -> Optional[str]:
        """
        Возвращает API ключ для текущего провайдера.
        
        Returns:
            API ключ или None
        """
        if self.config.ai_provider == "openai":
            return self.config.openai_api_key
        elif self.config.ai_provider == "groq":
            return self.config.groq_api_key
        elif self.config.ai_provider == "glm":
            return self.config.glm_api_key
        return None
    
    def _show_settings(self) -> None:
        """Показывает окно настроек."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            None,
            "Настройки",
            f"Текущие настройки:\n\n"
            f"AI Provider: {self.config.ai_provider}\n"
            f"Горячая клавиша: {self.config.hotkey}\n"
            f"Порог тишины: {self.config.silence_threshold}\n"
            f"Длительность тишины: {self.config.silence_duration}с\n"
            f"Автоскрытие: {self.config.auto_hide_delay}с\n\n"
            f"Для изменения настроек отредактируйте файл .env"
        )
    
    def _quit_app(self) -> None:
        """Выход из приложения."""
        self.logger.info("Запрос на выход из приложения")
        QApplication.instance().quit()
    
    def run(self) -> int:
        """
        Запускает главный цикл событий приложения.
        
        Returns:
            Код возврата приложения
        
        Requirements: 12.6
        """
        if not self._initialized:
            raise RuntimeError("Приложение не инициализировано. Вызовите initialize() сначала.")
        
        # Показать окно при запуске на 2 секунды
        self.floating_window.show_at_center()
        self.floating_window.set_status("RapidWhisper загружен!")
        
        # Автоматически скрыть через 2 секунды
        QTimer.singleShot(2000, self.floating_window.hide_with_animation)
        
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
            
            # Скрыть иконку трея
            if self.tray_icon:
                self.tray_icon.hide()
            
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
