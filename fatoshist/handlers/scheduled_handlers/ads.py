import logging
import random
import time

from telebot import types

from fatoshist.config import CHANNEL, CHANNEL_IMG, OWNER
from fatoshist.database.users import UserManager

user_manager = UserManager()

ads_links = [
    'https://www.profitablecpmratenetwork.com/djt7wpcj5z?key=3baa748bc0990b4b5c6727d07024a044',
    'https://www.profitablecpmratenetwork.com/ge7mn5gp?key=bebb7238590df1a541984429b5f12a77',
    'https://www.profitablecpmratenetwork.com/sjnxjg5x?key=512d296dd7bce4c432e80e070ba62fb9',
    'https://www.profitablecpmratenetwork.com/tdzhuvh1?key=e3443f5ad0657b7ca27193f9b13aa87e',
    'https://www.profitablecpmratenetwork.com/cq3hxfki?key=62cf0735cf731bb51245a4898086a824',
    'https://www.profitablecpmratenetwork.com/sjnxjg5x?key=512d296dd7bce4c432e80e070ba62fb9',
]


def ads_message_channel_user(bot, user_id):
    try:
        random_link = random.choice(ads_links)

        markup = types.InlineKeyboardMarkup()
        channel_ofc = types.InlineKeyboardButton('ADS', url=random_link)
        markup.add(channel_ofc)

        msg_text = (
            '<tg-emoji emoji-id="5458603043203327669">🔔</tg-emoji> <b>Apoie nosso canal!</b> <tg-emoji emoji-id="5458603043203327669">🔔</tg-emoji>\n\n'
            'Gostou do conteúdo? <tg-emoji emoji-id="6334540900005315791">🕰️</tg-emoji><tg-emoji emoji-id="5373098009640836781">📚</tg-emoji> Que tal nos dar uma força? Ao clicar nos anúncios, você nos ajuda a '
            'continuar trazendo histórias incríveis todos os dias, sem nenhum custo para você! <tg-emoji emoji-id="5445284980978621387">🚀</tg-emoji><tg-emoji emoji-id="5325547803936572038">✨</tg-emoji>\n\n'
            'Cada clique faz a diferença e nos permite manter o canal ativo e sempre atualizado. <tg-emoji emoji-id="5348388457196559257">😊</tg-emoji><tg-emoji emoji-id="5235516278571020309">🙏</tg-emoji>\n\n'
            '<b>Clique e apoie o canal com apenas um toque!</b> <tg-emoji emoji-id="5469645992531862101">🙌</tg-emoji>'
        )

        bot.send_message(user_id, msg_text, parse_mode='HTML', reply_markup=markup)
        return  
    except Exception as e:
        logging.error(f'Erro ao preparar a mensagem ADS para os usuários e canais: {e}')
        return  


def ads_msg_job(bot):
    try:
        for channel_id in [CHANNEL, CHANNEL_IMG]:
            random_link = random.choice(ads_links)
            markup = types.InlineKeyboardMarkup()
            channel_ofc = types.InlineKeyboardButton('ADS', url=random_link)
            markup.add(channel_ofc)

            msg_text = (
                '<tg-emoji emoji-id="5458603043203327669">🔔</tg-emoji> <b>Apoie nosso canal!</b> <tg-emoji emoji-id="5458603043203327669">🔔</tg-emoji>\n\n'
                'Gostou do conteúdo? <tg-emoji emoji-id="6334540900005315791">🕰️</tg-emoji><tg-emoji emoji-id="5373098009640836781">📚</tg-emoji> Que tal nos dar uma força? Ao clicar nos anúncios, você nos ajuda a '
                'continuar trazendo histórias incríveis todos os dias, sem nenhum custo para você! <tg-emoji emoji-id="5445284980978621387">🚀</tg-emoji><tg-emoji emoji-id="5325547803936572038">✨</tg-emoji>\n\n'
                'Cada clique faz a diferença e nos permite manter o canal ativo e sempre atualizado. <tg-emoji emoji-id="5348388457196559257">😊</tg-emoji><tg-emoji emoji-id="5235516278571020309">🙏</tg-emoji>\n\n'
                '<b>Clique e apoie o canal com apenas um toque!</b> <tg-emoji emoji-id="5469645992531862101">🙌</tg-emoji>\n\n'
                '#historia #ads #ajude_canal'
            )

            bot.send_message(channel_id, msg_text, parse_mode='HTML', reply_markup=markup)
            msg_text_owner = 'Mensagem de ADS enviado com sucesso para o canal'
            bot.send_message(OWNER, msg_text_owner, parse_mode="HTML")

            logging.info(f'Mensagem ADS enviada ao canal {channel_id}')
            time.sleep(1)

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
                    logging.error(f'Erro ao enviar mensagem de ADS para o usuário {user_id}: {e}')
                    user_manager.update_user(user_id, {'msg_private': 'false'})
                    continue
                user_manager.update_user(user_id, {'msg_private': 'false'})

            time.sleep(1)
            return  
    except Exception as e:
        logging.error(f'Erro ao enviar ADS para os usuários e canais: {e}')
        return  
