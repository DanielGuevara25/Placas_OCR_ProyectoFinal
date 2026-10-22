"""Servidor local de la demo protegida. Nunca se enlaza a la red local."""
from pathlib import Path
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    credentials = json.loads((ROOT / '.model-cache/demo/acceso.json').read_text(encoding='utf-8'))
    os.environ['DEMO_USER'] = credentials['username']
    os.environ['DEMO_PASSWORD'] = credentials['password']
    os.environ.setdefault('YOLO_CONFIG_DIR', str(ROOT / '.model-cache/ultralytics'))
    os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.model-cache/matplotlib'))
    os.environ.setdefault('YOLO_OFFLINE', 'true')
    from app.app import create_app
    from app.web_service import WebSettings
    from waitress import serve
    app = create_app(settings=WebSettings(ROOT / 'models/best.pt', device='cpu'))
    # Debug desactivado; un proceso, cuatro hilos y una inferencia simultánea.
    app.debug = False
    serve(app, host='127.0.0.1', port=8081, threads=4,
          max_request_body_size=12*1024*1024+128*1024,
          channel_timeout=60, connection_limit=32, ident='PlacaLab')


if __name__ == '__main__':
    main()
