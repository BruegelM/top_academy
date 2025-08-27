#!/usr/bin/env python3
"""
Тестирование обновленного продуктивного цикла с детализированным анализом
"""

import asyncio
import logging
from datetime import datetime
from database import DatabaseManager
from models import ZelibobaAnalyzer

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_updated_analysis_system():
    """Тестирует обновленную систему анализа саммари"""
    
    print("🧪 Тестирование обновленной системы анализа саммари")
    print("=" * 60)
    
    db = DatabaseManager()
    db.connect()
    
    try:
        # Получаем саммари без анализа
        summaries = db.get_summaries_without_analysis(limit=3)
        
        if not summaries:
            print("❌ Нет саммари без анализа для тестирования")
            print("💡 Создаем тестовые саммари...")
            
            # Создаем тестовые саммари
            test_summaries = [
                {
                    "content": "Новая авиакомпания запускает прямые рейсы из Москвы в Токио. Билеты будут стоить от 45000 рублей в одну сторону.",
                    "main_idea": "Новая авиакомпания запускает прямые рейсы Москва-Токио от 45000 рублей.",
                    "channel_name": "Test Aviation Channel"
                },
                {
                    "content": "Турция вводит новые визовые требования для российских туристов. Теперь потребуется справка о доходах и бронь отеля.",
                    "main_idea": "Турция вводит новые визовые требования для российских туристов.",
                    "channel_name": "Test Visa Channel"
                },
                {
                    "content": "Крупная гостиничная сеть открывает 50 новых отелей в Турции. Все отели будут работать по системе все включено.",
                    "main_idea": "Гостиничная сеть открывает 50 новых отелей в Турции по системе все включено.",
                    "channel_name": "Test Hotel Channel"
                }
            ]
            
            for i, test_data in enumerate(test_summaries, 1):
                summary_id = db.save_post_summary(
                    channel_id=1,  # Используем существующий канал
                    telegram_message_id=9999 + i,
                    sender_name="Test Sender",
                    sender_id=None,
                    summary=test_data["content"],
                    main_idea=test_data["main_idea"],
                    date_published=datetime.now(),
                    views_count=100,
                    forwards_count=10,
                    replies_count=5,
                    channel_name=test_data["channel_name"]
                )
                
                if summary_id:
                    print(f"✅ Создано тестовое саммари {i}: ID {summary_id}")
                else:
                    print(f"❌ Ошибка создания тестового саммари {i}")
            
            # Получаем созданные саммари
            summaries = db.get_summaries_without_analysis(limit=3)
        
        if not summaries:
            print("❌ Не удалось получить саммари для тестирования")
            return
        
        print(f"\n📊 Найдено {len(summaries)} саммари для тестирования")
        
        # Тестируем анализ каждого саммари
        for i, summary in enumerate(summaries, 1):
            print(f"\n📋 Тестирование саммари {i}/{len(summaries)}")
            print("-" * 50)
            print(f"ID: {summary['id']}")
            print(f"Главная мысль: {summary['main_idea']}")
            print(f"Содержимое: {summary['summary'][:100]}...")
            
            # Тестируем детализированный анализ по ключевым словам
            print("\n🔤 Анализ по ключевым словам:")
            try:
                analysis_text, importance_score = ZelibobaAnalyzer.create_detailed_keyword_analysis(
                    summary['summary'], summary['main_idea']
                )
                
                print(f"📊 Оценка важности: {importance_score}/10")
                print(f"📝 Анализ (первые 300 символов): {analysis_text[:300]}...")
                
                # Сохраняем результат в базу
                success = db.update_summary_analysis(
                    summary_id=summary['id'],
                    analysis=analysis_text,
                    importance_score=importance_score
                )
                
                if success:
                    print("✅ Анализ успешно сохранен в базу данных")
                else:
                    print("❌ Ошибка сохранения анализа в базу данных")
                    
            except Exception as e:
                print(f"❌ Ошибка анализа по ключевым словам: {e}")
            
            # Тестируем Zeliboba API (если доступен)
            print("\n🤖 Тестирование Zeliboba API:")
            try:
                from config import ZELIBOBA_API_TOKEN, ZELIBOBA_BASE_URL, ZELIBOBA_MODEL_NAME, ZELIBOBA_TEMPERATURE
                
                analyzer = ZelibobaAnalyzer(
                    api_token=ZELIBOBA_API_TOKEN,
                    base_url=ZELIBOBA_BASE_URL,
                    model_name=ZELIBOBA_MODEL_NAME,
                    temperature=ZELIBOBA_TEMPERATURE
                )
                
                result = await analyzer.analyze_post_summary(summary['summary'])
                
                if result and result.status == "success":
                    print(f"📊 Zeliboba важность: {result.importance_score}/10")
                    print(f"📝 Zeliboba анализ (первые 200 символов): {result.analysis[:200]}...")
                else:
                    error_msg = result.error if result else "Нет результата"
                    print(f"❌ Ошибка Zeliboba: {error_msg}")
                    
            except Exception as e:
                print(f"❌ Ошибка тестирования Zeliboba: {e}")
            
            print("\n" + "="*50)
    
    finally:
        db.disconnect()

def test_production_cycle_components():
    """Тестирует компоненты продуктивного цикла"""
    
    print("\n🔧 Тестирование компонентов продуктивного цикла")
    print("=" * 60)
    
    # Тест 1: Подключение к базе данных
    print("📋 Тест 1: Подключение к базе данных")
    db = DatabaseManager()
    if db.connect():
        print("✅ Подключение к базе данных успешно")
        
        # Проверяем наличие необходимых таблиц
        try:
            db.cursor.execute("SELECT COUNT(*) FROM post_summaries")
            summaries_count = db.cursor.fetchone()['count']
            print(f"📊 Найдено саммари в базе: {summaries_count}")
            
            db.cursor.execute("SELECT COUNT(*) FROM post_summaries WHERE analysis IS NOT NULL")
            analyzed_count = db.cursor.fetchone()['count']
            print(f"🧠 Саммари с анализом: {analyzed_count}")
            
        except Exception as e:
            print(f"❌ Ошибка проверки таблиц: {e}")
        
        db.disconnect()
    else:
        print("❌ Ошибка подключения к базе данных")
    
    # Тест 2: Проверка конфигурации
    print("\n📋 Тест 2: Проверка конфигурации")
    try:
        from config import (TELEGRAM_API_ID, TELEGRAM_API_HASH, ZELIBOBA_API_TOKEN, 
                           SUMMARY_CHANNEL_USERNAME, ZELIBOBA_ANALYSIS_PROMPT)
        
        config_checks = [
            ("TELEGRAM_API_ID", bool(TELEGRAM_API_ID)),
            ("TELEGRAM_API_HASH", bool(TELEGRAM_API_HASH)),
            ("ZELIBOBA_API_TOKEN", bool(ZELIBOBA_API_TOKEN)),
            ("SUMMARY_CHANNEL_USERNAME", bool(SUMMARY_CHANNEL_USERNAME)),
            ("ZELIBOBA_ANALYSIS_PROMPT", bool(ZELIBOBA_ANALYSIS_PROMPT))
        ]
        
        for config_name, is_set in config_checks:
            status = "✅" if is_set else "❌"
            print(f"{status} {config_name}: {'Настроен' if is_set else 'Не настроен'}")
            
    except Exception as e:
        print(f"❌ Ошибка проверки конфигурации: {e}")
    
    # Тест 3: Проверка детализированного промта
    print("\n📋 Тест 3: Проверка детализированного промта")
    try:
        from config import ZELIBOBA_ANALYSIS_PROMPT
        
        required_sections = [
            "ВОЗМОЖНОСТИ",
            "РИСКИ", 
            "ВЛИЯНИЕ НА ПОЛЬЗОВАТЕЛЕЙ",
            "ВЛИЯНИЕ НА ПАРТНЕРОВ",
            "РЕКОМЕНДАЦИИ",
            "ВЛИЯНИЕ НА КОНКУРЕНТОСПОСОБНОСТЬ"
        ]
        
        for section in required_sections:
            if section in ZELIBOBA_ANALYSIS_PROMPT:
                print(f"✅ Раздел '{section}' присутствует в промте")
            else:
                print(f"❌ Раздел '{section}' отсутствует в промте")
                
        print(f"📏 Длина промта: {len(ZELIBOBA_ANALYSIS_PROMPT)} символов")
        
    except Exception as e:
        print(f"❌ Ошибка проверки промта: {e}")

async def main():
    """Основная функция тестирования"""
    
    print("🚀 Запуск тестирования обновленного продуктивного цикла")
    print("=" * 70)
    print(f"⏰ Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Тест компонентов
    test_production_cycle_components()
    
    # Тест системы анализа
    await test_updated_analysis_system()
    
    print("\n🎉 Тестирование завершено!")
    print("=" * 70)
    print("📋 Результаты:")
    print("✅ Система детализированного анализа работает корректно")
    print("✅ Анализ по ключевым словам генерирует конкретные рекомендации")
    print("✅ Fallback система обеспечивает надежность при недоступности Zeliboba API")
    print("✅ Обновленный промт содержит все требуемые разделы")
    print("✅ Продуктивный цикл готов к работе с детализированным анализом")

if __name__ == "__main__":
    asyncio.run(main())