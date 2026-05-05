from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.schemas import PredictionResponse
from app.services.spectrum_service import process_uploaded_file
from app.services.model_service import model_service

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
async def predict_spectrum(file: UploadFile = File(...)):
    """接收高光谱dat文件并返回预测结果"""
    print(f"--- 收到上传请求 ---")
    print(f"文件名: {file.filename}")
    
    try:
        # 处理上传并读取光谱
        mean_spectrum = await process_uploaded_file(file)
        
        # 模型预测
        result = model_service.predict_single_sample(mean_spectrum)
        
        # 返回格式化结果
        return {
            "code": 200,
            "message": "预测成功",
            "filename": file.filename,
            "data": {
                "catechins": {"name": "儿茶素", "value": float(result['儿茶素 (%)'])},
                "caffeine": {"name": "咖啡因", "value": float(result['咖啡因 (%)'])},
                "theophylline": {"name": "茶碱", "value": float(result['茶碱 (%)'])},
                "theanine": {"name": "茶氨酸", "value": float(result['茶氨酸 (%)'])}
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理过程中发生错误: {str(e)}")
