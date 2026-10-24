# Estado de preparación de la entrega

Actualizado: **23 de octubre de 2026**. Esta lista distingue evidencias y
pendientes; no certifica una nota ni cumplimiento total. El historial anterior
se conserva en Git.

## Completado y publicado

| Componente | Evidencia y alcance |
|---|---|
| Repositorio público | `DanielGuevara25/Placas_OCR_ProyectoFinal`, rama `main`, verificado el 23/10 |
| Organización | `src/`, `app/`, `data/`, `models/`, `notebooks/`, `tests/`, `results/` y documentos |
| Licencia | AGPL-3.0-only para aportes propios, autorización del equipo y atribuciones |
| Documentación | Los seis documentos existen; estados actualizados el 23/10 |
| Dataset y EDA | 7.332 imágenes, 8.208 cajas, seis gráficos individuales y límites de procedencia |
| Modelos | Tres pesos publicados; descarga pública verificada con SHA256 el 21/10; hashes locales correctos el 23/10 |
| Notebooks | Cinco ejecutados, válidos, sin celdas pendientes ni errores guardados en la revisión del 23/10 |
| Pruebas | 16 unitarias aprobadas el 23/10; tres casos con modelos reales comprobados previamente |
| Evaluación | Métricas históricas del detector y evaluación OCR separada, con sus límites |
| Semana 5 | 60 ensayos procesados (17 completos, 43 podados), importancia/PDP, dos ajustes de 100 épocas y nueve escenarios |
| Demo protegida | Waitress, contraseña, HTTPS vía Cloudflare, límites y limpieza periódica; prueba real por HTTPS el 21/10 |

La selección S5 coincide con la referencia: **no hubo mejora demostrada**.
Los gráficos exploratorios no sustituyen múltiples semillas ni evaluación
independiente. Test quedó fuera de búsqueda. Ver [resultados S5](resultados_semana5.md).

## Acceso actual de la interfaz

La demo se preparó y verificó, pero **no estaba activa el 23/10**: el hostname
anterior no respondió y no se encontró `cloudflared` ejecutándose. Es un
pendiente operativo, no un despliegue nuevo por diseñar.

Para evaluar, reabrir servidor y túnel, comprobar desde otra red y comunicar
al profesor la URL vigente y las credenciales por separado. La PC debe estar
encendida, conectada y sin suspensión. No publicar la contraseña en GitHub.
Ver [demo temporal](demo_temporal.md) y [manual](manual_usuario.md).

`web_app.py` sirve para uso local en puerto 8080. La demo usa
`tools/servidor_demo.py` y Waitress en `127.0.0.1:8081`. No se ha contratado
alojamiento independiente; el PDF no exige pagar un servicio.

## Pendientes obligatorios de presentación

1. Incorporar el pitch de máximo cinco minutos, con interfaz real, 2-3 casos,
   manejo de errores, resultados, ética y enlace/QR del proyecto.
2. Incorporar el video que responda las preguntas asignadas por el profesor,
   en orden y numeradas, con la duración y plazo indicados por él.
3. Añadir ambos enlaces reales al README y verificar permisos de acceso.
4. Confirmar plazos: aparecen en blanco en el PDF proporcionado.

No se aportaron videos verificables durante esta revisión. No se afirma que
no existan fuera de la carpeta del proyecto; falta incorporarlos a la entrega.

## Calidad y reproducibilidad por cerrar

- Revisar estilo PEP 8 y docstrings. Los tests no certifican estilo, seguridad
  ni corrección completa del código.
- Consolidar dependencias de demo y comprobar instalación desde un clon limpio
  en Linux. El entorno Windows CPU existente sí fue probado.
- Usar una rama para futuras correcciones y etiquetar una versión cuando esté
  lista. Hasta esta revisión se observó sólo `main` y ningún tag.
- Definir condiciones de acceso al dataset si se requiere reproducir el
  entrenamiento. Los datos laborales completos no están publicados ni tienen
  licencia abierta declarada; hay autorización académica y publicación
  confirmada por el autor. La demo puede usar los checkpoints publicados.
- Confirmar contribuciones técnicas individuales si se quieren detallar;
  los integrantes y sus roles organizativos ya están documentados.

## Entornos y modelos

La web usa `models/best.pt`, del entrenamiento histórico de regularización,
y OCR `cct-s-v2-global-model`. S5 no sustituyó el modelo de la aplicación.
La consola `main.py` tiene otro recorrido, con detector de open-image-models.

Inferencia y tests funcionan en `.venv-tests/`, Python 3.12.14 CPU; versiones
en `requirements-tested.txt`, con dependencias adicionales en
`requirements-demo.txt`. No usar el antiguo lanzador de `.venv/`: su intérprete
base falta. Para S5 se recuperó Python 3.11 por separado y se reutilizó PyTorch
2.7.1+cu128 en la RTX 5070 Ti. No se confunden los entornos CPU y CUDA.

## Equipo y fechas confirmadas

Daniel Guevara (Scrum Master) y Christian Guerra (Product Owner), ambos como
equipo de desarrollo. Coordinación por WhatsApp sin publicar números privados.
Datos: 16-18/09; inicio formal: 22/09; entrenamientos históricos: 29/09-01/10;
pruebas iniciales: 05-09/10; web: 10-13/10; estudio ampliado: 20-21/10/2026.

## Evidencias relacionadas

- [Contraste completo contra el PDF](contraste_final_2026_10_23.md).
- [Pruebas e integración](pruebas.md).
- [Publicación verificada](../results/reports/verificacion_github.json).
- [Planificación](planificacion.md), [arquitectura](arquitectura.md) y
  [consideraciones éticas](consideraciones_eticas.md).
