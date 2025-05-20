"""
Сервис для работы с подписками пользователей
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from config.settings import settings
from core.services.payment_service import payment_service
from core.db.supabase_client import supabase

logger = logging.getLogger(__name__)

class SubscriptionService:
    """
    Класс для работы с подписками пользователей
    """
    # Типы подписок и их длительность в днях
    SUBSCRIPTION_TYPES = {
        "basic": 30,  # 30 дней
        "premium": 30  # 30 дней
    }
    
    # Цены подписок
    SUBSCRIPTION_PRICES = {
        "basic": 299,
        "premium": 599
    }
    
    def __init__(self):
        """
        Инициализация сервиса подписок
        """
        self.payment_service = payment_service
    
    async def create_subscription(self, telegram_id: str, plan_type: str = "basic") -> Dict:
        """
        Создает новую подписку для пользователя
        
        Args:
            telegram_id: Telegram ID пользователя
            plan_type: Тип подписки (basic/premium)
            
        Returns:
            Dict: Информация о созданной подписке или None в случае ошибки
        """
        try:
            # Создаем платеж через YooKassa
            payment_info = await self.payment_service.create_payment(telegram_id, plan_type)
            
            if not payment_info:
                logger.error(f"Не удалось создать платеж для пользователя {telegram_id}")
                return None

            # Находим пользователя по telegram_id
            user_result = supabase.table("users").select("id").eq("telegram_id", telegram_id).execute()
            
            if not user_result.data or len(user_result.data) == 0:
                logger.error(f"Пользователь с telegram_id {telegram_id} не найден")
                return None
                
            user_id = user_result.data[0]["id"]
            
            # Сохраняем информацию о подписке
            subscription_data = {
                "user_id": user_id,
                "plan_type": plan_type,
                "payment_id": payment_info["payment_id"],
                "order_id": payment_info["order_id"],
                "status": "pending",  # Ожидает оплаты
                "start_date": datetime.utcnow(),
                "end_date": None,
                "price": self.SUBSCRIPTION_PRICES[plan_type]
            }
            
            # Сохраняем в базу данных
            subscription_result = supabase.table("subscriptions").insert(subscription_data).execute()
            
            if not subscription_result.data or len(subscription_result.data) == 0:
                logger.error(f"Ошибка при сохранении подписки для пользователя {telegram_id}")
                return None
            
            return {
                "subscription_id": payment_info["payment_id"],
                "payment_url": payment_info["payment_url"],
                "status": "pending"
            }
            
        except Exception as e:
            logger.error(f"Ошибка при создании подписки: {e}")
            return None
    
    async def activate_subscription(self, payment_id: str) -> bool:
        """
        Активирует подписку после успешной оплаты
        
        Args:
            payment_id: ID платежа в YooKassa
            
        Returns:
            bool: True если подписка успешно активирована
        """
        try:
            # Проверяем статус платежа
            is_paid = await self.payment_service.check_payment(payment_id)
            
            if not is_paid:
                logger.error(f"Платеж {payment_id} не подтвержден")
                return False
            
            # TODO: Получить данные подписки из базы по payment_id

            # Получаем данные подписки из базы по payment_id
            subscription_result = supabase.table("subscriptions").select("*").eq("payment_id", payment_id).execute()
            
            if not subscription_result.data or len(subscription_result.data) == 0:
                logger.error(f"Подписка с payment_id {payment_id} не найдена")
                return False
                
            subscription = subscription_result.data[0]
            
            # Определяем длительность подписки
            plan_type = subscription["plan_type"]
            if plan_type not in self.SUBSCRIPTION_TYPES:
                plan_type = "basic"
              
            
            # Устанавливаем дату окончания подписки
            subscription_data = {
                "status": "active",
                "start_date": datetime.utcnow(),
                "end_date": datetime.utcnow() + timedelta(days=self.SUBSCRIPTION_TYPES[plan_type])
            }
            
            # Обновляем данные в базе
            update_result = supabase.table("subscriptions").update(subscription_data).eq("payment_id", payment_id).execute()
            
            return update_result.data and len(update_result.data) > 0
            
        except Exception as e:
            logger.error(f"Ошибка при активации подписки: {e}")
            return False
    
    async def check_subscription(self, telegram_id: str) -> Optional[Dict]:
        """
        Проверяет статус подписки пользователя
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            Optional[Dict]: Информация о подписке или None если подписка не найдена
        """
        try:
            # TODO: Получить данные подписки из базы
            # Находим пользователя по telegram_id
            user_result = supabase.table("users").select("id").eq("telegram_id", telegram_id).execute()
            
            if not user_result.data or len(user_result.data) == 0:
                logger.error(f"Пользователь с telegram_id {telegram_id} не найден")
                return None
                
            user_id = user_result.data[0]["id"]
            
            # Получаем данные подписки из базы
            subscription_result = supabase.table("subscriptions")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("status", "active")\
                .order("end_date", desc=True)\
                .limit(1)\
                .execute()
            
            if not subscription_result.data or len(subscription_result.data) == 0:
                return None
                
            subscription_data = subscription_result.data[0]
            
            # Проверяем срок действия
            if subscription_data["end_date"] and datetime.fromisoformat(subscription_data["end_date"]) < datetime.utcnow():
                subscription_data["status"] = "expired"
             # Обновляем статус в базе
                supabase.table("subscriptions").update({"status": "expired"}).eq("id", subscription_data["id"]).execute()
                
            return subscription_data
            
        except Exception as e:
            logger.error(f"Ошибка при проверке подписки: {e}")
            return None
    
    async def cancel_subscription(self, telegram_id: str) -> bool:
        """
        Отменяет активную подписку
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            bool: True если подписка успешно отменена
        """
        try:
            # TODO: Получить данные подписки из базы
            # Получаем данные подписки из базы
            subscription_data = await self.check_subscription(telegram_id)
            
            if not subscription_data or subscription_data["status"] != "active":
                logger.error(f"Нет активной подписки для пользователя {telegram_id}")
                return False
            
            # Обновляем статус подписки
            update_data = {
                "status": "cancelled",
                "cancelled_at": datetime.utcnow().isoformat()
            }
            
            # Обновляем данные в базе
            update_result = supabase.table("subscriptions").update(update_data).eq("id", subscription_data["id"]).execute()
            
            return update_result.data and len(update_result.data) > 0
            
        except Exception as e:
            logger.error(f"Ошибка при отмене подписки: {e}")
            return False
    
    async def get_subscription_info(self, telegram_id: str) -> Optional[Dict]:
        """
        Получает полную информацию о подписке пользователя
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            Optional[Dict]: Информация о подписке или None если подписка не найдена
        """
        try:
            # Получаем данные подписки из базы
            subscription_data = await self.check_subscription(telegram_id)
            
            if not subscription_data:
                return None
            
            # Добавляем дополнительную информацию
            end_date = datetime.fromisoformat(subscription_data["end_date"]) if subscription_data["end_date"] else None
            days_left = (end_date - datetime.utcnow()).days if end_date and subscription_data["status"] == "active" else 0
            
            subscription_info = {
                **subscription_data,
                "days_left": days_left,
                "is_active": subscription_data["status"] == "active",
                "price": self.SUBSCRIPTION_PRICES[subscription_data["plan_type"]]
            }
            
            return subscription_info
            
        except Exception as e:
            logger.error(f"Ошибка при получении информации о подписке: {e}")
            return None
    
    async def get_user_subscription(self, telegram_id):
        """
        Получает активную подписку пользователя
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            dict: Информация о подписке или None если подписка не найдена
        """
        try:
            # Получение пользователя
            user_result = supabase.table("users").select("id").eq("telegram_id", telegram_id).execute()
            
            if not user_result.data:
                logger.warning(f"Пользователь с telegram_id {telegram_id} не найден")
                return None
            
            user_id = user_result.data[0]["id"]
            
            # Получение активной подписки
            now = datetime.now().isoformat()
            subscription_result = supabase.table("subscriptions").select("*") \
                .eq("user_id", user_id) \
                .eq("status", "active") \
                .gte("end_date", now) \
                .order("end_date", desc=True) \
                .limit(1) \
                .execute()
            
            if not subscription_result.data:
                logger.info(f"Активная подписка для пользователя {telegram_id} не найдена")
                return None
            
            return subscription_result.data[0]
            
        except Exception as e:
            logger.error(f"Ошибка при получении подписки пользователя {telegram_id}: {e}")
            return None
    
    async def has_active_subscription(self, telegram_id):
        """
        Проверяет, есть ли у пользователя активная подписка
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            bool: True если есть активная подписка, иначе False
        """
        subscription = await self.get_user_subscription(telegram_id)
        return subscription is not None
    
    async def get_subscription_end_date(self, telegram_id):
        """
        Получает дату окончания подписки
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            str: Дата окончания подписки в формате ISO или None если подписка не найдена
        """
        subscription = await self.get_user_subscription(telegram_id)
        
        if not subscription:
            return None
        
        return subscription["end_date"]

# Создание экземпляра сервиса
subscription_service = SubscriptionService() 
