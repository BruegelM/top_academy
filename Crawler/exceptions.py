class CrawlerException(Exception):
    """Базовое исключение краулера"""
    pass

class MaxDepthExceeded(CrawlerException):
    """Превышена максимальная глубина сканирования"""
    pass

class MaxPagesExceeded(CrawlerException):
    """Превышено максимальное количество страниц"""
    pass

class RobotsTxtDisallowed(CrawlerException):
    """Доступ запрещен robots.txt"""
    pass

class InvalidURL(CrawlerException):
    """Недопустимый URL"""
    pass

class FetchError(CrawlerException):
    """Ошибка загрузки страницы"""
    pass

class ParseError(CrawlerException):
    """Ошибка парсинга контента"""
    pass

class StorageError(CrawlerException):
    """Ошибка хранилища данных"""
    pass