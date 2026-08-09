import logging
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from telebot import types
from telebot.apihelper import ApiTelegramException

from fatoshist.database.users import UserManager
from fatoshist.utils.get_historical import get_historical_events


TZ = ZoneInfo('America/Sao_Paulo')
user_manager = UserManager()


def send_historical_events_user(bot, user_id):
    today = datetime.now(TZ)
    events = get_historical_events()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Canal Oficial', url='https://t.me/historia_br'))
    markup.add(types.InlineKeyboardButton('Nosso site', url='https://www.historiadodia.com'))

    if events:
        message = (
            '<b>HOJE NA HISTÓRIA</b>\n\n'
            f'📅 | Acontecimento em <b>{today.day}/{today.month}</b>\n\n{events}'
        )
        sent_message = bot.send_message(user_id, message, parse_mode='HTML', reply_markup=markup)
        user_manager.set_user_message_id(user_id, sent_message.message_id)
        return True

    bot.send_message(
        user_id,
        '<b>Não há eventos históricos para hoje.</b>',
        parse_mode='HTML',
        reply_markup=markup,
    )
    logging.warning('Nenhum evento histórico para hoje no usuário %s', user_id)
    return False


def hist_user_job(bot):
    """Entrega conteúdo no horário/frequência escolhidos, uma única vez por dia."""
    try:
        now = datetime.now(TZ)
        today = now.date().isoformat()
        for user_model in user_manager.get_all_users({'msg_private': 'true'}):
            preferences = user_model.get('preferences') or {}
            delivery_hour = int(preferences.get('delivery_hour', 8))
            frequency = preferences.get('frequency', 'daily')
            if delivery_hour != now.hour:
                continue
            if frequency == 'weekly' and now.weekday() != 0:
                continue
            if user_model.get('last_personalized_delivery') == today:
                continue

            user_id = user_model['user_id']
            message_id = user_model.get('message_id')
            if message_id:
                try:
                    bot.delete_message(user_id, message_id)
                except Exception:
                    logging.warning('Não foi possível apagar a mensagem anterior de %s', user_id)

            try:
                if send_historical_events_user(bot, user_id):
                    user_manager.update_user(user_id, {'last_personalized_delivery': today})
                    logging.info('Mensagem histórica enviada ao usuário %s', user_id)
            except ApiTelegramException as exc:
                result = getattr(exc, 'result_json', {}) or {}
                description = result.get('description', str(exc)).lower()
                permanent = result.get('error_code') == 403 or (
                    result.get('error_code') == 400 and 'chat not found' in description
                )
                if permanent:
                    user_manager.update_user(user_id, {'msg_private': 'false'})
                else:
                    logging.error('Erro temporário do Telegram para %s: %s', user_id, exc)
            except Exception:
                logging.exception('Erro ao enviar eventos para o usuário %s', user_id)

            time.sleep(0.1)
    except Exception:
        logging.exception('Erro na rotina personalizada de eventos históricos')
