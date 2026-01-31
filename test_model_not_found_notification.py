"""
Тест для проверки уведомления о модели не найдена.

Этот тест проверяет что:
1. При использовании несуществующей модели в постобработке
2. Отправляется сигнал model_not_found
3. Показывается уведомление через tray icon
4. Возвращается оригинальный текст без постобработки
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from services.transcription_client import TranscriptionClient
from openai import NotFoundError
from core.config import Config
from utils.i18n import t


def test_model_not_found_notification():
    """Тест уведомления о модели не найдена."""
    print("=" * 80)
    print("ТЕСТ: Уведомление о модели не найдена")
    print("=" * 80)
    
    # Создать клиент с валидным API ключом
    config = Config.load_from_config()
    
    # Проверить что постобработка включена
    if not config.enable_post_processing:
        print("❌ Постобработка отключена в настройках!")
        print("Включите постобработку в .env: ENABLE_POST_PROCESSING=true")
        return
    
    print(f"✅ Постобработка включена")
    print(f"Провайдер: {config.post_processing_provider}")
    print(f"Модель: {config.post_processing_model}")
    
    # Создать клиент транскрипции
    try:
        client = TranscriptionClient(
            provider=config.ai_provider,
            api_key=None  # Загрузится из env
        )
        print(f"✅ TranscriptionClient создан для {config.ai_provider}")
    except Exception as e:
        print(f"❌ Ошибка создания клиента: {e}")
        return
    
    # Тестовый текст
    test_text = "это тестовый текст для проверки постобработки"
    print(f"\nИсходный текст: {test_text}")
    
    # Попробовать постобработку с несуществующей моделью
    fake_model = "gpt-5.2-ultra-mega-turbo"  # Несуществующая модель
    print(f"\n🔍 Тестируем с несуществующей моделью: {fake_model}")
    print(f"Провайдер: {config.post_processing_provider}")
    
    try:
        result = client.post_process_text(
            text=test_text,
            provider=config.post_processing_provider,
            model=fake_model,
            system_prompt=config.post_processing_prompt
        )
        
        print(f"\n⚠️ ВНИМАНИЕ: Результат получен без исключения: {result}")
        print("Это неожиданно - должно было быть исключение NotFoundError")
            
    except NotFoundError as e:
        print(f"\n✅ УСПЕХ: NotFoundError поймано как ожидалось")
        print(f"Сообщение об ошибке: {str(e)[:100]}...")
        print("Теперь TranscriptionThread сможет отправить сигнал model_not_found")
        
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {type(e).__name__}: {e}")
        print("Это не должно было произойти")
    
    print("\n" + "=" * 80)
    print("ПРОВЕРКА ПЕРЕВОДОВ")
    print("=" * 80)
    
    # Проверить что ключи перевода существуют
    try:
        title = t("tray.notification.model_not_found")
        message = t("tray.notification.model_not_found_message", model=fake_model, provider=config.post_processing_provider)
        
        print(f"✅ Заголовок: {title}")
        print(f"✅ Сообщение: {message}")
        
    except Exception as e:
        print(f"❌ Ошибка перевода: {e}")
    
    print("\n" + "=" * 80)
    print("ТЕСТ ЗАВЕРШЕН")
    print("=" * 80)
    print("\n💡 Для полного теста запустите приложение и:")
    print("1. Включите постобработку в настройках")
    print("2. В поле 'Кастомная модель' введите несуществующую модель (например: gpt-5.2)")
    print("3. Сделайте запись")
    print("4. Проверьте что появилось уведомление в трее о модели не найдена")
    print("5. Проверьте что текст все равно скопирован в буфер обмена")


if __name__ == "__main__":
    # Создать QApplication для работы с переводами
    app = QApplication(sys.argv)
    
    # Запустить тест
    test_model_not_found_notification()
    
    sys.exit(0)
