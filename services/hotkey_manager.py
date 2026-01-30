"""
Менеджер глобальных горячих клавиш.

Использует библиотеку keyboard для регистрации и обработки глобальных горячих клавиш.
"""

import keyboard
from typing import Callable, Optional
from utils.logger import get_logger

logger = get_logger()


class HotkeyManager:
    """
    Менеджер глобальных горячих клавиш.
    
    Предоставляет интерфейс для регистрации глобальных горячих клавиш,
    которые работают независимо от того, какое приложение находится в фокусе.
    """
    
    def __init__(self, callback: Callable):
        """
        Инициализирует менеджер горячих клавиш.
        
        Args:
            callback: Функция, которая будет вызвана при нажатии основной горячей клавиши
        
        Requirements: 1.1, 1.4
        """
        self.hotkey: Optional[str] = None
        self.callback: Callable = callback
        self._is_registered: bool = False
        self._additional_hotkeys: dict = {}  # Дополнительные горячие клавиши
    
    def register_hotkey(self, key: str = "F1", callback: Optional[Callable] = None) -> bool:
        """
        Регистрирует глобальную горячую клавишу.
        
        Args:
            key: Клавиша для регистрации (по умолчанию F1)
            callback: Опциональный callback для этой клавиши (если None, используется основной)
        
        Returns:
            True если регистрация успешна, False в случае ошибки
        
        Requirements: 1.1, 1.2
        """
        try:
            # Если это основная клавиша и уже есть зарегистрированная - отменяем старую
            if callback is None and self._is_registered and self.hotkey:
                keyboard.remove_hotkey(self.hotkey)
                logger.info(f"Старая горячая клавиша {self.hotkey} отменена")
            
            # Определяем callback для этой клавиши
            key_callback = callback if callback else self._on_hotkey_pressed
            
            # Регистрируем горячую клавишу
            keyboard.add_hotkey(key, key_callback, suppress=False)
            
            # Если это основная клавиша
            if callback is None:
                self.hotkey = key
                self._is_registered = True
            else:
                # Сохраняем дополнительную клавишу
                self._additional_hotkeys[key] = callback
            
            logger.info(f"Горячая клавиша {key} успешно зарегистрирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка регистрации горячей клавиши {key}: {e}")
            return False
    
    def unregister_hotkey(self) -> None:
        """
        Отменяет регистрацию всех горячих клавиш.
        
        Requirements: 12.4
        """
        # Отменить основную клавишу
        if self._is_registered and self.hotkey:
            try:
                keyboard.remove_hotkey(self.hotkey)
                logger.info(f"Горячая клавиша {self.hotkey} отменена")
            except Exception as e:
                logger.error(f"Ошибка отмены регистрации горячей клавиши: {e}")
            finally:
                self._is_registered = False
                self.hotkey = None
        
        # Отменить дополнительные клавиши
        for key in list(self._additional_hotkeys.keys()):
            try:
                keyboard.remove_hotkey(key)
                logger.info(f"Дополнительная горячая клавиша {key} отменена")
            except Exception as e:
                logger.error(f"Ошибка отмены регистрации дополнительной клавиши {key}: {e}")
        
        self._additional_hotkeys.clear()
    
    def _on_hotkey_pressed(self) -> None:
        """
        Внутренний callback при нажатии горячей клавиши.
        
        Вызывает пользовательский callback в безопасном контексте.
        
        Requirements: 1.2, 1.4
        """
        try:
            self.callback()
        except Exception as e:
            logger.error(f"Ошибка в callback горячей клавиши: {e}")
    
    def is_registered(self) -> bool:
        """
        Проверяет, зарегистрирована ли горячая клавиша.
        
        Returns:
            True если горячая клавиша зарегистрирована, False иначе
        """
        return self._is_registered
    
    def get_current_hotkey(self) -> Optional[str]:
        """
        Возвращает текущую зарегистрированную горячую клавишу.
        
        Returns:
            Строка с названием клавиши или None если не зарегистрирована
        """
        return self.hotkey if self._is_registered else None
