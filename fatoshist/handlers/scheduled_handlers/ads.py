import logging
import random
import time

from telebot import types

from fatoshist.config import CHANNEL, CHANNEL_IMG, OWNER
from fatoshist.database.users import UserManager

user_manager = UserManager()

ads_links = [
    'https://www.cpmrevenuegate.com/aczkcs92r?key=bf57d0551edc1505d3b77aa5cda4bd66',
    'https://www.cpmrevenuegate.com/n4tz3iaax?key=2a5964f0ee7306247266e686b1cd3934',
]


def ads_message_channel_user(bot, user_id):
    try:
        random_link = random.choice(ads_links)

        markup = types.InlineKeyboardMarkup()
        channel_ofc = types.InlineKeyboardButton('ADS', url=random_link)
        markup.add(channel_ofc)

        msg_text = (
            '🔔 <b>Apoie nosso canal!</b> 🔔\n\n'
            'Gostou do conteúdo? 🕰️📚 Que tal nos dar uma força? Ao clicar nos anúncios, você nos ajuda a '
            'continuar trazendo histórias incríveis todos os dias, sem nenhum custo para você! 🚀✨\n\n'
            'Cada clique faz a diferença e nos permite manter o canal ativo e sempre atualizado. 😊🙏\n\n'
            '<b>Clique e apoie o canal com apenas um toque!</b> 🙌'
        )

        bot.send_message(user_id, msg_text, parse_mode='HTML', reply_markup=markup)
    except Exception as e:
        logging.error(f'Erro ao preparar a mensagem ADS para os usuários e canais: {e}')


def ads_msg_job(bot):
    try:
        user_models = user_manager.get_all_users({'msg_private': 'true'})
        for user_model in user_models:
            user_id = user_model['user_id']

            try:
                ads_message_channel_user(bot, user_id)
                logging.info(f'Mensagem enviada ao usuário {user_id}')
            except Exception as e:
                if '403' in str(e) and 'user is deactivated' in str(e):
                    pass
                elif '400' in str(e) and 'chat not found' in str(e):
                    pass
                elif '403' in str(e) and "bot can't initiate conversation with a user" in str(e):
                    pass
                elif '403' in str(e) and 'bot was blocked by the user' in str(e):
                    pass
                else:
                    logging.error(f'Erro ao enviar mensagem para o usuário {user_id}: {e}')
                    user_manager.update_user(user_id, {'msg_private': 'false'})
                    continue
                user_manager.update_user(user_id, {'msg_private': 'false'})

            time.sleep(10)

        for channel_id in [CHANNEL, CHANNEL_IMG]:
            random_link = random.choice(ads_links)
            markup = types.InlineKeyboardMarkup()
            channel_ofc = types.InlineKeyboardButton('ADS', url=random_link)
            markup.add(channel_ofc)

            msg_text = (
                '🔔 <b>Apoie nosso canal!</b> 🔔\n\n'
                'Gostou do conteúdo? 🕰️📚 Que tal nos dar uma força? Ao clicar nos anúncios, você nos ajuda a '
                'continuar trazendo histórias incríveis todos os dias, sem nenhum custo para você! 🚀✨\n\n'
                'Cada clique faz a diferença e nos permite manter o canal ativo e sempre atualizado. 😊🙏\n\n'
                '<b>Clique e apoie o canal com apenas um toque!</b> 🙌\n\n'
                '#historia #ads #ajude_canal'
            )

            bot.send_message(channel_id, msg_text, parse_mode='HTML', reply_markup=markup)
            msg_text_owner = 'Mensagem de ADS enviado com sucesso para o canal'
            bot.send_message(OWNER, msg_text_owner)

            logging.info(f'Mensagem ADS enviada ao canal {channel_id}')
            time.sleep(10)
    except Exception as e:
        logging.error(f'Erro ao enviar ADS para os usuários e canais: {e}')
