"""Evalúa el OCR de la web sobre recortes anotados y transcripciones manuales."""
from src.paths import ROOT
import argparse
import csv
import hashlib
import json
import math
import re
import time
from collections import Counter
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def normalize(text):
    return re.sub(r'[\s-]+', '', text.upper())


def distance(reference, prediction):
    previous = list(range(len(prediction) + 1))
    for i, a in enumerate(reference, 1):
        current = [i]
        for j, b in enumerate(prediction, 1):
            current.append(min(current[-1]+1, previous[j]+1, previous[j-1]+(a != b)))
        previous = current
    return previous[-1]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_review(csv_path, manifest_path, folder):
    manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    with csv_path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ['id', 'texto_real', 'estado', 'observaciones']:
            raise ValueError('Columnas inesperadas en las transcripciones.')
        rows = list(reader)
    ids = [row['id'] for row in rows]
    expected = [row['id'] for row in manifest['records']]
    if len(ids) != len(set(ids)) or len(expected) != len(set(expected)) or set(ids) != set(expected):
        raise ValueError('IDs duplicados o discrepancia entre transcripciones y manifiesto.')
    if len(expected) != manifest['sample_plates']:
        raise ValueError('El total del manifiesto no coincide con sus registros.')
    for row in rows:
        if not re.fullmatch(r'placa_\d+', row['id']):
            raise ValueError('Identificador de recorte inválido.')
        if row['estado'] not in {'legible', 'ilegible', 'caja_incorrecta'}:
            raise ValueError(f"Falta revisar {row['id']}.")
        if row['estado'] == 'legible' and not re.fullmatch(r'[A-Z0-9]{2,12}', normalize(row['texto_real'])):
            raise ValueError(f"Transcripción legible inválida: {row['id']}.")
        if not (folder / 'recortes' / (row['id']+'.png')).is_file():
            raise ValueError(f"Falta el recorte {row['id']}.png.")
    if not any(row['estado'] == 'legible' for row in rows):
        raise ValueError('No hay transcripciones legibles para calcular métricas.')
    return rows, manifest


def evaluate(rows, read_crop, folder):
    details = []
    for index, row in enumerate(rows, 1):
        crop = folder / 'recortes' / (row['id']+'.png')
        error = None
        started = time.perf_counter()
        try:
            text, probabilities = read_crop(crop)
            probabilities = [float(p) for p in probabilities]
            if len(text) != len(probabilities) or any(not math.isfinite(p) or not 0 <= p <= 1 for p in probabilities):
                raise ValueError('Confianzas OCR inválidas o desalineadas.')
        except Exception as exc:
            # Un fallo en un recorte legible NO se elimina del denominador.
            text, probabilities, error = '', [], str(exc)
        elapsed = (time.perf_counter()-started)*1000
        reference = normalize(row['texto_real']) if row['estado']=='legible' else None
        prediction = normalize(text)
        edits = distance(reference, prediction) if reference is not None else None
        details.append({'id':row['id'], 'estado_manual':row['estado'],
                        'texto_real':reference, 'ocr_original':text, 'ocr_normalizado':prediction,
                        'coincide':prediction==reference if reference is not None else None,
                        'distancia_edicion':edits, 'caracteres_referencia':len(reference) if reference else None,
                        'confianza_media':sum(probabilities)/len(probabilities) if probabilities else None,
                        'confianzas_caracter':probabilities, 'error_ocr':error,
                        'ocr_ms':round(elapsed,3), 'sha256_recorte':sha256(crop)})
        print(f"[{index}/{len(rows)}] {row['id']}: {row['estado']}", flush=True)
    scored = [row for row in details if row['texto_real'] is not None]
    edits = sum(row['distancia_edicion'] for row in scored)
    characters = sum(row['caracteres_referencia'] for row in scored)
    correct = sum(row['coincide'] for row in scored)
    states = dict(Counter(row['estado'] for row in rows))
    summary = {'total_recortes':len(rows), 'estados_manuales':states,
               'placas_evaluables':len(scored), 'cobertura_transcripcion':len(scored)/len(rows),
               'placas_exactas':correct, 'exactitud_placa':correct/len(scored),
               'errores_edicion':edits, 'caracteres_referencia':characters, 'cer':edits/characters,
               'fallos_ocr_legibles':sum(row['error_ocr'] is not None for row in scored),
               'lecturas_vacias_legibles':sum(not row['ocr_normalizado'] for row in scored),
               'estado_ejecucion':'fallo_total_ocr' if all(row['error_ocr'] is not None for row in scored) else 'completada',
               'alcance':'OCR aislado sobre cajas anotadas de test; métricas condicionadas a transcripción legible, no del sistema completo.',
               'normalizacion':'Mayúsculas, quitar espacios y guiones; sin completar ceros ni sustituir letras por números.',
               'formula_cer':'Suma de distancias Levenshtein / suma de caracteres de referencia. Puede exceder 1 por inserciones.',
               'exclusiones':'Ilegibles y cajas incorrectas se cuentan y reportan aparte; fallos OCR en legibles cuentan como predicción vacía.',
               'limitaciones':'Muestra pequeña con imágenes potencialmente relacionadas; no se estima independencia ni se calibra confianza. No se ajustan modelos ni umbrales usando estos resultados.'}
    return summary, details


def run(args):
    rows, manifest = load_review(args.csv, args.manifest, args.folder)
    if args.output.exists() and any(args.output.iterdir()):
        raise ValueError('La salida ya contiene archivos. Usa --output con otra carpeta.')
    # Mismo wrapper y tratamiento BGR -> RGB que la aplicación entregada.
    import numpy as np
    from PIL import Image
    from src.config import LicensePlateConfig
    from src.providers import ComputeBackend
    from app.web_ocr import WebOCR
    started = time.perf_counter()
    cfg = LicensePlateConfig(compute_backend=ComputeBackend.CPU)
    ocr = WebOCR(cfg)
    load_ms = (time.perf_counter()-started)*1000

    def read_crop(path):
        with Image.open(path) as photo:
            bgr = np.ascontiguousarray(np.asarray(photo.convert('RGB'))[:, :, ::-1])
        chars, probs = ocr.read(bgr)
        return ''.join(chars), probs

    summary, details = evaluate(rows, read_crop, args.folder)
    packages = {}
    for package in ['fast-plate-ocr', 'onnxruntime', 'onnxruntime-gpu', 'numpy', 'Pillow']:
        try:
            packages[package] = version(package)
        except PackageNotFoundError:
            pass
    summary.update({'fecha_utc':datetime.now(timezone.utc).isoformat(), 'modelo':cfg.ocr_model,
                    'dispositivo_ocr':'CPU', 'interpolacion':'cubic', 'carga_modelo_ms':round(load_ms,2),
                    'semilla_muestra':manifest['seed'], 'imagenes_muestra':manifest['sample_images'],
                    'sha256_transcripciones':sha256(args.csv), 'sha256_manifest':sha256(args.manifest),
                    'versiones':packages})
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output/'metricas_ocr.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    (args.output/'detalle_ocr.json').write_text(json.dumps(details,ensure_ascii=False,indent=2),encoding='utf-8')
    with (args.output/'detalle_ocr.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f,fieldnames=list(details[0]))
        writer.writeheader()
        writer.writerows(details)
    print(f"Exactitud: {correct_percent(summary):.2f}% ({summary['placas_exactas']}/{summary['placas_evaluables']})")
    print(f"CER: {100*summary['cer']:.2f}%; cobertura de transcripción: {100*summary['cobertura_transcripcion']:.2f}%")
    print(f'Archivos guardados en {args.output.resolve()}')
    if summary['estado_ejecucion']=='fallo_total_ocr':
        raise ValueError('Fallaron todas las lecturas: revisa detalle_ocr.json; no presentes esto como rendimiento válido del modelo.')


def correct_percent(summary):
    return 100*summary['exactitud_placa']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder',type=Path,default=ROOT / 'data/review/revision_ocr_test')
    parser.add_argument('--csv',type=Path,default=ROOT / 'data/review/revision_ocr_test/transcripciones_revisadas.csv')
    parser.add_argument('--manifest',type=Path,default=ROOT / 'data/review/revision_ocr_test/manifest_privado.json')
    parser.add_argument('--output',type=Path,default=ROOT / 'results/ocr')
    args = parser.parse_args()
    try:
        run(args)
    except (OSError, ValueError, ImportError, RuntimeError) as exc:
        parser.exit(1,f'No se pudo completar la evaluación: {exc}\n')
