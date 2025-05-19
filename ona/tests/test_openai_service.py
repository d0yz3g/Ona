"""
Тесты для сервиса OpenAI
"""
import pytest
import os
from unittest import mock
from core.services.openai_service import OpenAIService
import openai
from config.settings import settings

@pytest.mark.asyncio
async def test_check_api_connection_success():
    """
    Тест успешного подключения к API OpenAI
    """
    # Мокаем openai.AsyncClient для тестирования без реального API ключа
    with mock.patch('openai.AsyncClient') as mock_async_client:
        # Настраиваем мок
        mock_client_instance = mock.AsyncMock()
        mock_client_instance.models.list = mock.AsyncMock(return_value=[])
        mock_async_client.return_value = mock_client_instance
        
        # Проверяем установку API ключа
        with mock.patch('openai.api_key', None):
            # Создаем экземпляр сервиса с моком
            service = OpenAIService()
            
            # Проверяем что API ключ был установлен
            assert openai.api_key is not None
        
        # Проверяем что соединение успешно
        result = await service.check_api_connection()
        assert result is True
        
        # Проверяем что был вызван нужный метод
        mock_client_instance.models.list.assert_called_once()

@pytest.mark.asyncio
async def test_check_api_connection_failure():
    """
    Тест неудачного подключения к API OpenAI
    """
    # Мокаем openai.AsyncClient для тестирования без реального API ключа
    with mock.patch('openai.AsyncClient') as mock_async_client:
        # Настраиваем мок с ошибкой
        mock_client_instance = mock.AsyncMock()
        mock_client_instance.models.list = mock.AsyncMock(side_effect=Exception("API Error"))
        mock_async_client.return_value = mock_client_instance
        
        # Создаем экземпляр сервиса с моком
        service = OpenAIService()
        
        # Проверяем что соединение неуспешно
        result = await service.check_api_connection()
        assert result is False
        
        # Проверяем что был вызван нужный метод
        mock_client_instance.models.list.assert_called_once()

@pytest.mark.asyncio
async def test_check_api_connection_no_api_key():
    """
    Тест проверки соединения без установленного API ключа
    """
    # Временно устанавливаем пустой API ключ
    with mock.patch('openai.api_key', ''):
        # Создаем экземпляр сервиса
        service = OpenAIService()
        
        # Проверяем что соединение неуспешно без вызова API
        result = await service.check_api_connection()
        assert result is False

@pytest.mark.asyncio
async def test_generate_profile_success():
    """
    Тест успешной генерации психологического профиля
    """
    # Мокаем openai.AsyncClient для тестирования без реального API ключа
    with mock.patch('openai.AsyncClient') as mock_async_client:
        # Настраиваем мок для возврата тестового ответа
        mock_client_instance = mock.AsyncMock()
        mock_chat_completions = mock.AsyncMock()
        mock_client_instance.chat.completions.create = mock_chat_completions
        
        # Создаем мок-ответ
        mock_response = mock.MagicMock()
        mock_response.choices = [mock.MagicMock()]
        mock_response.choices[0].message.content = "Тестовый профиль"
        mock_chat_completions.return_value = mock_response
        
        # Устанавливаем возвращаемое значение для AsyncClient
        mock_async_client.return_value = mock_client_instance
        
        # Создаем экземпляр сервиса
        service = OpenAIService()
        
        # Тестовые данные пользователя
        user_data = {
            "birth_date": "01.01.1990",
            "birth_time": "12:00",
            "birth_place": "Москва",
            "age": 33,
            "psychology_answers": {
                "0": {
                    "question_text": "Тестовый вопрос 1",
                    "option_text": "Тестовый ответ 1"
                },
                "1": {
                    "question_text": "Тестовый вопрос 2",
                    "option_text": "Тестовый ответ 2"
                }
            }
        }
        
        # Проверяем генерацию профиля
        profile = await service.generate_profile(user_data)
        
        # Проверяем результат
        assert profile == "Тестовый профиль"
        
        # Проверяем что был вызван нужный метод с правильными параметрами
        mock_chat_completions.assert_called_once()
        args, kwargs = mock_chat_completions.call_args
        assert kwargs["model"] == "gpt-4"
        assert len(kwargs["messages"]) == 2
        assert kwargs["messages"][0]["role"] == "system"
        assert kwargs["messages"][1]["role"] == "user"

@pytest.mark.asyncio
async def test_generate_profile_no_api_key():
    """
    Тест генерации профиля без установленного API ключа
    """
    # Временно устанавливаем пустой API ключ
    with mock.patch('openai.api_key', ''):
        # Создаем экземпляр сервиса
        service = OpenAIService()
        
        # Тестовые данные пользователя
        user_data = {"psychology_answers": {}}
        
        # Проверяем генерацию профиля
        profile = await service.generate_profile(user_data)
        
        # Проверяем результат
        assert "Невозможно сгенерировать профиль" in profile

@pytest.mark.asyncio
async def test_generate_profile_api_error():
    """
    Тест обработки ошибки API при генерации профиля
    """
    # Мокаем openai.AsyncClient для имитации ошибки
    with mock.patch('openai.AsyncClient') as mock_async_client:
        # Настраиваем мок с ошибкой
        mock_client_instance = mock.AsyncMock()
        mock_client_instance.chat.completions.create = mock.AsyncMock(side_effect=Exception("API Error"))
        mock_async_client.return_value = mock_client_instance
        
        # Создаем экземпляр сервиса
        service = OpenAIService()
        
        # Тестовые данные пользователя
        user_data = {"psychology_answers": {}}
        
        # Проверяем генерацию профиля
        profile = await service.generate_profile(user_data)
        
        # Проверяем результат
        assert "Произошла ошибка" in profile 