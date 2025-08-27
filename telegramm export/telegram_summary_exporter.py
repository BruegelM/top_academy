#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Программа для экспорта чатов Telegram с созданием саммари вместо сохранения полных текстов.
Создает краткие саммари постов с выделением главной мысли.
"""

import os
import sys
import asyncio
import datetime
import argparse
import subprocess
import importlib.util
import logging
import re
from typing import Optional

# Получаем директорию, в которой находится скрипт
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_summary_export.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Функция для проверки наличия модуля
def is_module_installed(module_name):
    """Проверяет, установлен ли модуль"""
    return importlib.util.find_spec(module_name) is not None

# Проверка наличия модуля telethon
telethon_installed = is_module_installed("telethon")

if not telethon_installed:
    print("Ошибка: Модуль telethon не установлен.")
    print("Установите его командой: pip install telethon")
    sys.exit(1)
else:
    # Импортируем telethon, если он установлен
    from telethon import TelegramClient, events
    from telethon.tl.types import InputPeerChannel, InputPeerChat, InputPeerUser

# Импорт наших модулей
try:
    from config import (TELEGRAM_API_ID, TELEGRAM_API_HASH, SESSION_PATH, DEFAULT_EXPORT_DIR,
                       ZELIBOBA_API_TOKEN, ZELIBOBA_BASE_URL, ZELIBOBA_MODEL_NAME,
                       ZELIBOBA_TEMPERATURE)
    from database import DatabaseManager
    from models import (Channel, PostSummary, ReactionParser, MessageProcessor, ExportStats,
                       ZelibobaAnalyzer)
except ImportError as e:
    logger.error(f"Ошибка импорта модулей: {e}")
    print("Убедитесь, что все необходимые файлы находятся в директории скрипта")
    sys.exit(1)

# Настройки API Telegram
API_ID = TELEGRAM_API_ID
API_HASH = TELEGRAM_API_HASH

class SummaryExportStats(ExportStats):
    """Расширенная статистика для экспорта саммари"""
    
    def __init__(self):
        super().__init__()
        self.summaries_created = 0
        self.summaries_failed = 0
        self.posts_too_short = 0
    
    def add_summary_created(self):
        """Увеличить счетчик созданных саммари"""
        self.summaries_created += 1
    
    def add_summary_failed(self):
        """Увеличить счетчик неудачных саммари"""
        self.summaries_failed += 1
    
    def add_post_too_short(self):
        """Увеличить счетчик слишком коротких постов"""
        self.posts_too_short += 1
    
    def get_summary(self) -> str:
        """Получить сводку статистики с саммари"""
        base_summary = super().get_summary()
        duration = self.get_duration()
        
        summary_stats = f"""
Статистика создания саммари:
- Создано саммари: {self.summaries_created}
- Ошибок создания саммари: {self.summaries_failed}
- Постов слишком коротких: {self.posts_too_short}
- Скорость создания саммари: {self.summaries_created/duration:.2f} саммари/сек
        """.strip()
        
        return base_summary + "\n\n" + summary_stats

async def get_entity_by_name_or_id(client, chat_identifier):
    """
    Получает entity чата по имени, юзернейму или ID
    """
    try:
        # Пробуем интерпретировать как ID
        if chat_identifier.isdigit():
            chat_id = int(chat_identifier)
            try:
                return await client.get_entity(chat_id)
            except Exception as e:
                print(f"Не удалось найти чат по ID {chat_id}: {e}")
                pass
        
        # Пробуем интерпретировать как юзернейм или название
        return await client.get_entity(chat_identifier)
    except Exception as e:
        print(f"Ошибка при поиске чата: {e}")
        return None

def extract_summary_parts(analysis_text: str) -> tuple:
    """
    Извлекает главную мысль и саммари из ответа GPT
    
    Args:
        analysis_text: текст ответа от GPT
        
    Returns:
        tuple: (main_idea, summary)
    """
    try:
        # Ищем главную мысль
        main_idea_match = re.search(r'ГЛАВНАЯ МЫСЛЬ:\s*(.+?)(?:\n\n|\nСАММАРИ:|$)', analysis_text, re.DOTALL | re.IGNORECASE)
        main_idea = main_idea_match.group(1).strip() if main_idea_match else ""
        
        # Ищем саммари
        summary_match = re.search(r'САММАРИ:\s*(.+)', analysis_text, re.DOTALL | re.IGNORECASE)
        summary = summary_match.group(1).strip() if summary_match else ""
        
        # Если не удалось извлечь по шаблону, используем весь текст как саммари
        if not main_idea and not summary:
            # Пытаемся найти первое предложение как главную мысль
            sentences = analysis_text.split('.')
            if len(sentences) > 1:
                main_idea = sentences[0].strip() + '.'
                summary = analysis_text
            else:
                main_idea = analysis_text[:200] + "..." if len(analysis_text) > 200 else analysis_text
                summary = analysis_text
        elif not main_idea:
            # Если есть саммари, но нет главной мысли, берем первое предложение саммари
            sentences = summary.split('.')
            main_idea = sentences[0].strip() + '.' if sentences else summary[:200] + "..."
        elif not summary:
            # Если есть главная мысль, но нет саммари, используем главную мысль как саммари
            summary = main_idea
        
        # Ограничиваем размер саммари (1000 слов)
        words = summary.split()
        if len(words) > 1000:
            summary = ' '.join(words[:1000]) + "..."
            logger.warning(f"Саммари обрезано до 1000 слов")
        
        return main_idea, summary
        
    except Exception as e:
        logger.error(f"Ошибка извлечения частей саммари: {e}")
        # В случае ошибки возвращаем исходный текст
        return analysis_text[:200] + "..." if len(analysis_text) > 200 else analysis_text, analysis_text

async def export_chat_with_summaries(client, chat_entity, limit=None, offset_date=None, output_file=None,
                                   save_to_db=True, db_manager=None, last_24_hours_only=True):
    """
    Экспортирует историю сообщений из указанного чата, создавая саммари вместо сохранения полных текстов
    
    Args:
        client: клиент Telethon
        chat_entity: объект чата/канала
        limit: максимальное количество сообщений
        offset_date: дата, с которой начинать экспорт
        output_file: путь к выходному файлу
        save_to_db: сохранять ли в базу данных
        db_manager: менеджер базы данных
        last_24_hours_only: экспортировать только сообщения за последние 24 часа
    
    Returns:
        tuple: (путь к файлу, статистика экспорта)
    """
    stats = SummaryExportStats()
    stats.add_channel()
    
    # Инициализация анализатора Zeliboba
    if not ZELIBOBA_API_TOKEN:
        logger.error("ZELIBOBA_API_TOKEN не настроен, невозможно создавать саммари")
        print("Ошибка: Для создания саммари необходим ZELIBOBA_API_TOKEN в .env файле")
        return None, stats
    
    zeliboba_analyzer = ZelibobaAnalyzer(
        ZELIBOBA_API_TOKEN,
        ZELIBOBA_BASE_URL,
        ZELIBOBA_MODEL_NAME,
        ZELIBOBA_TEMPERATURE
    )
    
    logger.info(f"Zeliboba анализатор инициализирован с моделью: {ZELIBOBA_MODEL_NAME}")
    
    # Получаем информацию о чате
    chat_title = getattr(chat_entity, 'title', None) or getattr(chat_entity, 'first_name', None)
    if not chat_title:
        chat_title = f"chat_{chat_entity.id}"
    
    chat_username = getattr(chat_entity, 'username', None)
    chat_type = 'channel' if hasattr(chat_entity, 'broadcast') else 'chat'
    
    logger.info(f"Начинаем экспорт чата с созданием саммари: {chat_title} (ID: {chat_entity.id})")
    
    # Сохраняем информацию о канале в БД
    channel_id = None
    if save_to_db and db_manager:
        channel = Channel(
            telegram_id=chat_entity.id,
            title=chat_title,
            username=chat_username,
            type=chat_type
        )
        channel_id = db_manager.save_channel(
            channel.telegram_id,
            channel.title,
            channel.username,
            channel.type
        )
        if not channel_id:
            logger.warning("Не удалось сохранить канал в БД, продолжаем без сохранения в БД")
            save_to_db = False
    
    # Создаем текущую дату для использования в имени файла и заголовке
    current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    
    # Определяем имя файла
    if output_file:
        filename = output_file
    else:
        # Создаем директорию для чатов если её нет
        chats_dir = os.path.join(SCRIPT_DIR, DEFAULT_EXPORT_DIR)
        os.makedirs(chats_dir, exist_ok=True)
        
        # Создаем имя файла на основе названия чата и текущей даты
        safe_title = chat_title
        for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
            safe_title = safe_title.replace(char, '_')
        
        filename = os.path.join(chats_dir, f"{safe_title}_summaries_{current_date}.txt")
    
    print(f"Экспорт чата '{chat_title}' с созданием саммари в файл '{filename}'...")
    
    # Вычисляем дату для фильтрации (24 часа назад)
    if last_24_hours_only and not offset_date:
        offset_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)
        print(f"Экспортируем только сообщения за последние 24 часа (с {offset_date.strftime('%Y-%m-%d %H:%M:%S UTC')})")
    
    # Получаем сообщения
    summaries_for_file = []
    processed_count = 0
    
    try:
        async for message in client.iter_messages(
            chat_entity,
            limit=limit,
            offset_date=offset_date,
            reverse=True  # Сообщения в хронологическом порядке
        ):
            # Дополнительная проверка времени сообщения для точной фильтрации
            if last_24_hours_only and message.date:
                # Проверяем, что сообщение не старше 24 часов
                now = datetime.datetime.now(datetime.timezone.utc)
                message_time = message.date.replace(tzinfo=datetime.timezone.utc) if message.date.tzinfo is None else message.date
                time_diff = now - message_time
                if time_diff.total_seconds() > 24 * 3600:  # 24 часа в секундах
                    continue
            
            stats.add_message()
            processed_count += 1
            
            if processed_count % 50 == 0:
                print(f"Обработано {processed_count} сообщений...")
            
            if message.text:
                # Проверяем минимальную длину сообщения для создания саммари
                if len(message.text.strip()) < 100:  # Минимум 100 символов
                    stats.add_post_too_short()
                    logger.debug(f"Сообщение {message.id} слишком короткое для саммари ({len(message.text)} символов)")
                    continue
                
                # Получение информации об отправителе
                sender = message.sender
                sender_name = "Unknown"
                sender_id = None
                
                if sender:
                    if hasattr(sender, 'first_name'):
                        sender_name = sender.first_name or ""
                        if hasattr(sender, 'last_name') and sender.last_name:
                            sender_name += f" {sender.last_name}"
                    elif hasattr(sender, 'title'):
                        sender_name = sender.title
                    
                    if hasattr(sender, 'id'):
                        sender_id = sender.id
                
                try:
                    # Создаем саммари через GPT
                    logger.debug(f"Создаем саммари для сообщения {message.id}")
                    
                    summary_result = await zeliboba_analyzer.create_summary(message.text)
                    
                    if summary_result and summary_result.get("status") == "success":
                        analysis_text = summary_result.get("analysis_text", "")
                        
                        if analysis_text:
                            # Извлекаем главную мысль и саммари
                            main_idea, summary = extract_summary_parts(analysis_text)
                            
                            # Сохраняем саммари в базу данных
                            if save_to_db and db_manager and channel_id:
                                summary_id = db_manager.save_post_summary(
                                    channel_id=channel_id,
                                    telegram_message_id=message.id,
                                    sender_name=sender_name,
                                    sender_id=sender_id,
                                    summary=summary,
                                    main_idea=main_idea,
                                    date_published=message.date,
                                    views_count=message.views or 0,
                                    forwards_count=message.forwards or 0,
                                    replies_count=getattr(message.replies, 'replies', 0) if hasattr(message, 'replies') and message.replies is not None else 0
                                )
                                
                                if summary_id:
                                    stats.add_db_save()
                                    
                                    # Сохраняем реакции если есть
                                    if hasattr(message, 'reactions') and message.reactions:
                                        reactions_data = ReactionParser.parse_reactions(message.reactions)
                                        if reactions_data:
                                            # Нормализуем типы реакций
                                            normalized_reactions = {
                                                ReactionParser.normalize_reaction_type(k): v
                                                for k, v in reactions_data.items()
                                            }
                                            db_manager.save_reactions(summary_id, normalized_reactions)
                                else:
                                    stats.add_error()
                            
                            # Форматируем саммари для файла
                            date_str = message.date.strftime("%Y-%m-%d %H:%M:%S")
                            formatted_summary = f"""
[{date_str}] {sender_name}:
ГЛАВНАЯ МЫСЛЬ: {main_idea}

САММАРИ:
{summary}

Оригинальные метрики: Просмотры: {message.views or 0}, Репосты: {message.forwards or 0}
{'-' * 80}
"""
                            summaries_for_file.append(formatted_summary)
                            stats.add_file_save()
                            stats.add_summary_created()
                            
                            logger.debug(f"✅ Саммари создано для сообщения {message.id}")
                        else:
                            logger.error(f"❌ Получен пустой ответ от GPT для сообщения {message.id}")
                            stats.add_summary_failed()
                    else:
                        error_message = summary_result.get("error", "Неизвестная ошибка") if summary_result else "Нет ответа от API"
                        logger.error(f"❌ Ошибка создания саммари для сообщения {message.id}: {error_message}")
                        stats.add_summary_failed()
                    
                    # Пауза между запросами к API
                    await asyncio.sleep(1.0)
                    
                except Exception as e:
                    logger.error(f"❌ Исключение при создании саммари для сообщения {message.id}: {e}")
                    stats.add_summary_failed()
                    stats.add_error()
                
    except Exception as e:
        logger.error(f"Ошибка при получении сообщений: {e}")
        stats.add_error()
    
    # Записываем саммари в файл
    if summaries_for_file:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Экспорт саммари чата: {chat_title}\n")
                f.write(f"Дата экспорта: {current_date.replace('_', ' ')}\n")
                f.write(f"Количество саммари: {len(summaries_for_file)}\n")
                f.write(f"ID канала: {chat_entity.id}\n")
                f.write(f"Username: {chat_username or 'Не указан'}\n")
                f.write(f"Тип: {chat_type}\n")
                f.write("=" * 80 + "\n\n")
                
                for summary in summaries_for_file:
                    f.write(f"{summary}\n")
            
            logger.info(f"Экспорт завершен. Создано {len(summaries_for_file)} саммари в файле '{filename}'")
            print(f"Экспорт завершен. Создано {len(summaries_for_file)} саммари в файле '{filename}'")
            
            if save_to_db and channel_id:
                print(f"Сохранено саммари в базу данных: {stats.summaries_created}")
            
            return filename, stats
            
        except Exception as e:
            logger.error(f"Ошибка записи в файл: {e}")
            stats.add_error()
            return None, stats
    else:
        logger.warning("Нет саммари для экспорта или произошла ошибка.")
        print("Нет саммари для экспорта или произошла ошибка.")
        return None, stats

def parse_arguments():
    """
    Парсит аргументы командной строки
    """
    parser = argparse.ArgumentParser(description="Экспорт чатов Telegram с созданием саммари")
    parser.add_argument("--chat", help="ID, username или название чата для экспорта")
    parser.add_argument("--limit", type=int, help="Максимальное количество сообщений для экспорта")
    parser.add_argument("--output", help="Имя выходного файла (по умолчанию: auto)")
    parser.add_argument("--no-db", action="store_true", help="Не сохранять в базу данных")
    parser.add_argument("--db-only", action="store_true", help="Сохранять только в базу данных (без текстового файла)")
    parser.add_argument("--init-db", action="store_true", help="Инициализировать базу данных и выйти")
    parser.add_argument("--all-time", action="store_true", help="Экспортировать все сообщения (по умолчанию только за последние 24 часа)")
    return parser.parse_args()

async def main():
    # Парсим аргументы командной строки
    args = parse_arguments()
    
    # Инициализация базы данных
    db_manager = None
    if args.init_db:
        print("Инициализация базы данных...")
        db_manager = DatabaseManager()
        if db_manager.connect():
            if db_manager.create_tables():
                print("База данных успешно инициализирована!")
            else:
                print("Ошибка при создании таблиц")
            db_manager.disconnect()
        else:
            print("Ошибка подключения к базе данных")
        return
    
    # Проверяем, указаны ли API_ID и API_HASH
    if not API_ID or not API_HASH:
        print("Пожалуйста, укажите ваш API_ID и API_HASH в файле config.py или .env")
        print("Получить их можно на сайте https://my.telegram.org")
        return
    
    # Проверяем наличие токена Zeliboba
    if not ZELIBOBA_API_TOKEN:
        print("Ошибка: ZELIBOBA_API_TOKEN не настроен в .env файле")
        print("Для создания саммари необходим токен API Zeliboba")
        return
    
    # Подключение к базе данных (если не отключено)
    save_to_db = not args.no_db
    if save_to_db:
        db_manager = DatabaseManager()
        if not db_manager.connect():
            print("Предупреждение: Не удалось подключиться к базе данных. Продолжаем без сохранения в БД.")
            save_to_db = False
        else:
            # Создаем таблицы если их нет
            db_manager.create_tables()
    
    # Создаем клиент Telegram
    session_path = os.path.join(SCRIPT_DIR, SESSION_PATH + "_summary")
    client = TelegramClient(session_path, API_ID, API_HASH)
    
    try:
        # Подключаемся к Telegram
        await client.start()
        
        # Проверяем, авторизован ли пользователь
        if not await client.is_user_authorized():
            print("Требуется авторизация. Следуйте инструкциям в консоли.")
            while True:
                phone = input("Введите номер телефона (с кодом страны): ")
                if phone.strip():
                    break
                print("Номер телефона не может быть пустым. Пожалуйста, попробуйте снова.")
            
            await client.send_code_request(phone)
            
            while True:
                code = input('Введите код подтверждения: ')
                if code.strip():
                    break
                print("Код подтверждения не может быть пустым. Пожалуйста, попробуйте снова.")
            
            await client.sign_in(phone, code)
        
        chat_entity = None
        limit = None
        
        # Если указан чат в аргументах, используем его
        if args.chat:
            chat_entity = await get_entity_by_name_or_id(client, args.chat)
            if not chat_entity:
                print(f"Чат '{args.chat}' не найден. Пожалуйста, проверьте введенные данные.")
                return
        else:
            # Получаем список диалогов
            print("Получение списка диалогов...")
            dialogs = await client.get_dialogs()
            
            print("\nСписок доступных чатов:")
            for i, dialog in enumerate(dialogs[:30], 1):  # Показываем первые 30 диалогов
                chat_name = dialog.name or "Unnamed"
                chat_type = "Канал" if hasattr(dialog.entity, 'broadcast') else "Чат"
                print(f"{i}. {chat_name} (ID: {dialog.id}) - {chat_type}")
            
            # Запрашиваем у пользователя, какой чат экспортировать
            choice = input("\nВведите номер чата из списка или ID/username чата: ")
            
            if choice.isdigit() and 1 <= int(choice) <= len(dialogs):
                # Выбор из списка
                chat_entity = dialogs[int(choice) - 1].entity
            else:
                # Поиск по ID или username
                chat_entity = await get_entity_by_name_or_id(client, choice)
            
            if not chat_entity:
                print("Чат не найден. Пожалуйста, проверьте введенные данные.")
                return
        
        # Определяем количество сообщений для экспорта
        if args.limit:
            limit = args.limit
        else:
            # Запрашиваем количество сообщений для экспорта
            limit_input = input("Введите максимальное количество сообщений для обработки (или нажмите Enter для обработки всех): ")
            try:
                limit = int(limit_input) if limit_input.strip() else None
            except ValueError:
                print("Введено некорректное число. Будут обработаны все сообщения.")
                limit = None
        
        # Экспортируем историю чата с созданием саммари
        output_file = None if args.db_only else (args.output if args.output else None)
        last_24_hours_only = not args.all_time  # По умолчанию только последние 24 часа, если не указан --all-time
        filename, stats = await export_chat_with_summaries(
            client,
            chat_entity,
            limit=limit,
            output_file=output_file,
            save_to_db=save_to_db,
            db_manager=db_manager,
            last_24_hours_only=last_24_hours_only
        )
        
        # Выводим статистику
        print("\n" + "="*50)
        print(stats.get_summary())
        
        if filename:
            print(f"\nФайл с саммари сохранен: {filename}")
        
        if save_to_db and db_manager:
            # Получаем статистику канала из БД
            try:
                # Получаем ID канала по telegram_id
                channel_info = db_manager.get_channel_by_telegram_id(chat_entity.id)
                if channel_info:
                    channel_stats = db_manager.get_channel_stats(channel_info[0])  # channel_info[0] это ID канала
                    if channel_stats:
                        print(f"Статистика канала в БД: {channel_stats}")
            except Exception as e:
                logger.warning(f"Не удалось получить статистику канала: {e}")
        
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        print(f"Произошла ошибка: {e}")
    finally:
        # Закрываем соединения
        await client.disconnect()
        if db_manager:
            db_manager.disconnect()

if __name__ == "__main__":
    print("🔄 Экспортер Telegram с созданием саммари")
    print("Этот скрипт создает краткие саммари постов вместо сохранения полных текстов")
    print("Требуется настроенный ZELIBOBA_API_TOKEN в .env файле")
    print("=" * 60)
    
    # Запускаем асинхронную функцию main
    asyncio.run(main())