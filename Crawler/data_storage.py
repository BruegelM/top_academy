import sqlite3
import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum
from .site_tree_builder import SiteTree, SiteNode
from .exceptions import StorageError

class ExportFormat(Enum):
    """Форматы экспорта данных"""
    JSON = 'json'
    XML = 'xml'
    HTML = 'html'
    CSV = 'csv'
    GRAPHML = 'graphml'

class DataStorage:
    """Класс для хранения и экспорта данных сканирования"""
    
    def __init__(self, storage_path: str = "crawler_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.storage_path / "crawler.db"
        self._init_database()
        
    def _init_database(self):
        """Инициализирует таблицы в базе данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Таблица для информации о сканировании
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS crawls (
                    id INTEGER PRIMARY KEY,
                    domain TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    total_pages INTEGER,
                    status TEXT,
                    config TEXT
                )
            """)
            
            # Таблица для страниц
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pages (
                    id INTEGER PRIMARY KEY,
                    crawl_id INTEGER,
                    url TEXT NOT NULL,
                    parent_url TEXT,
                    depth INTEGER,
                    status_code INTEGER,
                    content_type TEXT,
                    title TEXT,
                    description TEXT,
                    is_external INTEGER,
                    links_count INTEGER,
                    images_count INTEGER,
                    FOREIGN KEY (crawl_id) REFERENCES crawls (id)
                )
            """)
            
            # Индексы для ускорения запросов
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pages_url ON pages(url)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pages_crawl_id ON pages(crawl_id)")
            conn.commit()
            
    def save_tree(self, site_tree: SiteTree, crawl_id: int = None) -> int:
        """
        Сохраняет дерево сайта в базу данных
        
        :param site_tree: Дерево сайта для сохранения
        :param crawl_id: ID сканирования (None для создания нового)
        :return: ID сохраненного сканирования
        """
        if crawl_id is None:
            crawl_id = self._create_crawl(site_tree.domain)
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Удаляем старые данные для этого crawl_id
            cursor.execute("DELETE FROM pages WHERE crawl_id = ?", (crawl_id,))
            
            # Сохраняем все страницы
            for node in site_tree.nodes.values():
                cursor.execute("""
                    INSERT INTO pages (
                        crawl_id, url, parent_url, depth, status_code, content_type,
                        title, description, is_external, links_count, images_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    crawl_id, node.url, node.parent.url if node.parent else None,
                    node.depth, node.status_code, node.content_type,
                    node.metadata.get('title'), node.metadata.get('description'),
                    int(node.is_external), node.links_count, node.images_count
                ))
                
            conn.commit()
            
        return crawl_id
        
    def _create_crawl(self, domain: str) -> int:
        """Создает новую запись о сканировании"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO crawls (domain, start_time, status)
                VALUES (?, ?, ?)
            """, (domain, datetime.now().isoformat(), 'in_progress'))
            conn.commit()
            return cursor.lastrowid
            
    def complete_crawl(self, crawl_id: int, total_pages: int):
        """Помечает сканирование как завершенное"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE crawls 
                SET end_time = ?, status = 'completed', total_pages = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), total_pages, crawl_id))
            conn.commit()
            
    def export_tree(self, site_tree: SiteTree, format: ExportFormat, output_path: str):
        """
        Экспортирует дерево сайта в указанном формате
        
        :param site_tree: Дерево сайта для экспорта
        :param format: Формат экспорта (из enum ExportFormat)
        :param output_path: Путь для сохранения файла
        """
        output_path = Path(output_path)
        
        if format == ExportFormat.JSON:
            self._export_json(site_tree, output_path)
        elif format == ExportFormat.XML:
            self._export_xml(site_tree, output_path)
        elif format == ExportFormat.HTML:
            self._export_html(site_tree, output_path)
        elif format == ExportFormat.CSV:
            self._export_csv(site_tree, output_path)
        elif format == ExportFormat.GRAPHML:
            self._export_graphml(site_tree, output_path)
        else:
            raise StorageError(f"Unsupported export format: {format}")
            
    def _export_json(self, site_tree: SiteTree, output_path: Path):
        """Экспорт в JSON формат"""
        tree_data = {
            'site_info': {
                'domain': site_tree.domain,
                'total_pages': len(site_tree.nodes),
                'max_depth': max(n.depth for n in site_tree.nodes.values()),
                'created_at': datetime.now().isoformat()
            },
            'pages': [
                self._node_to_dict(node) 
                for node in site_tree.nodes.values()
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(tree_data, f, indent=2, ensure_ascii=False)
            
    def _node_to_dict(self, node: SiteNode) -> Dict:
        """Преобразует узел в словарь для экспорта"""
        return {
            'url': node.url,
            'depth': node.depth,
            'status_code': node.status_code,
            'content_type': node.content_type,
            'title': node.metadata.get('title'),
            'description': node.metadata.get('description'),
            'is_external': node.is_external,
            'links_count': node.links_count,
            'images_count': node.images_count,
            'parent_url': node.parent.url if node.parent else None
        }
        
    def _export_xml(self, site_tree: SiteTree, output_path: Path):
        """Экспорт в XML Sitemap формат"""
        xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        
        for node in site_tree.nodes.values():
            if not node.is_external and node.status_code == 200:
                xml_content.append('<url>')
                xml_content.append(f'<loc>{node.url}</loc>')
                if node.metadata.get('title'):
                    xml_content.append(f'<title>{node.metadata["title"]}</title>')
                xml_content.append(f'<depth>{node.depth}</depth>')
                xml_content.append('</url>')
                
        xml_content.append('</urlset>')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(xml_content))
            
    def _export_html(self, site_tree: SiteTree, output_path: Path):
        """Экспорт в HTML отчет"""
        html_content = [
            '<!DOCTYPE html>',
            '<html><head>',
            '<title>Site Tree Report</title>',
            '<style>',
            'body { font-family: Arial, sans-serif; margin: 20px; }',
            'h1 { color: #333; }',
            'ul { list-style-type: none; padding-left: 20px; }',
            'li { margin: 5px 0; }',
            '.external { color: #666; }',
            '.error { color: red; }',
            '</style>',
            '</head><body>',
            f'<h1>Site Tree: {site_tree.domain}</h1>',
            f'<p>Total pages: {len(site_tree.nodes)}</p>',
            '<ul>'
        ]
        
        def build_tree(node: SiteNode, level: int):
            indent = '&nbsp;' * 4 * level
            cls = 'external' if node.is_external else ''
            cls += ' error' if node.status_code and node.status_code >= 400 else ''
            
            html_content.append(
                f'<li>{indent}<a href="{node.url}" class="{cls}">'
                f'{node.metadata.get("title", node.url)}</a>'
                f'<span> (status: {node.status_code}, depth: {node.depth})</span></li>'
            )
            
            for child in sorted(node.children, key=lambda n: n.url):
                build_tree(child, level + 1)
                
        build_tree(site_tree.root, 0)
        html_content.append('</ul></body></html>')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_content))
            
    def _export_csv(self, site_tree: SiteTree, output_path: Path):
        """Экспорт в CSV формат"""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'URL', 'Depth', 'Status Code', 'Content Type', 'Title',
                'Description', 'Is External', 'Links Count', 'Images Count', 'Parent URL'
            ])
            
            for node in site_tree.nodes.values():
                writer.writerow([
                    node.url, node.depth, node.status_code, node.content_type,
                    node.metadata.get('title', ''), node.metadata.get('description', ''),
                    node.is_external, node.links_count, node.images_count,
                    node.parent.url if node.parent else ''
                ])
                
    def _export_graphml(self, site_tree: SiteTree, output_path: Path):
        """Экспорт в GraphML формат для визуализации графа"""
        graphml_content = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<graphml xmlns="http://graphml.graphdrawing.org/xmlns"',
            '         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
            '         xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns',
            '         http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">',
            '  <key id="url" for="node" attr.name="url" attr.type="string"/>',
            '  <key id="title" for="node" attr.name="title" attr.type="string"/>',
            '  <key id="depth" for="node" attr.name="depth" attr.type="int"/>',
            '  <key id="status" for="node" attr.name="status_code" attr.type="int"/>',
            '  <graph id="SiteTree" edgedefault="directed">'
        ]
        
        # Добавляем узлы
        for i, node in enumerate(site_tree.nodes.values()):
            graphml_content.extend([
                f'    <node id="n{i}">',
                f'      <data key="url">{node.url}</data>',
                f'      <data key="title">{node.metadata.get("title", "")}</data>',
                f'      <data key="depth">{node.depth}</data>',
                f'      <data key="status">{node.status_code or 0}</data>',
                '    </node>'
            ])
            
        # Добавляем рёбра
        node_to_id = {node.url: i for i, node in enumerate(site_tree.nodes.values())}
        edge_id = 0
        for node in site_tree.nodes.values():
            if node.parent:
                parent_id = node_to_id[node.parent.url]
                child_id = node_to_id[node.url]
                graphml_content.append(f'    <edge id="e{edge_id}" source="n{parent_id}" target="n{child_id}"/>')
                edge_id += 1
                
        graphml_content.extend([
            '  </graph>',
            '</graphml>'
        ])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(graphml_content))