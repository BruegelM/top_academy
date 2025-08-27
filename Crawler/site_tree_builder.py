from typing import Dict, List, Optional
from dataclasses import dataclass
from .utils.url_normalizer import URLNormalizer
from .exceptions import InvalidURL

@dataclass
class SiteNode:
    """Узел дерева сайта"""
    url: str
    parent: Optional['SiteNode'] = None
    children: List['SiteNode'] = None
    metadata: Dict = None
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    depth: int = 0
    is_external: bool = False
    links_count: int = 0
    images_count: int = 0
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.metadata is None:
            self.metadata = {}
        
        if self.parent:
            self.depth = self.parent.depth + 1

class SiteTree:
    """Дерево структуры сайта"""
    
    def __init__(self, root_url: str):
        self.root = SiteNode(root_url)
        self.nodes: Dict[str, SiteNode] = {root_url: self.root}
        self.domain = URLNormalizer.get_domain(root_url)
        
    def add_node(self, url: str, parent_url: str = None) -> SiteNode:
        """
        Добавляет новый узел в дерево
        
        :param url: URL нового узла
        :param parent_url: URL родительского узла
        :return: Созданный или существующий узел
        """
        if not URLNormalizer.is_valid_url(url):
            raise InvalidURL(f"Invalid URL: {url}")
            
        normalized_url = URLNormalizer.normalize(url)
        
        if normalized_url in self.nodes:
            return self.nodes[normalized_url]
            
        parent = self.nodes.get(parent_url) if parent_url else self.root
        is_external = URLNormalizer.get_domain(url) != self.domain
        
        node = SiteNode(
            url=normalized_url,
            parent=parent,
            is_external=is_external
        )
        
        parent.children.append(node)
        self.nodes[normalized_url] = node
        return node
        
    def find_node(self, url: str) -> Optional[SiteNode]:
        """Находит узел по URL"""
        return self.nodes.get(URLNormalizer.normalize(url))
        
    def update_node(self, url: str, **kwargs):
        """Обновляет данные узла"""
        node = self.find_node(url)
        if node:
            for key, value in kwargs.items():
                setattr(node, key, value)
                
    def get_stats(self) -> Dict:
        """Возвращает статистику по дереву"""
        return {
            'total_nodes': len(self.nodes),
            'external_links': sum(1 for n in self.nodes.values() if n.is_external),
            'max_depth': max(n.depth for n in self.nodes.values()),
            'avg_children': sum(len(n.children) for n in self.nodes.values()) / len(self.nodes)
        }

class SiteTreeBuilder:
    """Класс для построения и обновления дерева сайта"""
    
    def __init__(self):
        self.site_tree: Optional[SiteTree] = None
        
    def initialize_tree(self, root_url: str) -> SiteTree:
        """Инициализирует новое дерево сайта"""
        self.site_tree = SiteTree(root_url)
        return self.site_tree
        
    def add_page(self, url: str, parent_url: str, fetch_result, parse_result) -> SiteNode:
        """
        Добавляет страницу в дерево сайта
        
        :param url: URL страницы
        :param parent_url: URL родительской страницы
        :param fetch_result: Результат загрузки страницы
        :param parse_result: Результат парсинга страницы
        :return: Созданный или обновленный узел
        """
        node = self.site_tree.add_node(url, parent_url)
        
        node.status_code = fetch_result.status_code
        node.content_type = fetch_result.content_type
        
        if parse_result.metadata:
            node.metadata.update({
                'title': parse_result.metadata.title,
                'description': parse_result.metadata.description,
                'keywords': parse_result.metadata.keywords
            })
            
        node.links_count = len(parse_result.links)
        node.images_count = len(parse_result.images)
        
        return node