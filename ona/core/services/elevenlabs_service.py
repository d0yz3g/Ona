"""
Сервис для работы с 11Labs API
"""
import os
import logging
import aiohttp
from typing import Optional, Dict, Any
from core.config import settings

logger = logging.getLogger(__name__)

class ElevenLabsService:
    """
    Сервис для работы с 11Labs API
    """
    def __init__(self):
        """
        Инициализация сервиса 11Labs
        """
        if not settings.ELEVENLABS_API_KEY:
            raise ValueError("Не указан API ключ 11Labs")
            
        self.api_key = settings.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        # ID голоса для медитаций (Rachel - спокойный, умиротворяющий голос)
        self.voice_id = settings.ELEVENLABS_VOICE_ID
        
        # Параметры генерации по умолчанию
        self.default_params = {
            "model_id": settings.ELEVENLABS_MODEL_ID,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        # Проверяем доступность API
        self._check_api_availability()
    
    async def _check_api_availability(self):
        """
        Проверка доступности API
        """
        try:
            voices = await self.get_voices()
            if not voices:
                raise ValueError("Не удалось получить список голосов от 11Labs API")
            logger.info("11Labs API доступен")
        except Exception as e:
            logger.error(f"Ошибка при проверке доступности 11Labs API: {e}")
            raise
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Выполнение запроса к API
        
        Args:
            method: HTTP метод
            endpoint: Эндпоинт API
            data: Данные для отправки
            params: Параметры запроса
            
        Returns:
            Optional[Dict[str, Any]]: Ответ от API или None в случае ошибки
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Ошибка при запросе к 11Labs API: {response.status} - {error_text}"
                        )
                        return None
                        
        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса к 11Labs API: {e}")
            return None
    
    async def get_voices(self) -> Optional[Dict[str, Any]]:
        """
        Получение списка доступных голосов
        
        Returns:
            Optional[Dict[str, Any]]: Список голосов или None в случае ошибки
        """
        return await self._make_request("GET", "voices")
    
    async def get_voice(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение информации о конкретном голосе
        
        Args:
            voice_id: ID голоса
            
        Returns:
            Optional[Dict[str, Any]]: Информация о голосе или None в случае ошибки
        """
        return await self._make_request("GET", f"voices/{voice_id}")
    
    async def generate_audio(
        self,
        text: str,
        voice_id: Optional[str] = None,
        model_id: Optional[str] = None,
        voice_settings: Optional[Dict[str, Any]] = None
    ) -> Optional[bytes]:
        """
        Генерация аудио из текста
        
        Args:
            text: Текст для озвучивания
            voice_id: ID голоса (если None, используется голос по умолчанию)
            model_id: ID модели (если None, используется модель по умолчанию)
            voice_settings: Настройки голоса (если None, используются настройки по умолчанию)
            
        Returns:
            Optional[bytes]: Аудио в формате MP3 или None в случае ошибки
        """
        url = f"{self.base_url}/text-to-speech/{voice_id or self.voice_id}"
        
        data = {
            "text": text,
            "model_id": model_id or self.default_params["model_id"],
            "voice_settings": voice_settings or self.default_params["voice_settings"]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=url,
                    headers=self.headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Ошибка при генерации аудио: {response.status} - {error_text}"
                        )
                        return None
                        
        except Exception as e:
            logger.error(f"Ошибка при генерации аудио: {e}")
            return None

# Создание экземпляра сервиса
elevenlabs_service = ElevenLabsService() 