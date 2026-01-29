"""
Модуль конфигурации приложения RapidWhisper.

Этот модуль предоставляет класс Config для загрузки и валидации
конфигурационных параметров из .env файла.
"""

import os
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv


def get_config_dir() -> Path:
    """
    Возвращает путь к директории конфигурации приложения.
    
    Для Windows: %APPDATA%/RapidWhisper
    Для macOS: ~/Library/Application Support/RapidWhisper
    Для Linux: ~/.config/RapidWhisper
    
    Returns:
        Path: Путь к директории конфигурации
    """
    if os.name == 'nt':  # Windows
        base_dir = Path(os.getenv('APPDATA', '~'))
    elif os.sys.platform == 'darwin':  # macOS
        base_dir = Path.home() / 'Library' / 'Application Support'
    else:  # Linux
        base_dir = Path.home() / '.config'
    
    config_dir = base_dir / 'RapidWhisper'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_env_path() -> Path:
    """
    Возвращает путь к файлу .env.
    
    Сначала проверяет текущую директорию (для разработки),
    затем директорию конфигурации (для production).
    
    Returns:
        Path: Путь к файлу .env
    """
    # Для разработки - проверяем текущую директорию
    local_env = Path('.env')
    if local_env.exists():
        return local_env
    
    # Для production - используем AppData
    config_dir = get_config_dir()
    return config_dir / '.env'


def create_default_env() -> None:
    """
    Создает файл .env с настройками по умолчанию если его нет.
    """
    env_path = get_env_path()
    
    if not env_path.exists():
        default_content = """# ============================================
# AI Provider Configuration (REQUIRED)
# ============================================
# AI provider for transcription
# Default: groq (free and fast!)
# Options: openai, groq, glm
AI_PROVIDER=groq

# OpenAI API Key (for provider=openai)
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=

# Groq API Key (for provider=groq)
# Get from: https://console.groq.com/keys
GROQ_API_KEY=

# GLM API Key (for provider=glm)
# Get from: https://open.bigmodel.cn/usercenter/apikeys
GLM_API_KEY=

# ============================================
# Application Settings (OPTIONAL)
# ============================================
# Global hotkey for activating the application
# Default: ctrl+space
HOTKEY=ctrl+space

# Silence detection threshold (RMS value)
# Default: 0.02
# Range: 0.01 - 0.1 (lower = more sensitive)
SILENCE_THRESHOLD=0.02

# Silence duration before stopping recording (seconds)
# Default: 1.5
# Range: 0.5 - 5.0
SILENCE_DURATION=1.5

# Auto-hide delay after displaying result (seconds)
# Default: 2.5
# Range: 1.0 - 10.0
AUTO_HIDE_DELAY=2.5
"""
        env_path.write_text(default_content, encoding='utf-8')


class Config:
    """
    Конфигурация приложения RapidWhisper.
    
    Загружает параметры из .env файла и предоставляет значения по умолчанию
    для всех опциональных параметров. Поддерживает валидацию обязательных
    параметров.
    
    Attributes:
        glm_api_key (str): API ключ для Zhipu GLM API (опциональный)
        openai_api_key (str): API ключ для OpenAI API (опциональный)
        groq_api_key (str): API ключ для Groq API (опциональный)
        ai_provider (str): Провайдер AI для транскрипции (openai, groq, glm)
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
        # AI Provider параметры
        self.ai_provider: str = "groq"  # Groq по умолчанию (бесплатный и быстрый)
        self.glm_api_key: str = ""
        self.openai_api_key: str = ""
        self.groq_api_key: str = ""
        
        # Параметры приложения
        self.hotkey: str = "ctrl+space"
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
            env_path: Путь к .env файлу. Если None, использует get_env_path().
        
        Returns:
            Config: Объект конфигурации с загруженными параметрами.
        
        Example:
            >>> config = Config.load_from_env()
            >>> print(config.hotkey)
            'ctrl+space'
        """
        # Создать .env если его нет
        create_default_env()
        
        # Определить путь к .env
        if env_path is None:
            env_path = str(get_env_path())
        
        # Загрузить переменные окружения из .env файла
        load_dotenv(env_path, override=True)
        
        # Создать объект конфигурации
        config = Config()
        
        # Загрузить AI Provider параметры
        config.ai_provider = os.getenv("AI_PROVIDER", config.ai_provider).lower()
        config.glm_api_key = os.getenv("GLM_API_KEY", "")
        config.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        config.groq_api_key = os.getenv("GROQ_API_KEY", "")
        
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
        
        # Проверка AI Provider
        valid_providers = ["openai", "groq", "glm"]
        if self.ai_provider not in valid_providers:
            errors.append(f"AI_PROVIDER должен быть одним из {valid_providers}, получено: {self.ai_provider}")
        
        # Проверка API ключей в зависимости от провайдера
        if self.ai_provider == "openai" and not self.openai_api_key:
            errors.append("OPENAI_API_KEY не найден в .env файле. Получите ключ на https://platform.openai.com/api-keys")
        elif self.ai_provider == "groq" and not self.groq_api_key:
            errors.append("GROQ_API_KEY не найден в .env файле. Получите ключ на https://console.groq.com/keys")
        elif self.ai_provider == "glm" and not self.glm_api_key:
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
    
    def has_api_key(self) -> bool:
        """
        Проверяет наличие API ключа для текущего провайдера.
        
        Returns:
            bool: True если ключ установлен, False иначе
        """
        if self.ai_provider == "openai":
            return bool(self.openai_api_key)
        elif self.ai_provider == "groq":
            return bool(self.groq_api_key)
        elif self.ai_provider == "glm":
            return bool(self.glm_api_key)
        return False
    
    def __repr__(self) -> str:
        """Возвращает строковое представление конфигурации."""
        return (
            f"Config(ai_provider='{self.ai_provider}', "
            f"hotkey='{self.hotkey}', "
            f"silence_threshold={self.silence_threshold}, "
            f"silence_duration={self.silence_duration}, "
            f"auto_hide_delay={self.auto_hide_delay}, "
            f"window_size=({self.window_width}x{self.window_height}), "
            f"sample_rate={self.sample_rate}, "
            f"log_level='{self.log_level}')"
        )
