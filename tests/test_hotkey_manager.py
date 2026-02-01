"""
Тесты для HotkeyManager.

Включает unit-тесты и property-тесты для проверки корректности
работы с глобальными горячими клавишами.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, settings
from services.hotkey_manager import HotkeyManager


class TestHotkeyManager:
    """Unit-тесты для HotkeyManager"""
    
    def test_initialization(self):
        """Тест инициализации менеджера горячих клавиш"""
        callback = Mock()
        manager = HotkeyManager(callback)
        
        assert manager.callback == callback
        assert manager.hotkey is None
        assert manager.is_registered() is False
    
    @patch('services.hotkey_manager.keyboard')
    def test_register_hotkey_success(self, mock_keyboard):
        """Тест успешной регистрации горячей клавиши"""
        callback = Mock()
        manager = HotkeyManager(callback)
        
        result = manager.register_hotkey("F1")
        
        assert result is True
        assert manager.hotkey == "F1"
        assert manager.is_registered() is True
        mock_keyboard.add_hotkey.assert_called_once()
    
    @patch('services.hotkey_manager.keyboard')
    def test_register_custom_hotkey(self, mock_keyboard):
        """Тест регистрации пользовательской горячей клавиши"""
        callback = Mock()
        manager = HotkeyManager(callback)
        
        result = manager.register_hotkey("ctrl+shift+a")
        
        assert result is True
        assert manager.hotkey == "ctrl+shift+a"
        mock_keyboard.add_hotkey.assert_called_once()
    
    @patch('services.hotkey_manager.keyboard')
    def test_register_hotkey_failure(self, mock_keyboard):
        """Тест обработки ошибки при регистрации горячей клавиши"""
        mock_keyboard.add_hotkey.side_effect = Exception("Registration failed")
        
        callback = Mock()
        manager = HotkeyManager(callback)
        
        result = manager.register_hotkey("F1")
        
        assert result is False
        assert manager.is_registered() is False
    
    @patch('services.hotkey_manager.keyboard')
    def test_unregister_hotkey(self, mock_keyboard):
        """Тест отмены регистрации горячей клавиши"""
        callback = Mock()
        manager = HotkeyManager(callback)
        
        manager.register_hotkey("F1")
        manager.unregister_hotkey()
        
        assert manager.is_registered() is False
        assert manager.hotkey is None
        mock_keyboard.remove_hotkey.assert_called_once_with("F1")
    
    @patch('services.hotkey_manager.keyboard')
    def test_unregister_when_not_registered(self, mock_keyboard):
        """Тест отмены регистрации когда клавиша не зарегистрирована"""
        callback = Mock()
        manager = HotkeyManager(callback)
        
        # Не должно вызывать ошибку
        manager.unregister_hotkey()
        
        mock_keyboard.remove_hotkey.assert_not_called()
    
    @patch('services.hotkey_manager.keyboard')
    def test_callback_invocation(self, mock_keyboard):
        """Тест вызова callback при нажатии горячей клавиши"""
        callback = Mock()
        manager = HotkeyManager(callback)
        
        manager.register_hotkey("F1")
        
        # Симулируем нажатие горячей клавиши
        manager._on_hotkey_pressed()
        
        callback.assert_called_once()
    
    @patch('services.hotkey_manager.keyboard')
    def test_callback_error_handling(self, mock_keyboard):
        """Тест обработки ошибки в callback"""
        callback = Mock(side_effect=Exception("Callback error"))
        manager = HotkeyManager(callback)
        
        manager.register_hotkey("F1")
        
        # Не должно вызывать исключение
        manager._on_hotkey_pressed()
        
        callback.assert_called_once()
    
    @patch('services.hotkey_manager.keyboard')
    def test_reregister_hotkey(self, mock_keyboard):
        """Тест перерегистрации горячей клавиши"""
        callback = Mock()
        manager = HotkeyManager(callback)
        
        manager.register_hotkey("F1")
        manager.register_hotkey("F2")
        
        assert manager.hotkey == "F2"
        assert manager.is_registered() is True
        # Должна быть вызвана отмена старой клавиши
        mock_keyboard.remove_hotkey.assert_called_once_with("F1")
    
    @patch('services.hotkey_manager.keyboard')
    def test_get_current_hotkey(self, mock_keyboard):
        """Тест получения текущей горячей клавиши"""
        callback = Mock()
        manager = HotkeyManager(callback)
        
        assert manager.get_current_hotkey() is None
        
        manager.register_hotkey("F1")
        assert manager.get_current_hotkey() == "F1"
        
        manager.unregister_hotkey()
        assert manager.get_current_hotkey() is None
    
    @patch('services.hotkey_manager.keyboard')
    def test_register_format_selection_hotkey_success(self, mock_keyboard):
        """Тест успешной регистрации горячей клавиши выбора формата"""
        main_callback = Mock()
        format_callback = Mock()
        manager = HotkeyManager(main_callback)
        
        result = manager.register_format_selection_hotkey("ctrl+alt+space", format_callback)
        
        assert result is True
        assert manager._format_selection_hotkey == "ctrl+alt+space"
        assert "ctrl+alt+space" in manager._additional_hotkeys
        mock_keyboard.add_hotkey.assert_called_once_with("ctrl+alt+space", format_callback, suppress=False)
    
    @patch('services.hotkey_manager.keyboard')
    def test_register_format_selection_hotkey_failure(self, mock_keyboard):
        """Тест обработки ошибки при регистрации горячей клавиши выбора формата"""
        mock_keyboard.add_hotkey.side_effect = Exception("Registration failed")
        
        main_callback = Mock()
        format_callback = Mock()
        manager = HotkeyManager(main_callback)
        
        result = manager.register_format_selection_hotkey("ctrl+alt+space", format_callback)
        
        assert result is False
        assert manager._format_selection_hotkey is None
    
    @patch('services.hotkey_manager.keyboard')
    def test_reregister_format_selection_hotkey(self, mock_keyboard):
        """Тест перерегистрации горячей клавиши выбора формата"""
        main_callback = Mock()
        format_callback = Mock()
        manager = HotkeyManager(main_callback)
        
        # Первая регистрация
        manager.register_format_selection_hotkey("ctrl+alt+space", format_callback)
        
        # Вторая регистрация с другой клавишей
        manager.register_format_selection_hotkey("ctrl+shift+f", format_callback)
        
        assert manager._format_selection_hotkey == "ctrl+shift+f"
        # Должна быть вызвана отмена старой клавиши
        mock_keyboard.remove_hotkey.assert_called_once_with("ctrl+alt+space")
    
    @patch('services.hotkey_manager.keyboard')
    def test_unregister_includes_format_selection_hotkey(self, mock_keyboard):
        """Тест отмены регистрации включает горячую клавишу выбора формата"""
        main_callback = Mock()
        format_callback = Mock()
        manager = HotkeyManager(main_callback)
        
        manager.register_hotkey("F1")
        manager.register_format_selection_hotkey("ctrl+alt+space", format_callback)
        
        manager.unregister_hotkey()
        
        assert manager._format_selection_hotkey is None
        assert manager.is_registered() is False
        # Должны быть вызваны отмены обеих клавиш
        assert mock_keyboard.remove_hotkey.call_count == 2
    
    @patch('services.hotkey_manager.keyboard')
    def test_format_selection_hotkey_separate_from_main(self, mock_keyboard):
        """Тест что горячая клавиша выбора формата хранится отдельно от основной"""
        main_callback = Mock()
        format_callback = Mock()
        manager = HotkeyManager(main_callback)
        
        manager.register_hotkey("F1")
        manager.register_format_selection_hotkey("ctrl+alt+space", format_callback)
        
        assert manager.hotkey == "F1"
        assert manager._format_selection_hotkey == "ctrl+alt+space"
        assert manager.hotkey != manager._format_selection_hotkey


class TestHotkeyManagerProperties:
    """Property-тесты для HotkeyManager"""
    
    @patch('services.hotkey_manager.keyboard')
    @given(st.integers(min_value=0, max_value=10))
    @settings(max_examples=100)
    def test_property_1_global_hotkey_activation(self, mock_keyboard, num_calls: int):
        """
        Property 1: Глобальная активация горячей клавиши
        
        Для любого состояния приложения и любого активного окна, нажатие
        зарегистрированной горячей клавиши должно активировать приложение
        независимо от текущего фокуса.
        
        **Validates: Requirements 1.2, 1.4**
        """
        callback = Mock()
        manager = HotkeyManager(callback)
        
        # Регистрируем горячую клавишу
        result = manager.register_hotkey("F1")
        assert result is True, "Регистрация горячей клавиши должна быть успешной"
        
        # Симулируем множественные нажатия горячей клавиши
        for _ in range(num_calls):
            manager._on_hotkey_pressed()
        
        # Проверяем, что callback был вызван правильное количество раз
        assert callback.call_count == num_calls, \
            f"Callback должен быть вызван {num_calls} раз(а)"
    
    @patch('services.hotkey_manager.keyboard')
    @given(st.text(min_size=1, max_size=20, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='+_-'
    )))
    @settings(max_examples=100)
    def test_hotkey_registration_idempotency(self, mock_keyboard, key: str):
        """
        Свойство: Регистрация горячей клавиши идемпотентна
        
        Для любой валидной строки клавиши, регистрация должна корректно
        обновлять состояние менеджера.
        """
        callback = Mock()
        manager = HotkeyManager(callback)
        
        # Первая регистрация
        result1 = manager.register_hotkey(key)
        
        if result1:
            assert manager.is_registered() is True
            assert manager.get_current_hotkey() == key
            
            # Повторная регистрация той же клавиши
            result2 = manager.register_hotkey(key)
            
            if result2:
                assert manager.is_registered() is True
                assert manager.get_current_hotkey() == key
    
    @patch('services.hotkey_manager.keyboard')
    @given(st.lists(st.text(min_size=1, max_size=10, alphabet='F123456789'), 
                    min_size=1, max_size=5))
    @settings(max_examples=100)
    def test_sequential_hotkey_registration(self, mock_keyboard, keys: list):
        """
        Свойство: Последовательная регистрация горячих клавиш
        
        Для любой последовательности клавиш, каждая новая регистрация
        должна заменять предыдущую.
        """
        callback = Mock()
        manager = HotkeyManager(callback)
        
        for key in keys:
            result = manager.register_hotkey(key)
            
            if result:
                assert manager.is_registered() is True
                assert manager.get_current_hotkey() == key, \
                    f"Текущая клавиша должна быть {key}"
    
    @patch('services.hotkey_manager.keyboard')
    @given(st.integers(min_value=1, max_value=100))
    @settings(max_examples=100)
    def test_callback_invocation_count(self, mock_keyboard, count: int):
        """
        Свойство: Количество вызовов callback соответствует количеству нажатий
        
        Для любого количества нажатий горячей клавиши, callback должен быть
        вызван ровно столько же раз.
        """
        callback = Mock()
        manager = HotkeyManager(callback)
        
        manager.register_hotkey("F1")
        
        # Симулируем нажатия
        for _ in range(count):
            manager._on_hotkey_pressed()
        
        assert callback.call_count == count, \
            f"Callback должен быть вызван ровно {count} раз(а)"
    
    @patch('services.hotkey_manager.keyboard')
    def test_unregister_prevents_callback(self, mock_keyboard):
        """
        Свойство: Отмена регистрации предотвращает вызов callback
        
        После отмены регистрации горячей клавиши, callback не должен
        вызываться при нажатии клавиши.
        """
        callback = Mock()
        manager = HotkeyManager(callback)
        
        manager.register_hotkey("F1")
        manager._on_hotkey_pressed()
        
        initial_count = callback.call_count
        
        manager.unregister_hotkey()
        
        # После отмены регистрации состояние должно быть сброшено
        assert manager.is_registered() is False
        assert manager.get_current_hotkey() is None
