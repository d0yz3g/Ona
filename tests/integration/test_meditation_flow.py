"""
Интеграционные тесты для потока медитаций
"""
import pytest
from unittest.mock import patch, AsyncMock
from core.services.elevenlabs_service import ElevenLabsService
from core.services.meditation_service import MeditationService

@pytest.mark.asyncio
async def test_meditation_generation_flow():
    """
    Тест полного потока генерации медитации
    """
    # Мокаем сервис 11Labs
    with patch("core.services.meditation_service.elevenlabs_service") as mock_elevenlabs:
        # Настраиваем мок
        mock_elevenlabs.generate_audio.return_value = b"mock_audio_data"
        
        # Создаем сервис медитаций
        meditation_service = MeditationService()
        
        # Генерируем медитацию
        meditation_text = "Спокойная медитация для расслабления"
        audio_data = await meditation_service.generate_meditation(meditation_text)
        
        # Проверяем результаты
        assert audio_data is not None
        assert isinstance(audio_data, bytes)
        assert audio_data == b"mock_audio_data"
        
        # Проверяем, что сервис 11Labs был вызван с правильными параметрами
        mock_elevenlabs.generate_audio.assert_called_once()

@pytest.mark.asyncio
async def test_meditation_save_flow():
    """
    Тест сохранения медитации
    """
    # Мокаем сервисы
    with patch("core.services.meditation_service.elevenlabs_service") as mock_elevenlabs, \
         patch("core.services.meditation_service.supabase") as mock_supabase:
        
        # Настраиваем моки
        mock_elevenlabs.generate_audio.return_value = b"mock_audio_data"
        mock_supabase.table().insert().execute.return_value.data = [{"id": 1}]
        
        # Создаем сервис медитаций
        meditation_service = MeditationService()
        
        # Генерируем и сохраняем медитацию
        meditation_text = "Медитация для сна"
        result = await meditation_service.generate_and_save_meditation(
            user_id=123,
            text=meditation_text,
            type="sleep"
        )
        
        # Проверяем результаты
        assert result is not None
        assert "id" in result
        assert result["id"] == 1
        
        # Проверяем вызовы сервисов
        mock_elevenlabs.generate_audio.assert_called_once()
        mock_supabase.table().insert().execute.assert_called_once()

@pytest.mark.asyncio
async def test_meditation_error_handling():
    """
    Тест обработки ошибок при генерации медитации
    """
    # Мокаем сервис 11Labs для возврата ошибки
    with patch("core.services.meditation_service.elevenlabs_service") as mock_elevenlabs:
        mock_elevenlabs.generate_audio.return_value = None
        
        # Создаем сервис медитаций
        meditation_service = MeditationService()
        
        # Пытаемся сгенерировать медитацию
        meditation_text = "Медитация для стресса"
        audio_data = await meditation_service.generate_meditation(meditation_text)
        
        # Проверяем, что получили None при ошибке
        assert audio_data is None 