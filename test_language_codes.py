"""
Тест для проверки нормализации кодов языков.

Проверяет, что en-gb и en-us корректно обрабатываются.
"""

from utils.i18n import t, set_language, get_language

def test_language_normalization():
    """Тест нормализации кодов языков."""
    
    print("=== Тест нормализации кодов языков ===\n")
    
    # Тест 1: en-gb
    print("1. Установка языка en-gb")
    set_language("en-gb")
    current = get_language()
    print(f"   Текущий язык: {current}")
    print(f"   Перевод 'common.success': {t('common.success')}")
    assert current == "en-gb", f"Expected 'en-gb', got '{current}'"
    assert t('common.success') == "✅ Success", f"Translation failed for en-gb"
    print("   ✅ Passed\n")
    
    # Тест 2: en-us
    print("2. Установка языка en-us")
    set_language("en-us")
    current = get_language()
    print(f"   Текущий язык: {current}")
    print(f"   Перевод 'common.success': {t('common.success')}")
    assert current == "en-us", f"Expected 'en-us', got '{current}'"
    assert t('common.success') == "✅ Success", f"Translation failed for en-us"
    print("   ✅ Passed\n")
    
    # Тест 3: ru
    print("3. Установка языка ru")
    set_language("ru")
    current = get_language()
    print(f"   Текущий язык: {current}")
    print(f"   Перевод 'common.success': {t('common.success')}")
    assert current == "ru", f"Expected 'ru', got '{current}'"
    # Проверяем что перевод не на английском
    assert "Success" not in t('common.success'), f"Translation failed for ru - still in English"
    print("   ✅ Passed\n")
    
    # Тест 4: Переключение en-gb -> ru -> en-us
    print("4. Переключение языков")
    set_language("en-gb")
    print(f"   en-gb: {t('common.cancel')}")
    
    set_language("ru")
    print(f"   ru: {t('common.cancel')}")
    
    set_language("en-us")
    print(f"   en-us: {t('common.cancel')}")
    print("   ✅ Passed\n")
    
    print("=== Все тесты пройдены! ===")

if __name__ == "__main__":
    test_language_normalization()
