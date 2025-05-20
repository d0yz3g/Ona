import asyncio
import logging
from ona.core.services.telegram_service import TelegramService

logging.basicConfig(level=logging.INFO)

async def main():
    service = TelegramService()
    await service.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
