import hashlib
import hmac
import html
import json
import logging
import os
import re
import unicodedata
from datetime import datetime, time, timedelta, timezone
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, parse_qsl, urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from bson import ObjectId
from pymongo import ASCENDING, MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError


ROOT = Path(__file__).resolve().parent.parent
EVENTS_PATH = ROOT / 'fatoshist' / 'data' / 'eventos.json'
MAX_AUTH_AGE_SECONDS = 86400
MAX_FAVORITES = 200
MISSION_REQUIRED = {'explore', 'save', 'quiz'}
EDITORIAL_HOURS = (13, 14, 22)
TZ = ZoneInfo('America/Sao_Paulo')
ALLOWED_TOPICS = {'brasil', 'guerras', 'politica', 'ciencia', 'mulheres', 'civilizacoes', 'geral'}
ALLOWED_FREQUENCIES = {'daily', 'weekly'}
ALLOWED_HOURS = {8, 12, 18, 21}
_events_cache = None
_facts_cache = None
_mongo_client = None
_indexes_ready = False


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


def _fact_id(text):
    return hashlib.sha256(text.encode()).hexdigest()[:24]


def _facts():
    global _facts_cache
    if _facts_cache is None:
        records = {}
        for date_key, entries in _events().items():
            month, day = date_key.split('-', 1)
            for entry in entries:
                text_value = _plain(entry)
                identifier = _fact_id(text_value)
                records[identifier] = {
                    'id': identifier,
                    'date': f'{day}/{month}',
                    'text': text_value,
                    'source': 'eventos.json',
                }
        _facts_cache = records
    return _facts_cache


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
    global _mongo_client, _indexes_ready
    connection = os.environ.get('MONGO_CON', '')
    if not connection:
        raise RuntimeError('MONGO_CON não configurado')
    if _mongo_client is None:
        _mongo_client = MongoClient(
            connection,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            maxPoolSize=10,
        )
    db = _mongo_client.fatoshistbot
    if not _indexes_ready:
        db.museum_favorites.create_index([('user_id', ASCENDING), ('fact_id', ASCENDING)], unique=True)
        db.museum_favorites.create_index([('user_id', ASCENDING), ('saved_at', ASCENDING)])
        _indexes_ready = True
    return db


def _today():
    return datetime.now(TZ).date().isoformat()


def _mission_view(user):
    mission = user.get('daily_mission') or {}
    actions = mission.get('actions', []) if mission.get('date') == _today() else []
    return {
        'date': _today(),
        'actions': actions,
        'required': sorted(MISSION_REQUIRED),
        'completed': MISSION_REQUIRED.issubset(set(actions)),
        'reward_claimed': bool(mission.get('reward_claimed') and mission.get('date') == _today()),
        'reward_xp': 25,
    }


def _record_mission(db, user_id, action):
    if action not in {'explore', 'save', 'quiz', 'share'}:
        raise ValueError('ação de missão inválida')
    today = _today()
    user = db.users.find_one({'user_id': user_id}) or {}
    if (user.get('daily_mission') or {}).get('date') != today:
        db.users.update_one(
            {'user_id': user_id},
            {'$set': {
                'daily_mission.date': today,
                'daily_mission.actions': [],
                'daily_mission.reward_claimed': False,
            }},
        )
    updated = db.users.find_one_and_update(
        {'user_id': user_id, 'daily_mission.date': today},
        {'$addToSet': {'daily_mission.actions': action}},
        return_document=ReturnDocument.AFTER,
    ) or {}
    actions = set((updated.get('daily_mission') or {}).get('actions', []))
    if MISSION_REQUIRED.issubset(actions):
        rewarded = db.users.find_one_and_update(
            {
                'user_id': user_id,
                'daily_mission.date': today,
                'daily_mission.reward_claimed': {'$ne': True},
            },
            {
                '$set': {'daily_mission.reward_claimed': True},
                '$inc': {'xp': 25},
                '$addToSet': {'badges': 'missao_diaria'},
            },
            return_document=ReturnDocument.AFTER,
        )
        if rewarded:
            db.users.update_one(
                {'user_id': user_id},
                {'$set': {'level': 1 + int(rewarded.get('xp', 0)) // 100}},
            )
    return _mission_view(db.users.find_one({'user_id': user_id}) or {})


def _is_admin(user):
    owner = os.environ.get('OWNER_ID', '').strip()
    return user.get('sudo') == 'true' or (owner.isdigit() and user.get('user_id') == int(owner))


def _passport(user):
    xp = int(user.get('xp', 0))
    level = int(user.get('level', 1 + xp // 100))
    premium = user.get('premium') or {'active': False}
    expires = premium.get('expires_at')
    if isinstance(expires, datetime) and expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
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
        'admin': _is_admin(user),
        'mission': _mission_view(user),
        'preferences': user.get('preferences') or {'topics': ['geral'], 'frequency': 'daily', 'delivery_hour': 8},
    }


def search_events(term, limit=20):
    needle = _normalized(term.strip())
    if len(needle) < 2:
        return []
    results = []
    for record in _facts().values():
        if needle in _normalized(record['text']):
            results.append(record)
            if len(results) >= limit:
                return results
    return results


def _telegram_call(method, payload):
    token = os.environ.get('BOT_TOKEN', '')
    if not token:
        raise RuntimeError('BOT_TOKEN não configurado')
    request = Request(
        f'https://api.telegram.org/bot{token}/{method}',
        data=json.dumps(payload, ensure_ascii=False).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urlopen(request, timeout=10) as response:
            result = json.loads(response.read())
    except HTTPError as exc:
        detail = exc.read().decode(errors='replace')[:300]
        raise RuntimeError(f'Telegram recusou a operação: {detail}') from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError('Telegram temporariamente indisponível') from exc
    if not result.get('ok'):
        raise RuntimeError(result.get('description', 'Falha na API do Telegram'))
    return result['result']


def _next_editorial_slot(db):
    now = datetime.now(TZ)
    for offset in range(31):
        day = (now + timedelta(days=offset)).date()
        start = datetime.combine(day, time.min, TZ).astimezone(timezone.utc)
        end = start + timedelta(days=1)
        pending = db.editorial_queue.count_documents({
            'status': {'$in': ['pending', 'processing']},
            'scheduled_at': {'$gte': start, '$lt': end},
        })
        sent = db.editorial_posts.count_documents({
            'source': 'bcchannel',
            'published_at': {'$gte': start, '$lt': end},
        })
        if pending + sent >= 3:
            continue
        for hour in EDITORIAL_HOURS:
            local = datetime.combine(day, time(hour), TZ)
            if local <= now:
                continue
            candidate = local.astimezone(timezone.utc)
            lower, upper = candidate - timedelta(hours=1), candidate + timedelta(hours=1)
            collision = db.editorial_queue.find_one({
                'status': {'$in': ['pending', 'processing']},
                'scheduled_at': {'$gt': lower, '$lt': upper},
            }) or db.editorial_posts.find_one({'published_at': {'$gt': lower, '$lt': upper}})
            if not collision:
                return candidate
    raise RuntimeError('Não há horário editorial disponível')


def _serialize_queue(item):
    scheduled_at = item.get('scheduled_at')
    if isinstance(scheduled_at, datetime):
        if scheduled_at.tzinfo is None:
            scheduled_at = scheduled_at.replace(tzinfo=timezone.utc)
        scheduled_at = scheduled_at.isoformat()
    return {
        'id': str(item['_id']),
        'type': item.get('post_type', 'post'),
        'status': item.get('status'),
        'scheduled_at': scheduled_at,
        'attempts': item.get('attempts', 0),
    }


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
        db = _database()
        user = db.users.find_one({'user_id': user_id})
        if not user:
            db.users.insert_one({
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
                'daily_mission': {'date': None, 'actions': [], 'reward_claimed': False},
                'created_at': datetime.now(timezone.utc),
                'last_seen': datetime.now(timezone.utc),
            })
            user = db.users.find_one({'user_id': user_id})
        return user

    def _optional_user(self):
        if not self.headers.get('X-Telegram-Init-Data'):
            return None
        return self._auth_user()

    def _admin_user(self):
        user = self._auth_user()
        if not _is_admin(user):
            raise PermissionError('acesso restrito a administradores')
        return user

    def _body(self):
        size = min(int(self.headers.get('Content-Length', '0')), 8192)
        return json.loads(self.rfile.read(size) or b'{}')

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Allow', 'GET, POST, OPTIONS')
        self.end_headers()

    def do_GET(self):
        try:
            query = parse_qs(urlparse(self.path).query)
            action = query.get('action', ['health'])[0]
            if action == 'health':
                self._send(200, {'ok': True, 'service': 'museu-historico', 'version': '3.1'})
            elif action in {'date', 'search'}:
                user = self._optional_user()
                if action == 'date':
                    raw_date = query.get('date', [''])[0]
                    match = re.fullmatch(r'(\d{1,2})[/-](\d{1,2})', raw_date)
                    if not match:
                        raise ValueError('use uma data DD/MM')
                    day, month = map(int, match.groups())
                    datetime(2020, month, day)
                    key = f'{month}-{day}'
                    items = [_facts()[_fact_id(_plain(item))] for item in _events().get(key, [])]
                else:
                    items = search_events(query.get('q', [''])[0])
                if user and items:
                    _record_mission(_database(), user['user_id'], 'explore')
                self._send(200, {'items': items})
            elif action == 'profile':
                self._send(200, _passport(self._auth_user()))
            elif action == 'ranking':
                self._auth_user()
                cursor = _database().users.find(
                    {'xp': {'$gt': 0}}, {'_id': 0, 'first_name': 1, 'xp': 1, 'level': 1}
                ).sort('xp', -1).limit(10)
                self._send(200, {'items': list(cursor)})
            elif action == 'favorites':
                user = self._auth_user()
                cursor = _database().museum_favorites.find(
                    {'user_id': user['user_id']}, {'_id': 0, 'user_id': 0}
                ).sort('saved_at', -1).limit(MAX_FAVORITES)
                self._send(200, {'items': list(cursor)})
            elif action == 'mission':
                self._send(200, _mission_view(self._auth_user()))
            elif action == 'admin':
                self._admin_user()
                db = _database()
                queue = [_serialize_queue(item) for item in db.editorial_queue.find(
                    {'status': {'$in': ['pending', 'processing', 'failed']}},
                ).sort('scheduled_at', 1).limit(30)]
                suggestions = [{
                    'id': str(item['_id']),
                    'first_name': item.get('first_name', 'Usuário'),
                    'text': item.get('text', ''),
                    'source': item.get('source', ''),
                    'created_at': item.get('created_at'),
                } for item in db.suggestions.find({'status': 'pending'}).sort('created_at', 1).limit(30)]
                self._send(200, {
                    'stats': {
                        'users': db.users.count_documents({}),
                        'active_24h': db.users.count_documents({'last_seen': {'$gte': datetime.now(timezone.utc) - timedelta(hours=24)}}),
                        'favorites': db.museum_favorites.count_documents({}),
                        'pending_queue': len(queue),
                        'pending_suggestions': len(suggestions),
                    },
                    'queue': queue,
                    'suggestions': suggestions,
                })
            else:
                self._send(404, {'error': 'ação não encontrada'})
        except PermissionError as exc:
            self._send(403, {'error': str(exc)})
        except ValueError as exc:
            self._send(401, {'error': str(exc)})
        except RuntimeError as exc:
            self._send(503, {'error': str(exc)})
        except Exception:
            logging.exception('Erro na API GET')
            self._send(500, {'error': 'erro interno'})

    def do_POST(self):
        try:
            action = parse_qs(urlparse(self.path).query).get('action', [''])[0]
            payload = self._body()
            if action == 'preferences':
                user = self._auth_user()
                topics = sorted(set(payload.get('topics', [])) & ALLOWED_TOPICS) or ['geral']
                frequency = payload.get('frequency', 'daily')
                hour = int(payload.get('delivery_hour', 8))
                if frequency not in ALLOWED_FREQUENCIES or hour not in ALLOWED_HOURS:
                    raise ValueError('preferências inválidas')
                preferences = {'topics': topics, 'frequency': frequency, 'delivery_hour': hour}
                _database().users.update_one({'_id': user['_id']}, {'$set': {'preferences': preferences}})
                self._send(200, {'ok': True, 'preferences': preferences})
            elif action == 'favorite':
                user = self._auth_user()
                db = _database()
                identifier = str(payload.get('fact_id', ''))
                if payload.get('operation') == 'remove':
                    db.museum_favorites.delete_one({'user_id': user['user_id'], 'fact_id': identifier})
                    self._send(200, {'ok': True, 'saved': False})
                    return
                fact = _facts().get(identifier)
                if not fact:
                    raise ValueError('fato não pertence à base curada')
                exists = db.museum_favorites.find_one({'user_id': user['user_id'], 'fact_id': identifier})
                if not exists and db.museum_favorites.count_documents({'user_id': user['user_id']}) >= MAX_FAVORITES:
                    raise ValueError(f'limite de {MAX_FAVORITES} favoritos atingido')
                collection = re.sub(r'[<>\x00-\x1f]', '', str(payload.get('collection', 'Meu Museu'))).strip()[:40] or 'Meu Museu'
                db.museum_favorites.update_one(
                    {'user_id': user['user_id'], 'fact_id': identifier},
                    {'$set': {**fact, 'user_id': user['user_id'], 'fact_id': identifier, 'collection': collection, 'saved_at': datetime.now(timezone.utc)}},
                    upsert=True,
                )
                mission = _record_mission(db, user['user_id'], 'save')
                self._send(200, {'ok': True, 'saved': True, 'mission': mission})
            elif action == 'prepare-share':
                user = self._auth_user()
                fact = _facts().get(str(payload.get('fact_id', '')))
                if not fact:
                    raise ValueError('fato não pertence à base curada')
                result = _telegram_call('savePreparedInlineMessage', {
                    'user_id': user['user_id'],
                    'result': {
                        'type': 'article',
                        'id': fact['id'],
                        'title': f'Fato Histórico — {fact["date"]}',
                        'description': fact['text'][:180],
                        'input_message_content': {
                            'message_text': (
                                f'<b>📜 Fato Histórico — {html.escape(fact["date"])}</b>\n\n'
                                f'{html.escape(fact["text"])}\n\n<i>Fonte: base curada · @fatoshistbot</i>'
                            ),
                            'parse_mode': 'HTML',
                        },
                    },
                    'allow_user_chats': True,
                    'allow_bot_chats': False,
                    'allow_group_chats': True,
                    'allow_channel_chats': True,
                })
                _record_mission(_database(), user['user_id'], 'share')
                self._send(200, {'id': result['id']})
            elif action == 'admin-queue':
                self._admin_user()
                db = _database()
                item_id = ObjectId(str(payload.get('id', '')))
                operation = payload.get('operation')
                if operation == 'cancel':
                    result = db.editorial_queue.update_one(
                        {'_id': item_id, 'status': 'pending'},
                        {'$set': {'status': 'cancelled', 'updated_at': datetime.now(timezone.utc)}},
                    )
                elif operation == 'delay':
                    slot = _next_editorial_slot(db)
                    result = db.editorial_queue.update_one(
                        {'_id': item_id, 'status': 'pending'},
                        {'$set': {'scheduled_at': slot, 'updated_at': datetime.now(timezone.utc)}},
                    )
                else:
                    raise ValueError('operação administrativa inválida')
                if result.modified_count != 1:
                    raise ValueError('item não está mais pendente')
                self._send(200, {'ok': True})
            elif action == 'admin-suggestion':
                admin = self._admin_user()
                db = _database()
                suggestion_id = ObjectId(str(payload.get('id', '')))
                decision = payload.get('decision')
                if decision not in {'approve', 'reject'}:
                    raise ValueError('decisão inválida')
                suggestion = db.suggestions.find_one_and_update(
                    {'_id': suggestion_id, 'status': 'pending'},
                    {'$set': {'status': 'processing', 'moderator_id': admin['user_id']}},
                    return_document=ReturnDocument.AFTER,
                )
                if not suggestion:
                    raise ValueError('sugestão já processada')
                status = 'rejected'
                try:
                    if decision == 'approve':
                        owner_id = int(os.environ.get('OWNER_ID', '0'))
                        if not owner_id:
                            raise RuntimeError('OWNER_ID não configurado na Vercel')
                        staging = _telegram_call('sendMessage', {
                            'chat_id': owner_id,
                            'text': (
                                '<b>📜 Sugestão da comunidade</b>\n\n'
                                f'{html.escape(suggestion["text"])}\n\n'
                                f'<b>Fonte:</b> {html.escape(suggestion["source"])}\n'
                                f'<i>Colaboração de {html.escape(suggestion["first_name"])}</i>'
                            ),
                            'parse_mode': 'HTML',
                            'disable_web_page_preview': True,
                        })
                        db.editorial_queue.create_index('scheduled_at', unique=True)
                        for _attempt in range(5):
                            slot = _next_editorial_slot(db)
                            try:
                                db.editorial_queue.insert_one({
                                    'from_chat_id': owner_id,
                                    'message_id': staging['message_id'],
                                    'requested_by': admin['user_id'],
                                    'post_type': 'community',
                                    'status': 'pending',
                                    'scheduled_at': slot,
                                    'created_at': datetime.now(timezone.utc),
                                    'attempts': 0,
                                })
                                break
                            except DuplicateKeyError:
                                continue
                        else:
                            raise RuntimeError('não foi possível reservar horário editorial')
                        status = 'approved'
                    db.suggestions.update_one(
                        {'_id': suggestion_id},
                        {'$set': {'status': status, 'moderated_at': datetime.now(timezone.utc)}},
                    )
                    try:
                        _telegram_call('sendMessage', {
                            'chat_id': suggestion['user_id'],
                            'text': f'Sua sugestão foi {"aprovada e agendada" if status == "approved" else "recusada"}.',
                        })
                    except RuntimeError:
                        logging.info('Não foi possível avisar o autor da sugestão %s', suggestion_id)
                except Exception:
                    db.suggestions.update_one({'_id': suggestion_id}, {'$set': {'status': 'pending'}})
                    raise
                self._send(200, {'ok': True, 'status': status})
            else:
                self._send(404, {'error': 'ação não encontrada'})
        except PermissionError as exc:
            self._send(403, {'error': str(exc)})
        except (ValueError, json.JSONDecodeError, TypeError) as exc:
            self._send(400, {'error': str(exc)})
        except RuntimeError as exc:
            self._send(503, {'error': str(exc)})
        except Exception:
            logging.exception('Erro na API POST')
            self._send(500, {'error': 'erro interno'})
