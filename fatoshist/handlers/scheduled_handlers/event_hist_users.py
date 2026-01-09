import logging
import time
from datetime import datetime

from telebot import types
from telebot.apihelper import ApiTelegramException

from fatoshist.database.users import UserManager
from fatoshist.utils.get_historical import get_historical_events

user_manager = UserManager()


def send_historical_events_user(bot, user_id):
    try:
        today = datetime.now()
        day = today.day
        month = today.month
        events = get_historical_events()

        markup = types.InlineKeyboardMarkup()
        channel_ofc = types.InlineKeyboardButton('Canal Oficial 🇧🇷', url='https://t.me/historia_br')
        site = types.InlineKeyboardButton('Nosso site 🔗', url='https://www.historiadodia.com')

        markup.add(channel_ofc)
        markup.add(site)

        if events:
            message = f'<b>HOJE NA HISTÓRIA</b>\n\n📅 | Acontecimento em <b>{day}/{month}</b>\n\n{events}'
            sent_message = bot.send_message(user_id, message, parse_mode='HTML', reply_markup=markup)
            message_id = sent_message.message_id

            user_manager.set_user_message_id(user_id, message_id)
        else:
            bot.send_message(
                user_id,
                '<b>Não há eventos históricos para hoje.</b>',
                parse_mode='HTML',
                reply_markup=markup,
            )

            logging.warning(f'Nenhum evento histórico para hoje no users {user_id}')
            return  
    except Exception:
        logging.error('Erro ao enviar fatos históricos para os usuários:')
        return  

def hist_user_job(bot):
    try:
        user_models = user_manager.get_all_users({'msg_private': 'true'})
        for user_model in user_models:
            user_id = user_model['user_id']
            message_id = user_model['message_id']

            if message_id:
                try:
                    bot.delete_message(user_id, message_id)
                except Exception:
                    logging.warning(f'Não foi possível deletar msg eventos históricos do {user_id}')

                    pass

            try:
                send_historical_events_user(bot, user_id)
                logging.info(f'Mensagem de eventos históricos enviada ao usuário {user_id}.')
            except Exception as e:
                error_message = str(e).lower()
                if '403' in error_message and 'user is deactivated' in error_message:
                    logging.info(f'Usuário {user_id} está desativado.')
                elif '400' in error_message and 'chat not found' in error_message:
                    logging.info(f'Chat não encontrado para o usuário {user_id}.')
                elif '403' in error_message and "bot can't initiate conversation with a user" in error_message:
                    logging.info(f'Bot não pode iniciar conversa com o usuário {user_id}.')
                elif '403' in error_message and 'bot was blocked by the user' in error_message:
                    logging.info(f'Bot foi bloqueado pelo usuário {user_id}.')
                else:
                    logging.error(f'Erro ao enviar mensagem de eventos históricos para o usuário {user_id}: {e}')

                user_manager.update_user(user_id, {'msg_private': 'false'})

            time.sleep(10)
    except Exception:
        logging.error('Erro ao enviar eventos históricos para os usuários:')
        return  
