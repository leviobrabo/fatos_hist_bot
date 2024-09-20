import logging

from telebot import TeleBot, types

from fatoshist.config import GROUP_LOG
from fatoshist.database.groups import GroupManager

groups_manager = GroupManager()


def register(bot: TeleBot):
    @bot.message_handler(commands=['fwdoff'])
    def cmd_fwdoff(message):
        try:
            user_id = message.from_user.id
            chat_id = message.chat.id
            chat_name = message.chat.title
            chat_type = message.chat.type
            chat_member = bot.get_chat_member(chat_id, user_id)

            if chat_type in {'group', 'supergroup', 'channel'}:
                if chat_member.status not in {'administrator', 'creator'}:
                    bot.reply_to(
                        message,
                        'Você precisa ser um administrador para executar esta ação.',
                    )
                    return

                existing_chat = groups_manager.search_group(chat_id)
                if not existing_chat:
                    groups_manager.add_chat_db(chat_id, chat_name)
                    send_new_group_message(message.chat)
                    return

                if existing_chat.get('forwarding') == 'false':
                    bot.reply_to(
                        message,
                        f'O encaminhamento do <b>{chat_name}</b> já está desativado.',
                    )
                    return

            groups_manager.update_forwarding_status(chat_id, 'false')
            markup = types.InlineKeyboardMarkup()
            report_bugs = types.InlineKeyboardButton('Relatar bugs', url='https://t.me/kylorensbot')
            markup.add(report_bugs)
            bot.reply_to(
                message,
                (
                    f'<b>⚠️ O encaminhamento do <b>{chat_name}</b> foi DESATIVADO '
                    'com sucesso</b>.\n\nAgora o chat não receberá:\n\n• Imagens '
                    'históricas\nEncaminhamentos do canal oficial\nQuiz de história'
                ),
                reply_markup=markup,
            )
            bot.send_message(
                GROUP_LOG,
                f'<b>#{bot.get_me().username} #Fwdoff</b>\n<b>Chat</b>: {chat_name}\n' f'<b>ID:</b> <code>{chat_id}</code>',
            )

        except Exception as e:
            logging.error(f'Erro ao desativar o encaminhamento do chat: {str(e)}')

    @bot.message_handler(commands=['fwdon'])
    def cmd_fwdon(message):
        try:
            user_id = message.from_user.id
            chat_id = message.chat.id
            chat_name = message.chat.title
            chat_type = message.chat.type
            chat_member = bot.get_chat_member(chat_id, user_id)

            if chat_type in {'group', 'supergroup', 'channel'}:
                if chat_member.status not in {'administrator', 'creator'}:
                    bot.reply_to(
                        message,
                        'Você precisa ser um administrador para executar esta ação.',
                    )
                    return

                existing_chat = groups_manager.search_group(chat_id)
                if not existing_chat:
                    groups_manager.add_chat_db(chat_id, chat_name)
                    send_new_group_message(message.chat)
                    return

                if existing_chat.get('forwarding') == 'true':
                    bot.reply_to(
                        message,
                        f'As notificações do {chat_name} já estão ativadas.',
                    )
                    return

            groups_manager.update_forwarding_status(chat_id, 'true')
            markup = types.InlineKeyboardMarkup()
            report_bugs = types.InlineKeyboardButton('Relatar bugs', url='https://t.me/kylorensbot')
            markup.add(report_bugs)
            bot.reply_to(
                message,
                (
                    f'<b>O encaminhamento do {chat_name} foi ATIVADO com sucesso.</b>\n\n'
                    'Agora o chat receberá:\n\n• Imagens históricas\nEncaminhamentos do '
                    'canal oficial\nQuiz de história'
                ),
                reply_markup=markup,
            )
            bot.send_message(
                GROUP_LOG,
                f'<b>#{bot.get_me().username} #Fwdon</b>\n<b>Chat</b>: {chat_name}\n' f'<b>ID:</b> <code>{chat_id}</code>',
            )
        except Exception as e:
            logging.error(f'Erro ao ativar o encaminhamento do chat: {str(e)}')

    @bot.message_handler(commands=['settopic'])
    def cmd_settopic(message):
        try:
            user_id = message.from_user.id
            chat_id = message.chat.id
            chat_type = message.chat.type
            chat_member = bot.get_chat_member(chat_id, user_id)

            if message.reply_to_message and message.reply_to_message.message_thread_id:
                thread_id = message.reply_to_message.message_thread_id
            else:
                bot.reply_to(
                    message,
                    'Este comando deve ser uma resposta a uma mensagem com um tópico.',
                )
                return

            if chat_type in {'group', 'supergroup'}:
                if chat_member.status != 'creator':
                    bot.reply_to(
                        message,
                        'Você precisa ser o dono do chat para executar esta ação.',
                    )
                    return

                groups_manager.update_thread_id(chat_id, thread_id)

                bot.reply_to(
                    message,
                    (
                        f'O Tópico foi atualizado com sucesso!\n\nThread_id= '
                        f'<code>{thread_id}</code>\n\nAgora você receberá os fatos '
                        'históricos aqui'
                    ),
                )

        except Exception as e:
            logging.error(f'Erro ao definir o tópico: {str(e)}')

    @bot.message_handler(commands=['unsettopic'])
    def cmd_unsettopic(message):
        try:
            user_id = message.from_user.id
            chat_id = message.chat.id
            chat_type = message.chat.type
            chat_member = bot.get_chat_member(chat_id, user_id)

            if chat_type in {'group', 'supergroup'}:
                if chat_member.status != 'creator':
                    bot.reply_to(
                        message,
                        'Você precisa ser o dono do chat para executar esta ação.',
                    )
                    return

                groups_manager.update_thread_id(chat_id, '')

                bot.reply_to(
                    message,
                    'O envio das mensagens no tópico foi removido com sucesso!',
                )

        except Exception as e:
            logging.error(f'Erro ao remover o tópico: {str(e)}')

    def send_new_group_message(chat):
        chatusername = f'@{chat.username}' if chat.username else 'Private Group'
        bot.send_message(
            GROUP_LOG,
            text=(
                f'#{bot.get_me().username} #New_Group\n'
                f'<b>Chat:</b> {chat.title}\n<b>ID:</b> <code>{chat.id}</code>\n'
                f'<b>Link:</b> {chatusername}'
            ),
            parse_mode='html',
            disable_web_page_preview=True,
        )
