from src.paths import ROOT
import argparse
import multiprocessing
from pathlib import Path

import torch
import ultralytics
import yaml
from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--experimento",
        choices=["regularizacion", "rotacion"],
        required=True,
    )
    opcion = parser.parse_args().experimento

    base = ROOT
    ruta_args = base / "results/training" / "yolov9t_baseline" / "args.yaml"

    if ultralytics.__version__ != "8.4.171":
        raise RuntimeError(
            "El baseline usó Ultralytics 8.4.171. "
            f"Versión actual: {ultralytics.__version__}"
        )

    if not torch.cuda.is_available():
        raise RuntimeError("GPU no disponible.")

    with ruta_args.open(encoding="utf-8") as archivo:
        configuracion = yaml.safe_load(archivo)

    # Reutiliza la configuración del experimento base.
    for clave in ("save_dir", "model", "task", "mode"):
        configuracion.pop(clave, None)

    configuracion.update(
        data=str(base / "data/processed/dataset_placas" / "data_entrenamiento.yaml"),
        project=str(base / "results/training"),
        name=f"yolov9t_{opcion}",
        resume=False,
        exist_ok=False,
        save=True,
        save_period=1,
    )

    if opcion == "regularizacion":
        configuracion["weight_decay"] = 0.001
    else:
        configuracion["degrees"] = 5.0

    print("Experimento:", opcion)
    print("GPU:", torch.cuda.get_device_name(0))

    # Cada experimento comienza con los mismos pesos preentrenados.
    modelo = YOLO(str(base / "models/pretrained/yolov9t.pt"))
    modelo.train(**configuracion)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()