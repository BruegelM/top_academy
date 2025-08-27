from urllib.parse import urlparse, urljoin, urlunparse
import re

class URLNormalizer:
    """Класс для нормализации URL-адресов"""
    
    @staticmethod
    def normalize(url: str, base_url: str = None) -> str:
        """
        Нормализует URL:
        - Преобразует относительные URL в абсолютные
        - Удаляет фрагменты (#)
        - Нормализует параметры запроса
        - Стандартизирует схему и домен
        
        :param url: URL для нормализации
        :param base_url: Базовый URL для относительных ссылок
        :return: Нормализованный URL
        """
        if not url:
            raise ValueError("URL cannot be empty")
            
        # Если URL относительный и указан base_url
        if base_url and not url.startswith(('http://', 'https://')):
            url = urljoin(base_url, url)
            
        # Парсинг URL
        parsed = urlparse(url)
        
        # Удаление фрагмента
        parsed = parsed._replace(fragment='')
        
        # Нормализация схемы (http -> https)
        if parsed.scheme == 'http':
            parsed = parsed._replace(scheme='https')
            
        # Нормализация пути (удаление дублирующихся слэшей)
        path = re.sub(r'/{2,}', '/', parsed.path)
        parsed = parsed._replace(path=path)
        
        # Удаление стандартных портов
        if parsed.port:
            if (parsed.scheme == 'http' and parsed.port == 80) or \
               (parsed.scheme == 'https' and parsed.port == 443):
                parsed = parsed._replace(netloc=parsed.hostname)
                
        return urlunparse(parsed)

    @staticmethod
    def get_domain(url: str) -> str:
        """Извлекает домен из URL"""
        parsed = urlparse(url)
        return parsed.netloc.lower()
        
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Проверяет валидность URL"""
        try:
            parsed = urlparse(url)
            return all([parsed.scheme in ['http', 'https'], parsed.netloc])
        except:
            return False