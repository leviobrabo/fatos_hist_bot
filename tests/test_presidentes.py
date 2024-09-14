import json
from pathlib import Path

import pytest


@pytest.fixture(scope='class')
def presidentes():
    json_path = Path(__file__).resolve().parent.parent / 'fatoshist' / 'data' / 'presidentes.json'
    json_path = json_path.resolve()

    # Carregar o arquivo JSON
    try:
        with json_path.open('r', encoding='utf-8') as file:
            data = json.load(file)
        print(f'Conteúdo carregado: {len(data.keys())} presidentes')  # Para verificar a quantidade de presidentes
    except FileNotFoundError:
        data = {}
        print(f'Arquivo {json_path} não encontrado.')
    except json.JSONDecodeError as e:
        data = {}
        print(f'Erro ao decodificar JSON: {e}')

    return data


@pytest.fixture(scope='class')
def all_president_ids():
    """Gera a lista de todos os IDs de presidentes do 1 até 652."""
    return [str(i) for i in range(1, 653)]


def test_all_presidents_present(presidentes, all_president_ids):
    """Verifica se todos os IDs de 1 a 652 estão presentes no JSON."""
    missing_ids = [id for id in all_president_ids if id not in presidentes]
    assert not missing_ids, f'Os seguintes IDs de presidentes estão faltando no JSON: {missing_ids}'


def test_presidents_structure(presidentes, all_president_ids):
    """Verifica a estrutura e o conteúdo de cada presidente."""
    required_fields = ['titulo', 'posicao', 'nome', 'foto', 'partido', 'ano_de_mandato', 'vice_presidente', 'local']

    for id in all_president_ids:
        if id not in presidentes:
            pytest.fail(f'Presidente com ID {id} não encontrado no JSON.')

        presidente_data = presidentes[id]

        # Verifica se todas as chaves obrigatórias estão presentes e não estão vazias
        for field in required_fields:
            assert field in presidente_data, f"'{field}' não encontrado no presidente com ID {id}."
            assert isinstance(presidente_data[field], str), f"'{field}' deve ser uma string no presidente com ID {id}."
            assert presidente_data[field].strip(), f"'{field}' está vazio no presidente com ID {id}."
