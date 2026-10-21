"""Crea los cinco notebooks del proyecto con análisis y evidencia existentes.

No ejecuta entrenamientos ni atribuye resultados históricos a esta ejecución.
"""
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]

SETUP = '''from pathlib import Path
import sys, json, csv, hashlib
from html import escape
from IPython.display import display, Markdown, HTML, Image

ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "src/paths.py").is_file())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))
def table(rows):
    if not rows:
        return display(Markdown("Sin filas."))
    keys = list(rows[0])
    head = "".join("<th>" + escape(str(k)) + "</th>" for k in keys)
    body = "".join("<tr>" + "".join("<td>" + escape(str(r.get(k, ""))) + "</td>" for k in keys) + "</tr>" for r in rows)
    display(HTML("<table><thead><tr>"+head+"</tr></thead><tbody>"+body+"</tbody></table>"))
print("Raíz del proyecto localizada. Se utilizan evidencias reales del repositorio.")
'''


def md(text):
    return nbf.v4.new_markdown_cell(text)


def code(text):
    return nbf.v4.new_code_cell(text)


def save(name, cells):
    nb = nbf.v4.new_notebook(cells=cells, metadata={
        'kernelspec': {'display_name': 'Python 3 (PlacaLab)', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python'},
    })
    nbf.validate(nb)
    path = ROOT / 'notebooks' / name
    nbf.write(nb, path)
    print(path.name)


def main():
    save('01_exploracion.ipynb', [
        md('# 01 · Exploración del dataset de placas\n\nAutores: Daniel Guevara y Christian Guerra. '
           'El modo predeterminado reproduce el análisis de las evidencias agregadas publicadas. '
           'No requiere descargar fotografías privadas ni estima atributos demográficos.'),
        code(SETUP),
        md('## Fuente y particiones\n\nCapturas del sistema laboral del autor, con autorización de uso '
           'académico y publicación declarada por el equipo. No se ha indicado una licencia abierta '
           'del dataset. Una clase: placa. La auditoría comprueba formato y duplicados exactos, '
           'no independencia por vehículo ni corrección visual de todas las cajas.'),
        code('eda = load("results/metrics/analisis_datos.json")\n'
             'table([{"partición": k, **v} for k,v in eda["splits"].items()])\n'
             'assert sum(v["images"] for v in eda["splits"].values()) == eda["total_images"]\n'
             'print("Total:",eda["total_images"],"imágenes y",eda["total_valid_boxes"],"cajas")'),
        md('## Seis visualizaciones EDA\n\nSon figuras generadas por `src.analizar_datos` desde las imágenes '
           'y etiquetas originales. Sus resultados se conservan para revisión desde una copia pública.'),
        code('for name in ["01_particiones.png", "02_placas_por_imagen.png", "03_resoluciones.png", '
             '"04_area_placas.png", "05_centros.png", "06_forma_placas.png"]:\n'
             '    display(Image(filename=str(ROOT / "results/figures/eda" / name), width=800))'),
        code('table([{"variable": k, **eda[k]} for k in ["image_width_px","image_height_px","box_area_pct","box_height_px"]])\n'
             'print("Cajas de alto <16 px (%):",round(100*eda["box_height_below_16_px"]/eda["total_valid_boxes"],2))\n'
             'print("Duplicados exactos:", eda["decoded_pixel_duplicates"])'),
        md('## Interpretación y límites\n\nNo existen negativos anotados; falta evaluar falsas detecciones '
           'en imágenes sin placa. Las cajas pequeñas pueden dificultar OCR, sin demostrar causalidad. '
           'El tamaño de las particiones no garantiza independencia por sesión/vehículo. '
           'Para regenerar toda la auditoría local, con el dataset disponible, ejecutar '
           '`python -m src.analizar_datos`; no altera las particiones.'),
    ])
    save('02_preprocesamiento.ipynb', [
        md('# 02 · Preprocesamiento y control de calidad\n\nSe documenta y comprueba el pipeline existente. '
           'No se generan nuevas anotaciones ni se sobrescribe el dataset al ejecutar este notebook.'),
        code(SETUP),
        md('## Preparación del detector\n\n`src.preparar_dataset` selecciona filas revisadas SI, '
           'valida cajas YOLO, agrupa por SHA256 de píxeles y divide grupos con semilla 42. '
           'No convierte archivos sin etiqueta en negativos. La auditoría publica sólo estadísticas.'),
        code('eda = load("results/metrics/analisis_datos.json")\n'
             'table([{"control":k,"resultado":eda[k]} for k in ["review_rows","review_marked_yes","excluded_rows","issue_count","manifest_group_crossings"]])\n'
             'from src.preparar_dataset import validar_etiqueta\n'
             'dataset = ROOT / "data/processed/dataset_placas"\n'
             'labels = sorted((dataset / "labels").rglob("*.txt")) if dataset.is_dir() else []\n'
             'if labels:\n'
             '    for path in labels:\n'
             '        validar_etiqueta(path)\n'
             '    print("Etiquetas locales validadas en esta ejecución:",len(labels))\n'
             'else:\n'
             '    print("Dataset no incluido en esta copia: se consulta auditoría guardada, sin fingir nueva validación.")'),
        md('## Preprocesamiento real de la web\n\nValidación de formato, límite de 12 MiB y 20 megapíxeles, '
           'orientación EXIF y RGB. El detector recibe BGR; el OCR vuelve a RGB y reescala a 128×64 '
           'con interpolación cúbica. No se implementan CLAHE ni sharpening.'),
        code('from app.web_service import decode_image\n'
             'import numpy as np\n'
             'photo = decode_image((ROOT/"app/static/examples/gca4771.png").read_bytes())\n'
             'rgb = np.asarray(photo)\n'
             'bgr = np.ascontiguousarray(rgb[:,:,::-1])\n'
             'assert np.array_equal(bgr[:,:,::-1],rgb)\n'
             'print("Dimensiones RGB reales:",rgb.shape,"; tipo:",rgb.dtype,"; conversión BGR reversible comprobada.")'),
        md('## Normalización de texto y datos faltantes\n\nSe eliminan espacios/guiones y se pasa a '
           'mayúsculas; no se sustituyen O/0 o I/1. Las lecturas ilegibles no reciben etiquetas inventadas.'),
        code('from app.web_validation import declared_plate\n'
             'table([{"entrada":s,"normalizada":declared_plate(s)} for s in ["gca-4771"," GTW 9311 ","ABO123","AB0123"]])\n'
             'assert declared_plate("ABO123") != declared_plate("AB0123")'),
        md('Los valores extremos se revisan, no se eliminan automáticamente. Una geometría válida '
           'no certifica la exactitud visual de las anotaciones. Véase `docs/analisis_datos.md`.'),
    ])
    save('03_modelado.ipynb', [
        md('# 03 · Modelado y entrenamiento\n\nEl entrenamiento histórico ya está realizado. '
           'Este notebook inspecciona sus configuraciones, pesos y curvas. Entrenar es opcional '
           'y está desactivado para no iniciar 100 épocas por accidente.'),
        code(SETUP),
        code('import yaml\n'
             'names=["yolov9t_baseline","yolov9t_regularizacion","yolov9t_rotacion"]\n'
             'configs={n:yaml.safe_load((ROOT/"results/training"/n/"args.yaml").read_text(encoding="utf-8")) for n in names}\n'
             'keys=["epochs","imgsz","batch","seed","optimizer","weight_decay","degrees"]\n'
             'table([{"experimento":n,**{k:configs[n][k] for k in keys}} for n in names])'),
        md('## Detector y OCR separados\n\nYOLOv9t entrenado para una clase; el OCR '
           '`cct-s-v2-global-model` es preentrenado y no se entrenó localmente. La web usa '
           'regularización y la consola tiene por defecto otro backend: no son métricas intercambiables.'),
        code('arch=load("results/reports/arquitectura_modelos.json")\n'
             'table([{k:v for k,v in arch["detector"].items() if k!="yaml"}])\n'
             'manifest=load("models/manifest.json")\n'
             'weight=ROOT/manifest["web_detector"]["path"]\n'
             'if weight.is_file():\n'
             '    assert hashlib.sha256(weight.read_bytes()).hexdigest()==manifest["web_detector"]["sha256"]\n'
             '    print("Checkpoint web verificado por SHA256.")\n'
             'else:\n'
             '    print("Descargar pesos según models/README.md antes de inferencia; no se afirma que estén cargados.")'),
        code('display(Image(filename=str(ROOT/"results/figures/comparacion_entrenamiento.png"),width=1000))'),
        md('## Reentrenamiento opcional\n\nRequiere dataset local, peso base, CUDA y el entorno de '
           'entrenamiento correspondiente. Los scripts impiden sobrescribir nombres existentes. '
           'No habilitar sin revisar rutas y presupuesto de ejecución.'),
        code('RUN_TRAINING=False\n'
             'if RUN_TRAINING:\n'
             '    import subprocess\n'
             '    subprocess.run([sys.executable,"-m","src.entrenar_placas"],cwd=ROOT,check=True)\n'
             'else:\n'
             '    print("No se realizó nuevo entrenamiento. Los registros corresponden a las corridas históricas.")'),
    ])
    save('04_optimizacion.ipynb', [
        md('# 04 · Optimización y contraste con Semana 5\n\nResultados reales disponibles de tres '
           'configuraciones. Este notebook no transforma 100 épocas en 100 ensayos independientes '
           'ni atribuye una búsqueda Optuna que no se ha realizado.'),
        code(SETUP),
        code('from src.comparar_experimentos import main as comparar\n'
             'comparar()\n'
             'report=load("results/metrics/comparacion_experimentos.json")\n'
             'table([{k:r[k] for k in ["experiment","weight_decay","degrees","best_logged_epoch","map50_95","improvement_over_baseline_pp"]} for r in report["experiments"]])'),
        code('display(Image(filename=str(ROOT/"results/figures/comparacion_modelos.png"),width=1000))'),
        md('## Interpretación\n\nLa regularización aumenta mAP50–95 de validación en 0,384 puntos '
           'porcentuales. Una corrida por configuración no establece significancia. La rotación '
           'reduce la brecha train/val en las épocas reevaluadas, sin obtener el máximo mAP50–95. '
           'No se utiliza test para seleccionar hiperparámetros.'),
        code('import itertools\n'
             'observed={(r["weight_decay"],r["degrees"]) for r in report["experiments"]}\n'
             'grid=set(itertools.product([0.0005,0.001],[0.0,5.0]))\n'
             'print("Combinaciones observadas:",sorted(observed))\n'
             'print("Combinación ausente:",sorted(grid-observed))\n'
             'print("No se ajusta un sustituto con tres observaciones ni se fabrican PDP/interacciones.")'),
        md('## Qué pide el material recibido\n\n`Semana5_Workshops_semana5 (1).ipynb` contiene '
           'estrés controlado y 60 ensayos Optuna en Random Forest, importancia, slice/contorno, '
           'dependencia parcial mediante un sustituto y evaluación final separada. '
           'Adaptar ese método al detector exige nuevos experimentos o un estudio de inferencia '
           'claramente separado del entrenamiento. Está pendiente; este notebook no cierra ese requisito. '
           'Véase `docs/semana5_brechas.md`.'),
    ])
    save('05_evaluacion.ipynb', [
        md('# 05 · Evaluación y análisis de errores\n\nSe distinguen evidencia histórica de test, '
           'OCR aislado y pruebas funcionales. La ejecución no vuelve a usar test para elegir parámetros.'),
        code(SETUP),
        code('det=load("results/evaluation/detector_test.json")\n'
             'table([{"métrica":k,"valor":v} for k,v in det["metrics"].items()])\n'
             'print("Muestra del detector:",det["images"],"imágenes y",det["instances"],"instancias")'),
        md('El registro histórico del detector no guardó hash del checkpoint. No se asigna '
           'retrospectivamente el hash actual a esa ejecución sin evidencia adicional.'),
        code('ocr=load("results/evaluation/metricas_ocr.json")\n'
             'assert abs(ocr["exactitud_placa"]-ocr["placas_exactas"]/ocr["placas_evaluables"])<1e-12\n'
             'assert abs(ocr["cer"]-ocr["errores_edicion"]/ocr["caracteres_referencia"])<1e-12\n'
             'table([{k:ocr[k] for k in ["total_recortes","placas_evaluables","placas_exactas","exactitud_placa","cer","cobertura_transcripcion"]}])'),
        code('with (ROOT/"results/evaluation/detalle_ocr.csv").open(encoding="utf-8-sig",newline="") as f:\n'
             '    rows=list(csv.DictReader(f))\n'
             'errors=[r for r in rows if r["estado_manual"]=="legible" and r["coincide"]=="False"]\n'
             'accepted=sum(float(r["confianza_media"])>=.85 and min(json.loads(r["confianzas_caracter"]))>=.60 for r in errors)\n'
             'print("Lecturas erróneas evaluables:",len(errors),"; superan ambas reglas de confianza:",accepted)\n'
             'print("No se muestran matrículas adicionales: la evidencia detallada está en el CSV autorizado.")'),
        md('## Pruebas funcionales actuales\n\nLos ejemplos comprueban integración, no precisión estadística.'),
        code('smoke=load("results/reports/prueba_integracion_real.json")\n'
             'table([{"caso":r["case"],"HTTP":r["http_status"],"estado":r["validation"]["status"],"esperado":r["matches_expected_status"]} for r in smoke["cases"]])\n'
             'assert smoke["all_expected_statuses_observed"]'),
        md('Para repetir integración con pesos reales: `python -m tests.smoke_real`. '
           'Para pruebas unitarias: `python -m unittest discover -s tests -v`. '
           'Ambas son distintas de volver a evaluar todo test. Las exclusiones OCR, '
           'ausencia de negativos y dependencia posible por vehículo siguen vigentes.'),
    ])


if __name__ == '__main__':
    main()
