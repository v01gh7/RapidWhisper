"""
Тесты для ClipboardManager.

Включает unit-тесты и property-тесты для проверки корректности
работы с буфером обмена.
"""

import pytest
from hypothesis import given, strategies as st, settings
from services.clipboard_manager import ClipboardManager


class TestClipboardManager:
    """Unit-тесты для ClipboardManager"""
    
    def test_copy_to_clipboard_success(self):
        """Тест успешного копирования текста в буфер обмена"""
        text = "Test text for clipboard"
        result = ClipboardManager.copy_to_clipboard(text)
        
        assert result is True
        assert ClipboardManager.get_from_clipboard() == text
    
    def test_copy_empty_string(self):
        """Тест копирования пустой строки"""
        result = ClipboardManager.copy_to_clipboard("")
        
        assert result is True
        assert ClipboardManager.get_from_clipboard() == ""
    
    def test_copy_multiline_text(self):
        """Тест копирования многострочного текста"""
        text = "Line 1\nLine 2\nLine 3"
        result = ClipboardManager.copy_to_clipboard(text)
        
        assert result is True
        assert ClipboardManager.get_from_clipboard() == text
    
    def test_copy_unicode_text(self):
        """Тест копирования текста с Unicode символами"""
        text = "Привет мир! 你好世界 🌍"
        result = ClipboardManager.copy_to_clipboard(text)
        
        assert result is True
        assert ClipboardManager.get_from_clipboard() == text
    
    def test_get_from_clipboard_when_empty(self):
        """Тест получения из буфера обмена когда он пуст"""
        # Очистить буфер обмена
        ClipboardManager.copy_to_clipboard("")
        result = ClipboardManager.get_from_clipboard()
        
        assert result == ""
    
    def test_is_available(self):
        """Тест проверки доступности буфера обмена"""
        assert ClipboardManager.is_available() is True
    
    def test_copy_long_text(self):
        """Тест копирования длинного текста"""
        text = "A" * 10000
        result = ClipboardManager.copy_to_clipboard(text)
        
        assert result is True
        assert ClipboardManager.get_from_clipboard() == text


class TestClipboardManagerProperties:
    """Property-тесты для ClipboardManager"""
    
    @given(st.text(alphabet=st.characters(blacklist_characters='\x00', blacklist_categories=('Cc', 'Cs'))))
    @settings(max_examples=100)
    def test_property_22_copy_to_clipboard(self, text: str):
        """
        Property 22: Копирование в буфер обмена
        
        Для любого полученного текста транскрипции, полный текст должен быть
        скопирован в системный буфер обмена.
        
        **Validates: Requirements 8.2**
        """
        # Копируем текст в буфер обмена
        result = ClipboardManager.copy_to_clipboard(text)
        
        # Проверяем, что операция успешна
        assert result is True, "Копирование должно быть успешным"
        
        # Проверяем, что текст полностью скопирован
        clipboard_content = ClipboardManager.get_from_clipboard()
        assert clipboard_content == text, \
            f"Текст в буфере обмена должен совпадать с исходным текстом"
    
    @given(st.text(min_size=1, max_size=1000, alphabet=st.characters(blacklist_characters='\x00', blacklist_categories=('Cc', 'Cs'))))
    @settings(max_examples=100)
    def test_clipboard_preserves_content(self, text: str):
        """
        Свойство: Буфер обмена сохраняет содержимое без изменений
        
        Для любого непустого текста, содержимое буфера обмена должно
        точно соответствовать скопированному тексту.
        """
        ClipboardManager.copy_to_clipboard(text)
        retrieved = ClipboardManager.get_from_clipboard()
        
        assert retrieved == text, "Содержимое буфера обмена не должно изменяться"
    
    @given(st.text(alphabet=st.characters(blacklist_characters='\x00', blacklist_categories=('Cc', 'Cs'))), 
           st.text(alphabet=st.characters(blacklist_characters='\x00', blacklist_categories=('Cc', 'Cs'))))
    @settings(max_examples=100)
    def test_clipboard_overwrites_previous_content(self, text1: str, text2: str):
        """
        Свойство: Новое копирование перезаписывает предыдущее содержимое
        
        Для любых двух текстов, второе копирование должно полностью
        заменить содержимое первого копирования.
        """
        # Копируем первый текст
        ClipboardManager.copy_to_clipboard(text1)
        
        # Копируем второй текст
        ClipboardManager.copy_to_clipboard(text2)
        
        # Проверяем, что в буфере только второй текст
        clipboard_content = ClipboardManager.get_from_clipboard()
        assert clipboard_content == text2, \
            "Буфер обмена должен содержать только последний скопированный текст"
    
    @given(st.lists(st.text(alphabet=st.characters(blacklist_characters='\x00', blacklist_categories=('Cc', 'Cs'))), 
                    min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_clipboard_sequential_operations(self, texts: list):
        """
        Свойство: Последовательные операции копирования работают корректно
        
        Для любой последовательности текстов, каждая операция копирования
        должна корректно обновлять содержимое буфера обмена.
        """
        for text in texts:
            result = ClipboardManager.copy_to_clipboard(text)
            assert result is True, "Каждая операция копирования должна быть успешной"
            
            retrieved = ClipboardManager.get_from_clipboard()
            assert retrieved == text, \
                f"После копирования '{text}' буфер должен содержать этот текст"
    
    @given(st.text(alphabet=st.characters(blacklist_characters='\x00', blacklist_categories=('Cs',))))
    @settings(max_examples=100)
    def test_clipboard_handles_special_characters(self, text: str):
        """
        Свойство: Буфер обмена корректно обрабатывает специальные символы
        
        Для любого текста с различными Unicode символами, буфер обмена
        должен сохранять их без искажений.
        """
        result = ClipboardManager.copy_to_clipboard(text)
        assert result is True
        
        retrieved = ClipboardManager.get_from_clipboard()
        assert retrieved == text, \
            "Специальные символы должны сохраняться без искажений"
