"""
Тесты для сервиса YooKassa
"""
import pytest
from unittest import mock
import aiohttp
from core.services.payment_service import PaymentService

@pytest.mark.asyncio
async def test_create_payment_success():
    """
    Тест успешного создания платежа
    """
    # Мокаем aiohttp.ClientSession для тестирования без реального API
    with mock.patch('aiohttp.ClientSession') as mock_session:
        # Настраиваем мок для успешного ответа
        mock_response = mock.AsyncMock()
        mock_response.status = 200
        mock_response.json = mock.AsyncMock(return_value={
            "id": "test_payment_id",
            "confirmation": {
                "confirmation_url": "https://test.payment.url"
            }
        })
        
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
        
        # Создаем экземпляр сервиса
        service = PaymentService()
        
        # Тестовые данные
        telegram_id = "123456789"
        plan_type = "basic"
        
        # Проверяем создание платежа
        result = await service.create_payment(telegram_id, plan_type)
        
        # Проверяем результат
        assert result is not None
        assert "payment_id" in result
        assert "payment_url" in result
        assert "order_id" in result
        assert result["payment_id"] == "test_payment_id"
        assert result["payment_url"] == "https://test.payment.url"

@pytest.mark.asyncio
async def test_create_payment_api_error():
    """
    Тест обработки ошибки API при создании платежа
    """
    # Мокаем aiohttp.ClientSession для имитации ошибки
    with mock.patch('aiohttp.ClientSession') as mock_session:
        # Настраиваем мок для ошибки
        mock_response = mock.AsyncMock()
        mock_response.status = 400
        mock_response.text = mock.AsyncMock(return_value="Bad Request")
        
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
        
        # Создаем экземпляр сервиса
        service = PaymentService()
        
        # Проверяем создание платежа
        result = await service.create_payment("123456789")
        
        # Проверяем результат
        assert result is None

@pytest.mark.asyncio
async def test_check_payment_success():
    """
    Тест успешной проверки статуса платежа
    """
    # Мокаем aiohttp.ClientSession для тестирования без реального API
    with mock.patch('aiohttp.ClientSession') as mock_session:
        # Настраиваем мок для успешного ответа
        mock_response = mock.AsyncMock()
        mock_response.status = 200
        mock_response.json = mock.AsyncMock(return_value={
            "status": "succeeded"
        })
        
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        
        # Создаем экземпляр сервиса
        service = PaymentService()
        
        # Проверяем статус платежа
        result = await service.check_payment("test_payment_id")
        
        # Проверяем результат
        assert result is True

@pytest.mark.asyncio
async def test_check_payment_failed():
    """
    Тест проверки неуспешного платежа
    """
    # Мокаем aiohttp.ClientSession для тестирования без реального API
    with mock.patch('aiohttp.ClientSession') as mock_session:
        # Настраиваем мок для ответа с неуспешным статусом
        mock_response = mock.AsyncMock()
        mock_response.status = 200
        mock_response.json = mock.AsyncMock(return_value={
            "status": "canceled"
        })
        
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        
        # Создаем экземпляр сервиса
        service = PaymentService()
        
        # Проверяем статус платежа
        result = await service.check_payment("test_payment_id")
        
        # Проверяем результат
        assert result is False

@pytest.mark.asyncio
async def test_check_payment_api_error():
    """
    Тест обработки ошибки API при проверке платежа
    """
    # Мокаем aiohttp.ClientSession для имитации ошибки
    with mock.patch('aiohttp.ClientSession') as mock_session:
        # Настраиваем мок для ошибки
        mock_response = mock.AsyncMock()
        mock_response.status = 400
        mock_response.text = mock.AsyncMock(return_value="Bad Request")
        
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        
        # Создаем экземпляр сервиса
        service = PaymentService()
        
        # Проверяем статус платежа
        result = await service.check_payment("test_payment_id")
        
        # Проверяем результат
        assert result is False 