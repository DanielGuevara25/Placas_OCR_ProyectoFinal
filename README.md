# PlacaLab: detección de placas y OCR

Aplicación web Flask para detectar placas en fotografías, leer sus caracteres
y compararlos con una matrícula declarada. Es una herramienta de apoyo a la
revisión de evidencia vehicular; no aprueba pólizas ni demuestra fraude o identidad.

Repositorio: [DanielGuevara25/Placas_OCR_ProyectoFinal](https://github.com/DanielGuevara25/Placas_OCR_ProyectoFinal).

Estado: versión local verificada, entrega en preparación. El despliegue público,
la distribución de pesos, la licencia y los enlaces de videos siguen pendientes.

## Contenido

- [Estructura](#estructura)
- [Ejecución local](#ejecución-local)
- [Entrenamiento y evaluación](#entrenamiento-y-evaluación)
- [Pruebas](#pruebas)
- [Resultados disponibles](#resultados-disponibles)
- [Estado de entrega](#estado-de-entrega)

## Documentación técnica

- [Planificación y alcance](docs/planificacion.md).
- [Manual de usuario con capturas reales](docs/manual_usuario.md).
- [Arquitectura, modelos y flujo del sistema](docs/arquitectura.md).
- [Consideraciones éticas, privacidad y limitaciones](docs/consideraciones_eticas.md).
- [Análisis de datos](docs/analisis_datos.md).
- [Optimización](docs/optimizacion.md).
- [Pruebas](docs/pruebas.md).

## Estructura

```text
placas_ocr/
├── app/                 # Servidor Flask, HTML, CSS, JavaScript y OCR web
│   ├── app.py
│   ├── templates/
│   ├── static/
│   └── requirements.txt
├── src/                 # Detector, OCR de consola, preparación y experimentos
├── data/                # Datos locales y descripción de su organización
│   ├── raw/
│   ├── processed/
│   ├── annotations/
│   ├── review/
│   └── manifests/
├── models/              # Pesos locales y manifiesto SHA256
├── notebooks/           # Espacio para notebooks reales del proyecto
├── docs/                # Documentación y registro de migración
├── results/             # Entrenamiento, evaluación y salidas locales
├── tests/               # Pruebas de la web y validación
├── archive/             # Copias históricas locales, excluidas de Git
├── main.py              # Entrada de consola compatible
├── web_app.py           # Entrada web compatible
├── requirements.txt
└── .gitignore
```

Las imágenes del dataset, pesos y copias antiguas permanecen en el disco,
pero están excluidos de Git. No se han creado notebooks con resultados ficticios.
Consulta [el mapa de archivos](docs/organizacion.md) para localizar el material anterior.

## Ejecución local

Se requiere Python 3.11 o posterior. El entorno `.venv` recibido apunta a una
instalación de Python ausente; hay que reconstruirlo antes de utilizarlo.
Se verificó un entorno nuevo `.venv-tests/` con Python 3.12.14 en CPU.
`requirements-tested.txt` conserva las versiones que aprobaron las pruebas.

Con un Python funcional, desde la raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe web_app.py --device cpu
```

Para obtener el código desde GitHub:

```powershell
git clone https://github.com/DanielGuevara25/Placas_OCR_ProyectoFinal.git
cd Placas_OCR_ProyectoFinal
```

Después se prepara el entorno con los comandos anteriores. Para reproducir
las versiones probadas en Windows/Python 3.12, usar `requirements-tested.txt`
en lugar de `requirements.txt`. Los pesos y el dataset completo no se incluyen
en Git; la inferencia requiere obtener el detector según `models/README.md`.
Mientras su descarga pública esté pendiente, clonar el código por sí solo no
habilita la inferencia real. Las pruebas unitarias usan modelos simulados.

Abre `http://127.0.0.1:8080`. También se puede iniciar con
`python -m app.app --device cpu`.

La web utiliza `models/best.pt` (detector del experimento de regularización)
y `cct-s-v2-global-model` para OCR. El primer uso del OCR puede descargar
sus pesos y requiere Internet. Se puede cambiar el detector con
`--weights "ruta/al/modelo.pt"`. Consulta [models/README.md](models/README.md).

La consola mantiene un recorrido distinto: usa por defecto el detector
preentrenado de `open-image-models`, no el modelo entrenado de la web:

```powershell
python main.py --input "ruta/a/foto.jpg"
```

El servidor local actual no constituye un despliegue público.
El alojamiento web, servidor de producción y distribución pública de pesos
se prepararán después de verificar el entorno completo.

## Entrenamiento y evaluación

Los scripts se ejecutan como módulos desde la raíz. El entrenamiento requiere
CUDA y el dataset preparado; no se ejecuta al iniciar la web.

```powershell
python -m src.entrenar_placas
python -m src.entrenar_mejoras --experimento regularizacion
python -m src.entrenar_mejoras --experimento rotacion
python -m src.evaluar_curvas --solo-graficas
python -m src.preparar_revision_ocr
python -m src.evaluar_ocr
```

Los YAML/JSON de corridas anteriores conservan rutas históricas como evidencia.
El YAML local `data_entrenamiento.yaml` se actualizó a la nueva ubicación del dataset.
El manifiesto histórico de evaluación de curvas puede impedir reanudar una corrida
cuando detecta cambios de configuración; debe preservarse y compararse antes de regenerar.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

Tras reorganizar se ejecutaron 10 pruebas con modelos simulados: entradas inválidas,
HTML/CSS, selección de placas, exportación ZIP, errores y reutilización de modelos.
La inferencia real en CPU también se comprobó con tres ejemplos: coincidencia,
inconsistencia y ausencia de placa, todos con el estado esperado.
Consulta [el informe de pruebas](docs/pruebas.md).

## Resultados disponibles

- [Dataset: análisis exploratorio y seis gráficos](docs/analisis_datos.md).
- [Comparación de experimentos y optimización](docs/optimizacion.md).
- [Evaluación del detector](results/evaluation/README.md).
- [Análisis del OCR y limitaciones](results/evaluation/analisis_ocr.md).
- Configuraciones y métricas de los tres experimentos en `results/training/`.
- Curvas train/val y métricas por época en `results/overfitting/`.

Las métricas del detector, OCR y validación completa representan tareas distintas.
La confianza OCR no es una probabilidad calibrada de matrícula correcta.

| Experimento | Mejor mAP50-95 de validación | Época |
|---|---:|---:|
| Baseline | 88,673 % | 80 |
| Regularización | 89,057 % | 82 |
| Rotación | 88,884 % | 89 |

Valores de los registros de entrenamiento; una corrida por configuración.
La regularización mejora 0,384 puntos porcentuales sobre el baseline.
No se han comprobado diferencias estadísticamente significativas.

## Autores y contribuciones

| Integrante | Rol Scrum | Contribución |
|---|---|---|
| Daniel Guevara | Scrum Master | Integrante del equipo de desarrollo |
| Christian Guerra | Product Owner | Integrante del equipo de desarrollo |

Ambos conforman el equipo de desarrollo del proyecto. No se ha especificado
una distribución individual de tareas técnicas.

El proyecto comenzó el **22 de septiembre de 2026**. El equipo utilizó
**WhatsApp** como medio de coordinación y contacto. Los números y enlaces
de contacto no se incluyen en este repositorio.

## Estado de entrega

Este README es una base de organización, todavía no la documentación final
exigida por la materia. [Estado de entrega](docs/estado_entrega.md) registra
pendientes de documentación, optimización, licencias y despliegue.

La licencia del código sigue por definir. El autor confirmó autorización de uso
académico y publicación del dataset; sus condiciones y procedencia se documentan
en [data/procedencia.md](data/procedencia.md), sin atribuirle una licencia abierta.
Los enlaces del pitch y del video de preguntas aún no se han recibido.
