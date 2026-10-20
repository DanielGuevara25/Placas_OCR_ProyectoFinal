import base64
import io
import json
import unittest
import zipfile
import numpy as np
import test_web
from app.web_validation import declared_plate, assess_plate

class ValidationTests(unittest.TestCase):
    setUp = test_web.WebTests.setUp
    upload = test_web.WebTests.upload
    def test_selection_and_exports(self):
        self.ocr.read=lambda crop:(list('GSA1234'),[.95]*7)
        data=self.upload().get_json()
        self.assertEqual(data['result']['validation']['status'],'seleccion_pendiente')
        response=self.client.post('/api/select',json={'job_id':data['job_id'],'selected_plate_id':2})
        self.assertEqual(response.status_code,200)
        updated=response.get_json()
        self.assertEqual(updated['result']['validation']['status'],'coincide')
        self.assertEqual(updated['result']['validation']['selection_method'],'manual')
        self.assertEqual(self.detector.calls,1)
        with zipfile.ZipFile(io.BytesIO(base64.b64decode(updated['download_zip']))) as z:
            report=json.loads(z.read('resultados.json'))
            self.assertEqual(report['validation']['selected_plate_id'],2)
            self.assertEqual(report,updated['result'])
        self.assertEqual(self.client.post('/api/select',json={'job_id':data['job_id'],'selected_plate_id':9}).status_code,400)
        self.assertEqual(self.client.post('/api/select',json={'job_id':'expired','selected_plate_id':1}).status_code,410)

    def test_single_plate_and_mismatch(self):
        self.detector.detect=lambda frame:np.array([[0,0,50,35,.95,0]])
        self.ocr.read=lambda crop:(list('GSA1234'),[.95]*7)
        report=self.upload(declared_plate=' gsa -1234 ').get_json()['result']
        self.assertEqual(report['validation']['status'],'coincide')
        self.assertEqual(report['validation']['selection_method'],'automatic_single')
        report=self.upload(declared_plate='ABC1234').get_json()['result']
        self.assertEqual(report['validation']['status'],'inconsistencia')
        self.assertTrue(report['validation']['manual_review_required'])

    def test_uncertain_even_matching_and_no_plates(self):
        self.detector.detect=lambda frame:np.array([[0,0,50,35,.95,0]])
        self.ocr.read=lambda crop:(list('GSA1234'),[.95]*6+[.4])
        report=self.upload().get_json()['result']
        self.assertEqual(report['validation']['status'],'revision_manual')
        self.assertTrue(report['validation']['text_matches'])
        self.detector.detect=lambda frame:np.empty((0,6))
        self.assertEqual(self.upload().get_json()['result']['validation']['status'],'sin_placa')

    def test_declared_validation(self):
        for value in ['', 'ABC@123', 'A', 'A'*13, 'ÁBC123']:
            self.assertEqual(self.upload(declared_plate=value).status_code,400)
        self.assertEqual(declared_plate(' abc - 123 '),'ABC123')
        self.assertNotEqual(declared_plate('ABO123'),declared_plate('AB0123'))

if __name__=='__main__':unittest.main()
