from datetime import datetime

import pytz
import requests

from ..bot.bot import bot
from ..config import CHANNEL, OWNER
from ..loggers import logger
from ..utils.month import get_month_name


def get_births_of_the_day(CHANNEL):
    try:
        today = datetime.now(pytz.timezone('America/Sao_Paulo'))
        day = today.day
        month = today.month

        response = requests.get(
            f'https://pt.wikipedia.org/api/rest_v1/feed/onthisday/births/{month}/{day}',
            headers={'accept': 'application/json; charset=utf-8; profile="https://www.mediawiki.org/wiki/Specs/onthisday/0.3.3"'},
        )

        if response.status_code == '200':
            data = response.json()
            births = data.get('births', [])

            if len(births) > 0:
                birth_messages = []

                for index, birth in enumerate(births[:5], start=1):
                    birth_name = birth.get('text', '')
                    photo_url = birth.get('pages', [{}])[0].get('originalimage', {}).get('source', '')
                    if photo_url:
                        birth_name = f'<a href="{photo_url}">{birth_name}</a>'
                    info = birth.get('pages', [{}])[0].get('extract', 'Informações não disponíveis.')
                    date = birth.get('year', 'Data desconhecida.')

                    birth_message_text = f'<i>{index}.</i> <b>Nome:</b> {birth_name}\n<b>Informações:</b> {info}\n<b>Data de nascimento:</b> {date}'
                    birth_messages.append(birth_message_text)

                message = f'<b>🎂 | Nascimentos neste dia: {day} de {get_month_name(month)}</b>\n\n'
                message += '\n\n'.join(birth_messages)
                message += '\n\n#nascimentos_historicos'
                message += '\n\n<blockquote>💬 Você sabia? Siga o @historia_br e acesse nosso site historiadodia.com.</blockquote>'
                bot.send_message(CHANNEL, message, disable_web_page_preview=False)
                msg_text_owner = 'Mensagem de anivesário de canal enviada com sucesso'
                bot.send_message(OWNER, msg_text_owner)
            else:
                logger.info('Não há informações sobre nascidos hoje.')
        else:
            logger.warning('Erro ao obter informações:', response.status_code)

    except Exception as e:
        logger.error('Erro ao obter informações:', str(e))


def hist_channel_birth():
    try:
        get_births_of_the_day(CHANNEL)
        logger.success(f'Nascidos enviada o canal {CHANNEL}')
    except Exception as e:
        logger.error('Erro ao enviar o trabalho nascido:', str(e))
