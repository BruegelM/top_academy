# Руководство по развертыванию веб-краулера

## Системные требования

### Минимальные требования:
- **ОС:** Linux (Ubuntu 20.04+), macOS 10.15+, Windows 10+
- **Python:** 3.8+
- **RAM:** 2GB свободной памяти
- **Диск:** 1GB свободного места
- **Сеть:** Стабильное интернет-соединение

### Рекомендуемые требования:
- **ОС:** Linux (Ubuntu 22.04 LTS)
- **Python:** 3.11+
- **RAM:** 8GB+ для больших сайтов
- **Диск:** 10GB+ SSD для базы данных
- **CPU:** 4+ ядра для параллельной обработки
- **Сеть:** 100+ Mbps

## Установка и настройка

### 1. Установка через pip (рекомендуемый способ)

```bash
# Создание виртуального окружения
python -m venv crawler_env
source crawler_env/bin/activate  # Linux/Mac
# или
crawler_env\Scripts\activate     # Windows

# Установка пакета
pip install web-site-crawler

# Проверка установки
crawler --version
```

### 2. Установка из исходного кода

```bash
# Клонирование репозитория
git clone https://github.com/your-org/web-site-crawler.git
cd web-site-crawler

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Установка в режиме разработки
pip install -e .
```

### 3. Docker установка

```bash
# Сборка образа
docker build -t web-crawler .

# Запуск контейнера
docker run -v $(pwd)/data:/app/data web-crawler crawl https://example.com
```

## Конфигурация

### Основной конфигурационный файл

**Файл:** `~/.crawler/config.yaml`

```yaml
# Основные настройки краулера
crawler:
  max_depth: 10                    # Максимальная глубина сканирования
  max_pages: 1000                  # Максимальное количество страниц
  concurrent_requests: 10          # Одновременные запросы
  request_delay: 1.0              # Задержка между запросами (сек)
  timeout: 30                     # Таймаут запроса (сек)
  user_agent: "WebCrawler/1.0"    # User-Agent строка
  respect_robots_txt: true        # Соблюдать robots.txt
  follow_redirects: true          # Следовать редиректам
  max_redirects: 5                # Максимум редиректов

# Фильтры URL
filters:
  allowed_domains: []             # Разрешенные домены (пусто = все)
  excluded_patterns:              # Исключаемые паттерны
    - ".*\\.pdf$"
    - ".*\\.(jpg|png|gif|svg)$"
    - ".*\\.(zip|rar|tar|gz)$"
    - "/admin/.*"
    - "/private/.*"
    - ".*\\?.*download.*"

# Настройки хранения
storage:
  database_path: "~/.crawler/data/crawler.db"
  export_path: "~/.crawler/exports"
  cache_size: 1000                # Размер кэша в памяти
  backup_interval: 100            # Интервал резервного копирования

# Логирование
logging:
  level: "INFO"                   # DEBUG, INFO, WARNING, ERROR
  file: "~/.crawler/logs/crawler.log"
  max_size: "10MB"
  backup_count: 5
  console_output: true

# Производительность
performance:
  connection_pool_size: 100       # Размер пула соединений
  dns_cache_ttl: 300             # TTL DNS кэша (сек)
  keep_alive_timeout: 30         # Keep-alive таймаут
  memory_limit: "1GB"            # Лимит использования памяти
```

### Переменные окружения

```bash
# Основные настройки
export CRAWLER_CONFIG_PATH="/path/to/config.yaml"
export CRAWLER_DATA_DIR="/path/to/data"
export CRAWLER_LOG_LEVEL="INFO"

# Производительность
export CRAWLER_MAX_WORKERS=10
export CRAWLER_MEMORY_LIMIT="2GB"

# Безопасность
export CRAWLER_USER_AGENT="MyBot/1.0"
export CRAWLER_RATE_LIMIT=1.0
```

## Примеры использования

### 1. Базовое сканирование

```bash
# Простое сканирование сайта
crawler crawl https://example.com

# С ограничением глубины
crawler crawl https://example.com --max-depth 5

# С ограничением количества страниц
crawler crawl https://example.com --max-pages 500

# С настройкой параллельности
crawler crawl https://example.com --concurrent 20 --delay 0.5
```

### 2. Расширенные опции

```bash
# Сканирование с экспортом в разные форматы
crawler crawl https://example.com --format json,xml,html

# Сканирование с фильтрацией
crawler crawl https://example.com --exclude-pattern ".*\\.pdf$"

# Возобновление прерванного сканирования
crawler resume https://example.com

# Экспорт ранее сканированного сайта
crawler export example.com --format html --output site_map.html
```

### 3. Программное использование

```python
import asyncio
from web_crawler import CrawlerController, CrawlerConfig

async def main():
    # Создание конфигурации
    config = CrawlerConfig(
        max_depth=5,
        max_pages=1000,
        concurrent_requests=10,
        request_delay=1.0
    )
    
    # Инициализация краулера
    controller = CrawlerController(config)
    
    # Запуск сканирования
    site_tree = await controller.start_crawling("https://example.com")
    
    # Получение статистики
    stats = site_tree.get_stats()
    print(f"Сканировано страниц: {stats['total_pages']}")
    print(f"Максимальная глубина: {stats['max_depth']}")
    
    # Экспорт результатов
    await controller.data_storage.export_tree(
        site_tree, 
        format="json", 
        output_path="site_tree.json"
    )

if __name__ == "__main__":
    asyncio.run(main())
```

## Docker развертывание

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов проекта
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

# Создание директорий для данных
RUN mkdir -p /app/data /app/logs /app/exports

# Настройка пользователя
RUN useradd -m -u 1000 crawler && \
    chown -R crawler:crawler /app
USER crawler

# Переменные окружения
ENV CRAWLER_DATA_DIR=/app/data
ENV CRAWLER_LOG_LEVEL=INFO

# Точка входа
ENTRYPOINT ["crawler"]
CMD ["--help"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  web-crawler:
    build: .
    container_name: web-crawler
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./exports:/app/exports
      - ./config:/app/config
    environment:
      - CRAWLER_CONFIG_PATH=/app/config/config.yaml
      - CRAWLER_LOG_LEVEL=INFO
    restart: unless-stopped
    
  # Опциональный мониторинг
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana

volumes:
  grafana-storage:
```

## Мониторинг и логирование

### 1. Структура логов

```
~/.crawler/logs/
├── crawler.log              # Основной лог
├── crawler.log.1            # Ротированные логи
├── errors.log               # Только ошибки
└── performance.log          # Метрики производительности
```

### 2. Формат логов

```
2024-01-15 10:30:45 | INFO     | crawler.controller | Starting crawl for https://example.com
2024-01-15 10:30:46 | DEBUG    | crawler.fetcher    | Fetching: https://example.com/page1
2024-01-15 10:30:47 | WARNING  | crawler.parser     | Invalid link found: javascript:void(0)
2024-01-15 10:30:48 | ERROR    | crawler.fetcher    | HTTP 404 for https://example.com/missing
```

### 3. Метрики для мониторинга

```python
# Основные метрики
- pages_crawled_total          # Общее количество страниц
- pages_per_second            # Скорость сканирования
- http_requests_total         # Общее количество запросов
- http_request_duration       # Время ответа
- memory_usage_bytes          # Использование памяти
- queue_size                  # Размер очереди URL
- errors_total                # Количество ошибок
```

### 4. Настройка Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'web-crawler'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

## Производительность и оптимизация

### 1. Настройка производительности

```yaml
# Для небольших сайтов (< 1000 страниц)
crawler:
  concurrent_requests: 5
  request_delay: 2.0
  memory_limit: "512MB"

# Для средних сайтов (1000-10000 страниц)
crawler:
  concurrent_requests: 15
  request_delay: 1.0
  memory_limit: "2GB"

# Для больших сайтов (> 10000 страниц)
crawler:
  concurrent_requests: 25
  request_delay: 0.5
  memory_limit: "4GB"
```

### 2. Оптимизация базы данных

```sql
-- Индексы для ускорения запросов
CREATE INDEX idx_site_node_url ON site_node(url);
CREATE INDEX idx_site_node_parent ON site_node(parent_url);
CREATE INDEX idx_site_node_depth ON site_node(depth);
CREATE INDEX idx_url_queue_priority ON url_queue(priority, added_at);

-- Настройки SQLite для производительности
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = MEMORY;
```

### 3. Мониторинг ресурсов

```bash
# Мониторинг использования памяти
watch -n 1 'ps aux | grep crawler'

# Мониторинг сетевой активности
netstat -i

# Мониторинг дискового пространства
df -h ~/.crawler/

# Мониторинг производительности
htop
```

## Безопасность

### 1. Рекомендации по безопасности

- **Соблюдение robots.txt:** Всегда включено по умолчанию
- **Rate limiting:** Настройте разумные задержки между запросами
- **User-Agent:** Используйте идентифицирующий User-Agent
- **Таймауты:** Установите разумные таймауты для предотвращения зависания
- **Фильтрация:** Исключите приватные и административные разделы

### 2. Этические принципы

```yaml
# Рекомендуемые настройки для этичного сканирования
crawler:
  request_delay: 1.0              # Минимум 1 секунда между запросами
  concurrent_requests: 5          # Не более 5 одновременных запросов
  respect_robots_txt: true        # Обязательно соблюдать robots.txt
  user_agent: "YourBot/1.0 (+http://yoursite.com/bot)"

filters:
  excluded_patterns:
    - "/admin/.*"                 # Административные разделы
    - "/private/.*"               # Приватные разделы
    - "/user/.*"                  # Пользовательские данные
    - ".*login.*"                 # Страницы входа
    - ".*register.*"              # Страницы регистрации
```

## Устранение неполадок

### Частые проблемы и решения

#### 1. Высокое потребление памяти
```bash
# Уменьшите размер кэша
export CRAWLER_CACHE_SIZE=500

# Ограничьте количество одновременных запросов
crawler crawl https://example.com --concurrent 5
```

#### 2. Медленная работа
```bash
# Увеличьте параллельность
crawler crawl https://example.com --concurrent 20 --delay 0.5

# Используйте SSD для базы данных
export CRAWLER_DATA_DIR="/path/to/ssd/storage"
```

#### 3. Блокировка сайтом
```bash
# Увеличьте задержки
crawler crawl https://example.com --delay 3.0

# Смените User-Agent
export CRAWLER_USER_AGENT="Mozilla/5.0 (compatible; YourBot/1.0)"
```

#### 4. Ошибки парсинга
```bash
# Включите отладочное логирование
export CRAWLER_LOG_LEVEL=DEBUG

# Проверьте логи
tail -f ~/.crawler/logs/crawler.log
```

### Диагностические команды

```bash
# Проверка конфигурации
crawler config show

# Статистика сканирования
crawler stats example.com

# Проверка состояния базы данных
crawler db check

# Очистка кэша
crawler cache clear

# Экспорт логов для анализа
crawler logs export --format json --output debug.json
```

## Обновление и миграция

### Обновление версии

```bash
# Обновление через pip
pip install --upgrade web-site-crawler

# Проверка версии
crawler --version

# Миграция базы данных (если необходимо)
crawler db migrate
```

### Резервное копирование

```bash
# Создание резервной копии
crawler backup create --output backup_$(date +%Y%m%d).tar.gz

# Восстановление из резервной копии
crawler backup restore backup_20240115.tar.gz
```

## Поддержка и сообщество

### Получение помощи

- **Документация:** https://web-crawler.readthedocs.io/
- **GitHub Issues:** https://github.com/your-org/web-site-crawler/issues
- **Discussions:** https://github.com/your-org/web-site-crawler/discussions
- **Stack Overflow:** Тег `web-site-crawler`

### Вклад в проект

```bash
# Форк репозитория
git clone https://github.com/your-username/web-site-crawler.git

# Создание ветки для фичи
git checkout -b feature/new-feature

# Установка зависимостей для разработки
pip install -r requirements-dev.txt

# Запуск тестов
pytest

# Отправка pull request