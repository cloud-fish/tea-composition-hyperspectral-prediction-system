from pydantic import BaseModel
from typing import Optional



class SpectrumPoint(BaseModel):
    wavelength: float
    intensity: float


class SpectrumStatistics(BaseModel):
    min_intensity: float
    max_intensity: float
    avg_intensity: float
    peak_wavelength: float
    peak_intensity: float


class HyperspectralSampleMeta(BaseModel):
    sample_id: str
    sample_name: str
    device_name: str
    acquisition_date: Optional[str] = None
    samples: int
    lines: int
    bands: int
    interleave: str
    data_type: int
    wavelength_start: float
    wavelength_end: float
    wavelength_count: int
    center_x: int
    center_y: int
    preview_url: Optional[str] = None
    reflectance_preview_url: Optional[str] = None


class HyperspectralSpectrumResponse(BaseModel):
    sample_id: str
    sample_name: str
    device_name: str
    acquisition_date: Optional[str] = None
    unit: str
    x: int
    y: int
    points: list[SpectrumPoint]
    statistics: SpectrumStatistics
    preview_url: Optional[str] = None


class UploadedSampleImportResponse(BaseModel):
    sample_id: str
