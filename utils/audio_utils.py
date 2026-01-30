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


def trim_silence(audio_file_path: str, threshold: float = 0.02, padding_ms: int = 100) -> str:
    """
    Удаляет ВСЮ тишину из аудио файла (в начале, середине и конце).
    
    Args:
        audio_file_path: Путь к аудио файлу (WAV)
        threshold: Порог RMS для определения тишины (по умолчанию 0.02)
        padding_ms: Паддинг в миллисекундах перед и после каждого блока тишины (по умолчанию 100ms)
    
    Returns:
        str: Путь к обрезанному файлу (тот же файл, перезаписанный)
    
    Raises:
        Exception: Если не удалось обработать файл
    """
    try:
        logger.info(f"Удаление тишины из файла: {audio_file_path}")
        logger.info(f"Порог: {threshold}, Паддинг: {padding_ms}ms")
        
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
        
        # Найти все чанки выше порога (это звук, не тишина)
        is_sound = rms_values > threshold
        
        if not np.any(is_sound):
            logger.warning("Весь файл состоит из тишины, не обрезаем")
            return audio_file_path
        
        # Вычислить паддинг в чанках
        padding_samples = int((padding_ms / 1000.0) * framerate)
        padding_chunks = max(1, padding_samples // chunk_size)
        
        logger.info(f"Паддинг: {padding_chunks} чанков ({padding_chunks * chunk_size / framerate * 1000:.0f}ms)")
        
        # Собрать все сегменты звука с паддингом
        segments = []
        in_sound = False
        start_chunk = 0
        
        for i in range(len(is_sound)):
            if is_sound[i] and not in_sound:
                # Начало звука
                start_chunk = max(0, i - padding_chunks)  # Добавить паддинг перед звуком
                in_sound = True
            elif not is_sound[i] and in_sound:
                # Конец звука
                end_chunk = min(len(is_sound), i + padding_chunks)  # Добавить паддинг после звука
                segments.append((start_chunk, end_chunk))
                in_sound = False
        
        # Если файл заканчивается звуком
        if in_sound:
            end_chunk = min(len(is_sound), len(is_sound) + padding_chunks)
            segments.append((start_chunk, end_chunk))
        
        logger.info(f"Найдено {len(segments)} сегментов звука")
        
        # Объединить все сегменты
        result_chunks = []
        for start, end in segments:
            start_sample = start * chunk_size
            end_sample = end * chunk_size
            
            if n_channels == 2:
                segment = audio_data[start_sample:end_sample]
            else:
                segment = audio_data[start_sample:end_sample]
            
            result_chunks.append(segment)
        
        if not result_chunks:
            logger.warning("Не найдено сегментов звука")
            return audio_file_path
        
        # Склеить все сегменты
        trimmed_audio = np.concatenate(result_chunks)
        
        # Сохранить обрезанный файл
        with wave.open(audio_file_path, 'wb') as wf:
            wf.setnchannels(n_channels)
            wf.setsampwidth(sampwidth)
            wf.setframerate(framerate)
            wf.writeframes(trimmed_audio.tobytes())
        
        duration_before = n_frames / framerate
        duration_after = len(trimmed_audio) / framerate
        trimmed_seconds = duration_before - duration_after
        
        logger.info(f"Тишина удалена: {trimmed_seconds:.2f} сек удалено")
        logger.info(f"Длительность: {duration_before:.2f}с -> {duration_after:.2f}с")
        logger.info(f"Сохранено {len(segments)} сегментов звука")
        
        return audio_file_path
        
    except Exception as e:
        logger.error(f"Ошибка удаления тишины: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # Вернуть исходный файл если не удалось обрезать
        return audio_file_path
