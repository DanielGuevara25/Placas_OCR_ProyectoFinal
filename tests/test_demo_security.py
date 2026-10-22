import base64
import unittest

from flask import Flask, jsonify
from app.demo_security import install_demo_access


class DemoSecurityTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        install_demo_access(self.app, 'clave-exclusiva-demo-123', 'equipo')
        self.app.add_url_rule('/', endpoint='home', view_func=lambda: 'demo')
        self.app.add_url_rule('/api/detect', endpoint='detect', view_func=lambda: jsonify(ok=True), methods=['POST'])
        self.client = self.app.test_client()
        self.auth = {'Authorization': 'Basic '+base64.b64encode(b'equipo:clave-exclusiva-demo-123').decode()}

    def test_private_access_and_no_embedding(self):
        self.assertEqual(self.client.get('/').status_code, 401)
        self.assertEqual(self.client.get('/', headers={'Authorization':'Basic invalid'}).status_code, 401)
        response = self.client.get('/', headers=self.auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['X-Frame-Options'], 'DENY')

    def test_cross_origin_rejected_and_slot_released(self):
        self.assertEqual(self.client.post('/api/detect',headers={**self.auth,'Origin':'https://otro.example'}).status_code,403)
        for _ in range(6):
            self.assertEqual(self.client.post('/api/detect', headers=self.auth).status_code,200)
        self.assertEqual(self.client.post('/api/detect', headers=self.auth).status_code,429)

    def test_weak_configuration_rejected(self):
        with self.assertRaises(ValueError):
            install_demo_access(Flask('bad'), 'corta')


if __name__ == '__main__':
    unittest.main()
