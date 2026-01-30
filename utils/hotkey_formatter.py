"""
Утилита для форматирования горячих клавиш в читаемый вид.

Этот модуль предоставляет класс HotkeyFormatter для преобразования
строковых представлений горячих клавиш в удобный для пользователя формат.
"""

from typing import List


class HotkeyFormatter:
    """Форматирование горячих клавиш для отображения"""
    
    # Маппинг специальных клавиш на символы
    SPECIAL_KEYS = {
        'space': '⎵Space',
        'enter': '↵Enter',
        'tab': '⇥Tab',
        'backspace': '⌫Backspace',
        'delete': '⌦Delete',
        'esc': 'Esc',
        'escape': 'Esc',
        'up': '↑',
        'down': '↓',
        'left': '←',
        'right': '→',
    }
    
    # Маппинг модификаторов
    MODIFIERS = {
        'ctrl': 'Ctrl',
        'control': 'Ctrl',
        'alt': 'Alt',
        'shift': 'Shift',
        'cmd': 'Cmd',
        'command': 'Cmd',
        'win': 'Win',
        'windows': 'Win',
    }
    
    @staticmethod
    def format_hotkey(hotkey: str) -> str:
        """
        Форматировать горячую клавишу в читаемый вид.
        
        Args:
            hotkey: Строка горячей клавиши (например, "ctrl+space", "f1")
        
        Returns:
            Отформатированная строка (например, "Ctrl+⎵Space", "F1")
        
        Examples:
            >>> HotkeyFormatter.format_hotkey("ctrl+space")
            "Ctrl+⎵Space"
            >>> HotkeyFormatter.format_hotkey("f1")
            "F1"
            >>> HotkeyFormatter.format_hotkey("ctrl+shift+a")
            "Ctrl+Shift+A"
        """
        if not hotkey:
            return ""
        
        # Разделить на части
        parts = hotkey.lower().split('+')
        formatted_parts: List[str] = []
        
        for part in parts:
            part = part.strip()
            
            # Проверить модификаторы
            if part in HotkeyFormatter.MODIFIERS:
                formatted_parts.append(HotkeyFormatter.MODIFIERS[part])
            
            # Проверить специальные клавиши
            elif part in HotkeyFormatter.SPECIAL_KEYS:
                formatted_parts.append(HotkeyFormatter.SPECIAL_KEYS[part])
            
            # Функциональные клавиши (F1-F12)
            elif part.startswith('f') and len(part) <= 3:
                try:
                    num = int(part[1:])
                    if 1 <= num <= 12:
                        formatted_parts.append(f'F{num}')
                    else:
                        formatted_parts.append(part.upper())
                except ValueError:
                    formatted_parts.append(part.upper())
            
            # Обычные клавиши
            else:
                formatted_parts.append(part.upper())
        
        return '+'.join(formatted_parts)
