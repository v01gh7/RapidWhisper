"""
Виджет для захвата горячих клавиш.

Специальное поле ввода, которое автоматически захватывает нажатые клавиши
и отображает их как сочетание (например, Ctrl+Shift+R).
"""

from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent
from utils.i18n import t


class HotkeyInput(QLineEdit):
    """
    Поле ввода для захвата горячих клавиш.
    
    Автоматически захватывает нажатые клавиши и отображает их
    в формате, совместимом с библиотекой keyboard.
    
    Signals:
        hotkey_changed: Сигнал при изменении горячей клавиши
    """
    
    hotkey_changed = pyqtSignal(str)
    
    # Маппинг Qt клавиш на формат keyboard
    KEY_MAP = {
        Qt.Key.Key_Space: 'space',
        Qt.Key.Key_Return: 'enter',
        Qt.Key.Key_Enter: 'enter',
        Qt.Key.Key_Tab: 'tab',
        Qt.Key.Key_Backspace: 'backspace',
        Qt.Key.Key_Escape: 'esc',
        Qt.Key.Key_Delete: 'delete',
        Qt.Key.Key_Insert: 'insert',
        Qt.Key.Key_Home: 'home',
        Qt.Key.Key_End: 'end',
        Qt.Key.Key_PageUp: 'page up',
        Qt.Key.Key_PageDown: 'page down',
        Qt.Key.Key_Up: 'up',
        Qt.Key.Key_Down: 'down',
        Qt.Key.Key_Left: 'left',
        Qt.Key.Key_Right: 'right',
        Qt.Key.Key_F1: 'f1',
        Qt.Key.Key_F2: 'f2',
        Qt.Key.Key_F3: 'f3',
        Qt.Key.Key_F4: 'f4',
        Qt.Key.Key_F5: 'f5',
        Qt.Key.Key_F6: 'f6',
        Qt.Key.Key_F7: 'f7',
        Qt.Key.Key_F8: 'f8',
        Qt.Key.Key_F9: 'f9',
        Qt.Key.Key_F10: 'f10',
        Qt.Key.Key_F11: 'f11',
        Qt.Key.Key_F12: 'f12',
        # Специальные символы
        Qt.Key.Key_Slash: '/',
        Qt.Key.Key_Backslash: '\\',
        Qt.Key.Key_BracketLeft: '[',
        Qt.Key.Key_BracketRight: ']',
        Qt.Key.Key_BraceLeft: '{',
        Qt.Key.Key_BraceRight: '}',
        Qt.Key.Key_ParenLeft: '(',
        Qt.Key.Key_ParenRight: ')',
        Qt.Key.Key_Underscore: '_',
        Qt.Key.Key_Equal: '=',
        Qt.Key.Key_Plus: '+',
        Qt.Key.Key_Minus: '-',
        Qt.Key.Key_Asterisk: '*',
        Qt.Key.Key_Comma: ',',
        Qt.Key.Key_Period: '.',
        Qt.Key.Key_Semicolon: ';',
        Qt.Key.Key_Colon: ':',
        Qt.Key.Key_QuoteDbl: '"',
        Qt.Key.Key_Apostrophe: "'",
        Qt.Key.Key_Question: '?',
        Qt.Key.Key_Exclam: '!',
        Qt.Key.Key_At: '@',
        Qt.Key.Key_NumberSign: '#',
        Qt.Key.Key_Dollar: '$',
        Qt.Key.Key_Percent: '%',
        Qt.Key.Key_AsciiCircum: '^',
        Qt.Key.Key_Ampersand: '&',
        Qt.Key.Key_Bar: '|',
        Qt.Key.Key_AsciiTilde: '~',
        Qt.Key.Key_QuoteLeft: '`',
        Qt.Key.Key_Less: '<',
        Qt.Key.Key_Greater: '>',
    }
    
    def __init__(self, parent=None):
        """
        Инициализирует поле ввода горячей клавиши.
        
        Args:
            parent: Родительский виджет
        """
        super().__init__(parent)
        
        # Установить placeholder
        self.setPlaceholderText(t("settings.app.hotkey_placeholder"))
        
        # Сделать поле только для чтения (нельзя вводить текст вручную)
        self.setReadOnly(True)
        
        # Установить курсор
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Обрабатывает нажатие клавиши.
        
        Захватывает нажатые клавиши и формирует строку горячей клавиши.
        Поддерживает любые символы независимо от раскладки клавиатуры.
        
        Args:
            event: Событие нажатия клавиши
        """
        # Получить модификаторы
        modifiers = event.modifiers()
        key = event.key()
        
        # Игнорировать только модификаторы без основной клавиши
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
            return
        
        # Собрать части горячей клавиши
        parts = []
        
        # Добавить модификаторы
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            parts.append('ctrl')
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            parts.append('shift')
        if modifiers & Qt.KeyboardModifier.AltModifier:
            parts.append('alt')
        
        # Добавить основную клавишу
        key_part = None
        
        # Сначала проверяем специальные клавиши (F1-F12, стрелки, и т.д.)
        if key in self.KEY_MAP:
            key_part = self.KEY_MAP[key]
        else:
            # Попробовать получить текст клавиши (работает для любой раскладки)
            text = event.text()
            
            if text and text.isprintable() and not text.isspace():
                # Используем реальный символ, который был нажат
                # Это работает для любой раскладки клавиатуры
                key_part = text.lower()
            elif Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
                # Буквы A-Z (fallback если text пустой)
                key_part = chr(key).lower()
            elif Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
                # Цифры 0-9
                key_part = chr(key)
            else:
                # Для неизвестных клавиш используем nativeScanCode
                # Это позволит работать с любыми устройствами ввода
                scan_code = event.nativeScanCode()
                if scan_code > 0:
                    # Используем scan code для уникальной идентификации клавиши
                    key_part = f"scan_{scan_code}"
                else:
                    # Последний fallback - используем key code
                    key_part = f"key_{key}"
        
        if key_part:
            parts.append(key_part)
        else:
            # Если не удалось определить клавишу - игнорируем
            return
        
        # Сформировать строку горячей клавиши
        hotkey = '+'.join(parts)
        
        # Установить текст
        self.setText(hotkey)
        
        # Отправить сигнал
        self.hotkey_changed.emit(hotkey)
        
        # ВАЖНО: Убрать фокус с поля после выбора клавиши
        # Это предотвращает перезапись при следующем нажатии
        self.clearFocus()
        
        # Предотвратить стандартную обработку
        event.accept()
    
    def focusInEvent(self, event) -> None:
        """
        Обрабатывает получение фокуса.
        
        Очищает поле при получении фокуса, чтобы пользователь
        мог ввести новую горячую клавишу.
        
        Args:
            event: Событие получения фокуса
        """
        # Выделить весь текст для замены
        self.selectAll()
        super().focusInEvent(event)
    
    def mousePressEvent(self, event) -> None:
        """
        Обрабатывает клик мыши.
        
        Выделяет весь текст при клике.
        
        Args:
            event: Событие клика мыши
        """
        self.setFocus()
        self.selectAll()
        super().mousePressEvent(event)
