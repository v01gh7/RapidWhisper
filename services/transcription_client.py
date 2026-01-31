"""
Клиент для взаимодействия с AI API для транскрипции аудио.

Поддерживает несколько провайдеров: OpenAI, Groq, GLM, и кастомные OpenAI-совместимые API.
Использует OpenAI Python SDK с настройкой на разные API endpoints.
"""

import os
import shutil
from typing import BinaryIO, Optional
from pathlib import Path
from openai import OpenAI, AuthenticationError, APIConnectionError, APITimeoutError, Timeout, NotFoundError, BadRequestError

from utils.exceptions import (
    APIError,
    APIAuthenticationError,
    APINetworkError,
    APITimeoutError as CustomAPITimeoutError,
    InvalidAPIKeyError
)
from services.processing_coordinator import ProcessingCoordinator
from services.formatting_module import FormattingModule
from services.formatting_config import FormattingConfig


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
            self.model = model if model else "whisper-1"  # Используем кастомную модель если указана
        elif self.provider == "groq":
            self.base_url = "https://api.groq.com/openai/v1/"
            self.model = model if model else "whisper-large-v3"  # Используем кастомную модель если указана
        elif self.provider == "glm":
            self.base_url = "https://open.bigmodel.cn/api/paas/v4/"
            self.model = model if model else "glm-4-voice"  # Используем кастомную модель если указана
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
        
        except NotFoundError as e:
            logger.error(f"🔍 МОДЕЛЬ ТРАНСКРИПЦИИ НЕ НАЙДЕНА: {e}")
            logger.error(f"Модель '{self.model}' не существует для провайдера {self.provider}")
            logger.error("Проверьте название модели в настройках AI Provider")
            logger.warning("⚠️ Пробрасываем исключение для уведомления пользователя")
            # Пробросить исключение чтобы TranscriptionThread мог показать уведомление
            raise
        
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
    
    def post_process_text(self, text: str, provider: str, model: str, system_prompt: str, api_key: Optional[str] = None, base_url: Optional[str] = None, use_coding_plan: bool = False, temperature: float = 0.3) -> str:
        """
        Постобработка транскрибированного текста через LLM.
        
        Отправляет текст на дополнительную обработку для исправления ошибок,
        добавления пунктуации и улучшения читаемости.
        
        Args:
            text: Исходный транскрибированный текст
            provider: Провайдер для постобработки (groq, openai, glm, llm)
            model: Модель для постобработки
            system_prompt: Системный промпт для модели
            api_key: API ключ (если None, загружается из env)
            base_url: Base URL для LLM провайдера (локальные модели)
            use_coding_plan: Использовать Coding Plan endpoint для GLM
        
        Returns:
            Обработанный текст
        
        Raises:
            APIError: При ошибке обработки
        """
        from utils.logger import get_logger
        logger = get_logger()
        
        try:
            logger.info("=" * 80)
            logger.info("НАЧАЛО ПОСТОБРАБОТКИ ТЕКСТА")
            logger.info(f"Провайдер: {provider}")
            logger.info(f"Модель: {model}")
            logger.info(f"Длина исходного текста: {len(text)} символов")
            logger.info(f"Исходный текст: {text[:200]}...")
            logger.info(f"Системный промпт: {system_prompt[:100]}...")
            
            # Загрузить API ключ если не передан
            if api_key is None:
                if provider == "groq":
                    api_key = os.getenv("GROQ_API_KEY")
                    logger.info("Загружен GROQ_API_KEY из env")
                elif provider == "openai":
                    api_key = os.getenv("OPENAI_API_KEY")
                    logger.info("Загружен OPENAI_API_KEY из env")
                elif provider == "glm":
                    api_key = os.getenv("GLM_API_KEY")
                    logger.info("Загружен GLM_API_KEY из env")
                elif provider == "llm":
                    # LLM - локальные модели, ключ может быть любым или пустым
                    api_key = os.getenv("LLM_API_KEY", "local")
                    logger.info("Загружен LLM_API_KEY из env (или используется 'local')")
            
            if not api_key and provider != "llm":
                logger.error(f"API ключ для {provider} не найден!")
                raise InvalidAPIKeyError(f"API ключ для {provider} не найден")
            
            logger.info(f"API ключ найден: {api_key[:10]}...")
            
            # Настроить base_url в зависимости от провайдера
            if provider == "groq":
                base_url = "https://api.groq.com/openai/v1/"
            elif provider == "openai":
                base_url = "https://api.openai.com/v1/"
            elif provider == "glm":
                # GLM: выбор endpoint в зависимости от use_coding_plan
                if use_coding_plan:
                    # Попробуем Coding Plan endpoint
                    base_url = "https://api.z.ai/api/coding/paas/v4/"
                    logger.info("Используется GLM Coding Plan endpoint")
                    logger.warning("⚠️ Если запрос зависает, попробуйте отключить Coding Plan")
                else:
                    base_url = "https://open.bigmodel.cn/api/paas/v4/"
                    logger.info("Используется обычный GLM endpoint")
            elif provider == "llm":
                # LLM - локальные модели, base_url должен быть передан
                if not base_url:
                    base_url = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1/")
                logger.info(f"Используется локальный LLM endpoint: {base_url}")
            else:
                logger.error(f"Неизвестный провайдер: {provider}")
                raise ValueError(f"Неизвестный провайдер для постобработки: {provider}")
            
            logger.info(f"Base URL: {base_url}")
            
            # Создать клиент для постобработки с жестким таймаутом
            logger.info("Создание OpenAI клиента...")
            client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=Timeout(60.0, connect=10.0)  # 60 секунд на запрос, 10 на подключение
            )
            logger.info("Клиент создан успешно с таймаутом 60 секунд")
            
            # Отправить запрос на обработку
            logger.info("Отправка запроса на постобработку...")
            logger.info(f"Параметры: temperature={temperature}, max_tokens=2000")
            logger.info(f"Отправка к {base_url} с моделью {model}...")
            logger.info("⏱️ Таймаут: 60 секунд (после этого вернется оригинальный текст)")
            
            import time
            start_time = time.time()
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=temperature,  # Use provided temperature
                max_tokens=2000,
                timeout=60.0  # Дополнительный таймаут на уровне запроса
            )
            
            elapsed_time = time.time() - start_time
            logger.info(f"Запрос выполнен за {elapsed_time:.2f} секунд")
            elapsed_time = time.time() - start_time
            logger.info(f"Запрос выполнен за {elapsed_time:.2f} секунд")
            logger.info("Ответ получен от API")
            
            # Извлечь обработанный текст
            if response.choices and len(response.choices) > 0:
                processed_text = response.choices[0].message.content
                
                # Проверить что текст не None и не пустой
                if processed_text:
                    processed_text = processed_text.strip()
                    
                    if processed_text:  # Проверка что после strip() текст не пустой
                        logger.info(f"Обработанный текст получен, длина: {len(processed_text)} символов")
                        logger.info(f"Обработанный текст: {processed_text[:200]}...")
                        logger.info("✅ ПОСТОБРАБОТКА ЗАВЕРШЕНА УСПЕШНО")
                        logger.info("=" * 80)
                        return processed_text
                    else:
                        logger.warning("⚠️ Ответ постобработки пустой (после strip)!")
                        logger.warning("⚠️ Возвращаем оригинальный текст")
                        logger.info("=" * 80)
                        return text
                else:
                    logger.warning("⚠️ Ответ постобработки пустой (None или пустая строка)!")
                    logger.warning("⚠️ Возвращаем оригинальный текст")
                    logger.info("=" * 80)
                    return text
            else:
                logger.warning("⚠️ Ответ постобработки не содержит choices!")
                logger.warning("⚠️ Возвращаем оригинальный текст")
                logger.info("=" * 80)
                return text
        
        except APITimeoutError as e:
            logger.error("=" * 80)
            logger.error(f"⏱️ ТАЙМАУТ ПОСТОБРАБОТКИ: {e}")
            logger.error("Запрос превысил 60 секунд")
            logger.warning("⚠️ Возвращаем оригинальный текст без обработки")
            logger.error("=" * 80)
            return text
        
        except AuthenticationError as e:
            logger.error("=" * 80)
            logger.error(f"🔐 ОШИБКА АУТЕНТИФИКАЦИИ: {e}")
            logger.error("Проверьте API ключ в настройках")
            logger.warning("⚠️ Возвращаем оригинальный текст без обработки")
            logger.error("=" * 80)
            return text
        
        except APIConnectionError as e:
            logger.error("=" * 80)
            logger.error(f"🌐 ОШИБКА ПОДКЛЮЧЕНИЯ: {e}")
            logger.error(f"Не удалось подключиться к {base_url}")
            logger.error("Проверьте интернет-соединение и доступность API")
            logger.warning("⚠️ Возвращаем оригинальный текст без обработки")
            logger.error("=" * 80)
            return text
        
        except NotFoundError as e:
            logger.error("=" * 80)
            logger.error(f"🔍 МОДЕЛЬ НЕ НАЙДЕНА: {e}")
            logger.error(f"Модель '{model}' не существует для провайдера {provider}")
            logger.error("Проверьте название модели в настройках")
            logger.error("Доступные модели можно посмотреть в выпадающем списке")
            logger.warning("⚠️ Пробрасываем исключение для уведомления пользователя")
            logger.error("=" * 80)
            # Пробросить исключение чтобы TranscriptionThread мог показать уведомление
            raise
        
        except BadRequestError as e:
            logger.error("=" * 80)
            logger.error(f"❌ НЕВЕРНЫЙ ЗАПРОС: {e}")
            logger.error(f"Возможно модель '{model}' недоступна или параметры запроса некорректны")
            logger.error("Проверьте настройки постобработки")
            logger.warning("⚠️ Возвращаем оригинальный текст без обработки")
            logger.error("=" * 80)
            return text
        
        except KeyboardInterrupt:
            logger.error("=" * 80)
            logger.error("⚠️ ПРЕРВАНО ПОЛЬЗОВАТЕЛЕМ")
            logger.warning("⚠️ Возвращаем оригинальный текст без обработки")
            logger.error("=" * 80)
            return text
        
        except Exception as e:
            logger.error("=" * 80)
            logger.error(f"❌ ОШИБКА ПОСТОБРАБОТКИ: {e}")
            logger.error(f"Тип ошибки: {type(e).__name__}")
            import traceback
            logger.error(traceback.format_exc())
            logger.warning("⚠️ Возвращаем оригинальный текст без обработки")
            logger.error("=" * 80)
            # В случае ЛЮБОЙ ошибки возвращаем оригинальный текст
            return text



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
        model_not_found: Сигнал при ошибке "модель не найдена" (model: str, provider: str)
    
    Requirements: 9.2
    """
    
    # Сигналы
    transcription_complete = pyqtSignal(str)  # Транскрибированный текст
    transcription_error = pyqtSignal(Exception)  # Ошибка транскрипции
    model_not_found = pyqtSignal(str, str)  # Модель не найдена в постобработке (model, provider)
    transcription_model_not_found = pyqtSignal(str, str)  # Модель не найдена в транскрипции (model, provider)
    
    def __init__(self, audio_file_path: str, provider: str = "openai", api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None, statistics_manager=None):
        """
        Инициализирует поток транскрипции.
        
        Args:
            audio_file_path: Путь к аудио файлу для транскрипции
            provider: Провайдер AI (openai, groq, glm, custom)
            api_key: API ключ (опционально)
            base_url: Кастомный URL для API (для custom провайдера)
            model: Кастомная модель (для custom провайдера)
            statistics_manager: StatisticsManager для отслеживания статистики (опционально)
        """
        super().__init__()
        self.audio_file_path = audio_file_path
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.statistics_manager = statistics_manager
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
        
        transcribed_text = None
        
        try:
            logger.info(f"TranscriptionThread.run() начат для файла: {self.audio_file_path}")
            logger.info(f"Провайдер: {self.provider}")
            
            # Проверить настройку manual_stop и обрезать тишину если нужно
            from core.config import Config
            config = Config.load_from_env()
            
            removed_silence_duration = 0.0
            if config.manual_stop:
                logger.info("Режим ручной остановки: обрезка тишины...")
                from utils.audio_utils import trim_silence
                self.audio_file_path, removed_silence_duration = trim_silence(
                    self.audio_file_path, 
                    threshold=config.silence_threshold,
                    padding_ms=config.silence_padding
                )
                logger.info(f"Удалено тишины: {removed_silence_duration:.2f} секунд")
                
                # Track silence removal statistics if statistics_manager is available
                if self.statistics_manager and removed_silence_duration > 0:
                    logger.info(f"Отслеживание статистики удаления тишины: {removed_silence_duration:.2f}с")
                    self.statistics_manager.track_silence_removal(removed_silence_duration)
            
            # Создать клиент транскрипции
            logger.info(f"Создание TranscriptionClient для {self.provider}...")
            logger.info(f"Параметры: api_key={'***' if self.api_key else 'None'}, base_url={self.base_url}, model={self.model}")
            self.transcription_client = TranscriptionClient(
                provider=self.provider, 
                api_key=self.api_key,
                base_url=self.base_url,
                model=self.model
            )
            logger.info(f"TranscriptionClient создан успешно (модель: {self.transcription_client.model})")
            
            # Выполнить транскрипцию
            logger.info("Начало транскрипции...")
            try:
                text = self.transcription_client.transcribe_audio(self.audio_file_path)
                transcribed_text = text
                logger.info(f"Транскрипция завершена: {text[:50]}...")
            except NotFoundError as nf_error:
                logger.error(f"❌ Модель транскрипции не найдена: {nf_error}")
                logger.info("Отправка сигнала transcription_model_not_found для уведомления пользователя")
                # Отправить специальный сигнал для уведомления
                self.transcription_model_not_found.emit(self.transcription_client.model, self.provider)
                # Пробросить ошибку дальше чтобы остановить обработку
                raise
            
            # Process text through formatting and/or post-processing
            # Use ProcessingCoordinator to handle combined operations
            from services.window_monitor import WindowMonitor
            
            # Load formatting configuration
            formatting_config = FormattingConfig.from_env()
            
            # Create window monitor using factory method
            window_monitor = WindowMonitor.create()
            
            # Create formatting module
            formatting_module = FormattingModule(
                config_manager=None,
                ai_client_factory=None,
                window_monitor=window_monitor
            )
            formatting_module.config = formatting_config
            
            # Create processing coordinator
            coordinator = ProcessingCoordinator(
                formatting_module=formatting_module,
                config_manager=config
            )
            
            # Process the transcribed text
            try:
                transcribed_text = coordinator.process_transcription(
                    text=text,
                    transcription_client=self.transcription_client,
                    config=config
                )
            except NotFoundError as nf_error:
                logger.error(f"❌ Модель не найдена: {nf_error}")
                logger.info("Отправка сигнала model_not_found для уведомления пользователя")
                # Determine which model caused the error
                model_to_use = config.post_processing_custom_model if config.post_processing_custom_model else config.post_processing_model
                self.model_not_found.emit(model_to_use, config.post_processing_provider)
                logger.info("Используем оригинальный текст без обработки")
                # Continue with original text
            except Exception as processing_error:
                logger.error(f"❌ Ошибка обработки: {processing_error}")
                logger.info("Используем оригинальный текст без обработки")
                # Continue with original text
            
            # Отправить сигнал с результатом
            logger.info("Отправка сигнала transcription_complete")
            self.transcription_complete.emit(transcribed_text)
            
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
                    from core.config import Config, get_audio_recordings_dir, get_transcriptions_dir
                    from datetime import datetime
                    
                    config = Config.load_from_env()
                    
                    if config.keep_recordings:
                        # Создать имя файла с timestamp
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        base_filename = f"recording_{timestamp}"
                        
                        # Сохранить аудио файл в recordings/audio
                        audio_dir = get_audio_recordings_dir()
                        audio_filename = f"{base_filename}.wav"
                        audio_dest_path = audio_dir / audio_filename
                        
                        # Переместить аудио файл
                        shutil.move(self.audio_file_path, str(audio_dest_path))
                        logger.info(f"Запись сохранена: {audio_dest_path}")
                        
                        # Сохранить транскрипцию в recordings/transcriptions (если есть)
                        if transcribed_text:
                            transcriptions_dir = get_transcriptions_dir()
                            transcription_filename = f"{base_filename}.txt"
                            transcription_path = transcriptions_dir / transcription_filename
                            
                            # Записать текст в файл
                            transcription_path.write_text(transcribed_text, encoding='utf-8')
                            logger.info(f"Транскрипция сохранена: {transcription_path}")
                    else:
                        # Удалить временный файл с повторными попытками
                        import time
                        max_attempts = 3
                        for attempt in range(max_attempts):
                            try:
                                time.sleep(0.2 * (attempt + 1))  # Увеличивающаяся задержка: 0.2, 0.4, 0.6 сек
                                os.remove(self.audio_file_path)
                                logger.info(f"Временный файл удален: {self.audio_file_path}")
                                break
                            except PermissionError as pe:
                                if attempt < max_attempts - 1:
                                    logger.debug(f"Попытка {attempt + 1}/{max_attempts}: файл еще используется, ждем...")
                                    continue
                                else:
                                    raise pe
            except Exception as e:
                # Игнорировать ошибки удаления/перемещения файла
                logger.debug(f"Не удалось обработать временный файл: {e}")
