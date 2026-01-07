import logging
import random
from datetime import datetime

import pytz
import requests
from telebot import types

from fatoshist.config import CHANNEL_IMG
from fatoshist.database.imgs import PhotoManager
from fatoshist.utils.month import get_month_name

photo_manager = PhotoManager()

headers = {
    "accept": "application/json",
    "User-Agent": "HistoriaBot/1.0 (https://historiadodia.com; contato@historiadodia.com)"
}

def send_historical_events_CHANNEL_IMG_image(bot, CHANNEL_IMG):
    """Busca um evento histórico com uma imagem e envia para o canal."""
    try:
        today = datetime.now(pytz.timezone('America/Sao_Paulo'))
        day = today.day
        month = today.month

        response = requests.get(
            f"https://pt.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}",
            headers=headers,
            timeout=10
        )
        events = response.json().get('events', [])
        events_with_photo = [event for event in events if event.get('pages') and event['pages'][0].get('thumbnail')]

        if not events_with_photo:
            logging.info('Não há eventos com fotos para enviar hoje.')
            return

        random_event = random.choice(events_with_photo)
        photo_url = random_event['pages'][0]['thumbnail']['source']

        if photo_manager.db.cphoto.find_one({'photo_url': photo_url}):
            logging.info(f'Imagem já utilizada: {photo_url}. Buscando outra...')
            return

        event_text = random_event.get('text', '')
        event_year = random_event.get('year', '')
        event_extract = random_event.get('extract', '')

        caption = f'<b>🖼 | História ilustrada </b>\n\nEm <b>{day} de {get_month_name(month)} de {event_year}</b>\n\n<code>{event_text}</code>'
        if event_extract:
            caption += f'\n\n\n\n{event_extract}'
        caption += '\n\n#fotos_historicas #historia #ilustracoes_historia #imagem_historicas'
        caption += ' #HistóriaParaTodos #DivulgueAHistória #CompartilheConhecimento #HistóriaDoBrasil #HistóriaMundial'

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

        logging.info(f'Evento histórico em foto enviado com sucesso para o canal ID {CHANNEL_IMG}.')

    except Exception as e:
        logging.error(f'Falha ao enviar evento histórico: {e}')


def hist_channel_imgs_chn(bot):
    try:
        send_historical_events_CHANNEL_IMG_image(bot, CHANNEL_IMG)
        logging.info(f'Mensagem enviada para o canal {CHANNEL_IMG}')

    except Exception as e:
        logging.error(f'Erro ao enviar o trabalho de imagens: {e}')


def remove_all_url_photo():
    try:
        result = photo_manager.remove_all_url_photo()
        logging.info(f'Removidas {result.deleted_count} fotos do banco de dados.')
    except Exception as e:
        logging.error(f'Erro ao remover fotos: {e}')
