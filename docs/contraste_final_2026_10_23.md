# Contraste final con la directriz - 23/10/2026

**Actualización posterior al contraste:** el equipo solicitó corregir la
documentación. Se actualizaron README, planificación, arquitectura, ética,
manual, pruebas y estado de entrega. Las inconsistencias descritas en la
sección 3 de este informe registran el diagnóstico previo y ya se corrigieron.
Consultar [estado vigente](estado_entrega.md) para los pendientes actuales.
Esta actualización no graba videos, reactiva el túnel ni cierra los puntos
de calidad/reproducibilidad identificados en la sección 4.

## Dictamen

La base técnica está implementada y publicada, pero la entrega completa **no
está cerrada**. Faltan incorporar los dos videos obligatorios y sus enlaces;
restablecer y verificar el acceso de la demo; y pulir inconsistencias de la
documentación y requisitos de calidad/reproducibilidad detallados abajo.

Fuente: `PROYECTO_FINAL_descripcion_2026 (1).pdf`, 13 páginas, proporcionado
por el usuario. SHA256:
`d97f040dfe9a85fe212bbe0767438458235d5ddc026638025d4405275b5b5f61`.
Se extrajeron las 13 páginas y se renderizaron las páginas 6 a 10 para revisar
los requisitos de optimización, documentación, presentación y rúbrica.
Las instrucciones del PDF se utilizan como criterios de contraste; no como
autorización para comprar servicios, publicar datos ni inventar evidencias.

## Comprobaciones realizadas hoy

- Repositorio público confirmado por la API de GitHub:
  `DanielGuevara25/Placas_OCR_ProyectoFinal`.
- `main` remoto: `94c910f672ea980eec6445e7a7a2cd43ba6bb34a`.
- Todos los archivos principales contrastados existen localmente y en el árbol
  remoto: README, requirements, gitignore, LICENSE, seis documentos, cinco
  notebooks, README de datos/modelos, aplicación y dependencias de la app.
- Cinco notebooks válidos; todas sus celdas de código tienen contador de
  ejecución y ninguna salida de error guardada. Esto no significa que se
  reentrene el modelo al abrirlos: muestran evidencias y código reproducible.
- Tres checkpoints locales coinciden en tamaño y SHA256 con el manifiesto.
  La descarga pública de los tres fue verificada el 21/10; ver
  [verificación pública](../results/reports/verificacion_github.json).
- Se volvieron a ejecutar los **16 tests unitarios**, todos aprobados. Los
  mensajes de fallo OCR en algunos casos son simulaciones intencionales.
- Seis figuras EDA individuales y una lámina resumen; cinco capturas del manual.
- Ningún enlace relativo roto detectado en README y documentos principales.
- No se pudo acceder al hostname temporal anterior y no se encontró un proceso
  `cloudflared` activo. No se reabrió el túnel durante esta revisión.

## Matriz de requisitos

| Requisito de la directriz | Evidencia | Resultado |
|---|---|---|
| Repositorio público y estructura, pp. 1-2 | GitHub; `docs/`, `data/`, `notebooks/`, `src/`, `models/`, `app/`, `tests/`, `results/` | Presente y publicado |
| README con 14 apartados, pp. 2-3 | [README](../README.md) con badges, problema, datos, método, resultados, instalación, interfaz, autores, licencia y referencias | Parcial: videos sin enlaces y frases antiguas contradictorias |
| Dependencias, gitignore y licencia, pp. 1, 7-8 | Requirements principales y archivos específicos; AGPL-3.0-only y atribuciones | Presentes; requisitos raíz no fijan todas las versiones, aunque existe congelado Windows CPU |
| Cinco notebooks, p. 2 | [Notebooks](../notebooks/) 01 a 05 ejecutados | Presente |
| Código de preparación, modelo, entrenamiento y evaluación, p. 2 | `preparar_dataset.py`, `plate_detector.py`, `entrenar_placas.py`, `evaluar_ocr.py`, otros módulos en `src/` | Responsabilidades presentes con nombres adaptados a YOLO |
| Modelos accesibles, p. 2 | Tres `.pt`, manifiesto, recuperador con SHA256 y descarga pública comprobada | Presente; `.pt` es formato de PyTorch, no debe renombrarse a `.pkl` |
| Input validado, predicción, espera y errores, p. 4 | Flask, formulario, JS, validaciones y tests | Implementado; comprobación real por HTTPS guardada el 21/10 |
| Outputs, confianza, visualizaciones, p. 4 | Cajas, recortes, OCR, confianzas, comparación y JSON/ZIP | Implementado; no equivale a una probabilidad calibrada |
| Acerca del modelo, métricas, límites y ejemplos, p. 4 | Secciones de información y tres ejemplos precargados | Implementado |
| Acceso utilizable y link si aplica, pp. 1, 3, 10 | Túnel temporal protegido e instrucciones en [demo](demo_temporal.md) | Pendiente operativo: restablecer y compartir URL y acceso vigentes |
| Planificación, p. 5 | [Planificación](planificacion.md): problema, objetivos, alcance, cronograma, recursos y riesgos | Contenido presente, reconstruido honestamente; actualizar estados antiguos |
| EDA con 5-6 gráficos, p. 5 | [Análisis de datos](analisis_datos.md), seis figuras, estadísticas, faltantes, desbalance y extremos | Presente; no prueba independencia por vehículo |
| Arquitectura y pipeline, p. 5 | [Arquitectura](arquitectura.md), diagrama, capas/parámetros y versiones | Presente; corregir descripción antigua del servidor y acceso |
| Optimización S5, p. 6 | [Diseño](estudio_semana5.md), [resultados](resultados_semana5.md), notebook 04 y `results/semana5/` | Ejecutado con límites: ver interpretación debajo |
| Ocho ejes éticos, pp. 6-7 | [Consideraciones éticas](consideraciones_eticas.md) | Ocho apartados presentes; actualizar controles de la demo y retención |
| Manual con capturas, FAQ, ayuda y soporte, p. 7 | [Manual](manual_usuario.md), cinco capturas reales con explicaciones | Presente; añadir acceso a demo protegida y una vía de soporte accionable |
| Calidad, configuración y modularidad, p. 7 | Módulos separados, configuración, validación y manejo de errores | Parcial: estilo compacto con líneas extensas, docstrings desiguales; no se hizo auditoría completa PEP 8 |
| Versionamiento, branches y tags, p. 7 | Seis commits descriptivos publicados; sólo rama `main`, sin tags observados | Commits presentes; falta evidenciar rama de desarrollo y versión etiquetada |
| Al menos 3-5 tests, p. 8 | 16 pruebas aprobadas hoy | Supera el mínimo |
| Pitch de máximo cinco minutos, pp. 8-9 | README lo declara pendiente; no se aportó video verificable | Falta incorporar y comprobar |
| Video de preguntas del profesor, pp. 9-10 | No se aportaron preguntas ni video verificable; README pendiente | Falta incorporar y comprobar |
| Ambos enlaces de videos en README, pp. 3, 10 | Tabla de videos sin URLs | Falta |

La estructura del PDF muestra nombres orientativos genéricos (`model.py`,
`best_model.pkl`, `assets/`). El proyecto usa módulos con responsabilidades
equivalentes, pesos `.pt` y recursos Flask en `static/` y `templates/`.
Conviene hacer explícito ese mapa, sin duplicar código o cambiar extensiones
para aparentar equivalencia. La aceptación literal de nombres corresponde al
docente; no se garantiza aquí.

## Qué demuestra realmente Semana 5

Se procesaron 60 ensayos: 17 completos y 43 podados. Hay rangos, historial,
importancia fANOVA, slice, PDP y contorno de un sustituto, dos ajustes de 100
épocas y nueve escenarios de robustez. No faltan esos archivos experimentales.

Ganó la misma configuración de referencia. Por ello no se demuestra una mejora
del nuevo estudio; las dos corridas finales comparten configuración y semilla.
El sustituto se ajusta con 17 puntos completos y su R² varía entre particiones;
los gráficos son exploratorios. No se dispone de múltiples semillas ni de una
nueva evaluación final independiente del candidato ampliado. Test quedó fuera
de la búsqueda y se conserva la evaluación histórica, sin asignarle un hash
retroactivamente.

La rúbrica menciona mejoras cuantificables para excelencia. Tener las gráficas
no garantiza ese nivel; tampoco autoriza a afirmar una mejora que no ocurrió.
El resultado negativo está documentado y debe explicarse en la presentación.
Los 60 ensayos proceden del ejemplo docente, no de un número exigido en este PDF.

## Pendientes prioritarios

### 1. Videos obligatorios

El pitch debe durar como máximo cinco minutos e incluir los siete bloques:
problema 30 s, datos/método 60 s, desarrollo/optimización 45 s, demo real 60 s,
evaluación 45 s, ética 45 s y cierre 15 s. Mostrar 2-3 casos y manejo de errores,
audio claro, mínimo 720p, máximo 8-10 diapositivas y URL/QR del proyecto.
No hace falta una presentación en vivo: el PDF exige grabación de pantalla real.

El segundo video responde todas las preguntas asignadas, en orden y numeradas;
duración y plazo dependen de lo que entregue el profesor. No están especificados
en el PDF aportado. Los plazos del pitch y preguntas aparecen en blanco.
No se puede afirmar que estos videos no existan fuera de la carpeta revisada;
lo pendiente verificable es aportarlos y enlazarlos en README con acceso habilitado.

### 2. Acceso real de la interfaz

Reabrir servidor y túnel, verificar desde otra red y proporcionar el enlace
vigente y las credenciales al evaluador por un canal adecuado. No publicar la
contraseña en GitHub ni en el video. Un hostname temporal antiguo no debe
usarse como única referencia en un QR impreso: el repositorio tiene URL estable.
El PDF no exige pagar hosting ni nombra un proveedor obligatorio.

### 3. Coherencia de la documentación

Hay estados históricos mezclados con los actuales:

- README aún dice en su sección ética que faltan controles de acceso y en
  otra sección habla de pendientes de licencia/optimización ya resueltos.
- Planificación conserva tareas de publicación/S5 como pendientes y diez tests.
- Arquitectura describe únicamente Flask de desarrollo, sin autenticación
  ni temporizador; la demo usa Waitress, contraseña y limpieza periódica.
- Ética afirma que no hay acceso controlado ni limpieza programada. Sigue
  siendo cierto que no hay cuentas individuales o auditoría de usuarios.
- Manual explica localhost, pero no el ingreso a la demo mediante contraseña.
- Estado de entrega acumula pendientes antiguos y actualizaciones posteriores;
  separar historial de una lista vigente reduciría contradicciones.
- Pruebas debe distinguir los diez casos iniciales de los dieciséis actuales.

### 4. Reproducibilidad y calidad

- Consolidar versiones para instalación de demo y documentar por separado
  entorno Windows CPU, entrenamiento CUDA y una instalación limpia en Linux.
  Tener un entorno existente funcionando no prueba un clon limpio en Linux.
- Los datos de entrenamiento están excluidos del repositorio. Hay autorización
  declarada y documentación de procedencia, pero no enlace al dataset completo
  ni licencia abierta especificada. Esto no obliga a abrir los datos laborales;
  sí limita la reproducción del entrenamiento por terceros. Definir condiciones
  de acceso si se espera que el evaluador lo reproduzca.
- Ajustar estilo y docstrings de módulos compactos y revisar rutas absolutas
  en scripts propios. Las rutas históricas de `args.yaml` son evidencia, no
  deberían reescribirse sólo por estética.
- Trabajar futuras correcciones en una rama y etiquetar una versión cuando
  realmente esté lista. Crear una rama vacía no demuestra desarrollo previo.
- El PDF pide roles de autores y están presentes. Es recomendable describir
  además contribuciones técnicas concretas, sólo con confirmación del equipo.

## Límites de esta auditoría

No certifica una nota, cumplimiento jurídico, seguridad de producción, calidad
de cada etiqueta o corrección de todo el código. No se repitieron entrenamientos
ni se recalcularon métricas de test. Se comprobó existencia de evidencias,
consistencia básica, notebooks, tests, hashes y presencia remota. La conexión
fallida de la demo describe la comprobación de hoy, no su disponibilidad pasada.
Los extras de interfaz (multilenguaje, PDF/CSV, etc.) se valoran en el PDF pero
no sustituyen los requisitos mínimos ni son todos obligatorios.
