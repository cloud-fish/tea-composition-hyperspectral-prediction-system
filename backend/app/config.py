import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "茶叶成分高光谱预测 API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Model config
    MODEL_INPUT_DIM: int = 1
    MODEL_D_MODEL: int = 72
    MODEL_NUM_LAYERS: int = 2
    MODEL_NUM_HEADS: int = 4
    MODEL_D_FF: int = 128
    MODEL_MAX_SEQ_LEN: int = 204
    MODEL_DROPOUT: float = 0.1
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH: str = os.path.join(BASE_DIR, 'models', 'transformer_4components.pth')
    SCALER_X_PATH: str = os.path.join(BASE_DIR, 'models', 'scaler_x.pkl')
    SCALER_Y_PATH: str = os.path.join(BASE_DIR, 'models', 'scaler_y.pkl')
    TEMP_UPLOAD_DIR: str = os.path.join(BASE_DIR, "temp_uploads")
    DEVICE_NAME: str = "高光谱设备"
    DEVICE_ID: str | None = None
    DEVICE_MOUNT_PATH: str = os.path.join(BASE_DIR, "mounted_device")
    
    class Config:
        env_file = ".env"
        
settings = Settings()
