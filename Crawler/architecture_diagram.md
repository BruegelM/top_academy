# Диаграмма архитектуры веб-краулера

## Общая архитектура системы

```mermaid
graph TB
    subgraph "Web Crawler System"
        CC[Crawler Controller]
        UM[URL Manager]
        WF[Web Fetcher]
        CP[Content Parser]
        STB[Site Tree Builder]
        DS[Data Storage]
        
        CC --> UM
        CC --> WF
        CC --> CP
        CC --> STB
        CC --> DS
        
        UM --> WF
        WF --> CP
        CP --> STB
        CP --> UM
        STB --> DS
    end
    
    subgraph "External Resources"
        WEB[Web Sites]
        ROBOTS[robots.txt]
        SITEMAP[sitemap.xml]
    end
    
    WF --> WEB
    WF --> ROBOTS
    WF --> SITEMAP
    
    subgraph "Output Formats"
        JSON[JSON Tree]
        XML[XML Sitemap]
        HTML[HTML Report]
        CSV[CSV Data]
    end
    
    DS --> JSON
    DS --> XML
    DS --> HTML
    DS --> CSV
```

## Поток данных в системе

```mermaid
sequenceDiagram
    participant CC as Crawler Controller
    participant UM as URL Manager
    participant WF as Web Fetcher
    participant CP as Content Parser
    participant STB as Site Tree Builder
    participant DS as Data Storage

    CC->>UM: Инициализация с root URL
    CC->>WF: Запуск сканирования
    
    loop Основной цикл сканирования
        UM->>WF: Получить следующий URL
        WF->>WF: Загрузить страницу
        WF->>CP: Передать HTML контент
        CP->>CP: Извлечь ссылки и метаданные
        CP->>UM: Добавить новые URL в очередь
        CP->>STB: Создать/обновить узел дерева
        STB->>DS: Сохранить изменения
    end
    
    CC->>DS: Экспорт результатов
```

## Структура классов

```mermaid
classDiagram
    class CrawlerController {
        -config: CrawlerConfig
        -url_manager: URLManager
        -web_fetcher: WebFetcher
        -content_parser: ContentParser
        -tree_builder: SiteTreeBuilder
        -data_storage: DataStorage
        +start_crawling()
        +pause_crawling()
        +resume_crawling()
        +stop_crawling()
        +get_progress()
    }
    
    class URLManager {
        -pending_queue: PriorityQueue
        -processing_set: Set
        -completed_set: Set
        -failed_set: Set
        +add_url(url, priority)
        +get_next_url()
        +mark_completed(url)
        +mark_failed(url)
        +is_visited(url)
    }
    
    class WebFetcher {
        -session: aiohttp.ClientSession
        -rate_limiter: RateLimiter
        -robots_checker: RobotsChecker
        +fetch_page(url)
        +check_robots_txt(url)
        +handle_redirects(response)
    }
    
    class ContentParser {
        -html_parser: BeautifulSoup
        -url_normalizer: URLNormalizer
        +parse_html(content)
        +extract_links(soup)
        +extract_metadata(soup)
        +normalize_urls(links, base_url)
    }
    
    class SiteTreeBuilder {
        -site_tree: SiteTree
        +add_node(url, parent_url)
        +update_node(url, metadata)
        +get_node(url)
        +calculate_depth(url)
    }
    
    class DataStorage {
        -tree_data: SiteTree
        -export_formats: List
        +save_tree(tree)
        +load_tree()
        +export_json()
        +export_xml()
        +export_html()
    }
    
    class SiteNode {
        +url: str
        +parent: SiteNode
        +children: List[SiteNode]
        +metadata: Dict
        +status_code: int
        +depth: int
        +last_crawled: datetime
    }
    
    class SiteTree {
        +root: SiteNode
        +nodes: Dict[str, SiteNode]
        +domain: str
        +add_node(node)
        +find_node(url)
        +get_all_nodes()
    }
    
    CrawlerController --> URLManager
    CrawlerController --> WebFetcher
    CrawlerController --> ContentParser
    CrawlerController --> SiteTreeBuilder
    CrawlerController --> DataStorage
    SiteTreeBuilder --> SiteTree
    SiteTree --> SiteNode
```

## Алгоритм обхода URL

```mermaid
flowchart TD
    START([Начало сканирования]) --> INIT[Инициализация с root URL]
    INIT --> QUEUE{Есть URL в очереди?}
    
    QUEUE -->|Да| GET[Получить следующий URL]
    QUEUE -->|Нет| FINISH([Завершение сканирования])
    
    GET --> CHECK{URL уже посещен?}
    CHECK -->|Да| QUEUE
    CHECK -->|Нет| ROBOTS{Разрешен robots.txt?}
    
    ROBOTS -->|Нет| MARK_SKIP[Пометить как пропущенный]
    ROBOTS -->|Да| FETCH[Загрузить страницу]
    
    MARK_SKIP --> QUEUE
    
    FETCH --> SUCCESS{Успешная загрузка?}
    SUCCESS -->|Нет| ERROR[Обработать ошибку]
    SUCCESS -->|Да| PARSE[Парсить контент]
    
    ERROR --> RETRY{Повторить попытку?}
    RETRY -->|Да| FETCH
    RETRY -->|Нет| MARK_FAIL[Пометить как неудачный]
    
    MARK_FAIL --> QUEUE
    
    PARSE --> EXTRACT[Извлечь ссылки]
    EXTRACT --> FILTER[Фильтровать ссылки]
    FILTER --> ADD[Добавить новые URL в очередь]
    ADD --> UPDATE[Обновить дерево сайта]
    UPDATE --> SAVE[Сохранить изменения]
    SAVE --> QUEUE
```

## Система управления состоянием

```mermaid
stateDiagram-v2
    [*] --> Initialized
    Initialized --> Running: start_crawling()
    Running --> Paused: pause_crawling()
    Paused --> Running: resume_crawling()
    Running --> Completed: все URL обработаны
    Running --> Stopped: stop_crawling()
    Paused --> Stopped: stop_crawling()
    Completed --> [*]
    Stopped --> [*]
    
    state Running {
        [*] --> FetchingURL
        FetchingURL --> ParsingContent: успешная загрузка
        FetchingURL --> HandlingError: ошибка загрузки
        ParsingContent --> UpdatingTree: ссылки извлечены
        UpdatingTree --> FetchingURL: дерево обновлено
        HandlingError --> FetchingURL: ошибка обработана
    }
```

## Архитектура хранения данных

```mermaid
erDiagram
    SITE_TREE {
        string root_url
        string domain
        datetime created_at
        datetime updated_at
        int total_nodes
        int max_depth
    }
    
    SITE_NODE {
        string url PK
        string parent_url FK
        int depth
        int status_code
        string content_type
        datetime last_crawled
        boolean is_external
        text title
        text description
        json metadata
    }
    
    URL_QUEUE {
        string url PK
        int priority
        string status
        datetime added_at
        int retry_count
        datetime next_retry
    }
    
    CRAWL_LOG {
        int id PK
        string url FK
        datetime timestamp
        string action
        string status
        text error_message
        float response_time
    }
    
    SITE_TREE ||--o{ SITE_NODE : contains
    SITE_NODE ||--o{ SITE_NODE : parent_child
    URL_QUEUE ||--o{ CRAWL_LOG : logs
    SITE_NODE ||--o{ CRAWL_LOG : logs