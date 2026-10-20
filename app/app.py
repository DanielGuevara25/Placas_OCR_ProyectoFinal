"""Ejecutar en la raíz de placas_ocr: python web_app.py"""
from src.paths import ROOT
import argparse
import logging
import math
import copy
import secrets
import threading
import time
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename
from app.web_validation import declared_plate, apply_validation, rebuild_zip
from app.web_service import ImageError, ModelsError, PlateService, WebSettings, decode_image

def create_app(service=None,settings=None):
    app=Flask(__name__)
    app.config['MAX_CONTENT_LENGTH']=12*1024*1024+128*1024
    settings=settings or WebSettings(ROOT / 'models/best.pt')
    service=service or PlateService(settings)
    # Cuatro análisis, quince minutos en memoria; sin almacenamiento en disco.
    jobs={}
    jobs_lock=threading.Lock()
    def prune():
        now=time.monotonic()
        for key in list(jobs):
            if now-jobs[key][0]>900:del jobs[key]
    @app.get('/')
    def home():return render_template('index.html')
    @app.get('/api/status')
    def status():return jsonify(service.status())
    @app.post('/api/detect')
    def detect():
        file=request.files.get('image')
        if file is None or not file.filename:return jsonify(error='Selecciona una foto antes de analizar.'),400
        try:
            confidence=float(request.form.get('confidence',settings.default_confidence))
            if not math.isfinite(confidence) or not .1<=confidence<=.95:raise ValueError
        except (ValueError,TypeError):return jsonify(error='La confianza debe estar entre 0.10 y 0.95.'),400
        try:declared=declared_plate(request.form.get('declared_plate',''))
        except ValueError as exc:return jsonify(error=str(exc)),400
        data=file.read(12*1024*1024+1)
        if len(data)>12*1024*1024:return jsonify(error='La foto supera 12 MB.'),413
        try:
            photo=decode_image(data)
            name=secure_filename(file.filename) or 'foto'
            payload=service.process(photo,name,confidence)
            apply_validation(payload['result'],declared)
            rebuild_zip(payload)
            job_id=secrets.token_urlsafe(24)
            payload['job_id']=job_id
            with jobs_lock:
                prune()
                while len(jobs)>=4:del jobs[next(iter(jobs))]
                jobs[job_id]=(time.monotonic(),payload)
            return jsonify(payload)
        except ImageError as exc:return jsonify(error=str(exc)),400
        except ModelsError as exc:return jsonify(error=str(exc)),503
        except Exception:
            app.logger.exception('Fallo de inferencia')
            return jsonify(error='No se pudo analizar la foto. Revisa la consola para ver el detalle.'),500
    @app.post('/api/select')
    def select():
        data=request.get_json(silent=True)
        if not isinstance(data,dict):return jsonify(error='Solicitud inválida.'),400
        job_id=data.get('job_id'); selected=data.get('selected_plate_id')
        if not isinstance(job_id,str) or type(selected) is not int:return jsonify(error='Selecciona una placa válida.'),400
        with jobs_lock:
            prune()
            if job_id not in jobs:return jsonify(error='El análisis expiró. Vuelve a analizar la foto.'),410
            payload=copy.deepcopy(jobs[job_id][1])
            try:apply_validation(payload['result'],payload['result']['validation']['declared_plate'],selected)
            except ValueError as exc:return jsonify(error=str(exc)),400
            rebuild_zip(payload)
            jobs[job_id]=(jobs[job_id][0],payload)
        return jsonify(payload)
    @app.errorhandler(413)
    def too_large(error):return jsonify(error='La foto supera el límite de 12 MB.'),413
    @app.after_request
    def headers(response):
        response.headers['Cache-Control']='no-store'
        response.headers['X-Content-Type-Options']='nosniff'
        return response
    return app

def main():
    logging.basicConfig(level=logging.INFO)
    parser=argparse.ArgumentParser(description='Página local para detectar placas y ejecutar OCR.')
    parser.add_argument('--weights',type=Path,default=ROOT / 'models/best.pt')
    parser.add_argument('--device',choices=['auto','cpu','0'],default='auto')
    parser.add_argument('--port',type=int,default=8080)
    args=parser.parse_args()
    settings=WebSettings(args.weights.resolve(),args.device)
    print(f'Abre http://127.0.0.1:{args.port} en tu navegador.',flush=True)
    create_app(settings=settings).run(host='127.0.0.1',port=args.port,debug=False,use_reloader=False,threaded=True)


if __name__ == '__main__':
    main()
