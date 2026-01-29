"""
Модуль детектора тишины для автоматической остановки записи.

Детектор анализирует уровень громкости (RMS) аудио потока и определяет,
когда наступает тишина достаточной длительности для остановки записи.
"""

from typing import Optional, List
import time


class SilenceDetector:
    """
    Детектор тишины в аудио потоке.
    
    Анализирует RMS значения громкости и определяет моменты тишины
    с учетом адаптивного порога и debouncing для игнорирования коротких пауз.
    
    Attributes:
        threshold: Базовый порог RMS для определения тишины
        silence_duration: Длительность тишины в секундах для срабатывания
        min_speech_duration: Минимальная длительность речи для игнорирования коротких пауз
        silence_start_time: Время начала текущего периода тишины
        background_noise_level: Уровень фонового шума для адаптивного порога
        last_speech_time: Время последнего обнаружения речи
        adaptive_multiplier: Множитель для адаптивного порога
    """
    
    def __init__(
        self,
        threshold: float = 0.02,
        silence_duration: float = 1.5,
        min_speech_duration: float = 0.5
    ):
        """
        Инициализирует детектор тишины.
        
        Args:
            threshold: Базовый порог RMS для определения тишины (по умолчанию 0.02)
            silence_duration: Длительность тишины в секундах для срабатывания (по умолчанию 1.5)
            min_speech_duration: Минимальная длительность речи для debouncing (по умолчанию 0.5)
        """
        self.threshold = threshold
        self.silence_duration = silence_duration
        self.min_speech_duration = min_speech_duration
        
        self.silence_start_time: Optional[float] = None
        self.background_noise_level: float = 0.0
        self.last_speech_time: Optional[float] = None
        self.adaptive_multiplier: float = 2.0
        
        # Для отслеживания начала записи
        self._first_update = True
        self._recording_start_time: Optional[float] = None
    
    def update(self, rms: float, timestamp: float) -> bool:
        """
        Обновляет состояние детектора и проверяет наличие тишины.
        
        Анализирует текущее значение RMS и определяет, является ли это тишиной.
        Использует debouncing для игнорирования коротких пауз между словами.
        
        Args:
            rms: Текущее значение RMS громкости (0.0 - 1.0)
            timestamp: Временная метка в секундах
        
        Returns:
            True если обнаружена тишина достаточной длительности, иначе False
        """
        # Инициализация при первом обновлении
        if self._first_update:
            self._recording_start_time = timestamp
            self._first_update = False
        
        # Вычисляем адаптивный порог
        effective_threshold = self._get_effective_threshold()
        
        # Проверяем, является ли текущий уровень тишиной
        is_silent = rms < effective_threshold
        
        if is_silent:
            # Начинаем отсчет тишины, если еще не начали
            if self.silence_start_time is None:
                self.silence_start_time = timestamp
            
            # Проверяем длительность тишины
            silence_elapsed = timestamp - self.silence_start_time
            
            # Проверяем, что прошло достаточно времени с начала записи
            # и с момента последней речи (debouncing)
            if silence_elapsed >= self.silence_duration:
                # Проверяем debouncing: игнорируем короткие паузы
                if self.last_speech_time is not None:
                    time_since_speech = timestamp - self.last_speech_time
                    # Если с момента последней речи прошло меньше минимального времени,
                    # это короткая пауза - не срабатываем
                    if time_since_speech < self.min_speech_duration:
                        return False
                
                # Проверяем, что запись длится достаточно долго
                # (чтобы не срабатывать сразу при запуске)
                if self._recording_start_time is not None:
                    recording_duration = timestamp - self._recording_start_time
                    if recording_duration < self.min_speech_duration:
                        return False
                
                return True
        else:
            # Обнаружена речь - сбрасываем счетчик тишины
            self.silence_start_time = None
            self.last_speech_time = timestamp
        
        return False
    
    def calibrate_background_noise(self, rms_samples: List[float]) -> None:
        """
        Калибрует порог тишины на основе фонового шума.
        
        Анализирует набор RMS значений и вычисляет средний уровень
        фонового шума для адаптивного определения порога тишины.
        
        Args:
            rms_samples: Список RMS значений для анализа фонового шума
        """
        if not rms_samples:
            return
        
        # Вычисляем средний уровень как фоновый шум
        # Используем среднее значение нижних 50% значений
        # чтобы исключить выбросы от речи
        sorted_samples = sorted(rms_samples)
        lower_half = sorted_samples[:len(sorted_samples) // 2]
        
        if lower_half:
            self.background_noise_level = sum(lower_half) / len(lower_half)
        else:
            self.background_noise_level = sum(sorted_samples) / len(sorted_samples)
    
    def reset(self) -> None:
        """
        Сбрасывает состояние детектора.
        
        Очищает все временные метки и счетчики, возвращая детектор
        в начальное состояние для новой записи.
        """
        self.silence_start_time = None
        self.last_speech_time = None
        self._first_update = True
        self._recording_start_time = None
    
    def _get_effective_threshold(self) -> float:
        """
        Вычисляет эффективный порог с учетом фонового шума.
        
        Returns:
            Адаптивный порог тишины
        """
        if self.background_noise_level > 0:
            # Адаптивный порог: фоновый шум * множитель
            adaptive_threshold = self.background_noise_level * self.adaptive_multiplier
            # Используем максимум из базового и адаптивного порога
            return max(self.threshold, adaptive_threshold)
        else:
            # Если калибровка не проводилась, используем базовый порог
            return self.threshold
