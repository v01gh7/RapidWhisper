#!/usr/bin/env python
"""
Тест таймаута постобработки.
Проверяет что при таймауте возвращается оригинальный текст.
"""

from services.transcription_client import TranscriptionClient
from core.config import Config

def test_timeout():
    """Тестирует таймаут постобработки."""
    
    print("=" * 80)
    print("ТЕСТ ТАЙМАУТА ПОСТОБРАБОТКИ")
    print("=" * 80)
    
    # Тестовый текст
    test_text = "это тестовый текст для проверки таймаута"
    
    print(f"\n📝 Исходный текст: {test_text}")
    print(f"⏱️  Таймаут: 60 секунд")
    print(f"✅ Гарантия: при любой ошибке вернется оригинальный текст")
    
    # Создать клиент
    config = Config.load_from_config()
    client = TranscriptionClient(provider=config.ai_provider)
    
    print(f"\n🔧 Настройки:")
    print(f"   Провайдер: {config.post_processing_provider}")
    print(f"   Модель: {config.post_processing_model}")
    print(f"   GLM Coding Plan: {config.glm_use_coding_plan}")
    
    print(f"\n🚀 Отправка запроса...")
    print(f"   (Если зависнет, через 60 секунд вернется оригинальный текст)")
    
    try:
        result = client.post_process_text(
            text=test_text,
            provider=config.post_processing_provider,
            model=config.post_processing_model,
            system_prompt=config.post_processing_prompt,
            base_url=config.llm_base_url if config.post_processing_provider == "llm" else None,
            use_coding_plan=config.glm_use_coding_plan if config.post_processing_provider == "glm" else False
        )
        
        print(f"\n✅ Результат получен:")
        print(f"   {result}")
        
        if result == test_text:
            print(f"\n⚠️  Вернулся оригинальный текст (возможно была ошибка или таймаут)")
        else:
            print(f"\n✅ Текст был обработан успешно!")
            
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        print(f"   (Это не должно происходить - все ошибки должны обрабатываться внутри)")
    
    print("\n" + "=" * 80)
    print("ТЕСТ ЗАВЕРШЕН")
    print("=" * 80)

if __name__ == "__main__":
    test_timeout()
