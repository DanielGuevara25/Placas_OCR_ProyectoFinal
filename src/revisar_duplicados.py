from src.paths import ROOT
import csv
import hashlib
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np


def main():
    base = ROOT
    carpeta = base / "data/processed/dataset_placas" / "images"
    if not carpeta.is_dir():
        raise FileNotFoundError(f"No existe: {carpeta}")

    grupos = defaultdict(list)
    errores = []
    extensiones = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    imagenes = sorted(
        p for p in carpeta.rglob("*")
        if p.is_file() and p.suffix.lower() in extensiones
    )

    for numero, ruta in enumerate(imagenes, 1):
        relativa = ruta.relative_to(carpeta)

        try:
            datos = np.fromfile(str(ruta), dtype=np.uint8)
            if datos.size == 0:
                raise ValueError("Archivo vacío")

            imagen = cv2.imdecode(datos, cv2.IMREAD_COLOR)
            if imagen is None:
                raise ValueError("Imagen ilegible")

            resumen = hashlib.sha256()
            resumen.update(str(imagen.shape).encode())
            resumen.update(imagen.tobytes())
            grupos[resumen.hexdigest()].append(relativa)

        except (OSError, ValueError, cv2.error) as error:
            errores.append([relativa.as_posix(), str(error)])

        if numero % 500 == 0:
            print(f"Revisadas: {numero}/{len(imagenes)}")

    duplicados = [rutas for rutas in grupos.values() if len(rutas) > 1]
    cruzados = 0
    reporte = base / "data/manifests/duplicados_dataset.csv"

    with reporte.open("w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(
            ["grupo", "imagen", "particion", "cruza_particiones"]
        )

        for grupo, rutas in enumerate(duplicados, 1):
            particiones = {ruta.parts[0] for ruta in rutas}
            cruza = len(particiones) > 1
            cruzados += int(cruza)

            for ruta in rutas:
                escritor.writerow([
                    grupo,
                    ruta.as_posix(),
                    ruta.parts[0],
                    "SI" if cruza else "NO",
                ])

    with (base / "data/manifests/errores_revision_duplicados.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["imagen", "error"])
        escritor.writerows(errores)

    print("\nRESULTADO")
    print(f"Imágenes examinadas: {len(imagenes)}")
    print(f"Grupos de imágenes duplicadas: {len(duplicados)}")
    print(f"Copias adicionales: {sum(len(g) - 1 for g in duplicados)}")
    print(f"Grupos presentes en distintas particiones: {cruzados}")
    print(f"Imágenes con errores: {len(errores)}")
    print(f"Reporte: {reporte}")
    print("No se ha borrado ni modificado ninguna imagen.")


if __name__ == "__main__":
    main()