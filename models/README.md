# Modelos

- `best.pt`: copia del detector usado por la web, del experimento
  `results/training/yolov9t_regularizacion/weights/best.pt`.
- `baseline.pt`: mejor checkpoint del entrenamiento baseline.
- `rotacion.pt`: mejor checkpoint del entrenamiento con rotación.
- `manifest.json`: origen, tamaño, URL y SHA256 de los tres checkpoints.
- `pretrained/yolov9t.pt`: peso base empleado por los scripts de entrenamiento.
- `legacy/`: pesos anteriores conservados; no son el modelo predeterminado de la web.

El OCR web carga `cct-s-v2-global-model` mediante fast-plate-ocr.
La consola utiliza por defecto otro detector, de open-image-models.

Estos tres checkpoints finales pequeños están incluidos en Git; los pesos por
época, preentrenados auxiliares y datos completos siguen excluidos. Un clon
normal debe contener `models/best.pt` para la web, sin reconstruir entrenamientos.

Descargas directas una vez publicada esta revisión:

- [Regularización: best.pt](https://raw.githubusercontent.com/DanielGuevara25/Placas_OCR_ProyectoFinal/main/models/best.pt).
- [Baseline](https://raw.githubusercontent.com/DanielGuevara25/Placas_OCR_ProyectoFinal/main/models/baseline.pt).
- [Rotación](https://raw.githubusercontent.com/DanielGuevara25/Placas_OCR_ProyectoFinal/main/models/rotacion.pt).

Para recuperar o verificar uno: `python -m src.descargar_modelos --model best`.
También acepta `baseline` o `rotacion`. La descarga verifica tamaño y SHA256 antes
de reemplazar el destino; no sustituye archivos por una descarga incompleta.

Los `.pt` deben cargarse sólo si proceden de una fuente confiable; este manifiesto
permite comprobar los archivos publicados por el equipo. Las condiciones de
componentes y pesos de origen se distinguen en [licencias](../docs/licencias.md).
La publicación del modelo no publica el dataset ni le asigna una licencia abierta.
