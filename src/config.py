from src.paths import ROOT
from dataclasses import dataclass
from pathlib import Path
from src.providers import ComputeBackend

@dataclass
class LicensePlateConfig:
    compute_backend: ComputeBackend = ComputeBackend.CPU
    trt_cache_path: str = '.trt_cache'
    trt_fp16_enable: bool = True
    detector_backend: str = 'fast'
    fast_detection_model: str = 'yolo-v9-t-640-license-plate-end2end'
    weights_path: str = str(ROOT / 'models/legacy/best.pt')
    det_conf: float = 0.60
    det_iou: float = 0.85
    imgsz: int = 640
    device: str = 'cpu'
    ocr_engine: str = 'fast'
    ocr_model: str = 'cct-s-v2-global-model'
