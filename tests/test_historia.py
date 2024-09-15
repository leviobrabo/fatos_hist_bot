import json
from datetime import datetime
from pathlib import Path

import pytest


@pytest.fixture(scope='class')
def historias():
    json_path = Path(__file__).resolve().parent.parent / 'fatoshist' / 'data' / 'historia.json'
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


def test_all_dates_present(historias, all_dates):
    """Verifica se todas as datas de 1-1 a 12-31 estão presentes no JSON."""
    missing_dates = [date for date in all_dates if date not in historias]
    assert not missing_dates, f'As seguintes datas estão faltando no JSON: {missing_dates}'


def test_historias_structure(historias, all_dates):
    """Verifica a estrutura e o conteúdo de cada entrada de história em cada data."""
    for date in all_dates:
        if date not in historias:
            pytest.fail(f'Data {date} não encontrada no JSON.')

        historia_data = historias[date]

        assert 'photo' in historia_data, f"'photo' não encontrada na data {date}."
        assert isinstance(historia_data['photo'], str), f"'photo' deve ser uma string na data {date}."
        assert historia_data['photo'].strip(), f"'photo' está vazio na data {date}."

        assert 'text' in historia_data, f"'text' não encontrado na data {date}."
        assert isinstance(historia_data['text'], str), f"'text' deve ser uma string na data {date}."
        assert historia_data['text'].strip(), f"'text' está vazio na data {date}."
