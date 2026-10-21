# Notebooks

Los cinco notebooks exigidos están preparados y ejecutados con salidas reales:

1. [Exploración](01_exploracion.ipynb): particiones, estadísticos y seis gráficos.
2. [Preprocesamiento](02_preprocesamiento.ipynb): etiquetas, RGB/BGR y normalización.
3. [Modelado](03_modelado.ipynb): configuraciones, arquitectura y checkpoint verificado.
4. [Optimización](04_optimizacion.ipynb): comparación histórica y límites frente a Semana 5.
5. [Evaluación](05_evaluacion.ipynb): detector, OCR, errores y pruebas funcionales.

Instalar el entorno principal y después `pip install -r requirements-notebooks.txt`.
Para ejecutar los cinco con el mismo intérprete: `python tools/ejecutar_notebooks.py`.
El informe está en `results/reports/ejecucion_notebooks.json`.

El modo normal no entrena ni descarga datos. Los análisis guardados permiten
revisar las evidencias desde un clon público. La validación completa de etiquetas
requiere el dataset local; si falta, se declara y se consulta la auditoría previa.
El entrenamiento es opcional, explícito y desactivado de forma predeterminada.

Crear y ejecutar el notebook de optimización no sustituye los experimentos
avanzados aún pendientes: véase [contraste de Semana 5](../docs/semana5_brechas.md).
