"""
Утилиты для обработки аудио файлов.

Содержит функции для обрезки тишины, нормализации и других операций с аудио.
"""

import wave
import numpy as np
from pathlib import Path
from typing import Tuple
from utils.logger import get_logger

logger = get_logger()


def trim_silence(audio_file_path: str, threshold: float = 0.02) -> str:
    """
    Обрезает тишину в начале и конце аудио файла.
    
    Args:
        audio_file_path: Путь к аудио файлу (WAV)
        threshold: Порог RMS для определения тишины (по умолчанию 0.02)
    
    Returns:
        str: Путь к обрезанному файлу (тот же файл, перезаписанный)
    
    Raises:
        Exception: Если не удалось обработать файл
    """
    try:
        logger.info(f"Обрезка тишины в файле: {audio_file_path}")
        
        # Открыть WAV файл
        with wave.open(audio_file_path, 'rb') as wf:
            # Получить параметры
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            
            # Прочитать все фреймы
            frames = wf.readframes(n_frames)
        
        # Конвертировать в numpy array
        if sampwidth == 1:
            dtype = np.uint8
        elif sampwidth == 2:
            dtype = np.int16
        elif sampwidth == 4:
            dtype = np.int32
        else:
            raise ValueError(f"Неподдерживаемая ширина сэмпла: {sampwidth}")
        
        audio_data = np.frombuffer(frames, dtype=dtype)
        
        # Если стерео, преобразовать в моно для анализа
        if n_channels == 2:
            audio_data = audio_data.reshape(-1, 2)
            mono_data = audio_data.mean(axis=1)
        else:
            mono_data = audio_data
        
        # Нормализовать к диапазону [-1, 1]
        if dtype == np.uint8:
            mono_data = (mono_data.astype(np.float32) - 128) / 128
        else:
            max_val = np.iinfo(dtype).max
            mono_data = mono_data.astype(np.float32) / max_val
        
        # Вычислить RMS для каждого чанка (размер чанка = 1024 сэмпла)
        chunk_size = 1024
        n_chunks = len(mono_data) // chunk_size
        
        if n_chunks == 0:
            logger.warning("Файл слишком короткий для обрезки тишины")
            return audio_file_path
        
        rms_values = []
        for i in range(n_chunks):
            chunk = mono_data[i * chunk_size:(i + 1) * chunk_size]
            rms = np.sqrt(np.mean(chunk ** 2))
            rms_values.append(rms)
        
        rms_values = np.array(rms_values)
        
        # Найти первый и последний чанк выше порога
        above_threshold = rms_values > threshold
        
        if not np.any(above_threshold):
            logger.warning("Весь файл состоит из тишины, не обрезаем")
            return audio_file_path
        
        first_sound = np.argmax(above_threshold)
        last_sound = len(rms_values) - 1 - np.argmax(above_threshold[::-1])
        
        # Конвертировать индексы чанков в индексы сэмплов
        start_sample = first_sound * chunk_size
        end_sample = (last_sound + 1) * chunk_size
        
        # Обрезать аудио данные
        if n_channels == 2:
            trimmed_audio = audio_data[start_sample:end_sample]
        else:
            trimmed_audio = audio_data[start_sample:end_sample]
        
        # Сохранить обрезанный файл
        with wave.open(audio_file_path, 'wb') as wf:
            wf.setnchannels(n_channels)
            wf.setsampwidth(sampwidth)
            wf.setframerate(framerate)
            wf.writeframes(trimmed_audio.tobytes())
        
        duration_before = n_frames / framerate
        duration_after = len(trimmed_audio) / framerate
        trimmed_seconds = duration_before - duration_after
        
        logger.info(f"Тишина обрезана: {trimmed_seconds:.2f} сек удалено")
        logger.info(f"Длительность: {duration_before:.2f}с -> {duration_after:.2f}с")
        
        return audio_file_path
        
    except Exception as e:
        logger.error(f"Ошибка обрезки тишины: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # Вернуть исходный файл если не удалось обрезать
        return audio_file_path
