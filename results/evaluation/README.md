# Evaluación del detector en test

Resultados aportados por el usuario: 734 imágenes, 819 instancias, 0 imágenes sin anotaciones y 0 corruptas según la salida de evaluación. Modelo: entrenamientos/yolov9t_regularizacion/weights/best.pt. SHA256 de los pesos aún no registrado.

Precisión 98,6384 %; recall 97,9243 %; mAP50 99,4150 %; mAP50–95 89,3450 %. Son métricas del detector, no exactitud OCR ni aprobación de pólizas. Véase detector_test.json para valores exactos y configuración. La independencia de test requiere comprobar separación y duplicados con train/val.

La matriz adjunta muestra 816 coincidencias, 393 detecciones sin correspondencia y 3 anotaciones sin detección bajo sus criterios de filtrado/emparejamiento. No se deben combinar directamente esos conteos con la precisión y recall resumidos: corresponden a criterios/puntos de operación distintos. La corrida admitió detecciones con conf=0.001. El detalle de umbrales de la matriz debe comprobarse en la versión utilizada antes de interpretarla como rendimiento operacional.

La curva F1 indica aproximadamente 0.98 a confianza 0.466 en test. Es descriptiva: no se cambia el umbral de la aplicación a partir de test; el umbral operativo 0.60 sigue sin calibración y requiere evaluación en validación. El mAP resume un barrido de confianza; conf=0.001 no es recomendación de operación.

El test contiene 0 backgrounds según el escaneo; por tanto no permite caracterizar suficientemente falsas detecciones en imágenes completamente sin placas. Las demostraciones sin placa no sustituyen un conjunto negativo representativo.

La evaluación no se ejecutó en este entorno; se documenta la evidencia suministrada. Las curvas y matrices están en static/evaluation.
