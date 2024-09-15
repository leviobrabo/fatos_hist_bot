from datetime import datetime

from ..bot.bot import bot
from ..config import CHANNEL
from ..loggers import logger
from ..utils.get_historical import get_historical_events


def send_historical_events_channel(CHANNEL):
    try:
        today = datetime.now()
        day = today.day
        month = today.month
        events = get_historical_events()

        if events:
            message = (
                f'<b>HOJE NA HISTÓRIA</b>\n\n'
                f'📅 | Acontecimento em <b>{day}/{month}</b>\n\n'
                f'{events}\n\n#NesteDia #hoje_na_historia #historia #hoje #historia_do_dia\n\n'
                f'<blockquote>💬 Você sabia? Siga o @historia_br e acesse nosso site historiadodia.com.</blockquote>'
            )
            bot.send_message(CHANNEL, message)
        else:
            bot.send_message(
                CHANNEL,
                '<b>Não há eventos históricos para hoje.</b>',
                parse_mode='HTML',
            )

            logger.info(f'Nenhum evento histórico para hoje no grupo {CHANNEL}')

    except Exception as e:
        logger.error('Erro ao enviar fatos históricos para o canal:', str(e))


def hist_channel_events():
    try:
        send_historical_events_channel(CHANNEL)

        logger.success(f'Eventos históricos enviada o canal {CHANNEL}')

    except Exception as e:
        logger.error('Erro no trabalho de enviar fatos hist no canal:', str(e))
