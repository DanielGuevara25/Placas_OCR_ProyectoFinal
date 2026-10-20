# Detección de placas y OCR

Extraído de plate_system.rar. Se conservan plate_detector.py, ocr_engine.py y providers.py. Se sustituye la configuración por una versión mínima y se incorpora un ejecutable para fotografías. No incluye detector de vehículos, tracking, votación temporal ni monitoreo.

## Modelos

- Activo: `yolo-v9-t-640-license-plate-end2end`, provisto por open-image-models.
- OCR: `cct-s-v2-global-model`, provisto por fast-plate-ocr.
- Alternativo local: `weights/best.pt`, copiado sin modificar del archivo original. No se ha verificado aquí la arquitectura ni precisión de este checkpoint.

El RAR no contiene los pesos ONNX del detector activo ni los pesos del OCR. Las librerías los descargan en la primera inicialización; ese primer uso necesita Internet. No confundir best.pt con el detector YOLOv9 activo. Los demás checkpoints quedan en el RAR original.

## Ejecutar desde VS Code en Windows

Desde la carpeta extraída, en PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py --input "C:\ruta\foto.jpg"
```

Para una carpeta:

```powershell
.\.venv\Scripts\python.exe main.py --input "C:\ruta\imagenes" --output resultados
```

CPU es el valor predeterminado para facilitar la primera prueba. Para CUDA necesitas instalar y verificar ONNX Runtime GPU y sus dependencias compatibles. Luego usa `--device cuda`. Para best.pt instala Ultralytics y PyTorch compatibles y usa `--backend yolo`. Si ya tienes un entorno que ejecuta el sistema original, úsalo y conserva sus versiones instaladas.

Salidas: fotografía con cajas/texto, recortes de placas y resultados.json con texto, confianza de detección, confianza por carácter, promedio OCR y latencia de inferencia (sin carga de modelos). El promedio OCR es descriptivo; no es una probabilidad calibrada de que toda la matrícula sea correcta.

## Verificación y actividad de semana 3

Se verificó sintaxis y extracción de pesos; no se ejecutó inferencia real porque aquí no se dispone del entorno de modelos ni imágenes de ejemplo. Esta entrega aísla la inferencia y NO genera curvas de entrenamiento. Para el diagnóstico de overfitting se necesitan dataset etiquetado, particiones y un detector entrenable; el ONNX de inferencia no sustituye al entrenamiento. El RAR recibido no contiene dataset, etiquetas ni historial de métricas.

Fuentes de API: https://github.com/ankandrew/open-image-models y https://github.com/ankandrew/fast-plate-ocr
