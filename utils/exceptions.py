"""
Иерархия исключений для RapidWhisper.

Этот модуль определяет все пользовательские исключения, используемые в приложении.
Все исключения наследуются от базового класса RapidWhisperError и организованы
в логические категории: аудио ошибки, API ошибки и ошибки конфигурации.
"""

from typing import Optional


class RapidWhisperError(Exception):
    """
    Базовое исключение для всех ошибок RapidWhisper с поддержкой i18n.
    
    Все пользовательские исключения в приложении должны наследоваться от этого класса.
    Поддерживает как техническое сообщение для логирования (на русском), так и
    переводимое сообщение для отображения пользователю через систему i18n.
    
    Attributes:
        message: Техническое сообщение об ошибке для разработчиков (на русском, для логов)
        translation_key: Ключ для перевода сообщения через систему i18n
        translation_params: Параметры для интерполяции в переведенное сообщение
        _user_message: Опциональное переопределение пользовательского сообщения
    
    Examples:
        # Новый стиль с translation_key:
        raise RapidWhisperError(
            message="Ошибка аутентификации для Groq",
            translation_key="errors.api_authentication",
            provider="Groq"
        )
        
        # Старый стиль (обратная совместимость):
        raise RapidWhisperError(
            message="Ошибка аутентификации",
            user_message="Проверьте API ключ"
        )
    """
    
    def __init__(
        self, 
        message: str, 
        user_message: Optional[str] = None,
        translation_key: Optional[str] = None,
        **kwargs
    ):
        """
        Инициализирует исключение с поддержкой i18n.
        
        Args:
            message: Техническое сообщение об ошибке (на русском, для логов)
            user_message: Опциональное переопределение пользовательского сообщения
                         (используется для обратной совместимости)
            translation_key: Ключ для перевода через i18n (например, "errors.api_authentication")
            **kwargs: Параметры для интерполяции в переведенное сообщение
                     (например, provider="Groq", model="whisper-large-v3")
        """
        self.message = message
        self.translation_key = translation_key
        self.translation_params = kwargs
        self._user_message = user_message
        super().__init__(self.message)
    
    @property
    def user_message(self) -> str:
        """
        Получает переведенное пользовательское сообщение.
        
        Порядок приоритета:
        1. Если задан _user_message - возвращает его (обратная совместимость)
        2. Если задан translation_key - переводит через i18n систему
        3. Иначе возвращает техническое сообщение (fallback)
        
        Returns:
            Переведенное сообщение в текущем языке интерфейса
        """
        # Обратная совместимость: если задан user_message явно
        if self._user_message:
            return self._user_message
        
        # Новый стиль: перевод через i18n
        if self.translation_key:
            try:
                from utils.i18n import t
                return t(self.translation_key, **self.translation_params)
            except Exception as e:
                # Если i18n система недоступна или произошла ошибка,
                # логируем и возвращаем техническое сообщение
                try:
                    from utils.logger import get_logger
                    logger = get_logger()
                    logger.error(f"Не удалось перевести сообщение об ошибке: {e}")
                except:
                    pass  # Даже логирование не работает
                return self.message
        
        # Fallback: техническое сообщение
        return self.message


# ============================================================================
# Ошибки аудио подсистемы
# ============================================================================

class AudioError(RapidWhisperError):
    """
    Базовый класс для ошибок аудио подсистемы.
    
    Используется для всех ошибок, связанных с записью, обработкой
    и сохранением аудио данных.
    """
    pass


class MicrophoneUnavailableError(AudioError):
    """
    Микрофон недоступен или занят другим приложением.
    
    Возникает когда:
    - Микрофон используется другим приложением
    - Микрофон отключен или не найден в системе
    - Нет разрешения на доступ к микрофону
    """
    
    def __init__(self, message: str = "Микрофон недоступен"):
        super().__init__(
            message=message,
            translation_key="errors.microphone_unavailable"
        )


class RecordingTooShortError(AudioError):
    """
    Запись слишком короткая для обработки.
    
    Возникает когда длительность записи меньше минимально допустимой
    (обычно 0.5 секунды). Короткие записи не могут быть корректно
    обработаны системой распознавания речи.
    """
    
    def __init__(self, duration: Optional[float] = None):
        if duration is not None:
            message = f"Запись слишком короткая: {duration:.2f} секунд"
        else:
            message = "Запись слишком короткая"
        
        super().__init__(
            message=message,
            translation_key="errors.recording_too_short",
            duration=duration
        )


class EmptyRecordingError(AudioError):
    """
    Аудио буфер пустой или не содержит данных.
    
    Возникает когда:
    - Не удалось записать аудио данные
    - Аудио буфер был очищен до сохранения
    - Микрофон не передал данные
    """
    
    def __init__(self):
        super().__init__(
            message="Аудио буфер пустой",
            translation_key="errors.empty_recording"
        )


class AudioDeviceError(AudioError):
    """
    Общая ошибка аудио устройства.
    
    Используется для других ошибок аудио устройств, которые не попадают
    в более специфичные категории.
    """
    
    def __init__(self, error: str):
        super().__init__(
            message=f"Ошибка аудио устройства: {error}",
            translation_key="errors.audio_device_error",
            error=error
        )


# ============================================================================
# Ошибки API
# ============================================================================

class APIError(RapidWhisperError):
    """
    Базовый класс для ошибок взаимодействия с API.
    
    Используется для всех ошибок, связанных с запросами к GLM API
    и обработкой ответов.
    """
    pass


class APIAuthenticationError(APIError):
    """
    Ошибка аутентификации в API.
    
    Возникает когда:
    - API ключ отсутствует
    - API ключ неверный или истек
    - Нет доступа к запрашиваемому ресурсу
    """
    
    def __init__(self, provider: str, message: Optional[str] = None):
        if message is None:
            message = f"Ошибка аутентификации для {provider}"
        
        super().__init__(
            message=message,
            translation_key="errors.api_authentication",
            provider=provider
        )


class APINetworkError(APIError):
    """
    Ошибка подключения к API.
    
    Возникает когда:
    - Нет интернет соединения
    - API сервер недоступен
    - Проблемы с DNS или маршрутизацией
    """
    
    def __init__(self, provider: str, message: str = "Ошибка подключения к API"):
        super().__init__(
            message=message,
            translation_key="errors.api_network",
            provider=provider
        )


# Оставляем старые имена для обратной совместимости
AuthenticationError = APIAuthenticationError
APIConnectionError = APINetworkError


class APITimeoutError(APIError):
    """
    Превышено время ожидания ответа от API.
    
    Возникает когда API не отвечает в течение установленного таймаута
    (обычно 30 секунд). Может быть вызвано медленным соединением или
    высокой нагрузкой на сервер.
    """
    
    def __init__(self, provider: str, timeout: Optional[float] = None):
        if timeout is not None:
            message = f"Превышено время ожидания ответа от API ({timeout} сек)"
        else:
            message = "Превышено время ожидания ответа от API"
        
        super().__init__(
            message=message,
            translation_key="errors.api_timeout",
            provider=provider,
            timeout=timeout
        )


class ModelNotFoundError(APIError):
    """
    Модель не найдена или недоступна.
    
    Возникает когда:
    - Указанная модель не существует у провайдера
    - Нет доступа к запрашиваемой модели
    - Модель была удалена или переименована
    """
    
    def __init__(self, model: str, provider: str):
        super().__init__(
            message=f"Модель {model} не найдена у провайдера {provider}",
            translation_key="errors.model_not_found",
            model=model,
            provider=provider
        )


class APIResponseError(APIError):
    """
    Ошибка обработки ответа от API.
    
    Возникает когда:
    - API вернул некорректный формат данных
    - Отсутствуют ожидаемые поля в ответе
    - Не удалось распарсить JSON ответ
    """
    
    def __init__(self, message: str):
        super().__init__(
            message=f"Ошибка обработки ответа API: {message}",
            user_message="Ошибка обработки ответа от сервера"
        )


# ============================================================================
# Ошибки конфигурации
# ============================================================================

class ConfigurationError(RapidWhisperError):
    """
    Базовый класс для ошибок конфигурации приложения.
    
    Используется для всех ошибок, связанных с загрузкой и валидацией
    конфигурационных параметров.
    """
    pass


class InvalidAPIKeyError(ConfigurationError):
    """
    API ключ отсутствует или неверен.
    
    Возникает когда GLM_API_KEY не найден в переменных окружения
    или имеет пустое значение.
    """
    
    def __init__(self, provider: str):
        super().__init__(
            message=f"API ключ для {provider} не найден или пустой",
            translation_key="errors.invalid_api_key",
            provider=provider
        )


class MissingConfigError(ConfigurationError):
    """
    Отсутствует обязательный параметр конфигурации.
    
    Возникает когда обязательный параметр (например, API ключ)
    не найден в конфигурационном файле или переменных окружения.
    """
    
    def __init__(self, parameter: str):
        super().__init__(
            message=f"Отсутствует обязательный параметр конфигурации: {parameter}",
            translation_key="errors.missing_config",
            parameter=parameter
        )


class InvalidConfigError(ConfigurationError):
    """
    Некорректное значение параметра конфигурации.
    
    Возникает когда значение параметра не соответствует ожидаемому
    формату или находится вне допустимого диапазона.
    """
    
    def __init__(self, parameter: str, value: str, reason: str):
        super().__init__(
            message=f"Некорректное значение параметра {parameter}='{value}': {reason}",
            translation_key="errors.invalid_config",
            parameter=parameter,
            value=value,
            reason=reason
        )


class HotkeyConflictError(ConfigurationError):
    """
    Не удалось зарегистрировать горячую клавишу.
    
    Возникает когда:
    - Горячая клавиша уже используется другим приложением
    - Нет прав на регистрацию глобальных горячих клавиш
    - Указана некорректная комбинация клавиш
    """
    
    def __init__(self, hotkey: str, reason: Optional[str] = None):
        message = f"Не удалось зарегистрировать горячую клавишу {hotkey}"
        if reason:
            message += f": {reason}"
        
        super().__init__(
            message=message,
            translation_key="errors.hotkey_conflict",
            hotkey=hotkey,
            reason=reason
        )


# ============================================================================
# Вспомогательные функции
# ============================================================================

def get_user_friendly_message(error: Exception) -> str:
    """
    Получает понятное пользователю сообщение об ошибке.
    
    Если ошибка является экземпляром RapidWhisperError, возвращает
    user_message. Для других исключений возвращает общее сообщение.
    
    Args:
        error: Исключение для обработки
        
    Returns:
        Понятное пользователю сообщение об ошибке
    """
    if isinstance(error, RapidWhisperError):
        return error.user_message
    return "Произошла неожиданная ошибка"


def is_recoverable_error(error: Exception) -> bool:
    """
    Определяет, можно ли восстановиться после ошибки.
    
    Некоторые ошибки (например, сетевые) являются временными и после них
    можно продолжить работу. Другие (например, отсутствие API ключа)
    требуют вмешательства пользователя.
    
    Args:
        error: Исключение для проверки
        
    Returns:
        True если после ошибки можно продолжить работу, False иначе
    """
    # Временные ошибки, после которых можно продолжить
    recoverable_types = (
        APINetworkError,
        APIConnectionError,
        APITimeoutError,
        RecordingTooShortError,
        EmptyRecordingError,
        MicrophoneUnavailableError,
    )
    
    # Критические ошибки, требующие вмешательства
    critical_types = (
        APIAuthenticationError,
        AuthenticationError,
        InvalidAPIKeyError,
        MissingConfigError,
        InvalidConfigError,
    )
    
    if isinstance(error, critical_types):
        return False
    
    if isinstance(error, recoverable_types):
        return True
    
    # По умолчанию считаем ошибку восстановимой
    return True
