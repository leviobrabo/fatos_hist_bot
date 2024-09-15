import json
import os

FEBRUARY = 2
FEBRUARY_DAYS = 29
MONTHS_WITH_30_DAYS = {4, 6, 9, 11}
MAX_DAYS_30 = 30

current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, 'fatoshist', 'data', 'eventos.json')

try:
    with open(json_path, 'r', encoding='utf-8') as f:
        events = json.load(f)
except FileNotFoundError:
    print(f"Erro: Arquivo {json_path} não encontrado.")
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
    if missing_dates:
        print(f'Datas ausentes: {missing_dates}')
    else:
        print('Todas as datas estão presentes.')


def test_no_empty_arrays():
    empty_arrays = [date for date, event_list in events.items() if len(event_list) == 0]
    if empty_arrays:
        print(f'Datas com arrays vazios: {empty_arrays}')
    else:
        print('Nenhuma data possui arrays vazios.')


def run_tests():
    print('Verificando se todas as datas estão presentes:')
    test_has_all_dates()

    print('\nVerificando se há arrays vazios:')
    test_no_empty_arrays()


if __name__ == '__main__':
    run_tests()
