"""Prepara transcripción ciega usando cajas YOLO reales, sin ejecutar OCR."""
from src.paths import ROOT
import argparse
import csv
import html
import json
import math
import random
from pathlib import Path

from PIL import Image

EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
FIELDS = ['id', 'texto_real', 'estado', 'observaciones']


def read_boxes(label):
    boxes = []
    for line_number, line in enumerate(label.read_text(encoding='utf-8-sig').splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 5:
            raise ValueError(f'Etiqueta YOLO inválida: {label}, línea {line_number}')
        cls, x, y, w, h = map(float, parts)
        if not all(math.isfinite(v) for v in [cls, x, y, w, h]):
            raise ValueError(f'Etiqueta no finita: {label}')
        if cls != 0:
            continue
        if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < w <= 1 and 0 < h <= 1):
            raise ValueError(f'Coordenadas inválidas: {label}')
        boxes.append([x, y, w, h])
    return boxes


def prepare(dataset, output, count=50, seed=42):
    images = dataset / 'images' / 'test'
    labels = dataset / 'labels' / 'test'
    if not images.is_dir() or not labels.is_dir():
        raise ValueError('Faltan images/test o labels/test dentro del dataset.')
    candidates = sorted(p for p in images.iterdir() if p.suffix.lower() in EXTENSIONS)
    if count < 1 or count > len(candidates):
        raise ValueError(f'La muestra debe estar entre 1 y {len(candidates)} imágenes.')
    if output.exists() and any(output.iterdir()):
        raise ValueError('La carpeta de salida ya contiene archivos. Usa otra ruta para conservar tu revisión.')
    selected = random.Random(seed).sample(candidates, count)
    # Validar etiquetas antes de generar resultados; nunca usar nombres como texto real.
    annotations = []
    for photo in selected:
        label = labels / (photo.stem + '.txt')
        if not label.is_file():
            raise ValueError(f'Falta la etiqueta de una imagen seleccionada: {label}')
        annotations.append((photo, label, read_boxes(label)))
    output.mkdir(parents=True, exist_ok=True)
    (output / 'recortes').mkdir(exist_ok=True)
    (output / 'contexto').mkdir(exist_ok=True)
    manifest, records, cards = [], [], []
    for image_index, (photo, label, boxes) in enumerate(annotations, 1):
        with Image.open(photo) as source:
            source.load()
            rgb = source.convert('RGB')
        width, height = rgb.size
        context_name = f'imagen_{image_index:03d}.jpg'
        rgb.save(output / 'contexto' / context_name, quality=95)
        for box_index, (x, y, w, h) in enumerate(boxes, 1):
            coords = [max(0, math.floor((x-w/2)*width)), max(0, math.floor((y-h/2)*height)),
                      min(width, math.ceil((x+w/2)*width)), min(height, math.ceil((y+h/2)*height))]
            if coords[2] <= coords[0] or coords[3] <= coords[1]:
                raise ValueError(f'Caja vacía: {label}')
            item_id = f'placa_{len(records)+1:03d}'
            rgb.crop(tuple(coords)).save(output / 'recortes' / (item_id+'.png'))
            records.append(dict(id=item_id, texto_real='', estado='pendiente', observaciones=''))
            manifest.append(dict(id=item_id, imagen_origen=photo.name, etiqueta=label.name,
                                 indice_caja=box_index, bbox=coords, contexto=context_name))
            cards.append(f'''<article data-id="{item_id}"><h2>{item_id}</h2>
<img class="crop" src="recortes/{item_id}.png" alt="Recorte {item_id}">
<details><summary>Ver fotografía completa</summary><img class="context" src="contexto/{context_name}" alt="Contexto de {item_id}"><p>Si hay varias placas, usa el recorte de arriba para identificar cuál transcribir.</p></details>
<label>Texto verdadero <input class="truth" autocomplete="off" spellcheck="false" maxlength="40"></label>
<label>Estado <select class="state"><option value="pendiente">Pendiente</option><option value="legible">Legible y revisada</option><option value="ilegible">Ilegible</option><option value="caja_incorrecta">Caja incorrecta</option></select></label>
<label>Observaciones <input class="notes" maxlength="300"></label></article>''')
    with (output / 'transcripciones.csv').open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)
    metadata = dict(seed=seed, sample_images=count, sample_plates=len(records),
                    total_test_images=len(candidates), selection='Muestreo aleatorio simple de imágenes; todas sus cajas clase 0.',
                    source='Cajas anotadas de test; no detector, no OCR, no etiquetas de texto inferidas del nombre.',
                    records=manifest)
    (output / 'manifest_privado.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    page = PAGE.replace('<!--CARDS-->', '\n'.join(cards)).replace('<!--COUNT-->', str(len(records)))
    (output / 'revision.html').write_text(page, encoding='utf-8')
    print(f'Preparadas {count} imágenes y {len(records)} recortes.')
    print(f'Abre en tu navegador: {(output / "revision.html").resolve()}')
    print('Al terminar pulsa Descargar transcripciones. Guarda también manifest_privado.json.')


PAGE = '''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Revisión manual de placas</title>
<style>:root{color-scheme:dark}body{background:#17191e;color:#edf0f4;font:16px Segoe UI,Arial;margin:25px auto;padding:0 20px;max-width:1100px}p{line-height:1.7;color:#bac2cc}.toolbar{position:sticky;top:0;background:#17191ef5;padding:14px 0;z-index:1}button{padding:12px;border-radius:8px;background:#315849;color:#fff;border:1px solid #82b8a0;cursor:pointer}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(285px,1fr));gap:18px}article{background:#252930;padding:18px;border:1px solid #444c59;border-radius:10px}h2{font-size:18px}.crop{width:100%;height:150px;object-fit:contain;background:#111}.context{width:100%;height:auto}label{display:block;margin-top:14px}input,select{box-sizing:border-box;width:100%;padding:10px;margin-top:6px;font:inherit;background:#1a1d22;color:#fff;border:1px solid #66717e;border-radius:5px}.truth{text-transform:uppercase}summary{cursor:pointer;margin:12px 0}#status{color:#edca85}</style>
<h1>Transcripción manual para evaluar OCR</h1><p>Hay <!--COUNT--> placas. Lee la imagen, escribe el texto real y marca su estado. No consultes nombres originales ni predicciones OCR. Conserva ceros y letras tal como se ven; no adivines caracteres. Si no se puede leer, marca Ilegible. Si la caja no encierra una placa, marca Caja incorrecta.</p>
<div class="toolbar"><button id="save" type="button">Descargar transcripciones</button> <label>Continuar revisión desde un CSV descargado <input id="restore" type="file" accept=".csv"></label><p id="status" role="status">Descarga avances con frecuencia. Cerrar o recargar esta página descarta cambios que no hayas descargado.</p></div>
<div class="grid"><!--CARDS--></div><script>
const cards=Array.from(document.querySelectorAll('article'));
const fields=['id','texto_real','estado','observaciones'];
function parseCSV(text){const rows=[];let row=[],field='',quoted=false;for(let i=0;i<text.length;i++){let c=text[i];if(c==='"'){if(quoted&&text[i+1]==='"'){field+='"';i++;}else quoted=!quoted;}else if(c===','&&!quoted){row.push(field);field='';}else if((c==='\\n'||c==='\\r')&&!quoted){if(c==='\\r'&&text[i+1]==='\\n')i++;row.push(field);if(row.some(v=>v!==''))rows.push(row);row=[];field='';}else field+=c;}if(quoted)throw Error('CSV con comillas sin cerrar');if(field||row.length){row.push(field);rows.push(row);}return rows;}
document.getElementById('save').onclick=()=>{for(const card of cards){const state=card.querySelector('.state').value;const truth=card.querySelector('.truth').value.trim();if(state==='legible'&&!/^[A-Z0-9]{2,12}$/.test(truth.toUpperCase().replace(/[\\s-]+/g,''))){document.getElementById('status').textContent='Revisa el texto de '+card.dataset.id;card.querySelector('.truth').focus();return;}}
const quote=v=>'"'+String(v).replace(/"/g,'""')+'"';const rows=[fields,...cards.map(c=>[c.dataset.id,c.querySelector('.truth').value.trim().toUpperCase(),c.querySelector('.state').value,c.querySelector('.notes').value])];const csv='\\ufeff'+rows.map(r=>r.map(quote).join(',')).join('\\r\\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='transcripciones_revisadas.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);document.getElementById('status').textContent='Descarga generada: comprueba que el archivo se guardó. Puedes importar ese CSV para continuar.';};
document.getElementById('restore').onchange=async e=>{try{const file=e.target.files[0];if(!file)return;const rows=parseCSV((await file.text()).replace(/^\\ufeff/,''));if(JSON.stringify(rows.shift())!==JSON.stringify(fields))throw Error('Columnas de CSV incorrectas');const map=new Map(rows.map(r=>[r[0],r]));if(map.size!==cards.length||cards.some(c=>!map.has(c.dataset.id)))throw Error('El CSV no corresponde a esta muestra');for(const c of cards){const r=map.get(c.dataset.id);if(r.length!==4||!['pendiente','legible','ilegible','caja_incorrecta'].includes(r[2]))throw Error('Fila inválida');}for(const c of cards){const r=map.get(c.dataset.id);c.querySelector('.truth').value=r[1];c.querySelector('.state').value=r[2];c.querySelector('.notes').value=r[3];}document.getElementById('status').textContent='Revisión restaurada desde CSV.';}catch(err){document.getElementById('status').textContent=err.message;}};
</script></html>'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, default=ROOT / 'data/processed/dataset_placas')
    parser.add_argument('--output', type=Path, default=ROOT / 'data/review/revision_ocr_test')
    parser.add_argument('--n', type=int, default=50)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    try:
        prepare(args.dataset, args.output, args.n, args.seed)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'No se pudo preparar la revisión: {exc}\n')
