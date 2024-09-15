import json
from datetime import datetime
from pathlib import Path

import pytest


@pytest.fixture(scope='class')
def frases():
    json_path = Path(__file__).resolve().parent.parent / 'fatoshist' / 'data' / 'frases.json'
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


def test_all_dates_present(frases, all_dates):
    """Verifica se todas as datas de 1-1 a 12-31 estão presentes no JSON."""
    missing_dates = [date for date in all_dates if date not in frases]
    assert not missing_dates, f'As seguintes datas estão faltando no JSON: {missing_dates}'


def test_frases_structure(frases, all_dates):
    """Verifica a estrutura e o conteúdo de cada frase em cada data."""
    for date in all_dates:
        if date not in frases:
            pytest.fail(f'Data {date} não encontrada no JSON.')

        frase_data = frases[date]

        assert 'quote' in frase_data, f"'quote' não encontrada na data {date}."
        assert isinstance(frase_data['quote'], str), f"'quote' deve ser uma string na data {date}."
        assert frase_data['quote'].strip(), f"'quote' está vazia na data {date}."

        assert 'author' in frase_data, f"'author' não encontrado na data {date}."
        assert isinstance(frase_data['author'], str), f"'author' deve ser uma string na data {date}."
        assert frase_data['author'].strip(), f"'author' está vazio na data {date}."
