import logging
import random
from datetime import datetime

import pytz
import requests
from telebot import types

from fatoshist.config import GROUP_LOG
from fatoshist.database.groups import GroupManager
from fatoshist.utils.month import get_month_name

group_manager = GroupManager()


def send_historical_events_group_image(bot, chat_id):
    try:
        today = datetime.now(pytz.timezone('America/Sao_Paulo'))
        day = today.day
        month = today.month

        chat = group_manager.search_group(chat_id)
        topic = chat.get('thread_id')

        response = requests.get(f'https://pt.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}')
        events = response.json().get('events', [])

        if events:
            random_event = random.choice(events)
            if random_event.get('pages') and random_event['pages'][0].get('thumbnail'):
                photo_url = random_event['pages'][0]['thumbnail']['source']
            else:
                photo_url = None

            event_text = random_event.get('text', '')
            event_year = random_event.get('year', '')

            caption = f'<b>Você sabia?</b>\n\nEm <b>{day} de {get_month_name(month)} de {event_year}</b>\n\n<blockquote>{event_text}</blockquote>'
            inline_keyboard = types.InlineKeyboardMarkup()
            inline_keyboard.add(
                types.InlineKeyboardButton(text='📢 Canal Oficial', url='https://t.me/historia_br'),
                types.InlineKeyboardButton(text='Nosso site 🔗', url='https://www.historiadodia.com'),
            )

            if photo_url:
                bot.send_photo(
                    chat_id,
                    photo_url,
                    caption,
                    parse_mode='HTML',
                    reply_markup=inline_keyboard,
                    message_thread_id=topic,
                )
            else:
                bot.send_message(
                    chat_id,
                    caption,
                    parse_mode='HTML',
                    reply_markup=inline_keyboard,
                    message_thread_id=topic,
                )

            logging.info(f'Evento histórico em foto enviado com sucesso para o chat ID {chat_id}.')

        else:
            logging.info('Não há eventos históricos para o dia atual.')

    except Exception as e:
        logging.error(f'Falha ao enviar evento histórico: {e}')


def hist_image_chat_job(bot):
    try:
        chat_models = group_manager.get_all_chats({'forwarding': 'true'})
        for chat_model in chat_models:
            chat_id = chat_model['chat_id']
            if chat_id != GROUP_LOG:
                try:
                    send_historical_events_group_image(bot, chat_id)
                except Exception as e:
                    logging.error(f'Error sending imgs historical events to group {chat_id}: {str(e)}')
                    group_manager.update_forwarding_status(chat_id, {'forwarding': 'false'})
    except Exception as e:
        logging.error(f'Erro ao fazer o envio das imagens para chats: {e}')
