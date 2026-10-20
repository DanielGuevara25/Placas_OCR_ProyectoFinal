
"""
Motor OCR con arquitectura de backends intercambiables.
=======================================================

Backend activo: FastPlateOCR.

Para agregar un nuevo backend:
    1. Implementar una clase con el método: read(crop: np.ndarray) -> tuple[list[str], list[float]]
    2. Registrarla en OCREngine.__init__ bajo una nueva clave de 'engine'

Configuración en config.py:
    ocr_engine:  str = "fast"
    fast_model:  str = "cct-s-v2-global-model"
"""
from src.config import LicensePlateConfig
from src.providers import build_providers
import dataclasses
import numpy as np
import logging

logger = logging.getLogger("OCR-Engine")

# Interpolación al reescalar el crop de placa al tamaño de entrada del modelo
# (pisa el "linear" del yaml del hub, sin tocar el archivo cacheado).
# Opciones válidas: nearest | linear | cubic | area | lanczos4
_INTERPOLATION = "cubic"


# ══════════════════════════════
#   Preprocesado
# ══════════════════════════════

def preprocess_plate(crop: np.ndarray) -> np.ndarray:
    """
    Preprocesado aplicado al crop antes de pasarlo al backend OCR.
  
    args:
        crop: Imagen BGR con shape (H, W, C).
 
    return:
        imagen procesada con shape (H, W, C), dtype uint8.
 
    TODO: evaluar en producción si CLAHE o sharpening mejoran lecturas
          en placas EC de bajo contraste o con motion blur.
    """
    return crop

# ══════════════════════════════
#   Backends
# ══════════════════════════════

class _FastPlateOCRBackend:
    """ Backend fast-plate-ocr (LicensePlateRecognizer)."""
    def __init__(self, cfg: LicensePlateConfig):
        from fast_plate_ocr import LicensePlateRecognizer

        providers = build_providers(
            backend         = cfg.compute_backend,
            trt_cache_path  = cfg.trt_cache_path,
            trt_fp16_enable = cfg.trt_fp16_enable,
        )

        self._model = LicensePlateRecognizer(
            cfg.ocr_model,
            providers = providers,
        )
        if self._model.config.interpolation != _INTERPOLATION:
            self._model.config = dataclasses.replace(self._model.config, interpolation=_INTERPOLATION)
        logger.info("FastPlateOCR cargado (model=%s, interpolation=%s)", cfg.ocr_model, _INTERPOLATION)
    
    def read(self, crop: np.ndarray) -> tuple[list[str], list[float]]:
        crop = np.ascontiguousarray(preprocess_plate(crop)[:, :, ::-1])  # BGR -> RGB
        try:
            # remove_pad_char=False: conservamos el padding en el texto para que
            # quede alineado 1:1 con char_probs (largo fijo = max_plate_slots).
            results = self._model.run(crop, return_confidence=True, remove_pad_char=False)
        except Exception as e:
            logger.exception("FastPlateOCR falló")
            raise RuntimeError("El OCR no pudo procesar este recorte.") from e

        if not results:
            return [], []

        pred = results[0]
        pad_char = self._model.config.pad_char

        # Cada carácter de la lectura completa (con padding) se asocia a su
        # char_prob correspondiente. Como sabemos cuál es el padding char,
        # lo excluimos del resultado en vez de descartar esa info a ciegas.
        chars, char_probs = [], []
        if pred.char_probs is None or len(pred.plate) != len(pred.char_probs):
            raise RuntimeError("El OCR devolvió caracteres y confianzas desalineados.")
        for ch, prob in zip(pred.plate, pred.char_probs):
            if ch == pad_char:
                continue
            chars.append(ch)
            char_probs.append(float(prob))

        return chars, char_probs

# ══════════════════════════════
#   Motor OCR Unificado
# ══════════════════════════════
class WebOCR:
    """
    Selecciona el backend en tiempo de construcción.
 
    Backends disponibles:
        "fast"  →  _FastPlateOCRBackend  (default)
 
    Interfaz pública idéntica para todos los backends:
        chars, char_probs = engine.read(crop)
    """

    def __init__(self, cfg: LicensePlateConfig):
        engine = cfg.ocr_engine.lower().strip()
        engine = engine.lower().strip()

        if engine == "fast":
            self._backend = _FastPlateOCRBackend(cfg)
        else:
            raise ValueError(f"Engine desconocido: '{engine}'.")

        self._engine_name = engine

    def read(self, crop: np.ndarray) -> tuple[list[str], list[float]]:
        """
        Lee el texto de un crop de placa.
        Retorna dos listas en paralelo (chars, char_probs), una por cada
        carácter leído (sin padding) con su confianza correspondiente,
        o ([], []) si no detecta nada válido.
        """
        if crop is None or crop.size == 0:
            return [], []
        return self._backend.read(crop)