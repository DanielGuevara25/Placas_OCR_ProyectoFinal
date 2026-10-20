# Pruebas del sistema

## Entorno de comprobación

Se creó `.venv-tests/` con Python 3.12 para conservar el entorno original `.venv/`,
cuyo intérprete Python 3.11 ya no está disponible. Las dependencias se instalan con:

```powershell
.\.venv-tests\Scripts\python.exe -m pip install -r requirements.txt
```

## Pruebas unitarias

```powershell
.\.venv-tests\Scripts\python.exe -m unittest discover -s tests -v
```

Las 10 pruebas existentes aprobaron en la comprobación inicial con Flask 3.1.3
y los modelos simulados. Verifican:

- Rechazo de imágenes inválidas y umbrales incorrectos.
- Normalización y validación de la matrícula declarada.
- Recortes limitados al tamaño de la imagen.
- Selección manual cuando existen varias placas.
- Coincidencias, discrepancias y lecturas inciertas.
- Respuesta cuando no se detectan placas o falta el modelo.
- Manejo de errores OCR por recorte.
- Exportaciones JSON/ZIP y reutilización de modelos.
- Disponibilidad de HTML, JavaScript y CSS.

Los errores OCR impresos por algunos tests son intencionales: comprueban
el comportamiento cuando falla una lectura.

## Integración con modelos reales

```powershell
.\.venv-tests\Scripts\python.exe -m tests.smoke_real
```

Esta prueba usa Flask y los modelos reales en CPU. Envía las imágenes incluidas
en `app/static/examples/` al endpoint `/api/detect`, registra las predicciones
y compara el estado observado con el esperado para cada ejemplo.

El informe se guarda en `results/reports/prueba_integracion_real.json` e incluye
versiones, hashes de pesos e imágenes, tiempos, detecciones y validaciones.
Se conserva el resultado observado aunque difiera del esperado.

Tres ejemplos funcionales no estiman la precisión general del modelo ni
sustituyen la evaluación sobre un conjunto de prueba independiente.

## Resultado de la ejecución real

Entorno: Windows, Python 3.12.14, PyTorch 2.14.1 CPU, Ultralytics 8.4.171,
fast-plate-ocr 1.1.0 y ONNX Runtime 1.31.0. Las versiones completas están
en `requirements-tested.txt`. `pip check` no encontró dependencias rotas.
Las 10 pruebas unitarias también aprobaron dentro del entorno nuevo.

| Caso | Lectura real | Resultado | HTTP |
|---|---|---|---|
| Declarada GCA4771 | GCA4771 | Coincide | 200 |
| Declarada GTW9312 | GTW9311 | Inconsistencia, revisión manual | 200 |
| Imagen sin placa | Sin detecciones | Solicitar otra fotografía | 200 |

Los tres estados observados coincidieron con los esperados. El primer análisis
tardó 1.987 ms en cargar los modelos y 1.949 ms en procesar; los siguientes
procesamientos tardaron aproximadamente 52 y 38 ms. Son tiempos de esta ejecución,
no una garantía de latencia ni un benchmark general.

Para abrir la web con el entorno probado:

```powershell
.\.venv-tests\Scripts\python.exe web_app.py --device cpu --port 8080
```

Visitar `http://127.0.0.1:8080`. Además de endpoints y modelos, se comprobó
en el navegador el flujo de ejemplos, formulario y resultados de coincidencia,
inconsistencia y ausencia de placa. Las cinco capturas reales están en el
[manual de usuario](manual_usuario.md). No se ha realizado una auditoría completa
de accesibilidad, usabilidad, seguridad ni un despliegue público.
