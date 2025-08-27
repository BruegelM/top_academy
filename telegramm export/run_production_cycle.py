#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Продуктивный цикл: экспорт постов за 24 часа, анализ и публикация в канал
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Добавляем текущую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (TELEGRAM_API_ID, TELEGRAM_API_HASH, SESSION_PATH,
                   SUMMARY_CHANNEL_USERNAME)
from database import DatabaseManager
from telegram_publisher import TelegramPublisher

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_cycle.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Импорт Telethon
try:
    from telethon import TelegramClient
    from telegram_chat_exporter import export_chat_history, get_entity_by_name_or_id
except ImportError as e:
    logger.error(f"Ошибка импорта: {e}")
    sys.exit(1)

class ProductionCycle:
    """Класс для управления продуктивным циклом"""
    
    def __init__(self):
        self.client = None
        self.db_manager = None
        self.publisher = None
        self.analyzer = None
        
    async def initialize(self):
        """Инициализация всех компонентов"""
        logger.info("Инициализация продуктивного цикла...")
        
        # Проверяем настройки
        if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
            logger.error("Не настроены TELEGRAM_API_ID и TELEGRAM_API_HASH")
            return False
            
            
        if not SUMMARY_CHANNEL_USERNAME:
            logger.error("Не настроен SUMMARY_CHANNEL_USERNAME")
            return False
        
        # Инициализация базы данных
        self.db_manager = DatabaseManager()
        if not self.db_manager.connect():
            logger.error("Не удалось подключиться к базе данных")
            return False
        
        # Создаем таблицы если их нет
        self.db_manager.create_tables()
        
        # Инициализация Telegram клиента
        session_path = os.path.join(os.path.dirname(__file__), SESSION_PATH)
        self.client = TelegramClient(session_path, TELEGRAM_API_ID, TELEGRAM_API_HASH)
        
        try:
            await self.client.start()
            logger.info("Telegram клиент успешно подключен")
        except Exception as e:
            logger.error(f"Ошибка подключения к Telegram: {e}")
            return False
        
        # Инициализация публикатора
        self.publisher = TelegramPublisher()
        if not await self.publisher.connect():
            logger.error("Не удалось подключить публикатор")
            return False
        
        
        logger.info("Все компоненты успешно инициализированы")
        return True
    
    async def export_from_channels(self, channels_list):
        """Экспорт постов из списка каналов за последние 24 часа"""
        logger.info(f"Начинаем экспорт из {len(channels_list)} каналов")
        
        total_exported = 0
        
        for channel_name in channels_list:
            try:
                logger.info(f"Экспорт из канала: {channel_name}")
                
                # Получаем entity канала
                chat_entity = await get_entity_by_name_or_id(self.client, channel_name)
                if not chat_entity:
                    logger.warning(f"Канал {channel_name} не найден")
                    continue
                
                # Экспортируем только за последние 24 часа (по умолчанию)
                filename, stats = await export_chat_history(
                    self.client,
                    chat_entity,
                    limit=None,  # Без ограничения количества
                    output_file=None,  # Автоматическое имя файла
                    save_to_db=True,
                    db_manager=self.db_manager,
                    last_24_hours_only=True  # Только за последние 24 часа
                )
                
                if stats:
                    logger.info(f"Канал {channel_name}: экспортировано {stats.saved_to_db} сообщений")
                    total_exported += stats.saved_to_db
                else:
                    logger.warning(f"Не удалось экспортировать из канала {channel_name}")
                    
            except Exception as e:
                logger.error(f"Ошибка экспорта из канала {channel_name}: {e}")
                continue
        
        logger.info(f"Общий экспорт завершен. Всего экспортировано: {total_exported} сообщений")
        return total_exported
    
    async def analyze_new_posts(self, limit=None):
        """Анализ новых постов в базе данных"""
        logger.info("Анализ новых постов...")
        try:
            from summary_processor import SummaryProcessor
            processor = SummaryProcessor()
            analyzed_count = processor.analyze_recent_posts(limit=limit)
            logger.info(f"Проанализировано {analyzed_count} постов")
            return analyzed_count
        except Exception as e:
            logger.error(f"Ошибка анализа постов: {e}")
            raise
    
    async def publish_top_important_summaries(self, limit=5):
        """Публикация топ постов в канал (без анализа Zeliboba)"""
        logger.info(f"Публикация топ-{limit} новостей в канал {SUMMARY_CHANNEL_USERNAME}")
        
        try:
            # Получаем топ постов по метрикам
            top_posts = self.db_manager.get_top_important_posts_for_publication(limit)
            
            if not top_posts:
                logger.info("Нет новостей для публикации")
                return 0
            
            sent_count = 0
            for row in top_posts:
                try:
                    original_post = {
                        'content': row['content'],
                        'date_published': row['date_published'],
                        'telegram_message_id': row['telegram_message_id'],
                        'channel_username': row['channel_username']
                    }
                    
                    # Получаем анализ поста из базы
                    analysis = self.db_manager.get_post_analysis(row['id'])
                    if not analysis:
                        logger.warning(f"Анализ для поста {row['id']} не найден")
                        continue
                        
                    success = await self.publisher.send_summary(
                        SUMMARY_CHANNEL_USERNAME,
                        original_post,
                        analysis,
                        row['channel_title']
                    )
                    
                    if success:
                        sent_count += 1
                        await asyncio.sleep(2)
                    else:
                        logger.error(f"Не удалось отправить новость для поста {row['id']}")
                        
                except Exception as e:
                    logger.error(f"Ошибка обработки поста {row['id']}: {e}")
                    continue
            
            logger.info(f"Опубликовано {sent_count} из {len(top_posts)} новостей")
            return sent_count
            
        except Exception as e:
            logger.error(f"Ошибка публикации новостей: {e}")
            return 0
    
    
    async def cleanup(self):
        """Очистка ресурсов"""
        logger.info("Завершение работы...")
        
        if self.client:
            await self.client.disconnect()
        
        if self.publisher:
            await self.publisher.disconnect()
        
        if self.db_manager:
            self.db_manager.disconnect()
        
        logger.info("Все ресурсы освобождены")

async def main():
    """Основная функция продуктивного цикла"""
    
    # Список каналов для мониторинга
    channels_to_monitor = [
        "@wrkhotel",        # Официальный канал отелей
        "@Hotelier_PRO",    # Профессиональное сообщество отельеров
        "@russpass_business",  # Бизнес-новости туризма
        "@bnovonews",       # Новости гостиничного бизнеса
        "@buhtourbiz",      # Бюджетный туризм и бизнес
        "@corona_travel"    # Новости туризма в условиях пандемии
    ]
    
    cycle = ProductionCycle()
    
    try:
        # Инициализация
        if not await cycle.initialize():
            logger.error("Не удалось инициализировать продуктивный цикл")
            return
        
        logger.info("🚀 Запуск продуктивного цикла")
        logger.info(f"📅 Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"📺 Каналы для мониторинга: {', '.join(channels_to_monitor)}")
        logger.info(f"📤 Канал для публикации: {SUMMARY_CHANNEL_USERNAME}")
        
        # Шаг 1: Экспорт постов за последние 24 часа
        logger.info("=" * 50)
        logger.info("ШАГ 1: Экспорт постов за последние 24 часа")
        logger.info("=" * 50)
        
        exported_count = await cycle.export_from_channels(channels_to_monitor)
        
        if exported_count == 0:
            logger.info("Нет новых постов для экспорта")
        else:
            logger.info(f"✅ Экспортировано {exported_count} новых постов")
        
        # Шаг 2: Анализ новых постов
        logger.info("=" * 50)
        logger.info("ШАГ 2: Анализ новых постов")
        logger.info("=" * 50)
        
        analyzed_count = await cycle.analyze_new_posts()
        if analyzed_count == 0:
            logger.warning("Не удалось проанализировать посты")
        
        # Шаг 3: Публикация топ-5 самых важных новостей
        logger.info("=" * 50)
        logger.info("ШАГ 3: Публикация топ-5 самых важных новостей индустрии")
        logger.info("=" * 50)
        
        published_count = await cycle.publish_top_important_summaries(limit=5)
        
        if published_count == 0:
            logger.info("Нет важных новостей для публикации")
        else:
            logger.info(f"✅ Опубликовано {published_count} важных новостей")
        
        # Итоговая статистика
        logger.info("=" * 50)
        logger.info("ИТОГОВАЯ СТАТИСТИКА")
        logger.info("=" * 50)
        logger.info(f"📥 Экспортировано постов: {exported_count}")
        # analyzed_count уже получен выше
        logger.info(f"🧠 Проанализировано постов: {analyzed_count}")
        logger.info(f"📤 Опубликовано важных новостей: {published_count}")
        logger.info(f"⏰ Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("🎉 Продуктивный цикл завершен успешно!")
        
    except Exception as e:
        logger.error(f"Критическая ошибка в продуктивном цикле: {e}")
        raise
    finally:
        await cycle.cleanup()

if __name__ == "__main__":
    print("🤖 Запуск продуктивного цикла Telegram экспортера")
    print("📋 Этапы:")
    print("   1. Экспорт постов за последние 24 часа")
    print("   2. Анализ новых постов пропущен (режим без Zeliboba)")
    print("   3. Публикация топ-5 самых важных новостей в канал")
    print("=" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)