"""
Клиент для взаимодействия с Zhipu GLM API для транскрипции аудио.

Использует OpenAI Python SDK с настройкой на Zhipu AI API endpoint.
"""

import os
from typing import BinaryIO, Optional
from openai import OpenAI, AuthenticationError, APIConnectionError, APITimeoutError

from utils.exceptions import (
    APIError,
    APIAuthenticationError,
    APINetworkError,
    APITimeoutError as CustomAPITimeoutError,
    InvalidAPIKeyError
)


class GLMClient:
    """
    Клиент для Zhipu GLM API.
    
    Использует OpenAI SDK для отправки аудио файлов на транскрипцию
    через Zhipu AI API endpoint.
    
    Attributes:
        client: Экземпляр OpenAI клиента
        base_url: URL endpoint для Zhipu AI API
        model: Модель для транскрипции (whisper-1)
        timeout: Таймаут запроса в секундах
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализирует GLM клиент.
        
        Args:
            api_key: API ключ для Zhipu AI. Если не указан, загружается из GLM_API_KEY
        
        Raises:
            InvalidAPIKeyError: Если API ключ не найден или пустой
        """
        # Загрузить API ключ из переменной окружения или использовать переданный
        if api_key is None:
            api_key = os.getenv("GLM_API_KEY")
        
        if not api_key:
            raise InvalidAPIKeyError()
        
        # Настроить OpenAI клиент для Zhipu AI
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/"
        self.model = "whisper-1"
        self.timeout = 30
        
        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url=self.base_url,
                timeout=self.timeout
            )
        except Exception as e:
            raise APIError(f"Не удалось инициализировать GLM клиент: {e}")
    
    def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Отправляет аудио файл на транскрипцию и возвращает текст.
        
        Args:
            audio_file_path: Путь к аудио файлу (WAV формат)
        
        Returns:
            Транскрибированный текст
        
        Raises:
            APIAuthenticationError: Если API ключ неверен
            APINetworkError: Если произошла сетевая ошибка
            CustomAPITimeoutError: Если запрос превысил таймаут
            APIError: Для других ошибок API
        """
        try:
            # Подготовить аудио файл
            audio_file = self._prepare_audio_file(audio_file_path)
            
            # Отправить запрос на транскрипцию
            response = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                response_format="json"
            )
            
            # Извлечь текст из ответа
            if hasattr(response, 'text'):
                return response.text
            else:
                raise APIError("Ответ API не содержит поле 'text'")
        
        except AuthenticationError as e:
            raise APIAuthenticationError(str(e))
        
        except APITimeoutError as e:
            raise CustomAPITimeoutError(str(e))
        
        except APIConnectionError as e:
            raise APINetworkError(str(e))
        
        except Exception as e:
            # Обработать другие ошибки
            error_message = self._handle_api_error(e)
            raise APIError(error_message)
    
    def _prepare_audio_file(self, filepath: str) -> BinaryIO:
        """
        Подготавливает аудио файл для отправки в API.
        
        Args:
            filepath: Путь к аудио файлу
        
        Returns:
            Открытый файловый объект
        
        Raises:
            APIError: Если файл не найден или не может быть открыт
        """
        try:
            return open(filepath, 'rb')
        except FileNotFoundError:
            raise APIError(f"Аудио файл не найден: {filepath}")
        except Exception as e:
            raise APIError(f"Не удалось открыть аудио файл: {e}")
    
    def _handle_api_error(self, error: Exception) -> str:
        """
        Обрабатывает ошибки API и возвращает понятное сообщение.
        
        Args:
            error: Исключение от API
        
        Returns:
            Понятное сообщение об ошибке для пользователя
        """
        error_str = str(error).lower()
        
        # Определить тип ошибки по сообщению
        if "authentication" in error_str or "api key" in error_str:
            return "Ошибка аутентификации. Проверьте GLM_API_KEY в .env файле"
        elif "network" in error_str or "connection" in error_str:
            return "Ошибка сети. Проверьте подключение к интернету"
        elif "timeout" in error_str:
            return "Превышено время ожидания ответа от API"
        elif "rate limit" in error_str:
            return "Превышен лимит запросов к API"
        else:
            return f"Ошибка API: {error}"



from PyQt6.QtCore import QThread, pyqtSignal


class TranscriptionThread(QThread):
    """
    Поток для транскрипции аудио в фоновом режиме.
    
    Наследуется от QThread для неблокирующей транскрипции аудио.
    Отправляет сигналы при завершении транскрипции или при ошибке.
    
    Signals:
        transcription_complete: Сигнал с результатом транскрипции (str)
        transcription_error: Сигнал при ошибке транскрипции (Exception)
    
    Requirements: 9.2
    """
    
    # Сигналы
    transcription_complete = pyqtSignal(str)  # Транскрибированный текст
    transcription_error = pyqtSignal(Exception)  # Ошибка транскрипции
    
    def __init__(self, audio_file_path: str, api_key: Optional[str] = None):
        """
        Инициализирует поток транскрипции.
        
        Args:
            audio_file_path: Путь к аудио файлу для транскрипции
            api_key: API ключ для Zhipu AI (опционально)
        """
        super().__init__()
        self.audio_file_path = audio_file_path
        self.api_key = api_key
        self.glm_client: Optional[GLMClient] = None
    
    def run(self) -> None:
        """
        Выполняет транскрипцию аудио файла.
        
        Создает GLMClient, отправляет аудио на транскрипцию
        и отправляет сигнал с результатом или ошибкой.
        Удаляет временный файл после завершения.
        
        Requirements: 9.2
        """
        try:
            # Создать GLM клиент
            self.glm_client = GLMClient(api_key=self.api_key)
            
            # Выполнить транскрипцию
            text = self.glm_client.transcribe_audio(self.audio_file_path)
            
            # Отправить сигнал с результатом
            self.transcription_complete.emit(text)
            
        except Exception as e:
            # Отправить сигнал об ошибке
            self.transcription_error.emit(e)
            
        finally:
            # Удалить временный файл
            try:
                if os.path.exists(self.audio_file_path):
                    os.remove(self.audio_file_path)
            except Exception:
                # Игнорировать ошибки удаления файла
                pass
