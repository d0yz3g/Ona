"""
Сервис для работы с YooKassa API
"""
import uuid
import logging
import aiohttp
from datetime import datetime, timedelta
from config.settings import settings

logger = logging.getLogger(__name__)

class PaymentService:
    """
    Класс для работы с YooKassa API
    """
    def __init__(self):
        """
        Инициализация клиента YooKassa API
        """
        self.api_url = "https://api.yookassa.ru/v3"
        self.shop_id = settings.YOOKASSA_SHOP_ID
        self.api_key = settings.YOOKASSA_API_KEY
        
        # Проверяем наличие необходимых настроек
        if not self.shop_id or not self.api_key:
            logger.warning("Не установлены настройки YooKassa (shop_id или api_key)")
    
    async def create_payment(self, telegram_id: str, plan_type: str = "basic") -> dict:
        """
        Создает платеж в YooKassa
        
        Args:
            telegram_id: Telegram ID пользователя
            plan_type: Тип подписки (basic/premium)
            
        Returns:
            dict: Информация о созданном платеже или None в случае ошибки
        """
        # Определение суммы в зависимости от плана
        amount = {
            "basic": 299,
            "premium": 599
        }.get(plan_type, 299)
        
        # Создание идентификатора заказа
        order_id = str(uuid.uuid4())
        
        # Данные для запроса
        payment_data = {
            "amount": {
                "value": str(amount),
                "currency": "RUB"
            },
            "capture": True,
            "confirmation": {
                "type": "redirect",
                "return_url": f"{settings.BASE_URL}/api/payments/callback?telegram_id={telegram_id}&plan_type={plan_type}"
            },
            "description": f"Подписка на ONA - план {plan_type}",
            "metadata": {
                "telegram_id": telegram_id,
                "plan_type": plan_type,
                "order_id": order_id
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/payments",
                    json=payment_data,
                    auth=aiohttp.BasicAuth(self.shop_id, self.api_key),
                    headers={"Idempotence-Key": order_id}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Успешно создан платеж для пользователя {telegram_id}")
                        return {
                            "payment_id": result["id"],
                            "payment_url": result["confirmation"]["confirmation_url"],
                            "order_id": order_id
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка при создании платежа: {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"Ошибка при создании платежа: {e}")
            return None
    
    async def check_payment(self, payment_id: str) -> bool:
        """
        Проверяет статус платежа
        
        Args:
            payment_id: ID платежа в YooKassa
            
        Returns:
            bool: True если платеж успешен, иначе False
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/payments/{payment_id}",
                    auth=aiohttp.BasicAuth(self.shop_id, self.api_key)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["status"] == "succeeded"
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка при проверке платежа: {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Ошибка при проверке платежа: {e}")
            return False

# Создание экземпляра сервиса
payment_service = PaymentService() 