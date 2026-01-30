#!/usr/bin/env python
"""
Тест GLM Coding Plan endpoint.
Проверяет доступность и работоспособность.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def test_glm_coding_plan():
    """Тестирует GLM Coding Plan endpoint."""
    
    api_key = os.getenv("GLM_API_KEY")
    
    if not api_key:
        print("❌ GLM_API_KEY не найден в .env файле")
        return
    
    print("=" * 80)
    print("ТЕСТ GLM CODING PLAN ENDPOINT")
    print("=" * 80)
    
    # Тест 1: Обычный endpoint
    print("\n1. Тестирование обычного GLM endpoint...")
    print(f"   Endpoint: https://open.bigmodel.cn/api/paas/v4/")
    print(f"   Модель: glm-4-flash")
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://open.bigmodel.cn/api/paas/v4/",
            timeout=30
        )
        
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "user", "content": "Привет! Ответь одним словом: работает?"}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"   ✅ Ответ получен: {result}")
        print(f"   ✅ Обычный endpoint работает!")
        
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        print(f"   ❌ Обычный endpoint не работает")
    
    # Тест 2: Coding Plan endpoint
    print("\n2. Тестирование GLM Coding Plan endpoint...")
    print(f"   Endpoint: https://api.z.ai/api/coding/paas/v4/")
    print(f"   Модель: glm-4.7")
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.z.ai/api/coding/paas/v4/",
            timeout=30
        )
        
        print("   Отправка запроса...")
        
        response = client.chat.completions.create(
            model="glm-4.7",
            messages=[
                {"role": "user", "content": "Привет! Ответь одним словом: работает?"}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"   ✅ Ответ получен: {result}")
        print(f"   ✅ Coding Plan endpoint работает!")
        
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        print(f"   ❌ Coding Plan endpoint не работает")
        print(f"\n   💡 Возможные причины:")
        print(f"      1. У вас нет подписки Coding Plan")
        print(f"      2. API ключ не привязан к Coding Plan")
        print(f"      3. Модель glm-4.7 недоступна")
        print(f"      4. Endpoint изменился")
    
    print("\n" + "=" * 80)
    print("РЕКОМЕНДАЦИИ")
    print("=" * 80)
    print("\n💡 Если Coding Plan endpoint не работает:")
    print("   1. Используйте обычный GLM endpoint (отключите чекбокс)")
    print("   2. Или используйте Groq (бесплатный и быстрый)")
    print("\n✅ Если Coding Plan endpoint работает:")
    print("   1. Включите чекбокс 'Использовать Coding Plan' в настройках")
    print("   2. Выберите модель glm-4.7, glm-4.6, glm-4.5 или glm-4.5-air")

if __name__ == "__main__":
    test_glm_coding_plan()
