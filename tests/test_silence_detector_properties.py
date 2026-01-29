"""
Property-based тесты для SilenceDetector.

Проверяет универсальные свойства корректности детектора тишины
с использованием Hypothesis для генерации разнообразных входных данных.
"""

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from services.silence_detector import SilenceDetector


# Настройка Hypothesis для минимум 100 итераций
settings.register_profile("rapidwhisper", max_examples=100, deadline=None)
settings.load_profile("rapidwhisper")


class TestProperty11ContinuousVolumeAnalysis:
    """
    Property 11: Непрерывный анализ громкости
    
    Для любого активного процесса записи, детектор тишины должен получать
    RMS обновления для каждого аудио чанка.
    
    **Validates: Requirements 5.1**
    """
    
    @given(
        st.lists(
            st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=200
        )
    )
    @settings(max_examples=100)
    def test_detector_processes_all_rms_updates(self, rms_values):
        """
        Feature: rapid-whisper, Property 11: Непрерывный анализ громкости
        
        Для любого активного процесса записи, детектор тишины должен получать
        RMS обновления для каждого аудио чанка и обрабатывать их без ошибок.
        """
        detector = SilenceDetector(threshold=0.02, silence_duration=1.5)
        
        # Детектор должен обработать все RMS значения без исключений
        processed_count = 0
        for i, rms in enumerate(rms_values):
            timestamp = i * 0.05  # 50ms между обновлениями
            try:
                result = detector.update(rms, timestamp)
                # Результат должен быть булевым
                assert isinstance(result, bool)
                processed_count += 1
            except Exception as e:
                pytest.fail(f"Detector failed to process RMS update: {e}")
        
        # Все значения должны быть обработаны
        assert processed_count == len(rms_values)


class TestProperty12SilenceDetectionByTime:
    """
    Property 12: Обнаружение тишины по времени
    
    Для любой последовательности RMS значений, где все значения ниже порога
    в течение 1.5 секунд, детектор должен инициировать остановку записи.
    
    **Validates: Requirements 5.2**
    """
    
    @given(
        # Генерируем последовательность тихих значений (ниже порога 0.02)
        st.lists(
            st.floats(min_value=0.0, max_value=0.019, allow_nan=False, allow_infinity=False),
            min_size=32,  # 32 обновления для гарантии > 1.5 секунд с учетом floating point
            max_size=100
        ),
        # Начальная речь для прохождения debouncing
        st.lists(
            st.floats(min_value=0.1, max_value=1.0, allow_nan=False, allow_infinity=False),
            min_size=10,  # 0.5 секунды речи
            max_size=20
        )
    )
    @settings(max_examples=100)
    def test_silence_detected_after_duration(self, silence_values, speech_values):
        """
        Feature: rapid-whisper, Property 12: Обнаружение тишины по времени
        
        Для любой последовательности RMS значений, где все значения ниже порога
        в течение 1.5 секунд, детектор должен инициировать остановку записи.
        """
        detector = SilenceDetector(threshold=0.02, silence_duration=1.5)
        
        # Сначала подаем речь для прохождения debouncing
        for i, rms in enumerate(speech_values):
            timestamp = i * 0.05
            detector.update(rms, timestamp)
        
        # Затем подаем тишину
        silence_detected = False
        detection_timestamp = None
        silence_start_timestamp = len(speech_values) * 0.05
        
        for i, rms in enumerate(silence_values):
            timestamp = silence_start_timestamp + i * 0.05
            result = detector.update(rms, timestamp)
            
            if result:
                silence_detected = True
                detection_timestamp = timestamp
                break
        
        # Тишина должна быть обнаружена
        assert silence_detected, "Silence should be detected after 1.5 seconds"
        
        # Проверяем, что обнаружение произошло примерно через 1.5 секунды
        # после начала тишины (с небольшим допуском)
        if detection_timestamp is not None:
            silence_duration = detection_timestamp - silence_start_timestamp
            assert silence_duration >= 1.5, \
                f"Silence detected too early: {silence_duration}s < 1.5s"
            assert silence_duration <= 1.6, \
                f"Silence detected too late: {silence_duration}s > 1.6s"
    
    @given(
        # Генерируем последовательность тихих значений короче 1.5 секунд
        st.lists(
            st.floats(min_value=0.0, max_value=0.019, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=29  # Меньше 1.5 секунд
        ),
        # Начальная речь
        st.lists(
            st.floats(min_value=0.1, max_value=1.0, allow_nan=False, allow_infinity=False),
            min_size=10,
            max_size=20
        )
    )
    @settings(max_examples=100)
    def test_silence_not_detected_before_duration(self, short_silence, speech_values):
        """
        Feature: rapid-whisper, Property 12: Обнаружение тишины по времени
        
        Для любой последовательности RMS значений ниже порога, но короче 1.5 секунд,
        детектор НЕ должен инициировать остановку записи.
        """
        detector = SilenceDetector(threshold=0.02, silence_duration=1.5)
        
        # Сначала речь
        for i, rms in enumerate(speech_values):
            timestamp = i * 0.05
            detector.update(rms, timestamp)
        
        # Затем короткая тишина
        silence_start = len(speech_values) * 0.05
        for i, rms in enumerate(short_silence):
            timestamp = silence_start + i * 0.05
            result = detector.update(rms, timestamp)
            
            # Не должно срабатывать
            assert result is False, \
                f"Silence detected too early at {timestamp - silence_start}s"


class TestProperty13AdaptiveThreshold:
    """
    Property 13: Адаптивный порог тишины
    
    Для любого уровня фонового шума, порог тишины должен вычисляться
    как background_noise_level * adaptive_multiplier.
    
    **Validates: Requirements 5.3**
    """
    
    @given(
        # Генерируем различные уровни фонового шума
        st.lists(
            st.floats(min_value=0.001, max_value=0.1, allow_nan=False, allow_infinity=False),
            min_size=5,
            max_size=20
        )
    )
    @settings(max_examples=100)
    def test_adaptive_threshold_calculation(self, noise_samples):
        """
        Feature: rapid-whisper, Property 13: Адаптивный порог тишины
        
        Для любого уровня фонового шума, порог тишины должен вычисляться
        как background_noise_level * adaptive_multiplier.
        """
        detector = SilenceDetector(threshold=0.02)
        
        # Калибруем детектор с фоновым шумом
        detector.calibrate_background_noise(noise_samples)
        
        # Получаем эффективный порог
        effective_threshold = detector._get_effective_threshold()
        
        # Вычисляем ожидаемый адаптивный порог
        expected_adaptive = detector.background_noise_level * detector.adaptive_multiplier
        
        # Эффективный порог должен быть максимумом из базового и адаптивного
        expected_threshold = max(detector.threshold, expected_adaptive)
        
        # Проверяем соответствие
        assert abs(effective_threshold - expected_threshold) < 0.0001, \
            f"Threshold mismatch: {effective_threshold} != {expected_threshold}"
    
    @given(
        # Генерируем высокий фоновый шум
        st.lists(
            st.floats(min_value=0.02, max_value=0.1, allow_nan=False, allow_infinity=False),
            min_size=5,
            max_size=20
        )
    )
    @settings(max_examples=100)
    def test_adaptive_threshold_higher_than_base(self, high_noise_samples):
        """
        Feature: rapid-whisper, Property 13: Адаптивный порог тишины
        
        Для высокого уровня фонового шума, адаптивный порог должен быть
        выше базового порога.
        """
        detector = SilenceDetector(threshold=0.02)
        
        # Калибруем с высоким шумом
        detector.calibrate_background_noise(high_noise_samples)
        
        # Эффективный порог должен быть выше базового
        effective_threshold = detector._get_effective_threshold()
        
        # Если фоновый шум достаточно высок, адаптивный порог должен быть больше
        if detector.background_noise_level * detector.adaptive_multiplier > detector.threshold:
            assert effective_threshold > detector.threshold, \
                "Adaptive threshold should be higher than base threshold for high noise"
    
    @given(
        # Генерируем низкий фоновый шум
        st.lists(
            st.floats(min_value=0.001, max_value=0.009, allow_nan=False, allow_infinity=False),
            min_size=5,
            max_size=20
        )
    )
    @settings(max_examples=100)
    def test_base_threshold_used_for_low_noise(self, low_noise_samples):
        """
        Feature: rapid-whisper, Property 13: Адаптивный порог тишины
        
        Для низкого уровня фонового шума, должен использоваться базовый порог.
        """
        detector = SilenceDetector(threshold=0.02)
        
        # Калибруем с низким шумом
        detector.calibrate_background_noise(low_noise_samples)
        
        # Эффективный порог должен быть равен базовому
        effective_threshold = detector._get_effective_threshold()
        
        # Для низкого шума адаптивный порог будет ниже базового,
        # поэтому должен использоваться базовый
        assert effective_threshold == detector.threshold, \
            "Base threshold should be used for low background noise"


class TestProperty14IgnoringShortPauses:
    """
    Property 14: Игнорирование коротких пауз
    
    Для любой последовательности RMS с паузами менее 0.5 секунды,
    детектор не должен инициировать остановку записи.
    
    **Validates: Requirements 5.4**
    """
    
    @given(
        # Генерируем короткую паузу (менее 0.5 секунды)
        st.lists(
            st.floats(min_value=0.0, max_value=0.019, allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=9  # 0.45 секунды максимум
        ),
        # Речь до паузы
        st.lists(
            st.floats(min_value=0.1, max_value=1.0, allow_nan=False, allow_infinity=False),
            min_size=10,
            max_size=30
        ),
        # Речь после паузы
        st.lists(
            st.floats(min_value=0.1, max_value=1.0, allow_nan=False, allow_infinity=False),
            min_size=10,
            max_size=30
        )
    )
    @settings(max_examples=100)
    def test_short_pauses_ignored(self, short_pause, speech_before, speech_after):
        """
        Feature: rapid-whisper, Property 14: Игнорирование коротких пауз
        
        Для любой последовательности RMS с паузами менее 0.5 секунды,
        детектор не должен инициировать остановку записи.
        """
        detector = SilenceDetector(
            threshold=0.02,
            silence_duration=1.5,
            min_speech_duration=0.5
        )
        
        timestamp = 0.0
        
        # Речь до паузы
        for rms in speech_before:
            result = detector.update(rms, timestamp)
            assert result is False, "Should not detect silence during speech"
            timestamp += 0.05
        
        # Короткая пауза
        for rms in short_pause:
            result = detector.update(rms, timestamp)
            assert result is False, "Should not detect silence during short pause"
            timestamp += 0.05
        
        # Речь после паузы
        for rms in speech_after:
            result = detector.update(rms, timestamp)
            assert result is False, "Should not detect silence after short pause"
            timestamp += 0.05
        
        # Счетчик тишины должен быть сброшен после короткой паузы
        # (проверяем косвенно через отсутствие срабатывания)
    
    @given(
        # Генерируем несколько коротких пауз
        st.integers(min_value=2, max_value=5),  # Количество пауз
        st.integers(min_value=3, max_value=9)   # Длина каждой паузы (0.15-0.45 сек)
    )
    @settings(max_examples=100)
    def test_multiple_short_pauses_ignored(self, num_pauses, pause_length):
        """
        Feature: rapid-whisper, Property 14: Игнорирование коротких пауз
        
        Для любой последовательности с несколькими короткими паузами,
        детектор не должен инициировать остановку записи.
        """
        detector = SilenceDetector(
            threshold=0.02,
            silence_duration=1.5,
            min_speech_duration=0.5
        )
        
        timestamp = 0.0
        
        # Чередуем речь и короткие паузы
        for _ in range(num_pauses):
            # Речь (0.5 секунды)
            for _ in range(10):
                result = detector.update(0.5, timestamp)
                assert result is False
                timestamp += 0.05
            
            # Короткая пауза
            for _ in range(pause_length):
                result = detector.update(0.01, timestamp)
                assert result is False, \
                    f"Should not detect silence during short pause at {timestamp}s"
                timestamp += 0.05
    
    @given(
        # Генерируем длинную паузу (больше 1.5 секунд)
        st.lists(
            st.floats(min_value=0.0, max_value=0.019, allow_nan=False, allow_infinity=False),
            min_size=32,  # 32 обновления для гарантии > 1.5 секунд с учетом floating point
            max_size=60
        ),
        # Речь до паузы
        st.lists(
            st.floats(min_value=0.1, max_value=1.0, allow_nan=False, allow_infinity=False),
            min_size=10,
            max_size=30
        )
    )
    @settings(max_examples=100)
    def test_long_pause_detected(self, long_pause, speech_before):
        """
        Feature: rapid-whisper, Property 14: Игнорирование коротких пауз
        
        Для любой последовательности с длинной паузой (>= 1.5 секунды),
        детектор ДОЛЖЕН инициировать остановку записи.
        """
        detector = SilenceDetector(
            threshold=0.02,
            silence_duration=1.5,
            min_speech_duration=0.5
        )
        
        timestamp = 0.0
        
        # Речь до паузы
        for rms in speech_before:
            detector.update(rms, timestamp)
            timestamp += 0.05
        
        # Длинная пауза
        silence_detected = False
        for rms in long_pause:
            result = detector.update(rms, timestamp)
            if result:
                silence_detected = True
                break
            timestamp += 0.05
        
        # Длинная пауза должна быть обнаружена
        assert silence_detected, \
            "Long pause (>= 1.5s) should be detected"


class TestPropertyCombinations:
    """
    Тесты комбинаций свойств для проверки взаимодействия.
    """
    
    @given(
        # Генерируем смешанную последовательность
        st.lists(
            st.tuples(
                st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
                st.booleans()  # True = речь, False = тишина
            ),
            min_size=50,
            max_size=200
        ),
        # Уровень фонового шума
        st.lists(
            st.floats(min_value=0.001, max_value=0.05, allow_nan=False, allow_infinity=False),
            min_size=5,
            max_size=20
        )
    )
    @settings(max_examples=100)
    def test_adaptive_threshold_with_mixed_sequence(self, mixed_sequence, noise_samples):
        """
        Комбинированный тест: адаптивный порог + смешанная последовательность.
        
        Проверяет, что детектор корректно работает с адаптивным порогом
        при различных паттернах речи и тишины.
        """
        detector = SilenceDetector(threshold=0.02, silence_duration=1.5)
        
        # Калибруем с фоновым шумом
        detector.calibrate_background_noise(noise_samples)
        
        timestamp = 0.0
        
        # Обрабатываем смешанную последовательность
        for rms_base, is_speech in mixed_sequence:
            # Модифицируем RMS в зависимости от типа
            if is_speech:
                rms = max(0.1, rms_base)  # Речь - громко
            else:
                rms = min(0.01, rms_base)  # Тишина - тихо
            
            try:
                result = detector.update(rms, timestamp)
                assert isinstance(result, bool)
            except Exception as e:
                pytest.fail(f"Detector failed with adaptive threshold: {e}")
            
            timestamp += 0.05
