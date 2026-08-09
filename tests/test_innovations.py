import hashlib
import hmac
import json
from datetime import datetime, timezone
from urllib.parse import urlencode

import pytest

from api.index import search_events, validate_telegram_init_data
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


@pytest.mark.parametrize('value', ['', '31/02', '13/13', 'abc'])
def test_invalid_historical_dates(value):
    with pytest.raises(ValueError):
        parse_date(value)
