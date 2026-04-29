import logging
from datetime import datetime

import pytz
import requests
import random

from fatoshist.config import CHANNEL, OWNER
from fatoshist.utils.month import get_month_name
from fatoshist.utils.post_tracker import can_post, register_post, minutes_until_next

INTRO_TEMPLATES = [
    "<tg-emoji emoji-id='5373098009640836781'>📜</tg-emoji> Hoje a história registra nomes que marcaram o mundo.",
    "<tg-emoji emoji-id='5319190934510904031'>⏳</tg-emoji> Neste dia, grandes nomes nasceram e partiram.",
    "<tg-emoji emoji-id='5314361729117855941'>🌍</tg-emoji> O mundo mudou graças a essas pessoas.",
    "<tg-emoji emoji-id='5888854085024616252'>📅</tg-emoji> Neste dia, a história ganhou e perdeu figuras importantes.",
    "<tg-emoji emoji-id='5447644880824181073'>⚠️</tg-emoji> Pouca gente lembra desses nomes, mas eles mudaram tudo."
]

DEATH_TITLES = [
    "<tg-emoji emoji-id='5433769525117983603'>⚰️</tg-emoji> Quem nos deixou neste dia",
    "<tg-emoji emoji-id='5350571717922167592'>🕯️</tg-emoji> Figuras históricas que faleceram hoje",
    "<tg-emoji emoji-id='5325547803936572038'>🕰️</tg-emoji> Mortes que marcaram a história neste dia",
]

BIRTH_TITLES = [
    "<tg-emoji emoji-id='5370999492914976897'>🎂</tg-emoji> Quem nasceu neste dia",
    "<tg-emoji emoji-id='5325547803936572038'>🌟</tg-emoji> Nascimentos históricos de hoje",
    "<tg-emoji emoji-id='5379601719703379510'>👶</tg-emoji> Pessoas que nasceram neste dia e fizeram história",
]

CTA_TEMPLATES = [
    "<tg-emoji emoji-id='5213307977640979750'>💬</tg-emoji> Qual nome você já conhecia?",
    "<tg-emoji emoji-id='5470177992950946662'>👇</tg-emoji> Comente o mais famoso dessa lista",
    "<tg-emoji emoji-id='5917909521602187613'>🤔</tg-emoji> Algum nome te surpreendeu?",
    "<tg-emoji emoji-id='5317058732356542197'>🔥</tg-emoji> Reaja se acha importante lembrar dessas pessoas",
    "<tg-emoji emoji-id='5305417940760273444'>📢</tg-emoji> Compartilhe para não deixar a história ser esquecida"
]

HEADERS = {
    'accept': 'application/json',
    'User-Agent': 'HistoriaBot/1.0 (contato@historiadodia.com)'
}

intro = random.choice(INTRO_TEMPLATES)
death_title = random.choice(DEATH_TITLES)
birth_title = random.choice(BIRTH_TITLES)
cta = random.choice(CTA_TEMPLATES)

def get_births_and_deaths_of_the_day(bot, CHANNEL):
    try:
        today = datetime.now(pytz.timezone('America/Sao_Paulo'))
        day = today.day
        month = today.month

        deaths_response = requests.get(
            f'https://pt.wikipedia.org/api/rest_v1/feed/onthisday/deaths/{month}/{day}',
            headers=HEADERS,
            timeout=10
        )
        
        births_response = requests.get(
            f'https://pt.wikipedia.org/api/rest_v1/feed/onthisday/births/{month}/{day}',
            headers=HEADERS,
            timeout=10
        )

        deaths = []
        births = []

        if deaths_response.status_code == 200:
            deaths_data = deaths_response.json()
            deaths = deaths_data.get('deaths', [])
        else:
            logging.warning(
                            'Erro ao obter informações (deaths_of_day): %s',
                            deaths_response.status_code
                        )


        if births_response.status_code == 200:
            births_data = births_response.json()
            births = births_data.get('births', [])
        else:
            logging.warning(
                        'Erro ao obter informações (births_of_day): %s',
                        births_response.status_code
                    )

        death_messages = []
        birth_messages = []

        if deaths:
            index = 1
            for death in deaths:
                page = death.get('pages', [{}])[0]
                thumbnail = page.get('thumbnail', {}).get('source')
        
                # 🔴 ignora se não tiver imagem
                if not thumbnail:
                    continue
        
                name_death = death.get('text', '')
                name_death = f'<a href="{thumbnail}">{name_death}</a>'
        
                info = page.get('extract', 'Informações não disponíveis.')
                date = death.get('year', 'Data desconhecida.')
        
                death_message = (
                    f'<i>{index}.</i> <b>Nome:</b> {name_death}\n'
                    f'<b>Informações:</b> {info}\n'
                    f'<b>Data da morte:</b> {date}'
                )
        
                death_messages.append(death_message)
        
                index += 1
                if index > 5:
                    break

        if births:
            index = 1
            for birth in births:
                page = birth.get('pages', [{}])[0]
                thumbnail = page.get('thumbnail', {}).get('source')
        
                # 🔴 ignora se não tiver imagem
                if not thumbnail:
                    continue
        
                birth_name = birth.get('text', '')
                birth_name = f'<a href="{thumbnail}">{birth_name}</a>'
        
                info = page.get('extract', 'Informações não disponíveis.')
                date = birth.get('year', 'Data desconhecida.')
        
                birth_message_text = (
                    f'<i>{index}.</i> <b>Nome:</b> {birth_name}\n'
                    f'<b>Data de nascimento:</b> {date}\n'
                    f'<b>Informações:</b> {info}'
                )
        
                birth_messages.append(birth_message_text)
        
                index += 1
                if index > 5:
                    break

        if death_messages or birth_messages:
            message = f"{intro}\n\n"

            if death_messages:
                message += (
                    f'<blockquote expandable>'
                    f'<b>{death_title} - {day} de {get_month_name(month)}</b>\n\n'
                    f'{"\n\n".join(death_messages)}'
                    f'</blockquote>\n\n'
                )
        
            if birth_messages:
                message += (
                    f'<blockquote expandable>'
                    f'<b>{birth_title} - {day} de {get_month_name(month)}</b>\n\n'
                    f'{"\n\n".join(birth_messages)}'
                    f'</blockquote>\n\n'
                )
        
            message += (
                f'{cta}\n\n'
                f'#HistóriaDoDia #NascimentosHistoricos #MortesHistoricas\n\n'
                f'<blockquote><tg-emoji emoji-id="5458603043203327669">🔔</tg-emoji> Siga <b>@historia_br</b> e não perca nenhum momento da história.</blockquote>'
            )
            bot.send_message(CHANNEL, message, disable_web_page_preview=False)
            register_post()
        else:
            logging.info('Não há informações sobre nascidos ou mortos para o dia atual.')

    except Exception as e:
        logging.error(f'Erro ao enviar informações para o canal: {e}')


def hist_channel_birth_and_death(bot):
    try:
        if not can_post():
            mins = minutes_until_next()
            logging.info(f'[birth_death] Intervalo mínimo não atingido. Aguardando {mins}min.')
            return
        get_births_and_deaths_of_the_day(bot, CHANNEL)
        logging.info(f'Nascimentos e Mortes enviados para o canal {CHANNEL}')
        bot.send_message(chat_id=OWNER, text="<tg-emoji emoji-id='5429381339851796035'>✅</tg-emoji> Nascidos e mortos enviados com sucesso")
    except Exception as e:
        logging.error(f'Erro ao enviar o trabalho: {e}')
