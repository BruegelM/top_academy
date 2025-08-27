from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Optional
from urllib.parse import urlparse
from .utils.url_normalizer import URLNormalizer
from .exceptions import ParseError

class LinkInfo:
    """Информация о найденной ссылке"""
    
    def __init__(self, url: str, link_type: str):
        self.url = url
        self.link_type = link_type  # 'navigation', 'resource', 'form', 'frame'
        self.anchor_text: Optional[str] = None
        self.rel: Optional[str] = None
        self.title: Optional[str] = None

class PageMetadata:
    """Метаданные страницы"""
    
    def __init__(self):
        self.title: Optional[str] = None
        self.description: Optional[str] = None
        self.keywords: Optional[str] = None
        self.language: Optional[str] = None
        self.robots: Optional[str] = None
        self.canonical_url: Optional[str] = None

class ParseResult:
    """Результат парсинга страницы"""
    
    def __init__(self):
        self.links: List[LinkInfo] = []
        self.metadata = PageMetadata()
        self.images: List[str] = []
        self.scripts: List[str] = []
        self.stylesheets: List[str] = []

class ContentParser:
    """Класс для парсинга HTML контента и извлечения ссылок"""
    
    def __init__(self):
        self.url_normalizer = URLNormalizer()
        
    def parse_html(self, content: str, base_url: str) -> ParseResult:
        """
        Парсит HTML и извлекает ссылки и метаданные
        
        :param content: HTML контент страницы
        :param base_url: Базовый URL для нормализации ссылок
        :return: Объект ParseResult с результатами
        """
        result = ParseResult()
        
        try:
            soup = BeautifulSoup(content, 'lxml')
            
            # Извлечение метаданных
            self._extract_metadata(soup, result.metadata)
            
            # Извлечение ссылок
            result.links = self._extract_links(soup, base_url)
            
            # Извлечение ресурсов
            result.images, result.scripts, result.stylesheets = self._extract_resources(soup, base_url)
            
        except Exception as e:
            raise ParseError(f"Ошибка парсинга HTML: {e}") from e
            
        return result
        
    def _extract_metadata(self, soup: BeautifulSoup, metadata: PageMetadata) -> None:
        """Извлекает метаданные страницы"""
        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata.title = title_tag.text.strip()
            
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            content = meta.get('content', '')
            
            if name == 'description':
                metadata.description = content
            elif name == 'keywords':
                metadata.keywords = content
            elif name == 'robots':
                metadata.robots = content
            elif meta.get('http-equiv', '').lower() == 'content-language':
                metadata.language = content
                
        # Canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            metadata.canonical_url = self.url_normalizer.normalize(canonical['href'])
            
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[LinkInfo]:
        """Извлекает все ссылки из HTML"""
        links = []
        
        # Навигационные ссылки (тег <a>)
        for a in soup.find_all('a', href=True):
            if not a['href'].strip() or a['href'].startswith(('javascript:', 'mailto:', 'tel:')):
                continue
                
            link = LinkInfo(
                url=self.url_normalizer.normalize(a['href'], base_url),
                link_type='navigation'
            )
            link.anchor_text = a.text.strip()
            link.title = a.get('title')
            link.rel = a.get('rel')
            links.append(link)
            
        # Формы (тег <form>)
        for form in soup.find_all('form', action=True):
            if form['action'].strip():
                link = LinkInfo(
                    url=self.url_normalizer.normalize(form['action'], base_url),
                    link_type='form'
                )
                links.append(link)
                
        # Фреймы (теги <frame>, <iframe>)
        for frame in soup.find_all(['frame', 'iframe'], src=True):
            if frame['src'].strip():
                link = LinkInfo(
                    url=self.url_normalizer.normalize(frame['src'], base_url),
                    link_type='frame'
                )
                links.append(link)
                
        return links
        
    def _extract_resources(self, soup: BeautifulSoup, base_url: str) -> Tuple[List[str], List[str], List[str]]:
        """Извлекает ссылки на ресурсы (изображения, скрипты, стили)"""
        images = []
        scripts = []
        stylesheets = []
        
        # Изображения
        for img in soup.find_all('img', src=True):
            if img['src'].strip():
                images.append(self.url_normalizer.normalize(img['src'], base_url))
                
        # Скрипты
        for script in soup.find_all('script', src=True):
            if script['src'].strip():
                scripts.append(self.url_normalizer.normalize(script['src'], base_url))
                
        # Стили
        for link in soup.find_all('link', href=True):
            if link['href'].strip():
                rel = link.get('rel', [])
                if 'stylesheet' in rel:
                    stylesheets.append(self.url_normalizer.normalize(link['href'], base_url))
                    
        return images, scripts, stylesheets