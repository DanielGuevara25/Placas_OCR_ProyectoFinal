"""Integridad de descargas sin tráfico real ni sobrescritura de pesos."""
import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.descargar_modelos import download_verified


class DownloadTests(unittest.TestCase):
    def test_verified_download(self):
        data = b'checkpoint-de-prueba'
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'model.pt'
            with patch('urllib.request.urlopen', return_value=io.BytesIO(data)):
                result = download_verified('https://example.test/model.pt', target,
                                           hashlib.sha256(data).hexdigest(), len(data))
            self.assertEqual(result, 'downloaded_and_verified')
            self.assertEqual(target.read_bytes(), data)

    def test_bad_hash_preserves_existing_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'model.pt'
            target.write_bytes(b'original')
            with patch('urllib.request.urlopen', return_value=io.BytesIO(b'wrong')):
                with self.assertRaises(ValueError):
                    download_verified('https://example.test/model.pt', target, '0' * 64, 5)
            self.assertEqual(target.read_bytes(), b'original')
            self.assertEqual(list(Path(folder).glob('*.download')), [])

    def test_verified_local_file_needs_no_network(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'model.pt'
            target.write_bytes(b'valid')
            with patch('urllib.request.urlopen') as network:
                result = download_verified('https://example.test/model.pt', target,
                                           hashlib.sha256(b'valid').hexdigest(), 5)
            network.assert_not_called()
            self.assertEqual(result, 'already_verified')
