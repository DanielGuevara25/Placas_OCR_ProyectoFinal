# Estado de preparación de la entrega

Auditoría inicial: 19 de octubre de 2026. Este archivo registra pendientes;
no certifica que el proyecto ya cumpla toda la rúbrica.

## Aplicación identificada

La aplicación web usa Flask (`app/app.py`), HTML en `app/templates/`
y JavaScript/CSS en `app/static/`. Actualmente se inicia en localhost.
El código está separado en `src/` y `app/`; los lanzadores de la raíz conservan
los comandos anteriores. Las copias antiguas están en `archive/`, excluido de Git.
El mapa de movimientos está en `organizacion.md` y `migracion_archivos.json`.

La web carga por defecto
`models/best.pt` con Ultralytics (copia verificada del experimento de regularización),
y utiliza el OCR `cct-s-v2-global-model`. El detector predeterminado del
ejecutable de consola es distinto: emplea `open-image-models`.
La documentación final debe distinguir ambos recorridos.

## Orden de preparación y publicación

1. Inventariar evidencias, separar datos locales y definir exclusiones de Git: realizado.
2. Organizar `src/`, `app/`, `data/`, `models/`, `notebooks/` y `results/`
   conservando imports, recursos y rutas funcionales: realizado; 10 pruebas web aprobadas.
3. Reconstruir dependencias reproducibles y verificar pruebas e inferencia:
   realizado en `.venv-tests/`, Python 3.12.14 CPU; versiones en `requirements-tested.txt`.
4. Completar README y los seis documentos exigidos en `docs/`.
5. Distribución de tres checkpoints finales preparada y documentada;
   arranque de producción y despliegue web pendientes.
6. Revisar archivos publicables, crear el repositorio y subir el código.
7. Incorporar URL de la aplicación y enlaces reales de ambos videos.

## Evidencias encontradas

| Elemento | Evidencia local | Pendiente |
|---|---|---|
| Interfaz web | `app/app.py`, `app/templates/`, `app/static/` | Inferencia real comprobada en 3 ejemplos; despliegue pendiente |
| Experimentos | `docs/optimizacion.md`, comparación reproducible y dos figuras | Ampliación de sensibilidad/Workshop S5 pendiente |
| Detector | `results/evaluation/README.md` y `app/static/evaluation/` | Confirmar separación de datos; SHA256 en `models/manifest.json` |
| OCR | `results/evaluation/analisis_ocr.md` | Integrar resultados con sus límites |
| Pruebas | `tests/` y `docs/pruebas.md` | 10 unitarias y 3 casos reales aprobados |
| Ejemplos web | `app/static/examples/` | Comprobar permisos antes de publicación pública |
| Dependencias | `requirements.txt`, `requirements-tested.txt` | Instalación CPU verificada; despliegue por verificar |
| Git | Primera versión publicada en `main` de `DanielGuevara25/Placas_OCR_ProyectoFinal` | Completar pendientes antes de la entrega final |

## Documentación por completar

- `planificacion.md`: preparado como reconstrucción basada en evidencias;
  inicio y periodos de datos, entrenamiento, pruebas y web confirmados;
  plazo oficial pendiente.
- `analisis_datos.md`: preparado con procedencia declarada, auditoría de 7.332
  imágenes, etiquetas, duplicados exactos y seis gráficos EDA.
- `arquitectura.md`: preparado con diagrama, API, modelos inspeccionados,
  parámetros, versiones y límites del despliegue.
- `optimizacion.md`: comparación y límites documentados; faltan experimentos
  suficientes para dependencia parcial, importancia e interacciones del Workshop S5.
- `consideraciones_eticas.md`: preparado con los ocho ejes de la directriz,
  medidas implementadas y controles pendientes diferenciados.
- `manual_usuario.md`: preparado con cinco capturas reales y anotaciones,
  pasos, interpretación, exportaciones, FAQ y problemas comunes; contacto por WhatsApp.

No se deben presentar análisis o gráficos no realizados como evidencia experimental.

## Bloqueos técnicos observados

El ejecutable `.venv/Scripts/python.exe` apunta a una instalación ausente de
Python 3.11. No se ha podido listar las dependencias de ese entorno ni ejecutar
la aplicación con él. No se ha modificado ese entorno.

Se creó un entorno independiente `.venv-tests/` con Python 3.12.14 que sí ejecuta
las pruebas unitarias y la inferencia real en CPU. No es necesario usar el entorno roto
para iniciar la web; consultar `pruebas.md`.

Se agregaron PyTorch, Ultralytics, PyYAML y matplotlib a los requirements,
y se unificó la instalación de la web. El entrenamiento de mejoras exige
explícitamente Ultralytics 8.4.171. La instalación CPU está verificada;
falta verificar el entorno del despliegue. Las versiones probadas en Windows CPU están
fijadas en `requirements-tested.txt`; también se agregó ONNX Runtime para el OCR.

## Publicación web pendiente

Flask sirve también los HTML, CSS y JavaScript existentes. Es necesario alojar
el backend Python para ejecutar los modelos. Un alojamiento de archivos
estáticos por sí solo no ejecuta la inferencia.

Antes del despliegue hay que definir el servidor de producción, puerto e interfaz
de escucha, memoria disponible, dispositivo CPU/GPU, suministro de pesos y
descarga inicial del OCR. La retención de análisis usa memoria del proceso;
debe tenerse en cuenta al configurar múltiples procesos.

Los tres checkpoints finales están preparados para incluirse en Git, con origen,
descarga y SHA256 documentados; los pesos por época permanecen fuera.
El acceso remoto se comprueba después de publicar esta revisión.
También hay que revisar las imágenes de ejemplo y los resultados que contengan
matrículas antes de hacerlos públicos.

## Datos que requieren confirmación del equipo

- Equipo confirmado: Daniel Guevara (Scrum Master) y Christian Guerra
  (Product Owner), ambos como equipo de desarrollo. Distribución técnica
  individual pendiente de especificar. Coordinación y contacto mediante WhatsApp.
- Licencia pública específica del dataset: no indicada. El autor confirmó
  procedencia del sistema laboral y autorización para uso académico y publicación.
- Cronograma confirmado: datos 16–18/09/2026; inicio formal 22/09/2026;
  entrenamientos 29/09–01/10/2026; pruebas iniciales 05–09/10/2026;
  desarrollo web 10–13/10/2026. Plazo oficial y requisitos del Workshop S5 pendientes.
- Repositorio confirmado: `DanielGuevara25/Placas_OCR_ProyectoFinal`.
  Destino del despliegue pendiente.
- Enlaces de videos y preguntas asignadas por el profesor.

## Revisión posterior de requisitos

La auditoría del compañero identificó carencias adicionales: los cinco notebooks
ya se crearon y ejecutaron con salidas reales; los tres pesos finales quedaron
preparados para descarga; se completaron los apartados del README y se aplicó
AGPL-3.0-only tras autorización del equipo. Ver `auditoria_directriz.md`.

El notebook docente de Semana 5 confirma que falta el estudio ampliado de
Optuna, escenarios críticos, importancia, PDP e interacciones. No se marca
resuelto por añadir `04_optimizacion.ipynb`. Existe una RTX 5070 Ti de 16 GB
en el equipo, pero el entorno de pruebas actual usa PyTorch CPU; preparar
entrenamientos requiere restaurar un entorno CUDA y acordar el presupuesto.
