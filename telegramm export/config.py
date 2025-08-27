import os
from dotenv import load_dotenv
from typing import Dict, Any

# Загрузка переменных окружения
load_dotenv()

def get_required_env(key: str, is_sensitive: bool = False) -> str:
    """Получение обязательной переменной окружения
    
    Args:
        key: Имя переменной окружения
        is_sensitive: Если True, скрывает значение в логах
    """
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Не задана обязательная переменной окружения: {key}")
    if is_sensitive and len(value) > 4:
        return f"{value[:2]}...{value[-2:]}"
    return value

# Telegram API Settings
TELEGRAM_API_ID = int(get_required_env('TELEGRAM_API_ID'))
TELEGRAM_API_HASH = get_required_env('TELEGRAM_API_HASH')
SESSION_PATH = os.getenv('SESSION_PATH', 'telegram_exporter')

# Database Settings
DATABASE_CONFIG: Dict[str, Any] = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'telegram_export'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

# Export Settings
DEFAULT_EXPORT_DIR = os.getenv('EXPORT_DIR', 'Chats')
SUMMARY_CHANNEL_USERNAME = os.getenv('SUMMARY_CHANNEL_USERNAME')

# AI API Settings
class AISettings:
    ELIZA = {
        'api_token': os.getenv('ELIZA_API_TOKEN'),
        'base_url': os.getenv('ELIZA_BASE_URL', 'https://api.eliza.yandex.net'),
        'model': os.getenv('ELIZA_MODEL', 'gpt-4.1-nano'),
        'temperature': float(os.getenv('ELIZA_TEMPERATURE', '0.7')),
        'max_tokens': int(os.getenv('ELIZA_MAX_TOKENS', '1000'))
    }
    
    ZELIBOBA = {
        'api_token': os.getenv('ZELIBOBA_API_TOKEN'),
        'base_url': os.getenv('ZELIBOBA_BASE_URL'),
        'model': os.getenv('ZELIBOBA_MODEL', 'zeliboba-3.5'),
        'temperature': float(os.getenv('ZELIBOBA_TEMPERATURE', '0.7'))
    }

# Validate required settings
def validate_sensitive_data():
    """Проверка наличия всех критичных переменных окружения"""
    required_vars = {
        'TELEGRAM_API_ID': False,
        'TELEGRAM_API_HASH': True,
        'DB_PASSWORD': True,
        'SOY_TOKEN': True
    }
    
    missing = []
    for var, is_sensitive in required_vars.items():
        if not os.getenv(var):
            missing.append(var)
        elif is_sensitive:
            # Логируем только факт наличия чувствительных данных
            print(f"{var} is set (value hidden)")
    
    if missing:
        raise ValueError(f"Отсутствуют обязательные переменные: {', '.join(missing)}")

if not DATABASE_CONFIG['password']:
    raise ValueError("Не задан пароль для базы данных")

if not AISettings.ELIZA['api_token'] and not AISettings.ZELIBOBA['api_token']:
    raise ValueError("Не задан хотя бы один API токен (Eliza или Zeliboba)")

# Дополнительная валидация при запуске
validate_sensitive_data()