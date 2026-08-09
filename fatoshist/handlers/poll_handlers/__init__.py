import logging

from telebot import TeleBot, types

from fatoshist.database.groups import GroupManager
from fatoshist.database.poll_manager import PollManager
from fatoshist.database.users import UserManager

group_manager = GroupManager()
poll_manager = PollManager()
user_manager = UserManager()


def register(bot: TeleBot):
    @bot.poll_answer_handler()
    def handle_poll_answer(poll_answer: types.PollAnswer):
        try:
            user_id = poll_answer.user.id
            first_name = poll_answer.user.first_name
            username = poll_answer.user.username

            poll_id = poll_answer.poll_id
            if not poll_answer.option_ids:
                # O Telegram envia uma lista vazia quando o usuário retira o voto.
                return
            option_id = poll_answer.option_ids[0]

            poll_db = poll_manager.search_poll(poll_id)
            correto = None

            try:
                if poll_db:
                    correto = poll_db.get('correct_option_id')
            except AttributeError as e:
                logging.warning(f'Erro ao obter a opção correta da enquete: {e}')

            user = user_manager.get_user(user_id)
            if not user:
                user_manager.add_user(user_id=user_id, username=username, first_name=first_name)
            else:
                user_manager.update_last_seen(user_id)

            is_correct = correto is not None and option_id == correto
            if not poll_manager.register_answer(poll_id, user_id, option_id, is_correct):
                return

            user_manager.set_questions_user(user_id)
            if is_correct:
                user_manager.set_hit_user(user_id)
            user_manager.record_learning_activity(user_id, xp=15 if is_correct else 3, topic='quiz')
            mission = user_manager.record_daily_mission(user_id, 'quiz')
            if mission and mission.get('rewarded_now'):
                try:
                    bot.send_message(user_id, '🧭 Missão diária concluída! Você recebeu <b>25 XP</b>.', parse_mode='HTML')
                except Exception:
                    logging.info('Missão concluída, mas não foi possível avisar o usuário %s', user_id)

        except Exception as e:
            logging.error(f'Erro ao processar a resposta da enquete: {e}')
