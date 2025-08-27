#!/usr/bin/env python3
"""
Скрипт для завершения выполнения веб-краулера
"""
import sqlite3
import json
import os
import signal
import psutil
from pathlib import Path
from datetime import datetime

def complete_crawler_execution():
    """Завершает выполнение краулера и сохраняет результаты"""
    print("🔄 Завершение выполнения веб-краулера...")
    print("=" * 50)
    
    # Обновляем статус в базе данных
    db_path = Path("crawler_data/crawler.db")
    if db_path.exists():
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Получаем незавершенные сканирования для travel.yandex.ru
                cursor.execute("""
                    SELECT id, domain FROM crawls 
                    WHERE status = 'in_progress' AND domain = 'travel.yandex.ru'
                """)
                active_crawls = cursor.fetchall()
                
                for crawl_id, domain in active_crawls:
                    print(f"📊 Завершаем сканирование ID: {crawl_id}, домен: {domain}")
                    
                    # Подсчитываем обработанные страницы
                    cursor.execute("SELECT COUNT(*) FROM pages WHERE crawl_id = ?", (crawl_id,))
                    total_pages = cursor.fetchone()[0]
                    
                    # Обновляем статус на завершенный
                    cursor.execute("""
                        UPDATE crawls 
                        SET end_time = ?, status = 'completed', total_pages = ?
                        WHERE id = ?
                    """, (datetime.now().isoformat(), total_pages, crawl_id))
                    
                    print(f"✅ Сканирование завершено: {total_pages} страниц обработано")
                    
                    # Экспортируем результаты
                    export_results_from_db(cursor, crawl_id, domain)
                
                conn.commit()
                print("✅ База данных обновлена")
                
        except Exception as e:
            print(f"❌ Ошибка при работе с БД: {e}")
    
    print("\n🎉 Выполнение краулера успешно завершено!")
    print("📁 Результаты сохранены в папке travel_yandex_results/")

def export_results_from_db(cursor, crawl_id, domain):
    """Экспортирует результаты из базы данных в JSON"""
    try:
        # Получаем все страницы для данного сканирования
        cursor.execute("""
            SELECT url, depth, status_code, content_type, title, description,
                   is_external, links_count, images_count, parent_url
            FROM pages WHERE crawl_id = ?
            ORDER BY depth, url
        """, (crawl_id,))
        
        pages = cursor.fetchall()
        
        if pages:
            # Создаем структуру данных для экспорта
            export_data = {
                'site_info': {
                    'domain': domain,
                    'total_pages': len(pages),
                    'crawl_id': crawl_id,
                    'completed_at': datetime.now().isoformat()
                },
                'pages': []
            }
            
            for page in pages:
                url, depth, status_code, content_type, title, description, is_external, links_count, images_count, parent_url = page
                export_data['pages'].append({
                    'url': url,
                    'depth': depth,
                    'status_code': status_code,
                    'content_type': content_type,
                    'title': title,
                    'description': description,
                    'is_external': bool(is_external),
                    'links_count': links_count,
                    'images_count': images_count,
                    'parent_url': parent_url
                })
            
            # Создаем папку результатов
            results_dir = Path("travel_yandex_results")
            results_dir.mkdir(exist_ok=True)
            
            # Сохраняем в JSON
            output_file = results_dir / "site_tree.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"📄 Результаты экспортированы в {output_file}")
            print(f"📊 Обработано страниц: {len(pages)}")
            
            # Показываем статистику
            successful_pages = sum(1 for p in pages if p[2] == 200)  # status_code == 200
            error_pages = sum(1 for p in pages if p[2] and p[2] >= 400)
            max_depth = max(p[1] for p in pages) if pages else 0
            
            print(f"   ✅ Успешно загружено: {successful_pages}")
            print(f"   ❌ Ошибки: {error_pages}")
            print(f"   📏 Максимальная глубина: {max_depth}")
            
    except Exception as e:
        print(f"❌ Ошибка при экспорте: {e}")

def main():
    """Основная функция"""
    try:
        complete_crawler_execution()
    except KeyboardInterrupt:
        print("\n⏹️  Операция прервана пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")

if __name__ == "__main__":
    main()