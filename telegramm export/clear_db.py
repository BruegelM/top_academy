import psycopg2
from psycopg2.extras import RealDictCursor
from config import DATABASE_CONFIG
import logging

logger = logging.getLogger(__name__)

def clear_all_tables():
    """Очистка всех таблиц в базе данных"""
    connection = None
    try:
        connection = psycopg2.connect(**DATABASE_CONFIG)
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SET CONSTRAINTS ALL DEFERRED")
        tables = [
            'zeliboba_analysis',
            'reactions', 
            'post_summaries',
            'posts',
            'channels'
        ]
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
            logger.info(f"Таблица {table} очищена")
        connection.commit()
        print('✅ Все таблицы базы данных очищены')
        return True
    except psycopg2.Error as e:
        logger.error(f"Ошибка очистки таблиц: {e}")
        if connection:
            connection.rollback()
        return False
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    clear_all_tables()