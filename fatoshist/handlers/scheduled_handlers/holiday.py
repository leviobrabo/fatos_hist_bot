import json
import logging
from datetime import datetime
import pytz
import requests
from fatoshist.config import CHANNEL
from fatoshist.utils.month import get_month_name


def get_holidays_br_and_world_of_the_day(bot):
    try:
        today = datetime.now(pytz.timezone('America/Sao_Paulo'))
        day = today.day
        month = today.month

        # Abrindo o arquivo JSON de feriados brasileiros
        with open('./fatoshist/data/holidayBr.json', 'r', encoding='utf-8') as file:
            json_events = json.load(file)
            brazil_holidays = json_events.get(f'{month}-{day}', {}).get('births', [])  # Voltando para 'births' conforme o original

        # Obtendo feriados mundiais da API da Wikipedia
        response = requests.get(
            f'https://pt.wikipedia.org/api/rest_v1/feed/onthisday/holidays/{month}/{day}',
            headers={'accept': 'application/json; charset=utf-8; profile="https://www.mediawiki.org/wiki/Specs/onthisday/0.3.3"'},
        )

        world_holidays = []
        if response.status_code == 200:
            data = response.json()
            world_holidays = data.get('holidays', [])
        else:
            logging.warning(f'Erro ao obter informações (holiday): {response.status_code}')

        # Processando feriados brasileiros
        brazil_holiday_messages = []
        if brazil_holidays:
            for index, holiday in enumerate(brazil_holidays, start=1):
                name = holiday.get('name', 'Nome não disponível')
                bullet = '•'
                holiday_message = f'<i>{bullet}</i> {name}'
                brazil_holiday_messages.append(holiday_message)

        # Processando feriados mundiais
        world_holiday_messages = []
        if len(world_holidays) > 0:
            for index, holiday in enumerate(world_holidays[:5], start=1):
                name = f"<b>{holiday.get('text', 'Nome não disponível')}</b>"
                pages = holiday.get('pages', [])

                if len(pages) > 0:
                    info = pages[0].get('extract', 'Informações não disponíveis.')
                else:
                    info = 'Informações não disponíveis.'

                holiday_message = f'<i>{index}.</i> <b>Nome:</b> {name}\n<b>Informações:</b> {info}'
                world_holiday_messages.append(holiday_message)

        # Montando a mensagem final
        if brazil_holiday_messages or world_holiday_messages:
            message = f'<b>📅 | Datas comemorativas do dia {day} de {get_month_name(month)}</b>\n\n'

            # Se houver feriados brasileiros
            if brazil_holiday_messages:
                message += f'<blockquote expandable><b>🎊 | Feriados no Brasil 🇧🇷</b>\n\n'
                message += '\n'.join(brazil_holiday_messages)
                message += '</blockquote>\n\n'

            # Se houver feriados mundiais
            if world_holiday_messages:
                message += f'<blockquote expandable><b>🌍 | Feriados no mundo</b>\n\n'
                message += '\n\n'.join(world_holiday_messages)
                message += '</blockquote>\n\n'

            message += '#feriados_brasil #feriados_mundiais #historia #datas_comemorativas #HistóriaParaTodos\n\n'
            message += '<blockquote>💬 Você sabia? Siga o @historia_br e acesse nosso site historiadodia.com.</blockquote>'

            bot.send_message(CHANNEL, message, disable_web_page_preview=False)
        else:
            logging.info('Não há informações sobre feriados para o dia atual.')

    except Exception as e:
        logging.error(f'Erro ao enviar feriados para o canal: {e}')


def hist_channel_holiday_br_and_world(bot):
    try:
        get_holidays_br_and_world_of_the_day(bot)
        logging.info(f'Feriados brasileiros e mundiais enviados para o canal {CHANNEL}')
    except Exception as e:
        logging.error(f'Erro ao enviar o trabalho de feriados: {e}')
