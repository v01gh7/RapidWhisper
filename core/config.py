"""
Модуль конфигурации приложения RapidWhisper.

Этот модуль предоставляет класс Config для загрузки и валидации
конфигурационных параметров из .env файла.
"""

import os
import locale
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv


def get_system_language() -> str:
    """
    Определяет язык системы и возвращает соответствующий код языка.
    
    Поддерживаемые языки:
    - en (English)
    - zh (Chinese)
    - hi (Hindi)
    - es (Spanish)
    - fr (French)
    - ar (Arabic)
    - bn (Bengali)
    - ru (Russian)
    - pt (Portuguese)
    - ur (Urdu)
    - id (Indonesian)
    - de (German)
    - ja (Japanese)
    - tr (Turkish)
    - ko (Korean)
    
    Returns:
        str: Код языка (например: "ru", "en", "zh")
             Если язык системы не поддерживается, возвращает "en" (английский)
    """
    try:
        # Получить язык системы (используем getlocale вместо deprecated getdefaultlocale)
        try:
            system_locale = locale.getlocale()[0]
        except Exception:
            # Если getlocale не работает, пробуем через переменные окружения
            system_locale = os.getenv('LANG') or os.getenv('LANGUAGE') or os.getenv('LC_ALL')
        
        if not system_locale:
            return "en"
        
        # Извлечь код языка (первые 2 символа)
        lang_code = str(system_locale).lower()[:2]
        
        # Маппинг поддерживаемых языков
        supported_languages = {
            "en": "en",  # English
            "zh": "zh",  # Chinese
            "hi": "hi",  # Hindi
            "es": "es",  # Spanish
            "fr": "fr",  # French
            "ar": "ar",  # Arabic
            "bn": "bn",  # Bengali
            "ru": "ru",  # Russian
            "pt": "pt",  # Portuguese
            "ur": "ur",  # Urdu
            "id": "id",  # Indonesian
            "de": "de",  # German
            "ja": "ja",  # Japanese
            "tr": "tr",  # Turkish
            "ko": "ko",  # Korean
        }
        
        # Вернуть код языка если поддерживается, иначе английский
        return supported_languages.get(lang_code, "en")
        
    except Exception:
        # В случае ошибки вернуть английский
        return "en"


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


def get_recordings_dir() -> Path:
    """
    Возвращает путь к директории с сохраненными записями.
    
    Проверяет настройку RECORDINGS_PATH в .env файле.
    Если не указана, использует путь по умолчанию.
    
    Returns:
        Path: Путь к директории recordings
    """
    # Проверить пользовательский путь в .env
    custom_path = os.getenv('RECORDINGS_PATH')
    
    if custom_path and custom_path.strip():
        recordings_dir = Path(custom_path).expanduser()
    else:
        # Путь по умолчанию
        recordings_dir = get_config_dir() / 'recordings'
    
    recordings_dir.mkdir(parents=True, exist_ok=True)
    return recordings_dir


def get_audio_recordings_dir() -> Path:
    """
    Возвращает путь к директории с аудио записями.
    
    Returns:
        Path: Путь к директории recordings/audio
    """
    audio_dir = get_recordings_dir() / 'audio'
    audio_dir.mkdir(parents=True, exist_ok=True)
    return audio_dir


def get_transcriptions_dir() -> Path:
    """
    Возвращает путь к директории с транскрипциями.
    
    Returns:
        Path: Путь к директории recordings/transcriptions
    """
    transcriptions_dir = get_recordings_dir() / 'transcriptions'
    transcriptions_dir.mkdir(parents=True, exist_ok=True)
    return transcriptions_dir


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
# Options: openai, groq, glm, custom
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

# Custom OpenAI-compatible API (for provider=custom)
# Examples: LM Studio, Ollama, vLLM, LocalAI, etc.
CUSTOM_API_KEY=your_api_key_here
CUSTOM_BASE_URL=http://localhost:1234/v1/
CUSTOM_MODEL=whisper-1

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

# ============================================
# About Section Links (OPTIONAL)
# ============================================
# GitHub repository URL
GITHUB_URL=https://github.com/yourusername/rapidwhisper

# Documentation URL
DOCS_URL=https://github.com/yourusername/rapidwhisper/tree/main/docs

# ============================================
# Window Position (OPTIONAL)
# ============================================
# Remember window position after dragging
# Default: true
# Options: true, false
REMEMBER_WINDOW_POSITION=true

# Window position preset
# Default: center
# Options: center, top_left, top_right, bottom_left, bottom_right, custom
WINDOW_POSITION_PRESET=center

# Window position (automatically saved when you drag the window)
# Leave empty for preset position
WINDOW_POSITION_X=
WINDOW_POSITION_Y=

# ============================================
# Recordings (OPTIONAL)
# ============================================
# Keep audio recordings after transcription
# Default: false
# Options: true, false
KEEP_RECORDINGS=false

# Custom path for recordings (leave empty for default)
# Default: %APPDATA%/RapidWhisper/recordings
# Example: D:/MyRecordings
RECORDINGS_PATH=

# Manual stop mode (disable automatic silence detection)
# When enabled, recording will only stop when you press the hotkey again
# Silence at the beginning and end will be automatically trimmed
# Default: false
# Options: true, false
MANUAL_STOP=false
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
        custom_api_key (str): API ключ для кастомного провайдера (опциональный)
        custom_base_url (str): URL для кастомного провайдера (опциональный)
        custom_model (str): Модель для кастомного провайдера (опциональный)
        ai_provider (str): Провайдер AI для транскрипции (openai, groq, glm, custom)
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
        self.custom_api_key: str = ""
        self.custom_base_url: str = ""
        self.custom_model: str = "whisper-1"
        
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
        
        # Параметры определения тишины
        self.silence_threshold: float = 0.02
        self.silence_duration: float = 1.5
        self.silence_padding: int = 650  # Паддинг при обрезке тишины в миллисекундах
        
        # Параметры логирования
        self.log_level: str = "INFO"
        self.log_file: str = "rapidwhisper.log"
        
        # Ссылки для раздела "О программе"
        self.github_url: str = "https://github.com/yourusername/rapidwhisper"
        self.docs_url: str = "https://github.com/yourusername/rapidwhisper/tree/main/docs"
        
        # Позиция окна
        self.remember_window_position: bool = True
        self.window_position_preset: str = "center"  # center, top_left, top_right, bottom_left, bottom_right, custom
        self.window_position_x: Optional[int] = None
        self.window_position_y: Optional[int] = None
        
        # Сохранение записей
        self.keep_recordings: bool = False  # По умолчанию удалять записи после транскрипции
        self.recordings_path: str = ""  # Пользовательский путь для записей (пустая строка = путь по умолчанию)
        
        # Ручная остановка записи
        self.manual_stop: bool = False  # По умолчанию автоматическая остановка по тишине
        
        # Постобработка транскрипции
        self.enable_post_processing: bool = False  # Включить дополнительную обработку текста
        self.post_processing_provider: str = "groq"  # Провайдер для постобработки (groq, openai, glm, llm)
        self.post_processing_model: str = "llama-3.3-70b-versatile"  # Модель для постобработки (по умолчанию Groq)
        self.post_processing_prompt: str = (
            "Ты - редактор текста. Твоя задача: исправить грамматические ошибки, "
            "добавить знаки препинания и улучшить читаемость текста. "
            "Сохрани оригинальный смысл и стиль. Не добавляй ничего лишнего. "
            "Верни только исправленный текст без комментариев."
        )
        self.glm_use_coding_plan: bool = False  # Использовать Coding Plan endpoint для GLM
        self.llm_base_url: str = "http://localhost:1234/v1/"  # Base URL для локальных LLM моделей
        self.llm_api_key: str = "local"  # API ключ для локальных LLM (может быть любым)
        
        # Язык интерфейса (для будущей локализации)
        self.interface_language: str = get_system_language()  # Язык интерфейса (определяется из системы)
    
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
        config.custom_api_key = os.getenv("CUSTOM_API_KEY", "")
        config.custom_base_url = os.getenv("CUSTOM_BASE_URL", "")
        config.custom_model = os.getenv("CUSTOM_MODEL", config.custom_model)
        
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
        
        try:
            config.silence_padding = int(os.getenv("SILENCE_PADDING", config.silence_padding))
        except ValueError:
            pass
        
        # Загрузить параметры логирования
        config.log_level = os.getenv("LOG_LEVEL", config.log_level).upper()
        config.log_file = os.getenv("LOG_FILE", config.log_file)
        
        # Загрузить ссылки
        config.github_url = os.getenv("GITHUB_URL", config.github_url)
        config.docs_url = os.getenv("DOCS_URL", config.docs_url)
        
        # Загрузить настройки позиции окна
        remember_pos = os.getenv("REMEMBER_WINDOW_POSITION", "true").lower()
        config.remember_window_position = remember_pos in ("true", "1", "yes")
        
        config.window_position_preset = os.getenv("WINDOW_POSITION_PRESET", "center")
        
        try:
            pos_x = os.getenv("WINDOW_POSITION_X")
            if pos_x:
                config.window_position_x = int(pos_x)
        except ValueError:
            pass
        
        try:
            pos_y = os.getenv("WINDOW_POSITION_Y")
            if pos_y:
                config.window_position_y = int(pos_y)
        except ValueError:
            pass
        
        # Загрузить настройки сохранения записей
        keep_rec = os.getenv("KEEP_RECORDINGS", "false").lower()
        config.keep_recordings = keep_rec in ("true", "1", "yes")
        
        config.recordings_path = os.getenv("RECORDINGS_PATH", "")
        
        # Загрузить настройки ручной остановки
        manual_stop = os.getenv("MANUAL_STOP", "false").lower()
        config.manual_stop = manual_stop in ("true", "1", "yes")
        
        # Загрузить настройки постобработки
        enable_pp = os.getenv("ENABLE_POST_PROCESSING", "false").lower()
        config.enable_post_processing = enable_pp in ("true", "1", "yes")
        
        config.post_processing_provider = os.getenv("POST_PROCESSING_PROVIDER", config.post_processing_provider).lower()
        config.post_processing_model = os.getenv("POST_PROCESSING_MODEL", config.post_processing_model)
        config.post_processing_prompt = os.getenv("POST_PROCESSING_PROMPT", config.post_processing_prompt)
        
        # GLM Coding Plan
        glm_coding_plan = os.getenv("GLM_USE_CODING_PLAN", "false").lower()
        config.glm_use_coding_plan = glm_coding_plan in ("true", "1", "yes")
        
        # LLM (локальные модели)
        config.llm_base_url = os.getenv("LLM_BASE_URL", config.llm_base_url)
        config.llm_api_key = os.getenv("LLM_API_KEY", config.llm_api_key)
        
        # Язык интерфейса (для будущей локализации)
        # Если язык не установлен в .env, определяем язык системы
        interface_lang_env = os.getenv("INTERFACE_LANGUAGE", "")
        if interface_lang_env:
            # Язык был установлен вручную в .env
            config.interface_language = interface_lang_env
        else:
            # Язык не установлен, определяем из системы
            config.interface_language = get_system_language()
        
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
        valid_providers = ["openai", "groq", "glm", "custom"]
        if self.ai_provider not in valid_providers:
            errors.append(f"AI_PROVIDER должен быть одним из {valid_providers}, получено: {self.ai_provider}")
        
        # Проверка API ключей в зависимости от провайдера
        if self.ai_provider == "openai" and not self.openai_api_key:
            errors.append("OPENAI_API_KEY не найден в .env файле. Получите ключ на https://platform.openai.com/api-keys")
        elif self.ai_provider == "groq" and not self.groq_api_key:
            errors.append("GROQ_API_KEY не найден в .env файле. Получите ключ на https://console.groq.com/keys")
        elif self.ai_provider == "glm" and not self.glm_api_key:
            errors.append("GLM_API_KEY не найден в .env файле. Получите ключ на https://open.bigmodel.cn/")
        elif self.ai_provider == "custom":
            if not self.custom_api_key:
                errors.append("CUSTOM_API_KEY не найден в .env файле для custom провайдера")
            if not self.custom_base_url:
                errors.append("CUSTOM_BASE_URL не найден в .env файле для custom провайдера")
        
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
        elif self.ai_provider == "custom":
            return bool(self.custom_api_key and self.custom_base_url)
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
