"""
Конфигурация тестового окружения
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from core.config import settings
from core.services.elevenlabs_service import ElevenLabsService

@pytest.fixture(scope="session")
def event_loop():
    """
    Создание event loop для асинхронных тестов
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_elevenlabs_service():
    """
    Мок сервиса 11Labs
    """
    service = AsyncMock(spec=ElevenLabsService)
    
    # Настройка моков для методов
    service.get_voices.return_value = {
        "voices": [
            {
                "voice_id": "21m00Tcm4TlvDq8ikWAM",
                "name": "Rachel",
                "category": "premade"
            }
        ]
    }
    
    service.generate_audio.return_value = b"mock_audio_data"
    
    return service

@pytest.fixture
def mock_settings():
    """
    Мок настроек приложения
    """
    return MagicMock(
        ELEVENLABS_API_KEY="test_key",
        ELEVENLABS_VOICE_ID="21m00Tcm4TlvDq8ikWAM",
        ELEVENLABS_MODEL_ID="eleven_monolingual_v1"
    ) 