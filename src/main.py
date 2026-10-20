"""Detección y OCR por fotografía, sin vehículos ni tracking."""
import argparse
import json
import time
from pathlib import Path
import cv2
import numpy as np
from src.config import LicensePlateConfig
from src.providers import ComputeBackend
from src.plate_detector import PlateDetector
from src.ocr_engine import OCREngine


def process_image(image, detector, ocr):
    started = time.perf_counter()
    height, width = image.shape[:2]
    rows = []
    annotated = image.copy()
    for box in detector.detect(image):
        x1, y1, x2, y2 = map(int, box[:4])
        x1, x2 = max(0, min(width, x1)), max(0, min(width, x2))
        y1, y2 = max(0, min(height, y1)), max(0, min(height, y2))
        if x2 <= x1 or y2 <= y1:
            continue
        crop = image[y1:y2, x1:x2]
        chars, probs = ocr.read(crop)
        text = ''.join(chars)
        row = {'bbox': [x1, y1, x2, y2], 'detection_confidence': float(box[4]),
               'plate_text': text, 'character_confidences': probs,
               'ocr_mean_confidence': float(np.mean(probs)) if probs else None}
        rows.append((row, crop))
        cv2.rectangle(annotated, (x1,y1),(x2,y2),(40,210,40),2)
        cv2.putText(annotated, text or 'Sin lectura', (x1, max(20,y1-7)),
                    cv2.FONT_HERSHEY_SIMPLEX, .7, (40,210,40),2)
    return rows, annotated, (time.perf_counter()-started)*1000


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path, help='Foto o carpeta de fotos')
    parser.add_argument('--output', default=Path('results/predictions/individual'), type=Path)
    parser.add_argument('--backend', choices=['fast','yolo'], default='fast')
    parser.add_argument('--device', choices=['cpu','cuda'], default='cpu')
    args = parser.parse_args()
    paths = [args.input] if args.input.is_file() else sorted(p for p in args.input.iterdir() if p.suffix.lower() in {'.jpg','.jpeg','.png','.webp','.bmp'})
    if not paths: parser.error('No hay imágenes para procesar.')
    cfg = LicensePlateConfig(detector_backend=args.backend,
        compute_backend=ComputeBackend(args.device), device='0' if args.device=='cuda' else 'cpu')
    detector, ocr = PlateDetector(cfg), OCREngine(cfg)
    args.output.mkdir(parents=True, exist_ok=True)
    results = []
    for index, path in enumerate(paths):
        image = cv2.imread(str(path))
        if image is None:
            results.append({'image':str(path),'error':'Imagen ilegible'}); continue
        rows, annotated, elapsed = process_image(image,detector,ocr)
        prefix = f'{index:04d}_{path.stem}'
        cv2.imwrite(str(args.output / f'{prefix}_deteccion.jpg'), annotated)
        for number, (row, crop) in enumerate(rows):
            crop_name = f'{prefix}_placa_{number}.jpg'
            cv2.imwrite(str(args.output / crop_name),crop)
            row['crop_file'] = crop_name
        result = {'image':str(path),'plates':[row for row,crop in rows],'processing_ms':round(elapsed,2)}
        results.append(result)
        print(json.dumps(result,ensure_ascii=False))
    (args.output/'resultados.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__ == '__main__': main()
