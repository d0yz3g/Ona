from fastapi import FastAPI
from ona.api.health import router as health_router
from api.telegram_webhook import router as telegram_router
from config.settings import DEBUG

# Инициализация FastAPI приложения
app = FastAPI(
    title="ONA API",
    description="Backend for ONA Telegram Bot",
    version="0.1.0",
    debug=DEBUG
)

# Подключение роутеров
app.include_router(health_router)
app.include_router(telegram_router)

# Корневой эндпоинт
@app.get("/")
async def root():
    return {
        "name": "ONA API",
        "version": "0.1.0",
        "status": "running"
    } 
