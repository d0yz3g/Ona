"""
Сервис для работы с медитациями
"""
import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime
from core.services.elevenlabs_service import elevenlabs_service
from core.services.recommendation_service import recommendation_service
from core.db.supabase_client import supabase

logger = logging.getLogger(__name__)

class MeditationService:
    """
    Сервис для работы с медитациями
    """
    def __init__(self):
        """
        Инициализация сервиса медитаций
        """
        self.elevenlabs_service = elevenlabs_service
        self.recommendation_service = recommendation_service
        
        # Директория для хранения аудиофайлов
        self.audio_dir = "audio"
        os.makedirs(self.audio_dir, exist_ok=True)
    
    async def generate_meditation_audio(
        self,
        telegram_id: int,
        practice_type: str = "mindfulness"
    ) -> Optional[str]:
        """
        Генерация аудиомедитации
        
        Args:
            telegram_id: Telegram ID пользователя
            practice_type: Тип практики
            
        Returns:
            Optional[str]: Путь к аудиофайлу или None в случае ошибки
        """
        try:
            # Генерируем текст медитации
            meditation_text = await self.recommendation_service.generate_practice(
                telegram_id,
                practice_type
            )
            
            if not meditation_text:
                logger.error("Не удалось сгенерировать текст медитации")
                return None
            
            # Генерируем аудио
            audio_data = await self.elevenlabs_service.generate_audio(meditation_text)
            
            if not audio_data:
                logger.error("Не удалось сгенерировать аудио")
                return None
            
            # Создаем имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{telegram_id}_{practice_type}_{timestamp}.mp3"
            filepath = os.path.join(self.audio_dir, filename)
            
            # Сохраняем аудиофайл
            with open(filepath, "wb") as f:
                f.write(audio_data)
            
            # Сохраняем информацию о медитации в базу данных
            await self.save_meditation(telegram_id, practice_type, meditation_text, filename)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Ошибка при генерации аудиомедитации: {e}")
            return None
    
    async def save_meditation(
        self,
        telegram_id: int,
        practice_type: str,
        text: str,
        audio_filename: str
    ) -> bool:
        """
        Сохранение информации о медитации в базу данных
        
        Args:
            telegram_id: Telegram ID пользователя
            practice_type: Тип практики
            text: Текст медитации
            audio_filename: Имя аудиофайла
            
        Returns:
            bool: True если медитация успешно сохранена
        """
        try:
            # Получаем ID пользователя
            user_result = supabase.table("users").select("id").eq("telegram_id", telegram_id).execute()
            
            if not user_result.data:
                logger.error(f"Пользователь с telegram_id {telegram_id} не найден")
                return False
            
            user_id = user_result.data[0]["id"]
            
            # Сохраняем медитацию
            meditation_data = {
                "user_id": user_id,
                "type": practice_type,
                "text": text,
                "audio_filename": audio_filename,
                "created_at": datetime.now().isoformat()
            }
            
            response = supabase.table("meditations").insert(meditation_data).execute()
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении медитации: {e}")
            return False

# Создание экземпляра сервиса
meditation_service = MeditationService() 