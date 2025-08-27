#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Программа для экспорта чатов Telegram в текстовый файл и базу данных PostgreSQL.
Для работы требуется API ID и API Hash от Telegram.
Получить их можно на сайте https://my.telegram.org
"""

import os
import sys
import asyncio
import datetime
import argparse
import subprocess
import importlib.util
import logging
from typing import Optional

# Получаем директорию, в которой находится скрипт
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_export.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Функция для проверки наличия модуля
def is_module_installed(module_name):
    """Проверяет, установлен ли модуль"""
    return importlib.util.find_spec(module_name) is not None

# Функция для установки telethon
def install_telethon():
    """Устанавливает модуль telethon"""
    print("Попытка установить telethon...")
    
    # Проверяем, запущен ли скрипт из виртуального окружения
    in_venv = sys.prefix != sys.base_prefix
    
    if in_venv:
        print("Скрипт запущен из виртуального окружения. Устанавливаем telethon...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "telethon"])
            print("telethon успешно установлен!")
            return True
        except Exception as e:
            print(f"Ошибка при установке telethon: {e}")
    else:
        print("Скрипт запущен не из виртуального окружения.")
        venv_path = os.path.join(SCRIPT_DIR, "telegram_venv")
        
        if os.path.exists(venv_path):
            print(f"Найдено виртуальное окружение в {venv_path}")
            
            # Определяем путь к python в виртуальном окружении
            if sys.platform == "win32":
                python_path = os.path.join(venv_path, "Scripts", "python")
                activate_cmd = os.path.join(venv_path, "Scripts", "activate")
            else:
                python_path = os.path.join(venv_path, "bin", "python")
                activate_cmd = os.path.join(venv_path, "bin", "activate")
            
            print(f"Для использования виртуального окружения выполните:")
            print(f"source {activate_cmd} && python telegram_chat_exporter.py")
        else:
            print("Виртуальное окружение не найдено.")
            print("Запустите скрипт настройки для создания виртуального окружения:")
            print("python3 setup_telegram_exporter.py")
        
        print("\nАльтернативно, вы можете установить telethon глобально (не рекомендуется):")
        print("python3 -m pip install telethon --user")
    
    return False

# Проверка наличия модуля telethon
telethon_installed = is_module_installed("telethon")

if not telethon_installed:
    print("Ошибка: Модуль telethon не установлен.")
    
    # Спрашиваем пользователя, хочет ли он установить telethon
    choice = input("Хотите попробовать установить telethon сейчас? (y/n): ")
    
    if choice.lower() == 'y':
        if install_telethon():
            # Пробуем импортировать снова после установки
            try:
                # Перезагружаем sys.path, чтобы найти только что установленный модуль
                import site
                import importlib
                importlib.reload(site)
                
                from telethon import TelegramClient, events
                from telethon.tl.types import InputPeerChannel, InputPeerChat, InputPeerUser
                print("Модуль telethon успешно импортирован!")
            except ImportError:
                print("Не удалось импортировать telethon после установки.")
                print("Пожалуйста, перезапустите скрипт после активации виртуального окружения.")
                sys.exit(1)
        else:
            sys.exit(1)
    else:
        sys.exit(1)
else:
    # Импортируем telethon, если он установлен
    from telethon import TelegramClient, events
    from telethon.tl.types import InputPeerChannel, InputPeerChat, InputPeerUser

# Импорт наших модулей
try:
    from config import (TELEGRAM_API_ID, TELEGRAM_API_HASH, SESSION_PATH, DEFAULT_EXPORT_DIR)
    from database import DatabaseManager
    from models import (Channel, Post, ReactionParser, MessageProcessor, ExportStats)
except ImportError as e:
    logger.error(f"Ошибка импорта модулей: {e}")
    print("Убедитесь, что все необходимые файлы находятся в директории скрипта")
    sys.exit(1)

# Настройки API Telegram (для обратной совместимости)
API_ID = TELEGRAM_API_ID
API_HASH = TELEGRAM_API_HASH

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

async def export_chat_history(client, chat_entity, limit=None, offset_date=None, output_file=None,
                             save_to_db=True, db_manager=None, last_24_hours_only=True):
    """
    Экспортирует историю сообщений из указанного чата в файл и базу данных
    
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
    stats = ExportStats()
    stats.add_channel()
    
    # Анализ контента отключен
    logger.info("Анализ контента через Zeliboba отключен")
    
    # Получаем информацию о чате
    chat_title = getattr(chat_entity, 'title', None) or getattr(chat_entity, 'first_name', None)
    if not chat_title:
        chat_title = f"chat_{chat_entity.id}"
    
    chat_username = getattr(chat_entity, 'username', None)
    chat_type = 'channel' if hasattr(chat_entity, 'broadcast') else 'chat'
    
    logger.info(f"Начинаем экспорт чата: {chat_title} (ID: {chat_entity.id})")
    
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
        
        filename = os.path.join(chats_dir, f"{safe_title}_{current_date}.txt")
    
    print(f"Экспорт чата '{chat_title}' в файл '{filename}'...")
    
    # Вычисляем дату для фильтрации (24 часа назад)
    if last_24_hours_only and not offset_date:
        offset_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)
        print(f"Экспортируем только сообщения за последние 24 часа (с {offset_date.strftime('%Y-%m-%d %H:%M:%S UTC')})")
    
    # Получаем сообщения
    messages_for_file = []
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
            
            if processed_count % 100 == 0:
                print(f"Обработано {processed_count} сообщений...")
            
            if message.text:
                # Обработка сообщения для сохранения в БД
                if save_to_db and db_manager and channel_id:
                    post = MessageProcessor.extract_message_data(message, channel_id)
                    if post:
                        post_id = db_manager.save_post(
                            post.channel_id,
                            post.telegram_message_id,
                            post.sender_name,
                            post.sender_id,
                            post.content,
                            post.date_published,
                            post.views_count,
                            post.forwards_count,
                            post.replies_count
                        )
                        
                        if post_id:
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
                                    db_manager.save_reactions(post_id, normalized_reactions)
                        else:
                            stats.add_error()
                        
                        # Анализ контента отключен
                        logger.debug(f"Анализ контента для поста {post_id} отключен")
                
                # Обработка сообщения для сохранения в файл
                sender = message.sender
                sender_name = "Unknown"
                if sender:
                    sender_name = getattr(sender, 'first_name', '') or ''
                    if getattr(sender, 'last_name', ''):
                        sender_name += f" {sender.last_name}"
                    if not sender_name and getattr(sender, 'title', ''):
                        sender_name = sender.title
                    if not sender_name:
                        sender_name = f"User {sender.id}"
                
                formatted_message = MessageProcessor.format_message_for_file(message, sender_name)
                messages_for_file.append(formatted_message)
                stats.add_file_save()
                
    except Exception as e:
        logger.error(f"Ошибка при получении сообщений: {e}")
        stats.add_error()
    
    # Записываем сообщения в файл
    if messages_for_file:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Экспорт чата: {chat_title}\n")
                f.write(f"Дата экспорта: {current_date.replace('_', ' ')}\n")
                f.write(f"Количество сообщений: {len(messages_for_file)}\n")
                f.write(f"ID канала: {chat_entity.id}\n")
                f.write(f"Username: {chat_username or 'Не указан'}\n")
                f.write(f"Тип: {chat_type}\n")
                f.write("-" * 50 + "\n\n")
                
                for message in messages_for_file:
                    f.write(f"{message}\n")
            
            logger.info(f"Экспорт завершен. Сохранено {len(messages_for_file)} сообщений в файл '{filename}'")
            print(f"Экспорт завершен. Сохранено {len(messages_for_file)} сообщений в файл '{filename}'")
            
            if save_to_db and channel_id:
                print(f"Сохранено в базу данных: {stats.saved_to_db} сообщений")
            
            return filename, stats
            
        except Exception as e:
            logger.error(f"Ошибка записи в файл: {e}")
            stats.add_error()
            return None, stats
    else:
        logger.warning("Нет сообщений для экспорта или произошла ошибка.")
        print("Нет сообщений для экспорта или произошла ошибка.")
        return None, stats

def parse_arguments():
    """
    Парсит аргументы командной строки
    """
    parser = argparse.ArgumentParser(description="Экспорт чатов Telegram в текстовый файл и базу данных")
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
    session_path = os.path.join(SCRIPT_DIR, SESSION_PATH)
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
            limit_input = input("Введите максимальное количество сообщений для экспорта (или нажмите Enter для экспорта всех сообщений): ")
            try:
                limit = int(limit_input) if limit_input.strip() else None
            except ValueError:
                print("Введено некорректное число. Будут экспортированы все сообщения.")
                limit = None
        
        # Экспортируем историю чата
        output_file = None if args.db_only else (args.output if args.output else None)
        last_24_hours_only = not args.all_time  # По умолчанию только последние 24 часа, если не указан --all-time
        filename, stats = await export_chat_history(
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
            print(f"\nТекстовый файл сохранен: {filename}")
        
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
    # Проверяем, запущен ли скрипт из виртуального окружения
    in_venv = sys.prefix != sys.base_prefix
    if not in_venv:
        print("Предупреждение: Скрипт запущен не из виртуального окружения.")
        print("Для лучшей работы рекомендуется использовать виртуальное окружение:")
        print("1. Создайте виртуальное окружение: python3 -m venv telegram_venv")
        print("2. Активируйте его: source telegram_venv/bin/activate")
        print("3. Установите зависимости: python3 -m pip install telethon")
        print("4. Запустите скрипт снова")
        
        # Спрашиваем пользователя, хочет ли он продолжить
        choice = input("\nПродолжить без виртуального окружения? (y/n): ")
        if choice.lower() != 'y':
            sys.exit(0)
    
    # Запускаем асинхронную функцию main
    asyncio.run(main())