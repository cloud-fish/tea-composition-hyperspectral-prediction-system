from pydantic import BaseModel
from typing import List, Optional


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class DetectionItem(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox


class PestDetectionResponse(BaseModel):
    code: int = 200
    message: str = "检测成功"
    task_id: str
    filename: str
    detection_count: int
    detections: List[DetectionItem]
    result_image_url: str
