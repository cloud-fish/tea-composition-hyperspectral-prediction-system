import os
import uuid
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
import torch
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction
from app.config import settings


class PestDetectionService:
    """虫害检测服务，基于 SAHI + YOLO 模型。"""

    def __init__(self) -> None:
        self.model: Optional[AutoDetectionModel] = None
        self._model_loaded = False

    def _load_model(self) -> AutoDetectionModel:
        """懒加载检测模型。"""
        if self._model_loaded and self.model is not None:
            return self.model

        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.model = AutoDetectionModel.from_pretrained(
            model_type="yolo11",
            model_path=settings.PEST_DETECTION_MODEL_PATH,
            confidence_threshold=0.25,
            device=device,
        )
        self._model_loaded = True
        return self.model

    async def detect_pest(self, file: UploadFile) -> dict:
        """接收上传的虫害图像，返回检测结果。"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")

        # 验证文件类型
        ext = Path(file.filename).suffix.lower()
        if ext not in (".jpg", ".jpeg", ".png", ".bmp", ".webp"):
            raise HTTPException(status_code=400, detail="仅支持 jpg、jpeg、png、bmp、webp 格式的图像")

        # 保存上传文件
        task_id = uuid4().hex[:8]
        upload_dir = Path(settings.PEST_DETECTION_UPLOAD_DIR)
        result_dir = Path(settings.PEST_DETECTION_RESULT_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        result_dir.mkdir(parents=True, exist_ok=True)

        temp_path = upload_dir / f"{task_id}_{file.filename}"
        try:
            with temp_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # 执行 SAHI 切片推理
            model = self._load_model()
            result = get_sliced_prediction(
                str(temp_path),
                detection_model=model,
                slice_height=640,
                slice_width=640,
                overlap_height_ratio=0.2,
                overlap_width_ratio=0.2,
                perform_standard_pred=False,
                postprocess_type="GREEDYNMM",
                postprocess_match_metric="IOS",
                verbose=0,
            )

            # 解析检测结果
            detections = []
            for obj in result.object_prediction_list:
                detections.append({
                    "class_id": obj.category.id,
                    "class_name": obj.category.name,
                    "confidence": round(obj.score.value, 4),
                    "bbox": {
                        "x1": round(obj.bbox.minx, 2),
                        "y1": round(obj.bbox.miny, 2),
                        "x2": round(obj.bbox.maxx, 2),
                        "y2": round(obj.bbox.maxy, 2),
                    },
                })

            # 保存带标注的结果图
            result_image_path = result_dir / f"{task_id}_result{ext}"
            result.save_visual_export(str(result_image_path))

            return {
                "task_id": task_id,
                "filename": file.filename,
                "detection_count": len(detections),
                "detections": detections,
                "result_image_url": f"/api/pest-detection/result/{task_id}_result{ext}",
            }

        finally:
            # 清理临时上传文件
            if temp_path.exists():
                temp_path.unlink()

    def get_result_image(self, filename: str) -> Path:
        """获取结果图像路径。"""
        result_path = Path(settings.PEST_DETECTION_RESULT_DIR) / filename
        if not result_path.exists():
            raise HTTPException(status_code=404, detail="结果图像不存在")
        return result_path


pest_detection_service = PestDetectionService()
