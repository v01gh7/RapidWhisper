"""
Unit-тесты для модуля форматирования горячих клавиш.

Тестирует форматирование специальных клавиш, модификаторов,
функциональных клавиш и обработку невалидного ввода.
"""

import pytest
from utils.hotkey_formatter import HotkeyFormatter


class TestSpecialKeys:
    """Тесты форматирования специальных клавиш."""
    
    def test_format_space(self):
        """Тест форматирования клавиши space."""
        result = HotkeyFormatter.format_hotkey("space")
        assert result == "⎵Space"
    
    def test_format_enter(self):
        """Тест форматирования клавиши enter."""
        result = HotkeyFormatter.format_hotkey("enter")
        assert result == "↵Enter"
    
    def test_format_esc(self):
        """Тест форматирования клавиши esc."""
        result = HotkeyFormatter.format_hotkey("esc")
        assert result == "Esc"
    
    def test_format_escape(self):
        """Тест форматирования клавиши escape (альтернативное название)."""
        result = HotkeyFormatter.format_hotkey("escape")
        assert result == "Esc"
    
    def test_format_tab(self):
        """Тест форматирования клавиши tab."""
        result = HotkeyFormatter.format_hotkey("tab")
        assert result == "⇥Tab"
    
    def test_format_backspace(self):
        """Тест форматирования клавиши backspace."""
        result = HotkeyFormatter.format_hotkey("backspace")
        assert result == "⌫Backspace"
    
    def test_format_delete(self):
        """Тест форматирования клавиши delete."""
        result = HotkeyFormatter.format_hotkey("delete")
        assert result == "⌦Delete"
    
    def test_format_arrow_keys(self):
        """Тест форматирования клавиш-стрелок."""
        assert HotkeyFormatter.format_hotkey("up") == "↑"
        assert HotkeyFormatter.format_hotkey("down") == "↓"
        assert HotkeyFormatter.format_hotkey("left") == "←"
        assert HotkeyFormatter.format_hotkey("right") == "→"


class TestModifiers:
    """Тесты форматирования модификаторов."""
    
    def test_format_ctrl_modifier(self):
        """Тест форматирования модификатора ctrl."""
        result = HotkeyFormatter.format_hotkey("ctrl+a")
        assert result == "Ctrl+A"
    
    def test_format_control_modifier(self):
        """Тест форматирования модификатора control (альтернативное название)."""
        result = HotkeyFormatter.format_hotkey("control+a")
        assert result == "Ctrl+A"
    
    def test_format_alt_modifier(self):
        """Тест форматирования модификатора alt."""
        result = HotkeyFormatter.format_hotkey("alt+f1")
        assert result == "Alt+F1"
    
    def test_format_shift_modifier(self):
        """Тест форматирования модификатора shift."""
        result = HotkeyFormatter.format_hotkey("shift+space")
        assert result == "Shift+⎵Space"
    
    def test_format_cmd_modifier(self):
        """Тест форматирования модификатора cmd."""
        result = HotkeyFormatter.format_hotkey("cmd+c")
        assert result == "Cmd+C"
    
    def test_format_command_modifier(self):
        """Тест форматирования модификатора command (альтернативное название)."""
        result = HotkeyFormatter.format_hotkey("command+v")
        assert result == "Cmd+V"
    
    def test_format_win_modifier(self):
        """Тест форматирования модификатора win."""
        result = HotkeyFormatter.format_hotkey("win+d")
        assert result == "Win+D"
    
    def test_format_windows_modifier(self):
        """Тест форматирования модификатора windows (альтернативное название)."""
        result = HotkeyFormatter.format_hotkey("windows+e")
        assert result == "Win+E"
    
    def test_format_multiple_modifiers(self):
        """Тест форматирования нескольких модификаторов."""
        result = HotkeyFormatter.format_hotkey("ctrl+shift+a")
        assert result == "Ctrl+Shift+A"
    
    def test_format_three_modifiers(self):
        """Тест форматирования трех модификаторов."""
        result = HotkeyFormatter.format_hotkey("ctrl+alt+shift+delete")
        assert result == "Ctrl+Alt+Shift+⌦Delete"


class TestFunctionKeys:
    """Тесты форматирования функциональных клавиш."""
    
    def test_format_f1(self):
        """Тест форматирования клавиши F1."""
        result = HotkeyFormatter.format_hotkey("f1")
        assert result == "F1"
    
    def test_format_f5(self):
        """Тест форматирования клавиши F5."""
        result = HotkeyFormatter.format_hotkey("f5")
        assert result == "F5"
    
    def test_format_f12(self):
        """Тест форматирования клавиши F12."""
        result = HotkeyFormatter.format_hotkey("f12")
        assert result == "F12"
    
    def test_format_all_function_keys(self):
        """Тест форматирования всех функциональных клавиш F1-F12."""
        for i in range(1, 13):
            result = HotkeyFormatter.format_hotkey(f"f{i}")
            assert result == f"F{i}"
    
    def test_format_function_key_with_modifier(self):
        """Тест форматирования функциональной клавиши с модификатором."""
        result = HotkeyFormatter.format_hotkey("ctrl+f5")
        assert result == "Ctrl+F5"
    
    def test_format_invalid_function_key_number(self):
        """Тест форматирования невалидного номера функциональной клавиши."""
        # F13 и выше должны форматироваться в верхний регистр как обычные клавиши
        result = HotkeyFormatter.format_hotkey("f13")
        assert result == "F13"
    
    def test_format_f0(self):
        """Тест форматирования F0 (невалидная функциональная клавиша)."""
        result = HotkeyFormatter.format_hotkey("f0")
        assert result == "F0"


class TestRegularKeys:
    """Тесты форматирования обычных букв."""
    
    def test_format_single_letter_lowercase(self):
        """Тест форматирования одной буквы в нижнем регистре."""
        result = HotkeyFormatter.format_hotkey("a")
        assert result == "A"
    
    def test_format_single_letter_uppercase(self):
        """Тест форматирования одной буквы в верхнем регистре."""
        result = HotkeyFormatter.format_hotkey("A")
        assert result == "A"
    
    def test_format_multiple_letters(self):
        """Тест форматирования нескольких букв."""
        assert HotkeyFormatter.format_hotkey("a") == "A"
        assert HotkeyFormatter.format_hotkey("b") == "B"
        assert HotkeyFormatter.format_hotkey("z") == "Z"
    
    def test_format_number_key(self):
        """Тест форматирования цифровой клавиши."""
        result = HotkeyFormatter.format_hotkey("1")
        assert result == "1"
    
    def test_format_letter_with_modifier(self):
        """Тест форматирования буквы с модификатором."""
        result = HotkeyFormatter.format_hotkey("ctrl+c")
        assert result == "Ctrl+C"


class TestEdgeCases:
    """Тесты граничных случаев и невалидного ввода."""
    
    def test_format_empty_string(self):
        """Тест форматирования пустой строки."""
        result = HotkeyFormatter.format_hotkey("")
        assert result == ""
    
    def test_format_whitespace_only(self):
        """Тест форматирования строки только с пробелами."""
        result = HotkeyFormatter.format_hotkey("   ")
        # Пробелы будут обрезаны при split, останется пустая строка
        assert result == ""
    
    def test_format_with_extra_spaces(self):
        """Тест форматирования с лишними пробелами."""
        result = HotkeyFormatter.format_hotkey("ctrl + a")
        assert result == "Ctrl+A"
    
    def test_format_mixed_case(self):
        """Тест форматирования со смешанным регистром."""
        result = HotkeyFormatter.format_hotkey("CtRl+SpAcE")
        assert result == "Ctrl+⎵Space"
    
    def test_format_unknown_key(self):
        """Тест форматирования неизвестной клавиши."""
        result = HotkeyFormatter.format_hotkey("unknown")
        assert result == "UNKNOWN"
    
    def test_format_special_characters(self):
        """Тест форматирования специальных символов."""
        # Специальные символы должны форматироваться в верхний регистр
        result = HotkeyFormatter.format_hotkey("@")
        assert result == "@"
    
    def test_format_single_plus(self):
        """Тест форматирования одного символа плюс."""
        result = HotkeyFormatter.format_hotkey("+")
        # После split('+') получим пустые строки, которые после strip и upper дадут пустые строки
        # Но join их соединит с '+', поэтому результат будет '+'
        assert result == "+"
    
    def test_format_trailing_plus(self):
        """Тест форматирования с завершающим плюсом."""
        result = HotkeyFormatter.format_hotkey("ctrl+")
        # После split получим ['ctrl', ''], пустая строка даст пустой результат
        assert result == "Ctrl+"
    
    def test_format_leading_plus(self):
        """Тест форматирования с начальным плюсом."""
        result = HotkeyFormatter.format_hotkey("+a")
        # После split получим ['', 'a']
        assert result == "+A"
    
    def test_format_invalid_function_key_format(self):
        """Тест форматирования невалидного формата функциональной клавиши."""
        result = HotkeyFormatter.format_hotkey("fx")
        assert result == "FX"


class TestComplexCombinations:
    """Тесты сложных комбинаций клавиш."""
    
    def test_format_ctrl_alt_delete(self):
        """Тест форматирования классической комбинации Ctrl+Alt+Delete."""
        result = HotkeyFormatter.format_hotkey("ctrl+alt+delete")
        assert result == "Ctrl+Alt+⌦Delete"
    
    def test_format_shift_f10(self):
        """Тест форматирования Shift+F10."""
        result = HotkeyFormatter.format_hotkey("shift+f10")
        assert result == "Shift+F10"
    
    def test_format_ctrl_shift_esc(self):
        """Тест форматирования Ctrl+Shift+Esc."""
        result = HotkeyFormatter.format_hotkey("ctrl+shift+esc")
        assert result == "Ctrl+Shift+Esc"
    
    def test_format_alt_tab(self):
        """Тест форматирования Alt+Tab."""
        result = HotkeyFormatter.format_hotkey("alt+tab")
        assert result == "Alt+⇥Tab"
    
    def test_format_win_arrow(self):
        """Тест форматирования Win+Arrow."""
        result = HotkeyFormatter.format_hotkey("win+left")
        assert result == "Win+←"
    
    def test_format_ctrl_enter(self):
        """Тест форматирования Ctrl+Enter."""
        result = HotkeyFormatter.format_hotkey("ctrl+enter")
        assert result == "Ctrl+↵Enter"


class TestRequirementsValidation:
    """Тесты валидации требований."""
    
    def test_requirement_4_1_ctrl_modifier(self):
        """
        Requirement 4.1: WHEN горячая клавиша содержит модификатор "ctrl", 
        THEN Hotkey_Display SHALL отображать "Ctrl+"
        """
        result = HotkeyFormatter.format_hotkey("ctrl+a")
        assert result.startswith("Ctrl+")
        assert "Ctrl" in result
    
    def test_requirement_4_2_alt_modifier(self):
        """
        Requirement 4.2: WHEN горячая клавиша содержит модификатор "alt", 
        THEN Hotkey_Display SHALL отображать "Alt+"
        """
        result = HotkeyFormatter.format_hotkey("alt+f1")
        assert result.startswith("Alt+")
        assert "Alt" in result
    
    def test_requirement_4_3_shift_modifier(self):
        """
        Requirement 4.3: WHEN горячая клавиша содержит модификатор "shift", 
        THEN Hotkey_Display SHALL отображать "Shift+"
        """
        result = HotkeyFormatter.format_hotkey("shift+space")
        assert result.startswith("Shift+")
        assert "Shift" in result
    
    def test_requirement_4_4_space_key(self):
        """
        Requirement 4.4: WHEN горячая клавиша является "space", 
        THEN Hotkey_Display SHALL отображать "⎵Space"
        """
        result = HotkeyFormatter.format_hotkey("space")
        assert result == "⎵Space"
    
    def test_requirement_4_5_function_keys(self):
        """
        Requirement 4.5: WHEN горячая клавиша является функциональной клавишей (f1-f12), 
        THEN Hotkey_Display SHALL отображать её в верхнем регистре (F1-F12)
        """
        for i in range(1, 13):
            result = HotkeyFormatter.format_hotkey(f"f{i}")
            assert result == f"F{i}"
            assert result[0] == "F"
            assert result[0].isupper()
    
    def test_requirement_4_6_letter_uppercase(self):
        """
        Requirement 4.6: WHEN горячая клавиша является буквой, 
        THEN Hotkey_Display SHALL отображать её в верхнем регистре
        """
        for letter in "abcdefghijklmnopqrstuvwxyz":
            result = HotkeyFormatter.format_hotkey(letter)
            assert result == letter.upper()
            assert result.isupper()
