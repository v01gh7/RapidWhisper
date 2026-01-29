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
            callback: Функция, которая будет вызвана при нажатии горячей клавиши
        
        Requirements: 1.1, 1.4
        """
        self.hotkey: Optional[str] = None
        self.callback: Callable = callback
        self._is_registered: bool = False
    
    def register_hotkey(self, key: str = "F1") -> bool:
        """
        Регистрирует глобальную горячую клавишу.
        
        Args:
            key: Клавиша для регистрации (по умолчанию F1)
        
        Returns:
            True если регистрация успешна, False в случае ошибки
        
        Requirements: 1.1, 1.2
        """
        try:
            # Если уже зарегистрирована другая клавиша, отменяем её
            if self._is_registered and self.hotkey:
                self.unregister_hotkey()
            
            # Регистрируем новую горячую клавишу
            keyboard.add_hotkey(key, self._on_hotkey_pressed, suppress=False)
            
            self.hotkey = key
            self._is_registered = True
            
            logger.info(f"Горячая клавиша {key} успешно зарегистрирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка регистрации горячей клавиши {key}: {e}")
            return False
    
    def unregister_hotkey(self) -> None:
        """
        Отменяет регистрацию горячей клавиши.
        
        Requirements: 12.4
        """
        if self._is_registered and self.hotkey:
            try:
                keyboard.remove_hotkey(self.hotkey)
                logger.info(f"Горячая клавиша {self.hotkey} отменена")
            except Exception as e:
                logger.error(f"Ошибка отмены регистрации горячей клавиши: {e}")
            finally:
                self._is_registered = False
                self.hotkey = None
    
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
