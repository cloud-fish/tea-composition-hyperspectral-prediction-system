import os
import shutil
from fastapi import UploadFile, HTTPException
from utils import ReadHyperspectrum
from app.config import settings

async def process_uploaded_file(file: UploadFile):
    """保存上传文件并读取光谱数据"""
    if not file.filename.endswith('.dat'):
        raise HTTPException(status_code=400, detail="仅支持 .dat 格式的高光谱文件")
    
    os.makedirs(settings.TEMP_UPLOAD_DIR, exist_ok=True)
    temp_path = os.path.join(settings.TEMP_UPLOAD_DIR, file.filename)
    
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
