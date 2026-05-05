from pydantic import BaseModel

class ComponentValue(BaseModel):
    name: str
    value: float

class PredictionData(BaseModel):
    catechins: ComponentValue
    caffeine: ComponentValue
    theophylline: ComponentValue
    theanine: ComponentValue

class PredictionResponse(BaseModel):
    code: int
    message: str
    filename: str
    data: PredictionData

class HealthResponse(BaseModel):
    status: str
    message: str
    device: str
