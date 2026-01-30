import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, jsonify, g


def create_access_token(identity, expires_minutes=None):
    secret = current_app.config.get('JWT_SECRET')
    if not secret:
        raise RuntimeError('JWT_SECRET not set in app config')

    alg = current_app.config.get('JWT_ALGORITHM', 'HS256')
    exp_min = expires_minutes or current_app.config.get('JWT_EXP_MINUTES', 60)
    now = datetime.utcnow()
    payload = {
        'sub': identity,
        'iat': now,
        'exp': now + timedelta(minutes=exp_min)
    }
    token = jwt.encode(payload, secret, algorithm=alg)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token


def decode_token(token):
    secret = current_app.config.get('JWT_SECRET')
    alg = current_app.config.get('JWT_ALGORITHM', 'HS256')
    try:
        payload = jwt.decode(token, secret, algorithms=[alg])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', None)
        token = None
        if auth and auth.lower().startswith('bearer '):
            token = auth.split(None, 1)[1].strip()
        else:
            token = request.cookies.get('access_token')

        if not token:
            return jsonify({'error': 'Authorization required'}), 401
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        g.current_user = payload.get('sub')
        return f(*args, **kwargs)
    return decorated


def verify_credentials(username, password):
    admin_user = current_app.config.get('ADMIN_USERNAME')
    admin_pass = current_app.config.get('ADMIN_PASSWORD')
    if admin_user is None or admin_pass is None:
        return False
    return username == admin_user and password == admin_pass


def login_and_get_token(username, password):
    if not verify_credentials(username, password):
        return None
    token = create_access_token(identity=username)
    return token