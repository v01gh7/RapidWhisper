"""
GLM API клиент для транскрипции аудио через Zhipu AI.

Этот модуль предоставляет клиент для взаимодействия с Zhipu GLM API
для транскрипции аудио файлов в текст. Использует OpenAI Python SDK
с настроенным base_url для совместимости с GLM API.
"""

import os
from typing import BinaryIO, Optional
from pathlib import Path

import openai
from openai import OpenAI

from utils.exceptions import (
    AuthenticationError,
    APIConnectionError,
    APITimeoutError,
    APIResponseError,
    MissingConfigError,
)
from utils.logger import get_logger


logger = get_logger()


class GLMClient:
    """
    Клиент для взаимодействия с Zhipu GLM API.
    
    Использует OpenAI Python SDK с настроенным base_url для отправки
    аудио файлов на транскрипцию через модель whisper-1.
    
    Attributes:
        client: Экземпляр OpenAI клиента
        base_url: URL эндпоинта Zhipu AI API
        model: Название модели для транскрипции
        timeout: Таймаут запроса в секундах
    
    Example:
        >>> client = GLMClient(api_key="your_api_key")
        >>> text = client.transcribe_audio("recording.wav")
        >>> print(text)
        "Привет, это тестовая транскрипция"
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализирует GLM клиент.
        
        Args:
            api_key: API ключ для Zhipu AI. Если не указан, загружается
                    из переменной окружения GLM_API_KEY.
        
        Raises:
            MissingConfigError: Если API ключ не найден
        """
        # Загрузить API ключ из параметра или переменной окружения
        self.api_key = api_key or os.getenv("GLM_API_KEY")
        
        if not self.api_key:
            logger.error("GLM_API_KEY не найден в переменных окружения")
            raise MissingConfigError("GLM_API_KEY")
        
        # Настройки API
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/"
        self.model = "whisper-1"
        self.timeout = 30
        
        # Инициализировать OpenAI клиент с настройками для Zhipu AI
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout
            )
            logger.info(f"GLMClient инициализирован с base_url={self.base_url}")
        except Exception as e:
            logger.error(f"Ошибка инициализации OpenAI клиента: {e}")
            raise
    
    def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Отправляет аудио файл на транскрипцию и возвращает текст.
        
        Args:
            audio_file_path: Путь к аудио файлу в формате WAV
        
        Returns:
            Распознанный текст из аудио
        
        Raises:
            FileNotFoundError: Если аудио файл не найден
            AuthenticationError: Если API ключ неверный
            APIConnectionError: Если не удалось подключиться к API
            APITimeoutError: Если превышен таймаут запроса
            APIResponseError: Если ответ API некорректен
        
        Example:
            >>> client = GLMClient()
            >>> text = client.transcribe_audio("recording.wav")
            >>> print(text)
            "Привет, это тестовая транскрипция"
        """
        # Проверить существование файла
        if not os.path.exists(audio_file_path):
            logger.error(f"Аудио файл не найден: {audio_file_path}")
            raise FileNotFoundError(f"Аудио файл не найден: {audio_file_path}")
        
        logger.info(f"Начало транскрипции файла: {audio_file_path}")
        
        try:
            # Подготовить аудио файл для отправки
            audio_file = self._prepare_audio_file(audio_file_path)
            
            # Отправить запрос на транскрипцию
            logger.debug(f"Отправка запроса к API с моделью {self.model}")
            response = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                response_format="json"
            )
            
            # Извлечь текст из ответа
            if hasattr(response, 'text'):
                text = response.text
                logger.info(f"Транскрипция успешна, длина текста: {len(text)} символов")
                return text
            else:
                logger.error(f"Ответ API не содержит поле 'text': {response}")
                raise APIResponseError("Ответ API не содержит поле 'text'")
        
        except openai.AuthenticationError as e:
            logger.error(f"Ошибка аутентификации: {e}")
            self._handle_api_error(e)
        
        except openai.APIConnectionError as e:
            logger.error(f"Ошибка подключения к API: {e}")
            self._handle_api_error(e)
        
        except openai.APITimeoutError as e:
            logger.error(f"Превышен таймаут запроса: {e}")
            self._handle_api_error(e)
        
        except Exception as e:
            logger.error(f"Неожиданная ошибка при транскрипции: {e}")
            self._handle_api_error(e)
        
        finally:
            # Закрыть файл если он был открыт
            if 'audio_file' in locals() and hasattr(audio_file, 'close'):
                audio_file.close()
    
    def _prepare_audio_file(self, filepath: str) -> BinaryIO:
        """
        Подготавливает аудио файл для отправки в API.
        
        Открывает файл в бинарном режиме для чтения и возвращает
        файловый объект, который может быть передан в API.
        
        Args:
            filepath: Путь к аудио файлу
        
        Returns:
            Открытый файловый объект в бинарном режиме
        
        Raises:
            FileNotFoundError: Если файл не найден
            PermissionError: Если нет прав на чтение файла
        """
        try:
            # Открыть файл в бинарном режиме
            audio_file = open(filepath, 'rb')
            logger.debug(f"Файл {filepath} успешно открыт для чтения")
            return audio_file
        
        except FileNotFoundError:
            logger.error(f"Файл не найден: {filepath}")
            raise
        
        except PermissionError:
            logger.error(f"Нет прав на чтение файла: {filepath}")
            raise
        
        except Exception as e:
            logger.error(f"Ошибка открытия файла {filepath}: {e}")
            raise
    
    def _handle_api_error(self, error: Exception) -> str:
        """
        Обрабатывает ошибки API и преобразует их в понятные исключения.
        
        Анализирует тип ошибки от OpenAI SDK и преобразует её в
        соответствующее исключение из нашей иерархии ошибок с
        понятными сообщениями для пользователя.
        
        Args:
            error: Исключение от OpenAI SDK
        
        Raises:
            AuthenticationError: Для ошибок аутентификации
            APIConnectionError: Для ошибок подключения
            APITimeoutError: Для ошибок таймаута
            APIResponseError: Для других ошибок API
        """
        # Обработка ошибок таймаута (проверяем первым, так как это подкласс APIConnectionError)
        if isinstance(error, openai.APITimeoutError):
            raise APITimeoutError(timeout=self.timeout)
        
        # Обработка ошибок аутентификации
        if isinstance(error, openai.AuthenticationError):
            raise AuthenticationError(
                message=f"Ошибка аутентификации в GLM API: {error}"
            )
        
        # Обработка ошибок подключения
        if isinstance(error, openai.APIConnectionError):
            raise APIConnectionError(
                message=f"Не удалось подключиться к GLM API: {error}"
            )
        
        # Обработка других ошибок API
        raise APIResponseError(
            message=f"Ошибка при обработке запроса: {error}"
        )
