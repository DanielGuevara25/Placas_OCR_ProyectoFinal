# Auditoría de los pendientes señalados

Esta revisión corrige la impresión de que preparar los seis documentos equivalía
a cerrar toda la directriz. Los siguientes estados corresponden a evidencias,
no a una garantía de calificación.

| Punto observado | Acción de esta revisión | Estado |
|---|---|---|
| Notebooks ausentes | Cinco `.ipynb` creados, ejecutados y validados; salidas conservadas | Publicados y presencia remota verificada |
| Modelos inaccesibles | Tres `.pt` finales, manifiesto SHA256 y recuperador probado | Descarga pública de los tres verificada con tamaño y SHA256 |
| README parcial | Apartados de problema, dataset, método, métricas, interfaz, notebooks, ética, autores, licencia, referencias y videos | Estructura completada; contenidos pendientes señalados |
| Licencia ausente | Textos de terceros revisados; equipo autorizó AGPL-3.0-only y se añadió LICENSE | Resuelto; datos y terceros mantienen sus condiciones |
| Optimización S5 incompleta | 60 ensayos procesados, 17 completos; dos ajustes de 100 épocas, nueve escenarios e importancia/PDP | Ejecutado localmente; ver `resultados_semana5.md` |

Persisten el despliegue público y los dos videos. La publicación se verificó
el 21/10/2026; evidencia en `results/reports/verificacion_github.json`.
El estudio terminó el 21/10/2026. La búsqueda eligió
la referencia y no demostró mejora. Su adaptación al ejemplo docente y sus
límites están documentados; esto no implica garantía de calificación.

La referencia docente usa Random Forest y datos tabulares. Su adaptación al
detector debe acordar variables, particiones, métrica y presupuesto de ejecución,
sin copiar resultados médicos ni reutilizar test para buscar mejoras.
