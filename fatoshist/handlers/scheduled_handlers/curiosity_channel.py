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
                    f'⚠️ <b>POUCA GENTE SABE DISSO…</b>\n'
                    f'📜 <b>Curiosidades Históricas</b>\n'
                    f'<i>Um detalhe esquecido que muda a forma de ver a história.</i>\n\n'
                    f'<code>{info}</code>\n\n'
                    f'💬 <b>Você já sabia disso?</b>\n'
                    f'🔥 Reaja se essa curiosidade te surpreendeu\n\n'
                    f'#CuriosidadesHistoricas #HistóriaDoDia #VocêSabia\n'
                    f'#HistóriaParaTodos #Curiosidades\n\n'
                    f'<blockquote>🔔 Siga <b>@historia_br</b> e descubra o que os livros não contam.</blockquote>'
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
