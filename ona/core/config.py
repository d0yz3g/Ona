"""
Конфигурация приложения
"""
import os
import logging
from pydantic_settings import BaseSettings
from pydantic import validator

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """
    Настройки приложения
    """
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # 11Labs
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Rachel
    ELEVENLABS_MODEL_ID: str = os.getenv("ELEVENLABS_MODEL_ID", "eleven_monolingual_v1")
    
    @validator("OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY", "TELEGRAM_BOT_TOKEN", "ELEVENLABS_API_KEY")
    def validate_api_keys(cls, v, field):
        """
        Валидация API-ключей
        
        Args:
            v: Значение поля
            field: Имя поля
            
        Returns:
            str: Значение поля
            
        Raises:
            ValueError: Если ключ не указан
        """
        if not v:
            logger.error(f"Не указан {field.name}")
            raise ValueError(f"Не указан {field.name}")
        return v
    
    class Config:
        env_file = ".env"

# Создание экземпляра настроек
settings = Settings() 