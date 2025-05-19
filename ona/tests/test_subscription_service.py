"""
Тесты для сервиса управления подписками
"""
import pytest
from unittest import mock
from datetime import datetime, timedelta
from core.services.subscription_service import SubscriptionService

@pytest.mark.asyncio
async def test_create_subscription_success():
    """
    Тест успешного создания подписки
    """
    # Мокаем payment_service
    with mock.patch('core.services.subscription_service.payment_service') as mock_payment:
        # Настраиваем мок для успешного создания платежа
        mock_payment.create_payment.return_value = {
            "payment_id": "test_payment_id",
            "payment_url": "https://test.payment.url",
            "order_id": "test_order_id"
        }
        
        # Создаем экземпляр сервиса
        service = SubscriptionService()
        
        # Тестовые данные
        telegram_id = "123456789"
        plan_type = "basic"
        
        # Проверяем создание подписки
        result = await service.create_subscription(telegram_id, plan_type)
        
        # Проверяем результат
        assert result is not None
        assert "subscription_id" in result
        assert "payment_url" in result
        assert "status" in result
        assert result["status"] == "pending"
        assert result["subscription_id"] == "test_payment_id"
        assert result["payment_url"] == "https://test.payment.url"

@pytest.mark.asyncio
async def test_create_subscription_payment_error():
    """
    Тест обработки ошибки при создании платежа
    """
    # Мокаем payment_service
    with mock.patch('core.services.subscription_service.payment_service') as mock_payment:
        # Настраиваем мок для ошибки создания платежа
        mock_payment.create_payment.return_value = None
        
        # Создаем экземпляр сервиса
        service = SubscriptionService()
        
        # Проверяем создание подписки
        result = await service.create_subscription("123456789")
        
        # Проверяем результат
        assert result is None

@pytest.mark.asyncio
async def test_activate_subscription_success():
    """
    Тест успешной активации подписки
    """
    # Мокаем payment_service
    with mock.patch('core.services.subscription_service.payment_service') as mock_payment:
        # Настраиваем мок для успешной проверки платежа
        mock_payment.check_payment.return_value = True
        
        # Создаем экземпляр сервиса
        service = SubscriptionService()
        
        # Проверяем активацию подписки
        result = await service.activate_subscription("test_payment_id")
        
        # Проверяем результат
        assert result is True

@pytest.mark.asyncio
async def test_activate_subscription_payment_not_confirmed():
    """
    Тест активации подписки с неподтвержденным платежом
    """
    # Мокаем payment_service
    with mock.patch('core.services.subscription_service.payment_service') as mock_payment:
        # Настраиваем мок для неподтвержденного платежа
        mock_payment.check_payment.return_value = False
        
        # Создаем экземпляр сервиса
        service = SubscriptionService()
        
        # Проверяем активацию подписки
        result = await service.activate_subscription("test_payment_id")
        
        # Проверяем результат
        assert result is False

@pytest.mark.asyncio
async def test_check_subscription_active():
    """
    Тест проверки активной подписки
    """
    # Создаем тестовые данные
    subscription_data = {
        "telegram_id": "123456789",
        "plan_type": "basic",
        "status": "active",
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=30)
    }
    
    # Мокаем получение данных из базы
    with mock.patch('core.services.subscription_service.get_subscription_from_db', return_value=subscription_data):
        # Создаем экземпляр сервиса
        service = SubscriptionService()
        
        # Проверяем статус подписки
        result = await service.check_subscription("123456789")
        
        # Проверяем результат
        assert result is not None
        assert result["status"] == "active"
        assert "expires_at" in result

@pytest.mark.asyncio
async def test_check_subscription_expired():
    """
    Тест проверки просроченной подписки
    """
    # Создаем тестовые данные
    subscription_data = {
        "telegram_id": "123456789",
        "plan_type": "basic",
        "status": "active",
        "created_at": datetime.utcnow() - timedelta(days=31),
        "expires_at": datetime.utcnow() - timedelta(days=1)
    }
    
    # Мокаем получение данных из базы
    with mock.patch('core.services.subscription_service.get_subscription_from_db', return_value=subscription_data):
        # Создаем экземпляр сервиса
        service = SubscriptionService()
        
        # Проверяем статус подписки
        result = await service.check_subscription("123456789")
        
        # Проверяем результат
        assert result is not None
        assert result["status"] == "expired"

@pytest.mark.asyncio
async def test_cancel_subscription_success():
    """
    Тест успешной отмены подписки
    """
    # Создаем тестовые данные
    subscription_data = {
        "telegram_id": "123456789",
        "plan_type": "basic",
        "status": "active",
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=30)
    }
    
    # Мокаем получение и обновление данных в базе
    with mock.patch('core.services.subscription_service.get_subscription_from_db', return_value=subscription_data), \
         mock.patch('core.services.subscription_service.update_subscription_in_db', return_value=True):
        
        # Создаем экземпляр сервиса
        service = SubscriptionService()
        
        # Проверяем отмену подписки
        result = await service.cancel_subscription("123456789")
        
        # Проверяем результат
        assert result is True

@pytest.mark.asyncio
async def test_cancel_subscription_not_found():
    """
    Тест отмены несуществующей подписки
    """
    # Мокаем получение данных из базы
    with mock.patch('core.services.subscription_service.get_subscription_from_db', return_value=None):
        # Создаем экземпляр сервиса
        service = SubscriptionService()
        
        # Проверяем отмену подписки
        result = await service.cancel_subscription("123456789")
        
        # Проверяем результат
        assert result is False

@pytest.mark.asyncio
async def test_get_subscription_info():
    """
    Тест получения информации о подписке
    """
    # Создаем тестовые данные
    subscription_data = {
        "telegram_id": "123456789",
        "plan_type": "basic",
        "status": "active",
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=30)
    }
    
    # Мокаем получение данных из базы
    with mock.patch('core.services.subscription_service.get_subscription_from_db', return_value=subscription_data):
        # Создаем экземпляр сервиса
        service = SubscriptionService()
        
        # Получаем информацию о подписке
        result = await service.get_subscription_info("123456789")
        
        # Проверяем результат
        assert result is not None
        assert "days_left" in result
        assert "is_active" in result
        assert "price" in result
        assert result["is_active"] is True
        assert result["price"] == 299  # Цена basic подписки 