import asyncio
import logging
from ona.core.services.telegram_service import TelegramService

logging.basicConfig(level=logging.INFO)

async def main():
    service = TelegramService()
    await service.setup_handlers()
    await service.app.initialize()
    await service.app.start()
    
    print("✅ Бот запущен. Ожидаю сообщения...")
    await service.app.updater.start_polling()
    
    # ОЖИДАНИЕ CTRL+C или SIGINT
    await service.app.updater.wait_for_stop()

    await service.app.stop()
    await service.app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
