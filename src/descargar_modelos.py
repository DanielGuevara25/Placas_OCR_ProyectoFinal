"""Descarga opcional de checkpoints publicados, con verificación SHA256.

El clon normal de Git ya incluye los tres .pt; este comando permite recuperarlos.
"""
import argparse
import hashlib
import json
import os
import tempfile
import urllib.request
from pathlib import Path

from src.paths import ROOT


def download_verified(url, destination, expected_hash, expected_bytes):
    """No sustituye un archivo existente hasta verificar tamaño y hash."""
    destination = Path(destination)
    if destination.is_file() and hashlib.sha256(destination.read_bytes()).hexdigest() == expected_hash:
        return 'already_verified'
    if not url.startswith('https://'):
        raise ValueError('La descarga de modelos requiere HTTPS.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        digest, size = hashlib.sha256(), 0
        request = urllib.request.Request(url, headers={'User-Agent': 'PlacaLab-model-download'})
        with urllib.request.urlopen(request, timeout=60) as response:
            with tempfile.NamedTemporaryFile(dir=destination.parent, suffix='.download', delete=False) as stream:
                temp_path = Path(stream.name)
                while chunk := response.read(1024 * 1024):
                    size += len(chunk)
                    if size > expected_bytes:
                        raise ValueError('El archivo recibido supera el tamaño del manifiesto.')
                    digest.update(chunk)
                    stream.write(chunk)
        if size != expected_bytes or digest.hexdigest() != expected_hash:
            raise ValueError('El tamaño o SHA256 del modelo descargado no coincide.')
        os.replace(temp_path, destination)
        return 'downloaded_and_verified'
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', choices=['best', 'baseline', 'rotacion'], default='best')
    parser.add_argument('--dest', type=Path, help='Destino alternativo para verificar una descarga limpia.')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'models/manifest.json').read_text(encoding='utf-8'))
    record = manifest['available_checkpoints'][args.model]
    destination = args.dest or ROOT / record['path']
    state = download_verified(record['download_url'], destination, record['sha256'], record['bytes'])
    print(f'{args.model}: {state}; SHA256 correcto.')


if __name__ == '__main__':
    main()
