import random
from datetime import datetime

import pytz
import requests

from ..bot.bot import bot
from ..loggers import logger
from ..utils.month import get_month_name


@bot.message_handler(commands=['fotoshist'])
def cmd_photo_hist(message):
    try:
        today = datetime.now(pytz.timezone('America/Sao_Paulo'))
        day = today.day
        month = today.month

        response = requests.get(f'https://pt.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}')

        if response.status_code != '200':
            raise Exception(f'Falha na requisição: {response.status_code}')

        data = response.json()
        events = data.get('events', [])

        events_with_photo = [event for event in events if event.get('pages') and event['pages'][0].get('thumbnail')]

        if not events_with_photo:
            raise Exception('Nenhum evento com imagem encontrado para o dia de hoje.')

        random_event = random.choice(events_with_photo)
        photo_url = random_event['pages'][0]['thumbnail']['source']

        event_text = random_event.get('text', 'Sem descrição disponível.')
        event_year = random_event.get('year', 'Ano desconhecido')

        caption = f'🖼 | História ilustrada\n\n' f'Em <b>{day} de {get_month_name(month)} de {event_year}</b>\n\n' f'<code>{event_text}</code>'

        bot.send_photo(
            message.chat.id,
            photo_url,
            caption=caption,
            parse_mode='HTML',
            reply_to_message_id=message.message_id,
        )

    except Exception as e:
        logger.error(f'Erro ao enviar a imagem histórica: {e}')
