from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse
from typing import Optional

from app.schemas.hyperspectral import (
    HyperspectralSampleMeta,
    HyperspectralSpectrumResponse,
    UploadedSampleImportResponse,
)
from app.services.hyperspectral_service import hyperspectral_service

router = APIRouter()


@router.get("/hyperspectral/samples/{sample_id}", response_model=HyperspectralSampleMeta)
async def get_hyperspectral_sample_meta(sample_id: str):
    """获取高光谱样本元数据与预览信息"""
    return HyperspectralSampleMeta(**hyperspectral_service.get_sample_metadata(sample_id))


@router.get("/hyperspectral/samples/{sample_id}/spectrum", response_model=HyperspectralSpectrumResponse)
async def get_hyperspectral_spectrum(sample_id: str, x: Optional[int] = None, y: Optional[int] = None):
    """获取指定像素点的光谱曲线，默认返回中心像素"""
    return HyperspectralSpectrumResponse(**hyperspectral_service.get_spectrum(sample_id, x=x, y=y))


@router.get("/hyperspectral/samples/{sample_id}/preview")
async def get_hyperspectral_preview(sample_id: str, kind: str = "scene"):
    """返回样本预览图"""
    preview_path = hyperspectral_service.get_preview_path(sample_id, kind)
    return FileResponse(preview_path, media_type="image/png", filename=preview_path.name)


@router.post("/hyperspectral/upload/import", response_model=UploadedSampleImportResponse)
async def import_uploaded_hyperspectral_sample(files: list[UploadFile] = File(...)):
    """统一导入手动上传的文件或文件夹，并复用原有样本接口访问"""
    return UploadedSampleImportResponse(**(await hyperspectral_service.import_uploaded_files(files)))
