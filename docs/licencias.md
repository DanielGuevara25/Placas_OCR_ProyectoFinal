# Licencias y atribuciones

## Licencia de los aportes del equipo

El equipo autorizó publicar sus aportes propios bajo **GNU Affero General Public
License, versión 3 (AGPL-3.0-only)**. Autores declarados: Daniel Guevara y Christian
Guerra. El texto íntegro aplicado está en [LICENSE](../LICENSE) y se conserva
también en [AGPL-3.0.txt](licencias/AGPL-3.0.txt).

La licencia permite usar, estudiar, modificar y redistribuir el código bajo
sus condiciones. Incluye obligaciones sobre el código fuente de versiones
modificadas, también en los supuestos de interacción por red contemplados
en la licencia. No es una licencia de uso exclusivamente académico.

Se seleccionó esta opción teniendo en cuenta que la distribución instalada de Ultralytics
8.4.171 declara AGPL-3.0. No se añade una licencia MIT al proyecto completo
suponiendo que las dependencias tengan condiciones idénticas.
Referencias primarias: [licencia de Ultralytics](https://github.com/ultralytics/ultralytics/blob/main/LICENSE)
y [condiciones publicadas por Ultralytics](https://www.ultralytics.com/license).

No se atribuye al equipo la autoría de librerías, pesos preentrenados o material
del curso. Los componentes de terceros conservan sus titulares y condiciones.

## Componentes utilizados

| Componente | Licencia declarada por la distribución instalada | Evidencia |
|---|---|---|
| Ultralytics 8.4.171 | AGPL-3.0 | Texto íntegro distribuido con el paquete, conservado |
| fast-plate-ocr 1.1.0 | MIT | [Texto original](licencias/MIT-fast-plate-ocr.txt) |
| open-image-models 0.6.0 | MIT | [Texto original](licencias/MIT-open-image-models.txt) |

Los archivos de licencia se copiaron de sus distribuciones instaladas sin
reescribir los avisos de sus autores. Las demás dependencias mantienen sus
licencias originales; la lista no pretende relicenciar Python, Flask, PyTorch,
ONNX Runtime ni sus componentes transitivos.

## Modelos y datos

Los tres checkpoints finales son resultados locales de entrenamiento con
Ultralytics desde `yolov9t.pt`. Su publicación no elimina las condiciones de
los componentes y pesos de origen. El manifiesto indica procedencia y hash,
no atribuye al equipo el modelo base ni garantiza una licencia comercial distinta.

El OCR preentrenado se obtiene del hub de fast-plate-ocr, conservando su fuente.
La licencia del paquete no se usa para inventar condiciones adicionales de
datasets o modelos que no estén documentadas por su distribuidor.

La autorización de uso académico y publicación de las fotografías fue declarada
por el equipo; no se ha especificado una licencia abierta del dataset.
La futura licencia del código no se extiende automáticamente a las imágenes
laborales, sus transcripciones ni material docente recibido.
Véase [procedencia](../data/procedencia.md).
