# run_polling.py

import asyncio
from ona.core.services.telegram_service import TelegramService

if __name__ == "__main__":
    service = TelegramService()
    asyncio.run(service.start_polling())
