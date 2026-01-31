"""
Тест для проверки что кастомная модель правильно используется в TranscriptionClient.
"""

from services.transcription_client import TranscriptionClient
from core.config import Config


def test_custom_model_usage():
    """Проверяет что кастомная модель правильно передается в TranscriptionClient."""
    print("=" * 80)
    print("ТЕСТ: Использование кастомной модели в TranscriptionClient")
    print("=" * 80)
    
    # Загрузить конфигурацию из config.jsonc
    config = Config.load_from_config()
    
    test_cases = [
        # (provider, custom_model, expected_model)
        ("groq", None, "whisper-large-v3"),  # Дефолтная модель
        ("groq", "whisper-large-v3-turbo", "whisper-large-v3-turbo"),  # Кастомная модель
        ("openai", None, "whisper-1"),  # Дефолтная модель
        ("openai", "whisper-1-custom", "whisper-1-custom"),  # Кастомная модель
        ("glm", None, "glm-4-voice"),  # Дефолтная модель
        ("glm", "glm-4-voice-custom", "glm-4-voice-custom"),  # Кастомная модель
    ]
    
    print("\n📋 Проверка создания TranscriptionClient с разными моделями:\n")
    
    all_passed = True
    
    for provider, custom_model, expected_model in test_cases:
        try:
            # Создать клиент с кастомной моделью
            client = TranscriptionClient(
                provider=provider,
                model=custom_model
            )
            
            # Проверить что модель установлена правильно
            if client.model == expected_model:
                print(f"✅ {provider:10} | Custom: {str(custom_model):25} | Expected: {expected_model:25} | Got: {client.model}")
            else:
                print(f"❌ {provider:10} | Custom: {str(custom_model):25} | Expected: {expected_model:25} | Got: {client.model}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {provider:10} | Custom: {str(custom_model):25} | Error: {e}")
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
    print("=" * 80)
    
    return all_passed


if __name__ == "__main__":
    import sys
    success = test_custom_model_usage()
    sys.exit(0 if success else 1)
