import asyncio
import time
from typing import Dict
from collections import defaultdict

class RateLimiter:
    """
    Класс для ограничения скорости HTTP-запросов к доменам.
    Реализует механизм rate limiting с возможностью настройки задержки.
    """
    
    def __init__(self, delay: float = 1.0):
        """
        Инициализация RateLimiter
        
        :param delay: Минимальная задержка между запросами к одному домену (в секундах)
        """
        self.delay = delay
        self.domain_timers: Dict[str, float] = defaultdict(float)
        self.lock = asyncio.Lock()

    async def wait_if_needed(self, domain: str) -> None:
        """
        Асинхронно ожидает, если необходимо, чтобы соблюсти rate limiting
        
        :param domain: Домен, к которому планируется запрос
        """
        async with self.lock:
            last_request = self.domain_timers.get(domain, 0)
            elapsed = time.time() - last_request
            wait_time = max(0, self.delay - elapsed)
            
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                
            self.domain_timers[domain] = time.time()

    def update_delay(self, new_delay: float) -> None:
        """
        Обновляет задержку между запросами
        
        :param new_delay: Новая задержка в секундах
        """
        self.delay = new_delay

    def get_last_request_time(self, domain: str) -> float:
        """
        Возвращает время последнего запроса к указанному домену
        
        :param domain: Домен для проверки
        :return: Время последнего запроса (timestamp)
        """
        return self.domain_timers.get(domain, 0)

    def clear(self) -> None:
        """Очищает историю запросов"""
        self.domain_timers.clear()