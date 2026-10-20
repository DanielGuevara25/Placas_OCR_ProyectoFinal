from src.paths import ROOT
from pathlib import Path
import multiprocessing

import torch
import yaml
from ultralytics import YOLO


def main():
    base = ROOT
    dataset = base / "data/processed/dataset_placas"

    if not torch.cuda.is_available():
        raise RuntimeError("PyTorch no reconoce la GPU.")

    for particion in ("train", "val"):
        if not (dataset / "images" / particion).is_dir():
            raise FileNotFoundError(f"Falta images/{particion}")

    # Usa una ruta absoluta para localizar correctamente el dataset.
    configuracion = {
        "path": dataset.as_posix(),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "names": {0: "placa"},
    }

    data_yaml = dataset / "data_entrenamiento.yaml"
    data_yaml.write_text(
        yaml.safe_dump(configuracion, sort_keys=False),
        encoding="utf-8",
    )

    print("GPU:", torch.cuda.get_device_name(0))
    print("Dataset:", dataset)

    modelo = YOLO("models/pretrained/yolov9t.pt")

    modelo.train(
        data=str(data_yaml),
        epochs=100,
        imgsz=640,
        batch=16,
        device=0,
        workers=4,
        seed=42,
        patience=50,
        project=str(base / "results/training"),
        name="yolov9t_baseline",
        exist_ok=False,
        save=True,
        plots=True,
        cache=False,
        fliplr=0.0,
        flipud=0.0,
    )


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()