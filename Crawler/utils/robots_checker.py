from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import asyncio
import aiohttp
from typing import Dict, Optional
from ..exceptions import RobotsTxtDisallowed

class RobotsChecker:
    """
    Класс для проверки разрешений в robots.txt
    Реализует кэширование и асинхронную загрузку robots.txt
    """

    def __init__(self):
        self.robots_cache: Dict[str, RobotFileParser] = {}
        self.lock = asyncio.Lock()

    async def can_fetch(self, url: str, user_agent: str) -> bool:
        """
        Проверяет, разрешено ли сканирование URL согласно robots.txt
        
        :param url: URL для проверки
        :param user_agent: User-Agent строкa
        :return: True если доступ разрешен, False если запрещен
        """
        domain = urlparse(url).netloc
        if not domain:
            return False

        async with self.lock:
            if domain not in self.robots_cache:
                await self._load_robots_txt(domain, url, user_agent)

            rp = self.robots_cache.get(domain)
            return rp.can_fetch(user_agent, url) if rp else True

    async def _load_robots_txt(self, domain: str, base_url: str, user_agent: str) -> None:
        """
        Асинхронно загружает и парсит robots.txt для указанного домена
        
        :param domain: Домен для загрузки robots.txt
        :param base_url: Базовый URL для построения пути к robots.txt
        :param user_agent: User-Agent строка для запроса
        """
        robots_url = f"{urlparse(base_url).scheme}://{domain}/robots.txt"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(robots_url, headers={'User-Agent': user_agent}) as response:
                    if response.status == 200:
                        content = await response.text()
                        rp = RobotFileParser()
                        rp.parse(content.splitlines())
                        self.robots_cache[domain] = rp
                    else:
                        self.robots_cache[domain] = None
        except Exception:
            self.robots_cache[domain] = None

    def clear_cache(self) -> None:
        """Очищает кэш robots.txt"""
        self.robots_cache.clear()