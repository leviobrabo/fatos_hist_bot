import json
import logging
from datetime import datetime

import pytz
import requests

from fatoshist.config import CHANNEL
from fatoshist.utils.month import get_month_name


def get_holidays_br_and_world_of_the_day(bot):
    try:
        today = datetime.now(pytz.timezone('America/Sao_Paulo'))
        day = today.day
        month = today.month

        # Abrindo o arquivo JSON de feriados brasileiros
        with open('./fatoshist/data/holidayBr.json', 'r', encoding='utf-8') as file:
            json_events = json.load(file)
            births = json_events.get(f'{month:02d}-{day:02d}', {}).get('births', [])  # Voltando para 'births' conforme o original

        # Inicializa a lista `message_parts` para feriados brasileiros
        message_parts = []

        # Obtendo feriados mundiais da API da Wikipedia
        response = requests.get(
            f'https://pt.wikipedia.org/api/rest_v1/feed/onthisday/holidays/{month}/{day}',
            headers={'accept': 'application/json; charset=utf-8; profile="https://www.mediawiki.org/wiki/Specs/onthisday/0.3.3"'},
        )

        world_holidays = []
        if response.status_code == 200:
            data = response.json()
            world_holidays = data.get('holidays', [])
        else:
            logging.warning(f'Erro ao obter informações (holiday): {response.status_code}')

        # Processando feriados brasileiros
        if births:
            for index, birth in enumerate(births, start=1):
                name = birth.get('name', 'Nome não disponível')
                bullet = '•'
                birth_message = f'<i>{bullet}</i> {name}'
                message_parts.append(birth_message)

        # Processando feriados mundiais
        world_holiday_messages = []
        if len(world_holidays) > 0:
            for index, holiday in enumerate(world_holidays[:5], start=1):
                name = f"<b>{holiday.get('text', 'Nome não disponível')}</b>"
                pages = holiday.get('pages', [])

                if len(pages) > 0:
                    info = pages[0].get('extract', 'Informações não disponíveis.')
                else:
                    info = 'Informações não disponíveis.'

                holiday_message = f'<i>{index}.</i> <b>Nome:</b> {name}\n<b>Informações:</b> {info}'
                world_holiday_messages.append(holiday_message)

        # Montando a mensagem final
        if message_parts or world_holiday_messages:
            message = (
                f'⚠️ <b>ATENÇÃO!</b>\n'
                f'Hoje não é um dia comum.\n'
                f'📅 <b>{day} de {get_month_name(month)}</b> marca datas que muita gente ignora — mas fazem parte da história.\n\n'
            )
        
            # Feriados no Brasil
            if message_parts:
                message += (
                    f'<blockquote expandable>'
                    f'<b>🎊 | Feriados no Brasil 🇧🇷</b>\n\n'
                    f'Essas datas impactam diretamente o país:\n\n'
                    f'{"\n".join(message_parts)}'
                    f'</blockquote>\n\n'
                )
        
            # Feriados no mundo
            if world_holiday_messages:
                message += (
                    f'<blockquote expandable>'
                    f'<b>🌍 | Feriados pelo mundo</b>\n\n'
                    f'Enquanto você vive o seu dia, o mundo celebra isso:\n\n'
                    f'{"\n\n".join(world_holiday_messages)}'
                    f'</blockquote>\n\n'
                )
        
            message += (
                f'💬 <b>Comente:</b> você sabia de algum desses feriados?\n'
                f'🔥 Reaja se você gosta de descobrir datas que quase ninguém lembra\n\n'
                f'#DatasComemorativas #FeriadosHoje #HistóriaDoDia\n'
                f'#FeriadosBrasil #FeriadosMundiais #HistóriaParaTodos\n\n'
                f'<blockquote>🔔 Siga <b>@historia_br</b> e descubra o que este dia representa.</blockquote>'
            )
        
            bot.send_message(CHANNEL, message, disable_web_page_preview=False)
        else:
            logging.info('Não há informações sobre feriados para o dia atual.')

    except Exception as e:
        logging.error(f'Erro ao enviar feriados para o canal: {e}')


def hist_channel_holiday_br_and_world(bot):
    try:
        get_holidays_br_and_world_of_the_day(bot)
        logging.info(f'Feriados brasileiros e mundiais enviados para o canal {CHANNEL}')
    except Exception as e:
        logging.error(f'Erro ao enviar o trabalho de feriados: {e}')
