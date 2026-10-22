# Demostración mediante túnel temporal

La aplicación se sirve con Waitress en `127.0.0.1:8081`, sin depuración.
Cloudflare Quick Tunnel publica únicamente ese servicio mediante HTTPS.
No se modifica el router ni se publica un puerto de la red local.
El hostname es temporal y cambia al reiniciar el túnel.

## Acceso y datos

Se requiere autenticación HTTP Basic en todas las rutas, incluidos archivos
estáticos y API. Usuario y contraseña exclusivos se guardan localmente en
`.model-cache/demo/acceso.json`, excluido de Git. No usar esas credenciales
en otros servicios ni incluirlas en capturas o videos públicos. Compartirlas
únicamente con los evaluadores previstos. La contraseña permite acceso a
la demo: no identifica individualmente a los miembros del equipo.

La demo admite seis análisis por minuto en total, una inferencia simultánea,
fotos de hasta 12 MB y 20 megapíxeles. Rechaza mutaciones desde otros orígenes
del navegador. Los cuatro resultados recientes permanecen en memoria como
máximo 15 minutos, con limpieza cada 30 segundos. No se archivan las fotos;
las bibliotecas HTTP pueden usar archivos temporales durante la transferencia.
El navegador del visitante también recibe y puede conservar sus resultados.

Las pruebas automatizadas de la revisión pasan (16 casos). La comprobación
por HTTPS observó 401 sin contraseña, 200 con contraseña y detección/OCR
correctos en un ejemplo conocido. Esto no demuestra disponibilidad continua
ni ausencia de vulnerabilidades. Evidencia operativa local, sin contraseña:
`.model-cache/demo/comprobacion_publica.json`.

## Arranque en Windows

Desde la raíz, después de instalar `requirements-demo.txt` en el entorno
de la aplicación y descargar `cloudflared` oficial, abrir dos terminales:

```powershell
.\.venv-tests\Scripts\python.exe tools/servidor_demo.py
```

```powershell
.\.model-cache\demo\cloudflared.exe tunnel --url http://127.0.0.1:8081 --protocol http2 --no-autoupdate
```

El primer comando requiere el archivo de acceso local ya preparado. Para
otra instalación se debe generar una contraseña aleatoria de al menos 16
caracteres y guardarla en ese archivo como JSON con `username` y `password`.
No copiar ese archivo al repositorio. Usar siempre el enlace HTTPS generado,
sin insertar la contraseña en la URL.

La PC y la conexión deben mantenerse activas. El túnel no ofrece garantías
de disponibilidad y no es alojamiento independiente. Fuente:
[Cloudflare Quick Tunnels](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/).

## Cierre

En las terminales de arranque, Ctrl+C detiene cada proceso. Para el arranque
asistido en segundo plano, ejecutar desde la raíz:

```powershell
powershell -NoProfile -File tools/cerrar_demo.ps1
```

El script identifica únicamente el ejecutable del túnel de este proyecto
y el servidor de la demo. Cerrar ambos procesos corta el enlace y libera
los resultados mantenidos en memoria. Las demás aplicaciones no se detienen.
