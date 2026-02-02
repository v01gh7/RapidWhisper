"""
Модели данных для RapidWhisper.

Этот модуль содержит dataclass модели для представления аудио данных,
результатов транскрипции и информации об ошибках.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import wave
import os


@dataclass
class AudioData:
    """Данные записанного аудио.
    
    Attributes:
        sample_rate: Частота дискретизации в Гц (обычно 16000)
        channels: Количество аудио каналов (1 для моно, 2 для стерео)
        frames: Сырые аудио данные в байтах
        duration: Длительность аудио в секундах
        rms_values: Список RMS значений громкости для визуализации
    """
    sample_rate: int
    channels: int
    frames: bytes
    duration: float
    rms_values: List[float]
    
    def save_to_file(self, filepath: str) -> None:
        """Сохраняет аудио в WAV файл.
        
        Сохраняет аудио данные в формате WAV с параметрами:
        - Частота дискретизации: 16000 Hz
        - Каналы: моно (1)
        - Формат: int16 (2 байта на сэмпл)
        
        Args:
            filepath: Путь к файлу для сохранения (должен заканчиваться на .wav)
            
        Raises:
            OSError: Если не удается создать или записать файл
            ValueError: Если путь к файлу некорректен
        """
        if not filepath:
            from utils.exceptions import RapidWhisperError
            raise RapidWhisperError(
                message="Путь к файлу не может быть пустым",
                translation_key="errors.empty_filepath"
            )
        
        # Создать директорию если не существует
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Сохранить в WAV формате
        with wave.open(filepath, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Моно
            wav_file.setsampwidth(2)  # 2 байта = int16
            wav_file.setframerate(16000)  # 16000 Hz
            wav_file.writeframes(self.frames)


@dataclass
class TranscriptionResult:
    """Результат транскрипции речи в текст.
    
    Attributes:
        text: Распознанный текст
        duration: Длительность обработки в секундах
        language: Определенный язык (опционально)
        confidence: Уровень уверенности модели от 0.0 до 1.0 (опционально)
    """
    text: str
    duration: float
    language: Optional[str] = None
    confidence: Optional[float] = None
    
    def get_preview(self, max_length: int = 100) -> str:
        """Возвращает превью текста для отображения.
        
        Усекает текст до указанной максимальной длины для отображения
        в пользовательском интерфейсе. Если текст короче max_length,
        возвращается полный текст.
        
        Args:
            max_length: Максимальная длина превью в символах (по умолчанию 100)
            
        Returns:
            Усеченный текст длиной не более max_length символов
            
        Raises:
            ValueError: Если max_length меньше или равен 0
        """
        if max_length <= 0:
            from utils.exceptions import RapidWhisperError
            raise RapidWhisperError(
                message="max_length должен быть положительным числом",
                translation_key="errors.invalid_max_length"
            )
        
        if len(self.text) <= max_length:
            return self.text
        
        return self.text[:max_length]


@dataclass
class ErrorInfo:
    """Информация об ошибке для логирования и отображения.
    
    Attributes:
        error_type: Тип ошибки (имя класса исключения)
        message: Техническое сообщение об ошибке для разработчиков
        user_message: Понятное сообщение для пользователя
        timestamp: Время возникновения ошибки
    """
    error_type: str
    message: str
    user_message: str
    timestamp: datetime
    
    def log_to_file(self, log_path: str) -> None:
        """Записывает ошибку в лог файл.
        
        Добавляет информацию об ошибке в конец лог файла в формате:
        [TIMESTAMP] ERROR_TYPE: message (user_message)
        
        Если файл не существует, он будет создан. Если директория
        не существует, она будет создана автоматически.
        
        Args:
            log_path: Путь к лог файлу
            
        Raises:
            OSError: Если не удается создать или записать в файл
            ValueError: Если путь к файлу некорректен
        """
        if not log_path:
            raise ValueError("Путь к лог файлу не может быть пустым")
        
        # Создать директорию если не существует
        directory = os.path.dirname(log_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Форматировать сообщение об ошибке
        timestamp_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        log_message = (
            f"[{timestamp_str}] {self.error_type}: {self.message} "
            f"(user_message: {self.user_message})\n"
        )
        
        # Добавить в лог файл
        with open(log_path, 'a', encoding='utf-8') as log_file:
            log_file.write(log_message)
