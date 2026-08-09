import hashlib
import hmac
import json
from copy import deepcopy
from datetime import datetime, timezone
from types import SimpleNamespace
from urllib.parse import urlencode

import pytest

from api.index import _facts, search_events, validate_telegram_init_data
from fatoshist.database.users import UserManager
from fatoshist.services.historical_search import events_for_date, events_for_year, parse_date, search


def _signed_init_data(token, user, timestamp):
    values = {
        'auth_date': str(timestamp),
        'query_id': 'AA-test',
        'user': json.dumps(user, separators=(',', ':')),
    }
    check = '\n'.join(f'{key}={values[key]}' for key in sorted(values))
    secret = hmac.new(b'WebAppData', token.encode(), hashlib.sha256).digest()
    values['hash'] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    return urlencode(values)


def test_telegram_init_data_signature_and_expiration():
    token = '123456:ABCDEF'
    now = datetime(2026, 8, 9, 12, tzinfo=timezone.utc)
    signed = _signed_init_data(token, {'id': 42, 'first_name': 'Ada'}, int(now.timestamp()))

    assert validate_telegram_init_data(signed, token, now=now)['id'] == 42
    with pytest.raises(ValueError, match='assinatura'):
        validate_telegram_init_data(signed.replace('Ada', 'Eva'), token, now=now)
    with pytest.raises(ValueError, match='expirada'):
        validate_telegram_init_data(signed, token, max_age=1, now=datetime(2026, 8, 10, tzinfo=timezone.utc))


def test_historical_search_supports_dates_years_and_accents():
    assert parse_date('07/09') == (7, 9)
    assert events_for_date('1/1')['events']
    assert events_for_year(1945)
    assert search('Santos Dumont')
    assert search_events('independencia')


def test_mini_app_search_returns_stable_curated_fact_ids():
    item = search_events('independencia')[0]
    assert len(item['id']) == 24
    assert _facts()[item['id']]['text'] == item['text']


class _FakeUsers:
    def __init__(self, document):
        self.document = deepcopy(document)

    @staticmethod
    def _get(document, path):
        value = document
        for part in path.split('.'):
            value = value.get(part, {})
        return value

    @staticmethod
    def _set(document, path, value):
        target = document
        parts = path.split('.')
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        target[parts[-1]] = value

    def _matches(self, query):
        for key, expected in query.items():
            actual = self._get(self.document, key)
            if isinstance(expected, dict) and '$ne' in expected:
                if actual == expected['$ne']:
                    return False
            elif actual != expected:
                return False
        return True

    def _apply(self, update):
        for path, value in update.get('$set', {}).items():
            self._set(self.document, path, value)
        for path, value in update.get('$inc', {}).items():
            self._set(self.document, path, int(self._get(self.document, path) or 0) + value)
        for path, value in update.get('$addToSet', {}).items():
            current = self._get(self.document, path)
            if not isinstance(current, list):
                current = []
                self._set(self.document, path, current)
            if value not in current:
                current.append(value)

    def find_one(self, query):
        return deepcopy(self.document) if self._matches(query) else None

    def update_one(self, query, update):
        if self._matches(query):
            self._apply(update)
        return SimpleNamespace(modified_count=1)

    def find_one_and_update(self, query, update, **_kwargs):
        if not self._matches(query):
            return None
        self._apply(update)
        return deepcopy(self.document)


def test_daily_mission_rewards_only_once():
    users = _FakeUsers({
        'user_id': 42,
        'xp': 0,
        'level': 1,
        'badges': [],
        'daily_mission': {'date': None, 'actions': [], 'reward_claimed': False},
    })
    manager = UserManager.__new__(UserManager)
    manager.db = SimpleNamespace(users=users)

    assert not manager.record_daily_mission(42, 'explore')['completed']
    assert not manager.record_daily_mission(42, 'save')['completed']
    completed = manager.record_daily_mission(42, 'quiz')
    assert completed['completed'] and completed['rewarded_now']
    assert users.document['xp'] == 25
    assert 'missao_diaria' in users.document['badges']

    repeated = manager.record_daily_mission(42, 'quiz')
    assert repeated['completed'] and not repeated['rewarded_now']
    assert users.document['xp'] == 25


@pytest.mark.parametrize('value', ['', '31/02', '13/13', 'abc'])
def test_invalid_historical_dates(value):
    with pytest.raises(ValueError):
        parse_date(value)
