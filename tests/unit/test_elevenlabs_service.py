"""
Юнит-тесты для сервиса 11Labs
"""
import pytest
from unittest.mock import patch, AsyncMock
from core.services.elevenlabs_service import ElevenLabsService

@pytest.mark.asyncio
async def test_elevenlabs_service_initialization():
    """
    Тест инициализации сервиса 11Labs
    """
    with patch("core.services.elevenlabs_service.settings") as mock_settings:
        mock_settings.ELEVENLABS_API_KEY = "test_key"
        mock_settings.ELEVENLABS_VOICE_ID = "test_voice"
        mock_settings.ELEVENLABS_MODEL_ID = "test_model"
        
        service = ElevenLabsService()
        
        assert service.api_key == "test_key"
        assert service.voice_id == "test_voice"
        assert service.default_params["model_id"] == "test_model"

@pytest.mark.asyncio
async def test_get_voices(mock_elevenlabs_service):
    """
    Тест получения списка голосов
    """
    voices = await mock_elevenlabs_service.get_voices()
    
    assert voices is not None
    assert "voices" in voices
    assert len(voices["voices"]) > 0
    assert voices["voices"][0]["voice_id"] == "21m00Tcm4TlvDq8ikWAM"

@pytest.mark.asyncio
async def test_get_voice(mock_elevenlabs_service):
    """
    Тест получения информации о конкретном голосе
    """
    voice_id = "21m00Tcm4TlvDq8ikWAM"
    voice = await mock_elevenlabs_service.get_voice(voice_id)
    
    assert voice is not None
    assert "voice_id" in voice
    assert voice["voice_id"] == voice_id

@pytest.mark.asyncio
async def test_generate_audio(mock_elevenlabs_service):
    """
    Тест генерации аудио
    """
    text = "Тестовый текст для озвучивания"
    audio = await mock_elevenlabs_service.generate_audio(text)
    
    assert audio is not None
    assert isinstance(audio, bytes)
    assert audio == b"mock_audio_data"

@pytest.mark.asyncio
async def test_generate_audio_with_custom_params(mock_elevenlabs_service):
    """
    Тест генерации аудио с пользовательскими параметрами
    """
    text = "Тестовый текст"
    voice_id = "custom_voice"
    model_id = "custom_model"
    voice_settings = {
        "stability": 0.7,
        "similarity_boost": 0.8
    }
    
    audio = await mock_elevenlabs_service.generate_audio(
        text=text,
        voice_id=voice_id,
        model_id=model_id,
        voice_settings=voice_settings
    )
    
    assert audio is not None
    assert isinstance(audio, bytes)
    assert audio == b"mock_audio_data"

@pytest.mark.asyncio
async def test_error_handling(mock_elevenlabs_service):
    """
    Тест обработки ошибок
    """
    # Настраиваем мок на возврат ошибки
    mock_elevenlabs_service.get_voices.return_value = None
    
    voices = await mock_elevenlabs_service.get_voices()
    assert voices is None 