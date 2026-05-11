from pydantic import BaseModel


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
    acquisition_date: str | None = None
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
    preview_url: str | None = None
    reflectance_preview_url: str | None = None


class HyperspectralSpectrumResponse(BaseModel):
    sample_id: str
    sample_name: str
    device_name: str
    acquisition_date: str | None = None
    unit: str
    x: int
    y: int
    points: list[SpectrumPoint]
    statistics: SpectrumStatistics
    preview_url: str | None = None


class UploadedSampleImportResponse(BaseModel):
    sample_id: str
