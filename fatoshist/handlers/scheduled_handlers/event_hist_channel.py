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
                f'❌ Quase ninguém lembra desses fatos…\n'
                f'⚠️ Mas eles mudaram o rumo da história.\n\n'
                f'<b>Qual você acha que foi?</b>\n\n'
                f'{events}\n\n'
                f'<b>💬 Qual deles você não conhecia?</b>\n'
                f'<b>👇 Responda com o número nos comentários</b>\n\n'
                f'#NesteDia #HojeNaHistoria #HistóriaDoDia\n\n'
                f'<blockquote>🔔 Ative as notificações e siga @historia_br</blockquote>'
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
