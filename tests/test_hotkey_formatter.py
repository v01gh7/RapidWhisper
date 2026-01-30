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


# Property-Based Tests
# Feature: active-app-display, Property 5: Форматирование модификаторов

from hypothesis import given, strategies as st


class TestPropertyModifierFormatting:
    """Property-based тесты для форматирования модификаторов."""
    
    # Стратегии для генерации тестовых данных
    modifiers = st.sampled_from(['ctrl', 'control', 'alt', 'shift', 'cmd', 'command', 'win', 'windows'])
    keys = st.sampled_from([
        'a', 'b', 'c', 'z', 
        'space', 'enter', 'esc', 'tab',
        'f1', 'f5', 'f12',
        '1', '2', '9'
    ])
    
    @given(modifier=modifiers, key=keys)
    def test_property_single_modifier_formatting(self, modifier, key):
        """
        **Validates: Requirements 4.1, 4.2, 4.3**
        
        Property 5: Форматирование модификаторов
        
        For any hotkey containing a single modifier (ctrl, alt, shift, etc.),
        HotkeyFormatter должен отображать модификатор с заглавной буквы и знаком "+".
        """
        hotkey = f"{modifier}+{key}"
        result = HotkeyFormatter.format_hotkey(hotkey)
        
        # Определить ожидаемый формат модификатора
        expected_modifier_map = {
            'ctrl': 'Ctrl',
            'control': 'Ctrl',
            'alt': 'Alt',
            'shift': 'Shift',
            'cmd': 'Cmd',
            'command': 'Cmd',
            'win': 'Win',
            'windows': 'Win'
        }
        
        expected_modifier = expected_modifier_map[modifier]
        
        # Проверить, что результат содержит правильно отформатированный модификатор
        assert expected_modifier in result, \
            f"Expected '{expected_modifier}' in result '{result}' for hotkey '{hotkey}'"
        
        # Проверить, что модификатор идет первым и за ним следует "+"
        assert result.startswith(expected_modifier + "+"), \
            f"Expected result to start with '{expected_modifier}+' but got '{result}' for hotkey '{hotkey}'"
        
        # Проверить, что в результате есть знак "+"
        assert "+" in result, \
            f"Expected '+' separator in result '{result}' for hotkey '{hotkey}'"
    
    @given(
        modifier1=modifiers,
        modifier2=modifiers,
        key=keys
    )
    def test_property_multiple_modifiers_formatting(self, modifier1, modifier2, key):
        """
        **Validates: Requirements 4.1, 4.2, 4.3**
        
        Property 5: Форматирование модификаторов (множественные модификаторы)
        
        For any hotkey containing multiple modifiers,
        HotkeyFormatter должен отображать каждый модификатор с заглавной буквы и знаком "+".
        """
        # Пропустить случаи, когда модификаторы одинаковые или являются синонимами
        if modifier1 == modifier2:
            return
        if (modifier1 in ['ctrl', 'control'] and modifier2 in ['ctrl', 'control']):
            return
        if (modifier1 in ['cmd', 'command'] and modifier2 in ['cmd', 'command']):
            return
        if (modifier1 in ['win', 'windows'] and modifier2 in ['win', 'windows']):
            return
        
        hotkey = f"{modifier1}+{modifier2}+{key}"
        result = HotkeyFormatter.format_hotkey(hotkey)
        
        # Определить ожидаемые форматы модификаторов
        expected_modifier_map = {
            'ctrl': 'Ctrl',
            'control': 'Ctrl',
            'alt': 'Alt',
            'shift': 'Shift',
            'cmd': 'Cmd',
            'command': 'Cmd',
            'win': 'Win',
            'windows': 'Win'
        }
        
        expected_modifier1 = expected_modifier_map[modifier1]
        expected_modifier2 = expected_modifier_map[modifier2]
        
        # Проверить, что оба модификатора присутствуют в результате
        assert expected_modifier1 in result, \
            f"Expected '{expected_modifier1}' in result '{result}' for hotkey '{hotkey}'"
        assert expected_modifier2 in result, \
            f"Expected '{expected_modifier2}' in result '{result}' for hotkey '{hotkey}'"
        
        # Проверить, что результат содержит знаки "+"
        assert result.count("+") >= 2, \
            f"Expected at least 2 '+' separators in result '{result}' for hotkey '{hotkey}'"
        
        # Проверить, что модификаторы разделены знаком "+"
        parts = result.split("+")
        assert len(parts) >= 3, \
            f"Expected at least 3 parts in result '{result}' for hotkey '{hotkey}'"
    
    @given(
        modifier=modifiers,
        case_variant=st.sampled_from(['lower', 'upper', 'mixed'])
    )
    def test_property_modifier_case_insensitive(self, modifier, case_variant):
        """
        **Validates: Requirements 4.1, 4.2, 4.3**
        
        Property 5: Форматирование модификаторов (независимость от регистра)
        
        For any hotkey containing a modifier in any case (lower, upper, mixed),
        HotkeyFormatter должен отображать модификатор в правильном формате с заглавной буквы.
        """
        # Применить вариант регистра
        if case_variant == 'lower':
            test_modifier = modifier.lower()
        elif case_variant == 'upper':
            test_modifier = modifier.upper()
        else:  # mixed
            test_modifier = ''.join(
                c.upper() if i % 2 == 0 else c.lower() 
                for i, c in enumerate(modifier)
            )
        
        hotkey = f"{test_modifier}+a"
        result = HotkeyFormatter.format_hotkey(hotkey)
        
        # Определить ожидаемый формат модификатора
        expected_modifier_map = {
            'ctrl': 'Ctrl',
            'control': 'Ctrl',
            'alt': 'Alt',
            'shift': 'Shift',
            'cmd': 'Cmd',
            'command': 'Cmd',
            'win': 'Win',
            'windows': 'Win'
        }
        
        expected_modifier = expected_modifier_map[modifier.lower()]
        
        # Проверить, что результат содержит правильно отформатированный модификатор
        # независимо от исходного регистра
        assert expected_modifier in result, \
            f"Expected '{expected_modifier}' in result '{result}' for hotkey '{hotkey}' (case: {case_variant})"
        
        # Проверить, что модификатор идет первым и за ним следует "+"
        assert result.startswith(expected_modifier + "+"), \
            f"Expected result to start with '{expected_modifier}+' but got '{result}' for hotkey '{hotkey}' (case: {case_variant})"


# Feature: active-app-display, Property 6: Форматирование клавиш в верхний регистр


class TestPropertyKeyUppercaseFormatting:
    """Property-based тесты для форматирования клавиш в верхний регистр."""
    
    # Стратегии для генерации тестовых данных
    function_keys = st.sampled_from([f'f{i}' for i in range(1, 13)])
    letters = st.sampled_from(list('abcdefghijklmnopqrstuvwxyz'))
    case_variants = st.sampled_from(['lower', 'upper', 'mixed'])
    
    @given(function_key=function_keys)
    def test_property_function_key_uppercase(self, function_key):
        """
        **Validates: Requirements 4.5**
        
        Property 6: Форматирование клавиш в верхний регистр (функциональные клавиши)
        
        For any hotkey that is a function key (f1-f12),
        HotkeyFormatter должен отображать её в верхнем регистре (F1-F12).
        """
        result = HotkeyFormatter.format_hotkey(function_key)
        
        # Извлечь номер функциональной клавиши
        key_number = function_key[1:]
        expected = f'F{key_number}'
        
        # Проверить, что результат соответствует ожидаемому формату
        assert result == expected, \
            f"Expected '{expected}' but got '{result}' for function key '{function_key}'"
        
        # Проверить, что первая буква в верхнем регистре
        assert result[0] == 'F', \
            f"Expected first character to be 'F' but got '{result[0]}' for function key '{function_key}'"
        
        # Проверить, что первая буква действительно в верхнем регистре
        assert result[0].isupper(), \
            f"Expected first character to be uppercase but got '{result[0]}' for function key '{function_key}'"
    
    @given(letter=letters)
    def test_property_letter_uppercase(self, letter):
        """
        **Validates: Requirements 4.6**
        
        Property 6: Форматирование клавиш в верхний регистр (буквы)
        
        For any hotkey that is a letter,
        HotkeyFormatter должен отображать её в верхнем регистре.
        """
        result = HotkeyFormatter.format_hotkey(letter)
        
        # Проверить, что результат - это буква в верхнем регистре
        assert result == letter.upper(), \
            f"Expected '{letter.upper()}' but got '{result}' for letter '{letter}'"
        
        # Проверить, что результат действительно в верхнем регистре
        assert result.isupper(), \
            f"Expected uppercase letter but got '{result}' for letter '{letter}'"
        
        # Проверить, что результат - это одна буква
        assert len(result) == 1, \
            f"Expected single character but got '{result}' for letter '{letter}'"
    
    @given(
        function_key=function_keys,
        case_variant=case_variants
    )
    def test_property_function_key_case_insensitive(self, function_key, case_variant):
        """
        **Validates: Requirements 4.5**
        
        Property 6: Форматирование клавиш в верхний регистр (независимость от регистра)
        
        For any function key in any case (lower, upper, mixed),
        HotkeyFormatter должен отображать её в верхнем регистре.
        """
        # Применить вариант регистра
        if case_variant == 'lower':
            test_key = function_key.lower()
        elif case_variant == 'upper':
            test_key = function_key.upper()
        else:  # mixed
            test_key = ''.join(
                c.upper() if i % 2 == 0 else c.lower() 
                for i, c in enumerate(function_key)
            )
        
        result = HotkeyFormatter.format_hotkey(test_key)
        
        # Извлечь номер функциональной клавиши
        key_number = function_key[1:]
        expected = f'F{key_number}'
        
        # Проверить, что результат соответствует ожидаемому формату
        # независимо от исходного регистра
        assert result == expected, \
            f"Expected '{expected}' but got '{result}' for function key '{test_key}' (case: {case_variant})"
        
        # Проверить, что первая буква в верхнем регистре
        assert result[0].isupper(), \
            f"Expected uppercase 'F' but got '{result[0]}' for function key '{test_key}' (case: {case_variant})"
    
    @given(
        letter=letters,
        case_variant=case_variants
    )
    def test_property_letter_case_insensitive(self, letter, case_variant):
        """
        **Validates: Requirements 4.6**
        
        Property 6: Форматирование клавиш в верхний регистр (независимость от регистра)
        
        For any letter in any case (lower, upper),
        HotkeyFormatter должен отображать её в верхнем регистре.
        """
        # Применить вариант регистра
        if case_variant == 'lower':
            test_letter = letter.lower()
        elif case_variant == 'upper':
            test_letter = letter.upper()
        else:  # mixed - для одной буквы mixed = upper
            test_letter = letter.upper()
        
        result = HotkeyFormatter.format_hotkey(test_letter)
        
        # Проверить, что результат - это буква в верхнем регистре
        # независимо от исходного регистра
        assert result == letter.upper(), \
            f"Expected '{letter.upper()}' but got '{result}' for letter '{test_letter}' (case: {case_variant})"
        
        # Проверить, что результат действительно в верхнем регистре
        assert result.isupper(), \
            f"Expected uppercase letter but got '{result}' for letter '{test_letter}' (case: {case_variant})"
    
    @given(
        modifier=st.sampled_from(['ctrl', 'alt', 'shift']),
        function_key=function_keys
    )
    def test_property_function_key_with_modifier_uppercase(self, modifier, function_key):
        """
        **Validates: Requirements 4.5**
        
        Property 6: Форматирование клавиш в верхний регистр (функциональные клавиши с модификаторами)
        
        For any hotkey that is a function key with a modifier,
        HotkeyFormatter должен отображать функциональную клавишу в верхнем регистре.
        """
        hotkey = f"{modifier}+{function_key}"
        result = HotkeyFormatter.format_hotkey(hotkey)
        
        # Извлечь номер функциональной клавиши
        key_number = function_key[1:]
        expected_key = f'F{key_number}'
        
        # Проверить, что результат содержит функциональную клавишу в верхнем регистре
        assert expected_key in result, \
            f"Expected '{expected_key}' in result '{result}' for hotkey '{hotkey}'"
        
        # Проверить, что функциональная клавиша заканчивается на ожидаемый формат
        assert result.endswith(expected_key), \
            f"Expected result to end with '{expected_key}' but got '{result}' for hotkey '{hotkey}'"
        
        # Проверить, что 'F' в верхнем регистре
        key_part = result.split('+')[-1]
        assert key_part[0] == 'F', \
            f"Expected 'F' but got '{key_part[0]}' in result '{result}' for hotkey '{hotkey}'"
        assert key_part[0].isupper(), \
            f"Expected uppercase 'F' in result '{result}' for hotkey '{hotkey}'"
    
    @given(
        modifier=st.sampled_from(['ctrl', 'alt', 'shift']),
        letter=letters
    )
    def test_property_letter_with_modifier_uppercase(self, modifier, letter):
        """
        **Validates: Requirements 4.6**
        
        Property 6: Форматирование клавиш в верхний регистр (буквы с модификаторами)
        
        For any hotkey that is a letter with a modifier,
        HotkeyFormatter должен отображать букву в верхнем регистре.
        """
        hotkey = f"{modifier}+{letter}"
        result = HotkeyFormatter.format_hotkey(hotkey)
        
        expected_letter = letter.upper()
        
        # Проверить, что результат содержит букву в верхнем регистре
        assert expected_letter in result, \
            f"Expected '{expected_letter}' in result '{result}' for hotkey '{hotkey}'"
        
        # Проверить, что буква заканчивается на ожидаемый формат
        assert result.endswith(expected_letter), \
            f"Expected result to end with '{expected_letter}' but got '{result}' for hotkey '{hotkey}'"
        
        # Проверить, что буква в верхнем регистре
        key_part = result.split('+')[-1]
        assert key_part.isupper(), \
            f"Expected uppercase letter in result '{result}' for hotkey '{hotkey}'"
