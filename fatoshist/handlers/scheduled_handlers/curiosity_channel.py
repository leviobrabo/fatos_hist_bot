import json
import logging
from datetime import datetime

from fatoshist.config import CHANNEL


def get_curiosity(bot, CHANNEL):
    try:
        today = datetime.now()
        day = today.day
        month = today.month
        with open('./fatoshist/data/curiosidade.json', 'r', encoding='utf-8') as file:
            json_events = json.load(file)
            curiosidade = json_events.get(f'{month}-{day}', {})
            if curiosidade:
                info = curiosidade.get('texto', '')

                message = (
                    f'<b>📜| Curiosidades Históricas</b>\n\n'
                    f'<code>{info}</code>\n\n'
                    f'#curiosidades_históricas #historia #curiosidade #voce_sabia '
                    f'#HistóriaParaTodos #DivulgueAHistória #CompartilheConhecimento #HistóriaDoBrasil #HistóriaMundial\n\n'
                    f'<blockquote>💬 Você sabia? Siga o @historia_br e acesse nosso site historiadodia.com.</blockquote>'
                )
                bot.send_message(CHANNEL, message)
            else:
                logging.info('Não há informações para o dia de hoje. (curiosity)')

    except Exception as e:
        logging.error(f'Erro ao obter informações (curiosity): {e}')


def hist_channel_curiosity(bot):
    try:
        get_curiosity(bot, CHANNEL)

        logging.info(f'Curiosidade enviada o canal {CHANNEL}')

    except Exception as e:
        logging.error(f'Erro ao enviar o trabalho curiosidade: {e}')
