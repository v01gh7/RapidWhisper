"""
Тест для проверки обработки ошибок при использовании несуществующей модели.
"""
import os
from dotenv import load_dotenv
from services.transcription_client import TranscriptionClient

# Загрузить .env
load_dotenv()

def test_invalid_model():
    """Тест проверяет что несуществующая модель обрабатывается корректно."""
    
    print("🧪 Тест: Несуществующая модель")
    print("=" * 80)
    
    # Создать клиент
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("❌ GROQ_API_KEY не найден в .env файле")
        return
    
    client = TranscriptionClient(provider="groq", api_key=groq_api_key)
    
    # Тестовый текст
    test_text = "это тестовый текст для проверки обработки ошибок"
    
    print(f"📝 Исходный текст: {test_text}")
    print(f"🤖 Провайдер: groq")
    print(f"🎯 Модель: gpt-5.2 (несуществующая)")
    print()
    
    # Попробовать обработать с несуществующей моделью
    try:
        result = client.post_process_text(
            text=test_text,
            provider="groq",
            model="gpt-5.2",  # Несуществующая модель
            system_prompt="Fix grammar and add punctuation.",
            api_key=groq_api_key
        )
        
        print("=" * 80)
        print("✅ РЕЗУЛЬТАТ:")
        print(f"   Возвращен текст: {result}")
        
        if result == test_text:
            print("   ✅ Корректно: вернулся оригинальный текст")
        else:
            print("   ⚠️ Внимание: текст был изменен")
        
    except Exception as e:
        print("=" * 80)
        print(f"❌ ИСКЛЮЧЕНИЕ: {e}")
        print(f"   Тип: {type(e).__name__}")
        import traceback
        print(traceback.format_exc())


if __name__ == "__main__":
    test_invalid_model()
