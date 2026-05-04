import logging
import random
import time

from telebot import types

from fatoshist.config import CHANNEL, CHANNEL_IMG, OWNER
from fatoshist.database.users import UserManager
from fatoshist.database.groups import GroupManager

user_manager = UserManager()
group_manager = GroupManager()

ads_links = [
    'https://omg10.com/4/10930545',
    'https://omg10.com/4/10930547',
    'https://omg10.com/4/10930546',
    'https://omg10.com/4/10930523',
    'https://omg10.com/4/10963924',
    'https://omg10.com/4/10963927',
    'https://omg10.com/4/10963930',
    'https://omg10.com/4/10963933',
]


def ads_message_channel_user(bot, user_id):
    try:
        random_link = random.choice(ads_links)

        markup = types.InlineKeyboardMarkup()
        channel_ofc = types.InlineKeyboardButton('💰 GANHAR DINHEIRO', url=random_link)
        markup.add(channel_ofc)

        msg_text = (
            '<b>💸 Quer ganhar dinheiro pelo celular?</b>\n\n'
            'Você sabe que pode ganhar R$50, R$100 ou mais por dia apenasclicando em anúncios? \n\n'
            'É simples, rápido e não custanada para você!\n\n'
            '<b>👉 Clique no botão abaixo e comece AGORA!</b>\n'
        )

        bot.send_message(user_id, msg_text, parse_mode='HTML', reply_markup=markup)
        return
    except Exception as e:
        logging.error(f'Erro ao preparar a mensagem ADS para os usuários e canais: {e}')
        return  


def ads_msg_job(bot):
    try:
        random_link = random.choice(ads_links)

        for channel_id in [CHANNEL, CHANNEL_IMG]:
            markup = types.InlineKeyboardMarkup()
            channel_ofc = types.InlineKeyboardButton('💰 GANHAR DINHEIRO', url=random_link)
            markup.add(channel_ofc)

            msg_text = (
                '<b>💸 Quer ganhar dinheiro pelo celular?</b>\n\n'
                'Você sabe que pode ganhar R$50, R$100 ou mais por dia apenasclicando em anúncios? \n\n'
                'É simples, rápido e não custanada para você!\n\n'
                '<b>👉 Clique no botão abaixo e comece AGORA!</b>\n'
                '#dinheiro #ganhar #celular # rendextra'
            )

            bot.send_message(channel_id, msg_text, parse_mode='HTML', reply_markup=markup)
            logging.info(f'Mensagem ADS enviada ao canal {channel_id}')
            time.sleep(1)

        chats = list(group_manager.get_all_chats())
        for chat in chats:
            try:
                markup = types.InlineKeyboardMarkup()
                channel_ofc = types.InlineKeyboardButton('💰 GANHAR DINHEIRO', url=random_link)
                markup.add(channel_ofc)

                msg_text = (
                    '<b>💸 Quer ganhar dinheiro pelo celular?</b>\n\n'
                    'Você sabe que pode ganhar R$50, R$100 ou mais por dia apenasclicando em anúncios? \n\n'
                    'É simples, rápido e não custanada para você!\n\n'
                    '<b>👉 Clique no botão abaixo e comece AGORA!</b>\n'
                )

                bot.send_message(chat['chat_id'], msg_text, parse_mode='HTML', reply_markup=markup)
                logging.info(f'Mensagem ADS enviada ao grupo {chat["chat_id"]}')
            except Exception as e:
                if '403' in str(e) or 'blocked' in str(e) or 'kicked' in str(e):
                    group_manager.remove_chat_db(chat['chat_id'])
            time.sleep(0.5)

        user_models = user_manager.get_all_users({'msg_private': 'true'})
        success = 0
        failed = 0
        for user_model in user_models:
            user_id = user_model['user_id']

            try:
                markup = types.InlineKeyboardMarkup()
                channel_ofc = types.InlineKeyboardButton('💰 GANHAR DINHEIRO', url=random_link)
                markup.add(channel_ofc)

                msg_text = (
                    '<b>💸 Quer ganhar dinheiro pelo celular?</b>\n\n'
                    'Você sabe que pode ganhar R$50, R$100 ou mais por dia apenasclicando em anúncios? \n\n'
                    'É simples, rápido e não custanada para você!\n\n'
                    '<b>👉 Clique no botão abaixo e comece AGORA!</b>\n'
                )

                bot.send_message(user_id, msg_text, parse_mode='HTML', reply_markup=markup)
                success += 1
                logging.info(f'Mensagem ADS enviada ao usuário {user_id}')
            except Exception as e:
                if '403' in str(e) or 'blocked' in str(e) or 'deactivated' in str(e) or 'chat not found' in str(e):
                    user_manager.update_user(user_id, {'msg_private': 'false'})
                    failed += 1
                else:
                    failed += 1
            time.sleep(0.5)

        msg_text_owner = (
            f'<b>Mensagem ADS enviada com sucesso!</b>\n\n'
            f'📢 Canais: 2\n'
            f'👥 Grupos: {len(chats)}\n'
            f'👤 Usuários OK: {success}\n'
            f'❌ Usuários Falha: {failed}'
        )
        bot.send_message(OWNER, msg_text_owner, parse_mode="HTML")

    except Exception as e:
        logging.error(f'Erro ao enviar ADS para os usuários e canais: {e}')
        return
