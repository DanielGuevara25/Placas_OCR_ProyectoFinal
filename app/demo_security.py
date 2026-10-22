"""Controles opcionales para la demo temporal, activados con DEMO_PASSWORD."""
from collections import deque
import hmac
import threading
import time
from urllib.parse import urlsplit

from flask import g, jsonify, request


def install_demo_access(app, password, username='equipo'):
    if not password or len(password) < 16:
        raise ValueError('La contraseña de demostración debe tener al menos 16 caracteres.')
    limits = {'all': (180, 60), 'detect': (6, 60), 'failed_login': (30, 60)}
    events = {name: deque() for name in limits}
    lock = threading.Lock()
    inference = threading.BoundedSemaphore(1)

    def allow(name):
        count, period = limits[name]
        now = time.monotonic()
        with lock:
            queue = events[name]
            while queue and queue[0] <= now-period:
                queue.popleft()
            if len(queue) >= count:
                return False
            queue.append(now)
            return True

    def busy(message, delay=60):
        response = jsonify(error=message)
        response.status_code = 429
        response.headers['Retry-After'] = str(delay)
        return response

    @app.before_request
    def guard():
        auth = request.authorization
        valid = auth is not None and auth.type.lower() == 'basic'
        if valid:
            valid = hmac.compare_digest((auth.username or '').encode(), username.encode())
            valid &= hmac.compare_digest((auth.password or '').encode(), password.encode())
        if not valid:
            if not allow('failed_login'):
                return busy('Demasiados intentos. Espera un minuto.')
            response = jsonify(error='Introduce el usuario y la contraseña de la demostración.')
            response.status_code = 401
            response.headers['WWW-Authenticate'] = 'Basic realm="PlacaLab demo", charset="UTF-8"'
            return response
        if not allow('all'):
            return busy('Límite temporal de solicitudes. Espera un minuto.')
        if request.method in {'POST', 'PUT', 'PATCH', 'DELETE'}:
            origin = request.headers.get('Origin')
            if request.headers.get('Sec-Fetch-Site') == 'cross-site' or (
                origin and urlsplit(origin).netloc != request.host
            ):
                return jsonify(error='Solicitud desde un origen no permitido.'), 403
        if request.path == '/api/detect' and request.method == 'POST':
            if not allow('detect'):
                return busy('La demo admite seis análisis por minuto en total.')
            if not inference.acquire(blocking=False):
                return busy('Hay otro análisis en curso. Vuelve a intentarlo.', 3)
            g.demo_inference_acquired = True

    @app.teardown_request
    def release(error):
        if g.pop('demo_inference_acquired', False):
            inference.release()

    @app.after_request
    def headers(response):
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'none'; object-src 'none'; base-uri 'self'"
        response.headers['X-Robots-Tag'] = 'noindex, nofollow, noarchive'
        return response
