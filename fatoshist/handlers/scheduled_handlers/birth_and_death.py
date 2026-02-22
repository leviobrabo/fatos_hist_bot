import logging
from datetime import datetime

import pytz
import requests
import random

from fatoshist.config import CHANNEL, OWNER
from fatoshist.utils.month import get_month_name

INTRO_TEMPLATES = [
    "📜 Hoje a história registra nomes que marcaram o mundo.",
    "⏳ Neste dia, grandes nomes nasceram e partiram.",
    "🌍 O mundo mudou graças a essas pessoas.",
    "📅 Neste dia, a história ganhou e perdeu figuras importantes.",
    "⚠️ Pouca gente lembra desses nomes, mas eles mudaram tudo."
]

DEATH_TITLES = [
    "⚰️ Quem nos deixou neste dia",
    "🕯️ Figuras históricas que faleceram hoje",
    "🕰️ Mortes que marcaram a história neste dia",
]

BIRTH_TITLES = [
    "🎂 Quem nasceu neste dia",
    "🌟 Nascimentos históricos de hoje",
    "👶 Pessoas que nasceram neste dia e fizeram história",
]

CTA_TEMPLATES = [
    "💬 Qual nome você já conhecia?",
    "👇 Comente o mais famoso dessa lista",
    "🤔 Algum nome te surpreendeu?",
    "🔥 Reaja se acha importante lembrar dessas pessoas",
    "📢 Compartilhe para não deixar a história ser esquecida"
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
                    f'<b>{death_title} - {day} de {get_month_name(month)}</b>\n\n'
                    f'{"\n\n".join(birth_messages)}'
                    f'</blockquote>\n\n'
                )
        
            message += (
                f'{cta}\n\n'
                f'#HistóriaDoDia #NascimentosHistoricos #MortesHistoricas\n\n'
                f'<blockquote>🔔 Siga <b>@historia_br</b> e não perca nenhum momento da história.</blockquote>'
            )
            bot.send_message(CHANNEL, message, disable_web_page_preview=False)
        else:
            logging.info('Não há informações sobre nascidos ou mortos para o dia atual.')

    except Exception as e:
        logging.error(f'Erro ao enviar informações para o canal: {e}')


def hist_channel_birth_and_death(bot):
    try:
        get_births_and_deaths_of_the_day(bot, CHANNEL)
        logging.info(f'Nascimentos e Mortes enviados para o canal {CHANNEL}')
        bot.send_message(
                chat_id=OWNER,
                text=f"✅ VIVO E MORTOS enviado com sucesso: {intro}"
            )
    except Exception as e:
        logging.error(f'Erro ao enviar o trabalho: {e}')
