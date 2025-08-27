#!/usr/bin/env python3
"""
Скрипт для мониторинга выполнения веб-краулера
"""
import os
import time
import json
from pathlib import Path
import sqlite3

def check_crawler_status():
    """Проверяет статус выполнения краулера"""
    print("🔍 Проверка статуса веб-краулера...")
    print("=" * 50)
    
    # Проверяем наличие результатов
    results_dir = Path("travel_yandex_results")
    if results_dir.exists():
        print(f"✅ Папка результатов найдена: {results_dir}")
        files = list(results_dir.glob("*"))
        if files:
            print(f"📁 Найдено файлов: {len(files)}")
            for file in files:
                size = file.stat().st_size
                print(f"   - {file.name}: {size} байт")
        else:
            print("📁 Папка результатов пуста")
    else:
        print("❌ Папка результатов не найдена")
    
    # Проверяем базу данных
    db_path = Path("crawler_data/crawler.db")
    if db_path.exists():
        print(f"\n✅ База данных найдена: {db_path}")
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Получаем информацию о сканированиях
                cursor.execute("SELECT * FROM crawls ORDER BY id DESC LIMIT 5")
                crawls = cursor.fetchall()
                
                if crawls:
                    print("\n📊 Последние сканирования:")
                    for crawl in crawls:
                        crawl_id, domain, start_time, end_time, total_pages, status, config = crawl
                        print(f"   ID: {crawl_id}, Домен: {domain}")
                        print(f"   Статус: {status}, Страниц: {total_pages or 'N/A'}")
                        print(f"   Начало: {start_time}")
                        print(f"   Конец: {end_time or 'В процессе'}")
                        print()
                        
                        # Получаем статистику по страницам для последнего сканирования
                        if crawl == crawls[0]:  # Последнее сканирование
                            cursor.execute("""
                                SELECT 
                                    COUNT(*) as total,
                                    COUNT(CASE WHEN status_code = 200 THEN 1 END) as success,
                                    COUNT(CASE WHEN status_code >= 400 THEN 1 END) as errors,
                                    MAX(depth) as max_depth
                                FROM pages WHERE crawl_id = ?
                            """, (crawl_id,))
                            stats = cursor.fetchone()
                            if stats and stats[0] > 0:
                                total, success, errors, max_depth = stats
                                print(f"   📈 Статистика страниц:")
                                print(f"      Всего: {total}")
                                print(f"      Успешно: {success}")
                                print(f"      Ошибки: {errors}")
                                print(f"      Макс. глубина: {max_depth}")
                else:
                    print("\n📊 Сканирования не найдены")
                    
        except Exception as e:
            print(f"❌ Ошибка при чтении БД: {e}")
    else:
        print("\n❌ База данных не найдена")
    
    # Проверяем лог файлы
    log_files = [
        "crawler_test.log",
        "crawler.log"
    ]
    
    print("\n📋 Лог файлы:")
    for log_file in log_files:
        log_path = Path(log_file)
        if log_path.exists():
            size = log_path.stat().st_size
            print(f"   ✅ {log_file}: {size} байт")
            
            # Показываем последние строки
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"      Последние записи:")
                        for line in lines[-3:]:
                            print(f"      {line.strip()}")
            except Exception as e:
                print(f"      Ошибка чтения: {e}")
        else:
            print(f"   ❌ {log_file}: не найден")

def main():
    """Основная функция"""
    try:
        check_crawler_status()
        
        print("\n" + "=" * 50)
        print("🔄 Мониторинг завершен")
        
    except KeyboardInterrupt:
        print("\n⏹️  Мониторинг прерван пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")

if __name__ == "__main__":
    main()