"""
Аудио движок для записи и обработки звука с микрофона.

Этот модуль реализует AudioEngine - компонент для записи аудио с микрофона,
вычисления громкости (RMS) и сохранения записи в WAV файл.

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
"""

import wave
import time
import tempfile
from typing import List, Optional
import pyaudio
import numpy as np

from utils.exceptions import (
    MicrophoneUnavailableError,
    RecordingTooShortError,
    EmptyRecordingError,
    AudioDeviceError
)


class AudioEngine:
    """
    Движок для записи и обработки аудио с микрофона.
    
    Реализует запись аудио в формате WAV (16000 Hz, моно, int16),
    вычисление RMS громкости в реальном времени и сохранение
    записи во временный файл.
    
    Attributes:
        sample_rate: Частота дискретизации (16000 Hz)
        channels: Количество каналов (1 - моно)
        chunk_size: Размер аудио чанка в фреймах (1024)
        audio_buffer: Буфер для хранения записанных аудио данных
        stream: Поток PyAudio для записи
        is_recording: Флаг активной записи
        pyaudio_instance: Экземпляр PyAudio
    """
    
    def __init__(self):
        """
        Инициализирует AudioEngine с параметрами для записи речи.
        
        Параметры оптимизированы для распознавания речи:
        - 16000 Hz - стандартная частота для речевых моделей
        - Моно - достаточно для речи, экономит память
        - int16 - 16-битный формат, баланс качества и размера
        """
        # Параметры записи (Requirements 3.2, 3.3)
        self.sample_rate: int = 16000  # Hz
        self.channels: int = 1  # Моно
        self.chunk_size: int = 1024  # Фреймов
        self.format = pyaudio.paInt16  # 16-bit
        
        # Буфер для аудио данных (Requirement 3.4)
        self.audio_buffer: List[bytes] = []
        
        # Состояние записи
        self.stream: Optional[pyaudio.Stream] = None
        self.is_recording: bool = False
        self.pyaudio_instance: Optional[pyaudio.PyAudio] = None
        
        # Текущее RMS значение
        self._current_rms: float = 0.0
        
    def start_recording(self) -> None:
        """
        Начинает запись с микрофона по умолчанию.
        
        Открывает аудио поток и начинает буферизацию данных.
        Использует callback для обработки аудио в реальном времени.
        
        Raises:
            MicrophoneUnavailableError: Если микрофон недоступен или занят
            AudioDeviceError: Если произошла другая ошибка аудио устройства
            
        Requirements: 3.1
        """
        if self.is_recording:
            return
        
        try:
            # Инициализировать PyAudio
            self.pyaudio_instance = pyaudio.PyAudio()
            
            # Очистить буфер перед новой записью
            self.audio_buffer = []
            self._current_rms = 0.0
            
            # Открыть поток для записи
            self.stream = self.pyaudio_instance.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            # Начать запись
            self.stream.start_stream()
            self.is_recording = True
            
        except OSError as e:
            # Обработка ошибок доступа к микрофону
            error_msg = str(e).lower()
            if "device unavailable" in error_msg or "invalid device" in error_msg:
                raise MicrophoneUnavailableError(
                    f"Микрофон недоступен: {e}"
                )
            else:
                raise AudioDeviceError(str(e))
                
        except Exception as e:
            # Другие непредвиденные ошибки
            raise AudioDeviceError(error=f"Не удалось начать запись: {e}")
    
    def stop_recording(self) -> str:
        """
        Останавливает запись и сохраняет аудио в WAV файл.
        
        Закрывает аудио поток, освобождает ресурсы микрофона
        и сохраняет записанные данные во временный файл.
        
        Returns:
            Путь к сохраненному WAV файлу
            
        Raises:
            EmptyRecordingError: Если буфер пустой
            RecordingTooShortError: Если запись короче 0.5 секунды
            
        Requirements: 3.5
        """
        if not self.is_recording:
            from utils.exceptions import RapidWhisperError
            raise RapidWhisperError(
                message="Запись не активна",
                translation_key="errors.recording_not_active"
            )
        
        try:
            # Остановить и закрыть поток
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            # Закрыть PyAudio
            if self.pyaudio_instance:
                self.pyaudio_instance.terminate()
                self.pyaudio_instance = None
            
            self.is_recording = False
            
            # Проверить, что буфер не пустой
            if not self.audio_buffer:
                raise EmptyRecordingError()
            
            # Вычислить длительность записи
            total_frames = sum(len(chunk) for chunk in self.audio_buffer) // 2  # 2 bytes per sample
            duration = total_frames / self.sample_rate
            
            # Проверить минимальную длительность (0.5 секунды)
            if duration < 0.5:
                raise RecordingTooShortError(duration)
            
            # Сохранить в временный файл
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.wav',
                delete=False
            )
            filepath = temp_file.name
            temp_file.close()
            
            self._save_to_wav(filepath)
            
            return filepath
            
        except (EmptyRecordingError, RecordingTooShortError):
            # Пробросить ошибки валидации
            raise
            
        except Exception as e:
            raise AudioDeviceError(error=f"Ошибка при остановке записи: {e}")
    
    def get_current_rms(self) -> float:
        """
        Возвращает текущее RMS значение громкости.
        
        RMS (Root Mean Square) - среднеквадратичное значение амплитуды,
        нормализованное в диапазон [0.0, 1.0]. Используется для
        визуализации звуковой волны и определения тишины.
        
        Returns:
            RMS значение в диапазоне [0.0, 1.0]
            
        Requirements: 4.3
        """
        return self._current_rms
    
    def _audio_callback(
        self,
        in_data: bytes,
        frame_count: int,
        time_info: dict,
        status: int
    ) -> tuple:
        """
        Callback для обработки аудио потока в реальном времени.
        
        Вызывается PyAudio для каждого чанка аудио данных.
        Добавляет данные в буфер и вычисляет RMS громкости.
        
        Args:
            in_data: Сырые аудио данные (bytes)
            frame_count: Количество фреймов
            time_info: Информация о времени
            status: Статус потока
            
        Returns:
            Tuple (данные, флаг продолжения)
            
        Requirements: 3.4, 4.3
        """
        # Добавить данные в буфер (Requirement 3.4)
        self.audio_buffer.append(in_data)
        
        # Вычислить RMS для визуализации (Requirement 4.3)
        self._current_rms = self._calculate_rms(in_data)
        
        # Продолжить запись
        return (in_data, pyaudio.paContinue)
    
    def _calculate_rms(self, audio_data: bytes) -> float:
        """
        Вычисляет RMS (Root Mean Square) громкости аудио данных.
        
        RMS = sqrt(mean(samples^2)) / 32768.0
        
        Формула вычисляет среднеквадратичное значение амплитуды
        и нормализует его в диапазон [0.0, 1.0] делением на
        максимальное значение int16 (32768).
        
        Args:
            audio_data: Сырые аудио данные в формате int16
            
        Returns:
            RMS значение в диапазоне [0.0, 1.0]
            
        Requirements: 4.3
        """
        # Преобразовать bytes в numpy array int16
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        
        # Вычислить RMS: sqrt(mean(samples^2)) / 32768.0
        if len(audio_array) == 0:
            return 0.0
        
        # Преобразовать в float для точных вычислений
        audio_float = audio_array.astype(np.float64)
        
        # Вычислить среднеквадратичное значение
        rms = np.sqrt(np.mean(audio_float ** 2))
        
        # Нормализовать в диапазон [0.0, 1.0]
        normalized_rms = rms / 32768.0
        
        return float(normalized_rms)
    
    def _save_to_wav(self, filepath: str) -> None:
        """
        Сохраняет аудио буфер в WAV файл.
        
        Создает WAV файл с параметрами:
        - 16000 Hz sample rate
        - 1 канал (моно)
        - 16-bit (2 bytes per sample)
        
        Args:
            filepath: Путь для сохранения WAV файла
            
        Raises:
            AudioDeviceError: Если не удалось сохранить файл
            
        Requirements: 3.2, 3.5
        """
        try:
            with wave.open(filepath, 'wb') as wav_file:
                # Установить параметры WAV файла
                wav_file.setnchannels(self.channels)  # Моно
                wav_file.setsampwidth(2)  # 2 bytes = 16 bit
                wav_file.setframerate(self.sample_rate)  # 16000 Hz
                
                # Записать все данные из буфера
                for chunk in self.audio_buffer:
                    wav_file.writeframes(chunk)
                    
        except Exception as e:
            raise AudioDeviceError(error=f"Не удалось сохранить WAV файл: {e}")
    
    def cleanup(self) -> None:
        """
        Освобождает ресурсы аудио движка.
        
        Останавливает запись (если активна) и закрывает все потоки.
        Должен вызываться при завершении работы приложения.
        
        Requirements: 9.6, 12.2
        """
        if self.is_recording:
            try:
                if self.stream:
                    self.stream.stop_stream()
                    self.stream.close()
                    self.stream = None
                
                if self.pyaudio_instance:
                    self.pyaudio_instance.terminate()
                    self.pyaudio_instance = None
                    
                self.is_recording = False
                
            except Exception:
                # Игнорировать ошибки при очистке
                pass
        
        # Очистить буфер
        self.audio_buffer = []
        self._current_rms = 0.0



from PyQt6.QtCore import QThread, pyqtSignal


class AudioRecordingThread(QThread):
    """
    Поток для записи аудио в фоновом режиме.
    
    Наследуется от QThread для неблокирующей записи аудио.
    Периодически отправляет сигналы с RMS значениями для визуализации
    и сигнал при обнаружении тишины.
    
    Signals:
        rms_updated: Сигнал с текущим RMS значением (float)
        recording_stopped: Сигнал при остановке записи с путем к файлу (str)
        recording_error: Сигнал при ошибке записи (Exception)
        silence_detected: Сигнал при обнаружении тишины
    
    Requirements: 4.7, 9.1
    """
    
    # Сигналы
    rms_updated = pyqtSignal(float)  # RMS значение для визуализации
    recording_stopped = pyqtSignal(str)  # Путь к сохраненному файлу
    recording_error = pyqtSignal(Exception)  # Ошибка записи
    silence_detected = pyqtSignal()  # Обнаружена тишина
    
    def __init__(self, silence_detector=None, enable_silence_detection=True):
        """
        Инициализирует поток записи.
        
        Args:
            silence_detector: Экземпляр SilenceDetector для определения тишины
            enable_silence_detection: Включить автоматическое определение тишины (по умолчанию True)
        """
        super().__init__()
        self.audio_engine = AudioEngine()
        self.silence_detector = silence_detector
        self.enable_silence_detection = enable_silence_detection
        self._should_stop = False
        self._cancelled = False  # Флаг отмены (не сохранять файл)
        self._update_interval = 0.05  # 50ms между обновлениями RMS
    
    def run(self) -> None:
        """
        Главный цикл потока записи.
        
        Запускает запись, периодически обновляет RMS значения
        и проверяет условие остановки (тишина или ручная остановка).
        
        Requirements: 4.7, 9.1
        """
        try:
            # Начать запись
            self.audio_engine.start_recording()
            
            # Главный цикл записи
            while not self._should_stop:
                # Получить текущее RMS значение
                rms = self.audio_engine.get_current_rms()
                
                # Отправить сигнал для визуализации
                self.rms_updated.emit(rms)
                
                # Проверить тишину если детектор доступен И включено определение тишины
                if self.silence_detector and self.enable_silence_detection:
                    current_time = time.time()
                    is_silent = self.silence_detector.update(rms, current_time)
                    
                    if is_silent:
                        # Обнаружена тишина - отправить сигнал
                        self.silence_detected.emit()
                        break
                
                # Небольшая задержка между обновлениями
                time.sleep(self._update_interval)
            
            # Остановить запись и сохранить файл ТОЛЬКО если не отменено
            if not self._cancelled:
                filepath = self.audio_engine.stop_recording()
                self.recording_stopped.emit(filepath)
            else:
                # Просто остановить без сохранения
                self.audio_engine.cleanup()
            
        except Exception as e:
            # Отправить сигнал об ошибке
            self.recording_error.emit(e)
            
        finally:
            # Очистить ресурсы
            self.audio_engine.cleanup()
    
    def stop(self) -> None:
        """
        Останавливает запись.
        
        Устанавливает флаг остановки, который прерывает главный цикл.
        """
        self._should_stop = True
    
    def cancel(self) -> None:
        """
        Отменяет запись без сохранения файла.
        
        Устанавливает флаги остановки и отмены.
        """
        self._cancelled = True
        self._should_stop = True
