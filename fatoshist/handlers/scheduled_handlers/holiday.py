import logging
from datetime import datetime

import pytz
import requests

from fatoshist.config import CHANNEL
from fatoshist.utils.month import get_month_name


def get_holidays_of_the_day(bot, CHANNEL):
    try:
        today = datetime.now(pytz.timezone('America/Sao_Paulo'))
        day = today.day
        month = today.month

        response = requests.get(
            f'https://pt.wikipedia.org/api/rest_v1/feed/onthisday/holidays/{month}/{day}',
            headers={'accept': 'application/json; charset=utf-8; profile="https://www.mediawiki.org/wiki/Specs/onthisday/0.3.3"'},
        )

        if response.status_code == 200:
            data = response.json()
            holidays = data.get('holidays', [])

            if len(holidays) > 0:
                holiday_messages = []

                for index, holiday in enumerate(holidays[:5], start=1):
                    name = f"<b>{holiday.get('text', '')}</b>"
                    pages = holiday.get('pages', [])

                    # Check if there are pages and extract information
                    if len(pages) > 0:
                        info = pages[0].get('extract', 'Informações não disponíveis.')
                    else:
                        info = 'Informações não disponíveis.'

                    holiday_message = f'<i>{index}.</i> <b>Nome:</b> {name}\n<b>Informações:</b> {info}'
                    holiday_messages.append(holiday_message)

                message = f'<b>📆 | Datas comemorativas neste dia: {day} de {get_month_name(month)}</b>\n\n'
                message += '\n\n'.join(holiday_messages)
                message += '\n\n#feriados #historia #datas_comemorativas'
                message += '\n\n<blockquote>💬 Você sabia? Siga o @historia_br e acesse nosso site historiadodia.com.</blockquote>'

                bot.send_message(CHANNEL, message)
            else:
                logging.info('Não há informações sobre feriados mundiais para o dia atual.')

        else:
            logging.warning(f'Erro ao obter informações (holiday): {response.status_code}')

    except Exception as e:
        logging.error(f'Erro ao obter informações (holiday): {e}')



def hist_channel_holiday(bot):
    try:
        get_holidays_of_the_day(bot, CHANNEL)

        logging.info(f'Feriados enviada o canal {CHANNEL}')

    except Exception as e:
        logging.error(f'Erro ao enviar o trabalho feriados: {e}')
