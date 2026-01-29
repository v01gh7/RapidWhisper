"""
Unit-тесты для моделей данных.

Тестирует функциональность dataclass моделей AudioData, TranscriptionResult и ErrorInfo.
"""

import pytest
import os
import tempfile
import wave
from datetime import datetime
from models.data_models import AudioData, TranscriptionResult, ErrorInfo


class TestAudioData:
    """Тесты для класса AudioData."""
    
    def test_audio_data_creation(self):
        """Тест создания экземпляра AudioData."""
        audio_data = AudioData(
            sample_rate=16000,
            channels=1,
            frames=b'\x00\x01' * 1000,
            duration=2.5,
            rms_values=[0.1, 0.2, 0.3]
        )
        
        assert audio_data.sample_rate == 16000
        assert audio_data.channels == 1
        assert len(audio_data.frames) == 2000
        assert audio_data.duration == 2.5
        assert len(audio_data.rms_values) == 3
    
    def test_save_to_file_creates_wav(self):
        """Тест сохранения AudioData в WAV файл."""
        # Создать тестовые аудио данные (1 секунда тишины)
        sample_rate = 16000
        frames = b'\x00\x00' * sample_rate  # 1 секунда моно int16
        
        audio_data = AudioData(
            sample_rate=sample_rate,
            channels=1,
            frames=frames,
            duration=1.0,
            rms_values=[0.0]
        )
        
        # Сохранить в временный файл
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            audio_data.save_to_file(tmp_path)
            
            # Проверить, что файл создан
            assert os.path.exists(tmp_path)
            
            # Проверить параметры WAV файла
            with wave.open(tmp_path, 'rb') as wav_file:
                assert wav_file.getnchannels() == 1  # Моно
                assert wav_file.getsampwidth() == 2  # int16
                assert wav_file.getframerate() == 16000  # 16000 Hz
                assert wav_file.getnframes() == sample_rate  # 1 секунда
        finally:
            # Удалить временный файл
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def test_save_to_file_creates_directory(self):
        """Тест создания директории при сохранении файла."""
        audio_data = AudioData(
            sample_rate=16000,
            channels=1,
            frames=b'\x00\x00' * 1000,
            duration=0.1,
            rms_values=[0.0]
        )
        
        # Создать путь с несуществующей директорией
        with tempfile.TemporaryDirectory() as tmp_dir:
            nested_path = os.path.join(tmp_dir, 'subdir', 'test.wav')
            
            audio_data.save_to_file(nested_path)
            
            # Проверить, что файл создан
            assert os.path.exists(nested_path)
    
    def test_save_to_file_empty_path_raises_error(self):
        """Тест ошибки при пустом пути к файлу."""
        audio_data = AudioData(
            sample_rate=16000,
            channels=1,
            frames=b'\x00\x00' * 1000,
            duration=0.1,
            rms_values=[0.0]
        )
        
        with pytest.raises(ValueError, match="Путь к файлу не может быть пустым"):
            audio_data.save_to_file("")


class TestTranscriptionResult:
    """Тесты для класса TranscriptionResult."""
    
    def test_transcription_result_creation(self):
        """Тест создания экземпляра TranscriptionResult."""
        result = TranscriptionResult(
            text="Привет, мир!",
            duration=1.5,
            language="ru",
            confidence=0.95
        )
        
        assert result.text == "Привет, мир!"
        assert result.duration == 1.5
        assert result.language == "ru"
        assert result.confidence == 0.95
    
    def test_transcription_result_optional_fields(self):
        """Тест создания TranscriptionResult без опциональных полей."""
        result = TranscriptionResult(
            text="Тестовый текст",
            duration=2.0
        )
        
        assert result.text == "Тестовый текст"
        assert result.duration == 2.0
        assert result.language is None
        assert result.confidence is None
    
    def test_get_preview_short_text(self):
        """Тест получения превью для короткого текста."""
        result = TranscriptionResult(
            text="Короткий текст",
            duration=1.0
        )
        
        preview = result.get_preview(max_length=100)
        assert preview == "Короткий текст"
    
    def test_get_preview_long_text(self):
        """Тест усечения длинного текста."""
        long_text = "А" * 200
        result = TranscriptionResult(
            text=long_text,
            duration=5.0
        )
        
        preview = result.get_preview(max_length=100)
        assert len(preview) == 100
        assert preview == "А" * 100
    
    def test_get_preview_exact_length(self):
        """Тест текста точно равного max_length."""
        text = "Б" * 100
        result = TranscriptionResult(
            text=text,
            duration=2.0
        )
        
        preview = result.get_preview(max_length=100)
        assert len(preview) == 100
        assert preview == text
    
    def test_get_preview_custom_max_length(self):
        """Тест с пользовательским max_length."""
        result = TranscriptionResult(
            text="Это тестовый текст для проверки",
            duration=1.0
        )
        
        preview = result.get_preview(max_length=10)
        assert len(preview) == 10
        assert preview == "Это тестов"
    
    def test_get_preview_invalid_max_length(self):
        """Тест ошибки при некорректном max_length."""
        result = TranscriptionResult(
            text="Текст",
            duration=1.0
        )
        
        with pytest.raises(ValueError, match="max_length должен быть положительным числом"):
            result.get_preview(max_length=0)
        
        with pytest.raises(ValueError, match="max_length должен быть положительным числом"):
            result.get_preview(max_length=-1)


class TestErrorInfo:
    """Тесты для класса ErrorInfo."""
    
    def test_error_info_creation(self):
        """Тест создания экземпляра ErrorInfo."""
        timestamp = datetime.now()
        error_info = ErrorInfo(
            error_type="ValueError",
            message="Invalid value provided",
            user_message="Пожалуйста, проверьте введенные данные",
            timestamp=timestamp
        )
        
        assert error_info.error_type == "ValueError"
        assert error_info.message == "Invalid value provided"
        assert error_info.user_message == "Пожалуйста, проверьте введенные данные"
        assert error_info.timestamp == timestamp
    
    def test_log_to_file_creates_log(self):
        """Тест записи ошибки в лог файл."""
        timestamp = datetime(2024, 1, 15, 10, 30, 45)
        error_info = ErrorInfo(
            error_type="TestError",
            message="Test error message",
            user_message="Тестовое сообщение для пользователя",
            timestamp=timestamp
        )
        
        # Создать временный лог файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as tmp:
            tmp_path = tmp.name
        
        try:
            error_info.log_to_file(tmp_path)
            
            # Проверить, что файл существует и содержит правильные данные
            assert os.path.exists(tmp_path)
            
            with open(tmp_path, 'r', encoding='utf-8') as log_file:
                content = log_file.read()
                assert "[2024-01-15 10:30:45]" in content
                assert "TestError" in content
                assert "Test error message" in content
                assert "Тестовое сообщение для пользователя" in content
        finally:
            # Удалить временный файл
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def test_log_to_file_appends_to_existing(self):
        """Тест добавления ошибки в существующий лог файл."""
        timestamp1 = datetime(2024, 1, 15, 10, 0, 0)
        timestamp2 = datetime(2024, 1, 15, 11, 0, 0)
        
        error1 = ErrorInfo(
            error_type="Error1",
            message="First error",
            user_message="Первая ошибка",
            timestamp=timestamp1
        )
        
        error2 = ErrorInfo(
            error_type="Error2",
            message="Second error",
            user_message="Вторая ошибка",
            timestamp=timestamp2
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as tmp:
            tmp_path = tmp.name
        
        try:
            # Записать первую ошибку
            error1.log_to_file(tmp_path)
            
            # Записать вторую ошибку
            error2.log_to_file(tmp_path)
            
            # Проверить, что обе ошибки в файле
            with open(tmp_path, 'r', encoding='utf-8') as log_file:
                content = log_file.read()
                assert "Error1" in content
                assert "First error" in content
                assert "Error2" in content
                assert "Second error" in content
                
                # Проверить, что есть две строки
                lines = content.strip().split('\n')
                assert len(lines) == 2
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def test_log_to_file_creates_directory(self):
        """Тест создания директории при логировании."""
        error_info = ErrorInfo(
            error_type="TestError",
            message="Test message",
            user_message="Тест",
            timestamp=datetime.now()
        )
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            nested_path = os.path.join(tmp_dir, 'logs', 'subdir', 'test.log')
            
            error_info.log_to_file(nested_path)
            
            # Проверить, что файл создан
            assert os.path.exists(nested_path)
    
    def test_log_to_file_empty_path_raises_error(self):
        """Тест ошибки при пустом пути к лог файлу."""
        error_info = ErrorInfo(
            error_type="TestError",
            message="Test",
            user_message="Тест",
            timestamp=datetime.now()
        )
        
        with pytest.raises(ValueError, match="Путь к лог файлу не может быть пустым"):
            error_info.log_to_file("")
