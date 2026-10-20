"""
providers.py — Construcción de ONNX Execution Providers
=========================================================
Responsabilidad única: traducir un ComputeBackend a la lista de providers
que acepta FaceAnalysis / onnxruntime.
"""

import logging
from enum import Enum

logger = logging.getLogger(__name__)
 
class ComputeBackend(str, Enum):
    """
    Backend de inferencia.
 
    TENSORRT  — TensorRT + CUDA + CPU (mayor rendimiento, requiere compilación en primer uso).
    CUDA      — CUDA + CPU (sin overhead de compilación TRT).
    CPU       — Solo CPU (portabilidad máxima).
    """
    TENSORRT = "tensorrt"
    CUDA     = "cuda"
    CPU      = "cpu"

OnnxProviders = list[str | tuple[str, dict]]

def build_providers(
    backend: ComputeBackend,
    trt_cache_path: str = ".trt_cache",
    trt_fp16_enable: bool = True,
) -> OnnxProviders:
    """
    Construye la lista ordenada de ONNX Execution Providers para el backend elegido.

    ONNX Runtime intenta cada provider en orden y usa el primero disponible,
    por lo que CPU siempre va al final.

    Args:
        backend:          Backend deseado (ComputeBackend).
        trt_cache_path:   Directorio de caché para motores TensorRT compilados.
        trt_fp16_enable:  Activar precisión FP16 en TensorRT.

    Returns:
        Lista de providers lista para pasar a FaceAnalysis(providers=...)
    """
    if backend == ComputeBackend.TENSORRT:
        providers = _tensorrt_providers(trt_cache_path, trt_fp16_enable)

    elif backend == ComputeBackend.CUDA:
        providers = _cuda_providers()

    elif backend == ComputeBackend.CPU:
        providers = _cpu_providers()

    else:
        raise ValueError(
            f"Backend no soportado: {backend!r}. "
            f"Valores válidos: {[b.value for b in ComputeBackend]}"
        )
    logger.debug("Providers construidos para backend=%s: %s", backend.value, providers)
    return providers


# ═════════════════════════════════════
#  Constructores privados por backend
# ═════════════════════════════════════ 

def _tensorrt_providers(cache_path: str, fp16: bool) -> OnnxProviders:
    trt_options = {
        "trt_engine_cache_enable": True,
        "trt_engine_cache_path":   cache_path,
        "trt_fp16_enable":         fp16,
    }
    return [
        ("TensorrtExecutionProvider", trt_options),
        "CUDAExecutionProvider",
        "CPUExecutionProvider",
    ]


def _cuda_providers() -> OnnxProviders:
    return [
        "CUDAExecutionProvider",
        "CPUExecutionProvider",
    ]

def _cpu_providers() -> OnnxProviders:
    return ["CPUExecutionProvider"]