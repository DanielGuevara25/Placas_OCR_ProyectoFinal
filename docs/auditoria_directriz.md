# Auditoría de los pendientes señalados

Esta revisión corrige la impresión de que preparar los seis documentos equivalía
a cerrar toda la directriz. Los siguientes estados corresponden a evidencias,
no a una garantía de calificación.

| Punto observado | Acción de esta revisión | Estado |
|---|---|---|
| Notebooks ausentes | Cinco `.ipynb` creados, ejecutados y validados; salidas conservadas | Resuelto en archivos locales; publicar esta revisión |
| Modelos inaccesibles | Tres `.pt` finales, manifiesto SHA256 y recuperador probado | Preparados; verificar acceso remoto después de subir |
| README parcial | Apartados de problema, dataset, método, métricas, interfaz, notebooks, ética, autores, licencia, referencias y videos | Estructura completada; contenidos pendientes señalados |
| Licencia ausente | Textos de terceros revisados; equipo autorizó AGPL-3.0-only y se añadió LICENSE | Resuelto; datos y terceros mantienen sus condiciones |
| Optimización S5 incompleta | Notebook docente contrastado con el proyecto; brechas exactas documentadas | Sigue pendiente el estudio experimental ampliado |

Persisten además el despliegue público y los dos videos. Un notebook de
optimización con resultados históricos no sustituye 60 ensayos Optuna, robustez,
importancias y dependencia parcial/interacciones. No se marca ese requisito como
cumplido por tener un archivo con el nombre solicitado.

La referencia docente usa Random Forest y datos tabulares. Su adaptación al
detector debe acordar variables, particiones, métrica y presupuesto de ejecución,
sin copiar resultados médicos ni reutilizar test para buscar mejoras.
