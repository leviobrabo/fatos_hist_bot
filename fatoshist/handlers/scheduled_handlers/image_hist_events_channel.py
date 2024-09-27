import logging
import random
from datetime import datetime

import pytz
import requests

from fatoshist.config import CHANNEL
from fatoshist.utils.month import get_month_name


def send_historical_events_channel_image(bot, CHANNEL):
    try:
        today = datetime.now(pytz.timezone('America/Sao_Paulo'))
        day = today.day
        month = today.month

        response = requests.get(f'https://pt.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}')
        events = response.json().get('events', [])
        events_with_photo = [event for event in events if event.get('pages') and event['pages'][0].get('thumbnail')]

        if not events_with_photo:
            logging.info('Não há eventos com fotos para enviar hoje.')
            return

        random_event = random.choice(events_with_photo)
        event_text = random_event.get('text', '')
        event_year = random_event.get('year', '')

        caption = (
            f'<b>🖼 | História ilustrada </b>\n\n'
            f'Em <b>{day} de {get_month_name(month)} de {event_year}</b>\n\n'
            f'<code>{event_text}</code>\n\n#fotos_historicas #historia\n'
            f'#HistóriaParaTodos #DivulgueAHistória #CompartilheConhecimento #HistóriaDoBrasil #HistóriaMundial\n\n'
            f'<blockquote>💬 Você sabia? Siga o @historia_br e acesse nosso site historiadodia.com.</blockquote>'
        )

        options = {'parse_mode': 'HTML'}

        photo_url = random_event['pages'][0]['thumbnail']['source']
        bot.send_photo(CHANNEL, photo_url, caption=caption, **options)

        logging.info(f'Evento histórico em foto enviado com sucesso para o canal ID {CHANNEL}.')

    except Exception as e:
        logging.error(f'Falha ao enviar evento histórico: {e}')


def hist_channel_imgs(bot):
    try:
        send_historical_events_channel_image(bot, CHANNEL)
        logging.info(f'Mensagem enviada para o canal {CHANNEL}')

    except Exception as e:
        logging.error(f'Erro ao enviar o trabalho de imagens: {e}')
