#!/usr/bin/env python3
import asyncio
import logging
from Crawler.crawler_controller import CrawlerController, CrawlerConfig

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler_test.log'),
        logging.StreamHandler()
    ]
)

async def test_crawler():
    """Тестирует краулер на простом сайте"""
    
    config = CrawlerConfig(
        max_depth=1,
        max_pages=5,
        concurrent_requests=2,
        request_delay=1.0,
        timeout=10,
        user_agent="TestCrawler/1.0",
        respect_robots_txt=True
    )
    
    controller = CrawlerController(config)
    
    # Тестируем только на travel.yandex.ru
    test_url = "https://travel.yandex.ru"
    
    print(f"🕷️ Тестируем краулер на {test_url}")
    print("📋 Параметры:")
    print(f"   - Глубина: {config.max_depth}")
    print(f"   - Макс. страниц: {config.max_pages}")
    print(f"   - Задержка: {config.request_delay}s")
    print(f"   - Таймаут: {config.timeout}s")
    print()
    
    try:
        site_tree = await controller.start_crawling(test_url)
        
        print("✅ Сканирование завершено!")
        stats = site_tree.get_stats()
        print(f"📊 Статистика:")
        print(f"   - Всего узлов: {stats['total_nodes']}")
        print(f"   - Внешние ссылки: {stats['external_links']}")
        print(f"   - Максимальная глубина: {stats['max_depth']}")
        
        # Показываем найденные страницы
        print(f"\n📄 Найденные страницы:")
        for url, node in site_tree.nodes.items():
            title = node.metadata.get('title', 'Без заголовка')[:50]
            print(f"   [{node.status_code}] {url} - {title}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        logging.error(f"Ошибка тестирования: {e}")

if __name__ == "__main__":
    asyncio.run(test_crawler())