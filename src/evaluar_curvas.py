"""Evalua checkpoints locales de confianza en train/val y exporta curvas 300 DPI.
Ejecutar desde placas_ocr con el mismo entorno del entrenamiento.
No entrena ni evalua test. Reanuda las evaluaciones ya guardadas.
"""
from src.paths import ROOT
import argparse
import csv
import gc
import hashlib
import json
import multiprocessing
from pathlib import Path

EXPERIMENTOS = ['yolov9t_baseline', 'yolov9t_regularizacion', 'yolov9t_rotacion']
CAMPOS = ['experimento', 'epoca', 'split', 'sha256', 'precision', 'recall', 'map50', 'map50_95']

def huella(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def graficar(csv_path, salida):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    with csv_path.open(encoding='utf-8', newline='') as f:
        filas = list(csv.DictReader(f))
    for experimento in EXPERIMENTOS:
        fig, axes = plt.subplots(2, 2, figsize=(11, 8), constrained_layout=True)
        for ax, metrica, titulo in zip(axes.flat,
                ['map50_95', 'map50', 'precision', 'recall'],
                ['mAP@50-95', 'mAP@50', 'Precision', 'Recall']):
            for split, nombre in [('train', 'Entrenamiento'), ('val', 'Validacion')]:
                datos = sorted([r for r in filas if r['experimento'] == experimento and r['split'] == split],
                               key=lambda r: int(r['epoca']))
                ax.plot([int(r['epoca']) for r in datos], [float(r[metrica]) for r in datos], label=nombre)
            ax.set(title=titulo, xlabel='Epoca', ylabel='Valor', ylim=(0, 1))
            ax.grid(alpha=0.25)
            ax.legend()
        fig.suptitle(experimento + ' — evaluacion sin aumentos')
        fig.savefig(salida / (experimento + '_train_val.png'), dpi=300)
        plt.close(fig)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=Path, default=ROOT)
    parser.add_argument('--solo-graficas', action='store_true')
    args = parser.parse_args()
    base = args.base.resolve()
    salida = base / 'results/overfitting'
    salida.mkdir(exist_ok=True)
    csv_path = salida / 'metricas_por_epoca.csv'
    if args.solo_graficas:
        graficar(csv_path, salida)
        return
    import torch
    import ultralytics
    from ultralytics import YOLO
    if ultralytics.__version__ != '8.4.171':
        raise RuntimeError('Usa el entorno original: Ultralytics 8.4.171.')
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA no esta disponible en este entorno.')
    data = base / 'data/processed/dataset_placas' / 'data_entrenamiento.yaml'
    if not data.is_file():
        raise FileNotFoundError(data)
    ajustes = dict(data=str(data), imgsz=640, batch=16, device=0, workers=4,
                   conf=0.001, iou=0.7, max_det=300, augment=False, rect=True,
                   half=False, plots=False, save_json=False, save_txt=False,
                   verbose=False, project=str(salida / 'evaluaciones'),
                   name='temporal', exist_ok=True)
    config = {'ultralytics': ultralytics.__version__, 'torch': torch.__version__,
              'data_sha256': huella(data), 'ajustes': ajustes}
    manifiesto = salida / 'configuracion_evaluacion.json'
    if manifiesto.exists() and json.loads(manifiesto.read_text(encoding='utf-8')) != config:
        raise RuntimeError('Cambio la configuracion. Usa otra carpeta de salida para evitar mezclar evaluaciones.')
    manifiesto.write_text(json.dumps(config, indent=2), encoding='utf-8')
    pendientes = []
    for experimento in EXPERIMENTOS:
        carpeta = base / 'results/training' / experimento / 'weights'
        pesos = list(carpeta.glob('epoch*.pt'))
        if len(pesos) != 100:
            raise RuntimeError(f'{experimento}: se esperaban 100 checkpoints; hay {len(pesos)}.')
        # Checkpoints creados por tus propios entrenamientos; nunca usar archivos no confiables.
        for peso in pesos:
            ckpt = torch.load(peso, map_location='cpu', weights_only=False)
            epoca = int(ckpt['epoch']) + 1
            del ckpt
            if not 1 <= epoca <= 100:
                raise RuntimeError(f'Epoca invalida en {peso}: {epoca}')
            pendientes.append((experimento, epoca, peso, huella(peso)))
        epocas = [e for x, e, _, _ in pendientes if x == experimento]
        if sorted(epocas) != list(range(1, 101)):
            raise RuntimeError(f'{experimento}: faltan epocas o hay epocas repetidas.')
    completadas = set()
    if csv_path.exists():
        with csv_path.open(encoding='utf-8', newline='') as f:
            for r in csv.DictReader(f):
                completadas.add((r['experimento'], int(r['epoca']), r['split'], r['sha256']))
        actuales = {(x, e, h) for x, e, _, h in pendientes}
        if any((x, e, h) not in actuales for x, e, s, h in completadas):
            raise RuntimeError('Se modificaron checkpoints ya evaluados. No mezcles ejecuciones en este CSV.')
    for experimento, epoca, peso, sha in sorted(pendientes, key=lambda x: (x[0], x[1])):
        for split in ['train', 'val']:
            clave = (experimento, epoca, split, sha)
            if clave in completadas:
                continue
            print(f'\nEVALUANDO {experimento} | epoca {epoca}/100 | {split}', flush=True)
            modelo = YOLO(str(peso))
            metricas = modelo.val(split=split, **ajustes)
            p, r, ap50, ap = metricas.box.mean_results()
            fila = dict(zip(CAMPOS, [experimento, epoca, split, sha, float(p), float(r), float(ap50), float(ap)]))
            nueva = not csv_path.exists() or csv_path.stat().st_size == 0
            with csv_path.open('a', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=CAMPOS)
                if nueva:
                    writer.writeheader()
                writer.writerow(fila)
            completadas.add(clave)
            del modelo, metricas
            gc.collect()
            torch.cuda.empty_cache()
        graficar(csv_path, salida)
    print(f'\nTerminado: {csv_path}\nGraficas en: {salida}')

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
