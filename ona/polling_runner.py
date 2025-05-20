import asyncio
from aiogram import Bot, Dispatcher
from ona.config.settings import TELEGRAM_BOT_TOKEN
from ona.api.telegram_webhook import router  # если там хендлеры
# или импортируй хендлеры по-другому, если router — это FastAPI, а не aiogram

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
# Здесь добавь все свои хендлеры
dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
