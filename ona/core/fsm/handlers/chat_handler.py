"""
Обработчик состояния чата с AI-наставником
"""
import logging
from telegram import Update
from core.fsm.base_handler import StateHandler
from core.services.openai_service import openai_service
from core.services.subscription_service import subscription_service

logger = logging.getLogger(__name__)

class ChatHandler(StateHandler):
    """
    Обработчик состояния чата с AI-наставником
    """
    async def handle(self, update: Update):
        """
        Обработка сообщений в состоянии чата
        
        Args:
            update: Обновление от Telegram
        """
        if not update.message or not update.message.text:
            return
        
        try:
            # Проверяем наличие активной подписки
            has_subscription = await subscription_service.has_active_subscription(
                update.effective_user.id
            )
            
            if not has_subscription:
                await update.message.reply_text(
                    "Для общения с AI-наставником необходима активная подписка. "
                    "Пожалуйста, выберите подходящий план подписки.",
                    reply_markup=self.get_subscription_keyboard()
                )
                return
            
            # Генерируем ответ с помощью OpenAI
            response = await openai_service.generate_response(
                user_id=update.effective_user.id,
                user_message=update.message.text
            )
            
            if response:
                await update.message.reply_text(response)
            else:
                await update.message.reply_text(
                    "Извините, произошла ошибка при генерации ответа. "
                    "Пожалуйста, попробуйте позже."
                )
                
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения в чате: {e}")
            await update.message.reply_text(
                "Произошла ошибка при обработке сообщения. "
                "Пожалуйста, попробуйте позже."
            )
    
    def get_subscription_keyboard(self):
        """
        Создает клавиатуру для перехода к подписке
        
        Returns:
            InlineKeyboardMarkup: Клавиатура с кнопкой подписки
        """
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [[InlineKeyboardButton("Выбрать план подписки", callback_data="subscribe")]]
        return InlineKeyboardMarkup(keyboard) 