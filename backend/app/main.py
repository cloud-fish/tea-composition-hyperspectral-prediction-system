from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import device, health, predict
from app.services.model_service import model_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """服务启动时加载模型，避免每次请求都重新加载"""
    model_service.load_model()
    yield


app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, debug=True, lifespan=lifespan)

# 配置 CORS，允许前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中建议替换为实际前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["Health"])
app.include_router(predict.router, prefix=settings.API_V1_STR, tags=["Predict"])
app.include_router(device.router, prefix=settings.API_V1_STR, tags=["Device"])
