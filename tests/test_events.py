import json

# Definindo constantes para os valores mágicos
FEBRUARY = 2
FEBRUARY_DAYS = 29
MONTHS_WITH_30_DAYS = {4, 6, 9, 11}
MAX_DAYS_30 = 30

# Carregar o arquivo JSON contendo os eventos
with open(r'fatoshist\data\eventos.json', 'r', encoding='utf-8') as f:
    events = json.load(f)


# Função para verificar se o evento contém todas as datas de 1-1 a 12-31, incluindo 2-29 (ano bissexto)
def test_has_all_dates():
    # Gerar todas as datas de 1-1 a 12-31, incluindo 2-29
    all_dates = []
    for month in range(1, 13):
        for day in range(1, 32):
            # Verificar limites dos meses
            if month == FEBRUARY and day > FEBRUARY_DAYS:
                continue
            elif month in MONTHS_WITH_30_DAYS and day > MAX_DAYS_30:
                continue
            # Adicionar a data à lista
            date_str = f'{month}-{day}'
            all_dates.append(date_str)

    # Verificar se todas as datas estão presentes no JSON
    missing_dates = [date for date in all_dates if date not in events]
    if missing_dates:
        print(f'Datas ausentes: {missing_dates}')
    else:
        print('Todas as datas estão presentes.')


# Função para verificar se há arrays vazios
def test_no_empty_arrays():
    empty_arrays = [date for date, event_list in events.items() if len(event_list) == 0]
    if empty_arrays:
        print(f'Datas com arrays vazios: {empty_arrays}')
    else:
        print('Nenhuma data possui arrays vazios.')


# Função principal para executar os testes
def run_tests():
    print('Verificando se todas as datas estão presentes:')
    test_has_all_dates()

    print('\nVerificando se há arrays vazios:')
    test_no_empty_arrays()


if __name__ == '__main__':
    run_tests()
