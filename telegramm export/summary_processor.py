#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для обработки постов из телеграм каналов с созданием саммари
Вместо сохранения полных текстов постов создает и сохраняет только саммари
"""

import asyncio
import argparse
import sys
import logging
import re
from datetime import datetime
from database import DatabaseManager
from ai_analyzers import ZelibobaAnalyzer, ElizaAnalyzer
from models_optimized import MessageProcessor
from config import AISettings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('summary_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PostSummaryProcessor:
    def __init__(self):
        self.db = DatabaseManager()
        if not self.db.connect():
            logger.error("Не удалось подключиться к базе данных")
            sys.exit(1)
        
        # Инициализируем анализаторы из новых настроек
        self.zeliboba_analyzer = None
        self.eliza_analyzer = None
        
        if AISettings.ZELIBOBA['api_token']:
            self.zeliboba_analyzer = ZelibobaAnalyzer(
                AISettings.ZELIBOBA['api_token'],
                AISettings.ZELIBOBA['base_url'],
                AISettings.ZELIBOBA['model'],
                AISettings.ZELIBOBA['temperature']
            )
        
        if AISettings.ELIZA['api_token']:
            self.eliza_analyzer = ElizaAnalyzer(
                AISettings.ELIZA['api_token'],
                AISettings.ELIZA['base_url'],
                AISettings.ELIZA['model'],
                AISettings.ELIZA['temperature']
            )
        
        if not self.zeliboba_analyzer and not self.eliza_analyzer:
            logger.error("Не настроены API токены для Zeliboba или Eliza")
            sys.exit(1)
            
        logger.info(f"Инициализирован процессор саммари (Zeliboba: {AISettings.ZELIBOBA['model'] if self.zeliboba_analyzer else 'нет'}, Eliza: {AISettings.ELIZA['model'] if self.eliza_analyzer else 'нет'})")

    async def close(self):
        """Закрытие всех ресурсов"""
        if hasattr(self, 'db'):
            self.db.disconnect()
        if hasattr(self, 'eliza_analyzer') and self.eliza_analyzer:
            await self.eliza_analyzer.close()
        if hasattr(self, 'zeliboba_analyzer') and self.zeliboba_analyzer:
            await self.zeliboba_analyzer.close()

    def __del__(self):
        if hasattr(self, 'db'):
            self.db.disconnect()

    def extract_summary_parts(self, analysis_text: str) -> tuple:
        """
        Извлекает главную мысль, саммари и полный анализ из ответа GPT
        
        Args:
            analysis_text: текст ответа от GPT
            
        Returns:
            tuple: (main_idea, summary, full_analysis)
        """
        try:
            # Ищем главную мысль
            main_idea_match = re.search(
                r'(?:КРАТКОЕ РЕЗЮМЕ|ГЛАВНАЯ МЫСЛЬ):\s*(.+?)(?:\n\n|$)',
                analysis_text,
                re.DOTALL | re.IGNORECASE
            )
            main_idea = main_idea_match.group(1).strip() if main_idea_match else ""
            
            # Ищем саммари (первые 1000 слов)
            summary = analysis_text[:1000] + "..." if len(analysis_text) > 1000 else analysis_text
            
            # Если не удалось извлечь главную мысль, берем первое предложение
            if not main_idea:
                sentences = analysis_text.split('.')
                main_idea = sentences[0].strip() + '.' if sentences else analysis_text[:200] + "..."
            
            # Полный анализ сохраняем как есть
            full_analysis = analysis_text
            
            return main_idea, summary, full_analysis
            
        except Exception as e:
            logger.error(f"Ошибка извлечения частей саммари: {e}")
            # В случае ошибки возвращаем исходный текст
            return analysis_text[:200] + "..." if len(analysis_text) > 200 else analysis_text, analysis_text
    
    async def process_posts_to_summaries(self, limit=None):
        """Обрабатывает посты из таблицы posts и создает саммари"""
        logger.info("Поиск постов для создания саммари")
        
        try:
            # Получаем посты, для которых еще нет саммари
            query = """
                SELECT p.* FROM posts p
                LEFT JOIN post_summaries ps ON p.channel_id = ps.channel_id 
                    AND p.telegram_message_id = ps.telegram_message_id
                WHERE ps.id IS NULL
                AND p.content IS NOT NULL
                AND p.content != ''
                ORDER BY p.date_published DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            self.db.cursor.execute(query)
            posts = self.db.cursor.fetchall()
            
            if not posts:
                logger.info("Все посты уже имеют саммари")
                return
            
            logger.info(f"Найдено {len(posts)} постов для создания саммари")
            
            success_count = 0
            error_count = 0
            
            for i, post in enumerate(posts, 1):
                try:
                    logger.info(f"Создаем саммари для поста {i}/{len(posts)} (ID: {post['id']})")
                    
                    # Проверяем длину контента
                    if len(post['content']) < 50:
                        logger.warning(f"Пост {post['id']} слишком короткий для саммари, пропускаем")
                        continue
                    
                    # Создаем саммари через Eliza или Zeliboba
                    summary_result = None
                    if self.eliza_analyzer:
                        summary_result = await self.eliza_analyzer.analyze_content(
                            content=post['content'],
                            prompt="Создай краткое саммари новости для Яндекс Путешествий"
                        )
                    
                    # Если Eliza не сработал или не настроен, пробуем Zeliboba
                    if (not summary_result or summary_result.get("status") != "success") and self.zeliboba_analyzer:
                        summary_result = await self.zeliboba_analyzer.create_summary(post['content'])
                    
                    if summary_result and summary_result.get("status") == "success":
                        analysis_text = summary_result.get("analysis_text", "")
                        
                        if analysis_text:
                            # Извлекаем главную мысль и саммари
                            main_idea, summary = self.extract_summary_parts(analysis_text)
                            
                            # Сохраняем саммари и полный анализ в базу данных
                            summary_id = self.db.save_post_summary(
                                channel_id=post['channel_id'],
                                telegram_message_id=post['telegram_message_id'],
                                sender_name=post['sender_name'],
                                sender_id=post['sender_id'],
                                summary=summary,
                                main_idea=main_idea,
                                date_published=post['date_published'],
                                views_count=post['views_count'],
                                forwards_count=post['forwards_count'],
                                replies_count=post['replies_count'],
                                analysis=analysis_text  # Сохраняем полный анализ
                            )
                            
                            if summary_id:
                                logger.info(f"✅ Саммари успешно создано для поста {post['id']} (Summary ID: {summary_id})")
                                success_count += 1
                                
                                # Показываем краткую информацию о созданном саммари
                                logger.debug(f"Главная мысль: {main_idea[:100]}...")
                                logger.debug(f"Саммари: {summary[:200]}...")
                            else:
                                logger.error(f"❌ Не удалось сохранить саммари для поста {post['id']}")
                                error_count += 1
                        else:
                            logger.error(f"❌ Получен пустой ответ от GPT для поста {post['id']}")
                            error_count += 1
                    else:
                        error_message = summary_result.get("error", "Неизвестная ошибка") if summary_result else "Нет ответа от API"
                        logger.error(f"❌ Ошибка создания саммари для поста {post['id']}: {error_message}")
                        error_count += 1
                    
                    # Небольшая пауза между запросами
                    await asyncio.sleep(1.0)
                    
                except Exception as e:
                    logger.error(f"❌ Исключение при обработке поста {post['id']}: {e}")
                    error_count += 1
            
            logger.info(f"Обработка завершена. Успешно: {success_count}, Ошибок: {error_count}")
            
        except Exception as e:
            logger.error(f"Ошибка при получении постов для обработки: {e}")
    
    async def get_processing_statistics(self):
        """Получает статистику обработки"""
        try:
            # Статистика по постам
            self.db.cursor.execute("SELECT COUNT(*) as total_posts FROM posts WHERE content IS NOT NULL")
            posts_stats = self.db.cursor.fetchone()
            
            # Статистика по саммари
            self.db.cursor.execute("SELECT COUNT(*) as total_summaries FROM post_summaries")
            summaries_stats = self.db.cursor.fetchone()
            
            # Посты без саммари
            self.db.cursor.execute("""
                SELECT COUNT(*) as posts_without_summaries FROM posts p
                LEFT JOIN post_summaries ps ON p.channel_id = ps.channel_id 
                    AND p.telegram_message_id = ps.telegram_message_id
                WHERE ps.id IS NULL AND p.content IS NOT NULL AND p.content != ''
            """)
            pending_stats = self.db.cursor.fetchone()
            
            logger.info("📊 Статистика обработки саммари:")
            logger.info(f"   Всего постов с контентом: {posts_stats['total_posts']}")
            logger.info(f"   Создано саммари: {summaries_stats['total_summaries']}")
            logger.info(f"   Ожидают обработки: {pending_stats['posts_without_summaries']}")
            
            if posts_stats['total_posts'] > 0:
                completion_rate = (summaries_stats['total_summaries'] / posts_stats['total_posts']) * 100
                logger.info(f"   Процент завершения: {completion_rate:.1f}%")
                
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
    
    async def test_summary_creation(self, test_text: str = None):
        """Тестирует создание саммари"""
        if not test_text:
            test_text = """
            Новая гостиница Marriott открылась в центре Москвы. Отель предлагает 200 номеров различных категорий, 
            включая люксы с видом на Кремль. В отеле работают три ресторана, спа-центр и конференц-залы. 
            Управляющий отелем отметил, что они ожидают высокую загрузку благодаря удачному расположению. 
            Стоимость номеров начинается от 15 000 рублей за ночь. Отель уже принял первых гостей и получил 
            положительные отзывы о качестве сервиса.
            """
        
        logger.info("Тестирование создания саммари...")
        
        try:
            summary_result = None
            if self.eliza_analyzer:
                summary_result = await self.eliza_analyzer.analyze_content(
                    content=test_text,
                    prompt="Создай краткое саммари новости для Яндекс Путешествий"
                )
            
            if (not summary_result or summary_result.get("status") != "success") and self.zeliboba_analyzer:
                summary_result = await self.zeliboba_analyzer.create_summary(test_text)
            
            if summary_result and summary_result.get("status") == "success":
                analysis_text = summary_result.get("analysis_text", "")
                main_idea, summary = self.extract_summary_parts(analysis_text)
                
                logger.info("✅ Тест создания саммари прошел успешно")
                logger.info(f"Главная мысль: {main_idea}")
                logger.info(f"Саммари: {summary}")
                logger.info(f"Длина саммари: {len(summary.split())} слов")
                return True
            else:
                error = summary_result.get("error", "Неизвестная ошибка") if summary_result else "Нет ответа от API"
                logger.error(f"❌ Ошибка тестирования: {error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Исключение при тестировании: {e}")
            return False

async def main():
    parser = argparse.ArgumentParser(description="Обработка постов с созданием саммари")
    parser.add_argument("--process", action="store_true", help="Обработать посты и создать саммари")
    parser.add_argument("--stats", action="store_true", help="Показать статистику обработки")
    parser.add_argument("--test", action="store_true", help="Тестировать создание саммари")
    parser.add_argument("--limit", type=int, help="Ограничить количество постов для обработки")
    
    args = parser.parse_args()
    
    processor = PostSummaryProcessor()
    
    if args.test:
        success = await processor.test_summary_creation()
        if not success:
            sys.exit(1)
    
    if args.stats:
        await processor.get_processing_statistics()
    
    if args.process:
        await processor.process_posts_to_summaries(args.limit)
    
    if not any([args.process, args.stats, args.test]):
        print("Использование:")
        print("  python summary_processor.py --test                    # Тестировать создание саммари")
        print("  python summary_processor.py --process                 # Обработать все посты")
        print("  python summary_processor.py --process --limit 10      # Обработать 10 постов")
        print("  python summary_processor.py --stats                   # Показать статистику")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        processor = loop.run_until_complete(main())
        if hasattr(processor, 'close'):
            loop.run_until_complete(processor.close())
    finally:
        loop.close()
