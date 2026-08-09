import hashlib
import hmac
import json
import os
import re
import unicodedata
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, parse_qsl, urlparse

from pymongo import MongoClient


ROOT = Path(__file__).resolve().parent.parent
EVENTS_PATH = ROOT / 'fatoshist' / 'data' / 'eventos.json'
MAX_AUTH_AGE_SECONDS = 86400
ALLOWED_TOPICS = {'brasil', 'guerras', 'politica', 'ciencia', 'mulheres', 'civilizacoes', 'geral'}
ALLOWED_FREQUENCIES = {'daily', 'weekly'}
ALLOWED_HOURS = {8, 12, 18, 21}
_events_cache = None
_mongo_client = None


def _events():
    global _events_cache
    if _events_cache is None:
        with EVENTS_PATH.open(encoding='utf-8') as file:
            _events_cache = json.load(file)
    return _events_cache


def _plain(text):
    return re.sub(r'<[^>]+>', '', text).replace('•', '').strip()


def _normalized(text):
    value = unicodedata.normalize('NFKD', text.casefold())
    return ''.join(char for char in value if not unicodedata.combining(char))


def validate_telegram_init_data(init_data, bot_token=None, max_age=MAX_AUTH_AGE_SECONDS, now=None):
    """Valida a assinatura HMAC conforme a especificação oficial de Mini Apps."""
    if not init_data:
        raise ValueError('initData ausente')
    token = bot_token or os.environ.get('BOT_TOKEN', '')
    if not token:
        raise RuntimeError('BOT_TOKEN não configurado')

    values = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = values.pop('hash', '')
    if not received_hash:
        raise ValueError('hash ausente')
    data_check = '\n'.join(f'{key}={values[key]}' for key in sorted(values))
    secret = hmac.new(b'WebAppData', token.encode(), hashlib.sha256).digest()
    expected = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, received_hash):
        raise ValueError('assinatura inválida')

    auth_date = int(values.get('auth_date', '0'))
    current = int((now or datetime.now(timezone.utc)).timestamp())
    if auth_date <= 0 or current - auth_date > max_age or auth_date > current + 30:
        raise ValueError('sessão expirada')
    try:
        user = json.loads(values.get('user', '{}'))
    except json.JSONDecodeError as exc:
        raise ValueError('usuário inválido') from exc
    if not isinstance(user.get('id'), int):
        raise ValueError('usuário ausente')
    return user


def _database():
    global _mongo_client
    connection = os.environ.get('MONGO_CON', '')
    if not connection:
        raise RuntimeError('MONGO_CON não configurado')
    if _mongo_client is None:
        _mongo_client = MongoClient(connection, serverSelectionTimeoutMS=5000)
    return _mongo_client.fatoshistbot


def _passport(user):
    xp = int(user.get('xp', 0))
    level = int(user.get('level', 1 + xp // 100))
    premium = user.get('premium') or {'active': False}
    expires = premium.get('expires_at')
    active = bool(premium.get('active') and (not isinstance(expires, datetime) or expires > datetime.now(timezone.utc)))
    return {
        'first_name': user.get('first_name') or 'Historiador',
        'xp': xp,
        'level': level,
        'streak': int(user.get('streak', 0)),
        'badges': user.get('badges', []),
        'hits': int(user.get('hits', 0)),
        'questions': int(user.get('questions', 0)),
        'premium': active,
        'preferences': user.get('preferences') or {'topics': ['geral'], 'frequency': 'daily', 'delivery_hour': 8},
    }


def search_events(term, limit=20):
    needle = _normalized(term.strip())
    if len(needle) < 2:
        return []
    results = []
    for date_key, entries in _events().items():
        month, day = date_key.split('-', 1)
        for entry in entries:
            text = _plain(entry)
            if needle in _normalized(text):
                results.append({'date': f'{day}/{month}', 'text': text, 'source': 'eventos.json'})
                if len(results) >= limit:
                    return results
    return results


class handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False, default=str).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def _auth_user(self):
        telegram_user = validate_telegram_init_data(self.headers.get('X-Telegram-Init-Data', ''))
        user_id = telegram_user['id']
        user = _database().users.find_one({'user_id': user_id})
        if not user:
            _database().users.insert_one({
                'user_id': user_id,
                'username': telegram_user.get('username'),
                'first_name': telegram_user.get('first_name', ''),
                'sudo': 'false',
                'msg_private': 'true',
                'hits': 0,
                'questions': 0,
                'xp': 0,
                'level': 1,
                'streak': 0,
                'badges': [],
                'preferences': {'topics': ['geral'], 'frequency': 'daily', 'delivery_hour': 8},
                'created_at': datetime.now(timezone.utc),
                'last_seen': datetime.now(timezone.utc),
            })
            user = _database().users.find_one({'user_id': user_id})
        return user

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Allow', 'GET, POST, OPTIONS')
        self.end_headers()

    def do_GET(self):
        try:
            query = parse_qs(urlparse(self.path).query)
            action = query.get('action', ['health'])[0]
            if action == 'health':
                self._send(200, {'ok': True, 'service': 'museu-historico'})
            elif action == 'date':
                raw_date = query.get('date', [''])[0]
                match = re.fullmatch(r'(\d{1,2})[/-](\d{1,2})', raw_date)
                if not match:
                    raise ValueError('use uma data DD/MM')
                day, month = map(int, match.groups())
                datetime(2020, month, day)
                key = f'{month}-{day}'
                self._send(200, {'items': [
                    {'date': f'{day}/{month}', 'text': _plain(item), 'source': 'eventos.json'}
                    for item in _events().get(key, [])
                ]})
            elif action == 'search':
                self._send(200, {'items': search_events(query.get('q', [''])[0])})
            elif action == 'profile':
                self._send(200, _passport(self._auth_user()))
            elif action == 'ranking':
                self._auth_user()
                cursor = _database().users.find(
                    {'xp': {'$gt': 0}}, {'_id': 0, 'first_name': 1, 'xp': 1, 'level': 1}
                ).sort('xp', -1).limit(10)
                self._send(200, {'items': list(cursor)})
            else:
                self._send(404, {'error': 'ação não encontrada'})
        except ValueError as exc:
            self._send(401, {'error': str(exc)})
        except RuntimeError as exc:
            self._send(503, {'error': str(exc)})
        except Exception:
            self._send(500, {'error': 'erro interno'})

    def do_POST(self):
        try:
            query = parse_qs(urlparse(self.path).query)
            if query.get('action', [''])[0] != 'preferences':
                self._send(404, {'error': 'ação não encontrada'})
                return
            user = self._auth_user()
            size = min(int(self.headers.get('Content-Length', '0')), 4096)
            payload = json.loads(self.rfile.read(size) or b'{}')
            topics = sorted(set(payload.get('topics', [])) & ALLOWED_TOPICS) or ['geral']
            frequency = payload.get('frequency', 'daily')
            hour = int(payload.get('delivery_hour', 8))
            if frequency not in ALLOWED_FREQUENCIES or hour not in ALLOWED_HOURS:
                raise ValueError('preferências inválidas')
            preferences = {'topics': topics, 'frequency': frequency, 'delivery_hour': hour}
            _database().users.update_one({'_id': user['_id']}, {'$set': {'preferences': preferences}})
            self._send(200, {'ok': True, 'preferences': preferences})
        except (ValueError, json.JSONDecodeError) as exc:
            self._send(400, {'error': str(exc)})
        except RuntimeError as exc:
            self._send(503, {'error': str(exc)})
        except Exception:
            self._send(500, {'error': 'erro interno'})
