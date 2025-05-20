import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

class Settings:
    """
    Класс с настройками приложения, доступными как атрибуты
    """
    # Конфигурация Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

    # Конфигурация OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Конфигурация Telegram бота
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # Конфигурация 11Labs
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

    # Настройки приложения
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

    # Настройки платежной системы
    PAYMENT_PROVIDER_KEY = os.getenv("PAYMENT_PROVIDER_KEY", "")

    # YooKassa API settings
    YOOKASSA_SHOP_ID: str = os.getenv("YOOKASSA_SHOP_ID", "")
    YOOKASSA_API_KEY: str = os.getenv("YOOKASSA_API_KEY", "")

# Создаем экземпляр настроек для импорта в других модулях
settings = Settings()

# Для обратной совместимости с существующим кодом сохраняем переменные на уровне модуля
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_KEY = settings.SUPABASE_KEY
OPENAI_API_KEY = settings.OPENAI_API_KEY
TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
ELEVENLABS_API_KEY = settings.ELEVENLABS_API_KEY
DEBUG = settings.DEBUG
ENVIRONMENT = settings.ENVIRONMENT
PAYMENT_PROVIDER_KEY = settings.PAYMENT_PROVIDER_KEY
YOOKASSA_SHOP_ID = settings.YOOKASSA_SHOP_ID
YOOKASSA_API_KEY = settings.YOOKASSA_API_KEY 
