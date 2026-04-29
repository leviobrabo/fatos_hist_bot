import logging

from telebot import TeleBot, types

from fatoshist.config import CHANNEL, CHANNEL_IMG, CHANNEL_POST, GROUP_LOG
from fatoshist.database.groups import GroupManager

group_manager = GroupManager()


def send_new_group_message(bot: TeleBot, chat):
    try:
        chatusername = f'@{chat.username}' if chat.username else 'Private Group'
        bot.send_message(
            GROUP_LOG,
            text=f'#{bot.get_me().username} #New_Group\n'
            f'<b>Chat:</b> {chat.title}\n'
            f'<b>ID:</b> <code>{chat.id}</code>\n'
            f'<b>Link:</b> {chatusername}',
            parse_mode='html',
            message_thread_id=38551,
            disable_web_page_preview=True,
        )
    except Exception as e:
        logging.error(f'Erro ao adicionador grupo no banco de dados: {e}')


def register(bot):
    @bot.my_chat_member_handler()
    def send_group_greeting(message: types.ChatMemberUpdated):
        try:
            new_member = message.new_chat_member
            if message.chat.type != 'private' and new_member.status in {'member', 'administrator'}:
                chat_id = message.chat.id
                chat_name = message.chat.title

                if chat_id in {CHANNEL, CHANNEL_POST, GROUP_LOG, CHANNEL_IMG}:
                    logging.warning(f'Ignorando armazenamento de chat com ID {chat_id}, pois corresponde a um ID configurado.')
                    return

                existing_chat = group_manager.search_group(chat_id)
                if existing_chat:
                    logging.warning(f'O bate-papo com ID {chat_id} já existe no banco de dados.')
                    return

                group_manager.add_chat_db(chat_id, chat_name)
                logging.info(f'⭐️ O bot foi adicionado no grupo {chat_name} - ({chat_id})')

                send_new_group_message(bot, message.chat)

                try:
                    if message.chat.type in {'group', 'supergroup', 'channel'}:
                        markup = types.InlineKeyboardMarkup()
                        channel_ofc = types.InlineKeyboardButton('Canal Oficial', url='https://t.me/historia_br', icon_custom_emoji_id="5305417940760273444")
                        report_bugs = types.InlineKeyboardButton('Relatar bugs', url='https://t.me/kylorensbot', icon_custom_emoji_id="5447644880824181073")
                        web_site = types.InlineKeyboardButton('WebSite', url='https://www.historiadodia.com/', icon_custom_emoji_id="5271604874419647061")
                        markup.add(channel_ofc, report_bugs)
                        markup.add(web_site)
                        msg_text = (
                            'Olá, meu nome é <b>Fatos Históricos</b>! Obrigado por me adicionar em seu grupo.\n\n'
                            'Eu enviarei mensagens todos os dias às 8 horas e possuo alguns comandos.\n\n'
                            'Se quiser receber mais fatos históricos, conceda-me as permissões de administrador para fixar mensagens e '
                            'convidar usuários via link.'
                        )

                        bot.send_message(
                            chat_id,
                            msg_text,
                            reply_markup=markup,
                            parse_mode='HTML',
                        )

                except Exception as e:
                    logging.error(f'Erro ao lidar com saudação de grupo: {e}')

        except Exception as e:
            logging.error(f'Erro ao envias boas vindas no grupo: {e}')

    @bot.message_handler(content_types=['text'])
    def handle_text_messages(message):
        try:
            chat_type = message.chat.type

            if chat_type in {'group', 'supergroup'}:
                chat_id = message.chat.id
                chat_name = message.chat.title
                if chat_id in {CHANNEL, CHANNEL_POST, GROUP_LOG, CHANNEL_IMG}:
                    return

                existing_chat = group_manager.search_group(chat_id)
                if existing_chat:
                    return

                group_manager.add_chat_db(chat_id, chat_name)
                logging.info(f'⭐️ O bot foi adicionado no grupo {chat_name} - ({chat_id})')

                send_new_group_message(bot, message.chat)

                try:
                    markup = types.InlineKeyboardMarkup()
                    channel_ofc = types.InlineKeyboardButton('Canal Oficial', url='https://t.me/historia_br', icon_custom_emoji_id="5305417940760273444")
                    report_bugs = types.InlineKeyboardButton('Relatar bugs', url='https://t.me/kylorensbot', icon_custom_emoji_id="5447644880824181073")
                    web_site = types.InlineKeyboardButton('WebSite', url='https://www.historiadodia.com/', icon_custom_emoji_id="5271604874419647061")
                    markup.add(channel_ofc, report_bugs)
                    markup.add(web_site)
                    msg_text = (
                        'Olá, meu nome é <b>Fatos Históricos</b>! Obrigado por me adicionar em seu grupo.\n\n'
                        'Eu enviarei mensagens todos os dias às 8 horas e possuo alguns comandos.\n\n'
                        'Se quiser receber mais fatos históricos, conceda-me as permissões de administrador para fixar mensagens e '
                        'convidar usuários via link.'
                    )

                    bot.send_message(
                        chat_id,
                        msg_text,
                        reply_markup=markup,
                        parse_mode='HTML',
                    )

                except Exception as e:
                    logging.error(f'Erro ao lidar com saudação de grupo: {e}')
        except Exception as e:
            logging.error(f'Erro ao envias boas vindas no grupo: {e}')

    @bot.message_handler(content_types=['left_chat_member'])
    def on_left_chat_member(message):
        try:
            if message.left_chat_member.id == bot.get_me().id:
                chat_id = message.chat.id
                chat_name = message.chat.title
                group_manager.remove_chat_db(chat_id)
                logging.info(f'O bot foi removido do grupo {chat_name} - ({chat_id})')
        except Exception as e:
            logging.error(f'Erro ao remover grupo do banco de dados: {e}')
