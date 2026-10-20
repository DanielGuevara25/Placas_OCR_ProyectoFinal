"""
Detección de placas con backends intercambiables.

- yolo: modelo local mediante Ultralytics.
- fast: detector YOLOv9 mediante open-image-models.

Salida: array Nx6 [x1, y1, x2, y2, confianza, clase].
"""

import logging

import numpy as np

from src.config import LicensePlateConfig
from src.providers import build_providers

logger = logging.getLogger("Plate-Detector")


class _YOLOBackend:
    def __init__(self, cfg: LicensePlateConfig):
        from ultralytics import YOLO

        self._cfg = cfg
        self._model = YOLO(cfg.weights_path)
        self._model.fuse()

        logger.info("YOLO Plate Detector cargado: %s", cfg.weights_path)

    def detect(self, frame: np.ndarray) -> np.ndarray:
        predictions = self._model.predict(
            frame,
            conf=self._cfg.det_conf,
            iou=self._cfg.det_iou,
            imgsz=self._cfg.imgsz,
            device=self._cfg.device,
            verbose=False,
        )

        boxes = predictions[0].boxes

        if boxes is None or len(boxes) == 0:
            return np.empty((0, 6), dtype=np.float32)

        coordinates = boxes.xyxy.cpu().numpy()
        confidences = boxes.conf.cpu().numpy().reshape(-1, 1)
        classes = boxes.cls.cpu().numpy().reshape(-1, 1)

        return np.hstack(
            [coordinates, confidences, classes]
        ).astype(np.float32)


class _FastBackend:
    def __init__(self, cfg: LicensePlateConfig):
        from open_image_models import create_detector

        providers = build_providers(
            backend=cfg.compute_backend,
            trt_cache_path=cfg.trt_cache_path,
            trt_fp16_enable=cfg.trt_fp16_enable,
        )

        self._min_conf = cfg.det_conf

        self._model = create_detector(
            cfg.fast_detection_model,
            providers=providers,
            conf_thresh=cfg.det_conf,
        )

        logger.info(
            "Plate Detector cargado: %s",
            cfg.fast_detection_model,
        )

    def detect(self, frame: np.ndarray) -> np.ndarray:
        detections = self._model.predict(frame)
        rows = []

        for detection in detections:
            if detection.confidence < self._min_conf:
                continue

            box = detection.bounding_box
            if box is None:
                continue

            rows.append(
                [
                    box.x1,
                    box.y1,
                    box.x2,
                    box.y2,
                    detection.confidence,
                    0.0,
                ]
            )

        if not rows:
            return np.empty((0, 6), dtype=np.float32)

        return np.asarray(rows, dtype=np.float32)


_BACKENDS = {
    "yolo": _YOLOBackend,
    "fast": _FastBackend,
}


class PlateDetector:
    """Detector unificado de placas."""

    def __init__(self, config: LicensePlateConfig):
        self.cfg = config
        backend = config.detector_backend.lower().strip()

        backend_class = _BACKENDS.get(backend)

        if backend_class is None:
            raise ValueError(
                f"detector_backend desconocido: '{backend}'. "
                f"Opciones válidas: {list(_BACKENDS)}"
            )

        self._backend = backend_class(config)

        logger.info(
            "Detector de placas inicializado (backend=%s)",
            backend,
        )

    def detect(self, frame: np.ndarray) -> np.ndarray:
        """Devuelve Nx6 o un array vacío de forma (0, 6)."""
        return self._backend.detect(frame)