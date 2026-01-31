"""
Formatting Module for Transcription Formatting Feature.

This module handles automatic formatting of transcribed text based on
the active application window. It detects which application is currently
active and applies appropriate formatting rules using AI-powered text
transformation.
"""

from typing import Optional
from services.formatting_config import FormattingConfig
from services.window_monitor import WindowMonitor, WindowInfo
from utils.logger import get_logger

logger = get_logger()


# Application name patterns to format identifiers
FORMAT_MAPPINGS = {
    "notion": ["notion", "notion.exe", "notion.app"],
    "obsidian": ["obsidian", "obsidian.exe", "obsidian.app"],
    "markdown": [".md", ".markdown", "markdown"],  # Added "markdown" as app name
    "word": ["word", "winword.exe", "microsoft word", ".docx", ".doc"],
    "libreoffice": ["libreoffice", "soffice", "writer", ".odt"],
    "vscode": ["code", "vscode", "visual studio code"],
    "sublime": ["sublime", "sublime_text"],
    "notepad": ["notepad++", "notepad"],
}


def match_application_to_format(app_name: str, file_ext: str) -> Optional[str]:
    """
    Match detected application/file to a format type.
    
    Args:
        app_name: Active application name (lowercase)
        file_ext: Active file extension (with dot)
    
    Returns:
        Optional[str]: Format identifier or None if no match
    """
    app_lower = app_name.lower()
    
    for format_type, patterns in FORMAT_MAPPINGS.items():
        for pattern in patterns:
            if pattern.startswith("."):
                # File extension match
                if file_ext == pattern:
                    return format_type
            else:
                # Application name match
                if pattern in app_lower:
                    return format_type
    
    return None


class FormattingModule:
    """
    Handles automatic formatting of transcribed text based on active application.
    
    This module detects the active application window, matches it against
    configured formats, and applies appropriate formatting using AI.
    """
    
    def __init__(self, config_manager=None, ai_client_factory=None, window_monitor=None):
        """
        Initialize the formatting module.
        
        Args:
            config_manager: Configuration manager for loading settings, or FormattingConfig instance (optional)
            ai_client_factory: Factory for creating AI client instances (optional)
            window_monitor: Window monitoring component (optional)
        """
        # Accept either a FormattingConfig instance or load from environment
        if isinstance(config_manager, FormattingConfig):
            self.config = config_manager
        else:
            self.config = FormattingConfig.from_env()
        
        self.window_monitor = window_monitor or WindowMonitor.create()
        self.ai_client_factory = ai_client_factory
        
        logger.info(f"FormattingModule initialized: enabled={self.config.enabled}, "
                   f"provider={self.config.provider}, model={self.config.get_model()}")
    
    def should_format(self) -> bool:
        """
        Check if formatting is enabled in configuration.
        
        Returns:
            bool: True if formatting is enabled
        """
        return self.config.enabled
    
    def get_active_application_format(self) -> Optional[str]:
        """
        Detect active application and match against configured formats.
        
        Returns:
            Optional[str]: Format identifier (e.g., "notion", "obsidian", "markdown")
                          or None if no match
        """
        try:
            logger.info("  🔍 Определение активного окна...")
            
            # Get active window information
            window_info = self.window_monitor.get_active_window_info()
            
            if not window_info:
                logger.warning("  ⚠️ Не удалось получить информацию об активном окне")
                return None
            
            # Extract application name and file extension from window title
            app_name = window_info.process_name
            window_title = window_info.title
            
            logger.info(f"  📱 Активное окно:")
            logger.info(f"    - Процесс: {app_name}")
            logger.info(f"    - Заголовок: {window_title}")
            
            # Try to extract file extension from window title
            file_ext = ""
            if "." in window_title:
                parts = window_title.split(".")
                if len(parts) > 1:
                    # Get the last part after the last dot
                    potential_ext = parts[-1].split()[0]  # Take first word after dot
                    if len(potential_ext) <= 5:  # Reasonable extension length
                        file_ext = f".{potential_ext}"
            
            logger.info(f"    - Расширение файла: {file_ext if file_ext else 'не определено'}")
            
            # Match against configured applications
            logger.info(f"  🔎 Поиск соответствия формату...")
            format_type = match_application_to_format(app_name, file_ext)
            
            if format_type:
                logger.info(f"  ✅ Найдено соответствие: {format_type}")
                
                # Check if this format is in the configured applications list
                logger.info(f"  🔎 Проверка в списке настроенных приложений: {self.config.applications}")
                
                if format_type in self.config.applications:
                    logger.info(f"  ✅ Формат '{format_type}' найден в списке приложений")
                    return format_type
                
                # Check if app name matches any configured application
                for app in self.config.applications:
                    if app.lower() in [format_type, app_name.lower()]:
                        logger.info(f"  ✅ Приложение '{app}' соответствует формату '{format_type}'")
                        return format_type
                
                logger.warning(f"  ⚠️ Формат '{format_type}' не найден в списке настроенных приложений")
                return None
            
            logger.warning(f"  ⚠️ Не найдено соответствие для приложения '{app_name}' и расширения '{file_ext}'")
            return None
            
        except Exception as e:
            logger.error(f"  ❌ Ошибка при определении активного приложения: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def get_format_prompt(self, format_type: str) -> str:
        """
        Generate application-specific formatting prompt.
        
        DEPRECATED: This method is kept for backward compatibility.
        Prompts are now loaded from configuration via get_prompt_for_app().
        
        Args:
            format_type: Target format identifier
        
        Returns:
            str: System prompt for AI formatting (loaded from config)
        """
        # Load prompt from configuration instead of hardcoded prompts
        return self.config.get_prompt_for_app(format_type)
    
    def format_text(self, text: str, format_type: str) -> str:
        """
        Format text for the specified application type.
        
        Args:
            text: Original transcribed text
            format_type: Target format (e.g., "notion", "obsidian")
        
        Returns:
            str: Formatted text, or original text if formatting fails
        """
        try:
            logger.info(f"  🎨 Форматирование текста для формата: {format_type}")
            
            # Get application-specific prompt from config
            format_prompt = self.config.get_prompt_for_app(format_type)
            
            # If prompt is empty, it will use the universal default (handled in get_prompt_for_app)
            logger.info(f"  📝 Используется промпт для приложения '{format_type}'")
            logger.info(f"  📄 Промпт (первые 100 символов): {format_prompt[:100]}...")
            
            # Create AI client for formatting
            if self.ai_client_factory:
                ai_client = self.ai_client_factory.create(
                    provider=self.config.provider,
                    model=self.config.get_model()
                )
                logger.info(f"  🤖 Создан AI клиент через фабрику")
            else:
                # Use transcription client for formatting
                from services.transcription_client import TranscriptionClient
                import os
                
                logger.info(f"  🤖 Создание TranscriptionClient для провайдера: {self.config.provider}")
                
                # Get API key for the configured provider
                api_key = None
                base_url = None
                
                if self.config.provider == "groq":
                    api_key = os.getenv("GROQ_API_KEY")
                    logger.info(f"  🔑 Загружен GROQ_API_KEY: {api_key[:10] if api_key else 'НЕ НАЙДЕН'}...")
                elif self.config.provider == "openai":
                    api_key = os.getenv("OPENAI_API_KEY")
                    logger.info(f"  🔑 Загружен OPENAI_API_KEY: {api_key[:10] if api_key else 'НЕ НАЙДЕН'}...")
                elif self.config.provider == "glm":
                    api_key = os.getenv("GLM_API_KEY")
                    logger.info(f"  🔑 Загружен GLM_API_KEY: {api_key[:10] if api_key else 'НЕ НАЙДЕН'}...")
                elif self.config.provider == "custom":
                    api_key = os.getenv("CUSTOM_API_KEY")
                    base_url = os.getenv("CUSTOM_BASE_URL")
                    logger.info(f"  🔑 Загружен CUSTOM_API_KEY: {api_key[:10] if api_key else 'НЕ НАЙДЕН'}...")
                    logger.info(f"  🌐 CUSTOM_BASE_URL: {base_url}")
                
                if not api_key:
                    logger.error(f"  ❌ API ключ для провайдера {self.config.provider} не найден!")
                    return text
                
                # Create client
                ai_client = TranscriptionClient(
                    provider=self.config.provider,
                    api_key=api_key,
                    base_url=base_url,
                    model=self.config.get_model()
                )
                logger.info(f"  ✅ TranscriptionClient создан успешно")
            
            logger.info(f"  🚀 Отправка запроса на форматирование...")
            logger.info(f"    - Провайдер: {self.config.provider}")
            logger.info(f"    - Модель: {self.config.get_model()}")
            logger.info(f"    - Температура: {self.config.temperature}")
            
            # Use post_process_text method for formatting
            formatted_text = ai_client.post_process_text(
                text=text,
                provider=self.config.provider,
                model=self.config.get_model(),
                system_prompt=format_prompt,
                temperature=self.config.temperature
            )
            
            logger.info("  ✅ Текст успешно отформатирован")
            return formatted_text
            
        except Exception as e:
            logger.error(f"  ❌ Ошибка при форматировании текста: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Return original text on failure
            return text
    
    def process(self, text: str) -> str:
        """
        Main entry point for formatting pipeline.
        
        Args:
            text: Original transcribed text
        
        Returns:
            str: Formatted text if applicable, otherwise original text
        """
        logger.info("=" * 80)
        logger.info("*** НАЧАЛО ФОРМАТИРОВАНИЯ ТЕКСТА ***")
        logger.info("=" * 80)
        
        # Check if formatting is enabled
        logger.info(f"Проверка: форматирование включено = {self.config.enabled}")
        if not self.should_format():
            logger.info("❌ Форматирование отключено в настройках")
            logger.info("=" * 80)
            return text
        
        # Check if configuration is valid
        logger.info(f"Проверка конфигурации:")
        logger.info(f"  - Провайдер: {self.config.provider}")
        logger.info(f"  - Модель: {self.config.get_model()} {'(стандартная)' if not self.config.model else '(пользовательская)'}")
        logger.info(f"  - Приложения: {self.config.applications}")
        logger.info(f"  - Температура: {self.config.temperature}")
        logger.info(f"  - Системный промпт: {'Установлен' if self.config.system_prompt else 'Не установлен (используется стандартный)'}")
        
        if not self.config.is_valid():
            logger.warning("❌ Неверная конфигурация форматирования")
            logger.warning(f"  - Провайдер валиден: {self.config.provider in ['groq', 'openai', 'glm', 'custom']}")
            logger.warning(f"  - Приложения указаны: {bool(self.config.applications)}")
            logger.warning(f"  - Температура валидна: {0.0 <= self.config.temperature <= 1.0}")
            logger.info("=" * 80)
            return text
        
        logger.info("✅ Конфигурация валидна")
        
        # Get active application format
        logger.info("Определение активного приложения...")
        format_type = self.get_active_application_format()
        
        if not format_type:
            logger.info("❌ Активное приложение не соответствует настроенным форматам")
            logger.info("=" * 80)
            return text
        
        logger.info(f"✅ Определен формат: {format_type}")
        logger.info(f"Длина исходного текста: {len(text)} символов")
        logger.info(f"Исходный текст: {text[:100]}...")
        
        # Format the text
        formatted_text = self.format_text(text, format_type)
        
        logger.info(f"Длина отформатированного текста: {len(formatted_text)} символов")
        logger.info(f"Отформатированный текст: {formatted_text[:100]}...")
        logger.info("=" * 80)
        logger.info("*** КОНЕЦ ФОРМАТИРОВАНИЯ ТЕКСТА ***")
        logger.info("=" * 80)
        
        return formatted_text
