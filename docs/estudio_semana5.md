# Ejecución ampliada de Semana 5

El equipo autorizó utilizar la RTX 5070 Ti durante varias horas el 20 de octubre
de 2026. El programa reproducible es `tools/estudio_semana5.py`. Su estado real
se guarda en `results/semana5/estado.json`; preparar el programa no demuestra
que los experimentos estén terminados. Las evidencias anteriores se conservan.

## Diseño previo

- 60 ensayos TPE, semilla 42, con regularización `weight_decay` entre 0.0001 y
  0.003 (escala logarítmica) y rotación entre 0 y 10 grados. Los primeros cuatro
  puntos incluyen las tres configuraciones históricas y su combinación.
- Cada ensayo parte del mismo checkpoint preentrenado; utiliza una fracción fija
  de 35% de train, 12 épocas y val completa. Mediana de Optuna permite descartar
  ensayos después de cuatro épocas y diez ensayos iniciales. Se maximiza el mejor
  mAP50–95 de validación observado dentro de ese presupuesto.
- SGD, tasa inicial 0.01, momentum 0.937, batch 16 e imágenes de 640 píxeles
  permanecen fijos. Se fuerza SGD porque `optimizer=auto` puede elegir distinto
  optimizador según el número de iteraciones. No se atribuyen diferencias frente
  a las corridas históricas exclusivamente a los dos parámetros estudiados.
- Tras la búsqueda, la referencia y la configuración ganadora se entrenan desde
  el mismo preentrenamiento con train completo, 100 épocas y semilla 42. No se
  cambian los pesos utilizados actualmente por la aplicación.
- Test queda fuera del archivo de configuración del estudio. Val sirve para
  desarrollo y diagnóstico; no constituye una nueva evaluación independiente.

La búsqueda corta reduce el costo GPU, pero su clasificación de configuraciones
puede cambiar al entrenar 100 épocas. Una semilla no permite estimar la variación
entre entrenamientos. No se presentan los ensayos descartados como completos.

## Análisis y robustez

Los ensayos completos permiten generar historial, slice, importancia fANOVA,
y dependencia parcial de un sustituto Random Forest de 300 árboles. Se publica
R² y error absoluto de validación cruzada de cinco particiones del sustituto.
Si predice mal, sus gráficas no respaldan conclusiones fiables. El contorno
bidimensional es exploratorio y no demuestra una interacción causal.

Ambos ajustes finales se prueban sobre todas las imágenes de val en nueve
escenarios: limpio; ruido gaussiano con sigma 10 y 25; desenfoque de kernel 5 y 9;
brillo multiplicado por 0.5 y 1.5; resolución reducida a la mitad y restaurada;
y oclusión de una franja central del 10% del ancho de cada placa. Las semillas
del ruido dependen de la imagen y se repiten entre modelos. La oclusión es un
escenario artificial que utiliza las cajas anotadas, no una inferencia desplegada.

Se usan confianza 0.25, NMS IoU 0.7 y acierto IoU 0.5, emparejando predicciones
por confianza con una sola caja real. Se reportan precisión, recall y F1,
recall en cajas de menos de 1% del área de imagen y 2,000 remuestreos por imagen
para IC del recall y de su caída frente a limpio (bootstrap pareado). Estos IC
no representan incertidumbre de reentrenamiento ni independencia por vehículo.
No se usa una caída de cinco puntos como aceptación automática: el costo de
errores y el uso previsto deben justificar cualquier umbral operativo.

No hay negativos en el dataset; no se puede simular honestamente prevalencia
de imágenes sin placa ni estimar su tasa poblacional de falsos positivos.
La caída de una variable médica se adapta a oclusión visual, y el cambio de
escala/iluminación a cambios de adquisición. El análisis no optimiza el OCR.

## Reanudación y evidencia

La base Optuna y los checkpoints intermedios quedan en `.model-cache/semana5/`
(fuera de Git). Los parámetros, hashes, tablas, figuras y estados se guardan
en `results/semana5/`. Un ensayo interrumpido se marca fallido al reanudar;
los ensayos completados se conservan. El generador TPE se vuelve a inicializar
al reanudar, por lo que la continuación puede diferir de una corrida continua.
No se deben iniciar dos instancias contra la misma base de estudio.

En Linux con el entorno CUDA y dependencias instalados, desde la raíz:

```bash
python tools/estudio_semana5.py
```

Los tiempos finales dependen del equipo. El programa puede ocupar varias horas;
el cierre de sesión, suspensión o apagado interrumpe la ejecución.
