import json
from datetime import datetime
from pathlib import Path

import pytest


@pytest.fixture(scope='class')
def holidays():
    json_path = Path(__file__).resolve().parent.parent / 'fatoshist' / 'data' / 'holidayBr.json'
    json_path = json_path.resolve()

    try:
        with json_path.open('r', encoding='utf-8') as file:
            data = json.load(file)
        print(f'Conteúdo carregado: {data.keys()}')
    except FileNotFoundError:
        data = {}
        print(f'Arquivo {json_path} não encontrado.')
    except json.JSONDecodeError as e:
        data = {}
        print(f'Erro ao decodificar JSON: {e}')

    return data


@pytest.fixture(scope='class')
def all_dates():
    dates = []
    for month in range(1, 13):
        for day in range(1, 32):
            try:
                datetime(year=2020, month=month, day=day)
                dates.append(f'{month}-{day}')
            except ValueError:
                continue
    return dates


def test_all_dates_present(holidays, all_dates):
    """Verifica se todas as datas válidas de 1-1 a 12-31 estão presentes no JSON, se aplicável."""
    valid_dates = [date for date in all_dates if date in holidays]
    missing_dates = [date for date in valid_dates if date not in holidays]
    assert not missing_dates, f'As seguintes datas estão faltando no JSON: {missing_dates}'


def test_holidays_structure(holidays, all_dates):
    """Verifica a estrutura e o conteúdo de cada feriado em cada data."""
    for date in all_dates:
        if date not in holidays:
            continue

        holiday_data = holidays[date]

        assert 'births' in holiday_data, f"'births' não encontrada na data {date}."
        assert isinstance(holiday_data['births'], list), f"'births' deve ser uma lista na data {date}."
        assert holiday_data['births'], f"A lista 'births' está vazia na data {date}."

        for birth in holiday_data['births']:
            assert 'name' in birth, f"'name' não encontrado em um item da lista 'births' na data {date}."
            assert isinstance(birth['name'], str), f"'name' deve ser uma string na data {date}."
            assert birth['name'].strip(), f"'name' está vazio na data {date}."
