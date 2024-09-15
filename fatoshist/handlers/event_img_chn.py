import random
from datetime import datetime

import pytz
import requests
from telebot import types

from ..bot.bot import bot
from ..config import CHANNEL_IMG
from ..database.imgs import PhotoManager
from ..loggers import logger
from ..utils.month import get_month_name

photo_manager = PhotoManager()


def send_historical_events_CHANNEL_IMG_image(CHANNEL_IMG):
    """Busca um evento histórico com uma imagem e envia para o canal."""
    try:
        today = datetime.now(pytz.timezone('America/Sao_Paulo'))
        day = today.day
        month = today.month

        response = requests.get(f'https://pt.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}')
        events = response.json().get('events', [])
        events_with_photo = [event for event in events if event.get('pages') and event['pages'][0].get('thumbnail')]

        if not events_with_photo:
            logger.info('Não há eventos com fotos para enviar hoje.')
            return

        random_event = random.choice(events_with_photo)
        photo_url = random_event['pages'][0]['thumbnail']['source']

        if photo_manager.db.cphoto.find_one({'photo_url': photo_url}):
            logger.info(f'Imagem já utilizada: {photo_url}. Buscando outra...')
            return

        event_text = random_event.get('text', '')
        event_year = random_event.get('year', '')
        event_extract = random_event.get('extract', '')

        caption = f'<b>🖼 | História ilustrada </b>\n\nEm <b>{day} de {get_month_name(month)} de {event_year}</b>\n\n<code>{event_text}</code>'
        if event_extract:
            caption += f'\n\n\n\n{event_extract}'
        caption += '\n\n#fotos_historicas #historia #ilustracoes_historia #imagem_historicas'

        inline_keyboard = types.InlineKeyboardMarkup()
        inline_keyboard.add(
            types.InlineKeyboardButton(text='📢 Canal Oficial', url='https://t.me/historia_br'),
            types.InlineKeyboardButton(text='🔗 Site', url='https://www.historiadodia.com'),
        )

        bot.send_photo(
            CHANNEL_IMG,
            photo_url,
            caption,
            parse_mode='HTML',
            reply_markup=inline_keyboard,
        )

        photo_manager.add_url_photo(photo_url)

        logger.success(f'Evento histórico em foto enviado com sucesso para o canal ID {CHANNEL_IMG}.')

    except Exception as e:
        logger.error(f'Falha ao enviar evento histórico: {e}')


def hist_channel_imgs_chn():
    try:
        send_historical_events_CHANNEL_IMG_image(CHANNEL_IMG)
        logger.success(f'Mensagem enviada para o canal {CHANNEL_IMG}')

    except Exception as e:
        logger.error('Erro ao enviar o trabalho de imagens:', str(e))


def remove_all_url_photo():
    try:
        result = photo_manager.remove_all_url_photo()
        logger.info(f'Removidas {result.deleted_count} fotos do banco de dados.')
    except Exception as e:
        logger.error(f'Erro ao remover fotos: {e}')
