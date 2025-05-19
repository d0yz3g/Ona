"""
Обработчик состояния подписки
"""
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from core.fsm.base_handler import StateHandler
from core.services.payment_service import payment_service

logger = logging.getLogger(__name__)

class SubscriptionHandler(StateHandler):
    """
    Обработчик состояния подписки
    """
    async def handle(self, update: Update):
        """
        Обработка сообщений в состоянии подписки
        
        Args:
            update: Обновление от Telegram
        """
        if update.callback_query and update.callback_query.data == "subscribe":
            # Отображение информации о подписке
            await self.show_subscription_plans(update.callback_query)
        elif update.callback_query and update.callback_query.data.startswith("select_plan_"):
            # Обработка выбора плана
            plan_type = update.callback_query.data.replace("select_plan_", "")
            await self.process_plan_selection(update.callback_query, plan_type)
    
    async def show_subscription_plans(self, callback_query):
        """
        Отображение доступных планов подписки
        
        Args:
            callback_query: CallbackQuery от Telegram
        """
        plans_text = (
            "Выбери план подписки:\n\n"
            "🔹 Базовый (299 ₽/месяц):\n"
            "• Доступ к базовым медитациям\n"
            "• Ограниченное количество диалогов\n"
            "• Базовая поддержка\n\n"
            "🔸 Премиум (599 ₽/месяц):\n"
            "• Все базовые функции\n"
            "• Неограниченное количество диалогов\n"
            "• Приоритетная поддержка\n"
            "• Доступ к эксклюзивным медитациям\n"
            "• Персональные рекомендации"
        )
        
        # Создаем клавиатуру с кнопками выбора плана
        keyboard = [
            [
                InlineKeyboardButton("Базовый план", callback_data="select_plan_basic"),
                InlineKeyboardButton("Премиум план", callback_data="select_plan_premium")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем сообщение с планами
        await callback_query.edit_message_text(
            text=plans_text,
            reply_markup=reply_markup
        )
    
    async def process_plan_selection(self, callback_query, plan_type):
        """
        Обработка выбора плана подписки
        
        Args:
            callback_query: CallbackQuery от Telegram
            plan_type: Тип выбранного плана (basic/premium)
        """
        try:
            # Создаем платеж
            payment_info = await payment_service.create_payment(
                telegram_id=callback_query.from_user.id,
                plan_type=plan_type
            )
            
            if not payment_info:
                await callback_query.edit_message_text(
                    "Извините, произошла ошибка при создании платежа. Пожалуйста, попробуйте позже."
                )
                return
            
            # Создаем кнопку для перехода к оплате
            keyboard = [[InlineKeyboardButton("Оплатить", url=payment_info["payment_url"])]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Отправляем сообщение с кнопкой оплаты
            await callback_query.edit_message_text(
                text=f"Для оплаты подписки {plan_type} перейдите по ссылке:",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Ошибка при обработке выбора плана: {e}")
            await callback_query.edit_message_text(
                "Извините, произошла ошибка. Пожалуйста, попробуйте позже."
            ) 