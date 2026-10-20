# Evaluación OCR y análisis de errores

Ejecución local aportada por el usuario, 18/10/2026. Modelo cct-s-v2-global-model, fast-plate-ocr 1.1.0, CPU, interpolación cubic.

Se seleccionaron 50 imágenes de test con semilla 42 y se extrajeron sus 54 cajas clase placa anotadas. Transcripción manual con identificadores neutros, sin usar el nombre de archivo como etiqueta verdadera. El revisor marcó 22 legibles y 32 ilegibles: cobertura de transcripción 40,74 %. Se aceptan las transcripciones suministradas, sin auditoría visual independiente aquí.

Exactitud de placa completa: 17/22 = 77,27 %. CER agregado: 7/149 = 4,70 %. Cero errores de ejecución y cero lecturas vacías en los legibles. Se quitaron espacios y guiones y se pasó a mayúsculas; no se completaron ceros ni se sustituyeron O/0 o I/1.

| ID | Referencia manual | OCR | Distancia de edición | Confianza media | Mínima por carácter |
|---|---|---|---:|---:|---:|
| placa_001 | GST2652 | CST2692 | 2 | 92.72 % | 66.77 % |
| placa_025 | GBO9235 | GBQ9235 | 1 | 97.77 % | 84.62 % |
| placa_040 | GPN428 | GPN438 | 1 | 93.08 % | 58.91 % |
| placa_046 | GPM212 | GPW212 | 1 | 99.29 % | 96.16 % |
| placa_047 | GSO6774 | 6SQ6774 | 2 | 90.24 % | 52.24 % |

Tres de las cinco lecturas incorrectas superan simultáneamente las reglas iniciales de confianza media >=85 % y mínima por carácter >=60 % (placa_001, placa_025 y placa_046). Esto demuestra que esas reglas no garantizan la corrección de la lectura. Si se declarase el texto erróneo reconocido, la comparación podría registrar una coincidencia incorrecta. No se han cambiado umbrales usando este test.

La referencia GPN428 se conserva como transcrita: la nota del revisor sobre un cero inicial no se aplica automáticamente. Una segunda revisión de las referencias debe hacerse sobre las imágenes, sin corregirlas para favorecer la predicción.

## Límites de interpretación
- Métricas condicionales a legibilidad humana, sobre cajas anotadas; no miden detección+OCR ni validación completa de solicitud.
- Los 32 ilegibles no se cuentan como aciertos ni errores de texto, porque no tienen referencia verificable. Sí se incluyen en el conteo de cobertura.
- La muestra es pequeña y podría incluir vistas relacionadas; no se confirma independencia estadística ni ausencia de duplicados en este análisis.
- CER es distancia de edición agregada, no probabilidad de error por carácter ni promedio de confianza.
- La comparación sirve de apoyo: debe revisarse caja, lectura y contexto. No demuestra identidad del vehículo, autenticidad documental ni fraude.

Los archivos metricas_ocr.json y detalle_ocr.json contienen valores exactos y hashes de entradas/recortes. El CSV de detalle conserva las salidas para auditoría. No se ejecutó el OCR en este entorno; se verificaron los cálculos de la evidencia aportada.

## Recomendaciones de captura
La calidad de imagen puede limitar el OCR. Se recomienda que la placa tenga suficiente tamaño en la foto, enfoque, iluminación uniforme, poca inclinación y ausencia de reflejos o movimiento; usar archivos originales sin compresión excesiva. Si la evidencia no permite distinguir todos los caracteres, solicitar una nueva fotografía o revisión manual sin completar datos por suposición. La mejora con fotografías de mayor calidad es una hipótesis pendiente de medir, no un resultado demostrado. Se conservan las métricas actuales y las exclusiones explícitas.
