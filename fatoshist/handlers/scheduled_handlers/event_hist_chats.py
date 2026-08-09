import logging
from datetime import datetime

from telebot import types
from telebot.apihelper import ApiTelegramException

from fatoshist.config import GROUP_LOG
from fatoshist.database.groups import GroupManager
from fatoshist.utils.get_historical import get_historical_events
from fatoshist.utils.telegram_errors import is_topic_closed_exception

group_manager = GroupManager()

IGNORED_CHATS = {
    GROUP_LOG,
    -1003612921107,
}

def send_historical_events_group(bot, chat_id):
    topic = None
    try:
        today = datetime.now()
        day = today.day
        month = today.month

        chat = group_manager.search_group(chat_id)
        topic = chat.get('thread_id') or None
        events = get_historical_events()

        markup = types.InlineKeyboardMarkup()
        channel_ofc = types.InlineKeyboardButton('Canal Oficial', url='https://t.me/historia_br', icon_custom_emoji_id='5215391376081954505')
        site = types.InlineKeyboardButton('Nosso site', url='https://www.historiadodia.com', icon_custom_emoji_id='5395523172059602457')

        markup.add(channel_ofc)
        markup.add(site)

        if events:
            message = f'<b>HOJE NA HISTÓRIA</b>\n\n<tg-emoji emoji-id="5431897022456145283">📅</tg-emoji> | Acontecimento em <b>{day}/{month}</b>\n\n{events}'
            bot.send_message(
                chat_id,
                message,
                parse_mode='HTML',
                reply_markup=markup,
                message_thread_id=topic,
            )

            logging.info(f'Eventos históricos enviada com sucesso para o grupo {chat_id}')

        else:
            bot.send_message(
                chat_id,
                '<b>Não há eventos históricos para hoje.</b>',
                parse_mode='HTML',
                reply_markup=markup,
                message_thread_id=topic,
            )

            logging.warning(f'Nenhum evento histórico para hoje no grupo {chat_id}')
            return  
    except ApiTelegramException as e:
        description = e.result_json.get('description', '')
        if topic and is_topic_closed_exception(e):
            group_manager.update_thread_id(chat_id, '')
            logging.warning(
                f'Topic {topic} from chat {chat_id} is closed. Cleared thread_id from database.'
            )

        logging.warning(
            f'Erro Telegram ao enviar eventos históricos para {chat_id}: {description}'
        )

        # NÃO remove o chat — apenas loga
        return
    except Exception:
        # Erros de rede, dados ou programação não significam que o bot saiu do grupo.
        logging.exception(f'Erro inesperado ao enviar fatos históricos para o chat {chat_id}')
        return
        
def hist_chat_job(bot):
    try:
        chat_models = group_manager.get_all_chats({'forwarding': 'true'})
        for chat_model in chat_models:
            chat_id = chat_model['chat_id']
            if chat_id not in IGNORED_CHATS:
                try:
                    send_historical_events_group(bot, chat_id)
                except Exception as e:
                    logging.error(f'Error sending historical events to group {chat_id}: {str(e)}')

    except Exception as e:
        logging.error(f'Erro ao fazer o envio para chats: {e}')
