"""Resume evidencias existentes; no entrena ni vuelve a evaluar modelos.

Ejecutar desde la raíz: python -m src.comparar_experimentos
"""
import csv
import hashlib
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yaml

from src.paths import ROOT

NAMES = ['yolov9t_baseline', 'yolov9t_regularizacion', 'yolov9t_rotacion']
LABELS = ['Baseline', 'Regularización', 'Rotación']
MAP = 'metrics/mAP50-95(B)'


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return [{k.strip(): v.strip() for k, v in row.items()} for row in csv.DictReader(stream)]


def main():
    metrics = ROOT / 'results/metrics'
    figures = ROOT / 'results/figures'
    for path in (metrics, figures):
        path.mkdir(parents=True, exist_ok=True)
    reevaluation_path = ROOT / 'results/overfitting/metricas_por_epoca.csv'
    reeval = read_csv(reevaluation_path)
    assert len(reeval) == 600, 'Se esperaban 3 experimentos x 100 épocas x 2 splits.'
    sources = [reevaluation_path]
    summaries, training, configs = [], {}, {}
    for name in NAMES:
        folder = ROOT / 'results/training' / name
        path, config_path = folder / 'results.csv', folder / 'args.yaml'
        rows = read_csv(path)
        sources += [path, config_path]
        assert [int(r['epoch']) for r in rows] == list(range(1, 101))
        for row in rows:
            for key in ('metrics/precision(B)', 'metrics/recall(B)', 'metrics/mAP50(B)', MAP):
                assert math.isfinite(float(row[key])) and 0 <= float(row[key]) <= 1
        config = yaml.safe_load(config_path.read_text(encoding='utf-8'))
        configs[name], training[name] = config, rows
        best = max(rows, key=lambda r: float(r[MAP]))
        selected = {}
        for split in ('train', 'val'):
            selected[split] = [r for r in reeval if r['experimento'] == name and r['split'] == split]
            assert sorted(int(r['epoca']) for r in selected[split]) == list(range(1, 101))
            for row in selected[split]:
                assert all(math.isfinite(float(row[k])) and 0 <= float(row[k]) <= 1
                           for k in ('precision', 'recall', 'map50', 'map50_95'))
        by_epoch = {r['epoca']: r for r in selected['train']}
        assert all(by_epoch[r['epoca']]['sha256'] == r['sha256'] for r in selected['val'])
        best_re = max(selected['val'], key=lambda r: float(r['map50_95']))
        train_re = by_epoch[best_re['epoca']]
        summaries.append({
            'experiment': name, 'epochs': len(rows),
            'weight_decay': config['weight_decay'], 'degrees': config['degrees'],
            'best_logged_epoch': int(best['epoch']),
            'precision': float(best['metrics/precision(B)']),
            'recall': float(best['metrics/recall(B)']),
            'map50': float(best['metrics/mAP50(B)']),
            'map50_95': float(best[MAP]),
            'last_map50_95': float(rows[-1][MAP]),
            'recorded_training_minutes': float(rows[-1]['time']) / 60,
            'reevaluated_best_epoch': int(best_re['epoca']),
            'reevaluated_val_map50_95': float(best_re['map50_95']),
            'reevaluated_train_map50_95': float(train_re['map50_95']),
            'reevaluated_gap_pp': 100 * (float(train_re['map50_95']) - float(best_re['map50_95'])),
        })
    for row in summaries:
        row['improvement_over_baseline_pp'] = 100 * (row['map50_95'] - summaries[0]['map50_95'])
    ignored = {'model', 'name', 'save_dir'}
    differences = {name: {k: {'baseline': configs[NAMES[0]].get(k), 'experiment': v}
                         for k, v in configs[name].items()
                         if k not in ignored and configs[NAMES[0]].get(k) != v}
                   for name in NAMES}
    assert set(differences[NAMES[1]]) == {'weight_decay'}
    assert set(differences[NAMES[2]]) == {'degrees'}
    report = {
        'scope': 'Análisis de archivos históricos, sin nueva inferencia ni entrenamiento.',
        'selection_metric': 'Mayor mAP50-95 de validación, no test.',
        'runs_per_configuration': 1,
        'config_differences_excluding_model_path_and_output_names': differences,
        'experiments': summaries,
        'sources_sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sources},
    }
    (metrics / 'comparacion_experimentos.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with (metrics / 'comparacion_experimentos.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)

    colors = ['#536c88', '#14866d', '#b46b25']
    plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), layout='constrained')
    for name, label, color in zip(NAMES, LABELS, colors):
        rows = training[name]
        x = [int(r['epoch']) for r in rows]
        axes[0].plot(x, [100 * float(r[MAP]) for r in rows], label=label, color=color)
        axes[1].plot(x, [float(r['val/box_loss']) for r in rows], label=label, color=color)
    axes[0].set(title='mAP50-95 de validación', xlabel='Época', ylabel='mAP50-95 (%)')
    axes[1].set(title='Pérdida de localización en validación', xlabel='Época', ylabel='val/box_loss')
    for ax in axes:
        ax.grid(alpha=.2)
        ax.legend()
    fig.suptitle('YOLOv9t: registros de entrenamiento, una corrida por configuración')
    fig.savefig(figures / 'comparacion_entrenamiento.png', dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), layout='constrained')
    bars = axes[0].bar(LABELS, [r['map50_95'] * 100 for r in summaries], color=colors)
    axes[0].set(title='Mejor mAP50-95 registrado en validación', ylabel='mAP50-95 (%)', ylim=(0, 100))
    axes[0].bar_label(bars, labels=[f"{r['map50_95'] * 100:.3f}%\népoca {r['best_logged_epoch']}" for r in summaries], padding=3)
    bars = axes[1].bar(LABELS, [r['reevaluated_gap_pp'] for r in summaries], color=colors)
    axes[1].set(title='Brecha train - val en reevaluación sin aumentos',
                ylabel='Puntos porcentuales', ylim=(0, 5))
    axes[1].bar_label(bars, labels=[f"{r['reevaluated_gap_pp']:.3f} pp\népoca {r['reevaluated_best_epoch']}" for r in summaries], padding=3)
    fig.suptitle('Dos fuentes distintas: registro de entrenamiento y reevaluación de checkpoints')
    fig.savefig(figures / 'comparacion_modelos.png', dpi=180)
    plt.close(fig)
    for row in summaries:
        print(json.dumps(row, ensure_ascii=False))


if __name__ == '__main__':
    main()
