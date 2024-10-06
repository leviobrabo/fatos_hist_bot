import logging
from datetime import datetime
import pytz
import requests
from fatoshist.config import CHANNEL
from fatoshist.utils.month import get_month_name


def get_births_and_deaths_of_the_day(bot, CHANNEL):
    try:
        today = datetime.now(pytz.timezone('America/Sao_Paulo'))
        day = today.day
        month = today.month

        deaths_response = requests.get(
            f'https://pt.wikipedia.org/api/rest_v1/feed/onthisday/deaths/{month}/{day}',
            headers={'accept': 'application/json; charset=utf-8; profile="https://www.mediawiki.org/wiki/Specs/onthisday/0.3.3"'},
        )
        
        births_response = requests.get(
            f'https://pt.wikipedia.org/api/rest_v1/feed/onthisday/births/{month}/{day}',
            headers={'accept': 'application/json; charset=utf-8; profile="https://www.mediawiki.org/wiki/Specs/onthisday/0.3.3"'},
        )

        deaths = []
        births = []

        if deaths_response.status_code == 200:
            deaths_data = deaths_response.json()
            deaths = deaths_data.get('deaths', [])
        else:
            logging.warning('Erro ao obter informações (deaths_of_day):', deaths_response.status_code)

        if births_response.status_code == 200:
            births_data = births_response.json()
            births = births_data.get('births', [])
        else:
            logging.warning('Erro ao obter informações (births_of_day):', births_response.status_code)

        death_messages = []
        birth_messages = []

        if len(deaths) > 0:
            for index, death in enumerate(deaths[:5], start=1):
                name_death = death.get('text', '')
                photo_url = death.get('pages', [{}])[0].get('originalimage', {}).get('source', '')
                if photo_url:
                    name_death = f'<a href="{photo_url}">{name_death}</a>'
                info = death.get('pages', [{}])[0].get('extract', 'Informações não disponíveis.')
                date = death.get('year', 'Data desconhecida.')

                death_message = f'<i>{index}.</i> <b>Nome:</b> {name_death}\n<b>Informações:</b> {info}\n<b>Data da morte:</b> {date}'
                death_messages.append(death_message)

        if len(births) > 0:
            for index, birth in enumerate(births[:5], start=1):
                birth_name = birth.get('text', '')
                photo_url = birth.get('pages', [{}])[0].get('originalimage', {}).get('source', '')
                if photo_url:
                    birth_name = f'<a href="{photo_url}">{birth_name}</a>'
                info = birth.get('pages', [{}])[0].get('extract', 'Informações não disponíveis.')
                date = birth.get('year', 'Data desconhecida.')

                birth_message_text = f'<i>{index}.</i> <b>Nome:</b> {birth_name}\n<b>Data de nascimento:</b> {date}\n<b>Informações:</b> {info}'
                birth_messages.append(birth_message_text)

        if death_messages or birth_messages:
            message = f'<b>Vida e Legado: Nascimentos e Falecimentos do Dia</b>\n\n'

            if death_messages:
                message += f'<blockquote expandable><b>⚰️ |  Mortes neste dia: {day} de {get_month_name(month)}</b>\n\n'
                message += '\n\n'.join(death_messages)
                message += '</blockquote>\n\n'

            if birth_messages:
                message += f'<blockquote expandable><b>🎂 | Nascimentos neste dia: {day} de {get_month_name(month)}</b>\n\n'
                message += '\n\n'.join(birth_messages)
                message += '</blockquote>\n\n'

            message += '#nascimentos_historicos #historia #nascimentos #mortes_historicas #historia #falecimentos #HistóriaParaTodos\n\n'
            message += '<blockquote>💬 Você sabia? Siga o @historia_br e acesse nosso site historiadodia.com.</blockquote>'

            bot.send_message(CHANNEL, message, disable_web_page_preview=False)
        else:
            logging.info('Não há informações sobre nascidos ou mortos para o dia atual.')

    except Exception as e:
        logging.error(f'Erro ao enviar informações para o canal: {e}')


def hist_channel_birth_and_death(bot):
    try:
        get_births_and_deaths_of_the_day(bot, CHANNEL)
        logging.info(f'Nascimentos e Mortes enviados para o canal {CHANNEL}')
    except Exception as e:
        logging.error(f'Erro ao enviar o trabalho: {e}')
