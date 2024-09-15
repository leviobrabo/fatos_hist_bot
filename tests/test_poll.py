import json
from datetime import datetime
from pathlib import Path

import pytest

MAX_ALT_CHARS = 300
MAX_EXPLICACAO_CHARS = 200


@pytest.fixture(scope='class')
def perguntas():
    json_path = Path(__file__).resolve().parent.parent / 'fatoshist' / 'data' / 'perguntas.json'
    json_path = json_path.resolve()

    print(f'Looking for perguntas.json at: {json_path}')

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


def test_all_dates_present(perguntas, all_dates):
    """Verifica se todas as datas de 1-1 a 12-31 estão presentes no JSON."""
    missing_dates = [date for date in all_dates if date not in perguntas]
    assert not missing_dates, f'As seguintes datas estão faltando no JSON: {missing_dates}'


def test_questions_structure(perguntas, all_dates):
    """Verifica a estrutura e conteúdo de cada pergunta em cada data."""
    for date in all_dates:
        if date not in perguntas:
            pytest.fail(f'Data {date} não encontrada no JSON.')

        perguntas_date = perguntas[date]
        for pergunta_key in ['pergunta1', 'pergunta2', 'pergunta3', 'pergunta4']:
            assert pergunta_key in perguntas_date, f'{pergunta_key} não encontrada na data {date}.'

            pergunta = perguntas_date[pergunta_key]

            assert 'enunciado' in pergunta, f"'enunciado' não encontrado em {pergunta_key} na data {date}."
            assert isinstance(pergunta['enunciado'], str), f"'enunciado' deve ser uma string em {pergunta_key} na data {date}."
            assert pergunta['enunciado'].strip(), f"'enunciado' está vazio em {pergunta_key} na data {date}."

            assert 'alternativas' in pergunta, f"'alternativas' não encontrado em {pergunta_key} na data {date}."
            assert isinstance(pergunta['alternativas'], dict), f"'alternativas' deve ser um dicionário em {pergunta_key} na data {date}."

            for alt in ['alt1', 'alt2', 'alt3', 'alt4']:
                assert alt in pergunta['alternativas'], f"'{alt}' não encontrado em 'alternativas' de {pergunta_key} na data {date}."
                assert isinstance(pergunta['alternativas'][alt], str), f"'{alt}' deve ser uma string em {pergunta_key} na data {date}."
                assert (
                    len(pergunta['alternativas'][alt]) <= MAX_ALT_CHARS
                ), f"'{alt}' excede {MAX_ALT_CHARS} caracteres em {pergunta_key} na data {date}."

            assert 'correta' in pergunta, f"'correta' não encontrado em {pergunta_key} na data {date}."
            assert pergunta['correta'] in {'alt1', 'alt2', 'alt3', 'alt4'}, f"'correta' inválido em {pergunta_key} na data {date}."

            if 'explicacao' in pergunta:
                assert isinstance(pergunta['explicacao'], str), f"'explicacao' deve ser uma string em {pergunta_key} na data {date}."
                assert (
                    len(pergunta['explicacao']) <= MAX_EXPLICACAO_CHARS
                ), f"'explicacao' excede {MAX_EXPLICACAO_CHARS} caracteres em {pergunta_key} na data {date}."
