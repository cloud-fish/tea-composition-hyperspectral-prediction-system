import os
import shutil
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile, HTTPException
from utils import ReadHyperspectrum
from app.config import settings

async def process_uploaded_file(file: UploadFile):
    """保存上传文件并读取光谱数据"""
    if not file.filename or not file.filename.lower().endswith('.dat'):
        raise HTTPException(status_code=400, detail="仅支持 .dat 格式的高光谱文件")
    
    os.makedirs(settings.TEMP_UPLOAD_DIR, exist_ok=True)
    safe_name = Path(file.filename).name
    temp_path = os.path.join(settings.TEMP_UPLOAD_DIR, f"{uuid4().hex}_{safe_name}")
    
    try:
        # 保存文件
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 读取光谱数据
        mean_spectrum = ReadHyperspectrum.read_data(temp_path, file.filename)
        return mean_spectrum
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)

async def process_imported_sample(sample_id: str):
    """从已导入的固定样本目录中读取光谱数据"""
    dat_path = os.path.join(
        settings.HYPERSPECTRAL_DATA_ROOT,
        sample_id,
        "results",
        f"REFLECTANCE_{sample_id}.dat",
    )

    if not os.path.exists(dat_path):
        raise HTTPException(status_code=404, detail="导入样本的 .dat 文件不存在")

    return ReadHyperspectrum.read_data(dat_path, sample_id)
