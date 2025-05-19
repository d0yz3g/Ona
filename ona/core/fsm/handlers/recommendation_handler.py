"""
Обработчик для работы с рекомендациями
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from core.fsm.base_handler import StateHandler
from core.services.recommendation_service import recommendation_service
from core.services.subscription_service import subscription_service

logger = logging.getLogger(__name__)

class RecommendationHandler(StateHandler):
    """
    Обработчик для работы с рекомендациями
    """
    async def handle(self, update: Update):
        """
        Обработка запросов на рекомендации
        
        Args:
            update: Обновление от Telegram
        """
        if not update.message and not update.callback_query:
            return
        
        try:
            # Получаем telegram_id пользователя
            telegram_id = update.effective_user.id
            
            # Проверяем наличие активной подписки
            has_subscription = await subscription_service.has_active_subscription(telegram_id)
            
            if not has_subscription:
                await self.send_subscription_message(update)
                return
            
            # Обрабатываем callback_query для выбора типа практики
            if update.callback_query:
                await self.handle_practice_selection(update)
                return
            
            # Обрабатываем команду /recommendation
            if update.message.text == "/recommendation":
                await self.send_recommendation(update)
                return
            
            # Обрабатываем команду /practice
            if update.message.text == "/practice":
                await self.send_practice_menu(update)
                return
                
        except Exception as e:
            logger.error(f"Ошибка при обработке рекомендаций: {e}")
            await self.send_error_message(update)
    
    async def send_recommendation(self, update: Update):
        """
        Отправка ежедневной рекомендации
        
        Args:
            update: Обновление от Telegram
        """
        try:
            # Отправляем сообщение о генерации
            await update.message.reply_text(
                "Генерирую персонализированную рекомендацию... 🤔"
            )
            
            # Генерируем рекомендацию
            recommendation = await recommendation_service.generate_daily_recommendation(
                update.effective_user.id
            )
            
            if recommendation:
                await update.message.reply_text(recommendation)
            else:
                await update.message.reply_text(
                    "Извините, не удалось сгенерировать рекомендацию. "
                    "Пожалуйста, попробуйте позже."
                )
                
        except Exception as e:
            logger.error(f"Ошибка при отправке рекомендации: {e}")
            await self.send_error_message(update)
    
    async def send_practice_menu(self, update: Update):
        """
        Отправка меню выбора практики
        
        Args:
            update: Обновление от Telegram
        """
        keyboard = [
            [
                InlineKeyboardButton("Осознанность", callback_data="practice_mindfulness"),
                InlineKeyboardButton("Антистресс", callback_data="practice_stress")
            ],
            [
                InlineKeyboardButton("Сон", callback_data="practice_sleep"),
                InlineKeyboardButton("Энергия", callback_data="practice_energy")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Выберите тип практики:",
            reply_markup=reply_markup
        )
    
    async def handle_practice_selection(self, update: Update):
        """
        Обработка выбора типа практики
        
        Args:
            update: Обновление от Telegram
        """
        try:
            callback_query = update.callback_query
            await callback_query.answer()
            
            # Отправляем сообщение о генерации
            await callback_query.message.reply_text(
                "Генерирую персонализированную практику... 🤔"
            )
            
            # Извлекаем тип практики из callback_data
            practice_type = callback_query.data.replace("practice_", "")
            
            # Генерируем практику
            practice = await recommendation_service.generate_practice(
                callback_query.from_user.id,
                practice_type
            )
            
            if practice:
                await callback_query.message.reply_text(practice)
            else:
                await callback_query.message.reply_text(
                    "Извините, не удалось сгенерировать практику. "
                    "Пожалуйста, попробуйте позже."
                )
                
        except Exception as e:
            logger.error(f"Ошибка при обработке выбора практики: {e}")
            await self.send_error_message(update)
    
    async def send_subscription_message(self, update: Update):
        """
        Отправка сообщения о необходимости подписки
        
        Args:
            update: Обновление от Telegram
        """
        keyboard = [[InlineKeyboardButton("Выбрать план подписки", callback_data="subscribe")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            "Для получения персонализированных рекомендаций и практик "
            "необходима активная подписка. Пожалуйста, выберите подходящий план."
        )
        
        if update.callback_query:
            await update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        else:
            await update.message.reply_text(message, reply_markup=reply_markup)
    
    async def send_error_message(self, update: Update):
        """
        Отправка сообщения об ошибке
        
        Args:
            update: Обновление от Telegram
        """
        message = (
            "Произошла ошибка при обработке запроса. "
            "Пожалуйста, попробуйте позже или обратитесь в поддержку."
        )
        
        if update.callback_query:
            await update.callback_query.message.reply_text(message)
        else:
            await update.message.reply_text(message) 