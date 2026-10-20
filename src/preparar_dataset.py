from src.paths import ROOT
import csv
import hashlib
import math
import random
import shutil
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

BASE = ROOT
IMAGENES = BASE / "data/raw/Data"
ANOTACIONES = BASE / "data/annotations/anotaciones_propuestas"
SALIDA = BASE / "data/processed/dataset_placas"


def validar_etiqueta(ruta):
    if not ruta.exists():
        raise ValueError("Falta el TXT; no se asume que sea una imagen sin placas")

    texto = ruta.read_text(encoding="utf-8-sig")
    for numero, linea in enumerate(texto.splitlines(), 1):
        if not linea.strip():
            continue

        campos = linea.split()
        if len(campos) != 5 or campos[0] != "0":
            raise ValueError(f"Línea {numero}: se espera clase 0 y cuatro coordenadas")

        x, y, w, h = map(float, campos[1:])
        if not all(math.isfinite(v) for v in (x, y, w, h)):
            raise ValueError(f"Línea {numero}: coordenadas no válidas")

        if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < w <= 1 and 0 < h <= 1):
            raise ValueError(f"Línea {numero}: coordenadas fuera de rango")

        tolerancia = 1e-5
        if (
            x - w / 2 < -tolerancia
            or y - h / 2 < -tolerancia
            or x + w / 2 > 1 + tolerancia
            or y + h / 2 > 1 + tolerancia
        ):
            raise ValueError(f"Línea {numero}: caja fuera de la imagen")


def main():
    if SALIDA.exists():
        raise FileExistsError(
            f"Ya existe {SALIDA}. Usa otro nombre de salida para no sobrescribirla."
        )

    grupos = defaultdict(list)
    rechazadas = []
    vistas = set()

    with (ANOTACIONES / "revision.csv").open(
        encoding="utf-8-sig", newline=""
    ) as archivo:
        for fila in csv.DictReader(archivo):
            if fila["estado"] == "ERROR_IMAGEN":
                continue
            if fila["revisado"].strip().upper() != "SI":
                continue

            relativa = Path(fila["imagen"])
            if relativa.is_absolute() or ".." in relativa.parts:
                raise ValueError(f"Ruta no válida: {relativa}")

            if relativa.as_posix() in vistas:
                continue
            vistas.add(relativa.as_posix())

            imagen = IMAGENES / relativa
            etiqueta = ANOTACIONES / "labels" / relativa.with_suffix(".txt")

            try:
                contenido = imagen.read_bytes()
                matriz = cv2.imdecode(
                    np.frombuffer(contenido, dtype=np.uint8),
                    cv2.IMREAD_COLOR,
                )
                if matriz is None:
                    raise ValueError("Imagen ilegible")

                validar_etiqueta(etiqueta)

                # Agrupa imágenes visualmente idénticas aunque cambie el archivo.
                resumen = hashlib.sha256()
                resumen.update(str(matriz.shape).encode())
                resumen.update(matriz.tobytes())
                grupos[resumen.hexdigest()].append((relativa, imagen, etiqueta))

            except (OSError, ValueError, cv2.error) as error:
                rechazadas.append((relativa.as_posix(), str(error)))

    claves = sorted(grupos)
    if len(claves) < 10:
        raise ValueError("Hay menos de 10 grupos válidos; revisa las rutas y etiquetas.")

    random.Random(42).shuffle(claves)
    fin_train = int(len(claves) * 0.8)
    fin_val = int(len(claves) * 0.9)

    particiones = {
        "train": claves[:fin_train],
        "val": claves[fin_train:fin_val],
        "test": claves[fin_val:],
    }

    SALIDA.mkdir()
    manifiesto = []

    for particion, hashes in particiones.items():
        cantidad = 0

        for clave in hashes:
            for relativa, imagen, etiqueta in grupos[clave]:
                # Mantiene subcarpetas y evita colisiones entre extensiones.
                nombre = relativa.name.replace(".", "_") + imagen.suffix.lower()
                destino_relativo = relativa.parent / nombre

                destino_imagen = SALIDA / "images" / particion / destino_relativo
                destino_etiqueta = (
                    SALIDA / "labels" / particion
                    / destino_relativo.with_suffix(".txt")
                )

                destino_imagen.parent.mkdir(parents=True, exist_ok=True)
                destino_etiqueta.parent.mkdir(parents=True, exist_ok=True)

                shutil.copy2(imagen, destino_imagen)
                shutil.copy2(etiqueta, destino_etiqueta)

                manifiesto.append(
                    [relativa.as_posix(), particion, clave]
                )
                cantidad += 1

        print(f"{particion}: {cantidad} imágenes")

    # La ruta relativa se interpreta respecto al propio data.yaml.
    (SALIDA / "data.yaml").write_text(
        "path: .\n"
        "train: images/train\n"
        "val: images/val\n"
        "test: images/test\n"
        "names:\n"
        "  0: placa\n",
        encoding="utf-8",
    )

    for nombre, columnas, filas in [
        ("particiones.csv", ["imagen_original", "particion", "grupo"], manifiesto),
        ("excluidas.csv", ["imagen", "motivo"], rechazadas),
    ]:
        with (SALIDA / nombre).open(
            "w", encoding="utf-8-sig", newline=""
        ) as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(columnas)
            escritor.writerows(filas)

    print(f"\nExcluidas por problemas: {len(rechazadas)}")
    print(f"Dataset creado en: {SALIDA}")
    print("Los originales y las anotaciones originales se conservaron.")


if __name__ == "__main__":
    main()
