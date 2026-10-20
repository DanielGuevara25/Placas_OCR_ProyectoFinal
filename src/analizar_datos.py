"""Audita imágenes, etiquetas y particiones existentes sin modificarlas.

Ejecutar: python -m src.analizar_datos
"""
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from src.paths import DATASET, ROOT

SPLITS = ('train', 'val', 'test')
COLORS = ('#536c88', '#14866d', '#b46b25')
EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def describe(values):
    if not values:
        return None
    a = np.asarray(values, dtype=float)
    q = np.percentile(a, [0, 25, 50, 75, 100])
    return dict(zip(('min', 'q25', 'median', 'q75', 'max'), map(float, q)),
                mean=float(a.mean()), std=float(a.std()))


def main():
    figures = ROOT / 'results/figures/eda'
    figures.mkdir(parents=True, exist_ok=True)
    (ROOT / 'results/metrics').mkdir(parents=True, exist_ok=True)
    manifest_path = DATASET / 'particiones.csv'
    manifest = read_csv(manifest_path)
    expected = {}
    manifest_groups = defaultdict(set)
    issues = []
    for row in manifest:
        original = Path(row['imagen_original'])
        relative = original.parent / (original.name.replace('.', '_') + original.suffix.lower())
        key = row['particion'] + '/' + relative.as_posix()
        if key in expected:
            issues.append({'kind': 'duplicate_manifest_path', 'path': key})
        expected[key] = row['grupo']
        manifest_groups[row['grupo']].add(row['particion'])

    file_groups, pixel_groups = defaultdict(list), defaultdict(list)
    summaries, images, boxes = {}, [], []
    seen = set()
    for split in SPLITS:
        image_root, label_root = DATASET / 'images' / split, DATASET / 'labels' / split
        photos = sorted(p for p in image_root.rglob('*') if p.suffix.lower() in EXTENSIONS)
        label_files = set(label_root.rglob('*.txt'))
        matched_labels = set()
        s = Counter(images=len(photos))
        for index, photo in enumerate(photos, 1):
            relative = photo.relative_to(image_root)
            key = split + '/' + relative.as_posix()
            seen.add(key)
            data = photo.read_bytes()
            file_groups[hashlib.sha256(data).hexdigest()].append(key)
            image = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                s['unreadable_images'] += 1
                issues.append({'kind': 'unreadable_image', 'path': key})
                continue
            height, width = image.shape[:2]
            digest = hashlib.sha256()
            digest.update(str(image.shape).encode())
            digest.update(image.tobytes())
            pixel_hash = digest.hexdigest()
            pixel_groups[pixel_hash].append(key)
            if key not in expected or expected[key] != pixel_hash:
                issues.append({'kind': 'manifest_pixel_mismatch', 'path': key})
                s['manifest_mismatches'] += 1
            label = label_root / relative.with_suffix('.txt')
            count = 0
            if not label.is_file():
                s['missing_labels'] += 1
                issues.append({'kind': 'missing_label', 'path': key})
            else:
                matched_labels.add(label)
                lines = [line for line in label.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
                s['empty_labels'] += not lines
                for number, line in enumerate(lines, 1):
                    try:
                        parts = line.split()
                        if len(parts) != 5 or parts[0] != '0':
                            raise ValueError('Se espera clase 0 y cuatro coordenadas.')
                        x, y, w, h = map(float, parts[1:])
                        if not all(math.isfinite(v) for v in (x, y, w, h)):
                            raise ValueError('Coordenadas no finitas.')
                        if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < w <= 1 and 0 < h <= 1):
                            raise ValueError('Coordenadas normalizadas fuera de rango.')
                        if x-w/2 < -1e-5 or y-h/2 < -1e-5 or x+w/2 > 1+1e-5 or y+h/2 > 1+1e-5:
                            raise ValueError('Caja fuera de la imagen.')
                        boxes.append({'split': split, 'x': x, 'y': y, 'w': w, 'h': h,
                                      'area_pct': w*h*100, 'width_px': w*width,
                                      'height_px': h*height, 'aspect_ratio': w*width/(h*height)})
                        count += 1
                    except ValueError as exc:
                        s['invalid_label_lines'] += 1
                        issues.append({'kind': 'invalid_label', 'path': key, 'line': number, 'error': str(exc)})
            s['valid_boxes'] += count
            s['readable_images'] += 1
            s['multi_plate_images'] += count > 1
            images.append({'split': split, 'width': width, 'height': height,
                           'box_count': count, 'bytes': len(data)})
            if index % 1000 == 0:
                print(f'{split}: {index}/{len(photos)} imágenes auditadas', flush=True)
        s['orphan_labels'] = len(label_files - matched_labels)
        summaries[split] = dict(s)
        print(f'{split}: {json.dumps(summaries[split])}', flush=True)

    def duplicate_summary(groups):
        repeated = [items for items in groups.values() if len(items) > 1]
        crossed = [items for items in repeated if len({k.split('/')[0] for k in items}) > 1]
        return {'duplicate_groups': len(repeated), 'images_in_duplicate_groups': sum(map(len, repeated)),
                'cross_split_groups': len(crossed)}

    for missing in sorted(set(expected) - seen):
        issues.append({'kind': 'missing_manifest_image', 'path': missing})
    review = read_csv(ROOT / 'data/annotations/anotaciones_propuestas/revision.csv')
    report = {
        'scope': 'Auditoría local de imágenes y etiquetas; no entrenamiento ni inferencia.',
        'splits': summaries, 'total_images': sum(s['images'] for s in summaries.values()),
        'total_valid_boxes': len(boxes), 'manifest_rows': len(manifest),
        'manifest_group_crossings': sum(len(v) > 1 for v in manifest_groups.values()),
        'file_duplicates': duplicate_summary(file_groups),
        'decoded_pixel_duplicates': duplicate_summary(pixel_groups),
        'issue_count': len(issues),
        'review_rows': len(review),
        'review_marked_yes': sum(r.get('revisado', '').strip().upper() == 'SI' for r in review),
        'review_statuses': dict(Counter(r.get('estado') for r in review)),
        'excluded_rows': len(read_csv(DATASET / 'excluidas.csv')),
        'image_width_px': describe([r['width'] for r in images]),
        'image_height_px': describe([r['height'] for r in images]),
        'image_bytes': describe([r['bytes'] for r in images]),
        'boxes_per_image': dict(sorted(Counter(r['box_count'] for r in images).items())),
        'box_area_pct': describe([r['area_pct'] for r in boxes]),
        'box_width_px': describe([r['width_px'] for r in boxes]),
        'box_height_px': describe([r['height_px'] for r in boxes]),
        'box_aspect_ratio': describe([r['aspect_ratio'] for r in boxes]),
        'box_area_below_one_pct': sum(r['area_pct'] < 1 for r in boxes),
        'box_height_below_16_px': sum(r['height_px'] < 16 for r in boxes),
        'width_height_pearson_r': float(np.corrcoef([r['width'] for r in images], [r['height'] for r in images])[0, 1]),
        'manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        'limits': 'Sin auditoría de casi duplicados, vehículo/sesión, exactitud visual de cajas, legibilidad OCR ni procedencia/licencia.',
    }
    (ROOT / 'results/metrics/analisis_datos.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (ROOT / 'results/reports/dataset_audit_private.json').write_text(
        json.dumps(issues, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})

    def save(name):
        plt.gcf().savefig(figures / name, dpi=160, bbox_inches='tight')
        plt.close()

    x = np.arange(3)
    fig, ax = plt.subplots(figsize=(8, 5), layout='constrained')
    for offset, key, label, color in [(-.2, 'images', 'Imágenes', COLORS[0]), (.2, 'valid_boxes', 'Cajas válidas', COLORS[1])]:
        bars = ax.bar(x+offset, [summaries[s][key] for s in SPLITS], .4, label=label, color=color)
        ax.bar_label(bars, padding=3)
    ax.set(xticks=x, xticklabels=SPLITS, ylabel='Cantidad', title='1. Distribución por partición')
    ax.legend()
    save('01_particiones.png')

    fig, ax = plt.subplots(figsize=(8, 5), layout='constrained')
    counts = Counter(r['box_count'] for r in images)
    bars = ax.bar([str(k) for k in sorted(counts)], [counts[k] for k in sorted(counts)], color=COLORS[0])
    ax.bar_label(bars, padding=3)
    ax.set(xlabel='Cajas válidas por imagen', ylabel='Imágenes', title='2. Multiplicidad de placas anotadas')
    save('02_placas_por_imagen.png')

    fig, ax = plt.subplots(figsize=(8, 5), layout='constrained')
    for split, color in zip(SPLITS, COLORS):
        rows = [r for r in images if r['split'] == split]
        ax.scatter([r['width'] for r in rows], [r['height'] for r in rows], s=12, alpha=.25, color=color, label=split)
    ax.set(xlabel='Ancho original (px)', ylabel='Alto original (px)', title='3. Resolución de las fotografías')
    ax.legend()
    save('03_resoluciones.png')

    fig, ax = plt.subplots(figsize=(8, 5), layout='constrained')
    ax.boxplot([[r['area_pct'] for r in boxes if r['split'] == s] for s in SPLITS], tick_labels=SPLITS)
    ax.set(ylabel='Área de la caja / área de imagen (%)', title='4. Tamaño relativo de las placas anotadas')
    save('04_area_placas.png')

    fig, ax = plt.subplots(figsize=(8, 5), layout='constrained')
    h = ax.hist2d([r['x'] for r in boxes], [r['y'] for r in boxes], bins=25, range=[[0, 1], [0, 1]], cmap='viridis')
    ax.invert_yaxis()
    ax.set(xlabel='Centro x normalizado', ylabel='Centro y normalizado (origen arriba)', title='5. Ubicación de las cajas anotadas')
    fig.colorbar(h[3], ax=ax, label='Cajas por celda')
    save('05_centros.png')

    fig, ax = plt.subplots(figsize=(8, 5), layout='constrained')
    bins = np.linspace(0, max(r['aspect_ratio'] for r in boxes), 35)
    for split, color in zip(SPLITS, COLORS):
        ax.hist([r['aspect_ratio'] for r in boxes if r['split'] == split], bins=bins,
                density=True, histtype='step', linewidth=2, label=split, color=color)
    ax.set(xlabel='Ancho / alto de caja (píxeles)', ylabel='Densidad', title='6. Forma de las cajas por partición')
    ax.legend()
    save('06_forma_placas.png')
    print(json.dumps(report, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
