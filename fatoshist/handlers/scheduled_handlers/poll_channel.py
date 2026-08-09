import json
import logging
from datetime import datetime

from fatoshist.config import CHANNEL_POST
from fatoshist.utils.paths import data_path

CHANNEL_POSTS = [
    CHANNEL_POST,
    -1003612921107
]


def send_poll(bot, chat_id, question, options, correct_option_id, explanation):
    try:
        bot.send_poll(
            chat_id,
            question,
            options,
            is_anonymous=True,
            type='quiz',
            correct_option_id=correct_option_id,
            explanation=explanation[:200] if explanation else None,
            explanation_parse_mode='HTML',
        )

        logging.info(f'Enviada pergunta para o chat {chat_id}')

    except Exception as e:
        logging.error(f'Erro ao enviar a pergunta: {e}')


def send_question(bot):
    try:
        today = datetime.now()
        current_time = today.time()

        with data_path('perguntas.json').open('r', encoding='utf-8') as file:
            json_events = json.load(file)

        events = json_events[f'{today.month}-{today.day}']

        if current_time.hour == 10 and current_time.minute == 30:
            question_key = 'pergunta1'

        elif current_time.hour == 20 and current_time.minute == 30:
            question_key = 'pergunta2'

        elif current_time.hour == 12 and current_time.minute == 0:
            question_key = 'pergunta3'

        elif current_time.hour == 16 and current_time.minute == 30:
            question_key = 'pergunta4'
        else:
            logging.warning('send_question executado fora de um horário configurado: %s', current_time.strftime('%H:%M'))
            return

        question = events[question_key]
        for chat_id in CHANNEL_POSTS:
            send_poll(
                bot,
                chat_id,
                question['enunciado'],
                list(question['alternativas'].values()),
                list(question['alternativas']).index(question['correta']),
                question.get('explicacao', ''),
            )
    except Exception as e:
        logging.error(f'Erro ao enviar a pergunta: {e}')
