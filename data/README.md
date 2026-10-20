# Datos locales

- `raw/Data/`: fotografías originales trasladadas desde `Data/`.
- `raw/imagenes/`: carpeta de imágenes adicional conservada.
- `processed/dataset_placas/`: particiones y anotaciones del detector.
- `annotations/anotaciones_propuestas/`: propuestas de cajas y revisión.
- `review/revision_ocr_test/`: recortes y transcripciones para evaluación OCR.
- `manifests/`: inventarios y revisión de duplicados.

Estos contenidos están excluidos de Git por su volumen. El autor confirmó
autorización para uso académico y publicación de imágenes extraídas del sistema
de reconocimiento de placas de su lugar de trabajo. No se ha especificado una
licencia pública: consultar [procedencia y condiciones de uso](procedencia.md).
La información experimental publicada debe distinguir detector, OCR y pipeline completo.

Dataset procesado auditado: 7.332 imágenes y 8.208 cajas de clase placa.
El [análisis exploratorio](../docs/analisis_datos.md) incluye seis gráficos,
validación de etiquetas y comprobación de duplicados exactos.
