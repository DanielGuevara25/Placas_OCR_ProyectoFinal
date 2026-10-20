# Consideraciones éticas de PlacaLab

## Alcance de uso

El propósito es apoyar la revisión de fotografías de vehículos mediante detección
y comparación de placas. Los destinatarios son revisores humanos y usuarios
académicos. La salida no demuestra identidad del vehículo, autenticidad de la
documentación, ausencia de alteración ni existencia de fraude.

Este documento distingue medidas implementadas de acciones propuestas.
La inferencia local fue comprobada, pero no se ha validado un sistema autónomo
para decisiones de aseguramiento ni un servicio público multiusuario.

## 1. Sesgos del dataset

Las imágenes proceden del sistema de reconocimiento de placas del lugar de
trabajo del autor. La autorización para uso académico y publicación fue confirmada
por el autor; no implica que las capturas representen a todos los vehículos,
formatos de placa, cámaras, regiones o condiciones de iluminación.

El conjunto procesado contiene 7.332 imágenes y 8.208 cajas. No incluye imágenes
anotadas como negativas. El registro previo selecciona 7.332 filas revisadas
y omite 6.289 con estado `ERROR_IMAGEN`; no se diagnosticó en esta auditoría
la causa de esas omisiones. Puede existir sesgo de selección hacia capturas
que el proceso de preparación pudo leer y anotar.

El 30,82 % de las cajas tiene menos de 16 píxeles de alto. El OCR podría
perjudicar a usuarios que sólo disponen de fotografías pequeñas o difíciles.
Esta es una limitación plausible, no una medición causal del efecto de resolución.

Se descartaron duplicados exactos entre particiones, pero no capturas relacionadas
del mismo vehículo, sesión o cámara. Una dependencia no detectada podría hacer
que las métricas parezcan más generalizables de lo que realmente son.

## 2. Equidad y fairness

No se dispone de una auditoría de rendimiento por grupos de usuarios, condiciones
de captura, tipos de vehículos o formatos de matrícula. No se calcularon métricas
de fairness ni se afirma trato equitativo por la sola existencia de una clase.
No se infieren atributos demográficos a partir de una matrícula o fotografía.

Una lectura incorrecta puede producir una inconsistencia y trabajo adicional
para el usuario. El sistema reduce el alcance de la decisión mediante mensajes
de revisión y solicitud de otra foto, pero esas medidas no garantizan igualdad
de tasas de error entre grupos.

Como trabajo futuro se propone evaluar error, cobertura y frecuencia de revisión
por condiciones de imagen y formatos autorizados, sin inferir atributos sensibles.
Estas evaluaciones no están implementadas todavía.

## 3. Privacidad y datos

Las matrículas, fotografías, nombres de archivo y contexto de captura pueden
permitir vincular información con vehículos o personas. Se tratan como datos
que requieren cuidado, sin afirmar una clasificación jurídica universal.
La procedencia y autorización declaradas constan en
[data/procedencia.md](../data/procedencia.md).

Medidas implementadas:

- El backend procesa las cargas en memoria y no las escribe automáticamente en disco.
- Hay límites de tamaño y resolución; las solicitudes y resultados se validan.
- Las respuestas usan `Cache-Control: no-store` y `X-Content-Type-Options: nosniff`.
- El almacenamiento temporal tiene un máximo de cuatro análisis por proceso.
- Los datos completos e inventarios locales están excluidos de Git; los informes
  EDA públicos son agregados y no contienen nombres de archivo ni matrículas.

Límites de estas medidas:

- Los quince minutos de retención se aplican al limpiar durante una solicitud,
  no mediante borrado programado al segundo exacto de vencimiento.
- Las descargas guardadas por el usuario y los ejemplos estáticos sí persisten.
- El OCR puede descargar pesos al inicializar si no están en caché; la inferencia
  implementada usa modelos locales y no envía la foto a una API OCR externa.
- No hay cuentas, control de acceso ni vinculación de análisis a un usuario.
  Un identificador aleatorio no sustituye estos controles.
- No se realizó una evaluación jurídica de obligaciones aplicables ni se certifica
  cumplimiento de un régimen de protección de datos por estas medidas técnicas.

Antes de un despliegue público deben definirse acceso, transporte cifrado,
retención operativa, límites de solicitudes y gestión de datos exportados.
Estas son tareas pendientes, no controles ya desplegados.

## 4. Transparencia y explicabilidad

La interfaz muestra cajas, recortes, lectura original, confianza de detección
y confianzas por carácter. El JSON/ZIP conserva la placa declarada, selección,
texto normalizado, decisión y umbrales. Las reglas de comparación son explícitas.

Esto permite inspeccionar la evidencia y entender la comparación textual,
pero no explica internamente cada decisión de las redes neuronales. No se han
implementado SHAP, LIME ni mapas de atribución. La salida de región del OCR
no se utiliza para identificar país o procedencia del vehículo.

El promedio de confianza no está calibrado como probabilidad de matrícula
correcta. La evaluación encontró una lectura errónea con confianza media de
99,29 %. No debe presentarse ese promedio como garantía de exactitud.

## 5. Impacto social

El beneficio esperado es facilitar revisión de evidencia, hacer visible una
inconsistencia y conservar resultados inspeccionables. No se ha medido un ahorro
de tiempo o coste en operación real, por lo que no se presenta como impacto demostrado.

Los daños posibles incluyen solicitar trámites adicionales por una lectura
equivocada, asociar una placa de fondo al vehículo inspeccionado, aceptar una
coincidencia errónea o exponer imágenes y matrículas mediante una publicación
o exportación mal gestionada.

La selección manual ante varias detecciones y los mensajes de revisión están
implementados. Incluso con una sola detección, el usuario debe comprobar que
la caja pertenece al vehículo correcto; esa correspondencia semántica no la
garantiza la selección automática.

## 6. Responsabilidad y monitoreo

La decisión final corresponde al revisor y a la organización que utilice la
herramienta. El equipo del proyecto debe mantener documentación, versiones,
pruebas y registro de cambios. El equipo está conformado por Daniel Guevara
(Scrum Master) y Christian Guerra (Product Owner), ambos integrantes del equipo
de desarrollo. La distribución individual de tareas técnicas no se ha especificado.

El estado `coincide` registra igualdad de texto según reglas iniciales. Su
bandera `manual_review_required=false` no es una aprobación de póliza ni
una verificación de documentación. No existe un flujo implementado de firma
o autorización humana de decisiones comerciales.

Hay hashes del modelo usado, registros de pruebas y exportaciones por análisis.
No existe un historial central, monitoreo de deriva, revisión automática de
sesgos ni sistema de auditoría de usuarios en producción.

Plan propuesto: revisar muestras autorizadas de errores, medir cambios de
rendimiento por condiciones de captura, versionar modelos y datos, validar
cambios con datos separados y registrar decisiones de actualización. No se
debe reajustar el sistema repetidamente contra el mismo test para mejorar cifras.

## 7. Uso dual y mal uso

El reconocimiento de matrículas podría emplearse para seguimiento o vigilancia
fuera del propósito autorizado. El prototipo no implementa seguimiento temporal,
búsqueda de propietarios ni consulta de identidades; tampoco impide técnicamente
que un tercero reutilice su código con otro propósito.

El alcance académico y de revisión de evidencia debe quedar explícito.
No se debe presentar una inconsistencia como prueba de fraude ni una coincidencia
como prueba de identidad. La licencia del código y las condiciones del dataset
deben diferenciarse; autorización de publicación no equivale a una licencia
abierta específica que aún no se ha indicado.

## 8. Limitaciones y casos donde abstenerse

Se requiere otra foto o revisión cuando la lectura esté vacía, falle, sea ilegible,
no cumpla las reglas o la placa no se pueda asociar con el vehículo inspeccionado.
Los umbrales de media ≥0,85 y mínimo ≥0,60 son reglas iniciales sin calibración.

En la muestra OCR previa, tres de las cinco lecturas incorrectas superaron ambos
umbrales. Por tanto, las reglas pueden aceptar texto erróneo; si coincide con
la declaración equivocada, podría registrarse una coincidencia falsa.

La exactitud OCR reportada, 17/22 (77,27 %), se limita a recortes anotados
transcribibles. Los 32 ilegibles de 54 no tienen referencia verificable y no se
cuentan como aciertos. No se confunde esa cifra con el mAP del detector ni con
el rendimiento completo de validación.

El OCR tiene diez posiciones aunque el formulario acepte hasta doce caracteres.
No se demuestra soporte fiable de formatos más largos. Tampoco hay validación
suficiente para imágenes sin placa, fotografías alteradas, nuevos entornos,
formatos no representados o decisiones autónomas que afecten a una persona.

## Evidencias relacionadas

- [Análisis de datos y seis gráficos](analisis_datos.md).
- [Evaluación OCR y errores](../results/evaluation/analisis_ocr.md).
- [Pruebas funcionales](pruebas.md).
- [Arquitectura y retención real](arquitectura.md).

Las limitaciones pendientes forman parte del alcance documentado; no se
presentan como mitigaciones ya implementadas ni como requisitos cumplidos.
