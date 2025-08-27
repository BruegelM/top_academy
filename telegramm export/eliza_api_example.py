import os
import asyncio
import aiohttp
from config import (
    ELIZA_API_TOKEN,
    ELIZA_BASE_URL,
    ELIZA_CHAT_URL,
    ELIZA_DEFAULT_MODEL,
    ELIZA_DEFAULT_TEMPERATURE,
    ELIZA_DEFAULT_MAX_TOKENS,
    ELIZA_DEFAULT_TOP_P,
    ELIZA_DEFAULT_N
)

async def call_eliza_api():
    """Пример использования Eliza API для генерации текста"""
    headers = {
        "Authorization": f"OAuth {ELIZA_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": ELIZA_DEFAULT_MODEL,
        "messages": [
            {
                "role": "user",
                "content": "Привет! Расскажи о последних новостях в туризме"
            }
        ],
        "temperature": ELIZA_DEFAULT_TEMPERATURE,
        "max_tokens": ELIZA_DEFAULT_MAX_TOKENS,
        "top_p": ELIZA_DEFAULT_TOP_P,
        "n": ELIZA_DEFAULT_N
    }

    try:
        async with aiohttp.ClientSession() as session:
            print(f"📡 Отправка запроса к {ELIZA_CHAT_URL}")
            async with session.post(ELIZA_CHAT_URL, headers=headers, json=payload) as response:
                print(f"📊 Статус ответа: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ Успешный ответ:")
                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0].get('message', {}).get('content', '')
                        print(f"Ответ модели:\n{content}")
                    else:
                        print(f"Полный ответ:\n{result}")
                else:
                    error_text = await response.text()
                    print(f"❌ Ошибка: {response.status}")
                    print(f"Сообщение: {error_text}")
                    
    except Exception as e:
        print(f"❌ Исключение при запросе: {e}")

async def check_eliza_models():
    """Пример проверки доступных моделей Eliza API"""
    headers = {
        "Authorization": f"OAuth {ELIZA_API_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        async with aiohttp.ClientSession() as session:
            url = f"{ELIZA_BASE_URL}/models"
            print(f"📡 Запрос доступных моделей: {url}")
            async with session.get(url, headers=headers) as response:
                print(f"📊 Статус ответа: {response.status}")
                
                if response.status == 200:
                    models = await response.json()
                    print("✅ Доступные модели:")
                    print(models)
                else:
                    error_text = await response.text()
                    print(f"❌ Ошибка: {response.status}")
                    print(f"Сообщение: {error_text}")
                    
    except Exception as e:
        print(f"❌ Исключение при запросе: {e}")

if __name__ == "__main__":
    print("🔍 Тестирование Eliza API")
    asyncio.run(call_eliza_api())
    print("\n🔍 Проверка доступных моделей")
    asyncio.run(check_eliza_models())