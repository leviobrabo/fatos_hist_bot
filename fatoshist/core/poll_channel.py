import json
from datetime import datetime

from ..bot.bot import bot
from ..config import CHANNEL_POST
from ..loggers import logger


def send_poll(chat_id, question, options, correct_option_id, explanation):
    try:
        bot.send_poll(
            chat_id,
            question,
            options,
            is_anonymous=True,
            type='quiz',
            correct_option_id=correct_option_id,
            explanation=explanation[:200] if explanation else None,
        )

        logger.success(f'Enviada pergunta para o chat {chat_id}')

    except Exception as e:
        logger.error(f'Erro ao enviar a pergunta: {e}')


def send_question():
    try:
        today = datetime.now()
        current_time = today.time()

        with open('./fatoshistoricos/data/perguntas.json', 'r', encoding='utf-8') as file:
            json_events = json.load(file)

        events = json_events[f'{today.month}-{today.day}']

        if current_time.hour == '9' and current_time.minute == '30':
            send_poll(
                CHANNEL_POST,
                events['pergunta1']['enunciado'],
                list(events['pergunta1']['alternativas'].values()),
                list(events['pergunta1']['alternativas']).index(events['pergunta1']['correta']),
                events['pergunta1'].get('explicacao', ''),
            )

        elif current_time.hour == '12' and current_time.minute == '00':
            send_poll(
                CHANNEL_POST,
                events['pergunta2']['enunciado'],
                list(events['pergunta2']['alternativas'].values()),
                list(events['pergunta2']['alternativas']).index(events['pergunta2']['correta']),
                events['pergunta2'].get('explicacao', ''),
            )

        elif current_time.hour == '15' and current_time.minute == '00':
            send_poll(
                CHANNEL_POST,
                events['pergunta3']['enunciado'],
                list(events['pergunta3']['alternativas'].values()),
                list(events['pergunta3']['alternativas']).index(events['pergunta3']['correta']),
                events['pergunta3'].get('explicacao', ''),
            )

        elif current_time.hour == '17' and current_time.minute == '30':
            send_poll(
                CHANNEL_POST,
                events['pergunta4']['enunciado'],
                list(events['pergunta4']['alternativas'].values()),
                list(events['pergunta4']['alternativas']).index(events['pergunta4']['correta']),
                events['pergunta4'].get('explicacao', ''),
            )
    except Exception as e:
        logger.error(f'Erro ao enviar a pergunta: {e}')
