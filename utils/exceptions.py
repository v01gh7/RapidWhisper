"""
Иерархия исключений для RapidWhisper.

Этот модуль определяет все пользовательские исключения, используемые в приложении.
Все исключения наследуются от базового класса RapidWhisperError и организованы
в логические категории: аудио ошибки, API ошибки и ошибки конфигурации.
"""

from typing import Optional


class RapidWhisperError(Exception):
    """
    Базовое исключение для всех ошибок RapidWhisper.
    
    Все пользовательские исключения в приложении должны наследоваться от этого класса.
    Поддерживает как техническое сообщение для логирования, так и понятное
    сообщение для отображения пользователю.
    
    Attributes:
        message: Техническое сообщение об ошибке для разработчиков
        user_message: Понятное сообщение для пользователя (если не указано, используется message)
    """
    
    def __init__(self, message: str, user_message: Optional[str] = None):
        """
        Инициализирует исключение с сообщениями.
        
        Args:
            message: Техническое сообщение об ошибке
            user_message: Опциональное сообщение для пользователя
        """
        self.message = message
        self.user_message = user_message or message
        super().__init__(self.message)


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
            user_message="Микрофон занят другим приложением или недоступен"
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
            user_message="Запись слишком короткая, попробуйте еще раз"
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
            user_message="Не удалось записать аудио, попробуйте еще раз"
        )


class AudioDeviceError(AudioError):
    """
    Общая ошибка аудио устройства.
    
    Используется для других ошибок аудио устройств, которые не попадают
    в более специфичные категории.
    """
    
    def __init__(self, message: str):
        super().__init__(
            message=f"Ошибка аудио устройства: {message}",
            user_message="Ошибка работы с аудио устройством"
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
    
    def __init__(self, message: str = "Ошибка аутентификации"):
        super().__init__(
            message=message,
            user_message="Проверьте GLM_API_KEY в secrets.json"
        )


class APINetworkError(APIError):
    """
    Ошибка подключения к API.
    
    Возникает когда:
    - Нет интернет соединения
    - API сервер недоступен
    - Проблемы с DNS или маршрутизацией
    """
    
    def __init__(self, message: str = "Ошибка подключения к API"):
        super().__init__(
            message=message,
            user_message="Ошибка сети, проверьте подключение к интернету"
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
    
    def __init__(self, timeout: Optional[float] = None):
        if timeout is not None:
            message = f"Превышено время ожидания ответа от API ({timeout} сек)"
        else:
            message = "Превышено время ожидания ответа от API"
        
        super().__init__(
            message=message,
            user_message="Превышено время ожидания, попробуйте еще раз"
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
    
    def __init__(self):
        super().__init__(
            message="API ключ GLM_API_KEY не найден или пустой",
            user_message="Проверьте GLM_API_KEY в secrets.json"
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
            user_message=f"Не найден параметр {parameter} в конфигурации"
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
            user_message=f"Некорректное значение параметра {parameter}"
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
            user_message=f"Не удалось зарегистрировать горячую клавишу {hotkey}, попробуйте другую"
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
