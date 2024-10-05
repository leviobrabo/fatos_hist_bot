import logging
from datetime import datetime

from telebot import types

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

            logging.warning(f'Nenhum evento histórico para hoje no grupo {user_id}')

    except Exception as e:
        logging.error(f'Erro ao enviar fatos históricos para os usuários:')


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
                    logging.warning(f'Não foi possível deletar {user_id}')

                    pass

            send_historical_events_user(bot, user_id)

            logging.info(f'Mensagem de eventos historicos enviada ao usuário {user_id}')

    except Exception as e:
        logging.error(f'Erro ao enviar para os usuários:')
