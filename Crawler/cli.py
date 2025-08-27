import click
import asyncio
from pathlib import Path
from typing import Optional
from .crawler_controller import CrawlerController, CrawlerConfig
from .data_storage import ExportFormat

@click.group()
def cli():
    pass

@cli.command()
@click.argument('url')
@click.option('--max-depth', default=5, help='Максимальная глубина сканирования')
@click.option('--max-pages', default=1000, help='Максимальное количество страниц')
@click.option('--concurrent', default=10, help='Количество одновременных запросов')
@click.option('--delay', default=1.0, help='Задержка между запросами (секунды)')
@click.option('--user-agent', default='WebCrawler/1.0', help='User-Agent строка')
@click.option('--no-robots', is_flag=True, help='Игнорировать robots.txt')
@click.option('--output', default='output', help='Директория для сохранения результатов')
@click.option('--format', 'export_format', 
              type=click.Choice(['json', 'xml', 'html', 'all']),
              default='json', help='Формат экспорта')
def crawl(url, max_depth, max_pages, concurrent, delay, user_agent, no_robots, output, export_format):
    """Запускает сканирование сайта"""
    config = CrawlerConfig(
        max_depth=max_depth,
        max_pages=max_pages,
        concurrent_requests=concurrent,
        request_delay=delay,
        user_agent=user_agent,
        respect_robots_txt=not no_robots
    )
    
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    async def run_crawler():
        controller = CrawlerController(config)
        site_tree = await controller.start_crawling(url)
        
        if export_format == 'all':
            for fmt in ExportFormat:
                await controller.export_results(
                    fmt,
                    str(output_path / f'site_tree.{fmt.value}')
                )
        else:
            await controller.export_results(
                ExportFormat(export_format),
                str(output_path / f'site_tree.{export_format}')
            )
            
    asyncio.run(run_crawler())

@cli.command()
@click.argument('domain')
@click.option('--format', 'export_format',
              type=click.Choice(['json', 'xml', 'html']),
              default='json', help='Формат экспорта')
@click.option('--output', help='Путь для сохранения файла')
def export(domain, export_format, output):
    """Экспортирует результаты предыдущего сканирования"""
    if not output:
        output = f"{domain}_tree.{export_format}"
        
    async def run_export():
        controller = CrawlerController(CrawlerConfig())
        await controller.export_results(
            ExportFormat(export_format),
            output
        )
        
    asyncio.run(run_export())

@cli.command()
def list_sites():
    """Показывает список сканированных сайтов"""
    # TODO: Реализовать вывод списка сканированных сайтов из БД
    click.echo("Список сканированных сайтов будет здесь")

@cli.command()
@click.argument('domain')
def stats(domain):
    """Показывает статистику по сканированному сайту"""
    # TODO: Реализовать вывод статистики
    click.echo(f"Статистика для {domain} будет здесь")

if __name__ == '__main__':
    cli()