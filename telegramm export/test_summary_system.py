#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для тестирования системы саммари
"""

import asyncio
import logging
import sys
import os

# Добавляем текущую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ZELIBOBA_API_TOKEN, ZELIBOBA_MODEL_NAME, ZELIBOBA_TEMPERATURE
from database import DatabaseManager
from models import ZelibobaAnalyzer
from summary_processor import PostSummaryProcessor

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SummarySystemTester:
    """Класс для тестирования системы саммари"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.analyzer = None
        self.processor = None
    
    async def initialize(self):
        """Инициализация компонентов"""
        logger.info("Инициализация тестера системы саммари...")
        
        # Подключение к БД
        if not self.db.connect():
            logger.error("Не удалось подключиться к базе данных")
            return False
        
        # Проверка токена Zeliboba
        if not ZELIBOBA_API_TOKEN:
            logger.error("ZELIBOBA_API_TOKEN не настроен")
            return False
        
        # Инициализация анализатора
        self.analyzer = ZelibobaAnalyzer(
            ZELIBOBA_API_TOKEN,
            model_name=ZELIBOBA_MODEL_NAME,
            temperature=ZELIBOBA_TEMPERATURE
        )
        
        # Инициализация процессора
        self.processor = PostSummaryProcessor()
        
        logger.info("Все компоненты инициализированы")
        return True
    
    async def test_database_structure(self):
        """Тестирование структуры базы данных"""
        logger.info("🔍 Тестирование структуры базы данных...")
        
        try:
            # Проверяем существование таблицы post_summaries
            self.db.cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'post_summaries'
                );
            """)
            
            table_exists = self.db.cursor.fetchone()[0]
            
            if table_exists:
                logger.info("✅ Таблица post_summaries существует")
                
                # Проверяем структуру таблицы
                self.db.cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'post_summaries'
                    ORDER BY ordinal_position;
                """)
                
                columns = self.db.cursor.fetchall()
                logger.info("📋 Структура таблицы post_summaries:")
                for col in columns:
                    logger.info(f"   - {col['column_name']}: {col['data_type']}")
                
                # Проверяем количество записей
                self.db.cursor.execute("SELECT COUNT(*) as count FROM post_summaries")
                count = self.db.cursor.fetchone()['count']
                logger.info(f"📊 Количество саммари в БД: {count}")
                
                return True
            else:
                logger.error("❌ Таблица post_summaries не существует")
                logger.info("💡 Запустите: python telegram_summary_exporter.py --init-db")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка проверки БД: {e}")
            return False
    
    async def test_summary_creation(self):
        """Тестирование создания саммари"""
        logger.info("🔍 Тестирование создания саммари...")
        
        test_text = """
        Новая гостиница Marriott International открылась в центре Москвы на Тверской улице. 
        Отель предлагает 200 номеров различных категорий, включая 50 люксов с панорамным видом на Кремль. 
        
        В отеле работают три ресторана: основной ресторан европейской кухни, суши-бар и кофейня. 
        Также доступны спа-центр площадью 800 кв.м, фитнес-зал и конференц-залы на 300 человек.
        
        Управляющий отелем Александр Петров отметил, что они ожидают высокую загрузку благодаря 
        удачному расположению в историческом центре города. Стоимость номеров начинается от 15 000 рублей 
        за ночь в стандартном номере и до 80 000 рублей за президентский люкс.
        
        Отель уже принял первых гостей и получил положительные отзывы о качестве сервиса и 
        современном дизайне интерьеров. Планируется, что к концу года загрузка достигнет 75%.
        """
        
        try:
            # Тестируем создание саммари
            summary_result = await self.analyzer.create_summary(test_text)
            
            if summary_result and summary_result.get("status") == "success":
                analysis_text = summary_result.get("analysis_text", "")
                
                # Извлекаем части саммари
                from summary_processor import PostSummaryProcessor
                processor = PostSummaryProcessor()
                main_idea, summary = processor.extract_summary_parts(analysis_text)
                
                logger.info("✅ Саммари успешно создано")
                logger.info(f"💡 Главная мысль: {main_idea}")
                logger.info(f"📝 Саммари: {summary[:200]}...")
                logger.info(f"📏 Длина саммари: {len(summary.split())} слов")
                
                # Проверяем ограничения
                word_count = len(summary.split())
                if word_count <= 1000:
                    logger.info("✅ Саммари соответствует ограничению в 1000 слов")
                else:
                    logger.warning(f"⚠️ Саммари превышает лимит: {word_count} слов")
                
                return True
            else:
                error = summary_result.get("error", "Неизвестная ошибка") if summary_result else "Нет ответа"
                logger.error(f"❌ Ошибка создания саммари: {error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Исключение при тестировании саммари: {e}")
            return False
    
    async def test_existing_posts_processing(self):
        """Тестирование обработки существующих постов"""
        logger.info("🔍 Тестирование обработки существующих постов...")
        
        try:
            # Проверяем наличие постов для обработки
            self.db.cursor.execute("""
                SELECT COUNT(*) as count FROM posts p
                LEFT JOIN post_summaries ps ON p.channel_id = ps.channel_id 
                    AND p.telegram_message_id = ps.telegram_message_id
                WHERE ps.id IS NULL
                AND p.content IS NOT NULL
                AND p.content != ''
                AND LENGTH(p.content) >= 100
            """)
            
            posts_to_process = self.db.cursor.fetchone()['count']
            logger.info(f"📊 Постов ожидают создания саммари: {posts_to_process}")
            
            if posts_to_process > 0:
                logger.info("✅ Есть посты для обработки")
                logger.info("💡 Запустите: python summary_processor.py --process --limit 5")
                return True
            else:
                logger.info("ℹ️ Нет постов для обработки (все уже имеют саммари)")
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка проверки постов: {e}")
            return False
    
    async def test_summary_analysis(self):
        """Тестирование анализа важности саммари"""
        logger.info("🔍 Тестирование анализа важности саммари...")
        
        try:
            # Проверяем наличие саммари для анализа
            self.db.cursor.execute("""
                SELECT COUNT(*) as count FROM post_summaries ps
                LEFT JOIN zeliboba_analysis za ON ps.id = za.post_id 
                    AND za.analysis_type = 'summary_importance'
                WHERE za.id IS NULL
            """)
            
            summaries_to_analyze = self.db.cursor.fetchone()['count']
            logger.info(f"📊 Саммари ожидают анализа важности: {summaries_to_analyze}")
            
            if summaries_to_analyze > 0:
                logger.info("✅ Есть саммари для анализа важности")
                return True
            else:
                logger.info("ℹ️ Нет саммари для анализа (все уже проанализированы)")
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка проверки саммари: {e}")
            return False
    
    async def test_publication_readiness(self):
        """Тестирование готовности к публикации"""
        logger.info("🔍 Тестирование готовности к публикации...")
        
        try:
            # Проверяем наличие важных саммари для публикации
            important_summaries = self.db.get_top_important_summaries_for_publication(5)
            
            if important_summaries:
                logger.info(f"✅ Найдено {len(important_summaries)} важных саммари для публикации")
                
                for i, summary in enumerate(important_summaries, 1):
                    importance_score = summary.get('importance_score', 'N/A')
                    channel_title = summary.get('channel_title', 'Unknown')
                    main_idea = summary.get('main_idea', '')[:100] + "..."
                    
                    logger.info(f"   {i}. Важность: {importance_score}/10, Канал: {channel_title}")
                    logger.info(f"      Главная мысль: {main_idea}")
                
                return True
            else:
                logger.info("ℹ️ Нет важных саммари для публикации")
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка проверки готовности к публикации: {e}")
            return False
    
    async def run_full_test(self):
        """Запуск полного тестирования"""
        logger.info("🚀 Запуск полного тестирования системы саммари")
        logger.info("=" * 60)
        
        tests = [
            ("Структура базы данных", self.test_database_structure),
            ("Создание саммари", self.test_summary_creation),
            ("Обработка существующих постов", self.test_existing_posts_processing),
            ("Анализ важности саммари", self.test_summary_analysis),
            ("Готовность к публикации", self.test_publication_readiness),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n📋 Тест: {test_name}")
            logger.info("-" * 40)
            
            try:
                result = await test_func()
                if result:
                    logger.info(f"✅ {test_name}: ПРОЙДЕН")
                    passed += 1
                else:
                    logger.error(f"❌ {test_name}: НЕ ПРОЙДЕН")
            except Exception as e:
                logger.error(f"❌ {test_name}: ОШИБКА - {e}")
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 ИТОГИ ТЕСТИРОВАНИЯ")
        logger.info("=" * 60)
        logger.info(f"✅ Пройдено тестов: {passed}/{total}")
        logger.info(f"❌ Не пройдено тестов: {total - passed}/{total}")
        
        if passed == total:
            logger.info("🎉 Все тесты пройдены! Система саммари готова к работе.")
        else:
            logger.warning("⚠️ Некоторые тесты не пройдены. Проверьте настройки и исправьте ошибки.")
        
        return passed == total
    
    def cleanup(self):
        """Очистка ресурсов"""
        if self.db:
            self.db.disconnect()

async def main():
    """Основная функция тестирования"""
    tester = SummarySystemTester()
    
    try:
        if not await tester.initialize():
            logger.error("Не удалось инициализировать тестер")
            return
        
        await tester.run_full_test()
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    print("🧪 Тестирование системы саммари")
    print("Этот скрипт проверяет все компоненты системы саммари")
    print("=" * 60)
    
    asyncio.run(main())