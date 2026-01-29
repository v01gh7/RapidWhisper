"""
Модуль конфигурации приложения RapidWhisper.

Этот модуль предоставляет класс Config для загрузки и валидации
конфигурационных параметров из .env файла.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv


class Config:
    """
    Конфигурация приложения RapidWhisper.
    
    Загружает параметры из .env файла и предоставляет значения по умолчанию
    для всех опциональных параметров. Поддерживает валидацию обязательных
    параметров.
    
    Attributes:
        glm_api_key (str): API ключ для Zhipu GLM API (обязательный)
        hotkey (str): Глобальная горячая клавиша для активации приложения
        silence_threshold (float): Порог RMS для определения тишины
        silence_duration (float): Длительность тишины в секундах для остановки записи
        auto_hide_delay (float): Задержка автоматического скрытия окна в секундах
        window_width (int): Ширина плавающего окна в пикселях
        window_height (int): Высота плавающего окна в пикселях
        sample_rate (int): Частота дискретизации аудио в Гц
        chunk_size (int): Размер аудио чанка в фреймах
        log_level (str): Уровень логирования
        log_file (str): Путь к файлу логов
    """
    
    def __init__(self):
        """Инициализирует конфигурацию со значениями по умолчанию."""
        # Обязательные параметры
        self.glm_api_key: str = ""
        
        # Параметры приложения
        self.hotkey: str = "F1"
        self.silence_threshold: float = 0.02
        self.silence_duration: float = 1.5
        self.auto_hide_delay: float = 2.5
        
        # Параметры окна
        self.window_width: int = 400
        self.window_height: int = 120
        
        # Параметры аудио
        self.sample_rate: int = 16000
        self.chunk_size: int = 1024
        
        # Параметры логирования
        self.log_level: str = "INFO"
        self.log_file: str = "rapidwhisper.log"
    
    @staticmethod
    def load_from_env(env_path: Optional[str] = None) -> 'Config':
        """
        Загружает конфигурацию из .env файла.
        
        Читает параметры из .env файла и создает объект Config с загруженными
        значениями. Если параметр отсутствует в .env файле, используется
        значение по умолчанию.
        
        Args:
            env_path: Путь к .env файлу. Если None, ищет .env в текущей директории.
        
        Returns:
            Config: Объект конфигурации с загруженными параметрами.
        
        Example:
            >>> config = Config.load_from_env()
            >>> print(config.hotkey)
            'F1'
        """
        # Загрузить переменные окружения из .env файла
        if env_path:
            load_dotenv(env_path, override=True)
        else:
            load_dotenv(override=True)
        
        # Создать объект конфигурации
        config = Config()
        
        # Загрузить обязательные параметры
        config.glm_api_key = os.getenv("GLM_API_KEY", "")
        
        # Загрузить параметры приложения
        config.hotkey = os.getenv("HOTKEY", config.hotkey)
        
        # Загрузить числовые параметры с обработкой ошибок
        try:
            value = float(os.getenv("SILENCE_THRESHOLD", config.silence_threshold))
            # Check for NaN and inf
            if not (value != value or value == float('inf') or value == float('-inf')):
                config.silence_threshold = value
        except (ValueError, TypeError):
            pass  # Использовать значение по умолчанию
        
        try:
            value = float(os.getenv("SILENCE_DURATION", config.silence_duration))
            if not (value != value or value == float('inf') or value == float('-inf')):
                config.silence_duration = value
        except (ValueError, TypeError):
            pass
        
        try:
            value = float(os.getenv("AUTO_HIDE_DELAY", config.auto_hide_delay))
            if not (value != value or value == float('inf') or value == float('-inf')):
                config.auto_hide_delay = value
        except (ValueError, TypeError):
            pass
        
        # Загрузить параметры окна
        try:
            config.window_width = int(os.getenv("WINDOW_WIDTH", config.window_width))
        except ValueError:
            pass
        
        try:
            config.window_height = int(os.getenv("WINDOW_HEIGHT", config.window_height))
        except ValueError:
            pass
        
        # Загрузить параметры аудио
        try:
            config.sample_rate = int(os.getenv("SAMPLE_RATE", config.sample_rate))
        except ValueError:
            pass
        
        try:
            config.chunk_size = int(os.getenv("CHUNK_SIZE", config.chunk_size))
        except ValueError:
            pass
        
        # Загрузить параметры логирования
        config.log_level = os.getenv("LOG_LEVEL", config.log_level).upper()
        config.log_file = os.getenv("LOG_FILE", config.log_file)
        
        return config
    
    def validate(self) -> List[str]:
        """
        Валидирует конфигурацию и возвращает список ошибок.
        
        Проверяет обязательные параметры и корректность значений всех параметров.
        Если конфигурация валидна, возвращает пустой список.
        
        Returns:
            List[str]: Список сообщений об ошибках. Пустой список, если ошибок нет.
        
        Example:
            >>> config = Config()
            >>> errors = config.validate()
            >>> if errors:
            ...     print("Ошибки конфигурации:", errors)
        """
        errors: List[str] = []
        
        # Проверка обязательных параметров
        if not self.glm_api_key:
            errors.append("GLM_API_KEY не найден в .env файле. Получите ключ на https://open.bigmodel.cn/")
        
        # Проверка корректности значений
        if self.silence_threshold < 0.01 or self.silence_threshold > 0.1:
            errors.append(f"SILENCE_THRESHOLD должен быть в диапазоне 0.01-0.1, получено: {self.silence_threshold}")
        
        if self.silence_duration < 0.5 or self.silence_duration > 5.0:
            errors.append(f"SILENCE_DURATION должен быть в диапазоне 0.5-5.0, получено: {self.silence_duration}")
        
        if self.auto_hide_delay < 1.0 or self.auto_hide_delay > 10.0:
            errors.append(f"AUTO_HIDE_DELAY должен быть в диапазоне 1.0-10.0, получено: {self.auto_hide_delay}")
        
        if self.window_width < 200 or self.window_width > 1000:
            errors.append(f"WINDOW_WIDTH должен быть в диапазоне 200-1000, получено: {self.window_width}")
        
        if self.window_height < 80 or self.window_height > 500:
            errors.append(f"WINDOW_HEIGHT должен быть в диапазоне 80-500, получено: {self.window_height}")
        
        if self.sample_rate not in [16000, 44100, 48000]:
            errors.append(f"SAMPLE_RATE должен быть 16000, 44100 или 48000, получено: {self.sample_rate}")
        
        if self.chunk_size < 256 or self.chunk_size > 4096:
            errors.append(f"CHUNK_SIZE должен быть в диапазоне 256-4096, получено: {self.chunk_size}")
        
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            errors.append(f"LOG_LEVEL должен быть одним из {valid_log_levels}, получено: {self.log_level}")
        
        return errors
    
    def __repr__(self) -> str:
        """Возвращает строковое представление конфигурации."""
        return (
            f"Config(hotkey='{self.hotkey}', "
            f"silence_threshold={self.silence_threshold}, "
            f"silence_duration={self.silence_duration}, "
            f"auto_hide_delay={self.auto_hide_delay}, "
            f"window_size=({self.window_width}x{self.window_height}), "
            f"sample_rate={self.sample_rate}, "
            f"log_level='{self.log_level}')"
        )
