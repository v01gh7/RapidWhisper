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


# List of common browser process names
BROWSER_PROCESSES = [
    "chrome", "chrome.exe",
    "firefox", "firefox.exe",
    "msedge", "msedge.exe",
    "opera", "opera.exe",
    "brave", "brave.exe",
    "vivaldi", "vivaldi.exe",
    "safari", "safari.app",
]


def is_browser(app_name: str) -> bool:
    """
    Check if the application is a web browser.
    
    Args:
        app_name: Application name (lowercase)
    
    Returns:
        bool: True if application is a browser
    """
    app_lower = app_name.lower()
    return any(browser in app_lower for browser in BROWSER_PROCESSES)


def match_window_to_format(window_title: str, app_name: str, keywords_map: dict) -> Optional[str]:
    """
    Match window title or application name to a format type using keywords.
    
    This function checks both window title and application name against
    configured keywords to determine the appropriate format.
    
    PRIORITY: Application name is checked FIRST for messengers (Telegram, WhatsApp, etc.)
    because window title shows chat name, not app name.
    
    Args:
        window_title: Window/tab title
        app_name: Application process name
        keywords_map: Dictionary of format_type -> keywords mapping from config
    
    Returns:
        Optional[str]: Format identifier or None if no match
    """
    title_lower = window_title.lower()
    app_lower = app_name.lower()
    
    # STEP 1: Check application name FIRST (priority for messengers)
    # This ensures Telegram/WhatsApp/Discord are detected even if chat name doesn't contain keywords
    for format_type, patterns in keywords_map.items():
        for pattern in patterns:
            pattern_lower = pattern.lower()
            
            # Check application name
            if pattern_lower in app_lower:
                logger.info(f"  ✅ Найдено совпадение в имени приложения: '{pattern}' → формат '{format_type}'")
                return format_type
    
    # STEP 2: Check window title (for browsers and other apps where title matters)
    for format_type, patterns in keywords_map.items():
        for pattern in patterns:
            pattern_lower = pattern.lower()
            
            # Check window title
            if pattern_lower in title_lower:
                logger.info(f"  ✅ Найдено совпадение в заголовке: '{pattern}' → формат '{format_type}'")
                return format_type
            
            # Check file extension in window title
            if pattern.startswith(".") and pattern_lower in title_lower:
                logger.info(f"  ✅ Найдено совпадение расширения: '{pattern}' → формат '{format_type}'")
                return format_type
    
    return None


class FormattingModule:
    """
    Handles automatic formatting of transcribed text based on active application.
    
    This module detects the active application window, matches it against
    configured formats, and applies appropriate formatting using AI.
    """
    
    def __init__(self, config_manager=None, ai_client_factory=None, window_monitor=None, state_manager=None):
        """
        Initialize the formatting module.
        
        Args:
            config_manager: Configuration manager for loading settings, or FormattingConfig instance (optional)
            ai_client_factory: Factory for creating AI client instances (optional)
            window_monitor: Window monitoring component (optional)
            state_manager: State manager for manual format selection (optional)
        """
        # Accept either a FormattingConfig instance or load from environment
        if isinstance(config_manager, FormattingConfig):
            self.config = config_manager
        else:
            from core.config_loader import get_config_loader
            self.config = FormattingConfig.from_config(get_config_loader())
        
        self.window_monitor = window_monitor or WindowMonitor.create()
        self.ai_client_factory = ai_client_factory
        self.state_manager = state_manager
        
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
        
        PRIORITY ORDER (highest to lowest):
        1. Manual format selection (from StateManager)
        2. Fixed format setting (use_fixed_format)
        3. Automatic application detection
        4. Fallback/universal format
        
        Returns:
            Optional[str]: Format identifier (e.g., "notion", "obsidian", "markdown")
                          or "_fallback" if use_fixed_format is enabled
                          or None if no match
        """
        try:
            # PRIORITY 1: Check manual selection first (Requirements 4.1, 4.2, 4.3, 3.4)
            if self.state_manager:
                manual_selection = self.state_manager.get_manual_format_selection()
                if manual_selection:
                    logger.info(f"  🎯 Using manual format selection: {manual_selection}")
                    return manual_selection
            
            # PRIORITY 2: If fixed format is enabled, always use fallback prompt
            if self.config.use_fixed_format:
                logger.info("  🔒 Фиксированный формат включен - используется универсальный промпт")
                return "_fallback"
            
            logger.info("  🔍 Определение активного окна...")
            
            # Get active window information
            window_info = self.window_monitor.get_active_window_info()
            
            if not window_info:
                logger.warning("  ⚠️ Не удалось получить информацию об активном окне")
                return None
            
            # Extract application name and window title
            app_name = window_info.process_name
            window_title = window_info.title
            
            logger.info(f"  📱 Активное окно:")
            logger.info(f"    - Процесс: {app_name}")
            logger.info(f"    - Заголовок: {window_title}")
            
            # Check if we have keywords configured
            if not self.config.web_app_keywords:
                logger.warning("  ⚠️ Ключевые слова приложений не настроены")
                return None
            
            # Try to match window title or app name against keywords
            logger.info(f"  🔎 Поиск соответствия в ключевых словах...")
            format_type = match_window_to_format(
                window_title=window_title,
                app_name=app_name,
                keywords_map=self.config.web_app_keywords
            )
            
            if format_type:
                logger.info(f"  ✅ Найдено соответствие: {format_type}")
                
                # Check if this format is in the configured applications list
                logger.info(f"  🔎 Проверка в списке настроенных приложений: {self.config.applications}")

                # Match application key case-insensitively to avoid config/UI case drift
                app_lookup = {app.lower(): app for app in self.config.applications}
                matched_app_name = app_lookup.get(format_type.lower())

                if matched_app_name:
                    if matched_app_name != format_type:
                        logger.info(
                            f"  ℹ️ Формат '{format_type}' приведен к имени приложения '{matched_app_name}'"
                        )
                    logger.info(f"  ✅ Формат '{matched_app_name}' найден в списке приложений")
                    return matched_app_name

                logger.warning(f"  ⚠️ Формат '{format_type}' не найден в списке настроенных приложений")
                return None
            
            logger.warning(f"  ⚠️ Не найдено соответствие для приложения '{app_name}' и заголовка '{window_title}'")
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
                
                logger.info(f"  🤖 Создание TranscriptionClient для провайдера: {self.config.provider}")
                
                # Get API key from config (already loaded from secrets.json)
                api_key = None
                base_url = None
                
                if self.config.provider == "groq":
                    from core.config_loader import get_config_loader
                    config_loader = get_config_loader()
                    api_key = config_loader.get("ai_provider.api_keys.groq")
                    logger.info(f"  🔑 Загружен GROQ_API_KEY: {api_key[:10] if api_key else 'НЕ НАЙДЕН'}...")
                elif self.config.provider == "openai":
                    from core.config_loader import get_config_loader
                    config_loader = get_config_loader()
                    api_key = config_loader.get("ai_provider.api_keys.openai")
                    logger.info(f"  🔑 Загружен OPENAI_API_KEY: {api_key[:10] if api_key else 'НЕ НАЙДЕН'}...")
                elif self.config.provider == "glm":
                    from core.config_loader import get_config_loader
                    config_loader = get_config_loader()
                    api_key = config_loader.get("ai_provider.api_keys.glm")
                    logger.info(f"  🔑 Загружен GLM_API_KEY: {api_key[:10] if api_key else 'НЕ НАЙДЕН'}...")
                elif self.config.provider == "zai":
                    # Z.AI uses GLM_API_KEY
                    from core.config_loader import get_config_loader
                    config_loader = get_config_loader()
                    api_key = config_loader.get("ai_provider.api_keys.glm")
                    logger.info(f"  🔑 Загружен GLM_API_KEY для Z.AI: {api_key[:10] if api_key else 'НЕ НАЙДЕН'}...")
                elif self.config.provider == "custom":
                    # Custom API key is in self.config.custom_api_key (loaded from secrets.json)
                    api_key = self.config.custom_api_key
                    base_url = self.config.custom_base_url
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
                temperature=self.config.temperature,
                api_key=api_key
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
            logger.warning(f"  - Провайдер валиден: {self.config.provider in ['groq', 'openai', 'glm', 'zai', 'custom']}")
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
