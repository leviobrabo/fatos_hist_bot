import logging
from datetime import datetime

import requests

from fatoshist.config import CHANNEL
from fatoshist.utils.month import get_month_name


def get_deaths_of_the_day(bot, CHANNEL):
    try:
        today = datetime.now()
        day = today.day
        month = today.month

        response = requests.get(
            f'https://pt.wikipedia.org/api/rest_v1/feed/onthisday/deaths/{month}/{day}',
            headers={'accept': 'application/json; charset=utf-8; profile="https://www.mediawiki.org/wiki/Specs/onthisday/0.3.3"'},
        )

        if response.status_code == 200:
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

                message = f'<b><tg-emoji emoji-id=\"5433769525117983603\">⚰️</tg-emoji> |  Mortes neste dia: {day} de {get_month_name(month)}</b>\n\n'
                message += '\n\n'.join(death_messages)
                message += '\n\n#mortes_historicas #historia #falecimentos'
                message += ' #HistóriaParaTodos #DivulgueAHistória #CompartilheConhecimento #HistóriaDoBrasil #HistóriaMundial'
                message += '\n\n<blockquote><tg-emoji emoji-id=\"5213307977640979750\">💬</tg-emoji>  Você sabia? Siga o @historia_br e acesse nosso site historiadodia.com.</blockquote>'

                bot.send_message(CHANNEL, message, parse_mode="HTML", disable_web_page_preview=False)
            else:   
                logging.info('Não há informações sobre mortos para o dia atual.')

        else:
            logging.warning('Erro ao obter informações (death_of_day):', response.status_code)

    except Exception:
        logging.error('Erro ao enviar mortos para os canal:')


def hist_channel_death(bot):
    try:
        get_deaths_of_the_day(bot, CHANNEL)
        logging.info(f'Mortos enviada o canal {CHANNEL}')
    except Exception as e:
        logging.info(f'Erro ao enviar o trabalho mortes: {e}')
