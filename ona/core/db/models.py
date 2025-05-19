from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NatalData(BaseModel):
    """
    Модель для хранения натальных данных пользователя
    """
    birth_date: str
    birth_time: Optional[str] = None
    birth_place: str
    age: int

class UserProfile(BaseModel):
    """
    Модель для хранения профиля пользователя
    """
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    natal_data: Optional[NatalData] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now) 