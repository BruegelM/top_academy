#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тестовый скрипт для проверки новой системы определения важности новостей
"""

import asyncio
import logging
import sys
import os

# Добавляем текущую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from config import ZELIBOBA_ANALYSIS_PROMPT

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_importance_calculation():
    """Тестирование расчета важности постов"""
    
    db = DatabaseManager()
    if not db.connect():
        logger.error("Не удалось подключиться к базе данных")
        return
    
    try:
        logger.info("🧪 Тестирование новой системы определения важности")
        logger.info("=" * 60)
        
        # Показываем новый промпт
        logger.info("📝 Новый промпт для Zeliboba:")
        logger.info(f"   {ZELIBOBA_ANALYSIS_PROMPT[:200]}...")
        logger.info("=" * 60)
        
        # Получаем топ важных постов с новой системой
        logger.info("🔍 Получение топ-10 важных постов с комплексной оценкой...")
        important_posts = db.get_top_important_posts_for_publication(limit=10)
        
        if not important_posts:
            logger.warning("Нет постов для анализа важности")
            return
        
        logger.info(f"📊 Найдено {len(important_posts)} постов для анализа")
        logger.info("=" * 60)
        
        # Показываем детальную информацию по каждому посту
        for i, post in enumerate(important_posts, 1):
            details = post.get('importance_details', {})
            
            logger.info(f"🏆 ПОСТ #{i} - Важность: {post['importance_score']}/10")
            logger.info(f"   📺 Канал: {post['channel_title']}")
            logger.info(f"   📅 Дата: {post['date_published']}")
            logger.info(f"   📝 Заголовок: {post['content'][:100]}...")
            
            logger.info("   📈 Детали расчета важности:")
            logger.info(f"      🤖 AI оценка: {details.get('ai_importance', 'N/A')}/10")
            logger.info(f"      💬 Вовлеченность: {details.get('engagement_score', 'N/A')}")
            logger.info(f"      🏨 Отношение к отелям: {details.get('hotel_relation_score', 'N/A')}")
            logger.info(f"      🏭 Влияние на индустрию: {details.get('industry_impact_score', 'N/A')}")
            logger.info(f"      😊 Тональность: {details.get('sentiment_score', 'N/A')}")
            
            logger.info("   📊 Метрики поста:")
            logger.info(f"      👍 Позитивные реакции: {details.get('positive_reactions', 0)}")
            logger.info(f"      🔄 Репосты: {details.get('forwards', 0)}")
            logger.info(f"      💬 Комментарии: {details.get('replies', 0)}")
            logger.info(f"      👀 Просмотры: {details.get('views', 0)}")
            logger.info("-" * 60)
        
        # Статистика по факторам важности
        logger.info("📈 СТАТИСТИКА ПО ФАКТОРАМ ВАЖНОСТИ:")
        
        ai_scores = [p.get('importance_details', {}).get('ai_importance', 0) for p in important_posts]
        engagement_scores = [p.get('importance_details', {}).get('engagement_score', 0) for p in important_posts]
        hotel_scores = [p.get('importance_details', {}).get('hotel_relation_score', 0) for p in important_posts]
        
        if ai_scores:
            logger.info(f"   🤖 Средняя AI оценка: {sum(ai_scores)/len(ai_scores):.2f}")
        if engagement_scores:
            logger.info(f"   💬 Средняя вовлеченность: {sum(engagement_scores)/len(engagement_scores):.2f}")
        if hotel_scores:
            logger.info(f"   🏨 Постов с отношением к отелям: {sum(1 for s in hotel_scores if s > 0)}")
        
        logger.info("=" * 60)
        logger.info("✅ Тестирование завершено успешно!")
        
    except Exception as e:
        logger.error(f"Ошибка при тестировании: {e}")
    finally:
        db.disconnect()

def show_importance_formula():
    """Показать формулу расчета важности"""
    logger.info("🧮 ФОРМУЛА РАСЧЕТА ВАЖНОСТИ НОВОСТЕЙ:")
    logger.info("=" * 60)
    logger.info("📊 Факторы и их веса:")
    logger.info("   🤖 AI оценка (1-10): 40% веса")
    logger.info("   💬 Вовлеченность: 20% веса")
    logger.info("      - Позитивные реакции × 0.3")
    logger.info("      - Репосты × 0.4 (самый важный)")
    logger.info("      - Комментарии × 0.2")
    logger.info("      - Просмотры ÷ 1000 × 0.1")
    logger.info("   🏨 Отношение к отелям: 18% веса")
    logger.info("      - Прямое: 3 балла")
    logger.info("      - Косвенное: 1 балл")
    logger.info("      - Отсутствует: 0 баллов")
    logger.info("   🏭 Влияние на индустрию: 15% веса")
    logger.info("      - Высокое: 3 балла")
    logger.info("      - Среднее: 2 балла")
    logger.info("      - Низкое: 1 балл")
    logger.info("   😊 Тональность: 7% веса")
    logger.info("      - Позитивная: +1 балл")
    logger.info("      - Негативная: -0.5 балла")
    logger.info("      - Нейтральная: 0 баллов")
    logger.info("=" * 60)

if __name__ == "__main__":
    print("🧪 Тестирование новой системы определения важности новостей")
    print("=" * 60)
    
    show_importance_formula()
    test_importance_calculation()