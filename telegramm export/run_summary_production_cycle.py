#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Продуктивный цикл с саммари: экспорт постов за 24 часа, создание саммари и публикация в канал
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Добавляем текущую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (TELEGRAM_API_ID, TELEGRAM_API_HASH, SESSION_PATH,
                   ZELIBOBA_API_TOKEN, SUMMARY_CHANNEL_USERNAME,
                   ZELIBOBA_ANALYSIS_PROMPT, ZELIBOBA_MODEL_NAME, ZELIBOBA_TEMPERATURE)
from database import DatabaseManager
from telegram_publisher import TelegramPublisher
from models import ZelibobaAnalyzer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('summary_production_cycle.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Импорт Telethon
try:
    from telethon import TelegramClient
    from telegram_summary_exporter import export_chat_with_summaries, get_entity_by_name_or_id
except ImportError as e:
    logger.error(f"Ошибка импорта: {e}")
    sys.exit(1)

class SummaryProductionCycle:
    """Класс для управления продуктивным циклом с саммари"""
    
    def __init__(self):
        self.client = None
        self.db_manager = None
        self.publisher = None
        self.analyzer = None
        
    async def initialize(self):
        """Инициализация всех компонентов"""
        logger.info("Инициализация продуктивного цикла с саммари...")
        
        # Проверяем настройки
        if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
            logger.error("Не настроены TELEGRAM_API_ID и TELEGRAM_API_HASH")
            return False
            
        if not ZELIBOBA_API_TOKEN:
            logger.error("Не настроен ZELIBOBA_API_TOKEN")
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
        session_path = os.path.join(os.path.dirname(__file__), SESSION_PATH + "_summary")
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
        
        # Инициализация анализатора Zeliboba
        self.analyzer = ZelibobaAnalyzer(
            ZELIBOBA_API_TOKEN,
            model_name=ZELIBOBA_MODEL_NAME,
            temperature=ZELIBOBA_TEMPERATURE
        )
        
        logger.info("Все компоненты успешно инициализированы")
        return True
    
    async def export_summaries_from_channels(self, channels_list):
        """Экспорт постов из списка каналов с созданием саммари за последние 24 часа"""
        logger.info(f"Начинаем экспорт с созданием саммари из {len(channels_list)} каналов")
        
        total_summaries_created = 0
        
        for channel_name in channels_list:
            try:
                logger.info(f"Экспорт с созданием саммари из канала: {channel_name}")
                
                # Получаем entity канала
                chat_entity = await get_entity_by_name_or_id(self.client, channel_name)
                if not chat_entity:
                    logger.warning(f"Канал {channel_name} не найден")
                    continue
                
                # Экспортируем только за последние 24 часа с созданием саммари
                filename, stats = await export_chat_with_summaries(
                    self.client,
                    chat_entity,
                    limit=None,  # Без ограничения количества
                    output_file=None,  # Автоматическое имя файла
                    save_to_db=True,
                    db_manager=self.db_manager,
                    last_24_hours_only=True  # Только за последние 24 часа
                )
                
                if stats:
                    summaries_count = getattr(stats, 'summaries_created', 0)
                    logger.info(f"Канал {channel_name}: создано {summaries_count} саммари")
                    total_summaries_created += summaries_count
                else:
                    logger.warning(f"Не удалось экспортировать из канала {channel_name}")
                    
            except Exception as e:
                logger.error(f"Ошибка экспорта из канала {channel_name}: {e}")
                continue
        
        logger.info(f"Общий экспорт завершен. Всего создано саммари: {total_summaries_created}")
        return total_summaries_created
    
    async def analyze_summaries(self, limit=None, use_keyword_analysis=True):
        """Анализ саммари для определения важности (Zeliboba API + анализ по ключевым словам)"""
        logger.info("Начинаем анализ саммари для определения важности")
        
        try:
            # Получаем саммари без анализа важности
            summaries = self.db_manager.get_summaries_without_analysis(limit)
            
            if not summaries:
                logger.info("Нет новых саммари для анализа")
                return 0
            
            logger.info(f"Найдено {len(summaries)} саммари для анализа")
            
            success_count = 0
            error_count = 0
            
            for i, summary in enumerate(summaries, 1):
                try:
                    logger.info(f"Анализируем саммари {i}/{len(summaries)} (ID: {summary['id']})")
                    
                    # Проверяем, что у саммари есть контент
                    if not summary['summary'] or not summary['summary'].strip():
                        logger.warning(f"Саммари {summary['id']} не содержит текста, пропускаем")
                        continue
                    
                    analysis_text = None
                    importance_score = 5.0
                    analysis_successful = False
                    
                    # Сначала пробуем Zeliboba API
                    try:
                        logger.info(f"Пробуем анализ через Zeliboba API для саммари {summary['id']}")
                        analysis_result = await self.analyzer.analyze_post_summary(summary['summary'])
                        
                        if analysis_result and analysis_result.status == "success":
                            analysis_text = analysis_result.analysis
                            importance_score = analysis_result.importance_score
                            analysis_successful = True
                            logger.info(f"✅ Zeliboba анализ успешен для саммари {summary['id']}, важность: {importance_score}/10")
                        else:
                            error_msg = analysis_result.error if analysis_result else "Нет результата"
                            logger.warning(f"⚠️ Zeliboba анализ неуспешен для саммари {summary['id']}: {error_msg}")
                    except Exception as zeliboba_error:
                        logger.warning(f"⚠️ Ошибка Zeliboba API для саммари {summary['id']}: {zeliboba_error}")
                    
                    # Если Zeliboba не сработал, используем анализ по ключевым словам
                    if not analysis_successful and use_keyword_analysis:
                        logger.info(f"Используем анализ по ключевым словам для саммари {summary['id']}")
                        try:
                            # Получаем содержимое поста для более точного анализа
                            post_content = summary.get('summary', '')
                            main_idea = summary.get('main_idea', '')
                            
                            # Используем новую детализированную функцию анализа
                            analysis_text, importance_score = ZelibobaAnalyzer.create_detailed_keyword_analysis(
                                post_content, main_idea
                            )
                            analysis_successful = True
                            logger.info(f"✅ Анализ по ключевым словам успешен для саммари {summary['id']}, важность: {importance_score}/10")
                        except Exception as keyword_error:
                            logger.error(f"❌ Ошибка анализа по ключевым словам для саммари {summary['id']}: {keyword_error}")
                    
                    # Сохраняем результат анализа
                    if analysis_successful and analysis_text:
                        success = self.db_manager.update_summary_analysis(
                            summary_id=summary['id'],
                            analysis=analysis_text,
                            importance_score=importance_score
                        )
                        
                        if success:
                            success_count += 1
                            logger.info(f"✅ Анализ успешно сохранен для саммари {summary['id']}")
                        else:
                            logger.error(f"❌ Не удалось сохранить анализ для саммари {summary['id']}")
                            error_count += 1
                    else:
                        logger.error(f"❌ Не удалось проанализировать саммари {summary['id']}")
                        error_count += 1
                    
                    # Пауза между анализами
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка при анализе саммари {summary['id']}: {e}")
                    error_count += 1
            
            logger.info(f"Анализ завершен. Успешно: {success_count}, Ошибок: {error_count}")
            return success_count
            
        except Exception as e:
            logger.error(f"Ошибка при анализе саммари: {e}")
            return 0
    
    async def publish_top_important_summaries(self, limit=5):
        """Публикация топ-5 самых важных саммари в канал"""
        logger.info(f"Публикация топ-{limit} самых важных саммари в канал {SUMMARY_CHANNEL_USERNAME}")
        
        try:
            # Получаем топ важных саммари за последние 24 часа
            important_summaries = self.db_manager.get_top_important_summaries_for_publication(limit)
            
            if not important_summaries:
                logger.info("Нет важных саммари для публикации")
                return 0
            
            sent_count = 0
            for row in important_summaries:
                try:
                    # Формируем данные для публикации саммари
                    summary_data = {
                        'summary': row['summary'],
                        'main_idea': row['main_idea'],
                        'analysis': row['analysis'],  # Используем поле analysis вместо analysis_text
                        'importance_score': row['importance_score'],
                        'date_published': row['date_published'],
                        'telegram_message_id': row['telegram_message_id'],
                        'channel_username': row.get('channel_username', ''),
                        'channel_title': row['channel_title']
                    }
                    
                    importance_score = row.get('importance_score', 5)
                    logger.info(f"Публикуем саммари с важностью {importance_score}/10 из канала {row['channel_title']}")
                    
                    # Отправляем саммари с анализом
                    success = await self.publisher.send_summary_with_analysis(
                        SUMMARY_CHANNEL_USERNAME,
                        summary_data
                    )
                    
                    if success:
                        sent_count += 1
                        # Небольшая пауза между отправками
                        await asyncio.sleep(2)
                    else:
                        logger.error(f"Не удалось отправить саммари для поста {row['id']}")
                        
                except Exception as e:
                    logger.error(f"Ошибка обработки саммари {row['id']}: {e}")
                    continue
            
            logger.info(f"Опубликовано {sent_count} из {len(important_summaries)} важных саммари")
            return sent_count
            
        except Exception as e:
            logger.error(f"Ошибка публикации важных саммари: {e}")
            return 0
    
    async def get_statistics(self):
        """Получение статистики работы с саммари"""
        try:
            # Статистика по саммари
            self.db_manager.cursor.execute("SELECT COUNT(*) as total_summaries FROM post_summaries")
            summaries_stats = self.db_manager.cursor.fetchone()
            
            # Статистика по анализам саммари
            self.db_manager.cursor.execute("""
                SELECT COUNT(*) as analyzed_summaries FROM zeliboba_analysis 
                WHERE analysis_type = 'summary_importance' AND status = 'success'
            """)
            analyzed_stats = self.db_manager.cursor.fetchone()
            
            # Саммари за последние 24 часа
            self.db_manager.cursor.execute("""
                SELECT COUNT(*) as recent_summaries FROM post_summaries 
                WHERE date_published >= NOW() - INTERVAL '24 hours'
            """)
            recent_stats = self.db_manager.cursor.fetchone()
            
            logger.info("📊 Статистика работы с саммари:")
            logger.info(f"   Всего саммари: {summaries_stats['total_summaries']}")
            logger.info(f"   Проанализировано саммари: {analyzed_stats['analyzed_summaries']}")
            logger.info(f"   Саммари за 24 часа: {recent_stats['recent_summaries']}")
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
    
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
    """Основная функция продуктивного цикла с саммари"""
    
    # Список каналов для мониторинга (можно настроить)
    # Основные каналы для мониторинга (можно настроить)
    PRIMARY_CHANNELS = (
        "@wrkhotel",        # Официальный канал отелей
        "@Hotelier_PRO",    # Профессиональное сообщество отельеров
        "@russpass_business",  # Бизнес-новости туризма
        "@bnovonews",       # Новости гостиничного бизнеса
        "@buhtourbiz",      # Бюджетный туризм и бизнес
        "@corona_travel"    # Аналитика туристического рынка
    )

    # Дополнительные каналы (раскомментировать по необходимости)
    # SECONDARY_CHANNELS = (
    #     "@another_channel",
    #     "@test_channel",
    # )

    channels_to_monitor = PRIMARY_CHANNELS  # + SECONDARY_CHANNELS
    
    cycle = SummaryProductionCycle()
    
    try:
        # Инициализация
        if not await cycle.initialize():
            logger.error("Не удалось инициализировать продуктивный цикл с саммари")
            return
        
        logger.info("🚀 Запуск продуктивного цикла с саммари")
        logger.info(f"📅 Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"📺 Каналы для мониторинга: {', '.join(channels_to_monitor)}")
        logger.info(f"📤 Канал для публикации: {SUMMARY_CHANNEL_USERNAME}")
        
        # Показываем текущую статистику
        await cycle.get_statistics()
        
        # Шаг 1: Экспорт постов с созданием саммари за последние 24 часа
        logger.info("=" * 50)
        logger.info("ШАГ 1: Экспорт постов с созданием саммари за последние 24 часа")
        logger.info("=" * 50)
        
        summaries_created = await cycle.export_summaries_from_channels(channels_to_monitor)
        
        if summaries_created == 0:
            logger.info("Нет новых постов для создания саммари")
        else:
            logger.info(f"✅ Создано {summaries_created} новых саммари")
        
        # Шаг 2: Анализ саммари для определения важности через Zeliboba AI
        logger.info("=" * 50)
        logger.info("ШАГ 2: Анализ саммари для определения важности через Zeliboba AI")
        logger.info("=" * 50)
        
        analyzed_count = await cycle.analyze_summaries()
        
        if analyzed_count == 0:
            logger.info("Нет новых саммари для анализа")
        else:
            logger.info(f"✅ Проанализировано {analyzed_count} новых саммари")
        
        # Шаг 3: Публикация топ-5 самых важных саммари
        logger.info("=" * 50)
        logger.info("ШАГ 3: Публикация топ-5 самых важных саммари индустрии")
        logger.info("=" * 50)
        
        published_count = await cycle.publish_top_important_summaries(limit=5)
        
        if published_count == 0:
            logger.info("Нет важных саммари для публикации")
        else:
            logger.info(f"✅ Опубликовано {published_count} важных саммари")
        
        # Итоговая статистика
        logger.info("=" * 50)
        logger.info("ИТОГОВАЯ СТАТИСТИКА")
        logger.info("=" * 50)
        logger.info(f"📝 Создано саммари: {summaries_created}")
        logger.info(f"🧠 Проанализировано саммари: {analyzed_count}")
        logger.info(f"📤 Опубликовано важных саммари: {published_count}")
        logger.info(f"⏰ Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("🎉 Продуктивный цикл с саммари завершен успешно!")
        
        # Финальная статистика
        await cycle.get_statistics()
        
    except Exception as e:
        logger.error(f"Критическая ошибка в продуктивном цикле: {e}")
        raise
    finally:
        await cycle.cleanup()

if __name__ == "__main__":
    print("🤖 Запуск продуктивного цикла с саммари Telegram экспортера")
    print("📋 Этапы:")
    print("   1. Экспорт постов с созданием саммари за последние 24 часа")
    print("   2. Анализ саммари для определения важности через Zeliboba AI")
    print("   3. Публикация топ-5 самых важных саммари в канал")
    print("💡 Особенности:")
    print("   - Сохраняются только саммари, не полные тексты постов")
    print("   - Саммари не более 3 абзацев и 1000 слов")
    print("   - Явное выделение главной мысли каждого поста")
    print("=" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)