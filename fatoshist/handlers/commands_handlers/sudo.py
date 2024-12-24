import logging

import psutil
import telebot
from telebot import TeleBot, types

from fatoshist.config import GROUP_LOG, OWNER
from fatoshist.database.groups import GroupManager
from fatoshist.database.users import UserManager

user_manager = UserManager()
group_manager = GroupManager()


def register(bot: TeleBot):
    @bot.message_handler(commands=['add_sudo'])
    def cmd_add_sudo(message):
        try:
            if message.chat.type != 'private' and message.from_user.id != OWNER:
                return

            if len(message.text.split()) != '2':
                bot.send_message(
                    message.chat.id,
                    'Por favor, forneça um ID de usuário após /add_sudo.',
                )
                return

            user_id = int(message.text.split()[1])
            user_db = user_manager.get_user(user_id)

            if user_db and user_db.get('sudo') == 'true':
                bot.send_message(
                    message.chat.id,
                    'Este usuário já tem permissão de sudo.',
                )
                return

            result = user_manager.set_user_sudo(user_id)

            if result.modified_count > 0:
                username = '@' + message.from_user.username if message.from_user.username else 'Não tem um nome de usuário'
                updated_user = user_manager.get_user(user_id)

                if updated_user:
                    bot.send_message(
                        message.chat.id,
                        f"<b>Novo sudo adicionado com sucesso</b>\n\n"
                        f"<b>ID:</b> <code>{user_id}</code>\n"
                        f"<b>Nome:</b> {updated_user.get('first_name')}\n"
                        f"<b>Username:</b> {username}",
                        parse_mode='HTML',
                    )
                    bot.send_message(
                        GROUP_LOG,
                        f"<b>#{bot.get_me().username} #New_sudo</b>\n"
                        f"<b>ID:</b> <code>{user_id}</code>\n"
                        f"<b>Nome:</b> {updated_user.get('first_name')}\n"
                        f"<b>Username:</b> {username}",
                        parse_mode='HTML',
                    )
            else:
                bot.send_message(
                    message.chat.id,
                    'Usuário não encontrado no banco de dados.',
                )

        except Exception as e:
            logging.error(f'Erro ao adicionar um usuário sudo: {e}')

    @bot.message_handler(commands=['rem_sudo'])
    def cmd_rem_sudo(message):
        try:
            if message.chat.type != 'private' and message.from_user.id != OWNER:
                return

            if len(message.text.split()) != '2':
                bot.send_message(
                    message.chat.id,
                    'Por favor, forneça um ID de usuário após /rem_sudo.',
                )
                return

            user_id = int(message.text.split()[1])
            user = user_manager.get_user(user_id)

            if user and user.get('sudo') == 'false':
                bot.send_message(
                    message.chat.id,
                    'Este usuário já não tem permissão de sudo.',
                )
                return

            result = user_manager.set_user_sudo(user_id)

            if result.modified_count > 0:
                username = '@' + message.from_user.username if message.from_user.username else 'Não tem um nome de usuário'
                updated_user = user_manager.get_user(user_id)

                if updated_user:
                    bot.send_message(
                        message.chat.id,
                        f"<b>User sudo removido com sucesso</b>\n\n"
                        f"<b>ID:</b> <code>{user_id}</code>\n"
                        f"<b>Nome:</b> {updated_user.get('first_name')}\n"
                        f"<b>Username:</b> {username}",
                        parse_mode='HTML',
                    )
                    bot.send_message(
                        GROUP_LOG,
                        f"<b>#{bot.get_me().username} #Rem_sudo</b>\n"
                        f"<b>ID:</b> <code>{user_id}</code>\n"
                        f"<b>Nome:</b> {updated_user.get('first_name')}\n"
                        f"<b>Username:</b> {username}",
                        parse_mode='HTML',
                    )
            else:
                bot.send_message(
                    message.chat.id,
                    'Usuário não encontrado no banco de dados.',
                )

        except Exception as e:
            logging.error(f'Erro ao remover um usuário sudo: {e}')

    @bot.message_handler(commands=['grupos'])
    def cmd_group(message):
        try:
            if message.from_user.id != OWNER and message.chat.type != 'private':
                return

            chats = list(group_manager.get_all_chats().sort('chat_id', 1))
            contador = 1
            chunk_size = 3900 - len(message.text)
            message_chunks = []
            current_chunk = ''

            for chat in chats:
                if chat['chat_id'] >= 0:
                    continue

                group_message = f"<b>{contador}:</b> <b>Group=</b> {chat['chat_name']} || " f"<b>ID:</b> <code>{chat['chat_id']}</code>\n"

                if len(current_chunk + group_message) > chunk_size:
                    message_chunks.append(current_chunk)
                    current_chunk = ''

                current_chunk += group_message
                contador += 1

            if current_chunk:
                message_chunks.append(current_chunk)

            index = 0

            def get_markup(index):
                markup = types.InlineKeyboardMarkup()

                if index > 0:
                    markup.add(types.InlineKeyboardButton('<< Voltar', callback_data=f'groups:{index - 1}'))

                if index < len(message_chunks) - 1:
                    markup.add(types.InlineKeyboardButton('Próximo >>', callback_data=f'groups:{index + 1}'))

                return markup

            bot.send_message(
                message.chat.id,
                message_chunks[index],
                reply_markup=get_markup(index),
                parse_mode='HTML',
            )

            @bot.callback_query_handler(func=lambda query: query.data.startswith('groups:'))
            def callback_handler(query):
                nonlocal index
                index = int(query.data.split(':')[1])

                bot.edit_message_text(
                    chat_id=query.message.chat.id,
                    message_id=query.message.message_id,
                    text=message_chunks[index],
                    reply_markup=get_markup(index),
                    parse_mode='HTML',
                )
                bot.answer_callback_query(callback_query_id=query.id)

        except Exception as e:
            logging.error(f'Erro ao enviar a lista de grupos: {e}')

    @bot.message_handler(commands=['stats'])
    def cmd_stats(message):
        try:
            if message.from_user.id == OWNER:
                count_users = len(list(user_manager.get_all_users()))
                count_groups = len(list(group_manager.get_all_chats()))
                user_stats = f' ☆ {count_users} usuários\n ☆ {count_groups} Grupos'
                bot.reply_to(message, f'\n──❑ 「 Bot Stats 」 ❑──\n\n{user_stats}')
        except Exception as e:
            logging.error(f'Erro ao enviar o stats do bot: {e}')

    @bot.message_handler(commands=['bcusers'])
    def cmd_broadcast_pv(message):
        try:
            if message.from_user.id != OWNER and message.chat.type != 'private':
                return

            sent_message = bot.send_message(message.chat.id, '<i>Processing...</i>', parse_mode='HTML')

            if not message.reply_to_message:
                bot.edit_message_text(
                    chat_id=sent_message.chat.id,
                    message_id=sent_message.message_id,
                    text='<b>Por favor, responda a uma mensagem para o broadcast.</b>',
                    parse_mode='HTML',
                )
                return

            reply_msg = message.reply_to_message
            ulist = user_manager.get_all_users()
            success_br = 0
            block_num = 0
            no_success = 0

            for user in ulist:
                try:
                    bot.send_message(user['user_id'], reply_msg.text)
                    success_br += 1
                except telebot.apihelper.ApiException as err:
                    if err.result.status_code == '403':
                        block_num += 1
                    else:
                        no_success += 1

            bot.edit_message_text(
                chat_id=sent_message.chat.id,
                message_id=sent_message.message_id,
                text=(
                    f'╭─❑ 「 <b>Broadcast Concluído</b> 」 ❑──\n'
                    f'│- <b>Total usuários:</b> `{len(ulist)}`\n'
                    f'│- <b>Ativos:</b> `{success_br}`\n'
                    f'│- <b>Inativos:</b> `{block_num}`\n'
                    f'│- <b>Falha:</b> `{no_success}`\n'
                    f'╰❑'
                ),
                parse_mode='HTML',
            )

        except Exception as e:
            logging.error(f'Erro ao enviar o broadcast para user: {e}')

    @bot.message_handler(commands=['bcgps'])
    def cmd_broadcast_chat(message):
        try:
            if message.from_user.id != OWNER:
                return
            if message.chat.type != 'private':
                return

            command_parts = message.text.split(' ')
            sent_message = bot.send_message(message.chat.id, '<i>Processing...</i>', parse_mode='HTML')

            if message.reply_to_message:
                reply_msg = message.reply_to_message
                ulist = group_manager.get_all_chats()
                success_br = 0
                no_success = 0
                block_num = 0

                for chat in ulist:
                    try:
                        if message.text.startswith('/bc'):
                            bot.forward_message(
                                chat['chat_id'],
                                reply_msg.chat.id,
                                reply_msg.message_id,
                            )
                        elif message.text.startswith('/bc'):
                            bot.send_message(chat['chat_id'], reply_msg.text)
                        success_br += 1
                    except telebot.apihelper.ApiException as err:
                        if err.result.status_code == 403:
                            block_num += 1
                        else:
                            no_success += 1

                bot.send_message(
                    message.chat.id,
                    f'╭─❑ 「 <b>Broadcast Concluído</b> 」 ❑──\n'
                    f'│- <b>Total grupos:</b> `{sum(1 for _ in ulist)}`\n'
                    f'│- <b>Ativos:</b> `{success_br}`\n'
                    f'│- <b>Inativos:</b> `{block_num}`\n'
                    f'│- <b>Falha:</b> `{no_success}`\n'
                    f'╰❑',
                )
            else:
                if len(command_parts) < 2:
                    bot.send_message(
                        message.chat.id,
                        '<i>I need text to broadcast.</i>',
                        parse_mode='HTML',
                    )
                    return

                query = ' '.join(command_parts[1:])
                web_preview = query.startswith('-d')
                query_ = query[2:].strip() if web_preview else query
                ulist = group_manager.get_all_chats()
                success_br = 0
                no_success = 0
                block_num = 0

                for chat in ulist:
                    try:
                        bot.send_message(
                            chat['chat_id'],
                            query_,
                            disable_web_page_preview=not web_preview,
                            parse_mode='HTML',
                        )
                        success_br += 1
                    except telebot.apihelper.ApiException as err:
                        if err.result.status_code == 403:
                            block_num += 1
                        else:
                            no_success += 1

                bot.edit_message_text(
                    chat_id=sent_message.chat.id,
                    message_id=sent_message.message_id,
                    text=(
                        f'╭─❑ 「 <b>Broadcast Concluído</b> 」 ❑──\n'
                        f'│- <b>Total grupos:</b> `{sum(1 for _ in ulist)}`\n'
                        f'│- <b>Ativos:</b> `{success_br}`\n'
                        f'│- <b>Inativos:</b> `{block_num}`\n'
                        f'│- <b>Falha:</b> `{no_success}`\n'
                        f'╰❑'
                    ),
                    parse_mode='HTML',
                )
        except Exception as e:
            logging.error(f'Erro ao enviar o broadcast para grupos: {e}')

    @bot.message_handler(commands=['sys'])
    def cmd_sys(message: types.Message):
        try:
            if message.from_user.id == OWNER:
                bot.reply_to(
                    message,
                    f'\n──❑ 「 System Stats 」 ❑──\n\n ☆ CPU usage: {psutil.cpu_percent(4)} %\n' f' ☆ RAM usage: {psutil.virtual_memory()[2]} %',
                )
        except Exception as e:
            logging.error(f'Erro ao enviar a lista de comandos do sistema: {e}')
            
    @bot.message_handler(commands=['bc'])
    def broadcast_handler(message):
        """Handler para o comando /bc. Encaminha uma mensagem para todos os usuários com delay e atualização do status."""
        if not user_manager.is_sudo(message.from_user.id):
            bot.reply_to(message, "Você não tem permissão para usar este comando.")
            return
    
        if not message.reply_to_message:
            bot.reply_to(message, "Por favor, responda a uma mensagem para enviá-la como broadcast.")
            return
    
        broadcast_message = message.reply_to_message
        users = user_manager.get_all_users()
        sent_count = 0
        failed_count = 0
    
        status_message = bot.reply_to(message, f"Iniciando envio...\nEnviadas: {sent_count}\nFalhas: {failed_count}")
        
        for idx, user in enumerate(users):
            try:
                bot.forward_message(chat_id=user["user_id"], from_chat_id=broadcast_message.chat.id, message_id=broadcast_message.message_id)
                sent_count += 1
            except Exception as e:
                logging.error(f"Erro ao enviar mensagem para {user['user_id']}: {e}")
                failed_count += 1
                
                if "Too Many Requests" in str(e):
                    retry_after = int(str(e).split('retry after ')[-1].split()[0])
                    logging.warning(f"Erro 429. Aguardando {retry_after} segundos antes de continuar...")
                    time.sleep(retry_after)
                else:
                    user_manager.remove_user_db(user["user_id"])
                    logging.warning(f"Usuário {user['user_id']} bloqueou o bot e foi removido do banco de dados.")
            
            if idx % 100 == 0 or idx == len(users) - 1:
                try:
                    bot.edit_message_text(
                        chat_id=status_message.chat.id,
                        message_id=status_message.message_id,
                        text=f"Broadcast em andamento...\nEnviadas: {sent_count}\nFalhas: {failed_count}\nUsuários processados: {idx + 1}/{len(users)}"
                    )
                except Exception as e:
                    logging.error(f"Erro ao atualizar status do broadcast: {e}")
    
            time.sleep(2)
    
        try:
            bot.edit_message_text(
                chat_id=status_message.chat.id,
                message_id=status_message.message_id,
                text=f"Broadcast concluído.\nEnviadas: {sent_count}\nFalhas: {failed_count}"
            )
        except Exception as e:
            logging.error(f"Erro ao finalizar mensagem de status do broadcast: {e}")

    
    return [
        types.BotCommand('/add_sudo', 'Elevar usuário'),
        types.BotCommand('/rem_sudo', 'Remover usuário'),
        types.BotCommand('/grupos', 'Lista de grupos'),
        types.BotCommand('/stats', 'Estatística do bot'),
        types.BotCommand('/bcusers', 'Broadcast para usuários'),
        types.BotCommand('/bcgps', 'Broadcast para grupos'),
        types.BotCommand('/bc', 'Broadcast para todos users'),
        types.BotCommand('/sys', 'Uso do servidor'),
    ]
