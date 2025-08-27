import asyncio
from typing import Dict, Optional, Set
from enum import IntEnum
from dataclasses import dataclass
from urllib.parse import urlparse
from .utils.url_normalizer import URLNormalizer
from .exceptions import InvalidURL, MaxPagesExceeded

class URLPriority(IntEnum):
    """Приоритеты обработки URL"""
    HIGH = 1    # Главная страница, sitemap.xml
    MEDIUM = 2  # Страницы верхнего уровня
    LOW = 3     # Глубоко вложенные страницы

@dataclass
class URLInfo:
    """Информация об URL в очереди"""
    url: str
    priority: URLPriority
    depth: int
    parent_url: Optional[str] = None
    retry_count: int = 0
    last_error: Optional[str] = None

class URLManager:
    """Класс для управления очередью URL и отслеживания состояния"""
    
    def __init__(self, max_pages: int = 1000):
        self.max_pages = max_pages
        self.pending_queue = asyncio.PriorityQueue()
        self.processing: Set[str] = set()
        self.completed: Set[str] = set()
        self.failed: Set[str] = set()
        self.url_info: Dict[str, URLInfo] = {}
        self.lock = asyncio.Lock()
        self.total_processed = 0
        
    async def add_url(self, url: str, depth: int = 0, parent_url: str = None) -> bool:
        """
        Добавляет URL в очередь на обработку
        
        :param url: URL для добавления
        :param depth: Глубина вложенности URL
        :param parent_url: Родительский URL
        :return: True если URL добавлен, False если уже существует
        """
        if not URLNormalizer.is_valid_url(url):
            raise InvalidURL(f"Недопустимый URL: {url}")
            
        normalized_url = URLNormalizer.normalize(url, parent_url)
        
        async with self.lock:
            # Проверка лимита страниц
            if self.total_processed >= self.max_pages:
                raise MaxPagesExceeded(f"Достигнут лимит в {self.max_pages} страниц")
                
            # Проверка, что URL еще не был обработан или не в очереди
            if (normalized_url in self.url_info or 
                normalized_url in self.processing or 
                normalized_url in self.completed or 
                normalized_url in self.failed):
                return False
                
            # Определение приоритета
            priority = URLPriority.HIGH if depth == 0 else (
                URLPriority.MEDIUM if depth < 3 else URLPriority.LOW
            )
            
            # Добавление в очередь
            url_info = URLInfo(
                url=normalized_url,
                priority=priority,
                depth=depth,
                parent_url=parent_url
            )
            
            await self.pending_queue.put((priority.value, normalized_url))
            self.url_info[normalized_url] = url_info
            return True
            
    async def get_next_url(self) -> Optional[URLInfo]:
        """
        Получает следующий URL для обработки
        
        :return: Информация об URL или None если очередь пуста
        """
        async with self.lock:
            if self.pending_queue.empty():
                return None
                
            _, url = await self.pending_queue.get()
            url_info = self.url_info[url]
            self.processing.add(url)
            return url_info
            
    async def mark_completed(self, url: str) -> None:
        """Помечает URL как успешно обработанный"""
        async with self.lock:
            self.processing.discard(url)
            self.completed.add(url)
            self.total_processed += 1
            
    async def mark_failed(self, url: str, error: str) -> None:
        """Помечает URL как обработанный с ошибкой"""
        async with self.lock:
            self.processing.discard(url)
            self.failed.add(url)
            self.total_processed += 1
            
            if url in self.url_info:
                self.url_info[url].last_error = error
                self.url_info[url].retry_count += 1
                
    def get_stats(self) -> Dict[str, int]:
        """Возвращает статистику обработки URL"""
        return {
            'pending': self.pending_queue.qsize(),
            'processing': len(self.processing),
            'completed': len(self.completed),
            'failed': len(self.failed),
            'total_processed': self.total_processed
        }