from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime

# Загрузка переменных окружения
load_dotenv()

# Получение конфигурации Supabase из переменных окружения
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Создание клиента Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY, options={"schema": "public"})  

# Функции для работы с пользователями
async def get_user_by_telegram_id(telegram_id: int):
    """
    Получение пользователя по его Telegram ID
    """
    response = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

async def create_user(telegram_id: int, first_name: str = None, last_name: str = None, username: str = None):
    """
    Создание нового пользователя
    """
    user_data = {
        "telegram_id": telegram_id,
        "first_name": first_name,
        "last_name": last_name,
        "username": username
    }
    response = supabase.table("users").insert(user_data).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

# Функции для работы с профилями
async def get_profile(user_id: int):
    """
    Получение профиля пользователя
    """
    response = supabase.table("profiles").select("*").eq("user_id", user_id).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

async def create_profile(profile_data: dict):
    """
    Создание нового профиля пользователя
    """
    # Добавляем время создания и обновления
    if "created_at" not in profile_data:
        profile_data["created_at"] = datetime.now().isoformat()
    if "updated_at" not in profile_data:
        profile_data["updated_at"] = datetime.now().isoformat()
    
    response = supabase.table("profiles").insert(profile_data).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

async def update_profile(user_id: int, profile_data: dict):
    """
    Обновление профиля пользователя
    
    Args:
        user_id: ID пользователя
        profile_data: Новые данные профиля
    """
    # Добавляем время обновления
    if "updated_at" not in profile_data:
        profile_data["updated_at"] = datetime.now().isoformat()
    
    response = supabase.table("profiles").update(profile_data).eq("user_id", user_id).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

# Функции для работы с историей диалогов
async def save_message(user_id: int, message_text: str, is_user: bool = True):
    """
    Сохранение сообщения в истории диалогов
    """
    message_data = {
        "user_id": user_id,
        "message_text": message_text,
        "is_user": is_user
    }
    response = supabase.table("conversations").insert(message_data).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

async def get_user_conversation_history(user_id: int, limit: int = 10):
    """
    Получение истории диалогов пользователя
    """
    response = supabase.table("conversations") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .limit(limit) \
        .execute()
    return response.data if response.data else [] 
