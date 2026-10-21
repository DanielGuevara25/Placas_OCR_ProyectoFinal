"""Estudio GPU reanudable. No lee ni evalúa la partición test.

Ejecutar desde la raíz: python tools/estudio_semana5.py
Los ensayos son una aproximación de bajo presupuesto; los dos ajustes finales
usan train completo y 100 épocas. No se sustituyen las métricas históricas.
"""
from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import os
from pathlib import Path
import platform
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/semana5"
CACHE = ROOT / ".model-cache/semana5"
os.environ.setdefault("YOLO_CONFIG_DIR", str(ROOT / ".model-cache/ultralytics"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".model-cache/matplotlib"))
os.environ.setdefault("YOLO_OFFLINE", "true")


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    tmp.replace(path)


def sha(path):
    with open(path, "rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def status(stage, **details):
    value = {"stage": stage, "updated": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **details}
    dump(OUT / "estado.json", value)
    print(json.dumps(value, ensure_ascii=False), flush=True)


def export_trials(study):
    rows = [{"number": t.number, "state": t.state.name, "value": t.value,
             **t.params, "seconds": t.duration.total_seconds() if t.duration else None,
             "intermediate": dict(t.intermediate_values)} for t in study.trials]
    dump(OUT / "ensayos.json", rows)
    with (OUT / "ensayos.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["number", "state", "value", "weight_decay", "degrees", "seconds"])
        writer.writeheader()
        writer.writerows({k: r.get(k) for k in writer.fieldnames} for r in rows)


def analysis(study):
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.inspection import PartialDependenceDisplay, permutation_importance
    from sklearn.model_selection import cross_val_score, KFold
    complete = [t for t in study.trials if t.state.name == "COMPLETE"]
    if len(complete) < 10:
        dump(OUT / "sustituto.json", {"status": "insufficient", "completed": len(complete)})
        return
    x = np.array([[np.log10(t.params["weight_decay"]), t.params["degrees"]] for t in complete])
    y = np.array([t.value for t in complete])
    rf = RandomForestRegressor(n_estimators=300, min_samples_leaf=3, random_state=42, n_jobs=2)
    cv = KFold(5, shuffle=True, random_state=42)
    r2 = cross_val_score(rf, x, y, cv=cv, scoring="r2")
    mae = -cross_val_score(rf, x, y, cv=cv, scoring="neg_mean_absolute_error")
    rf.fit(x, y)
    # Importancia de permutación sobre todos los datos es descriptiva, no generalización.
    imp = permutation_importance(rf, x, y, n_repeats=30, random_state=42, n_jobs=2)
    import optuna
    importance = optuna.importance.get_param_importances(study)
    dump(OUT / "sustituto.json", {"completed": len(complete), "cv_r2": r2.tolist(),
         "cv_mae": mae.tolist(), "features": ["log10(weight_decay)", "degrees"],
         "permutation_training_descriptive": imp.importances_mean.tolist(),
         "optuna_fanova": importance, "warning": "PDP e interacciones exploratorias; no causales. Revisar R2 de CV y cobertura; no extrapolar al ajuste de 100 épocas."})
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot([t.number for t in complete], y, "o", label="Ensayo completo")
    ax.plot([t.number for t in complete], np.maximum.accumulate(y), label="Mejor acumulado")
    ax.set(xlabel="Ensayo", ylabel="mAP50–95 de validación (proxy)")
    ax.legend(); fig.tight_layout(); fig.savefig(OUT / "historial.png", dpi=160); plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for i, name in enumerate(["log10(weight_decay)", "degrees"]):
        axes[i].scatter(x[:, i], y, s=20); axes[i].set(xlabel=name, ylabel="mAP50–95 proxy")
    fig.tight_layout(); fig.savefig(OUT / "slice.png", dpi=160); plt.close(fig)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    PartialDependenceDisplay.from_estimator(rf, x, [0, 1, (0, 1)],
        feature_names=["log10(weight_decay)", "degrees"], ax=axes)
    fig.suptitle("Sustituto RF: dependencia parcial exploratoria (validación proxy)")
    fig.tight_layout(); fig.savefig(OUT / "pdp_interaccion.png", dpi=160); plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(list(importance), list(importance.values())); ax.set(ylabel="Importancia fANOVA")
    fig.tight_layout(); fig.savefig(OUT / "importancia.png", dpi=160); plt.close(fig)


def robustness(weights):
    """Predicciones a conf=.25, IoU de acierto=.5; bootstrap pareado por imagen.

    Se evalúan todas las imágenes val, sin reajustar umbrales. Los escenarios
    son transformaciones de validación y no representan nueva población.
    """
    import cv2
    import numpy as np
    from ultralytics import YOLO
    from PIL import Image
    paths = sorted((ROOT / "data/processed/dataset_placas/images/val").glob("*"))
    paths = [p for p in paths if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}]
    scenarios = ["limpio", "ruido_10", "ruido_25", "blur_5", "blur_9", "oscuro_05", "claro_15", "resolucion_05", "oclusion_10"]
    all_records = []
    for label, checkpoint in weights.items():
        model = YOLO(str(checkpoint))
        for scenario in scenarios:
            dest = OUT / f"robustez_{label}_{scenario}.json"
            if dest.exists():
                all_records.extend(json.loads(dest.read_text(encoding="utf-8"))); continue
            status("robustez", model=label, scenario=scenario)
            records = []
            for start in range(0, len(paths), 16):
                batch_paths = paths[start:start + 16]
                arrays, truths, areas = [], [], []
                for path in batch_paths:
                    im = np.asarray(Image.open(path).convert("RGB"))[:, :, ::-1].copy()
                    h, w = im.shape[:2]
                    gt = []
                    for line in (ROOT / "data/processed/dataset_placas/labels/val" / (path.stem + ".txt")).read_text().splitlines():
                        _, cx, cy, bw, bh = map(float, line.split())
                        gt.append([(cx-bw/2)*w, (cy-bh/2)*h, (cx+bw/2)*w, (cy+bh/2)*h])
                    gt = np.array(gt).reshape(-1, 4)
                    rng = np.random.default_rng(int(hashlib.sha256(path.name.encode()).hexdigest()[:8], 16) + 42)
                    if scenario.startswith("ruido"):
                        im = np.clip(im.astype(float) + rng.normal(0, int(scenario.split("_")[1]), im.shape), 0, 255).astype("uint8")
                    elif scenario.startswith("blur"):
                        k = int(scenario.split("_")[1]); im = cv2.GaussianBlur(im, (k, k), 0)
                    elif scenario == "oscuro_05": im = (im * .5).astype("uint8")
                    elif scenario == "claro_15": im = np.clip(im * 1.5, 0, 255).astype("uint8")
                    elif scenario == "resolucion_05": im = cv2.resize(cv2.resize(im, (max(1, w//2), max(1, h//2))), (w, h))
                    elif scenario == "oclusion_10":
                        # Franja vertical central del 10% del ancho de cada placa.
                        for x1, y1, x2, y2 in gt:
                            mid = (x1+x2)/2; half = .05*(x2-x1)
                            im[max(0,int(y1)):min(h,int(y2)+1), max(0,int(mid-half)):min(w,int(mid+half)+1)] = 127
                    arrays.append(im); truths.append(gt)
                    areas.append(((gt[:,2]-gt[:,0])*(gt[:,3]-gt[:,1])/(w*h)).tolist())
                predictions = model.predict(arrays, imgsz=640, conf=.25, iou=.7, device=0, verbose=False)
                for path, pred, gt, area in zip(batch_paths, predictions, truths, areas):
                    boxes = pred.boxes.xyxy.cpu().numpy()
                    conf = pred.boxes.conf.cpu().numpy()
                    used = set(); matched = []
                    for idx in np.argsort(-conf):
                        b = boxes[idx]
                        lo = np.maximum(b[:2], gt[:,:2]); hi = np.minimum(b[2:], gt[:,2:])
                        inter = np.maximum(hi-lo, 0).prod(axis=1)
                        union = (b[2:]-b[:2]).prod() + (gt[:,2:]-gt[:,:2]).prod(axis=1) - inter
                        iou = inter / np.maximum(union, 1e-9)
                        for j in used: iou[j] = -1
                        j = int(iou.argmax()) if len(iou) else -1
                        if j >= 0 and iou[j] >= .5: used.add(j); matched.append(j)
                    records.append({"image_sha256": sha(path), "model": label, "scenario": scenario,
                        "tp": len(used), "fp": len(boxes)-len(used), "fn": len(gt)-len(used),
                        "small_gt": sum(a < .01 for a in area),
                        "small_tp": sum(area[j] < .01 for j in matched)})
            dump(dest, records); all_records.extend(records)
        del model; gc.collect()
    summary = []
    for label in weights:
        clean = [r for r in all_records if r["model"] == label and r["scenario"] == "limpio"]
        clean_array = np.array([[r[k] for k in ("tp", "fp", "fn")] for r in clean])
        for scenario in scenarios:
            rows = [r for r in all_records if r["model"] == label and r["scenario"] == scenario]
            a = np.array([[r[k] for k in ("tp", "fp", "fn")] for r in rows])
            tp, fp, fn = a.sum(axis=0)
            rng = np.random.default_rng(42)
            inds = rng.integers(0, len(a), size=(2000, len(a)))
            bt, bf, bn = a[inds].sum(axis=1).T
            ct, cf, cn = clean_array[inds].sum(axis=1).T
            recall = bt/np.maximum(bt+bn, 1)
            drop = ct/np.maximum(ct+cn, 1)-recall
            summary.append({"model": label, "scenario": scenario, "n_images": len(a),
                "precision": float(tp/max(tp+fp,1)), "recall": float(tp/max(tp+fn,1)),
                "f1": float(2*tp/max(2*tp+fp+fn,1)),
                "recall_ci95": np.quantile(recall,[.025,.975]).tolist(),
                "recall_drop_vs_clean_ci95_paired": np.quantile(drop,[.025,.975]).tolist(),
                "small_recall": sum(r["small_tp"] for r in rows)/max(sum(r["small_gt"] for r in rows),1)})
    dump(OUT / "robustez_resumen.json", summary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=60)
    parser.add_argument("--proxy-epochs", type=int, default=12)
    parser.add_argument("--fraction", type=float, default=.35)
    parser.add_argument("--final-epochs", type=int, default=100)
    args = parser.parse_args()
    import torch
    import optuna
    import ultralytics
    from ultralytics import YOLO
    import yaml
    ultralytics.settings.update({"sync": False, "clearml": False, "comet": False,
        "dvc": False, "mlflow": False, "raytune": False, "wandb": False})
    if not torch.cuda.is_available(): raise RuntimeError("CUDA no disponible; no iniciar ensayos CPU por accidente")
    torch.ones(4, device="cuda").sum().item()
    OUT.mkdir(parents=True, exist_ok=True); CACHE.mkdir(parents=True, exist_ok=True)
    dataset = ROOT / "data/processed/dataset_placas"
    # Listado explícito de train y val; la configuración no contiene test.
    data_config = CACHE / "data.yaml"
    data_config.write_text(yaml.safe_dump({"path": str(dataset), "train": "images/train", "val": "images/val", "names": {0:"placa"}}), encoding="utf-8")
    plan = {"seed":42, "metric":"validation mAP50-95; best epoch within proxy budget",
        "trials":args.trials,"proxy_epochs":args.proxy_epochs,"fraction":args.fraction,
        "final_epochs":args.final_epochs, "parameters":{"weight_decay":[.0001,.003,"log"],"degrees":[0.,10.]},
        "sampler":"TPE, 10 startup trials", "pruner":"Median; 10 startup trials, 4 warmup epochs",
        "optimizer":"SGD", "lr0":.01, "momentum":.937,
        "gpu":torch.cuda.get_device_name(0),"torch":torch.__version__,"ultralytics":ultralytics.__version__,
        "python":platform.python_version(), "pretrained_sha256":sha(ROOT / "models/pretrained/yolov9t.pt"),
        "limitations":["Una semilla; IC de robustez por imagen no mide variación de entrenamiento",
            "Submuestra fija de train; ranking proxy puede cambiar a 100 épocas",
            "Val se reutiliza para búsqueda y análisis; resultados de desarrollo, no estimación independiente",
            "Sin negativos ni grupos por vehículo/sesión; no estima falsos positivos en población real",
            "Desbalance binario y caída de variables médicas no se trasladan literalmente a detección de una clase"]}
    plan_path = OUT / "plan.json"
    if plan_path.exists() and json.loads(plan_path.read_text(encoding="utf-8")) != plan:
        raise RuntimeError("El plan existente difiere: usar un nuevo directorio para otro estudio")
    dump(plan_path, plan)
    manifest = OUT / "datos_hashes.json"
    if not manifest.exists():
        hashes = {}
        for split in ("train", "val"):
            for kind in ("images", "labels"):
                for p in sorted((dataset/kind/split).glob("*")):
                    if p.is_file() and p.suffix != ".cache": hashes[p.relative_to(dataset).as_posix()] = sha(p)
        dump(manifest, hashes)
    baseline = yaml.safe_load((ROOT / "results/training/yolov9t_baseline/args.yaml").read_text())
    for key in ("save_dir", "model", "task", "mode"): baseline.pop(key, None)
    baseline.update(data=str(data_config), device=0, workers=0, project=str(CACHE / "training"),
        save=True, save_period=-1, plots=False, verbose=False, exist_ok=False,
        seed=42, deterministic=True, resume=False, optimizer="SGD", lr0=.01, momentum=.937)
    study = optuna.create_study(study_name="placas_s5_proxy_v1", storage="sqlite:///" + (CACHE / "optuna.sqlite3").as_posix(),
        direction="maximize", load_if_exists=True, sampler=optuna.samplers.TPESampler(seed=42, n_startup_trials=10),
        pruner=optuna.pruners.MedianPruner(n_startup_trials=10, n_warmup_steps=4))
    # Recuperación tras cierre del proceso: no presentar RUNNING como terminado.
    for t in study.get_trials(states=(optuna.trial.TrialState.RUNNING,)):
        study.tell(t.number, state=optuna.trial.TrialState.FAIL)
    if not study.trials:
        for wd, deg in [(.0005,0.),(.001,0.),(.0005,5.),(.001,5.)]:
            study.enqueue_trial({"weight_decay":wd,"degrees":deg})
    def objective(trial):
        wd = trial.suggest_float("weight_decay", .0001, .003, log=True)
        deg = trial.suggest_float("degrees", 0., 10.)
        status("busqueda", trial=trial.number, parameters=trial.params, total=args.trials)
        model = YOLO(str(ROOT / "models/pretrained/yolov9t.pt"))
        best = -1.
        def callback(trainer):
            nonlocal best
            metric = trainer.metrics.get("metrics/mAP50-95(B)")
            if metric is None: return
            best = max(best, float(metric)); trial.report(best, trainer.epoch+1)
            status("busqueda", trial=trial.number, epoch=trainer.epoch+1,
                proxy_epochs=args.proxy_epochs, best_map50_95=best, total=args.trials)
            if trial.should_prune(): raise optuna.TrialPruned()
        model.add_callback("on_fit_epoch_end", callback)
        try:
            model.train(**{**baseline, "name":f"proxy_{trial.number:03d}", "epochs":args.proxy_epochs,
                "fraction":args.fraction,"patience":args.proxy_epochs+1,"close_mosaic":3,
                "weight_decay":wd,"degrees":deg})
            if best < 0: raise RuntimeError("No se registró métrica de validación")
            return best
        finally:
            del model; gc.collect(); torch.cuda.empty_cache()
    finished = sum(t.state.is_finished() for t in study.trials)
    if finished < args.trials:
        study.optimize(objective, n_trials=args.trials-finished,
            callbacks=[lambda study, trial: export_trials(study)], gc_after_trial=True)
    export_trials(study); analysis(study)
    winner = study.best_trial
    dump(OUT / "seleccion.json", {"trial":winner.number,"proxy_value":winner.value,"params":winner.params,
        "selection":"Mayor mAP50-95 proxy; no se elige con robustez ni test"})
    weights = {}
    for name, params in [("referencia", {"weight_decay":.0005,"degrees":0.}), ("optimizado",winner.params)]:
        target = CACHE / "training" / ("final_"+name)
        record = OUT / f"final_{name}.json"
        if not record.exists():
            status("entrenamiento_final", model=name, parameters=params)
            # Un entrenamiento interrumpido se conserva; el reintento usa otra carpeta.
            run_name = "final_"+name if not target.exists() else "final_"+name+"_"+str(int(time.time()))
            model = YOLO(str(ROOT / "models/pretrained/yolov9t.pt"))
            def progress(trainer):
                status("entrenamiento_final", model=name, epoch=trainer.epoch+1,
                    epochs=args.final_epochs, validation=trainer.metrics)
            model.add_callback("on_fit_epoch_end", progress)
            model.train(**{**baseline, **params, "name":run_name,"epochs":args.final_epochs,
                "fraction":1.,"patience":args.final_epochs+1,"close_mosaic":10})
            target = Path(model.trainer.save_dir)
            checkpoint = target / "weights/best.pt"
            import shutil
            shutil.copy2(target / "results.csv", OUT / f"final_{name}_epochs.csv")
            shutil.copy2(target / "args.yaml", OUT / f"final_{name}_args.yaml")
            dump(record, {"checkpoint":str(checkpoint.relative_to(ROOT)),"sha256":sha(checkpoint),
                "params":params,"epochs":args.final_epochs,"validation":model.trainer.metrics})
            del model; gc.collect(); torch.cuda.empty_cache()
        weights[name] = ROOT / json.loads(record.read_text(encoding="utf-8"))["checkpoint"]
    robustness(weights)
    status("completado", best_trial=winner.number, test_used=False)
    # Renderizar las evidencias nuevas usando el entorno de notebooks disponible.
    # Un fallo de renderizado no borra ni invalida los experimentos guardados.
    import subprocess
    nbpython = ROOT / ".venv-tests/Scripts/python.exe"
    if nbpython.exists():
        try:
            subprocess.run([str(nbpython), str(ROOT / "tools/integrar_estudio_notebook.py")], cwd=ROOT, check=True)
            subprocess.run([str(nbpython), str(ROOT / "tools/ejecutar_notebooks.py")], cwd=ROOT, check=True)
        except Exception as exc:
            dump(OUT / "error_notebooks.json", {"error":str(exc)})


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    try: main()
    except Exception as exc:
        status("error", error=str(exc), traceback=traceback.format_exc())
        raise
