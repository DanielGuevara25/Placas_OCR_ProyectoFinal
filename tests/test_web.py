import base64
import io
import json
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from PIL import Image
from app.app import create_app
from app.web_service import PlateService, WebSettings, decode_image, ImageError, ModelsError

def photo_bytes():
    stream=io.BytesIO();Image.new('RGB',(120,80),(255,0,0)).save(stream,'PNG');return stream.getvalue()

class Detector:
    def __init__(self):self.cfg=SimpleNamespace(det_conf=.6);self.calls=0
    def detect(self,frame):
        self.calls+=1
        # BGR original rojo: [0,0,255].
        assert tuple(frame[0,0])==(0,0,255)
        return np.array([[-5,-2,50,35,.94,0],[60,40,140,95,.86,0],[4,4,4,8,.9,0],[2,2,15,15,.9,1]],dtype=float)

class OCR:
    def __init__(self):self.calls=0
    def read(self,crop):
        self.calls+=1
        if self.calls==2:raise RuntimeError('Simula falla OCR')
        return list('GSA1234'),[.9]*7

class WebTests(unittest.TestCase):
    def setUp(self):
        self.detector=Detector();self.ocr=OCR();self.loads=0
        def factory(settings):self.loads+=1;return self.detector,self.ocr,'cpu'
        self.service=PlateService(WebSettings(Path('best.pt')),factory)
        self.client=create_app(service=self.service).test_client()

    def upload(self,**kwargs):
        data={'image':(io.BytesIO(photo_bytes()),'foto.png'),'confidence':'.6','declared_plate':'GSA-1234'};data.update(kwargs)
        return self.client.post('/api/detect',data=data,content_type='multipart/form-data')

    def test_multi_plate_clamping_ocr_error_and_zip(self):
        response=self.upload();self.assertEqual(response.status_code,200)
        data=response.get_json();rows=data['result']['plates'];self.assertEqual(len(rows),2)
        self.assertEqual(rows[0]['bbox'],[0,0,50,35]);self.assertEqual(rows[1]['bbox'],[60,40,120,80])
        self.assertEqual(rows[0]['plate_text'],'GSA1234');self.assertEqual(rows[1]['ocr_status'],'error')
        with zipfile.ZipFile(io.BytesIO(base64.b64decode(data['download_zip']))) as z:
            self.assertEqual(set(z.namelist()),{'foto_anotada.jpg','resultados.json','placa_001.png','placa_002.png'})
            self.assertEqual(json.loads(z.read('resultados.json'))['plates'][0]['plate_text'],'GSA1234')

    def test_cache_and_threshold(self):
        self.upload();self.upload(confidence='.75')
        self.assertEqual(self.loads,1);self.assertEqual(self.detector.cfg.det_conf,.75)

    def test_invalid_image_and_threshold(self):
        response=self.client.post('/api/detect',data={'image':(io.BytesIO(b'bad'),'fake.jpg')})
        self.assertEqual(response.status_code,400)
        for value in ['nan','inf','.99','abc']:
            self.assertEqual(self.upload(confidence=value).status_code,400)
        self.assertEqual(self.client.post('/api/detect').status_code,400)

    def test_no_plates_is_valid(self):
        self.detector.detect=lambda frame:np.empty((0,6))
        self.assertEqual(self.upload().get_json()['result']['plates'],[])

    def test_missing_model_error(self):
        def factory(settings):raise ModelsError('Falta modelo')
        app=create_app(service=PlateService(WebSettings(Path('missing.pt')),factory))
        r=app.test_client().post('/api/detect',data={'image':(io.BytesIO(photo_bytes()),'foto.png'),'declared_plate':'GSA1234'})
        self.assertEqual(r.status_code,503);self.assertEqual(r.get_json()['error'],'Falta modelo')

    def test_home_and_static(self):
        self.assertEqual(self.client.get('/').status_code,200)
        for path in ['/static/app.js','/static/styles.css']:
            with self.client.get(path) as response:self.assertEqual(response.status_code,200)

if __name__=='__main__':unittest.main()
