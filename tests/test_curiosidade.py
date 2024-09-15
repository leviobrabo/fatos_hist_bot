import json
from datetime import datetime
from pathlib import Path

import pytest


@pytest.fixture(scope='class')
def curiosidades():
    json_path = Path(__file__).resolve().parent.parent / 'fatoshist' / 'data' / 'curiosidade.json'
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


def test_all_dates_present(curiosidades, all_dates):
    """Verifica se todas as datas de 1-1 a 12-31 estão presentes no JSON."""
    missing_dates = [date for date in all_dates if date not in curiosidades]
    assert not missing_dates, f'As seguintes datas estão faltando no JSON: {missing_dates}'


def test_curiosidades_structure(curiosidades, all_dates):
    """Verifica a estrutura e conteúdo de cada curiosidade em cada data."""
    for date in all_dates:
        if date not in curiosidades:
            pytest.fail(f'Data {date} não encontrada no JSON.')

        curiosidade_data = curiosidades[date]

        assert 'texto' in curiosidade_data, f"'texto' não encontrado na data {date}."
        assert isinstance(curiosidade_data['texto'], str), f"'texto' deve ser uma string na data {date}."
        assert curiosidade_data['texto'].strip(), f"'texto' está vazio na data {date}."

        if 'texto1' in curiosidade_data:
            assert isinstance(curiosidade_data['texto1'], str), f"'texto1' deve ser uma string na data {date}."
            assert curiosidade_data['texto1'].strip(), f"'texto1' está vazio na data {date}."
