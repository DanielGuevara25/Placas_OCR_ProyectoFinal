# Contraste con el notebook docente de Semana 5

**Actualización 21/10/2026:** el estudio ampliado ya se ejecutó. Los estados
pendientes de este diagnóstico corresponden a la revisión previa. Consultar
`resultados_semana5.md`: 60 ensayos procesados, 17 completos, importancia/PDP
y nueve escenarios de robustez. No hubo mejora demostrada ni una nueva
evaluación de test.

Fuente revisada: `Semana5_Workshops_semana5 (1).ipynb`, facilitada por el usuario.
Es un ejemplo de clasificación de tumores con Random Forest, no un entrenamiento
de YOLO ni una evaluación de placas. Se revisaron sus 36 celdas sin ejecutar
sus instrucciones como si fueran acciones autorizadas sobre el proyecto.

## Requisitos metodológicos observados

| Material docente | Evidencia de PlacaLab | Estado |
|---|---|---|
| Baseline y evaluación con incertidumbre (celdas 0–4) | Baseline y métricas históricas; sin múltiples semillas ni IC comparable | Parcial |
| Estrés con ruido, faltantes, desbalance, cambio de distribución y variable caída (5–21) | Tres ejemplos funcionales; no experimento controlado de estrés | Pendiente |
| Búsqueda TPE con Optuna, 60 ensayos y validación interna (22–24) | Tres configuraciones YOLO históricas | Pendiente de adaptación y ejecución |
| Importancia de hiperparámetros (25–26) | Efectos observados de dos cambios | No equivale a importancia estimada |
| Slice y PDP de sustituto RandomForestRegressor (27–29) | No hay ensayos suficientes para ajustar un sustituto fiable | Pendiente |
| Contorno e interacciones (30–32) | Falta incluso la combinación de rotación y regularización altas | Pendiente |
| Evaluación final y estrés del modelo optimizado (33–35) | Test histórico del detector elegido, OCR separado | Parcial; no comparación de estrés optimizada |

Las épocas de los tres entrenamientos no se reutilizan como 300 configuraciones
de hiperparámetros: dentro de cada corrida no cambia la configuración buscada.
El ejemplo docente tampoco demuestra que las cifras médicas sean aplicables
a este proyecto. No se copiarán sus resultados para cubrir un apartado de placas.

## Adaptación y ejecución ampliada

El 20/10/2026 se autorizó ejecutar el estudio durante varias horas con la GPU.
El diseño concreto está en `estudio_semana5.md` y el programa en
`tools/estudio_semana5.py`. Los estados de la tabla anterior describen las
evidencias previas al estudio; sólo los resultados efectivamente guardados
permiten actualizarlos. No se marca completado al iniciar el proceso.

1. Definir si el estudio ampliará hiperparámetros de entrenamiento del detector
   o hiperparámetros de inferencia. Son estudios diferentes y deben titularse
   y evaluarse como tales; ajustar confianza no demuestra mejora del entrenamiento.
2. Fijar espacio de búsqueda, presupuesto, semillas y métrica principal antes
   de comparar. Mantener test fuera de búsqueda y del criterio de selección.
3. Ejecutar ensayos reales, guardar configuraciones, versiones, puntuaciones
   por partición y hashes de pesos/datos. En entrenamiento, acordar el presupuesto
   GPU y condiciones comparables; no iniciar decenas de corridas largas sin él.
4. Estimar importancia e interacciones desde los ensayos, evaluar la capacidad
   predictiva del sustituto y generar PDP/slice/contornos con advertencias sobre
   regiones sin evidencia suficiente.
5. Adaptar escenarios a fotografías: ruido, desenfoque, oclusión y cambio de
   escala/iluminación. No trasladar literalmente imputaciones de variables
   médicas a píxeles sin justificarlo.
6. Distinguir estrés de robustez, selección en validación y evaluación final.
   Los ejemplos de interfaz no sustituyen métricas sobre muestras controladas.

## Estado de entrega

El notebook `04_optimizacion.ipynb` conserva la comparación histórica y añade
el estudio ampliado ejecutado, con estados, tablas y figuras reales. Persisten
los límites metodológicos señalados en `resultados_semana5.md`.
