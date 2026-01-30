"""
Клиент для взаимодействия с AI API для транскрипции аудио.

Поддерживает несколько провайдеров: OpenAI, Groq, GLM, и кастомные OpenAI-совместимые API.
Использует OpenAI Python SDK с настройкой на разные API endpoints.
"""

import os
import shutil
from typing import BinaryIO, Optional
from pathlib import Path
from openai import OpenAI, AuthenticationError, APIConnectionError, APITimeoutError

from utils.exceptions import (
    APIError,
    APIAuthenticationError,
    APINetworkError,
    APITimeoutError as CustomAPITimeoutError,
    InvalidAPIKeyError
)


class TranscriptionClient:
    """
    Универсальный клиент для транскрипции аудио.
    
    Поддерживает несколько провайдеров: OpenAI, Groq, GLM, и кастомные OpenAI-совместимые API.
    Использует OpenAI SDK для всех провайдеров.
    
    Attributes:
        client: Экземпляр OpenAI клиента
        provider: Название провайдера (openai, groq, glm, custom)
        base_url: URL endpoint для API
        model: Модель для транскрипции
        timeout: Таймаут запроса в секундах
    """
    
    def __init__(self, provider: str = "openai", api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        """
        Инициализирует клиент транскрипции.
        
        Args:
            provider: Провайдер AI (openai, groq, glm, custom)
            api_key: API ключ. Если не указан, загружается из переменных окружения
            base_url: Кастомный URL для API (для custom провайдера)
            model: Кастомная модель (для custom провайдера)
        
        Raises:
            InvalidAPIKeyError: Если API ключ не найден или пустой
            ValueError: Если провайдер неизвестен или не хватает параметров
        """
        self.provider = provider.lower()
        
        # Загрузить API ключ из переменной окружения если не передан
        if api_key is None:
            if self.provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
            elif self.provider == "groq":
                api_key = os.getenv("GROQ_API_KEY")
            elif self.provider == "glm":
                api_key = os.getenv("GLM_API_KEY")
            elif self.provider == "custom":
                api_key = os.getenv("CUSTOM_API_KEY")
            else:
                raise ValueError(f"Неизвестный провайдер: {provider}")
        
        if not api_key:
            raise InvalidAPIKeyError()
        
        # Настроить параметры в зависимости от провайдера
        if self.provider == "openai":
            self.base_url = "https://api.openai.com/v1/"
            self.model = "whisper-1"
        elif self.provider == "groq":
            self.base_url = "https://api.groq.com/openai/v1/"
            self.model = "whisper-large-v3"
        elif self.provider == "glm":
            self.base_url = "https://open.bigmodel.cn/api/paas/v4/"
            self.model = "glm-4-voice"
        elif self.provider == "custom":
            # Для кастомного провайдера требуются base_url и model
            if base_url is None:
                base_url = os.getenv("CUSTOM_BASE_URL")
            if model is None:
                model = os.getenv("CUSTOM_MODEL", "whisper-1")
            
            if not base_url:
                raise ValueError("Для custom провайдера требуется CUSTOM_BASE_URL")
            
            self.base_url = base_url
            self.model = model
        else:
            raise ValueError(f"Неизвестный провайдер: {provider}")
        
        self.timeout = 30
        
        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url=self.base_url,
                timeout=self.timeout
            )
        except Exception as e:
            raise APIError(f"Не удалось инициализировать клиент {provider}: {e}")
    
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
        from utils.logger import get_logger
        logger = get_logger()
        
        audio_file = None
        try:
            logger.info(f"Подготовка аудио файла: {audio_file_path}")
            
            # Подготовить аудио файл
            audio_file = self._prepare_audio_file(audio_file_path)
            logger.info("Аудио файл открыт успешно")
            
            # Отправить запрос на транскрипцию
            logger.info(f"Отправка запроса к API: {self.base_url}")
            logger.info(f"Модель: {self.model}, Таймаут: {self.timeout}с")
            
            response = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                response_format="json"
            )
            
            logger.info("Ответ от API получен")
            
            # Извлечь текст из ответа
            if hasattr(response, 'text'):
                logger.info(f"Текст извлечен: {response.text[:50]}...")
                return response.text
            else:
                logger.error("Ответ API не содержит поле 'text'")
                raise APIError("Ответ API не содержит поле 'text'")
        
        except AuthenticationError as e:
            logger.error(f"Ошибка аутентификации: {e}")
            raise APIAuthenticationError(str(e))
        
        except APITimeoutError as e:
            logger.error(f"Таймаут API: {e}")
            raise CustomAPITimeoutError(str(e))
        
        except APIConnectionError as e:
            logger.error(f"Ошибка подключения к API: {e}")
            raise APINetworkError(str(e))
        
        except Exception as ex:
            # Обработать другие ошибки
            logger.error(f"Неожиданная ошибка API: {ex}")
            import traceback
            logger.error(traceback.format_exc())
            error_message = self._handle_api_error(ex)
            raise APIError(error_message)
        
        finally:
            # ВАЖНО: Закрыть файл после использования
            if audio_file:
                try:
                    audio_file.close()
                    logger.info("Аудио файл закрыт")
                except Exception as close_error:
                    logger.warning(f"Не удалось закрыть файл: {close_error}")
    
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


# Обратная совместимость
GLMClient = TranscriptionClient


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
    
    def __init__(self, audio_file_path: str, provider: str = "openai", api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        """
        Инициализирует поток транскрипции.
        
        Args:
            audio_file_path: Путь к аудио файлу для транскрипции
            provider: Провайдер AI (openai, groq, glm, custom)
            api_key: API ключ (опционально)
            base_url: Кастомный URL для API (для custom провайдера)
            model: Кастомная модель (для custom провайдера)
        """
        super().__init__()
        self.audio_file_path = audio_file_path
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.transcription_client: Optional[TranscriptionClient] = None
    
    def run(self) -> None:
        """
        Выполняет транскрипцию аудио файла.
        
        Создает GLMClient, отправляет аудио на транскрипцию
        и отправляет сигнал с результатом или ошибкой.
        Удаляет временный файл после завершения.
        
        Requirements: 9.2
        """
        from utils.logger import get_logger
        logger = get_logger()
        
        try:
            logger.info(f"TranscriptionThread.run() начат для файла: {self.audio_file_path}")
            logger.info(f"Провайдер: {self.provider}")
            
            # Создать клиент транскрипции
            logger.info(f"Создание TranscriptionClient для {self.provider}...")
            self.transcription_client = TranscriptionClient(
                provider=self.provider, 
                api_key=self.api_key,
                base_url=self.base_url,
                model=self.model
            )
            logger.info(f"TranscriptionClient создан успешно (модель: {self.transcription_client.model})")
            
            # Выполнить транскрипцию
            logger.info("Начало транскрипции...")
            text = self.transcription_client.transcribe_audio(self.audio_file_path)
            logger.info(f"Транскрипция завершена: {text[:50]}...")
            
            # Отправить сигнал с результатом
            logger.info("Отправка сигнала transcription_complete")
            self.transcription_complete.emit(text)
            
        except Exception as e:
            # Отправить сигнал об ошибке
            logger.error(f"Ошибка в TranscriptionThread: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.transcription_error.emit(e)
            
        finally:
            # Удалить или сохранить временный файл в зависимости от настроек
            try:
                if os.path.exists(self.audio_file_path):
                    # Загрузить конфигурацию для проверки настройки
                    from core.config import Config, get_recordings_dir
                    from datetime import datetime
                    
                    config = Config.load_from_env()
                    
                    if config.keep_recordings:
                        # Сохранить файл в директорию recordings
                        recordings_dir = get_recordings_dir()
                        
                        # Создать имя файла с timestamp
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"recording_{timestamp}.wav"
                        dest_path = recordings_dir / filename
                        
                        # Переместить файл
                        shutil.move(self.audio_file_path, str(dest_path))
                        logger.info(f"Запись сохранена: {dest_path}")
                    else:
                        # Удалить временный файл
                        import time
                        time.sleep(0.1)
                        os.remove(self.audio_file_path)
                        logger.info(f"Временный файл удален: {self.audio_file_path}")
            except Exception as e:
                # Игнорировать ошибки удаления/перемещения файла
                logger.warning(f"Не удалось обработать временный файл: {e}")
