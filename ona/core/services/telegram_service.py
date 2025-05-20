from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from ona.config.settings import TELEGRAM_BOT_TOKEN
from ona.utils.state_router import state_router
from ona.core.fsm.handlers.registration_handler import STATES as REGISTRATION_STATES
from ona.core.fsm.handlers.profiling_psychology_handler import STATE as PSYCHOLOGY_STATE
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramService:
    """
    Класс для работы с Telegram Bot API
    """
    def __init__(self):
        """
        Инициализация сервиса Telegram бота
        """
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
    async def setup_handlers(self):
        """
        Настройка обработчиков команд и сообщений
        """
        # Настройка обработчиков команд
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        
        # Обработчик текстовых сообщений
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Обработчик голосовых сообщений
        self.app.add_handler(MessageHandler(filters.VOICE, self.handle_voice_message))
        
        # Обработчик callback-запросов от инлайн-кнопок
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Обработчик ошибок
        self.app.add_error_handler(self.error_handler)
        #УДАЛИТЬ ПОТОМ
        self.app.add_handler(MessageHandler(filters.ALL, self.debug_handler))
    
    async def start_command(self, update: Update, context):
        """
        Обработка команды /start
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
    
    async def help_command(self, update: Update, context):
        """
        Обработка команды /help
        """
        help_text = (
            "Я твой персональный наставник ONA. Вот что я умею:\n\n"
            "/start - Начать общение с ботом\n"
            "/help - Показать это сообщение помощи\n\n"
            "Ты можешь общаться со мной в свободной форме, и я постараюсь помочь тебе."
        )
        await update.message.reply_text(help_text)
    
    async def handle_message(self, update: Update, context):
        """
        Обработка текстовых сообщений
        """
        user_message = update.message.text
        logger.info(f"Получено сообщение: {user_message}")
        
        # Здесь будет логика обработки сообщений пользователя
        # Временный ответ для тестирования
        await update.message.reply_text(f"Я получила твое сообщение: {user_message}")
    
    async def handle_voice_message(self, update: Update, context):
        """
        Обработка голосовых сообщений
        """
        logger.info("Получено голосовое сообщение")
        
        # Получение файла голосового сообщения
        voice_file = await update.message.voice.get_file()
        voice_bytes = await voice_file.download_as_bytearray()
        
        # Здесь будет код для преобразования голоса в текст (будет добавлен позже)
        # Пока отправляем заглушку
        await update.message.reply_text("Получено голосовое сообщение. Функция преобразования голоса в текст будет добавлена позже.")
    
    async def handle_callback(self, update: Update, context):
        """
        Обработка callback-запросов от инлайн-кнопок
        """
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        logger.info(f"Получен callback: {callback_data}")
        
        # Здесь будет логика обработки callback-запросов
        # Временный ответ для тестирования
        await query.edit_message_text(text=f"Выбран вариант: {callback_data}")
    
    async def error_handler(self, update: Update, context):
        """
        Обработка ошибок
        """
        logger.error(f"Ошибка при обработке запроса: {context.error}")
    async def debug_handler(self, update: Update, context):
    print(f"\n📩 ПРИШЛО ОБНОВЛЕНИЕ: {update}")

    async def start_polling(self):
        """
        Запуск бота в режиме long polling
        """
        await self.setup_handlers()
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
    
    async def setup_webhook(self, webhook_url: str, secret_token: str = None):
        """
        Настройка webhook для получения обновлений
        
        Args:
            webhook_url: URL для webhook
            secret_token: Секретный токен для проверки подлинности запросов
        """
        await self.setup_handlers()
        await self.app.initialize()
        await self.app.start()
        await self.bot.set_webhook(url=webhook_url, secret_token=secret_token)
    
    async def process_update(self, update_data: dict):
        """
        Обработка обновления, полученного через webhook
        
        Args:
            update_data: Словарь с данными обновления от Telegram
        """
        update = Update.de_json(update_data, self.bot)
        
        # Обработка различных типов обновлений согласно work-plan
        if update.message and update.message.text:
            # Обработка текстового сообщения
            await self.handle_text_message(update)
        elif update.message and update.message.voice:
            # Обработка голосового сообщения
            await self.handle_voice_message(update, None)
        elif update.callback_query:
            # Обработка нажатия на кнопку
            await self.handle_callback_query(update.callback_query)
        else:
            # Передаем обновление в стандартный обработчик для других типов
            await self.app.process_update(update)
    
    async def handle_text_message(self, update: Update):
        """
        Обработка текстовых сообщений с маршрутизацией через FSM
        """
        logger.info(f"Обработка текстового сообщения: {update.message.text}")
        
        # Маршрутизация через FSM
        await state_router.route(update)
        
        # Сохранение сообщения в историю
        user = await self.get_or_create_user(update.effective_user)
        await self.save_message(user["id"], update.message.text, is_user=True)
    
    async def handle_callback_query(self, callback_query):
        """
        Обработка callback-запросов (нажатий на кнопки)
        """
        # Получение данных из кнопки
        data = callback_query.data
        logger.info(f"Обработка callback-запроса: {data}")
        
        # Обработка различных типов кнопок
        if data == "start_profiling":
            # Начало профайлинга - переводим пользователя в состояние регистрации
            user_id = callback_query.from_user.id
            
            # В соответствии с work-plan используем состояние PROFILING_NATAL
            await state_router.set_user_state(user_id, REGISTRATION_STATES["PROFILING_NATAL"])
            
            # Создаем фиктивное обновление для обработки
            fake_update = Update(
                update_id=0,
                message=callback_query.message,
                effective_user=callback_query.from_user
            )
            
            # Запускаем маршрутизацию для начала процесса профилирования
            await state_router.route(fake_update)
            
            # Удаляем старое сообщение с кнопкой
            await callback_query.message.delete()
        elif data == "continue_profiling":
            # Продолжение профайлинга - переход к психологическому профилированию
            user_id = callback_query.from_user.id
            
            # Устанавливаем новое состояние
            await state_router.set_user_state(user_id, PSYCHOLOGY_STATE)
            
            # Отправляем сообщение о переходе к следующему этапу
            await callback_query.message.reply_text(
                "Отлично! Теперь переходим ко второму этапу профайлинга - психологическому опроснику. "
                "Этот этап поможет мне лучше понять твои психологические особенности, ценности и предпочтения."
            )
            
            # Создаем фиктивное обновление для обработки
            fake_update = Update(
                update_id=0,
                message=callback_query.message,
                effective_user=callback_query.from_user
            )
            
            # Запускаем маршрутизацию для психологического профилирования
            await state_router.route(fake_update)
        elif data.startswith("answer_"):
            # Ответ на вопрос психологического профилирования
            user_id = callback_query.from_user.id
            
            # Получение текущего состояния пользователя
            current_state = await state_router.get_user_state(user_id)
            
            # Создаем фиктивное обновление для обработки
            fake_update = Update(
                update_id=0,
                callback_query=callback_query,
                effective_user=callback_query.from_user
            )
            
            # Маршрутизация через FSM
            await state_router.route(fake_update)
        elif data == "next_stage":
            # Переход к следующему этапу (будет реализовано в следующих задачах)
            await callback_query.message.reply_text(
                "Следующий этап будет доступен в ближайшее время!"
            )
        
        # Подтверждение обработки запроса
        await callback_query.answer()
    
    async def get_or_create_user(self, effective_user):
        """
        Получение или создание пользователя в базе данных
        
        Args:
            effective_user: Пользователь из обновления Telegram
            
        Returns:
            Словарь с данными пользователя
        """
        # Заглушка - в будущем будет заменена на реальное обращение к базе данных
        user_id = effective_user.id
        logger.info(f"Получение или создание пользователя: {user_id}")
        return {
            "id": user_id,
            "username": effective_user.username,
            "first_name": effective_user.first_name,
            "last_name": effective_user.last_name,
        }
    
    async def save_message(self, user_id, text, is_user=True):
        """
        Сохранение сообщения в историю диалога
        
        Args:
            user_id: Идентификатор пользователя
            text: Текст сообщения
            is_user: Флаг, указывающий на то, что сообщение от пользователя
        """
        # Заглушка - в будущем будет заменена на реальное сохранение в базе данных
        logger.info(f"Сохранение сообщения для пользователя {user_id}: {text[:50]}...")
    
    async def stop(self):
        """
        Остановка бота
        """
        if self.app.updater:
            await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown() 
