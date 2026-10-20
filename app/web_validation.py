"""Comparación de placa para apoyo a inspección; no autoriza pólizas."""
import re
import base64
import io
import json
import zipfile

OCR_MEAN_MIN = .85
OCR_CHARACTER_MIN = .60

def normalize_plate(value):
    return re.sub(r'[\s-]+', '', value.upper())

def declared_plate(value):
    if not isinstance(value,str) or len(value)>40:
        raise ValueError('Ingresa una placa declarada válida.')
    normalized=normalize_plate(value)
    if not re.fullmatch(r'[A-Z0-9]{2,12}',normalized):
        raise ValueError('La placa debe contener de 2 a 12 letras o números; puedes usar espacios y guiones.')
    return normalized

def assess_plate(row, declared):
    text=normalize_plate(row['plate_text'])
    probs=row['character_confidences']
    mean=row['ocr_mean_confidence']
    match=bool(text) and text==declared
    reliable=(row['ocr_status']=='read' and re.fullmatch(r'[A-Z0-9]{2,12}',text)
              and probs and mean is not None and mean>=OCR_MEAN_MIN and min(probs)>=OCR_CHARACTER_MIN)
    if not reliable:
        status='revision_manual';message='Lectura vacía, fallida o dudosa. Revisa el recorte y solicita otra foto si hace falta.'
    elif match:
        status='coincide';message='La lectura OCR coincide con la placa declarada. Se registra solo coincidencia de placa.'
    else:
        status='inconsistencia';message='La lectura OCR no coincide con la placa declarada. Requiere revisión manual; no implica fraude.'
    return {'status':status,'message':message,'normalized_reading':text,'text_matches':match,
            'manual_review_required':status!='coincide'}

def apply_validation(result,declared,selected_id=None):
    rows=result['plates']
    for row in rows:row['validation']=assess_plate(row,declared)
    if selected_id is not None and selected_id not in [row['id'] for row in rows]:
        raise ValueError('Selecciona una placa detectada válida.')
    if len(rows)==1:selected_id=rows[0]['id']
    if not rows:
        summary={'status':'sin_placa','message':'No se detectó una placa. Solicita otra fotografía del vehículo.', 'manual_review_required':True}
    elif selected_id is None:
        summary={'status':'seleccion_pendiente','message':'Hay varias placas. Selecciona la del vehículo inspeccionado antes de comparar.', 'manual_review_required':True}
    else:summary=dict(next(row['validation'] for row in rows if row['id']==selected_id))
    result['validation']={**summary,'declared_plate':declared,'selected_plate_id':selected_id,
        'selection_method':'automatic_single' if len(rows)==1 else ('manual' if selected_id else None),
        'ocr_mean_min':OCR_MEAN_MIN,'ocr_character_min':OCR_CHARACTER_MIN,
        'scope':'Apoyo a validación de placa; no valida documentos, identidad completa del vehículo ni aprueba pólizas.',
        'threshold_note':'Umbrales iniciales de revisión no calibrados; deben validarse con lecturas verdaderas.'}

def rebuild_zip(payload):
    archive=io.BytesIO()
    def bytes_from_url(value):return base64.b64decode(value.split(',',1)[1])
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('foto_anotada.jpg',bytes_from_url(payload['annotated_image']))
        z.writestr('resultados.json',json.dumps(payload['result'],ensure_ascii=False,indent=2))
        for row,crop in zip(payload['result']['plates'],payload['crops']):z.writestr(row['crop_file'],bytes_from_url(crop))
    payload['download_zip']=base64.b64encode(archive.getvalue()).decode('ascii')
