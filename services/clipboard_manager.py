"""
Менеджер буфера обмена для копирования и получения текста.

Использует pyperclip для кроссплатформенной работы с буфером обмена.
"""

import pyperclip
from typing import Optional


class ClipboardManager:
    """
    Менеджер буфера обмена.
    
    Предоставляет простой интерфейс для копирования текста в буфер обмена
    и получения текста из буфера обмена с обработкой ошибок.
    """
    
    @staticmethod
    def copy_to_clipboard(text: str) -> bool:
        """
        Копирует текст в буфер обмена.
        
        Args:
            text: Текст для копирования
        
        Returns:
            True если копирование успешно, False в случае ошибки
        
        Requirements: 8.2
        """
        try:
            pyperclip.copy(text)
            return True
        except Exception as e:
            # Логировать ошибку, но не прерывать работу приложения
            print(f"Ошибка копирования в буфер обмена: {e}")
            return False
    
    @staticmethod
    def get_from_clipboard() -> Optional[str]:
        """
        Получает текст из буфера обмена.
        
        Returns:
            Текст из буфера обмена или None в случае ошибки
        """
        try:
            return pyperclip.paste()
        except Exception as e:
            # Логировать ошибку
            print(f"Ошибка получения из буфера обмена: {e}")
            return None
    
    @staticmethod
    def is_available() -> bool:
        """
        Проверяет доступность буфера обмена.
        
        Returns:
            True если буфер обмена доступен, False иначе
        """
        try:
            # Попытка получить текст из буфера обмена
            pyperclip.paste()
            return True
        except Exception:
            return False
