from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from app.schemas.pest_detection import PestDetectionResponse
from app.services.pest_detection_service import pest_detection_service

router = APIRouter()


@router.post("/pest-detection/detect", response_model=PestDetectionResponse)
async def detect_pest(file: UploadFile = File(...)):
    """接收虫害图像并返回检测结果"""
    return PestDetectionResponse(**(await pest_detection_service.detect_pest(file)))


@router.get("/pest-detection/result/{filename}")
async def get_result_image(filename: str):
    """获取检测结果图像"""
    result_path = pest_detection_service.get_result_image(filename)
    return FileResponse(result_path, media_type="image/png", filename=filename)
