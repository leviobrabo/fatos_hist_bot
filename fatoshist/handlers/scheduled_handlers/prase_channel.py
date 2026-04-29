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
                    f'<tg-emoji emoji-id="5 447644880824181073">⚠️</tg-emoji> <b>ESSA FRASE AINDA INCOMODA MUITA GENTE…</b>\n\n'
                    f'<tg-emoji emoji-id="5177854824840414935">💡</tg-emoji> <b>Citação para refletir</b>\n\n'
                    f'<blockquote><i>"{quote}"</i>\n— <b>{author}</b></blockquote>\n\n'
                    f'<tg-emoji emoji-id="5213307977640979750">💬</tg-emoji> <b>Você concorda com essa ideia hoje?</b>\n'
                    f'<tg-emoji emoji-id="5235478122081560535">👍</tg-emoji> Sim  <tg-emoji emoji-id="5472309400536358507">👎</tg-emoji> Não\n\n'
                    f'#CitaçãoDoDia #Reflexão #HistóriaDoDia\n'
                    f'#Cultura #Pensar #HistóriaParaTodos\n\n'
                    f'<blockquote><tg-emoji emoji-id="5458603043203327669">🔔</tg-emoji> Siga <b>@historia_br</b> para refletir com a história.</blockquote>'
                )
                bot.send_message(CHANNEL, message, parse_mode="HTML")
            else:
                logging.info('Não há informações para o dia de hoje. (frase)')

    except Exception as e:
        logging.error(f'Erro ao obter informações (prase): {e}')


def hist_channel_frase(bot):
    try:
        get_frase(bot, CHANNEL)

        logging.info(f'Frase enviada o canal {CHANNEL}')

    except Exception as e:
        logging.error(f'Erro ao enviar o trabalho frase: {e}')
