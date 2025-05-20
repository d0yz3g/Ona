import logging
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from ona.config.settings import TELEGRAM_BOT_TOKEN
from ona.utils.state_router import state_router
from ona.core.fsm.handlers.registration_handler import STATES as REGISTRATION_STATES
from ona.core.fsm.handlers.profiling_psychology_handler import STATE as PSYCHOLOGY_STATE

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
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    async def setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.app.add_handler(MessageHandler(filters.VOICE, self.handle_voice_message))
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        self.app.add_error_handler(self.error_handler)
        # DEBUG: лог всех апдейтов
        self.app.add_handler(MessageHandler(filters.ALL, self.debug_handler))

    async def debug_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"\n📩 DEBUG: Получено обновление от Telegram:\n{update}")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await update.message.reply_text(
            f"Привет, {user.first_name}! 👋\n\n"
            "Я ONA – твой личный AI-наставник для психологического роста и самопознания.\n\n"
            "Готова начать путь самопознания?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✨ Начать профайлинг", callback_data="start_profiling")]
            ])
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Команда помощи. Пока в разработке.")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info(f"Получено сообщение: {update.message.text}")
        await update.message.reply_text(f"Я получила твоё сообщение: {update.message.text}")

    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info("Голосовое сообщение получено.")
        await update.message.reply_text("Голосовое сообщение получено. Обработка позже.")

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(f"Выбран вариант: {query.data}")

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Ошибка при обработке запроса: {context.error}")

    def start_polling(self):
    import asyncio
    asyncio.run(self._start_polling())

async def _start_polling(self):
    await self.setup_handlers()
    await self.app.run_polling()



