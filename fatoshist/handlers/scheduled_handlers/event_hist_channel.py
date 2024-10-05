import logging
from datetime import datetime

from fatoshist.config import CHANNEL
from fatoshist.utils.get_historical import get_historical_events


def send_historical_events_channel(bot, CHANNEL):
    try:
        today = datetime.now()
        day = today.day
        month = today.month
        events = get_historical_events()

        if events:
            message = (
                f'<b>HOJE NA HISTÓRIA</b>\n\n'
                f'📅 | Acontecimento em <b>{day}/{month}</b>\n\n'
                f'{events}\n\n#NesteDia #hoje_na_historia #historia #hoje #historia_do_dia '
                f'#HistóriaParaTodos #DivulgueAHistória #CompartilheConhecimento #HistóriaDoBrasil #HistóriaMundial\n\n'
                f'<blockquote>💬 Você sabia? Siga o @historia_br e acesse nosso site historiadodia.com.</blockquote>'
            )
            bot.send_message(CHANNEL, message)
        else:
            bot.send_message(
                CHANNEL,
                '<b>Não há eventos históricos para hoje.</b>',
                parse_mode='HTML',
            )

            logging.info(f'Nenhum evento histórico para hoje no grupo {CHANNEL}')

    except Exception as e:
        logging.error(f'Erro ao enviar fatos históricos para o canal: {e}')


def hist_channel_events(bot):
    try:
        send_historical_events_channel(bot, CHANNEL)

        logging.info(f'Eventos históricos enviada o canal {CHANNEL}')

    except Exception as e:
        logging.error(f'Erro no trabalho de enviar fatos hist no canal: {e}')
