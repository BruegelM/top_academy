import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from config import DATABASE_CONFIG
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Подключение к базе данных PostgreSQL"""
        try:
            self.connection = psycopg2.connect(**DATABASE_CONFIG)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            logger.info("Успешное подключение к базе данных")
            return True
        except psycopg2.Error as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            return False
    
    def disconnect(self):
        """Отключение от базы данных"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Отключение от базы данных")
    
    def create_tables(self):
        """Создание таблиц в базе данных"""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS channels (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    username TEXT,
                    type TEXT DEFAULT 'channel',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS post_summaries (
                    id SERIAL PRIMARY KEY,
                    channel_id INTEGER NOT NULL,
                    telegram_message_id BIGINT NOT NULL,
                    sender_name TEXT,
                    sender_id BIGINT,
                    summary TEXT NOT NULL,
                    main_idea TEXT NOT NULL,
                    date_published TIMESTAMP NOT NULL,
                    views_count INTEGER DEFAULT 0,
                    forwards_count INTEGER DEFAULT 0,
                    replies_count INTEGER DEFAULT 0,
                    analysis TEXT,
                    importance_score REAL DEFAULT 5.0,
                    channel_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (channel_id) REFERENCES channels (id),
                    UNIQUE(channel_id, telegram_message_id)
                );
            """)
            
            self.cursor.execute("""
                DO $$
                BEGIN
                    BEGIN
                        ALTER TABLE post_summaries ADD COLUMN analysis TEXT;
                    EXCEPTION
                        WHEN duplicate_column THEN NULL;
                    END;
                    
                    BEGIN
                        ALTER TABLE post_summaries ADD COLUMN importance_score REAL DEFAULT 5.0;
                    EXCEPTION
                        WHEN duplicate_column THEN NULL;
                    END;
                    
                    BEGIN
                        ALTER TABLE post_summaries ADD COLUMN channel_name TEXT;
                    EXCEPTION
                        WHEN duplicate_column THEN NULL;
                    END;
                END $$;
            """)
            
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id SERIAL PRIMARY KEY,
                    channel_id INTEGER NOT NULL,
                    telegram_message_id BIGINT NOT NULL,
                    sender_name TEXT,
                    sender_id BIGINT,
                    content TEXT,
                    date_published TIMESTAMP NOT NULL,
                    views_count INTEGER DEFAULT 0,
                    forwards_count INTEGER DEFAULT 0,
                    replies_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (channel_id) REFERENCES channels (id),
                    UNIQUE(channel_id, telegram_message_id)
                );
            """)
            
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS reactions (
                    id SERIAL PRIMARY KEY,
                    post_id INTEGER NOT NULL,
                    reaction_type TEXT NOT NULL,
                    count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (post_id) REFERENCES posts (id),
                    UNIQUE(post_id, reaction_type)
                );
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_posts_channel_id ON posts(channel_id);
                CREATE INDEX IF NOT EXISTS idx_posts_date_published ON posts(date_published);
                CREATE INDEX IF NOT EXISTS idx_post_summaries_channel_id ON post_summaries(channel_id);
                CREATE INDEX IF NOT EXISTS idx_post_summaries_date_published ON post_summaries(date_published);
                CREATE INDEX IF NOT EXISTS idx_reactions_post_id ON reactions(post_id);
            """)
            
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis (
                    id SERIAL PRIMARY KEY,
                    post_id INTEGER NOT NULL,
                    analysis_type TEXT NOT NULL DEFAULT 'default',
                    result JSONB NOT NULL,
                    prompt TEXT NOT NULL,
                    analysis_text TEXT,
                    status TEXT NOT NULL DEFAULT 'success',
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (post_id) REFERENCES posts (id),
                    UNIQUE(post_id, analysis_type)
                );
            """)
            
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_analysis_post_id ON analysis(post_id);
                CREATE INDEX IF NOT EXISTS idx_analysis_type ON analysis(analysis_type);
                CREATE INDEX IF NOT EXISTS idx_analysis_status ON analysis(status);
            """)
            
            self.connection.commit()
            logger.info("Таблицы успешно созданы")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка создания таблиц: {e}")
            self.connection.rollback()
            return False
    
    def save_channel(self, telegram_id, title, username=None, channel_type='channel'):
        """Сохранение информации о канале"""
        try:
            self.cursor.execute("""
                INSERT INTO channels (telegram_id, title, username, type)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (telegram_id) 
                DO UPDATE SET 
                    title = EXCLUDED.title,
                    username = EXCLUDED.username,
                    type = EXCLUDED.type
                RETURNING id;
            """, (telegram_id, title, username, channel_type))
            
            channel_id = self.cursor.fetchone()['id']
            self.connection.commit()
            logger.info(f"Канал сохранен: {title} (ID: {channel_id})")
            return channel_id
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка сохранения канала: {e}")
            self.connection.rollback()
            return None
    
    def save_post(self, channel_id, telegram_message_id, sender_name, sender_id, 
                  content, date_published, views_count=0, forwards_count=0, replies_count=0):
        """Сохранение поста"""
        try:
            self.cursor.execute("""
                INSERT INTO posts (
                    channel_id, telegram_message_id, sender_name, sender_id,
                    content, date_published, views_count, forwards_count, replies_count
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (channel_id, telegram_message_id)
                DO UPDATE SET
                    content = EXCLUDED.content,
                    views_count = EXCLUDED.views_count,
                    forwards_count = EXCLUDED.forwards_count,
                    replies_count = EXCLUDED.replies_count,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id;
            """, (channel_id, telegram_message_id, sender_name, sender_id,
                  content, date_published, views_count, forwards_count, replies_count))
            
            post_id = self.cursor.fetchone()['id']
            self.connection.commit()
            logger.debug(f"Пост сохранен: ID {post_id}")
            return post_id
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка сохранения поста: {e}")
            self.connection.rollback()
            return None
    
    def save_post_summary(self, channel_id, telegram_message_id, sender_name, sender_id,
                         summary, main_idea, date_published, views_count=0, forwards_count=0, replies_count=0, channel_name=None):
        """Сохранение саммари поста"""
        try:
            self.cursor.execute("""
                INSERT INTO post_summaries (
                    channel_id, telegram_message_id, sender_name, sender_id,
                    summary, main_idea, date_published, views_count, forwards_count, replies_count, channel_name
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (channel_id, telegram_message_id)
                DO UPDATE SET
                    summary = EXCLUDED.summary,
                    main_idea = EXCLUDED.main_idea,
                    views_count = EXCLUDED.views_count,
                    forwards_count = EXCLUDED.forwards_count,
                    replies_count = EXCLUDED.replies_count,
                    channel_name = EXCLUDED.channel_name,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id;
            """, (channel_id, telegram_message_id, sender_name, sender_id,
                  summary, main_idea, date_published, views_count, forwards_count, replies_count, channel_name))
            
            summary_id = self.cursor.fetchone()['id']
            self.connection.commit()
            logger.debug(f"Саммари поста сохранено: ID {summary_id}")
            return summary_id
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка сохранения саммари поста: {e}")
            self.connection.rollback()
            return None

    def update_summary_analysis(self, summary_id, analysis, importance_score):
        """Обновление саммари с результатами анализа"""
        try:
            self.cursor.execute("""
                UPDATE post_summaries
                SET analysis = %s, importance_score = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id;
            """, (analysis, importance_score, summary_id))
            
            result = self.cursor.fetchone()
            if result:
                self.connection.commit()
                logger.debug(f"Анализ саммари обновлен: ID {summary_id}, важность {importance_score}")
                return True
            else:
                logger.warning(f"Саммари с ID {summary_id} не найдено")
                return False
                
        except psycopg2.Error as e:
            logger.error(f"Ошибка обновления анализа саммари: {e}")
            self.connection.rollback()
            return False

    def get_summaries_without_analysis(self, limit=None):
        """Получение саммари без анализа"""
        try:
            query = """
                SELECT ps.*, c.title as channel_title
                FROM post_summaries ps
                JOIN channels c ON ps.channel_id = c.id
                WHERE ps.analysis IS NULL
                ORDER BY ps.date_published DESC
            """
            
            params = []
            if limit:
                query += " LIMIT %s"
                params.append(limit)
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка получения саммари без анализа: {e}")
            return []

    def save_reactions(self, post_id, reactions_data):
        """Сохранение реакций к посту"""
        if not reactions_data:
            return True
            
        try:
            for reaction_type, count in reactions_data.items():
                self.cursor.execute("""
                    INSERT INTO reactions (post_id, reaction_type, count)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (post_id, reaction_type)
                    DO UPDATE SET
                        count = EXCLUDED.count,
                        updated_at = CURRENT_TIMESTAMP;
                """, (post_id, reaction_type, count))
            
            self.connection.commit()
            logger.debug(f"Реакции сохранены для поста {post_id}")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка сохранения реакций: {e}")
            self.connection.rollback()
            return False
    
    def get_channel_stats(self, channel_id):
        """Получение статистики канала"""
        try:
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total_posts,
                    MIN(date_published) as first_post_date,
                    MAX(date_published) as last_post_date,
                    AVG(views_count) as avg_views,
                    SUM(views_count) as total_views
                FROM posts 
                WHERE channel_id = %s;
            """, (channel_id,))
            
            return self.cursor.fetchone()
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return None
    
    def get_channel_by_telegram_id(self, telegram_id):
        """Получение информации о канале по telegram_id"""
        try:
            self.cursor.execute("""
                SELECT id, telegram_id, title, username, type, created_at
                FROM channels
                WHERE telegram_id = %s;
            """, (telegram_id,))
            
            return self.cursor.fetchone()
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка получения канала: {e}")
            return None
    
    def get_channel_by_id(self, channel_id):
        """Получение информации о канале по ID"""
        try:
            self.cursor.execute("""
                SELECT id, telegram_id, title, username, type, created_at
                FROM channels
                WHERE id = %s;
            """, (channel_id,))
            
            return self.cursor.fetchone()
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка получения канала по ID: {e}")
            return None
    
    def get_summaries_by_date_range(self, channel_id, start_date, end_date):
        """Получение саммари постов за период"""
        try:
            self.cursor.execute("""
                SELECT ps.*, c.title as channel_title
                FROM post_summaries ps
                JOIN channels c ON ps.channel_id = c.id
                WHERE ps.channel_id = %s
                AND ps.date_published BETWEEN %s AND %s
                ORDER BY ps.date_published DESC;
            """, (channel_id, start_date, end_date))
            
            return self.cursor.fetchall()
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка получения саммари постов: {e}")
            return []

    def get_posts_by_date_range(self, channel_id, start_date, end_date):
        """Получение постов за период (устаревший метод)"""
        try:
            self.cursor.execute("""
                SELECT p.*, c.title as channel_title
                FROM posts p
                JOIN channels c ON p.channel_id = c.id
                WHERE p.channel_id = %s
                AND p.date_published BETWEEN %s AND %s
                ORDER BY p.date_published DESC;
            """, (channel_id, start_date, end_date))
            
            return self.cursor.fetchall()
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка получения постов: {e}")
            return []
    
    def get_top_posts_by_reactions(self, channel_id, limit=10):
        """Получение топ постов по реакциям"""
        try:
            self.cursor.execute("""
                SELECT 
                    p.*,
                    c.title as channel_title,
                    SUM(r.count) as total_reactions
                FROM posts p
                JOIN channels c ON p.channel_id = c.id
                LEFT JOIN reactions r ON p.id = r.post_id
                WHERE p.channel_id = %s
                GROUP BY p.id, c.title
                ORDER BY total_reactions DESC NULLS LAST
                LIMIT %s;
            """, (channel_id, limit))
            
            return self.cursor.fetchall()
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка получения топ постов: {e}")
            return []
            
    
    def calculate_post_importance_score(self, post_data):
        """Упрощенный расчет важности поста на основе метрик"""
        try:
            views_count = post_data.get('views_count', 0)
            forwards_count = post_data.get('forwards_count', 0)
            replies_count = post_data.get('replies_count', 0)
            
            # Получаем реакции для поста
            self.cursor.execute("""
                SELECT reaction_type, count FROM reactions
                WHERE post_id = %s
            """, (post_data['id'],))
            reactions = self.cursor.fetchall()
            
            # Подсчитываем позитивные реакции
            positive_reactions = ['👍', 'like', '❤️', 'heart', '🥰', 'love', '😁', 'laugh', '👏', 'clap', '🔥', 'fire', '💯', 'hundred']
            positive_reaction_count = 0
            total_reaction_count = 0
            
            for reaction in reactions:
                total_reaction_count += reaction['count']
                if any(pos in reaction['reaction_type'].lower() for pos in positive_reactions):
                    positive_reaction_count += reaction['count']
            
            # Упрощенный расчет важности (1-10)
            importance_score = min(10, max(1,
                (forwards_count * 0.5) +
                (replies_count * 0.3) +
                (positive_reaction_count * 0.2) +
                (views_count / 1000 * 0.1)
            ))
            
            return {
                'final_score': round(importance_score, 2),
                'forwards': forwards_count,
                'replies': replies_count,
                'positive_reactions': positive_reaction_count,
                'total_reactions': total_reaction_count,
                'views': views_count
            }
            
        except Exception as e:
            logger.error(f"Ошибка расчета важности поста: {e}")
            return {'final_score': 5.0}
    
    def get_top_important_summaries_for_publication(self, limit=5):
        """Получение топ саммари для публикации на основе метрик"""
        try:
            query = """
                SELECT
                    ps.id, ps.summary, ps.main_idea, ps.date_published, ps.telegram_message_id,
                    ps.views_count, ps.forwards_count, ps.replies_count,
                    COALESCE(ps.channel_name, c.title) as channel_title, c.username as channel_username
                FROM post_summaries ps
                JOIN channels c ON ps.channel_id = c.id
                ORDER BY
                    ps.forwards_count DESC,
                    ps.replies_count DESC,
                    ps.views_count DESC,
                    ps.date_published DESC
                LIMIT %s;
            """
            
            self.cursor.execute(query, (limit,))
            results = self.cursor.fetchall()
            
            logger.info(f"Найдено {len(results)} саммари для публикации")
            return results
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка получения саммари: {e}")
            return []

    def get_top_important_posts_for_publication(self, limit=5):
        """Получение топ постов для публикации на основе метрик"""
        try:
            query = """
                SELECT
                    p.id, p.content, p.date_published, p.telegram_message_id,
                    p.views_count, p.forwards_count, p.replies_count,
                    c.title as channel_title, c.username as channel_username
                FROM posts p
                JOIN channels c ON p.channel_id = c.id
                WHERE p.date_published >= NOW() - INTERVAL '24 hours'
                ORDER BY
                    p.forwards_count DESC,
                    p.replies_count DESC,
                    p.views_count DESC,
                    p.date_published DESC
                LIMIT %s;
            """
            
            self.cursor.execute(query, (limit,))
            results = self.cursor.fetchall()
            
            logger.info(f"Найдено {len(results)} постов для публикации")
            return results
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка получения постов: {e}")
            return []

    def clear_all_tables(self):
        """Очистка всех таблиц в базе данных"""
        try:
            # Отключаем проверку внешних ключей для очистки
            self.cursor.execute("SET CONSTRAINTS ALL DEFERRED")
            
            # Очищаем таблицы в правильном порядке (от дочерних к родительским)
            tables = [
                'analysis',
                'reactions',
                'post_summaries',
                'posts',
                'channels'
            ]
            
            for table in tables:
                self.cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
                logger.info(f"Таблица {table} очищена")
            
            self.connection.commit()
            logger.info("Все таблицы успешно очищены")
            return True
            
        except psycopg2.Error as e:
            logger.error(f"Ошибка очистки таблиц: {e}")
            self.connection.rollback()
            return False