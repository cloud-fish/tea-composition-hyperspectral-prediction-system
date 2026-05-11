from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import os
import shutil
from uuid import uuid4

import numpy as np
from fastapi import HTTPException, UploadFile

from app.config import settings


@dataclass
class HyperspectralSampleRecord:
    sample_id: str
    sample_name: str
    dat_path: Path
    hdr_path: Path
    metadata: dict[str, Any]


class HyperspectralService:
    def __init__(self) -> None:
        self.data_root = Path(settings.HYPERSPECTRAL_DATA_ROOT)
        self._record_cache: dict[str, HyperspectralSampleRecord] = {}
        self._cube_cache: dict[str, np.memmap] = {}

    def get_sample_metadata(self, sample_id: str) -> dict[str, Any]:
        record = self._get_sample_record(sample_id)
        metadata = record.metadata
        return {
            "sample_id": record.sample_id,
            "sample_name": record.sample_name,
            "device_name": metadata.get("sensor type", "Specim IQ"),
            "acquisition_date": metadata.get("acquisition date"),
            "samples": int(metadata["samples"]),
            "lines": int(metadata["lines"]),
            "bands": int(metadata["bands"]),
            "interleave": str(metadata["interleave"]).upper(),
            "data_type": int(metadata["data type"]),
            "wavelength_start": float(metadata["wavelength"][0]),
            "wavelength_end": float(metadata["wavelength"][-1]),
            "wavelength_count": len(metadata["wavelength"]),
            "center_x": int(metadata["samples"]) // 2,
            "center_y": int(metadata["lines"]) // 2,
            "preview_url": self._build_preview_url(sample_id, "scene"),
            "reflectance_preview_url": self._build_preview_url(sample_id, "reflectance"),
        }

    def get_spectrum(self, sample_id: str, x: int | None = None, y: int | None = None) -> dict[str, Any]:
        record = self._get_sample_record(sample_id)
        metadata = record.metadata
        sample_count = int(metadata["samples"])
        line_count = int(metadata["lines"])
        x = sample_count // 2 if x is None else x
        y = line_count // 2 if y is None else y

        if x < 0 or x >= sample_count or y < 0 or y >= line_count:
            raise HTTPException(status_code=400, detail="坐标超出高光谱图像范围")

        cube = self._get_cube(record)
        spectrum = np.asarray(cube[y, :, x], dtype=np.float64)
        wavelengths = metadata["wavelength"]
        peak_index = int(np.argmax(spectrum))

        return {
            "sample_id": record.sample_id,
            "sample_name": record.sample_name,
            "device_name": metadata.get("sensor type", "Specim IQ"),
            "acquisition_date": metadata.get("acquisition date"),
            "unit": "反射率",
            "x": x,
            "y": y,
            "points": [
                {
                    "wavelength": float(wavelength),
                    "intensity": float(intensity),
                }
                for wavelength, intensity in zip(wavelengths, spectrum, strict=True)
            ],
            "statistics": {
                "min_intensity": float(np.min(spectrum)),
                "max_intensity": float(np.max(spectrum)),
                "avg_intensity": float(np.mean(spectrum)),
                "peak_wavelength": float(wavelengths[peak_index]),
                "peak_intensity": float(spectrum[peak_index]),
            },
            "preview_url": self._build_preview_url(sample_id, "scene"),
        }

    async def import_uploaded_files(self, files: list[UploadFile]) -> dict[str, str]:
        if not files:
            raise HTTPException(status_code=400, detail="上传内容为空")

        sample_id = f"upload_{uuid4().hex[:8]}"
        sample_dir = self.data_root / sample_id / "results"
        sample_dir.mkdir(parents=True, exist_ok=True)

        saved_paths: list[Path] = []
        try:
            for file in files:
                if not file.filename:
                    continue
                saved_path = await self._save_upload_file(file, sample_dir)
                normalized_path = self._normalize_uploaded_file_name(saved_path, sample_id)
                saved_paths.append(normalized_path)

            dat_path = self._select_uploaded_dat_path(saved_paths)
            hdr_path = self._select_uploaded_hdr_path(saved_paths, dat_path)
            if hdr_path is None or not hdr_path.exists():
                hdr_path = self._create_default_hdr(dat_path, sample_id)
                saved_paths.append(hdr_path)

            self._record_cache.pop(sample_id, None)
            self._cube_cache.pop(sample_id, None)
            self.get_sample_metadata(sample_id)
            return {"sample_id": sample_id}
        except Exception:
            shutil.rmtree(self.data_root / sample_id, ignore_errors=True)
            self._record_cache.pop(sample_id, None)
            self._cube_cache.pop(sample_id, None)
            raise

    def get_preview_path(self, sample_id: str, kind: str) -> Path:
        record = self._get_sample_record(sample_id)
        sample_dir = record.dat_path.parent
        preview_map = {
            "scene": sample_dir / f"RGBSCENE_{sample_id}.png",
            "reflectance": sample_dir / f"REFLECTANCE_{sample_id}.png",
            "background": sample_dir / f"RGBBACKGROUND_{sample_id}.png",
            "viewfinder": sample_dir / f"RGBVIEWFINDER_{sample_id}.png",
        }

        preview_path = preview_map.get(kind)
        if preview_path is None:
            raise HTTPException(status_code=400, detail="不支持的预览图类型")
        if not preview_path.exists():
            raise HTTPException(status_code=404, detail="预览图不存在")
        return preview_path

    def _get_sample_record(self, sample_id: str) -> HyperspectralSampleRecord:
        if sample_id in self._record_cache:
            return self._record_cache[sample_id]

        sample_dir = self.data_root / sample_id / "results"
        if not sample_dir.exists():
            raise HTTPException(status_code=404, detail="高光谱样本目录不存在")

        dat_path = sample_dir / f"REFLECTANCE_{sample_id}.dat"
        hdr_path = sample_dir / f"REFLECTANCE_{sample_id}.hdr"

        if not dat_path.exists() or not hdr_path.exists():
            raise HTTPException(status_code=404, detail="高光谱数据文件不完整")

        metadata = self._parse_envi_header(hdr_path)
        record = HyperspectralSampleRecord(
            sample_id=sample_id,
            sample_name=dat_path.stem,
            dat_path=dat_path,
            hdr_path=hdr_path,
            metadata=metadata,
        )
        self._record_cache[sample_id] = record
        return record

    def _get_cube(self, record: HyperspectralSampleRecord) -> np.memmap:
        if record.sample_id in self._cube_cache:
            return self._cube_cache[record.sample_id]

        metadata = record.metadata
        interleave = str(metadata["interleave"]).upper()
        if interleave != "BIL":
            raise HTTPException(status_code=400, detail=f"暂不支持 {interleave} 交错格式")

        dtype = self._get_numpy_dtype(int(metadata["data type"]), int(metadata["byte order"]))
        shape = (int(metadata["lines"]), int(metadata["bands"]), int(metadata["samples"]))
        cube = np.memmap(
            record.dat_path,
            dtype=dtype,
            mode="r",
            offset=int(metadata["header offset"]),
            shape=shape,
        )
        self._cube_cache[record.sample_id] = cube
        return cube

    async def _save_upload_file(self, file: UploadFile, target_dir: Path) -> Path:
        safe_name = Path(file.filename or "upload.bin").name
        target_path = target_dir / safe_name
        with target_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        await file.close()
        return target_path

    def _normalize_uploaded_file_name(self, file_path: Path, sample_id: str) -> Path:
        name_upper = file_path.name.upper()
        target_name: str | None = None

        if name_upper.startswith("REFLECTANCE_") and file_path.suffix.lower() == ".dat":
            target_name = f"REFLECTANCE_{sample_id}.dat"
        elif name_upper.startswith("REFLECTANCE_") and file_path.suffix.lower() == ".hdr":
            target_name = f"REFLECTANCE_{sample_id}.hdr"
        elif name_upper.startswith("REFLECTANCE_") and file_path.suffix.lower() == ".png":
            target_name = f"REFLECTANCE_{sample_id}.png"
        elif name_upper.startswith("RGBSCENE_") and file_path.suffix.lower() == ".png":
            target_name = f"RGBSCENE_{sample_id}.png"
        elif name_upper.startswith("RGBBACKGROUND_") and file_path.suffix.lower() == ".png":
            target_name = f"RGBBACKGROUND_{sample_id}.png"
        elif name_upper.startswith("RGBVIEWFINDER_") and file_path.suffix.lower() == ".png":
            target_name = f"RGBVIEWFINDER_{sample_id}.png"
        elif name_upper.startswith("REFLECTANCE_") and file_path.name.lower().endswith(".dat.enp"):
            target_name = f"REFLECTANCE_{sample_id}.dat.enp"

        if target_name is None or file_path.name == target_name:
            return file_path

        target_path = file_path.with_name(target_name)
        if target_path.exists():
            target_path.unlink()
        file_path.rename(target_path)
        return target_path

    def _select_uploaded_dat_path(self, saved_paths: list[Path]) -> Path:
        dat_paths = [
            path for path in saved_paths
            if path.is_file() and path.name.lower().endswith(".dat")
        ]
        if not dat_paths:
            raise HTTPException(status_code=400, detail="上传文件夹中未找到 .dat 高光谱文件")
        return next((path for path in dat_paths if path.stem.upper().startswith("REFLECTANCE_")), dat_paths[0])

    def _select_uploaded_hdr_path(self, saved_paths: list[Path], dat_path: Path) -> Path | None:
        expected_hdr = dat_path.with_suffix(".hdr")
        if expected_hdr.exists():
            return expected_hdr

        hdr_paths = [path for path in saved_paths if path.is_file() and path.suffix.lower() == ".hdr"]
        return hdr_paths[0] if hdr_paths else None

    def _create_default_hdr(self, dat_path: Path, sample_id: str) -> Path:
        hdr_path = dat_path.with_suffix(".hdr")
        wavelengths = ", ".join(f"{value:.2f}" for value in np.arange(400, 1012, 3, dtype=np.float64))
        hdr_content = "\n".join([
            "ENVI",
            "description = {Generated from uploaded .dat file}",
            "samples = 512",
            "lines = 512",
            "bands = 204",
            "header offset = 0",
            "file type = ENVI Standard",
            "data type = 4",
            "interleave = bil",
            "sensor type = Manual Upload",
            "byte order = 0",
            f"sample id = {sample_id}",
            f"wavelength = {{{wavelengths}}}",
            "",
        ])
        hdr_path.write_text(hdr_content, encoding="utf-8")
        return hdr_path

    def _parse_envi_header(self, hdr_path: Path) -> dict[str, Any]:
        lines = hdr_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        parsed: dict[str, Any] = {}
        index = 0

        while index < len(lines):
            raw_line = lines[index].strip()
            index += 1

            if not raw_line or raw_line == "ENVI" or "=" not in raw_line:
                continue

            key, value = [part.strip() for part in raw_line.split("=", 1)]

            if value.startswith("{"):
                segments = [value[1:]]
                while not segments[-1].strip().endswith("}") and index < len(lines):
                    segments.append(lines[index].strip())
                    index += 1
                value = " ".join(segments).rsplit("}", 1)[0].strip()

            parsed[key.lower()] = self._coerce_header_value(key.lower(), value)

        required_keys = {"samples", "lines", "bands", "header offset", "data type", "interleave", "byte order", "wavelength"}
        missing_keys = required_keys - parsed.keys()
        if missing_keys:
            raise HTTPException(status_code=400, detail=f"HDR 文件缺少必要字段: {', '.join(sorted(missing_keys))}")

        return parsed

    def _coerce_header_value(self, key: str, value: str) -> Any:
        if key in {"samples", "lines", "bands", "header offset", "data type", "byte order", "fps", "tint"}:
            return int(float(value))
        if key in {"latitude", "longitude"}:
            return float(value)
        if key in {"wavelength", "default bands", "binning"}:
            return [
                float(item) if key == "wavelength" else int(float(item))
                for item in (segment.strip() for segment in value.split(","))
                if item
            ]
        return value

    def _get_numpy_dtype(self, data_type: int, byte_order: int) -> np.dtype:
        type_map = {
            1: np.uint8,
            2: np.int16,
            3: np.int32,
            4: np.float32,
            5: np.float64,
            12: np.uint16,
        }
        numpy_type = type_map.get(data_type)
        if numpy_type is None:
            raise HTTPException(status_code=400, detail=f"暂不支持 ENVI data type={data_type}")

        dtype = np.dtype(numpy_type)
        if dtype.byteorder == "|" or byte_order not in {0, 1}:
            return dtype
        return dtype.newbyteorder("<" if byte_order == 0 else ">")

    def _build_preview_url(self, sample_id: str, kind: str) -> str | None:
        try:
            self.get_preview_path(sample_id, kind)
        except HTTPException:
            return None
        return f"{settings.API_V1_STR}/hyperspectral/samples/{sample_id}/preview?kind={kind}"


hyperspectral_service = HyperspectralService()
