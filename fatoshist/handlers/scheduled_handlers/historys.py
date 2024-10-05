import json
import logging
from datetime import datetime

from fatoshist.config import CHANNEL, OWNER


def get_history(bot, CHANNEL):
    try:
        today = datetime.now()
        day = today.day
        month = today.month

        with open('./fatoshist/data/historia.json', 'r', encoding='utf-8') as file:
            json_events = json.load(file)
            historia = json_events.get(f'{month}-{day}', {})

            if historia:
                photo_url = historia.get('photo', '')
                caption = historia.get('text', '')

                if photo_url and caption:
                    message = (
                        f'<b>História narrada 📰</b>\n\n'
                        f'<code>{caption}</code>\n\n'
                        f'#historia #historia_narrada\n'
                        f'#HistóriaParaTodos #DivulgueAHistória #CompartilheConhecimento\n' 
                        f'#HistóriaDoBrasil #HistóriaMundial\n\n'
                        f'<blockquote>💬 Você sabia? Siga o @historia_br e acesse nosso site historiadodia.com.</blockquote>'
                    )
                    bot.send_photo(CHANNEL, photo=photo_url, caption=message, parse_mode='HTML')
                else:
                    logging.info('Informações históricas incompletas para o dia de hoje.')
                    warning_message = (
                        f'A legenda da história para o dia {day}/{month} é muito longa '
                        f'({len(caption)} caracteres). Por favor, corrija para que não exceda 1024 caracteres.'
                    )
                    bot.send_message(OWNER, warning_message)
            else:
                logging.info('Não há informações para o dia de hoje. (historys)')

    except Exception as e:
        logging.error(f'Erro ao obter informações (historys): {str(e)}', exc_info=True)


def hist_channel_history(bot):
    try:
        get_history(bot, CHANNEL)
        logging.info(f'História enviada ao canal {CHANNEL}')
    except Exception as e:
        logging.error(f'Erro ao enviar a história: {str(e)}')
