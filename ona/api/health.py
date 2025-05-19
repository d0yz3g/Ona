from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    """
    Проверка работоспособности API
    """
    return {"status": "ok"} 