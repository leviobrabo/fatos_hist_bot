import json
from pathlib import Path

FEBRUARY = 2
FEBRUARY_DAYS = 29
MONTHS_WITH_30_DAYS = {4, 6, 9, 11}
MAX_DAYS_30 = 30

json_path = Path(__file__).resolve().parent.parent / 'fatoshist' / 'data' / 'eventos.json'

try:
    with json_path.open('r', encoding='utf-8') as f:
        events = json.load(f)
except FileNotFoundError:
    print(f'Erro: Arquivo {json_path} não encontrado.')
    events = {}


def test_has_all_dates():
    all_dates = []
    for month in range(1, 13):
        for day in range(1, 32):
            if month == FEBRUARY and day > FEBRUARY_DAYS:
                continue
            elif month in MONTHS_WITH_30_DAYS and day > MAX_DAYS_30:
                continue
            date_str = f'{month}-{day}'
            all_dates.append(date_str)

    missing_dates = [date for date in all_dates if date not in events]
    assert not missing_dates, f'Datas ausentes: {missing_dates}'


def test_no_empty_arrays():
    empty_arrays = [date for date, event_list in events.items() if len(event_list) == 0]
    assert not empty_arrays, f'Datas com arrays vazios: {empty_arrays}'


def test_no_duplicate_events_on_same_date():
    duplicated_dates = [date for date, event_list in events.items() if len(event_list) != len(set(event_list))]
    assert not duplicated_dates, f'Datas com eventos duplicados: {duplicated_dates}'


def run_tests():
    print('Verificando se todas as datas estão presentes:')
    test_has_all_dates()

    print('\nVerificando se há arrays vazios:')
    test_no_empty_arrays()


if __name__ == '__main__':
    run_tests()
