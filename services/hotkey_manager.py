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
        self._format_selection_hotkey: Optional[str] = None  # Горячая клавиша выбора формата
        self._manual_format_hotkey: Optional[str] = None  # Горячая клавиша ручного форматирования
    
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
    
    def register_format_selection_hotkey(self, key: str, callback: Callable) -> bool:
        """
        Регистрирует горячую клавишу для выбора формата.
        
        Args:
            key: Комбинация клавиш (например, "ctrl+alt+space")
            callback: Функция, которая будет вызвана при нажатии горячей клавиши
        
        Returns:
            True если регистрация успешна, False в случае ошибки
        
        Requirements: 1.1, 1.2, 1.4, 10.2
        """
        try:
            # Если уже есть зарегистрированная клавиша выбора формата - отменяем старую
            if self._format_selection_hotkey:
                keyboard.remove_hotkey(self._format_selection_hotkey)
                if self._format_selection_hotkey in self._additional_hotkeys:
                    del self._additional_hotkeys[self._format_selection_hotkey]
                logger.info(f"Старая горячая клавиша выбора формата {self._format_selection_hotkey} отменена")
            
            # Регистрируем горячую клавишу
            keyboard.add_hotkey(key, callback, suppress=False)
            
            # Сохраняем клавишу выбора формата
            self._format_selection_hotkey = key
            self._additional_hotkeys[key] = callback
            
            logger.info(f"Горячая клавиша выбора формата {key} успешно зарегистрирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка регистрации горячей клавиши выбора формата {key}: {e}")
            
            # Try default binding as fallback
            default_key = "ctrl+alt+space"
            if key != default_key:
                logger.info(f"Попытка использовать дефолтную комбинацию: {default_key}")
                try:
                    keyboard.add_hotkey(default_key, callback, suppress=False)
                    self._format_selection_hotkey = default_key
                    self._additional_hotkeys[default_key] = callback
                    logger.info(f"Дефолтная горячая клавиша выбора формата {default_key} успешно зарегистрирована")
                    return True
                except Exception as fallback_error:
                    logger.error(f"Ошибка регистрации дефолтной горячей клавиши: {fallback_error}")
            
            # Log error and continue without format selection hotkey
            logger.warning("Продолжение работы без горячей клавиши выбора формата")
            return False
    
    def register_manual_format_hotkey(self, key: str, callback: Callable) -> bool:
        """
        Регистрирует горячую клавишу для ручного форматирования текста.
        
        Args:
            key: сочетание клавиш (например, "ctrl+shift+space")
            callback: функция, вызываемая при нажатии
        
        Returns:
            True если регистрация успешна, иначе False
        
        Requirements: 1.1, 1.2, 1.4
        """
        try:
            # Удаляем предыдущую горячую клавишу ручного форматирования
            if self._manual_format_hotkey:
                keyboard.remove_hotkey(self._manual_format_hotkey)
                if self._manual_format_hotkey in self._additional_hotkeys:
                    del self._additional_hotkeys[self._manual_format_hotkey]
                logger.info(
                    f"Старая горячая клавиша ручного форматирования {self._manual_format_hotkey} отменена"
                )
            
            # Регистрируем новую горячую клавишу
            keyboard.add_hotkey(key, callback, suppress=False)
            
            self._manual_format_hotkey = key
            self._additional_hotkeys[key] = callback
            
            logger.info(f"Горячая клавиша ручного форматирования {key} успешно зарегистрирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка регистрации горячей клавиши ручного форматирования {key}: {e}")
            
            # Попытка регистрации значения по умолчанию
            default_key = "ctrl+shift+space"
            if key != default_key:
                logger.info(f"Попытка регистрации значения по умолчанию: {default_key}")
                try:
                    keyboard.add_hotkey(default_key, callback, suppress=False)
                    self._manual_format_hotkey = default_key
                    self._additional_hotkeys[default_key] = callback
                    logger.info(
                        f"Резервная горячая клавиша ручного форматирования {default_key} успешно зарегистрирована"
                    )
                    return True
                except Exception as fallback_error:
                    logger.error(f"Ошибка регистрации резервной горячей клавиши: {fallback_error}")
            
            logger.warning("Горячая клавиша для ручного форматирования недоступна")
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
        
        # Отменить клавишу выбора формата
        if self._format_selection_hotkey:
            try:
                keyboard.remove_hotkey(self._format_selection_hotkey)
                logger.info(f"Горячая клавиша выбора формата {self._format_selection_hotkey} отменена")
                # Удалить из дополнительных клавиш, чтобы не обрабатывать дважды
                if self._format_selection_hotkey in self._additional_hotkeys:
                    del self._additional_hotkeys[self._format_selection_hotkey]
            except Exception as e:
                logger.error(f"Ошибка отмены регистрации клавиши выбора формата: {e}")
            finally:
                self._format_selection_hotkey = None

        if self._manual_format_hotkey:
            try:
                keyboard.remove_hotkey(self._manual_format_hotkey)
                logger.info(f"Горячая клавиша ручного форматирования {self._manual_format_hotkey} отменена")
                if self._manual_format_hotkey in self._additional_hotkeys:
                    del self._additional_hotkeys[self._manual_format_hotkey]
            except Exception as e:
                logger.error(f"Ошибка при удалении горячей клавиши ручного форматирования: {e}")
            finally:
                self._manual_format_hotkey = None
        
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
