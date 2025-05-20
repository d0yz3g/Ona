from fastapi import APIRouter, Request, Depends, HTTPException
from ona.config.settings import TELEGRAM_BOT_TOKEN
from ona.core.services.telegram_service import TelegramService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telegram", tags=["telegram"])

# Создание экземпляра TelegramService
telegram_service = TelegramService()

# Зависимость для проверки токена Telegram в заголовке
async def verify_telegram_token(request: Request):
    """
    Проверка подлинности запроса от Telegram Bot API
    """
    if "X-Telegram-Bot-Api-Secret-Token" in request.headers:
        # Здесь должна быть проверка секретного токена, если он настроен
        pass
    return True

@router.post("/webhook", dependencies=[Depends(verify_telegram_token)])
async def telegram_webhook(request: Request):
    """
    Обработчик вебхуков от Telegram Bot API
    """
    try:
        # Получение JSON-данных из запроса
        update_data = await request.json()
        logger.info(f"Получено обновление от Telegram: {update_data}")
        
        # Обработка обновления с помощью TelegramService
        await telegram_service.process_update(update_data)
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Ошибка при обработке вебхука: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/setup_webhook")
async def setup_webhook(webhook_url: str, secret_token: str = None):
    """
    Настройка вебхука для Telegram бота
    """
    try:
        await telegram_service.setup_webhook(webhook_url, secret_token)
        return {
            "status": "success",
            "message": f"Webhook успешно настроен на URL: {webhook_url}"
        }
    except Exception as e:
        logger.error(f"Ошибка при настройке вебхука: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 
