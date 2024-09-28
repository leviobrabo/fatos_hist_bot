import json
import logging
from datetime import datetime

from fatoshist.database.groups import GroupManager
from fatoshist.database.poll_manager import PollManager
from fatoshist.database.users import UserManager

group_manager = GroupManager()
poll_manager = PollManager()
user_manager = UserManager()


def send_poll_chat(bot, chat_id, question, options, correct_option_id, explanation, message_thread_id):
    try:
        today = datetime.now()
        current_date = today.strftime('%d/%m/%Y')

        chat_info = bot.get_chat(chat_id)
        chat_type = chat_info.type

        is_anonymous = True if chat_type == 'channel' else False

        sent_poll = bot.send_poll(
            chat_id,
            question,
            options,
            is_anonymous=is_anonymous,
            type="quiz",
            correct_option_id=correct_option_id,
            explanation=explanation[:200] if explanation else None,
            message_thread_id=message_thread_id,
        )

        poll_id = sent_poll.poll.id

        poll_manager.add_poll(chat_id, poll_id, correct_option_id, current_date)

        logging.info(f'Enviada pergunta para o chat {chat_id}')

    except Exception as e:
        logging.error(f'Erro ao enviar a pergunta: {e}')


def send_question_chat(bot):
    try:
        today = datetime.now()
        current_time = today.time()

        with open('./fatoshist/data/perguntas.json', 'r', encoding='utf-8') as file:
            json_events = json.load(file)

        events = json_events[f'{today.month}-{today.day}']

        all_chats = group_manager.get_all_chats({'forwarding': 'true'})

        for chat in all_chats:
            chat_id = chat['chat_id']
            chat_db = group_manager.search_group(chat_id)
            thread_id = chat_db.get('thread_id')
            if chat_id:
                if current_time.hour == 10 and current_time.minute == 30:
                    logging.info('envio das questões')
                    send_poll_chat(
                        bot,
                        chat_id,
                        events['pergunta1']['enunciado'],
                        list(events['pergunta1']['alternativas'].values()),
                        list(events['pergunta1']['alternativas']).index(events['pergunta1']['correta']),
                        events['pergunta1'].get('explicacao', ''),
                        thread_id,
                    )

                elif current_time.hour == 13 and current_time.minute == 10:
                    send_poll_chat(
                        bot,
                        chat_id,
                        events['pergunta2']['enunciado'],
                        list(events['pergunta2']['alternativas'].values()),
                        list(events['pergunta2']['alternativas']).index(events['pergunta2']['correta']),
                        events['pergunta2'].get('explicacao', ''),
                        thread_id,
                    )

                elif current_time.hour == 13 and current_time.minute == 30:
                    send_poll_chat(
                        bot,
                        chat_id,
                        events['pergunta3']['enunciado'],
                        list(events['pergunta3']['alternativas'].values()),
                        list(events['pergunta3']['alternativas']).index(events['pergunta3']['correta']),
                        events['pergunta3'].get('explicacao', ''),
                        thread_id,
                    )

                elif current_time.hour == 18 and current_time.minute == 00:
                    send_poll_chat(
                        bot,
                        chat_id,
                        events['pergunta4']['enunciado'],
                        list(events['pergunta4']['alternativas'].values()),
                        list(events['pergunta4']['alternativas']).index(events['pergunta4']['correta']),
                        events['pergunta4'].get('explicacao', ''),
                        thread_id,
                    )

    except Exception as e:
        logging.error(f'Erro ao enviar a pergunta: {e}')


def remove_all_poll():
    try:
        logging.info('Removido as polls do banco de dados!')

        poll_manager.remove_all_poll_db()
    except Exception as e:
        logging.error(f'Erro ao processar a resposta da enquete: {e}')
