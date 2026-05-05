from fastapi import APIRouter
from app.schemas.schemas import HealthResponse
from app.services.model_service import model_service

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """验证服务是否正常运行"""
    return {
        "status": "ok", 
        "message": "服务运行正常", 
        "device": str(model_service.device)
    }
