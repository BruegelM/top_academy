# Техническая спецификация веб-краулера

## Обзор системы

Веб-краулер представляет собой асинхронное приложение на Python, предназначенное для систематического обхода веб-сайтов и построения их иерархической структуры в виде дерева.

## Технологический стек

### Основные библиотеки:
- **aiohttp** - асинхронные HTTP запросы
- **asyncio** - асинхронное программирование
- **BeautifulSoup4** - парсинг HTML
- **urllib.robotparser** - обработка robots.txt
- **sqlite3** - локальное хранение данных
- **pydantic** - валидация данных
- **click** - CLI интерфейс

### Дополнительные зависимости:
- **aiofiles** - асинхронная работа с файлами
- **yarl** - работа с URL
- **lxml** - быстрый XML/HTML парсер
- **tqdm** - индикатор прогресса
- **loguru** - продвинутое логирование

## Детальная спецификация компонентов

### 1. CrawlerController

**Файл:** `crawler_controller.py`

```python
class CrawlerConfig(BaseModel):
    """Конфигурация краулера"""
    max_depth: int = 10
    max_pages: int = 1000
    concurrent_requests: int = 10
    request_delay: float = 1.0
    timeout: int = 30
    user_agent: str = "WebCrawler/1.0"
    respect_robots_txt: bool = True
    follow_redirects: bool = True
    max_redirects: int = 5
    allowed_domains: List[str] = []
    excluded_patterns: List[str] = []

class CrawlerController:
    """Главный контроллер краулера"""
    
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.url_manager = URLManager()
        self.web_fetcher = WebFetcher(config)
        self.content_parser = ContentParser()
        self.tree_builder = SiteTreeBuilder()
        self.data_storage = DataStorage()
        self.is_running = False
        self.stats = CrawlStats()
    
    async def start_crawling(self, root_url: str) -> SiteTree:
        """Запуск процесса сканирования"""
        
    async def pause_crawling(self):
        """Приостановка сканирования"""
        
    async def resume_crawling(self):
        """Возобновление сканирования"""
        
    async def stop_crawling(self):
        """Остановка сканирования"""
```

### 2. URLManager

**Файл:** `url_manager.py`

```python
class URLPriority(IntEnum):
    """Приоритеты URL"""
    HIGH = 1    # Главная страница, sitemap
    MEDIUM = 2  # Страницы верхнего уровня
    LOW = 3     # Глубоко вложенные страницы

class URLStatus(Enum):
    """Статусы URL"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class URLInfo(BaseModel):
    """Информация об URL"""
    url: str
    priority: URLPriority
    depth: int
    parent_url: Optional[str] = None
    added_at: datetime
    retry_count: int = 0
    last_error: Optional[str] = None

class URLManager:
    """Менеджер URL для управления очередью сканирования"""
    
    def __init__(self):
        self.pending_queue = asyncio.PriorityQueue()
        self.processing_set = set()
        self.completed_set = set()
        self.failed_set = set()
        self.url_info = {}
        self.lock = asyncio.Lock()
    
    async def add_url(self, url: str, priority: URLPriority, 
                     depth: int, parent_url: str = None):
        """Добавление URL в очередь"""
        
    async def get_next_url(self) -> Optional[URLInfo]:
        """Получение следующего URL для обработки"""
        
    async def mark_completed(self, url: str):
        """Пометка URL как завершенного"""
        
    async def mark_failed(self, url: str, error: str):
        """Пометка URL как неудачного"""
        
    def is_visited(self, url: str) -> bool:
        """Проверка, был ли URL уже посещен"""
        
    def get_stats(self) -> Dict[str, int]:
        """Получение статистики обработки URL"""
```

### 3. WebFetcher

**Файл:** `web_fetcher.py`

```python
class FetchResult(BaseModel):
    """Результат загрузки страницы"""
    url: str
    status_code: int
    content: Optional[str] = None
    content_type: Optional[str] = None
    headers: Dict[str, str] = {}
    response_time: float = 0.0
    error: Optional[str] = None
    redirected_from: Optional[str] = None

class RateLimiter:
    """Ограничитель скорости запросов"""
    
    def __init__(self, delay: float):
        self.delay = delay
        self.last_request = {}
    
    async def wait_if_needed(self, domain: str):
        """Ожидание перед запросом если необходимо"""

class RobotsChecker:
    """Проверка robots.txt"""
    
    def __init__(self):
        self.robots_cache = {}
    
    async def can_fetch(self, url: str, user_agent: str) -> bool:
        """Проверка разрешения на загрузку URL"""

class WebFetcher:
    """Загрузчик веб-страниц"""
    
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.session = None
        self.rate_limiter = RateLimiter(config.request_delay)
        self.robots_checker = RobotsChecker()
    
    async def __aenter__(self):
        """Инициализация HTTP сессии"""
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие HTTP сессии"""
        
    async def fetch_page(self, url: str) -> FetchResult:
        """Загрузка страницы"""
        
    async def _make_request(self, url: str) -> aiohttp.ClientResponse:
        """Выполнение HTTP запроса"""
        
    def _extract_content_type(self, response: aiohttp.ClientResponse) -> str:
        """Извлечение типа контента"""
```

### 4. ContentParser

**Файл:** `content_parser.py`

```python
class LinkInfo(BaseModel):
    """Информация о ссылке"""
    url: str
    link_type: str  # 'navigation', 'resource', 'form', 'frame'
    anchor_text: Optional[str] = None
    title: Optional[str] = None
    rel: Optional[str] = None

class PageMetadata(BaseModel):
    """Метаданные страницы"""
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None
    canonical_url: Optional[str] = None
    language: Optional[str] = None
    robots: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None

class ParseResult(BaseModel):
    """Результат парсинга страницы"""
    links: List[LinkInfo] = []
    metadata: PageMetadata = PageMetadata()
    images: List[str] = []
    scripts: List[str] = []
    stylesheets: List[str] = []

class URLNormalizer:
    """Нормализатор URL"""
    
    @staticmethod
    def normalize(url: str, base_url: str) -> str:
        """Нормализация URL"""
        
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Проверка валидности URL"""
        
    @staticmethod
    def get_domain(url: str) -> str:
        """Извлечение домена из URL"""

class ContentParser:
    """Парсер HTML контента"""
    
    def __init__(self):
        self.url_normalizer = URLNormalizer()
    
    def parse_html(self, content: str, base_url: str) -> ParseResult:
        """Парсинг HTML контента"""
        
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[LinkInfo]:
        """Извлечение всех ссылок"""
        
    def _extract_metadata(self, soup: BeautifulSoup) -> PageMetadata:
        """Извлечение метаданных страницы"""
        
    def _extract_resources(self, soup: BeautifulSoup, base_url: str) -> Tuple[List[str], List[str], List[str]]:
        """Извлечение ресурсов (изображения, скрипты, стили)"""
```

### 5. SiteTreeBuilder

**Файл:** `site_tree_builder.py`

```python
class SiteNode:
    """Узел дерева сайта"""
    
    def __init__(self, url: str, parent: Optional['SiteNode'] = None):
        self.url = url
        self.parent = parent
        self.children: List['SiteNode'] = []
        self.metadata: PageMetadata = PageMetadata()
        self.status_code: Optional[int] = None
        self.content_type: Optional[str] = None
        self.last_crawled: Optional[datetime] = None
        self.depth = 0 if parent is None else parent.depth + 1
        self.is_external = False
        self.response_time: float = 0.0
        self.links_count = 0
        self.images_count = 0
    
    def add_child(self, child: 'SiteNode'):
        """Добавление дочернего узла"""
        
    def remove_child(self, child: 'SiteNode'):
        """Удаление дочернего узла"""
        
    def get_path(self) -> List[str]:
        """Получение пути от корня до узла"""
        
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование узла в словарь"""

class SiteTree:
    """Дерево структуры сайта"""
    
    def __init__(self, root_url: str):
        self.root = SiteNode(root_url)
        self.nodes: Dict[str, SiteNode] = {root_url: self.root}
        self.domain = URLNormalizer.get_domain(root_url)
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_node(self, url: str, parent_url: str = None) -> SiteNode:
        """Добавление узла в дерево"""
        
    def find_node(self, url: str) -> Optional[SiteNode]:
        """Поиск узла по URL"""
        
    def update_node(self, url: str, **kwargs):
        """Обновление данных узла"""
        
    def get_all_nodes(self) -> List[SiteNode]:
        """Получение всех узлов дерева"""
        
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики дерева"""
        
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование дерева в словарь"""

class SiteTreeBuilder:
    """Построитель дерева сайта"""
    
    def __init__(self):
        self.site_tree: Optional[SiteTree] = None
    
    def initialize_tree(self, root_url: str) -> SiteTree:
        """Инициализация дерева"""
        
    def add_page(self, url: str, parent_url: str, 
                fetch_result: FetchResult, 
                parse_result: ParseResult) -> SiteNode:
        """Добавление страницы в дерево"""
        
    def update_page(self, url: str, **kwargs):
        """Обновление данных страницы"""
        
    def get_tree(self) -> Optional[SiteTree]:
        """Получение дерева сайта"""
```

### 6. DataStorage

**Файл:** `data_storage.py`

```python
class ExportFormat(Enum):
    """Форматы экспорта"""
    JSON = "json"
    XML = "xml"
    HTML = "html"
    CSV = "csv"
    GRAPHML = "graphml"

class DataStorage:
    """Система хранения данных"""
    
    def __init__(self, storage_path: str = "crawler_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.db_path = self.storage_path / "crawler.db"
        self._init_database()
    
    def _init_database(self):
        """Инициализация базы данных"""
        
    async def save_tree(self, site_tree: SiteTree):
        """Сохранение дерева в базу данных"""
        
    async def load_tree(self, domain: str) -> Optional[SiteTree]:
        """Загрузка дерева из базы данных"""
        
    async def export_tree(self, site_tree: SiteTree, 
                         format: ExportFormat, 
                         output_path: str):
        """Экспорт дерева в указанном формате"""
        
    def _export_json(self, site_tree: SiteTree, output_path: str):
        """Экспорт в JSON формат"""
        
    def _export_xml(self, site_tree: SiteTree, output_path: str):
        """Экспорт в XML Sitemap формат"""
        
    def _export_html(self, site_tree: SiteTree, output_path: str):
        """Экспорт в HTML отчет"""
        
    def _export_csv(self, site_tree: SiteTree, output_path: str):
        """Экспорт в CSV формат"""
        
    def _export_graphml(self, site_tree: SiteTree, output_path: str):
        """Экспорт в GraphML формат для визуализации"""
```

## CLI интерфейс

**Файл:** `cli.py`

```python
@click.group()
def cli():
    """Web Crawler CLI"""
    pass

@cli.command()
@click.argument('url')
@click.option('--max-depth', default=10, help='Максимальная глубина сканирования')
@click.option('--max-pages', default=1000, help='Максимальное количество страниц')
@click.option('--output', default='output', help='Папка для сохранения результатов')
@click.option('--format', 'export_format', 
              type=click.Choice(['json', 'xml', 'html', 'csv', 'all']),
              default='json', help='Формат экспорта')
@click.option('--concurrent', default=10, help='Количество одновременных запросов')
@click.option('--delay', default=1.0, help='Задержка между запросами (сек)')
def crawl(url, max_depth, max_pages, output, export_format, concurrent, delay):
    """Запуск сканирования сайта"""
    
@cli.command()
@click.argument('domain')
@click.option('--format', 'export_format',
              type=click.Choice(['json', 'xml', 'html', 'csv']),
              default='json', help='Формат экспорта')
@click.option('--output', help='Путь к файлу результата')
def export(domain, export_format, output):
    """Экспорт ранее сканированного сайта"""
    
@cli.command()
def list_sites():
    """Список сканированных сайтов"""
    
@cli.command()
@click.argument('domain')
def stats(domain):
    """Статистика по сканированному сайту"""
```

## Конфигурационный файл

**Файл:** `config.yaml`

```yaml
crawler:
  max_depth: 10
  max_pages: 1000
  concurrent_requests: 10
  request_delay: 1.0
  timeout: 30
  user_agent: "WebCrawler/1.0"
  respect_robots_txt: true
  follow_redirects: true
  max_redirects: 5

filters:
  allowed_domains: []
  excluded_patterns:
    - ".*\\.pdf$"
    - ".*\\.jpg$"
    - ".*\\.png$"
    - ".*\\.gif$"
    - ".*\\.zip$"
    - "/admin/.*"
    - "/private/.*"

storage:
  database_path: "crawler_data/crawler.db"
  export_path: "exports"

logging:
  level: "INFO"
  file: "crawler.log"
  max_size: "10MB"
  backup_count: 5
```

## Требования к производительности

### Масштабируемость:
- Поддержка сканирования сайтов до 100,000 страниц
- Обработка до 50 одновременных запросов
- Использование памяти не более 1GB для больших сайтов

### Надежность:
- Автоматическое восстановление после сбоев
- Сохранение прогресса каждые 100 обработанных страниц
- Retry механизм для неудачных запросов

### Безопасность:
- Соблюдение robots.txt
- Ограничение скорости запросов
- Обработка HTTP заголовков безопасности
- Валидация всех входных данных

## Тестирование

### Unit тесты:
- Тестирование каждого компонента отдельно
- Мокирование HTTP запросов
- Тестирование граничных случаев

### Integration тесты:
- Тестирование взаимодействия компонентов
- Тестирование с реальными веб-сайтами
- Тестирование производительности

### End-to-end тесты:
- Полный цикл сканирования
- Тестирование различных форматов экспорта
- Тестирование CLI интерфейса