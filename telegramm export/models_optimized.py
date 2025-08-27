from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)

@dataclass
class Channel:
    """Модель канала/чата"""
    telegram_id: int
    title: str
    username: Optional[str] = None
    type: str = 'channel'
    id: Optional[int] = None
    created_at: Optional[datetime] = None

@dataclass
class Post:
    """Модель поста/сообщения"""
    channel_id: int
    telegram_message_id: int
    content: str
    date_published: datetime
    sender_name: Optional[str] = None
    sender_id: Optional[int] = None
    views_count: int = 0
    forwards_count: int = 0
    replies_count: int = 0
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Reaction:
    """Модель реакции"""
    post_id: int
    reaction_type: str
    count: int
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class PostSummary:
    """Модель саммари поста"""
    channel_id: int
    telegram_message_id: int
    summary: str
    main_idea: str
    date_published: datetime
    sender_name: Optional[str] = None
    sender_id: Optional[int] = None
    views_count: int = 0
    forwards_count: int = 0
    replies_count: int = 0
    channel_name: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ReactionParser:
    """Парсер реакций из Telegram API"""
    
    @staticmethod
    def parse_reactions(message_reactions) -> Dict[str, int]:
        """Парсит реакции из объекта сообщения Telegram"""
        reactions = {}
        
        if not message_reactions or not hasattr(message_reactions, 'results'):
            return reactions
        
        for reaction in message_reactions.results:
            if hasattr(reaction, 'reaction'):
                if hasattr(reaction.reaction, 'emoticon'):
                    reaction_type = reaction.reaction.emoticon
                elif hasattr(reaction.reaction, 'document_id'):
                    reaction_type = f"custom_{reaction.reaction.document_id}"
                else:
                    reaction_type = "unknown"
                
                reactions[reaction_type] = reaction.count
        
        return reactions
    
    @staticmethod
    def normalize_reaction_type(reaction_type: str) -> str:
        """Нормализует тип реакции для удобства анализа"""
        emoji_mapping = {
            '👍': 'like',
            '👎': 'dislike',
            '❤️': 'heart',
            '🔥': 'fire',
            '🥰': 'love',
            '😁': 'laugh',
            '😱': 'wow',
            '😢': 'sad',
            '😡': 'angry'
        }
        
        return emoji_mapping.get(reaction_type, reaction_type)

class MessageProcessor:
    """Обработчик сообщений из Telegram"""
    
    @staticmethod
    def extract_message_data(message, channel_id: int) -> Optional[Post]:
        """Извлекает данные из сообщения Telegram"""
        if not message.text:
            return None
        
        sender_name = "Unknown"
        sender_id = None
        
        if message.sender:
            if hasattr(message.sender, 'first_name'):
                sender_name = message.sender.first_name or ""
                if hasattr(message.sender, 'last_name') and message.sender.last_name:
                    sender_name += f" {message.sender.last_name}"
            elif hasattr(message.sender, 'title'):
                sender_name = message.sender.title
            
            if hasattr(message.sender, 'id'):
                sender_id = message.sender.id
        
        return Post(
            channel_id=channel_id,
            telegram_message_id=message.id,
            content=message.text,
            date_published=message.date,
            sender_name=sender_name,
            sender_id=sender_id,
            views_count=message.views or 0,
            forwards_count=message.forwards or 0,
            replies_count=getattr(message.replies, 'replies', 0) if hasattr(message, 'replies') and message.replies is not None else 0
        )
    
    @staticmethod
    def format_message_for_file(message, sender_name: str) -> str:
        """Форматирует сообщение для записи в файл"""
        date_str = message.date.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{date_str}] {sender_name}: {message.text}"

class ExportStats:
    """Статистика экспорта"""
    
    def __init__(self):
        self.total_messages = 0
        self.saved_to_db = 0
        self.saved_to_file = 0
        self.errors = 0
        self.channels_processed = 0
        self.start_time = datetime.now()
    
    def add_message(self):
        self.total_messages += 1
    
    def add_db_save(self):
        self.saved_to_db += 1
    
    def add_file_save(self):
        self.saved_to_file += 1
    
    def add_error(self):
        self.errors += 1
    
    def add_channel(self):
        self.channels_processed += 1
    
    def get_duration(self) -> float:
        return (datetime.now() - self.start_time).total_seconds()
    
    def get_summary(self) -> str:
        duration = self.get_duration()
        return f"""
Статистика экспорта:
- Обработано каналов: {self.channels_processed}
- Всего сообщений: {self.total_messages}
- Сохранено в БД: {self.saved_to_db}
- Сохранено в файлы: {self.saved_to_file}
- Ошибок: {self.errors}
- Время выполнения: {duration:.2f} сек
- Скорость: {self.total_messages/duration:.2f} сообщений/сек
        """.strip()