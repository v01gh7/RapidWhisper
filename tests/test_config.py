"""
Unit-тесты для модуля конфигурации.

Тестирует загрузку конфигурации из .env файла, использование значений
по умолчанию и валидацию параметров.
"""

import os
import pytest
from pathlib import Path
from core.config import Config


class TestConfigDefaults:
    """Тесты значений по умолчанию."""
    
    def test_default_values(self):
        """Тест инициализации с значениями по умолчанию."""
        config = Config()
        
        assert config.glm_api_key == ""
        assert config.hotkey == "ctrl+space"
        assert config.silence_threshold == 0.02
        assert config.silence_duration == 1.5
        assert config.auto_hide_delay == 2.5
        assert config.window_width == 400
        assert config.window_height == 120
        assert config.sample_rate == 16000
        assert config.chunk_size == 1024
        assert config.log_level == "INFO"
        assert config.log_file == "rapidwhisper.log"


class TestConfigLoadFromEnv:
    """Тесты загрузки конфигурации из .env файла."""
    
    def test_load_all_parameters(self, tmp_path, monkeypatch):
        """Тест загрузки всех параметров из .env файла."""
        # Очистить все переменные окружения
        for key in ["GLM_API_KEY", "HOTKEY", "SILENCE_THRESHOLD", "SILENCE_DURATION", 
                    "AUTO_HIDE_DELAY", "WINDOW_WIDTH", "WINDOW_HEIGHT", "SAMPLE_RATE",
                    "CHUNK_SIZE", "LOG_LEVEL", "LOG_FILE", "GROQ_API_KEY", "OPENAI_API_KEY",
                    "CUSTOM_API_KEY", "AI_PROVIDER"]:
            monkeypatch.delenv(key, raising=False)
        
        env_file = tmp_path / ".env"
        env_content = """
AI_PROVIDER=groq
GROQ_API_KEY=test_key_123
HOTKEY=F2
SILENCE_THRESHOLD=0.03
SILENCE_DURATION=2.0
AUTO_HIDE_DELAY=3.0
WINDOW_WIDTH=500
WINDOW_HEIGHT=150
SAMPLE_RATE=44100
CHUNK_SIZE=2048
LOG_LEVEL=DEBUG
LOG_FILE=test.log
"""
        env_file.write_text(env_content)
        
        config = Config.load_from_env(str(env_file))
        
        assert config.groq_api_key == "test_key_123"
        assert config.hotkey == "F2"
        assert config.silence_threshold == 0.03
        assert config.silence_duration == 2.0
        assert config.auto_hide_delay == 3.0
        assert config.window_width == 500
        assert config.window_height == 150
        assert config.sample_rate == 44100
        assert config.chunk_size == 2048
        assert config.log_level == "DEBUG"
        assert config.log_file == "test.log"
    
    def test_load_only_required_parameters(self, tmp_path, monkeypatch):
        """Тест загрузки только обязательных параметров."""
        # Очистить все переменные окружения
        for key in ["GLM_API_KEY", "HOTKEY", "SILENCE_THRESHOLD", "SILENCE_DURATION", 
                    "AUTO_HIDE_DELAY", "WINDOW_WIDTH", "WINDOW_HEIGHT", "SAMPLE_RATE",
                    "CHUNK_SIZE", "LOG_LEVEL", "LOG_FILE", "GROQ_API_KEY"]:
            monkeypatch.delenv(key, raising=False)
        
        env_file = tmp_path / ".env"
        env_file.write_text("GROQ_API_KEY=test_key_456\n")
        
        config = Config.load_from_env(str(env_file))
        
        assert config.groq_api_key == "test_key_456"
        # Проверить, что остальные параметры имеют значения по умолчанию
        assert config.hotkey == "ctrl+space"
        assert config.silence_threshold == 0.02
        assert config.window_width == 400
    
    def test_load_partial_parameters(self, tmp_path, monkeypatch):
        """Тест загрузки части параметров."""
        # Очистить все переменные окружения
        for key in ["GLM_API_KEY", "HOTKEY", "SILENCE_THRESHOLD", "SILENCE_DURATION", 
                    "AUTO_HIDE_DELAY", "WINDOW_WIDTH", "WINDOW_HEIGHT", "SAMPLE_RATE",
                    "CHUNK_SIZE", "LOG_LEVEL", "LOG_FILE", "GROQ_API_KEY", "OPENAI_API_KEY",
                    "CUSTOM_API_KEY", "AI_PROVIDER"]:
            monkeypatch.delenv(key, raising=False)
        
        env_file = tmp_path / ".env"
        env_content = """
AI_PROVIDER=groq
GROQ_API_KEY=partial_key
HOTKEY=F3
WINDOW_WIDTH=600
"""
        env_file.write_text(env_content)
        
        config = Config.load_from_env(str(env_file))
        
        assert config.groq_api_key == "partial_key"
        assert config.hotkey == "F3"
        assert config.window_width == 600
        # Остальные параметры должны быть по умолчанию
        assert config.silence_threshold == 0.02
        assert config.auto_hide_delay == 2.5
        assert config.log_level == "INFO"
    
    def test_load_empty_env_file(self, tmp_path, monkeypatch):
        """Тест загрузки из пустого .env файла."""
        # Очистить все переменные окружения
        for key in ["GLM_API_KEY", "HOTKEY", "SILENCE_THRESHOLD", "SILENCE_DURATION", 
                    "AUTO_HIDE_DELAY", "WINDOW_WIDTH", "WINDOW_HEIGHT", "SAMPLE_RATE",
                    "CHUNK_SIZE", "LOG_LEVEL", "LOG_FILE", "GROQ_API_KEY"]:
            monkeypatch.delenv(key, raising=False)
        
        env_file = tmp_path / ".env"
        env_file.write_text("")
        
        config = Config.load_from_env(str(env_file))
        
        # Все параметры должны быть по умолчанию
        assert config.glm_api_key == ""
        assert config.hotkey == "ctrl+space"
        assert config.silence_threshold == 0.02
    
    def test_load_with_invalid_numeric_values(self, tmp_path, monkeypatch):
        """Тест обработки некорректных числовых значений."""
        # Очистить все переменные окружения
        for key in ["GLM_API_KEY", "HOTKEY", "SILENCE_THRESHOLD", "SILENCE_DURATION", 
                    "AUTO_HIDE_DELAY", "WINDOW_WIDTH", "WINDOW_HEIGHT", "SAMPLE_RATE",
                    "CHUNK_SIZE", "LOG_LEVEL", "LOG_FILE", "GROQ_API_KEY", "OPENAI_API_KEY",
                    "CUSTOM_API_KEY", "AI_PROVIDER"]:
            monkeypatch.delenv(key, raising=False)
        
        env_file = tmp_path / ".env"
        env_content = """
AI_PROVIDER=groq
GROQ_API_KEY=test_key
SILENCE_THRESHOLD=invalid
WINDOW_WIDTH=not_a_number
CHUNK_SIZE=abc
"""
        env_file.write_text(env_content)
        
        config = Config.load_from_env(str(env_file))
        
        # При ошибке парсинга должны использоваться значения по умолчанию
        assert config.silence_threshold == 0.02
        assert config.window_width == 400
        assert config.chunk_size == 1024
    
    def test_load_with_lowercase_log_level(self, tmp_path, monkeypatch):
        """Тест преобразования уровня логирования в верхний регистр."""
        # Очистить все переменные окружения
        for key in ["GLM_API_KEY", "HOTKEY", "SILENCE_THRESHOLD", "SILENCE_DURATION", 
                    "AUTO_HIDE_DELAY", "WINDOW_WIDTH", "WINDOW_HEIGHT", "SAMPLE_RATE",
                    "CHUNK_SIZE", "LOG_LEVEL", "LOG_FILE", "GROQ_API_KEY", "OPENAI_API_KEY",
                    "CUSTOM_API_KEY", "AI_PROVIDER"]:
            monkeypatch.delenv(key, raising=False)
        
        env_file = tmp_path / ".env"
        env_file.write_text("AI_PROVIDER=groq\nGROQ_API_KEY=test\nLOG_LEVEL=debug\n")
        
        config = Config.load_from_env(str(env_file))
        
        assert config.log_level == "DEBUG"
    
    def test_load_without_env_path(self, monkeypatch, tmp_path):
        """Тест загрузки с явным указанием пути к .env файлу."""
        # Очистить все переменные окружения
        for key in ["GLM_API_KEY", "HOTKEY", "SILENCE_THRESHOLD", "SILENCE_DURATION", 
                    "AUTO_HIDE_DELAY", "WINDOW_WIDTH", "WINDOW_HEIGHT", "SAMPLE_RATE",
                    "CHUNK_SIZE", "LOG_LEVEL", "LOG_FILE", "GROQ_API_KEY", "OPENAI_API_KEY",
                    "CUSTOM_API_KEY", "AI_PROVIDER"]:
            monkeypatch.delenv(key, raising=False)
        
        # Создать .env в изолированной директории
        env_file = tmp_path / ".env"
        env_file.write_text("AI_PROVIDER=groq\nGROQ_API_KEY=default_path_key\n")
        
        # Загрузить конфигурацию с явным указанием пути
        config = Config.load_from_env(str(env_file))
        
        assert config.groq_api_key == "default_path_key"


class TestConfigValidation:
    """Тесты валидации конфигурации."""
    
    def test_valid_configuration(self):
        """Тест валидации корректной конфигурации."""
        config = Config()
        config.ai_provider = "groq"
        config.groq_api_key = "valid_key"
        
        errors = config.validate()
        
        assert errors == []
    
    def test_missing_api_key(self):
        """Тест валидации при отсутствии API ключа."""
        config = Config()
        config.ai_provider = "groq"
        config.groq_api_key = ""
        
        errors = config.validate()
        
        assert len(errors) == 1
        assert "GROQ_API_KEY" in errors[0]
        assert "не найден" in errors[0]
    
    def test_invalid_silence_threshold_too_low(self):
        """Тест валидации слишком низкого порога тишины."""
        config = Config()
        config.ai_provider = "groq"
        config.groq_api_key = "valid_key"
        config.silence_threshold = 0.005
        
        errors = config.validate()
        
        assert len(errors) == 1
        assert "SILENCE_THRESHOLD" in errors[0]
        assert "0.01-0.1" in errors[0]
    
    def test_invalid_silence_threshold_too_high(self):
        """Тест валидации слишком высокого порога тишины."""
        config = Config()
        config.ai_provider = "groq"
        config.groq_api_key = "valid_key"
        config.silence_threshold = 0.15
        
        errors = config.validate()
        
        assert len(errors) == 1
        assert "SILENCE_THRESHOLD" in errors[0]
    
    def test_invalid_silence_duration(self):
        """Тест валидации некорректной длительности тишины."""
        config = Config()
        config.ai_provider = "groq"
        config.groq_api_key = "valid_key"
        config.silence_duration = 0.3
        
        errors = config.validate()
        
        assert len(errors) == 1
        assert "SILENCE_DURATION" in errors[0]
        assert "0.5-5.0" in errors[0]
    
    def test_invalid_auto_hide_delay(self):
        """Тест валидации некорректной задержки автоскрытия."""
        config = Config()
        config.ai_provider = "groq"
        config.groq_api_key = "valid_key"
        config.auto_hide_delay = 15.0
        
        errors = config.validate()
        
        assert len(errors) == 1
        assert "AUTO_HIDE_DELAY" in errors[0]
    
    def test_invalid_window_dimensions(self):
        """Тест валидации некорректных размеров окна."""
        config = Config()
        config.ai_provider = "groq"
        config.groq_api_key = "valid_key"
        config.window_width = 100
        config.window_height = 600
        
        errors = config.validate()
        
        assert len(errors) == 2
        assert any("WINDOW_WIDTH" in error for error in errors)
        assert any("WINDOW_HEIGHT" in error for error in errors)
    
    def test_invalid_sample_rate(self):
        """Тест валидации некорректной частоты дискретизации."""
        config = Config()
        config.ai_provider = "groq"
        config.groq_api_key = "valid_key"
        config.sample_rate = 22050
        
        errors = config.validate()
        
        assert len(errors) == 1
        assert "SAMPLE_RATE" in errors[0]
        assert "16000, 44100 или 48000" in errors[0]
    
    def test_invalid_chunk_size(self):
        """Тест валидации некорректного размера чанка."""
        config = Config()
        config.ai_provider = "groq"
        config.groq_api_key = "valid_key"
        config.chunk_size = 100
        
        errors = config.validate()
        
        assert len(errors) == 1
        assert "CHUNK_SIZE" in errors[0]
    
    def test_invalid_log_level(self):
        """Тест валидации некорректного уровня логирования."""
        config = Config()
        config.ai_provider = "groq"
        config.groq_api_key = "valid_key"
        config.log_level = "TRACE"
        
        errors = config.validate()
        
        assert len(errors) == 1
        assert "LOG_LEVEL" in errors[0]
    
    def test_multiple_validation_errors(self):
        """Тест валидации с несколькими ошибками."""
        config = Config()
        config.ai_provider = "groq"
        config.groq_api_key = ""
        config.silence_threshold = 0.005
        config.window_width = 50
        config.sample_rate = 8000
        
        errors = config.validate()
        
        assert len(errors) == 4
        assert any("GROQ_API_KEY" in error for error in errors)
        assert any("SILENCE_THRESHOLD" in error for error in errors)
        assert any("WINDOW_WIDTH" in error for error in errors)
        assert any("SAMPLE_RATE" in error for error in errors)


class TestConfigRepr:
    """Тесты строкового представления конфигурации."""
    
    def test_repr(self):
        """Тест строкового представления."""
        config = Config()
        config.ai_provider = "groq"
        config.groq_api_key = "test_key"
        
        repr_str = repr(config)
        
        assert "Config(" in repr_str
        assert "hotkey='ctrl+space'" in repr_str
        assert "silence_threshold=0.02" in repr_str
        assert "window_size=(400x120)" in repr_str
        assert "log_level='INFO'" in repr_str


class TestConfigIntegration:
    """Интеграционные тесты конфигурации."""
    
    def test_load_and_validate_valid_config(self, tmp_path, monkeypatch):
        """Тест загрузки и валидации корректной конфигурации."""
        # Очистить все переменные окружения
        for key in ["GLM_API_KEY", "HOTKEY", "SILENCE_THRESHOLD", "SILENCE_DURATION", 
                    "AUTO_HIDE_DELAY", "WINDOW_WIDTH", "WINDOW_HEIGHT", "SAMPLE_RATE",
                    "CHUNK_SIZE", "LOG_LEVEL", "LOG_FILE", "GROQ_API_KEY", "AI_PROVIDER"]:
            monkeypatch.delenv(key, raising=False)
        
        env_file = tmp_path / ".env"
        env_content = """
AI_PROVIDER=groq
GROQ_API_KEY=integration_test_key
HOTKEY=F4
SILENCE_THRESHOLD=0.025
WINDOW_WIDTH=450
"""
        env_file.write_text(env_content)
        
        config = Config.load_from_env(str(env_file))
        errors = config.validate()
        
        assert errors == []
        assert config.groq_api_key == "integration_test_key"
        assert config.hotkey == "F4"
    
    def test_load_and_validate_invalid_config(self, tmp_path, monkeypatch):
        """Тест загрузки и валидации некорректной конфигурации."""
        # Очистить все переменные окружения
        for key in ["GLM_API_KEY", "HOTKEY", "SILENCE_THRESHOLD", "SILENCE_DURATION", 
                    "AUTO_HIDE_DELAY", "WINDOW_WIDTH", "WINDOW_HEIGHT", "SAMPLE_RATE",
                    "CHUNK_SIZE", "LOG_LEVEL", "LOG_FILE", "GROQ_API_KEY", "AI_PROVIDER"]:
            monkeypatch.delenv(key, raising=False)
        
        env_file = tmp_path / ".env"
        env_content = """
AI_PROVIDER=groq
SILENCE_THRESHOLD=0.005
WINDOW_WIDTH=50
"""
        env_file.write_text(env_content)
        
        config = Config.load_from_env(str(env_file))
        errors = config.validate()
        
        assert len(errors) >= 2
        assert any("GROQ_API_KEY" in error for error in errors)



# ============================================================================
# Property-Based Tests
# ============================================================================

from hypothesis import given, assume, settings, HealthCheck
from hypothesis import strategies as st
import tempfile


class TestConfigPropertyBasedTests:
    """Property-based тесты для конфигурации."""
    
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        hotkey=st.text(min_size=1, max_size=10, alphabet=st.characters(min_codepoint=33, max_codepoint=126, blacklist_characters='\n\r\t"\'#=')),
        silence_threshold=st.floats(min_value=0.01, max_value=0.1, allow_nan=False, allow_infinity=False),
        silence_duration=st.floats(min_value=0.5, max_value=5.0, allow_nan=False, allow_infinity=False),
        auto_hide_delay=st.floats(min_value=1.0, max_value=10.0, allow_nan=False, allow_infinity=False),
        window_width=st.integers(min_value=200, max_value=1000),
        window_height=st.integers(min_value=80, max_value=500),
        sample_rate=st.sampled_from([16000, 44100, 48000]),
        chunk_size=st.integers(min_value=256, max_value=4096),
        log_level=st.sampled_from(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    )
    def test_property_32_parameter_configurability(
        self, tmp_path, monkeypatch,
        hotkey, silence_threshold, silence_duration, auto_hide_delay,
        window_width, window_height, sample_rate, chunk_size, log_level
    ):
        """
        **Validates: Requirements 11.2, 11.3, 11.4**
        
        Property 32: Настраиваемость параметров
        
        Для любого конфигурационного параметра (горячая клавиша, порог тишины, 
        время автоскрытия), значение должно загружаться из конфигурационного файла, 
        если оно там указано.
        
        Этот тест проверяет, что ANY валидное значение параметра из .env файла
        корректно загружается в объект Config.
        """
        # Очистить все переменные окружения
        for key in ["GLM_API_KEY", "HOTKEY", "SILENCE_THRESHOLD", "SILENCE_DURATION", 
                    "AUTO_HIDE_DELAY", "WINDOW_WIDTH", "WINDOW_HEIGHT", "SAMPLE_RATE",
                    "CHUNK_SIZE", "LOG_LEVEL", "LOG_FILE", "GROQ_API_KEY", "OPENAI_API_KEY", 
                    "CUSTOM_API_KEY", "AI_PROVIDER"]:
            monkeypatch.delenv(key, raising=False)
        
        # Создать .env файл с сгенерированными значениями
        env_file = tmp_path / ".env"
        env_content = f"""
AI_PROVIDER=groq
GROQ_API_KEY=test_api_key_property
HOTKEY={hotkey}
SILENCE_THRESHOLD={silence_threshold}
SILENCE_DURATION={silence_duration}
AUTO_HIDE_DELAY={auto_hide_delay}
WINDOW_WIDTH={window_width}
WINDOW_HEIGHT={window_height}
SAMPLE_RATE={sample_rate}
CHUNK_SIZE={chunk_size}
LOG_LEVEL={log_level}
"""
        env_file.write_text(env_content, encoding='utf-8')
        
        # Загрузить конфигурацию
        config = Config.load_from_env(str(env_file))
        
        # Проверить, что все значения загружены из файла
        assert config.hotkey == hotkey, f"Hotkey should be loaded from .env: expected {hotkey}, got {config.hotkey}"
        assert abs(config.silence_threshold - silence_threshold) < 0.0001, \
            f"Silence threshold should be loaded from .env: expected {silence_threshold}, got {config.silence_threshold}"
        assert abs(config.silence_duration - silence_duration) < 0.0001, \
            f"Silence duration should be loaded from .env: expected {silence_duration}, got {config.silence_duration}"
        assert abs(config.auto_hide_delay - auto_hide_delay) < 0.0001, \
            f"Auto hide delay should be loaded from .env: expected {auto_hide_delay}, got {config.auto_hide_delay}"
        assert config.window_width == window_width, \
            f"Window width should be loaded from .env: expected {window_width}, got {config.window_width}"
        assert config.window_height == window_height, \
            f"Window height should be loaded from .env: expected {window_height}, got {config.window_height}"
        assert config.sample_rate == sample_rate, \
            f"Sample rate should be loaded from .env: expected {sample_rate}, got {config.sample_rate}"
        assert config.chunk_size == chunk_size, \
            f"Chunk size should be loaded from .env: expected {chunk_size}, got {config.chunk_size}"
        assert config.log_level == log_level, \
            f"Log level should be loaded from .env: expected {log_level}, got {config.log_level}"
    
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        missing_params=st.lists(
            st.sampled_from([
                "HOTKEY", "SILENCE_THRESHOLD", "SILENCE_DURATION", 
                "AUTO_HIDE_DELAY", "WINDOW_WIDTH", "WINDOW_HEIGHT",
                "SAMPLE_RATE", "CHUNK_SIZE", "LOG_LEVEL"
            ]),
            min_size=1,
            max_size=9,
            unique=True
        )
    )
    def test_property_33_default_values(self, tmp_path, monkeypatch, missing_params):
        """
        **Validates: Requirements 11.5**
        
        Property 33: Значения по умолчанию
        
        Для любого отсутствующего конфигурационного параметра, должно 
        использоваться предопределенное значение по умолчанию.
        
        Этот тест проверяет, что ANY отсутствующий параметр получает
        корректное значение по умолчанию.
        """
        # Очистить все переменные окружения
        for key in ["GLM_API_KEY", "HOTKEY", "SILENCE_THRESHOLD", "SILENCE_DURATION", 
                    "AUTO_HIDE_DELAY", "WINDOW_WIDTH", "WINDOW_HEIGHT", "SAMPLE_RATE",
                    "CHUNK_SIZE", "LOG_LEVEL", "LOG_FILE", "GROQ_API_KEY", "OPENAI_API_KEY",
                    "CUSTOM_API_KEY", "AI_PROVIDER"]:
            monkeypatch.delenv(key, raising=False)
        
        # Определить значения по умолчанию
        defaults = {
            "HOTKEY": "ctrl+space",
            "SILENCE_THRESHOLD": 0.02,
            "SILENCE_DURATION": 1.5,
            "AUTO_HIDE_DELAY": 2.5,
            "WINDOW_WIDTH": 400,
            "WINDOW_HEIGHT": 120,
            "SAMPLE_RATE": 16000,
            "CHUNK_SIZE": 1024,
            "LOG_LEVEL": "INFO",
        }
        
        # Создать .env файл только с параметрами, которые НЕ отсутствуют
        env_file = tmp_path / ".env"
        env_content = "AI_PROVIDER=groq\nGROQ_API_KEY=test_key\n"
        
        # Добавить только те параметры, которые не в списке отсутствующих
        all_params = list(defaults.keys())
        present_params = [p for p in all_params if p not in missing_params]
        
        for param in present_params:
            # Использовать не-дефолтные значения для присутствующих параметров
            if param == "HOTKEY":
                env_content += f"{param}=F9\n"
            elif param == "SILENCE_THRESHOLD":
                env_content += f"{param}=0.05\n"
            elif param == "SILENCE_DURATION":
                env_content += f"{param}=3.0\n"
            elif param == "AUTO_HIDE_DELAY":
                env_content += f"{param}=5.0\n"
            elif param == "WINDOW_WIDTH":
                env_content += f"{param}=600\n"
            elif param == "WINDOW_HEIGHT":
                env_content += f"{param}=200\n"
            elif param == "SAMPLE_RATE":
                env_content += f"{param}=44100\n"
            elif param == "CHUNK_SIZE":
                env_content += f"{param}=2048\n"
            elif param == "LOG_LEVEL":
                env_content += f"{param}=DEBUG\n"
        
        env_file.write_text(env_content, encoding='utf-8')
        
        # Загрузить конфигурацию
        config = Config.load_from_env(str(env_file))
        
        # Проверить, что отсутствующие параметры имеют значения по умолчанию
        for param in missing_params:
            if param == "HOTKEY":
                assert config.hotkey == defaults[param], \
                    f"Missing {param} should use default value: expected {defaults[param]}, got {config.hotkey}"
            elif param == "SILENCE_THRESHOLD":
                assert abs(config.silence_threshold - defaults[param]) < 0.0001, \
                    f"Missing {param} should use default value: expected {defaults[param]}, got {config.silence_threshold}"
            elif param == "SILENCE_DURATION":
                assert abs(config.silence_duration - defaults[param]) < 0.0001, \
                    f"Missing {param} should use default value: expected {defaults[param]}, got {config.silence_duration}"
            elif param == "AUTO_HIDE_DELAY":
                assert abs(config.auto_hide_delay - defaults[param]) < 0.0001, \
                    f"Missing {param} should use default value: expected {defaults[param]}, got {config.auto_hide_delay}"
            elif param == "WINDOW_WIDTH":
                assert config.window_width == defaults[param], \
                    f"Missing {param} should use default value: expected {defaults[param]}, got {config.window_width}"
            elif param == "WINDOW_HEIGHT":
                assert config.window_height == defaults[param], \
                    f"Missing {param} should use default value: expected {defaults[param]}, got {config.window_height}"
            elif param == "SAMPLE_RATE":
                assert config.sample_rate == defaults[param], \
                    f"Missing {param} should use default value: expected {defaults[param]}, got {config.sample_rate}"
            elif param == "CHUNK_SIZE":
                assert config.chunk_size == defaults[param], \
                    f"Missing {param} should use default value: expected {defaults[param]}, got {config.chunk_size}"
            elif param == "LOG_LEVEL":
                assert config.log_level == defaults[param], \
                    f"Missing {param} should use default value: expected {defaults[param]}, got {config.log_level}"
    
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        invalid_float=st.one_of(
            st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=33, max_codepoint=126)).filter(
                lambda x: not x.replace('.', '', 1).replace('-', '', 1).replace('+', '', 1).replace('e', '', 1).replace('E', '', 1).isdigit()
            ),
            st.just("not_a_number"),
            st.just("abc123"),
            st.just("NaN"),
            st.just("inf"),
        ),
        invalid_int=st.one_of(
            st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=33, max_codepoint=126)).filter(
                lambda x: not x.lstrip('-+').isdigit()
            ),
            st.just("12.34"),
            st.just("xyz"),
            st.just("1e5"),
        ),
    )
    def test_property_33_defaults_on_invalid_values(self, tmp_path, monkeypatch, invalid_float, invalid_int):
        """
        **Validates: Requirements 11.5**
        
        Property 33: Значения по умолчанию (расширенный тест)
        
        Для любого некорректного значения конфигурационного параметра,
        должно использоваться предопределенное значение по умолчанию.
        
        Этот тест проверяет, что при ANY некорректном значении в .env файле
        используется значение по умолчанию.
        """
        # Очистить все переменные окружения
        for key in ["GLM_API_KEY", "HOTKEY", "SILENCE_THRESHOLD", "SILENCE_DURATION", 
                    "AUTO_HIDE_DELAY", "WINDOW_WIDTH", "WINDOW_HEIGHT", "SAMPLE_RATE",
                    "CHUNK_SIZE", "LOG_LEVEL", "LOG_FILE", "GROQ_API_KEY", "OPENAI_API_KEY",
                    "CUSTOM_API_KEY", "AI_PROVIDER"]:
            monkeypatch.delenv(key, raising=False)
        
        # Создать .env файл с некорректными значениями
        env_file = tmp_path / ".env"
        env_content = f"""
AI_PROVIDER=groq
GROQ_API_KEY=test_key
SILENCE_THRESHOLD={invalid_float}
SILENCE_DURATION={invalid_float}
AUTO_HIDE_DELAY={invalid_float}
WINDOW_WIDTH={invalid_int}
WINDOW_HEIGHT={invalid_int}
CHUNK_SIZE={invalid_int}
"""
        env_file.write_text(env_content, encoding='utf-8')
        
        # Загрузить конфигурацию
        config = Config.load_from_env(str(env_file))
        
        # Проверить, что используются значения по умолчанию
        assert abs(config.silence_threshold - 0.02) < 0.0001, \
            f"Invalid SILENCE_THRESHOLD should use default: expected 0.02, got {config.silence_threshold}"
        assert abs(config.silence_duration - 1.5) < 0.0001, \
            f"Invalid SILENCE_DURATION should use default: expected 1.5, got {config.silence_duration}"
        assert abs(config.auto_hide_delay - 2.5) < 0.0001, \
            f"Invalid AUTO_HIDE_DELAY should use default: expected 2.5, got {config.auto_hide_delay}"
        assert config.window_width == 400, \
            f"Invalid WINDOW_WIDTH should use default: expected 400, got {config.window_width}"
        assert config.window_height == 120, \
            f"Invalid WINDOW_HEIGHT should use default: expected 120, got {config.window_height}"
        assert config.chunk_size == 1024, \
            f"Invalid CHUNK_SIZE should use default: expected 1024, got {config.chunk_size}"
    
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        api_key=st.text(min_size=1, max_size=100, alphabet=st.characters(min_codepoint=33, max_codepoint=126, blacklist_characters='\n\r\t"\'#=')),
        hotkey=st.text(min_size=1, max_size=10, alphabet=st.characters(min_codepoint=33, max_codepoint=126, blacklist_characters='\n\r\t"\'#=')),
        log_file=st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=33, max_codepoint=126, blacklist_characters='\n\r\t/\\"\'#=')),
    )
    def test_property_32_string_parameters(self, tmp_path, monkeypatch, api_key, hotkey, log_file):
        """
        **Validates: Requirements 11.2**
        
        Property 32: Настраиваемость параметров (строковые параметры)
        
        Для любого строкового конфигурационного параметра, значение должно 
        загружаться из конфигурационного файла точно как указано.
        
        Этот тест проверяет, что ANY строковое значение корректно загружается.
        """
        # Очистить все переменные окружения
        for key in ["GLM_API_KEY", "HOTKEY", "SILENCE_THRESHOLD", "SILENCE_DURATION", 
                    "AUTO_HIDE_DELAY", "WINDOW_WIDTH", "WINDOW_HEIGHT", "SAMPLE_RATE",
                    "CHUNK_SIZE", "LOG_LEVEL", "LOG_FILE", "GROQ_API_KEY", "OPENAI_API_KEY",
                    "CUSTOM_API_KEY", "AI_PROVIDER"]:
            monkeypatch.delenv(key, raising=False)
        
        # Создать .env файл
        env_file = tmp_path / ".env"
        env_content = f"""
AI_PROVIDER=groq
GROQ_API_KEY={api_key}
HOTKEY={hotkey}
LOG_FILE={log_file}
"""
        env_file.write_text(env_content, encoding='utf-8')
        
        # Загрузить конфигурацию
        config = Config.load_from_env(str(env_file))
        
        # Проверить, что строковые значения загружены точно
        assert config.groq_api_key == api_key, \
            f"API key should be loaded exactly: expected '{api_key}', got '{config.groq_api_key}'"
        assert config.hotkey == hotkey, \
            f"Hotkey should be loaded exactly: expected '{hotkey}', got '{config.hotkey}'"
        assert config.log_file == log_file, \
            f"Log file should be loaded exactly: expected '{log_file}', got '{config.log_file}'"
