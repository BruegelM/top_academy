import asyncio
import re
import logging
from dataclasses import dataclass
from typing import Dict, Optional, List
from .url_manager import URLManager
from .web_fetcher import WebFetcher
from .content_parser import ContentParser
from .site_tree_builder import SiteTree, SiteTreeBuilder
from .data_storage import DataStorage, ExportFormat
from .exceptions import (MaxPagesExceeded, InvalidURL,
                        FetchError, ParseError, StorageError)
from .utils.url_normalizer import URLNormalizer

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CrawlerConfig:
    """Конфигурация веб-краулера"""
    max_depth: int = 10
    max_pages: int = 1000
    concurrent_requests: int = 10
    request_delay: float = 1.0
    timeout: int = 30
    user_agent: str = "WebCrawler/1.0"
    respect_robots_txt: bool = True
    follow_redirects: bool = True
    max_redirects: int = 5
    allowed_domains: List[str] = None
    excluded_patterns: List[str] = None

class CrawlerController:
    """Основной контроллер веб-краулера"""
    
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.url_manager = URLManager(max_pages=config.max_pages)
        self.web_fetcher: Optional[WebFetcher] = None
        self.content_parser = ContentParser()
        self.tree_builder = SiteTreeBuilder()
        self.data_storage = DataStorage()
        self.site_tree: Optional[SiteTree] = None
        self.is_running = False
        self.crawl_id: Optional[int] = None
        
    async def start_crawling(self, root_url: str) -> SiteTree:
        """
        Запускает процесс сканирования сайта
        
        :param root_url: Начальный URL для сканирования
        :return: Дерево сайта с результатами сканирования
        """
        if self.is_running:
            raise RuntimeError("Crawler is already running")
            
        self.is_running = True
        self.site_tree = self.tree_builder.initialize_tree(root_url)
        self.crawl_id = self.data_storage._create_crawl(URLNormalizer.get_domain(root_url))
        
        try:
            async with WebFetcher({
                'request_delay': self.config.request_delay,
                'timeout': self.config.timeout,
                'user_agent': self.config.user_agent,
                'respect_robots_txt': self.config.respect_robots_txt,
                'follow_redirects': self.config.follow_redirects
            }) as self.web_fetcher:
                # Добавляем начальный URL в очередь
                await self.url_manager.add_url(root_url, depth=0)
                
                # Запускаем worker'ы для параллельной обработки
                workers = [
                    self._worker() 
                    for _ in range(self.config.concurrent_requests)
                ]
                await asyncio.gather(*workers)
                
        finally:
            self.is_running = False
            if self.site_tree:
                self.data_storage.save_tree(self.site_tree, self.crawl_id)
                self.data_storage.complete_crawl(
                    self.crawl_id, 
                    len(self.site_tree.nodes)
                )
                
        return self.site_tree
        
    async def _worker(self):
        """Worker для обработки URL из очереди"""
        worker_id = id(asyncio.current_task())
        logger.info(f"Worker {worker_id} запущен")
        
        while self.is_running:
            try:
                url_info = await self.url_manager.get_next_url()
                if not url_info:
                    # Проверяем, есть ли еще URL в обработке
                    if not self.url_manager.processing:
                        logger.info(f"Worker {worker_id}: нет URL для обработки, завершаем")
                        break
                    await asyncio.sleep(0.1)
                    continue
                    
                logger.info(f"Worker {worker_id} обрабатывает: {url_info.url}")
                
                try:
                    # Загружаем страницу
                    fetch_result = await self.web_fetcher.fetch_page(url_info.url)
                    logger.info(f"Страница загружена: {url_info.url}, статус: {fetch_result.status_code}")
                    
                    # Парсим контент, если это HTML
                    if fetch_result.content_type and 'text/html' in fetch_result.content_type:
                        logger.info(f"Парсим HTML контент: {url_info.url}")
                        parse_result = self.content_parser.parse_html(
                            fetch_result.content,
                            url_info.url
                        )
                        
                        logger.info(f"Найдено {len(parse_result.links)} ссылок на {url_info.url}")
                        
                        # Добавляем страницу в дерево
                        node = self.tree_builder.add_page(
                            url_info.url,
                            url_info.parent_url,
                            fetch_result,
                            parse_result
                        )
                        
                        logger.info(f"Страница добавлена в дерево: {url_info.url}")
                        
                        # Добавляем найденные ссылки в очередь
                        new_links_count = 0
                        for link in parse_result.links:
                            if self._should_follow_url(link.url, url_info.depth + 1):
                                await self.url_manager.add_url(
                                    link.url,
                                    depth=url_info.depth + 1,
                                    parent_url=url_info.url
                                )
                                new_links_count += 1
                        
                        logger.info(f"Добавлено {new_links_count} новых ссылок в очередь")
                    else:
                        logger.info(f"Пропускаем не-HTML контент: {url_info.url}")
                                
                    await self.url_manager.mark_completed(url_info.url)
                    logger.info(f"URL помечен как завершенный: {url_info.url}")
                    
                except FetchError as e:
                    logger.error(f"Ошибка загрузки {url_info.url}: {e}")
                    await self.url_manager.mark_failed(url_info.url, str(e))
                except ParseError as e:
                    logger.error(f"Ошибка парсинга {url_info.url}: {e}")
                    await self.url_manager.mark_failed(url_info.url, str(e))
                except Exception as e:
                    logger.error(f"Неожиданная ошибка для {url_info.url}: {e}")
                    await self.url_manager.mark_failed(url_info.url, f"Unexpected error: {e}")
                    
            except MaxPagesExceeded:
                logger.info(f"Worker {worker_id}: достигнут лимит страниц")
                self.is_running = False
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                continue
                
        logger.info(f"Worker {worker_id} завершен")
                
    def _should_follow_url(self, url: str, depth: int) -> bool:
        """Проверяет, нужно ли сканировать URL"""
        # Проверка максимальной глубины
        if depth > self.config.max_depth:
            return False
            
        # Проверка разрешенных доменов
        domain = URLNormalizer.get_domain(url)
        if (self.config.allowed_domains and 
            domain not in self.config.allowed_domains):
            return False
            
        # Проверка исключенных паттернов
        if self.config.excluded_patterns:
            for pattern in self.config.excluded_patterns:
                if re.search(pattern, url):
                    return False
                    
        return True
        
    async def export_results(self, format: ExportFormat, output_path: str):
        """
        Экспортирует результаты сканирования
        
        :param format: Формат экспорта
        :param output_path: Путь для сохранения
        """
        if not self.site_tree:
            raise StorageError("No site tree to export")
            
        self.data_storage.export_tree(self.site_tree, format, output_path)