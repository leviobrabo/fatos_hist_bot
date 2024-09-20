import json
from datetime import datetime

import pytz

from fatoshist.config import CHANNEL
import logging
from fatoshist.utils.month import get_month_name


def get_holiday_br_of_the_day(bot,CHANNEL):
    try:
        today = datetime.now(pytz.timezone('America/Sao_Paulo'))
        day = today.day
        month = today.month

        with open('./fatoshistoricos/data/holidayBr.json', 'r', encoding='utf-8') as file:
            json_events = json.load(file)
            births = json_events.get(f'{month}-{day}', {}).get('births', [])

            if births:
                message_parts = []
                for index, birth in enumerate(births, start=1):
                    name = birth.get('name', '')
                    bullet = '•'
                    birth_message = f'<i>{bullet}</i> {name}'
                    message_parts.append(birth_message)

                message = f'<b>🎊 | Data comemorativa do dia 🇧🇷</b> \n\n<b><i>{day} de {get_month_name(month)}</i></b>\n\n'
                message += '\n'.join(message_parts)
                message += '\n\n#feriados_brasil #historia #feriados'
                message += '\n\n<blockquote>💬 Você sabia? Siga o @historia_br e acesse nosso site historiadodia.com.</blockquote>'
                bot.send_message(CHANNEL, message)
            else:
                logging.warning('Não há informações sobre nascidos hoje.')

    except Exception as e:
        logging.error(f'Erro ao obter informações: {e}')


def hist_channel_holiday_br(bot):
    try:
        get_holiday_br_of_the_day(bot,CHANNEL)

        logging.info(f'Feriados brasileiro enviada o canal {CHANNEL}')

    except Exception as e:
        logging.error(f'Erro ao enviar o trabalho feriados: {e}')
