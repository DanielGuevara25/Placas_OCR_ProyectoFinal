"""Inspecciona pesos locales y el OCR ya cacheado, sin entrenar ni descargar."""
import hashlib
import json
import os
from importlib.metadata import version

from src.paths import DEFAULT_WEIGHTS, ROOT


def main():
    cache = ROOT / '.model-cache'
    cache.mkdir(exist_ok=True)
    os.environ.setdefault('YOLO_CONFIG_DIR', str(cache))
    from ultralytics import YOLO
    from fast_plate_ocr.inference.hub import MODEL_CACHE_DIR
    import onnxruntime as ort
    import yaml

    folder = MODEL_CACHE_DIR / 'cct-s-v2-global-model'
    ocr_path = folder / 'cct_s_v2_global.onnx'
    config_path = folder / 'cct_s_v2_global_plate_config.yaml'
    for path in (DEFAULT_WEIGHTS, ocr_path, config_path):
        if not path.is_file():
            raise FileNotFoundError(f'Archivo local requerido: {path.name}')
    model = YOLO(DEFAULT_WEIGHTS)
    report = {
        'detector': {
            'checkpoint': 'models/best.pt',
            'sha256': hashlib.sha256(DEFAULT_WEIGHTS.read_bytes()).hexdigest(),
            'parameters_before_fusion': sum(p.numel() for p in model.model.parameters()),
            'top_level_blocks': len(model.model.model),
            'yaml': model.model.yaml,
        },
        'versions': {name: version(name) for name in ('torch', 'ultralytics', 'fast-plate-ocr', 'onnxruntime')},
    }
    model.model.fuse(verbose=False)
    report['detector']['parameters_after_fusion'] = sum(p.numel() for p in model.model.parameters())
    session = ort.InferenceSession(str(ocr_path), providers=['CPUExecutionProvider'])
    report['ocr'] = {
        'model': 'cct-s-v2-global-model',
        'onnx_sha256': hashlib.sha256(ocr_path.read_bytes()).hexdigest(),
        'config_sha256': hashlib.sha256(config_path.read_bytes()).hexdigest(),
        'cached_config': yaml.safe_load(config_path.read_text(encoding='utf-8')),
        'application_interpolation': 'cubic',
        'inputs': [{'name': i.name, 'shape': i.shape, 'type': i.type} for i in session.get_inputs()],
        'outputs': [{'name': i.name, 'shape': i.shape, 'type': i.type} for i in session.get_outputs()],
        'note': 'La aplicación usa caracteres; no consume la salida de región.',
    }
    output = ROOT / 'results/reports/arquitectura_modelos.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str) + '\n', encoding='utf-8')
    print(f'Arquitectura inspeccionada: {output}')


if __name__ == '__main__':
    main()
