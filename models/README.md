# Modelos

- `best.pt`: copia del detector usado por la web, del experimento
  `results/training/yolov9t_regularizacion/weights/best.pt`.
- `manifest.json`: origen, tamaño y SHA256 de esa copia, verificados al organizar.
- `pretrained/yolov9t.pt`: peso base empleado por los scripts de entrenamiento.
- `legacy/`: pesos anteriores conservados; no son el modelo predeterminado de la web.

El OCR web carga `cct-s-v2-global-model` mediante fast-plate-ocr.
La consola utiliza por defecto otro detector, de open-image-models.

Los pesos binarios están excluidos de Git. Falta definir su distribución pública,
licencias y descarga reproducible antes de publicar el repositorio final.
