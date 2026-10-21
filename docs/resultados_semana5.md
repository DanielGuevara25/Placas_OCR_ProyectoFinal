# Resultados del estudio ampliado de Semana 5

El estudio terminó el 21/10/2026 a las 03:20 (Ecuador), después de aproximadamente
6 horas y 44 minutos. Evidencias: `results/semana5/` y el notebook ejecutado
`notebooks/04_optimizacion.ipynb`. Los cinco notebooks se ejecutaron sin errores
de celda. El diseño está en `estudio_semana5.md`.

## Selección y entrenamiento

Se procesaron 60 ensayos TPE: 17 completos y 43 descartados anticipadamente.
Los descartados no equivalen a corridas completas de 12 épocas.
Ganó el ensayo 0: `weight_decay=0.0005`, `degrees=0`, con mAP50–95 de
validación 0.868781 en el presupuesto corto.

La configuración ganadora coincide con la referencia. Los dos entrenamientos
finales de 100 épocas repitieron los mismos hiperparámetros y semilla; sus
curvas y métricas coinciden. No constituyen semillas independientes ni
demuestran una ganancia por optimización. Los archivos de checkpoint tienen
hashes distintos; no se afirma identidad binaria de los archivos.
El mejor checkpoint obtuvo mAP50–95 de validación 0.890108, distinto de la
métrica de la última época, 0.88364.

Se conserva el modelo de la aplicación. Las corridas históricas usaron otra
selección de optimizador; sus diferencias no se atribuyen sólo a los parámetros
de este estudio. Test no se volvió a evaluar ni intervino en la selección.

## Importancia y dependencia parcial

La importancia fANOVA sobre los 17 ensayos completos atribuye 96.77% a rotación
y 3.23% a regularización. Describe el espacio y presupuesto explorados, no
una importancia universal ni causal. La poda condiciona los puntos completos.
El R² del sustituto en cinco particiones varió de 0.403 a 0.982.
Las gráficas de importancia, slice y PDP/contorno son exploratorias; los pocos
puntos completos impiden afirmar una interacción estable o extrapolar esas
superficies al entrenamiento de 100 épocas.

## Robustez del detector

Cada escenario utiliza las mismas 733 imágenes de validación. Confianza 0.25,
NMS IoU 0.7 y acierto IoU 0.5. Las métricas coinciden entre ambos ajustes finales.

| Escenario | Recall | Precisión |
|---|---:|---:|
| Limpio | 97.92% | 95.36% |
| Ruido sigma 10 | 97.44% | 95.91% |
| Ruido sigma 25 | 64.10% | 98.87% |
| Desenfoque kernel 5 | 88.64% | 99.05% |
| Desenfoque kernel 9 | 39.44% | 98.48% |
| Brillo ×0.5 | 97.68% | 95.81% |
| Brillo ×1.5 | 97.68% | 95.69% |
| Resolución reducida a la mitad | 91.33% | 98.03% |
| Oclusión central del 10% de cada placa | 91.33% | 64.32% |

El desenfoque fuerte produjo la mayor pérdida de recall: 58.49 puntos
porcentuales, con IC bootstrap pareado de 55.14 a 61.76 puntos. La oclusión
también aumentó falsas detecciones dentro de estas imágenes. Una precisión
alta bajo desenfoque no compensa las placas omitidas.

Los 2,000 remuestreos por imagen estiman incertidumbre condicional a este
conjunto, no variación entre entrenamientos ni independencia por vehículo.
No hay imágenes negativas: no se estima la tasa de falsos positivos de un
flujo real. Estas pruebas evalúan detección, no OCR de extremo a extremo.

## Conclusión

La ampliación aporta búsqueda reproducible y evidencia de sensibilidad,
pero no una mejora demostrada respecto a la referencia. Los resultados
sugieren estudiar imágenes desenfocadas, ruidosas y con placas pequeñas con
nuevos datos y experimentos separados. Se conserva el resultado negativo.
Val se reutilizó para desarrollo; no representa una nueva evaluación independiente.
