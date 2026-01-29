"""
Unit-тесты для SilenceDetector.

Проверяет корректность определения тишины, адаптивного порога,
debouncing и сброса состояния.
"""

import pytest
from services.silence_detector import SilenceDetector


class TestSilenceDetectorInitialization:
    """Тесты инициализации детектора тишины."""
    
    def test_default_initialization(self):
        """Тест инициализации с параметрами по умолчанию."""
        detector = SilenceDetector()
        
        assert detector.threshold == 0.02
        assert detector.silence_duration == 1.5
        assert detector.min_speech_duration == 0.5
        assert detector.silence_start_time is None
        assert detector.background_noise_level == 0.0
        assert detector.last_speech_time is None
    
    def test_custom_initialization(self):
        """Тест инициализации с пользовательскими параметрами."""
        detector = SilenceDetector(
            threshold=0.03,
            silence_duration=2.0,
            min_speech_duration=0.7
        )
        
        assert detector.threshold == 0.03
        assert detector.silence_duration == 2.0
        assert detector.min_speech_duration == 0.7


class TestSilenceDetection:
    """Тесты обнаружения тишины."""
    
    def test_silence_not_detected_with_loud_audio(self):
        """Тест: тишина не обнаруживается при громком звуке."""
        detector = SilenceDetector(threshold=0.02, silence_duration=1.5)
        
        # Подаем громкие значения RMS
        for i in range(40):  # 2 секунды при 50ms обновлениях
            timestamp = i * 0.05
            result = detector.update(0.5, timestamp)
            assert result is False
    
    def test_silence_detected_after_duration(self):
        """Тест: тишина обнаруживается после заданной длительности."""
        detector = SilenceDetector(threshold=0.02, silence_duration=1.5)
        
        # Сначала речь, чтобы пройти debouncing
        for i in range(20):  # 1 секунда речи
            detector.update(0.5, i * 0.05)
        
        # Затем тишина
        silence_detected = False
        for i in range(20, 60):  # 2 секунды тишины
            timestamp = i * 0.05
            result = detector.update(0.01, timestamp)
            if result:
                silence_detected = True
                break
        
        assert silence_detected
    
    def test_silence_not_detected_before_duration(self):
        """Тест: тишина не обнаруживается до истечения длительности."""
        detector = SilenceDetector(threshold=0.02, silence_duration=1.5)
        
        # Подаем тихие значения, но меньше чем silence_duration
        for i in range(20):  # 1 секунда тишины (меньше 1.5)
            timestamp = i * 0.05
            result = detector.update(0.01, timestamp)
            assert result is False
    
    def test_silence_counter_resets_on_speech(self):
        """Тест: счетчик тишины сбрасывается при обнаружении речи."""
        detector = SilenceDetector(threshold=0.02, silence_duration=1.5)
        
        # Начинаем с речи
        for i in range(10):
            detector.update(0.5, i * 0.05)
        
        # Тишина на 1 секунду
        for i in range(10, 30):
            detector.update(0.01, i * 0.05)
        
        # Снова речь - должна сбросить счетчик
        detector.update(0.5, 1.5)
        
        # Проверяем, что счетчик сброшен
        assert detector.silence_start_time is None
        
        # Новая тишина должна начать отсчет заново
        for i in range(31, 65):  # Еще 1.7 секунды тишины
            timestamp = i * 0.05
            result = detector.update(0.01, timestamp)
            if result:
                break
        
        # Тишина должна быть обнаружена только после полных 1.5 секунд
        assert result


class TestDebouncing:
    """Тесты debouncing для игнорирования коротких пауз."""
    
    def test_short_pause_ignored(self):
        """Тест: короткие паузы (< 0.5 сек) игнорируются."""
        detector = SilenceDetector(
            threshold=0.02,
            silence_duration=1.5,
            min_speech_duration=0.5
        )
        
        # Речь
        for i in range(20):  # 1 секунда
            detector.update(0.5, i * 0.05)
        
        # Короткая пауза (0.4 секунды)
        for i in range(20, 28):
            detector.update(0.01, i * 0.05)
        
        # Снова речь
        for i in range(28, 48):
            detector.update(0.5, i * 0.05)
        
        # Длинная пауза (2 секунды)
        silence_detected = False
        for i in range(48, 88):
            timestamp = i * 0.05
            result = detector.update(0.01, timestamp)
            if result:
                silence_detected = True
                break
        
        # Тишина должна быть обнаружена после длинной паузы
        assert silence_detected
    
    def test_no_detection_at_recording_start(self):
        """Тест: тишина не обнаруживается сразу при запуске записи."""
        detector = SilenceDetector(
            threshold=0.02,
            silence_duration=1.5,
            min_speech_duration=0.5
        )
        
        # Подаем тишину с самого начала
        for i in range(40):  # 2 секунды тишины
            timestamp = i * 0.05
            result = detector.update(0.01, timestamp)
            # Не должно срабатывать в первые 0.5 секунды
            if timestamp < 0.5:
                assert result is False


class TestBackgroundNoiseCalibration:
    """Тесты калибровки фонового шума."""
    
    def test_calibrate_with_samples(self):
        """Тест калибровки с набором RMS значений."""
        detector = SilenceDetector()
        
        # Набор значений с фоновым шумом
        samples = [0.01, 0.015, 0.02, 0.012, 0.018, 0.5, 0.6]  # Последние два - выбросы
        
        detector.calibrate_background_noise(samples)
        
        # Фоновый шум должен быть вычислен из нижней половины
        assert detector.background_noise_level > 0
        assert detector.background_noise_level < 0.02  # Должен игнорировать выбросы
    
    def test_calibrate_with_empty_list(self):
        """Тест калибровки с пустым списком."""
        detector = SilenceDetector()
        
        detector.calibrate_background_noise([])
        
        # Фоновый шум должен остаться 0
        assert detector.background_noise_level == 0.0
    
    def test_adaptive_threshold_after_calibration(self):
        """Тест адаптивного порога после калибровки."""
        detector = SilenceDetector(threshold=0.02)
        
        # Калибруем с высоким фоновым шумом
        samples = [0.03, 0.035, 0.032, 0.028, 0.031]
        detector.calibrate_background_noise(samples)
        
        # Эффективный порог должен быть выше базового
        effective_threshold = detector._get_effective_threshold()
        assert effective_threshold > detector.threshold
        
        # Должен быть примерно background_noise * 2.0
        expected = detector.background_noise_level * detector.adaptive_multiplier
        assert abs(effective_threshold - expected) < 0.001
    
    def test_threshold_without_calibration(self):
        """Тест порога без калибровки."""
        detector = SilenceDetector(threshold=0.02)
        
        # Без калибровки должен использоваться базовый порог
        effective_threshold = detector._get_effective_threshold()
        assert effective_threshold == detector.threshold


class TestReset:
    """Тесты сброса состояния детектора."""
    
    def test_reset_clears_state(self):
        """Тест: reset() очищает все состояние."""
        detector = SilenceDetector()
        
        # Устанавливаем некоторое состояние
        detector.update(0.5, 0.0)
        detector.update(0.01, 0.5)
        detector.silence_start_time = 1.0
        detector.last_speech_time = 0.5
        
        # Сбрасываем
        detector.reset()
        
        # Проверяем, что все сброшено
        assert detector.silence_start_time is None
        assert detector.last_speech_time is None
        assert detector._first_update is True
        assert detector._recording_start_time is None
    
    def test_detector_works_after_reset(self):
        """Тест: детектор работает корректно после сброса."""
        detector = SilenceDetector(threshold=0.02, silence_duration=1.5)
        
        # Первая запись
        for i in range(20):
            detector.update(0.5, i * 0.05)
        
        # Сброс
        detector.reset()
        
        # Вторая запись должна работать нормально
        for i in range(20):
            detector.update(0.5, i * 0.05)
        
        silence_detected = False
        for i in range(20, 60):
            timestamp = i * 0.05
            result = detector.update(0.01, timestamp)
            if result:
                silence_detected = True
                break
        
        assert silence_detected


class TestEdgeCases:
    """Тесты граничных случаев."""
    
    def test_zero_rms_values(self):
        """Тест с нулевыми RMS значениями."""
        detector = SilenceDetector(threshold=0.02, silence_duration=1.5)
        
        # Речь
        for i in range(20):
            detector.update(0.5, i * 0.05)
        
        # Полная тишина (RMS = 0)
        silence_detected = False
        for i in range(20, 60):
            timestamp = i * 0.05
            result = detector.update(0.0, timestamp)
            if result:
                silence_detected = True
                break
        
        assert silence_detected
    
    def test_rms_exactly_at_threshold(self):
        """Тест с RMS точно на пороге."""
        detector = SilenceDetector(threshold=0.02, silence_duration=1.5)
        
        # Речь
        for i in range(20):
            detector.update(0.5, i * 0.05)
        
        # RMS точно на пороге (должно считаться речью, не тишиной)
        for i in range(20, 60):
            timestamp = i * 0.05
            result = detector.update(0.02, timestamp)
            assert result is False  # Не должно срабатывать
    
    def test_alternating_speech_and_silence(self):
        """Тест с чередующейся речью и тишиной."""
        detector = SilenceDetector(threshold=0.02, silence_duration=1.5)
        
        # Чередуем речь и короткую тишину
        for cycle in range(5):
            # Речь (0.5 сек)
            for i in range(10):
                timestamp = (cycle * 20 + i) * 0.05
                detector.update(0.5, timestamp)
            
            # Короткая тишина (0.5 сек)
            for i in range(10, 20):
                timestamp = (cycle * 20 + i) * 0.05
                result = detector.update(0.01, timestamp)
                # Не должно срабатывать на коротких паузах
                assert result is False
    
    def test_very_long_silence(self):
        """Тест с очень длинной тишиной."""
        detector = SilenceDetector(threshold=0.02, silence_duration=1.5)
        
        # Речь
        for i in range(20):
            detector.update(0.5, i * 0.05)
        
        # Очень длинная тишина (5 секунд)
        silence_detected = False
        detection_time = None
        for i in range(20, 120):
            timestamp = i * 0.05
            result = detector.update(0.01, timestamp)
            if result and not silence_detected:
                silence_detected = True
                detection_time = timestamp
                break
        
        assert silence_detected
        # Должно сработать примерно через 1.5 секунды после начала тишины
        assert detection_time is not None
        assert 2.4 < detection_time < 2.6  # 1 сек речи + 1.5 сек тишины
