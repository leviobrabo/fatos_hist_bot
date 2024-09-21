import json
import logging
from datetime import datetime

import pytz

from fatoshist.config import CHANNEL


def get_frase(bot, CHANNEL):
    try:
        today = datetime.now(pytz.timezone('America/Sao_Paulo'))
        day = today.day
        month = today.month

        with open('./fatoshist/data/frases.json', 'r', encoding='utf-8') as file:
            json_events = json.load(file)
            frase = json_events.get(f'{month}-{day}')
            if frase:
                quote = frase.get('quote', '')
                author = frase.get('author', '')

                message = (
                    f'<b>💡 Citação para refletir</b>\n\n'
                    f'<blockquote><i>"{quote}"</i> - <b>{author}</b></blockquote>\n\n'
                    f'#cultura #historia #citacao #refletir #frases'
                )
                bot.send_message(CHANNEL, message)
            else:
                logging.info('Não há informações para o dia de hoje.')

    except Exception as e:
        logging.error(f'Erro ao obter informações: {e}')



def hist_channel_frase(bot):
    try:
        get_frase(bot, CHANNEL)

        logging.info(f'Frase enviada o canal {CHANNEL}')

    except Exception as e:
        logging.error(f'Erro ao enviar o trabalho curiosidade: {e}')
