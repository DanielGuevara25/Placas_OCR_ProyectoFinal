# Planificación del proyecto PlacaLab

## Estado y trazabilidad de este documento

Esta planificación se reconstruye durante la preparación de la entrega a partir
del código, resultados y decisiones disponibles. No se presenta como un plan
inicial fechado antes del desarrollo. El equipo confirmó el inicio del proyecto
el **22 de septiembre de 2026** y el uso de **WhatsApp** para coordinación y
contacto. También confirmó las fechas de preparación de datos, entrenamiento,
pruebas y desarrollo web indicadas más adelante. La fecha límite oficial sigue
pendiente. Los integrantes y roles fueron confirmados por el equipo.

## Problema y relevancia

La revisión de evidencia fotográfica de un vehículo requiere comprobar que la
placa visible concuerde con la declarada. La lectura manual puede verse limitada
por imágenes pequeñas, placas de otros vehículos o caracteres poco distinguibles.

PlacaLab propone detectar las placas, mostrar recortes, reconocer caracteres
y hacer explícita la comparación. Se dirige a revisores humanos de evidencia
vehicular y a una demostración académica aplicada a seguros. La utilidad operativa
es una motivación; no se ha medido ahorro de tiempo o coste en una organización.

## Objetivo general

Desarrollar y documentar una aplicación web que detecte placas en fotografías,
reconozca su texto y apoye la comparación con una matrícula declarada, mostrando
evidencia, resultados y limitaciones para revisión humana.

## Objetivos específicos y evidencia

| Objetivo | Evidencia disponible | Estado |
|---|---|---|
| Preparar un dataset con particiones reproducibles | 7.332 imágenes, manifiesto y semilla 42 | Ejecutado; independencia por vehículo pendiente |
| Entrenar un detector y comparar variantes | Baseline, regularización y rotación, 100 épocas cada uno | Ejecutado |
| Evaluar detección y lectura por separado | Métricas del detector y muestra OCR transcrita | Ejecutado con límites documentados |
| Integrar una web con validación, ejemplos y exportación | Flask, HTML/CSS/JS y modelos locales | Funcional localmente |
| Comprobar el comportamiento | 10 pruebas unitarias, 3 casos reales y recorrido visual | Ejecutado |
| Documentar arquitectura, datos, optimización y ética | Archivos de `docs/` y gráficos | Preparado; pendientes específicos del Workshop S5 |
| Publicar una versión reproducible | Repositorio público y despliegue accesible | Pendiente |
| Comunicar el proyecto | Pitch y respuestas a preguntas | Pendiente |

## Alcance

Incluye fotografías estáticas, una clase de objeto, varias placas por imagen,
selección manual cuando corresponde, OCR preentrenado, comparación textual,
confianzas, advertencias y descargas JSON/ZIP/recortes.

Quedan fuera del alcance validado: vídeo en tiempo real, seguimiento temporal,
consulta de propietarios, identificación integral del vehículo, detección de
daños, autenticidad documental, detección de fraude y aprobación automática
de pólizas. El servicio público multiusuario todavía requiere preparación.

## Metodología y decisiones

1. Utilizar capturas del sistema laboral del autor, quien confirmó autorización
   para uso académico y publicación. Documentar procedencia sin atribuir una
   licencia abierta no especificada.
2. Preparar cajas YOLO con propuestas de detector y registros de revisión;
   separar grupos de píxeles idénticos con semilla 42.
3. Comparar tres configuraciones de YOLOv9t con una métrica principal explícita:
   mAP50-95 de validación. No usar test para elegir hiperparámetros.
4. Conservar el experimento de regularización como detector de la web por
   su mayor resultado de validación entre las corridas disponibles.
5. Integrar OCR preentrenado y reglas de comparación inspeccionables, manteniendo
   resultados reales aunque existan errores o baja cobertura de transcripción.
6. Verificar por pruebas automatizadas e interacción real y documentar los límites.

## Cronograma: secuencia prevista frente a ejecución observada

La columna prevista expresa una secuencia lógica reconstruida para organizar
la entrega. Las fechas históricas de ejecución fueron confirmadas por el equipo;
no se dispone de un cronograma inicial para medir desviaciones frente al plan.

| Fase | Secuencia prevista | Ejecución observada | Fecha y fuente |
|---|---|---|---|
| Definición | Precisar problema, usuarios y alcance | Caso de revisión vehicular documentado | Inicio del proyecto: 22/09/2026, confirmado por el equipo |
| Datos (preparación previa) | Reunir, anotar y dividir | Dataset preparado; auditoría adicional durante la entrega | 16–18/09/2026, confirmado por el equipo |
| Modelado y experimentos | Entrenar baseline y variantes | Tres registros de 100 épocas; comparación de configuraciones documentada | 29/09–01/10/2026, tres días, confirmado por el equipo |
| Pruebas iniciales | Comprobar el comportamiento del sistema | Periodo de pruebas declarado por el equipo | 05–09/10/2026, confirmado por el equipo |
| Interfaz | Integrar carga, resultados y ejemplos | Desarrollo de la web local | 10–13/10/2026, confirmado por el equipo |
| Evaluación adicional | Medir detector y OCR por separado | Evidencias y análisis de errores posteriores a las pruebas iniciales | Archivos de evaluación indican 18/10/2026 |
| Verificación | Probar y corregir integración | Entorno CPU reconstruido y pruebas aprobadas | Preparación de entrega, 19/10/2026 |
| Documentación | Completar seis documentos y README | Archivos preparados con evidencias y pendientes | Preparación de entrega, 19/10/2026 |
| Publicación | GitHub, pesos y despliegue | Pendiente de preparar y verificar | Fecha propuesta pendiente |
| Presentación | Grabar pitch y responder preguntas asignadas | Pendiente | Plazos oficiales pendientes |

No se calcula retraso ni cumplimiento de plazos porque no se dispone de la
fecha límite ni de un cronograma inicial por fase. La fecha de inicio confirmada
no se atribuye a todas las actividades. La directriz adjunta deja en blanco
las fechas de videos.

La preparación de datos del 16 al 18 de septiembre es una actividad previa
al inicio formal del 22 de septiembre. Las pruebas del 5 al 9 de octubre
se distinguen de las evaluaciones adicionales del 18 y de las verificaciones
de integración realizadas durante la preparación de la entrega. No se atribuyen
las pruebas de navegador de la versión actual al periodo anterior al desarrollo web.

## Recursos

| Recurso | Uso y disponibilidad |
|---|---|
| Datos | 7.332 imágenes procesadas y 8.208 cajas; originales locales conservados |
| Pesos | `models/best.pt`, peso base y checkpoints históricos locales |
| Entrenamiento | Scripts con CUDA; el registro histórico indica PyTorch 2.7.1+cu128 |
| Inferencia probada | Windows, Python 3.12.14 y PyTorch 2.14.1 CPU en `.venv-tests/` |
| Software | Ultralytics, fast-plate-ocr, ONNX Runtime, Flask, NumPy y Pillow |
| Interfaz | Navegador y recursos HTML/CSS/JavaScript existentes |
| Publicación | Cuenta/repositorio GitHub y alojamiento aún por concretar |
| Equipo humano | Daniel Guevara (Scrum Master) y Christian Guerra (Product Owner); ambos integran el equipo de desarrollo |

Las versiones completas verificadas están en `requirements-tested.txt`.
No se ha medido el mínimo de RAM ni se ha validado una capacidad de concurrencia
de producción. El OCR necesita sus pesos en caché o conexión para obtenerlos
en la primera inicialización.

## Equipo y responsabilidades

| Integrante | Rol Scrum | Participación confirmada |
|---|---|---|
| Daniel Guevara | Scrum Master | Equipo de desarrollo |
| Christian Guerra | Product Owner | Equipo de desarrollo |

Los roles organizativos se distinguen de la participación técnica: ambos
forman parte del equipo de desarrollo. No se atribuyen tareas específicas
de programación, entrenamiento o documentación a una persona sin confirmación.

La coordinación y el contacto del equipo se realizaron mediante WhatsApp.
No se publican números telefónicos ni enlaces de invitación que no hayan
sido proporcionados para ese fin.

## Riesgos y mitigación

| Riesgo | Medida aplicada | Pendiente |
|---|---|---|
| Capturas relacionadas entre particiones | Agrupación y auditoría de duplicados exactos | Auditar vehículo/sesión y casi duplicados |
| OCR incorrecto con alta confianza | Mostrar recortes, texto y advertencias; pedir revisión en casos inciertos | Calibración y evaluación mayor |
| Fondos negativos poco representados | Limitación declarada y ejemplo funcional sin placa | Construir conjunto negativo representativo |
| Etiquetas geométricamente válidas pero incorrectas | Comprobación de formato, coordenadas y manifiesto | Auditoría visual independiente |
| Problemas de instalación | Entorno nuevo probado y versiones guardadas | Verificar plataforma de despliegue |
| Exposición de fotos y matrículas | Separación de datos locales e informes agregados | Controles de acceso y retención de producción |
| Modelo inaccesible al clonar | Pesos locales con SHA256 y origen registrado | Definir descarga pública reproducible |
| Evidencia insuficiente de optimización avanzada | Reportar tres corridas y límites reales | Diseño suficiente para requisitos del Workshop S5 |
| Retrasos de presentación | Identificar dos videos y preparar guiones | Confirmar plazos y preguntas del profesor |

## Criterios de cierre de la entrega

- Repositorio público accesible con README, licencia definida, dependencias,
  estructura y documentación verificadas.
- Obtención de pesos y ejecución desde una copia nueva documentadas y probadas.
- Interfaz desplegada y comprobada en su entorno final.
- Métricas, comparación con baseline, gráficos y límites trazables a evidencias.
- Pendientes de optimización avanzada resueltos o explícitamente identificados
  sin presentarlos como análisis ejecutados.
- Pitch de máximo cinco minutos con interfaz real y casos de uso, más video
  de respuestas a las preguntas asignadas; enlaces reales en el README.
- Integrantes, contribuciones, contacto y fechas confirmados.

## Documentos relacionados

- [Análisis de datos](analisis_datos.md).
- [Optimización](optimizacion.md).
- [Arquitectura](arquitectura.md).
- [Consideraciones éticas](consideraciones_eticas.md).
- [Manual de usuario](manual_usuario.md).
- [Estado de entrega](estado_entrega.md).
