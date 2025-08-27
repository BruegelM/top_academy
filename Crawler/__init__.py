# Make Crawler a proper Python package
from .exceptions import (
    CrawlerException,
    MaxDepthExceeded,
    MaxPagesExceeded,
    RobotsTxtDisallowed,
    InvalidURL,
    FetchError,
    ParseError,
    StorageError
)

__all__ = [
    'CrawlerController',
    'URLManager',
    'WebFetcher',
    'ContentParser',
    'SiteTreeBuilder',
    'DataStorage',
    'exceptions'
]