from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
import logging

logger = logging.getLogger(__name__)

class BaseHandler:
    """
    Базовый класс для всех обработчиков состояний
    """
    def __init__(self, next_state=None):
        """
        Инициализация базового обработчика
        
        Args:
            next_state: Следующее состояние, в которое нужно перейти после обработки
        """
        self.next_state = next_state
    
    async def handle(self, update: Update):
        """
        Метод для обработки обновления от Telegram
        
        Args:
            update: Обновление от Telegram
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    async def set_next_state(self, update: Update, state_router, state=None):
        """
        Установка следующего состояния для пользователя
        
        Args:
            update: Обновление от Telegram
            state_router: Маршрутизатор состояний
            state: Следующее состояние, если оно отличается от self.next_state
        """
        user_id = update.effective_user.id
        next_state = state or self.next_state
        
        if next_state:
            await state_router.set_user_state(user_id, next_state)
            logger.info(f"Установлено следующее состояние для пользователя {user_id}: {next_state}")


class InitialHandler(BaseHandler):
    """
    Обработчик начального состояния
    """
    def __init__(self):
        super().__init__(next_state="awaiting_input")
    
    async def handle(self, update: Update):
        """
        Обработка сообщения в начальном состоянии
        
        Args:
            update: Обновление от Telegram
        """
        user = update.effective_user
        
        await update.message.reply_text(
            f"Привет, {user.first_name}! 👋\n\n"
            "Я ONA – твой личный AI-наставник для психологического роста и самопознания.\n\n"
            "Я могу помочь тебе лучше понять себя через профайлинг личности. "
            "Это позволит раскрыть твои сильные стороны и потенциал развития.\n\n"
            "Готова начать путь самопознания?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✨ Начать профайлинг", callback_data="start_profiling")]
            ])
        )
        
        # Изменение состояния пользователя
        from ona.utils.state_router import state_router
        await self.set_next_state(update, state_router)


class AwaitingInputHandler(BaseHandler):
    """
    Обработчик состояния ожидания ввода пользователя
    """
    def __init__(self):
        super().__init__(next_state=None)  # Остаемся в том же состоянии
    
    async def handle(self, update: Update):
        """
        Обработка сообщения в состоянии ожидания ввода
        
        Args:
            update: Обновление от Telegram
        """
        user_message = update.message.text
        
        if "профайлинг" in user_message.lower() or "профилирование" in user_message.lower():
            # Если пользователь спрашивает о профайлинге в тексте
            await update.message.reply_text(
                "Профайлинг — это процесс раскрытия твоей личности через серию вопросов и анализ твоих ответов.\n\n"
                "Первый этап — сбор базовой информации о тебе, включая натальные данные (дата, время и место рождения).\n\n"
                "Хочешь начать?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✨ Начать профайлинг", callback_data="start_profiling")]
                ])
            )
        else:
            # Простая обработка сообщения пользователя
            await update.message.reply_text(
                f"Спасибо за твое сообщение!\n\n"
                "В данный момент я работаю в режиме ограниченной функциональности и предлагаю тебе пройти профайлинг личности. "
                "Это поможет мне лучше понять тебя и настроить наше взаимодействие.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✨ Начать профайлинг", callback_data="start_profiling")]
                ])
            ) 
