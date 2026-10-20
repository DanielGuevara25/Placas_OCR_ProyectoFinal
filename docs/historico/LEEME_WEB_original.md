# Validación vehicular para seguros - PlacaLab

## Instalar
1. Copia web_app.py, web_service.py, web_ocr.py, web_validation.py, requirements_web.txt y las carpetas
   templates y static a la raíz de **placas_ocr**, junto a config.py y plate_detector.py.
2. Conserva providers.py, el entorno .venv y el resto de tu proyecto original.
3. Desde PowerShell, en placas_ocr:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements_web.txt
.\.venv\Scripts\python.exe web_app.py
```

Abre http://127.0.0.1:8080 en el navegador.

No se incluyen pesos en este ZIP. La ruta predeterminada es:
`entrenamientos/yolov9t_regularizacion/weights/best.pt`.

Si necesitas otra ubicación:
```powershell
.\.venv\Scripts\python.exe web_app.py --weights "C:\ruta\best.pt"
```

Para forzar CPU:
```powershell
.\.venv\Scripts\python.exe web_app.py --device cpu
```

El detector usa CUDA cuando está disponible. El OCR usa ONNX Runtime en CPU,
para reutilizar el entorno funcionando sin configurar nuevas dependencias CUDA de ONNX.
El primer análisis carga los modelos y puede descargar los pesos OCR; necesita Internet.
La aplicación queda escuchando solo en tu PC. Detén el servidor con Ctrl+C.

## Funciones
- Una foto por análisis; múltiples placas en cada imagen.
- Vista previa, imagen original y anotada, recortes y texto OCR sin corregirlo silenciosamente.
- Confianza de detección y por carácter; el promedio OCR no es probabilidad de placa correcta.
- Descarga de JSON, cada recorte o ZIP con foto anotada y todos los resultados.
- Validación de imagen real, límite de 12 MB y 20 megapíxeles, orientación EXIF.
- Avisos de imagen ilegible, falta de modelo, cero detecciones y falla OCR por placa.

Las fotos y resultados se procesan en memoria, sin almacenamiento en disco. Se conservan hasta cuatro análisis durante quince minutos para permitir selección y exportación; se borran al detener el servidor. Los análisis vencidos se descartan en la siguiente petición de análisis o selección. No subir esta versión local directamente a un servidor público.
El navegador conserva el resultado visible hasta cambiar la foto o cerrar la página.

## Integración
- web_app.py: servidor y endpoints.
- web_service.py: carga única de modelos y pipeline de detección/recorte/OCR.
- web_ocr.py: adaptación del OCR suministrado; convierte BGR a RGB y comunica fallos.
- config.py y plate_detector.py: se usan los archivos existentes, configurando backend yolo
  y la ruta de regularización solo para la web; no se modifica su configuración global.
- main.py sigue siendo el ejecutable por consola; la página tiene su propio pipeline.

Confianza inicial 0.60: ajuste práctico inicial, no umbral optimizado con test.
El detector usa NMS IoU 0.7. Ajusta la confianza en la página si necesitas explorar resultados.
No se validó la precisión del OCR con transcripciones verdaderas; verifica las lecturas.

## Verificación
Se comprobaron los endpoints y el pipeline con dobles de prueba:
recortes dentro de la imagen, múltiples placas, fallos OCR, archivo ZIP y carga única de modelos.
La inferencia real con tu best.pt y la caché OCR debe probarse en tu PC: esos pesos no se suministraron aquí.

Pruebas opcionales desde esta carpeta (tests/ también se incluye):
```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

APIs consultadas:
- https://flask.palletsprojects.com/en/stable/patterns/fileuploads/
- https://docs.ultralytics.com/modes/predict/
- https://ankandrew.github.io/fast-plate-ocr/latest/inference/running_inference/

## Validación para seguros
Ingresa la placa declarada antes de analizar la foto. La comparación elimina espacios y guiones y convierte a mayúsculas; no sustituye O por 0 ni I por 1. Se admiten de 2 a 12 caracteres ASCII alfanuméricos, sin imponer un formato de país.

- Una placa: selección automática y comparación.
- Varias placas: selección manual del vehículo; no se elige automáticamente la que coincide.
- Coincidencia: lectura coincidente con promedio OCR >=0.85 y cada carácter >=0.60.
- Inconsistencia: lectura con esos umbrales que difiere de la placa declarada; revisión manual, no afirmación de fraude.
- Lectura vacía, inválida, fallida o bajo umbrales: revisión manual incluso si el texto coincide.
- Sin detección: solicitar otra foto.

Los umbrales son reglas iniciales NO calibradas ni indicadores de precisión. Deben evaluarse con transcripciones verdaderas antes de uso operacional. Cambiar la placa declarada invalida la comparación visible y requiere otro análisis.

La selección se valida en el servidor y actualiza tanto JSON como ZIP. El informe incluye placa declarada, lectura original y normalizada, placa seleccionada, método de selección, decisión, necesidad de revisión y reglas usadas. No hay aprobación automática de pólizas. No valida documentación, características del automóvil, identidad completa ni daños.

Actualizar: detener servidor con Ctrl+C, copiar TODOS los archivos del ZIP a placas_ocr reemplazando únicamente los archivos de esta aplicación, e iniciar de nuevo. Puerto por defecto 8080.

Tema visual: gris oscuro y grafito, con texto claro y alertas verdes, ámbar y rojas. Si ves el estilo anterior, recarga con Ctrl+F5.

## Ejemplos y Acerca del modelo
Copia también static/examples al actualizar. Los tres botones cargan fotografía y placa declarada; el análisis real se ejecuta al pulsar Validar placa. No se usan respuestas simuladas.
- gca4771.png: Toyota, transcripción visual GCA4771; declaración GCA4771.
- gtw9311.png: Kia, transcripción visual GTW9311; declaración GTW9312 para explorar una inconsistencia.
- sin_placa.png: Chevrolet sin placa visible en la parte trasera; declaración de prueba ABC1234.
Las imágenes aportadas por el usuario tienen otras resoluciones que algunos archivos de las pruebas anteriores, por lo que se deben volver a analizar. Su inclusión no acredita derechos de publicación ni convierte los ejemplos en un conjunto de test representativo.
La sección Acerca del modelo incluye funcionamiento, reglas, privacidad y limitaciones. Las métricas agregadas se muestran como pendientes; deben completarse con los resultados reales de evaluación antes de la entrega final.

## Métricas incorporadas
La sección Acerca del modelo muestra la evaluación test aportada el 18/10/2026. Valores exactos y salvedades en evaluation/detector_test.json y evaluation/README.md. Copia también evaluation y static/evaluation. Las métricas OCR siguen pendientes.

## Evaluación OCR incorporada
Resultados locales verificados: 17/22 placas exactas (77,27 %), CER 7/149 (4,70 %). Muestra de 54 recortes de cajas anotadas: 22 legibles y 32 ilegibles. Métricas condicionadas a legibilidad, no del pipeline completo. Ver evaluation/analisis_ocr.md. Se observaron errores con confianza alta; no se cambiaron umbrales usando test.
