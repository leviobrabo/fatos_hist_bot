import json
from datetime import datetime

from ..bot.bot import bot
from ..database.groups import GroupManager
from ..database.poll_manager import PollManager
from ..database.users import UserManager
from ..loggers import logger

group_manager = GroupManager()
poll_manager = PollManager()
user_manager = UserManager()


def send_poll_chat(chat_id, poll_data, message_thread_id):
    try:
        today = datetime.now()
        current_date = today.strftime('%d/%m/%Y')

        chat_info = bot.get_chat(chat_id)
        chat_type = chat_info.type

        is_anonymous = True if chat_type == 'channel' else False

        sent_poll = bot.send_poll(
            chat_id,
            poll_data['question'],
            poll_data['options'],
            is_anonymous=is_anonymous,
            type='quiz',
            correct_option_id=poll_data['correct_option_id'],
            explanation=poll_data.get('explanation', '')[:200],
            message_thread_id=message_thread_id,
        )

        poll_id = sent_poll.poll.id

        poll_manager.add_poll_db(chat_id, poll_id, poll_data['correct_option_id'], current_date)

        logger.success(f'Enviada pergunta para o chat {chat_id}')

    except Exception as e:
        logger.error(f'Erro ao enviar a pergunta: {e}')


def send_question_chat():
    try:
        today = datetime.now()
        current_time = today.time()

        with open('./fatoshistoricos/data/perguntas.json', 'r', encoding='utf-8') as file:
            json_events = json.load(file)

        events = json_events[f'{today.month}-{today.day}']

        all_chats = group_manager.get_all_chats({'forwarding': 'true'})

        for chat in all_chats:
            chat_id = chat['chat_id']
            chat_db = group_manager.search_group(chat_id)
            thread_id = chat_db.get('thread_id')
            if chat_id:
                if current_time.hour == '10' and current_time.minute == '30':
                    send_poll_chat(
                        chat_id,
                        events['pergunta1']['enunciado'],
                        list(events['pergunta1']['alternativas'].values()),
                        list(events['pergunta1']['alternativas']).index(events['pergunta1']['correta']),
                        events['pergunta1'].get('explicacao', ''),
                        thread_id,
                    )

                elif current_time.hour == '13' and current_time.minute == '30':
                    send_poll_chat(
                        chat_id,
                        events['pergunta2']['enunciado'],
                        list(events['pergunta2']['alternativas'].values()),
                        list(events['pergunta2']['alternativas']).index(events['pergunta2']['correta']),
                        events['pergunta2'].get('explicacao', ''),
                        thread_id,
                    )

                elif current_time.hour == '16' and current_time.minute == '00':
                    send_poll_chat(
                        chat_id,
                        events['pergunta3']['enunciado'],
                        list(events['pergunta3']['alternativas'].values()),
                        list(events['pergunta3']['alternativas']).index(events['pergunta3']['correta']),
                        events['pergunta3'].get('explicacao', ''),
                        thread_id,
                    )

                elif current_time.hour == '18' and current_time.minute == '00':
                    send_poll_chat(
                        chat_id,
                        events['pergunta4']['enunciado'],
                        list(events['pergunta4']['alternativas'].values()),
                        list(events['pergunta4']['alternativas']).index(events['pergunta4']['correta']),
                        events['pergunta4'].get('explicacao', ''),
                        thread_id,
                    )

    except Exception as e:
        logger.error(f'Erro ao enviar a pergunta: {e}')


@bot.poll_answer_handler()
def handle_poll_answer(poll_answer):
    try:
        user_id = poll_answer.user.id
        first_name = poll_answer.user.first_name
        last_name = poll_answer.user.last_name
        username = poll_answer.user.username

        poll_id = poll_answer.poll_id
        option_id = poll_answer.option_ids[0]

        poll_db = poll_manager.search_poll(poll_id)
        correto = None

        try:
            if poll_db:
                correto = poll_db.get('correct_option_id')
        except AttributeError as e:
            logger.warning(f'Erro ao obter a opção correta da enquete: {e}')

        user = user_manager.search_user(user_id)
        if not user:
            user_manager.add_new_user(user_id, first_name, last_name, username)

        poll_manager.set_questions_user(user_id)

        if correto is not None and option_id == correto:
            poll_manager.set_hit_user(user_id)

    except Exception as e:
        logger.error(f'Erro ao processar a resposta da enquete: {e}')


def remove_all_poll():
    try:
        logger.success('Removido as polls do banco de dados!')

        poll_manager.remove_all_poll_db()
    except Exception as e:
        logger.error(f'Erro ao processar a resposta da enquete: {e}')
