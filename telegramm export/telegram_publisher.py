#!/usr/bin/env python3
"""
Модуль для отправки саммаризации в Telegram канал
"""

import asyncio
import logging
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from telethon.tl.functions.channels import CreateChannelRequest
from telethon.tl.functions.account import UpdateUsernameRequest
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, SESSION_PATH
from database import DatabaseManager

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TelegramPublisher:
    """Класс для отправки саммаризации в Telegram канал"""
    
    def __init__(self, target_channel=None):
        # Используем отдельную сессию для публикатора
        self.client = TelegramClient(SESSION_PATH + "_publisher", TELEGRAM_API_ID, TELEGRAM_API_HASH)
        self.target_channel = target_channel
        
    async def connect(self):
        """Подключение к Telegram"""
        try:
            await self.client.start()
            logger.info("Успешное подключение к Telegram для публикации")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения к Telegram: {e}")
            return False
    
    async def disconnect(self):
        """Отключение от Telegram"""
        if self.client.is_connected():
            await self.client.disconnect()
            logger.info("Отключение от Telegram")
    
    async def create_summary_channel(self, channel_name="AI Саммаризация"):
        """Создание нового канала для саммаризации"""
        try:
            # Создаем канал
            result = await self.client(CreateChannelRequest(
                title=channel_name,
                about="Автоматическая саммаризация постов с помощью AI",
                megagroup=False  # Канал, а не группа
            ))
            
            channel = result.chats[0]
            logger.info(f"Создан канал: {channel_name} (ID: {channel.id})")
            
            # Делаем канал публичным (опционально)
            username = f"ai_summary_{datetime.now().strftime('%Y%m%d')}"
            try:
                await self.client(UpdateUsernameRequest(
                    channel=channel,
                    username=username
                ))
                logger.info(f"Канал доступен по адресу: @{username}")
            except Exception as e:
                logger.warning(f"Не удалось установить username для канала: {e}")
            
            return channel.id
            
        except Exception as e:
            logger.error(f"Ошибка создания канала: {e}")
            return None
    
    async def send_summary(self, channel_target, original_post, analysis_result=None, source_channel="Unknown"):
        """Отправка саммаризации в канал"""
        try:
            # Формируем сообщение с саммаризацией
            if analysis_result is None:
                analysis_result = {
                    'analysis_text': 'Анализ не выполнен',
                    'model_used': 'None',
                    'status': 'skipped'
                }
            message = self._format_summary_message(original_post, analysis_result, source_channel)
            
            # Всегда разбиваем сообщение на части для гарантии доставки полного анализа
            messages = self._split_long_message(message, max_length=4000)
            
            for i, msg_part in enumerate(messages):
                await self.client.send_message(channel_target, msg_part, parse_mode='markdown')
                if i < len(messages) - 1:  # Пауза между частями, кроме последней
                    await asyncio.sleep(2)  # Увеличиваем паузу для надежности
            
            logger.info(f"Саммаризация отправлена в канал {channel_target} ({len(messages)} частей)")
            return True
            
        except FloodWaitError as e:
            logger.warning(f"Flood wait: ожидание {e.seconds} секунд")
            await asyncio.sleep(e.seconds)
            return await self.send_summary(channel_target, original_post, analysis_result, source_channel)
            
        except Exception as e:
            logger.error(f"Ошибка отправки саммаризации: {e}")
            return False
    
    async def send_summary_post(self, channel_target, summary_post, analysis_result, source_channel="Unknown"):
        """Отправка саммари поста в канал"""
        try:
            # Формируем сообщение с саммари
            message = self._format_summary_post_message(summary_post, analysis_result, source_channel)
            
            # Всегда разбиваем сообщение на части для гарантии доставки полного анализа
            messages = self._split_long_message(message, max_length=4000)
            
            for i, msg_part in enumerate(messages):
                await self.client.send_message(channel_target, msg_part, parse_mode='markdown')
                if i < len(messages) - 1:  # Пауза между частями, кроме последней
                    await asyncio.sleep(2)  # Увеличиваем паузу для надежности
            
            logger.info(f"Саммари отправлено в канал {channel_target} ({len(messages)} частей)")
            return True
            
        except FloodWaitError as e:
            logger.warning(f"Flood wait: ожидание {e.seconds} секунд")
            await asyncio.sleep(e.seconds)
            return await self.send_summary_post(channel_target, summary_post, analysis_result, source_channel)
            
        except Exception as e:
            logger.error(f"Ошибка отправки саммари: {e}")
            return False
    
    def _split_long_message(self, message, max_length=4000):
        """Разбивает длинное сообщение на части с сохранением структуры анализа"""
        if len(message) <= max_length:
            return [message]
        
        parts = []
        current_part = ""
        lines = message.split('\n')
        
        # Добавляем заголовок к каждой части (кроме первой)
        header_lines = []
        for i, line in enumerate(lines):
            if line.startswith('📊 **ПОЛНЫЙ АНАЛИЗ ВЛИЯНИЯ НА ЯНДЕКС ПУТЕШЕСТВИЯ:**'):
                header_lines = lines[:i+1]  # Включаем заголовок анализа
                break
            elif i < 10:  # Берем первые строки как заголовок
                continue
        
        for i, line in enumerate(lines):
            # Если добавление строки превысит лимит
            if len(current_part) + len(line) + 1 > max_length:
                if current_part:
                    parts.append(current_part.strip())
                    
                    # Для продолжения анализа добавляем краткий заголовок
                    if len(parts) > 1 and any('АНАЛИЗ ВЛИЯНИЯ' in part for part in parts):
                        current_part = f"🤖 **Анализ влияния на Яндекс Путешествия (продолжение {len(parts)})**\n\n{line}\n"
                    else:
                        current_part = line + '\n'
                else:
                    # Если одна строка слишком длинная, разбиваем её по предложениям
                    if '. ' in line and len(line) > max_length:
                        sentences = line.split('. ')
                        temp_line = ""
                        for sentence in sentences:
                            if len(temp_line) + len(sentence) + 2 > max_length:
                                if temp_line:
                                    parts.append(temp_line.strip())
                                temp_line = sentence + '. '
                            else:
                                temp_line += sentence + '. '
                        current_part = temp_line
                    else:
                        # Разбиваем по символам как последний вариант
                        while len(line) > max_length:
                            parts.append(line[:max_length])
                            line = line[max_length:]
                        current_part = line + '\n'
            else:
                current_part += line + '\n'
        
        if current_part.strip():
            parts.append(current_part.strip())
        
        # Добавляем номера частей для длинных анализов
        if len(parts) > 1:
            for i in range(len(parts)):
                if i == 0:
                    parts[i] += f"\n\n_Часть 1 из {len(parts)}_"
                else:
                    parts[i] += f"\n\n_Часть {i+1} из {len(parts)}_"
        
        return parts
    
    def _format_summary_message(self, original_post, analysis_result, source_channel):
        """Форматирование сообщения с саммаризацией"""
        
        # Извлекаем данные из анализа
        analysis_text = analysis_result.get('analysis_text', 'Анализ недоступен')
        model_used = analysis_result.get('model_used', 'Unknown')
        status = analysis_result.get('status', 'unknown')
        
        # Извлекаем заголовок из оригинального поста
        original_content = original_post.get('content', '')
        lines = original_content.split('\n')
        title = lines[0] if lines else original_content
        
        # Формируем ссылку на оригинальный пост
        telegram_message_id = original_post.get('telegram_message_id')
        channel_username = original_post.get('channel_username', source_channel)
        
        # Убираем @ из username если есть
        if channel_username and channel_username.startswith('@'):
            channel_username = channel_username[1:]
        
        post_link = f"https://t.me/{channel_username}/{telegram_message_id}" if telegram_message_id and channel_username else "Ссылка недоступна"
        
        # Форматируем дату
        date_published = original_post.get('date_published', datetime.now())
        if isinstance(date_published, str):
            date_str = date_published
        else:
            date_str = date_published.strftime("%Y-%m-%d %H:%M")
        
        # Очищаем анализ от ненужных частей
        cleaned_analysis = self._clean_analysis_text(analysis_text)
        
        # Создаем сообщение с очищенным анализом
        message = f"""🤖 **Анализ влияния на Яндекс Путешествия**

📅 **Дата:** {date_str}
📺 **Источник:** {source_channel}
🧠 **Модель:** {model_used}
✅ **Статус:** {status}

📝 **Заголовок новости:**
_{title}_

🔗 **[Читать оригинальный пост]({post_link})**

📊 **АНАЛИЗ ВЛИЯНИЯ НА ЯНДЕКС ПУТЕШЕСТВИЯ:**

{cleaned_analysis}

---
_Автоматический анализ влияния на Яндекс Путешествия с помощью Zeliboba AI_
"""
        
        return message
    
    def _clean_analysis_text(self, analysis_text):
        """Очищает текст анализа от ненужных частей"""
        # Убираем "Анализ текста:" и все до первого структурированного элемента
        lines = analysis_text.split('\n')
        cleaned_lines = []
        skip_until_structure = True
        
        for line in lines:
            line = line.strip()
            
            # Пропускаем строки до начала структурированного анализа
            if skip_until_structure:
                if any(keyword in line.lower() for keyword in ['тональность:', 'отношение к', 'влияние на', 'важность:', 'ключевые']):
                    skip_until_structure = False
                    cleaned_lines.append(line)
                elif 'влияние на яндекс путешествия:' in line.lower():
                    skip_until_structure = False
                    cleaned_lines.append(line)
                else:
                    continue
            else:
                cleaned_lines.append(line)
        
        # Если не нашли структурированный анализ, возвращаем исходный текст
        if not cleaned_lines:
            return analysis_text
        
        return '\n'.join(cleaned_lines)
    
    def _format_summary_post_message(self, summary_post, analysis_result, source_channel):
        """Форматирование сообщения с саммари поста"""
        
        # Извлекаем данные из анализа
        analysis_text = analysis_result.get('analysis_text', 'Анализ недоступен')
        model_used = analysis_result.get('model_used', 'Unknown')
        status = analysis_result.get('status', 'unknown')
        
        # Извлекаем данные саммари
        main_idea = summary_post.get('main_idea', '')
        summary = summary_post.get('summary', '')
        
        # Формируем ссылку на оригинальный пост
        telegram_message_id = summary_post.get('telegram_message_id')
        channel_username = summary_post.get('channel_username', source_channel)
        
        # Убираем @ из username если есть
        if channel_username and channel_username.startswith('@'):
            channel_username = channel_username[1:]
        
        post_link = f"https://t.me/{channel_username}/{telegram_message_id}" if telegram_message_id and channel_username else "Ссылка недоступна"
        
        # Форматируем дату
        date_published = summary_post.get('date_published', datetime.now())
        if isinstance(date_published, str):
            date_str = date_published
        else:
            date_str = date_published.strftime("%Y-%m-%d %H:%M")
        
        # Очищаем анализ от ненужных частей
        cleaned_analysis = self._clean_analysis_text(analysis_text)
        
        # Создаем сообщение с очищенным анализом
        message = f"""🤖 **Анализ влияния новости на Яндекс Путешествия**

📅 **Дата:** {date_str}
📺 **Источник:** {source_channel}
🧠 **Модель:** {model_used}
✅ **Статус:** {status}

💡 **Главная мысль:**
_{main_idea}_

📝 **Краткое саммари:**
{summary}

🔗 **[Читать оригинальный пост]({post_link})**

📊 **АНАЛИЗ ВЛИЯНИЯ НА ЯНДЕКС ПУТЕШЕСТВИЯ:**

{cleaned_analysis}

---
_Автоматический анализ влияния на Яндекс Путешествия с помощью Zeliboba AI_
"""
        
        return message
    
    async def send_batch_summaries(self, channel_target, limit=10):
        """Отправка пакета саммаризаций из базы данных"""
        db = DatabaseManager()
        if not db.connect():
            logger.error("Не удалось подключиться к базе данных")
            return 0
        
        try:
            # Получаем успешные анализы, которые еще не были отправлены
            query = """
                SELECT 
                    p.id, p.content, p.date_published,
                    c.title as channel_title,
                    za.analysis_text, za.model_name, za.status, za.result
                FROM posts p
                JOIN channels c ON p.channel_id = c.id
                JOIN zeliboba_analysis za ON p.id = za.post_id
                WHERE za.status = 'success' 
                AND za.analysis_text IS NOT NULL
                ORDER BY p.date_published DESC
                LIMIT %s;
            """
            
            db.cursor.execute(query, (limit,))
            results = db.cursor.fetchall()
            
            if not results:
                logger.info("Нет анализов для отправки")
                return 0
            
            sent_count = 0
            for row in results:
                original_post = {
                    'content': row['content'],
                    'date_published': row['date_published']
                }
                
                analysis_result = {
                    'analysis_text': row['analysis_text'],
                    'model_used': row['model_name'],
                    'status': row['status']
                }
                
                success = await self.send_summary(
                    channel_target,
                    original_post,
                    analysis_result,
                    row['channel_title']
                )
                
                if success:
                    sent_count += 1
                    # Небольшая пауза между отправками
                    await asyncio.sleep(1)
                else:
                    logger.error(f"Не удалось отправить саммаризацию для поста {row['id']}")
            
            logger.info(f"Отправлено {sent_count} саммаризаций из {len(results)}")
            return sent_count
            
        except Exception as e:
            logger.error(f"Ошибка отправки пакета саммаризаций: {e}")
            return 0
        finally:
            db.disconnect()
    
    async def send_summary_with_analysis(self, channel_target, summary_data):
        """Отправка саммари с анализом в канал"""
        try:
            # Формируем сообщение с саммари и анализом
            message = self._format_summary_with_analysis_message(summary_data)
            
            # Всегда разбиваем сообщение на части для гарантии доставки полного анализа
            messages = self._split_long_message(message, max_length=4000)
            
            for i, msg_part in enumerate(messages):
                await self.client.send_message(channel_target, msg_part, parse_mode='markdown')
                if i < len(messages) - 1:  # Пауза между частями, кроме последней
                    await asyncio.sleep(2)  # Увеличиваем паузу для надежности
            
            logger.info(f"Саммари с анализом отправлено в канал {channel_target} ({len(messages)} частей)")
            return True
            
        except FloodWaitError as e:
            logger.warning(f"Flood wait: ожидание {e.seconds} секунд")
            await asyncio.sleep(e.seconds)
            return await self.send_summary_with_analysis(channel_target, summary_data)
            
        except Exception as e:
            logger.error(f"Ошибка отправки саммари с анализом: {e}")
            return False
    
    def _format_summary_with_analysis_message(self, summary_data):
        """Форматирование сообщения с саммари и анализом"""
        
        # Извлекаем данные саммари
        main_idea = summary_data.get('main_idea', '')
        summary = summary_data.get('summary', '')
        analysis = summary_data.get('analysis', 'Анализ недоступен')
        importance_score = summary_data.get('importance_score', 5.0)
        channel_title = summary_data.get('channel_title', 'Unknown')
        
        # Формируем ссылку на оригинальный пост
        telegram_message_id = summary_data.get('telegram_message_id')
        channel_username = summary_data.get('channel_username', '')
        
        # Убираем @ из username если есть
        if channel_username and channel_username.startswith('@'):
            channel_username = channel_username[1:]
        
        post_link = f"https://t.me/{channel_username}/{telegram_message_id}" if telegram_message_id and channel_username else "Ссылка недоступна"
        
        # Форматируем дату
        date_published = summary_data.get('date_published', datetime.now())
        if isinstance(date_published, str):
            date_str = date_published
        else:
            date_str = date_published.strftime("%Y-%m-%d %H:%M")
        
        # Определяем эмодзи важности
        if importance_score >= 9:
            importance_emoji = "🔥🔥🔥"
        elif importance_score >= 8:
            importance_emoji = "🔥🔥"
        elif importance_score >= 7:
            importance_emoji = "🔥"
        else:
            importance_emoji = "📊"
        
        # Создаем сообщение
        message = f"""{importance_emoji} **Анализ влияния новости на Яндекс Путешествия**

📅 **Дата:** {date_str}
📺 **Источник:** {channel_title}
⭐ **Важность:** {importance_score}/10

💡 **Главная мысль:**
_{main_idea}_

📝 **Краткое саммари:**
{summary}

🔗 **[Читать оригинальный пост]({post_link})**

📊 **ПОЛНЫЙ АНАЛИЗ ВЛИЯНИЯ НА ЯНДЕКС ПУТЕШЕСТВИЯ:**

{analysis}

---
_Автоматический анализ влияния на Яндекс Путешествия с помощью Zeliboba AI_
"""
        
        return message

async def main():
    """Основная функция для тестирования"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Отправка саммаризации в Telegram')
    parser.add_argument('--create-channel', action='store_true', help='Создать новый канал')
    parser.add_argument('--channel-name', default='AI Саммаризация', help='Название канала')
    parser.add_argument('--send-summaries', type=int, help='Отправить N саммаризаций')
    parser.add_argument('--channel-id', help='ID канала или username для отправки (например: -1001234567890 или @channel_name)')
    
    args = parser.parse_args()
    
    publisher = TelegramPublisher()
    
    if not await publisher.connect():
        logger.error("Не удалось подключиться к Telegram")
        return
    
    try:
        if args.create_channel:
            channel_id = await publisher.create_summary_channel(args.channel_name)
            if channel_id:
                print(f"✅ Канал создан! ID: {channel_id}")
                print(f"Используйте --channel-id {channel_id} для отправки саммаризаций")
            else:
                print("❌ Не удалось создать канал")
        
        elif args.send_summaries and args.channel_id:
            sent = await publisher.send_batch_summaries(args.channel_id, args.send_summaries)
            print(f"✅ Отправлено {sent} саммаризаций")
        
        else:
            print("Использование:")
            print("  python telegram_publisher.py --create-channel")
            print("  python telegram_publisher.py --send-summaries 5 --channel-id CHANNEL_ID")
    
    finally:
        await publisher.disconnect()

if __name__ == "__main__":
    asyncio.run(main())