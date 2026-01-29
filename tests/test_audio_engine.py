"""
Unit-тесты для AudioEngine.

Тестирует функциональность записи аудио, вычисления RMS
и сохранения в WAV файл.
"""

import pytest
import numpy as np
import wave
import os
from unittest.mock import Mock, patch, MagicMock
import pyaudio

from services.audio_engine import AudioEngine
from utils.exceptions import (
    MicrophoneUnavailableError,
    RecordingTooShortError,
    EmptyRecordingError,
    AudioDeviceError
)


class TestAudioEngineInitialization:
    """Тесты инициализации AudioEngine."""
    
    def test_initialization_with_correct_parameters(self):
        """
        Тест инициализации с правильными параметрами.
        
        Requirements: 3.2, 3.3
        """
        engine = AudioEngine()
        
        # Проверить параметры записи
        assert engine.sample_rate == 16000, "Sample rate должен быть 16000 Hz"
        assert engine.channels == 1, "Должен использоваться моно канал"
        assert engine.format == pyaudio.paInt16, "Формат должен быть int16"
        assert engine.chunk_size == 1024, "Chunk size должен быть 1024"
        
        # Проверить начальное состояние
        assert engine.is_recording is False, "Запись не должна быть активна"
        assert engine.audio_buffer == [], "Буфер должен быть пустым"
        assert engine.stream is None, "Поток должен быть None"
        assert engine.pyaudio_instance is None, "PyAudio instance должен быть None"


class TestAudioEngineRecording:
    """Тесты записи аудио."""
    
    @patch('pyaudio.PyAudio')
    def test_start_recording_opens_stream(self, mock_pyaudio_class):
        """
        Тест что start_recording открывает аудио поток.
        
        Requirements: 3.1
        """
        # Настроить мок
        mock_pyaudio = Mock()
        mock_stream = Mock()
        mock_pyaudio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_pyaudio
        
        engine = AudioEngine()
        engine.start_recording()
        
        # Проверить что PyAudio был инициализирован
        mock_pyaudio_class.assert_called_once()
        
        # Проверить что поток был открыт с правильными параметрами
        mock_pyaudio.open.assert_called_once()
        call_kwargs = mock_pyaudio.open.call_args[1]
        assert call_kwargs['format'] == pyaudio.paInt16
        assert call_kwargs['channels'] == 1
        assert call_kwargs['rate'] == 16000
        assert call_kwargs['input'] is True
        assert call_kwargs['frames_per_buffer'] == 1024
        
        # Проверить что поток был запущен
        mock_stream.start_stream.assert_called_once()
        assert engine.is_recording is True
    
    @patch('pyaudio.PyAudio')
    def test_start_recording_clears_buffer(self, mock_pyaudio_class):
        """
        Тест что start_recording очищает буфер перед новой записью.
        
        Requirements: 3.4
        """
        # Настроить мок
        mock_pyaudio = Mock()
        mock_stream = Mock()
        mock_pyaudio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_pyaudio
        
        engine = AudioEngine()
        engine.audio_buffer = [b'old_data']
        engine._current_rms = 0.5
        
        engine.start_recording()
        
        # Проверить что буфер был очищен
        assert engine.audio_buffer == []
        assert engine._current_rms == 0.0
    
    @patch('pyaudio.PyAudio')
    def test_microphone_unavailable_error(self, mock_pyaudio_class):
        """
        Тест обработки ошибки недоступного микрофона.
        
        Requirements: 3.6, 10.1
        """
        # Настроить мок для симуляции ошибки
        mock_pyaudio = Mock()
        mock_pyaudio.open.side_effect = OSError("device unavailable")
        mock_pyaudio_class.return_value = mock_pyaudio
        
        engine = AudioEngine()
        
        with pytest.raises(MicrophoneUnavailableError) as exc_info:
            engine.start_recording()
        
        assert "Микрофон недоступен" in str(exc_info.value.message)
        assert "Микрофон занят" in exc_info.value.user_message
    
    @patch('pyaudio.PyAudio')
    def test_audio_device_error(self, mock_pyaudio_class):
        """
        Тест обработки общей ошибки аудио устройства.
        
        Requirements: 10.1
        """
        # Настроить мок для симуляции другой ошибки
        mock_pyaudio = Mock()
        mock_pyaudio.open.side_effect = OSError("unknown error")
        mock_pyaudio_class.return_value = mock_pyaudio
        
        engine = AudioEngine()
        
        with pytest.raises(AudioDeviceError):
            engine.start_recording()


class TestAudioEngineStopRecording:
    """Тесты остановки записи."""
    
    @patch('pyaudio.PyAudio')
    def test_stop_recording_creates_wav_file(self, mock_pyaudio_class):
        """
        Тест создания WAV файла после остановки записи.
        
        Requirements: 3.5
        """
        # Настроить мок
        mock_pyaudio = Mock()
        mock_stream = Mock()
        mock_pyaudio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_pyaudio
        
        engine = AudioEngine()
        engine.start_recording()
        
        # Добавить достаточно данных (1 секунда)
        sample_data = np.zeros(16000, dtype=np.int16).tobytes()
        engine.audio_buffer = [sample_data]
        
        # Остановить запись
        filepath = engine.stop_recording()
        
        # Проверить что файл был создан
        assert os.path.exists(filepath), "WAV файл должен быть создан"
        assert filepath.endswith('.wav'), "Файл должен иметь расширение .wav"
        
        # Проверить параметры WAV файла
        with wave.open(filepath, 'rb') as wav_file:
            assert wav_file.getnchannels() == 1, "Должен быть моно канал"
            assert wav_file.getsampwidth() == 2, "Должен быть 16-bit (2 bytes)"
            assert wav_file.getframerate() == 16000, "Sample rate должен быть 16000 Hz"
        
        # Очистить временный файл
        os.remove(filepath)
        
        # Проверить что поток был закрыт
        mock_stream.stop_stream.assert_called_once()
        mock_stream.close.assert_called_once()
        mock_pyaudio.terminate.assert_called_once()
        assert engine.is_recording is False
    
    @patch('pyaudio.PyAudio')
    def test_empty_recording_error(self, mock_pyaudio_class):
        """
        Тест обработки пустого буфера.
        
        Requirements: 10.3
        """
        # Настроить мок
        mock_pyaudio = Mock()
        mock_stream = Mock()
        mock_pyaudio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_pyaudio
        
        engine = AudioEngine()
        engine.start_recording()
        
        # Буфер остается пустым
        engine.audio_buffer = []
        
        with pytest.raises(EmptyRecordingError):
            engine.stop_recording()
    
    @patch('pyaudio.PyAudio')
    def test_recording_too_short_error(self, mock_pyaudio_class):
        """
        Тест обработки слишком короткой записи.
        
        Requirements: 10.3
        """
        # Настроить мок
        mock_pyaudio = Mock()
        mock_stream = Mock()
        mock_pyaudio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_pyaudio
        
        engine = AudioEngine()
        engine.start_recording()
        
        # Добавить очень короткую запись (0.1 секунды)
        short_data = np.zeros(1600, dtype=np.int16).tobytes()
        engine.audio_buffer = [short_data]
        
        with pytest.raises(RecordingTooShortError) as exc_info:
            engine.stop_recording()
        
        assert "слишком короткая" in exc_info.value.user_message.lower()


class TestAudioEngineRMSCalculation:
    """Тесты вычисления RMS."""
    
    def test_calculate_rms_with_silence(self):
        """
        Тест вычисления RMS для тишины (нулевые значения).
        
        Requirements: 4.3
        """
        engine = AudioEngine()
        
        # Создать тишину (все нули)
        silence = np.zeros(1024, dtype=np.int16).tobytes()
        
        rms = engine._calculate_rms(silence)
        
        assert rms == 0.0, "RMS тишины должен быть 0.0"
    
    def test_calculate_rms_with_max_amplitude(self):
        """
        Тест вычисления RMS для максимальной амплитуды.
        
        Requirements: 4.3
        """
        engine = AudioEngine()
        
        # Создать максимальную амплитуду
        max_amplitude = np.full(1024, 32767, dtype=np.int16).tobytes()
        
        rms = engine._calculate_rms(max_amplitude)
        
        # RMS должен быть близок к 1.0 (32767 / 32768)
        assert 0.99 < rms <= 1.0, f"RMS максимальной амплитуды должен быть ~1.0, получено {rms}"
    
    def test_calculate_rms_formula_correctness(self):
        """
        Тест корректности формулы RMS: sqrt(mean(samples^2)) / 32768.0
        
        Requirements: 4.3
        Property 8: Корректность вычисления RMS
        """
        engine = AudioEngine()
        
        # Создать известные значения
        samples = np.array([100, 200, 300, 400, 500], dtype=np.int16)
        audio_data = samples.tobytes()
        
        # Вычислить RMS через движок
        calculated_rms = engine._calculate_rms(audio_data)
        
        # Вычислить ожидаемое значение вручную
        expected_rms = np.sqrt(np.mean(samples.astype(np.float64) ** 2)) / 32768.0
        
        # Проверить что значения совпадают с точностью до погрешности
        assert abs(calculated_rms - expected_rms) < 0.0001, \
            f"RMS должен быть {expected_rms}, получено {calculated_rms}"
    
    def test_get_current_rms(self):
        """
        Тест получения текущего RMS значения.
        
        Requirements: 4.3
        """
        engine = AudioEngine()
        
        # Установить RMS значение
        engine._current_rms = 0.5
        
        # Получить значение
        rms = engine.get_current_rms()
        
        assert rms == 0.5, "get_current_rms должен возвращать текущее RMS значение"


class TestAudioEngineCallback:
    """Тесты callback функции."""
    
    def test_audio_callback_adds_to_buffer(self):
        """
        Тест что callback добавляет данные в буфер.
        
        Requirements: 3.4
        """
        engine = AudioEngine()
        
        # Создать тестовые данные
        test_data = np.zeros(1024, dtype=np.int16).tobytes()
        
        # Вызвать callback
        result = engine._audio_callback(test_data, 1024, {}, 0)
        
        # Проверить что данные добавлены в буфер
        assert len(engine.audio_buffer) == 1
        assert engine.audio_buffer[0] == test_data
        
        # Проверить возвращаемое значение
        assert result == (test_data, pyaudio.paContinue)
    
    def test_audio_callback_updates_rms(self):
        """
        Тест что callback обновляет RMS значение.
        
        Requirements: 4.3
        """
        engine = AudioEngine()
        
        # Создать данные с известной амплитудой
        samples = np.full(1024, 1000, dtype=np.int16)
        test_data = samples.tobytes()
        
        # Вызвать callback
        engine._audio_callback(test_data, 1024, {}, 0)
        
        # Проверить что RMS был обновлен
        assert engine._current_rms > 0.0, "RMS должен быть обновлен"
        
        # Проверить что RMS соответствует ожидаемому значению
        expected_rms = 1000.0 / 32768.0
        assert abs(engine._current_rms - expected_rms) < 0.001


class TestAudioEngineCleanup:
    """Тесты очистки ресурсов."""
    
    @patch('pyaudio.PyAudio')
    def test_cleanup_stops_recording(self, mock_pyaudio_class):
        """
        Тест что cleanup останавливает запись.
        
        Requirements: 9.6, 12.2
        """
        # Настроить мок
        mock_pyaudio = Mock()
        mock_stream = Mock()
        mock_pyaudio.open.return_value = mock_stream
        mock_pyaudio_class.return_value = mock_pyaudio
        
        engine = AudioEngine()
        engine.start_recording()
        
        # Добавить данные в буфер
        engine.audio_buffer = [b'test_data']
        engine._current_rms = 0.5
        
        # Очистить ресурсы
        engine.cleanup()
        
        # Проверить что поток был остановлен
        mock_stream.stop_stream.assert_called_once()
        mock_stream.close.assert_called_once()
        mock_pyaudio.terminate.assert_called_once()
        
        # Проверить что состояние сброшено
        assert engine.is_recording is False
        assert engine.audio_buffer == []
        assert engine._current_rms == 0.0
    
    def test_cleanup_when_not_recording(self):
        """
        Тест что cleanup безопасен когда запись не активна.
        
        Requirements: 12.2
        """
        engine = AudioEngine()
        
        # Вызвать cleanup без активной записи
        engine.cleanup()  # Не должно вызвать ошибку
        
        assert engine.is_recording is False
        assert engine.audio_buffer == []


class TestAudioEngineSaveToWav:
    """Тесты сохранения в WAV файл."""
    
    def test_save_to_wav_creates_valid_file(self, tmp_path):
        """
        Тест создания валидного WAV файла.
        
        Requirements: 3.2, 3.5
        """
        engine = AudioEngine()
        
        # Создать тестовые данные (1 секунда)
        sample_data = np.zeros(16000, dtype=np.int16).tobytes()
        engine.audio_buffer = [sample_data]
        
        # Сохранить в файл
        filepath = tmp_path / "test_audio.wav"
        engine._save_to_wav(str(filepath))
        
        # Проверить что файл создан
        assert filepath.exists()
        
        # Проверить параметры WAV файла
        with wave.open(str(filepath), 'rb') as wav_file:
            assert wav_file.getnchannels() == 1
            assert wav_file.getsampwidth() == 2
            assert wav_file.getframerate() == 16000
            assert wav_file.getnframes() == 16000
    
    def test_save_to_wav_with_multiple_chunks(self, tmp_path):
        """
        Тест сохранения нескольких чанков в один файл.
        
        Requirements: 3.4, 3.5
        """
        engine = AudioEngine()
        
        # Создать несколько чанков
        chunk1 = np.zeros(1024, dtype=np.int16).tobytes()
        chunk2 = np.ones(1024, dtype=np.int16).tobytes()
        chunk3 = np.full(1024, 100, dtype=np.int16).tobytes()
        engine.audio_buffer = [chunk1, chunk2, chunk3]
        
        # Сохранить в файл
        filepath = tmp_path / "test_multi_chunk.wav"
        engine._save_to_wav(str(filepath))
        
        # Проверить что все чанки сохранены
        with wave.open(str(filepath), 'rb') as wav_file:
            assert wav_file.getnframes() == 3072  # 3 * 1024



# ============================================================================
# Property-Based Tests
# ============================================================================

from hypothesis import given, settings
from hypothesis import strategies as st


class TestAudioEngineRMSProperties:
    """Property-based тесты для вычисления RMS."""
    
    @given(st.lists(
        st.integers(min_value=-32768, max_value=32767),
        min_size=1,
        max_size=1024
    ))
    @settings(max_examples=100, deadline=None)
    def test_property_rms_calculation_correctness(self, samples):
        """
        Feature: rapid-whisper, Property 8: Корректность вычисления RMS
        
        Для любого аудио буфера с известными значениями, вычисленное RMS 
        должно равняться sqrt(mean(samples^2)) / 32768.0
        
        **Validates: Requirements 4.3**
        
        Этот property-тест проверяет, что формула RMS реализована корректно
        для любых возможных значений аудио сэмплов в диапазоне int16.
        """
        engine = AudioEngine()
        
        # Преобразовать список в numpy array и затем в bytes
        audio_array = np.array(samples, dtype=np.int16)
        audio_data = audio_array.tobytes()
        
        # Вычислить RMS через движок
        calculated_rms = engine._calculate_rms(audio_data)
        
        # Вычислить ожидаемое RMS значение по формуле
        # RMS = sqrt(mean(samples^2)) / 32768.0
        audio_float = audio_array.astype(np.float64)
        expected_rms = np.sqrt(np.mean(audio_float ** 2)) / 32768.0
        
        # Проверить что значения совпадают с точностью до погрешности
        # Используем относительную погрешность для малых значений
        if expected_rms > 0.0001:
            # Для больших значений используем относительную погрешность
            relative_error = abs(calculated_rms - expected_rms) / expected_rms
            assert relative_error < 0.0001, \
                f"RMS должен быть {expected_rms}, получено {calculated_rms}, " \
                f"относительная погрешность {relative_error}"
        else:
            # Для малых значений используем абсолютную погрешность
            absolute_error = abs(calculated_rms - expected_rms)
            assert absolute_error < 0.0001, \
                f"RMS должен быть {expected_rms}, получено {calculated_rms}, " \
                f"абсолютная погрешность {absolute_error}"
    
    @given(st.lists(
        st.integers(min_value=-32768, max_value=32767),
        min_size=1,
        max_size=1024
    ))
    @settings(max_examples=100, deadline=None)
    def test_property_rms_range(self, samples):
        """
        Property: RMS значение всегда в диапазоне [0.0, 1.0]
        
        Для любого аудио буфера, вычисленное RMS должно быть
        в диапазоне от 0.0 до 1.0 (включительно).
        
        **Validates: Requirements 4.3**
        """
        engine = AudioEngine()
        
        # Преобразовать в bytes
        audio_array = np.array(samples, dtype=np.int16)
        audio_data = audio_array.tobytes()
        
        # Вычислить RMS
        rms = engine._calculate_rms(audio_data)
        
        # Проверить диапазон
        assert 0.0 <= rms <= 1.0, \
            f"RMS должен быть в диапазоне [0.0, 1.0], получено {rms}"
    
    @given(st.integers(min_value=-32768, max_value=32767))
    @settings(max_examples=100, deadline=None)
    def test_property_rms_constant_signal(self, constant_value):
        """
        Property: RMS константного сигнала равен abs(value) / 32768.0
        
        Для любого константного сигнала (все сэмплы одинаковые),
        RMS должен равняться abs(value) / 32768.0
        
        **Validates: Requirements 4.3**
        """
        engine = AudioEngine()
        
        # Создать константный сигнал
        samples = np.full(100, constant_value, dtype=np.int16)
        audio_data = samples.tobytes()
        
        # Вычислить RMS
        calculated_rms = engine._calculate_rms(audio_data)
        
        # Ожидаемое значение для константного сигнала
        expected_rms = abs(constant_value) / 32768.0
        
        # Проверить
        assert abs(calculated_rms - expected_rms) < 0.0001, \
            f"RMS константного сигнала {constant_value} должен быть {expected_rms}, " \
            f"получено {calculated_rms}"
    
    @given(st.lists(
        st.integers(min_value=-32768, max_value=32767),
        min_size=1,
        max_size=1024
    ))
    @settings(max_examples=100, deadline=None)
    def test_property_rms_scaling(self, samples):
        """
        Property: Удвоение амплитуды удваивает RMS
        
        Для любого аудио сигнала, если удвоить все значения,
        RMS также должен удвоиться (с учетом ограничений int16).
        
        **Validates: Requirements 4.3**
        """
        engine = AudioEngine()
        
        # Создать оригинальный сигнал (ограничить диапазон для избежания переполнения)
        samples_limited = [s // 4 for s in samples]  # Делим на 4, чтобы можно было удвоить
        audio_array1 = np.array(samples_limited, dtype=np.int16)
        audio_data1 = audio_array1.tobytes()
        
        # Вычислить RMS оригинала
        rms1 = engine._calculate_rms(audio_data1)
        
        # Создать удвоенный сигнал
        audio_array2 = np.array([s * 2 for s in samples_limited], dtype=np.int16)
        audio_data2 = audio_array2.tobytes()
        
        # Вычислить RMS удвоенного сигнала
        rms2 = engine._calculate_rms(audio_data2)
        
        # Проверить что RMS удвоился (с учетом погрешности)
        if rms1 > 0.0001:  # Избегаем деления на очень малые числа
            ratio = rms2 / rms1
            assert abs(ratio - 2.0) < 0.01, \
                f"При удвоении амплитуды RMS должен удвоиться, " \
                f"получено соотношение {ratio}"
    
    @settings(max_examples=100, deadline=None)
    @given(st.integers(min_value=1, max_value=2048))
    def test_property_rms_silence(self, buffer_size):
        """
        Property: RMS тишины всегда равен 0.0
        
        Для любого размера буфера, заполненного нулями (тишина),
        RMS должен быть равен 0.0
        
        **Validates: Requirements 4.3**
        """
        engine = AudioEngine()
        
        # Создать тишину
        silence = np.zeros(buffer_size, dtype=np.int16)
        audio_data = silence.tobytes()
        
        # Вычислить RMS
        rms = engine._calculate_rms(audio_data)
        
        # Проверить что RMS равен 0
        assert rms == 0.0, \
            f"RMS тишины должен быть 0.0, получено {rms}"


class TestAudioEngineBufferGrowthProperties:
    """Property-based тесты для роста аудио буфера."""
    
    @given(st.lists(
        st.binary(min_size=1024, max_size=1024),  # Чанки фиксированного размера
        min_size=2,
        max_size=50
    ))
    @settings(max_examples=100, deadline=None)
    def test_property_buffer_growth_monotonic(self, audio_chunks):
        """
        Feature: rapid-whisper, Property 5: Рост аудио буфера
        
        Для любого активного процесса записи, размер аудио буфера должен 
        монотонно возрастать с течением времени.
        
        **Validates: Requirements 3.4**
        
        Этот property-тест проверяет, что при добавлении аудио чанков
        в буфер через callback, размер буфера монотонно увеличивается.
        """
        engine = AudioEngine()
        
        # Начальный размер буфера
        previous_buffer_size = 0
        
        # Симулировать последовательные вызовы callback
        for i, chunk in enumerate(audio_chunks):
            # Вызвать callback для добавления чанка в буфер
            engine._audio_callback(chunk, len(chunk) // 2, {}, 0)
            
            # Получить текущий размер буфера
            current_buffer_size = len(engine.audio_buffer)
            
            # Проверить что размер буфера увеличился
            assert current_buffer_size > previous_buffer_size, \
                f"Размер буфера должен монотонно возрастать: " \
                f"итерация {i}, предыдущий размер {previous_buffer_size}, " \
                f"текущий размер {current_buffer_size}"
            
            # Проверить что размер увеличился ровно на 1 элемент
            assert current_buffer_size == previous_buffer_size + 1, \
                f"Размер буфера должен увеличиваться на 1 при каждом callback: " \
                f"ожидалось {previous_buffer_size + 1}, получено {current_buffer_size}"
            
            # Обновить предыдущий размер
            previous_buffer_size = current_buffer_size
        
        # Проверить что финальный размер буфера равен количеству чанков
        assert len(engine.audio_buffer) == len(audio_chunks), \
            f"Финальный размер буфера должен равняться количеству чанков: " \
            f"ожидалось {len(audio_chunks)}, получено {len(engine.audio_buffer)}"
    
    @given(st.integers(min_value=1, max_value=100))
    @settings(max_examples=100, deadline=None)
    def test_property_buffer_growth_with_uniform_chunks(self, num_chunks):
        """
        Property: Рост буфера с одинаковыми чанками
        
        Для любого количества одинаковых аудио чанков, размер буфера
        должен линейно возрастать от 0 до num_chunks.
        
        **Validates: Requirements 3.4**
        """
        engine = AudioEngine()
        
        # Создать одинаковые чанки
        chunk = np.zeros(1024, dtype=np.int16).tobytes()
        
        # Отслеживать размеры буфера
        buffer_sizes = [0]  # Начальный размер
        
        # Добавить чанки
        for i in range(num_chunks):
            engine._audio_callback(chunk, 1024, {}, 0)
            buffer_sizes.append(len(engine.audio_buffer))
        
        # Проверить монотонный рост
        for i in range(1, len(buffer_sizes)):
            assert buffer_sizes[i] > buffer_sizes[i-1], \
                f"Размер буфера должен монотонно возрастать: " \
                f"buffer_sizes[{i}] = {buffer_sizes[i]}, " \
                f"buffer_sizes[{i-1}] = {buffer_sizes[i-1]}"
        
        # Проверить линейный рост (каждый шаг +1)
        for i in range(len(buffer_sizes)):
            assert buffer_sizes[i] == i, \
                f"Размер буфера должен расти линейно: " \
                f"на шаге {i} ожидалось {i}, получено {buffer_sizes[i]}"
    
    @given(
        st.lists(
            st.integers(min_value=512, max_value=2048),
            min_size=2,
            max_size=30
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_property_buffer_growth_with_variable_chunks(self, chunk_sizes):
        """
        Property: Рост буфера с чанками переменного размера
        
        Для любой последовательности чанков различного размера,
        размер буфера должен монотонно возрастать независимо от
        размера отдельных чанков.
        
        **Validates: Requirements 3.4**
        """
        engine = AudioEngine()
        
        previous_count = 0
        
        for i, size in enumerate(chunk_sizes):
            # Создать чанк указанного размера
            chunk = np.zeros(size, dtype=np.int16).tobytes()
            
            # Добавить в буфер
            engine._audio_callback(chunk, size, {}, 0)
            
            # Проверить что количество элементов в буфере увеличилось
            current_count = len(engine.audio_buffer)
            assert current_count == previous_count + 1, \
                f"Количество элементов в буфере должно увеличиваться на 1: " \
                f"итерация {i}, размер чанка {size}, " \
                f"предыдущее количество {previous_count}, " \
                f"текущее количество {current_count}"
            
            previous_count = current_count
    
    @given(st.integers(min_value=1, max_value=50))
    @settings(max_examples=100, deadline=None)
    def test_property_buffer_total_bytes_growth(self, num_chunks):
        """
        Property: Рост общего размера данных в буфере
        
        Для любого количества чанков, общий размер данных в байтах
        в буфере должен монотонно возрастать.
        
        **Validates: Requirements 3.4**
        """
        engine = AudioEngine()
        
        # Создать чанк фиксированного размера
        chunk_size = 1024
        chunk = np.zeros(chunk_size, dtype=np.int16).tobytes()
        
        previous_total_bytes = 0
        
        for i in range(num_chunks):
            # Добавить чанк
            engine._audio_callback(chunk, chunk_size, {}, 0)
            
            # Вычислить общий размер данных в буфере
            current_total_bytes = sum(len(c) for c in engine.audio_buffer)
            
            # Проверить монотонный рост
            assert current_total_bytes > previous_total_bytes, \
                f"Общий размер данных в буфере должен монотонно возрастать: " \
                f"итерация {i}, предыдущий размер {previous_total_bytes} байт, " \
                f"текущий размер {current_total_bytes} байт"
            
            # Проверить что размер увеличился на размер чанка
            expected_total = previous_total_bytes + len(chunk)
            assert current_total_bytes == expected_total, \
                f"Размер должен увеличиться на {len(chunk)} байт: " \
                f"ожидалось {expected_total}, получено {current_total_bytes}"
            
            previous_total_bytes = current_total_bytes
    
    @given(st.integers(min_value=1, max_value=100))
    @settings(max_examples=100, deadline=None)
    def test_property_buffer_never_shrinks(self, num_operations):
        """
        Property: Буфер никогда не уменьшается во время записи
        
        Для любого количества операций callback, размер буфера
        никогда не должен уменьшаться (только увеличиваться или оставаться прежним).
        
        **Validates: Requirements 3.4**
        """
        engine = AudioEngine()
        
        # Создать чанк
        chunk = np.zeros(1024, dtype=np.int16).tobytes()
        
        max_buffer_size = 0
        
        for i in range(num_operations):
            # Добавить чанк
            engine._audio_callback(chunk, 1024, {}, 0)
            
            # Получить текущий размер
            current_size = len(engine.audio_buffer)
            
            # Проверить что размер не уменьшился
            assert current_size >= max_buffer_size, \
                f"Размер буфера не должен уменьшаться: " \
                f"итерация {i}, максимальный размер {max_buffer_size}, " \
                f"текущий размер {current_size}"
            
            # Обновить максимальный размер
            max_buffer_size = max(max_buffer_size, current_size)
