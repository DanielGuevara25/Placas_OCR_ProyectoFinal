# Pruebas del sistema

## Entorno de comprobación

Se creó `.venv-tests/` con Python 3.12 para conservar el entorno original `.venv/`,
cuyo intérprete Python 3.11 ya no está disponible. Las dependencias se instalan con:

```powershell
.\.venv-tests\Scripts\python.exe -m pip install -r requirements.txt
```

Para el servidor protegido instalar además `requirements-demo.txt`. El entorno
CPU congelado se describe en `requirements-tested.txt`; notebooks y estudio S5
tienen dependencias adicionales separadas. No se ha verificado un clon limpio
en Linux ni se presenta el entorno Windows como una prueba de portabilidad.

## Pruebas unitarias

```powershell
.\.venv-tests\Scripts\python.exe -m unittest discover -s tests -v
```

Las **16 pruebas actuales aprobaron el 23/10/2026**. La comprobación inicial
tenía diez casos; se añadieron tres de integridad de modelos y tres de acceso
protegido. Se usan modelos simulados y descargas simuladas. Verifican:

- Rechazo de imágenes inválidas y umbrales incorrectos.
- Normalización y validación de la matrícula declarada.
- Recortes limitados al tamaño de la imagen.
- Selección manual cuando existen varias placas.
- Coincidencias, discrepancias y lecturas inciertas.
- Respuesta cuando no se detectan placas o falta el modelo.
- Manejo de errores OCR por recorte.
- Exportaciones JSON/ZIP y reutilización de modelos.
- Disponibilidad de HTML, JavaScript y CSS.
- Acceso con contraseña, rechazo de credenciales inválidas y configuración débil.
- Bloqueo de peticiones de otro origen y límite de análisis de la demo.
- Integridad SHA256/tamaño y conservación del modelo ante descargas inválidas.

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
Los diez casos iniciales también aprobaron dentro del entorno nuevo; la suite
ampliada de dieciséis se volvió a verificar el 23/10/2026.

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
de accesibilidad, usabilidad ni seguridad de producción.

## Demo temporal por HTTPS

El 21/10/2026 se comprobó el servidor Waitress y el enlace Cloudflare:
401 sin contraseña, 200 con contraseña y una inferencia real con resultado
`coincide` sobre un ejemplo conocido. La evidencia operativa está localmente
en `.model-cache/demo/comprobacion_publica.json`, sin incluir la contraseña.
Esto no constituye una prueba de carga ni una medición de disponibilidad.
El 23/10 el hostname anterior no respondió y no se encontró un túnel activo.
Se debe reabrir y comprobar el enlace vigente antes de la evaluación.
