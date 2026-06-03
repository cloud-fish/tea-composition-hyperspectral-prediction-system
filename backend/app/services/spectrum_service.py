import os
import tempfile
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile, HTTPException
from utils import ReadHyperspectrum
from app.config import settings

async def process_uploaded_file(file: UploadFile):
    """保存上传文件并读取光谱数据"""
    if not file.filename or not file.filename.lower().endswith('.dat'):
        raise HTTPException(status_code=400, detail="仅支持 .dat 格式的高光谱文件")
    
    safe_name = Path(file.filename).name
    # 使用系统临时目录，用完自动清理
    with tempfile.NamedTemporaryFile(suffix=f"_{safe_name}", delete=False) as tmp:
        tmp.write(file.file.read())
        temp_path = tmp.name
    
    try:
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
