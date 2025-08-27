import os
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import asyncio
import csv
from datetime import datetime

# Загрузка конфигурации
load_dotenv()

class TelegramExporter:
    def __init__(self):
        self.api_id = os.getenv('API_ID')
        self.api_hash = os.getenv('API_HASH')
        self.phone = os.getenv('PHONE')
        self.session_name = os.getenv('SESSION_NAME')
        self.client = None
        
    async def connect(self):
        """Подключение к Telegram API"""
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        await self.client.start(self.phone)
        
    async def get_chats(self):
        """Получение списка чатов"""
        if not self.client:
            await self.connect()
            
        dialogs = await self.client.get_dialogs()
        return dialogs
        
    async def export_messages(self, chat_id, limit=100):
        """Экспорт сообщений из чата"""
        messages = await self.client.get_messages(chat_id, limit=limit)
        return messages
        
    def format_message(self, message, chat_name):
        """Форматирование сообщения для CSV с учетом разных типов"""
        msg_type = 'text'
        content = message.text or ''
        
        if message.photo:
            msg_type = 'photo'
            content = f"photo_{message.id}"
        elif message.document:
            msg_type = 'document'
            content = f"{message.document.mime_type} ({message.file.name or 'unnamed'})"
        elif message.sticker:
            msg_type = 'sticker'
            content = f"sticker_{message.sticker.id}"
        elif message.action:
            msg_type = 'action'
            content = str(message.action)
            
        return {
            'date': message.date.strftime('%Y-%m-%d %H:%M:%S'),
            'sender': self._get_sender_name(message.sender),
            'type': msg_type,
            'text': content,
            'chat': chat_name
        }
        
    def _get_sender_name(self, sender):
        """Получение имени отправителя"""
        if not sender:
            return 'System'
        if hasattr(sender, 'first_name'):
            return f"{sender.first_name} {sender.last_name or ''}".strip()
        return sender.title or str(sender.id)

    async def export_to_csv(self, chat_id, limit=100, filename='export.csv'):
        """Экспорт сообщений в CSV файл"""
        messages = await self.export_messages(chat_id, limit)
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['date', 'sender', 'type', 'text', 'chat']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            chat_name = await self.client.get_entity(chat_id)
            for message in messages:
                formatted = self.format_message(message, chat_name.title)
                writer.writerow(formatted)

async def select_chat_interactive(exporter):
    """Интерактивный выбор чата"""
    dialogs = await exporter.get_chats()
    
    print("Доступные чаты:")
    for i, dialog in enumerate(dialogs):
        print(f"{i+1}. {dialog.name} ({dialog.id})")
    
    while True:
        try:
            choice = int(input("Выберите номер чата для экспорта: ")) - 1
            if 0 <= choice < len(dialogs):
                return dialogs[choice]
            print("Неверный номер, попробуйте снова")
        except ValueError:
            print("Введите число")

async def main(exporter: TelegramExporter) -> None:
    try:
        await exporter.connect()
        chat = await select_chat_interactive(exporter)
        limit = int(input(f"Сколько сообщений экспортировать? (по умолчанию {os.getenv('DEFAULT_LIMIT')}): ")
                   or os.getenv('DEFAULT_LIMIT'))
        
        filename = f"chat_export_{chat.id}.csv"
        print(f"Начинаю экспорт {limit} сообщений из чата '{chat.name}'...")
        await exporter.export_to_csv(chat.id, limit, filename)
        print(f"Экспорт завершен. Сохранено в {filename}")
        
    except SessionPasswordNeededError:
        print("Требуется двухфакторная аутентификация. Введите пароль:")
        password = input()
        await exporter.client.sign_in(password=password)
        await main(exporter)
    except Exception as e:
        print(f"Ошибка при экспорте: {str(e)}")
    finally:
        await exporter.client.disconnect()

async def run():
    exporter = TelegramExporter()
    await main(exporter)

if __name__ == '__main__':
    asyncio.run(run())