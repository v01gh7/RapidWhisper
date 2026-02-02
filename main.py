"""
RapidWhisper - Главное приложение.

Минималистичное приложение для быстрой транскрипции речи с микрофона
используя Zhipu GLM API.
"""

import sys
from typing import Optional
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from pathlib import Path

from core.config import Config, get_config_dir
from core.state_manager import StateManager, AppState
from core.statistics_manager import StatisticsManager
from services.hotkey_manager import HotkeyManager
from services.audio_engine import AudioRecordingThread
from services.transcription_client import TranscriptionThread
from services.clipboard_manager import ClipboardManager
from services.silence_detector import SilenceDetector
from ui.floating_window import FloatingWindow
from ui.tray_icon import TrayIcon
from utils.logger import get_logger
from utils.single_instance import SingleInstance
from utils.i18n import t


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
    
    # Сигнал для format selection hotkey
    _format_selection_hotkey_signal = pyqtSignal()
    
    # Сигнал для отмены записи (ESC)
    _cancel_recording_signal = pyqtSignal()
    
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
        self.statistics_manager: StatisticsManager = None
        
        # Потоки
        self.recording_thread: AudioRecordingThread = None
        self.transcription_thread: TranscriptionThread = None
        
        # Окно настроек (единственный экземпляр)
        self.settings_window = None
        
        # Диалог выбора формата (единственный экземпляр)
        self.format_selection_dialog = None
        self._format_dialog_open = False
        
        # Флаг инициализации
        self._initialized = False
        
        # Флаг показа окна при запуске
        self._startup_window_visible = False
        
        # Флаг необходимости первоначальной настройки
        self._needs_setup = False
    
    def initialize(self) -> None:
        """
        Инициализирует все компоненты приложения.
        
        Загружает конфигурацию, создает компоненты и подключает сигналы.
        
        Requirements: 12.1
        """
        try:
            # Загрузить конфигурацию из config.jsonc
            self.config = Config.load_from_config()
            
            # Проверить наличие API ключа
            if not self.config.has_api_key():
                self.logger.warning("API ключ не установлен - требуется первоначальная настройка")
                # Флаг что нужна первоначальная настройка
                self._needs_setup = True
            else:
                self._needs_setup = False
                
                # Валидировать только если ключ есть
                errors = self.config.validate()
                
                if errors:
                    for error in errors:
                        self.logger.error(f"Ошибка конфигурации: {error}")
                    raise ValueError("Ошибки в конфигурации. Проверьте config.jsonc и secrets.json")
            
            self.logger.info("Конфигурация загружена успешно")
            
            # Логировать информацию о провайдере
            api_key = self._get_api_key_for_provider()
            if api_key:
                self.logger.info(f"AI Provider: {self.config.ai_provider}")
                self.logger.info(f"API ключ загружен: {api_key[:10]}...")
            else:
                self.logger.warning(f"API ключ для провайдера {self.config.ai_provider} не найден!")
            
            # Логировать режим ручной остановки
            self.logger.info(f"Режим ручной остановки: {self.config.manual_stop}")
            
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
        
        # Statistics Manager
        config_dir = get_config_dir()
        self.statistics_manager = StatisticsManager(config_dir)
        
        # Floating Window - передаем конфигурацию для инициализации прозрачности
        self.floating_window = FloatingWindow(config=self.config)
        self.floating_window.apply_blur_effect()
        
        # Установить конфигурацию для инициализации window monitor и info panel
        self.floating_window.set_config(self.config)
        
        # Tray Icon - передаем floating_window как parent
        self.tray_icon = TrayIcon(parent=self.floating_window)
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
        self._show_window_signal.connect(self._show_window_with_config)
        self._hide_window_signal.connect(self.floating_window.hide_with_animation)
        self._set_status_signal.connect(self.floating_window.set_status)
        self._set_result_signal.connect(lambda text: self.floating_window.set_result_text(text, max_length=100))
        self._start_recording_animation_signal.connect(self.floating_window.get_waveform_widget().start_recording_animation)
        self._start_loading_animation_signal.connect(self.floating_window.get_waveform_widget().start_loading_animation)
        self._stop_animation_signal.connect(self.floating_window.get_waveform_widget().stop_animation)
        self._start_auto_hide_signal.connect(self.floating_window.start_auto_hide_timer)
        
        # ВАЖНО: Подключаем сигнал горячей клавиши к обработчику в главном потоке
        self._hotkey_pressed_signal.connect(self._handle_hotkey_in_main_thread)
        
        # Подключаем сигнал format selection hotkey
        self._format_selection_hotkey_signal.connect(self._handle_format_selection_in_main_thread)
        
        # Подключаем сигнал отмены записи
        self._cancel_recording_signal.connect(self._handle_cancel_recording)
        
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
            
            # Зарегистрировать ESC для отмены записи
            self.hotkey_manager.register_hotkey("esc", self._on_cancel_pressed)
            
            # Зарегистрировать горячую клавишу выбора формата (Requirements: 1.1, 1.2)
            format_hotkey = self.config.format_selection_hotkey or "ctrl+alt+space"
            success = self.hotkey_manager.register_format_selection_hotkey(
                format_hotkey,
                self._on_format_selection_hotkey
            )
            
            if success:
                self.logger.info(f"Горячая клавиша выбора формата зарегистрирована: {format_hotkey}")
            else:
                self.logger.warning(f"Не удалось зарегистрировать горячую клавишу выбора формата: {format_hotkey}")
            
            self.logger.info(f"Горячая клавиша зарегистрирована: {self.config.hotkey}")
            self.logger.info("ESC зарегистрирован для отмены записи")
            
        except Exception as e:
            self.logger.error(f"Не удалось зарегистрировать горячую клавишу: {e}")
            raise
    
    def _on_cancel_pressed(self) -> None:
        """
        Обработчик нажатия ESC для отмены записи.
        
        Вызывается из потока keyboard, поэтому использует сигнал
        для безопасной передачи в главный поток Qt.
        """
        self.logger.info("ESC нажат")
        # Отправляем сигнал в главный поток Qt
        self._cancel_recording_signal.emit()
    
    def _handle_cancel_recording(self) -> None:
        """
        Обрабатывает отмену записи в главном потоке Qt.
        """
        self.logger.info("Обработка отмены записи")
        
        # Отменяем только если идет запись
        if self.state_manager.current_state == AppState.RECORDING:
            self.logger.info("Отмена записи по ESC")
            
            # Остановить поток записи БЕЗ сохранения файла
            if self.recording_thread and self.recording_thread.isRunning():
                self.recording_thread.cancel()  # Используем cancel вместо stop
                self.logger.info("Поток записи отменен (без сохранения)")
            
            # Скрыть окно
            self._hide_window_signal.emit()
            
            # Показать уведомление
            self.tray_icon.show_message(
                t("tray.notification.recording_cancelled"),
                t("tray.notification.recording_cancelled_message"),
                duration=3000
            )
            
            # Вернуться в IDLE
            self.state_manager.transition_to(AppState.IDLE)
            
            # Сбросить статус трея
            self.tray_icon.set_status(t("tray.tooltip.ready", hotkey=self.config.hotkey))
        else:
            self.logger.info(f"ESC нажат в состоянии {self.state_manager.current_state.value}, игнорируем")
    
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
    
    def _on_format_selection_hotkey(self) -> None:
        """
        Обработчик нажатия горячей клавиши выбора формата.
        
        Вызывается из потока keyboard. Эмитит сигнал для обработки в главном потоке.
        
        Requirements: 1.2, 1.3, 3.1, 3.2
        """
        self.logger.info("Горячая клавиша выбора формата нажата")
        self._format_selection_hotkey_signal.emit()
    
    def _handle_format_selection_in_main_thread(self) -> None:
        """
        Обрабатывает нажатие горячей клавиши выбора формата в главном потоке Qt.
        
        Этот метод вызывается через сигнал из главного потока.
        """
        self.logger.info("Обработка горячей клавиши выбора формата в главном потоке Qt")
        
        # Check if recording is already active
        if self.state_manager.current_state == AppState.RECORDING:
            self.logger.info("Запись уже активна - игнорируем нажатие клавиши выбора формата")
            return
        
        # Check if API key is configured
        if not self.config.has_api_key():
            self.logger.warning("Попытка выбора формата без API ключа")
            self.tray_icon.show_message(
                t("tray.notification.no_api_key"),
                t("tray.notification.no_api_key_message"),
                duration=5000
            )
            # Open settings
            self._show_settings()
            return
        
        # Show format selection dialog
        self._show_format_selection_dialog()
    
    def _handle_hotkey_in_main_thread(self) -> None:
        """
        Обрабатывает нажатие горячей клавиши в главном потоке Qt.
        
        Этот метод вызывается через сигнал из главного потока.
        Повторное нажатие останавливает запись.
        """
        self.logger.info("Обработка горячей клавиши в главном потоке Qt")
        
        # Проверить наличие API ключа
        if not self.config.has_api_key():
            self.logger.warning("Попытка записи без API ключа")
            
            # Показать уведомление
            self.tray_icon.show_message(
                t("tray.notification.no_api_key"),
                t("tray.notification.no_api_key_message"),
                duration=5000
            )
            
            # Открыть настройки
            self._show_settings()
            return
        
        # Игнорировать нажатия во время показа окна при запуске
        if self._startup_window_visible:
            self.logger.info("Игнорирование нажатия - окно запуска еще видимо")
            return
        
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
    
    def _show_window_with_config(self) -> None:
        """
        Показывает окно с учетом настройки запоминания позиции.
        
        Логика:
        - Всегда передаем use_saved_position=True
        - Внутри show_at_center() проверяется WINDOW_POSITION_PRESET
        - Если preset='custom' - используется пользовательская позиция
        - Если preset='center'/'top_left'/etc - используется предустановленная позиция
        """
        # Всегда используем сохраненную позицию (preset или custom)
        self.floating_window.show_at_center(use_saved_position=True)
    
    def _start_recording(self) -> None:
        """
        Начинает запись аудио.
        
        Показывает окно, запускает поток записи и визуализацию.
        
        Requirements: 3.1, 4.1
        """
        try:
            self.logger.info("_start_recording вызван")
            
            # ВАЖНО: Перезагрузить конфигурацию перед записью
            # чтобы применить последние изменения настроек
            self.config = Config.load_from_config()
            self.logger.info(f"Конфигурация перезагружена: manual_stop={self.config.manual_stop}")
            
            # Показать info panel при начале записи
            self.floating_window.show_info_panel()
            
            # Показать окно через сигнал (безопасно для потоков)
            self.logger.info("Отправка сигнала показа окна...")
            self._show_window_signal.emit()
            
            self.logger.info("Отправка сигнала установки статуса...")
            self._set_status_signal.emit(t("status.recording"))
            
            # Запустить анимацию записи
            self.logger.info("Отправка сигнала запуска анимации...")
            self._start_recording_animation_signal.emit()
            
            # Сбросить детектор тишины
            self.silence_detector.reset()
            
            # Создать и запустить поток записи
            # Передать флаг enable_silence_detection в зависимости от режима
            enable_silence = not self.config.manual_stop
            self.recording_thread = AudioRecordingThread(
                self.silence_detector, 
                enable_silence_detection=enable_silence
            )
            self.logger.info(f"AudioRecordingThread создан: enable_silence_detection={enable_silence}")
            
            # Подключить сигналы потока
            self.recording_thread.rms_updated.connect(
                self.floating_window.get_waveform_widget().update_rms
            )
            
            # Подключить сигнал тишины только если НЕ включен ручной режим
            if not self.config.manual_stop:
                self.logger.info("Режим автоматической остановки: подключаем сигнал тишины")
                self.recording_thread.silence_detected.connect(
                    self.state_manager.on_silence_detected
                )
            else:
                self.logger.info("Режим ручной остановки: сигнал тишины НЕ подключается")
            
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
        
        # Track recording statistics
        try:
            import wave
            with wave.open(audio_file_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration_seconds = frames / float(rate)
                self.statistics_manager.track_recording(duration_seconds)
                self.logger.info(f"Recording statistics tracked: {duration_seconds:.2f} seconds")
        except Exception as e:
            self.logger.error(f"Failed to track recording statistics: {e}")
        
        # Если мы в состоянии PROCESSING (остановлено вручную или по тишине),
        # запустить транскрипцию
        if self.state_manager.current_state == AppState.PROCESSING:
            self.logger.info("Состояние PROCESSING, запуск транскрипции...")
            self._start_transcription()
        elif self.state_manager.current_state == AppState.RECORDING:
            # Если еще в RECORDING, значит остановка по тишине еще не обработана
            self.logger.info("Вызов state_manager.on_silence_detected()")
            self.state_manager.on_silence_detected()
            # После перехода в PROCESSING запустить транскрипцию
            if self.state_manager.current_state == AppState.PROCESSING:
                self._start_transcription()
    
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
            # Проверить что файл существует
            if not hasattr(self, '_audio_file_path') or not self._audio_file_path:
                self.logger.error("Нет аудио файла для транскрипции!")
                self.state_manager.on_error(Exception("Аудио файл не найден"))
                return
            
            self.logger.info(f"_start_transcription вызван, файл: {self._audio_file_path}")
            
            # СКРЫТЬ ОКНО при обработке
            self._hide_window_signal.emit()
            
            # Показать статус в трее
            self.tray_icon.set_status(t("status.processing"))
            self.logger.info("Статус трея обновлен: Обработка аудио...")
            
            # Получить модель для транскрипции
            transcription_model = self._get_transcription_model_for_provider()
            if transcription_model:
                self.logger.info(f"🎙️ Модель транскрипции: {transcription_model}")
            else:
                # Показать дефолтную модель для провайдера
                default_models = {
                    "groq": "whisper-large-v3",
                    "openai": "whisper-1",
                    "glm": "glm-4-voice"
                }
                default_model = default_models.get(self.config.ai_provider, "unknown")
                self.logger.info(f"🎙️ Модель транскрипции: {default_model} (default для {self.config.ai_provider})")
            self.logger.info(f"custom_model из конфига: '{self.config.custom_model}'")
            
            # Создать и запустить поток транскрипции
            self.transcription_thread = TranscriptionThread(
                self._audio_file_path,
                provider=self.config.ai_provider,
                api_key=self._get_api_key_for_provider(),
                base_url=self.config.custom_base_url if self.config.ai_provider == "custom" else None,
                model=transcription_model,
                statistics_manager=self.statistics_manager,
                state_manager=self.state_manager
            )
            
            self.logger.info("TranscriptionThread создан")
            
            # Подключить сигналы потока
            self.transcription_thread.transcription_complete.connect(
                self._on_transcription_complete
            )
            self.transcription_thread.transcription_error.connect(
                self._on_transcription_error
            )
            self.transcription_thread.model_not_found.connect(
                self._on_model_not_found
            )
            self.transcription_thread.transcription_model_not_found.connect(
                self._on_transcription_model_not_found
            )
            self.transcription_thread.api_error.connect(
                self._on_api_error
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
        
        # Track transcription statistics
        try:
            import wave
            with wave.open(self._audio_file_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                audio_duration = frames / float(rate)
                self.statistics_manager.track_transcription(audio_duration, text)
                self.logger.info(f"Transcription statistics tracked: {audio_duration:.2f} seconds, {len(text)} characters")
        except Exception as e:
            self.logger.error(f"Failed to track transcription statistics: {e}")
        
        self.state_manager.on_transcription_complete(text)
    
    def _on_transcription_error(self, error: Exception) -> None:
        """
        Обработчик ошибки транскрипции.
        
        Args:
            error: Исключение
        """
        self.logger.error(f"Ошибка транскрипции: {error}")
        self.state_manager.on_error(error)
    
    def _on_model_not_found(self, model: str, provider: str) -> None:
        """
        Обработчик ошибки "модель не найдена" в постобработке.
        
        Показывает уведомление пользователю через tray icon.
        
        Args:
            model: Название модели
            provider: Провайдер
        """
        self.logger.warning(f"Модель постобработки не найдена: {model} для провайдера {provider}")
        
        # Показать уведомление в трее
        self.tray_icon.show_message(
            t("tray.notification.model_not_found"),
            t("tray.notification.model_not_found_message", model=model, provider=provider),
            duration=8000  # 8 секунд - дольше чем обычные уведомления
        )
        
        self.logger.info("Уведомление о модели постобработки не найдена показано пользователю")
    
    def _on_transcription_model_not_found(self, model: str, provider: str) -> None:
        """
        Обработчик ошибки "модель транскрипции не найдена".
        
        Показывает уведомление пользователю через tray icon.
        
        Args:
            model: Название модели
            provider: Провайдер
        """
        self.logger.warning(f"Модель транскрипции не найдена: {model} для провайдера {provider}")
        
        # Показать уведомление в трее
        self.tray_icon.show_message(
            t("tray.notification.transcription_model_not_found"),
            t("tray.notification.transcription_model_not_found_message", model=model, provider=provider),
            duration=8000  # 8 секунд - дольше чем обычные уведомления
        )
        
        self.logger.info("Уведомление о модели транскрипции не найдена показано пользователю")
    
    def _on_api_error(self, error_type: str, error_message: str, provider: str) -> None:
        """
        Обработчик ошибок API (rate limit, authentication, connection, etc.).
        
        Показывает уведомление пользователю через tray icon.
        
        Args:
            error_type: Тип ошибки (RateLimitError, AuthenticationError, etc.)
            error_message: Сообщение об ошибке
            provider: Провайдер
        """
        self.logger.warning(f"API Error: {error_type} для провайдера {provider}")
        self.logger.warning(f"Сообщение: {error_message}")
        
        # Создать понятное сообщение для пользователя
        if error_type == "RateLimitError":
            # Извлечь время ожидания из сообщения
            import re
            wait_time_match = re.search(r'try again in (\d+[msh][\d.]*[msh]*)', error_message)
            wait_time = wait_time_match.group(1) if wait_time_match else t("tray.notification.api_rate_limit_wait_default", default="несколько минут")
            
            title = t("tray.notification.api_rate_limit")
            message = t("tray.notification.api_rate_limit_message", provider=provider, wait_time=wait_time)
        elif error_type == "AuthenticationError":
            title = t("tray.notification.api_authentication")
            message = t("tray.notification.api_authentication_message", provider=provider)
        elif error_type == "APIConnectionError":
            title = t("tray.notification.api_connection")
            message = t("tray.notification.api_connection_message", provider=provider)
        elif error_type == "APITimeoutError":
            title = t("tray.notification.api_timeout")
            message = t("tray.notification.api_timeout_message", provider=provider)
        else:
            title = t("tray.notification.api_error")
            message = t("tray.notification.api_error_message", provider=provider, error=error_message[:200])
        
        # Показать уведомление в трее
        self.tray_icon.show_message(
            title,
            message,
            duration=10000  # 10 секунд - дольше для важных ошибок
        )
        
        self.logger.info(f"Уведомление об ошибке API показано пользователю: {title}")
    
    def _display_result(self, text: str) -> None:
        """
        Отображает результат транскрипции.
        
        Копирует текст в буфер обмена и показывает уведомление в трее.
        
        Requirements: 8.1, 8.2, 8.3, 8.6
        """
        try:
            # Скопировать в буфер обмена
            # Проверить, содержит ли текст HTML теги
            if '<h1>' in text or '<h2>' in text or '<h3>' in text or '<p>' in text or '<strong>' in text or '<ul>' in text or '<ol>' in text:
                # Это HTML - использовать RichClipboardManager
                self.logger.info("Обнаружен HTML в тексте, используем RichClipboardManager")
                from services.rich_clipboard_manager import RichClipboardManager
                
                # Создать plain text версию для fallback
                import re
                plain_text = text
                plain_text = re.sub(r'<h[1-6]>(.*?)</h[1-6]>', r'\1\n', plain_text)
                plain_text = re.sub(r'<p>(.*?)</p>', r'\1\n', plain_text)
                plain_text = re.sub(r'<strong>(.*?)</strong>', r'\1', plain_text)
                plain_text = re.sub(r'<em>(.*?)</em>', r'\1', plain_text)
                plain_text = re.sub(r'<li>(.*?)</li>', r'- \1\n', plain_text)
                plain_text = re.sub(r'</?[^>]+>', '', plain_text)
                plain_text = re.sub(r'\n\n+', '\n\n', plain_text).strip()
                
                success = RichClipboardManager.copy_html_to_clipboard(text, plain_text)
                if success:
                    self.logger.info(f"HTML скопирован в буфер обмена: {text[:50]}...")
                else:
                    self.logger.warning("Не удалось скопировать HTML, используем обычный текст")
                    self.clipboard_manager.copy_to_clipboard(plain_text)
            else:
                # Обычный текст
                self.clipboard_manager.copy_to_clipboard(text)
                self.logger.info(f"Текст скопирован в буфер обмена: {text[:50]}...")
            
            # Показать уведомление в трее
            self.tray_icon.show_message(
                t("common.success"),
                f"{t('tray.notification.text_copied')}\n\n{text[:100]}{'...' if len(text) > 100 else ''}",
                duration=5000  # 5 секунд
            )
            
            # Сбросить статус трея
            self.tray_icon.set_status(t("tray.tooltip.ready", hotkey=self.config.hotkey))
            
            self.logger.info("Результат обработан")
            
            # НЕ переходим в IDLE здесь - пусть StateManager обработает
            # Переход в DISPLAYING уже произошел в state_manager.on_transcription_complete
            # Автоматически перейдем в IDLE через таймер
            QTimer.singleShot(100, lambda: self.state_manager.transition_to(AppState.IDLE))

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
            self.tray_icon.set_status(t("tray.tooltip.ready", hotkey=self.config.hotkey))
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
            # СКРЫТЬ ОКНО при ошибке
            self._hide_window_signal.emit()
            
            # Показать уведомление в трее вместо окна
            error_message = f"{t('errors.transcription_failed', error=str(error))}"
            self.tray_icon.show_message(
                t("tray.notification.error_occurred"),
                error_message,
                duration=5000  # 5 секунд
            )
            
            # Сбросить статус трея
            self.tray_icon.set_status(t("tray.tooltip.ready", hotkey=self.config.hotkey))
            
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
        elif self.config.ai_provider == "custom":
            return self.config.custom_api_key
        return None
    
    def _get_transcription_model_for_provider(self) -> Optional[str]:
        """
        Получает модель транскрипции для текущего провайдера.
        
        Приоритет:
        1. transcription_model из config (если указана)
        2. custom_model из config (для обратной совместимости)
        3. None (использовать дефолтную модель провайдера)
        
        Returns:
            Название модели или None для дефолтной
        """
        # Приоритет 1: transcription_model (новое поле)
        transcription_model = getattr(self.config, 'transcription_model', '')
        if transcription_model:
            return transcription_model
        
        # Приоритет 2: custom_model (старое поле для обратной совместимости)
        if self.config.custom_model:
            return self.config.custom_model
        
        # Приоритет 3: дефолтная модель провайдера
        return None
    
    def _show_settings(self) -> None:
        """Показывает окно настроек."""
        # Если окно уже существует и видимо - просто активируем его
        if self.settings_window is not None:
            if self.settings_window.isVisible():
                # Окно уже открыто - активируем его
                self.settings_window.raise_()
                self.settings_window.activateWindow()
                self.logger.info("Окно настроек уже открыто - активация")
                return
            else:
                # Окно существует но скрыто - удаляем его
                self.settings_window.deleteLater()
                self.settings_window = None
        
        # Создаем новое окно настроек
        from ui.settings_window import SettingsWindow
        
        # ВАЖНО: Передаем None как parent чтобы окно было независимым
        # Также передаем tray_icon для показа уведомлений и statistics_manager для статистики
        self.settings_window = SettingsWindow(
            self.config, 
            statistics_manager=self.statistics_manager,
            tray_icon=self.tray_icon, 
            parent=None  # Changed from self.floating_window to None
        )
        
        # Подключить сигнал сохранения настроек
        self.settings_window.settings_saved.connect(self._on_settings_saved)
        
        # Подключить сигнал закрытия окна для очистки ссылки
        self.settings_window.finished.connect(self._on_settings_window_closed)
        
        # Центрировать окно настроек на экране
        self.settings_window.center_on_screen()
        
        # Show and raise the window
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()
        
        self.logger.info("Окно настроек создано и показано")
    
    def _show_format_selection_dialog(self) -> None:
        """
        Показывает диалог выбора формата и обрабатывает результат.
        
        Создает FormatSelectionDialog, показывает его модально,
        сохраняет выбранный формат в StateManager и автоматически
        начинает запись.
        
        Requirements: 2.1, 3.1, 3.2, 10.4
        """
        try:
            # Если диалог уже открыт - просто поднять его на передний план
            if self._format_dialog_open and self.format_selection_dialog is not None:
                self.logger.info("Диалог уже открыт, поднимаем на передний план")
                self.format_selection_dialog.raise_()
                self.format_selection_dialog.activateWindow()
                return
            
            self.logger.info("Показ диалога выбора формата")
            
            # Import dialog and formatting config
            from ui.format_selection_dialog import FormatSelectionDialog
            from services.formatting_config import FormattingConfig
            from core.config_loader import get_config_loader
            
            # Load formatting configuration
            config_loader = get_config_loader()
            formatting_config = FormattingConfig.from_config(config_loader)
            
            # Create dialog (without parent to ensure it shows)
            self.format_selection_dialog = FormatSelectionDialog(formatting_config, parent=None)
            self._format_dialog_open = True
            self.logger.info("Диалог создан, показываем...")
            
            result = self.format_selection_dialog.exec()
            self.logger.info(f"Диалог закрыт с результатом: {result}")
            
            # Сбросить флаг
            self._format_dialog_open = False
            
            # Check if user selected a format (accepted dialog)
            if result == self.format_selection_dialog.DialogCode.Accepted:
                selected_format = self.format_selection_dialog.get_selected_format()
                
                if selected_format:
                    self.logger.info(f"Пользователь выбрал формат: {selected_format}")
                    
                    # Store selection in StateManager
                    self.state_manager.set_manual_format_selection(selected_format)
                    
                    # Show notification
                    format_name = selected_format.replace("_", " ").title()
                    if selected_format == "_fallback":
                        format_name = t("format_selection.universal_format")
                    
                    self.tray_icon.show_message(
                        t("format_selection.format_selected_title"),
                        t("format_selection.format_selected_message", format=format_name),
                        duration=3000
                    )
                    
                    # Automatically start recording
                    self.logger.info("Автоматический запуск записи после выбора формата")
                    QTimer.singleShot(100, lambda: self._hotkey_pressed_signal.emit())
                else:
                    self.logger.warning("Диалог принят, но формат не выбран")
            else:
                self.logger.info("Пользователь отменил выбор формата")
            
            # Очистить ссылку на диалог
            self.format_selection_dialog = None
                
        except Exception as e:
            self.logger.error(f"Ошибка при показе диалога выбора формата: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            self._format_dialog_open = False
            self.format_selection_dialog = None
            
            # Show error notification but don't block recording functionality
            self.tray_icon.show_message(
                t("common.error"),
                t("format_selection.dialog_error"),
                duration=5000
            )
    
    def _on_settings_window_closed(self) -> None:
        """Обработчик закрытия окна настроек."""
        self.logger.info("Окно настроек закрыто")
        # Очищаем ссылку на окно
        if self.settings_window is not None:
            self.settings_window.deleteLater()
            self.settings_window = None
    
    def _on_settings_saved(self):
        """
        Обработчик сохранения настроек.
        
        Перезагружает настройки и проверяет наличие API ключа.
        """
        # Перезагрузить настройки
        self._reload_settings()
        
        # Проверить что теперь есть API ключ
        if self.config.has_api_key():
            self._needs_setup = False
            self.tray_icon.set_status(t("tray.tooltip.ready", hotkey=self.config.hotkey))
            self.logger.info("API ключ установлен - приложение готово к работе")
        else:
            self.logger.warning("API ключ все еще не установлен")
    
    def _show_welcome_dialog(self):
        """Показывает приветственное окно при первом запуске."""
        from PyQt6.QtWidgets import QMessageBox
        
        msg = QMessageBox(self.floating_window)
        msg.setWindowTitle(t("tray.notification.welcome_dialog_title"))
        msg.setIcon(QMessageBox.Icon.Information)
        
        msg.setText(t("tray.notification.welcome_dialog_text"))
        
        msg.setInformativeText(t("tray.notification.welcome_dialog_info"))
        
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setDefaultButton(QMessageBox.StandardButton.Ok)
        
        # Применить темный стиль
        msg.setStyleSheet("""
            QMessageBox {
                background-color: rgba(30, 30, 30, 150);
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
        """)
        
        msg.exec()
    
    def _reload_settings(self):
        """
        Перезагружает настройки без перезапуска приложения.
        
        Применяет новые настройки для всех компонентов которые можно обновить
        без полного перезапуска.
        """
        try:
            self.logger.info("Перезагрузка настроек...")
            
            # Загрузить новую конфигурацию из config.jsonc
            new_config = Config.load_from_config()
            errors = new_config.validate()
            
            if errors:
                self.logger.error("Ошибки в новой конфигурации:")
                for error in errors:
                    self.logger.error(f"  - {error}")
                
                # Показать уведомление об ошибке
                self.tray_icon.show_message(
                    t("tray.notification.settings_error"),
                    t("tray.notification.settings_error_message"),
                    duration=5000
                )
                return
            
            # Сохранить старую конфигурацию для сравнения
            old_config = self.config
            self.config = new_config
            
            # Обновить компоненты которые можно обновить без перезапуска
            
            # 1. Обновить детектор тишины
            if (old_config.silence_threshold != new_config.silence_threshold or
                old_config.silence_duration != new_config.silence_duration):
                try:
                    self.silence_detector = SilenceDetector(
                        threshold=new_config.silence_threshold,
                        silence_duration=new_config.silence_duration
                    )
                    self.logger.info(f"Детектор тишины обновлен: threshold={new_config.silence_threshold}, duration={new_config.silence_duration}")
                except Exception as e:
                    self.logger.error(f"Ошибка обновления детектора тишины: {e}")
            
            # 2. Обновить горячую клавишу если изменилась
            if old_config.hotkey != new_config.hotkey:
                try:
                    self.logger.info(f"Обновление горячей клавиши: {old_config.hotkey} -> {new_config.hotkey}")
                    
                    # Отменить старую регистрацию
                    if self.hotkey_manager:
                        self.hotkey_manager.unregister_hotkey()
                        self.logger.info("Старая горячая клавиша отменена")
                    
                    # Зарегистрировать новую
                    self.hotkey_manager = HotkeyManager(self._on_hotkey_pressed)
                    success = self.hotkey_manager.register_hotkey(new_config.hotkey)
                    
                    if success:
                        # Зарегистрировать ESC снова
                        self.hotkey_manager.register_hotkey("esc", self._on_cancel_pressed)
                        self.logger.info(f"Горячая клавиша обновлена: {new_config.hotkey}")
                        
                        # Обновить отображение горячей клавиши в info panel
                        if self.floating_window.info_panel:
                            self.floating_window.info_panel.update_hotkey_display()
                            self.logger.info("Отображение горячей клавиши обновлено")
                    else:
                        self.logger.error(f"Не удалось зарегистрировать новую горячую клавишу: {new_config.hotkey}")
                        # Попытаться вернуть старую
                        self.hotkey_manager = HotkeyManager(self._on_hotkey_pressed)
                        self.hotkey_manager.register_hotkey(old_config.hotkey)
                        self.hotkey_manager.register_hotkey("esc", self._on_cancel_pressed)
                        self.config.hotkey = old_config.hotkey
                        
                        self.tray_icon.show_message(
                            t("tray.notification.hotkey_error"),
                            t("tray.notification.hotkey_error_message", new_hotkey=new_config.hotkey, old_hotkey=old_config.hotkey),
                            duration=5000
                        )
                        return
                        
                except Exception as e:
                    self.logger.error(f"Ошибка обновления горячей клавиши: {e}")
                    import traceback
                    self.logger.error(traceback.format_exc())
            
            # 3. Логировать изменения AI Provider
            if old_config.ai_provider != new_config.ai_provider:
                self.logger.info(f"AI Provider изменен: {old_config.ai_provider} -> {new_config.ai_provider}")
            
            # 4. Проверить API ключ для нового провайдера
            api_key = self._get_api_key_for_provider()
            if api_key:
                self.logger.info(f"API ключ для {new_config.ai_provider} загружен: {api_key[:10]}...")
            else:
                self.logger.warning(f"API ключ для провайдера {new_config.ai_provider} не найден!")
            
            # 5. Логировать изменение manual_stop
            if old_config.manual_stop != new_config.manual_stop:
                self.logger.info(f"Режим ручной остановки изменен: {old_config.manual_stop} -> {new_config.manual_stop}")
            
            # НЕ показываем уведомление здесь - оно уже показано в settings_window.py
            self.logger.info("Настройки успешно перезагружены")
            
        except Exception as e:
            self.logger.error(f"Ошибка перезагрузки настроек: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            
            # Показать уведомление об ошибке
            self.tray_icon.show_message(
                t("tray.notification.settings_apply_error"),
                t("tray.notification.settings_apply_error_message", error=str(e)),
                duration=5000
            )
    
    def _quit_app(self) -> None:
        """Выход из приложения."""
        self.logger.info("Запрос на выход из приложения (через меню трея)")
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
        
        # Проверить необходимость первоначальной настройки
        if self._needs_setup:
            self.logger.info("Первый запуск - требуется настройка API ключа")
            
            # Показать приветственное окно с инструкциями
            self._show_welcome_dialog()
            
            # Показать уведомление в трее
            self.tray_icon.show_message(
                t("tray.notification.welcome"),
                t("tray.notification.welcome_message"),
                duration=10000
            )
            
            # Обновить статус трея
            self.tray_icon.set_status("⚠️ Требуется настройка API ключа")
            
            # Открыть настройки
            QTimer.singleShot(500, self._show_settings)
            
        else:
            # Показать окно при запуске на 2 секунды - ВСЕГДА ПО ЦЕНТРУ
            self.floating_window.show_at_center(use_saved_position=False)
            self.floating_window.set_startup_message(t("tray.notification.launched"))
            
            # Установить флаг что идет инициализация
            self._startup_window_visible = True
            
            # Автоматически скрыть через 2 секунды и сбросить флаг
            def hide_startup_window():
                self._startup_window_visible = False
                self.floating_window.hide_with_animation()
                # Сбросить стиль ПОСЛЕ анимации (300ms + небольшая задержка)
                QTimer.singleShot(400, self.floating_window.reset_status_style)
            
            QTimer.singleShot(2000, hide_startup_window)
        
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
    # ВАЖНО: Установить AppUserModelID для Windows уведомлений
    # Это нужно сделать ДО создания QApplication
    try:
        import ctypes
        # Загрузить конфигурацию из config.jsonc для AppUserModelID
        from core.config import Config
        temp_config = Config.load_from_config()
        
        # Установить AppUserModelID для правильного отображения в Windows уведомлениях
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(temp_config.app_user_model_id)
    except Exception:
        pass  # Игнорируем ошибки на не-Windows системах
    
    # Проверить что приложение еще не запущено
    single_instance = SingleInstance("RapidWhisper")
    
    if single_instance.is_already_running():
        print("❌ RapidWhisper уже запущен!")
        print("Проверьте системный трей.")
        
        # Показать MessageBox на Windows
        try:
            from PyQt6.QtWidgets import QMessageBox
            temp_app = QApplication(sys.argv)
            QMessageBox.warning(
                None,
                t("errors.already_running_title"),
                t("errors.already_running_message"),
                QMessageBox.StandardButton.Ok
            )
        except Exception:
            pass
        
        sys.exit(1)
    
    # Захватить блокировку
    if not single_instance.acquire():
        print("❌ Не удалось захватить блокировку приложения")
        sys.exit(1)
    
    # Создать QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("RapidWhisper")
    app.setOrganizationName("RapidWhisper")
    app.setApplicationDisplayName("RapidWhisper")
    
    # ВАЖНО: Не закрывать приложение при закрытии последнего окна
    # Приложение работает в трее и должно закрываться только через меню
    app.setQuitOnLastWindowClosed(False)
    
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
        single_instance.release()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
