from datetime import datetime

import requests

from ..bot.bot import bot
from ..config import CHANNEL
from ..loggers import logger
from ..utils.month import get_month_name


def get_deaths_of_the_day(CHANNEL):
    try:
        today = datetime.now()
        day = today.day
        month = today.month

        response = requests.get(
            f'https://pt.wikipedia.org/api/rest_v1/feed/onthisday/deaths/{month}/{day}',
            headers={'accept': 'application/json; charset=utf-8; profile="https://www.mediawiki.org/wiki/Specs/onthisday/0.3.3"'},
        )

        if response.status_code == '200':
            data = response.json()
            deaths = data.get('deaths', [])

            if len(deaths) > 0:
                death_messages = []

                for index, death in enumerate(deaths[:5], start=1):
                    name_death = death.get('text', '')
                    photo_url = death.get('pages', [{}])[0].get('originalimage', {}).get('source', '')
                    if photo_url:
                        name = f'<a href="{photo_url}">{name_death}</a>'
                    info = death.get('pages', [{}])[0].get('extract', 'Informações não disponíveis.')
                    date = death.get('year', 'Data desconhecida.')

                    death_message = f'<i>{index}.</i> <b>Nome:</b> {name}\n<b>Informações:</b> {info}\n<b>Data da morte:</b> {date}'
                    death_messages.append(death_message)

                message = f'<b>⚰️ |  Mortes neste dia: {day} de {get_month_name(month)}</b>\n\n'
                message += '\n\n'.join(death_messages)
                message += '\n\n#mortes_historicas #historia #falecimentos'
                message += '\n\n<blockquote>💬 Você sabia? Siga o @historia_br e acesse nosso site historiadodia.com.</blockquote>'

                bot.send_message(CHANNEL, message, disable_web_page_preview=False)
            else:
                logger.info('Não há informações sobre mortos para o dia atual.')

        else:
            logger.warning('Erro ao obter informações:', response.status_code)

    except Exception as e:
        logger.error('Erro ao enviar mortos para os canal:', str(e))


def hist_channel_death():
    try:
        get_deaths_of_the_day(CHANNEL)
        logger.success(f'Mortos enviada o canal {CHANNEL}')
    except Exception as e:
        logger.info('Erro ao enviar o trabalho mortes:', str(e))
