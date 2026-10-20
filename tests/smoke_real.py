"""Prueba manual de integración con pesos reales: python -m tests.smoke_real.

No forma parte de unittest discover: puede descargar modelos y tarda más.
"""
import hashlib
import io
import json
import os
import platform
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from app.app import create_app
from app.web_service import WebSettings
from src.paths import DEFAULT_WEIGHTS, ROOT


def main():
    cache = ROOT / '.model-cache'
    cache.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault('YOLO_CONFIG_DIR', str(cache))
    output = ROOT / 'results/reports/prueba_integracion_real.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    app = create_app(settings=WebSettings(DEFAULT_WEIGHTS, device='cpu'))
    client = app.test_client()
    report = {
        'run_utc': datetime.now(timezone.utc).isoformat(),
        'python': platform.python_version(),
        'device': 'cpu',
        'weights_sha256': hashlib.sha256(DEFAULT_WEIGHTS.read_bytes()).hexdigest(),
        'versions': {name: version(name) for name in
                     ('torch', 'ultralytics', 'fast-plate-ocr', 'Flask', 'numpy')},
        'cases': [],
    }
    cases = [('coincidencia', 'gca4771.png', 'GCA4771'),
             ('inconsistencia', 'gtw9311.png', 'GTW9312'),
             ('sin_placa', 'sin_placa.png', 'ABC1234')]
    for name, filename, declared in cases:
        data = (ROOT / 'app/static/examples' / filename).read_bytes()
        response = client.post('/api/detect', data={
            'image': (io.BytesIO(data), filename),
            'confidence': '0.60', 'declared_plate': declared,
        }, content_type='multipart/form-data')
        payload = response.get_json()
        result = payload.get('result', {})
        # Registrar lo observado, incluso si el modelo falla o lee otra matrícula.
        row = {
            'case': name, 'input': filename, 'http_status': response.status_code,
            'input_sha256': hashlib.sha256(data).hexdigest(),
            'expected_validation_status': 'coincide' if name == 'coincidencia' else name,
            'matches_expected_status': result.get('validation', {}).get('status') ==
                                       ('coincide' if name == 'coincidencia' else name),
            'error': payload.get('error'),
            'plate_count': len(result.get('plates', [])),
            'validation': result.get('validation'),
            'plates': result.get('plates', []),
            'processing_ms': result.get('processing_ms'),
            'model_load_ms': result.get('model_load_ms'),
        }
        report['cases'].append(row)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(row, ensure_ascii=False), flush=True)
    report['all_requests_succeeded'] = all(r['http_status'] == 200 for r in report['cases'])
    report['all_expected_statuses_observed'] = all(r['matches_expected_status'] for r in report['cases'])
    report['note'] = 'Tres ejemplos funcionales; no constituyen una evaluación estadística de precisión.'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Informe: {output}', flush=True)
    if not report['all_requests_succeeded']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
