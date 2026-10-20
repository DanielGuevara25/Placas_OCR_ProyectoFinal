from src.paths import ROOT
import csv
from pathlib import Path

import cv2
import numpy as np

from src.config import LicensePlateConfig
from src.plate_detector import PlateDetector


COLUMNAS = ["imagen", "cantidad_cajas", "estado", "revisado"]


def main():
    entrada = ROOT / 'data/raw/Data'
    salida = ROOT / 'data/annotations/anotaciones_propuestas'
    reporte = salida / "revision.csv"

    if not entrada.is_dir():
        raise FileNotFoundError(f"No existe: {entrada.resolve()}")

    extensiones = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    fotos = sorted(
        p for p in entrada.rglob("*")
        if p.is_file() and p.suffix.lower() in extensiones
    )

    if not fotos:
        raise ValueError("No se encontraron imágenes dentro de Data.")

    claves = [
        str(p.relative_to(entrada).with_suffix("")).casefold()
        for p in fotos
    ]
    if len(claves) != len(set(claves)):
        raise ValueError(
            "Hay imágenes con el mismo nombre y distinta extensión "
            "en una misma carpeta. Revisa esos nombres."
        )

    salida.mkdir(parents=True, exist_ok=True)

    # Recupera el progreso sin depender del orden de las imágenes.
    procesadas = set()
    tiene_reporte = reporte.exists() and reporte.stat().st_size > 0

    if tiene_reporte:
        with reporte.open(
            "r", newline="", encoding="utf-8-sig"
        ) as archivo:
            lector = csv.DictReader(archivo)

            if lector.fieldnames != COLUMNAS:
                raise ValueError(
                    "El encabezado de revision.csv no es el esperado."
                )

            for fila in lector:
                nombre = fila.get("imagen")
                estado = fila.get("estado")
                if nombre and estado:
                    procesadas.add(nombre)

    pendientes = [
        p for p in fotos
        if p.relative_to(entrada).as_posix() not in procesadas
    ]

    print(f"Imágenes encontradas: {len(fotos)}")
    print(f"Ya registradas: {len(fotos) - len(pendientes)}")
    print(f"Pendientes: {len(pendientes)}")

    if not pendientes:
        print("No hay imágenes pendientes.")
        return

    cfg = LicensePlateConfig()
    cfg.detector_backend = "fast"
    cfg.det_conf = 0.25
    detector = PlateDetector(cfg)

    # UTF-8 sin BOM al añadir; con BOM al crear el archivo.
    codificacion = "utf-8" if tiene_reporte else "utf-8-sig"

    with reporte.open(
        "a", newline="", encoding=codificacion
    ) as archivo:
        escritor = csv.writer(archivo)

        if not tiene_reporte:
            escritor.writerow(COLUMNAS)
            archivo.flush()

        for numero, ruta in enumerate(pendientes, start=1):
            relativa = ruta.relative_to(entrada)
            nombre = relativa.as_posix()

            # Controla archivos vacíos, dañados o inaccesibles.
            try:
                contenido = np.fromfile(str(ruta), dtype=np.uint8)

                if contenido.size == 0:
                    raise ValueError("Archivo vacío")

                imagen = cv2.imdecode(
                    contenido, cv2.IMREAD_COLOR
                )

                if imagen is None:
                    raise ValueError("Imagen dañada o formato no legible")

            except (OSError, ValueError, cv2.error) as error:
                escritor.writerow([nombre, 0, "ERROR_IMAGEN", ""])
                archivo.flush()
                print(
                    f"[{numero}/{len(pendientes)}] "
                    f"ERROR_IMAGEN: {nombre}: {error}"
                )
                continue

            alto, ancho = imagen.shape[:2]

            # Si falla el modelo, se detiene sin registrar esta imagen.
            # Al ejecutar otra vez, volverá a intentar procesarla.
            detecciones = detector.detect(imagen)

            vista = imagen.copy()
            lineas = []

            for x1, y1, x2, y2, confianza, _ in detecciones:
                valores = np.array(
                    [x1, y1, x2, y2, confianza], dtype=float
                )
                if not np.isfinite(valores).all():
                    continue

                x1 = float(np.clip(x1, 0, ancho))
                x2 = float(np.clip(x2, 0, ancho))
                y1 = float(np.clip(y1, 0, alto))
                y2 = float(np.clip(y2, 0, alto))

                if x2 <= x1 or y2 <= y1:
                    continue

                centro_x = (x1 + x2) / (2 * ancho)
                centro_y = (y1 + y2) / (2 * alto)
                ancho_caja = (x2 - x1) / ancho
                alto_caja = (y2 - y1) / alto

                lineas.append(
                    f"0 {centro_x:.6f} {centro_y:.6f} "
                    f"{ancho_caja:.6f} {alto_caja:.6f}"
                )

                cv2.rectangle(
                    vista,
                    (int(x1), int(y1)),
                    (int(x2), int(y2)),
                    (0, 255, 0),
                    2,
                )
                cv2.putText(
                    vista,
                    f"placa {confianza:.2f}",
                    (int(x1), max(15, int(y1) - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                )

            etiqueta = (
                salida / "labels" / relativa.with_suffix(".txt")
            )

            # Conserva cualquier etiqueta que ya exista.
            if lineas and not etiqueta.exists():
                etiqueta.parent.mkdir(parents=True, exist_ok=True)
                etiqueta.write_text(
                    "\n".join(lineas) + "\n",
                    encoding="utf-8",
                )

            preview = (
                salida / "revision"
                / relativa.with_name(relativa.name + ".jpg")
            )

            if not preview.exists():
                preview.parent.mkdir(parents=True, exist_ok=True)
                correcto, contenido_jpg = cv2.imencode(".jpg", vista)

                if not correcto:
                    raise RuntimeError(
                        f"No se pudo generar la vista: {preview}"
                    )

                contenido_jpg.tofile(str(preview))

            if etiqueta.exists():
                estado = "CAJAS_POR_REVISAR"
            else:
                estado = "SIN_DETECCION_REVISAR"

            escritor.writerow([nombre, len(lineas), estado, ""])
            archivo.flush()

            print(
                f"[{numero}/{len(pendientes)}] "
                f"{nombre}: {len(lineas)} cajas — {estado}"
            )

    print(f"\nFinalizado. Resultados: {salida.resolve()}")
    print("Revisa las cajas antes de usarlas para entrenar.")


if __name__ == "__main__":
    main()
