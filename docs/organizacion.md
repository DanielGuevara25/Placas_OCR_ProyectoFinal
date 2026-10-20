# Mapa de archivos y comandos

## Código y web

| Ubicación anterior | Ubicación actual |
|---|---|
| `config.py`, `providers.py`, `plate_detector.py`, `ocr_engine.py` | `src/` |
| Scripts de preparación, entrenamiento y evaluación | `src/`, mismos nombres |
| Implementación de `main.py` | `src/main.py`; lanzador compatible en la raíz |
| Implementación de `web_app.py` | `app/app.py`; lanzador compatible en la raíz |
| `web_service.py`, `web_ocr.py`, `web_validation.py` | `app/` |
| `templates/`, `static/` | `app/templates/`, `app/static/` |
| Documentación inicial README y LEEME_WEB | `docs/historico/` |
| `codigo_proyecto/`, `placas_web/` | `archive/` |

Para un script trasladado, usar `python -m src.nombre_sin_extension` desde la raíz,
por ejemplo `python -m src.revisar_duplicados`. No ejecutar directamente
`python src/nombre.py`, porque las importaciones usan el paquete `src`.

## Datos y resultados

| Ubicación anterior | Ubicación actual |
|---|---|
| `Data/`, `imagenes/` | `data/raw/Data/`, `data/raw/imagenes/` |
| `dataset_placas/` | `data/processed/dataset_placas/` |
| `anotaciones_propuestas/` | `data/annotations/anotaciones_propuestas/` |
| `revision_ocr_test/` | `data/review/revision_ocr_test/` |
| CSV de inventario y duplicados de la raíz | `data/manifests/` |
| `entrenamientos/` | `results/training/` |
| `evaluation/` | `results/evaluation/` |
| `analisis_overfitting/` | `results/overfitting/` |
| `evaluacion_final_ocr/` | `results/ocr/` |
| `resultados/`, `resultados_lote/` | `results/predictions/individual/`, `results/predictions/lote/` |
| `runs/` | `results/runs/` |
| `weights/` | `models/legacy/` |
| `yolov9t.pt` | `models/pretrained/yolov9t.pt` |

La web usa una copia verificada del mejor peso de regularización en `models/best.pt`.
Los checkpoints originales permanecen en `results/training/`.

Los registros experimentales históricos no se reescriben para simular corridas
en las nuevas rutas. Las fechas, métricas y configuraciones históricas se conservan.

Durante la migración se detectó una colisión entre los nombres `Data` y `data`
en Windows. Se resolvió mediante un nombre temporal y se comprobaron 13.621
archivos originales en `data/raw/Data/`.
