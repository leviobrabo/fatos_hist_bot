import html
import json
import random
import re
import unicodedata
from datetime import datetime
from functools import lru_cache

from fatoshist.utils.paths import DATA_DIR, data_path


DATE_PATTERN = re.compile(r'\[(\d{1,2})/(\d{1,2})/(\d{3,4})\]')
TAG_PATTERN = re.compile(r'<[^>]+>')


def normalize(value):
    value = unicodedata.normalize('NFKD', str(value))
    return ''.join(char for char in value if not unicodedata.combining(char)).casefold()


def plain_text(value):
    return html.unescape(TAG_PATTERN.sub('', str(value))).strip()


@lru_cache(maxsize=32)
def load_json(filename):
    with data_path(filename).open(encoding='utf-8') as file:
        return json.load(file)


def parse_date(value):
    match = re.fullmatch(r'\s*(\d{1,2})[\-/](\d{1,2})\s*', value or '')
    if not match:
        raise ValueError('Use o formato DD/MM, por exemplo: /data 07/09')
    day, month = map(int, match.groups())
    datetime(2020, month, day)
    return day, month


def events_for_date(value):
    day, month = parse_date(value)
    events = load_json('eventos.json').get(f'{month}-{day}', [])
    return {
        'day': day,
        'month': month,
        'events': [plain_text(event) for event in events],
        'source': 'eventos.json',
    }


def events_for_year(year, limit=12):
    year = int(year)
    if year < 1 or year > datetime.now().year:
        raise ValueError('Informe um ano entre 1 e o ano atual.')
    matches = []
    for events in load_json('eventos.json').values():
        for event in events:
            date_match = DATE_PATTERN.search(event)
            if date_match and int(date_match.group(3)) == year:
                matches.append(plain_text(event))
    return matches[:limit]


def _walk(value, path=''):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk(child, f'{path}.{key}' if path else str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f'{path}.{index}' if path else str(index))
    elif isinstance(value, str) and value.strip():
        yield path, value


@lru_cache(maxsize=1)
def searchable_records():
    records = []
    filenames = (
        'eventos.json',
        'curiosidade.json',
        'historia.json',
        'frases.json',
        'presidentes.json',
        'mulheres_historicas.json',
        'inventores.json',
        'guerras.json',
        'civilizacoes.json',
        'descobertas.json',
    )
    for filename in filenames:
        path = DATA_DIR / filename
        if not path.exists():
            continue
        data = load_json(filename)
        for record_path, value in _walk(data):
            cleaned = plain_text(value)
            if len(cleaned) >= 20:
                records.append({
                    'text': cleaned,
                    'normalized': normalize(cleaned),
                    'source': filename,
                    'path': record_path,
                })
    return records


def search(term, limit=8):
    query = normalize(term).strip()
    if len(query) < 3:
        raise ValueError('Digite pelo menos 3 caracteres para pesquisar.')
    words = [word for word in query.split() if len(word) >= 2]
    scored = []
    seen = set()
    for record in searchable_records():
        text = record['normalized']
        score = sum(3 if word in text else 0 for word in words)
        if query in text:
            score += 8
        if score == 0 or record['text'] in seen:
            continue
        seen.add(record['text'])
        scored.append((score, record))
    scored.sort(key=lambda item: (-item[0], len(item[1]['text'])))
    return [record for _score, record in scored[:limit]]


def random_fact():
    events = load_json('eventos.json')
    populated = [(key, values) for key, values in events.items() if values]
    date_key, values = random.choice(populated)
    month, day = map(int, date_key.split('-'))
    return {'day': day, 'month': month, 'text': plain_text(random.choice(values)), 'source': 'eventos.json'}


def infer_topic(text):
    normalized = normalize(text)
    topics = {
        'brasil': ('brasil', 'brasileir', 'rio de janeiro', 'sao paulo'),
        'guerras': ('guerra', 'batalha', 'exercito', 'militar'),
        'politica': ('presidente', 'governo', 'republica', 'imperador'),
        'ciencia': ('cient', 'invent', 'descob', 'tecnolog'),
        'mulheres': ('mulher', 'rainha', 'atriz', 'escritora'),
        'civilizacoes': ('civilizacao', 'imperio', 'antiguidade', 'medieval'),
    }
    for topic, keywords in topics.items():
        if any(keyword in normalized for keyword in keywords):
            return topic
    return 'geral'
