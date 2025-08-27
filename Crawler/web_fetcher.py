import aiohttp
import asyncio
import logging
from typing import Dict, Optional
from urllib.parse import urlparse
from .exceptions import FetchError, RobotsTxtDisallowed
from .utils import RateLimiter, RobotsChecker

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FetchResult:
    """Результат загрузки веб-страницы"""
    
    def __init__(self, url: str):
        self.url = url
        self.status_code: Optional[int] = None
        self.content: Optional[str] = None
        self.content_type: Optional[str] = None
        self.headers: Dict[str, str] = {}
        self.error: Optional[str] = None
        self.redirected_from: Optional[str] = None
        self.response_time: float = 0.0

class WebFetcher:
    """Класс для асинхронной загрузки веб-страниц"""
    
    def __init__(self, config):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiter = RateLimiter(config.get('request_delay', 1.0))
        self.robots_checker = RobotsChecker()
        
    async def __aenter__(self):
        """Инициализация HTTP-сессии"""
        timeout = aiohttp.ClientTimeout(total=self.config.get('timeout', 30))
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={'User-Agent': self.config.get('user_agent')}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие HTTP-сессии"""
        if self.session:
            await self.session.close()
            
    async def fetch_page(self, url: str) -> FetchResult:
        """
        Загружает веб-страницу и возвращает результат
        
        :param url: URL для загрузки
        :return: Объект FetchResult с результатами
        """
        result = FetchResult(url)
        logger.info(f"Начинаем загрузку: {url}")
        
        if not urlparse(url).scheme:
            url = 'https://' + url
            logger.info(f"Добавлена схема https: {url}")
            
        # Проверка robots.txt
        if self.config.get('respect_robots_txt', True):
            logger.info(f"Проверяем robots.txt для {url}")
            can_fetch = await self.robots_checker.can_fetch(url, self.config.get('user_agent'))
            if not can_fetch:
                logger.warning(f"URL {url} запрещен в robots.txt")
                raise RobotsTxtDisallowed(f"URL {url} запрещен в robots.txt")
            logger.info(f"robots.txt разрешает сканирование {url}")
                
        try:
            # Ожидание соблюдения rate limit
            domain = urlparse(url).netloc
            logger.info(f"Применяем rate limiting для домена {domain}")
            await self.rate_limiter.wait_if_needed(domain)
            
            start_time = asyncio.get_event_loop().time()
            logger.info(f"Отправляем HTTP запрос к {url}")
            
            async with self.session.get(url, allow_redirects=self.config.get('follow_redirects', True)) as response:
                result.status_code = response.status
                result.content_type = response.headers.get('Content-Type')
                result.headers = dict(response.headers)
                
                logger.info(f"Получен ответ {response.status} для {url}, Content-Type: {result.content_type}")
                
                if response.history:
                    result.redirected_from = str(response.history[0].url)
                    logger.info(f"Редирект с {result.redirected_from} на {url}")
                    
                # Загружаем только текстовый контент
                if 'text/html' in (result.content_type or ''):
                    result.content = await response.text()
                    logger.info(f"Загружен HTML контент для {url}, размер: {len(result.content)} символов")
                else:
                    result.content = None
                    logger.info(f"Пропускаем не-HTML контент для {url}")
                    
            result.response_time = asyncio.get_event_loop().time() - start_time
            logger.info(f"Загрузка {url} завершена за {result.response_time:.2f} сек")
            
        except Exception as e:
            result.error = str(e)
            logger.error(f"Ошибка при загрузке {url}: {e}")
            raise FetchError(f"Ошибка при загрузке {url}: {e}") from e
            
        return result